#!/usr/bin/env python3
"""
Detailed Template Quality Analysis
Identify and fix remaining quality issues to achieve 100%
"""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent
sys.path.append(str(repo_root))

from agentic_core.planning.sequential_thinking_workflow import SequentialThinkingEnhancedWorkflow


def analyze_template_quality():
    """Analyze each template's quality in detail."""

    print("🔍 DETAILED TEMPLATE QUALITY ANALYSIS")
    print("=" * 60)
    print("Identifying issues to achieve 100% quality")

    workflow = SequentialThinkingEnhancedWorkflow(seq_thinking_enabled=True)

    # Test all ADG templates
    adg_templates = [
        {
            'name': 'ADG Graph Analysis',
            'type': 'adg_analysis',
            'config': {'complexity': 'high', 'files': ['adg.sqlite']},
            'expected_data': ['10,432', '681,161', '5,301', 'L0: 7,220'],
            'expected_context': ['node_count', 'edge_count', 'layer_info', 'violation_count']
        },
        {
            'name': 'Violation Remediation',
            'type': 'violation_remediation',
            'config': {'complexity': 'high', 'files': ['violations.json']},
            'expected_data': ['5,301', '1,200', '2,800', '1,301'],
            'expected_context': ['violation_count', 'high_severity_count', 'medium_severity_count', 'low_severity_count']
        },
        {
            'name': 'Architectural Review',
            'type': 'architecture',
            'config': {'complexity': 'high', 'files': ['design.md']},
            'expected_data': ['156', 'Layered Architecture', 'Dependency Injection', 'Event-Driven'],
            'expected_context': ['component_count', 'patterns_used', 'integration_points', 'quality_attributes']
        },
        {
            'name': 'Dependency Graph Analysis',
            'type': 'implementation',
            'config': {'complexity': 'high', 'files': ['f1.py', 'f2.py', 'f3.py', 'f4.py', 'f5.py', 'f6.py']},
            'expected_data': ['681,161', '0', '15', '42'],
            'expected_context': ['dependency_count', 'circular_deps', 'longest_chain', 'hub_nodes']
        },
        {
            'name': 'Layer Boundary Audit',
            'type': 'layer_boundary_audit',
            'config': {'complexity': 'high', 'files': ['layers.py']},
            'expected_data': ['7', '69.2%', '41.8%', '17'],
            'expected_context': ['layer_count', 'layer_distribution', 'boundary_violations', 'gravity_violations']
        },
        {
            'name': 'Anti-pattern Detection',
            'type': 'anti_pattern_detection',
            'config': {'complexity': 'medium', 'files': ['patterns.py']},
            'expected_data': ['5,301', '1,200', 'Exception Handling', '234'],
            'expected_context': ['antipattern_count', 'high_impact_count', 'common_categories', 'affected_files']
        },
        {
            'name': 'System Restructuring',
            'type': 'system_restructuring',
            'config': {'complexity': 'critical', 'files': ['legacy.py']},
            'expected_data': ['Large-scale enterprise', 'Cyclomatic Complexity', 'Layer violations', 'technical debt'],
            'expected_context': ['system_size', 'complexity_metrics', 'identified_issues', 'restructuring_goals']
        },
        {
            'name': 'Graph Traversal Optimization',
            'type': 'graph_traversal_optimization',
            'config': {'complexity': 'high', 'files': ['graph.py']},
            'expected_data': ['2.3s', '681,161 edges', '100+ queries', 'Layer boundary'],
            'expected_context': ['current_traversal_time', 'graph_size', 'traversal_frequency', 'bottlenecks']
        }
    ]

    results = []

    for template_test in adg_templates:
        print(f"\n🧪 Analyzing: {template_test['name']}")
        print("-" * 50)

        try:
            # Get template
            step_config = {
                'name': template_test['name'],
                'type': template_test['type'],
                **template_test['config']
            }

            template_content = workflow._get_seq_thinking_template(template_test['type'], step_config)

            # Detailed quality analysis
            analysis = {
                'has_sequential_structure': '### Thought 1:' in template_content,
                'missing_thoughts': [],
                'data_found': [],
                'data_missing': [],
                'context_found': [],
                'context_missing': [],
                'quality_issues': []
            }

            # Check all 6 thoughts
            for i in range(1, 7):
                thought = f"### Thought {i}:"
                if thought in template_content:
                    analysis['has_sequential_structure'] = True
                else:
                    analysis['missing_thoughts'].append(i)
                    analysis['quality_issues'].append(f"Missing Thought {i}")

            # Check expected data
            for data in template_test['expected_data']:
                if data in template_content:
                    analysis['data_found'].append(data)
                else:
                    analysis['data_missing'].append(data)
                    analysis['quality_issues'].append(f"Missing data: {data}")

            # Check expected context variables - look for VALUES not variable names
            for context in template_test['expected_context']:
                # Map context variable names to expected values
                context_to_value_map = {
                    'node_count': '10,432',
                    'edge_count': '681,161',
                    'violation_count': '5,301',
                    'layer_info': 'L0: 7,220',
                    'high_severity_count': '1,200',
                    'medium_severity_count': '2,800',
                    'low_severity_count': '1,301',
                    'common_violation_types': 'except:Exception',
                    'boundary_violations': '17',
                    'gravity_violations': '17',
                    'layer_count': '7',
                    'layer_distribution': '69.2%',
                    'dependency_count': '681,161',
                    'circular_deps': '0',
                    'longest_chain': '15',
                    'hub_nodes': '42',
                    'component_count': '156',
                    'patterns_used': 'Layered Architecture',
                    'integration_points': '45',
                    'quality_attributes': 'Performance',
                    'antipattern_count': '5,301',
                    'high_impact_count': '1,200',
                    'common_categories': 'Exception Handling',
                    'affected_files': '234',
                    'system_size': 'Large-scale enterprise',
                    'complexity_metrics': 'Cyclomatic Complexity',
                    'identified_issues': 'Layer violations',
                    'restructuring_goals': 'technical debt',
                    'current_traversal_time': '2.3s',
                    'graph_size': '681,161 edges',
                    'traversal_frequency': '100+',
                    'bottlenecks': 'Layer boundary'
                }

                expected_value = context_to_value_map.get(context, context)
                if expected_value in template_content:
                    analysis['context_found'].append(context)
                else:
                    analysis['context_missing'].append(context)
                    analysis['quality_issues'].append(f"Missing context value for: {context} (expected: {expected_value})")

            # Calculate quality score
            total_checks = 6 + len(template_test['expected_data']) + len(template_test['expected_context'])
            passed_checks = (6 - len(analysis['missing_thoughts']) +
                           len(analysis['data_found']) +
                           len(analysis['context_found']))

            quality_score = (passed_checks / total_checks) * 100

            result = {
                'template': template_test['name'],
                'type': template_test['type'],
                'quality_score': quality_score,
                'analysis': analysis,
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'issues': analysis['quality_issues'],
                'success': True
            }

            results.append(result)

            # Display results
            status = "🎉 PERFECT" if quality_score == 100 else "✅ GOOD" if quality_score >= 80 else "⚠️  NEEDS WORK"
            print(f"   Status: {status}")
            print(f"   Quality Score: {quality_score:.1f}%")
            print(f"   Checks Passed: {passed_checks}/{total_checks}")

            if analysis['quality_issues']:
                print(f"   Issues ({len(analysis['quality_issues'])}):")
                for issue in analysis['quality_issues'][:5]:  # Show first 5
                    print(f"     - {issue}")
                if len(analysis['quality_issues']) > 5:
                    print(f"     ... and {len(analysis['quality_issues']) - 5} more")
            else:
                print("   ✅ No issues found")

        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append({
                'template': template_test['name'],
                'success': False,
                'error': str(e)
            })

    # Summary
    print("\n📊 QUALITY ANALYSIS SUMMARY")
    print("=" * 60)

    successful = [r for r in results if r.get('success', False)]
    if successful:
        avg_quality = sum(r['quality_score'] for r in successful) / len(successful)
        perfect_templates = [r for r in successful if r['quality_score'] == 100]
        good_templates = [r for r in successful if r['quality_score'] >= 80]

        print(f"Templates Analyzed: {len(successful)}")
        print(f"Average Quality: {avg_quality:.1f}%")
        print(f"Perfect (100%): {len(perfect_templates)}")
        print(f"Good (80%+): {len(good_templates)}")

        # Identify templates needing fixes
        need_fixes = [r for r in successful if r['quality_score'] < 100]
        if need_fixes:
            print("\n🔧 TEMPLATES NEEDING FIXES:")
            for template in need_fixes:
                print(f"   ❌ {template['template']}: {template['quality_score']:.1f}%")
                print(f"      Issues: {len(template['issues'])}")
                for issue in template['issues'][:3]:
                    print(f"        - {issue}")
        else:
            print("\n🎉 ALL TEMPLATES ARE PERFECT!")

    return results

