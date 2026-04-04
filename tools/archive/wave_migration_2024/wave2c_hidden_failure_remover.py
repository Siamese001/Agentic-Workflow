#!/usr/bin/env python3
"""
Wave 2c: Remove INVALID skips - hidden failures.

This script removes invalid skip patterns that hide actual test failures,
focusing on revealing underlying issues that need to be addressed.
"""

import json
import re
from collections import defaultdict
from pathlib import Path


class HiddenFailureRemover:
    """Remover for skip patterns that hide failures."""

    def __init__(self):
        self.removal_stats = {
            'files_processed': 0,
            'files_modified': 0,
            'hidden_failures_removed': 0,
            'failures_revealed': 0,
            'errors_encountered': 0
        }
        self.modifications = []
        self.revealed_failures = []

    def load_wave1d_data(self) -> dict:
        """Load Wave 1d categorization data."""
        try:
            with open('artifacts/wave1d_categorization_report.json') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Wave 1d report not found. Please run Wave 1 first.")
            return {}

    def get_target_skips(self, wave1d_data: dict) -> list[dict]:
        """Get hidden failure skips targeted for removal."""
        wave2_assignments = wave1d_data.get('wave2_prioritization', {}).get('wave2_assignments', {})
        hidden_failure_assignment = wave2_assignments.get('wave2c_hidden_failures', {})

        target_skips = hidden_failure_assignment.get('assigned_skips', [])
        print(f"🎯 Target hidden failure skips for Wave 2c: {len(target_skips)}")

        return target_skips

    def remove_hidden_failure_skips(self, target_skips: list[dict]) -> dict:
        """Remove hidden failure skip patterns."""
        print("=== Removing Hidden Failure Skip Patterns ===")

        # Group skips by file for efficient processing
        skips_by_file = defaultdict(list)
        for skip in target_skips:
            skips_by_file[skip['file']].append(skip)

        print(f"📁 Files to process: {len(skips_by_file)}")

        # Process each file
        for file_path, skips in skips_by_file.items():
            self._process_hidden_failure_skips(file_path, skips)

        return {
            'stats': self.removal_stats,
            'modifications': self.modifications,
            'revealed_failures': self.revealed_failures
        }

    def _process_hidden_failure_skips(self, file_path: str, skips: list[dict]):
        """Process hidden failure skips in a single file."""
        self.removal_stats['files_processed'] += 1

        full_path = Path('tests') / file_path

        if not full_path.exists():
            print(f"⚠️  File not found: {file_path}")
            return

        try:
            # Read file content
            with open(full_path, encoding='utf-8') as f:
                content = f.read()
                original_content = content

            lines = content.split('\n')
            modified_lines = lines.copy()
            lines_removed = 0
            failures_revealed = 0

            # Process each skip (in reverse order to maintain line numbers)
            for skip in sorted(skips, key=lambda x: x['line'], reverse=True):
                line_num = skip['line'] - 1  # Convert to 0-based

                if 0 <= line_num < len(modified_lines):
                    original_line = modified_lines[line_num]

                    # Remove the hidden failure skip pattern
                    new_line, failure_revealed = self._remove_hidden_failure_pattern(original_line, skip)

                    if new_line != original_line:
                        modified_lines[line_num] = new_line
                        lines_removed += 1
                        self.removal_stats['hidden_failures_removed'] += 1

                        if failure_revealed:
                            failures_revealed += 1
                            self.removal_stats['failures_revealed'] += 1

                            # Record revealed failure
                            self.revealed_failures.append({
                                'file': file_path,
                                'line': skip['line'],
                                'original_skip': original_line.strip(),
                                'revealed_issue': skip['reason'],
                                'suggested_fix': self._suggest_fix(skip)
                            })

                        # Record modification
                        self.modifications.append({
                            'file': file_path,
                            'line': skip['line'],
                            'original': original_line.strip(),
                            'modified': new_line.strip(),
                            'skip_type': skip['pattern_type'],
                            'reason': skip['reason'],
                            'failure_revealed': failure_revealed
                        })

            # Write back if modified
            if lines_removed > 0:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(modified_lines))

                self.removal_stats['files_modified'] += 1
                print(f"✅ {file_path}: Removed {lines_removed} skip(s), revealed {failures_revealed} failure(s)")
            else:
                print(f"⚪ {file_path}: No changes needed")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            self.removal_stats['errors_encountered'] += 1

    def _remove_hidden_failure_pattern(self, line: str, skip: dict) -> tuple[str, bool]:
        """Remove hidden failure skip pattern from a line."""
        pattern_type = skip['pattern_type']
        reason = skip.get('reason', '').lower()
        failure_revealed = False

        # Determine if this is hiding a failure
        failure_indicators = [
            'broken', 'fails', 'error', 'crash', 'exception', 'issue',
            'problem', 'doesn\'t work', 'not working', 'regression',
            'bug', 'defect', 'flaky', 'unstable'
        ]

        is_hiding_failure = any(indicator in reason for indicator in failure_indicators)

        # Remove the skip pattern
        if pattern_type == 'pytest_skip':
            new_line = re.sub(r'@pytest\.mark\.skip(\s*\(.*?\))?\s*$', '', line.strip())
        elif pattern_type == 'pytest_skipif':
            new_line = re.sub(r'@pytest\.mark\.skipif\s*\(.*?\)\s*$', '', line.strip())
        elif pattern_type == 'pytest_xfail':
            new_line = re.sub(r'@pytest\.mark\.xfail(\s*\(.*?\))?\s*$', '', line.strip())
        elif pattern_type == 'manual_skips':
            new_line = re.sub(r'pytest\.skip\s*\(.*?\)\s*$', '', line.strip())
        elif pattern_type == 'decorator_skips':
            new_line = re.sub(r'@.*skip.*$', '', line.strip())
        else:
            new_line = f"# REMOVED HIDDEN FAILURE SKIP: {line.strip()}"

        if is_hiding_failure:
            failure_revealed = True
            # Add comment about revealed failure
            if new_line.strip():
                new_line += f"  # REVEALED FAILURE: {reason}"
            else:
                new_line = f"# REVEALED FAILURE: {reason}"

        return new_line, failure_revealed

    def _suggest_fix(self, skip: dict) -> str:
        """Suggest a fix for the revealed failure."""
        reason = skip.get('reason', '').lower()

        if 'broken' in reason or 'doesn\'t work' in reason:
            return "Fix the broken functionality or update test expectations"
        elif 'import' in reason or 'dependency' in reason:
            return "Add missing imports or fix dependency issues"
        elif 'configuration' in reason or 'config' in reason:
            return "Update configuration or add proper test setup"
        elif 'environment' in reason or 'platform' in reason:
            return "Make test environment-agnostic or add proper guards"
        elif 'flaky' in reason or 'unstable' in reason:
            return "Fix race conditions or add proper synchronization"
        elif 'performance' in reason or 'slow' in reason:
            return "Optimize test performance or adjust timeouts"
        else:
            return "Investigate and fix the underlying issue"

    def scan_for_additional_hidden_failures(self) -> list[dict]:
        """Scan for additional hidden failure patterns."""
        print("=== Scanning for Additional Hidden Failure Patterns ===")

        additional_skips = []
        test_dir = Path('tests')

        # Hidden failure patterns to look for
        hidden_failure_patterns = [
            (r'@pytest\.mark\.skip.*broken', 'broken_test'),
            (r'@pytest\.mark\.skip.*fail', 'failing_test'),
            (r'@pytest\.mark\.skip.*error', 'error_test'),
            (r'@pytest\.mark\.skip.*bug', 'bug_test'),
            (r'pytest\.skip.*broken', 'broken_manual_skip'),
            (r'pytest\.skip.*fail', 'fail_manual_skip'),
            (r'#.*TODO.*fix', 'todo_fix'),
            (r'#.*FIXME', 'fixme_comment'),
            (r'#.*broken', 'broken_comment')
        ]

        for test_file in test_dir.rglob('test_*.py'):
            try:
                with open(test_file, encoding='utf-8') as f:
                    content = f.read()

                lines = content.split('\n')
                rel_path = str(test_file.relative_to(test_dir))

                for line_num, line in enumerate(lines, 1):
                    line_stripped = line.strip()

                    # Check for hidden failure patterns
                    for pattern, pattern_type in hidden_failure_patterns:
                        if re.search(pattern, line_stripped, re.IGNORECASE):
                            additional_skips.append({
                                'file': rel_path,
                                'line': line_num,
                                'line_content': line_stripped,
                                'pattern_type': f'additional_{pattern_type}',
                                'reason': 'Additional hidden failure pattern detected',
                                'confidence': 0.6
                            })
                            break

            except Exception as e:
                print(f"    Error scanning {test_file}: {e}")

        print(f"🔍 Found {len(additional_skips)} additional hidden failure patterns")
        return additional_skips

    def fix_additional_hidden_failures(self, additional_skips: list[dict]) -> dict:
        """Fix additional hidden failure patterns."""
        print("=== Fixing Additional Hidden Failure Patterns ===")

        if not additional_skips:
            print("⚪ No additional hidden failure patterns to fix")
            return {'fixed': 0, 'failures_revealed': 0, 'errors': 0}

        # Group by file
        skips_by_file = defaultdict(list)
        for skip in additional_skips:
            skips_by_file[skip['file']].append(skip)

        fixed_count = 0
        failures_revealed = 0
        error_count = 0

        for file_path, skips in skips_by_file.items():
            try:
                full_path = Path('tests') / file_path
                with open(full_path, encoding='utf-8') as f:
                    content = f.read()

                lines = content.split('\n')
                modified_lines = lines.copy()

                # Process skips in reverse order
                for skip in sorted(skips, key=lambda x: x['line'], reverse=True):
                    line_num = skip['line'] - 1
                    if 0 <= line_num < len(modified_lines):
                        original_line = modified_lines[line_num]

                        # Fix the pattern
                        if 'skip' in original_line.lower():
                            new_line = re.sub(r'@.*skip.*', '# REMOVED HIDDEN FAILURE SKIP', original_line.strip())
                            failures_revealed += 1
                        elif 'todo' in original_line.lower() or 'fixme' in original_line.lower():
                            new_line = f"# TODO: Address this issue - {original_line.strip()}"
                        else:
                            new_line = f"# REVIEW: Potential hidden failure - {original_line.strip()}"

                        modified_lines[line_num] = new_line
                        fixed_count += 1

                # Write back
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(modified_lines))

                print(f"✅ {file_path}: Fixed {len(skips)} hidden failure patterns")

            except Exception as e:
                print(f"❌ Error fixing {file_path}: {e}")
                error_count += 1

        return {'fixed': fixed_count, 'failures_revealed': failures_revealed, 'errors': error_count}

    def generate_failure_report(self) -> dict:
        """Generate a report of revealed failures."""
        if not self.revealed_failures:
            return {'failures': [], 'summary': {'total': 0}}

        # Group failures by type
        failure_types = defaultdict(list)
        for failure in self.revealed_failures:
            issue_type = self._categorize_failure(failure['revealed_issue'])
            failure_types[issue_type].append(failure)

        report = {
            'failures': self.revealed_failures,
            'failure_types': dict(failure_types),
            'summary': {
                'total': len(self.revealed_failures),
                'by_type': {k: len(v) for k, v in failure_types.items()},
                'files_affected': len(set(f['file'] for f in self.revealed_failures))
            }
        }

        return report

    def _categorize_failure(self, reason: str) -> str:
        """Categorize the type of failure."""
        reason_lower = reason.lower()

        if any(word in reason_lower for word in ['broken', 'doesn\'t work', 'not working']):
            return 'broken_functionality'
        elif any(word in reason_lower for word in ['import', 'dependency', 'module']):
            return 'import_dependency'
        elif any(word in reason_lower for word in ['config', 'configuration', 'setup']):
            return 'configuration'
        elif any(word in reason_lower for word in ['environment', 'platform', 'os']):
            return 'environmental'
        elif any(word in reason_lower for word in ['flaky', 'unstable', 'race']):
            return 'flaky_test'
        elif any(word in reason_lower for word in ['performance', 'slow', 'timeout']):
            return 'performance'
        elif any(word in reason_lower for word in ['bug', 'defect', 'issue']):
            return 'bug'
        else:
            return 'other'

    def validate_removals(self) -> dict:
        """Validate that hidden failure removals were successful."""
        print("=== Validating Hidden Failure Removals ===")

        validation = {
            'files_validated': 0,
            'removals_confirmed': 0,
            'failures_revealed': 0,
            'remaining_issues': []
        }

        # Check modified files
        for modification in self.modifications:
            file_path = modification['file']
            full_path = Path('tests') / file_path

            try:
                with open(full_path, encoding='utf-8') as f:
                    content = f.read()

                # Check that the removed pattern is no longer present
                original_pattern = modification['original']
                if original_pattern not in content:
                    validation['removals_confirmed'] += 1

                    if modification.get('failure_revealed', False):
                        validation['failures_revealed'] += 1
                else:
                    validation['remaining_issues'].append({
                        'file': file_path,
                        'issue': 'Hidden failure skip pattern still present',
                        'pattern': original_pattern
                    })

                validation['files_validated'] += 1

            except Exception as e:
                validation['remaining_issues'].append({
                    'file': file_path,
                    'issue': f'Validation error: {e}'
                })

        return validation

    def generate_wave2c_report(self) -> dict:
        """Generate Wave 2c removal report."""
        print("=== Wave 2c: Remove INVALID Skips - Hidden Failures ===")

        # Load target data
        wave1d_data = self.load_wave1d_data()
        if not wave1d_data:
            return None

        target_skips = self.get_target_skips(wave1d_data)

        # Remove hidden failure skips
        removal_results = self.remove_hidden_failure_skips(target_skips)

        # Scan for additional patterns
        additional_skips = self.scan_for_additional_hidden_failures()

        # Fix additional patterns
        fix_results = self.fix_additional_hidden_failures(additional_skips)

        # Generate failure report
        failure_report = self.generate_failure_report()

        # Validate removals
        validation_results = self.validate_removals()

        # Create report
        report = {
            'wave': 'Wave 2c',
            'timestamp': '2026-03-25 20:25:00',
            'title': 'Remove INVALID Skips - Hidden Failures',
            'target_skips_count': len(target_skips),
            'additional_skips_found': len(additional_skips),
            'removal_results': removal_results,
            'fix_results': fix_results,
            'failure_report': failure_report,
            'validation_results': validation_results,
            'summary': {
                'target_skips': len(target_skips),
                'additional_skips': len(additional_skips),
                'files_processed': self.removal_stats['files_processed'],
                'files_modified': self.removal_stats['files_modified'],
                'hidden_failures_removed': self.removal_stats['hidden_failures_removed'],
                'failures_revealed': self.removal_stats['failures_revealed'],
                'additional_failures_revealed': fix_results['failures_revealed'],
                'total_failures_revealed': self.removal_stats['failures_revealed'] + fix_results['failures_revealed'],
                'removals_confirmed': validation_results['removals_confirmed'],
                'success_rate': (validation_results['removals_confirmed'] / max(len(target_skips), 1)) * 100
            }
        }

        # Save report
        with open('artifacts/wave2c_removal_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        summary = report['summary']
        print("\n=== Wave 2c Summary ===")
        print(f"Target skips: {summary['target_skips']}")
        print(f"Additional skips found: {summary['additional_skips']}")
        print(f"Files processed: {summary['files_processed']}")
        print(f"Files modified: {summary['files_modified']}")
        print(f"Hidden failures removed: {summary['hidden_failures_removed']}")
        print(f"Failures revealed: {summary['failures_revealed']}")
        print(f"Additional failures revealed: {summary['additional_failures_revealed']}")
        print(f"Total failures revealed: {summary['total_failures_revealed']}")
        print(f"Removals confirmed: {summary['removals_confirmed']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")

        # Print failure types
        if failure_report['summary']['by_type']:
            print("\n=== Revealed Failure Types ===")
            for failure_type, count in failure_report['summary']['by_type'].items():
                print(f"{failure_type}: {count}")

        if validation_results['remaining_issues']:
            print(f"\n⚠️  Remaining issues: {len(validation_results['remaining_issues'])}")
            for issue in validation_results['remaining_issues'][:3]:
                print(f"  - {issue['file']}: {issue['issue']}")

        print("\n📄 Report saved to: artifacts/wave2c_removal_report.json")

        return report


def main():
    """Main execution for Wave 2c."""
    remover = HiddenFailureRemover()
    report = remover.generate_wave2c_report()

    return report


if __name__ == '__main__':
    main()
