# API Documentation: apps_qwen_config

**Target Audience**: developers, api_users

# apps_qwen_config API Documentation

**File**: `apps_qwen_config.py`
**Classes**: 3
**Functions**: 3

## Classes

- **AppsQwenModelConfig**
- **AppsQwenPromptConfig**
- **AppsQwenConfig**

## Functions

- **get_model_config** -> AppsQwenModelConfig
- **get_prompt_config** -> AppsQwenPromptConfig
- **validate_configuration** -> bool


## Class: AppsQwenModelConfig

**Description**: Configuration for Qwen model in apps context.



## Class: AppsQwenPromptConfig

**Description**: Configuration for prompt templates by app.



## Class: AppsQwenConfig

**Description**: Central configuration manager for apps Qwen integration.

### Methods

#### get_model_config
**Parameters**: cls, use_case
**Returns**: AppsQwenModelConfig
**Description**: Get model configuration for specific use case.

        Args:
            use_case: Type of inference task

        Returns:
            Model configuration

        Raises:
            ValueError: If use case not found
        

#### get_prompt_config
**Parameters**: cls, app_name
**Returns**: AppsQwenPromptConfig
**Description**: Get prompt configuration for specific app.

        Args:
            app_name: Name of the app

        Returns:
            Prompt configuration

        Raises:
            ValueError: If app not found
        

#### validate_configuration
**Parameters**: cls
**Returns**: bool
**Description**: Validate all configurations are complete.

        Returns:
            True if configuration is valid
        



## Function: get_model_config

**Parameters**: cls, use_case
**Returns**: AppsQwenModelConfig
**Description**: Get model configuration for specific use case.

        Args:
            use_case: Type of inference task

        Returns:
            Model configuration

        Raises:
            ValueError: If use case not found
        



## Function: get_prompt_config

**Parameters**: cls, app_name
**Returns**: AppsQwenPromptConfig
**Description**: Get prompt configuration for specific app.

        Args:
            app_name: Name of the app

        Returns:
            Prompt configuration

        Raises:
            ValueError: If app not found
        



## Function: validate_configuration

**Parameters**: cls
**Returns**: bool
**Description**: Validate all configurations are complete.

        Returns:
            True if configuration is valid
        



## Usage Examples

### Class Usage

```python
# Using AppsQwenModelConfig
appsqwenmodelconfig = AppsQwenModelConfig()
```

```python
# Using AppsQwenPromptConfig
appsqwenpromptconfig = AppsQwenPromptConfig()
```

```python
# Using AppsQwenConfig
appsqwenconfig = AppsQwenConfig()
appsqwenconfig.get_model_config()
appsqwenconfig.get_prompt_config()
```

### Function Usage

```python
# Using get_model_config
result = get_model_config(cls, use_case)
```

```python
# Using get_prompt_config
result = get_prompt_config(cls, app_name)
```

```python
# Using validate_configuration
result = validate_configuration(cls)
```



---
**Generated**: 2026-03-26T09:39:03.605249
**Type**: api_reference
**Quality**: comprehensive
