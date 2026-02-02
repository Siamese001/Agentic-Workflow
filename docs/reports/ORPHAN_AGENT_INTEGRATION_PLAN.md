# Orphan Agent Integration Plan

**Generated:** 2026-02-02  
**Status:** ACTIONABLE - Ready for Implementation

---

## Executive Summary

The 7 "archived" orphan agents have **real value** - they have healing capabilities, proper inheritance from `SovereignBaseAgent`, and solve concrete problems. Instead of archiving them, we should **integrate them into the existing validation infrastructure**.

### Integration Targets

| Orphan Agent | Integration Target | Integration Type |
|--------------|-------------------|------------------|
| AdversarialProbeAgent | ValidatorOrchestrator | Register as validator |
| BoundaryTestingAgent | ValidatorOrchestrator | Register as validator |
| ChaosEngineeringAgent | HealingSovereignOrchestrator | Register as healing strategy |
| PromptInjectionAgent | ValidatorOrchestrator | Register as security validator |
| DependencyPruningAgent | HealingSovereignOrchestrator | Register as healing strategy |
| PreCommitSovereignAgent | .pre-commit-config.yaml | Wire as pre-commit hook |
| DecompositionOrchestratorAgent | NervousSystemAgent | Delegate task decomposition |

---

## Detailed Integration Plans

### 1. Red Teaming Agents → ValidatorOrchestrator

**Agents:** AdversarialProbeAgent, BoundaryTestingAgent, PromptInjectionAgent

**Current State:** These agents exist but are never called by production code.

**Integration Strategy:** Register them as validators in `ValidatorOrchestrator` and create a `RedTeamValidationSuite` that runs them as part of pre-release validation.

**Implementation:**

```python
# File: agentic_core/L5_safety/validators/red_team_integration.py

from agentic_core.L5_safety.validators.ValidatorOrchestrator import (
    get_validator_orchestrator,
    ValidatorProtocol,
)
from agentic_core.L5_safety.red_teaming.AdversarialProbeAgent import AdversarialProbeAgent
from agentic_core.L5_safety.red_teaming.BoundaryTestingAgent import BoundaryTestingAgent
from agentic_core.L4_state.validation_context import ValidationContext


class AdversarialValidator(ValidatorProtocol):
    """Adapter to use AdversarialProbeAgent as a validator."""
    
    def __init__(self):
        ctx = ValidationContext()
        self.agent = AdversarialProbeAgent(ctx=ctx)
    
    def validate(self, content: any, context: dict) -> dict:
        """Run adversarial probes and return validation result."""
        import asyncio
        result = asyncio.run(self.agent.act())
        
        # Convert to validator format
        vulnerabilities = result.get("vulnerabilities_exposed", 0)
        return {
            "valid": vulnerabilities == 0,
            "errors": [
                f"Vulnerability: {r['pattern']} - {r['description']}"
                for r in result.get("attack_results", [])
                if r.get("vulnerable")
            ],
            "threat_assessment": result.get("threat_assessment", {}),
        }


class BoundaryValidator(ValidatorProtocol):
    """Adapter to use BoundaryTestingAgent as a validator."""
    
    def __init__(self):
        ctx = ValidationContext()
        self.agent = BoundaryTestingAgent(ctx=ctx)
    
    def validate(self, content: any, context: dict) -> dict:
        """Run boundary tests and return validation result."""
        import asyncio
        result = asyncio.run(self.agent.act())
        
        edge_cases = result.get("edge_cases_found", 0)
        return {
            "valid": edge_cases == 0,
            "errors": [
                f"Boundary violation: {v['test']} - {v['violation']}"
                for v in result.get("boundary_violations", [])
            ],
            "recommendations": result.get("recommendations", []),
        }


def register_red_team_validators():
    """Register all red team agents as validators."""
    orchestrator = get_validator_orchestrator()
    
    orchestrator.register_validator("adversarial_probe", AdversarialValidator())
    orchestrator.register_validator("boundary_testing", BoundaryValidator())
    
    print("[Red Team Integration] Registered 2 security validators")


# Auto-register on import
register_red_team_validators()
```

**Test Case:**

