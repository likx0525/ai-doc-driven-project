<!-- ai-skill: ai-doc-driven-project skill-version: 0.3.4 revision-time: 2026-06-06T04:45:00+08:00 -->
# AGENTS.md

本项目采用 AI 文档驱动开发。`AGENTS.md` 是 Codex 根入口；详细规则、事实和记录放在 `docs/` 下。

## Skill 元数据

文件第一行必须保留。`revision-time` 表示本 skill 包的生成/修订时间，不是项目使用本 skill 的时间。

```text
<!-- ai-skill: ai-doc-driven-project skill-version: <version> revision-time: <ISO-8601 time> -->
```

该注释用于识别当前项目文档结构采用的 skill 版本和 skill 包修订时间。每次 `init`、`audit` 或 `update` 只能将它刷新为 manifest 中的 skill 修订时间，不得写入运行命令的当前时间。缺失、过期或格式异常时，必须运行：

```bash
python scripts/thread_coordination_check.py --check --record
```

或重新执行：

```bash
python bin/apply_skill.py update --target . --write
```

## 启动读取顺序

每次任务开始先读取：

1. `docs/ai-dev/DOCS_INDEX.md`
2. `docs/ai-dev/PROJECT_STATE.md`
3. `docs/ai-dev/tasks.md`
4. `docs/ai-dev/decisions.md`

然后根据任务类型读取专项文档。`docs/ai-dev/DOC_UPDATE_TRIGGERS.yml` 和 `DOC_UPDATE_TRIGGERS.md` 主要在完成前用于文档影响检查，不必在每个任务开始时完整读取。

## 工作模式选择

默认使用当前线程完成小范围、可直接验证的任务。以下情况必须读取 `docs/codex/CODEX_WORK_MODE_SELECTION.md` 和 `docs/ai-dev/orchestration/WORK_MODE_ROUTING.md` 后再决定工作模式：

- 多模块、大范围、长时间或高风险改动；
- 需要 worktree、fork、side conversation、subagents、handoff 或 automation；
- 存在并发编辑、文档冲突、待合并 changeset；
- 当前 Codex 线程已经发生上下文压缩，或即将使用 `/compact`、自动 compact 后继续工作；
- 涉及安全、隐私、生产部署、数据迁移或历史数据解释。

使用线程、worktree、subagents、fork、多会话或上下文压缩时，还必须按需维护：

- `docs/ai-dev/orchestration/THREAD_REGISTRY.md`
- `docs/ai-dev/orchestration/THREAD_WORK_PACKETS.md`
- `docs/ai-dev/orchestration/THREAD_HANDOFFS.md`
- `docs/ai-dev/orchestration/CONTEXT_COMPACTION_POLICY.md`
- `docs/ai-dev/orchestration/MERGE_POLICY.md`
- `docs/ai-dev/concurrency/SESSIONS.md`
- `docs/ai-dev/concurrency/LOCKS.md`
- `docs/ai-dev/concurrency/MERGE_QUEUE.md`

主线程负责最终合并、事实确认和项目事实归档。子线程、subagents、worktree、fork 的输出默认不是项目事实，必须经主线程采纳并写入 `docs/`。

## Codex 会话压缩治理

Codex 线程发生 `/compact` 或自动 compact 后，必须把关键状态外置到项目文档，不能只依赖压缩摘要。压缩计数使用 `compact_count` 记录在 `docs/ai-dev/concurrency/SESSIONS.md` 和 `docs/ai-dev/orchestration/THREAD_REGISTRY.md`。

项目默认阈值：

| compact_count | 处理规则 |
|---:|---|
| 0 | 正常继续 |
| 1 | 可以继续，但必须更新任务状态、关键决策、风险和下一步 |
| 2 | 进入迁移阈值；除小范围收尾外，必须创建 handoff 并新开会话或 fork |
| >= 3 | 不得继续承担新开发任务；只能整理 handoff、更新文档并切换新会话 |

