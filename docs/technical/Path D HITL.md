# Path D HITL — Human-in-the-Loop

## Overview

Path D is the Human-in-the-Loop (HITL) escalation path activated when the healing subsystem cannot resolve a failure autonomously, or when the risk tier of a proposed change exceeds the autonomous approval threshold. HITL decisions are fully auditable, replayable, and feed back into the RLHF optimizer as DPO pairs.

---

## Architecture

```
HealingStrategy (L5) — autonomous paths exhausted
        │
        ▼
HumanReviewQueue (L5 enforcement)
        │  submit_for_review(context_bundle)
        │
        ▼
Reviewer (external: GitHub PR / Slack / operator console)
        │  approve / reject / modify_diff / escalate
        │
        ▼
HumanReviewAdapter (L5 enforcement)
        │  check_status / get_pending_reviews
        │
        ▼
HITL Decision Logger (system_learning)
        │  log_hitl_decision → evidence file
        │
        ▼
DPO Pair Generator (L6 observability)
        │  control_output vs candidate_output + human_decision
        │
        ▼
RLHF Optimizer (system_learning)
        │  propose_from_dpo → RLHFChangePackage
        │
        ▼
Meta-Learning Pipeline
```

---

## Human Review Queue Enforcer

**File:** `agentic_core/L5_safety/enforcement/human_review_queue_enforcer.py`

`HumanReviewQueue` is the primary HITL intake and dispatch mechanism.

| Method | Description |
|---|---|
| `submit_for_review(context_bundle)` | Enqueues a `ReviewRequest` with full `ContextBundle` |
| `approve(request_id, reviewer_id, notes)` | Marks request APPROVED, triggers callbacks |
| `reject(request_id, reviewer_id, notes)` | Marks request REJECTED, triggers callbacks |
| `modify_diff(request_id, new_diff)` | Reviewer edits the proposed diff before approval |
| `escalate(request_id, next_reviewer)` | Advances `escalation_level` and `escalation_chain` |
| `get_pending_requests()` | Returns all requests in PENDING state |
| `get_request_status(request_id)` | Returns current `ReviewStatus` |
| `register_callback(event, fn)` | Registers a callback for APPROVE / REJECT events |
| `_evict_oldest()` | Evicts oldest request when queue is at capacity |
| `_process_expired()` | Transitions timed-out requests to EXPIRED |
| `_trigger_callback(event, request)` | Fires registered callbacks |
| `_emit_policy_update_proposal()` | Emits a policy update proposal on pattern of rejections |
| `get_queue_stats()` | Returns depth, latency, and escalation distribution |

### `ReviewRequest` dataclass

| Field | Type | Description |
|---|---|---|
| `request_id` | `str` | Unique identifier |
| `created_at` | `datetime` | Queue entry time |
| `status` | `ReviewStatus` | PENDING / APPROVED / REJECTED / EXPIRED |
| `context_bundle` | `ContextBundle | None` | Full context payload |
| `reviewer_id` | `str | None` | ID of assigned reviewer |
| `review_started_at` | `datetime | None` | Clock-in time |
| `review_completed_at` | `datetime | None` | Clock-out time |
| `review_notes` | `str` | Free-text reviewer notes |
| `escalation_level` | `int` | Number of escalation hops |
| `escalation_chain` | `list[str]` | Ordered list of reviewers in chain |
| `timeout_seconds` | `int` | TTL before automatic expiry |

### `ContextBundle` dataclass

The full context payload delivered to the reviewer:

| Field | Type | Description |
|---|---|---|
| `detection_signal` | `dict[str, Any]` | Raw detection event from L4a |
| `proposed_diff` | `ProposedDiff` | Structured diff with line counts |
| `ai_rationale` | `str` | Healing agent's stated rationale |
| `simulated_outcome` | `SimulatedOutcome` | Pre-computed simulation results |
| `risk_assessment` | `dict[str, Any]` | Tier, blast radius, impact surface |
| `similar_past_cases` | `list[dict[str, Any]]` | Nearest historical cases by embedding |
| `additional_context` | `dict[str, Any]` | Extension point |

### `ProposedDiff` dataclass

