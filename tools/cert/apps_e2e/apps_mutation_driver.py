"""W4 of plan apps-fort-knox-parity-c5d9a3 \u2014 Apps_e2e Mutation Rejection Driver.

Closes the hostile-reviewer gap: \"the W3 compiler rejects synthetic
hand-crafted bad assertions; prove it also rejects realistic tampering
of genuine apps_e2e evidence.\"

This driver:
  1. Picks real production artifacts under
     `artifacts/certification/apps_e2e/` (verifier_report, per-app proof
     bundles, matrix).
  2. Clones each into
     `artifacts/certification/apps_e2e/_mutation_sandbox/` (originals are
     read-only).
  3. Applies a typed mutation to the clone.
  4. Constructs a synthetic apps_e2e assertion that references the
     tampered clone and runs it through the W3 compiler's pure validator
     (`compile_apps_e2e_signoff.validate_assertion`); expects REJECTED.
  5. Emits a structured `apps_mutation_rejection_report.json` with
     per-tamper-class and per-app cross-indices, plus `summary` counts.

Exit code:
  0 \u2014 all scenarios rejected
  1 \u2014 one or more scenarios accepted (compiler validator escape)
  2 \u2014 fatal: source artifact missing, schema invalid, etc.

The W2 emitter projects from the mutation report into PASS assertions
for `mutation_rejection` (cross-cutting on certified apps), closing
APPS-REQ-018/019/020 mutation-rejection control.

The static negative controls (`no_synthetic_trace`, `no_mock_mode`,
`no_fixture_runtime_mode`) are projected by the W2 emitter directly
from each app's e2e_proof.json bundle (`synthetic_trace_detected`,
`mock_mode_detected`, `fixture_runtime_mode` boolean fields).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
APPS_E2E_DIR = REPO_ROOT / "artifacts" / "certification" / "apps_e2e"
SANDBOX_DIR = APPS_E2E_DIR / "_mutation_sandbox"
REPORT_PATH = APPS_E2E_DIR / "apps_mutation_rejection_report.json"

DRIVER_PATH_REL = "tools/cert/apps_e2e/apps_mutation_driver.py"
DRIVER_VERSION = "apps_mutation_driver-v1.0"

# Import the W3 compiler's validator so we use the EXACT same logic the
# real signoff path uses. No reimplementation here \u2014 that would be a
# trust-bypass.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import compile_apps_e2e_signoff as compiler_mod  # type: ignore  # noqa: E402


# =============================================================================
# Hash + helpers
# =============================================================================

def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


def _iso_stale(hours_back: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=hours_back)).strftime(
        "%Y-%m-%dT%H:%M:%S+00:00"
    )


def _aid(*parts: str) -> str:
    return "ASRT-" + hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:40]


def _clone(src: Path, label: str) -> Path:
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    dst = SANDBOX_DIR / f"{label}__{src.name}"
    shutil.copyfile(src, dst)
    return dst


def _rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return p.as_posix()


# =============================================================================
# Synthetic requirement + assertion builders (compiler-validator inputs)
# =============================================================================

def _make_req(
    *,
    req_id: str,
    claim_type: str,
    required_controls: list[str],
    allowed_verifier_commands: list[str],
    allowed_artifact_classes: list[str],
    owner_app: str | None = None,
    freshness_hours: int = 168,
) -> dict[str, Any]:
    return {
        "req_id": req_id,
        "title": f"Synthetic mutation harness for {req_id}",
        "claim_type": claim_type,
        "priority": "P0",
        "requirement_group": "MUTATION_HARNESS",
        "required_proof_depth": "STRICT_EVIDENCE",
        "acceptance_rule": "synthetic",
        "fail_closed_if_missing": True,
        "depends_on_req_ids": [],
        "is_final_hundred_percent_row": False,
        "is_positive_control": False,
        "required_controls": required_controls,
        "supplemental_controls": [],
        "owner_app": owner_app,
        "allowed_verifier_commands": allowed_verifier_commands,
        "allowed_artifact_classes": allowed_artifact_classes,
        "freshness_hours": freshness_hours,
    }


def _make_assertion(
    *,
    req_id: str,
    control: str,
    artifact_path: Path,
    artifact_sha256: str,
    artifact_class: str,
    pointer: str,
    app_name: str | None,
    salt: str,
    generated_by_command: str = "tools/cert/apps_e2e/emit_apps_evidence_assertions.py",
    assertion_class: str = "APPS_SPINE_CERTIFIED_ASSERTION",
    assertion_result: str = "PASS",
    row_specific: bool = True,
    contains_req_id: bool = False,
    contains_control: bool = True,
    freshness_hours: int = 168,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    return {
        "assertion_id": _aid(req_id, control, artifact_sha256, pointer, salt),
        "req_id": req_id,
        "control": control,
        "assertion_result": assertion_result,
        "assertion_class": assertion_class,
        "generated_by_command": generated_by_command,
        "verifier_exit_code": 0,
        "verifier_version": DRIVER_VERSION,
        "generated_at_utc": generated_at_utc or _iso_now(),
        "artifact_path": _rel(artifact_path),
        "artifact_sha256": artifact_sha256,
        "artifact_class": artifact_class,
        "artifact_payload_pointer": pointer,
        "artifact_contains_req_id": contains_req_id,
        "artifact_contains_control": contains_control,
        "row_specific": row_specific,
        "freshness_hours": freshness_hours,
        "proof_payload": {"match": True, "tamper_test": True},
        "app_name": app_name,
    }


def _validate(assertion: dict[str, Any], req: dict[str, Any]) -> tuple[bool, str]:
    """Run compiler's validator. Returns (accepted_as_PASS, reason)."""
    return compiler_mod.validate_assertion(assertion, req, {})


