---
title: Pilot 2：有限自动协作实施计划
description: 实现完整路由判定表、AgentScope 两级 Sidecar 窄适配和持久化邀请预算，并验证故障降级。
document_type: implementation-plan
status: review
created: 2026-09-05
updated: 2026-09-05
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - pilot
  - coordination
canonical: true
related:
  - 2026-09-05-implementation-roadmap.md
  - 2026-09-05-pilot-0-foundation.md
  - 2026-09-05-pilot-1-knowledge.md
  - ../../product/overview.md
  - ../../decisions/0005-public-integration-contracts-and-fail-closed-semantics.md
---

# Pilot 2：有限自动协作实施计划

> 执行者使用 `executing-plans`，默认单 Agent。本计划未执行。Pilot 1 的负责人评审及本阶段实施授权通过后才执行；自动协作仅在本阶段资格全部通过后开放。

**目标：** 无明确提及时按规则选择唯一主答、最多邀请两名一层补充专家，显式 @保持原生直达及 Sidecar 零介入。

**架构：** Hikmah 确定性规则返回路由理由，AgentScope 负责公开事件映射与 Sidecar 协作。实际专家入口复用 P0 准入和 PostgreSQL 原子保留，不能只在协调器本地计数。

**技术栈：** 固定版本 AgentScope 的公开 Channel 接口、Mattermost REST/WebSocket、Hikmah Python 治理服务、pytest 和隔离 E2E。

