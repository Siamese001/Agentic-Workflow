"""Remove extracted section runners from canonical_dispatch."""
from __future__ import annotations

import logging
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
src_path = REPO / "apps_rg/runtime/orchestration/canonical_dispatch.py"
src = src_path.read_text(encoding="utf-8")
m_start = src.index("def _run_competencies_lane_from_cli")
m_end = src.index("_BRIEF_FETCH_MAX_BYTES")
new_src = src[:m_start] + src[m_end:]
src_path.write_text(new_src, encoding="utf-8")
logging.info("C3 write receipt: tools/governance_legacy/_trim_canonical_dispatch.py write side effect recorded")
print("trimmed", m_end - m_start, "bytes")
