#!/usr/bin/env python3
"""Phase 4 Documentation Generation Tool - Comprehensive Knowledge Transfer.

This tool generates comprehensive documentation for the Agentic Workflow system,
including API documentation, architectural overviews, tutorials, and knowledge
transfer materials.

Usage:
    python tools/generate_documentation.py --api agentic_core/L5_safety/
    python tools/generate_documentation.py --architecture agentic_core/
    python tools/generate_documentation.py --knowledge-transfer --all
    python tools/generate_documentation.py --validate docs/
"""

import argparse
import logging
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile


def _discover_repo_root(start: Path) -> Path:
    """Best-effort repository root discovery for direct script and package execution."""
    for candidate in (start, *start.parents):
        if (candidate / "agentic_core").exists() or (candidate / ".git").exists():
            return candidate
        if candidate.name == "tools" and (candidate / "generate").exists():
            return candidate.parent
    return start.parent.parent


REPO_ROOT = _discover_repo_root(Path(__file__).resolve().parent)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _atomic_write_text(path: Path, content: str) -> None:
    """Write text atomically to avoid truncated docs on interruption."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


from agentic_core.core.documentation_framework import (
    DocumentationType,
    documentation_manager,
)
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def generate_api_documentation(source_paths: list[Path], output_dir: Path) -> bool:
    """Generate API documentation from Python source files."""
    logger.info("Generating API documentation...")

    success = True

    for source_path in tqdm(source_paths, desc="Processing", unit="item"):
        if not source_path.exists():
            logger.warning(f"Source path not found: {source_path}")
            continue

        # Find Python files
        if source_path.is_file():
            python_files = [source_path]
        else:
            python_files = list(source_path.rglob("*.py"))

        for py_file in tqdm(python_files, desc="Processing", unit="item"):
            try:
                # Generate output path
                relative_path = py_file.relative_to(source_path.parent)
                output_path = output_dir / "api" / relative_path.with_suffix(".md")

                logger.info(f"Generating API docs for: {py_file}")
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Generate documentation
                artifact = documentation_manager.generate_documentation(
                    DocumentationType.API_REFERENCE,
                    py_file,
                    output_path,
                )

                logger.info(f"✅ Generated: {output_path}")

            except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
                logger.exception("Failed to generate API docs for %s", py_file)
                success = False

    return success


def generate_architecture_documentation(source_path: Path, output_dir: Path) -> bool:
    """Generate comprehensive architectural documentation."""
    logger.info("Generating architectural documentation...")

    try:
        output_path = output_dir / "architecture" / "system_overview.md"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        artifact = documentation_manager.generate_documentation(
            DocumentationType.ARCHITECTURAL_OVERVIEW,
            source_path,
            output_path,
        )

        logger.info(f"✅ Generated: {output_path}")
        return True

    except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
        logger.error(f"Failed to generate architecture documentation: {e}")
        return False


def generate_knowledge_transfer_docs(output_dir: Path) -> bool:
    """Generate comprehensive knowledge transfer documentation."""
    logger.info("Generating knowledge transfer documentation...")

    try:
        output_path = output_dir / "knowledge_transfer" / "developer_onboarding.md"

        artifact = documentation_manager.generate_documentation(
            DocumentationType.KNOWLEDGE_TRANSFER,
            None,  # Knowledge transfer doesn't require source
            output_path,
        )

        logger.info(f"✅ Generated: {output_path}")
        return True

    except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
        logger.error(f"Failed to generate knowledge transfer documentation: {e}")
        return False


def generate_tutorials(output_dir: Path) -> bool:
    """Generate tutorial documentation."""
    logger.info("Generating tutorial documentation...")

    tutorials = [
        {
            "title": "Getting Started with Agentic Workflow",
            "content": """# Getting Started with Agentic Workflow

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
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
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
    \"\"\"A simple agent that demonstrates basic functionality.\"\"\"

    def __init__(self, config: dict):
        super().__init__(config)
        self.reasoning_enabled = True

    def execute(self, task: dict) -> dict:
        \"\"\"Execute a task with reasoning.\"\"\"
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
    \"\"\"An advanced agent with multiple capabilities.\"\"\"

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
    \"\"\"Agent with comprehensive error handling.\"\"\"

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

        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
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
""",
            "file_name": "getting_started.md",
        },
        {
            "title": "Agent Development Guide",
            "content": """# Agent Development Guide

## Overview

This guide covers advanced agent development patterns, best practices, and common scenarios in the Agentic Workflow system.

