# API Documentation: pytest_config_guardrail

**Target Audience**: developers, api_users

# pytest_config_guardrail API Documentation

**File**: `pytest_config_guardrail.py`
**Classes**: 2
**Functions**: 15

## Classes

- **PytestEnforcementGuard**
- **TestPytestConfigGuardBrittleMarkerDetection**

## Functions

- **main**
- **__init__**
- **validate_pytest_configuration** -> tuple[list[str], list[str]]
- **_validate_pytest_ini** -> None
- **_extract_markers_from_ini** -> set[str]
- **_validate_markers** -> None
- **_validate_conftest** -> None
- **_validate_collection_modifyitems** -> None
- **_check_brittle_marker_access** -> None
- **_is_getoption_call** -> bool
- **_validate_marker_consistency** -> None
- **_get_pytest_ini_markers** -> set[str]
- **_get_used_test_markers** -> set[str]
- **test_detects_brittle_getoption_m**
- **test_allows_robust_getattr_pattern**


## Class: PytestEnforcementGuard

**Description**: Enforces pytest configuration hardening rules.

### Methods

#### __init__
**Parameters**: self, repo_root

#### validate_pytest_configuration
**Parameters**: self
**Returns**: tuple[list[str], list[str]]
**Description**: Validate entire pytest configuration setup.

#### _validate_pytest_ini
**Parameters**: self, pytest_ini
**Returns**: None
**Description**: Validate pytest.ini configuration.

#### _extract_markers_from_ini
**Parameters**: self, content
**Returns**: set[str]
**Description**: Extract marker names from pytest.ini.

#### _validate_markers
**Parameters**: self, markers
**Returns**: None
**Description**: Validate marker configuration.

#### _validate_conftest
**Parameters**: self, conftest
**Returns**: None
**Description**: Validate conftest.py for hook transparency.

#### _validate_collection_modifyitems
**Parameters**: self, conftest, node
**Returns**: None
**Description**: Validate pytest_collection_modifyitems hook.

#### _check_brittle_marker_access
**Parameters**: self, conftest, node
**Returns**: None
**Description**: Check for brittle config.getoption("-m") marker access patterns.

        Flags any use of getoption("-m") or getoption('-m') with or without default arg.
        Robust alternative: getattr(config.option, "markexpr", "")
        

#### _is_getoption_call
**Parameters**: self, node
**Returns**: bool
**Description**: Check if a Call node is a getoption method call.

#### _validate_marker_consistency
**Parameters**: self
**Returns**: None
**Description**: Validate marker usage across test files.

#### _get_pytest_ini_markers
**Parameters**: self
**Returns**: set[str]
**Description**: Get markers from pytest.ini.

#### _get_used_test_markers
**Parameters**: self
**Returns**: set[str]
**Description**: Get markers actually used in test files.



## Class: TestPytestConfigGuardBrittleMarkerDetection

**Description**: Unit tests for brittle marker access detection.

### Methods

#### test_detects_brittle_getoption_m
**Parameters**: self
**Description**: Test that getoption("-m") is flagged as brittle.

#### test_allows_robust_getattr_pattern
**Parameters**: self
**Description**: Test that getattr(config.option, 'markexpr', '') is NOT flagged.



## Function: main

**Description**: Run pytest enforcement validation.



## Function: __init__

**Parameters**: self, repo_root


## Function: validate_pytest_configuration

**Parameters**: self
**Returns**: tuple[list[str], list[str]]
**Description**: Validate entire pytest configuration setup.



## Function: _validate_pytest_ini

**Parameters**: self, pytest_ini
**Returns**: None
**Description**: Validate pytest.ini configuration.



## Function: _extract_markers_from_ini

**Parameters**: self, content
**Returns**: set[str]
**Description**: Extract marker names from pytest.ini.



## Function: _validate_markers

**Parameters**: self, markers
**Returns**: None
**Description**: Validate marker configuration.



## Function: _validate_conftest

**Parameters**: self, conftest
**Returns**: None
**Description**: Validate conftest.py for hook transparency.



## Function: _validate_collection_modifyitems

**Parameters**: self, conftest, node
**Returns**: None
**Description**: Validate pytest_collection_modifyitems hook.



## Function: _check_brittle_marker_access

**Parameters**: self, conftest, node
**Returns**: None
**Description**: Check for brittle config.getoption("-m") marker access patterns.

        Flags any use of getoption("-m") or getoption('-m') with or without default arg.
        Robust alternative: getattr(config.option, "markexpr", "")
        



## Function: _is_getoption_call

**Parameters**: self, node
**Returns**: bool
**Description**: Check if a Call node is a getoption method call.



## Function: _validate_marker_consistency

**Parameters**: self
**Returns**: None
**Description**: Validate marker usage across test files.



## Function: _get_pytest_ini_markers

**Parameters**: self
**Returns**: set[str]
**Description**: Get markers from pytest.ini.



## Function: _get_used_test_markers

**Parameters**: self
**Returns**: set[str]
**Description**: Get markers actually used in test files.



## Function: test_detects_brittle_getoption_m

**Parameters**: self
**Description**: Test that getoption("-m") is flagged as brittle.



## Function: test_allows_robust_getattr_pattern

**Parameters**: self
**Description**: Test that getattr(config.option, 'markexpr', '') is NOT flagged.



## Usage Examples

### Class Usage

```python
# Using PytestEnforcementGuard
pytestenforcementguard = PytestEnforcementGuard()
pytestenforcementguard.validate_pytest_configuration()
```

```python
# Using TestPytestConfigGuardBrittleMarkerDetection
testpytestconfigguardbrittlemarkerdetection = TestPytestConfigGuardBrittleMarkerDetection()
testpytestconfigguardbrittlemarkerdetection.test_detects_brittle_getoption_m()
testpytestconfigguardbrittlemarkerdetection.test_allows_robust_getattr_pattern()
```

### Function Usage

```python
# Using main
result = main()
```

```python
# Using __init__
result = __init__(repo_root)
```

```python
# Using validate_pytest_configuration
result = validate_pytest_configuration()
```



---
**Generated**: 2026-03-26T09:39:04.908424
**Type**: api_reference
**Quality**: comprehensive
