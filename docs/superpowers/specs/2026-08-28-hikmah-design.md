# Hikmah（群贤）产品与技术架构设计

> 状态：已完成交互式设计并获用户逐节批准，等待正式文档复核  
> 日期：2026-08-28  
> GitHub 仓库名：hikmah  
> 产品英文名：Hikmah  
> 产品中文名：群贤

## 1. 文档地位与命名约束

本文是 Hikmah 首个 MVP 的架构事实源。交互画布中出现过的早期工作名称均由本文取代。

只有产品本身具有品牌名：

- 英文名：Hikmah
- 中文名：群贤
- 仓库名：hikmah

Team Space、Channel、Thread、Temporary Group Chat、Expert Seat、Personal Agent、Team Coordinator Sidecar、Channel Coordinator Sidecar、Agent Gateway、AgentLink、Policy / Approval Service、Knowledge、TaskRun 等均为功能标签，不是独立品牌，也不设置独立文化名称。

## 2. 产品愿景

Hikmah 为邀请制私有小团队提供一个人类与 Agent 专家共同参与的协作社区。团队成员在频道、线程和临时群聊中沟通；由 QwenPaw 实现的专业 Agent 以稳定“专家席位”存在；由 AgentScope 构建的团队与频道协调智能体以轻量边车形式维护协作秩序。

Hikmah 的核心不是“让 Agent 多说话”，而是让人类能够在清楚的身份、权限、上下文、审批和审计边界内使用多个专业 Agent。

### 2.1 目标

- 支持 3–20 人的单一私有 Team Space，成员通过邀请加入。
- 支持长期 Channel、Channel 内 Thread，以及独立的 Temporary Group Chat。
- 支持团队拥有、成员共享使用的 Expert Seat；共享专家通常由服务端 QwenPaw 实现。
- 支持成员绑定仅本人可用的 Personal Agent；Personal Agent 可以由成员本机 QwenPaw 提供。
- 支持显式 @专家直达，以及未显式 @时的克制式单主答路由。
- 支持只读自动执行、副作用审批、完整审计和人审知识晋升。
- 保持 AgentScope 与 QwenPaw 的上游代码独立、可升级和可替换。

### 2.2 非目标

首个 MVP 不包含：

- 公开社区、公开频道或陌生人发现；
- 专家市场、计费或商业分成；
- 跨组织联邦；
- 移动原生客户端；
- 复杂无代码工作流编辑器；
- 自动把普通聊天升级为全局记忆；
- 允许 Personal Agent 成为共享频道成员；
- 维护 AgentScope 或 QwenPaw 的私有长期 fork。

### 2.3 MVP 成功标准

一个 3–20 人团队可以完成以下闭环：

1. Owner 创建私有 Team Space 并邀请成员。
2. Admin 创建 Channel、配置共享 Expert Seat 和频道规则。
3. Member 在 Thread 中提出真实团队目标。
4. 显式 @时消息直达指定专家；未显式 @时由 Channel Coordinator Sidecar 选择一名主答专家。
5. 主答专家可以邀请补充专家并形成执行方案。
6. 只读操作自动运行；副作用操作按规则自动放行或展示 Execution Card 请求批准。
7. 执行结果、失败和审批均可审计。
8. 人类可以把有价值的结论审阅、定范围、脱敏并晋升为团队知识。

## 3. 核心设计原则

1. **显式意图优先。** 人类明确 @专家时，系统不得重新路由、改写问题或指定其他主答。
2. **协调边车保持轻量。** Team / Channel Coordinator Sidecar 默认静默，只处理路由、秩序、审批呈现、总结和知识治理，不给出专业结论。
3. **个人与共享身份严格分离。** Personal Agent 永远只属于一个 Member，不能被其他成员调用，也不能直接发布到共享空间。
4. **上下文最小化。** Agent 只获得完成当前任务所需、经授权的上下文。
5. **普通记忆默认不跨频道。** 跨频道知识只能经明确的人类审阅和发布。
6. **策略独立于 Agent。** 副作用是否可执行由 Hikmah 的 Policy / Approval Service 决定，协调边车和专业专家均无权替人类批准。
7. **能力授权而非身份继承。** 不因某个 Agent 属于某位用户，就继承该用户的全部权限。
8. **上游零侵入优先。** 通过 Adapter 和公开接口集成；缺失能力先在 Hikmah 侧适配。
9. **失败必须可见。** 离线、超时、部分失败和状态不明不得被静默掩盖。
10. **所有高影响路径可审计。** 记录上下文授权、路由、邀请、工具提案、审批、执行和知识晋升，但不记录密钥或模型私有推理。

