"""V15 P10.3 — Integration Result Envelope Tests.

Validates the shared contract module and JSON envelope output from
both governance CLIs (review_summary + policy_pack validator).
"""

from __future__ import annotations

import json
from pathlib import Path

from agentic_core.L0_routing.types.integration_contract_types import (
    Finding,
    ResultEnvelope,
)
from ops_scripts.policy.validate_v15_policy_pack import (
    build_validator_envelope,
    validate_policy_pack,
)
from ops_scripts.review.generate_v15_review_summary import (
    generate_summary_with_envelope,
)

# ===========================================================================
# Helpers
# ===========================================================================


def _write_json(tmp_path: Path, name: str, data: dict) -> Path:
    p = tmp_path / name
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def _evidence(phase: str, passed: int = 5, violations: int = 0):
    return {
        "phase": phase,
        "gate": f"gate_{phase.lower()}",
        "passed": passed,
        "violations": violations,
        "total_checks": passed + violations,
        "blocking": False,
        "passed_details": [],
        "violation_details": [],
    }


def _guardian(status: str = "PASS"):
    return {
        "status": status,
        "violations": [],
        "metadata": {
            "total_tests": 88,
            "passed_tests": 88,
            "failed_tests": 0,
            "skipped_tests": 0,
            "failed_by_category": {},
        },
    }


def _valid_pack():
    return {
        "version": "1.0.0",
        "rules": [
            {
                "rule_id": "TEST_001",
                "applies_to": "PIPE",
                "severity": "WARN",
                "description": "test",
                "enabled": True,
            },
        ],
    }


# ===========================================================================
# A) Contract Module (ResultEnvelope + Finding)
# ===========================================================================


class TestContractModule:
    """Core contract dataclasses."""

    def test_pass_status(self):
        env = ResultEnvelope(tool="test", exit_code=0)
        assert env.status == "PASS"

    def test_warn_status(self):
        env = ResultEnvelope(tool="test", exit_code=0)
        env.findings.append(Finding(code="W", severity="WARN", message="warn"))
        assert env.status == "WARN"

    def test_fail_status_exit_code(self):
        env = ResultEnvelope(tool="test", exit_code=2)
        assert env.status == "FAIL"

    def test_fail_status_error_finding(self):
        env = ResultEnvelope(tool="test", exit_code=0)
        env.findings.append(Finding(code="E", severity="ERROR", message="err"))
        assert env.status == "FAIL"

    def test_to_ordered_dict_keys(self):
        env = ResultEnvelope(tool="test", exit_code=0)
        d = env.to_ordered_dict()
        assert set(d.keys()) == {
            "tool",
            "schema_version",
            "status",
            "exit_code",
            "inputs",
            "findings",
            "outputs",
        }

    def test_schema_version(self):
        env = ResultEnvelope(tool="test", exit_code=0)
        assert env.to_ordered_dict()["schema_version"] == "1.0.0"

    def test_to_json_deterministic(self):
        env = ResultEnvelope(tool="test", exit_code=0)
        env.inputs["b"] = {"path": "b.json", "present": True}
        env.inputs["a"] = {"path": "a.json", "present": False}
        j1 = env.to_json()
        j2 = env.to_json()
        assert j1 == j2
        parsed = json.loads(j1)
        assert list(parsed["inputs"].keys()) == ["a", "b"]

    def test_write_json(self, tmp_path):
        env = ResultEnvelope(tool="test", exit_code=0)
        out = tmp_path / "result.json"
        env.write_json(out)
        assert out.is_file()
        parsed = json.loads(out.read_text(encoding="utf-8"))
        assert parsed["tool"] == "test"
        assert parsed["status"] == "PASS"

    def test_finding_to_ordered_dict(self):
        f = Finding(code="C", severity="WARN", message="msg", context={"k": "v"})
        d = f.to_ordered_dict()
        assert list(d.keys()) == ["code", "context", "message", "severity"]

    def test_finding_no_context(self):
        f = Finding(code="C", severity="INFO", message="msg")
        d = f.to_ordered_dict()
        assert d["context"] == {}


# ===========================================================================
# B) Review Summary Envelope
# ===========================================================================


