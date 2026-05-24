#!/usr/bin/env python3
"""Backward-compatible entrypoint — delegates to ``check_section_x2_x1d_drift.py``."""

from __future__ import annotations

import runpy
from pathlib import Path

if __name__ == "__main__":
    target = Path(__file__).resolve().parent / "check_section_x2_x1d_drift.py"
    runpy.run_path(str(target), run_name="__main__")
