"""W2 sentinel tests for apps_lic manifest + HOP L2 SSOT (hard-delete convergence).

Covers:
- P5: PreloadedOutreachContextManifest (35 fields, BriefingReady)
- P6: hop_pipeline.py REGISTRY (replaces retired YAML static DAG)
- Product __main__ uses canonical_dispatch only; integrated_r4 deleted from agentic_core.

Plan: apps-lic-spine-product-convergence hard-delete.
"""
from __future__ import annotations

import uuid
from dataclasses import fields as dc_fields
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_lic"
ENTRYPOINTS_DIR = REPO_ROOT / "agentic_core" / "runtime" / "entrypoints"

R4_LIC_ENTRYPOINT = ENTRYPOINTS_DIR / "integrated_r4_lic_pipeline_run.py"
MANIFEST_MODULE = APP_DIR / "integrations" / "preloaded_outreach_context_manifest.py"
STATIC_DAG = APP_DIR / "config" / "apps_lic_static_dag.yaml"


# ---------------------------------------------------------------------------
# Hard-delete — integrated_r4 removed from agentic_core
# ---------------------------------------------------------------------------

def test_integrated_r4_lic_entrypoint_deleted():
    """integrated_r4_lic_pipeline_run must not exist in agentic_core."""
    assert not R4_LIC_ENTRYPOINT.exists(), (
        f"Retired runner must be deleted: {R4_LIC_ENTRYPOINT}"
    )


def test_r4_lic_entrypoint_distinct_from_rg():
    """P4: Product __main__ must not resolve apps_rg L2 recipes or import GovernedLic."""
    import ast

    from agentic_core.runtime.l2_recipe_resolver import _register_builtin_recipes

    registry = _register_builtin_recipes()
    assert "apps_rg" in registry
    assert "apps_lic" not in registry
    main_src = (APP_DIR / "__main__.py").read_text(encoding="utf-8")
    assert "run_canonical_apps_lic_spine" in main_src
    tree = ast.parse(main_src)
    forbidden_modules = {
        "governed_lic_run",
        "spine_handoff",
        "campaign_batch_orchestrator",
        "integrated_r4_lic_pipeline_run",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split(".")[0]
                assert mod not in forbidden_modules, f"Forbidden import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                assert root not in forbidden_modules, f"Forbidden import from: {node.module}"


# ---------------------------------------------------------------------------
# P5 — PreloadedOutreachContextManifest (35 fields)
# ---------------------------------------------------------------------------

def test_manifest_module_exists():
    """P5: preloaded_outreach_context_manifest.py must exist."""
    assert MANIFEST_MODULE.exists(), f"Missing: {MANIFEST_MODULE}"


def test_manifest_has_35_fields():
    """P5: PreloadedOutreachContextManifest must have exactly 35 fields."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        PreloadedOutreachContextManifest,
    )
    count = len(dc_fields(PreloadedOutreachContextManifest))
    assert count == 35, (
        f"PreloadedOutreachContextManifest has {count} fields; expected 35. "
        "Plan spec requires exactly 35 fields."
    )


def test_manifest_has_required_governance_fields():
    """P5: Manifest must have claim_permission_map, proof_mode, omission_policy,
    personalization_mode, confidence_score, audit_refs, content_hashes, origin_label_map."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        PreloadedOutreachContextManifest,
    )
    field_names = {f.name for f in dc_fields(PreloadedOutreachContextManifest)}
    required = {
        "claim_permission_map",
        "proof_mode",
        "personalization_mode",
        "omission_policy",
        "confidence_score",
        "audit_refs",
        "content_hashes",
        "origin_label_map",
        "manifest_hash",
        "freshness_status",
        "source_items",
        "unsupported_fact_flags",
    }
    missing = required - field_names
    assert not missing, f"Manifest missing required governance fields: {missing}"


def _make_test_manifest(**overrides):
    """Build a minimal valid manifest for testing."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        build_manifest,
        SourceItem,
    )
    defaults = dict(
        manifest_id=str(uuid.uuid4()),
        request_id="req-test-001",
        run_id="run-test-001",
        trace_id="tr-test-001",
        policy_hash="sha256:abc123",
        blueprint_hash="sha256:def456",
        replay_key="r4_lic:0000000000000000",
        user_profile_ref="sha256:profile001",
        resume_ref="sha256:resume001",
        target_role_ref="sha256:jd001",
        job_description_ref="sha256:jd001",
        application_status="none",
        company_brief_ref="sha256:company001",
        recipient_brief_ref="sha256:recipient001",
        relationship_context_ref="sha256:rel001",
        channel="email",
        outreach_mode="cold",
        recipient_class="RECRUITER",
        recipient_seniority="MANAGER",
        relationship_distance="cold",
        source_items=[SourceItem(
            source_id="s1", source_type="resume", label="Resume",
            uri="sha256:resume001", field_ref="resume_ref"
        )],
        origin_label_map={"resume_ref": "Resume v1"},
        content_hashes={"resume_ref": "sha256:resume001"},
        freshness_status="fresh",
        unsupported_fact_flags=[],
        claim_permission_map={"default_claim": "allowed"},
        proof_mode="resume_metric",
        personalization_mode="role",
        omission_policy="omit_unsupported",
        confidence_score=0.85,
        send_mode="draft_only",
        personalization_confidence=0.80,
        required_hitl_flags=[],
        audit_refs=["tr-upstream-001"],
    )
    defaults.update(overrides)
    return build_manifest(**defaults)


def test_manifest_hash_is_deterministic():
    """P5: Two manifests with identical inputs must produce the same manifest_hash."""
    m1 = _make_test_manifest()
    m2 = _make_test_manifest(
        manifest_id=m1.manifest_id,
        request_id=m1.request_id,
        run_id=m1.run_id,
        trace_id=m1.trace_id,
    )
    assert m1.manifest_hash == m2.manifest_hash


def test_manifest_hash_changes_on_field_change():
    """P5: Changing any field must produce a different manifest_hash."""
    m1 = _make_test_manifest()
    m2 = _make_test_manifest(
        manifest_id=m1.manifest_id,
        request_id=m1.request_id,
        run_id=m1.run_id,
        trace_id=m1.trace_id,
        confidence_score=0.50,  # changed
    )
    assert m1.manifest_hash != m2.manifest_hash


def test_manifest_is_frozen():
    """P5: PreloadedOutreachContextManifest must be frozen (immutable)."""
    m = _make_test_manifest()
    with pytest.raises(AttributeError):  # frozen dataclass raises FrozenInstanceError (subclass of AttributeError)
        m.channel = "linkedin"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# P5 — BriefingReady validation (8 criteria)
# ---------------------------------------------------------------------------

def test_briefing_ready_passes_on_valid_manifest():
    """P5: validate_briefing_ready returns is_valid=True for a complete manifest."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        validate_briefing_ready,
    )
    m = _make_test_manifest()
    result = validate_briefing_ready(m)
    assert result.is_valid, f"Expected valid, got r5={result.r5_reason_code}: {result.detail}"


