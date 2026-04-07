#!/usr/bin/env python3
"""
Debug Template Rendering
Fix ADG context injection issues
"""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent
sys.path.append(str(repo_root))

from apps_shared.prompts.sequential_thinking_templates import (
    SequentialThinkingTemplate,
    get_template,
    render_template,
)


def debug_template_rendering():
    """Debug why ADG context isn't being injected properly."""

    print("🔍 Debug Template Rendering")
    print("=" * 50)

    # Test ADG template
    template_type = SequentialThinkingTemplate.SWE_ADG_ANALYSIS
    template = get_template(template_type)

    print(f"Template: {template.name}")
    print(f"Variables: {template.variables}")
    print(f"Content length: {len(template.content)}")
    print()

    # Test variables
    test_vars = {
        'analysis_title': 'Test ADG Analysis',
        'context': 'Test context for debugging',
        'node_count': '10,432',
        'edge_count': '681,161',
        'layer_info': 'L0: 7,220 nodes, L1: 4,362 nodes, L2-L6: 2,850 nodes',
        'violation_count': '5,301',
    }

    print("Test Variables:")
    for key, value in test_vars.items():
        print(f"  {key}: {value}")
    print()

    # Check if variables exist in template
    print("Variable Presence Check:")
    for var in template.variables:
        placeholder = f"{{{var}}}"
        present = placeholder in template.content
        print(f"  {var}: {'✅' if present else '❌'} ({placeholder})")
    print()

    # Render template
    try:
        rendered = render_template(template_type, **test_vars)

        print("Rendered Template Sample:")
        print("-" * 30)
        lines = rendered.split('\n')
        for i, line in enumerate(lines[:15]):
            print(f"{i+1:2d}: {line}")

        print("\nVariable Replacement Check:")
        for var in template.variables:
            placeholder = f"{{{var}}}"
            still_present = placeholder in rendered
            print(f"  {var}: {'❌ NOT REPLACED' if still_present else '✅ REPLACED'}")

        # Check for real data
        print("\nReal Data Check:")
        real_data_checks = {
            '10,432': 'Node count',
            '681,161': 'Edge count',
            '5,301': 'Violation count',
            'L0: 7,220': 'Layer info',
        }

        for data, description in real_data_checks.items():
            present = data in rendered
            print(f"  {description}: {'✅' if present else '❌'} ({data})")

        return rendered

    except Exception as e:
        print(f"❌ Rendering failed: {e}")
        return None

def test_all_adg_templates():
    """Test all ADG templates with proper context."""

    print("\n🔧 Testing All ADG Templates")
    print("=" * 50)

    # Full ADG context
    adg_context = {
        'node_count': '10,432',
        'edge_count': '681,161',
        'violation_count': '5,301',
        'layer_info': 'L0: 7,220 nodes, L1: 4,362 nodes, L2-L6: 2,850 nodes',
        'high_severity_count': '1,200',
        'medium_severity_count': '2,800',
        'low_severity_count': '1,301',
        'common_violation_types': 'except:Exception, for_retry, CURRENT_PHASE, except:bare',
        'boundary_violations': '17',
        'gravity_violations': '17',
        'layer_count': '7',
        'layer_distribution': 'L0: 69.2%, L1: 41.8%, L2: 14.4%, L3: 7.7%, L4: 1.9%, L5: 1.4%, L6: 1.9%',
        'dependency_count': '681,161',
        'circular_deps': '0',
        'longest_chain': '15',
        'hub_nodes': '42',
        'component_count': '156',
        'patterns_used': 'Layered Architecture, Dependency Injection, Event-Driven',
        'integration_points': '45',
        'quality_attributes': 'Performance, Scalability, Maintainability, Security',
        'antipattern_count': '5,301',
        'high_impact_count': '1,200',
        'common_categories': 'Exception Handling, Retry Logic, State Management',
        'affected_files': '234',
        'system_size': 'Large-scale enterprise system',
        'complexity_metrics': 'Cyclomatic Complexity: 8.5 avg, Coupling: 12.3 avg',
        'identified_issues': 'Layer violations, Exception handling anti-patterns, Circular dependencies',
        'restructuring_goals': 'Improve layer compliance, Reduce technical debt, Enhance maintainability',
        'current_traversal_time': '2.3s average',
        'graph_size': '681,161 edges',
        'traversal_frequency': '100+ queries/hour',
        'bottlenecks': 'Layer boundary queries, Violation filtering, Graph traversal',
    }

    adg_templates = [
        (SequentialThinkingTemplate.SWE_ADG_ANALYSIS, {
            'analysis_title': 'System ADG Health Analysis',
            'context': 'Comprehensive analysis of system architecture and dependency graph',
            **adg_context,
        }),

        (SequentialThinkingTemplate.SWE_VIOLATION_REMEDIATION, {
            'remediation_title': 'Critical Violation Remediation Strategy',
            'context': 'System has 5,301 violations requiring systematic remediation',
            **adg_context,
        }),

        (SequentialThinkingTemplate.SWE_ARCHITECTURAL_REVIEW, {
            'review_title': 'System Architecture Review',
            'context': 'Comprehensive review of current system architecture and patterns',
            **adg_context,
        }),
    ]

    results = []

    for template_type, vars_dict in adg_templates:
        print(f"\n🧪 Testing: {template_type.value}")
        print("-" * 40)

        try:
            rendered = render_template(template_type, **vars_dict)
            template = get_template(template_type)

            # Check for real data
            has_real_data = any(data in rendered for data in ['10,432', '681,161', '5,301'])
            has_adg_context = any(context in rendered for context in ['node_count', 'edge_count', 'violation_count'])

            results.append({
                'template': template_type.value,
                'name': template.name,
                'success': True,
                'has_real_data': has_real_data,
                'has_adg_context': has_adg_context,
                'length': len(rendered),
            })

            print(f"✅ {template.name}")
            print(f"   Real Data: {'✅' if has_real_data else '❌'}")
            print(f"   ADG Context: {'✅' if has_adg_context else '❌'}")
            print(f"   Length: {len(rendered):,} characters")

            # Show sample
            sample = rendered[:200].replace('\n', ' ')
            print(f"   Sample: {sample}...")

        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append({
                'template': template_type.value,
                'success': False,
                'error': str(e),
            })

    return results

def main():
    """Main debug execution."""

    print("🚀 Template Rendering Debug Suite")
    print("=" * 60)

    # Debug single template
    debug_template_rendering()

    # Test all ADG templates
    results = test_all_adg_templates()

    # Summary
    print("\n📊 Debug Summary")
    print("=" * 60)

    successful = [r for r in results if r.get('success', False)]
    with_real_data = [r for r in successful if r.get('has_real_data', False)]
    with_adg_context = [r for r in successful if r.get('has_adg_context', False)]

    print(f"Total Templates: {len(results)}")
    print(f"Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"With Real Data: {len(with_real_data)} ({len(with_real_data)/len(successful)*100:.1f}%)")
    print(f"With ADG Context: {len(with_adg_context)} ({len(with_adg_context)/len(successful)*100:.1f}%)")

    if len(with_real_data) == len(successful):
        print("\n🎉 Template rendering is working correctly!")
    else:
        print("\n⚠️  Template rendering needs fixes")

if __name__ == "__main__":
    main()
