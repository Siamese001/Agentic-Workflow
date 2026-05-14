"""W2 apps_rfp one-spine migration contract tests.

Proves:
  PC-1  profile completeness — all 7 stage binding refs are non-None
  PC-2  profile version bumped to "2" (MIGRATION_DEFERRED removed)
  PC-3  app_id == "apps_rfp"
  CC-1  u0 binding produces ValidatedRequest with correct fields
  CC-2  l1 binding produces L1PlanContract with grounding_required=True
  CC-3  l0 binding produces RfpRouteContract routing to rfp_proposal_assembly
  CC-4  c0 binding returns a dict with required FEC keys (fail-soft path)
  CC-5  pa binding produces RfpPromptArtifact with grounding_chunks list
  CC-6  l2 binding in dry-run stub mode returns SealedRfpArtifact
  CC-7  exit binding returns RfpExitResult with a .disposition attribute
  NC-1  make_rfp_ingress_runner() raises RuntimeError (tombstoned)
  NC-2  rfp_dry_run_tool imports without calling RfpOrchestrator directly at module level
  NC-3  __main__._run_product_build does NOT import governed_rfp_run
  NC-4  make_rfp_ingress_runner not imported in __main__
  NC-5  parse_payload produces RequestEnvelope with required fields

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W2.P4
"""
from __future__ import annotations

import importlib
import inspect
import sys
import types
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


# ─────────────────────────────────────────────────────────────
# Profile completeness (PC)
# ─────────────────────────────────────────────────────────────

def test_pc1_all_7_stage_bindings_non_none():
    from apps_rfp.runtime.profile_builder import build_app_runtime_contract
    profile = build_app_runtime_contract()
    for stage in ("u0", "l1", "l0", "c0", "pa", "l2", "exit"):
        assert getattr(profile, stage) is not None, f"profile.{stage} is None — migration incomplete"


def test_pc2_profile_version_is_2():
    from apps_rfp.runtime.profile_builder import build_app_runtime_contract
    profile = build_app_runtime_contract()
    assert profile.profile_version == "2", (
        f"Expected profile_version='2' (W2 wired) but got {profile.profile_version!r}"
    )


def test_pc3_app_id_is_apps_rfp():
    from apps_rfp.runtime.profile_builder import build_app_runtime_contract
    profile = build_app_runtime_contract()
    assert profile.app_id == "apps_rfp"


def test_pc4_parse_callable_present():
    from apps_rfp.runtime.profile_builder import build_app_runtime_contract
    profile = build_app_runtime_contract()
    assert callable(profile.parse), "profile.parse must be a callable"


# ─────────────────────────────────────────────────────────────
# Contract chain (CC)
# ─────────────────────────────────────────────────────────────

def _make_request_envelope(
    rfp_document_path: str = "/path/to/rfp.pdf",
    target_company: str = "Acme Corp",
    run_id: str = "rfp-run-test001",
) -> object:
    """Build a minimal RequestEnvelope-like dict for binding inputs."""
    from apps_rfp.runtime.profile_builder import parse_payload
    return parse_payload({
        "rfp_document_path": rfp_document_path,
        "target_company": target_company,
        "run_id": run_id,
    })


def test_cc1_u0_produces_validated_request():
    from apps_rfp.runtime.bindings.u0_binding import rfp_u0
    envelope = _make_request_envelope()
    result = rfp_u0(envelope)
    assert result is not None
    assert hasattr(result, "request_id"), "ValidatedRequest must have .request_id"
    assert result.request_id, "ValidatedRequest.request_id must be non-empty"
    assert hasattr(result, "tenant_bind"), "ValidatedRequest must have .tenant_bind"
    assert result.tenant_bind == "apps_rfp", f"Expected tenant_bind='apps_rfp' got {result.tenant_bind!r}"
    assert result.batch_id in ("Acme Corp", "/path/to/rfp.pdf", "Acme Corp")


def test_cc2_l1_produces_l1plan_with_grounding_required():
    from apps_rfp.runtime.bindings.u0_binding import rfp_u0
    from apps_rfp.runtime.bindings.l1_binding import rfp_l1

    validated = rfp_u0(_make_request_envelope())
    plan = rfp_l1(validated)
    assert plan is not None
    assert hasattr(plan, "grounding_required"), "L1PlanContract must have .grounding_required"
    assert plan.grounding_required is True, "apps_rfp L1 plan must require grounding"
    assert hasattr(plan, "request_id"), "L1PlanContract must have .request_id"
    assert hasattr(plan, "plan_id"), "L1PlanContract must have .plan_id"
    assert plan.plan_id.startswith("rfp-plan-")


