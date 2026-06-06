# DOC_UPDATE_TRIGGERS

> Document status: current  
> Machine-readable source: `DOC_UPDATE_TRIGGERS.yml`  
> Human-readable purpose: explain when code, docs, sessions, agents, hooks, or operational changes require documentation updates.

## Rule-source principle

`DOC_UPDATE_TRIGGERS.yml` is the machine-readable source of truth. This Markdown file explains the policy for humans. When the YAML and this file disagree, update the YAML first and then regenerate or revise this explanation.

## Required check

Run a documentation impact check before finishing any non-trivial task:

```bash
python scripts/ai_doc_impact_check.py --staged
```

For advisory checks:

```bash
python scripts/ai_doc_impact_check.py --staged --advisory
```

For initial template installation:

```bash
python scripts/ai_doc_impact_check.py --mode template_install --advisory
```

For strict merge evidence:

```bash
python scripts/ai_doc_impact_check.py --staged --record
```

## Major trigger categories

| Category | Examples | Required action |
|---|---|---|
| Skill metadata | `AGENTS.md` ai-skill stamp, manifest version, revision-time | Keep `AGENTS.md`, `manifest.yml`, README, SKILL, and changelog aligned. |
| Requirements | new feature, changed scope, acceptance criteria | Update requirements, tasks, traceability, and product docs. |
| Bug fix | confirmed bug, regression, root cause | Update bug reports, test runs, tasks, and lessons learned. |
| Architecture | module boundary, dependency direction, ADR | Update architecture docs and run `architecture_check.py`. |
| Data model | schema, migration, lifecycle, backup/restore | Update data model, migrations, lifecycle, and confirmation records. |
| Security/privacy | secrets, permission, PII, auth, logs | Update security/privacy docs and run global secret scan. |
| UI/manual | user flow, UI copy, manual behavior | Update UI spec, user manual, quick start, and FAQ. |
| Deploy/release | deployment, rollback, versioning | Update deployment, operations, release checklist, changelog, rollback. |
| Codex session | compact, fork, subagent, worktree, side conversation | Update thread registry, handoff, merge policy, and usage log. |
| Agent policy | `.codex/agents`, `.codex/config.toml`, hooks | Update agent role policy and thread coordination checks. |
| Release package | build scripts, schemas, package validation, bilingual sync | Run package validation and update changelog. |

## Stub-template exception

During initial installation or structural update, many stub documents may be copied at once. That is not the same as confirming business rules, data models, or production behavior. Use:

```bash
python scripts/ai_doc_impact_check.py --mode template_install --advisory
```

This still checks core structure and secrets, but it does not treat copied stubs as confirmed business fact changes.

## Secret scanning

The checker scans every changed file for credential-like values. A file-level placeholder such as `<redacted>` does not suppress other real-looking values in the same file. `.env`, `.env.*`, private-key files, local secret files, and `.ai-secrets/**` are always treated as sensitive paths except `.env.example`.

## Human confirmation

Human confirmation is required before project facts are finalized for:

- business rules;
- data model and migration semantics;
- permission and privacy behavior;
- state flows and historical data interpretation;
- production release, rollback, and operational risk.

Use `--confirmed` only after confirmation is obtained or explicitly deferred and recorded.


## v0.3.3 addition: project auto-commit strategy

Machine rule `project_auto_commit_policy` triggers when:

- `docs/ai-dev/git/AUTO_COMMIT_POLICY.md` changes;
- `docs/ai-dev/git/AUTO_COMMIT_CONFIG.json` changes;
- `scripts/project_auto_commit.py` changes;
- task type is `auto_commit`, `git_commit`, `commit_policy`, or `version_control`.

User or project-owner confirmation is required before enabling local auto-commit. Auto-commit must not include `.ai-secrets/`, `.env`, private keys, certificates, kubeconfig files, or real tokens.
