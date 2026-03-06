# Healing & Escalation Loop

## Overview

The healing and escalation loop is a mathematically deterministic, zero-loss subsystem responsible for detecting failures, computing confidence scores, routing repair work to the appropriate healing tier, and escalating when local attempts are exhausted. It spans L2 (Execution), L5 (Safety), and `system_learning` layers.

---

## Architecture

```
FailureSignal
     │
     ▼
HealingTierRouter (L2.3 — single choke point)
     │
     ├─ heal_confidence >= X (0.75) ──► LOCAL_AGENT tier
     ├─ heal_confidence >= Y (0.40) ──► QWEN_VLLM tier
     └─ heal_confidence <  Y        ──► GEMINI_2_5_PRO tier
                                            │
                                    retry_count >= max_retries
                                    forces GEMINI_2_5_PRO
     │
     ▼
HealingStrategy (L5 enforcement)
     │
     ▼
HealingOutcomeAggregator (system_learning — feedback to meta-learning)
```

---

## Tier Routing — Single Choke Point

**File:** `agentic_core/L2_execution/healers/healing_tier_router.py`

`route_healing_tier` is the **only** place in the repository that selects between `LOCAL_AGENT`, `QWEN_VLLM`, and `GEMINI_2_5_PRO`. No environment variable access, no external data loading, fixed-precision arithmetic.

### `compute_heal_confidence(healing_input, *, meta_prior_provider) -> tuple[float, tuple[str, ...]]`

Six weighted components (weights sum to 1.0):

| Component | Weight | Description |
|---|---|---|
| `failure_prior` | 0.25 | Compile-time frozen per `failure_type` |
| `blast_radius_contribution` | 0.20 | `(1 - blast_radius_estimate)` |
| `historical_success` | 0.15 | From `HISTORICAL_SUCCESS_RATES` or live `MetaPriorProvider` |
| `tool_readiness` | 0.15 | Fixed at 0.8 for determinism |
| `retry_decay` | 0.10 | `max(0, 1 - retry_count * 0.1)` |
| `failure_entropy` | 0.15 | LOW=1.0 / MEDIUM=0.7 / HIGH=0.3 |

Score is rounded to 6 decimal places. Output includes `reason_codes` tuple for full auditability.

### `FAILURE_CLASS_PRIORS` (compile-time frozen)

```python
"syntax_error":           0.90
"missing_import":         0.85
"naming_violation":       0.85
"type_hint_error":        0.80
"import_cycle":           0.70
"location_violation":     0.65
"structure_violation":    0.60
"gravity_leak":           0.55
"integrity_gate_failure": 0.50
"test_failure":           0.45
"runtime_error":          0.35
"unknown":                0.30
```

### Replay Key

`_compute_replay_key(healing_input, decision)` — SHA-256 over `agent_id`, `failure_type`, `error_signature`, `trace_id`, `retry_count`, `blast_radius_estimate`, `heal_confidence`, `tier.value`, and `HISTORICAL_DATA_HASH`. Timestamp explicitly excluded.

### `SovereigntyViolation` (Exception)

Raised when an agent not in the compile-time frozen `TIERING_ALLOWLIST` attempts to invoke the tier router.

---

## Tiering Allowlist

**File:** `agentic_core/L2_execution/healers/tiering_allowlist.py`

`TIERING_ALLOWLIST` is a `frozenset[tuple[str, str]]` — compile-time frozen, no CSV loading, no runtime mutation. Agents currently enrolled:

- `CodeHealerAgent` — `agentic_core/L5_safety/reasoning/`
- `GravityLeakRepairAgent` — `agentic_core/L5_safety/reasoning/`
- `IntegrityGateExecutorAgent` — `agentic_core/L5_safety/reasoning/`
- `LocationHealerAgent` — `agentic_core/L5_safety/reasoning/`
- `SafetyExecutorAgent` — `agentic_core/L5_safety/reasoning/`
- `StructureHealerAgent` — `agentic_core/L5_safety/reasoning/`
- `TypeHintFixerAgent` — `agentic_core/L5_safety/reasoning/`
- `DispatchOutreachToolsAgent` — `apps_lic/reasoning/`
- `OutreachValidationExecutorAgent` — `apps_lic/reasoning/`
- `DispatchResumeToolsAgent` — `apps_rg/reasoning/`
- `remediation_dispatcher` — `agentic_core/L2_execution/scripts/`

Agents absent from the allowlist **must** emit `FailureSignal` only; they may not invoke `route_healing_tier` directly.

Helper functions: `is_tiering_allowed(agent_name)`, `is_tiering_allowed_by_path(file_path)`.

---

## Tier Configuration

**File:** `agentic_core/L2_execution/healers/healing_tier_config.py`

`HealingTierConfig` is a `frozen=True, slots=True` dataclass. Hard-fails in `__post_init__` if `X <= Y` or values are out of range.

