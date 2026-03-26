# API Documentation: metrics_emission

**Target Audience**: developers, api_users

# metrics_emission API Documentation

**File**: `metrics_emission.py`
**Classes**: 7
**Functions**: 19

## Classes

- **EmissionRecord**
- **BlastRadiusConfig**
- **ActivationFlags**
- **MetricsEmissionEnforcer**
- **BlastRadiusEnforcer**
- **PhaseLockStore**
- **ActivationFlagsStore**

## Functions

- **single_authoritative_emission** -> None
- **validate_blast_radius** -> bool
- **persist_phase_lock** -> None
- **restore_phase_lock** -> dict | None
- **persist_activation_flags** -> None
- **restore_activation_flags** -> ActivationFlags | None
- **__new__** -> 'MetricsEmissionEnforcer'
- **single_authoritative_emission** -> None
- **_calculate_blast_radius** -> int
- **verify_emission_chokepoint** -> bool
- **clear_emissions_for_trace** -> None
- **__init__**
- **validate_blast_radius** -> bool
- **_calculate_proposal_radius** -> int
- **persist** -> None
- **restore** -> dict | None
- **is_locked** -> bool
- **persist_flags** -> None
- **restore_flags** -> ActivationFlags | None


## Class: EmissionRecord

**Description**: Record of a metrics emission to prevent duplicates.



## Class: BlastRadiusConfig

**Description**: Configuration for blast radius containment.



## Class: ActivationFlags

**Description**: L4-persisted, signed, replay-bound activation flags for Wave 16.



## Class: MetricsEmissionEnforcer

**Description**: Enforces single authoritative metrics emission and blast radius containment.

### Methods

#### __new__
**Parameters**: cls
**Returns**: 'MetricsEmissionEnforcer'

#### single_authoritative_emission
**Parameters**: self, trace_id, artifact_type, artifact
**Returns**: None
**Description**: Single control-spine chokepoint for all metrics emissions.

        Args:
            trace_id: Execution trace identifier
            artifact_type: Type of metric artifact being emitted
            artifact: The artifact being emitted

        Raises:
            RuntimeError: If duplicate emission detected
            ValueError: If blast radius exceeded
        

#### _calculate_blast_radius
**Parameters**: self, artifact
**Returns**: int
**Description**: Calculate deterministic blast radius bound to explicit state surface.

        Args:
            artifact: The artifact to calculate blast radius for

        Returns:
            Integer blast radius value
        

#### verify_emission_chokepoint
**Parameters**: self, trace_id, artifact_type
**Returns**: bool
**Description**: Verify that emission went through the authorized chokepoint.

        Args:
            trace_id: Execution trace identifier
            artifact_type: Type of metric artifact

        Returns:
            True if emission was authorized, False otherwise
        

#### clear_emissions_for_trace
**Parameters**: self, trace_id
**Returns**: None
**Description**: Clear emission records for a specific trace (for testing/cleanup).

        Args:
            trace_id: Trace ID to clear records for
        



## Class: BlastRadiusEnforcer

**Description**: Enforces blast radius containment for meta-learning proposals.

### Methods

#### __init__
**Parameters**: self, config

#### validate_blast_radius
**Parameters**: self, proposal, state_surface_bytes
**Returns**: bool
**Description**: Validate that proposal blast radius is within limits.

        Args:
            proposal: Meta-learning proposal to validate
            state_surface_bytes: Size of state surface in bytes

        Returns:
            True if blast radius is acceptable

        Raises:
            ValueError: If blast radius exceeds limits
        

#### _calculate_proposal_radius
**Parameters**: self, proposal
**Returns**: int
**Description**: Deterministic blast radius calculation for proposals.

        Args:
            proposal: Proposal to calculate radius for

        Returns:
            Integer blast radius
        



## Class: PhaseLockStore

**Description**: Persists and restores phase lock state in L4.

### Methods

#### persist
**Parameters**: self, phase, locked, metadata
**Returns**: None
**Description**: Persist phase lock state to L4 storage.

        Args:
            phase: Phase number to lock
            locked: Whether the phase is locked
            metadata: Optional metadata to store with lock
        

#### restore
**Parameters**: self
**Returns**: dict | None
**Description**: Restore phase lock state from L4 storage.

        Returns:
            Lock data dictionary or None if not found
        

#### is_locked
**Parameters**: self, phase
**Returns**: bool
**Description**: Check if a specific phase is locked.

        Args:
            phase: Phase number to check

        Returns:
            True if phase is locked
        



## Class: ActivationFlagsStore

**Description**: Manages L4-persisted, signed, replay-bound activation flags.

### Methods

#### persist_flags
**Parameters**: self, flags
**Returns**: None
**Description**: Persist activation flags to L4 with signature.

        Args:
            flags: Activation flags to persist
        

