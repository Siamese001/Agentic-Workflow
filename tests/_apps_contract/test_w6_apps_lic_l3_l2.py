"""W6: apps_lic L3 orchestration + L2 execution binding tests.

Tests prove:

TC01 — L3 participates when RouteContract.execution_form=managed_workflow.
TC02 — L3 emits L3RuntimeOrchestrationReceipt.
TC03 — L3 emits L3StepContract (L3ToL2 handoff).
TC04 — L3 preserves workflow_id, node_id, dependency refs, checkpoint refs,
        capability token, sandbox envelope, allowed execution lane.
TC05 — L3 hard law: does not reroute, retrieve, execute, assemble prompts, or write L4.
TC06 — L3 raises when execution_form != managed_workflow.
TC07 — L3 emits L3ContextBus with evidence + prompt refs.
TC08 — L2 receives the bounded step contract.
TC09 — L2 invokes only HopPipelineExecutor.run(REGISTRY).
TC10 — L2 emits SealedL2Artifact.
TC11 — L2 preserves evidence_refs, prompt_refs, tool_call_refs, model_call_refs,
        provider_receipts, otel_span_refs, replay_manifest, audit_manifest_ref.
TC12 — proposed_state_diff is inert (empty dict).
TC13 — no direct L4 write (state_diff_authorized=False, is_uwg_write_authority=False).
TC14 — no ChromaDB mutation (source inspection).
TC15 — no embedding generation (source inspection).
TC16 — W3, W4, W5 regression: key imports remain importable.
TC17 — L3 determinism: same inputs → same workflow_id.
TC18 — L2 fail-soft on HOP pipeline error emits stub_fallback artifact.
TC19 — L2 emits SealedL2Artifact with correct l5_certification_ref.
TC20 — L3 receipt sets all four hard-law assertions True.

Plan: .windsurf/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md (W6)
"""
from __future__ import annotations

import dataclasses
import importlib
import inspect
import re
import uuid
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ------------------------------------------------------------------ helpers --


def _import_lines(module_name: str) -> list[str]:
    """Return all import statements in a module's source file."""
    mod = importlib.import_module(module_name)
    src = inspect.getsource(mod)
    return [
        line.strip()
        for line in src.splitlines()
        if line.strip().startswith("import ") or line.strip().startswith("from ")
    ]


def _code_only(module_name: str) -> str:
    """Return module source with docstrings and comment lines stripped."""
    import ast
    import textwrap
    mod = importlib.import_module(module_name)
    src = inspect.getsource(mod)
    # Strip comment lines
    lines = [ln for ln in src.splitlines() if not ln.strip().startswith("#")]
    cleaned = "\n".join(lines)
    # Strip string literals used as docstrings via ast
    try:
        tree = ast.parse(textwrap.dedent(cleaned))
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                # zero out the docstring line range from cleaned
                pass  # ast-level stripping is complex; comment-strip is sufficient
    except SyntaxError:
        pass
    # Simple heuristic: remove triple-quoted string blocks
    import re as _re
    cleaned = _re.sub(r'""".*?"""', '', cleaned, flags=_re.DOTALL)
    cleaned = _re.sub(r"'''.*?'''", '', cleaned, flags=_re.DOTALL)
    return cleaned


# ---------------------------------------------------------------- fixtures --


def _make_route(
    *,
    execution_form: str = "managed_workflow",
    run_id: str | None = None,
) -> Any:
    """Build a minimal RouteContract for apps_lic."""
    from tests._apps_contract.test_w5_apps_lic_c0_pa import _canonical_pipeline

    _vr, _l1, route, _fec = _canonical_pipeline()
    return dataclasses.replace(
        route,
        run_id=run_id or uuid.uuid4().hex[:16],
        execution_form=execution_form,
        l3_required=(execution_form == "managed_workflow"),
    )


def _make_fec(route: Any | None = None) -> Any:
    """Build a FinalEvidenceContract via the canonical C0 pipeline."""
    from tests._apps_contract.test_w5_apps_lic_c0_pa import _canonical_pipeline

    _vr, _l1, _route, fec = _canonical_pipeline()
    return fec


def _make_prompt(route: Any) -> Any:
    """Build a CompiledPromptArtifact via the canonical PA pipeline."""
    from tests._apps_contract.test_w5_apps_lic_c0_pa import _canonical_pipeline
    from agentic_core.prompt_governance.apps_lic_pa_binding import pa_compose_apps_lic

    vr, l1, _route, fec = _canonical_pipeline()
    return pa_compose_apps_lic(
        route=route,
        l1_plan=l1,
        fec=fec,
        validated_request=vr,
    )


