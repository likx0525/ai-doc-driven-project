# LOCKS.md

> 文档状态：stub

## 目标

记录核心文档、任务、模块的临时编辑锁，减少并发编辑冲突。

## 锁类型

- `read`：只读
- `write`：准备修改
- `merge`：正在合并
- `review`：正在审查

## 锁状态

- `active`：有效
- `released`：已释放
- `stale`：疑似过期

## 当前锁

| 锁编号 | 会话 | 文件/任务/模块 | 锁类型 | 开始时间 | 状态 | 说明 |
|---|---|---|---|---|---|---|

## 加锁规则

1. 修改核心文档前必须检查 `LOCKS.md`。
2. 同一核心文档同一时间只能有一个 active write 锁。
3. write 锁与 merge 锁不能同时作用于同一文件/任务/模块。
4. 如果已有 active write 或 merge 锁，不得直接修改该目标。
5. 可以写入 changeset，等待主线程合并。
6. 锁使用完成后必须标记 released。
7. 疑似过期锁不得直接删除，应标记 stale，并在 `CONFLICTS.md` 中记录。
8. 合并前运行 `python scripts/thread_coordination_check.py --strict --record`。
