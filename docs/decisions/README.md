---
title: Hikmah 架构决策记录
description: Hikmah Architecture Decision Records 的状态索引和维护入口。
document_type: documentation-index
status: active
created: 2026-08-28
updated: 2026-08-28
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - architecture
  - decisions
canonical: false
related:
  - ../project/documentation-policy.md
  - ../project/prd-architecture-review-tracker.md
---

# Hikmah 架构决策记录

ADR 记录成本高、难以逆转的技术决定及其理由。旧 ADR 不删除；决定变化时通过新的 ADR 或 `superseded_by` 建立历史链。

| ADR | 状态 | 决定 |
|---|---|---|
| [ADR-0001](0001-reuse-first-thin-control-plane.md) | Accepted | 复用优先，只建设 Hikmah 必需的轻量治理控制层 |
| [ADR-0002](0002-collaboration-foundation-spike.md) | Superseded | 通过同场景 Spike 评估协作底座候选方案 |
| [ADR-0003](0003-adopt-mattermost-as-collaboration-foundation.md) | Accepted | 选定 Mattermost 作为 Hikmah 协作底座与 UI 宿主 |
| [ADR-0004](0004-trusted-identity-and-personal-agent-isolation.md) | Accepted | 使用 Mattermost 可信身份并严格隔离 Personal Agent |
| [ADR-0005](0005-public-integration-contracts-and-fail-closed-semantics.md) | Accepted | 只采用公开集成契约并统一 fail-closed 失败语义 |
| [ADR-0006](0006-governance-metadata-persistence-and-schema-lifecycle.md) | Accepted | 使用 PostgreSQL 与 Alembic 管理治理元数据生命周期 |

状态生命周期和 metadata 规则见[文档治理规范](../project/documentation-policy.md)。

ADR 的 `Accepted` 只表示终态决策已接受，不自动证明代码、运行、升级或法律门禁已经通过。实现与验证状态见 [PRD 与技术架构方案审查跟踪表](../project/prd-architecture-review-tracker.md)。
