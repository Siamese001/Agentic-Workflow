"""Qwen judge gateway — rubric-YAML-driven LLM-as-Judge surface on top of
the existing Qwen vLLM infrastructure.

This module is the **judge** counterpart to ``QwenInferenceGateway``
(generator surface). Judge calls are structurally different from
generator calls:

- **Determinism**: ``temperature=0.0`` (greedy decode) and a content-
  derived seed so a given (rubric, candidate, context) tuple yields the
  same composite every time. Generator calls use ``temperature>=0.7`` for
  diversity; judges must not.
- **Output shape**: judges return a :class:`JudgeVerdict` carrying a
  composite score, soft-dimension scores, caller-supplied hard-gate
  results, rationale, and a ``first_failed_gate`` sentinel. Generators
  return free text. The verdict shape mirrors
  ``apps_eval/engines/narrative_judge_scorer.JudgeVerdict`` so callers
  that already consume that shape (NarrativeJudgeScorer) can adopt this
  gateway with minimal refactor.
- **Preflight + demotion**: when
  :func:`vllm_health_probe.is_qwen_available` returns False, the gateway
  returns a deterministic-fallback verdict with
  ``first_failed_gate="qwen_preflight_failed"`` and
  ``fallback_reason="preflight_failed"``. No exception is raised.
- **Closed-loop evidence**: every invocation emits a ``JUDGE_DECISION:``
  marker via :mod:`tools.capture.append_marker`, drained into the
  canonical decision ledger by ``queue_to_ledger.py``. Pairs with the
  calibration harness (P1.3) for weekly judge-drift spot checks.

Hard-gate responsibility
------------------------
Hard gates are DOMAIN-SPECIFIC (anti-overfitting for résumé bullets,
regulatory disclosure for LIC outreach, requirement-coverage for RFP
sections). The gateway does NOT evaluate hard gates itself — the caller
pre-computes them and passes a list via
``JudgeRequest.pre_computed_hard_gates``. This keeps the gateway
layer-pure (L2 utility that wraps a model call) and lets every app
continue to own its hard-gate library. The gateway still respects them:
if any pre-computed gate failed, ``accepted=False`` and
``composite`` is ignored (hard-gate failure is a veto).

Rubric shape
------------
The gateway reads the same YAML shape used by ``narrative_judge.yaml``:

    rubric_id: <str>
    applies_to: [<hop_id>, ...]
    hard_gates:          # metadata only; caller evaluates
      - gate_id: <str>
        description: <str>
        failure_mode: instant_reject
    soft_dimensions:
      - dimension_id: <str>
        weight: <float>  # sum of all weights should be ~1.0
        min_score: <float>  # dimension veto if below
        judge_prompt: <str>  # per-dim rubric prompt
    composite_threshold: <float>  # default 0.85

Per-call the gateway constructs a single prompt listing every
``judge_prompt``, expects a JSON response of
``{dimension_id: float, ...}``, then computes the composite per the
weights in the rubric. When the model response is not strict JSON, the
gateway falls back to the deterministic heuristic (composite=0.0) and
records ``fallback_reason="parse_failure"``.

Layer purity
------------
Lives at ``agentic_core/L2_execution/healers/``. Imports L0 model-
registry constants (via ``QwenInferenceGateway``) and the L2
``vllm_health_probe``; never imports from ``apps_*``, ``L4``, or ``L5``.

Plan reference
--------------
``docs/archive/windsurf/legacy-tree/plans/apps-eval-qwen32b-rollout-b7c4d9.md`` Wave 1 (P1.1).
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from agentic_core.L2_execution.healers.vllm_health_probe import (
    is_qwen_available,
)
from agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway import (  # guardian: allow-layer-violation -- L2 judge wraps existing L3 Qwen inference gateway (same pattern as L2 ConfidenceAwareExecutor wrapping HealingRouter)
    QwenInferenceGateway,
    QwenInferenceRequest,
)

_LOGGER = logging.getLogger(__name__)

# Fallback sentinels for the rationale field so callers can grep for them.
_FALLBACK_PREFLIGHT: str = "preflight_failed"
_FALLBACK_PARSE: str = "parse_failure"
_FALLBACK_EMPTY: str = "empty_response"
_FALLBACK_EXCEPTION: str = "gateway_exception"

# Deterministic-fallback sentinel model id (distinguishes from real model runs
# in the ledger).
_DETERMINISTIC_FALLBACK_MODEL: str = "deterministic_fallback"

# Default rubric threshold when the YAML omits ``composite_threshold``.
_DEFAULT_COMPOSITE_THRESHOLD: float = 0.85


@dataclass(frozen=True)
class HardGateResult:
    """One hard-gate result passed in by the caller.

    Attributes:
        gate_id: Stable identifier (e.g. ``"provenance"``,
            ``"length_parity"``).
        passed: True when the gate accepts the candidate.
        detail: Short human-readable reason string.
    """

    gate_id: str
    passed: bool
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "passed": self.passed,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class JudgeRequest:
    """Input to :meth:`QwenJudgeGateway.judge`.

    Attributes:
        app_name: Calling app identifier (e.g. ``"apps_lic"``, used for
            marker / ledger provenance).
        rubric_path: Path to the YAML rubric.
        candidate_text: The sealed candidate to judge (single artifact).
        pre_computed_hard_gates: Caller-evaluated hard-gate results.
            Any False entry vetoes acceptance regardless of composite.
        context_metadata: Free-form dict merged into the prompt so
            per-request facets (jd_facets, company_facets, etc.) are
            available to the rubric dimensions that want them.
        max_tokens: Max completion budget. Default 2048.
        emit_marker: When True (default), emit a ``JUDGE_DECISION``
            marker on every call. Test fixtures set this False.
    """

    app_name: str
    rubric_path: Path
    candidate_text: str
    pre_computed_hard_gates: tuple[HardGateResult, ...] = ()
    context_metadata: dict[str, Any] = field(default_factory=dict)
    max_tokens: int = 2048
    emit_marker: bool = True


@dataclass(frozen=True)
class JudgeVerdict:
    """Result of :meth:`QwenJudgeGateway.judge`.

    Attributes:
        accepted: True iff every hard gate passed AND composite reached
            ``composite_threshold``.
        composite: Weighted soft-dimension score in [0.0, 1.0].
        hard_gates: Serialized caller-supplied hard-gate list.
        soft_scores: Per-dimension scores returned by the LLM (or empty
            on fallback).
        rationale: Short human-readable summary.
        first_failed_gate: gate_id of the first failing hard gate, or
            one of the ``_FALLBACK_*`` sentinels when the LLM call was
            not successful, or None when everything passed.
        model_used: Model identifier (the real Qwen model id on success;
            ``_DETERMINISTIC_FALLBACK_MODEL`` on preflight/parse/empty
            fallback).
        fallback_reason: Empty on success; sentinel string otherwise.
        latency_ms: End-to-end latency including preflight + inference.
        rubric_id: Loaded rubric id (or ``"<unknown>"`` when the YAML
            omits it).
        rubric_hash: SHA-256 of the rubric bytes (hex, 12-char prefix).
            Enables verdict-replay audits.
    """

    accepted: bool
    composite: float
    hard_gates: list[dict[str, Any]]
    soft_scores: dict[str, float]
    rationale: str
    first_failed_gate: str | None
    model_used: str
    fallback_reason: str
    latency_ms: float
    rubric_id: str
    rubric_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "composite": round(self.composite, 4),
            "hard_gates": list(self.hard_gates),
            "soft_scores": {k: round(v, 4) for k, v in self.soft_scores.items()},
            "rationale": self.rationale,
            "first_failed_gate": self.first_failed_gate,
            "model_used": self.model_used,
            "fallback_reason": self.fallback_reason,
            "latency_ms": round(self.latency_ms, 1),
            "rubric_id": self.rubric_id,
            "rubric_hash": self.rubric_hash,
        }


class QwenJudgeGateway:
    """Judge-mode wrapper over :class:`QwenInferenceGateway`.

    Apps adopt by instantiating once (typically in a composition root or
    per-orchestrator) and calling :meth:`judge` with a fresh
    :class:`JudgeRequest` per candidate. The gateway is safe to share
    across calls; it holds no per-call mutable state beyond the
    underlying ``QwenInferenceGateway`` singleton.

    Construction:

        gateway = QwenJudgeGateway()  # uses default QwenInferenceGateway
        # or inject for tests:
        gateway = QwenJudgeGateway(inference_gateway=fake_gw)
    """

    def __init__(
        self,
        inference_gateway: QwenInferenceGateway | None = None,
    ) -> None:
        self._inference = inference_gateway or QwenInferenceGateway()

    async def judge(self, request: JudgeRequest) -> JudgeVerdict:
        """Evaluate ``request.candidate_text`` against the rubric.

        Execution order:
        1. Load rubric + compute rubric hash.
        2. Check if any pre-computed hard gate failed — fast veto path.
        3. Preflight vLLM via :func:`is_qwen_available`. On False,
           return deterministic fallback.
        4. Build the judge prompt + invoke Qwen with ``temperature=0``.
        5. Parse the JSON response; compute composite per rubric
           weights. Any parse failure falls back deterministically.
        6. Emit ``JUDGE_DECISION`` marker (unless disabled).
        """
        started = time.time()

        rubric, rubric_hash = _load_rubric_with_hash(request.rubric_path)
        rubric_id = str(rubric.get("rubric_id", "<unknown>"))

        hard_gates_serialized: list[dict[str, Any]] = [
            hg.to_dict() for hg in request.pre_computed_hard_gates
        ]
        first_failed: str | None = next(
            (hg.gate_id for hg in request.pre_computed_hard_gates if not hg.passed),
            None,
        )

        # Fast-path hard-gate veto — no LLM call when a deterministic
        # hard gate already failed. Emits marker for audit trail.
        if first_failed is not None:
            verdict = JudgeVerdict(
                accepted=False,
                composite=0.0,
                hard_gates=hard_gates_serialized,
                soft_scores={},
                rationale=f"hard_gate_veto: {first_failed}",
                first_failed_gate=first_failed,
                model_used=_DETERMINISTIC_FALLBACK_MODEL,
                fallback_reason="hard_gate_veto",
                latency_ms=(time.time() - started) * 1000.0,
                rubric_id=rubric_id,
                rubric_hash=rubric_hash,
            )
            if request.emit_marker:
                _emit_judge_decision_marker(request, verdict)
            return verdict

        # Preflight: is local vLLM up and serving a Qwen model?
        if not is_qwen_available():
            verdict = JudgeVerdict(
                accepted=False,
                composite=0.0,
                hard_gates=hard_gates_serialized,
                soft_scores={},
                rationale="qwen_preflight_failed",
                first_failed_gate="qwen_preflight_failed",
                model_used=_DETERMINISTIC_FALLBACK_MODEL,
                fallback_reason=_FALLBACK_PREFLIGHT,
                latency_ms=(time.time() - started) * 1000.0,
                rubric_id=rubric_id,
                rubric_hash=rubric_hash,
            )
            if request.emit_marker:
                _emit_judge_decision_marker(request, verdict)
            return verdict

        # Inference — temperature=0 for greedy-deterministic decoding.
        prompt = _build_judge_prompt(
            rubric=rubric,
            candidate_text=request.candidate_text,
            context_metadata=request.context_metadata,
        )
        inference_request = QwenInferenceRequest(
            app_name=f"{request.app_name}:judge",
            prompt=prompt,
            max_tokens=request.max_tokens,
            temperature=0.0,
            use_cache=True,
        )

        try:
            inference_response = await self._inference.infer(inference_request)
        except (ValueError, TypeError, RuntimeError) as exc:
            verdict = JudgeVerdict(
                accepted=False,
                composite=0.0,
                hard_gates=hard_gates_serialized,
                soft_scores={},
                rationale=f"inference_exception: {type(exc).__name__}",
                first_failed_gate="inference_exception",
                model_used=_DETERMINISTIC_FALLBACK_MODEL,
                fallback_reason=_FALLBACK_EXCEPTION,
                latency_ms=(time.time() - started) * 1000.0,
                rubric_id=rubric_id,
                rubric_hash=rubric_hash,
            )
            if request.emit_marker:
                _emit_judge_decision_marker(request, verdict)
            return verdict

        if not inference_response.success or not (inference_response.response or "").strip():
            verdict = JudgeVerdict(
                accepted=False,
                composite=0.0,
                hard_gates=hard_gates_serialized,
                soft_scores={},
                rationale=f"inference_failed: {inference_response.error_message or 'empty_response'}",
                first_failed_gate="inference_failed",
                model_used=_DETERMINISTIC_FALLBACK_MODEL,
                fallback_reason=_FALLBACK_EMPTY,
                latency_ms=(time.time() - started) * 1000.0,
                rubric_id=rubric_id,
                rubric_hash=rubric_hash,
            )
            if request.emit_marker:
                _emit_judge_decision_marker(request, verdict)
            return verdict

        soft_scores = _parse_soft_scores(inference_response.response or "")
        if not soft_scores:
            verdict = JudgeVerdict(
                accepted=False,
                composite=0.0,
                hard_gates=hard_gates_serialized,
                soft_scores={},
                rationale="parse_failure: non-JSON or missing dimensions",
                first_failed_gate="parse_failure",
                model_used=inference_response.model_used,
                fallback_reason=_FALLBACK_PARSE,
                latency_ms=(time.time() - started) * 1000.0,
                rubric_id=rubric_id,
                rubric_hash=rubric_hash,
            )
            if request.emit_marker:
                _emit_judge_decision_marker(request, verdict)
            return verdict

        composite, dim_veto = _compose(soft_scores, rubric)
        threshold = float(rubric.get("composite_threshold", _DEFAULT_COMPOSITE_THRESHOLD))
        accepted = dim_veto is None and composite >= threshold

        rationale = (
            f"dim_veto:{dim_veto}"
            if dim_veto is not None
            else f"composite={composite:.3f} threshold={threshold:.2f}"
        )

        verdict = JudgeVerdict(
            accepted=accepted,
            composite=composite,
            hard_gates=hard_gates_serialized,
            soft_scores=soft_scores,
            rationale=rationale,
            first_failed_gate=dim_veto,
            model_used=inference_response.model_used,
            fallback_reason="",
            latency_ms=(time.time() - started) * 1000.0,
            rubric_id=rubric_id,
            rubric_hash=rubric_hash,
        )
        if request.emit_marker:
            _emit_judge_decision_marker(request, verdict)
        return verdict


# ---------------------------------------------------------------------------
# Module helpers
# ---------------------------------------------------------------------------


def _load_rubric_with_hash(path: Path) -> tuple[dict[str, Any], str]:
    """Load a rubric YAML and return ``(rubric_dict, sha256_prefix_12)``.

    Missing / unparseable rubrics return ``({}, "missing")`` so the
    gateway degrades gracefully rather than raising inside a judge call.
    """
    if not path.exists():
        return {}, "missing"
    try:
        raw_bytes = path.read_bytes()
    except OSError:
        return {}, "missing"
    digest = hashlib.sha256(raw_bytes).hexdigest()[:12]
    try:
        parsed = yaml.safe_load(raw_bytes.decode("utf-8")) or {}
    except (UnicodeDecodeError, yaml.YAMLError):
        return {}, digest
    if not isinstance(parsed, dict):
        return {}, digest
    return parsed, digest


def _build_judge_prompt(
    *,
    rubric: dict[str, Any],
    candidate_text: str,
    context_metadata: dict[str, Any],
) -> str:
    """Assemble the deterministic judge prompt from the rubric."""
    dims = rubric.get("soft_dimensions", []) or []
    dim_lines: list[str] = []
    expected_keys: list[str] = []
    for dim in dims:
        dim_id = str(dim.get("dimension_id", "")).strip()
        if not dim_id:
            continue
        expected_keys.append(dim_id)
        prompt_body = str(dim.get("judge_prompt", "Score 0.0-1.0.")).strip()
        dim_lines.append(f"- {dim_id}: {prompt_body}")

    json_schema = (
        "{"
        + ", ".join(f'"{k}": <float 0-1>' for k in expected_keys)
        + "}"
    )

    ctx_lines = [f"- {k}: {v}" for k, v in (context_metadata or {}).items()]
    ctx_block = "\n".join(ctx_lines) if ctx_lines else "(none)"

    return (
        "You are a rubric judge. Return STRICT JSON only — no prose, no "
        "markdown fences. The JSON object MUST contain exactly these keys, "
        "each a float in [0.0, 1.0]:\n"
        f"  {json_schema}\n\n"
        "Scoring dimensions (one per key):\n"
        + "\n".join(dim_lines)
        + "\n\nContext:\n"
        + ctx_block
        + "\n\nCandidate:\n"
        + (candidate_text or "")
        + "\n\nReturn JSON now."
    )


def _parse_soft_scores(text: str) -> dict[str, float]:
    """Parse the judge JSON response. Empty dict on any parse failure.

    Accepts either a bare JSON object or a JSON object inside a markdown
    fence. Keys must map to floats or ints; any other type skips the
    entry.
    """
    candidate = text.strip()
    if candidate.startswith("```"):
        # Strip markdown fence if the model emitted one despite the
        # instruction. Take the first fenced block.
        lines = candidate.splitlines()
        inner: list[str] = []
        in_fence = False
        for ln in lines:
            if ln.startswith("```"):
                if in_fence:
                    break
                in_fence = True
                continue
            if in_fence:
                inner.append(ln)
        candidate = "\n".join(inner).strip()

    try:
        parsed = json.loads(candidate)
    except (json.JSONDecodeError, ValueError):
        return {}
    if not isinstance(parsed, dict):
        return {}
    scores: dict[str, float] = {}
    for key, value in parsed.items():
        if not isinstance(key, str):
            continue
        if isinstance(value, bool):
            # bool is a subclass of int in Python; reject explicitly.
            continue
        if isinstance(value, (int, float)):
            scores[key] = max(0.0, min(1.0, float(value)))
    return scores


def _compose(
    soft_scores: dict[str, float],
    rubric: dict[str, Any],
) -> tuple[float, str | None]:
    """Compute weighted composite; return ``(composite, first_veto_dim_id)``.

    A dimension below its ``min_score`` collapses the composite to 0.0
    and is reported as a veto. When no dimensions are declared (or
    weights sum to zero), the composite is 0.0 with no veto.
    """
    dims = rubric.get("soft_dimensions", []) or []
    total_weight = 0.0
    running = 0.0
    for dim in dims:
        dim_id = str(dim.get("dimension_id", "")).strip()
        if not dim_id:
            continue
        weight = float(dim.get("weight", 0.0))
        min_score = float(dim.get("min_score", 0.0))
        score = float(soft_scores.get(dim_id, 0.0))
        if score < min_score:
            return 0.0, dim_id
        running += weight * score
        total_weight += weight
    if total_weight <= 0.0:
        return 0.0, None
    return min(1.0, running / total_weight), None


def _emit_judge_decision_marker(
    request: JudgeRequest,
    verdict: JudgeVerdict,
) -> None:
    """Best-effort ``JUDGE_DECISION`` marker emission. Never raises.

    Uses :mod:`tools.capture.append_marker` as a subprocess would, but
    calls the in-process helper directly to avoid the subprocess cost on
    every judge call. The helper validates the marker shape; any
    unexpected state logs a warning but does not interrupt the judge.
    """
    try:
        from tools.capture.append_marker import (  # noqa: PLC0415 — local import keeps cold module load cheap
            append_marker,
        )
    except ImportError:  # guardian: allow-return-none-swallow -- P1 ADG burndown
        return

    payload = (
        f"JUDGE_DECISION: type=judge_decision, "
        f"app_name={request.app_name}, "
        f"rubric_id={verdict.rubric_id}, "
        f"rubric_hash={verdict.rubric_hash}, "
        f"accepted={verdict.accepted}, "
        f"composite={verdict.composite:.4f}, "
        f"model_used={verdict.model_used}, "
        f"fallback_reason={verdict.fallback_reason or 'none'}, "
        f"first_failed_gate={verdict.first_failed_gate or 'none'}, "
        f"latency_ms={verdict.latency_ms:.1f}"
    )
    try:
        ok, msg = append_marker(payload, session_hint=request.app_name)
        if not ok:
            _LOGGER.info("judge_decision marker rejected: %s", msg)
    except (OSError, PermissionError) as exc:  # guardian: allow-log-and-swallow -- P1 ADG burndown
        _LOGGER.info("judge_decision marker emission failed: %s", exc)


__all__ = [
    "HardGateResult",
    "JudgeRequest",
    "JudgeVerdict",
    "QwenJudgeGateway",
]
