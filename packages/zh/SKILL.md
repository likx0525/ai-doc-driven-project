---
name: ai-doc-driven-project
description: One-time AI documentation system generator for new, in-progress, or upgraded projects. Use when the user asks to initialize, audit, or update a project with a single root AGENTS.md Codex entry, docs/ rules and project facts, ai-skill revision metadata, Codex work-mode routing, compact_count governance, main-session/subagent role constraints, orchestration, concurrency, changesets, architecture checks, document update checks, thread coordination checks, optional local auto-commit policy, secrets handling, and project documentation templates without implementing business features.
---

# ai-doc-driven-project

本 skill 是一次性的项目规则与文档治理生成器。它创建、审计或更新项目内 AI 文档驱动开发体系。运行完成后，后续项目工作依赖目标项目中的 `AGENTS.md`、`docs/`、`.codex/` 和检查脚本，而不是依赖本 skill 正文。

## 入口设计

- 生成根目录 `AGENTS.md`。
- `AGENTS.md` 是 Codex 入口。
- `AGENTS.md` 第一行必须有 ai-skill 元数据注释：

  ```text
  <!-- ai-skill: ai-doc-driven-project skill-version: <version> revision-time: <ISO-8601 time> -->
  ```

- 每次使用本 skill 执行 `init`、`audit` 或 `update`，都必须确保该注释与 skill 包内 `templates/manifest.yml` 的 `skill_version` 和 `skill_revision_time` 一致；不得写入项目实际执行时间。
- `AGENTS.md` 保持相对简短，只负责入口索引、任务路由和硬性门禁。
- 详细规则、项目事实、检查记录、agent 角色、compact 记录和协作记录放在 `docs/` 下。
## 推荐执行方式

优先使用内置执行器预览和应用：

```bash
python bin/apply_skill.py init --target <project-root> --dry-run
python bin/apply_skill.py init --target <project-root> --write
python bin/apply_skill.py audit --target <project-root> --dry-run
python bin/apply_skill.py audit --target <project-root> --write
python bin/apply_skill.py update --target <project-root> --dry-run
python bin/apply_skill.py update --target <project-root> --write
```

执行器读取 `templates/manifest.yml`，并采用保守策略：创建缺失文件，不覆盖已有项目文件；已有 `AGENTS.md` 只追加受保护规则块，并把 ai-skill 元数据校准为 skill 包修订时间。如需创建本地测试凭据占位文件，增加 `--create-test-secrets`。

如果需要固定 revision time，可传入：

```bash
python bin/apply_skill.py update --target <project-root> --write --revision-time 2026-06-06T04:45:00+08:00
```

如果无法运行执行器，则按本文件的 Template map 和 Hard rules 手工执行，并手工写入 `AGENTS.md` 第一行 ai-skill 元数据。

## 模式

### init

用于新项目或尚无 AI 文档治理体系的项目。

1. 创建或补齐根目录 `AGENTS.md`，不得盲目覆盖已有重要内容。
2. 在 `AGENTS.md` 第一行写入 ai-skill 元数据注释。
3. 按 `templates/manifest.yml` 复制模板目录到目标项目。
4. 追加 `templates/gitignore-additions.txt` 到 `.gitignore`，避免 `.ai-secrets/` 和本地 secret 文件进入版本库。
5. 创建 runtime-only 目录：`docs/archive/`、`docs/ai-dev/thread-check-runs/`、`logs/samples/`、`.ai-secrets/`。
6. 创建本地 `.ai-secrets/README.md`。
7. 如需要测试凭据且 `.ai-secrets/test-secrets.local.md` 不存在，按 `docs/env/TEST_SECRETS_FORMAT.md` 的格式创建本地占位文件；不得提交真实敏感信息。

### audit

用于进行中项目接管审查。

1. 先检查现有代码、文档、配置、测试、环境说明、日志和项目结构，再提出改动。
2. 检查并补齐根目录 `AGENTS.md`，将 ai-skill 元数据校准为 skill 包修订时间。
3. 检查并补齐 `docs/`、`logs/`、`scripts/`、`.codex/agents/`、`.codex/hooks.json` 和本地 `.ai-secrets/` 指引。
4. 更新 `docs/ai-dev/PROJECT_AUDIT.md`，记录发现、风险、缺失文档和建议下一步。
5. 审计阶段不实现新业务功能或大型重构，除非用户另行确认。

### update

用于已有 AI 文档治理体系的项目结构升级。

