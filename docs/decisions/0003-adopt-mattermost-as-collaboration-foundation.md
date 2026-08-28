---
title: ADR-0003：选定 Mattermost 作为协作底座 (Collaboration Foundation)
description: 记录选定 Mattermost v11.10.x 作为 Hikmah 团队协作数据面与 UI 宿主的架构决议与集成策略。
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
  - ../research/2026-08-28-mattermost-zulip-webui-integration.md
  - ../product/overview.md
---

# ADR-0003：选定 Mattermost 作为协作底座 (Collaboration Foundation)

> **状态**：Accepted（已采纳）  
> **决策者**：产品负责人与架构组  
> **关联调研**：[WebUI 与协作底座整合深度调研](../research/2026-08-28-mattermost-zulip-webui-integration.md)

---

## 1. 背景与上下文 (Context)

在 [ADR-0001](0001-reuse-first-thin-control-plane.md) 中，Hikmah 确立了**复用优先、建设轻量治理控制层**的核心原则，避免从零研发重复的即时通信全栈。

在 [ADR-0002](0002-collaboration-foundation-spike.md) 与专项调研中，我们针对候选底座（Mattermost、Zulip、Open WebUI Channels、CircleChat）进行了技术生态、扩展模型、Agent 接入可行性与许可证边界的综合评估：

- **Mattermost**：成熟的企业级私有 IM，拥有完整的 Team/Channel/Thread/DM/文件/搜索体系、强大的 Bot API & WebSocket 事件流，以及独有的 **Web App Plugin 机制**（允许在无需 fork 核心前端的前提下嵌入 React 视图、右侧侧边栏、自定义 Post 渲染与顶部栏入口）。QwenPaw 官方已具备原生 Mattermost 接入支持。
- **Zulip**：Topic 线程模型清晰，Apache-2.0 协议友好，但缺乏类似 Web App Plugin 的运行时轻量 UI 注入机制，定制富交互需要 fork WebUI 或单独维护门户。
- **Open WebUI / CircleChat**：作为交互模式参考，但作为私有团队通用生产级 IM 协作底座存在成熟度或权限模型局限。

---

## 2. 决策内容 (Decision)

我们正式**选定 Mattermost (`v11.10.x+`) 作为 Hikmah 的团队协作底座（Collaboration Foundation）与用户界面宿主**：

### 2.1 职责与事实源划分
1. **Mattermost 是协作数据面与 UI 宿主**：负责组织/团队/频道管理、消息流、线程、文件、未读通知、基础 RBAC 与客户端分发（Web / Desktop / Mobile）。
2. **Hikmah 是独立的薄治理与编排控制层 (Python FastAPI)**：负责 Expert Seat 席位映射、Coordinator Sidecar 智能协调（静默/@ 抑制/单主答）、Knowledge Promotion 人审晋升流、全链路 Correlation Record 审计与 Personal Agent 隐私上下文控制。
3. **Hikmah 不复制第四套状态**：Hikmah 仅持久化自身的薄治理元数据（席位映射、协调规则、审核记录、Trace 关联），不直连读写 Mattermost 私有数据库，不复制全量聊天历史。

### 2.2 交互与扩展架构
1. **UI 宿主形态**：采用 **Mattermost Web App Plugin (React 19 / TypeScript)** 嵌入定制入口：
   - 右侧面板 (Right-Hand Sidebar, RHS)：承载 Agent 详情、知识晋升审核单、审批卡片与执行 Trace。
   - 自定义 Post 富组件：渲染结构化审批按钮、流式状态指示与引用溯源卡片。
   - 主菜单与顶部栏入口：提供 Hikmah 团队治理控制台与个人 Agent 隐私空间。
2. **通信与集成协议**：
   - 使用 Mattermost 官方 REST API (v4) 与 Bot Token 驱动 Expert 席位发帖与交互。
   - 通过 Mattermost WebSocket 事件流监听频道动态并分发给 Hikmah Coordinator 与 Sidecar。
   - 绝不使用未合并的私有补丁，绝不维护长期私有 fork。

### 2.3 个人专属 Agent (Personal Agent) 隐私保护
- 不将 Personal Agent 注册为 Mattermost 公共可私聊的 Bot。
- Personal Agent 仅在 Hikmah 提供的 Owner-only 专属页面中交互，由本地/私有 Runtime 直连；仅当 Owner 显式点击“分享到频道”时，才通过 Hikmah 将生成内容以 Owner 署名或授权卡片发布至指定 Mattermost 频道。

---

## 3. 影响与收益 (Consequences)

### 正向收益 (Positive)
- **研发效率极大提升**：直接复用 Mattermost 极其成熟的消息流、富文本、文件上传、多端客户端与权限安全，研发团队可 100% 聚焦于 Agent 治理与编排创新。
- **用户体验零割裂**：用户在熟悉的统一团队聊天界面内与同事及 Agent 协作，无需在多个独立系统间来回切换。
- **无侵入可升级性**：纯 Plugin + Bot API 集成模式使得 Mattermost 上游版本可无缝滚动升级，不产生私有代码分叉包袱。

### 限制与应对 (Trade-offs & Mitigations)
- **许可证与品牌合规**：Mattermost 核心采用 AGPL-3.0 / Commercial 许可。Hikmah 采用 Apache-2.0 独立服务与公开 Plugin 架构，通过官方扩展点解耦，严格保持接口与进程隔离，符合开源与分发规范。
- **多底座抽象**：Hikmah 控制层内部定义统一的 `CollaborationFoundationAdapter` 抽象接口，隔离 Mattermost 具体 API 细节，为未来扩展保留清晰边界。
