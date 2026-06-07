#!/usr/bin/env python3
"""
test_pre_write_gate_core_guard.py — W3.P2 unit tests for Core Addition Author-Gate.

Tests check_core_addition_receipt() in isolation by patching the module-level
constants (repo_root, session_state, _SCHEMA_PATH, _VIOLATIONS_LOG) so no real
filesystem state is required.

Plan: core-addition-author-gate-governance-f3b9e2, W3.P2
"""

import importlib
import json
import os
import sys
import pathlib
import tempfile
import textwrap

import pytest

# ---------------------------------------------------------------------------
# Helpers to build fixture data
# ---------------------------------------------------------------------------

_PLAN_ID = "core-addition-author-gate-governance-f3b9e2"
_TARGET_PATH = "c:/Git/Agentic-Workflow-FRESH/agentic_core/L0_routing/new_module.py"
_COVERED_PATH = "agentic_core/L0_routing/new_module.py"


def _make_session_state(
    *,
    plan_id: str = _PLAN_ID,
    plan_type: str = "platform_core_change",
    touches_core: bool = True,
    gate_required: bool = True,
    receipt_ref: str = "artifacts/governance/receipt.json",
) -> dict:
    return {
        "current_tier": "T2",
        "task_created": True,
        "task_started": True,
        "active_plan": {
            "plan_id": plan_id,
            "plan_type": plan_type,
            "touches_agentic_core": touches_core,
            "core_addition_author_gate_required": gate_required,
            "author_gate_receipt_ref": receipt_ref,
        },
    }


def _make_receipt(
    *,
    plan_id: str = _PLAN_ID,
    plan_type: str = "platform_core_change",
    changed_paths: list[str] | None = None,
    verdict: str = "PASS",
    digest: str = "sha256:abc123",
) -> dict:
    if changed_paths is None:
        changed_paths = [_COVERED_PATH]
    return {
        "receipt_type": "CoreAdditionAuthorGateReceipt",
        "plan_id": plan_id,
        "plan_type": plan_type,
        "changed_paths": changed_paths,
        "decision": {
            "verdict": verdict,
            "rationale": "All checks pass.",
            "decided_at": "2026-05-12T06:00:00Z",
        },
        "tests": {
            "spine_substrate_test":             {"result": "PASS", "evidence": "ok"},
            "any_app_capability_test":          {"result": "PASS", "evidence": "ok"},
            "app_owned_meaning_test":           {"result": "PASS", "evidence": "ok"},
            "no_app_literal_test":              {"result": "PASS", "evidence": "ok"},
            "plugin_test":                      {"result": "PASS", "evidence": "ok"},
            "negative_control_test":            {"result": "PASS", "evidence": "ok"},
            "platform_approval_test":           {"result": "PASS", "evidence": "ok"},
            "boundary_preservation_test":       {"result": "PASS", "evidence": "ok"},
            "contract_compatibility_test":      {"result": "PASS", "evidence": "ok"},
            "runtime_proof_compatibility_test": {"result": "PASS", "evidence": "ok"},
        },
        "artifacts": {
            "no_app_literal_scan_ref": {
                "path": "artifacts/governance/no_app_literal_scan.json",
                "digest": "sha256:a1",
                "verdict": "PASS",
                "plan_id": plan_id,
                "freshness_ts": "2026-05-12T06:00:00Z",
                "changed_paths_covered": changed_paths,
            },
            "strict_scan_ref": {
                "path": "artifacts/governance/strict_scan.json",
                "digest": "sha256:a2",
                "verdict": "PASS",
                "plan_id": plan_id,
                "freshness_ts": "2026-05-12T06:00:00Z",
                "changed_paths_covered": changed_paths,
            },
            "negative_control_results_ref": {
                "path": "artifacts/governance/negative_controls.json",
                "digest": "sha256:a3",
                "verdict": "PASS",
                "plan_id": plan_id,
                "freshness_ts": "2026-05-12T06:00:00Z",
                "changed_paths_covered": changed_paths,
            },
            "plugin_proof_ref": {
                "path": "artifacts/governance/plugin_proof.json",
                "digest": "sha256:a4",
                "verdict": "PASS",
                "plan_id": plan_id,
                "freshness_ts": "2026-05-12T06:00:00Z",
                "changed_paths_covered": changed_paths,
            },
            "boundary_scan_ref": {
                "path": "artifacts/governance/boundary_scan.json",
                "digest": "sha256:a5",
                "verdict": "PASS",
                "plan_id": plan_id,
                "freshness_ts": "2026-05-12T06:00:00Z",
                "changed_paths_covered": changed_paths,
            },
            "contract_schema_scan_ref": {
                "path": "artifacts/governance/contract_schema_scan.json",
                "digest": "sha256:a6",
                "verdict": "PASS",
                "plan_id": plan_id,
                "freshness_ts": "2026-05-12T06:00:00Z",
                "changed_paths_covered": changed_paths,
            },
        },
        "signature": {"receipt_digest": digest},
    }


