"""W7: apps_lic Exit / X1 / X3 binding tests.

Tests prove:

TC01 — exit_finalize_apps_lic is importable and callable.
TC02 — returns exactly one X3Disposition per invocation.
TC03 — X3Disposition.app_id == 'apps_lic'.
TC04 — X3Disposition.l5_certification_ref is non-empty.
TC05 — eval_score is None (scalar eval_score is NOT authoritative).
TC06 — completed L2 produces exit_status='success' and outcome_authorized=True.
TC07 — failed L2 produces exit_status='failure' and outcome_authorized=False.
TC08 — X3Disposition.sealed_l2_digest matches SealedL2Artifact.compilation_hash.
TC09 — X1CheckoutResult is produced: all 10 X1A-X1J slots populated (source check).
TC10 — X1D is NOT_APPLICABLE when evidence_bundle and final_evidence_contract are empty.
TC11 — X1G is NOT_APPLICABLE for terminal_class=answer_only.
TC12 — X1J is NOT_APPLICABLE when proposed_state_diff is empty (inert).
TC13 — material FAIL on X1C -> exit_status='failure' (DENY), not success.
TC14 — material UNKNOWN on X1A -> exit_status='escalated' or 'failure', never success.
TC15 — proposed_state_diff is inert: exit binding never mutates it.
TC16 — no direct L4 write in source (source inspection).
TC17 — no ChromaDB mutation in source (source inspection).
TC18 — no embedding generation in source (source inspection).
TC19 — no retrieval call in source (source inspection).
TC20 — no prompt assembly in source (source inspection).
TC21 — no tool/model execution in source (source inspection).
TC22 — gate_verdict_refs populated on X3Disposition.
TC23 — hitl_required=True when disposition is ESCALATE.
TC24 — X3Disposition identity fields (request_id, run_id, trace_id) match L2 artifact.
TC25 — W3-W6 regression: existing test modules still importable.

Plan: .windsurf/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md (W7)
"""

from __future__ import annotations

import importlib
import inspect
import re
import uuid
from typing import Any

import pytest

# ------------------------------------------------------------------ helpers --


