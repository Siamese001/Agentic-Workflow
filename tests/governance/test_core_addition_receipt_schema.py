#!/usr/bin/env python3
"""
test_core_addition_receipt_schema.py - W2.P2 Schema Validation Tests

Validates that CoreAdditionAuthorGateReceipt.schema.json correctly accepts
valid receipts and rejects invalid ones across all required fields.

Plan: core-addition-author-gate-governance-f3b9e2, W2.P2
"""

import copy
import json
import pathlib

import jsonschema
import pytest

SCHEMA_PATH = pathlib.Path(__file__).parents[2] / ".claude" / "schemas" / "CoreAdditionAuthorGateReceipt.schema.json"

with SCHEMA_PATH.open(encoding="utf-8") as _f:
    SCHEMA = json.load(_f)

_VALIDATOR = jsonschema.Draft7Validator(SCHEMA)


def _validate(doc: dict) -> list[str]:
    """Return list of error messages (empty = valid)."""
    return [e.message for e in _VALIDATOR.iter_errors(doc)]


def _valid() -> dict:
    """Return a fully valid minimal receipt."""
    return {
        "receipt_type": "CoreAdditionAuthorGateReceipt",
        "plan_id": "core-addition-author-gate-governance-f3b9e2",
        "plan_type": "platform_core_change",
        "changed_paths": ["agentic_core/L0_routing/new_module.py"],
        "decision": {
            "verdict": "PASS",
            "rationale": "All tests pass and no app literals found.",
            "decided_at": "2026-05-12T06:00:00Z",
        },
        "tests": {
            "spine_substrate_test":             {"result": "PASS", "evidence": "Generic only."},
            "any_app_capability_test":          {"result": "PASS", "evidence": "No app capability."},
            "app_owned_meaning_test":           {"result": "PASS", "evidence": "Apps own meaning."},
            "no_app_literal_test":              {"result": "PASS", "evidence": "Scan clean."},
            "plugin_test":                      {"result": "PASS", "evidence": "Plugin fixture passes."},
            "negative_control_test":            {"result": "PASS", "evidence": "All 20 negative controls pass."},
            "platform_approval_test":           {"result": "PASS", "evidence": "Approved in plan."},
            "boundary_preservation_test":       {"result": "PASS", "evidence": "Boundary scan clean."},
            "contract_compatibility_test":      {"result": "PASS", "evidence": "Schema scan clean."},
            "runtime_proof_compatibility_test": {"result": "PASS", "evidence": "Runtime proof passes."},
        },
        "artifacts": {
            "no_app_literal_scan_ref": {
                "path": "artifacts/governance/no_app_literal_scan.json",
                "digest": "sha256:abc123",
                "verdict": "PASS",
                "plan_id": "core-addition-author-gate-governance-f3b9e2",
                "freshness_ts": "2026-05-12T06:00:00Z",
                "changed_paths_covered": ["agentic_core/L0_routing/new_module.py"],
            },
            "strict_scan_ref": {
                "path": "artifacts/governance/strict_scan.json",
                "digest": "sha256:def456",
                "verdict": "PASS",
                "plan_id": "core-addition-author-gate-governance-f3b9e2",
                "freshness_ts": "2026-05-12T06:00:00Z",
                "changed_paths_covered": ["agentic_core/L0_routing/new_module.py"],
            },
            "negative_control_results_ref": {
                "path": "artifacts/governance/negative_controls.json",
                "digest": "sha256:ghi789",
                "verdict": "PASS",
                "plan_id": "core-addition-author-gate-governance-f3b9e2",
                "freshness_ts": "2026-05-12T06:00:00Z",
                "changed_paths_covered": ["agentic_core/L0_routing/new_module.py"],
            },
            "plugin_proof_ref": {
                "path": "artifacts/governance/plugin_proof.json",
                "digest": "sha256:jkl012",
                "verdict": "PASS",
                "plan_id": "core-addition-author-gate-governance-f3b9e2",
                "freshness_ts": "2026-05-12T06:00:00Z",
                "changed_paths_covered": ["agentic_core/L0_routing/new_module.py"],
            },
            "boundary_scan_ref": {
                "path": "artifacts/governance/boundary_scan.json",
                "digest": "sha256:mno345",
                "verdict": "PASS",
                "plan_id": "core-addition-author-gate-governance-f3b9e2",
                "freshness_ts": "2026-05-12T06:00:00Z",
                "changed_paths_covered": ["agentic_core/L0_routing/new_module.py"],
            },
            "contract_schema_scan_ref": {
                "path": "artifacts/governance/contract_schema_scan.json",
                "digest": "sha256:pqr678",
                "verdict": "PASS",
                "plan_id": "core-addition-author-gate-governance-f3b9e2",
                "freshness_ts": "2026-05-12T06:00:00Z",
                "changed_paths_covered": ["agentic_core/L0_routing/new_module.py"],
            },
        },
        "signature": {
            "receipt_digest": "sha256:stu901",
        },
    }


