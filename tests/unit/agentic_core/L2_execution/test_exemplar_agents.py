"""Tests for W6 exemplar validator + healer pair (plan c8e4f1)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from agentic_core.base_agents.SovereignHealerBase import (
    HealerCannotValidateError,
    SovereignHealerBase,
)
from agentic_core.base_agents.SovereignValidatorBase import (
    SovereignValidatorBase,
    ValidatorCannotHealError,
)
from agentic_core.L2_execution.enforcement.agent_seal_helper import (
    REQUIRES_SEALED_RETURN_ATTR,
)
from agentic_core.L2_execution.reasoning.examples.code_quality_healer import (
    CodeQualityHealerExemplar,
)
from agentic_core.L2_execution.reasoning.examples.code_quality_validator import (
    CodeQualityValidatorExemplar,
)
from agentic_core.L2_execution.types.sealed_l2_artifact import (
    SealedL2Artifact,
    TerminalClassification,
)
from agentic_core.L5_safety.types.heal_request_types import (
    HealOutcome,
    HealRequest,
)


class TestValidatorInheritance:
    def test_is_subclass_of_validator_base(self):
        assert issubclass(CodeQualityValidatorExemplar, SovereignValidatorBase)

    def test_has_sealed_return_marker(self):
        assert getattr(CodeQualityValidatorExemplar, REQUIRES_SEALED_RETURN_ATTR) is True

    def test_cannot_invoke_heal_on_validator(self):
        v = CodeQualityValidatorExemplar()
        with pytest.raises(ValidatorCannotHealError):
            v.heal({"violation": "x"})


class TestValidatorLogic:
    def test_accepts_compliant_code(self):
        v = CodeQualityValidatorExemplar(max_line_length=80)
        verdict = v.validate({"code": "short line\nanother short\n"})
        assert verdict["is_allowed"] is True

    def test_rejects_long_line(self):
        v = CodeQualityValidatorExemplar(max_line_length=20)
        verdict = v.validate({"code": "x" * 40})
        assert verdict["is_allowed"] is False
        assert "1 line" in verdict["reason"]
        assert verdict["evidence"]["offending_lines"]

    def test_rejects_non_dict_packet(self):
        v = CodeQualityValidatorExemplar()
        verdict = v.validate("not a dict")
        assert verdict["is_allowed"] is False

    def test_rejects_non_string_code(self):
        v = CodeQualityValidatorExemplar()
        verdict = v.validate({"code": 42})
        assert verdict["is_allowed"] is False


class TestValidatorEvaluate:
    def test_returns_sealed_artifact_on_pass(self):
        v = CodeQualityValidatorExemplar(max_line_length=80)
        seal = v.evaluate({"code": "ok\n"})
        assert isinstance(seal, SealedL2Artifact)
        assert seal.terminal_classification is TerminalClassification.SUCCESS
        assert seal.has_commit_payload is False
        assert seal.state_diff == {}

    def test_returns_sealed_artifact_on_fail(self):
        v = CodeQualityValidatorExemplar(max_line_length=20)
        seal = v.evaluate({"code": "x" * 40})
        assert isinstance(seal, SealedL2Artifact)
        assert seal.terminal_classification is TerminalClassification.REJECTED


class TestHealerInheritance:
    def test_is_subclass_of_healer_base(self):
        assert issubclass(CodeQualityHealerExemplar, SovereignHealerBase)

    def test_has_sealed_return_marker(self):
        assert getattr(CodeQualityHealerExemplar, REQUIRES_SEALED_RETURN_ATTR) is True

    def test_cannot_invoke_validate_on_healer(self):
        h = CodeQualityHealerExemplar()
        with pytest.raises(HealerCannotValidateError):
            h.validate("packet")


def _make_heal_request(code: str, max_len: int = 20) -> HealRequest:
    return HealRequest(
        request_id="heal-req-1",
        parent_packet_id="pkt-42",
        policy_hash="pol-abc",
        blueprint_hash="bp-xyz",
        violation_payload={"code": code, "max_line_length": max_len},
        originating_run_id="run-1",
    )


class TestHealerLogic:
    def test_repairs_long_line(self):
        h = CodeQualityHealerExemplar()
        req = _make_heal_request("hello world " * 20, max_len=30)
        result = h.heal(req)
        assert result.outcome is HealOutcome.SUCCESS
        assert result.reason_code == "long_lines_wrapped"
        assert result.repair_count == 1
        assert result.policy_hash == "pol-abc"
        assert result.blueprint_hash == "bp-xyz"
        assert result.parent_packet_id == "pkt-42"
        assert result.evidence["lines_changed"] >= 1

    def test_no_repair_needed_is_success(self):
        h = CodeQualityHealerExemplar()
        req = _make_heal_request("short\n", max_len=80)
        result = h.heal(req)
        assert result.outcome is HealOutcome.SUCCESS
        assert result.reason_code == "no_repair_needed"

    def test_missing_code_payload_is_fail_terminal(self):
        h = CodeQualityHealerExemplar()
        req = HealRequest(
            request_id="r",
            parent_packet_id="p",
            policy_hash="pol",
            blueprint_hash="bp",
            violation_payload={},  # no 'code' key
            originating_run_id="run",
        )
        result = h.heal(req)
        assert result.outcome is HealOutcome.FAIL_TERMINAL
        assert result.reason_code == "missing_code_payload"

    def test_invalid_request_type_escalates(self):
        h = CodeQualityHealerExemplar()
        result = h.heal({"not": "a HealRequest"})
        assert result.outcome is HealOutcome.NEEDS_HELP
        assert result.reason_code == "invalid_heal_request_type"


class TestHealerRepair:
    def test_returns_sealed_artifact(self):
        h = CodeQualityHealerExemplar()
        req = _make_heal_request("hello " * 50, max_len=40)
        seal = h.repair(req)
        assert isinstance(seal, SealedL2Artifact)
        assert seal.terminal_classification is TerminalClassification.SUCCESS
        assert seal.has_commit_payload is False
        assert seal.state_diff == {}
        assert seal.exec_trace["policy_hash"] == "pol-abc"
        assert seal.exec_trace["blueprint_hash"] == "bp-xyz"
        assert seal.exec_trace["parent_packet_id"] == "pkt-42"

    def test_needs_help_seal_for_invalid_request(self):
        h = CodeQualityHealerExemplar()
        seal = h.repair("not a HealRequest")
        assert seal.terminal_classification is TerminalClassification.NEEDS_HELP


class TestSnapshotBindingInvariant:
    def test_heal_preserves_originating_hashes(self):
        """L2 Execute v2 §E4: heal MUST use same policy/blueprint as E2."""
        h = CodeQualityHealerExemplar()
        req = _make_heal_request("x " * 30, max_len=20)
        result = h.heal(req)
        # The two hashes in result MUST equal the ones in req.
        assert result.policy_hash == req.policy_hash
        assert result.blueprint_hash == req.blueprint_hash


GATE_SCRIPT = (
    Path(__file__).resolve().parents[4]
    / "ops_scripts"
    / "ci"
    / "check_agent_sealed_return.py"
)


class TestCIGateAcceptsExemplars:
    """Verify the W5 CI gate does NOT flag the W6 exemplars."""

    def test_gate_passes_on_current_repo_for_examples_dir(self, tmp_path: Path):
        # Copy just the examples dir into a staging tree the gate will scan.
        staging = tmp_path / "agentic_core" / "L2_execution" / "reasoning" / "examples"
        staging.mkdir(parents=True)
        src_dir = Path(__file__).resolve().parents[4] / "agentic_core" / "L2_execution" / "reasoning" / "examples"
        for p in src_dir.glob("*.py"):
            (staging / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
        # Also stage the seal helper so the AST gate can resolve names (it only
        # AST-scans, doesn't import — but having the file tree prevents "parse_error"
        # noise on empty dir).
        (tmp_path / "agentic_core" / "__init__.py").write_text("", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(GATE_SCRIPT), str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 0, (
            f"Gate flagged exemplars as non-conforming.\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
