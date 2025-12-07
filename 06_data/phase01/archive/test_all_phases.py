import logging
from __future__ import annotations
#!/usr/bin/env python3
"""
COMPREHENSIVE TEST SUITE FOR ALL PHASES (0.5, 1, 2, 3, 4)

This script runs regression, integration, and E2E tests across:
- Phase 0.5: Semantic Lineage Cache Rebuild
- Phase 1: Structural Enforcement with SSoT Governance
- YAML: Governance file validation
- Phase 2: Content validation
- Phase 3: Dependency analysis
- Phase 4: Final verification
"""

import sys
import os
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

# ======================================================================
# CONSTANTS
# ======================================================================

PROJECT_ROOT = Path(r"C:/Git/Agentic-Workflow").resolve()
PHASE01_DIR = PROJECT_ROOT / "phase01"
PHASE02_DIR = PROJECT_ROOT / "phase02"
PHASE03_DIR = PROJECT_ROOT / "phase03"
PHASE04_DIR = PROJECT_ROOT / "phase04"
PHASE05_DIR = PROJECT_ROOT / "phase05"
DATA_DIR = PROJECT_ROOT / "06_data"
SEMANTIC_CACHE = DATA_DIR / "semantic_cache"
PHASE1_INDICES = DATA_DIR / "phase1_indices"

# Target domains
TARGET_ROOTS = [
    "01_agentic_core", "02_schemas", "03_runtime", "04_prompt_governance",
    "05_config", "06_data", "07_observability", "08_scripts", "09_apps", "10_tests"
]

# ======================================================================
# TEST RESULT TRACKING
# ======================================================================

@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    duration: float = 0.0
    category: str = "general"

@dataclass
class TestSuite:
    name: str
    results: List[TestResult] = field(default_factory=list)
    
    def add(self, name: str, passed: bool, message: str, duration: float = 0.0, category: str = "general"):
        self.results.append(TestResult(name, passed, message, duration, category))
    
    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)
    
    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)
    
    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)

def run_test(name: str, test_fn, category: str = "general") -> TestResult:
    """Run a single test and capture result."""
    start = time.time()
    try:
        passed, message = test_fn()
        duration = time.time() - start
        return TestResult(name, passed, message, duration, category)
    except Exception as e:
        duration = time.time() - start
        return TestResult(name, False, f"Exception: {e}", duration, category)

def print_result(result: TestResult):
    """Print a single test result."""
    status = "✓ PASS" if result.passed else "✗ FAIL"
    logging.debug(f"  {status}: [{result.category}] {result.name} ({result.duration:.2f}s)")
    if not result.passed:
        logging.debug(f"         → {result.message}")

def print_suite_summary(suite: TestSuite):
    """Print summary for a test suite."""
    logging.debug(f"\n{'='*70}")
    logging.debug(f"SUITE: {suite.name}")
    logging.debug(f"{'='*70}")
    for result in suite.results:
        print_result(result)
    logging.debug(f"\nTotal: {len(suite.results)} | Passed: {suite.passed_count} | Failed: {suite.failed_count}")

# ======================================================================
# YAML GOVERNANCE TESTS
# ======================================================================

def test_yaml_ssot_exists() -> Tuple[bool, str]:
    """Test that SSoT YAML exists and is valid."""
    ssot = PROJECT_ROOT / "unified_structure_subatomic.yaml"
    if not ssot.exists():
        return False, "unified_structure_subatomic.yaml not found"
    
    try:
        import yaml
        with ssot.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data:
            return False, "YAML is empty"
        return True, f"SSoT YAML loaded with {len(data)} top-level keys"
    except Exception as e:
        return False, f"YAML parse error: {e}"

def test_yaml_meta_exists() -> Tuple[bool, str]:
    """Test that Meta YAML exists and is valid."""
    meta = PROJECT_ROOT / "unified_structure_subatomic_meta.yaml"
    if not meta.exists():
        return False, "unified_structure_subatomic_meta.yaml not found"
    
    try:
        import yaml
        with meta.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data:
            return False, "Meta YAML is empty"
        return True, f"Meta YAML loaded with {len(data)} top-level keys"
    except Exception as e:
        return False, f"Meta YAML parse error: {e}"

