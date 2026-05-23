"""One-off: extract section CLI runners from canonical_dispatch."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
src_path = REPO / "apps_rg/runtime/orchestration/canonical_dispatch.py"
src = src_path.read_text(encoding="utf-8")
m_start = src.index("def _run_competencies_lane_from_cli")
m_end = src.index("_BRIEF_FETCH_MAX_BYTES")
chunk = src[m_start:m_end]
chunk = re.sub(r"def _run_(\w+)_lane_from_cli", r"def run_section_\1_spine", chunk)
header = '''"""Section spine CLI runners — invoked only via apps_rg_spine_run (d8f4a2)."""
from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from apps_rg.runtime.orchestration.canonical_dispatch import (
    build_raw_request_for_r4,
    _effective_lane_provider,
    _read_optional_brief,
    _resolve_lane_manual_brief,
)

'''
out = REPO / "apps_rg/runtime/spine/section_cli_runners.py"
out.write_text(header + chunk, encoding="utf-8")
print(f"wrote {out} ({len(header + chunk)} bytes)")
