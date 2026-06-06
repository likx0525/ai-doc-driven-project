#!/usr/bin/env python3
"""Validate docs/architecture/MODULE_BOUNDARIES.yml and check simple dependency rules.

Exit codes:
  0: passed
  1: schema or dependency violation
  2: configuration/tooling error
  3: module boundaries are still a stub or human architecture confirmation is required
"""
from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

CONFIG_PATH = Path("docs/architecture/MODULE_BOUNDARIES.yml")
SOURCE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
IGNORE_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "env", "node_modules", "dist", "build", "coverage", ".next", ".nuxt", "target", "vendor", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


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
            print("ERROR: PyYAML is required only when MODULE_BOUNDARIES.yml is not JSON-compatible YAML.", file=sys.stderr)
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


def iter_source_files(root: Path) -> list[str]:
    out: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in IGNORE_DIRS for part in rel_parts):
            continue
        out.append(norm_path(path.relative_to(root)))
    return sorted(out)


def matches_glob(path: str, pattern: str) -> bool:
    path = norm_path(path)
    pattern = norm_path(pattern)
    if pattern.endswith("/**"):
        prefix = pattern[:-3].rstrip("/")
        return path == prefix or path.startswith(prefix + "/")
    if pattern.endswith("/"):
        prefix = pattern.rstrip("/")
        return path == prefix or path.startswith(prefix + "/")
    return fnmatch.fnmatch(path, pattern)


