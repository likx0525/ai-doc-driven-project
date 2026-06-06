# THREAD_SYNC_LOG

> 文档状态：stub

## 目标

记录主线程与其他线程、subagents、worktree、fork 之间的同步事件。

## 同步事件类型

- `session-start`
- `pre-compact`
- `post-compact`
- `handoff-created`
- `subagent-start`
- `subagent-stop`
- `merge-start`
- `merge-complete`
- `conflict-detected`
- `new-session-start`

## 记录表

| Date | Event | Source thread | Target thread | compact_count | Files / scope | Result | Notes |
|---|---|---|---|---:|---|---|---|
