---
title: Hikmah PRD 与技术架构方案审查跟踪表
description: 跟踪 PRD、架构决策、研究结论与代码脚手架之间尚未闭环的设计、证据和验收问题。
document_type: design-record
status: active
created: 2026-08-28
updated: 2026-09-05
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - product
  - architecture
  - review
  - governance
canonical: true
related:
  - ../../README.md
  - ../product/overview.md
  - ../architecture/README.md
  - ../decisions/0002-collaboration-foundation-spike.md
  - ../decisions/0003-adopt-mattermost-as-collaboration-foundation.md
  - ../decisions/0007-knowledge-collaboration-pilot-and-runtime-boundaries.md
  - ../research/2026-09-05-knowledge-collaboration-feasibility.md
  - ../research/2026-08-28-mattermost-zulip-webui-integration.md
---

# Hikmah PRD 与技术架构方案审查跟踪表

> 审查基线：Git commit `0d45229`，2026-08-28。
> 当前定位：仓库中的 API、Web、服务适配器、数据模型和测试均按**架构脚手架**理解，不代表生产实现、真实联调或安全验收已经完成。
>
> 2026-09-05 增量复核：Hikmah `8ea48c2`，QwenPaw `v2.2.0-beta.1`；本轮仅文档、源码核验和函数级实验。用户批准 ADR-0007 的试点方案，新增 AR-009～AR-012；不把设计批准升级为运行验证。

## 1. 目的与边界

本文是本轮 PRD、设计和技术架构审查的唯一问题跟踪入口。它记录目标架构、正式文档、研究证据与现有脚手架之间的差异，并为后续决策和验证定义关闭条件。

- 本文不授权代码实现、部署、外部联调、许可证判断或生产变更；这些工作必须另行批准。
- 脚手架缺少生产能力本身不视为代码缺陷；只有当文档把未验证能力表述为已完成，或脚手架体现的契约与目标设计冲突时，才形成跟踪项。
- 构建通过、单元测试通过、存在接口类或 UI 组件，只能证明脚手架具备局部静态完整性，不能替代跨系统运行证据。
- ADR 的 `Accepted` 表示选择已被接受，不自动表示运行态 Spike、隐私隔离、升级兼容或许可证门禁已经通过。
- 正式文档终态已通过 ADR-0004～ADR-0006、目标版本基线和产品规范完成归一化；设计闭环与运行证据仍使用不同状态，不能相互替代。

## 2. 状态与优先级

| 状态 | 含义 |
|---|---|
| `open` | 差异已确认，尚未形成完整设计或证据要求 |
| `decision-needed` | 需要产品或架构负责人明确选择并更新事实源 |
| `evidence-needed` | 目标设计基本明确，但缺少可复现验证或外部复核证据 |
| `design-resolved` | 文档与决策已经闭环；若涉及实现，运行验证仍可单独待办 |
| `validated` | 要求的运行、测试、升级或合规证据已经归档并复核 |
| `deferred` | 经负责人明确接受风险后延期，并记录复核日期和触发条件 |
| `not-authorized` | 仅记录未来可能需要的代码工作，本次未授权且不得实施 |

优先级不表示立即编码：`P0` 阻止宣称架构或关键门禁已验证；`P1` 应在相关交付切片进入实现前解决；`P2` 应在发布或运维承诺前解决。

## 3. 跟踪总览