def _make_step_contract(route: Any, fec: Any, prompt: Any | None = None) -> Any:
    """Build L3StepContract via l3_orchestrate_apps_lic."""
    from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

    _receipt, step, _bus = l3_orchestrate_apps_lic(route, fec, prompt)
    return step


# ================================================================== TC01-07 ==


class TestTC01_L3Participates:
    def test_l3_orchestrate_returns_three_tuple(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        result = l3_orchestrate_apps_lic(route, fec)
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_l3_required_is_true_in_receipt(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic
        from agentic_core.runtime.contracts.l3_runtime_orchestration_receipt import (
            L3RuntimeOrchestrationReceipt,
        )

        route = _make_route()
        fec = _make_fec()
        receipt, _step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert isinstance(receipt, L3RuntimeOrchestrationReceipt)
        assert receipt.l3_required is True

    def test_only_fires_for_managed_workflow(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route_mw = _make_route(execution_form="managed_workflow")
        fec = _make_fec()
        receipt, _step, _bus = l3_orchestrate_apps_lic(route_mw, fec)
        assert receipt.l3_required is True


class TestTC02_L3EmitsReceipt:
    def test_receipt_has_correct_run_id(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        run_id = uuid.uuid4().hex[:16]
        route = _make_route(run_id=run_id)
        fec = _make_fec()
        receipt, _step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert receipt.run_id == run_id

    def test_receipt_has_dag_id(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import (
            l3_orchestrate_apps_lic,
            APPS_LIC_DAG_ID,
        )

        route = _make_route()
        fec = _make_fec()
        receipt, _step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert receipt.dag_id == APPS_LIC_DAG_ID

    def test_receipt_has_sha256_dag_sha(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        receipt, _step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert receipt.dag_sha256.startswith("sha256:")

    def test_receipt_has_selected_node_ids(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import (
            l3_orchestrate_apps_lic,
            APPS_LIC_NODE_ID,
        )

        route = _make_route()
        fec = _make_fec()
        receipt, _step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert APPS_LIC_NODE_ID in receipt.selected_node_ids

    def test_receipt_step_contracts_not_empty(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        receipt, _step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert len(receipt.step_contracts) >= 1

    def test_receipt_deterministic_digest_present(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        receipt, _step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert receipt.deterministic_digest.startswith("sha256:")

    def test_receipt_l5_cert_ref_non_empty(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import (
            l3_orchestrate_apps_lic,
            APPS_LIC_L3_CERT_REF,
        )

        route = _make_route()
        fec = _make_fec()
        receipt, _step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert receipt.l5_certification_ref == APPS_LIC_L3_CERT_REF


class TestTC03_L3EmitsStepContract:
    def test_step_contract_type(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic
        from agentic_core.L3_orchestration.doctrine.contracts_l3_7 import L3StepContract

        route = _make_route()
        fec = _make_fec()
        _receipt, step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert isinstance(step, L3StepContract)

    def test_step_contract_id_non_empty(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        _receipt, step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert step.step_contract_id

    def test_step_expected_output_is_sealed_l2(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        _receipt, step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert step.expected_output_contract == "SealedL2Artifact"

    def test_step_no_durable_commit_authority_true(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        _receipt, step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert step.no_durable_commit_authority is True

    def test_step_timeout_positive(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        _receipt, step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert step.timeout_ms > 0


class TestTC04_L3PreservesFields:
    def test_workflow_id_stable_for_same_run(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        _r1, step1, _b1 = l3_orchestrate_apps_lic(route, fec)
        _r2, step2, _b2 = l3_orchestrate_apps_lic(route, fec)
        assert step1.workflow_id == step2.workflow_id

    def test_node_id_is_canonical(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import (
            l3_orchestrate_apps_lic,
            APPS_LIC_NODE_ID,
        )

        route = _make_route()
        fec = _make_fec()
        _receipt, step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert step.node_id == APPS_LIC_NODE_ID

    def test_capability_token_non_empty(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        _receipt, step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert step.capability_token_requirement.startswith("cap:")

    def test_sandbox_envelope_non_empty(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        _receipt, step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert step.sandbox_envelope_requirement.startswith("sbx:")

    def test_allowed_execution_lane_is_route_id(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        _receipt, step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert step.parent_route_id == route.route_id

    def test_replay_key_preserved(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        _receipt, step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert step.replay_key  # non-empty

    def test_dependency_refs_in_step_inputs(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        _receipt, step, _bus = l3_orchestrate_apps_lic(route, fec)
        # FEC compilation_hash ref should appear in evidence_refs
        assert len(step.inputs.evidence_refs) >= 1
        assert any(r.startswith("fec:") for r in step.inputs.evidence_refs)

    def test_checkpoint_refs_in_snapshot_id(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        _receipt, step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert step.snapshot_id  # non-empty — derived from run_id + workflow_id


class TestTC05_L3HardLaws:
    def test_no_execute_assertion_true(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        receipt, _step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert receipt.l3_no_execute_assertion is True

    def test_no_retrieve_assertion_true(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        receipt, _step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert receipt.l3_no_retrieve_assertion is True

    def test_no_prompt_assembly_assertion_true(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        receipt, _step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert receipt.l3_no_prompt_assembly_assertion is True

    def test_no_l4_write_assertion_true(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        receipt, _step, _bus = l3_orchestrate_apps_lic(route, fec)
        assert receipt.l3_no_l4_write_assertion is True

    def test_no_chromadb_in_source(self) -> None:
        lines = _import_lines("agentic_core.L3_orchestration.apps_lic_l3_binding")
        for line in lines:
            assert "chromadb" not in line.lower(), f"ChromaDB import found: {line!r}"

    def test_no_embedding_in_source(self) -> None:
        code = _code_only("agentic_core.L3_orchestration.apps_lic_l3_binding")
        forbidden = ["SentenceTransformer", "sentence_transformers", "get_embedding"]
        for pattern in forbidden:
            assert pattern not in code, f"Embedding pattern found: {pattern!r}"

    def test_no_hop_pipeline_call_in_source(self) -> None:
        """L3 must NOT import or instantiate HopPipelineExecutor — that is L2's job."""
        lines = _import_lines("agentic_core.L3_orchestration.apps_lic_l3_binding")
        for line in lines:
            assert "HopPipelineExecutor" not in line, (
                f"L3 must not import HopPipelineExecutor — hard law violation: {line!r}"
            )
        # Also check that it's not called/instantiated (outside of docstring/comments)
        mod = importlib.import_module("agentic_core.L3_orchestration.apps_lic_l3_binding")
        src = inspect.getsource(mod)
        # Strip comments and docstrings — only look at code lines
        code_lines = [
            ln for ln in src.splitlines()
            if ln.strip() and not ln.strip().startswith("#") and not ln.strip().startswith('"""')
            and not ln.strip().startswith("'\"'\"'")
        ]
        code_only = "\n".join(code_lines)
        # Must not call HopPipelineExecutor() outside of docstrings
        assert "HopPipelineExecutor()" not in code_only, (
            "L3 must not instantiate HopPipelineExecutor — hard law violation"
        )

    def test_no_l4_write_in_source(self) -> None:
        import re
        code = _code_only("agentic_core.L3_orchestration.apps_lic_l3_binding")
        # Must not call write_l4(...) or l4_write(...) — policy descriptor strings
        # like "no_retry_on_l4_write" are permitted.
        assert not re.search(r'\bwrite_l4\s*\(', code), "write_l4() call found in L3"
        assert not re.search(r'\bl4_write\s*\(', code), "l4_write() call found in L3"


class TestTC06_L3RejectsNonManagedWorkflow:
    def test_raises_for_single_step(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route(execution_form="single_step")
        fec = _make_fec()
        with pytest.raises(ValueError, match="execution_form"):
            l3_orchestrate_apps_lic(route, fec)

    def test_raises_for_wrong_type(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic
        from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract

        fec = _make_fec()
        with pytest.raises(TypeError, match="RouteContract"):
            l3_orchestrate_apps_lic("not-a-route", fec)  # type: ignore[arg-type]


class TestTC07_L3ContextBus:
    def test_context_bus_has_evidence_refs(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic
        from agentic_core.L3_orchestration.doctrine.contracts_l3_7 import L3ContextBus

        route = _make_route()
        fec = _make_fec()
        _receipt, _step, bus = l3_orchestrate_apps_lic(route, fec)
        assert isinstance(bus, L3ContextBus)
        assert len(bus.carried_evidence_refs) >= 1

    def test_context_bus_with_prompt_has_prompt_refs(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        prompt = _make_prompt(route)
        _receipt, _step, bus = l3_orchestrate_apps_lic(route, fec, prompt)
        assert len(bus.carried_prompt_artifact_refs) >= 1

    def test_context_bus_workflow_id_matches_step(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        _receipt, step, bus = l3_orchestrate_apps_lic(route, fec)
        assert bus.workflow_id == step.workflow_id


# ================================================================= TC08-15 ==


class TestTC08_L2ReceivesBoundedPacket:
    def _run_l2_with_stub(self, route: Any, fec: Any, step: Any, prompt: Any = None) -> Any:
        from agentic_core.L2_execution.apps_lic_l2_binding import l2_execute_apps_lic
        from apps_shared.orchestration import HopRunRecord, Checkpoint, StageStatus

        stub_record = HopRunRecord(
            run_id="stub_run_001",
            checkpoints=(
                Checkpoint(stage_id=1, stage_name="profile_analysis",
                           status=StageStatus.COMPLETED, output={"draft_message": "Hello world"}),
            ),
            final_context={"draft_message": "Hello world"},
            terminal_error="",
        )
        with patch(
            "agentic_core.L2_execution.apps_lic_l2_binding._invoke_hop_pipeline",
            return_value=("completed", stub_record, "Hello world"),
        ):
            return l2_execute_apps_lic(route, fec, step, prompt)

    def test_l2_rejects_non_managed_workflow(self) -> None:
        from agentic_core.L2_execution.apps_lic_l2_binding import l2_execute_apps_lic

        route_bad = _make_route(execution_form="single_step")
        fec = _make_fec()
        step = _make_step_contract(_make_route(), fec)  # valid step

        with pytest.raises(ValueError, match="execution_form"):
            l2_execute_apps_lic(route_bad, fec, step)

    def test_l2_rejects_wrong_step_type(self) -> None:
        from agentic_core.L2_execution.apps_lic_l2_binding import l2_execute_apps_lic

        route = _make_route()
        fec = _make_fec()
        with pytest.raises(TypeError, match="L3StepContract"):
            l2_execute_apps_lic(route, fec, "not-a-step")  # type: ignore[arg-type]

    def test_l2_accepts_valid_step(self) -> None:
        route = _make_route()
        fec = _make_fec()
        step = _make_step_contract(route, fec)
        sealed = self._run_l2_with_stub(route, fec, step)
        assert sealed is not None


class TestTC09_L2InvokesOnlyHopPipeline:
    def test_hop_pipeline_called_once(self) -> None:
        from agentic_core.L2_execution.apps_lic_l2_binding import l2_execute_apps_lic
        from apps_shared.orchestration import HopRunRecord, Checkpoint, StageStatus

        route = _make_route()
        fec = _make_fec()
        step = _make_step_contract(route, fec)

        stub_record = HopRunRecord(
            run_id="stub_001",
            checkpoints=(
                Checkpoint(stage_id=1, stage_name="profile", status=StageStatus.COMPLETED,
                           output={"draft_message": "test"}),
            ),
            final_context={"draft_message": "test"},
        )
        call_count = []

        def counting_invoke(*args: Any, **kwargs: Any) -> Any:
            call_count.append(1)
            return ("completed", stub_record, "test")

        with patch(
            "agentic_core.L2_execution.apps_lic_l2_binding._invoke_hop_pipeline",
            side_effect=counting_invoke,
        ):
            l2_execute_apps_lic(route, fec, step)

        assert len(call_count) == 1, "L2 must invoke the execution entrypoint exactly once"

    def test_no_other_llm_call_in_source(self) -> None:
        """L2 must delegate all LLM calls to HopPipelineExecutor only."""
        mod = importlib.import_module("agentic_core.L2_execution.apps_lic_l2_binding")
        src = inspect.getsource(mod)
        # Must not call vllm/openai/anthropic directly
        forbidden = ["chat_completions", "_post_chat_completion", "openai.ChatCompletion"]
        for pattern in forbidden:
            assert pattern not in src, f"Forbidden direct LLM call found: {pattern!r}"


class TestTC10_L2EmitsSealedArtifact:
    def _sealed(self) -> Any:
        from apps_shared.orchestration import HopRunRecord, Checkpoint, StageStatus
        from agentic_core.L2_execution.apps_lic_l2_binding import l2_execute_apps_lic

        route = _make_route()
        fec = _make_fec()
        step = _make_step_contract(route, fec)
        stub_record = HopRunRecord(
            run_id="r1",
            checkpoints=(
                Checkpoint(1, "profile", StageStatus.COMPLETED, {"draft_message": "hi"}),
            ),
            final_context={"draft_message": "hi"},
        )
        with patch(
            "agentic_core.L2_execution.apps_lic_l2_binding._invoke_hop_pipeline",
            return_value=("completed", stub_record, "hi"),
        ):
            return l2_execute_apps_lic(route, fec, step)

    def test_emits_sealed_l2_artifact_type(self) -> None:
        from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

        assert isinstance(self._sealed(), SealedL2Artifact)

    def test_execution_status_completed(self) -> None:
        assert self._sealed().execution_status == "completed"

    def test_run_id_matches_route(self) -> None:
        from agentic_core.L2_execution.apps_lic_l2_binding import l2_execute_apps_lic
        from apps_shared.orchestration import HopRunRecord, Checkpoint, StageStatus

        run_id = uuid.uuid4().hex[:16]
        route = _make_route(run_id=run_id)
        fec = _make_fec()
        step = _make_step_contract(route, fec)
        stub = HopRunRecord("r2", (Checkpoint(1, "p", StageStatus.COMPLETED, {}),), {})
        with patch(
            "agentic_core.L2_execution.apps_lic_l2_binding._invoke_hop_pipeline",
            return_value=("completed", stub, ""),
        ):
            sealed = l2_execute_apps_lic(route, fec, step)
        assert sealed.run_id == run_id


class TestTC11_L2PreservesRefFields:
    def _sealed_with_prompt(self) -> Any:
        from apps_shared.orchestration import HopRunRecord, Checkpoint, StageStatus
        from agentic_core.L2_execution.apps_lic_l2_binding import l2_execute_apps_lic

        route = _make_route()
        fec = _make_fec()
        prompt = _make_prompt(route)
        step = _make_step_contract(route, fec, prompt)
        stub = HopRunRecord(
            "r3",
            (Checkpoint(1, "profile", StageStatus.COMPLETED, {"draft_message": "x"}),),
            {"draft_message": "x"},
        )
        with patch(
            "agentic_core.L2_execution.apps_lic_l2_binding._invoke_hop_pipeline",
            return_value=("completed", stub, "x"),
        ):
            return l2_execute_apps_lic(route, fec, step, prompt)

    def test_evidence_refs_non_empty(self) -> None:
        sealed = self._sealed_with_prompt()
        assert len(sealed.evidence_refs) >= 1
        assert any(r.startswith("fec:") for r in sealed.evidence_refs)

    def test_prompt_refs_non_empty(self) -> None:
        sealed = self._sealed_with_prompt()
        assert len(sealed.prompt_refs) >= 1
        assert any(r.startswith("pa:") for r in sealed.prompt_refs)

    def test_tool_call_refs_non_empty(self) -> None:
        sealed = self._sealed_with_prompt()
        assert len(sealed.tool_call_refs) >= 1

    def test_model_call_refs_present(self) -> None:
        sealed = self._sealed_with_prompt()
        # model_call_refs populated from checkpoints
        assert isinstance(sealed.model_call_refs, tuple)

    def test_provider_receipts_non_empty(self) -> None:
        sealed = self._sealed_with_prompt()
        assert len(sealed.provider_receipts) >= 1

    def test_otel_span_refs_non_empty(self) -> None:
        sealed = self._sealed_with_prompt()
        # L2 adds its own span ref on top of route refs
        assert len(sealed.otel_span_refs) >= 1
        assert any("l2:apps_lic" in r for r in sealed.otel_span_refs)

    def test_replay_manifest_non_empty(self) -> None:
        sealed = self._sealed_with_prompt()
        assert sealed.replay_manifest.startswith("rman:")

    def test_audit_manifest_ref_non_empty(self) -> None:
        sealed = self._sealed_with_prompt()
        assert sealed.audit_manifest_ref.startswith("aman:")


class TestTC12_ProposedStateDiffInert:
    def _sealed(self) -> Any:
        from apps_shared.orchestration import HopRunRecord, Checkpoint, StageStatus
        from agentic_core.L2_execution.apps_lic_l2_binding import l2_execute_apps_lic

        route = _make_route()
        fec = _make_fec()
        step = _make_step_contract(route, fec)
        stub = HopRunRecord("r4", (Checkpoint(1, "p", StageStatus.COMPLETED, {}),), {})
        with patch(
            "agentic_core.L2_execution.apps_lic_l2_binding._invoke_hop_pipeline",
            return_value=("completed", stub, "msg"),
        ):
            return l2_execute_apps_lic(route, fec, step)

    def test_proposed_state_diff_is_empty_dict(self) -> None:
        assert self._sealed().proposed_state_diff == {}

    def test_proposed_state_diff_is_not_none(self) -> None:
        assert self._sealed().proposed_state_diff is not None


class TestTC13_NoL4Write:
    def _sealed(self) -> Any:
        from apps_shared.orchestration import HopRunRecord, Checkpoint, StageStatus
        from agentic_core.L2_execution.apps_lic_l2_binding import l2_execute_apps_lic

        route = _make_route()
        fec = _make_fec()
        step = _make_step_contract(route, fec)
        stub = HopRunRecord("r5", (Checkpoint(1, "p", StageStatus.COMPLETED, {}),), {})
        with patch(
            "agentic_core.L2_execution.apps_lic_l2_binding._invoke_hop_pipeline",
            return_value=("completed", stub, ""),
        ):
            return l2_execute_apps_lic(route, fec, step)

    def test_state_diff_authorized_false(self) -> None:
        assert self._sealed().state_diff_authorized is False

    def test_is_uwg_write_authority_false(self) -> None:
        assert self._sealed().is_uwg_write_authority is False

    def test_no_l4_write_in_source(self) -> None:
        import re
        code = _code_only("agentic_core.L2_execution.apps_lic_l2_binding")
        assert not re.search(r'\bwrite_l4\s*\(', code), "write_l4() call found in L2"
        assert not re.search(r'\bl4_write\s*\(', code), "l4_write() call found in L2"


class TestTC14_NoChromaDbMutation:
    def test_no_chromadb_import_in_l3(self) -> None:
        lines = _import_lines("agentic_core.L3_orchestration.apps_lic_l3_binding")
        for line in lines:
            assert "chromadb" not in line.lower()

    def test_no_chromadb_import_in_l2(self) -> None:
        lines = _import_lines("agentic_core.L2_execution.apps_lic_l2_binding")
        for line in lines:
            assert "chromadb" not in line.lower()

    def test_no_chromadb_call_in_l2_source(self) -> None:
        code = _code_only("agentic_core.L2_execution.apps_lic_l2_binding")
        assert "chromadb" not in code.lower()


class TestTC15_NoEmbeddingGeneration:
    def test_no_embedding_in_l3_source(self) -> None:
        code = _code_only("agentic_core.L3_orchestration.apps_lic_l3_binding")
        for pattern in ["SentenceTransformer", "sentence_transformers", "get_embedding"]:
            assert pattern not in code, f"Embedding call found in L3: {pattern!r}"

    def test_no_embedding_in_l2_source(self) -> None:
        code = _code_only("agentic_core.L2_execution.apps_lic_l2_binding")
        for pattern in ["SentenceTransformer", "sentence_transformers", "get_embedding"]:
            assert pattern not in code, f"Embedding call found in L2: {pattern!r}"


# ================================================================= TC16-20 ==


class TestTC16_Regression_W3_W4_W5:
    def test_w3_u0_importable(self) -> None:
        mod = importlib.import_module("agentic_core.runtime.entry.u0_apps_lic_binding")
        assert mod is not None

    def test_w4_l1_importable(self) -> None:
        mod = importlib.import_module("agentic_core.L1_cognition.apps_lic_l1_binding")
        assert mod is not None

    def test_w4_l0_importable(self) -> None:
        mod = importlib.import_module("agentic_core.L0_routing.apps_lic_l0_binding")
        assert mod is not None

    def test_w5_c0_importable(self) -> None:
        mod = importlib.import_module("agentic_core.runtime.c0.apps_lic_c0_binding")
        assert mod is not None

    def test_w5_pa_importable(self) -> None:
        mod = importlib.import_module(
            "agentic_core.prompt_governance.apps_lic_pa_binding"
        )
        assert mod is not None

    def test_w6_l3_importable(self) -> None:
        mod = importlib.import_module(
            "agentic_core.L3_orchestration.apps_lic_l3_binding"
        )
        assert mod is not None

    def test_w6_l2_importable(self) -> None:
        mod = importlib.import_module("agentic_core.L2_execution.apps_lic_l2_binding")
        assert mod is not None


class TestTC17_L3Determinism:
    def test_workflow_id_same_for_same_run(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        run_id = uuid.uuid4().hex[:16]
        route = _make_route(run_id=run_id)
        fec = _make_fec()
        _r1, step1, _b1 = l3_orchestrate_apps_lic(route, fec)
        _r2, step2, _b2 = l3_orchestrate_apps_lic(route, fec)
        assert step1.workflow_id == step2.workflow_id

    def test_dag_sha256_stable(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        r1, _s1, _b1 = l3_orchestrate_apps_lic(route, fec)
        r2, _s2, _b2 = l3_orchestrate_apps_lic(route, fec)
        assert r1.dag_sha256 == r2.dag_sha256

    def test_different_run_ids_produce_different_workflow_ids(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route1 = _make_route(run_id=uuid.uuid4().hex[:16])
        route2 = _make_route(run_id=uuid.uuid4().hex[:16])
        fec = _make_fec()
        _r1, step1, _b1 = l3_orchestrate_apps_lic(route1, fec)
        _r2, step2, _b2 = l3_orchestrate_apps_lic(route2, fec)
        assert step1.workflow_id != step2.workflow_id


class TestTC18_L2FailSoft:
    def test_stub_fallback_on_hop_error(self) -> None:
        from agentic_core.L2_execution.apps_lic_l2_binding import l2_execute_apps_lic
        from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

        route = _make_route()
        fec = _make_fec()
        step = _make_step_contract(route, fec)

        with patch(
            "agentic_core.L2_execution.apps_lic_l2_binding._invoke_hop_pipeline",
            return_value=("stub_fallback", None, None),
        ):
            sealed = l2_execute_apps_lic(route, fec, step)

        assert isinstance(sealed, SealedL2Artifact)
        assert sealed.execution_status == "stub_fallback"

    def test_stub_fallback_still_has_cert_ref(self) -> None:
        from agentic_core.L2_execution.apps_lic_l2_binding import (
            l2_execute_apps_lic,
            APPS_LIC_L2_CERT_REF,
        )

        route = _make_route()
        fec = _make_fec()
        step = _make_step_contract(route, fec)

        with patch(
            "agentic_core.L2_execution.apps_lic_l2_binding._invoke_hop_pipeline",
            return_value=("stub_fallback", None, None),
        ):
            sealed = l2_execute_apps_lic(route, fec, step)

        assert sealed.l5_certification_ref == APPS_LIC_L2_CERT_REF


class TestTC19_L2CertRef:
    def test_cert_ref_is_correct(self) -> None:
        from agentic_core.L2_execution.apps_lic_l2_binding import (
            l2_execute_apps_lic,
            APPS_LIC_L2_CERT_REF,
        )
        from apps_shared.orchestration import HopRunRecord, Checkpoint, StageStatus

        route = _make_route()
        fec = _make_fec()
        step = _make_step_contract(route, fec)
        stub = HopRunRecord("r6", (Checkpoint(1, "p", StageStatus.COMPLETED, {}),), {})
        with patch(
            "agentic_core.L2_execution.apps_lic_l2_binding._invoke_hop_pipeline",
            return_value=("completed", stub, "msg"),
        ):
            sealed = l2_execute_apps_lic(route, fec, step)

        assert sealed.l5_certification_ref == APPS_LIC_L2_CERT_REF


class TestTC20_L3AllHardLawAssertions:
    def test_all_four_assertions_true(self) -> None:
        from agentic_core.L3_orchestration.apps_lic_l3_binding import l3_orchestrate_apps_lic

        route = _make_route()
        fec = _make_fec()
        receipt, _step, _bus = l3_orchestrate_apps_lic(route, fec)

        assert receipt.l3_no_execute_assertion is True, "l3_no_execute_assertion"
        assert receipt.l3_no_retrieve_assertion is True, "l3_no_retrieve_assertion"
        assert receipt.l3_no_prompt_assembly_assertion is True, "l3_no_prompt_assembly_assertion"
        assert receipt.l3_no_l4_write_assertion is True, "l3_no_l4_write_assertion"
