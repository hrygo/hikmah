---
title: Hikmah 研究报告索引
description: 汇总 Hikmah 外部组件、源码、协议、许可和复用路线的研究证据。
document_type: documentation-index
status: active
created: 2026-08-28
updated: 2026-09-05
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - research
  - reuse
canonical: false
related:
  - ../decisions/README.md
  - ../project/prd-architecture-review-tracker.md
---

# Hikmah 研究报告索引

研究报告提供时间有界的证据和建议，不自动改变产品规范或 ADR 状态。

| 报告 | 状态 | 作用 |
|---|---|---|
| [GitHub 复用调研与组件决策矩阵](2026-08-28-github-reuse-landscape.md) | Completed snapshot | 建立“不重复造轮子”的候选长名单；后续决定以 ADR 为准 |
| [Mattermost、Zulip 与 WebUI 整合调研](2026-08-28-mattermost-zulip-webui-integration.md) | Completed snapshot | 固定调研时点版本并形成已由 ADR-0003～ADR-0005 落地的建议 |
| [知识协作试点可行性核验](2026-09-05-knowledge-collaboration-feasibility.md) | Completed snapshot | 固定版本信任模型、提及函数实验与公开 Hook 证据；方案由 ADR-0007 接受，真实联调仍待验证 |


引用研究结论时应同时记录快照日期、版本和证据边界。研究中的“建议”“候选”和“待批准”只反映当时状态；正式终态以产品规范和 Accepted ADR 为准，当前证据状态以审查跟踪表为准。版本或许可发生变化后新增带日期的后续报告，不静默改写历史证据。