def validate_schema(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    modules = data.get("modules")
    if modules is None:
        issues.append("missing top-level 'modules' list")
        modules = []
    if not isinstance(modules, list):
        issues.append("top-level 'modules' must be a list")
        return issues
    names: set[str] = set()
    for idx, module in enumerate(modules):
        if not isinstance(module, dict):
            issues.append(f"modules[{idx}] must be a mapping")
            continue
        name = module.get("name")
        if not name or not isinstance(name, str):
            issues.append(f"modules[{idx}] missing string 'name'")
            continue
        if name in names:
            issues.append(f"duplicate module name: {name}")
        names.add(name)
        paths = module.get("paths")
        if not isinstance(paths, list) or not paths:
            issues.append(f"module {name}: 'paths' must be a non-empty list")
        for field in ["import_roots", "allowed_dependencies", "forbidden_dependencies", "owners"]:
            if field in module and not isinstance(module[field], list):
                issues.append(f"module {name}: '{field}' must be a list")
    rules = data.get("rules", {})
    if rules is not None and not isinstance(rules, dict):
        issues.append("top-level 'rules' must be a mapping")
    elif isinstance(rules, dict):
        for field in ["dependency_direction", "forbidden_dependencies", "shared_modules"]:
            if field in rules and not isinstance(rules[field], list):
                issues.append(f"rules.{field} must be a list")
        for idx, rule in enumerate(rules.get("forbidden_dependencies", []) or []):
            if not isinstance(rule, dict) or not rule.get("from") or not rule.get("to"):
                issues.append(f"rules.forbidden_dependencies[{idx}] must contain from/to")
    return issues


def module_for_path(path: str, modules: list[dict[str, Any]]) -> str | None:
    for module in modules:
        for pattern in module.get("paths", []) or []:
            if matches_glob(path, str(pattern)):
                return str(module.get("name"))
    return None


def import_root_to_module(modules: list[dict[str, Any]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for module in modules:
        name = str(module.get("name"))
        for root in module.get("import_roots") or []:
            mapping[str(root)] = name
        for pattern in module.get("paths", []) or []:
            pat = norm_path(str(pattern)).replace("/**", "")
            parts = [part for part in pat.split("/") if part and part not in {"src", "app", "lib", "packages", "services", "*", "**"}]
            if parts:
                mapping.setdefault(parts[0], name)
    return mapping


def imports_from_python(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return []
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


IMPORT_RE = re.compile(r"(?:import\s+(?:[^'\"]+\s+from\s+)?|export\s+[^'\"]+\s+from\s+|require\(|import\()\s*['\"]([^'\"]+)['\"]")


def imports_from_js_ts(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    return IMPORT_RE.findall(text)


def resolve_relative_import(source: Path, specifier: str, root: Path) -> str | None:
    if not specifier.startswith("."):
        return None
    base = (source.parent / specifier).resolve()
    try:
        return norm_path(base.relative_to(root.resolve()))
    except Exception:
        return None


def target_module_for_import(source_path: Path, specifier: str, root: Path, modules: list[dict[str, Any]], root_map: dict[str, str]) -> str | None:
    if specifier.startswith("."):
        rel = resolve_relative_import(source_path, specifier, root)
        return module_for_path(rel, modules) if rel else None
    first = specifier.split("/", 1)[0]
    if first.startswith("@") and "/" in specifier:
        first = "/".join(specifier.split("/", 2)[:2])
    return root_map.get(first) or root_map.get(specifier.split(".", 1)[0])


def source_imports(path: Path) -> list[str]:
    ext = path.suffix.lower()
    if ext == ".py":
        return imports_from_python(path)
    if ext in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
        return imports_from_js_ts(path)
    return []


def check_dependencies(root: Path, files: list[str], data: dict[str, Any]) -> tuple[list[str], list[str]]:
    modules = data.get("modules") or []
    rules = data.get("rules") or {}
    shared = set(str(x) for x in (rules.get("shared_modules") or []))
    root_map = import_root_to_module(modules)
    violations: list[str] = []
    warnings: list[str] = []
    module_by_name = {str(m.get("name")): m for m in modules if isinstance(m, dict) and m.get("name")}
    global_forbidden = {(str(r.get("from")), str(r.get("to"))): str(r.get("reason", "forbidden dependency")) for r in (rules.get("forbidden_dependencies") or []) if isinstance(r, dict)}
    for rel in files:
        path = root / rel
        if path.suffix.lower() not in SOURCE_EXTENSIONS or not path.exists():
            continue
        source_module = module_for_path(rel, modules)
        if not source_module:
            warnings.append(f"{rel}: source file does not match any module path")
            continue
        current_module = module_by_name.get(source_module, {})
        allowed = set(str(x) for x in (current_module.get("allowed_dependencies") or []))
        forbidden = set(str(x) for x in (current_module.get("forbidden_dependencies") or []))
        for specifier in source_imports(path):
            target_module = target_module_for_import(path, specifier, root, modules, root_map)
            if not target_module or target_module == source_module or target_module in shared:
                continue
            if target_module in forbidden:
                violations.append(f"{rel}: {source_module} imports {target_module} via {specifier!r}, but it is forbidden")
            if (source_module, target_module) in global_forbidden:
                violations.append(f"{rel}: {source_module} imports {target_module} via {specifier!r}: {global_forbidden[(source_module, target_module)]}")
            if data.get("checks", {}).get("enforce_allowed_dependencies", True) and allowed and target_module not in allowed:
                violations.append(f"{rel}: {source_module} imports {target_module} via {specifier!r}, but allowed_dependencies={sorted(allowed)}")
    return violations, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate module boundary schema and simple import dependency rules.")
    parser.add_argument("--project-root", default=".", help="Project root. Default: current directory.")
    parser.add_argument("--changed", nargs="*", help="Explicit changed file list.")
    parser.add_argument("--staged", action="store_true", help="Use git staged files.")
    parser.add_argument("--since", help="Use git diff --name-only <REV>.")
    parser.add_argument("--all", action="store_true", help="Scan all tracked source files when git is available; falls back to source files outside ignored dirs.")
    parser.add_argument("--advisory", action="store_true", help="Do not fail for stub/unknown module warnings.")
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    os.chdir(root)
    data = load_yaml(root / CONFIG_PATH)
    schema_issues = validate_schema(data)
    if schema_issues:
        print("Architecture boundary schema issues:")
        for issue in schema_issues:
            print(f"- {issue}")
        return 1
    modules = data.get("modules") or []
    if args.all:
        files = [norm_path(item) for item in git_lines(["ls-files"], root)] or iter_source_files(root)
    else:
        files = changed_files(args, root)
    source_files = [item for item in files if (root / item).suffix.lower() in SOURCE_EXTENSIONS]
    if not modules:
        print("Architecture boundary schema is valid, but modules is empty: MODULE_BOUNDARIES.yml is still a stub.")
        if source_files and not args.advisory:
            print("Source files changed but no module boundaries are defined. Fill MODULE_BOUNDARIES.yml or rerun with --advisory and document why it is safe.")
            return 3
        return 0
    violations, warnings = check_dependencies(root, source_files, data)
    unknown_policy = str((data.get("checks") or {}).get("unknown_source_files", "warn")).lower()
    if warnings:
        print("Architecture warnings:")
        for warning in warnings:
            print(f"- {warning}")
        if unknown_policy == "error":
            violations.extend(warnings)
    if violations:
        print("Architecture boundary violations:")
        for violation in violations:
            print(f"- {violation}")
        return 1
    print("Architecture check passed.")
    if source_files:
        print("Checked source files:")
        for item in source_files:
            print(f"- {item}")
    else:
        print("No source files detected for dependency scanning.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