| ID | 主题 | 问题性质 | 优先级 | 当前状态 | 阻断的声明或阶段 |
|---|---|---|---|---|---|
| AR-001 | Mattermost 选型决议与 Spike 证据脱节 | 决策/证据 | P0 | `evidence-needed` | “Foundation 已完成运行验证” |
| AR-002 | 身份、授权与 Personal Agent 隔离契约 | 安全/领域设计 | P0 | `design-resolved` | 实现仍需独立授权与安全验证 |
| AR-003 | Mattermost/QwenPaw/AgentScope 适配契约与失败语义 | 集成契约 | P0 | `design-resolved` | 实现仍需独立授权与契约验证 |
| AR-004 | Mattermost Plugin 与 AgentScope 纵向链路缺少可部署验证 | 交付/证据 | P0 | `evidence-needed` | “Web App Plugin 或 Sidecar 已可运行” |
| AR-005 | Coordinator 路由终态判定表 | 产品行为 | P1 | `design-resolved` | Sidecar 实现与验收用例 |
| AR-006 | 持久化、迁移、测试隔离与恢复终态 | 数据架构 | P1 | `design-resolved` | 实现仍需独立授权与恢复验证 |
| AR-007 | 版本基线、许可证与品牌结论缺少统一证据 | 依赖/合规 | P0 | `evidence-needed` | 对外版本兼容与分发合规声明 |
| AR-008 | NFR 与运行验收指标 | 质量属性 | P1 | `design-resolved` | 测量证据仍由 release qualification 产生 |
| AR-009 | 共享 Runtime 隔离与托管隐私边界 | 安全/证据 | P0 | `evidence-needed` | 真实频道数据与后续 Personal Agent 开放 |
| AR-010 | 专家请求准入、准确提及与循环预算 | 集成/证据 | P0 | `evidence-needed` | 专家直达及有限自动协作开放 |
| AR-011 | 知识受众、引用与撤回传播 | 数据/证据 | P0 | `evidence-needed` | Pilot 1 知识发布与受控回答 |
| AR-012 | 知识协作试点效果与阶段资格 | 产品/证据 | P1 | `evidence-needed` | 扩大试点及价值结论 |

## 4. 详细跟踪项

### AR-001：Mattermost 选型决议与 Spike 证据脱节

**已确认事实**

- [ADR-0002](../decisions/0002-collaboration-foundation-spike.md) 要求在选型前完成统一场景、硬门禁和可复现输出。
- [ADR-0003](../decisions/0003-adopt-mattermost-as-collaboration-foundation.md) 已接受 Mattermost 为目标协作底座。
- [产品规范](../product/overview.md)的验证体系与第 17 节阶段资格、[WebUI 整合调研](../research/2026-08-28-mattermost-zulip-webui-integration.md)仍把真实垂直 Spike 作为待执行门禁。
- 当前仓库未归档一套覆盖 ADR-0002 Required scenarios、Hard gates 和 Output 的可复现运行证据。

**终态决议与待证事项**

1. ADR-0003 的终态语义是“战略选型已接受”，不表示 ADR-0002 的运行门禁已经通过。
2. 仍须执行 Spike，或由决策者用新的风险接受记录明确说明哪些门禁被豁免、为何可接受、何时复核。
3. Spike 环境、固定版本、脚本、结果、失败项、升级过程和退出路径须归档到 `docs/research/` 下的稳定位置或引用不可变外部证据。

**关闭条件**

- 所有 Required scenarios 和 Hard gates 均有逐项证据，或存在明确批准的偏差记录；
- 根 README、文档中心、架构导航、产品规范和 ADR 索引对“已选型”与“已验证”的用词一致；
- 未执行的运行验证不再使用 `Done`、`通过`或等价完成态描述。

### AR-002：身份、授权与 Personal Agent 隔离契约未闭环

**已确认事实**

- [产品规范](../product/overview.md)要求身份由 Foundation 权威执行，Personal Agent 为 Owner-only，且不能作为共享 Channel 成员。
- API 脚手架尚无统一的已认证 Actor 与角色依赖；[`seats.py`](../../apps/api/src/hikmah/api/v1/seats.py)接受可选 `user_id` 查询参数，[`knowledge.py`](../../apps/api/src/hikmah/api/v1/knowledge.py)从请求体取得审阅者身份。
- [`ExpertSeat`](../../apps/api/src/hikmah/models/seat.py)同时承载共享席位和 Personal Agent，并包含 Mattermost 用户映射；[`seat.py` schema](../../apps/api/src/hikmah/schemas/seat.py)还把 `runtime_config` 放入通用契约。

以上是脚手架与目标边界的差异，不认定为已发布漏洞；但在进入真实用户实现前必须先完成设计闭环。

