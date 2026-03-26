# API Documentation: capability_registry

**Target Audience**: developers, api_users

# capability_registry API Documentation

**File**: `capability_registry.py`
**Classes**: 13
**Functions**: 31

## Classes

- **CapabilityNotFoundError** (inherits from LookupError)
- **CapabilityPermissionError** (inherits from PermissionError)
- **UnregisteredAgentError** (inherits from RuntimeError)
- **ExclusiveCapabilityConflictError** (inherits from RuntimeError)
- **RegistryVersionError** (inherits from RuntimeError)
- **UnregisteredDispatchError** (inherits from RuntimeError)
- **CapabilityOwnership** (inherits from str, Enum)
- **CapabilityRegistryEntry**
- **CapabilityToken**
- **CapabilityDecision**
- **RunContext**
- **CapabilityRegistry**
- **CapabilityDecisionStore**

## Functions

- **resolve_agent_for_capability** -> CapabilityDecision
- **get_capability_registry** -> CapabilityRegistry
- **get_capability_decision_store** -> CapabilityDecisionStore
- **reset_capability_registry** -> None
- **reset_capability_decision_store** -> None
- **_sha256** -> str
- **__post_init__** -> None
- **allows_caller** -> bool
- **has_capability** -> bool
- **meets_policy** -> bool
- **create** -> CapabilityToken
- **create** -> RunContext
- **__init__** -> None
- **register** -> int
- **deactivate** -> int
- **is_registered** -> bool
- **get_entry** -> CapabilityRegistryEntry | None
- **agents_for_capability** -> list[CapabilityRegistryEntry]
- **capability_owner** -> CapabilityRegistryEntry | None
- **all_capabilities** -> list[str]
- **all_agents** -> list[str]
- **registry_version** -> int
- **version_history** -> list[tuple[int, str]]
- **_exclusive_owners** -> list[str]
- **__init__** -> None
- **ingest** -> None
- **by_run_id** -> list[CapabilityDecision]
- **by_capability** -> list[CapabilityDecision]
- **by_agent** -> list[CapabilityDecision]
- **all_decisions** -> list[CapabilityDecision]
- **unresolved_dispatches** -> list[CapabilityDecision]


## Class: CapabilityNotFoundError

**Description**: Raised when no registered agent has the requested capability.

    Gate A enforcement: dispatch without registry resolution fails.
    

**Inherits from**: LookupError



## Class: CapabilityPermissionError

**Description**: Raised when caller is not in allowed_callers for the capability.

    Gate B enforcement: capability token must have resolved_agent_id.
    

**Inherits from**: PermissionError



## Class: UnregisteredAgentError

**Description**: Raised when selected agent is not in CapabilityRegistry.

    Gate C enforcement: unregistered agents must not do production work.
    

**Inherits from**: RuntimeError



## Class: ExclusiveCapabilityConflictError

**Description**: Raised when multiple agents claim exclusive ownership without shared policy.

    Gate D enforcement: exclusive capability conflicts must be explicit.
    

**Inherits from**: RuntimeError



## Class: RegistryVersionError

**Description**: Raised on illegal registry mutation without version increment.

    Gate E enforcement: capability changes must be versioned.
    

**Inherits from**: RuntimeError



## Class: UnregisteredDispatchError

**Description**: Raised when dispatch bypasses registry resolution.

    Gate A enforcement: all dispatches must go through resolve_agent_for_capability().
    

**Inherits from**: RuntimeError



## Class: CapabilityOwnership

**Description**: How execution ownership is held for a capability.

**Inherits from**: str, Enum



## Class: CapabilityRegistryEntry

**Description**: Registry entry for one versioned agent capability declaration.

    Spec §2 fields (10 required):
        agent_id, agent_version, layer, capability_set,
        allowed_callers, action_classes, policy_requirements,
        human_review_requirement, owner_team, active_status
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### allows_caller
**Parameters**: self, caller_agent_id
**Returns**: bool
**Description**: Wildcard '*' allows all callers.

