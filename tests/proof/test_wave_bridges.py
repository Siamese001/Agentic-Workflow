"""Targeted unit tests for the Wave 1-7 bridges and orchestrators.

Each test validates one module in isolation against its public contract.
Failures here indicate a regression in the new code, independent of the
harness end-to-end run.
"""
from __future__ import annotations

import time

import pytest


# ---------------------------------------------------------------------------
# Wave 1 — U0 -> L1 plan bridge
# ---------------------------------------------------------------------------

def test_wave1_u0_to_l1_plan_bridge_passes_real_validated_request():
    from agentic_core.L0_routing.intake import (
        IntakePipeline,
        IntakePolicy,
        RawIngressEnvelope,
    )
    from agentic_core.L1_cognition.bridges import validated_request_to_plan_contract

    env = RawIngressEnvelope(
        transport="api",
        method="POST",
        content_type="application/json",
        source_channel="test",
        claimed_tenant_id="tA",
        claimed_workspace_id="wA",
        claimed_user_id="u1",
        auth_credential={"kind": "api_key", "token": "t"},
        body_text="hello world",
        request_id_hint="rq-test",
        upstream_traceparent="trace-test",
        region="us",
        declared_modalities=("text",),
    )
    outcome = IntakePipeline(IntakePolicy()).run(env)
    assert outcome.accepted, f"intake rejected: {outcome.rejected}"

    plan = validated_request_to_plan_contract(outcome.validated)
    assert plan.task_spec.startswith("intake.")
    assert plan.query_spec == "user_query"
    assert plan.grounding_required is True
    assert plan.user_task_text == outcome.validated.normalized_payload


def test_wave1_bridge_rejects_misauthorized_validated_request():
    """Defense-in-depth: bridge MUST reject a slip whose authority field was
    forged. We construct a forged stand-in directly (not via
    ValidatedRequest's own __post_init__) since the dataclass itself
    already enforces the same invariant.
    """
    from agentic_core.L1_cognition.bridges import validated_request_to_plan_contract

    class _ForgedVR:
        # Minimal duck-typed stand-in. The bridge inspects only
        # permitted_next_layer + downstream_authority + a few fields.
        permitted_next_layer = "L1"
        downstream_authority = "forged"
        normalized_payload = "x"
        request_shape_class = "api_json"

    with pytest.raises(ValueError, match="downstream_authority"):
        validated_request_to_plan_contract(_ForgedVR())  # type: ignore[arg-type]


def test_wave1_bridge_rejects_wrong_next_layer():
    from agentic_core.L1_cognition.bridges import validated_request_to_plan_contract

    class _Wrong:
        permitted_next_layer = "L0"  # MUST be L1
        downstream_authority = "none"
        normalized_payload = "x"
        request_shape_class = "api_json"

    with pytest.raises(ValueError, match="permitted_next_layer"):
        validated_request_to_plan_contract(_Wrong())  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Wave 2 — V15 -> C0 RouteContract adapter
# ---------------------------------------------------------------------------

def test_wave2_v15_to_c0_route_contract_preserves_hmac():
    from agentic_core.L0_routing.c0_retrieval.verdicts import SourceClass
    from agentic_core.L0_routing.reasoning.v15_route_selector import (
        RouteSignalsV15,
        select_route_v15,
    )
    from agentic_core.L0_routing.reasoning.v15_to_c0_adapter import (
        v15_to_route_contract,
    )
    from agentic_core.L0_routing.types.route_contract_v15 import (
        AuthorityScope,
        CapabilityClass,
        FreshnessClassV15,
        SandboxClass,
        SideEffectClass,
        SupportTargetV15,
        WriteAuthority,
    )

    signals = RouteSignalsV15(
        ingress_ok=True,
        authority=AuthorityScope(
            tenant_scope="tA",
            acl_scope=("reader",),
            region_scope="us",
            capability_class=CapabilityClass.READ_ONLY,
            side_effect_class=SideEffectClass.PURE,
            sandbox_class=SandboxClass.NO_SANDBOX,
            write_authority=WriteAuthority.NONE_UNTIL_UWG,
        ),
        policy_hash="ph",
        blueprint_hash="bp",
        snapshot_id="snap",
        trace_root="tr",
        route_span_id="rs",
        replay_key="rk",
        route_telemetry_event_id="te",
        classifier_confidence=0.8,
        grounding_required=True,
        support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
        freshness_class=FreshnessClassV15.STATIC,
    )
    v15 = select_route_v15(signals).sign(b"test-key")
    assert v15.signatures.hmac_sig != ""

    c0_route = v15_to_route_contract(
        v15,
        allowed_sources=(SourceClass.DOCS,),
    )
    assert c0_route.hmac_sig == v15.signatures.hmac_sig
    assert c0_route.tenant_scope == "tA"
    assert c0_route.region == "us"
    assert "deterministic_route_digest" in c0_route.origin_trust_manifest


