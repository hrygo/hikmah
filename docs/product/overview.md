---
title: Hikmah（群贤）产品与技术架构设计
description: Hikmah 的产品愿景、系统边界、领域模型、Agent 协作规则和 MVP 技术架构事实源。
document_type: product-spec
status: active
created: 2026-08-28
updated: 2026-08-28
owners:
  - hikmah-maintainers
audience:
  - users
  - contributors
  - maintainers
tags:
  - product
  - architecture
  - agents
canonical: true
related:
  - ../research/2026-08-28-github-reuse-landscape.md
  - ../research/2026-08-28-mattermost-zulip-webui-integration.md
  - ../decisions/0001-reuse-first-thin-control-plane.md
  - ../decisions/0002-collaboration-foundation-spike.md
  - ../decisions/0003-adopt-mattermost-as-collaboration-foundation.md
  - ../decisions/0004-trusted-identity-and-personal-agent-isolation.md
  - ../decisions/0005-public-integration-contracts-and-fail-closed-semantics.md
  - ../decisions/0006-governance-metadata-persistence-and-schema-lifecycle.md
  - ../architecture/version-baseline.md
  - ../project/prd-architecture-review-tracker.md
---

# Hikmah（群贤）产品与技术架构设计

> GitHub 仓库名：`hikmah`；产品英文名：Hikmah；产品中文名：群贤。
>
> 调研基线：[GitHub 复用调研与组件决策矩阵](../research/2026-08-28-github-reuse-landscape.md)

## 1. 文档地位与命名约束

本文是 Hikmah 首个 MVP 的产品与技术架构事实源，使用规范性语言定义产品终态。早期“控制面 + 自建 Agent Gateway”的实现架构已被复用优先架构替代。

终态要求与交付状态严格分离：本文和 Accepted ADR 定义系统必须达到的行为；[审查跟踪表](../project/prd-architecture-review-tracker.md)记录脚手架差距、实现授权和验证证据。目标要求不得因当前实现缺失而降级，未验证能力也不得据此宣称已经交付。

只有产品本身具有品牌名：

- 英文名：Hikmah
- 中文名：群贤
- GitHub 仓库名：hikmah

Team Space、Channel、Thread、Temporary Group Chat、Expert Seat、Personal Agent、Team Coordinator Sidecar、Channel Coordinator Sidecar、Knowledge Promotion、Correlation Record 等均为功能标签，不设置独立品牌名。

## 2. 产品愿景

Hikmah 为邀请制私有小团队提供一个人类与 Agent 专家共同参与的协作社区。团队成员在 Channel、Thread 和 Temporary Group Chat 中沟通；由 QwenPaw 实现的专业 Agent 以稳定 Expert Seat 存在；由 AgentScope 构建的 Team / Channel Coordinator Sidecar 以轻量边车形式维护协作秩序。

Hikmah 的核心不是重新实现聊天平台，也不是让 Agent 多说话，而是让人类在清楚的身份、权限、上下文、审批和审计边界内共同使用多个专业 Agent。

### 2.1 目标

- 支持 3–20 人的单一私有 Team Space，成员通过邀请加入；
- 支持长期 Channel、Channel 内 Thread，以及独立 Temporary Group Chat；
- 支持团队拥有、成员共享使用的 Expert Seat；共享专家通常由服务端 QwenPaw 实现；
- 支持成员绑定仅本人可用的 Personal Agent；Personal Agent 可以由成员本机 QwenPaw 提供；
- 支持显式 @专家直达，以及未显式 @时克制的单主答路由；
- 支持只读自动执行、副作用审批、关联审计和人审知识晋升；
- 通过成熟 Foundation 和公开扩展点交付，不复制通用聊天、身份、工作流、记忆或观测系统；
- 保持 Foundation、AgentScope 与 QwenPaw 可独立升级、可替换、无长期私有 fork。

### 2.2 非目标

首个 MVP 不包含：

- 公开社区、公开 Channel、陌生人发现或跨组织联邦；
- 专家市场、计费或商业分成；
- 自研 Team/Channel/Thread/Message、搜索、文件和通知平台；
- 自研用户系统、通用 RBAC/Policy、通用工作流、消息总线、记忆或观测平台；
- 移动原生客户端；
- 复杂无代码工作流编辑器；
- 自动把普通聊天升级为全局记忆；
- 允许 Personal Agent 成为共享 Channel 成员；
- 修改或长期 fork Foundation、AgentScope、QwenPaw。

### 2.3 MVP 成功标准

一个 3–20 人团队能在被选定的协作 Foundation 上完成：

1. Owner 创建私有 Team Space 并邀请成员；
2. Admin 创建 Channel、配置共享 Expert Seat 和频道规则；
3. Member 在 Thread 中提出真实团队目标；
4. 显式 @时由 Foundation 直达指定专家；未显式 @时由 Channel Coordinator Sidecar 选择一名主答专家；
5. 主答专家按规则邀请补充专家，并在同一 Thread 形成可见结果；
6. 只读操作自动运行；副作用按运行时规则自动放行或暂停等待人类批准；
7. 消息、Agent 会话、工具、审批与 Trace 可关联审计，且不复制聊天事实源；
8. 人类可以把有价值的结论审阅、定范围、脱敏并晋升为团队知识；
9. 成员本机 Personal QwenPaw 仅本人可用，不能读取共享 Channel，结果由本人确认后分享；
10. Foundation 的兼容升级不需要核心补丁，契约测试仍通过。

## 3. 核心设计原则

