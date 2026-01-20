#!/usr/bin/env python3
"""
test_unified_hygiene_validator.py - Phase 2 Hygiene Validator Test Suite

Tests:
1. GAP-4 Verification: Duplicate file detection via MD5 hash
2. Orphan Logic Test: Dead code detection
3. Marker Scanning: Technical debt marker aggregation
4. Self-tests: Internal validator tests

Usage:
    python scripts/test_unified_hygiene_validator.py
    python scripts/test_unified_hygiene_validator.py --duplicates-only
    python scripts/test_unified_hygiene_validator.py --orphans-only
    python scripts/test_unified_hygiene_validator.py --markers-only
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def run_self_tests() -> Dict[str, Any]:
    """Run the UnifiedStructureValidatorAgent's internal self-tests."""
    from agentic_core.L5_safety.unified.UnifiedStructureValidatorAgent import UnifiedStructureValidatorAgent
    validator = UnifiedStructureValidatorAgent(project_root=PROJECT_ROOT)
    return validator._run_self_tests()


def test_gap4_duplicate_detection() -> Dict[str, Any]:
    """
    GAP-4 Verification: Test duplicate file detection.
    
    Creates two identical files in different directories and verifies
    the validator detects them as duplicates via MD5 hash.
    """
    from agentic_core.L5_safety.unified.UnifiedStructureValidatorAgent import UnifiedStructureValidatorAgent
    
    # Use the test fixtures directory
    fixtures_dir = PROJECT_ROOT / "tests" / "hygiene_test_fixtures"
    
    if not fixtures_dir.exists():
        return {
            "status": "SKIP",
            "reason": f"Test fixtures directory not found: {fixtures_dir}"
        }
    
    validator = UnifiedStructureValidatorAgent(project_root=fixtures_dir)
    validator._scan_repository()
    duplicates = validator._find_duplicates()
    
    # Check if our test duplicates were detected
    duplicate_found = False
    for dup in duplicates:
        files = dup.get('files', [])
        if any('duplicate_a' in f for f in files) and any('duplicate_b' in f for f in files):
            duplicate_found = True
            break
    
    return {
        "status": "PASS" if duplicate_found else "FAIL",
        "duplicates_found": len(duplicates),
        "test_duplicate_detected": duplicate_found,
        "details": duplicates,
    }


def test_orphan_detection() -> Dict[str, Any]:
    """
    Orphan Logic Test: Test dead code detection.
    
    Verifies the validator identifies files not imported anywhere.
    """
    from agentic_core.L5_safety.unified.UnifiedStructureValidatorAgent import UnifiedStructureValidatorAgent
    
    # Use the test fixtures directory
    fixtures_dir = PROJECT_ROOT / "tests" / "hygiene_test_fixtures"
    
    if not fixtures_dir.exists():
        return {
            "status": "SKIP",
            "reason": f"Test fixtures directory not found: {fixtures_dir}"
        }
    
    validator = UnifiedStructureValidatorAgent(project_root=fixtures_dir)
    validator._scan_repository()
    orphans = validator._find_orphans()
    
    # Check if our test orphan was detected (renamed to avoid test_ prefix filtering)
    orphan_found = any('orphan_dead_code_file' in o.get('file', '') for o in orphans)
    
    return {
        "status": "PASS" if orphan_found else "FAIL",
        "orphans_found": len(orphans),
        "test_orphan_detected": orphan_found,
        "details": orphans,
    }


def test_marker_scanning() -> Dict[str, Any]:
    """
    Marker Scanning Test: Test technical debt marker detection.
    
    Verifies the validator finds TODO, FIXME, HACK, XXX, BUG markers.
    """
    from agentic_core.L5_safety.unified.UnifiedStructureValidatorAgent import UnifiedStructureValidatorAgent
    
    # Use the test fixtures directory
    fixtures_dir = PROJECT_ROOT / "tests" / "hygiene_test_fixtures"
    
    if not fixtures_dir.exists():
        return {
            "status": "SKIP",
            "reason": f"Test fixtures directory not found: {fixtures_dir}"
        }
    
    validator = UnifiedStructureValidatorAgent(project_root=fixtures_dir)
    validator._scan_repository()
    markers = validator._scan_markers()
    
    # Check marker types found
    marker_types = set(m.get('type', '') for m in markers)
    expected_markers = {'TODO', 'FIXME', 'HACK', 'XXX', 'BUG'}
    
    # Check if markers are from our test file
    test_file_markers = [m for m in markers if 'marker_test_file' in m.get('file', '')]
    
    all_expected_found = expected_markers.issubset(marker_types)
    
    return {
        "status": "PASS" if all_expected_found and len(test_file_markers) > 0 else "FAIL",
        "total_markers_found": len(markers),
        "test_file_markers": len(test_file_markers),
        "marker_types_found": list(marker_types),
        "expected_markers": list(expected_markers),
        "all_expected_found": all_expected_found,
        "details": test_file_markers[:10],  # First 10 for brevity
    }


def test_full_validation() -> Dict[str, Any]:
    """
    Full Validation Test: Run complete repository validation.
    """
    from agentic_core.L5_safety.unified.UnifiedStructureValidatorAgent import UnifiedStructureValidatorAgent
    
    # Use the test fixtures directory for controlled testing
    fixtures_dir = PROJECT_ROOT / "tests" / "hygiene_test_fixtures"
    
    if not fixtures_dir.exists():
        return {
            "status": "SKIP",
            "reason": f"Test fixtures directory not found: {fixtures_dir}"
        }
    
    validator = UnifiedStructureValidatorAgent(project_root=fixtures_dir)
    results = validator.validate_repository()
    
    return {
        "status": results.get('status', 'UNKNOWN'),
        "total_violations": results.get('total_violations', 0),
        "summary": results.get('summary', {}),
    }


