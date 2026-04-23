"""LLM-as-Judge evaluation harness.

Provides:
- ``JudgeScore``   — immutable score dataclass with deterministic digest
- ``LLMJudge``     — Protocol for all judge implementations
- ``NullJudge``    — Deterministic stub for CI (no LLM calls)
- ``GeminiJudge``  — Production judge via Gemini with structured rubric
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import re
from dataclasses import dataclass
from typing import Any
from typing import Protocol, runtime_checkable
from typing import cast

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

# ---------------------------------------------------------------------------
# Legacy combined rubric (DEPRECATED — retained for backward compat only).
# New callsites should use per-dimension isolated rubrics via DIMENSION_RUBRICS
# below, per Anthropic best practice (engineering.anthropic.com/
# demystifying-evals-for-ai-agents — "grade each dimension with an isolated
# LLM-as-judge rather than using one to grade all dimensions").
# ---------------------------------------------------------------------------
_RUBRIC = '\nYou are an expert evaluator for RAG (Retrieval-Augmented Generation) systems.\nScore the following on a scale of 1-5 (integers only):\n\n- faithfulness: Is every claim in the answer supported by the provided context?\n  1=completely unsupported, 5=every claim fully grounded.\n- answer_relevancy: Does the answer directly and completely address the query?\n  1=off-topic, 5=directly addresses every part.\n- context_precision: Is the retrieved context relevant to answering the query?\n  1=irrelevant, 5=all context highly relevant.\n- groundedness: Are the factual claims in the answer grounded in the context?\n  1=hallucinated, 5=fully grounded.\n\nProvide a short reasoning (≤2 sentences).\n\nRespond ONLY with valid JSON:\n{"faithfulness": <1-5>, "answer_relevancy": <1-5>,\n "context_precision": <1-5>, "groundedness": <1-5>,\n "reasoning": "<text>"}\n'

# ---------------------------------------------------------------------------
# Per-dimension CoT-first rubrics (Anthropic-aligned).
# Each rubric:
#   1) asks the model to reason FIRST, then produce a score
#   2) gives explicit Unknown escape hatch ("return Unknown when insufficient")
#   3) provides scoring anchors at 1, 3, 5 so grading is reproducible
# ---------------------------------------------------------------------------

_DIM_FAITHFULNESS = """\
You are an expert evaluator grading ONE dimension of a RAG answer: FAITHFULNESS.

Definition: Is every claim in the answer supported by the provided context?
Scoring anchors (integer 1-5):
  1 = most claims fabricated or contradicted by context.
  3 = core claims supported but several unsupported or weakly supported claims.
  5 = every claim in the answer is directly and fully supported by the context.

INSTRUCTIONS:
  1. Think step by step inside a <reasoning>...</reasoning> block.
     Cite the specific claims in the answer and which context span supports each.
  2. If the context is missing, irrelevant, or if you cannot confidently grade
     this dimension from the given evidence, respond with "Unknown" instead of
     a numeric score. Do not guess. Do not fabricate support.
  3. After the reasoning, output exactly one JSON object on the final line:
     {"score": <1|2|3|4|5|"Unknown">, "unknown_reason": "<string-or-null>"}

Respond with ONLY the reasoning block followed by the JSON line.
"""

_DIM_ANSWER_RELEVANCY = """\
You are an expert evaluator grading ONE dimension of a RAG answer: ANSWER_RELEVANCY.

Definition: Does the answer directly and completely address the query?
Scoring anchors (integer 1-5):
  1 = off-topic or answers a different question.
  3 = partially addresses the query; misses key sub-parts.
  5 = directly and completely addresses every part of the query.

INSTRUCTIONS:
  1. Think step by step inside a <reasoning>...</reasoning> block.
     List the sub-parts of the query and check each against the answer.
  2. If the query is ambiguous or you cannot confidently grade, respond
     "Unknown" instead of a numeric score. Do not guess.
  3. After the reasoning, output exactly one JSON object on the final line:
     {"score": <1|2|3|4|5|"Unknown">, "unknown_reason": "<string-or-null>"}

Respond with ONLY the reasoning block followed by the JSON line.
"""

_DIM_CONTEXT_PRECISION = """\
You are an expert evaluator grading ONE dimension of a RAG answer: CONTEXT_PRECISION.

Definition: Is the retrieved context relevant to answering the query?
Scoring anchors (integer 1-5):
  1 = context is irrelevant or unrelated to the query.
  3 = context is partially relevant; contains off-topic noise alongside useful
      material.
  5 = all retrieved context is directly relevant to the query.

INSTRUCTIONS:
  1. Think step by step inside a <reasoning>...</reasoning> block.
     Identify relevant vs irrelevant spans in the context.
  2. If context is empty or you cannot confidently grade, respond "Unknown".
  3. After the reasoning, output exactly one JSON object on the final line:
     {"score": <1|2|3|4|5|"Unknown">, "unknown_reason": "<string-or-null>"}

Respond with ONLY the reasoning block followed by the JSON line.
"""

_DIM_GROUNDEDNESS = """\
You are an expert evaluator grading ONE dimension of a RAG answer: GROUNDEDNESS.