**终态决议**

1. [ADR-0004](../decisions/0004-trusted-identity-and-personal-agent-isolation.md)已接受 Mattermost OAuth/BFF、服务端 `AuthenticatedActor`、角色矩阵与服务身份传播。
2. Shared Expert Seat 与 Personal Agent Binding 是独立领域/API 契约；Personal Agent 不注册公共 Mattermost Bot。
3. Secret 使用服务端受控存储与 allowlist 响应，不进入普通 API、帖子 props 或 Correlation 正文。
4. 越权、分享、撤销、治理角色误读和跨 Channel 用例是 release security gate。

2026-09-05 复核补充：ADR-0004/0007 已明确产品治理角色与基础设施运维角色的区别，托管 owner-only 不承诺防主机管理员读取。运行隔离证据单独由 AR-009 跟踪，原 `design-resolved` 不表示这一安全边界已通过。

**关闭条件**

- 设计关闭：已由 ADR-0004 与产品规范完成，状态为 `design-resolved`；
- 交付关闭：未来实施必须由权威 ACL、QwenPaw owner/tenant 隔离和自动化安全用例证明；
- 对应代码记录：CR-001、CR-002、CR-010，均保持 `not-authorized`。

### AR-003：适配契约与失败语义未固化

**已确认事实**

- [`runtime.py`](../../apps/api/src/hikmah/services/runtime.py)使用暂定的 QwenPaw `/api/v1/agents/{agent_id}/run` JSON 调用，并在异常时返回 `completed` 模拟结果。
- 当前只读参考基线 `../QwenPaw` 的 `v2.2.0-beta.1` Console API 使用 `/api/console/chat`、`X-Agent-Id` 和 SSE；二者不是同一已验证契约。
- [`foundation.py`](../../apps/api/src/hikmah/services/foundation.py)在无 Token 时返回成功形态的模拟状态或消息。
- AgentScope 在当前代码中只有模型枚举和设计语义，没有生产事件入口或已固定的公开 API 映射。

**终态决议**

1. [ADR-0005](../decisions/0005-public-integration-contracts-and-fail-closed-semantics.md)已固定 Mattermost、QwenPaw、AgentScope、Plugin 与 Hikmah REST 的公开边界。
2. [目标版本基线](../architecture/version-baseline.md)统一维护版本与发布 BOM 语义。
3. `unconfigured`、`degraded`、`unreachable`、`verification_required` 等状态与 `ready/completed` 互斥；隐式 mock success 被正式禁止。

**关闭条件**

- 设计关闭：已由 ADR-0005、版本基线和产品规范完成，状态为 `design-resolved`；
- 交付关闭：未来联调证据覆盖流式响应、取消、错误、重试、状态未知和 correlation 传播；
- 对应代码记录：CR-003、CR-004、CR-006、CR-010，均保持 `not-authorized`。

### AR-004：Mattermost Plugin 与 AgentScope 纵向链路缺少可部署验证

**已确认事实**

- [`plugin.tsx`](../../apps/web/src/plugin.tsx)包含注册脚手架，但当前 [`vite.config.ts`](../../apps/web/vite.config.ts)构建的是以 `main.tsx` 为入口的独立 SPA。
- `apps/web` 当前没有 Mattermost 插件 manifest、插件包结构或安装验证证据。
- 当前没有从 Mattermost 真实事件进入 AgentScope Sidecar、再到 QwenPaw 专家并回写同一 Thread 的生产链路。

**终态交付形态与待证事项**

1. 垂直 Spike 必须覆盖插件安装、事件接收、显式 @直达、Sidecar 静默、未 @单主答、流式回帖和 Correlation 关联。
2. 生产交付物固定为 Mattermost Web App Plugin；独立治理控制台仅保留开发/演示用途，不构成第二个生产聊天入口。
3. 记录插件安装/卸载、升级、失败回退和无核心补丁验证。

正式交付形态与失败语义已由 ADR-0005 解决；本项只剩可部署包和真实纵向链路证据，因此保持 `evidence-needed`。

**关闭条件**

