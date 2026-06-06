# ai-doc-driven-project

`ai-doc-driven-project` 是一次性的 AI 文档驱动项目治理初始化 / 接管审计 skill。它用于新项目初始化，或在接管进行中项目时补齐项目内的 Codex 根入口、规则文档、项目事实文档、检查脚本、协作记录、Codex 线程治理、agent 角色边界和敏感信息边界。

## 当前入口设计

1. 目标项目使用 `AGENTS.md` 作为 Codex 入口。
2. `AGENTS.md` 保持简短，只负责入口索引、任务路由和硬性门禁。
3. `AGENTS.md` 第一行必须包含 skill 元数据戳，例如：

   ```text
   <!-- ai-skill: ai-doc-driven-project skill-version: 0.3.4 revision-time: 2026-06-06T04:45:00+08:00 -->
   ```

4. 每次用本 skill 初始化、审计或更新项目文档结构时，都必须确保上述注释与 skill 包内 manifest 的 `skill_version` 和 `skill_revision_time` 一致；不得写入项目实际执行时间。
5. 详细规则、项目事实、检查记录和协作记录进入 `docs/` 下专项文档。

## 三种使用方式

### 方式一：由 AI 按 skill 执行

```text
请使用 ai-doc-driven-project 初始化当前项目。项目大方向是：……
```

或：

```text
请使用 ai-doc-driven-project 接管审查当前项目。这个项目已经开发了一段时间，请先审查，不要开发新功能。
```

或：

```text
请使用 ai-doc-driven-project 更新当前项目的 AI 文档结构，保留现有业务文档和项目特定规则。
```

### 方式二：使用内置执行器

在 skill 包根目录运行：

```bash
python bin/apply_skill.py init --target /path/to/project --dry-run
python bin/apply_skill.py init --target /path/to/project --write
python bin/apply_skill.py audit --target /path/to/project --dry-run
python bin/apply_skill.py audit --target /path/to/project --write
python bin/apply_skill.py update --target /path/to/project --dry-run
python bin/apply_skill.py update --target /path/to/project --write
```

执行器依据 `templates/manifest.yml` 工作，默认 dry-run；加 `--write` 才会写入。执行器保守处理：创建缺失文件，不覆盖已有项目文件；已有 `AGENTS.md` 只追加受保护规则块并更新第一行 ai-skill 元数据。

如需创建本地测试凭据占位文件，增加 `--create-test-secrets`；该文件只允许保存在 `.ai-secrets/`，不得提交。

### 方式三：更新 AGENTS 元数据戳

如果只是需要刷新 `AGENTS.md` 顶部 skill 注释，可以运行：

```bash
python bin/apply_skill.py update --target /path/to/project --write
```

默认使用 skill 包内置修订时间；仅 skill 维护者重新打包时才应覆盖：

```bash
python bin/apply_skill.py update --target /path/to/project --write --revision-time 2026-06-06T04:45:00+08:00
```

## 会创建或补齐的目标项目结构

- 根入口：`AGENTS.md`
- AI 开发管理：`docs/ai-dev/`
- 规则专项文档：`docs/ai-dev/rules/`
- Codex App 能力选择：`docs/codex/`
- 线程、worktree、subagents、handoff、merge、compact：`docs/ai-dev/orchestration/`
- 多会话与文档冲突管理：`docs/ai-dev/concurrency/` 和 `docs/ai-dev/changesets/`
- 线程协调检查记录：`docs/ai-dev/thread-check-runs/`
- 架构：`docs/architecture/`，其中 `MODULE_BOUNDARIES.yml` 是机器可读架构边界文件
- 产品、业务、开发、数据、质量、安全、集成、可观测性、环境、测试、手册、部署、产物：`docs/product/`、`docs/business/`、`docs/development/`、`docs/data/`、`docs/quality/`、`docs/security/`、`docs/integrations/`、`docs/observability/`、`docs/env/`、`docs/test/`、`docs/manual/`、`docs/deploy/`、`docs/artifacts/`
- 日志样本说明：`logs/`
- 检查脚本：`scripts/ai_doc_impact_check.py`、`scripts/architecture_check.py`、`scripts/thread_coordination_check.py`、`scripts/project_auto_commit.py`
- Codex agents 配置：`.codex/agents/`
- Codex hooks 示例配置：`.codex/hooks.json`
- 本地测试敏感信息目录：`.ai-secrets/`，必须从版本库排除

## manifest

`templates/manifest.yml` 是模板复制和本地生成文件的机器可读清单，包含：

- root file 映射；
- template directory 映射；
- runtime-only 目录；
- `.ai-secrets` 本地文件；
- `.gitignore` 追加项；
- 检查脚本、Codex agent 和 hooks 配置路径。

后续新增模板或调整目标路径时，优先更新 manifest，再同步 README / SKILL / DOCS_INDEX。

## 关键机制

### 文档自动更新防漏

`docs/ai-dev/DOC_UPDATE_TRIGGERS.yml` 是文档更新触发规则的机器可读事实源，`DOC_UPDATE_TRIGGERS.md` 是人读说明。

常见检查命令：

```bash
python scripts/ai_doc_impact_check.py --record
python scripts/ai_doc_impact_check.py --staged
python scripts/ai_doc_impact_check.py --since HEAD~1
python scripts/ai_doc_impact_check.py --changed src/user/service.py docs/product/PRODUCT_SPEC.md
python scripts/ai_doc_impact_check.py --task-type data_model_change --record
python scripts/ai_doc_impact_check.py --task-type compact --record
python scripts/ai_doc_impact_check.py --task-type agent_role --record
```

