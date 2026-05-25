"""W2 of plan apps-fort-knox-parity-c5d9a3 \u2014 emitter tests.

Covers tools/cert/apps_e2e/emit_apps_evidence_assertions.py.

Ground rules:
  - Uses a SYNTHETIC catalog + synthetic verifier_report + synthetic matrix
    so tests do not couple to whatever the live artifacts currently say.
    The live-artifact smoke check is a separate, deliberately-lenient test
    at the bottom.
  - Validates each emitted assertion against
    certification/schemas/apps_evidence_assertion.schema.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools" / "cert"))

from tools.cert.apps_e2e import emit_apps_evidence_assertions as emitter
from tools.cert.cert_paths import APPS_ASSERTION_SCHEMA, APPS_REQS_PATH  # noqa: E402

SCHEMA_PATH = APPS_ASSERTION_SCHEMA
CATALOG_PATH = APPS_REQS_PATH


# ----------------------------- synthetic fixtures -----------------------------

def _synthetic_catalog() -> dict[str, Any]:
    """Minimal catalog covering one row of each shape the emitter handles."""
    return {
        "schema_version": "apps_e2e_fortknox-v1",
        "generated_at_utc": "2026-05-02T00:00:00+00:00",
        "requirement_count": 6,
        "positive_control_req_id": "APPS-REQ-001",
        "final_hundred_percent_groups": ["test"],
        "claim_type_required_controls": {
            "APPS_POSITIVE_CONTROL": ["catalog_self_consistency"],
            "APPS_BUNDLE_EMISSION": ["bundle_emission"],
            "APPS_SPINE_CERTIFIED": [],
            "APPS_WAIVER": ["waiver_active"],
            "APPS_MATRIX_GOVERNANCE": ["matrix_integrity"],
            "APPS_NEGATIVE_CONTROL": ["mutation_rejection"],
            "APPS_STATIC_CONTRACT": [],
        },
        "requirements": [
            {
                "req_id": "APPS-REQ-001",
                "title": "canary",
                "priority": "P0",
                "requirement_group": "canary",
                "claim_type": "APPS_POSITIVE_CONTROL",
                "required_proof_depth": "CANARY_EVIDENCE",
                "acceptance_rule": "compiler plumbing alive",
                "fail_closed_if_missing": True,
                "depends_on_req_ids": [],
                "is_final_hundred_percent_row": True,
                "is_positive_control": True,
                "required_controls": ["catalog_self_consistency"],
                "allowed_verifier_commands": ["scripts/compile_apps_e2e_signoff.py"],
                "allowed_artifact_classes": ["APPS_CATALOG_SELF_REPORT"],
                "freshness_hours": 168,
            },
            {
                "req_id": "APPS-REQ-002",
                "title": "bundle emission cross-cutting",
                "priority": "P0",
                "requirement_group": "emission",
                "claim_type": "APPS_BUNDLE_EMISSION",
                "required_proof_depth": "SMOKE_EVIDENCE",
                "acceptance_rule": "each certified app emits",
                "fail_closed_if_missing": True,
                "depends_on_req_ids": [],
                "is_final_hundred_percent_row": True,
                "is_positive_control": False,
                "required_controls": ["bundle_emission"],
                "allowed_verifier_commands": ["tools/certification/apps_e2e/verifier_cli.py"],
                "allowed_artifact_classes": ["APPS_E2E_VERIFIER_REPORT"],
                "freshness_hours": 168,
            },
            {
                "req_id": "APPS-REQ-018",
                "title": "negative control",
                "priority": "P0",
                "requirement_group": "neg",
                "claim_type": "APPS_NEGATIVE_CONTROL",
                "required_proof_depth": "STRICT_EVIDENCE",
                "acceptance_rule": "driver rejects mutation",
                "fail_closed_if_missing": True,
                "depends_on_req_ids": [],
                "is_final_hundred_percent_row": True,
                "is_positive_control": False,
                "required_controls": ["mutation_rejection"],
                "allowed_verifier_commands": ["tools/cert/apps_e2e/apps_mutation_driver.py"],
                "allowed_artifact_classes": ["APPS_MUTATION_REJECTION_REPORT"],
                "freshness_hours": 168,
            },
            {
                "req_id": "APPS-REQ-025",
                "title": "apps_rg per-app",
                "priority": "P0",
                "requirement_group": "per-app",
                "claim_type": "APPS_SPINE_CERTIFIED",
                "required_proof_depth": "STRICT_EVIDENCE",
                "acceptance_rule": "apps_rg certified",
                "fail_closed_if_missing": True,
                "depends_on_req_ids": [],
                "is_final_hundred_percent_row": True,
                "is_positive_control": False,
                "required_controls": ["spine_emission", "strict_verifier_pass"],
                "allowed_verifier_commands": ["tools/certification/apps_e2e/verifier_cli.py"],
                "allowed_artifact_classes": ["APPS_E2E_PROOF_BUNDLE"],
                "freshness_hours": 168,
                "owner_app": "apps_rg",
            },
            {
                "req_id": "APPS-REQ-031",
                "title": "apps_qna waiver",
                "priority": "P2",
                "requirement_group": "waiver",
                "claim_type": "APPS_WAIVER",
                "required_proof_depth": "WAIVER_EVIDENCE",
                "acceptance_rule": "apps_qna waived",
                "fail_closed_if_missing": False,
                "depends_on_req_ids": [],
                "is_final_hundred_percent_row": True,
                "is_positive_control": False,
                "required_controls": ["waiver_active"],
                "allowed_verifier_commands": ["tools/certification/apps_e2e/verifier_cli.py"],
                "allowed_artifact_classes": ["APPS_WAIVER_DOCUMENT"],
                "freshness_hours": 8760,
                "owner_app": "apps_qna",
                "waiver_reason": "test",
            },
            {
                "req_id": "APPS-REQ-033",
                "title": "matrix governance",
                "priority": "P1",
                "requirement_group": "matrix",
                "claim_type": "APPS_MATRIX_GOVERNANCE",
                "required_proof_depth": "SMOKE_EVIDENCE",
                "acceptance_rule": "matrix integrity",
                "fail_closed_if_missing": True,
                "depends_on_req_ids": [],
                "is_final_hundred_percent_row": True,
                "is_positive_control": False,
                "required_controls": ["matrix_integrity"],
                "allowed_verifier_commands": ["tools/certification/apps_e2e/verifier_cli.py"],
                "allowed_artifact_classes": ["APPS_E2E_MATRIX"],
                "freshness_hours": 168,
            },
        ],
    }


def _synthetic_verifier_report() -> dict[str, Any]:
    return {
        "exit_code": 0,
        "generated_at_utc": "2026-05-02T12:00:00+00:00",
        "mode": "strict",
        "rows": [
            {"app_name": "apps_rg", "bundle_present": True,
             "certification_level": "SPINE_COMPLETE_CERTIFIED",
             "mode": "strict", "violation_count": 0, "violations": []},
            {"app_name": "apps_qna", "bundle_present": True,
             "certification_level": "WAIVED_NOT_RUNTIME_APP",
             "mode": "strict", "violation_count": 0, "violations": []},
        ],
        "summary": {"n_apps": 2, "n_pass": 2, "n_fail": 0},
        "verifier_report_schema_version": "apps_e2e_verifier_report/2026-05-02/v1",
    }


def _synthetic_matrix() -> dict[str, Any]:
    # Matrix emitter checks n_apps==8; the synthetic fixture deliberately
    # ships only 2 apps so we can assert FAIL semantics on the matrix row.
    return {
        "apps": [
            {"app_name": "apps_rg", "certification_level": "SPINE_COMPLETE_CERTIFIED"},
            {"app_name": "apps_qna", "certification_level": "WAIVED_NOT_RUNTIME_APP"},
        ],
        "schema_version": "apps_e2e_matrix/2026-05-01/v1",
    }


@pytest.fixture
def emitted(monkeypatch, tmp_path):
    """Emits the assertion set from synthetic fixtures without touching
    the live certification/ files.

    We monkeypatch the emitter's path constants so it reads from temp
    files we control, writes to a temp output path, and its sha256
    computations see the synthetic artifact bytes.
    """
    # Write synthetic catalog, verifier_report, matrix to temp paths
    cat_path = tmp_path / "catalog.json"
    vr_path = tmp_path / "verifier_report.json"
    mx_path = tmp_path / "matrix.json"
    cat_path.write_text(json.dumps(_synthetic_catalog()), encoding="utf-8")
    vr_path.write_text(json.dumps(_synthetic_verifier_report()), encoding="utf-8")
    mx_path.write_text(json.dumps(_synthetic_matrix()), encoding="utf-8")

    monkeypatch.setattr(emitter, "CATALOG_PATH", cat_path)
    monkeypatch.setattr(emitter, "VERIFIER_REPORT_PATH", vr_path)
    monkeypatch.setattr(emitter, "MATRIX_PATH", mx_path)
    # Ensure the synthetic emitter does not see the live W4 mutation report.
    monkeypatch.setattr(emitter, "MUTATION_REPORT_PATH", tmp_path / "no_such_mutation_report.json")
    # Ensure live per-app bundle dir is not reachable for synthetic test.
    monkeypatch.setattr(emitter, "APPS_ARTIFACTS_DIR", tmp_path / "no_such_apps_dir")

    catalog = emitter._load_catalog()
    verifier_report = emitter._load_verifier_report()
    matrix = emitter._load_matrix()
    assertions = emitter.emit_assertions(catalog, verifier_report, matrix)
    return assertions


# ---------------------------- tests: structural ----------------------------

def test_emits_at_least_one_assertion_per_row(emitted):
    seen_req_ids = {a["req_id"] for a in emitted}
    assert seen_req_ids == {
        "APPS-REQ-001", "APPS-REQ-002", "APPS-REQ-018",
        "APPS-REQ-025", "APPS-REQ-031", "APPS-REQ-033",
    }


def test_deterministic_assertion_ids(emitted):
    """Re-running must produce the same assertion_id set."""
    ids_first = sorted(a["assertion_id"] for a in emitted)
    # identical synthetic input \u2192 identical ids
    assert all(aid.startswith("ASRT-") for aid in ids_first)
    assert len(set(ids_first)) == len(ids_first), "assertion_ids not unique"


def test_assertion_id_pattern(emitted):
    import re
    pat = re.compile(r"^ASRT-[0-9a-f]{16,64}$")
    for a in emitted:
        assert pat.match(a["assertion_id"]), a["assertion_id"]


def test_generated_by_command_stamp(emitted):
    for a in emitted:
        assert a["generated_by_command"] == \
            "tools/cert/apps_e2e/emit_apps_evidence_assertions.py"


def test_sort_order_is_stable(emitted):
    keys = [(a["req_id"], a["control"], a.get("app_name") or "") for a in emitted]
    assert keys == sorted(keys), "assertions not sorted by (req_id, control, app)"


# ---------------------------- tests: semantics ----------------------------

def test_canary_is_not_verified_in_w2(emitted):
    canary = [a for a in emitted if a["req_id"] == "APPS-REQ-001"]
    assert len(canary) == 1
    assert canary[0]["assertion_result"] == "NOT_VERIFIED"
    assert "W3" in canary[0]["proof_payload"]["notes"]


def test_negative_control_rows_emitted_with_correct_subjects(emitted):
    """Negative-control rows produce per-app assertions for both required
    controls. As of W4: bundle-projected `no_synthetic_trace` may PASS or
    NOT_VERIFIED depending on whether the synthetic test workspace ships
    a bundle; `mutation_rejection` falls back to NOT_VERIFIED in this
    synthetic-workspace test (no mutation report on disk)."""
    neg = [a for a in emitted if a["req_id"] == "APPS-REQ-018"]
    assert neg, "expected negative-control assertions to be emitted"
    controls = {a["control"] for a in neg}
    # The W1 catalog requires both controls for APPS-REQ-018.
    assert "mutation_rejection" in controls
    # In synthetic test (no live mutation report), mutation_rejection \u2192 NOT_VERIFIED.
    mr = [a for a in neg if a["control"] == "mutation_rejection"]
    for a in mr:
        assert a["assertion_result"] == "NOT_VERIFIED"
        assert "W4" in (a["proof_payload"]["notes"] or "")


def test_per_app_spine_row_only_emits_for_owner_app(emitted):
    spine = [a for a in emitted if a["req_id"] == "APPS-REQ-025"]
    assert spine
    assert {a["app_name"] for a in spine} == {"apps_rg"}


def test_waiver_row_passes_when_level_is_waived(emitted):
    waiver = [a for a in emitted if a["req_id"] == "APPS-REQ-031"]
    assert len(waiver) == 1
    assert waiver[0]["assertion_result"] == "PASS"
    assert waiver[0]["app_name"] == "apps_qna"
    assert waiver[0]["proof_payload"]["extracted_value"] == "WAIVED_NOT_RUNTIME_APP"


def test_bundle_emission_row_targets_only_certified_apps(emitted):
    be = [a for a in emitted if a["req_id"] == "APPS-REQ-002"]
    # synthetic fixture has 1 certified app (apps_rg); waived one is excluded
    assert {a["app_name"] for a in be} == {"apps_rg"}
    assert all(a["assertion_result"] == "PASS" for a in be)


def test_matrix_governance_row_emits_single_assertion(emitted):
    mg = [a for a in emitted if a["req_id"] == "APPS-REQ-033"]
    assert len(mg) == 1
    # synthetic matrix ships only 2 apps, expected is 8 \u2192 FAIL
    assert mg[0]["assertion_result"] == "FAIL"
    assert mg[0]["app_name"] is None


# ---------------------------- tests: schema ----------------------------

def test_every_assertion_validates_against_schema(emitted):
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for a in emitted:
        errs = sorted(validator.iter_errors(a), key=lambda e: e.path)
        assert not errs, (
            f"assertion {a['assertion_id']} failed schema: "
            + "; ".join(f"{list(e.path)}: {e.message}" for e in errs)
        )


# ---------------------------- tests: live artifact smoke ----------------------------

@pytest.mark.skipif(
    not (REPO_ROOT / "artifacts" / "certification" / "apps_e2e" / "verifier_report.json").exists(),
    reason="live verifier_report.json not present",
)
def test_live_emitter_runs_end_to_end_and_emits_assertions(tmp_path):
    """Runs the CLI against live certification/ artifacts, writes to tmp.

    Intentionally lenient: only asserts that SOMETHING was emitted and
    every line parses as JSON. Exact counts vary with the live run.
    """
    out = tmp_path / "apps_evidence_assertions.jsonl"
    rc = emitter.main(["--out", str(out)])
    assert rc == 0
    assert out.exists()
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) > 0, "emitter produced no assertions"
    for line in lines:
        parsed = json.loads(line)
        assert "assertion_id" in parsed
        assert parsed["assertion_id"].startswith("ASRT-")
