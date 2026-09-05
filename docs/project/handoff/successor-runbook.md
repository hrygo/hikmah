---
title: Hikmah 接续团队运行手册
description: 无原会话上下文时的制品接收、首轮启动、任务分派、滚动细化和异常处理操作。
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
  - operations
canonical: true
related:
  - README.md
  - decision-register.md
  - records-and-acceptance.md
  - ../../development/worker-delivery-protocol.md
  - ../../development/plans/2026-09-05-p0-01-worker-packet.md
---

# Hikmah 接续团队运行手册

本手册中的导入操作只在接收者自己的新目录或获准 checkout 执行，不改 main、不清现有工作区。只读检查可以立即完成；实施和环境操作仍遵守对应授权。

## 1. 接收可携带制品

交付目录包含：`hikmah-handoff.bundle`、`delivery.json`、`user-design-working-copy.html`。`delivery.json` 记录 bundle 的 SHA-256、交付 commit、分支、前置 commit 及设计副本哈希；它是本地制品清单，不作为发布签名或软件供应链证明。

bundle 以 `8ea48c2dc006b9ca69950e98821ed235e129a8b9` 为前置；接收仓库必须已有该 commit。没有该 commit 时，从团队授权的仓库/备份取得原始历史，不能改写前置要求。原始仓库地址和凭据通过团队已有渠道取得，不复制到本交接包。

将 `HANDOFF_DIR` 设置为收到的交付目录，在**新接收 checkout**中运行：

```bash
git status --short --branch
git cat-file -e 8ea48c2dc006b9ca69950e98821ed235e129a8b9^{commit}
git bundle verify "$HANDOFF_DIR/hikmah-handoff.bundle"
git bundle list-heads "$HANDOFF_DIR/hikmah-handoff.bundle"
```

预期：前置 commit 存在，bundle 校验成功，公布分支为 `refs/heads/docs/knowledge-collaboration-pilot`，目标 commit 与 delivery.json 一致。先核对 SHA-256；不把文件大小一致当校验。不要在含用户未提交修改的原 checkout 里切换分支。

确认接收分支名尚不存在后，以新本地分支导入；同名已存在则选择其他新名并记录，不能加 force：

```bash
git fetch "$HANDOFF_DIR/hikmah-handoff.bundle" refs/heads/docs/knowledge-collaboration-pilot:refs/heads/handoff/received-2026-09-05
git switch handoff/received-2026-09-05
git log -1 --format=%H
python3 scripts/check_handoff.py
python3 -m unittest discover -s tests/handoff -v
```

最后两条命令只依赖标准库，不导入 Hikmah app，也不触发旧 pytest conftest。校验输出应明确 `integrity_only: true`、任务数 45、初始 verified 数 0、errors 为空；人员字段为空和未授权状态是事实，不是运行错误。不能把数字 0 改成 45 来满足“交接完成”。

`user-design-working-copy.html` 不自动覆盖仓库中的设计册。由其拥有者确认内容，单独建立设计同步任务；比对来源、哈希和 PRD/ADR 后再决定是否提交。

## 2. 接续负责人首次工作会

由仓库/产品负责人确定技术负责人、评审人和需要时的操作者，填写 `state.json` 的 `receiving_roles`，并建立[接收记录](records-and-acceptance.md)。这些职责不要求离任顾问继续在线；技术负责人可以是新的资深工程师或有相应资格判断能力的团队成员，不能仅由缺少独立验收能力的 worker 自我认证。

会议只需明确五个结果：

1. 各自能够说清当前 M0 阶段、完整终态和禁止绕过的门禁。
2. 每个人知道原有用户设计修改的归属与保留位置。
3. 第一批只准备 P0-01.A～D，真实服务/数据尚未开放。
4. 负责人接管 D-01～D-08 决策，不把“询问前任顾问”写作依赖。
5. 下一轮的实施范围、reviewer、环境和授权记录明确；未明确项保持 pending。

## 3. 第一张任务卡的领取与验收

技术负责人核对 P0-01.A 的输入基线和只写两文件范围；BOM 安装不在本卡内。已有工具链可用时，仅允许独立安全测试；旧 API suite 必须等待 P0-01.C 安全接线完成。

在正式任务/Issue 中引用完整卡片、基线 commit、允许路径、期望七个断言、禁止动作和评审人。若当前授权已覆盖本卡，实现者直接执行；若只批准交接文档，保持 `not_authorized`，由有权负责人决定实施范围。

