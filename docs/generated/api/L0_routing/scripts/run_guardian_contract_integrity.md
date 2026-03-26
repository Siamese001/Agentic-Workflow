# API Documentation: run_guardian_contract_integrity

**Target Audience**: developers, api_users

# run_guardian_contract_integrity API Documentation

**File**: `run_guardian_contract_integrity.py`
**Classes**: 0
**Functions**: 11


## Functions

- **_check_imports_contract** -> bool
- **_check_imports_normalize** -> bool
- **_check_returns_guardian_result** -> bool
- **_check_no_raw_json_dumps** -> list[int]
- **_check_imports_scan_caps** -> bool
- **_check_uses_guard_scan_budget** -> bool
- **_check_no_raise_exception_for_caps** -> list[tuple[int, str]]
- **_check_no_raise_runtime_error_for_caps** -> list[int]
- **_module_to_path** -> str
- **run_contract_integrity_guardian** -> GuardianResult
- **main** -> int


## Function: _check_imports_contract

**Parameters**: tree
**Returns**: bool
**Description**: Check if the module imports from the canonical contract path.



## Function: _check_imports_normalize

**Parameters**: tree
**Returns**: bool
**Description**: Check if the module imports normalize_repo_path.



## Function: _check_returns_guardian_result

**Parameters**: tree
**Returns**: bool
**Description**: Check if any function has a return type annotation of GuardianResult.



## Function: _check_no_raw_json_dumps

**Parameters**: tree
**Returns**: list[int]
**Description**: 
    Find json.dumps calls that are NOT on a GuardianResult method.
    Returns line numbers of suspicious calls.
    



## Function: _check_imports_scan_caps

**Parameters**: tree
**Returns**: bool
**Description**: Check if the module imports any scan cap constants.



## Function: _check_uses_guard_scan_budget

**Parameters**: tree
**Returns**: bool
**Description**: Check if the module imports guard_scan_budget from SSOT.



## Function: _check_no_raise_exception_for_caps

**Parameters**: tree
**Returns**: list[tuple[int, str]]
**Description**: 
    AST-detect 'raise <AnyException>(...)' where the message string references
    scan cap constant names. Returns (line_number, exception_name) tuples.
    Catches RuntimeError, ValueError, Exception, or any custom exception.
    



## Function: _check_no_raise_runtime_error_for_caps

**Parameters**: tree
**Returns**: list[int]
**Description**: Legacy wrapper — returns line numbers only.



## Function: _module_to_path

**Parameters**: module
**Returns**: str
**Description**: Convert dotted module path to file path.



## Function: run_contract_integrity_guardian

**Parameters**: repo_root, timestamp
**Returns**: GuardianResult
**Description**: 
    Scan all guardian scripts from SSOT registry and verify they follow the contract.
    



## Function: main

**Returns**: int


## Usage Examples

### Function Usage

```python
# Using _check_imports_contract
result = _check_imports_contract(tree)
```

```python
# Using _check_imports_normalize
result = _check_imports_normalize(tree)
```

```python
# Using _check_returns_guardian_result
result = _check_returns_guardian_result(tree)
```



---
**Generated**: 2026-03-26T09:39:03.212519
**Type**: api_reference
**Quality**: comprehensive
