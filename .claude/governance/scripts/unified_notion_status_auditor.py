#!/usr/bin/env python3
"""Shim — SSOT: ``tools.notion.unified_notion_status_auditor``. Sets Cursor artifact vendor."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.environ.setdefault("NOTION_STATUS_VIOLATIONS_VENDOR", "cursor")

from tools.notion.unified_notion_status_auditor import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