def main():
    parser = argparse.ArgumentParser(description='Test UnifiedStructureValidatorAgent')
    parser.add_argument('--self-test', action='store_true', help='Run only self-tests')
    parser.add_argument('--duplicates-only', action='store_true', help='Run only duplicate detection test')
    parser.add_argument('--orphans-only', action='store_true', help='Run only orphan detection test')
    parser.add_argument('--markers-only', action='store_true', help='Run only marker scanning test')
    parser.add_argument('--output-dir', type=str, default='test_results', help='Output directory for JSON results')
    args = parser.parse_args()
    
    output_dir = PROJECT_ROOT / args.output_dir
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print("=" * 60)
    print("UnifiedStructureValidatorAgent Test Suite (Phase 2)")
    print("=" * 60)
    
    results = {
        'timestamp': timestamp,
        'tests': {},
    }
    
    all_passed = True
    
    # Self-tests
    if args.self_test or not any([args.duplicates_only, args.orphans_only, args.markers_only]):
        print("\n[1/5] Running self-tests...")
        try:
            self_test_results = run_self_tests()
            results['tests']['self_tests'] = self_test_results
            passed = self_test_results.get('passed', 0)
            failed = self_test_results.get('failed', 0)
            print(f"  ✓ Self-tests: {passed} passed, {failed} failed")
            if failed > 0:
                all_passed = False
                for test in self_test_results.get('tests', []):
                    if test.get('status') == 'failed':
                        print(f"    ✗ {test.get('name')}: {test.get('error')}")
        except Exception as e:
            print(f"  ✗ Self-tests failed: {e}")
            results['tests']['self_tests'] = {'error': str(e)}
            all_passed = False
    
    # GAP-4 Duplicate Detection
    if args.duplicates_only or not any([args.self_test, args.orphans_only, args.markers_only]):
        print("\n[2/5] Running GAP-4 duplicate detection test...")
        try:
            dup_results = test_gap4_duplicate_detection()
            results['tests']['gap4_duplicates'] = dup_results
            
            if dup_results.get('status') == 'PASS':
                print(f"  ✓ GAP-4 PASSED: Duplicate files detected ({dup_results.get('duplicates_found')} groups)")
            elif dup_results.get('status') == 'SKIP':
                print(f"  ⊘ GAP-4 SKIPPED: {dup_results.get('reason')}")
            else:
                print(f"  ✗ GAP-4 FAILED: Test duplicates not detected")
                all_passed = False
        except Exception as e:
            print(f"  ✗ GAP-4 test failed: {e}")
            results['tests']['gap4_duplicates'] = {'error': str(e)}
            all_passed = False
    
    # Orphan Detection
    if args.orphans_only or not any([args.self_test, args.duplicates_only, args.markers_only]):
        print("\n[3/5] Running orphan detection test...")
        try:
            orphan_results = test_orphan_detection()
            results['tests']['orphan_detection'] = orphan_results
            
            if orphan_results.get('status') == 'PASS':
                print(f"  ✓ Orphan detection PASSED: {orphan_results.get('orphans_found')} orphans found")
            elif orphan_results.get('status') == 'SKIP':
                print(f"  ⊘ Orphan detection SKIPPED: {orphan_results.get('reason')}")
            else:
                print(f"  ✗ Orphan detection FAILED: Test orphan not detected")
                all_passed = False
        except Exception as e:
            print(f"  ✗ Orphan detection test failed: {e}")
            results['tests']['orphan_detection'] = {'error': str(e)}
            all_passed = False
    
    # Marker Scanning
    if args.markers_only or not any([args.self_test, args.duplicates_only, args.orphans_only]):
        print("\n[4/5] Running marker scanning test...")
        try:
            marker_results = test_marker_scanning()
            results['tests']['marker_scanning'] = marker_results
            
            if marker_results.get('status') == 'PASS':
                print(f"  ✓ Marker scanning PASSED: {marker_results.get('total_markers_found')} markers found")
                print(f"    Types: {marker_results.get('marker_types_found')}")
            elif marker_results.get('status') == 'SKIP':
                print(f"  ⊘ Marker scanning SKIPPED: {marker_results.get('reason')}")
            else:
                print(f"  ✗ Marker scanning FAILED: Not all expected markers found")
                print(f"    Expected: {marker_results.get('expected_markers')}")
                print(f"    Found: {marker_results.get('marker_types_found')}")
                all_passed = False
        except Exception as e:
            print(f"  ✗ Marker scanning test failed: {e}")
            results['tests']['marker_scanning'] = {'error': str(e)}
            all_passed = False
    
    # Full Validation
    if not any([args.self_test, args.duplicates_only, args.orphans_only, args.markers_only]):
        print("\n[5/5] Running full validation test...")
        try:
            full_results = test_full_validation()
            results['tests']['full_validation'] = full_results
            
            print(f"  ✓ Full validation completed")
            print(f"    Status: {full_results.get('status')}")
            print(f"    Total violations: {full_results.get('total_violations')}")
            summary = full_results.get('summary', {})
            for key, value in summary.items():
                print(f"    - {key}: {value}")
        except Exception as e:
            print(f"  ✗ Full validation test failed: {e}")
            results['tests']['full_validation'] = {'error': str(e)}
            all_passed = False
    
    # Save results
    output_file = output_dir / f'unified_hygiene_validator_test_{timestamp}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n{'=' * 60}")
    print(f"Results saved to: {output_file}")
    
    if all_passed:
        print("✓ ALL TESTS PASSED")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
