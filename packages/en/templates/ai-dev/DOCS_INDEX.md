# DOCS_INDEX

> Document status: current  
> Purpose: catalog the project documentation system and distinguish templates from facts.

## Status values

| Status | Meaning | Can be treated as fact source? |
|---|---|---|
| stub | Template placeholder, not filled for this project | No |
| draft | Partially filled, may contain unverified assumptions | Partial; verify before relying on it |
| current | Current working source of truth | Yes, within its scope |
| verified | Confirmed by tests, owner review, or production evidence | Yes |
| deprecated/reference | Historical reference only | No |
| superseded | Replaced by another document | No |

## Core rule sources

| Path | Purpose | Status | Fact source |
|---|---|---|---|
| `AGENTS.md` | Root Codex entry and hard gates | current | yes |
| `docs/ai-dev/DOCS_INDEX.md` | Documentation map and status definitions | current | yes |
| `docs/ai-dev/DOC_UPDATE_TRIGGERS.yml` | Machine-readable documentation trigger rules | current | yes |
| `docs/ai-dev/DOC_UPDATE_TRIGGERS.md` | Human explanation of trigger rules | current | yes, secondary to YAML |
| `docs/ai-dev/PROJECT_STATE.md` | Current project state | draft | partial |
| `docs/ai-dev/tasks.md` | Active and historical tasks | draft | partial |
| `docs/ai-dev/decisions.md` | Confirmed decisions | draft | yes when decision is marked confirmed |
| `docs/ai-dev/requirements.md` | Requirements and acceptance criteria | draft | partial |
| `docs/architecture/MODULE_BOUNDARIES.yml` | Module boundary config | stub | no until filled and checked |
| `docs/ai-dev/orchestration/AGENT_ROLE_POLICY.md` | Agent role and fact-boundary policy | current | yes |
| `docs/ai-dev/orchestration/CONTEXT_COMPACTION_POLICY.md` | compact_count policy | current | yes |
| `docs/ai-dev/orchestration/MERGE_POLICY.md` | Merge gate policy | current | yes |
| `docs/ai-dev/concurrency/LOCKS.md` | Multi-session locks | draft | partial |
| `docs/ai-dev/concurrency/MERGE_QUEUE.md` | Pending changeset queue | draft | partial |
| `docs/ai-dev/git/AUTO_COMMIT_POLICY.md` | Optional project auto-commit strategy; permits only explicitly enabled local commits | current | yes |
| `docs/ai-dev/git/AUTO_COMMIT_CONFIG.json` | Auto-commit capability switches and protected path configuration | current | yes |
| `scripts/project_auto_commit.py` | Auto-commit planning and explicit local-commit helper | current | no |

## Template facts warning

Most product, business, data, test, deploy, manual, and observability documents start as stubs. Do not infer project behavior from empty templates. A document becomes a fact source only after it contains project-specific content and its status is updated from `stub` to `draft`, `current`, or `verified`.

## Generated run records

- `docs/ai-dev/doc-update-runs/DUR-*.md` is optional check evidence.
- `docs/ai-dev/thread-check-runs/TC-*.md` is optional thread-check evidence.
- `docs/ai-dev/migration-runs/MIG-*.md` is optional skill application or update evidence.

These records are runtime artifacts and should not be versioned.