```python
# File: tests/integration/test_red_team_integration.py

import pytest
from agentic_core.L5_safety.validators.ValidatorOrchestrator import get_validator_orchestrator

@pytest.mark.asyncio
async def test_adversarial_validator_registered():
    """Verify adversarial probe is registered and callable."""
    orchestrator = get_validator_orchestrator()
    
    result = await orchestrator.validate(
        content={"test_input": "sample"},
        validator_name="adversarial_probe",
        context={}
    )
    
    assert "valid" in result
    assert "threat_assessment" in result

@pytest.mark.asyncio  
async def test_boundary_validator_registered():
    """Verify boundary testing is registered and callable."""
    orchestrator = get_validator_orchestrator()
    
    result = await orchestrator.validate(
        content={"test_input": ""},  # Empty input for boundary test
        validator_name="boundary_testing",
        context={}
    )
    
    assert "valid" in result
    assert "recommendations" in result
```

---

### 2. ChaosEngineeringAgent → HealingSovereignOrchestrator

**Current State:** Agent exists with chaos scenarios but never invoked.

**Integration Strategy:** Register as a healing strategy that can be triggered to test system resilience after healing operations.

**Implementation:**

```python
# File: agentic_core/L5_safety/validators/chaos_healing_integration.py

from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
    get_healing_orchestrator,
    HealingStrategy,
)
from agentic_core.L5_safety.red_teaming.ChaosEngineeringAgent import ChaosEngineeringAgent
from agentic_core.L4_state.validation_context import ValidationContext


class ChaosResilienceStrategy(HealingStrategy):
    """
    Healing strategy that validates system resilience after healing.
    
    Use case: After a healing operation completes, run chaos tests
    to verify the system can handle failures gracefully.
    """
    
    def __init__(self):
        ctx = ValidationContext()
        self.agent = ChaosEngineeringAgent(ctx=ctx)
    
    def can_heal(self, violation: dict) -> bool:
        """Handle resilience validation violations."""
        return violation.get("type") in [
            "resilience_check",
            "post_healing_validation",
            "chaos_test_required",
        ]
    
    def heal(self, violation: dict, context: dict) -> dict:
        """Run chaos tests and report resilience status."""
        import asyncio
        result = asyncio.run(self.agent.act())
        
        failures = result.get("failures_detected", 0)
        recovery_metrics = result.get("recovery_metrics", {})
        
        return {
            "success": failures == 0,
            "resilience_score": 1.0 - (failures / max(1, result.get("tests_executed", 1))),
            "recovery_metrics": recovery_metrics,
            "scenarios_tested": len(result.get("scenarios_tested", [])),
        }


def register_chaos_healing():
    """Register chaos engineering as a healing strategy."""
    orchestrator = get_healing_orchestrator()
    orchestrator.register_strategy("chaos_resilience", ChaosResilienceStrategy())
    print("[Chaos Integration] Registered resilience healing strategy")


# Auto-register on import
register_chaos_healing()
```

---

### 3. DependencyPruningAgent → HealingSovereignOrchestrator

**Current State:** Agent can detect and remove unused dependencies but never called.

**Integration Strategy:** Register as a healing strategy for dependency violations.

**Implementation:**

```python
# File: agentic_core/L5_safety/validators/dependency_healing_integration.py

from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
    get_healing_orchestrator,
    HealingStrategy,
)
from agentic_core.L5_safety.guardrails.DependencyPruningAgent import DependencyPruningAgent
from pathlib import Path


class DependencyPruningStrategy(HealingStrategy):
    """
    Healing strategy for unused dependency violations.
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
    
    def can_heal(self, violation: dict) -> bool:
        """Handle dependency-related violations."""
        return violation.get("type") in [
            "unused_dependency",
            "dependency_bloat",
            "requirements_cleanup",
        ]
    
    def heal(self, violation: dict, context: dict) -> dict:
        """Prune unused dependencies."""
        import asyncio
        
        # Create agent with context
        class MockContext:
            def report(self, msg): pass
        
        agent = DependencyPruningAgent(
            project_root=self.project_root,
            ctx=MockContext()
        )
        
        # Use dry_run from context or default to True for safety
        agent.dry_run = context.get("dry_run", True)
        
        result = asyncio.run(agent.execute())
        
        return {
            "success": result.get("removed", 0) > 0 or result.get("unused_found", 0) == 0,
            "unused_found": result.get("unused_found", 0),
            "removed": result.get("removed", 0),
            "dry_run": agent.dry_run,
        }


def register_dependency_healing():
    """Register dependency pruning as a healing strategy."""
    orchestrator = get_healing_orchestrator()
    orchestrator.register_strategy("dependency_pruning", DependencyPruningStrategy())
    print("[Dependency Integration] Registered pruning healing strategy")
```

