# THREAD_COORDINATION

> 文档状态：current

## 目标

定义主线程如何协调其他会话、fork、worktree、subagents 和 automation。

## 协调原则

1. 主线程是唯一最终事实收口方。
2. 并发线程必须有 `THREAD_REGISTRY` 记录。
3. 每个非主线程任务必须有明确工作包或审查范围。
4. 输出默认是候选结论，必须通过 handoff 和 merge policy 才能进入事实源。
5. 压缩次数必须记录，达到迁移阈值后应新开会话。
6. 核心文档修改必须检查 `LOCKS.md`。
7. 合并前必须检查 `MERGE_QUEUE.md` 和 `CONFLICTS.md`。

## 主线程检查清单

- [ ] 是否登记当前线程和角色？
- [ ] 是否有 active write / merge 锁冲突？
- [ ] 是否有 pending / conflict changeset？
- [ ] 是否有 compact_count >= 2 的线程仍在承担新任务？
- [ ] 是否有 subagent 输出缺少 handoff？
- [ ] 是否运行 `thread_coordination_check.py`？

## 同步记录

| Date | Coordinator | Threads synced | compact_count issues | Locks | Merge queue | Decision | Notes |
|---|---|---|---|---|---|---|---|
