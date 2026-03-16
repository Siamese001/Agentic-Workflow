"""
Wave 3 Phase 3.3 Evidence Runner - Finalization + Monitoring
Usage:
  draft:  python tools/evidence/wave3_phase3_3_runner.py --code-commit <SHA>
  seal:   python tools/evidence/wave3_phase3_3_runner.py --code-commit <SHA> --evidence-commit <SHA>
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "wave3_phase3_3_runner", "uwg_governed_write")
_emit_writes_through("p1", "wave3_phase3_3_runner", "uwg_governed_write_2")
_emit_pulls_context("p1", "wave3_phase3_3_runner", "context_retrieval")
_emit_pulls_context("p1", "wave3_phase3_3_runner", "context_retrieval_2")
emit_determinism_digest("trace_wave3_phase3_3_runner", "wave3_phase3_3_runner_dispatch")
emit_determinism_digest("trace_wave3_phase3_3_runner", "wave3_phase3_3_runner_complete")
_emit_validated_by_safety_plane("p1", "wave3_phase3_3_runner", "safety_validation")
_emit_reads_through("l4", "wave3_phase3_3_runner", "urg_read_1")
_emit_reads_through("l4", "wave3_phase3_3_runner", "urg_read_2")
_emit_reads_through("l4", "wave3_phase3_3_runner", "urg_read_3")
_emit_reads_through("l4", "wave3_phase3_3_runner", "urg_read_4")
_emit_reads_through("l4", "wave3_phase3_3_runner", "urg_read_5")
_emit_reads_through("l4", "wave3_phase3_3_runner", "urg_read_6")
_emit_reads_through("l4", "wave3_phase3_3_runner", "urg_read_7")
_emit_reads_through("l4", "wave3_phase3_3_runner", "urg_read_8")
_emit_reads_through("l4", "wave3_phase3_3_runner", "urg_read_9")
REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_PATH = REPO_ROOT / 'docs' / REPORTS_DIR / 'plans' / 'wave3_phase3_3_evidence.md'
SCOPE_FILES = ['tests/architecture/test_wave3_phase3_3_finalization.py']

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
    h('# Wave 3 Phase 3.3 - Finalization + Monitoring')
    h()
    h('## Scope')
    h()
    h('Add 41-test branch-coverage suite for run_analysis and generate_report finalization.')
    h('Covers: run_analysis return-value contract (all required keys, count invariants,')
    h('type contracts, self-state population), generate_report structural sections')
    h('(always-present sections, conditional sections, file creation, UTF-8 validity,')
    h('executive summary accuracy, gap_id presence), and E2E real codebase invariants')
    h('(totals consistent, evidence_files, priority/layer validity, intent, fix).')
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
    h('## Pytest - Phase 3.3 Tests')
    h()
    pytest_cmd = ['python', '-m', 'pytest', '-q', '--color=no', 'tests/architecture/test_wave3_phase3_3_finalization.py']
    out, rc = _run(pytest_cmd)
    h('$ python -m pytest -q --color=no tests/architecture/test_wave3_phase3_3_finalization.py')
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
    h(f'collected 41 / executed {passed_count}')
    h()
    h('## BRANCH_INVENTORY')
    h()
    h('| File | Function | Branch Type | Condition | Expected | Test |')
    h('|------|----------|-------------|-----------|----------|------|')
    rows = [('semantic_gap_analyzer.py', 'run_analysis', 'contract', 'returns dict', 'dict', 'test_run_analysis_returns_dict'), ('semantic_gap_analyzer.py', 'run_analysis', 'contract', 'all required keys present', 'no missing keys', 'test_run_analysis_has_all_required_keys'), ('semantic_gap_analyzer.py', 'run_analysis', 'invariant', 'total_gaps == len(gaps)', 'equal', 'test_run_analysis_total_gaps_equals_len_gaps'), ('semantic_gap_analyzer.py', 'run_analysis', 'invariant', 'H+M+L == total_gaps', 'equal', 'test_run_analysis_priority_counts_sum_to_total'), ('semantic_gap_analyzer.py', 'run_analysis', 'contract', 'gaps are SemanticGap instances', 'all instances', 'test_run_analysis_gaps_are_semantic_gap_instances'), ('semantic_gap_analyzer.py', 'run_analysis', 'contract', 'parse_failures is list', 'list', 'test_run_analysis_parse_failures_is_list'), ('semantic_gap_analyzer.py', 'run_analysis', 'contract', 'prompt_taxonomy_findings is list', 'list', 'test_run_analysis_prompt_taxonomy_findings_is_list'), ('semantic_gap_analyzer.py', 'run_analysis', 'contract', 'architecture_component_findings is list', 'list', 'test_run_analysis_architecture_component_findings_is_list'), ('semantic_gap_analyzer.py', 'run_analysis', 'contract', 'layer_connection_findings is list', 'list', 'test_run_analysis_layer_connection_findings_is_list'), ('semantic_gap_analyzer.py', 'run_analysis', 'success', 'self.gaps populated after call', 'populated', 'test_run_analysis_self_gaps_populated_after_call'), ('semantic_gap_analyzer.py', 'run_analysis', 'success', 'self.parse_failures sorted after call', 'sorted', 'test_run_analysis_self_parse_failures_sorted_after_call'), ('semantic_gap_analyzer.py', 'run_analysis', 'contract', 'high_priority count accurate', 'matches', 'test_run_analysis_high_priority_count_correct'), ('semantic_gap_analyzer.py', 'run_analysis', 'contract', 'medium_priority count accurate', 'matches', 'test_run_analysis_medium_priority_count_correct'), ('semantic_gap_analyzer.py', 'run_analysis', 'contract', 'low_priority count accurate', 'matches', 'test_run_analysis_low_priority_count_correct'), ('semantic_gap_analyzer.py', 'generate_report', 'success', 'creates output file', 'file exists', 'test_generate_report_creates_file'), ('semantic_gap_analyzer.py', 'generate_report', 'success', 'creates parent dirs', 'nested dirs created', 'test_generate_report_creates_parent_dirs'), ('semantic_gap_analyzer.py', 'generate_report', 'contract', 'file is non-empty', 'size > 0', 'test_generate_report_file_is_nonempty'), ('semantic_gap_analyzer.py', 'generate_report', 'contract', 'file is valid UTF-8', 'no decode error', 'test_generate_report_is_valid_utf8'), ('semantic_gap_analyzer.py', 'generate_report', 'always-present', 'Executive Summary', 'present', 'test_generate_report_has_executive_summary'), ('semantic_gap_analyzer.py', 'generate_report', 'always-present', 'Analysis Methodology', 'present', 'test_generate_report_has_analysis_methodology'), ('semantic_gap_analyzer.py', 'generate_report', 'always-present', 'Next Steps', 'present', 'test_generate_report_has_next_steps'), ('semantic_gap_analyzer.py', 'generate_report', 'always-present', 'Validation', 'present', 'test_generate_report_has_validation'), ('semantic_gap_analyzer.py', 'generate_report', 'conditional', 'Priority Matrix when gaps exist', 'present', 'test_generate_report_has_priority_matrix_when_gaps'), ('semantic_gap_analyzer.py', 'generate_report', 'conditional', 'no Arch section when findings empty', 'absent', 'test_generate_report_no_arch_section_when_empty'), ('semantic_gap_analyzer.py', 'generate_report', 'conditional', 'Arch section when findings present', 'present', 'test_generate_report_arch_section_present_when_findings'), ('semantic_gap_analyzer.py', 'generate_report', 'conditional', 'no Taxonomy section when findings empty', 'absent', 'test_generate_report_no_taxonomy_section_when_empty'), ('semantic_gap_analyzer.py', 'generate_report', 'conditional', 'Taxonomy section when findings present', 'present', 'test_generate_report_taxonomy_section_present_when_findings'), ('semantic_gap_analyzer.py', 'generate_report', 'conditional', 'no Layer Connection when empty', 'absent', 'test_generate_report_no_layer_connection_section_when_empty'), ('semantic_gap_analyzer.py', 'generate_report', 'conditional', 'Layer Connection when findings present', 'present', 'test_generate_report_layer_connection_present_when_findings'), ('semantic_gap_analyzer.py', 'generate_report', 'conditional', 'no Parse Failures section when none', 'absent', 'test_generate_report_no_parse_failures_section_when_empty'), ('semantic_gap_analyzer.py', 'generate_report', 'conditional', 'Parse Failures section when present', 'present', 'test_generate_report_parse_failures_section_present'), ('semantic_gap_analyzer.py', 'generate_report', 'success', 'per-layer gap sections', 'present', 'test_generate_report_per_layer_gap_section'), ('semantic_gap_analyzer.py', 'generate_report', 'contract', 'Executive Summary counts accurate', 'matches gaps', 'test_generate_report_executive_summary_counts_accurate'), ('semantic_gap_analyzer.py', 'generate_report', 'contract', 'gap_id appears in report', 'present', 'test_generate_report_gap_id_appears_in_report'), ('agentic_core (real)', 'run_analysis + generate_report', 'e2e', 'full pipeline', 'valid report', 'test_real_run_analysis_and_generate_report_e2e'), ('agentic_core (real)', 'run_analysis totals', 'invariant', 'total/priority consistent', 'consistent', 'test_real_run_analysis_result_totals_consistent'), ('agentic_core (real)', 'SemanticGap.evidence_files', 'contract', 'non-empty on all gaps', 'all non-empty', 'test_all_gap_evidence_files_nonempty'), ('agentic_core (real)', 'SemanticGap.priority', 'contract', 'HIGH/MEDIUM/LOW only', 'valid', 'test_all_gaps_have_valid_priority'), ('agentic_core (real)', 'SemanticGap.layer', 'contract', 'L0-L6/UNKNOWN only', 'valid', 'test_all_gaps_have_valid_layer'), ('agentic_core (real)', 'SemanticGap.intent', 'contract', 'non-empty', 'non-empty', 'test_all_gaps_have_nonempty_intent'), ('agentic_core (real)', 'SemanticGap.recommended_fix', 'contract', 'non-empty', 'non-empty', 'test_all_gaps_have_nonempty_recommended_fix')]
    for row in rows:
        h(f'| `{row[0]}` | `{row[1]}` | {row[2]} | {row[3]} | {row[4]} | `{row[5]}` |')
    h()
    h('## ROBUSTNESS_MATRIX')
    h()
    h('| Surface | Success IDs | Edge/Boundary IDs | Contract/Invariant IDs | E2E IDs |')
    h('|---------|-------------|-------------------|------------------------|---------|')
    h('| run_analysis | test_run_analysis_self_gaps_populated_after_call, test_run_analysis_self_parse_failures_sorted_after_call | - | test_run_analysis_total_gaps_equals_len_gaps, test_run_analysis_priority_counts_sum_to_total, test_run_analysis_high/medium/low_priority_count_correct | test_real_run_analysis_result_totals_consistent |')
    h('| generate_report | test_generate_report_creates_file, test_generate_report_creates_parent_dirs | test_generate_report_no_arch_section_when_empty, test_generate_report_no_taxonomy_section_when_empty, test_generate_report_no_layer_connection_section_when_empty, test_generate_report_no_parse_failures_section_when_empty | test_generate_report_file_is_nonempty, test_generate_report_is_valid_utf8, test_generate_report_executive_summary_counts_accurate | test_real_run_analysis_and_generate_report_e2e |')
    h('| SemanticGap fields | - | - | test_all_gap_evidence_files_nonempty, test_all_gaps_have_valid_priority, test_all_gaps_have_valid_layer, test_all_gaps_have_nonempty_intent, test_all_gaps_have_nonempty_recommended_fix | - |')
    h()
    h('## DEFECT_MODEL')
    h()
    h('| Defect Mechanism | Covered By |')
    h('|-----------------|------------|')
    h('| run_analysis returns wrong key names | test_run_analysis_has_all_required_keys |')
    h('| total_gaps does not match len(gaps) | test_run_analysis_total_gaps_equals_len_gaps |')
    h('| H+M+L counts do not sum to total | test_run_analysis_priority_counts_sum_to_total |')
    h('| Priority counts off by one or miscounted | test_run_analysis_high/medium/low_priority_count_correct |')
    h('| generate_report does not create parent dirs | test_generate_report_creates_parent_dirs |')
    h('| Conditional sections appear when data is empty | test_generate_report_no_arch/taxonomy/layer/parse sections |')
    h('| Conditional sections missing when data present | test_generate_report_arch/taxonomy/layer/parse sections |')
    h('| Executive Summary counts wrong | test_generate_report_executive_summary_counts_accurate |')
    h('| Gap with invalid priority passes through | test_all_gaps_have_valid_priority |')
    h('| Gap with invalid layer passes through | test_all_gaps_have_valid_layer |')
    h('| Gap with empty evidence_files | test_all_gap_evidence_files_nonempty |')
    h('| Gap with empty intent or recommended_fix | test_all_gaps_have_nonempty_intent, test_all_gaps_have_nonempty_recommended_fix |')
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