## Agent Architecture

### Base Agent Class

All agents inherit from `SovereignBaseAgent`, which provides:

- Lifecycle management (initialize, execute, cleanup)
- State management capabilities
- Safety and governance integration
- Logging and monitoring

### Mixin System

Mixins provide composable functionality:

- **ReasoningMixin**: Cognitive processing and decision making
- **ToolMixin**: External tool integration and execution
- **StateMixin**: Advanced state management
- **HealingMixin**: Self-healing capabilities
- **ValidationMixin**: Input validation and sanitization

## Development Patterns

### 1. Basic Agent Pattern

```python
from agentic_core.core.base_agent import SovereignBaseAgent

class BasicAgent(SovereignBaseAgent):
    def __init__(self, config: dict):
        super().__init__(config)
        self.setup_agent_specific_config(config)

    def execute(self, task: dict) -> dict:
        # Validate input
        self.validate_task(task)

        # Process task
        result = self.process_task(task)

        # Validate output
        self.validate_result(result)

        return result
```

### 2. Reasoning Agent Pattern

```python
from agentic_core.L1_reasoning.mixins.reasoning_mixin import ReasoningMixin

class ReasoningAgent(SovereignBaseAgent, ReasoningMixin):
    def execute(self, task: dict) -> dict:
        # Reason about the task
        reasoning = self.reason_about_task(task)

        # Choose execution strategy
        strategy = self.select_strategy(reasoning)

        # Execute with strategy
        result = self.execute_with_strategy(task, strategy)

        return result
```

### 3. Tool-Using Agent Pattern

```python
from agentic_core.L2_execution.mixins.tool_mixin import ToolMixin

class ToolAgent(SovereignBaseAgent, ToolMixin):
    def __init__(self, config: dict):
        super().__init__(config)
        self.register_tools([
            "file_processor",
            "data_analyzer",
            "report_generator"
        ])

    def execute(self, task: dict) -> dict:
        # Determine required tools
        required_tools = self.analyze_tool_requirements(task)

        # Execute tools in sequence
        results = {}
        for tool in required_tools:
            results[tool] = self.execute_tool(tool, task)

        return self.consolidate_results(results)
```

### 4. Stateful Agent Pattern

```python
from agentic_core.L4_state.mixins.state_mixin import StateMixin

class StatefulAgent(SovereignBaseAgent, StateMixin):
    def execute(self, task: dict) -> dict:
        # Load previous state
        previous_state = self.load_state(task.get("session_id"))

        # Process with context
        result = self.process_with_context(task, previous_state)

        # Save new state
        self.save_state(task.get("session_id"), result)

        return result
```

## Advanced Features

### Custom Mixins

Create your own mixins for reusable functionality:

```python
class CustomMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_feature = True

    def custom_operation(self, data: dict) -> dict:
        # Custom logic here
        return processed_data

class CustomAgent(SovereignBaseAgent, CustomMixin):
    def execute(self, task: dict) -> dict:
        # Use custom mixin functionality
        return self.custom_operation(task)
```

### Async Agent Pattern

For I/O-bound operations:

```python
import asyncio
from agentic_core.core.base_agent import AsyncSovereignBaseAgent

class AsyncAgent(AsyncSovereignBaseAgent):
    async def execute(self, task: dict) -> dict:
        # Async operations
        result = await self.process_async(task)
        return result
```

### Multi-Agent Coordination

```python
class CoordinatorAgent(SovereignBaseAgent):
    def __init__(self, config: dict):
        super().__init__(config)
        self.sub_agents = self.initialize_sub_agents(config)

    def execute(self, task: dict) -> dict:
        # Decompose task
        subtasks = self.decompose_task(task)

        # Execute subtasks
        results = {}
        for subtask in subtasks:
            agent = self.select_agent(subtask)
            results[subtask["id"]] = agent.execute(subtask)

        # Consolidate results
        return self.consolidate_results(results)
```

## Testing Strategies

### Unit Testing

```python
import pytest
from unittest.mock import Mock, patch

class TestMyAgent:
    def test_execute_success(self):
        config = {"agent_id": "test"}
        agent = MyAgent(config)

        task = {"id": "test", "data": "sample"}
        result = agent.execute(task)

        assert result["status"] == "success"
        assert "output" in result

    def test_execute_with_mock(self):
        config = {"agent_id": "test"}
        agent = MyAgent(config)

        # Mock external dependencies
        with patch.object(agent, 'external_service') as mock_service:
            mock_service.return_value = {"result": "mocked"}

            task = {"id": "test", "use_external": True}
            result = agent.execute(task)

            assert result["output"] == "mocked"
            mock_service.assert_called_once()
```