def _wrap_scenario(
    *,
    name: str,
    description: str,
    tamper_class: str,
    artifact_path: Path,
    artifact_sha: str,
    accepted: bool,
    reason: str,
    app_name: str | None,
) -> dict[str, Any]:
    return {
        "name": name,
        "description": description,
        "tamper_class": tamper_class,
        "expected_verdict": "REJECTED",
        "actual_verdict": "ACCEPTED" if accepted else "REJECTED",
        "compiler_reason": reason or "(no reason \u2014 accepted)",
        "artifact_path": _rel(artifact_path),
        "artifact_sha256": artifact_sha,
        "app_name": app_name,
        "passes_rejection": not accepted,
    }


# =============================================================================
# Source artifacts
# =============================================================================

def _get_source_artifacts() -> dict[str, Path]:
    """Pick concrete production artifacts to mutate."""
    sources: dict[str, Path] = {
        "verifier_report": APPS_E2E_DIR / "verifier_report.json",
        "matrix": APPS_E2E_DIR / "apps_e2e_matrix.json",
    }
    for app in (
        "apps_eval",
        "apps_rg",
        "apps_research",
        "apps_lic",
        "apps_exec",
        "apps_rfp",
        "apps_qna",
        "apps_underwriting_ai",
    ):
        bundle = APPS_E2E_DIR / app / f"{app}_e2e_proof.json"
        if bundle.exists():
            sources[f"bundle_{app}"] = bundle
    return sources


# =============================================================================
# Mutations \u2014 each returns a scenario dict
# =============================================================================

