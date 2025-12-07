import logging
from __future__ import annotations
#!/usr/bin/env python3
"""
END-TO-END TEST SUITE FOR PHASE 0.5 AND PHASE 1

This script runs comprehensive tests for:
- Phase 0.5: Semantic Lineage Cache Rebuild
- Phase 1: Structural Enforcement with SSoT Governance

Test Categories:
1. Pre-condition validation
2. Execution tests
3. Post-condition validation
4. Regression tests
5. Edge case tests
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

# ======================================================================
# CONSTANTS
# ======================================================================

PROJECT_ROOT = Path(r"C:/Git/Agentic-Workflow").resolve()
PHASE01_DIR = PROJECT_ROOT / "phase01"
PHASE05_DIR = PROJECT_ROOT / "phase05"
DATA_DIR = PROJECT_ROOT / "06_data"
SEMANTIC_CACHE = DATA_DIR / "semantic_cache"
PHASE1_INDICES = DATA_DIR / "phase1_indices"

# Target domains for Phase 1
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

@dataclass
class TestSuite:
    name: str
    results: List[TestResult] = field(default_factory=list)
    
    def add(self, name: str, passed: bool, message: str, duration: float = 0.0):
        self.results.append(TestResult(name, passed, message, duration))
    
    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)
    
    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)
    
    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)

# ======================================================================
# TEST UTILITIES
# ======================================================================

def run_test(name: str, test_fn) -> TestResult:
    """Run a single test and capture result."""
    start = time.time()
    try:
        passed, message = test_fn()
        duration = time.time() - start
        return TestResult(name, passed, message, duration)
    except Exception as e:
        duration = time.time() - start
        return TestResult(name, False, f"Exception: {e}", duration)

def print_result(result: TestResult):
    """Print a single test result."""
    status = "✓ PASS" if result.passed else "✗ FAIL"
    logging.debug(f"  {status}: {result.name} ({result.duration:.2f}s)")
    if not result.passed:
        logging.debug(f"         → {result.message}")

def print_suite_summary(suite: TestSuite):
    """Print summary for a test suite."""
    logging.debug(f"\n{'='*60}")
    logging.debug(f"SUITE: {suite.name}")
    logging.debug(f"{'='*60}")
    for result in suite.results:
        print_result(result)
    logging.debug(f"\nTotal: {len(suite.results)} | Passed: {suite.passed_count} | Failed: {suite.failed_count}")

# ======================================================================
# PHASE 0.5 TESTS
# ======================================================================

def test_phase05_cache_structure() -> Tuple[bool, str]:
    """Test that semantic_cache has correct structure."""
    required_dirs = ["ast", "diffs", "embeddings", "golden", "integrity", "meta", "safety"]
    missing = []
    for d in required_dirs:
        if not (SEMANTIC_CACHE / d).exists():
            missing.append(d)
    if missing:
        return False, f"Missing directories: {missing}"
    return True, "All required directories exist"

def test_phase05_meta_exists() -> Tuple[bool, str]:
    """Test that meta directory has required files."""
    meta_dir = SEMANTIC_CACHE / "meta"
    if not meta_dir.exists():
        return False, "meta directory does not exist"
    
    # Check for transaction manifest
    manifest = meta_dir / "transaction_manifest.json"
    if manifest.exists():
        try:
            with manifest.open() as f:
                data = json.load(f)
            return True, f"Transaction manifest exists with {len(data.get('transactions', []))} transactions"
        except Exception as e:
            return False, f"Failed to parse transaction manifest: {e}"
    return True, "Meta directory exists (no manifest yet)"

def test_phase05_archive_roots_exist() -> Tuple[bool, str]:
    """Test that archive roots exist."""
    rg_archive = DATA_DIR / "resume_engine_archive"
    lic_archive = DATA_DIR / "reachout_engine_archive"
    
    issues = []
    if not rg_archive.exists():
        issues.append("resume_engine_archive missing")
    if not lic_archive.exists():
        issues.append("reachout_engine_archive missing")
    
    if issues:
        return False, "; ".join(issues)
    return True, "Both archive roots exist"

def run_phase05_tests() -> TestSuite:
    """Run all Phase 0.5 tests."""
    suite = TestSuite("Phase 0.5 - Semantic Lineage Cache")
    
    tests = [
        ("Cache Structure", test_phase05_cache_structure),
        ("Meta Directory", test_phase05_meta_exists),
        ("Archive Roots", test_phase05_archive_roots_exist),
    ]
    
    for name, test_fn in tests:
        result = run_test(name, test_fn)
        suite.results.append(result)
    
    return suite

# ======================================================================
# PHASE 1 TESTS
# ======================================================================

def test_phase01_yaml_files_exist() -> Tuple[bool, str]:
    """Test that YAML governance files exist."""
    ssot = PROJECT_ROOT / "unified_structure_subatomic.yaml"
    meta = PROJECT_ROOT / "unified_structure_subatomic_meta.yaml"
    
    issues = []
    if not ssot.exists():
        issues.append("unified_structure_subatomic.yaml missing")
    if not meta.exists():
        issues.append("unified_structure_subatomic_meta.yaml missing")
    
    if issues:
        return False, "; ".join(issues)
    return True, "Both YAML files exist"

def test_phase01_target_roots_exist() -> Tuple[bool, str]:
    """Test that all target root directories exist."""
    missing = []
    for root in TARGET_ROOTS:
        if not (PROJECT_ROOT / root).exists():
            missing.append(root)
    
    if missing:
        return False, f"Missing target roots: {missing}"
    return True, f"All {len(TARGET_ROOTS)} target roots exist"

def test_phase01_no_deeply_nested_unassigned() -> Tuple[bool, str]:
    """Test that there are no deeply nested _unassigned folders (>3 levels)."""
    issues = []
    
    for root in TARGET_ROOTS:
        root_path = PROJECT_ROOT / root
        if not root_path.exists():
            continue
        
        for path in root_path.rglob("_unassigned*"):
            if path.is_dir():
                # Count nesting depth of _unassigned folders
                parts = path.relative_to(root_path).parts
                unassigned_count = sum(1 for p in parts if p.startswith("_unassigned"))
                if unassigned_count > 2:
                    issues.append(f"{root}: {path.relative_to(root_path)} has {unassigned_count} nested _unassigned levels")
    
    if issues:
        return False, f"Found {len(issues)} deeply nested _unassigned paths"
    return True, "No deeply nested _unassigned folders found"

def test_phase01_apps_structure() -> Tuple[bool, str]:
    """Test that apps domain has correct structure (apps_rg, apps_lic)."""
    apps_root = PROJECT_ROOT / "09_apps"
    if not apps_root.exists():
        return False, "09_apps directory does not exist"
    
    required = ["apps_rg", "apps_lic"]
    missing = []
    for d in required:
        if not (apps_root / d).exists():
            missing.append(d)
    
    if missing:
        return False, f"Missing apps subdirectories: {missing}"
    
    # Check for forbidden L*/P* folders at root level
    forbidden = []
    for item in apps_root.iterdir():
        if item.is_dir() and (item.name.startswith("L") or item.name.startswith("P")):
            # Check if it contains any files
            files = list(item.rglob("*.py"))
            if files:
                forbidden.append(f"{item.name} ({len(files)} files)")
    
    if forbidden:
        return False, f"Forbidden L*/P* folders with files: {forbidden}"
    
    return True, "Apps structure is correct (apps_rg, apps_lic exist, no forbidden folders with files)"

def test_phase01_tests_structure() -> Tuple[bool, str]:
    """Test that tests domain has correct taxonomy structure."""
    tests_root = PROJECT_ROOT / "10_tests"
    if not tests_root.exists():
        return False, "10_tests directory does not exist"
    
    required = ["unit", "integration", "perf"]
    missing = []
    for d in required:
        if not (tests_root / d).exists():
            missing.append(d)
    
    if missing:
        return False, f"Missing tests taxonomy directories: {missing}"
    
    return True, "Tests taxonomy structure is correct"

def test_phase01_mapping_report() -> Tuple[bool, str]:
    """Test that Phase 1 mapping report exists and is valid."""
    report_path = PHASE1_INDICES / "phase01_mapping_report.json"
    if not report_path.exists():
        return False, "phase01_mapping_report.json does not exist"
    
    try:
        with report_path.open() as f:
            data = json.load(f)
        
        total = data.get("total_files_processed", 0)
        moves = data.get("moves_executed", 0)
        violations = data.get("violations", 0)
        
        return True, f"Report valid: {total} files processed, {moves} moves, {violations} violations"
    except Exception as e:
        return False, f"Failed to parse mapping report: {e}"

def test_phase01_no_windows_path_errors() -> Tuple[bool, str]:
    """Test that no paths exceed Windows MAX_PATH limit."""
    max_path = 260
    long_paths = []
    
    for root in TARGET_ROOTS:
        root_path = PROJECT_ROOT / root
        if not root_path.exists():
            continue
        
        for path in root_path.rglob("*"):
            if len(str(path)) > max_path:
                long_paths.append(str(path)[:100] + "...")
    
    if long_paths:
        return False, f"Found {len(long_paths)} paths exceeding MAX_PATH"
    return True, "All paths within Windows MAX_PATH limit"

def test_phase01_apps_files_routed() -> Tuple[bool, str]:
    """Test that apps files are correctly routed to apps_rg/apps_lic."""
    apps_root = PROJECT_ROOT / "09_apps"
    
    # Count files in apps_rg and apps_lic
    rg_files = list((apps_root / "apps_rg").rglob("*.py")) if (apps_root / "apps_rg").exists() else []
    lic_files = list((apps_root / "apps_lic").rglob("*.py")) if (apps_root / "apps_lic").exists() else []
    
    # Count files in _unassigned_apps_unknown
    unassigned = list((apps_root / "_unassigned_apps_unknown").rglob("*.py")) if (apps_root / "_unassigned_apps_unknown").exists() else []
    
    # Count files in forbidden L*/P* folders
    forbidden_files = []
    for item in apps_root.iterdir():
        if item.is_dir() and (item.name.startswith("L") or item.name.startswith("P")):
            forbidden_files.extend(list(item.rglob("*.py")))
    
    if forbidden_files:
        return False, f"Found {len(forbidden_files)} files in forbidden L*/P* folders"
    
    total_routed = len(rg_files) + len(lic_files)
    return True, f"Apps routing: {len(rg_files)} in apps_rg, {len(lic_files)} in apps_lic, {len(unassigned)} unassigned"

def test_phase01_support_domains_flat() -> Tuple[bool, str]:
    """Test that support domains don't have L*/P* cognitive folders."""
    support_domains = ["02_schemas", "03_runtime", "04_prompt_governance", "05_config", "07_observability", "08_scripts"]
    
    issues = []
    for domain in support_domains:
        domain_path = PROJECT_ROOT / domain
        if not domain_path.exists():
            continue
        
        for item in domain_path.iterdir():
            if item.is_dir() and (item.name.startswith("L") and "_" in item.name):
                # Check if it contains actual files (not just empty)
                files = list(item.rglob("*.py"))
                if files:
                    issues.append(f"{domain}/{item.name}: {len(files)} files")
    
    if issues:
        return False, f"Found L* folders with files in support domains: {issues[:5]}"
    return True, "Support domains have no L*/P* folders with files"

