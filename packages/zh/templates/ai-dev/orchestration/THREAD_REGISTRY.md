# THREAD_REGISTRY

> 文档状态：stub

## 目标

登记主线程、side conversation、fork、worktree、subagents 和 automation 线程，确保每个并发输出都有来源、范围、状态、压缩次数和合并去向。

## 线程状态

- `active`：进行中。
- `handoff-ready`：已准备交接，等待主线程采纳。
- `merged`：已由主线程采纳并写入事实源或 changeset。
- `rejected`：已拒绝。
- `stale`：疑似过期，需要确认。
- `closed`：关闭，不再继续。

## 记录规则

1. 主线程应至少登记一次。
2. 使用 `/new`、`/fork`、side conversation、worktree 或 subagent 时必须新增记录。
3. 每次 compact 后必须更新 `compact_count`。
4. `compact_count >= 2` 的线程不得继续承接新开发任务，除非只做收尾或 handoff。
5. 任何非主线程输出被采纳前，必须关联 `THREAD_HANDOFFS`、`MERGE_QUEUE` 或 changeset。

## 线程登记表

| Thread ID | Date | Role | Mode | Scope | Owner | compact_count | Status | Handoff | Merge target | Notes |
|---|---|---|---|---|---|---:|---|---|---|---|
