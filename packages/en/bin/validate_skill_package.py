#!/usr/bin/env python3
"""Validate an ai-doc-driven-project skill package."""
from __future__ import annotations
import argparse, ast, json, re, sys, tomllib
from pathlib import Path

FORBIDDEN_PARTS = {'.pytest_cache', '__pycache__', '.mypy_cache', '.ruff_cache', '.ai-secrets'}
RUNTIME_PATTERNS = [re.compile(r'TC-\d{8}-\d{6}\.md$'), re.compile(r'DUR-\d{8}-\d{6}\.md$'), re.compile(r'AC-\d{8}-\d{6}\.md$')]
CRITICAL_FILES = [
    'templates/AGENTS.md',
    'templates/ai-dev/DOC_UPDATE_TRIGGERS.md',
    'templates/ai-dev/DOC_UPDATE_TRIGGERS.yml',
    'templates/ai-dev/DOCS_INDEX.md',
    'templates/ai-dev/orchestration/AGENT_ROLE_POLICY.md',
    'templates/ai-dev/orchestration/CONTEXT_COMPACTION_POLICY.md',
    'templates/scripts/ai_doc_impact_check.py',
    'templates/scripts/thread_coordination_check.py',
    'templates/scripts/project_auto_commit.py',
    'templates/scripts/architecture_check.py',
    'templates/codex-config/hooks.json',
    'templates/codex-config/config.toml',
    'templates/ai-dev/git/AUTO_COMMIT_POLICY.md',
    'templates/ai-dev/git/AUTO_COMMIT_CONFIG.json',
]


def error(msg: str, issues: list[str]):
    issues.append(msg)


def validate(root: Path, english: bool = False) -> list[str]:
    issues: list[str] = []
    manifest_path = root/'templates/manifest.yml'
    if not manifest_path.exists():
        return ['missing templates/manifest.yml']
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for rel in CRITICAL_FILES:
        if not (root/rel).exists():
            error(f'missing critical file: {rel}', issues)
    # Runtime artifact pollution
    for p in root.rglob('*'):
        if any(part in FORBIDDEN_PARTS for part in p.parts):
            error(f'forbidden generated artifact: {p.relative_to(root)}', issues)
        if any(rx.search(p.name) for rx in RUNTIME_PATTERNS):
            error(f'runtime run record must not be packaged: {p.relative_to(root)}', issues)
    # Manifest sources exist
    for item in manifest.get('copy_trees', []):
        if not (root/item['source']).exists():
            error(f"manifest source missing: {item['source']}", issues)
    # Python parse
    for rel in ['templates/scripts/ai_doc_impact_check.py','templates/scripts/thread_coordination_check.py',
    'templates/scripts/project_auto_commit.py','templates/scripts/architecture_check.py','templates/scripts/project_auto_commit.py','bin/apply_ai_doc_driven_project.py','bin/apply_skill.py','bin/validate_skill_package.py','bin/build_release.py']:
        p=root/rel
        if p.exists():
            ast.parse(p.read_text(encoding='utf-8'))
    # TOML and JSON parse
    json.loads((root/'templates/codex-config/hooks.json').read_text(encoding='utf-8'))
    tomllib.loads((root/'templates/codex-config/config.toml').read_text(encoding='utf-8'))
    auto_commit_config=json.loads((root/'templates/ai-dev/git/AUTO_COMMIT_CONFIG.json').read_text(encoding='utf-8'))
    if auto_commit_config.get('allow_auto_push') is not False:
        error('AUTO_COMMIT_CONFIG.json must keep allow_auto_push=false by default', issues)
    if auto_commit_config.get('enabled') is not False:
        error('AUTO_COMMIT_CONFIG.json must be disabled by default', issues)
    agent_names=set()
    for p in (root/'templates/codex-agents').glob('*.toml'):
        data=tomllib.loads(p.read_text(encoding='utf-8'))
        for field in ['name','description','developer_instructions']:
            if not isinstance(data.get(field), str) or not data[field].strip():
                error(f'{p.relative_to(root)} missing {field}', issues)
        agent_names.add(data.get('name'))
    for required in ['main-session-coordinator','thread-manager','merge-coordinator']:
        if required not in agent_names:
            error(f'missing agent {required}', issues)
    # Hooks must not default-record Stop/SubagentStop.
    hooks_text=(root/'templates/codex-config/hooks.json').read_text(encoding='utf-8')
    if '--event Stop --record' in hooks_text or '--event SubagentStop --record' in hooks_text:
        error('Stop/SubagentStop hooks must not use --record by default', issues)
    if '--hook-json' not in hooks_text:
        error('hooks.json must use --hook-json', issues)
    # English package must have no Chinese characters.
    if english:
        rx = re.compile(r'[\u4e00-\u9fff]')
        for p in root.rglob('*'):
            if p.is_file() and p.suffix.lower() in {'.md','.txt','.toml','.json','.yml','.yaml','.py'}:
                if rx.search(p.read_text(encoding='utf-8', errors='ignore')):
                    error(f'English package contains Chinese characters: {p.relative_to(root)}', issues)
    return issues


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--english', action='store_true')
    args=ap.parse_args()
    issues=validate(Path(args.root).resolve(), args.english)
    if issues:
        print('Skill package validation failed:')
        for i in issues:
            print('-', i)
        return 1
    print('Skill package validation passed.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
