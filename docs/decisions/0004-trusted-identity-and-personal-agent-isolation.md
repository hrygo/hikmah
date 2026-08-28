---
title: ADR-0004：采用 Mattermost 信任身份并隔离 Personal Agent
description: 规定 Hikmah 的认证、授权、角色映射、服务身份和 Personal Agent owner-only 隔离终态。
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
  - identity
  - authorization
  - privacy
canonical: true
related:
  - 0001-reuse-first-thin-control-plane.md
  - 0003-adopt-mattermost-as-collaboration-foundation.md
  - ../product/overview.md
  - ../research/2026-08-28-mattermost-zulip-webui-integration.md
  - ../project/prd-architecture-review-tracker.md
---

# ADR-0004：采用 Mattermost 信任身份并隔离 Personal Agent

> **状态**：Accepted（已采纳）
>
> **验证边界**：本文规定终态安全契约。只有身份、越权和 owner-only 验收证据归档后，相关交付才可标记为 `validated`。

## 1. 背景与约束

Mattermost 是 Hikmah 的协作身份、Team 成员关系、Channel ACL 与用户会话事实源。Hikmah 需要在不复制用户系统和通用 RBAC 的前提下提供 Expert Seat、Sidecar、Knowledge Promotion 与 Correlation 等产品能力。

Personal Agent 的隐私边界比普通 Mattermost Bot 私聊更严格：它只能由唯一绑定 Member 调用，不能被其他成员发现、私聊、拉入共享空间或由 Team Owner/Admin 读取正文。UI 隐藏和客户端自报身份都不能构成安全边界。

## 2. 决策

### 2.1 交互式身份

1. Mattermost 管理员为 Hikmah 注册受信任的机密 OAuth 2.0 客户端，关闭动态客户端注册。
2. Hikmah Python BFF 使用 Authorization Code Flow；`state` 必须单次校验，并使用 PKCE。
3. Mattermost access/refresh token 只保存在 Hikmah 服务端加密存储中。浏览器只持有短期、可撤销、`Secure`、`HttpOnly` 且具有明确 `SameSite` 与 Path 作用域的 Hikmah 会话 Cookie。
4. `/hikmah/*` 由受控反向代理路由至 BFF；Hikmah Cookie 不覆盖 Mattermost 自有 Cookie。
5. 浏览器提交的 `user_id`、`team_id`、角色名称、Bot 身份或“我是管理员”等字段永远不是授权事实。

### 2.2 `AuthenticatedActor` 契约

每个受保护请求必须由服务端解析一个不可由调用方覆盖的 `AuthenticatedActor`，至少包含：

- Mattermost user id；
- 当前 Team id 与已验证的 Team/Channel 成员关系；
- Hikmah 角色投影；
- 会话 id、认证时间和撤销状态；
- 请求 correlation id；
- Actor 类型：`human`、`service`、`expert` 或 `sidecar`。

所有资源访问同时校验 Actor、Team/Channel 作用域、资源 owner、当前状态版本与所需 capability。不存在认证信息返回 `401`；已认证但无权访问返回 `403`；Personal Agent 等需要隐藏存在性的资源返回 `404`。

### 2.3 人类角色与权限

| 角色 | 允许 | 明确禁止 |
|---|---|---|
| Team Owner | 管理 Team 级治理配置、任命 Admin、执行恢复与删除策略 | 因治理角色读取任意 Personal Agent 正文或工具数据 |
| Admin | 管理共享 Expert Seat、Channel Rule、Knowledge Review 与授权范围内的 Correlation | 读取或调用他人的 Personal Agent；绕过运行时审批 |
| Member | 使用获授权 Channel/Expert、管理自己的 Personal Agent Binding、提出 Knowledge Candidate、查看本人有权的 Trace | 自报身份/角色；访问其他 Member 的绑定、私有正文或 Secret |

Team Owner 与 Admin 的治理权限不继承 Personal Agent owner 权限。知识审核者身份由 `AuthenticatedActor` 写入，不能由请求体指定。

### 2.4 服务与 Agent 身份

- Mattermost Bot、Webhook、QwenPaw Runtime 和 AgentScope Sidecar 使用彼此独立、可轮换、最小作用域的服务凭据。
- 服务间请求必须使用固定受众、短期凭据或可验证签名，并具备时间窗、nonce 与重放保护。
- Expert 和 Sidecar 不继承创建者、Owner、Admin 或 System Admin 权限。
- 外部事件、帖子属性、模型输出、MCP 注解和 Agent Card 一律按不可信输入处理，不能改变 Actor 或 capability。

### 2.5 Shared Expert 与 Personal Agent 分离

`ExpertSeatBinding` 与 `PersonalAgentBinding` 是两个独立领域契约：

- `ExpertSeatBinding` 属于 Team，映射 Mattermost Bot/Service Account、QwenPaw Workspace、Channel Membership 与 capability；
- `PersonalAgentBinding` 属于唯一 Member，不映射公共可搜索或可私聊的 Mattermost Bot，不是 Shared Expert 的布尔变体；
- 中心托管模式通过 QwenPaw Hub 的 owner/tenant 隔离与代理边界连接；成员本机模式只允许经安全连接 Spike 验证的出站连接器；
- Personal Agent 私有请求、结果、长期记忆、技能与本地资源不进入 Hikmah 团队数据库、Correlation 正文或共享检索；
- Owner 执行“分享到 Channel”时，系统重新校验目标 Channel 发帖权限，并创建只含 Owner 明确选择内容的新 Mattermost Post。共享快照不能反向读取个人会话。

### 2.6 敏感字段

- API 输入与输出分离；读取契约只返回明确 allowlist 字段。
- Runtime token、OAuth token、Bot token、连接 Secret 与原始 `runtime_config` 不进入普通 API 响应、URL、帖子 props、浏览器日志或 Correlation Record。
- 持久层只保存 Secret 引用、版本和轮换元数据；Secret 值由受控 Secret 存储持有。

## 3. 拒绝的替代方案

- **Hikmah 自建用户和密码系统**：重复 Mattermost 身份事实源，增加同步、撤销和账户恢复风险。
- **信任浏览器 header/query/body 中的用户 ID**：可被伪造，不能用于授权。
- **Personal Agent 作为普通 Mattermost Bot**：Mattermost 的普通私聊权限不能证明严格 owner-only。
- **Team Owner/Admin 可治理性等同于私有数据可见性**：违反最小权限和个人边界。

## 4. 后果与门禁

- 所有公共 API 都必须以 `AuthenticatedActor` 为入口，OpenAPI 必须声明统一安全方案与 `401/403/404` 语义。
- Shared Expert 与 Personal Agent 的数据库、schema、API 和前端契约必须分离。
- 任何真实用户交付必须通过冒充身份、跨 Channel、Admin 越权、Personal Agent 枚举/调用、分享重放和 Secret 泄漏用例。
- 无法由权威 ACL 或受验证代理证明 owner-only 时，Personal Agent 功能保持关闭。
