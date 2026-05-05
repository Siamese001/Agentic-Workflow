"""Production log miner for RationaleQualityJudge holdout expansion.

Plan: apps-underwriting-ai-rationale-judge-deferred-d4e7a2 W3.P3.2.

Reads production underwriting decision logs from a configurable source,
applies PII redaction, and emits candidate holdout examples to a staging
directory for human review.  Examples are NEVER written directly to the
holdout dataset — a human reviewer must inspect and promote them.

PII redaction
-------------
The following fields are stripped / masked before any example is written:

- Applicant name (``applicant_name``, ``borrower_name``)
- SSN / tax ID (``ssn``, ``tax_id``, ``ein``) — replaced with ``<REDACTED_SSN>``
- Date of birth (``dob``, ``date_of_birth``) — replaced with ``<REDACTED_DOB>``
- Street address (``address``, ``street``, ``zip``, ``postal_code``)
- Phone / email (``phone``, ``email``)
- Free-text regex patterns for common PII in rationale text

Usage
-----
::

    python tools/underwriting/prod_log_miner.py \\
        --source /path/to/decision_logs.jsonl \\
        --output artifacts/staging/rationale_holdout_candidates/ \\
        --limit 500

Environment variables
---------------------
PROD_LOG_MINER_BYPASS=1
    Emit a warning and exit 0 without reading any logs (dry-run mode for CI).

LOG_SOURCE_PATH
    Override the ``--source`` argument.

STAGING_DIR
    Override the ``--output`` argument.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from datetime import date
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

_BYPASS = os.getenv("PROD_LOG_MINER_BYPASS", "").strip() == "1"

_DEFAULT_STAGING = REPO_ROOT / "artifacts" / "staging" / "rationale_holdout_candidates"

_PII_TEXT_PATTERNS: list[tuple[str, str]] = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "<REDACTED_SSN>"),
    (r"\b\d{3}\s\d{2}\s\d{4}\b", "<REDACTED_SSN>"),
    (r"\b[A-Z][a-z]+ [A-Z][a-z]+\b(?=\s+(?:applied|requested|submitted))", "<REDACTED_NAME>"),
    (r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", "<REDACTED_DATE>"),
    (r"\b[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}\b", "<REDACTED_EMAIL>"),
    (r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "<REDACTED_PHONE>"),
    (r"\b\d{5}(?:-\d{4})?\b", "<REDACTED_ZIP>"),
]

_PII_FIELD_KEYS = frozenset(
    {
        "applicant_name",
        "borrower_name",
        "ssn",
        "tax_id",
        "ein",
        "dob",
        "date_of_birth",
        "address",
        "street",
        "zip",
        "postal_code",
        "phone",
        "email",
        "first_name",
        "last_name",
        "full_name",
    }
)

_COMPILED_PATTERNS = [(re.compile(p), repl) for p, repl in _PII_TEXT_PATTERNS]


def redact_text(text: str) -> str:
    """Apply regex-based PII redaction to a free-text string."""
    for pattern, replacement in _COMPILED_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def redact_record(record: dict[str, Any]) -> dict[str, Any]:
    """Deep-copy and redact PII from a log record dict."""
    out: dict[str, Any] = {}
    for key, value in record.items():
        if key.lower() in _PII_FIELD_KEYS:
            out[key] = "<REDACTED>"
        elif isinstance(value, str):
            out[key] = redact_text(value)
        elif isinstance(value, dict):
            out[key] = redact_record(value)
        elif isinstance(value, list):
            out[key] = [
                redact_record(v) if isinstance(v, dict)
                else (redact_text(v) if isinstance(v, str) else v)
                for v in value
            ]
        else:
            out[key] = value
    return out


def _to_candidate(record: dict[str, Any], idx: int) -> dict[str, Any] | None:
    """Convert a raw log record to a holdout candidate shape.

    Returns None if the record lacks the minimum required fields.
    """
    rationale = record.get("rationale") or record.get("rationale_text", "")
    if not rationale or len(rationale.strip()) < 20:
        return None

    clean = redact_record(record)
    candidate_id = f"uw-candidate-{date.today().isoformat()}-{idx:04d}"

    return {
        "candidate_id": candidate_id,
        "source": "prod_log_miner",
        "mined_at": date.today().isoformat(),
        "labeler_id": None,
        "ground_truth_score": None,
        "dim_id": clean.get("dim_id", "UNKNOWN"),
        "rationale_text": clean.get("rationale") or clean.get("rationale_text", ""),
        "evidence_refs": clean.get("evidence_refs", []),
        "decision_verdict": clean.get("verdict") or clean.get("decision_verdict", ""),
        "_review_required": True,
        "_pii_redacted": True,
    }


def mine(
    source_path: Path,
    output_dir: Path,
    limit: int = 500,
) -> dict[str, int]:
    """Mine ``source_path`` (JSONL) and write candidates to ``output_dir``.

    Returns a summary dict with ``total_read``, ``candidates_emitted``,
    ``skipped_no_rationale``, ``skipped_limit``.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    total_read = 0
    emitted = 0
    skipped_no_rationale = 0
    skipped_limit = 0
    candidates: list[dict[str, Any]] = []

    with source_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            total_read += 1
            if emitted >= limit:
                skipped_limit += 1
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                skipped_no_rationale += 1
                continue

            candidate = _to_candidate(record, emitted)
            if candidate is None:
                skipped_no_rationale += 1
                continue

            candidates.append(candidate)
            emitted += 1

    out_path = output_dir / f"candidates_{date.today().isoformat()}_{uuid.uuid4().hex[:8]}.jsonl"
    with out_path.open("w", encoding="utf-8") as fh:
        for c in candidates:
            fh.write(json.dumps(c) + "\n")

    return {
        "total_read": total_read,
        "candidates_emitted": emitted,
        "skipped_no_rationale": skipped_no_rationale,
        "skipped_limit": skipped_limit,
        "output_file": str(out_path),
    }


def main() -> None:
    if _BYPASS:
        print("BYPASS: PROD_LOG_MINER_BYPASS=1 — no log mining performed.")
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="Mine production underwriting logs for holdout candidates."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(os.getenv("LOG_SOURCE_PATH", "")),
        help="Path to a JSONL file of production decision log records.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(os.getenv("STAGING_DIR", str(_DEFAULT_STAGING))),
        help="Output directory for redacted candidate JSONL files.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Maximum number of candidate examples to emit per run.",
    )
    args = parser.parse_args()

    if not args.source or not args.source.exists():
        print(
            "ERROR: --source path not provided or does not exist. "
            "Set LOG_SOURCE_PATH or pass --source.",
            file=sys.stderr,
        )
        sys.exit(2)

    print(f"Mining: {args.source}")
    print(f"Output: {args.output}")
    print(f"Limit:  {args.limit}")

    summary = mine(args.source, args.output, args.limit)
    print(f"\nSummary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print(
        "\nNOTE: Candidates require human review before promotion to holdout. "
        "Set labeler_id and ground_truth_score on each example, then append to "
        "apps_underwriting_ai/holdout/rationale_judge_holdout.yaml."
    )


if __name__ == "__main__":
    main()