1. 将 `AGENTS.md` 第一行 ai-skill 元数据校准为 skill 包修订时间。
2. 补齐新增文档、脚本、agent 配置和 hooks 示例。
3. 不覆盖已有项目特定内容。
4. 对旧版空模板或泛化文档，只补齐缺失文件，不强制替换。
5. 运行或建议运行 `ai_doc_impact_check.py` 和 `thread_coordination_check.py`。

## 必需生成结构

目标项目应包含：

- `AGENTS.md`
- `docs/ai-dev/`：规则、触发器、追踪关系、项目状态、审计、任务、决策、经验、编排、并发、changesets、doc-update run records、thread-check run records
- `docs/ai-dev/orchestration/AGENT_ROLE_POLICY.md`
- `docs/ai-dev/orchestration/CONTEXT_COMPACTION_POLICY.md`
- `docs/architecture/`：`MODULE_BOUNDARIES.yml`、架构文档、债务记录、检查清单、ADR 模板
- `docs/codex/`：Codex App 能力选择、线程、subagents、worktree、usage log
- `docs/product/`、`docs/business/`、`docs/development/`、`docs/data/`、`docs/quality/`、`docs/security/`、`docs/integrations/`、`docs/observability/`、`docs/env/`、`docs/test/`、`docs/manual/`、`docs/deploy/`、`docs/artifacts/`、`docs/archive/`
- `logs/README.md` 和 `logs/samples/`
- `scripts/ai_doc_impact_check.py`
- `scripts/architecture_check.py`
- `scripts/thread_coordination_check.py`
- `.codex/agents/*.toml`
- `.codex/hooks.json`
- 本地 `.ai-secrets/README.md` 和按需 `.ai-secrets/test-secrets.local.md`，且 `.ai-secrets/` 被版本库排除

## Template map

机器可读映射见 `templates/manifest.yml`。核心映射：

- `templates/AGENTS.md` -> `AGENTS.md`
- `templates/gitignore-additions.txt` -> append to `.gitignore` if missing
- `templates/ai-dev/` -> `docs/ai-dev/`
- `templates/architecture/` -> `docs/architecture/`
- `templates/codex/` -> `docs/codex/`
- `templates/product/` -> `docs/product/`
- `templates/business/` -> `docs/business/`
- `templates/development/` -> `docs/development/`
- `templates/data/` -> `docs/data/`
- `templates/quality/` -> `docs/quality/`
- `templates/security/` -> `docs/security/`
- `templates/integrations/` -> `docs/integrations/`
- `templates/observability/` -> `docs/observability/`
- `templates/env/` -> `docs/env/`
- `templates/test/` -> `docs/test/`
- `templates/manual/` -> `docs/manual/`
- `templates/deploy/` -> `docs/deploy/`
- `templates/artifacts/` -> `docs/artifacts/`
- `templates/logs/` -> `logs/`
- `templates/scripts/` -> `scripts/`
- `templates/codex-agents/` -> `.codex/agents/`
- `templates/codex-config/` -> `.codex/`

## Existing-file preservation

应用到目标项目时：

1. 不盲目覆盖已有 `AGENTS.md`。只补充缺失的路由和门禁，并保留不冲突的项目特定说明。
2. 必须将已有 `AGENTS.md` 顶部 ai-skill 元数据校准为 skill 包修订时间。
3. 项目特定内容与模板内容冲突时，以目标项目已确认事实为准，并在 `PROJECT_AUDIT.md` 记录冲突。
4. 有价值的既有项目说明应进入对应 `docs/` 专项文档。

## 检查脚本

### 文档影响检查

`docs/ai-dev/DOC_UPDATE_TRIGGERS.yml` 是唯一机器可读事实源。`scripts/ai_doc_impact_check.py` 支持：

```bash
python scripts/ai_doc_impact_check.py --record
python scripts/ai_doc_impact_check.py --staged
python scripts/ai_doc_impact_check.py --since HEAD~1
python scripts/ai_doc_impact_check.py --changed <files...>
python scripts/ai_doc_impact_check.py --task-type data_model_change --record
python scripts/ai_doc_impact_check.py --task-type compact --record
python scripts/ai_doc_impact_check.py --task-type agent_role --record
```

脚本应输出命中的 trigger、required docs、suggested docs、缺失文档、未触达文档、敏感信息风险和人工确认事项。

### 架构边界检查

`docs/architecture/MODULE_BOUNDARIES.yml` 是机器可读架构边界来源。`scripts/architecture_check.py` 支持：

```bash
python scripts/architecture_check.py --changed <files...>
python scripts/architecture_check.py --staged
python scripts/architecture_check.py --since HEAD~1
python scripts/architecture_check.py --all
```

初始化时 `MODULE_BOUNDARIES.yml` 是 `stub`。填入模块边界并通过检查前，不要把它标为高可信事实源。


