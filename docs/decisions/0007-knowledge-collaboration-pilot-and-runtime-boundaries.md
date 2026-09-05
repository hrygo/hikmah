---
title: ADR-0007：采用知识协作试点与明确的运行隔离边界
description: 保留完整 MVP 终态，先验证团队知识问答与方案协作，固化隔离、准入、知识受众和分阶段开放要求。
document_type: architecture-decision
status: accepted
created: 2026-09-05
updated: 2026-09-05
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - architecture
  - product
  - knowledge
  - isolation
canonical: true
related:
  - 0004-trusted-identity-and-personal-agent-isolation.md
  - 0005-public-integration-contracts-and-fail-closed-semantics.md
  - 0006-governance-metadata-persistence-and-schema-lifecycle.md
  - ../product/overview.md
  - ../research/2026-09-05-knowledge-collaboration-feasibility.md
  - ../project/prd-architecture-review-tracker.md
  - ../design/approval-record.md
---

# ADR-0007：采用知识协作试点与明确的运行隔离边界

> 状态：Accepted。用户于 2026-09-05 选择首批价值为“团队知识问答与方案协作”，并批准方案 A 的文档优化。
>
> 授权边界：更新设计、ADR、证据与跟踪；不授权代码、部署、真实联调或对外发布。运行验证仍未完成。

## 1. 背景

Hikmah 已选择 Mattermost + QwenPaw + AgentScope 的薄治理架构。当前完整 MVP 同时包含共享专家、自动路由、知识晋升、Personal Agent、审批及升级恢复；一次联调全部能力会混合产品价值和技术边界的验证。

本轮[可行性证据](../research/2026-09-05-knowledge-collaboration-feasibility.md)确认：QwenPaw 的共享实例具有操作者信任假设，session 不等于用户权限；原生 Mattermost 提及判断存在宽匹配；公开运行时 Hook 可短路执行，但位于 Channel 获取上下文之后。源码支持一种扩展方向，不证明它已经满足 Hikmah 的安全与交付要求。

## 2. 备选方案

| 方案 | 收益 | 代价 | 决议 |
|---|---|---|---|
| A：保留完整终态，增加分阶段试点 | 先验证真实知识价值，按能力关闭风险；保持原架构方向 | 需要独立记录每阶段证据与未开放能力 | 采用 |
| B：一次实现完整 MVP | 产品功能整体性强 | 本机连接、审批、隔离与协作同时联调，问题归因困难 | 不采用 |
| C：等待上游补齐后再建设 | 自有适配少 | 时间依赖上游，无法先验证团队价值 | 仅作为公开扩展点不足时的能力级退出选择 |

## 3. 决策

### 3.1 试点与完整 MVP 分开验收

完整产品目标和发布门禁保持有效。交付顺序调整为：隔离资格实验 → 显式 @知识协作与人工晋升 → 有限自动协作 → Personal Agent/业务执行的独立能力阶段 → 完整 MVP 发布资格。产品规范第 17 节是阶段范围与指标的事实源，不把试点成功标记为完整 MVP 成功。

首批 Web/Desktop 支持问答、方案比较、引用、人类邀请补充专家、知识审核与撤回；每席位只服务一个 Channel。先用至少 30 个真实任务记录可用性、引用、返工和采纳成本，安全用例逐项通过；无真实报告时不宣称价值或规模目标达成。

### 3.2 运行隔离与隐私承诺

不同频道的自动记忆、文件、索引、凭据和执行环境隔离；复用专业配置与已发布知识，不共享未审核对话。用配置、Bot ACL 和受限运行环境共同落实，而不是把 session/Workspace 名称当成安全证明。试点工具仅用于受控知识读取与草稿，不能借“只读任务”开放任意 Shell 或成员个人账户。

Personal Agent 的 owner-only 是产品和运行时授权边界；托管基础设施管理员是独立的可信运维角色。防基础设施管理员读取需要单独的威胁模型与技术决策，不能从 Hub 登录或容器隔离推导。现有产品角色限制继续有效。

### 3.3 公开 Hook 作为待验证的准入扩展

优先验证 `register_runtime_hook` / `PRE_DISPATCH` 在模型执行前完成真实 Post、发送者、目标、去重、作用域及自动邀请预算检查。它不选择专家、不改写人类请求、不拥有审批状态机；显式 @路径不依赖 AgentScope Sidecar 存活。

Hook 在 Channel 获取上下文之后，读取权限仍由前置 ACL 与运行隔离保障。必须验证 Hook 注册/缺失、故障、短路输出、重载、命令与其他入口覆盖，以及并发预算和重启恢复；相关检查不可用时拒绝对应 Agent 工作。公开扩展不足时关闭能力，再通过新 ADR 决定上游改进或窄适配；不改写私有方法或引入通用 Runtime Gateway。

### 3.4 协作与知识生命周期

补齐多候选高置信度、并列、仅 @人类及无法判定的路由分支。自动路由限一名主答、两名一层补充专家；人类显式 @多位专家仍直达，专家不自动追加邀请。预算在实际专家入口生效，不能只靠 Sidecar。

知识读取与公开回答同时核验发起者和目标受众。来源受限时使用获准发布的知识版本作为引用。撤回覆盖检索、发送、缓存、既有会话、自动记忆和索引；无法确认状态时停止受影响输出。已送达用户的内容不承诺收回，检查与外部发送之间的竞态必须有明确验收边界。

## 4. 后果与回退

- 增加按信任域运行的资源成本和 Hook 契约维护成本；先测量再扩大跨频道复用，不以共享可写记忆降低成本。
- 工具写权限、Personal Agent 和自动邀请逐项开放；未验证能力保持关闭，不删减完整终态。
- 故障优先禁用相关 Agent 能力，保留 Mattermost 原生聊天；回退不启用未治理执行，不清除用户数据。
- ADR-0004～0006 的补充条款及 PRD 同步修订；历史研究保留原快照，当前证据在新报告中记录。
- 交付关闭条件由 AR-009～AR-012 跟踪，代码候选保持 `not-authorized`。
