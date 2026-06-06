# MERGE_POLICY

> 文档状态：current

## 目标

定义 side conversation、fork、worktree、subagents 和 changeset 的合并规则。任何并发输出在被主线程采纳前，都不是项目事实。

## 合并前必须检查

- 是否有对应 thread / worktree / subagent / changeset 记录。
- 是否列明改动范围、验证结果、风险和回退方式。
- 是否执行或手工完成 `ai_doc_impact_check.py`。
- 是否执行或手工完成架构边界检查。
- 是否执行或手工完成 `thread_coordination_check.py --strict`。
- 是否存在真实 secret、真实用户隐私数据、未脱敏日志或敏感截图。
- 是否把未确认需求、猜测、探索结论写成了项目事实。
- 是否需要用户确认数据模型、业务规则、状态流、权限或历史数据解释。
- 如果来源线程 `compact_count >= 2`，是否已提供 new-session handoff。
- 如果来源是 subagent，是否符合 `AGENT_ROLE_POLICY.md`。

## 合并决策

| 条件 | 决策 |
|---|---|
| 结果可验证、文档影响明确、无冲突、角色权限合规 | 合并并更新事实文档 |
| 结果有价值但事实未确认 | 写入 pending changeset 或待确认事项 |
| 与当前事实源冲突 | 记录 `CONFLICTS.md`，不得直接覆盖 |
| 缺少测试或验证 | 可合并文档草案，但不得声称已通过 |
| 涉及敏感信息泄露 | 阻断合并，先清理、脱敏、记录风险 |
| 来源线程压缩过多且无 handoff | 阻断合并，先补 handoff 或新会话复核 |
| 无法回退或影响面不清 | 阻断合并，拆分或补充方案 |

## changeset 状态

- `pending`：待评审或待用户确认。
- `merging`：主线程正在合并。
- `merged`：已由主线程采纳并写入事实源。
- `rejected`：明确拒绝，需说明原因。
- `conflict`：存在冲突，必须先处理。

## 合并记录模板

| ID | Date | Source | Source role | compact_count | Decision | Docs updated | Checks | Tests | Rollback | Owner | Notes |
|---|---|---|---|---:|---|---|---|---|---|---|---|
