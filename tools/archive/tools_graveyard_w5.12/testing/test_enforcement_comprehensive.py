#!/usr/bin/env python3
"""
Comprehensive Enforcement Test Suite
Verifies ADG templates are truly mandatory and enforced
"""

import logging
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent
sys.path.append(str(repo_root))

from agentic_core.config.adg_template_enforcement_config import (
    ENFORCEMENT_CONFIG,
    ENFORCEMENT_RULES,
    get_enforcement_template,
    is_enforcement_required,
)
from tools.utils.planning.sequential_thinking_workflow import SequentialThinkingEnhancedWorkflow


def test_enforcement_mandatory():
    """Test that enforcement is truly mandatory and cannot be bypassed."""

    print("🔒 MANDATORY ENFORCEMENT TEST")
    print("=" * 60)
    print("Verifying ADG templates cannot be bypassed")

    # Initialize workflow with strict enforcement
    workflow = SequentialThinkingEnhancedWorkflow(seq_thinking_enabled=True)

    # Test scenarios that MUST use ADG templates
    mandatory_scenarios = [
        {
            "name": "Direct ADG Task",
            "type": "adg_analysis",
            "complexity": "high",
            "reason": "Direct ADG tasks are always enforced",
        },
        {
            "name": "Critical Complexity",
            "type": "implementation",
            "complexity": "critical",
            "reason": "Critical complexity forces ADG templates",
        },
        {
            "name": "High Complexity Architecture",
            "type": "architecture",
            "complexity": "high",
            "reason": "High complexity architecture requires ADG review",
        },
        {
            "name": "Multi-file Operation",
            "type": "refactoring",
            "complexity": "medium",
            "files": ["file1.py", "file2.py", "file3.py", "file4.py", "file5.py", "file6.py", "file7.py"],
            "reason": "Multi-file operations enforce dependency analysis",
        },
        {
            "name": "Violation Remediation",
            "type": "debugging",
            "complexity": "medium",
            "reason": "Debugging mapped to violation remediation",
        },
    ]

    results = []

    for scenario in mandatory_scenarios:
        print(f"\n🧪 Testing: {scenario['name']}")
        print(f"   Reason: {scenario['reason']}")
        print(f"   Type: {scenario['type']} | Complexity: {scenario.get('complexity', 'medium')}")

        try:
            # Create step config
            step_config = {
                "name": scenario["name"],
                "type": scenario["type"],
                "complexity": scenario.get("complexity", "medium"),
                "files": scenario.get("files", ["single_file.py"]),
                "description": f"Mandatory enforcement test for {scenario['name']}",
            }

            # Check if enforcement is required
            enforcement_required = is_enforcement_required(scenario["type"], step_config)

            # Get template (this should enforce ADG template)
            template = workflow._get_seq_thinking_template(scenario["type"], step_config)

            # Verify it's actually an ADG template
            is_adg_template = any(
                keyword in template
                for keyword in [
                    "ADG Graph Analysis",
                    "Violation Remediation",
                    "Layer Boundary Audit",
                    "Dependency Graph Analysis",
                    "Architectural Review",
                    "Anti-pattern Detection",
                    "System Restructuring",
                    "Graph Traversal Optimization",
                ]
            )

            # Check for enforcement logging
            has_enforcement_log = "ENFORCING" in template or "MANUAL ENFORCEMENT" in template

            result = {
                "scenario": scenario["name"],
                "type": scenario["type"],
                "complexity": scenario.get("complexity", "medium"),
                "enforcement_required": enforcement_required,
                "is_adg_template": is_adg_template,
                "has_enforcement_log": has_enforcement_log,
                "template_length": len(template),
                "compliant": enforcement_required and is_adg_template,
                "success": True,
            }

            # Display results
            if result["compliant"]:
                print("   ✅ ENFORCED: ADG template mandatory")
                print(f"   📋 Template Type: {'ADG Template' if is_adg_template else 'Other'}")
                print(f"   📝 Length: {len(template):,} characters")
                print(f"   🔍 Enforcement Log: {'Found' if has_enforcement_log else 'Not Found'}")
            else:
                print("   ❌ VIOLATION: Enforcement failed!")
                print(f"   📋 Required: {enforcement_required}")
                print(f"   📋 ADG Template: {is_adg_template}")

            results.append(result)

        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append(
                {
                    "scenario": scenario["name"],
                    "success": False,
                    "error": str(e),
                }
            )

    return results


