# Runtime Directory Structure

This directory follows the canonical OpenAI agentic runtime architecture with clear separation of concerns.

## Migrated Modules (New Canonical Structure)

### 🚀 `inference/`

Core execution and context management

- `executor.py` - Main execution engine
- `execution_budget_manager.py` - Budget and resource limits
- `context_manager.py` - Context handling and state
- `runtime_utils.py` - Shared inference utilities

### 🎯 `orchestration/`

Policy and tool orchestration

- `policy_engine.py` - Policy enforcement and decisions
- `tool_registry.py` - Tool registration and discovery

### 💰 `cost/`

Cost tracking and management

- `cost_tracking.json` - Cost configuration and tracking data

### 📊 `telemetry/`

Metrics collection and monitoring

- `telemetry.py` - Telemetry bus and data collection
- `metrics.py` - Metrics computation and aggregation
- `metrics.json` - Metrics configuration and schema

### 🛠️ `utils/`

Shared utilities and observability

- `observability.py` - Observability infrastructure

## Existing Subdirectories (Unchanged)

These subdirectories were already properly organized and remain unchanged:

### 🏗️ `infra/`

Infrastructure components (sandbox, model routing, DI container)

- `sandbox/` - Sandboxing and isolation
- `model_routing/` - LLM model routing policies
- `di_container/` - Dependency injection container

### 🧠 `meta/`

Metacognition and retrieval systems

- `metacognition/` - Uncertainty modeling and hypothesis generation
- `retrieval/` - Information retrieval and ranking
- `ranking/` - Score computation and merging
- `schema_validation/` - Schema validation utilities

### 🧪 `eval/`

Evaluation and testing frameworks

- `simulation/` - Scenario simulation
- `golden_state/` - Golden state testing

### ⚙️ `core/`

Core models and shared data structures

- `models/` - Core data models and types

## Empty Directories (Future Use)

These directories are reserved for future canonical components:

- `safety_runtime/` - Runtime safety mechanisms
- `state/` - State management and persistence
- `mcp_middleware/` - Model Context Protocol middleware

## Import Guidelines

When importing from runtime, use the new canonical paths:

```python
# ✅ Correct imports for migrated modules
from runtime.inference.executor import Executor
from runtime.inference.execution_budget_manager import ExecutionBudgetManager
from runtime.orchestration.policy_engine import PolicyEngine
from runtime.telemetry.telemetry import get_telemetry_bus
from runtime.cost.cost_tracking import load_cost_config

# ✅ Existing imports (unchanged)
from runtime.infra.sandbox.models import ToolCallRequest
from runtime.meta.metacognition.models import Hypothesis
from runtime.eval.simulation.simulator import run_scenario
from runtime.core.models.models import ExecutionProfile
```

## Migration History

- **Date**: 2025-11-30
- **Files Migrated**: 11 root-level runtime files
- **Imports Updated**: 23 test files
- **Structure**: Canonical OpenAI agentic runtime architecture
- **Status**: ✅ Complete and verified