- 有可复现插件包和固定 Mattermost 版本的安装证据；
- 一条真实端到端链路按验收脚本通过，并保留失败与回退证据；
- 在此之前，文档只能称其为目标架构或脚手架。

### AR-005：Coordinator 路由规则缺少可执行判定表

**已确认事实**

- 产品已规定：显式 @时 Sidecar 100% 静默；未 @时先过协作意图门控，最多选择一名主答。
- [`coordinator.py`](../../apps/api/src/hikmah/services/coordinator.py)已实现显式 @静默骨架，但暂不使用消息内容；默认席位、置信度阈值、Channel 资格、循环抑制和去重规则尚未按已批准终态契约实现。

**终态决议**

1. [产品规范 9.3](../product/overview.md)已定义重复事件、Agent loop、显式 @、闲聊、单候选、默认专家、低置信度与无候选的有序判定表。
2. 自动路由每个原始事件最多一名主答、两名一层补充专家；低于阈值只问一个澄清问题。人类显式 @多名专家按原目标执行，不被单主答预算改写，且不自动追加邀请。
3. 理由码、不变量、资格检查与循环预算构成实现无关的验收输入。

2026-09-05 复核补充：产品规范已补齐多候选唯一高匹配、并列、仅 @人类、无法判定和已关联 Agent 事件分支；原生 Channel 函数级实验与目标专家入口预算的待证项见 AR-010。

**关闭条件**

- 设计关闭：产品规范已包含路由真值表、理由码和不变量，状态为 `design-resolved`；
- 交付关闭：未来实现用固定 Given/When/Then 向量证明显式 @零介入、普通聊天零触发和单主答；
- 对应代码记录：CR-007、CR-010，均保持 `not-authorized`。

### AR-006：持久化、迁移、测试隔离与恢复边界未决

**已确认事实**

- [`infra/docker-compose.yml`](../../infra/docker-compose.yml)为 Hikmah API 配置容器内 SQLite，未声明对应持久卷；PostgreSQL 服务当前主要供 Mattermost 使用。
- 项目声明 Alembic 依赖，但当前没有迁移配置或版本目录。
- [`conftest.py`](../../apps/api/tests/conftest.py)复用应用全局 Engine，并在测试前后创建/删除全部表；若测试环境变量配置错误，可能触碰非测试数据库。

**终态决议**

1. [ADR-0006](../decisions/0006-governance-metadata-persistence-and-schema-lifecycle.md)已接受生产/资格环境 PostgreSQL 16 独立 database/role 与 Alembic。
2. SQLite 仅限隔离本地开发/单元测试；集成/E2E 使用临时 PostgreSQL。
3. 数据最小化、保留、expand/migrate/contract、测试误连保护、RPO/RTO 和恢复演练均已规范化。

**关闭条件**

- 设计关闭：已由 ADR-0006 与产品部署/NFR 规范完成，状态为 `design-resolved`；
- 交付关闭：未来实现提供迁移、备份/恢复和测试隔离证据；
- 对应代码记录：CR-008、CR-010，均保持 `not-authorized`。

### AR-007：版本基线、许可证与品牌结论缺少统一证据

**已确认事实**

- 正式目标基线采用 React `19.2.x`、TypeScript `6.0.x`、Vite `8.x`；当前 Web/API Client 脚手架 manifest 仍包含 TypeScript 5.7 和 Vite 6 的依赖范围。
- 本地只读参考仓库固定在 Mattermost `v11.10.1`、mattermost-plugin-agents `v2.6.0`、QwenPaw `v2.2.0-beta.1`、AgentScope `v2.0.7.post1`；正式版本口径已统一到目标版本基线，脚手架依赖仍待未来授权任务对齐。
- [ADR-0003](../decisions/0003-adopt-mattermost-as-collaboration-foundation.md)含有确定性的许可证与分发兼容表述，但现有材料同时声明许可证/品牌仍需专门复核；工程调研不能替代法律意见。

**终态决议与待证事项**

