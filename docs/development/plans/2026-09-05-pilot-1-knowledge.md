---
title: Pilot 1：团队知识问答与方案协作实施计划
description: 实现人审知识版本、目标受众授权、引用与撤回，再以真实任务建立业务效果基线。
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
  - knowledge
canonical: true
related:
  - 2026-09-05-implementation-roadmap.md
  - 2026-09-05-pilot-0-foundation.md
  - 2026-09-05-pilot-2-coordination.md
  - ../../product/overview.md
  - ../../decisions/0006-governance-metadata-persistence-and-schema-lifecycle.md
---

# Pilot 1：团队知识问答与方案协作实施计划

> 执行者使用 `executing-plans`，默认单 Agent。本计划未执行；使用真实资料前需明确数据范围、参与者和运维责任。

**目标：** 团队能在原讨论中向专家问答、比较方案、人工晋升知识，查看有效引用并撤回知识；用至少 30 个真实任务决定是否扩大试点。

**架构：** PostgreSQL 保存经人审的知识规范对象；Runtime 索引只是可重建投影。检索先核验请求者和目标频道受众，发送前再次核验权威版本；拒绝不确定授权。

**技术栈：** P0 的 FastAPI/SQLAlchemy、React Plugin、QwenPaw 公开工具扩展及 pytest/Vitest；先做简单词法检索，不增加独立向量库或新的通用评测平台。

