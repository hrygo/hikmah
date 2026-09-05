---
title: Hikmah 目标版本与发布基线
description: 规定 Hikmah 正式架构的目标组件版本、版本事实源、兼容性支持和许可证发布门禁。
document_type: architecture-overview
status: active
created: 2026-08-28
updated: 2026-08-28
review_after: 2026-09-28
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - architecture
  - versions
  - compatibility
  - licensing
canonical: true
related:
  - ../../README.md
  - ../decisions/0003-adopt-mattermost-as-collaboration-foundation.md
  - ../decisions/0005-public-integration-contracts-and-fail-closed-semantics.md
  - ../decisions/0006-governance-metadata-persistence-and-schema-lifecycle.md
  - ../project/prd-architecture-review-tracker.md
---

# Hikmah 目标版本与发布基线

本文是目标版本口径的唯一事实源。产品规范只引用本页，不重复维护易变化版本。版本进入表中表示正式目标，不表示当前脚手架 manifest 已对齐，也不表示兼容、升级或许可证门禁已经通过。

## 1. 目标基线快照

| 组件 | 目标版本 | 用途与边界 |
|---|---|---|
| Mattermost Team Edition | `v11.10.1` | 协作数据面、身份、Web/Desktop/Mobile UI 与 Web App Plugin 宿主 |
| mattermost-plugin-agents | `v2.6.0` | 只读参考 Custom Post、权限与 Agent UX；不作为 Hikmah Runtime |
| QwenPaw | `v2.2.0-beta.1` | Shared Expert、Personal Agent、Channel、Workspace、工具与治理运行时 |
| AgentScope | `v2.0.7.post1` | Team/Channel Coordinator、ChannelBase、Team 与 HITL 运行语义 |
| PostgreSQL | `16` | Mattermost 与 Hikmah 的独立数据库；不得共用 database/schema/role |
| Python | `>=3.14,<3.15` | Hikmah API 与控制面目标运行时 |
| React | `19.2.x` | Mattermost Web App Plugin 产品 UI |
| TypeScript | `6.0.x` | Web 与共享 API Client 类型系统 |
| Vite | `8.x` | Plugin bundle 与开发预览构建 |
| Node.js | `24 LTS` | Web 构建与测试运行时 |
| pnpm | `11.21.x` | Monorepo Node 包管理器 |

本地只读参考仓库使用 Monorepo 根目录相对路径 `../mattermost`、`../mattermost-plugin-agents`、`../QwenPaw`、`../agentscope` 与 `../zulip`。固定 tag、commit、工作树清洁状态与调研时点记录在[整合调研](../research/2026-08-28-mattermost-zulip-webui-integration.md)；发布 BOM 必须以 lockfile、容器 digest 和 SBOM 补足精确解析版本。

## 2. 版本语义

- **目标版本**：正式设计要求实现和验证的版本；脚手架依赖可以暂时不同，但不得据此宣称兼容。
- **已验证版本**：目标版本完成契约、安全、端到端、备份恢复和升级测试后，才进入发布支持矩阵。
- **支持版本**：维护者明确承诺安全更新和问题复现的已验证版本；每个 release 只有一个权威 BOM。
- **参考版本**：用于 Borrow 源码、交互或测试模式，不形成运行依赖。

README badge、贡献指南和 AGENTS 只能摘要本页，并必须注明“目标基线”。manifest/lockfile 与本页不一致时，发布门禁失败；不得静默修改文档或降低依赖来掩盖差异。

## 3. 兼容与升级规则

1. 所有外部组件固定 tag/version 和容器 digest，禁止浮动 `latest`。
2. 目标 patch/minor 升级先在隔离环境运行契约、权限、Plugin、数据迁移和核心旅程测试。
3. Mattermost 升级必须验证 Plugin 安装/禁用、Custom Post 文本降级、REST/WebSocket/OAuth 与 QwenPaw Channel。
4. QwenPaw/AgentScope 升级必须验证公开 API、SSE/event schema、session、取消、错误与 HITL 状态。
5. 每次升级保留已验证前一版本的回退制品、数据库恢复点和操作步骤。
6. 未通过矩阵的版本标记 `unsupported`；“基于公开扩展点”不等于自动兼容或无缝升级。

## 4. 许可证、品牌与供应链门禁

- 工程调研只记录许可证和商标风险，不构成法律意见，也不使用“已经合规”作为结论。
- 每种目标分发方式必须记录 Mattermost edition、源码/二进制/容器来源、插件分发、品牌呈现、商业用途和修改情况，并由有权负责人完成许可证与商标复核。
- 法律/品牌复核未通过时不得发布相应分发物；必要时执行 ADR-0003 的退出路径并重新评估 Zulip/独立 UI。
- 每个 release 生成 SBOM、许可证清单、依赖来源/校验值和安全公告复核记录。
- Node/Python 安装使用锁文件与冻结模式；依赖脚本默认阻断，只批准经审查的最小集合。

## 5. 发布证据

正式支持一个版本组合至少需要：

- 可复现构建与容器 digest；
- Mattermost/QwenPaw/AgentScope 契约测试；
- 核心旅程、身份隔离和 fail-closed 安全测试；
- Plugin 安装、禁用、升级和回退证据；
- PostgreSQL 迁移、备份与恢复证据；
- SBOM、许可证/品牌复核记录；
- NFR 测量报告及已知偏差。

证据缺失时，状态只能是 `target` 或 `evidence-needed`，不能标记为 supported、validated、production-ready 或等价终态。
