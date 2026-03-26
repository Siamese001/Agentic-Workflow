# API Documentation: workflow_loader_types

**Target Audience**: developers, api_users

# workflow_loader_types API Documentation

**File**: `workflow_loader_types.py`
**Classes**: 4
**Functions**: 21

## Classes

- **WordCountConstraints**
- **KNodeConfig**
- **CreativeBriefConfig**
- **WorkflowLoader**

## Functions

- **create_workflow_loader** -> WorkflowLoader
- **from_list** -> WordCountConstraints
- **__post_init__** -> None
- **__init__**
- **_load_workflow** -> None
- **_get_fallback_workflow** -> dict[str, Any]
- **get_version** -> str
- **get_metadata** -> dict[str, Any]
- **get_role_config** -> dict[str, Any]
- **get_task_pipeline** -> list[dict[str, Any]]
- **get_context_config** -> dict[str, Any]
- **get_reasoning_config** -> dict[str, Any]
- **get_creative_brief** -> CreativeBriefConfig
- **get_knode_configs** -> dict[str, KNodeConfig]
- **get_knode_config** -> KNodeConfig | None
- **get_validation_rules** -> dict[str, Any]
- **get_pre_flight_tests** -> list[dict[str, Any]]
- **get_file_complexity_thresholds** -> dict[str, int]
- **get_required_files** -> list[str]
- **get_enforcement_rules** -> list[str]
- **reload** -> None


## Class: WordCountConstraints

**Description**: Word count constraints for a section.

### Methods

#### from_list
**Parameters**: cls, word_range
**Returns**: WordCountConstraints
**Description**: Create from a list like [120, 140].



## Class: KNodeConfig

**Description**: configuration for a single K-node.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: CreativeBriefConfig

**Description**: Creative brief configuration.



## Class: WorkflowLoader

**Description**: Loads and provides access to workflow configuration from JSON.

### Methods

#### __init__
**Parameters**: self, workflow_path
**Description**: 
        Initialize WorkflowLoader.

        Args:
            workflow_path: Path to workflow JSON file. Defaults to active_workflow.json.
        

#### _load_workflow
**Parameters**: self
**Returns**: None
**Description**: Load the workflow JSON from disk.

#### _get_fallback_workflow
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get minimal fallback workflow configuration.

#### get_version
**Parameters**: self
**Returns**: str
**Description**: Get the workflow version.

#### get_metadata
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get the metadata section.

#### get_role_config
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get the role configuration (section 1).

#### get_task_pipeline
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get the Task pipeline phases.

#### get_context_config
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get the context management configuration.

#### get_reasoning_config
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get the reasoning configuration.

#### get_creative_brief
**Parameters**: self
**Returns**: CreativeBriefConfig
**Description**: Extract and return the creative brief configuration.

#### get_knode_configs
**Parameters**: self
**Returns**: dict[str, KNodeConfig]
**Description**: Get all K-node configurations.

#### get_knode_config
**Parameters**: self, node_id
**Returns**: KNodeConfig | None
**Description**: Get a specific K-node configuration.

#### get_validation_rules
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get validation rules and thresholds.

#### get_pre_flight_tests
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get pre-flight validation tests.

#### get_file_complexity_thresholds
**Parameters**: self
**Returns**: dict[str, int]
**Description**: Get file complexity gate thresholds.

#### get_required_files
**Parameters**: self
**Returns**: list[str]
**Description**: Get list of required files.

#### get_enforcement_rules
**Parameters**: self
**Returns**: list[str]
**Description**: Get critical enforcement rules.

#### reload
**Parameters**: self
**Returns**: None
**Description**: Reload the workflow from disk and clear all caches.



## Function: create_workflow_loader

**Parameters**: workflow_path
**Returns**: WorkflowLoader
**Description**: Create a WorkflowLoader instance.



## Function: from_list

**Parameters**: cls, word_range
**Returns**: WordCountConstraints
**Description**: Create from a list like [120, 140].



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, workflow_path
**Description**: 
        Initialize WorkflowLoader.

        Args:
            workflow_path: Path to workflow JSON file. Defaults to active_workflow.json.
        



## Function: _load_workflow

**Parameters**: self
**Returns**: None
**Description**: Load the workflow JSON from disk.



## Function: _get_fallback_workflow

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get minimal fallback workflow configuration.



## Function: get_version

**Parameters**: self
**Returns**: str
**Description**: Get the workflow version.



## Function: get_metadata

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get the metadata section.



## Function: get_role_config

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get the role configuration (section 1).



## Function: get_task_pipeline

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get the Task pipeline phases.



## Function: get_context_config

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get the context management configuration.



## Function: get_reasoning_config

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get the reasoning configuration.



## Function: get_creative_brief

**Parameters**: self
**Returns**: CreativeBriefConfig
**Description**: Extract and return the creative brief configuration.



## Function: get_knode_configs

**Parameters**: self
**Returns**: dict[str, KNodeConfig]
**Description**: Get all K-node configurations.



## Function: get_knode_config

**Parameters**: self, node_id
**Returns**: KNodeConfig | None
**Description**: Get a specific K-node configuration.



## Function: get_validation_rules

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get validation rules and thresholds.



## Function: get_pre_flight_tests

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: Get pre-flight validation tests.



## Function: get_file_complexity_thresholds

**Parameters**: self
**Returns**: dict[str, int]
**Description**: Get file complexity gate thresholds.



## Function: get_required_files

**Parameters**: self
**Returns**: list[str]
**Description**: Get list of required files.



## Function: get_enforcement_rules

**Parameters**: self
**Returns**: list[str]
**Description**: Get critical enforcement rules.



## Function: reload

**Parameters**: self
**Returns**: None
**Description**: Reload the workflow from disk and clear all caches.



## Usage Examples

### Class Usage

```python
# Using WordCountConstraints
wordcountconstraints = WordCountConstraints()
wordcountconstraints.from_list()
```

```python
# Using KNodeConfig
knodeconfig = KNodeConfig()
```

```python
# Using CreativeBriefConfig
creativebriefconfig = CreativeBriefConfig()
```

### Function Usage

```python
# Using create_workflow_loader
result = create_workflow_loader(workflow_path)
```

```python
# Using from_list
result = from_list(cls, word_range)
```

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:04.422945
**Type**: api_reference
**Quality**: comprehensive