def mut_sha256_flip(key: str, src: Path, app_name: str | None) -> dict[str, Any]:
    """Clone, flip a payload byte, claim original sha."""
    dst = _clone(src, f"sha_flip_{key}")
    raw = dst.read_bytes()
    tampered = raw[:-2] + bytes([raw[-2] ^ 0x01]) + raw[-1:] if len(raw) >= 2 else b"x"
    dst.write_bytes(tampered)
    tampered_sha = _sha256_file(dst)
    original_sha = _sha256_file(src)
    req = _make_req(
        req_id="APPS-REQ-MUT-001",
        claim_type="APPS_SPINE_CERTIFIED",
        required_controls=["spine_emission"],
        allowed_verifier_commands=["tools/cert/apps_e2e/emit_apps_evidence_assertions.py"],
        allowed_artifact_classes=["APPS_E2E_VERIFIER_REPORT", "APPS_E2E_PROOF_BUNDLE", "APPS_E2E_MATRIX"],
        owner_app=app_name,
    )
    assertion = _make_assertion(
        req_id="APPS-REQ-MUT-001",
        control="spine_emission",
        artifact_path=dst,
        artifact_sha256=original_sha,  # CLAIM original; on-disk is tampered
        artifact_class=_artifact_class_for(src),
        pointer="/rows/0" if "verifier_report" in key else "/apps/0" if "matrix" in key else "/app_name",
        app_name=app_name,
        salt="sha_flip",
    )
    accepted, reason = _validate(assertion, req)
    return _wrap_scenario(
        name=f"sha256_flip__{key}",
        description=f"Tampered byte in artifact; assertion still claims original sha256 ({original_sha[:12]}); on-disk is ({tampered_sha[:12]}).",
        tamper_class="sha256_flip",
        artifact_path=dst,
        artifact_sha=tampered_sha,
        accepted=accepted,
        reason=reason,
        app_name=app_name,
    )


def mut_wrong_app_name(key: str, src: Path, app_name: str | None) -> dict[str, Any]:
    """Per-app row but assertion.app_name does not match owner_app."""
    if app_name is None:
        return _wrap_scenario(
            name=f"wrong_app_name__{key}",
            description="N/A (source has no app_name binding)",
            tamper_class="wrong_app_name",
            artifact_path=src,
            artifact_sha=_sha256_file(src),
            accepted=False,
            reason="not applicable; skipped",
            app_name=None,
        )
    dst = _clone(src, f"wrong_app_{key}")
    sha = _sha256_file(dst)
    req = _make_req(
        req_id="APPS-REQ-MUT-002",
        claim_type="APPS_SPINE_CERTIFIED",
        required_controls=["spine_emission"],
        allowed_verifier_commands=["tools/cert/apps_e2e/emit_apps_evidence_assertions.py"],
        allowed_artifact_classes=["APPS_E2E_VERIFIER_REPORT", "APPS_E2E_PROOF_BUNDLE", "APPS_E2E_MATRIX"],
        owner_app=app_name,  # row binds to this app
    )
    # Assertion claims a DIFFERENT app
    wrong_app = "apps_qna" if app_name != "apps_qna" else "apps_eval"
    assertion = _make_assertion(
        req_id="APPS-REQ-MUT-002",
        control="spine_emission",
        artifact_path=dst,
        artifact_sha256=sha,
        artifact_class=_artifact_class_for(src),
        pointer="/rows/0" if "verifier_report" in key else "/app_name",
        app_name=wrong_app,
        salt="wrong_app",
    )
    accepted, reason = _validate(assertion, req)
    return _wrap_scenario(
        name=f"wrong_app_name__{key}",
        description=f"Row owner_app={app_name} but assertion.app_name={wrong_app}.",
        tamper_class="wrong_app_name",
        artifact_path=dst,
        artifact_sha=sha,
        accepted=accepted,
        reason=reason,
        app_name=app_name,
    )


