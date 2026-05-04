"""tools.calibration.lic_judge_holdout_ingest — DS1-P1.

Plan: .windsurf/plans/apps-lic-calibration-holdout-e8f1c4.md W5 DS1-P1

Offline-only holdout corpus ingest pipeline.

Reads a human-labeled CSV of outreach drafts + per-judge scores and produces
a canonical JSONL judgment file for use by lic_judge_spearman_calibration.py.

Design constraints
------------------
- Offline-only: never called from the hot path.
- No provider API calls.  No durable state beyond the output JSONL.
- No subprocess calls.
- Input CSV must be validated before output rows are emitted.
- Decision-only: the ingestor never modifies any judge source file.

CSV schema (required columns)
------------------------------
draft_id         : unique identifier for the draft (str)
draft_text       : the outreach draft text (str)
grader_id        : one of the 5 canonical lic judge grader IDs (str)
human_score      : human annotator score in [0.0, 1.0] (float)
recipient_class  : e.g. EXECUTIVE, RECRUITER, HIRING_MANAGER (str)
outreach_mode    : cold | warm | referral | follow_up (str)

Optional columns (passed through to JSONL, not validated):
  annotator_id, annotation_date, confidence, notes

Output JSONL schema (one line per row)
---------------------------------------
{
  "draft_id":       str,
  "draft_text":     str,
  "grader_id":      str,
  "human_score":    float,
  "recipient_class": str,
  "outreach_mode":  str,
  "run_context":    {...}   # synthesised from row for judge.grade() calls
}

Usage
-----
  python tools/calibration/lic_judge_holdout_ingest.py \\
      --input  data/holdout/lic_holdout_labeled.csv \\
      --output artifacts/calibration/lic_holdout_corpus.jsonl

  python tools/calibration/lic_judge_holdout_ingest.py --help
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS: frozenset[str] = frozenset(
    {"draft_id", "draft_text", "grader_id", "human_score", "recipient_class", "outreach_mode"}
)

VALID_GRADER_IDS: frozenset[str] = frozenset({
    "lic::ask_friction_judge::v1",
    "lic::antipattern_clean_judge::v1",
    "lic::proof_appropriate_judge::v1",
    "lic::personalization_judge::v1",
    "lic::asymmetric_insight_judge::v1",
    "lic::response_likelihood_judge::v2",
    "lic::brand_voice_judge::v2",
})

VALID_OUTREACH_MODES: frozenset[str] = frozenset(
    {"cold", "warm", "referral", "follow_up"}
)

OPTIONAL_PASSTHROUGH: tuple[str, ...] = (
    "annotator_id",
    "annotation_date",
    "confidence",
    "notes",
)


# ---------------------------------------------------------------------------
# Row dataclass
# ---------------------------------------------------------------------------


@dataclass
class HoldoutRow:
    """One validated judgment row ready for JSONL output."""

    draft_id: str
    draft_text: str
    grader_id: str
    human_score: float
    recipient_class: str
    outreach_mode: str
    run_context: dict
    extra: dict  # passthrough optional columns


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def _validate_columns(header: list[str], path: str) -> None:
    missing = REQUIRED_COLUMNS - set(header)
    if missing:
        raise ValueError(
            f"CSV '{path}' is missing required columns: {sorted(missing)}"
        )


def _parse_score(raw: str, row_num: int) -> float:
    try:
        score = float(raw)
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"Row {row_num}: human_score '{raw}' is not a valid float"
        ) from exc
    if not (0.0 <= score <= 1.0):
        raise ValueError(
            f"Row {row_num}: human_score {score} is outside [0.0, 1.0]"
        )
    return score


def _validate_grader_id(grader_id: str, row_num: int) -> None:
    if grader_id not in VALID_GRADER_IDS:
        raise ValueError(
            f"Row {row_num}: unknown grader_id '{grader_id}'. "
            f"Valid: {sorted(VALID_GRADER_IDS)}"
        )


def _validate_outreach_mode(mode: str, row_num: int) -> None:
    if mode not in VALID_OUTREACH_MODES:
        raise ValueError(
            f"Row {row_num}: unknown outreach_mode '{mode}'. "
            f"Valid: {sorted(VALID_OUTREACH_MODES)}"
        )


_REQUIRED_COLUMNS: frozenset[str] = frozenset({
    "draft_id", "draft_text", "grader_id", "human_score",
    "recipient_class", "outreach_mode",
})

_BOOL_COLUMNS: frozenset[str] = frozenset({"asymmetric_insight_required"})


def _build_run_context(row: dict[str, str]) -> dict:
    """Synthesise a run_context compatible with judge.grade().

    Required keys are always set. Any extra columns beyond REQUIRED_COLUMNS
    are passed through so that judge heuristics can consume them (e.g.
    personalization_mode, asymmetric_insight_required).
    """
    ctx: dict = {
        "output": {"text": row.get("draft_text", "")},
        "recipient_class": row.get("recipient_class", ""),
        "outreach_mode": row.get("outreach_mode", ""),
    }
    for k, v in row.items():
        if k in _REQUIRED_COLUMNS or k in ctx:
            continue
        # Coerce known boolean columns
        if k in _BOOL_COLUMNS:
            ctx[k] = v.strip().lower() in ("1", "true", "yes")
        else:
            ctx[k] = v
    return ctx


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------


def ingest_csv(
    csv_path: Path,
    *,
    strict: bool = True,
) -> Iterator[HoldoutRow]:
    """Yield validated HoldoutRow objects from csv_path.

    Parameters
    ----------
    csv_path : Path to the input CSV file.
    strict   : When True (default), a validation error aborts the run.
               When False, invalid rows are skipped (logged to stderr).
    """
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError(f"CSV '{csv_path}' appears to be empty.")
        _validate_columns(list(reader.fieldnames), str(csv_path))

        for row_num, raw_row in enumerate(reader, start=2):  # 1=header
            try:
                grader_id = raw_row["grader_id"].strip()
                _validate_grader_id(grader_id, row_num)

                outreach_mode = raw_row["outreach_mode"].strip()
                _validate_outreach_mode(outreach_mode, row_num)

                human_score = _parse_score(raw_row["human_score"].strip(), row_num)

                draft_id = raw_row["draft_id"].strip()
                if not draft_id:
                    raise ValueError(f"Row {row_num}: draft_id is empty")

                draft_text = raw_row["draft_text"].strip()

                extra = {
                    k: raw_row.get(k, "")
                    for k in OPTIONAL_PASSTHROUGH
                    if k in (reader.fieldnames or [])
                }

                yield HoldoutRow(
                    draft_id=draft_id,
                    draft_text=draft_text,
                    grader_id=grader_id,
                    human_score=human_score,
                    recipient_class=raw_row["recipient_class"].strip(),
                    outreach_mode=outreach_mode,
                    run_context=_build_run_context(raw_row),
                    extra=extra,
                )
            except ValueError as exc:
                if strict:
                    raise
                print(f"[SKIP] {exc}", file=sys.stderr)


def write_jsonl(rows: Iterator[HoldoutRow], output_path: Path) -> int:
    """Write rows to output_path as JSONL. Returns count written."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with open(output_path, "w", encoding="utf-8") as fh:
        for row in rows:
            payload = {
                "draft_id": row.draft_id,
                "draft_text": row.draft_text,
                "grader_id": row.grader_id,
                "human_score": row.human_score,
                "recipient_class": row.recipient_class,
                "outreach_mode": row.outreach_mode,
                "run_context": row.run_context,
                **row.extra,
            }
            fh.write(json.dumps(payload) + "\n")
            count += 1
    return count


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Ingest human-labeled holdout CSV into canonical JSONL for "
            "lic_judge_spearman_calibration.py"
        )
    )
    p.add_argument("--input", required=True, help="Path to labeled CSV file")
    p.add_argument(
        "--output",
        default="artifacts/calibration/lic_holdout_corpus.jsonl",
        help="Output JSONL path (default: artifacts/calibration/lic_holdout_corpus.jsonl)",
    )
    p.add_argument(
        "--lenient",
        action="store_true",
        default=False,
        help="Skip invalid rows instead of aborting (default: strict)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        rows = ingest_csv(input_path, strict=not args.lenient)
        count = write_jsonl(rows, output_path)
        print(f"Ingested {count} rows → {output_path}")
        return 0
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "HoldoutRow",
    "ingest_csv",
    "write_jsonl",
    "REQUIRED_COLUMNS",
    "VALID_GRADER_IDS",
    "VALID_OUTREACH_MODES",
]
