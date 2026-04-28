"""OTEL span reference module — REQ-L0-NO-RETRIEVAL-001.

Static metadata. Declares stable span names emitted at the L0 intake
boundary when a retrieval attempt is detected and rejected. This
module does not emit spans, does not import an OTEL exporter, and
does not mutate runtime state.
"""

from __future__ import annotations

from typing import Final, Tuple

STEP1_REQ_ID: Final[str] = "REQ-L0-NO-RETRIEVAL-001"
EXPECTED_FAIL_REASON: Final[str] = "L0_RETRIEVAL_BLOCKED"

SPAN_NAMES: Final[Tuple[str, ...]] = (
    "l0.intake.retrieval_attempt.detected",
    "l0.intake.retrieval_attempt.rejected",
    "l0.boundary.no_retrieval.attestation",
)
