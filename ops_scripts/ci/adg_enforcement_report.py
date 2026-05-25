#!/usr/bin/env python3
"""CI shim — enforcement report SSOT lives in ``tools.adg.integration.enforcement_report``."""

from __future__ import annotations

__adg_consumer_mode__ = "inventory"

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.adg.integration.enforcement_report import (  # noqa: E402
    ARTIFACTS_ADG,
    build_enforcement_report,
    compute_certified_rollup,
    latest_enforcement_report,
    write_enforcement_report,
    _load_json,
)

__all__ = [
    "ARTIFACTS_ADG",
    "build_enforcement_report",
    "compute_certified_rollup",
    "latest_enforcement_report",
    "write_enforcement_report",
    "_load_json",
]
