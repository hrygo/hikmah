---
title: P0-01 任务包：测试隔离与显式应用生命周期
description: 将第一个工作包冻结为四张有精确读写范围、接口、测试和停止条件的单 worker 任务卡。
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
  - implementation
  - testing
canonical: true
related:
  - 2026-09-05-pilot-0-foundation.md
  - 2026-09-05-work-item-sequence.md
  - ../worker-delivery-protocol.md
  - ../../decisions/0006-governance-metadata-persistence-and-schema-lifecycle.md
---

# P0-01 任务包：测试隔离与显式应用生命周期

> 执行技能为 `executing-plans`。四张卡准备度 `specified`、执行状态 `not_authorized`，均未执行。技术负责人核验本卡输入/工具链和前置交付后置为 ready；只在已有授权覆盖本卡动作时领取，默认单 worker 串行。

**目标：** 自动化测试无论受到工作目录 `.env` 还是进程环境变量影响，都只能创建自身内存数据库；导入业务模块不创建 Settings/Engine，不连接持久数据库。

**架构：** 测试保护函数 → 显式 Database 工厂 → 显式 Settings 与 app 工厂 → 独立 fixture/进程回归。应用生命周期只释放自己的资源，schema 生命周期交给测试 fixture 或后续 Alembic。

**技术栈：** 现有 Python 3.14、pytest/pytest-asyncio、SQLAlchemy asyncio/aiosqlite、FastAPI/httpx；本包不引入新依赖、服务或镜像。

**规范与全局约束：** [Pilot 0](2026-09-05-pilot-0-foundation.md)、[ADR-0006](../../decisions/0006-governance-metadata-persistence-and-schema-lifecycle.md)及[交付规范](../worker-delivery-protocol.md)。本包不修复 Runtime mock、OAuth 或生产迁移；这些能力在后续包验收前保持未就绪。

## 0. 基线和共同执行条件

调查基线 `fedafaedf6fc691f3beb6bff42afa7259da0d61f`，2026-09-05。实现时必须在交接记录写实际起点和上一张已验证卡的 commit；后续工作区与此文不符时先更新卡，不盲目套 patch。

本次源码确认：`models/base.py` 导入全局 settings 并创建 Engine/sessionmaker；`conftest.py` 复用它并清表；`config.py` 末尾立即构造 Settings；Foundation/Runtime 构造默认值也绑定该 settings；六个 API 测试文件直接导入全局 app。图谱仅定位符号，注入关系以源码为准。

| 卡 | 输入 | 允许写入 | 验收责任 |
|---|---|---|---|
| P0-01.A | 本文保护契约 | 新增 `apps/api/src/hikmah/core/test_database.py`、`tests/unit/test_database_policy.py` | 技术负责人核验负向集合和导入安全 |
| P0-01.B | A verified | 新增 `apps/api/src/hikmah/core/database.py`、`tests/unit/test_database_factory.py` | 技术负责人核验独立 Engine、连接与释放 |
| P0-01.C | B verified | 本文 C 节完整白名单 | 技术负责人审阅跨文件原子接线 |
| P0-01.D | C verified | 新增 `tests/unit/test_database_environment.py`；修改 `pyproject.toml`、`.github/workflows/ci.yml`；补本包验证记录 | 负责人复核误连证据和 CI 收集 |

执行目录为仓库根目录；所有测试输入均为合成数据。A/B 完成不能解锁旧 API suite，必须先完成 C 接线。只用获准的既有 Python 环境；如果 `uv run --no-sync` 无法找到依赖，记录阻塞，由负责人按现有授权处理环境，不能先运行 `uv sync` 或改锁文件。

每张卡共用收尾：对应测试通过→`uv run --no-sync ruff check` 和 `ruff format --check` 检查允许路径→对应路径严格 Mypy→`git diff --check`→仅暂存白名单→提交→交接记录。所有命令都检查实际断言，不只看退出码；发布、push、清库和改上游不在本包范围内。

