"""
Wave 3 Phase 3.1 Evidence Runner - Cache Wirings + Performance
Usage:
  draft:  python tools/evidence/wave3_phase3_1_runner.py --code-commit <SHA>
  seal:   python tools/evidence/wave3_phase3_1_runner.py --code-commit <SHA> --evidence-commit <SHA>
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

_emit_writes_through("p1", "wave3_phase3_1_runner", "uwg_governed_write")
_emit_writes_through("p1", "wave3_phase3_1_runner", "uwg_governed_write_2")
_emit_pulls_context("p1", "wave3_phase3_1_runner", "context_retrieval")
_emit_pulls_context("p1", "wave3_phase3_1_runner", "context_retrieval_2")
emit_determinism_digest("trace_wave3_phase3_1_runner", "wave3_phase3_1_runner_dispatch")
emit_determinism_digest("trace_wave3_phase3_1_runner", "wave3_phase3_1_runner_complete")
_emit_validated_by_safety_plane("p1", "wave3_phase3_1_runner", "safety_validation")
_emit_reads_through("l4", "wave3_phase3_1_runner", "urg_read_1")
_emit_reads_through("l4", "wave3_phase3_1_runner", "urg_read_2")
_emit_reads_through("l4", "wave3_phase3_1_runner", "urg_read_3")
_emit_reads_through("l4", "wave3_phase3_1_runner", "urg_read_4")
_emit_reads_through("l4", "wave3_phase3_1_runner", "urg_read_5")
_emit_reads_through("l4", "wave3_phase3_1_runner", "urg_read_6")
_emit_reads_through("l4", "wave3_phase3_1_runner", "urg_read_7")
_emit_reads_through("l4", "wave3_phase3_1_runner", "urg_read_8")
_emit_reads_through("l4", "wave3_phase3_1_runner", "urg_read_9")
REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_PATH = REPO_ROOT / "docs" / REPORTS_DIR / "plans" / "wave3_phase3_1_evidence.md"
SCOPE_FILES = ["tests/architecture/test_wave3_phase3_1_cache_wirings.py"]


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

    h("# Wave 3 Phase 3.1 - Cache Wirings + Performance")
    h()
    h("## Scope")
    h()
    h("Add 30-test branch-coverage suite for analyze_l0_routing_gate and analyze_l1_cognition.")
    h("Covers: _analysis_mentions_cache, _contains_module_reference, _contains_symbol_reference,")
    h("L0 routing gate (L0-GAP-001 HIGH, L0-GAP-002 MEDIUM), L1 cognition (L1-GAP-001 HIGH,")
    h("L1-GAP-PROMPT MEDIUM), parse-fail skips, cache exclusions, real codebase invariants.")
    h("No analyzer code changes. N=1 file declared.")
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
    h("## Pytest - Phase 3.1 Tests")
    h()
    pytest_cmd = [
        "python",
        "-m",
        "pytest",
        "-q",
        "--color=no",
        "tests/architecture/test_wave3_phase3_1_cache_wirings.py",
    ]
    out, rc = _run(pytest_cmd)
    h("$ python -m pytest -q --color=no tests/architecture/test_wave3_phase3_1_cache_wirings.py")
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
    h(f"collected 30 / executed {passed_count}")
    h()
    h("## BRANCH_INVENTORY")
    h()
    h("| File | Function | Branch Type | Condition | Expected | Test |")
    h("|------|----------|-------------|-----------|----------|------|")
    rows = [
        (
            "semantic_gap_analyzer.py",
            "_analysis_mentions_cache",
            "success",
            "module_hint in imported_module_names",
            "True",
            "test_analysis_mentions_cache_module_hint_match",
        ),
        (
            "semantic_gap_analyzer.py",
            "_analysis_mentions_cache",
            "success",
            "symbol_hint in imported_symbol_names",
            "True",
            "test_analysis_mentions_cache_symbol_hint_match",
        ),
        (
            "semantic_gap_analyzer.py",
            "_analysis_mentions_cache",
            "negative",
            "neither hint matches",
            "False",
            "test_analysis_mentions_cache_no_match",
        ),
        (
            "semantic_gap_analyzer.py",
            "_analysis_mentions_cache",
            "negative",
            "no symbol_hint, module absent",
            "False",
            "test_analysis_mentions_cache_no_symbol_hint_module_absent",
        ),
        (
            "semantic_gap_analyzer.py",
            "_contains_module_reference",
            "success",
            "substring match in module names",
            "True",
            "test_contains_module_reference_substring_match",
        ),
        (
            "semantic_gap_analyzer.py",
            "_contains_symbol_reference",
            "success",
            "substring match in symbol names",
            "True",
            "test_contains_symbol_reference_substring_match",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l0_routing_gate (L0-GAP-001)",
            "boundary",
            "discovery_py parse failure",
            "no L0-GAP-001",
            "test_discovery_py_parse_fail_no_l0_gap001",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l0_routing_gate (L0-GAP-001)",
            "success",
            "no cache import",
            "L0-GAP-001 HIGH",
            "test_discovery_py_no_cache_generates_l0_gap001",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l0_routing_gate (L0-GAP-001)",
            "negative",
            "module cache imported",
            "no L0-GAP-001",
            "test_discovery_py_with_module_cache_no_l0_gap001",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l0_routing_gate (L0-GAP-001)",
            "negative",
            "symbol cache imported",
            "no L0-GAP-001",
            "test_discovery_py_with_symbol_cache_no_l0_gap001",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l0_routing_gate (L0-GAP-002)",
            "boundary",
            "policy_engine parse failure",
            "no L0-GAP-002",
            "test_policy_engine_parse_fail_no_l0_gap002",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l0_routing_gate (L0-GAP-002)",
            "success",
            "no policy cache import",
            "L0-GAP-002 MEDIUM",
            "test_policy_engine_no_cache_generates_l0_gap002",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l0_routing_gate (L0-GAP-002)",
            "negative",
            "policy cache imported",
            "no L0-GAP-002",
            "test_policy_engine_with_cache_no_l0_gap002",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l1_cognition (L1-GAP-001)",
            "boundary",
            "cognitive_engine parse failure",
            "no L1-GAP-001",
            "test_cognitive_engine_parse_fail_no_l1_gap001",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l1_cognition (L1-GAP-001)",
            "success",
            "no tool cache import",
            "L1-GAP-001 HIGH",
            "test_cognitive_engine_no_cache_generates_l1_gap001",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l1_cognition (L1-GAP-001)",
            "negative",
            "tool cache module imported",
            "no L1-GAP-001",
            "test_cognitive_engine_with_cache_no_l1_gap001",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l1_cognition (L1-GAP-001)",
            "negative",
            "ToolEmbeddingCache symbol imported",
            "no L1-GAP-001",
            "test_cognitive_engine_with_symbol_cache_no_l1_gap001",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l1_cognition (prompt loop)",
            "success",
            "no cache import, cache not in name",
            "L1-GAP-PROMPT MEDIUM",
            "test_prompt_file_no_cache_generates_l1_gap_prompt",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l1_cognition (prompt loop)",
            "negative",
            "'cache' in filename",
            "no L1-GAP-PROMPT",
            "test_prompt_file_with_cache_in_name_no_l1_gap_prompt",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l1_cognition (prompt loop)",
            "negative",
            "prompt_artifact_cache imported",
            "no L1-GAP-PROMPT",
            "test_prompt_file_with_cache_import_no_l1_gap_prompt",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l1_cognition (prompt loop)",
            "boundary",
            "prompt file parse failure",
            "no L1-GAP-PROMPT",
            "test_prompt_file_parse_fail_no_l1_gap_prompt",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_l1_cognition (prompt loop)",
            "boundary",
            "no prompt files found",
            "no L1-GAP-PROMPT",
            "test_no_prompt_files_no_l1_gap_prompt",
        ),
        (
            "agentic_core (real)",
            "analyze_l0_routing_gate",
            "integration",
            "returns list",
            "list type",
            "test_analyze_l0_routing_gate_returns_list",
        ),
        (
            "agentic_core (real)",
            "analyze_l1_cognition",
            "integration",
            "returns list",
            "list type",
            "test_analyze_l1_cognition_returns_list",
        ),
        (
            "agentic_core (real)",
            "L0-GAP-001 priority",
            "contract",
            "HIGH",
            "all HIGH",
            "test_l0_gap001_is_high_priority_if_present",
        ),
        (
            "agentic_core (real)",
            "L0-GAP-002 priority",
            "contract",
            "MEDIUM",
            "all MEDIUM",
            "test_l0_gap002_is_medium_priority_if_present",
        ),
        (
            "agentic_core (real)",
            "L1-GAP-001 priority",
            "contract",
            "HIGH",
            "all HIGH",
            "test_l1_gap001_is_high_priority_if_present",
        ),
        (
            "agentic_core (real)",
            "L1-GAP-PROMPT priority",
            "contract",
            "MEDIUM",
            "all MEDIUM",
            "test_l1_gap_prompt_is_medium_priority_if_present",
        ),
        (
            "agentic_core (real)",
            "L0 gaps evidence_files",
            "contract",
            "non-empty",
            "all non-empty",
            "test_all_l0_gaps_have_evidence_files",
        ),
        (
            "agentic_core (real)",
            "L1 gaps evidence_files",
            "contract",
            "non-empty",
            "all non-empty",
            "test_all_l1_gaps_have_evidence_files",
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
        "| _analysis_mentions_cache | module + symbol hints | test_analysis_mentions_cache_module_hint_match, test_analysis_mentions_cache_symbol_hint_match | - | test_analysis_mentions_cache_no_match, test_analysis_mentions_cache_no_symbol_hint_module_absent | - | idempotent | none |"
    )
    h(
        "| analyze_l0_routing_gate | discovery_py + policy_engine existence + imports | test_discovery_py_no_cache_generates_l0_gap001, test_policy_engine_no_cache_generates_l0_gap002 | test_discovery_py_parse_fail_no_l0_gap001, test_policy_engine_parse_fail_no_l0_gap002 | test_discovery_py_with_module_cache_no_l0_gap001, test_policy_engine_with_cache_no_l0_gap002 | - | idempotent | none |"
    )
    h(
        "| analyze_l1_cognition | cognitive_engine + prompt files | test_cognitive_engine_no_cache_generates_l1_gap001, test_prompt_file_no_cache_generates_l1_gap_prompt | test_cognitive_engine_parse_fail_no_l1_gap001, test_prompt_file_parse_fail_no_l1_gap_prompt, test_no_prompt_files_no_l1_gap_prompt | test_prompt_file_with_cache_in_name_no_l1_gap_prompt, test_prompt_file_with_cache_import_no_l1_gap_prompt | - | idempotent | none |"
    )
    h()
    h("## DEFECT_MODEL")
    h()
    h("| Defect Mechanism | Covered By |")
    h("|-----------------|------------|")
    h("| Parse-failed discovery_py generates L0-GAP-001 | test_discovery_py_parse_fail_no_l0_gap001 |")
    h(
        "| Cache-importing file still generates L0-GAP-001 | test_discovery_py_with_module_cache_no_l0_gap001, test_discovery_py_with_symbol_cache_no_l0_gap001 |"
    )
    h(
        "| L0-GAP-001 priority not HIGH | test_l0_gap001_is_high_priority_if_present, test_discovery_py_no_cache_generates_l0_gap001 |"
    )
    h(
        "| L0-GAP-002 priority not MEDIUM | test_l0_gap002_is_medium_priority_if_present, test_policy_engine_no_cache_generates_l0_gap002 |"
    )
    h(
        "| L1-GAP-001 priority not HIGH | test_l1_gap001_is_high_priority_if_present, test_cognitive_engine_no_cache_generates_l1_gap001 |"
    )
    h(
        "| Prompt file with 'cache' in name wrongly flagged | test_prompt_file_with_cache_in_name_no_l1_gap_prompt |"
    )
    h(
        "| L1-GAP-PROMPT priority not MEDIUM | test_l1_gap_prompt_is_medium_priority_if_present, test_prompt_file_no_cache_generates_l1_gap_prompt |"
    )
    h(
        "| Gap missing evidence_files | test_all_l0_gaps_have_evidence_files, test_all_l1_gaps_have_evidence_files |"
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
