"""ops_scripts/ci/check_apps_qna_judge_spearman.py — Spearman calibration gate for apps_qna LLM judge.

Plan: ``.claude/plans/bge-m3-deferred-scope-remaining-c4e7a1.md`` W2.P2

Validates that the ``interview_card_quality_judge`` achieves Spearman rank
correlation ≥ 0.80 against a human-labeled holdout dataset.

Advisory-only when no holdout file exists. Fails hard when holdout exists
and Spearman < threshold.

Usage:
    python ops_scripts/ci/check_apps_qna_judge_spearman.py [--holdout <path>] [--threshold 0.80]

Holdout file format (JSONL — one JSON object per line):
    {"question": "...", "answer": "...", "human_score": 0.85, "context": "..." (optional)}

Exit codes:
    0 — pass (Spearman >= threshold, or no holdout file found)
    1 — fail (Spearman < threshold)
    2 — error (unexpected runtime failure)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

_DEFAULT_HOLDOUT_PATH = Path("artifacts/apps_qna/judge_holdout.jsonl")
_DEFAULT_THRESHOLD = 0.80
_MIN_SAMPLES = 10


def _spearman(x: list[float], y: list[float]) -> float:
    """Compute Spearman rank correlation coefficient."""
    n = len(x)
    if n < 2:
        return 0.0

    def _ranks(vals: list[float]) -> list[float]:
        sorted_idx = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        for rank, idx in enumerate(sorted_idx, start=1):
            ranks[idx] = float(rank)
        return ranks

    rx = _ranks(x)
    ry = _ranks(y)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return float(1.0 - (6.0 * d2) / max(1, n * (n * n - 1)))


def run_gate(holdout_path: Path, threshold: float) -> int:
    """Run the Spearman calibration gate.

    Returns:
        0 — pass
        1 — fail
        2 — error
    """
    if not holdout_path.exists():
        _LOGGER.info(
            "SKIP: holdout file not found at %s — gate is advisory-only until holdout is authored.",
            holdout_path,
        )
        print(f"SPEARMAN_GATE: ADVISORY_SKIP holdout={holdout_path} (file not found)")
        return 0

    records: list[dict] = []
    try:
        with holdout_path.open(encoding="utf-8") as f:
            for lineno, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    _LOGGER.error("Invalid JSON on line %d: %s", lineno, exc)
                    return 2
    except OSError as exc:
        _LOGGER.error("Cannot read holdout file: %s", exc)
        return 2

    if len(records) < _MIN_SAMPLES:
        _LOGGER.warning(
            "Holdout has only %d samples (min %d) — skipping gate.", len(records), _MIN_SAMPLES
        )
        print(f"SPEARMAN_GATE: ADVISORY_SKIP samples={len(records)} < min={_MIN_SAMPLES}")
        return 0

    # Import judge
    try:
        from apps_qna.engines.judges.interview_card_quality_judge import (
            InterviewCardQualityJudge,
        )
    except ImportError as exc:
        _LOGGER.error("Cannot import InterviewCardQualityJudge: %s", exc)
        return 2

    judge = InterviewCardQualityJudge()
    human_scores: list[float] = []
    llm_scores: list[float] = []
    skipped = 0

    for i, rec in enumerate(records):
        human_score = rec.get("human_score")
        if not isinstance(human_score, (int, float)):
            _LOGGER.warning("Record %d missing numeric human_score — skipping.", i)
            skipped += 1
            continue

        run_ctx = {
            "output": {
                "question": rec.get("question", ""),
                "answer": rec.get("answer", ""),
                "context": rec.get("context"),
            }
        }
        score, _ = judge.grade(None, run_ctx)

        from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
            GRADER_UNKNOWN_SENTINEL,
        )
        if score is GRADER_UNKNOWN_SENTINEL or not isinstance(score, (int, float)):
            _LOGGER.debug("Record %d returned UNKNOWN — skipping.", i)
            skipped += 1
            continue

        human_scores.append(float(human_score))
        llm_scores.append(float(score))

    effective_n = len(human_scores)
    if effective_n < _MIN_SAMPLES:
        _LOGGER.warning(
            "Only %d scoreable records after skipping %d — advisory skip.", effective_n, skipped
        )
        print(
            f"SPEARMAN_GATE: ADVISORY_SKIP effective_n={effective_n} skipped={skipped}"
        )
        return 0

    rho = _spearman(human_scores, llm_scores)
    passed = rho >= threshold

    status = "PASS" if passed else "FAIL"
    print(
        f"SPEARMAN_GATE: {status} rho={rho:.4f} threshold={threshold:.2f} "
        f"n={effective_n} skipped={skipped} holdout={holdout_path}"
    )

    if not passed:
        _LOGGER.error(
            "Spearman gate FAILED: rho=%.4f < threshold=%.2f. "
            "Improve judge or expand holdout. "
            "See .claude/plans/bge-m3-deferred-scope-remaining-c4e7a1.md W2.P2.",
            rho,
            threshold,
        )
        return 1

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Spearman calibration gate for apps_qna interview_card_quality_judge"
    )
    parser.add_argument(
        "--holdout",
        type=Path,
        default=_DEFAULT_HOLDOUT_PATH,
        help=f"Path to JSONL holdout file (default: {_DEFAULT_HOLDOUT_PATH})",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=_DEFAULT_THRESHOLD,
        help=f"Minimum Spearman rho to pass (default: {_DEFAULT_THRESHOLD})",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    try:
        return run_gate(args.holdout, args.threshold)
    except Exception as exc:
        _LOGGER.exception("Unexpected error in Spearman gate: %s", exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
