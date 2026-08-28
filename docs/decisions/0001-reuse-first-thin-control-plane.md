# ADR-0001：复用优先的轻量治理控制层

- 状态：Accepted（复用优先原则）；具体轻量控制层边界随架构修订稿等待用户复核
- 日期：2026-08-28
- 决策者：产品设计会话；“不重复造轮子”原则由用户明确批准
- 关联：[GitHub 复用调研](../research/2026-08-28-github-reuse-landscape.md)

## Context

早期 Hikmah 设计把 Community Web/API、Team/Channel/Thread/Message、RBAC、Agent Gateway、AgentLink、Policy/Approval、TaskRun、Memory、Scheduler 和 Audit 视为产品自有组件。

GitHub 广泛调研和固定提交源码核对表明：

- Mattermost、Zulip、Open WebUI Channels 等已覆盖团队消息、Thread、文件、搜索、身份、权限和 Bot/Event 接入；
- QwenPaw 已提供多种协作 Channel、公开 Channel 插件注册、ReMe、Governance/Approval、Cron、MCP/A2A/ACP 能力；
- AgentScope 已提供 Channel、Team、Session、权限/HITL、持久化、计划任务和 OpenTelemetry；
- MCP、A2A、AG-UI、CloudEvents 和 OpenTelemetry 已分别覆盖工具、Agent 间协作、前端事件、事件信封与观测协议；
- 授权、工作流、记忆和 LLM 观测领域也已有成熟项目，当前没有证据支持 Hikmah 复制这些通用能力。

继续按早期设计建设会增加重复实现、许可证误判、安全攻击面、数据双写、升级耦合和长期维护负担。

## Decision

用户已明确接受“系统设计不重复造轮子”和“所有组件先做广泛 GitHub 调研”的原则。根据本轮证据，修订稿进一步把 Hikmah 定位为成熟协作 Foundation、AgentScope 与 QwenPaw 之上的**轻量治理与编排控制层**；这个具体边界须随完整修订稿一起复核。

所有组件按以下优先级决策：

1. Adopt 上游原生能力；
2. 通过官方 API、插件、Bot、Webhook 或开放协议 Integrate；
3. 只 Borrow 可复用模式；
4. 最后才 Build-gap，且只实现 Hikmah 特有语义。

Hikmah 自有范围收敛为：

- Expert Seat 与 Foundation/QwenPaw Runtime Binding；
- Team/Channel Sidecar 的静默、显式 @抑制与未 @单主答规则；
- owner-only Personal Agent 绑定、最小上下文和显式分享；
- 人审 Knowledge Promotion、来源、作用域、版本与撤回；
- 跨 Foundation、AgentScope、QwenPaw、工具与审批的 Correlation Ledger；
- 部署适配、能力探测、契约测试和升级门禁。

以下内容不再作为 Hikmah 独立基础设施：聊天 Web/API、消息库、搜索、用户系统、通用 RBAC、Agent Gateway、AgentLink、通用审批决策引擎、TaskRun 工作流引擎、通用记忆、Scheduler、Event Bus 和 Observability SDK。

AgentScope 与 QwenPaw 原则上不修改。确认缺少通用扩展点时，只提交最小上游 PR；Hikmah 等待正式发布并固定版本，不依赖未合并补丁或长期私有 fork。

## Consequences

### Positive

- MVP 工作量和攻击面显著缩小；
- 消息、权限、文件、搜索、会话、审批和升级由成熟社区持续维护；
- AgentScope、QwenPaw 与协作底座可独立升级和替换；
- 产品差异集中在人机协作规则、身份边界和知识治理。

### Negative

- 产品 UI 和部分交互会受 Foundation 扩展边界约束；
- 必须持续跟踪许可证、商标、安全公告和兼容版本；
- 跨系统排障依赖良好的 correlation id、契约测试和版本清单；
- Foundation 迁移成本必须通过薄适配与数据权威边界控制。

## Rejected alternatives

1. **从零建设完整社区平台**：重复实现成熟能力，维护面最大。
2. **直接 fork 某个相似 AI 社区项目**：短期看似更快，长期继承核心补丁和升级负担。
3. **把 AgentScope 或 QwenPaw 改造成产品后端**：污染上游职责，违背可替换和上游零侵入边界。
4. **提前叠加 OPA/OpenFGA、Temporal、独立向量库和观测平台**：当前没有被测量的缺口，属于基础设施先行。

## Compliance gate

任何新增组件的设计或实现 PR 都必须链接复用调研或补充记录，并回答 Adopt / Integrate / Borrow 为何均不足。没有证据时默认不允许自建。