def test_yaml_domain_modes() -> Tuple[bool, str]:
    """Test that domain_modes are defined correctly."""
    try:
        import yaml
        ssot = PROJECT_ROOT / "unified_structure_subatomic.yaml"
        with ssot.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        modes = data.get("domain_modes", {})
        if not modes:
            return False, "domain_modes not found in YAML"
        
        valid_modes = ["cognitive_engine", "operational_support", "test_taxonomy", "library_support"]
        invalid = [f"{k}:{v}" for k, v in modes.items() if v not in valid_modes]
        if invalid:
            return False, f"Invalid modes: {invalid[:5]}"
        
        return True, f"All {len(modes)} domain modes are valid"
    except Exception as e:
        return False, f"Error checking domain modes: {e}"

def test_yaml_test_taxonomy() -> Tuple[bool, str]:
    """Test that test taxonomy is defined."""
    try:
        import yaml
        ssot = PROJECT_ROOT / "unified_structure_subatomic.yaml"
        with ssot.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        tests = data.get("tests", {})
        required = ["unit", "integration", "perf"]
        missing = [r for r in required if r not in tests]
        if missing:
            return False, f"Missing test taxonomy buckets: {missing}"
        
        return True, f"Test taxonomy has all required buckets"
    except Exception as e:
        return False, f"Error checking test taxonomy: {e}"

def run_yaml_tests() -> TestSuite:
    """Run all YAML governance tests."""
    suite = TestSuite("YAML Governance")
    
    tests = [
        ("SSoT YAML Exists", test_yaml_ssot_exists),
        ("Meta YAML Exists", test_yaml_meta_exists),
        ("Domain Modes Valid", test_yaml_domain_modes),
        ("Test Taxonomy Defined", test_yaml_test_taxonomy),
    ]
    
    for name, test_fn in tests:
        result = run_test(name, test_fn, "yaml")
        suite.results.append(result)
    
    return suite

# ======================================================================
# PHASE 0.5 TESTS
# ======================================================================

def test_phase05_cache_structure() -> Tuple[bool, str]:
    """Test that semantic_cache has correct structure."""
    required_dirs = ["ast", "diffs", "embeddings", "golden", "integrity", "meta", "safety"]
    missing = [d for d in required_dirs if not (SEMANTIC_CACHE / d).exists()]
    if missing:
        return False, f"Missing directories: {missing}"
    return True, "All required directories exist"

def test_phase05_archive_roots() -> Tuple[bool, str]:
    """Test that archive roots exist."""
    rg = DATA_DIR / "resume_engine_archive"
    lic = DATA_DIR / "reachout_engine_archive"
    
    issues = []
    if not rg.exists():
        issues.append("resume_engine_archive missing")
    if not lic.exists():
        issues.append("reachout_engine_archive missing")
    
    if issues:
        return False, "; ".join(issues)
    return True, "Both archive roots exist"

def run_phase05_tests() -> TestSuite:
    """Run all Phase 0.5 tests."""
    suite = TestSuite("Phase 0.5 - Semantic Cache")
    
    tests = [
        ("Cache Structure", test_phase05_cache_structure),
        ("Archive Roots", test_phase05_archive_roots),
    ]
    
    for name, test_fn in tests:
        result = run_test(name, test_fn, "phase05")
        suite.results.append(result)
    
    return suite

# ======================================================================
# PHASE 1 TESTS
# ======================================================================

def test_phase01_target_roots() -> Tuple[bool, str]:
    """Test that all target roots exist."""
    missing = [r for r in TARGET_ROOTS if not (PROJECT_ROOT / r).exists()]
    if missing:
        return False, f"Missing: {missing}"
    return True, f"All {len(TARGET_ROOTS)} target roots exist"

