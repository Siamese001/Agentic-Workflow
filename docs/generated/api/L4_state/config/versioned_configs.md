# API Documentation: versioned_configs

**Target Audience**: developers, api_users

# versioned_configs API Documentation

**File**: `versioned_configs.py`
**Classes**: 6
**Functions**: 14

## Classes

- **PolicyConfig**
- **RoutingConfig**
- **ModelConfig**
- **BudgetConfig**
- **L4ActiveConfigs**
- **MLCacheConfig**

## Functions

- **_sha256** -> str
- **get_active_configs** -> L4ActiveConfigs
- **get_ml_cache_config** -> MLCacheConfig
- **canonical_bytes** -> bytes
- **config_hash** -> str
- **canonical_bytes** -> bytes
- **config_hash** -> str
- **canonical_bytes** -> bytes
- **config_hash** -> str
- **canonical_bytes** -> bytes
- **config_hash** -> str
- **hashes** -> dict[str, str]
- **canonical_bytes** -> bytes
- **config_hash** -> str


## Class: PolicyConfig

**Description**: Tool allowlist, file scope, and budget policy.

### Methods

#### canonical_bytes
**Parameters**: self
**Returns**: bytes

#### config_hash
**Parameters**: self
**Returns**: str



## Class: RoutingConfig

**Description**: Mode routing thresholds and escalation parameters.

### Methods

#### canonical_bytes
**Parameters**: self
**Returns**: bytes

#### config_hash
**Parameters**: self
**Returns**: str



## Class: ModelConfig

**Description**: Model name/version used by cognition and embedding.

### Methods

#### canonical_bytes
**Parameters**: self
**Returns**: bytes

#### config_hash
**Parameters**: self
**Returns**: str



## Class: BudgetConfig

**Description**: Token budget ceilings, retry ceilings, max_k.

### Methods

#### canonical_bytes
**Parameters**: self
**Returns**: bytes

#### config_hash
**Parameters**: self
**Returns**: str



## Class: L4ActiveConfigs

**Description**: 
    L4 SSOT registry of active versioned configs.

    This is the single authoritative source consulted by L2.0 validation.
    

### Methods

#### hashes
**Parameters**: self
**Returns**: dict[str, str]



## Class: MLCacheConfig

**Description**: Versioned ML cache policy: TTL, max entries, eviction mode.

### Methods

#### canonical_bytes
**Parameters**: self
**Returns**: bytes

#### config_hash
**Parameters**: self
**Returns**: str



## Function: _sha256

**Parameters**: data
**Returns**: str


## Function: get_active_configs

**Returns**: L4ActiveConfigs
**Description**: Return the module-level L4 SSOT active config registry.



## Function: get_ml_cache_config

**Returns**: MLCacheConfig
**Description**: Return the module-level ML cache config singleton.



## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes


## Function: config_hash

**Parameters**: self
**Returns**: str


## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes


## Function: config_hash

**Parameters**: self
**Returns**: str


## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes


## Function: config_hash

**Parameters**: self
**Returns**: str


## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes


## Function: config_hash

**Parameters**: self
**Returns**: str


## Function: hashes

**Parameters**: self
**Returns**: dict[str, str]


## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes


## Function: config_hash

**Parameters**: self
**Returns**: str


## Usage Examples

### Class Usage

```python
# Using PolicyConfig
policyconfig = PolicyConfig()
policyconfig.canonical_bytes()
policyconfig.config_hash()
```

```python
# Using RoutingConfig
routingconfig = RoutingConfig()
routingconfig.canonical_bytes()
routingconfig.config_hash()
```

```python
# Using ModelConfig
modelconfig = ModelConfig()
modelconfig.canonical_bytes()
modelconfig.config_hash()
```

### Function Usage

```python
# Using _sha256
result = _sha256(data)
```

```python
# Using get_active_configs
result = get_active_configs()
```

```python
# Using get_ml_cache_config
result = get_ml_cache_config()
```



---
**Generated**: 2026-03-26T09:39:04.476693
**Type**: api_reference
**Quality**: comprehensive
