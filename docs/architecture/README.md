---
title: Hikmah 架构导航
description: 提供 Hikmah 系统边界、组件关系、事实源和当前架构状态的入口。
document_type: architecture-overview
status: active
created: 2026-08-28
updated: 2026-08-28
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - architecture
  - navigation
canonical: false
related:
  - ../product/overview.md
  - ../decisions/README.md
  - ../research/README.md
---

# Hikmah 架构导航

Hikmah 是建立在现有协作平台、QwenPaw 和 AgentScope 之上的轻量产品层。当前产品行为与完整边界以[产品与技术架构](../product/overview.md)为准；不可逆技术选择由 [ADR](../decisions/README.md) 记录，候选和源码证据由[研究报告](../research/README.md)提供。

## 当前组件关系

```text
协作 Foundation ── 用户、团队、频道、消息、文件、搜索、RBAC
       │
       ├── Hikmah 产品层 ── 专家席位、策略、审批、知识候选、审计
       │          │
       │          ├── QwenPaw ── 共享专家与个人 Agent Runtime
       │          └── AgentScope ── 团队/频道轻量协调边车
       │
       └── Hikmah WebUI 扩展 ── 产品页、RHS、富消息卡片
```

## 当前状态

- 复用优先和轻量控制层原则已经接受：[ADR-0001](../decisions/0001-reuse-first-thin-control-plane.md)。
- 协作底座已正式选定 Mattermost：[ADR-0003](../decisions/0003-adopt-mattermost-as-collaboration-foundation.md)。
- 架构形态确立为 **Mattermost 宿主壳 + Hikmah Web App Plugin (TS/React) + Python FastAPI 控制面**（参考 [WebUI 整合调研](../research/2026-08-28-mattermost-zulip-webui-integration.md)）。


## 维护规则

不要在本导航页复制领域规则或接口定义。架构发生变化时，先更新 Accepted ADR 和产品事实源，再更新此处摘要。