#### has_capability
**Parameters**: self, capability_name
**Returns**: bool

#### meets_policy
**Parameters**: self, policy_hash
**Returns**: bool



## Class: CapabilityToken

**Description**: Typed token issued on every successful capability resolution.

    Spec §4 fields: capability_name, capability_token, resolved_agent_id.
    Also carries trace_id for ADG binding.
    

### Methods

#### create
**Parameters**: cls
**Returns**: CapabilityToken



## Class: CapabilityDecision

**Description**: Result of resolve_agent_for_capability() — bound to trace.



## Class: RunContext

**Description**: Minimal run context for capability resolution.

### Methods

#### create
**Parameters**: cls, run_id, trace_id, policy_hash
**Returns**: RunContext



## Class: CapabilityRegistry

**Description**: Thread-safe agent capability registry.

    Spec §1: the central directory mapping agents to capabilities.
    Spec §5: exposes ownership, sharing, and parallelizability.
    Spec §6: every mutation increments registry_version.

    Only registered agents may execute. Dispatch must go through
    resolve_agent_for_capability() — no direct agent lookup allowed.
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### register
**Parameters**: self, entry, reason
**Returns**: int
**Description**: Register or update an agent entry. Returns new registry_version.

#### deactivate
**Parameters**: self, agent_id, reason
**Returns**: int
**Description**: Mark agent inactive. Returns new registry_version.

#### is_registered
**Parameters**: self, agent_id
**Returns**: bool

#### get_entry
**Parameters**: self, agent_id
**Returns**: CapabilityRegistryEntry | None

#### agents_for_capability
**Parameters**: self, capability_name
**Returns**: list[CapabilityRegistryEntry]
**Description**: Return all active entries that declare this capability.

#### capability_owner
**Parameters**: self, capability_name
**Returns**: CapabilityRegistryEntry | None
**Description**: Return the SINGLETON owner of a capability, or None if shared/absent.

#### all_capabilities
**Parameters**: self
**Returns**: list[str]
**Description**: Return sorted list of all declared capabilities.

#### all_agents
**Parameters**: self
**Returns**: list[str]

#### registry_version
**Parameters**: self
**Returns**: int

#### version_history
**Parameters**: self
**Returns**: list[tuple[int, str]]

#### _exclusive_owners
**Parameters**: self, capability_name
**Returns**: list[str]



## Class: CapabilityDecisionStore

**Description**: In-memory queryable store for all issued CapabilityDecision records.

### Methods

#### __init__
**Parameters**: self
**Returns**: None

#### ingest
**Parameters**: self, decision
**Returns**: None

#### by_run_id
**Parameters**: self, run_id
**Returns**: list[CapabilityDecision]

#### by_capability
**Parameters**: self, capability_name
**Returns**: list[CapabilityDecision]

#### by_agent
**Parameters**: self, agent_id
**Returns**: list[CapabilityDecision]

#### all_decisions
**Parameters**: self
**Returns**: list[CapabilityDecision]

#### unresolved_dispatches
**Parameters**: self
**Returns**: list[CapabilityDecision]
**Description**: Decisions where resolved_agent_id is empty (Gate B violation).



## Function: resolve_agent_for_capability

**Parameters**: capability_name, caller_agent_id, run_context
**Returns**: CapabilityDecision
**Description**: Mandatory capability resolution entrypoint — P2/L3 spec §3.

    Steps (in order, all mandatory):
      1. query CapabilityRegistry for capability_name
      2. validate caller permission (allowed_callers check)
      3. return eligible target agents
      4. bind capability decision to trace (issues_capability_token ADG edge)
      5. reject unregistered or unauthorized matches

    Args:
        capability_name:   The capability being requested.
        caller_agent_id:   Agent making the dispatch request.
        run_context:       RunContext carrying run_id, trace_id, policy_hash.
        registry:          CapabilityRegistry to consult (uses global if None).
        preferred_agent_id: Optional hint for which agent to select.

    Returns:
        CapabilityDecision with CapabilityToken and resolved_agent_id.

    Raises:
        CapabilityNotFoundError:     No registered agent has this capability.
        CapabilityPermissionError:   Caller not in allowed_callers.
        UnregisteredAgentError:      preferred_agent_id not in registry.
    



