#!/usr/bin/env python3
"""Remove local caches and generated run records before validation."""
from __future__ import annotations
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR_NAMES = {'.pytest_cache', '__pycache__', '.mypy_cache', '.ruff_cache'}
FILE_PATTERNS = ['*.pyc', '*.pyo', 'TC-*.md', 'DUR-*.md', 'AC-*.md']

removed = []
for p in sorted(ROOT.rglob('*'), key=lambda x: len(x.parts), reverse=True):
    if p.is_dir() and p.name in DIR_NAMES:
        shutil.rmtree(p, ignore_errors=True)
        removed.append(p.relative_to(ROOT).as_posix())
for pat in FILE_PATTERNS:
    for p in ROOT.rglob(pat):
        if p.is_file():
            try:
                p.unlink()
                removed.append(p.relative_to(ROOT).as_posix())
            except FileNotFoundError:
                pass
print(f'Removed {len(removed)} local artifact(s).')
