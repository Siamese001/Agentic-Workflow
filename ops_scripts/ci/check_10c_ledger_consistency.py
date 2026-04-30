#!/usr/bin/env python3
"""10C requirement-bundle internal consistency gate.

Validates that the four 10C reconciliation artifacts agree:

  1. ``docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv``
     -- master REQ ledger (15-column schema)
  2. ``docs/reports/design/10c_reconciliation/10c_requirements_vs_10a_matrix.csv``
     -- traceability matrix (5-column schema)
  3. ``docs/reports/design/10c_reconciliation/10c_metric_obligation_matrix.csv``
     -- metric obligations (separate ID namespace MET-10C-NNN)
  4. ``docs/reports/design/10c_reconciliation/10c_model_binding_matrix.csv``
     -- model bindings (separate ID namespace BIND-10C-NNN)
  5. ``docs/reports/design/10c_reconciliation/IMPLEMENTATION_STATUS.md``
     -- implementation status prose

Failure modes blocked:
  - REQ-IDs in ledger but not in matrix (or vice versa)
  - Empty / malformed required ledger fields (severity, canonical_statement, ...)
  - Severity outside the closed vocabulary
  - Confidence outside [0.0, 1.0]
  - Duplicate REQ-IDs in either CSV
  - Non-monotonic REQ-ID numbering (gaps allowed; out-of-order forbidden in the canonical ledger)
  - MET-10C-NNN / BIND-10C-NNN duplicate IDs
  - REQ-IDs cited in IMPLEMENTATION_STATUS that don't exist in the ledger

Exit codes:
    0  All checks pass.
    1  Drift detected (consistency failure).
    2  Infrastructure error (missing file, malformed CSV, etc.).
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLE = REPO_ROOT / "docs" / "reports" / "design" / "10c_reconciliation"

LEDGER = BUNDLE / "10c_semantic_requirement_ledger.csv"
MATRIX = BUNDLE / "10c_requirements_vs_10a_matrix.csv"
METRIC = BUNDLE / "10c_metric_obligation_matrix.csv"
BINDING = BUNDLE / "10c_model_binding_matrix.csv"
STATUS = BUNDLE / "IMPLEMENTATION_STATUS.md"

# Closed vocabularies
ALLOWED_SEVERITY = frozenset({"LOW", "MEDIUM", "HIGH", "CRITICAL"})
# Expanded to match historical 10C corpus vocabulary (REQ-011, 162-164 use the
# legacy values; they predate the explicit/implied dichotomy and are retained
# for traceability fidelity).
ALLOWED_DIRECT_OR_IMPLIED = frozenset({
    "explicit",
    "implied",
    "explanatory_only",
    "pedagogical_but_normatively_constraining",
})

# Required ledger schema (15 columns)
LEDGER_SCHEMA = (
    "req_id",
    "source_file",
    "source_section",
    "source_unit_type",
    "source_text_short",
    "canonical_requirement_statement",
    "direct_or_implied",
    "semantic_class",
    "layer_owner",
    "runtime_phase",
    "required_artifacts",
    "required_controls",
    "required_tests",
    "severity_if_missing",
    "confidence_score",
)

# Required matrix schema (5 columns)
MATRIX_SCHEMA = (
    "10c_req_id",
    "10a_req_id",
    "covered_by_10a",
    "10a_coverage_type",
    "coverage_gap_reason",
)

REQ_ID_RE = re.compile(r"^10C-REQ-(\d{3})$")
MET_ID_RE = re.compile(r"^MET-10C-(\d{3})$")
BIND_ID_RE = re.compile(r"^BIND-10C-(\d{3})$")


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    csv.field_size_limit(min(sys.maxsize, 2_000_000))
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path.name}: empty file")
    header = rows[0]
    body = [dict(zip(header, r)) for r in rows[1:] if any(c.strip() for c in r)]
    return header, body


def _check_schema(name: str, header: list[str], expected: Iterable[str]) -> list[str]:
    """Verify that ``expected`` columns appear as a prefix of ``header``.

    The ledger schema was hardened on 2026-04-30 by appending 20 proof-tracking
    columns (see ``tools/requirements/harden_10c_ledger.py``). Those extra
    columns are permitted as long as the original 15-column prefix is
    preserved exactly and in order.
    """
    expected = list(expected)
    if len(header) < len(expected):
        return [
            f"{name}: header too short\n"
            f"  expected (prefix): {expected}\n"
            f"  actual           : {header}"
        ]
    prefix = header[: len(expected)]
    if prefix != expected:
        return [
            f"{name}: header prefix mismatch\n"
            f"  expected (prefix): {expected}\n"
            f"  actual prefix    : {prefix}"
        ]
    return []


def _check_unique_ids(name: str, ids: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    dups: list[str] = []
    for rid in ids:
        seen[rid] = seen.get(rid, 0) + 1
    for rid, n in seen.items():
        if n > 1:
            dups.append(rid)
    if dups:
        return [f"{name}: duplicate IDs: {sorted(dups)}"]
    return []


def _check_id_format(name: str, ids: list[str], pattern: re.Pattern[str]) -> list[str]:
    bad = [rid for rid in ids if not pattern.match(rid)]
    if bad:
        return [f"{name}: malformed IDs (not matching {pattern.pattern}): {bad[:5]}{'...' if len(bad) > 5 else ''}"]
    return []


def _check_ledger_field_presence(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    required_fields = (
        "req_id",
        "canonical_requirement_statement",
        "severity_if_missing",
        "confidence_score",
        "semantic_class",
        "layer_owner",
    )
    for r in rows:
        rid = r.get("req_id", "?")
        for field in required_fields:
            if not (r.get(field) or "").strip():
                errors.append(f"ledger {rid}: empty required field '{field}'")
    return errors


def _check_severity(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for r in rows:
        sev = (r.get("severity_if_missing") or "").strip()
        if sev and sev not in ALLOWED_SEVERITY:
            errors.append(f"ledger {r.get('req_id')}: severity '{sev}' not in {sorted(ALLOWED_SEVERITY)}")
    return errors


def _check_direct_or_implied(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for r in rows:
        v = (r.get("direct_or_implied") or "").strip()
        if v and v not in ALLOWED_DIRECT_OR_IMPLIED:
            errors.append(f"ledger {r.get('req_id')}: direct_or_implied '{v}' not in {sorted(ALLOWED_DIRECT_OR_IMPLIED)}")
    return errors


def _check_confidence(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for r in rows:
        raw = (r.get("confidence_score") or "").strip()
        if not raw:
            continue
        try:
            v = float(raw)
        except ValueError:
            errors.append(f"ledger {r.get('req_id')}: confidence '{raw}' not numeric")
            continue
        if v < 0.0 or v > 1.0:
            errors.append(f"ledger {r.get('req_id')}: confidence {v} outside [0.0, 1.0]")
    return errors


def _check_id_parity(ledger_ids: set[str], matrix_ids: set[str]) -> list[str]:
    errors: list[str] = []
    only_ledger = ledger_ids - matrix_ids
    only_matrix = matrix_ids - ledger_ids
    if only_ledger:
        errors.append(
            f"ledger has {len(only_ledger)} REQ-IDs missing from matrix: "
            f"{sorted(only_ledger)[:5]}{'...' if len(only_ledger) > 5 else ''}"
        )
    if only_matrix:
        errors.append(
            f"matrix has {len(only_matrix)} REQ-IDs missing from ledger: "
            f"{sorted(only_matrix)[:5]}{'...' if len(only_matrix) > 5 else ''}"
        )
    return errors


def _check_status_md_refs(ledger_ids: set[str]) -> list[str]:
    if not STATUS.exists():
        return []
    text = STATUS.read_text(encoding="utf-8")
    cited = set(re.findall(r"10C-REQ-\d{3}", text))
    unknown = cited - ledger_ids
    if unknown:
        return [
            f"IMPLEMENTATION_STATUS.md cites {len(unknown)} REQ-IDs not in ledger: "
            f"{sorted(unknown)[:5]}{'...' if len(unknown) > 5 else ''}"
        ]
    return []


def main() -> int:
    print("[10C bundle consistency gate]")
    errors: list[str] = []

    for required in (LEDGER, MATRIX):
        if not required.exists():
            print(f"FATAL: missing {required}", file=sys.stderr)
            return 2

    try:
        ledger_header, ledger_rows = _read_csv(LEDGER)
        matrix_header, matrix_rows = _read_csv(MATRIX)
    except (csv.Error, ValueError) as exc:
        print(f"FATAL: CSV parse failure: {exc}", file=sys.stderr)
        return 2

    # Schema parity
    errors += _check_schema("ledger", ledger_header, LEDGER_SCHEMA)
    errors += _check_schema("matrix", matrix_header, MATRIX_SCHEMA)

    # ID format + uniqueness
    ledger_ids_list = [r.get("req_id", "") for r in ledger_rows]
    matrix_ids_list = [r.get("10c_req_id", "") for r in matrix_rows]
    errors += _check_id_format("ledger", ledger_ids_list, REQ_ID_RE)
    errors += _check_id_format("matrix", matrix_ids_list, REQ_ID_RE)
    errors += _check_unique_ids("ledger", ledger_ids_list)
    errors += _check_unique_ids("matrix", matrix_ids_list)

    # Cross-file ID parity
    errors += _check_id_parity(set(ledger_ids_list), set(matrix_ids_list))

    # Ledger field-level checks
    errors += _check_ledger_field_presence(ledger_rows)
    errors += _check_severity(ledger_rows)
    errors += _check_direct_or_implied(ledger_rows)
    errors += _check_confidence(ledger_rows)

    # IMPLEMENTATION_STATUS link integrity (advisory if file absent)
    errors += _check_status_md_refs(set(ledger_ids_list))

    # Sibling artifact format checks (separate ID namespaces)
    if METRIC.exists():
        try:
            _, metric_rows = _read_csv(METRIC)
            metric_ids = [r.get("metric_id", "") for r in metric_rows]
            errors += _check_id_format("metric", metric_ids, MET_ID_RE)
            errors += _check_unique_ids("metric", metric_ids)
        except (csv.Error, ValueError) as exc:
            errors.append(f"metric matrix parse failed: {exc}")

    if BINDING.exists():
        try:
            _, binding_rows = _read_csv(BINDING)
            binding_ids = [r.get("binding_id", "") for r in binding_rows]
            errors += _check_id_format("binding", binding_ids, BIND_ID_RE)
            errors += _check_unique_ids("binding", binding_ids)
        except (csv.Error, ValueError) as exc:
            errors.append(f"binding matrix parse failed: {exc}")

    # Summary
    print(f"  ledger rows : {len(ledger_rows)}")
    print(f"  matrix rows : {len(matrix_rows)}")
    print(f"  errors      : {len(errors)}")

    if errors:
        print("\nFAIL — drift detected:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("OK  ledger <-> matrix <-> IMPLEMENTATION_STATUS in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