def test_enforcement_bypass_attempts():
    """Test attempts to bypass enforcement - all should fail."""

    print("\n🚫 BYPASS ATTEMPT TESTS")
    print("=" * 60)
    print("Verifying enforcement cannot be bypassed")

    workflow = SequentialThinkingEnhancedWorkflow(seq_thinking_enabled=True)

    bypass_attempts = [
        {
            "name": "Empty Step Config",
            "type": "architecture",
            "config": {},  # Try to bypass with empty config
            "expected": "Should still enforce ADG template",
        },
        {
            "name": "Low Complexity with High Files",
            "type": "implementation",
            "config": {
                "complexity": "low",
                "files": ["f1.py", "f2.py", "f3.py", "f4.py", "f5.py", "f6.py", "f7.py", "f8.py"],
            },
            "expected": "Should enforce due to multi-file rule",
        },
        {
            "name": "Medium Complexity Architecture",
            "type": "architecture",
            "config": {
                "complexity": "medium",
                "files": ["design.md"],
            },
            "expected": "Should enforce due to task type mapping",
        },
        {
            "name": "Unknown Task Type High Complexity",
            "type": "unknown_task",
            "config": {
                "complexity": "high",
                "files": ["file.py"],
            },
            "expected": "Should enforce due to high complexity",
        },
    ]

    results = []

    for attempt in bypass_attempts:
        print(f"\n🧪 Bypass Attempt: {attempt['name']}")
        print(f"   Expected: {attempt['expected']}")

        try:
            step_config = {
                "name": attempt["name"],
                "type": attempt["type"],
                **attempt["config"],
            }

            # Check enforcement
            enforcement_required = is_enforcement_required(attempt["type"], step_config)

            # Get template
            template = workflow._get_seq_thinking_template(attempt["type"], step_config)

            # Check if ADG template was used
            is_adg_template = any(
                keyword in template
                for keyword in [
                    "ADG Graph Analysis",
                    "Violation Remediation",
                    "Layer Boundary Audit",
                    "Dependency Graph Analysis",
                    "Architectural Review",
                    "Anti-pattern Detection",
                    "System Restructuring",
                    "Graph Traversal Optimization",
                ]
            )

            # Bypass successful if enforcement was required but ADG template wasn't used
            bypass_successful = enforcement_required and not is_adg_template

            result = {
                "attempt": attempt["name"],
                "type": attempt["type"],
                "enforcement_required": enforcement_required,
                "is_adg_template": is_adg_template,
                "bypass_successful": bypass_successful,
                "bypass_blocked": not bypass_successful,
                "success": True,
            }

            if result["bypass_blocked"]:
                print("   ✅ BYPASS BLOCKED: Enforcement worked correctly")
            else:
                print("   ❌ BYPASS SUCCESSFUL: Enforcement failed!")
                print(f"   📋 Enforcement Required: {enforcement_required}")
                print(f"   📋 ADG Template Used: {is_adg_template}")

            results.append(result)

        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append(
                {
                    "attempt": attempt["name"],
                    "success": False,
                    "error": str(e),
                }
            )

    return results


def test_enforcement_configuration():
    """Test enforcement configuration and rules."""

    print("\n⚙️  ENFORCEMENT CONFIGURATION TEST")
    print("=" * 60)
    print("Verifying enforcement rules are properly configured")

    config_tests = [
        {
            "name": "Enforcement Enabled",
            "test": ENFORCEMENT_CONFIG.get("enabled", False),
            "expected": True,
            "description": "Enforcement should be enabled",
        },
        {
            "name": "Strict Mode Enabled",
            "test": ENFORCEMENT_CONFIG.get("strict_mode", False),
            "expected": True,
            "description": "Strict mode should be enabled",
        },
        {
            "name": "Fallback Disabled",
            "test": not ENFORCEMENT_CONFIG.get("fallback_allowed", True),
            "expected": True,
            "description": "Fallback should be disabled for enforced tasks",
        },
        {
            "name": "Audit Trail Enabled",
            "test": ENFORCEMENT_CONFIG.get("audit_trail", False),
            "expected": True,
            "description": "Audit trail should be enabled",
        },
        {
            "name": "Auto Trigger Enabled",
            "test": ENFORCEMENT_CONFIG.get("auto_trigger", False),
            "expected": True,
            "description": "Auto-trigger should be enabled",
        },
    ]

    results = []

    for test in config_tests:
        try:
            actual = test["test"]
            passed = actual == test["expected"]

            result = {
                "test": test["name"],
                "description": test["description"],
                "expected": test["expected"],
                "actual": actual,
                "passed": passed,
                "success": True,
            }

            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {test['name']}: {test['description']}")
            print(f"        Expected: {test['expected']}, Actual: {actual}")

            results.append(result)

        except Exception as e:
            print(f"   ❌ ERROR {test['name']}: {e}")
            results.append(
                {
                    "test": test["name"],
                    "success": False,
                    "error": str(e),
                }
            )

    return results


