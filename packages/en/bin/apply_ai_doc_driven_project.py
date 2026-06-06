#!/usr/bin/env python3
"""Conservatively apply ai-doc-driven-project templates to a target project.

Default is dry-run. Existing project-authored files are preserved. Update mode
migrates generated governance files so AGENTS.md metadata cannot drift away from
scripts, hooks, and trigger rules. AGENTS.md is stamped with the skill package
revision time, not the time this script is run in a target project.
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Iterable

SKILL_NAME = "ai-doc-driven-project"
DEFAULT_SKILL_VERSION = "0.3.4"
DEFAULT_SKILL_REVISION_TIME = "2026-06-06T04:45:00+08:00"
MARKER = "<!-- ai-doc-driven-project: suggested AGENTS additions -->"
UPDATE_MARKER = "<!-- ai-doc-driven-project: v0.3.4 generated-update additions -->"
REQUIRED_AGENTS_TERMS = [
    "CONTEXT_COMPACTION_POLICY",
    "AGENT_ROLE_POLICY",
    "thread_coordination_check.py",
    "template_install",
    "migration-runs",
]
STAMP_RE = re.compile(r"^\s*<!--\s*ai-skill:\s*ai-doc-driven-project\b.*?-->\s*\n?", re.IGNORECASE | re.DOTALL)


def norm(path: Path | str) -> str:
    return str(path).replace(os.sep, "/")


def metadata_comment(skill_version: str, revision_time: str) -> str:
    return f"<!-- ai-skill: {SKILL_NAME} skill-version: {skill_version} revision-time: {revision_time} -->"


def stamp_agents_text(text: str, skill_version: str, revision_time: str) -> str:
    stripped = STAMP_RE.sub("", text, count=1).lstrip("\ufeff\n")
    return metadata_comment(skill_version, revision_time) + "\n" + stripped.rstrip() + "\n"


def generated_update_block() -> str:
    return f"""{UPDATE_MARKER}

## ai-doc-driven-project 0.3.4 update additions

