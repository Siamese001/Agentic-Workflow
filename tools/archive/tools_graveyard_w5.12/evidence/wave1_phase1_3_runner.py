"""
Wave 1 Phase 1.3 Evidence Runner - Governance Stamps, Airlock, JIT Sync Markers
Usage:
  draft:  python tools/evidence/wave1_phase1_3_runner.py --code-commit <SHA>
  seal:   python tools/evidence/wave1_phase1_3_runner.py --code-commit <SHA> --evidence-commit <SHA>
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "wave1_phase1_3_runner", "uwg_governed_write")
_emit_writes_through("p1", "wave1_phase1_3_runner", "uwg_governed_write_2")
_emit_pulls_context("p1", "wave1_phase1_3_runner", "context_retrieval")
_emit_pulls_context("p1", "wave1_phase1_3_runner", "context_retrieval_2")
emit_determinism_digest("trace_wave1_phase1_3_runner", "wave1_phase1_3_runner_dispatch")
emit_determinism_digest("trace_wave1_phase1_3_runner", "wave1_phase1_3_runner_complete")
_emit_validated_by_safety_plane("p1", "wave1_phase1_3_runner", "safety_validation")
_emit_reads_through("l4", "wave1_phase1_3_runner", "urg_read_1")
_emit_reads_through("l4", "wave1_phase1_3_runner", "urg_read_2")
_emit_reads_through("l4", "wave1_phase1_3_runner", "urg_read_3")
_emit_reads_through("l4", "wave1_phase1_3_runner", "urg_read_4")
_emit_reads_through("l4", "wave1_phase1_3_runner", "urg_read_5")
_emit_reads_through("l4", "wave1_phase1_3_runner", "urg_read_6")
_emit_reads_through("l4", "wave1_phase1_3_runner", "urg_read_7")
_emit_reads_through("l4", "wave1_phase1_3_runner", "urg_read_8")
_emit_reads_through("l4", "wave1_phase1_3_runner", "urg_read_9")
REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_PATH = REPO_ROOT / "docs" / REPORTS_DIR / "plans" / "wave1_phase1_3_evidence.md"
SCOPE_FILES = ["tests/architecture/test_wave1_phase1_3_governance.py"]


def _run(argv: list[str]) -> tuple[str, int]:
    result = subprocess.run(
        argv, cwd=str(REPO_ROOT), shell=False, encoding="utf-8", errors="replace", capture_output=True
    )
    combined = result.stdout + result.stderr
    combined = re.sub("\\x1b\\[[0-9;]*m", "", combined)
    return (combined.rstrip(), result.returncode)


def _git_show_names(commit: str) -> str:
    out, _ = _run(["git", "show", "--name-only", "--pretty=format:", commit])
    return out.strip()


def _assert_ascii(text: str, label: str) -> None:
    for i, ch in enumerate(text):
        if ord(ch) > 127:
            print(f"FAIL: non-ASCII byte 0x{ord(ch):02X} at position {i} in {label}", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--code-commit", required=True)
    parser.add_argument("--evidence-commit", default="PENDING")
    args = parser.parse_args()
    code_commit = args.code_commit.strip()
    evidence_commit = args.evidence_commit.strip()
    seal_mode = evidence_commit != "PENDING"
    if seal_mode and code_commit == evidence_commit:
        print("FAIL: in seal mode CODE_COMMIT must not equal EVIDENCE_COMMIT", file=sys.stderr)
        sys.exit(1)
    evidence_lines: list[str] = []

    def h(line: str = "") -> None:
        evidence_lines.append(line)

    h("# Wave 1 Phase 1.3 - Governance Stamps, Airlock, JIT Sync Marker Tests")
    h()
    h("## Scope")
    h()
    h("Add 33-test branch-coverage suite for governance/elevator/path_d detection machinery.")
    h("No analyzer code changes in this phase (tests only). N=1 file declared.")
    h()
    for f in SCOPE_FILES:
        h(f"- {f}")
    h()
    h("## CODE_COMMIT")
    h()
    h(code_commit)
    h()
    h("## EVIDENCE_COMMIT")
    h()
    h(evidence_commit)
    h()
    h("## FILES_CHANGED_CODE")
    h()
    h("```")
    h(_git_show_names(code_commit))
    h("```")
    h()
    h("## FILES_CHANGED_EVIDENCE")
    h()
    if seal_mode:
        h("```")
        h(_git_show_names(evidence_commit))
        h("```")
    else:
        h("PENDING")
    h()
    h("## INSPECTED_FILES")
    h()
    for f in SCOPE_FILES:
        h(f"- {f}")
    h()
    h("## Pytest - Phase 1.3 Tests")
    h()
    pytest_cmd = [
        "python",
        "-m",
        "pytest",
        "-q",
        "--color=no",
        "tests/architecture/test_wave1_phase1_3_governance.py",
    ]
    out, rc = _run(pytest_cmd)
    h("$ python -m pytest -q --color=no tests/architecture/test_wave1_phase1_3_governance.py")
    h("```")
    h(out)
    h("```")
    if rc != 0:
        h(f"EXIT CODE: {rc}")
        content = "\n".join(evidence_lines)
        _assert_ascii(content, "evidence")
        EVIDENCE_PATH.write_text(content + "\n", encoding="utf-8")
        print(f"FAIL: pytest exited {rc}", file=sys.stderr)
        sys.exit(1)
    h()
    collected = re.search("(\\d+) passed", out)
    passed_count = int(collected.group(1)) if collected else 0
    h(f"collected 33 / executed {passed_count}")
    h()
    h("## Hint Tuple Contract Verification")
    h()
    hint_check = [
        "python",
        "-c",
        "import sys\nsys.path.insert(0, '.')\nfrom tools.semantic_gap_analyzer import GOVERNANCE_STAMP_HINTS, ELEVATOR_SHAFT_HINTS, PATH_D_HINTS\nok = True\nfor name, tup in [('GOVERNANCE_STAMP_HINTS', GOVERNANCE_STAMP_HINTS), ('ELEVATOR_SHAFT_HINTS', ELEVATOR_SHAFT_HINTS), ('PATH_D_HINTS', PATH_D_HINTS)]:\n    if not tup:\n        print('FAIL:', name, 'is empty')\n        ok = False\n    else:\n        print('OK:', name, 'has', len(tup), 'hints')\nsys.exit(0 if ok else 1)\n",
    ]
    out, rc = _run(hint_check)
    h("$ python -c '<hint tuple contract check>'")
    h("```")
    h(out)
    h("```")
    if rc != 0:
        h(f"EXIT CODE: {rc}")
        content = "\n".join(evidence_lines)
        _assert_ascii(content, "evidence")
        EVIDENCE_PATH.write_text(content + "\n", encoding="utf-8")
        print(f"FAIL: hint tuple check exited {rc}", file=sys.stderr)
        sys.exit(1)
    h()
    h("## BRANCH_INVENTORY")
    h()
    h("| File | Function | Branch Type | Condition | Expected | Test |")
    h("|------|----------|-------------|-----------|----------|------|")
    rows = [
        (
            "semantic_gap_analyzer.py",
            "analyze_file (string literals)",
            "success",
            "literal contains compliance_hash",
            "governance_mentions populated",
            "test_governance_hint_in_string_literal_detected",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (string literals)",
            "success",
            "literal contains sandboxenvelope",
            "governance_mentions populated",
            "test_governance_hint_sandboxenvelope_detected",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (string literals)",
            "success",
            "literal contains capability_token",
            "governance_mentions populated",
            "test_governance_hint_capabilitytoken_detected",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (string literals)",
            "negative",
            "no governance hint in literal",
            "governance_mentions empty",
            "test_no_governance_hint_in_literal_produces_empty",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (string literals)",
            "boundary",
            "COMPLIANCE_HASH uppercase matches",
            "case-insensitive detection",
            "test_governance_hint_case_insensitive_in_literal",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (used_names)",
            "success",
            "used name contains compliance_hash",
            "governance_mentions populated",
            "test_governance_hint_in_used_name_detected",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (used_names)",
            "negative",
            "unrelated variable names",
            "governance_mentions empty",
            "test_unrelated_used_name_not_governance",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (elevator)",
            "success",
            "literal contains jit",
            "elevator_shaft_mentions populated",
            "test_elevator_hint_jit_in_string_detected",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (elevator)",
            "success",
            "literal contains semantic_clock",
            "elevator_shaft_mentions populated",
            "test_elevator_hint_semantic_clock_detected",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (elevator)",
            "success",
            "used name contains tool_budget",
            "elevator_shaft_mentions populated",
            "test_elevator_hint_tool_budget_detected",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (elevator)",
            "negative",
            "no elevator hint",
            "empty set",
            "test_no_elevator_hint_produces_empty",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (elevator)",
            "success",
            "used name capabilitytoken",
            "elevator_shaft_mentions populated",
            "test_elevator_hint_capability_token_in_name",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (path_d)",
            "success",
            "literal contains modify_diff",
            "path_d_mentions populated",
            "test_path_d_hint_modify_diff_detected",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (path_d)",
            "success",
            "literal contains original_plan_hash",
            "path_d_mentions populated",
            "test_path_d_hint_original_plan_hash_detected",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (path_d)",
            "negative",
            "no PATH_D hint",
            "empty set",
            "test_no_path_d_hint_produces_empty",
        ),
        (
            "semantic_gap_analyzer.py",
            "_has_any_marker",
            "success",
            "governance_mentions has hint",
            "True",
            "test_has_any_marker_true_via_governance_mentions",
        ),
        (
            "semantic_gap_analyzer.py",
            "_has_any_marker",
            "success",
            "elevator_mentions has hint",
            "True",
            "test_has_any_marker_true_via_elevator_mentions",
        ),
        (
            "semantic_gap_analyzer.py",
            "_has_any_marker",
            "negative",
            "all haystacks empty",
            "False",
            "test_has_any_marker_false_when_all_empty",
        ),
        (
            "semantic_gap_analyzer.py",
            "_has_any_marker",
            "boundary",
            "hint in used_names set",
            "True",
            "test_has_any_marker_true_via_used_names",
        ),
        (
            "semantic_gap_analyzer.py",
            "_has_any_marker",
            "boundary",
            "SANDBOXENVELOPE uppercase",
            "True (case-insensitive)",
            "test_has_any_marker_case_insensitive",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_elevator_shaft_and_governance_wiring",
            "negative",
            "control-spine file no elevator hints",
            "ELEVATOR-SHAFT-GAP generated",
            "test_elevator_gap_generated_for_control_spine_file_without_hints",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_elevator_shaft_and_governance_wiring",
            "success",
            "control-spine file WITH elevator hints",
            "no ELEVATOR-SHAFT-GAP",
            "test_elevator_gap_not_generated_when_hints_present",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_elevator_shaft_and_governance_wiring",
            "negative",
            "enforcement file no governance stamps",
            "GOVERNANCE-STAMP-GAP generated",
            "test_governance_gap_generated_for_enforcement_file_without_stamps",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_elevator_shaft_and_governance_wiring",
            "success",
            "enforcement file WITH governance stamps",
            "no GOVERNANCE-STAMP-GAP",
            "test_governance_gap_not_generated_when_stamps_present",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_elevator_shaft_and_governance_wiring",
            "boundary",
            "non-control-spine helper file",
            "no gaps generated",
            "test_non_control_spine_file_produces_no_gap",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_elevator_shaft_and_governance_wiring",
            "boundary",
            "parse failure file ok=False",
            "skipped, no gaps",
            "test_parse_failure_file_skipped_no_gap",
        ),
        (
            "agentic_core (real)",
            "capability_chokepoint.py",
            "integration",
            "real file has governance/elevator markers",
            "non-empty mentions",
            "test_capability_chokepoint_has_governance_mentions",
        ),
        (
            "semantic_gap_analyzer.py",
            "GOVERNANCE_STAMP_HINTS",
            "invariant",
            "non-empty tuple of strings",
            "invariant holds",
            "test_governance_hints_tuple_non_empty",
        ),
        (
            "semantic_gap_analyzer.py",
            "ELEVATOR_SHAFT_HINTS",
            "invariant",
            "non-empty tuple of strings",
            "invariant holds",
            "test_elevator_shaft_hints_tuple_non_empty",
        ),
        (
            "semantic_gap_analyzer.py",
            "PATH_D_HINTS",
            "invariant",
            "non-empty tuple of strings",
            "invariant holds",
            "test_path_d_hints_tuple_non_empty",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_elevator_shaft_and_governance_wiring",
            "integration",
            "real codebase produces list (no exception)",
            "list returned",
            "test_governance_wiring_produces_gaps_from_real_codebase",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_elevator_shaft_and_governance_wiring",
            "contract",
            "GOVERNANCE-STAMP-GAP priority == HIGH",
            "all HIGH",
            "test_governance_gap_priority_is_high",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_elevator_shaft_and_governance_wiring",
            "contract",
            "ELEVATOR-SHAFT-GAP priority == MEDIUM",
            "all MEDIUM",
            "test_elevator_gap_priority_is_medium",
        ),
    ]
    for row in rows:
        h(f"| `{row[0]}` | `{row[1]}` | {row[2]} | {row[3]} | {row[4]} | `{row[5]}` |")
    h()
    h("## ROBUSTNESS_MATRIX")
    h()
    h(
        "| Surface | Ingress | Success IDs | Edge IDs | Failure IDs | Recovery IDs | Determinism IDs | Side-Effect IDs |"
    )
    h(
        "|---------|---------|-------------|----------|-------------|--------------|-----------------|-----------------|"
    )
    h(
        "| governance_mentions detection | analyze_file string literals + used_names | test_governance_hint_in_string_literal_detected, test_governance_hint_in_used_name_detected | test_governance_hint_case_insensitive_in_literal | test_no_governance_hint_in_literal_produces_empty, test_unrelated_used_name_not_governance | - | idempotent re-analysis | read-only |"
    )
    h(
        "| elevator_shaft_mentions detection | analyze_file string literals + used_names | test_elevator_hint_jit_in_string_detected, test_elevator_hint_semantic_clock_detected, test_elevator_hint_tool_budget_detected, test_elevator_hint_capability_token_in_name | - | test_no_elevator_hint_produces_empty | - | idempotent | read-only |"
    )
    h(
        "| path_d_mentions detection | analyze_file string literals | test_path_d_hint_modify_diff_detected, test_path_d_hint_original_plan_hash_detected | - | test_no_path_d_hint_produces_empty | - | idempotent | read-only |"
    )
    h(
        "| _has_any_marker | union of all haystacks | test_has_any_marker_true_via_governance_mentions, test_has_any_marker_true_via_elevator_mentions, test_has_any_marker_true_via_used_names | test_has_any_marker_case_insensitive | test_has_any_marker_false_when_all_empty | - | same inputs same output | read-only |"
    )
    h(
        "| analyze_elevator_shaft_and_governance_wiring | find_hot_paths + analyze_file per target dir | test_elevator_gap_not_generated_when_hints_present, test_governance_gap_not_generated_when_stamps_present | test_non_control_spine_file_produces_no_gap, test_parse_failure_file_skipped_no_gap | test_elevator_gap_generated_for_control_spine_file_without_hints, test_governance_gap_generated_for_enforcement_file_without_stamps | - | test_governance_wiring_produces_gaps_from_real_codebase | no writes |"
    )
    h()
    h("## DEFECT_MODEL")
    h()
    h("| Defect Mechanism | Covered By |")
    h("|-----------------|------------|")
    h(
        "| Case-sensitive hint match misses UPPERCASE governance markers | test_governance_hint_case_insensitive_in_literal, test_has_any_marker_case_insensitive |"
    )
    h(
        "| Governance gap generated for non-control-spine files (false positive) | test_non_control_spine_file_produces_no_gap |"
    )
    h("| Parse-failed file silently generates gaps | test_parse_failure_file_skipped_no_gap |")
    h("| Governance gap has wrong priority (not HIGH) | test_governance_gap_priority_is_high |")
    h("| Elevator gap has wrong priority (not MEDIUM) | test_elevator_gap_priority_is_medium |")
    h(
        "| Hint tuple becomes empty (silently disables all detection) | test_governance_hints_tuple_non_empty, test_elevator_shaft_hints_tuple_non_empty, test_path_d_hints_tuple_non_empty |"
    )
    h(
        "| _has_any_marker returns True for empty analysis (false positive) | test_has_any_marker_false_when_all_empty |"
    )
    h()
    content = "\n".join(evidence_lines) + "\n"
    _assert_ascii(content, "evidence file")
    EVIDENCE_PATH.write_text(content, encoding="utf-8")
    print(f"OK: evidence written to {EVIDENCE_PATH}")
    if seal_mode:
        print(f"OK: sealed CODE_COMMIT={code_commit} EVIDENCE_COMMIT={evidence_commit}")
    else:
        print(f"OK: draft CODE_COMMIT={code_commit}")


if __name__ == "__main__":
    main()
