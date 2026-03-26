# API Documentation: test_rigor_enforcer

**Target Audience**: developers, api_users

# test_rigor_enforcer API Documentation

**File**: `test_rigor_enforcer.py`
**Classes**: 3
**Functions**: 8

## Classes

- **TestCoverageRequirement**
- **ValidationResult**
- **TestRigorEnforcer**

## Functions

- **__init__**
- **declare_scope** -> None
- **add_coverage_requirement** -> None
- **validate_pre_code_generation** -> ValidationResult
- **validate_post_code_generation** -> ValidationResult
- **_run_pytest_collect** -> int | None
- **_run_pytest_execute** -> tuple[int, int, int] | None
- **generate_validation_report** -> str


## Class: TestCoverageRequirement

**Description**: Requirement for test coverage of a changed surface.



## Class: ValidationResult

**Description**: Result of test rigor validation.



## Class: TestRigorEnforcer

**Description**: Enforces constitutional testing requirements during code generation.

### Methods

#### __init__
**Parameters**: self, project_root

#### declare_scope
**Parameters**: self, changed_files
**Returns**: None
**Description**: Declare scope of code changes (Step 1 of pre-code-generation gate).

#### add_coverage_requirement
**Parameters**: self, requirement
**Returns**: None
**Description**: Add test coverage requirement for a changed surface.

#### validate_pre_code_generation
**Parameters**: self
**Returns**: ValidationResult
**Description**: Validate that test requirements are declared before code generation.

        Enforces §1.2: Tests MUST exist before logic changes are committed.

        Returns:
            ValidationResult with compliant=True if requirements declared, False otherwise
        

#### validate_post_code_generation
**Parameters**: self, test_path
**Returns**: ValidationResult
**Description**: Validate test coverage after code changes.

        Enforces:
        - §1.12: Zero-tolerance for test skipping (collection == execution)
        - §1.1: Test coverage matches declared requirements

        Args:
            test_path: Optional path to test directory/file. If None, runs all tests.

        Returns:
            ValidationResult with compliance status and metrics
        

#### _run_pytest_collect
**Parameters**: self, test_path
**Returns**: int | None
**Description**: Run pytest --collect-only and return count of collected tests.

#### _run_pytest_execute
**Parameters**: self, test_path
**Returns**: tuple[int, int, int] | None
**Description**: Run pytest and return (passed, failed, skipped) counts.

#### generate_validation_report
**Parameters**: self, result
**Returns**: str
**Description**: Generate validation report for post-code validation.



## Function: __init__

**Parameters**: self, project_root


## Function: declare_scope

**Parameters**: self, changed_files
**Returns**: None
**Description**: Declare scope of code changes (Step 1 of pre-code-generation gate).



## Function: add_coverage_requirement

**Parameters**: self, requirement
**Returns**: None
**Description**: Add test coverage requirement for a changed surface.



## Function: validate_pre_code_generation

**Parameters**: self
**Returns**: ValidationResult
**Description**: Validate that test requirements are declared before code generation.

        Enforces §1.2: Tests MUST exist before logic changes are committed.

        Returns:
            ValidationResult with compliant=True if requirements declared, False otherwise
        



## Function: validate_post_code_generation

**Parameters**: self, test_path
**Returns**: ValidationResult
**Description**: Validate test coverage after code changes.

        Enforces:
        - §1.12: Zero-tolerance for test skipping (collection == execution)
        - §1.1: Test coverage matches declared requirements

        Args:
            test_path: Optional path to test directory/file. If None, runs all tests.

        Returns:
            ValidationResult with compliance status and metrics
        



## Function: _run_pytest_collect

**Parameters**: self, test_path
**Returns**: int | None
**Description**: Run pytest --collect-only and return count of collected tests.



## Function: _run_pytest_execute

**Parameters**: self, test_path
**Returns**: tuple[int, int, int] | None
**Description**: Run pytest and return (passed, failed, skipped) counts.



## Function: generate_validation_report

**Parameters**: self, result
**Returns**: str
**Description**: Generate validation report for post-code validation.



## Usage Examples

### Class Usage

```python
# Using TestCoverageRequirement
testcoveragerequirement = TestCoverageRequirement()
```

```python
# Using ValidationResult
validationresult = ValidationResult()
```

```python
# Using TestRigorEnforcer
testrigorenforcer = TestRigorEnforcer()
testrigorenforcer.declare_scope()
testrigorenforcer.add_coverage_requirement()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using declare_scope
result = declare_scope(changed_files)
```

```python
# Using add_coverage_requirement
result = add_coverage_requirement(requirement)
```



---
**Generated**: 2026-03-26T09:39:04.966710
**Type**: api_reference
**Quality**: comprehensive
