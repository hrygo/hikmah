# Security Policy

## Project status

Hikmah（群贤）已形成正式目标架构，现有代码仍是未通过生产安全门禁的脚手架。身份、授权与 Personal Agent 隔离以 [ADR-0004](docs/decisions/0004-trusted-identity-and-personal-agent-isolation.md) 为准；外部集成与失败语义以 [ADR-0005](docs/decisions/0005-public-integration-contracts-and-fail-closed-semantics.md) 为准；当前实现与验证差距见[审查跟踪表](docs/project/prd-architecture-review-tracker.md)。在相关证据归档前，不对外声明 production-ready 或已完成安全验证。

## Reporting a vulnerability

请优先通过 GitHub Security Advisories 私下报告漏洞：

- [创建私密安全报告](https://github.com/hrygo/hikmah/security/advisories/new)

如果 Security Advisories 暂不可用，请通过 GitHub 私下联系维护者 [@hrygo](https://github.com/hrygo)。不要在公开 Issue、PR、讨论区、日志或截图中披露可利用细节。

## Please do not include

- 密钥、令牌、完整环境变量或私有仓库地址；
- 成员、客户或 Personal Agent 的私有正文；
- 可直接复现的利用链、攻击载荷或未修复漏洞细节；
- 模型私有推理、内部系统提示或其他不应公开的运行数据。

## Scope

安全报告可以涉及：

- 身份、权限、Agent/插件/工具作用域绕过；
- Cross-Channel 或 Personal Agent 数据泄漏；
- 审批绑定、重放、参数漂移和 fail-closed 失效；
- AgentScope、QwenPaw、Foundation Adapter 的不安全集成；
- 文档、示例或默认配置造成的凭据泄漏。

## Disclosure

维护者会先确认报告、评估影响并协调修复和发布。项目处于早期阶段，当前不承诺固定响应或修复时限；公开披露时间由维护者与报告者根据风险共同决定。

## Security baseline

所有贡献必须：

- 遵循最小权限和默认拒绝；
- 在系统边界校验外部输入和第三方响应；
- 不记录密钥、令牌、完整环境变量或模型私有推理；
- 为高影响路径提供可验证的权限、审批、审计和失败处理证据。
