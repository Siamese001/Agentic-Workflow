"""
Run all 6-batch test suites and validate 100% pass rate
"""
import subprocess
import sys
from pathlib import Path


# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_test_suite(test_file: str) -> tuple[bool, str]:
    """Run a single test suite and return success status."""
    print(f"\n{'=' * 60}")
    print(f'Running: {test_file}')
    print('=' * 60)
    result = subprocess.run([sys.executable, '-m', 'pytest', test_file, '-v', '--tb=short'], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
    return (result.returncode == 0, result.stdout + result.stderr)

def main():
    """Run all batch tests."""
    test_suites = ['tests/apps_rg/test_batch_1_foundation.py', 'tests/apps_rg/test_batch_2_hops.py', 'tests/apps_rg/test_batch_3_generation.py', 'tests/apps_rg/test_batch_4_refinement_part1.py', 'tests/apps_rg/test_batch_5_refinement_part2.py', 'tests/apps_rg/test_batch_6_safety.py']
    results = {}
    for test_suite in test_suites:
        success, output = run_test_suite(test_suite)
        results[test_suite] = success
        if not success:
            print(f'\n❌ FAILED: {test_suite}')
            print(output[-1000:])
        else:
            print(f'\n✅ PASSED: {test_suite}')
    print('\n' + '=' * 60)
    print('FINAL SUMMARY')
    print('=' * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for suite, success in results.items():
        status = '✅ PASS' if success else '❌ FAIL'
        print(f'{status} - {Path(suite).name}')
    print(f'\nTotal: {passed}/{total} passed ({100 * passed / total:.0f}%)')
    if passed == total:
        print('\n🎉 ALL BATCH TESTS PASSED!')
        return 0
    else:
        print(f'\n⚠️ {total - passed} test suites failed.')
        return 1
if __name__ == '__main__':
    sys.exit(main())
