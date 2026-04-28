"""OTEL span reference module — REQ-PA-PROVIDER-AWARE-RENDER-001.

Static metadata. Declares stable span names emitted by the PA
provider-aware rendering surface (template id and provider id are
expected attributes on these spans). This module does not emit spans,
does not import an OTEL exporter, and does not mutate runtime state.
"""

from __future__ import annotations

from typing import Final, Tuple

STEP1_REQ_ID: Final[str] = "REQ-PA-PROVIDER-AWARE-RENDER-001"
EXPECTED_FAIL_REASON: Final[str] = "PROVIDER_TEMPLATE_NOT_DECLARED"

SPAN_NAMES: Final[Tuple[str, ...]] = (
    "pa.provider_aware_render.template_resolved",
    "pa.provider_aware_render.render.start",
    "pa.provider_aware_render.render.complete",
    "pa.provider_aware_render.render.blocked",
)
