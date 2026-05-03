"""Rolling-window Wilson-CI agreement tracker for Qwen/frontier pairing (W3.2).

Records each (qwen_rationale, frontier_rationale) pair along with a
deterministic agreement flag (Jaccard-overlap heuristic on significant
tokens). Over a 4-week rolling window the tracker emits a watchdog
verdict via the existing Wilson-CI primitive in
``agentic_core.L6_observability.promotion_gates``:

  * ``INSUFFICIENT`` — fewer than ``min_n`` samples in-window
  * ``AGREE``        — Wilson lower-bound of p(agree) >= threshold
  * ``DISAGREE``     — Wilson lower-bound < threshold (alert)

Threshold = 0.85 (per plan ``apps-underwriting-ai-activation-e8a3c5``
compliance-posture section; matches predecessor W4 P4.4 pattern).
min_n = 30 (matches ``promotion_gates.promotion_decision`` default
``min_n_each_arm``).

Storage: durable JSONL at
``artifacts/apps_underwriting_ai/rationale_agreement.jsonl``. One line
per sample, append-only. The path is overridable for tests via the
``APPS_UW_AGREEMENT_LOG_PATH`` env var.

Callers from the assembler invoke :func:`record_pair` after the Qwen
path has accepted AND the frontier path has returned a non-``None``
rationale. :func:`watchdog_verdict` is called by calibration jobs /
RCA probes — NOT in the hot path.

Compliance-posture floor: this module is telemetry only. It never
mutates any ``DecisionPacket`` field. Every failure path is fail-soft.
"""
from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path

from agentic_core.L6_observability.promotion_gates import (
    WilsonInterval,
    wilson_interval,
)

_LOGGER = logging.getLogger(__name__)

AGREEMENT_THRESHOLD: float = 0.85
"""Wilson lower-bound gate below which the watchdog flags DISAGREE.

Inherited from plan compliance-posture section."""

MIN_SAMPLES: int = 30
"""Minimum samples in-window before a verdict is non-INSUFFICIENT."""

ROLLING_WINDOW_SECONDS: int = 4 * 7 * 24 * 60 * 60
"""4 weeks."""

JACCARD_AGREE_THRESHOLD: float = 0.30
"""Token-overlap threshold for deterministic agreement classification.

Rationales are short (2-4 sentences). A Jaccard index of 0.3 on
significant tokens (len>=5, lowercased, stopword-filtered) is a
conservative "they said similar things" signal. Below this threshold
the two rationales materially diverge.
"""

_STOPWORDS: frozenset[str] = frozenset(
    {
        "about",
        "above",
        "after",
        "again",
        "against",
        "because",
        "before",
        "being",
        "below",
        "between",
        "could",
        "doing",
        "during",
        "further",
        "having",
        "other",
        "should",
        "their",
        "there",
        "these",
        "those",
        "through",
        "under",
        "until",
        "where",
        "which",
        "while",
        "would",
    }
)

_TOKEN_RE = re.compile(r"[A-Za-z]+")


@dataclass(frozen=True)
class AgreementSample:
    """Single pairing sample written to the durable log."""

    ts_unix: float
    request_id: str
    verdict: str
    qwen_chars: int
    frontier_chars: int
    jaccard: float
    agreed: bool
    frontier_model: str

    def to_jsonl(self) -> str:
        return json.dumps(
            {
                "ts_unix": self.ts_unix,
                "request_id": self.request_id,
                "verdict": self.verdict,
                "qwen_chars": self.qwen_chars,
                "frontier_chars": self.frontier_chars,
                "jaccard": self.jaccard,
                "agreed": self.agreed,
                "frontier_model": self.frontier_model,
            },
            separators=(",", ":"),
            sort_keys=True,
        )


@dataclass(frozen=True)
class WatchdogVerdict:
    """Output of :func:`watchdog_verdict`."""

    state: str  # "INSUFFICIENT" | "AGREE" | "DISAGREE"
    interval: WilsonInterval
    threshold: float
    min_samples: int
    window_seconds: int


def _significant_tokens(text: str) -> set[str]:
    """Lowercased tokens of length >= 5, stopwords removed."""
    tokens = {t.lower() for t in _TOKEN_RE.findall(text) if len(t) >= 5}
    return tokens - _STOPWORDS


