---
title: Hikmah Documentation Reorganization Plan
description: 将 Hikmah 文档重组为开源项目可维护的信息架构，并统一文档 metadata 与状态。
document_type: implementation-plan
status: completed
created: 2026-08-28
updated: 2026-08-28
owners:
  - hikmah-maintainers
audience:
  - maintainers
tags:
  - documentation
  - information-architecture
canonical: false
related:
  - ../product/overview.md
  - ../project/documentation-policy.md
---

# Hikmah Documentation Reorganization Implementation Plan

> 执行状态：已完成。本文保留为文档信息架构迁移的审计记录。

> **For agentic workers:** Execute this plan task-by-task in the current repository. Preserve approved content and historical artifacts; do not change product decisions while reorganizing documentation.

**Goal:** 将 Hikmah 文档整理为面向开源用户、贡献者和维护者的稳定目录，统一 metadata、生命周期、导航和相对链接。

**Architecture:** 保留 GitHub 需要原生发现的根目录社区文件；产品、架构、决策、研究、设计、开发规则和历史资料统一由 `docs/` 管理。当前批准内容不拆写、不改义，只调整事实源位置、状态标识和导航。

**Tech Stack:** GitHub Flavored Markdown、YAML front matter、HTML metadata、Git。

**Spec:** 本计划依据 2026-08-28 已批准的文档架构方案：生命周期分层，并保留根目录 GitHub 入口文件。

## Global Constraints

- 根目录 `README.md`、`CONTRIBUTING.md`、`SECURITY.md`、`CODE_OF_CONDUCT.md`、`LICENSE` 保持原位。
- 不删除历史 HTML 源片段或 `manifest.sha256`。
- 不改变 ADR 状态和产品结论；只把现有状态规范化为 metadata。
- Markdown 文档使用 YAML front matter；完整 HTML 使用 `<meta name="hikmah:*">`；HTML 片段使用顶部 metadata 注释。
- 所有迁移后的内部链接必须有效。
- `docs/superpowers/` 在迁移完成后不存在。

---

### Task 1: 建立文档治理与导航入口

**Files:**

- Create: `docs/README.md`
- Create: `docs/project/documentation-policy.md`
- Create: `docs/architecture/README.md`
- Create: `docs/decisions/README.md`
- Create: `docs/research/README.md`
- Create: `docs/design/README.md`
- Create: `docs/development/README.md`
- Create: `docs/archive/README.md`

**Acceptance:** 每个入口说明目标读者、事实源、文档状态和下一阅读路径；metadata schema 与状态枚举只有一个定义位置。

### Task 2: 迁移现有文档到稳定目录

**Moves:**

- `docs/superpowers/specs/2026-08-28-hikmah-design.md` → `docs/product/overview.md`
- `docs/superpowers/specs/2026-08-28-hikmah-github-bootstrap-design.md` → `docs/archive/github-bootstrap/design.md`
- `docs/superpowers/plans/2026-08-28-hikmah-github-bootstrap.md` → `docs/archive/github-bootstrap/implementation-plan.md`
- `docs/superpowers/plans/2026-08-28-documentation-reorganization.md` → `docs/archive/documentation-reorganization-plan.md`
- `docs/design-book/hikmah-design-book.html` → `docs/design/hikmah-design-book.html`
- `docs/design-book/approval-record.md` → `docs/design/approval-record.md`
- `docs/design-book/source-screens/` → `docs/archive/design-sources/`

**Acceptance:** 内容无丢失；历史文件明确标为 archived；设计册与批准记录仍可访问。

### Task 3: 为全部文档添加 metadata

**Rules:**

- 所有 `docs/**/*.md` 包含 `title`、`description`、`document_type`、`status`、`created`、`updated`、`owners`、`audience`、`tags`、`canonical`。
- ADR 保持 `accepted` 或 `proposed`；研究报告为 `review`；产品事实源为 `review`；索引和治理规则为 `active`；历史材料为 `archived`。
- 完整 HTML 在 `<head>` 中添加 `hikmah:title`、`hikmah:document-type`、`hikmah:status`、`hikmah:created`、`hikmah:updated`、`hikmah:canonical`。
- HTML 片段首部使用不会改变渲染的 metadata 注释。

**Acceptance:** 不再使用正文引用块或列表模拟文档属性；正文中的业务状态说明可保留。

### Task 4: 修复导航与引用

**Files:**

- Modify: `README.md`
- Modify: all moved Markdown/HTML documents containing relative paths

**Acceptance:** 根 README 指向 `docs/README.md` 和新的事实源；Markdown 与 HTML 相对链接都指向迁移后的路径；历史计划中的命令与路径作为历史记录保留原文，但其 metadata 明确为 archived。

### Task 5: 验证文档完整性

**Checks:**

- 枚举 `docs/`，确认不存在 `docs/superpowers/` 和 `docs/design-book/`。
- 校验所有 Markdown 文档有完整 front matter。
- 校验 Markdown 相对链接指向存在文件。
- 校验 HTML 设计册链接和 metadata。
- 对迁移前后文档集合与源片段 SHA-256 manifest 做完整性检查。
- 运行 `git diff --check` 和敏感信息扫描。

**Acceptance:** 所有检查通过；Git 状态只包含本次文档重组。
