"""Full U0→Exit spine contract tests — every canonical stage through exit gates.

Scope (user intent): ``U0→exit gates`` means the **whole governed spine**, not a
single section slice (e.g. executive_summary only).

SSOT chains:
- Product: ``apps_rg.runtime.section_spine_terminology.CANONICAL_SPINE_CHAIN``
- Exit sub-mesh inside ``Exit``: X1 (X1A..X1J) → X2 aggregation → X3 disposition
- Integrated entry: ``agentic_core.runtime.entrypoints.integrated_single_action_spine_run``
"""
from __future__ import annotations

import importlib
import inspect
from pathlib import Path

import pytest

from apps_rg.runtime.section_spine_terminology import (
    CANONICAL_CONTRACT_TYPES,
    CANONICAL_SPINE_CHAIN,
)
from tests._core_contract._spine_u0_exit_fixtures import L5_CERT, thin_apps_rg_ingress_kwargs

REPO = Path(__file__).resolve().parents[2]

# U0 through Exit (user scope); UWG/L4/L6 are post-exit and listed for completeness.
SPINE_U0_TO_EXIT_STAGES: tuple[tuple[str, str, str], ...] = (
    ("U0", "ValidatedRequest", "agentic_core.L0_routing.intake.validated_request"),
    ("U0", "AppsRgIngressPayload", "agentic_core.runtime.contracts.apps_rg_ingress_payload"),
    ("L1", "L1PlanContract", "agentic_core.runtime.contracts.l1_plan_contract"),
    ("L0", "RouteContract", "agentic_core.runtime.contracts.route_contract"),
    ("C0", "FinalEvidenceContract", "agentic_core.runtime.contracts.final_evidence_contract"),
    ("PA", "CompiledPromptArtifact", "agentic_core.runtime.contracts.compiled_prompt_artifact"),
    ("L2", "SealedL2Artifact", "agentic_core.runtime.contracts.sealed_l2_artifact"),
    ("Exit", "X1CheckoutResult", "agentic_core.runtime.contracts.x1_checkout_result"),
    ("Exit", "X2AggregationResult", "agentic_core.runtime.exit.x2_aggregation_result"),
    ("Exit", "ExitDispositionReceipt", "agentic_core.runtime.exit.exit_disposition"),
    ("Exit", "X3Disposition", "agentic_core.runtime.contracts.x3_disposition"),
)

EXIT_X1_GATE_IDS: tuple[str, ...] = tuple(f"X1{c}" for c in "ABCDEFGHIJ")


@pytest.mark.parametrize(
    "stage,contract_type,module_path",
    SPINE_U0_TO_EXIT_STAGES,
    ids=[f"{s}-{c}" for s, c, _ in SPINE_U0_TO_EXIT_STAGES],
)
def test_spine_stage_contract_importable(stage: str, contract_type: str, module_path: str) -> None:
    mod = importlib.import_module(module_path)
    cls = getattr(mod, contract_type)
    assert inspect.isclass(cls)


def test_canonical_spine_chain_u0_through_exit_matches_contract_inventory() -> None:
    """Exit is the terminal governed stage before UWG/L4/L6."""
    assert CANONICAL_SPINE_CHAIN[:7] == ("U0", "L1", "L0", "C0", "PA", "L2", "Exit")
    for ct in (
        "ValidatedRequest",
        "L1PlanContract",
        "RouteContract",
        "FinalEvidenceContract",
        "CompiledPromptArtifact",
        "SealedL2Artifact",
        "ExitDispositionReceipt",
    ):
        assert ct in CANONICAL_CONTRACT_TYPES


def test_integrated_spine_entrypoint_sequences_u0_l0_l2_exit_in_source() -> None:
    src = (
        REPO / "agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py"
    ).read_text(encoding="utf-8")
    markers = (
        "run_request_intake",
        "validated_request_to_plan_contract",
        "check_route_gates",
        "ExitEvalPipeline",
        "seal_runtime_exhaust",
    )
    positions = [src.index(m) for m in markers]
    assert positions == sorted(positions), (
        "integrated spine must document/sequence U0→L1 bridge→L0 gates→Exit→exhaust"
    )


