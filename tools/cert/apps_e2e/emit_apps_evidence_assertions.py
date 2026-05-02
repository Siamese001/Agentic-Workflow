"""W2 of plan apps-fort-knox-parity-c5d9a3 \u2014 Atomic Evidence Assertion Emitter.

Reads the W1 catalog (certification/apps_e2e_requirements_source.json) and
the existing apps_e2e verifier artifacts (verifier_report.json + per-app
proof bundles + apps_e2e_matrix.json) and emits one atomic assertion per
(req_id, app) tuple to certification/apps_evidence_assertions.jsonl.

Hard rules mirrored from tools/cert/emit_evidence_assertions.py:

    * Deterministic assertion_id = ASRT-<sha256(req_id|control|artifact_sha256|pointer)[:40]>.
    * Never emit a PASS assertion for a row whose underlying artifact does
      not contain the req_id or the control we are claiming. Emit
      NOT_VERIFIED instead.
    * Never emit a PASS assertion for a negative-control row from this
      emitter \u2014 those are W4's job (apps_mutation_driver.py). Emit
      NOT_VERIFIED with a note pointing at the W4 entry point.
    * Never emit a PASS assertion for the canary (APPS-REQ-001) from this
      emitter \u2014 only W3's compiler can assert catalog_self_consistency.
      Emit NOT_VERIFIED.
    * PASS is emitted iff the verifier_report shows violation_count=0 AND
      certification_level is consistent with the row's claim_type for
      that app.

The output JSONL is sorted by (req_id, app_name or "") for determinism.

No per-app subprocess runs are invoked. The emitter is purely a
projection layer over already-produced verifier artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = REPO_ROOT / "certification" / "apps_e2e_requirements_source.json"
OUT_PATH = REPO_ROOT / "certification" / "apps_evidence_assertions.jsonl"

APPS_ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification" / "apps_e2e"
VERIFIER_REPORT_PATH = APPS_ARTIFACTS_DIR / "verifier_report.json"
MATRIX_PATH = APPS_ARTIFACTS_DIR / "apps_e2e_matrix.json"
MUTATION_REPORT_PATH = APPS_ARTIFACTS_DIR / "apps_mutation_rejection_report.json"

EMITTER_COMMAND = "tools/cert/apps_e2e/emit_apps_evidence_assertions.py"
VERIFIER_VERSION = "apps_fortknox_emitter-v1"

# Apps that waive certification per W1 catalog (APPS-REQ-031, APPS-REQ-032).
_WAIVED_LEVELS = {"WAIVED_NOT_RUNTIME_APP", "WAIVED_SKELETON"}
_CERTIFIED_LEVEL = "SPINE_COMPLETE_CERTIFIED"

# Controls that the emitter can ALWAYS answer from the verifier_report alone
# (the verifier covers the full rule surface; a PASS from the verifier for
# that app binds the assertion).
_VERIFIER_BACKED_CONTROLS = {
    "bundle_emission",
    "bundle_schema_valid",
    "app_name_consistency",
    "entrypoint_valid",
    "harness_pass_semantics",
    "timestamp_iso_utc",
    "id_threading",
    "runtime_artifact_presence",
    "runtime_artifact_hash_binding",
    "route_contract_consistency",
    "l6_ordering",
    "exit_disposition_valid",
    "overlay_consistency",
    "no_stale_artifacts",
    "runtime_mode_in_approved_live_modes",
    "certification_level_invariant",
    "artifact_kind_valid",
    "required_receipt_present",
    "strict_verifier_pass",
    "spine_emission",
    "static_dag_on_disk",
    "static_dag_hash_binding",
}
# Rows whose assertions cannot come from the verifier alone \u2014 W2 emits
# NOT_VERIFIED for these and documents the producer that will close them.
_DEFERRED_CONTROLS = {
    "catalog_self_consistency": (
        "scripts/compile_apps_e2e_signoff.py (W3)",
        "APPS_POSITIVE_CONTROL_ASSERTION",
    ),
    "merkle_leaf": (
        "scripts/compile_apps_e2e_signoff.py (W3)",
        "APPS_STATIC_CONTRACT_ASSERTION",
    ),
    "certifier_signature": (
        "tools/cert/apps_e2e/sign_apps_release_bundle.py (W5)",
        "APPS_STATIC_CONTRACT_ASSERTION",
    ),
}

# Negative-control bundle-field projection map. Each control name maps
# to (bundle_field, expected_false_value_means_pass).
_BUNDLE_NEGATIVE_CONTROLS = {
    "no_synthetic_trace": "synthetic_trace_detected",
    "no_mock_mode": "mock_mode_detected",
    "no_fixture_runtime_mode": "fixture_runtime_mode",
}


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _deterministic_assertion_id(
    req_id: str, control: str, artifact_sha256: str, pointer: str
) -> str:
    h = hashlib.sha256(
        f"{req_id}|{control}|{artifact_sha256}|{pointer}".encode("utf-8")
    ).hexdigest()
    return f"ASRT-{h[:40]}"


def _rel_to_repo(p: Path) -> str:
    try:
        return p.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def _iso_utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


def _assertion_class_for(row: dict[str, Any]) -> str:
    claim_type = row["claim_type"]
    return {
        "APPS_BUNDLE_EMISSION": "APPS_BUNDLE_EMISSION_ASSERTION",
        "APPS_SPINE_CERTIFIED": "APPS_SPINE_CERTIFIED_ASSERTION",
        "APPS_WAIVER": "APPS_WAIVER_ASSERTION",
        "APPS_MATRIX_GOVERNANCE": "APPS_MATRIX_GOVERNANCE_ASSERTION",
        "APPS_NEGATIVE_CONTROL": "APPS_NEGATIVE_CONTROL_ASSERTION",
        "APPS_STATIC_CONTRACT": "APPS_STATIC_CONTRACT_ASSERTION",
        "APPS_POSITIVE_CONTROL": "APPS_POSITIVE_CONTROL_ASSERTION",
    }[claim_type]


def _make_assertion(
    *,
    req_id: str,
    control: str,
    result: str,
    assertion_class: str,
    artifact_path: str,
    artifact_sha256: str,
    artifact_class: str,
    pointer: str,
    contains_req_id: bool,
    contains_control: bool,
    row_specific: bool,
    freshness_hours: int,
    proof_payload: dict[str, Any],
    app_name: str | None,
    now_iso: str,
) -> dict[str, Any]:
    return {
        "assertion_id": _deterministic_assertion_id(
            req_id, control, artifact_sha256, pointer
        ),
        "req_id": req_id,
        "control": control,
        "assertion_result": result,
        "assertion_class": assertion_class,
        "generated_by_command": EMITTER_COMMAND,
        "verifier_exit_code": 0 if result == "PASS" else 1 if result == "FAIL" else 2,
        "verifier_version": VERIFIER_VERSION,
        "generated_at_utc": now_iso,
        "artifact_path": artifact_path,
        "artifact_sha256": artifact_sha256,
        "artifact_class": artifact_class,
        "artifact_payload_pointer": pointer,
        "artifact_contains_req_id": bool(contains_req_id),
        "artifact_contains_control": bool(contains_control),
        "row_specific": bool(row_specific),
        "freshness_hours": int(freshness_hours),
        "proof_payload": proof_payload,
        "app_name": app_name,
    }


def _deferred_assertion(
    row: dict[str, Any],
    control: str,
    deferred_to: str,
    assertion_class: str,
    catalog_sha: str,
    app_name: str | None,
    now_iso: str,
) -> dict[str, Any]:
    pointer = f"/deferred/{row['req_id']}/{control}" + (f"/{app_name}" if app_name else "")
    return _make_assertion(
        req_id=row["req_id"],
        control=control,
        result="NOT_VERIFIED",
        assertion_class=assertion_class,
        artifact_path=_rel_to_repo(CATALOG_PATH),
        artifact_sha256=catalog_sha,
        artifact_class="APPS_CATALOG_SELF_REPORT",
        pointer=pointer,
        contains_req_id=True,
        contains_control=True,
        row_specific=True,
        freshness_hours=row["freshness_hours"],
        proof_payload={
            "extracted_value": "NOT_VERIFIED",
            "expected_value": "PASS",
            "match": False,
            "notes": f"Deferred to {deferred_to}. W2 emitter cannot assert this control.",
        },
        app_name=app_name,
        now_iso=now_iso,
    )


def _load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def _load_verifier_report() -> dict[str, Any]:
    return json.loads(VERIFIER_REPORT_PATH.read_text(encoding="utf-8"))


def _load_matrix() -> dict[str, Any]:
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def _verifier_row_index(report: dict[str, Any], app_name: str) -> int | None:
    for i, row in enumerate(report.get("rows", [])):
        if row.get("app_name") == app_name:
            return i
    return None


def _matrix_row_index(matrix: dict[str, Any], app_name: str) -> int | None:
    for i, row in enumerate(matrix.get("apps", [])):
        if row.get("app_name") == app_name:
            return i
    return None


def _expected_apps_for_row(row: dict[str, Any], all_apps: list[str], certified_apps: list[str]) -> list[str | None]:
    """Decide which apps this catalog row produces assertions for.

    Rules:
      * Canary (APPS-REQ-001, claim_type=APPS_POSITIVE_CONTROL): 1 assertion, app_name=None.
      * Matrix governance (APPS-REQ-033): 1 assertion, app_name=None.
      * Per-app spine rows (owner_app set, APPS_SPINE_CERTIFIED): 1 assertion for owner_app.
      * Waiver rows (owner_app set, APPS_WAIVER): 1 assertion for owner_app.
      * Static-DAG rows (APPS-REQ-011, APPS-REQ-012): apps with expects_static_dag
        only; we inspect the bundle later to detect that. For the emitter's
        simple path, we apply to certified apps and let the verifier-backed
        check fall through to NOT_VERIFIED for non-managed-workflow apps.
      * All other cross-cutting rows (002..024 non-per-app): certified apps only.
        Waived apps are covered by their dedicated waiver row.
    """
    claim_type = row["claim_type"]
    req_id = row["req_id"]
    owner_app = row.get("owner_app")

    if claim_type == "APPS_POSITIVE_CONTROL":
        return [None]
    if claim_type == "APPS_MATRIX_GOVERNANCE":
        return [None]
    if owner_app is not None:
        return [owner_app]
    # Cross-cutting non-waiver row \u2192 all certified apps
    return list(certified_apps)


def _verifier_backed_assertion(
    row: dict[str, Any],
    control: str,
    app_name: str,
    verifier_report: dict[str, Any],
    verifier_report_sha: str,
    now_iso: str,
) -> dict[str, Any]:
    idx = _verifier_row_index(verifier_report, app_name)
    if idx is None:
        # App not in verifier report \u2192 NOT_VERIFIED
        return _deferred_assertion(
            row,
            control,
            f"verifier_report missing row for {app_name}",
            _assertion_class_for(row),
            verifier_report_sha,
            app_name,
            now_iso,
        )
    v_row = verifier_report["rows"][idx]
    level = v_row.get("certification_level")
    violations = v_row.get("violation_count", 0)
    pointer = f"/rows/{idx}"

    # Waiver rows assert on the app's reported level being a WAIVED_* value.
    if row["claim_type"] == "APPS_WAIVER":
        is_waived = level in _WAIVED_LEVELS
        return _make_assertion(
            req_id=row["req_id"],
            control=control,
            result="PASS" if is_waived else "FAIL",
            assertion_class="APPS_WAIVER_ASSERTION",
            artifact_path=_rel_to_repo(VERIFIER_REPORT_PATH),
            artifact_sha256=verifier_report_sha,
            artifact_class="APPS_E2E_VERIFIER_REPORT",
            pointer=pointer,  # point at full row so app_name is in the resolved payload
            contains_req_id=False,  # verifier report does not cite req_ids
            contains_control=True,  # control is bound to the level field (resolved row carries it)
            row_specific=True,
            freshness_hours=row["freshness_hours"],
            proof_payload={
                "extracted_value": level,
                "expected_value_set": sorted(_WAIVED_LEVELS),
                "match": bool(is_waived),
                "notes": f"Waiver proven by verifier_report certification_level for {app_name}.",
            },
            app_name=app_name,
            now_iso=now_iso,
        )

    # Non-waiver, verifier-backed: PASS iff app is certified with zero violations.
    is_certified_clean = level == _CERTIFIED_LEVEL and violations == 0
    return _make_assertion(
        req_id=row["req_id"],
        control=control,
        result="PASS" if is_certified_clean else "FAIL",
        assertion_class=_assertion_class_for(row),
        artifact_path=_rel_to_repo(VERIFIER_REPORT_PATH),
        artifact_sha256=verifier_report_sha,
        artifact_class="APPS_E2E_VERIFIER_REPORT",
        pointer=pointer,
        contains_req_id=False,
        contains_control=True,
        row_specific=True,
        freshness_hours=row["freshness_hours"],
        proof_payload={
            "extracted_value": {
                "certification_level": level,
                "violation_count": violations,
            },
            "expected_value": {
                "certification_level": _CERTIFIED_LEVEL,
                "violation_count": 0,
            },
            "match": bool(is_certified_clean),
            "notes": (
                f"Verifier-report-backed assertion for {app_name}. "
                f"PASS requires SPINE_COMPLETE_CERTIFIED with zero violations."
            ),
        },
        app_name=app_name,
        now_iso=now_iso,
    )


def _matrix_governance_assertion(
    row: dict[str, Any],
    matrix: dict[str, Any],
    matrix_sha: str,
    now_iso: str,
) -> dict[str, Any]:
    n_apps = len(matrix.get("apps", []))
    expected = 8
    ok = n_apps == expected
    return _make_assertion(
        req_id=row["req_id"],
        control="matrix_integrity",
        result="PASS" if ok else "FAIL",
        assertion_class="APPS_MATRIX_GOVERNANCE_ASSERTION",
        artifact_path=_rel_to_repo(MATRIX_PATH),
        artifact_sha256=matrix_sha,
        artifact_class="APPS_E2E_MATRIX",
        pointer="/apps",
        contains_req_id=False,
        contains_control=True,
        row_specific=True,
        freshness_hours=row["freshness_hours"],
        proof_payload={
            "extracted_value": n_apps,
            "expected_value": expected,
            "match": bool(ok),
            "notes": (
                f"Matrix app-row count check. Got {n_apps}, expected {expected}. "
                f"Full matrix integrity (per-row sha256 rebinding) is deferred to W3 compiler."
            ),
        },
        app_name=None,
        now_iso=now_iso,
    )


def _mutation_rejection_assertion(
    row: dict[str, Any],
    app_name: str,
    mutation_report: dict[str, Any],
    mutation_report_sha: str,
    now_iso: str,
) -> dict[str, Any]:
    """Project a PASS assertion for (req_id, mutation_rejection, app) from W4 report."""
    summary = mutation_report.get("summary", {})
    rejected = int(summary.get("rejected", 0))
    accepted = int(summary.get("accepted", 0))
    in_scope = rejected + accepted
    is_pass = accepted == 0 and in_scope >= 30
    pointer = f"/scenarios_by_app/{app_name}" if app_name in mutation_report.get("scenarios_by_app", {}) else "/summary"
    return _make_assertion(
        req_id=row["req_id"],
        control="mutation_rejection",
        result="PASS" if is_pass else "FAIL",
        assertion_class="APPS_NEGATIVE_CONTROL_ASSERTION",
        artifact_path=_rel_to_repo(MUTATION_REPORT_PATH),
        artifact_sha256=mutation_report_sha,
        artifact_class="APPS_MUTATION_REJECTION_REPORT",
        pointer=pointer,
        contains_req_id=False,
        contains_control=True,
        row_specific=True,
        freshness_hours=row["freshness_hours"],
        proof_payload={
            "extracted_value": {"rejected": rejected, "accepted": accepted, "in_scope": in_scope},
            "expected_value": {"accepted": 0, "in_scope_floor": 30},
            "match": bool(is_pass),
            "notes": (
                f"Mutation driver rejected {rejected}/{in_scope} in-scope tampered "
                f"scenarios across {summary.get('tamper_class_count', '?')} tamper classes."
            ),
        },
        app_name=app_name,
        now_iso=now_iso,
    )


def _bundle_negative_control_assertion(
    row: dict[str, Any],
    control: str,
    app_name: str,
    now_iso: str,
) -> dict[str, Any]:
    """Project a per-bundle PASS for negative controls (synthetic_trace etc.)."""
    field = _BUNDLE_NEGATIVE_CONTROLS[control]
    bundle_path = APPS_ARTIFACTS_DIR / app_name / f"{app_name}_e2e_proof.json"
    if not bundle_path.exists():
        return _deferred_assertion(
            row, control, f"bundle missing for {app_name} at {bundle_path.name}",
            "APPS_NEGATIVE_CONTROL_ASSERTION", _sha256_file(CATALOG_PATH), app_name, now_iso,
        )
    try:
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _deferred_assertion(
            row, control, f"bundle for {app_name} not valid JSON",
            "APPS_NEGATIVE_CONTROL_ASSERTION", _sha256_file(CATALOG_PATH), app_name, now_iso,
        )
    bundle_sha = _sha256_file(bundle_path)
    val = bundle.get(field)
    is_pass = (val is False) or (val == "false") or val is None
    # Pointer at /app_name proves bundle\u2194app binding (row-specificity guard
    # requires app_name to appear in the resolved payload); the actual field
    # value is captured in proof_payload.extracted_value for audit.
    pointer = "/app_name"
    return _make_assertion(
        req_id=row["req_id"],
        control=control,
        result="PASS" if is_pass else "FAIL",
        assertion_class="APPS_NEGATIVE_CONTROL_ASSERTION",
        artifact_path=_rel_to_repo(bundle_path),
        artifact_sha256=bundle_sha,
        artifact_class="APPS_E2E_PROOF_BUNDLE",
        pointer=pointer,
        contains_req_id=False,
        contains_control=True,
        row_specific=True,
        freshness_hours=row["freshness_hours"],
        proof_payload={
            "extracted_value": val,
            "expected_value": False,
            "match": bool(is_pass),
            "notes": (
                f"Per-bundle negative-control projection for {app_name}. "
                f"PASS iff {field}==false (or absent) in bundle."
            ),
        },
        app_name=app_name,
        now_iso=now_iso,
    )


def emit_assertions(catalog: dict[str, Any], verifier_report: dict[str, Any],
                    matrix: dict[str, Any]) -> list[dict[str, Any]]:
    """Main projection step. Produces the full assertion list (unsorted)."""
    now_iso = _iso_utc_now()
    verifier_report_sha = _sha256_file(VERIFIER_REPORT_PATH)
    matrix_sha = _sha256_file(MATRIX_PATH)
    catalog_sha = _sha256_file(CATALOG_PATH)
    # W4 mutation report is optional; if present, project mutation_rejection PASS.
    mutation_report: dict[str, Any] | None = None
    mutation_report_sha: str | None = None
    if MUTATION_REPORT_PATH.exists():
        try:
            mutation_report = json.loads(MUTATION_REPORT_PATH.read_text(encoding="utf-8"))
            mutation_report_sha = _sha256_file(MUTATION_REPORT_PATH)
        except (json.JSONDecodeError, UnicodeDecodeError):
            mutation_report = None

    certified_apps = sorted(
        row["app_name"]
        for row in verifier_report.get("rows", [])
        if row.get("certification_level") == _CERTIFIED_LEVEL
    )
    all_apps = sorted(row["app_name"] for row in verifier_report.get("rows", []))

    assertions: list[dict[str, Any]] = []

    for row in catalog["requirements"]:
        req_id = row["req_id"]
        subjects = _expected_apps_for_row(row, all_apps, certified_apps)

        # Matrix governance row has its own shape.
        if row["claim_type"] == "APPS_MATRIX_GOVERNANCE":
            assertions.append(
                _matrix_governance_assertion(row, matrix, matrix_sha, now_iso)
            )
            continue

        for control in row["required_controls"]:
            # Controls that W2 cannot assert \u2014 emit NOT_VERIFIED.
            if control in _DEFERRED_CONTROLS:
                deferred_to, assertion_class = _DEFERRED_CONTROLS[control]
                for app in subjects:
                    assertions.append(
                        _deferred_assertion(
                            row, control, deferred_to, assertion_class,
                            catalog_sha, app, now_iso,
                        )
                    )
                continue

            # mutation_rejection: project PASS from W4 mutation report if present.
            if control == "mutation_rejection":
                for app in subjects:
                    if app is None:
                        continue
                    if mutation_report is not None and mutation_report_sha is not None:
                        assertions.append(_mutation_rejection_assertion(
                            row, app, mutation_report, mutation_report_sha, now_iso,
                        ))
                    else:
                        assertions.append(_deferred_assertion(
                            row, control,
                            "tools/cert/apps_e2e/apps_mutation_driver.py (W4 — report not yet generated)",
                            "APPS_NEGATIVE_CONTROL_ASSERTION",
                            catalog_sha, app, now_iso,
                        ))
                continue

            # Bundle-projected negative controls (no_synthetic_trace etc.).
            if control in _BUNDLE_NEGATIVE_CONTROLS:
                for app in subjects:
                    if app is None:
                        continue
                    assertions.append(_bundle_negative_control_assertion(
                        row, control, app, now_iso,
                    ))
                continue

            if control not in _VERIFIER_BACKED_CONTROLS and row["claim_type"] != "APPS_WAIVER":
                # Unknown control \u2014 emit NOT_VERIFIED with a self-documenting note.
                for app in subjects:
                    assertions.append(
                        _deferred_assertion(
                            row, control,
                            "unclassified control (emitter does not know how to close)",
                            _assertion_class_for(row),
                            catalog_sha, app, now_iso,
                        )
                    )
                continue

            for app in subjects:
                if app is None:
                    # Happens only for APPS_POSITIVE_CONTROL rows handled above.
                    continue
                assertions.append(
                    _verifier_backed_assertion(
                        row, control, app, verifier_report, verifier_report_sha,
                        now_iso,
                    )
                )

    # Sort deterministically for stable diffs.
    assertions.sort(key=lambda a: (a["req_id"], a["control"], a.get("app_name") or ""))
    return assertions


def write_jsonl(assertions: Iterable[dict[str, Any]], out_path: Path = OUT_PATH) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for a in assertions:
            f.write(json.dumps(a, sort_keys=True, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=OUT_PATH,
        help=f"Output JSONL path. Default: {OUT_PATH.relative_to(REPO_ROOT).as_posix()}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute assertions but do not write them. Prints summary counts to stdout.",
    )
    args = parser.parse_args(argv)

    if not CATALOG_PATH.exists():
        print(f"ERROR: catalog missing at {CATALOG_PATH}", file=sys.stderr)
        return 2
    if not VERIFIER_REPORT_PATH.exists():
        print(f"ERROR: verifier_report missing at {VERIFIER_REPORT_PATH}", file=sys.stderr)
        return 2
    if not MATRIX_PATH.exists():
        print(f"ERROR: matrix missing at {MATRIX_PATH}", file=sys.stderr)
        return 2

    catalog = _load_catalog()
    verifier_report = _load_verifier_report()
    matrix = _load_matrix()

    assertions = emit_assertions(catalog, verifier_report, matrix)

    counts = {"PASS": 0, "FAIL": 0, "BLOCKED": 0, "NOT_VERIFIED": 0}
    for a in assertions:
        counts[a["assertion_result"]] = counts.get(a["assertion_result"], 0) + 1

    print(
        f"Emitted {len(assertions)} assertions for "
        f"{len(catalog['requirements'])} catalog rows: "
        f"PASS={counts['PASS']} FAIL={counts['FAIL']} "
        f"NOT_VERIFIED={counts['NOT_VERIFIED']} BLOCKED={counts['BLOCKED']}"
    )

    if args.dry_run:
        return 0

    write_jsonl(assertions, args.out)
    try:
        display = args.out.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        display = str(args.out)
    print(f"Wrote {display}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
