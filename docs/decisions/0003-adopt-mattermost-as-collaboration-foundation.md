---
title: ADR-0003：选定 Mattermost 作为协作底座 (Collaboration Foundation)
description: 记录选定 Mattermost 作为 Hikmah 团队协作数据面与 UI 宿主的架构决议、验证门禁与退出路径。
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
  - decisions
  - mattermost
  - collaboration-foundation
canonical: true
related:
  - 0001-reuse-first-thin-control-plane.md
  - 0002-collaboration-foundation-spike.md
  - 0004-trusted-identity-and-personal-agent-isolation.md
  - 0005-public-integration-contracts-and-fail-closed-semantics.md
  - 0006-governance-metadata-persistence-and-schema-lifecycle.md
  - ../architecture/version-baseline.md
  - ../research/2026-08-28-mattermost-zulip-webui-integration.md
  - ../product/overview.md
  - ../project/prd-architecture-review-tracker.md
---

# ADR-0003：选定 Mattermost 作为协作底座 (Collaboration Foundation)

> **状态**：Accepted（已采纳）
>
> **决策者**：产品负责人与架构组
>
> **关联调研**：[WebUI 与协作底座整合深度调研](../research/2026-08-28-mattermost-zulip-webui-integration.md)
>
> **验证边界**：`Accepted` 表示 Mattermost 作为目标底座的决策已采纳，不表示 ADR-0002 的运行态 Spike、隐私、升级及许可证/品牌门禁均已有证据。开放项见 [AR-001、AR-004、AR-007](../project/prd-architecture-review-tracker.md)。

---

## 1. 背景与上下文 (Context)

在 [ADR-0001](0001-reuse-first-thin-control-plane.md) 中，Hikmah 确立了**复用优先、建设轻量治理控制层**的核心原则，避免从零研发重复的即时通信全栈。

在 [ADR-0002](0002-collaboration-foundation-spike.md) 与专项调研中，我们针对候选底座（Mattermost、Zulip、Open WebUI Channels、CircleChat）进行了技术生态、扩展模型、Agent 接入可行性与许可证边界的综合评估：

- **Mattermost**：成熟的企业级私有 IM，拥有完整的 Team/Channel/Thread/DM/文件/搜索体系、强大的 Bot API & WebSocket 事件流，以及独有的 **Web App Plugin 机制**（允许在无需 fork 核心前端的前提下嵌入 React 视图、右侧侧边栏、自定义 Post 渲染与顶部栏入口）。QwenPaw 官方已具备原生 Mattermost 接入支持。
- **Zulip**：Topic 线程模型清晰，Apache-2.0 协议友好，但缺乏类似 Web App Plugin 的运行时轻量 UI 注入机制，定制富交互需要 fork WebUI 或单独维护门户。
- **Open WebUI / CircleChat**：作为交互模式参考，但作为私有团队通用生产级 IM 协作底座存在成熟度或权限模型局限。

---

## 2. 决策内容 (Decision)

我们正式**选定 Mattermost 作为 Hikmah 的团队协作底座（Collaboration Foundation）与用户界面宿主**。精确目标版本由[版本基线](../architecture/version-baseline.md)唯一维护。

### 2.1 职责与事实源划分
1. **Mattermost 是协作数据面与 UI 宿主**：负责组织/团队/频道管理、消息流、线程、文件、未读通知、基础 RBAC 与客户端分发（Web / Desktop / Mobile）。
2. **Hikmah 是独立的薄治理与编排控制层 (Python FastAPI)**：负责 Expert Seat 席位映射、Coordinator Sidecar 智能协调（静默/@ 抑制/单主答）、Knowledge Promotion 人审晋升流、全链路 Correlation Record 审计与 Personal Agent 隐私上下文控制。
3. **Hikmah 不复制第四套状态**：Hikmah 仅持久化自身的薄治理元数据（席位映射、协调规则、审核记录、Trace 关联），不直连读写 Mattermost 私有数据库，不复制全量聊天历史。

### 2.2 交互与扩展架构
1. **UI 宿主形态**：采用 **Mattermost Web App Plugin (React 19 / TypeScript)** 嵌入定制入口：
   - 右侧面板 (Right-Hand Sidebar, RHS)：承载 Agent 详情、知识晋升审核单、审批卡片与执行 Trace。
   - 自定义 Post 富组件：渲染结构化审批按钮、流式状态指示与引用溯源卡片。
   - 主菜单与顶部栏入口：提供 Hikmah 团队治理控制台与 Personal Agent owner-only 产品页。
2. **通信与集成协议**：
   - 使用 Mattermost 官方 REST API (v4) 与 Bot Token 驱动 Expert 席位发帖与交互。
   - 通过 Mattermost WebSocket 事件流监听频道动态并分发给 Hikmah Coordinator 与 Sidecar。
   - 通过 Mattermost OAuth 2.0 + Hikmah BFF 建立交互式可信身份；浏览器不持有上游服务凭据。
   - 绝不使用未合并的私有补丁，绝不维护长期私有 fork。

### 2.3 个人专属 Agent (Personal Agent) 隐私保护
- 不将 Personal Agent 注册为 Mattermost 公共可私聊的 Bot。
- Personal Agent 仅在 Hikmah 提供的 Owner-only 专属页面中交互，由本地/私有 Runtime 直连；仅当 Owner 显式点击“分享到频道”时，才通过 Hikmah 将生成内容以 Owner 署名或授权卡片发布至指定 Mattermost 频道。
- 身份、角色、资源授权、404 隐藏存在性和 Secret 边界遵守 [ADR-0004](0004-trusted-identity-and-personal-agent-isolation.md)。

---

## 3. 影响与收益 (Consequences)

### 正向收益 (Positive)
- **复用成熟协作能力**：直接采用 Mattermost 消息、文件、多端客户端与基础权限，Hikmah 聚焦治理与编排差异化能力。
- **统一协作入口**：人类、Shared Expert 与治理动作在 Mattermost 信息架构内可见，Personal Agent 保持独立 owner-only 边界。
- **受支持的升级边界**：只依赖公开 Plugin、REST、WebSocket 与 OAuth 接口，不产生私有 fork；每个目标版本仍必须通过兼容与回退门禁。

### 限制与应对 (Trade-offs & Mitigations)
- **许可证与品牌门禁**：进程/接口隔离是工程边界，不构成法律结论。每种分发方式必须完成许可证与商标复核；未通过时禁止发布。
- **单底座窄适配**：只实现 Mattermost 所需的窄适配边界，不预建多 Foundation 通用框架。切换底座时通过新的 ADR 和迁移方案演进。

## 4. 发布门禁与退出路径

Mattermost 进入 Hikmah 支持矩阵前必须完成：

1. OAuth/BFF、Plugin、REST/WebSocket 与 QwenPaw Mattermost Channel 契约验证；
2. 显式 @零介入、未 @单主答和 Personal Agent owner-only 安全验证；
3. Plugin 安装、禁用、文本降级、目标版本升级和回退验证；
4. 目标分发模式的许可证与品牌复核；
5. PostgreSQL 迁移、备份恢复和量化 NFR 验收。

任一硬门禁失败时，Mattermost 仍是已接受的目标方向，但相应 release 不得发布。若缺口无法通过公开扩展点修复，则创建新的 ADR 评估 Zulip 或独立 UI，并由新 ADR supersede 本决议；失败本身不授权 fork Mattermost。
