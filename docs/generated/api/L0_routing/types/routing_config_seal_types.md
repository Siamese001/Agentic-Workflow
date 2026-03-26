# API Documentation: routing_config_seal_types

**Target Audience**: developers, api_users

# routing_config_seal_types API Documentation

**File**: `routing_config_seal_types.py`
**Classes**: 3
**Functions**: 5

## Classes

- **RoutingConfigSealViolation** (inherits from RuntimeError)
- **RoutingConfigSeal**
- **SealedRoutingContext**

## Functions

- **create** -> RoutingConfigSeal
- **verify** -> bool
- **__init__** -> None
- **seal** -> RoutingConfigSeal
- **verify_or_raise** -> None


## Class: RoutingConfigSealViolation

**Description**: Raised when routing config is mutated after sealing.

**Inherits from**: RuntimeError



## Class: RoutingConfigSeal

**Description**: Immutable seal over a routing configuration snapshot.

    Once sealed, the config hash must remain constant for the
    duration of the run.  Verification re-derives the hash and
    compares.
    

### Methods

#### create
**Returns**: RoutingConfigSeal
**Description**: Seal a routing config snapshot.

#### verify
**Parameters**: self, config
**Returns**: bool
**Description**: Verify config has not changed since sealing.



## Class: SealedRoutingContext

**Description**: Context manager that enforces routing config immutability.

    Usage::

        ctx = SealedRoutingContext(config, version="1.0")
        ctx.verify_or_raise(config)  # ok
        config["new_key"] = "value"
        ctx.verify_or_raise(config)  # raises
    

### Methods

#### __init__
**Parameters**: self, config
**Returns**: None

#### seal
**Parameters**: self
**Returns**: RoutingConfigSeal

#### verify_or_raise
**Parameters**: self, config
**Returns**: None
**Description**: Raise if config has been mutated since sealing.



## Function: create

**Returns**: RoutingConfigSeal
**Description**: Seal a routing config snapshot.



## Function: verify

**Parameters**: self, config
**Returns**: bool
**Description**: Verify config has not changed since sealing.



## Function: __init__

**Parameters**: self, config
**Returns**: None


## Function: seal

**Parameters**: self
**Returns**: RoutingConfigSeal


## Function: verify_or_raise

**Parameters**: self, config
**Returns**: None
**Description**: Raise if config has been mutated since sealing.



## Usage Examples

### Class Usage

```python
# Using RoutingConfigSealViolation
routingconfigsealviolation = RoutingConfigSealViolation()
```

```python
# Using RoutingConfigSeal
routingconfigseal = RoutingConfigSeal()
routingconfigseal.create()
routingconfigseal.verify()
```

```python
# Using SealedRoutingContext
sealedroutingcontext = SealedRoutingContext()
sealedroutingcontext.seal()
sealedroutingcontext.verify_or_raise()
```

### Function Usage

```python
# Using create
result = create()
```

```python
# Using verify
result = verify(config)
```

```python
# Using __init__
result = __init__(config)
```



---
**Generated**: 2026-03-26T09:39:03.468498
**Type**: api_reference
**Quality**: comprehensive
