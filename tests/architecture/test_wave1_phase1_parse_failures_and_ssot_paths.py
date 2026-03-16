"""
Wave 1 Phase 1.1 — Parse Failure Remediation & SSOT Path Correctness

Branch inventory:
  SSOTFolderCleanupAgent._load_ssot_config
    - success: imports resolve inside method body (no SyntaxError)
    - negative: module-level import placement would cause SyntaxError
  forensic_discovery_prep try-block
    - success: import block is indented inside try (no SyntaxError)
    - negative: unindented import inside try causes SyntaxError
  run_guardian_hierarchy_compliance.scan_missing_structure
    - success: import block is indented inside function body (no SyntaxError)
    - negative: unindented import inside function causes SyntaxError
  ARCHITECTURE_COMPONENT_RULES write_gateway path
    - success: path resolves to L2_execution/tools/write_gateway.py and exists
    - negative: old wrong path (L2_execution/write_gateway.py) must NOT exist
  ARCHITECTURE_COMPONENT_RULES meta_learning_pipeline path
    - success: path resolves to utils/meta_learning_engine_util.py and exists
    - negative: old wrong path (system_learning/...) must NOT exist
  ARCHITECTURE_COMPONENT_RULES all components
    - success: all 5 rule paths exist
    - negative: any rule referencing a non-existent file is a gap
  Analyzer component presence output
    - success: write_gateway row shows exists=True
    - success: meta_learning_pipeline row shows exists=True
    - negative: no component row should show "missing file"
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L0_ROUTING_DIR,
    L2_EXECUTION_DIR,
    SYSTEM_LEARNING_DIR,
    TOOLS_DIR,
)
from agentic_core.L5_safety.enforcement.import_guard import get_import_guard
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_wave1_phase1_parse_failures_and_ssot_paths")
_emit_applies_guardrail("p0", "test_wave1_phase1_parse_failures_and_ssot_paths", "p0_governance")
_emit_reads_policy_state("p0", "test_wave1_phase1_parse_failures_and_ssot_paths", "policy_binding")
_emit_snapshots_state("p0", "test_wave1_phase1_parse_failures_and_ssot_paths", "state_snapshot")
emit_replay_key("p0", "test_wave1_phase1_parse_failures_and_ssot_paths")
emit_determinism_digest("p0", "test_wave1_phase1_parse_failures_and_ssot_paths")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTIC_CORE = REPO_ROOT / AGENTIC_CORE_DIR
PARSE_FAILURE_FILES = [AGENTIC_CORE / L0_ROUTING_DIR / 'reasoning' / 'SSOTFolderCleanupAgent.py', AGENTIC_CORE / L0_ROUTING_DIR / 'scripts' / 'forensic_discovery_prep.py', AGENTIC_CORE / L0_ROUTING_DIR / 'scripts' / 'run_guardian_hierarchy_compliance.py']
WRITE_GATEWAY_CORRECT = AGENTIC_CORE / L2_EXECUTION_DIR / TOOLS_DIR / 'write_gateway.py'
WRITE_GATEWAY_WRONG = AGENTIC_CORE / L2_EXECUTION_DIR / 'write_gateway.py'
META_LEARNING_CORRECT = AGENTIC_CORE / 'utils' / 'meta_learning_engine_util.py'
META_LEARNING_WRONG = AGENTIC_CORE / SYSTEM_LEARNING_DIR / 'pipelines' / 'meta_learning_pipeline.py'

def _ast_parse_ok(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding='utf-8'))
        return (True, '')
    except SyntaxError as exc:
        return (False, str(exc))

def _ast_parse_raises(source: str) -> bool:
    try:
        ast.parse(source)
        return False
    except SyntaxError:
        return True

@pytest.mark.architecture
@pytest.mark.parametrize('filepath', PARSE_FAILURE_FILES, ids=[p.name for p in PARSE_FAILURE_FILES])
def test_parse_failure_file_parses_cleanly(filepath):
    """Success: each formerly-broken file must now parse without SyntaxError."""
    assert filepath.exists(), f'File missing: {filepath}'
    ok, err = _ast_parse_ok(filepath)
    assert ok, f'{filepath.name} still has a SyntaxError: {err}'

@pytest.mark.architecture
def test_unindented_import_inside_method_raises_syntax_error():
    """Negative control: import at column-0 inside method body is a SyntaxError."""
    broken = 'class Foo:\n    def bar(self):\n        pass\nfrom os import path\n'
    broken_regression = 'class Foo:\n    def bar(self):\n        """doc"""\nfrom os import path\n        self.x = 1\n'
    assert _ast_parse_raises(broken_regression), 'Expected SyntaxError for unindented import inside method body'

@pytest.mark.architecture
def test_unindented_import_inside_try_raises_syntax_error():
    """Negative control: import at col-0 inside try: block is a SyntaxError."""
    broken = 'try:\nfrom os import path\nexcept ImportError:\n    pass\n'
    assert _ast_parse_raises(broken), 'Expected SyntaxError for unindented import inside try block'

@pytest.mark.architecture
def test_unindented_import_inside_function_raises_syntax_error():
    """Negative control: import at col-0 inside function body is a SyntaxError."""
    broken = 'def foo():\n    """doc"""\nfrom os import path\n    x = 1\n'
    assert _ast_parse_raises(broken), 'Expected SyntaxError for unindented import inside function body'

@pytest.mark.architecture
def test_ssot_folder_cleanup_agent_import_is_inside_method():
    """Success: _load_ssot_config import is indented (inside method body)."""
    src = PARSE_FAILURE_FILES[0].read_text(encoding='utf-8')
    tree = ast.parse(src)
    lines = src.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and ('L0_routing.config' in node.module):
            line_text = lines[node.lineno - 1]
            assert line_text.startswith(' ') or line_text.startswith('\t'), f'Import at line {node.lineno} is not indented: {line_text!r}'
            return
    pytest.fail('Could not find L0_routing.config import in SSOTFolderCleanupAgent.py')

@pytest.mark.architecture
def test_forensic_discovery_prep_import_is_inside_try():
    """Success: the L0_routing.config import in forensic_discovery_prep is inside try block."""
    src = PARSE_FAILURE_FILES[1].read_text(encoding='utf-8')
    tree = ast.parse(src)
    lines = src.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for child in ast.walk(node):
                if isinstance(child, ast.ImportFrom) and child.module and ('L0_routing.config' in child.module):
                    line_text = lines[child.lineno - 1]
                    assert line_text.startswith('    '), f'Import at line {child.lineno} is not 4-space indented: {line_text!r}'
                    return
    pytest.fail('Could not find L0_routing.config import inside try block in forensic_discovery_prep.py')

@pytest.mark.architecture
def test_run_guardian_hierarchy_compliance_import_is_inside_function():
    """Success: the L0_routing.config import is inside scan_missing_structure body."""
    src = PARSE_FAILURE_FILES[2].read_text(encoding='utf-8')
    tree = ast.parse(src)
    lines = src.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'scan_missing_structure':
            for child in ast.walk(node):
                if isinstance(child, ast.ImportFrom) and child.module and ('L0_routing.config' in child.module):
                    line_text = lines[child.lineno - 1]
                    assert line_text.startswith('    '), f'Import at line {child.lineno} is not indented: {line_text!r}'
                    return
    pytest.fail('Could not find L0_routing.config import inside scan_missing_structure in run_guardian_hierarchy_compliance.py')

@pytest.mark.architecture
def test_write_gateway_correct_path_exists():
    """Success: write_gateway lives at L2_execution/tools/write_gateway.py."""
    assert WRITE_GATEWAY_CORRECT.exists(), f'write_gateway not found at correct path: {WRITE_GATEWAY_CORRECT}'

@pytest.mark.architecture
def test_meta_learning_pipeline_correct_path_exists():
    """Success: meta_learning engine lives at utils/meta_learning_engine_util.py."""
    assert META_LEARNING_CORRECT.exists(), f'meta_learning engine not found at correct path: {META_LEARNING_CORRECT}'

@pytest.mark.architecture
def test_write_gateway_wrong_path_does_not_exist():
    """Negative control: the old wrong path L2_execution/write_gateway.py must not exist."""
    assert not WRITE_GATEWAY_WRONG.exists(), f'write_gateway found at stale/wrong path: {WRITE_GATEWAY_WRONG} — analyzer would report false-missing and rule must be updated.'

@pytest.mark.architecture
def test_meta_learning_wrong_path_does_not_exist():
    """Negative control: system_learning/pipelines/meta_learning_pipeline.py must not exist."""
    assert not META_LEARNING_WRONG.exists(), f'Unexpected file at stale path: {META_LEARNING_WRONG} — analyzer rule already corrected but this file should not exist.'

@pytest.mark.architecture
def test_all_architecture_component_rule_paths_exist():
    """Success: every rule in ARCHITECTURE_COMPONENT_RULES points to an existing file."""
    sys.path.insert(0, str(REPO_ROOT))
    import importlib
    get_import_guard().check(operation='import_module', module_name='tools.semantic_gap_analyzer')
    analyzer = importlib.import_module('tools.semantic_gap_analyzer')
    missing = []
    for rule in analyzer.ARCHITECTURE_COMPONENT_RULES:
        if not rule['path'].exists():
            missing.append(f"{rule['key']} -> {rule['path']}")
    assert not missing, 'ARCHITECTURE_COMPONENT_RULES contains rules pointing to non-existent files:\n' + '\n'.join(missing)

@pytest.mark.architecture
def test_all_architecture_component_rule_paths_parse_cleanly():
    """Success: every rule path can be AST-parsed without SyntaxError."""
    sys.path.insert(0, str(REPO_ROOT))
    import importlib
    get_import_guard().check(operation='import_module', module_name='tools.semantic_gap_analyzer')
    analyzer = importlib.import_module('tools.semantic_gap_analyzer')
    failures = []
    for rule in analyzer.ARCHITECTURE_COMPONENT_RULES:
        p = rule['path']
        if p.exists():
            ok, err = _ast_parse_ok(p)
            if not ok:
                failures.append(f"{rule['key']}: {err}")
    assert not failures, 'Some SSOT component files have parse errors:\n' + '\n'.join(failures)

@pytest.mark.architecture
def test_analyzer_reports_no_missing_component_files():
    """Success: running analyze_architecture_component_presence() finds all components."""
    sys.path.insert(0, str(REPO_ROOT))
    import importlib
    get_import_guard().check(operation='import_module', module_name='tools.semantic_gap_analyzer')
    analyzer_mod = importlib.import_module('tools.semantic_gap_analyzer')
    analyzer = analyzer_mod.SemanticGapAnalyzer()
    gaps = analyzer.analyze_architecture_component_presence()
    missing_gaps = [g for g in gaps if 'missing' in g.reality.lower() and 'missing file' in g.reality.lower()]
    assert not missing_gaps, 'Analyzer still reports missing SSOT component files:\n' + '\n'.join(f'  {g.gap_id}: {g.reality}' for g in missing_gaps)

@pytest.mark.architecture
def test_analyzer_write_gateway_finding_shows_present():
    """Success: architecture_component_findings for write_gateway shows exists=True."""
    sys.path.insert(0, str(REPO_ROOT))
    import importlib
    get_import_guard().check(operation='import_module', module_name='tools.semantic_gap_analyzer')
    analyzer_mod = importlib.import_module('tools.semantic_gap_analyzer')
    analyzer = analyzer_mod.SemanticGapAnalyzer()
    analyzer.analyze_architecture_component_presence()
    findings = {f['component']: f for f in analyzer.architecture_component_findings}
    assert 'write_gateway' in findings, 'write_gateway not in architecture_component_findings'
    assert findings['write_gateway']['exists'] is True, f"write_gateway exists=False: {findings['write_gateway']}"

@pytest.mark.architecture
def test_analyzer_meta_learning_pipeline_finding_shows_present():
    """Success: architecture_component_findings for meta_learning_pipeline shows exists=True."""
    sys.path.insert(0, str(REPO_ROOT))
    import importlib
    get_import_guard().check(operation='import_module', module_name='tools.semantic_gap_analyzer')
    analyzer_mod = importlib.import_module('tools.semantic_gap_analyzer')
    analyzer = analyzer_mod.SemanticGapAnalyzer()
    analyzer.analyze_architecture_component_presence()
    findings = {f['component']: f for f in analyzer.architecture_component_findings}
    assert 'meta_learning_pipeline' in findings, 'meta_learning_pipeline not in architecture_component_findings'
    assert findings['meta_learning_pipeline']['exists'] is True, f"meta_learning_pipeline exists=False: {findings['meta_learning_pipeline']}"

@pytest.mark.architecture
def test_analyzer_no_component_finding_shows_missing_file():
    """Negative control: no component finding should have signals_present='missing file'."""
    sys.path.insert(0, str(REPO_ROOT))
    import importlib
    get_import_guard().check(operation='import_module', module_name='tools.semantic_gap_analyzer')
    analyzer_mod = importlib.import_module('tools.semantic_gap_analyzer')
    analyzer = analyzer_mod.SemanticGapAnalyzer()
    analyzer.analyze_architecture_component_presence()
    bad = [f for f in analyzer.architecture_component_findings if f['signals_present'] == 'missing file']
    assert not bad, "Components still report 'missing file':\n" + '\n'.join(f"  {f['component']}: {f['file']}" for f in bad)

@pytest.mark.architecture
def test_ast_parse_ok_returns_true_for_valid_source():
    """Success: _ast_parse_ok reports True for a minimal valid file."""
    tmp = Path(__file__).parent / '_tmp_valid_parse_test.py'
    tmp.write_text('x = 1\n', encoding='utf-8')
    try:
        ok, err = _ast_parse_ok(tmp)
        assert ok is True
        assert err == ''
    finally:
        tmp.unlink(missing_ok=True)

@pytest.mark.architecture
def test_ast_parse_ok_returns_false_for_broken_source():
    """Failure path: _ast_parse_ok reports False for a file with SyntaxError."""
    tmp = Path(__file__).parent / '_tmp_broken_parse_test.py'
    tmp.write_text('def foo(:\n    pass\n', encoding='utf-8')
    try:
        ok, err = _ast_parse_ok(tmp)
        assert ok is False
        assert err != ''
    finally:
        tmp.unlink(missing_ok=True)

@pytest.mark.architecture
def test_ast_parse_ok_empty_file_is_valid():
    """Boundary: empty file is valid Python and should return True."""
    tmp = Path(__file__).parent / '_tmp_empty_parse_test.py'
    tmp.write_text('', encoding='utf-8')
    try:
        ok, err = _ast_parse_ok(tmp)
        assert ok is True
    finally:
        tmp.unlink(missing_ok=True)
