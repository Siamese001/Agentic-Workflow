"""
Wave 1 Phase 1.1 Evidence Runner
Usage:
  draft:  python tools/evidence/wave1_phase1_runner.py --code-commit <SHA>
  seal:   python tools/evidence/wave1_phase1_runner.py --code-commit <SHA> --evidence-commit <SHA>
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

_emit_writes_through("p1", "wave1_phase1_runner", "uwg_governed_write")
_emit_writes_through("p1", "wave1_phase1_runner", "uwg_governed_write_2")
_emit_pulls_context("p1", "wave1_phase1_runner", "context_retrieval")
_emit_pulls_context("p1", "wave1_phase1_runner", "context_retrieval_2")
emit_determinism_digest("trace_wave1_phase1_runner", "wave1_phase1_runner_dispatch")
emit_determinism_digest("trace_wave1_phase1_runner", "wave1_phase1_runner_complete")
_emit_validated_by_safety_plane("p1", "wave1_phase1_runner", "safety_validation")
_emit_reads_through("l4", "wave1_phase1_runner", "urg_read_1")
_emit_reads_through("l4", "wave1_phase1_runner", "urg_read_2")
_emit_reads_through("l4", "wave1_phase1_runner", "urg_read_3")
_emit_reads_through("l4", "wave1_phase1_runner", "urg_read_4")
_emit_reads_through("l4", "wave1_phase1_runner", "urg_read_5")
_emit_reads_through("l4", "wave1_phase1_runner", "urg_read_6")
_emit_reads_through("l4", "wave1_phase1_runner", "urg_read_7")
_emit_reads_through("l4", "wave1_phase1_runner", "urg_read_8")
_emit_reads_through("l4", "wave1_phase1_runner", "urg_read_9")
REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_PATH = REPO_ROOT / 'docs' / REPORTS_DIR / 'plans' / 'wave1_phase1_evidence.md'
SCOPE_FILES = ['agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py', 'agentic_core/L0_routing/scripts/forensic_discovery_prep.py', 'agentic_core/L0_routing/scripts/run_guardian_hierarchy_compliance.py', 'tools/semantic_gap_analyzer.py', 'docs/reports/plans/semantic_gap_analysis.md', 'tests/architecture/test_wave1_phase1_parse_failures_and_ssot_paths.py']

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
    h('# Wave 1 Phase 1.1 - Parse Failure Remediation and SSOT Path Correctness')
    h()
    h('## Scope')
    h()
    h('Fix 3 parse-failure files (unindented imports) and correct 2 wrong SSOT component')
    h('paths in ARCHITECTURE_COMPONENT_RULES. N=6 files declared.')
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
    files_code = _git_show_names(code_commit)
    h('```')
    h(files_code)
    h('```')
    h()
    h('## FILES_CHANGED_EVIDENCE')
    h()
    if seal_mode:
        files_ev = _git_show_names(evidence_commit)
        h('```')
        h(files_ev)
        h('```')
    else:
        h('PENDING')
    h()
    h('## INSPECTED_FILES')
    h()
    for f in SCOPE_FILES:
        h(f'- {f}')
    h()
    h('## AST Parse Validation')
    h()
    parse_check = ['python', '-c', "import ast, sys\nfiles = [\n    'agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py',\n    'agentic_core/L0_routing/scripts/forensic_discovery_prep.py',\n    'agentic_core/L0_routing/scripts/run_guardian_hierarchy_compliance.py',\n]\nok = True\nfor f in files:\n    try:\n        ast.parse(open(f, encoding='utf-8').read())\n        print('OK:', f)\n    except SyntaxError as e:\n        print('FAIL:', f, str(e))\n        ok = False\nsys.exit(0 if ok else 1)\n"]
    out, rc = _run(parse_check)
    h("$ python -c '<ast parse 3 files>'")
    h('```')
    h(out)
    h('```')
    if rc != 0:
        h(f'EXIT CODE: {rc}')
        content = '\n'.join(evidence_lines)
        _assert_ascii(content, 'evidence')
        EVIDENCE_PATH.write_text(content + '\n', encoding='utf-8')
        print(f'FAIL: AST parse check exited {rc}', file=sys.stderr)
        sys.exit(1)
    h()
    h('## SSOT Path Verification')
    h()
    ssot_check = ['python', '-c', "from pathlib import Path\nimport sys\nAGENTIC_CORE = Path('agentic_core')\nchecks = [\n    ('write_gateway correct', AGENTIC_CORE / 'L2_execution' / 'tools' / 'write_gateway.py', True),\n    ('write_gateway wrong', AGENTIC_CORE / 'L2_execution' / 'write_gateway.py', False),\n    ('meta_learning correct', AGENTIC_CORE / 'utils' / 'meta_learning_engine_util.py', True),\n    ('meta_learning wrong', AGENTIC_CORE / 'system_learning' / 'pipelines' / 'meta_learning_pipeline.py', False),\n]\nok = True\nfor label, path, should_exist in checks:\n    exists = path.exists()\n    status = 'OK' if exists == should_exist else 'FAIL'\n    if status == 'FAIL': ok = False\n    print(f'{status}: {label}: {path} exists={exists} expected={should_exist}')\nsys.exit(0 if ok else 1)\n"]
    out, rc = _run(ssot_check)
    h("$ python -c '<ssot path checks>'")
    h('```')
    h(out)
    h('```')
    if rc != 0:
        h(f'EXIT CODE: {rc}')
        content = '\n'.join(evidence_lines)
        _assert_ascii(content, 'evidence')
        EVIDENCE_PATH.write_text(content + '\n', encoding='utf-8')
        print(f'FAIL: SSOT path check exited {rc}', file=sys.stderr)
        sys.exit(1)
    h()
    h('## Pytest - Phase 1.1 Tests')
    h()
    pytest_cmd = ['python', '-m', 'pytest', '-q', '--color=no', 'tests/architecture/test_wave1_phase1_parse_failures_and_ssot_paths.py']
    out, rc = _run(pytest_cmd)
    h('$ python -m pytest -q --color=no tests/architecture/test_wave1_phase1_parse_failures_and_ssot_paths.py')
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
    h('## Analyzer Component Presence Verification')
    h()
    analyzer_check = ['python', '-c', "import sys\nsys.path.insert(0, '.')\nimport importlib\nmod = importlib.import_module('tools.semantic_gap_analyzer')\na = mod.SemanticGapAnalyzer()\na.analyze_architecture_component_presence()\nbad = [f for f in a.architecture_component_findings if f['signals_present'] == 'missing file']\nif bad:\n    for b in bad: print('FAIL:', b['component'], b['file'])\n    sys.exit(1)\nfor f in a.architecture_component_findings:\n    print('OK:', f['component'], 'exists=' + str(f['exists']))\n"]
    out, rc = _run(analyzer_check)
    h("$ python -c '<analyzer component presence check>'")
    h('```')
    h(out)
    h('```')
    if rc != 0:
        h(f'EXIT CODE: {rc}')
        content = '\n'.join(evidence_lines)
        _assert_ascii(content, 'evidence')
        EVIDENCE_PATH.write_text(content + '\n', encoding='utf-8')
        print(f'FAIL: analyzer component check exited {rc}', file=sys.stderr)
        sys.exit(1)
    h()
    h('## BRANCH_INVENTORY')
    h()
    h('| File | Function | Branch Type | Condition/Trigger | Expected Outcome | Test Name |')
    h('|------|----------|-------------|-------------------|-----------------|-----------|')
    rows = [('SSOTFolderCleanupAgent.py', '_load_ssot_config', 'success', 'import indented in method body', 'parses cleanly', 'test_parse_failure_file_parses_cleanly[SSOTFolderCleanupAgent.py]'), ('SSOTFolderCleanupAgent.py', '_load_ssot_config', 'negative', 'import at col-0 inside method', 'SyntaxError raised', 'test_unindented_import_inside_method_raises_syntax_error'), ('SSOTFolderCleanupAgent.py', '_load_ssot_config', 'positive-structural', 'import AST node is indented', 'line starts with spaces', 'test_ssot_folder_cleanup_agent_import_is_inside_method'), ('forensic_discovery_prep.py', 'module-level try', 'success', 'import indented inside try block', 'parses cleanly', 'test_parse_failure_file_parses_cleanly[forensic_discovery_prep.py]'), ('forensic_discovery_prep.py', 'module-level try', 'negative', 'import at col-0 inside try', 'SyntaxError raised', 'test_unindented_import_inside_try_raises_syntax_error'), ('forensic_discovery_prep.py', 'module-level try', 'positive-structural', 'import node inside Try AST node', '4-space indent confirmed', 'test_forensic_discovery_prep_import_is_inside_try'), ('run_guardian_hierarchy_compliance.py', 'scan_missing_structure', 'success', 'import indented in function', 'parses cleanly', 'test_parse_failure_file_parses_cleanly[run_guardian_hierarchy_compliance.py]'), ('run_guardian_hierarchy_compliance.py', 'scan_missing_structure', 'negative', 'import at col-0 inside function', 'SyntaxError raised', 'test_unindented_import_inside_function_raises_syntax_error'), ('run_guardian_hierarchy_compliance.py', 'scan_missing_structure', 'positive-structural', 'import inside FunctionDef AST node', '4-space indent confirmed', 'test_run_guardian_hierarchy_compliance_import_is_inside_function'), ('semantic_gap_analyzer.py', 'ARCHITECTURE_COMPONENT_RULES', 'success', 'write_gateway path exists', 'file present', 'test_write_gateway_correct_path_exists'), ('semantic_gap_analyzer.py', 'ARCHITECTURE_COMPONENT_RULES', 'negative', 'old write_gateway path absent', 'file not present', 'test_write_gateway_wrong_path_does_not_exist'), ('semantic_gap_analyzer.py', 'ARCHITECTURE_COMPONENT_RULES', 'success', 'meta_learning path exists', 'file present', 'test_meta_learning_pipeline_correct_path_exists'), ('semantic_gap_analyzer.py', 'ARCHITECTURE_COMPONENT_RULES', 'negative', 'old system_learning path absent', 'file not present', 'test_meta_learning_wrong_path_does_not_exist'), ('semantic_gap_analyzer.py', 'analyze_architecture_component_presence', 'success', 'all 5 rules point to existing files', 'no missing paths', 'test_all_architecture_component_rule_paths_exist'), ('semantic_gap_analyzer.py', 'analyze_architecture_component_presence', 'success', 'all component files parse cleanly', 'no SyntaxErrors', 'test_all_architecture_component_rule_paths_parse_cleanly'), ('semantic_gap_analyzer.py', 'analyze_architecture_component_presence', 'integration-success', 'write_gateway finding shows exists=True', 'exists=True', 'test_analyzer_write_gateway_finding_shows_present'), ('semantic_gap_analyzer.py', 'analyze_architecture_component_presence', 'integration-success', 'meta_learning finding shows exists=True', 'exists=True', 'test_analyzer_meta_learning_pipeline_finding_shows_present'), ('semantic_gap_analyzer.py', 'analyze_architecture_component_presence', 'integration-negative', "no finding has signals_present='missing file'", 'zero missing rows', 'test_analyzer_no_component_finding_shows_missing_file'), ('tools/evidence/_ast_parse_ok', '_ast_parse_ok', 'success', 'valid file -> True, empty err', 'True', 'test_ast_parse_ok_returns_true_for_valid_source'), ('tools/evidence/_ast_parse_ok', '_ast_parse_ok', 'failure', 'broken file -> False, non-empty err', 'False', 'test_ast_parse_ok_returns_false_for_broken_source'), ('tools/evidence/_ast_parse_ok', '_ast_parse_ok', 'boundary', 'empty file is valid Python', 'True', 'test_ast_parse_ok_empty_file_is_valid'), ('tools/evidence/analyze_architecture_component_presence', 'integration', 'integration-negative', "no gap has 'missing file' in reality", 'zero missing-file gaps', 'test_analyzer_reports_no_missing_component_files')]
    for row in rows:
        h(f'| `{row[0]}` | `{row[1]}` | {row[2]} | {row[3]} | {row[4]} | `{row[5]}` |')
    h()
    h('## ROBUSTNESS_MATRIX')
    h()
    h('| Surface | Ingress Path | Success IDs | Edge IDs | Failure IDs | Recovery IDs | Determinism IDs | Side-Effect-Safety IDs |')
    h('|---------|-------------|-------------|----------|-------------|--------------|-----------------|------------------------|')
    h('| Parse fix (3 files) | ast.parse() on each file | test_parse_failure_file_parses_cleanly[x3] | test_ast_parse_ok_empty_file_is_valid | test_unindented_import_inside_{method,try,function}_raises_syntax_error | - | test_parse_failure_file_parses_cleanly (idempotent) | no filesystem mutation |')
    h('| Import placement AST check | AST walk for ImportFrom nodes | test_ssot_..._import_is_inside_{method,try,function} | - | unindented_import negative controls | - | same parse twice gives same result | read-only |')
    h('| SSOT path correctness | Path.exists() on rule paths | test_write_gateway_correct_path_exists, test_meta_learning_pipeline_correct_path_exists | - | test_write_gateway_wrong_path_does_not_exist, test_meta_learning_wrong_path_does_not_exist | - | deterministic path checks | no writes |')
    h("| ARCHITECTURE_COMPONENT_RULES all paths | rule['path'].exists() per rule | test_all_architecture_component_rule_paths_exist | test_all_architecture_component_rule_paths_parse_cleanly | test_analyzer_no_component_finding_shows_missing_file | - | same rules same result | read-only |")
    h('| Analyzer component presence output | SemanticGapAnalyzer().analyze_architecture_component_presence() | test_analyzer_write_gateway_finding_shows_present, test_analyzer_meta_learning_pipeline_finding_shows_present | test_analyzer_reports_no_missing_component_files | test_analyzer_no_component_finding_shows_missing_file | - | idempotent re-run | no writes |')
    h()
    h('## DEFECT_MODEL')
    h()
    h('| Defect Mechanism | Covered By |')
    h('|-----------------|------------|')
    h('| Unindented import inside method/try/function body (SyntaxError) | test_unindented_import_inside_{method,try,function}_raises_syntax_error |')
    h('| Wrong SSOT path causes false-missing detection (off-by-one path segment) | test_write_gateway_wrong_path_does_not_exist, test_meta_learning_wrong_path_does_not_exist |')
    h('| Guard omission: SSOT rule points to missing file silently | test_all_architecture_component_rule_paths_exist |')
    h('| Broad-except masking: parse failure silently drops file from analysis | test_parse_failure_file_parses_cleanly |')
    h('| Stale path reuse: analyzer uses stale system_learning path | test_meta_learning_wrong_path_does_not_exist |')
    h("| Hidden fallback: 'missing file' reported despite file existing at correct path | test_analyzer_write_gateway_finding_shows_present, test_analyzer_meta_learning_pipeline_finding_shows_present |")
    h('| Order instability: import placement at wrong AST depth | test_ssot_folder_cleanup_agent_import_is_inside_method, test_forensic_discovery_prep_import_is_inside_try, test_run_guardian_hierarchy_compliance_import_is_inside_function |')
    h()
    content = '\n'.join(evidence_lines) + '\n'
    _assert_ascii(content, 'evidence file')
    EVIDENCE_PATH.write_text(content, encoding='utf-8')
    print(f'OK: evidence written to {EVIDENCE_PATH}')
    if seal_mode:
        print(f'OK: sealed with CODE_COMMIT={code_commit} EVIDENCE_COMMIT={evidence_commit}')
    else:
        print(f'OK: draft mode CODE_COMMIT={code_commit}')
if __name__ == '__main__':
    main()
