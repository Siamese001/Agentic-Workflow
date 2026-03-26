# API Documentation: routing_contracts_types

**Target Audience**: developers, api_users

# routing_contracts_types API Documentation

**File**: `routing_contracts_types.py`
**Classes**: 14
**Functions**: 48

## Classes

- **LawSlotHandler**
- **PolicyConfigGuard**
- **PolicyMutationIncident** (inherits from Exception)
- **PolicyAlignmentResult**
- **GuardrailGuard**
- **ArtifactAbsenceFailure** (inherits from Exception)
- **MetaGuardianResult**
- **HealingTransactionBoundary**
- **ResultEmissionViolation** (inherits from Exception)
- **RouteRecoveryBox**
- **PipeOrderViolation** (inherits from Exception)
- **PipeOrderEnforcer**
- **TieredVigilanceMonitor**
- **TelemetryEmitter**

## Functions

- **static_policy_alignment_check** -> PolicyAlignmentResult
- **enforce_artifact_presence** -> None
- **enforce_route_decision_presence** -> None
- **meta_guardian_check** -> MetaGuardianResult
- **aggregate_gate_check** -> bool
- **validate_result_emission** -> None
- **_deterministic_bytes** -> bytes
- **__init__** -> None
- **register_twin** -> None
- **freeze** -> None
- **acquire_slot** -> Any
- **depletion_tracker** -> CapabilityDepletionTracker
- **__init__** -> None
- **policy_hash** -> str
- **read_config** -> dict[str, Any]
- **__init__** -> None
- **check_budget** -> bool
- **check_payload_integrity** -> bool
- **check_safety_markers** -> bool
- **check_boundary_tokens** -> bool
- **enforce_all** -> bool
- **__init__** -> None
- **__init__** -> None
- **__enter__** -> HealingTransactionBoundary
- **__exit__** -> bool
- **commit** -> None
- **committed** -> bool
- **rolled_back** -> bool
- **__init__** -> None
- **__init__** -> None
- **handle_overflow** -> str
- **attempts** -> int
- **__init__** -> None
- **__init__** -> None
- **advance** -> int
- **current_step** -> int
- **is_complete** -> bool
- **__init__** -> None
- **escalate** -> EvacuationProtocol | None
- **current_tier** -> VigilanceTier
- **evacuated** -> bool
- **__init__** -> None
- **emit_incident** -> None
- **emit_result** -> None
- **emit_route_decision** -> None
- **emit_typed_artifact** -> None
- **flush_to_artifacts_dir** -> Any
- **events** -> list[dict[str, Any]]


## Class: LawSlotHandler

**Description**: §3.6 — Enforces tool isolation via read-only twins.

    Direct reference to live tool instances is PROHIBITED.
    The Slot Handler enforces Capability Depletion tracking (§15.4).
    

### Methods

#### __init__
**Parameters**: self, trace_id, total_slots
**Returns**: None

#### register_twin
**Parameters**: self, tool_name, read_only_twin
**Returns**: None
**Description**: Register a read-only twin for a tool. Live instances are rejected.

#### freeze
**Parameters**: self
**Returns**: None
**Description**: Freeze registrations — no further twins may be added.

#### acquire_slot
**Parameters**: self, tool_name
**Returns**: Any
**Description**: Acquire a tool slot via read-only twin. Fail-closed on depletion.

#### depletion_tracker
**Parameters**: self
**Returns**: CapabilityDepletionTracker



## Class: PolicyConfigGuard

**Description**: §4.1/§4.3 — Enforces policy immutability within a healing wave.

    Read-once: policy_config hash is captured at wave start.
    Any mutation detected during the wave raises a critical incident.
    

### Methods

#### __init__
**Parameters**: self, policy_config, wave_id
**Returns**: None

#### policy_hash
**Parameters**: self
**Returns**: str

#### read_config
**Parameters**: self, current_config
**Returns**: dict[str, Any]
**Description**: Read policy config. Fail-closed if mutated since wave start.



## Class: PolicyMutationIncident

**Description**: §4.3 — Critical incident: policy_config mutated during healing wave.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, wave_id, expected_hash, actual_hash
**Returns**: None



