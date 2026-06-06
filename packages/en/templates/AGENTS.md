<!-- ai-skill: ai-doc-driven-project skill-version: 0.3.4 revision-time: 2026-06-06T04:45:00+08:00 -->
# AGENTS.md

This project uses AI documentation-driven development. `AGENTS.md` is the root Codex entry. Detailed rules, facts, decisions, and records live under `docs/`.

## Skill Metadata

The first line must be preserved. `revision-time` is the skill package generation or revision time, not the time when this project runs the skill. `init`, `audit`, and `update` must calibrate the line to `templates/manifest.yml` values.

## Startup Reading Order

Read these first:

1. `docs/ai-dev/DOCS_INDEX.md`
2. `docs/ai-dev/PROJECT_STATE.md`
3. `docs/ai-dev/tasks.md`
4. `docs/ai-dev/decisions.md`

Then read task-specific documents. Use `DOC_UPDATE_TRIGGERS.yml` and `DOC_UPDATE_TRIGGERS.md` before completion checks.

## Work Mode Routing

Use the current thread for small, verifiable work. Before using worktrees, forks, side conversations, subagents, handoff, automation, or multi-session work, read:

- `docs/codex/CODEX_WORK_MODE_SELECTION.md`
- `docs/ai-dev/orchestration/WORK_MODE_ROUTING.md`
- `docs/ai-dev/orchestration/AGENT_ROLE_POLICY.md`
- `docs/ai-dev/orchestration/MERGE_POLICY.md`

The main thread is responsible for final merge, fact adoption, and project fact archival. Outputs from subagents, worktrees, forks, or side conversations are candidates only until adopted by the main thread and written to the appropriate `docs/` source.

## Context Compaction Governance

Track Codex context compaction with `compact_count` in `docs/ai-dev/concurrency/SESSIONS.md` and `docs/ai-dev/orchestration/THREAD_REGISTRY.md`.

| compact_count | Rule |
|---:|---|
| 0 | Continue normally. |
| 1 | Continue only after externalizing status, decisions, risks, and next steps into docs. |
| 2 | Migration threshold. Except for narrow closeout, create handoff and start `/new` or `/fork`. |
| >= 3 | Do not take on new development. Prepare handoff and switch conversations. |

For security, privacy, credentials, data migration, release, rollback, historical data interpretation, or complex architecture work, prefer a new conversation at `compact_count >= 1`.

## Agent Role Boundaries

`.codex/agents/*.toml` must include `name`, `description`, and `developer_instructions`. Reviewers, explorers, workers, subagents, forks, and worktrees must not directly write candidate output as project facts unless the main thread explicitly adopts it.


## Optional Project Auto-Commit Strategy

Auto-commit is disabled by default. In this skill, auto-commit means local `git commit` only; automatic push is forbidden. Before any AI or script performs automatic stage/commit, it must read:

- `docs/ai-dev/git/AUTO_COMMIT_POLICY.md`
- `docs/ai-dev/git/AUTO_COMMIT_CONFIG.json`

A local commit may run only when both the config file and CLI explicitly opt in:

```bash
python scripts/project_auto_commit.py --plan
python scripts/project_auto_commit.py --commit -m "docs: update AI governance"
```

Auto-commit is forbidden for `.ai-secrets/`, `.env`, private keys, certificates, kubeconfig files, real tokens, real passwords, real user-private data, active lock conflicts, blocked merge queue items, or compact migration thresholds without handoff. Auto-commit does not replace testing, documentation impact checks, thread coordination checks, architecture checks, or user confirmation.

## Completion Gates

Before completion, run or justify not running:

```bash
python scripts/ai_doc_impact_check.py --record
python scripts/architecture_check.py --advisory
python scripts/thread_coordination_check.py --check --record
```

For auto-commit or commit wrap-up, first run:

```bash
python scripts/project_auto_commit.py --plan
```

A local commit is allowed only after explicit user or project-policy opt-in. Automatic push is forbidden.

For strict merge checks:

```bash
python scripts/ai_doc_impact_check.py --staged --strict --record
python scripts/thread_coordination_check.py --staged --strict --record
```

## Hard Rules

- Never overwrite human-authored project facts without preserving history or recording a decision.
- Never store real secrets in `docs/`, `logs/`, reports, screenshots, or final answers.
- Never treat raw chat history or compressed context summaries as verified project facts.
- Record conflicts, locks, handoffs, and merge decisions in the corresponding `docs/ai-dev/` files.
- Auto-commit is disabled by default; even when enabled, it may create only local commits and must never push.

## v0.3.3 generated-file update rules

- `revision-time` is the skill package revision time; normal project usage must not replace it with the current time.
- During `update`, generated governance files such as scripts, hooks, `.codex/config.toml`, and `DOC_UPDATE_TRIGGERS.yml` may be migrated; project fact documents are preserved by default.
- After initial installation or structural update, use `--mode template_install` for document impact checks so stub templates are not treated as confirmed business facts.
- Default Codex hooks must not write `TC-*` records; use `--record` only for strict merge checks or CI evidence.

## v0.3.3 auto-commit strategy additions

- v0.3.3 adds the optional project auto-commit strategy; it is disabled by default, allows only explicit local commits, and never pushes.
