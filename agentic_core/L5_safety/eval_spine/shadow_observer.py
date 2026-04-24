"""Shadow observer — converts SealedL2Artifact → ExitDecision, write-only.

Design (Author-Gate 2026-04-23, confidence 0.86):
  - Observer posture: never gates, never raises upward, never mutates state.
  - Gated by env var ``EVAL_SPINE_SHADOW=1`` (default off).
  - Produces ``artifacts/eval_spine/<trace_id>.json`` on each sealed artifact.
  - Any failure is swallowed + logged to stderr; the live exit path is
    unaffected.

This module intentionally does NOT:
  - touch ADR-023 surfaces
  - change the existing ExitControlGate decision
  - require any rubric / model / LLM-judge configuration
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping

from agentic_core.L5_safety.eval_spine.budget_envelope import BudgetEnvelope
from agentic_core.L5_safety.eval_spine.exit_eval import (
    ExitEvalPolicy,
    ExitEvalResult,
    SealedArtifact,
    evaluate_exit,
)

if TYPE_CHECKING:
    from agentic_core.L2_execution.types.sealed_l2_artifact import SealedL2Artifact


_SHADOW_FLAG = "EVAL_SPINE_SHADOW"
_DEFAULT_OUTPUT_ROOT = Path("artifacts/eval_spine")
_logger = logging.getLogger(__name__)


def is_shadow_enabled() -> bool:
    """Return True iff ``EVAL_SPINE_SHADOW`` is set to a truthy value."""
    raw = os.environ.get(_SHADOW_FLAG, "")
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _coerce_tool_calls(raw: Any) -> list[Mapping[str, str]]:
    """Accept only canonical-shape records ({tool, args_hash}); drop others."""
    if not isinstance(raw, list):
        return []
    canonical: list[Mapping[str, str]] = []
    for entry in raw:
        if not isinstance(entry, Mapping):
            continue
        tool = entry.get("tool")
        args_hash = entry.get("args_hash")
        if isinstance(tool, str) and isinstance(args_hash, str) and tool:
            canonical.append({"tool": tool, "args_hash": args_hash})
    return canonical


def sealed_l2_to_eval_spine(artifact: "SealedL2Artifact") -> SealedArtifact:
    """Convert an L2 sealed artifact into an eval_spine.SealedArtifact.

    The conversion is forgiving: missing fields resolve to safe defaults.
    Never raises.
    """
    exec_trace: Mapping[str, Any] = artifact.exec_trace or {}
    evidence: Mapping[str, Any] = artifact.evidence_bundle or {}
    from agentic_core.L2_execution.types.sealed_l2_artifact import (
        TerminalClassification,
    )

    failure = artifact.terminal_classification != TerminalClassification.SUCCESS
    tool_calls = _coerce_tool_calls(exec_trace.get("tool_calls"))

    return SealedArtifact(
        request_id=artifact.artifact_id or "unknown",
        trace_id=artifact.trace_id or "unknown",
        answer_text=str(evidence.get("answer_text", "")),
        artifact_payload=artifact.state_diff or None,
        context_text=str(evidence.get("context_text", "")),
        predicted_tool_calls=tuple(tool_calls),
        retry_count=int(exec_trace.get("retry_count", 0) or 0),
        failure=failure,
        latency_ms=int(exec_trace.get("latency_ms", 0) or 0),
        tokens_consumed=int(exec_trace.get("tokens", 0) or 0),
        cost_usd_consumed=float(exec_trace.get("cost_usd", 0.0) or 0.0),
        session_id=exec_trace.get("session_id"),
        tenant=exec_trace.get("tenant"),
        agent_class=exec_trace.get("agent_class"),
        agent_version=exec_trace.get("agent_version"),
    )


def _default_envelope() -> BudgetEnvelope:
    """Generous default envelope — shadow mode does not enforce budgets."""
    return BudgetEnvelope(
        tokens_max=None,
        latency_ms_max=None,
        tool_calls_max=None,
        cost_usd_max=None,
        origin="shadow_default",
    )


def _default_policy(policy_snapshot: str) -> ExitEvalPolicy:
    return ExitEvalPolicy(policy_snapshot=policy_snapshot)


def emit_shadow_exit_decision(
    artifact: "SealedL2Artifact",
    *,
    policy_snapshot: str = "shadow-unknown",
    output_root: Path | None = None,
    envelope: BudgetEnvelope | None = None,
    policy: ExitEvalPolicy | None = None,
) -> Path | None:
    """Compute + write an ExitDecision artifact. Return the path, or None on skip.

    Any exception is caught and logged; callers never see a raise. This is
    the only public entry point; call sites should use it inside their own
    try/except defensively.
    """
    if not is_shadow_enabled():
        return None

    try:
        sealed = sealed_l2_to_eval_spine(artifact)
        env = envelope or _default_envelope()
        pol = policy or _default_policy(policy_snapshot)
        result: ExitEvalResult = evaluate_exit(sealed, env, pol)
        root = output_root or _DEFAULT_OUTPUT_ROOT
        root.mkdir(parents=True, exist_ok=True)
        target = root / f"{sealed.trace_id}.json"
        payload = result.exit_decision.to_dict()
        with target.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        _logger.debug(
            "eval_spine shadow wrote %s (disposition=%s reason=%s)",
            target,
            result.exit_decision.disposition,
            result.exit_decision.reason_code,
        )
        return target
    except (  # guardian: allow-return-none-swallow -- shadow observer must never surface exceptions to live exit path; None signals no-shadow-written per Author-Gate 2026-04-23
        OSError,
        ValueError,
        TypeError,
        AttributeError,
    ) as exc:
        _logger.warning("eval_spine shadow emission failed: %s", exc)
        return None


__all__ = [
    "emit_shadow_exit_decision",
    "is_shadow_enabled",
    "sealed_l2_to_eval_spine",
]
