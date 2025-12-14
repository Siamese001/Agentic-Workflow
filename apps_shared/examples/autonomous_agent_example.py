"""
Autonomous Agent System - Complete Usage Example

Demonstrates how to use the enhanced autonomy features:
1. Episodic Memory - Learning from past experiences
2. Reasoning Kernel - System 2 thinking
3. Dynamic Tool Discovery - Runtime tool finding
4. Recursive Planning - Hierarchical task execution
"""

import asyncio
import logging
from datetime import datetime

# Import autonomous components
from runtime.core.autonomous_subatomic_hop import (
    AutonomousSubatomicHop,
    AutonomousHopConfig,
    AutonomyConfig,
    create_autonomous_hop
)

# Import hardening components
from runtime.shared.semantic_cache import SemanticCache
from agentic_core.L2_execution.mcp_manager import create_mcp_manager
from runtime.core.telemetry import TelemetryRecorder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Example task functions
async def research_task(goal: str, context: dict) -> dict:
    """Example research task that demonstrates autonomy."""
    # This would normally use tools and reasoning
    return {
        "research_findings": f"Research completed for: {goal}",
        "sources": ["source1", "source2"],
        "confidence": 0.85
    }


async def coding_task(goal: str, context: dict) -> dict:
    """Example coding task that uses dynamic tools."""
    # This would normally discover and use coding tools
    return {
        "code": f"def implement_{hash(goal)}():\n    pass",
        "tests": ["test_case_1"],
        "success": True
    }


async def complex_analysis_task(goal: str, context: dict) -> dict:
    """Example complex task that requires recursive planning."""
    # This would normally break down into sub-tasks
    return {
        "analysis": "Complex analysis completed",
        "subtasks_completed": 3,
        "insights": ["insight1", "insight2", "insight3"]
    }


async def demonstrate_episodic_memory():
    """Demonstrate episodic memory capabilities."""
    print("\n=== Episodic Memory Demo ===")
    
    # Create config with memory enabled
    autonomy_config = AutonomyConfig(
        enable_episodic_memory=True,
        memory_similarity_threshold=0.8,
        memory_min_rating=0.6
    )
    
    config = AutonomousHopConfig(
        autonomy=autonomy_config,
        storage_path="./demo_memory_store"
    )
    
    # Create autonomous hop
    hop = create_autonomous_hop(
        hop_function=research_task,
        config=config,
        initial_context={"agent_role": "RESEARCHER"}
    )
    
    # First execution - will be committed to memory
    print("\nFirst execution (learning phase):")
    result1 = await hop.run(
        goal="Analyze market trends for AI technology",
        context={"year": 2024}
    )
    print(f"Result: {result1}")
    
    # Commit to memory
    await hop.commit_execution_to_memory(
        task="Analyze market trends for AI technology",
        plan="Research AI market trends using available tools",
        result=result1,
        success=True,
        tools_used=["search_tool", "analysis_tool"]
    )
    
    # Second execution - will recall from memory
    print("\nSecond execution (with memory recall):")
    result2 = await hop.run(
        goal="Research AI market trends and analysis",
        context={"year": 2024}
    )
    print(f"Result: {result2}")
    
    if hop.memory_context:
        print(f"\nMemory recalled: {hop.memory_context[:200]}...")


async def demonstrate_reasoning_kernel():
    """Demonstrate System 2 thinking capabilities."""
    print("\n=== Reasoning Kernel Demo ===")
    
    # Create config with reasoning enabled
    autonomy_config = AutonomyConfig(
        enable_reasoning_kernel=True,
        reasoning_max_candidates=3,
        reasoning_critique_threshold=0.7,
        enable_tree_of_thoughts=True
    )
    
    config = AutonomousHopConfig(autonomy=autonomy_config)
    
    # Create autonomous hop
    hop = create_autonomous_hop(
        hop_function=coding_task,
        config=config,
        initial_context={"agent_role": "CODER"}
    )
    
    # Execute with reasoning
    print("\nExecuting with System 2 thinking:")
    result = await hop.run(
        goal="Create a Python function to analyze data and generate visualizations",
        constraints=["Must handle large datasets", "Should be memory efficient"],
        context={"requirements": ["pandas", "matplotlib"]}
    )
    
    print(f"Result: {result}")
    
    if hop.reasoning_trace:
        print(f"\nReasoning confidence: {hop.reasoning_trace.confidence:.2f}")
        print(f"Candidates considered: {len(hop.reasoning_trace.candidates)}")
        print(f"Reasoning time: {hop.reasoning_trace.reasoning_time_ms:.0f}ms")