1. **复用优先，不重复造轮子。** 任何组件依次检查 Adopt、Integrate、Borrow，只有证明确有产品特有缺口时才 Build-gap。
2. **显式意图优先。** 人类明确 @专家时，系统不得重新路由、改写问题或指定其他主答。
3. **协调边车保持轻量。** Team / Channel Coordinator Sidecar 默认静默，只处理路由、秩序、审批呈现、总结和知识治理，不给专业结论。
4. **个人与共享身份严格分离。** Personal Agent 永远只属于一个 Member，不能被其他成员调用，也不能直接发布到共享空间。
5. **上下文最小化。** Agent 只获得完成当前任务所需、经授权的上下文。
6. **普通记忆默认不跨 Channel。** 跨 Channel 知识只能经明确的人类审阅和发布。
7. **权限在权威系统内执行。** Foundation 控制协作访问；AgentScope/QwenPaw 控制各自工具执行与 HITL；Hikmah 只绑定和展示规则，不复制决策引擎。
8. **能力授权而非身份继承。** Agent 不继承 Owner、创建者或 Bot 管理员的全部权限。
9. **上游零侵入。** 只用公开 API、Bot、Webhook、Plugin 与开放协议；必要扩展只走通用最小上游 PR。
10. **单一事实源。** 消息、运行状态、审批和知识各自只有一个权威所有者；Hikmah 只保存关联与产品特有元数据。
11. **失败必须可见。** 离线、超时、部分失败和状态不明不得被静默掩盖。
12. **高影响路径可审计。** 记录授权、路由、工具提案、审批、执行和知识晋升，但不记录密钥、无关私密正文或模型私有推理。

## 4. 复用决策与证据边界

### 4.1 终态架构结论

Hikmah 是成熟协作 Foundation、AgentScope 和 QwenPaw 之上的**轻量治理与编排控制层**，不是新的社区全栈。

```text
Human Web / Desktop / Mobile Client
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ Mattermost Collaboration Foundation                 │
│ Identity · Invite · Team · Channel · Thread · DM    │
│ Message · File · Search · Notification · RBAC       │
└──────────────┬──────────────────┬───────────────────┘
               │ Plugin/OAuth/Bot/Event
               ▼
        Hikmah Web App Plugin + Python BFF
        Identity · Bindings · Rules · Knowledge
        Correlation · Contracts · Governance API
               │                         │
        ┌──────▼───────┐          ┌──────▼────────────┐
        │ AgentScope   │          │ QwenPaw           │
        │ Sidecars     │          │ Shared Channels   │
        └──────────────┘          │ Personal Runtime  │
                                  └───────────────────┘
```

Foundation 是协作事实源；AgentScope 和 QwenPaw 是各自运行事实源；Hikmah 不把三者的数据复制成第四套完整状态。

### 4.2 协作底座正式选型 (Mattermost)

团队已正式通过 [ADR-0003](../decisions/0003-adopt-mattermost-as-collaboration-foundation.md) 采纳 **Mattermost** 作为 Hikmah 的团队协作底座与 UI 宿主。精确目标版本由[版本基线](../architecture/version-baseline.md)唯一维护：

| 维度 | 正式方案与决议 |
|---|---|
| **协作数据面** | 由 Mattermost 统一承载 Team、Channel、Thread、DM、文件上传、全文搜索与基础 RBAC 权限。 |
| **UI 宿主与扩展** | 生产界面采用 **Mattermost Web App Plugin** 注入 RHS、Custom Post 与治理工作台；独立 SPA 只用于开发预览。 |
| **交互式身份** | Python BFF 使用 Mattermost OAuth 2.0 Authorization Code + PKCE，浏览器只持有安全的 Hikmah 会话 Cookie。 |
| **通信与事件集成** | 通过 Mattermost 官方 REST API (v4) 与 WebSocket 事件流实现双向消息编排与 Sidecar 监听，严格遵守非侵入集成原则。 |
| **双核心 Agent 运行时** | 唯一绑定 **QwenPaw**（共享专家与个人 Runtime）和 **AgentScope**（Team/Channel Coordinator）；Hikmah 不建设通用 Runtime Gateway。 |


### 4.3 持续复用门禁

每个新组件和交付切片都必须：

1. 写清需求、非需求、权威数据源和安全边界；
2. 检索 GitHub 与官方生态，可合理比较时至少列出三个候选；
3. 核对许可/品牌、发布活跃度、维护集中度、扩展点、安全公告和升级路径；
4. 进行最小 Spike 和故障/升级验证；
5. 用 ADR 记录 Adopt / Integrate / Borrow / Build-gap、退出条件与再评估触发器。

这是一套持续证据流程，不宣称对 GitHub 的绝对穷尽保证。

## 5. 系统边界与代码所有权

### 5.1 Collaboration Foundation 拥有

- 用户账户、邀请、基础角色和 Channel ACL；
- Team Space、Channel、Thread/Topic、Temporary Group Chat/DM 及消息；
- 文件、搜索、通知、在线状态和客户端体验；
- Bot/Service Account、Webhook/Event API 与平台级审计；
- 协作数据的备份、恢复、保留和升级。

Hikmah 不复制这些数据，也不直接读写 Foundation 私有数据库。

### 5.2 Hikmah 拥有

- Expert Seat、Foundation Identity Binding、QwenPaw Runtime Binding；
- Team/Channel Sidecar Rule Profile；
- Personal Agent Binding 与 owner-only 约束；
- Knowledge Candidate、人工审阅、作用域、版本和撤回；
- 跨系统 Correlation Record、产品级治理事件与安全审计引用；
- Foundation、AgentScope、QwenPaw 的部署配置、能力探测和契约测试。