# ---------------------------------------------------------------------------
# Test 1: valid minimal receipt passes
# ---------------------------------------------------------------------------

def test_valid_minimal_receipt_passes():
    errors = _validate(_valid())
    assert errors == [], f"Unexpected validation errors: {errors}"


# ---------------------------------------------------------------------------
# Test 2: missing receipt_type fails
# ---------------------------------------------------------------------------

def test_missing_receipt_type_fails():
    doc = _valid()
    del doc["receipt_type"]
    errors = _validate(doc)
    assert errors, "Expected validation error for missing receipt_type"


# ---------------------------------------------------------------------------
# Test 3: wrong plan_type fails
# ---------------------------------------------------------------------------

def test_wrong_plan_type_fails():
    doc = _valid()
    doc["plan_type"] = "refactor"
    errors = _validate(doc)
    assert errors, "Expected validation error for plan_type != platform_core_change"


# ---------------------------------------------------------------------------
# Test 4: missing changed_paths fails
# ---------------------------------------------------------------------------

def test_missing_changed_paths_fails():
    doc = _valid()
    del doc["changed_paths"]
    errors = _validate(doc)
    assert errors, "Expected validation error for missing changed_paths"


# ---------------------------------------------------------------------------
# Test 5: changed_paths outside agentic_core fails
# ---------------------------------------------------------------------------

def test_changed_paths_outside_agentic_core_fails():
    doc = _valid()
    doc["changed_paths"] = ["apps_rg/some_module.py"]
    errors = _validate(doc)
    assert errors, "Expected validation error for changed_paths not under agentic_core/"


# ---------------------------------------------------------------------------
# Test 6: missing required test object fails
# ---------------------------------------------------------------------------

def test_missing_required_test_object_fails():
    doc = _valid()
    del doc["tests"]["spine_substrate_test"]
    errors = _validate(doc)
    assert errors, "Expected validation error for missing spine_substrate_test"


# ---------------------------------------------------------------------------
# Test 7: test result SKIP fails (only PASS/FAIL allowed)
# ---------------------------------------------------------------------------

def test_test_result_skip_fails():
    doc = _valid()
    doc["tests"]["spine_substrate_test"]["result"] = "SKIP"
    errors = _validate(doc)
    assert errors, "Expected validation error for test result 'SKIP'"


# ---------------------------------------------------------------------------
# Test 8: missing test evidence fails
# ---------------------------------------------------------------------------

def test_missing_test_evidence_fails():
    doc = _valid()
    del doc["tests"]["no_app_literal_test"]["evidence"]
    errors = _validate(doc)
    assert errors, "Expected validation error for missing test evidence"


# ---------------------------------------------------------------------------
# Test 9: extra unexpected test key fails (additionalProperties: false)
# ---------------------------------------------------------------------------

def test_extra_unexpected_test_key_fails():
    doc = _valid()
    doc["tests"]["unexpected_new_test"] = {"result": "PASS", "evidence": "Extra."}
    errors = _validate(doc)
    assert errors, "Expected validation error for extra test key (additionalProperties: false)"


# ---------------------------------------------------------------------------
# Test 10: missing artifact ref fails
# ---------------------------------------------------------------------------

def test_missing_artifact_ref_fails():
    doc = _valid()
    del doc["artifacts"]["plugin_proof_ref"]
    errors = _validate(doc)
    assert errors, "Expected validation error for missing plugin_proof_ref"


# ---------------------------------------------------------------------------
# Test 11: artifact verdict FAIL is schema-valid but gate helper rejects it
#           (schema allows FAIL; rejection is enforced at gate/hook layer)
# ---------------------------------------------------------------------------