**规范与全局约束：** 继承[总览约束](2026-09-05-implementation-roadmap.md#1-全局约束)；[PRD 第 11、17 节](../../product/overview.md)及 [ADR-0006](../../decisions/0006-governance-metadata-persistence-and-schema-lifecycle.md)为事实源。进入本计划前 P0 资格通过；P1-01～03 只用合成数据验证，全部安全/恢复/许可门禁通过后才做 P1-04。Sidecar 自动主答、自动邀请、Personal 和业务写工具保持关闭。后文 API 短路径以 `apps/api/src/hikmah/` 为根。

## P1-01：知识候选、人审与不可变发布版本

**文件：** 修改 `models/knowledge.py`、`schemas/knowledge.py`、`api/v1/knowledge.py`；新增 `models/knowledge_version.py`、`services/knowledge_publication.py`、`apps/api/tests/test_knowledge_publication.py`、后继 Alembic 迁移；同步 `packages/api-client/src/` 和知识审核组件的类型/调用。P0 已有的 Actor、集中授权、会话和版本冲突机制直接复用。

**数据契约：** `KnowledgeCandidate` 保存来源引用、拟发布正文、敏感级别、拟发布 scope、proposer、review state、递增 `revision`。`KnowledgeVersion` 保存 `knowledge_id`、`version`、`content`、`content_digest`、`source_refs`、`publication_scope`、`sensitivity`、`proposer_id`、`reviewer_id`、`status: Literal["published", "superseded", "withdrawn"]`、时间。正文/来源/scope 不可原地改写，修订生成新版本。来源引用保存在获准规范对象内，Trace 不复制正文。

**审批接口：** `POST /api/v1/knowledge/candidates`；`POST /api/v1/knowledge/candidates/{id}/review` 请求仅含 `expected_revision: int`、`decision: Literal["approve", "reject"]`、`content_digest: str`、`idempotency_key: str`。reviewer 从 `AuthenticatedActor` 得出。编辑后的正文必须先保存候选新 revision，再批准；拒绝旧 digest。`GET /api/v1/knowledge/{id}/versions/{version}` 按当前 Actor/scope 返回安全视图。

- [ ] 新增并运行 digest 漂移失败测试；下面函数签名属于本任务交付物：

```python
import pytest
from hikmah.services.knowledge_publication import require_review_match

def test_review_cannot_approve_changed_candidate() -> None:
    with pytest.raises(ValueError, match="review_conflict"):
        require_review_match(4, "digest-new", 3, "digest-old")
```

- [ ] 运行 `uv run pytest apps/api/tests/test_knowledge_publication.py -v`，先确认新函数不存在；实现：

```python
def require_review_match(
    current_revision: int, current_digest: str,
    expected_revision: int, expected_digest: str,
) -> None:
    if (current_revision, current_digest) != (expected_revision, expected_digest):
        raise ValueError("review_conflict")
```

- [ ] 按固定序列化规则计算 digest：正文、来源引用、敏感级别、目标 scope 均纳入，键排序、编码固定；数据库用行锁或带 revision 的条件更新保证检查与发布一个事务。发布版本和幂等键唯一约束避免重复审核产生两份版本。
- [ ] 审阅前分别验证来源可处理/可分享权限和目标发布权限；仅“能读”不足以赋予转发权限。scope 明确为获准的整个 Team 或 Channel 受众；本阶段不支持零散个人授权对象直接注入频道回复。Bot/模型不得担任人类 reviewer；未获批准的摘要保持原 scope。
- [ ] HTTP/DB 回归覆盖：无权 reviewer、Body 伪造身份、无来源处理权、目标范围扩大、候选被并发编辑、重复批准、驳回后重放、原始标题/链接脱敏、来源删除或权限变动。修改正文/目标/来源任何一项都使旧批准失效；错误映射统一为 403/404/409，不返回敏感内容。
- [ ] 迁移升级并用隔离恢复库核验版本与审计关系，运行测试、Mypy 和 Client typecheck。提交 `feat: publish immutable knowledge through human review`。验收以数据库只有一个获批版本、真实 reviewer 和精确 scope 为证据。

## P1-02：面向受众的检索、引用及受控回答

**文件：** 新增 `services/knowledge_access.py`、`services/knowledge_retrieval.py`、`schemas/knowledge_query.py`、`api/internal/knowledge.py`、`integrations/qwenpaw/hikmah_knowledge.py`、`apps/api/tests/test_knowledge_access.py`、`test_knowledge_retrieval.py`、`tests/contracts/test_knowledge_runtime.py`；修改知识规范对象查询索引及 Runtime 配置。

**接口：** `KnowledgeQuery(post_id: str, seat_id: str, query: str, limit: int)`，limit 范围 1～10；使用 P0 内部服务认证和准入登记反查 Actor、Team、Thread，不接受模型指定 Actor/scope。`Citation(knowledge_id: str, version: int, content_digest: str, label: str, authorized_url: str)`；`KnowledgeHit(citation: Citation, excerpt: str)`。无获准证据返回空数组及 `evidence_insufficient`，不回退到全库检索。

**纯授权函数：** `can_use_version(status: str, requester_allowed: bool, audience_allowed: bool, source_grant_valid: bool) -> bool`。该函数只组合已经过权威核验的结果，不能把模型声称的 bool 当输入。

- [ ] 写并先运行受众交叉测试：

```python
from hikmah.services.knowledge_access import can_use_version

def test_requester_access_is_insufficient_for_channel_answer() -> None:
    assert not can_use_version("published", True, False, True)
    assert not can_use_version("withdrawn", True, True, True)
    assert not can_use_version("published", True, True, False)
    assert can_use_version("published", True, True, True)
```

- [ ] 用 `uv run pytest apps/api/tests/test_knowledge_access.py -v` 确认失败，再实现四项 conjunction。授权查询结果失败/过期/状态未知均视为 false；上游返回 403/404 时不暴露对象是否存在。
- [ ] 实现限定授权集合后的词法检索、分页/上限、引用构建。先基于规范表的标题/关键词/正文查询建立可解释基线；排序不改变权限过滤，分页数量不泄漏未授权命中。只有后续真实任务证明召回不足才另开检索优化任务。
- [ ] 明确频道受众判断：发布 grant 是覆盖该 Team/Channel 的显式人审授权，不是当前成员清单碰巧均可访问。每次读取检查请求者仍属于频道、知识 grant 未缩窄、来源处理授权仍有效；成员/来源/策略变动使已缓存授权失效。知识链接指向受保护的知识版本视图，不把原始私有链接或标题输出给目标受众。
- [ ] QwenPaw 仅注册该受控知识工具及草稿能力。系统上下文要求逐项引用、区分来源事实与推断，无证据明确说明；来源正文中的指令不改变工具/发布权限。网络工具和任意 Shell 保持禁用。新增对应 prompt 版本回归，不允许模型返回的任意 URL 直接作为可信引用。
- [ ] `test_knowledge_retrieval.py` 覆盖允许/禁止对象混合检索、分页侧信道、引用版本不存在、私有 source 标题、伪造 Actor、超长 query、提示注入和无答案。契约测试验证 Runtime 实際获得的只是获准 excerpt/citation，固定版本投影内容与权威 digest 相符。
- [ ] 运行 `uv run pytest apps/api/tests/test_knowledge_access.py apps/api/tests/test_knowledge_retrieval.py -v`，再在合成环境执行 `uv run pytest tests/contracts/test_knowledge_runtime.py -v`。提交 `feat: restrict knowledge retrieval to authorized publication audiences`；有引用不等于引用支持断言，后者由 P1-04 人类逐项评分。

## P1-03：撤回传播、发送前复核与 Web 闭环

**文件：** 新增 `services/knowledge_revocation.py`、`services/answer_guard.py`、`models/knowledge_usage.py`、`apps/api/tests/test_knowledge_revocation.py`、`test_answer_guard.py`、`tests/e2e/test_knowledge_lifecycle.py`、`docs/research/knowledge-revocation-qualification.md`；修改知识 API/迁移、Runtime 插件、`apps/web/src/components/RhsPanel.tsx`、`packages/api-client/src/`；新增 `apps/web/tests/KnowledgeLifecycle.test.tsx`。

**接口：** `POST /api/v1/knowledge/{id}/versions/{version}/withdraw` 含 `expected_status_version: int`、`idempotency_key: str`、非敏感撤回原因；Actor 从 BFF 得出。`KnowledgeUsage` 仅记录知识 id/version/digest、runtime/session/correlation 引用，不保存回答正文。`requires_context_reset(used: set[tuple[str, int]], revoked: set[tuple[str, int]]) -> bool`；`AnswerGuard` 在实际发送边界核验使用版本集合、当前成员/来源/目标授权和输出目标。

- [ ] 写并运行旧会话污染测试：

```python
from hikmah.services.knowledge_revocation import requires_context_reset

def test_old_session_cannot_reuse_withdrawn_version() -> None:
    assert requires_context_reset({("k1", 2)}, {("k1", 2)})
    assert not requires_context_reset({("k1", 3)}, {("k1", 2)})
```

- [ ] `uv run pytest apps/api/tests/test_knowledge_revocation.py -v` 先失败，再实现集合相交判断。该函数是筛选受影响上下文的工具，不是撤回完成证明；无法取得完整 usage/投影清单时，停用相关席位上下文并整体重建。
- [ ] 撤回事务先改变权威状态/授权版本并写审计；所有查询立即拒绝被撤回版本。清除派生检索缓存和索引，停止受影响生成，重建相关旧 session/自动记忆。若上游公开能力不能可靠删除污染记忆，则暂停 Runtime，创建空白且受控的新 session/投影；确认无旧内容后再恢复，不要求私有改库。
- [ ] 给每次生成建立使用版本清单及 scope revision；发送前以权威状态复核，缺失清单、依赖失效、权限改变均阻断。确认 QwenPaw 公开发送路径能在任何内容离开受控环境前执行该检查；若不能，关闭该知识回答能力并提交公开扩展决策，不能只检查模型最终输出后声称已经阻止流式泄漏。
- [ ] 首批受治理知识回答采用发送前缓冲最终答案；流式用户体验只可在逐段授权及撤回测试通过后开放。每次实际发送前检查与本地撤回事务协调；记录检查完成、外部请求开始/返回的时间及知识版本。外部权限改变与外部已在途请求不具有分布式原子性：已发出的内容标记潜在暴露，由获准人按 Foundation 更正/删除流程处理，停止后续发送。
- [ ] 增加可控 barrier 测试：检索后撤回、生成中撤回、准备发送前撤回均为零 Post；请求已发出后才撤回不谎称零披露，须记录该竞态且无后续 Post；源权限收窄、成员移除、旧缓存/旧会话续问、索引重建、恢复旧备份均保持禁止。异常时不得用“知识服务不可用”触发全历史 fallback。
- [ ] RHS 完成提议→预览正文/来源/受众/敏感级别→人类确认→版本链接→撤回；重复点击使用相同幂等键，内容改动显示需重新审核。未知状态显示待核验，不能显示发布成功。只显示授权范围内的引用、审计和列表计数，Web/Desktop 实际验证，移动端退化为安全文本。
- [ ] 运行 `uv run pytest apps/api/tests/test_knowledge_revocation.py apps/api/tests/test_answer_guard.py -v`、`pnpm --dir apps/web test`，再在隔离目标执行 `uv run pytest tests/e2e/test_knowledge_lifecycle.py -v`。完成一次含 withdrawn 版本的独立备份恢复、重建投影后再次验证拒绝。
- [ ] 提交 `feat: withdraw knowledge across retrieval and answer delivery`；报告区分“新检索阻断”“旧上下文清除”“发送前阻断”“已外发竞态”。任何一项缺乏证据都不开放真实知识。

## P1-04：真实任务基线和试点决策

**文件：** 新增 `evals/knowledge-pilot/schema.json`、`synthetic-sample.jsonl`、`scorecard.py`、`test_scorecard.py`、`README.md`；新增 `docs/research/knowledge-pilot-baseline.md`。真实问题/答案/来源只保存在获准的仓库外路径，仓库样例严格合成。

**输入契约：** 每任务字段 `task_id`、`category: Literal["knowledge_qa", "solution_collaboration"]`、受控 `source_ref`、`target_scope_ref`、`expected_outcome_ref`、`rubric_version`、`bom_ref`、`adopted: bool`、`usable: bool`、`attempts_cost: list[Decimal]`、`rework_minutes`、`baseline_minutes`、引用存在/有效/支持断言/受众适用的计数、失败原因。成本币种、计价时点和估算/实账区别必须在 report metadata 中固定。

**输出契约：** 分类别及合计报告通过数/总数、四种引用分项、无答案表现、返工分钟分布、所有尝试总成本、采纳数和每采纳成本；缺失值/无法计价单列。`cost_per_adoption(costs: list[Decimal], adopted_count: int) -> Decimal | None`；采纳数为零返回 None，不返回零。

- [ ] 写成本边界测试并确认初次缺失函数失败：

```python
from decimal import Decimal
from scorecard import cost_per_adoption

def test_failed_attempts_count_and_zero_adoption_is_not_zero_cost() -> None:
    costs = [Decimal("1.20"), Decimal("0.80")]
    assert cost_per_adoption(costs, 1) == Decimal("2.00")
    assert cost_per_adoption(costs, 0) is None
```

- [ ] 用 `uv run pytest evals/knowledge-pilot/test_scorecard.py -v` 先失败，再实现 Decimal 求和/除法及负成本、负采纳数拒绝；不要把缺失成本默认为零。测评脚本只做固定口径汇总，不自建评分 Agent 或通用评测平台。
- [ ] 真实任务开始前由负责人冻结至少 30 个任务及分布、评分 rubric、目标受众和模型/BOM。建议先 15 个知识问答、15 个方案协作，覆盖无答案、冲突和过期证据；此分布是实施建议，执行时可由负责人调整并记录，不能看完结果再换样本。
- [ ] 固定正确性、完整性、可行动性评分和采纳定义；让有资格的人复核每个引用是否支持具体断言。记录原流程同类任务的操作时间和资料条件，若不能配对比较，报告描述性差异，不称因果提效；运行顺序和学习效应一起记录。
- [ ] 明确实际试点团队、授权资料、成本上限、模型提供方和运维负责人后，才进行运行。所有尝试含失败/人工重试计入成本；不因答案不好只保留成功样本，不把真实内容写入 Trace 或公开报告。
- [ ] 执行各任务并汇总，样例命令的参数读取仓库外路径，入口应拒绝仓库内真实数据：

```bash
python3 evals/knowledge-pilot/scorecard.py --input-file "$PILOT_RESULTS_FILE" --output-file "$PILOT_REPORT_FILE"
```

`PILOT_RESULTS_FILE`/`PILOT_REPORT_FILE` 是操作者预先设置的受控绝对路径，不包含凭据。脚本拒绝输入覆盖及意外向仓库写出真实明细；只将脱敏摘要写入研究报告。

- [ ] 完整运行越权、误提及、重放、撤回和循环禁止用例；一项安全失败就停止相关能力，业务平均收益不得抵消。记录每个未运行项；30 个任务仅为首批学习样本，不宣称统计充分或市场需求已验证。
- [ ] 提交 `docs: record knowledge pilot baseline and expansion decision`。负责人根据效果、返工、成本和运维负担选择继续/缩小/扩大，并写明理由；未有真实报告时不填数值、不标记通过。只有明确批准扩大且安全门禁全通过才开放 Pilot 2。

## 跨任务验收和回退

P1-01 的规范对象/版本为 P1-02、P1-03 唯一知识状态来源；审批和撤回复用 P0 Actor 与原子写入。P1-04 只在 P1-03 实际知识生命周期资格通过后进入真实团队。回退为停用知识工具/回答、保留原生聊天及全部规范对象；不恢复已经撤回的旧索引，不删除审阅与撤回审计。跟踪 AR-011/012 与 CR-013/014 时标记各自已验证范围，不能提前关闭完整 MVP 剩余要求。
