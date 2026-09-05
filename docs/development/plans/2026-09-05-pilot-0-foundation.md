---
title: Pilot 0：安全基础与隔离资格实施计划
description: 先保护测试数据库，再验证公开准入扩展、隔离部署、可信身份及单专家插件纵向链路。
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
  - security
canonical: true
related:
  - 2026-09-05-implementation-roadmap.md
  - 2026-09-05-pilot-1-knowledge.md
  - ../../decisions/0007-knowledge-collaboration-pilot-and-runtime-boundaries.md
  - ../../research/2026-09-05-knowledge-collaboration-feasibility.md
  - 2026-09-05-work-item-sequence.md
  - 2026-09-05-p0-01-worker-packet.md
---

# Pilot 0：安全基础与隔离资格实施计划

> 执行者使用 `executing-plans`，默认单 Agent。所有任务未执行；只有获得对应实施授权后才修改代码或操作实验环境。

本文七项是集成工作包，按[工作项队列](2026-09-05-work-item-sequence.md)细化后分派；P0-01 使用[四张完整任务卡](2026-09-05-p0-01-worker-packet.md)。公开 Hook、认证选型、恢复与阶段资格由技术负责人判断，不要求 worker 自行完成未确定的安全设计。

**目标：** 在合成数据环境证明一个 Shared Expert 能安全接收明确提及、受控回复原 Thread，并通过身份、隔离、持久化和故障门禁。

**架构：** 原生 Mattermost Channel 直达 QwenPaw；公开 Hook 只负责准入。Hikmah 提供 OAuth/BFF、元数据治理和 Plugin，Sidecar 在本阶段关闭。

**技术栈：** Python/FastAPI、SQLAlchemy/Alembic、PostgreSQL、React Plugin、pytest/Vitest；QwenPaw 资格实验独立于 API Python 工作区。

