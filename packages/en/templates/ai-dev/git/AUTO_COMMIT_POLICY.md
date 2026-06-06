# AUTO_COMMIT_POLICY

> Document status: current

## Purpose

Define the optional project-level auto-commit strategy. In this skill, auto-commit means **local git commit only**. Auto-stage and auto-commit are disabled by default, and automatic push is never allowed.

This policy can reduce cleanup cost after long-running work, documentation structure upgrades, or governance-script synchronization, but it does not replace user confirmation, tests, secret scanning, or main-session merge decisions.

## Default strategy

| Level | Meaning | Default state |
|---|---|---|
| `disabled` | No automatic stage or commit | Default |
| `manual_suggest` | Only show a commit plan and suggested command | Recommended default |
| `stage_only` | The script may stage explicitly listed paths but may not commit | Optional |
| `local_commit` | The script may create a local commit after checks pass | Explicit opt-in required |
| `push` | Push automatically to a remote | Forbidden |

## Hard constraints

- Auto-commit is off by default.
- A local commit may run only when both `docs/ai-dev/git/AUTO_COMMIT_CONFIG.json` and the CLI explicitly opt in.
- Automatic push is forbidden. Remote push, PR creation, and merge must be handled explicitly by the user or an external CI/review process.
- `.ai-secrets/`, `.env`, private keys, certificates, kubeconfig files, real tokens, real passwords, and real user-private data must never be committed.
- Auto-commit is forbidden when there is an active write/merge lock conflict, a blocked/conflict merge queue item, or a compact_count migration threshold without handoff.
- Auto-commit must not bypass `ai_doc_impact_check.py`, `thread_coordination_check.py`, or `architecture_check.py`.
- Unconfirmed business rules, data models, permission rules, state flows, or historical-data interpretations must not be encoded as confirmed facts in a commit message.
- Auto-commit must not turn subagent, fork, or worktree candidate conclusions into project facts. The main session must still adopt them.

## Enabling steps

1. Read this file and the auto-commit rules in `AGENTS.md`.
2. Edit `docs/ai-dev/git/AUTO_COMMIT_CONFIG.json`, setting `enabled` and the required capabilities to `true`.
3. Prefer a work branch; avoid auto-commit on protected branches such as `main`, `master`, `production`, `prod`, or `release`.
4. First run:

```bash
python scripts/project_auto_commit.py --plan
```

5. Create a local commit only after reviewing the scope, checks, and message:

```bash
python scripts/project_auto_commit.py --commit -m "docs: update AI governance strategy"
```

To let the script stage paths, list the paths explicitly:

```bash
python scripts/project_auto_commit.py --auto-stage --paths AGENTS.md docs/ai-dev/git/AUTO_COMMIT_POLICY.md --commit -m "docs: add auto-commit policy"
```

## Recommended commit granularity

- One commit should represent one semantic topic.
- Documentation governance upgrades, business features, refactors, test fixes, and security fixes should be separate commits.
- Large file sets should use a worktree, changeset, or manual commit review first.
- Auto-commit is suitable for documentation-structure upgrades, check-script synchronization, and small rule fixes; it is not suitable for high-risk production changes.

## Commit message format

Recommended:

```text
<type>: <summary>

- Why: <reason>
- Scope: <key files or modules>
- Checks: <commands run>
- Docs: <docs updated>
```

Commit messages must not include real secrets, real tokens, real passwords, real user-private data, unconfirmed business commitments, or unverified production status.

## Final task output

After using the auto-commit strategy, the task result must state:

```text
Auto-commit strategy: disabled/manual_suggest/stage_only/local_commit
Local commit performed: yes/no
Commit hash: <hash>/none
Push performed: no
Pre-commit checks: run/not run; result
Uncommitted changes: yes/no; notes
```
