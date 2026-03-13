"""Integration tests for the full prompt provenance lifecycle.

Covers:
  - TestFullPromptLifecycleIntegration: build → validate → execute → drift → adapt → bus
"""

from __future__ import annotations

import hashlib

import pytest

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_TS = 1_700_200_000
_H64 = "a" * 64
_H64b = "b" * 64


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _make_outcome_record(
    trace_id="tr-001",
    final_outcome="SUCCESS",
    groundedness=0.85,
    hitl=False,
    healer=False,
    healer_id=None,
    guardrail_hits=(),
    replay_status="NOT_TESTED",
    failure_slot="NONE",
    prompt_hash=None,
):
    from system_learning.types.prompt_artifact_types import PromptOutcomeRecord

    ph = prompt_hash or _sha256("prompt")
    oid = _sha256(trace_id + final_outcome + str(groundedness))
    return PromptOutcomeRecord(
        outcome_id=oid,
        prompt_hash=ph,
        trace_id=trace_id,
        route="PATH_A",
        model="gpt-4o",
        groundedness_score=groundedness,
        guardrail_hits=guardrail_hits,
        healer_invoked=healer,
        healer_id=healer_id,
        hitl_escalation=hitl,
        replay_status=replay_status,
        final_outcome=final_outcome,
        failure_slot=failure_slot,
        support_score=0.9,
        completeness_score=0.95,
        citation_count=3,
        adg_entity_name=f"ADG::PromptOutcome::{oid[:16]}",
        timestamp_utc=_TS,
    )


def _make_build_request(
    s0="System role content",
    d0="Defensive fence content",
    i0="Instruction content",
    c0="Context / RAG content",
    u0="User input here",
    template_ids=("tmpl-001",),
    fewshot_ids=("fs-001",),
    injection_ids=("inj-001",),
    model_target="gpt-4o",
    policy_hash=None,
):
    from system_learning.engines.prompt_provenance_builder import (
        PromptBuildRequest,
        SlotPayload,
    )

    return PromptBuildRequest(
        s0=SlotPayload(content=s0),
        d0=SlotPayload(content=d0),
        i0=SlotPayload(content=i0),
        c0=SlotPayload(content=c0, source_ids=(_sha256("chunk-1"),)),
        u0=SlotPayload(content=u0),
        template_ids=template_ids,
        fewshot_ids=fewshot_ids,
        injection_ids=injection_ids,
        model_target=model_target,
        policy_hash=policy_hash,
        adg_entity_prefix="ADG::CompiledPrompt",
        timestamp_utc=_TS,
    )


# ===========================================================================
# 8. Integration — full prompt lifecycle
# ===========================================================================


class TestFullPromptLifecycleIntegration:
    """End-to-end: build → validate → execute → drift → adapt → bus."""

    def _build_artifact(self):
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt

        req = _make_build_request(policy_hash=_sha256("policy_v1"))
        result = build_compiled_prompt(req)
        return result.artifact, result.adg_relations

    def test_build_to_validate_pipeline(self):
        from system_learning.engines.prompt_safety_validator import (
            PromptSafetyValidator,
            SafetyValidatorConfig,
        )

        artifact, prov_rels = self._build_artifact()
        ph = _sha256("policy_v1")
        cfg = SafetyValidatorConfig(active_policy_hash=ph)
        decision, safety_rels = PromptSafetyValidator(cfg).validate(artifact, _TS)
        assert decision.allowed is True
        total_rels = prov_rels + safety_rels
        rel_types = {r for (_, r, _) in total_rels}
        from system_learning.types.prompt_adg_relations import (
            PROVENANCE_USES_S0_RULE,
            SAFETY_ALLOWED,
        )

        assert PROVENANCE_USES_S0_RULE in rel_types
        assert SAFETY_ALLOWED in rel_types

    def test_execute_produces_outcome_record(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        artifact, _ = self._build_artifact()
        result = trace_execution(
            artifact.prompt_hash,
            "tr-integration-001",
            {
                "route_selected": "PATH_A",
                "model_id": "gpt-4o",
                "latency_ms": 400,
                "retrieval_groundedness_score": 0.88,
                "success": True,
                "chunk_ids": ["c1", "c2"],
                "citation_set_hash": _sha256("cset"),
            },
            _TS + 10,
        )
        assert result.outcome_record.final_outcome == "SUCCESS"
        assert result.outcome_record.groundedness_score == pytest.approx(0.88, abs=1e-5)

    def test_adapt_outcome_to_bus_record(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        artifact, _ = self._build_artifact()
        exec_result = trace_execution(
            artifact.prompt_hash,
            "tr-adapt-001",
            {"success": True, "retrieval_groundedness_score": 0.9},
            _TS + 20,
        )
        bus_record = convert_outcome_to_record(exec_result.outcome_record)
        assert bus_record.outcome_class == "SUCCESS"
        assert bus_record.retrieval_groundedness == pytest.approx(0.9, abs=1e-5)

    def test_drift_detected_after_groundedness_drop(self):
        from system_learning.engines.prompt_drift_detector import detect_prompt_drift

        baseline = [_make_outcome_record(trace_id=f"b{i}", groundedness=0.9) for i in range(20)]
        current = [_make_outcome_record(trace_id=f"c{i}", groundedness=0.7) for i in range(20)]
        signals = detect_prompt_drift(baseline, current, _H64, _H64b, _TS)
        assert any(s.drift_type == "GROUNDEDNESS_DROP" for s in signals)

    def test_bus_adapter_feeds_meta_learning_cluster(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcomes_to_records
        from system_learning.engines.rca_cluster_engine import cluster_records

        outcomes = [
            _make_outcome_record(trace_id=f"tr-{i}", groundedness=0.2, final_outcome="SAFE_FAILURE")
            for i in range(6)
        ]
        records = convert_outcomes_to_records(outcomes)
        clusters = cluster_records(records, _TS)
        assert len(clusters) >= 1
        # Should produce a LOW_GROUNDEDNESS cluster
        patterns = {c.failure_pattern for c in clusters}
        assert "LOW_GROUNDEDNESS" in patterns

    def test_all_adg_relations_use_known_relation_types(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.engines.prompt_safety_validator import validate_prompt
        from system_learning.types.prompt_adg_relations import ALL_PROMPT_RELATIONS

        artifact, prov_rels = self._build_artifact()
        _, safety_rels = validate_prompt(artifact, _TS)
        exec_result = trace_execution(artifact.prompt_hash, "tr-all-rels", {"success": True}, _TS + 5)
        all_rels = prov_rels + safety_rels + exec_result.adg_relations
        for _, rel, _ in all_rels:
            assert rel in ALL_PROMPT_RELATIONS, f"Unknown relation type emitted: {rel!r}"

    def test_provenance_chain_prompt_hash_consistent(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt

        req = _make_build_request()
        build_result = build_compiled_prompt(req)
        artifact = build_result.artifact

        exec_result = trace_execution(
            artifact.prompt_hash,
            "tr-chain-001",
            {"success": True, "retrieval_groundedness_score": 0.85},
            _TS + 100,
        )
        # The outcome record should reference the same prompt hash
        assert exec_result.outcome_record.prompt_hash == artifact.prompt_hash
