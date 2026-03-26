# API Documentation: pii_vault_enforcer

**Target Audience**: developers, api_users

# pii_vault_enforcer API Documentation

**File**: `pii_vault_enforcer.py`
**Classes**: 1
**Functions**: 3

## Classes

- **PiiVault**

## Functions

- **__init__**
- **tokenize** -> str
- **restore** -> str


## Class: PiiVault

**Description**: 
    L5 Safety: The Secret Vault.
    Handles tokenization and de-tokenization of sensitive data.
    

### Methods

#### __init__
**Parameters**: self, config

#### tokenize
**Parameters**: self, trace_id, text
**Returns**: str
**Description**: Swaps real PII for safe tokens.

#### restore
**Parameters**: self, trace_id, text
**Returns**: str
**Description**: Restores real data from tokens after the LLM is done.



## Function: __init__

**Parameters**: self, config


## Function: tokenize

**Parameters**: self, trace_id, text
**Returns**: str
**Description**: Swaps real PII for safe tokens.



## Function: restore

**Parameters**: self, trace_id, text
**Returns**: str
**Description**: Restores real data from tokens after the LLM is done.



## Usage Examples

### Class Usage

```python
# Using PiiVault
piivault = PiiVault()
piivault.tokenize()
piivault.restore()
```

### Function Usage

```python
# Using __init__
result = __init__(config)
```

```python
# Using tokenize
result = tokenize(trace_id, text)
```

```python
# Using restore
result = restore(trace_id, text)
```



---
**Generated**: 2026-03-26T09:39:04.890690
**Type**: api_reference
**Quality**: comprehensive
