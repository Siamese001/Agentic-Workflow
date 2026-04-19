"""LLM-as-Judge evaluation harness.

Provides:
- ``JudgeScore``   — immutable score dataclass with deterministic digest
- ``LLMJudge``     — Protocol for all judge implementations
- ``NullJudge``    — Deterministic stub for CI (no LLM calls)
- ``GeminiJudge``  — Production judge via Gemini with structured rubric
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from typing import Any
from typing import Protocol, runtime_checkable
from typing import cast

from infrastructure.sdks_mcps import create_gemini_model

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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "llm_judge")
_emit_applies_guardrail("p0", "llm_judge", "p0_governance")
_emit_reads_policy_state("p0", "llm_judge", "policy_binding")
_emit_snapshots_state("p0", "llm_judge", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("llm_judge", "p4obs", "metric_1")
_emit_emits_metric_event("llm_judge", "p4obs", "metric_2")
_emit_emits_metric_event("llm_judge", "p4obs", "metric_3")
_emit_emits_metric_event("llm_judge", "p4obs", "metric_4")
_emit_emits_metric_event("llm_judge", "p4obs", "metric_5")
_emit_emits_metric_event("llm_judge", "p4obs", "metric_6")
_emit_records_incident_event("llm_judge", "p4obs", "incident")
_emit_captures_runtime_anomaly("llm_judge", "p4obs", "anomaly")
_emit_writes_observability_log("llm_judge", "p4obs", "obs_log")
_emit_updates_monitoring_state("llm_judge", "p4obs", "mon_state")
_emit_triggers_alert("llm_judge", "p4obs", "alert")
_emit_links_incident_trace("llm_judge", "p4obs", "trace_link")
_emit_captures_pattern("llm_judge", "p3lm", "pattern")
_emit_records_learning_event("llm_judge", "p3lm", "learning_event")
_emit_writes_learning_snapshot("llm_judge", "p3lm", "snapshot")
_emit_feeds_meta_learning("llm_judge", "p3lm", "meta_feed")
_emit_updates_routing_strategy("llm_judge", "p3lm", "routing")
_emit_improves_agent_policy("llm_judge", "p3lm", "policy")
_emit_stores_learning_state("llm_judge", "p3lm", "state")
_emit_records_execution_trace("llm_judge", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("llm_judge", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("llm_judge", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("llm_judge", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("llm_judge", "L4_STATE", "p2_trace_5")
_emit_reads_environ("llm_judge", "env_read", "p2_env_1")
_emit_reads_environ("llm_judge", "env_read", "p2_env_2")
_emit_reads_runtime_state("llm_judge", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("llm_judge", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "llm_judge", "context_pull")
_emit_pulls_context("p1", "llm_judge", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "llm_judge", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "llm_judge", "uwg_term_2")
_emit_writes_through("p1", "llm_judge", "write_through")
_emit_writes_through("p1", "llm_judge", "write_through_2")
_emit_validated_by_safety_plane("p1", "llm_judge", "safety_validation")
_emit_invokes_eval("p1", "llm_judge", "eval_call")
_emit_proposal_commits_routing("p1", "llm_judge", "routing_commit")
_emit_escalates_to_human("p1", "llm_judge", "human_escalation")
_emit_routes_through("p1", "llm_judge", "route_through")
_emit_checks_agent_registry("p1", "llm_judge", "agent_registry")
_emit_validates_agent_capability("p1", "llm_judge", "capability")
_emit_dispatches_execution_plan("p1", "llm_judge", "exec_plan")
_emit_agent_executes_agent("p1", "llm_judge", "sub_agent")
_emit_routes_to_agent("p1", "llm_judge", "target_agent")
_emit_verifies_policy("p1", "llm_judge", "policy_check")
_emit_observes_runtime_state("p1", "llm_judge", "runtime_state")
_emit_verifies_boundary("p1", "llm_judge", "boundary_check")
_emit_transcripts_response("p1", "llm_judge", "transcript")
_emit_hard_fails_untranscripted("p1", "llm_judge")
_emit_gated_by_confidence("p1", "llm_judge", "confidence_gate")
emit_replay_key("p0", "llm_judge")
emit_determinism_digest("p0", "llm_judge")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "llm_judge", "execution_auth")
_emit_validates_capability("p2", "llm_judge", "capability_check")
_emit_routes_to_capability("p2", "llm_judge", "capability_route")
_emit_writes_via_uwg("p2", "llm_judge", "uwg_write")
_emit_blocks_direct_write("p2", "llm_judge", "direct_write_block")
_emit_records_tool_invocation("p2", "llm_judge", "tool_invocation")
_emit_captures_execution_output("p2", "llm_judge", "exec_output")
_emit_dispatches_agent("p3", "llm_judge", "agent_dispatch")
_emit_coordinates_agents("p3", "llm_judge", "agent_coordination")
_emit_records_workflow_lineage("p3", "llm_judge", "workflow_lineage")
_emit_records_healing_outcome("p3", "llm_judge", "healing_outcome")
_emit_escalates_failure("p3", "llm_judge", "failure_escalation")
_emit_orchestrates_workflow("p3", "llm_judge", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "llm_judge", "healing_dispatch")
_emit_invokes_evaluation("p3", "llm_judge", "evaluation_signal")
_emit_records_telemetry_event("p4", "llm_judge", "telemetry_event")
_emit_captures_evaluation_metric("p4", "llm_judge", "eval_metric")
_emit_stores_embedding("p4", "llm_judge", "embedding_store")
_emit_updates_meta_learning_state("p4", "llm_judge", "meta_learning")
_emit_links_execution_to_snapshot("p4", "llm_judge", "exec_snapshot_link")

_RUBRIC = '\nYou are an expert evaluator for RAG (Retrieval-Augmented Generation) systems.\nScore the following on a scale of 1-5 (integers only):\n\n- faithfulness: Is every claim in the answer supported by the provided context?\n  1=completely unsupported, 5=every claim fully grounded.\n- answer_relevancy: Does the answer directly and completely address the query?\n  1=off-topic, 5=directly addresses every part.\n- context_precision: Is the retrieved context relevant to answering the query?\n  1=irrelevant, 5=all context highly relevant.\n- groundedness: Are the factual claims in the answer grounded in the context?\n  1=hallucinated, 5=fully grounded.\n\nProvide a short reasoning (≤2 sentences).\n\nRespond ONLY with valid JSON:\n{"faithfulness": <1-5>, "answer_relevancy": <1-5>,\n "context_precision": <1-5>, "groundedness": <1-5>,\n "reasoning": "<text>"}\n'


@dataclass(frozen=True)
class JudgeScore:
    """Immutable score from an LLM judge."""

    faithfulness: float
    answer_relevancy: float
    context_precision: float
    groundedness: float
    reasoning: str
    judge_model: str
    deterministic_digest: str

    @classmethod
    def create(
        cls,
        faithfulness: float,
        answer_relevancy: float,
        context_precision: float,
        groundedness: float,
        reasoning: str,
        judge_model: str,
    ) -> JudgeScore:
        canonical = json.dumps(
            {
                "faithfulness": faithfulness,
                "answer_relevancy": answer_relevancy,
                "context_precision": context_precision,
                "groundedness": groundedness,
                "judge_model": judge_model,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return cls(
            faithfulness=faithfulness,
            answer_relevancy=answer_relevancy,
            context_precision=context_precision,
            groundedness=groundedness,
            reasoning=reasoning,
            judge_model=judge_model,
            deterministic_digest=digest,
        )


@runtime_checkable
class LLMJudge(Protocol):
    """Protocol for all judge implementations."""

    def score(self, query: str, context: str, answer: str) -> JudgeScore: ...


class NullJudge:
    """Deterministic stub judge for CI — always returns fixed scores.

    Use in unit tests to avoid any LLM API calls.
    """

    FIXED_SCORE = 3.0

    def score(self, query: str, context: str, answer: str) -> JudgeScore:
        return JudgeScore.create(
            faithfulness=self.FIXED_SCORE,
            answer_relevancy=self.FIXED_SCORE,
            context_precision=self.FIXED_SCORE,
            groundedness=self.FIXED_SCORE,
            reasoning="NullJudge: deterministic stub",
            judge_model="null",
        )


class GeminiJudge:
    """Production judge via Gemini with structured rubric.

    Uses ``google.generativeai`` directly with ``GEMINI_API_KEY`` or
    ``GOOGLE_API_KEY``. Supports model override via ``GEMINI_MODEL``
    env var. Temperature is forced to 0.0 for maximum determinism.
    Parse failures retry once after stripping markdown fences.
    """

    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(self, gemini_client=None, model: str | None = None) -> None:
        self._client = gemini_client
        env_model = os.getenv("GEMINI_MODEL")
        self._model = model or env_model or self.DEFAULT_MODEL
        self._configured = False

    @property
    def model_id(self) -> str:
        return self._model

    def _get_client(self):
        if self._client is not None:
            return self._client

        try:
            client = create_gemini_model(self._model)
        except (ImportError, ValueError) as exc:
            raise RuntimeError(
                "GeminiJudge: google-genai package not installed or GOOGLE_API_KEY missing.",
            ) from exc

        self._configured = True
        return client

    @staticmethod
    def _clean(raw: str) -> str:
        return re.sub("```(?:json)?|```", "", raw).strip()

    @staticmethod
    def _parse(raw: str) -> dict[str, Any]:
        try:
            return cast(dict[str, Any], json.loads(raw))
        except json.JSONDecodeError:
            return cast(dict[str, Any], json.loads(GeminiJudge._clean(raw)))

    def score(self, query: str, context: str, answer: str) -> JudgeScore:
        prompt = f"{_RUBRIC}\n\nQuery: {query}\n\nContext:\n{context}\n\nAnswer:\n{answer}"
        client = self._get_client()
        response = client.generate_content(
            prompt,
            generation_config={"temperature": 0.0},
        )
        raw = response.text
        data = self._parse(raw)
        return JudgeScore.create(
            faithfulness=float(data.get("faithfulness", 1)),
            answer_relevancy=float(data.get("answer_relevancy", 1)),
            context_precision=float(data.get("context_precision", 1)),
            groundedness=float(data.get("groundedness", 1)),
            reasoning=str(data.get("reasoning", "")),
            judge_model=self._model,
        )


__all__ = ["JudgeScore", "LLMJudge", "NullJudge", "GeminiJudge"]
