#!/usr/bin/env python3
"""
Identify test violations based on classification and patterns.

VIOLATION TYPES:
1. try/except ImportError → pytest.skip (should use direct import or proper markers)
2. pytest.skip without marker context
3. pytest.importorskip in unmarked test
4. skipping first-party imports
5. skipping core modules
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class TestViolation:
    file_path: str
    test_name: str
    violation_type: str
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    suggested_fix: str
    line_number: int = 0


class ViolationDetector:
    """Detect test violations based on classification and patterns."""

    def __init__(self):
        self.violations = []

        # First-party modules that should never be skipped
        self.first_party_modules = {
            'agentic_core', 'apps_', 'tools', 'ops_scripts', 'tests',
            'system_learning', 'infrastructure', 'artifacts', 'data'
        }

    def detect_violations(self, inventory_file: str, classification_file: str) -> list[TestViolation]:
        """Detect all violations in the test suite."""
        print("🔍 Detecting test violations...")

        # Load data
        with open(inventory_file) as f:
            inventory = json.load(f)

        with open(classification_file) as f:
            classification = json.load(f)

        # Create lookup maps
        test_map = {}
        for test in inventory['tests']:
            key = f"{test['file_path']}::{test['test_name']}"
            test_map[key] = test

        class_map = {}
        for cls in classification['classifications']:
            key = f"{cls['file_path']}::{cls['test_name']}"
            class_map[key] = cls

        # Detect violations
        for key, test_data in test_map.items():
            cls_data = class_map.get(key, {})

            # Skip type violations
            self._check_skip_violations(test_data, cls_data)

            # Core test violations
            self._check_core_violations(test_data, cls_data)

            # First-party import violations
            self._check_first_party_violations(test_data, cls_data)

            # Marker violations
            self._check_marker_violations(test_data, cls_data)

        return self.violations

    def _check_skip_violations(self, test_data: dict, cls_data: dict):
        """Check for improper skip patterns."""
        skip_type = test_data['skip_type']
        dependency = test_data['dependency']

        # VIOLATION: try/except ImportError patterns (detected as runtime_condition)
        if skip_type == 'runtime_condition' and 'ImportError' in test_data.get('skip_reason', ''):
            self.violations.append(TestViolation(
                file_path=test_data['file_path'],
                test_name=test_data['test_name'],
                violation_type='import_error_skip',
                severity='HIGH',
                description='Using try/except ImportError pattern instead of proper marker',
                suggested_fix='Use direct import for core tests or pytest.importorskip with @pytest.mark.optional',
                line_number=test_data['line_number']
            ))

        # VIOLATION: pytest.importorskip without optional marker
        elif skip_type == 'marker' and dependency and cls_data.get('category') != 'OPTIONAL':
            self.violations.append(TestViolation(
                file_path=test_data['file_path'],
                test_name=test_data['test_name'],
                violation_type='unmarked_importorskip',
                severity='HIGH',
                description=f'Using pytest.importorskip for {dependency} without optional marker',
                suggested_fix='Add @pytest.mark.optional or @pytest.mark.external marker',
                line_number=test_data['line_number']
            ))

    def _check_core_violations(self, test_data: dict, cls_data: dict):
        """Check for core test violations."""
        category = cls_data.get('category', 'CORE')
        skip_type = test_data['skip_type']

        # VIOLATION: Core tests should not skip
        if category == 'CORE' and skip_type != 'none':
            self.violations.append(TestViolation(
                file_path=test_data['file_path'],
                test_name=test_data['test_name'],
                violation_type='core_test_skip',
                severity='HIGH',
                description='Core test should not skip - validates required functionality',
                suggested_fix='Remove skip logic or reclassify as OPTIONAL/EXTERNAL',
                line_number=test_data['line_number']
            ))

        # VIOLATION: Core tests with low confidence classification
        elif category == 'CORE' and cls_data.get('confidence', 0) < 0.7:
            self.violations.append(TestViolation(
                file_path=test_data['file_path'],
                test_name=test_data['test_name'],
                violation_type='uncertain_core',
                severity='MEDIUM',
                description='Core test classification has low confidence',
                suggested_fix='Add explicit @pytest.mark.core marker',
                line_number=test_data['line_number']
            ))

    def _check_first_party_violations(self, test_data: dict, cls_data: dict):
        """Check for first-party import violations."""
        dependency = test_data['dependency']
        skip_type = test_data['skip_type']

        if skip_type in ['import_error', 'marker'] and dependency:
            # Check if dependency is first-party
            for fp_module in self.first_party_modules:
                if dependency.startswith(fp_module):
                    self.violations.append(TestViolation(
                        file_path=test_data['file_path'],
                        test_name=test_data['test_name'],
                        violation_type='first_party_skip',
                        severity='HIGH',
                        description=f'Skipping first-party module: {dependency}',
                        suggested_fix='Never skip first-party imports - ensure module is available',
                        line_number=test_data['line_number']
                    ))
                    break

    def _check_marker_violations(self, test_data: dict, cls_data: dict):
        """Check for marker violations."""
        # This would need actual file analysis to detect missing markers
        # For now, flag tests with low confidence that should have explicit markers
        confidence = cls_data.get('confidence', 0)
        category = cls_data.get('category', 'CORE')

        if confidence < 0.6 and category != 'CORE':
            self.violations.append(TestViolation(
                file_path=test_data['file_path'],
                test_name=test_data['test_name'],
                violation_type='missing_marker',
                severity='MEDIUM',
                description=f'Test classification uncertain ({category}) - needs explicit marker',
                suggested_fix=f'Add @pytest.mark.{category.lower()} marker',
                line_number=test_data['line_number']
            ))


def generate_violation_report(violations: list[TestViolation]) -> dict[str, Any]:
    """Generate comprehensive violation report."""
    print(f"📋 Generating violation report for {len(violations)} violations...")

    # Group violations by type and severity
    by_type = {}
    by_severity = {'HIGH': [], 'MEDIUM': [], 'LOW': []}

    for violation in violations:
        # Group by type
        vtype = violation.violation_type
        if vtype not in by_type:
            by_type[vtype] = []
        by_type[vtype].append(violation)

        # Group by severity
        by_severity[violation.severity].append(violation)

    # Build report
    report = {
        "metadata": {
            "scan_timestamp": "2026-03-24T18:31:00Z",
            "total_violations": len(violations),
            "detector_version": "1.0"
        },
        "summary": {
            "by_type": {vtype: len(vlist) for vtype, vlist in by_type.items()},
            "by_severity": {
                "HIGH": len(by_severity['HIGH']),
                "MEDIUM": len(by_severity['MEDIUM']),
                "LOW": len(by_severity['LOW'])
            }
        },
        "violations": []
    }

    # Add violation details
    for violation in violations:
        report["violations"].append({
            "file_path": violation.file_path,
            "test_name": violation.test_name,
            "violation_type": violation.violation_type,
            "severity": violation.severity,
            "description": violation.description,
            "suggested_fix": violation.suggested_fix,
            "line_number": violation.line_number
        })

    return report


def main():
    """Main entry point."""
    print("=" * 80)
    print("TEST VIOLATION DETECTOR")
    print("=" * 80)

    detector = ViolationDetector()

    inventory_file = 'tools/test_enforcement/test_inventory.json'
    classification_file = 'tools/test_enforcement/test_classification.json'

    violations = detector.detect_violations(inventory_file, classification_file)
    report = generate_violation_report(violations)

    # Write violations report
    output_dir = PROJECT_ROOT / "tools" / "test_enforcement"
    violations_file = output_dir / "test_violations.json"

    with open(violations_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, sort_keys=True)

    print(f"✅ Violations report written to: {violations_file}")

    # Print summary
    summary = report["summary"]
    print("\n📊 VIOLATIONS SUMMARY:")
    print(f"  Total violations: {report['metadata']['total_violations']}")

    print("\nBy severity:")
    for severity, count in summary["by_severity"].items():
        print(f"  {severity}: {count}")

    print("\nBy type:")
    for vtype, count in summary["by_type"].items():
        print(f"  {vtype}: {count}")

    # Show high-priority violations
    high_priority_violations = [v for v in violations if v.severity == 'HIGH']
    if high_priority_violations:
        print("\n🚨 HIGH PRIORITY VIOLATIONS (sample):")
        for violation in high_priority_violations[:5]:
            print(f"  {violation.file_path}:{violation.test_name}")
            print(f"    {violation.description}")
            print(f"    Fix: {violation.suggested_fix}")

        if len(high_priority_violations) > 5:
            print(f"  ... and {len(high_priority_violations) - 5} more")

    print("\n" + "=" * 80)
    print("NEXT STEP: Refactor tests to fix violations")
    print("=" * 80)


if __name__ == "__main__":
    main()
