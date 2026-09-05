---
title: Hikmah 文档治理与 Metadata 规范
description: 定义 Hikmah 文档目录、metadata 字段、状态生命周期、事实源和维护规则。
document_type: documentation-policy
status: active
created: 2026-08-28
updated: 2026-08-28
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - documentation
  - governance
  - metadata
canonical: true
related:
  - ../README.md
  - ../architecture/version-baseline.md
  - prd-architecture-review-tracker.md
---

# Hikmah 文档治理与 Metadata 规范

## 1. 目标

文档应让读者快速确认三件事：这份文档解决什么问题、当前是否仍然有效、哪一份文件拥有最终解释权。目录负责可发现性，metadata 负责机器可读状态，Git 历史负责版本追溯。

Hikmah 在产品成熟前采用生命周期与用途分层；教程、How-to、Reference、Explanation 等 [Diátaxis](https://www.diataxis.fr/) 类型在出现真实用户任务后逐步引入，不预建空目录。

## 2. 文件位置

- GitHub 原生入口保留在仓库根目录：`README.md`、`CONTRIBUTING.md`、`SECURITY.md`、`CODE_OF_CONDUCT.md`、`LICENSE`。
- 产品、架构、决策、研究、设计和开发文档统一存放在 `docs/`。
- 已完成、已替代或只用于追溯的材料移入 `docs/archive/`，不删除历史 ADR。
- 工具专属路径不得成为长期信息架构，例如 `docs/superpowers/`。

## 3. Markdown Metadata

所有 `docs/**/*.md` 必须以 YAML front matter 开头：

```yaml
---
title: 文档标题
description: 一句话说明文档用途
document_type: product-spec
status: review
created: 2026-08-28
updated: 2026-08-28
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - product
canonical: true
related:
  - ../decisions/0001-reuse-first-thin-control-plane.md
---
```

### 3.1 必填字段

| 字段 | 含义 |
|---|---|
| `title` | 人类可读标题，应与正文一级标题一致或语义等价 |
| `description` | 一句话说明用途和边界 |
| `document_type` | 文档类型，使用下节定义的稳定值 |
| `status` | 当前生命周期状态 |
| `created` | 首次创建日期，ISO `YYYY-MM-DD` |
| `updated` | 最后一次实质更新日期，ISO `YYYY-MM-DD` |
| `owners` | 负责维护和复核的角色或团队 |
| `audience` | `users`、`contributors`、`maintainers` 等目标读者 |
| `tags` | 低基数主题标签，不重复目录层级 |
| `canonical` | 是否为该主题的唯一事实源 |

### 3.2 可选字段

- `related`：强相关文档的相对路径。
- `supersedes`：当前文档明确替代的文档。
- `superseded_by`：替代当前文档的文档；与 `status: superseded` 同时使用。
- `review_after`：需要重新核验的日期，适合外部版本和许可调研。

### 3.3 文档类型

稳定类型包括：

- `documentation-index`
- `documentation-policy`
- `product-spec`
- `architecture-overview`
- `architecture-decision`
- `research-report`
- `design-record`
- `development-guide`
- `implementation-plan`
- `archive-index`
- `archived-artifact`

新增类型前应先确认现有类型无法准确表达用途，避免同义词扩散。

## 4. 状态生命周期

通用状态如下：

```text
draft → review → proposed → accepted / active → completed
                              │          │
                              └──────────┴→ superseded / deprecated / archived
```

| 状态 | 适用语义 |
|---|---|
| `draft` | 尚未完成，不能作为实现依据 |
| `review` | 内容完整，等待负责人复核 |
| `proposed` | 有明确候选决定，尚未接受；主要用于 ADR |
| `accepted` | 决策已经接受；主要用于 ADR |
| `active` | 当前有效的说明、导航、规则或记录 |
| `in-progress` | 正在执行的计划 |
| `completed` | 计划或一次性交付已完成，仍可能保留在活动区 |
| `superseded` | 已被另一份文档替代，必须填写 `superseded_by` |
| `deprecated` | 仍可读取但不应继续采用 |
| `archived` | 只用于历史追溯，不作为当前实现依据 |

ADR 遵循 `proposed → accepted → superseded/deprecated`；不删除旧 ADR。研究报告通常使用 `review`、`active` 或 `archived`，并在外部依赖易变化时设置 `review_after`。

## 5. HTML Metadata

完整 HTML 文档在 `<head>` 中使用：

```html
<meta name="hikmah:title" content="文档标题">
<meta name="hikmah:document-type" content="design-record">
<meta name="hikmah:status" content="review">
<meta name="hikmah:created" content="2026-08-28">
<meta name="hikmah:updated" content="2026-08-28">
<meta name="hikmah:canonical" content="false">
```

不能独立渲染的 HTML 源片段在首行使用 `<!-- hikmah-document-metadata ... -->` 注释。校验清单、哈希 manifest 和图片不是文档，不添加伪 metadata。

## 6. 事实源和引用

- 一个主题最多只有一份 `canonical: true` 文档。
- 导航页必须使用 `canonical: false`，只摘要并链接事实源。
- 研究报告提供证据，不自动把建议升级为已接受决策。
- ADR 记录“为什么决定”，产品规范记录“系统应当怎样表现”。两者冲突时，更新较新的 Accepted ADR 和产品事实源必须在同一个变更中对齐。
- 内部引用使用相对路径；不引用本机绝对路径作为读者入口。

### 6.1 终态规范与交付证据

- 产品规范、架构导航和 Accepted ADR 使用确定性的规范语言描述目标终态，不因当前脚手架缺失而降低要求。
- `Accepted` 表示决定已接受；`active` 表示文档当前有效。二者都不自动表示代码已经实现、运行门禁已经通过或 release 已受支持。
- 当前实现、授权、运行、升级、恢复、许可证/品牌和 NFR 证据由[审查跟踪表](prd-architecture-review-tracker.md)管理。
- 正式文档不得使用“已合规”“无缝升级”“生产就绪”等需要外部证据的完成态语言，除非同段链接适用范围明确的验证记录。
- 研究报告保留快照时点的建议与候选语言；后续决定用顶部“后续决议”说明关联 ADR，不静默改写原始证据。
- 历史归档保持原文，不参与当前状态统计；入口必须明确其非事实源地位。

## 7. 变更维护

- 内容发生实质变化时更新 `updated`；仅移动文件或修正拼写可保持原日期。
- 状态变化必须在同一提交中更新入口页的状态总览。
- 移动文档必须同时修复根 README、目录入口、Markdown 和 HTML 链接。
- 归档文档保持原文；只允许补 metadata、归档说明和已失效链接的明确标注。
- 提交前检查 front matter、相对链接、HTML metadata、`git diff --check` 和敏感信息。
