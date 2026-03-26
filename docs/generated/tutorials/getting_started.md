# Getting Started with Agentic Workflow

# Getting Started with Agentic Workflow

## Introduction

The Agentic Workflow system is a sophisticated multi-layered architecture designed for autonomous agent execution with built-in governance and healing capabilities. This tutorial will guide you through the basics of setting up and using the system.

## Prerequisites

Before you begin, ensure you have:

- Python 3.8 or higher installed
- Git for version control
- A suitable IDE (VS Code recommended)
- Basic understanding of Python and agent-based systems

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/agentic-workflow.git
cd agentic-workflow
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Initial Setup

```bash
python scripts/setup.py
```

## Basic Concepts

### Layered Architecture

The system is organized into 6 distinct layers:

- **L0**: Routing and Orchestration
- **L1**: Reasoning and Decision Making
- **L2**: Execution and Tool Use
- **L3**: Workflow Orchestration
- **L4**: State Management
- **L5**: Safety and Governance

Each layer maintains sovereignty while coordinating with others through well-defined interfaces.

### Agents

Agents are autonomous execution units that inherit from `SovereignBaseAgent`. They can be enhanced with mixins for additional functionality.

### Safety and Governance

The L5 layer provides oversight and validation for all operations, ensuring safe and compliant execution.

## Your First Agent

### Creating a Simple Agent

```python
from agentic_core.core.base_agent import SovereignBaseAgent
from agentic_core.L1_reasoning.mixins.reasoning_mixin import ReasoningMixin

class MyFirstAgent(SovereignBaseAgent, ReasoningMixin):
    """A simple agent that demonstrates basic functionality."""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.reasoning_enabled = True
    
    def execute(self, task: dict) -> dict:
        """Execute a task with reasoning."""
        # Use reasoning mixin
        reasoning_result = self.reason_about_task(task)
        
        # Perform main execution
        result = {
            "task_id": task.get("id"),
            "status": "completed",
            "reasoning": reasoning_result,
            "output": f"Processed task: {task.get('description')}"
        }
        
        return result
```

### Running Your Agent

```python
from agentic_core.L0_routing.runtime_manager import RuntimeManager

# Create agent configuration
config = {
    "agent_id": "my_first_agent",
    "reasoning_enabled": True,
    "safety_checks": True
}

# Initialize and run agent
agent = MyFirstAgent(config)
runtime = RuntimeManager()

# Execute a task
task = {
    "id": "task_001",
    "description": "Process sample data"
}

result = runtime.execute_agent(agent, task)
print(result)
```

## Advanced Features

### Using Mixins

Mixins provide composable functionality:

```python
from agentic_core.L2_execution.mixins.tool_mixin import ToolMixin
from agentic_core.L4_state.mixins.state_mixin import StateMixin

class AdvancedAgent(SovereignBaseAgent, ReasoningMixin, ToolMixin, StateMixin):
    """An advanced agent with multiple capabilities."""
    
    def execute(self, task: dict) -> dict:
        # Reason about the task
        reasoning = self.reason_about_task(task)
        
        # Use tools if needed
        if reasoning.get("needs_tools"):
            tool_result = self.execute_tool(reasoning["tool_name"], reasoning["tool_args"])
        
        # Manage state
        self.update_state({"last_task": task["id"], "status": "processing"})
        
        return {
            "task_id": task["id"],
            "reasoning": reasoning,
            "tool_result": tool_result if reasoning.get("needs_tools") else None,
            "state": self.get_current_state()
        }
```

### Error Handling

The system provides comprehensive error handling:

```python
class RobustAgent(SovereignBaseAgent):
    """Agent with comprehensive error handling."""
    
    def execute(self, task: dict) -> dict:
        try:
            # Main execution logic
            result = self.process_task(task)
            
        except ValueError as e:
            # Handle validation errors
            logger.error(f"Validation error: {e}")
            result = {"error": "Invalid task data", "details": str(e)}
            
        except RuntimeError as e:
            # Handle runtime errors
            logger.error(f"Runtime error: {e}")
            result = {"error": "Execution failed", "details": str(e)}
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error: {e}")
            result = {"error": "Unexpected error", "details": str(e)}
        
        return result
```

## Testing Your Agent

### Unit Tests

```python
import pytest
from your_module import MyFirstAgent

class TestMyFirstAgent:
    def test_agent_initialization(self):
        config = {"agent_id": "test_agent"}
        agent = MyFirstAgent(config)
        
        assert agent.agent_id == "test_agent"
        assert agent.reasoning_enabled is True
    
    def test_agent_execution(self):
        config = {"agent_id": "test_agent"}
        agent = MyFirstAgent(config)
        
        task = {"id": "test_task", "description": "Test task"}
        result = agent.execute(task)
        
        assert result["task_id"] == "test_task"
        assert result["status"] == "completed"
        assert "reasoning" in result
```

### Integration Tests

```python
def test_agent_with_runtime_manager():
    config = {"agent_id": "integration_test_agent"}
    agent = MyFirstAgent(config)
    runtime = RuntimeManager()
    
    task = {"id": "integration_task", "description": "Integration test"}
    result = runtime.execute_agent(agent, task)
    
    assert result["status"] == "completed"
    assert "reasoning" in result
```

## Best Practices

### 1. Follow Layer Boundaries
- Keep L0 code in L0 modules
- Don't bypass layer interfaces
- Use proper dependency injection

### 2. Implement Proper Error Handling
- Handle specific exceptions
- Provide meaningful error messages
- Log errors appropriately

### 3. Write Comprehensive Tests
- Test both success and failure cases
- Use mocks for external dependencies
- Maintain good test coverage

### 4. Document Your Code
- Use clear docstrings
- Document public APIs
- Provide usage examples

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Permission Errors**: Check mutation prohibition settings
3. **Performance Issues**: Enable performance monitoring
4. **Test Failures**: Check test configuration and dependencies

### Getting Help

- Check the [troubleshooting guide](../troubleshooting/)
- Review the [API documentation](../api/)
- Join the team chat for questions
- Create GitHub issues for bugs

## Next Steps

Now that you've completed this tutorial:

1. Explore the [architecture documentation](../architecture/)
2. Review the [API reference](../api/)
3. Try the advanced examples
4. Contribute to the project

Happy coding with Agentic Workflow!