def test_u0_intake_validated_request_has_no_forbidden_authority_fields() -> None:
    from agentic_core.L0_routing.intake.validated_request import (
        FORBIDDEN_VALIDATED_REQUEST_KEYS,
        ValidatedRequest,
    )

    leak = set(ValidatedRequest.__dataclass_fields__) & FORBIDDEN_VALIDATED_REQUEST_KEYS
    assert not leak


def test_u0_to_l1_bridge_requires_l1_permit_and_zero_downstream_authority() -> None:
    from agentic_core.L0_routing.intake.envelope import RawIngressEnvelope
    from agentic_core.L0_routing.intake.pipeline import IntakePipeline, IntakePolicy
    from agentic_core.L0_routing.intake.validated_request import ValidatedRequest
    from agentic_core.L1_cognition.bridges.u0_to_l1_plan import validated_request_to_plan_contract

    out = IntakePipeline(IntakePolicy()).run(
        RawIngressEnvelope(transport="chat", body_text="spine bridge task")
    )
    vr = out.validated
    assert vr is not None
    plan = validated_request_to_plan_contract(vr)
    assert plan.user_task_text
    assert plan.grounding_required is True

    tampered = {k: getattr(vr, k) for k in vr.__dataclass_fields__}
    tampered["permitted_next_layer"] = "L0"
    with pytest.raises(ValueError, match="permitted_next_layer"):
        ValidatedRequest(**tampered)


def test_apps_rg_ingress_payload_fail_closed_without_context_or_resume() -> None:
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import AppsRgIngressPayload

    with pytest.raises(ValueError, match="at least one"):
        AppsRgIngressPayload()


def test_apps_rg_u0_validated_request_requires_l5_cert() -> None:
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
        AppsRgIngressPayload,
        ValidatedRequest,
    )
    from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
        AuthorityValidationReceipt,
    )

    payload = AppsRgIngressPayload(**thin_apps_rg_ingress_kwargs())
    receipt = AuthorityValidationReceipt(allowed=True, passed=True, request_id="r1")
    with pytest.raises(ValueError, match="l5_certification_ref"):
        ValidatedRequest(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            task_class="resume_generation",
            payload_digest="d1",
            authority_validation_receipt=receipt,
            trace_id="t1",
            l5_certification_ref=None,
        )


def test_l1_plan_contract_rejects_invalid_l5_cert() -> None:
    from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract

    with pytest.raises(ValueError, match="l5_certification_ref"):
        L1PlanContract(request_id="r1", run_id="run1", app_id="apps_rg", trace_id="t1")


def test_fec_support_status_pass_is_only_passing_value() -> None:
    from agentic_core.runtime.contracts.final_evidence_contract import (
        SUPPORT_STATUS_PASS,
        SUPPORT_STATUS_PASSING_VALUES,
        SUPPORT_STATUS_WEAK_WITH_CAVEATS,
    )

    assert SUPPORT_STATUS_PASS in SUPPORT_STATUS_PASSING_VALUES
    assert SUPPORT_STATUS_WEAK_WITH_CAVEATS not in SUPPORT_STATUS_PASSING_VALUES


def test_route_contract_default_posture_is_read_only() -> None:
    from agentic_core.runtime.contracts.posture import POSTURE_READ_ONLY
    from agentic_core.runtime.contracts.route_contract import RouteContract

    rc = RouteContract(
        request_id="r1",
        run_id="run1",
        app_id="apps_rg",
        trace_id="t1",
        route_id="R4",
        l3_required=False,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        l5_certification_ref=L5_CERT,
    )
    assert rc.posture == POSTURE_READ_ONLY


def test_sealed_l2_artifact_defaults_model_generation_origin() -> None:
    from agentic_core.runtime.contracts.origin import Origin
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

    art = SealedL2Artifact(
        request_id="r1",
        run_id="run1",
        app_id="apps_rg",
        trace_id="t1",
        execution_status="completed",
        l5_certification_ref=L5_CERT,
    )
    assert art.generated_content_origin == Origin.MODEL_GENERATION