## 4. 系统边界与代码所有权

Hikmah 是独立产品仓库，也是产品领域数据和公共契约的唯一所有者。AgentScope 与 QwenPaw 是上游运行时。

<pre>
Hikmah Web / API
        │
        ├── Collaboration Domain
        │     ├── Identity / RBAC
        │     ├── Team / Channel / Thread / Group Chat
        │     ├── Expert Seat / Personal Agent Binding
        │     ├── TaskRun
        │     ├── Policy / Approval
        │     ├── Knowledge Promotion
        │     └── Audit
        │
        ├── Coordination Adapter ──> AgentScope
        │                              ├── Team Coordinator Sidecar
        │                              └── Channel Coordinator Sidecar
        │
        └── Agent Gateway / AgentLink
              ├── QwenPaw Adapter ──> 服务端共享专家
              └── AgentLink Client ─> 成员本机 Personal Agent
</pre>

### 4.1 Hikmah 拥有

- Team Space、Channel、Thread、Temporary Group Chat 和消息；
- 人类成员、角色、频道可见性和能力授权；
- Expert Seat、Channel Expert Membership 和 Runtime Binding 映射；
- TaskRun、Execution Card、Approval Decision 和执行状态；
- 团队知识、知识晋升流程和审计事件；
- Agent Gateway 的产品级版本化契约。

### 4.2 AgentScope 拥有

- Team / Pipeline / MessageBus 等协调运行语义；
- Team Coordinator Sidecar 与 Channel Coordinator Sidecar 的会话和运行状态；
- 专家邀请及多 Agent 协作的运行时机制。

Hikmah 不读取或写入 AgentScope 私有数据库，不依赖其未公开实现。

### 4.3 QwenPaw 拥有

- Agent Workspace、Skills、Plugins、专业记忆和工具执行环境；
- 服务端共享专家的运行时；
- 成员本机 Personal Agent 的长期记忆和本地资源。

Hikmah 不复制 QwenPaw 私有工作区，不把 Personal Agent 的长期记忆上传到团队服务端。

### 4.4 已检查的上游基线

- AgentScope：提交 6c5c9eedb0a1afe515edcf6f2abec079e7ff6d9a
- QwenPaw：提交 35725c216eb93de790b464034e97795c3a0c7136

设计依据包括 AgentScope 的 Agent Service、Team / Invite / TeamSay、Channel、Session、Message Bus、持久化与 Pipeline 能力，以及 QwenPaw 的多 Agent Workspace、Skills / Plugins、Channel、ChatGroup、ACL、ACP、外部 Agent 委派、权限暂停恢复和流式事件能力。

这些是针对上述本地提交的已验证事实，不承诺未来版本保持内部实现不变。Adapter 必须通过能力探测和契约测试适配固定版本。

### 4.5 上游修改的唯一流程

1. 证明缺失的是可复用的通用扩展点，而不是 Hikmah 私有需求。
2. 在对应上游的独立分支完成最小修改。
3. 向 AgentScope 或 QwenPaw 提交 PR。
4. Hikmah 不依赖未合并的长期本地补丁。
5. 等待上游正式发布后固定新版本，再由 Adapter 启用能力。

禁止 vendor 上游源码、monkey patch 私有实现、直接读写上游数据库或维护长期私有 fork。

## 5. 逻辑组件

| 组件 | 单一职责 | 主要依赖 |
|---|---|---|
| Community Web / API | 提供团队、频道、线程、群聊、消息、Agent 与审批界面 | Collaboration Domain |
| Collaboration Domain | 保存权威领域状态并执行身份、ACL、路由前置规则和 TaskRun 状态机 | 产品数据存储、Audit |
| Coordination Adapter | 把 Hikmah 协作事件翻译为 AgentScope 公共语义，管理两级协调边车 | AgentScope |
| Agent Gateway | 统一 Agent 注册、在线状态、调用、流式事件、取消和错误模型 | QwenPaw Adapter、AgentLink |
| QwenPaw Adapter | 把产品级调用契约映射到 QwenPaw 公开 ACP / API / Plugin 能力 | QwenPaw |
| AgentLink | 为成员本机 Personal Agent 提供认证出站连接和 Owner Scope | Agent Gateway |
| Policy / Approval Service | 评估能力、目标、风险、自动放行规则和人类审批 | RBAC、Audit |
| Knowledge Promotion | 将带来源的知识候选经人审、定范围和脱敏后发布 | Channel Context、Team Knowledge |
| Audit | 记录关键决策与状态变化，支持按权限查询和回放 | 全部产品组件 |

