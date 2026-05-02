"""W3 of plan apps-fort-knox-parity-c5d9a3 \u2014 compiler tests.

Covers scripts/compile_apps_e2e_signoff.py. Uses synthetic fixtures so
tests do not couple to the live on-disk assertion set.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from scripts import compile_apps_e2e_signoff as compiler

REPO_ROOT = Path(__file__).resolve().parents[3]


# ----------------------------- synthetic helpers -----------------------------

def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _mini_catalog(with_canary: bool = True, duplicate_canary: bool = False) -> dict[str, Any]:
    """Minimal catalog: canary + 1 per-app row + 1 waiver."""
    reqs: list[dict[str, Any]] = []
    if with_canary:
        reqs.append(
            {
                "req_id": "APPS-REQ-001",
                "title": "canary",
                "priority": "P0",
                "requirement_group": "canary",
                "claim_type": "APPS_POSITIVE_CONTROL",
                "required_proof_depth": "CANARY_EVIDENCE",
                "acceptance_rule": "canary",
                "fail_closed_if_missing": True,
                "depends_on_req_ids": [],
                "is_final_hundred_percent_row": True,
                "is_positive_control": True,
                "required_controls": ["catalog_self_consistency"],
                "allowed_verifier_commands": ["scripts/compile_apps_e2e_signoff.py"],
                "allowed_artifact_classes": ["APPS_CATALOG_SELF_REPORT"],
                "freshness_hours": 168,
            }
        )
    if duplicate_canary:
        reqs.append({**reqs[0], "req_id": "APPS-REQ-002", "is_positive_control": True})
    reqs.append(
        {
            "req_id": "APPS-REQ-025",
            "title": "apps_rg per-app",
            "priority": "P0",
            "requirement_group": "per-app",
            "claim_type": "APPS_SPINE_CERTIFIED",
            "required_proof_depth": "STRICT_EVIDENCE",
            "acceptance_rule": "certified",
            "fail_closed_if_missing": True,
            "depends_on_req_ids": [],
            "is_final_hundred_percent_row": True,
            "is_positive_control": False,
            "required_controls": ["spine_emission"],
            "allowed_verifier_commands": [
                "tools/cert/apps_e2e/emit_apps_evidence_assertions.py"
            ],
            "allowed_artifact_classes": ["APPS_E2E_VERIFIER_REPORT"],
            "freshness_hours": 168,
            "owner_app": "apps_rg",
        }
    )
    reqs.append(
        {
            "req_id": "APPS-REQ-031",
            "title": "apps_qna waiver",
            "priority": "P2",
            "requirement_group": "waiver",
            "claim_type": "APPS_WAIVER",
            "required_proof_depth": "WAIVER_EVIDENCE",
            "acceptance_rule": "waived",
            "fail_closed_if_missing": False,
            "depends_on_req_ids": [],
            "is_final_hundred_percent_row": True,
            "is_positive_control": False,
            "required_controls": ["waiver_active"],
            "allowed_verifier_commands": [
                "tools/cert/apps_e2e/emit_apps_evidence_assertions.py"
            ],
            "allowed_artifact_classes": ["APPS_E2E_VERIFIER_REPORT"],
            "freshness_hours": 8760,
            "owner_app": "apps_qna",
            "waiver_reason": "test",
        }
    )
    claim_type_required_controls: dict[str, list[str]] = {
        "APPS_POSITIVE_CONTROL": ["catalog_self_consistency"],
        "APPS_SPINE_CERTIFIED": [],
        "APPS_WAIVER": ["waiver_active"],
    }
    return {
        "schema_version": "apps_e2e_fortknox-v1",
        "generated_at_utc": "2026-05-02T00:00:00+00:00",
        "requirement_count": len(reqs),
        "positive_control_req_id": "APPS-REQ-001",
        "final_hundred_percent_groups": ["test"],
        "claim_type_required_controls": claim_type_required_controls,
        "requirements": reqs,
    }


def _mini_verifier_report() -> dict[str, Any]:
    return {
        "exit_code": 0,
        "generated_at_utc": "2026-05-02T12:00:00+00:00",
        "mode": "strict",
        "rows": [
            {
                "app_name": "apps_rg",
                "bundle_present": True,
                "certification_level": "SPINE_COMPLETE_CERTIFIED",
                "mode": "strict",
                "violation_count": 0,
                "violations": [],
            },
            {
                "app_name": "apps_qna",
                "bundle_present": True,
                "certification_level": "WAIVED_NOT_RUNTIME_APP",
                "mode": "strict",
                "violation_count": 0,
                "violations": [],
            },
        ],
        "summary": {"n_apps": 2, "n_pass": 2, "n_fail": 0},
        "verifier_report_schema_version": "apps_e2e_verifier_report/2026-05-02/v1",
    }


def _make_assertion(
    req_id: str,
    control: str,
    artifact_path: str,
    artifact_sha: str,
    pointer: str,
    app_name: str | None,
    generated_by: str = "tools/cert/apps_e2e/emit_apps_evidence_assertions.py",
    assertion_class: str = "APPS_SPINE_CERTIFIED_ASSERTION",
    artifact_class: str = "APPS_E2E_VERIFIER_REPORT",
) -> dict[str, Any]:
    from datetime import datetime, timezone

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    h = hashlib.sha256(
        f"{req_id}|{control}|{artifact_sha}|{pointer}".encode("utf-8")
    ).hexdigest()
    return {
        "assertion_id": f"ASRT-{h[:40]}",
        "req_id": req_id,
        "control": control,
        "assertion_result": "PASS",
        "assertion_class": assertion_class,
        "generated_by_command": generated_by,
        "verifier_exit_code": 0,
        "verifier_version": "test-v1",
        "generated_at_utc": now_iso,
        "artifact_path": artifact_path,
        "artifact_sha256": artifact_sha,
        "artifact_class": artifact_class,
        "artifact_payload_pointer": pointer,
        "artifact_contains_req_id": False,
        "artifact_contains_control": True,
        "row_specific": True,
        "freshness_hours": 168,
        "proof_payload": {"match": True},
        "app_name": app_name,
    }


# --------------------------- catalog self-consistency ---------------------------

def test_canary_check_passes_on_valid_catalog():
    assert compiler.check_catalog_self_consistency(_mini_catalog()) == []


def test_canary_check_fails_on_duplicate_canary():
    cat = _mini_catalog(duplicate_canary=True)
    violations = compiler.check_catalog_self_consistency(cat)
    assert any("positive_control" in v for v in violations)


def test_canary_check_fails_on_no_canary():
    cat = _mini_catalog(with_canary=False)
    violations = compiler.check_catalog_self_consistency(cat)
    assert any("positive_control" in v for v in violations)


def test_canary_check_fails_on_dangling_depends_on():
    cat = _mini_catalog()
    cat["requirements"][1]["depends_on_req_ids"] = ["APPS-REQ-999"]
    violations = compiler.check_catalog_self_consistency(cat)
    assert any("APPS-REQ-999" in v for v in violations)


def test_canary_check_fails_on_self_dependency():
    cat = _mini_catalog()
    cat["requirements"][1]["depends_on_req_ids"] = ["APPS-REQ-025"]
    violations = compiler.check_catalog_self_consistency(cat)
    assert any("itself" in v for v in violations)


# --------------------------- end-to-end compile ---------------------------

@pytest.fixture
def workspace(tmp_path):
    """Materializes catalog + verifier_report + assertions.jsonl in tmp."""
    catalog = _mini_catalog()
    verifier_report = _mini_verifier_report()
    vr_path = tmp_path / "verifier_report.json"
    vr_path.write_text(json.dumps(verifier_report, sort_keys=True), encoding="utf-8")
    vr_sha = _sha256_file(vr_path)

    # Per-app spine assertion binds APPS-REQ-025 via app_name=apps_rg at /rows/0
    a_spine = _make_assertion(
        req_id="APPS-REQ-025",
        control="spine_emission",
        artifact_path=str(vr_path.relative_to(tmp_path.anchor)) if False else "test_vr.json",
        artifact_sha=vr_sha,
        pointer="/rows/0",
        app_name="apps_rg",
    )
    # Waiver assertion for apps_qna at /rows/1
    a_waiver = _make_assertion(
        req_id="APPS-REQ-031",
        control="waiver_active",
        artifact_path="test_vr.json",
        artifact_sha=vr_sha,
        pointer="/rows/1",
        app_name="apps_qna",
        assertion_class="APPS_WAIVER_ASSERTION",
    )

    # We need artifact_path to resolve relative to REPO_ROOT when the compiler
    # re-hashes. Easiest: monkeypatch REPO_ROOT to tmp_path for this test.
    cat_path = tmp_path / "catalog.json"
    cat_path.write_text(json.dumps(catalog, sort_keys=True), encoding="utf-8")
    # Place the verifier_report at the path the assertions reference.
    referenced = tmp_path / "test_vr.json"
    referenced.write_text(vr_path.read_text(encoding="utf-8"), encoding="utf-8")

    jsonl_path = tmp_path / "apps_evidence_assertions.jsonl"
    with jsonl_path.open("w", encoding="utf-8", newline="\n") as f:
        for a in (a_spine, a_waiver):
            f.write(json.dumps(a, sort_keys=True) + "\n")

    return {
        "catalog": cat_path,
        "jsonl": jsonl_path,
        "repo_root": tmp_path,
    }


def test_compile_report_produces_signed_off_rows(workspace, monkeypatch):
    monkeypatch.setattr(compiler, "REPO_ROOT", workspace["repo_root"])
    report = compiler.compile_report(workspace["catalog"], workspace["jsonl"])
    by_id = {r["req_id"]: r for r in report["rows"]}

    # Canary self-emitted by compiler \u2192 PASS
    assert by_id["APPS-REQ-001"]["computed_status"] == "SIGNED_OFF"
    # Per-app row \u2192 PASS
    assert by_id["APPS-REQ-025"]["computed_status"] == "SIGNED_OFF"
    # Waiver row \u2192 SIGNED_OFF_WITH_WAIVER (distinct status)
    assert by_id["APPS-REQ-031"]["computed_status"] == "SIGNED_OFF_WITH_WAIVER"


def test_compile_report_positive_control_status_pass(workspace, monkeypatch):
    monkeypatch.setattr(compiler, "REPO_ROOT", workspace["repo_root"])
    report = compiler.compile_report(workspace["catalog"], workspace["jsonl"])
    assert report["positive_control_status"] == "PASS"


def test_compile_report_trust_level_waivers(workspace, monkeypatch):
    monkeypatch.setattr(compiler, "REPO_ROOT", workspace["repo_root"])
    report = compiler.compile_report(workspace["catalog"], workspace["jsonl"])
    # Every row SIGNED_OFF or SIGNED_OFF_WITH_WAIVER \u2192 SIGNED_OFF_WITH_WAIVERS
    assert report["trust_level"] == "SIGNED_OFF_WITH_WAIVERS"


def test_compile_report_row_digest_is_stable(workspace, monkeypatch):
    monkeypatch.setattr(compiler, "REPO_ROOT", workspace["repo_root"])
    r1 = compiler.compile_report(workspace["catalog"], workspace["jsonl"])
    r2 = compiler.compile_report(workspace["catalog"], workspace["jsonl"])
    # evaluated_at_utc changes between runs, but row_digest must not
    d1 = {row["req_id"]: row["row_digest"] for row in r1["rows"]}
    d2 = {row["req_id"]: row["row_digest"] for row in r2["rows"]}
    assert d1 == d2


def test_compile_report_schema_valid(workspace, monkeypatch):
    jsonschema = pytest.importorskip("jsonschema")
    monkeypatch.setattr(compiler, "REPO_ROOT", workspace["repo_root"])
    report = compiler.compile_report(workspace["catalog"], workspace["jsonl"])
    schema = json.loads(compiler.REPORT_SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errs = sorted(validator.iter_errors(report), key=lambda e: list(e.path))
    assert not errs, "; ".join(e.message for e in errs[:3])


# --------------------------- producer allowlist ---------------------------

def test_compile_rejects_assertion_from_disallowed_command(workspace, monkeypatch):
    """An assertion stamped with a command NOT in allowed_verifier_commands
    must be treated as not-a-PASS by the validator."""
    monkeypatch.setattr(compiler, "REPO_ROOT", workspace["repo_root"])
    # Read assertions, rewrite the spine one with a bogus command
    lines = workspace["jsonl"].read_text(encoding="utf-8").splitlines()
    new_lines = []
    for line in lines:
        a = json.loads(line)
        if a["req_id"] == "APPS-REQ-025":
            a["generated_by_command"] = "tools/evil/fake_producer.py"
            # assertion_id must change because its inputs changed (re-derive)
            h = hashlib.sha256(
                f"{a['req_id']}|{a['control']}|{a['artifact_sha256']}|{a['artifact_payload_pointer']}".encode("utf-8")
            ).hexdigest()
            a["assertion_id"] = f"ASRT-{h[:40]}"
        new_lines.append(json.dumps(a, sort_keys=True))
    workspace["jsonl"].write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    report = compiler.compile_report(workspace["catalog"], workspace["jsonl"])
    by_id = {r["req_id"]: r for r in report["rows"]}
    assert by_id["APPS-REQ-025"]["computed_status"] == "BLOCKED"
    assert "allowed_verifier_commands" in (by_id["APPS-REQ-025"]["blocking_gap"] or "")


# --------------------------- merkle ---------------------------

def test_merkle_stable_across_runs(workspace, monkeypatch):
    monkeypatch.setattr(compiler, "REPO_ROOT", workspace["repo_root"])
    r1 = compiler.compile_report(workspace["catalog"], workspace["jsonl"])
    r2 = compiler.compile_report(workspace["catalog"], workspace["jsonl"])
    assert compiler.build_merkle(r1["rows"])["root"] == compiler.build_merkle(r2["rows"])["root"]


def test_merkle_changes_when_row_changes(workspace, monkeypatch):
    monkeypatch.setattr(compiler, "REPO_ROOT", workspace["repo_root"])
    r1 = compiler.compile_report(workspace["catalog"], workspace["jsonl"])
    root1 = compiler.build_merkle(r1["rows"])["root"]
    # Break the workspace: remove the spine assertion
    lines = workspace["jsonl"].read_text(encoding="utf-8").splitlines()
    keep = [line for line in lines if '"APPS-REQ-025"' not in line]
    workspace["jsonl"].write_text("\n".join(keep) + "\n", encoding="utf-8")
    r2 = compiler.compile_report(workspace["catalog"], workspace["jsonl"])
    root2 = compiler.build_merkle(r2["rows"])["root"]
    assert root1 != root2


# --------------------------- live artifact smoke ---------------------------

@pytest.mark.skipif(
    not (REPO_ROOT / "certification" / "apps_evidence_assertions.jsonl").exists(),
    reason="live apps_evidence_assertions.jsonl not present",
)
def test_live_compile_canary_passes():
    """Runs the compiler against the live W1+W2 artifacts. Expects canary PASS."""
    report = compiler.compile_report()
    assert report["positive_control_status"] == "PASS"
    # With negative-control rows (018, 019, 020) still blocked pre-W4, expect
    # at least the non-neg-control count to be SIGNED_OFF.
    assert report["summary"]["signed_off"] >= 25