async def demonstrate_dynamic_tools():
    """Demonstrate dynamic tool discovery."""
    print("\n=== Dynamic Tool Discovery Demo ===")
    
    # Create config with tool discovery enabled
    autonomy_config = AutonomyConfig(
        enable_dynamic_tools=True,
        tool_max_matches=3,
        tool_min_relevance=0.6
    )
    
    config = AutonomousHopConfig(autonomy=autonomy_config)
    
    # Create autonomous hop
    hop = create_autonomous_hop(
        hop_function=coding_task,
        config=config,
        initial_context={"agent_role": "CODER"}
    )
    
    # Execute with tool discovery
    print("\nExecuting with dynamic tool discovery:")
    result = await hop.run(
        goal="Process CSV file and calculate statistics",
        plan="Use file reading tools and calculation utilities"
    )
    
    print(f"Result: {result}")
    
    if hop.selected_tools:
        print(f"\nTools discovered and used:")
        for tool in hop.selected_tools:
            print(f"  - {tool['name']} (relevance: {tool['relevance']:.2f})")


async def demonstrate_recursive_planning():
    """Demonstrate recursive planning for complex tasks."""
    print("\n=== Recursive Planning Demo ===")
    
    # Create config with recursive planning enabled
    autonomy_config = AutonomyConfig(
        enable_recursive_planning=True,
        planner_max_depth=3,
        planner_max_parallel=5
    )
    
    config = AutonomousHopConfig(autonomy=autonomy_config)
    
    # Create autonomous hop
    hop = create_autonomous_hop(
        hop_function=complex_analysis_task,
        config=config,
        initial_context={"agent_role": "RESEARCHER"}
    )
    
    # Execute complex task
    print("\nExecuting complex task with recursive planning:")
    result = await hop.run(
        goal="Design and implement a complete data analysis pipeline for financial data",
        context={
            "data_sources": ["market_data", "company_reports"],
            "requirements": ["real-time processing", "anomaly detection"]
        }
    )
    
    print(f"Result: {result}")


async def demonstrate_full_autonomy():
    """Demonstrate all autonomy features working together."""
    print("\n=== Full Autonomy Integration Demo ===")
    
    # Create config with all features enabled
    autonomy_config = AutonomyConfig(
        enable_episodic_memory=True,
        enable_reasoning_kernel=True,
        enable_dynamic_tools=True,
        enable_recursive_planning=True,
        memory_similarity_threshold=0.85,
        reasoning_critique_threshold=0.7
    )
    
    config = AutonomousHopConfig(
        autonomy=autonomy_config,
        storage_path="./full_autonomy_store"
    )
    
    # Create autonomous hop with all features
    hop = create_autonomous_hop(
        hop_function=complex_analysis_task,
        config=config,
        initial_context={"agent_role": "DATA_ANALYST"}
    )
    
    # Execute complex task
    print("\nExecuting with full autonomy enabled:")
    result = await hop.run(
        goal="Build a machine learning model to predict customer churn",
        constraints=["Must be interpretable", "Should handle imbalanced data"],
        context={
            "data": "customer_churn_dataset.csv",
            "deadline": "2 weeks",
            "team_size": 3
        }
    )
    
    print(f"\nFinal Result: {result}")
    
    # Show autonomy insights
    print("\n=== Autonomy Insights ===")
    
    if hop.memory_context:
        print("✓ Episodic memory: Retrieved relevant past experience")
    
    if hop.reasoning_trace:
        print(f"✓ Reasoning kernel: Deliberated with {hop.reasoning_trace.confidence:.2f} confidence")
    
    if hop.selected_tools:
        print(f"✓ Dynamic tools: Discovered {len(hop.selected_tools)} relevant tools")
    
    # Commit the full execution to memory
    await hop.commit_execution_to_memory(
        task="Build a machine learning model to predict customer churn",
        plan="Recursive plan with data preprocessing, model training, and evaluation",
        result=result,
        success=True,
        tools_used=[t["name"] for t in hop.selected_tools]
    )
    
    print("✓ Execution committed to episodic memory for future learning")


async def main():
    """Run all autonomy demonstrations."""
    print("🤖 Autonomous Agent System Demo")
    print("=" * 50)
    
    try:
        # Run individual demos
        await demonstrate_episodic_memory()
        await demonstrate_reasoning_kernel()
        await demonstrate_dynamic_tools()
        await demonstrate_recursive_planning()
        
        # Run full integration demo
        await demonstrate_full_autonomy()
        
        print("\n" + "=" * 50)
        print("✅ All autonomy demonstrations completed successfully!")
        
    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        raise


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())
