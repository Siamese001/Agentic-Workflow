"""I0-aligned claim_text vs proof_text policy for executive-summary C0 facts (W2)."""

from __future__ import annotations

import re
from typing import Any

CLAIM_PROOF_SCHEMA_VERSION = "master_skills_arsenal_claim_proof_v2"

# Substrings banned in display-allowed claim_text (credential_policy_v1 + S5 employer/FSA inventory).
CLAIM_TEXT_BANNED_SUBSTRINGS: tuple[str, ...] = (
    "fellow of the society of actuaries",
    "aws certified",
    "databricks lakehouse",
    " towers perrin",
    " ing,",
    " aetna",
    "fsa credential",
    "multi-greek hedging",
    "multi-agent orchestration",
    "graphrag retrieval",
    "sandboxed execution",
    "validation controls, and replayable execution traces",
    "deterministic routing, multi-agent orchestration",
)

# Mechanism-inventory comma-chain detector (neg_mechanism_inventory_001).
_MECHANISM_CHAIN_PARTS = (
    "deterministic routing",
    "multi-agent orchestration",
    "graphrag",
    "sandboxed execution",
    "policy gating",
    "validation controls",
    "replayable execution traces",
)


def normalize_claim_text_for_audit(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def claim_text_violates_i0_display_policy(claim_text: str) -> list[str]:
    """Return human-readable violation codes; empty list means PASS for I0 display policy."""
    norm = normalize_claim_text_for_audit(claim_text)
    if not norm:
        return ["claim_text_empty"]
    violations: list[str] = []
    for banned in CLAIM_TEXT_BANNED_SUBSTRINGS:
        if banned in norm:
            violations.append(f"banned_substring:{banned}")
    chain_hits = sum(1 for part in _MECHANISM_CHAIN_PARTS if part in norm)
    if chain_hits >= 3:
        violations.append(f"mechanism_inventory_chain_hits:{chain_hits}")
    return violations


def validate_claim_proof_row(row: dict[str, Any]) -> list[str]:
    """Validate one candidate fact row for claim/proof split invariants."""
    issues: list[str] = []
    claim = str(row.get("claim_text") or "").strip()
    proof = row.get("proof_text")
    if not claim:
        issues.append("missing_claim_text")
        return issues
    if proof is None:
        return issues
    proof_s = str(proof).strip()
    if not proof_s:
        issues.append("empty_proof_text")
        return issues
    if claim == proof_s:
        issues.append("claim_text_equals_proof_text")
    issues.extend(claim_text_violates_i0_display_policy(claim))
    return issues


def apply_w2_offending_fact_migrations(row: dict[str, Any]) -> dict[str, Any]:
    """Deterministic W2.2 migration for the two Brown-offending facts."""
    fid = str(row.get("candidate_fact_id") or row.get("fact_id") or "").strip()
    out = dict(row)
    if fid == "fact_engineering_platform_001":
        original = str(out.get("claim_text") or "").strip()
        out["proof_text"] = out.get("proof_text") or original
        out["claim_text"] = (
            "Designed and operationalized a governed agentic AI platform for regulated enterprise "
            "workflows, improving control-plane delivery, validation discipline, and audit-ready execution."
        )
        out["claim_proof_split_version"] = CLAIM_PROOF_SCHEMA_VERSION
        return out
    if fid == "fact_engineering_platform_002":
        original = str(out.get("claim_text") or "").strip()
        out["proof_text"] = out.get("proof_text") or original
        # forward_projection_preferred_c0_display_text: when this fact is assigned to an
        # S6 capstone position, use this forward-modal framing instead of the backward
        # past-tense "Built and applied..." claim text. RC-C from plan
        # exec-summary-rc-structural-repair-f4a8c2.
        out["forward_projection_preferred_c0_display_text"] = (
            "Software dependency graph intelligence enables accelerated legacy-system analysis, "
            "exposes architecture dependency chains, and improves transformation visibility "
            "across enterprise complexity."
        )
        out["claim_proof_split_version"] = CLAIM_PROOF_SCHEMA_VERSION
        return out
    if fid == "fact_quant_hpc_003":
        original = str(out.get("claim_text") or "").strip()
        out["proof_text"] = out.get("proof_text") or original
        out["claim_text"] = (
            "Built quantitative rigor through derivatives pricing, capital modeling, and portfolio "
            "stress analytics across early-career actuarial roles."
        )
        # preferred_c0_display_text is the safe display framing for C0 prompt injection:
        # the raw claim_text above contains "derivatives pricing" which triggers
        # x2_exec_summary_s5_no_derivatives_inventory when passed verbatim to the LLM.
        # format_selected_facts_for_c0 reads this field before claim_text.
        out["preferred_c0_display_text"] = (
            "That governance discipline is grounded in quantitative rigor established through "
            "FSA-chartered actuarial work in capital modeling and portfolio stress analytics, "
            "informing data governance and AI strategy at scale."
        )
        out["claim_proof_split_version"] = CLAIM_PROOF_SCHEMA_VERSION
        return out
    return out
