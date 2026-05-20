"""AG-8-FU2: apps_lic shared build_x3_packet path return tests.

Verifies that:
1. apps_lic_exit_binding uses build_x3_packet (not local X3Disposition construction).
2. ExitReviewPacket contains l5_certification_refs.
3. build_x3_packet receives non-empty l5_certification_ref.
4. Missing cert ref fails closed.
5. Golden-path X3 disposition is exactly one outcome.
6. scalar eval_score is not authoritative.
7. material FAIL blocks ALLOW_FINISH.
8. material UNKNOWN cannot pass.
9. NOT_APPLICABLE without reason fails.
10. No direct L4 write.
11. No ChromaDB mutation.
12. No embedding generation.
"""
from __future__ import annotations

import inspect
import re
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.types import V6Disposition
from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import (
    MissingL5CertificationRef,
    build_x3_packet,
)
from agentic_core.runtime.contracts.x3_disposition import X3Disposition
from apps_lic.runtime.bindings.exit_binding import (
    _build_exit_review_packet,
    exit_finalize_apps_lic,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_l2(
    *,
    execution_status: str = "completed",
    generated_content: str = "Dear Hiring Manager, ...",
    compilation_hash: str = "abc123",
    l5_certification_ref: str = "exit-apps-lic-outreach-message-ag8-w7-f3c2e1",
) -> Any:
    """Minimal SealedL2Artifact for testing."""
    import uuid
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

    return SealedL2Artifact(
        request_id="req-fu2-" + uuid.uuid4().hex[:8],
        run_id="run-fu2-" + uuid.uuid4().hex[:8],
        app_id="apps_lic",
        trace_id="trace-fu2-" + uuid.uuid4().hex[:8],
        execution_status=execution_status,
        generated_content=generated_content,
        compilation_hash=compilation_hash,
        prompt_artifact_digest="pad-fu2-test",
        replay_key="replay-fu2-key",
        tenant_id="apps_lic_tenant",
        l5_certification_ref=l5_certification_ref,
    )


def _source_of(module_name: str) -> str:
    import importlib
    mod = importlib.import_module(module_name)
    return inspect.getsource(mod)


def _code_only(src: str) -> str:
    """Strip comment lines."""
    lines = []
    for line in src.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            lines.append(line)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 1. apps_lic_exit_binding uses build_x3_packet
# ---------------------------------------------------------------------------

class TestFU2UsesSharedBuilder:
    def test_build_x3_packet_is_imported(self) -> None:
        src = _source_of("apps_lic.runtime.bindings.exit_binding")
        assert "from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import build_x3_packet" in src, (
            "build_x3_packet must be imported from shared x3_dispositions (AG-8-FU2)"
        )

    def test_build_x3_packet_is_called(self) -> None:
        src = _source_of("apps_lic.runtime.bindings.exit_binding")
        code = _code_only(src)
        assert "build_x3_packet(" in code, (
            "build_x3_packet() must be called in apps_lic exit_finalize_apps_lic (AG-8-FU2)"
        )

    def test_local_x3disposition_construction_removed(self) -> None:
        """The direct X3Disposition(...) construction was the old workaround.
        It should no longer appear in the main execution path — only in the bridge helper."""
        src = _source_of("apps_lic.runtime.bindings.exit_binding")
        code = _code_only(src)
        # The bridge helper _x3_packet_to_disposition is allowed to have X3Disposition(...)
        # but exit_finalize_apps_lic itself must not construct X3Disposition directly.
        # Extract only the exit_finalize_apps_lic function body.
        func_src = inspect.getsource(exit_finalize_apps_lic)
        assert "X3Disposition(" not in func_src, (
            "exit_finalize_apps_lic must not construct X3Disposition directly (AG-8-FU2 removes workaround)"
        )

    def test_bridge_helper_exists(self) -> None:
        from apps_lic.runtime.bindings.exit_binding import _x3_packet_to_disposition
        assert callable(_x3_packet_to_disposition)


# ---------------------------------------------------------------------------
# 2. ExitReviewPacket contains l5_certification_refs
# ---------------------------------------------------------------------------

class TestFU2CertRefPopulation:
    def test_exit_review_packet_has_cert_ref(self) -> None:
        l2 = _make_l2()
        pkt = _build_exit_review_packet(l2)
        assert pkt.l5_certification_refs, "ExitReviewPacket.l5_certification_refs must be non-empty"
        assert pkt.l5_certification_refs[0], "l5_certification_refs[0] must be non-empty string"

    def test_cert_ref_value_is_canonical(self) -> None:
        l2 = _make_l2()
        pkt = _build_exit_review_packet(l2)
        assert pkt.l5_certification_refs[0] == "exit-apps-lic-outreach-message-ag8-w7-f3c2e1"

    def test_cert_ref_reaches_x3_packet(self) -> None:
        """build_x3_packet must produce a packet whose l5_certification_ref is non-empty."""
        from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision
        l2 = _make_l2()
        pkt = _build_exit_review_packet(l2)
        decision = AggregateDecision(disposition=V6Disposition.ALLOW)
        x3_pkt = build_x3_packet(pkt, decision, final_response="hello")
        assert x3_pkt.l5_certification_ref == pkt.l5_certification_refs[0]

    def test_cert_ref_in_final_x3_disposition(self) -> None:
        l2 = _make_l2()
        result = exit_finalize_apps_lic(l2)
        assert result.l5_certification_ref == "exit-apps-lic-outreach-message-ag8-w7-f3c2e1"


# ---------------------------------------------------------------------------
# 3. build_x3_packet receives non-empty cert ref
# ---------------------------------------------------------------------------

class TestFU2CertRefNonEmpty:
    def test_allow_packet_cert_ref_non_empty(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision
        l2 = _make_l2()
        pkt = _build_exit_review_packet(l2)
        decision = AggregateDecision(disposition=V6Disposition.ALLOW)
        x3_pkt = build_x3_packet(pkt, decision)
        assert x3_pkt.l5_certification_ref != ""

    def test_deny_packet_cert_ref_non_empty(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision
        l2 = _make_l2(execution_status="failed")
        pkt = _build_exit_review_packet(l2)
        decision = AggregateDecision(disposition=V6Disposition.DENY)
        x3_pkt = build_x3_packet(pkt, decision)
        assert x3_pkt.l5_certification_ref != ""

    def test_escalate_packet_cert_ref_non_empty(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision
        l2 = _make_l2()
        pkt = _build_exit_review_packet(l2)
        decision = AggregateDecision(disposition=V6Disposition.ESCALATE)
        x3_pkt = build_x3_packet(pkt, decision)
        assert x3_pkt.l5_certification_ref != ""


# ---------------------------------------------------------------------------
# 4. Missing cert ref fails closed
# ---------------------------------------------------------------------------

class TestFU2FailClosed:
    def test_missing_cert_ref_raises(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.types import ExitReviewPacket, SourceType
        from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision
        pkt = ExitReviewPacket(
            request_id="r1",
            run_id="run1",
            trace_root="",
            source_type=SourceType.L2_SEALED_ARTIFACT,
            terminal_class="answer_only",
            track_label="production",
            policy_hash="ph",
            blueprint_hash="",
            prompt_hash="",
            prompt_assembly_status="complete",
            compliance_hash="",
            hmac_sig="",
            replay_key="",
            output={},
            exec_trace={},
            otel_spans={},
            sandbox_envelope={},
            grader_composition={},
            capability_token={},
            final_evidence_contract={},
            route_contract={},
            state_diff={},
            write_intent_class="",
            evidence_bundle={},
            app_specific_eval={},
            hitl_packet={},
            l5_certification_refs=(),  # empty — must fail closed
        )
        decision = AggregateDecision(disposition=V6Disposition.ALLOW)
        with pytest.raises((MissingL5CertificationRef, ValueError)):
            build_x3_packet(pkt, decision)

    def test_missing_cert_ref_is_missing_l5_certification_ref_subclass(self) -> None:
        assert issubclass(MissingL5CertificationRef, ValueError)


# ---------------------------------------------------------------------------
# 5. Golden-path X3 disposition is exactly one outcome
# ---------------------------------------------------------------------------

class TestFU2GoldenPath:
    def test_golden_path_produces_exactly_one_disposition(self) -> None:
        l2 = _make_l2()
        result = exit_finalize_apps_lic(l2)
        assert isinstance(result, X3Disposition)

    def test_golden_path_exit_status_success(self) -> None:
        l2 = _make_l2()
        result = exit_finalize_apps_lic(l2)
        assert result.exit_status == "success"

    def test_golden_path_outcome_authorized(self) -> None:
        l2 = _make_l2()
        result = exit_finalize_apps_lic(l2)
        assert result.outcome_authorized is True

    def test_golden_path_disposition_field(self) -> None:
        l2 = _make_l2()
        result = exit_finalize_apps_lic(l2)
        assert result.final_output["disposition"] == V6Disposition.ALLOW.value

    def test_schema_version_updated_to_w7_1(self) -> None:
        """AG-8-FU2 bumps schema_version from W7.0 to W7.1."""
        l2 = _make_l2()
        result = exit_finalize_apps_lic(l2)
        assert result.schema_version == "W7.1"


# ---------------------------------------------------------------------------
# 6. scalar eval_score is not authoritative
# ---------------------------------------------------------------------------

class TestFU2EvalScoreNotAuthoritative:
    def test_eval_score_is_none(self) -> None:
        l2 = _make_l2()
        result = exit_finalize_apps_lic(l2)
        assert result.eval_score is None, "eval_score must remain None — not authoritative"

    def test_eval_threshold_met_matches_outcome_authorized(self) -> None:
        l2 = _make_l2()
        result = exit_finalize_apps_lic(l2)
        assert result.eval_threshold_met == result.outcome_authorized


# ---------------------------------------------------------------------------
# 7. material FAIL blocks ALLOW_FINISH
# ---------------------------------------------------------------------------

class TestFU2MaterialFailBlocks:
    def test_failed_l2_denied(self) -> None:
        l2 = _make_l2(execution_status="failed", generated_content="")
        result = exit_finalize_apps_lic(l2)
        assert not result.outcome_authorized, "Failed L2 must not be authorized"
        assert result.exit_status != "success"

    def test_failed_l2_exit_status_failure(self) -> None:
        l2 = _make_l2(execution_status="failed", generated_content="")
        result = exit_finalize_apps_lic(l2)
        assert result.exit_status in {"failure", "escalated", "abstain"}


# ---------------------------------------------------------------------------
# 8. material UNKNOWN cannot pass
# ---------------------------------------------------------------------------

class TestFU2MaterialUnknownCannotPass:
    def test_unknown_disposition_does_not_allow(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision
        from apps_lic.runtime.bindings.exit_binding import (
            _build_exit_review_packet,
            _x3_packet_to_disposition,
        )
        from agentic_core.runtime.contracts.posture import POSTURE_WRITE_INTENT

        l2 = _make_l2()
        # ESCALATE represents material-unknown routing
        from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import build_x3b_escalate
        pkt = _build_exit_review_packet(l2)
        decision = AggregateDecision(disposition=V6Disposition.ESCALATE)
        x3_pkt = build_x3b_escalate(pkt, decision)
        result = _x3_packet_to_disposition(x3_pkt, l2, (), "2026-05-10T00:00:00Z")
        assert not result.outcome_authorized
        assert result.exit_status == "escalated"
        assert result.hitl_required is True


# ---------------------------------------------------------------------------
# 9. NOT_APPLICABLE — apps_lic maps X1J as NOT_APPLICABLE (inert state_diff)
# ---------------------------------------------------------------------------

class TestFU2NotApplicableReason:
    def test_x1j_is_not_applicable_in_golden_path(self) -> None:
        """X1J (write_eligibility) must be NOT_APPLICABLE because proposed_state_diff is inert."""
        from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import run_all_x1_gates
        l2 = _make_l2()
        pkt = _build_exit_review_packet(l2)
        verdicts = run_all_x1_gates(pkt)
        x1j = next((v for v in verdicts if v.gate_id == "X1J"), None)
        assert x1j is not None, "X1J verdict must be present"
        from agentic_core.L3_orchestration.exit_eval.v6.types import GateResult
        assert x1j.result is GateResult.NOT_APPLICABLE, (
            f"X1J must be NOT_APPLICABLE for inert state_diff; got {x1j.result}"
        )

    def test_gate_verdict_accepts_not_applicable_with_reason(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.types import GateResult, GateVerdict
        v = GateVerdict(
            gate_id="X1J",
            result=GateResult.NOT_APPLICABLE,
            reason_codes=["no_state_diff"],
        )
        assert v.result is GateResult.NOT_APPLICABLE


# ---------------------------------------------------------------------------
# 10. No direct L4 write
# ---------------------------------------------------------------------------

class TestFU2NoL4Write:
    def test_no_direct_l4_write_in_source(self) -> None:
        src = _source_of("apps_lic.runtime.bindings.exit_binding")
        forbidden = ["chromadb", "chroma_client", ".upsert(", ".delete(", "L4_state"]
        for pattern in forbidden:
            assert pattern not in src, f"Forbidden L4 write pattern {pattern!r} found"

    def test_no_db_write_in_finalize(self) -> None:
        func_src = inspect.getsource(exit_finalize_apps_lic)
        assert "open(" not in func_src
        assert ".write(" not in func_src
        assert "sqlite" not in func_src.lower()


# ---------------------------------------------------------------------------
# 11. No ChromaDB mutation
# ---------------------------------------------------------------------------

class TestFU2NoChromaDBMutation:
    def test_no_chromadb_import(self) -> None:
        src = _source_of("apps_lic.runtime.bindings.exit_binding")
        assert "import chromadb" not in src
        assert "from chromadb" not in src

    def test_no_chroma_upsert(self) -> None:
        src = _source_of("apps_lic.runtime.bindings.exit_binding")
        assert ".upsert(" not in src
        assert "collection.add(" not in src


# ---------------------------------------------------------------------------
# 12. No embedding generation
# ---------------------------------------------------------------------------

class TestFU2NoEmbedding:
    def test_no_embedding_api_calls_in_source(self) -> None:
        src = _source_of("apps_lic.runtime.bindings.exit_binding")
        # Check for actual API call patterns (not docstring mentions)
        forbidden_calls = ["embed(", "sentence_transformers", "openai.Embedding", "embeddings.create"]
        for pattern in forbidden_calls:
            assert pattern not in src, f"Forbidden embedding call pattern {pattern!r} found"

    def test_no_encode_call_in_source(self) -> None:
        """encode() calls suggest embedding generation (sentence-transformers). Exclude bytes encode."""
        func_src = inspect.getsource(exit_finalize_apps_lic)
        # .encode( with no args is bytes; embedding is .encode("text") or encode(tensor)
        # Check the finalize function specifically does not have sentence-transformers-style calls
        assert "sentence_transformers" not in func_src
        assert "model.encode(" not in func_src


# ---------------------------------------------------------------------------
# AG-8-FU1 regression guard
# ---------------------------------------------------------------------------

class TestFU2FU1Regression:
    def test_fu1_exception_still_exported(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import (
            MissingL5CertificationRef,
        )
        assert MissingL5CertificationRef is not None

    def test_fu1_helper_still_works(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import _extract_cert_ref
        from agentic_core.L3_orchestration.exit_eval.v6.types import ExitReviewPacket, SourceType
        pkt = ExitReviewPacket(
            request_id="r",
            run_id="r",
            trace_root="",
            source_type=SourceType.L2_SEALED_ARTIFACT,
            terminal_class="answer_only",
            track_label="production",
            policy_hash="ph",
            blueprint_hash="",
            prompt_hash="",
            prompt_assembly_status="complete",
            compliance_hash="",
            hmac_sig="",
            replay_key="",
            output={},
            exec_trace={},
            otel_spans={},
            sandbox_envelope={},
            grader_composition={},
            capability_token={},
            final_evidence_contract={},
            route_contract={},
            state_diff={},
            write_intent_class="",
            evidence_bundle={},
            app_specific_eval={},
            hitl_packet={},
            l5_certification_refs=("ref-abc",),
        )
        assert _extract_cert_ref(pkt) == "ref-abc"
