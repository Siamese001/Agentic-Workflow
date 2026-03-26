# API Documentation: forensic_discovery_prep

**Target Audience**: developers, api_users

# forensic_discovery_prep API Documentation

**File**: `forensic_discovery_prep.py`
**Classes**: 1
**Functions**: 14

## Classes

- **ForensicAgentRecord**

## Functions

- **_get_safe_subprocess_check_output**
- **sha256_file** -> str
- **extract_precise_mro** -> list[str]
- **build_class_bases_map** -> dict[str, list[str]]
- **resolve_full_mro** -> list[str]
- **stub_sentinel_detected** -> bool
- **forensic_inspect** -> ForensicAgentRecord
- **get_git_commit** -> str
- **atomic_write** -> None
- **_compute_ssot_validation** -> dict[str, str]
- **_derive_mixins** -> list[str]
- **_to_v54_schema** -> dict
- **run_forensic_discovery** -> int
- **score** -> int


## Class: ForensicAgentRecord

**Description**: The absolute truth for a single agent under audit.



## Function: _get_safe_subprocess_check_output



## Function: sha256_file

**Parameters**: path
**Returns**: str


## Function: extract_precise_mro

**Parameters**: node
**Returns**: list[str]
**Description**: 
    Extracts base classes in exact declaration order to detect 'Inheritance Traps'.
    Example: class MyAgent(SafetyMixin, BaseAgent) -> ["SafetyMixin", "BaseAgent"]
    



## Function: build_class_bases_map

**Parameters**: project_root
**Returns**: dict[str, list[str]]
**Description**: Build repo-wide mapping of class_name → direct base class names from AST.

    Scans all .py files under known source roots to enable full MRO resolution.
    On name collision, first-seen definition wins (deterministic via sorted paths).
    Handles starred bases (e.g. ``class Foo(*BASE_CLASSES)``) by resolving
    module-level tuple assignments in the same file.
    



## Function: resolve_full_mro

**Parameters**: direct_bases, class_map, _seen
**Returns**: list[str]
**Description**: Recursively expand direct bases into a full transitive MRO chain.

    Returns a flat list of all ancestor class names (deduplicated, depth-first).
    



## Function: stub_sentinel_detected

**Parameters**: content
**Returns**: bool


## Function: forensic_inspect

**Parameters**: name, layer, file_path
**Returns**: ForensicAgentRecord
**Description**: 
    Analyzes a file to build the Forensic Record.
    



## Function: get_git_commit

**Parameters**: root
**Returns**: str


## Function: atomic_write

**Parameters**: path, data
**Returns**: None


## Function: _compute_ssot_validation

**Parameters**: project_root
**Returns**: dict[str, str]
**Description**: Compute ssot_validation section: self-hash vs SSOT constant.



## Function: _derive_mixins

**Parameters**: mro_chain
**Returns**: list[str]
**Description**: Derive mixins deterministically from MRO chain entries containing 'Mixin'.



## Function: _to_v54_schema

**Parameters**: legacy, project_root
**Returns**: dict
**Description**: Transform legacy discovery output to v5.4 strict schema.



## Function: run_forensic_discovery

**Parameters**: out_path
**Returns**: int


## Function: score

**Parameters**: cls
**Returns**: int


## Usage Examples

### Class Usage

```python
# Using ForensicAgentRecord
forensicagentrecord = ForensicAgentRecord()
```

### Function Usage

```python
# Using _get_safe_subprocess_check_output
result = _get_safe_subprocess_check_output()
```

```python
# Using sha256_file
result = sha256_file(path)
```

```python
# Using extract_precise_mro
result = extract_precise_mro(node)
```



---
**Generated**: 2026-03-26T09:39:03.141323
**Type**: api_reference
**Quality**: comprehensive
