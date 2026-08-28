# Hikmah（群贤）

Hikmah 是一个面向 3–20 人私有团队的人机协作社区。人类成员与专业 Agent 在团队、频道、线程和临时群聊中按明确规则共同工作。

当前仓库处于设计阶段，尚未开始产品代码实现。

## 设计文档

- [产品与技术架构设计](docs/superpowers/specs/2026-08-28-hikmah-design.md)
- [自包含 HTML 设计册](docs/design-book/hikmah-design-book.html)
- [设计批准记录](docs/design-book/approval-record.md)
- [交互画布源材料](docs/design-book/source-screens/README.md)

## 上游边界

Hikmah 通过公开接口集成 AgentScope 与 QwenPaw。原则上不修改两个上游仓库；确需补充通用扩展点时，修改必须作为最小 PR 提交到对应上游，并在正式发布后由 Hikmah 固定版本使用。
