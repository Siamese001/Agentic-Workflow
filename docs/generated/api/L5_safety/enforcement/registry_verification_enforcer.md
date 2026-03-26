# API Documentation: registry_verification_enforcer

**Target Audience**: developers, api_users

# registry_verification_enforcer API Documentation

**File**: `registry_verification_enforcer.py`
**Classes**: 3
**Functions**: 12

## Classes

- **AgentInfo**
- **VerificationResult**
- **RegistryVerifier**

## Functions

- **run_verification** -> VerificationResult
- **__init__**
- **_find_project_root** -> Path
- **_find_discovery_json** -> Path
- **_is_excluded** -> bool
- **_is_test_file** -> bool
- **_extract_layer** -> str
- **_parse_agent_file** -> AgentInfo | None
- **scan_filesystem** -> list[AgentInfo]
- **load_registry** -> list[dict[str, Any]]
- **verify_registry** -> VerificationResult
- **generate_report** -> str


## Class: AgentInfo

**Description**: Information about a discovered agent.



## Class: VerificationResult

**Description**: Result of registry verification.



## Class: RegistryVerifier

**Description**: Verifies agent registry completeness against filesystem.

### Methods

#### __init__
**Parameters**: self, project_root
**Description**: Initialize verifier with project root.

#### _find_project_root
**Parameters**: self
**Returns**: Path
**Description**: Find project root by looking for pyproject.toml or .git.

#### _find_discovery_json
**Parameters**: self
**Returns**: Path
**Description**: Find the agent discovery JSON file.

#### _is_excluded
**Parameters**: self, path
**Returns**: bool
**Description**: Check if path should be excluded from scanning.

#### _is_test_file
**Parameters**: self, path
**Returns**: bool
**Description**: Check if path is a test file.

#### _extract_layer
**Parameters**: self, relative_path
**Returns**: str
**Description**: Extract layer from relative path.

#### _parse_agent_file
**Parameters**: self, file_path
**Returns**: AgentInfo | None
**Description**: Parse an agent file to extract class information.

#### scan_filesystem
**Parameters**: self
**Returns**: list[AgentInfo]
**Description**: Scan filesystem for all agent files.

#### load_registry
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Load agent registry from JSON file.

#### verify_registry
**Parameters**: self
**Returns**: VerificationResult
**Description**: Perform full registry verification.

#### generate_report
**Parameters**: self, result
**Returns**: str
**Description**: Generate markdown report from verification result.



## Function: run_verification

**Returns**: VerificationResult
**Description**: Run registry verification and return result.



## Function: __init__

**Parameters**: self, project_root
**Description**: Initialize verifier with project root.



## Function: _find_project_root

**Parameters**: self
**Returns**: Path
**Description**: Find project root by looking for pyproject.toml or .git.



## Function: _find_discovery_json

**Parameters**: self
**Returns**: Path
**Description**: Find the agent discovery JSON file.



## Function: _is_excluded

**Parameters**: self, path
**Returns**: bool
**Description**: Check if path should be excluded from scanning.



## Function: _is_test_file

**Parameters**: self, path
**Returns**: bool
**Description**: Check if path is a test file.



## Function: _extract_layer

**Parameters**: self, relative_path
**Returns**: str
**Description**: Extract layer from relative path.



## Function: _parse_agent_file

**Parameters**: self, file_path
**Returns**: AgentInfo | None
**Description**: Parse an agent file to extract class information.



## Function: scan_filesystem

**Parameters**: self
**Returns**: list[AgentInfo]
**Description**: Scan filesystem for all agent files.



## Function: load_registry

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Load agent registry from JSON file.



## Function: verify_registry

**Parameters**: self
**Returns**: VerificationResult
**Description**: Perform full registry verification.



## Function: generate_report

**Parameters**: self, result
**Returns**: str
**Description**: Generate markdown report from verification result.



## Usage Examples

### Class Usage

```python
# Using AgentInfo
agentinfo = AgentInfo()
```

```python
# Using VerificationResult
verificationresult = VerificationResult()
```

```python
# Using RegistryVerifier
registryverifier = RegistryVerifier()
registryverifier.scan_filesystem()
registryverifier.load_registry()
```

### Function Usage

```python
# Using run_verification
result = run_verification()
```

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using _find_project_root
result = _find_project_root()
```



---
**Generated**: 2026-03-26T09:39:04.914705
**Type**: api_reference
**Quality**: comprehensive