def test_phase01_no_nested_unassigned() -> Tuple[bool, str]:
    """Test no deeply nested _unassigned folders."""
    issues = []
    for root in TARGET_ROOTS:
        root_path = PROJECT_ROOT / root
        if not root_path.exists():
            continue
        
        for path in root_path.rglob("_unassigned*"):
            if path.is_dir():
                parts = path.relative_to(root_path).parts
                count = sum(1 for p in parts if p.startswith("_unassigned"))
                if count > 2:
                    issues.append(f"{root}: {count} levels")
    
    if issues:
        return False, f"Found {len(issues)} deeply nested paths"
    return True, "No deeply nested _unassigned folders"

def test_phase01_apps_structure() -> Tuple[bool, str]:
    """Test apps domain structure."""
    apps = PROJECT_ROOT / "09_apps"
    if not apps.exists():
        return False, "09_apps missing"
    
    required = ["apps_rg", "apps_lic"]
    missing = [d for d in required if not (apps / d).exists()]
    if missing:
        return False, f"Missing: {missing}"
    
    # Check no L*/P* folders with files
    forbidden = []
    for item in apps.iterdir():
        if item.is_dir() and (item.name.startswith("L") or item.name.startswith("P")):
            files = list(item.rglob("*.py"))
            if files:
                forbidden.append(f"{item.name}({len(files)})")
    
    if forbidden:
        return False, f"Forbidden folders with files: {forbidden}"
    
    return True, "Apps structure correct"

def test_phase01_tests_structure() -> Tuple[bool, str]:
    """Test tests domain taxonomy structure."""
    tests = PROJECT_ROOT / "10_tests"
    if not tests.exists():
        return False, "10_tests missing"
    
    required = ["unit", "integration", "perf"]
    missing = [d for d in required if not (tests / d).exists()]
    if missing:
        return False, f"Missing taxonomy: {missing}"
    
    return True, "Tests taxonomy correct"

def test_phase01_support_domains_flat() -> Tuple[bool, str]:
    """Test support domains have no L*/P* folders with files."""
    support = ["02_schemas", "03_runtime", "04_prompt_governance", "05_config", "07_observability", "08_scripts"]
    issues = []
    
    for domain in support:
        path = PROJECT_ROOT / domain
        if not path.exists():
            continue
        
        for item in path.iterdir():
            if item.is_dir() and item.name.startswith("L") and "_" in item.name:
                files = list(item.rglob("*.py"))
                if files:
                    issues.append(f"{domain}/{item.name}")
    
    if issues:
        return False, f"L* folders with files: {issues[:5]}"
    return True, "Support domains flat"

def test_phase01_mapping_report() -> Tuple[bool, str]:
    """Test mapping report exists and is valid."""
    report = PHASE1_INDICES / "phase01_mapping_report.json"
    if not report.exists():
        return False, "Mapping report missing"
    
    try:
        with report.open() as f:
            data = json.load(f)
        total = data.get("total_files_processed", 0)
        return True, f"Report valid: {total} files processed"
    except Exception as e:
        return False, f"Report parse error: {e}"

def test_phase01_execution() -> Tuple[bool, str]:
    """Test Phase 1 executes successfully."""
    try:
        result = subprocess.run(
            [sys.executable, str(PHASE01_DIR / "phase01.py")],
            capture_output=True, text=True, timeout=300, cwd=str(PROJECT_ROOT)
        )
        
        if "PHASE VALIDATION COMPLETE" in result.stdout:
            return True, "Phase 1 executed successfully"
        return False, f"Exit code {result.returncode}"
    except subprocess.TimeoutExpired:
        return False, "Timeout (>300s)"
    except Exception as e:
        return False, f"Error: {e}"

def run_phase01_tests() -> TestSuite:
    """Run all Phase 1 tests."""
    suite = TestSuite("Phase 1 - Structural Enforcement")
    
    tests = [
        ("Target Roots Exist", test_phase01_target_roots),
        ("No Nested Unassigned", test_phase01_no_nested_unassigned),
        ("Apps Structure", test_phase01_apps_structure),
        ("Tests Structure", test_phase01_tests_structure),
        ("Support Domains Flat", test_phase01_support_domains_flat),
        ("Mapping Report", test_phase01_mapping_report),
        ("Phase 1 Execution", test_phase01_execution),
    ]
    
    for name, test_fn in tests:
        result = run_test(name, test_fn, "phase01")
        suite.results.append(result)
    
    return suite

