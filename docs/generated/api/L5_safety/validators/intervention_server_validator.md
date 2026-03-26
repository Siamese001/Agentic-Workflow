# API Documentation: intervention_server_validator

**Target Audience**: developers, api_users

# intervention_server_validator API Documentation

**File**: `intervention_server_validator.py`
**Classes**: 2
**Functions**: 7

## Classes

- **InterventionContext**
- **InterventionServer**

## Functions

- **check_intervention_required** -> tuple[bool, list[str]]
- **get_intervention_server** -> InterventionServer
- **to_dict** -> dict[str, Any]
- **__init__** -> None
- **_setup_app** -> None
- **check_telepathy** -> str | None
- **parse_telepathy_commands** -> dict[str, Any]


## Class: InterventionContext

**Description**: Context for human intervention decision.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for API response.



## Class: InterventionServer

**Description**: 
    Human-in-the-Loop intervention server.

    Provides:
    - Web UI for human approval/veto
    - API endpoints for programmatic control
    - Async event synchronization
    - Telepathy interface for instruction files

    Canon Validator Pattern:
        if high_risk or (many_modifications and strategic_plan):
            start_intervention_server(ctx)
            await approval_event.wait()
            if "VETOED" in ctx.signals:
                break
    

### Methods

#### __init__
**Parameters**: self, host, port, instructions_path
**Returns**: None
**Description**: 
        Initialize the intervention server.

        Args:
            host: Server host address
            port: Server port
            instructions_path: Path to human instructions file (telepathy)
        

#### _setup_app
**Parameters**: self
**Returns**: None
**Description**: Setup FastAPI application with endpoints.

#### check_telepathy
**Parameters**: self
**Returns**: str | None
**Description**: 
        Check for human instructions via telepathy file.

        Canon Validator Pattern:
            instruction_file = Path("observability/human_instructions.md")
            if instruction_file.exists():
                instructions = instruction_file.read_text().strip()
        

#### parse_telepathy_commands
**Parameters**: self, instructions
**Returns**: dict[str, Any]
**Description**: Parse telepathy instructions for commands.



## Function: check_intervention_required

**Parameters**: cycle, modified_count, signals, quality_score, high_risk_threshold, signal_threshold
**Returns**: tuple[bool, list[str]]
**Description**: 
    Check if human intervention is required based on Canon Validator thresholds.

    Args:
        cycle: Current cycle number
        modified_count: Number of modified items
        signals: List of active signal names
        quality_score: Optional quality score
        high_risk_threshold: Modified count threshold
        signal_threshold: Signal count threshold

    Returns:
        Tuple of (intervention_required, risk_factors)
    



## Function: get_intervention_server

**Parameters**: host, port
**Returns**: InterventionServer
**Description**: Get or create the global InterventionServer instance.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for API response.



## Function: __init__

**Parameters**: self, host, port, instructions_path
**Returns**: None
**Description**: 
        Initialize the intervention server.

        Args:
            host: Server host address
            port: Server port
            instructions_path: Path to human instructions file (telepathy)
        



## Function: _setup_app

**Parameters**: self
**Returns**: None
**Description**: Setup FastAPI application with endpoints.



## Function: check_telepathy

**Parameters**: self
**Returns**: str | None
**Description**: 
        Check for human instructions via telepathy file.

        Canon Validator Pattern:
            instruction_file = Path("observability/human_instructions.md")
            if instruction_file.exists():
                instructions = instruction_file.read_text().strip()
        



## Function: parse_telepathy_commands

**Parameters**: self, instructions
**Returns**: dict[str, Any]
**Description**: Parse telepathy instructions for commands.



## Usage Examples

### Class Usage

```python
# Using InterventionContext
interventioncontext = InterventionContext()
interventioncontext.to_dict()
```

```python
# Using InterventionServer
interventionserver = InterventionServer()
interventionserver.check_telepathy()
interventionserver.parse_telepathy_commands()
```

### Function Usage

```python
# Using check_intervention_required
result = check_intervention_required(cycle, modified_count)
```

```python
# Using get_intervention_server
result = get_intervention_server(host, port)
```

```python
# Using to_dict
result = to_dict()
```



---
**Generated**: 2026-03-26T09:39:05.832282
**Type**: api_reference
**Quality**: comprehensive
