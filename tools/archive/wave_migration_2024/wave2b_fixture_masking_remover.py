#!/usr/bin/env python3
"""
Wave 2b: Remove INVALID skips - masking fixtures.

This script removes invalid skip patterns that mask fixture issues,
focusing on fixture-based skip mechanisms and anti-patterns.
"""

import json
import re
from collections import defaultdict
from pathlib import Path


class FixtureMaskingRemover:
    """Remover for fixture-based skip masking patterns."""

    def __init__(self):
        self.removal_stats = {
            'files_processed': 0,
            'files_modified': 0,
            'fixture_skips_removed': 0,
            'fixture_patterns_fixed': 0,
            'errors_encountered': 0
        }
        self.modifications = []

    def load_wave1d_data(self) -> dict:
        """Load Wave 1d categorization data."""
        try:
            with open('artifacts/wave1d_categorization_report.json') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Wave 1d report not found. Please run Wave 1 first.")
            return {}

    def get_target_skips(self, wave1d_data: dict) -> list[dict]:
        """Get fixture masking skips targeted for removal."""
        wave2_assignments = wave1d_data.get('wave2_prioritization', {}).get('wave2_assignments', {})
        fixture_assignment = wave2_assignments.get('wave2b_masking_fixtures', {})

        target_skips = fixture_assignment.get('assigned_skips', [])
        print(f"🎯 Target fixture masking skips for Wave 2b: {len(target_skips)}")

        return target_skips

    def remove_fixture_masking_skips(self, target_skips: list[dict]) -> dict:
        """Remove fixture masking skip patterns."""
        print("=== Removing Fixture Masking Skip Patterns ===")

        # Group skips by file for efficient processing
        skips_by_file = defaultdict(list)
        for skip in target_skips:
            skips_by_file[skip['file']].append(skip)

        print(f"📁 Files to process: {len(skips_by_file)}")

        # Process each file
        for file_path, skips in skips_by_file.items():
            self._process_fixture_skips(file_path, skips)

        return {
            'stats': self.removal_stats,
            'modifications': self.modifications
        }

    def _process_fixture_skips(self, file_path: str, skips: list[dict]):
        """Process fixture skips in a single file."""
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
            patterns_fixed = 0

            # Process each skip (in reverse order to maintain line numbers)
            for skip in sorted(skips, key=lambda x: x['line'], reverse=True):
                line_num = skip['line'] - 1  # Convert to 0-based

                if 0 <= line_num < len(modified_lines):
                    original_line = modified_lines[line_num]

                    # Remove or fix the fixture skip pattern
                    new_line, pattern_fixed = self._remove_fixture_skip_pattern(original_line, skip)

                    if new_line != original_line:
                        modified_lines[line_num] = new_line
                        lines_removed += 1
                        self.removal_stats['fixture_skips_removed'] += 1

                        if pattern_fixed:
                            patterns_fixed += 1
                            self.removal_stats['fixture_patterns_fixed'] += 1

                        # Record modification
                        self.modifications.append({
                            'file': file_path,
                            'line': skip['line'],
                            'original': original_line.strip(),
                            'modified': new_line.strip(),
                            'skip_type': skip['pattern_type'],
                            'reason': skip['reason'],
                            'pattern_fixed': pattern_fixed
                        })

            # Write back if modified
            if lines_removed > 0 or patterns_fixed > 0:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(modified_lines))

                self.removal_stats['files_modified'] += 1
                print(f"✅ {file_path}: Removed {lines_removed} skip(s), fixed {patterns_fixed} pattern(s)")
            else:
                print(f"⚪ {file_path}: No changes needed")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            self.removal_stats['errors_encountered'] += 1

    def _remove_fixture_skip_pattern(self, line: str, skip: dict) -> tuple[str, bool]:
        """Remove fixture skip pattern from a line."""
        pattern_type = skip['pattern_type']
        pattern_fixed = False

        # Fixture-based skip patterns
        if pattern_type == 'fixture_skips':
            # Remove fixture-based skip methods
            if 'def test_skip_' in line or 'def _skip_' in line:
                # Comment out the entire fixture method
                new_line = f"# REMOVED FIXTURE SKIP: {line.strip()}"
                pattern_fixed = True
            else:
                # Remove fixture usage
                new_line = re.sub(r'@pytest\.mark\.skip.*fixture.*', '', line.strip())
                if new_line != line.strip():
                    pattern_fixed = True
                else:
                    new_line = f"# REMOVED FIXTURE SKIP: {line.strip()}"

        # Conditional fixture skips
        elif 'fixture' in line.lower() and 'skip' in line.lower():
            # Remove conditional skip based on fixture
            new_line = re.sub(r'@pytest\.mark\.skipif.*fixture.*', '', line.strip())
            if new_line != line.strip():
                pattern_fixed = True
            else:
                new_line = f"# REMOVED FIXTURE SKIP: {line.strip()}"
                pattern_fixed = True

        # Manual fixture skips
        elif pattern_type == 'manual_skips' and 'fixture' in line.lower():
            # Remove manual skip calls related to fixtures
            new_line = re.sub(r'pytest\.skip.*fixture.*', '', line.strip())
            if new_line != line.strip():
                pattern_fixed = True
            else:
                new_line = f"# REMOVED FIXTURE SKIP: {line.strip()}"
                pattern_fixed = True

        else:
            # Default: comment out the line
            new_line = f"# REMOVED FIXTURE SKIP: {line.strip()}"

        return new_line, pattern_fixed

    def scan_for_additional_fixture_skips(self) -> list[dict]:
        """Scan for additional fixture skip patterns not in Wave 1d."""
        print("=== Scanning for Additional Fixture Skip Patterns ===")

        additional_skips = []
        test_dir = Path('tests')

        # Common fixture skip patterns to look for
        fixture_skip_patterns = [
            r'@pytest\.mark\.skip.*fixture',
            r'pytest\.skip.*fixture',
            r'def.*skip.*fixture',
            r'@.*skip.*fixture',
            r'if.*fixture.*skip',
            r'fixture.*pytest\.skip'
        ]

        for test_file in test_dir.rglob('test_*.py'):
            try:
                with open(test_file, encoding='utf-8') as f:
                    content = f.read()

                lines = content.split('\n')
                rel_path = str(test_file.relative_to(test_dir))

                for line_num, line in enumerate(lines, 1):
                    line_stripped = line.strip()

                    # Check for fixture skip patterns
                    for pattern in fixture_skip_patterns:
                        if re.search(pattern, line_stripped, re.IGNORECASE):
                            additional_skips.append({
                                'file': rel_path,
                                'line': line_num,
                                'line_content': line_stripped,
                                'pattern_type': 'additional_fixture_skip',
                                'reason': 'Additional fixture skip pattern detected',
                                'confidence': 0.7
                            })
                            break

            except Exception as e:
                print(f"    Error scanning {test_file}: {e}")

        print(f"🔍 Found {len(additional_skips)} additional fixture skip patterns")
        return additional_skips

    def fix_fixture_patterns(self, additional_skips: list[dict]) -> dict:
        """Fix additional fixture skip patterns."""
        print("=== Fixing Additional Fixture Patterns ===")

        if not additional_skips:
            print("⚪ No additional fixture patterns to fix")
            return {'fixed': 0, 'errors': 0}

        # Group by file
        skips_by_file = defaultdict(list)
        for skip in additional_skips:
            skips_by_file[skip['file']].append(skip)

        fixed_count = 0
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
                        new_line = f"# FIXED FIXTURE PATTERN: {original_line.strip()}"
                        modified_lines[line_num] = new_line
                        fixed_count += 1

                # Write back
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(modified_lines))

                print(f"✅ {file_path}: Fixed {len(skips)} fixture patterns")

            except Exception as e:
                print(f"❌ Error fixing {file_path}: {e}")
                error_count += 1

        return {'fixed': fixed_count, 'errors': error_count}

    def validate_removals(self) -> dict:
        """Validate that fixture skip removals were successful."""
        print("=== Validating Fixture Skip Removals ===")

        validation = {
            'files_validated': 0,
            'removals_confirmed': 0,
            'patterns_fixed': 0,
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

                    if modification.get('pattern_fixed', False):
                        validation['patterns_fixed'] += 1
                else:
                    validation['remaining_issues'].append({
                        'file': file_path,
                        'issue': 'Fixture skip pattern still present',
                        'pattern': original_pattern
                    })

                validation['files_validated'] += 1

            except Exception as e:
                validation['remaining_issues'].append({
                    'file': file_path,
                    'issue': f'Validation error: {e}'
                })

        return validation

    def generate_wave2b_report(self) -> dict:
        """Generate Wave 2b removal report."""
        print("=== Wave 2b: Remove INVALID Skips - Masking Fixtures ===")

        # Load target data
        wave1d_data = self.load_wave1d_data()
        if not wave1d_data:
            return None

        target_skips = self.get_target_skips(wave1d_data)

        # Remove fixture masking skips
        removal_results = self.remove_fixture_masking_skips(target_skips)

        # Scan for additional patterns
        additional_skips = self.scan_for_additional_fixture_skips()

        # Fix additional patterns
        fix_results = self.fix_fixture_patterns(additional_skips)

        # Validate removals
        validation_results = self.validate_removals()

        # Create report
        report = {
            'wave': 'Wave 2b',
            'timestamp': '2026-03-25 20:20:00',
            'title': 'Remove INVALID Skips - Masking Fixtures',
            'target_skips_count': len(target_skips),
            'additional_skips_found': len(additional_skips),
            'removal_results': removal_results,
            'fix_results': fix_results,
            'validation_results': validation_results,
            'summary': {
                'target_skips': len(target_skips),
                'additional_skips': len(additional_skips),
                'files_processed': self.removal_stats['files_processed'],
                'files_modified': self.removal_stats['files_modified'],
                'fixture_skips_removed': self.removal_stats['fixture_skips_removed'],
                'fixture_patterns_fixed': self.removal_stats['fixture_patterns_fixed'],
                'additional_patterns_fixed': fix_results['fixed'],
                'removals_confirmed': validation_results['removals_confirmed'],
                'total_patterns_fixed': validation_results['patterns_fixed'] + fix_results['fixed'],
                'success_rate': (validation_results['removals_confirmed'] / max(len(target_skips), 1)) * 100
            }
        }

        # Save report
        with open('artifacts/wave2b_removal_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        summary = report['summary']
        print("\n=== Wave 2b Summary ===")
        print(f"Target skips: {summary['target_skips']}")
        print(f"Additional skips found: {summary['additional_skips']}")
        print(f"Files processed: {summary['files_processed']}")
        print(f"Files modified: {summary['files_modified']}")
        print(f"Fixture skips removed: {summary['fixture_skips_removed']}")
        print(f"Fixture patterns fixed: {summary['fixture_patterns_fixed']}")
        print(f"Additional patterns fixed: {summary['additional_patterns_fixed']}")
        print(f"Total patterns fixed: {summary['total_patterns_fixed']}")
        print(f"Removals confirmed: {summary['removals_confirmed']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")

        if validation_results['remaining_issues']:
            print(f"\n⚠️  Remaining issues: {len(validation_results['remaining_issues'])}")
            for issue in validation_results['remaining_issues'][:3]:
                print(f"  - {issue['file']}: {issue['issue']}")

        print("\n📄 Report saved to: artifacts/wave2b_removal_report.json")

        return report


def main():
    """Main execution for Wave 2b."""
    remover = FixtureMaskingRemover()
    report = remover.generate_wave2b_report()

    return report


if __name__ == '__main__':
    main()