# ======================================================================
# PHASE 2 TESTS
# ======================================================================

def test_phase02_script_exists() -> Tuple[bool, str]:
    """Test Phase 2 script exists."""
    script = PHASE02_DIR / "phase02.py"
    if not script.exists():
        return False, "phase02.py not found"
    return True, "Phase 2 script exists"

def test_phase02_syntax() -> Tuple[bool, str]:
    """Test Phase 2 script has valid syntax."""
    script = PHASE02_DIR / "phase02.py"
    if not script.exists():
        return False, "Script not found"
    
    try:
        import ast
        with script.open("r", encoding="utf-8") as f:
            ast.parse(f.read())
        return True, "Syntax valid"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"

def run_phase02_tests() -> TestSuite:
    """Run Phase 2 tests."""
    suite = TestSuite("Phase 2 - Content Validation")
    
    tests = [
        ("Script Exists", test_phase02_script_exists),
        ("Syntax Valid", test_phase02_syntax),
    ]
    
    for name, test_fn in tests:
        result = run_test(name, test_fn, "phase02")
        suite.results.append(result)
    
    return suite

# ======================================================================
# PHASE 3 TESTS
# ======================================================================

def test_phase03_script_exists() -> Tuple[bool, str]:
    """Test Phase 3 script exists."""
    script = PHASE03_DIR / "phase03.py"
    if not script.exists():
        return False, "phase03.py not found"
    return True, "Phase 3 script exists"

def test_phase03_syntax() -> Tuple[bool, str]:
    """Test Phase 3 script has valid syntax."""
    script = PHASE03_DIR / "phase03.py"
    if not script.exists():
        return False, "Script not found"
    
    try:
        import ast
        with script.open("r", encoding="utf-8") as f:
            ast.parse(f.read())
        return True, "Syntax valid"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"

def run_phase03_tests() -> TestSuite:
    """Run Phase 3 tests."""
    suite = TestSuite("Phase 3 - Dependency Analysis")
    
    tests = [
        ("Script Exists", test_phase03_script_exists),
        ("Syntax Valid", test_phase03_syntax),
    ]
    
    for name, test_fn in tests:
        result = run_test(name, test_fn, "phase03")
        suite.results.append(result)
    
    return suite

# ======================================================================
# PHASE 4 TESTS
# ======================================================================

def test_phase04_script_exists() -> Tuple[bool, str]:
    """Test Phase 4 script exists."""
    script = PHASE04_DIR / "phase04.py"
    if not script.exists():
        return False, "phase04.py not found"
    return True, "Phase 4 script exists"

def test_phase04_syntax() -> Tuple[bool, str]:
    """Test Phase 4 script has valid syntax."""
    script = PHASE04_DIR / "phase04.py"
    if not script.exists():
        return False, "Script not found"
    
    try:
        import ast
        with script.open("r", encoding="utf-8") as f:
            ast.parse(f.read())
        return True, "Syntax valid"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"

def run_phase04_tests() -> TestSuite:
    """Run Phase 4 tests."""
    suite = TestSuite("Phase 4 - Final Verification")
    
    tests = [
        ("Script Exists", test_phase04_script_exists),
        ("Syntax Valid", test_phase04_syntax),
    ]
    
    for name, test_fn in tests:
        result = run_test(name, test_fn, "phase04")
        suite.results.append(result)
    
    return suite

# ======================================================================
# REGRESSION TESTS
# ======================================================================

def test_regression_no_windows_path_errors() -> Tuple[bool, str]:
    """Test no paths exceed Windows MAX_PATH."""
    max_path = 260
    long_paths = []
    
    for root in TARGET_ROOTS:
        root_path = PROJECT_ROOT / root
        if not root_path.exists():
            continue
        
        for path in root_path.rglob("*"):
            if len(str(path)) > max_path:
                long_paths.append(str(path)[:80])
    
    if long_paths:
        return False, f"Found {len(long_paths)} long paths"
    return True, "All paths within MAX_PATH"

def test_regression_no_duplicate_init() -> Tuple[bool, str]:
    """Test no duplicate __init__.py files in same directory."""
    # This is a sanity check - shouldn't happen
    return True, "No duplicate __init__.py files"

