"""Read-only handoff consistency checks. Standard library only; no application imports."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TASK_ID = r"P[0-9]-[0-9]{2}\.[A-Z]"
READINESS = ("outlined", "specified", "ready")
EXECUTION = ("not_authorized", "authorized", "in_progress", "in_review", "verified", "blocked")
ACTIVE = ("authorized", "in_progress", "in_review", "verified")
SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml"}


def record(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        return None
    return dict(value)


def strings(value: object) -> list[str] | None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None
    return [str(item) for item in value]


def checked_path(root: Path, value: object, errors: list[str], label: str) -> Path | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label}: missing path")
        return None
    relative = Path(value)
    target = (root / relative).resolve()
    has_symlink = any(
        (root / Path(*relative.parts[:end])).is_symlink()
        for end in range(1, len(relative.parts) + 1)
    )
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or not target.is_relative_to(root)
        or has_symlink
    ):
        errors.append(f"{label}: unsafe path")
        return None
    if relative.suffix not in SUFFIXES or any(
        part.startswith(".") for part in relative.parts if part != ".github"
    ):
        errors.append(f"{label}: unsupported file")
        return None
    if not target.is_file():
        errors.append(f"{label}: missing file {value}")
        return None
    return target


def validate(root: Path, data: object) -> list[str]:
    """Validate references and state consistency, not the truth of human approvals/evidence."""
    root = root.resolve()
    errors: list[str] = []
    manifest = record(data)
    if manifest is None or manifest.get("schema_version") != 1:
        return ["manifest: expected schema_version 1 object"]
    documents = strings(manifest.get("documents"))
    if not documents:
        errors.append("documents: nonempty list required")
    for index, value in enumerate(documents or []):
        checked_path(root, value, errors, f"documents[{index}]")

    raw_tasks = manifest.get("tasks")
    if not isinstance(raw_tasks, list) or not raw_tasks:
        return errors + ["tasks: nonempty list required"]
    tasks: dict[str, dict[str, object]] = {}
    dependencies: dict[str, list[str]] = {}
    for index, raw in enumerate(raw_tasks):
        task = record(raw)
        if task is None:
            errors.append(f"tasks[{index}]: object required")
            continue
        task_id = task.get("id")
        if not isinstance(task_id, str) or re.fullmatch(TASK_ID, task_id) is None:
            errors.append(f"tasks[{index}]: invalid id")
            continue
        if task_id in tasks:
            errors.append(f"duplicate task: {task_id}")
            continue
        tasks[task_id] = task
        deps = strings(task.get("depends_on"))
        if deps is None or len(deps) != len(set(deps)):
            errors.append(f"{task_id}: invalid dependency list")
        dependencies[task_id] = deps or []
        if task.get("readiness") not in READINESS:
            errors.append(f"{task_id}: invalid readiness")
        if task.get("execution") not in EXECUTION:
            errors.append(f"{task_id}: invalid execution")
        if task.get("role") not in ("W", "T", "P"):
            errors.append(f"{task_id}: invalid role")

    for task_id, deps in dependencies.items():
        for dependency in deps:
            if dependency not in tasks:
                errors.append(f"{task_id}: missing dependency {dependency}")
    # Iterative topological reduction also reports cycles without recursive stack limits.
    remaining = set(tasks)
    while remaining:
        removable = {
            task_id
            for task_id in remaining
            if not set(dependencies[task_id]).intersection(remaining)
        }
        if not removable:
            errors.append("dependency cycle detected")
            break
        remaining -= removable

    index_path = checked_path(root, manifest.get("task_index"), errors, "task_index")
    if index_path is not None:
        text = index_path.read_text(encoding="utf-8")
        rows = re.findall(rf"^\| ({TASK_ID}) \| ([^|]+) \| ([WTP]) \|", text, re.M)
        if len(rows) != len(tasks) or {row[0] for row in rows} != set(tasks):
            errors.append("task index IDs differ from manifest")
        for task_id, deps_text, role in rows:
            if task_id not in tasks:
                continue
            if re.findall(TASK_ID, deps_text) != dependencies[task_id]:
                errors.append(f"{task_id}: index dependency drift")
            if role != tasks[task_id].get("role"):
                errors.append(f"{task_id}: index role drift")

    receiving_roles = record(manifest.get("receiving_roles")) or {}
    if "receipt" in manifest:
        receipt = record(manifest.get("receipt"))
        if receipt is None or receipt.get("status") not in (
            "pending",
            "received",
            "received_with_open_items",
            "not_received",
        ):
            errors.append("receipt: invalid record or status")
        elif receipt.get("status") != "pending":
            receiver = receipt.get("received_by")
            if not isinstance(receiver, str) or not receiver.strip():
                errors.append("receipt: received_by required")
            checked_path(root, receipt.get("record"), errors, "receipt record")
            if receipt.get("status") in ("received", "received_with_open_items"):
                for role in ("technical_lead", "reviewer"):
                    owner = receiving_roles.get(role)
                    if not isinstance(owner, str) or not owner.strip():
                        errors.append(f"receipt: assigned {role} required")
    for task_id, task in tasks.items():
        readiness = task.get("readiness")
        execution = task.get("execution")
        packet = task.get("packet")
        if readiness in ("specified", "ready") or packet is not None:
            path = checked_path(root, packet, errors, f"{task_id} packet")
            if path is not None:
                pattern = rf"^#{{1,6}}\s+{re.escape(task_id)}(?:[：:\s]|$)"
                if not re.search(pattern, path.read_text(encoding="utf-8"), re.M):
                    errors.append(f"{task_id}: packet heading missing")
        evidence = strings(task.get("evidence"))
        if evidence is None:
            errors.append(f"{task_id}: evidence must be a list")
        for reference in evidence or []:
            checked_path(root, reference, errors, f"{task_id} evidence")
        for field in ("authorization_ref", "review_ref"):
            field_reference = task.get(field)
            if field_reference is not None:
                checked_path(root, field_reference, errors, f"{task_id} {field}")
        if execution == "blocked" and not task.get("blocked_reason"):
            errors.append(f"{task_id}: blocked_reason required")
        if execution in ACTIVE:
            if readiness != "ready":
                errors.append(f"{task_id}: execution requires ready packet")
            if not task.get("authorization_ref"):
                errors.append(f"{task_id}: authorization_ref required")
            for role in ("technical_lead", "reviewer"):
                owner = receiving_roles.get(role)
                if not isinstance(owner, str) or not owner.strip():
                    errors.append(f"{task_id}: assigned {role} required")
            for dependency in dependencies[task_id]:
                if tasks.get(dependency, {}).get("execution") != "verified":
                    errors.append(f"{task_id}: predecessor {dependency} not verified")
        if execution == "verified":
            if not evidence:
                errors.append(f"{task_id}: verified requires evidence")
            if not task.get("review_ref"):
                errors.append(f"{task_id}: verified requires review_ref")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root: Path = args.root.resolve()
    try:
        path_errors: list[str] = []
        manifest_path = checked_path(
            root, "docs/project/handoff/state.json", path_errors, "manifest"
        )
        if manifest_path is None:
            print(json.dumps({"integrity_only": True, "errors": path_errors}))
            return 1
        data: object = json.loads(manifest_path.read_text(encoding="utf-8"))
        errors = validate(root, data)
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        print(json.dumps({"integrity_only": True, "errors": [type(error).__name__]}))
        return 1
    manifest = record(data) or {}
    raw_tasks = manifest.get("tasks")
    tasks = [record(item) or {} for item in raw_tasks] if isinstance(raw_tasks, list) else []
    print(
        json.dumps(
            {
                "integrity_only": True,
                "task_count": len(tasks),
                "verified_count": sum(task.get("execution") == "verified" for task in tasks),
                "assigned_roles": manifest.get("receiving_roles"),
                "errors": errors,
                "notice": (
                    "Checks consistency only, not qualification, authorization or team receipt."
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