组件之间只通过版本化接口和领域事件通信。AgentScope 或 QwenPaw 内部结构变化不得泄漏到 Community Web / API。

## 6. 两级协调模型

### 6.1 Team Coordinator Sidecar

Team Space 关联一个 AgentScope 构建的 Team Coordinator Sidecar。它是系统范围的轻量协调智能体，不是共享专家。

允许职责：

- 维护团队级 Expert Seat 名册和跨频道治理规则的运行视图；
- 处理明确授权的跨频道治理事件；
- 协调知识候选进入团队级审阅流程；
- 处理全局计划性总结和治理提示。

禁止职责：

- 自行回答专业问题；
- 读取与当前治理事件无关的频道正文；
- 替 Member、Admin 或 Owner 批准副作用；
- 自动把频道内容提升为团队知识。

### 6.2 Channel Coordinator Sidecar

每个 Channel 关联一个 AgentScope 构建的 Channel Coordinator Sidecar。它默认静默、按事件唤醒。

允许介入：

- 未显式 @且通过协作意图门控时选择一名主答专家；
- 请求长期无人响应时提醒或改派一次；
- 多位专家竞争主答时指定单一主答，并让补充者转入 Thread；
- 发现结论冲突时提示主答整合；
- 展示审批、硬规则、定时总结和知识候选。

禁止介入：

- 在明确 @专家的路径中重新路由、总结、调停或邀请其他专家；
- 自行给出专业结论；
- 代替专业专家执行工具；
- 代替人类批准操作。

规则判断优先；只有专长匹配确有歧义时才调用轻量模型。必要时最多提出一个澄清问题。

## 7. 领域模型

### 7.1 人类角色

| 角色 | 权限 |
|---|---|
| Team Owner | 创建 Team Space、任命 Admin、最终治理与恢复权限 |
| Admin | 邀请 Member、配置 Channel、Expert Seat、Channel 规则和低风险自动放行策略 |
| Member | 参与获授权空间、@专家、发起任务、批准本人有权批准的动作、绑定 Personal Agent |

MVP 的产品实例只承载一个私有 Team Space。领域对象仍保留 Team Space 标识，以保持边界清晰，但不提供多租户切换体验。

### 7.2 协作空间

- **Team Space**：成员、共享专家名册、全局规则、团队知识和审计边界。
- **Channel**：长期主题、成员可见性、Expert Seat、响应规则和频道记忆。
- **Thread**：具体讨论或任务的消息、参与者、TaskRun、审批、结果和知识候选。
- **Temporary Group Chat**：独立于 Channel 的临时会话，按显式成员列表授权。默认不创建协调边车；Agent 仅在被明确邀请或 @时参与。内容不会自动进入 Channel 记忆或团队知识。

### 7.3 三类 Agent 身份

#### Shared Expert Seat

Expert Seat 是团队拥有的稳定社交身份，包含名称、头像、专长、职责、可见性和频道权限。它通过版本化 Agent Runtime Binding 指向服务端运行时，通常是 QwenPaw。

更换运行时或升级 Workspace 不改变 Expert Seat 的社交身份和审计连续性。

Channel Expert Membership 把 Expert Seat 分配给指定 Channel，并分别声明：

- 是否可被 @；
- 是否可被智能路由选中；
- 是否可主动补充；
- 可读取哪些上下文和资源；
- 可提议或执行哪些工具能力。

#### Personal Agent

Personal Agent Binding 只绑定一个 Member，可由该成员本机 QwenPaw 提供。

本节及后文所说的 Personal Agent Owner，是指该 Agent 绑定的 Member，不等同于 Team Owner 治理角色。

- 只有 Owner Member 可以调用；
- 不能被其他成员 @；
- 不是 Channel 或 Temporary Group Chat 的共享成员；
- 只能接收 Owner 明确选择的最小上下文；
- 输出默认只对 Owner 可见；
- 不能直接发布共享消息；
- Owner 执行“分享到频道”后，内容才成为新的 Channel 消息。

#### Coordinator Sidecar