## Class: PolicyAlignmentResult

**Description**: §6.4 — Result of static policy alignment check.



## Class: GuardrailGuard

**Description**: §7.3 — Unified guardrail guard enforcing four sub-checks.

    All checks are fail-closed: any failure blocks progression.
    

### Methods

#### check_budget
**Parameters**: self, token_cap
**Returns**: bool
**Description**: Budget Guard: tokens within budget.

#### check_payload_integrity
**Parameters**: self, payload_hash, expected_hash
**Returns**: bool
**Description**: Payload Integrity (Plast): hash match required.

#### check_safety_markers
**Parameters**: self, markers
**Returns**: bool
**Description**: Safety Markers: all required markers must be present.

#### check_boundary_tokens
**Parameters**: self, boundary_token
**Returns**: bool
**Description**: Boundary Tokens: fast-fail on missing/empty token.

#### enforce_all
**Parameters**: self, token_cap, payload_hash, expected_hash, markers, boundary_token
**Returns**: bool
**Description**: Run all four guards. Fail-closed: any single failure = block.



## Class: ArtifactAbsenceFailure

**Description**: §7.5 — Automatic failure when a required artifact is absent.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, artifact_name
**Returns**: None



## Class: MetaGuardianResult

**Description**: §7.6 — Meta-Guardian enforcement result.



## Class: HealingTransactionBoundary

**Description**: §10.1 — All healing occurs inside a transactional boundary.

    Fail-closed: any exception triggers rollback and prevents partial state.
    

### Methods

#### __init__
**Parameters**: self, trace_id
**Returns**: None

#### __enter__
**Parameters**: self
**Returns**: HealingTransactionBoundary

#### __exit__
**Parameters**: self, exc_type, exc_val, exc_tb
**Returns**: bool

#### commit
**Parameters**: self
**Returns**: None
**Description**: Explicitly commit the transaction.

#### committed
**Parameters**: self
**Returns**: bool

#### rolled_back
**Parameters**: self
**Returns**: bool



## Class: ResultEmissionViolation

**Description**: §10.4 — RESULT emitted from unauthorized layer.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, layer
**Returns**: None



## Class: RouteRecoveryBox

**Description**: §11.2 — TokenOverflow events trigger retry/downgrade, not hard crash.

### Methods

#### __init__
**Parameters**: self, trace_id, max_retries
**Returns**: None

#### handle_overflow
**Parameters**: self, tokens_requested, budget_limit
**Returns**: str
**Description**: Handle TokenOverflow. Returns action: 'retry', 'downgrade', or 'reject'.

#### attempts
**Parameters**: self
**Returns**: int



## Class: PipeOrderViolation

**Description**: §2.5 — Pipe order violation detected.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, expected, actual, step
**Returns**: None



## Class: PipeOrderEnforcer

**Description**: §2.5 — Enforces strict healer pipe order (1..10). No reordering allowed.

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### advance
**Parameters**: self, step_name
**Returns**: int
**Description**: Advance to next pipe step. Fail-closed on wrong order.

#### current_step
**Parameters**: self
**Returns**: int

#### is_complete
**Parameters**: self
**Returns**: bool



## Class: TieredVigilanceMonitor

**Description**: §15.1 — Tiered Vigilance Strategy with Evacuation Protocol.

    Tier I: Budget/Token Drains (Dashboard Signature)
    Tier II: Anomalous Presence (Exclusive Dynamic Probes)
    Tier III: Evacuation Alert Engage (Emergency Exfiltration/Shutdown)
    

### Methods

#### __init__
**Parameters**: self, trace_id
**Returns**: None

#### escalate
**Parameters**: self, tier, reason
**Returns**: EvacuationProtocol | None
**Description**: Escalate to a tier. Tier III triggers evacuation.

#### current_tier
**Parameters**: self
**Returns**: VigilanceTier

#### evacuated
**Parameters**: self
**Returns**: bool



## Class: TelemetryEmitter

**Description**: §15.6 — All INCIDENT and RESULT artifacts must emit telemetry events.

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### emit_incident
**Parameters**: self, incident
**Returns**: None
**Description**: Emit telemetry for INCIDENT artifact.

