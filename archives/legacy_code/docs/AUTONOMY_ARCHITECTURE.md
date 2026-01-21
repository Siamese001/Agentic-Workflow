# Agent Autonomy Architecture

## Overview

This document describes the autonomy upgrade that transforms agents from **Level 2 (Reliable Executors)** to **Level 4 (Adaptive Learners)** by implementing four key components:

1. **Episodic Memory** - Agents learn from past experiences
2. **Reasoning Kernel** - System 2 thinking with deliberation
3. **Dynamic Tool Registry** - Runtime tool discovery
4. **Recursive Planner** - Hierarchical task execution

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS AGENT                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Episodic Memory │  │ Reasoning Kernel│  │Tool Registry │ │
│  │                 │  │                 │  │              │ │
│  │ • Recall        │  │ • Generate      │  │ • Discover   │ │
│  │ • Commit        │  │ • Critique      │  │ • Register   │ │
│  │ • Learn         │  │ • Refine        │  │ • Match      │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │            Recursive Planner (Executive)                │ │
│  │                                                         │ │
│  │  • Decompose complex goals                              │ │
│  │  • Design sub-workflows                                 │ │
│  │  • Spawn child orchestrators                            │ │
│  │  • Coordinate execution                                 │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           AutonomousSubatomicHop                         │ │
│  │                                                         │ │
│  │  THINK → Memory + Reasoning                             │ │
│  │  ACT   → Dynamic Tools + Recursive Planning             │ │
│  │  CRITIQUE → Failure Pattern Analysis                    │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Episodic Memory (`agentic_core/L1_cognition/episodic_memory.py`)

**Purpose**: Enables agents to recall past successes/failures to avoid repeating errors.

**Key Features**:

- Vector-based similarity search for experience retrieval
- Persistent storage using BlobStorageAdapter
- Automatic filtering by success rating and agent role
- Failure pattern analysis for learning from mistakes

**Usage**:

```python
# Recall relevant experience
memory_context = await episodic_memory.recall_relevant_experience(
    current_task="Analyze market data",
    agent_role="RESEARCHER",
    min_rating=0.7
)

# Commit new experience
episode_id = await episodic_memory.commit_episode(
    task="Analyze market data",
    plan="Used pandas and matplotlib",
    result="Generated 5 key insights",
    rating=0.9,
    agent_role="RESEARCHER"
)
```

### 2. Reasoning Kernel (`runtime/core/reasoning_kernel.py`)

**Purpose**: Implements System 2 thinking, allowing agents to deliberate before acting.

**Key Features**:

- Generates multiple candidate approaches
- Self-critique and refinement loop
- Tree of Thoughts (ToT) reasoning
- Confidence scoring and selection

**Usage**:

```python
# Deliberate on a complex task
plan, trace = await reasoning_kernel.deliberate(
    context={"requirements": ["fast", "scalable"]},
    goal="Design a data processing pipeline",
    constraints=["Must handle 1M records/sec"]
)

print(f"Selected plan confidence: {trace.confidence}")
```

### 3. Dynamic Tool Registry (`agentic_core/L2_execution/tool_registry.py`)

**Purpose**: Allows agents to discover tools at runtime instead of being hardcoded.

**Key Features**:

- Semantic similarity matching for tool discovery
- Automatic tool registration and categorization
- Usage statistics and success tracking
- MCP tool integration

**Usage**:

```python
# Find tools for a task
matches = await tool_registry.find_tools_for_task(
    task_description="Process CSV and calculate statistics",
    max_tools=3,
    min_relevance=0.7
)

# Register a new tool
tool_registry.register(
    name="analyze_data",
    func=analyze_function,
    description="Statistical analysis of datasets",
    category="analysis"
)
```

### 4. Recursive Planner (`apps_rg/L3_orchestration/recursive_agent.py`)

**Purpose**: Enables hierarchical execution by spawning sub-orchestrators for complex goals.

**Key Features**:

- Automatic goal decomposition
- Dependency-aware task scheduling
- Parallel/adaptive execution strategies
- Depth-limited recursion

**Usage**:

```python
# Plan and execute complex goal
result = await recursive_planner.plan_and_execute(
    complex_goal="Build ML pipeline for fraud detection",
    context={"data_source": "transactions.db"},
    current_depth=0
)
```

## Integration with SubatomicHop

The `AutonomousSubatomicHop` class integrates all autonomy components:

```python
# Configuration
autonomy_config = AutonomyConfig(
    enable_episodic_memory=True,
    enable_reasoning_kernel=True,
    enable_dynamic_tools=True,
    enable_recursive_planning=True
)

config = AutonomousHopConfig(autonomy=autonomy_config)

# Create autonomous hop
hop = create_autonomous_hop(
    hop_function=my_task_function,
    config=config,
    initial_context={"agent_role": "DATA_ANALYST"}
)

# Execute with full autonomy
result = await hop.run(
    goal="Complex task requiring all autonomy features",
    constraints=["Must be efficient", "Should be scalable"]
)
```

## Execution Flow

### THINK Stage (Enhanced)

1. **Memory Recall**: Query episodic memory for relevant past experiences
2. **Reasoning**: Use Reasoning Kernel to generate and critique multiple approaches
3. **Plan Selection**: Select best plan based on confidence score

### ACT Stage (Enhanced)