def mut_unapproved_verifier(key: str, src: Path, app_name: str | None) -> dict[str, Any]:
    dst = _clone(src, f"unapproved_{key}")
    sha = _sha256_file(dst)
    req = _make_req(
        req_id="APPS-REQ-MUT-003",
        claim_type="APPS_SPINE_CERTIFIED",
        required_controls=["spine_emission"],
        allowed_verifier_commands=["tools/cert/apps_e2e/emit_apps_evidence_assertions.py"],
        allowed_artifact_classes=["APPS_E2E_VERIFIER_REPORT", "APPS_E2E_PROOF_BUNDLE", "APPS_E2E_MATRIX"],
        owner_app=app_name,
    )
    assertion = _make_assertion(
        req_id="APPS-REQ-MUT-003",
        control="spine_emission",
        artifact_path=dst,
        artifact_sha256=sha,
        artifact_class=_artifact_class_for(src),
        pointer="/rows/0" if "verifier_report" in key else "/app_name",
        app_name=app_name,
        salt="unapproved",
        generated_by_command="tools/cert/apps_e2e/totally_evil_producer.py",
    )
    accepted, reason = _validate(assertion, req)
    return _wrap_scenario(
        name=f"unapproved_verifier__{key}",
        description="Assertion stamped with a generated_by_command not in allowed_verifier_commands.",
        tamper_class="unapproved_verifier",
        artifact_path=dst,
        artifact_sha=sha,
        accepted=accepted,
        reason=reason,
        app_name=app_name,
    )


def mut_wrong_artifact_class(key: str, src: Path, app_name: str | None) -> dict[str, Any]:
    dst = _clone(src, f"wrong_class_{key}")
    sha = _sha256_file(dst)
    req = _make_req(
        req_id="APPS-REQ-MUT-004",
        claim_type="APPS_SPINE_CERTIFIED",
        required_controls=["spine_emission"],
        allowed_verifier_commands=["tools/cert/apps_e2e/emit_apps_evidence_assertions.py"],
        allowed_artifact_classes=["APPS_E2E_VERIFIER_REPORT"],  # narrow
        owner_app=app_name,
    )
    assertion = _make_assertion(
        req_id="APPS-REQ-MUT-004",
        control="spine_emission",
        artifact_path=dst,
        artifact_sha256=sha,
        artifact_class="APPS_TOTALLY_FAKE_CLASS",  # not allowed
        pointer="/rows/0",
        app_name=app_name,
        salt="wrong_class",
    )
    accepted, reason = _validate(assertion, req)
    return _wrap_scenario(
        name=f"wrong_artifact_class__{key}",
        description="Assertion declares an artifact_class not on the row's allowlist.",
        tamper_class="wrong_artifact_class",
        artifact_path=dst,
        artifact_sha=sha,
        accepted=accepted,
        reason=reason,
        app_name=app_name,
    )


def mut_stale_timestamp(key: str, src: Path, app_name: str | None) -> dict[str, Any]:
    dst = _clone(src, f"stale_{key}")
    sha = _sha256_file(dst)
    req = _make_req(
        req_id="APPS-REQ-MUT-005",
        claim_type="APPS_SPINE_CERTIFIED",
        required_controls=["spine_emission"],
        allowed_verifier_commands=["tools/cert/apps_e2e/emit_apps_evidence_assertions.py"],
        allowed_artifact_classes=["APPS_E2E_VERIFIER_REPORT", "APPS_E2E_PROOF_BUNDLE", "APPS_E2E_MATRIX"],
        owner_app=app_name,
        freshness_hours=48,
    )
    assertion = _make_assertion(
        req_id="APPS-REQ-MUT-005",
        control="spine_emission",
        artifact_path=dst,
        artifact_sha256=sha,
        artifact_class=_artifact_class_for(src),
        pointer="/rows/0" if "verifier_report" in key else "/app_name",
        app_name=app_name,
        salt="stale",
        generated_at_utc=_iso_stale(720),  # 30 days
        freshness_hours=48,
    )
    accepted, reason = _validate(assertion, req)
    return _wrap_scenario(
        name=f"stale_timestamp__{key}",
        description="generated_at_utc is 30 days ago under a 48-hour freshness window.",
        tamper_class="stale_timestamp",
        artifact_path=dst,
        artifact_sha=sha,
        accepted=accepted,
        reason=reason,
        app_name=app_name,
    )


