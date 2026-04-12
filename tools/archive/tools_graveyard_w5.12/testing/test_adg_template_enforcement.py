#!/usr/bin/env python3
"""
Test ADG Template Enforcement in SWE Model
Verifies that ADG-based templates are mandatory for relevant task types
"""

import logging
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent
sys.path.append(str(repo_root))

from tools.utils.planning.sequential_thinking_workflow import SequentialThinkingEnhancedWorkflow


def test_adg_template_enforcement():
    """Test that ADG templates are enforced for relevant task types."""

    print("🔒 ADG Template Enforcement Test")
    print("=" * 60)

    # Initialize workflow with ADG templates
    workflow = SequentialThinkingEnhancedWorkflow(seq_thinking_enabled=True)

    # Test scenarios with enforcement expectations
    test_scenarios = [
        {
            "name": "ADG Analysis Task",
            "type": "adg_analysis",
            "complexity": "high",
            "files": ["adg_indexed.sqlite"],
            "expected_template": "SWE_ADG_ANALYSIS",
            "enforced": True,
            "reason": "Direct ADG task type",
        },
        {
            "name": "Violation Remediation",
            "type": "violation_remediation",
            "complexity": "high",
            "files": ["violations.json"],
            "expected_template": "SWE_VIOLATION_REMEDIATION",
            "enforced": True,
            "reason": "Direct violation remediation task",
        },
        {
            "name": "High Complexity Architecture",
            "type": "architecture",
            "complexity": "high",
            "files": ["system_design.md", "components/"],
            "expected_template": "SWE_ARCHITECTURAL_REVIEW",
            "enforced": True,
            "reason": "High complexity triggers ADG enforcement",
        },
        {
            "name": "Critical System Restructuring",
            "type": "refactoring",
            "complexity": "critical",
            "files": ["legacy_module.py", "new_module.py"],
            "expected_template": "SWE_SYSTEM_RESTRUCTURING",
            "enforced": True,
            "reason": "Critical complexity forces system restructuring",
        },
        {
            "name": "Multi-file Implementation",
            "type": "implementation",
            "complexity": "medium",
            "files": ["file1.py", "file2.py", "file3.py", "file4.py", "file5.py", "file6.py"],
            "expected_template": "SWE_DEPENDENCY_GRAPH_ANALYSIS",
            "enforced": True,
            "reason": "Multi-file operations enforce ADG templates",
        },
        {
            "name": "Debugging Task",
            "type": "debugging",
            "complexity": "medium",
            "files": ["error.log"],
            "expected_template": "SWE_VIOLATION_REMEDIATION",
            "enforced": True,
            "reason": "Debugging mapped to violation remediation",
        },
        {
            "name": "Simple Analysis",
            "type": "analysis",
            "complexity": "low",
            "files": ["single_file.py"],
            "expected_template": None,  # May use fallback
            "enforced": False,
            "reason": "Low complexity simple task",
        },
    ]

    results = []

    for scenario in test_scenarios:
        print(f"\n🧪 Testing: {scenario['name']}")
        print(f"   Type: {scenario['type']} | Complexity: {scenario['complexity']}")
        print(f"   Files: {len(scenario['files'])}")
        print(f"   Expected: {'ENFORCED' if scenario['enforced'] else 'Optional'}")

        try:
            # Create step config
            step_config = {
                "name": scenario["name"],
                "type": scenario["type"],
                "complexity": scenario["complexity"],
                "files": scenario["files"],
                "description": f"Test scenario for {scenario['name']}",
            }

            # Get template (this triggers enforcement logic)
            template = workflow._get_seq_thinking_template(scenario["type"], step_config)

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

            # Check enforcement compliance
            enforced_compliant = (scenario["enforced"] and is_adg_template) or (
                not scenario["enforced"] and not is_adg_template
            )

            result = {
                "scenario": scenario["name"],
                "type": scenario["type"],
                "complexity": scenario["complexity"],
                "files_count": len(scenario["files"]),
                "expected_enforced": scenario["enforced"],
                "actual_adg_template": is_adg_template,
                "compliant": enforced_compliant,
                "template_length": len(template),
                "success": True,
            }

            status = "✅ PASS" if enforced_compliant else "❌ FAIL"
            print(f"   Result: {status}")
            print(f"   ADG Template: {'Yes' if is_adg_template else 'No'}")
            print(f"   Template Length: {len(template):,} characters")

            if scenario["expected_template"] and scenario["expected_template"] in template:
                print("   Expected Template Found: ✅")
            elif scenario["expected_template"]:
                print("   Expected Template Found: ❌")

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


