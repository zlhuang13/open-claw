#!/usr/bin/env python3
"""Compatibility wrapper for the standalone UMI dashboard."""
from pathlib import Path
import runpy
import sys

NEW_DASHBOARD_DIR = Path(__file__).resolve().parents[3] / 'umi-dashboard' / 'scripts' / 'dashboard'

if str(NEW_DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(NEW_DASHBOARD_DIR))


def run():
    module = runpy.run_path(str(NEW_DASHBOARD_DIR / 'server.py'))
    module['run']()


if __name__ == '__main__':
    run()
