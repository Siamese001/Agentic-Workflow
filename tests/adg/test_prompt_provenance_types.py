"""Tests for prompt artifact types and ADG relation constants.

Covers:
  - prompt_artifact_types.py  — type construction, invariants, hashing
  - prompt_adg_relations.py   — relation constant completeness
"""

from __future__ import annotations

import hashlib
import json

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_prompt_provenance_types")
_emit_applies_guardrail("p0", "test_prompt_provenance_types", "p0_governance")
_emit_reads_policy_state("p0", "test_prompt_provenance_types", "policy_binding")
_emit_snapshots_state("p0", "test_prompt_provenance_types", "state_snapshot")
emit_replay_key("p0", "test_prompt_provenance_types")
emit_determinism_digest("p0", "test_prompt_provenance_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_TS = 1_700_200_000
_H64 = "a" * 64
_H64b = "b" * 64


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _make_slot_manifest(
    total_tokens=512,
    budget_class="STANDARD",
):
    from system_learning.types.prompt_artifact_types import PromptSlotManifest

    s0 = _sha256("s0_content")
    d0 = _sha256("d0_content")
    i0 = _sha256("i0_content")
    c0 = _sha256("c0_content")
    u0 = _sha256("u0_content")
    return PromptSlotManifest(
        s0_hash=s0,
        d0_hash=d0,
        i0_hash=i0,
        c0_hash=c0,
        u0_hash=u0,
        s0_tokens=100,
        d0_tokens=80,
        i0_tokens=100,
        c0_tokens=160,
        u0_tokens=72,
        total_tokens=total_tokens,
        budget_class=budget_class,
    )


def _make_artifact(
    prompt_hash=None,
    budget_class="STANDARD",
    total_tokens=512,
    policy_hash=None,
    model_target="gpt-4o",
):
    from system_learning.types.prompt_artifact_types import CompiledPromptArtifact

    ph = prompt_hash or _sha256("prompt_content")
    manifest = _make_slot_manifest(total_tokens=total_tokens, budget_class=budget_class)
    return CompiledPromptArtifact(
        prompt_hash=ph,
        slot_manifest=manifest,
        template_ids=("tmpl-001",),
        fewshot_ids=("fs-001", "fs-002"),
        injection_ids=("inj-001",),
        c0_sources=(_sha256("chunk-1"), _sha256("chunk-2")),
        model_target=model_target,
        policy_hash=policy_hash,
        adg_entity_name=f"ADG::CompiledPrompt::{ph[:16]}",
        influence_class="C0_INFORMATIONAL",
        timestamp_utc=_TS,
    )


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


# ===========================================================================
# 1. Type construction and invariants
# ===========================================================================


class TestPromptSlotManifest:
    def test_construction_succeeds(self):
        m = _make_slot_manifest()
        assert m.budget_class == "STANDARD"
        assert m.total_tokens == 512

    def test_invalid_budget_class_raises(self):
        from system_learning.types.prompt_artifact_types import PromptSlotManifest

        with pytest.raises(ValueError, match="budget_class"):
            PromptSlotManifest(
                s0_hash=_H64,
                d0_hash=_H64,
                i0_hash=_H64,
                c0_hash=_H64,
                u0_hash=_H64,
                s0_tokens=1,
                d0_tokens=1,
                i0_tokens=1,
                c0_tokens=1,
                u0_tokens=1,
                total_tokens=5,
                budget_class="INVALID",
            )

    def test_negative_token_count_raises(self):
        from system_learning.types.prompt_artifact_types import PromptSlotManifest

        with pytest.raises(ValueError, match="s0_tokens"):
            PromptSlotManifest(
                s0_hash=_H64,
                d0_hash=_H64,
                i0_hash=_H64,
                c0_hash=_H64,
                u0_hash=_H64,
                s0_tokens=-1,
                d0_tokens=1,
                i0_tokens=1,
                c0_tokens=1,
                u0_tokens=1,
                total_tokens=3,
                budget_class="COMPACT",
            )

    def test_stable_hash_is_sha256_of_to_json(self):
        m = _make_slot_manifest()
        from system_learning.enforcement.determinism import deterministic_json

        expected = _sha256(deterministic_json(m.to_dict()))
        assert m.stable_hash() == expected

    def test_stable_hash_deterministic(self):
        m1 = _make_slot_manifest()
        m2 = _make_slot_manifest()
        assert m1.stable_hash() == m2.stable_hash()

    def test_all_budget_classes_accepted(self):
        for bc in ("COMPACT", "STANDARD", "EXTENDED", "OVERFLOW"):
            m = _make_slot_manifest(budget_class=bc)
            assert m.budget_class == bc

    def test_to_dict_contains_all_keys(self):
        m = _make_slot_manifest()
        d = m.to_dict()
        for key in (
            "s0_hash",
            "d0_hash",
            "i0_hash",
            "c0_hash",
            "u0_hash",
            "s0_tokens",
            "d0_tokens",
            "i0_tokens",
            "c0_tokens",
            "u0_tokens",
            "total_tokens",
            "budget_class",
        ):
            assert key in d


class TestCompiledPromptArtifact:
    def test_construction_succeeds(self):
        a = _make_artifact()
        assert a.influence_class == "C0_INFORMATIONAL"
        assert a.adg_entity_name.startswith("ADG::")

    def test_wrong_influence_class_raises(self):
        from system_learning.types.prompt_artifact_types import CompiledPromptArtifact

        with pytest.raises(ValueError, match="influence_class"):
            CompiledPromptArtifact(
                prompt_hash=_H64,
                slot_manifest=_make_slot_manifest(),
                template_ids=(),
                fewshot_ids=(),
                injection_ids=(),
                c0_sources=(),
                model_target="gpt-4o",
                policy_hash=None,
                adg_entity_name="ADG::CompiledPrompt::test",
                influence_class="ROUTING",
                timestamp_utc=_TS,
            )

    def test_adg_entity_must_start_with_adg(self):
        from system_learning.types.prompt_artifact_types import CompiledPromptArtifact

        with pytest.raises(ValueError, match="ADG::"):
            CompiledPromptArtifact(
                prompt_hash=_H64,
                slot_manifest=_make_slot_manifest(),
                template_ids=(),
                fewshot_ids=(),
                injection_ids=(),
                c0_sources=(),
                model_target="gpt-4o",
                policy_hash=None,
                adg_entity_name="CompiledPrompt::test",
                influence_class="C0_INFORMATIONAL",
                timestamp_utc=_TS,
            )

    def test_empty_prompt_hash_raises(self):
        from system_learning.types.prompt_artifact_types import CompiledPromptArtifact

        with pytest.raises(ValueError, match="prompt_hash"):
            CompiledPromptArtifact(
                prompt_hash="",
                slot_manifest=_make_slot_manifest(),
                template_ids=(),
                fewshot_ids=(),
                injection_ids=(),
                c0_sources=(),
                model_target="gpt-4o",
                policy_hash=None,
                adg_entity_name="ADG::CompiledPrompt::test",
                influence_class="C0_INFORMATIONAL",
                timestamp_utc=_TS,
            )

    def test_stable_hash_is_sha256_of_to_json(self):
        a = _make_artifact()
        expected = _sha256(a.to_json())
        assert a.stable_hash() == expected

    def test_stable_hash_deterministic(self):
        a1 = _make_artifact()
        a2 = _make_artifact()
        assert a1.stable_hash() == a2.stable_hash()

    def test_distinct_model_targets_differ_in_hash(self):
        a1 = _make_artifact(model_target="gpt-4o")
        a2 = _make_artifact(model_target="claude-3-5")
        assert a1.stable_hash() != a2.stable_hash()

    def test_to_json_valid_json(self):
        a = _make_artifact()
        parsed = json.loads(a.to_json())
        assert isinstance(parsed, dict)
        assert "prompt_hash" in parsed

    def test_frozen_immutability(self):
        a = _make_artifact()
        with pytest.raises((AttributeError, TypeError)):
            a.model_target = "mutated"


class TestPromptSafetyDecision:
    def _make_allowed(self):
        from system_learning.types.prompt_artifact_types import PromptSafetyDecision

        did = _sha256("decision_allowed")
        return PromptSafetyDecision(
            decision_id=did,
            prompt_hash=_H64,
            allowed=True,
            policy_hash=_H64,
            guardrail_set=("g1", "g2"),
            budget_class="STANDARD",
            denial_reasons=(),
            adg_relation="compiled_prompt_allowed",
            timestamp_utc=_TS,
        )

    def test_allowed_decision_construction(self):
        d = self._make_allowed()
        assert d.allowed is True
        assert len(d.denial_reasons) == 0

    def test_allowed_with_denial_reasons_raises(self):
        from system_learning.types.prompt_artifact_types import PromptSafetyDecision

        with pytest.raises(ValueError, match="denial_reasons must be empty"):
            PromptSafetyDecision(
                decision_id=_H64,
                prompt_hash=_H64,
                allowed=True,
                policy_hash=None,
                guardrail_set=(),
                budget_class="STANDARD",
                denial_reasons=("REASON",),
                adg_relation="compiled_prompt_allowed",
                timestamp_utc=_TS,
            )

    def test_blocked_without_denial_reasons_raises(self):
        from system_learning.types.prompt_artifact_types import PromptSafetyDecision

        with pytest.raises(ValueError, match="must not be empty"):
            PromptSafetyDecision(
                decision_id=_H64,
                prompt_hash=_H64,
                allowed=False,
                policy_hash=None,
                guardrail_set=(),
                budget_class="STANDARD",
                denial_reasons=(),
                adg_relation="compiled_prompt_blocked",
                timestamp_utc=_TS,
            )

    def test_invalid_adg_relation_raises(self):
        from system_learning.types.prompt_artifact_types import PromptSafetyDecision

        with pytest.raises(ValueError, match="adg_relation"):
            PromptSafetyDecision(
                decision_id=_H64,
                prompt_hash=_H64,
                allowed=True,
                policy_hash=None,
                guardrail_set=(),
                budget_class="STANDARD",
                denial_reasons=(),
                adg_relation="invalid_relation",
                timestamp_utc=_TS,
            )

    def test_stable_hash_deterministic(self):
        d = self._make_allowed()
        assert d.stable_hash() == d.stable_hash()


class TestPromptOutcomeRecord:
    def test_construction_succeeds(self):
        r = _make_outcome_record()
        assert r.final_outcome == "SUCCESS"
        assert r.failure_slot == "NONE"

    def test_invalid_final_outcome_raises(self):
        with pytest.raises(ValueError, match="final_outcome"):
            _make_outcome_record(final_outcome="INVALID_OUTCOME")

    def test_invalid_failure_slot_raises(self):
        with pytest.raises(ValueError, match="failure_slot"):
            _make_outcome_record(failure_slot="X9")

    def test_groundedness_out_of_range_raises(self):
        with pytest.raises(ValueError, match="groundedness_score"):
            _make_outcome_record(groundedness=1.5)

    def test_empty_trace_id_raises(self):
        from system_learning.types.prompt_artifact_types import PromptOutcomeRecord

        oid = _sha256("oid")
        with pytest.raises(ValueError, match="trace_id"):
            PromptOutcomeRecord(
                outcome_id=oid,
                prompt_hash=_H64,
                trace_id="",
                route="R",
                model="m",
                groundedness_score=0.5,
                guardrail_hits=(),
                healer_invoked=False,
                healer_id=None,
                hitl_escalation=False,
                replay_status="NOT_TESTED",
                final_outcome="SUCCESS",
                failure_slot="NONE",
                support_score=0.5,
                completeness_score=0.5,
                citation_count=0,
                adg_entity_name=f"ADG::PromptOutcome::{oid[:16]}",
                timestamp_utc=_TS,
            )

    def test_invalid_replay_status_raises(self):
        from system_learning.types.prompt_artifact_types import PromptOutcomeRecord

        oid = _sha256("oid2")
        with pytest.raises(ValueError, match="replay_status"):
            PromptOutcomeRecord(
                outcome_id=oid,
                prompt_hash=_H64,
                trace_id="tr-x",
                route="R",
                model="m",
                groundedness_score=0.5,
                guardrail_hits=(),
                healer_invoked=False,
                healer_id=None,
                hitl_escalation=False,
                replay_status="MAYBE",
                final_outcome="SUCCESS",
                failure_slot="NONE",
                support_score=0.5,
                completeness_score=0.5,
                citation_count=0,
                adg_entity_name=f"ADG::PromptOutcome::{oid[:16]}",
                timestamp_utc=_TS,
            )

    def test_stable_hash_is_sha256_of_to_json(self):
        r = _make_outcome_record()
        expected = _sha256(r.to_json())
        assert r.stable_hash() == expected


class TestPreferenceRecord:
    def _make_preference(self, decision="ACCEPTED", patch=None):
        from system_learning.types.prompt_artifact_types import PreferenceRecord

        pid = _sha256("pref" + decision)
        return PreferenceRecord(
            preference_id=pid,
            prompt_hash=_H64,
            trace_id="tr-001",
            proposal_summary="Model said X",
            human_patch=patch,
            decision=decision,
            outcome="SUCCESS",
            adg_entity_name=f"ADG::PreferenceRecord::{pid[:16]}",
            timestamp_utc=_TS,
        )

    def test_accepted_without_patch_succeeds(self):
        r = self._make_preference(decision="ACCEPTED")
        assert r.decision == "ACCEPTED"

    def test_modified_without_patch_raises(self):
        with pytest.raises(ValueError, match="human_patch"):
            self._make_preference(decision="MODIFIED", patch=None)

    def test_modified_with_patch_succeeds(self):
        r = self._make_preference(decision="MODIFIED", patch="corrected text")
        assert r.human_patch == "corrected text"

    def test_invalid_decision_raises(self):
        from system_learning.types.prompt_artifact_types import PreferenceRecord

        pid = _sha256("bad")
        with pytest.raises(ValueError, match="decision"):
            PreferenceRecord(
                preference_id=pid,
                prompt_hash=_H64,
                trace_id="tr-001",
                proposal_summary="X",
                human_patch=None,
                decision="INVALID",
                outcome="SUCCESS",
                adg_entity_name=f"ADG::PreferenceRecord::{pid[:16]}",
                timestamp_utc=_TS,
            )

    def test_stable_hash_deterministic(self):
        r = self._make_preference()
        assert r.stable_hash() == r.stable_hash()


class TestPromptDriftSignal:
    def _make_signal(self, drift_type="GROUNDEDNESS_DROP", adg_rel=None):
        from system_learning.types.prompt_artifact_types import PromptDriftSignal

        sid = _sha256("sig" + drift_type)
        return PromptDriftSignal(
            signal_id=sid,
            prompt_hash_before=_H64,
            prompt_hash_after=_H64b,
            drift_type=drift_type,
            magnitude=-0.1,
            affected_slot="C0",
            baseline_window_size=20,
            current_window_size=20,
            adg_relation=adg_rel or "prompt_prompt_regression_detected",
            timestamp_utc=_TS,
        )

    def test_construction_succeeds(self):
        s = self._make_signal()
        assert s.drift_type == "GROUNDEDNESS_DROP"

    def test_invalid_drift_type_raises(self):
        with pytest.raises(ValueError, match="drift_type"):
            self._make_signal(drift_type="BAD_DRIFT")

    def test_invalid_adg_relation_raises(self):
        with pytest.raises(ValueError, match="adg_relation"):
            self._make_signal(adg_rel="bad_relation")

    def test_current_window_size_zero_raises(self):
        from system_learning.types.prompt_artifact_types import PromptDriftSignal

        sid = _sha256("sig_bad")
        with pytest.raises(ValueError, match="current_window_size"):
            PromptDriftSignal(
                signal_id=sid,
                prompt_hash_before=_H64,
                prompt_hash_after=_H64b,
                drift_type="GROUNDEDNESS_DROP",
                magnitude=-0.1,
                affected_slot=None,
                baseline_window_size=10,
                current_window_size=0,
                adg_relation="prompt_prompt_regression_detected",
                timestamp_utc=_TS,
            )

    def test_stable_hash_deterministic(self):
        s = self._make_signal()
        assert s.stable_hash() == s.stable_hash()


# ===========================================================================
# 2. ADG relation constants
# ===========================================================================


class TestPromptADGRelations:
    def test_all_relation_sets_are_frozensets(self):
        from system_learning.types import prompt_adg_relations as rel

        for attr in (
            "PROVENANCE_RELATIONS",
            "SAFETY_RELATIONS",
            "EXECUTION_RELATIONS",
            "OUTCOME_RELATIONS",
            "RETRIEVAL_RELATIONS",
            "DRIFT_RELATIONS",
            "OPTIMIZATION_RELATIONS",
            "BUDGET_RELATIONS",
            "HITL_RELATIONS",
            "ALL_PROMPT_RELATIONS",
        ):
            obj = getattr(rel, attr)
            assert isinstance(obj, frozenset), f"{attr} is not a frozenset"

    def test_all_prompt_relations_is_union_of_all_families(self):
        from system_learning.types import prompt_adg_relations as rel

        union = (
            rel.PROVENANCE_RELATIONS
            | rel.SAFETY_RELATIONS
            | rel.EXECUTION_RELATIONS
            | rel.OUTCOME_RELATIONS
            | rel.RETRIEVAL_RELATIONS
            | rel.DRIFT_RELATIONS
            | rel.OPTIMIZATION_RELATIONS
            | rel.BUDGET_RELATIONS
            | rel.HITL_RELATIONS
        )
        assert union == rel.ALL_PROMPT_RELATIONS

    def test_provenance_has_all_9_slot_relations(self):
        from system_learning.types import prompt_adg_relations as rel

        expected = {
            rel.PROVENANCE_TEMPLATE_USED_BY,
            rel.PROVENANCE_FEWSHOT_USED_BY,
            rel.PROVENANCE_INSTRUCTION_INJECTION_SOURCE,
            rel.PROVENANCE_C0_CONTEXT_SOURCE,
            rel.PROVENANCE_USES_S0_RULE,
            rel.PROVENANCE_USES_D0_FENCE,
            rel.PROVENANCE_USES_I0_INSTRUCTION,
            rel.PROVENANCE_USES_C0_CONTEXT,
            rel.PROVENANCE_CONTAINS_U0_INPUT,
        }
        assert expected == rel.PROVENANCE_RELATIONS

    def test_safety_has_5_relations(self):
        from system_learning.types import prompt_adg_relations as rel

        assert len(rel.SAFETY_RELATIONS) == 5

    def test_outcome_has_6_relations(self):
        from system_learning.types import prompt_adg_relations as rel

        assert len(rel.OUTCOME_RELATIONS) == 6

    def test_no_duplicate_across_families(self):
        from system_learning.types import prompt_adg_relations as rel

        families = [
            rel.PROVENANCE_RELATIONS,
            rel.SAFETY_RELATIONS,
            rel.EXECUTION_RELATIONS,
            rel.OUTCOME_RELATIONS,
            rel.RETRIEVAL_RELATIONS,
            rel.DRIFT_RELATIONS,
            rel.OPTIMIZATION_RELATIONS,
            rel.BUDGET_RELATIONS,
            rel.HITL_RELATIONS,
        ]
        total = sum(len(f) for f in families)
        assert total == len(rel.ALL_PROMPT_RELATIONS), (
            f"Duplicate relations detected: {total} total vs {len(rel.ALL_PROMPT_RELATIONS)} unique"
        )

    def test_all_relation_strings_are_snake_case(self):
        from system_learning.types import prompt_adg_relations as rel

        for r in rel.ALL_PROMPT_RELATIONS:
            assert r == r.lower(), f"Relation not lowercase: {r!r}"
            assert " " not in r, f"Relation has spaces: {r!r}"
