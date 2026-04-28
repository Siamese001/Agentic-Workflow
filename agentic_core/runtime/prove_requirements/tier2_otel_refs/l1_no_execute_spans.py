"""OTEL span reference module — REQ-L1-NO-EXECUTE-001.

Static metadata. Declares stable span names emitted at the L1
cognition boundary when a tool/model execution attempt is detected
and rejected. This module does not emit spans, does not import an
OTEL exporter, and does not mutate runtime state.
"""

from __future__ import annotations

from typing import Final, Tuple

STEP1_REQ_ID: Final[str] = "REQ-L1-NO-EXECUTE-001"
EXPECTED_FAIL_REASON: Final[str] = "L1_EXECUTION_BLOCKED"

SPAN_NAMES: Final[Tuple[str, ...]] = (
    "l1.cognition.execution_attempt.detected",
    "l1.cognition.execution_attempt.rejected",
    "l1.boundary.no_execute.attestation",
)