- `file_path: Path`
- `original_content: str`
- `proposed_content: str`
- `change_summary: str`
- `lines_added: int`
- `lines_removed: int`

### `SimulatedOutcome` dataclass

- `success_probability: float`
- `expected_side_effects: list[str]`
- `regression_risk: str`
- `test_results: dict[str, bool]`
- `rollback_complexity: str`

---

## Human Review Adapter

**File:** `agentic_core/L5_safety/enforcement/HumanReviewAdapter.py`

`HumanReviewAdapter` provides a lightweight in-memory queue for simpler HITL integrations (e.g., non-batch healing flows). In production this integrates with GitHub PRs, Slack, or an operator console.

| Method | Description |
|---|---|
| `submit_for_review(agent_name, file_path, description, proposed_change)` | Enqueues a `ReviewRequest`, returns `review_id` |
| `check_status(review_id)` | Returns current `ReviewStatus` |
| `get_pending_reviews()` | Returns all PENDING requests |
| `is_available()` | Whether the adapter is accepting submissions |
| `get_queue_depth()` | Number of outstanding PENDING reviews |
| `approve(review_id, notes)` | Sets status to APPROVED |
| `reject(review_id, notes)` | Sets status to REJECTED |
| `clear_expired()` | Removes all EXPIRED entries |
| `_expire_if_stale(request)` | Single-entry staleness check |
| `_expire_stale_requests()` | Batch staleness sweep |

Default TTL: `24` hours. Configurable via `ttl_hours` constructor argument.

### `ReviewRequest` dataclass (Adapter variant)

| Field | Type |
|---|---|
| `review_id` | `str` |
| `agent_name` | `str` |
| `file_path` | `str` |
| `change_description` | `str` |
| `proposed_change` | `str` |
| `status` | `ReviewStatus` |
| `submitted_at` | `str` (ISO 8601) |
| `reviewed_at` | `str | None` |
| `reviewer_notes` | `str | None` |
| `metadata` | `dict[str, Any]` |

`ReviewStatus` enum values: `PENDING`, `APPROVED`, `REJECTED`, `EXPIRED`.

---

## Phase Acceptance Guardrail

**File:** `agentic_core/L5_safety/enforcement/phase_acceptance_guardrail.py`

`PhaseAcceptanceGuard` is the pre-merge HITL check for phased work.

| Method | Description |
|---|---|
| `check_testpaths_contract_sync()` | Verifies `pytest.ini` testpaths match `test_testpaths_contract.py` |
| `check_evidence_files_protocol()` | Validates evidence file shape (dual-hash, ASCII-only, section order) |
| `_is_allowed_truncation(section)` | Allows known-safe section truncation |
| `check_phase_evidence_completeness(evidence_path)` | Confirms all required sections are present |
| `validate()` | Runs all checks, returns list of violations |
| `report()` | Returns human-readable summary of validate() output |

---

## HITL Decision Logger

**File:** `system_learning/engines/hitl_decision_logger.py`

Thread-safe, stdlib-only logger that appends structured records to the active evidence file.

### `log_hitl_decision(agent, file_path, violation, proposed, decision, extra)`

Appends a `HITL_DECISION_N` record with:
- `Agent=` — class name of the triggering agent
- `File=` — affected file path
- `Violation=` — violation type (e.g., `PASCAL_IN_NON_AGENT_FOLDER`)
- `Proposed=` — planned action (e.g., `ARCHIVE`, `MOVE`)
- `Decision=` — outcome (e.g., `APPROVED`, `SKIPPED`, `MANUAL`)
- `extra` — optional key-value pairs

Returns the sequential decision number (1-based). Records are ASCII-only (byte-scan invariant §2). Evidence path resolved from `HITL_EVIDENCE_FILE` env var or `docs/reports/evidence/wave6_evidence.md`.

`get_decision_count()` — total decisions logged in this process lifetime.
`reset_for_testing()` — test isolation only.

---

## DPO Pair Generation — L6 Observability

**File:** `agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py`

Converts APPROVE/REJECT decisions into Direct Preference Optimization pairs for downstream RLHF training.

`DPOPairGenerator` (Protocol):
```python
def generate(
    *,
    control_output_bytes: bytes,
    candidate_output_bytes: bytes,
    human_decision: str,        # "APPROVE" or "REJECT"
    reason_codes: tuple[str, ...],
) -> DPOPair
```

