# Contributing to Hikmah

感谢你关注 Hikmah（群贤）。项目当前处于设计与复用验证阶段，尚未进入产品代码实现；贡献应先帮助我们收敛正确的边界，再进入实现。

## Before you start

请先阅读：

- [README](README.md)
- [产品与技术架构设计](docs/superpowers/specs/2026-08-28-hikmah-design.md)
- [复用优先调研](docs/research/2026-08-28-github-reuse-landscape.md)
- [ADR-0001：复用优先的轻量治理控制层](docs/decisions/0001-reuse-first-thin-control-plane.md)
- [ADR-0002：Foundation Reuse Spike](docs/decisions/0002-collaboration-foundation-spike.md)

Proposed 状态的 ADR 仍是待复核方案，不能当作已批准的实现决定。

## Contribution principles

1. **Design first.** 涉及公共接口、数据边界、权限、隐私、部署或上游集成的改动，先提交设计说明和验收标准。
2. **Reuse first.** 新增组件依次评估 Adopt、Integrate、Borrow、Build-gap；没有证据证明前三者不足时，不自建通用基础设施。
3. **Upstream zero-intrusion.** AgentScope 与 QwenPaw 原则上不修改；通用扩展点只通过对应上游的最小 PR 提交。
4. **Least privilege.** Agent、插件和工具只获得完成任务所需的最小作用域。
5. **Auditable changes.** 高影响路径必须说明身份、能力、数据来源、审批和审计影响。

## Workflow

1. 先在 Issue 中说明问题、用户影响和非目标。
2. 需要架构决策时，在 docs/decisions/ 增加 ADR，并明确状态、替代方案、退出条件和验收门禁。
3. 需要实现时，为一个独立 Slice 编写 implementation plan，再按小步提交代码。
4. 在 PR 中链接 Issue、设计文档和验证证据；保持每个提交只包含一个逻辑变化。
5. 合并前重新检查依赖许可证、敏感信息、权限边界和上游兼容性。

## Technology baseline

未来产品代码使用：

- Python 3.14、FastAPI、Pydantic v2、SQLAlchemy 2.x、Alembic、uv、Ruff、mypy 和 pytest；
- React 19.2、TypeScript 6、Vite 8、Node.js 24 LTS、pnpm、TanStack Query、React Router、Vitest 和 Playwright；
- FastAPI OpenAPI 驱动前端 TypeScript 客户端；流式事件按需要使用 SSE 或 WebSocket。

当前没有可运行的应用测试或构建命令。实现 Slice 后，PR 必须报告适用的 lint、typecheck、unit/integration test 和 end-to-end test 输出，不能用“看起来能工作”替代证据。

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

