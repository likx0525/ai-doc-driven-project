# THREAD_HANDOFFS

> 文档状态：stub

## 目标

记录线程、subagent、worktree、fork、压缩迁移和人工交接的 handoff。handoff 是主线程合并和新会话继续工作的最低上下文包。

## Handoff 状态

- `draft`：草稿，尚不完整。
- `ready`：可供主线程或新会话接收。
- `accepted`：已被主线程采纳。
- `rejected`：拒绝采纳。
- `superseded`：被后续 handoff 替代。

## Handoff 模板

```text
Handoff ID：HO-YYYYMMDD-001
来源线程 / worktree / subagent：
来源角色：coordinator / worker / reviewer / explorer / subagent / automation
compact_count：0 / 1 / 2 / 3+
任务范围：
已完成：
未完成：
关键事实源：
已确认决策：
未确认事项：
已修改文件：
已运行检查：
未运行检查及原因：
风险：
敏感信息检查：
需要主线程确认：
建议合并方式：
可回退方式：
```

## 记录表

| Handoff ID | Date | Source | Role | compact_count | Scope | Status | Merge decision | Notes |
|---|---|---|---|---:|---|---|---|---|