# ---------------------------------------------------------------------------
# Fixture: patch module-level paths so tests are hermetic
# ---------------------------------------------------------------------------

@pytest.fixture()
def gate(tmp_path, monkeypatch):
    """
    Import pre_write_gate fresh and patch its path constants to tmp_path
    so no real session_state / receipt files are touched.
    """
    # Ensure the module is freshly imported each test (avoids state bleed)
    scripts_dir = str(
        pathlib.Path(__file__).resolve().parents[3] / ".claude" / "governance/scripts" / "_legacy_windsurf"
    )
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    # Remove cached module to ensure clean import
    for key in list(sys.modules.keys()):
        if "pre_write_gate" in key:
            del sys.modules[key]

    import pre_write_gate as pwg

    # Patch paths to tmp_path
    fake_state = tmp_path / "session_state.json"
    fake_violations = tmp_path / "violations.jsonl"
    schema_path = (
        pathlib.Path(__file__).resolve().parents[3]
        / ".claude" / "schemas" / "CoreAdditionAuthorGateReceipt.schema.json"
    )

    monkeypatch.setattr(pwg, "session_state", fake_state)
    monkeypatch.setattr(pwg, "_VIOLATIONS_LOG", fake_violations)
    monkeypatch.setattr(pwg, "repo_root", tmp_path)
    monkeypatch.setattr(pwg, "_SCHEMA_PATH", schema_path)

    # Ensure bypass env var is unset by default
    monkeypatch.delenv("CORE_ADDITION_GATE_BYPASS", raising=False)

    return pwg, tmp_path, fake_state, fake_violations


def _write_state(fake_state, state_dict):
    fake_state.write_text(json.dumps(state_dict), encoding="utf-8")


def _write_receipt(tmp_path, receipt_dict, filename="receipt.json"):
    receipt_file = tmp_path / filename
    receipt_file.write_text(json.dumps(receipt_dict), encoding="utf-8")
    return str(receipt_file)


# ---------------------------------------------------------------------------
# Test 1: non-core write skips check
# ---------------------------------------------------------------------------

def test_non_core_write_skips_check(gate):
    pwg, tmp_path, fake_state, _ = gate
    # No session_state written — would block if core check ran
    result = pwg.check_core_addition_receipt(
        "apps_rg/some_module.py", "some content"
    )
    assert result is None


def test_non_core_write_skips_check_generic_py(gate):
    pwg, tmp_path, fake_state, _ = gate
    result = pwg.check_core_addition_receipt(
        "tools/analysis/foo.py", "print('hello')"
    )
    assert result is None


# ---------------------------------------------------------------------------
# Test 2: core write without active plan metadata blocks
# ---------------------------------------------------------------------------

def test_core_write_no_session_state_blocks(gate):
    pwg, tmp_path, fake_state, _ = gate
    # fake_state does not exist
    result = pwg.check_core_addition_receipt(_TARGET_PATH, "")
    assert result is not None
    assert "blocked" in result


def test_core_write_no_active_plan_key_blocks(gate):
    pwg, tmp_path, fake_state, _ = gate
    _write_state(fake_state, {"current_tier": "T2"})
    result = pwg.check_core_addition_receipt(_TARGET_PATH, "")
    assert result is not None
    assert "plan_id" in result


# ---------------------------------------------------------------------------
# Test 3: core write with plan_type != platform_core_change blocks
# ---------------------------------------------------------------------------

def test_wrong_plan_type_blocks(gate):
    pwg, tmp_path, fake_state, _ = gate
    state = _make_session_state(plan_type="refactor")
    _write_state(fake_state, state)
    result = pwg.check_core_addition_receipt(_TARGET_PATH, "")
    assert result is not None
    assert "platform_core_change" in result


