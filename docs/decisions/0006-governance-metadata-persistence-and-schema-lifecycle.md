---
title: ADR-0006：采用 PostgreSQL 管理治理元数据与 Alembic schema 生命周期
description: 规定 Hikmah 薄治理数据的生产持久化、迁移、测试隔离、保留、备份和恢复终态。
document_type: architecture-decision
status: accepted
created: 2026-08-28
updated: 2026-08-28
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - architecture
  - data
  - postgresql
  - migrations
canonical: true
related:
  - 0001-reuse-first-thin-control-plane.md
  - 0004-trusted-identity-and-personal-agent-isolation.md
  - ../architecture/version-baseline.md
  - ../product/overview.md
  - ../project/prd-architecture-review-tracker.md
---

# ADR-0006：采用 PostgreSQL 管理治理元数据与 Alembic schema 生命周期

> **状态**：Accepted（已采纳）
>
> **验证边界**：本文定义数据终态。迁移、备份/恢复和误连保护必须在目标环境验证后才能视为交付完成。

## 1. 背景与约束

Hikmah 只持久化 Expert/Personal Binding、Sidecar Rule、Knowledge Candidate/Review 与 Correlation 等薄治理元数据，不复制 Mattermost 消息正文、QwenPaw 私有会话或 AgentScope 权威运行状态。

生产环境需要并发一致性、受控迁移、备份恢复和审计保留。容器内无持久卷的 SQLite、运行时 `create_all` 和测试复用应用数据库都不能满足这些边界。

## 2. 决策

### 2.1 环境数据库

| 环境 | 数据库 | 约束 |
|---|---|---|
| Production / release qualification | PostgreSQL 16 | Hikmah 独立 database、role 与 credentials；不得复用 Mattermost database/schema/role |
| Integration / E2E | 临时 PostgreSQL 16 | 每次运行独立 database，按迁移初始化并在完成后销毁 |
| Unit test | 内存或临时文件 SQLite，或临时 PostgreSQL | 必须显式 test profile；不得连接任何持久环境 |
| Local development | SQLite 或本地 PostgreSQL | SQLite 只用于单开发者脚手架，不作为兼容性或生产证据 |

同一 PostgreSQL cluster 可以托管 Mattermost 与 Hikmah，但两者必须使用不同 database、role、Secret、备份对象和权限边界。Hikmah 永远不查询 Mattermost database。

### 2.2 Schema 生命周期

- Alembic 是生产和集成环境唯一 schema 迁移机制。
- 每个 schema 变更与领域/API 变更同一交付切片评审，并包含前向迁移、兼容窗口、数据校验和回退/前滚策略。
- 应用启动只检查 schema revision；revision 不兼容时拒绝进入 `ready`，不得自动执行破坏性迁移。
- ORM `create_all/drop_all` 仅允许隔离单元测试；不得用于生产、Spike、集成或恢复流程。
- 破坏性变更采用 expand → migrate → contract，至少跨一个可回退发布窗口。

### 2.3 数据最小化与保留

| 数据 | 默认保留 |
|---|---|
| Expert/Personal Binding、Rule Profile | 活跃期间保留；撤销后保留 30 天审计 tombstone，再删除非必要配置 |
| 未发布或拒绝的 Knowledge Candidate | 最终决定后 90 天 |
| 已发布 Team Knowledge 与版本历史 | 保留至明确撤回/删除；撤回后停止检索注入 |
| Correlation 与治理审计元数据 | 180 天，可由 Team policy 在 30–365 天内调整 |

数据库不保存 Secret 值、Mattermost/QwenPaw 私密正文、模型私有推理或 Personal Agent 请求/结果。外部对象只保存最小 ID、digest、状态、时间和必要审计元数据。

### 2.4 事务与并发

- Knowledge review、规则更新、分享与撤销使用事务和乐观版本控制。
- 写 API 必须接受幂等键或资源版本；冲突返回 `409`，不得覆盖较新状态。
- 外部副作用与数据库不能伪装成单一分布式事务；先记录意图与 correlation，再依据权威系统结果更新派生状态。

### 2.5 测试隔离保护

- 测试 fixture 必须创建专用 Engine/Session 并通过依赖注入传入，不复用应用全局 Engine。
- test profile 必须验证 database 名称、host/临时路径和显式测试标志；不满足保护条件时立即拒绝执行清库操作。
- 测试不得对默认开发或生产 URL 运行 `drop_all`、truncate 或 destructive migration。

### 2.6 备份、恢复与加密

- PostgreSQL 数据卷、备份和传输使用加密；凭据由 Secret 管理，不进入镜像或仓库。
- 每日至少一次自动备份，保留 7 个日备份和 4 个周备份。
- 目标 RPO 为 24 小时，目标 RTO 为 4 小时。
- 每个目标发布版本至少完成一次隔离恢复演练，并验证 schema revision、引用完整性、知识状态和 Correlation 可读性。

## 3. 拒绝的替代方案

- **生产 SQLite**：并发、运维、迁移和恢复边界不足。
- **与 Mattermost 共用 database/schema/role**：违反上游零侵入和故障/权限隔离。
- **应用启动自动建表或破坏性升级**：不可审计且难以回退。
- **复制消息/运行时正文便于查询**：形成第四套事实源并扩大隐私风险。

## 4. 后果与门禁

- 部署资料必须提供 Hikmah 独立 PostgreSQL 初始化、最小权限、迁移、备份和恢复步骤。
- 数据模型或 REST 契约变更必须同步 Alembic、API Client、产品文档和保留影响说明。
- release qualification 必须使用 PostgreSQL；SQLite 测试结果不能证明生产数据库兼容性。
