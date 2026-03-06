# Governance & Safety

## Overview

The Governance & Safety layer (L5) is the sole structural enforcement authority in the system. It enforces architectural boundaries, capability constraints, provider policies, write-set integrity, and behavioral governance across all agent executions. L5 gates every write, every LLM call, and every healing attempt. No other layer may perform persistent writes except through L5-certified paths.

---

## Architecture

```
Agent Execution Intent
        │
        ▼
GovernanceShieldValidator (L5)   ← content risk scan
        │
        ▼
VerificationGate (L5)            ← AST structural verification
        │
        ▼
CapabilityChokepoint (L2)        ← token issuance + authorization
        │
        ▼
L2BoundaryVerifier (L2)          ← packet + envelope integrity
        │
        ▼
WriteSetEnforcer (L2)            ← declared write-set enforcement
        │
        ▼
UniversalWriteGateway (L2)       ← physical write (only path)
        │
        ▼
HashChainAuditLog (L2)           ← tamper-evident audit record
        │
        ▼
DeterminismDigestEmitter (L6)    ← single-emission observability digest
```

---

## GovernanceShieldValidator — Content Risk Scanner

**File:** `agentic_core/L5_safety/validators/governance_validator.py`

`GovernanceShieldValidator` scans agent-generated content for privacy violations, forbidden patterns, and behavioral compliance before any downstream action.

| Method | Description |
|---|---|
| `scan_risk_level(content)` | Returns a risk tier: LOW / MEDIUM / HIGH / CRITICAL |
| `detect_privacy_language(content)` | Flags PII, sensitive identifiers, and regulated language |
| `check_forbidden_patterns(content)` | Tests against configurable forbidden pattern list |
| `generate_safety_protocol(risk_level)` | Returns the enforcement protocol for the detected risk tier |
| `audit_content_compliance(content)` | Full compliance sweep, returns `GovernanceResult` |
| `sanitize_claims(content)` | Strips or redacts non-compliant claims |

`GovernanceResult` dataclass:

| Field | Type | Description |
|---|---|---|
| `passed` | `bool` | Overall compliance gate result |
| `issues` | `list[str]` | List of detected issues |
| `risk_level` | `str` | LOW / MEDIUM / HIGH / CRITICAL |
| `score` | `float | None` | Numeric risk score if computed |
| `protocol` | `str | None` | Enforcement protocol identifier |
| `metadata` | `dict[str, Any]` | Extensible metadata |

---

## ArchivalGatekeeper — Safe Delete / Move / Archive

**File:** `agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py`

`ArchivalGatekeeper` is a singleton (via `get_instance()`) that mediates all destructive file operations. Every move, archive, and delete must pass through this gate.

`ArchivalOperation(Enum)`: `MOVE`, `ARCHIVE`, `DELETE`, `RESTORE`.

| Method | Description |
|---|---|
| `get_instance()` | Returns or creates the singleton |
| `reset_instance()` | Test isolation — resets singleton state |
| `safe_move(src, dst, requester, reason)` | Validated move with L4 ledger notification |
| `safe_archive(src, requester, reason)` | Moves to archive path with audit log |
| `safe_delete(src, requester, reason)` | Deletes with approval check and audit |
| `restore_from_archive(archive_path, dst)` | Reverses a prior `safe_archive` |
| `set_l4_ledger_hook(fn)` | Injects L4 ledger notification callback |
| `_notify_l4_ledger(result)` | Fires the L4 ledger hook |
| `set_input_function(fn)` | Replaces `input()` for non-interactive flows |
| `set_require_approval(flag)` | Enables / disables human approval requirement |
| `get_audit_log()` | Returns full list of `ArchivalResult` entries |
| `get_operation_count()` | Count of operations performed |

`ArchivalResult` dataclass:

| Field | Type | Description |
|---|---|---|
| `success` | `bool` | Operation outcome |
| `operation` | `ArchivalOperation` | Type of operation |
| `source_path` | `Path` | Source path |
| `destination_path` | `Path | None` | Destination (null for DELETE) |
| `requester_agent` | `str` | Agent that requested the operation |
| `reason` | `str` | Stated reason |
| `timestamp` | `str` | ISO 8601 timestamp |
| `error` | `str | None` | Error message if failed |
| `approval_status` | `str` | APPROVED / AUTO / DENIED |

---

## CircuitBreaker — Execution Rate Gate

**File:** `agentic_core/L5_safety/enforcement/circuit_breaker_gate.py`

`CircuitBreaker` implements exponential-backoff circuit breaking for any governance-protected execution path.

