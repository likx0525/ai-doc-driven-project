# CHANGELOG

## 0.3.4 - 2026-06-06T04:45:00+08:00

- Prepared the package with LICENSE, NOTICE, SECURITY, CONTRIBUTING, and TEMPLATE_OUTPUT_LICENSE files.
- Added GitHub Actions CI workflow, issue templates, PR template, and compatibility notes.
- Replaced static secret-like test fixtures with dynamically constructed fake values to reduce secret-scanning false positives.
- Updated package metadata to v0.3.4.

## 0.3.3 - 2026-06-05T06:30:00+08:00

- Added the optional project auto-commit strategy: disabled by default, permits only explicitly enabled local git commits, and never pushes automatically.
- Added `docs/ai-dev/git/AUTO_COMMIT_POLICY.md` and `AUTO_COMMIT_CONFIG.json`.
- Added `scripts/project_auto_commit.py` for planning, explicit staging, and local commits after checks pass.
- Extended `DOC_UPDATE_TRIGGERS.yml`, `AGENTS.md`, `DOCS_INDEX.md`, and Codex work-mode docs with auto-commit gates.

## 0.3.2 - 2026-06-05T05:24:46+08:00

- Fixed update migrations: generated scripts, hooks, Codex config, and trigger rules migrate with the skill version.
- Fixed Codex hooks: Stop/SubagentStop now emit hook JSON; default hooks no longer write TC run records.
- Fixed secret scanning: all changed files are scanned and placeholder decisions are made per matched value.
- Fixed hidden-file path normalization: `.env` is no longer normalized to `env`.
- Added `.codex/config.toml`, package build tooling, package validation, and schema files.
- Added `ai_doc_impact_check.py --mode init|template_install`.
- Cleaned runtime artifacts from package archives.

## 0.3.1

- Defined AGENTS.md metadata revision-time as the skill package revision time.
- Published Chinese and English packages.
