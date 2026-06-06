#!/usr/bin/env python3
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / 'apply_ai_doc_driven_project.py'
sys.path.insert(0, str(HERE))
runpy.run_path(str(SCRIPT), run_name='__main__')