def test_wave2_v15_route_id_starts_with_r3_for_grounded_route():
    from agentic_core.L0_routing.reasoning.v15_to_c0_adapter import (
        v15_to_route_contract,
    )
    from agentic_core.L0_routing.reasoning.v15_route_selector import (
        RouteSignalsV15,
        select_route_v15,
    )
    from agentic_core.L0_routing.types.route_contract_v15 import (
        AuthorityScope,
        CapabilityClass,
        FreshnessClassV15,
        SandboxClass,
        SideEffectClass,
        SupportTargetV15,
        WriteAuthority,
    )

    signals = RouteSignalsV15(
        ingress_ok=True,
        authority=AuthorityScope(
            tenant_scope="tA", acl_scope=("reader",), region_scope="us",
            capability_class=CapabilityClass.READ_ONLY,
            side_effect_class=SideEffectClass.PURE,
            sandbox_class=SandboxClass.NO_SANDBOX,
            write_authority=WriteAuthority.NONE_UNTIL_UWG,
        ),
        policy_hash="ph", blueprint_hash="bp", snapshot_id="snap",
        trace_root="tr", route_span_id="rs", replay_key="rk",
        route_telemetry_event_id="te",
        classifier_confidence=0.85,
        grounding_required=True,
        support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
        freshness_class=FreshnessClassV15.STATIC,
    )
    v15 = select_route_v15(signals).sign(b"test-key")
    c0_route = v15_to_route_contract(v15)
    assert c0_route.route_id.startswith("R3_")


# ---------------------------------------------------------------------------
# Wave 6 — BUS_T / BUS_P / BUS_U enforcement
# ---------------------------------------------------------------------------

def test_wave6_bus_t_blocks_current_run_feedback():
    from agentic_core.L6_system_learning.buses import BusT, TelemetryRecord
    from agentic_core.L6_system_learning._base import BusPublishError

    bus = BusT()
    bus.set_current_run("run-1")
    rec = TelemetryRecord(
        run_id="run-1", sealed_at_unix=time.time(),
        trace_id="t", request_id="r", metric_name="m", metric_value=1.0,
    )
    with pytest.raises(BusPublishError, match="current"):
        bus.publish(rec)


def test_wave6_bus_t_accepts_future_run():
    from agentic_core.L6_system_learning.buses import BusT, TelemetryRecord

    bus = BusT()
    bus.set_current_run("run-1")
    bus.publish(TelemetryRecord(
        run_id="run-2", sealed_at_unix=time.time(),
        trace_id="t", request_id="r", metric_name="m", metric_value=1.0,
    ))
    assert bus.count() == 1


def test_wave6_bus_u_default_deny_without_uwg_receipt():
    from agentic_core.L6_system_learning.buses import BusU, PromotionRecord, UWGGateError

    bus = BusU()
    rec = PromotionRecord(
        run_id="run-1", sealed_at_unix=time.time(),
        proposal_id="p1", target_layer="L0",
        target_artifact="x", delta={}, uwg_receipt=None,
    )
    with pytest.raises(UWGGateError, match="missing_uwg_receipt|missing uwg"):
        bus.publish(rec)


def test_wave6_bus_u_accepts_with_valid_receipt():
    from agentic_core.L6_system_learning.buses import (
        BusU,
        PromotionRecord,
        UWGReceipt,
    )

    bus = BusU()
    sealed = time.time()
    rec = PromotionRecord(
        run_id="run-future", sealed_at_unix=sealed,
        proposal_id="p2", target_layer="L0",
        target_artifact="x", delta={"new": 1},
        uwg_receipt=UWGReceipt(
            receipt_id="r1", sealed_run_id="run-future",
            approver_id="approver", approved_at_unix=sealed,
        ),
    )
    bus.publish(rec)
    assert bus.count() == 1


