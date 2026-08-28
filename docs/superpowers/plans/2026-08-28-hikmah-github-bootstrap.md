# Hikmah GitHub Repository Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有 Hikmah 设计阶段仓库整理为公开、可协作的 hrygo/hikmah GitHub 仓库，并保留清晰的 Python + React 实现基线。

**Architecture:** 保留现有 main 历史和设计事实源，在仓库根目录建立公开项目入口，在 .github/ 建立轻量协作入口。当前只添加可运行的文档、许可证、忽略规则和版本标记；真实 API/Web 应用与 CI 在 Slice 1 产生业务代码后再落地。

**Tech Stack:** Python 3.14.x、FastAPI、Pydantic v2、SQLAlchemy 2.x、Alembic、uv、Ruff、mypy、pytest；React 19.2.x、TypeScript 6.x、Vite 8.x、Node.js 24 LTS、pnpm、TanStack Query、React Router、Vitest、Playwright。

**Spec:** docs/superpowers/specs/2026-08-28-hikmah-github-bootstrap-design.md

## Global Constraints

- GitHub 仓库必须是公开的 hrygo/hikmah，许可证为 Apache-2.0。
- 保留现有 main 分支、既有提交和用户已经 staged 的两张招聘海报；不重置、不强推、不删除远端历史。
- 保留执行期间发现的 docs/decisions/、docs/research/ 与设计材料改动原文；不覆盖、不删除、不将其与其他文档混写。
- README 必须说明设计阶段状态、Python + React 技术栈、AgentScope/QwenPaw 上游边界和现有设计文档入口。
- .gitignore 必须覆盖 .env、私钥、虚拟环境、依赖目录、构建产物、缓存、日志和系统文件，并保留 .superpowers/ 规则。
- 不生成没有业务内容的前后端空壳，不添加无法执行的 CI、依赖升级或发布流水线。
- 持久化文档中的命令使用原生 git、gh、rg 等可移植命令，不写入本机 rtk 包装器。
- 任何提交前都要检查 staged diff、敏感信息和 git diff --check；远端只使用普通 git push -u origin main。

---

### Task 1: Add runtime markers and repository-safe ignore rules

**Files:**
- Modify: .gitignore
- Create: .python-version
- Create: .nvmrc

**Interfaces:**
- Consumes: Existing .gitignore entries .DS_Store and .superpowers/.
- Produces: Python 3.14 and Node.js 24 runtime hints, plus ignore rules that prevent local secrets, environments, caches, logs and build output from entering Git.

- [ ] **Step 1: Extend .gitignore without removing existing project rules**

Add sections for operating-system files, IDE files, local environment files, Python artifacts, Node artifacts, build output, test/coverage caches, logs, local temporary files and private keys. Keep .DS_Store and .superpowers/. Allow a safe example environment file with !.env.example.

- [ ] **Step 2: Add runtime version markers**

Create .python-version containing exactly 3.14 and .nvmrc containing exactly 24, each ending with a newline.

- [ ] **Step 3: Verify ignore behavior**

Run:

~~~bash
git check-ignore -v --no-index .env .env.local .venv node_modules dist coverage .DS_Store .superpowers/session.json
git check-ignore -v --no-index .env.example
~~~

Expected: the first command reports every path as ignored; the second command reports no matching ignore rule for .env.example.

- [ ] **Step 4: Verify the diff**

Run:

~~~bash
git diff --check -- .gitignore .python-version .nvmrc
git diff -- .gitignore .python-version .nvmrc
~~~

Expected: no whitespace errors and only the intended ignore/runtime changes.

- [ ] **Step 5: Commit the repository hygiene slice**

~~~bash
git add .gitignore .python-version .nvmrc
git commit --only .gitignore .python-version .nvmrc -m "chore: establish repository hygiene defaults"
~~~

### Task 2: Add license and community health files

**Files:**
- Create: LICENSE
- Create: CONTRIBUTING.md
- Create: CODE_OF_CONDUCT.md
- Create: SECURITY.md

**Interfaces:**
- Consumes: Approved Apache-2.0 license choice and Hikmah design rules for design-first changes, upstream isolation, privacy and auditability.
- Produces: Public contribution, conduct and security entry points that do not invent an email address or promise unavailable support infrastructure.

- [ ] **Step 1: Add the standard Apache License 2.0 text**

Create LICENSE with the unmodified Apache License 2.0 text and the copyright line Copyright 2026 Hikmah contributors.

- [ ] **Step 2: Write contribution guidance for the design-stage repository**

Document the current status, issue/PR workflow, design-first rule, required scope and acceptance criteria, Python/React quality gates for future code, public API/OpenAPI contract expectations, privacy/audit review, and the rule that AgentScope/QwenPaw changes must go through their upstream projects.

- [ ] **Step 3: Add a contributor code of conduct**