- The `AGENTS.md` ai-skill `revision-time` is the bundled skill revision time, not the time the skill is applied to a project.
- `update` mode may replace generated governance files such as scripts, hooks, Codex config, and `DOC_UPDATE_TRIGGERS.yml`; project fact documents remain preserve-only unless `--overwrite` is used.
- Codex hooks must use `thread_coordination_check.py --hook-json` for `Stop` and `SubagentStop`; default hooks must not write `TC-*` records on every turn.
- Documentation impact checks should use `--mode template_install` during initial template installation so stub templates are not mistaken for confirmed business facts.
- Strict merge checks may write run records explicitly with `--record`; routine hooks should remain advisory and non-mutating.
"""


def find_skill_root(script: Path, explicit: str | None = None) -> Path:
    if explicit:
        root = Path(explicit).resolve()
        if not (root / "templates" / "manifest.yml").exists():
            raise SystemExit(f"Missing templates/manifest.yml under {root}")
        return root
    for candidate in [script.parent, *script.parents]:
        if (candidate / "templates" / "manifest.yml").exists():
            return candidate
    raise SystemExit("Cannot locate skill root. Run from the skill package or pass --skill-root.")


def load_manifest(root: Path) -> dict[str, Any]:
    path = root / "templates" / "manifest.yml"
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
            data = yaml.safe_load(text)
        except Exception as exc:
            raise SystemExit(f"Cannot parse {path}; keep it JSON-compatible or install PyYAML: {exc}")
    if not isinstance(data, dict):
        raise SystemExit(f"Invalid manifest: {path}")
    return data


def rel_from_tree(source_root: Path, item: Path, target_root: str) -> str:
    return f"{target_root.rstrip('/')}/{item.relative_to(source_root).as_posix()}"


def matches_policy(rel: str, patterns: Iterable[str]) -> bool:
    rel = rel.replace("\\", "/")
    for pat in patterns:
        pat = str(pat).replace("\\", "/")
        if pat.endswith("/**") and (rel == pat[:-3].rstrip("/") or rel.startswith(pat[:-3].rstrip("/") + "/")):
            return True
        if pat.endswith("/*") and rel.startswith(pat[:-2].rstrip("/") + "/"):
            return True
        if pat == rel:
            return True
        if "*" in pat:
            import fnmatch
            if fnmatch.fnmatch(rel, pat):
                return True
    return False


class Writer:
    def __init__(self, target: Path, dry_run: bool, overwrite: bool, mode: str, manifest: dict[str, Any]) -> None:
        self.target = target.resolve()
        self.dry_run = dry_run
        self.overwrite = overwrite
        self.mode = mode
        self.manifest = manifest
        self.actions: list[str] = []
        self.warnings: list[str] = []
        self.changed: list[str] = []
        self.diffs: list[str] = []
        policy = manifest.get("update_policy") or {}
        self.safe_replace = [str(x) for x in policy.get("generated_safe_replace", [])]
        self.preserve_only = [str(x) for x in policy.get("preserve_only", [])]
        self.migration_report_dir = str(policy.get("migration_report_dir") or "docs/ai-dev/migration-runs")

    def log(self, text: str) -> None:
        self.actions.append(text)

    def warn(self, text: str) -> None:
        self.warnings.append(text)

    def mkdir(self, rel: str, keep: bool = False) -> None:
        path = self.target / rel
        if not path.exists():
            self.log(f"mkdir {norm(path)}")
            if not self.dry_run:
                path.mkdir(parents=True, exist_ok=True)
        if keep and rel != ".ai-secrets":
            self.write_if_missing(f"{rel.rstrip('/')}/.gitkeep", "")

    def _write(self, rel: str, content: str, action: str) -> None:
        path = self.target / rel
        self.log(f"{action} {norm(path)}")
        if not self.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self.changed.append(rel)

    def write_if_missing(self, rel: str, content: str) -> None:
        path = self.target / rel
        if path.exists() and not self.overwrite:
            self.log(f"skip existing {norm(path)}")
            return
        self._write(rel, content, "overwrite" if path.exists() else "write")

    def replace_generated(self, rel: str, content: str, source: Path) -> None:
        path = self.target / rel
        if path.exists():
            old = path.read_text(encoding="utf-8", errors="ignore")
            if old == content:
                self.log(f"skip generated {norm(path)}; already current")
                return
            self.diffs.append("\n".join(difflib.unified_diff(old.splitlines(), content.splitlines(), fromfile=rel+":old", tofile=rel+":new", lineterm=""))[:12000])
            self._write(rel, content, "replace generated")
        else:
            self._write(rel, content, f"copy {norm(source)} ->")

    def copy_file(self, source: Path, rel: str) -> None:
        content = source.read_text(encoding="utf-8", errors="ignore") if source.suffix.lower() in {".md", ".yml", ".yaml", ".json", ".toml", ".py", ".txt", ""} else None
        dest = self.target / rel
        if self.overwrite:
            self.log(("overwrite " if dest.exists() else "copy ") + f"{norm(source)} -> {norm(dest)}")
            if not self.dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
            self.changed.append(rel)
            return
        if self.mode == "update" and not matches_policy(rel, self.preserve_only) and matches_policy(rel, self.safe_replace):
            if content is None:
                self.log(("replace generated " if dest.exists() else "copy ") + f"{norm(source)} -> {norm(dest)}")
                if not self.dry_run:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, dest)
                self.changed.append(rel)
            else:
                self.replace_generated(rel, content, source)
            return
        if dest.exists():
            self.log(f"skip existing {norm(dest)}")
            return
        self.log(f"copy {norm(source)} -> {norm(dest)}")
        if not self.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        self.changed.append(rel)

    def copy_tree(self, source: Path, target_rel: str) -> None:
        if not source.exists():
            self.warn(f"missing template tree: {norm(source)}")
            return
        for item in sorted(source.rglob("*")):
            if item.is_file() and not any(part in {"__pycache__", ".pytest_cache"} for part in item.parts):
                self.copy_file(item, rel_from_tree(source, item, target_rel))

    def merge_agents(self, source: Path, rel: str, skill_version: str, revision_time: str) -> None:
        dest = self.target / rel
        template = stamp_agents_text(source.read_text(encoding="utf-8"), skill_version, revision_time)
        if not dest.exists() or self.overwrite:
            self.write_if_missing(rel, template)
            return
        current = dest.read_text(encoding="utf-8", errors="ignore")
        configured = MARKER in current or ("docs/ai-dev/DOCS_INDEX.md" in current and SKILL_NAME in current)
        if configured or self.mode == "update":
            stamped = stamp_agents_text(current, skill_version, revision_time)
            if any(term not in stamped for term in REQUIRED_AGENTS_TERMS) and UPDATE_MARKER not in stamped:
                stamped = stamped.rstrip() + "\n\n" + generated_update_block().rstrip() + "\n"
            if stamped != current:
                self._write(rel, stamped, "update ai-skill metadata / v0.3.4 block in")
            else:
                self.log(f"skip existing {norm(dest)}; AGENTS metadata and v0.3.4 block are current")
            return
        supplement = current.rstrip() + "\n\n" + MARKER + "\n\n" + template.strip() + "\n"
        supplement = stamp_agents_text(supplement, skill_version, revision_time)
        self._write(rel, supplement, "append suggested AGENTS sections and metadata stamp to")

    def append_gitignore(self, entries: Iterable[str]) -> None:
        path = self.target / ".gitignore"
        existing = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        lines = {line.strip() for line in existing.splitlines()}
        missing = [entry for entry in entries if entry and entry not in lines]
        if not missing:
            self.log("skip .gitignore; entries already present")
            return
        block = "\n# ai-doc-driven-project local files\n" + "\n".join(missing) + "\n"
        self.log("append .gitignore entries: " + ", ".join(missing))
        if not self.dry_run:
            path.write_text(existing.rstrip() + block if existing else block.lstrip(), encoding="utf-8")
        self.changed.append(".gitignore")

def skill_revision_time_from_manifest(manifest: dict[str, Any]) -> str:
    return str(manifest.get("skill_revision_time") or manifest.get("generated_at") or DEFAULT_SKILL_REVISION_TIME)


def render_local_secret_placeholder(language: str) -> str:
    return """# test-secrets.local.md