`CircuitState(Enum)`: `CLOSED` (normal), `OPEN` (blocking), `HALF_OPEN` (probing).

`CircuitBreakerConfig` dataclass:

| Field | Default-driven | Description |
|---|---|---|
| `failure_threshold` | — | Failures before OPEN |
| `success_threshold` | — | Successes in HALF_OPEN before CLOSED |
| `reset_timeout_seconds` | — | Initial backoff before HALF_OPEN |
| `max_reset_timeout_seconds` | — | Backoff ceiling |
| `backoff_multiplier` | — | Exponential growth factor |
| `half_open_max_calls` | — | Parallel probes allowed in HALF_OPEN |
| `execution_timeout_seconds` | — | Per-call timeout |

`CircuitBreakerMetrics` dataclass: `total_calls`, `successful_calls`, `failed_calls`, `rejected_calls`, `timed_out_calls`, `state_transitions`, `last_failure_time`, `last_success_time`, `current_backoff`.

`CircuitBreaker` methods:

| Method | Description |
|---|---|
| `state` | Current `CircuitState` |
| `is_closed()` / `is_open()` / `is_half_open()` | State predicates |
| `allow_request()` | Returns `True` if request may proceed |
| `record_success()` / `record_failure()` | Outcome recording |
| `_apply_exponential_backoff()` | Computes next backoff duration |
| `_transition_to_open()` / `_transition_to_half_open()` / `_transition_to_closed()` | State transitions |
| `get_time_until_retry()` | Seconds until HALF_OPEN probe allowed |
| `protect(fn)` | Context manager wrapping a callable |

`CircuitBreakerOpenError(Exception)` / `CircuitBreakerTimeoutError(Exception)` — raised on blocked / timed-out calls.

---

## Oscillation Firewall

**File:** `agentic_core/L5_safety/enforcement/oscillation_firewall_gate.py`

Prevents healing tier thrashing.

`OscillationFirewallConfig` dataclass: `cooldown_window: int`, `freeze_cycles: int`.

`OscillationFirewall` methods: `record_tier_decision`, `assert_no_oscillation`, `is_tier_frozen`, `get_frozen_tiers`, `reset_for_testing`.

`OscillationFirewallTripped(RuntimeError)` — raised when oscillation is detected.

---

## LazySeam Governance — Import Boundary Enforcement

**Files:**
- `agentic_core/L5_safety/governance/lazy_seam_enforcer.py`
- `agentic_core/L5_safety/governance/lazy_seam_classifier.py`
- `agentic_core/L5_safety/governance/lazy_seam_scanner.py`

The lazy seam suite governs upward imports (lower-layer modules importing higher-layer modules). These are permitted only via lazy-import patterns and only for allowlisted seams.

`LazyUpwardImport` dataclass (shared by enforcer and scanner):

| Field | Type | Description |
|---|---|---|
| `source_file` | `Path` | File performing the import |
| `source_layer` | `int` | Layer number of the importing file |
| `target_layer` | `int` | Layer number of the imported module |
| `import_statement` | `str` | Full import statement text |
| `line_number` | `int` | Line in source file |
| `context` | `str` | Surrounding code context |

### `LazySeamEnforcer`

| Method | Description |
|---|---|
| `scan_file(path)` | AST-scans a single file for upward imports |
| `scan_codebase()` | Full repo scan, returns all `LazyUpwardImport` instances |
| `enforce()` | Raises if any non-allowlisted upward import is found |
| `print_results()` | Human-readable report |

### `LazySeamClassifier`

| Method | Description |
|---|---|
| `_classify_seam(import)` | Classifies as ALLOWLISTED / VIOLATION / UNKNOWN |
| `classify_all_seams()` | Classifies all detected seams |
| `save_allowlist()` | Persists current allowlist to disk |
| `print_summary()` | Summary of classification results |

### `LazySeamScanner`

| Method | Description |
|---|---|
| `scan_codebase()` | Baseline scan for allowlist generation |
| `export_allowlist()` | Exports discovered seams as an allowlist JSON |

---

## SSOT Structure Validation

**File:** `agentic_core/L5_safety/enforcement/ssot_structure_validation_enforcer.py`

`SSOTStructureValidator` enforces the structural blueprint. See [Healer-Validator Resolution Symmetry](Healer-Validator%20Resolution%20Symmetry%20in%20Architecture.md) for method details.

`StructureViolation` dataclass: `agent_class`, `agent_path`, `violation_type`, `message`, `severity`, `suggested_fix`.

`StructureValidationResult` dataclass aggregates `base_agent_violations`, `layer_violations`, `depth_violations`, `territory_violations`.

---

## SSOT Guardrail — Import Boundary Scans

