# API Documentation: orchestrator_engine

**Target Audience**: developers, api_users

# orchestrator_engine API Documentation

**File**: `orchestrator_engine.py`
**Classes**: 3
**Functions**: 22

## Classes

- **L3OrchestrationStrategy** (inherits from OrchestrationStrategy)
- **OrchestratorMode** (inherits from str, Enum)
- **Orchestrator** (inherits from SovereignBaseAgent)

## Functions

- **get_consolidated_orchestrator** -> Orchestrator
- **__init__** -> None
- **get_available_agents** -> list[str]
- **__init__**
- **_get_CredentialScannerAgent**
- **strategies** -> dict[str, Any]
- **dispatch** -> dict[str, Any]
- **run_mission** -> MissionResult
- **run_agent** -> AgentResult
- **_run_compliance_mode** -> AgentResult
- **_run_healing_mode** -> AgentResult
- **_run_ssot_mode** -> AgentResult
- **_run_full_mode** -> AgentResult
- **get_available_agents** -> list[str]
- **validate_mission** -> bool
- **_validate_agent_import** -> bool
- **_v15_build_operation_manifest** -> SurgicalManifest | None
- **heal_repository** -> dict[str, int]
- **_orchestrator_heal_body** -> dict[str, int]
- **heal** -> dict[str, Any]
- **_heal_body**
- **_state_hash**


## Class: L3OrchestrationStrategy

**Description**: 
    L3-specific orchestration strategy preserving original Orchestrator logic.

    FACADE PATTERN: Encapsulates the complex orchestration logic while delegating
    to the unified strategy pattern.
    

**Inherits from**: OrchestrationStrategy

### Methods

#### __init__
**Parameters**: self, config, mode
**Returns**: None
**Description**: Initialize with orchestration configuration.

#### get_available_agents
**Parameters**: self
**Returns**: list[str]
**Description**: Get list of agents this orchestrator can coordinate.



## Class: OrchestratorMode

**Description**: Orchestration modes supported by Orchestrator.

**Inherits from**: str, Enum



## Class: Orchestrator

**Description**: 
    The Central Nervous System for Agentic Workflow.

    FACADE SHELL: Delegates to UnifiedAgent with L3OrchestrationStrategy.
    SIGNATURE COMPATIBILITY: 100% preserved - no breaking changes.

    Architecture: Strategy Pattern
    - Instead of hardcoding 10+ sub-agents, we delegate to domain-specific Strategies.
    - Inherits from SovereignBaseAgent for standard logging/state management.
    - Implements IOrchestratorAgent protocol for type-safe orchestration.

    Phase 2: Supports mode-based behavior switching:
    - healing: Focus on heal_repository operations
    - compliance: Focus on compliance validation
    - ssot: Focus on SSOT enforcement
    - full: Run all operations
    - unified: Default mode (same as full)

    Phase 3: Facade pattern delegating to UnifiedAgent.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, agent_id, mode

#### _get_CredentialScannerAgent
**Description**: Lazy loader for CredentialScannerAgent (upward L3->L5 seam).

#### strategies
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Lazy-load strategies to avoid circular imports.

#### dispatch
**Parameters**: self, domain, action, payload
**Returns**: dict[str, Any]
**Description**: 
        Routes a request to the appropriate strategy.

        Args:
            domain (str): The strategy domain ('safety', 'rl').
            action (str): The method to call on the strategy.
            payload (dict): Data to pass to the strategy.
        

#### run_mission
**Parameters**: self, agents, dry_run, execute, context
**Returns**: MissionResult
**Description**: 
        Execute a mission across multiple agents.

        Implements IOrchestratorAgent.run_mission protocol.

        Args:
            agents: List of agent names to coordinate
            dry_run: If True, only simulate execution
            execute: If True, apply changes (opposite of dry_run)
            context: Optional execution context for shared state

        Returns:
            MissionResult with aggregated outcomes
        

#### run_agent
**Parameters**: self, agent_name, dry_run, context
**Returns**: AgentResult
**Description**: 
        Execute a single agent with standardized result.

        [PHASE 3: FORWARD-ROLLING RECURSION]
        Enforces linear depth limits and parameter merging for recursive healing.
        

