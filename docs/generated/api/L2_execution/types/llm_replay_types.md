# API Documentation: llm_replay_types

**Target Audience**: developers, api_users

# llm_replay_types API Documentation

**File**: `llm_replay_types.py`
**Classes**: 3
**Functions**: 9

## Classes

- **ReplayMode** (inherits from <ast.Attribute object at 0x000001CBFADD5790>)
- **ReplayBundle**
- **LLMReplayStrategy**

## Functions

- **is_authoritative** -> bool
- **mode_label** -> str
- **verify_replay_integrity** -> bool
- **validate_production_mode** -> None
- **create** -> ReplayBundle
- **verify_checksum** -> bool
- **replay** -> bytes
- **is_authoritative** -> bool
- **governance_label** -> str


## Class: ReplayMode

**Description**: LLM replay mode policy.

    RECORDED_OUTPUT: Default for production. Uses stored raw
        response bytes verbatim.
    DETERMINISTIC_INFERENCE: Dev/test only. Re-invokes the LLM
        with temperature=0 + seed. Labeled NON_AUTHORITATIVE.
    

**Inherits from**: enum.Enum



## Class: ReplayBundle

**Description**: Immutable bundle of LLM interaction artifacts for replay.

    All fields are pinned at capture time and frozen.
    

### Methods

#### create
**Returns**: ReplayBundle
**Description**: Construct a bundle with computed checksums.

#### verify_checksum
**Parameters**: self
**Returns**: bool
**Description**: Re-derive provider checksum and compare.



## Class: LLMReplayStrategy

**Description**: Strategy for replaying an LLM interaction.

    Combines the replay bundle with the mode policy.
    

### Methods

#### replay
**Parameters**: self
**Returns**: bytes
**Description**: Execute the replay strategy.

        RECORDED_OUTPUT: return stored raw_response_bytes.
        DETERMINISTIC_INFERENCE: raise (not implemented in
            production — requires explicit dev/test wiring).
        

#### is_authoritative
**Parameters**: self
**Returns**: bool

#### governance_label
**Parameters**: self
**Returns**: str



## Function: is_authoritative

**Parameters**: mode
**Returns**: bool
**Description**: Only RECORDED_OUTPUT is authoritative for governance.



## Function: mode_label

**Parameters**: mode
**Returns**: str
**Description**: Return the governance label for a replay mode.



## Function: verify_replay_integrity

**Parameters**: bundle
**Returns**: bool
**Description**: Re-derive replay_hash and verify bundle integrity.

    Returns True only if the re-derived hash matches the
    stored replay_hash.
    



## Function: validate_production_mode

**Parameters**: mode
**Returns**: None
**Description**: Raise if mode is not allowed in production.



## Function: create

**Returns**: ReplayBundle
**Description**: Construct a bundle with computed checksums.



## Function: verify_checksum

**Parameters**: self
**Returns**: bool
**Description**: Re-derive provider checksum and compare.



## Function: replay

**Parameters**: self
**Returns**: bytes
**Description**: Execute the replay strategy.

        RECORDED_OUTPUT: return stored raw_response_bytes.
        DETERMINISTIC_INFERENCE: raise (not implemented in
            production — requires explicit dev/test wiring).
        



## Function: is_authoritative

**Parameters**: self
**Returns**: bool


## Function: governance_label

**Parameters**: self
**Returns**: str


## Usage Examples

### Class Usage

```python
# Using ReplayMode
replaymode = ReplayMode()
```

```python
# Using ReplayBundle
replaybundle = ReplayBundle()
replaybundle.create()
replaybundle.verify_checksum()
```

```python
# Using LLMReplayStrategy
llmreplaystrategy = LLMReplayStrategy()
llmreplaystrategy.replay()
llmreplaystrategy.is_authoritative()
```

### Function Usage

```python
# Using is_authoritative
result = is_authoritative(mode)
```

```python
# Using mode_label
result = mode_label(mode)
```

```python
# Using verify_replay_integrity
result = verify_replay_integrity(bundle)
```



---
**Generated**: 2026-03-26T09:39:03.976647
**Type**: api_reference
**Quality**: comprehensive