**File:** `agentic_core/L5_safety/enforcement/ssot_guardrail.py`

`Violation` dataclass: `file`, `line`, `rule`, `detail`, `severity`.
`ScanResult` dataclass: `files_scanned: int`, `violations: list[Violation]`.

---

## Capability Chokepoint — Token Issuance

**File:** `agentic_core/L2_execution/enforcement/capability_chokepoint.py`

`CapabilityChokepoint` — singleton gate for all capability tokens.

| Method | Description |
|---|---|
| `issue_token(subject, permissions, constraints)` | Issues a `CapabilityTokenArtifact` |
| `authorize_and_execute(fn, ...)` | Combined authorize + execute dispatch |
| `freeze()` | Permanently locks token issuance |
| `decisions` | Full `CapabilityDecisionArtifact` history |

---

## Write-Set Enforcer

**File:** `agentic_core/L2_execution/enforcement/write_set_enforcer.py`

`WriteSetEnforcer` (dataclass): `declared_write_set: frozenset[str]`, `_actual_writes: set[str]`, `_aborted: bool`.

`WriteSetViolation(RuntimeError)` — raised on first undeclared write. Execution aborts immediately.

---

## Provider Substitution Guard

**File:** `agentic_core/L2_execution/enforcement/provider_substitution_prohibition.py`

`ProviderSubstitutionGuard` enforces that the LLM provider that responds matches the provider declared in the capability token. Methods: `register_request`, `validate_response`, `handle_failure`, `clear_request`.

`ProviderSubstitutionViolation(Exception)` — raised on provider mismatch.

---

## Network Egress Guard

**File:** `agentic_core/L2_execution/enforcement/network_egress_guard.py`

`NetworkEgressViolation(Exception)` — raised on undeclared outbound network access. Symmetric to `WriteSetViolation` for network paths.

---

## Tool Policy Enforcer

**File:** `agentic_core/L2_execution/enforcement/tool_policy_enforcer.py`

`ToolPolicyEnforcer`:
- `register_rule(tool_name, rule)` — registers a policy rule
- `resolve_slots(tool_name, args)` — resolves argument slots
- `enforce(tool_name, args)` — validates args against rules
- `build_artifact(decision)` — produces `CapabilityDecisionArtifact`

---

## Verification Gate

**File:** `agentic_core/L5_safety/enforcement/verification_gate.py`

`VerificationGate(HallucinationDetectionMixin, SovereignBaseAgent)` — AST-based structural verifier. All verification is via `ast.parse`, never regex.

Methods: `verify_action`, `verify_modification`, `_verify_import_exists`, `_verify_function_exists`, `_verify_class_exists`, `_verify_variable_exists`, `_verify_method_exists`, `_verify_any_node_exists`, `clear_cache`, `get_cache_stats`.

---

## Phase Acceptance Guardrail

**File:** `agentic_core/L5_safety/enforcement/phase_acceptance_guardrail.py`

`PhaseAcceptanceGuard` — pre-merge governance gate. Methods: `check_testpaths_contract_sync`, `check_evidence_files_protocol`, `check_phase_evidence_completeness`, `validate`, `report`.

---

## Human Review Queue

**File:** `agentic_core/L5_safety/enforcement/human_review_queue_enforcer.py`

`HumanReviewQueue` — HITL escalation queue. Methods: `submit_for_review`, `approve`, `reject`, `modify_diff`, `escalate`, `get_queue_stats`. See [Path D HITL](Path%20D%20HITL.md) for full documentation.

---

## L2 Boundary Verifier

**File:** `agentic_core/L2_execution/enforcement/boundary_verifier.py`

`L2BoundaryVerifier` — validates instruction packets, L5 certifications, and sandbox envelopes at the L2 ingress boundary. Methods: `verify_instruction_packet`, `verify_l5_certification`, `verify_envelope`, `is_packet_valid`, `is_envelope_valid`.

---

## Layer Model Constraints

| Layer | Write Authority | Notes |
|---|---|---|
| L0 | No persistent writes | Routing / classification only |
| L1 | No persistent writes | Cognition / planning only |
| L2 | Writes via `UniversalWriteGateway` only | Requires `CapabilityTokenArtifact` |
| L3 | No persistent writes | Orchestration / dispatch only |
| L4 | No persistent writes | State reads only |
| **L5** | **Sole structural enforcement authority** | All writes must be L5-certified |
| L6 | No persistent writes | Observability / digest emission only |

`L2BoundaryVerifier.verify_l5_certification` is the runtime enforcement of this constraint — any execution packet without a valid L5 cert is rejected before it reaches the write path.