`DefaultDeterministicDPOPairGenerator` implementation:
1. Validates `human_decision` ∈ `{"APPROVE", "REJECT"}`
2. Computes `control_hash = SHA-256(control_output_bytes)`
3. Computes `candidate_hash = SHA-256(candidate_output_bytes)`
4. Builds `DPOExampleId(control_hash, candidate_hash)`
5. Returns `DPOPair(example_id, control_output_hash, candidate_output_hash, human_decision, reasons)`

No side effects, no wall-clock timestamps in keys — fully deterministic.

---

## DPO Pair Bounding

**File:** `agentic_core/L6_observability/engines/dpo_pair_generator.py`

`DPOBoundingPolicy` dataclass:
- `min_clamp: float` — minimum raw score after clamping
- `max_clamp: float` — maximum raw score after clamping
- `max_delta: float` — maximum allowed deviation from control score

`BoundedDPOPair(NamedTuple)` — DPO pair with bounding policy applied. `BoundingViolation(Exception)` raised when `max_delta` is exceeded.

---

## RLHF Optimizer

**File:** `system_learning/engines/rlhf_optimizer_impl.py`

`DefaultRLHFOptimizer.propose_from_dpo(dpo_batch)` — processes a batch of `DPOPair` objects and emits an `RLHFChangePackage`.

`RLHFChangePackage` dataclass:

| Field | Type | Description |
|---|---|---|
| `surface_name` | `str` | Config surface to update |
| `parameter` | `str` | Parameter name |
| `direction` | `str` | `UP` / `DOWN` |
| `delta` | `float` | Magnitude of change |
| `justification` | `str` | Human-readable rationale |
| `snapshot_id` | `str` | Source snapshot reference |
| `pair_count` | `int` | Number of DPO pairs processed |
| `preference_strength` | `float` | Aggregate preference signal strength |

`RLHFOptimizer` (Protocol in `system_learning/engines/rlhf_optimizer.py`) defines `propose_from_dpo`. `DefaultDeterministicRLHFOptimizer` is the production implementation.

---

## Agent Gym — HITL Benchmark Loop

**File:** `agentic_core/L3_orchestration/engines/agent_gym_engine.py`

`AgentGym(SovereignBaseAgent)` provides a controlled evaluation environment for benchmarking healing agent decisions before HITL escalation.

| Method | Description |
|---|---|
| `register_scenario(scenario)` | Registers a test scenario |
| `run_benchmark(scenario_id)` | Executes benchmark, returns scored result |
| `_execute_test_cases(scenario)` | Runs all test cases within scenario |
| `_create_benchmark_result(cases)` | Aggregates per-case results |
| `run_training_session(agent, episodes)` | Online training over multiple episodes |
| `get_scenario(scenario_id)` | Looks up a registered scenario |
| `list_scenarios()` | Returns all registered scenario IDs |
| `get_session_history()` | Full history of benchmark sessions |
| `_classify_performance(score)` | Maps numeric score to tier label |
| `_generate_recommendations(result)` | Produces actionable improvement suggestions |
| `_identify_improvement_areas(result)` | Finds weak spots in agent behavior |

---

## Approval Gates

**File:** `system_learning/pipelines/approval_gates.py`

`ApprovalDecision(Enum)` — `APPROVE`, `REJECT`, `DEFER`.

`ApprovalGate(Protocol)`:
- `decide(proposal, context) -> ApprovalDecision`

`RiskTierClassifier(Protocol)`:
- `classify(proposal) -> str` — returns risk tier label

`DefaultRuleBasedGate` — production implementation applying configurable risk rules.
`DefaultRiskClassifier` — classifies proposals into risk tiers using `ChangePackage` fields.

**File:** `system_learning/pipelines/approval_gate_impl.py`

`ApprovalDecision` dataclass (implementation-level): `approved: bool`, `reason: str`, `requires_manual_review: bool`.

Concrete gate implementations:
- `AutoApprovalGate` — approves based on configurable confidence thresholds
- `AlwaysApproveGate` — test utility
- `NeverApproveGate` — circuit-breaker / lockdown utility