worker 的启动消息使用如下固定内容，并附上实际卡片和授权记录，不依赖本会话：

> 你负责执行 P0-01.A。先阅读 AGENTS.md、交付规范和 P0-01 任务包，只改 A 的两条白名单路径。确认起点 commit 与任务记录一致，写失败测试、运行并确认缺失行为、实现、重跑断言、按卡片完成质量检查。不要运行旧 API suite、同步依赖、启动服务或修改上游。发现边界冲突先停止并提交最小证据。你不是工作区唯一使用者，保留所有他人修改。提交本卡 diff、red/green 输出、commit、剩余问题给评审人；不要把自测成功标为最终 verified。

评审人复核保护函数被真实测试导入、六个拒绝和一个允许输入真实通过、无导入副作用、差异未越界，再记录 review。技术负责人更新状态和证据引用；只有 A verified 才细化/解锁 B，依次推进 C/D。

## 4. 其余 41 项的细化程序

当前只冻结近期可确定的实现；后续上游实验、OAuth、受众发布和发送前拦截仍需现场证据。继任技术负责人按下列固定程序将 outlined 条目变成可领取任务，而不是把一句目标交给 worker：

1. 读取该工作包、相关 ADR、决策记录及已通过前置卡，记录新的实际 commit。
2. 按公开固定版本定位符号/签名，提供精确源码或契约证据；图谱缺口回到源码，不把零 caller 当不存在。
3. 选定最小实现，写出完整类型/参数/返回值、授权主体、事务/幂等和异常边界；需要新决策时先走 D 类记录。
4. 为该条目写完整任务卡，格式和完整度对齐 P0-01；测试导入真实被测逻辑，提供 imports、fixture、合成输入、命令及负向期望。
5. 本人按“空会话阅读”复核：不需要新选组件、不出现未定义接口、不要求任意工具权限、不依赖未来文件。提交评审后置为 specified/ready。
6. 将 `state.json` 的 packet 指向新 Markdown 文件。文件须有精确 `## P0-02.A：标题` 形式的任务标题；执行只在 ready/authorized/前置 verified 时开始。

如果负责人无法冻结接口或解释安全用例，条目保持 blocked，由团队另行安排资格审查能力。资源不足是待解决的团队问题，不能通过降低验收来隐藏。

## 5. 每次交付与上下文重启

维护链路：阶段 → 工作包 → 任务卡 → 实现 PR → 验证记录 → AR/CR 对应范围。状态更新写入 `state.json`；工作队列表管理 ID/依赖/角色，两者由校验器核对。实施计划开头的“离任快照”只作历史说明，不维护第二份实时完成统计。

会话结束前提交：当前卡和 commit、工作区未提交改动归属、已执行命令/断言、未运行项、卡住的条件、下一步唯一动作。新执行者从这些记录恢复；未知外部写操作不得重试，旧评估样本和失败日志不得删去。

每 PR 运行 handoff integrity CI。CI 检查已定义，不表示远端已运行或已被分支保护设为 required；维护者依现有权限核验。产品发布仍需原有代码、契约、端到端、安全和恢复门禁。

## 6. 发现问题后的动作

| 情况 | 立即动作 | 由谁解决 |
|---|---|---|
| 校验器报缺失文件/依赖漂移 | 停止分派受影响卡，修复清单或文档引用并回归 | 技术负责人 |
| 上游签名或行为不符 | 固定 commit/输入/输出，关闭能力，执行 D-01/D-03/D-07 | 技术负责人及评审人 |
| 执行者需扩大白名单或改变接口 | 保存 diff，提出卡片修订，不临场扩展 | 技术负责人 |
| 无人具备安全/架构验收能力 | 仅做文档和合成准备，明确人员缺口 | 产品/仓库负责人 |
| 真实数据误连、权限泄漏或未知外部写 | 停止新工作、保存最小证据、依授权恢复方案处理 | 操作者及安全/技术负责人 |
| 业务价值不佳 | 保留完整失败样本，按 D-08 分析，不自动增加复杂度 | 产品负责人 |

可携带制品损坏时，从原始授权仓库和已记录提交恢复文档分支；不能凭摘要重造事实。所有方案修改和批准都在团队正常任务/PR 中记录，离任顾问不再承担运行时职责。
