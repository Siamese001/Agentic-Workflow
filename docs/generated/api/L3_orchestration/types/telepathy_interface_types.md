# API Documentation: telepathy_interface_types

**Target Audience**: developers, api_users

# telepathy_interface_types API Documentation

**File**: `telepathy_interface_types.py`
**Classes**: 1
**Functions**: 7

## Classes

- **TelepathyInterface**

## Functions

- **get_telepathy_interface** -> TelepathyInterface
- **__init__**
- **check_instructions** -> str | None
- **parse_instructions** -> dict[str, Any]
- **consume_instructions** -> None
- **inject_into_context** -> Any
- **clear_instructions** -> None


## Class: TelepathyInterface

**Description**: 
    Human instruction telepathy interface for dynamic mission control.

    Watches observability/human_instructions.md for commands and injects
    them into the execution context to alter mission behavior.
    

### Methods

#### __init__
**Parameters**: self, instructions_path
**Description**: 
        Initialize the telepathy interface.

        Args:
            instructions_path: Path to the human instructions file
        

#### check_instructions
**Parameters**: self, cycle
**Returns**: str | None
**Description**: 
        Check for new human instructions.

        Args:
            cycle: Current mission cycle

        Returns:
            Instruction text if found, None otherwise
        

#### parse_instructions
**Parameters**: self, instructions
**Returns**: dict[str, Any]
**Description**: 
        Parse human instructions into executable commands.

        Args:
            instructions: Raw instruction text

        Returns:
            Dictionary of parsed commands and signals
        

#### consume_instructions
**Parameters**: self, instructions
**Returns**: None
**Description**: 
        Mark instructions as consumed to prevent re-processing.

        Args:
            instructions: The instructions that were consumed
        

#### inject_into_context
**Parameters**: self, context, commands
**Returns**: Any
**Description**: 
        Inject parsed commands into execution context.

        Args:
            context: Current execution context
            commands: Parsed commands from telepathy

        Returns:
            Modified context with injected commands
        

#### clear_instructions
**Parameters**: self
**Returns**: None
**Description**: Clear the instructions file.



## Function: get_telepathy_interface

**Parameters**: instructions_path
**Returns**: TelepathyInterface
**Description**: Get or create the global telepathy interface instance.



## Function: __init__

**Parameters**: self, instructions_path
**Description**: 
        Initialize the telepathy interface.

        Args:
            instructions_path: Path to the human instructions file
        



## Function: check_instructions

**Parameters**: self, cycle
**Returns**: str | None
**Description**: 
        Check for new human instructions.

        Args:
            cycle: Current mission cycle

        Returns:
            Instruction text if found, None otherwise
        



## Function: parse_instructions

**Parameters**: self, instructions
**Returns**: dict[str, Any]
**Description**: 
        Parse human instructions into executable commands.

        Args:
            instructions: Raw instruction text

        Returns:
            Dictionary of parsed commands and signals
        



## Function: consume_instructions

**Parameters**: self, instructions
**Returns**: None
**Description**: 
        Mark instructions as consumed to prevent re-processing.

        Args:
            instructions: The instructions that were consumed
        



## Function: inject_into_context

**Parameters**: self, context, commands
**Returns**: Any
**Description**: 
        Inject parsed commands into execution context.

        Args:
            context: Current execution context
            commands: Parsed commands from telepathy

        Returns:
            Modified context with injected commands
        



## Function: clear_instructions

**Parameters**: self
**Returns**: None
**Description**: Clear the instructions file.



## Usage Examples

### Class Usage

```python
# Using TelepathyInterface
telepathyinterface = TelepathyInterface()
telepathyinterface.check_instructions()
telepathyinterface.parse_instructions()
```

### Function Usage

```python
# Using get_telepathy_interface
result = get_telepathy_interface(instructions_path)
```

```python
# Using __init__
result = __init__(instructions_path)
```

```python
# Using check_instructions
result = check_instructions(cycle)
```



---
**Generated**: 2026-03-26T09:39:04.419948
**Type**: api_reference
**Quality**: comprehensive