### Integration Testing

```python
def test_agent_integration():
    # Test with real dependencies
    config = {"agent_id": "integration_test"}
    agent = MyAgent(config)

    # Test full workflow
    task = create_complex_task()
    result = agent.execute(task)

    # Validate end-to-end behavior
    assert result["status"] == "success"
    assert all_required_fields_present(result)
```

### Performance Testing

```python
import time

def test_agent_performance():
    config = {"agent_id": "performance_test"}
    agent = MyAgent(config)

    # Measure execution time
    start_time = time.time()
    result = agent.execute(create_large_task())
    execution_time = time.time() - start_time

    # Validate performance requirements
    assert execution_time < 5.0  # Should complete within 5 seconds
    assert result["status"] == "success"
```

## Error Handling Patterns

### Structured Error Handling

```python
class RobustAgent(SovereignBaseAgent):
    def execute(self, task: dict) -> dict:
        try:
            # Pre-execution validation
            self.validate_preconditions(task)

            # Main execution
            result = self.execute_main(task)

            # Post-execution validation
            self.validate_result(result)

            return result

        except ValidationError as e:
            return self.handle_validation_error(e, task)

        except ExecutionError as e:
            return self.handle_execution_error(e, task)

        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            return self.handle_unexpected_error(e, task)
```

### Retry Pattern

```python
class RetryAgent(SovereignBaseAgent):
    def execute(self, task: dict) -> dict:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return self.execute_with_retry(task)

            except TemporaryError as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
```

## Performance Optimization

### Caching Pattern

```python
class CachedAgent(SovereignBaseAgent):
    def __init__(self, config: dict):
        super().__init__(config)
        self.cache = {}

    def execute(self, task: dict) -> dict:
        cache_key = self.generate_cache_key(task)

        if cache_key in self.cache:
            return self.cache[cache_key]

        result = self.compute_result(task)
        self.cache[cache_key] = result

        return result
```

### Batch Processing Pattern

```python
class BatchAgent(SovereignBaseAgent):
    def execute(self, task: dict) -> dict:
        items = task.get("items", [])

        # Process in batches
        batch_size = 100
        results = []

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = self.process_batch(batch)
            results.extend(batch_results)

        return {"results": results, "total_processed": len(items)}
```

## Best Practices

### 1. Configuration Management

```python
class ConfiguredAgent(SovereignBaseAgent):
    def __init__(self, config: dict):
        super().__init__(config)
        self.validate_config(config)
        self.setup_from_config(config)

    def validate_config(self, config: dict):
        required_fields = ["agent_id", "mode", "timeout"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required config field: {field}")
```

### 2. Resource Management

```python
class ResourceAwareAgent(SovereignBaseAgent):
    def execute(self, task: dict) -> dict:
        # Acquire resources
        with self.acquire_resources():
            # Execute with resources
            result = self.execute_with_resources(task)

        return result
```

### 3. Monitoring and Observability

```python
class MonitoredAgent(SovereignBaseAgent):
    def execute(self, task: dict) -> dict:
        with self.monitor_execution("execute"):
            result = self.execute_main(task)
            self.record_metrics(task, result)
            return result
```

## Migration and Upgrade

### Version Compatibility

```python
class VersionedAgent(SovereignBaseAgent):
    SUPPORTED_VERSIONS = ["1.0", "1.1", "2.0"]

    def execute(self, task: dict) -> dict:
        version = task.get("version", "1.0")

        if version not in self.SUPPORTED_VERSIONS:
            raise ValueError(f"Unsupported version: {version}")

        # Route to version-specific handler
        handler = getattr(self, f"execute_v{version.replace('.', '_')}")
        return handler(task)
```

