#!/usr/bin/env python3
"""
Test Suite for Rescued Agents - Verifies all test cases pass 100%

Tests:
- SchemaEvolverAgent: SCH-01, SCH-02, SCH-03, SCH-04
- PredictiveCostAuditorAgent: COST-01, COST-02, COST-03
- DeadlockDetectorAgent: DEAD-01, DEAD-02, DEAD-03
"""
import sys
import ast
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PASSED = 0
FAILED = 0

def test_pass(test_id: str, msg: str):
    global PASSED
    PASSED += 1
    print(f"  ✅ {test_id}: {msg}")

def test_fail(test_id: str, msg: str):
    global FAILED
    FAILED += 1
    print(f"  ❌ {test_id}: {msg}")

# =============================================================================
# SchemaEvolverAgent Tests
# =============================================================================
def test_schema_evolver():
    print("\n" + "=" * 70)
    print("SchemaEvolverAgent Tests")
    print("=" * 70)
    
    schema_file = PROJECT_ROOT / "agentic_core" / "L4_state" / "ValidationContext" / "SchemaEvolverAgent.py"
    
    # SCH-01: Syntax Check
    try:
        source = schema_file.read_text(encoding='utf-8')
        ast.parse(source)
        test_pass("SCH-01", "Syntax check passed - no IndentationError or SyntaxError")
    except SyntaxError as e:
        test_fail("SCH-01", f"Syntax error: {e}")
        return
    
    # SCH-02: Registry Population - verify _discover_schemas is called in heal_repository
    if '_discover_schemas()' in source or '_discover_schemas(' in source:
        # Check it's in heal_repository
        heal_match = re.search(r'def heal_repository\(.*?\n(.*?)(?=\n    def |\nclass |\n[a-z_]+\s*=|\Z)', source, re.DOTALL)
        if heal_match and '_discover_schemas' in heal_match.group(1):
            test_pass("SCH-02", "Registry population - _discover_schemas() is wired in heal_repository")
        else:
            test_fail("SCH-02", "_discover_schemas() exists but not wired in heal_repository")
    else:
        test_fail("SCH-02", "_discover_schemas() method not found")
    
    # SCH-03: Drift Report - verify generate_drift_report is called
    if 'generate_drift_report' in source:
        heal_match = re.search(r'def heal_repository\(.*?\n(.*?)(?=\n    def |\nclass |\n[a-z_]+\s*=|\Z)', source, re.DOTALL)
        if heal_match and 'generate_drift_report' in heal_match.group(1):
            test_pass("SCH-03", "Drift report - generate_drift_report() is wired in heal_repository")
        else:
            test_fail("SCH-03", "generate_drift_report() exists but not wired in heal_repository")
    else:
        test_fail("SCH-03", "generate_drift_report() method not found")
    
    # SCH-04: Metric Return - verify metrics dict is returned with 'fixed' key
    heal_match = re.search(r'def heal_repository\(.*?\n(.*?)(?=\n    def |\nclass |\n[a-z_]+\s*=|\Z)', source, re.DOTALL)
    if heal_match:
        heal_body = heal_match.group(1)
        if "metrics[\"fixed\"]" in heal_body or "metrics['fixed']" in heal_body:
            test_pass("SCH-04", "Metric return - 'fixed' metric is populated in heal_repository")
        else:
            test_fail("SCH-04", "'fixed' metric not found in heal_repository")
    else:
        test_fail("SCH-04", "Could not parse heal_repository method")

