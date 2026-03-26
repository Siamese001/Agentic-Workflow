# API Documentation: validation_orchestrator

**Target Audience**: developers, api_users

# validation_orchestrator API Documentation

**File**: `validation_orchestrator.py`
**Classes**: 1
**Functions**: 15

## Classes

- **ValidationOrchestrator** (inherits from SovereignBaseAgent)

## Functions

- **_load_activation_gate** -> Any
- **_get_file_io** -> Any
- **_init_registry** -> None
- **__init__** -> None
- **can_run** -> bool
- **get_file_hash** -> str
- **check_cache** -> dict[str, Any] | None
- **store_cache** -> None
- **_get_violation_details** -> str
- **_get_reference_fix** -> str | None
- **_build_task** -> str
- **_record_success** -> None
- **execute** -> None
- **heal_repository** -> dict[str, int]
- **heal** -> dict[str, Any]


## Class: ValidationOrchestrator

**Description**: 
    Validation orchestrator for Canon validation agents.

    Provides shared infrastructure for validation including:
        - Verification registry with check functions for all Canon keys.
        - File hashing for cache invalidation.
        - Redis caching for validation results.
        - LLM-based smart fix capabilities with retry logic.

    Class Attributes:
        VERIFICATION_REGISTRY: Dict mapping Canon keys to check functions.
        _registry_built: Flag indicating if registry has been initialized.

    Instance Attributes:
        ctx: ValidationContext for file access and reporting.
        name: Agent name for logging and reporting.
        layer: Optional layer identifier.
    

**Inherits from**: SovereignBaseAgent

### Methods

#### _init_registry
**Parameters**: cls, ctx
**Returns**: None
**Description**: 
        Build the verification registry once.

        Initializes VERIFICATION_REGISTRY with check functions for all Canon keys.
        Uses dynamic import for L2 StructuralEngineerAgent to avoid gravity violation.

        Args:
            ctx: ValidationContext for agent initialization.
        

#### __init__
**Parameters**: self, context, name, layer
**Returns**: None
**Description**: 
        Initialize the Canon base agent.

        Args:
            context: ValidationContext for file access and reporting.
            name: Agent name (defaults to class name).
            layer: Optional layer identifier for logging.
        

#### can_run
**Parameters**: self
**Returns**: bool
**Description**: 
        Check if agent can run.

        Returns:
            True unless CRITICAL_FAIL signal is present in context.
        

#### get_file_hash
**Parameters**: self, file_path
**Returns**: str
**Description**: 
        Calculate SHA-256 hash of a file.

        Args:
            file_path: Path to file to hash.

        Returns:
            Hex digest of SHA-256 hash, or empty string on error.
        

#### check_cache
**Parameters**: self, file_path, key
**Returns**: dict[str, Any] | None
**Description**: 
        Check Redis cache for validation result.

        Args:
            file_path: Path to file being validated.
            key: Canon key number.

        Returns:
            Cached result dict or None if not cached.
        

#### store_cache
**Parameters**: self, file_path, key, result
**Returns**: None
**Description**: 
        Store validation result in Redis cache.

        Args:
            file_path: Path to file being validated.
            key: Canon key number.
            result: Validation result to cache.
        

#### _get_violation_details
**Parameters**: self, res, file_path
**Returns**: str
**Description**: Extract violation details relevant to a specific file.

#### _get_reference_fix
**Parameters**: self, violation_desc
**Returns**: str | None
**Description**: Find similar patterns and return reference fix if available.

#### _build_task
**Parameters**: self, violation_key, file_path, details, ref_fix
**Returns**: str
**Description**: Build the task description for LLM healing.

#### _record_success
**Parameters**: self, file_path, violation_key, violation_desc, fixed_code
**Returns**: None
**Description**: Record a successful healing attempt.

