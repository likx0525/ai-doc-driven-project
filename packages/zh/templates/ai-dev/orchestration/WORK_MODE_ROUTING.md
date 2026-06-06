# WORK_MODE_ROUTING

> 文档状态：current

## 目标

定义 Codex 工作模式选择规则。原则是：小任务保持轻量；可分离、可回退、可追踪、可合并的大任务优先并发；上下文压缩后及时外置事实；最终事实由主线程收口到 `docs/`。

## 工作模式选择矩阵

| 场景 | 推荐模式 | 禁用或慎用模式 | 必须记录 | 说明 |
|---|---|---|---|---|
| 单文件小修、文案修正、简单解释 | 当前线程 | worktree / subagents | 轻量结果即可 | 成本低、冲突小 |
| 需求澄清、事实确认 | 当前线程 | 直接写成已确认事实 | requirements / decisions | 未确认事项保持待确认 |
| compact_count = 1 | 当前线程收尾或继续小范围任务 | 扩大范围、长链路推理 | SESSIONS, THREAD_REGISTRY, CODEX_USAGE_LOG | 必须外置关键状态 |
| compact_count >= 2 | `/new` 或 `/fork` + handoff | 继续新开发任务 | CONTEXT_COMPACTION_POLICY, THREAD_HANDOFFS | 达到迁移阈值 |
| 多模块探索、方案比较 | side conversation / subagents | 直接改核心事实文档 | THREAD_REGISTRY, THREAD_HANDOFFS | 探索输出不是项目事实 |
| 大型重构、跨模块改动 | Codex-managed worktree | 直接在主线大量改动 | WORKTREES, MERGE_POLICY, changeset | 需要隔离和可回退 |
| 长期并行分支 | permanent worktree | 无记录并行 | WORKTREES, SESSIONS, LOCKS | 必须明确所有权和合并规则 |
| 安全、隐私、凭据相关 | 当前线程 + security-reviewer | 未脱敏多线程扩散 | SECURITY, SECRETS_POLICY, CODEX_USAGE_LOG | compact_count >= 1 时优先新会话 |
| 测试复现、日志分析 | 当前线程 / reviewer subagent | 未脱敏日志外传 | test-runs, bug-reports, LOGGING | 日志和报告必须脱敏 |
| 发布、部署、回滚 | 当前线程 + checklist | subagent 自行决定发布 | DEPLOYMENT, RELEASE_CHECKLIST, ROLLBACK | 用户确认优先 |
| 文档冲突或多会话编辑 | changeset + MERGE_QUEUE | 直接覆盖 docs | LOCKS, CONFLICTS, MERGE_QUEUE | 主线程合并收口 |

## 选择流程

1. 判断任务是否可在当前线程安全完成。
2. 检查当前线程 `compact_count`。
3. 判断是否存在并发收益：可分解、边界清楚、结果可合并、失败可回退。
4. 判断风险：数据、隐私、安全、生产部署、历史数据解释、业务规则。
5. 选择最小足够模式。
6. 使用非当前线程模式时，创建或更新对应记录。
7. 使用 subagents 前，读取 `AGENT_ROLE_POLICY.md`。
8. 合并前由主线程检查 handoff、文档影响、架构影响、线程协调、测试和敏感信息。

## 必须运行的检查

```bash
python scripts/thread_coordination_check.py --check --record
```

严格合并前：

```bash
python scripts/thread_coordination_check.py --strict --record
```

## 记录表

| ID | Date | Mode | Scope | Owner | compact_count | Status | Required merge docs | Notes |
|---|---|---|---|---|---:|---|---|---|