安全、隐私、凭据、数据迁移、生产发布、历史数据解释、复杂架构重构任务，在 `compact_count >= 1` 时即应优先新开会话。新会话必须读取 handoff、PROJECT_STATE、tasks、decisions 和相关专项文档，不得只依赖上一会话压缩摘要。

## Agent 角色约束

使用 subagents 或自定义 agent 前，必须读取：

- `docs/ai-dev/orchestration/AGENT_ROLE_POLICY.md`
- `docs/ai-dev/orchestration/SUBAGENTS.md`
- `docs/ai-dev/orchestration/MERGE_POLICY.md`

`.codex/agents/*.toml` 必须声明 `name`、`description`、`developer_instructions`。除 `main-session-coordinator` 或主线程明确采纳外，任何 reviewer、explorer、worker、subagent 不得直接把输出写成项目事实，不得绕过 handoff、LOCKS、MERGE_QUEUE 或 merge policy。


## 项目自动提交可选策略

自动提交默认关闭。这里的自动提交只指本地 `git commit`，不得自动 push。任何 AI 或脚本在执行自动 stage / commit 前，必须读取：

- `docs/ai-dev/git/AUTO_COMMIT_POLICY.md`
- `docs/ai-dev/git/AUTO_COMMIT_CONFIG.json`

只有配置文件和命令行同时显式允许时，才可运行：

```bash
python scripts/project_auto_commit.py --plan
python scripts/project_auto_commit.py --commit -m "docs: update AI governance"
```

涉及 `.ai-secrets/`、`.env`、私钥、证书、kubeconfig、真实 token、真实密码、真实用户隐私数据、active lock 冲突、blocked merge queue、未 handoff 的 compact 迁移阈值时，不得自动提交。自动提交不能替代测试、文档影响检查、线程协调检查、架构检查或用户确认。

## 任务类型路由

