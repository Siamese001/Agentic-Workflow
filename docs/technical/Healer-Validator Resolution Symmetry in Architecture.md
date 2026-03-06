# Healer-Validator Resolution Symmetry in Architecture

## Overview

The healer-validator resolution symmetry describes the architectural contract ensuring that every mutation produced by a healing agent can be independently verified by a validation agent using the same AST-based analysis primitives. Healing and validation are symmetric operations over the same code surface — healer produces a candidate diff; validator confirms structural correctness using `VerificationGate` before the write is committed.

---

## Symmetry Contract

```
Healing Agent (L5)
    │  produces candidate change
    ▼
VerificationGate (L5)
    │  AST-verifies: import, function, class, method, variable presence
    │  confirms write-set is declared and within bounds
    ▼
UniversalWriteGateway (L2)
    │  executes write only on ALLOW decision
    ▼
HashChainAuditLog (L2)
    │  appends sealed AuditEntry (prev_hash chained)
    ▼
DeterminismDigestEmitter (L6)
    │  emits once per execution — detects duplicate emission
    ▼
ExecutionTrace → sealed with hash_chain_root, policy_hash, prev_hash
```

The validator **cannot** approve a write it cannot structurally verify. The healer **cannot** bypass `WriteSetEnforcer` without a prior declaration of the write set.

---

## VerificationGate — L5 AST Validator

**File:** `agentic_core/L5_safety/enforcement/verification_gate.py`

`VerificationGate(HallucinationDetectionMixin, SovereignBaseAgent)` — the single structural arbiter for all proposed mutations.

| Method | Description |
|---|---|
| `verify_action(action)` | Top-level entry: dispatches to type-specific verifiers |
| `_verify_target_in_ast(file, target)` | Parses file AST and routes to sub-verifier |
| `_verify_import_exists(tree, target)` | Confirms import statement is present |
| `_verify_function_exists(tree, target)` | Confirms function definition at module scope |
| `_verify_class_exists(tree, target)` | Confirms class definition |
| `_verify_variable_exists(tree, target)` | Confirms module-level assignment |
| `_verify_method_exists(tree, class, method)` | Confirms method within a named class |
| `_verify_any_node_exists(tree, target)` | Fallback: any node matching name |
| `verify_modification(file, old_sig, new_sig)` | Pre/post structural signature comparison |
| `_map_violation_to_action(violation)` | Maps detected violation type to remediation action |
| `_extract_target_from_violation(violation)` | Extracts target symbol from violation context |
| `clear_cache()` / `get_cache_stats()` | LRU cache management for parsed ASTs |
| `heal(context)` | Self-healing entry point (inherits from `SovereignBaseAgent`) |

All verification methods use `ast.parse` — no regex, no string search.

---

## Write-Set Enforcer — L2 Structural Boundary

**File:** `agentic_core/L2_execution/enforcement/write_set_enforcer.py`

`WriteSetEnforcer` (dataclass) enforces that every write performed during an agent execution was declared before the agent started.

| Field | Type | Description |
|---|---|---|
| `declared_write_set` | `frozenset[str]` | Paths declared at envelope creation time |
| `_actual_writes` | `set[str]` | Accumulates paths written during execution |
| `_aborted` | `bool` | Set on first violation; blocks further writes |

`WriteSetViolation(RuntimeError)` — raised when an undeclared path is written. The execution is aborted immediately; no partial write is committed.

---

## Capability Token — Authorization Before Write

**File:** `agentic_core/L2_execution/types/capability_token_types.py`

A `CapabilityTokenArtifact` must be issued and checked before any write operation.

`CapabilityTokenArtifact` dataclass fields:
- `artifact_type: Literal['CAPABILITY_TOKEN']`
- `semantic_clock: SemanticClockSnapshot`
- `trace_id: str`
- `subject: CapabilityTokenSubject` — `kind` and `id` of the requesting agent
- `issued_by: str`
- `permissions: tuple[str, ...]`
- `constraints: CapabilityConstraints` — `allowed_paths` and `max_tool_calls`
- `policy_config_hash: str | None`

`CapabilityDecisionArtifact` records the ALLOW/DENY decision with `deny_reason`.

`CapabilityEnforcer` enforces per-execution:
- `issue_token(subject, permissions, constraints)` — issues a single-use token
- `check(tool_name, resource_path)` — validates against `allowed_paths` patterns
- `authorize_and_execute(fn, ...)` — combined authorize + execute with call-count tracking
- `decisions` — full audit log of all ALLOW/DENY events

`CapabilityChokepoint` (`agentic_core/L2_execution/enforcement/capability_chokepoint.py`) is the singleton gate that all capability tokens pass through:
- `issue_token(...)` — delegates to `CapabilityEnforcer`
- `authorize_and_execute(fn, ...)` — single dispatch point
- `freeze()` — permanently locks further token issuance (used at phase boundary)

---

## L2 Boundary Verifier

**File:** `agentic_core/L2_execution/enforcement/boundary_verifier.py`

`L2BoundaryVerifier` validates that all incoming instruction packets and sandbox envelopes are correctly formed and L5-certified before execution begins.