## P0-01.A：单元测试数据库准入

**接口：** `require_unit_test_database(environment: str, url: str) -> None`，失败统一 `ValueError("isolated unit-test database required")`。仅同时满足环境 `test` 和精确 URL `sqlite+aiosqlite:///:memory:` 放行；不做字符串包含判断，不接受内存 URI 别名。

- [ ] 新增测试文件，完整内容如下；测试只导入保护模块，不导入 app/models/config：

```python
import pytest

from hikmah.core.test_database import require_unit_test_database


@pytest.mark.parametrize(
    ("environment", "url"),
    [
        ("development", "sqlite+aiosqlite:///:memory:"),
        ("production", "sqlite+aiosqlite:///:memory:"),
        ("test", "sqlite+aiosqlite:///hikmah.db"),
        ("test", "postgresql+asyncpg://db/hikmah"),
        ("test", "sqlite+aiosqlite:///file:memory?mode=memory&uri=true"),
        ("test", ""),
    ],
)
def test_rejects_other_databases(environment: str, url: str) -> None:
    with pytest.raises(ValueError, match="isolated unit-test database required"):
        require_unit_test_database(environment, url)


def test_accepts_explicit_memory_database() -> None:
    require_unit_test_database("test", "sqlite+aiosqlite:///:memory:")
```

- [ ] 运行 `uv run --no-sync pytest tests/unit/test_database_policy.py -v`，预期由于新模块不存在而失败，不能出现数据库连接或旧 fixture 的清表日志。
- [ ] 新增生产保护模块，完整实现如下：

```python
def require_unit_test_database(environment: str, url: str) -> None:
    if environment != "test" or url != "sqlite+aiosqlite:///:memory:":
        raise ValueError("isolated unit-test database required")
```

- [ ] 重跑同一命令，预期六个拒绝用例及一个允许用例通过；核对测试没有复制另一份保护函数。
- [ ] 按共同收尾检查两文件，提交 `test: guard unit tests against persistent databases`，交接 A 的实际 commit 和七个断言结果。

**停止/回退：** 任何 import 读取用户配置或持久数据库都停止并交给负责人；本卡仅新增两个文件，撤销本卡提交不应涉及用户数据。A 只证明保护函数，尚未证明真实测试已使用保护。

## P0-01.B：显式 Database 工厂

**接口：** `Database(engine: AsyncEngine, sessions: async_sessionmaker[AsyncSession])` 为 frozen dataclass；`create_database(url: str) -> Database`。调用创建 Engine 对象但不打开连接；函数不读取 Settings，不创建表、不管理迁移。调用方负责 `await database.engine.dispose()`。

- [ ] 新建 `test_database_factory.py`，以下测试验证实例隔离，所有输入只用 A 允许的内存 URL：

```python
from sqlalchemy import text

from hikmah.core.database import create_database
from hikmah.core.test_database import require_unit_test_database


async def test_two_engines_do_not_share_rows() -> None:
    url = "sqlite+aiosqlite:///:memory:"
    require_unit_test_database("test", url)
    first = create_database(url)
    second = create_database(url)
    try:
        for database in (first, second):
            async with database.engine.begin() as connection:
                await connection.execute(text("CREATE TABLE sentinel (value INTEGER)"))
        async with first.engine.begin() as connection:
            await connection.execute(text("INSERT INTO sentinel VALUES (7)"))
        async with second.engine.connect() as connection:
            count = await connection.scalar(text("SELECT count(*) FROM sentinel"))
        assert count == 0
    finally:
        await first.engine.dispose()
        await second.engine.dispose()
```

- [ ] 运行 `uv run --no-sync pytest tests/unit/test_database_factory.py -v`，确认缺失工厂而失败。
- [ ] 实现完整工厂；此时不接线、不删旧 Engine：