#### emit_result
**Parameters**: self, result
**Returns**: None
**Description**: Emit telemetry for RESULT artifact.

#### emit_route_decision
**Parameters**: self, artifact
**Returns**: None
**Description**: Emit telemetry for ROUTE_DECISION artifact (§3.1 durable sink).

#### emit_typed_artifact
**Parameters**: self, type_label, artifact
**Returns**: None
**Description**: Emit telemetry for any typed dataclass artifact (§Wave2.1 generic sink).

#### flush_to_artifacts_dir
**Parameters**: self, artifacts_dir
**Returns**: Any
**Description**: Persist all buffered events as NDJSON to *artifacts_dir*.

        File: ``telemetry_events.ndjson`` (one JSON object per line).
        Follows the same mkdir-then-write pattern as ``write_guardian_result``.

        Returns:
            Path to the written file, or *None* if there are no events.
        

#### events
**Parameters**: self
**Returns**: list[dict[str, Any]]



## Function: static_policy_alignment_check

**Parameters**: trace_id, policy_hash, context, policy_rules
**Returns**: PolicyAlignmentResult
**Description**: §6.4 — Execute static policy alignment check. Fail-closed on violation.



## Function: enforce_artifact_presence

**Parameters**: artifact, artifact_name
**Returns**: None
**Description**: §7.5 — Fail-closed: absence of artifact is automatic failure.



## Function: enforce_route_decision_presence

**Parameters**: audit_payload
**Returns**: None
**Description**: §3.1 — Under V15, downstream validation requires a RouteDecisionArtifact.

    Fail-closed: if V15 is enforced and the artifact is missing or None,
    raise V15HardFailAbort.  Non-V15 behaviour is unchanged (no-op).
    



## Function: meta_guardian_check

**Parameters**: total_invariants, covered_invariants, threshold
**Returns**: MetaGuardianResult
**Description**: §7.6 — Meta-Guardian: enforce ≥95% invariant coverage.



## Function: aggregate_gate_check

**Parameters**: aggregate
**Returns**: bool
**Description**: §7.7 — Guardian validates AGGREGATE before L2 heal admission.

    Fail-closed: None or missing required fields = reject.
    



## Function: validate_result_emission

**Parameters**: layer
**Returns**: None
**Description**: §10.4 — RESULT may only be emitted by L2 after successful heal.

    L0/L5/L6 cannot write RESULT or HEALING_PLAN.
    



## Function: _deterministic_bytes

**Parameters**: obj
**Returns**: bytes
**Description**: Produce deterministic bytes for hashing (sorted keys).



## Function: __init__

**Parameters**: self, trace_id, total_slots
**Returns**: None


## Function: register_twin

**Parameters**: self, tool_name, read_only_twin
**Returns**: None
**Description**: Register a read-only twin for a tool. Live instances are rejected.



## Function: freeze

**Parameters**: self
**Returns**: None
**Description**: Freeze registrations — no further twins may be added.



## Function: acquire_slot

**Parameters**: self, tool_name
**Returns**: Any
**Description**: Acquire a tool slot via read-only twin. Fail-closed on depletion.



## Function: depletion_tracker

**Parameters**: self
**Returns**: CapabilityDepletionTracker


## Function: __init__

**Parameters**: self, policy_config, wave_id
**Returns**: None


## Function: policy_hash

**Parameters**: self
**Returns**: str


## Function: read_config

**Parameters**: self, current_config
**Returns**: dict[str, Any]
**Description**: Read policy config. Fail-closed if mutated since wave start.



## Function: __init__

**Parameters**: self, wave_id, expected_hash, actual_hash
**Returns**: None


## Function: check_budget

**Parameters**: self, token_cap
**Returns**: bool
**Description**: Budget Guard: tokens within budget.



## Function: check_payload_integrity

**Parameters**: self, payload_hash, expected_hash
**Returns**: bool
**Description**: Payload Integrity (Plast): hash match required.



## Function: check_safety_markers

**Parameters**: self, markers
**Returns**: bool
**Description**: Safety Markers: all required markers must be present.



## Function: check_boundary_tokens

