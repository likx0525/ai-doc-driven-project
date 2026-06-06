# Compatibility Notes

This skill is designed around Codex-style project instructions and project-local
configuration files:

- Root `AGENTS.md` as the primary project instruction entry.
- Project-local `.codex/agents/*.toml` custom agent profiles.
- Project-local `.codex/config.toml` agent limits.
- Project-local `.codex/hooks.json` lifecycle hook examples.

Hooks are advisory examples. Review and trust project hooks before enabling them in
a local environment. If the Codex hook schema, agent profile format, or AGENTS.md
loading behavior changes, update:

- `templates/codex-config/hooks.json`
- `templates/codex-config/config.toml`
- `templates/codex-agents/*.toml`
- `templates/scripts/thread_coordination_check.py`
- related tests and schemas

Keep `templates/AGENTS.md` compact enough to remain practical as a root project
instruction file.
