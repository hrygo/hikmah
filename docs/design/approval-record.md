---
title: Hikmah 设计批准与修订记录
description: 记录 Hikmah 交互式产品设计阶段的批准结果、修订依据和适用边界。
document_type: design-record
status: active
created: 2026-08-28
updated: 2026-08-28
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - design
  - approvals
canonical: true
related:
  - ../product/overview.md
  - hikmah-design-book.html
---

# Hikmah 设计批准与修订记录

> 来源：当前交互式产品设计会话中的终端确认、visual companion 点击事件及 GitHub 复用调研。

## 已批准内容

| 顺序 | 设计内容 | 批准结果 |
|---|---|---|
| 1 | AgentScope × QwenPaw 总体组合架构 | 历史批准；其中自建 Agent Gateway 的实现方式已被 ADR-0001 替代，产品行为不变 |
| 2 | 系统边界与代码所有权 | 批准；产品独立仓库，上游原则不修改 |
| 3 | 领域模型、三类 Agent 身份与权限 | 批准 |
| 4 | 显式 @ / 未显式 @双路径、协作流与边车干预边界 | 产品行为获批准；早期自建 TaskRun 状态机已被 Correlation Record 方案替代，等待整体复核 |
| 5 | 记忆作用域、Personal Agent 隐私、知识晋升和执行审批 | 批准 |
| 6 | 运行拓扑、降级、验证、MVP 与成册交付 | 批准 |
| 7 | 最终品牌命名 | GitHub repo 为 hikmah；英文 Hikmah；中文 群贤 |
| 8 | 其他实体命名 | 不设置独立品牌名，只使用功能名称 |
| 9 | 系统设计原则 | 批准“不重复造轮子”；产品本身及各组件都须先开展广泛 GitHub 调研 |

## 2026-08-28 复用优先修订

GitHub 调研发现早期架构重复了成熟协作平台、AgentScope 和 QwenPaw 已有能力，因此作出以下文档修订：

- `ADR-0001` 中“复用优先”原则已接受；由调研推导出的轻量治理控制层边界随完整修订稿等待用户复核；
- 自建 Community Web/API、Agent Gateway、AgentLink、独立 Policy/Approval、TaskRun 工作流等早期实现被撤销；
- Mattermost、Zulip、Open WebUI Channels、CircleChat 进入统一 Foundation Reuse Spike；
- `ADR-0002` 仍为 Proposed，候选排序、验收方法和修订后的完整架构等待用户复核；
- 此次修订不改变三类 Agent 身份、两级轻量 Sidecar、显式 @零介入、Personal Agent owner-only、知识人审晋升等已批准产品行为。

## 适用规则

- 原始画布是设计过程材料，可能保留早期工作名称或未选择方案。
- 本批准记录用于追溯，不替代正式规范。
- 状态为 Accepted 的 ADR 记录架构原则；Proposed ADR 不能视为已获用户批准。
- 最终要求以 `docs/product/overview.md` 和 Accepted ADR 为准。

## 2026-08-28 文档信息架构重组

- 批准按生命周期组织 `docs/`：产品、架构、决策、研究、设计、开发、项目治理和历史归档。
- 批准根目录 GitHub 社区入口例外：`README.md`、`CONTRIBUTING.md`、`SECURITY.md`、`CODE_OF_CONDUCT.md` 和 `LICENSE` 保持原位。
- 批准 Markdown 使用 YAML front matter、完整 HTML 使用 `hikmah:*` meta、HTML 源片段使用 metadata 注释。
- 批准历史设计画布和已完成计划归档但不删除，并以导航、状态和相对链接保证可追溯性。
