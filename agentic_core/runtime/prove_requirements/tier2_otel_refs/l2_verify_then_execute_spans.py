"""OTEL span reference module — REQ-L2-VERIFY-THEN-EXECUTE-001.

Static metadata. Declares stable span names emitted by the L2
local-critique / verify-then-execute verdict surface. This module does
not emit spans, does not import an OTEL exporter, and does not mutate
runtime state.
"""

from __future__ import annotations

from typing import Final, Tuple

STEP1_REQ_ID: Final[str] = "REQ-L2-VERIFY-THEN-EXECUTE-001"
EXPECTED_FAIL_REASON: Final[str] = "VERIFY_THEN_EXECUTE_REQUIRED"

SPAN_NAMES: Final[Tuple[str, ...]] = (
    "l2.verify_then_execute.local_critique.start",
    "l2.verify_then_execute.local_critique.verdict",
    "l2.verify_then_execute.execute.gated",
    "l2.verify_then_execute.execute.blocked",
)
