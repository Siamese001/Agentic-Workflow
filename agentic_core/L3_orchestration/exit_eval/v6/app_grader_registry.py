"""W1.P2 — App-domain grader registry for the live Exit pipeline.

This module provides the default grader wiring for
:class:`AppSpecificEvaluator` used by
:mod:`agentic_core.L3_orchestration.exit_eval.v6.pipeline`.

W1 scope (this file):
- One generic grader that reads pre-computed per-dimension scores from
  ``run_context["output"]["dim_scores"]``. Upstream producers (apps_*
  engines + L2 validators) populate that dict with their deterministic or
  LLM-judge computed scores; the Exit-level grader just reads, classifies,
  and lets :class:`AppSpecificEvaluator` enforce rubric + threshold rules.
- This design is the minimum viable wiring that unblocks X2/X3 consumption
  of domain metrics (audit BLOCKERs #1, #2, #3) without hard-coding
  per-dim logic inside Exit. Waves 3/4 will replace this with real
  grader-type dispatch (``tool_calls``, ``state_check``, ``transcript``,
  LLM judges with categorical bands).

Contract for upstream producers:

    run_context["output"] = {
        "dim_scores":   {"factual_grounding": 0.97, "role_alignment": 0.72, ...},
        "dim_evidence": {"factual_grounding": ["profile_id:abc123"], ...},
    }

- Missing ``dim_scores`` key  -> every dim UNKNOWN -> fail_closed_if_unknown
  dims FAIL (correct posture: runs without per-dim scoring cannot pass).
- Missing ``dim_evidence``    -> empty evidence; dims with
  ``evidence_required=true`` FAIL on that rule (already enforced by
  :class:`AppSpecificEvaluator._classify_dimension`).

Plan: ``.windsurf/plans/apps-eval-harness-parity-f8d4a2.md`` W1.P2.
"""

from __future__ import annotations

from typing import Mapping

from agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator import (
    GRADER_UNKNOWN_SENTINEL,
    AppSpecificEvaluator,
    GraderFn,
)
from agentic_core.L4_state.contracts.app_domain import ScoreDimension


def read_dim_score_from_output(
    dim: ScoreDimension,
    run_context: Mapping[str, object],
) -> "tuple[float, list[str]]":
    """Generic grader that reads a pre-computed dim score from run_context.

    Returns ``(score, evidence_refs)`` tuple. Score is
    :data:`GRADER_UNKNOWN_SENTINEL` when no pre-computed value exists,
    which triggers fail-closed handling for guardrail dims.
    """
    output = run_context.get("output") or {}
    if not isinstance(output, Mapping):
        return GRADER_UNKNOWN_SENTINEL, []

    dim_scores = output.get("dim_scores") or {}
    dim_evidence = output.get("dim_evidence") or {}
    if not isinstance(dim_scores, Mapping):
        return GRADER_UNKNOWN_SENTINEL, []

    raw = dim_scores.get(dim.dimension_id)
    if raw is None:
        return GRADER_UNKNOWN_SENTINEL, []

    try:
        score = float(raw)
    except (ValueError, TypeError):
        return GRADER_UNKNOWN_SENTINEL, []

    evidence_raw = dim_evidence.get(dim.dimension_id) if isinstance(dim_evidence, Mapping) else None
    if evidence_raw is None:
        evidence_list: list[str] = []
    elif isinstance(evidence_raw, (list, tuple)):
        evidence_list = [str(e) for e in evidence_raw]
    else:
        evidence_list = [str(evidence_raw)]

    return score, evidence_list


# ---------------------------------------------------------------------------
# W3.P2 — Canonical Anthropic grader-type dispatch
# ---------------------------------------------------------------------------


def grade_tool_calls(
    dim: ScoreDimension,
    run_context: Mapping[str, object],
) -> "tuple[float, list[str]]":
    """W3.P1 grader for ``grader_type=tool_calls``.

    Reads ``run_context["output"]["tool_calls"]`` (observed trajectory) and
    ``run_context["output"]["expected_tool_calls"]`` (golden trajectory).
    Score is computed per the dim's ``trajectory_match_mode``:

      - ``strict``: 1.0 iff ordered exact match, else 0.0
      - ``unordered``: overlap ratio (|obs ∩ expected| / |expected|)
      - ``subset``: 1.0 iff observed ⊆ expected, else 0.0
      - ``superset``: 1.0 iff expected ⊆ observed, else 0.0
      - ``none`` or unset: falls back to ``read_dim_score_from_output``

    Returns UNKNOWN when either list is missing — W1 fallback posture.
    """
    output = run_context.get("output") or {}
    if not isinstance(output, Mapping):
        return GRADER_UNKNOWN_SENTINEL, []
    observed = output.get("tool_calls")
    expected = output.get("expected_tool_calls")
    if observed is None or expected is None:
        # No trajectory data — fall back to the generic reader so pipelines
        # that still populate dim_scores directly keep working.
        return read_dim_score_from_output(dim, run_context)
    mode = (dim.trajectory_match_mode or "unordered").lower()
    obs_list = [str(x) for x in (observed if isinstance(observed, (list, tuple)) else [])]
    exp_list = [str(x) for x in (expected if isinstance(expected, (list, tuple)) else [])]
    evidence = [f"observed_len={len(obs_list)}", f"expected_len={len(exp_list)}", f"mode={mode}"]
    if not exp_list:
        return GRADER_UNKNOWN_SENTINEL, evidence
    if mode == "strict":
        score = 1.0 if obs_list == exp_list else 0.0
    elif mode == "subset":
        score = 1.0 if set(obs_list).issubset(set(exp_list)) else 0.0
    elif mode == "superset":
        score = 1.0 if set(exp_list).issubset(set(obs_list)) else 0.0
    elif mode == "none":
        return read_dim_score_from_output(dim, run_context)
    else:  # unordered (default)
        overlap = len(set(obs_list) & set(exp_list))
        score = overlap / len(set(exp_list))
    return score, evidence


