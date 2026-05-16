"""Competencies lane X2 / FEC parity diagnostics for E2E proof (apps_rg-local).

Used by ``ops_scripts/ci/prove_apps_rg_e2e_runtime.py`` — does not import agentic_core.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping


_FV_RE = re.compile(r"\b(fv_c0_smoke:[^\s|]+|fv_[a-z0-9_:]+|bul_[a-z0-9_]+)\b", re.I)


def scrape_fact_id_tokens_from_compiled_prompt(compiled_prompt_path: Path) -> list[str]:
    """Return ordered-unique chroma/FEC-like fact-vector tokens skimmed from ``compiled_prompt.txt``."""
    if not compiled_prompt_path.is_file():
        return []
    text = compiled_prompt_path.read_text(encoding="utf-8", errors="replace")
    seen: dict[str, None] = {}
    for m in _FV_RE.finditer(text):
        tok = m.group(0).strip()
        if tok and tok not in seen:
            seen[tok] = None
    return list(seen.keys())


def _competencies_section_from_final(blob: Mapping[str, Any]) -> Mapping[str, Any] | None:
    for sec in blob.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        if str(sec.get("section_id") or "").strip().lower() == "competencies":
            snap = sec.get("l2_output_snapshot")
            return snap if isinstance(snap, dict) else None
    return None


def build_competencies_x2_diagnostics(
    *,
    l2_output: Mapping[str, Any] | None,
    final_resume_blob: Mapping[str, Any] | None,
    x2_failed_checks: list[str],
    fec_evidence_refs_available: list[str],
    compiled_prompt_fact_refs_available: list[str],
    fix_applied: str = "",
    decisive_reason: str = "",
) -> dict[str, Any]:
    """Summarize competencies JSON parity lane vs assembled final_resume snapshot."""
    snap = (
        _competencies_section_from_final(final_resume_blob)
        if isinstance(final_resume_blob, dict)
        else None
    )
    parity = False
    if isinstance(l2_output, Mapping) and isinstance(snap, Mapping):
        parity = snap == dict(l2_output)

    return {
        "competencies_json_parity_final_vs_lane_l2": parity,
        "fec_evidence_refs_available": list(fec_evidence_refs_available),
        "compiled_prompt_fact_refs_available": list(compiled_prompt_fact_refs_available),
        "x2_failed_checks": list(x2_failed_checks),
        "fix_applied": fix_applied,
        "decisive_reason": decisive_reason,
    }


__all__ = [
    "build_competencies_x2_diagnostics",
    "scrape_fact_id_tokens_from_compiled_prompt",
]
