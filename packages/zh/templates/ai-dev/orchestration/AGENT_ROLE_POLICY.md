# AGENT_ROLE_POLICY

> 文档状态：current

## 目标

定义主线程、子线程、worktree、fork、side conversation、subagents 和自定义 `.codex/agents/*.toml` 的角色边界。核心原则：**主线程收口事实，其他 agent 只产出候选结论或变更集。**

## 角色权限矩阵

| 角色 | 可做 | 不得做 | 必须输出 / 记录 |
|---|---|---|---|
| `main-session-coordinator` / 主线程 | 任务拆分、模式选择、最终采纳、合并、事实归档、回退决策 | 未检查 handoff / locks / merge queue 就合并；把未确认事实写成事实源 | `THREAD_REGISTRY`, `MERGE_QUEUE`, `THREAD_HANDOFFS`, `PROJECT_STATE`, `decisions` |
| `thread-manager` | 维护会话、compact_count、锁、handoff、冲突、合并队列 | 决定业务事实或架构事实；绕过主线程采纳 | `SESSIONS`, `LOCKS`, `THREAD_SYNC_LOG`, `CONFLICTS` |
| `merge-coordinator` | 检查 changeset、测试结果、文档影响、可回退性 | 自行发布、删除冲突记录、覆盖事实源 | `MERGE_POLICY`, `MERGE_QUEUE`, `CONFLICTS`, `doc-update-runs` |
| `worker` | 在明确任务包内实现或修复 | 扩大范围、直接修改核心事实源、跳过测试说明 | 变更范围、测试结果、风险、回退方式 |
| `reviewer` | 审查代码、文档、测试、安全、架构 | 直接合并、直接改项目事实源、声称未验证事项已确认 | 证据、风险、置信度、未验证事项 |
| `explorer` | 只读探索、依赖图、代码理解、候选方案 | 修改代码或事实文档、输出最终决策 | 探索路径、发现、候选结论、待验证事项 |
| `security-reviewer` | 检查 secret、隐私、权限、脱敏风险 | 传播真实 secret、把敏感样本复制到 docs/logs | 风险等级、证据位置、脱敏建议 |
| `automation` | 执行明确、可重复的检查或生成任务 | 自行改需求/架构/发布策略 | 命令、输入、输出、退出码 |

## 自定义 agent TOML 规则

`.codex/agents/*.toml` 必须包含：

```toml
name = "..."
description = "..."
developer_instructions = """
...
"""
```

`developer_instructions` 至少必须表达：

1. 该 agent 的职责范围。
2. 是否允许写入文件。
3. 不得直接合并或归档项目事实。
4. 输出必须包含证据、风险、未验证事项和建议交接格式。
5. 需要主线程采纳后才可进入事实源。

## 主线程采纳规则

其他 agent 输出成为项目事实必须满足：

1. 有来源记录：`THREAD_REGISTRY` / `SESSIONS` / subagent 名称 / worktree / fork。
2. 有 handoff：范围、发现、已改文件、验证结果、风险、回退方式完整。
3. 通过或手工完成：`ai_doc_impact_check.py`、`architecture_check.py`、`thread_coordination_check.py`。
4. 对业务规则、状态流、数据模型、权限、隐私、历史数据解释等高风险事实，有用户确认或可验证证据。
5. 主线程写入对应 `docs/` 事实源，并在 `MERGE_QUEUE` 或 `MERGE_POLICY` 记录采纳结论。

## 禁止事项

- reviewer / explorer / security-reviewer 不得直接把候选结论写入 `PROJECT_STATE.md`、`decisions.md`、`BUSINESS_RULES.md`、`DATA_MODEL.md` 等事实源。
- subagent 不得自行创建发布、部署、迁移或权限变更决策。
- worker 不得在没有任务包或锁记录的情况下修改核心文档。
- 多 agent 并发时，不得同时持有同一核心文档的 active write 锁。
- 压缩后的旧线程不得继续承担新开发任务，除非 compact_count 未超过阈值且已完成外部化记录。

## 强制检查

合并前或并发任务结束前运行：

```bash
python scripts/thread_coordination_check.py --strict --record
```

如只是任务中途自检，可运行：

```bash
python scripts/thread_coordination_check.py --check --record --advisory
```

## v0.3.2 补充：Codex config 约束

项目会生成 `.codex/config.toml`，默认 `[agents] max_threads = 4`、`max_depth = 1`。不得把 `max_depth` 提高到 1 以上，除非主线程明确记录理由、风险和回退方式。
