---
title: Hikmah 团队交接入口
description: 顾问退出后的独立接手流程、事实基线、职责分配、资产交付及签收要求。
document_type: development-guide
status: active
created: 2026-09-05
updated: 2026-09-05
owners:
  - hikmah-maintainers
audience:
  - maintainers
  - contributors
tags:
  - handoff
  - delivery
canonical: true
related:
  - ../long-term-roadmap.md
  - ../prd-architecture-review-tracker.md
  - ../../development/worker-delivery-protocol.md
  - ../../development/plans/2026-09-05-work-item-sequence.md
  - successor-runbook.md
  - decision-register.md
  - records-and-acceptance.md
  - validation-record.md
---

# Hikmah 团队交接入口

这套交接面向没有原会话上下文的接续团队。产品负责人、技术负责人、worker 与评审人可以据仓库资料持续推进；后续问题由接续团队按职责处理，不以离任顾问回复作为任何任务的前置条件。

交付范围是产品方向、实施工作包、任务分派机制、已知风险与资格决策、只读校验器和可携带的 Git 交付物。产品仍是脚手架；交接完成不能解释为试点、部署或生产资格完成。

## 1. 第一次接手，从这里开始

1. 按[接手运行手册](successor-runbook.md)核验仓库基线和交付制品，不先启动服务、同步依赖或运行旧 API suite。
2. 用标准库检查交接完整性：`python3 scripts/check_handoff.py`；自测：`python3 -m unittest discover -s tests/handoff -v`。脚本支持 Python 3.9 及以上，产品 API 的 Python 3.14 目标不变。
3. 阅读[长期路线图](../long-term-roadmap.md)、[实施总览](../../development/plans/2026-09-05-implementation-roadmap.md)和[交付规范](../../development/worker-delivery-protocol.md)，明确本轮只处于 M0 的准备阶段。
4. 指定接续技术负责人和评审责任人，按[记录与签收](records-and-acceptance.md)完成接收检查，更新 `state.json` 的角色字段。无人承担这些职责时保持未分派；不能要求 worker 自审并开放能力。
5. 技术负责人复核 [P0-01.A 的完整任务卡](../../development/plans/2026-09-05-p0-01-worker-packet.md#p0-01a单元测试数据库准入)。确认工具链、基线及授权后，才将此卡标为 ready/authorized；其余任务按前置证据逐项解锁。

## 2. 离任时的事实基线

以下是 2026-09-05 的本地核验快照。后续团队以新的实测记录运行状态，不能把快照永久当现状。

| 项目 | 已知事实 | 不得推导的结论 |
|---|---|---|
| 本地 `main` 与缓存 `origin/main` | 都指向 `8ea48c2dc006b9ca69950e98821ed235e129a8b9`，对应 PR #4 合并 | 本次未刷新远端，不能据缓存保证远端永远一致 |
| 交接前文档分支 | `docs/knowledge-collaboration-pilot`，输入 HEAD `3aea245daa32a55b5e976638418963601d929e12` | 本地文档提交未因此成为 main 或远端发布 |
| 文档历史 | `080c903` 试点/隔离决策；`fedafae` 实施工作包；`3aea245` 长期路线/worker 规范 | 文档通过不是代码或运行门禁通过 |
| 代码 | 架构脚手架；API 测试误连风险、全局 Settings/Engine、模拟成功仍未修复 | 不能直接接真实团队或用旧 suite 验证交接 |
| 计划 | 14 个试点工作包、45 个工作项；P0-01.A～D 有完整卡，其余条目待前置证据后细化 | 45 项不是 45 张已批准实施卡；完成数仍为 0 |
| 运行与业务证据 | 本轮没有真实 OAuth/Plugin/Hook/隔离恢复/知识生命周期或 30 个真实任务评估 | 不宣称 Pilot 0/1/2 qualified、效果达标或生产就绪 |
| 原有设计册修改 | `docs/design/hikmah-design-book.html` 有用户未提交改动，SHA-256 为 `41b5d457ea658815dd008d57cb785053838510eb81989596cb7ab9849f61bb83` | 不纳入顾问提交，不覆盖、不自动当本轮新版规范 |

上述 HTML 在可携带交付目录中另存原样副本，供拥有者核对；其保留不表示内容获批。Git bundle 只承载已提交内容，不混入该用户工作副本、数据库、环境文件或凭据。

## 3. 已确定的方向与尚未证明的关键点

已确定：Mattermost 协作底座；QwenPaw 专家运行；AgentScope 两级协调；Hikmah 薄治理；先知识协作，后有限自动协作，再个人/业务执行，最后完整 MVP 资格。正式产品语义由 [PRD](../../product/overview.md)和 Accepted ADR 管理。

尚未证明、必须由继任者处理的高风险问题：

- QwenPaw 公开 Hook 缺失/卸载/故障时，是否确实阻止所有开放入口执行。
- Hook 之前的上下文读取、跨频道文件/记忆/工具隔离是否成立。
- 公开发送边界能否阻止撤回后新内容泄漏，并如实处理已在途发送。
- 固定版本的 OAuth、Plugin React 宿主兼容、迁移恢复及 AgentScope 邀请预算是否成立。

每项都有[决策交接记录](decision-register.md)，列明固定事实、实验、通过/失败动作与后继任务。继任者有足够路径继续查证；公开接口能力不足时允许得出失败结论并修订 ADR，不承诺必然通过。

## 4. 资料地图与唯一责任

| 资料 | 维护什么 | 接续责任人 |
|---|---|---|
| PRD / Accepted ADR / 版本基线 | 产品行为、架构取舍、精确目标版本 | 产品与技术负责人 |
| 长期路线图 / 实施总览 | 阶段目标与工作包 | 技术负责人，产品负责人确认方向 |
| 工作项队列 / `state.json` | ID/依赖/角色；动态准备度、授权和执行证据引用 | 技术负责人 |
| 完整任务卡 | 精确白名单、接口、测试、停止条件 | 技术负责人冻结，worker 执行 |
| 审查跟踪表 | AR/CR 的设计、授权、验证范围 | 技术负责人及评审人 |
| 本目录决策记录 | 尚未消除的关键未知及其解决程序 | 被指派的技术负责人 |
| 验证与签收记录 | 实际结果、制品哈希、接收人和日期 | 交付者与接收者分别填写 |

`state.json` 是工作项状态账本，不是 Agent 运行、审批或通用工作流系统。校验器只检查结构、依赖、文件和必要证据引用，不能辨别人工批准真伪、证据质量或产品安全。`errors: []` 只表示交接清单一致。

## 5. 权限、密钥和团队接收

仓库内不交接真实 Token、数据库口令、模型凭据或个人上下文。本轮没有创建/轮换/授予运行凭据。未来由受指派的操作者在批准目标按受控存储配置引用；权限实际可用与否由操作者核验。团队账号、角色、环境与预算不存在时不能由 worker 虚构默认值。

实现授权由产品/仓库负责人按任务范围记录。先前对 PR #4 的管理员合并豁免仅适用于那次操作，不授权后续绕过保护。后续远端 push、PR 合并、安装/部署和真实评估需落在明确授权范围内；已有明确授权不重复请求。

交接制品已形成与团队已签收分开记录。此快照中的接收角色尚未正式指定，签收状态为 `pending`；接续团队完成运行手册并填写接收记录后才能改为 received。离任顾问不会替未到场成员签字，也不是未来流程中的批准人。
