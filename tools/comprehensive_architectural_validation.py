#!/usr/bin/env python3
"""
Comprehensive architectural validation.
Run all validation checks to verify architectural compliance.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ComprehensiveArchitecturalValidator:
    """Comprehensive architectural compliance validator."""

    def __init__(self):
        self.validation_results = {}
        self.start_time = datetime.now()

    def validate_layer_gravity(self):
        """Validate layer gravity compliance."""
        print("🔍 Validating layer gravity compliance...")

        try:
            # Run layer violation check
            result = subprocess.run(
                ['python', 'tools/check_layer_violations_fixed.py'],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=60
            )

            layer_results = {
                'exit_code': result.returncode,
                'output': result.stdout,
                'errors': result.stderr,
                'violations': 0,
                'compliant': result.returncode == 0
            }

            # Parse violations from output
            if 'Total violations:' in result.stdout:
                import re
                match = re.search(r'Total violations:\s+(\d+)', result.stdout)
                if match:
                    layer_results['violations'] = int(match.group(1))
                    layer_results['compliant'] = int(match.group(1)) == 0

            self.validation_results['layer_gravity'] = layer_results

            print(f"  ✅ Layer violations: {layer_results['violations']}")
            print(f"     Compliant: {layer_results['compliant']}")

        except subprocess.TimeoutExpired:
            self.validation_results['layer_gravity'] = {
                'exit_code': -1,
                'errors': 'Timeout',
                'compliant': False,
                'violations': -1
            }
            print("  ❌ Layer validation timed out")
        except Exception as e:
            self.validation_results['layer_gravity'] = {
                'exit_code': -1,
                'errors': str(e),
                'compliant': False,
                'violations': -1
            }
            print(f"  ❌ Layer validation error: {e}")

    def validate_silent_swallowers(self):
        """Validate silent swallower compliance."""
        print("🔍 Validating silent swallower compliance...")

        try:
            # Check if silent swallower report exists
            report_file = PROJECT_ROOT / "tools" / "silent_swallower_report.json"
            if report_file.exists():
                with open(report_file) as f:
                    report = json.load(f)

                total_violations = len(report.get('violations', []))
                high_severity = len([v for v in report.get('violations', []) if v.get('severity') == 'HIGH'])
                medium_severity = len([v for v in report.get('violations', []) if v.get('severity') == 'MEDIUM'])
                low_severity = len([v for v in report.get('violations', []) if v.get('severity') == 'LOW'])

                swallower_results = {
                    'total_violations': total_violations,
                    'high_severity': high_severity,
                    'medium_severity': medium_severity,
                    'low_severity': low_severity,
                    'compliant': high_severity == 0,  # High severity must be 0
                    'report_exists': True
                }
            else:
                swallower_results = {
                    'total_violations': -1,
                    'compliant': False,
                    'report_exists': False
                }

            self.validation_results['silent_swallowers'] = swallower_results

            print(f"  ✅ Silent swallower violations: {swallower_results.get('total_violations', 'Unknown')}")
            print(f"     HIGH: {swallower_results.get('high_severity', 'Unknown')}")
            print(f"     MEDIUM: {swallower_results.get('medium_severity', 'Unknown')}")
            print(f"     LOW: {swallower_results.get('low_severity', 'Unknown')}")
            print(f"     Compliant: {swallower_results.get('compliant', False)}")

        except Exception as e:
            self.validation_results['silent_swallowers'] = {
                'total_violations': -1,
                'compliant': False,
                'errors': str(e)
            }
            print(f"  ❌ Silent swallower validation error: {e}")

    def validate_test_enforcement(self):
        """Validate test enforcement compliance."""
        print("🔍 Validating test enforcement compliance...")

        try:
            # Check if test enforcement report exists
            report_file = PROJECT_ROOT / "tools" / "test_enforcement" / "test_violations.json"
            if report_file.exists():
                with open(report_file) as f:
                    report = json.load(f)

                total_violations = len(report.get('violations', []))
                high_severity = len([v for v in report.get('violations', []) if v.get('severity') == 'HIGH'])
                medium_severity = len([v for v in report.get('violations', []) if v.get('severity') == 'MEDIUM'])

                test_results = {
                    'total_violations': total_violations,
                    'high_severity': high_severity,
                    'medium_severity': medium_severity,
                    'compliant': high_severity == 0,  # High severity must be 0
                    'report_exists': True
                }
            else:
                test_results = {
                    'total_violations': -1,
                    'compliant': False,
                    'report_exists': False
                }

            self.validation_results['test_enforcement'] = test_results

            print(f"  ✅ Test enforcement violations: {test_results.get('total_violations', 'Unknown')}")
            print(f"     HIGH: {test_results.get('high_severity', 'Unknown')}")
            print(f"     MEDIUM: {test_results.get('medium_severity', 'Unknown')}")
            print(f"     Compliant: {test_results.get('compliant', False)}")

        except Exception as e:
            self.validation_results['test_enforcement'] = {
                'total_violations': -1,
                'compliant': False,
                'errors': str(e)
            }
            print(f"  ❌ Test enforcement validation error: {e}")

    def validate_adg_separation(self):
        """Validate static/runtime ADG separation."""
        print("🔍 Validating ADG separation...")

        try:
            # Check clean static ADG exists
            clean_adg_dir = PROJECT_ROOT / "artifacts" / "adg_truly_clean"
            runtime_adg_dir = PROJECT_ROOT / "artifacts" / "adg_runtime"

            clean_files = list(clean_adg_dir.glob("*.sqlite")) if clean_adg_dir.exists() else []
            runtime_files = list(runtime_adg_dir.glob("*.sqlite")) if runtime_adg_dir.exists() else []

            separation_results = {
                'clean_static_exists': len(clean_files) > 0,
                'runtime_exists': len(runtime_files) > 0,
                'clean_files': len(clean_files),
                'runtime_files': len(runtime_files),
                'compliant': len(clean_files) > 0 and len(runtime_files) > 0
            }

            self.validation_results['adg_separation'] = separation_results

            print(f"  ✅ Clean static ADG: {separation_results['clean_files']} files")
            print(f"     Runtime ADG: {separation_results['runtime_files']} files")
            print(f"     Separation compliant: {separation_results['compliant']}")

        except Exception as e:
            self.validation_results['adg_separation'] = {
                'clean_static_exists': False,
                'runtime_exists': False,
                'compliant': False,
                'errors': str(e)
            }
            print(f"  ❌ ADG separation validation error: {e}")

    def validate_l_contracts_layer(self):
        """Validate L_CONTRACTS layer implementation."""
        print("🔍 Validating L_CONTRACTS layer...")

        try:
            # Check L_CONTRACTS directory and files
            l_contracts_dir = PROJECT_ROOT / "agentic_core" / "L_CONTRACTS"
            init_file = l_contracts_dir / "__init__.py"
            contract_file = l_contracts_dir / "lifecycle_trace_contract.py"

            l_contracts_results = {
                'directory_exists': l_contracts_dir.exists(),
                'init_exists': init_file.exists(),
                'contract_exists': contract_file.exists(),
                'compliant': l_contracts_dir.exists() and init_file.exists() and contract_file.exists()
            }

            self.validation_results['l_contracts'] = l_contracts_results

            print(f"  ✅ L_CONTRACTS directory: {l_contracts_results['directory_exists']}")
            print(f"     __init__.py: {l_contracts_results['init_exists']}")
            print(f"     Contract file: {l_contracts_results['contract_exists']}")
            print(f"     L_CONTRACTS compliant: {l_contracts_results['compliant']}")

        except Exception as e:
            self.validation_results['l_contracts'] = {
                'directory_exists': False,
                'compliant': False,
                'errors': str(e)
            }
            print(f"  ❌ L_CONTRACTS validation error: {e}")

    def calculate_overall_compliance(self):
        """Calculate overall architectural compliance score."""
        print("📊 Calculating overall compliance...")

        categories = {
            'layer_gravity': {'weight': 0.3, 'required': True},
            'silent_swallowers': {'weight': 0.25, 'required': True},
            'test_enforcement': {'weight': 0.25, 'required': True},
            'adg_separation': {'weight': 0.1, 'required': True},
            'l_contracts': {'weight': 0.1, 'required': True}
        }

        total_score = 0
        total_weight = 0
        compliance_details = {}

        for category, config in categories.items():
            result = self.validation_results.get(category, {})
            compliant = result.get('compliant', False)
            weight = config['weight']
            required = config['required']

            if compliant:
                score = weight
            else:
                score = 0 if required else weight * 0.5  # Non-required get 50% if non-compliant

            compliance_details[category] = {
                'compliant': compliant,
                'score': score,
                'weight': weight,
                'required': required
            }

            total_score += score
            total_weight += weight

        overall_compliance = (total_score / total_weight * 100) if total_weight > 0 else 0

        return overall_compliance, compliance_details

    def generate_comprehensive_report(self):
        """Generate comprehensive validation report."""
        print("📋 Generating comprehensive validation report...")

        overall_compliance, compliance_details = self.calculate_overall_compliance()

        report = {
            'validation_timestamp': self.start_time.isoformat(),
            'validation_duration': str(datetime.now() - self.start_time),
            'overall_compliance': overall_compliance,
            'compliance_details': compliance_details,
            'validation_results': self.validation_results,
            'summary': {
                'total_categories': len(compliance_details),
                'compliant_categories': sum(1 for d in compliance_details.values() if d['compliant']),
                'critical_issues': [
                    cat for cat, details in compliance_details.items()
                    if not details['compliant'] and details['required']
                ]
            },
            'recommendations': self._generate_recommendations(compliance_details)
        }

        report_file = PROJECT_ROOT / "tools" / "comprehensive_architectural_validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"✅ Comprehensive report written to: {report_file}")

        return report

    def _generate_recommendations(self, compliance_details):
        """Generate improvement recommendations."""
        recommendations = []

        for category, details in compliance_details.items():
            if not details['compliant']:
                if category == 'layer_gravity':
                    recommendations.append("Fix remaining layer gravity violations using tools/fix_layer_gravity_violations.py")
                elif category == 'silent_swallowers':
                    recommendations.append("Apply silent swallower fixes using tools/fix_high_severity_silent_swallowers.py")
                elif category == 'test_enforcement':
                    recommendations.append("Fix test enforcement violations using tools/fix_test_enforcement_high.py")
                elif category == 'adg_separation':
                    recommendations.append("Deploy clean static/runtime ADG separation using tools/deploy_clean_adg_separation.py")
                elif category == 'l_contracts':
                    recommendations.append("Ensure L_CONTRACTS layer is properly implemented")

        return recommendations


def main():
    """Main entry point."""
    print("=" * 80)
    print("COMPREHENSIVE ARCHITECTURAL VALIDATOR")
    print("=" * 80)
    print("Running comprehensive architectural compliance validation...")
    print("=" * 80)

    validator = ComprehensiveArchitecturalValidator()

    # Run all validations
    validator.validate_layer_gravity()
    validator.validate_silent_swallowers()
    validator.validate_test_enforcement()
    validator.validate_adg_separation()
    validator.validate_l_contracts_layer()

    # Generate comprehensive report
    report = validator.generate_comprehensive_report()

    print("\n" + "=" * 80)
    print("🎉 COMPREHENSIVE VALIDATION COMPLETED!")
    print(f"✅ Overall compliance: {report['overall_compliance']:.1f}%")
    print(f"📁 Categories compliant: {report['summary']['compliant_categories']}/{report['summary']['total_categories']}")

    if report['summary']['critical_issues']:
        print("\n⚠️  CRITICAL ISSUES:")
        for issue in report['summary']['critical_issues']:
            print(f"   - {issue}")

    if report['recommendations']:
        print("\n📝 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"   - {rec}")
    else:
        print("\n🎉 EXCELLENT ARCHITECTURAL COMPLIANCE!")

    print(f"⏱️  Validation duration: {report['validation_duration']}")
    print("=" * 80)


if __name__ == "__main__":
    main()
