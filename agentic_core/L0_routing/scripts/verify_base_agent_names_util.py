#!/usr/bin/env python3
"""Verify Base Agent names in dashboard data."""

import json
from pathlib import Path
from agentic_core.L0_routing.config import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
)

project_root = Path(__file__).parent.parent
data_file = project_root / AGENTIC_CORE_DIR / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"

content = data_file.read_text(encoding="utf-8")
lines = [l for l in content.split("\n") if not l.strip().startswith("//")]
content = "\n".join(lines).replace("window.dashboardData = ", "").strip().rstrip(";")
data = json.loads(content)

print("\nFirst 10 territories in dashboard data:")
print("=" * 60)
for i, row in enumerate(data[:10]):
    print(f"{i + 1}. {row['Territory']}")

print("\n" + "=" * 60)
print("Base Agent territories:")
print("=" * 60)
for row in data:
    if "Base Agent" in row["Territory"] or row["Territory"] == "Sovereign Base Agent":
        print(f"  ✅ {row['Territory']}")