#### execute
**Parameters**: self
**Returns**: None
**Description**: 
        Execute validation checks.
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Validate Canon keys and run registered verification checks.

        Iterates through the VERIFICATION_REGISTRY and runs all registered
        checks for Canon validation. Can apply smart fixes when execute=True.

        Args:
            dry_run: If True, only report violations without fixing.
            execute: If True, apply fixes using smart_fix.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum allowed recursion depth.
            _call_path: Set of agent names already in call chain.

        Returns:
            Dict with violations_found, violations_fixed, errors, skipped.
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by CanonBaseAgent.

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
        



## Function: _load_activation_gate

**Returns**: Any
**Description**: Load L5 activation gate via approved L0 seam (no static L2→L5 import).



## Function: _get_file_io

**Returns**: Any
**Description**: Return a FileIo instance for direct L2.2 writes.



## Function: _init_registry

**Parameters**: cls, ctx
**Returns**: None
**Description**: 
        Build the verification registry once.

        Initializes VERIFICATION_REGISTRY with check functions for all Canon keys.
        Uses dynamic import for L2 StructuralEngineerAgent to avoid gravity violation.

        Args:
            ctx: ValidationContext for agent initialization.
        



## Function: __init__

**Parameters**: self, context, name, layer
**Returns**: None
**Description**: 
        Initialize the Canon base agent.

        Args:
            context: ValidationContext for file access and reporting.
            name: Agent name (defaults to class name).
            layer: Optional layer identifier for logging.
        



## Function: can_run

**Parameters**: self
**Returns**: bool
**Description**: 
        Check if agent can run.

        Returns:
            True unless CRITICAL_FAIL signal is present in context.
        



## Function: get_file_hash

**Parameters**: self, file_path
**Returns**: str
**Description**: 
        Calculate SHA-256 hash of a file.

        Args:
            file_path: Path to file to hash.

        Returns:
            Hex digest of SHA-256 hash, or empty string on error.
        



## Function: check_cache

**Parameters**: self, file_path, key
**Returns**: dict[str, Any] | None
**Description**: 
        Check Redis cache for validation result.

        Args:
            file_path: Path to file being validated.
            key: Canon key number.

        Returns:
            Cached result dict or None if not cached.
        



## Function: store_cache

**Parameters**: self, file_path, key, result
**Returns**: None
**Description**: 
        Store validation result in Redis cache.

        Args:
            file_path: Path to file being validated.
            key: Canon key number.
            result: Validation result to cache.
        



## Function: _get_violation_details

**Parameters**: self, res, file_path
**Returns**: str
**Description**: Extract violation details relevant to a specific file.



## Function: _get_reference_fix

**Parameters**: self, violation_desc
**Returns**: str | None
**Description**: Find similar patterns and return reference fix if available.



## Function: _build_task

**Parameters**: self, violation_key, file_path, details, ref_fix
**Returns**: str
**Description**: Build the task description for LLM healing.



## Function: _record_success

**Parameters**: self, file_path, violation_key, violation_desc, fixed_code
**Returns**: None
**Description**: Record a successful healing attempt.



## Function: execute

**Parameters**: self
**Returns**: None
**Description**: 
        Execute validation checks.
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: Validate Canon keys and run registered verification checks.

        Iterates through the VERIFICATION_REGISTRY and runs all registered
        checks for Canon validation. Can apply smart fixes when execute=True.

        Args:
            dry_run: If True, only report violations without fixing.
            execute: If True, apply fixes using smart_fix.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum allowed recursion depth.
            _call_path: Set of agent names already in call chain.

        Returns:
            Dict with violations_found, violations_fixed, errors, skipped.
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by CanonBaseAgent.

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
        



## Usage Examples

### Class Usage

```python
# Using ValidationOrchestrator
validationorchestrator = ValidationOrchestrator()
validationorchestrator.can_run()
validationorchestrator.get_file_hash()
```

### Function Usage

```python
# Using _load_activation_gate
result = _load_activation_gate()
```

```python
# Using _get_file_io
result = _get_file_io()
```

```python
# Using _init_registry
result = _init_registry(cls, ctx)
```



---
**Generated**: 2026-03-26T09:39:03.784440
**Type**: api_reference
**Quality**: comprehensive