```python
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine


@dataclass(frozen=True)
class Database:
    engine: AsyncEngine
    sessions: async_sessionmaker[AsyncSession]


def create_database(url: str) -> Database:
    engine = create_async_engine(url)
    return Database(
        engine=engine,
        sessions=async_sessionmaker(engine, expire_on_commit=False),
    )
```

- [ ] 增加下列用例，直接阻止底层连接；工厂创建成功、显式连接才触发拒绝，证明构造与连接分开。资源释放在 finally 中执行：

```python
from typing import Never

import aiosqlite
import pytest

from hikmah.core.database import create_database


async def test_factory_does_not_connect(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse_connect(*_args: object, **_kwargs: object) -> Never:
        raise AssertionError("explicit connection attempted")

    monkeypatch.setattr(aiosqlite, "connect", refuse_connect)
    database = create_database("sqlite+aiosqlite:///:memory:")
    try:
        with pytest.raises(AssertionError, match="explicit connection attempted"):
            async with database.engine.connect():
                pass
    finally:
        await database.engine.dispose()
```
- [ ] 运行 A/B 两个文件和共同收尾，提交 `refactor: construct isolated database resources explicitly`。验收必须包含两实例数据隔离与连接生命周期，不能只有 dataclass 字段相等。

**停止/回退：** 如果需要修改 Settings、模型或 fixture，停止；那是 C 的原子接线范围。不得为通过 B 修改数据库方言或安装新依赖。

## P0-01.C：配置、应用与测试原子接线

**目的：** 消除导入副作用并让全部现有 API 测试使用新 Database。此卡是一次必要的跨文件原子变更：旧 app、全局配置和 fixture 不能分别保持半接线状态。worker 只按下表改，不选择新的依赖注入框架。

**白名单与具体修改：**

| 文件 | 修改锚点与要求 |
|---|---|
| `apps/api/src/hikmah/core/config.py` | 保留 Settings 字段，删除模块末尾 `settings = Settings()`；新增 `load_settings() -> Settings`，只在函数被调用时构造 Settings |
| `apps/api/src/hikmah/models/base.py` | Base 映射字段原样保留；移除 Engine/sessionmaker/settings 全局构造；`get_db_session(request: Request) -> AsyncGenerator[AsyncSession]` 从 app.state.database 取得会话并保持 commit/rollback |
| `apps/api/src/hikmah/main.py` | 新增 `create_app(settings: Settings, database: Database) -> FastAPI`；middleware、handlers、router 注册移入；handlers 读取该 app 设置；lifespan 只在 finally 释放该 DB；删除模块级 app 构造 |
| `apps/api/src/hikmah/main.py` | 新增 `create_default_app() -> FastAPI`，仅在运行入口调用 load_settings/create_database；`get_openapi_schema(app: FastAPI) -> dict[str, object]` 使用显式 app；Uvicorn 启动改 factory |
| `apps/api/src/hikmah/services/foundation.py` | `MattermostFoundationService(base_url: str, token: str)` 必须显式参数；删除 settings 导入及全局 `foundation_service`，其他行为留给 P0-06 |
| `apps/api/src/hikmah/services/runtime.py` | `AgentRuntimeBridgeService(qwenpaw_url: str)` 必须显式参数；删除 settings 导入及全局 `runtime_bridge`，其他行为留给 P0-06 |
| `apps/api/tests/conftest.py` | 删除旧 autouse 全局建表/清表；增加本节 fixtures，全部只用显式 test Settings/Database |
| `apps/api/tests/test_health.py`、`test_seats.py`、`test_rules.py`、`test_knowledge.py`、`test_traces.py` | 删除 `from hikmah.main import app`；HTTP 用例参数注入 `client: AsyncClient`，移除局部重复客户端构造，原业务断言保留 |
| `apps/api/tests/test_openapi.py` | 删除全局 app 导入；测试参数改 `app: FastAPI`，原 OpenAPI 断言保留 |
| 新增 `apps/api/tests/test_app_factory.py` | 校验独立 app、会话 commit/rollback、未知 profile 拒绝、lifespan 释放且无 create_all |
| `tests/unit/test_database_factory.py` | 增加导入安全子进程回归；保留 B 的隔离和连接断言 |
| `apps/api/Dockerfile`、`AGENTS.md`、`CONTRIBUTING.md`、根 `README.md` | 仅将活动启动示例中的 `hikmah.main:app` 改为 `hikmah.main:create_default_app --factory`；保留其他内容，历史 archive 不批改 |

