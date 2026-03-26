# API Documentation: ResourceManagerAgent

**Target Audience**: developers, api_users

# ResourceManagerAgent API Documentation

**File**: `ResourceManagerAgent.py`
**Classes**: 6
**Functions**: 17

## Classes

- **ResourceType** (inherits from Enum)
- **AllocationStatus** (inherits from Enum)
- **ResourceAllocation**
- **ResourceBudget**
- **ResourceConfig**
- **ResourceManagerAgent** (inherits from SovereignBaseAgent)

## Functions

- **create_legacy_budget_manager** -> ResourceManagerAgent
- **create_legacy_proactive_manager** -> ResourceManagerAgent
- **create_legacy_fallback_manager** -> ResourceManagerAgent
- **available** -> float
- **utilization** -> float
- **is_exhausted** -> bool
- **heal_repository** -> dict[str, Any]
- **__init__**
- **set_budget** -> None
- **allocate** -> ResourceAllocation
- **_apply_fallback** -> ResourceAllocation
- **release** -> bool
- **is_exhausted** -> bool
- **get_utilization** -> float
- **get_budget_status** -> dict[str, Any]
- **get_all_budgets** -> dict[str, dict[str, Any]]
- **heal** -> dict


## Class: ResourceType

**Description**: Types of resources managed.

**Inherits from**: Enum



## Class: AllocationStatus

**Description**: Status of resource allocation.

**Inherits from**: Enum



## Class: ResourceAllocation

**Description**: Represents a resource allocation.



## Class: ResourceBudget

**Description**: Budget configuration for a resource type.

### Methods

#### available
**Parameters**: self
**Returns**: float

#### utilization
**Parameters**: self
**Returns**: float

#### is_exhausted
**Parameters**: self
**Returns**: bool



## Class: ResourceConfig

**Description**: configuration for resource management.



## Class: ResourceManagerAgent

**Description**: 
    Thread-safe unified resource manager.

    Consolidates:
    - BudgetManagerAgent (budget tracking)
    - ProactiveResourceManagerAgent (proactive allocation)
    - FallbackManagerAgent (fallback strategies)

    Usage:
        manager = ResourceManagerAgent()

        # Set budget
        manager.set_budget(ResourceType.BUDGET, total=1000.0)

        # Request allocation
        result = manager.allocate("agent_1", ResourceType.BUDGET, 100.0)

        # Check if exhausted
        if manager.is_exhausted(ResourceType.BUDGET):
            print("Budget exhausted!")
    

**Inherits from**: SovereignBaseAgent

### Methods

#### heal_repository
**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        

#### __init__
**Parameters**: self, agent_config

#### set_budget
**Parameters**: self, resource_type, total, hard_cap, warning_threshold
**Returns**: None
**Description**: Set budget for a resource type.

#### allocate
**Parameters**: self, agent_id, resource_type, amount, priority
**Returns**: ResourceAllocation
**Description**: 
        Allocate resources to an agent.

        Thread-safe allocation with hard cap enforcement.

        Args:
            agent_id: Requesting agent identifier
            resource_type: Type of resource to allocate
            amount: Amount to allocate
            priority: Priority level (higher = more important)

        Returns:
            ResourceAllocation with status
        

#### _apply_fallback
**Parameters**: self, agent_id, resource_type, amount, priority
**Returns**: ResourceAllocation
**Description**: Apply fallback strategies when allocation fails.

#### release
**Parameters**: self, agent_id, resource_type, amount
**Returns**: bool
**Description**: Release allocated resources.

#### is_exhausted
**Parameters**: self, resource_type
**Returns**: bool
**Description**: Check if a resource type is exhausted.

#### get_utilization
**Parameters**: self, resource_type
**Returns**: float
**Description**: Get current utilization for a resource type.

#### get_budget_status
**Parameters**: self, resource_type
**Returns**: dict[str, Any]
**Description**: Get detailed budget status.

#### get_all_budgets
**Parameters**: self
**Returns**: dict[str, dict[str, Any]]
**Description**: Get status of all budgets.

#### heal
**Parameters**: self, violation
**Returns**: dict
**Description**: Heal resource management violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (budget, memory, cpu, tokens)
                - resource_type: ResourceType enum value
                - agent_id: Agent that caused the violation

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Function: create_legacy_budget_manager

**Returns**: ResourceManagerAgent
**Description**: Create a resource manager configured for budget management.



## Function: create_legacy_proactive_manager

**Returns**: ResourceManagerAgent
**Description**: Create a resource manager with proactive allocation enabled.



## Function: create_legacy_fallback_manager

**Returns**: ResourceManagerAgent
**Description**: Create a resource manager with fallback strategies.



## Function: available

**Parameters**: self
**Returns**: float


## Function: utilization

**Parameters**: self
**Returns**: float


## Function: is_exhausted

**Parameters**: self
**Returns**: bool


## Function: heal_repository

**Parameters**: self, dry_run, execute
**Returns**: dict[str, Any]
**Description**: 
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        



## Function: __init__

**Parameters**: self, agent_config


## Function: set_budget

**Parameters**: self, resource_type, total, hard_cap, warning_threshold
**Returns**: None
**Description**: Set budget for a resource type.



## Function: allocate

**Parameters**: self, agent_id, resource_type, amount, priority
**Returns**: ResourceAllocation
**Description**: 
        Allocate resources to an agent.

        Thread-safe allocation with hard cap enforcement.

        Args:
            agent_id: Requesting agent identifier
            resource_type: Type of resource to allocate
            amount: Amount to allocate
            priority: Priority level (higher = more important)

        Returns:
            ResourceAllocation with status
        



## Function: _apply_fallback

**Parameters**: self, agent_id, resource_type, amount, priority
**Returns**: ResourceAllocation
**Description**: Apply fallback strategies when allocation fails.



## Function: release

**Parameters**: self, agent_id, resource_type, amount
**Returns**: bool
**Description**: Release allocated resources.



## Function: is_exhausted

**Parameters**: self, resource_type
**Returns**: bool
**Description**: Check if a resource type is exhausted.



## Function: get_utilization

**Parameters**: self, resource_type
**Returns**: float
**Description**: Get current utilization for a resource type.



## Function: get_budget_status

**Parameters**: self, resource_type
**Returns**: dict[str, Any]
**Description**: Get detailed budget status.



## Function: get_all_budgets

**Parameters**: self
**Returns**: dict[str, dict[str, Any]]
**Description**: Get status of all budgets.



## Function: heal

**Parameters**: self, violation
**Returns**: dict
**Description**: Heal resource management violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (budget, memory, cpu, tokens)
                - resource_type: ResourceType enum value
                - agent_id: Agent that caused the violation

        Returns:
            Dictionary with healing results following standard_heal format.
        



## Usage Examples

### Class Usage

```python
# Using ResourceType
resourcetype = ResourceType()
```

```python
# Using AllocationStatus
allocationstatus = AllocationStatus()
```

```python
# Using ResourceAllocation
resourceallocation = ResourceAllocation()
```

### Function Usage

```python
# Using create_legacy_budget_manager
result = create_legacy_budget_manager()
```

```python
# Using create_legacy_proactive_manager
result = create_legacy_proactive_manager()
```

```python
# Using create_legacy_fallback_manager
result = create_legacy_fallback_manager()
```



---
**Generated**: 2026-03-26T09:39:05.373058
**Type**: api_reference
**Quality**: comprehensive
