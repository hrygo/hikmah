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
  - ../architecture/version-baseline.md
  - ../decisions/0004-trusted-identity-and-personal-agent-isolation.md
  - ../decisions/0005-public-integration-contracts-and-fail-closed-semantics.md
  - ../decisions/0006-governance-metadata-persistence-and-schema-lifecycle.md
  - ../project/prd-architecture-review-tracker.md
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
| 4 | 显式 @ / 未显式 @双路径、协作流与边车干预边界 | 批准；早期 TaskRun 状态机由 Correlation Record 替代，终态判定表写入产品规范 |
| 5 | 记忆作用域、Personal Agent 隐私、知识晋升和执行审批 | 批准 |
| 6 | 运行拓扑、降级、验证、MVP 与成册交付 | 批准 |
| 7 | 最终品牌命名 | GitHub repo 为 hikmah；英文 Hikmah；中文 群贤 |
| 8 | 其他实体命名 | 不设置独立品牌名，只使用功能名称 |
| 9 | 系统设计原则 | 批准“不重复造轮子”；产品本身及各组件都须先开展广泛 GitHub 调研 |

## 2026-08-28 复用优先与底座定型决议

GitHub 调研与深度代码分析完成了底座选型与架构定型：

- `ADR-0001`（轻量治理控制层）与 `ADR-0003`（选定 Mattermost 作为协作底座与 UI 宿主）正式 Accepted；
- 自建 Community Web/API、Agent Gateway、AgentLink、独立 Policy/Approval、TaskRun 工作流等早期自建轮子全部撤销；
- 架构定型为 **Mattermost 宿主壳 + Web App Plugin (React 19 / TypeScript) + Python FastAPI 控制面**；
- 运行时唯一绑定 **QwenPaw**（专家席位 & 个人专属助理）与 **AgentScope**（团队/频道 Coordinator Sidecar 协调与多 Agent 协同工作流）；
- 此次定型严格保持三类 Agent 身份、两级轻量 Sidecar、显式 @ 零介入、Personal Agent owner-only、知识人审晋升等已批准产品行为。

## 适用规则

- 原始画布是设计过程材料，保留早期工作名称作为历史档案。
- 本批准记录用于追溯，不替代正式规范。
- 最终技术要求以 `docs/product/overview.md`、目标版本基线和 Accepted ADR（ADR-0001、ADR-0003～ADR-0006）为准。


## 2026-08-28 文档信息架构重组

- 批准按生命周期组织 `docs/`：产品、架构、决策、研究、设计、开发、项目治理和历史归档。
- 批准根目录 GitHub 社区入口例外：`README.md`、`CONTRIBUTING.md`、`SECURITY.md`、`CODE_OF_CONDUCT.md` 和 `LICENSE` 保持原位。
- 批准 Markdown 使用 YAML front matter、完整 HTML 使用 `hikmah:*` meta、HTML 源片段使用 metadata 注释。
- 批准历史设计画布和已完成计划归档但不删除，并以导航、状态和相对链接保证可追溯性。

## 2026-08-28 正式文档终态归一化

用户明确批准“方案 A，仅修改文档”：正式产品规范、架构导航和 ADR 使用确定性的目标终态语言，审查跟踪表单独记录脚手架差距、代码授权和验证证据。

- 接受 ADR-0004：Mattermost OAuth/BFF 可信身份、角色矩阵和 Personal Agent owner-only 隔离；
- 接受 ADR-0005：Mattermost/QwenPaw/AgentScope 公开契约、生产 Plugin 交付和 fail-closed 状态；
- 接受 ADR-0006：Hikmah 独立 PostgreSQL 16 database/role、Alembic、保留与恢复；
- 批准 Coordinator 终态判定表、每事件一名主答/最多两名补充专家的循环预算；
- 批准 MVP 量化 NFR 与 release qualification 门禁；
- 批准目标版本基线作为唯一版本口径；
- 明确许可证/品牌、运行 Spike、升级和端到端结果仍需证据，不因设计获批而标记为已验证。
