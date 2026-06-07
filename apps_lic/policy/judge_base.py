"""JudgeBase — generic LLM-as-Judge primitive for LIC HOPs.

Implements the constitutionally-shaped Judge pattern from
`docs/reference/_notes/LLM as a Judge vs. Ensemble vs. Hybrid.md`. One
primitive consumed by four LIC HOP Judges (HOP1 LLM-fallback, HOP2
strategic_brief faithfulness, HOP6 strategic alignment, HOP8 narrative
executive_summary).

The class is intentionally tiny: load a rubric YAML, accept a pluggable
``evaluate`` callable, emit a `JudgeScorecard` shape that matches the
reference doc's OUTPUT ARTIFACT spec verbatim, dispatch the
score+rule_id through `judge_disposition_policy.yaml` to map onto the
X3 disposition vocabulary (ALLOW/REVISE/DENY/HITL/ABSTAIN). Reuses the
`DecisionRouter` primitive shipped in plan b3a4d2 — no new dispatch
engine.

The deterministic-backend mode (default) ships today. The LLM-backend
mode is a leaf swap-in: replace `evaluate` with a callable that wraps
an LLM call. The integration surface inside each HOP does not change.

See `docs/archive/windsurf/legacy-tree/plans/judge-base-and-four-judges-c5e1f3.md` for the
seven architectural decisions that shape this module (D1-D7).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml

from apps_lic.policy.decision_router import DecisionRouter

LOG = logging.getLogger(__name__)


class RubricLoadError(ValueError):
    """Raised when a rubric YAML fails schema validation at load time."""


# ---------------------------------------------------------------------- #
# Constitutional scorecard shape (D5)
# ---------------------------------------------------------------------- #


@dataclass(frozen=True)
class JudgeScorecard:
    """The OUTPUT ARTIFACT shape every Judge emits.

    Mirrors the reference doc's spec verbatim: judge_scorecard,
    gate_verdict, reason_codes[], evidence_refs[], confidence,
    abstain_flag, remediation_hint, X3 disposition. The ``score``
    field is added because the deterministic backends produce numeric
    scores naturally; LLM backends can populate it from a rubric-
    declared scoring schema.
    """

    judge_name: str
    rubric_version: str
    score: float  # in [0.0, 1.0]
    verdict: str  # PASS / FAIL / UNKNOWN — pre-disposition raw verdict
    x3_disposition: str  # ALLOW / REVISE / DENY / HITL / ABSTAIN
    reason_codes: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    confidence: float = 1.0  # in [0.0, 1.0]
    abstain_flag: bool = False
    remediation_hint: str = ""
    backend: str = "deterministic"  # "deterministic" | "llm"

    def to_dict(self) -> dict[str, Any]:
        """Plain-dict view suitable for buffer write or JSON serialization."""
        return {
            "judge_name": self.judge_name,
            "rubric_version": self.rubric_version,
            "score": self.score,
            "verdict": self.verdict,
            "x3_disposition": self.x3_disposition,
            "reason_codes": list(self.reason_codes),
            "evidence_refs": list(self.evidence_refs),
            "confidence": self.confidence,
            "abstain_flag": self.abstain_flag,
            "remediation_hint": self.remediation_hint,
            "backend": self.backend,
        }


# ---------------------------------------------------------------------- #
# Rubric loader
# ---------------------------------------------------------------------- #


_REQUIRED_RUBRIC_KEYS = {"rubric_id", "rubric_version", "judge_name", "score_bands"}


@dataclass(frozen=True)
class Rubric:
    """A loaded, validated rubric definition.

    The rubric drives Judge configuration: identity, scoring schema,
    score→band mapping, deterministic-backend parameters. The
    ``params`` block is consumed by the per-Judge deterministic
    `evaluate` implementations and is rubric-specific.
    """

    rubric_id: str
    rubric_version: str
    judge_name: str
    description: str
    score_bands: tuple[tuple[float, str], ...]  # ((threshold, band_label), ...) sorted ascending
    params: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path) -> Rubric:
        p = Path(path)
        if not p.is_file():
            raise RubricLoadError(f"Rubric file not found: {path}")
        try:
            with open(p, encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
        except yaml.YAMLError as exc:
            raise RubricLoadError(f"Invalid YAML at {path}: {exc}") from exc
        missing = _REQUIRED_RUBRIC_KEYS - set(raw.keys())
        if missing:
            raise RubricLoadError(
                f"Rubric {path} missing required top-level keys: {sorted(missing)}"
            )
        bands_raw = raw.get("score_bands")
        if not isinstance(bands_raw, list) or not bands_raw:
            raise RubricLoadError(
                f"Rubric {path} 'score_bands' must be a non-empty list"
            )
        bands: list[tuple[float, str]] = []
        for entry in bands_raw:
            if not isinstance(entry, dict):
                raise RubricLoadError(f"Rubric {path} score_bands entry not a mapping: {entry}")
            if "min_score" not in entry or "band" not in entry:
                raise RubricLoadError(
                    f"Rubric {path} score_bands entry missing 'min_score' or 'band': {entry}"
                )
            bands.append((float(entry["min_score"]), str(entry["band"])))
        bands.sort(key=lambda x: x[0])
        return cls(
            rubric_id=str(raw["rubric_id"]),
            rubric_version=str(raw["rubric_version"]),
            judge_name=str(raw["judge_name"]),
            description=str(raw.get("description", "")),
            score_bands=tuple(bands),
            params=dict(raw.get("params") or {}),
            raw=dict(raw),
        )

    def band_for_score(self, score: float) -> str:
        """Return the highest band label whose ``min_score`` <= score."""
        chosen = self.score_bands[0][1]
        for threshold, label in self.score_bands:
            if score >= threshold:
                chosen = label
        return chosen


# ---------------------------------------------------------------------- #
# JudgeBase primitive
# ---------------------------------------------------------------------- #


# Type alias for the pluggable evaluate callable.
# Returns: (score in [0,1], reason_codes, evidence_refs, remediation_hint)
EvaluateFn = Callable[
    [dict[str, Any], Rubric],
    tuple[float, list[str], list[str], str],
]


class JudgeBase:
    """LLM-as-Judge primitive (D1).

    Construct once per (rubric, evaluate-fn) pair. Call ``judge(state)``
    per evaluation. The class enforces:

      - constitutional `JudgeScorecard` shape (D5)
      - X3 disposition mapping via `judge_disposition_policy.yaml` (D3)
      - ABSTAIN-on-failure semantics (D6)
      - ROUTER_DECISION marker emission per constitutional §29

    Args:
        rubric_path: path to a rubric YAML (Rubric.load contract).
        evaluate_fn: pluggable scoring function. Receives ``(state,
            rubric)``, returns ``(score, reason_codes,
            evidence_refs, remediation_hint)``. May raise — the Judge
            converts any raise into an ABSTAIN scorecard with
            ``abstain_flag=True``.
        disposition_policy_path: path to the X3-mapping policy YAML.
            Defaults to the bundled ``judge_disposition_policy.yaml``.
        backend: arbitrary string label, surfaced in scorecard.backend.
            Defaults to ``"deterministic"``.
    """

    def __init__(
        self,
        rubric_path: str | Path,
        evaluate_fn: EvaluateFn,
        *,
        disposition_policy_path: str | Path | None = None,
        backend: str = "deterministic",
    ) -> None:
        self.rubric = Rubric.load(rubric_path)
        self.evaluate_fn = evaluate_fn
        self.backend = backend
        if disposition_policy_path is None:
            disposition_policy_path = (
                Path(__file__).resolve().parent / "judge_disposition_policy.yaml"
            )
        self._dispatcher = DecisionRouter(disposition_policy_path)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def judge(
        self,
        state: dict[str, Any],
        *,
        rule_id: str | None = None,
        emit_marker: bool | None = None,
    ) -> JudgeScorecard:
        """Run the rubric against ``state`` and emit a `JudgeScorecard`.

        On any exception from ``evaluate_fn``, returns an ABSTAIN
        scorecard (D6) — the Judge never raises into its caller.
        ``rule_id`` defaults to the rubric_id when not provided; the
        disposition policy can match on either ``rule_id`` or the
        derived ``score_band``.
        """
        if not isinstance(state, dict):
            raise TypeError(f"state must be dict, got {type(state).__name__}")

        effective_rule_id = rule_id or self.rubric.rubric_id

        try:
            score, reason_codes, evidence_refs, remediation = self.evaluate_fn(
                state, self.rubric
            )
        except Exception as exc:  # guardian: allow-broad-catch -- D6 ABSTAIN-on-failure
            LOG.warning(
                "Judge %s evaluate_fn raised; returning ABSTAIN: %s",
                self.rubric.judge_name,
                exc,
            )
            return self._abstain_scorecard(
                effective_rule_id,
                reason="evaluate_fn_raised",
                detail=str(exc),
            )

        # Clamp score into [0, 1] to keep the rubric contract honest.
        score = max(0.0, min(1.0, float(score)))
        band = self.rubric.band_for_score(score)
        verdict = _verdict_from_band(band)

        # Resolve X3 disposition via the disposition policy (D3).
        dispatch_state = {
            "rule_id": effective_rule_id,
            "score_band": band,
            "verdict": verdict,
        }
        match = self._dispatcher.resolve(
            dispatch_state, emit_marker=emit_marker
        )
        x3 = str(match.verdict.get("x3_disposition", "HITL"))
        confidence = float(match.verdict.get("confidence", 1.0))

        return JudgeScorecard(
            judge_name=self.rubric.judge_name,
            rubric_version=self.rubric.rubric_version,
            score=score,
            verdict=verdict,
            x3_disposition=x3,
            reason_codes=tuple(reason_codes or ()),
            evidence_refs=tuple(evidence_refs or ()),
            confidence=confidence,
            abstain_flag=(x3 == "ABSTAIN"),
            remediation_hint=str(remediation or ""),
            backend=self.backend,
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _abstain_scorecard(
        self,
        rule_id: str,
        *,
        reason: str,
        detail: str = "",
    ) -> JudgeScorecard:
        """Construct an ABSTAIN scorecard for the failure path (D6)."""
        return JudgeScorecard(
            judge_name=self.rubric.judge_name,
            rubric_version=self.rubric.rubric_version,
            score=0.0,
            verdict="UNKNOWN",
            x3_disposition="ABSTAIN",
            reason_codes=(reason,),
            evidence_refs=(),
            confidence=0.0,
            abstain_flag=True,
            remediation_hint=detail,
            backend=self.backend,
        )


# ---------------------------------------------------------------------- #
# Module-level helpers
# ---------------------------------------------------------------------- #


def _verdict_from_band(band: str) -> str:
    """Map a score-band label to the raw PASS/FAIL/UNKNOWN verdict.

    The X3 disposition is computed separately by the disposition
    policy YAML, which can be tuned without code edits. This local
    mapping is intentionally permissive about non-WEAK bands: any
    band that scored numerically is PASS (the rubric was applicable);
    the score_band field carries the granularity for downstream
    disposition. UNKNOWN is reserved for bands that ALSO indicate
    no scorable signal (e.g. an explicit "UNKNOWN" / "ABSTAIN" band).
    """
    band_upper = band.upper()
    if band_upper in {"WEAK", "FAIL", "RED"}:
        return "FAIL"
    if band_upper in {"UNKNOWN", "ABSTAIN", "INDETERMINATE"}:
        return "UNKNOWN"
    # STRONG, MODERATE, PASS, GREEN, and any rubric-specific band:
    # the evaluator returned a numeric score, so the verdict is PASS.
    return "PASS"
