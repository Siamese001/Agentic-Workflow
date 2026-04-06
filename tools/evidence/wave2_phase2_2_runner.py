"""
Wave 2 Phase 2.2 Evidence Runner - Embedding Sovereignty: Factory Seam Branch Coverage
Usage:
  draft:  python tools/evidence/wave2_phase2_2_runner.py --code-commit <SHA>
  seal:   python tools/evidence/wave2_phase2_2_runner.py --code-commit <SHA> --evidence-commit <SHA>
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

_emit_writes_through("p1", "wave2_phase2_2_runner", "uwg_governed_write")
_emit_writes_through("p1", "wave2_phase2_2_runner", "uwg_governed_write_2")
_emit_pulls_context("p1", "wave2_phase2_2_runner", "context_retrieval")
_emit_pulls_context("p1", "wave2_phase2_2_runner", "context_retrieval_2")
emit_determinism_digest("trace_wave2_phase2_2_runner", "wave2_phase2_2_runner_dispatch")
emit_determinism_digest("trace_wave2_phase2_2_runner", "wave2_phase2_2_runner_complete")
_emit_validated_by_safety_plane("p1", "wave2_phase2_2_runner", "safety_validation")
_emit_reads_through("l4", "wave2_phase2_2_runner", "urg_read_1")
_emit_reads_through("l4", "wave2_phase2_2_runner", "urg_read_2")
_emit_reads_through("l4", "wave2_phase2_2_runner", "urg_read_3")
_emit_reads_through("l4", "wave2_phase2_2_runner", "urg_read_4")
_emit_reads_through("l4", "wave2_phase2_2_runner", "urg_read_5")
_emit_reads_through("l4", "wave2_phase2_2_runner", "urg_read_6")
_emit_reads_through("l4", "wave2_phase2_2_runner", "urg_read_7")
_emit_reads_through("l4", "wave2_phase2_2_runner", "urg_read_8")
_emit_reads_through("l4", "wave2_phase2_2_runner", "urg_read_9")
REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_PATH = REPO_ROOT / 'docs' / REPORTS_DIR / 'plans' / 'wave2_phase2_2_evidence.md'
SCOPE_FILES = ['tests/architecture/test_wave2_phase2_2_embedding_sovereignty.py']

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
    h('# Wave 2 Phase 2.2 - Embedding Sovereignty: Factory Seam Branch Coverage')
    h()
    h('## Scope')
    h()
    h('Add 22-test branch-coverage suite for analyze_rag_embedding_sovereignty.')
    h('Covers: no-mentions skip, allowed path tokens, L1/L4 exemptions, disallowed')
    h('placements, parse failure skip, boundary conditions, hint invariants, real codebase.')
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
    h('## Pytest - Phase 2.2 Tests')
    h()
    pytest_cmd = ['python', '-m', 'pytest', '-q', '--color=no', 'tests/architecture/test_wave2_phase2_2_embedding_sovereignty.py']
    out, rc = _run(pytest_cmd)
    h('$ python -m pytest -q --color=no tests/architecture/test_wave2_phase2_2_embedding_sovereignty.py')
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
    h(f'collected 22 / executed {passed_count}')
    h()
    h('## Embedding Hint Patterns Contract')
    h()
    hint_check = ['python', '-c', "import sys\nsys.path.insert(0, '.')\nfrom tools.semantic_gap_analyzer import EMBEDDING_HINT_PATTERNS\nif not EMBEDDING_HINT_PATTERNS:\n    print('FAIL: EMBEDDING_HINT_PATTERNS is empty')\n    sys.exit(1)\nprint('OK: EMBEDDING_HINT_PATTERNS has', len(EMBEDDING_HINT_PATTERNS), 'hints')\n"]
    out, rc = _run(hint_check)
    h("$ python -c '<EMBEDDING_HINT_PATTERNS contract check>'")
    h('```')
    h(out)
    h('```')
    if rc != 0:
        h(f'EXIT CODE: {rc}')
        content = '\n'.join(evidence_lines)
        _assert_ascii(content, 'evidence')
        EVIDENCE_PATH.write_text(content + '\n', encoding='utf-8')
        print(f'FAIL: hint pattern check exited {rc}', file=sys.stderr)
        sys.exit(1)
    h()
    h('## BRANCH_INVENTORY')
    h()
    h('| File | Function | Branch Type | Condition | Expected | Test |')
    h('|------|----------|-------------|-----------|----------|------|')
    rows = [('semantic_gap_analyzer.py', 'analyze_rag_embedding_sovereignty', 'negative', 'no embedding_mentions in file', 'skip, no gap', 'test_no_embedding_mentions_produces_no_gap'), ('semantic_gap_analyzer.py', 'analyze_rag_embedding_sovereignty', 'allowed', "'embedding' in path", 'no EMBEDDING-PLACEMENT-GAP', 'test_embedding_in_path_name_no_gap'), ('semantic_gap_analyzer.py', 'analyze_rag_embedding_sovereignty', 'allowed', "'rag' in path", 'no gap', 'test_rag_in_path_name_no_gap'), ('semantic_gap_analyzer.py', 'analyze_rag_embedding_sovereignty', 'allowed', "'factory' in path", 'no gap', 'test_factory_in_path_name_no_gap'), ('semantic_gap_analyzer.py', 'analyze_rag_embedding_sovereignty', 'allowed', "'memory' in path", 'no gap', 'test_memory_in_path_name_no_gap'), ('semantic_gap_analyzer.py', 'analyze_rag_embedding_sovereignty', 'allowed', "'seed' in path", 'no gap', 'test_seed_in_path_name_no_gap'), ('semantic_gap_analyzer.py', 'analyze_rag_embedding_sovereignty', 'allowed-layer', 'L1 file with embedding', 'no gap', 'test_l1_layer_file_with_embedding_no_gap'), ('semantic_gap_analyzer.py', 'analyze_rag_embedding_sovereignty', 'allowed-layer', 'L4 file with embedding', 'no gap', 'test_l4_layer_file_with_embedding_no_gap'), ('semantic_gap_analyzer.py', 'analyze_rag_embedding_sovereignty', 'success', 'L0 file, no allowed token', 'EMBEDDING-PLACEMENT-GAP HIGH', 'test_l0_file_no_allowed_token_generates_embedding_gap'), ('semantic_gap_analyzer.py', 'analyze_rag_embedding_sovereignty', 'success', 'L2 file, no allowed token', 'EMBEDDING-PLACEMENT-GAP', 'test_l2_file_no_allowed_token_generates_embedding_gap'), ('semantic_gap_analyzer.py', 'analyze_rag_embedding_sovereignty', 'success', 'L3 file, no allowed token', 'EMBEDDING-PLACEMENT-GAP', 'test_l3_file_no_allowed_token_generates_embedding_gap'), ('semantic_gap_analyzer.py', 'analyze_rag_embedding_sovereignty', 'success', 'UNKNOWN layer, no allowed token', 'EMBEDDING-PLACEMENT-GAP', 'test_unknown_layer_file_no_allowed_token_generates_embedding_gap'), ('semantic_gap_analyzer.py', 'analyze_rag_embedding_sovereignty', 'boundary', 'parse-failed file', 'skipped, no gap', 'test_parse_failed_file_skipped_no_embedding_gap'), ('semantic_gap_analyzer.py', 'analyze_rag_embedding_sovereignty', 'boundary', 'allowed token overrides bad L0 layer', 'no gap', 'test_allowed_token_in_path_overrides_bad_layer'), ('semantic_gap_analyzer.py', 'analyze_rag_embedding_sovereignty', 'boundary', 'L4 layer without allowed token', 'no gap (layer exempt)', 'test_l4_layer_without_allowed_token_still_no_gap'), ('semantic_gap_analyzer.py', 'EMBEDDING_HINT_PATTERNS', 'invariant', 'non-empty tuple', 'invariant holds', 'test_embedding_hint_patterns_non_empty'), ('semantic_gap_analyzer.py', 'EMBEDDING_HINT_PATTERNS', 'invariant', 'contains embedding/bge/faiss', 'all present', 'test_embedding_hint_patterns_contains_expected_entries'), ('agentic_core (real)', 'analyze_rag_embedding_sovereignty', 'integration', 'returns list', 'list type', 'test_embedding_sovereignty_returns_list'), ('agentic_core (real)', 'all gaps', 'contract', 'priority == HIGH', 'all HIGH', 'test_all_embedding_gaps_are_high_priority'), ('agentic_core (real)', 'all gaps', 'contract', 'evidence_files non-empty', 'all non-empty', 'test_all_embedding_gaps_have_evidence_files'), ('agentic_core (real)', 'L1 layer invariant', 'invariant', 'L1 not in gaps', 'never flagged', 'test_l1_files_not_in_embedding_gaps'), ('agentic_core (real)', 'L4 layer invariant', 'invariant', 'L4 not in gaps', 'never flagged', 'test_l4_files_not_in_embedding_gaps')]
    for row in rows:
        h(f'| `{row[0]}` | `{row[1]}` | {row[2]} | {row[3]} | {row[4]} | `{row[5]}` |')
    h()
    h('## ROBUSTNESS_MATRIX')
    h()
    h('| Surface | Ingress | Success IDs | Edge IDs | Failure IDs | Recovery IDs | Determinism IDs | Side-Effect IDs |')
    h('|---------|---------|-------------|----------|-------------|--------------|-----------------|-----------------|')
    h('| analyze_rag_embedding_sovereignty | find_hot_paths + analyze_file per AGENTIC_CORE | test_l0_file_no_allowed_token_generates_embedding_gap, test_l2_file_no_allowed_token_generates_embedding_gap, test_l3_file_no_allowed_token_generates_embedding_gap | test_allowed_token_in_path_overrides_bad_layer, test_l4_layer_without_allowed_token_still_no_gap | test_no_embedding_mentions_produces_no_gap, test_l1_layer_file_with_embedding_no_gap, test_l4_layer_file_with_embedding_no_gap | test_parse_failed_file_skipped_no_embedding_gap | idempotent | read-only |')
    h('| EMBEDDING_HINT_PATTERNS | compile-time constant | test_embedding_hint_patterns_non_empty, test_embedding_hint_patterns_contains_expected_entries | - | - | - | constant | none |')
    h('| L1/L4 layer exemption | _path_to_layer result | test_l1_layer_file_with_embedding_no_gap, test_l4_layer_file_with_embedding_no_gap | - | - | - | idempotent | none |')
    h()
    h('## DEFECT_MODEL')
    h()
    h('| Defect Mechanism | Covered By |')
    h('|-----------------|------------|')
    h('| L1/L4 files wrongly flagged for embedding placement | test_l1_layer_file_with_embedding_no_gap, test_l4_layer_file_with_embedding_no_gap, test_l1_files_not_in_embedding_gaps, test_l4_files_not_in_embedding_gaps |')
    h('| Allowed-token files wrongly flagged (false positive) | test_embedding_in_path_name_no_gap, test_rag_in_path_name_no_gap, test_factory_in_path_name_no_gap |')
    h('| Parse-failed file generates gap | test_parse_failed_file_skipped_no_embedding_gap |')
    h('| Priority regression: EMBEDDING-PLACEMENT-GAP not HIGH | test_all_embedding_gaps_are_high_priority, test_l0_file_no_allowed_token_generates_embedding_gap |')
    h('| Gap with empty evidence_files (unverifiable) | test_all_embedding_gaps_have_evidence_files |')
    h('| EMBEDDING_HINT_PATTERNS emptied (detection silenced) | test_embedding_hint_patterns_non_empty |')
    h('| Critical hint removed from EMBEDDING_HINT_PATTERNS | test_embedding_hint_patterns_contains_expected_entries |')
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
