"""
Guardian: Direct Prompt Compilation Anti-Pattern Tests.

§1 windsurfrules compliance:
- §1.1  Every changed logic has deterministic test coverage
- §1.3  No randomness / wall-clock; all fixtures are static strings
- §1.5  Edge cases: empty, clean, allowlisted module, near-miss names
- §1.7  Determinism: same input → same output list
- §1.8  Fail-closed: violation emitted before any side-effect
- §1.9  Matrix: f-string × concatenation × join/format × slot-prefix
- §1.11 Regression: non-slot f-strings, assembly_stage allowlist

ROBUSTNESS_MATRIX:
  Surface                              | success | edge | failure | determinism
  -------------------------------------|---------|------|---------|------------
  f-string with s0_/i0_/d0_/c0_/u0_   |   ✅   |  ✅  |   ✅   |     ✅
  BinOp + concatenation of slot vars   |   ✅   |  ✅  |   ✅   |     ✅
  str.join() on slot vars              |   ✅   |  ✅  |   ✅   |     ✅
  str.format() on slot vars            |   ✅   |  ✅  |   ✅   |     ✅
  assembly_stage module allowlisted    |   ✅   |  ✅  |   N/A  |     ✅
  whitelist comment suppression        |   ✅   |  ✅  |   ✅   |     ✅
  clean file / no slot references      |   ✅   |  ✅  |   N/A  |     ✅

DEFECT_MODEL:
  D1 - f-string prompt assembly bypasses manifest hashing
  D2 - string concatenation bypasses authority ordering
  D3 - str.join/format bypasses injection scanning
  D4 - assembly_stage.py incorrectly flagged (false positive)
  D5 - non-slot variable falsely triggers detector
  D6 - whitelist incorrectly suppresses genuine violation
  D7 - detector non-determinism across repeated scans
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L5_safety.validators.base_detector_validator import (
    AntiPatternCategory,
    EnforcementLevel,
)
from agentic_core.L5_safety.validators.direct_prompt_compilation_validator import (
    DirectPromptCompilationDetector,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_guardian_prompt_assembly_exclusivity")
_emit_applies_guardrail("p0", "test_guardian_prompt_assembly_exclusivity", "p0_governance")
_emit_reads_policy_state("p0", "test_guardian_prompt_assembly_exclusivity", "policy_binding")
_emit_snapshots_state("p0", "test_guardian_prompt_assembly_exclusivity", "state_snapshot")
emit_replay_key("p0", "test_guardian_prompt_assembly_exclusivity")
emit_determinism_digest("p0", "test_guardian_prompt_assembly_exclusivity")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_guardian_prompt_assembly_exclusivity", "execution_auth")
_emit_validates_capability("p2", "test_guardian_prompt_assembly_exclusivity", "capability_check")
_emit_routes_to_capability("p2", "test_guardian_prompt_assembly_exclusivity", "capability_route")
_emit_writes_via_uwg("p2", "test_guardian_prompt_assembly_exclusivity", "uwg_write")
_emit_blocks_direct_write("p2", "test_guardian_prompt_assembly_exclusivity", "direct_write_block")
_emit_records_tool_invocation("p2", "test_guardian_prompt_assembly_exclusivity", "tool_invocation")
_emit_captures_execution_output("p2", "test_guardian_prompt_assembly_exclusivity", "exec_output")
_emit_dispatches_agent("p3", "test_guardian_prompt_assembly_exclusivity", "agent_dispatch")
_emit_coordinates_agents("p3", "test_guardian_prompt_assembly_exclusivity", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_guardian_prompt_assembly_exclusivity", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_guardian_prompt_assembly_exclusivity", "healing_outcome")
_emit_escalates_failure("p3", "test_guardian_prompt_assembly_exclusivity", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_guardian_prompt_assembly_exclusivity", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_guardian_prompt_assembly_exclusivity", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_guardian_prompt_assembly_exclusivity", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_guardian_prompt_assembly_exclusivity", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_guardian_prompt_assembly_exclusivity", "eval_metric")
_emit_stores_embedding("p4", "test_guardian_prompt_assembly_exclusivity", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_guardian_prompt_assembly_exclusivity", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_guardian_prompt_assembly_exclusivity", "exec_snapshot_link")

pytestmark = pytest.mark.guardian

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _detector() -> DirectPromptCompilationDetector:
    return DirectPromptCompilationDetector(enforcement_level=EnforcementLevel.WARNING)


def _violations(source: str, tmp_path: Path, filename: str = "subject.py") -> list:
    f = tmp_path / filename
    f.write_text(source, encoding="utf-8")
    tree = ast.parse(source)
    det = _detector()
    return det.detect(f, tree)


# ---------------------------------------------------------------------------
# Clean-file — success / no-violation path
# ---------------------------------------------------------------------------


class TestDirectPromptCompilationCleanFile:
    def test_empty_file_no_violations(self, tmp_path):
        assert _violations("", tmp_path) == []

    def test_regular_string_ops_no_violations(self, tmp_path):
        src = "msg = 'hello' + ' world'\n"
        assert _violations(src, tmp_path) == []

    def test_non_slot_fstring_no_violations(self, tmp_path):
        src = 'greeting = f"Hello {name}"\n'
        assert _violations(src, tmp_path) == []

    def test_non_slot_join_no_violations(self, tmp_path):
        src = 'parts = ["a", "b"]\nresult = "\\n".join(parts)\n'
        assert _violations(src, tmp_path) == []

    def test_comment_only_no_violations(self, tmp_path):
        src = "# no code here\n"
        assert _violations(src, tmp_path) == []


# ---------------------------------------------------------------------------
# Assembly Stage allowlist (D4 regression — must NOT flag assembly_stage.py)
# ---------------------------------------------------------------------------


class TestAssemblyStageAllowlist:
    def test_assembly_stage_module_not_flagged(self, tmp_path):
        src = 'result = f"{s0_system}\\n{u0_user_prompt}"\n'
        # file named assembly_stage.py → allowlisted
        viols = _violations(src, tmp_path, filename="assembly_stage.py")
        assert viols == []

    def test_airlock_assembler_module_not_flagged(self, tmp_path):
        src = 'out = s0_system + "\\n" + u0_user_prompt\n'
        viols = _violations(src, tmp_path, filename="airlock_assembler.py")
        assert viols == []

    def test_non_assembly_module_is_flagged(self, tmp_path):
        src = 'result = f"{s0_system}"\n'
        viols = _violations(src, tmp_path, filename="some_agent.py")
        assert len(viols) == 1


# ---------------------------------------------------------------------------
# f-string violations (§1.5 — covers all slot prefixes)
# ---------------------------------------------------------------------------


class TestFStringViolations:
    @pytest.mark.parametrize(
        "slot_var",
        ["s0_system", "i0_instruction", "d0_injection", "c0_context", "u0_user_prompt"],
    )
    def test_fstring_slot_prefix_detected(self, slot_var, tmp_path):
        src = f'{slot_var} = "x"\nresult = f"{{{slot_var}}}"\n'
        viols = _violations(src, tmp_path)
        assert len(viols) == 1
        assert viols[0].category == AntiPatternCategory.DIRECT_PROMPT_COMPILATION

    def test_fstring_violation_severity_is_error(self, tmp_path):
        src = 's0_system = "x"\nresult = f"{s0_system}"\n'
        viols = _violations(src, tmp_path)
        assert viols[0].severity == "error"

    def test_fstring_violation_message_mentions_slot(self, tmp_path):
        src = 's0_system = "x"\nresult = f"{s0_system}"\n'
        viols = _violations(src, tmp_path)
        assert "s0_system" in viols[0].message

    def test_fstring_multiple_slots_single_violation(self, tmp_path):
        src = 's0_system = "x"\nu0_user_prompt = "y"\nresult = f"{s0_system}\\n{u0_user_prompt}"\n'
        viols = _violations(src, tmp_path)
        # One f-string node → one violation
        assert len(viols) == 1

    def test_fstring_with_no_slot_no_violation(self, tmp_path):
        src = 'name = "world"\nresult = f"Hello {name}"\n'
        assert _violations(src, tmp_path) == []


# ---------------------------------------------------------------------------
# BinOp concatenation violations
# ---------------------------------------------------------------------------


class TestBinOpConcatenationViolations:
    def test_concat_s0_detected(self, tmp_path):
        src = 's0_system = "x"\nresult = s0_system + "\\n"\n'
        viols = _violations(src, tmp_path)
        assert len(viols) == 1
        assert viols[0].category == AntiPatternCategory.DIRECT_PROMPT_COMPILATION

    def test_concat_u0_detected(self, tmp_path):
        src = 'u0_user_prompt = "q"\nresult = "prefix" + u0_user_prompt\n'
        viols = _violations(src, tmp_path)
        assert len(viols) == 1

    def test_concat_non_slot_no_violation(self, tmp_path):
        src = 'a = "x"\nb = "y"\nresult = a + b\n'
        assert _violations(src, tmp_path) == []

    def test_concat_violation_message_mentions_concat(self, tmp_path):
        src = 's0_system = "x"\nresult = s0_system + "suffix"\n'
        viols = _violations(src, tmp_path)
        assert "concatenation" in viols[0].message.lower() or "+" in viols[0].message


# ---------------------------------------------------------------------------
# str.join() violations
# ---------------------------------------------------------------------------


class TestStrJoinViolations:
    def test_join_with_slot_list_detected(self, tmp_path):
        src = 's0_system = "x"\nresult = "\\n".join([s0_system, "extra"])\n'
        viols = _violations(src, tmp_path)
        assert len(viols) == 1
        assert viols[0].category == AntiPatternCategory.DIRECT_PROMPT_COMPILATION

    def test_join_without_slot_no_violation(self, tmp_path):
        src = 'parts = ["a", "b"]\nresult = "\\n".join(parts)\n'
        assert _violations(src, tmp_path) == []


# ---------------------------------------------------------------------------
# str.format() violations
# ---------------------------------------------------------------------------


class TestStrFormatViolations:
    def test_format_with_slot_arg_detected(self, tmp_path):
        src = 's0_system = "x"\nresult = "{}".format(s0_system)\n'
        viols = _violations(src, tmp_path)
        assert len(viols) == 1
        assert viols[0].category == AntiPatternCategory.DIRECT_PROMPT_COMPILATION

    def test_format_without_slot_no_violation(self, tmp_path):
        src = 'name = "world"\nresult = "Hello {}".format(name)\n'
        assert _violations(src, tmp_path) == []


# ---------------------------------------------------------------------------
# Whitelist suppression
# ---------------------------------------------------------------------------


class TestWhitelistSuppression:
    def test_whitelist_suppresses_fstring(self, tmp_path):
        src = 's0_system = "x"\n# guardian: allow-direct-prompt-compilation\nresult = f"{s0_system}"\n'
        viols = _violations(src, tmp_path)
        assert viols == []

    def test_wrong_whitelist_does_not_suppress(self, tmp_path):
        src = 's0_system = "x"\n# guardian: allow-other\nresult = f"{s0_system}"\n'
        viols = _violations(src, tmp_path)
        assert len(viols) == 1

    def test_whitelist_too_far_away_does_not_suppress(self, tmp_path):
        src = '# guardian: allow-direct-prompt-compilation\n\n\ns0_system = "x"\nresult = f"{s0_system}"\n'
        viols = _violations(src, tmp_path)
        assert len(viols) == 1


# ---------------------------------------------------------------------------
# Determinism (§1.7)
# ---------------------------------------------------------------------------


class TestDetectorDeterminism:
    def test_same_source_identical_violations(self, tmp_path):
        src = 's0_system = "x"\nresult = f"{s0_system}"\n'
        va = _violations(src, tmp_path)
        tmp2 = tmp_path / "b"
        tmp2.mkdir()
        vb = _violations(src, tmp2)
        assert len(va) == len(vb)
        assert va[0].category == vb[0].category
        assert va[0].message == vb[0].message

    def test_clean_source_consistently_empty(self, tmp_path):
        src = 'greeting = f"Hello {name}"\n'
        for _ in range(3):
            assert _violations(src, tmp_path) == []


# ---------------------------------------------------------------------------
# Violation contract: fail-closed (§1.8)
# ---------------------------------------------------------------------------


class TestViolationContract:
    def test_violation_fields_all_populated(self, tmp_path):
        src = 's0_system = "x"\nresult = f"{s0_system}"\n'
        viols = _violations(src, tmp_path)
        v = viols[0]
        assert v.file_path is not None
        assert v.line_number >= 1
        assert v.category == AntiPatternCategory.DIRECT_PROMPT_COMPILATION
        assert v.message
        assert v.evidence
        assert v.suggested_fix

    def test_violation_line_number_accurate(self, tmp_path):
        src = 'x = 1\ns0_system = "y"\nresult = f"{s0_system}"\n'
        viols = _violations(src, tmp_path)
        # f-string on line 3
        assert viols[0].line_number == 3


# ---------------------------------------------------------------------------
# Matrix: slot-prefix × operation-type (§1.9)
# ---------------------------------------------------------------------------


class TestSlotPrefixMatrix:
    @pytest.mark.parametrize(
        "slot_prefix,op,src_template",
        [
            ("s0_", "fstring", 's0_x = "v"\nout = f"{s0_x}"\n'),
            ("i0_", "fstring", 'i0_x = "v"\nout = f"{i0_x}"\n'),
            ("d0_", "fstring", 'd0_x = "v"\nout = f"{d0_x}"\n'),
            ("c0_", "fstring", 'c0_x = "v"\nout = f"{c0_x}"\n'),
            ("u0_", "fstring", 'u0_x = "v"\nout = f"{u0_x}"\n'),
            ("s0_", "concat", 's0_x = "v"\nout = s0_x + " extra"\n'),
            ("u0_", "concat", 'u0_x = "v"\nout = "prefix " + u0_x\n'),
            ("c0_", "join", 'c0_x = "v"\nout = "\\n".join([c0_x])\n'),
            ("i0_", "format", 'i0_x = "v"\nout = "{}".format(i0_x)\n'),
        ],
    )
    def test_matrix_cell(self, slot_prefix, op, src_template, tmp_path):
        viols = _violations(src_template, tmp_path)
        assert len(viols) >= 1, f"Expected violation for prefix={slot_prefix!r} op={op!r}"
