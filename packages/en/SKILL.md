---
name: ai-doc-driven-project
description: One-time AI documentation system generator for new, in-progress, or upgraded projects. Use when the user asks to initialize, audit, or update a project with a single root AGENTS.md Codex entry, docs/ rules and project facts, ai-skill revision metadata, Codex work-mode routing, compact_count governance, main-session/subagent role constraints, orchestration, concurrency, changesets, architecture checks, document update checks, thread coordination checks, optional local auto-commit policy, secrets handling, and project documentation templates without implementing business features.
---

# ai-doc-driven-project

This skill initializes, audits, or upgrades an AI documentation governance system inside a target project. After it runs, future project work should rely on the generated `AGENTS.md`, `docs/`, `.codex/`, and scripts rather than on this skill body.

## Entry Design

- Generate root `AGENTS.md`.
- `AGENTS.md` is the Codex entry.
- The first line of `AGENTS.md` must contain:

```text
<!-- ai-skill: ai-doc-driven-project skill-version: <version> revision-time: <ISO-8601 time> -->
```

The `revision-time` field records the skill package generation or revision time from `templates/manifest.yml`; it is not the target project usage time.

## Recommended Execution

```bash
python bin/apply_skill.py init --target <project-root> --dry-run
python bin/apply_skill.py init --target <project-root> --write
python bin/apply_skill.py audit --target <project-root> --dry-run
python bin/apply_skill.py audit --target <project-root> --write
python bin/apply_skill.py update --target <project-root> --dry-run
python bin/apply_skill.py update --target <project-root> --write
```

The executor reads `templates/manifest.yml`, creates missing files, preserves existing project-specific content, and calibrates the `AGENTS.md` metadata stamp to the bundled `skill_revision_time`.

## Modes

### init

Use for a new project or a project without an AI documentation governance structure. Create `AGENTS.md`, copy template trees, append `.gitignore` entries, create runtime-only directories, and create `.ai-secrets/README.md`.

### audit

Use for an in-progress project. Inspect existing code, documents, tests, configuration, logs, and project structure before proposing changes. Record findings in `docs/ai-dev/PROJECT_AUDIT.md`.

### update

Use to upgrade an existing ai-doc-driven-project structure. Add missing current-release documents, scripts, Codex agent profiles, and hook examples without overwriting project-specific content.


## Auto-Commit Strategy

Generate `docs/ai-dev/git/AUTO_COMMIT_POLICY.md`, `docs/ai-dev/git/AUTO_COMMIT_CONFIG.json`, and `scripts/project_auto_commit.py`. The strategy is optional and disabled by default. It permits only local git commits when the project config and command line both explicitly opt in. It must never push automatically.

Before any local auto-commit, the project must pass or explicitly account for documentation impact checks, thread coordination checks, architecture checks, and secret scanning. Protected paths such as `.ai-secrets/`, `.env`, private keys, certificates, kubeconfig files, and real tokens must never be committed.

## Required Constraints

- Do not treat empty templates as verified project facts.
- Do not copy raw chat history into project documents.
- Do not write real secrets into versioned files.
- Do not let subagents, reviewers, workers, forks, worktrees, or side conversations bypass handoff and merge policy.
- Run document impact, architecture, and thread coordination checks before complex merges.

## v0.3.3 key changes

- Added the optional project auto-commit strategy and helper script.
- `update` mode migrates generated governance files so `AGENTS.md` cannot claim a newer skill version while scripts, hooks, or `DOC_UPDATE_TRIGGERS.yml` remain old.
- `Stop`, `SubagentStop`, and compaction hooks now use `--hook-json --advisory` by default and do not write `TC-*` run records on every turn.
- `ai_doc_impact_check.py` adds `--mode init|template_install` so initial stub template installation is not mistaken for confirmed business fact changes.
- Secret scanning now evaluates each matched value individually and runs across all changed files.
- `.codex/config.toml` is generated with `[agents] max_threads = 4` and `max_depth = 1`.
- `bin/validate_skill_package.py` and `bin/build_release.py` provide package validation and clean packaging.