1. [目标版本基线](../architecture/version-baseline.md)已定义目标、已验证、支持和参考版本语义，以及唯一 release BOM。
2. 正式入口已把目标版本与脚手架解析版本分开；未经验证不得把版本组合标记为 `validated` / `supported`，也不得作法律合规结论。
3. Mattermost/QwenPaw/AgentScope 升级、回退、SBOM 和供应链门禁已规范化。
4. 目标分发模式的许可证/品牌复核和实际升级证据尚未产生，因此本项保持 `evidence-needed`。

**关闭条件**

- 文档、manifest、锁文件和参考仓库使用同一版本口径；
- 许可证/品牌结论有明确审查者、适用分发模式、日期和未决限制；
- 完成目标版本组合的升级与回退验证后，方可将该组合标记为 `validated`；满足支持窗口、回归门禁和责任人要求后，方可标记为 `supported`。

### AR-008：NFR 与运行验收缺少可测量指标

**已确认事实**

- [产品规范](../product/overview.md)描述了可靠性、降级、安全和可观测原则，但没有为关键旅程给出统一的量化目标和测量方法。
- 当前健康检查、单元测试和构建结果不能证明 3–20 人团队规模下的延迟、容量、恢复、审计完整性或隐私隔离。

**终态决议**

1. [产品规范 14.1](../product/overview.md)已定义容量、API/路由延迟、状态可见性、可用性、幂等/循环、审计、隐私和恢复指标。
2. 每份报告必须记录 BOM、环境、数据集、并发、样本量、百分位和偏差。
3. 没有测量报告时禁止 production-ready/high-performance 声明。

**关闭条件**

- 设计关闭：产品事实源已包含指标、方法和阈值，状态为 `design-resolved`；
- 交付关闭：未来 Spike/release 报告逐项提供测量证据；
- 对应代码记录：CR-010 保持 `not-authorized`。

### AR-009：共享 Runtime 隔离与托管隐私边界

**证据与决议**

- [本轮核验报告](../research/2026-09-05-knowledge-collaboration-feasibility.md)记录 QwenPaw 共享实例信任模型、Workspace 长期记忆及 Hub 运维可见性；它们不构成按用户/频道隔离已验证的证据。
- ADR-0004/0007 和产品规范第 8 节要求试点每席位单 Channel，隔离配置、数据、凭据及执行环境，区分产品 owner-only 与可信基础设施管理员。

**关闭条件**

- Pilot 1 前证明不同频道的文件、自动记忆、检索、工具和凭据不能交叉访问，覆盖成员移除与权限收窄；明确哪些同频道成员共享哪些业务能力；
- 后续 Personal Agent 阶段分别证明产品角色授权、本机/托管数据路径及日志/备份边界；明确可信运维方，不宣称未实现的防运维读取；
- 记录环境、BOM、用例、结果、失败项和复核人；部分阶段通过不能提前关闭剩余范围。

状态为 `evidence-needed`；对应 CR-011。

### AR-010：专家请求准入、准确提及与循环预算

**证据与决议**

- 原始 `_is_triggered` 的六个函数级输入中，其他 Bot 提及、用户名子串和代码示例均可触发；不能据此断言完整链路已执行或已形成循环。
- 公开 `register_runtime_hook`、`PRE_DISPATCH` 和短路语义已由源码核验，但 Hook 位于 Channel 取上下文之后。
- ADR-0005/0007 采用原生 Channel + 待验证准入扩展方向，完整规则在产品规范第 9 节。

**关闭条件**

- 真实人类精确提及仅唤醒指定专家；用户名碰撞、引用/代码示例、伪造角色和 correlation 不取得调用资格；
- 专家入口核验权威 Post、发送者、Channel 与预算；去重/预算原子占用覆盖并发、重放、重启和迟到事件；
- Hook 未注册、故障、超时、重载时不能进入未治理执行；覆盖命令、Console、后台及实际开放的所有入口；
- 分别验证前置读取隔离和 Hook 短路输出；Sidecar 停止时显式 @仍可通过独立准入路径工作；
- 自动路由最多一名主答、两名一层补充专家；人类显式多专家目标不被改写，补充专家不能递归邀请。

