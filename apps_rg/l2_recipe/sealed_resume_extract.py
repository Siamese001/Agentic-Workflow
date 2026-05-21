"""Extract structured resume dict from L2 sealed artifacts (apps_rg)."""
from __future__ import annotations

import json
from typing import Any


def generated_resume_from_sealed_l2(sealed: Any) -> dict[str, Any] | None:
    """Return ``generated_resume`` payload from a sealed L2 result, if present."""
    if sealed is None:
        return None
    diff = getattr(sealed, "proposed_state_diff", None)
    if isinstance(diff, dict):
        gr = diff.get("generated_resume")
        if isinstance(gr, dict):
            return gr
        # Non-JSON path: envelope stores prose under top-level ``raw_text`` only.
        if set(diff.keys()) == {"raw_text"}:
            rt = diff.get("raw_text")
            return {"raw_text": rt} if rt is not None else {"raw_text": ""}
    gc = getattr(sealed, "generated_content", None)
    if isinstance(gc, str) and gc.strip():
        try:
            obj = json.loads(gc)
        except json.JSONDecodeError:  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
            return None
        if isinstance(obj, dict):
            return obj
    return None


__all__ = ["generated_resume_from_sealed_l2"]
