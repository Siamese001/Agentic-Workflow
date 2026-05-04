"""W2 sentinel tests for apps_lic R4 entrypoint + manifest + static DAG.

Covers P4, P5, P6:
- P4: integrated_r4_lic_pipeline_run.py exists; apps_lic identity constants correct;
       LicR4RunResult declared; R5 terminal path wired.
- P5: PreloadedOutreachContextManifest has exactly 35 fields; manifest_hash is
       deterministic; build_manifest() works; BriefingReady validation enforces all
       8 criteria with correct R5 reason codes.
- P6: apps_lic_static_dag.yaml exists; has exactly 5 stages in correct order;
       invariants declared; forbidden send_mode entries present.

Plan: apps-lic-canonical-spine-wireup-e7c2a5 W2.
"""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import fields as dc_fields
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_lic"
ENTRYPOINTS_DIR = REPO_ROOT / "agentic_core" / "runtime" / "entrypoints"

R4_LIC_ENTRYPOINT = ENTRYPOINTS_DIR / "integrated_r4_lic_pipeline_run.py"
MANIFEST_MODULE = APP_DIR / "integrations" / "preloaded_outreach_context_manifest.py"
STATIC_DAG = APP_DIR / "config" / "apps_lic_static_dag.yaml"


def _src(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# P4 — R4 entrypoint with apps_lic identity binding
# ---------------------------------------------------------------------------

def test_r4_lic_entrypoint_exists():
    """P4: integrated_r4_lic_pipeline_run.py must exist."""
    assert R4_LIC_ENTRYPOINT.exists(), (
        f"Missing: {R4_LIC_ENTRYPOINT}. "
        "W2 P4 requires a thin R4 wrapper with apps_lic identity."
    )


def test_r4_lic_identity_constants():
    """P4: APP_NAME, SOURCE_CHANNEL, DECLARED_SCHEMA must use apps_lic identity."""
    from agentic_core.runtime.entrypoints.integrated_r4_lic_pipeline_run import (
        APP_NAME,
        SOURCE_CHANNEL,
        DECLARED_SCHEMA,
        ROUTE_ID,
    )
    assert APP_NAME == "apps_lic"
    assert "apps_lic" in SOURCE_CHANNEL
    assert "apps_lic" in DECLARED_SCHEMA
    assert ROUTE_ID == "R4_SINGLE_ACTION"


def test_r4_lic_result_type_declared():
    """P4: LicR4RunResult must be importable and have required fields."""
    from agentic_core.runtime.entrypoints.integrated_r4_lic_pipeline_run import (
        LicR4RunResult,
    )
    result_fields = {f.name for f in dc_fields(LicR4RunResult)}
    required = {
        "run_id", "request_id", "route_id", "x3_disposition",
        "terminal_r5", "terminal_r5_reason", "artifact_dir",
    }
    missing = required - result_fields
    assert not missing, f"LicR4RunResult missing fields: {missing}"


def test_r4_lic_entrypoint_distinct_from_rg():
    """P4: apps_lic entrypoint must have its own identity constants, not apps_rg's."""
    from agentic_core.runtime.entrypoints.integrated_r4_lic_pipeline_run import (
        APP_NAME,
        SOURCE_CHANNEL,
        DECLARED_SCHEMA,
        _PRODUCER_COMPONENT,
    )
    # Runtime constants must be apps_lic — docstring may reference rg for contrast
    assert APP_NAME == "apps_lic"
    assert SOURCE_CHANNEL == "apps_lic_cli"
    assert DECLARED_SCHEMA == "apps_lic_outreach_v1"
    assert "integrated_r4_lic_pipeline_run" in _PRODUCER_COMPONENT
    assert "apps_rg" not in _PRODUCER_COMPONENT


def test_r4_lic_r5_terminal_path_present():
    """P4: Entrypoint must have an R5 terminal code path that skips L2."""
    src = _src(R4_LIC_ENTRYPOINT)
    assert "terminal_r5=True" in src or "terminal_r5 = True" in src, (
        "R5 terminal path not found in R4 lic entrypoint. "
        "When L0 gate fires, L2 must be skipped."
    )
    assert "_build_r5_exit_receipts" in src


def test_r4_lic_no_durable_write_in_entrypoint():
    """P4: R4 lic entrypoint must not perform durable writes to artifact dir outside
    the manifest seal at the end (run manifest JSON is allowed)."""
    import ast
    tree = ast.parse(_src(R4_LIC_ENTRYPOINT))
    write_violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = ""
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name == "open" and len(node.args) >= 2:
                mode_arg = node.args[1]
                if isinstance(mode_arg, ast.Constant) and isinstance(mode_arg.value, str):
                    if any(c in mode_arg.value for c in ("w", "a", "x")):
                        write_violations.append(f"open(..., {mode_arg.value!r})")
    assert not write_violations, (
        f"Write-mode open() in R4 lic entrypoint: {write_violations}. "
        "Durable writes must go through Exit → UWG → L4."
    )


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
# P6 — apps_lic_static_dag.yaml (5 stages)
# ---------------------------------------------------------------------------

def test_static_dag_exists():
    """P6: apps_lic_static_dag.yaml must exist."""
    assert STATIC_DAG.exists(), f"Missing: {STATIC_DAG}"


def test_static_dag_has_5_stages():
    """P6: Static DAG must have exactly 5 stages."""
    with STATIC_DAG.open(encoding="utf-8") as fh:
        dag = yaml.safe_load(fh)
    stages = dag.get("stages", [])
    assert len(stages) == 5, (
        f"apps_lic_static_dag.yaml has {len(stages)} stages; expected 5. "
        "Plan spec: load_manifest → validate_context → plan_message → compose_draft → seal_output."
    )


def test_static_dag_stage_order():
    """P6: Stages must be in canonical order with correct stage_ids."""
    with STATIC_DAG.open(encoding="utf-8") as fh:
        dag = yaml.safe_load(fh)
    expected_ids = [
        "load_manifest",
        "validate_context",
        "plan_message",
        "compose_draft",
        "seal_output",
    ]
    actual_ids = [s["stage_id"] for s in dag["stages"]]
    assert actual_ids == expected_ids, (
        f"Stage order mismatch. Expected {expected_ids}, got {actual_ids}."
    )
    # Verify order field matches position
    for i, stage in enumerate(dag["stages"], start=1):
        assert stage["order"] == i, (
            f"Stage {stage['stage_id']} has order={stage['order']}; expected {i}."
        )


def test_static_dag_forbidden_send_modes_referenced():
    """P6: Static DAG must reference the forbidden send_mode values in compose_draft."""
    with STATIC_DAG.open(encoding="utf-8") as fh:
        content = fh.read()
    # The DAG must document that forbidden modes cause fail-closed
    assert "send_now" in content or "forbidden_send_mode" in content, (
        "apps_lic_static_dag.yaml must reference forbidden send_mode handling."
    )


def test_static_dag_route_family():
    """P6: Static DAG must declare route_family=R4_SINGLE_ACTION."""
    with STATIC_DAG.open(encoding="utf-8") as fh:
        dag = yaml.safe_load(fh)
    assert dag.get("route_family") == "R4_SINGLE_ACTION", (
        f"route_family={dag.get('route_family')!r}; expected 'R4_SINGLE_ACTION'."
    )


def test_static_dag_no_provider_calls_declared():
    """P6: No stage in the static DAG may declare calls to external providers."""
    with STATIC_DAG.open(encoding="utf-8") as fh:
        content = fh.read()
    provider_keywords = ["openai", "anthropic", "gemini", "llm_call", "provider_call"]
    found = [kw for kw in provider_keywords if kw in content.lower()]
    assert not found, (
        f"Provider references in static DAG: {found}. "
        "L2 static DAG is composition-only; no provider calls allowed."
    )