def main():
    """Main quality analysis."""

    print("🎯 TEMPLATE QUALITY OPTIMIZATION")
    print("=" * 80)
    print("Analyzing and fixing template quality to achieve 100%")

    results = analyze_template_quality()

    # Determine if fixes are needed
    successful = [r for r in results if r.get('success', False)]
    need_fixes = [r for r in successful if r['quality_score'] < 100]

    if need_fixes:
        print("\n🔧 QUALITY FIXES REQUIRED")
        print("=" * 60)
        print(f"Templates needing fixes: {len(need_fixes)}")

        # Common issues to fix
        all_issues = []
        for template in need_fixes:
            all_issues.extend(template['issues'])

        # Count issue types
        issue_counts = {}
        for issue in all_issues:
            if 'Missing Thought' in issue:
                issue_counts['missing_thoughts'] = issue_counts.get('missing_thoughts', 0) + 1
            elif 'Missing data:' in issue:
                issue_counts['missing_data'] = issue_counts.get('missing_data', 0) + 1
            elif 'Missing context:' in issue:
                issue_counts['missing_context'] = issue_counts.get('missing_context', 0) + 1

        print("\nIssue Summary:")
        for issue_type, count in issue_counts.items():
            print(f"   {issue_type}: {count} occurrences")

        print("\n💡 RECOMMENDED FIXES:")
        if issue_counts.get('missing_thoughts', 0) > 0:
            print("   1. Fix missing sequential thought structure")
        if issue_counts.get('missing_data', 0) > 0:
            print("   2. Ensure all expected data is in templates")
        if issue_counts.get('missing_context', 0) > 0:
            print("   3. Fix context variable injection")

        return False
    else:
        print("\n🎉 QUALITY STATUS: PERFECT - 100% ACHIEVED!")
        print("=" * 60)
        print("✅ All templates have perfect quality")
        print("✅ All sequential thoughts present")
        print("✅ All expected data integrated")
        print("✅ All context variables injected")
        print("🚀 Ready for commit and GitHub sync")
        return True

if __name__ == "__main__":
    main()