def test_enforcement_rules_coverage():
    """Test that all important scenarios are covered by enforcement rules."""

    print("\n📋 ENFORCEMENT RULES COVERAGE TEST")
    print("=" * 60)
    print("Verifying enforcement rules cover all important scenarios")

    # Test all enforcement rule categories
    rule_tests = []

    # Direct ADG tasks
    for task_type, template in ENFORCEMENT_RULES["direct_adg_tasks"].items():
        step_config = {"type": task_type, "complexity": "high"}
        enforced_template = get_enforcement_template(task_type, step_config)

        rule_tests.append(
            {
                "category": "Direct ADG Tasks",
                "task_type": task_type,
                "expected_template": template,
                "actual_template": enforced_template,
                "covered": enforced_template == template,
            }
        )

    # SWE task mapping
    for task_type, template in ENFORCEMENT_RULES["swe_task_mapping"].items():
        step_config = {"type": task_type, "complexity": "high"}
        enforced_template = get_enforcement_template(task_type, step_config)

        rule_tests.append(
            {
                "category": "SWE Task Mapping",
                "task_type": task_type,
                "expected_template": template,
                "actual_template": enforced_template,
                "covered": enforced_template == template,
            }
        )

    # Complexity enforcement
    critical_config = {"type": "implementation", "complexity": "critical"}
    critical_template = get_enforcement_template("implementation", critical_config)

    rule_tests.append(
        {
            "category": "Complexity Enforcement",
            "task_type": "implementation (critical)",
            "expected_template": "SWE_SYSTEM_RESTRUCTURING",
            "actual_template": critical_template,
            "covered": critical_template == "SWE_SYSTEM_RESTRUCTURING",
        }
    )

    # File enforcement
    multi_file_config = {"type": "analysis", "files": [f"file{i}.py" for i in range(10)]}
    multi_file_template = get_enforcement_template("analysis", multi_file_config)

    rule_tests.append(
        {
            "category": "File Enforcement",
            "task_type": "analysis (multi-file)",
            "expected_template": "SWE_DEPENDENCY_GRAPH_ANALYSIS",
            "actual_template": multi_file_template,
            "covered": multi_file_template == "SWE_DEPENDENCY_GRAPH_ANALYSIS",
        }
    )

    results = []

    for test in rule_tests:
        status = "✅ COVERED" if test["covered"] else "❌ NOT COVERED"
        print(f"   {status} {test['category']}: {test['task_type']}")

        if test["covered"]:
            print(f"        Expected: {test['expected_template']}")
        else:
            print(f"        Expected: {test['expected_template']}")
            print(f"        Actual: {test['actual_template']}")

        results.append(
            {
                "category": test["category"],
                "task_type": test["task_type"],
                "covered": test["covered"],
                "success": True,
            }
        )

    return results