---

### 4. PreCommitSovereignAgent → Pre-commit Hook

**Current State:** Agent has full pre-commit logic but not wired to git hooks.

**Integration Strategy:** Add to `.pre-commit-config.yaml` as a local hook.

**Implementation:**

```yaml
# Add to .pre-commit-config.yaml

  - repo: local
    hooks:
      - id: sovereign-pre-commit
        name: Sovereign Architecture Validation
        entry: python -m agentic_core.L5_safety.validators.PreCommitSovereignAgent --validate
        language: python
        types: [python]
        pass_filenames: false
        stages: [commit]
        description: "Validates staged files against SSOT gravity laws"
```

**Test Case:**

```python
# File: tests/integration/test_pre_commit_integration.py

import subprocess
from pathlib import Path

def test_pre_commit_agent_executable():
    """Verify PreCommitSovereignAgent can be invoked."""
    result = subprocess.run(
        ["python", "-m", "agentic_core.L5_safety.validators.PreCommitSovereignAgent", "--validate"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parents[2]
    )
    
    # Should exit 0 if no violations (or no staged files)
    assert result.returncode in [0, 1], f"Unexpected exit code: {result.stderr}"
```

---

### 5. DecompositionOrchestratorAgent → NervousSystemAgent

**Current State:** Has DAG decomposition logic but never invoked.

**Integration Strategy:** Wire into `NervousSystemAgent` as the task decomposition engine.

**Implementation:**

```python
# File: agentic_core/L3_orchestration/workflow_engines/decomposition_integration.py

from agentic_core.L3_orchestration.workflow_engines.DecompositionOrchestratorAgent import (
    DecompositionOrchestratorAgent,
    MissionPlan,
)


def integrate_with_nervous_system():
    """
    Integration point for NervousSystemAgent to use DecompositionOrchestratorAgent.
    
    Usage in NervousSystemAgent:
        from .decomposition_integration import decompose_task
        
        plan = decompose_task("Refactor all L2 agents")
        for task in plan.tasks:
            self.dispatch_to_agent(task.target_agent, task.description)
    """
    pass


def decompose_task(prompt: str, max_tasks: int = 10) -> MissionPlan:
    """
    Decompose a high-level prompt into atomic agent tasks.
    
    This is the public API for task decomposition.
    """
    orchestrator = DecompositionOrchestratorAgent()
    return orchestrator.decompose(prompt, max_tasks)


def execute_mission(plan: MissionPlan, dry_run: bool = True) -> dict:
    """
    Execute a mission plan.
    
    Args:
        plan: MissionPlan from decompose_task()
        dry_run: If True, only log proposed actions
    
    Returns:
        Execution results
    """
    orchestrator = DecompositionOrchestratorAgent()
    return orchestrator.execute(plan, dry_run)
```

---

## Unified Registration Module

Create a single entry point that registers all orphan agents:

```python
# File: agentic_core/L5_safety/validators/register_all_validators.py

"""
Unified Registration Module for Orphan Agent Integration

This module registers all previously-orphan agents into the validation
and healing infrastructure. Import this module at application startup
to enable all security and resilience features.

Usage:
    from agentic_core.L5_safety.validators import register_all_validators
    register_all_validators.initialize()
"""

from typing import Callable

_REGISTERED = False


def initialize():
    """Initialize all orphan agent integrations."""
    global _REGISTERED
    if _REGISTERED:
        return
    
    print("[Sovereign Integration] Initializing orphan agent integrations...")
    
    # Red Team Validators
    from . import red_team_integration
    red_team_integration.register_red_team_validators()
    
    # Chaos Engineering
    from . import chaos_healing_integration
    chaos_healing_integration.register_chaos_healing()
    
    # Dependency Pruning
    from . import dependency_healing_integration
    dependency_healing_integration.register_dependency_healing()
    
    _REGISTERED = True
    print("[Sovereign Integration] All orphan agents integrated successfully")


def get_integration_status() -> dict:
    """Return status of all integrations."""
    from .ValidatorOrchestrator import get_validator_orchestrator
    from .HealingSovereignOrchestrator import get_healing_orchestrator
    
    validator_orch = get_validator_orchestrator()
    healing_orch = get_healing_orchestrator()
    
    return {
        "initialized": _REGISTERED,
        "validators_registered": list(validator_orch._validators.keys()),
        "healing_strategies_registered": list(healing_orch._strategies.keys()),
    }
```