def test_artifact_verdict_fail_is_schema_valid_gate_rejects():
    """
    The JSON Schema allows verdict: FAIL — the schema does not hard-block it
    because a receipt documenting a failed scan is a valid intermediate state.
    Enforcement that all artifacts must have verdict=PASS before a write is
    permitted is done at the gate/hook layer (W3), not the schema layer.
    """
    doc = _valid()
    doc["artifacts"]["strict_scan_ref"]["verdict"] = "FAIL"
    errors = _validate(doc)
    # Schema accepts it; gate layer is responsible for rejecting verdict=FAIL
    assert errors == [], (
        "Schema should accept verdict=FAIL (gate enforces PASS requirement); "
        f"got unexpected schema errors: {errors}"
    )

    # Gate-level helper: verify that a simple check function would reject it
    def _gate_check(receipt: dict) -> bool:
        """Returns True if all artifact verdicts are PASS."""
        return all(
            ref["verdict"] == "PASS"
            for ref in receipt["artifacts"].values()
        )

    assert not _gate_check(doc), "Gate helper must reject receipt with artifact verdict=FAIL"
    assert _gate_check(_valid()), "Gate helper must accept receipt with all artifact verdicts=PASS"


# ---------------------------------------------------------------------------
# Test 12: missing signature.receipt_digest fails
# ---------------------------------------------------------------------------

def test_missing_signature_receipt_digest_fails():
    doc = _valid()
    del doc["signature"]["receipt_digest"]
    errors = _validate(doc)
    assert errors, "Expected validation error for missing signature.receipt_digest"


# ---------------------------------------------------------------------------
# Additional coverage: empty changed_paths fails (minItems: 1)
# ---------------------------------------------------------------------------

def test_empty_changed_paths_fails():
    doc = _valid()
    doc["changed_paths"] = []
    errors = _validate(doc)
    assert errors, "Expected validation error for empty changed_paths array"


# ---------------------------------------------------------------------------
# Additional coverage: wrong receipt_type const fails
# ---------------------------------------------------------------------------

def test_wrong_receipt_type_const_fails():
    doc = _valid()
    doc["receipt_type"] = "SomeOtherReceipt"
    errors = _validate(doc)
    assert errors, "Expected validation error for wrong receipt_type value"


# ---------------------------------------------------------------------------
# Additional coverage: decision verdict UNKNOWN fails (only PASS/FAIL allowed)
# ---------------------------------------------------------------------------

def test_decision_verdict_unknown_fails():
    doc = _valid()
    doc["decision"]["verdict"] = "UNKNOWN"
    errors = _validate(doc)
    assert errors, "Expected validation error for decision verdict 'UNKNOWN'"


# ---------------------------------------------------------------------------
# Additional coverage: root additionalProperties false rejects extra keys
# ---------------------------------------------------------------------------

def test_root_extra_property_fails():
    doc = _valid()
    doc["unexpected_root_key"] = "should_fail"
    errors = _validate(doc)
    assert errors, "Expected validation error for unexpected root-level property"


# ---------------------------------------------------------------------------
# Additional coverage: artifact with missing path fails
# ---------------------------------------------------------------------------

def test_artifact_missing_path_fails():
    doc = _valid()
    del doc["artifacts"]["boundary_scan_ref"]["path"]
    errors = _validate(doc)
    assert errors, "Expected validation error for artifact missing 'path'"


# ---------------------------------------------------------------------------
# Additional coverage: artifact with empty changed_paths_covered fails
# ---------------------------------------------------------------------------

def test_artifact_empty_changed_paths_covered_fails():
    doc = _valid()
    doc["artifacts"]["contract_schema_scan_ref"]["changed_paths_covered"] = []
    errors = _validate(doc)
    assert errors, "Expected validation error for empty artifact changed_paths_covered"


# ---------------------------------------------------------------------------
# Additional coverage: artifact changed_paths_covered outside agentic_core fails
# ---------------------------------------------------------------------------

def test_artifact_changed_paths_outside_agentic_core_fails():
    doc = _valid()
    doc["artifacts"]["no_app_literal_scan_ref"]["changed_paths_covered"] = ["apps_lic/some.py"]
    errors = _validate(doc)
    assert errors, "Expected validation error for artifact paths outside agentic_core/"