Hikmah 不拥有通用消息、身份、工作流、审批、记忆或观测引擎。

### 5.3 AgentScope 拥有

- Team / Invite / TeamSay、Channel、Session、MessageBus 等协调运行语义；
- Team / Channel Coordinator Sidecar 的会话和运行状态；
- 专家邀请与多 Agent 协作的运行时机制；
- PermissionEngine/HITL、持久化、计划/后台任务和 OpenTelemetry 接入。

Hikmah 通过目标版本的 [`ChannelBase`](https://github.com/agentscope-ai/agentscope/blob/v2.0.7.post1/src/agentscope/app/channel/_base.py) 等公开接口集成，不读取或写入 AgentScope 私有数据库。

### 5.4 QwenPaw 拥有

- Agent Workspace、Skills、Plugins、专业记忆和工具执行环境；
- 服务端 Shared Expert 的运行时；
- 成员本机 Personal Agent 的长期记忆和本地资源；
- Channel、MCP、Governance/Approval、Cron 及运行会话；
- 可选 A2A/ACP 能力，但按协议正确职责使用。

共享专家优先使用 QwenPaw 现有 Channel；缺失 Foundation 适配时，使用其公开 `register_channel` 在 Hikmah 仓库实现外部插件。

### 5.5 上游版本与修改流程

[目标版本与发布基线](../architecture/version-baseline.md)是版本事实源。每个 release 使用唯一 BOM、lockfile、容器 digest 与 SBOM；只有完成契约、安全、升级和回退验证的组合才进入支持矩阵。

确需修改上游时：

1. 证明缺失的是可复用的通用扩展点，不是 Hikmah 私有需求；
2. 在对应上游独立分支完成最小修改并提交 PR；
3. Hikmah 不依赖未合并补丁；
4. 等待上游正式发布并固定版本后，再启用能力。

禁止 vendor 上游源码、monkey patch、直接读写上游数据库或维护长期私有 fork。

## 6. 逻辑组件

| 组件 | 单一职责 | 复用方式 |
|---|---|---|
| Mattermost Foundation | 提供 Team、Channel、Thread、DM、消息、文件、搜索、身份、RBAC 与客户端 | Adopt；不修改核心 |
| Expert Seat Binding | 把稳定社交身份映射到 Foundation Bot/Service Account 与固定 QwenPaw Workspace | Hikmah Build-gap |
| Coordination Adapter | 把 Foundation 事件映射到 AgentScope Channel/Team 公共语义 | Integrate；Foundation API + AgentScope `ChannelBase` |
| Sidecar Rule Profile | 表达静默、显式 @抑制、未 @单主答和有限干预规则 | Hikmah Build-gap；确定性规则优先 |
| Personal Agent Binding | 绑定唯一 Member、QwenPaw owner runtime、owner-only 产品页和显式分享能力 | Hikmah Build-gap + QwenPaw Hub/受验证本地连接器 |
| Policy Binding | 把 Team 能力与风险规则编译到 Foundation、AgentScope、QwenPaw 的权威执行点 | Hikmah 薄配置层，不是决策引擎 |
| Knowledge Promotion | 将带来源候选经人审、定范围、脱敏后发布、替代或撤回 | Hikmah PostgreSQL 规范对象 + 可重建 Runtime/RAG 投影 |
| Correlation Ledger | 关联外部 message/thread、runtime session、tool、approval 与 trace id | Hikmah Build-gap；不复制正文 |
| Contract Test Suite | 验证核心旅程、权限、故障、升级和上游兼容性 | Hikmah Build-gap |

组件优先部署为 Foundation Plugin 或最小外部服务；只有扩展边界无法满足时才增加独立进程。

## 7. 两级协调模型

### 7.1 Team Coordinator Sidecar

Team Space 关联一个 AgentScope 构建的 Team Coordinator Sidecar。它在身份上是全局协调 Agent，在行为上是轻量、低频、默认静默的边车，不是 Shared Expert。

允许职责：

- 维护 Expert Seat 名册和跨 Channel 治理规则的运行视图；
- 处理明确授权的跨 Channel 治理事件；
- 协调 Knowledge Candidate 进入团队级审阅；
- 处理计划性总结和治理提示。

禁止职责：

- 自行回答专业问题；
- 读取与当前治理事件无关的 Channel 正文；
- 替 Member、Admin 或 Owner 批准副作用；
- 自动把 Channel 内容提升为 Team Knowledge。

### 7.2 Channel Coordinator Sidecar

每个 Channel 关联一个 AgentScope 构建的 Channel Coordinator Sidecar。它通过 Foundation 公开事件接口观察该 Channel，默认静默、按事件唤醒。

允许介入：

- 未显式 @且通过协作意图门控时选择一名主答专家；
- 请求长期无人响应时提醒或改派一次；
- 多位专家竞争主答时指定单一主答，并让补充者留在 Thread；
- 发现结论冲突时提示主答整合；
- 展示审批、硬规则、定时总结和 Knowledge Candidate。

禁止介入：

- 明确 @专家时重新路由、总结、调停、邀请或代答；
- 自行给出专业结论；
- 代替专业专家执行工具；
- 代替人类批准操作。

规则判断优先；只有专长匹配确有歧义时才调用轻量模型。必要时最多提出一个澄清问题。

## 8. 领域模型与 Foundation 映射

### 8.1 人类角色

| Hikmah 角色 | Foundation 映射 | 允许 | 明确禁止 |
|---|---|---|---|
| Team Owner | 系统/团队最高管理角色 | 创建 Team、任命 Admin、治理配置、恢复与删除策略 | 因治理角色读取 Personal Agent 私有正文或绕过运行时审批 |
| Admin | Team/Channel 管理角色 | 邀请 Member、配置共享 Expert Seat/Sidecar、审核 Knowledge、查看授权 Trace | 调用或读取他人的 Personal Agent；自授 System Admin/工具权限 |
| Member | 普通受邀成员 | 参与获授权空间、@专家、管理自己的 Personal Agent、提出 Knowledge Candidate | 自报身份/角色；读取其他 Member 的绑定、Secret 或私有内容 |

MVP 只承载一个私有 Team Space。Hikmah 不复制 Foundation 用户系统；所有受保护操作遵守 [ADR-0004](../decisions/0004-trusted-identity-and-personal-agent-isolation.md)。

### 8.2 可信 Actor 与授权

每个受保护请求必须由服务端从 Mattermost OAuth/BFF session 解析 `AuthenticatedActor`，并校验 Team/Channel 成员关系、资源 owner、所需 capability、状态版本和幂等键。调用方提交的 `user_id`、`team_id`、角色或 reviewer 字段不是授权事实。

Team Owner/Admin 治理权限与 Personal Agent owner 权限相互独立。Bot、Expert、Sidecar 与服务使用独立身份和最小权限凭据；任何帖子、Webhook、模型输出或工具元数据都不能提升权限。

### 8.3 协作空间

- **Team Space**：Foundation 中的私有 Team/Realm/Workspace，承载成员、Channel、共享专家名册和治理边界。
- **Channel**：长期主题、成员可见性、Expert Seat、Sidecar Rule Profile 和 Channel-local 上下文。
- **Thread**：Foundation 原生 Thread 或 Topic，是消息与专家协作的透明上下文载体。
- **Temporary Group Chat**：Foundation 原生 Group DM 或临时私有空间，按显式成员列表授权；默认无 Sidecar，Agent 只在被邀请或 @时参与。

### 8.4 Shared Expert Seat

Expert Seat 是团队拥有的稳定社交身份，包含名称、头像、专长、职责、可见性和 Channel 权限。它映射到：

1. Foundation Bot/Service Account；
2. 固定版本 QwenPaw Runtime/Workspace；
3. 可用 Channel、上下文、工具与风险规则。

更换 Workspace 或升级 QwenPaw 不改变 Expert Seat 社交身份和审计连续性。

Channel Expert Membership 至少分别声明：是否可被 @、是否可被 Sidecar 路由、是否可主动补充、可读取哪些上下文、可提议或执行哪些工具。

Shared Expert Seat 是 Team 资源，不包含 `is_personal` 变体；公开读取契约不返回 Runtime Secret 或原始配置。

### 8.5 Personal Agent

Personal Agent Binding 只绑定一个 Member，可由该成员本机 QwenPaw 提供。此处 Owner 指绑定该 Agent 的 Member，不等同于 Team Owner。

- 只有绑定 Member 可以调用；
- 不能被其他成员 @；
- 不是共享 Channel 或 Temporary Group Chat 的成员；
- 不注册公共可搜索或可私聊的 Mattermost Bot 身份；
- 通过 owner-only Hikmah 产品页连接 QwenPaw Hub，或连接已通过安全 Spike 的本地出站连接器；
- 只能接收 Owner 明确选择的最小上下文；
- 输出默认只对 Owner 可见；
- 不能直接发布共享消息；
- Owner 执行“分享到 Channel”后，内容才成为新的 Foundation 消息。

服务端对无权访问者返回 `404` 以隐藏绑定存在性。无法由权威 ACL 与运行时 owner/tenant 隔离证明这些约束时，Personal Agent 功能保持关闭。

### 8.6 Coordinator Sidecar

Team / Channel Coordinator Sidecar 是系统级协调身份，不是 Expert Seat，不拥有专业业务工具权限。其 Foundation Bot 身份必须可被人类识别，并与专业专家在头像、标签或角色上区分。

## 9. 消息路由与协作流

### 9.1 路径 A：明确 @专家

1. Member 在 Foundation Thread 中明确 @一名或多名 Expert Seat；
2. Foundation 验证空间可见性、成员关系与 Bot 权限，并把原始事件直达对应 QwenPaw Channel；
3. 被 @的每位专家在同一 Thread 独立响应；
4. Channel Sidecar 可以收到事件，但确定性规则立即进入 observe-only，产生 **0 次**重路由、总结、调停或邀请；
5. 专家提出副作用工具调用时，由其 QwenPaw/AgentScope 权限与 HITL 机制处理；这不构成 Sidecar 介入；
6. 显式目标离线或失败时原样显示，不擅自替换其他专家。

### 9.2 路径 B：未明确 @

1. Channel Sidecar 从 Foundation 事件中执行协作意图门控；闲聊、广播和纯人类讨论默认不触发 Agent；
2. 按 Channel 规则、Expert Seat 专长和可用性选择一名主答；
3. 规则无法消除歧义时才使用轻量模型，必要时只问一个澄清问题；
4. Sidecar 通过 Foundation 原生 @或 Bot 事件唤醒主答 QwenPaw；
5. 主答可以在同一 Thread 通过原生 @邀请最多两名补充专家，自动邀请深度为一层；
6. 补充者把证据留在同一 Thread，主答负责统一结论；
7. 副作用进入运行时原生权限/审批流程；
8. 结束时可提出带来源的 Knowledge Candidate，但不能自动发布。

### 9.3 Coordinator 终态判定表

按下列顺序执行第一条命中规则；模型分类不能覆盖更高优先级的确定性规则：

| 优先级 | 输入条件 | Sidecar 动作 | 不变量/理由码 |
|---:|---|---|---|
| 1 | 重复或已处理的 event id | 静默丢弃，不产生新副作用 | `duplicate_event` |
| 2 | Bot/Expert/Sidecar 生成且无等待中的 correlation | 静默丢弃 | `agent_loop_suppressed` |
| 3 | 人类显式 @一名或多名 Expert Seat | `observe-only`，不路由、不总结、不邀请、不代答 | `explicit_expert_mention`；介入次数必须为 0 |
| 4 | 人类只显式 @Coordinator | 只回答治理/路由说明或提出一个澄清问题，不给专业结论 | `coordinator_addressed` |
| 5 | 无 @且为闲聊、广播、通知或纯人类讨论 | 静默 | `no_collaboration_intent` |
| 6 | 无 @、协作意图成立且只有一名符合 Channel/capability/availability 的专家 | 选择该专家为唯一主答 | `single_eligible_expert` |
| 7 | 无 @、规则指定的默认专家当前符合资格且置信度达到阈值 | 选择默认专家为唯一主答 | `eligible_default_expert` |
| 8 | 多名候选且规则/轻量分类仍低于阈值 | 只提出一个澄清问题，不唤醒专家 | `clarification_required` |
| 9 | 无符合资格或目标离线 | 显示不可用，不擅自替换 | `no_eligible_expert` |

资格检查至少包含：Team/Channel 成员关系、Shared Expert 类型、启用状态、可路由标志、capability、上下文作用域、运行时 readiness 与循环预算。每个原始人类事件最多产生一名主答、两名一层补充专家和三个自动参与的 Agent；超过预算必须等待人类继续。

### 9.4 Correlation Record，不是 TaskRun 引擎

Hikmah 不再建设权威 TaskRun 状态机。一个 Correlation Record 只保存：

- Hikmah correlation id；
- Foundation team/channel/thread/message id；
- Sidecar 与专家 runtime/session id；
- tool proposal、approval、execution 与 trace 的外部引用；
- 主答 Expert Seat、路由理由、作用域和时间；
- 供 UI 使用的派生阶段与最后已知状态。

持久执行状态由实际运行者拥有。派生状态不能驱动重放或越过运行时审批；状态不一致时显示“待核验”，不猜测成功。

## 10. 接口与协议边界

### 10.1 主要接口

| 接口 | 用途 | 约束 |
|---|---|---|
| Foundation Bot/Event/Webhook API | 人类、Expert、Sidecar 的协作消息与身份 | 用户/Agent 主通道；固定版本并做契约测试 |
| AgentScope `ChannelBase` / Team | Sidecar 事件映射和多 Agent 协调 | 只用公开接口，不读私库 |
| QwenPaw Mattermost Channel / Hub / Console API | Shared/Personal Agent 的消息与运行时通道 | Shared Expert 使用内置 Mattermost Channel；Console 仅使用固定版本公开 SSE 契约 |
| Mattermost Web App Plugin API | 配置 UI、审批投影、知识晋升动作 | 生产 UI 的唯一产品入口；不改核心源码 |

所有外部接口遵守 [ADR-0005](../decisions/0005-public-integration-contracts-and-fail-closed-semantics.md)；未配置、异常、mock 和 fallback 不能表示为真实成功。

### 10.2 身份与错误契约

- 公共 API 使用 `/api/v1` 资源路径、分页 List、部分更新 PATCH 和输入/输出分离 schema。
- 受保护 API 只信任服务端解析的 `AuthenticatedActor`；OpenAPI 声明统一安全方案。
- 错误响应统一为 `error.code`、安全的 `error.message`、可选非敏感 `error.details` 和 correlation id。
- `401/403/404/409/422/429/5xx` 语义全局一致；内部堆栈、Secret 和第三方原始错误不得返回客户端。

### 10.3 开放协议

- **MCP**：用于工具、资源与 Prompt；Adopt。工具描述和注解按不可信输入处理，授权仍由运行时执行。
- **A2A**：只用于独立 Agent 间 Task/Artifact 协作。MVP 先用透明的 Foundation Thread；证明其不足后才接 A2A。关键审批不能只依赖 A2A Message。
- **ACP**：面向编辑器/客户端与编码 Agent，不作为 Hikmah Personal Agent 通道，也不替代 Foundation Bot API。
- **AG-UI**：只有未来需要自建 Agent 侧栏且 Foundation 原生事件不足时采用。
- **CloudEvents**：可作为跨系统事件元数据信封，不是引入新 Event Bus 的理由。
- **OpenTelemetry**：用于 Trace、Metric、Log 关联；优先使用 AgentScope/QwenPaw 现有 instrumentation。

### 10.4 最小产品契约

| 对象 | 必需语义 |
|---|---|
| ExpertSeatBinding | seat id、foundation identity、runtime type、workspace/version、capabilities、allowed channels |
| SidecarRuleProfile | scope、explicit-mention suppression、intent gate、lead selection、intervention limits |
| PersonalAgentBinding | member id、foundation private identity/session、runtime binding、share policy、revocation state |
| PolicyBinding | capability、resource scope、runtime rule reference、preauthorization boundary、expiry |
| KnowledgeCandidate | source refs、content、proposed scope、sensitivity、proposer、review state |
| CorrelationRecord | external ids、lead seat、route reason、approval/tool/trace refs、derived status |

这些是产品数据，不组成新的通用 Agent 传输协议。

## 11. 上下文、记忆与知识

### 11.1 作用域

| 作用域 | 权威实现 | 跨 Channel 规则 |
|---|---|---|
| Thread / Channel 对话 | Foundation | 默认不跨 Channel |
| Expert Stable Memory | QwenPaw ReMe；必要时 AgentScope ReMe/Mem0 | 仅身份、能力、技能版本和经批准的专业记忆 |
| Team Knowledge | Hikmah PostgreSQL 保存已审阅规范对象；QwenPaw/AgentScope 索引是可重建投影 | 只有已审阅对象可按发布范围检索 |
| Personal Agent Memory | 成员本机 QwenPaw | 留在本机，不注入 Shared Expert |

Agent 只读取当前任务需要的授权消息引用或片段。不得为了“可能有用”抓取整个 Channel、其他 Channel 或 Personal Agent 历史。

### 11.2 Knowledge Promotion

唯一允许的跨 Channel 内容晋升流程：

```text
Knowledge Candidate
  → 人类审阅
  → 确定适用范围与敏感级别
  → 必要时脱敏
  → 发布 Team Knowledge
  → 版本化、替代或撤回
```

每个 Team Knowledge 对象保存来源、提出者、审阅者、适用范围、敏感级别、版本和状态。

硬规则：模型不能自动发布 Team Knowledge；总结不等于发布；没有明确人类确认时内容留在原作用域；撤回后不得注入新会话，历史关联仍保留。

### 11.3 Personal Agent 数据

成员本机 QwenPaw 的长期记忆、私有技能和本地资源留在本机。团队服务器默认只保存绑定状态、最小连接元数据和关联引用，不保存 Personal Agent 私有请求与结果正文。

Owner 主动分享时，分享内容成为新的 Foundation 消息，可标记“由 Personal Agent 辅助生成”；原始私聊仍不因此变成共享数据。

## 12. 执行治理

Hikmah 不建设独立 Policy / Approval 决策服务。职责拆分为：

- Foundation RBAC：谁能看、说、邀请和管理 Channel/Bot；
- AgentScope PermissionEngine/HITL：AgentScope 侧工具是否允许、询问或拒绝；
- QwenPaw Governance/Approval：QwenPaw 侧工具、OS Driver 和外部动作的策略与暂停恢复；
- Hikmah Policy Binding：把 Team 规则配置到权威执行点，并把审批投影到人类可见界面；
- Correlation Ledger：记录规则版本、提案、审批与实际运行引用。

### 12.1 风险处理

| 类别 | 默认处理 |
|---|---|
| 只读、分析、草稿、无外部副作用计算 | 可自动执行；运行时仍记录工具和输入范围 |
| 写文件、发消息、修改任务、调用业务系统等副作用 | 请求人类审批；Admin 只可预先放行边界清晰、可撤销的低风险动作 |
| 越权、目标含糊、参数漂移、凭据缺失、策略冲突或审批系统不可用 | 默认拒绝 / fail closed |

### 12.2 Execution Card 投影

Execution Card 是对运行时原生 tool proposal / approval request 的人类可读投影，不是 Hikmah 自有执行引擎。它必须显示：

- 发起 Member、提出 Expert Seat 与实际 Runtime；
- 工具、目标、标准化参数；
- 对象数量、外部接收方、影响范围和可回退性；
- diff、消息预览或等价变更摘要；
- 所需能力、策略依据、审批有效期和运行时 proposal id。

批准必须绑定精确工具、参数、资源作用域、计划 digest、有效期和单次 nonce。实质变化必须重新审批；Sidecar 和 Expert 不能成为人类审批者。

## 13. 部署拓扑

```text
Private Team Server
├── Mattermost Foundation
├── Hikmah Web App Plugin + Python OAuth/BFF
│   ├── Bindings & Sidecar Rules
│   ├── Knowledge Promotion
│   └── Correlation Ledger
├── Hikmah PostgreSQL 16（独立 database/role）
├── AgentScope Coordination Runtime
├── Shared QwenPaw Workspaces
└── OpenTelemetry collector/backend（按需）

Member Device
└── Personal QwenPaw
    └── 受验证 TLS outbound connector → Hikmah owner-only surface
```

原则：

- Foundation、AgentScope 和 QwenPaw 使用固定版本与独立数据卷；
- Personal Agent 只主动出站，不开放到公网的本机入站端口；
- Foundation 凭据、QwenPaw Secret 和工具凭据分开存储、最小权限、可轮换；
- Plugin/Agent 视为不可信执行单元，不暴露 Docker Socket 或无边界主机目录；
- Mattermost 与 Hikmah 可以共用 PostgreSQL cluster，但不得共用 database、schema、role 或 credentials；
- 不为了“未来可能需要”部署 Temporal、OPA/OpenFGA、Keycloak、独立向量数据库或事件总线。

## 14. 可靠性、降级与可观测性

- 显式目标离线时不擅自替换 Expert；
- Sidecar 故障时，Foundation 原生显式 @仍应直达 Expert；
- 只对可证明幂等的只读动作有限重试；
- 副作用超时或状态未知时标记 `verification_required`，禁止自动重试；
- Foundation 事件必须去重；迟到事件不能越过已取消或已拒绝的运行时操作；
- 任何权限或审批执行点不可用时，副作用 fail closed；
- Correlation Record 不是消息备份，恢复以各权威系统为准；
- 使用 OpenTelemetry 贯通 Foundation event、Sidecar session、QwenPaw session 与 tool call；正文和敏感参数先脱敏；
- 观测后端可从 Langfuse、OpenLIT、Phoenix 等选择，但必须单独核验许可证与数据边界。

### 14.1 MVP 量化 NFR

以下指标是 release qualification 的终态要求，均在[目标版本基线](../architecture/version-baseline.md)和 20 人上限环境测量；外部模型生成耗时单独报告，不混入 Hikmah 内部处理延迟。

| 维度 | 目标与测量口径 |
|---|---|
| 容量 | 单 Team 20 名 Member、50 个 Channel、20 个同时活跃 Thread、10 个并发 Agent task 下保持门禁指标 |
| API 延迟 | 不含上游调用时，治理读取 p95 ≤ 300 ms、事务写入 p95 ≤ 500 ms |
| 路由延迟 | 规范化事件进入后，确定性 Coordinator 决策 p95 ≤ 500 ms；需要轻量分类时 p95 ≤ 3 s |
| 状态可见性 | 获得权威依赖状态后，RHS/Post 状态投影 p95 ≤ 2 s |
| 可用性 | Hikmah 控制面月度目标 ≥ 99.5%（排除计划维护与已单独归因的上游故障）；Hikmah 故障不得阻塞 Mattermost 原生人类聊天 |
| 幂等与循环 | 回放测试中重复外部副作用为 0；显式 @ Sidecar 介入为 0；自动参与不超过一名主答和两名补充专家 |
| 审计完整性 | 100% 治理写操作、副作用提案/审批/结果与知识发布具有 Actor、scope、规则版本和 correlation |
| 隐私与授权 | Personal Agent、跨 Channel 和治理角色越权测试容忍数为 0 |
| 数据恢复 | RPO ≤ 24 h，RTO ≤ 4 h；每个目标 release 完成一次隔离恢复演练 |

每份性能/可靠性报告必须记录环境、BOM、数据集、并发、采样窗口、样本量、百分位和未达标项。没有测量报告时不得使用 production-ready、high-performance 或等价声明。

## 15. 安全与隐私边界

身份、授权、Personal Agent 与敏感字段的正式决策见 [ADR-0004](../decisions/0004-trusted-identity-and-personal-agent-isolation.md)。

### 15.1 强制约束

- 所有 Foundation、Bot、Plugin、Webhook 和工具输入都按不可信数据处理；
- 用户消息中的指令不能提升系统权限或改变 Sidecar/Expert 能力；
- MCP Tool annotation、Agent Card、A2A Message、Plugin metadata 不能作为授权依据；
- Personal Agent 的 owner-only 必须由 Foundation ACL 证明，而不只是 UI 隐藏；
- Shared Expert、Personal Agent、Team Sidecar、Channel Sidecar 使用不同身份和凭据；
- Agent 不继承创建者或 Bot 管理员权限；
- 审计不保存 Secret、Token、无关私密正文或模型私有推理；
- 文件、URL、富文本、Webhook 和模型输出进入工具前必须做类型、大小、目标和作用域校验；
- 高权限 Plugin、任意 Python Tool、Docker Socket、宿主目录写入默认禁止；
- 依赖使用固定版本、SBOM、许可证清单和安全公告复核。

### 15.2 重点威胁测试

- 跨 Channel 越权读取、私有 Thread 泄漏和搜索侧信道；
- Personal Agent 被其他 Member 调用、被拉入共享 Channel 或读取共享历史；
- Team Owner/Admin 治理角色误读 Personal Agent 正文；
- 提示注入诱导 Sidecar 越过显式 @静默规则；
- 多 Expert 自动互相 @形成回复环或资源放大；
- 审批重放、参数替换、计划 digest 漂移和迟到执行；
- 恶意文件、URL、MCP Server、Bot Webhook 与 Agent Card；
- Correlation/Trace 泄漏正文、凭据或跨租户标识。

## 16. 验证体系

### 16.1 Mattermost release qualification

1. 可复现自托管，不修改核心；
2. Team、Channel、Thread/Topic、DM、文件、搜索与邀请闭环；
3. QwenPaw Expert @直达、流式回复和同 Thread 上下文；
4. Sidecar 显式 @零介入、未 @单主答；
5. Personal QwenPaw owner-only、不可读共享空间、可显式分享；
6. 只读自动、副作用暂停/批准/恢复可见且可关联；
7. 无消息双写的跨系统 Trace；
8. 兼容升级后契约测试通过。

许可证/品牌、核心补丁、主机高权限、身份隔离、Plugin 安装、升级/回退任一硬门禁失败时阻止发布；失败触发 ADR-0003 退出路径评估，不授权绕过门禁。

### 16.2 发布门禁

一个版本组合只有同时满足以下条件才能进入支持矩阵：

1. 版本 BOM、容器 digest、锁文件和 SBOM 固定；
2. Mattermost OAuth、Plugin、REST/WebSocket、QwenPaw Channel/Hub 与 AgentScope adapter 契约通过；
3. `AuthenticatedActor`、角色矩阵、Personal Agent owner-only 和跨 Channel 威胁用例通过；
4. PostgreSQL migration、备份、恢复和测试误连保护通过；
5. 量化 NFR 有测量报告，偏差经明确风险接受；
6. 目标分发模式的许可证与品牌复核有负责人、日期和适用范围。

### 16.3 自动化测试

- Sidecar Rule Profile、Binding、Knowledge Promotion 与 Correlation 的单元/性质测试；
- Foundation、AgentScope、QwenPaw 固定版本契约测试；
- 显式 @、未 @、多专家、离线、取消、审批和分享集成测试；
- owner-only、跨 Channel、治理角色、重放、提示注入与 SSRF/文件安全测试；
- 备份/恢复、版本升级、Webhook 重放和部分失败端到端测试；
- 使用 promptfoo/garak 等现成工具维护回归集，不自建通用评测框架。

## 17. MVP 交付切片

### Slice 0：Mattermost 资格验证与退出门禁

- 在目标版本基线部署 Mattermost、Hikmah Plugin/BFF、一个 Shared QwenPaw Expert 与一个 AgentScope Sidecar；
- 完成 OAuth、显式 @、未 @、owner-only、Correlation、Plugin 降级、备份恢复和兼容升级验收；
- 完成目标分发模式的许可证/品牌复核；
- 任一硬门禁失败时依据 ADR-0003 重新评估 Zulip/独立 UI，不修改上游核心或降低隐私要求。

### Slice 1：Foundation + Shared Expert 直达

- 部署已选 Foundation；
- Team/Channel/Thread、邀请和权限；
- Expert Seat Binding；
- 一个服务端 QwenPaw Expert 的明确 @直达；
- 基础 Correlation 与契约测试。

### Slice 2：轻量 Sidecar 与多专家协作

- Team/Channel Sidecar；
- 显式 @零介入；
- 未 @规则门控、单主答和有限邀请；
- 无人响应、冲突和失败可见性。

### Slice 3：Personal Agent 与执行治理

- 本机 QwenPaw owner-only 连接；
- 最小上下文和显式分享；
- Policy Binding、Execution Card 投影与副作用审批关联。

### Slice 4：Knowledge Promotion 与生产加固

- Knowledge Candidate、人审、范围、版本和撤回；
- 安全回归、可观测性、备份恢复和升级门禁；
- 依赖许可证/SBOM 和运营手册。

以上 Slice 仅定义目标交付顺序；是否以及何时进入代码实现必须由独立任务明确授权。当前代码脚手架不构成任何 Slice 已完成的证据；开放设计与验证项见[架构审查跟踪表](../project/prd-architecture-review-tracker.md)。

## 18. 决策记录

### 18.1 已批准的产品决策

- 品牌：仓库 `hikmah`；英文 Hikmah；中文 群贤；其他实体不独立命名；
- 用户范围：3–20 人邀请制私有小团队；
- 协作结构：一个 Team Space；长期 Channel 与 Thread；Temporary Group Chat 独立；
- 共享专家：团队拥有，通常由服务端 QwenPaw 实现；
- Personal Agent：仅绑定 Member 使用，可由本机 QwenPaw 提供，私密输出后人工分享；
- 协调定位：AgentScope 构建 Team/Channel 两级轻量 Sidecar，身份全局、行为边车、默认静默；
- 显式 @：直达指定 Expert，Channel Sidecar 只观察；
- 未显式 @：规则优先，歧义才用轻量模型，只选一名主答；
- 记忆：普通对话 Channel-local；跨 Channel 只允许人审 Knowledge Promotion；
- 执行：只读可自动；副作用审批或 Admin 边界清晰的低风险预授权；始终审计；
- 上游：原则不修改 AgentScope/QwenPaw；必要修改只提交上游 PR。

### 18.2 核心架构决策
 
- [ADR-0001](../decisions/0001-reuse-first-thin-control-plane.md)：Accepted；复用优先原则，仅建设 Hikmah 特有的轻量治理控制层；
- [ADR-0002](../decisions/0002-collaboration-foundation-spike.md)：Superseded；协作底座评估标准与 Spike 用例；
- [ADR-0003](../decisions/0003-adopt-mattermost-as-collaboration-foundation.md)：Accepted；选定 Mattermost 作为协作底座与 UI 宿主；
- [ADR-0004](../decisions/0004-trusted-identity-and-personal-agent-isolation.md)：Accepted；Mattermost 信任身份、角色授权和 Personal Agent owner-only 隔离；
- [ADR-0005](../decisions/0005-public-integration-contracts-and-fail-closed-semantics.md)：Accepted；公开集成契约、Plugin 交付与 fail-closed 状态；
- [ADR-0006](../decisions/0006-governance-metadata-persistence-and-schema-lifecycle.md)：Accepted；PostgreSQL、Alembic、数据保留和恢复；
- 架构定力：深耕 Mattermost + QwenPaw + AgentScope，不自建通用聊天全栈或多余 Agent 运行时。


## 19. 持久化设计资产

- 本规范：`docs/product/overview.md`
- GitHub 调研：`docs/research/2026-08-28-github-reuse-landscape.md`
- 决策记录：`docs/decisions/`
- 目标版本基线：`docs/architecture/version-baseline.md`
- 视觉设计册：`docs/design/hikmah-design-book.html`
- 批准记录：`docs/design/approval-record.md`
- 审查与验证跟踪：`docs/project/prd-architecture-review-tracker.md`
- 历史画布：`docs/archive/design-sources/`

历史画布继续作为设计过程档案保存，可能包含已被本规范替代的早期架构。发生差异时，以本规范和状态为 Accepted 的 ADR 为准。
