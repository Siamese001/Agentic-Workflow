"""Fort Knox v2 — Core compiler and data-integrity tests.

These tests do NOT tamper with the bundle. They assert that the compiler
and its inputs obey the Fort Knox invariants in their normal state.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPILER = REPO_ROOT / "scripts" / "compile_requirement_signoff.py"
BUNDLE_VERIFIER = REPO_ROOT / "scripts" / "verify_final_requirement_signoff_bundle.py"
EMITTER = REPO_ROOT / "tools" / "cert" / "emit_evidence_assertions.py"
REQS_PATH = REPO_ROOT / "certification" / "requirements_source.json"
ASSERTIONS_PATH = REPO_ROOT / "certification" / "evidence_assertions.jsonl"
OUTPUT_DIR = REPO_ROOT / "artifacts" / "certification"
REPORT_PATH = OUTPUT_DIR / "final_requirement_signoff_report.json"
MERKLE_PATH = OUTPUT_DIR / "final_requirement_signoff_report.merkle.json"
SHA256_PATH = OUTPUT_DIR / "final_requirement_signoff_report.sha256"
SIG_PATH = OUTPUT_DIR / "final_requirement_signoff_report.signature.json"

REQS_SCHEMA = REPO_ROOT / "certification" / "schemas" / "requirements_source.schema.json"
ASSERTION_SCHEMA = REPO_ROOT / "certification" / "schemas" / "evidence_assertion.schema.json"
REPORT_SCHEMA = REPO_ROOT / "certification" / "schemas" / "final_requirement_signoff_report.schema.json"


@pytest.fixture(scope="module", autouse=True)
def compile_once():
    """Compile once at module load so every test sees a fresh report."""
    r = subprocess.run([sys.executable, str(COMPILER)],
                       cwd=REPO_ROOT, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"compiler failed: {r.stderr}"
    yield


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Schema validity
# ---------------------------------------------------------------------------

def test_requirements_source_schema_valid():
    v = Draft202012Validator(_load(REQS_SCHEMA))
    errs = list(v.iter_errors(_load(REQS_PATH)))
    assert not errs, f"requirements_source schema violations: {[e.message for e in errs[:3]]}"


def test_final_report_schema_valid():
    v = Draft202012Validator(_load(REPORT_SCHEMA))
    errs = list(v.iter_errors(_load(REPORT_PATH)))
    assert not errs, f"report schema violations: {[e.message for e in errs[:3]]}"


def test_every_assertion_schema_valid():
    v = Draft202012Validator(_load(ASSERTION_SCHEMA))
    with ASSERTIONS_PATH.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            errs = list(v.iter_errors(obj))
            assert not errs, f"line {lineno}: {[e.message for e in errs[:2]]}"


# ---------------------------------------------------------------------------
# Uniqueness
# ---------------------------------------------------------------------------

def test_no_duplicate_req_ids():
    reqs = _load(REQS_PATH)["requirements"]
    ids = [r["req_id"] for r in reqs]
    assert len(ids) == len(set(ids)), "duplicate req_id in requirements_source.json"


def test_no_duplicate_assertion_ids():
    aids = []
    with ASSERTIONS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                aids.append(json.loads(line)["assertion_id"])
    assert len(aids) == len(set(aids)), "duplicate assertion_id in evidence_assertions.jsonl"


# ---------------------------------------------------------------------------
# Report structure
# ---------------------------------------------------------------------------

def test_report_rows_exactly_match_source_req_ids():
    src_ids = {r["req_id"] for r in _load(REQS_PATH)["requirements"]}
    rpt_ids = {r["req_id"] for r in _load(REPORT_PATH)["rows"]}
    assert src_ids == rpt_ids, f"drift: extra={rpt_ids - src_ids}, missing={src_ids - rpt_ids}"


def test_report_sha256_matches_sidecar():
    h = hashlib.sha256()
    with REPORT_PATH.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    actual = h.hexdigest()
    sidecar = SHA256_PATH.read_text(encoding="utf-8").split()[0]
    assert actual == sidecar, f"sha256 drift: disk={actual[:12]} sidecar={sidecar[:12]}"


def test_signed_off_rows_have_no_blocking_gap():
    for row in _load(REPORT_PATH)["rows"]:
        if row["computed_status"] == "SIGNED_OFF":
            assert row.get("blocking_gap") in (None, ""), (
                f"{row['req_id']} SIGNED_OFF but has blocking_gap={row.get('blocking_gap')!r}"
            )


def test_blocked_rows_have_blocking_gap():
    for row in _load(REPORT_PATH)["rows"]:
        if row["computed_status"] in ("BLOCKED", "NOT_VERIFIED"):
            assert row.get("blocking_gap"), (
                f"{row['req_id']} status={row['computed_status']} but blocking_gap is empty"
            )


def test_signed_off_rows_have_all_controls_passed():
    for row in _load(REPORT_PATH)["rows"]:
        if row["computed_status"] == "SIGNED_OFF":
            failed = [c for c in row["controls"] if not c["passed"]]
            assert not failed, (
                f"{row['req_id']} SIGNED_OFF but controls failing: {[c['name'] for c in failed]}"
            )


def test_every_signed_off_control_has_assertion_id():
    for row in _load(REPORT_PATH)["rows"]:
        if row["computed_status"] != "SIGNED_OFF":
            continue
        for c in row["controls"]:
            if not c["passed"]:
                continue
            # Allow None if the req declared the control as artifactless
            # (but require at least one of assertion_id, reason='artifactless')
            if c["assertion_id"] is None:
                assert "artifactless" in (c.get("reason") or "").lower(), (
                    f"{row['req_id']}.{c['name']} PASS with no assertion_id and no artifactless reason"
                )


def test_final_hundred_percent_rows_gated_by_non_finals():
    report = _load(REPORT_PATH)
    open_non_final = [r for r in report["rows"]
                      if not r["is_final_hundred_percent_row"]
                      and r["computed_status"] != "SIGNED_OFF"]
    signed_finals = [r for r in report["rows"]
                     if r["is_final_hundred_percent_row"]
                     and r["computed_status"] == "SIGNED_OFF"]
    if open_non_final:
        assert not signed_finals, (
            f"final-100% rows {[r['req_id'] for r in signed_finals]} SIGNED_OFF "
            f"while {len(open_non_final)} non-final open"
        )


# ---------------------------------------------------------------------------
# Trust level gating
# ---------------------------------------------------------------------------

def test_trust_level_gated_by_signature_and_signoff():
    report = _load(REPORT_PATH)
    sig = _load(SIG_PATH)
    s = report["summary"]
    tl = report["trust_level"]
    all_signed = (s["signed_off"] == s["total"] and s["total"] > 0)
    sig_verified = sig.get("signature_verification_status") == "VERIFIED"
    if tl == "FINAL_SIGNED_CERTIFICATION":
        assert all_signed, "FINAL_SIGNED_CERTIFICATION but not all rows SIGNED_OFF"
        assert sig_verified, "FINAL_SIGNED_CERTIFICATION but signature not VERIFIED"
    if not all_signed:
        assert tl == "DEVELOPMENT_PROOF", (
            f"trust_level={tl} but rows open: {s['blocked'] + s['not_verified']}"
        )


# ---------------------------------------------------------------------------
# Compiler hostility — cannot trust spreadsheets
# ---------------------------------------------------------------------------

def test_compiler_source_does_not_import_openpyxl():
    src = COMPILER.read_text(encoding="utf-8")
    assert "import openpyxl" not in src, "compiler must not depend on XLSX"
    assert "FULL_OVERWRITE.xlsx" not in src
    # Compiler also must not read the legacy user XLSX path
    assert "Downloads" not in src


def test_compiler_requires_atomic_assertions_not_manifest():
    """Compiler must consume evidence_assertions.jsonl, not evidence_manifest.jsonl.
    Functional rejection of linked_req_ids-only artifacts is covered by M07."""
    src = COMPILER.read_text(encoding="utf-8")
    assert "evidence_assertions.jsonl" in src
    # Must NOT open the legacy manifest file as an input
    assert 'evidence_manifest.jsonl"' not in src and "evidence_manifest.jsonl'" not in src
