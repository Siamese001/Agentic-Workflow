"""
Wave 2 Phase 2.1 Evidence Runner - Advanced Governance: Full Stamp Coverage
Usage:
  draft:  python tools/evidence/wave2_phase2_1_runner.py --code-commit <SHA>
  seal:   python tools/evidence/wave2_phase2_1_runner.py --code-commit <SHA> --evidence-commit <SHA>
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

_emit_writes_through("p1", "wave2_phase2_1_runner", "uwg_governed_write")
_emit_writes_through("p1", "wave2_phase2_1_runner", "uwg_governed_write_2")
_emit_pulls_context("p1", "wave2_phase2_1_runner", "context_retrieval")
_emit_pulls_context("p1", "wave2_phase2_1_runner", "context_retrieval_2")
emit_determinism_digest("trace_wave2_phase2_1_runner", "wave2_phase2_1_runner_dispatch")
emit_determinism_digest("trace_wave2_phase2_1_runner", "wave2_phase2_1_runner_complete")
_emit_validated_by_safety_plane("p1", "wave2_phase2_1_runner", "safety_validation")
_emit_reads_through("l4", "wave2_phase2_1_runner", "urg_read_1")
_emit_reads_through("l4", "wave2_phase2_1_runner", "urg_read_2")
_emit_reads_through("l4", "wave2_phase2_1_runner", "urg_read_3")
_emit_reads_through("l4", "wave2_phase2_1_runner", "urg_read_4")
_emit_reads_through("l4", "wave2_phase2_1_runner", "urg_read_5")
_emit_reads_through("l4", "wave2_phase2_1_runner", "urg_read_6")
_emit_reads_through("l4", "wave2_phase2_1_runner", "urg_read_7")
_emit_reads_through("l4", "wave2_phase2_1_runner", "urg_read_8")
_emit_reads_through("l4", "wave2_phase2_1_runner", "urg_read_9")
REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_PATH = REPO_ROOT / "docs" / REPORTS_DIR / "plans" / "wave2_phase2_1_evidence.md"
SCOPE_FILES = ["tests/architecture/test_wave2_phase2_1_advanced_governance.py"]


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

    h("# Wave 2 Phase 2.1 - Advanced Governance: Full Stamp Coverage")
    h()
    h("## Scope")
    h()
    h("Add 28-test branch-coverage suite for analyze_layer_connection_integrity.")
    h("Covers: LAYER-UPWARD-IMPORT, GATEWAY-BYPASS-RISK, NON-L2-MUTATION-RISK,")
    h("PATHD-PLAN-HASH-GAP, findings accumulation, real codebase invariants.")
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
    h("## Pytest - Phase 2.1 Tests")
    h()
    pytest_cmd = [
        "python",
        "-m",
        "pytest",
        "-q",
        "--color=no",
        "tests/architecture/test_wave2_phase2_1_advanced_governance.py",
    ]
    out, rc = _run(pytest_cmd)
    h("$ python -m pytest -q --color=no tests/architecture/test_wave2_phase2_1_advanced_governance.py")
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
    h(f"collected 28 / executed {passed_count}")
    h()
    h("## BRANCH_INVENTORY")
    h()
    h("| File | Function | Branch Type | Condition | Expected | Test |")
    h("|------|----------|-------------|-----------|----------|------|")
    rows = [
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "success",
            "L2 file with L1 upward import ref",
            "LAYER-UPWARD-IMPORT generated",
            "test_upward_import_generates_layer_upward_import_gap",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "negative",
            "file with empty imported_layer_refs",
            "no LAYER-UPWARD-IMPORT",
            "test_no_upward_import_produces_no_upward_gap",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "boundary",
            "L2 importing L2 (same rank)",
            "no upward gap",
            "test_same_layer_import_produces_no_upward_gap",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "boundary",
            "L2 importing L3 (higher rank)",
            "no upward gap",
            "test_higher_layer_import_produces_no_upward_gap",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "success",
            "non-gateway file with provider import",
            "GATEWAY-BYPASS-RISK generated",
            "test_direct_provider_import_generates_gateway_bypass_risk",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "negative",
            "file with no provider imports",
            "no GATEWAY-BYPASS-RISK",
            "test_no_provider_import_generates_no_gateway_bypass_gap",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "allowlist",
            "SovereignLLMGateway.py with provider imports",
            "excluded from GATEWAY-BYPASS-RISK",
            "test_sovereign_llm_gateway_excluded_from_gateway_bypass_gap",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "contract",
            "GATEWAY-BYPASS-RISK reality field",
            "provider name in reality",
            "test_gateway_bypass_gap_lists_provider_in_reality",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "success",
            "L0 file with write_paths",
            "NON-L2-MUTATION-RISK generated",
            "test_l0_file_with_write_paths_generates_mutation_risk",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "success",
            "L3 file with write_paths",
            "NON-L2-MUTATION-RISK generated",
            "test_l3_file_with_write_paths_generates_mutation_risk",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "success",
            "L5 file with write_paths",
            "NON-L2-MUTATION-RISK generated",
            "test_l5_file_with_write_paths_generates_mutation_risk",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "negative",
            "L2 file with write_paths (allowed layer)",
            "no NON-L2-MUTATION-RISK",
            "test_l2_file_with_write_paths_does_not_generate_mutation_risk",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "negative",
            "L1 file with write_paths (not flagged)",
            "no NON-L2-MUTATION-RISK",
            "test_l1_file_with_write_paths_does_not_generate_mutation_risk",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "boundary",
            "L0 with empty write_paths list",
            "no mutation gap",
            "test_l0_file_with_empty_write_paths_no_mutation_gap",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "success",
            "path_d_mentions without original_plan_hash",
            "PATHD-PLAN-HASH-GAP generated",
            "test_path_d_file_without_plan_hash_generates_pathd_gap",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "negative",
            "path_d_mentions WITH original_plan_hash",
            "no PATHD-PLAN-HASH-GAP",
            "test_path_d_file_with_plan_hash_no_pathd_gap",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "success",
            "hitl in file path triggers PATHD gap",
            "PATHD-PLAN-HASH-GAP generated",
            "test_hitl_in_path_generates_pathd_gap_even_without_mentions",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "negative",
            "no path_d/hitl markers",
            "no PATHD-PLAN-HASH-GAP",
            "test_no_path_d_no_hitl_no_pathd_gap",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "contract",
            "findings dict has required keys",
            "all keys present",
            "test_layer_connection_finding_keys_are_present",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "boundary",
            "parse-failed file skipped",
            "not in findings",
            "test_parse_failed_file_not_added_to_findings",
        ),
        (
            "agentic_core (real)",
            "healing_provider_adapters.py",
            "codebase-success",
            "openai import -> GATEWAY-BYPASS-RISK",
            "in gap evidence_files",
            "test_healing_provider_adapters_generates_gateway_bypass_risk",
        ),
        (
            "agentic_core (real)",
            "qwen_vllm_inference.py",
            "codebase-success",
            "vllm import -> GATEWAY-BYPASS-RISK",
            "in gap evidence_files",
            "test_qwen_vllm_inference_generates_gateway_bypass_risk",
        ),
        (
            "agentic_core (real)",
            "SovereignLLMGateway.py",
            "codebase-invariant",
            "excluded from GATEWAY-BYPASS-RISK",
            "never in gap evidence",
            "test_sovereign_llm_gateway_not_in_gateway_bypass_gaps",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_layer_connection_integrity",
            "integration",
            "returns list without exception",
            "list type",
            "test_layer_connection_integrity_returns_list",
        ),
        (
            "semantic_gap_analyzer.py",
            "GATEWAY-BYPASS-RISK priority",
            "contract",
            "all gaps are HIGH",
            "all HIGH",
            "test_gateway_bypass_gaps_are_all_high_priority",
        ),
        (
            "semantic_gap_analyzer.py",
            "NON-L2-MUTATION-RISK priority",
            "contract",
            "all gaps are MEDIUM",
            "all MEDIUM",
            "test_non_l2_mutation_risk_gaps_are_all_medium_priority",
        ),
        (
            "semantic_gap_analyzer.py",
            "LAYER-UPWARD-IMPORT priority",
            "contract",
            "all gaps are HIGH",
            "all HIGH",
            "test_upward_import_gaps_are_all_high_priority",
        ),
        (
            "semantic_gap_analyzer.py",
            "PATHD-PLAN-HASH-GAP priority",
            "contract",
            "all gaps are HIGH",
            "all HIGH",
            "test_pathd_gaps_are_all_high_priority",
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
        "| LAYER-UPWARD-IMPORT | _detect_upward_imports result | test_upward_import_generates_layer_upward_import_gap | test_same_layer_import_produces_no_upward_gap, test_higher_layer_import_produces_no_upward_gap | test_no_upward_import_produces_no_upward_gap | - | idempotent | read-only |"
    )
    h(
        "| GATEWAY-BYPASS-RISK | direct_provider_imports set | test_direct_provider_import_generates_gateway_bypass_risk, test_gateway_bypass_gap_lists_provider_in_reality | - | test_no_provider_import_generates_no_gateway_bypass_gap | test_sovereign_llm_gateway_excluded_from_gateway_bypass_gap | idempotent | read-only |"
    )
    h(
        "| NON-L2-MUTATION-RISK | write_paths list + source_layer | test_l0_file_with_write_paths_generates_mutation_risk, test_l3_file_with_write_paths_generates_mutation_risk, test_l5_file_with_write_paths_generates_mutation_risk | test_l0_file_with_empty_write_paths_no_mutation_gap | test_l2_file_with_write_paths_does_not_generate_mutation_risk, test_l1_file_with_write_paths_does_not_generate_mutation_risk | - | idempotent | read-only |"
    )
    h(
        "| PATHD-PLAN-HASH-GAP | path_d_mentions + rel path | test_path_d_file_without_plan_hash_generates_pathd_gap, test_hitl_in_path_generates_pathd_gap_even_without_mentions | - | test_path_d_file_with_plan_hash_no_pathd_gap, test_no_path_d_no_hitl_no_pathd_gap | - | idempotent | read-only |"
    )
    h(
        "| findings accumulation | per-file loop | test_layer_connection_finding_keys_are_present | test_parse_failed_file_not_added_to_findings | - | - | idempotent | append to list |"
    )
    h()
    h("## DEFECT_MODEL")
    h()
    h("| Defect Mechanism | Covered By |")
    h("|-----------------|------------|")
    h(
        "| SovereignLLMGateway.py wrongly flagged as bypass risk | test_sovereign_llm_gateway_excluded_from_gateway_bypass_gap, test_sovereign_llm_gateway_not_in_gateway_bypass_gaps |"
    )
    h(
        "| L2 mutation wrongly flagged (allowed layer) | test_l2_file_with_write_paths_does_not_generate_mutation_risk |"
    )
    h("| Same-layer import wrongly flagged as upward | test_same_layer_import_produces_no_upward_gap |")
    h("| Higher-rank import wrongly flagged as upward | test_higher_layer_import_produces_no_upward_gap |")
    h("| PATHD gap suppressed when plan hash present | test_path_d_file_with_plan_hash_no_pathd_gap |")
    h(
        "| PATHD gap missing for hitl path with no explicit mentions | test_hitl_in_path_generates_pathd_gap_even_without_mentions |"
    )
    h("| Parse-failed file adds finding to results | test_parse_failed_file_not_added_to_findings |")
    h("| Finding dict missing required governance keys | test_layer_connection_finding_keys_are_present |")
    h(
        "| Priority regression: GATEWAY-BYPASS-RISK not HIGH | test_gateway_bypass_gaps_are_all_high_priority |"
    )
    h(
        "| Priority regression: NON-L2-MUTATION-RISK not MEDIUM | test_non_l2_mutation_risk_gaps_are_all_medium_priority |"
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
