# Hikmah API

Hikmah API 是目标架构中的 FastAPI 薄治理与编排控制面，负责可信 Actor 投影、Shared Expert/Personal Agent Binding、Sidecar Rule、Knowledge Promotion 与 Correlation，不拥有 Mattermost 消息、QwenPaw 会话或 AgentScope 运行状态。

## 当前状态

本目录是架构脚手架，不代表认证、公开适配器、数据库迁移或发布门禁已经完成。不得在真实用户或生产环境使用当前接口作为安全边界。

## 正式契约

- [产品与技术架构](../../docs/product/overview.md)
- [ADR-0004：可信身份与 Personal Agent 隔离](../../docs/decisions/0004-trusted-identity-and-personal-agent-isolation.md)
- [ADR-0005：公开集成契约与 fail-closed 语义](../../docs/decisions/0005-public-integration-contracts-and-fail-closed-semantics.md)
- [ADR-0006：治理元数据持久化与 schema 生命周期](../../docs/decisions/0006-governance-metadata-persistence-and-schema-lifecycle.md)
- [审查跟踪表](../../docs/project/prd-architecture-review-tracker.md)

正式实现必须从 Mattermost OAuth/BFF session 解析可信 Actor，不接受调用方自报身份；生产数据使用独立 PostgreSQL 16 database/role 并由 Alembic 迁移；未配置、不可达、mock 或 fallback 不能表示为 `ok`、`ready` 或 `completed`。
