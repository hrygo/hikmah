---
title: Hikmah 知识协作试点可行性核验
description: 记录固定 QwenPaw 版本的信任边界、提及函数实验与公开 Hook 证据，区分设计推断和真实联调缺口。
document_type: research-report
status: completed
created: 2026-09-05
updated: 2026-09-05
review_after: 2026-10-05
owners:
  - hikmah-maintainers
audience:
  - contributors
  - maintainers
tags:
  - research
  - knowledge
  - integration
canonical: false
related:
  - ../product/overview.md
  - ../decisions/0007-knowledge-collaboration-pilot-and-runtime-boundaries.md
  - ../project/prd-architecture-review-tracker.md
---

# Hikmah 知识协作试点可行性核验

## 1. 核验范围

日期：2026-09-05。Hikmah 基线为 `8ea48c2`；本地只读参考 `../QwenPaw` 位于 `v2.2.0-beta.1`（commit 前缀 `8ff77893`），检查时工作树清洁；`../mattermost` 为 `v11.10.1`。未更新上游、启动服务、调用模型或执行真实用户任务。

结构查询使用代码图谱 Tier 2 定位，再读取关键源码；QwenPaw 相关文件覆盖检查均为 `metadata_match`，没有记录到解析缺口，此信号不证明完整性。Hikmah 文档不在图谱索引范围，采用直接读取。本轮观察仅适用于固定版本及列出的边界，不推导为上游漏洞、完整运行证明或最新版本保证。

## 2. 已确认的证据

| 证据 | 当前结论 | 边界 |
|---|---|---|
| [QwenPaw SECURITY.md](https://github.com/agentscope-ai/QwenPaw/blob/v2.2.0-beta.1/SECURITY.md) | 同一实例的调用者共享已授予该实例的权限；session 不是用户授权边界 | 共享业务专家可以成立，但须按信任域部署，不能混入个人数据 |
| [Hub 文档](https://github.com/agentscope-ai/QwenPaw/blob/v2.2.0-beta.1/website/public/docs/hub.zh.md) | 面向可信内部团队，按用户隔离进程/容器；服务器管理员可访问服务器、数据库和备份 | 不支持由产品 owner-only 推导防运维读取，也不据此承诺强对抗多租户 |
| [长期记忆文档](https://github.com/agentscope-ai/QwenPaw/blob/v2.2.0-beta.1/website/public/docs/memory.zh.md) | Workspace 文件与 ReMe 包含自动记忆及可检索知识 | Thread 分会话不能单独证明跨频道长期记忆隔离 |
| [Mattermost Channel](https://github.com/agentscope-ai/QwenPaw/blob/v2.2.0-beta.1/src/qwenpaw/app/channels/mattermost/channel.py) | `_is_triggered` 排除自身发送者，并用用户名子串判断提及；事件处理先获取上下文，再交给运行时 | 函数级行为见第 3 节；后续 ACL 或运行时仍可能拒绝，不将触发等同于最终执行 |
| [PluginApi](https://github.com/agentscope-ai/QwenPaw/blob/v2.2.0-beta.1/src/qwenpaw/plugins/api.py) | 公开 `register_runtime_hook` 与 `register_channel` 存在 | 注册接口存在不表示部署、重载和入口覆盖已验证 |
| [Runtime](https://github.com/agentscope-ai/QwenPaw/blob/v2.2.0-beta.1/src/qwenpaw/runtime/runtime.py)、[HookRegistry](https://github.com/agentscope-ai/QwenPaw/blob/v2.2.0-beta.1/src/qwenpaw/runtime/hooks.py) | `PRE_DISPATCH` 先于命令分发及模型构建；`SHORT_CIRCUIT` 可返回，Hook 异常不由 Registry 吞掉 | 可作为准入扩展候选；前置上下文读取、短路输出与整体故障行为待联调 |
| [审批入口](https://github.com/agentscope-ai/QwenPaw/blob/v2.2.0-beta.1/src/qwenpaw/app/routers/approval.py) | 入口校验 request 与 root session，解析审批范围并请求服务完成审批 | 不能从 session 校验推导 Mattermost 人类角色授权；精确参数、身份与重放仍需契约测试 |

Mattermost 官方 [OAuth 说明](https://developers.mattermost.com/integrate/apps/authentication/oauth2/)说明支持 PKCE；[插件说明](https://developers.mattermost.com/integrate/plugins/overview/)将 Web App 与原生移动插件能力区分。上述网页于核验日期读取，不能代替固定部署版本测试。

## 3. 原生触发函数实验

从目标文件的 AST 提取原始 `_is_triggered`，只提供函数所需的对象字段，未导入或启动 QwenPaw。`channel_type=P`、`thread_follow=False`，目标 Bot 为 `expert_a` / `expert`：

| 输入 | 函数结果 |
|---|---|
| 人类消息 `@expert question` | `True` |
| 另一 Bot 消息 `@expert continue` | `True` |
| 人类消息 `@expert2 question` | `True` |
| 人类代码示例中的 `@expert` | `True` |
| 目标 Bot 自己发送 `@expert continue` | `False` |
| 普通消息 `hello` | `False` |

复现命令（从 Hikmah 仓库根目录运行，保持只读参考 checkout）：

```bash
python3 - <<'PY'
import ast
from pathlib import Path
from types import SimpleNamespace

path = Path('../QwenPaw/src/qwenpaw/app/channels/mattermost/channel.py')
tree = ast.parse(path.read_text())
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
           and n.name == 'MattermostChannel')
fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
          and n.name == '_is_triggered')
namespace = {}
exec(compile(ast.Module(body=[fn], type_ignores=[]), str(path), 'exec'), namespace)
bot = SimpleNamespace(_bot_id='expert_a', _bot_username='expert',
                      _thread_follow=False, _participated_threads=set())
cases = [('human', '@expert question'), ('expert_b', '@expert continue'),
         ('human', '@expert2 question'), ('human', 'example: `@expert`'),
         ('expert_a', '@expert continue'), ('human', 'hello')]
for sender, message in cases:
    print(sender, repr(message), namespace['_is_triggered'](
        bot, {'user_id': sender, 'message': message}, 'P'))
PY
```

该实验不证明真实群聊一定形成循环；它证明仅靠原生提及筛选不足以保证 Hikmah 的准确目标与一层邀请规则。仍须覆盖完整入口、ACL、Hook、并发预算及发帖回流。

## 4. 设计推断与待证事项

获批方向为：保持原生 Channel，优先验证公开 Hook 的确定性准入；按频道信任域隔离记忆与执行；知识检索和回答同时约束目标受众；用首批真实任务验证问答和方案协作价值。

这些都是待实施的设计要求。尚未验证：Hook 缺失时拒绝工作、所有入口覆盖、读取隔离、准确提及解析、并发与重启预算、知识撤回传播、审批身份、真实任务效果、资源成本、完整插件安装、升级/恢复和分发许可。对应关闭条件见 AR-009～AR-012，既有 AR-001/004/007 继续开放。
