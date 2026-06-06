# Contributing

Thank you for improving ai-doc-driven-project. This repository contains generated
skill packages in two language variants. Keep changes auditable and synchronized.

## Required checks before a pull request

Run from the repository root:

```bash
python -m pytest
python scripts/clean_runtime_artifacts.py
python packages/zh/bin/validate_skill_package.py --root packages/zh
python packages/en/bin/validate_skill_package.py --root packages/en --english
```

## Template change rules

- If you add or move a template, update `templates/manifest.yml`.
- If a generated project document changes, update `templates/ai-dev/DOCS_INDEX.md` when applicable.
- If a document update rule changes, update `templates/ai-dev/DOC_UPDATE_TRIGGERS.yml` and the human-readable Markdown file.
- If a script behavior changes, update tests and schemas where applicable.
- If a Codex agent changes, keep `developer_instructions` explicit and update `AGENT_ROLE_POLICY.md` when the role boundary changes.
- Keep zh/en package structures equivalent unless a file is intentionally language-specific.
- Do not commit `.ai-secrets/`, `.env`, real tokens, runtime run records, or generated archive files.

## Version and revision time

`AGENTS.md` metadata uses the skill package revision time, not the time a user
runs the skill. When changing the package version, update the version and
revision time in both language packages consistently.

## Pull request expectations

Use the PR template checklist. Describe whether your change affects:

- Generated target-project files.
- Skill package packaging behavior.
- Runtime checks or hooks.
- Security posture.
- zh/en synchronization.
