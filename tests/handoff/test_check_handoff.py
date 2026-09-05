"""Handoff integrity checks, isolated from application configuration and databases."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from typing import cast

CHECKER = Path(__file__).resolve().parents[2] / "scripts/check_handoff.py"
spec = importlib.util.spec_from_file_location("check_handoff", CHECKER)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
validate = cast(Callable[[Path, object], list[str]], module.validate)


class HandoffValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        docs = self.root / "docs"
        docs.mkdir()
        (docs / "index.md").write_text(
            "# Queue\n\n| P0-01.A | 无 | W | First | Test |\n"
            "| P0-01.B | P0-01.A | W | Second | Test |\n",
            encoding="utf-8",
        )
        (docs / "packet.md").write_text("## P0-01.A：First\n", encoding="utf-8")
        self.tasks: list[dict[str, object]] = [
            {
                "id": "P0-01.A",
                "depends_on": [],
                "role": "W",
                "readiness": "specified",
                "execution": "not_authorized",
                "packet": "docs/packet.md",
                "authorization_ref": None,
                "evidence": [],
                "review_ref": None,
                "blocked_reason": None,
            },
            {
                "id": "P0-01.B",
                "depends_on": ["P0-01.A"],
                "role": "W",
                "readiness": "outlined",
                "execution": "not_authorized",
                "packet": None,
                "authorization_ref": None,
                "evidence": [],
                "review_ref": None,
                "blocked_reason": None,
            },
        ]
        self.data: dict[str, object] = {
            "schema_version": 1,
            "documents": ["docs/index.md", "docs/packet.md"],
            "task_index": "docs/index.md",
            "tasks": self.tasks,
            "receiving_roles": {"technical_lead": None, "reviewer": None},
        }

    def test_pending_handoff_is_valid_but_not_execution_approval(self) -> None:
        self.assertEqual(validate(self.root, self.data), [])

    def test_missing_document_is_rejected(self) -> None:
        (self.root / "docs/packet.md").unlink()
        self.assertTrue(any("missing" in error for error in validate(self.root, self.data)))

    def test_missing_dependency_is_rejected(self) -> None:
        self.tasks[1]["depends_on"] = ["P0-99.A"]
        self.assertTrue(any("dependency" in error for error in validate(self.root, self.data)))

    def test_cycle_is_rejected(self) -> None:
        self.tasks[0]["depends_on"] = ["P0-01.B"]
        self.assertTrue(any("cycle" in error for error in validate(self.root, self.data)))

    def test_duplicate_task_is_rejected(self) -> None:
        self.tasks.append(dict(self.tasks[0]))
        self.assertTrue(any("duplicate" in error for error in validate(self.root, self.data)))

    def test_missing_packet_heading_is_rejected(self) -> None:
        self.tasks[1]["readiness"] = "specified"
        self.tasks[1]["packet"] = "docs/packet.md"
        self.assertTrue(any("heading" in error for error in validate(self.root, self.data)))

    def test_verified_without_evidence_is_rejected(self) -> None:
        self.tasks[0]["readiness"] = "ready"
        self.tasks[0]["execution"] = "verified"
        errors = validate(self.root, self.data)
        self.assertTrue(any("evidence" in error for error in errors))
        self.assertTrue(any("authorization" in error for error in errors))

    def test_unverified_predecessor_cannot_unlock_execution(self) -> None:
        (self.root / "docs/packet.md").write_text(
            "## P0-01.A：First\n## P0-01.B：Second\n", encoding="utf-8"
        )
        self.tasks[1].update(
            readiness="ready",
            execution="in_progress",
            packet="docs/packet.md",
            authorization_ref="docs/packet.md",
        )
        self.data["receiving_roles"] = {"technical_lead": "lead", "reviewer": "reviewer"}
        self.assertTrue(any("predecessor" in error for error in validate(self.root, self.data)))

    def test_consistent_verified_record_requires_human_evidence_review(self) -> None:
        self.tasks[0].update(
            readiness="ready",
            execution="verified",
            authorization_ref="docs/packet.md",
            evidence=["docs/packet.md"],
            review_ref="docs/packet.md",
        )
        self.data["receiving_roles"] = {"technical_lead": "lead", "reviewer": "reviewer"}
        self.assertEqual(validate(self.root, self.data), [])

    def test_index_drift_is_rejected(self) -> None:
        (self.root / "docs/index.md").write_text("# Empty queue\n", encoding="utf-8")
        self.assertTrue(any("index" in error for error in validate(self.root, self.data)))

    def test_absolute_and_parent_paths_are_rejected(self) -> None:
        self.data["documents"] = ["../outside.md", "/absolute.md"]
        self.assertTrue(any("unsafe path" in error for error in validate(self.root, self.data)))

    def test_environment_file_is_never_accepted_as_evidence(self) -> None:
        (self.root / ".env").write_text("synthetic-data", encoding="utf-8")
        self.data["documents"] = [".env"]
        self.assertTrue(any("unsupported file" in e for e in validate(self.root, self.data)))

    def test_external_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "external.md"
            target.write_text("synthetic-data", encoding="utf-8")
            (self.root / "docs/link.md").symlink_to(target)
            self.data["documents"] = ["docs/link.md"]
            self.assertTrue(any("unsafe path" in e for e in validate(self.root, self.data)))

    def test_internal_secret_symlink_is_rejected(self) -> None:
        target = self.root / ".env"
        target.write_text("synthetic-data", encoding="utf-8")
        (self.root / "docs/link.md").symlink_to(target)
        self.data["documents"] = ["docs/link.md"]
        self.assertTrue(any("unsafe path" in e for e in validate(self.root, self.data)))

    def test_malformed_manifest_returns_errors_instead_of_crashing(self) -> None:
        malformed: tuple[object, ...] = (None, [], {"schema_version": 1, "tasks": [None]})
        for data in malformed:
            with self.subTest(data=data):
                self.assertTrue(validate(self.root, data))

    def test_unknown_status_and_block_without_reason_are_rejected(self) -> None:
        self.tasks[0].update(readiness="green", execution="blocked")
        errors = validate(self.root, self.data)
        self.assertTrue(any("readiness" in error for error in errors))
        self.assertTrue(any("blocked_reason" in error for error in errors))

    def test_container_values_in_status_fields_do_not_crash(self) -> None:
        self.tasks[0].update(readiness=[], execution={}, role=[])
        self.assertTrue(validate(self.root, self.data))

    def test_receipt_cannot_be_completed_without_receiver_and_record(self) -> None:
        self.data["receipt"] = {"status": "received", "received_by": None, "record": None}
        self.assertTrue(any("receipt" in e for e in validate(self.root, self.data)))

    def test_pending_receipt_is_explicitly_allowed(self) -> None:
        self.data["receipt"] = {"status": "pending", "received_by": None, "record": None}
        self.assertEqual(validate(self.root, self.data), [])

    def test_cli_checks_manifest_without_changing_it(self) -> None:
        manifest = self.root / "docs/project/handoff/state.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps(self.data), encoding="utf-8")
        before = manifest.read_bytes()
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(self.root)],
            capture_output=True,
            text=True,
            timeout=20,
            env={},
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["task_count"], 2)
        self.assertTrue(output["integrity_only"])
        self.assertEqual(manifest.read_bytes(), before)

    def test_cli_rejects_symlinked_manifest(self) -> None:
        manifest = self.root / "docs/project/handoff/state.json"
        manifest.parent.mkdir(parents=True)
        secret = self.root / ".env"
        secret.write_text(json.dumps(self.data), encoding="utf-8")
        manifest.symlink_to(secret)
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(self.root)],
            capture_output=True,
            text=True,
            timeout=20,
            env={},
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsafe path", result.stdout)


if __name__ == "__main__":
    unittest.main()