Pilot 1 前验证准确提及、独立准入和受控回帖；自动邀请部分在 Pilot 2 开放前完成。未完成全范围前维持 `evidence-needed`；对应 CR-012，并补充 CR-006/007/010。

### AR-011：知识受众、引用与撤回传播

**证据与决议**

- 产品规范第 11 节与 ADR-0006/0007 已要求权威知识版本、受众授权、来源溯源、撤回传播和外部已披露内容边界。
- 本轮没有检索、缓存、会话或真实发帖实验，不能标记已验证。

**关闭条件**

- 证明知识发布者有来源处理与目标发布权限，频道答案不泄漏仅提问者可见的内容、链接或标题；
- 引用可定位有效知识版本，能够支持对应断言；区分模型推断，证据不足可见；
- 覆盖生成途中撤回、范围收窄、成员变化、旧会话续问、缓存和自动记忆残留；无法确认状态时停止相关输出；
- 记录检查与外部发送的竞态处理及限制，不能宣称已发送内容可原子撤回；
- 规范对象与重建投影的迁移/恢复后仍保持撤回和权限状态。

这是 Pilot 1 开放知识发布的必要条件；状态为 `evidence-needed`，对应 CR-013。

### AR-012：知识协作试点效果与阶段资格

**决议与待证事项**

- 用户于 2026-09-05 选择知识问答与方案协作，并批准方案 A 的文档更新；批准记录见[设计修订记录](../design/approval-record.md)。
- 产品规范第 17 节定义 Pilot 0/1/2、后续独立能力及完整发布资格；原 Slice 0～4 能力保留，最小知识闭环提前。
- 至少 30 个真实任务的可用率、引用准确性、人工返工和每个采纳答案成本尚未测量。

**关闭条件**

- 评估前固定任务分布、来源、目标受众、评分和 BOM；评估材料经授权且受控；
- 归档逐项结果、样本量、失败/重试成本、无采纳情况和原有流程对照；由产品负责人记录扩大或停止试点的依据；
- 实际开放能力的安全、数据恢复、插件与目标使用方式的许可证/品牌门禁通过；未开放能力明确保持关闭；
- 完整 MVP 仍逐项满足第 2.3/14.1/16 节，不能用局部试点或单元测试代替。

状态为 `evidence-needed`；对应 CR-014。该条的批准不授权执行真实评估或部署。

## 5. 未来代码变更记录（本次不实施）

下表只把审查中暴露的潜在代码工作持久化，防止后续遗漏。对应终态设计已经由产品规范和 Accepted ADR 批准，但本表不是实施计划，也不授权修改列出的文件。每项仍须满足所列证据或执行条件，并由独立任务明确授权后方可实施。

