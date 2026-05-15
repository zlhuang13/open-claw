"""Shared path helpers for the standalone UMI dashboard."""
from pathlib import Path

DASHBOARD_DIR = Path(__file__).resolve().parent
SKILL_DIR = DASHBOARD_DIR.parent.parent
WORKSPACE_DIR = SKILL_DIR.parent.parent
GARDEN_TRACKER_DIR = WORKSPACE_DIR / 'skills' / 'garden-tracker'
DATA_DIR = GARDEN_TRACKER_DIR / 'data'
PHOTOS_DIR = GARDEN_TRACKER_DIR / 'photos'
CAT_PHOTOS_DIR = DATA_DIR / 'cat_photos'

BIND = '100.86.143.43'
PORT = 80
