# CODEX_THREADS

> 文档状态：current

## 目标

记录 Codex 会话、`/new`、`/fork`、`/compact`、自动 compact、subagent thread 和 resume 行为在本项目中的使用规则。

## 规则

- 长任务可以使用 Codex 自动 compact 或手动 `/compact` 继续推进，但关键状态必须写入项目文档。
- `compact_count` 记录在 `docs/ai-dev/concurrency/SESSIONS.md` 和 `docs/ai-dev/orchestration/THREAD_REGISTRY.md`。
- `compact_count >= 2` 时，除小范围收尾外，必须创建 handoff 并优先 `/new` 或 `/fork`。
- 新会话必须读取 handoff 与项目文档，不得只依赖上一会话摘要。
- Fork 用于替代方案探索；`/new` 用于主线任务继续推进。

## 必须同步的文档

- `docs/ai-dev/orchestration/CONTEXT_COMPACTION_POLICY.md`
- `docs/ai-dev/orchestration/THREAD_REGISTRY.md`
- `docs/ai-dev/orchestration/THREAD_HANDOFFS.md`
- `docs/ai-dev/concurrency/SESSIONS.md`
- `docs/codex/CODEX_USAGE_LOG.md`

## 记录表

| Date | Command/event | Thread | compact_count | Reason | Handoff | New thread/fork | Notes |
|---|---|---|---:|---|---|---|---|
