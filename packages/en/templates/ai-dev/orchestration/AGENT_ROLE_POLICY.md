# AGENT_ROLE_POLICY

> Document status: current  
> Fact source: yes, for AI role boundaries and coordination policy.

## Purpose

This policy defines which Codex session or subagent may coordinate, review, merge, or write project facts. It prevents side conversations, forks, worktrees, and subagents from silently turning exploratory output into durable project truth.

## Core rule

Only the main session may adopt outputs as project facts. A fact becomes durable only after both conditions are true:

1. The main session explicitly accepts it.
2. The accepted result is written to the appropriate fact-source document under `docs/`.

Subagents, worktrees, forks, and side conversations produce candidate findings only. Their output is never authoritative by itself.

## Role matrix

| Role | May do | Must not do | Required records |
|---|---|---|---|
| main-session-coordinator | Plan task scope, choose work mode, accept/reject findings, update fact sources, decide final merge | Hide unresolved risk, treat unconfirmed assumptions as facts | `PROJECT_STATE.md`, `tasks.md`, `decisions.md`, `MERGE_QUEUE.md` when needed |
| thread-manager | Track sessions, compact count, locks, handoffs, and queue state | Decide business facts or architecture decisions alone | `SESSIONS.md`, `LOCKS.md`, `THREAD_REGISTRY.md`, `THREAD_HANDOFFS.md` |
| merge-coordinator | Review pending changesets for checks, conflicts, rollback, and doc impact | Override the main session or merge unconfirmed facts | `MERGE_POLICY.md`, `MERGE_QUEUE.md`, changeset records |
| architecture-reviewer | Review dependency direction, module boundaries, ADR impact | Modify product/business facts as final truth | `ARCHITECTURE.md`, `MODULE_BOUNDARIES.yml`, ADR notes |
| docs-reviewer | Review doc completeness, stale facts, trigger coverage | Declare implementation behavior as requirements without confirmation | `DOCS_INDEX.md`, `DOC_UPDATE_TRIGGERS.*` |
| security-reviewer | Review secrets, privacy, permissions, and sensitive logs | Spread unredacted secrets across sessions or docs | `SECRETS_POLICY.md`, `PRIVACY.md`, `PERMISSIONS.md` |
| test-reviewer | Review test plan, test evidence, regression risk | Claim production readiness without evidence | `test-plan.md`, `test-runs.md` |
| code-explorer | Inspect code and propose findings | Write discoveries as confirmed requirements | handoff or investigation notes |

## Subagent output contract

Every subagent result must include:

- scope inspected;
- evidence and file references;
- confidence level;
- unresolved assumptions;
- whether project docs need updates;
- whether secrets or sensitive data were encountered;
- a clear recommendation to accept, revise, or reject.

## Merge boundary

A merge is blocked when:

- no handoff exists for non-trivial side work;
- active write/merge locks conflict;
- `compact_count` has reached the migration threshold without handoff;
- `.codex/agents/*.toml` changed without reviewing this policy;
- security, privacy, data migration, permission, or production-release facts are unconfirmed.

Run before strict merge:

```bash
python scripts/thread_coordination_check.py --staged --strict --record
```
