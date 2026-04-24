"""Tests for W5 agent_seal_helper + check_agent_sealed_return CI gate (plan c8e4f1)."""
from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from agentic_core.L2_execution.enforcement.agent_seal_helper import (
    REQUIRES_SEALED_RETURN_ATTR,
    build_seal_from_heal,
    build_seal_from_validator,
    heal_outcome_to_terminal,
    requires_sealed_return,
)
from agentic_core.L2_execution.types.sealed_l2_artifact import (
    SealedL2Artifact,
    TerminalClassification,
)
from agentic_core.L5_safety.types.heal_request_types import HealOutcome, HealResult


def _heal(outcome: HealOutcome = HealOutcome.SUCCESS) -> HealResult:
    return HealResult(
        outcome=outcome,
        reason_code="ok",
        parent_packet_id="pkt-1",
        repair_count=1,
        policy_hash="pol-abc",
        blueprint_hash="bp-xyz",
        evidence={"k": "v"},
    )


class TestOutcomeToTerminal:
    @pytest.mark.parametrize(
        ("outcome", "expected"),
        [
            (HealOutcome.SUCCESS, TerminalClassification.SUCCESS),
            (HealOutcome.SOFT_REPAIRABLE, TerminalClassification.SUCCESS),
            (HealOutcome.FAIL_TERMINAL, TerminalClassification.FAILURE),
            (HealOutcome.NEEDS_HELP, TerminalClassification.NEEDS_HELP),
        ],
    )
    def test_mapping(self, outcome, expected):
        assert heal_outcome_to_terminal(outcome) is expected


class TestBuildSealFromHeal:
    def test_success_seal(self):
        seal = build_seal_from_heal(_heal(HealOutcome.SUCCESS), trace_id="t-1")
        assert isinstance(seal, SealedL2Artifact)
        assert seal.trace_id == "t-1"
        assert seal.terminal_classification is TerminalClassification.SUCCESS
        assert seal.has_commit_payload is False
        assert seal.state_diff == {}  # L2 never commits
        assert seal.exec_trace["policy_hash"] == "pol-abc"
        assert seal.exec_trace["blueprint_hash"] == "bp-xyz"
        assert seal.exec_trace["parent_packet_id"] == "pkt-1"
        assert seal.escalation_reason is None

    def test_needs_help_includes_escalation(self):
        r = HealResult(
            outcome=HealOutcome.NEEDS_HELP,
            reason_code="not_implemented",
            parent_packet_id="pkt-1",
            repair_count=0,
            policy_hash="pol",
            blueprint_hash="bp",
            message="agent escalates",
        )
        seal = build_seal_from_heal(r, trace_id="t-2")
        assert seal.terminal_classification is TerminalClassification.NEEDS_HELP
        assert seal.escalation_reason == "agent escalates"

    def test_fail_terminal_maps_to_failure(self):
        seal = build_seal_from_heal(_heal(HealOutcome.FAIL_TERMINAL), trace_id="t-3")
        assert seal.terminal_classification is TerminalClassification.FAILURE

    def test_evidence_bundle_override(self):
        seal = build_seal_from_heal(
            _heal(HealOutcome.SUCCESS),
            trace_id="t-4",
            evidence_bundle={"override": True},
        )
        assert seal.evidence_bundle == {"override": True}

    def test_seal_is_frozen(self):
        seal = build_seal_from_heal(_heal(), trace_id="t-5")
        with pytest.raises((AttributeError, TypeError)):
            seal.artifact_id = "changed"  # type: ignore[misc]


class TestBuildSealFromValidator:
    def test_approved_verdict(self):
        seal = build_seal_from_validator(
            {"decision": "approved", "tool_name": "t.x", "reason": "ok"},
            trace_id="t-10",
        )
        assert seal.terminal_classification is TerminalClassification.SUCCESS
        assert seal.validation_counters.policy_checks_passed == 1
        assert seal.escalation_reason is None

    def test_confirm_required_verdict(self):
        seal = build_seal_from_validator(
            {"decision": "confirm_required", "tool_name": "t.x", "reason": "critical mutation"},
            trace_id="t-11",
        )
        assert seal.terminal_classification is TerminalClassification.NEEDS_HELP
        assert seal.escalation_reason == "critical mutation"

    def test_rejected_verdict(self):
        seal = build_seal_from_validator(
            {"decision": "rejected", "tool_name": "t.x", "reason": "hard_policy"},
            trace_id="t-12",
        )
        assert seal.terminal_classification is TerminalClassification.REJECTED
        assert seal.validation_counters.policy_checks_failed == 1


class TestRequiresSealedReturnMarker:
    def test_decorator_sets_attribute(self):
        @requires_sealed_return
        class _Marked:
            pass

        assert getattr(_Marked, REQUIRES_SEALED_RETURN_ATTR) is True

    def test_unmarked_class_has_no_attribute(self):
        class _Unmarked:
            pass

        assert not hasattr(_Unmarked, REQUIRES_SEALED_RETURN_ATTR)


# ---- CI gate integration tests ----


def _write_sample_repo(base: Path, conforming: bool) -> None:
    """Create a minimal fake 'agentic_core' tree with a marked class."""
    agentic_core = base / "agentic_core"
    agentic_core.mkdir(parents=True)
    (agentic_core / "__init__.py").write_text("", encoding="utf-8")
    target_dir = agentic_core / "L2_execution" / "reasoning"
    target_dir.mkdir(parents=True)
    (target_dir / "__init__.py").write_text("", encoding="utf-8")
    ret_hint = "SealedL2Artifact" if conforming else "dict"
    source = textwrap.dedent(
        f"""
        from __future__ import annotations
        from typing import Any


        def requires_sealed_return(cls):
            cls.__l2v2_requires_sealed_return__ = True
            return cls


        class SealedL2Artifact:  # stand-in for the real type
            pass


        @requires_sealed_return
        class FakeAgent:
            def do_work(self, payload: dict[str, Any]) -> {ret_hint}:
                return {{}} if {conforming is False!r} else SealedL2Artifact()


        class UnmarkedAgent:
            def do_work(self, payload: dict[str, Any]) -> dict:
                return {{}}
        """
    ).strip()
    (target_dir / "_fake_agent.py").write_text(source, encoding="utf-8")


GATE_SCRIPT = Path(__file__).resolve().parents[4] / "ops_scripts" / "ci" / "check_agent_sealed_return.py"


class TestCIGate:
    def test_gate_script_exists(self):
        assert GATE_SCRIPT.is_file(), f"Gate script not found at {GATE_SCRIPT}"

    def test_gate_passes_on_conforming_repo(self, tmp_path: Path):
        _write_sample_repo(tmp_path, conforming=True)
        result = subprocess.run(
            [sys.executable, str(GATE_SCRIPT), str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    def test_gate_fails_on_violation(self, tmp_path: Path):
        _write_sample_repo(tmp_path, conforming=False)
        result = subprocess.run(
            [sys.executable, str(GATE_SCRIPT), str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 1, (
            f"Expected exit 1 (violation), got {result.returncode}. "
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
        )
        assert "FakeAgent.do_work" in result.stdout
        assert "UnmarkedAgent" not in result.stdout  # unmarked class not inspected

    def test_gate_tolerates_empty_repo(self, tmp_path: Path):
        result = subprocess.run(
            [sys.executable, str(GATE_SCRIPT), str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 0