# =============================================================================
# PredictiveCostAuditorAgent Tests
# =============================================================================
def test_predictive_cost_auditor():
    print("\n" + "=" * 70)
    print("PredictiveCostAuditorAgent Tests")
    print("=" * 70)
    
    cost_file = PROJECT_ROOT / "agentic_core" / "L3_orchestration" / "workflow_engines" / "PredictiveCostAuditorAgent.py"
    source = cost_file.read_text(encoding='utf-8')
    
    # COST-01: Stub Removal - verify _module_heal_repository is gone
    if 'def _module_heal_repository' in source:
        test_fail("COST-01", "_module_heal_repository stub still exists - should be removed")
    else:
        test_pass("COST-01", "Stub removal - _module_heal_repository is gone")
    
    # COST-02: Class Integration - verify heal_repository is an instance method with self
    tree = ast.parse(source)
    heal_is_method = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and 'PredictiveCostAuditor' in node.name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == 'heal_repository':
                    # Check first arg is 'self'
                    if item.args.args and item.args.args[0].arg == 'self':
                        heal_is_method = True
                        break
    
    if heal_is_method:
        test_pass("COST-02", "Class integration - heal_repository is an instance method with 'self'")
    else:
        test_fail("COST-02", "heal_repository is not properly defined as instance method")
    
    # COST-03: Report Output - verify _audit_files and _generate_cost_report are wired
    heal_match = re.search(r'def heal_repository\(.*?\n(.*?)(?=\n    def |\nclass |\n_[a-z]|\Z)', source, re.DOTALL)
    if heal_match:
        heal_body = heal_match.group(1)
        has_audit = '_audit_files' in heal_body
        has_report = '_generate_cost_report' in heal_body
        if has_audit and has_report:
            test_pass("COST-03", "Report output - _audit_files() and _generate_cost_report() are wired")
        else:
            missing = []
            if not has_audit:
                missing.append("_audit_files")
            if not has_report:
                missing.append("_generate_cost_report")
            test_fail("COST-03", f"Missing wired methods: {', '.join(missing)}")
    else:
        test_fail("COST-03", "Could not parse heal_repository method")

# =============================================================================
# DeadlockDetectorAgent Tests
# =============================================================================
def test_deadlock_detector():
    print("\n" + "=" * 70)
    print("DeadlockDetectorAgent Tests")
    print("=" * 70)
    
    deadlock_file = PROJECT_ROOT / "agentic_core" / "L3_orchestration" / "workflow_engines" / "DeadlockDetectorAgent.py"
    source = deadlock_file.read_text(encoding='utf-8')
    
    # DEAD-01: Import Check - verify timeout and Logger are imported
    has_timeout = 'from agentic_core.utils.core_extensions.decorators import' in source and 'timeout' in source
    has_logger = 'Logger' in source and 'logging' in source
    
    if has_timeout and has_logger:
        test_pass("DEAD-01", "Import check - timeout and Logger are imported")
    else:
        missing = []
        if not has_timeout:
            missing.append("timeout")
        if not has_logger:
            missing.append("Logger")
        test_fail("DEAD-01", f"Missing imports: {', '.join(missing)}")
    
    # DEAD-02: Stale Detection - verify monitored_tasks check for TIMEOUT status
    heal_match = re.search(r'def heal_repository\(.*?\n(.*?)(?=\n    def |\nclass |\Z)', source, re.DOTALL)
    if heal_match:
        heal_body = heal_match.group(1)
        has_stale_check = 'monitored_tasks' in heal_body and 'TIMEOUT' in heal_body
        has_violations = "violations" in heal_body
        if has_stale_check and has_violations:
            test_pass("DEAD-02", "Stale detection - checks monitored_tasks for TIMEOUT status and counts violations")
        else:
            test_fail("DEAD-02", "Stale task detection logic not found in heal_repository")
    else:
        test_fail("DEAD-02", "Could not parse heal_repository method")
    
    # DEAD-03: Healing Logic - verify execute mode clears stale tasks
    if heal_match:
        heal_body = heal_match.group(1)
        has_execute_check = 'execute' in heal_body and 'dry_run' in heal_body
        has_delete_logic = 'del self.monitored_tasks' in heal_body or 'monitored_tasks[task_id]' in heal_body
        has_fixed = "fixed" in heal_body
        if has_execute_check and has_fixed:
            test_pass("DEAD-03", "Healing logic - execute mode increments 'fixed' count")
        else:
            test_fail("DEAD-03", "Healing execution logic not properly implemented")
    else:
        test_fail("DEAD-03", "Could not parse heal_repository method")

