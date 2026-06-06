# CONTEXT_COMPACTION_POLICY

> 文档状态：current

## 目标

控制 Codex 长会话的上下文压缩次数，避免关键事实只存在于压缩摘要中。压缩可以延长工作线程，但不能替代项目文档、handoff 和任务状态记录。

## 术语

- `compact_count`：当前 Codex 线程已经发生的上下文压缩次数，包括手动 `/compact` 和可确认的自动 compact。
- `compaction event`：一次 `/compact`、自动 compact、或已知的上下文摘要替换事件。
- `migration threshold`：达到后必须准备迁移到新会话或 fork 的阈值。
- `new-session handoff`：为新会话准备的最小上下文包。

## 压缩阈值

| compact_count | 等级 | 处理规则 |
|---:|---|---|
| 0 | normal | 正常继续。 |
| 1 | watch | 可以继续，但必须更新 `PROJECT_STATE`、`tasks`、关键 `decisions`、风险和下一步。 |
| 2 | migration | 进入迁移阈值。除小范围收尾外，必须创建 handoff，并优先 `/new` 或 `/fork`。 |
| >= 3 | stop-new-work | 不得继续承担新开发、架构重构、数据迁移、安全排查或发布任务；只能整理 handoff、更新文档并切换新会话。 |

高风险任务的阈值更低：安全、隐私、凭据、数据迁移、生产发布、历史数据解释、复杂架构重构，在 `compact_count >= 1` 时即应优先新开会话。

## 每次压缩前

压缩前必须尽量完成：

1. 更新 `docs/ai-dev/concurrency/SESSIONS.md` 中当前会话的 `compact_count`、当前目标和下一步。
2. 更新 `docs/ai-dev/tasks.md`：已完成、进行中、阻塞项。
3. 更新 `docs/ai-dev/decisions.md`：已确认决策；未确认事项不得写成事实。
4. 若存在并发或长任务，更新 `THREAD_HANDOFFS.md`。
5. 运行或安排运行：

```bash
python scripts/thread_coordination_check.py --event PreCompact --record
```

## 每次压缩后

压缩后继续工作前必须：

1. 重新读取 `AGENTS.md`、`PROJECT_STATE.md`、`tasks.md`、`decisions.md` 和相关专项文档。
2. 不把压缩摘要中的内容直接当成事实；必须核对 `docs/` 或代码证据。
3. 增加 `compact_count` 并记录压缩原因。
4. 运行或安排运行：

```bash
python scripts/thread_coordination_check.py --event PostCompact --record
```

## 新会话 handoff 最小内容

当达到迁移阈值时，旧会话必须给新会话留下：

```text
来源线程：TH-YYYYMMDD-001
compact_count：2+
任务目标：
已完成：
未完成：
关键事实源：
已确认决策：
未确认事项：
已修改文件：
已运行检查：
未运行检查及原因：
风险：
下一步建议：
```

新会话启动后必须先读 handoff 和项目文档，而不是只读上一线程的摘要。

## `/new` 与 `/fork` 选择

- 任务继续沿主线推进，且不需要保留旧上下文分叉探索：优先 `/new`。
- 需要保留当前线程作为对照，探索替代方案：使用 `/fork`。
- 使用 subagents 并行审查时，主线程必须等待结果并汇总，不得让子线程直接归档项目事实。

## 记录表

| Thread ID | Date | compact_count | Event | Reason | Handoff | New session / fork | Status | Notes |
|---|---|---:|---|---|---|---|---|---|

## v0.3.2 补充：hooks 不写运行记录

`PreCompact`、`PostCompact`、`Stop`、`SubagentStop` 默认只运行 `--hook-json --advisory`。只有人工合并检查或 CI 才使用 `--record` 写入 `TC-*`。