# ---------------------------------------------------------------------------
# Test 4: core write with touches_agentic_core=false blocks
# ---------------------------------------------------------------------------

def test_touches_core_false_blocks(gate):
    pwg, tmp_path, fake_state, _ = gate
    state = _make_session_state(touches_core=False)
    _write_state(fake_state, state)
    result = pwg.check_core_addition_receipt(_TARGET_PATH, "")
    assert result is not None
    assert "touches_agentic_core" in result


# ---------------------------------------------------------------------------
# Test 5: core write with missing author_gate_receipt_ref blocks
# ---------------------------------------------------------------------------

def test_missing_receipt_ref_blocks(gate):
    pwg, tmp_path, fake_state, _ = gate
    state = _make_session_state(receipt_ref="")
    _write_state(fake_state, state)
    result = pwg.check_core_addition_receipt(_TARGET_PATH, "")
    assert result is not None
    assert "author_gate_receipt_ref" in result


# ---------------------------------------------------------------------------
# Test 6: missing receipt file blocks
# ---------------------------------------------------------------------------

def test_missing_receipt_file_blocks(gate):
    pwg, tmp_path, fake_state, _ = gate
    state = _make_session_state(receipt_ref="nonexistent/receipt.json")
    _write_state(fake_state, state)
    result = pwg.check_core_addition_receipt(_TARGET_PATH, "")
    assert result is not None
    assert "cannot read receipt file" in result


# ---------------------------------------------------------------------------
# Test 7: malformed receipt JSON blocks
# ---------------------------------------------------------------------------

def test_malformed_receipt_json_blocks(gate):
    pwg, tmp_path, fake_state, _ = gate
    bad_receipt = tmp_path / "bad.json"
    bad_receipt.write_text("{not valid json", encoding="utf-8")
    state = _make_session_state(receipt_ref=str(bad_receipt))
    _write_state(fake_state, state)
    result = pwg.check_core_addition_receipt(_TARGET_PATH, "")
    assert result is not None
    assert "malformed receipt JSON" in result


# ---------------------------------------------------------------------------
# Test 8: receipt schema validation failure blocks
# ---------------------------------------------------------------------------

def test_receipt_schema_validation_failure_blocks(gate):
    pwg, tmp_path, fake_state, _ = gate
    # Missing required fields — will fail schema
    bad_receipt = {"receipt_type": "CoreAdditionAuthorGateReceipt"}
    receipt_path = _write_receipt(tmp_path, bad_receipt)
    state = _make_session_state(receipt_ref=receipt_path)
    _write_state(fake_state, state)
    result = pwg.check_core_addition_receipt(_TARGET_PATH, "")
    assert result is not None
    assert "schema validation" in result


# ---------------------------------------------------------------------------
# Test 9: receipt plan_id mismatch blocks
# ---------------------------------------------------------------------------

def test_receipt_plan_id_mismatch_blocks(gate):
    pwg, tmp_path, fake_state, _ = gate
    receipt = _make_receipt(plan_id="different-plan-aabbcc")
    receipt_path = _write_receipt(tmp_path, receipt)
    state = _make_session_state(receipt_ref=receipt_path)
    _write_state(fake_state, state)
    result = pwg.check_core_addition_receipt(_TARGET_PATH, "")
    assert result is not None
    assert "plan_id" in result


# ---------------------------------------------------------------------------
# Test 10: receipt decision.verdict != PASS blocks
# ---------------------------------------------------------------------------

def test_receipt_verdict_fail_blocks(gate):
    pwg, tmp_path, fake_state, _ = gate
    receipt = _make_receipt(verdict="FAIL")
    receipt_path = _write_receipt(tmp_path, receipt)
    state = _make_session_state(receipt_ref=receipt_path)
    _write_state(fake_state, state)
    result = pwg.check_core_addition_receipt(_TARGET_PATH, "")
    assert result is not None
    assert "verdict" in result


# ---------------------------------------------------------------------------
# Test 11: attempted path not in receipt.changed_paths blocks
# ---------------------------------------------------------------------------

def test_path_not_in_changed_paths_blocks(gate):
    pwg, tmp_path, fake_state, _ = gate
    receipt = _make_receipt(changed_paths=["agentic_core/L1_cognition/other.py"])
    receipt_path = _write_receipt(tmp_path, receipt)
    state = _make_session_state(receipt_ref=receipt_path)
    _write_state(fake_state, state)
    result = pwg.check_core_addition_receipt(_TARGET_PATH, "")
    assert result is not None
    assert "changed_paths" in result


