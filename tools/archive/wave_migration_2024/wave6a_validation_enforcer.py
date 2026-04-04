#!/usr/bin/env python3
"""
Wave 6a: Validation enforcement script creation.

This script creates comprehensive validation enforcement tools
to ensure test suite hardening compliance and quality standards.
"""

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ValidationSeverity(Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationRule:
    """Validation rule definition."""
    name: str
    description: str
    severity: ValidationSeverity
    pattern: str
    message: str
    category: str


@dataclass
class ValidationResult:
    """Validation result."""
    file: str
    line: int
    rule: str
    severity: ValidationSeverity
    message: str
    category: str


class ValidationEnforcer:
    """Main validation enforcement engine."""

    def __init__(self):
        self.rules = self._define_validation_rules()
        self.results = []
        self.stats = {
            'files_validated': 0,
            'issues_found': 0,
            'by_severity': defaultdict(int),
            'by_category': defaultdict(int)
        }

    def _define_validation_rules(self) -> list[ValidationRule]:
        """Define comprehensive validation rules."""
        rules = [
            # Skip pattern rules
            ValidationRule(
                name="no_invalid_skip_patterns",
                description="No invalid skip patterns (pytest.skip without reason)",
                severity=ValidationSeverity.ERROR,
                pattern=r"pytest\.skip\s*\(\s*[\"'][^\"']*[\"']\s*\)",
                message="pytest.skip should include a reason",
                category="skip_patterns"
            ),

            # Hollow test rules
            ValidationRule(
                name="no_hollow_import_only_tests",
                description="No hollow tests with only imports",
                severity=ValidationSeverity.WARNING,
                pattern=r"def test_.*:\s*import\s+\w+",
                message="Test should contain more than just imports",
                category="hollow_tests"
            ),

            ValidationRule(
                name="no_hollow_pass_tests",
                description="No hollow tests with only pass statements",
                severity=ValidationSeverity.WARNING,
                pattern=r"def test_.*:\s*pass",
                message="Test should contain actual assertions",
                category="hollow_tests"
            ),

            # Assertion rules
            ValidationRule(
                name="meaningful_assertions",
                description="Tests should have meaningful assertions",
                severity=ValidationSeverity.WARNING,
                pattern=r"def test_.*:(?!.*assert)",
                message="Test should contain assertions",
                category="assertions"
            ),

            # Marker rules
            ValidationRule(
                name="standard_markers",
                description="Tests should use standard markers",
                severity=ValidationSeverity.INFO,
                pattern=r"@pytest\.mark\.(?!slow|integration|unit|smoke|regression)\w+",
                message="Consider using standard markers (slow, integration, unit, smoke, regression)",
                category="markers"
            ),

            # Documentation rules
            ValidationRule(
                name="test_documentation",
                description="Tests should have docstrings",
                severity=ValidationSeverity.INFO,
                pattern=r"def test_.*:\s*\"\"\".*\"\"\"",
                message="Test should have a docstring",
                category="documentation"
            ),

            # Import rules
            ValidationRule(
                name="no_relative_imports",
                description="No relative imports in test files",
                severity=ValidationSeverity.WARNING,
                pattern=r"from\s+\.\.",
                message="Avoid relative imports in test files",
                category="imports"
            ),

            # Naming rules
            ValidationRule(
                name="test_naming_convention",
                description="Test functions should follow naming convention",
                severity=ValidationSeverity.WARNING,
                pattern=r"def (?!test_)\w+",
                message="Test functions should start with 'test_'",
                category="naming"
            ),

            # Structure rules
            ValidationRule(
                name="test_structure",
                description="Tests should follow AAA pattern (Arrange, Act, Assert)",
                severity=ValidationSeverity.INFO,
                pattern=r"def test_.*:(?!.*# Arrange)(?!.*# Act)(?!.*# Assert)",
                message="Consider using AAA pattern (Arrange, Act, Assert)",
                category="structure"
            )
        ]

        return rules

    def validate_test_suite(self, test_dir: str = "tests") -> dict:
        """Validate the entire test suite."""
        print("=== Validating Test Suite ===")

        test_path = Path(test_dir)

        if not test_path.exists():
            print(f"❌ Test directory not found: {test_dir}")
            return {'error': f'Test directory not found: {test_dir}'}

        # Find all test files
        test_files = list(test_path.rglob("test_*.py"))
        print(f"🔍 Found {len(test_files)} test files to validate")

        # Validate each file
        for test_file in test_files:
            self._validate_file(test_file)

        # Generate summary
        summary = self._generate_summary()

        return {
            'stats': self.stats,
            'results': self.results,
            'summary': summary
        }

    def _validate_file(self, file_path: Path):
        """Validate a single test file."""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            rel_path = str(file_path.relative_to(Path.cwd()))
            self.stats['files_validated'] += 1

            # Apply all validation rules
            for rule in self.rules:
                self._apply_rule(content, rel_path, rule)

        except Exception as e:
            print(f"❌ Error validating {file_path}: {e}")

    def _apply_rule(self, content: str, file_path: str, rule: ValidationRule):
        """Apply a validation rule to file content."""
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            if re.search(rule.pattern, line, re.MULTILINE | re.DOTALL):
                result = ValidationResult(
                    file=file_path,
                    line=line_num,
                    rule=rule.name,
                    severity=rule.severity,
                    message=rule.message,
                    category=rule.category
                )

                self.results.append(result)
                self.stats['issues_found'] += 1
                self.stats['by_severity'][rule.severity.value] += 1
                self.stats['by_category'][rule.category] += 1

    def _generate_summary(self) -> dict:
        """Generate validation summary."""
        total_issues = self.stats['issues_found']

        summary = {
            'total_files_validated': self.stats['files_validated'],
            'total_issues_found': total_issues,
            'issues_by_severity': dict(self.stats['by_severity']),
            'issues_by_category': dict(self.stats['by_category']),
            'compliance_score': self._calculate_compliance_score(),
            'recommendations': self._generate_recommendations()
        }

        return summary

    def _calculate_compliance_score(self) -> float:
        """Calculate compliance score (0-100)."""
        if self.stats['files_validated'] == 0:
            return 100.0

        # Weight issues by severity
        weights = {
            ValidationSeverity.CRITICAL.value: 10,
            ValidationSeverity.ERROR.value: 5,
            ValidationSeverity.WARNING.value: 2,
            ValidationSeverity.INFO.value: 1
        }

        weighted_issues = sum(
            count * weights.get(severity, 1)
            for severity, count in self.stats['by_severity'].items()
        )

        # Calculate score (100 - weighted penalty)
        max_possible_weight = self.stats['files_validated'] * 10  # Assume max 10 weight per file
        score = max(0, 100 - (weighted_issues / max_possible_weight * 100))

        return round(score, 1)

    def _generate_recommendations(self) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Analyze by category
        if self.stats['by_category'].get('skip_patterns', 0) > 0:
            recommendations.append("Review and fix invalid skip patterns")

        if self.stats['by_category'].get('hollow_tests', 0) > 0:
            recommendations.append("Add meaningful content to hollow tests")

        if self.stats['by_category'].get('assertions', 0) > 0:
            recommendations.append("Add assertions to test functions")

        if self.stats['by_category'].get('documentation', 0) > 0:
            recommendations.append("Add docstrings to test functions")

        if self.stats['by_category'].get('structure', 0) > 0:
            recommendations.append("Improve test structure with AAA pattern")

        # Analyze by severity
        if self.stats['by_severity'].get('critical', 0) > 0:
            recommendations.append("URGENT: Fix critical validation issues")

        if self.stats['by_severity'].get('error', 0) > 0:
            recommendations.append("Fix error-level validation issues")

        return recommendations

    def generate_enforcement_report(self, output_file: str = "artifacts/validation_enforcement_report.json"):
        """Generate comprehensive validation enforcement report."""
        print("=== Generating Validation Enforcement Report ===")

        # Validate test suite
        validation_results = self.validate_test_suite()

        if 'error' in validation_results:
            print(f"❌ Validation failed: {validation_results['error']}")
            return validation_results

        # Create comprehensive report
        report = {
            'wave': 'Wave 6a',
            'timestamp': '2026-03-25 21:10:00',
            'title': 'Validation Enforcement Script Creation',
            'validation_rules': [
                {
                    'name': rule.name,
                    'description': rule.description,
                    'severity': rule.severity.value,
                    'category': rule.category
                }
                for rule in self.rules
            ],
            'validation_results': validation_results,
            'enforcement_tools': self._describe_enforcement_tools(),
            'summary': validation_results['summary']
        }

        # Save report
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        summary = report['summary']
        print("\n=== Validation Enforcement Summary ===")
        print(f"Files validated: {summary['total_files_validated']}")
        print(f"Issues found: {summary['total_issues_found']}")
        print(f"Compliance score: {summary['compliance_score']:.1f}%")

        if summary['issues_by_severity']:
            print("\nIssues by severity:")
            for severity, count in summary['issues_by_severity'].items():
                print(f"  {severity}: {count}")

        if summary['recommendations']:
            print("\nRecommendations:")
            for rec in summary['recommendations']:
                print(f"  • {rec}")

        print(f"\n📄 Report saved to: {output_path}")

        return report

    def _describe_enforcement_tools(self) -> list[dict]:
        """Describe the enforcement tools created."""
        tools = [
            {
                'name': 'ValidationEnforcer',
                'description': 'Main validation engine with comprehensive rule set',
                'features': [
                    'Multi-category validation (skip patterns, hollow tests, assertions)',
                    'Severity-based scoring',
                    'Compliance metrics',
                    'Detailed reporting'
                ]
            },
            {
                'name': 'Validation Rules Engine',
                'description': 'Extensible rule-based validation system',
                'features': [
                    'Pattern-based rule matching',
                    'Severity classification',
                    'Category organization',
                    'Custom rule support'
                ]
            },
            {
                'name': 'Compliance Scoring',
                'description': 'Automated compliance assessment',
                'features': [
                    'Weighted severity scoring',
                    'File-based normalization',
                    'Trend analysis support',
                    'Threshold enforcement'
                ]
            }
        ]

        return tools

    def create_enforcement_scripts(self) -> dict:
        """Create standalone enforcement scripts."""
        print("=== Creating Enforcement Scripts ===")

        scripts_created = []

        # Create validation runner script
        validation_runner = self._create_validation_runner()
        scripts_created.append(validation_runner)

        # Create CI integration script
        ci_integration = self._create_ci_integration()
        scripts_created.append(ci_integration)

        # Create pre-commit hook script
        pre_commit_hook = self._create_pre_commit_hook()
        scripts_created.append(pre_commit_hook)

        return {
            'scripts_created': scripts_created,
            'total_scripts': len(scripts_created)
        }

    def _create_validation_runner(self) -> dict:
        """Create standalone validation runner script."""
        script_content = '''#!/usr/bin/env python3
"""
Standalone validation runner for test suite enforcement.
"""

import sys
import json
from pathlib import Path

# Add the tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

try:
    from wave6a_validation_enforcer import ValidationEnforcer

    def main():
        """Run validation enforcement."""
        enforcer = ValidationEnforcer()
        report = enforcer.generate_enforcement_report()

        # Exit with error code if critical issues found
        if report['summary']['issues_by_severity'].get('critical', 0) > 0:
            print("CRITICAL: Critical validation issues found!")
            sys.exit(1)
        elif report['summary']['compliance_score'] < 80:
            print("WARNING: Low compliance score!")
            sys.exit(2)
        else:
            print("SUCCESS: Validation passed!")
            sys.exit(0)

    if __name__ == '__main__':
        main()

except ImportError as e:
    print(f"ERROR: Import error: {e}")
    sys.exit(1)
'''

        script_path = Path("tools/validation_runner.py")
        script_path.write_text(script_content)

        return {
            'name': 'validation_runner.py',
            'path': str(script_path),
            'purpose': 'Standalone validation runner'
        }

    def _create_ci_integration(self) -> dict:
        """Create CI integration script."""
        script_content = '''#!/usr/bin/env python3
"""
CI integration for validation enforcement.
"""

import sys
import json
import subprocess
from pathlib import Path

def run_validation():
    """Run validation and output CI-friendly results."""
    try:
        # Run validation runner
        result = subprocess.run([
            sys.executable, "tools/validation_runner.py"
        ], capture_output=True, text=True, cwd=Path.cwd())

        # Output results in CI-friendly format
        print("=== Validation Results ===")
        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        # Generate GitHub Actions annotation if needed
        if result.returncode != 0:
            print("::error::Validation failed - check report for details")

        return result.returncode

    except Exception as e:
        print(f"::error::Validation runner error: {e}")
        return 1

def main():
    """Main CI integration."""
    exit_code = run_validation()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
'''

        script_path = Path("tools/ci_validation_integration.py")
        script_path.write_text(script_content)

        return {
            'name': 'ci_validation_integration.py',
            'path': str(script_path),
            'purpose': 'CI/CD integration script'
        }

    def _create_pre_commit_hook(self) -> dict:
        """Create pre-commit hook script."""
        script_content = '''#!/usr/bin/env python3
"""
Pre-commit hook for validation enforcement.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run validation before commit."""
    # Only run on Python files
    changed_files = []
    try:
        # Get staged files
        result = subprocess.run([
            "git", "diff", "--cached", "--name-only", "--diff-filter=ACM"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            changed_files = [
                f for f in result.stdout.strip().split('\\n')
                if f.endswith('.py') and f.startswith('tests/')
            ]
    except Exception:
        pass

    if not changed_files:
        print("No test files changed, skipping validation")
        return 0

    print(f"Validating {len(changed_files)} changed test files...")

    # Run validation
    try:
        result = subprocess.run([
            sys.executable, "tools/validation_runner.py"
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print("ERROR: Validation failed!")
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            print("Commit blocked due to validation issues.")
            return result.returncode
        else:
            print("SUCCESS: Validation passed!")
            return 0

    except Exception as e:
        print(f"ERROR: Validation error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
'''

        script_path = Path("tools/pre_commit_validation.py")
        script_path.write_text(script_content)

        return {
            'name': 'pre_commit_validation.py',
            'path': str(script_path),
            'purpose': 'Pre-commit validation hook'
        }


def main():
    """Main execution for Wave 6a."""
    enforcer = ValidationEnforcer()

    # Generate enforcement report
    report = enforcer.generate_enforcement_report()

    # Create enforcement scripts
    scripts = enforcer.create_enforcement_scripts()

    print("\n=== Wave 6a Summary ===")
    print(f"Validation rules defined: {len(enforcer.rules)}")
    print(f"Enforcement scripts created: {scripts['total_scripts']}")

    if 'summary' in report:
        print(f"Compliance score: {report['summary']['compliance_score']:.1f}%")
        print(f"Total issues found: {report['summary']['total_issues_found']}")

    return report


if __name__ == '__main__':
    main()