This guide provides comprehensive patterns and best practices for developing robust agents in the Agentic Workflow system.
""",
            "file_name": "agent_development.md",
        },
    ]

    success = True
    tutorials_dir = output_dir / "tutorials"

    for tutorial in tqdm(tutorials, desc="Processing", unit="item"):
        try:
            tutorial_path = tutorials_dir / tutorial["file_name"]
            tutorial_path.parent.mkdir(parents=True, exist_ok=True)

            with open(tutorial_path, "w", encoding="utf-8") as f:
                f.write(f"# {tutorial['title']}\n\n")
                f.write(tutorial["content"])

            logger.info(f"✅ Generated tutorial: {tutorial_path}")

        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            logger.error(f"Failed to generate tutorial {tutorial['file_name']}: {e}")
            success = False

    return success


def validate_documentation(docs_dir: Path) -> bool:
    """Validate existing documentation quality."""
    logger.info("Validating documentation quality...")

    from agentic_core.core.documentation_framework import DocumentationQualityValidator

    validator = DocumentationQualityValidator()
    md_files = list(docs_dir.rglob("*.md"))

    total_files = len(md_files)
    valid_files = 0

    for md_file in tqdm(md_files, desc="Processing", unit="item"):
        try:
            with open(md_file, encoding="utf-8") as f:
                content = f.read()

            # Simple validation (in real implementation, would use proper parsing)
            if len(content) > 100 and "#" in content:
                valid_files += 1
                logger.info(f"✅ Valid: {md_file.name}")
            else:
                logger.warning(f"⚠️  Low quality: {md_file.name}")

        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            logger.error(f"❌ Failed to validate {md_file}: {e}")

    logger.info(f"Documentation validation: {valid_files}/{total_files} files passed")
    return valid_files == total_files


def generate_documentation_index(docs_dir: Path) -> bool:
    """Generate a comprehensive documentation index."""
    logger.info("Generating documentation index...")

    try:
        index_content = """# Agentic Workflow Documentation

## Overview

This is the comprehensive documentation for the Agentic Workflow system, a multi-layered architecture for autonomous agent execution with built-in governance and healing capabilities.

## Documentation Structure

### 📚 API Documentation
Detailed API reference for all components, classes, and methods.

- [Core API](api/core/) - Core framework and base classes
- [L0 Routing API](api/L0_routing/) - Routing and orchestration components
- [L1 Reasoning API](api/L1_reasoning/) - Reasoning and decision making
- [L2 Execution API](api/L2_execution/) - Tool execution and external integration
- [L3 Orchestration API](api/L3_orchestration/) - Workflow orchestration
- [L4 State API](api/L4_state/) - State management and persistence
- [L5 Safety API](api/L5_safety/) - Safety and governance components

### 🏗️ Architecture Documentation
System architecture, design patterns, and integration guides.

- [System Overview](architecture/system_overview.md) - Complete system architecture
- [Layer Documentation](architecture/) - Detailed layer documentation
- [Design Patterns](architecture/patterns/) - Common design patterns
- [Integration Guide](architecture/integration.md) - Integration with external systems

### 🎓 Tutorials and Guides
Step-by-step tutorials and comprehensive guides.

- [Getting Started](tutorials/getting_started.md) - Quick start guide
- [Agent Development](tutorials/agent_development.md) - Agent development guide
- [Advanced Features](tutorials/advanced/) - Advanced features and patterns
- [Best Practices](tutorials/best_practices.md) - Development best practices

### 📖 Knowledge Transfer
Comprehensive knowledge transfer materials for team onboarding.

- [Developer Onboarding](knowledge_transfer/developer_onboarding.md) - New developer guide
- [Architecture Deep Dive](knowledge_transfer/architecture_dive.md) - Detailed architecture guide
- [Development Workflows](knowledge_transfer/workflows.md) - Development processes
- [Troubleshooting Guide](knowledge_transfer/troubleshooting.md) - Common issues and solutions

### 🔧 Reference Materials
Additional reference materials and resources.

- [Configuration Reference](reference/configuration.md) - Configuration options
- [Error Codes](reference/error_codes.md) - Error code reference
- [Performance Guide](reference/performance.md) - Performance optimization
- [Security Guide](reference/security.md) - Security considerations

## Quick Links

### For New Developers
1. [Getting Started](tutorials/getting_started.md)
2. [Developer Onboarding](knowledge_transfer/developer_onboarding.md)
3. [API Reference](api/)

### For Architects
1. [System Overview](architecture/system_overview.md)
2. [Architecture Deep Dive](knowledge_transfer/architecture_dive.md)
3. [Design Patterns](architecture/patterns/)

### For Operators
1. [Configuration Reference](reference/configuration.md)
2. [Troubleshooting Guide](knowledge_transfer/troubleshooting.md)
3. [Performance Guide](reference/performance.md)

## Contributing to Documentation

### Adding Documentation
1. Choose the appropriate section based on content type
2. Follow the established documentation patterns
3. Include examples and code samples
4. Test all code examples