Use Contributor Covenant 2.1 text, identify Hikmah maintainers as the enforcement contact, and direct reports to the private security channel when the concern contains a vulnerability.

- [ ] **Step 4: Add the security policy**

State that vulnerabilities must be reported privately through GitHub Security Advisories when available; public Issues must not contain credentials, private data, exploit details or model-private reasoning. Explain that the project is design-stage and response times are not yet committed.

- [ ] **Step 5: Validate the health files**

Run:

~~~bash
rg -n "Apache License|Hikmah contributors|Security Advisories|private|AgentScope|QwenPaw" LICENSE CONTRIBUTING.md CODE_OF_CONDUCT.md SECURITY.md
git diff --cached --check -- LICENSE CONTRIBUTING.md CODE_OF_CONDUCT.md SECURITY.md
~~~

Expected: each required policy phrase is present and the diff has no whitespace errors.

- [ ] **Step 6: Commit the community baseline**

~~~bash
git add LICENSE CONTRIBUTING.md CODE_OF_CONDUCT.md SECURITY.md
git commit --only LICENSE CONTRIBUTING.md CODE_OF_CONDUCT.md SECURITY.md -m "docs: add open source community baseline"
~~~

### Task 3: Configure GitHub collaboration templates

**Files:**
- Create: .github/CODEOWNERS
- Create: .github/PULL_REQUEST_TEMPLATE.md
- Create: .github/ISSUE_TEMPLATE/config.yml
- Create: .github/ISSUE_TEMPLATE/bug_report.md
- Create: .github/ISSUE_TEMPLATE/feature_request.md

**Interfaces:**
- Consumes: @hrygo GitHub identity confirmed by gh auth status and the contribution/security policy from Task 2.
- Produces: Lightweight issue, PR and code-ownership conventions for a public design-stage repository.

- [ ] **Step 1: Add code ownership**

Create .github/CODEOWNERS with a comment explaining the default maintainer and the rule * @hrygo.

- [ ] **Step 2: Add the pull request template**

Require a summary, scope, linked issue/design doc, validation evidence, user-visible impact, permissions/privacy/audit impact, upstream impact, and a checklist confirming no secrets or unrelated changes.

- [ ] **Step 3: Add issue templates and configuration**

Create Markdown templates that collect reproducible evidence for bugs and problem context/acceptance criteria for proposals. Set blank_issues_enabled: true in config.yml so design discussions can still be opened when neither template fits.

- [ ] **Step 4: Verify template references**

Run:

~~~bash
rg -n "@hrygo|validation|privacy|audit|acceptance|blank_issues_enabled" .github
git diff --cached --check -- .github/CODEOWNERS .github/PULL_REQUEST_TEMPLATE.md .github/ISSUE_TEMPLATE/config.yml .github/ISSUE_TEMPLATE/bug_report.md .github/ISSUE_TEMPLATE/feature_request.md
~~~

Expected: owner, validation and scope prompts exist, and blank Issues are explicitly enabled.

- [ ] **Step 5: Commit GitHub collaboration files**

~~~bash
git add .github/CODEOWNERS .github/PULL_REQUEST_TEMPLATE.md .github/ISSUE_TEMPLATE/config.yml .github/ISSUE_TEMPLATE/bug_report.md .github/ISSUE_TEMPLATE/feature_request.md
git commit --only .github/CODEOWNERS .github/PULL_REQUEST_TEMPLATE.md .github/ISSUE_TEMPLATE/config.yml .github/ISSUE_TEMPLATE/bug_report.md .github/ISSUE_TEMPLATE/feature_request.md -m "chore: add GitHub collaboration templates"
~~~

### Task 4: Rewrite the public project README

**Files:**
- Modify: README.md

**Interfaces:**
- Consumes: Existing product name, design-doc links, approved architecture, selected stack, community files, and assets/hikmah-developer-recruitment-card.png.
- Produces: A bilingual GitHub landing page that accurately describes a design-stage project without claiming an implemented product, passing tests or CI.

- [ ] **Step 1: Define the README sections**

Use this order: title and concise positioning, design-stage notice, English summary, current scope, architecture principles, selected stack, documentation links, implementation roadmap, upstream boundaries, contribution/security/license links, and recruitment asset.

- [ ] **Step 2: Add accurate status and technology copy**

State that Hikmah targets invitation-only private teams of 3–20 people; record Python 3.14/FastAPI/Pydantic/uv/Ruff/mypy/pytest and React 19.2/TypeScript 6/Vite 8/Node 24/pnpm/TanStack Query/React Router/Vitest/Playwright; state that OpenAPI drives generated TypeScript clients and SSE/WebSocket are selected by interaction needs.

- [ ] **Step 3: Link every public maintenance entry point**

