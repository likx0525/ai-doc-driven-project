#!/usr/bin/env python3
"""Check Codex thread coordination, agent role constraints, and compact_count policy.

Exit codes:
  0: passed or advisory-only findings
  1: policy violations detected
  2: configuration/tooling error
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

SKILL_NAME = "ai-doc-driven-project"
STAMP_RE = re.compile(r"^\s*<!--\s*ai-skill:\s*ai-doc-driven-project\b(?P<body>.*?)-->\s*", re.IGNORECASE | re.DOTALL)
REVISION_RE = re.compile(r"revision-time:\s*([^\s>]+)")
VERSION_RE = re.compile(r"skill-version:\s*([^\s>]+)")
CORE_DOCS = [
    "AGENTS.md",
    "docs/ai-dev/orchestration/AGENT_ROLE_POLICY.md",
    "docs/ai-dev/orchestration/CONTEXT_COMPACTION_POLICY.md",
    "docs/ai-dev/orchestration/THREAD_REGISTRY.md",
    "docs/ai-dev/orchestration/THREAD_HANDOFFS.md",
    "docs/ai-dev/orchestration/MERGE_POLICY.md",
    "docs/ai-dev/concurrency/SESSIONS.md",
    "docs/ai-dev/concurrency/LOCKS.md",
    "docs/ai-dev/concurrency/MERGE_QUEUE.md",
]
HIGH_RISK_TASK_TYPES = {"security", "privacy", "secret_change", "credential_change", "data_migration", "migration", "deployment", "release", "rollback", "architecture_change", "historical_data_interpretation", "permission_change"}


def norm_path(value: str | Path) -> str:
    path = str(value).replace("\\", "/")
    if path.startswith("./"):
        path = path[2:]
    return path


def git_lines(args: list[str], root: Path) -> list[str]:
    try:
        result = subprocess.run(["git", *args], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    except FileNotFoundError:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def changed_files(args: argparse.Namespace, root: Path) -> list[str]:
    if args.changed:
        return sorted({norm_path(item) for item in args.changed if item.strip()})
    if args.staged:
        return sorted({norm_path(item) for item in git_lines(["diff", "--name-only", "--cached"], root)})
    if args.since:
        return sorted({norm_path(item) for item in git_lines(["diff", "--name-only", args.since], root)})
    changed = set(git_lines(["diff", "--name-only", "HEAD", "--"], root))
    changed.update(git_lines(["ls-files", "--others", "--exclude-standard"], root))
    return sorted({norm_path(item) for item in changed})


def matches(path: str, pattern: str) -> bool:
    path = norm_path(path)
    pattern = norm_path(pattern)
    if pattern.endswith("/**"):
        prefix = pattern[:-3].rstrip("/")
        return path == prefix or path.startswith(prefix + "/")
    return fnmatch.fnmatch(path, pattern)


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_table_records(text: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    header: list[str] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not (line.startswith("|") and line.endswith("|")):
            header = None
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
            continue
        if header is None:
            header = cells
            continue
        if len(cells) == len(header):
            records.append({header[i]: cells[i] for i in range(len(cells))})
    return records


def parse_stamp(root: Path) -> tuple[list[str], list[str], dict[str, str]]:
    issues: list[str] = []
    warnings: list[str] = []
    info: dict[str, str] = {}
    text = read_text(root, "AGENTS.md")
    if not text:
        issues.append("AGENTS.md missing")
        return issues, warnings, info
    match = STAMP_RE.match(text)
    if not match:
        issues.append("AGENTS.md first line is missing ai-skill metadata comment")
        return issues, warnings, info
    body = match.group("body") or ""
    rev = REVISION_RE.search(body)
    version = VERSION_RE.search(body)
    if not rev:
        issues.append("AGENTS.md ai-skill metadata is missing revision-time")
    else:
        value = rev.group(1)
        info["revision_time"] = value
        try:
            dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            issues.append(f"AGENTS.md revision-time is not valid ISO-8601: {value}")
    if not version:
        warnings.append("AGENTS.md ai-skill metadata has no skill-version; recommended format includes skill-version")
    else:
        info["skill_version"] = version.group(1)
    return issues, warnings, info


def load_toml(path: Path) -> dict[str, Any]:
    try:
        import tomllib
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Python 3.11+ tomllib is required to validate TOML") from exc
    with path.open("rb") as fh:
        return tomllib.load(fh)


def check_codex_config(root: Path) -> tuple[list[str], list[str], dict[str, Any]]:
    issues: list[str] = []
    warnings: list[str] = []
    info: dict[str, Any] = {}
    path = root / ".codex/config.toml"
    if not path.exists():
        warnings.append(".codex/config.toml missing; subagent max_threads/max_depth defaults depend on Codex configuration")
        return issues, warnings, info
    try:
        data = load_toml(path)
    except Exception as exc:
        issues.append(f".codex/config.toml invalid TOML: {exc}")
        return issues, warnings, info
    agents = data.get("agents") or {}
    if not isinstance(agents, dict):
        issues.append(".codex/config.toml [agents] must be a table")
        return issues, warnings, info
    max_threads = agents.get("max_threads")
    max_depth = agents.get("max_depth")
    info = {"max_threads": max_threads, "max_depth": max_depth}
    if not isinstance(max_threads, int):
        warnings.append(".codex/config.toml should set [agents].max_threads")
    elif max_threads > 6:
        warnings.append("[agents].max_threads > 6 can create unnecessary fan-out")
    if not isinstance(max_depth, int):
        warnings.append(".codex/config.toml should set [agents].max_depth")
    elif max_depth > 1:
        issues.append("[agents].max_depth > 1 is not allowed by this skill; prevent recursive delegation")
    return issues, warnings, info


def check_agents(root: Path) -> tuple[list[str], list[str], list[dict[str, str]]]:
    issues: list[str] = []
    warnings: list[str] = []
    agents: list[dict[str, str]] = []
    agent_dir = root / ".codex/agents"
    if not agent_dir.exists():
        warnings.append(".codex/agents directory missing; custom agent role enforcement cannot run")
        return issues, warnings, agents
    files = sorted(agent_dir.glob("*.toml"))
    if not files:
        warnings.append(".codex/agents contains no *.toml files")
        return issues, warnings, agents
    for path in files:
        try:
            data = load_toml(path)
        except Exception as exc:
            issues.append(f"{norm_path(path.relative_to(root))}: invalid TOML: {exc}")
            continue
        record = {"file": norm_path(path.relative_to(root))}
        for field in ["name", "description", "developer_instructions"]:
            value = data.get(field)
            if not isinstance(value, str) or not value.strip():
                issues.append(f"{record['file']}: missing non-empty {field}")
            else:
                record[field] = value.strip().splitlines()[0][:120]
        instructions = str(data.get("developer_instructions") or "").lower()
        if instructions and not any(term in instructions for term in ["handoff", "merge", "main thread", "project fact"]):
            warnings.append(f"{record['file']}: developer_instructions should mention handoff/merge/main-thread fact boundary")
        agents.append(record)
    if not any(item.get("name") == "main-session-coordinator" for item in agents):
        issues.append("missing .codex/agents/main-session-coordinator.toml")
    return issues, warnings, agents


def numeric(value: str) -> int | None:
    match = re.search(r"(\d+)", value)
    return int(match.group(1)) if match else None


def compact_records(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for rel in ["docs/ai-dev/concurrency/SESSIONS.md", "docs/ai-dev/orchestration/THREAD_REGISTRY.md", "docs/codex/CODEX_USAGE_LOG.md"]:
        text = read_text(root, rel)
        if not text:
            continue
        for rec in parse_table_records(text):
            key = next((k for k in rec if "compact" in k.lower()), None)
            if not key:
                continue
            count = numeric(rec.get(key, ""))
            if count is not None:
                source = next((rec.get(k) for k in rec if k.lower() in {"session", "thread id", "thread", "id"} or "session" in k.lower()), "unknown")
                records.append({"file": rel, "source": source or "unknown", "compact_count": count})
        for match in re.finditer(r"compact_count\s*[：:]\s*(\d+)\+?", text, re.IGNORECASE):
            records.append({"file": rel, "source": "inline", "compact_count": int(match.group(1))})
    seen: set[tuple[str, str, int]] = set()
    out: list[dict[str, Any]] = []
    for rec in records:
        key = (str(rec["file"]), str(rec["source"]), int(rec["compact_count"]))
        if key not in seen:
            seen.add(key)
            out.append(rec)
    return out


def has_real_handoff(root: Path) -> bool:
    text = read_text(root, "docs/ai-dev/orchestration/THREAD_HANDOFFS.md") + "\n" + read_text(root, "docs/ai-dev/orchestration/HANDOFF.md")
    return bool(re.search(r"HO-\d{8}-\d{3}", text))


def check_compaction(root: Path, args: argparse.Namespace) -> tuple[list[str], list[str], list[dict[str, Any]]]:
    issues: list[str] = []
    warnings: list[str] = []
    records = compact_records(root)
    max_seen = max([int(r["compact_count"]) for r in records], default=0)
    if not records:
        warnings.append("no compact_count records found; keep SESSIONS.md / THREAD_REGISTRY.md updated after compact events")
    for rec in records:
        count = int(rec["compact_count"])
        label = f"{rec['file']} ({rec['source']}): compact_count={count}"
        if count >= args.hard_compactions:
            issues.append(label + " exceeds hard policy; stop new work and create a new session handoff")
        elif count >= args.max_compactions:
            issues.append(label + " reached migration threshold; create handoff and use /new or /fork before non-trivial work")
        elif count >= 1:
            warnings.append(label + " requires externalized state in docs before continuing")
    if set(args.task_type).intersection(HIGH_RISK_TASK_TYPES) and max_seen >= 1:
        issues.append("high-risk task with compact_count >= 1; prefer new session with handoff before continuing")
    if (max_seen >= args.max_compactions or args.require_handoff or args.event in {"PreCompact", "PostCompact", "SubagentStop"}) and not has_real_handoff(root):
        warnings.append("no real HO-YYYYMMDD-NNN handoff record found; create THREAD_HANDOFFS entry before migration or merge")
    return issues, warnings, records


def check_locks(root: Path) -> tuple[list[str], list[str], list[dict[str, str]]]:
    issues: list[str] = []
    warnings: list[str] = []
    records = parse_table_records(read_text(root, "docs/ai-dev/concurrency/LOCKS.md"))
    active: dict[str, list[dict[str, str]]] = {}
    for rec in records:
        normalized = {k.lower(): v for k, v in rec.items()}
        status = next((v for k, v in normalized.items() if k == "status"), "").lower()
        lock_type = next((v for k, v in normalized.items() if "type" in k), "").lower()
        target = next((v for k, v in normalized.items() if "target" in k or "module" in k or "file" in k), "")
        if not target or status != "active" or lock_type not in {"write", "merge"}:
            continue
        active.setdefault(target, []).append(rec)
    for target, rows in active.items():
        if len(rows) > 1:
            issues.append(f"active write/merge lock conflict on {target}: {len(rows)} active locks")
    if not records:
        warnings.append("LOCKS.md has no lock records; this is fine for single-thread work, but multi-session edits must record locks")
    return issues, warnings, records


def check_merge_queue(root: Path) -> tuple[list[str], list[str], list[dict[str, str]]]:
    issues: list[str] = []
    warnings: list[str] = []
    records = parse_table_records(read_text(root, "docs/ai-dev/concurrency/MERGE_QUEUE.md"))
    for rec in records:
        status = " ".join(rec.values()).lower()
        identifier = next(iter(rec.values()), "unknown")
        if "conflict" in status or "blocked" in status:
            issues.append(f"MERGE_QUEUE contains unresolved blocked/conflict item: {identifier}")
        elif "pending" in status or "merging" in status:
            warnings.append(f"MERGE_QUEUE contains unfinished item: {identifier}")
    return issues, warnings, records


def check_core_docs(root: Path) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    for rel in CORE_DOCS:
        if not (root / rel).exists():
            issues.append(f"missing required coordination doc: {rel}")
    for rel in ["scripts/ai_doc_impact_check.py", "scripts/architecture_check.py", "scripts/thread_coordination_check.py"]:
        if not (root / rel).exists():
            warnings.append(f"{rel} missing")
    return issues, warnings


def event_specific_checks(root: Path, args: argparse.Namespace, changed: list[str]) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    event = args.event
    if event == "SessionStart":
        warnings.append("SessionStart: read AGENTS.md, PROJECT_STATE.md, tasks.md, and active locks before editing")
    if event == "PreCompact":
        warnings.append("PreCompact: externalize session state and prepare handoff before compacting")
    if event == "PostCompact":
        warnings.append("PostCompact: increment compact_count and reread AGENTS.md plus project fact documents before continuing")
    if event == "SubagentStop" and not has_real_handoff(root):
        warnings.append("SubagentStop: record subagent result in THREAD_HANDOFFS.md before merge")
    agent_change = any(matches(p, ".codex/agents/**") for p in changed)
    if agent_change and "docs/ai-dev/orchestration/AGENT_ROLE_POLICY.md" not in changed:
        warnings.append(".codex/agents changed without AGENT_ROLE_POLICY.md in changed files; confirm role policy remains current")
    coordination_change = any(matches(p, "docs/ai-dev/orchestration/**") or matches(p, "docs/ai-dev/concurrency/**") for p in changed)
    if coordination_change and "scripts/thread_coordination_check.py" not in changed:
        warnings.append("coordination docs changed; consider whether thread_coordination_check.py also needs updates")
    return issues, warnings


def build_report(root: Path, args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    changed = changed_files(args, root)
    issues: list[str] = []
    warnings: list[str] = []
    core_issues, core_warnings = check_core_docs(root)
    stamp_issues, stamp_warnings, stamp_info = parse_stamp(root)
    config_issues, config_warnings, config_info = check_codex_config(root)
    agent_issues, agent_warnings, agents = check_agents(root)
    compact_issues, compact_warnings, compactions = check_compaction(root, args)
    lock_issues, lock_warnings, locks = check_locks(root)
    merge_issues, merge_warnings, queue = check_merge_queue(root)
    event_issues, event_warnings = event_specific_checks(root, args, changed)
    for bucket in [core_issues, stamp_issues, config_issues, agent_issues, compact_issues, lock_issues, merge_issues, event_issues]:
        issues.extend(bucket)
    for bucket in [core_warnings, stamp_warnings, config_warnings, agent_warnings, compact_warnings, lock_warnings, merge_warnings, event_warnings]:
        warnings.extend(bucket)
    exit_code = 0 if args.advisory or not issues else 1
    report = {
        "checked_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "event": args.event,
        "changed_files": changed,
        "task_types": args.task_type,
        "advisory": args.advisory,
        "policy": {"max_compactions": args.max_compactions, "hard_compactions": args.hard_compactions},
        "codex_config": config_info,
        "agents": agents,
        "stamp": stamp_info,
        "compactions": compactions,
        "locks_checked": len(locks),
        "merge_queue_items_checked": len(queue),
        "issues": issues,
        "warnings": warnings,
        "summary": {"issue_count": len(issues), "warning_count": len(warnings), "agent_count": len(agents), "max_compact_count": max([int(r["compact_count"]) for r in compactions], default=0)},
    }
    return report, exit_code


def render_text(report: dict[str, Any], exit_code: int) -> str:
    lines = ["Thread coordination check", f"Checked at: {report['checked_at']}", f"Event: {report['event']}", f"Exit code: {exit_code}", ""]
    if report.get("changed_files"):
        lines.append("Changed files:")
        lines.extend(f"- {item}" for item in report["changed_files"])
        lines.append("")
    lines.append("Summary:")
    for key, value in report.get("summary", {}).items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    if report.get("stamp"):
        lines.append("AGENTS metadata:")
        for key, value in report["stamp"].items():
            lines.append(f"- {key}: {value}")
        lines.append("")
    if report.get("codex_config"):
        lines.append("Codex config:")
        for key, value in report["codex_config"].items():
            lines.append(f"- {key}: {value}")
        lines.append("")
    if report.get("compactions"):
        lines.append("Compaction records:")
        for item in report["compactions"]:
            lines.append(f"- {item['file']} {item['source']}: compact_count={item['compact_count']}")
        lines.append("")
    if report.get("issues"):
        lines.append("Issues:")
        lines.extend(f"- {item}" for item in report["issues"])
        lines.append("")
    if report.get("warnings"):
        lines.append("Warnings:")
        lines.extend(f"- {item}" for item in report["warnings"])
        lines.append("")
    if not report.get("issues") and not report.get("warnings"):
        lines.append("No coordination issues detected.")
    if report.get("advisory") and report.get("issues"):
        lines.append("Advisory mode: issues were reported but exit code remains 0.")
    return "\n".join(lines)


def hook_json_payload(report: dict[str, Any], exit_code: int) -> dict[str, Any]:
    issues = report.get("issues") or []
    warnings = report.get("warnings") or []
    summary = report.get("summary") or {}
    prefix = f"ai-doc-driven-project: {summary.get('issue_count',0)} issue(s), {summary.get('warning_count',0)} warning(s)."
    detail = "; ".join((issues + warnings)[:3])
    payload: dict[str, Any] = {"continue": True, "suppressOutput": False}
    if detail:
        payload["systemMessage"] = prefix + " " + detail
    else:
        payload["systemMessage"] = prefix
    if report.get("event") == "SessionStart":
        payload["hookSpecificOutput"] = {"hookEventName": "SessionStart", "additionalContext": "Read AGENTS.md, docs/ai-dev/PROJECT_STATE.md, docs/ai-dev/tasks.md, and active locks before editing. Keep subagent outputs non-factual until the main session adopts them."}
    return payload


def write_record(root: Path, report: dict[str, Any], text: str) -> Path:
    run_dir = root / "docs/ai-dev/thread-check-runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = run_dir / f"TC-{stamp}.md"
    body = [f"# TC-{stamp}", "", f"- Checked at: {report['checked_at']}", f"- Event: {report['event']}", f"- Issues: {report['summary']['issue_count']}", f"- Warnings: {report['summary']['warning_count']}", f"- Max compact_count: {report['summary']['max_compact_count']}", "", "```text", text, "```", ""]
    path.write_text("\n".join(body), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check Codex thread coordination, role constraints, and compact_count policy.")
    parser.add_argument("--project-root", "--target", dest="project_root", default=".")
    parser.add_argument("--check", action="store_true", help="accepted for readability; check is the default")
    parser.add_argument("--event", default="manual", choices=["manual", "SessionStart", "PreCompact", "PostCompact", "SubagentStart", "SubagentStop", "Stop"])
    parser.add_argument("--changed", nargs="*", help="Explicit changed file list")
    parser.add_argument("--staged", action="store_true", help="Use git staged files")
    parser.add_argument("--since", help="Use git diff --name-only <REV>")
    parser.add_argument("--task-type", action="append", default=[], help="Task type hint, e.g. security, data_migration, architecture_change")
    parser.add_argument("--max-compactions", type=int, default=2, help="Migration threshold. Default: 2")
    parser.add_argument("--hard-compactions", type=int, default=3, help="Hard stop threshold. Default: 3")
    parser.add_argument("--require-handoff", action="store_true", help="Warn when no real HO-YYYYMMDD-NNN handoff exists")
    parser.add_argument("--record", action="store_true", help="Write docs/ai-dev/thread-check-runs/TC-*.md")
    parser.add_argument("--strict", action="store_true", help="Compatibility flag; strict is default unless --advisory is used")
    parser.add_argument("--advisory", action="store_true", help="Report issues but exit 0")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--hook-json", action="store_true", help="Emit Codex hook-compatible JSON on stdout. Required for Stop/SubagentStop hooks.")
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    if not root.exists():
        if args.hook_json:
            print(json.dumps({"continue": True, "systemMessage": f"project root does not exist: {root}", "suppressOutput": False}))
            return 0 if args.advisory else 2
        print(f"ERROR: project root does not exist: {root}", file=sys.stderr)
        return 2
    os.chdir(root)
    report, exit_code = build_report(root, args)
    text = json.dumps(report, ensure_ascii=False, indent=2) if args.json else render_text(report, exit_code)
    if args.record and not args.hook_json:
        record_path = write_record(root, report, text)
        if args.json:
            report["record_path"] = norm_path(record_path.relative_to(root))
            text = json.dumps(report, ensure_ascii=False, indent=2)
        else:
            text += f"\n\nRecord written: {norm_path(record_path.relative_to(root))}"
    if args.hook_json:
        print(json.dumps(hook_json_payload(report, exit_code), ensure_ascii=False))
    else:
        print(text)
    return 0 if args.advisory else exit_code


if __name__ == "__main__":
    raise SystemExit(main())