#### _run_compliance_mode
**Parameters**: self, agent_name, dry_run, context
**Returns**: AgentResult
**Description**: 
        Execute agent in COMPLIANCE mode.

        Risk 4: Credential Detection Integration
        - Runs standard compliance checks
        - Scans for hardcoded credentials using CredentialScannerAgent
        

#### _run_healing_mode
**Parameters**: self, agent_name, dry_run, context
**Returns**: AgentResult
**Description**: Execute agent in HEALING mode - focus on heal_repository.

#### _run_ssot_mode
**Parameters**: self, agent_name, dry_run, context
**Returns**: AgentResult
**Description**: Execute agent in SSOT mode - enforce SSOT compliance.

#### _run_full_mode
**Parameters**: self, agent_name, dry_run, context
**Returns**: AgentResult
**Description**: 
        Execute agent in FULL/UNIFIED mode with Zero-Loss Context Merging.

        [HARDENING] Merges accumulated_context with retry_context to preserve 'goal' and 'dataset'.
        

#### get_available_agents
**Parameters**: self
**Returns**: list[str]
**Description**: 
        Get list of agents this orchestrator can coordinate.

        Uses ssot_discovery for file lookups (no rglob).

        Returns:
            List of agent class names
        

#### validate_mission
**Parameters**: self, agents, context
**Returns**: bool
**Description**: 
        Pre-flight validation before mission execution.

        Args:
            agents: List of agent names to validate
            context: Optional execution context

        Returns:
            True if mission can proceed, False otherwise
        

#### _validate_agent_import
**Parameters**: self, agent_name
**Returns**: bool
**Description**: 
        [PHASE 3: PERFORMANCE] Cached Pre-Flight Import Validation.

        Uses a local cache to skip redundant subprocess checks for repeat agent calls.

        Performs a subprocess check to verify the agent module is importable
        before attempting to run it. This prevents runtime crashes from
        missing dependencies, syntax errors, or circular imports.

        [ULTRA-HARDENED] Validates module path against whitelist before subprocess execution
        to prevent arbitrary code execution security vulnerabilities.

        Args:
            agent_name: Name of the agent to validate

        Returns:
            True if agent is importable, False otherwise
        

#### _v15_build_operation_manifest
**Parameters**: self, operation, target_layer
**Returns**: SurgicalManifest | None
**Description**: §8.1a — Construct SurgicalManifest for orchestrator-level operation.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        L3 Orchestration Agent - Central Nervous System Healing.

        WIRED CAPABILITIES:
        - Validates strategy configurations
        - Checks agent discovery paths
        - Verifies mission execution capabilities
        

#### _orchestrator_heal_body
**Parameters**: self, dry_run
**Returns**: dict[str, int]
**Description**: Core healing logic extracted for gateway wrapping.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by Orchestrator.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Function: get_consolidated_orchestrator

**Parameters**: project_root
**Returns**: Orchestrator
**Description**: 
    [INTEGRATION] Factory method required by execute_ssot.py.
    Instantiates the orchestrator with the hardened Unified mode and resolved root.
    



## Function: __init__

**Parameters**: self, config, mode
**Returns**: None
**Description**: Initialize with orchestration configuration.



## Function: get_available_agents

**Parameters**: self
**Returns**: list[str]
**Description**: Get list of agents this orchestrator can coordinate.



## Function: __init__

**Parameters**: self, agent_id, mode


## Function: _get_CredentialScannerAgent

**Description**: Lazy loader for CredentialScannerAgent (upward L3->L5 seam).



## Function: strategies

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Lazy-load strategies to avoid circular imports.



## Function: dispatch

**Parameters**: self, domain, action, payload
**Returns**: dict[str, Any]
**Description**: 
        Routes a request to the appropriate strategy.

        Args:
            domain (str): The strategy domain ('safety', 'rl').
            action (str): The method to call on the strategy.
            payload (dict): Data to pass to the strategy.
        



## Function: run_mission

**Parameters**: self, agents, dry_run, execute, context
**Returns**: MissionResult
**Description**: 
        Execute a mission across multiple agents.

        Implements IOrchestratorAgent.run_mission protocol.

        Args:
            agents: List of agent names to coordinate
            dry_run: If True, only simulate execution
            execute: If True, apply changes (opposite of dry_run)
            context: Optional execution context for shared state

        Returns:
            MissionResult with aggregated outcomes
        



