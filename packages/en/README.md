# ai-doc-driven-project

`ai-doc-driven-project` is a one-time AI documentation governance skill for initializing, auditing, or upgrading a project. It creates a single Codex root entry, project fact documents, rule documents, check scripts, Codex agent profiles, orchestration records, concurrency records, and local-only secrets guidance.

## Entry Model

1. The target project uses `AGENTS.md` as the Codex entry.
2. `AGENTS.md` stays relatively short and routes the agent to detailed documents under `docs/`.
3. The first line of `AGENTS.md` must contain the skill metadata stamp:

```text
<!-- ai-skill: ai-doc-driven-project skill-version: 0.3.4 revision-time: 2026-06-06T04:45:00+08:00 -->
```

`revision-time` is the skill package generation or revision time from `templates/manifest.yml`. It is not the time when a target project runs `init`, `audit`, or `update`. Runtime application records are written separately under `docs/ai-dev/doc-update-runs/`.

## Quick Use

Run from the skill package root:

```bash
python bin/apply_skill.py init --target /path/to/project --dry-run
python bin/apply_skill.py init --target /path/to/project --write
python bin/apply_skill.py audit --target /path/to/project --dry-run
python bin/apply_skill.py audit --target /path/to/project --write
python bin/apply_skill.py update --target /path/to/project --dry-run
python bin/apply_skill.py update --target /path/to/project --write
```

The executor is conservative: it creates missing files, preserves existing project-specific content, and appends protected additions to an existing `AGENTS.md`.

## Generated Structure

- `AGENTS.md`
- `docs/ai-dev/` for project state, rules, tasks, decisions, traceability, orchestration, concurrency, changesets, and run records
- `docs/architecture/` including `MODULE_BOUNDARIES.yml`
- `docs/codex/` for Codex work-mode, thread, subagent, and worktree usage
- `scripts/ai_doc_impact_check.py`
- `scripts/architecture_check.py`
- `scripts/thread_coordination_check.py`
- `scripts/project_auto_commit.py`
- `docs/ai-dev/git/AUTO_COMMIT_POLICY.md` and `docs/ai-dev/git/AUTO_COMMIT_CONFIG.json`
- `.codex/agents/` custom agent profiles
- `.codex/hooks.json` advisory hook examples
- `.ai-secrets/` local-only secret guidance


## Optional Auto-Commit Strategy

The generated project includes an optional local auto-commit strategy. It is disabled by default. In this skill, auto-commit means local `git commit` only; automatic push is forbidden.

Key files:

- `docs/ai-dev/git/AUTO_COMMIT_POLICY.md`
- `docs/ai-dev/git/AUTO_COMMIT_CONFIG.json`
- `scripts/project_auto_commit.py`

Inspect the plan first:

```bash
python scripts/project_auto_commit.py --plan
```

A commit may run only when both the project config and CLI explicitly opt in:

```bash
python scripts/project_auto_commit.py --commit -m "docs: update AI governance"
```

The helper refuses protected paths such as `.ai-secrets/`, `.env`, private keys, certificates, kubeconfig files, and secret-like content. It also runs documentation impact, thread coordination, and architecture checks before committing unless the project policy explicitly allows skipping checks. It never pushes.

## Important Checks

```bash
python scripts/ai_doc_impact_check.py --record
python scripts/architecture_check.py --advisory
python scripts/thread_coordination_check.py --check --record
python scripts/thread_coordination_check.py --staged --strict --record
```

## Main Rules

- Subagent, fork, worktree, and side-conversation outputs are candidates, not project facts.
- Only the main session coordinator or the main thread can adopt a candidate into project facts.
- Context compaction must be tracked with `compact_count`. At `compact_count >= 2`, hand off to a new conversation except for narrow closeout work.
- Real secrets must never be written into `docs/`, `logs/`, reports, screenshots, or final answers.

## v0.3.3 key changes

- Added the optional project auto-commit strategy, disabled by default and limited to explicit local commits.
- `update` mode migrates generated governance files so `AGENTS.md` cannot claim a newer skill version while scripts, hooks, or `DOC_UPDATE_TRIGGERS.yml` remain old.
- `Stop`, `SubagentStop`, and compaction hooks now use `--hook-json --advisory` by default and do not write `TC-*` run records on every turn.
- `ai_doc_impact_check.py` adds `--mode init|template_install` so initial stub template installation is not mistaken for confirmed business fact changes.
- Secret scanning now evaluates each matched value individually and runs across all changed files.
- `.codex/config.toml` is generated with `[agents] max_threads = 4` and `max_depth = 1`.
- `bin/validate_skill_package.py` and `bin/build_release.py` provide package validation and clean packaging.