class TestReviewSummaryEnvelope:
    """Envelope from review summary generator."""

    def test_all_pass_envelope(self, tmp_path):
        ev = {}
        for ph in ["P3", "P4", "P5", "P6"]:
            ev[ph] = _write_json(tmp_path, f"v15_{ph.lower()}_evidence.json", _evidence(ph))
        gp = _write_json(tmp_path, "guardian_report.json", _guardian())

        md, code, env = generate_summary_with_envelope(
            evidence_files=ev,
            guardian_report_paths=[gp],
            out_path="summary.md",
        )
        assert code == 0
        assert env.status == "PASS"
        assert env.tool == "review_summary"
        d = env.to_ordered_dict()
        assert d["schema_version"] == "1.0.0"
        assert d["exit_code"] == 0
        assert "evidence_p3" in d["inputs"]
        assert d["outputs"]["markdown"]["path"] == "summary.md"

    def test_missing_guardian_envelope_warn(self, tmp_path):
        ev = {}
        for ph in ["P3", "P4", "P5", "P6"]:
            ev[ph] = _write_json(tmp_path, f"v15_{ph.lower()}_evidence.json", _evidence(ph))

        md, code, env = generate_summary_with_envelope(
            evidence_files=ev,
            guardian_report_paths=[tmp_path / "nonexistent.json"],
            out_path="summary.md",
        )
        assert code == 0
        assert env.status == "WARN"
        warn_codes = [f.code for f in env.findings if f.severity == "WARN"]
        assert "INPUT_MISSING" in warn_codes
        assert "APPROVAL_NO" in warn_codes

    def test_partial_missing_evidence(self, tmp_path):
        ev = {
            "P3": _write_json(tmp_path, "v15_p3_evidence.json", _evidence("P3")),
            "P4": tmp_path / "v15_p4_evidence.json",
        }
        gp = _write_json(tmp_path, "guardian_report.json", _guardian())

        md, code, env = generate_summary_with_envelope(
            evidence_files=ev,
            guardian_report_paths=[gp],
            out_path="summary.md",
        )
        assert code == 0
        assert env.status == "WARN"
        missing_findings = [f for f in env.findings if f.code == "INPUT_MISSING"]
        assert any("P4" in f.message for f in missing_findings)

    def test_all_missing_envelope_fail(self, tmp_path):
        ev = {ph: tmp_path / f"v15_{ph.lower()}_evidence.json" for ph in ["P3", "P4"]}
        md, code, env = generate_summary_with_envelope(
            evidence_files=ev,
            guardian_report_paths=[tmp_path / "nonexistent.json"],
        )
        assert code == 1
        assert env.status == "FAIL"
        assert any(f.code == "ALL_INPUTS_MISSING" for f in env.findings)

    def test_determinism(self, tmp_path):
        ev = {}
        for ph in ["P3", "P4", "P5", "P6"]:
            ev[ph] = _write_json(tmp_path, f"v15_{ph.lower()}_evidence.json", _evidence(ph))
        gp = _write_json(tmp_path, "guardian_report.json", _guardian())

        _, _, env1 = generate_summary_with_envelope(
            evidence_files=ev,
            guardian_report_paths=[gp],
            out_path="s.md",
        )
        _, _, env2 = generate_summary_with_envelope(
            evidence_files=ev,
            guardian_report_paths=[gp],
            out_path="s.md",
        )
        assert env1.to_json() == env2.to_json()


# ===========================================================================
# C) Policy Validator Envelope
# ===========================================================================


class TestPolicyValidatorEnvelope:
    """Envelope from policy pack validator."""

    def test_valid_pack_envelope(self, tmp_path):
        pack_path = _write_json(tmp_path, "pack.json", _valid_pack())
        code, errors, warnings = validate_policy_pack(_valid_pack())
        env = build_validator_envelope(str(pack_path), code, errors, warnings)

        assert env.status == "PASS"
        assert env.tool == "policy_pack_validator"
        d = env.to_ordered_dict()
        assert d["exit_code"] == 0
        assert d["inputs"]["policy_pack"]["present"] is True

    def test_schema_fail_envelope(self, tmp_path):
        bad = {"version": "1.0.0", "rules": [{"rule_id": "X"}]}
        pack_path = _write_json(tmp_path, "bad.json", bad)
        code, errors, warnings = validate_policy_pack(bad)
        env = build_validator_envelope(str(pack_path), code, errors, warnings)

        assert env.status == "FAIL"
        assert env.exit_code == 2
        error_findings = [f for f in env.findings if f.severity == "ERROR"]
        assert len(error_findings) > 0
        assert all(f.code == "SCHEMA_ERROR" for f in error_findings)

    def test_duplicate_fail_envelope(self, tmp_path):
        dup = _valid_pack()
        dup["rules"].append(dup["rules"][0].copy())
        pack_path = _write_json(tmp_path, "dup.json", dup)
        code, errors, warnings = validate_policy_pack(dup)
        env = build_validator_envelope(str(pack_path), code, errors, warnings)

        assert env.status == "FAIL"
        assert env.exit_code == 3
        assert any(f.code == "DUPLICATE_RULE_ID" for f in env.findings)

    def test_warning_envelope(self, tmp_path):
        pack = _valid_pack()
        pack["future"] = "compat"
        pack_path = _write_json(tmp_path, "pack.json", pack)
        code, errors, warnings = validate_policy_pack(pack)
        env = build_validator_envelope(str(pack_path), code, errors, warnings)

        assert env.status == "WARN"
        assert env.exit_code == 0
        warn_findings = [f for f in env.findings if f.severity == "WARN"]
        assert len(warn_findings) > 0

    def test_json_written_on_fail(self, tmp_path):
        bad = {"version": "1.0.0", "rules": [{"rule_id": "X"}]}
        pack_path = _write_json(tmp_path, "bad.json", bad)
        code, errors, warnings = validate_policy_pack(bad)
        env = build_validator_envelope(str(pack_path), code, errors, warnings)
        out = tmp_path / "result.json"
        env.write_json(out)

        assert out.is_file()
        parsed = json.loads(out.read_text(encoding="utf-8"))
        assert parsed["status"] == "FAIL"
        assert parsed["exit_code"] == 2

    def test_determinism(self, tmp_path):
        pack_path = _write_json(tmp_path, "pack.json", _valid_pack())
        code, errors, warnings = validate_policy_pack(_valid_pack())
        env1 = build_validator_envelope(str(pack_path), code, errors, warnings)
        env2 = build_validator_envelope(str(pack_path), code, errors, warnings)
        assert env1.to_json() == env2.to_json()