def run_phase01_tests() -> TestSuite:
    """Run all Phase 1 tests."""
    suite = TestSuite("Phase 1 - Structural Enforcement")
    
    tests = [
        ("YAML Files Exist", test_phase01_yaml_files_exist),
        ("Target Roots Exist", test_phase01_target_roots_exist),
        ("No Deeply Nested Unassigned", test_phase01_no_deeply_nested_unassigned),
        ("Apps Structure", test_phase01_apps_structure),
        ("Tests Structure", test_phase01_tests_structure),
        ("Mapping Report", test_phase01_mapping_report),
        ("No Windows Path Errors", test_phase01_no_windows_path_errors),
        ("Apps Files Routed", test_phase01_apps_files_routed),
        ("Support Domains Flat", test_phase01_support_domains_flat),
    ]
    
    for name, test_fn in tests:
        result = run_test(name, test_fn)
        suite.results.append(result)
    
    return suite

# ======================================================================
# EXECUTION TESTS
# ======================================================================

def test_phase01_execution() -> Tuple[bool, str]:
    """Test that Phase 1 executes without errors."""
    import subprocess
    
    try:
        result = subprocess.run(
            [sys.executable, str(PHASE01_DIR / "phase01.py")],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(PROJECT_ROOT)
        )
        
        if result.returncode != 0:
            return False, f"Exit code {result.returncode}: {result.stderr[:200]}"
        
        # Check for PHASE VALIDATION COMPLETE
        if "PHASE VALIDATION COMPLETE" in result.stdout:
            return True, "Phase 1 executed successfully"
        else:
            return False, "Phase 1 did not complete validation"
    except subprocess.TimeoutExpired:
        return False, "Phase 1 execution timed out (>300s)"
    except Exception as e:
        return False, f"Execution error: {e}"

