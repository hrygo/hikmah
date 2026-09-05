---
title: Hikmah WebUI 与协作底座整合深度调研
description: 基于固定 Release 源码评估 Mattermost、Zulip、AgentScope、QwenPaw 与 Hikmah WebUI 的整合路线。
document_type: research-report
status: completed
created: 2026-08-28
updated: 2026-08-28

review_after: 2026-11-28
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - research
  - mattermost
  - zulip
  - webui
canonical: false
related:
  - ../product/overview.md
  - ../decisions/0002-collaboration-foundation-spike.md
  - ../decisions/0003-adopt-mattermost-as-collaboration-foundation.md
  - ../decisions/0004-trusted-identity-and-personal-agent-isolation.md
  - ../decisions/0005-public-integration-contracts-and-fail-closed-semantics.md
  - ../project/prd-architecture-review-tracker.md
---

# Hikmah WebUI 与协作底座整合深度调研

> 范围：Mattermost、Zulip、AgentScope、QwenPaw 及 Mattermost Agents 的代码级整合评估。
>
> 原则：复用优先、不修改上游核心、不依赖未合并的上游补丁。
>
> 后续决议：本报告提出的 Mattermost 宿主、OAuth/BFF、owner-only Personal Agent 与公开适配边界已由 ADR-0003～ADR-0005 接受。本报告保留调研快照；正式终态以产品规范和 Accepted ADR 为准，尚缺运行/法律证据的事项以审查跟踪表为准。

## 1. 执行结论

此前把“独立 Hikmah WebUI”当作默认方向并不合适。对最新发布代码进行深读后，本报告建议：

1. **MVP 的最终用户界面采用 Mattermost 宿主壳 + Hikmah Web App Plugin 的混合形态**，而不是从零实现一个完整聊天客户端。
2. **Mattermost 是协作数据面和 UI 宿主，不是 Hikmah 的业务后端**。它负责身份、团队、频道、帖子、线程、文件、搜索、未读和基础权限；Hikmah 只负责专家、协调边车、执行、审批、知识候选和个人 Agent 的薄控制面。
3. **Hikmah 自有代码保持 Python + TypeScript**：TypeScript 负责嵌入 Mattermost 的产品界面与富消息卡片；Python 负责控制面、策略、映射和 Agent 适配。MVP 不需要 Go 服务端插件，也不需要修改 Mattermost、AgentScope 或 QwenPaw 核心代码。
4. **Zulip 保留为首要备选，但不建议作为当前 WebUI 宿主**。它的 API、主题模型和 Apache-2.0 许可很有吸引力；然而当前没有可与 Mattermost Web App Plugin 相当的运行时 UI 扩展模型，富卡片和产品级页面通常需要修改上游 WebUI 或另做门户。
5. **个人 Agent 的现有映射必须修正**：不能把“严格仅主人可用”寄托在 Mattermost/Zulip 的普通 Bot 私聊权限上。推荐把个人 Agent 放在 Hikmah 的 owner-only 产品页面，不把它作为可被其他成员直接私聊的 Foundation Bot；分享时只把主人明确选择的结果发布到频道。
6. **QwenPaw Hub 可复用一半能力**：它已有用户认证、`owner_user_id` 隔离、HTTP/WebSocket 代理和个人 Runtime；但目前只支持 Hub 主机上的 `local/docker` 托管，尚不等于“成员自己电脑上的 QwenPaw 反向接入”。本地设备连接仍需单独做复用优先的安全连接 Spike。

如果“用户绝不能感知 Mattermost 品牌或产品存在”是硬要求，则本建议失效：Mattermost 可以深度品牌化和扩展，但不是无痕 headless UI SDK。届时应重新评估独立前端及现成聊天 UI/SDK，而不是 fork Mattermost WebUI。

## 2. 调研对象与可复现基线

### 2.1 最新 Release 克隆

| 项目 | Release | 固定提交 | 本地只读目录 | 状态 |
|---|---:|---|---|---|
| Mattermost | `v11.10.1` | `f9deca984f8a8d38a5f5e50600b45e22c90ebca1` | `/Users/hrygo/Documents/mattermost` | detached HEAD，clean |
| Zulip Server | `12.2` | `1e73e1d754761b73c18135a3f25d0673f31cd8b3` | `/Users/hrygo/Documents/zulip` | detached HEAD，clean |
| Mattermost Agents | `v2.1.0` | `379b06b188d96544a909524f511823713f41b3d2` | `/Users/hrygo/Documents/mattermost-plugin-agents` | detached HEAD，clean |