表中第二次出现的测试短文件名均位于 `apps/api/tests/`。当前源码检索未见外部使用两个服务单例，执行时在 `apps/api`、`packages`、`infra`、`.github` 重查精确符号；如新出现消费者，交由负责人扩展白名单，不能删除使用者来省事。

**冻结接口与生命周期：** `app.state.settings` 为本 app 的 Settings；`app.state.database` 为本 app 的 Database。`create_app` 不加载环境、不启动连接、不建表。profile 允许 `test/development/demo/pilot/production`，未知值拒绝；本卡阶段 pilot/production 在默认启动入口以明确的迁移资格缺失错误停止，P0-04 才用真实 revision probe 解锁。开发不再隐式建表，初始开发数据准备也须走后续迁移。该临时限制必须在 README 说明。

**安全 fixture 的精确契约：**

- `test_settings() -> Settings`：`_env_file=None`，显式覆盖所有当前配置字段：app_name=`Hikmah Test`、environment=`test`、debug=false、api_v1_prefix=`/api/v1`、database_url 为精确内存 URL、mattermost_url=`http://localhost:8065`、mattermost_bot_token 空字符串、mattermost_team_name=`test-team`、qwenpaw_endpoint=`http://localhost:8080`、cors_origins 为空列表。未来增加字段必须补显式测试值。
- `database(test_settings) -> AsyncGenerator[Database]`：先保护环境/URL，再创建 Engine；创建 metadata 只在本 fixture，finally dispose；不调用 `drop_all`。先确保现有四个领域模型通过 router 导入注册到同一 Base.metadata。
- `app(test_settings, database) -> FastAPI`：只调用 `create_app`，不导入默认实例。
- `client(app) -> AsyncGenerator[AsyncClient]`：`ASGITransport(app=app)`、`base_url="http://test"`；无外部连接。httpx 不自动执行 lifespan，生命周期测试显式使用 `app.router.lifespan_context(app)`。
- `db_session(database) -> AsyncGenerator[AsyncSession]`：使用该 Database.sessions；关闭会话不删业务库。测试与 HTTP 同一用例共享同一个内存 Engine，不同用例不同 Engine。

- [ ] 先在独立 `tests/unit/test_database_factory.py` 增加导入安全子进程测试：将 Pydantic Settings 构造和 SQLAlchemy `create_async_engine` 替换为一旦调用即抛异常的 spy，再导入 config/models.base/main/两个 services 模块。固定只导入，不访问默认启动函数；旧代码应因导入构造而失败。测试子进程环境仅传显式非敏感路径和 test 值，不继承真实连接/凭据。
- [ ] 按白名单逐处进行接线，保留路由路径、业务 schema 和现有错误行为；本卡不兼做 OAuth/失败语义升级。新增需要的模块类型 imports，不引入 `Any`/`type: ignore` 掩盖 app.state 的类型边界；用运行时 `isinstance(value, Database)` 验证依赖对象并在错误时明确拒绝。
- [ ] `get_db_session` 的核心行为采用以下片段，imports 明确为 `AsyncGenerator`、`Request`、`AsyncSession`、本包的 `Database`；Base 定义保持原样：

