"""Extract JSON embedded in ``raw_text`` wrappers (honest repair, apps_rg-only)."""

from __future__ import annotations

import json
import re
from typing import Any

from apps_rg.l2_recipe.resume_output_shape import REAL_RESUME, classify_resume_payload
from apps_rg.l2_recipe.rg_output_minimal_validate import minimal_rg_output_valid

_REPAIR_TYPE = "RAW_TEXT_JSON_UNWRAP"


def _extract_first_balanced_object(s: str) -> str | None:
    """Return slice of first top-level `{`…`}` balanced object, or None."""
    s_stripped = s.strip()
    i = s_stripped.find("{")
    if i < 0:
        return None
    depth = 0
    in_str = False
    esc = False
    quote = ""
    for j in range(i, len(s_stripped)):
        c = s_stripped[j]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == quote:
                in_str = False
            continue
        if c in "\"'":
            in_str = True
            quote = c
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s_stripped[i : j + 1]
    return None


def _strip_markdown_fencelike_prefix(s: str) -> str:
    """Remove common ```json / ``` wrappers (best-effort, no content mutation)."""
    t = s.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*```\s*$", "", t)
    return t.strip()


def try_unwrap_raw_text_to_resume(raw_text: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """If *raw_text* contains a single parseable JSON object that passes minimal + shape gates.

    Returns (inner_dict, receipt). On failure (including prose-only), (None, {…}).
    """
    receipt: dict[str, Any] = {
        "repair_applied": False,
        "repair_type": _REPAIR_TYPE,
        "original_shape": "RAW_TEXT_WRAPPER",
        "validation_status": "FAIL",
    }
    if not isinstance(raw_text, str) or not raw_text.strip():
        return None, receipt

    candidate = _strip_markdown_fencelike_prefix(raw_text)
    slice_ = _extract_first_balanced_object(candidate)
    if slice_ is None:
        return None, receipt

    try:
        inner = json.loads(slice_)
    except json.JSONDecodeError:
        return None, receipt

    if not isinstance(inner, dict):
        return None, receipt

    ok_min, reason = minimal_rg_output_valid(inner)
    if not ok_min:
        receipt["minimal_schema_reason"] = reason
        return None, receipt

    shape = classify_resume_payload(inner)
    if shape.generation_status != REAL_RESUME:
        receipt["shape_reason"] = shape.generation_status
        return None, receipt

    receipt["repair_applied"] = True
    receipt["validation_status"] = "PASS"
    return inner, receipt


__all__ = ["try_unwrap_raw_text_to_resume"]
