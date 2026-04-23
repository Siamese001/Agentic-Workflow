"""CI gate: LLM-judge calibration (LJH4.3).

Blocks merge when judge-vs-human Cohen's κ falls below the configured
threshold (default 0.6) on any rubric in ``data/eval/golden/``.

Exit codes:
- 0  κ >= threshold on every rubric (or skipped — see below)
- 1  κ below threshold on at least one rubric
- 2  Gate was skipped (golden set empty AND ``--allow-empty`` set);
     not a failure but distinguishable in CI logs.

Skipping rules:
- If ``data/eval/golden/<rubric>/`` has < ``--min-items`` items (default 10),
  the rubric is reported but does not fail the gate — the gate only
  enforces κ once the gold set is large enough to produce a stable κ.
- If judge outputs are missing (``--judge-outputs`` not found), the gate
  fails UNLESS ``--allow-missing-judge-outputs`` is set (used during
  bootstrapping).

Reads:
- Golden items: ``data/eval/golden/<rubric>/*.json``
- Judge outputs: ``<--judge-outputs>`` — JSONL of
  ``{"item_id": str, "dimension": str, "score": int|"Unknown"}``

Writes:
- Report: ``artifacts/eval/judge_calibration_report.json``
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.evaluation.judges.calibration import cohens_kappa  # noqa: E402

DEFAULT_THRESHOLD = 0.6
DEFAULT_MIN_ITEMS = 10


def _load_gold_items(gold_dir: Path) -> dict[str, dict]:
    items: dict[str, dict] = {}
    if not gold_dir.exists():
        return items
    for path in sorted(gold_dir.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[WARN] skipping malformed gold item {path}: {exc}", file=sys.stderr)
            continue
        item_id = data.get("item_id")
        if not item_id:
            continue
        items[item_id] = data
    return items


def _load_judge_outputs(path: Path) -> list[dict]:
    if not path.exists():
        return []
    outputs: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                outputs.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return outputs


def _normalize(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, str) and value.strip().lower() == "unknown":
        return None
    try:
        iv = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return iv if 1 <= iv <= 5 else None


def calibrate_rubric(
    rubric: str,
    gold_dir: Path,
    judge_outputs: list[dict],
) -> dict:
    gold_items = _load_gold_items(gold_dir)
    pairs: list[tuple[int, int]] = []
    for out in judge_outputs:
        if out.get("dimension") and out["dimension"] != rubric:
            continue
        item_id = out.get("item_id")
        if item_id not in gold_items:
            continue
        gold = _normalize(gold_items[item_id].get("gold_score"))
        judge = _normalize(out.get("score"))
        if gold is None or judge is None:
            continue
        pairs.append((gold, judge))
    if not pairs:
        kappa = float("nan")
    else:
        gold_labels = [p[0] for p in pairs]
        judge_labels = [p[1] for p in pairs]
        kappa = cohens_kappa(gold_labels, judge_labels)
    return {
        "rubric": rubric,
        "pair_count": len(pairs),
        "gold_item_count": len(gold_items),
        "cohens_kappa": kappa,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold-root", type=Path, default=REPO_ROOT / "data" / "eval" / "golden")
    parser.add_argument("--judge-outputs", type=Path, required=False)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--min-items", type=int, default=DEFAULT_MIN_ITEMS)
    parser.add_argument("--allow-empty", action="store_true")
    parser.add_argument("--allow-missing-judge-outputs", action="store_true")
    parser.add_argument(
        "--report-out",
        type=Path,
        default=REPO_ROOT / "artifacts" / "eval" / "judge_calibration_report.json",
    )
    args = parser.parse_args(argv)

    if not args.gold_root.exists():
        print(f"[INFO] no golden set at {args.gold_root}")
        if args.allow_empty:
            return 2
        return 1

    # Find leaf rubric dirs — any dir containing at least one *.json gold item
    rubric_dirs: list[Path] = []
    for p in sorted(args.gold_root.rglob("*")):
        if p.is_dir() and any(p.glob("*.json")):
            rubric_dirs.append(p)

    if not rubric_dirs:
        print(f"[INFO] no rubric dirs under {args.gold_root}")
        if args.allow_empty:
            return 2
        return 1

    judge_outputs: list[dict] = []
    if args.judge_outputs:
        judge_outputs = _load_judge_outputs(args.judge_outputs)
        if not judge_outputs and not args.allow_missing_judge_outputs:
            print(f"[ERROR] judge outputs empty/missing: {args.judge_outputs}")
            return 1

    reports: list[dict] = []
    gate_failed = False
    gate_status_lines: list[str] = []
    for rubric_dir in rubric_dirs:
        rubric = rubric_dir.name
        report = calibrate_rubric(rubric, rubric_dir, judge_outputs)
        reports.append(report)
        gold_n = report["gold_item_count"]
        pairs = report["pair_count"]
        kappa = report["cohens_kappa"]
        if gold_n < args.min_items:
            gate_status_lines.append(
                f"  [SKIP] {rubric:30s} gold={gold_n:3d} (< min {args.min_items})",
            )
            continue
        if pairs == 0:
            gate_status_lines.append(
                f"  [SKIP] {rubric:30s} gold={gold_n:3d} no judge outputs matched",
            )
            continue
        if kappa != kappa:  # NaN
            gate_status_lines.append(f"  [SKIP] {rubric:30s} kappa=NaN")
            continue
        if kappa < args.threshold:
            gate_failed = True
            gate_status_lines.append(
                f"  [FAIL] {rubric:30s} kappa={kappa:.3f} < {args.threshold}",
            )
        else:
            gate_status_lines.append(
                f"  [PASS] {rubric:30s} kappa={kappa:.3f} >= {args.threshold}",
            )

    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        json.dumps(
            {
                "threshold": args.threshold,
                "min_items": args.min_items,
                "reports": reports,
                "gate_failed": gate_failed,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("LJH4.3 judge-calibration gate")
    print(f"  threshold={args.threshold}  min_items={args.min_items}")
    for line in gate_status_lines:
        print(line)
    print(f"  report: {args.report_out}")
    return 1 if gate_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
