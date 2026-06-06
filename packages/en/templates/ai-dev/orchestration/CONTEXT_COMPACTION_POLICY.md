# CONTEXT_COMPACTION_POLICY

> Document status: current  
> Fact source: yes, for Codex context compaction governance.

## Purpose

Codex may compact a long conversation manually or automatically. Compaction lets work continue, but repeated summaries can lose nuance, stale assumptions, and unresolved risks. This project therefore treats `compact_count` as a coordination signal.

## Default thresholds

| compact_count | Policy |
|---:|---|
| 0 | Continue normally. Keep important decisions in docs rather than chat memory. |
| 1 | Continue with caution. Externalize current state, task progress, decisions, risks, and next steps into docs. |
| 2 | Migration threshold. Except for small cleanup, create a handoff and start a new conversation or fork. |
| >= 3 | Hard stop for new work. Only produce handoff, update docs, and migrate to a fresh session. |

## High-risk work

For security, privacy, credentials, production release, rollback, data migration, permissions, historical data interpretation, or large architecture changes, prefer a new session when `compact_count >= 1`.

## Required records

Update at least one of these records after compaction:

- `docs/ai-dev/concurrency/SESSIONS.md`
- `docs/ai-dev/orchestration/THREAD_REGISTRY.md`
- `docs/codex/CODEX_USAGE_LOG.md`

When crossing the migration threshold, add a handoff record in:

- `docs/ai-dev/orchestration/THREAD_HANDOFFS.md`

## Handoff minimum

A compaction or session-migration handoff must include:

- source session/thread;
- `compact_count`;
- current task goal;
- confirmed facts and source documents;
- unconfirmed assumptions;
- modified files;
- checks run and checks not run;
- risks, rollback notes, and recommended next action.

## Checks

```bash
python scripts/thread_coordination_check.py --event PreCompact --hook-json --advisory
python scripts/thread_coordination_check.py --event PostCompact --hook-json --advisory
python scripts/thread_coordination_check.py --strict --record
```
