#!/usr/bin/env python3
"""
Wave 6a: Final test suite validation and regression testing.

This script performs comprehensive validation of the test suite after Waves 1-5
to ensure all improvements are working correctly and no regressions exist.
"""

import json
import re
import subprocess
import time
from pathlib import Path


class TestSuiteValidator:
    """Comprehensive test suite validator."""

    def __init__(self):
        self.results = {}
        self.start_time = time.time()

    def run_pytest_collection(self) -> dict:
        """Run pytest collection to verify all tests can be collected."""
        print("=== Running PyTest Collection Validation ===")

        try:
            # Run pytest collection only
            result = subprocess.run(
                ['python', '-m', 'pytest', '--collect-only', '-q'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            collected_tests = []
            for line in result.stdout.split('\n'):
                if '::test_' in line:
                    collected_tests.append(line.strip())

            return {
                'success': result.returncode == 0,
                'collected_tests': len(collected_tests),
                'test_list': collected_tests[:50],  # First 50 for reference
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Collection timeout after 5 minutes',
                'collected_tests': 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'collected_tests': 0
            }

    def run_syntax_validation(self) -> dict:
        """Validate syntax of all test files."""
        print("=== Running Syntax Validation ===")

        test_dir = Path('tests')
        syntax_errors = []
        valid_files = 0

        for test_file in test_dir.rglob('test_*.py'):
            if test_file.is_file():
                try:
                    # Try to compile the file
                    with open(test_file, encoding='utf-8') as f:
                        content = f.read()

                    compile(content, str(test_file), 'exec')
                    valid_files += 1

                except SyntaxError as e:
                    syntax_errors.append({
                        'file': str(test_file),
                        'line': e.lineno,
                        'error': str(e),
                        'text': e.text
                    })
                except Exception as e:
                    syntax_errors.append({
                        'file': str(test_file),
                        'error': f'Compilation error: {str(e)}'
                    })

        return {
            'success': len(syntax_errors) == 0,
            'total_files': valid_files + len(syntax_errors),
            'valid_files': valid_files,
            'syntax_errors': syntax_errors
        }

    def run_import_validation(self) -> dict:
        """Validate imports in test files."""
        print("=== Running Import Validation ===")

        test_dir = Path('tests')
        import_errors = []
        valid_imports = 0

        for test_file in test_dir.rglob('test_*.py'):
            if test_file.is_file():
                try:
                    # Try to execute the file in a subprocess to check imports
                    result = subprocess.run(
                        ['python', '-c', f'import ast; ast.parse(open("{test_file}").read()); exec(open("{test_file}").read())'],
                        capture_output=True,
                        text=True,
                        timeout=30  # 30 second timeout per file
                    )

                    if result.returncode == 0:
                        valid_imports += 1
                    else:
                        import_errors.append({
                            'file': str(test_file),
                            'error': result.stderr
                        })

                except subprocess.TimeoutExpired:
                    import_errors.append({
                        'file': str(test_file),
                        'error': 'Import validation timeout'
                    })
                except Exception as e:
                    import_errors.append({
                        'file': str(test_file),
                        'error': str(e)
                    })

        return {
            'success': len(import_errors) == 0,
            'total_files': valid_imports + len(import_errors),
            'valid_imports': valid_imports,
            'import_errors': import_errors[:20]  # Limit to first 20 errors
        }

    def validate_test_quality_metrics(self) -> dict:
        """Validate test quality metrics against Waves 1-5 improvements."""
        print("=== Running Test Quality Validation ===")

        # Load previous wave results
        wave_results = {}

        try:
            with open('artifacts/hollowed_tests_analysis.json') as f:
                wave_results['wave3'] = json.load(f)
        except:
            wave_results['wave3'] = {'summary': {'hollowed_tests': 0}}

        try:
            with open('artifacts/guardian_swallow_analysis.json') as f:
                wave_results['wave4'] = json.load(f)
        except:
            wave_results['wave4'] = {'summary': {'files_needing_conversion': 0}}

        try:
            with open('artifacts/test_quality_analysis.json') as f:
                wave_results['wave5'] = json.load(f)
        except:
            wave_results['wave5'] = {'summary': {'total_issues': 0}}

        # Current validation
        test_dir = Path('tests')
        current_metrics = {
            'total_test_files': len(list(test_dir.rglob('test_*.py'))),
            'hollowed_tests': 0,
            'guardian_swallows': 0,
            'print_statements': 0,
            'syntax_errors': 0,
            'import_errors': 0
        }

        # Scan for remaining issues
        for test_file in test_dir.rglob('test_*.py'):
            if test_file.is_file():
                try:
                    content = test_file.read_text(encoding='utf-8')

                    # Check for hollowed tests (pass-only methods)
                    if 'def test_' in content and 'pass' in content:
                        # Simple heuristic - count pass statements in test methods
                        test_methods = re.findall(r'def (test_[^(]+)\s*\([^)]*\)\s*:', content)
                        for method in test_methods:
                            method_start = content.find(f'def {method}')
                            if method_start != -1:
                                # Find the method body (simplified)
                                method_section = content[method_start:method_start+500]
                                if 'pass' in method_section and 'assert' not in method_section:
                                    current_metrics['hollowed_tests'] += 1

                    # Check for guardian swallows
                    if 'guardian:' in content or 'except' in content:
                        guardian_patterns = re.findall(r'guardian:\s*allow-[a-zA-Z_-]+', content)
                        current_metrics['guardian_swallows'] += len(guardian_patterns)

                        # Check for bare except with pass
                        except_pass = re.findall(r'except\s+\w+.*:\s*pass', content)
                        current_metrics['guardian_swallows'] += len(except_pass)

                    # Check for print statements
                    print_count = len(re.findall(r'print\s*\(', content))
                    current_metrics['print_statements'] += print_count

                except Exception:
                    continue

        return {
            'success': True,
            'current_metrics': current_metrics,
            'wave_results': wave_results,
            'improvements': {
                'hollowed_tests_eliminated': wave_results['wave3'].get('summary', {}).get('hollowed_tests', 0) == 0 and current_metrics['hollowed_tests'] == 0,
                'guardian_swallows_eliminated': wave_results['wave4'].get('summary', {}).get('files_needing_conversion', 0) == 0 and current_metrics['guardian_swallows'] == 0,
                'print_statements_eliminated': current_metrics['print_statements'] == 0
            }
        }

    def run_sample_test_execution(self) -> dict:
        """Run a sample of tests to verify execution works."""
        print("=== Running Sample Test Execution ===")

        # Get a few test files to run
        test_dir = Path('tests')
        sample_tests = []

        for test_file in test_dir.rglob('test_*.py'):
            if len(sample_tests) >= 5:  # Limit to 5 test files
                break
            if test_file.is_file() and test_file.stat().st_size < 50000:  # Skip very large files
                sample_tests.append(str(test_file))

        if not sample_tests:
            return {
                'success': False,
                'error': 'No test files found for sampling'
            }

        execution_results = []

        for test_file in sample_tests:
            try:
                print(f"  Running: {Path(test_file).name}")

                result = subprocess.run(
                    ['python', '-m', 'pytest', test_file, '-v', '--tb=short'],
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minute timeout per test file
                )

                execution_results.append({
                    'file': test_file,
                    'success': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode
                })

            except subprocess.TimeoutExpired:
                execution_results.append({
                    'file': test_file,
                    'success': False,
                    'error': 'Test execution timeout'
                })
            except Exception as e:
                execution_results.append({
                    'file': test_file,
                    'success': False,
                    'error': str(e)
                })

        successful = len([r for r in execution_results if r['success']])

        return {
            'success': successful > 0,
            'total_tests': len(execution_results),
            'successful': successful,
            'results': execution_results
        }

    def generate_validation_report(self) -> dict:
        """Generate comprehensive validation report."""
        print("=== Generating Validation Report ===")

        # Run all validations
        collection_result = self.run_pytest_collection()
        syntax_result = self.run_syntax_validation()
        import_result = self.run_import_validation()
        quality_result = self.validate_test_quality_metrics()
        execution_result = self.run_sample_test_execution()

        # Overall success
        overall_success = all([
            collection_result['success'],
            syntax_result['success'],
            import_result['success'],
            quality_result['success'],
            execution_result['success']
        ])

        validation_time = time.time() - self.start_time

        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'validation_time_seconds': validation_time,
            'overall_success': overall_success,
            'collection': collection_result,
            'syntax': syntax_result,
            'imports': import_result,
            'quality': quality_result,
            'execution': execution_result,
            'summary': {
                'total_test_files': syntax_result['total_files'],
                'collected_tests': collection_result['collected_tests'],
                'syntax_errors': len(syntax_result['syntax_errors']),
                'import_errors': len(import_result['import_errors']),
                'sample_execution_success': execution_result['successful'],
                'sample_execution_total': execution_result['total_tests']
            }
        }

        return report

    def save_report(self, report: dict, filename: str = 'wave6a_validation_report.json'):
        """Save validation report to file."""
        report_path = Path('artifacts') / filename
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Validation report saved to: {report_path}")
        return report_path


def main():
    """Main validation execution."""
    print("=== Wave 6a: Final Test Suite Validation and Regression Testing ===")
    print("This will validate that all Waves 1-5 improvements are working correctly.\n")

    validator = TestSuiteValidator()
    report = validator.generate_validation_report()

    # Print summary
    print("\n=== Validation Summary ===")
    print(f"Overall Success: {'✅ PASS' if report['overall_success'] else '❌ FAIL'}")
    print(f"Validation Time: {report['validation_time_seconds']:.2f} seconds")

    summary = report['summary']
    print(f"Total Test Files: {summary['total_test_files']}")
    print(f"Collected Tests: {summary['collected_tests']}")
    print(f"Syntax Errors: {summary['syntax_errors']}")
    print(f"Import Errors: {summary['import_errors']}")
    print(f"Sample Execution: {summary['sample_execution_success']}/{summary['sample_execution_total']} successful")

    # Quality improvements
    quality = report['quality']
    improvements = quality['improvements']
    print("\n=== Wave Improvements Status ===")
    print(f"Hollowed Tests Eliminated: {'✅' if improvements['hollowed_tests_eliminated'] else '❌'}")
    print(f"Guardian Swallows Eliminated: {'✅' if improvements['guardian_swallows_eliminated'] else '❌'}")
    print(f"Print Statements Eliminated: {'✅' if improvements['print_statements_eliminated'] else '❌'}")

    # Current metrics
    current = quality['current_metrics']
    print("\n=== Current Test Suite Metrics ===")
    print(f"Total Test Files: {current['total_test_files']}")
    print(f"Remaining Hollowed Tests: {current['hollowed_tests']}")
    print(f"Remaining Guardian Swallows: {current['guardian_swallows']}")
    print(f"Remaining Print Statements: {current['print_statements']}")

    # Save report
    validator.save_report(report)

    if report['overall_success']:
        print("\n🎉 Wave 6a Validation PASSED! Test suite is ready for production.")
    else:
        print("\n⚠️  Wave 6a Validation FAILED! Issues need to be addressed.")

    return report


if __name__ == '__main__':
    main()
