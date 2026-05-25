"""Cross-file consistency gate for the 10C reconciliation bundle (W4d-3).

Validates that the four bundle artifacts agree:

  1. ``10c_semantic_requirement_ledger.csv``           (W4d-2, 200 rows x 43 cols)
  2. ``10c_requirements_vs_10a_matrix.csv``            (W4d-3, 200 rows x 13 cols)
  3. ``10c_metric_obligation_matrix.csv``              (W4d-3, 35  rows x 28 cols)
  4. ``10c_model_binding_matrix.csv`` +
     ``10c_nonmodel_control_binding_matrix.csv``       (W4d-3, 8+6 rows x 27 cols)

Checks performed:

  C1. REQ ID parity between ledger and requirements_vs_10a matrix.
  C2. Every CRITICAL/HIGH ledger REQ has all 8 mandatory proof fields populated.
  C3. Every metric in metric_obligation has at least one ``req_id_refs`` entry,
      and every referenced REQ exists in the ledger.
  C4. Every binding (model + nonmodel) has at least one ``req_id_refs`` entry,
      and every referenced REQ exists in the ledger.
  C5. Every ``canonical_owner_surface`` value across the bundle is in the
      canonical 15-surface vocabulary.
  C6. Every NEW best-practice gap row in requirements_vs_10a (REQ-174..200)
      either has an external_proof_pack_ref OR a corresponding plan file
      mentioned in coverage_gap_reason.
  C7. The split between model_binding and nonmodel_control_binding is
      well-formed: no binding_id appears in both files, every binding_id
      exists in exactly one of the two.
  C8. Every ``coverage_status_normalized`` value is in the canonical 4-value
      vocabulary.

Exit codes:
  0 = all checks passed
  1 = at least one consistency error
  2 = bundle file missing or unreadable
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BUNDLE = REPO_ROOT / "docs" / "reports" / "design" / "10c_reconciliation"
ARTIFACTS = REPO_ROOT / "artifacts" / "requirements"

LEDGER = BUNDLE / "10c_semantic_requirement_ledger.csv"
MATRIX_REQS = BUNDLE / "10c_requirements_vs_10a_matrix.csv"
MATRIX_METRIC = BUNDLE / "10c_metric_obligation_matrix.csv"
MATRIX_MODEL = BUNDLE / "10c_model_binding_matrix.csv"
MATRIX_NONMODEL = BUNDLE / "10c_nonmodel_control_binding_matrix.csv"

JSON_OUT = ARTIFACTS / "10c_cross_file_consistency.json"
MD_OUT = ARTIFACTS / "10c_cross_file_consistency.md"

CANONICAL_OWNER_VOCAB = frozenset({
    "00A_L5_Governance_Safety",
    "00B_L4_State_Archive_and_UWG",
    "00C_Runtime_Gates_Current_Run_Mesh",
    "01_U0_Request_Intake",
    "02_L1_Reasoning_Plan",
    "03_L0_Route_Decision",
    "03_L3_Orchestration",
    "03A_C0_Context_Engine",
    "03B_PA_Prompt_Assembly",
    "04_L2_Execute",
    "05_Exit_Evaluation_and_Control",
    "06_L6_Observability_and_System_Learning",
    "99_End_to_End_Runtime_Proof_and_Acceptance",
    "Offline_Ingestion_Index_Build",
    "Cross_Cutting_Observability_Replay_Audit",
})

CANONICAL_COVERAGE_STATUS = frozenset({"YES", "PARTIAL", "NO", "NOT_APPLICABLE"})

MANDATORY_LEDGER_PROOF_FIELDS = (
    "runtime_artifact_expected",
    "otel_span_expected",
    "replay_proof_expected",
    "negative_control_expected",
    "negative_control_specific",
    "test_file_expected",
    "acceptance_command",
    "ci_gate_name",
)

NEW_BEST_PRACTICE_RANGE = range(174, 201)  # REQ-174 through REQ-200 inclusive


def _load_csv(path: Path) -> list[dict[str, str]]:
    csv.field_size_limit(2_000_000)
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _split_req_refs(refs: str) -> list[str]:
    if not refs:
        return []
    # Accept either space- or comma-separated lists
    raw = refs.replace(",", " ")
    return [tok.strip() for tok in raw.split() if tok.strip()]


def _check_files_exist() -> list[str]:
    errors: list[str] = []
    for p in (LEDGER, MATRIX_REQS, MATRIX_METRIC, MATRIX_MODEL, MATRIX_NONMODEL):
        if not p.exists():
            errors.append(f"missing bundle file: {p.relative_to(REPO_ROOT)}")
    return errors


def _check_c1_id_parity(ledger_ids: set[str], reqs_matrix_ids: set[str]) -> list[str]:
    errors: list[str] = []
    only_ledger = ledger_ids - reqs_matrix_ids
    only_matrix = reqs_matrix_ids - ledger_ids
    if only_ledger:
        errors.append(
            f"C1: {len(only_ledger)} ledger REQ-IDs missing from requirements_vs_10a "
            f"matrix (sample: {sorted(only_ledger)[:5]})"
        )
    if only_matrix:
        errors.append(
            f"C1: {len(only_matrix)} requirements_vs_10a REQ-IDs missing from ledger "
            f"(sample: {sorted(only_matrix)[:5]})"
        )
    return errors


def _check_c2_critical_high_proof(ledger_rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for r in ledger_rows:
        sev = (r.get("severity_if_missing") or "").strip().upper()
        if sev not in {"CRITICAL", "HIGH"}:
            continue
        missing = [f for f in MANDATORY_LEDGER_PROOF_FIELDS if not (r.get(f) or "").strip()]
        if missing:
            errors.append(
                f"C2: {r['req_id']} ({sev}) missing proof fields: {missing}"
            )
    return errors


def _check_c3_metric_req_linkage(
    metric_rows: list[dict[str, str]], ledger_ids: set[str]
) -> list[str]:
    errors: list[str] = []
    unlinked = 0
    bad_refs: list[str] = []
    for r in metric_rows:
        refs = _split_req_refs(r.get("req_id_refs", ""))
        if not refs:
            unlinked += 1
            errors.append(f"C3: {r['metric_id']} ({r.get('metric_name', '')}) has no req_id_refs")
            continue
        for ref in refs:
            if ref not in ledger_ids:
                bad_refs.append(f"{r['metric_id']}->{ref}")
    if bad_refs:
        errors.append(
            f"C3: {len(bad_refs)} metric->REQ refs point to nonexistent ledger rows "
            f"(sample: {bad_refs[:5]})"
        )
    return errors


def _check_c4_binding_req_linkage(
    binding_rows: list[dict[str, str]], ledger_ids: set[str], label: str
) -> list[str]:
    errors: list[str] = []
    bad_refs: list[str] = []
    for r in binding_rows:
        refs = _split_req_refs(r.get("req_id_refs", ""))
        if not refs:
            errors.append(f"C4: [{label}] {r['binding_id']} has no req_id_refs")
            continue
        for ref in refs:
            if ref not in ledger_ids:
                bad_refs.append(f"{r['binding_id']}->{ref}")
    if bad_refs:
        errors.append(
            f"C4: [{label}] {len(bad_refs)} binding->REQ refs point to nonexistent "
            f"ledger rows (sample: {bad_refs[:5]})"
        )
    return errors


def _check_c5_owner_vocab(
    rows: list[dict[str, str]], col: str, label: str
) -> list[str]:
    errors: list[str] = []
    bad: list[str] = []
    for r in rows:
        owner = (r.get(col) or "").strip()
        if not owner:
            continue
        if owner not in CANONICAL_OWNER_VOCAB:
            bad.append(f"{r.get('req_id') or r.get('metric_id') or r.get('binding_id') or r.get('10c_req_id')}: '{owner}'")
    if bad:
        errors.append(
            f"C5: [{label}] {len(bad)} rows have non-canonical owner values "
            f"(sample: {bad[:5]})"
        )
    return errors


def _check_c6_new_best_practice_proof_pack(
    reqs_matrix_rows: list[dict[str, str]],
) -> list[str]:
    errors: list[str] = []
    weak: list[str] = []
    for r in reqs_matrix_rows:
        rid = r["10c_req_id"]
        try:
            num = int(rid.rsplit("-", 1)[-1])
        except ValueError:
            continue
        if num not in NEW_BEST_PRACTICE_RANGE:
            continue
        # Must be marked as new best practice
        gap_class = (r.get("baseline_gap_class") or "").strip()
        if gap_class != "new_best_practice":
            errors.append(
                f"C6: {rid} is in REQ-174..200 range but baseline_gap_class='{gap_class}' "
                f"(expected new_best_practice)"
            )
            continue
        # Must have either external_proof_pack_ref OR a wave label OR a plan reference
        ext = (r.get("external_proof_pack_ref") or "").strip()
        wave = (r.get("new_best_practice_wave") or "").strip()
        reason = (r.get("coverage_gap_reason") or "").strip()
        if not ext and not wave and "see " not in reason.lower():
            weak.append(rid)
    if weak:
        errors.append(
            f"C6: {len(weak)} new-best-practice rows lack proof pack OR wave OR plan ref "
            f"(sample: {weak[:5]})"
        )
    return errors


def _check_c7_binding_split(
    model_rows: list[dict[str, str]], nonmodel_rows: list[dict[str, str]]
) -> list[str]:
    errors: list[str] = []
    model_ids = {r["binding_id"] for r in model_rows}
    nonmodel_ids = {r["binding_id"] for r in nonmodel_rows}
    overlap = model_ids & nonmodel_ids
    if overlap:
        errors.append(f"C7: {len(overlap)} binding_ids appear in BOTH files: {sorted(overlap)}")
    # Validate is_model_invocation flag matches the file
    for r in model_rows:
        if (r.get("is_model_invocation") or "").strip().lower() != "true":
            errors.append(f"C7: model_binding row {r['binding_id']} has is_model_invocation != 'true'")
    for r in nonmodel_rows:
        if (r.get("is_model_invocation") or "").strip().lower() != "false":
            errors.append(f"C7: nonmodel_binding row {r['binding_id']} has is_model_invocation != 'false'")
    return errors


def _check_c8_coverage_status_vocab(reqs_matrix_rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    bad: list[str] = []
    for r in reqs_matrix_rows:
        status = (r.get("coverage_status_normalized") or "").strip()
        if status and status not in CANONICAL_COVERAGE_STATUS:
            bad.append(f"{r['10c_req_id']}: '{status}'")
    if bad:
        errors.append(
            f"C8: {len(bad)} requirements_vs_10a rows have invalid "
            f"coverage_status_normalized (sample: {bad[:5]})"
        )
    return errors


def _emit_report(report: dict, cmd: str) -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    payload = {
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "validation_command": cmd,
        "bundle": {
            "ledger": str(LEDGER.relative_to(REPO_ROOT)).replace("\\", "/"),
            "requirements_vs_10a_matrix": str(MATRIX_REQS.relative_to(REPO_ROOT)).replace("\\", "/"),
            "metric_obligation_matrix": str(MATRIX_METRIC.relative_to(REPO_ROOT)).replace("\\", "/"),
            "model_binding_matrix": str(MATRIX_MODEL.relative_to(REPO_ROOT)).replace("\\", "/"),
            "nonmodel_control_binding_matrix": str(MATRIX_NONMODEL.relative_to(REPO_ROOT)).replace("\\", "/"),
        },
        "row_counts": report["row_counts"],
        "column_counts": report["column_counts"],
        "checks": report["checks"],
        "errors": report["errors"],
        "warnings": report["warnings"],
        "passed": not report["errors"],
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = ["# 10C Cross-File Consistency Report (W4d-3)", ""]
    md.append(f"- Validated at (UTC): {payload['validated_at_utc']}")
    md.append(f"- Command: `{cmd}`")
    md.append(f"- Passed: **{payload['passed']}**")
    md.append("")
    md.append("## Bundle row + column counts")
    md.append("")
    md.append("| File | Rows | Columns |")
    md.append("|---|---:|---:|")
    for label, key in (
        ("Ledger", "ledger"),
        ("Requirements vs 10a", "requirements_vs_10a"),
        ("Metric obligation", "metric_obligation"),
        ("Model binding", "model_binding"),
        ("Nonmodel control binding", "nonmodel_control_binding"),
    ):
        md.append(
            f"| {label} | {report['row_counts'][key]} | {report['column_counts'][key]} |"
        )
    md.append("")
    md.append("## Check summary")
    md.append("")
    for cid, info in report["checks"].items():
        md.append(f"- **{cid}** ({info['name']}): {'PASS' if info['passed'] else 'FAIL'} — {info['message']}")
    md.append("")
    if report["errors"]:
        md.append("## Errors")
        md.append("")
        for e in report["errors"]:
            md.append(f"- {e}")
        md.append("")
    if report["warnings"]:
        md.append("## Warnings")
        md.append("")
        for w in report["warnings"]:
            md.append(f"- {w}")
        md.append("")
    MD_OUT.write_text("\n".join(md), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="10C cross-file consistency gate (W4d-3).")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any error (default).")
    parser.add_argument("--no-strict", dest="strict", action="store_false")
    parser.set_defaults(strict=True)
    args = parser.parse_args()

    cmd = "python ops_scripts/ci/check_10c_cross_file_consistency.py" + (
        " --strict" if args.strict else " --no-strict"
    )

    print("[10C cross-file consistency gate W4d-3]")
    file_errors = _check_files_exist()
    if file_errors:
        for e in file_errors:
            print(f"  FATAL: {e}", file=sys.stderr)
        return 2

    ledger_rows = _load_csv(LEDGER)
    reqs_matrix_rows = _load_csv(MATRIX_REQS)
    metric_rows = _load_csv(MATRIX_METRIC)
    model_rows = _load_csv(MATRIX_MODEL)
    nonmodel_rows = _load_csv(MATRIX_NONMODEL)

    ledger_ids = {r["req_id"] for r in ledger_rows}
    reqs_matrix_ids = {r["10c_req_id"] for r in reqs_matrix_rows}

    checks: dict[str, dict[str, str | bool]] = {}
    all_errors: list[str] = []

    # C1
    e = _check_c1_id_parity(ledger_ids, reqs_matrix_ids)
    checks["C1"] = {
        "name": "REQ ID parity (ledger <-> requirements_vs_10a)",
        "passed": not e,
        "message": "all 200 IDs match" if not e else "; ".join(e),
    }
    all_errors.extend(e)

    # C2
    e = _check_c2_critical_high_proof(ledger_rows)
    checks["C2"] = {
        "name": "CRITICAL/HIGH proof-field completeness",
        "passed": not e,
        "message": "all CRITICAL/HIGH rows have 8 mandatory proof fields" if not e else f"{len(e)} rows missing proof fields",
    }
    all_errors.extend(e)

    # C3
    e = _check_c3_metric_req_linkage(metric_rows, ledger_ids)
    checks["C3"] = {
        "name": "Metric -> REQ linkage",
        "passed": not e,
        "message": "all 35 metrics linked to >=1 valid ledger REQ" if not e else f"{len(e)} linkage errors",
    }
    all_errors.extend(e)

    # C4
    e_model = _check_c4_binding_req_linkage(model_rows, ledger_ids, "model")
    e_nonmodel = _check_c4_binding_req_linkage(nonmodel_rows, ledger_ids, "nonmodel")
    checks["C4"] = {
        "name": "Binding -> REQ linkage (model + nonmodel)",
        "passed": not (e_model or e_nonmodel),
        "message": "all bindings linked to >=1 valid ledger REQ"
        if not (e_model or e_nonmodel)
        else f"{len(e_model) + len(e_nonmodel)} linkage errors",
    }
    all_errors.extend(e_model)
    all_errors.extend(e_nonmodel)

    # C5
    e_l = _check_c5_owner_vocab(ledger_rows, "canonical_owner_surface", "ledger")
    e_r = _check_c5_owner_vocab(reqs_matrix_rows, "canonical_owner_surface", "requirements_vs_10a")
    e_m = _check_c5_owner_vocab(metric_rows, "canonical_owner_surface", "metric_obligation")
    e_mb = _check_c5_owner_vocab(model_rows, "canonical_owner_surface", "model_binding")
    e_nb = _check_c5_owner_vocab(nonmodel_rows, "canonical_owner_surface", "nonmodel_control_binding")
    e_all_owner = e_l + e_r + e_m + e_mb + e_nb
    checks["C5"] = {
        "name": "Owner vocabulary canonicality (all 5 files)",
        "passed": not e_all_owner,
        "message": "all owner values are in canonical 15-surface vocabulary"
        if not e_all_owner
        else f"{len(e_all_owner)} non-canonical owner values",
    }
    all_errors.extend(e_all_owner)

    # C6
    e = _check_c6_new_best_practice_proof_pack(reqs_matrix_rows)
    checks["C6"] = {
        "name": "New-best-practice rows have proof-pack OR wave OR plan ref",
        "passed": not e,
        "message": "all REQ-174..200 rows have wave/plan ref" if not e else f"{len(e)} weak refs",
    }
    all_errors.extend(e)

    # C7
    e = _check_c7_binding_split(model_rows, nonmodel_rows)
    checks["C7"] = {
        "name": "Model/nonmodel binding split is well-formed",
        "passed": not e,
        "message": f"{len(model_rows)} model + {len(nonmodel_rows)} nonmodel; no overlap"
        if not e
        else f"{len(e)} split errors",
    }
    all_errors.extend(e)

    # C8
    e = _check_c8_coverage_status_vocab(reqs_matrix_rows)
    checks["C8"] = {
        "name": "coverage_status_normalized vocabulary canonicality",
        "passed": not e,
        "message": "all coverage_status values in {YES, PARTIAL, NO, NOT_APPLICABLE}"
        if not e
        else f"{len(e)} non-canonical values",
    }
    all_errors.extend(e)

    report = {
        "row_counts": {
            "ledger": len(ledger_rows),
            "requirements_vs_10a": len(reqs_matrix_rows),
            "metric_obligation": len(metric_rows),
            "model_binding": len(model_rows),
            "nonmodel_control_binding": len(nonmodel_rows),
        },
        "column_counts": {
            "ledger": len(ledger_rows[0]) if ledger_rows else 0,
            "requirements_vs_10a": len(reqs_matrix_rows[0]) if reqs_matrix_rows else 0,
            "metric_obligation": len(metric_rows[0]) if metric_rows else 0,
            "model_binding": len(model_rows[0]) if model_rows else 0,
            "nonmodel_control_binding": len(nonmodel_rows[0]) if nonmodel_rows else 0,
        },
        "checks": checks,
        "errors": all_errors,
        "warnings": [],
    }
    _emit_report(report, cmd)

    print(f"  ledger rows                      : {report['row_counts']['ledger']}")
    print(f"  requirements_vs_10a rows         : {report['row_counts']['requirements_vs_10a']}")
    print(f"  metric_obligation rows           : {report['row_counts']['metric_obligation']}")
    print(f"  model_binding rows               : {report['row_counts']['model_binding']}")
    print(f"  nonmodel_control_binding rows    : {report['row_counts']['nonmodel_control_binding']}")
    for cid, info in checks.items():
        flag = "PASS" if info["passed"] else "FAIL"
        print(f"  {cid:<3} {flag} -- {info['name']}")
    print(f"  artifacts                        : {JSON_OUT.relative_to(REPO_ROOT)}, {MD_OUT.relative_to(REPO_ROOT)}")
    print(f"  total errors                     : {len(all_errors)}")

    if all_errors:
        print("\nFAIL -- consistency errors:")
        for err in all_errors[:20]:
            print(f"  - {err}")
        if len(all_errors) > 20:
            print(f"  ... +{len(all_errors) - 20} more")
        return 1 if args.strict else 0

    print("\nOK  10C cross-file consistency passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