## Function: run_agent

**Parameters**: self, agent_name, dry_run, context
**Returns**: AgentResult
**Description**: 
        Execute a single agent with standardized result.

        [PHASE 3: FORWARD-ROLLING RECURSION]
        Enforces linear depth limits and parameter merging for recursive healing.
        



## Function: _run_compliance_mode

**Parameters**: self, agent_name, dry_run, context
**Returns**: AgentResult
**Description**: 
        Execute agent in COMPLIANCE mode.

        Risk 4: Credential Detection Integration
        - Runs standard compliance checks
        - Scans for hardcoded credentials using CredentialScannerAgent
        



## Function: _run_healing_mode

**Parameters**: self, agent_name, dry_run, context
**Returns**: AgentResult
**Description**: Execute agent in HEALING mode - focus on heal_repository.



## Function: _run_ssot_mode

**Parameters**: self, agent_name, dry_run, context
**Returns**: AgentResult
**Description**: Execute agent in SSOT mode - enforce SSOT compliance.



## Function: _run_full_mode

**Parameters**: self, agent_name, dry_run, context
**Returns**: AgentResult
**Description**: 
        Execute agent in FULL/UNIFIED mode with Zero-Loss Context Merging.

        [HARDENING] Merges accumulated_context with retry_context to preserve 'goal' and 'dataset'.
        



## Function: get_available_agents

**Parameters**: self
**Returns**: list[str]
**Description**: 
        Get list of agents this orchestrator can coordinate.

        Uses ssot_discovery for file lookups (no rglob).

        Returns:
            List of agent class names
        



## Function: validate_mission

**Parameters**: self, agents, context
**Returns**: bool
**Description**: 
        Pre-flight validation before mission execution.

        Args:
            agents: List of agent names to validate
            context: Optional execution context

        Returns:
            True if mission can proceed, False otherwise
        



## Function: _validate_agent_import

**Parameters**: self, agent_name
**Returns**: bool
**Description**: 
        [PHASE 3: PERFORMANCE] Cached Pre-Flight Import Validation.

        Uses a local cache to skip redundant subprocess checks for repeat agent calls.

        Performs a subprocess check to verify the agent module is importable
        before attempting to run it. This prevents runtime crashes from
        missing dependencies, syntax errors, or circular imports.

        [ULTRA-HARDENED] Validates module path against whitelist before subprocess execution
        to prevent arbitrary code execution security vulnerabilities.

        Args:
            agent_name: Name of the agent to validate

        Returns:
            True if agent is importable, False otherwise
        



## Function: _v15_build_operation_manifest

**Parameters**: self, operation, target_layer
**Returns**: SurgicalManifest | None
**Description**: §8.1a — Construct SurgicalManifest for orchestrator-level operation.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: 
        L3 Orchestration Agent - Central Nervous System Healing.

        WIRED CAPABILITIES:
        - Validates strategy configurations
        - Checks agent discovery paths
        - Verifies mission execution capabilities
        



## Function: _orchestrator_heal_body

**Parameters**: self, dry_run
**Returns**: dict[str, int]
**Description**: Core healing logic extracted for gateway wrapping.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by Orchestrator.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Function: _heal_body

**Parameters**: m


## Function: _state_hash



## Usage Examples

### Class Usage

```python
# Using L3OrchestrationStrategy
l3orchestrationstrategy = L3OrchestrationStrategy()
l3orchestrationstrategy.get_available_agents()
```

```python
# Using OrchestratorMode
orchestratormode = OrchestratorMode()
```

```python
# Using Orchestrator
orchestrator = Orchestrator()
orchestrator.strategies()
orchestrator.dispatch()
```

### Function Usage

```python
# Using get_consolidated_orchestrator
result = get_consolidated_orchestrator(project_root)
```

```python
# Using __init__
result = __init__(config, mode)
```

```python
# Using get_available_agents
result = get_available_agents()
```



---
**Generated**: 2026-03-26T09:39:04.184429
**Type**: api_reference
**Quality**: comprehensive