| Constant | Value | Mutability |
|---|---|---|
| `HEALING_CONFIDENCE_X` | 0.75 | **CANNOT BE MODIFIED by meta-learning** |
| `HEALING_CONFIDENCE_Y` | 0.40 | **CANNOT BE MODIFIED by meta-learning** |
| `max_heal_retries` | 3 | Configurable |
| `model_qwen_vllm_id` | `Qwen/Qwen2.5-7B-Instruct` | Pinned |
| `model_qwen_14b_vllm_id` | `Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4` | Pinned (RTX 5090, ≥16 GB VRAM) |
| `model_gemini_2_5_pro_id` | `gemini-2.5-pro` | Pinned |
| `QWEN_GPU_MEM_UTIL` | 0.70 | SSOT — do not override per call-site |

Qwen 14B agent routing keys: `arch_governor`, `file_classification`, `cognitive_disposition`, `observability_probe`.

BMG embedding (`BAAI/bge-m3`) agent routing keys: `location`, `root_hygiene`.

---

## Healing Provider Invocation

**File:** `agentic_core/L2_execution/healers/healing_tier_dispatcher.py`

`HealingProviderInvoker` (Protocol) defines three invocation paths:

- `invoke_local(...)` — local deterministic agent
- `invoke_qwen_vllm(...)` — vLLM-hosted Qwen inference
- `invoke_gemini(...)` — Gemini 2.5 Pro API

---

## L5 Healing Strategy

**File:** `agentic_core/L5_safety/enforcement/HealingStrategy.py`

`HealingStrategy` is the L5 enforcement layer that bridges the tier router to physical agent execution.

| Method | Description |
|---|---|
| `name()` | Returns strategy identifier |
| `get_tiers()` | Returns ordered tier list |
| `should_run_tier(tier)` | Tier eligibility check |
| `get_agent(tier)` | Resolves agent for given tier |
| `execute_agent(agent, context)` | Executes with trace and envelope |
| `should_abort_tier(result)` | Abort condition after execution |

---

## Oscillation Firewall

**File:** `agentic_core/L5_safety/enforcement/oscillation_firewall_gate.py`

Prevents thrashing between healing tiers across cycles.

`OscillationFirewallConfig` dataclass:
- `cooldown_window: int` — sliding window of tier decisions to inspect
- `freeze_cycles: int` — number of cycles a frozen tier remains locked

`OscillationFirewall` methods:
- `record_tier_decision(tier)` — appends to decision history
- `assert_no_oscillation()` — raises `OscillationFirewallTripped` on detected thrash
- `is_tier_frozen(tier)` / `get_frozen_tiers()` — frozen tier inspection
- `reset_for_testing()` — test isolation

`OscillationFirewallTripped` extends `RuntimeError`.

---

## Outcome Aggregation & Feedback

**File:** `system_learning/engines/healing_outcome_aggregator.py`

`HealingOutcomeAggregator` ingests per-invocation outcomes and produces snapshots consumed by the meta-learning pipeline.

| Method | Description |
|---|---|
| `ingest(event)` | Ingests raw healing outcome event |
| `ingest_invocation(record)` | Ingests a typed `InvocationRecord` |
| `compute_success_rate(failure_type)` | Returns current windowed success rate |
| `build_proposal()` | Builds a config change proposal from current window |
| `create_snapshot()` | Serializes current aggregate state |
| `snapshot()` | Returns latest snapshot reference |
| `clear_aggregates()` | Resets window (for testing) |

`HealingOutcomeAggregatorProtocol` defines the minimal interface: `ingest_invocation`, `compute_success_rate`, `create_snapshot`.

---

## Execution Gateway

**File:** `agentic_core/L2_execution/engines/ExecutionGateway.py`

`ExecutionGateway` wraps all agent execution with trace, envelope creation, and signature verification.

- `execute_with_trace(...)` — full instrumented execution
- `create_envelope(...)` — produces `SandboxEnvelope` with `ToolBudget`

---

## Healing Tier Types

**File:** `agentic_core/L2_execution/healers/healing_tier_types.py`

- `HealingTier` — `str, Enum` with values `LOCAL_AGENT`, `QWEN_VLLM`, `GEMINI_2_5_PRO`
- `HealingInput` — structured failure context fed to the router
- `HealingDecision` — immutable output of `route_healing_tier`

---

## Historical Success Rate Seam

`get_historical_success_rate(error_signature, *, meta_prior_provider)` resolves the success-rate prior in priority order:

1. Test-time `_HISTORICAL_OVERRIDES` dict
2. Live `MetaPriorProvider.get_prior(error_signature)` (Phase 1 live store path)
3. Compile-time frozen `HISTORICAL_SUCCESS_RATES`

`set_historical_success_rate` / `clear_historical_success_rates` — test utilities only; production code does not call these.

---

## Data Contract: `HISTORICAL_DATA_VERSION`

`HISTORICAL_DATA_VERSION = "v1.0.0"` — SHA-256 first 16 hex chars included in every replay key to version-stamp historical priors. Bump this when `HISTORICAL_SUCCESS_RATES` changes.
