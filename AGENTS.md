# Hikmah（群贤）- AI Agent 协作与开发规范指南

> 🎯 **指令声明**：本文件是所有 AI Coding Agents（包括 Antigravity、Claude Code、Cursor 等）在 `hikmah` Monorepo 开展架构设计、代码编写、重构、测试与文档维护的**最高事实源与执行准则**。

> 📌 **项目状态与事实边界**：正式产品终态以 [`docs/product/overview.md`](docs/product/overview.md) 和 Accepted ADR 为准；精确目标版本以 [`docs/architecture/version-baseline.md`](docs/architecture/version-baseline.md) 为准。截至审查基线 `0d45229`，现有代码是架构脚手架，不代表真实联调、安全、升级或生产门禁已经通过。差距、证据与未授权代码工作统一见 [`docs/project/prd-architecture-review-tracker.md`](docs/project/prd-architecture-review-tracker.md)。

> 📌 **长期方向与任务交付**：研发路线遵循[长期路线图](docs/project/long-term-roadmap.md)；实施分派遵循[受控任务交付规范](docs/development/worker-delivery-protocol.md)和[工作项队列](docs/development/plans/2026-09-05-work-item-sequence.md)。工作包不能直接作为单 worker 任务；先冻结任务卡，再在对应授权和前置证据满足时执行。

---

## 🏛️ 项目定位与三大基石 (Core Foundation & Fact Sources)

Hikmah 是面向 3–20 人私有团队的**轻量人机协作治理与编排层**。我们遵循 **“复用优先 (Reuse-First)”** 原则，绝不从零重造即时通信、通用工作流或多余 Agent 运行时。

```
                    ┌──────────────────────────────────────────┐
                    │       Mattermost（目标版本见基线）          │
                    │  (组织/团队/频道/消息/权限/Web App Plugin 宿主) │
                    └─────────────────────┬────────────────────┘
                                          │ Events / Plugin API
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Hikmah 控制层 (Control Plane)                          │
│        Python 3.14 + FastAPI · 席位映射 · 静默规则 · 人审知识晋升 · 关联审计           │
└──────────────────────┬───────────────────────────────┬──────────────────────┘
                       │                               │
                       ▼                               ▼
       ┌───────────────────────────────┐ ┌───────────────────────────────┐
       │     QwenPaw 专家/个人运行时     │ │    AgentScope 多智能体框架    │
       │ (驱动共享专家席位与私有专属助理)   │ │  (驱动 Coordinator 频道协调器)  │
       └───────────────────────────────┘ └───────────────────────────────┘
```

| 系统基石 | 选型与定位 | 事实源归属 (Source of Truth) |
|---|---|---|
| 🏢 **协作底座 (Collaboration Foundation)** | **Mattermost**（精确版本见目标基线） | **协作与通信事实源** · 组织/团队/频道/消息/文件/权限与 UI 宿主 |
| 🧠 **专家与个人 Agent 运行时** | **QwenPaw** | **专家与个人 Agent 运行事实源** · 驱动团队共享专家席位与个人专属助理 |
| 🤖 **团队多智能体协同框架** | **AgentScope** | **多 Agent 协同与协调事实源** · 驱动频道 Coordinator Sidecar 与协同流 |
| 🛡️ **Hikmah 控制层 (Control Plane)** | **Python FastAPI + React Plugin** | **治理与编排事实源** · 席位映射/静默规则/人审知识晋升/关联审计 |

---

## 🔗 本地关联与上游只读参考仓库 (Related & Reference Repositories)

在开发环境中，同级目录维护了各基石项目的官方上游仓库。**关联仓库必须严格保持与官方最新 Release 版本同步，本地仅检出并保留最新 Release Tag**，供 Agents 查阅官方 API 契约、数据结构与插件机制（**仅供只读查阅与契约核验，严禁侵入修改**）：