Team / Channel Coordinator Sidecar 是系统级协调身份，不是专业 Expert Seat，不拥有业务工具权限。

### 7.4 能力授权

权限按能力和作用域授予，至少分离以下动作：

- 查看 Team / Channel / Thread / Group Chat；
- 读取正文或只读取元数据；
- 回复消息；
- 接收显式 @；
- 被智能路由选中；
- 邀请补充专家；
- 检索团队知识；
- 提议工具调用；
- 执行只读工具；
- 执行副作用工具；
- 审批；
- 发布或撤回团队知识。

默认拒绝。Agent 不继承其 Owner 或创建者的全部权限。

## 8. 消息路由与协作任务流

### 8.1 路径 A：明确 @专家

1. Member 明确 @一名或多名 Expert Seat。
2. Hikmah 验证发言者、空间、专家成员关系和调用能力。
3. Agent Gateway 把消息及最小 Thread Context Envelope 直接投递给指定 QwenPaw。
4. 被 @的每位专家独立响应。
5. Channel Coordinator Sidecar 只观察并记录可审计事件，不改写问题、不选择主答、不邀请他人、不总结、不调停。
6. 专家若提出副作用工具调用，独立 Policy / Approval Service 继续生效；这不构成协调边车介入。

显式 @的专家离线时，系统明确显示离线或失败，不擅自替换为其他专家。

### 8.2 路径 B：未明确 @

1. Channel Coordinator Sidecar 先执行协作意图门控。闲聊、广播和纯人类讨论默认不触发 Agent。
2. 按 Channel 规则、Expert Seat 专长和可用性选择一名主答专家。
3. 仅在规则无法消除歧义时使用轻量模型；必要时提出一个澄清问题。
4. 创建 TaskRun，固定目标、上下文授权、主答席位、预算、超时和状态。
5. Agent Gateway 投递给主答 QwenPaw。
6. 主答专家可通过 AgentScope Team / Invite 语义邀请补充专家。
7. 补充专家把结果交给主答，主答负责统一输出。
8. 需要副作用时进入审批与执行流程。
9. 任务结束后可产生带来源的 Knowledge Candidate，但不能自动发布。

### 8.3 TaskRun 状态机

主路径：

<pre>
OPEN → ROUTED → WORKING
                    ├──→ COMPLETED
                    └──→ AWAITING_APPROVAL → EXECUTING → COMPLETED

任一活动状态可在符合规则时终止为 FAILED 或 CANCELLED。
</pre>

状态规则：

- OPEN：目标已创建，尚未选择运行时。
- ROUTED：已确定目标 Expert Seat 和 Runtime Binding。
- WORKING：专家正在分析、协作或生成方案。
- AWAITING_APPROVAL：存在未获授权的副作用提案。
- EXECUTING：已获授权的精确计划正在执行。
- COMPLETED：结果已落定；不得继续执行工具。
- FAILED：发生明确失败；重试必须创建新的执行尝试并保留关联。
- CANCELLED：人类或系统取消；迟到事件只能记录，不能恢复执行。

## 9. Agent Gateway 最小逻辑契约

本节定义稳定语义，不预先锁定具体序列化格式。

| 契约 | 必需语义 |
|---|---|
| AgentDescriptor | Expert Seat / Personal Agent 标识、runtime type、capabilities、版本、在线状态 |
| ContextEnvelope | Team / Channel / Thread 标识、授权内容引用、来源、敏感级别、能力范围、有效期 |
| Invocation | invocation id、发起者、目标 Agent、direct / routed 模式、目标、ContextEnvelope、deadline |
| AgentEvent | started、stream delta、plan、expert invite、tool proposal、approval required、result、error、cancelled |
| CapabilityGrant | subject、capability、resource scope、expiry、nonce、签发者 |
| ApprovalDecision | approver、plan digest、resource scope、expiry、decision、reason |
| KnowledgeCandidate | source refs、候选内容、建议作用域、敏感级别、提出者 |

所有可重放消息具有唯一 id 和幂等键。协议必须允许能力探测、取消、超时、流式事件和明确错误分类。

## 10. 上下文、记忆与知识

### 10.1 记忆作用域

