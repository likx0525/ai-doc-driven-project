# THREAD_WORK_PACKETS

> 文档状态：stub

## 目标

将复杂任务拆成可分配给主线程、worker、reviewer、explorer、subagent 或 worktree 的最小工作包。工作包必须边界清晰、可验证、可回退、可合并。

## 工作包状态

- `planned`
- `active`
- `blocked`
- `handoff-ready`
- `merged`
- `rejected`
- `cancelled`

## 工作包模板

```text
Work Packet ID：WP-YYYYMMDD-001
目标：
分配角色：
允许修改范围：
禁止修改范围：
必读文档：
预期输出：
验证方式：
文档影响：
风险：
回退方式：
```

## 记录表

| WP ID | Date | Role | Scope | Allowed paths | Forbidden paths | Status | Handoff | Notes |
|---|---|---|---|---|---|---|---|---|
