"""Auto-discover and load dashboard modules."""
import importlib.util
from pathlib import Path


def discover_modules(modules_dir):
    """Return list of module objects from .py files, skipping private files."""
    modules_dir = Path(modules_dir)
    mods = []
    for path in sorted(modules_dir.glob('*.py')):
        if path.name.startswith('_') or path.name == '__init__.py':
            continue
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mods.append(mod)
    return mods