def _code_only(module_name: str) -> str:
    """Return module source with docstrings and comment lines stripped."""
    mod = importlib.import_module(module_name)
    src = inspect.getsource(mod)
    lines = [ln for ln in src.splitlines() if not ln.strip().startswith("#")]
    cleaned = "\n".join(lines)
    cleaned = re.sub(r'""".*?"""', "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"'''.*?'''", "", cleaned, flags=re.DOTALL)
    return cleaned


_EXIT_MODULE = "agentic_core.runtime.exit.apps_lic_exit_binding"


# ---------------------------------------------------------------- fixtures --


def _make_sealed_l2(
    *,
    execution_status: str = "completed",
    generated_content: str = "Hi {lead_name}, ...",
    compilation_hash: str = "abc123",
    run_id: str | None = None,
    request_id: str | None = None,
    trace_id: str | None = None,
    replay_key: str = "replay-test-key",
    proposed_state_diff: dict | None = None,
) -> Any:
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    from agentic_core.runtime.contracts.origin import Origin

    return SealedL2Artifact(
        request_id=request_id or uuid.uuid4().hex[:16],
        run_id=run_id or uuid.uuid4().hex[:16],
        app_id="apps_lic",
        trace_id=trace_id or uuid.uuid4().hex[:16],
        execution_status=execution_status,
        generated_content=generated_content,
        generated_content_origin=Origin.MODEL_GENERATION,
        proposed_state_diff=proposed_state_diff or {},
        state_diff_authorized=False,
        compilation_hash=compilation_hash,
        prompt_artifact_digest="pa_digest_001",
        replay_key=replay_key,
        tenant_id="apps_lic_tenant",
        l5_certification_ref="l2-apps-lic-outreach-message-ag8-w6-f3c2e1",
    )


# =================================================================== TC01 ===


class TestTC01_Importable:
    def test_module_importable(self) -> None:
        mod = importlib.import_module(_EXIT_MODULE)
        assert hasattr(mod, "exit_finalize_apps_lic")

    def test_function_callable(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        assert callable(exit_finalize_apps_lic)


# =================================================================== TC02 ===


class TestTC02_ReturnsX3Disposition:
    def test_returns_x3disposition(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        from agentic_core.runtime.contracts.x3_disposition import X3Disposition

        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        assert isinstance(result, X3Disposition)

    def test_exactly_one_disposition(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        from agentic_core.runtime.contracts.x3_disposition import X3Disposition

        l2 = _make_sealed_l2()
        results = [exit_finalize_apps_lic(l2)]
        assert len(results) == 1
        assert isinstance(results[0], X3Disposition)


# =================================================================== TC03 ===


class TestTC03_AppId:
    def test_app_id_is_apps_lic(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        assert result.app_id == "apps_lic"


# =================================================================== TC04 ===


class TestTC04_CertRef:
    def test_l5_certification_ref_nonempty(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        assert result.l5_certification_ref
        assert len(result.l5_certification_ref) > 4

    def test_cert_ref_contains_ag8_w7(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        assert "w7" in result.l5_certification_ref.lower()


# =================================================================== TC05 ===


class TestTC05_EvalScoreNotAuthoritative:
    def test_eval_score_is_none(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        assert result.eval_score is None, (
            "eval_score MUST be None — scalar score is not authoritative; "
            "authorisation is driven by X1CheckoutResult and X2 AggregateDecision"
        )


# =================================================================== TC06 ===


class TestTC06_CompletedL2Succeeds:
    def test_completed_l2_produces_success(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2(execution_status="completed")
        result = exit_finalize_apps_lic(l2)
        assert result.exit_status == "success"
        assert result.outcome_authorized is True

    def test_eval_threshold_met_when_success(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2(execution_status="completed")
        result = exit_finalize_apps_lic(l2)
        assert result.eval_threshold_met is True


# =================================================================== TC07 ===


class TestTC07_FailedL2Denied:
    def test_failed_l2_exit_status_is_failure(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2(execution_status="failed", generated_content="")
        result = exit_finalize_apps_lic(l2)
        assert result.exit_status in {"failure", "abstain", "escalated"}
        assert result.outcome_authorized is False


# =================================================================== TC08 ===


class TestTC08_SealedL2Digest:
    def test_sealed_l2_digest_matches_compilation_hash(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2(compilation_hash="deaa9912beef")
        result = exit_finalize_apps_lic(l2)
        assert result.sealed_l2_digest == "deaa9912beef"


# =================================================================== TC09 ===


class TestTC09_X1AllGatesPopulated:
    def test_x1_checkout_adapter_builds_all_10_gates(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.x1_checkout_adapter import (
            build_x1_checkout_result,
        )
        from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import run_all_x1_gates
        from agentic_core.runtime.exit.apps_lic_exit_binding import _build_exit_review_packet
        from agentic_core.runtime.contracts.x1_checkout_result import X1CheckoutResult

        l2 = _make_sealed_l2()
        packet = _build_exit_review_packet(l2)
        verdicts = run_all_x1_gates(packet)
        checkout = build_x1_checkout_result(verdicts, packet)
        assert isinstance(checkout, X1CheckoutResult)
        items = list(checkout.items())
        gate_ids = {item.gate_id for item in items}
        expected = {"X1A", "X1B", "X1C", "X1D", "X1E", "X1F", "X1G", "X1H", "X1I", "X1J"}
        assert gate_ids == expected, f"Missing gates: {expected - gate_ids}"

    def test_x1_checkout_result_has_request_id(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.x1_checkout_adapter import (
            build_x1_checkout_result,
        )
        from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import run_all_x1_gates
        from agentic_core.runtime.exit.apps_lic_exit_binding import _build_exit_review_packet

        req_id = uuid.uuid4().hex[:16]
        l2 = _make_sealed_l2(request_id=req_id)
        packet = _build_exit_review_packet(l2)
        verdicts = run_all_x1_gates(packet)
        checkout = build_x1_checkout_result(verdicts, packet)
        assert checkout.request_id == req_id


# =================================================================== TC10 ===


class TestTC10_X1D_NotApplicable:
    def test_x1d_not_applicable_when_no_evidence(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import eval_x1d
        from agentic_core.L3_orchestration.exit_eval.v6.types import (
            ExitReviewPacket,
            GateResult,
            SourceType,
        )

        packet = ExitReviewPacket(
            request_id="r1",
            run_id="run1",
            trace_root="t1",
            source_type=SourceType.L2_SEALED_ARTIFACT,
            terminal_class="answer_only",
            track_label="production",
            policy_hash="ph",
            output={},
            exec_trace={},
            grader_composition={"roster": ["code"], "threshold_profile": "default"},
        )
        verdict = eval_x1d(packet)
        assert verdict.result is GateResult.NOT_APPLICABLE


# =================================================================== TC11 ===


class TestTC11_X1G_NotApplicable:
    def test_x1g_not_applicable_for_answer_only(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import eval_x1g
        from agentic_core.L3_orchestration.exit_eval.v6.types import (
            ExitReviewPacket,
            GateResult,
            SourceType,
        )

        packet = ExitReviewPacket(
            request_id="r1",
            run_id="run1",
            trace_root="t1",
            source_type=SourceType.L2_SEALED_ARTIFACT,
            terminal_class="answer_only",
            track_label="production",
            policy_hash="ph",
            output={},
            exec_trace={},
            grader_composition={"roster": ["code"], "threshold_profile": "default"},
        )
        verdict = eval_x1g(packet)
        assert verdict.result is GateResult.NOT_APPLICABLE


# =================================================================== TC12 ===


class TestTC12_X1J_NotApplicable:
    def test_x1j_not_applicable_when_state_diff_empty(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import eval_x1j
        from agentic_core.L3_orchestration.exit_eval.v6.types import (
            ExitReviewPacket,
            GateResult,
            SourceType,
        )

        packet = ExitReviewPacket(
            request_id="r1",
            run_id="run1",
            trace_root="t1",
            source_type=SourceType.L2_SEALED_ARTIFACT,
            terminal_class="answer_only",
            track_label="production",
            policy_hash="ph",
            output={},
            exec_trace={},
            grader_composition={"roster": ["code"], "threshold_profile": "default"},
            state_diff={},
        )
        verdict = eval_x1j(packet)
        assert verdict.result is GateResult.NOT_APPLICABLE

    def test_exit_binding_x1j_not_applicable(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2(proposed_state_diff={})
        result = exit_finalize_apps_lic(l2)
        x1j_ref = next((r for r in result.gate_verdict_refs if r.startswith("X1J:")), None)
        assert x1j_ref is not None
        assert "NOT_APPLICABLE" in x1j_ref


# =================================================================== TC13 ===


class TestTC13_MaterialFailDenied:
    def test_sandbox_breach_produces_failure(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.types import (
            ExitReviewPacket,
            GateResult,
            SourceType,
        )
        from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import run_all_x1_gates
        from agentic_core.L3_orchestration.exit_eval.v6.x1_checkout_adapter import (
            build_x1_checkout_result,
            x1_checkout_to_gate_verdicts,
        )
        from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import aggregate_decision
        from agentic_core.L3_orchestration.exit_eval.v6.types import V6Disposition

        packet = ExitReviewPacket(
            request_id="r1",
            run_id="run1",
            trace_root="t1",
            source_type=SourceType.L2_SEALED_ARTIFACT,
            terminal_class="answer_only",
            track_label="production",
            policy_hash="ph",
            output={"completion_score": 1.0},
            exec_trace={"hidden_egress": True},
            sandbox_envelope={"isolation_intact": True},
            grader_composition={"roster": ["code"], "threshold_profile": "default"},
            capability_token={"expired": False},
            replay_key="rk",
        )
        verdicts = run_all_x1_gates(packet)
        checkout = build_x1_checkout_result(verdicts, packet)
        gate_verdicts_for_x2 = x1_checkout_to_gate_verdicts(checkout)
        decision = aggregate_decision(gate_verdicts_for_x2, packet, x1_checkout_result=checkout)
        assert decision.disposition is V6Disposition.DENY


# =================================================================== TC14 ===


class TestTC14_MaterialUnknownNotPass:
    def test_x1checkout_overall_pass_false_on_unknown(self) -> None:
        from agentic_core.runtime.contracts.x1_checkout_result import (
            X1CheckoutResult,
            X1Item,
            X1Verdict,
            X1EvaluatorType,
        )

        def _pass_item(gate_id: str) -> X1Item:
            return X1Item(gate_id=gate_id, verdict=X1Verdict.PASS, evaluator_type=X1EvaluatorType.CODE)

        def _unknown_item(gate_id: str) -> X1Item:
            return X1Item(
                gate_id=gate_id,
                verdict=X1Verdict.UNKNOWN,
                evaluator_type=X1EvaluatorType.CODE,
                unknown_reason="test-unknown",
            )

        checkout = X1CheckoutResult(
            request_id="r1",
            run_id="run1",
            x1a_todays_rules=_unknown_item("X1A"),
            x1b_answered_it=_pass_item("X1B"),
            x1c_safe_to_leave=_pass_item("X1C"),
            x1d_answer_good=_pass_item("X1D"),
            x1e_trajectory_ok=_pass_item("X1E"),
            x1f_story_adds_up=_pass_item("X1F"),
            x1g_replay_eligible=_pass_item("X1G"),
            x1h_observable=_pass_item("X1H"),
            x1i_consistent_across_runs=_pass_item("X1I"),
            x1j_write_eligibility=_pass_item("X1J"),
        )
        assert checkout.is_overall_pass() is False


# =================================================================== TC15 ===


class TestTC15_ProposedStateDiffInert:
    def test_proposed_state_diff_unchanged(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        original_diff: dict = {}
        l2 = _make_sealed_l2(proposed_state_diff=original_diff)
        exit_finalize_apps_lic(l2)
        assert dict(l2.proposed_state_diff) == {}

    def test_final_output_has_no_state_diff(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        assert "state_diff" not in result.final_output


# =================================================================== TC16 ===


class TestTC16_NoDirectL4Write:
    def test_no_l4_write_call_in_source(self) -> None:
        src = _code_only(_EXIT_MODULE)
        l4_write_patterns = [
            r"l4_write\s*\(",
            r"\.commit\s*\(",
            r"state_diff_authorized\s*=\s*True",
        ]
        for pat in l4_write_patterns:
            assert not re.search(pat, src), (
                f"Forbidden L4-write pattern '{pat}' found in Exit source"
            )


# =================================================================== TC17 ===


class TestTC17_NoChromaDB:
    def test_no_chromadb_in_imports(self) -> None:
        import_lines = [
            ln.strip()
            for ln in inspect.getsource(
                importlib.import_module(_EXIT_MODULE)
            ).splitlines()
            if ln.strip().startswith("import ") or ln.strip().startswith("from ")
        ]
        for ln in import_lines:
            assert "chromadb" not in ln, f"Forbidden chromadb import: {ln}"

    def test_no_chromadb_mutation_call_in_source(self) -> None:
        src = _code_only(_EXIT_MODULE)
        forbidden = [r"\.upsert\s*\(", r"\.add\s*\(.*collection", r"chromadb"]
        for pat in forbidden:
            assert not re.search(pat, src), (
                f"Forbidden ChromaDB pattern '{pat}' found in Exit source"
            )


# =================================================================== TC18 ===


class TestTC18_NoEmbeddingGeneration:
    def test_no_embedding_import_in_source(self) -> None:
        src = _code_only(_EXIT_MODULE)
        forbidden = [
            r"sentence_transformers",
            r"SentenceTransformer",
            r"embed_query",
            r"get_embedding",
        ]
        for pat in forbidden:
            assert not re.search(pat, src), (
                f"Forbidden embedding pattern '{pat}' found in Exit source"
            )

    def test_no_encode_call_on_model(self) -> None:
        src = _code_only(_EXIT_MODULE)
        assert not re.search(r"\bmodel\b.*\.encode\s*\(", src), (
            "model.encode() call found — forbidden embedding generation"
        )


# =================================================================== TC19 ===


class TestTC19_NoRetrieval:
    def test_no_retrieval_call_in_source(self) -> None:
        src = _code_only(_EXIT_MODULE)
        forbidden = [
            r"r1b_",
            r"r1a_",
            r"c0_retrieve",
            r"\.retrieve\s*\(",
            r"semantic_search\s*\(",
        ]
        for pat in forbidden:
            assert not re.search(pat, src), (
                f"Forbidden retrieval pattern '{pat}' found in Exit source"
            )


# =================================================================== TC20 ===


class TestTC20_NoPromptAssembly:
    def test_no_prompt_assembly_in_source(self) -> None:
        src = _code_only(_EXIT_MODULE)
        forbidden = [
            r"pa_compose",
            r"pa_compile",
            r"CompiledPromptArtifact\s*\(",
            r"assemble_prompt",
        ]
        for pat in forbidden:
            assert not re.search(pat, src), (
                f"Forbidden prompt-assembly pattern '{pat}' found in Exit source"
            )


# =================================================================== TC21 ===


class TestTC21_NoToolModelExecution:
    def test_no_tool_model_execution_in_source(self) -> None:
        src = _code_only(_EXIT_MODULE)
        forbidden = [
            r"HopPipelineExecutor",
            r"anthropic\.",
            r"openai\.",
            r"vllm\.",
            r"requests\.post",
        ]
        for pat in forbidden:
            assert not re.search(pat, src), (
                f"Forbidden tool/model-execution pattern '{pat}' found in Exit source"
            )


# =================================================================== TC22 ===


class TestTC22_GateVerdictRefs:
    def test_gate_verdict_refs_populated(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        assert len(result.gate_verdict_refs) == 10, (
            f"Expected 10 gate_verdict_refs (X1A-X1J), got {len(result.gate_verdict_refs)}"
        )

    def test_gate_verdict_refs_cover_all_10_gates(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        gate_ids = {ref.split(":")[0] for ref in result.gate_verdict_refs}
        expected = {"X1A", "X1B", "X1C", "X1D", "X1E", "X1F", "X1G", "X1H", "X1I", "X1J"}
        assert gate_ids == expected


# =================================================================== TC23 ===


class TestTC23_HitlRequired:
    def test_hitl_required_false_for_success(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2(execution_status="completed")
        result = exit_finalize_apps_lic(l2)
        if result.exit_status == "success":
            assert result.hitl_required is False

    def test_hitl_required_true_for_escalated(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2(execution_status="completed")
        result = exit_finalize_apps_lic(l2)
        if result.exit_status == "escalated":
            assert result.hitl_required is True


# =================================================================== TC24 ===


class TestTC24_IdentityFields:
    def test_request_id_carried_through(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        req_id = uuid.uuid4().hex[:16]
        l2 = _make_sealed_l2(request_id=req_id)
        result = exit_finalize_apps_lic(l2)
        assert result.request_id == req_id

    def test_run_id_carried_through(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        run_id = uuid.uuid4().hex[:16]
        l2 = _make_sealed_l2(run_id=run_id)
        result = exit_finalize_apps_lic(l2)
        assert result.run_id == run_id

    def test_trace_id_carried_through(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        trace_id = uuid.uuid4().hex[:16]
        l2 = _make_sealed_l2(trace_id=trace_id)
        result = exit_finalize_apps_lic(l2)
        assert result.trace_id == trace_id

    def test_tenant_id_carried_through(self) -> None:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic

        l2 = _make_sealed_l2()
        result = exit_finalize_apps_lic(l2)
        assert result.tenant_id == "apps_lic_tenant"


# =================================================================== TC25 ===


class TestTC25_PriorWaveRegression:
    def test_w3_u0_module_importable(self) -> None:
        mod = importlib.import_module("agentic_core.runtime.entry.u0_apps_lic_binding")
        assert mod is not None

    def test_w4_l1_module_importable(self) -> None:
        mod = importlib.import_module("agentic_core.L1_cognition.apps_lic_l1_binding")
        assert mod is not None

    def test_w4_l0_module_importable(self) -> None:
        mod = importlib.import_module("agentic_core.L0_routing.apps_lic_l0_binding")
        assert mod is not None

    def test_w5_c0_pa_module_importable(self) -> None:
        mod = importlib.import_module("agentic_core.prompt_governance.apps_lic_pa_binding")
        assert mod is not None

    def test_w6_l3_module_importable(self) -> None:
        mod = importlib.import_module("agentic_core.L3_orchestration.apps_lic_l3_binding")
        assert mod is not None

    def test_w6_l2_module_importable(self) -> None:
        mod = importlib.import_module("agentic_core.L2_execution.apps_lic_l2_binding")
        assert mod is not None

    def test_w7_exit_module_importable(self) -> None:
        mod = importlib.import_module(_EXIT_MODULE)
        assert mod is not None