def mut_not_row_specific(key: str, src: Path, app_name: str | None) -> dict[str, Any]:
    dst = _clone(src, f"not_row_spec_{key}")
    sha = _sha256_file(dst)
    req = _make_req(
        req_id="APPS-REQ-MUT-006",
        claim_type="APPS_SPINE_CERTIFIED",
        required_controls=["spine_emission"],
        allowed_verifier_commands=["tools/cert/apps_e2e/emit_apps_evidence_assertions.py"],
        allowed_artifact_classes=["APPS_E2E_VERIFIER_REPORT", "APPS_E2E_PROOF_BUNDLE", "APPS_E2E_MATRIX"],
        owner_app=app_name,
    )
    assertion = _make_assertion(
        req_id="APPS-REQ-MUT-006",
        control="spine_emission",
        artifact_path=dst,
        artifact_sha256=sha,
        artifact_class=_artifact_class_for(src),
        pointer="/rows/0" if "verifier_report" in key else "/app_name",
        app_name=app_name,
        salt="not_row_spec",
        row_specific=False,
    )
    accepted, reason = _validate(assertion, req)
    return _wrap_scenario(
        name=f"not_row_specific__{key}",
        description="Assertion sets row_specific=False (broad claim).",
        tamper_class="not_row_specific",
        artifact_path=dst,
        artifact_sha=sha,
        accepted=accepted,
        reason=reason,
        app_name=app_name,
    )


def mut_fail_as_pass(key: str, src: Path, app_name: str | None) -> dict[str, Any]:
    dst = _clone(src, f"fail_pass_{key}")
    sha = _sha256_file(dst)
    req = _make_req(
        req_id="APPS-REQ-MUT-007",
        claim_type="APPS_SPINE_CERTIFIED",
        required_controls=["spine_emission"],
        allowed_verifier_commands=["tools/cert/apps_e2e/emit_apps_evidence_assertions.py"],
        allowed_artifact_classes=["APPS_E2E_VERIFIER_REPORT", "APPS_E2E_PROOF_BUNDLE", "APPS_E2E_MATRIX"],
        owner_app=app_name,
    )
    assertion = _make_assertion(
        req_id="APPS-REQ-MUT-007",
        control="spine_emission",
        artifact_path=dst,
        artifact_sha256=sha,
        artifact_class=_artifact_class_for(src),
        pointer="/rows/0" if "verifier_report" in key else "/app_name",
        app_name=app_name,
        salt="fail_pass",
        assertion_result="FAIL",
    )
    accepted, reason = _validate(assertion, req)
    return _wrap_scenario(
        name=f"fail_as_pass__{key}",
        description="assertion_result=FAIL but submitted as if it counts as PASS.",
        tamper_class="fail_as_pass",
        artifact_path=dst,
        artifact_sha=sha,
        accepted=accepted,
        reason=reason,
        app_name=app_name,
    )


