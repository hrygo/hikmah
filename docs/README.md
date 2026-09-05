---
title: Hikmah 文档中心
description: Hikmah 产品、架构、决策、研究、设计、开发和历史资料的统一导航入口。
document_type: documentation-index
status: active
created: 2026-08-28
updated: 2026-09-05
owners:
  - hikmah-maintainers
audience:
  - users
  - contributors
  - maintainers
tags:
  - documentation
  - navigation
canonical: false
---

# Hikmah 文档中心

本目录是 Hikmah（群贤）产品与开源项目文档的统一入口。根目录 `README.md`、`CONTRIBUTING.md`、`SECURITY.md`、`CODE_OF_CONDUCT.md` 和 `LICENSE` 保留在 GitHub 可原生发现的位置；其余长期文档在这里按用途和生命周期管理。

## 推荐阅读顺序

1. [产品与技术架构](product/overview.md)：了解愿景、边界、领域模型和 MVP。
2. [架构导航](architecture/README.md)：理解组件关系、事实源和当前技术状态。
3. [目标版本与发布基线](architecture/version-baseline.md)：确认目标 BOM、兼容和许可证门禁。
4. [架构决策记录](decisions/README.md)：查看已经接受或仍在提议中的不可逆决策。
5. [PRD 与技术架构方案审查跟踪表](project/prd-architecture-review-tracker.md)：确认设计闭环、实现授权和验证状态。
6. [研究报告](research/README.md)：查阅复用调研、源码证据和候选方案。
7. [设计资料](design/README.md)：查看设计册和批准记录。
8. [开发文档](development/README.md)：进入贡献、实施和验证流程。

## 文档分区

| 分区 | 用途 | 主要读者 |
|---|---|---|
| [`product/`](product/overview.md) | 产品愿景、范围、行为和产品级架构事实源 | 全部参与者 |
| [`architecture/`](architecture/README.md) | 系统地图、组件边界和技术导航 | 贡献者、维护者 |
| [`decisions/`](decisions/README.md) | Architecture Decision Records | 贡献者、维护者 |
| [`research/`](research/README.md) | 外部调研、源码证据和 Spike 结论 | 贡献者、维护者 |
| [`design/`](design/README.md) | 设计册、批准记录和可视化交付物 | 产品、设计、维护者 |
| [`development/`](development/README.md) | 开发入口、计划和质量要求 | 贡献者 |
| [`project/`](project/documentation-policy.md) | 文档治理规则、metadata 规范和[架构审查跟踪](project/prd-architecture-review-tracker.md) | 维护者 |
| [`archive/`](archive/README.md) | 已完成、已替代或仅供追溯的资料 | 维护者 |

## 当前状态

| 主题 | 状态 | 事实源 |
|---|---|---|
| 复用优先原则 | Accepted | [ADR-0001](decisions/0001-reuse-first-thin-control-plane.md) |
| Collaboration Foundation 选型 (Mattermost) | Accepted | [ADR-0003](decisions/0003-adopt-mattermost-as-collaboration-foundation.md) |
| 身份与 Personal Agent 隔离 | Accepted | [ADR-0004](decisions/0004-trusted-identity-and-personal-agent-isolation.md) |
| 集成与 fail-closed 语义 | Accepted | [ADR-0005](decisions/0005-public-integration-contracts-and-fail-closed-semantics.md) |
| 治理元数据持久化 | Accepted | [ADR-0006](decisions/0006-governance-metadata-persistence-and-schema-lifecycle.md) |
| 知识协作试点与运行边界 | Accepted / 运行证据待补 | [ADR-0007](decisions/0007-knowledge-collaboration-pilot-and-runtime-boundaries.md) |
| 产品与技术架构 | Active | [产品与技术架构](product/overview.md) |
| 目标版本与发布基线 | Active | [版本基线](architecture/version-baseline.md) |
| HTML 设计册 | Active / 待同步本轮试点补充 | [设计资料](design/README.md) |
| PRD 与技术架构审查 | Active / 设计与证据分项跟踪 | [审查跟踪表](project/prd-architecture-review-tracker.md) |

状态与 metadata 的唯一规范见[文档治理规则](project/documentation-policy.md)。