def jaccard_overlap(text_a: str, text_b: str) -> float:
    """Deterministic 0..1 overlap score on significant tokens.

    Two empty inputs return 0.0 (no overlap claim). Single-empty input
    returns 0.0.
    """
    a = _significant_tokens(text_a)
    b = _significant_tokens(text_b)
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _log_path() -> Path:
    override = os.environ.get("APPS_UW_AGREEMENT_LOG_PATH", "").strip()
    if override:
        return Path(override)
    return Path("artifacts") / "apps_underwriting_ai" / "rationale_agreement.jsonl"


def record_pair(
    *,
    request_id: str,
    verdict_value: str,
    qwen_rationale: str,
    frontier_rationale: str,
    frontier_model: str,
    now: float | None = None,
) -> AgreementSample:
    """Record one pairing sample to the durable JSONL log.

    Returns the sample for inspection. Never raises — on any filesystem
    failure the sample is returned but the log write is skipped
    (fail-soft, regulated-domain compliance floor).
    """
    ts = time.time() if now is None else now
    jaccard = jaccard_overlap(qwen_rationale, frontier_rationale)
    agreed = jaccard >= JACCARD_AGREE_THRESHOLD
    sample = AgreementSample(
        ts_unix=ts,
        request_id=request_id,
        verdict=verdict_value,
        qwen_chars=len(qwen_rationale),
        frontier_chars=len(frontier_rationale),
        jaccard=round(jaccard, 4),
        agreed=agreed,
        frontier_model=frontier_model,
    )
    try:
        path = _log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(sample.to_jsonl())
            fh.write("\n")
    except OSError as exc:
        _LOGGER.info(
            "[apps_underwriting_ai.agreement_tracker] log write skipped: %s", exc
        )
    return sample


def _iter_samples(path: Path) -> list[AgreementSample]:
    if not path.is_file():
        return []
    out: list[AgreementSample] = []
    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                try:
                    out.append(
                        AgreementSample(
                            ts_unix=float(row["ts_unix"]),
                            request_id=str(row.get("request_id", "")),
                            verdict=str(row.get("verdict", "")),
                            qwen_chars=int(row.get("qwen_chars", 0)),
                            frontier_chars=int(row.get("frontier_chars", 0)),
                            jaccard=float(row.get("jaccard", 0.0)),
                            agreed=bool(row.get("agreed", False)),
                            frontier_model=str(row.get("frontier_model", "")),
                        )
                    )
                except (KeyError, TypeError, ValueError):
                    continue
    except OSError as exc:
        _LOGGER.info(
            "[apps_underwriting_ai.agreement_tracker] log read skipped: %s", exc
        )
        return []
    return out


def watchdog_verdict(
    *,
    now: float | None = None,
    window_seconds: int = ROLLING_WINDOW_SECONDS,
    min_samples: int = MIN_SAMPLES,
    threshold: float = AGREEMENT_THRESHOLD,
) -> WatchdogVerdict:
    """Compute the rolling-window Wilson-CI watchdog state.

    Reads the JSONL log, filters to samples within ``window_seconds`` of
    ``now``, computes Wilson interval on ``sum(agreed) / n``, and
    returns a verdict. Fail-soft on any read failure (returns
    ``INSUFFICIENT`` with an empty interval).
    """
    current = time.time() if now is None else now
    cutoff = current - window_seconds
    samples = [s for s in _iter_samples(_log_path()) if s.ts_unix >= cutoff]
    n = len(samples)
    successes = sum(1 for s in samples if s.agreed)
    interval = wilson_interval(successes, n)

    if n < min_samples:
        state = "INSUFFICIENT"
    elif interval.lower >= threshold:
        state = "AGREE"
    else:
        state = "DISAGREE"
    return WatchdogVerdict(
        state=state,
        interval=interval,
        threshold=threshold,
        min_samples=min_samples,
        window_seconds=window_seconds,
    )


__all__ = [
    "AGREEMENT_THRESHOLD",
    "AgreementSample",
    "JACCARD_AGREE_THRESHOLD",
    "MIN_SAMPLES",
    "ROLLING_WINDOW_SECONDS",
    "WatchdogVerdict",
    "jaccard_overlap",
    "record_pair",
    "watchdog_verdict",
]
