# Hikmah GitHub 复用调研与组件决策矩阵

> 状态：架构修订的证据基线，等待用户复核  
> 快照日期：2026-08-28  
> 适用范围：Hikmah（群贤）产品、协作底座、Agent 运行时、协议、权限、记忆、审批、工作流与可观测性  
> 结论边界：本报告能降低重复造轮子的概率，但不能对整个 GitHub 做数学意义上的穷尽证明；每个交付切片仍须重新执行复用门禁。

## 1. 调研方法

### 1.1 判定词

| 判定 | 含义 |
|---|---|
| Adopt | 原样部署或直接使用上游能力，不修改上游源码。 |
| Integrate | 通过官方 API、插件、Bot、Webhook 或协议连接。 |
| Borrow | 只借鉴领域模型、交互或安全模式，不形成运行时依赖。 |
| Build-gap | 仅实现没有成熟通用解法、且属于 Hikmah 产品差异化的薄层。 |
| Reject-now | 当前不采用；不代表项目本身质量低。 |

### 1.2 评估维度

每个候选按以下维度评估，GitHub Stars 只作成熟度信号，不作选型结论：

1. 与 3–20 人邀请制人机团队、Channel、Thread、DM 和文件协作的功能贴合度；
2. 许可证、商标、品牌、再分发和未来商业化约束；
3. 最近提交、发布节奏、维护者集中度和升级兼容性；
4. 官方 Bot、插件、Webhook、事件 API 和身份/RBAC 扩展边界；
5. 私有部署、备份、升级、安全加固和日常运维成本；
6. 与 AgentScope、QwenPaw 的现成连接能力；
7. 是否会迫使 Hikmah 维护上游补丁、复制数据或自建通用基础设施。

### 1.3 证据来源