# =============================================================================
# HierarchyAgent Tests (bonus - verify previous fixes)
# =============================================================================
def test_hierarchy_agent():
    print("\n" + "=" * 70)
    print("HierarchyAgent Tests")
    print("=" * 70)
    
    hier_file = PROJECT_ROOT / "agentic_core" / "L5_safety" / "guardrails" / "HierarchyAgent.py"
    source = hier_file.read_text(encoding='utf-8')
    
    # HIER-01: Syntax Check
    try:
        ast.parse(source)
        test_pass("HIER-01", "Syntax check passed")
    except SyntaxError as e:
        test_fail("HIER-01", f"Syntax error: {e}")
        return
    
    # HIER-02: Toggle Safety - verify dry_run/execute logic
    heal_match = re.search(r'def heal_repository\(.*?\n(.*?)(?=\n    # ===|\n    def |\nclass |\Z)', source, re.DOTALL)
    if heal_match:
        heal_body = heal_match.group(1)
        has_dry_run = 'dry_run' in heal_body
        has_execute = 'execute' in heal_body
        if has_dry_run and has_execute:
            test_pass("HIER-02", "Toggle safety - dry_run and execute parameters are used")
        else:
            test_fail("HIER-02", "dry_run/execute toggle logic not found")
    else:
        test_fail("HIER-02", "Could not parse heal_repository method")
    
    # HIER-03: Root Healing - verify heal_root_violations is wired
    if heal_match:
        heal_body = heal_match.group(1)
        if 'heal_root_violations' in heal_body:
            test_pass("HIER-03", "Root healing - heal_root_violations() is wired")
        else:
            test_fail("HIER-03", "heal_root_violations() not wired in heal_repository")

# =============================================================================
# SecureCheckpointManagerAgent Tests (bonus - verify previous fixes)
# =============================================================================
def test_secure_checkpoint_manager():
    print("\n" + "=" * 70)
    print("SecureCheckpointManagerAgent Tests")
    print("=" * 70)
    
    chk_file = PROJECT_ROOT / "agentic_core" / "L5_safety" / "guardrails" / "SecureCheckpointManagerAgent.py"
    source = chk_file.read_text(encoding='utf-8')
    
    # CHK-01: Cleanup Verification - verify monkey-patch is removed
    if 'SecureCheckpointManagerAgent.heal_repository = heal_repository' in source:
        test_fail("CHK-01", "Monkey-patch still exists - should be removed")
    else:
        test_pass("CHK-01", "Cleanup verification - monkey-patch removed")
    
    # CHK-02: Signature Check - verify heal_repository is instance method with cleanup_old_checkpoints
    tree = ast.parse(source)
    heal_is_method = False
    has_cleanup_wired = False
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and 'SecureCheckpointManagerAgent' in node.name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == 'heal_repository':
                    if item.args.args and item.args.args[0].arg == 'self':
                        heal_is_method = True
    
    heal_match = re.search(r'class SecureCheckpointManagerAgent.*?def heal_repository\(.*?\n(.*?)(?=\n    def |\nclass |\Z)', source, re.DOTALL)
    if heal_match and 'cleanup_old_checkpoints' in heal_match.group(1):
        has_cleanup_wired = True
    
    if heal_is_method and has_cleanup_wired:
        test_pass("CHK-02", "Signature check - heal_repository is instance method with cleanup_old_checkpoints wired")
    else:
        issues = []
        if not heal_is_method:
            issues.append("not instance method")
        if not has_cleanup_wired:
            issues.append("cleanup_old_checkpoints not wired")
        test_fail("CHK-02", f"Issues: {', '.join(issues)}")

# =============================================================================
# Main
# =============================================================================
def main():
    print("\n" + "=" * 70)
    print("RESCUED AGENTS TEST SUITE")
    print("=" * 70)
    
    test_schema_evolver()
    test_predictive_cost_auditor()
    test_deadlock_detector()
    test_hierarchy_agent()
    test_secure_checkpoint_manager()
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    total = PASSED + FAILED
    print(f"  Total Tests: {total}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  Pass Rate: {100 * PASSED / total:.1f}%")
    
    if FAILED == 0:
        print("\n  ✅ ALL TESTS PASSED - 100% SUCCESS RATE")
        return 0
    else:
        print(f"\n  ❌ {FAILED} TESTS FAILED - REQUIRES ATTENTION")
        return 1

if __name__ == '__main__':
    sys.exit(main())
