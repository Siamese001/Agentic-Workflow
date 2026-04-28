"""OTEL span reference module — REQ-PA-AIRLOCK-SECURITY-001.

Static metadata. Declares stable span names emitted by the PA airlock
security surface (verdict, score, and blocked branches). This module
does not emit spans, does not import an OTEL exporter, and does not
mutate runtime state.
"""

from __future__ import annotations

from typing import Final, Tuple

STEP1_REQ_ID: Final[str] = "REQ-PA-AIRLOCK-SECURITY-001"
EXPECTED_FAIL_REASON: Final[str] = "PA_AIRLOCK_SECURITY_BLOCKED"

SPAN_NAMES: Final[Tuple[str, ...]] = (
    "pa.airlock.evaluate.start",
    "pa.airlock.evaluate.score",
    "pa.airlock.evaluate.verdict",
    "pa.airlock.evaluate.blocked",
)
