# API Documentation: runtime_invariant_checker

**Target Audience**: developers, api_users

# runtime_invariant_checker API Documentation

**File**: `runtime_invariant_checker.py`
**Classes**: 0
**Functions**: 13


## Functions

- **assert_mutation_source_is_l2** -> None
- **assert_mutation_in_ledger** -> None
- **assert_state_read_source_is_l4** -> None
- **assert_c0_no_authority_fields** -> None
- **assert_telemetry_no_config_mutation** -> None
- **assert_human_patch_l5_clearance** -> None
- **run_all_invariants** -> list[str]
- **_check_inv1** -> None
- **_check_inv2** -> None
- **_check_inv3** -> None
- **_check_inv4** -> None
- **_check_inv5** -> None
- **_check_inv6** -> None


## Function: assert_mutation_source_is_l2

**Parameters**: mutation_source
**Returns**: None
**Description**: Invariant 1: L2 is the ONLY mutation executor.



## Function: assert_mutation_in_ledger

**Parameters**: ledger_entries, file_path, operation
**Returns**: None
**Description**: Invariant 2: All mutations pass through UWG (present in ledger).



## Function: assert_state_read_source_is_l4

**Parameters**: state_read_source
**Returns**: None
**Description**: Invariant 3: L4 is the sole state authority.



## Function: assert_c0_no_authority_fields

**Parameters**: c0_payload
**Returns**: None
**Description**: Invariant 4: C0 context never carries authority fields.



## Function: assert_telemetry_no_config_mutation

**Parameters**: current_stage, config_mutated
**Returns**: None
**Description**: Invariant 5: L6 telemetry cannot mutate runtime state before S9.



## Function: assert_human_patch_l5_clearance

**Parameters**: l5_clearance_signature
**Returns**: None
**Description**: Invariant 6: Human patches must pass L5 re-clearance.



## Function: run_all_invariants

**Returns**: list[str]
**Description**: Run all applicable invariants. Returns list of violation messages (empty = clean).



## Function: _check_inv1

**Parameters**: mutation_source
**Returns**: None


## Function: _check_inv2

**Parameters**: args
**Returns**: None


## Function: _check_inv3

**Parameters**: state_read_source
**Returns**: None


## Function: _check_inv4

**Parameters**: c0_payload
**Returns**: None


## Function: _check_inv5

**Parameters**: args
**Returns**: None


## Function: _check_inv6

**Parameters**: sig
**Returns**: None


## Usage Examples

### Function Usage

```python
# Using assert_mutation_source_is_l2
result = assert_mutation_source_is_l2(mutation_source)
```

```python
# Using assert_mutation_in_ledger
result = assert_mutation_in_ledger(ledger_entries, file_path)
```

```python
# Using assert_state_read_source_is_l4
result = assert_state_read_source_is_l4(state_read_source)
```



---
**Generated**: 2026-03-26T09:39:05.018600
**Type**: api_reference
**Quality**: comprehensive
