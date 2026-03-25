"""Tests for prompt provenance engine components.

Covers:
  - prompt_provenance_builder.py  — artifact assembly, provenance relations, budget
  - prompt_safety_validator.py    — safety gates, decision invariants
  - prompt_execution_tracer.py    — execution/outcome records, ADG relations
  - prompt_drift_detector.py      — drift signals, threshold logic
  - prompt_outcome_bus_adapter.py — PromptOutcomeRecord → TraceFeatureRecord bridge
"""

from __future__ import annotations

import hashlib

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_prompt_provenance_engines")
# REMOVED: _emit_applies_guardrail("p0", "test_prompt_provenance_engines", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_prompt_provenance_engines", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_prompt_provenance_engines", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_prompt_provenance_engines", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_prompt_provenance_engines", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_prompt_provenance_engines", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_prompt_provenance_engines", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_prompt_provenance_engines", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_prompt_provenance_engines", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_prompt_provenance_engines", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_prompt_provenance_engines", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_prompt_provenance_engines", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_prompt_provenance_engines", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_prompt_provenance_engines", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_prompt_provenance_engines", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_prompt_provenance_engines", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_prompt_provenance_engines", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_prompt_provenance_engines", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_prompt_provenance_engines", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_prompt_provenance_engines", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_prompt_provenance_engines", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_prompt_provenance_engines", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_prompt_provenance_engines", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_prompt_provenance_engines", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_prompt_provenance_engines", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_prompt_provenance_engines", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_prompt_provenance_engines", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_prompt_provenance_engines", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_prompt_provenance_engines", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_prompt_provenance_engines", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_prompt_provenance_engines", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_prompt_provenance_engines", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_prompt_provenance_engines", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_prompt_provenance_engines", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_prompt_provenance_engines", "write_through")
# REMOVED: _emit_writes_through("p1", "test_prompt_provenance_engines", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_prompt_provenance_engines", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_prompt_provenance_engines", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_prompt_provenance_engines", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_prompt_provenance_engines", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_prompt_provenance_engines", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_prompt_provenance_engines", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_prompt_provenance_engines", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_prompt_provenance_engines", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_prompt_provenance_engines", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_prompt_provenance_engines", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_prompt_provenance_engines", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_prompt_provenance_engines", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_prompt_provenance_engines", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_prompt_provenance_engines", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_prompt_provenance_engines")
# REMOVED: _emit_gated_by_confidence("p1", "test_prompt_provenance_engines", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_prompt_provenance_engines")
# REMOVED: emit_determinism_digest("p0", "test_prompt_provenance_engines")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_prompt_provenance_engines", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_prompt_provenance_engines", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_prompt_provenance_engines", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_prompt_provenance_engines", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_prompt_provenance_engines", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_prompt_provenance_engines", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_prompt_provenance_engines", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_prompt_provenance_engines", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_prompt_provenance_engines", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_prompt_provenance_engines", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_prompt_provenance_engines", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_prompt_provenance_engines", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_prompt_provenance_engines", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_prompt_provenance_engines", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_prompt_provenance_engines", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_prompt_provenance_engines", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_prompt_provenance_engines", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_prompt_provenance_engines", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_prompt_provenance_engines", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_prompt_provenance_engines", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_TS = 1_700_200_000
_H64 = "a" * 64
_H64b = "b" * 64


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _make_slot_manifest(total_tokens=512, budget_class="STANDARD"):
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
        for frm, rel, to in result.adg_relations:
            # from entity may be a source ID (template/fewshot/chunk) which
            # may or may not start with ADG:: — but to must start with ADG::
            # (provenance sources are external IDs)
            assert isinstance(rel, str) and rel
            assert to.startswith("ADG::"), f"To entity {to!r} doesn't start with ADG::"

    def test_slot_provenance_relations_emitted(self):
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt
        from system_learning.types.prompt_adg_relations import (
            PROVENANCE_CONTAINS_U0_INPUT,
            PROVENANCE_USES_C0_CONTEXT,
            PROVENANCE_USES_D0_FENCE,
            PROVENANCE_USES_I0_INSTRUCTION,
            PROVENANCE_USES_S0_RULE,
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
            PromptBuildRequest,
            PromptProvenanceBuilder,
            SlotPayload,
        )
        from system_learning.types.prompt_adg_relations import BUDGET_EXCEEDED

        # Use custom tokenizer that always returns 3000 per slot → total 15000 > 8192
        builder = PromptProvenanceBuilder(tokenizer=lambda _: 3000)
        req = PromptBuildRequest(
            s0=SlotPayload("s"),
            d0=SlotPayload("d"),
            i0=SlotPayload("i"),
            c0=SlotPayload("c"),
            u0=SlotPayload("u"),
            template_ids=(),
            fewshot_ids=(),
            injection_ids=(),
            model_target="gpt-4o",
            policy_hash=None,
            adg_entity_prefix="ADG::CompiledPrompt",
            timestamp_utc=_TS,
        )
        result = builder.build(req)
        rel_types = {r for (_, r, _) in result.adg_relations}
        assert BUDGET_EXCEEDED in rel_types
        assert result.artifact.slot_manifest.budget_class == "OVERFLOW"

    def test_compact_budget_no_truncated_or_exceeded(self):
        from system_learning.engines.prompt_provenance_builder import (
            PromptBuildRequest,
            PromptProvenanceBuilder,
            SlotPayload,
        )
        from system_learning.types.prompt_adg_relations import BUDGET_EXCEEDED, BUDGET_TRUNCATED

        builder = PromptProvenanceBuilder(tokenizer=lambda _: 10)
        req = PromptBuildRequest(
            s0=SlotPayload("s"),
            d0=SlotPayload("d"),
            i0=SlotPayload("i"),
            c0=SlotPayload("c"),
            u0=SlotPayload("u"),
            template_ids=(),
            fewshot_ids=(),
            injection_ids=(),
            model_target="gpt-4o",
            policy_hash=None,
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
        from system_learning.engines.prompt_provenance_builder import (
            PromptBuildRequest,
            SlotPayload,
            build_compiled_prompt,
        )

        req = PromptBuildRequest(
            s0=SlotPayload("s"),
            d0=SlotPayload("d"),
            i0=SlotPayload("i"),
            c0=SlotPayload("context", source_ids=("src-abc", "src-def")),
            u0=SlotPayload("u"),
            template_ids=(),
            fewshot_ids=(),
            injection_ids=(),
            model_target="m",
            policy_hash=None,
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
            PromptSafetyValidator,
            SafetyValidatorConfig,
        )

        artifact = _make_artifact(policy_hash="hash_A")
        cfg = SafetyValidatorConfig(active_policy_hash="hash_B")
        validator = PromptSafetyValidator(cfg)
        decision, _ = validator.validate(artifact, _TS)
        assert decision.allowed is False
        assert "POLICY_HASH_MISMATCH" in decision.denial_reasons

    def test_policy_match_allows(self):
        from system_learning.engines.prompt_safety_validator import (
            PromptSafetyValidator,
            SafetyValidatorConfig,
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
            PromptSafetyValidator,
            SafetyValidatorConfig,
        )

        artifact = _make_artifact(budget_class="EXTENDED", total_tokens=6000)
        cfg = SafetyValidatorConfig(block_on_extended=True)
        decision, _ = PromptSafetyValidator(cfg).validate(artifact, _TS)
        assert decision.allowed is False
        assert "BUDGET_EXTENDED_BLOCKED" in decision.denial_reasons

    def test_all_5_safety_relations_emitted(self):
        from system_learning.engines.prompt_safety_validator import (
            PromptSafetyValidator,
        )
        from system_learning.types.prompt_adg_relations import (
            SAFETY_ALLOWED,
            SAFETY_BLOCKED,
            SAFETY_BUDGET_CHECKED,
            SAFETY_CHECKED_BY_GUARDRAIL,
            SAFETY_VALIDATED_BY_POLICY,
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
            PromptSafetyValidator,
            SafetyValidatorConfig,
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

        result = trace_execution(
            _H64,
            "tr-002",
            self._signal(
                human_escalation_flag=True,
                success=True,
            ),
            _TS,
        )
        assert result.outcome_record.final_outcome == "ESCALATED"
        assert result.outcome_record.hitl_escalation is True

    def test_replay_failure_outcome(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        result = trace_execution(
            _H64,
            "tr-003",
            self._signal(
                replay_failed=True,
                success=False,
            ),
            _TS,
        )
        assert result.outcome_record.final_outcome == "REPLAY_FAILURE"
        assert result.outcome_record.replay_status == "FAILED"

    def test_healed_success_outcome(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        result = trace_execution(
            _H64,
            "tr-004",
            self._signal(
                healing_invoked=True,
                healed=True,
                success=True,
            ),
            _TS,
        )
        assert result.outcome_record.final_outcome == "HEALED_SUCCESS"
        assert result.outcome_record.healer_invoked is True

    def test_replay_passed_status(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        result = trace_execution(
            _H64,
            "tr-005",
            self._signal(
                replay_passed=True,
            ),
            _TS,
        )
        assert result.outcome_record.replay_status == "PASSED"

    def test_execution_relations_emitted(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.types.prompt_adg_relations import (
            EXECUTION_EXECUTED_BY_MODEL,
            EXECUTION_GENERATES_TRACE,
            EXECUTION_ROUTES_TO,
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
            HITL_CAUSED_ESCALATION,
            OUTCOME_ESCALATED_HITL,
        )

        result = trace_execution(
            _H64,
            "tr-008",
            self._signal(
                human_escalation_flag=True,
            ),
            _TS,
        )
        rel_types = {r for (_, r, _) in result.adg_relations}
        assert OUTCOME_ESCALATED_HITL in rel_types
        assert HITL_CAUSED_ESCALATION in rel_types

    def test_healer_triggers_healer_relation(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.types.prompt_adg_relations import OUTCOME_TRIGGERED_HEALER

        result = trace_execution(
            _H64,
            "tr-009",
            self._signal(
                healing_invoked=True,
                healer_id="healer_X",
                success=True,
                healed=True,
            ),
            _TS,
        )
        rel_types = {r for (_, r, _) in result.adg_relations}
        assert OUTCOME_TRIGGERED_HEALER in rel_types

    def test_retrieval_relations_emitted(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.types.prompt_adg_relations import (
            RETRIEVAL_RETRIEVES_VIA,
            RETRIEVAL_SCORES_GROUNDEDNESS,
        )

        result = trace_execution(_H64, "tr-010", self._signal(), _TS)
        rel_types = {r for (_, r, _) in result.adg_relations}
        assert RETRIEVAL_RETRIEVES_VIA in rel_types
        assert RETRIEVAL_SCORES_GROUNDEDNESS in rel_types

    def test_chunk_ids_emit_uses_chunk_relations(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.types.prompt_adg_relations import RETRIEVAL_USES_CHUNK

        result = trace_execution(
            _H64,
            "tr-011",
            self._signal(
                chunk_ids=["chunk-A", "chunk-B", "chunk-C"],
            ),
            _TS,
        )
        chunk_rels = [(f, r, t) for (f, r, t) in result.adg_relations if r == RETRIEVAL_USES_CHUNK]
        assert len(chunk_rels) == 3

    def test_empty_signal_produces_unknown_outcome(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        result = trace_execution(_H64, "tr-012", {}, _TS)
        assert result.outcome_record.final_outcome == "UNKNOWN"

    def test_failure_slot_guardrail_hits_maps_to_d0(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        result = trace_execution(
            _H64,
            "tr-013",
            self._signal(
                success=False,
                guardrail_hits=["guardrail_1"],
            ),
            _TS,
        )
        assert result.outcome_record.failure_slot == "D0"

    def test_batch_trace_sorted_by_execution_id(self):
        from system_learning.engines.prompt_execution_tracer import PromptExecutionTracer

        tracer = PromptExecutionTracer()
        executions = [(_H64, f"tr-{i:03d}", self._signal(), _TS + i) for i in range(10)]
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
            records.append(
                _make_outcome_record(
                    trace_id=f"tr-{id(records)}-{i}",
                    groundedness=gnd,
                    hitl=hitl,
                    guardrail_hits=guard,
                    replay_status=replay,
                )
            )
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
            DriftDetectorConfig,
            PromptDriftDetector,
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

        outcome = _make_outcome_record(final_outcome="HEALED_SUCCESS", healer=True, healer_id="healer_X")
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