| Method | Description |
|---|---|
| `verify_instruction_packet(packet)` | Structural packet validation |
| `verify_l5_certification(cert)` | Checks L5 signature on certification artifact |
| `verify_instruction_packet_with_l5(packet, cert)` | Combined validation |
| `verify_packet(packet)` | Alias for packet-only path |
| `verify_envelope(envelope)` | Validates `SandboxEnvelope` structure and signature |
| `verify_sandbox_envelope(envelope)` | Full sandbox envelope integrity check |
| `is_packet_valid(packet)` / `is_l5_certified(cert)` | Boolean fast-path helpers |
| `is_packet_valid_with_l5(packet, cert)` | Combined boolean check |
| `is_envelope_valid(envelope)` | Envelope boolean check |

---

## Provider Substitution Guard

**File:** `agentic_core/L2_execution/enforcement/provider_substitution_prohibition.py`

Prevents a healing agent from silently substituting a different LLM provider than what was declared in the capability token.

`ProviderRequest` dataclass: `provider`, `model`, `agent_id`, `request_id`.

`ProviderSubstitutionGuard`:
- `register_request(req)` — registers the declared provider before invocation
- `validate_response(response, req_id)` — confirms the responding provider matches
- `handle_failure(req_id, error)` — records failure without substituting
- `clear_request(req_id)` — cleanup after completion

`ProviderSubstitutionViolation(Exception)` — raised when the response provider does not match the declared request provider.

---

## Provider Binding Determinism

**File:** `agentic_core/L2_execution/enforcement/provider_binding_determinism.py`

`ProviderBindingContext` dataclass — sealed context that pins the exact provider, model, gateway version, and semantic clock vector for every LLM call:

- `provider_id: str`
- `model_id: str`
- `gateway_version: str`
- `semantic_clock_vector: dict[str, int]`

Changes to any field produce a different `replay_key`, making provider drift detectable in replay.

---

## Network Egress Guard

**File:** `agentic_core/L2_execution/enforcement/network_egress_guard.py`

`NetworkEgressViolation(Exception)` — raised when an agent attempts an outbound network call that was not declared in its capability token. This is the symmetric counterpart to `WriteSetViolation` for network access.

---

## Tool Policy Enforcer

**File:** `agentic_core/L2_execution/enforcement/tool_policy_enforcer.py`

`ToolPolicyEnforcer` — enforces per-tool execution rules after capability token issuance.

- `register_rule(tool_name, rule)` — registers a policy rule for a named tool
- `resolve_slots(tool_name, args)` — resolves argument slots against policy
- `enforce(tool_name, args)` — validates args against registered rules
- `build_artifact(decision)` — produces a `CapabilityDecisionArtifact`

---

## Hash Chain Audit Log — Tamper Evidence

**File:** `agentic_core/L2_execution/audit/hash_chain_audit_log.py`

`HashChainAuditLog` — append-only, SHA-256 chained log. Every `AuditEntry` carries `previous_hash`, forming a tamper-evident chain.

`AuditEntry` dataclass:
- `entry_index: int`
- `previous_hash: str`
- `entry_hash: str`
- `timestamp: str`
- `tier: str`
- `action: str`
- `payload: dict[str, Any]`

| Method | Description |
|---|---|
| `append(tier, action, payload)` | Appends and chains a new entry |
| `seal()` | Marks the log as finalized |
| `verify_chain_integrity()` | Re-computes all hashes, confirms no tampering |
| `chain_root` | Returns the root hash of the entire chain |
| `length` / `entries` | Inspection properties |

---

## SSOT Structure Validator — Healer Target Verification

**File:** `agentic_core/L5_safety/enforcement/ssot_structure_validation_enforcer.py`

`SSOTStructureValidator` confirms that any file a healer intends to create or move lands in the correct layer and depth.

Key validation checks:
- `_validate_base_agent_location(path)` — base agents must be in `agentic_core/base_agents/`
- `_validate_layer_assignment(path)` — confirms L0–L6 layer assignment matches file content
- `_validate_depth(path)` — depth must match layer expectation
- `_validate_territory(path)` — app territory isolation (`apps_lic` vs `apps_rg`)
- `_validate_forbidden_patterns(path)` — blocks forbidden naming patterns

`StructureViolation` dataclass: `agent_class`, `agent_path`, `violation_type`, `message`, `severity`, `suggested_fix`.

`StructureValidationResult` dataclass aggregates violations into typed lists: `base_agent_violations`, `layer_violations`, `depth_violations`, `territory_violations`.

---

## SSOT Guardrail Violation Types

**File:** `agentic_core/L5_safety/enforcement/ssot_guardrail.py`

`Violation` dataclass: `file`, `line`, `rule`, `detail`, `severity`.

`ScanResult` dataclass: `files_scanned: int`, `violations: list[Violation]`.

---

## Execution Trace — Sealed Evidence

**File:** `agentic_core/L2_execution/types/execution_trace_types.py`

`ExecutionTrace` is the immutable, sealed output of every agent execution. It binds healer output to validator decision in a single artifact.

Key fields:
- `governed_payload_hash: str` — hash of the governed input
- `sandbox_envelope_ids: tuple[str, ...]` — all envelopes used
- `llm_response_hash: str` — hash of raw LLM output
- `validation_decision: str` — ALLOW / DENY / ESCALATE
- `hash_chain_root: str` — root of `HashChainAuditLog`
- `policy_hash: str` — hash of active policy config
- `prev_hash: str` — link to previous `ExecutionTrace`
- `transcript_hash: str` — hash of full execution transcript
- `replay_key: str` — deterministic replay identifier

`ExecutionTraceBuilder` provides a fluent builder API: `set_governed_payload`, `add_sandbox_envelope`, `set_llm_response`, `set_validation_decision`, `set_hash_chain_root`, `set_timing`, `seal()`.
