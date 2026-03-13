"""Comprehensive tests for the ADG-backed prompt provenance and learning system.

Covers all seven components introduced by the WINDSURF ADDENDUM:

  1.  prompt_artifact_types.py     — type construction, invariants, hashing
  2.  prompt_adg_relations.py      — relation constant completeness
  3.  prompt_provenance_builder.py — artifact assembly, provenance relations, budget
  4.  prompt_safety_validator.py   — safety gates, decision invariants
  5.  prompt_execution_tracer.py   — execution/outcome records, ADG relations
  6.  prompt_drift_detector.py     — drift signals, threshold logic
  7.  prompt_outcome_bus_adapter.py — PromptOutcomeRecord → TraceFeatureRecord bridge

Test philosophy
---------------
- All tests are deterministic (no random, no wall-clock).
- Every type's stable_hash() is verified as SHA-256(to_json()).
- All ADG relations produced have from/to entities starting with ADG::.
- Integration path: build → validate → execute → drift → adapt → bus.
"""

from __future__ import annotations

import hashlib
import json

import pytest

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
        s0_hash=s0, d0_hash=d0, i0_hash=i0, c0_hash=c0, u0_hash=u0,
        s0_tokens=100, d0_tokens=80, i0_tokens=100, c0_tokens=160, u0_tokens=72,
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
        PromptBuildRequest, SlotPayload,
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
                s0_hash=_H64, d0_hash=_H64, i0_hash=_H64, c0_hash=_H64, u0_hash=_H64,
                s0_tokens=1, d0_tokens=1, i0_tokens=1, c0_tokens=1, u0_tokens=1,
                total_tokens=5, budget_class="INVALID",
            )

    def test_negative_token_count_raises(self):
        from system_learning.types.prompt_artifact_types import PromptSlotManifest

        with pytest.raises(ValueError, match="s0_tokens"):
            PromptSlotManifest(
                s0_hash=_H64, d0_hash=_H64, i0_hash=_H64, c0_hash=_H64, u0_hash=_H64,
                s0_tokens=-1, d0_tokens=1, i0_tokens=1, c0_tokens=1, u0_tokens=1,
                total_tokens=3, budget_class="COMPACT",
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
        for key in ("s0_hash", "d0_hash", "i0_hash", "c0_hash", "u0_hash",
                    "s0_tokens", "d0_tokens", "i0_tokens", "c0_tokens", "u0_tokens",
                    "total_tokens", "budget_class"):
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
                template_ids=(), fewshot_ids=(), injection_ids=(), c0_sources=(),
                model_target="gpt-4o", policy_hash=None,
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
                template_ids=(), fewshot_ids=(), injection_ids=(), c0_sources=(),
                model_target="gpt-4o", policy_hash=None,
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
                template_ids=(), fewshot_ids=(), injection_ids=(), c0_sources=(),
                model_target="gpt-4o", policy_hash=None,
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
                decision_id=_H64, prompt_hash=_H64,
                allowed=True, policy_hash=None,
                guardrail_set=(), budget_class="STANDARD",
                denial_reasons=("REASON",),
                adg_relation="compiled_prompt_allowed",
                timestamp_utc=_TS,
            )

    def test_blocked_without_denial_reasons_raises(self):
        from system_learning.types.prompt_artifact_types import PromptSafetyDecision

        with pytest.raises(ValueError, match="must not be empty"):
            PromptSafetyDecision(
                decision_id=_H64, prompt_hash=_H64,
                allowed=False, policy_hash=None,
                guardrail_set=(), budget_class="STANDARD",
                denial_reasons=(),
                adg_relation="compiled_prompt_blocked",
                timestamp_utc=_TS,
            )

    def test_invalid_adg_relation_raises(self):
        from system_learning.types.prompt_artifact_types import PromptSafetyDecision

        with pytest.raises(ValueError, match="adg_relation"):
            PromptSafetyDecision(
                decision_id=_H64, prompt_hash=_H64,
                allowed=True, policy_hash=None,
                guardrail_set=(), budget_class="STANDARD",
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
                outcome_id=oid, prompt_hash=_H64, trace_id="",
                route="R", model="m", groundedness_score=0.5,
                guardrail_hits=(), healer_invoked=False, healer_id=None,
                hitl_escalation=False, replay_status="NOT_TESTED",
                final_outcome="SUCCESS", failure_slot="NONE",
                support_score=0.5, completeness_score=0.5, citation_count=0,
                adg_entity_name=f"ADG::PromptOutcome::{oid[:16]}",
                timestamp_utc=_TS,
            )

    def test_invalid_replay_status_raises(self):
        from system_learning.types.prompt_artifact_types import PromptOutcomeRecord

        oid = _sha256("oid2")
        with pytest.raises(ValueError, match="replay_status"):
            PromptOutcomeRecord(
                outcome_id=oid, prompt_hash=_H64, trace_id="tr-x",
                route="R", model="m", groundedness_score=0.5,
                guardrail_hits=(), healer_invoked=False, healer_id=None,
                hitl_escalation=False, replay_status="MAYBE",
                final_outcome="SUCCESS", failure_slot="NONE",
                support_score=0.5, completeness_score=0.5, citation_count=0,
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
            preference_id=pid, prompt_hash=_H64, trace_id="tr-001",
            proposal_summary="Model said X", human_patch=patch,
            decision=decision, outcome="SUCCESS",
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
                preference_id=pid, prompt_hash=_H64, trace_id="tr-001",
                proposal_summary="X", human_patch=None,
                decision="INVALID", outcome="SUCCESS",
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
                signal_id=sid, prompt_hash_before=_H64, prompt_hash_after=_H64b,
                drift_type="GROUNDEDNESS_DROP", magnitude=-0.1,
                affected_slot=None, baseline_window_size=10, current_window_size=0,
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

        for attr in ("PROVENANCE_RELATIONS", "SAFETY_RELATIONS", "EXECUTION_RELATIONS",
                     "OUTCOME_RELATIONS", "RETRIEVAL_RELATIONS", "DRIFT_RELATIONS",
                     "OPTIMIZATION_RELATIONS", "BUDGET_RELATIONS", "HITL_RELATIONS",
                     "ALL_PROMPT_RELATIONS"):
            obj = getattr(rel, attr)
            assert isinstance(obj, frozenset), f"{attr} is not a frozenset"

    def test_all_prompt_relations_is_union_of_all_families(self):
        from system_learning.types import prompt_adg_relations as rel

        union = (
            rel.PROVENANCE_RELATIONS | rel.SAFETY_RELATIONS | rel.EXECUTION_RELATIONS |
            rel.OUTCOME_RELATIONS | rel.RETRIEVAL_RELATIONS | rel.DRIFT_RELATIONS |
            rel.OPTIMIZATION_RELATIONS | rel.BUDGET_RELATIONS | rel.HITL_RELATIONS
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
            rel.PROVENANCE_RELATIONS, rel.SAFETY_RELATIONS, rel.EXECUTION_RELATIONS,
            rel.OUTCOME_RELATIONS, rel.RETRIEVAL_RELATIONS, rel.DRIFT_RELATIONS,
            rel.OPTIMIZATION_RELATIONS, rel.BUDGET_RELATIONS, rel.HITL_RELATIONS,
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


# ===========================================================================
# 3. PromptProvenanceBuilder
# ===========================================================================


class TestPromptProvenanceBuilder:

    def test_build_produces_artifact_and_relations(self):
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt

        req = _make_build_request()
        result = build_compiled_prompt(req)
        assert result.artifact.influence_class == "C0_INFORMATIONAL"
        assert len(result.adg_relations) > 0

    def test_artifact_adg_entity_starts_with_adg(self):
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt

        result = build_compiled_prompt(_make_build_request())
        assert result.artifact.adg_entity_name.startswith("ADG::")

    def test_all_relations_have_adg_from_and_to(self):
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt

        result = build_compiled_prompt(_make_build_request())
        for (frm, rel, to) in result.adg_relations:
            # from entity may be a source ID (template/fewshot/chunk) which
            # may or may not start with ADG:: — but to must start with ADG::
            # (provenance sources are external IDs)
            assert isinstance(rel, str) and rel
            assert to.startswith("ADG::"), f"To entity {to!r} doesn't start with ADG::"

    def test_slot_provenance_relations_emitted(self):
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt
        from system_learning.types.prompt_adg_relations import (
            PROVENANCE_USES_S0_RULE, PROVENANCE_USES_D0_FENCE,
            PROVENANCE_USES_I0_INSTRUCTION, PROVENANCE_USES_C0_CONTEXT,
            PROVENANCE_CONTAINS_U0_INPUT,
        )

        result = build_compiled_prompt(_make_build_request())
        rel_types = {r for (_, r, _) in result.adg_relations}
        assert PROVENANCE_USES_S0_RULE in rel_types
        assert PROVENANCE_USES_D0_FENCE in rel_types
        assert PROVENANCE_USES_I0_INSTRUCTION in rel_types
        assert PROVENANCE_USES_C0_CONTEXT in rel_types
        assert PROVENANCE_CONTAINS_U0_INPUT in rel_types

    def test_template_used_by_relation_emitted(self):
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt
        from system_learning.types.prompt_adg_relations import PROVENANCE_TEMPLATE_USED_BY

        result = build_compiled_prompt(_make_build_request(template_ids=("tmpl-A",)))
        rels = [(f, r, t) for (f, r, t) in result.adg_relations if r == PROVENANCE_TEMPLATE_USED_BY]
        assert len(rels) == 1
        assert rels[0][0] == "tmpl-A"

    def test_fewshot_used_by_relation_emitted_for_each_id(self):
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt
        from system_learning.types.prompt_adg_relations import PROVENANCE_FEWSHOT_USED_BY

        result = build_compiled_prompt(_make_build_request(fewshot_ids=("fs-1", "fs-2", "fs-3")))
        fs_rels = [(f, r, t) for (f, r, t) in result.adg_relations if r == PROVENANCE_FEWSHOT_USED_BY]
        assert len(fs_rels) == 3

    def test_budget_token_profile_relation_emitted(self):
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt
        from system_learning.types.prompt_adg_relations import BUDGET_TOKEN_PROFILE

        result = build_compiled_prompt(_make_build_request())
        rel_types = {r for (_, r, _) in result.adg_relations}
        assert BUDGET_TOKEN_PROFILE in rel_types

    def test_overflow_budget_emits_exceeded_relation(self):
        from system_learning.engines.prompt_provenance_builder import (
            PromptProvenanceBuilder, PromptBuildRequest, SlotPayload,
        )
        from system_learning.types.prompt_adg_relations import BUDGET_EXCEEDED

        # Use custom tokenizer that always returns 3000 per slot → total 15000 > 8192
        builder = PromptProvenanceBuilder(tokenizer=lambda _: 3000)
        req = PromptBuildRequest(
            s0=SlotPayload("s"), d0=SlotPayload("d"), i0=SlotPayload("i"),
            c0=SlotPayload("c"), u0=SlotPayload("u"),
            template_ids=(), fewshot_ids=(), injection_ids=(),
            model_target="gpt-4o", policy_hash=None,
            adg_entity_prefix="ADG::CompiledPrompt",
            timestamp_utc=_TS,
        )
        result = builder.build(req)
        rel_types = {r for (_, r, _) in result.adg_relations}
        assert BUDGET_EXCEEDED in rel_types
        assert result.artifact.slot_manifest.budget_class == "OVERFLOW"

    def test_compact_budget_no_truncated_or_exceeded(self):
        from system_learning.engines.prompt_provenance_builder import (
            PromptProvenanceBuilder, PromptBuildRequest, SlotPayload,
        )
        from system_learning.types.prompt_adg_relations import BUDGET_EXCEEDED, BUDGET_TRUNCATED

        builder = PromptProvenanceBuilder(tokenizer=lambda _: 10)
        req = PromptBuildRequest(
            s0=SlotPayload("s"), d0=SlotPayload("d"), i0=SlotPayload("i"),
            c0=SlotPayload("c"), u0=SlotPayload("u"),
            template_ids=(), fewshot_ids=(), injection_ids=(),
            model_target="gpt-4o", policy_hash=None,
            adg_entity_prefix="ADG::CompiledPrompt",
            timestamp_utc=_TS,
        )
        result = builder.build(req)
        rel_types = {r for (_, r, _) in result.adg_relations}
        assert BUDGET_EXCEEDED not in rel_types
        assert BUDGET_TRUNCATED not in rel_types
        assert result.artifact.slot_manifest.budget_class == "COMPACT"

    def test_same_request_twice_same_artifact_hash(self):
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt

        req = _make_build_request()
        r1 = build_compiled_prompt(req)
        r2 = build_compiled_prompt(req)
        assert r1.artifact.stable_hash() == r2.artifact.stable_hash()

    def test_different_s0_content_different_prompt_hash(self):
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt

        r1 = build_compiled_prompt(_make_build_request(s0="Role A"))
        r2 = build_compiled_prompt(_make_build_request(s0="Role B"))
        assert r1.artifact.prompt_hash != r2.artifact.prompt_hash

    def test_c0_source_ids_merged_with_c0_hash(self):
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt, SlotPayload, PromptBuildRequest

        req = PromptBuildRequest(
            s0=SlotPayload("s"), d0=SlotPayload("d"), i0=SlotPayload("i"),
            c0=SlotPayload("context", source_ids=("src-abc", "src-def")),
            u0=SlotPayload("u"),
            template_ids=(), fewshot_ids=(), injection_ids=(),
            model_target="m", policy_hash=None,
            adg_entity_prefix="ADG::CompiledPrompt",
            timestamp_utc=_TS,
        )
        result = build_compiled_prompt(req)
        # c0_sources must include the two explicit source IDs + the c0 hash itself
        assert "src-abc" in result.artifact.c0_sources
        assert "src-def" in result.artifact.c0_sources


# ===========================================================================
# 4. PromptSafetyValidator
# ===========================================================================


class TestPromptSafetyValidator:

    def test_no_config_allows_any_artifact(self):
        from system_learning.engines.prompt_safety_validator import validate_prompt

        artifact = _make_artifact()
        decision, rels = validate_prompt(artifact, _TS)
        assert decision.allowed is True
        assert decision.adg_relation == "compiled_prompt_allowed"

    def test_policy_mismatch_blocks(self):
        from system_learning.engines.prompt_safety_validator import (
            PromptSafetyValidator, SafetyValidatorConfig,
        )

        artifact = _make_artifact(policy_hash="hash_A")
        cfg = SafetyValidatorConfig(active_policy_hash="hash_B")
        validator = PromptSafetyValidator(cfg)
        decision, _ = validator.validate(artifact, _TS)
        assert decision.allowed is False
        assert "POLICY_HASH_MISMATCH" in decision.denial_reasons

    def test_policy_match_allows(self):
        from system_learning.engines.prompt_safety_validator import (
            PromptSafetyValidator, SafetyValidatorConfig,
        )

        ph = _sha256("policy")
        artifact = _make_artifact(policy_hash=ph)
        cfg = SafetyValidatorConfig(active_policy_hash=ph)
        decision, _ = PromptSafetyValidator(cfg).validate(artifact, _TS)
        assert decision.allowed is True

    def test_overflow_budget_always_blocked(self):
        from system_learning.engines.prompt_safety_validator import validate_prompt

        artifact = _make_artifact(budget_class="OVERFLOW", total_tokens=10000)
        decision, _ = validate_prompt(artifact, _TS)
        assert decision.allowed is False
        assert "BUDGET_OVERFLOW" in decision.denial_reasons

    def test_extended_budget_allowed_by_default(self):
        from system_learning.engines.prompt_safety_validator import validate_prompt

        artifact = _make_artifact(budget_class="EXTENDED", total_tokens=6000)
        decision, _ = validate_prompt(artifact, _TS)
        assert decision.allowed is True

    def test_extended_budget_blocked_when_configured(self):
        from system_learning.engines.prompt_safety_validator import (
            PromptSafetyValidator, SafetyValidatorConfig,
        )

        artifact = _make_artifact(budget_class="EXTENDED", total_tokens=6000)
        cfg = SafetyValidatorConfig(block_on_extended=True)
        decision, _ = PromptSafetyValidator(cfg).validate(artifact, _TS)
        assert decision.allowed is False
        assert "BUDGET_EXTENDED_BLOCKED" in decision.denial_reasons

    def test_all_5_safety_relations_emitted(self):
        from system_learning.engines.prompt_safety_validator import (
            PromptSafetyValidator, SafetyValidatorConfig,
        )
        from system_learning.types.prompt_adg_relations import (
            SAFETY_VALIDATED_BY_POLICY, SAFETY_CHECKED_BY_GUARDRAIL,
            SAFETY_BUDGET_CHECKED, SAFETY_ALLOWED, SAFETY_BLOCKED,
        )

        artifact = _make_artifact()
        decision, rels = PromptSafetyValidator().validate(artifact, _TS)
        rel_types = {r for (_, r, _) in rels}
        assert SAFETY_VALIDATED_BY_POLICY in rel_types
        assert SAFETY_CHECKED_BY_GUARDRAIL in rel_types
        assert SAFETY_BUDGET_CHECKED in rel_types
        assert (SAFETY_ALLOWED if decision.allowed else SAFETY_BLOCKED) in rel_types

    def test_decision_id_deterministic(self):
        from system_learning.engines.prompt_safety_validator import validate_prompt

        artifact = _make_artifact()
        d1, _ = validate_prompt(artifact, _TS)
        d2, _ = validate_prompt(artifact, _TS)
        assert d1.decision_id == d2.decision_id

    def test_blocked_uses_blocked_adg_relation(self):
        from system_learning.engines.prompt_safety_validator import validate_prompt

        artifact = _make_artifact(budget_class="OVERFLOW", total_tokens=9999)
        decision, rels = validate_prompt(artifact, _TS)
        assert decision.adg_relation == "compiled_prompt_blocked"
        blocked_rels = [(f, r, t) for (f, r, t) in rels if r == "compiled_prompt_blocked"]
        assert len(blocked_rels) == 1

    def test_policy_mismatch_warning_only_when_configured(self):
        from system_learning.engines.prompt_safety_validator import (
            PromptSafetyValidator, SafetyValidatorConfig,
        )

        artifact = _make_artifact(policy_hash="hash_A")
        cfg = SafetyValidatorConfig(
            active_policy_hash="hash_B",
            block_on_policy_mismatch=False,
        )
        decision, _ = PromptSafetyValidator(cfg).validate(artifact, _TS)
        # Mismatch is not blocking
        assert decision.allowed is True


# ===========================================================================
# 5. PromptExecutionTracer
# ===========================================================================


class TestPromptExecutionTracer:

    def _signal(self, **kwargs):
        base = {
            "route_selected": "PATH_A",
            "model_id": "gpt-4o",
            "latency_ms": 350,
            "input_tokens": 512,
            "output_tokens": 200,
            "retrieval_path": "RAG_BGE",
            "retrieval_groundedness_score": 0.88,
            "success": True,
        }
        base.update(kwargs)
        return base

    def test_trace_produces_execution_and_outcome_record(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        result = trace_execution(_H64, "tr-001", self._signal(), _TS)
        assert result.execution_record.trace_id == "tr-001"
        assert result.execution_record.prompt_hash == _H64
        assert result.outcome_record.final_outcome == "SUCCESS"

    def test_success_outcome_from_success_signal(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        result = trace_execution(_H64, "tr-001", self._signal(success=True), _TS)
        assert result.outcome_record.final_outcome == "SUCCESS"

    def test_escalated_outcome_from_hitl_flag(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        result = trace_execution(_H64, "tr-002", self._signal(
            human_escalation_flag=True, success=True,
        ), _TS)
        assert result.outcome_record.final_outcome == "ESCALATED"
        assert result.outcome_record.hitl_escalation is True

    def test_replay_failure_outcome(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        result = trace_execution(_H64, "tr-003", self._signal(
            replay_failed=True, success=False,
        ), _TS)
        assert result.outcome_record.final_outcome == "REPLAY_FAILURE"
        assert result.outcome_record.replay_status == "FAILED"

    def test_healed_success_outcome(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        result = trace_execution(_H64, "tr-004", self._signal(
            healing_invoked=True, healed=True, success=True,
        ), _TS)
        assert result.outcome_record.final_outcome == "HEALED_SUCCESS"
        assert result.outcome_record.healer_invoked is True

    def test_replay_passed_status(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        result = trace_execution(_H64, "tr-005", self._signal(
            replay_passed=True,
        ), _TS)
        assert result.outcome_record.replay_status == "PASSED"

    def test_execution_relations_emitted(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.types.prompt_adg_relations import (
            EXECUTION_ROUTES_TO, EXECUTION_EXECUTED_BY_MODEL, EXECUTION_GENERATES_TRACE,
        )

        result = trace_execution(_H64, "tr-006", self._signal(), _TS)
        rel_types = {r for (_, r, _) in result.adg_relations}
        assert EXECUTION_ROUTES_TO in rel_types
        assert EXECUTION_EXECUTED_BY_MODEL in rel_types
        assert EXECUTION_GENERATES_TRACE in rel_types

    def test_outcome_produced_answer_for_success(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.types.prompt_adg_relations import OUTCOME_PRODUCED_ANSWER

        result = trace_execution(_H64, "tr-007", self._signal(success=True), _TS)
        rel_types = {r for (_, r, _) in result.adg_relations}
        assert OUTCOME_PRODUCED_ANSWER in rel_types

    def test_hitl_escalation_emits_hitl_relations(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.types.prompt_adg_relations import (
            OUTCOME_ESCALATED_HITL, HITL_CAUSED_ESCALATION,
        )

        result = trace_execution(_H64, "tr-008", self._signal(
            human_escalation_flag=True,
        ), _TS)
        rel_types = {r for (_, r, _) in result.adg_relations}
        assert OUTCOME_ESCALATED_HITL in rel_types
        assert HITL_CAUSED_ESCALATION in rel_types

    def test_healer_triggers_healer_relation(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.types.prompt_adg_relations import OUTCOME_TRIGGERED_HEALER

        result = trace_execution(_H64, "tr-009", self._signal(
            healing_invoked=True, healer_id="healer_X", success=True, healed=True,
        ), _TS)
        rel_types = {r for (_, r, _) in result.adg_relations}
        assert OUTCOME_TRIGGERED_HEALER in rel_types

    def test_retrieval_relations_emitted(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.types.prompt_adg_relations import (
            RETRIEVAL_RETRIEVES_VIA, RETRIEVAL_SCORES_GROUNDEDNESS,
        )

        result = trace_execution(_H64, "tr-010", self._signal(), _TS)
        rel_types = {r for (_, r, _) in result.adg_relations}
        assert RETRIEVAL_RETRIEVES_VIA in rel_types
        assert RETRIEVAL_SCORES_GROUNDEDNESS in rel_types

    def test_chunk_ids_emit_uses_chunk_relations(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.types.prompt_adg_relations import RETRIEVAL_USES_CHUNK

        result = trace_execution(_H64, "tr-011", self._signal(
            chunk_ids=["chunk-A", "chunk-B", "chunk-C"],
        ), _TS)
        chunk_rels = [(f, r, t) for (f, r, t) in result.adg_relations if r == RETRIEVAL_USES_CHUNK]
        assert len(chunk_rels) == 3

    def test_empty_signal_produces_unknown_outcome(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        result = trace_execution(_H64, "tr-012", {}, _TS)
        assert result.outcome_record.final_outcome == "UNKNOWN"

    def test_failure_slot_guardrail_hits_maps_to_d0(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        result = trace_execution(_H64, "tr-013", self._signal(
            success=False,
            guardrail_hits=["guardrail_1"],
        ), _TS)
        assert result.outcome_record.failure_slot == "D0"

    def test_batch_trace_sorted_by_execution_id(self):
        from system_learning.engines.prompt_execution_tracer import PromptExecutionTracer

        tracer = PromptExecutionTracer()
        executions = [
            (_H64, f"tr-{i:03d}", self._signal(), _TS + i)
            for i in range(10)
        ]
        results = tracer.trace_batch(executions)
        ids = [r.execution_record.execution_id for r in results]
        assert ids == sorted(ids)

    def test_execution_id_deterministic(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        r1 = trace_execution(_H64, "tr-det", self._signal(), _TS)
        r2 = trace_execution(_H64, "tr-det", self._signal(), _TS)
        assert r1.execution_record.execution_id == r2.execution_record.execution_id


# ===========================================================================
# 6. PromptDriftDetector
# ===========================================================================


class TestPromptDriftDetector:

    def _make_window(self, n, hitl_rate=0.0, gnd=0.8, replay_fail_rate=0.0, guard_hit_rate=0.0):
        records = []
        for i in range(n):
            hitl = i < int(n * hitl_rate)
            replay = "FAILED" if i < int(n * replay_fail_rate) else "NOT_TESTED"
            guard = ("g1",) if i < int(n * guard_hit_rate) else ()
            records.append(_make_outcome_record(
                trace_id=f"tr-{id(records)}-{i}",
                groundedness=gnd,
                hitl=hitl,
                guardrail_hits=guard,
                replay_status=replay,
            ))
        return records

    def test_no_drift_produces_no_signals(self):
        from system_learning.engines.prompt_drift_detector import detect_prompt_drift

        baseline = self._make_window(20, hitl_rate=0.1, gnd=0.8)
        current = self._make_window(20, hitl_rate=0.1, gnd=0.8)
        signals = detect_prompt_drift(baseline, current, _H64, _H64b, _TS)
        # Only version_replaced_by when hashes differ
        sig_types = {s.drift_type for s in signals}
        assert "ESCALATION_RATE_INCREASE" not in sig_types
        assert "GROUNDEDNESS_DROP" not in sig_types

    def test_groundedness_drop_detected(self):
        from system_learning.engines.prompt_drift_detector import detect_prompt_drift

        baseline = self._make_window(20, gnd=0.9)
        current = self._make_window(20, gnd=0.7)
        signals = detect_prompt_drift(baseline, current, _H64, _H64b, _TS)
        drift_types = {s.drift_type for s in signals}
        assert "GROUNDEDNESS_DROP" in drift_types

    def test_escalation_increase_detected(self):
        from system_learning.engines.prompt_drift_detector import detect_prompt_drift

        baseline = self._make_window(20, hitl_rate=0.0)
        current = self._make_window(20, hitl_rate=0.4)
        signals = detect_prompt_drift(baseline, current, _H64, _H64b, _TS)
        drift_types = {s.drift_type for s in signals}
        assert "ESCALATION_RATE_INCREASE" in drift_types

    def test_replay_instability_detected(self):
        from system_learning.engines.prompt_drift_detector import detect_prompt_drift

        baseline = self._make_window(20, replay_fail_rate=0.0)
        current = self._make_window(20, replay_fail_rate=0.4)
        signals = detect_prompt_drift(baseline, current, _H64, _H64b, _TS)
        drift_types = {s.drift_type for s in signals}
        assert "REPLAY_INSTABILITY" in drift_types

    def test_guardrail_violation_increase_detected(self):
        from system_learning.engines.prompt_drift_detector import detect_prompt_drift

        baseline = self._make_window(20, guard_hit_rate=0.0)
        current = self._make_window(20, guard_hit_rate=0.5)
        signals = detect_prompt_drift(baseline, current, _H64, _H64b, _TS)
        drift_types = {s.drift_type for s in signals}
        assert "GUARDRAIL_VIOLATION_INCREASE" in drift_types

    def test_improvement_detected_when_groundedness_rises(self):
        from system_learning.engines.prompt_drift_detector import detect_prompt_drift

        baseline = self._make_window(20, gnd=0.5)
        current = self._make_window(20, gnd=0.9)
        signals = detect_prompt_drift(baseline, current, _H64, _H64b, _TS)
        drift_types = {s.drift_type for s in signals}
        assert "IMPROVEMENT_DETECTED" in drift_types

    def test_empty_current_window_produces_no_signals(self):
        from system_learning.engines.prompt_drift_detector import detect_prompt_drift

        baseline = self._make_window(10)
        signals = detect_prompt_drift(baseline, [], _H64, _H64b, _TS)
        assert signals == []

    def test_version_replaced_by_emitted_when_hashes_differ(self):
        from system_learning.engines.prompt_drift_detector import detect_prompt_drift
        from system_learning.types.prompt_adg_relations import DRIFT_VERSION_REPLACED_BY

        baseline = self._make_window(5, gnd=0.8)
        current = self._make_window(5, gnd=0.8)
        signals = detect_prompt_drift(baseline, current, _H64, _H64b, _TS)
        rel_types = {s.adg_relation for s in signals}
        assert DRIFT_VERSION_REPLACED_BY in rel_types

    def test_no_version_replaced_by_when_same_hash(self):
        from system_learning.engines.prompt_drift_detector import detect_prompt_drift
        from system_learning.types.prompt_adg_relations import DRIFT_VERSION_REPLACED_BY

        baseline = self._make_window(5, gnd=0.8)
        current = self._make_window(5, gnd=0.8)
        signals = detect_prompt_drift(baseline, current, _H64, _H64, _TS)
        rel_types = {s.adg_relation for s in signals}
        assert DRIFT_VERSION_REPLACED_BY not in rel_types

    def test_signal_ids_deterministic(self):
        from system_learning.engines.prompt_drift_detector import detect_prompt_drift

        baseline = self._make_window(10, gnd=0.9)
        current = self._make_window(10, gnd=0.7)
        s1 = detect_prompt_drift(baseline, current, _H64, _H64b, _TS)
        s2 = detect_prompt_drift(baseline, current, _H64, _H64b, _TS)
        assert [s.signal_id for s in s1] == [s.signal_id for s in s2]

    def test_template_supersession_emits_correct_relation(self):
        from system_learning.engines.prompt_drift_detector import PromptDriftDetector
        from system_learning.types.prompt_adg_relations import DRIFT_TEMPLATE_SUPERSEDED

        detector = PromptDriftDetector()
        sig = detector.detect_template_supersession(_H64, _H64b, _TS)
        assert sig.adg_relation == DRIFT_TEMPLATE_SUPERSEDED

    def test_regression_signals_use_regression_adg_relation(self):
        from system_learning.engines.prompt_drift_detector import detect_prompt_drift
        from system_learning.types.prompt_adg_relations import DRIFT_REGRESSION_DETECTED

        baseline = self._make_window(20, gnd=0.9)
        current = self._make_window(20, gnd=0.7)
        signals = detect_prompt_drift(baseline, current, _H64, _H64b, _TS)
        regression_sigs = [s for s in signals if s.adg_relation == DRIFT_REGRESSION_DETECTED]
        assert len(regression_sigs) >= 1

    def test_custom_threshold_filters_small_changes(self):
        from system_learning.engines.prompt_drift_detector import (
            PromptDriftDetector, DriftDetectorConfig,
        )

        # Very high threshold — small gnd change (0.03) should not trigger
        cfg = DriftDetectorConfig(groundedness_threshold=0.20)
        detector = PromptDriftDetector(cfg)
        baseline = self._make_window(20, gnd=0.80)
        current = self._make_window(20, gnd=0.77)
        signals = detector.detect(baseline, current, _H64, _H64b, _TS)
        drift_types = {s.drift_type for s in signals}
        assert "GROUNDEDNESS_DROP" not in drift_types


# ===========================================================================
# 7. PromptOutcomeBusAdapter
# ===========================================================================


class TestPromptOutcomeBusAdapter:

    def test_convert_success_outcome(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        outcome = _make_outcome_record(final_outcome="SUCCESS", groundedness=0.9)
        record = convert_outcome_to_record(outcome)
        assert record.outcome_class == "SUCCESS"
        assert record.retrieval_groundedness == 0.9

    def test_escalated_maps_to_human_override(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        outcome = _make_outcome_record(final_outcome="ESCALATED", hitl=True)
        record = convert_outcome_to_record(outcome)
        assert record.outcome_class == "HUMAN_OVERRIDE"

    def test_replay_failure_maps_correctly(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        outcome = _make_outcome_record(final_outcome="REPLAY_FAILURE", replay_status="FAILED")
        record = convert_outcome_to_record(outcome)
        assert record.outcome_class == "REPLAY_FAILURE"

    def test_failure_slot_s0_adds_policy_edge(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        outcome = _make_outcome_record(final_outcome="SAFE_FAILURE", failure_slot="S0")
        record = convert_outcome_to_record(outcome)
        assert "prompt_slot_S0_failure" in record.policy_edges

    def test_failure_slot_c0_adds_policy_edge(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        outcome = _make_outcome_record(final_outcome="SAFE_FAILURE", failure_slot="C0")
        record = convert_outcome_to_record(outcome)
        assert "prompt_slot_C0_failure" in record.policy_edges

    def test_failure_slot_none_no_policy_edge(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        outcome = _make_outcome_record(final_outcome="SUCCESS", failure_slot="NONE")
        record = convert_outcome_to_record(outcome)
        assert len(record.policy_edges) == 0

    def test_high_groundedness_maps_to_rag_bge(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        outcome = _make_outcome_record(groundedness=0.85)
        record = convert_outcome_to_record(outcome)
        assert record.retrieval_pattern == "RAG_BGE"

    def test_low_groundedness_maps_to_low_confidence(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        outcome = _make_outcome_record(groundedness=0.2)
        record = convert_outcome_to_record(outcome)
        assert record.retrieval_pattern == "LOW_CONFIDENCE_RETRIEVAL"

    def test_mid_groundedness_maps_to_rag_mixed(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        outcome = _make_outcome_record(groundedness=0.55)
        record = convert_outcome_to_record(outcome)
        assert record.retrieval_pattern == "RAG_MIXED"

    def test_healer_id_propagated(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        outcome = _make_outcome_record(
            final_outcome="HEALED_SUCCESS", healer=True, healer_id="healer_X"
        )
        record = convert_outcome_to_record(outcome)
        assert record.healer_used == "healer_X"

    def test_hitl_escalation_propagated(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        outcome = _make_outcome_record(final_outcome="ESCALATED", hitl=True)
        record = convert_outcome_to_record(outcome)
        assert record.hitl_escalation is True

    def test_guardrail_hits_propagated(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        outcome = _make_outcome_record(guardrail_hits=("g1", "g2"))
        record = convert_outcome_to_record(outcome)
        assert "g1" in record.guardrail_edges
        assert "g2" in record.guardrail_edges

    def test_record_id_deterministic(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        outcome = _make_outcome_record()
        r1 = convert_outcome_to_record(outcome)
        r2 = convert_outcome_to_record(outcome)
        assert r1.record_id == r2.record_id

    def test_feature_bundle_hash_matches_outcome_stable_hash(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        outcome = _make_outcome_record()
        record = convert_outcome_to_record(outcome)
        assert record.feature_bundle_hash == outcome.stable_hash()

    def test_batch_sorted_by_record_id(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcomes_to_records

        outcomes = [_make_outcome_record(trace_id=f"tr-{i:03d}") for i in range(10)]
        records = convert_outcomes_to_records(outcomes)
        ids = [r.record_id for r in records]
        assert ids == sorted(ids)

    def test_batch_skip_conversion_error_silently(self):
        from system_learning.engines.prompt_outcome_bus_adapter import PromptOutcomeBusAdapter

        adapter = PromptOutcomeBusAdapter()
        valid = _make_outcome_record(trace_id="tr-v")
        # Patch convert to raise on second call
        call_count = [0]
        original_convert = adapter.convert

        def patched_convert(outcome):
            call_count[0] += 1
            if call_count[0] == 2:
                raise RuntimeError("injected error")
            return original_convert(outcome)

        adapter.convert = patched_convert
        outcomes = [_make_outcome_record(trace_id=f"tr-{i}") for i in range(5)]
        records = adapter.convert_batch(outcomes)
        # 4 out of 5 should succeed (1 skipped)
        assert len(records) == 4


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
            PromptSafetyValidator, SafetyValidatorConfig,
        )

        artifact, prov_rels = self._build_artifact()
        ph = _sha256("policy_v1")
        cfg = SafetyValidatorConfig(active_policy_hash=ph)
        decision, safety_rels = PromptSafetyValidator(cfg).validate(artifact, _TS)
        assert decision.allowed is True
        total_rels = prov_rels + safety_rels
        rel_types = {r for (_, r, _) in total_rels}
        from system_learning.types.prompt_adg_relations import (
            PROVENANCE_USES_S0_RULE, SAFETY_ALLOWED,
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
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt
        from system_learning.engines.prompt_safety_validator import validate_prompt
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.types.prompt_adg_relations import ALL_PROMPT_RELATIONS

        artifact, prov_rels = self._build_artifact()
        _, safety_rels = validate_prompt(artifact, _TS)
        exec_result = trace_execution(
            artifact.prompt_hash, "tr-all-rels", {"success": True}, _TS + 5
        )
        all_rels = prov_rels + safety_rels + exec_result.adg_relations
        for (_, rel, _) in all_rels:
            assert rel in ALL_PROMPT_RELATIONS, (
                f"Unknown relation type emitted: {rel!r}"
            )

    def test_provenance_chain_prompt_hash_consistent(self):
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt
        from system_learning.engines.prompt_execution_tracer import trace_execution

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