| 任务类型 | 必读文档 |
|---|---|
| 新需求 / 需求确认 | `docs/ai-dev/requirements.md`, `docs/ai-dev/rules/human-participation.md`, `docs/product/PRODUCT_SPEC.md`, `docs/product/USER_FLOWS.md`, `docs/ai-dev/TRACEABILITY.md` |
| 用户反馈 / 审查反馈 | `docs/ai-dev/feedback.md`, `docs/ai-dev/tasks.md`, `docs/ai-dev/rules/task-flow.md` |
| 代码修改 | `docs/architecture/ARCHITECTURE.md`, `docs/architecture/MODULES.md`, `docs/architecture/MODULE_BOUNDARIES.yml`, `docs/development/CODE_CONVENTIONS.md`, `docs/test/test-plan.md` |
| 架构 / 模块 / 依赖方向 | `docs/architecture/ARCHITECTURE.md`, `docs/architecture/MODULES.md`, `docs/architecture/MODULE_BOUNDARIES.yml`, `docs/architecture/ARCHITECTURE_CHECKLIST.md`, `docs/architecture/ARCHITECTURE_DEBT.md` |
| UI / 交互 / 用户流程 | `docs/product/UI_SPEC.md`, `docs/product/USER_FLOWS.md`, `docs/product/GLOSSARY.md`, `docs/manual/MANUAL_GENERATION_RULES.md` |
| 业务规则 / 状态流 | `docs/business/BUSINESS_RULES.md`, `docs/business/STATE_FLOWS.md`, `docs/ai-dev/decisions.md`, `docs/architecture/DATA_MODEL.md` |
| 数据模型 / 迁移 / 备份恢复 | `docs/architecture/DATA_MODEL.md`, `docs/data/MIGRATIONS.md`, `docs/data/DATA_LIFECYCLE.md`, `docs/data/BACKUP_RESTORE.md` |
| API / 集成 / Webhook | `docs/development/API_CONTRACTS.md`, `docs/integrations/INTEGRATIONS.md`, `docs/integrations/EXTERNAL_APIS.md`, `docs/integrations/WEBHOOKS.md` |
| 测试 / 缺陷 | `docs/test/test-plan.md`, `docs/test/test-cases.md`, `docs/test/test-runs.md`, `docs/test/bug-reports.md` |
| 产品手册 / 帮助文档 | `docs/manual/MANUAL_GENERATION_RULES.md`, `docs/manual/MANUAL_INDEX.md`, `docs/manual/USER_MANUAL.md`, `docs/manual/QUICK_START.md`, `docs/manual/FAQ.md` |
| 部署 / 发布 / 回滚 / 运维 | `docs/deploy/DEPLOYMENT.md`, `docs/deploy/RELEASE_CHECKLIST.md`, `docs/deploy/ROLLBACK.md`, `docs/deploy/OPERATIONS.md`, `docs/deploy/CHANGELOG.md`, `docs/env/environment.md` |
| 安全 / 隐私 / 权限 / 凭据 | `docs/ai-dev/rules/security.md`, `docs/security/SECURITY.md`, `docs/security/PRIVACY.md`, `docs/security/PERMISSIONS.md`, `docs/security/SECRETS_POLICY.md`, `docs/env/credentials-note.md` |
| Codex App 能力 / 产物 / 线程压缩 | `docs/codex/CODEX_APP_USAGE.md`, `docs/codex/CODEX_THREADS.md`, `docs/codex/CODEX_WORK_MODE_SELECTION.md`, `docs/codex/CODEX_USAGE_LOG.md`, `docs/ai-dev/orchestration/CONTEXT_COMPACTION_POLICY.md`, `docs/artifacts/ARTIFACTS.md` |
| 知识沉淀 / 规则改进 | `docs/ai-dev/rules/knowledge-capture.md`, `docs/ai-dev/LESSONS_LEARNED.md`, `docs/ai-dev/RULE_CHANGE_REQUESTS.md` |
| 自动提交 / Git 收尾 | `docs/ai-dev/git/AUTO_COMMIT_POLICY.md`, `docs/ai-dev/git/AUTO_COMMIT_CONFIG.json`, `docs/ai-dev/orchestration/MERGE_POLICY.md`, `docs/ai-dev/concurrency/LOCKS.md`, `docs/ai-dev/concurrency/MERGE_QUEUE.md` |

## 修改前门禁

修改代码或文档前，必须判断是否涉及：

1. 模块边界、依赖方向或架构约束；
2. 数据模型、迁移、备份恢复或历史数据解释；
3. 业务规则、状态流、权限模型或隐私策略；
4. 外部 API、Webhook、凭据或环境配置；
5. 用户可见行为、UI、手册或测试用例；
6. worktree、subagents、fork、changeset、上下文压缩或并发冲突；
7. 需要用户确认的事实、需求、规则或验收标准。

涉及架构边界时，优先运行：

```bash
python scripts/architecture_check.py
```

涉及多会话、subagents、worktree、fork、locks、merge queue 或压缩治理时，优先运行：

```bash
python scripts/thread_coordination_check.py --check --record
```

## 完成前门禁

任务完成前必须完成：

1. 测试或验证；无法测试时说明原因，不得声称已通过；
2. 文档影响检查；
3. 如修改代码或架构，执行或手工完成架构边界检查；
4. 敏感信息检查；
5. 如果使用 worktree / subagents / fork / 多会话 / 上下文压缩，完成 handoff、agent role、merge policy 与线程协调检查；
6. 将聊天中形成的长期事实写入对应 `docs/` 文件；未确认事项不得写成已确认事实。

优先运行：

```bash
python scripts/ai_doc_impact_check.py --record
python scripts/thread_coordination_check.py --check --record
```

提交前或需要严格检查时运行：

```bash
python scripts/ai_doc_impact_check.py --staged --record
python scripts/thread_coordination_check.py --staged --strict --record
```