Release 依据：

- [Mattermost v11.10.1](https://github.com/mattermost/mattermost/releases/tag/v11.10.1)
- [Zulip Server 12.2](https://github.com/zulip/zulip/releases/tag/12.2)
- [Mattermost Agents v2.1.0](https://github.com/mattermost/mattermost-plugin-agents/releases/tag/v2.1.0)

本次还交叉检查了已经固定的上游工作树：

| 项目 | 固定提交 | 用途 |
|---|---|---|
| AgentScope | `6c5c9eedb0a1afe515edcf6f2abec079e7ff6d9a` | `ChannelBase`、团队/频道协调边车基础 |
| QwenPaw | `35725c216eb93de790b464034e97795c3a0c7136` | Mattermost Channel、插件注册点、Hub、多用户/个人 Runtime |

### 2.2 方法和证据边界

- 深读发布标签下的架构文档、API、WebUI 扩展点、认证、Bot/私聊权限、许可和品牌边界。
- 克隆代码仅用于静态阅读；没有安装依赖、运行构建脚本或执行仓库代码。
- 同时检查官方 Mattermost Agents 插件，判断是否已有可直接复用的专家管理和权限实现。
- 代码知识图谱在本次新仓库索引时被另一个未确认的索引任务占用，因此 Mattermost/Zulip 的结论使用精确源码搜索和完整权威文件阅读得出；AgentScope/QwenPaw 的既有图索引与源码搜索相互校验。负面结论均限制在本报告列出的发布版本和检查范围内。
- 许可与商标部分是工程风险识别，不构成法律意见；商用或重新品牌发布前仍需法律复核。

## 3. Hikmah 的不可妥协需求

本次不按“功能最多”选底座，而按以下产品边界选：

- 3–20 人私密团队；有频道、线程和临时群聊。
- 共享专家席位通常由 QwenPaw 实现。
- 团队/频道自身是 AgentScope 协调边车：全局存在、轻量、默认沉默。
- 明确 `@专家` 时，协调边车只观察，不介入。
- 个人 Agent 严格仅主人可用；不能读取或加入共享频道；只有主人可以明确分享结果。
- 不重建聊天、用户、RBAC、搜索、文件和未读系统。
- 原则上不修改 AgentScope、QwenPaw、Mattermost 或 Zulip 核心；确有通用价值的修改走各自上游 PR，Hikmah 不依赖未合并补丁。
- 技术路线限定为 Python + TypeScript；只有验证确实无法绕开时才引入 Go。

## 4. 代码级发现

### 4.1 Mattermost：适合作为 UI 宿主和协作数据面

Mattermost v11.10.1 是 Go 服务端与 React/TypeScript WebApp 的单仓库。它提供稳定 REST API、WebSocket 事件和公开 TypeScript 客户端：

- [`@mattermost/client`](https://github.com/mattermost/mattermost/blob/v11.10.1/webapp/platform/client/README.md) 可以在浏览器中使用，处理 Cookie、CSRF 和 Token。
- [REST/WebSocket API 入口](https://github.com/mattermost/mattermost/blob/v11.10.1/api/v4/source/introduction.yaml) 明确了 `/api/v4` 与 `/api/v4/websocket`。
- WebApp 本身不是一个可直接嵌入 Hikmah 的完整聊天 UI 组件库；它是应用级私有包。因此“复用 Mattermost UI”应通过宿主扩展，而不是把其频道组件复制到另一个 SPA。

Web App Plugin 是本次选型的决定性差异：

- 官方明确把它定位为无需 fork/rebase 即可扩展 WebApp 的机制；支持频道头、侧栏、RHS、根组件和自定义帖子渲染。[官方说明](https://developers.mattermost.com/integrate/plugins/components/webapp/)
- 当前 SDK 支持 `registerCustomRoute`、`registerProduct`、`registerRightHandSidebarComponent`、`registerPostTypeComponent` 和 WebSocket 事件处理。[SDK 参考](https://developers.mattermost.com/integrate/reference/webapp/webapp-reference/)
- WebApp-only 插件不强制携带 Go 服务端组件。[快速开始](https://developers.mattermost.com/integrate/plugins/components/webapp/hello-world/)
- Hikmah 控制面可通过 Bot/REST 创建 `custom_hikmah_*` 帖子，TS 插件只负责渲染；帖子 `props` 只作为显示输入，不能作为审批授权依据。

这使得 Mattermost 能承载以下 Hikmah 产品面：

- Product 页面：专家目录、个人 Agent、知识候选、团队治理。
- 频道头/RHS：本频道专家席位、规则、协调边车状态。
- 富帖子：执行进度、审批请求、结果、知识候选、来源与审计摘要。
- 原生频道/线程：人类与专家的日常交流，不重复实现消息体验。

认证方面，Mattermost 可作为 OAuth 2.0 授权服务器，支持机密客户端授权码流，也支持 SPA 的 PKCE。Hikmah 应使用 Python BFF 的机密客户端授权码流，把令牌保存在服务端，浏览器只持有 HttpOnly Hikmah 会话；不要信任前端声称的 Mattermost user ID。[官方 OAuth 2.0 文档](https://developers.mattermost.com/integrate/apps/authentication/oauth2/)

品牌和许可不是零成本：

- 站点名称、登录页图像和文字可以配置。[品牌工具](https://docs.mattermost.com/administration-guide/configure/custom-branding-tools.html)
- About 等区域仍可能显示 Mattermost 归属信息；完全抹去品牌不能通过普通配置保证。
- v11.10.1 仓库对官方编译平台、源码构建、WebApp/配置工具采用不同许可说明，且 Mattermost 商标另受约束。发布模式必须按实际交付物复核。[v11.10.1 LICENSE](https://github.com/mattermost/mattermost/blob/v11.10.1/LICENSE.txt)、[许可 FAQ](https://docs.mattermost.com/product-overview/faq-license.html)、[商标规则](https://mattermost.com/trademark-standards-of-use/)
- 不能通过 fork WebApp 来追求无痕品牌；这违反 Hikmah 的“不改上游核心”原则，也会引入持续 rebase 成本。

升级方面，插件 SDK 是受支持边界，但不是零风险。Mattermost 已公告 v12 WebApp/插件将迁移 React 19；Hikmah 必须把每个目标 Mattermost 次版本纳入兼容矩阵和预发布验证，而不能依赖内部 WebApp 组件。[弃用与升级说明](https://docs.mattermost.com/product-overview/deprecated-features.html)

### 4.2 Zulip：协作模型强，但不适合作为当前混合 UI 宿主

Zulip 12.2 使用 Python/Django 后端、Tornado 实时事件和 TypeScript/JavaScript WebApp；整体采用 Apache-2.0。它的优势非常明确：

- Stream + Topic 天然适合长期结构化讨论。
- `/api/v1` 和 `/register` + `/events` 是稳定、公开、面向第三方客户端的接口。[API 设计](https://zulip.readthedocs.io/en/latest/processes/api-design.html)、[实时事件](https://dev.zulip.com/api/real-time-events)
- 组织名称和 Logo 可替换 Zulip 品牌。[组织资料](https://zulip.com/help/create-your-organization-profile)

但 WebUI 整合存在两个结构性问题：

1. 发布版本中没有找到与 Mattermost `registerPlugin`、custom route、product page、custom post renderer 对等的运行时 UI 插件 API。
2. Zulip 自己的 Widget 文档明确说明没有插件模型；新增 Widget 通常进入核心或提交上游。通用 `zform` 只能发送预设回复，无法承担 Hikmah 的执行/审批/知识富卡片。[Widget 子系统](https://github.com/zulip/zulip/blob/12.2/docs/subsystems/widgets.md)

独立 Hikmah SPA 对接 Zulip API 也不是低成本捷径：

- 稳定 API 默认使用 email + API key 的 HTTP Basic 认证；API key 不应存入浏览器。
- Web 客户端自己的 Session Cookie + CSRF 路径主要是 `/json` 内部接口，而不是应长期依赖的第三方 `/api/v1` 契约。[认证分支源码](https://github.com/zulip/zulip/blob/12.2/zerver/lib/rest.py#L183-L205)、[API key 文档](https://dev.zulip.com/api/api-keys)
- 因此独立浏览器客户端仍需 Hikmah BFF，并自行实现大量消息 UI 状态；官方 `zulip-js` 更偏 Node/API-key 客户端，不是完整浏览器聊天 SDK。

结论：如果 Mattermost 在许可、商标或部署硬门槛上失败，Zulip 是优秀的协作底座备选；但必须接受“原生 Zulip UI + 外部 Hikmah 门户”的割裂体验，或承担独立前端的显著成本。

### 4.3 Mattermost Agents：借鉴，不作为 Hikmah Agent Runtime

官方 Mattermost Agents v2.1.0 证明了“在 Mattermost 壳内做 Agent 产品”在工程上成立：

- 有 Agent 产品页、持久 Agent 与 Bot 身份、创建者/管理员、用户与频道访问规则、MCP 工具白名单和审批 UI。[管理 Agent](https://docs.mattermost.com/agents/docs/features/managing_agents.html)
- `bots/permissions.go` 在服务端统一执行用户、团队和频道 allow/block 规则；这是个人/共享 Agent 权限设计的重要参考。[固定版本源码](https://github.com/mattermost/mattermost-plugin-agents/blob/v2.1.0/bots/permissions.go#L19-L118)

但它不应直接成为 Hikmah 的 Agent 运行时：

- 它已经拥有自己的模型 Provider、Agent 配置、MCP、工具策略、记忆/会话和执行链，直接采用会与 QwenPaw/AgentScope 形成双重事实源。
- Provider 扩展边界是模型服务/OpenAI-compatible LLM，不是“委托给外部 QwenPaw Agent Runtime”；Provider 注册表在 Go 代码中静态定义。[Provider 源码](https://github.com/mattermost/mattermost-plugin-agents/blob/v2.1.0/llm/providers.go)
- 自助创建多个 Agent 的部分能力受 Mattermost 许可约束。

因此选择是 **Borrow，而不是 Adopt**：复用其交互模式、权限语义和测试场景；Hikmah 的 Runtime 真相仍在 QwenPaw/AgentScope。

### 4.4 AgentScope 与 QwenPaw 的既有连接点

- QwenPaw 已有 Mattermost Channel，实现 REST/WebSocket、提及触发、线程会话和可选 thread-follow；共享专家无需 Hikmah 重写 Mattermost 消息适配。[固定提交源码](https://github.com/agentscope-ai/QwenPaw/blob/35725c216eb93de790b464034e97795c3a0c7136/src/qwenpaw/app/channels/mattermost/channel.py)
- QwenPaw `PluginApi.register_channel` 是外部频道适配的公开注册点；如未来切换 Zulip，应优先在 Hikmah/独立插件包中实现适配，而不是修改 QwenPaw 核心。[固定提交源码](https://github.com/agentscope-ai/QwenPaw/blob/35725c216eb93de790b464034e97795c3a0c7136/src/qwenpaw/plugins/api.py#L631)
- AgentScope `ChannelBase` 是团队/频道协调边车应遵守的适配边界；当前固定提交中没有 Mattermost/Zulip 原生适配，因此 Hikmah 应拥有一个薄适配器。[固定提交源码](https://github.com/agentscope-ai/agentscope/blob/6c5c9eedb0a1afe515edcf6f2abec079e7ff6d9a/src/agentscope/app/channel/_base.py#L213)

### 4.5 QwenPaw Hub：可复用的个人 Runtime 控制面及其边界

QwenPaw Hub 已实现：

- Hub 用户认证和 Bearer Token 校验。
- `tenant_id`、`owner_user_id` 绑定；非管理员访问他人 Runtime 时返回 404。
- 每个用户的个人 Runtime 自动选择/创建。
- `/api/{path}` HTTP 代理与同路径 WebSocket 代理。
- Hub 到 Runtime 的独立内部边界令牌，浏览器授权头不会透传给 Runtime。
- 凭据按个人 Tenant/Runtime 范围隔离。

关键源码：

- [所有权校验与个人 Runtime](https://github.com/agentscope-ai/QwenPaw/blob/35725c216eb93de790b464034e97795c3a0c7136/src/qwenpaw/hub/control_app.py#L278-L352)
- [HTTP/WebSocket 个人 Runtime 代理](https://github.com/agentscope-ai/QwenPaw/blob/35725c216eb93de790b464034e97795c3a0c7136/src/qwenpaw/hub/control_app.py#L1203-L1415)
- [Provisioner 当前仅为 local/docker](https://github.com/agentscope-ai/QwenPaw/blob/35725c216eb93de790b464034e97795c3a0c7136/src/qwenpaw/hub/config.py#L229-L234)

因此：

- 对“由团队服务托管的个人 QwenPaw”，Hub 可以直接进入后续验证。
- 对“成员自己电脑运行的 QwenPaw”，Hub 尚无现成 remote provisioner、设备配对或出站隧道。Windows reverse tunnel 代码是同一宿主内 AppContainer 到宿主服务的隔离设施，不是互联网远程接入方案。
- ACP 可作为 Agent 交互协议参考，但不能自动解决设备身份、网络穿透、撤销、轮换和离线状态。

## 5. WebUI 路线比较

| 路线 | 聊天能力复用 | Hikmah 产品面 | Python + TS | 不 fork | 个人 Agent 严格边界 | 综合判断 |
|---|---|---|---|---|---|---|
| A. 独立 Hikmah SPA + Mattermost API | 中 | 高 | 是 | 是 | 可由 BFF 实现 | 可行但重复实现大量聊天体验，暂缓 |
| B. Mattermost 原生 UI，不做插件 | 高 | 低 | 是 | 是 | 否 | 太像“给 Mattermost 加几个 Bot” |
| **C. Mattermost 壳 + Hikmah TS Plugin + Python 控制面** | **高** | **高** | **是** | **是** | **改用 owner-only 产品页后可实现** | **推荐 MVP** |
| D. fork/白标 Mattermost WebApp | 高 | 高 | 否，涉及 Go/上游内部 | 否 | 可实现 | 否决 |
| E. Zulip 原生 UI + 外部门户 | 高 | 中低 | 是 | 是 | 需外部门户实现 | 备选，但体验割裂 |
| F. 独立 Hikmah SPA + Zulip API | 中 | 高 | 是 | 是 | 可由 BFF 实现 | BFF 与 UI 重建成本最高 |
| G. fork Zulip WebUI | 高 | 高 | 是 | 否 | 可实现 | 否决 |

### 5.1 为什么不立即做独立 Hikmah WebUI

独立界面并非只需“消息列表 + 输入框”。要达到可用协作产品，至少还要复制：

- 虚拟滚动、分页、未读边界和跳转定位；
- 草稿、编辑、删除、回复、线程和附件；
- 提及补全、Emoji、通知、搜索、置顶和保存；
- WebSocket 重连、乱序/重复事件处理和乐观更新；
- 权限变化、频道成员变化和删除事件；
- 键盘导航、可访问性、移动端响应式与本地化。

这些不是 Hikmah 的差异化能力。Mattermost Plugin 路线可以直接保留原生实现，把自研投入集中在专家协作。

### 5.2 何时才升级为独立 Hikmah WebUI

只有以下任一条件被真实用户验证后，才重开独立前端决策：

- 用户因 Mattermost 信息架构而无法理解或完成 Hikmah 核心任务；
- 品牌/商标要求不允许出现 Mattermost 产品归属；
- 插件 SDK 无法承载经验证的关键交互，且上游无稳定扩展点；
- 需要同时支持多个协作底座，并确认统一客户端的价值高于适配成本。

## 6. 推荐整合架构

```text
┌──────────────────────── 浏览器 ────────────────────────┐
│ Mattermost 原生频道/线程                               │
│ + Hikmah TypeScript Web App Plugin                     │
│   ├─ Product 页面：专家 / 个人 Agent / 知识 / 治理      │
│   ├─ 频道头与 RHS：席位 / 规则 / 边车状态               │
│   └─ custom_hikmah_*：执行 / 审批 / 结果 / 知识卡片     │
└───────────────┬──────────────────────┬─────────────────┘
                │ Mattermost REST/WS   │ Hikmah Session
                ▼                      ▼
┌────────────────────────┐   ┌───────────────────────────┐
│ Mattermost Foundation  │   │ Hikmah Python Control Plane│
│ 用户/团队/频道/帖子/文件 │◄─►│ OAuth/BFF、策略、映射、审计 │
│ 线程/搜索/未读/RBAC      │   │ 执行、审批、知识候选        │
└───────────────┬────────┘   └───────────┬───────────────┘
                │ Bot REST/WS            │ Runtime adapters
                ▼                        ▼
        ┌───────────────┐       ┌────────────────────────┐
        │ 共享 QwenPaw   │       │ AgentScope 协调边车      │
        │ 专家席位        │       │ team/channel scoped     │
        └───────────────┘       └────────────────────────┘
                                             │
                           ┌─────────────────┴────────────┐
                           │ 个人 Agent owner-only surface│
                           │ QwenPaw Hub 或未来本地连接器   │
                           └──────────────────────────────┘
```

### 6.1 事实源划分

| 数据/行为 | 唯一事实源 | Hikmah 是否复制 |
|---|---|---|
| 用户、团队、频道、成员关系 | Mattermost | 只缓存外部 ID 与最小投影 |
| 帖子、线程、文件、搜索、未读 | Mattermost | 不复制全文历史，按需保存关联 ID/审计摘要 |
| 专家定义、版本、能力、所有者 | Hikmah | 是 |
| 专家与频道席位绑定 | Hikmah | 是，并引用 Mattermost IDs |
| QwenPaw 会话、工具和运行时状态 | QwenPaw | 只保存运行时引用和可公开状态 |
| 团队/频道协调规则与状态 | Hikmah + AgentScope | 是 |
| 执行、审批、幂等键、审计 | Hikmah | 是；帖子卡片只是投影 |
| 个人 Agent 私有历史 | 用户个人 QwenPaw | 否；明确分享时生成独立快照 |

### 6.2 运行时职责

**Hikmah TypeScript Plugin**

- 只调用稳定 Mattermost Plugin SDK 和 Hikmah 公共 API。
- 不 import Mattermost WebApp 内部私有组件。
- 自定义帖子类型使用命名空间 `custom_hikmah_*`。
- UI 隐藏按钮不等于授权；所有变更操作由控制面重新鉴权。

**Hikmah Python Control Plane**

- 通过 Mattermost OAuth 2.0 绑定用户身份。
- 保存 Mattermost external IDs、Agent/runtime IDs 和关联状态。
- 校验团队/频道成员关系、专家席位、审批角色和资源版本。
- 为按钮操作提供幂等键和状态机，避免重复执行。
- 通过 Bot 令牌或受控服务账号使用 Mattermost REST/WebSocket。
- 调用 QwenPaw 和 AgentScope 公开扩展边界，不侵入其内部存储。

**QwenPaw 共享专家**

- 每个专家使用明确 Bot 身份和最小频道成员范围。
- 利用现有 Mattermost Channel 的 `@`/线程语义。
- 不能把 System Admin 权限授予专家 Bot。

**AgentScope 团队/频道边车**

- 每个团队/频道拥有逻辑身份，但默认静默观察。
- 明确 `@专家` 时写入 `directed=true` 路由事实，边车只观察。
- 仅在规则触发、无人接手、冲突协调或明确 `@边车` 时介入。
- 其输出和干预原因必须可审计。

## 7. 个人 Agent 的硬门槛修正

### 7.1 为什么不能使用普通 Foundation Bot 私聊

Mattermost 默认普通用户角色拥有创建私聊和查看成员的能力；创建 Direct Channel 的服务端检查是通用权限与成员可见性，不是“这个 Bot 只允许某个主人私聊”的对象级 ACL。[默认角色源码](https://github.com/mattermost/mattermost/blob/v11.10.1/server/public/model/role.go#L1170)、[创建私聊源码](https://github.com/mattermost/mattermost/blob/v11.10.1/server/channels/api4/channel.go#L602)

Zulip 也不是替代解法：其消息发送逻辑明确允许人类向 Bot 发私信，即使组织已关闭普通用户私信。[固定版本源码](https://github.com/zulip/zulip/blob/12.2/zerver/actions/message_send.py#L1640)

因此“个人 Agent = Foundation Bot + owner DM”无法满足当前的严格边界。Mattermost Agents 插件可以在插件服务端拒绝未授权使用，但那是插件自身的运行时权限，不是 Foundation 对私聊对象的原生 ACL；直接采用又会重复 QwenPaw Runtime。

### 7.2 推荐模型

个人 Agent 不加入 Mattermost 团队/频道，也不暴露可搜索、可私聊的 Mattermost Bot 身份：

1. 主人从 Hikmah Product 页面打开个人 Agent。
2. Python 控制面用已验证的 Hikmah/Mattermost 身份解析唯一 owner binding。
3. 控制面连接到该 owner 的 QwenPaw Runtime；QwenPaw Hub 已能覆盖中心托管模式。
4. 其他成员既没有 UI 入口，也无法通过 API 解析或调用该 Runtime；控制面返回 404 而非泄露存在性。
5. 主人点击“分享到频道”时，控制面重新校验主人对目标频道的发帖权限，生成新的共享快照帖子。
6. 快照只含主人明确选择的内容、来源与时间，不给频道任何回读个人会话或工具的能力。

### 7.3 本地 QwenPaw 的未闭合环节

成员本地运行模式仍缺一个安全、可撤销的连接器。下一项 Spike 必须优先评估现成开源方案，而不是自造加密隧道，验收至少包括：

- 本地端只建立出站连接，不要求家庭路由器开放端口；
- 一次性配对码不能重放，设备密钥可轮换和撤销；
- 控制面只能路由到已绑定 owner，不能枚举其他 Runtime；
- 端到端或应用层消息加密边界明确；
- 离线、重连、背压、取消和大消息限制可观察；
- Agent 工具权限仍由本地 QwenPaw 决定，Hikmah 不接管主人的本地凭据；
- 能复用 QwenPaw HTTP/WebSocket/ACP 边界，不修改 QwenPaw 核心。

在该 Spike 通过前，不应把“成员本地 QwenPaw 已可安全接入”写成已完成能力。

## 8. 认证与安全边界

### 8.1 推荐认证流

1. Mattermost 管理员注册一个受信任的 Hikmah OAuth 2.0 机密客户端，关闭动态客户端注册。
2. Python BFF 执行 Authorization Code Flow；`state` 必须一次性校验，建议同时使用 PKCE。
3. OAuth access/refresh token 只存控制面加密存储；浏览器只获取 `Secure`、`HttpOnly`、适当 `SameSite` 的短会话 Cookie。
4. 反向代理把 `/hikmah/*` 路由到 Python BFF，使插件和控制面保持可控同源；路径与 Cookie scope 必须避免覆盖 Mattermost 自身 Cookie。
5. 每个写操作都重新验证 Hikmah session、资源 owner、Mattermost 成员关系、当前状态版本和幂等键。

### 8.2 必须禁止的捷径

- 不接受浏览器提交的 `user_id`、`team_id` 或“我是管理员”作为授权事实。
- 不把 Mattermost OAuth token、Bot token、QwenPaw token 放入 `localStorage`、帖子 `props`、URL query 或前端日志。
- 不因按钮在 UI 中不可见就跳过服务端权限检查。
- 不把富帖子正文或 Agent 输出当作可信指令；工具执行必须经过结构化策略和审批。
- 不给共享专家或协调边车 System Admin；频道成员资格与 Bot 权限采用最小集合。
- 不自动把个人 Agent 上下文同步到共享频道。

## 9. 建议的 Hikmah 仓库边界

这不是最终目录承诺，只是用于验证职责是否清晰：

```text
hikmah/
├── apps/
│   └── mattermost-webapp/       # TypeScript，宿主 UI 扩展
├── services/
│   └── control-plane/           # Python，OAuth/BFF/策略/执行/审计
├── packages/
│   └── contracts/               # OpenAPI/JSON Schema/生成类型
├── adapters/
│   ├── mattermost/              # Foundation 端口
│   ├── qwenpaw/                 # Runtime 端口
│   └── agentscope/              # 协调边车 ChannelBase 适配
└── tests/
    ├── contract/
    └── vertical-slice/
```

只为当前已选 Mattermost 实现一个 Foundation Adapter。不要在 MVP 预先设计一个同时覆盖 Mattermost/Zulip 的庞大通用抽象；先把稳定外部契约、领域事件和合同测试建立起来，真正确认切换需求后再抽取第二实现。

## 10. 下一阶段验证计划

在更新正式 ADR 前，建议执行一个最小但完整的垂直 Spike。它不是生产实现，必须在临时环境中完成：

### 10.1 S0：许可、商标与产品呈现门槛

- 明确 Hikmah 的交付模式：托管服务、官方二进制部署、源码构建或客户自建。
- 法律复核 Mattermost 许可组合和商标呈现。
- 产品负责人接受“主要呈现 Hikmah 品牌，但部分系统区域仍可能出现 Mattermost 归属”。

失败条件：必须完全无痕白标，或交付模式与许可边界冲突。

### 10.2 S1：宿主 UI 与身份

- WebApp-only 插件注册 Hikmah Product 页面、频道 RHS 和一个 `custom_hikmah_probe` 帖子类型。
- Python BFF 完成 Mattermost OAuth 登录、`/users/me` 校验和 HttpOnly 会话。
- 不使用 Mattermost WebApp 私有组件，不携带 Go server plugin。

### 10.3 S2：共享专家

- 一个 QwenPaw Mattermost 专家加入指定测试频道。
- `@专家` 在原线程回复，重连后不重复响应。
- 非席位频道不能调用该专家。

### 10.4 S3：团队/频道协调边车

- AgentScope 适配器只消费规范化事件。
- 普通对话保持沉默；明确 `@专家` 时记录观察但零干预。
- 明确 `@边车` 或测试规则触发时才发言，并附可审计原因。

### 10.5 S4：执行与审批卡片

- QwenPaw 发起一项需审批操作，控制面写入版本化执行记录并投影为自定义帖子。
- 两次点击、旧版本点击、无权限点击都不能重复或越权执行。
- 卡片损坏或插件未加载时仍有可理解的纯文本降级。

### 10.6 S5：个人 Agent

- Hub 托管个人 Runtime 证明 owner-only 代理、404 隐藏、凭据隔离和明确分享快照。
- 另做本地 QwenPaw 连接器候选 Spike；在通过安全验收前不承诺本地模式上线。

### 10.7 升级与回退

- 在 Mattermost v11.10.1 与目标下一兼容版本运行合同/E2E 测试。
- 禁用 Hikmah 插件后，Mattermost 原生频道仍完整可用。
- 停止 Hikmah 控制面后，聊天数据不丢失；自定义帖子有文本降级。
- QwenPaw/AgentScope 不可用时，控制面显示退化状态而不是阻塞人类交流。

## 11. 后续正式决议

本报告形成下列建议后，用户已通过 ADR-0003～ADR-0005 将其接受为正式目标架构：

1. Mattermost 为首选协作 Foundation 和 MVP UI 宿主；Zulip 为首要备选。
2. Hikmah MVP 不建设独立完整 WebUI，而建设嵌入 Mattermost 的 TS 产品层。
3. Python 控制面通过 Mattermost OAuth/BFF 负责 Hikmah 身份、策略、Agent 映射、执行与审计。
4. 共享专家继续使用 QwenPaw Mattermost Channel；协调边车使用 Hikmah 所有的 AgentScope ChannelBase 适配器。
5. 个人 Agent 不映射为 Foundation Bot；使用 owner-only Hikmah 产品面。
6. QwenPaw Hub 先用于中心托管个人 Runtime；成员本地 QwenPaw 连接作为独立复用优先 Spike。
7. 法律/品牌门槛或插件垂直 Spike 任一失败，则回到 Zulip/独立 UI 候选，不 fork 上游。

## 12. 当前推荐的决策语句

> Hikmah（群贤）采用 Mattermost 作为协作数据面与 MVP WebUI 宿主，通过 TypeScript Web App Plugin 提供专家、协调、执行、审批、知识与个人 Agent 产品体验；Python 控制面通过 OAuth/BFF 和稳定 API 管理 Hikmah 领域状态，并以 QwenPaw 为专家/个人 Agent Runtime、AgentScope 为轻量团队/频道协调边车。Hikmah 不 fork 或修改上游核心。个人 Agent 不作为 Foundation Bot 暴露，其本地设备接入须通过后续安全连接 Spike。
