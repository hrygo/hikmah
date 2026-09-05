---
title: ADR-0005：采用公开集成契约与 fail-closed 失败语义
description: 固化 Mattermost、QwenPaw、AgentScope、Web App Plugin 与 Hikmah API 的正式集成边界和失败状态。
document_type: architecture-decision
status: accepted
created: 2026-08-28
updated: 2026-09-05
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - architecture
  - integration
  - api
  - reliability
canonical: true
related:
  - 0001-reuse-first-thin-control-plane.md
  - 0003-adopt-mattermost-as-collaboration-foundation.md
  - 0004-trusted-identity-and-personal-agent-isolation.md
  - 0007-knowledge-collaboration-pilot-and-runtime-boundaries.md
  - ../architecture/version-baseline.md
  - ../product/overview.md
  - ../project/prd-architecture-review-tracker.md
---

# ADR-0005：采用公开集成契约与 fail-closed 失败语义

> **状态**：Accepted（已采纳）
>
> **验证边界**：本文定义可实现、可测试的终态契约，不表示当前脚手架或真实环境已经通过端到端验证。

## 1. 背景与约束

Hikmah 连接 Mattermost、QwenPaw 与 AgentScope，但不建设通用 Agent Gateway、消息总线或第二套运行时。集成必须只依赖固定版本的公开接口，并且在未配置、不可达、超时、部分失败或状态未知时准确暴露状态。

返回模拟成功、调用未固定的私有 endpoint、把独立开发 SPA 当作 Mattermost Plugin，都会让脚手架行为被误认成生产契约。

## 2. 决策

### 2.1 Mattermost 边界

- 协作消息与身份只通过 Mattermost REST API v4、WebSocket 事件、OAuth 2.0、Bot/Service Account 与公开 Web App Plugin API 访问。
- Hikmah 不读取 Mattermost 私有数据库，不依赖内部 WebApp 组件，不使用未发布补丁。
- 入站事件先校验来源、版本、Team/Channel 作用域、事件类型、大小和去重键，再转换为内部不可变事件信封。
- 出站 Post 必须携带 idempotency/correlation 信息；超时后状态标记为 `verification_required`，不得自动重发副作用。

### 2.2 QwenPaw 边界

- Shared Expert 的消息主通道是 QwenPaw 固定版本自带的 Mattermost Channel；Hikmah 不重写该消息适配，也不通过自造通用 Runtime Bridge 代替它。
- Personal Agent 中心托管模式通过 QwenPaw Hub 的 owner/tenant 隔离代理访问。
- 只有确需 Console 交互时才使用固定版本公开的 `POST /api/console/chat`、`X-Agent-Id`、SSE 和认证契约；不得使用未在目标版本公开文档中的 `/api/v1/agents/{id}/run` 等路径。
- QwenPaw 返回的 JSON、SSE event、错误和模型输出均按不可信外部数据验证后使用。

2026-09-05 补充：依据 ADR-0007，优先验证通过公开 `register_runtime_hook` / `PRE_DISPATCH` 增加确定性准入，保留原生 Mattermost Channel 与运行时职责。检查真实 Post、发送者、目标、作用域、去重和邀请预算，不进行专长选择或模型改写。显式 @准入独立于 Sidecar；扩展缺失、校验故障或不能证明必要上下文时停止接收对应工作。

Hook 在 Channel 上下文获取之后执行，不能替代前置 Bot ACL、文件/记忆隔离及最小上下文读取。注册、短路、异常、重载、命令、Console 和后台等入口必须有契约证据；未经保护的入口关闭。若公开扩展点无法满足要求，能力保持关闭并经新 ADR 选择上游改进或窄适配，不覆盖私有方法、不用隐式 fallback。

### 2.3 AgentScope 边界

- Team/Channel Coordinator 使用 Hikmah 所有的薄适配器，把已验证 Mattermost 事件映射到固定版本 AgentScope `ChannelBase`/Team 公共语义。
- AgentScope 拥有 Sidecar session、协调运行和 HITL 状态；Hikmah 只保存外部引用、路由理由和派生展示状态。
- 适配器不得把 AgentScope 内部对象、私有数据库或未公开类型暴露为 Hikmah 公共 API。

### 2.4 Web 交付边界

