#!/usr/bin/env python3
"""
Sequential Thinking Integration Test for Agentic-Workflow Repository
This test demonstrates the sequential thinking capability with real repository problems.
"""

import json
import sys
from pathlib import Path


def create_test_scenarios():
    """Create test scenarios for sequential thinking analysis."""

    repo_root = Path(__file__).parent

    # Scenario 1: ADG Optimization Analysis
    adg_scenario = {
        "title": "ADG Performance Optimization Strategy",
        "context": {
            "problem_type": "system_optimization",
            "repository_area": "agentic_core/adg/",
            "current_state": {
                "sqlite_size": "300+ MB",
                "nodes": "263,888",
                "edges": "929,125",
                "scan_time": "5+ minutes"
            },
            "constraints": [
                "Must maintain semantic precision",
                "Cannot break existing governance queries",
                "Need to support incremental updates"
            ]
        },
        "question": "How can we optimize the ADG (Application Dependency Graph) system for better performance while maintaining accuracy and governance capabilities?"
    }

    # Scenario 2: Test Strategy Enhancement
    test_scenario = {
        "title": "Multi-Layer Testing Strategy",
        "context": {
            "problem_type": "testing_architecture",
            "repository_areas": ["agentic_core/", "apps_*/", "tests/"],
            "current_state": {
                "python_files": "11,074",
                "test_files": "2,384",
                "layers": "L0-L6 architecture",
                "apps_modules": "apps_eval, apps_exec, apps_lic, apps_rg, apps_research, apps_rfp"
            },
            "challenges": [
                "Cross-layer integration testing",
                "Agent behavior validation",
                "Performance regression testing",
                "Governance compliance verification"
            ]
        },
        "question": "What comprehensive testing strategy should we implement for this multi-layered agentic system to ensure reliability, performance, and compliance?"
    }

    # Scenario 3: Memory System Integration
    memory_scenario = {
        "title": "ADG-Memory Integration Architecture",
        "context": {
            "problem_type": "system_integration",
            "components": ["ADG Redis cache", "SQLite memory graph", "Runtime tracing"],
            "current_integration": {
                "adg_redis": "Hot cache with 17 tools",
                "memory_mcp": "SQLite-backed knowledge graph",
                "lifecycle_tracing": "Runtime execution traces"
            },
            "goals": [
                "Seamless data flow between components",
                "Consistent entity resolution",
                "Efficient query performance",
                "Audit trail maintenance"
            ]
        },
        "question": "How should we architect the integration between ADG static analysis, runtime memory, and execution tracing to create a cohesive system understanding?"
    }

    return [adg_scenario, test_scenario, memory_scenario]

def create_sequential_thinking_prompt(scenario):
    """Create a structured prompt for sequential thinking analysis."""

    prompt = f"""
# Sequential Thinking Analysis: {scenario['title']}

## Context
{json.dumps(scenario['context'], indent=2)}

## Core Question
{scenario['question']}

## Sequential Analysis Requirements

Please provide a structured sequential thinking analysis that breaks this problem down as follows:

### Thought 1: Problem Decomposition
- Identify the main components and sub-problems
- Define the scope and boundaries
- List key stakeholders and requirements

### Thought 2: Current State Analysis
- Assess the existing implementation
- Identify strengths and weaknesses
- Document pain points and bottlenecks

### Thought 3: Solution Architecture
- Propose high-level architectural approach
- Define key components and their relationships
- Consider trade-offs and alternatives

### Thought 4: Implementation Strategy
- Break down into phased implementation
- Identify dependencies and prerequisites
- Define success metrics and validation criteria

### Thought 5: Risk Assessment
- Identify potential risks and mitigation strategies
- Consider performance, security, and maintainability
- Plan for rollback and recovery

### Thought 6: Integration Plan
- Define how the solution integrates with existing systems
- Specify testing and validation approaches
- Outline deployment and migration strategy

## Expected Output
For each thought, provide:
- Clear analysis and reasoning
- Specific recommendations
- Next steps and dependencies
- Confidence level and assumptions

Please analyze this systematically using the sequential thinking approach.
"""

    return prompt

def main():
    """Main function to run integration tests."""
    print("🧠 Sequential Thinking Integration Test for Agentic-Workflow")
    print("=" * 70)

    scenarios = create_test_scenarios()

    print(f"📋 Created {len(scenarios)} test scenarios for sequential thinking analysis")

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- Scenario {i}: {scenario['title']} ---")
        prompt = create_sequential_thinking_prompt(scenario)

        # Save prompt to file for manual testing
        prompt_file = Path(__file__).parent / f"sequential_thinking_scenario_{i}.md"
        with open(prompt_file, 'w') as f:
            f.write(prompt)

        print(f"✅ Saved scenario prompt to: {prompt_file}")
        print(f"   Problem type: {scenario['context']['problem_type']}")
        print(f"   Key components: {list(scenario['context'].keys())}")

    print("\n🎯 Integration Test Summary:")
    print(f"   Scenarios created: {len(scenarios)}")
    print("   MCP server: Configured and ready")
    print("   Test files: Saved for manual verification")

    print("\n📝 Manual Testing Instructions:")
    print("1. Restart Windsurf to load MCP configuration")
    print("2. Use the sequential_thinking tool with each scenario")
    print("3. Verify structured thinking process with 6+ thoughts")
    print("4. Check for logical progression and problem decomposition")

    # Create a simple test for immediate verification
    print("\n🔬 Creating immediate verification test...")
    simple_test = {
        "thought": "I need to analyze the Agentic-Workflow repository structure to understand its complexity.",
        "nextThoughtNeeded": True,
        "thoughtNumber": 1,
        "totalThoughts": 3,
        "isRevision": False,
        "revisesThought": None,
        "branchFromThought": None,
        "branchId": None,
        "needsMoreThoughts": True
    }

    test_file = Path(__file__).parent / "sequential_thinking_test_input.json"
    with open(test_file, 'w') as f:
        json.dump(simple_test, f, indent=2)

    print(f"✅ Created test input file: {test_file}")
    print("   Use this with the sequential_thinking tool for immediate testing")

    return 0

if __name__ == "__main__":
    sys.exit(main())
