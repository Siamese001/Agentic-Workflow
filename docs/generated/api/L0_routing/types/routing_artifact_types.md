# API Documentation: routing_artifact_types

**Target Audience**: developers, api_users

# routing_artifact_types API Documentation

**File**: `routing_artifact_types.py`
**Classes**: 18
**Functions**: 6

## Classes

- **RoutingRationale** (inherits from str, Enum)
- **RoutePath** (inherits from str, Enum)
- **RouteDecisionArtifact**
- **TokenGateResult** (inherits from str, Enum)
- **TokenCapArtifact**
- **PermsArtifact**
- **SeverityEnum** (inherits from str, Enum)
- **SelfHealingTrigger**
- **AggregateArtifact**
- **ResultArtifact**
- **IncidentArtifact**
- **TokenControlArtifact**
- **VigilanceTier** (inherits from str, Enum)
- **EvacuationProtocol**
- **CapabilityDepletionTracker**
- **PolicyConfigSnapshot**
- **HealingPlan**
- **StaleWriteIncident**

## Functions

- **__post_init__** -> None
- **__post_init__** -> None
- **depletion_rate** -> float
- **consume_slot** -> bool
- **__post_init__** -> None
- **__post_init__** -> None


## Class: RoutingRationale

**Description**: §3.2 — Rationale restricted to a finite enum. Free-form prose is invalid.

**Inherits from**: str, Enum



## Class: RoutePath

**Description**: §3.3 — Routing paths strictly defined (5 paths).

**Inherits from**: str, Enum



## Class: RouteDecisionArtifact

**Description**: §3.1 — Typed RouteDecision artifact with all 7 required fields.



## Class: TokenGateResult

**Description**: Gate result for TokenCap enforcement.

**Inherits from**: str, Enum



## Class: TokenCapArtifact

**Description**: §11.1 — TokenCap enforcement artifact. Emitted before any LLM call.



## Class: PermsArtifact

**Description**: §11.1 — Perms artifact passed to agent with budget authorization.



## Class: SeverityEnum

**Description**: Severity levels for incidents and triggers.

**Inherits from**: str, Enum



## Class: SelfHealingTrigger

**Description**: §5.4 — L6 emits to L2 to trigger healing from observability signals.



## Class: AggregateArtifact

**Description**: §2.8 — AGGREGATE emitted on conditional flows (L2 pre-heal).



## Class: ResultArtifact

**Description**: §10.4 — RESULT emitted exclusively by L2 after successful heal.

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: IncidentArtifact

**Description**: §15.6 — INCIDENT with mandatory telemetry event emission.



## Class: TokenControlArtifact

**Description**: §6.3 — Emitted PRIOR to LLM submission. Token-bounded (<=300 tokens).

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: VigilanceTier

**Description**: §15.1 — Monitoring is strictly stratified into three tiers.

**Inherits from**: str, Enum



## Class: EvacuationProtocol

**Description**: §15.1 — Tier III Evacuation Alert Engage (freeze + exfiltration path).



## Class: CapabilityDepletionTracker

**Description**: §15.4 — Tracks tool slot depletion rate.

### Methods

#### depletion_rate
**Parameters**: self
**Returns**: float

#### consume_slot
**Parameters**: self, tool_name
**Returns**: bool
**Description**: Consume a tool slot. Returns False if depleted (fail-closed).



## Class: PolicyConfigSnapshot

**Description**: §4.1 — Immutable snapshot of policy_config taken at wave start.



## Class: HealingPlan

**Description**: §1.7 — Typed HealingPlan artifact with all required fields.

    Represents a structured healing plan that L2 agents produce
    and L0/L5/L6 cannot write.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Class: StaleWriteIncident

**Description**: §2.5 — Typed StaleWriteIncident for hash-mismatch detection.

    Emitted when a healer attempts to write to a file whose hash
    has changed since the boundary snapshot was taken.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: depletion_rate

**Parameters**: self
**Returns**: float


## Function: consume_slot

**Parameters**: self, tool_name
**Returns**: bool
**Description**: Consume a tool slot. Returns False if depleted (fail-closed).



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using RoutingRationale
routingrationale = RoutingRationale()
```

```python
# Using RoutePath
routepath = RoutePath()
```

```python
# Using RouteDecisionArtifact
routedecisionartifact = RouteDecisionArtifact()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using depletion_rate
result = depletion_rate()
```



---
**Generated**: 2026-03-26T09:39:03.466662
**Type**: api_reference
**Quality**: comprehensive
