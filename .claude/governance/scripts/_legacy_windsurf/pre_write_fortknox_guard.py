#!/usr/bin/env python3
"""Fort Knox pre-write guard — Constitutional §32 (Windsurf mirror of .claude/governance/scripts)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_CURSOR_GUARD = Path(__file__).resolve().parents[2] / ".claude" / "governance/scripts" / "pre_write_fortknox_guard.py"
_spec = importlib.util.spec_from_file_location("cursor_pre_write_fortknox_guard", _CURSOR_GUARD)
_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_mod)
sys.exit(_mod.main())