如果脚本不可用，必须手工根据 `docs/ai-dev/DOC_UPDATE_TRIGGERS.yml`、`docs/ai-dev/DOC_UPDATE_TRIGGERS.md`、`docs/ai-dev/orchestration/AGENT_ROLE_POLICY.md`、`docs/ai-dev/orchestration/CONTEXT_COMPACTION_POLICY.md` 检查，并在 `docs/ai-dev/doc-update-runs/` 或 `docs/ai-dev/thread-check-runs/` 记录。

## 硬性原则

- 不覆盖已有重要文件，不删除已有代码。
- 不在根目录散放 AI 生成文档、截图、报告、临时文件。
- 不把聊天上下文或压缩摘要作为长期事实来源。
- 不把代码中识别到的行为直接视为已确认需求。
- 没有实际执行测试时，不得声称“已测试通过”。
- 没有实际执行部署时，不得声称“已部署成功”。
- 涉及数据模型、业务规则、状态流、模块边界、依赖方向、历史数据解释方式时，必须先获得用户确认。
- 功能开发和重构默认分开。
- 真实敏感信息只能保存在 `.ai-secrets/*.local.md`，且必须从版本库排除。
- `docs/`、`logs/`、报告、截图、最终回答和提交信息不得包含真实密码、真实 token、真实密钥或真实用户隐私数据。
- 高并发优先，但必须可回退、可追踪、可合并。
- 主线程是最终事实收口方；其他线程和 subagents 输出默认只是候选结论。
- 自动提交默认关闭；启用后也只允许本地 commit，不得自动 push。

## 结果输出格式

小任务使用轻量格式：

```text
完成内容：
验证情况：
文档影响检查：已执行/未执行，DUR-.../无
架构检查：已执行/未执行/不适用
线程协调检查：已执行/未执行/不适用，TC-.../无
compact_count：0/1/2/3+/未知
敏感信息检查：已检查/未检查/不适用
自动提交策略：disabled/manual_suggest/stage_only/local_commit；commit hash/无
更新文档：
待确认事项：
建议下一步：
```

复杂任务、并发任务或使用 worktree/subagents/fork/上下文压缩时使用完整格式：

```text
Codex 工作模式：当前线程/新对话/fork/side/worktree/subagents/automation/不适用
线程 ID：TH-YYYYMMDD-001/无
线程角色：coordinator/worker/reviewer/explorer/subagent/automation/不适用
compact_count：0/1/2/3+/未知
是否需要新会话：是/否；原因：
关联任务包：WP-YYYYMMDD-001/无
changeset：CS-YYYYMMDD-001/无
文档检查报告：DUR-YYYYMMDD-001/无
线程协调检查：TC-YYYYMMDD-001/无
架构检查：已执行/未执行/不适用
测试情况：已测试/未测试/静态检查/部分测试/无法测试
敏感信息检查：已检查/未检查/不适用
自动提交策略：disabled/manual_suggest/stage_only/local_commit
是否执行本地 commit：是/否；commit hash：<hash>/无
是否执行 push：否
是否可回退：是/否
回退方式：
更新文档：
新增产物：
待确认事项：
建议下一步：
```

## v0.3.3 生成型文件升级规则

- `revision-time` 表示 skill 包修订时间，不得在普通项目使用时改成当前时间。
- 使用 `update` 升级项目文档结构时，脚本、hooks、`.codex/config.toml`、`DOC_UPDATE_TRIGGERS.yml` 等生成型治理文件可以被迁移；项目事实文档默认保留。
- 初次安装或结构升级后做文档影响检查时，使用 `--mode template_install`，避免把 stub 模板当成已确认业务事实。
- Codex hooks 默认不得写 `TC-*`；严格合并或 CI 才使用 `--record`。

## v0.3.3 自动提交策略补充

- v0.3.3 新增项目自动提交可选策略；默认关闭，只允许显式启用的本地 commit，永不自动 push。