def mut_inject_synthetic_trace(key: str, src: Path, app_name: str | None) -> dict[str, Any]:
    """Inject synthetic_trace_detected=true into a bundle clone, then claim PASS."""
    dst = _clone(src, f"synthetic_inject_{key}")
    try:
        d = json.loads(dst.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _wrap_scenario(
            name=f"inject_synthetic_trace__{key}",
            description="N/A (source not JSON)",
            tamper_class="inject_synthetic_trace",
            artifact_path=dst,
            artifact_sha=_sha256_file(dst),
            accepted=False,
            reason="not applicable",
            app_name=app_name,
        )
    # Inject. If source is a bundle, set the field; if verifier_report, inject into row.
    if isinstance(d, dict) and "synthetic_trace_detected" in d:
        d["synthetic_trace_detected"] = True
        pointer = "/synthetic_trace_detected"
    elif isinstance(d, dict) and "rows" in d and isinstance(d["rows"], list) and d["rows"]:
        d["rows"][0]["synthetic_trace_injected"] = True
        pointer = "/rows/0/synthetic_trace_injected"
    else:
        d["synthetic_trace_injected"] = True
        pointer = "/synthetic_trace_injected"
    dst.write_text(json.dumps(d, sort_keys=True), encoding="utf-8")
    new_sha = _sha256_file(dst)
    original_sha = _sha256_file(src)
    req = _make_req(
        req_id="APPS-REQ-MUT-008",
        claim_type="APPS_SPINE_CERTIFIED",
        required_controls=["spine_emission"],
        allowed_verifier_commands=["tools/cert/apps_e2e/emit_apps_evidence_assertions.py"],
        allowed_artifact_classes=["APPS_E2E_VERIFIER_REPORT", "APPS_E2E_PROOF_BUNDLE", "APPS_E2E_MATRIX"],
        owner_app=app_name,
    )
    # Claim ORIGINAL sha to compound the tamper
    assertion = _make_assertion(
        req_id="APPS-REQ-MUT-008",
        control="spine_emission",
        artifact_path=dst,
        artifact_sha256=original_sha,
        artifact_class=_artifact_class_for(src),
        pointer=pointer,
        app_name=app_name,
        salt="synthetic_inject",
    )
    accepted, reason = _validate(assertion, req)
    return _wrap_scenario(
        name=f"inject_synthetic_trace__{key}",
        description="Tampered bundle with synthetic_trace marker injected; assertion claims original sha and PASS.",
        tamper_class="inject_synthetic_trace",
        artifact_path=dst,
        artifact_sha=new_sha,
        accepted=accepted,
        reason=reason,
        app_name=app_name,
    )


def mut_inject_mock_mode(key: str, src: Path, app_name: str | None) -> dict[str, Any]:
    dst = _clone(src, f"mock_inject_{key}")
    try:
        d = json.loads(dst.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _wrap_scenario(
            name=f"inject_mock_mode__{key}",
            description="N/A (source not JSON)",
            tamper_class="inject_mock_mode",
            artifact_path=dst,
            artifact_sha=_sha256_file(dst),
            accepted=False,
            reason="not applicable",
            app_name=app_name,
        )
    if isinstance(d, dict) and "mock_mode_detected" in d:
        d["mock_mode_detected"] = True
        pointer = "/mock_mode_detected"
    else:
        d["mock_mode_injected"] = True
        pointer = "/mock_mode_injected"
    dst.write_text(json.dumps(d, sort_keys=True), encoding="utf-8")
    new_sha = _sha256_file(dst)
    original_sha = _sha256_file(src)
    req = _make_req(
        req_id="APPS-REQ-MUT-009",
        claim_type="APPS_SPINE_CERTIFIED",
        required_controls=["spine_emission"],
        allowed_verifier_commands=["tools/cert/apps_e2e/emit_apps_evidence_assertions.py"],
        allowed_artifact_classes=["APPS_E2E_VERIFIER_REPORT", "APPS_E2E_PROOF_BUNDLE", "APPS_E2E_MATRIX"],
        owner_app=app_name,
    )
    assertion = _make_assertion(
        req_id="APPS-REQ-MUT-009",
        control="spine_emission",
        artifact_path=dst,
        artifact_sha256=original_sha,
        artifact_class=_artifact_class_for(src),
        pointer=pointer,
        app_name=app_name,
        salt="mock_inject",
    )
    accepted, reason = _validate(assertion, req)
    return _wrap_scenario(
        name=f"inject_mock_mode__{key}",
        description="Tampered bundle with mock_mode flag flipped on; assertion claims original sha and PASS.",
        tamper_class="inject_mock_mode",
        artifact_path=dst,
        artifact_sha=new_sha,
        accepted=accepted,
        reason=reason,
        app_name=app_name,
    )


def mut_inject_fixture_runtime(key: str, src: Path, app_name: str | None) -> dict[str, Any]:
    dst = _clone(src, f"fixture_inject_{key}")
    try:
        d = json.loads(dst.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _wrap_scenario(
            name=f"inject_fixture_runtime__{key}",
            description="N/A (source not JSON)",
            tamper_class="inject_fixture_runtime",
            artifact_path=dst,
            artifact_sha=_sha256_file(dst),
            accepted=False,
            reason="not applicable",
            app_name=app_name,
        )
    if isinstance(d, dict) and "fixture_runtime_mode" in d:
        d["fixture_runtime_mode"] = True
        pointer = "/fixture_runtime_mode"
    else:
        d["fixture_runtime_injected"] = True
        pointer = "/fixture_runtime_injected"
    dst.write_text(json.dumps(d, sort_keys=True), encoding="utf-8")
    new_sha = _sha256_file(dst)
    original_sha = _sha256_file(src)
    req = _make_req(
        req_id="APPS-REQ-MUT-010",
        claim_type="APPS_SPINE_CERTIFIED",
        required_controls=["spine_emission"],
        allowed_verifier_commands=["tools/cert/apps_e2e/emit_apps_evidence_assertions.py"],
        allowed_artifact_classes=["APPS_E2E_VERIFIER_REPORT", "APPS_E2E_PROOF_BUNDLE", "APPS_E2E_MATRIX"],
        owner_app=app_name,
    )
    assertion = _make_assertion(
        req_id="APPS-REQ-MUT-010",
        control="spine_emission",
        artifact_path=dst,
        artifact_sha256=original_sha,
        artifact_class=_artifact_class_for(src),
        pointer=pointer,
        app_name=app_name,
        salt="fixture_inject",
    )
    accepted, reason = _validate(assertion, req)
    return _wrap_scenario(
        name=f"inject_fixture_runtime__{key}",
        description="Tampered bundle with fixture_runtime_mode flipped on; assertion claims original sha.",
        tamper_class="inject_fixture_runtime",
        artifact_path=dst,
        artifact_sha=new_sha,
        accepted=accepted,
        reason=reason,
        app_name=app_name,
    )


def mut_swap_certification_level(key: str, src: Path, app_name: str | None) -> dict[str, Any]:
    """Flip certification_level to NOT_CERTIFIED in clone; assertion still claims spine_emission control PASS."""
    dst = _clone(src, f"level_swap_{key}")
    try:
        d = json.loads(dst.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _wrap_scenario(
            name=f"swap_certification_level__{key}",
            description="N/A (source not JSON)",
            tamper_class="swap_certification_level",
            artifact_path=dst,
            artifact_sha=_sha256_file(dst),
            accepted=False,
            reason="not applicable",
            app_name=app_name,
        )
    # Mutate the level if present
    mutated = False
    if isinstance(d, dict) and d.get("certification_level"):
        d["certification_level"] = "NOT_CERTIFIED_TAMPERED"
        mutated = True
    elif isinstance(d, dict) and "rows" in d and isinstance(d["rows"], list) and d["rows"]:
        for row in d["rows"]:
            if "certification_level" in row:
                row["certification_level"] = "NOT_CERTIFIED_TAMPERED"
                mutated = True
                break
    if not mutated:
        return _wrap_scenario(
            name=f"swap_certification_level__{key}",
            description="N/A (source has no certification_level field)",
            tamper_class="swap_certification_level",
            artifact_path=dst,
            artifact_sha=_sha256_file(dst),
            accepted=False,
            reason="not applicable",
            app_name=app_name,
        )
    dst.write_text(json.dumps(d, sort_keys=True), encoding="utf-8")
    new_sha = _sha256_file(dst)
    original_sha = _sha256_file(src)
    req = _make_req(
        req_id="APPS-REQ-MUT-011",
        claim_type="APPS_SPINE_CERTIFIED",
        required_controls=["spine_emission"],
        allowed_verifier_commands=["tools/cert/apps_e2e/emit_apps_evidence_assertions.py"],
        allowed_artifact_classes=["APPS_E2E_VERIFIER_REPORT", "APPS_E2E_PROOF_BUNDLE", "APPS_E2E_MATRIX"],
        owner_app=app_name,
    )
    assertion = _make_assertion(
        req_id="APPS-REQ-MUT-011",
        control="spine_emission",
        artifact_path=dst,
        artifact_sha256=original_sha,  # claim original sha despite tamper
        artifact_class=_artifact_class_for(src),
        pointer="/rows/0" if "verifier_report" in key else "/certification_level",
        app_name=app_name,
        salt="level_swap",
    )
    accepted, reason = _validate(assertion, req)
    return _wrap_scenario(
        name=f"swap_certification_level__{key}",
        description="Tampered certification_level → NOT_CERTIFIED_TAMPERED; assertion claims original sha + PASS.",
        tamper_class="swap_certification_level",
        artifact_path=dst,
        artifact_sha=new_sha,
        accepted=accepted,
        reason=reason,
        app_name=app_name,
    )


# Map source artifact key to its artifact_class.
def _artifact_class_for(src: Path) -> str:
    if "verifier_report" in src.name:
        return "APPS_E2E_VERIFIER_REPORT"
    if "matrix" in src.name:
        return "APPS_E2E_MATRIX"
    return "APPS_E2E_PROOF_BUNDLE"


# =============================================================================
# Driver
# =============================================================================

_MUTATION_FUNCS = (
    mut_sha256_flip,
    mut_wrong_app_name,
    mut_unapproved_verifier,
    mut_wrong_artifact_class,
    mut_stale_timestamp,
    mut_not_row_specific,
    mut_fail_as_pass,
    mut_inject_synthetic_trace,
    mut_inject_mock_mode,
    mut_inject_fixture_runtime,
    mut_swap_certification_level,
)


def run_mutations() -> list[dict[str, Any]]:
    sources = _get_source_artifacts()
    if not sources:
        raise FileNotFoundError("no apps_e2e production artifacts found to mutate")

    # Reset sandbox.
    if SANDBOX_DIR.exists():
        shutil.rmtree(SANDBOX_DIR)
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

    scenarios: list[dict[str, Any]] = []
    for src_key, src_path in sources.items():
        # Map source to app_name (None for verifier_report and matrix).
        app_name: str | None = None
        if src_key.startswith("bundle_"):
            app_name = src_key[len("bundle_"):]
        for fn in _MUTATION_FUNCS:
            scenario = fn(src_key, src_path, app_name)
            scenarios.append(scenario)
    return scenarios


def build_report(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    by_class: dict[str, list[str]] = {}
    by_app: dict[str, list[str]] = {}
    for s in scenarios:
        by_class.setdefault(s["tamper_class"], []).append(s["name"])
        if s.get("app_name"):
            by_app.setdefault(s["app_name"], []).append(s["name"])
    skipped = sum(1 for s in scenarios if "not applicable" in (s["compiler_reason"] or ""))
    in_scope = [s for s in scenarios if "not applicable" not in (s["compiler_reason"] or "")]
    rejected = sum(1 for s in in_scope if s["passes_rejection"])
    accepted = sum(1 for s in in_scope if not s["passes_rejection"])
    return {
        "schema_version": "apps_mutation_rejection_report-v1",
        "driver_path": DRIVER_PATH_REL,
        "driver_version": DRIVER_VERSION,
        "generated_at_utc": _iso_now(),
        "scenarios": scenarios,
        "by_tamper_class": by_class,
        "scenarios_by_app": by_app,
        "summary": {
            "total": len(scenarios),
            "rejected": rejected,
            "accepted": accepted,
            "skipped_not_applicable": skipped,
            "rejection_rate": (
                round(rejected / max(1, len(scenarios) - skipped), 4)
            ),
            "tamper_class_count": len(by_class),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=REPORT_PATH)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--fail-on-accept", action="store_true",
                        help="Exit non-zero if any in-scope scenario was accepted (default: True).")
    args = parser.parse_args(argv)

    try:
        scenarios = run_mutations()
    except FileNotFoundError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 2
    report = build_report(scenarios)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    s = report["summary"]
    if not args.quiet:
        print(
            f"[apps_mutation_driver] {s['total']} scenarios; "
            f"rejected={s['rejected']} accepted={s['accepted']} "
            f"skipped={s['skipped_not_applicable']} "
            f"rate={s['rejection_rate']:.2%}"
        )
        print(f"  tamper classes: {s['tamper_class_count']}")
        print(f"  report:         {_rel(args.out)}")

    if s["accepted"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
