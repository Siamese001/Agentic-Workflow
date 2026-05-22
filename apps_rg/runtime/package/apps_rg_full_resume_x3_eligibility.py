"""W3 — apps_rg L2 résumé product truth for package / X3 full-success eligibility (app-local)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from apps_rg.l2_recipe.resume_output_shape import (
    BLOCKED_PROVIDER_LANE,
    BLOCKED_STUB_PROVIDER,
    FAILED_ARTIFACT_GATE,
    FAILED_PROVIDER,
    REAL_RESUME,
    STUB_RECEIPT,
)
from apps_rg.runtime.product_output_policy import docx_output_required

_BLOCKED_FULL_SUCCESS: frozenset[str] = frozenset(
    {
        STUB_RECEIPT,
        FAILED_PROVIDER,
        BLOCKED_STUB_PROVIDER,
        BLOCKED_PROVIDER_LANE,
        FAILED_ARTIFACT_GATE,
    }
)


def evaluate_apps_rg_full_success_eligibility(
    *,
    manifest: Mapping[str, Any],
    run_root: Path,
) -> tuple[bool, list[str]]:
    """Return (eligible, reasons). *run_root* is the artifact directory containing the manifest file.

    Ineligible when W1/W2 product constraints are not satisfied for REAL_RESUME full success.
    """
    reasons: list[str] = []
    gs = manifest.get("apps_rg_generation_status")
    rs = manifest.get("resume_shape")
    fr = manifest.get("full_resume_generated")

    if gs is None or (isinstance(gs, str) and not str(gs).strip()):
        reasons.append("missing_generation_status")
    elif gs in _BLOCKED_FULL_SUCCESS:
        reasons.append(f"blocked_generation_status:{gs}")
    elif gs != REAL_RESUME:
        reasons.append(f"generation_status_not_real_resume:{gs!r}")

    if rs is None or (isinstance(rs, str) and not str(rs).strip()):
        reasons.append("missing_resume_shape")
    elif rs != REAL_RESUME:
        reasons.append(f"resume_shape_not_real_resume:{rs!r}")

    if fr is not True:
        reasons.append("full_resume_generated_not_true")

    require_docx = docx_output_required() or manifest.get("docx_output_required") is True
    if require_docx:
        dv = manifest.get("docx_verified")
        if dv is not True:
            reasons.append(f"docx_verified_not_true:{dv!r}")

    json_rel = str(manifest.get("generated_resume_json_relpath") or "outputs/generated_resume.json")
    jp = (run_root / json_rel).resolve()

    if not jp.is_file():
        reasons.append(f"missing_generated_resume_json:{json_rel}")
    else:
        try:
            raw = jp.read_text(encoding="utf-8").strip()
            if not raw:
                reasons.append("empty_generated_resume_json")
            else:
                obj = json.loads(raw)
                if not isinstance(obj, dict) or len(obj) == 0:
                    reasons.append("generated_resume_json_not_nonempty_object")
        except (OSError, json.JSONDecodeError) as exc:
            reasons.append(f"generated_resume_json_invalid:{exc}")

    if require_docx:
        docx_rel = str(manifest.get("resume_docx_relpath") or "outputs/resume.docx")
        dp = (run_root / docx_rel).resolve()
        if not dp.is_file() or dp.stat().st_size <= 0:
            reasons.append(f"missing_or_empty_resume_docx:{docx_rel}")

    ra = manifest.get("required_artifacts")
    if isinstance(ra, dict) and ra:
        for key, val in ra.items():
            if key == "docx_verified":
                if require_docx and val is not True:
                    reasons.append(f"required_artifacts_docx_verified_false:{val!r}")
            elif val != "verified":
                reasons.append(f"required_artifact_not_verified:{key}={val!r}")

    return (len(reasons) == 0, reasons)


__all__ = [
    "evaluate_apps_rg_full_success_eligibility",
]
