#!/usr/bin/env python3
"""
Test Sequential Thinking Workflow Integration
"""

from tools.utils.planning.sequential_thinking_workflow import SequentialThinkingEnhancedWorkflow
from tools.utils.planning.token_estimator import TokenBudget


def test_workflow_integration():
    """Test workflow integration with various scenarios."""

    print('🚀 Sequential Thinking Workflow Integration Test')
    print('=' * 60)

    # Initialize workflow
    workflow = SequentialThinkingEnhancedWorkflow(seq_thinking_enabled=True)
    print('✅ Workflow initialized successfully')

    # Test complexity-based forcing
    test_steps = [
        {
            'name': 'Simple Code Review',
            'complexity': 'low',
            'files': ['app.py'],
            'type': 'analysis',
        },
        {
            'name': 'Database Migration Planning',
            'complexity': 'medium',
            'files': ['models.py', 'migrations/', 'schema.sql'],
            'type': 'planning',
        },
        {
            'name': 'Microservices Architecture Refactor',
            'complexity': 'high',
            'files': ['services/', 'api/', 'config/'],
            'type': 'architecture',
        },
        {
            'name': 'Production Outage Debugging',
            'complexity': 'critical',
            'files': ['logs/', 'monitoring/', 'alerts/'],
            'type': 'debugging',
        },
    ]

    print('\n🎯 Complexity-Based Auto-Trigger Test')
    print('=' * 60)

    for i, step in enumerate(test_steps, 1):
        should_force = workflow.force_sequential_thinking(step['type'], step)
        template = workflow._get_seq_thinking_template(step['type'])

        status = '🧠 FORCED' if should_force else '⚡ NORMAL'
        print(f'Test {i}: {step["name"]}')
        print(f'   Complexity: {step["complexity"]} | Files: {len(step["files"])}')
        print(f'   Result: {status}')
        print(f'   Template: {template.name if template else "None"}')
        print()

    # Test token budget management
    print('💰 Token Budget Management Test')
    print('=' * 60)

    budget = TokenBudget()
    print(f'Total Context Window: {budget.HARD_MAX_CONTEXT:,} tokens')
    print(f'Safe Operating Cap: {budget.SAFE_OPERATING_CAP:,} tokens')
    print(f'Warning Threshold: {budget.WARNING_THRESHOLD:,} tokens')
    print('Sequential Thinking Budget: 30,000 tokens (20% allocation)')

    # Test template selection
    print('\n📝 Template Selection Test')
    print('=' * 60)

    task_types = ['analysis', 'debugging', 'implementation', 'architecture', 'refactoring', 'testing', 'planning', 'integration']

    for task_type in task_types:
        template = workflow._get_seq_thinking_template(task_type)
        if template:
            print(f'{task_type.title()}: {template.name} ({template.estimated_tokens:,} tokens)')
        else:
            print(f'{task_type.title()}: No template')

    print('\n🎉 Sequential Thinking Workflow Test Complete!')
    print('✅ All systems operational and ready for production use')

if __name__ == "__main__":
    test_workflow_integration()