### Documentation Standards
- Use clear, concise language
- Include practical examples
- Maintain consistent formatting
- Update related documentation when making changes

### Review Process
- All documentation changes require review
- Technical accuracy must be validated
- User perspective should be considered
- Accessibility standards must be met

## Getting Help

If you need help with the documentation:

1. Check the [troubleshooting guide](knowledge_transfer/troubleshooting.md)
2. Search existing documentation
3. Ask questions in team chat
4. Create documentation issues for improvements

## Documentation Metadata

**Generated**: {datetime.now().isoformat()}
**Version**: 1.0.0
**Last Updated**: {datetime.now().strftime("%Y-%m-%d")}
**Maintainers**: Agentic Workflow Team

---

*This documentation is continuously updated. Check back regularly for the latest information.*
"""

        index_path = docs_dir / "README.md"
        index_path.parent.mkdir(parents=True, exist_ok=True)

        _atomic_write_text(index_path, index_content)

        logger.info(f"✅ Generated documentation index: {index_path}")
        return True

    except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
        logger.error(f"Failed to generate documentation index: {e}")
        return False


def main():
    """Main entry point for documentation generation."""
    parser = argparse.ArgumentParser(
        description="Documentation Generation Tool - Phase 4 Implementation",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # API documentation command
    api_parser = subparsers.add_parser("api", help="Generate API documentation")
    api_parser.add_argument("sources", nargs="+", help="Source files or directories")
    api_parser.add_argument("--output", default="docs/generated", help="Output directory")

    # Architecture documentation command
    arch_parser = subparsers.add_parser("architecture", help="Generate architecture documentation")
    arch_parser.add_argument("source", help="Source directory for architecture analysis")
    arch_parser.add_argument("--output", default="docs/generated", help="Output directory")

    # Knowledge transfer command
    kt_parser = subparsers.add_parser("knowledge-transfer", help="Generate knowledge transfer docs")
    kt_parser.add_argument("--output", default="docs/generated", help="Output directory")
    kt_parser.add_argument("--all", action="store_true", help="Generate all knowledge transfer materials")

    # Tutorials command
    tutorials_parser = subparsers.add_parser("tutorials", help="Generate tutorial documentation")
    tutorials_parser.add_argument("--output", default="docs/generated", help="Output directory")

    # Validation command
    validate_parser = subparsers.add_parser("validate", help="Validate documentation quality")
    validate_parser.add_argument("docs_dir", help="Documentation directory to validate")

    # Index command
    index_parser = subparsers.add_parser("index", help="Generate documentation index")
    index_parser.add_argument("--output", default="docs", help="Documentation directory")

    # Generate all command
    all_parser = subparsers.add_parser("all", help="Generate all documentation")
    all_parser.add_argument("--source", default="agentic_core", help="Source directory")
    all_parser.add_argument("--output", default="docs/generated", help="Output directory")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    success = True

    if args.command == "api":
        source_paths = [Path(p) for p in args.sources]
        output_dir = Path(args.output)
        success = generate_api_documentation(source_paths, output_dir)

    elif args.command == "architecture":
        source_path = Path(args.source)
        output_dir = Path(args.output)
        success = generate_architecture_documentation(source_path, output_dir)

    elif args.command == "knowledge-transfer":
        output_dir = Path(args.output)
        success = generate_knowledge_transfer_docs(output_dir)

    elif args.command == "tutorials":
        output_dir = Path(args.output)
        success = generate_tutorials(output_dir)

    elif args.command == "validate":
        docs_dir = Path(args.docs_dir)
        success = validate_documentation(docs_dir)

    elif args.command == "index":
        output_dir = Path(args.output)
        success = generate_documentation_index(output_dir)

    elif args.command == "all":
        source_path = Path(args.source)
        output_dir = Path(args.output)

        logger.info("Generating all documentation...")

        # Generate API docs
        api_paths = [
            source_path / layer
            for layer in [
                "L0_routing",
                "L1_reasoning",
                "L2_execution",
                "L3_orchestration",
                "L4_state",
                "L5_safety",
            ]
        ]
        success &= generate_api_documentation(api_paths, output_dir)

        # Generate architecture docs
        success &= generate_architecture_documentation(source_path, output_dir)

        # Generate knowledge transfer docs
        success &= generate_knowledge_transfer_docs(output_dir)

        # Generate tutorials
        success &= generate_tutorials(output_dir)

        # Generate index
        success &= generate_documentation_index(output_dir)

        logger.info(f"Documentation generation complete. Results in: {output_dir}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