#### restore_flags
**Parameters**: self
**Returns**: ActivationFlags | None
**Description**: Restore activation flags from L4.

        Returns:
            ActivationFlags or None if not found
        



## Function: single_authoritative_emission

**Parameters**: trace_id, artifact_type, artifact
**Returns**: None
**Description**: Exported function for single authoritative emission.



## Function: validate_blast_radius

**Parameters**: proposal, state_surface_bytes
**Returns**: bool
**Description**: Exported function for blast radius validation.



## Function: persist_phase_lock

**Parameters**: phase, locked, metadata
**Returns**: None
**Description**: Exported function for phase lock persistence.



## Function: restore_phase_lock

**Returns**: dict | None
**Description**: Exported function for phase lock restoration.



## Function: persist_activation_flags

**Parameters**: flags
**Returns**: None
**Description**: Exported function for activation flags persistence.



## Function: restore_activation_flags

**Returns**: ActivationFlags | None
**Description**: Exported function for activation flags restoration.



## Function: __new__

**Parameters**: cls
**Returns**: 'MetricsEmissionEnforcer'


## Function: single_authoritative_emission

**Parameters**: self, trace_id, artifact_type, artifact
**Returns**: None
**Description**: Single control-spine chokepoint for all metrics emissions.

        Args:
            trace_id: Execution trace identifier
            artifact_type: Type of metric artifact being emitted
            artifact: The artifact being emitted

        Raises:
            RuntimeError: If duplicate emission detected
            ValueError: If blast radius exceeded
        



## Function: _calculate_blast_radius

**Parameters**: self, artifact
**Returns**: int
**Description**: Calculate deterministic blast radius bound to explicit state surface.

        Args:
            artifact: The artifact to calculate blast radius for

        Returns:
            Integer blast radius value
        



## Function: verify_emission_chokepoint

**Parameters**: self, trace_id, artifact_type
**Returns**: bool
**Description**: Verify that emission went through the authorized chokepoint.

        Args:
            trace_id: Execution trace identifier
            artifact_type: Type of metric artifact

        Returns:
            True if emission was authorized, False otherwise
        



## Function: clear_emissions_for_trace

**Parameters**: self, trace_id
**Returns**: None
**Description**: Clear emission records for a specific trace (for testing/cleanup).

        Args:
            trace_id: Trace ID to clear records for
        



## Function: __init__

**Parameters**: self, config


## Function: validate_blast_radius

**Parameters**: self, proposal, state_surface_bytes
**Returns**: bool
**Description**: Validate that proposal blast radius is within limits.

        Args:
            proposal: Meta-learning proposal to validate
            state_surface_bytes: Size of state surface in bytes

        Returns:
            True if blast radius is acceptable

        Raises:
            ValueError: If blast radius exceeds limits
        



## Function: _calculate_proposal_radius

**Parameters**: self, proposal
**Returns**: int
**Description**: Deterministic blast radius calculation for proposals.

        Args:
            proposal: Proposal to calculate radius for

        Returns:
            Integer blast radius
        



## Function: persist

**Parameters**: self, phase, locked, metadata
**Returns**: None
**Description**: Persist phase lock state to L4 storage.

        Args:
            phase: Phase number to lock
            locked: Whether the phase is locked
            metadata: Optional metadata to store with lock
        



## Function: restore

**Parameters**: self
**Returns**: dict | None
**Description**: Restore phase lock state from L4 storage.

        Returns:
            Lock data dictionary or None if not found
        



## Function: is_locked

**Parameters**: self, phase
**Returns**: bool
**Description**: Check if a specific phase is locked.

        Args:
            phase: Phase number to check

        Returns:
            True if phase is locked
        



## Function: persist_flags

**Parameters**: self, flags
**Returns**: None
**Description**: Persist activation flags to L4 with signature.

        Args:
            flags: Activation flags to persist
        



## Function: restore_flags

**Parameters**: self
**Returns**: ActivationFlags | None
**Description**: Restore activation flags from L4.

        Returns:
            ActivationFlags or None if not found
        



## Usage Examples

### Class Usage

```python
# Using EmissionRecord
emissionrecord = EmissionRecord()
```

```python
# Using BlastRadiusConfig
blastradiusconfig = BlastRadiusConfig()
```

```python
# Using ActivationFlags
activationflags = ActivationFlags()
```

### Function Usage

```python
# Using single_authoritative_emission
result = single_authoritative_emission(trace_id, artifact_type)
```

```python
# Using validate_blast_radius
result = validate_blast_radius(proposal, state_surface_bytes)
```

```python
# Using persist_phase_lock
result = persist_phase_lock(phase, locked)
```



---
**Generated**: 2026-03-26T09:39:04.504581
**Type**: api_reference
**Quality**: comprehensive
