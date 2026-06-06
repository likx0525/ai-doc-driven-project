#!/usr/bin/env python3
"""Check whether a project change requires documentation updates.

The machine-readable rule source is docs/ai-dev/DOC_UPDATE_TRIGGERS.yml.

Exit codes:
  0: passed
  1: required docs are missing, not touched, or forbidden/sensitive content is detected
  2: configuration/tooling error
  3: human confirmation is required
"""
from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

CONFIG_PATH = Path("docs/ai-dev/DOC_UPDATE_TRIGGERS.yml")
RUN_DIR = Path("docs/ai-dev/doc-update-runs")
CORE_REQUIRED = [
    Path("AGENTS.md"),
    Path("docs/ai-dev/DOCS_INDEX.md"),
    Path("docs/ai-dev/DOC_UPDATE_TRIGGERS.md"),
    Path("docs/ai-dev/DOC_UPDATE_TRIGGERS.yml"),
]
GLOBAL_SENSITIVE_PATHS = [
    ".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "*.kubeconfig", "*.local.secret", "*.local.secrets", ".ai-secrets/**"
]
SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("named_secret", re.compile(r"(?i)\b(api[_-]?key|secret|token|password|passwd|pwd)\b\s*[:=]\s*['\"]?([^'\"\s#]{12,})")),
    ("database_url", re.compile(r"(?i)\b(database_url|db_url|dsn)\b\s*[:=]\s*['\"]?([a-z][a-z0-9+.-]+://[^\s'\"]{12,})")),
]
SAFE_VALUE_HINTS = ["<redacted>", "redacted", "example", "placeholder", "changeme", "dummy", "your_", "xxx", "***", "<token>", "<secret>", "<password>"]


def norm_path(value: str | Path) -> str:
    path = str(value).replace("\\", "/")
    if path.startswith("./"):
        path = path[2:]
    return path


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        print(f"ERROR: missing config: {path}", file=sys.stderr)
        raise SystemExit(2)
    raw = path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except Exception as exc:
            print("ERROR: PyYAML is required only when DOC_UPDATE_TRIGGERS.yml is not JSON-compatible YAML.", file=sys.stderr)
            raise SystemExit(2) from exc
        try:
            data = yaml.safe_load(raw) or {}
        except Exception as exc:
            print(f"ERROR: failed to parse {path}: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
    if not isinstance(data, dict):
        print(f"ERROR: {path} must contain a mapping/object.", file=sys.stderr)
        raise SystemExit(2)
    return data


def normalize_triggers(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = data.get("triggers", data)
    if not isinstance(raw, dict):
        print("ERROR: trigger config must contain a mapping named 'triggers'.", file=sys.stderr)
        raise SystemExit(2)
    out: dict[str, dict[str, Any]] = {}
    for key, value in raw.items():
        if not isinstance(value, dict):
            print(f"ERROR: trigger {key!r} must be a mapping.", file=sys.stderr)
            raise SystemExit(2)
        out[str(key)] = value
    return out


def git_lines(args: list[str], root: Path) -> list[str]:
    try:
        result = subprocess.run(["git", *args], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    except FileNotFoundError:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def changed_files_from_git(args: argparse.Namespace, root: Path) -> list[str]:
    if args.changed:
        return sorted({norm_path(item) for item in args.changed if item.strip()})
    if args.staged:
        return sorted({norm_path(item) for item in git_lines(["diff", "--name-only", "--cached"], root)})
    if args.since:
        return sorted({norm_path(item) for item in git_lines(["diff", "--name-only", args.since], root)})
    changed = set(git_lines(["diff", "--name-only", "HEAD", "--"], root))
    changed.update(git_lines(["ls-files", "--others", "--exclude-standard"], root))
    return sorted({norm_path(item) for item in changed})


def matches_glob(path: str, pattern: str) -> bool:
    path = norm_path(path)
    pattern = norm_path(pattern)
    if not pattern:
        return False
    if pattern.endswith("/**"):
        prefix = pattern[:-3].rstrip("/")
        return path == prefix or path.startswith(prefix + "/")
    if pattern.endswith("/"):
        prefix = pattern.rstrip("/")
        return path == prefix or path.startswith(prefix + "/")
    return fnmatch.fnmatch(path, pattern)


def any_path_matches(paths: Iterable[str], patterns: Iterable[str]) -> bool:
    return any(matches_glob(path, pattern) for path in paths for pattern in patterns)


def doc_exists(root: Path, doc: str) -> bool:
    doc = norm_path(doc)
    if any(ch in doc for ch in "*?["):
        return bool(list(root.glob(doc)))
    path = root / doc
    return path.is_dir() if doc.endswith("/") else path.exists()


def doc_touched(changed: Iterable[str], doc: str) -> bool:
    doc = norm_path(doc)
    for path in changed:
        path = norm_path(path)
        if any(ch in doc for ch in "*?[") and matches_glob(path, doc):
            return True
        if doc.endswith("/"):
            prefix = doc.rstrip("/")
            if path == prefix or path.startswith(prefix + "/"):
                return True
        elif path == doc or path.startswith(doc.rstrip("/") + "/"):
            return True
    return False


def safe_placeholder(value: str) -> bool:
    lowered = value.lower().strip('"\'` ,;')
    if not lowered:
        return True
    if any(hint in lowered for hint in SAFE_VALUE_HINTS):
        return True
    if re.fullmatch(r"[xX*_.-]{4,}", lowered):
        return True
    return False


def file_secret_issues(path: Path) -> list[str]:
    issues: list[str] = []
    try:
        if not path.exists() or path.is_dir() or path.stat().st_size > 1_500_000:
            return issues
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return issues
    for name, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group(match.lastindex or 0)
            if safe_placeholder(value):
                continue
            snippet = match.group(0)[:100].replace("\n", " ")
            issues.append(f"possible {name}: {snippet}")
    return issues


def global_sensitive_issues(root: Path, changed: list[str]) -> list[str]:
    issues: list[str] = []
    for rel in changed:
        if rel == ".env.example":
            continue
        sensitive_path = any(matches_glob(rel, pat) for pat in GLOBAL_SENSITIVE_PATHS)
        content_issues = file_secret_issues(root / rel)
        if sensitive_path:
            issues.append(f"{rel}: sensitive local/credential path changed; verify it is not committed or contains only safe placeholders")
        for issue in content_issues:
            issues.append(f"{rel}: {issue}")
    return issues


def forbidden_path_issues(root: Path, changed: list[str], trigger: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    forbidden = trigger.get("forbidden_locations") or []
    for item in forbidden:
        if isinstance(item, str):
            patterns = [item]
            reason = "forbidden location"
        elif isinstance(item, dict):
            patterns = item.get("paths") or []
            reason = str(item.get("reason") or "forbidden location")
        else:
            continue
        if isinstance(patterns, str):
            patterns = [patterns]
        for changed_path in changed:
            if not any(matches_glob(changed_path, pat) for pat in patterns):
                continue
            if changed_path == ".env.example":
                continue
            content_issues = file_secret_issues(root / changed_path)
            if not content_issues:
                issues.append(f"{changed_path}: {reason}")
            for content_issue in content_issues:
                issues.append(f"{changed_path}: {reason}; {content_issue}")
    return issues


def triggered_by_task_type(task_types: list[str], trigger: dict[str, Any]) -> bool:
    detect = trigger.get("detect") or {}
    expected = detect.get("task_types") or []
    if isinstance(expected, str):
        expected = [expected]
    return bool(set(task_types).intersection(str(item) for item in expected))


def triggered_by_paths(changed: list[str], trigger: dict[str, Any]) -> bool:
    detect = trigger.get("detect") or {}
    patterns = detect.get("paths") or []
    if isinstance(patterns, str):
        patterns = [patterns]
    return any_path_matches(changed, [str(item) for item in patterns])


def build_report(root: Path, changed: list[str], task_types: list[str], advisory: bool, confirmed: bool, mode: str) -> tuple[dict[str, Any], int]:
    missing_core = [str(path) for path in CORE_REQUIRED if not (root / path).exists()]
    data = load_yaml(root / CONFIG_PATH)
    triggers = normalize_triggers(data)
    template_install = mode in {"init", "template_install"}

    hits: list[dict[str, Any]] = []
    all_missing: list[str] = []
    all_not_touched: list[str] = []
    all_forbidden: list[str] = global_sensitive_issues(root, changed)
    all_confirmations: list[str] = []

    for trigger_id, trigger in triggers.items():
        by_type = triggered_by_task_type(task_types, trigger)
        by_path = False if template_install else triggered_by_paths(changed, trigger)
        if not (by_type or by_path):
            continue
        ignore_when = trigger.get("ignore_when") or {}
        ignored_task_types = set(str(x) for x in (ignore_when.get("task_types") or [])) if isinstance(ignore_when, dict) else set()
        if ignored_task_types.intersection(task_types):
            continue

        required = [str(item) for item in (trigger.get("required_docs") or [])]
        suggested = [str(item) for item in (trigger.get("suggested_docs") or [])]
        missing = [doc for doc in required if not doc_exists(root, doc)]
        not_touched = [] if template_install else [doc for doc in required if doc_exists(root, doc) and not doc_touched(changed, doc)]
        forbidden = forbidden_path_issues(root, changed, trigger)
        confirmations = [] if template_install else [str(item) for item in (trigger.get("confirmation_required") or [])]

        all_missing.extend(f"{trigger_id}: {doc}" for doc in missing)
        all_not_touched.extend(f"{trigger_id}: {doc}" for doc in not_touched)
        all_forbidden.extend(f"{trigger_id}: {issue}" for issue in forbidden)
        all_confirmations.extend(f"{trigger_id}: {item}" for item in confirmations)
        hits.append({
            "id": trigger_id,
            "description": trigger.get("description", ""),
            "matched_by": [x for x, ok in [("task_type", by_type), ("path", by_path)] if ok],
            "required_docs": required,
            "suggested_docs": suggested,
            "missing_required_docs": missing,
            "required_docs_not_touched": not_touched,
            "forbidden_issues": forbidden,
            "confirmation_required": confirmations,
        })

    exit_code = 0
    if missing_core or all_missing or all_forbidden:
        exit_code = 1
    if all_not_touched and not advisory:
        exit_code = 1
    if exit_code == 0 and all_confirmations and not confirmed:
        exit_code = 3
    report = {
        "checked_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "mode": mode,
        "changed_files": changed,
        "task_types": task_types,
        "triggered": hits,
        "missing_core_files": missing_core,
        "sensitive_issues": all_forbidden,
        "summary": {
            "trigger_count": len(hits),
            "missing_required_count": len(all_missing) + len(missing_core),
            "required_not_touched_count": len(all_not_touched),
            "forbidden_issue_count": len(all_forbidden),
            "confirmation_required_count": len(all_confirmations),
            "advisory": advisory,
            "confirmed": confirmed,
            "template_install_mode": template_install,
        },
    }
    return report, exit_code


def render_text(report: dict[str, Any], exit_code: int) -> str:
    lines = ["AI document impact check", f"Checked at: {report['checked_at']}", f"Mode: {report.get('mode','normal')}", f"Exit code: {exit_code}", ""]
    changed = report.get("changed_files") or []
    lines.append("Changed files:" if changed else "Changed files: none detected. Use --changed, --staged, --since, or --task-type when needed.")
    lines.extend(f"- {item}" for item in changed)
    lines.append("")
    if report.get("missing_core_files"):
        lines.append("Missing core files:")
        lines.extend(f"- {item}" for item in report["missing_core_files"])
        lines.append("")
    if report.get("sensitive_issues"):
        lines.append("Sensitive / forbidden issues:")
        lines.extend(f"- {item}" for item in report["sensitive_issues"])
        lines.append("")
    hits = report.get("triggered") or []
    if not hits:
        lines.append("Triggered rules: none")
    else:
        lines.append("Triggered rules:")
        for hit in hits:
            lines.append(f"- {hit['id']}: {hit.get('description','')}")
            for label, key in [("required_docs", "required_docs"), ("suggested_docs", "suggested_docs"), ("MISSING required docs", "missing_required_docs"), ("required docs not touched", "required_docs_not_touched"), ("FORBIDDEN / sensitive content issues", "forbidden_issues"), ("human confirmation required", "confirmation_required")]:
                if hit.get(key):
                    lines.append(f"  {label}:")
                    lines.extend(f"  - {doc}" for doc in hit[key])
    lines.append("")
    lines.append("Summary:")
    for key, value in report.get("summary", {}).items():
        lines.append(f"- {key}: {value}")
    if report.get("summary", {}).get("required_not_touched_count"):
        lines.append("If a required document is already current, rerun with --advisory or record the reason in the task result / DUR file.")
    if report.get("summary", {}).get("confirmation_required_count") and not report.get("summary", {}).get("confirmed"):
        lines.append("Human confirmation is required. Rerun with --confirmed only after confirmation is obtained or explicitly deferred.")
    return "\n".join(lines)


def write_record(root: Path, report: dict[str, Any], text: str) -> Path:
    run_dir = root / RUN_DIR
    run_dir.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = run_dir / f"DUR-{stamp}.md"
    body = [
        f"# DUR-{stamp}", "", f"- Checked at: {report['checked_at']}", f"- Mode: {report.get('mode','normal')}",
        f"- Trigger count: {report['summary']['trigger_count']}",
        f"- Missing required docs: {report['summary']['missing_required_count']}",
        f"- Required docs not touched: {report['summary']['required_not_touched_count']}",
        f"- Forbidden issues: {report['summary']['forbidden_issue_count']}",
        f"- Confirmation required: {report['summary']['confirmation_required_count']}", "", "```text", text, "```", "",
    ]
    path.write_text("\n".join(body), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check documentation impact from changed files and DOC_UPDATE_TRIGGERS.yml.")
    parser.add_argument("--project-root", "--target", dest="project_root", default=".", help="Project root. Default: current directory.")
    parser.add_argument("--changed", nargs="*", help="Explicit changed file list.")
    parser.add_argument("--staged", action="store_true", help="Use git staged files.")
    parser.add_argument("--since", help="Use git diff --name-only <REV>.")
    parser.add_argument("--task-type", action="append", default=[], help="Explicit trigger/task type, e.g. data_model_change.")
    parser.add_argument("--mode", choices=["normal", "init", "template_install"], default="normal", help="Use init/template_install for initial stub template installation.")
    parser.add_argument("--record", "--write-run", dest="record", action="store_true", help="Write docs/ai-dev/doc-update-runs/DUR-*.md.")
    parser.add_argument("--strict", action="store_true", help="Compatibility flag; strict behavior is default unless --advisory is used.")
    parser.add_argument("--advisory", action="store_true", help="Warn about required docs not touched but do not fail for that condition.")
    parser.add_argument("--confirmed", action="store_true", help="Indicate human confirmation requirements have been satisfied or explicitly deferred.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    os.chdir(root)
    changed = changed_files_from_git(args, root)
    report, exit_code = build_report(root, changed, [str(item) for item in args.task_type], args.advisory, args.confirmed, args.mode)
    text = json.dumps(report, ensure_ascii=False, indent=2) if args.json else render_text(report, exit_code)
    if args.record:
        record_path = write_record(root, report, text)
        if args.json:
            report["record_path"] = norm_path(record_path.relative_to(root))
            text = json.dumps(report, ensure_ascii=False, indent=2)
        else:
            text += f"\n\nRecord written: {norm_path(record_path.relative_to(root))}"
    print(text)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