### 项目自动提交策略

生成 `docs/ai-dev/git/AUTO_COMMIT_POLICY.md`、`docs/ai-dev/git/AUTO_COMMIT_CONFIG.json` 和 `scripts/project_auto_commit.py`。自动提交默认关闭，只允许显式启用后的本地 `git commit`，不得自动 push。启用前必须通过文档影响检查、线程协调检查、架构检查和敏感信息检查。

### 线程协调、角色和压缩检查

`scripts/thread_coordination_check.py` 支持：

```bash
python scripts/thread_coordination_check.py --check --record
python scripts/thread_coordination_check.py --staged --strict --record
python scripts/thread_coordination_check.py --event PreCompact --record
python scripts/thread_coordination_check.py --event PostCompact --record
python scripts/thread_coordination_check.py --event SubagentStop --record
python scripts/thread_coordination_check.py --task-type security --strict --record
```

检查内容：

- `AGENTS.md` 顶部 ai-skill 元数据；
- `.codex/agents/*.toml` 必填字段和主控 agent；
- `compact_count` 阈值；
- handoff 是否存在；
- LOCKS active write / merge 冲突；
- MERGE_QUEUE blocked / conflict；
- Codex hooks 和 subagent 事件的交接提醒。

## Codex compact policy

只考虑 Codex 时，长会话可以使用 `/compact` 或自动 compact 继续工作，但重复压缩会把早期上下文转成摘要。为降低信息损耗，本 skill 采用硬性治理：

- `compact_count = 0`：正常继续。
- `compact_count = 1`：可以继续，但必须把项目状态、任务、决策、风险和下一步写入 `docs/`。
- `compact_count = 2`：达到迁移阈值；除小范围收尾外，必须创建 handoff，并使用 `/new` 或 `/fork`。
- `compact_count >= 3`：不得继续承担新开发任务，只能整理 handoff、更新文档并切换新会话。
- 高风险任务在 `compact_count >= 1` 时优先新开会话。

## Agent role policy

- 主线程 / `main-session-coordinator` 负责最终合并、事实确认和项目事实归档。
- `thread-manager` 维护线程、锁、handoff、compact_count 和 merge queue。
- `merge-coordinator` 做合并前检查，不替代主线程决策。
- reviewer / explorer / security-reviewer / test-reviewer 输出默认不是项目事实。
- subagents、worktree、fork、side conversation 输出必须通过 handoff 与 merge policy。
- `.codex/agents/*.toml` 必须包含 `developer_instructions`，明确权限边界。

## Hard rules

- 不覆盖重要已有文件。
- 不删除已有代码。
- 不把空模板、占位内容、聊天上下文或压缩摘要当成项目事实。
- 不在 `docs/`、`logs/`、报告、截图、最终回答、提交信息或 `AGENTS.md` 中保存真实敏感信息。
- 测试环境真实凭据只能保存在 `.ai-secrets/*.local.md`，且必须从版本库排除。
- 所有模板、步骤和输出都必须以 `AGENTS.md` 作为唯一根入口。
- 使用 `docs/ai-dev/DOC_UPDATE_TRIGGERS.yml` 和 `scripts/ai_doc_impact_check.py` 防止遗漏文档更新。
- 使用 `docs/architecture/MODULE_BOUNDARIES.yml` 和 `scripts/architecture_check.py` 检查架构边界。
- 使用 `scripts/thread_coordination_check.py` 检查主会话、其他会话、agent 角色、compact_count、锁和合并队列。
- 涉及业务规则、数据模型、状态流、权限、隐私、历史数据解释方式时，必须确认来源，必要时请求用户确认。
- 高并发优先，但必须可回退、可追踪、可合并。
- 主线程负责最终合并、确认和事实归档。

## v0.3.3 关键修复

- `update` 模式会迁移生成型治理文件，避免 `AGENTS.md` 已升级而脚本、hooks 或 `DOC_UPDATE_TRIGGERS.yml` 仍停留在旧版。
- `Stop` / `SubagentStop` / compact 相关 hooks 默认使用 `--hook-json --advisory`，不再每轮写入 `TC-*` 记录。
- 文档影响检查新增 `--mode init|template_install`，初始化模板时不会把 stub 文档误判为已确认业务事实。
- Secret 扫描改为逐个匹配值判断占位符，并对所有 changed files 做全局敏感扫描。
- 新增 `.codex/config.toml`，默认 `[agents] max_threads = 4`、`max_depth = 1`。
- 新增 `bin/validate_skill_package.py` 与 `bin/build_release.py`，用于包校验和干净打包。
