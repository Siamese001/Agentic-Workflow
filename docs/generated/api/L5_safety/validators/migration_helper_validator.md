# API Documentation: migration_helper_validator

**Target Audience**: developers, api_users

# migration_helper_validator API Documentation

**File**: `migration_helper_validator.py`
**Classes**: 3
**Functions**: 9

## Classes

- **ComplianceResult**
- **MigrationStatus**
- **MigrationHelper**

## Functions

- **check_agent_compliance** -> ComplianceResult
- **get_migration_status** -> MigrationStatus
- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]
- **check_agent_compliance** -> ComplianceResult
- **_has_feature_flag_mixin** -> bool
- **_has_method** -> bool
- **get_migration_status** -> MigrationStatus
- **generate_migration_report** -> str


## Class: ComplianceResult

**Description**: Result of agent compliance check.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: MigrationStatus

**Description**: Overall migration status.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: MigrationHelper

**Description**: Helper for tracking migration compliance.

### Methods

#### check_agent_compliance
**Parameters**: cls, agent_class, strict
**Returns**: ComplianceResult
**Description**: Check if an agent class is compliant with migration requirements.

        Args:
            agent_class: The agent class to check
            strict: If True, require all components; if False, only require mixin

        Returns:
            ComplianceResult with compliance details
        

#### _has_feature_flag_mixin
**Parameters**: cls, agent_class
**Returns**: bool
**Description**: Check if agent has FeatureFlaggedAgentMixin in MRO.

#### _has_method
**Parameters**: cls, agent_class, method_name
**Returns**: bool
**Description**: Check if agent has a specific method.

#### get_migration_status
**Parameters**: cls, agent_classes, strict
**Returns**: MigrationStatus
**Description**: Get overall migration status for a list of agents.

        Args:
            agent_classes: List of agent classes to check
            strict: If True, use strict compliance checking

        Returns:
            MigrationStatus with overall statistics
        

#### generate_migration_report
**Parameters**: cls, agent_classes, strict
**Returns**: str
**Description**: Generate a human-readable migration report.

        Args:
            agent_classes: List of agent classes to check
            strict: If True, use strict compliance checking

        Returns:
            Formatted migration report string
        



## Function: check_agent_compliance

**Parameters**: agent_class, strict
**Returns**: ComplianceResult
**Description**: Check if an agent class is compliant with migration requirements.



## Function: get_migration_status

**Parameters**: agent_classes, strict
**Returns**: MigrationStatus
**Description**: Get overall migration status for a list of agents.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: check_agent_compliance

**Parameters**: cls, agent_class, strict
**Returns**: ComplianceResult
**Description**: Check if an agent class is compliant with migration requirements.

        Args:
            agent_class: The agent class to check
            strict: If True, require all components; if False, only require mixin

        Returns:
            ComplianceResult with compliance details
        



## Function: _has_feature_flag_mixin

**Parameters**: cls, agent_class
**Returns**: bool
**Description**: Check if agent has FeatureFlaggedAgentMixin in MRO.



## Function: _has_method

**Parameters**: cls, agent_class, method_name
**Returns**: bool
**Description**: Check if agent has a specific method.



## Function: get_migration_status

**Parameters**: cls, agent_classes, strict
**Returns**: MigrationStatus
**Description**: Get overall migration status for a list of agents.

        Args:
            agent_classes: List of agent classes to check
            strict: If True, use strict compliance checking

        Returns:
            MigrationStatus with overall statistics
        



## Function: generate_migration_report

**Parameters**: cls, agent_classes, strict
**Returns**: str
**Description**: Generate a human-readable migration report.

        Args:
            agent_classes: List of agent classes to check
            strict: If True, use strict compliance checking

        Returns:
            Formatted migration report string
        



## Usage Examples

### Class Usage

```python
# Using ComplianceResult
complianceresult = ComplianceResult()
complianceresult.to_dict()
```

```python
# Using MigrationStatus
migrationstatus = MigrationStatus()
migrationstatus.to_dict()
```

```python
# Using MigrationHelper
migrationhelper = MigrationHelper()
migrationhelper.check_agent_compliance()
migrationhelper.get_migration_status()
```

### Function Usage

```python
# Using check_agent_compliance
result = check_agent_compliance(agent_class, strict)
```

```python
# Using get_migration_status
result = get_migration_status(agent_classes, strict)
```

```python
# Using to_dict
result = to_dict()
```



---
**Generated**: 2026-03-26T09:39:05.845883
**Type**: api_reference
**Quality**: comprehensive