This file stays local only and must not be committed. It may contain test-environment or local-development credentials only. Keep all real values under `.ai-secrets/`.

## TEST_DATABASE_URL
Purpose: test database connection.
Value: <redacted>

## TEST_API_KEY
Purpose: test API calls.
Value: <redacted>
"""


def git_ignore_check(target: Path, writer: Writer) -> None:
    if not (target / ".git").exists():
        writer.log("skip git check-ignore; target is not a git repository")
        return
    if writer.dry_run:
        writer.log("skip git check-ignore in dry-run")
        return
    try:
        result = subprocess.run(["git", "check-ignore", ".ai-secrets/test-secrets.local.md"], cwd=target, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except FileNotFoundError:
        writer.warn("git not available; cannot verify .ai-secrets ignore rule")
        return
    if result.returncode == 0:
        writer.log("git check-ignore passed for .ai-secrets/test-secrets.local.md")
    else:
        writer.warn("git check-ignore did not confirm .ai-secrets/test-secrets.local.md; verify .gitignore and tracked files")


def write_application_record(writer: Writer, mode: str, skill_version: str, revision_time: str) -> None:
    report_dir = writer.target / writer.migration_report_dir
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    rel = f"{writer.migration_report_dir.rstrip('/')}/MIG-{stamp}.md"
    body = [
        f"# MIG-{stamp}",
        "",
        f"- Mode: {mode}",
        f"- Skill: {SKILL_NAME}",
        f"- Skill version: {skill_version}",
        f"- Skill revision time: {revision_time}",
        f"- Dry run: {writer.dry_run}",
        "",
        "## Changed files",
        "",
        *(f"- {item}" for item in sorted(set(writer.changed)) or ["none"]),
        "",
        "## Actions",
        "",
        *(f"- {item}" for item in writer.actions[:250]),
    ]
    if writer.diffs:
        body.extend(["", "## Diff preview", ""])
        for diff in writer.diffs[:10]:
            body.extend(["```diff", diff, "```"])
    if not writer.dry_run:
        report_dir.mkdir(parents=True, exist_ok=True)
    writer.write_if_missing(rel, "\n".join(body) + "\n")


def append_audit(writer: Writer, mode: str, skill_version: str, revision_time: str) -> None:
    if mode != "audit":
        return
    path = writer.target / "docs/ai-dev/PROJECT_AUDIT.md"
    record = (
        f"\n\n## Skill audit record - {dt.datetime.now().isoformat(timespec='seconds')}\n\n"
        "- Mode: audit\n"
        "- Single root entry: AGENTS.md\n"
        f"- AGENTS metadata: `{metadata_comment(skill_version, revision_time)}`\n"
        f"- Generated by: {SKILL_NAME} {skill_version}\n"
    )
    if not writer.dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        old = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else "# PROJECT_AUDIT\n\n> Document status: draft\n"
        path.write_text(old.rstrip() + record, encoding="utf-8")
    writer.log(f"append audit record to {norm(path)}")
    writer.changed.append("docs/ai-dev/PROJECT_AUDIT.md")


def apply(args: argparse.Namespace) -> Writer:
    skill_root = find_skill_root(Path(__file__).resolve(), args.skill_root)
    manifest = load_manifest(skill_root)
    skill_version = str(manifest.get("skill_version") or DEFAULT_SKILL_VERSION)
    revision_time = args.revision_time or skill_revision_time_from_manifest(manifest)
    language = str(manifest.get("language") or "en")

    target = Path(args.target).resolve()
    writer = Writer(target, dry_run=not args.write, overwrite=args.overwrite, mode=args.mode, manifest=manifest)
    if not target.exists():
        writer.mkdir(".")

    entry = manifest.get("entry") or (manifest.get("root_files") or [{}])[0]
    writer.merge_agents(skill_root / entry.get("source", "templates/AGENTS.md"), entry.get("target", "AGENTS.md"), skill_version, revision_time)

    for item in manifest.get("copy_trees", []):
        writer.copy_tree(skill_root / item["source"], item["target"])
    for rel in manifest.get("runtime_dirs", []):
        writer.mkdir(rel, keep=True)
    writer.append_gitignore(manifest.get("gitignore_entries", []))
    local_readme = next((item for item in manifest.get("local_only_files", []) if item.get("target") == ".ai-secrets/README.md"), {})
    writer.write_if_missing(".ai-secrets/README.md", str(local_readme.get("content") or "# .ai-secrets\n"))
    if args.include_test_secrets:
        writer.write_if_missing(".ai-secrets/test-secrets.local.md", render_local_secret_placeholder(language))
    append_audit(writer, args.mode, skill_version, revision_time)
    if args.record or (args.mode == "update" and args.write and not args.no_migration_report):
        write_application_record(writer, args.mode, skill_version, revision_time)
    git_ignore_check(target, writer)
    return writer


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["init", "audit", "update"], help="init new projects, audit in-progress projects, or update an existing doc structure")
    parser.add_argument("--target", default=".")
    parser.add_argument("--skill-root")
    parser.add_argument("--write", action="store_true", help="write changes; default is dry-run")
    parser.add_argument("--dry-run", action="store_true", help="accepted for readability; default behavior")
    parser.add_argument("--overwrite", action="store_true", help="overwrite existing files; use with care")
    parser.add_argument("--revision-time", help="Override AGENTS.md ai-skill revision-time. Intended only for skill maintainers/repackaging.")
    parser.add_argument("--include-test-secrets", "--create-test-secrets", action="store_true", help="create local .ai-secrets/test-secrets.local.md with redacted placeholders")
    parser.add_argument("--record", action="store_true", help="write a migration/application report under docs/ai-dev/migration-runs")
    parser.add_argument("--no-migration-report", action="store_true", help="with update --write, skip the default migration/application report")
    args = parser.parse_args()
    writer = apply(args)
    print("ai-doc-driven-project apply result")
    print(f"mode: {args.mode}")
    print(f"target: {Path(args.target).resolve()}")
    print(f"dry_run: {not args.write}")
    if writer.warnings:
        print("warnings:")
        for item in writer.warnings:
            print(f"- {item}")
    print("actions:")
    for item in writer.actions:
        print(f"- {item}")
    if writer.changed:
        print("changed_files:")
        for item in sorted(set(writer.changed)):
            print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
