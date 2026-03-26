# API Documentation: UnifiedAgent

**Target Audience**: developers, api_users

# UnifiedAgent API Documentation

**File**: `UnifiedAgent.py`
**Classes**: 14
**Functions**: 33

## Classes

- **AgentCategory** (inherits from Enum)
- **ValidationResult**
- **OrchestrationResult**
- **HealingResult**
- **BaseStrategy** (inherits from ABC)
- **ValidatorStrategy** (inherits from BaseStrategy)
- **OrchestrationStrategy** (inherits from BaseStrategy)
- **HealingStrategy** (inherits from BaseStrategy)
- **GenericStrategy** (inherits from BaseStrategy)
- **LocationHealingStrategy** (inherits from HealingStrategy)
- **StructuralValidatorStrategy** (inherits from ValidatorStrategy)
- **CodeValidatorStrategy** (inherits from ValidatorStrategy)
- **StructureHealingStrategy** (inherits from HealingStrategy)
- **UnifiedAgent** (inherits from SovereignBaseAgent)

## Functions

- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]
- **__init__** -> None
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **_to_string** -> str
- **__init__** -> None
- **_get_target_data** -> Any | None
- **_apply_validation_rule** -> dict[str, Any]
- **_calculate_keyword_score** -> float
- **__init__** -> None
- **_determine_next_actions** -> list[str]
- **__init__** -> None
- **_scan_violations** -> list[dict[str, Any]]
- **_attempt_fix** -> dict[str, Any]
- **heal_repository** -> dict[str, int]
- **__init__** -> None
- **heal_repository** -> dict[str, Any]
- **__init__** -> None
- **__init__** -> None
- **__init__** -> None
- **heal_repository** -> dict[str, Any]
- **__post_init__** -> None
- **_load_unified_config** -> dict[str, Any]
- **_create_strategy** -> BaseStrategy
- **_get_trace_id** -> str
- **execute_sync** -> ValidationResult | OrchestrationResult | HealingResult | dict[str, Any]
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]
- **get_category** -> AgentCategory
- **get_strategy** -> BaseStrategy
- **get_config** -> dict[str, Any]


## Class: AgentCategory

**Description**: Unified agent category classification.

**Inherits from**: Enum



## Class: ValidationResult

**Description**: Standardized validation result across all validator agents.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Class: OrchestrationResult

**Description**: Standardized orchestration result across all orchestrator agents.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Class: HealingResult

**Description**: Standardized healing result across all healer agents.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Class: BaseStrategy

**Description**: Base strategy for unified agent implementations.

**Inherits from**: ABC

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize strategy with configuration.

#### heal_repository
**Parameters**: self, agent, dry_run, execute
**Returns**: dict[str, int]
**Description**: Base healing implementation.

#### heal
**Parameters**: self, agent, violation
**Returns**: dict[str, Any]
**Description**: Base violation healing.

#### _to_string
**Parameters**: self, content
**Returns**: str
**Description**: Convert content to string for analysis.



## Class: ValidatorStrategy

**Description**: Strategy for validator agents.

**Inherits from**: BaseStrategy

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize validator strategy with configuration.

#### _get_target_data
**Parameters**: self, agent
**Returns**: Any | None
**Description**: Extract target data from agent context.

#### _apply_validation_rule
**Parameters**: self, data, rule_name, rule_config
**Returns**: dict[str, Any]
**Description**: Apply a single validation rule.

#### _calculate_keyword_score
**Parameters**: self, data, reference
**Returns**: float
**Description**: Calculate keyword match score between data and reference.



## Class: OrchestrationStrategy

**Description**: Strategy for orchestrator agents.

**Inherits from**: BaseStrategy

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize orchestration strategy with configuration.

#### _determine_next_actions
**Parameters**: self, completed_steps, signals
**Returns**: list[str]
**Description**: Determine next actions based on completed steps and signals.



## Class: HealingStrategy

**Description**: Strategy for healer agents.

**Inherits from**: BaseStrategy

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize healing strategy with configuration.

#### _scan_violations
**Parameters**: self, agent
**Returns**: list[dict[str, Any]]
**Description**: Scan for violations in the repository.

#### _attempt_fix
**Parameters**: self, agent, violation
**Returns**: dict[str, Any]
**Description**: Attempt to fix a violation.

#### heal_repository
**Parameters**: self, agent, dry_run, execute
**Returns**: dict[str, int]
**Description**: Heal repository violations.



## Class: GenericStrategy

**Description**: Strategy for generic agents.

**Inherits from**: BaseStrategy



## Class: LocationHealingStrategy

**Description**: 
    Location-specific healing strategy for file moves, deletions, and import fixing.

    FACADE PATTERN: Encapsulates the LocationHealerAgent logic while delegating
    to the unified strategy pattern.

    Handles:
    - Safe file moves with collision handling
    - Safe file deletions with backup
    - Backup directory management
    - Import path fixing after moves
    - Post-heal validation
    - Archive operations
    

**Inherits from**: HealingStrategy

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize with location healing configuration.

#### heal_repository
**Parameters**: self, agent, dry_run, execute
**Returns**: dict[str, Any]
**Description**: Heal repository location violations.



## Class: StructuralValidatorStrategy

**Description**: 
    Structural validation strategy for gravity, hierarchy, naming, and documentation.

    FACADE PATTERN: Encapsulates the StructuralValidatorAgent logic while delegating
    to the unified strategy pattern.

    Handles:
    - Layer gravity enforcement (L0-L6)
    - Hierarchy compliance validation
    - Naming convention enforcement
    - Documentation validation
    

**Inherits from**: ValidatorStrategy

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize with structural validation configuration.



## Class: CodeValidatorStrategy

