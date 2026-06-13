"""Judge Spearman calibration — scaffold + SYNTHETIC smoke run.

Plan: `docs/archive/windsurf/legacy-tree/plans/judge-spearman-calibration-a7e4c9.md`.

Status
------
SCAFFOLD ONLY. Against real human-labeled holdout, this module computes
Spearman rank correlation between v2 deterministic judge scores and
human scores, reports ρ per judge, and emits a calibration-evidence
JSON artifact. Against synthetic fixtures (current state), the ρ number
is MEANINGLESS by construction — running against synthetic labels
exists only to exercise the plumbing.

Activation
----------
Replace `apps_eval/fixtures/holdout/<app>.jsonl` rows' tags by removing
``SYNTHETIC_SEED_ONLY`` and adding ``RELEASE_GATE`` once human-labeled
corpus lands per plan `holdout-corpus-authoring-b5d2f6`. Then this
module produces real ρ.

Output shape
------------
``{
    "judge_id": "rg::executive_positioning_judge::v2",
    "n": 100,
    "spearman_rho": 0.84,
    "p_value": 1.2e-28,
    "is_synthetic_smoke": false,
    "meets_threshold": true,
    "threshold": 0.80,
}``
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional

# Ensure repo root is on sys.path when this script is run standalone.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

Logger = logging.getLogger(__name__)

SPEARMAN_THRESHOLD: float = 0.80

# (judge_id, dotted import path, dim_key in human labels, app_id for fixture).
JUDGE_CALIBRATION_TARGETS: tuple[tuple[str, str, str, str], ...] = (
    (
        "rg::executive_positioning_judge::v2",
        "apps_rg.engines.judges.executive_positioning_judge",
        "executive_positioning",
        "apps_rg",
    ),
    (
        "lic::response_likelihood_judge::v2",
        "apps_lic.engines.judges.response_likelihood_judge",
        "response_likelihood",
        "apps_lic",
    ),
    (
        "lic::brand_voice_judge::v2",
        "apps_lic.engines.judges.brand_voice_judge",
        "brand_voice",
        "apps_lic",
    ),
)


@dataclass(frozen=True)
class CalibrationResult:
    judge_id: str
    n: int
    spearman_rho: Optional[float]
    p_value: Optional[float]
    is_synthetic_smoke: bool
    meets_threshold: bool
    threshold: float
    error: str = ""


def _load_holdout_rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _is_synthetic(rows: Iterable[dict]) -> bool:
    for row in rows:
        tags = row.get("tags") or []
        if "SYNTHETIC_SEED_ONLY" in tags:
            return True
    return False


def _spearman(a: list[float], b: list[float]) -> tuple[Optional[float], Optional[float]]:
    try:
        from scipy.stats import spearmanr  # type: ignore
    except ImportError:
        return None, None
    if len(a) < 2 or len(b) < 2:
        return None, None
    try:
        result = spearmanr(a, b)
        return float(result.statistic), float(result.pvalue)
    except (ValueError, TypeError) as exc:
        Logger.warning("spearmanr failed: %s", exc)
        return None, None


def _extract_pair(row: dict, dim_key: str) -> Optional[tuple[float, str]]:
    """Return (human_score, output_text) if present."""
    human_scores = row.get("rubric_dim_human_scores") or {}
    if not isinstance(human_scores, dict):
        return None
    if dim_key not in human_scores:
        return None
    try:
        human = float(human_scores[dim_key])
    except (TypeError, ValueError):
        return None
    expected = row.get("expected") or row.get("output") or ""
    if not isinstance(expected, str):
        return None
    return human, expected


def calibrate_judge(
    judge_id: str,
    import_path: str,
    dim_key: str,
    app_id: str,
    fixtures_root: Path,
) -> CalibrationResult:
    import importlib

    try:
        module = importlib.import_module(import_path)
    except ImportError as exc:
        return CalibrationResult(
            judge_id=judge_id,
            n=0,
            spearman_rho=None,
            p_value=None,
            is_synthetic_smoke=False,
            meets_threshold=False,
            threshold=SPEARMAN_THRESHOLD,
            error=f"import_error: {exc}",
        )
    grade = getattr(module, "grade", None)
    if not callable(grade):
        return CalibrationResult(
            judge_id=judge_id,
            n=0,
            spearman_rho=None,
            p_value=None,
            is_synthetic_smoke=False,
            meets_threshold=False,
            threshold=SPEARMAN_THRESHOLD,
            error="module has no grade() callable",
        )

    holdout_path = fixtures_root / "holdout" / f"{app_id}.jsonl"
    rows = _load_holdout_rows(holdout_path)
    synthetic = _is_synthetic(rows)
    human_scores: list[float] = []
    judge_scores: list[float] = []
    for row in rows:
        pair = _extract_pair(row, dim_key)
        if pair is None:
            continue
        human, text = pair
        run_ctx = {
            "output": {"text": text},
            "rfp_context": {"win_themes": row.get("win_themes", ["scalability"])},
            "brand_voice_profile": row.get("brand_voice_profile", {}),
        }
        score, _refs = grade(None, run_ctx)
        if isinstance(score, (int, float)):
            human_scores.append(float(human))
            judge_scores.append(float(score))

    rho, pvalue = _spearman(human_scores, judge_scores)
    meets = (rho is not None) and (not synthetic) and (rho >= SPEARMAN_THRESHOLD)

    return CalibrationResult(
        judge_id=judge_id,
        n=len(human_scores),
        spearman_rho=rho,
        p_value=pvalue,
        is_synthetic_smoke=synthetic,
        meets_threshold=meets,
        threshold=SPEARMAN_THRESHOLD,
    )


def run_all(fixtures_root: Path) -> list[CalibrationResult]:
    return [
        calibrate_judge(judge_id, import_path, dim_key, app_id, fixtures_root)
        for judge_id, import_path, dim_key, app_id in JUDGE_CALIBRATION_TARGETS
    ]


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Judge Spearman calibration scaffold")
    p.add_argument(
        "--fixtures-root",
        type=Path,
        default=Path("apps_eval/fixtures"),
        help="Root of apps_eval/fixtures/ (holdout/ subdir is consumed)",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/calibration/judge_spearman.json"),
    )
    return p


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = _build_parser().parse_args(argv)
    results = run_all(args.fixtures_root)
    payload = {
        "generated_at": "2026-05-03",
        "threshold": SPEARMAN_THRESHOLD,
        "results": [asdict(r) for r in results],
        "any_synthetic_smoke": any(r.is_synthetic_smoke for r in results),
        "all_meet_threshold": all(r.meets_threshold for r in results),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["any_synthetic_smoke"]:
        Logger.warning(
            "SYNTHETIC smoke run — ρ values are MEANINGLESS. Real calibration requires "
            "human-labeled holdout per plan holdout-corpus-authoring-b5d2f6."
        )
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
