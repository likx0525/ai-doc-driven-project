# ai-doc-driven-project

A Codex-oriented AI documentation governance skill for initializing, auditing,
and upgrading project documentation structures.

Chinese README: [README.zh-CN.md](README.zh-CN.md)

It creates a single root `AGENTS.md`, project fact documents under `docs/`, Codex
agent profiles under `.codex/agents`, optional hooks, thread coordination checks,
document-impact checks, architecture checks, secret-safety rules, and an optional
local-only auto-commit policy.

## Packages

- `packages/zh`: Chinese skill package.
- `packages/en`: English skill package.

## Install / use from source

```bash
python packages/en/bin/apply_skill.py init --target /path/to/project --dry-run
python packages/en/bin/apply_skill.py init --target /path/to/project --write

python packages/zh/bin/apply_skill.py init --target /path/to/project --dry-run
python packages/zh/bin/apply_skill.py init --target /path/to/project --write
```

## Validate

```bash
python -m pytest
python scripts/clean_runtime_artifacts.py
python packages/zh/bin/validate_skill_package.py --root packages/zh
python packages/en/bin/validate_skill_package.py --root packages/en --english
```

## License

The repository source is MIT licensed. Generated template output may be incorporated
into the target project and governed by that target project's license; see
`TEMPLATE_OUTPUT_LICENSE.md`.

## Security

Do not open public issues containing credentials, private logs, or personal data.
Follow `SECURITY.md` for vulnerability reports.
