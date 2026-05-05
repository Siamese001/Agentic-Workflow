"""P1.3 Governance tests — apps_underwriting_ai routing matrix.

Enforces that UnderwritingRouteSelector outputs the correct route_family
and route_mode for all 7 demo request types in the route decision matrix,
and that the selector is metadata-only (no imports of engines, C0 adapters,
providers, or L4 write surfaces).

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 P1.3.

All 10 tests pass immediately after P1.2 creates UnderwritingRouteSelector.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_underwriting_ai"
SELECTOR_PATH = APP_DIR / "integrations" / "underwriting_route_selector.py"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_underwriting_ai.integrations.underwriting_route_selector import (
    RouteSelectorInput,
    UnderwritingRouteSelector,
    build_r1a_cache_key,
)

_selector = UnderwritingRouteSelector()


# ---------------------------------------------------------------------------
# Routing test 1 — full underwriting demo → R3R4_MANAGED_WORKFLOW
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_full_underwriting_demo_routes_to_r3r4_managed_workflow() -> None:
    """Full underwriting demo request must resolve to R3R4_MANAGED_WORKFLOW / FULL_DECISION_PACKET."""
    inp = RouteSelectorInput(
        product_class="MORTGAGE_DEMO",
        applicant_type="INDIVIDUAL",
        submitted_document_profile=["BANK_STATEMENT", "TAX_RETURN", "CREDIT_REPORT"],
        completeness_score=0.95,
        contradiction_score=0.05,
        risk_tier_band="LOW",
        demo_mode="full_decision",
        demo_policy_profile="fixture_policy_v1",
    )
    out = _selector.select(inp)
    assert out.canonical_route_family == "R3R4_MANAGED_WORKFLOW", (
        f"Full underwriting demo routed to {out.canonical_route_family!r}; "
        "expected R3R4_MANAGED_WORKFLOW."
    )
    assert out.underwriting_route_mode == "FULL_DECISION_PACKET", (
        f"Full underwriting demo mode={out.underwriting_route_mode!r}; "
        "expected FULL_DECISION_PACKET."
    )
    assert out.l3_required is True
    assert out.c0_mode == "SUBMITTED_DOCUMENT_EVIDENCE_ONLY"
    assert out.exit_mode == "FAIL_CLOSED"


# ---------------------------------------------------------------------------
# Routing test 2 — evidence-only review → R3_SIMPLE_GROUNDED_READ
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_evidence_only_review_routes_to_r3_simple_grounded_read() -> None:
    """Evidence-only review must resolve to R3_SIMPLE_GROUNDED_READ / EVIDENCE_ONLY_REVIEW."""
    inp = RouteSelectorInput(
        product_class="MORTGAGE_DEMO",
        applicant_type="INDIVIDUAL",
        submitted_document_profile=["BANK_STATEMENT"],
        completeness_score=0.70,
        contradiction_score=0.10,
        risk_tier_band="MEDIUM",
        demo_mode="evidence_only",
    )
    out = _selector.select(inp)
    assert out.canonical_route_family == "R3_SIMPLE_GROUNDED_READ", (
        f"Evidence-only routed to {out.canonical_route_family!r}; "
        "expected R3_SIMPLE_GROUNDED_READ."
    )
    assert out.underwriting_route_mode == "EVIDENCE_ONLY_REVIEW"
    assert out.l3_required is False
    assert out.c0_mode == "SUBMITTED_DOCUMENT_EVIDENCE_ONLY"


# ---------------------------------------------------------------------------
# Routing test 3 — schema / demo utility → R4_SINGLE_ACTION
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_schema_utility_routes_to_r4_single_action() -> None:
    """Schema / demo utility must resolve to R4_SINGLE_ACTION / ADMIN_OR_SCHEMA_UTILITY."""
    inp = RouteSelectorInput(
        demo_mode="schema_utility",
        completeness_score=0.0,
    )
    out = _selector.select(inp)
    assert out.canonical_route_family == "R4_SINGLE_ACTION", (
        f"Schema utility routed to {out.canonical_route_family!r}; expected R4_SINGLE_ACTION."
    )
    assert out.underwriting_route_mode == "ADMIN_OR_SCHEMA_UTILITY"
    assert out.l3_required is False
    assert out.c0_mode == "NONE"


# ---------------------------------------------------------------------------
# Routing test 4 — exact replay → R1A_EXACT_CACHE
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_exact_replay_routes_to_r1a_exact_cache() -> None:
    """Exact replay request (cache key present) must resolve to R1A_EXACT_CACHE / EXACT_REPLAY."""
    inp = RouteSelectorInput(
        product_class="MORTGAGE_DEMO",
        completeness_score=0.90,
        demo_mode="full_decision",
        exact_cache_key="sha256:abcdef1234567890",
    )
    out = _selector.select(inp)
    assert out.canonical_route_family == "R1A_EXACT_CACHE", (
        f"Exact replay routed to {out.canonical_route_family!r}; expected R1A_EXACT_CACHE."
    )
    assert out.underwriting_route_mode == "EXACT_REPLAY"
    assert out.cache_policy == "ALLOW_EXACT"
    assert out.l3_required is False


# ---------------------------------------------------------------------------
# Routing test 5 — doc-help only → R1B_SEMANTIC_CACHE
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_doc_help_routes_to_r1b_semantic_cache() -> None:
    """Doc-help demo mode must resolve to R1B_SEMANTIC_CACHE / DOC_HELP_ONLY (no verdict reuse)."""
    inp = RouteSelectorInput(
        completeness_score=0.80,
        demo_mode="doc_help",
        semantic_cache_available=True,
    )
    out = _selector.select(inp)
    assert out.canonical_route_family == "R1B_SEMANTIC_CACHE", (
        f"Doc-help routed to {out.canonical_route_family!r}; expected R1B_SEMANTIC_CACHE."
    )
    assert out.underwriting_route_mode == "DOC_HELP_ONLY"
    assert out.cache_policy == "ALLOW_SEMANTIC_DOC_HELP_ONLY"
    assert "no_verdict_reuse" in out.route_reason_codes


# ---------------------------------------------------------------------------
# Routing test 6 — missing fixture documents → R5_FALLBACK
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_missing_documents_routes_to_r5_fallback() -> None:
    """Incomplete document set (completeness below threshold) must resolve to R5_FALLBACK."""
    inp = RouteSelectorInput(
        product_class="MORTGAGE_DEMO",
        submitted_document_profile=[],
        completeness_score=0.20,
        demo_mode="full_decision",
    )
    out = _selector.select(inp)
    assert out.canonical_route_family == "R5_FALLBACK", (
        f"Missing docs routed to {out.canonical_route_family!r}; expected R5_FALLBACK."
    )
    assert out.underwriting_route_mode == "MISSING_INPUT_SAFE_FALLBACK"
    assert out.exit_mode == "FAIL_CLOSED"
    assert any("completeness_score" in rc for rc in out.route_reason_codes)


# ---------------------------------------------------------------------------
# Routing test 7 — borderline synthetic case → R3R4_MANAGED_WORKFLOW + HITL posture
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_borderline_synthetic_case_routes_to_r3r4_with_hitl_posture() -> None:
    """Borderline risk band must resolve to R3R4_MANAGED_WORKFLOW / BORDERLINE_HITL_POSTURE."""
    inp = RouteSelectorInput(
        product_class="MORTGAGE_DEMO",
        applicant_type="INDIVIDUAL",
        submitted_document_profile=["BANK_STATEMENT", "TAX_RETURN"],
        completeness_score=0.75,
        contradiction_score=0.10,
        risk_tier_band="BORDERLINE",
        demo_mode="full_decision",
    )
    out = _selector.select(inp)
    assert out.canonical_route_family == "R3R4_MANAGED_WORKFLOW", (
        f"Borderline case routed to {out.canonical_route_family!r}; "
        "expected R3R4_MANAGED_WORKFLOW."
    )
    assert out.underwriting_route_mode == "BORDERLINE_HITL_POSTURE", (
        f"Borderline mode={out.underwriting_route_mode!r}; expected BORDERLINE_HITL_POSTURE."
    )
    assert out.hitl_posture in ("SOFT_POSTURE", "HARD_FREEZE"), (
        f"Borderline hitl_posture={out.hitl_posture!r}; expected SOFT_POSTURE or HARD_FREEZE."
    )
    assert out.l3_required is True
    assert out.exit_mode == "FAIL_CLOSED"


# ---------------------------------------------------------------------------
# Routing test 8 — high contradiction score triggers HARD_FREEZE
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_high_contradiction_score_triggers_hard_freeze() -> None:
    """Contradiction score >= 0.60 must set hitl_posture=HARD_FREEZE."""
    inp = RouteSelectorInput(
        product_class="MORTGAGE_DEMO",
        submitted_document_profile=["BANK_STATEMENT", "TAX_RETURN"],
        completeness_score=0.85,
        contradiction_score=0.75,
        risk_tier_band="MEDIUM",
        demo_mode="full_decision",
    )
    out = _selector.select(inp)
    assert out.canonical_route_family == "R3R4_MANAGED_WORKFLOW"
    assert out.hitl_posture == "HARD_FREEZE", (
        f"contradiction_score=0.75 produced hitl_posture={out.hitl_posture!r}; "
        "expected HARD_FREEZE."
    )
    assert any("hard_freeze" in rc for rc in out.route_reason_codes)


# ---------------------------------------------------------------------------
# Routing test 9 — R3R4 route carries required spine flags
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_r3r4_route_carries_all_required_spine_flags() -> None:
    """R3R4_MANAGED_WORKFLOW route must declare all required spine contract fields."""
    inp = RouteSelectorInput(
        product_class="MORTGAGE_DEMO",
        submitted_document_profile=["BANK_STATEMENT", "TAX_RETURN", "CREDIT_REPORT"],
        completeness_score=0.90,
        contradiction_score=0.05,
        risk_tier_band="LOW",
        demo_mode="full_decision",
    )
    out = _selector.select(inp)
    assert out.canonical_route_family == "R3R4_MANAGED_WORKFLOW"
    assert out.l3_required is True, "R3R4 route must set l3_required=True"
    assert out.c0_mode == "SUBMITTED_DOCUMENT_EVIDENCE_ONLY", (
        "R3R4 route must set c0_mode=SUBMITTED_DOCUMENT_EVIDENCE_ONLY"
    )
    assert out.pa_required == "rationale_enrichment_enabled", (
        "R3R4 route must set pa_required=rationale_enrichment_enabled"
    )
    assert out.exit_mode == "FAIL_CLOSED", "R3R4 route must set exit_mode=FAIL_CLOSED"
    assert out.cache_policy == "NO_CACHE", (
        "R3R4 route must set cache_policy=NO_CACHE (no verdict reuse via cache)"
    )


# ---------------------------------------------------------------------------
# Routing test 10 — selector is metadata-only (no engine/provider/L4 imports)
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_underwriting_route_selector_is_metadata_only() -> None:
    """UnderwritingRouteSelector must not import engines, providers, C0, or L4 surfaces."""
    assert SELECTOR_PATH.exists(), f"underwriting_route_selector.py missing: {SELECTOR_PATH}"
    src = SELECTOR_PATH.read_text(encoding="utf-8")
    tree = ast.parse(src)

    forbidden_modules = [
        "apps_underwriting_ai.engines",
        "underwriting_c0_adapter",
        "underwriting_l3_workflow_adapter",
        "underwriting_l2_step_adapters",
        "underwriting_exit_fec_producer",
        "openai",
        "anthropic",
        "cohere",
        "litellm",
        "agentic_core.L4",
        "L4_state",
    ]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in forbidden_modules:
                    if alias.name.startswith(forbidden):
                        pytest.fail(
                            f"UnderwritingRouteSelector imports forbidden module "
                            f"'{alias.name}' at line {node.lineno}. "
                            "The selector is metadata-only and must not import "
                            "engines, C0 adapters, providers, or L4 write surfaces."
                        )
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for forbidden in forbidden_modules:
                if mod.startswith(forbidden):
                    pytest.fail(
                        f"UnderwritingRouteSelector imports from forbidden module "
                        f"'{mod}' at line {node.lineno}. "
                        "The selector is metadata-only."
                    )


# ---------------------------------------------------------------------------
# D2.2 — R1A cache key hit-path tests (5 cases)
# ---------------------------------------------------------------------------

_BASE_KEY_KWARGS: dict = {
    "request_envelope_hash": "sha256-req-aabbcc",
    "doc_content_hashes": ["sha256-doc-001", "sha256-doc-002"],
    "policy_hash": "sha256-policy-standard-v1",
    "blueprint_hash": "sha256-blueprint-v1",
    "scorer_version": "deterministic_risk_scorer_v1",
    "schema_version": "1.1",
}


@pytest.mark.governance
def test_r1a_cache_key_exact_hit_same_inputs() -> None:
    """Same inputs always produce the same 64-char hex key (exact-cache hit)."""
    k1 = build_r1a_cache_key(**_BASE_KEY_KWARGS)
    k2 = build_r1a_cache_key(**_BASE_KEY_KWARGS)
    assert k1 == k2, "Same inputs must yield identical R1A cache key."
    assert len(k1) == 64, f"Key must be 64 hex chars (SHA-256); got {len(k1)}."


@pytest.mark.governance
def test_r1a_cache_key_policy_drift_produces_miss() -> None:
    """Changing policy_hash must produce a different key (policy drift → miss)."""
    k_base = build_r1a_cache_key(**_BASE_KEY_KWARGS)
    drifted = dict(_BASE_KEY_KWARGS, policy_hash="sha256-policy-DRIFTED-v2")
    k_drift = build_r1a_cache_key(**drifted)
    assert k_base != k_drift, (
        "Policy drift must produce a distinct key; cache must not replay stale decision."
    )


@pytest.mark.governance
def test_r1a_cache_key_doc_drift_produces_miss() -> None:
    """Changing any document content hash must produce a different key (doc drift → miss)."""
    k_base = build_r1a_cache_key(**_BASE_KEY_KWARGS)
    drifted = dict(
        _BASE_KEY_KWARGS,
        doc_content_hashes=["sha256-doc-001", "sha256-doc-NEWCONTENT"],
    )
    k_drift = build_r1a_cache_key(**drifted)
    assert k_base != k_drift, (
        "Document content drift must produce a distinct key."
    )


@pytest.mark.governance
def test_r1a_cache_key_scorer_version_bump_produces_miss() -> None:
    """Bumping scorer_version must produce a different key (scorer bump → miss)."""
    k_base = build_r1a_cache_key(**_BASE_KEY_KWARGS)
    drifted = dict(_BASE_KEY_KWARGS, scorer_version="deterministic_risk_scorer_v2")
    k_drift = build_r1a_cache_key(**drifted)
    assert k_base != k_drift, (
        "Scorer version bump must produce a distinct key."
    )


@pytest.mark.governance
def test_r1a_cache_key_schema_version_bump_produces_miss() -> None:
    """Bumping schema_version must produce a different key (schema bump → miss)."""
    k_base = build_r1a_cache_key(**_BASE_KEY_KWARGS)
    drifted = dict(_BASE_KEY_KWARGS, schema_version="1.2")
    k_drift = build_r1a_cache_key(**drifted)
    assert k_base != k_drift, (
        "Schema version bump must produce a distinct key."
    )
