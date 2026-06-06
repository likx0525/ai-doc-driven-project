# SUBAGENTS

> 文档状态：current

## 目标

定义 Codex subagents 的使用范围、输出格式和主线程采纳规则。subagents 适用于并行审查、探索和局部实现，不适用于直接确认项目事实。

## 使用前提

- 用户或主线程明确要求使用 subagents。
- 任务可拆分，边界清晰，结果可合并。
- 已读取 `AGENT_ROLE_POLICY.md` 和 `WORK_MODE_ROUTING.md`。
- 敏感信息已经脱敏，或任务被限制在主线程 / security-reviewer。

## 输出要求

每个 subagent 必须输出：

```text
Agent：
角色：reviewer / explorer / worker / security-reviewer / test-reviewer / architecture-reviewer
任务范围：
证据：
发现：
风险：
未验证事项：
建议：
是否修改文件：是/否；文件列表：
需要主线程采纳：是
```

## 禁止事项

- subagent 不得直接合并。
- subagent 不得把输出写成 `PROJECT_STATE`、`decisions`、`BUSINESS_RULES`、`DATA_MODEL` 等事实源。
- subagent 不得擅自扩大任务范围。
- subagent 不得处理或传播未脱敏真实 secret。

## 记录表

| ID | Date | Agent | Role | Scope | Status | Handoff | Main decision | Notes |
|---|---|---|---|---|---|---|---|---|