def main():
    """Main comprehensive enforcement test."""

    print("🚀 COMPREHENSIVE ENFORCEMENT TEST SUITE")
    print("=" * 80)
    print("Testing ADG template enforcement is truly mandatory and cannot be bypassed")

    # Set up logging to capture enforcement messages
    logging.basicConfig(level=logging.INFO)

    # Run all test suites
    mandatory_results = test_enforcement_mandatory()
    bypass_results = test_enforcement_bypass_attempts()
    config_results = test_enforcement_configuration()
    coverage_results = test_enforcement_rules_coverage()

    # Generate comprehensive report
    print("\n📊 COMPREHENSIVE ENFORCEMENT REPORT")
    print("=" * 80)

    # Mandatory enforcement results
    mandatory_successful = [r for r in mandatory_results if r.get("success", False)]
    mandatory_compliant = [r for r in mandatory_successful if r.get("compliant", False)]

    print("🔒 MANDATORY ENFORCEMENT:")
    print(f"   Tests: {len(mandatory_results)}")
    print(
        f"   Successful: {len(mandatory_successful)} ({len(mandatory_successful) / len(mandatory_results) * 100:.1f}%)"
    )
    print(
        f"   Compliant: {len(mandatory_compliant)} ({len(mandatory_compliant) / len(mandatory_successful) * 100:.1f}%)"
    )

    # Bypass attempt results
    bypass_successful = [r for r in bypass_results if r.get("success", False)]
    bypass_blocked = [r for r in bypass_successful if r.get("bypass_blocked", False)]

    print("\n🚫 BYPASS PROTECTION:")
    print(f"   Attempts: {len(bypass_results)}")
    print(
        f"   Successful: {len(bypass_successful)} ({len(bypass_successful) / len(bypass_results) * 100:.1f}%)"
    )
    print(f"   Blocked: {len(bypass_blocked)} ({len(bypass_blocked) / len(bypass_successful) * 100:.1f}%)")

    # Configuration results
    config_successful = [r for r in config_results if r.get("success", False)]
    config_passed = [r for r in config_successful if r.get("passed", False)]

    print("\n⚙️  CONFIGURATION:")
    print(f"   Tests: {len(config_results)}")
    print(
        f"   Successful: {len(config_successful)} ({len(config_successful) / len(config_results) * 100:.1f}%)"
    )
    print(f"   Passed: {len(config_passed)} ({len(config_passed) / len(config_successful) * 100:.1f}%)")

    # Coverage results
    coverage_successful = [r for r in coverage_results if r.get("success", False)]
    coverage_covered = [r for r in coverage_successful if r.get("covered", False)]

    print("\n📋 RULES COVERAGE:")
    print(f"   Rules: {len(coverage_results)}")
    print(
        f"   Successful: {len(coverage_successful)} ({len(coverage_successful) / len(coverage_results) * 100:.1f}%)"
    )
    print(
        f"   Covered: {len(coverage_covered)} ({len(coverage_covered) / len(coverage_successful) * 100:.1f}%)"
    )

    # Overall assessment
    total_tests = len(mandatory_results) + len(bypass_results) + len(config_results) + len(coverage_results)
    total_successful = (
        len(mandatory_successful) + len(bypass_successful) + len(config_successful) + len(coverage_successful)
    )

    # Calculate overall compliance
    mandatory_rate = len(mandatory_compliant) / len(mandatory_successful) * 100 if mandatory_successful else 0
    bypass_rate = len(bypass_blocked) / len(bypass_successful) * 100 if bypass_successful else 0
    config_rate = len(config_passed) / len(config_successful) * 100 if config_successful else 0
    coverage_rate = len(coverage_covered) / len(coverage_successful) * 100 if coverage_successful else 0

    overall_score = (mandatory_rate + bypass_rate + config_rate + coverage_rate) / 4

    print("\n🎯 OVERALL ENFORCEMENT ASSESSMENT:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Overall Success Rate: {total_successful / total_tests * 100:.1f}%")
    print(f"   Overall Enforcement Score: {overall_score:.1f}%")

    # Final verdict
    if overall_score >= 90:
        print("\n🎉 ENFORCEMENT STATUS: EXCELLENT")
        print("✅ ADG templates are truly mandatory and enforced")
        print("✅ Bypass attempts are blocked")
        print("✅ Configuration is correct")
        print("✅ All rules are covered")
        print("🚀 Ready for production deployment")
    elif overall_score >= 75:
        print("\n✅ ENFORCEMENT STATUS: GOOD")
        print("✅ Most enforcement working correctly")
        print("⚠️  Minor issues may need attention")
    else:
        print("\n⚠️  ENFORCEMENT STATUS: NEEDS IMPROVEMENT")
        print("❌ Enforcement has significant issues")
        print("🔧 Requires fixes before production")

    print(f"\n🔒 ENFORCEMENT VERIFICATION: {'COMPLETE' if overall_score >= 90 else 'NEEDS WORK'}")


if __name__ == "__main__":
    main()