| 作用域 | 内容 | 跨频道规则 |
|---|---|---|
| Thread / Channel Memory | 普通对话、阶段结论、附件引用 | 默认不跨频道 |
| Expert Stable Memory | 专家身份、专业能力、技能版本、安全约束 | 团队可复用，由 Admin 管理，不从聊天自动改写 |
| Team Knowledge | 已审阅知识对象 | 可按发布范围跨频道检索 |
| Personal Agent Memory | Owner 私有长期记忆和本地资源 | 默认留在本机，不能注入共享专家 |

ContextEnvelope 只包含当前任务需要的授权片段或引用。不得为了“可能有用”而把整个 Channel、其他 Channel 或 Personal Agent 历史交给专家。

### 10.2 知识晋升

唯一允许的跨频道内容晋升流程：

<pre>
Knowledge Candidate
    → 人类审阅
    → 确定适用范围与敏感级别
    → 必要时脱敏
    → 发布 Team Knowledge
    → 版本化、替代或撤回
</pre>

每个团队知识对象必须保存来源、提出者、审阅者、适用范围、敏感级别、版本和当前状态。

硬规则：

- 模型不能自动发布团队知识；
- 总结不等于发布；
- 没有人类明确确认时，内容留在原作用域；
- 撤回后不得再注入新 Invocation，但历史审计仍保留。

### 10.3 Personal Agent 数据

成员本机 QwenPaw 的长期记忆和私有技能留在本机。Hikmah 服务端默认只保存连接状态、调用元数据和审计摘要，不持久化 Personal Agent 的私有请求正文与结果正文。

Owner 主动“分享到频道”时，分享内容成为新的 Channel 消息，并可保留“由 Personal Agent 辅助生成”的来源标记。

## 11. 执行治理

Policy / Approval Service 独立于协调边车和专业专家。

### 11.1 风险分级

| 类别 | 默认处理 |
|---|---|
| 只读、分析、草稿、无外部副作用计算 | 可自动执行，但记录工具、输入范围和结果摘要 |
| 写文件、发消息、修改任务、调用业务系统等副作用 | 请求人类审批；Admin 可预先放行边界清晰的低风险动作 |
| 超出 Agent / Member / Channel / Tool 能力，目标含糊、参数漂移、凭据缺失或策略冲突 | 默认拒绝 |

### 11.2 Execution Card

Execution Card 必须让批准者看见：

- 发起 Member、提出 Expert Seat 和实际 Runtime；
- 工具、目标和标准化后的精确参数；
- 对象数量、外部接收方、影响范围和可回退性；
- diff、消息预览或等价变更摘要；
- 所需能力、策略依据和审批有效期。

### 11.3 审批绑定

Approval Decision 绑定：

- Invocation；
- 工具身份；
- 标准化参数；
- 资源作用域；
- 计划摘要 digest；
- 有效期；
- 单次 nonce。

任何实质变化使审批失效并重新请求。审批不可泛化、不可转让、不可重放。协调边车和专业专家不能成为人类审批者。

策略、身份或审计服务不可用时，副作用操作 fail closed。

## 12. 部署拓扑

### 12.1 私有团队服务器

服务器运行：

- Hikmah Web / API 与 Collaboration Domain；
- 产品数据、Team Knowledge 和 Audit；
- AgentScope 协调运行时；
- Agent Gateway、Policy / Approval Service；
- 服务端共享 QwenPaw 专家池。

共享 QwenPaw 按 Expert Seat 隔离 Workspace、Skills、Plugins 和能力。Admin 负责配置，Member 只能通过产品授权调用。

### 12.2 成员本机

成员可在自己的设备运行 QwenPaw Personal Agent 和 AgentLink Client。

- AgentLink Client 主动建立认证 WebSocket 出站长连接；
- 本机不开放入站端口；
- 连接使用 Owner 绑定、短期、最小能力令牌；
- 服务器只发送 Owner 明确选择的 ContextEnvelope；
- 断线时显示离线，不静默代答；
- 重新连接不会自动重放副作用操作。

### 12.3 首个 MVP 技术栈基线

首个 MVP 采用 Python + React 的类型安全、异步优先技术基线：

- 后端使用 Python 3.14、FastAPI、Pydantic v2、SQLAlchemy 2.x、Alembic、uv、Ruff、mypy strict 和 pytest。
- 前端使用 React 19.2、TypeScript 6.x、Vite 8.x、Node.js 24 LTS、pnpm、TanStack Query、React Router、Vitest 和 Playwright。
- FastAPI 生成版本化 OpenAPI，前端从 OpenAPI 生成 TypeScript 类型与客户端，不手工维护两套公共接口模型。
- 流式 Agent 事件优先使用 SSE；需要双向实时控制、取消或连接状态同步时使用 WebSocket。