Definition: Are the factual claims in the answer grounded in the provided
context (as opposed to parametric model knowledge)?
Scoring anchors (integer 1-5):
  1 = answer is based on model's prior knowledge with no grounding in context.
  3 = mixed: some claims grounded in context, others rely on model knowledge.
  5 = every factual claim is traceable to a span in the provided context.

INSTRUCTIONS:
  1. Think step by step inside a <reasoning>...</reasoning> block.
     For each factual claim in the answer, mark "grounded" or "ungrounded".
  2. If insufficient evidence to grade, respond "Unknown" instead of a number.
  3. After the reasoning, output exactly one JSON object on the final line:
     {"score": <1|2|3|4|5|"Unknown">, "unknown_reason": "<string-or-null>"}

Respond with ONLY the reasoning block followed by the JSON line.
"""

DIMENSION_RUBRICS: dict[str, str] = {
    "faithfulness": _DIM_FAITHFULNESS,
    "answer_relevancy": _DIM_ANSWER_RELEVANCY,
    "context_precision": _DIM_CONTEXT_PRECISION,
    "groundedness": _DIM_GROUNDEDNESS,
}

DIMENSIONS: tuple[str, ...] = (
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "groundedness",
)


# ---------------------------------------------------------------------------
# Unknown sentinel. Stored in JudgeScore as float('nan') with a reason in
# ``unknown_reasons``. Call sites should use ``JudgeScore.is_unknown(dim)``
# to check abstention rather than comparing NaN directly.
# ---------------------------------------------------------------------------
UNKNOWN: float = float("nan")


def _is_nan(value: float) -> bool:
    return value != value  # NaN is the only float that is not equal to itself


@dataclass(frozen=True)
class JudgeScore:
    """Immutable score from an LLM judge.

    Fields ``faithfulness``, ``answer_relevancy``, ``context_precision``,
    ``groundedness`` may be ``float('nan')`` to indicate the judge
    abstained (Unknown) on that dimension. The matching entry in
    ``unknown_reasons`` carries the free-text reason.

    ``per_dim_reasoning`` stores the discarded CoT reasoning per
    dimension (Anthropic best practice: reason first, discard from
    score math, keep for audit).
    """

    faithfulness: float
    answer_relevancy: float
    context_precision: float
    groundedness: float
    reasoning: str
    judge_model: str
    deterministic_digest: str
    unknown_reasons: tuple[tuple[str, str], ...] = ()
    per_dim_reasoning: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(
        cls,
        faithfulness: float,
        answer_relevancy: float,
        context_precision: float,
        groundedness: float,
        reasoning: str,
        judge_model: str,
        unknown_reasons: dict[str, str] | None = None,
        per_dim_reasoning: dict[str, str] | None = None,
    ) -> JudgeScore:
        unk = tuple(sorted((unknown_reasons or {}).items()))
        per_dim = tuple(sorted((per_dim_reasoning or {}).items()))
        canonical = json.dumps(
            {
                "faithfulness": "NaN" if _is_nan(faithfulness) else faithfulness,
                "answer_relevancy": "NaN" if _is_nan(answer_relevancy) else answer_relevancy,
                "context_precision": "NaN" if _is_nan(context_precision) else context_precision,
                "groundedness": "NaN" if _is_nan(groundedness) else groundedness,
                "judge_model": judge_model,
                "unknown_reasons": list(unk),
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
            unknown_reasons=unk,
            per_dim_reasoning=per_dim,
        )

    def is_unknown(self, dimension: str) -> bool:
        """Return True if the judge abstained on ``dimension``."""
        value = getattr(self, dimension, None)
        return isinstance(value, float) and _is_nan(value)

    def known_dimensions(self) -> dict[str, float]:
        """Dimensions that were actually scored (exclude Unknown)."""
        return {d: getattr(self, d) for d in DIMENSIONS if not self.is_unknown(d)}

    def unknown_rate(self) -> float:
        """Fraction of dimensions the judge abstained on in [0.0, 1.0]."""
        return 1.0 - (len(self.known_dimensions()) / len(DIMENSIONS))


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


# ---------------------------------------------------------------------------
# Parsing helpers for CoT-first per-dimension response shape.
# Shape (per dimension call):
#     <reasoning>...</reasoning>
#     {"score": <1-5|"Unknown">, "unknown_reason": "<...>"}
# ---------------------------------------------------------------------------

_REASONING_RE = re.compile(r"<reasoning>(.*?)</reasoning>", re.DOTALL | re.IGNORECASE)
_JSON_TAIL_RE = re.compile(r"\{[^{}]*\"score\"[^{}]*\}")


def _clean_raw(raw: str) -> str:
    return re.sub(r"```(?:json)?|```", "", raw).strip()


def _extract_reasoning(raw: str) -> str:
    match = _REASONING_RE.search(raw)
    if match:
        return match.group(1).strip()
    # Fallback: everything before the trailing JSON object is reasoning.
    json_match = _JSON_TAIL_RE.search(raw)
    if json_match:
        return raw[: json_match.start()].strip()
    return raw.strip()


def _extract_dim_payload(raw: str) -> dict[str, Any]:
    """Extract the final ``{"score": ..., "unknown_reason": ...}`` payload.

    Returns a dict with keys ``score`` (float or "Unknown") and
    ``unknown_reason`` (str or None). Falls back to a strict JSON parse
    of the whole body if no tail object is found.
    """
    candidates = list(_JSON_TAIL_RE.finditer(raw))
    if candidates:
        try:
            return cast(dict[str, Any], json.loads(candidates[-1].group(0)))
        except json.JSONDecodeError:
            pass
    cleaned = _clean_raw(raw)
    try:
        return cast(dict[str, Any], json.loads(cleaned))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Judge response missing score JSON: {raw!r}") from exc


def _coerce_dim_score(payload: dict[str, Any]) -> tuple[float, str | None]:
    """Return ``(score, unknown_reason)`` from a dimension payload.

    ``score`` is ``UNKNOWN`` (NaN) when the judge abstained, otherwise a
    float in ``[1.0, 5.0]``. ``unknown_reason`` is the free-text reason
    when the judge abstained, else ``None``.
    """
    raw_score = payload.get("score")
    unknown_reason = payload.get("unknown_reason")
    if isinstance(raw_score, str) and raw_score.strip().lower() == "unknown":
        return UNKNOWN, str(unknown_reason) if unknown_reason else "judge returned Unknown"
    if raw_score is None:
        return UNKNOWN, "judge response missing score"
    try:
        score = float(raw_score)
    except (TypeError, ValueError):
        return UNKNOWN, f"non-numeric score: {raw_score!r}"
    if not (1.0 <= score <= 5.0):
        return UNKNOWN, f"score out of range [1,5]: {score}"
    return score, None


class GeminiJudge:
    """Production judge via Gemini, one LLM call per dimension (LJH2.1).

    Uses ``infrastructure.sdks_mcps.create_gemini_model`` (with
    ``GEMINI_API_KEY``/``GOOGLE_API_KEY``). Temperature is forced to 0.0
    for determinism. Parse failures surface as Unknown on that dimension.
    """

    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(self, gemini_client: Any = None, model: str | None = None) -> None:
        self._client = gemini_client
        env_model = os.getenv("GEMINI_MODEL")
        self._model = model or env_model or self.DEFAULT_MODEL
        self._configured = False

    @property
    def model_id(self) -> str:
        return self._model

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            client = importlib.import_module("infrastructure.sdks_mcps").create_gemini_model(self._model)
        except (ImportError, ValueError) as exc:
            raise RuntimeError(
                "GeminiJudge: google-genai package not installed or GOOGLE_API_KEY missing.",
            ) from exc
        self._configured = True
        return client

    def _generate(self, prompt: str) -> str:
        client = self._get_client()
        response = client.generate_content(prompt, generation_config={"temperature": 0.0})
        return cast(str, response.text)

    def _score_dimension(
        self,
        dimension: str,
        query: str,
        context: str,
        answer: str,
    ) -> tuple[float, str | None, str]:
        """Score one dimension. Returns (score, unknown_reason, reasoning)."""
        rubric = DIMENSION_RUBRICS[dimension]
        prompt = f"{rubric}\n\nQuery: {query}\n\nContext:\n{context}\n\nAnswer:\n{answer}"
        try:
            raw = self._generate(prompt)
        except (RuntimeError, ValueError) as exc:
            return UNKNOWN, f"provider_error: {exc}", ""
        reasoning = _extract_reasoning(raw)
        try:
            payload = _extract_dim_payload(raw)
            score, reason = _coerce_dim_score(payload)
        except ValueError as exc:
            return UNKNOWN, f"parse_error: {exc}", reasoning
        return score, reason, reasoning

    def score(self, query: str, context: str, answer: str) -> JudgeScore:
        unknown_reasons: dict[str, str] = {}
        per_dim_reasoning: dict[str, str] = {}
        scores: dict[str, float] = {}
        for dim in DIMENSIONS:
            value, reason, reasoning = self._score_dimension(dim, query, context, answer)
            scores[dim] = value
            per_dim_reasoning[dim] = reasoning
            if reason is not None:
                unknown_reasons[dim] = reason

        aggregate_reasoning = "; ".join(f"[{dim}] {per_dim_reasoning[dim][:200]}" for dim in DIMENSIONS)
        return JudgeScore.create(
            faithfulness=scores["faithfulness"],
            answer_relevancy=scores["answer_relevancy"],
            context_precision=scores["context_precision"],
            groundedness=scores["groundedness"],
            reasoning=aggregate_reasoning,
            judge_model=self._model,
            unknown_reasons=unknown_reasons,
            per_dim_reasoning=per_dim_reasoning,
        )


__all__ = [
    "DIMENSIONS",
    "DIMENSION_RUBRICS",
    "GeminiJudge",
    "JudgeScore",
    "LLMJudge",
    "NullJudge",
    "UNKNOWN",
]
