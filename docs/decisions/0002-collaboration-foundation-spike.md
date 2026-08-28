---
title: ADR-0002：通过 Foundation Reuse Spike 选择协作底座
description: 提议通过统一场景和硬门槛验证 Mattermost、Zulip 等协作底座。
document_type: architecture-decision
status: proposed
created: 2026-08-28
updated: 2026-08-28
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - architecture
  - collaboration-foundation
  - spike
canonical: true
related:
  - 0001-reuse-first-thin-control-plane.md
  - ../research/2026-08-28-github-reuse-landscape.md
  - ../research/2026-08-28-mattermost-zulip-webui-integration.md
---

# ADR-0002：通过 Foundation Reuse Spike 选择协作底座

> 决策类型：待产品负责人复核后执行的选型验证。

## Context

Hikmah 需要邀请制 Team、Channel、Thread/Topic、DM、文件、搜索、基础 RBAC、Bot/Event API、自托管和可升级性。文档和源码调研无法替代真实安装、端到端 Agent 接入、隐私隔离、许可确认与升级验证。

四个候选覆盖不同风险轴：

- Mattermost：技术成熟，且 QwenPaw 已有内置 Channel；许可与品牌路径必须先确认；
- Zulip：Apache-2.0，Topic 模型清晰；需要 QwenPaw 外部 Channel Plugin；
- Open WebUI Channels：AI 原生体验最强；定制许可证、三类身份和 Personal Agent 隔离待证；
- CircleChat：功能形态最接近；项目成熟度、维护集中度和高权限部署路径待证。

## Proposed decision

在任何 Hikmah 应用实现前，先运行一个有时间上限、使用同一验收脚本的 Foundation Reuse Spike：

1. Mattermost 为技术首选；
2. Zulip 为首要备选，并在 Mattermost 许可/品牌门禁失败时自动升为首选；
3. Open WebUI Channels 用于检验 AI 原生 Foundation 是否能无侵入满足身份与本地 Agent 边界；
4. CircleChat 用于功能完整度和交互模式对照，当前不作为生产底座默认候选。

Matrix、Rocket.Chat、Discourse、LibreChat 与 OpenAgents 保留为长名单；只有前四项均失败或需求发生变化时再进入 Spike。

最终选定结果必须另写 Accepted ADR；本 ADR 不预先指定赢家。

## Required scenarios

1. 私有部署、邀请、Channel、Thread/Topic、DM、文件、搜索；
2. Shared QwenPaw Expert 通过 @在同一 Thread 流式回复；
3. AgentScope Channel Sidecar 观察事件；显式 @为零介入，未 @只选一名主答；
4. 本机 Personal QwenPaw 仅 Owner 可用、不能读共享 Channel、可由 Owner 显式分享；
5. 只读自动、副作用原生审批暂停/恢复、可见且可审计；
6. 跨系统关联而不复制消息正文；
7. 在无核心补丁条件下完成一次兼容升级。

## Hard gates

- 许可证、商标、品牌和目标分发方式获接受；
- 不修改 Foundation、AgentScope、QwenPaw 核心源码；
- 不新增消息、身份、通用审批或通用工作流引擎；
- Personal Agent 隐私测试和 Sidecar 显式 @静默测试全部通过；
- 插件、工具和容器不获得无法解释的主机级权限；
- 部署、备份、恢复、升级和退出路径可重复。

## Output

Spike 必须输出：

- 可复现环境和固定版本清单；
- 每个场景的通过/失败证据；
- 许可证/品牌结论和未决问题；
- 运维、安全、升级、插件开发量和迁移成本对比；
- 最终 Accepted/Rejected ADR；
- 未入选候选的明确退出理由。

## Consequences

- 在底座确定前，不编写面向某一 Foundation 的完整实现计划；
- 允许写一次性验证 Adapter，但不得把它包装成生产组件；
- 若所有候选失败，先复盘需求是否过度定制，再扩大候选范围；“全部失败”本身不授权从零建设完整社区平台。
