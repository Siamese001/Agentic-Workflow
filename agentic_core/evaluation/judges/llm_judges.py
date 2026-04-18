"""LLM-backed judges — evaluation requiring LLM inference.

Each judge consumes an EvidenceBundle and a JudgeProvider, renders a
prompt from the rubric template, sends it to the LLM, and parses the
structured response into a JudgeVerdict.

Judges implemented:
- GOV-001: Policy compliance review
- GOV-003: Orchestration completeness review
- SEC-001: Dynamic execution safety review
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from agentic_core.evaluation.judges.rubric_engine import RubricEngine
from agentic_core.evaluation.judges.types import (
    EvidenceBundle,
    EvidenceItem,
    JudgeProvider,
    JudgeVerdict,
    ScoringCriterion,
    VerdictOutcome,
)

_log = logging.getLogger(__name__)


def _verdict_id() -> str:
    return uuid.uuid4().hex[:12]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _format_adg_edges(bundle: EvidenceBundle) -> str:
    """Format ADG edges as readable text for LLM prompts."""
    lines: list[str] = []
    for rel, edges in bundle.adg_edges.items():
        lines.append(f"\n## {rel} ({len(edges)} edges)")
        for edge in edges[:20]:
            target = edge.get("target_name", edge.get("source_name", "?"))
            line_no = edge.get("line_no", 0)
            symbol = edge.get("symbol", "")
            lines.append(f"  - {target} (line {line_no}, symbol: {symbol})")
        if len(edges) > 20:
            lines.append(f"  ... and {len(edges) - 20} more")
    return "\n".join(lines) if lines else "(no ADG edges)"


def _format_source_snippets(bundle: EvidenceBundle) -> str:
    """Format source snippets for LLM prompts."""
    parts: list[str] = []
    for snippet in bundle.source_snippets[:5]:
        header = f"# {snippet.file_path}:{snippet.start_line}-{snippet.end_line}"
        if snippet.symbol:
            header += f" ({snippet.symbol})"
        parts.append(f"{header}\n{snippet.content}")
    if len(bundle.source_snippets) > 5:
        parts.append(f"... and {len(bundle.source_snippets) - 5} more snippets")
    return "\n\n".join(parts) if parts else "(no source code available)"


def _compute_weighted_score(
    criteria_scores: dict[str, float],
    criteria: tuple[ScoringCriterion, ...],
) -> float:
    """Compute weighted average from criteria scores."""
    if not criteria_scores or not criteria:
        return 0.0

    total_weight = 0.0
    weighted_sum = 0.0
    for c in criteria:
        score = criteria_scores.get(c.criterion_id, 0.0)
        weighted_sum += score * c.weight
        total_weight += c.weight

    return round(weighted_sum / total_weight, 4) if total_weight > 0 else 0.0


def _outcome_from_score(
    score: float,
    pass_threshold: float,
    warn_threshold: float,
) -> str:
    """Determine outcome from score and thresholds."""
    if score >= pass_threshold:
        return VerdictOutcome.PASS.value
    elif score >= warn_threshold:
        return VerdictOutcome.WARN.value
    else:
        return VerdictOutcome.FAIL.value


async def judge_gov_001(
    bundle: EvidenceBundle,
    provider: JudgeProvider,
    rubric_engine: RubricEngine,
) -> JudgeVerdict:
    """GOV-001: Policy Compliance Review.

    LLM evaluates whether guardrail calls and policy reads are substantive.
    """
    rubric = rubric_engine.get("GOV-001")
    if not rubric:
        return JudgeVerdict(
            verdict_id=_verdict_id(),
            target=bundle.target,
            dimension="governance_quality",
            rubric_id="GOV-001",
            outcome=VerdictOutcome.ERROR.value,
            score=0.0,
            reasoning="Rubric GOV-001 not found",
            provider_id=provider.provider_id,
            created_at=_now_iso(),
        )

    source_code = _format_source_snippets(bundle)
    adg_edges = _format_adg_edges(bundle)

    prompt = (
        f"You are evaluating governance compliance for module: {bundle.target}\n\n"
        f"Source code:\n```python\n{source_code}\n```\n\n"
        f"ADG governance edges:\n{adg_edges}\n\n"
        f"Score each criterion 0.0-1.0:\n"
        f"1. guardrail_substantive: Are guardrail calls using meaningful parameters?\n"
        f"2. policy_integration: Are policy reads integrated into logic flow?\n\n"
        f'Respond ONLY with valid JSON: {{"guardrail_substantive": <0-1>, '
        f'"policy_integration": <0-1>, "reasoning": "<text>"}}'
    )

    try:
        result = await provider.judge(prompt, "GOV-001")
    except (RuntimeError, ValueError, TypeError, KeyError) as exc:
        _log.warning("[judge_gov_001] Provider error: %s", exc)
        return JudgeVerdict(
            verdict_id=_verdict_id(),
            target=bundle.target,
            dimension="governance_quality",
            rubric_id="GOV-001",
            outcome=VerdictOutcome.ERROR.value,
            score=0.0,
            reasoning=f"Provider error: {exc}",
            provider_id=provider.provider_id,
            adg_digest=bundle.adg_digest,
            evidence_hash=bundle.evidence_hash,
            created_at=_now_iso(),
        )

    criteria_scores = result.get("criteria_scores", {})
    score = _compute_weighted_score(criteria_scores, rubric.scoring_criteria)
    if not criteria_scores:
        score = result.get("score", 0.0)

    outcome = _outcome_from_score(score, rubric.pass_threshold, rubric.warn_threshold)
    reasoning = result.get("reasoning", "")

    return JudgeVerdict(
        verdict_id=_verdict_id(),
        target=bundle.target,
        dimension="governance_quality",
        rubric_id="GOV-001",
        outcome=outcome,
        score=score,
        reasoning=reasoning,
        severity=rubric.severity,
        adg_digest=bundle.adg_digest,
        provider_id=provider.provider_id,
        evidence_hash=bundle.evidence_hash,
        created_at=_now_iso(),
    )


async def judge_gov_003(
    bundle: EvidenceBundle,
    provider: JudgeProvider,
    rubric_engine: RubricEngine,
) -> JudgeVerdict:
    """GOV-003: Orchestration Completeness Review.

    LLM evaluates dispatch tracking, error handling, and healing integration.
    """
    rubric = rubric_engine.get("GOV-003")
    if not rubric:
        return JudgeVerdict(
            verdict_id=_verdict_id(),
            target=bundle.target,
            dimension="governance_quality",
            rubric_id="GOV-003",
            outcome=VerdictOutcome.ERROR.value,
            score=0.0,
            reasoning="Rubric GOV-003 not found",
            provider_id=provider.provider_id,
            created_at=_now_iso(),
        )

    source_code = _format_source_snippets(bundle)
    adg_edges = _format_adg_edges(bundle)

    prompt = (
        f"You are evaluating orchestration completeness for module: {bundle.target}\n\n"
        f"Source code:\n```python\n{source_code}\n```\n\n"
        f"ADG orchestration edges:\n{adg_edges}\n\n"
        f"Score each criterion 0.0-1.0:\n"
        f"1. dispatch_tracking: Do agent dispatches include lineage/trace IDs?\n"
        f"2. error_handling: Are failure escalation paths present?\n"
        f"3. healing_integration: Are healing mechanisms integrated?\n\n"
        f'Respond ONLY with valid JSON: {{"dispatch_tracking": <0-1>, '
        f'"error_handling": <0-1>, "healing_integration": <0-1>, "reasoning": "<text>"}}'
    )

    try:
        result = await provider.judge(prompt, "GOV-003")
    except (RuntimeError, ValueError, TypeError, KeyError) as exc:
        _log.warning("[judge_gov_003] Provider error: %s", exc)
        return JudgeVerdict(
            verdict_id=_verdict_id(),
            target=bundle.target,
            dimension="governance_quality",
            rubric_id="GOV-003",
            outcome=VerdictOutcome.ERROR.value,
            score=0.0,
            reasoning=f"Provider error: {exc}",
            provider_id=provider.provider_id,
            adg_digest=bundle.adg_digest,
            evidence_hash=bundle.evidence_hash,
            created_at=_now_iso(),
        )

    criteria_scores = result.get("criteria_scores", {})
    score = _compute_weighted_score(criteria_scores, rubric.scoring_criteria)
    if not criteria_scores:
        score = result.get("score", 0.0)

    outcome = _outcome_from_score(score, rubric.pass_threshold, rubric.warn_threshold)
    reasoning = result.get("reasoning", "")

    return JudgeVerdict(
        verdict_id=_verdict_id(),
        target=bundle.target,
        dimension="governance_quality",
        rubric_id="GOV-003",
        outcome=outcome,
        score=score,
        reasoning=reasoning,
        severity=rubric.severity,
        adg_digest=bundle.adg_digest,
        provider_id=provider.provider_id,
        evidence_hash=bundle.evidence_hash,
        created_at=_now_iso(),
    )


async def judge_sec_001(
    bundle: EvidenceBundle,
    provider: JudgeProvider,
    rubric_engine: RubricEngine,
) -> JudgeVerdict:
    """SEC-001: Dynamic Execution Safety Review.

    LLM reviews modules with eval/exec/getattr for safety practices.
    """
    rubric = rubric_engine.get("SEC-001")
    if not rubric:
        return JudgeVerdict(
            verdict_id=_verdict_id(),
            target=bundle.target,
            dimension="security",
            rubric_id="SEC-001",
            outcome=VerdictOutcome.ERROR.value,
            score=0.0,
            reasoning="Rubric SEC-001 not found",
            provider_id=provider.provider_id,
            created_at=_now_iso(),
        )

    # Skip if no dynamic execution edges
    dynamic_edges = bundle.adg_edges.get("invokes_eval", [])
    dynamic_edges += bundle.adg_edges.get("invokes_getattr_dynamic", [])
    if not dynamic_edges:
        return JudgeVerdict(
            verdict_id=_verdict_id(),
            target=bundle.target,
            dimension="security",
            rubric_id="SEC-001",
            outcome=VerdictOutcome.SKIP.value,
            score=1.0,
            reasoning="No dynamic execution edges — module does not use eval/exec/getattr",
            severity=rubric.severity,
            adg_digest=bundle.adg_digest,
            provider_id=provider.provider_id,
            evidence_hash=bundle.evidence_hash,
            created_at=_now_iso(),
        )

    source_code = _format_source_snippets(bundle)
    adg_edges = _format_adg_edges(bundle)

    prompt = (
        f"You are a security reviewer evaluating dynamic execution in module: {bundle.target}\n\n"
        f"Source code around dynamic calls:\n```python\n{source_code}\n```\n\n"
        f"ADG dynamic execution edges:\n{adg_edges}\n\n"
        f"Score each criterion 0.0-1.0:\n"
        f"1. input_validation: Are inputs to eval/exec/getattr validated?\n"
        f"2. scope_restriction: Is dynamic execution scoped minimally?\n"
        f"3. documentation: Is the rationale documented?\n\n"
        f'Respond ONLY with valid JSON: {{"input_validation": <0-1>, '
        f'"scope_restriction": <0-1>, "documentation": <0-1>, "reasoning": "<text>"}}'
    )

    try:
        result = await provider.judge(prompt, "SEC-001")
    except (RuntimeError, ValueError, TypeError, KeyError) as exc:
        _log.warning("[judge_sec_001] Provider error: %s", exc)
        return JudgeVerdict(
            verdict_id=_verdict_id(),
            target=bundle.target,
            dimension="security",
            rubric_id="SEC-001",
            outcome=VerdictOutcome.ERROR.value,
            score=0.0,
            reasoning=f"Provider error: {exc}",
            provider_id=provider.provider_id,
            adg_digest=bundle.adg_digest,
            evidence_hash=bundle.evidence_hash,
            created_at=_now_iso(),
        )

    criteria_scores = result.get("criteria_scores", {})
    score = _compute_weighted_score(criteria_scores, rubric.scoring_criteria)
    if not criteria_scores:
        score = result.get("score", 0.0)

    outcome = _outcome_from_score(score, rubric.pass_threshold, rubric.warn_threshold)
    reasoning = result.get("reasoning", "")

    evidence_items = [
        EvidenceItem(
            evidence_type="dynamic_execution",
            key=edge.get("symbol", "unknown"),
            value=json.dumps(edge),
            file_path=edge.get("source_file", ""),
            line_no=edge.get("line_no", 0),
        )
        for edge in dynamic_edges[:10]
    ]

    return JudgeVerdict(
        verdict_id=_verdict_id(),
        target=bundle.target,
        dimension="security",
        rubric_id="SEC-001",
        outcome=outcome,
        score=score,
        reasoning=reasoning,
        evidence_items=tuple(evidence_items),
        severity=rubric.severity,
        adg_digest=bundle.adg_digest,
        provider_id=provider.provider_id,
        evidence_hash=bundle.evidence_hash,
        created_at=_now_iso(),
    )


# ===================================================================
# Registry — maps rubric_id to LLM judge function
# ===================================================================

LLM_JUDGES: dict[str, Any] = {
    "GOV-001": judge_gov_001,
    "GOV-003": judge_gov_003,
    "SEC-001": judge_sec_001,
}


async def run_llm_judge(
    rubric_id: str,
    bundle: EvidenceBundle,
    provider: JudgeProvider,
    rubric_engine: RubricEngine,
) -> JudgeVerdict | None:
    """Run an LLM judge by rubric ID.

    Returns None if rubric_id is not an LLM judge.
    """
    judge_fn = LLM_JUDGES.get(rubric_id)
    if judge_fn is None:
        return None
    return await judge_fn(bundle, provider, rubric_engine)


__all__ = [
    "LLM_JUDGES",
    "judge_gov_001",
    "judge_gov_003",
    "judge_sec_001",
    "run_llm_judge",
]
