# Root-level conftest.py — loaded by pytest BEFORE any test collection
# This ensures the repo root is on sys.path so tools.adg, apps_*, etc. are importable
import sys
from pathlib import Path

_REPO_ROOT = str(Path(__file__).resolve().parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
