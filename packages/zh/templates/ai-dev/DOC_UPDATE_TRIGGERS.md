# DOC_UPDATE_TRIGGERS.md

> 文档状态：current  
> 机器可读事实源：`DOC_UPDATE_TRIGGERS.yml`  
> 规则版本：0.3.1

## 目标

定义项目开发过程中各类事件触发的文档更新规则。脚本优先读取 `DOC_UPDATE_TRIGGERS.yml`；本文件用于人工阅读。

## 使用方式

```bash
python scripts/ai_doc_impact_check.py --record
python scripts/ai_doc_impact_check.py --staged --record
python scripts/ai_doc_impact_check.py --since HEAD~1
python scripts/ai_doc_impact_check.py --changed src/user/service.py docs/product/PRODUCT_SPEC.md
python scripts/ai_doc_impact_check.py --task-type data_model_change --record
python scripts/ai_doc_impact_check.py --task-type compact --record
python scripts/ai_doc_impact_check.py --task-type agent_role --record
```

## 根入口规则

- Codex 根入口规则只使用 `AGENTS.md`。
- `AGENTS.md` 第一行必须包含 `<!-- ai-skill: ai-doc-driven-project skill-version: <version> revision-time: <ISO-8601> -->`。
- 每次使用 skill 初始化、审计或更新项目文档结构时，必须确保该注释与 skill 包内 manifest 的版本和修订时间一致；不得写入项目实际执行时间。

## Codex 线程、压缩与 agent 规则

- `/compact` 或自动 compact 后必须维护 `compact_count`，并把关键事实写入项目文档。
- `compact_count >= 2` 时，除小范围收尾外，必须创建 handoff 并优先 `/new` 或 `/fork`。
- `.codex/agents/*.toml` 必须包含 `name`、`description`、`developer_instructions`。
- 非主线程 / 非 `main-session-coordinator` 输出默认不是项目事实，必须通过 handoff 和 merge policy。
- 合并前优先运行 `python scripts/thread_coordination_check.py --strict --record`。

## 触发矩阵

