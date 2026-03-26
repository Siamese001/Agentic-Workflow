# API Documentation: territory_ssot_definitions_util

**Target Audience**: developers, api_users

# territory_ssot_definitions_util API Documentation

**File**: `territory_ssot_definitions_util.py`
**Classes**: 0
**Functions**: 11


## Functions

- **get_base_agent_territory** -> str
- **get_territory_from_path** -> str
- **get_territory_sort_key** -> int
- **refine_territory_by_ast** -> str
- **_categorize_l3_orchestration** -> str
- **_categorize_apps_lic** -> str
- **_categorize_l2_execution** -> str
- **_categorize_l5_guardrails** -> str
- **_categorize_l1_cognition** -> str
- **_categorize_apps_rg** -> str
- **_categorize_l5_validators** -> str


## Function: get_base_agent_territory

**Parameters**: layer
**Returns**: str
**Description**: 
    Get the canonical territory name for a base agent in a given layer.

    Args:
        layer: Layer name (e.g., 'L0', 'L1', 'Base')

    Returns:
        Canonical territory name for the base agent
    



## Function: get_territory_from_path

**Parameters**: layer, path_str, is_base_class, class_name
**Returns**: str
**Description**: 
    Determine the canonical territory name based on layer, path, and class type.

    Args:
        layer: Layer name (e.g., 'L0', 'L1', 'Base')
        path_str: Lowercase path string (e.g., 'agentic_core/l5_safety/validators')
        is_base_class: Whether this is a base agent class
        class_name: Name of the class (optional, for special cases)

    Returns:
        Canonical territory name
    



## Function: get_territory_sort_key

**Parameters**: territory
**Returns**: int
**Description**: 
    Get the sort key for a territory (for canonical ordering).

    Args:
        territory: Territory name

    Returns:
        Sort key (lower = earlier in list)
    



## Function: refine_territory_by_ast

**Parameters**: territory, class_name, docstring, path_str
**Returns**: str
**Description**: 
    Refine high-count territories into sub-territories using AST analysis.

    This function subdivides territories with >15 agents into semantically
    meaningful sub-territories based on class name patterns, docstring keywords,
    and directory structure.

    Args:
        territory: Current territory from get_territory_from_path()
        class_name: Agent class name
        docstring: Class docstring (first line or full)
        path_str: Normalized path string (lowercase, forward slashes)

    Returns:
        Refined territory name or original if no subdivision needed
    



## Function: _categorize_l3_orchestration

**Parameters**: class_name, docstring, path_str
**Returns**: str
**Description**: Categorize L3 Orchestration/Core agents into 5 sub-territories.



## Function: _categorize_apps_lic

**Parameters**: class_name, docstring, path_str
**Returns**: str
**Description**: Categorize Apps Lic agents into 5 sub-territories.



## Function: _categorize_l2_execution

**Parameters**: class_name, docstring, path_str
**Returns**: str
**Description**: Categorize L2 Execution/Core agents into 3 sub-territories.



## Function: _categorize_l5_guardrails

**Parameters**: class_name, docstring, path_str
**Returns**: str
**Description**: Categorize L5 Safety/Guardrails agents into 3 sub-territories.



## Function: _categorize_l1_cognition

**Parameters**: class_name, docstring, path_str
**Returns**: str
**Description**: Categorize L1 Cognition/Core agents into 4 sub-territories.



## Function: _categorize_apps_rg

**Parameters**: class_name, docstring, path_str
**Returns**: str
**Description**: Categorize Apps Rg agents into 3 sub-territories.



## Function: _categorize_l5_validators

**Parameters**: class_name, docstring, path_str
**Returns**: str
**Description**: Categorize L5 Safety/Validators agents into 2 sub-territories.



## Usage Examples

### Function Usage

```python
# Using get_base_agent_territory
result = get_base_agent_territory(layer)
```

```python
# Using get_territory_from_path
result = get_territory_from_path(layer, path_str)
```

```python
# Using get_territory_sort_key
result = get_territory_sort_key(territory)
```



---
**Generated**: 2026-03-26T09:39:03.278727
**Type**: api_reference
**Quality**: comprehensive
