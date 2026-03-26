# API Documentation: sovereign_policy_registry_enforcer

**Target Audience**: developers, api_users

# sovereign_policy_registry_enforcer API Documentation

**File**: `sovereign_policy_registry_enforcer.py`
**Classes**: 3
**Functions**: 1

## Classes

- **PolicySeverity** (inherits from Enum)
- **SovereignPolicy**
- **SovereignPolicyRegistry**

## Functions

- **get_all**


## Class: PolicySeverity

**Inherits from**: Enum



## Class: SovereignPolicy



## Class: SovereignPolicyRegistry

**Description**: 
    The Immutable Constitution of the Agentic Core.
    Defines what IS allowed, independent of HOW it is checked.
    

### Methods

#### get_all
**Parameters**: cls



## Function: get_all

**Parameters**: cls


## Usage Examples

### Class Usage

```python
# Using PolicySeverity
policyseverity = PolicySeverity()
```

```python
# Using SovereignPolicy
sovereignpolicy = SovereignPolicy()
```

```python
# Using SovereignPolicyRegistry
sovereignpolicyregistry = SovereignPolicyRegistry()
sovereignpolicyregistry.get_all()
```

### Function Usage

```python
# Using get_all
result = get_all(cls)
```



---
**Generated**: 2026-03-26T09:39:04.940651
**Type**: api_reference
**Quality**: comprehensive