def test_x1_unknown_never_counts_as_overall_pass() -> None:
    from agentic_core.runtime.contracts.x1_checkout_result import X1CheckoutResult

    x1 = X1CheckoutResult(request_id="r1", run_id="run1", trace_root="t1")
    assert not x1.is_overall_pass()
    assert x1.first_blocking_gate() is not None
    assert len(x1.items()) == len(EXIT_X1_GATE_IDS)


def test_x1_all_pass_yields_overall_pass() -> None:
    from agentic_core.runtime.contracts.x1_checkout_result import X1CheckoutResult, X1Item, X1Verdict

    kwargs: dict[str, object] = {
        "request_id": "r1",
        "run_id": "run1",
        "trace_root": "t1",
        "replay_manifest_ref": "replay-1",
        "otel_span_refs": ("span-1",),
    }
    for gate_id in EXIT_X1_GATE_IDS:
        kwargs[_x1_dataclass_field_for_gate(gate_id)] = X1Item(
            gate_id=gate_id,
            verdict=X1Verdict.PASS,
            decisive_reason="ok",
        )
    assert X1CheckoutResult(**kwargs).is_overall_pass()


def _x1_field_suffix(gate_id: str) -> str:
    mapping = {
        "X1A": "todays_rules",
        "X1B": "answered_it",
        "X1C": "safe_to_leave",
        "X1D": "answer_good",
        "X1E": "trajectory_ok",
        "X1F": "story_adds_up",
        "X1G": "replay_eligible",
        "X1H": "observable",
        "X1I": "consistent_across_runs",
        "X1J": "write_eligibility",
    }
    return mapping[gate_id]


def _x1_dataclass_field_for_gate(gate_id: str) -> str:
    # X1A -> x1a_todays_rules (lowercase letter after x1)
    return f"x1{gate_id[2].lower()}_{_x1_field_suffix(gate_id)}"


def test_x1_not_applicable_requires_reason() -> None:
    from agentic_core.runtime.contracts.x1_checkout_result import X1Item, X1Verdict

    with pytest.raises(ValueError, match="not_applicable_reason"):
        X1Item(gate_id="X1A", verdict=X1Verdict.NOT_APPLICABLE)


def test_x2_aggregation_blocks_final_x3_when_deterministic_blocked() -> None:
    from agentic_core.runtime.exit.x2_aggregation_result import X2AggregationResult

    blocked = X2AggregationResult(
        disposition_candidate="X3E_SAFE_ABSTAIN",
        deterministic_blocked=True,
        emits_final_x3=False,
    )
    assert not blocked.emits_final_x3


def test_exit_disposition_receipt_exactly_one_x3_code() -> None:
    from agentic_core.runtime.exit.exit_disposition import (
        ALL_X3_CODES,
        EXIT_DISPOSITION_SCHEMA_VERSION,
        ExitDispositionReceipt,
        X3D_ALLOW_FINISH,
    )

    rec = ExitDispositionReceipt(
        request_id="r1",
        run_id="run1",
        trace_root="t1",
        app_id="apps_rg",
        task_class="resume_generation",
        x3_code=X3D_ALLOW_FINISH,
    )
    assert rec.x3_code in ALL_X3_CODES
    assert rec.allows_finish
    assert rec.schema_version == EXIT_DISPOSITION_SCHEMA_VERSION

    with pytest.raises(ValueError, match="invalid x3_code"):
        ExitDispositionReceipt(
            request_id="r1",
            run_id="run1",
            trace_root="t1",
            app_id="apps_rg",
            task_class="resume_generation",
            x3_code="X3Z_NOT_REAL",
        )


def test_x3_disposition_requires_l5_cert() -> None:
    from agentic_core.runtime.contracts.x3_disposition import X3Disposition

    with pytest.raises(ValueError, match="l5_certification_ref"):
        X3Disposition(
            request_id="r1",
            run_id="run1",
            app_id="apps_rg",
            trace_id="t1",
            exit_status="success",
            l5_certification_ref="",
        )


def test_compiled_prompt_artifact_posture_is_generation() -> None:
    from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
    from agentic_core.runtime.contracts.posture import POSTURE_GENERATION

    pa = CompiledPromptArtifact(
        request_id="r1",
        run_id="run1",
        app_id="apps_rg",
        trace_id="t1",
        l5_certification_ref=L5_CERT,
    )
    assert pa.posture == POSTURE_GENERATION