def run_execution_tests() -> TestSuite:
    """Run execution tests."""
    suite = TestSuite("Execution Tests")
    
    tests = [
        ("Phase 1 Execution", test_phase01_execution),
    ]
    
    for name, test_fn in tests:
        result = run_test(name, test_fn)
        suite.results.append(result)
    
    return suite

# ======================================================================
# MAIN
# ======================================================================

def main():
    logging.debug("="*60)
    logging.debug("END-TO-END TEST SUITE FOR PHASE 0.5 AND PHASE 1")
    logging.debug("="*60)
    logging.debug(f"Project Root: {PROJECT_ROOT}")
    logging.debug(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_suites: List[TestSuite] = []
    
    # Run Phase 0.5 tests
    logging.debug("\n[1/3] Running Phase 0.5 tests...")
    suite05 = run_phase05_tests()
    all_suites.append(suite05)
    print_suite_summary(suite05)
    
    # Run Phase 1 tests
    logging.debug("\n[2/3] Running Phase 1 tests...")
    suite01 = run_phase01_tests()
    all_suites.append(suite01)
    print_suite_summary(suite01)
    
    # Run execution tests
    logging.debug("\n[3/3] Running execution tests...")
    suite_exec = run_execution_tests()
    all_suites.append(suite_exec)
    print_suite_summary(suite_exec)
    
    # Final summary
    logging.debug("\n" + "="*60)
    logging.debug("FINAL SUMMARY")
    logging.debug("="*60)
    
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