```python
async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession]:
    database = request.app.state.database
    if not isinstance(database, Database):
        raise RuntimeError("application database is not configured")
    async with database.sessions() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

- [ ] 先创建安全 fixture 和测试 app，再运行 `uv run --no-sync pytest apps/api/tests/test_app_factory.py -v`。测试在内存中增加只用于本用例的写入/抛错路由：成功响应后新 session 能读到记录；抛错后新 session 无记录；第二个 app 无第一 app 数据。路由只存在测试创建的 app，不写入生产 router。
- [ ] 明确两类启动测试：`create_app` 只构造无连接；进入 lifespan 后不会创建表，退出/异常退出调用 dispose。以临时内存 DB 查询 `sqlite_master` 验证没有自动业务表，不能只检查 mock 被调用。
- [ ] 重跑导入安全用例，再运行 `uv run --no-sync pytest apps/api/tests -v`；六个测试文件全部使用 fixture，任何旧全局 app/Engine 引用残留都阻止验收。运行严格 Mypy/Ruff，记录新增启动命令及未开放生产 profile。
- [ ] 提交 `refactor: wire explicit settings and application test fixtures`。跨文件 atomic diff 由负责人逐项核对白名单和原断言；不能拆成可启动但测试仍指向旧库的半成品 PR。

**停止/回退：** 发现 Settings 隐式读取、消费者超出白名单、原业务接口必须改变或现有持久数据需迁移，停止并交技术负责人；仅形成代码制品，不启动在线服务。回退本卡代码保留 A/B，但旧 suite 在重新验证前仍禁止运行。

## P0-01.D：误连、环境污染与 CI 的闭环证明

**接口：** 新增 `tests/unit/test_database_environment.py`；测试用 `tmp_path` 创建本用例自己的文件 SQLite sentinel，不用仓库 `hikmah.db`。子进程只通过标准库 `subprocess.run`、当前 `sys.executable`、显式最小 env 和 60 秒 timeout 执行受限检查，不安装依赖、不访问网络。

- [ ] 编写参数化子进程测试：一种通过工作目录 `.env` 指向 sentinel；一种通过 `HIKMAH_DATABASE_URL` 指向 sentinel；一种同时存在且值冲突。`.env` 仅含合成测试路径，无真实凭据。
- [ ] 每个场景先创建 sentinel 表和固定行，记录数据库 schema 与行；子进程执行 `pytest apps/api/tests/test_health.py apps/api/tests/test_openapi.py -v` 并使用 C 安全 fixtures。结束后父进程再次读取 sentinel schema/行，必须完全一致；不能只看子进程通过或文件 hash。
- [ ] 子进程工作目录使用 tmp_path，测试文件以解析后的仓库绝对路径传入，显式加载仓库 pyproject 配置。保证 `PYTHONPATH` 指向当前源码且不覆盖用户全局环境；若测试导入依赖当前 editable 安装，先核验路径，不静默运行其他安装版本。
- [ ] 运行 `uv run --no-sync pytest tests/unit/test_database_environment.py -v`，预期三个污染场景仍只使用内存测试库、sentinel 不变、子进程无泄漏输出。故意把测试 Settings 改成文件 URL 的故障注入只在子进程输入里做，预期保护先拒绝，sentinel 仍不变。
- [ ] 修改 pytest `testpaths` 为 `tests/unit` 和 `apps/api/tests`；CI 先运行独立 unit 再运行 API suite，Mypy 纳入 `tests/unit`，不加跳过标记。使用 `uv run --no-sync pytest --collect-only -q tests/unit apps/api/tests` 核验新增文件均在收集结果。
- [ ] 运行 P0-01 所有单测和 API suite、Ruff/Mypy，记录原有 API 断言没有删除且误连用例实际通过；再执行 `git diff --check`，提交 `test: enforce isolated database execution in CI`。

**工作包退出：** A/B/C/D 全部 verified；无 import-time Settings/Engine，旧 suite 不再清持久库，环境污染被隔离，事务和生命周期行为正确，CI 收集完整。仍不意味着 PostgreSQL 迁移、恢复、身份或 Hook 资格已完成。下一步仅解锁 P0-02.A 的负责人契约卡。
