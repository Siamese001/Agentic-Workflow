# API Documentation: classification

**Target Audience**: developers, api_users

# classification API Documentation

**File**: `classification.py`
**Classes**: 0
**Functions**: 6


## Functions

- **get_classification_suffix_patterns_compiled** -> dict[Pattern, str]
- **get_compound_suffix_patterns_compiled** -> list[tuple[Pattern, str, str, str]]
- **get_folder_purity_patterns_compiled** -> dict[str, list[Pattern]]
- **get_folder_purity_disallowed_compiled** -> dict[str, list[Pattern]]
- **get_forbidden_compound_patterns_compiled** -> list[Pattern]
- **get_folder_key_for_path** -> str


## Function: get_classification_suffix_patterns_compiled

**Returns**: dict[Pattern, str]
**Description**: Compile and cache classification suffix patterns.



## Function: get_compound_suffix_patterns_compiled

**Returns**: list[tuple[Pattern, str, str, str]]
**Description**: Compile and cache compound suffix conflict patterns.



## Function: get_folder_purity_patterns_compiled

**Returns**: dict[str, list[Pattern]]
**Description**: Compile and cache folder purity patterns.



## Function: get_folder_purity_disallowed_compiled

**Returns**: dict[str, list[Pattern]]
**Description**: Compile and cache folder purity disallowed patterns.



## Function: get_forbidden_compound_patterns_compiled

**Returns**: list[Pattern]
**Description**: Compile and cache forbidden compound patterns.



## Function: get_folder_key_for_path

**Parameters**: path
**Returns**: str
**Description**: 
    Get the folder purity key for a given path.

    Handles special cases:
    - config/agent_configs -> agent_configs
    - runtime/engine -> engines (via alias)
    - runtime/config -> config
    - prompt_governance -> prompt_governance
    - L*/subfolder -> subfolder
    



## Usage Examples

### Function Usage

```python
# Using get_classification_suffix_patterns_compiled
result = get_classification_suffix_patterns_compiled()
```

```python
# Using get_compound_suffix_patterns_compiled
result = get_compound_suffix_patterns_compiled()
```

```python
# Using get_folder_purity_patterns_compiled
result = get_folder_purity_patterns_compiled()
```



---
**Generated**: 2026-03-26T09:39:05.911282
**Type**: api_reference
**Quality**: comprehensive
