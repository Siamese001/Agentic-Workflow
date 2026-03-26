# API Documentation: assembly_stage

**Target Audience**: developers, api_users

# assembly_stage API Documentation

**File**: `assembly_stage.py`
**Classes**: 2
**Functions**: 5

## Classes

- **GovernedPayload**
- **AirlockAssembler**

## Functions

- **canonical_bytes** -> bytes
- **__post_init__**
- **_sanitize** -> str
- **_shred** -> tuple[str, ...]
- **assemble** -> GovernedPayload


## Class: GovernedPayload

**Description**: 
    Immutable governed payload with assembly stage slots.

    Slots are ordered S0→D0→I0→C0→U0 for deterministic manifest hashing.
    

### Methods

#### __post_init__
**Parameters**: self



## Class: AirlockAssembler

**Description**: 
    Assembly stage for composing governed payloads with deterministic hashing.

    Implements the Assembly Stage (GAP-03) with stable slot composition
    and deterministic manifest hashing.
    

### Methods

#### _sanitize
**Parameters**: u0_user_prompt
**Returns**: str
**Description**: 
        Deterministic minimal sanitizer for user prompts.

        Performs exact, deterministic substitutions only - no ML or fuzzy matching.

        Args:
            u0_user_prompt: Raw user prompt text

        Returns:
            Sanitized user prompt text
        

#### _shred
**Parameters**: u0_user_prompt
**Returns**: tuple[str, ...]
**Description**: 
        Deterministic shred of user prompt into atomic intent check IDs.

        Splits by common intent delimiters and returns lexicographically sorted IDs.

        Args:
            u0_user_prompt: User prompt text to shred

        Returns:
            Tuple of stable, lexicographically sorted check IDs
        

#### assemble
**Returns**: GovernedPayload
**Description**: 
        Assemble a governed payload from component slots.

        Performs sanitization first, then shredding, then computes manifest hash.

        Args:
            s0_system: System prompt slot
            d0_injections: Reserved injection slot (default empty)
            i0_instructional: Instructional prompt slot
            c0_context: Context slot
            u0_user_prompt: User prompt slot

        Returns:
            GovernedPayload with deterministic manifest hash
        



## Function: canonical_bytes

**Parameters**: data
**Returns**: bytes
**Description**: 
    Convert a dictionary to canonical JSON bytes for deterministic hashing.

    Args:
        data: Dictionary to canonicalize

    Returns:
        Deterministic bytes representation
    



## Function: __post_init__

**Parameters**: self


## Function: _sanitize

**Parameters**: u0_user_prompt
**Returns**: str
**Description**: 
        Deterministic minimal sanitizer for user prompts.

        Performs exact, deterministic substitutions only - no ML or fuzzy matching.

        Args:
            u0_user_prompt: Raw user prompt text

        Returns:
            Sanitized user prompt text
        



## Function: _shred

**Parameters**: u0_user_prompt
**Returns**: tuple[str, ...]
**Description**: 
        Deterministic shred of user prompt into atomic intent check IDs.

        Splits by common intent delimiters and returns lexicographically sorted IDs.

        Args:
            u0_user_prompt: User prompt text to shred

        Returns:
            Tuple of stable, lexicographically sorted check IDs
        



## Function: assemble

**Returns**: GovernedPayload
**Description**: 
        Assemble a governed payload from component slots.

        Performs sanitization first, then shredding, then computes manifest hash.

        Args:
            s0_system: System prompt slot
            d0_injections: Reserved injection slot (default empty)
            i0_instructional: Instructional prompt slot
            c0_context: Context slot
            u0_user_prompt: User prompt slot

        Returns:
            GovernedPayload with deterministic manifest hash
        



## Usage Examples

### Class Usage

```python
# Using GovernedPayload
governedpayload = GovernedPayload()
```

```python
# Using AirlockAssembler
airlockassembler = AirlockAssembler()
airlockassembler.assemble()
```

### Function Usage

```python
# Using canonical_bytes
result = canonical_bytes(data)
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using _sanitize
result = _sanitize(u0_user_prompt)
```



---
**Generated**: 2026-03-26T09:39:02.651608
**Type**: api_reference
**Quality**: comprehensive
