---
title: Hikmah 接收、任务与决策记录协议
description: 规定可复制的接收检查、任务评审和技术决策字段及示例，保留清晰的未授权和待签收状态。
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
  - evidence
canonical: true
related:
  - README.md
  - successor-runbook.md
  - decision-register.md
  - ../../development/worker-delivery-protocol.md
---

# Hikmah 接收、任务与决策记录协议

接续团队在正常 Issue/PR 和仓库 Markdown 中留存可复核记录；不依赖本会话，也不新建通用工作流服务。以下是记录的填写协议，字段值必须由实际执行或有权人员提供，不能复制示例为真实批准。

## 1. 接收记录

接收者在本目录新增 `receipt.md`，遵循项目 Markdown metadata，状态先为 review。正文逐项填写下表；没有执行的条目保持未勾选并附原因。

| 项目 | 接收者必须留下的结果 |
|---|---|
| 制品 | 收到的 bundle SHA-256、delivery.json、导入后 commit 和前置 commit |
| 完整性 | 两条交接检查命令的实际输出、时间和使用的 Python 版本 |
| 事实复述 | 当前阶段、产品完成范围、45 项状态和未验证门禁；不能仅写“已了解” |
| 设计资产 | 用户 HTML 副本哈希、归属人与后续处理决定；未确认则继续保留 |
| 角色 | 产品负责人、技术负责人、reviewer，运行任务开始前再明确 operator；填写有权指定的人或团队，不写离任顾问 |
| 第一动作 | P0-01.A 的卡片、实际基线、工具链、实施授权或继续等待授权的理由 |
| 风险 | D-01～D-08 的接管人/角色，不能以顾问离任为阻塞原因 |
| 接收结论 | received / received_with_open_items / not_received，列出未接收项及解决人 |

仓库中的 `state.json` 初始 `receiving_roles` 为空、`receipt.status` 为 pending。接收者完成检查后更新角色与 receipt 引用、日期和结论；顾问交付者不能代为签收。接收不自动批准任何产品实施、部署或数据访问。

## 2. 任务证据记录

新增记录路径建议 `docs/development/evidence/P0-01.A.md`；创建时先添加正式 metadata。该记录的主体使用以下固定顺序，便于弱上下文执行者和评审人核对：

1. **Identity：** task id、实际起点 commit、交付 commit、Issue/PR、执行人及 reviewer。
2. **Authorization：** 有权人员明确允许的任务和动作、原始批准引用、允许环境/数据；没有批准时记 not_authorized。
3. **Contract：** 本卡消费/产生的接口与规则版本；任何与卡片不一致的地方单列，不默认为改设计已批准。
4. **Scope：** 实际读写文件和原因、未提交用户改动的保留情况。
5. **Red：** 测试命令、失败断言及证明的缺失行为；环境失败不能冒充行为失败。
6. **Green：** 实际通过的断言、完整脱敏输出引用、执行环境/时间；原始真实内容不得进入记录。
7. **Limits：** mock、契约、E2E、未运行与未知项分别列出，结果只覆盖对应范围。
8. **Rollback：** 本卡可回退制品与持久数据边界。
9. **Review：** 评审人复核内容、结论和日期。未复核保持 in_review。

只有 reviewer 复核后才在 state.json 设置 verified，并写 `authorization_ref`、至少一个 `evidence`、`review_ref` 的仓库相对文件路径。记录可以引用同一个包含上述完整内容的证据文件；校验器只检查引用存在，证据是否充分由 reviewer 负责。不得引用 `.env`、外部秘密路径或原始敏感日志。

**初始状态示例（真实尚未执行）：**

```json
{
  "id": "P0-01.A",
  "readiness": "specified",
  "execution": "not_authorized",
  "authorization_ref": null,
  "evidence": [],
  "review_ref": null
}
```

不要为了填满记录而创建虚假的红绿结果或用户名。当前交接资料的完整性检查成功也不能把这条状态改为 verified。

## 3. 决策记录

继任负责人处理 D-01～D-08 时，新增有日期的 research/decision 记录并链接原 D 项。保持事实、推断和决定分开，必含：

| 字段 | 具体内容 |
|---|---|
| Question | 唯一要判断的能力或边界，影响哪些后继任务 |
| Fixed inputs | 完整 commit/BOM、公开接口签名、合成数据、授权环境 |
| Hypothesis | 预期行为和可证伪条件，不能写不可检验的“安全可靠” |
| Experiment | 步骤、对照组、独立观察点、故障注入与终止方式 |
| Results | 每用例 expected/actual、pass/fail/not_run、输出引用与失败项 |
| Alternatives | 最小可行候选及各自代价；不包含违反 Accepted ADR 的默认绕过 |
| Decision | 继续/关闭/修订 ADR、适用范围、剩余风险、回退 |
| Ownership | 作出技术判断和批准范围的人、日期、下一张卡 |

需要改变产品承诺、认证/隐私/持久化边界或目标版本时，先由有权负责人批准新 ADR/基线，再修改 PRD/计划/任务卡；worker 不能通过实现结果倒逼规范变更。

## 4. 分派新卡的完整性检查

对照已提供的 P0-01.A～D，把下一条 outlined 工作项写成完整 Markdown 卡：精确标题 ID、基线、前置证据、白名单、完整类型/函数/字段、实际负向样例与 fixture、red/green 命令、输出、停止/回退和评审人。不得把本节字段清单或简短队列表当实现卡。

负责人须进行一次空会话演练：仅凭本卡及其明示输入，能否知道第一条命令、失败预期、允许改动和遇到异常的处理人；如果还需要问离任顾问一个技术问题，补入当前团队的决策记录后再分派。模型名称、工具是否有图谱或是否有 skills 都不能成为隐含前置：缺工具时按 AGENTS.md 的源码回退规则工作。

## 5. 状态维护的边界

`state.json` 与队列表的 ID/依赖/角色同步变更；准备度、执行状态、证据引用以 state.json 为准。阶段放行继续以 PRD/AR/CR 及真实资格报告为准；接收记录以 receipt.md 为准。本目录交接快照记录离任时事实，不随任务完成逐次重写历史。