| 记录 ID | 来源 | 可能涉及的代码范围 | 预期目标 | 实施前置条件 | 执行状态 |
|---|---|---|---|---|---|
| CR-001 | AR-002 | `apps/api/src/hikmah/api/v1/`、`core/`、API tests | 引入可信 `AuthenticatedActor`/等价身份依赖和集中授权；删除查询参数或请求体中的自报身份 | ADR-0004 已接受；须由独立实现任务授权 | `not-authorized` |
| CR-002 | AR-002 | `models/seat.py`、`schemas/seat.py`、Seats API、API Client、Web | 将 Shared Expert Seat 与 Personal Agent Binding 的领域/API 边界分开；敏感 `runtime_config` 不进入普通读取响应 | ADR-0004 已接受；须由独立实现任务授权并补安全回归 | `not-authorized` |
| CR-003 | AR-003 | `services/runtime.py`、配置、Runtime tests | 按固定 QwenPaw 版本实现认证、SSE、取消和错误映射；模拟器改为显式测试替身，禁止异常回落为 `completed` | ADR-0005 已接受；须由独立实现任务授权并固定验证矩阵 | `not-authorized` |
| CR-004 | AR-003 | `services/foundation.py`、Health API、配置、tests | Mattermost 未配置、不可达、降级和成功使用互斥状态；消息发送失败不得返回成功形态 | ADR-0005 已接受；须由独立实现任务授权并完成连接验证 | `not-authorized` |
| CR-005 | AR-004 | `apps/web/vite.config.ts`、`src/plugin.tsx`、未来 manifest/打包配置 | 生成可安装 Mattermost Web App Plugin 包；明确独立 SPA 与 Plugin 的双构建或单构建策略 | ADR-0003/0005 与版本基线已确定；须由独立实现任务授权并取得安装证据 | `not-authorized` |
| CR-006 | AR-003、AR-004 | API service/event modules、AgentScope adapter、integration tests | 建立 Mattermost event → AgentScope Sidecar → QwenPaw → 同 Thread 回写及 Correlation 传播链路 | 事件、幂等与失败契约已确定；须由独立垂直 Spike 任务授权 | `not-authorized` |
| CR-007 | AR-005 | `services/coordinator.py`、规则模型、Coordinator tests | 实现协作意图门控、Channel 资格、阈值、默认席位校验、去重、迟到事件和循环抑制 | 产品规范判定表与理由码已确定；须由独立实现任务授权 | `not-authorized` |
| CR-008 | AR-006 | `models/base.py`、`tests/conftest.py`、`infra/`、未来 Alembic 文件 | 隔离测试数据库，引入迁移生命周期和持久化部署；禁止测试误连非测试库 | ADR-0006 已接受；须由独立实现任务授权并提供目标环境 | `not-authorized` |
| CR-009 | AR-007 | Python/Node manifests、lockfile、容器镜像和 CI | 将解析依赖与批准 BOM 对齐，增加版本/许可证/SBOM/兼容性检查 | 目标 BOM 已确定；须先完成许可证/品牌复核，再由独立任务授权 | `not-authorized` |
| CR-010 | AR-002、AR-004、AR-008 | API/Web/integration/e2e/security tests、CI | 增加隐私越权、契约、端到端、升级、恢复和量化 NFR 门禁 | 安全/NFR 终态已确定；须由独立验证任务授权并建立可重复环境 | `not-authorized` |
| CR-011 | AR-009 | 未来 Runtime 部署/凭据/记忆配置与隔离测试 | 按频道信任域隔离共享专家，证明文件/工具/检索边界；明确托管隐私范围 | ADR-0004/0007 已接受；需独立任务授权与隔离环境 | `not-authorized` |
| CR-012 | AR-010 | 未来 QwenPaw 公开插件、准入与契约测试 | 验证 PRE_DISPATCH 准入、真实 Post 核验、准确提及、并发预算及故障拒绝 | ADR-0005/0007 已接受；需独立 Spike 授权，公开扩展不足时另行决策 | `not-authorized` |
| CR-013 | AR-011 | Knowledge API/models、Runtime 投影、API Client/Web 与测试 | 受众授权、版本引用、发送前复核、缓存/会话撤回与恢复验证 | ADR-0006/0007 已接受；需独立实现任务授权 | `not-authorized` |
| CR-014 | AR-012 | 未来试点评估资料、契约/E2E 验证与报告 | 建立至少 30 个真实任务基准，记录质量、返工、成本和能力开放证据 | 需独立评估授权、数据使用许可及已通过的相关安全门禁 | `not-authorized` |

若未来批准其中一项，应创建独立 Issue/计划并关联对应 `AR-*` 与 `CR-*`；不得直接把本表状态改为 `validated` 作为实现证据。

## 6. 文档处理顺序

建议只按文档与证据依赖推进，不代表代码排期：

1. 先处理 AR-001 与 AR-007，统一“已选型、已验证、可分发”的状态口径。
2. 再处理 AR-002 与 AR-005，冻结安全边界和用户可观察行为。
3. 随后处理 AR-003 与 AR-006，冻结集成契约和数据生命周期。
4. 最后用 AR-004 与 AR-008 定义纵向 Spike 和运行验收方法。

任何条目状态变化时，应在同一文档变更中补充证据链接、复核人、复核日期和剩余风险；不得仅修改状态单元格。
