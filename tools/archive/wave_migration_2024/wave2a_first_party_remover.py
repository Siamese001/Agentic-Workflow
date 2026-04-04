#!/usr/bin/env python3
"""
Wave 2a: Remove INVALID skips - first-party skip patterns.

This script removes invalid first-party skip patterns identified in Wave 1,
focusing on clear anti-patterns and development convenience skips.
"""

import json
import re
from collections import defaultdict
from pathlib import Path


class FirstPartySkipRemover:
    """Remover for invalid first-party skip patterns."""

    def __init__(self):
        self.removal_stats = {
            'files_processed': 0,
            'files_modified': 0,
            'skips_removed': 0,
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
        """Get first-party skip patterns targeted for removal."""
        wave2_assignments = wave1d_data.get('wave2_prioritization', {}).get('wave2_assignments', {})
        first_party_assignment = wave2_assignments.get('wave2a_first_party', {})

        target_skips = first_party_assignment.get('assigned_skips', [])
        print(f"🎯 Target skips for Wave 2a: {len(target_skips)}")

        return target_skips

    def remove_first_party_skips(self, target_skips: list[dict]) -> dict:
        """Remove first-party skip patterns from test files."""
        print("=== Removing First-Party Skip Patterns ===")

        # Group skips by file for efficient processing
        skips_by_file = defaultdict(list)
        for skip in target_skips:
            skips_by_file[skip['file']].append(skip)

        print(f"📁 Files to process: {len(skips_by_file)}")

        # Process each file
        for file_path, skips in skips_by_file.items():
            self._process_file_skips(file_path, skips)

        return {
            'stats': self.removal_stats,
            'modifications': self.modifications
        }

    def _process_file_skips(self, file_path: str, skips: list[dict]):
        """Process skips in a single file."""
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

            # Process each skip (in reverse order to maintain line numbers)
            for skip in sorted(skips, key=lambda x: x['line'], reverse=True):
                line_num = skip['line'] - 1  # Convert to 0-based

                if 0 <= line_num < len(modified_lines):
                    original_line = modified_lines[line_num]

                    # Remove the skip decorator
                    new_line = self._remove_skip_decorator(original_line, skip)

                    if new_line != original_line:
                        modified_lines[line_num] = new_line
                        lines_removed += 1
                        self.removal_stats['skips_removed'] += 1

                        # Record modification
                        self.modifications.append({
                            'file': file_path,
                            'line': skip['line'],
                            'original': original_line.strip(),
                            'modified': new_line.strip(),
                            'skip_type': skip['pattern_type'],
                            'reason': skip['reason']
                        })

            # Write back if modified
            if lines_removed > 0:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(modified_lines))

                self.removal_stats['files_modified'] += 1
                print(f"✅ {file_path}: Removed {lines_removed} skip(s)")
            else:
                print(f"⚪ {file_path}: No skips removed")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            self.removal_stats['errors_encountered'] += 1

    def _remove_skip_decorator(self, line: str, skip: dict) -> str:
        """Remove skip decorator from a line."""
        pattern_type = skip['pattern_type']

        # Patterns to remove
        if pattern_type == 'pytest_skip':
            # Remove @pytest.mark.skip(...) or @pytest.mark.skip
            return re.sub(r'@pytest\.mark\.skip(\s*\(.*?\))?\s*$', '', line.strip())

        elif pattern_type == 'pytest_skipif':
            # Remove @pytest.mark.skipif(...)
            return re.sub(r'@pytest\.mark\.skipif\s*\(.*?\)\s*$', '', line.strip())

        elif pattern_type == 'pytest_xfail':
            # Remove @pytest.mark.xfail(...) or @pytest.mark.xfail
            return re.sub(r'@pytest\.mark\.xfail(\s*\(.*?\))?\s*$', '', line.strip())

        elif pattern_type == 'manual_skips':
            # Remove pytest.skip(...) calls
            return re.sub(r'pytest\.skip\s*\(.*?\)\s*$', '', line.strip())

        elif pattern_type == 'decorator_skips':
            # Remove generic skip decorators
            return re.sub(r'@.*skip.*$', '', line.strip())

        # Default: comment out the line
        return f"# REMOVED SKIP: {line.strip()}"

    def validate_removals(self) -> dict:
        """Validate that removals were successful."""
        print("=== Validating Skip Removals ===")

        validation = {
            'files_validated': 0,
            'removals_confirmed': 0,
            'remaining_issues': []
        }

        # Check modified files
        for modification in self.modifications:
            file_path = modification['file']
            full_path = Path('tests') / file_path

            try:
                with open(full_path, encoding='utf-8') as f:
                    content = f.read()

                # Check that the removed skip pattern is no longer present
                original_pattern = modification['original']
                if original_pattern not in content:
                    validation['removals_confirmed'] += 1
                else:
                    validation['remaining_issues'].append({
                        'file': file_path,
                        'issue': 'Skip pattern still present',
                        'pattern': original_pattern
                    })

                validation['files_validated'] += 1

            except Exception as e:
                validation['remaining_issues'].append({
                    'file': file_path,
                    'issue': f'Validation error: {e}'
                })

        return validation

    def generate_wave2a_report(self) -> dict:
        """Generate Wave 2a removal report."""
        print("=== Wave 2a: Remove INVALID Skips - First-Party Patterns ===")

        # Load target data
        wave1d_data = self.load_wave1d_data()
        if not wave1d_data:
            return None

        target_skips = self.get_target_skips(wave1d_data)

        if not target_skips:
            print("⚠️  No target skips found for Wave 2a")
            return {'stats': self.removal_stats, 'target_count': 0}

        # Remove skips
        removal_results = self.remove_first_party_skips(target_skips)

        # Validate removals
        validation_results = self.validate_removals()

        # Create report
        report = {
            'wave': 'Wave 2a',
            'timestamp': '2026-03-25 20:15:00',
            'title': 'Remove INVALID Skips - First-Party Patterns',
            'target_skips_count': len(target_skips),
            'removal_results': removal_results,
            'validation_results': validation_results,
            'summary': {
                'target_skips': len(target_skips),
                'files_processed': self.removal_stats['files_processed'],
                'files_modified': self.removal_stats['files_modified'],
                'skips_removed': self.removal_stats['skips_removed'],
                'errors_encountered': self.removal_stats['errors_encountered'],
                'removals_confirmed': validation_results['removals_confirmed'],
                'success_rate': (validation_results['removals_confirmed'] / max(len(target_skips), 1)) * 100
            }
        }

        # Save report
        with open('artifacts/wave2a_removal_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        summary = report['summary']
        print("\n=== Wave 2a Summary ===")
        print(f"Target skips: {summary['target_skips']}")
        print(f"Files processed: {summary['files_processed']}")
        print(f"Files modified: {summary['files_modified']}")
        print(f"Skips removed: {summary['skips_removed']}")
        print(f"Removals confirmed: {summary['removals_confirmed']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")

        if validation_results['remaining_issues']:
            print(f"\n⚠️  Remaining issues: {len(validation_results['remaining_issues'])}")
            for issue in validation_results['remaining_issues'][:3]:
                print(f"  - {issue['file']}: {issue['issue']}")

        print("\n📄 Report saved to: artifacts/wave2a_removal_report.json")

        return report


def main():
    """Main execution for Wave 2a."""
    remover = FirstPartySkipRemover()
    report = remover.generate_wave2a_report()

    return report


if __name__ == '__main__':
    main()