**Parameters**: self, boundary_token
**Returns**: bool
**Description**: Boundary Tokens: fast-fail on missing/empty token.



## Function: enforce_all

**Parameters**: self, token_cap, payload_hash, expected_hash, markers, boundary_token
**Returns**: bool
**Description**: Run all four guards. Fail-closed: any single failure = block.



## Function: __init__

**Parameters**: self, artifact_name
**Returns**: None


## Function: __init__

**Parameters**: self, trace_id
**Returns**: None


## Function: __enter__

**Parameters**: self
**Returns**: HealingTransactionBoundary


## Function: __exit__

**Parameters**: self, exc_type, exc_val, exc_tb
**Returns**: bool


## Function: commit

**Parameters**: self
**Returns**: None
**Description**: Explicitly commit the transaction.



## Function: committed

**Parameters**: self
**Returns**: bool


## Function: rolled_back

**Parameters**: self
**Returns**: bool


## Function: __init__

**Parameters**: self, layer
**Returns**: None


## Function: __init__

**Parameters**: self, trace_id, max_retries
**Returns**: None


## Function: handle_overflow

**Parameters**: self, tokens_requested, budget_limit
**Returns**: str
**Description**: Handle TokenOverflow. Returns action: 'retry', 'downgrade', or 'reject'.



## Function: attempts

**Parameters**: self
**Returns**: int


## Function: __init__

**Parameters**: self, expected, actual, step
**Returns**: None


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: advance

**Parameters**: self, step_name
**Returns**: int
**Description**: Advance to next pipe step. Fail-closed on wrong order.



## Function: current_step

**Parameters**: self
**Returns**: int


## Function: is_complete

**Parameters**: self
**Returns**: bool


## Function: __init__

**Parameters**: self, trace_id
**Returns**: None


## Function: escalate

**Parameters**: self, tier, reason
**Returns**: EvacuationProtocol | None
**Description**: Escalate to a tier. Tier III triggers evacuation.



## Function: current_tier

**Parameters**: self
**Returns**: VigilanceTier


## Function: evacuated

**Parameters**: self
**Returns**: bool


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: emit_incident

**Parameters**: self, incident
**Returns**: None
**Description**: Emit telemetry for INCIDENT artifact.



## Function: emit_result

**Parameters**: self, result
**Returns**: None
**Description**: Emit telemetry for RESULT artifact.



## Function: emit_route_decision

**Parameters**: self, artifact
**Returns**: None
**Description**: Emit telemetry for ROUTE_DECISION artifact (§3.1 durable sink).



## Function: emit_typed_artifact

**Parameters**: self, type_label, artifact
**Returns**: None
**Description**: Emit telemetry for any typed dataclass artifact (§Wave2.1 generic sink).



## Function: flush_to_artifacts_dir

**Parameters**: self, artifacts_dir
**Returns**: Any
**Description**: Persist all buffered events as NDJSON to *artifacts_dir*.

        File: ``telemetry_events.ndjson`` (one JSON object per line).
        Follows the same mkdir-then-write pattern as ``write_guardian_result``.

        Returns:
            Path to the written file, or *None* if there are no events.
        



## Function: events

**Parameters**: self
**Returns**: list[dict[str, Any]]


## Usage Examples

### Class Usage

```python
# Using LawSlotHandler
lawslothandler = LawSlotHandler()
lawslothandler.register_twin()
lawslothandler.freeze()
```

```python
# Using PolicyConfigGuard
policyconfigguard = PolicyConfigGuard()
policyconfigguard.policy_hash()
policyconfigguard.read_config()
```

```python
# Using PolicyMutationIncident
policymutationincident = PolicyMutationIncident()
```

### Function Usage

```python
# Using static_policy_alignment_check
result = static_policy_alignment_check(trace_id, policy_hash)
```

```python
# Using enforce_artifact_presence
result = enforce_artifact_presence(artifact, artifact_name)
```

```python
# Using enforce_route_decision_presence
result = enforce_route_decision_presence(audit_payload)
```



---
**Generated**: 2026-03-26T09:39:03.475619
**Type**: api_reference
**Quality**: comprehensive
