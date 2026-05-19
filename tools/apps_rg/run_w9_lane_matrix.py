#!/usr/bin/env python3
"""Run Wave 9 product-visible section lanes (same surface as W8)."""
from __future__ import annotations

import runpy
from pathlib import Path

if __name__ == "__main__":
    script = Path(__file__).resolve().parent / "run_w8_lane_matrix.py"
    runpy.run_path(str(script), run_name="__main__")
