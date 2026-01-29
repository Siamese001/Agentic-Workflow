"""
Guardian Suite Configuration and Reporting
Provides architectural health summary reporting for all Guardian tests
"""
import sys
import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Generate Guardian report after test completion
    """
    # Check if we're running guardian tests
    guardian_tests_found = False
    for stat_name, stat_items in terminalreporter.stats.items():
        if hasattr(stat_items, '__iter__'):
            for item in stat_items:
                if hasattr(item, 'nodeid') and 'guardian' in item.nodeid:
                    guardian_tests_found = True
                    break
        if guardian_tests_found:
            break
    
    # Skip report generation if no guardian tests were found
    if not guardian_tests_found:
        return
    
    # Collect test results
    stats = terminalreporter.stats
    passed_tests = len(stats.get('passed', []))
    failed_items = stats.get('failed', [])
    error_items = stats.get('error', [])
    skipped_tests = len(stats.get('skipped', []))

    total_tests = passed_tests + len(failed_items) + len(error_items) + skipped_tests
    failed_tests = len(failed_items) + len(error_items)
    
    # Analyze failures by category
    failed_by_category = {
        'MRO Integrity': [],
        'Import Safety': [],
        'SSOT Alignment': [],
        'Other': []
    }
    
    # Categorize failed tests
    for failed_test in list(failed_items) + list(error_items):
        test_name = getattr(failed_test, 'nodeid', str(failed_test))
        if 'mro' in test_name.lower():
            failed_by_category['MRO Integrity'].append(test_name)
        elif 'import' in test_name.lower():
            failed_by_category['Import Safety'].append(test_name)
        elif 'ssot' in test_name.lower() or 'alignment' in test_name.lower():
            failed_by_category['SSOT Alignment'].append(test_name)
        else:
            failed_by_category['Other'].append(test_name)
    
    # Generate report
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("GUARDIAN ARCHITECTURAL HEALTH REPORT")
    report_lines.append("=" * 60)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Exit Status: {'PASS' if exitstatus == 0 else 'FAIL'}")
    report_lines.append("")
    
    # Summary
    report_lines.append("EXECUTION SUMMARY:")
    report_lines.append(f"  Total Tests Run: {total_tests}")
    report_lines.append(f"  Passed: {passed_tests}")
    report_lines.append(f"  Failed: {failed_tests}")
    report_lines.append(f"  Skipped: {skipped_tests}")
    report_lines.append("")
    
    # Failed gates
    if failed_tests > 0:
        report_lines.append("FAILED GATES:")
        for category, failures in failed_by_category.items():
            if failures:
                report_lines.append(f"  ❌ {category}: {len(failures)} test(s)")
                for failure in failures:
                    report_lines.append(f"     - {failure}")
        report_lines.append("")
    else:
        report_lines.append("✅ ALL GUARDIAN GATES PASSED")
        report_lines.append("")
    
    # Status and recommendations
    if exitstatus == 0:
        report_lines.append("ARCHITECTURAL HEALTH: ✅ OPTIMAL")
        report_lines.append("All architectural integrity checks passed.")
        report_lines.append("The codebase maintains structural integrity.")
    else:
        report_lines.append("ARCHITECTURAL HEALTH: ⚠️  COMPROMISED")
        report_lines.append("Architectural violations detected.")
        report_lines.append("Please review failed tests and remediate issues.")
        report_lines.append("")
        report_lines.append("RECOMMENDED ACTIONS:")
        if failed_by_category['MRO Integrity']:
            report_lines.append("  - Fix MRO violations and inheritance issues")
        if failed_by_category['Import Safety']:
            report_lines.append("  - Resolve import errors and circular dependencies")
        if failed_by_category['SSOT Alignment']:
            report_lines.append("  - Correct SSOT alignment and file placement issues")
        if failed_by_category['Other']:
            report_lines.append("  - Review and fix other architectural violations")
    
    report_lines.append("=" * 60)
    
    # Write report to file
    report_content = "\n".join(report_lines)
    report_path = Path("guardian_report.txt")
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Print summary to terminal
        print("\n" + "=" * 60)
        print("GUARDIAN REPORT GENERATED")
        print("=" * 60)
        print(f"Report saved to: {report_path.absolute()}")
        print(f"Status: {'PASS' if exitstatus == 0 else 'FAIL'}")
        if failed_tests > 0:
            print(f"Failed Tests: {failed_tests}")
        print("=" * 60)
        
    except Exception as e:
        print(f"Warning: Could not write guardian report: {e}")


@pytest.fixture(scope="session", autouse=True)
def guardian_session_marker():
    """
    Automatically mark all guardian tests
    """
    pass
