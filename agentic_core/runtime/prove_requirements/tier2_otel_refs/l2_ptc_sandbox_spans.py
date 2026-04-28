"""OTEL span reference module — REQ-L2-PTC-SANDBOX-001.

Static metadata. Declares stable span names emitted at PTC sandbox
boundaries (entry / exit / verdict). This module does not emit spans,
does not import an OTEL exporter, and does not mutate runtime state.
"""

from __future__ import annotations

from typing import Final, Tuple

STEP1_REQ_ID: Final[str] = "REQ-L2-PTC-SANDBOX-001"
EXPECTED_FAIL_REASON: Final[str] = "PTC_SANDBOX_REQUIRED"

SPAN_NAMES: Final[Tuple[str, ...]] = (
    "l2.ptc_sandbox.entry",
    "l2.ptc_sandbox.profile_resolved",
    "l2.ptc_sandbox.exit",
    "l2.ptc_sandbox.verdict",
)
