# API Documentation: canary_token_defense_strategy

**Target Audience**: developers, api_users

# canary_token_defense_strategy API Documentation

**File**: `canary_token_defense_strategy.py`
**Classes**: 2
**Functions**: 9

## Classes

- **CanaryToken**
- **CanaryDefense**

## Functions

- **__init__** -> None
- **generate_canary** -> CanaryToken
- **inject_canary** -> tuple[str, CanaryToken]
- **wrap_user_input** -> str
- **detect_canary_leakage** -> tuple[bool, dict]
- **validate_input_structure** -> tuple[bool, list[str]]
- **create_hardened_prompt** -> tuple[str, str, CanaryToken]
- **clear_canary** -> None
- **get_active_canaries** -> list[CanaryToken]


## Class: CanaryToken

**Description**: Represents a canary token for injection defense.



## Class: CanaryDefense

**Description**: 
    Canary Token Defense System.

    Prevents prompt injection and system prompt leakage by:
    1. Injecting invisible canary tokens into system prompts
    2. Detecting if tokens appear in outputs (indicates jailbreak)
    3. Wrapping user inputs to prevent instruction following
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### generate_canary
**Parameters**: self, purpose
**Returns**: CanaryToken
**Description**: 
        Generate a new canary token.

        Args:
            purpose: Purpose of the canary (e.g., "system_integrity", "prompt_leak")

        Returns:
            CanaryToken instance
        

#### inject_canary
**Parameters**: self, system_prompt, canary
**Returns**: tuple[str, CanaryToken]
**Description**: 
        Inject canary token into system prompt.

        Args:
            system_prompt: Original system prompt
            canary: Optional existing canary to use

        Returns:
            Tuple of (hardened_prompt, canary_used)
        

#### wrap_user_input
**Parameters**: self, user_input
**Returns**: str
**Description**: 
        Wrap user input in XML tags to prevent instruction following.

        Args:
            user_input: Raw user input

        Returns:
            Wrapped input with XML tags
        

#### detect_canary_leakage
**Parameters**: self, output, canary
**Returns**: tuple[bool, dict]
**Description**: 
        Check if canary token has leaked into output.

        Args:
            output: Model output to check
            canary: Canary token to look for

        Returns:
            Tuple of (is_leaked, detection_info)
        

#### validate_input_structure
**Parameters**: self, messages
**Returns**: tuple[bool, list[str]]
**Description**: 
        Validate that user inputs are properly wrapped.

        Args:
            messages: List of message dictionaries

        Returns:
            Tuple of (is_valid, issues)
        

#### create_hardened_prompt
**Parameters**: self, system_prompt, user_input, canary
**Returns**: tuple[str, str, CanaryToken]
**Description**: 
        Create a fully hardened prompt with canary and wrapped input.

        Args:
            system_prompt: System prompt to harden
            user_input: User input to wrap
            canary: Optional existing canary

        Returns:
            Tuple of (hardened_system_prompt, wrapped_user_input, canary)
        

#### clear_canary
**Parameters**: self, canary
**Returns**: None
**Description**: Remove a canary token from active use.

#### get_active_canaries
**Parameters**: self
**Returns**: list[CanaryToken]
**Description**: Get list of all active canary tokens.



## Function: __init__

**Parameters**: self
**Returns**: None


## Function: generate_canary

**Parameters**: self, purpose
**Returns**: CanaryToken
**Description**: 
        Generate a new canary token.

        Args:
            purpose: Purpose of the canary (e.g., "system_integrity", "prompt_leak")

        Returns:
            CanaryToken instance
        



## Function: inject_canary

**Parameters**: self, system_prompt, canary
**Returns**: tuple[str, CanaryToken]
**Description**: 
        Inject canary token into system prompt.

        Args:
            system_prompt: Original system prompt
            canary: Optional existing canary to use

        Returns:
            Tuple of (hardened_prompt, canary_used)
        



## Function: wrap_user_input

**Parameters**: self, user_input
**Returns**: str
**Description**: 
        Wrap user input in XML tags to prevent instruction following.

        Args:
            user_input: Raw user input

        Returns:
            Wrapped input with XML tags
        



## Function: detect_canary_leakage

**Parameters**: self, output, canary
**Returns**: tuple[bool, dict]
**Description**: 
        Check if canary token has leaked into output.

        Args:
            output: Model output to check
            canary: Canary token to look for

        Returns:
            Tuple of (is_leaked, detection_info)
        



## Function: validate_input_structure

**Parameters**: self, messages
**Returns**: tuple[bool, list[str]]
**Description**: 
        Validate that user inputs are properly wrapped.

        Args:
            messages: List of message dictionaries

        Returns:
            Tuple of (is_valid, issues)
        



## Function: create_hardened_prompt

**Parameters**: self, system_prompt, user_input, canary
**Returns**: tuple[str, str, CanaryToken]
**Description**: 
        Create a fully hardened prompt with canary and wrapped input.

        Args:
            system_prompt: System prompt to harden
            user_input: User input to wrap
            canary: Optional existing canary

        Returns:
            Tuple of (hardened_system_prompt, wrapped_user_input, canary)
        



## Function: clear_canary

**Parameters**: self, canary
**Returns**: None
**Description**: Remove a canary token from active use.



## Function: get_active_canaries

**Parameters**: self
**Returns**: list[CanaryToken]
**Description**: Get list of all active canary tokens.



## Usage Examples

### Class Usage

```python
# Using CanaryToken
canarytoken = CanaryToken()
```

```python
# Using CanaryDefense
canarydefense = CanaryDefense()
canarydefense.generate_canary()
canarydefense.inject_canary()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using generate_canary
result = generate_canary(purpose)
```

```python
# Using inject_canary
result = inject_canary(system_prompt, canary)
```



---
**Generated**: 2026-03-26T09:39:04.781805
**Type**: api_reference
**Quality**: comprehensive