- 生产用户界面是可安装的 Mattermost Web App Plugin，必须包含合法 manifest、固定 plugin id、WebApp bundle 和兼容版本声明。
- 独立 Vite SPA 仅是开发预览与组件调试入口，不是生产用户界面或第二个聊天客户端。
- Plugin 与 Python BFF 通过同源 `/hikmah/*` API 通信；浏览器不直接持有 Mattermost、QwenPaw 或 AgentScope 服务凭据。
- 首批产品治理界面支持 Web/Desktop；原生移动客户端只承诺聊天、文本降级和受支持 Web 入口，不声明 Web App Plugin 交互在原生移动端等价。

### 2.5 Hikmah REST 契约

- 资源使用复数名词与 `/api/v1` 前缀；输入、输出和内部模型分离。
- 所有错误使用统一结构：`error.code`、安全的人类可读 `error.message`、可选的非敏感 `error.details` 与 correlation id。
- 统一状态码：`400` 格式错误、`401` 未认证、`403` 无权限、`404` 不存在或需隐藏存在性、`409` 状态/版本冲突、`422` 语义校验失败、`429` 限流、`5xx` 服务端或依赖失败。
- List API 必须分页；PATCH 只修改明确提供的字段；外部 ID 使用不同类型/命名，不能混用。

### 2.6 运行与健康状态

以下状态互斥且具有稳定语义：

| 状态 | 含义 |
|---|---|
| `unconfigured` | 必需配置或凭据不存在，能力不可用 |
| `connecting` | 正在建立连接，尚未可接收新工作 |
| `ready` | 固定版本契约探测通过，可接收工作 |
| `degraded` | 部分只读或展示能力可用，关键路径受限 |
| `unreachable` | 依赖不可达或超时 |
| `rejected` | 认证、授权、策略或输入拒绝 |
| `in_progress` | 权威运行时确认工作执行中 |
| `completed` | 权威运行时给出成功终态且结果通过契约校验 |
| `verification_required` | 副作用或超时后的真实终态未知，需要读取权威系统核验 |

未配置、异常、mock 或 fallback 永远不能返回 `ready`、`ok` 或 `completed`。模拟器只允许在显式 test/demo profile 使用，响应、UI 和 Trace 必须带不可去除的 `simulated` 标识，健康检查不得把模拟依赖计为真实就绪。

### 2.7 重试、幂等与循环控制

- 只对可证明幂等的读取、能力探测和无副作用事件消费进行有界指数退避重试。
- 写操作、工具调用和外部消息在状态未知时不自动重试。
- Mattermost event id、post id、correlation id 与运行时 session/tool id 用于去重和追踪。
- Bot/Agent 生成事件默认不再次触发 Sidecar；只有明确 correlation 等待的回复可进入，并受每 Thread 的参与者和轮次预算限制。

预算必须在目标专家入口生效，不能只在 Sidecar 上检查；正文中的 correlation 不是许可。事件去重与预算占用须原子处理并覆盖重启恢复；不能把 Correlation 派生状态作为重新执行依据。自动路由最多一名主答和两名一层补充专家；显式 @多名专家按人类目标执行，不自动追加邀请。完整判定表见产品规范第 9.3 节。

试点正常回写原 Thread 是边界明确的服务预授权，限定 Bot、Channel、Thread、内容与次数；业务写工具、任意发帖和知识发布不能沿用该授权。状态未知仍按 `verification_required` 处理。

## 3. 拒绝的替代方案

- **自建统一 Agent Gateway**：重复 QwenPaw/AgentScope 运行时与状态机。
- **隐式 mock fallback**：把不可用伪装成成功，破坏审计和运维判断。
- **预先设计多 Foundation 通用框架**：当前只有 Mattermost 被接受；只保留窄边界，不为未验证需求建立通用抽象。
- **生产独立聊天 SPA**：重复 Mattermost 客户端和权限体验。

## 4. 后果与门禁

- 每个外部适配器必须有固定版本、认证、请求/事件、流式、错误、取消、幂等和超时契约测试。
- Mattermost Plugin 必须通过安装、禁用、升级和文本降级验证。
- 一条 Mattermost → Sidecar/QwenPaw → 同 Thread 回写 → Correlation 的真实链路通过前，只能称为目标架构或脚手架。
