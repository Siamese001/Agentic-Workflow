# API Documentation: RegressionOracleAgent

**Target Audience**: developers, api_users

# RegressionOracleAgent API Documentation

**File**: `RegressionOracleAgent.py`
**Classes**: 1
**Functions**: 8

## Classes

- **RegressionOracleAgent** (inherits from SovereignBaseAgent)

## Functions

- **__init__** -> None
- **_ast_safety_check** -> list[str]
- **_emit_regression_check_pass** -> Any
- **heal_repository** -> dict[str, int]
- **post_heal_validation** -> dict[str, Any]
- **cleanup_violations** -> list[dict[str, Any]]
- **run_with_cleanup** -> dict[str, Any]
- **heal** -> dict[str, Any]


## Class: RegressionOracleAgent

**Description**: 
    The Regression Oracle - Automated Test Synthesizer

    Subscribes to AtomicBlackboard FILE_MODIFIED signals.
    Generates pytest cases for changed methods.
    Queries Pinecone for historical edge cases.
    Runs tests and performs self-correction.

    Process:
    1. Detect file modification
    2. Identify changed methods via diff
    3. Query Pinecone for failure patterns
    4. Generate pytest with edge cases
    5. Run test and self-correct if needed
    6. Emit REGRESSION_CHECK_PASS signal
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self, ctx
**Returns**: None
**Description**: 
        Initialize Regression Oracle.

        Args:
            ctx: ValidationContext
        

#### _ast_safety_check
**Parameters**: test_code
**Returns**: list[str]
**Description**: AST-scan generated test code for dangerous nodes before execution.

        Returns a list of violation descriptions (empty = safe).
        

#### _emit_regression_check_pass
**Parameters**: self, file_path, method_name
**Returns**: Any
**Description**: Emit REGRESSION_CHECK_PASS signal to blackboard.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L5 safety agent - operational only.

#### post_heal_validation
**Parameters**: self, generated_tests, dry_run
**Returns**: dict[str, Any]
**Description**: 
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        GOLD STANDARD: Post-heal validation confirming test coverage.
        Verifies tests were successfully generated and pass.

        Args:
            generated_tests: Tests generated during healing
            dry_run: If True, only preview without applying

        Returns:
            Dict with validation status and details
        

#### cleanup_violations
**Parameters**: self, violations, dry_run, max_actions
**Returns**: list[dict[str, Any]]
**Description**: 
        GOLD STANDARD: Cleanup regression violations with test regeneration.

        Args:
            violations: List of RegressionViolation objects
            dry_run: If True, only preview actions
            max_actions: Maximum cleanup actions per run

        Returns:
            List of action dicts with results and batch summary
        

#### run_with_cleanup
**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: 
        GOLD STANDARD: Full regression oracle with autonomous cleanup.
        Detects method changes, generates tests, and validates coverage.

        Args:
            dry_run: If True, only preview cleanup actions

        Returns:
            Dict with comprehensive execution and cleanup summaries
        

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by RegressionOracleAgent.

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
        



## Function: __init__

**Parameters**: self, ctx
**Returns**: None
**Description**: 
        Initialize Regression Oracle.

        Args:
            ctx: ValidationContext
        



## Function: _ast_safety_check

**Parameters**: test_code
**Returns**: list[str]
**Description**: AST-scan generated test code for dangerous nodes before execution.

        Returns a list of violation descriptions (empty = safe).
        



## Function: _emit_regression_check_pass

**Parameters**: self, file_path, method_name
**Returns**: Any
**Description**: Emit REGRESSION_CHECK_PASS signal to blackboard.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, int]
**Description**: L5 safety agent - operational only.



## Function: post_heal_validation

**Parameters**: self, generated_tests, dry_run
**Returns**: dict[str, Any]
**Description**: 
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        GOLD STANDARD: Post-heal validation confirming test coverage.
        Verifies tests were successfully generated and pass.

        Args:
            generated_tests: Tests generated during healing
            dry_run: If True, only preview without applying

        Returns:
            Dict with validation status and details
        



## Function: cleanup_violations

**Parameters**: self, violations, dry_run, max_actions
**Returns**: list[dict[str, Any]]
**Description**: 
        GOLD STANDARD: Cleanup regression violations with test regeneration.

        Args:
            violations: List of RegressionViolation objects
            dry_run: If True, only preview actions
            max_actions: Maximum cleanup actions per run

        Returns:
            List of action dicts with results and batch summary
        



## Function: run_with_cleanup

**Parameters**: self, dry_run
**Returns**: dict[str, Any]
**Description**: 
        GOLD STANDARD: Full regression oracle with autonomous cleanup.
        Detects method changes, generates tests, and validates coverage.

        Args:
            dry_run: If True, only preview cleanup actions

        Returns:
            Dict with comprehensive execution and cleanup summaries
        



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by RegressionOracleAgent.

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
# Using RegressionOracleAgent
regressionoracleagent = RegressionOracleAgent()
regressionoracleagent.heal_repository()
regressionoracleagent.post_heal_validation()
```

### Function Usage

```python
# Using __init__
result = __init__(ctx)
```

```python
# Using _ast_safety_check
result = _ast_safety_check(test_code)
```

```python
# Using _emit_regression_check_pass
result = _emit_regression_check_pass(file_path, method_name)
```



---
**Generated**: 2026-03-26T09:39:05.365016
**Type**: api_reference
**Quality**: comprehensive
