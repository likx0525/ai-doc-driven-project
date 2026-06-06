#!/usr/bin/env python3
"""Build a clean package archive for this skill package."""
from __future__ import annotations
import argparse, shutil, zipfile
from pathlib import Path

EXCLUDE_PARTS = {'.pytest_cache', '__pycache__', '.mypy_cache', '.ruff_cache', '.ai-secrets', '.git'}
EXCLUDE_PREFIXES = ['docs/ai-dev/thread-check-runs/TC-', 'docs/ai-dev/doc-update-runs/DUR-', 'docs/ai-dev/git/auto-commit-runs/AC-']
EXCLUDE_SUFFIXES = ['.pyc', '.pyo', '.DS_Store']


def include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    if any(part in EXCLUDE_PARTS for part in path.relative_to(root).parts):
        return False
    if any(rel.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
        return False
    if any(rel.endswith(suffix) for suffix in EXCLUDE_SUFFIXES):
        return False
    return True


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', required=True)
    ap.add_argument('--top-name')
    args=ap.parse_args()
    root=Path(args.root).resolve()
    top=args.top_name or root.name
    out=Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(root.rglob('*')):
            if p.is_file() and include(p, root):
                zf.write(p, f'{top}/{p.relative_to(root).as_posix()}')
    print(out)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