**Description**: 
    Code-specific validation strategy for syntax, canon, async, and print validation.

    FACADE PATTERN: Encapsulates the CodeValidatorAgent logic while delegating
    to the unified strategy pattern.

    Handles:
    - Syntax error detection
    - Canonical pattern compliance
    - Async/await usage validation
    - Print statement policy enforcement
    

**Inherits from**: ValidatorStrategy

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize with code validation configuration.



## Class: StructureHealingStrategy

**Description**: 
    Structure-specific healing strategy for gravity, hierarchy, naming, and territory.

    FACADE PATTERN: Encapsulates the StructureHealerAgent logic while delegating
    to the unified strategy pattern.

    Handles:
    - Gravity violation healing (layer import rules)
    - Hierarchy compliance healing
    - Naming convention enforcement
    - Territory/location healing
    - Blueprint compliance healing
    

**Inherits from**: HealingStrategy

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None
**Description**: Initialize with structure healing configuration.

#### heal_repository
**Parameters**: self, agent, dry_run, execute
**Returns**: dict[str, Any]
**Description**: Heal repository structure violations.



## Class: UnifiedAgent

**Description**: 
    Unified consolidation core for 85% of agent redundancy.

    Provides standardized implementations while preserving domain-specific
    customization through configuration and strategy pattern.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None
**Description**: Initialize unified agent with category and configuration.

#### _load_unified_config
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Load configuration for the unified agent.

#### _create_strategy
**Parameters**: self
**Returns**: BaseStrategy
**Description**: Create strategy based on category.

#### _get_trace_id
**Parameters**: self
**Returns**: str
**Description**: Return the active trace_id or generate a fresh UUID.

#### execute_sync
**Parameters**: self
**Returns**: ValidationResult | OrchestrationResult | HealingResult | dict[str, Any]
**Description**: Synchronous wrapper for execute.

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, int]
**Description**: Unified healing implementation.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: Unified violation healing.

#### get_category
**Parameters**: self
**Returns**: AgentCategory
**Description**: Get the agent's category.

#### get_strategy
**Parameters**: self
**Returns**: BaseStrategy
**Description**: Get the agent's strategy.

#### get_config
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get the agent's configuration.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize strategy with configuration.



## Function: heal_repository

**Parameters**: self, agent, dry_run, execute
**Returns**: dict[str, int]
**Description**: Base healing implementation.



## Function: heal

**Parameters**: self, agent, violation
**Returns**: dict[str, Any]
**Description**: Base violation healing.



## Function: _to_string

**Parameters**: self, content
**Returns**: str
**Description**: Convert content to string for analysis.



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize validator strategy with configuration.



## Function: _get_target_data

**Parameters**: self, agent
**Returns**: Any | None
**Description**: Extract target data from agent context.



## Function: _apply_validation_rule

**Parameters**: self, data, rule_name, rule_config
**Returns**: dict[str, Any]
**Description**: Apply a single validation rule.



## Function: _calculate_keyword_score

**Parameters**: self, data, reference
**Returns**: float
**Description**: Calculate keyword match score between data and reference.



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize orchestration strategy with configuration.



## Function: _determine_next_actions

**Parameters**: self, completed_steps, signals
**Returns**: list[str]
**Description**: Determine next actions based on completed steps and signals.



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize healing strategy with configuration.



## Function: _scan_violations

**Parameters**: self, agent
**Returns**: list[dict[str, Any]]
**Description**: Scan for violations in the repository.



## Function: _attempt_fix

**Parameters**: self, agent, violation
**Returns**: dict[str, Any]
**Description**: Attempt to fix a violation.



## Function: heal_repository

**Parameters**: self, agent, dry_run, execute
**Returns**: dict[str, int]
**Description**: Heal repository violations.



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize with location healing configuration.



## Function: heal_repository

**Parameters**: self, agent, dry_run, execute
**Returns**: dict[str, Any]
**Description**: Heal repository location violations.



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize with structural validation configuration.



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize with code validation configuration.



## Function: __init__

**Parameters**: self, config
**Returns**: None
**Description**: Initialize with structure healing configuration.



## Function: heal_repository

**Parameters**: self, agent, dry_run, execute
**Returns**: dict[str, Any]
**Description**: Heal repository structure violations.



## Function: __post_init__

**Parameters**: self
**Returns**: None
**Description**: Initialize unified agent with category and configuration.



## Function: _load_unified_config

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Load configuration for the unified agent.



## Function: _create_strategy

**Parameters**: self
**Returns**: BaseStrategy
**Description**: Create strategy based on category.



## Function: _get_trace_id

**Parameters**: self
**Returns**: str
**Description**: Return the active trace_id or generate a fresh UUID.



## Function: execute_sync

**Parameters**: self
**Returns**: ValidationResult | OrchestrationResult | HealingResult | dict[str, Any]
**Description**: Synchronous wrapper for execute.



## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, int]
**Description**: Unified healing implementation.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: Unified violation healing.



## Function: get_category

**Parameters**: self
**Returns**: AgentCategory
**Description**: Get the agent's category.



## Function: get_strategy

**Parameters**: self
**Returns**: BaseStrategy
**Description**: Get the agent's strategy.



## Function: get_config

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get the agent's configuration.



## Usage Examples

### Class Usage

```python
# Using AgentCategory
agentcategory = AgentCategory()
```

```python
# Using ValidationResult
validationresult = ValidationResult()
validationresult.to_dict()
```

```python
# Using OrchestrationResult
orchestrationresult = OrchestrationResult()
orchestrationresult.to_dict()
```

### Function Usage

```python
# Using to_dict
result = to_dict()
```

```python
# Using to_dict
result = to_dict()
```

```python
# Using to_dict
result = to_dict()
```



---
**Generated**: 2026-03-26T09:39:04.328726
**Type**: api_reference
**Quality**: comprehensive
