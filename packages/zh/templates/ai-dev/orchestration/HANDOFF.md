# HANDOFF

> 文档状态：current

## 目标

为线程、worktree、subagents、压缩迁移或人工交接提供统一格式，避免上下文只留在聊天或压缩摘要中。

## Handoff 模板

```text
Handoff ID：HO-YYYYMMDD-001
来源线程 / worktree / subagent：
来源角色：coordinator / worker / reviewer / explorer / subagent / automation
compact_count：0 / 1 / 2 / 3+
任务范围：
已完成：
未完成：
关键发现：
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

## 记录

| Handoff ID | Date | Source | Role | compact_count | Scope | Status | Merge decision | Notes |
|---|---|---|---|---:|---|---|---|---|
