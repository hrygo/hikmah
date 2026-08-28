---
title: Hikmah GitHub 仓库初始化与技术栈设计
description: 记录 Hikmah 开源仓库初始化、协作基线和首个技术栈选择的历史设计。
document_type: archived-artifact
status: archived
created: 2026-08-28
updated: 2026-08-28
owners:
  - hikmah-maintainers
audience:
  - maintainers
tags:
  - archive
  - github
  - bootstrap
canonical: false
related:
  - implementation-plan.md
  - ../../product/overview.md
---

# Hikmah GitHub 仓库初始化与技术栈设计

> 归档说明：本设计已完成实施，仅用于追溯仓库基线。当前产品和技术要求以 [`docs/product/overview.md`](../../product/overview.md) 为准。

## 1. 目标与范围

将已有的 Hikmah 设计阶段仓库整理为可公开协作的 GitHub 仓库，并记录首个实现切片所采用的 Python + React 技术基线。此次交付包含仓库说明、忽略规则、Apache-2.0 许可证、贡献与安全入口、GitHub Issue/PR 模板、远端仓库描述和 topics。

此次交付不实现产品功能，不生成没有业务内容的前后端空壳，不添加无法运行的 CI，不修改 AgentScope 或 QwenPaw 上游代码，也不强制覆盖任何现有远端历史。

## 2. 当前基线

- 本地目录已经是 Git 仓库，当前分支为 `main`。
- 已有提交 `2a8611f docs: add Hikmah architecture design book`。
- 本地尚未配置 `origin`；目标远端为公开仓库 `https://github.com/hrygo/hikmah.git`。
- 现有产品规范、设计册和批准记录保留为设计事实源。
- `assets/hikmah-developer-recruitment-card.png` 与 `assets/hikmah-developer-recruitment-card-back.png` 已由工作区现状纳入版本控制范围，不移除、不改写。

## 3. 仓库健康基线

### 3.1 文档与维护入口

- `README.md`：中英双语项目定位、设计阶段状态、核心边界、架构文档、技术栈、路线图、贡献方式和许可证。
- `LICENSE`：标准 Apache License 2.0 文本，版权主体使用 `Hikmah contributors`，不虚构个人法定姓名。
- `CONTRIBUTING.md`：设计优先、变更范围、测试要求、接口契约、上游零侵入和 PR 约定。
- `CODE_OF_CONDUCT.md`：采用 Contributor Covenant，明确维护者处理渠道。
- `SECURITY.md`：优先使用 GitHub Security Advisories 私下报告，禁止在公开 Issue 中发布凭据、私有数据或可利用细节。

### 3.2 GitHub 协作配置

- `.github/CODEOWNERS`：默认由 `@hrygo` 负责审阅。
- `.github/PULL_REQUEST_TEMPLATE.md`：要求说明范围、验证、权限/隐私影响、审计影响和上游依赖。
- `.github/ISSUE_TEMPLATE/bug_report.md`：收集复现步骤、环境和安全/隐私影响。
- `.github/ISSUE_TEMPLATE/feature_request.md`：收集问题背景、设计边界、验收标准和替代方案。
- `.github/ISSUE_TEMPLATE/config.yml`：保留空白 Issue，以便处理不适合模板的设计讨论。

### 3.3 忽略与运行时版本

`.gitignore` 覆盖 macOS、IDE、Python/Node 环境、缓存、构建产物、覆盖率、日志、环境变量和私钥，同时保留现有 `.superpowers/` 忽略规则。新增 `.python-version` 使用 `3.14`，新增 `.nvmrc` 使用 `24`；补丁版本由锁文件和 CI 矩阵固定，不把本地缓存提交进仓库。

## 4. 已选技术栈

### 4.1 后端

- Python `3.14.x`：异步优先，公共函数完整类型标注。
- FastAPI：REST API、OpenAPI 文档和流式端点。
- Pydantic `v2`：请求、响应、配置和外部服务数据的边界校验。
- SQLAlchemy `2.x` + Alembic：异步数据访问与可审查迁移；具体数据库部署在 Slice 1 implementation plan 中固定。
- `uv`：Python 版本、虚拟环境、依赖和锁文件管理。
- Ruff：统一 Python lint 与 format；`mypy --strict` 做类型门禁；pytest 做单元与集成测试。

### 4.2 前端

- React `19.2.x` + TypeScript `6.x`。
- Vite `8.x`：独立 Python API 后端配套的前端构建工具。
- Node.js `24 LTS` + pnpm：前端运行时与依赖管理。
- TanStack Query：服务端状态、缓存和请求生命周期。
- React Router：页面路由；局部交互状态优先使用 React 原生状态，避免早期引入重量级全局状态。
- Vitest + Playwright：组件/单元测试与跨浏览器端到端验收。

### 4.3 跨端契约与实时通信

- FastAPI 生成版本化 OpenAPI；前端从 OpenAPI 生成 TypeScript 类型与客户端，不手工维护两套公共接口模型。
- API 错误统一为结构化错误对象，边界处校验外部输入和第三方响应。
- 流式 Agent 事件优先采用 SSE；需要双向实时控制、取消或连接状态同步时使用 WebSocket。
- 未来代码边界为 `apps/api`、`apps/web`、`packages/api-client`、`tests/e2e`、`docs`、`infra`；本次不创建空目录或空应用。

## 5. Git 工作流与远端操作

1. 保留现有 `main` 分支和历史；先检查 staged/unstaged 差异，确保不覆盖用户改动。
2. 按职责拆分为仓库基线文档/配置提交；提交前检查 staged diff、敏感信息和本地验证结果。
3. 使用 GitHub CLI 创建公开仓库 `hrygo/hikmah`，设置描述和 topics，配置 HTTPS `origin`。
4. 只执行普通 `git push -u origin main`；不使用 `--force`，不删除或覆盖远端已有历史。
5. 推送后通过 GitHub API/CLI 复核公开可见性、默认分支、描述、topics、远端提交和本地干净状态。

GitHub 描述为：

> Hikmah（群贤）— a private human–agent collaboration community for small teams, built around identity, permissions, context, approvals, and auditability.

topics 为：

`ai`、`multi-agent`、`human-ai-collaboration`、`agent-orchestration`、`team-collaboration`、`private-teams`、`agentscope`、`qwenpaw`、`knowledge-management`、`auditability`

## 6. 验收标准

- 本地 `main` 历史仍可追溯，未发生强制重写。
- README 能让新贡献者在不阅读全部设计文档的情况下理解项目定位、当前状态、技术栈和入口文档。
- 不会跟踪 `.env`、私钥、虚拟环境、依赖目录、构建产物和系统缓存。
- Apache-2.0、贡献、安全、行为准则和 GitHub Issue/PR 入口均存在且互相链接。
- GitHub 仓库为公开状态，名称、描述、topics、默认分支和远端提交与本地目标一致。
- 由于当前尚无产品代码，不宣称测试、构建或 CI 已通过；这些门禁在 Slice 1 产生真实代码后建立。

## 7. 依据

版本选择以 2026-08-28 的官方资料为准：Python 3.14 维护版本、React 19.2、Vite 8、Node.js 24 LTS、TypeScript 6.0、FastAPI 0.141.x、uv 项目管理、Ruff lint/format 与 Playwright 测试。具体链接见 README 的技术栈说明与实施记录。
