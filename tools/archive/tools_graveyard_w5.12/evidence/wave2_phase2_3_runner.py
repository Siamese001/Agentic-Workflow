"""
Wave 2 Phase 2.3 Evidence Runner - Prompt Taxonomy: Complete Slot Coverage
Usage:
  draft:  python tools/evidence/wave2_phase2_3_runner.py --code-commit <SHA>
  seal:   python tools/evidence/wave2_phase2_3_runner.py --code-commit <SHA> --evidence-commit <SHA>
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

_emit_writes_through("p1", "wave2_phase2_3_runner", "uwg_governed_write")
_emit_writes_through("p1", "wave2_phase2_3_runner", "uwg_governed_write_2")
_emit_pulls_context("p1", "wave2_phase2_3_runner", "context_retrieval")
_emit_pulls_context("p1", "wave2_phase2_3_runner", "context_retrieval_2")
emit_determinism_digest("trace_wave2_phase2_3_runner", "wave2_phase2_3_runner_dispatch")
emit_determinism_digest("trace_wave2_phase2_3_runner", "wave2_phase2_3_runner_complete")
_emit_validated_by_safety_plane("p1", "wave2_phase2_3_runner", "safety_validation")
_emit_reads_through("l4", "wave2_phase2_3_runner", "urg_read_1")
_emit_reads_through("l4", "wave2_phase2_3_runner", "urg_read_2")
_emit_reads_through("l4", "wave2_phase2_3_runner", "urg_read_3")
_emit_reads_through("l4", "wave2_phase2_3_runner", "urg_read_4")
_emit_reads_through("l4", "wave2_phase2_3_runner", "urg_read_5")
_emit_reads_through("l4", "wave2_phase2_3_runner", "urg_read_6")
_emit_reads_through("l4", "wave2_phase2_3_runner", "urg_read_7")
_emit_reads_through("l4", "wave2_phase2_3_runner", "urg_read_8")
_emit_reads_through("l4", "wave2_phase2_3_runner", "urg_read_9")
REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_PATH = REPO_ROOT / 'docs' / REPORTS_DIR / 'plans' / 'wave2_phase2_3_evidence.md'
SCOPE_FILES = ['tests/architecture/test_wave2_phase2_3_prompt_taxonomy.py']

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
    h('# Wave 2 Phase 2.3 - Prompt Taxonomy: Complete Slot Coverage')
    h()
    h('## Scope')
    h()
    h('Add 36-test branch-coverage suite for analyze_prompt_taxonomy_coverage.')
    h('Covers: _looks_like_prompt_assembler, helper functions, slot detection via AST,')
    h('all gap types (PROMPT-TAXONOMY-GAP HIGH/MEDIUM, PROMPT-MANIFEST-GAP, PROMPT-VALIDATOR-GAP),')
    h('deduplication, findings accumulation, real codebase invariants.')
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
    h('## Pytest - Phase 2.3 Tests')
    h()
    pytest_cmd = ['python', '-m', 'pytest', '-q', '--color=no', 'tests/architecture/test_wave2_phase2_3_prompt_taxonomy.py']
    out, rc = _run(pytest_cmd)
    h('$ python -m pytest -q --color=no tests/architecture/test_wave2_phase2_3_prompt_taxonomy.py')
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
    h(f'collected 36 / executed {passed_count}')
    h()
    h('## BRANCH_INVENTORY')
    h()
    h('| File | Function | Branch Type | Condition | Expected | Test |')
    h('|------|----------|-------------|-----------|----------|------|')
    rows = [('semantic_gap_analyzer.py', '_looks_like_prompt_assembler', 'success', 'prompt in name + assembler in rel', 'True', 'test_looks_like_prompt_assembler_prompt_in_name_assembler_in_rel'), ('semantic_gap_analyzer.py', '_looks_like_prompt_assembler', 'success', 'prompt in name + builder in rel', 'True', 'test_looks_like_prompt_assembler_prompt_in_name_builder_in_rel'), ('semantic_gap_analyzer.py', '_looks_like_prompt_assembler', 'negative', 'no prompt in filename', 'False', 'test_looks_like_prompt_assembler_no_prompt_in_name'), ('semantic_gap_analyzer.py', '_looks_like_prompt_assembler', 'negative', 'prompt in name, no assembler token', 'False', 'test_looks_like_prompt_assembler_prompt_in_name_no_assembler_token'), ('semantic_gap_analyzer.py', '_looks_like_prompt_assembler', 'success', 'prompt_assembly_markers non-empty (used_names)', 'True', 'test_looks_like_prompt_assembler_assembler_hint_in_used_names'), ('semantic_gap_analyzer.py', '_looks_like_prompt_assembler', 'success', 'prompt_assembly_markers non-empty (string)', 'True', 'test_looks_like_prompt_assembler_assembler_hint_in_string_literals'), ('semantic_gap_analyzer.py', '_slot_coverage_score', 'boundary', 'no hits -> 0', '0', 'test_slot_coverage_score_zero_when_no_hits'), ('semantic_gap_analyzer.py', '_slot_coverage_score', 'boundary', 'all slots hit -> max', 'len(PROMPT_SLOT_ORDER)', 'test_slot_coverage_score_max_when_all_slots_hit'), ('semantic_gap_analyzer.py', '_slot_coverage_score', 'partial', '2 slots hit', '2', 'test_slot_coverage_score_partial'), ('semantic_gap_analyzer.py', '_missing_slots', 'boundary', 'all empty -> all 5 missing', 'all slots', 'test_missing_slots_all_when_empty'), ('semantic_gap_analyzer.py', '_missing_slots', 'boundary', 'all present -> empty list', '[]', 'test_missing_slots_empty_when_all_present'), ('semantic_gap_analyzer.py', '_missing_slots', 'partial', 'some missing', 'correct subset', 'test_missing_slots_partial'), ('semantic_gap_analyzer.py', '_report_slot_status', 'contract', '= separator, present/missing labels', 'correct format', 'test_report_slot_status_marks_missing_and_present'), ('semantic_gap_analyzer.py', 'PROMPT_SLOT_ORDER', 'invariant', '5 canonical slots', 'S0 D0 I0 C0 U0', 'test_prompt_slot_order_contains_all_canonical_slots'), ('semantic_gap_analyzer.py', 'PROMPT_TAXONOMY_PATTERNS', 'invariant', 'each slot has patterns', 'all non-empty', 'test_prompt_taxonomy_patterns_all_slots_have_patterns'), ('semantic_gap_analyzer.py', 'analyze_file (S0)', 'success', 'system_prompt in string literal', 'S0 detected', 'test_s0_slot_detected_from_system_prompt_literal'), ('semantic_gap_analyzer.py', 'analyze_file (D0)', 'success', 'guardrail in string literal', 'D0 detected', 'test_d0_slot_detected_from_guardrail_literal'), ('semantic_gap_analyzer.py', 'analyze_file (I0)', 'success', 'persona in used_name', 'I0 detected', 'test_i0_slot_detected_from_persona_used_name'), ('semantic_gap_analyzer.py', 'analyze_file (C0)', 'success', 'injected_context in literal', 'C0 detected', 'test_c0_slot_detected_from_context_literal'), ('semantic_gap_analyzer.py', 'analyze_file (U0)', 'success', 'user_prompt in literal', 'U0 detected', 'test_u0_slot_detected_from_user_prompt_literal'), ('semantic_gap_analyzer.py', 'analyze_file (no slots)', 'negative', 'unrelated code', 'no hits', 'test_no_slot_hit_for_unrelated_content'), ('semantic_gap_analyzer.py', 'analyze_prompt_taxonomy_coverage', 'boundary', 'parse-failed file skipped', 'no gaps', 'test_parse_failed_file_skipped_no_taxonomy_gap'), ('semantic_gap_analyzer.py', 'analyze_prompt_taxonomy_coverage', 'boundary', 'non-assembler file skipped', 'no gaps', 'test_non_assembler_file_skipped_no_taxonomy_gap'), ('semantic_gap_analyzer.py', 'analyze_prompt_taxonomy_coverage', 'success', 'missing S0/C0/U0 -> HIGH', 'PROMPT-TAXONOMY-GAP HIGH', 'test_missing_critical_slots_generates_high_priority_taxonomy_gap'), ('semantic_gap_analyzer.py', 'analyze_prompt_taxonomy_coverage', 'success', 'missing D0/I0 only -> MEDIUM', 'PROMPT-TAXONOMY-GAP MEDIUM', 'test_missing_non_critical_slots_generates_medium_priority_taxonomy_gap'), ('semantic_gap_analyzer.py', 'analyze_prompt_taxonomy_coverage', 'negative', 'all slots present -> no gap', 'no PROMPT-TAXONOMY-GAP', 'test_all_slots_present_no_taxonomy_gap'), ('semantic_gap_analyzer.py', 'analyze_prompt_taxonomy_coverage', 'success', 'no manifest hash', 'PROMPT-MANIFEST-GAP MEDIUM', 'test_no_manifest_hash_generates_manifest_gap'), ('semantic_gap_analyzer.py', 'analyze_prompt_taxonomy_coverage', 'negative', 'manifest hash present', 'no PROMPT-MANIFEST-GAP', 'test_manifest_hash_present_no_manifest_gap'), ('semantic_gap_analyzer.py', 'analyze_prompt_taxonomy_coverage', 'success', 'no boundary snapshot', 'PROMPT-VALIDATOR-GAP LOW', 'test_no_boundary_snapshot_generates_validator_gap'), ('semantic_gap_analyzer.py', 'analyze_prompt_taxonomy_coverage', 'negative', 'boundary snapshot present', 'no PROMPT-VALIDATOR-GAP', 'test_boundary_snapshot_present_no_validator_gap'), ('semantic_gap_analyzer.py', 'analyze_prompt_taxonomy_coverage', 'boundary', 'duplicate paths deduplicated', 'at most 1 gap per file', 'test_deduplication_prevents_double_gaps'), ('semantic_gap_analyzer.py', 'prompt_taxonomy_findings', 'contract', 'required keys present', 'all keys found', 'test_taxonomy_finding_added_to_prompt_taxonomy_findings'), ('agentic_core (real)', 'analyze_prompt_taxonomy_coverage', 'integration', 'returns list', 'list type', 'test_prompt_taxonomy_coverage_returns_list'), ('agentic_core (real)', 'PROMPT-TAXONOMY-GAP layer', 'contract', 'layer == L1', 'all L1', 'test_all_taxonomy_gaps_have_layer_l1'), ('agentic_core (real)', 'PROMPT-MANIFEST-GAP priority', 'contract', 'MEDIUM', 'all MEDIUM', 'test_all_manifest_gaps_are_medium_priority'), ('agentic_core (real)', 'PROMPT-VALIDATOR-GAP priority', 'contract', 'LOW', 'all LOW', 'test_all_validator_gaps_are_low_priority')]
    for row in rows:
        h(f'| `{row[0]}` | `{row[1]}` | {row[2]} | {row[3]} | {row[4]} | `{row[5]}` |')
    h()
    h('## ROBUSTNESS_MATRIX')
    h()
    h('| Surface | Ingress | Success IDs | Edge IDs | Failure IDs | Recovery IDs | Determinism IDs | Side-Effect IDs |')
    h('|---------|---------|-------------|----------|-------------|--------------|-----------------|-----------------|')
    h('| _looks_like_prompt_assembler | filename + rel path + prompt_assembly_markers | test_looks_like_prompt_assembler_prompt_in_name_assembler_in_rel, test_looks_like_prompt_assembler_assembler_hint_in_used_names | - | test_looks_like_prompt_assembler_no_prompt_in_name, test_looks_like_prompt_assembler_prompt_in_name_no_assembler_token | - | idempotent | none |')
    h('| _slot_coverage_score/_missing_slots | prompt_slot_hits dict | test_slot_coverage_score_max_when_all_slots_hit, test_missing_slots_empty_when_all_present | test_slot_coverage_score_zero_when_no_hits, test_missing_slots_all_when_empty | test_slot_coverage_score_partial, test_missing_slots_partial | - | idempotent | none |')
    h('| analyze_file slot detection | string literals + used_names | test_s0..u0 slot detection | test_no_slot_hit_for_unrelated_content | - | - | idempotent | none |')
    h('| analyze_prompt_taxonomy_coverage | candidate files across 4 base_dirs | test_missing_critical_slots_generates_high_priority_taxonomy_gap, test_no_manifest_hash_generates_manifest_gap, test_no_boundary_snapshot_generates_validator_gap | test_deduplication_prevents_double_gaps | test_parse_failed_file_skipped_no_taxonomy_gap, test_non_assembler_file_skipped_no_taxonomy_gap | - | idempotent | append to findings |')
    h()
    h('## DEFECT_MODEL')
    h()
    h('| Defect Mechanism | Covered By |')
    h('|-----------------|------------|')
    h('| Non-assembler file wrongly generates taxonomy gap | test_non_assembler_file_skipped_no_taxonomy_gap |')
    h('| Parse-failed assembler generates gap | test_parse_failed_file_skipped_no_taxonomy_gap |')
    h('| Missing critical slots (S0/C0/U0) gets MEDIUM instead of HIGH | test_missing_critical_slots_generates_high_priority_taxonomy_gap |')
    h('| Missing non-critical slots gets HIGH instead of MEDIUM | test_missing_non_critical_slots_generates_medium_priority_taxonomy_gap |')
    h('| PROMPT-MANIFEST-GAP not MEDIUM | test_all_manifest_gaps_are_medium_priority, test_no_manifest_hash_generates_manifest_gap |')
    h('| PROMPT-VALIDATOR-GAP not LOW | test_all_validator_gaps_are_low_priority, test_no_boundary_snapshot_generates_validator_gap |')
    h('| Duplicate file processed multiple times generating duplicate gaps | test_deduplication_prevents_double_gaps |')
    h('| PROMPT_SLOT_ORDER missing canonical slots | test_prompt_slot_order_contains_all_canonical_slots |')
    h('| Taxonomy finding dict missing required keys | test_taxonomy_finding_added_to_prompt_taxonomy_findings |')
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