def test_wave6_bus_u_rejects_receipt_run_id_mismatch():
    from agentic_core.L6_system_learning.buses import (
        BusU,
        PromotionRecord,
        UWGGateError,
        UWGReceipt,
    )

    bus = BusU()
    sealed = time.time()
    rec = PromotionRecord(
        run_id="run-A", sealed_at_unix=sealed,
        proposal_id="p3", target_layer="L0",
        target_artifact="x", delta={},
        uwg_receipt=UWGReceipt(
            receipt_id="r2", sealed_run_id="run-B",  # mismatch!
            approver_id="approver", approved_at_unix=sealed,
        ),
    )
    with pytest.raises(UWGGateError, match="does not match"):
        bus.publish(rec)


# ---------------------------------------------------------------------------
# Wave 3 — Prompt Assembly orchestrator
# ---------------------------------------------------------------------------

def test_wave3_assemble_prompt_round_trips_through_pa_pipeline():
    """Smoke: orchestrator runs end-to-end on real C0 + route + plan."""
    from agentic_core.L0_routing.c0_retrieval.dispatcher import run_c0
    from agentic_core.L0_routing.c0_retrieval.candidate_pool import (
        CandidateEvidencePool,
    )
    from agentic_core.prompt_governance.orchestrator import assemble_prompt

    # Use the C0 test factories (already imported by the harness).
    import importlib.util
    import pathlib

    factory_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "agentic_core" / "L0_routing" / "c0_retrieval" / "_factories.py"
    )
    spec = importlib.util.spec_from_file_location("_facs", factory_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    route = mod.make_route()
    plan = mod.make_plan_contract()
    chunk = mod.make_chunk()

    def fetch(p, r):
        return CandidateEvidencePool(
            plan_id=p.plan_id, candidates=(chunk,),
            lanes_used=tuple(chunk.found_by_lanes),
        )

    result = run_c0(
        route=route, plan_contract=plan,
        fetch=fetch, adjacency=lambda nid, allowed: (),
        request_id="rq-pa-test",
    )
    compiled = assemble_prompt(
        final_contract=result.contract,
        route=route, plan=plan,
        request_id="rq-pa-test",
        secret_key=b"test",
    )
    assert compiled.manifest_hash
    assert compiled.hmac_signature
    assert compiled.replay_key
    assert compiled.slot_manifest
    assert compiled.authority_order_proof
    assert "L5_policy" in compiled.authority_order_proof[0]


# ---------------------------------------------------------------------------
# Wave 4 — L2 bounded executor
# ---------------------------------------------------------------------------

def test_wave4_bounded_executor_records_attempt_and_seals():
    from dataclasses import dataclass

    from agentic_core.L2_execution.bounded_executor import (
        ModelInvokeResult,
        execute,
    )

    # Stub a CompiledPromptEnvelope-shaped object with the minimum surface.
    @dataclass(frozen=True)
    class _StubEnv:
        is_dispatchable: bool = True
        dispatch_disposition: str = "PASS"

        @property
        def prompt_budget_report(self) -> dict:
            return {}

        @property
        def replay_metadata(self) -> dict:
            return {}

        @property
        def envelope(self):
            class _E:
                metadata: dict = {}
            return _E()

    def _model(_env):
        return ModelInvokeResult(
            output_text="answer", token_usage=10, model_id="stub", cost_usd=0.0,
        )

    sealed = execute(
        _StubEnv(),
        model_invoke=_model,
        request_id="rq-x", trace_id="tr-x",
        max_attempts=1,
    )
    assert sealed.answer_text == "answer"
    assert sealed.tokens_consumed == 10
    assert sealed.failure is False
    assert sealed.capability_token_id.startswith("cap-")
    assert len(sealed.invocation_records) == 1
    assert sealed.invocation_records[0].model_id == "stub"


def test_wave4_executor_refuses_non_dispatchable_envelope():
    from dataclasses import dataclass

    from agentic_core.L2_execution.bounded_executor import (
        L2ExecutorError,
        ModelInvokeResult,
        execute,
    )

    @dataclass(frozen=True)
    class _Blocked:
        is_dispatchable: bool = False
        dispatch_disposition: str = "BLOCKED_BUDGET"

        @property
        def prompt_budget_report(self) -> dict:
            return {}

        @property
        def replay_metadata(self) -> dict:
            return {}

        @property
        def envelope(self):
            class _E:
                metadata: dict = {}
            return _E()

    def _model(_env):
        return ModelInvokeResult(output_text="x", token_usage=1)

    with pytest.raises(L2ExecutorError, match="not dispatchable"):
        execute(_Blocked(), model_invoke=_model,
                request_id="r", trace_id="t")
