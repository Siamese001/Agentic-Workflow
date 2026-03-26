# API Documentation: replay_bundle_emitter

**Target Audience**: developers, api_users

# replay_bundle_emitter API Documentation

**File**: `replay_bundle_emitter.py`
**Classes**: 0
**Functions**: 1


## Functions

- **emit_replay_bundle** -> ReplayBundle


## Function: emit_replay_bundle

**Parameters**: mission_id, execution_start_tick, execution_end_tick, manifest_hash, active_config_hashes, store
**Returns**: ReplayBundle
**Description**: 
    Build and persist a ReplayBundle to the L4 SSOT store.

    Returns the persisted ReplayBundle (with stable replay_hash).
    Non-mutating to knowledge index.
    



## Usage Examples

### Function Usage

```python
# Using emit_replay_bundle
result = emit_replay_bundle(mission_id, execution_start_tick)
```



---
**Generated**: 2026-03-26T09:39:04.541725
**Type**: api_reference
**Quality**: comprehensive
