"""OTEL span reference module — REQ-L3-L2-STEP-HANDOFF-001.

Static metadata. Declares stable span names emitted at the L3->L2 step
checkpoint boundary (handoff issued, checkpoint persisted, resume
attempt, resume blocked). This module does not emit spans, does not
import an OTEL exporter, and does not mutate runtime state.
"""

from __future__ import annotations

from typing import Final, Tuple

STEP1_REQ_ID: Final[str] = "REQ-L3-L2-STEP-HANDOFF-001"
EXPECTED_FAIL_REASON: Final[str] = "L3_L2_HANDOFF_CHECKPOINT_MISSING"

SPAN_NAMES: Final[Tuple[str, ...]] = (
    "l3.l2_step_handoff.issued",
    "l3.l2_step_handoff.checkpoint.persisted",
    "l3.l2_step_handoff.resume.attempted",
    "l3.l2_step_handoff.resume.blocked",
)