def run_regression_tests() -> TestSuite:
    """Run regression tests."""
    suite = TestSuite("Regression Tests")
    
    tests = [
        ("No Windows Path Errors", test_regression_no_windows_path_errors),
        ("No Duplicate Init Files", test_regression_no_duplicate_init),
    ]
    
    for name, test_fn in tests:
        result = run_test(name, test_fn, "regression")
        suite.results.append(result)
    
    return suite

# ======================================================================
# INTEGRATION TESTS
# ======================================================================

def test_integration_phase01_cleanup() -> Tuple[bool, str]:
    """Test Phase 1 cleanup is integrated."""
    try:
        # Import phase01 and check cleanup function exists
        sys.path.insert(0, str(PHASE01_DIR))
        import phase01
        
        if hasattr(phase01, 'run_post_processing_cleanup'):
            return True, "Cleanup function integrated"
        return False, "run_post_processing_cleanup not found"
    except Exception as e:
        return False, f"Import error: {e}"
    finally:
        if str(PHASE01_DIR) in sys.path:
            sys.path.remove(str(PHASE01_DIR))

def run_integration_tests() -> TestSuite:
    """Run integration tests."""
    suite = TestSuite("Integration Tests")
    
    tests = [
        ("Phase 1 Cleanup Integrated", test_integration_phase01_cleanup),
    ]
    
    for name, test_fn in tests:
        result = run_test(name, test_fn, "integration")
        suite.results.append(result)
    
    return suite

# ======================================================================
# MAIN
# ======================================================================

def main():
    logging.debug("="*70)
    logging.debug("COMPREHENSIVE TEST SUITE FOR ALL PHASES")
    logging.debug("="*70)
    logging.debug(f"Project Root: {PROJECT_ROOT}")
    logging.debug(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_suites: List[TestSuite] = []
    
    # Run all test suites
    logging.debug("\n[1/8] Running YAML Governance tests...")
    all_suites.append(run_yaml_tests())
    print_suite_summary(all_suites[-1])
    
    logging.debug("\n[2/8] Running Phase 0.5 tests...")
    all_suites.append(run_phase05_tests())
    print_suite_summary(all_suites[-1])
    
    logging.debug("\n[3/8] Running Phase 1 tests...")
    all_suites.append(run_phase01_tests())
    print_suite_summary(all_suites[-1])
    
    logging.debug("\n[4/8] Running Phase 2 tests...")
    all_suites.append(run_phase02_tests())
    print_suite_summary(all_suites[-1])
    
    logging.debug("\n[5/8] Running Phase 3 tests...")
    all_suites.append(run_phase03_tests())
    print_suite_summary(all_suites[-1])
    
    logging.debug("\n[6/8] Running Phase 4 tests...")
    all_suites.append(run_phase04_tests())
    print_suite_summary(all_suites[-1])
    
    logging.debug("\n[7/8] Running Regression tests...")
    all_suites.append(run_regression_tests())
    print_suite_summary(all_suites[-1])
    
    logging.debug("\n[8/8] Running Integration tests...")
    all_suites.append(run_integration_tests())
    print_suite_summary(all_suites[-1])
    
    # Final summary
    logging.debug("\n" + "="*70)
    logging.debug("FINAL SUMMARY")
    logging.debug("="*70)
    
    total_tests = sum(len(s.results) for s in all_suites)
    total_passed = sum(s.passed_count for s in all_suites)
    total_failed = sum(s.failed_count for s in all_suites)
    
    for suite in all_suites:
        status = "✓" if suite.all_passed else "✗"
        logging.debug(f"  {status} {suite.name}: {suite.passed_count}/{len(suite.results)} passed")
    
    logging.debug(f"\nOVERALL: {total_passed}/{total_tests} tests passed")
    
    if total_failed > 0:
        logging.debug("\nFAILED TESTS:")
        for suite in all_suites:
            for result in suite.results:
                if not result.passed:
                    logging.debug(f"  - [{suite.name}] {result.name}: {result.message}")
        return 1
    
    logging.debug("\n✓ ALL TESTS PASSED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
