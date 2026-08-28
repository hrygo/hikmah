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
  - version-baseline.md
  - ../project/prd-architecture-review-tracker.md
---

# Hikmah 架构导航

Hikmah 是建立在 Mattermost、QwenPaw 和 AgentScope 之上的轻量治理与编排层。终态产品行为以[产品与技术架构](../product/overview.md)为准；不可逆技术选择由 [ADR](../decisions/README.md) 记录；精确目标版本由[版本基线](version-baseline.md)维护；研究报告只提供时间有界证据。

截至 2026-08-28，仓库代码用于表达目标架构和接口边界，属于架构脚手架；本页的组件关系不代表真实端到端链路已经通过。设计、证据和验收缺口统一见 [PRD 与技术架构方案审查跟踪表](../project/prd-architecture-review-tracker.md)。

## 终态组件关系

```text
Mattermost Foundation ── 用户、团队、频道、消息、文件、搜索、RBAC
       │
       ├── Hikmah Web App Plugin + OAuth/BFF
       │          └── 专家席位、规则、知识、关联审计
       │          │
       │          ├── QwenPaw ── 共享专家 Channel 与 owner-only Personal Runtime
       │          └── AgentScope ── Team/Channel 轻量协调边车
       │
       └── Hikmah PostgreSQL ── 独立治理元数据，不复制消息正文
```

## 当前状态

- 复用优先和轻量控制层原则已经接受：[ADR-0001](../decisions/0001-reuse-first-thin-control-plane.md)。
- 协作底座已正式选定 Mattermost：[ADR-0003](../decisions/0003-adopt-mattermost-as-collaboration-foundation.md)。
- 身份与 Personal Agent 隔离遵守 [ADR-0004](../decisions/0004-trusted-identity-and-personal-agent-isolation.md)。
- 集成、Plugin 交付和失败语义遵守 [ADR-0005](../decisions/0005-public-integration-contracts-and-fail-closed-semantics.md)。
- 治理元数据、迁移与恢复遵守 [ADR-0006](../decisions/0006-governance-metadata-persistence-and-schema-lifecycle.md)。
- 架构形态为 **Mattermost 宿主壳 + Hikmah Web App Plugin + Python OAuth/BFF + PostgreSQL + QwenPaw + AgentScope**。
- “已选定”不等于“已完成运行验证”；当前开放项及关闭条件见[架构审查跟踪表](../project/prd-architecture-review-tracker.md)。


## 维护规则

不要在本导航页复制领域规则或接口定义。架构发生变化时，先更新 Accepted ADR 和产品事实源，再更新此处摘要。
