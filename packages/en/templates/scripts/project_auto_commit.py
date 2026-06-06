#!/usr/bin/env python3
"""Optional local auto-commit helper for ai-doc-driven-project projects.

Default behavior is plan/suggest only. Local git commit is allowed only when
project config and CLI flags both explicitly opt in. This helper never pushes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

CONFIG_PATH = Path("docs/ai-dev/git/AUTO_COMMIT_CONFIG.json")
DEFAULT_PROTECTED_PATHS = [
    ".ai-secrets/**",
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*.kubeconfig",
    "**/id_rsa",
    "**/id_ed25519",
    "logs/**/*.log",
]
SECRET_RE = re.compile(r"(?i)\b(api[_-]?key|secret|token|password|passwd|pwd)\b\s*[:=]\s*['\"]?([^'\"\s#]{12,})")
SAFE_VALUE_HINTS = ["<redacted>", "redacted", "example", "placeholder", "changeme", "dummy", "your_", "xxx", "***"]


def norm_path(value: str | Path) -> str:
    path = str(value).replace("\\", "/")
    if path.startswith("./"):
        path = path[2:]
    return path


def run_git(root: Path, args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(["git", *args], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except FileNotFoundError:
        raise SystemExit("git is not available")
    if check and result.returncode != 0:
        raise SystemExit(result.stderr.strip() or result.stdout.strip() or f"git {' '.join(args)} failed")
    return result


def find_repo_root(start: Path) -> Path:
    result = run_git(start, ["rev-parse", "--show-toplevel"], check=False)
    if result.returncode != 0:
        raise SystemExit("project_auto_commit.py must run inside a git repository")
    return Path(result.stdout.strip()).resolve()


def load_config(root: Path) -> dict[str, Any]:
    path = root / CONFIG_PATH
    if not path.exists():
        return {
            "schema_version": 1,
            "enabled": False,
            "mode": "manual_suggest",
            "allow_auto_stage": False,
            "allow_auto_commit": False,
            "allow_auto_push": False,
            "protected_paths": DEFAULT_PROTECTED_PATHS,
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid {CONFIG_PATH}: {exc}")
    if not isinstance(data, dict):
        raise SystemExit(f"invalid {CONFIG_PATH}: root must be a JSON object")
    data.setdefault("protected_paths", DEFAULT_PROTECTED_PATHS)
    data.setdefault("enabled", False)
    data.setdefault("mode", "manual_suggest")
    data.setdefault("allow_auto_stage", False)
    data.setdefault("allow_auto_commit", False)
    data.setdefault("allow_auto_push", False)
    data.setdefault("max_files_per_commit", 50)
    data.setdefault("disallow_branches", ["main", "master", "production", "prod", "release"])
    data.setdefault("allow_protected_branch_commit", False)
    data.setdefault("require_checks", True)
    data.setdefault("checks", ["ai_doc_impact", "thread_coordination", "architecture"])
    return data


def matches(path: str, pattern: str) -> bool:
    path = norm_path(path)
    pattern = norm_path(pattern)
    if pattern.endswith("/**"):
        prefix = pattern[:-3].rstrip("/")
        return path == prefix or path.startswith(prefix + "/")
    return fnmatch.fnmatch(path, pattern)


def git_lines(root: Path, args: list[str]) -> list[str]:
    result = run_git(root, args, check=False)
    if result.returncode != 0:
        return []
    return [norm_path(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def staged_files(root: Path) -> list[str]:
    return sorted(set(git_lines(root, ["diff", "--name-only", "--cached"])))


def unstaged_files(root: Path) -> list[str]:
    files = set(git_lines(root, ["diff", "--name-only"]))
    files.update(git_lines(root, ["ls-files", "--others", "--exclude-standard"]))
    return sorted(files)


def current_branch(root: Path) -> str:
    result = run_git(root, ["branch", "--show-current"], check=False)
    return result.stdout.strip() or "DETACHED"


def protected_hits(files: list[str], patterns: list[str]) -> list[str]:
    return sorted({path for path in files if any(matches(path, pattern) for pattern in patterns)})


def safe_placeholder(value: str) -> bool:
    lowered = value.lower().strip('"\'` ,;')
    return not lowered or any(hint in lowered for hint in SAFE_VALUE_HINTS) or bool(re.fullmatch(r"[xX*_.-]{4,}", lowered))


def content_secret_hits(root: Path, files: list[str]) -> list[str]:
    hits: list[str] = []
    for rel in files:
        path = root / rel
        if not path.exists() or path.is_dir():
            continue
        try:
            if path.stat().st_size > 1_500_000:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for match in SECRET_RE.finditer(text):
            value = match.group(2)
            if not safe_placeholder(value):
                hits.append(f"{rel}: possible secret-like value near {match.group(1)}")
                break
    return hits


def run_builtin_check(root: Path, name: str, advisory: bool = False) -> tuple[int, str]:
    commands = {
        "ai_doc_impact": [sys.executable, "scripts/ai_doc_impact_check.py", "--staged"],
        "thread_coordination": [sys.executable, "scripts/thread_coordination_check.py", "--staged", "--strict"],
        "architecture": [sys.executable, "scripts/architecture_check.py", "--staged", "--advisory"],
    }
    cmd = commands.get(name)
    if cmd is None:
        return 1, f"unknown built-in check: {name}"
    script = root / cmd[1]
    if not script.exists():
        return 1, f"missing check script: {cmd[1]}"
    result = subprocess.run(cmd, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    output = (result.stdout + "\n" + result.stderr).strip()
    if advisory and result.returncode != 0:
        return 0, f"{name}: advisory failure suppressed: {output[:1000]}"
    return result.returncode, output[:2000]


def validate_commit_message(message: str) -> list[str]:
    issues: list[str] = []
    if not message.strip():
        issues.append("commit message is empty")
    if len(message.splitlines()[0]) > 100:
        issues.append("commit subject should be <= 100 characters")
    if SECRET_RE.search(message):
        issues.append("commit message appears to contain a secret-like value")
    return issues


def build_plan(root: Path, config: dict[str, Any]) -> dict[str, Any]:
    staged = staged_files(root)
    unstaged = unstaged_files(root)
    branch = current_branch(root)
    protected = protected_hits(staged + unstaged, [str(x) for x in config.get("protected_paths", DEFAULT_PROTECTED_PATHS)])
    secret_hits = content_secret_hits(root, staged + unstaged)
    return {
        "checked_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "repo_root": norm_path(root),
        "config_path": norm_path(CONFIG_PATH),
        "enabled": bool(config.get("enabled")),
        "mode": config.get("mode"),
        "allow_auto_stage": bool(config.get("allow_auto_stage")),
        "allow_auto_commit": bool(config.get("allow_auto_commit")),
        "allow_auto_push": bool(config.get("allow_auto_push")),
        "branch": branch,
        "staged_files": staged,
        "unstaged_files": unstaged,
        "protected_path_hits": protected,
        "secret_like_hits": secret_hits,
    }


def render_plan(plan: dict[str, Any]) -> str:
    lines = ["Project auto-commit plan", f"Checked at: {plan['checked_at']}", f"Repo: {plan['repo_root']}", ""]
    for key in ["enabled", "mode", "allow_auto_stage", "allow_auto_commit", "allow_auto_push", "branch"]:
        lines.append(f"- {key}: {plan.get(key)}")
    lines.append("")
    for label, key in [("Staged files", "staged_files"), ("Unstaged/untracked files", "unstaged_files"), ("Protected path hits", "protected_path_hits"), ("Secret-like hits", "secret_like_hits")]:
        items = plan.get(key) or []
        lines.append(f"{label}:" if items else f"{label}: none")
        lines.extend(f"- {item}" for item in items)
        lines.append("")
    lines.append("Default policy: plan/suggest only. To commit, enable AUTO_COMMIT_CONFIG.json and pass --commit with an explicit --message. This helper never pushes.")
    return "\n".join(lines)


def stage_paths(root: Path, paths: list[str], config: dict[str, Any]) -> None:
    if not paths:
        raise SystemExit("--auto-stage requires explicit --paths; stage-all is intentionally not supported by default")
    normalized = [norm_path(p) for p in paths]
    protected = protected_hits(normalized, [str(x) for x in config.get("protected_paths", DEFAULT_PROTECTED_PATHS)])
    if protected:
        raise SystemExit("refusing to stage protected paths: " + ", ".join(protected))
    run_git(root, ["add", "--", *normalized], check=True)


def enforce_commit_policy(root: Path, config: dict[str, Any], args: argparse.Namespace, staged: list[str]) -> None:
    if not config.get("enabled"):
        raise SystemExit("auto-commit is disabled in docs/ai-dev/git/AUTO_COMMIT_CONFIG.json")
    if not config.get("allow_auto_commit"):
        raise SystemExit("allow_auto_commit is false; only plan/suggest mode is allowed")
    if config.get("allow_auto_push"):
        raise SystemExit("allow_auto_push must remain false; this helper never pushes")
    if args.auto_stage and not config.get("allow_auto_stage"):
        raise SystemExit("--auto-stage requested but allow_auto_stage is false")
    branch = current_branch(root)
    disallowed = set(str(x) for x in config.get("disallow_branches", []))
    if branch in disallowed and not config.get("allow_protected_branch_commit"):
        raise SystemExit(f"refusing auto-commit on protected branch {branch!r}; use a work branch or change project policy")
    max_files = int(config.get("max_files_per_commit", 50))
    if len(staged) > max_files:
        raise SystemExit(f"refusing auto-commit with {len(staged)} staged files; max_files_per_commit={max_files}")
    protected = protected_hits(staged, [str(x) for x in config.get("protected_paths", DEFAULT_PROTECTED_PATHS)])
    if protected:
        raise SystemExit("refusing to commit protected paths: " + ", ".join(protected))
    secret_hits = content_secret_hits(root, staged)
    if secret_hits:
        raise SystemExit("refusing to commit possible secrets: " + "; ".join(secret_hits[:10]))
    message_issues = validate_commit_message(args.message or "")
    if message_issues:
        raise SystemExit("invalid commit message: " + "; ".join(message_issues))


def run_checks(root: Path, config: dict[str, Any], args: argparse.Namespace) -> list[str]:
    outputs: list[str] = []
    if args.no_checks:
        if not config.get("allow_skip_checks"):
            raise SystemExit("--no-checks is not allowed by project auto-commit policy")
        return ["checks skipped by explicit CLI flag and project policy"]
    if not config.get("require_checks", True):
        return ["checks disabled by project policy"]
    for check_name in config.get("checks", ["ai_doc_impact", "thread_coordination", "architecture"]):
        code, output = run_builtin_check(root, str(check_name), advisory=bool(args.advisory_checks))
        outputs.append(f"{check_name}: exit={code}")
        if code != 0:
            raise SystemExit(f"pre-commit check failed: {check_name}\n{output}")
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan or perform an explicitly enabled local git commit. Never pushes.")
    parser.add_argument("--project-root", "--target", dest="project_root", default=".")
    parser.add_argument("--plan", action="store_true", help="show current auto-commit status; default action")
    parser.add_argument("--commit", action="store_true", help="perform a local git commit when config and checks allow it")
    parser.add_argument("--auto-stage", action="store_true", help="stage explicit --paths before committing; requires allow_auto_stage=true")
    parser.add_argument("--paths", nargs="*", default=[], help="explicit paths allowed for --auto-stage")
    parser.add_argument("--message", "-m", help="commit message; required with --commit")
    parser.add_argument("--no-checks", action="store_true", help="skip built-in checks only if allow_skip_checks=true")
    parser.add_argument("--advisory-checks", action="store_true", help="treat built-in check failures as advisory; not recommended")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    start = Path(args.project_root).resolve()
    root = find_repo_root(start)
    os.chdir(root)
    config = load_config(root)

    if args.auto_stage:
        stage_paths(root, args.paths, config)

    plan = build_plan(root, config)
    if not args.commit:
        text = json.dumps(plan, indent=2, ensure_ascii=False) if args.json else render_plan(plan)
        print(text)
        return 0

    staged = staged_files(root)
    if not staged:
        raise SystemExit("nothing staged for commit")
    enforce_commit_policy(root, config, args, staged)
    check_outputs = run_checks(root, config, args)
    result = run_git(root, ["commit", "-m", args.message or ""], check=False)
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or result.stdout.strip() or "git commit failed")
    payload = {
        "committed": True,
        "branch": current_branch(root),
        "files": staged,
        "checks": check_outputs,
        "output": result.stdout.strip(),
        "push_performed": False,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else result.stdout.strip() + "\n\nPush performed: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