上述技术基线必须在不改变本文安全、隐私和所有权边界的前提下，于对应交付切片的 implementation plan 中落地。关系数据库产品、对象存储、部署编排、认证提供方和实时基础设施的具体实现仍属于后续实施选择。

## 13. 可靠性与错误处理

- **显式目标离线：** 明确显示目标专家不可用，不自动替换。
- **协调边车故障：** 显式 @路径仍可直达；未显式 @时请求人类选择专家。
- **部分专家失败：** 主答专家可基于已获得结果完成答复，但必须标记缺失的补充意见。
- **幂等与去重：** Invocation、AgentEvent、Tool Execution 均携带幂等键。
- **重试：** 只对声明幂等的只读操作做有限、带退避重试。
- **副作用状态不明：** 不盲目重试，进入人工核验状态。
- **超时与取消：** deadline 到期或用户取消后停止接受新执行事件；迟到事件只进入审计。
- **背压：** 单 Channel 和单 Agent 设置并发与队列上限；超限明确排队或拒绝。
- **Adapter 不兼容：** 能力探测失败时禁用相关能力并显示版本错误，不尝试调用私有接口。

## 14. 安全与隐私

- 所有资源访问默认拒绝，并同时校验 Human、Agent、Channel 和 Tool 作用域。
- 能力令牌短期有效、Owner 绑定、可撤销并带防重放 nonce。
- Agent 通过受控工具代理访问外部系统，不直接获得用户长期凭据。
- 外部网页、附件、消息和工具输出均视为不可信内容，不能覆盖 Policy 或 Approval 规则。
- ContextEnvelope 记录来源和授权依据，便于泄漏调查。
- Personal Agent 私有正文不对 Team Owner 或 Admin 开放；治理角色只能查看在线状态、资源消耗和必要的运行审计元数据。
- Audit 不保存密钥、令牌、完整环境变量或模型私有推理。
- 团队知识发布前必须确认敏感级别与可见范围。
- 所有“分享到频道”都是 Owner 的显式发布动作，发布后适用 Channel 的保留与审计规则。

## 15. 验证策略

### 15.1 单元测试

- RBAC 与能力判定；
- direct / routed 路由规则；
- TaskRun 状态转换；
- Approval digest 与失效规则；
- Knowledge Promotion 状态机；
- ContextEnvelope 最小化和作用域过滤。

### 15.2 契约测试

- 对固定 AgentScope 版本验证 Team、Invite、TeamSay、Channel、Session、Message Bus 和取消 / 错误映射；
- 对固定 QwenPaw 版本验证 ACP / API、流式事件、权限暂停恢复、Agent Workspace 和 Channel ACL；
- 验证能力探测与不兼容版本的明确失败。

### 15.3 集成测试

- 明确 @一名或多名专家时直达且协调边车不介入；
- 未明确 @时只选择一个主答；
- 主答邀请补充专家并统一整合；
- 只读自动执行；
- 副作用生成 Execution Card；
- 参数改变后旧审批失效；
- Personal Agent 离线、重连和 Owner-only 输出；
- Knowledge Candidate 经人审发布和撤回。

### 15.4 安全测试

- 跨 Channel 上下文泄漏；
- Personal Agent 越权、被他人 @或私有正文对治理角色泄漏；
- CapabilityGrant 重放；
- Prompt injection 试图绕过 Policy；
- 审批参数漂移；
- 审计中出现密钥或私有推理。

### 15.5 端到端验收场景

1. Member 在 Channel 明确 @共享专家，专家响应，Sidecar 只记录。
2. Member 未明确 @提出协作目标，Sidecar 选择主答并创建 TaskRun。
3. 主答提出写操作，系统展示精确 Execution Card；参数变化触发重新审批。
4. Member 调用本机 Personal Agent，结果仅本人可见；主动分享后才进入 Channel。
5. 人类把 Thread 结论晋升为 Team Knowledge，并能撤回。
6. Channel Sidecar 故障时显式 @仍可工作，未 @路径要求人类选专家。

## 16. MVP 交付切片

完整 MVP 跨越协作、Agent 接入、治理、个人运行时和知识五个子系统，不使用一份巨型 implementation plan 一次性交付。按以下顺序形成独立、可验收的切片。

