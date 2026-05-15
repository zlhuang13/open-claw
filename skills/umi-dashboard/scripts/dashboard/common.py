"""Shared path helpers for the standalone UMI dashboard."""
from pathlib import Path
import shutil

UMI_DASHBOARD_DIR = Path(__file__).resolve().parent
UMI_SKILL_DIR = UMI_DASHBOARD_DIR.parent.parent
WORKSPACE_DIR = UMI_SKILL_DIR.parent.parent
GARDEN_TRACKER_DIR = WORKSPACE_DIR / 'skills' / 'garden-tracker'

UMI_DATA_DIR = UMI_SKILL_DIR / 'data'
GARDEN_DATA_DIR = GARDEN_TRACKER_DIR / 'data'
GARDEN_PHOTOS_DIR = GARDEN_TRACKER_DIR / 'photos'
CAT_PHOTOS_DIR = UMI_DATA_DIR / 'cat_photos'

BIND = '100.86.143.43'
PORT = 80


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def migrate_file(filename: str) -> Path:
    ensure_dir(UMI_DATA_DIR)
    new_path = UMI_DATA_DIR / filename
    old_path = GARDEN_DATA_DIR / filename
    if not new_path.exists() and old_path.exists():
        shutil.move(str(old_path), str(new_path))
    return new_path if new_path.exists() else old_path


def migrate_dir(dirname: str) -> Path:
    ensure_dir(UMI_DATA_DIR)
    new_path = UMI_DATA_DIR / dirname
    old_path = GARDEN_DATA_DIR / dirname
    if not new_path.exists() and old_path.exists():
        shutil.move(str(old_path), str(new_path))
    return new_path if new_path.exists() else old_path


def garden_file(filename: str) -> Path:
    return GARDEN_DATA_DIR / filename


INVENTORY_DB_PATH = migrate_file('inventory.db')
BIN_CACHE_PATH = migrate_file('bin_cache.txt')
CATS_DIARY_DB_PATH = migrate_file('cats_diary.db')
CATS_PROFILES_DB_PATH = migrate_file('cats_profiles.db')
CAT_PHOTOS_DIR = migrate_dir('cat_photos')

GARDEN_DB_PATH = garden_file('garden.db')
GARDEN_INFO_PATH = garden_file('garden_info.json')
DISMISSED_TODOS_PATH = garden_file('dismissed_todos.json')
