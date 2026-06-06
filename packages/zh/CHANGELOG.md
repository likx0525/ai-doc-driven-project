# CHANGELOG

## 0.3.4 - 2026-06-06T04:45:00+08:00

- 补齐 LICENSE、NOTICE、SECURITY、CONTRIBUTING、TEMPLATE_OUTPUT_LICENSE 等治理文件。
- 新增 GitHub Actions CI workflow、issue 模板、PR 模板和兼容性文档。
- 修复测试中的静态 secret-like fixture 字符串，降低 secret scanning 误报。
- 将包元数据更新为 v0.3.4。

## 0.3.3 - 2026-06-05T06:30:00+08:00

- 新增项目自动提交可选策略：默认关闭，只允许显式启用的本地 git commit，永不自动 push。
- 新增 `docs/ai-dev/git/AUTO_COMMIT_POLICY.md` 和 `AUTO_COMMIT_CONFIG.json`。
- 新增 `scripts/project_auto_commit.py`，支持 plan、显式 staging、检查通过后的本地 commit。
- 扩展 `DOC_UPDATE_TRIGGERS.yml`、`AGENTS.md`、`DOCS_INDEX.md` 和 Codex 工作模式文档，纳入自动提交门禁。

## 0.3.2 - 2026-06-05T05:24:46+08:00

- 修复 update 迁移：生成型脚本、hooks、Codex config 和触发规则会随 skill 版本迁移。
- 修复 Codex hooks：Stop/SubagentStop 使用 hook JSON 输出；默认 hooks 不再写 TC 运行记录。
- 修复 secret scan：所有 changed files 都会扫描；占位符判断改为逐个匹配值判断。
- 修复隐藏文件路径规范化：不再把 `.env` 变成 `env`。
- 新增 `.codex/config.toml`、package build、package validation 和 schema 文件。
- 新增 `ai_doc_impact_check.py --mode init|template_install`。
- 清理 package archive 中的 runtime artifacts。

## 0.3.1

- 将 AGENTS.md metadata 的 revision-time 明确定义为 skill 包修订时间。
- 生成中文包与英文包。
