"""Shared helper to load dev_tools scripts by file path.

dev_tools/ has no __init__.py (not a runtime package), so tests must load
modules via importlib.util.spec_from_file_location.

Usage in tests::

    from tests.helpers.dev_tools_loader import load_dev_script

    mod = load_dev_script("add_agent_suffix_plan_util.py")
    assert mod is not None
"""

import importlib.util
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[2]
OPS_SCRIPTS_DIR = "ops_scripts"
DEV_SCRIPTS_DIR = REPO_ROOT / OPS_SCRIPTS_DIR / "dev_tools" / "l0_scripts"


def load_dev_script(filename: str) -> ModuleType:
    """Load a ops_scripts/dev_tools/l0_scripts/<filename> module by file path.

    Args:
        filename: Script filename (e.g. ``"my_util.py"``).

    Returns:
        The loaded module object.

    Raises:
        FileNotFoundError: If the script does not exist.
        ImportError: If the module fails to load.
    """
    script_path = DEV_SCRIPTS_DIR / filename
    if not script_path.exists():
        raise FileNotFoundError(f"ops_scripts/dev_tools/l0_scripts/{filename} not found")

    stem = script_path.stem
    spec = importlib.util.spec_from_file_location(stem, str(script_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot create spec for {script_path}")

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