Link CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, LICENSE, the GitHub issue templates implicitly through GitHub, the architecture spec, the approval/revision record, the source-screen archive, the reuse decisions, and the reuse research. Link the current standalone HTML design book only if it exists at implementation time; do not restore it if the user removes it again.

- [ ] **Step 4: Add the recruitment image with a stable relative path**

Embed assets/hikmah-developer-recruitment-card.png using a relative Markdown path and alt text that describes its purpose.

- [ ] **Step 5: Validate README links and claims**

Run:

~~~bash
rg -n "设计阶段|Python|React|FastAPI|Vite|AgentScope|QwenPaw|CONTRIBUTING|SECURITY|LICENSE|assets/hikmah-developer-recruitment-card.png" README.md
test -f docs/superpowers/specs/2026-08-28-hikmah-design.md
test -f docs/design-book/approval-record.md
test -f docs/design-book/source-screens/README.md
test -f assets/hikmah-developer-recruitment-card.png
git diff --check -- README.md
~~~

Expected: all test commands succeed and the README contains no claim that product code, tests or CI already exist. The standalone HTML design book is not restored or recreated by this task.

- [ ] **Step 6: Commit the README slice**

~~~bash
git add README.md
git commit --only README.md -m "docs: publish Hikmah project overview"
~~~

### Task 5: Commit the user-provided recruitment assets separately

**Files:**
- Include: assets/hikmah-developer-recruitment-card.png
- Include: assets/hikmah-developer-recruitment-card-back.png

**Interfaces:**
- Consumes: The two files already staged by the user; Task 4 references the front image without modifying either file.
- Produces: A separate, reviewable asset commit that preserves the user’s binary files exactly.

- [ ] **Step 1: Confirm only the two expected assets are staged**

~~~bash
git diff --cached --name-status
~~~

Expected: exactly the two assets/hikmah-developer-recruitment-card*.png paths are listed.

- [ ] **Step 2: Commit the staged assets without re-staging other files**

~~~bash
git commit --only assets/hikmah-developer-recruitment-card.png assets/hikmah-developer-recruitment-card-back.png -m "docs: add developer recruitment assets"
~~~

- [ ] **Step 3: Verify the asset commit**

~~~bash
git show --stat --oneline --summary HEAD
git status --short --branch
~~~

Expected: the latest commit contains exactly the two PNG assets and the worktree has no unexpected staged files.

### Task 6: Publish the existing reuse-first architecture revision

**Files:**
- Include: docs/decisions/0001-reuse-first-thin-control-plane.md
- Include: docs/decisions/0002-collaboration-foundation-spike.md
- Include: docs/research/2026-08-28-github-reuse-landscape.md
- Include: docs/design-book/approval-record.md
- Include: docs/design-book/hikmah-design-book.html (modified by the user; preserve its current content)
- Include: docs/superpowers/specs/2026-08-28-hikmah-design.md

**Interfaces:**
- Consumes: Three untracked project documents and three concurrent user changes; their current statuses remain visible, their contents are not edited, and the current HTML modification is retained.
- Produces: A separate, reviewable documentation commit so the public repository preserves the reuse-first evidence, proposed Foundation Reuse Spike, revised approval record, current design book and current architecture specification.

- [ ] **Step 1: Confirm the exact pre-existing document set**

~~~bash
git status --short -- docs/decisions docs/research docs/design-book/approval-record.md docs/design-book/hikmah-design-book.html docs/superpowers/specs/2026-08-28-hikmah-design.md
~~~

Expected: exactly three untracked Markdown paths, two modified Markdown paths and one modified HTML path are listed; do not stage any other path in this task.

- [ ] **Step 2: Scan the documents before publication**

~~~bash
rg -n "BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|gh[pousr]_[A-Za-z0-9_]+|api[_-]?key[[:space:]]*=" docs/decisions docs/research
git diff --text -G "BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|gh[pousr]_[A-Za-z0-9_]+|api[_-]?key[[:space:]]*=" -- docs/design-book/approval-record.md docs/design-book/hikmah-design-book.html docs/superpowers/specs/2026-08-28-hikmah-design.md
git diff --check -- docs/decisions docs/research docs/design-book/approval-record.md docs/design-book/hikmah-design-book.html docs/superpowers/specs/2026-08-28-hikmah-design.md
~~~

Expected: the secret scan has no matches and the whitespace check has no errors; the current HTML modification remains visible.

- [ ] **Step 3: Commit only the six named paths**

~~~bash
git add docs/decisions/0001-reuse-first-thin-control-plane.md docs/decisions/0002-collaboration-foundation-spike.md docs/research/2026-08-28-github-reuse-landscape.md docs/design-book/approval-record.md docs/design-book/hikmah-design-book.html docs/superpowers/specs/2026-08-28-hikmah-design.md
git commit --only docs/decisions/0001-reuse-first-thin-control-plane.md docs/decisions/0002-collaboration-foundation-spike.md docs/research/2026-08-28-github-reuse-landscape.md docs/design-book/approval-record.md docs/design-book/hikmah-design-book.html docs/superpowers/specs/2026-08-28-hikmah-design.md -m "docs: publish reuse-first architecture revision"
~~~