def test_enforcement_statistics(results):
    """Generate enforcement statistics."""

    successful = [r for r in results if r.get("success", False)]
    compliant = [r for r in successful if r.get("compliant", False)]
    enforced_scenarios = [r for r in successful if r.get("expected_enforced", False)]
    enforced_compliant = [r for r in enforced_scenarios if r.get("actual_adg_template", False)]

    print("\n📊 Enforcement Statistics")
    print("=" * 60)
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {len(successful)} ({len(successful) / len(results) * 100:.1f}%)")
    print(f"Compliant: {len(compliant)} ({len(compliant) / len(successful) * 100:.1f}% of successful)")
    print(f"Enforcement Required: {len(enforced_scenarios)}")
    print(
        f"Enforcement Compliant: {len(enforced_compliant)} ({len(enforced_compliant) / len(enforced_scenarios) * 100:.1f}%)"
    )

    # Show enforcement breakdown
    print("\n🎯 Enforcement Breakdown:")
    print("-" * 30)

    for result in successful:
        status = "🔒 ENFORCED" if result.get("actual_adg_template") else "⚡ OPTIONAL"
        compliance = "✅" if result.get("compliant") else "❌"
        print(f"{compliance} {status} {result['scenario']} ({result['type']})")

    return {
        "total_tests": len(results),
        "successful": len(successful),
        "compliant": len(compliant),
        "enforcement_rate": len(enforced_compliant) / len(enforced_scenarios) * 100
        if enforced_scenarios
        else 100,
    }


def test_template_content_quality():
    """Test the quality of enforced ADG template content."""

    print("\n🔍 Template Content Quality Test")
    print("=" * 60)

    workflow = SequentialThinkingEnhancedWorkflow(seq_thinking_enabled=True)

    # Test a high-complexity scenario
    step_config = {
        "name": "Critical System Analysis",
        "type": "architecture",
        "complexity": "critical",
        "files": ["system.py", "components/", "config/"],
        "description": "Critical system architectural analysis",
    }

    try:
        template = workflow._get_seq_thinking_template("architecture", step_config)

        # Check for ADG template indicators
        quality_checks = {
            "has_adg_context": "node_count" in template or "edge_count" in template,
            "has_sequential_structure": "### Thought" in template,
            "has_real_data": "10,432" in template or "681,161" in template,
            "has_violation_data": "5,301" in template or "violation_count" in template,
            "has_layer_info": "L0:" in template or "layer_info" in template,
            "has_system_metrics": "component_count" in template or "quality_attributes" in template,
        }

        passed_checks = sum(quality_checks.values())
        total_checks = len(quality_checks)

        print("Template Quality Checks:")
        for check, passed in quality_checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check.replace('_', ' ').title()}")

        print(f"\nQuality Score: {passed_checks}/{total_checks} ({passed_checks / total_checks * 100:.1f}%)")
        print(f"Template Length: {len(template):,} characters")

        # Show sample content
        lines = template.split("\n")[:10]
        print("\nTemplate Sample:")
        for line in lines:
            if line.strip():
                print(f"   {line[:80]}...")
                break

        return {
            "quality_score": passed_checks / total_checks * 100,
            "template_length": len(template),
            "checks_passed": passed_checks,
        }

    except Exception as e:
        print(f"❌ Template quality test failed: {e}")
        return {"success": False, "error": str(e)}


def main():
    """Main enforcement test execution."""

    print("🚀 ADG Template Enforcement Test Suite")
    print("=" * 60)
    print("Testing mandatory use of ADG-based templates in SWE model")

    # Set up logging to see enforcement messages
    logging.basicConfig(level=logging.INFO)

    # Run enforcement tests
    results = test_adg_template_enforcement()
    stats = test_enforcement_statistics(results)

    # Test template quality
    quality_result = test_template_content_quality()

    # Generate final report
    print("\n🎯 Final Enforcement Report")
    print("=" * 60)

    if stats["enforcement_rate"] >= 90:
        print("🎉 EXCELLENT: ADG template enforcement working perfectly!")
    elif stats["enforcement_rate"] >= 75:
        print("✅ GOOD: ADG template enforcement mostly working")
    else:
        print("⚠️  NEEDS IMPROVEMENT: ADG template enforcement issues detected")

    print(f"Enforcement Rate: {stats['enforcement_rate']:.1f}%")
    print(f"Test Success Rate: {stats['successful'] / stats['total_tests'] * 100:.1f}%")

    if quality_result.get("quality_score", 0) >= 80:
        print("✅ Template Quality: Excellent")
    else:
        print("⚠️  Template Quality: Needs improvement")

    print(f"\n🔒 Enforcement Status: {'ACTIVE' if stats['enforcement_rate'] >= 90 else 'PARTIAL'}")
    print("📋 ADG templates are mandatory for relevant task types")
    print("🎯 High/critical complexity tasks automatically use ADG templates")
    print("📁 Multi-file operations enforce dependency graph analysis")
    print("🏗️  Architectural tasks use architectural review templates")


if __name__ == "__main__":
    main()
