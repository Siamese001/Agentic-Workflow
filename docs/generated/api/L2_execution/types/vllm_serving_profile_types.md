# API Documentation: vllm_serving_profile_types

**Target Audience**: developers, api_users

# vllm_serving_profile_types API Documentation

**File**: `vllm_serving_profile_types.py`
**Classes**: 3
**Functions**: 5

## Classes

- **VLLMServingProfile**
- **VLLMServingProfileInvalid** (inherits from Exception)
- **VLLMCoChangeViolation** (inherits from Exception)

## Functions

- **assert_no_simultaneous_increase** -> None
- **get_profile** -> VLLMServingProfile
- **__post_init__** -> None
- **__init__** -> None
- **__init__** -> None


## Class: VLLMServingProfile

**Description**: Immutable serving profile for a vLLM tier.

    Validated at construction time. Startup fails on invalid config.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: VLLMServingProfileInvalid

**Description**: Raised when a serving profile fails validation.

    Triggers hard fail at startup — never silently ignored.
    

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, profile, reason
**Returns**: None



## Class: VLLMCoChangeViolation

**Description**: Raised when max_model_len and max_num_seqs both increase simultaneously.

    This invariant prevents KV-cache OOM on 32GB GPU.
    

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, profile, old_max_model_len, new_max_model_len, old_max_num_seqs, new_max_num_seqs
**Returns**: None



## Function: assert_no_simultaneous_increase

**Parameters**: old_max_model_len, new_max_model_len, old_max_num_seqs, new_max_num_seqs, profile_name
**Returns**: None
**Description**: Enforce: max_model_len and max_num_seqs cannot both increase in same commit.

    Args:
        old_max_model_len: Previous max_model_len value.
        new_max_model_len: Proposed new max_model_len value.
        old_max_num_seqs: Previous max_num_seqs value.
        new_max_num_seqs: Proposed new max_num_seqs value.
        profile_name: Profile name for error reporting.

    Raises:
        VLLMCoChangeViolation: If both values increase simultaneously.
    



## Function: get_profile

**Parameters**: tier
**Returns**: VLLMServingProfile
**Description**: Retrieve serving profile by tier name.

    Args:
        tier: Tier name ("local_fast" or "local_strong").

    Returns:
        VLLMServingProfile for the requested tier.

    Raises:
        KeyError: If tier is not in SERVING_PROFILE_REGISTRY.
    



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __init__

**Parameters**: self, profile, reason
**Returns**: None


## Function: __init__

**Parameters**: self, profile, old_max_model_len, new_max_model_len, old_max_num_seqs, new_max_num_seqs
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using VLLMServingProfile
vllmservingprofile = VLLMServingProfile()
```

```python
# Using VLLMServingProfileInvalid
vllmservingprofileinvalid = VLLMServingProfileInvalid()
```

```python
# Using VLLMCoChangeViolation
vllmcochangeviolation = VLLMCoChangeViolation()
```

### Function Usage

```python
# Using assert_no_simultaneous_increase
result = assert_no_simultaneous_increase(old_max_model_len, new_max_model_len)
```

```python
# Using get_profile
result = get_profile(tier)
```

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:04.039383
**Type**: api_reference
**Quality**: comprehensive