- GitHub 仓库元数据、Release、README、官方文档、许可证和关键源码；
- 本地固定提交的源码与代码图：
  - [AgentScope @ `6c5c9eed`](https://github.com/agentscope-ai/agentscope/tree/6c5c9eedb0a1afe515edcf6f2abec079e7ff6d9a)
  - [QwenPaw @ `35725c21`](https://github.com/agentscope-ai/QwenPaw/tree/35725c216eb93de790b464034e97795c3a0c7136)
- 对所有依赖结论使用公开扩展点做源码核对；本地代码图覆盖检查未报告这些证据路径存在缺口。该结果是当前索引的最佳努力验证，不替代后续版本的契约测试。

## 2. 执行结论

1. **Hikmah 不应建设新的聊天/社区全栈。** Team、Channel、Thread、DM、消息、搜索、文件、通知、基础身份与 RBAC 应由成熟协作底座提供。
2. **Hikmah 应缩成轻量治理与编排控制层。** 只保留 Expert Seat 映射、Sidecar 规则、Personal Agent 私有绑定、人审知识晋升、跨系统关联审计和部署适配。
3. **共享专家直接使用协作底座的原生 Bot/事件通道。** QwenPaw 已有 Mattermost 和 Matrix Channel；也提供公开 Channel 插件注册接口。无需自建 Agent Gateway 或 AgentLink。
4. **AgentScope 已提供 Channel、Team、Session、权限/HITL、持久化、计划任务和 OpenTelemetry 接口。** Hikmah 不再复制这些运行时能力。
5. **最终协作底座不能仅凭文档拍板。** 先执行 Foundation Reuse Spike；Mattermost 是技术首选，Zulip 是许可证路径更清晰的首要备选，Open WebUI Channels 与 CircleChat 分别作为 AI 原生和功能完整度对照。
6. **不引入独立工作流、授权、记忆和观测平台，除非出现已测量的缺口。** Temporal、OpenFGA、OPA、Keycloak、pgvector、Langfuse 等只进入条件候选，不进入 MVP 默认栈。

## 3. 协作底座候选

### 3.1 必须进入 Spike 的四个候选

| 顺序 | 候选 | 已验证价值 | 主要硬门槛 | 当前判定 |
|---:|---|---|---|---|
| 1 | [Mattermost](https://github.com/mattermost/mattermost) | 成熟的 Channel、Thread、DM、文件、搜索、RBAC、Bot/Plugin/WebSocket API；QwenPaw 已内置 Mattermost Channel。2026-08-24 发布 v11.10.1。 | 仓库不同目录、构建物、企业功能和商标存在不同许可规则；必须确认目标发行方式与品牌方案。不得修改核心。 | **Spike 首选；通过许可门禁后 Adopt** |
| 2 | [Zulip](https://github.com/zulip/zulip) | Apache-2.0；Topic 天然承载 Thread；成熟 Bot/Event API、搜索与自托管；2026-08-10 发布 12.2。 | QwenPaw 尚无内置 Zulip Channel，需要在 Hikmah 仓库以公开插件接口实现薄适配。 | **Spike 首要备选；Integrate** |
| 3 | [Open WebUI](https://github.com/open-webui/open-webui) | Channels 已支持人类与 AI 同线讨论、Thread、Reaction、Pin、访问控制、模型/Agent 与 MCP；2026-08-25 发布 v0.11.1。 | 0.6.6 后为带品牌限制的定制许可证；Personal Agent、三类身份和外部 QwenPaw 映射需验证；工具代码具有高权限风险。 | **AI 原生对照；许可与身份门禁** |
| 4 | [CircleChat](https://github.com/tashfeenahmed/circlechat) | 与 Hikmah 目标最相似：人类/Agent 一等身份、Channel、DM、Thread、审批、Agent Runtime、MCP、审计和持久工作流。 | 2026-08-28 观察时项目很年轻、贡献者高度集中、无 GitHub Release；部分部署方式涉及 Docker Socket 高权限。 | **Borrow + 隔离 Spike；不作稳定底座** |

### 3.2 深读结论

#### Mattermost

- [QwenPaw Mattermost Channel](https://github.com/agentscope-ai/QwenPaw/blob/35725c216eb93de790b464034e97795c3a0c7136/src/qwenpaw/app/channels/mattermost/channel.py) 已实现 WebSocket 收取、REST 回复、DM 会话、按 root post 隔离的 Thread 会话、@触发、历史补齐、访问控制和断线重连。
- `thread_follow_without_mention` 可用于同一线程的连续协作，但必须通过测试避免多个专家形成自动回复环。
- [Mattermost Agents 插件](https://github.com/mattermost/mattermost-plugin-agents) 已证明 Agent Pane、DM、@Agent、共享线程上下文和 MCP 工具是可复用路径。
- [Channel Automation 插件](https://github.com/mattermost/mattermost-plugin-channel-automation) 已提供消息/定时/成员事件触发、持久队列和线程回复模式；Hikmah 不应复制通用 Channel Automation 引擎。
- 许可证不能只看仓库顶部标签。Spike 的第一个闸门是确认采用的发行物、源码构建方式、企业功能、品牌和再分发约束。

#### Zulip

- Topic 是强制可见的线程维度，适合把“讨论上下文”留在原 Channel/Topic。
- [Zulip Bot API](https://zulip.com/api/running-bots) 与实时事件 API 可承载共享专家和 Sidecar，无需修改服务器。
- [zulipmcp](https://github.com/zulip/zulipmcp) 已展示 @Agent、按 Stream/Topic 会话、长轮询、历史补齐、禁用机器人和 Stream allowlist 等模式。
- QwenPaw 的 [公开 `register_channel`](https://github.com/agentscope-ai/QwenPaw/blob/35725c216eb93de790b464034e97795c3a0c7136/src/qwenpaw/plugins/api.py#L631) 允许 Zulip 适配留在 Hikmah 仓库，符合“上游零侵入”。

#### Open WebUI Channels

- 产品形态最接近“人与多个 AI 在一个时间线协作”，适合验证专家选择、流式回复和 AI 原生管理体验。
- 它仍然首先是 AI 工作台；Hikmah 的 Team/Channel Sidecar、Owner-only Personal Agent 与人审知识晋升并非一一对应。
- 其定制许可证和品牌要求是长期产品风险；即使当前 3–20 人规模可能落在例外范围内，也不能把当前例外当作未来商业模式保证。

#### CircleChat

- 值得 Borrow 的模式：Agent action allowlist、Context Packet、审批对象、Agent webhook/socket、工作流步骤、审计与模型使用量。
- 不采用其代码作为底座的当前原因不是功能缺失，而是维护集中度、版本成熟度、运维面和高权限部署路径尚未达到基础设施要求。
- 禁止照搬把 Docker Socket 暴露给应用进程的部署方式；这相当于给应用主机级控制能力。

### 3.3 长名单与排除理由

| 候选 | 价值 | 当前处理 |
|---|---|---|
| [Matrix / Synapse](https://github.com/element-hq/synapse) | 开放协议、Room、Thread、AppService、E2EE；QwenPaw 已有 Matrix Channel。 | MVP 不需要联邦/E2EE 带来的复杂度；作为未来隐私或联邦需求的回退项。 |
| [Rocket.Chat](https://github.com/RocketChat/Rocket.Chat) | 成熟自托管协作和 Apps Engine。 | 缺少相对 Mattermost/Zulip 的决定性优势，且 QwenPaw 无现成适配。 |
| [Discourse](https://github.com/discourse/discourse) | 成熟 Topic/Plugin/搜索与社区治理。 | 偏异步论坛，不适合小团队实时 Agent 协作主界面。 |
| [LibreChat](https://github.com/danny-avila/LibreChat) | MIT、多模型、Agent 与 MCP。 | 更像个人/共享 AI Chat，不是完整团队频道底座。 |
| [OpenAgents](https://github.com/openagents-org/openagents) | Apache-2.0，多 Agent Workspace、@、Thread、文件、MCP/A2A。 | 适合借鉴本地 Agent Launcher/Network；人类治理和小团队协作不是其首要模型。 |
| [ClawNet](https://github.com/hkgai-official/ClawNet) | 人类授权身份、作用域权限、审计的多 Agent 社交网络。 | 早期项目；Borrow 治理模式。 |
| [GoRaven](https://github.com/8treenet/goraven) | 团队 Agent Workspace、配额、工具权限、MCP/RAG。 | 与 QwenPaw 运行时职责重叠；Borrow 管理体验。 |

## 4. 组件级复用矩阵

| 组件/能力 | Adopt / Integrate | Hikmah 只保留的 Build-gap | 不再建设 |
|---|---|---|---|
| Team、Channel、Thread、DM、消息、文件、搜索、通知 | Foundation 最终入选者 | 部署配置与产品入口 | Community Web/API、消息库、搜索服务 |
| 基础身份、邀请、角色、Channel ACL | Foundation 原生能力；必要时接 OIDC | Expert/Sidecar/Personal Agent 到平台身份的映射 | 自建用户系统、通用 RBAC 引擎 |
| 共享专业 Agent | QwenPaw 原生 Channel 或外部 Channel Plugin | Expert Seat 配置与 Runtime Binding | 通用 Agent Gateway |
| Team/Channel Sidecar | AgentScope `ChannelBase`、Team、Session 与公开事件接口 | 静默规则、显式 @抑制、未 @单主答选择 | 新协调运行时、私有 AgentScope fork |
| Personal Agent | 本机 QwenPaw 主动连入 Foundation 的 owner-only Bot/DM | Owner 绑定、最小上下文选择与显式分享规则 | AgentLink 服务、入站本机代理 |
| 工具连接 | [MCP](https://github.com/modelcontextprotocol/modelcontextprotocol) | 工具 allowlist 与产品级展示 | 私有工具协议 |
| Agent 间协作 | 先用 Foundation Thread；确需独立远程 Agent 时再接 [A2A](https://github.com/a2aproject/A2A) | Lead Expert 与邀请规则 | MVP 自研 Agent-to-Agent 协议 |
| 前端流式 Agent 事件 | Foundation 原生 UI/Event API；自定义侧栏时再评估 [AG-UI](https://github.com/ag-ui-protocol/ag-ui) | 极少量产品状态映射 | 自建通用前端事件协议 |
| 权限与审批 | Foundation RBAC + [AgentScope PermissionEngine](https://github.com/agentscope-ai/agentscope/blob/6c5c9eedb0a1afe515edcf6f2abec079e7ff6d9a/src/agentscope/permission/_engine.py) + QwenPaw Governance/Approval | Team 规则到两个运行时配置的 Policy Binding、审批关联记录 | 独立 Policy/Approval 决策引擎 |
| 会话、持久运行与计划任务 | AgentScope/QwenPaw 现有 Session、持久化、Scheduler/Cron | 跨系统 correlation id | MVP 工作流引擎、TaskRun 状态机 |
| 专家记忆 | QwenPaw ReMe；AgentScope ReMe/Mem0 适配 | 作用域配置 | 独立通用记忆层 |
| Team Knowledge | AgentScope RAG/ReMe 或简单可审计存储，经 Spike 选择 | 人审晋升、来源、版本、撤回 | 聊天自动跨频道记忆 |
| 事件与消息总线 | Foundation Event API/Webhook；内部边界必要时用 [CloudEvents](https://github.com/cloudevents/spec) 信封 | 幂等与关联映射 | 独立通用 Event Bus（MVP） |
| 可观测性 | [OpenTelemetry](https://github.com/open-telemetry/opentelemetry-specification)；按需接 Langfuse/OpenLIT/Phoenix | 产品级相关字段与脱敏策略 | 自研 Trace/Metric/Log SDK |
| 安全评测与隐私 | 按需使用 [promptfoo](https://github.com/promptfoo/promptfoo)、[garak](https://github.com/NVIDIA/garak)、[Presidio](https://github.com/data-privacy-stack/presidio) | Hikmah 威胁用例、回归集和门禁 | 自研通用红队/PII 引擎 |
| 跨系统审计 | Foundation 审计 + AgentScope/QwenPaw 运行日志 | 只存决策、来源与外部对象引用的关联账本 | 复制保存全部聊天正文 |

## 5. 协议边界

| 协议/接口 | 正确用途 | Hikmah 决策 |
|---|---|---|
| Foundation Bot/Event/Webhook API | 用户、专家、Sidecar 在协作空间中的消息收发与身份呈现 | **主通道** |
| MCP | Agent 发现并调用工具、资源与 Prompt | **Adopt**；工具注解按不可信输入处理 |
| A2A | 独立 Agent 之间交换 Task、Message、Artifact 与流式状态 | **Conditional**；先证明 Foundation Thread 不足。审批不能只靠 A2A Message 传递 |
| ACP | 编辑器/客户端与编码 Agent 的 JSON-RPC 会话 | **不作为 Hikmah Personal Agent 传输层** |
| AG-UI | Agent 到定制前端的事件流 | **Conditional**；仅自建 Agent 侧栏时使用 |
| CloudEvents | 跨系统事件的标准元数据信封 | **Borrow/Conditional**；不是引入新消息总线的理由 |
| OpenTelemetry | Trace、Metric、Log 的供应商中立语义 | **Adopt** |

## 6. 更广的 GitHub 扫描范围

下表记录本轮广泛扫描的代表项目。Stars 为 2026-08-28 观察到的约数，会随时间变化。

| 类别 | 代表项目 | 观察结论 |
|---|---|---|
| 协作/社区 | [Zulip](https://github.com/zulip/zulip) ≈25.8k、[Mattermost](https://github.com/mattermost/mattermost) ≈38.9k、[Rocket.Chat](https://github.com/RocketChat/Rocket.Chat) ≈46.0k、[Synapse](https://github.com/element-hq/synapse) ≈4.6k、[Discourse](https://github.com/discourse/discourse) ≈47.7k、[CircleChat](https://github.com/tashfeenahmed/circlechat) ≈53 | 通用协作能力已成熟，不应重建；差异主要在许可、Agent 接入和运维复杂度。 |
| AI 工作台 | [Open WebUI](https://github.com/open-webui/open-webui) ≈150k、[LibreChat](https://github.com/danny-avila/LibreChat) ≈42.5k、[LobeHub](https://github.com/lobehub/lobehub) ≈82.1k、[AnythingLLM](https://github.com/Mintplex-Labs/anything-llm) ≈65.3k、[Dify](https://github.com/langgenius/dify) ≈153.7k、[Flowise](https://github.com/FlowiseAI/Flowise) ≈55.4k、[Langflow](https://github.com/langflow-ai/langflow) ≈153.8k | 可复用 AI UI、工具和知识模式；多数不是完整团队社区，且部分许可证含额外约束。 |
| Agent 编排 | [AgentScope](https://github.com/agentscope-ai/agentscope) ≈29.8k、[QwenPaw](https://github.com/agentscope-ai/QwenPaw) ≈34.6k、[AutoGen](https://github.com/microsoft/autogen) ≈60.7k、[LangGraph](https://github.com/langchain-ai/langgraph) ≈40.6k、[CrewAI](https://github.com/crewAIInc/crewAI) ≈57.7k、[CAMEL](https://github.com/camel-ai/camel) ≈17.6k、[MetaGPT](https://github.com/FoundationAgents/MetaGPT) ≈70.1k | 用户已确定 AgentScope + QwenPaw；其他项目用于模式和替换性校验，不叠加第二套运行时。 |
| Agent 协议 | [A2A](https://github.com/a2aproject/A2A) ≈25.5k、[MCP](https://github.com/modelcontextprotocol/modelcontextprotocol) ≈9.1k、[ACP](https://github.com/agentclientprotocol/agent-client-protocol) ≈4.1k、[AG-UI](https://github.com/ag-ui-protocol/ag-ui) ≈15.6k、[CloudEvents](https://github.com/cloudevents/spec) ≈5.9k | 采用开放协议，但按职责使用；不能把协议名称当作新基础设施。 |
| 身份/授权 | [OPA](https://github.com/open-policy-agent/opa) ≈12.2k、[OpenFGA](https://github.com/openfga/openfga) ≈5.7k、[Cedar](https://github.com/cedar-policy/cedar) ≈1.7k、[SpiceDB](https://github.com/authzed/spicedb) ≈7.0k、[Casbin](https://github.com/casbin/casbin) ≈20.4k、[Keycloak](https://github.com/keycloak/keycloak) ≈36.5k | 成熟方案充足；MVP 先复用 Foundation 与两个运行时的权限，不叠加授权平台。 |
| 人审/审批 | [HumanLayer](https://github.com/humanlayer/humanlayer) ≈11.3k、[agent-inbox](https://github.com/agent-inbox/agent-inbox) ≈1.1k | 可 Borrow 人审交互；执行授权优先使用 AgentScope/QwenPaw 现成暂停恢复能力。 |
| 记忆/RAG | [ReMe](https://github.com/agentscope-ai/ReMe) ≈3.4k、[Mem0](https://github.com/mem0ai/mem0) ≈64.2k、[Graphiti](https://github.com/getzep/graphiti) ≈30.4k、[Letta](https://github.com/letta-ai/letta) ≈24.5k、[Hindsight](https://github.com/vectorize-io/hindsight) ≈21.5k、[pgvector](https://github.com/pgvector/pgvector) ≈22.8k | 不缺通用记忆引擎；Hikmah 的独特价值是人审晋升和作用域治理。 |
| 观测/评测 | [Langfuse](https://github.com/langfuse/langfuse) ≈33.8k、[Phoenix](https://github.com/Arize-ai/phoenix) ≈11.2k、[OpenLIT](https://github.com/openlit/openlit) ≈2.7k、[OpenTelemetry](https://github.com/open-telemetry/opentelemetry-specification) ≈4.3k、[promptfoo](https://github.com/promptfoo/promptfoo) ≈24.6k、[garak](https://github.com/NVIDIA/garak) ≈9.0k | 复用 OTel 与现成后端/测试工具；逐项核验许可证，尤其是非 OSI 或企业目录。 |
| 持久工作流/事件 | [Temporal](https://github.com/temporalio/temporal) ≈22.6k、[Conductor](https://github.com/conductor-oss/conductor) ≈32.1k、[NATS](https://github.com/nats-io/nats-server) ≈20.6k、[Hatchet](https://github.com/hatchet-dev/hatchet) ≈7.8k、[DBOS](https://github.com/dbos-inc/dbos-transact-py) ≈1.6k、[Restate](https://github.com/restatedev/restate) ≈4.3k | 均比自研可靠；但 MVP 尚无跨运行时长事务证据，因此现在连这些也不引入。 |

## 7. Hikmah 唯一合理的自建薄层

1. **Expert Seat Binding**：把产品中的稳定专家身份映射到 Foundation Bot/Service Account 和固定版本 QwenPaw Workspace。
2. **Sidecar Rule Profile**：显式 @时 Sidecar 只观察；未 @时规则优先、歧义才用轻量模型、只选一名主答。
3. **Personal Agent Binding**：成员本机 QwenPaw 只连接 Owner 私聊，不加入共享 Channel；分享必须由 Owner 明确触发。
4. **Knowledge Promotion**：把来源明确的候选经人类审阅、定范围、脱敏、版本化后发布或撤回。
5. **Correlation Ledger**：关联 Foundation message/thread、AgentScope session、QwenPaw session、tool call、approval 和 trace id；不复制原始聊天事实源。
6. **Deployment Adapter 与 Contract Test**：把选定上游的配置、能力探测和升级验证固定为可重复运行的产品资产。

除此之外的组件默认推定为“应复用”，由提出自建者承担证明责任。

## 8. Foundation Reuse Spike

### 8.1 验收场景

每个入围候选必须在不修改其核心源码的前提下完成同一组场景：

1. 可重复的私有部署、邀请制 Team、Channel、Thread/Topic、DM、文件和搜索；
2. 共享 QwenPaw 专家被 @后流式回复，并保持同一 Thread 上下文；
3. AgentScope Channel Sidecar 可观察所需事件；明确 @专家时产生 **0 次**协调介入；未 @时只选择一名主答；
4. 本机 Personal QwenPaw 仅 Owner 可调用，不能读取或加入共享 Channel；Owner 可显式分享一条新消息；
5. 只读自动运行，副作用通过运行时原生审批暂停/恢复，审批可被人类看见并关联审计；
6. Foundation、AgentScope、QwenPaw 和工具调用可用 correlation id / trace id 贯通，而不复制保存消息正文；
7. 升级到候选的下一个兼容版本后，契约测试仍通过，无核心补丁。

### 8.2 一票否决项

- 许可证、品牌或分发方式不被产品目标接受；
- 必须 fork 或 monkey patch Foundation、AgentScope 或 QwenPaw；
- 必须自建消息、身份、通用审批或通用工作流引擎才能完成 MVP；
- Personal Agent 能读取非 Owner 内容，或 Agent/插件拥有未收敛的主机级权限；
- 明确 @路径中 Sidecar 会改写、重路由、总结或调停；
- 升级只能依靠不可重复的人工补丁。

### 8.3 选型规则

- Mattermost 只有通过许可/品牌门禁后，技术优势才生效；
- 若 Mattermost 许可或品牌门禁失败，Zulip 自动成为首选，不为保留 Mattermost 而绕过规则；
- Open WebUI 只有同时通过许可证、三类身份、外部 QwenPaw 与 Personal Agent 隔离验证时才可入选；
- CircleChat 当前只可被选作参考实现，除非维护/发布成熟度在决策时发生可验证变化；
- 最终选择用新的 ADR 记录，不在本报告中预先伪装成已批准决定。

## 9. 持续“不造轮子”门禁

每个新组件、每个交付 Slice、每次准备引入基础设施前，必须：

1. 写清需求、非需求、数据权威源和安全边界；
2. 在 GitHub 与官方生态检索；可合理比较时至少列出 3 个候选；
3. 核对许可证/商标、最近发布、维护集中度、公开扩展点、安全通告和升级路径；
4. 优先按 Adopt → Integrate → Borrow → Build-gap 顺序决策；
5. 用最小 Spike 验证关键用户旅程、失效模式和升级，不把 README 当作完成证据；
6. 用 ADR 记录选择、拒绝理由、退出条件和再评估触发器；
7. 若必须改 AgentScope/QwenPaw，只提交通用最小上游 PR，等待正式发布并固定版本；
8. 每个版本发布前重新检查依赖许可证、安全通告、SBOM、固定版本和契约测试。

允许自建的证明必须同时回答：现有项目为何不能 Adopt、为何不能 Integrate、为何不能只 Borrow、需要维护多少年、退出和迁移路径是什么。

## 10. 研究后被撤销的早期设计

以下早期概念不再是 Hikmah 的独立组件：

- `Community Web / API`：改为采用 Foundation 原生 Web/API；
- `Collaboration Domain`：Team/Channel/Thread/Message/RBAC 回归 Foundation 权威数据；
- `Agent Gateway / AgentLink`：改为 Foundation 原生 Bot/Event Channel 与 QwenPaw Channel Plugin；
- `Policy / Approval Service`：改为 Foundation RBAC + AgentScope/QwenPaw 原生权限/HITL + 薄 Policy Binding；
- `TaskRun` 工作流状态机：改为跨系统 Correlation Record；持久执行状态由对应运行时拥有；
- 独立 Memory、Scheduler、Workflow、Event Bus、Observability：MVP 不建设。

这次撤销不是减少产品能力，而是把通用能力交还给已经维护它们的上游，让 Hikmah 聚焦“群贤如何被组织、约束和共同使用”。