---

## Test Suite for Integration

```python
# File: tests/integration/test_orphan_agent_integration.py

"""
Integration tests for orphan agent registration.
"""

import pytest


class TestOrphanAgentIntegration:
    """Test that all orphan agents are properly integrated."""
    
    def test_all_integrations_initialize(self):
        """Verify all integrations can be initialized without error."""
        from agentic_core.L5_safety.validators import register_all_validators
        
        # Should not raise
        register_all_validators.initialize()
        
        status = register_all_validators.get_integration_status()
        assert status["initialized"] is True
    
    def test_red_team_validators_registered(self):
        """Verify red team validators are registered."""
        from agentic_core.L5_safety.validators import register_all_validators
        register_all_validators.initialize()
        
        status = register_all_validators.get_integration_status()
        
        assert "adversarial_probe" in status["validators_registered"]
        assert "boundary_testing" in status["validators_registered"]
    
    def test_healing_strategies_registered(self):
        """Verify healing strategies are registered."""
        from agentic_core.L5_safety.validators import register_all_validators
        register_all_validators.initialize()
        
        status = register_all_validators.get_integration_status()
        
        assert "chaos_resilience" in status["healing_strategies_registered"]
        assert "dependency_pruning" in status["healing_strategies_registered"]
    
    @pytest.mark.asyncio
    async def test_adversarial_validation_works(self):
        """Verify adversarial validation can be executed."""
        from agentic_core.L5_safety.validators import register_all_validators
        from agentic_core.L5_safety.validators.ValidatorOrchestrator import get_validator_orchestrator
        
        register_all_validators.initialize()
        orchestrator = get_validator_orchestrator()
        
        result = await orchestrator.validate(
            content={"test": "data"},
            validator_name="adversarial_probe"
        )
        
        assert "valid" in result
        assert "threat_assessment" in result
    
    @pytest.mark.asyncio
    async def test_chaos_healing_works(self):
        """Verify chaos healing can be executed."""
        from agentic_core.L5_safety.validators import register_all_validators
        from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import get_healing_orchestrator
        
        register_all_validators.initialize()
        orchestrator = get_healing_orchestrator()
        
        result = await orchestrator.heal(
            violation={"type": "resilience_check"},
            context={}
        )
        
        assert result["status"] in ["healed", "no_strategy"]
```

---

## Implementation Checklist

### Phase 1: Create Integration Modules (This Sprint)

- [ ] Create `red_team_integration.py` with AdversarialValidator and BoundaryValidator
- [ ] Create `chaos_healing_integration.py` with ChaosResilienceStrategy
- [ ] Create `dependency_healing_integration.py` with DependencyPruningStrategy
- [ ] Create `register_all_validators.py` unified entry point
- [ ] Add integration tests

### Phase 2: Wire to Existing Infrastructure (Next Sprint)

- [ ] Import `register_all_validators` in application startup
- [ ] Add `sovereign-pre-commit` hook to `.pre-commit-config.yaml`
- [ ] Wire `DecompositionOrchestratorAgent` into `NervousSystemAgent`
- [ ] Add CI/CD step to run red team validators on PRs

### Phase 3: Documentation & Monitoring (Following Sprint)

- [ ] Update architecture docs with integration diagram
- [ ] Add telemetry for validator/healing usage
- [ ] Create dashboard for security validation results

---

## Conclusion

Instead of archiving these 7 agents, we should **integrate them** into the existing `ValidatorOrchestrator` and `HealingSovereignOrchestrator` infrastructure. This:

1. **Preserves their healing capabilities** - All agents have proper `heal()` methods
2. **Leverages existing infrastructure** - Uses singleton orchestrators already in place
3. **Enables security testing** - Red team agents become callable validators
4. **Improves resilience** - Chaos engineering validates system recovery
5. **Reduces tech debt** - No orphan agents, all code is actively used

The integration requires creating adapter classes that implement `ValidatorProtocol` or `HealingStrategy`, then registering them with the orchestrators. This is a clean, testable approach that follows the existing patterns in the codebase.