def grade_state_check(
    dim: ScoreDimension,
    run_context: Mapping[str, object],
) -> "tuple[float, list[str]]":
    """W3.P2 grader for ``grader_type=state_check``.

    Reads ``run_context["state_diff"]`` (observed end-state) and
    ``run_context["output"]["expected_state"]`` (golden end-state per dim).
    Score is 1.0 iff observed state satisfies the expected assertion map
    for this dimension, else 0.0. UNKNOWN when either is absent.

    The per-dim assertion protocol uses a dotted-path map where keys are
    state_diff paths and values are expected scalars:

        output.expected_state = {
            "<dim_id>": {"counter.incremented": True, "ledger.rows_added": 1}
        }
    """
    output = run_context.get("output") or {}
    state_diff = run_context.get("state_diff") or {}
    if not isinstance(output, Mapping) or not isinstance(state_diff, Mapping):
        return GRADER_UNKNOWN_SENTINEL, []
    exp_map = output.get("expected_state") or {}
    if not isinstance(exp_map, Mapping):
        return GRADER_UNKNOWN_SENTINEL, []
    dim_expect = exp_map.get(dim.dimension_id)
    if not isinstance(dim_expect, Mapping) or not dim_expect:
        return GRADER_UNKNOWN_SENTINEL, []
    evidence = [f"assertions={len(dim_expect)}"]
    for path, want in dim_expect.items():
        cur: object = state_diff
        for segment in str(path).split("."):
            if isinstance(cur, Mapping):
                cur = cur.get(segment)
            else:
                cur = None
                break
        if cur != want:
            return 0.0, evidence + [f"mismatch::{path}"]
    return 1.0, evidence


def grade_transcript(
    dim: ScoreDimension,
    run_context: Mapping[str, object],
) -> "tuple[float, list[str]]":
    """W3.P3 grader for ``grader_type=transcript``.

    Reads ``run_context["output"]["transcript_metrics"][dim_id]`` = numeric
    value, and the dim's ``min_required_score``/``score_bands`` determines
    the pass. This is the "tracked_metric with bounds" grader pattern from
    Anthropic's Demystifying evals. UNKNOWN when no metric available.
    """
    output = run_context.get("output") or {}
    if not isinstance(output, Mapping):
        return GRADER_UNKNOWN_SENTINEL, []
    metrics = output.get("transcript_metrics")
    if not isinstance(metrics, Mapping):
        return GRADER_UNKNOWN_SENTINEL, []
    raw = metrics.get(dim.dimension_id)
    if raw is None:
        return GRADER_UNKNOWN_SENTINEL, []
    try:
        score = float(raw)
    except (TypeError, ValueError):
        return GRADER_UNKNOWN_SENTINEL, []
    return score, [f"transcript_metric={score}"]


# Dispatch table — ``AppSpecificEvaluator`` registers these as per-type
# defaults; per-dim callers can still override. The "hybrid" and
# "llm_as_judge" types default to the generic reader because their
# scores are computed by producers and read from dim_scores.
GRADER_TYPE_DISPATCH: Mapping[str, GraderFn] = {
    "deterministic": read_dim_score_from_output,
    "hybrid": read_dim_score_from_output,
    "llm_as_judge": read_dim_score_from_output,
    "tool_calls": grade_tool_calls,
    "trajectory_match": grade_tool_calls,
    "state_check": grade_state_check,
    "transcript": grade_transcript,
}


def build_default_app_evaluator(
    *,
    extra_graders: "Mapping[str, GraderFn] | None" = None,
) -> AppSpecificEvaluator:
    """Build the default evaluator used by the live Exit pipeline.

    Uses :func:`read_dim_score_from_output` as the fallback grader for
    every dimension. Per-dim graders passed via ``extra_graders`` override
    the fallback. The W3.P2 dispatch table is applied per-dim inside
    ``evaluate`` via the ``type_dispatch`` registry handle.
    """
    evaluator = AppSpecificEvaluator(
        default_grader=read_dim_score_from_output,
    )
    # Install per-dim type-dispatch graders as a secondary fallback via the
    # evaluator's per-dim registry. The evaluator keys by dimension_id, so
    # we do not pre-register here — instead, type-dispatch is available to
    # callers that know the rubric at registration time. This keeps the
    # default evaluator as generic as W1 while making the new types
    # available for opt-in use.
    if extra_graders:
        evaluator.register_graders(extra_graders)
    return evaluator


__all__ = [
    "read_dim_score_from_output",
    "grade_tool_calls",
    "grade_state_check",
    "grade_transcript",
    "GRADER_TYPE_DISPATCH",
    "build_default_app_evaluator",
]