1. **Tool Discovery**: Find relevant tools using semantic search
2. **Recursive Planning**: For complex tasks, spawn sub-orchestrators
3. **Execution**: Execute with dynamically discovered tools

### CRITIQUE Stage (Enhanced)

1. **Standard Critique**: Apply existing quality criteria
2. **Pattern Analysis**: Check episodic memory for failure patterns
3. **Learning**: Commit execution results to memory

## Benefits

### 1. Improved Performance

- **Reduced Redundancy**: Agents avoid repeating failed approaches
- **Better Planning**: System 2 thinking leads to more robust plans
- **Tool Efficiency**: Dynamic discovery ensures optimal tool usage

### 2. Enhanced Adaptability

- **Learning**: Continuous improvement from experience
- **Flexibility**: Can handle novel situations without reprogramming
- **Scalability**: Recursive planning handles arbitrarily complex tasks

### 3. Better Observability

- **Reasoning Traces**: Full audit of decision-making process
- **Memory Analytics**: Insights into common failure patterns
- **Tool Usage**: Statistics on tool effectiveness

## Configuration Options

### AutonomyConfig

```python
@dataclass
class AutonomyConfig:
    # Feature flags
    enable_episodic_memory: bool = False
    enable_reasoning_kernel: bool = False
    enable_dynamic_tools: bool = False
    enable_recursive_planning: bool = False

    # Episodic Memory
    memory_similarity_threshold: float = 0.85
    memory_min_rating: float = 0.6

    # Reasoning Kernel
    reasoning_max_candidates: int = 3
    reasoning_critique_threshold: float = 0.7
    enable_tree_of_thoughts: bool = True

    # Tool Registry
    tool_max_matches: int = 5
    tool_min_relevance: float = 0.6

    # Recursive Planner
    planner_max_depth: int = 3
    planner_max_parallel: int = 5
```

## Best Practices

### 1. Gradual Enablement

Start with individual features and gradually enable more:

```python
# Phase 1: Enable only episodic memory
autonomy_config = AutonomyConfig(enable_episodic_memory=True)

# Phase 2: Add reasoning kernel
autonomy_config.enable_reasoning_kernel = True

# Phase 3: Enable all features
autonomy_config = AutonomyConfig(
    enable_episodic_memory=True,
    enable_reasoning_kernel=True,
    enable_dynamic_tools=True,
    enable_recursive_planning=True
)
```

### 2. Memory Management

- Set appropriate similarity thresholds to balance recall vs precision
- Regularly clean up old episodes to maintain performance
- Use agent role filtering for more relevant memory recall

### 3. Tool Organization

- Categorize tools logically (filesystem, network, analysis, etc.)
- Provide clear, descriptive tool descriptions
- Track tool usage to identify popular/effective tools

### 4. Recursive Planning

- Set reasonable depth limits to prevent infinite recursion
- Use parallel execution for independent sub-tasks
- Monitor resource usage when spawning many sub-orchestrators

## Monitoring and Debugging

### Telemetry Integration
The autonomy components emit telemetry events for monitoring:

```python
# Memory recall events
telemetry.record_event({
    "event_type": "MEMORY_RECALL",
    "payload": {
        "similarity_score": 0.92,
        "episodes_considered": 15,
        "memory_hit": True
    }
})

# Reasoning trace events
telemetry.record_event({
    "event_type": "REASONING_COMPLETE",
    "payload": {
        "candidates_generated": 3,
        "confidence_score": 0.87,
        "reasoning_time_ms": 1250
    }
})
```

### Debug Mode
Enable debug logging to trace autonomy decisions:

```python
logging.getLogger("agentic_core.L1_cognition").setLevel(logging.DEBUG)
logging.getLogger("runtime.core.reasoning_kernel").setLevel(logging.DEBUG)
logging.getLogger("agentic_core.L2_execution.tool_registry").setLevel(logging.DEBUG)
```

## Future Enhancements

1. **Collaborative Memory**: Share episodic memory across agents
2. **Meta-Learning**: Learn optimal reasoning strategies
3. **Tool Composition**: Automatically compose tools for complex tasks
4. **Adaptive Thresholds**: Dynamically adjust thresholds based on performance

## Migration Guide

### From Standard SubatomicHop
1. Import `AutonomousSubatomicHop` instead of `SubatomicHop`
2. Use `AutonomousHopConfig` instead of `SubatomicHopConfig`
3. Enable desired autonomy features in `AutonomyConfig`
4. Update initialization to pass autonomy config

### Example Migration

```python
# Before
from runtime.core.subatomic_hop import SubatomicHop, SubatomicHopConfig

hop = SubatomicHop(
    hop_function=my_function,
    config=SubatomicHopConfig()
)

# After
from runtime.core.autonomous_subatomic_hop import (
    AutonomousSubatomicHop,
    AutonomousHopConfig,
    AutonomyConfig
)

hop = AutonomousSubatomicHop(
    hop_function=my_function,
    config=AutonomousHopConfig(
        autonomy=AutonomyConfig(
            enable_episodic_memory=True,
            enable_reasoning_kernel=True
        )
    )
)
```

## Conclusion

The autonomy architecture transforms agents from simple executors into adaptive learners capable of:
- Learning from experience
- Thinking before acting
- Discovering tools dynamically
- Planning hierarchically

This represents a significant step toward truly autonomous AI agents that can handle complex, novel situations with minimal human intervention.
