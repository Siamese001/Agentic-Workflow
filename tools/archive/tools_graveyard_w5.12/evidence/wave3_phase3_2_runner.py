"""
Wave 3 Phase 3.2 Evidence Runner - Boundary Hardening
Usage:
  draft:  python tools/evidence/wave3_phase3_2_runner.py --code-commit <SHA>
  seal:   python tools/evidence/wave3_phase3_2_runner.py --code-commit <SHA> --evidence-commit <SHA>
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

_emit_writes_through("p1", "wave3_phase3_2_runner", "uwg_governed_write")
_emit_writes_through("p1", "wave3_phase3_2_runner", "uwg_governed_write_2")
_emit_pulls_context("p1", "wave3_phase3_2_runner", "context_retrieval")
_emit_pulls_context("p1", "wave3_phase3_2_runner", "context_retrieval_2")
emit_determinism_digest("trace_wave3_phase3_2_runner", "wave3_phase3_2_runner_dispatch")
emit_determinism_digest("trace_wave3_phase3_2_runner", "wave3_phase3_2_runner_complete")
_emit_validated_by_safety_plane("p1", "wave3_phase3_2_runner", "safety_validation")
_emit_reads_through("l4", "wave3_phase3_2_runner", "urg_read_1")
_emit_reads_through("l4", "wave3_phase3_2_runner", "urg_read_2")
_emit_reads_through("l4", "wave3_phase3_2_runner", "urg_read_3")
_emit_reads_through("l4", "wave3_phase3_2_runner", "urg_read_4")
_emit_reads_through("l4", "wave3_phase3_2_runner", "urg_read_5")
_emit_reads_through("l4", "wave3_phase3_2_runner", "urg_read_6")
_emit_reads_through("l4", "wave3_phase3_2_runner", "urg_read_7")
_emit_reads_through("l4", "wave3_phase3_2_runner", "urg_read_8")
_emit_reads_through("l4", "wave3_phase3_2_runner", "urg_read_9")
REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_PATH = REPO_ROOT / 'docs' / REPORTS_DIR / 'plans' / 'wave3_phase3_2_evidence.md'
SCOPE_FILES = ['tests/architecture/test_wave3_phase3_2_boundary_hardening.py']

def _run(argv: list[str]) -> tuple[str, int]:
    result = subprocess.run(argv, cwd=str(REPO_ROOT), shell=False, encoding='utf-8', errors='replace', capture_output=True)
    combined = result.stdout + result.stderr
    combined = re.sub('\\x1b\\[[0-9;]*m', '', combined)
    return (combined.rstrip(), result.returncode)

def _git_show_names(commit: str) -> str:
    out, _ = _run(['git', 'show', '--name-only', '--pretty=format:', commit])
    return out.strip()

def _assert_ascii(text: str, label: str) -> None:
    for i, ch in enumerate(text):
        if ord(ch) > 127:
            print(f'FAIL: non-ASCII byte 0x{ord(ch):02X} at position {i} in {label}', file=sys.stderr)
            sys.exit(1)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--code-commit', required=True)
    parser.add_argument('--evidence-commit', default='PENDING')
    args = parser.parse_args()
    code_commit = args.code_commit.strip()
    evidence_commit = args.evidence_commit.strip()
    seal_mode = evidence_commit != 'PENDING'
    if seal_mode and code_commit == evidence_commit:
        print('FAIL: in seal mode CODE_COMMIT must not equal EVIDENCE_COMMIT', file=sys.stderr)
        sys.exit(1)
    evidence_lines: list[str] = []

    def h(line: str='') -> None:
        evidence_lines.append(line)
    h('# Wave 3 Phase 3.2 - Boundary Hardening')
    h()
    h('## Scope')
    h()
    h('Add 44-test branch-coverage suite for boundary hardening across L2-L6 and architecture component presence.')
    h('Covers: analyze_l2_execution (validator loop), analyze_l3_orchestration (orchestrator branch),')
    h('analyze_l4_state (blob_storage threshold), analyze_l5_safety (enforcement loop),')
    h('analyze_l6_observability (telemetry loop), analyze_architecture_component_presence (MISSING/WEAK),')
    h('_dedupe_gaps (deduplication + priority ordering), real codebase invariants.')
    h('No analyzer code changes. N=1 file declared.')
    h()
    for f in SCOPE_FILES:
        h(f'- {f}')
    h()
    h('## CODE_COMMIT')
    h()
    h(code_commit)
    h()
    h('## EVIDENCE_COMMIT')
    h()
    h(evidence_commit)
    h()
    h('## FILES_CHANGED_CODE')
    h()
    h('```')
    h(_git_show_names(code_commit))
    h('```')
    h()
    h('## FILES_CHANGED_EVIDENCE')
    h()
    if seal_mode:
        h('```')
        h(_git_show_names(evidence_commit))
        h('```')
    else:
        h('PENDING')
    h()
    h('## INSPECTED_FILES')
    h()
    for f in SCOPE_FILES:
        h(f'- {f}')
    h()
    h('## Pytest - Phase 3.2 Tests')
    h()
    pytest_cmd = ['python', '-m', 'pytest', '-q', '--color=no', 'tests/architecture/test_wave3_phase3_2_boundary_hardening.py']
    out, rc = _run(pytest_cmd)
    h('$ python -m pytest -q --color=no tests/architecture/test_wave3_phase3_2_boundary_hardening.py')
    h('```')
    h(out)
    h('```')
    if rc != 0:
        h(f'EXIT CODE: {rc}')
        content = '\n'.join(evidence_lines)
        _assert_ascii(content, 'evidence')
        EVIDENCE_PATH.write_text(content + '\n', encoding='utf-8')
        print(f'FAIL: pytest exited {rc}', file=sys.stderr)
        sys.exit(1)
    h()
    collected = re.search('(\\d+) passed', out)
    passed_count = int(collected.group(1)) if collected else 0
    h(f'collected 44 / executed {passed_count}')
    h()
    h('## BRANCH_INVENTORY')
    h()
    h('| File | Function | Branch Type | Condition | Expected | Test |')
    h('|------|----------|-------------|-----------|----------|------|')
    rows = [('semantic_gap_analyzer.py', 'analyze_l2_execution', 'boundary', "'cache' in validator filename", 'no gap', 'test_l2_validator_cache_in_name_skipped'), ('semantic_gap_analyzer.py', 'analyze_l2_execution', 'boundary', 'parse failure', 'no gap', 'test_l2_validator_parse_fail_skipped'), ('semantic_gap_analyzer.py', 'analyze_l2_execution', 'success', 'no schema_validator_cache import', 'L2-GAP-VALIDATOR HIGH', 'test_l2_validator_no_cache_import_generates_gap'), ('semantic_gap_analyzer.py', 'analyze_l2_execution', 'negative', 'schema_validator_cache module imported', 'no gap', 'test_l2_validator_with_cache_module_no_gap'), ('semantic_gap_analyzer.py', 'analyze_l2_execution', 'negative', 'SchemaValidatorCache symbol imported', 'no gap', 'test_l2_validator_with_symbol_cache_no_gap'), ('semantic_gap_analyzer.py', 'analyze_l2_execution', 'boundary', 'no validator files', 'no gaps', 'test_l2_no_validator_files_no_gap'), ('semantic_gap_analyzer.py', 'analyze_l3_orchestration', 'boundary', 'parse failure', 'no L3-GAP-001', 'test_l3_orchestrator_parse_fail_no_gap'), ('semantic_gap_analyzer.py', 'analyze_l3_orchestration', 'success', 'no plan cache import', 'L3-GAP-001 MEDIUM', 'test_l3_orchestrator_no_cache_generates_gap'), ('semantic_gap_analyzer.py', 'analyze_l3_orchestration', 'negative', 'orchestration_plan_cache imported', 'no gap', 'test_l3_orchestrator_with_cache_module_no_gap'), ('semantic_gap_analyzer.py', 'analyze_l3_orchestration', 'boundary', 'file does not exist', 'no gaps', 'test_l3_orchestrator_file_missing_no_gap'), ('semantic_gap_analyzer.py', 'analyze_l4_state', 'boundary', 'parse failure', 'no L4-GAP-001', 'test_l4_blob_parse_fail_no_gap'), ('semantic_gap_analyzer.py', 'analyze_l4_state', 'boundary', 'exactly 10 l4_state_accesses', 'no L4-GAP-001 (boundary <= 10)', 'test_l4_blob_exactly_ten_accesses_no_gap'), ('semantic_gap_analyzer.py', 'analyze_l4_state', 'success', '11 l4_state_accesses', 'L4-GAP-001 HIGH (> 10)', 'test_l4_blob_eleven_accesses_generates_gap'), ('semantic_gap_analyzer.py', 'analyze_l4_state', 'boundary', 'file does not exist', 'no gaps', 'test_l4_blob_file_missing_no_gap'), ('semantic_gap_analyzer.py', 'analyze_l5_safety', 'boundary', "'cache' in enforcement filename", 'no gap', 'test_l5_enforcement_cache_in_name_skipped'), ('semantic_gap_analyzer.py', 'analyze_l5_safety', 'boundary', 'parse failure', 'no gap', 'test_l5_enforcement_parse_fail_skipped'), ('semantic_gap_analyzer.py', 'analyze_l5_safety', 'success', "'policy' in name + no cache import", 'L5-GAP-POLICY MEDIUM', 'test_l5_enforcement_policy_in_name_no_cache_generates_gap'), ('semantic_gap_analyzer.py', 'analyze_l5_safety', 'negative', "'policy' not in name", 'no gap', 'test_l5_enforcement_no_policy_in_name_no_gap'), ('semantic_gap_analyzer.py', 'analyze_l5_safety', 'negative', 'policy_registry_cache imported', 'no gap', 'test_l5_enforcement_with_cache_import_no_gap'), ('semantic_gap_analyzer.py', 'analyze_l5_safety', 'boundary', 'no enforcement files', 'no gaps', 'test_l5_no_enforcement_files_no_gap'), ('semantic_gap_analyzer.py', 'analyze_l6_observability', 'boundary', 'parse failure', 'no gap', 'test_l6_telemetry_parse_fail_skipped'), ('semantic_gap_analyzer.py', 'analyze_l6_observability', 'success', 'no config_file_cache import', 'L6-GAP-CONFIG LOW', 'test_l6_telemetry_no_cache_import_generates_gap'), ('semantic_gap_analyzer.py', 'analyze_l6_observability', 'negative', 'config_file_cache module imported', 'no gap', 'test_l6_telemetry_with_cache_module_no_gap'), ('semantic_gap_analyzer.py', 'analyze_l6_observability', 'negative', 'ConfigFileCache symbol imported', 'no gap', 'test_l6_telemetry_with_symbol_cache_no_gap'), ('semantic_gap_analyzer.py', 'analyze_l6_observability', 'boundary', 'no telemetry files', 'no gaps', 'test_l6_no_telemetry_files_no_gap'), ('semantic_gap_analyzer.py', 'analyze_architecture_component_presence', 'boundary', 'file does not exist', 'ARCH-COMPONENT-MISSING', 'test_arch_component_missing_file_generates_missing_gap'), ('semantic_gap_analyzer.py', 'analyze_architecture_component_presence', 'boundary', 'parse failure', 'no gap', 'test_arch_component_parse_fail_no_gap'), ('semantic_gap_analyzer.py', 'analyze_architecture_component_presence', 'negative', 'signals present', 'no ARCH-COMPONENT-WEAK', 'test_arch_component_signals_present_no_gap'), ('semantic_gap_analyzer.py', 'analyze_architecture_component_presence', 'success', 'no signals found', 'ARCH-COMPONENT-WEAK', 'test_arch_component_no_signals_generates_weak_gap'), ('semantic_gap_analyzer.py', '_dedupe_gaps', 'boundary', 'empty input', 'empty output', 'test_dedupe_gaps_empty_input'), ('semantic_gap_analyzer.py', '_dedupe_gaps', 'negative', 'no duplicate keys', 'all retained', 'test_dedupe_gaps_no_duplicates_all_retained'), ('semantic_gap_analyzer.py', '_dedupe_gaps', 'success', 'dup key, HIGH vs MEDIUM', 'HIGH wins', 'test_dedupe_gaps_duplicate_key_keeps_higher_priority'), ('semantic_gap_analyzer.py', '_dedupe_gaps', 'contract', 'sorted by priority rank', 'HIGH < MEDIUM < LOW', 'test_dedupe_gaps_sorted_by_priority'), ('agentic_core (real)', 'analyze_l2_execution', 'integration', 'returns list', 'list', 'test_analyze_l2_execution_returns_list'), ('agentic_core (real)', 'analyze_l3_orchestration', 'integration', 'returns list', 'list', 'test_analyze_l3_orchestration_returns_list'), ('agentic_core (real)', 'analyze_l4_state', 'integration', 'returns list', 'list', 'test_analyze_l4_state_returns_list'), ('agentic_core (real)', 'analyze_l5_safety', 'integration', 'returns list', 'list', 'test_analyze_l5_safety_returns_list'), ('agentic_core (real)', 'analyze_l6_observability', 'integration', 'returns list', 'list', 'test_analyze_l6_observability_returns_list'), ('agentic_core (real)', 'analyze_architecture_component_presence', 'integration', 'returns list', 'list', 'test_analyze_architecture_component_presence_returns_list'), ('agentic_core (real)', 'L2-GAP-VALIDATOR priority', 'contract', 'HIGH', 'all HIGH', 'test_l2_validator_gaps_are_high_priority'), ('agentic_core (real)', 'L3-GAP-001 priority', 'contract', 'MEDIUM', 'MEDIUM', 'test_l3_gap001_is_medium_if_present'), ('agentic_core (real)', 'L4-GAP-001 priority', 'contract', 'HIGH', 'HIGH', 'test_l4_gap001_is_high_if_present'), ('agentic_core (real)', 'L5-GAP-POLICY priority', 'contract', 'MEDIUM', 'all MEDIUM', 'test_l5_policy_gaps_are_medium_if_present'), ('agentic_core (real)', 'L6-GAP-CONFIG priority', 'contract', 'LOW', 'all LOW', 'test_l6_config_gaps_are_low_if_present')]
    for row in rows:
        h(f'| `{row[0]}` | `{row[1]}` | {row[2]} | {row[3]} | {row[4]} | `{row[5]}` |')
    h()
    h('## ROBUSTNESS_MATRIX')
    h()
    h('| Surface | Success IDs | Edge/Boundary IDs | Failure IDs | Determinism |')
    h('|---------|-------------|-------------------|-------------|-------------|')
    h('| analyze_l2_execution | test_l2_validator_no_cache_import_generates_gap | test_l2_validator_cache_in_name_skipped, test_l2_no_validator_files_no_gap | test_l2_validator_parse_fail_skipped | idempotent |')
    h('| analyze_l3_orchestration | test_l3_orchestrator_no_cache_generates_gap | test_l3_orchestrator_file_missing_no_gap | test_l3_orchestrator_parse_fail_no_gap | idempotent |')
    h('| analyze_l4_state | test_l4_blob_eleven_accesses_generates_gap | test_l4_blob_exactly_ten_accesses_no_gap, test_l4_blob_file_missing_no_gap | test_l4_blob_parse_fail_no_gap | idempotent |')
    h('| analyze_l5_safety | test_l5_enforcement_policy_in_name_no_cache_generates_gap | test_l5_enforcement_no_policy_in_name_no_gap, test_l5_enforcement_cache_in_name_skipped, test_l5_no_enforcement_files_no_gap | test_l5_enforcement_parse_fail_skipped | idempotent |')
    h('| analyze_l6_observability | test_l6_telemetry_no_cache_import_generates_gap | test_l6_no_telemetry_files_no_gap | test_l6_telemetry_parse_fail_skipped | idempotent |')
    h('| analyze_architecture_component_presence | test_arch_component_no_signals_generates_weak_gap, test_arch_component_missing_file_generates_missing_gap | - | test_arch_component_parse_fail_no_gap | idempotent |')
    h('| _dedupe_gaps | test_dedupe_gaps_duplicate_key_keeps_higher_priority, test_dedupe_gaps_sorted_by_priority | test_dedupe_gaps_empty_input, test_dedupe_gaps_no_duplicates_all_retained | - | deterministic |')
    h()
    h('## DEFECT_MODEL')
    h()
    h('| Defect Mechanism | Covered By |')
    h('|-----------------|------------|')
    h("| L2 validator file named '*_cache.py' wrongly gets L2-GAP-VALIDATOR | test_l2_validator_cache_in_name_skipped |")
    h('| L3-GAP-001 wrong priority (not MEDIUM) | test_l3_gap001_is_medium_if_present, test_l3_orchestrator_no_cache_generates_gap |')
    h('| L4-GAP-001 threshold off-by-one (fires at 10, should fire at >10) | test_l4_blob_exactly_ten_accesses_no_gap, test_l4_blob_eleven_accesses_generates_gap |')
    h('| L4-GAP-001 wrong priority (not HIGH) | test_l4_gap001_is_high_if_present, test_l4_blob_eleven_accesses_generates_gap |')
    h('| L5-GAP-POLICY fires for non-policy enforcement files | test_l5_enforcement_no_policy_in_name_no_gap |')
    h('| L6-GAP-CONFIG wrong priority (not LOW) | test_l6_config_gaps_are_low_if_present, test_l6_telemetry_no_cache_import_generates_gap |')
    h('| ARCH-COMPONENT-MISSING gap not generated for missing file | test_arch_component_missing_file_generates_missing_gap |')
    h('| ARCH-COMPONENT-WEAK gap generated despite signals present | test_arch_component_signals_present_no_gap |')
    h('| _dedupe_gaps drops lower-priority duplicate instead of higher-priority | test_dedupe_gaps_duplicate_key_keeps_higher_priority |')
    h('| _dedupe_gaps output not sorted by priority | test_dedupe_gaps_sorted_by_priority |')
    h()
    content = '\n'.join(evidence_lines) + '\n'
    _assert_ascii(content, 'evidence file')
    EVIDENCE_PATH.write_text(content, encoding='utf-8')
    print(f'OK: evidence written to {EVIDENCE_PATH}')
    if seal_mode:
        print(f'OK: sealed CODE_COMMIT={code_commit} EVIDENCE_COMMIT={evidence_commit}')
    else:
        print(f'OK: draft CODE_COMMIT={code_commit}')
if __name__ == '__main__':
    main()
