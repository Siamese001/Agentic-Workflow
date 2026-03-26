# API Documentation: ssot_structure_validation_enforcer

**Target Audience**: developers, api_users

# ssot_structure_validation_enforcer API Documentation

**File**: `ssot_structure_validation_enforcer.py`
**Classes**: 3
**Functions**: 19

## Classes

- **StructureViolation**
- **StructureValidationResult**
- **SSOTStructureValidator**

## Functions

- **run_structure_validation** -> StructureValidationResult
- **compliance_percentage** -> float
- **is_fully_compliant** -> bool
- **__init__**
- **_normalize_path** -> str
- **_get_territory** -> str | None
- **_get_expected_depth** -> int
- **_get_actual_depth** -> int
- **_is_base_agent** -> bool
- **_is_in_variable_depth_folder** -> bool
- **_is_in_l4_approved_folder** -> bool
- **_validate_base_agent_location** -> StructureViolation | None
- **_validate_layer_assignment** -> StructureViolation | None
- **_validate_depth** -> StructureViolation | None
- **_validate_territory** -> StructureViolation | None
- **_validate_forbidden_patterns** -> StructureViolation | None
- **validate_agent** -> list[StructureViolation]
- **validate_structure** -> StructureValidationResult
- **generate_report** -> str


## Class: StructureViolation

**Description**: A single structure violation.



## Class: StructureValidationResult

**Description**: Result of SSOT structure validation.

### Methods

#### compliance_percentage
**Parameters**: self
**Returns**: float
**Description**: Calculate compliance percentage.

#### is_fully_compliant
**Parameters**: self
**Returns**: bool
**Description**: Check if all agents are compliant.



## Class: SSOTStructureValidator

**Description**: Validates agent structure against SSOT definitions.

### Methods

#### __init__
**Parameters**: self, project_root
**Description**: Initialize validator with project root.

#### _normalize_path
**Parameters**: self, path
**Returns**: str
**Description**: Normalize path separators to forward slashes.

#### _get_territory
**Parameters**: self, path
**Returns**: str | None
**Description**: Get the territory for a given path.

#### _get_expected_depth
**Parameters**: self, territory
**Returns**: int
**Description**: Get expected depth for a territory.

#### _get_actual_depth
**Parameters**: self, path
**Returns**: int
**Description**: Get actual depth of a file path.

#### _is_base_agent
**Parameters**: self, class_name
**Returns**: bool
**Description**: Check if class name indicates a base agent.

#### _is_in_variable_depth_folder
**Parameters**: self, path
**Returns**: bool
**Description**: Check if path is in a variable depth folder.

#### _is_in_l4_approved_folder
**Parameters**: self, path
**Returns**: bool
**Description**: Check if path is in an L4 approved folder.

#### _validate_base_agent_location
**Parameters**: self, agent
**Returns**: StructureViolation | None
**Description**: Validate that base agents are in the correct location.

#### _validate_layer_assignment
**Parameters**: self, agent
**Returns**: StructureViolation | None
**Description**: Validate that agent layer matches its path.

#### _validate_depth
**Parameters**: self, agent
**Returns**: StructureViolation | None
**Description**: Validate path depth against territory requirements.

#### _validate_territory
**Parameters**: self, agent
**Returns**: StructureViolation | None
**Description**: Validate agent is in a recognized territory.

#### _validate_forbidden_patterns
**Parameters**: self, agent
**Returns**: StructureViolation | None
**Description**: Check for forbidden patterns in path.

#### validate_agent
**Parameters**: self, agent
**Returns**: list[StructureViolation]
**Description**: Validate a single agent against all SSOT rules.

#### validate_structure
**Parameters**: self
**Returns**: StructureValidationResult
**Description**: Perform full SSOT structure validation.

#### generate_report
**Parameters**: self, result
**Returns**: str
**Description**: Generate markdown report from validation result.



## Function: run_structure_validation

**Returns**: StructureValidationResult
**Description**: Run SSOT structure validation and return result.



## Function: compliance_percentage

**Parameters**: self
**Returns**: float
**Description**: Calculate compliance percentage.



## Function: is_fully_compliant

**Parameters**: self
**Returns**: bool
**Description**: Check if all agents are compliant.



## Function: __init__

**Parameters**: self, project_root
**Description**: Initialize validator with project root.



## Function: _normalize_path

**Parameters**: self, path
**Returns**: str
**Description**: Normalize path separators to forward slashes.



## Function: _get_territory

**Parameters**: self, path
**Returns**: str | None
**Description**: Get the territory for a given path.



## Function: _get_expected_depth

**Parameters**: self, territory
**Returns**: int
**Description**: Get expected depth for a territory.



## Function: _get_actual_depth

**Parameters**: self, path
**Returns**: int
**Description**: Get actual depth of a file path.



## Function: _is_base_agent

**Parameters**: self, class_name
**Returns**: bool
**Description**: Check if class name indicates a base agent.



## Function: _is_in_variable_depth_folder

**Parameters**: self, path
**Returns**: bool
**Description**: Check if path is in a variable depth folder.



## Function: _is_in_l4_approved_folder

**Parameters**: self, path
**Returns**: bool
**Description**: Check if path is in an L4 approved folder.



## Function: _validate_base_agent_location

**Parameters**: self, agent
**Returns**: StructureViolation | None
**Description**: Validate that base agents are in the correct location.



## Function: _validate_layer_assignment

**Parameters**: self, agent
**Returns**: StructureViolation | None
**Description**: Validate that agent layer matches its path.



## Function: _validate_depth

**Parameters**: self, agent
**Returns**: StructureViolation | None
**Description**: Validate path depth against territory requirements.



## Function: _validate_territory

**Parameters**: self, agent
**Returns**: StructureViolation | None
**Description**: Validate agent is in a recognized territory.



## Function: _validate_forbidden_patterns

**Parameters**: self, agent
**Returns**: StructureViolation | None
**Description**: Check for forbidden patterns in path.



## Function: validate_agent

**Parameters**: self, agent
**Returns**: list[StructureViolation]
**Description**: Validate a single agent against all SSOT rules.



## Function: validate_structure

**Parameters**: self
**Returns**: StructureValidationResult
**Description**: Perform full SSOT structure validation.



## Function: generate_report

**Parameters**: self, result
**Returns**: str
**Description**: Generate markdown report from validation result.



## Usage Examples

### Class Usage

```python
# Using StructureViolation
structureviolation = StructureViolation()
```

```python
# Using StructureValidationResult
structurevalidationresult = StructureValidationResult()
structurevalidationresult.compliance_percentage()
structurevalidationresult.is_fully_compliant()
```

```python
# Using SSOTStructureValidator
ssotstructurevalidator = SSOTStructureValidator()
ssotstructurevalidator.validate_agent()
ssotstructurevalidator.validate_structure()
```

### Function Usage

```python
# Using run_structure_validation
result = run_structure_validation()
```

```python
# Using compliance_percentage
result = compliance_percentage()
```

```python
# Using is_fully_compliant
result = is_fully_compliant()
```



---
**Generated**: 2026-03-26T09:39:04.954536
**Type**: api_reference
**Quality**: comprehensive