## Function: get_capability_registry

**Returns**: CapabilityRegistry
**Description**: Return the process-level CapabilityRegistry singleton.



## Function: get_capability_decision_store

**Returns**: CapabilityDecisionStore
**Description**: Return the process-level CapabilityDecisionStore singleton.



## Function: reset_capability_registry

**Returns**: None
**Description**: Reset global registry (for testing).



## Function: reset_capability_decision_store

**Returns**: None
**Description**: Reset global store (for testing).



## Function: _sha256

**Parameters**: value
**Returns**: str


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: allows_caller

**Parameters**: self, caller_agent_id
**Returns**: bool
**Description**: Wildcard '*' allows all callers.



## Function: has_capability

**Parameters**: self, capability_name
**Returns**: bool


## Function: meets_policy

**Parameters**: self, policy_hash
**Returns**: bool


## Function: create

**Parameters**: cls
**Returns**: CapabilityToken


## Function: create

**Parameters**: cls, run_id, trace_id, policy_hash
**Returns**: RunContext


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: register

**Parameters**: self, entry, reason
**Returns**: int
**Description**: Register or update an agent entry. Returns new registry_version.



## Function: deactivate

**Parameters**: self, agent_id, reason
**Returns**: int
**Description**: Mark agent inactive. Returns new registry_version.



## Function: is_registered

**Parameters**: self, agent_id
**Returns**: bool


## Function: get_entry

**Parameters**: self, agent_id
**Returns**: CapabilityRegistryEntry | None


## Function: agents_for_capability

**Parameters**: self, capability_name
**Returns**: list[CapabilityRegistryEntry]
**Description**: Return all active entries that declare this capability.



## Function: capability_owner

**Parameters**: self, capability_name
**Returns**: CapabilityRegistryEntry | None
**Description**: Return the SINGLETON owner of a capability, or None if shared/absent.



## Function: all_capabilities

**Parameters**: self
**Returns**: list[str]
**Description**: Return sorted list of all declared capabilities.



## Function: all_agents

**Parameters**: self
**Returns**: list[str]


## Function: registry_version

**Parameters**: self
**Returns**: int


## Function: version_history

**Parameters**: self
**Returns**: list[tuple[int, str]]


## Function: _exclusive_owners

**Parameters**: self, capability_name
**Returns**: list[str]


## Function: __init__

**Parameters**: self
**Returns**: None


## Function: ingest

**Parameters**: self, decision
**Returns**: None


## Function: by_run_id

**Parameters**: self, run_id
**Returns**: list[CapabilityDecision]


## Function: by_capability

**Parameters**: self, capability_name
**Returns**: list[CapabilityDecision]


## Function: by_agent

**Parameters**: self, agent_id
**Returns**: list[CapabilityDecision]


## Function: all_decisions

**Parameters**: self
**Returns**: list[CapabilityDecision]


## Function: unresolved_dispatches

**Parameters**: self
**Returns**: list[CapabilityDecision]
**Description**: Decisions where resolved_agent_id is empty (Gate B violation).



## Usage Examples

### Class Usage

```python
# Using CapabilityNotFoundError
capabilitynotfounderror = CapabilityNotFoundError()
```

```python
# Using CapabilityPermissionError
capabilitypermissionerror = CapabilityPermissionError()
```

```python
# Using UnregisteredAgentError
unregisteredagenterror = UnregisteredAgentError()
```

### Function Usage

```python
# Using resolve_agent_for_capability
result = resolve_agent_for_capability(capability_name, caller_agent_id)
```

```python
# Using get_capability_registry
result = get_capability_registry()
```

```python
# Using get_capability_decision_store
result = get_capability_decision_store()
```



---
**Generated**: 2026-03-26T09:39:04.341659
**Type**: api_reference
**Quality**: comprehensive
