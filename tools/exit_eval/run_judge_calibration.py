"""Judge calibration harness — run a ``JudgeProtocol`` over the gold set.

Usage:

    python -m tools.exit_eval.run_judge_calibration \\
        --judge anthropic|openai|http|fake \\
        --gold data/judge_calibration/gold_set.jsonl \\
        --outputs data/judge_calibration/judge_runs/<id>-<ts>.jsonl \\
        --report data/judge_calibration/reports/<YYYY-MM-DD>.json

Steps:

1. Load every item from the gold jsonl.
2. Build a :class:`~agentic_core.L3_orchestration.exit_eval.graders.llm_judge.JudgeProtocol`
   instance per the ``--judge`` flag.
3. For each of the four pointwise dimensions declared in
   ``config/judges/rubrics.yaml`` (defaults to faithfulness /
   answer_relevancy / context_precision / groundedness), synthesise a
   :class:`Dimension`, build a ``context`` from the gold row (query,
   context, answer), call ``judge.judge(...)``, write an aligned row.
4. Pass both files to
   :func:`agentic_core.evaluation.judges.calibration.summarize_judge_vs_human`
   and write the report json.

Design choices:

- The harness itself is I/O only; all scoring / IAA math lives in
  ``agentic_core/evaluation/judges/calibration.py``.
- The ``fake`` judge is deterministic and always returns the human score
  ± a caller-controlled noise — makes the harness runnable in CI with
  no network dependency and gives us ground-truth round-trip tests.
- Real judges (anthropic/openai/http) are constructed via the same
  adapters shipped in Wave A; the harness knows nothing about their
  internals.

Exit codes:

    0 — harness completed, report written.
    1 — input validation error (bad args / missing gold file).
    2 — judge construction or I/O error.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from agentic_core.evaluation.judges.calibration import (
    JudgeCalibrationReport,
    summarize_judge_vs_human,
)
from agentic_core.L3_orchestration.exit_eval.dimension import (
    Dimension,
    GraderClass,
)
from agentic_core.L3_orchestration.exit_eval.graders.llm_judge import (
    JudgeProtocol,
    JudgeResponse,
)

DEFAULT_DIMENSIONS: tuple[str, ...] = (
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "groundedness",
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GOLD_PATH = REPO_ROOT / "data" / "judge_calibration" / "gold_set.jsonl"


# --------------------------------------------------------------------- #
# Deterministic fake judge — lets the harness run without network access
# and lets tests validate the end-to-end wiring.
# --------------------------------------------------------------------- #


@dataclass
class _FakeCalibrationJudge:
    """Returns human score ± fixed bias per dimension.

    ``noise_by_dim`` is additive: fake_score = clamp(human + noise, 1, 5).
    Missing ("Unknown") human labels are mirrored as ``abstain=True``
    iff ``abstain_on_unknown=True``.
    """

    gold_by_id: Mapping[str, Mapping[str, Any]]
    noise_by_dim: Mapping[str, int] = None  # type: ignore[assignment]
    abstain_on_unknown: bool = True

    def __post_init__(self) -> None:
        if self.noise_by_dim is None:
            self.noise_by_dim = {}

    def judge(
        self,
        dimension: Dimension,
        context: Mapping[str, Any],
    ) -> JudgeResponse:
        item_id = str(context.get("item_id", ""))
        row = self.gold_by_id.get(item_id, {})
        human = row.get(dimension.name)
        if _is_unknown(human):
            return JudgeResponse(
                score=0.0,
                abstain=bool(self.abstain_on_unknown),
                reasoning="fake-judge: mirrored Unknown",
            )
        try:
            base = int(human)
        except (TypeError, ValueError):
            return JudgeResponse(score=0.0, abstain=True, reasoning="fake-judge: non-numeric")
        noisy = base + int(self.noise_by_dim.get(dimension.name, 0))
        clamped = max(1, min(5, noisy))
        return JudgeResponse(
            score=float(clamped),
            abstain=False,
            reasoning=f"fake-judge: human={base} noise={self.noise_by_dim.get(dimension.name, 0)}",
        )


def _is_unknown(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip().lower() in {"unknown", ""}:
        return True
    return False


# --------------------------------------------------------------------- #
# Real-judge construction helpers. Import lazily so that running the
# fake-judge smoke path does not require the adapter SDKs to be present.
# --------------------------------------------------------------------- #


def _build_real_judge(kind: str) -> JudgeProtocol:
    kind = kind.lower()
    if kind == "anthropic":
        from agentic_core.L3_orchestration.exit_eval.judges.anthropic_judge import (
            AnthropicJudge,
        )

        return AnthropicJudge(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    if kind == "openai":
        from agentic_core.L3_orchestration.exit_eval.judges.openai_judge import (
            OpenAIJudge,
        )

        return OpenAIJudge(api_key=os.environ.get("OPENAI_API_KEY"))
    if kind == "http":
        from agentic_core.L3_orchestration.exit_eval.judges.http_judge import (
            HttpJudge,
        )

        endpoint = os.environ.get("JUDGE_ENDPOINT_URL")
        model = os.environ.get("JUDGE_MODEL", "unspecified")
        if not endpoint:
            raise ValueError(
                "HTTP judge requires JUDGE_ENDPOINT_URL env var"
            )
        return HttpJudge(endpoint=endpoint, model=model)
    raise ValueError(f"unknown --judge kind: {kind!r}")


# --------------------------------------------------------------------- #
# Core harness
# --------------------------------------------------------------------- #


def _load_gold(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"gold set not found: {path}")
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if "item_id" not in row:
                raise ValueError(f"{path}:{line_no}: missing item_id")
            rows.append(row)
    return rows


def _dimension_for(name: str) -> Dimension:
    """Construct a synthetic :class:`Dimension` for harness use.

    The harness never runs the composition logic — only calls
    ``judge.judge(dimension, ctx)`` — so threshold / weight are inert
    placeholders here. Dimension validates threshold ∈ [0, 1].
    """
    return Dimension(
        name=name,
        grader_class=GraderClass.MODEL_BASED,
        threshold=0.6,
        weight=1.0,
        abstain_allowed=True,
        is_hard_gate=False,
    )


@dataclass
class RunSummary:
    n_items: int
    n_abstained: int
    judge_path: Path
    report_path: Path
    report: JudgeCalibrationReport


def run_calibration(
    *,
    judge: JudgeProtocol,
    judge_id: str,
    gold_path: Path = DEFAULT_GOLD_PATH,
    outputs_path: Path | None = None,
    report_path: Path | None = None,
    dimensions: Iterable[str] = DEFAULT_DIMENSIONS,
    progress: Callable[[int, int], None] | None = None,
) -> RunSummary:
    """Run ``judge`` over ``gold_path``, persist outputs and report.

    Parameters
    ----------
    judge:
        Any object implementing :class:`JudgeProtocol`.
    judge_id:
        Short stable identifier written into filenames and appended to
        judge rows (e.g. "anthropic-claude-3-5-sonnet").
    gold_path:
        Path to gold jsonl. Defaults to repo-standard location.
    outputs_path:
        Where to write the judge's jsonl. Default:
        ``data/judge_calibration/judge_runs/<judge_id>-<ISO-ts>.jsonl``.
    report_path:
        Where to write the calibration report JSON. Default:
        ``data/judge_calibration/reports/<ISO-date>-<judge_id>.json``.
    dimensions:
        Which dimensions to score. Default: all four pointwise dims.
    progress:
        Optional callback ``(done, total)`` for UI wiring.
    """
    gold_rows = _load_gold(gold_path)
    total = len(gold_rows)
    if total == 0:
        raise ValueError(f"gold set is empty: {gold_path}")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    if outputs_path is None:
        outputs_path = (
            gold_path.parent / "judge_runs" / f"{judge_id}-{ts}.jsonl"
        )
    if report_path is None:
        report_path = (
            gold_path.parent
            / "reports"
            / f"{ts.split('T')[0]}-{judge_id}.json"
        )
    outputs_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    dims = tuple(dimensions)
    n_abstained = 0
    with outputs_path.open("w", encoding="utf-8") as fh:
        for idx, gold_row in enumerate(gold_rows, 1):
            out_row: dict[str, Any] = {
                "item_id": gold_row["item_id"],
                "judge_id": judge_id,
                "judged_at": datetime.now(timezone.utc).isoformat(),
            }
            ctx = {
                "item_id": gold_row["item_id"],
                "query": gold_row.get("query", ""),
                "context": gold_row.get("context", ""),
                "answer": gold_row.get("answer", ""),
            }
            for dim_name in dims:
                dim = _dimension_for(dim_name)
                try:
                    response = judge.judge(dim, ctx)
                except Exception as exc:  # guardian: allow-broad -- harness records judge failures as Unknown rather than aborting the entire run; downstream IAA handles Unknown correctly
                    out_row[dim_name] = "Unknown"
                    out_row[f"{dim_name}_error"] = f"{type(exc).__name__}: {exc}"
                    n_abstained += 1
                    continue
                if response.abstain:
                    out_row[dim_name] = "Unknown"
                    out_row[f"{dim_name}_reasoning"] = response.reasoning
                    n_abstained += 1
                else:
                    # Round to int so the IAA machinery sees an ordinal score
                    out_row[dim_name] = int(round(response.score))
                    out_row[f"{dim_name}_reasoning"] = response.reasoning
            fh.write(json.dumps(out_row, separators=(",", ":")) + "\n")
            if progress is not None:
                progress(idx, total)

    report = summarize_judge_vs_human(
        gold_path=gold_path,
        judge_path=outputs_path,
        dimensions=dims,
    )
    report_path.write_text(
        json.dumps(report.to_dict(), indent=2), encoding="utf-8"
    )
    return RunSummary(
        n_items=total,
        n_abstained=n_abstained,
        judge_path=outputs_path,
        report_path=report_path,
        report=report,
    )


# --------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------- #


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--judge",
        required=True,
        choices=["anthropic", "openai", "http", "fake"],
        help="Which JudgeProtocol adapter to run.",
    )
    parser.add_argument(
        "--judge-id",
        default=None,
        help="Stable judge id stamped into output filenames (default: --judge value plus timestamp).",
    )
    parser.add_argument(
        "--gold",
        type=Path,
        default=DEFAULT_GOLD_PATH,
    )
    parser.add_argument(
        "--outputs",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--dim",
        action="append",
        help="Restrict to a dimension (may be passed multiple times).",
    )
    parser.add_argument(
        "--fake-noise",
        type=int,
        default=0,
        help="For --judge fake: integer bias added to every score (default 0 = perfect agreement).",
    )
    parser.add_argument(
        "--min-kappa",
        type=float,
        default=0.0,
        help="If set, exit 3 when any dimension κ < this threshold.",
    )
    args = parser.parse_args(argv)

    judge_id = args.judge_id or args.judge

    try:
        if args.judge == "fake":
            gold_rows = _load_gold(args.gold)
            gold_by_id = {str(r["item_id"]): r for r in gold_rows}
            judge: JudgeProtocol = _FakeCalibrationJudge(
                gold_by_id=gold_by_id,
                noise_by_dim={
                    d: args.fake_noise for d in (args.dim or DEFAULT_DIMENSIONS)
                },
            )
        else:
            judge = _build_real_judge(args.judge)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except ImportError as exc:
        print(f"ERROR: adapter import failed: {exc}", file=sys.stderr)
        return 2

    summary = run_calibration(
        judge=judge,
        judge_id=judge_id,
        gold_path=args.gold,
        outputs_path=args.outputs,
        report_path=args.report,
        dimensions=args.dim or DEFAULT_DIMENSIONS,
    )
    print(
        f"Judge calibration complete: n={summary.n_items} "
        f"abstained={summary.n_abstained}"
    )
    print(f"  judge outputs: {summary.judge_path}")
    print(f"  report:        {summary.report_path}")
    for dim, kappa in summary.report.dimension_kappa.items():
        alpha = summary.report.dimension_alpha.get(dim, float("nan"))
        print(f"  [{dim:22s}] kappa={kappa:.3f} alpha={alpha:.3f}")
    if args.min_kappa > 0:
        failing = [
            d for d, k in summary.report.dimension_kappa.items() if k < args.min_kappa
        ]
        if failing:
            print(
                f"\nFAIL: dimensions below κ={args.min_kappa}: {failing}",
                file=sys.stderr,
            )
            return 3
    return 0


if __name__ == "__main__":
    sys.exit(_main())
