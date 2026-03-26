# API Documentation: unified_cst_healer_util

**Target Audience**: developers, api_users

# unified_cst_healer_util API Documentation

**File**: `unified_cst_healer_util.py`
**Classes**: 3
**Functions**: 5

## Classes

- **HealingConfig**
- **HealingResult**
- **UnifiedCSTHealer**

## Functions

- **__init__**
- **heal_file** -> HealingResult
- **heal_files** -> HealingResult
- **_detect_violations** -> list[ViolationConstraint]
- **_apply_transformers** -> dict[str, Any]


## Class: HealingConfig

**Description**: Configuration for unified healing operations.



## Class: HealingResult

**Description**: Result of a healing operation.



## Class: UnifiedCSTHealer

**Description**: 
    Unified entry point for all CST-based healing operations.

    Provides orchestration of multiple transformers with proper
    ordering and conflict resolution.
    

### Methods

#### __init__
**Parameters**: self, config, context_manager
**Description**: 
        Initialize the unified healer.

        Args:
            config: Healing configuration (uses defaults if not provided)
            context_manager: Optional L4ContextManager for verification gate
        

#### heal_file
**Parameters**: self, file_path, violations
**Returns**: HealingResult
**Description**: 
        Heal a single file using all enabled transformers.

        Args:
            file_path: Path to the file to heal
            violations: Optional list of specific violations to fix

        Returns:
            HealingResult with details of the operation
        

#### heal_files
**Parameters**: self, file_paths, violations_map
**Returns**: HealingResult
**Description**: 
        Heal multiple files.

        Args:
            file_paths: List of file paths to heal
            violations_map: Optional mapping of paths to violations

        Returns:
            Aggregated HealingResult
        

#### _detect_violations
**Parameters**: self, content, file_path
**Returns**: list[ViolationConstraint]
**Description**: 
        Auto-detect violations in the content.

        Args:
            content: File content
            file_path: Path to the file

        Returns:
            List of detected violations
        

#### _apply_transformers
**Parameters**: self, context
**Returns**: dict[str, Any]
**Description**: 
        Apply all enabled transformers in the correct order.

        Args:
            context: Surgical context with violations

        Returns:
            Dict with healing results
        



## Function: __init__

**Parameters**: self, config, context_manager
**Description**: 
        Initialize the unified healer.

        Args:
            config: Healing configuration (uses defaults if not provided)
            context_manager: Optional L4ContextManager for verification gate
        



## Function: heal_file

**Parameters**: self, file_path, violations
**Returns**: HealingResult
**Description**: 
        Heal a single file using all enabled transformers.

        Args:
            file_path: Path to the file to heal
            violations: Optional list of specific violations to fix

        Returns:
            HealingResult with details of the operation
        



## Function: heal_files

**Parameters**: self, file_paths, violations_map
**Returns**: HealingResult
**Description**: 
        Heal multiple files.

        Args:
            file_paths: List of file paths to heal
            violations_map: Optional mapping of paths to violations

        Returns:
            Aggregated HealingResult
        



## Function: _detect_violations

**Parameters**: self, content, file_path
**Returns**: list[ViolationConstraint]
**Description**: 
        Auto-detect violations in the content.

        Args:
            content: File content
            file_path: Path to the file

        Returns:
            List of detected violations
        



## Function: _apply_transformers

**Parameters**: self, context
**Returns**: dict[str, Any]
**Description**: 
        Apply all enabled transformers in the correct order.

        Args:
            context: Surgical context with violations

        Returns:
            Dict with healing results
        



## Usage Examples

### Class Usage

```python
# Using HealingConfig
healingconfig = HealingConfig()
```

```python
# Using HealingResult
healingresult = HealingResult()
```

```python
# Using UnifiedCSTHealer
unifiedcsthealer = UnifiedCSTHealer()
unifiedcsthealer.heal_file()
unifiedcsthealer.heal_files()
```

### Function Usage

```python
# Using __init__
result = __init__(config, context_manager)
```

```python
# Using heal_file
result = heal_file(file_path, violations)
```

```python
# Using heal_files
result = heal_files(file_paths, violations_map)
```



---
**Generated**: 2026-03-26T09:39:05.702339
**Type**: api_reference
**Quality**: comprehensive