| 本地相对路径 | 官方 GitHub 仓库 | 同步最新 Release | 作用与参考定位 |
|---|---|---|---|
| `../mattermost` | [mattermost/mattermost](https://github.com/mattermost/mattermost) | `v11.10.1` | 官方协作底座与 Web App Plugin 宿主参考源码 |
| `../mattermost-plugin-agents` | [mattermost/mattermost-plugin-agents](https://github.com/mattermost/mattermost-plugin-agents) | `v2.6.0` | 官方 Agent 插件架构与 Custom Post 实现参考 |
| `../QwenPaw` | [agentscope-ai/QwenPaw](https://github.com/agentscope-ai/QwenPaw) | `v2.2.0-beta.1` | 团队共享专家与个人专属助理运行时参考源码与 Channel 接入 |
| `../agentscope` | [agentscope-ai/agentscope](https://github.com/agentscope-ai/agentscope) | `v2.0.7.post1` | 团队多智能体协作框架与 Coordinator Sidecar 协调工作流参考 |
| `../zulip` | [zulip/zulip](https://github.com/zulip/zulip) | `12.2` | 备选底座研究与 Topic 消息模型设计参考 |


> 📌 **版本同步与维护准则**：
> 1. **最新 Release 同步**：所有关联上游仓库必须定期使用 `git fetch --tags` 获取最新发布，并检出至官方最新 Release Tag。
> 2. **路径引用规范**：在项目文档、配置与说明中，统一使用相对于 Monorepo 根目录的相对路径（如 `../agentscope`）及对应的 GitHub 官方仓库链接。
> 3. **只读与零侵入红线**：禁止在关联上游仓库中引入未提交代码、临时修改或私有分支，保持 HEAD 严格与上游 Release 标签一致。

---

## 📐 核心架构原则与硬性门禁 (Non-Negotiable Rules)

1. **复用优先与薄治理**（[ADR-0001](docs/decisions/0001-reuse-first-thin-control-plane.md)）：
   - 严禁自建 IM 消息存储、通用工作流引擎或独立聊天客户端；
   - Hikmah 仅维护自有薄治理数据（席位映射、协调规则、审核单、Correlation Trace）。
2. **底座选型唯一性**（[ADR-0003](docs/decisions/0003-adopt-mattermost-as-collaboration-foundation.md)）：
   - 协作底座已正式确定为 **Mattermost**；UI 采用 **Mattermost Web App Plugin (React 19 / TS 6)** 注入 RHS 与 Custom Post。
3. **上游零侵入 (Zero Upstream Intrusion)**：
   - 严禁 vendor 上游源码；严禁直读直写 Mattermost 私有数据库；严禁维护长期私有 fork；
   - 仅通过官方 REST API (v4)、WebSocket 事件流及公开 Plugin 机制与上游交互。
4. **个人 Agent 隐私保护 (Owner-Only Isolation)**：
   - Personal Agent 绝不能注册为公共可见的 Bot，严禁在未经 Owner 显式授权时读取群聊或暴露私有上下文。
5. **Coordinator Sidecar 静默规则**：
   - 成员显式 `@` 专家时，Coordinator 100% 静默观察，绝不擅自抢答或改写提问；
   - 未 `@` 且触发提问时，依规则最多推选一名主答专家。
6. **知识人审晋升 (Human-in-the-Loop Knowledge Promotion)**：
   - 群聊对话沉淀为团队知识资产前，必须经过人工审核、作用域圈定与脱敏确认。
7. **全链路关联审计 (Correlation Record)**：
   - 跨系统串联 Mattermost Post、QwenPaw 运行、AgentScope 协调与工具调用，记录元数据与 Trace，不复制私密消息正文。

---

## 📖 核心领域模型速查 (Domain Concepts)

| 领域模型 | 对应类/契约 | 核心作用与说明 |
|---|---|---|
| 🪑 **ExpertSeatBinding** | 目标契约；当前脚手架为 `hikmah.models.seat.ExpertSeat` | 团队共享专家席位，将 QwenPaw Workspace 映射为 Mattermost Bot；不得承载 Personal Agent |
| 🔒 **PersonalAgentBinding** | 目标独立契约；见 ADR-0004 | 唯一 Member 的 owner-only QwenPaw Runtime 绑定，不注册公共 Mattermost Bot |
| 🛡️ **SidecarRuleProfile** | `hikmah.models.rule.SidecarRuleProfile` | 频道级协调规则（显式提及静默、未提及策略、置信度阈值、写操作审核要求） |
| 📚 **KnowledgeCandidate** | `hikmah.models.knowledge.KnowledgeCandidate` | 知识晋升提议单（群聊高价值结论沉淀的人审流水线与作用域圈定） |
| 🔍 **CorrelationRecord** | `hikmah.models.trace.CorrelationRecord` | 跨系统关联审计追踪（串联 Post、Runtime Session 与 Tool Call，零私密正文复制） |

---

## 📁 Monorepo 目录结构

```
hikmah/
├── apps/
│   ├── api/                     # 后端目标：Python 3.14.x · FastAPI · SQLAlchemy 2.x · Pydantic v2
│   │   ├── src/hikmah/
│   │   │   ├── main.py          # FastAPI 启动入口、CORS 与统一异常拦截
│   │   │   ├── core/            # 配置 (Pydantic Settings)、领域异常
│   │   │   ├── models/          # SQLAlchemy 2.x 异步 ORM 模型
│   │   │   ├── schemas/         # Pydantic v2 强类型数据契约
│   │   │   ├── services/        # Mattermost/QwenPaw/AgentScope 桥接服务
│   │   │   └── api/v1/          # Health, Seats, Rules, Knowledge, Traces REST 接口
│   │   └── tests/               # pytest 单元与集成测试 (conftest 自动初始化表结构)
│   └── web/                     # 前端目标：React 19.2 · TypeScript 6.0 · Vite 8
│       ├── src/
│       │   ├── plugin.tsx       # Mattermost Web App Plugin 入口 (RHS, Custom Post)
│       │   ├── App.tsx          # 独立治理控制台主界面
│       │   └── components/      # RHS 知识审核面板、交互卡片、席位控制台
│       └── tests/               # Vitest 组件测试
├── packages/
│   └── api-client/              # 共享 TypeScript 类型定义与基于 OpenAPI 的 API Client
├── infra/                       # 目标部署：Mattermost + 独立 PostgreSQL 16 治理库 + Hikmah API
├── docs/                        # 官方文档中心 (产品规范、架构导航、ADRs、研究报告)
├── .github/workflows/ci.yml     # 2026 最佳实践 GitHub Actions CI 流水线
├── pyproject.toml               # Python 根配置与 uv 工作区 (Ruff, Mypy Strict, Pytest)
├── pnpm-workspace.yaml          # Node.js 根配置与 pnpm 工作区
├── package.json                 # 根工作区 package.json ("name": "hikmah")
└── AGENTS.md                    # 本文件
```

目录中的类名和模块表示当前脚手架位置；如果与终态契约不一致，先依据审查跟踪表创建明确任务，不得把脚手架结构反向升级为产品事实源。

---

## 🛠️ 常用开发与验证命令

> 当前脚手架的 API fixture 会复用应用数据库并清表。P0-01 的隔离接线通过前，不执行下列旧 API suite 或包含它的全量命令；先按[首个工作包任务卡](docs/development/plans/2026-09-05-p0-01-worker-packet.md)执行独立安全测试。纯文档修改执行文档校验，不以运行旧 suite 作为收尾动作。

### 1. 后端 (Python / uv)
```bash
# 同步并安装全部工作区依赖
uv sync --all-groups

# 代码格式化与 Lint 检查
uv run ruff format .
uv run ruff check .

# 严格类型检查 (Strict Typecheck)
uv run mypy apps/api/src apps/api/tests

# 运行自动化测试套件
uv run pytest apps/api/tests -v

# 启动本地开发服务
uv run uvicorn hikmah.main:app --reload --port 8000
```

### 2. 前端与共享包 (Node.js / pnpm)
```bash
# 安装依赖
pnpm install

# 批准依赖构建脚本 (pnpm 11 安全策略)
pnpm approve-builds --all

# 严格类型检查
pnpm run typecheck

# 运行前端 Vitest 单元测试
pnpm run test

# 生产构建 (Vite App & Packages)
pnpm run build

# 启动前端独立控制台 Dev Server
pnpm run dev:web
```

### 3. 全量门禁一键验证 (Full Quality Gate)
```bash
uv run ruff format --check . && \
uv run ruff check . && \
uv run mypy apps/api/src apps/api/tests && \
uv run pytest apps/api/tests -v && \
pnpm run typecheck && \
pnpm run test && \
pnpm run build
```

---

## 🤖 AI Agent 编码与协作纪律 (Agent Discipline)

1. **先验证后断言 (Verify Before Claim)**：
   - 任何代码生成或修改后，必须主动执行对应的 `ruff`, `mypy`, `pytest` 或 `pnpm typecheck` / `test`，确认通过后方可报告完成。
2. **严禁类型降级**：
   - Python 代码必须满足 `mypy --strict` 标准，严禁在无必要时使用 `Any`；
   - TypeScript 代码必须开启全部严格检查，严禁引入未使用的变量或导入。
3. **文档与代码强同步**：
   - 领域模型字段或 REST 接口变动时，必须同步更新 `packages/api-client`、`apps/web` 与 `docs/` 文档。
4. **Git 与 PR 协作规范**：
   - `main` 分支已开启分支保护，严禁 Force Push，所有合并必须走 Pull Request；
   - **PR 标题**：严格遵守 Conventional Commits 格式（如 `feat: ...`, `fix: ...`, `docs: ...`, `chore: ...`, `ci: ...`）；
   - **关联 Issue 强校验**：PR 正文必须显式关联目标 Issue（如 `Fixes #123` 或 `Refs #123`；非功能性小微改动可标注 `[skip-issue]` 并在 PR 中说明原因）。
5. **Issue 与 PR 标签规范 (Label Taxonomy)**：
   - 所有创建的 Issue 与 PR 必须严格遵照 [`.github/labels.yml`](.github/labels.yml) 定义的标准体系进行标签归类，禁止擅自创建未定义的非标标签；
   - **创建 Issue 标签组合建议**：
     - `Type`（必需，1个）：如 `type: bug` / `type: feat` / `type: proposal` / `type: docs` 等；
     - `Area`（可选/推荐，1~2个）：如 `area: api` / `area: web` / `area: plugin` / `area: bridge` / `area: infra`；
     - `Priority`（按需，1个）：如 `priority: high` / `priority: medium`；
     - `Status`（初始）：默认赋予 `status: triage`，进入处理后推进为 `status: in-progress`。
   - **创建/管理 PR 标签组合建议**：
     - `Type`（必需，对齐 PR 性质）：如 `type: feat` / `type: fix` / `type: refactor`；
     - `Area`（推荐）：涉及的技术模块标签；
     - `Size`（按需）：由变更行数确定（`size: XS` ~ `size: XL`）；
     - `PR 状态`：如草稿/进行中打上 `pr: work-in-progress`。
6. **长期路线与执行型团队交付**：
   - 任务必须能追溯到阶段、工作包、PRD/ADR 和验收证据；试点通过不能替代完整 MVP 或发布资格。
   - 技术负责人负责上游契约、技术取舍、安全/持久化边界、任务拆分和验收；worker 只执行冻结卡片，不临场发明 API、升级版本或改变治理规则。
   - 只有 `ready + authorized + 前置卡 verified` 的任务可领取。每卡明确基线、精确读写白名单、输入/输出、失败测试、验证命令、回退和停止条件。
   - 发现公开扩展不足、权限/版本冲突、未知用户改动或目标环境不符时停止本卡并提交证据；不能靠降级测试、模拟成功、扩大作用域继续推进。
   - 任务完成、工作包集成、阶段资格、能力开放分别验收；规划文档不作为执行证据。队列中的角色安排不构成启动多 Agent 或操作外部环境的授权。