def test_apps_lic_briefing_ready_requires_confidence_freshness_sources_hashes_and_audit_refs():
    """P5 plan sentinel: BriefingReady checks all 8 criteria end-to-end."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        validate_briefing_ready,
    )

    # Low confidence → APPS_RESEARCH_WEAK_SUPPORT
    m = _make_test_manifest(confidence_score=0.30)
    r = validate_briefing_ready(m, confidence_threshold=0.60)
    assert not r.is_valid and r.r5_reason_code == "APPS_RESEARCH_WEAK_SUPPORT"

    # Stale freshness → APPS_RESEARCH_STALE
    m = _make_test_manifest(freshness_status="stale")
    r = validate_briefing_ready(m)
    assert not r.is_valid and r.r5_reason_code == "APPS_RESEARCH_STALE"

    # Empty source_items → APPS_RESEARCH_EMPTY
    m = _make_test_manifest(source_items=[])
    r = validate_briefing_ready(m)
    assert not r.is_valid and r.r5_reason_code == "APPS_RESEARCH_EMPTY"

    # Empty audit_refs → APPS_RESEARCH_BLOCKED
    m = _make_test_manifest(audit_refs=[])
    r = validate_briefing_ready(m)
    assert not r.is_valid and r.r5_reason_code == "APPS_RESEARCH_BLOCKED"

    # Empty content_hashes → APPS_RESEARCH_EMPTY
    m = _make_test_manifest(content_hashes={})
    r = validate_briefing_ready(m)
    assert not r.is_valid and r.r5_reason_code == "APPS_RESEARCH_EMPTY"

    # Empty origin_label_map → APPS_RESEARCH_EMPTY
    m = _make_test_manifest(origin_label_map={})
    r = validate_briefing_ready(m)
    assert not r.is_valid and r.r5_reason_code == "APPS_RESEARCH_EMPTY"

    # Unclassified unsupported gap → APPS_RESEARCH_BLOCKED
    m = _make_test_manifest(
        unsupported_fact_flags=["unclassified_claim"],
        claim_permission_map={},  # not classified
    )
    r = validate_briefing_ready(m)
    assert not r.is_valid and r.r5_reason_code == "APPS_RESEARCH_BLOCKED"


def test_briefing_ready_allows_stale_when_policy_permits():
    """P5: validate_briefing_ready with allow_stale=True accepts stale freshness."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        validate_briefing_ready,
    )
    m = _make_test_manifest(freshness_status="stale")
    result = validate_briefing_ready(m, allow_stale=True)
    assert result.is_valid, f"Expected valid with allow_stale=True, got: {result.detail}"


# ---------------------------------------------------------------------------
# P6 — hop_pipeline.py REGISTRY (replaces apps_lic_static_dag.yaml)
# ---------------------------------------------------------------------------

def test_static_yaml_dag_deleted():
    """P4: Legacy static YAML L2 DAG removed."""
    assert not STATIC_DAG.exists(), f"Retired: {STATIC_DAG}"


def test_hop_pipeline_registry_has_nine_stages():
    """P6: Product L2 SSOT is 9-stage HOP REGISTRY."""
    from apps_lic.config.hop_pipeline import REGISTRY

    assert REGISTRY.stage_count() == 9


def test_hop_pipeline_stage_order():
    """P6: HOP stages follow canonical outreach order."""
    from apps_lic.config.hop_pipeline import REGISTRY

    names = [s.stage_name for s in REGISTRY.ordered()]
    assert names[0] == "profile_analysis"
    assert "generation" in names
    assert names[-1] == "integration"


def test_hop_pipeline_generation_stage_present():
    """P6: Generation stage exists (draft generation seam)."""
    from apps_lic.config.hop_pipeline import REGISTRY

    assert any(s.stage_name == "generation" for s in REGISTRY.ordered())


def test_static_dag_route_family_placeholder():
    """P6: Route family R4 is L0-owned, not YAML DAG."""
    from apps_lic.runtime.bindings.l0_binding import ROUTE_FAMILY_R4_MANAGED_DRAFT

    assert ROUTE_FAMILY_R4_MANAGED_DRAFT == "R4_MANAGED_DRAFT"