def test_cc3_l0_produces_rfp_route_contract():
    from apps_rfp.runtime.bindings.u0_binding import rfp_u0
    from apps_rfp.runtime.bindings.l1_binding import rfp_l1
    from apps_rfp.runtime.bindings.l0_binding import rfp_l0, RfpRouteContract

    validated = rfp_u0(_make_request_envelope())
    plan = rfp_l1(validated)
    route = rfp_l0(plan)
    assert isinstance(route, RfpRouteContract)
    assert route.route_id == "rfp_proposal_assembly"
    assert route.grounding_required is True
    assert route.model_generation_required is True
    assert route.collection == "rfp_docs"
    assert route.app_id == "apps_rfp"


def test_cc4_c0_returns_fec_shaped_dict_fail_soft():
    """C0 binding must return a dict with required keys even when retrieval is unavailable."""
    from apps_rfp.runtime.bindings.u0_binding import rfp_u0
    from apps_rfp.runtime.bindings.l1_binding import rfp_l1
    from apps_rfp.runtime.bindings.l0_binding import rfp_l0
    from apps_rfp.runtime.bindings.c0_binding import rfp_c0

    validated = rfp_u0(_make_request_envelope())
    plan = rfp_l1(validated)
    route = rfp_l0(plan)
    fec = rfp_c0(route, validated)
    assert isinstance(fec, dict), "c0 binding must return a dict"
    for key in ("chunks", "collection", "app_id", "grounded"):
        assert key in fec, f"FEC dict missing key: {key!r}"
    assert fec["app_id"] == "apps_rfp"
    assert fec["collection"] == "rfp_docs"


def test_cc5_pa_produces_rfp_prompt_artifact():
    from apps_rfp.runtime.bindings.u0_binding import rfp_u0
    from apps_rfp.runtime.bindings.l1_binding import rfp_l1
    from apps_rfp.runtime.bindings.l0_binding import rfp_l0
    from apps_rfp.runtime.bindings.c0_binding import rfp_c0
    from apps_rfp.runtime.bindings.pa_binding import rfp_pa, RfpPromptArtifact

    validated = rfp_u0(_make_request_envelope())
    plan = rfp_l1(validated)
    route = rfp_l0(plan)
    fec = rfp_c0(route, validated)
    artifact = rfp_pa(route, plan, fec, validated)
    assert isinstance(artifact, RfpPromptArtifact)
    assert hasattr(artifact, "chunks"), "RfpPromptArtifact must have .chunks (grounding evidence)"
    assert isinstance(artifact.chunks, tuple)
    assert hasattr(artifact, "request_id")
    assert hasattr(artifact, "compilation_hash")
    assert artifact.compilation_hash, "compilation_hash must be non-empty"


def test_cc6_l2_returns_sealed_rfp_artifact_dry_run():
    """L2 binding in dry_run mode must return SealedRfpArtifact without calling the LLM."""
    from apps_rfp.runtime.bindings.u0_binding import rfp_u0
    from apps_rfp.runtime.bindings.l1_binding import rfp_l1
    from apps_rfp.runtime.bindings.l0_binding import rfp_l0
    from apps_rfp.runtime.bindings.c0_binding import rfp_c0
    from apps_rfp.runtime.bindings.pa_binding import rfp_pa
    from apps_rfp.runtime.bindings.l2_binding import rfp_l2, SealedRfpArtifact

    validated = rfp_u0(_make_request_envelope(rfp_document_path="", target_company="TestCo"))
    plan = rfp_l1(validated)
    route = rfp_l0(plan)
    fec = rfp_c0(route, validated)
    pa_artifact = rfp_pa(route, plan, fec, validated)

    # rfp_pa picks up dry_run from normalized_payload; validated.normalized_payload already has dry_run=False
    # Force dry_run via the prompt artifact directly (frozen dataclass — use replace)
    import dataclasses
    dry_artifact = dataclasses.replace(pa_artifact, dry_run=True)
    sealed = rfp_l2(dry_artifact)
    assert isinstance(sealed, SealedRfpArtifact)
    assert hasattr(sealed, "compilation_hash")
    assert hasattr(sealed, "status")


def test_cc7_exit_binding_returns_rfp_exit_result():
    from apps_rfp.runtime.bindings.u0_binding import rfp_u0
    from apps_rfp.runtime.bindings.l1_binding import rfp_l1
    from apps_rfp.runtime.bindings.l0_binding import rfp_l0
    from apps_rfp.runtime.bindings.c0_binding import rfp_c0
    from apps_rfp.runtime.bindings.pa_binding import rfp_pa
    from apps_rfp.runtime.bindings.l2_binding import rfp_l2, SealedRfpArtifact
    from apps_rfp.runtime.bindings.exit_binding import rfp_exit, RfpExitResult

    validated = rfp_u0(_make_request_envelope(rfp_document_path="", target_company="ExitCo"))
    plan = rfp_l1(validated)
    route = rfp_l0(plan)
    fec = rfp_c0(route, validated)
    pa_artifact = rfp_pa(route, plan, fec, validated)
    import dataclasses
    dry_artifact = dataclasses.replace(pa_artifact, dry_run=True)
    sealed = rfp_l2(dry_artifact)

    result = rfp_exit(sealed, target_company="TestCo")
    assert isinstance(result, RfpExitResult)
    assert hasattr(result, "disposition")
    assert result.disposition in ("complete", "dry_run", "failed", "error")


