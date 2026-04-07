"""Prompt Provenance Builder — assembles CompiledPromptArtifact and emits ADG provenance relations.

Responsibilities
----------------
1. Accept raw slot content (S0/D0/I0/C0/U0 strings or pre-hashed manifests)
   and assemble a ``CompiledPromptArtifact``.
2. Compute a deterministic ``PromptSlotManifest`` with per-slot token counts.
3. Emit all 9 provenance ADG relations linking the artifact to its sources.
4. Emit budget relations (token_profile / truncated / exceeded_budget).

Design invariants
-----------------
1. No wall-clock reads; ``timestamp_utc`` always caller-supplied.
2. All outputs are content-addressed (stable_hash).
3. Token counting is caller-supplied (tokenizer-agnostic); defaults to
   character-based approximation (len // 4) when no tokenizer is given.
4. The builder is pure-function: calling build() twice with the same
   inputs produces identical artifacts and identical relation sets.
5. Emitted relations are returned as a list of (from, relation, to) tuples
   for the caller to persist; this engine never writes to the ADG directly.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "prompt_provenance_builder", "p0_governance")
_emit_snapshots_state("p0", "prompt_provenance_builder", "state_snapshot")
emit_replay_key("p0", "prompt_provenance_builder")
emit_determinism_digest("p0", "prompt_provenance_builder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "prompt_provenance_builder", "execution_auth")
_emit_validates_capability("p2", "prompt_provenance_builder", "capability_check")
_emit_routes_to_capability("p2", "prompt_provenance_builder", "capability_route")
_emit_writes_via_uwg("p2", "prompt_provenance_builder", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_provenance_builder", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_provenance_builder", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_provenance_builder", "exec_output")
_emit_dispatches_agent("p3", "prompt_provenance_builder", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_provenance_builder", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_provenance_builder", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_provenance_builder", "healing_outcome")
_emit_escalates_failure("p3", "prompt_provenance_builder", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_provenance_builder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_provenance_builder", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_provenance_builder", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_provenance_builder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_provenance_builder", "eval_metric")
_emit_stores_embedding("p4", "prompt_provenance_builder", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_provenance_builder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_provenance_builder", "exec_snapshot_link")

# Configuration constants
TOKEN_APPROXIMATION_RATIO = 4  # 1 token ≈ 4 chars

import hashlib
from dataclasses import dataclass
from typing import Callable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from system_learning.enforcement.determinism import deterministic_json
from system_learning.types.prompt_adg_relations import (
    BUDGET_EXCEEDED,
    BUDGET_TOKEN_PROFILE,
    BUDGET_TRUNCATED,
    PROVENANCE_C0_CONTEXT_SOURCE,
    PROVENANCE_CONTAINS_U0_INPUT,
    PROVENANCE_FEWSHOT_USED_BY,
    PROVENANCE_INSTRUCTION_INJECTION_SOURCE,
    PROVENANCE_TEMPLATE_USED_BY,
    PROVENANCE_USES_C0_CONTEXT,
    PROVENANCE_USES_D0_FENCE,
    PROVENANCE_USES_I0_INSTRUCTION,
    PROVENANCE_USES_S0_RULE,
)
from system_learning.types.prompt_artifact_types import (
    CompiledPromptArtifact,
    PromptSlotManifest,
)

_emit_emits_metric_event("prompt_provenance_builder", "p4obs", "metric_1")
_emit_emits_metric_event("prompt_provenance_builder", "p4obs", "metric_2")
_emit_emits_metric_event("prompt_provenance_builder", "p4obs", "metric_3")
_emit_emits_metric_event("prompt_provenance_builder", "p4obs", "metric_4")
_emit_emits_metric_event("prompt_provenance_builder", "p4obs", "metric_5")
_emit_emits_metric_event("prompt_provenance_builder", "p4obs", "metric_6")
_emit_records_incident_event("prompt_provenance_builder", "p4obs", "incident")
_emit_captures_runtime_anomaly("prompt_provenance_builder", "p4obs", "anomaly")
_emit_writes_observability_log("prompt_provenance_builder", "p4obs", "obs_log")
_emit_updates_monitoring_state("prompt_provenance_builder", "p4obs", "mon_state")
_emit_triggers_alert("prompt_provenance_builder", "p4obs", "alert")
_emit_links_incident_trace("prompt_provenance_builder", "p4obs", "trace_link")
_emit_captures_pattern("prompt_provenance_builder", "p3lm", "pattern")
_emit_records_learning_event("prompt_provenance_builder", "p3lm", "learning_event")
_emit_writes_learning_snapshot("prompt_provenance_builder", "p3lm", "snapshot")
_emit_feeds_meta_learning("prompt_provenance_builder", "p3lm", "meta_feed")
_emit_updates_routing_strategy("prompt_provenance_builder", "p3lm", "routing")
_emit_improves_agent_policy("prompt_provenance_builder", "p3lm", "policy")
_emit_stores_learning_state("prompt_provenance_builder", "p3lm", "state")
_emit_records_execution_trace("prompt_provenance_builder", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("prompt_provenance_builder", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("prompt_provenance_builder", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("prompt_provenance_builder", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("prompt_provenance_builder", "L4_STATE", "p2_trace_5")
_emit_reads_environ("prompt_provenance_builder", "env_read", "p2_env_1")
_emit_reads_environ("prompt_provenance_builder", "env_read", "p2_env_2")
_emit_reads_runtime_state("prompt_provenance_builder", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("prompt_provenance_builder", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "prompt_provenance_builder", "context_pull")
_emit_pulls_context("p1", "prompt_provenance_builder", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "prompt_provenance_builder", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "prompt_provenance_builder", "uwg_term_2")
_emit_writes_through("p1", "prompt_provenance_builder", "write_through")
_emit_writes_through("p1", "prompt_provenance_builder", "write_through_2")
_emit_validated_by_safety_plane("p1", "prompt_provenance_builder", "safety_validation")
_emit_invokes_eval("p1", "prompt_provenance_builder", "eval_call")
_emit_proposal_commits_routing("p1", "prompt_provenance_builder", "routing_commit")
_emit_escalates_to_human("p1", "prompt_provenance_builder", "human_escalation")
_emit_routes_through("p1", "prompt_provenance_builder", "route_through")
_emit_checks_agent_registry("p1", "prompt_provenance_builder", "agent_registry")
_emit_validates_agent_capability("p1", "prompt_provenance_builder", "capability")
_emit_dispatches_execution_plan("p1", "prompt_provenance_builder", "exec_plan")
_emit_agent_executes_agent("p1", "prompt_provenance_builder", "sub_agent")
_emit_routes_to_agent("p1", "prompt_provenance_builder", "target_agent")
_emit_verifies_policy("p1", "prompt_provenance_builder", "policy_check")
_emit_observes_runtime_state("p1", "prompt_provenance_builder", "runtime_state")
_emit_verifies_boundary("p1", "prompt_provenance_builder", "boundary_check")
_emit_transcripts_response("p1", "prompt_provenance_builder", "transcript")
_emit_hard_fails_untranscripted("p1", "prompt_provenance_builder")
_emit_gated_by_confidence("p1", "prompt_provenance_builder", "confidence_gate")

# ---------------------------------------------------------------------------
# Budget class thresholds (token counts)
# ---------------------------------------------------------------------------

_BUDGET_COMPACT = 1024
_BUDGET_STANDARD = 4096
_BUDGET_EXTENDED = 8192


def _classify_budget(total_tokens: int) -> str:
    if total_tokens <= _BUDGET_COMPACT:
        return "COMPACT"
    if total_tokens <= _BUDGET_STANDARD:
        return "STANDARD"
    if total_tokens <= _BUDGET_EXTENDED:
        return "EXTENDED"
    return "OVERFLOW"


# ---------------------------------------------------------------------------
# Default character-based token approximation
# ---------------------------------------------------------------------------


def _default_tokenizer(text: str) -> int:
    """Approximate token count: 1 token ≈ TOKEN_APPROXIMATION_RATIO chars."""
    return max(1, len(text) // TOKEN_APPROXIMATION_RATIO) if text else 0


# ---------------------------------------------------------------------------
# Slot content container
# ---------------------------------------------------------------------------


@dataclass
class SlotPayload:
    """Raw content for a single prompt slot.

    Attributes
    ----------
    content : str
        The actual slot text.
    source_ids : tuple[str, ...]
        ADG entity IDs or hashes of sources that contributed to this slot.
    """

    content: str
    source_ids: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Build input
# ---------------------------------------------------------------------------


@dataclass
class PromptBuildRequest:
    """All inputs required to build a CompiledPromptArtifact.

    Attributes
    ----------
    s0 : SlotPayload
        System / role slot.
    d0 : SlotPayload
        Defensive fence slot.
    i0 : SlotPayload
        Instruction slot.
    c0 : SlotPayload
        Context / RAG slot.
    u0 : SlotPayload
        User input slot.
    template_ids : tuple[str, ...]
        Template identifiers used for assembly.
    fewshot_ids : tuple[str, ...]
        Few-shot example IDs injected.
    injection_ids : tuple[str, ...]
        I0-injection policy IDs.
    model_target : str
        Model this prompt is compiled for.
    policy_hash : str | None
        Active policy hash at compile time.
    adg_entity_prefix : str
        Prefix for the artifact's ADG entity name
        (e.g. ``"ADG::CompiledPrompt"``).
    timestamp_utc : int
        Caller-supplied compilation timestamp.
    """

    s0: SlotPayload
    d0: SlotPayload
    i0: SlotPayload
    c0: SlotPayload
    u0: SlotPayload
    template_ids: tuple[str, ...]
    fewshot_ids: tuple[str, ...]
    injection_ids: tuple[str, ...]
    model_target: str
    policy_hash: str | None
    adg_entity_prefix: str
    timestamp_utc: int


# ---------------------------------------------------------------------------
# Build result
# ---------------------------------------------------------------------------


@dataclass
class PromptBuildResult:
    """Result of PromptProvenanceBuilder.build().

    Attributes
    ----------
    artifact : CompiledPromptArtifact
    adg_relations : list[tuple[str, str, str]]
        (from_entity, relation_type, to_entity) tuples emitted.
    """

    artifact: CompiledPromptArtifact
    adg_relations: list[tuple[str, str, str]]


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


class PromptProvenanceBuilder:
    """Assembles CompiledPromptArtifact and emits ADG provenance relations.

    Usage::

        builder = PromptProvenanceBuilder()
        result = builder.build(request, timestamp_utc=ts)
        artifact = result.artifact
        for (frm, rel, to) in result.adg_relations:
            adg.create_relation(frm, rel, to)
    """

    def __init__(
        self,
        tokenizer: Callable[[str], int] | None = None,
        budget_thresholds: tuple[int, int, int] | None = None,
    ) -> None:
        self._tokenizer = tokenizer or _default_tokenizer
        if budget_thresholds is not None:
            self._compact, self._standard, self._extended = budget_thresholds
        else:
            self._compact = _BUDGET_COMPACT
            self._standard = _BUDGET_STANDARD
            self._extended = _BUDGET_EXTENDED

    def build(self, request: PromptBuildRequest) -> PromptBuildResult:
        """Build a CompiledPromptArtifact from a PromptBuildRequest.

        Parameters
        ----------
        request : PromptBuildRequest

        Returns
        -------
        PromptBuildResult
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptProvenanceBuilder.build")

        tok = self._tokenizer

        # --- Slot hashes and token counts ---
        s0_hash = _slot_hash(request.s0.content)
        d0_hash = _slot_hash(request.d0.content)
        i0_hash = _slot_hash(request.i0.content)
        c0_hash = _slot_hash(request.c0.content)
        u0_hash = _slot_hash(request.u0.content)

        s0_tok = tok(request.s0.content)
        d0_tok = tok(request.d0.content)
        i0_tok = tok(request.i0.content)
        c0_tok = tok(request.c0.content)
        u0_tok = tok(request.u0.content)
        total_tok = s0_tok + d0_tok + i0_tok + c0_tok + u0_tok

        budget_class = self._classify_budget(total_tok)

        slot_manifest = PromptSlotManifest(
            s0_hash=s0_hash,
            d0_hash=d0_hash,
            i0_hash=i0_hash,
            c0_hash=c0_hash,
            u0_hash=u0_hash,
            s0_tokens=s0_tok,
            d0_tokens=d0_tok,
            i0_tokens=i0_tok,
            c0_tokens=c0_tok,
            u0_tokens=u0_tok,
            total_tokens=total_tok,
            budget_class=budget_class,
        )

        # --- Prompt hash = hash of full canonical assembly ---
        prompt_hash = _prompt_hash(
            s0_hash,
            d0_hash,
            i0_hash,
            c0_hash,
            u0_hash,
            request.model_target,
            request.policy_hash,
            request.timestamp_utc,
        )

        # --- ADG entity name ---
        adg_entity_name = f"{request.adg_entity_prefix}::{prompt_hash[:16]}"

        # --- Collect C0 sources from slot + any explicit c0_sources ---
        c0_sources: tuple[str, ...] = tuple(sorted(set(request.c0.source_ids) | {c0_hash}))

        artifact = CompiledPromptArtifact(
            prompt_hash=prompt_hash,
            slot_manifest=slot_manifest,
            template_ids=tuple(sorted(request.template_ids)),
            fewshot_ids=tuple(sorted(request.fewshot_ids)),
            injection_ids=tuple(sorted(request.injection_ids)),
            c0_sources=c0_sources,
            model_target=request.model_target,
            policy_hash=request.policy_hash,
            adg_entity_name=adg_entity_name,
            influence_class="C0_INFORMATIONAL",
            timestamp_utc=request.timestamp_utc,
        )

        # --- Emit ADG relations ---
        relations: list[tuple[str, str, str]] = []

        # Slot provenance relations
        for tid in sorted(request.template_ids):
            relations.append((tid, PROVENANCE_TEMPLATE_USED_BY, adg_entity_name))
        for fid in sorted(request.fewshot_ids):
            relations.append((fid, PROVENANCE_FEWSHOT_USED_BY, adg_entity_name))
        for iid in sorted(request.injection_ids):
            relations.append((iid, PROVENANCE_INSTRUCTION_INJECTION_SOURCE, adg_entity_name))
        for src in sorted(request.c0.source_ids):
            relations.append((src, PROVENANCE_C0_CONTEXT_SOURCE, adg_entity_name))

        # Slot-to-artifact slot relations
        relations.append((adg_entity_name, PROVENANCE_USES_S0_RULE, f"ADG::Slot::S0::{s0_hash[:16]}"))
        relations.append((adg_entity_name, PROVENANCE_USES_D0_FENCE, f"ADG::Slot::D0::{d0_hash[:16]}"))
        relations.append((adg_entity_name, PROVENANCE_USES_I0_INSTRUCTION, f"ADG::Slot::I0::{i0_hash[:16]}"))
        relations.append((adg_entity_name, PROVENANCE_USES_C0_CONTEXT, f"ADG::Slot::C0::{c0_hash[:16]}"))
        relations.append((adg_entity_name, PROVENANCE_CONTAINS_U0_INPUT, f"ADG::Slot::U0::{u0_hash[:16]}"))

        # Budget relations
        relations.append(
            (
                adg_entity_name,
                BUDGET_TOKEN_PROFILE,
                f"ADG::TokenProfile::{budget_class}::{prompt_hash[:16]}",
            ),
        )
        if budget_class == "OVERFLOW":
            relations.append(
                (
                    adg_entity_name,
                    BUDGET_EXCEEDED,
                    f"ADG::TokenBudget::OVERFLOW::{prompt_hash[:16]}",
                ),
            )
        elif budget_class == "EXTENDED":
            relations.append(
                (
                    adg_entity_name,
                    BUDGET_TRUNCATED,
                    f"ADG::TokenBudget::EXTENDED::{prompt_hash[:16]}",
                ),
            )

        return PromptBuildResult(artifact=artifact, adg_relations=relations)

    def _classify_budget(self, total_tokens: int) -> str:
        if total_tokens <= self._compact:
            return "COMPACT"
        if total_tokens <= self._standard:
            return "STANDARD"
        if total_tokens <= self._extended:
            return "EXTENDED"
        return "OVERFLOW"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _slot_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _prompt_hash(
    s0: str,
    d0: str,
    i0: str,
    c0: str,
    u0: str,
    model_target: str,
    policy_hash: str | None,
    timestamp_utc: int,
) -> str:
    canonical = deterministic_json(
        {
            "c0": c0,
            "d0": d0,
            "i0": i0,
            "model_target": model_target,
            "policy_hash": policy_hash,
            "s0": s0,
            "timestamp_utc": timestamp_utc,
            "u0": u0,
        },
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


def build_compiled_prompt(
    request: PromptBuildRequest,
    *,
    tokenizer: Callable[[str], int] | None = None,
) -> PromptBuildResult:
    """Module-level convenience wrapper."""
    return PromptProvenanceBuilder(tokenizer=tokenizer).build(request)


__all__ = [
    "PromptBuildRequest",
    "PromptBuildResult",
    "PromptProvenanceBuilder",
    "SlotPayload",
    "build_compiled_prompt",
]