| Trigger ID | 事件 | 检测线索 | 必须检查/更新的文档 | 建议检查文档 | 需人工确认 |
|---|---|---|---|---|---|
| `codex_entry_change` | Codex 根入口规则变化；AGENTS.md 是唯一根入口。 | paths: AGENTS.md<br>task_types: codex_entry_change, rule_change | docs/ai-dev/DOCS_INDEX.md, docs/ai-dev/RULE_CHANGE_REQUESTS.md | README.md | - |
| `new_requirement` | 新增需求或需求范围变化。 | paths: docs/ai-dev/requirements.md, docs/product/PRODUCT_SPEC.md<br>task_types: new_requirement, requirement, feature_request | docs/ai-dev/requirements.md, docs/ai-dev/tasks.md, docs/ai-dev/TRACEABILITY.md | docs/product/PRODUCT_SPEC.md, docs/product/USER_FLOWS.md | - |
| `requirement_confirmation` | 需求被用户确认或修改为项目事实。 | paths: docs/ai-dev/decisions.md, docs/ai-dev/PROJECT_STATE.md<br>task_types: requirement_confirmation, decision | docs/ai-dev/requirements.md, docs/ai-dev/decisions.md, docs/ai-dev/PROJECT_STATE.md, docs/ai-dev/TRACEABILITY.md | - | - |
| `user_feedback` | 收到用户反馈、审查反馈或验收反馈。 | paths: docs/ai-dev/feedback.md<br>task_types: user_feedback, feedback | docs/ai-dev/feedback.md, docs/ai-dev/tasks.md | docs/manual/FAQ.md | - |
| `bug_discovery` | 发现缺陷、回归或异常行为。 | paths: docs/test/bug-reports.md<br>task_types: bug_discovery, bug_report | docs/test/bug-reports.md, docs/ai-dev/tasks.md, docs/test/test-cases.md | docs/ai-dev/feedback.md | - |
| `bug_fix` | 修复缺陷或回归。 | task_types: bug_fix | docs/test/bug-reports.md, docs/test/test-runs.md | docs/deploy/CHANGELOG.md, docs/test/test-cases.md | - |
| `feature_completion` | 新功能完成或功能行为实质变化。 | task_types: feature_completion, feature | docs/ai-dev/tasks.md, docs/test/test-cases.md, docs/ai-dev/TRACEABILITY.md | docs/manual/USER_MANUAL.md, docs/deploy/CHANGELOG.md | - |
| `ui_change` | 界面、文案、布局、交互或可视化输出变化。 | paths: src/**/components/**, components/**, pages/**, docs/product/UI_SPEC.md<br>task_types: ui_change, ux_change | docs/product/UI_SPEC.md, docs/product/USER_FLOWS.md | docs/manual/USER_MANUAL.md, docs/artifacts/ARTIFACTS.md | - |
| `user_flow_change` | 用户流程、使用路径或端到端场景变化。 | paths: docs/product/USER_FLOWS.md<br>task_types: user_flow_change | docs/product/USER_FLOWS.md, docs/test/test-cases.md | docs/manual/USER_MANUAL.md | - |
| `business_rule_change` | 业务规则、计算规则、校验规则或权限业务含义变化。 | paths: docs/business/BUSINESS_RULES.md<br>task_types: business_rule_change | docs/business/BUSINESS_RULES.md, docs/ai-dev/decisions.md, docs/test/test-cases.md | - | business_owner_or_user |
| `state_flow_change` | 状态机、生命周期、审批流、订单流等变化。 | paths: docs/business/STATE_FLOWS.md<br>task_types: state_flow_change | docs/business/STATE_FLOWS.md, docs/architecture/DATA_MODEL.md, docs/test/test-cases.md | - | business_owner_or_user |
| `data_model_change` | 数据模型、schema、字段、索引或持久化结构变化。 | paths: docs/architecture/DATA_MODEL.md, db/**, database/**, migrations/**, prisma/**, schema/**<br>task_types: data_model_change, schema_change | docs/architecture/DATA_MODEL.md, docs/ai-dev/decisions.md, docs/data/MIGRATIONS.md | docs/data/DATA_LIFECYCLE.md, docs/data/BACKUP_RESTORE.md | data_owner_or_user |
| `data_migration` | 迁移、回填、清洗、导入导出或历史数据解释变化。 | paths: migrations/**, scripts/**, docs/data/MIGRATIONS.md<br>task_types: data_migration | docs/data/MIGRATIONS.md, docs/data/BACKUP_RESTORE.md, docs/deploy/RELEASE_CHECKLIST.md | - | data_owner_or_user |
| `persistence_change` | 新增或修改持久化数据。 | paths: db/**, database/**, migrations/**, prisma/**, schema/**<br>task_types: persistence_change | docs/data/DATA_LIFECYCLE.md, docs/data/BACKUP_RESTORE.md | docs/architecture/DATA_MODEL.md | - |
| `architecture_change` | 架构、模块边界或依赖方向变化。 | paths: docs/architecture/**<br>task_types: architecture_change, refactor | docs/architecture/ARCHITECTURE.md, docs/architecture/MODULES.md, docs/architecture/MODULE_BOUNDARIES.yml, docs/architecture/ARCHITECTURE_CHECKLIST.md | docs/architecture/ADR/, docs/architecture/ARCHITECTURE_DEBT.md | - |
| `module_change` | 新增、删除、拆分或合并模块。 | paths: docs/architecture/MODULES.md, docs/architecture/MODULE_BOUNDARIES.yml<br>task_types: module_change | docs/architecture/MODULES.md, docs/architecture/MODULE_BOUNDARIES.yml, docs/development/DEVELOPMENT_GUIDE.md | docs/development/CODE_CONVENTIONS.md | - |
| `api_change` | 新增或修改 API、接口契约、SDK 或内部服务契约。 | paths: docs/development/API_CONTRACTS.md, api/**, routes/**, src/**/api/**, app/**/api/**<br>task_types: api_change | docs/development/API_CONTRACTS.md, docs/test/test-cases.md | docs/integrations/EXTERNAL_APIS.md | - |
| `integration_change` | 新增或修改外部服务、第三方 API 或集成配置。 | paths: docs/integrations/**, docs/env/credentials-note.md<br>task_types: integration_change | docs/integrations/INTEGRATIONS.md, docs/integrations/EXTERNAL_APIS.md, docs/env/credentials-note.md, docs/test/test-cases.md | - | - |
| `webhook_change` | 新增或修改 Webhook、回调、事件订阅。 | paths: docs/integrations/WEBHOOKS.md<br>task_types: webhook_change | docs/integrations/WEBHOOKS.md, docs/test/test-cases.md, docs/security/SECURITY.md | - | - |
| `dependency_change` | 新增、升级、删除依赖或运行时环境依赖变化。 | paths: package.json, package-lock.json, pnpm-lock.yaml, yarn.lock, requirements.txt, pyproject.toml, poetry.lock, go.mod, Cargo.toml, docs/env/dependencies.md<br>task_types: dependency_change | docs/env/dependencies.md, docs/development/DEPENDENCY_POLICY.md | - | - |
| `performance_change` | 性能、容量、吞吐、延迟、资源占用相关修改。 | paths: docs/quality/PERFORMANCE.md<br>task_types: performance_change | docs/quality/PERFORMANCE.md, docs/quality/NON_FUNCTIONAL_REQUIREMENTS.md, docs/test/test-runs.md | - | - |
| `compatibility_change` | 浏览器、平台、版本、设备或向后兼容性变化。 | paths: docs/quality/COMPATIBILITY.md<br>task_types: compatibility_change | docs/quality/COMPATIBILITY.md, docs/test/test-cases.md | - | - |
| `accessibility_change` | 可访问性、键盘导航、屏幕阅读器或无障碍体验变化。 | paths: docs/quality/ACCESSIBILITY.md, docs/product/UI_SPEC.md<br>task_types: accessibility_change | docs/quality/ACCESSIBILITY.md, docs/product/UI_SPEC.md | - | - |
| `permission_change` | 权限、角色、认证授权、访问控制变化。 | paths: docs/security/PERMISSIONS.md<br>task_types: permission_change, auth_change | docs/security/PERMISSIONS.md, docs/security/SECURITY.md, docs/test/test-cases.md | - | security_owner_or_user |
| `user_data_change` | 用户数据、隐私数据、采集、处理、保留或删除规则变化。 | paths: docs/security/PRIVACY.md, docs/data/DATA_LIFECYCLE.md<br>task_types: user_data_change, privacy_change | docs/security/PRIVACY.md, docs/data/DATA_LIFECYCLE.md | - | privacy_or_data_owner |
| `secret_or_credential_change` | 敏感信息、凭据、secret 策略变化。 | paths: .ai-secrets/**, docs/security/**, docs/env/credentials-note.md, docs/env/TEST_SECRETS_FORMAT.md<br>task_types: secret_change, credential_change | docs/security/SECRETS_POLICY.md, docs/env/credentials-note.md, docs/env/TEST_SECRETS_FORMAT.md | - | - |
| `test_execution` | 执行测试、验收、验证或复现。 | paths: docs/test/test-runs.md<br>task_types: test_execution, verification | docs/test/test-runs.md | docs/test/bug-reports.md, docs/artifacts/ARTIFACTS.md | - |
| `codex_capability_use` | 使用 Codex App 能力、浏览器、Chrome、computer use、automation、skills、artifacts 或图像生成。 | paths: docs/codex/**, docs/artifacts/**<br>task_types: codex_capability_use, artifact_change, image_generation, browser_use, automation_use | docs/codex/CODEX_USAGE_LOG.md | docs/artifacts/ARTIFACTS.md, docs/codex/CODEX_THREADS.md, docs/ai-dev/orchestration/CONTEXT_COMPACTION_POLICY.md | - |
| `worktree_subagent_or_fork` | 使用 worktree、subagents、fork、side conversation 或多线程协作。 | paths: docs/ai-dev/orchestration/**, docs/ai-dev/concurrency/**, .codex/agents/**, .codex/hooks.json<br>task_types: worktree, subagent, fork, side_conversation, multi_session, context_compaction, thread_coordination | docs/ai-dev/orchestration/WORK_MODE_ROUTING.md, docs/ai-dev/orchestration/THREAD_REGISTRY.md, docs/ai-dev/orchestration/THREAD_HANDOFFS.md, docs/ai-dev/orchestration/MERGE_POLICY.md, docs/codex/CODEX_USAGE_LOG.md, docs/ai-dev/orchestration/AGENT_ROLE_POLICY.md, docs/ai-dev/orchestration/CONTEXT_COMPACTION_POLICY.md, docs/ai-dev/orchestration/THREAD_COORDINATION.md, docs/ai-dev/concurrency/SESSIONS.md | - | - |
| `artifact_change` | 新增或修改 AI 产物、截图、报告、导出文件或生成物索引。 | paths: docs/artifacts/**<br>task_types: artifact_change, screenshot, report | docs/artifacts/ARTIFACTS.md | docs/test/test-runs.md, docs/manual/USER_MANUAL.md | - |
| `log_analysis` | 日志分析、脱敏日志样本或运行时异常分析。 | paths: logs/**, docs/observability/LOGGING.md<br>task_types: log_analysis | docs/observability/LOGGING.md | docs/observability/INCIDENTS.md, docs/test/bug-reports.md | - |
| `incident` | 事故、线上问题、重大故障或恢复过程。 | paths: docs/observability/INCIDENTS.md<br>task_types: incident | docs/observability/INCIDENTS.md, docs/ai-dev/tasks.md | docs/deploy/CHANGELOG.md, docs/deploy/ROLLBACK.md | - |
| `deployment` | 部署、环境变更或上线操作。 | paths: docs/deploy/DEPLOYMENT.md, docs/env/environment.md, deploy/**, .github/workflows/**<br>task_types: deployment | docs/deploy/DEPLOYMENT.md, docs/test/test-runs.md | docs/deploy/CHANGELOG.md, docs/deploy/ROLLBACK.md | - |
| `release` | 发布、版本变更、变更日志或发布检查。 | paths: docs/deploy/RELEASE_CHECKLIST.md, docs/deploy/CHANGELOG.md, docs/deploy/VERSIONING.md<br>task_types: release | docs/deploy/RELEASE_CHECKLIST.md, docs/deploy/CHANGELOG.md, docs/deploy/VERSIONING.md | - | - |
| `manual_update` | 产品手册、FAQ、快速开始或用户帮助文档更新。 | paths: docs/manual/**<br>task_types: manual_update, help_docs | docs/manual/MANUAL_INDEX.md, docs/manual/USER_MANUAL.md, docs/manual/QUICK_START.md, docs/manual/FAQ.md, docs/ai-dev/TRACEABILITY.md | - | - |
| `lesson_or_rule_update` | 经验沉淀、规则改进或 AI 工作方式调整。 | paths: docs/ai-dev/LESSONS_LEARNED.md, docs/ai-dev/RULE_CHANGE_REQUESTS.md, docs/ai-dev/rules/**<br>task_types: lesson, rule_update | docs/ai-dev/LESSONS_LEARNED.md, docs/ai-dev/RULE_CHANGE_REQUESTS.md | AGENTS.md, docs/ai-dev/DOCS_INDEX.md | - |
| `multi_session` | 多会话开始、结束、锁定、冲突或同步。 | paths: docs/ai-dev/concurrency/**<br>task_types: multi_session, lock, session | docs/ai-dev/concurrency/SESSIONS.md, docs/ai-dev/concurrency/LOCKS.md | docs/ai-dev/concurrency/MERGE_QUEUE.md | - |
| `changeset_change` | changeset 创建、合并、拒绝或队列状态变化。 | paths: docs/ai-dev/changesets/**, docs/ai-dev/concurrency/MERGE_QUEUE.md<br>task_types: changeset, merge | docs/ai-dev/concurrency/MERGE_QUEUE.md, docs/ai-dev/tasks.md | docs/ai-dev/DOCS_INDEX.md, docs/ai-dev/concurrency/CONFLICTS.md | - |
| `doc_inventory_change` | 新增、归档、废弃、重命名文档或文档状态变化。 | paths: docs/ai-dev/DOCS_INDEX.md, docs/archive/**<br>task_types: doc_inventory_change, new_doc, archive_doc, deprecate_doc, doc_status_change | docs/ai-dev/DOCS_INDEX.md | docs/ai-dev/PROJECT_AUDIT.md | - |
| `source_code_change` | 源代码、应用代码、库代码、包或服务代码变化。用于兜底提醒测试和任务记录，不推断具体业务语义。 | paths: src/**, app/**, lib/**, packages/**, services/**<br>task_types: source_code_change, code_change | docs/ai-dev/tasks.md, docs/test/test-runs.md | docs/test/test-cases.md, docs/architecture/ARCHITECTURE.md, docs/deploy/CHANGELOG.md | - |
| `skill_revision_metadata` | 使用 ai-doc-driven-project 初始化、审计或更新项目文档结构，必须更新 AGENTS.md 顶部 ai-skill 元数据注释。 | paths: AGENTS.md, docs/ai-dev/DOCS_INDEX.md, docs/ai-dev/doc-update-runs/**<br>task_types: skill_init, skill_update, doc_structure_update, audit, init, update | AGENTS.md, docs/ai-dev/DOCS_INDEX.md, docs/ai-dev/PROJECT_STATE.md, docs/ai-dev/doc-update-runs/ | README.md, docs/ai-dev/PROJECT_AUDIT.md | - |
| `codex_context_compaction` | Codex 线程发生 /compact、自动 compact、上下文压缩或压缩后继续工作。 | paths: docs/ai-dev/orchestration/CONTEXT_COMPACTION_POLICY.md, docs/ai-dev/orchestration/THREAD_REGISTRY.md, docs/ai-dev/orchestration/THREAD_HANDOFFS.md, docs/ai-dev/concurrency/SESSIONS.md, docs/codex/CODEX_THREADS.md<br>task_types: compact, codex_compaction, context_compaction, pre_compact, post_compact, new_session, resume_session | docs/ai-dev/orchestration/CONTEXT_COMPACTION_POLICY.md, docs/ai-dev/orchestration/THREAD_REGISTRY.md, docs/ai-dev/orchestration/THREAD_HANDOFFS.md, docs/ai-dev/concurrency/SESSIONS.md, docs/codex/CODEX_USAGE_LOG.md | docs/ai-dev/tasks.md, docs/ai-dev/decisions.md, docs/ai-dev/PROJECT_STATE.md | - |
| `agent_role_policy` | 自定义 Codex agent、subagent 角色边界、主会话协调 agent 或 reviewer/explorer/worker 权限变化。 | paths: .codex/agents/**, docs/ai-dev/orchestration/AGENT_ROLE_POLICY.md, docs/ai-dev/orchestration/SUBAGENTS.md<br>task_types: agent_role, agent_config, subagent_policy, main_session_coordinator, thread_manager, merge_coordinator | docs/ai-dev/orchestration/AGENT_ROLE_POLICY.md, docs/ai-dev/orchestration/SUBAGENTS.md, docs/ai-dev/orchestration/MERGE_POLICY.md, docs/ai-dev/orchestration/THREAD_HANDOFFS.md | docs/codex/CODEX_SUBAGENTS.md, docs/codex/CODEX_USAGE_LOG.md | - |
| `thread_coordination_enforcement` | 线程协调、锁、合并队列、handoff、Codex hooks 或强制校验脚本变化。 | paths: scripts/thread_coordination_check.py, .codex/hooks.json, docs/ai-dev/concurrency/**, docs/ai-dev/orchestration/THREAD_COORDINATION.md, docs/ai-dev/orchestration/MERGE_POLICY.md<br>task_types: thread_coordination, lock_check, merge_queue, handoff_check, codex_hook, script_enforcement | docs/ai-dev/orchestration/THREAD_COORDINATION.md, docs/ai-dev/orchestration/THREAD_HANDOFFS.md, docs/ai-dev/orchestration/MERGE_POLICY.md, docs/ai-dev/concurrency/SESSIONS.md, docs/ai-dev/concurrency/LOCKS.md, docs/ai-dev/concurrency/MERGE_QUEUE.md | docs/ai-dev/concurrency/CONFLICTS.md, docs/ai-dev/thread-check-runs/ | - |

## 任务结束检查

每次任务结束前必须输出：

- 文档触发检查：已检查 / 未检查
- 命中的 trigger
- 按规则应检查或更新的文档
- 实际更新的文档
- 未更新原因
- 需人工确认的事项
- `doc-update-runs` 记录路径（如已生成）
- 如涉及线程、subagent、worktree、fork 或 compact，还要输出 `thread-check-runs` 记录路径

## 维护规则

- `DOC_UPDATE_TRIGGERS.yml` 是机器可读主规则源。
- 修改本文件时必须同步 YAML，或从 YAML 重新生成本文件。
- 新增 trigger 时应包含 `description`、`detect`、`required_docs`，必要时添加 `confirmation_required` 和 `forbidden_locations`。

## v0.3.2 补充：模板安装模式

初始化或结构升级时使用：

```bash
python scripts/ai_doc_impact_check.py --mode template_install --advisory
```

该模式仍检查核心文件和敏感信息，但不会把复制 stub 模板误判为已确认业务事实变更。


## v0.3.3 新增：项目自动提交策略

机器规则 `project_auto_commit_policy` 在以下情况触发：

- 修改 `docs/ai-dev/git/AUTO_COMMIT_POLICY.md`；
- 修改 `docs/ai-dev/git/AUTO_COMMIT_CONFIG.json`；
- 修改 `scripts/project_auto_commit.py`；
- 任务类型为 `auto_commit`、`git_commit`、`commit_policy` 或 `version_control`。

启用本地自动 commit 前必须获得用户或项目 owner 确认。自动提交不得包含 `.ai-secrets/`、`.env`、私钥、证书、kubeconfig 或真实 token。