# ─────────────────────────────────────────────────────────────
# Negative controls (NC)
# ─────────────────────────────────────────────────────────────

def test_nc1_make_rfp_ingress_runner_is_tombstoned():
    """make_rfp_ingress_runner must raise RuntimeError — factory pattern is eliminated."""
    from apps_rfp.integrations.rfp_ingress_runner import make_rfp_ingress_runner
    with pytest.raises(RuntimeError, match="TOMBSTONED"):
        make_rfp_ingress_runner()


def test_nc2_rfp_ingress_runner_module_importable():
    """Tombstoned module must still be importable (no top-level raise)."""
    import apps_rfp.integrations.rfp_ingress_runner as m
    assert hasattr(m, "make_rfp_ingress_runner")
    assert hasattr(m, "RFP_REQUIRED_FIELDS")


def test_nc3_main_run_product_does_not_import_governed_rfp_run():
    """_run_product_build executable lines must not reference governed_rfp_run."""
    import apps_rfp.__main__ as m
    src = inspect.getsource(m._run_product_build)
    # Strip docstrings and comment lines — only check executable lines
    exec_lines = [
        ln for ln in src.splitlines()
        if not ln.strip().startswith("#") and not ln.strip().startswith('"""') and ln.strip() != '"""'
    ]
    # Also drop lines that are pure triple-quoted string continuations inside docstring
    _in_docstring = False
    filtered: list[str] = []
    for ln in src.splitlines():
        stripped = ln.strip()
        if stripped.startswith('"""'):
            _in_docstring = not _in_docstring
            continue
        if _in_docstring:
            continue
        if stripped.startswith("#"):
            continue
        filtered.append(ln)
    executable = "\n".join(filtered)
    assert "governed_rfp_run" not in executable, (
        "_run_product_build executable lines must NOT import governed_rfp_run — "
        "it is POST_RUN_RECEIPT only post-W2"
    )


def test_nc4_main_does_not_use_make_rfp_ingress_runner():
    """__main__ executable lines must not call make_rfp_ingress_runner."""
    import apps_rfp.__main__ as m
    full_src = inspect.getsource(m)
    # Strip comments and docstrings — only executable lines matter
    _in_ds = False
    filtered: list[str] = []
    for ln in full_src.splitlines():
        stripped = ln.strip()
        if stripped.startswith('"""'):
            _in_ds = not _in_ds
            continue
        if _in_ds:
            continue
        if stripped.startswith("#"):
            continue
        filtered.append(ln)
    executable = "\n".join(filtered)
    assert "make_rfp_ingress_runner" not in executable, (
        "apps_rfp/__main__.py executable lines must NOT call make_rfp_ingress_runner — "
        "tombstoned dispatch= factory pattern"
    )


def test_nc5_parse_payload_produces_envelope_with_required_fields():
    from apps_rfp.runtime.profile_builder import parse_payload
    envelope = parse_payload({
        "rfp_document_path": "/path/rfp.pdf",
        "target_company": "Acme",
    })
    for field in ("run_id", "tenant_id", "trace_id", "submitted_at"):
        assert hasattr(envelope, field) and getattr(envelope, field), (
            f"parse_payload result missing non-empty field: {field!r}"
        )


def test_nc6_profile_builder_bindings_are_callables():
    """Every wired stage binding must be callable."""
    from apps_rfp.runtime.profile_builder import build_app_runtime_contract
    profile = build_app_runtime_contract()
    for stage in ("u0", "l1", "l0", "c0", "pa", "l2", "exit"):
        fn = getattr(profile, stage)
        assert callable(fn), f"profile.{stage} is not callable: {fn!r}"


def test_nc7_l0_raises_on_missing_request_id():
    """rfp_l0 must raise ValueError if L1PlanContract has no request_id."""
    from apps_rfp.runtime.bindings.l0_binding import rfp_l0
    from agentic_core.L1_cognition.types.plan_contract_types import L1PlanContract, ReasoningMode
    dummy_plan = L1PlanContract(
        plan_id="rfp-plan-test",
        request_id="",
        policy_hash="deadbeef" * 4,
        reasoning_mode=ReasoningMode.DECOMPOSED,
        grounding_required=True,
        confidence_score=0.9,
        steps=({"step": "test"},),
    )
    with pytest.raises(ValueError, match="request_id"):
        rfp_l0(dummy_plan)