- [ ] **Step 4: Verify the decision/research commit**

~~~bash
git show --stat --oneline --summary HEAD
git status --short --branch
~~~

Expected: the latest commit contains exactly the six named paths, including the current HTML modification; the recruitment assets were already committed separately in Task 5; and no unrelated file is staged.

### Task 7: Create the public GitHub repository and publish metadata

**Files:**
- Modify: .git/config via GitHub CLI remote setup
- Remote: https://github.com/hrygo/hikmah.git

**Interfaces:**
- Consumes: A committed local main branch, authenticated GitHub CLI account hrygo, and the exact description/topics from the approved spec.
- Produces: A public GitHub repository with origin, description, topics, and main as its initial default branch.

- [ ] **Step 1: Confirm the target repository is still absent**

~~~bash
gh repo view hrygo/hikmah --json name,visibility,description,url,defaultBranchRef,isEmpty
~~~

Expected: GitHub reports that the repository cannot be resolved. If it already exists, stop before any create or push operation and inspect its default branch/history.

- [ ] **Step 2: Create the public repository from the local source**

~~~bash
gh repo create hrygo/hikmah --public --source=. --remote=origin --description "Hikmah（群贤）— a private human–agent collaboration community for small teams, built around identity, permissions, context, approvals, and auditability."
~~~

Expected: GitHub creates the public repository and configures origin; the command must not initialize a second local history.

- [ ] **Step 3: Set the approved topics**

~~~bash
gh repo edit hrygo/hikmah --add-topic ai --add-topic multi-agent --add-topic human-ai-collaboration --add-topic agent-orchestration --add-topic team-collaboration --add-topic private-teams --add-topic agentscope --add-topic qwenpaw --add-topic knowledge-management --add-topic auditability
~~~

Expected: the command succeeds without changing source files or local history.

- [ ] **Step 4: Push the existing main branch**

~~~bash
git push -u origin main
~~~

Expected: the existing local commits are uploaded; no force option is used.

### Task 8: Verify the published repository and local acceptance criteria

**Files:**
- Verify: README.md, .gitignore, LICENSE, community files, .github/*, .python-version, .nvmrc
- Verify remote: hrygo/hikmah

**Interfaces:**
- Consumes: All committed slices and the remote created in Task 7.
- Produces: Fresh evidence for local history, working-tree state, remote metadata, topics, default branch and published commit.

- [ ] **Step 1: Verify local history and cleanliness**

~~~bash
git status --short --branch
git log --oneline --decorate -5
git remote -v
~~~

Expected: branch is main tracking origin/main; existing commit 2a8611f remains in history; origin uses HTTPS; and no uncommitted change introduced by this plan remains. Any pre-existing user change is listed separately and is not overwritten.

- [ ] **Step 2: Verify repository files and secret exclusions**

~~~bash
git ls-files
git check-ignore -v --no-index .env .env.local .venv node_modules dist coverage .DS_Store
git grep -n -I -E "BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|gh[pousr]_[A-Za-z0-9_]+|api[_-]?key[[:space:]]*=" -- ':!docs/superpowers/specs/*'
~~~

Expected: required files are tracked, local-only paths are ignored, and the secret scan returns no matches. The current design-book state is preserved; any intentional documentation mention must be reviewed rather than silently ignored.

- [ ] **Step 3: Verify remote metadata and publication**

~~~bash
gh repo view hrygo/hikmah --json name,visibility,description,url,defaultBranchRef,isEmpty,repositoryTopics
gh api repos/hrygo/hikmah/commits/main --jq '.sha'
~~~

Expected: name is hikmah, visibility is PUBLIC, description and all ten topics match the approved spec, default branch is main, repository is non-empty, and the remote commit SHA equals local git rev-parse HEAD.

- [ ] **Step 4: Re-run whitespace and link existence checks**

~~~bash
git diff --check
test -f README.md
test -f LICENSE
test -f CONTRIBUTING.md
test -f CODE_OF_CONDUCT.md
test -f SECURITY.md
test -f .github/CODEOWNERS
test -f .github/PULL_REQUEST_TEMPLATE.md
~~~

Expected: all checks exit successfully. Because this repository has no product code yet, report that no application tests/build were run rather than claiming they pass. Pre-existing user changes are not treated as failures of this plan.

- [ ] **Step 5: Record the final change summary**

Report the files changed, the intentional non-changes (no product code, no CI, no upstream edits), the commit hashes, the GitHub URL, metadata, and any residual limitation such as CI being deferred until Slice 1.