脚本会检查：命中的 trigger、required docs、suggested docs、敏感信息高风险位置和内容、人工确认事项，以及可选生成 `docs/ai-dev/doc-update-runs/DUR-*.md`。

### 架构边界检查

`docs/architecture/MODULE_BOUNDARIES.yml` 是机器可读架构边界来源。初始化时它是 `stub`，填入模块边界前不得把它视为高可信事实源。

```bash
python scripts/architecture_check.py --changed src/foo.py
python scripts/architecture_check.py --staged
python scripts/architecture_check.py --since HEAD~1
python scripts/architecture_check.py --all
```

脚本会校验 YAML schema，并对 Python / JavaScript / TypeScript 的简单 import 依赖做边界检查。

### 线程协调、agent 角色和 compact 治理

新增 `scripts/thread_coordination_check.py`，用于检查：

- `AGENTS.md` 第一行 ai-skill 元数据注释是否存在且格式正确；
- `.codex/agents/*.toml` 是否包含 `name`、`description`、`developer_instructions`；
- 是否存在 `main-session-coordinator`；
- `compact_count` 是否达到迁移阈值；
- 是否缺少 handoff；
- 是否存在 active write / merge 锁冲突；
- `MERGE_QUEUE` 是否存在 blocked / conflict 项；
- Codex hooks / subagent / compact 事件是否需要记录。

常用命令：

```bash
python scripts/thread_coordination_check.py --check --record
python scripts/thread_coordination_check.py --staged --strict --record
python scripts/thread_coordination_check.py --event PreCompact --record
python scripts/thread_coordination_check.py --event PostCompact --record
python scripts/thread_coordination_check.py --event SubagentStop --record
```

`.codex/hooks.json` 提供 Codex lifecycle hooks 示例，会在 `PreCompact`、`PostCompact`、`SubagentStop`、`Stop` 事件上以 advisory 方式运行线程协调检查。项目本地 hooks 需要在 Codex 中审查并信任后才会生效。

### Codex 会话压缩策略

Codex 长任务可通过 `/compact` 或自动 compact 继续推进，但压缩摘要会替代早期上下文，因此关键事实必须落到 `docs/`。本 skill 的默认策略：

- `compact_count = 0`：正常继续；
- `compact_count = 1`：可以继续，但必须更新项目状态、任务、决策和下一步；
- `compact_count = 2`：迁移阈值，除小范围收尾外必须 handoff 并新开会话或 fork；
- `compact_count >= 3`：不得继续承担新开发任务，只能整理 handoff 和切换会话。

高风险任务在 `compact_count >= 1` 时即应优先新开会话。


### 项目自动提交可选策略

本 skill 新增可选的本地自动提交策略。默认关闭，只用于本地 `git commit`，永不自动 push。

关键文件：

- `docs/ai-dev/git/AUTO_COMMIT_POLICY.md`
- `docs/ai-dev/git/AUTO_COMMIT_CONFIG.json`
- `scripts/project_auto_commit.py`

先查看计划：

```bash
python scripts/project_auto_commit.py --plan
```

只有项目配置和命令行同时显式启用后，才允许：

```bash
python scripts/project_auto_commit.py --commit -m "docs: update AI governance"
```

该脚本会拒绝提交 `.ai-secrets/`、`.env`、私钥、证书、kubeconfig、真实 token 或 secret-like 内容，并在提交前运行文档影响、线程协调和架构检查。

### 文档状态与可信度

新项目初始化后的大量文档只是 `stub` 或 `draft`。空模板不能当作事实源。`DOCS_INDEX.md` 使用以下状态：`stub`、`draft`、`current`、`verified`、`deprecated/reference`、`superseded`。

### 敏感信息

`.ai-secrets/` 用于保存本机测试环境敏感信息，必须从版本库排除。真实密码、真实 token、真实密钥、真实用户隐私数据不得写入 `docs/`、`logs/`、截图、测试报告、提交信息或最终回答。

`docs/env/TEST_SECRETS_FORMAT.md` 只说明 `.ai-secrets/test-secrets.local.md` 的格式，不得填写真实值。

### 编排、并发与合并收口

`docs/ai-dev/orchestration/` 定义工作模式选择、handoff、compact policy、agent role policy 和 merge policy。高并发优先，但合并必须收口。主线程负责最终采纳、合并和项目事实归档。子线程、subagents、worktree、fork 的输出默认不是项目事实，必须经主线程采纳并写入 `docs/`。

## v0.3.3 关键修复

- `update` 模式会迁移生成型治理文件，避免 `AGENTS.md` 已升级而脚本、hooks 或 `DOC_UPDATE_TRIGGERS.yml` 仍停留在旧版。
- `Stop` / `SubagentStop` / compact 相关 hooks 默认使用 `--hook-json --advisory`，不再每轮写入 `TC-*` 记录。
- 文档影响检查新增 `--mode init|template_install`，初始化模板时不会把 stub 文档误判为已确认业务事实。
- Secret 扫描改为逐个匹配值判断占位符，并对所有 changed files 做全局敏感扫描。
- 新增 `.codex/config.toml`，默认 `[agents] max_threads = 4`、`max_depth = 1`。
- 新增 `bin/validate_skill_package.py` 与 `bin/build_release.py`，用于包校验和干净打包。