# ---------------------------------------------------------------------------
# Test 12: missing or malformed receipt_digest blocks
# ---------------------------------------------------------------------------

def test_missing_receipt_digest_blocks(gate):
    pwg, tmp_path, fake_state, _ = gate
    receipt = _make_receipt()
    del receipt["signature"]["receipt_digest"]
    receipt_path = _write_receipt(tmp_path, receipt)
    state = _make_session_state(receipt_ref=receipt_path)
    _write_state(fake_state, state)
    result = pwg.check_core_addition_receipt(_TARGET_PATH, "")
    assert result is not None
    # Schema rejects missing receipt_digest before semantic check
    assert result is not None


def test_malformed_receipt_digest_no_prefix_blocks(gate):
    pwg, tmp_path, fake_state, _ = gate
    receipt = _make_receipt(digest="abc123nohashprefix")
    receipt_path = _write_receipt(tmp_path, receipt)
    state = _make_session_state(receipt_ref=receipt_path)
    _write_state(fake_state, state)
    result = pwg.check_core_addition_receipt(_TARGET_PATH, "")
    assert result is not None
    assert "receipt_digest" in result


# ---------------------------------------------------------------------------
# Test 13: forbidden app literal in new_string blocks
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("literal", [
    "apps_rg",
    "apps_lic",
    "apps_research",
    "apps_qna",
    "resume_generator",
    "outreach",
    "company_brief",
    "interview_card",
    "recruiter",
])
def test_forbidden_app_literal_blocks(gate, literal):
    pwg, tmp_path, fake_state, _ = gate
    receipt = _make_receipt()
    receipt_path = _write_receipt(tmp_path, receipt)
    state = _make_session_state(receipt_ref=receipt_path)
    _write_state(fake_state, state)
    new_content = f"# some code\nMODULE = '{literal}'\n"
    result = pwg.check_core_addition_receipt(_TARGET_PATH, new_content)
    assert result is not None
    assert literal in result or "forbidden app literal" in result


# ---------------------------------------------------------------------------
# Test 14: valid receipt allows core write
# ---------------------------------------------------------------------------

def test_valid_receipt_allows_core_write(gate):
    pwg, tmp_path, fake_state, _ = gate
    receipt = _make_receipt()
    receipt_path = _write_receipt(tmp_path, receipt)
    state = _make_session_state(receipt_ref=receipt_path)
    _write_state(fake_state, state)
    result = pwg.check_core_addition_receipt(
        _TARGET_PATH,
        "# generic infrastructure code only\ndef _process(data): return data\n",
    )
    assert result is None


# ---------------------------------------------------------------------------
# Test 15: CORE_ADDITION_GATE_BYPASS=1 allows write and logs JSONL event
# ---------------------------------------------------------------------------

def test_bypass_allows_write_and_logs_event(gate, monkeypatch):
    pwg, tmp_path, fake_state, fake_violations = gate
    monkeypatch.setenv("CORE_ADDITION_GATE_BYPASS", "1")
    # No session_state — would normally block
    result = pwg.check_core_addition_receipt(_TARGET_PATH, "apps_rg_forbidden_literal")
    # Bypass must return None (allow write)
    assert result is None
    # Audit log must have been written
    assert fake_violations.exists(), "violations log must be created on bypass"
    lines = fake_violations.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    event = json.loads(lines[0])
    assert event["path"] == _TARGET_PATH
    assert event["bypassed"] is True
    assert "timestamp" in event
    assert "reason" in event
    assert event["CORE_ADDITION_GATE_BYPASS"] == "1"


def test_bypass_logs_even_for_forbidden_literal(gate, monkeypatch):
    pwg, tmp_path, fake_state, fake_violations = gate
    monkeypatch.setenv("CORE_ADDITION_GATE_BYPASS", "1")
    # Write valid state + receipt so the literal scan is reached
    receipt = _make_receipt()
    receipt_path = _write_receipt(tmp_path, receipt)
    state = _make_session_state(receipt_ref=receipt_path)
    _write_state(fake_state, state)
    result = pwg.check_core_addition_receipt(_TARGET_PATH, "apps_rg is forbidden")
    assert result is None  # bypass allows it
    assert fake_violations.exists()
    event = json.loads(fake_violations.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert "apps_rg" in event["reason"]
