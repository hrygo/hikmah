# Contributing to Hikmah

感谢你关注并参与 Hikmah（群贤）的开发与建设。

## Before you start

请先通读核心架构与治理文档：

- [README](README.md)
- [产品与技术架构设计](docs/product/overview.md)
- [目标版本与发布基线](docs/architecture/version-baseline.md)
- [PRD 与技术架构方案审查跟踪表](docs/project/prd-architecture-review-tracker.md)
- [复用优先调研报告](docs/research/2026-08-28-github-reuse-landscape.md)
- [ADR-0001：复用优先的轻量治理控制层](docs/decisions/0001-reuse-first-thin-control-plane.md)
- [ADR-0003：选定 Mattermost 作为协作底座](docs/decisions/0003-adopt-mattermost-as-collaboration-foundation.md)
- [ADR-0004：可信身份与 Personal Agent 隔离](docs/decisions/0004-trusted-identity-and-personal-agent-isolation.md)
- [ADR-0005：公开集成契约与 fail-closed 语义](docs/decisions/0005-public-integration-contracts-and-fail-closed-semantics.md)
- [ADR-0006：治理元数据持久化与 schema 生命周期](docs/decisions/0006-governance-metadata-persistence-and-schema-lifecycle.md)

所有贡献与实现均需严格遵循已批准的 Accepted ADR 与产品事实源规范。

当前仓库代码是架构脚手架。审查跟踪表中的 `CR-*` 只记录潜在工作；只有独立 Issue/任务明确授权后才能实施，且不得用脚手架构建通过替代真实集成或发布证据。

## Contribution principles

1. **Design first.** 涉及公共接口、数据边界、权限、隐私、部署或上游集成的改动，先提交设计说明和验收标准。
2. **Reuse first.** 新增组件依次评估 Adopt、Integrate、Borrow、Build-gap；没有证据证明前三者不足时，不自建通用基础设施。
3. **Upstream zero-intrusion.** AgentScope、QwenPaw 与 Mattermost 坚持非侵入集成，原则上不修改上游核心；通用扩展点只通过对应上游的最小 PR 提交。
4. **Least privilege.** Agent、插件和工具只获得完成任务所需的最小作用域。
5. **Auditable changes.** 高影响路径必须说明身份、能力、数据来源、审批和审计影响。

## Workflow

1. 先在 Issue 中说明问题、用户影响和非目标。
2. 需要架构决策时，在 `docs/decisions/` 增加 ADR，并明确状态、替代方案、退出条件和验收门禁。
3. 需要实现时，为一个独立 Slice 编写 implementation plan，再按小步提交代码。
4. 在 PR 中链接 Issue、设计文档和验证证据；保持每个提交只包含一个逻辑变化。
5. 合并前重新检查依赖许可证、敏感信息、权限边界和上游兼容性。

## Technology baseline

Hikmah 目标技术基线如下；精确版本与支持状态只以[目标版本与发布基线](docs/architecture/version-baseline.md)为准：

- **后端 (Backend)**：Python 3.14.x、FastAPI、Pydantic v2、SQLAlchemy 2.x、Alembic、uv、Ruff、mypy (--strict) 和 pytest；
- **前端 (Frontend)**：React 19.2.x、TypeScript 6.0.x、Vite 8.x、Node.js 24 LTS、pnpm、TanStack Query、React Router、Vitest 和 Playwright；
- **协作底座集成 (Foundation)**：Mattermost Web App Plugin (React/TS) + Bot API & WebSocket 事件流；
- **契约与流式**：FastAPI OpenAPI 驱动前端 TypeScript 客户端；流式事件采用 SSE，双向控制采用 WebSocket。

所有代码 PR 必须附带适用的 lint、typecheck、unit/integration test 和 end-to-end test 验证结果，杜绝无测试验证的提交。


## Pull requests

PR 描述至少包含：

- 变更目标、范围和明确的非目标；
- 关联 Issue、ADR 或 implementation plan；
- 本地验证命令与完整结果；
- 用户可见行为、数据迁移、权限、隐私和审计影响；
- AgentScope、QwenPaw 或协作底座的兼容性影响；
- 未包含密钥、令牌、私有环境变量、模型私有推理或无关重构。

## Commit messages

使用 Conventional Commits 风格，例如：

- docs: clarify the reuse boundary
- feat: add a scoped sidecar rule
- fix: reject an expired capability grant
- test: cover explicit mention routing
- chore: update development tooling

## Security and conduct

请勿在公开 Issue、PR 或日志中提交凭据、个人私有数据、可利用细节或模型私有推理。安全问题请遵循 [SECURITY.md](SECURITY.md)；行为准则见 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

## License

提交到本仓库的内容默认按 [Apache-2.0](LICENSE) 发布，除非贡献者在提交时明确声明其他适用条款。
