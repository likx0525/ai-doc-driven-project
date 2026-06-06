# MERGE_QUEUE.md

> 文档状态：stub

## 目标

记录待合并、合并中、已合并、被拒绝或存在冲突的 changeset / handoff / subagent 输出。

## 合并状态

- `pending`：待合并
- `merging`：合并中
- `merged`：已合并
- `rejected`：已拒绝
- `conflict`：存在冲突
- `blocked`：被测试、文档、权限、角色或 compact_count 问题阻断

## 合并队列

| Changeset | 来源会话 | 来源角色 | 来源任务 | compact_count | 状态 | 目标文档 | 是否冲突 | 必需检查 | 处理结论 |
|---|---|---|---|---:|---|---|---|---|---|
