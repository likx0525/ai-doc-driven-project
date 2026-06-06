# CODEX_WORK_MODE_SELECTION

> 文档状态：current

## 目标

为 Codex 当前线程、`/new`、`/fork`、side conversation、worktree、subagents、automation 和 compact 后继续工作提供选择标准。

## 选择矩阵

| 场景 | 推荐模式 | 禁用或慎用 | 必须记录 |
|---|---|---|---|
| 小范围单文件修改 | 当前线程 | subagents/worktree | 轻量结果 |
| 长任务但 compact_count = 0 | 当前线程，必要时阶段性文档外置 | 无文档记录的长上下文 | tasks / PROJECT_STATE |
| compact_count = 1 | 当前线程收尾；继续前更新 docs | 继续扩大范围 | SESSIONS / THREAD_REGISTRY / CODEX_USAGE_LOG |
| compact_count >= 2 | `/new` 或 `/fork` + handoff | 继续新开发任务 | THREAD_HANDOFFS / CONTEXT_COMPACTION_POLICY |
| 多方案探索 | `/fork` / side conversation / explorer | 直接改事实源 | THREAD_REGISTRY / HANDOFFS |
| 多模块实现或重构 | worktree / worker | 直接在主线大改 | WORKTREES / MERGE_QUEUE |
| 并行审查 | subagents / reviewers | subagent 自行合并 | SUBAGENTS / AGENT_ROLE_POLICY |
| 安全、隐私、凭据 | 主线程 + security-reviewer | 未脱敏扩散 | SECURITY / SECRETS_POLICY / CODEX_USAGE_LOG |
| 发布、部署、迁移 | 主线程 + checklist | subagent 自行决定 | RELEASE_CHECKLIST / ROLLBACK / MIGRATIONS |
| 文档治理收尾且检查通过 | `manual_suggest` 或显式本地 auto-commit | 自动 push | AUTO_COMMIT_POLICY / AUTO_COMMIT_CONFIG |

## 完成前检查

```bash
python scripts/ai_doc_impact_check.py --record
python scripts/thread_coordination_check.py --check --record
```

严格合并前：

```bash
python scripts/thread_coordination_check.py --strict --record
```


自动提交收尾前：

```bash
python scripts/project_auto_commit.py --plan
```
