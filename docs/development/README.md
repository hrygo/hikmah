---
title: Hikmah 开发文档
description: Hikmah 贡献、实现计划、质量门禁和开发者文档的统一入口。
document_type: development-guide
status: active
created: 2026-08-28
updated: 2026-09-05
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - development
  - contributing
canonical: false
related:
  - ../../CONTRIBUTING.md
  - ../product/overview.md
  - ../architecture/version-baseline.md
  - ../decisions/README.md
  - ../project/prd-architecture-review-tracker.md
  - plans/2026-09-05-implementation-roadmap.md
  - ../project/long-term-roadmap.md
  - worker-delivery-protocol.md
  - plans/2026-09-05-work-item-sequence.md
---

# Hikmah 开发文档

Hikmah 当前仍处于产品与架构验证阶段。参与开发前请依次阅读：

1. [贡献指南](../../CONTRIBUTING.md)
2. [产品与技术架构](../product/overview.md)
3. [架构决策记录](../decisions/README.md)
4. [目标版本与发布基线](../architecture/version-baseline.md)
5. [PRD 与技术架构方案审查跟踪表](../project/prd-architecture-review-tracker.md)
6. [文档治理规则](../project/documentation-policy.md)

截至审查基线 `0d45229`，现有代码是用于讨论领域模型、接口和工程边界的脚手架，不代表生产能力。不得用构建或单元测试通过替代真实集成、安全、升级、恢复或许可证证据；后续代码实现必须由独立任务明确授权。

已完成的仓库初始化计划保存在[历史归档](../archive/github-bootstrap/implementation-plan.md)。新的实施计划应围绕一个可独立验证的交付切片编写；完成后根据其长期价值标记为 `completed` 或移入 `archive/`。

长期研发先读[路线图与方向约束](../project/long-term-roadmap.md)，分派和接续任务读[受控任务交付规范](worker-delivery-protocol.md)。知识协作的[实施总览](plans/2026-09-05-implementation-roadmap.md)与 Pilot 0～2 子计划包含 14 个工作包，[工作项队列](plans/2026-09-05-work-item-sequence.md)进一步分解为 45 项；当前完整的[首个工作包任务卡](plans/2026-09-05-p0-01-worker-packet.md)覆盖四张卡。

所有实施文档状态为 `review`、尚未执行；后继任务在前置证据成立后滚动冻结接口，不把简要工作项直接交给 worker 补设计。生成计划不改变代码授权、阶段资格或能力开放状态。