**规范与全局约束：** 继承[总览全部约束](2026-09-05-implementation-roadmap.md#1-全局约束)，严格实现 [PRD 第 7、9、14、17 节](../../product/overview.md)。Sidecar 不给专业结论、不替人审批；显式人类多专家不受自动单主答预算改写，指定专家不能自动再邀请。个人代理和业务写能力继续关闭。本文 API 短路径位于 `apps/api/src/hikmah/`。

## P2-01：完整、确定性的路由判定

**文件：** 修改 `services/coordinator.py`、`models/rule.py`、`schemas/rule.py`、规则 API；新增 `schemas/routing.py`、`services/event_normalization.py`、`apps/api/tests/test_routing_matrix.py`、`test_event_normalization.py`；同步 API Client 规则类型和 Web 配置。

**输入契约：** `RouteInput` 为不可变 dataclass，字段及默认值如下；字段来自规范化后的权威事实，不能直接由消息 JSON 反序列化：

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class RouteInput:
    valid: bool = False
    duplicate: bool = False
    sender_is_agent: bool = False
    correlated_agent_event: bool = False
    explicit_experts: tuple[str, ...] = ()
    coordinator_only: bool = False
    other_mentions: bool = False
    collaboration_intent: bool = False
    eligible: tuple[str, ...] = ()
    default_seat: str | None = None
    scores: tuple[tuple[str, float], ...] = ()
    threshold: float = 0.8
```

**输出契约：** `RouteDecision(action: Literal["silent", "observe", "governance", "unavailable", "select", "clarify"], target: str | None, reason: str)`；`evaluate_route(value: RouteInput) -> RouteDecision`。`valid=False` 表示无法建立权威事实，须静默；`threshold` 来自已审阅 Channel 规则，示例 0.8 只是测试默认，不宣称为优化后的产品值。

- [ ] 写精确理由码测试；先创建 schema，再让新 `evaluate_route` 缺失/不满足断言而失败：

```python
from hikmah.schemas.routing import RouteInput
from hikmah.services.coordinator import evaluate_route

def test_explicit_experts_override_automatic_selection() -> None:
    result = evaluate_route(RouteInput(
        valid=True, explicit_experts=("seat-a", "seat-b"),
        collaboration_intent=True, eligible=("seat-c",),
    ))
    assert (result.action, result.target, result.reason) == (
        "observe", None, "explicit_expert_mention",
    )

def test_tied_candidates_require_clarification() -> None:
    result = evaluate_route(RouteInput(
        valid=True, collaboration_intent=True, eligible=("a", "b"),
        scores=(("a", 0.9), ("b", 0.9)),
    ))
    assert (result.action, result.target, result.reason) == (
        "clarify", None, "clarification_required",
    )
```

- [ ] 运行 `uv run pytest apps/api/tests/test_routing_matrix.py -v` 确认上述失败；实现按顺序第一命中规则，`valid=False` 作为输入校验先拒绝。单候选直接选；多候选先检查合格默认及阈值，再检查唯一最高分；无分数/非有限值/越界分数不得猜测。默认专家不合格时不能通过默认选项绕过资格。

| 顺序 | 条件 | action / reason |
|---:|---|---|
| 输入保护 | 无法验证输入 | silent / unsupported_input |
| 1 | duplicate | silent / duplicate_event |
| 2 | Agent 事件且合法关联；否则 | observe / correlated_agent_event；silent / agent_loop_suppressed |
| 3 | 人类准确提及专家 | observe / explicit_expert_mention |
| 4 | 仅提及 Coordinator | governance / coordinator_addressed |
| 5 | 其他人类/群体/未知提及 | silent / human_addressed |
| 6 | 无协作意图 | silent / no_collaboration_intent |
| 7 | 无合格专家 | unavailable / no_eligible_expert |
| 8 | 一名合格专家 | select / single_eligible_expert |
| 9 | 合格默认且达阈值 | select / eligible_default_expert |
| 10 | 唯一最高合格专家且达阈值 | select / unique_best_expert |
| 11 | 并列、低置信度或不可靠判断 | clarify / clarification_required |

- [ ] 在事件规范化层执行权威 Post/发送者/提及校验、成员关系、shared 类型、启用/可路由、capability、scope、readiness 和预算检查。`eligible` 是经这些检查的集合；推理模型不能写入事实字段。只在确定性专长规则无法消除多候选歧义时调用轻量分类，结果仍只产生候选分数。
- [ ] 把表中每行加入参数化回归，并增加排列不变性：候选顺序改变不影响结果；每次输出最多一个 target；只有 `select` 有 target；显式专家分支不会调用轻量模型、消息写回、邀请、总结或调停。代码/引用提及、用户名碰撞、人类提及、未知目标分别断言。
- [ ] 运行矩阵及规范化测试、规则 HTTP 测试和全局严格检查；提交 `feat: implement deterministic coordinator routing matrix`。本任务只证明纯决策，实际事件幂等、可见发帖和跨服务预算由 P2-02/03 验证。

## P2-02：AgentScope 窄适配与持久邀请预算

**文件：** 新增 `integrations/agentscope/hikmah_sidecar.py`、独立运行配置及锁文件、`services/coordination_ledger.py`、`models/coordination.py`、后继 Alembic 迁移、`apps/api/tests/test_coordination_budget.py`、`tests/contracts/test_agentscope_adapter.py`；修改 P0 `services/admission.py`、`schemas/admission.py`、内部准入 API、Trace 投影及 Web 状态。

**接口：** `reserve_participation(session: AsyncSession, root_post_id: str, seat_id: str, role: Literal["lead", "supplement"], inviter_seat_id: str | None, depth: int) -> bool`。调用前已经核验服务身份和权威根 Post；账本保存原始人类事件、Channel/Thread、规则版本、选定主答、受邀席位和外部引用，不能承担运行时执行/审批状态机。

**持久不变量：** 每根人类事件只有一条自动路由记录；`(root_post_id, seat_id)` 唯一；最多一 lead、两 supplement；supplement 只可由该 lead 发起且 `depth=1`，被邀请者不能继续邀请。重试产生新帖子 id 也不能重置根事件预算。显式人类调用沿 P0 直达，不创建自动扩展资格。

- [ ] 写角色/深度纯判定测试，并定义 `may_invite(is_auto_lead: bool, depth: int, remaining: int) -> bool`：

```python
from hikmah.services.coordination_ledger import may_invite

def test_supplement_cannot_invite_again() -> None:
    assert may_invite(True, 1, 2)
    assert not may_invite(False, 1, 2)
    assert not may_invite(True, 2, 2)
    assert not may_invite(True, 1, 0)
```

- [ ] 运行 `uv run pytest apps/api/tests/test_coordination_budget.py -v` 先失败；实现 `return is_auto_lead and depth == 1 and remaining > 0`。事务版 `reserve_participation` 必须对根事件预算行加锁并依靠唯一约束；不能从客户端提供 remaining，也不能只使用进程内锁。
- [ ] 在同一事务中固定唯一主答、占用参与者/提示预算和准入保留。重复角色、同一席位改角色、主答未知结果、新 Post 伪造旧 correlation、补充者递归、跨 Thread、过期/取消来源均拒绝。外部发送前持久记录派生 `dispatch_pending`，超时变 `verification_required`，不自动换主答或再次发送。
- [ ] 用固定版本公开 `ChannelBase`/协作接口实现 Mattermost WebSocket→权威事件查询→`RouteInput`→`RouteDecision`→原生 @/Bot Post→QwenPaw。事件适配只用公开契约；不实现另一条通用任务总线。将确切公开调用签名与最终依赖版本记录在 `test_agentscope_adapter.py` 契约断言中，目标不兼容先停止。
- [ ] 自动邀请先经服务身份登记精确根事件、邀请者、目标席位和 Thread，再发邀请 Post。目标专家 Hook 反查并原子消费同一登记；仅正文中的 @和 correlation 无效。QwenPaw 主答没有公开方式在发邀请前登记时，自动邀请保持关闭并作为本阶段未通过项，不能由 Sidecar偷偷代为扩展授权。
- [ ] Team Sidecar 只处理名册/规则视图、经授权的知识候选移交及明确配置的治理提醒，不读无关频道正文。Channel Sidecar 的澄清/治理提示每个人类事件合计最多一次；明确 @时全部禁止。无人响应先显示状态，只在新的真实人类授权后改派一次；未知执行不因超时自动重试。
- [ ] 冲突提示和主答整合、计划性总结仅在其 Channel 规则与授权范围内触发，沿用 P1 受众/发送检查；总结只产生候选，不发布知识。定时触发复用既有运行时能力，不自建调度器；未配置计划任务默认不启动。
- [ ] 在隔离 PostgreSQL 运行 20 个并发邀请，断言每根事件参与者不超过 3、只有 lead 能邀请、重启后预算不恢复；测试提示预算、迟到回复和部分失败。运行单测及 `uv run pytest tests/contracts/test_agentscope_adapter.py -v`。提交 `feat: coordinate through public adapters with durable invitation limits`。

## P2-03：重放、循环和故障降级资格

**文件：** 新增 `tests/e2e/test_pilot_two.py`、`tests/integration/test_coordination_replay.py`、`tests/fixtures/coordination-events.json`、`docs/research/pilot-2-qualification.md`；修改只针对隔离 profile 的故障注入 fixture、Plugin 派生状态测试、CI 可选择的契约/E2E 作业。

**接口：** 脱敏实验结果字段 `root_post_id`、`explicit_expert_count`、`sidecar_interventions`、`automatic_leads`、`automatic_supplements`、`max_invitation_depth`、`duplicate_external_posts`、`observed_runtime_starts`、`status_unknown_retries`、`evidence_refs`。所有计数来自权威 Post/运行时启动观察及账本关联，不能只统计 Sidecar 计划输出。

- [ ] 先写验收结果判定函数测试，定义 `within_automatic_budget(leads: int, supplements: int, depth: int) -> bool`：

```python
def within_automatic_budget(leads: int, supplements: int, depth: int) -> bool:
    return 0 <= leads <= 1 and 0 <= supplements <= 2 and 0 <= depth <= 1

def test_budget_rejects_amplification() -> None:
    assert within_automatic_budget(1, 2, 1)
    assert not within_automatic_budget(2, 0, 1)
    assert not within_automatic_budget(1, 3, 1)
    assert not within_automatic_budget(1, 2, 2)
```

- [ ] 将判定函数放 `tests/e2e/coordination_assertions.py`，测试先从该模块导入执行失败，再实现；配置包路径使独立测试可导入。此函数不参与生产授权，不能把它的通过当端到端证据。
- [ ] 在获准隔离环境逐一注入：事件重复/乱序、席位选择后离线、Sidecar 进程重启、准入数据库短断、上游 POST 发出后超时、Hook 重载、恶意 Agent 无限互相 @、伪造 correlation、同根事件用不同 Post 邀请、补充专家再邀请、迟到结果和权限撤销。期望重复外部副作用为 0、未知结果自动重试为 0。
- [ ] 停止 AgentScope，验证合法人类明确 @仍由独立 P0 准入通过、同 Thread 回答且 Sidecar 介入 0；随后停止准入服务，确认模型/工具启动为 0。二者是不同故障域，不能为保证“直达”而绕过准入。
- [ ] 显式一名和多名专家、人类手工邀请、只 @Coordinator、只 @人类、无 @闲聊、无资格专家、默认失效、唯一高分、并列/低分逐项实际验证。对显式专家统计路由、澄清、总结、调停、邀请和代答合计必须为 0；人类显式多专家不能被自动预算拒绝或改写。
- [ ] 复测 P1 知识：自动主答/补充者均只获得该目标频道获准内容，撤回传播仍有效；补充信息回原 Thread，主答只整合获准证据。测量规范化到决策延迟并单列模型时间，不将轻量分类开销藏入上游耗时。
- [ ] 运行 `uv run pytest tests/integration/test_coordination_replay.py -v`、`uv run pytest tests/e2e/test_pilot_two.py -v` 和全局门禁；报告 BOM、并发、样本、实际指标和失败项。仅在全部阶段安全不变量通过后标记 Pilot 2 qualified；完整 NFR 仍在 RQ 验收。
- [ ] 提交 `test: qualify bounded collaboration and degraded operation`，由负责人决定开放范围。失败时禁用自动路由/邀请，保留已经独立通过门禁的显式专家与知识能力；若故障影响共享准入或知识授权，则同步停用受影响能力，不能笼统宣称降级可用。

## 发布衔接

本计划完成仅表示有限自动协作通过资格。将 AR-005/010、CR-006/007/012 的证据按实际覆盖范围关联，Personal、业务执行及完整发布要求进入[总览高级能力工作包](2026-09-05-implementation-roadmap.md#4-完整终态覆盖与高级能力排期)。不把剩余门禁改为已验证，不自动部署或合并到 main。