### Slice 1：共享专家直达的协作骨架

- 单一私有 Team Space；
- Owner / Admin / Member；
- Channel、Thread、Temporary Group Chat；
- Expert Seat、Runtime Binding、Channel Expert Membership；
- Agent Gateway 与服务端 QwenPaw Adapter；
- 明确 @专家直达；
- 基础流式响应、离线状态和 Audit。

验收：团队成员能在 Thread 中 @共享 QwenPaw 专家获得流式结果，协调层不改写或重路由。

### Slice 2：轻量协调与多专家协作

- Team / Channel Coordinator Sidecar；
- 未显式 @的协作意图门控；
- 单主答路由；
- TaskRun；
- 主答邀请补充专家；
- 降级和取消。

验收：未 @目标时系统只选择一个主答；Sidecar 故障不会破坏显式 @路径。

### Slice 3：策略、审批与受控执行

- 能力授权；
- Policy / Approval Service；
- Execution Card；
- 只读自动执行；
- 低风险 Admin 预授权；
- 副作用执行、状态不明和人工核验。

验收：任何未授权副作用都不能执行；批准绑定精确计划且不可重放。

### Slice 4：本机 Personal Agent

- Personal Agent Binding；
- AgentLink 出站连接；
- Owner-only ContextEnvelope 和私密流式结果；
- 离线 / 重连；
- Owner 主动分享到 Channel。

验收：其他成员、Team Owner 和 Admin 均无法读取私有正文或调用该 Agent；只有绑定 Member 可以调用。

### Slice 5：团队知识与全面加固

- Knowledge Candidate；
- 人审、定范围、脱敏、发布、版本化和撤回；
- 跨切片安全、可靠性和端到端验证；
- MVP 运维与审计查询。

验收：普通聊天不跨 Channel；只有已发布 Team Knowledge 可在授权 Channel 检索。

用户批准本文后，下一步只为 Slice 1 编写 implementation plan。

## 17. 有意延后的实施选择

以下选择不改变本架构，故不在本文提前锁定：

- 关系数据库和对象存储产品；
- 单进程、容器或编排部署方式；
- 具体认证提供方；
- 实时消息基础设施的具体实现；
- Adapter 的序列化格式和代码语言。

每个实施计划必须基于上述 Python + React 技术栈、当时固定的 AgentScope / QwenPaw 版本，为尚未锁定的基础设施选择最小方案，并满足本文的契约测试、隐私和降级要求。

## 18. 已批准的决策记录

| 决策 | 结果 |
|---|---|
| 产品范围 | 邀请制私有小团队，3–20 人 |
| 协作结构 | 单一 Team Space、Channel、Thread，Temporary Group Chat 独立 |
| 总体架构 | Hikmah 产品层 + AgentScope 协调 + Agent Gateway + QwenPaw 专家 |
| 协调方式 | Team / Channel 两级轻量 Sidecar，默认静默 |
| 显式 @ | 直达指定专家，Channel Sidecar 仅观察 |
| 未显式 @ | 规则优先，歧义时轻量模型，只选择一名主答 |
| 共享专家 | 团队拥有，通常由服务端 QwenPaw 实现 |
| Personal Agent | 仅 Owner 使用，可由成员本机 QwenPaw 实现 |
| 记忆 | 普通对话 Channel-local；跨 Channel 仅人审晋升 |
| 执行 | 只读可自动；副作用审批或 Admin 低风险预授权 |
| 上游代码 | 原则不修改；必要修改仅通过上游 PR 和正式版本 |
| 部署 | 私有团队服务器 + Personal Agent 出站连接 |
| 首个 MVP 技术基线 | Python 3.14 + FastAPI；React 19.2 + TypeScript 6 + Vite 8；OpenAPI 驱动前端契约 |
| 品牌 | GitHub repo 为 hikmah；英文 Hikmah；中文 群贤 |
| 实体命名 | 其他实体不设置独立品牌名 |
| 成册交付 | Markdown 规范 + 自包含 HTML 设计册 + 源画布档案 |

## 19. 设计产物

- 本规范：docs/superpowers/specs/2026-08-28-hikmah-design.md
- HTML 设计册：docs/design-book/hikmah-design-book.html
- 批准记录：docs/design-book/approval-record.md
- 原始画布档案：docs/design-book/source-screens/

HTML 设计册是便于阅读、演示和打印的视觉版本；若与本文存在差异，以本文为准。
