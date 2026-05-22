"""Load pa_core_law_v1 contract blocks for reference-by-name in section PA templates."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_CONTRACT_PATH = Path(__file__).resolve().parent / "pa_core_law_v1.yaml"
KNOWN_CONTRACT_IDS = frozenset(
    {
        "pa_truth_oath_v1",
        "pa_proof_binding_v1",
        "pa_targeting_only_v1",
        "pa_untrusted_data_fence_v1",
    }
)


@lru_cache(maxsize=1)
def load_pa_core_law_document() -> dict[str, Any]:
    raw = yaml.safe_load(_CONTRACT_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"invalid pa_core_law document: {_CONTRACT_PATH}")
    return raw


def load_pa_core_law_contract(contract_id: str) -> str:
    if contract_id not in KNOWN_CONTRACT_IDS:
        raise KeyError(f"unknown pa_core_law contract_id: {contract_id!r}")
    doc = load_pa_core_law_document()
    contracts = doc.get("contracts") or {}
    body = contracts.get(contract_id)
    if not isinstance(body, str) or not body.strip():
        raise KeyError(f"missing or empty contract body: {contract_id!r}")
    return body.strip()


def s0_truth_oath_reference_line() -> str:
    """One-line S0 bound satisfying PromptAssemblyInput validator + core-law reference."""
    return (
        "NO FABRICATION: governed by pa_truth_oath_v1 (apps_rg/prompt_assembly/pa_core_law_v1.yaml). "
        "Section proof bound: C0 selected facts and ALLOWED_SOURCE_FACT_IDS only."
    )


def d0_untrusted_fence_reference_line() -> str:
    """D0 pointer for section templates and w7 shell."""
    return "Implements pa_untrusted_data_fence_v1 (pa_core_law_v1.yaml)."


def core_law_marker_for_section(section_family: str) -> str:
    """Stable template marker comment id per rollout family."""
    markers = {
        "executive_summary": "EXEC_SUMMARY_PROMPT_CORE_LAW_V3",
        "headline": "HEADLINE_PROMPT_CORE_LAW_V3",
        "competencies": "COMPETENCIES_PROMPT_CORE_LAW_V3",
        "unify_ibm": "UNIFY_IBM_PROMPT_CORE_LAW_V3",
    }
    key = section_family.strip().lower()
    if key not in markers:
        raise KeyError(f"unknown section_family for core-law marker: {section_family!r}")
    return markers[key]


__all__ = [
    "KNOWN_CONTRACT_IDS",
    "core_law_marker_for_section",
    "d0_untrusted_fence_reference_line",
    "load_pa_core_law_contract",
    "load_pa_core_law_document",
    "s0_truth_oath_reference_line",
]