**规范与全局约束：** 继承[总览第 1 节](2026-09-05-implementation-roadmap.md#1-全局约束)的全部版本、隐私和交付要求；执行前阅读 [PRD 第 8～17 节](../../product/overview.md)及 [ADR-0007](../../decisions/0007-knowledge-collaboration-pilot-and-runtime-boundaries.md)。文件路径以仓库根目录为起点；“新增”均指本任务待创建文件。测试示例是必须实现的断言，不是当前可运行代码。

## P0-01：测试误连保护与应用工厂

**文件：** 精确分卡白名单见[首个工作包任务包](2026-09-05-p0-01-worker-packet.md)。新增测试 DB 保护/工厂及环境污染测试；修改 config/base/main、两个服务的配置构造、conftest、六个 API 测试及启动引用；CI 在最后一张卡接入。配置消除导入副作用必须与 app/fixture 接线一起完成，不能只传入 `_env_file=None` 就声称测试未读取 `.env`。

**接口：** `require_unit_test_database(environment: str, url: str) -> None`；不导入 Settings 或 Engine。`Database` dataclass 持有 `engine: AsyncEngine`、`sessions: async_sessionmaker[AsyncSession]`；`create_database(url: str) -> Database`；`create_app(settings: Settings, database: Database) -> FastAPI`。`get_db_session(request: Request)` 从 `request.app.state.database` 取得会话，保持 commit/rollback 语义。`Base` 仅持有 ORM metadata，不创建 Engine。

配置与入口增加 `load_settings() -> Settings`、`create_default_app() -> FastAPI`，加载配置仅发生在显式默认启动。移除 `config.py` 的模块级 Settings、服务默认参数绑定和模块级单例，测试使用注入 app；生产启动迁移资格在 P0-04 解锁前明确停止，不隐式 `create_all`。

- [ ] 在独立 `tests/unit/` 写安全测试，避免加载旧的 API autouse fixture：

```python
import pytest
from hikmah.core.test_database import require_unit_test_database

@pytest.mark.parametrize("environment,url", [
    ("development", "sqlite+aiosqlite:///:memory:"),
    ("test", "sqlite+aiosqlite:///hikmah.db"),
    ("test", "postgresql+asyncpg://db/hikmah"),
])
def test_rejects_non_ephemeral_database(environment: str, url: str) -> None:
    with pytest.raises(ValueError, match="isolated unit-test database required"):
        require_unit_test_database(environment, url)

def test_accepts_explicit_memory_database() -> None:
    require_unit_test_database("test", "sqlite+aiosqlite:///:memory:")
```

- [ ] 运行 `uv run pytest tests/unit/test_database_policy.py -v`；首次应因新模块不存在失败，不能因连接应用数据库失败。若运行依赖尚不可用，记录阻塞，不先执行旧 suite。
- [ ] 在任何 Engine 创建前执行最小保护，并把数据库所有权从导入全局移到应用实例：

```python
def require_unit_test_database(environment: str, url: str) -> None:
    if environment != "test" or url != "sqlite+aiosqlite:///:memory:":
        raise ValueError("isolated unit-test database required")
```

- [ ] 重写 API fixture：显式 `Settings(_env_file=None, environment="test", database_url="sqlite+aiosqlite:///:memory:")`；在创建 Engine 前调用保护。环境配置别名也必须被这些显式值覆盖；每用例独立 Engine/连接、创建 metadata 后 dispose，不对持久库 `drop_all`。HTTP 客户端注入该 app，生产不再启动 `create_all`。
- [ ] 增加 `test_app_factory.py`：两 app 写入互不相见；导入 models 不打开连接；未知 profile 启动拒绝；异常事务 rollback；子进程设置文件型 `HIKMAH_DATABASE_URL` 后运行测试，临时目录中的预置 sentinel 表和值保持不变。这里的文件数据库只由测试自身创建，不用仓库现有 DB 作验证对象。
- [ ] 重跑安全测试和 `uv run pytest apps/api/tests/test_app_factory.py -v`，再跑旧 `uv run pytest apps/api/tests -v`；Ruff、严格 Mypy 通过。将 `tests/unit/` 加到 pytest 收集和严格类型检查范围，CI 同步。
- [ ] 自审仅测试隔离和应用生命周期差异，提交 `fix: isolate test databases and inject application state`。验收证据包括误连被拒绝、sentinel 不变和两 app 隔离；退出码不能代替三项断言。

## P0-02：公开 Hook 的先行资格实验

**文件：** 新增 `experiments/qwenpaw-admission/pyproject.toml`、`admission_probe.py`、`tests/test_probe_contract.py`、`cases.json`；新增 `docs/research/qwenpaw-admission-qualification.md`。实验包不加入根 uv workspace，不修改上游。报告只有执行结果齐全后才标记完成。

**接口：** 实验配置固定上游版本/commit；`ProbeResult` 是 JSON 对象，字段为 `case_id: str`、`expected_model_starts: int`、`actual_model_starts: int`、`expected_tool_starts: int`、`actual_tool_starts: int`、`actual_posts: int`、`actual_context_reads: list[str]`、`status: Literal["pass", "fail", "not_run"]`、`evidence_ref: str`。只计数和存合成资源引用，不记录凭据。生产准入接口在 P0-06 定义，不能把 probe 当生产代理。

- [ ] 先写结果判定测试，覆盖“未运行不能通过”和“Hook 拒绝但模型仍启动”：

```python
def is_execution_blocked(model_starts: int, tool_starts: int, ran: bool) -> bool:
    return ran and model_starts == 0 and tool_starts == 0

def test_failure_must_block_execution() -> None:
    assert is_execution_blocked(0, 0, True)
    assert not is_execution_blocked(1, 0, True)
    assert not is_execution_blocked(0, 1, True)
    assert not is_execution_blocked(0, 0, False)
```

- [ ] 把函数放到 `admission_probe.py`，测试从模块导入；先运行 `uv run --project experiments/qwenpaw-admission pytest experiments/qwenpaw-admission/tests/test_probe_contract.py -v` 确認导入失败，再实现上述判定。实验依赖同步和运行时启动仅在获准环境执行。
- [ ] 用固定版本公开 `PluginApi.register_runtime_hook` 注册 `PRE_DISPATCH`。按[研究报告](../../research/2026-09-05-knowledge-collaboration-feasibility.md)定位的公开签名编写插件；启动时核验已注册状态，拒绝分支返回公开 `HookAction.SHORT_CIRCUIT`；异常不转换为允许。将完整调用签名、载入方式、退出状态写入资格报告供 P0-06 复用，任何版本差异暂停而非猜测。
- [ ] 在两个合成 Channel、两个隔离 Runtime 上逐项执行 `cases.json`：准确人类提及；用户名相邻前缀；代码块/引用中的提及；他人 Bot 伪造调用；本 Bot 回声；跨 Channel；重复事件；准入服务超时/异常；Hook 首次未注册；运行中卸载/重载；新 Workspace；斜杠命令；Console；后台定时入口；短路后的可见状态；Sidecar 停止。应禁止的路径必须证明模型和工具启动数均为 0；所有入口无法证明受保护时保持关闭。
- [ ] 重点先做“Hook 缺失/卸载”负向实验。仅仅有 readiness 健康检查不足以通过：必须证明不可用期间没有入口绕过准入。允许通过公开配置关闭 Console/后台功能、隔离网络和阻止未就绪 Channel 激活；若不能证明运行中失效仍被阻断，记为失败并停止后续路线，提交新 ADR 候选，不用 watchdog 延迟发现代替阻断。
- [ ] 分别记录 Hook 前的上下文读取：Bot 不属于另一 Channel，运行环境不能读另一记忆/索引/文件；普通问答仅取获准 Thread。Hook 即使拒绝执行，也不能掩盖提前越权读取。
- [ ] 自审实验源码、实际计数及脱敏证据，提交 `test: qualify public QwenPaw admission hooks`。纯函数、源码分析和 mock 全通过仍不能关闭 AR-010；真实固定版本的全部强制负向用例通过才允许进入 P0-03。

## P0-03：固定 BOM 与隔离拓扑

**文件：** 修改 `pyproject.toml`、`apps/api/pyproject.toml`、根/Web/API Client 的 `package.json`、`uv.lock`、`pnpm-lock.yaml`、`.github/workflows/ci.yml`；新增 `infra/pilot/compose.yml`、`infra/pilot/README.md`、`infra/pilot/bom.json`、`infra/pilot/validate_bom.py`、`tests/unit/test_bom.py`。不改动现有开发 Compose 或用户数据卷。

**接口：** BOM JSON 含 `schema_version: 1`、`components: list`；每项含 `name`、`version`、`source_commit`（源码组件）、`image_digest`（容器组件）、`license_evidence_ref`、`qualification_status`。`validate_bom(data: object) -> list[str]` 输出全部结构/固定版本错误；未取得证据的组件不得写 `qualified`。密钥配置只存 `*_secret_ref` 或 Compose 外部 secret 文件引用。

- [ ] 先写固定制品负向测试；样例只表达测试输入，不能充当真实 digest：

```python
from infra.pilot.validate_bom import validate_bom

def test_rejects_floating_image() -> None:
    errors = validate_bom({"schema_version": 1, "components": [{
        "name": "mattermost", "version": "latest",
        "image_digest": "", "qualification_status": "qualified",
        "license_evidence_ref": "",
    }]})
    assert any("version" in item for item in errors)
    assert any("digest" in item for item in errors)
    assert any("evidence" in item for item in errors)
```

- [ ] 运行 `uv run pytest tests/unit/test_bom.py -v` 确认缺失校验失败；实现类型检查和组件对应目标版本验证，`image_digest` 必须是实际解析的 `sha256:` 加 64 位十六进制值，源码 commit 必须由目标检出验证。新增包初始化文件使上述模块可导入。
- [ ] 先完成目标组件许可证/品牌及拟用方式复核，再在获准安装环境验证 Python 3.14 API 依赖、PostgreSQL 异步驱动、OAuth 客户端库与 Web 构建矩阵；QwenPaw/AgentScope 保留各自官方支持的隔离运行环境，不强塞进 API workspace。将实际解析版本锁定；目标版本不兼容则输出失败证据和 ADR 决策，不擅自下调 React/TS/Vite。
- [ ] 编写独立 Compose：独立项目名、卷、数据库/role；内部网络最小开放，Runtime 禁用任意 Shell、Docker Socket、宿主目录及跨频道卷。Foundation Bot、OAuth、准入和模型调用各自凭据；密钥来自仓库外受控路径，日志不展开配置值。配置缺失须启动失败。
- [ ] 在获准目标上运行 `docker compose -f infra/pilot/compose.yml config --quiet`，验证两席位跨卷/跨频道读取失败、数据库角色互读失败、无非必要公网监听；停止一个 Runtime 不影响人类聊天。只对该独立项目操作，恢复使用原制品和原卷，不删除卷。
- [ ] 运行目标工具链的 typecheck/test/build 及 BOM 校验，生成 SBOM、目标使用/分发方式的许可证及品牌复核记录。CI 不再用无条件批准全部依赖构建脚本作为安全依据；批准确有必要且已核验的包。
- [ ] 提交 `build: pin pilot artifacts and isolate runtime deployment`；未完成许可证/品牌及隔离实测不能开放真实团队。

## P0-04：治理数据库迁移、幂等和隔离恢复

**文件：** 新增 `alembic.ini`、`apps/api/migrations/env.py`、`apps/api/migrations/versions/0001_governance.py`、`apps/api/src/hikmah/models/admission.py`、`services/admission_store.py`、`apps/api/tests/test_admission_store.py`、`tests/integration/test_migrations.py`、`tests/integration/conftest.py`、`infra/pilot/backup_restore.py`、`docs/development/database-operations.md`；修改 `models/trace.py`、数据库配置与依赖。

**接口：** `reserve_admission(session: AsyncSession, post_id: str, seat_id: str, correlation_id: str) -> bool`。唯一约束 `(post_id, seat_id)`；准入元数据仅记真实来源、绑定版本和派生状态，不能承担 TaskRun。测试工厂 `make_test_database() -> Database` 使用 P0-01 内存 Engine；生产并发证明使用独立 PostgreSQL，不以 SQLite 结果代替。

- [ ] 在 `test_admission_store.py` 写重复保留测试，使用本文件导入的 `reserve_admission` 和由安全 conftest 提供的 `db_session: AsyncSession`：

```python
from sqlalchemy.ext.asyncio import AsyncSession
from hikmah.services.admission_store import reserve_admission

async def test_duplicate_post_is_not_reserved_twice(db_session: AsyncSession) -> None:
    assert await reserve_admission(db_session, "post-a", "seat-a", "trace-a")
    assert not await reserve_admission(db_session, "post-a", "seat-a", "trace-a")
    assert await reserve_admission(db_session, "post-a", "seat-b", "trace-b")
```

- [ ] 运行 `uv run pytest apps/api/tests/test_admission_store.py -v`，确认缺失实现失败；使用数据库唯一约束和 `ON CONFLICT DO NOTHING` 的受支持方言实现，不用“先 SELECT 再 INSERT”。保留单独第二席位的合法显式调用。
- [ ] 为现有治理模型建立首个迁移，补充约束/索引及关联元数据；P0-05 session、P0-06 绑定字段用各自后继迁移，不在首迁移预建未来完整产品。生产启动仅检查迁移 head，一致才 ready；缺失/落后返回未就绪，不自动改表。
- [ ] PostgreSQL 集成 fixture 必须只连接由本次测试创建且带随机名称/所有权标记的独立 database；拒绝业务库 URL，核验目标标记后才执行任何 DDL。在空库升级、前版升级、并发重复 20 次、故障回滚、进程重启重放条件验证最多一次保留。并发用例放 `tests/integration/test_migrations.py`。
- [ ] 实现恢复工具参数为 `--action {backup,restore-verify}`、`--profile-file`、`--output-dir`；profile 指向仓库外连接引用，不传口令。`restore-verify` 只创建独立恢复库，拒绝覆盖在线库；校验 schema、行数、外键及关键幂等键，并生成耗时/恢复点报告。备份加密和访问权限纳入操作文档。
- [ ] 运行 `uv run pytest tests/integration/test_migrations.py -v`（已获准隔离 DB 才执行）；实测备份→独立恢复→应用只读启动→重复事件仍拒绝，记录 RPO/RTO 样本。最终发布继续承担 24 h / 4 h 门禁，演练报告不能只记录 dump 成功。
- [ ] 提交 `feat: migrate governance metadata and verify recovery`；原型 SQLite 数据存在时先盘点并备份，制定单独迁移任务，不把 `create_all` 或清库作为升级策略。

## P0-05：可信 Actor、OAuth/BFF 与集中授权

**文件：** 新增 `core/auth.py`、`core/authorization.py`、`schemas/actor.py`、`api/v1/auth.py`、`models/auth_session.py`（均在 `apps/api/src/hikmah/`）；新增后继 Alembic 迁移、`apps/api/tests/test_auth.py`、`test_authorization.py`；修改 `api/v1/router.py`、`seats.py`、`knowledge.py`、`rules.py`、`traces.py`、`main.py`、`packages/api-client/src/index.ts` 及相应类型文件。

**接口：** 不可变 `AuthenticatedActor(user_id: str, team_id: str, session_id: str)` 仅由后端身份依赖构造；`require_actor(request: Request) -> AuthenticatedActor`；`authorize_channel(actor: AuthenticatedActor, channel_id: str, capability: str) -> None` 查权威成员/角色并失败拒绝。`GET /api/v1/auth/login`、`GET /api/v1/auth/callback`、`POST /api/v1/auth/logout`；浏览器只接收安全 cookie 和独立 CSRF 机制，不取得上游 Token。

- [ ] 用 `httpx.AsyncClient` 和 P0-01 app fixture 写匿名访问测试；`client` 无 cookie，不覆盖生产 auth 依赖：

```python
from httpx import AsyncClient

async def test_claimed_identity_does_not_authenticate(client: AsyncClient) -> None:
    response = await client.get("/api/v1/seats/missing", params={"user_id": "owner"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthenticated"
```

- [ ] 运行 `uv run pytest apps/api/tests/test_auth.py apps/api/tests/test_authorization.py -v`，确认旧自报身份/无保护路由不满足断言；以 P0-03 固定的成熟 OAuth 库实现 state、适用的 PKCE、回调 URL 白名单、session 轮换/过期/撤销、HttpOnly/Secure/SameSite cookie、CSRF 和服务端 Token 引用，不自建加密原语。
- [ ] 授权只根据公开 Mattermost 用户/Team/Channel API 和当前 session。客户端 `user_id`、reviewer、角色一律不能赋权；Bot 不能作为人类审阅者；权限查询异常拒绝。对象不存在或不可见统一 404，匿名 401，已认证但操作 capability 不足 403，版本冲突 409。
- [ ] 扩充测试：伪造 callback/state、session fixation、CSRF、登出后复用、成员被移出、跨 Team/Channel、管理员访问个人路径、Body reviewer 欺骗、上游超时。HTTP mock 只模拟上游响应，不直接注入“已授权”结论；所有受保护路由纳入矩阵，未实现的 Personal API 不注册。
- [ ] OAuth/session 增量迁移、统一错误 schema 和 OpenAPI 安全方案同步；API Client 删除身份 query/body 参数。异常返回稳定 code/message/correlation，日志脱敏，不把第三方响应堆栈发给用户。
- [ ] 在隔离 Mattermost 验证登录→查看获准席位→撤销成员→相同 session 被拒绝；运行 API 严格检查、客户端 typecheck。提交 `feat: authenticate governance requests through Mattermost BFF`。mock 成功不替代真实 OAuth 资格。

## P0-06：Shared Expert 绑定、请求准入和真实状态

**文件：** 新增 `models/expert_binding.py`、`schemas/admission.py`、`services/admission.py`、`services/post_verification.py`、`services/adapter_status.py`、`api/internal/admission.py`；修改 `models/seat.py`、`schemas/seat.py`、`api/v1/seats.py`、`services/foundation.py`、`services/runtime.py`、`models/trace.py`；新增后继迁移、`integrations/qwenpaw/hikmah_admission.py`、`apps/api/tests/test_admission.py`、`apps/api/tests/test_adapter_failures.py`、`tests/contracts/test_mattermost_contract.py`。路径未带前缀的 API 文件均位于 `apps/api/src/hikmah/`。

**接口：** `ExpertSeatBinding` 仅共享席位：`id`、`team_id`、`channel_id`、`bot_user_id`、`runtime_ref`、`workspace_ref`、`capabilities`、`enabled`、`version`；单席位单 Channel。`AdmissionRequest(post_id: str, seat_id: str)`；调用 runtime 身份由独立服务认证得出，不能由 body 声明。`AdmissionDecision(allowed: bool, reason: str, correlation_id: str | None)`；`POST /internal/v1/admissions` 仅受认证内部服务可达，独立于浏览器 `/api/v1`。所有字段均须 Pydantic 严格校验并禁止多余输入。

**状态契约：** `services/adapter_status.py` 定义 ADR-0005 的全部状态：`unconfigured`、`connecting`、`ready`、`degraded`、`unreachable`、`rejected`、`in_progress`、`completed`、`verification_required`。`ready` 只在固定版本契约探测通过时成立，`completed` 只来自权威成功终态；模拟器只在显式 test/demo profile，响应/UI/Trace 均强制 `simulated` 标识，健康检查不计入就绪。外部写请求发出后超时为 `verification_required`，不能再 POST。UI 状态是投影，不启动重试。

- [ ] 编写适配器负向测试；`MattermostFoundationService` 在 P0-01 的显式构造基础上增加已冻结的 Settings/`httpx.AsyncClient` 注入契约，测试使用 `MockTransport` 记录请求次数：

```python
def classify_post_failure(request_was_sent: bool) -> str:
    return "verification_required" if request_was_sent else "unreachable"

def test_unknown_post_is_not_a_retryable_failure() -> None:
    assert classify_post_failure(True) == "verification_required"
    assert classify_post_failure(False) == "unreachable"
```

- [ ] 首先从新增状态模块导入该函数运行失败测试，再实现分类；`test_adapter_failures.py` 进一步断言无 Token 不发请求且不返回 mock success，超时只发一次 POST，伪造 completed 事件被拒绝。删除 invented `/api/v1/agents/{id}/run` 调用；共享专家使用原生 Channel，Console 仅保留已获固定版本契约验证的用途，否则关闭。
- [ ] 实现绑定输入/输出分离和持久化：验证 Bot 类型、Team/Channel 归属、Runtime 注册及单 Channel 独占；输出仅显示安全标识和状态，无凭据、连接细节和私有上下文。Personal 旧字段不能映射为公共共享 Bot；有历史个人记录先拒绝启用并输出迁移清单，不删除数据。所有列表分页，PATCH 只更新明确提供的字段并核验 expected version。
- [ ] 实现窄准入顺序：服务身份绑定席位→读取权威 Post/发送者/Channel→解析准确提及（排除引用/代码/前缀）→验证人类与席位资格→原子 reserve→返回结果。P0/P1 只允许人类明确调用；任何 Agent 帖子不产生新工作。多显式目标分别保留，错误目标不重新路由。
- [ ] 将 P0-02 已验证公开 Hook 接到内部准入端点；失败短路且停用不受保护入口。内部认证使用 P0-03 已核验的服务凭据机制，并绑定调用 runtime、请求有效性和重放保护；不能把 correlation 当凭据。Hook 不接触模型或选择专家。
- [ ] `test_admission.py` 覆盖权威 Post 与请求身份/Channel/席位不匹配、Post 编辑/删除、资格撤销、并发重放、凭据轮换、准入超时、非人类发送者、代码引用提及。只有经权威 Post 核验且以当前内容重新确认的请求可执行；发送前再查原 Thread、Channel、绑定和许可。保留 metadata Trace，禁止私密正文。
- [ ] 运行 `uv run pytest apps/api/tests/test_admission.py apps/api/tests/test_adapter_failures.py -v` 和固定版本 Mattermost 契约测试；用 P0-02 故障集回归最终插件。补齐认证失败、未知 JSON/event、实际开放的流式片段、取消/迟到结果、外部 ID 错配用例；未获得权威取消结果不能显示已取消，不能靠重放产生替代任务。提交 `feat: admit explicit expert requests with verified provenance`。任何读取或写回路径绕过准入/许可检查均阻止 P0-07 放行。

## P0-07：可安装 Plugin 与 Pilot 0 纵向验收

**文件：** 新增 `apps/web/plugin.json`、`apps/web/vite.plugin.config.ts`、`apps/web/scripts/package-plugin.mjs`、`apps/web/tests/plugin.test.tsx`、`apps/web/tests/package-plugin.test.mjs`、`tests/e2e/test_pilot_zero.py`、`tests/e2e/conftest.py`、`docs/research/pilot-0-qualification.md`；修改 `apps/web/src/plugin.tsx`、RHS/席位组件、`packages/api-client/src/index.ts`、`apps/web/package.json`、CI。Plugin id 固定 `com.hrygo.hikmah`。

**接口：** 生产浏览器访问同源 `/hikmah/api/v1`，反向代理去掉 `/hikmah` 转发到 BFF `/api/v1`，OAuth callback 同样显式映射；本地 SPA 只作开发。Plugin 打包脚本输出 manifest 指定的单一 Webapp bundle 和安装归档；`POST`/`PATCH` 携带 CSRF，不携带自报用户身份。`uninitialize()` 清理 listener、注册返回的释放句柄和尚未完成请求。

- [ ] 编写注册/卸载测试及归档检查：Fake Registry 明确记录 RHS/Custom Post 注册次数与释放次数；两次 install/uninstall 不产生重复 handler；包内只有 manifest 声明路径，manifest id 与代码一致。错误的缺失 bundle 输入必须打包失败。

```javascript
import assert from 'node:assert/strict';
import {validateManifest} from '../scripts/package-plugin.mjs';

assert.throws(() => validateManifest({
  id: 'com.hrygo.hikmah',
  webapp: {bundle_path: 'webapp/missing.js'},
}, new Set()), /bundle/);
```

- [ ] 运行 `pnpm --dir apps/web test`；新增 `test:package` 脚本运行 `node --test tests/package-plugin.test.mjs`，先确认打包校验导出缺失失败再实现。`validateManifest(manifest, files)` 验证 id、兼容版本字段、相对 bundle 路径及实际文件存在性；不得接受目录穿越路径。
- [ ] 实现专用 Plugin build 与打包，不把 SPA HTML 当插件；核验 Mattermost 宿主公开 React/Plugin API 与目标 React 19.2 的兼容性。不能通过私有注入、第二聊天客户端或默默改版本绕过不兼容。将 `eslint . || true` 改为真实失败，并完成类型/生命周期清理。
- [ ] 在 RHS 展示席位可用性、原 Thread 的 Correlation、明确失败/待核验状态，提供返回原讨论入口。预留知识页入口但 P1 完成前不显示可用。Custom Post 输入严格 schema，富文本/URL 渲染做大小及协议白名单校验，不信任 Post props 授权。
- [ ] 用独立 E2E fixture 创建合成 Team/Channel/成员，配置来自仓库外 profile；fixture 只清理自身标记的资源。验证 OAuth 登录、安装/禁用/重启、同 Thread 读取/回帖、精确提及、多显式专家、人类邀请补充专家、相邻用户名、代码引用、跨频道、缺失/故障准入、重复事件、Bot 回声、Sidecar 关闭。用前一个已验证制品执行升级及回退，检查绑定/权限/治理数据保留，旧新 Client/API 契约兼容；首次安装没有前版时明确记为未验证并保留到后续 release。禁用所有机器人后人类聊天仍可用。
- [ ] 运行 `pnpm --dir apps/web test:package`、`pnpm --dir apps/web build:plugin`、全局质量门禁，再在获准环境执行 `uv run pytest tests/e2e/test_pilot_zero.py -v`。报告必须分列合成单测、固定版本契约和实际 E2E；未运行项不算通过。
- [ ] 提交 `feat: package governance plugin and qualify explicit expert flow`。Pilot 0 退出条件是 BOM/OAuth/安装/隔离/准确提及/故障拒绝/幂等/恢复/受控回帖均有证据。经负责人复核后仅开放 Pilot 1 的实现与资格验证，真实数据仍须满足其入场条件。

## 执行记录与回退

每任务提交前运行其针对性测试以及[总览质量门禁](2026-09-05-implementation-roadmap.md#5-验证与证据格式)，Issue/PR 按仓库规范关联。接口变化需同步 OpenAPI、API Client 与 Web。失败先停止对应能力并保留证据，不能回退到 mock success、无准入直达或清库；用户数据和上游检出保持完整。
