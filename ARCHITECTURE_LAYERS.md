# Agentic Architecture — L0–L6 Layer Reference

> **Second README.** This document covers the full L0–L6 layered architecture: the hardening criteria applied to each layer, what 100% capability coverage at each layer unlocks, and why every layer is load-bearing for production-grade agentic systems.

The main [README](README.md) describes the platform from the outside. This document describes it from the inside — layer by layer, criterion by criterion.

---

## Layer Map

```
┌─────────────────────────────────────────────────────────────────┐
│  L6  OBSERVABILITY   — dashboards, latency budgets, health      │
├─────────────────────────────────────────────────────────────────┤
│  L5  SAFETY          — guardrails, SSOT, HITL, audit registry   │
├─────────────────────────────────────────────────────────────────┤
│  L4  STATE           — versioned state, conflict detection      │
├─────────────────────────────────────────────────────────────────┤
│  L3  ORCHESTRATION   — capability registry, agent handoff       │
├─────────────────────────────────────────────────────────────────┤
│  L2  EXECUTION       — sovereign gateways, determinism, tools   │
├─────────────────────────────────────────────────────────────────┤
│  L1  COGNITION       — propose-only reasoning, planning         │
├─────────────────────────────────────────────────────────────────┤
│  L0  ROUTING         — entry policy, contracts, capacity        │
└─────────────────────────────────────────────────────────────────┘

Gravity rule: layer N may only import from layers 0 … N.
Upward imports are architectural violations detected by CI.
```

Every request enters at L0, flows downward through controlled interfaces, and emits lifecycle signals that flow upward through L6. No layer may bypass another.

---

## Cross-Layer Lifecycle Signals

Every module in every layer emits the same canonical lifecycle trace contract. These signals are the connective tissue that makes the entire stack observable and replayable.

| Signal | What it means |
|---|---|
| `emit_replay_key` | Deterministic key for exact-input replay |
| `emit_determinism_digest` | SHA-256 digest binding inputs to a decision |
| `_emit_routes_through` | Route selection recorded in ADG |
| `_emit_applies_guardrail` | Policy enforcement point activated |
| `_emit_reads_policy_state` | Policy state consumed — version-locked |
| `_emit_records_execution_trace` | Execution trace appended to audit log |
| `_emit_signs_execution_trace` | Hash-chain signature applied |
| `_emit_snapshots_state` | Point-in-time state snapshot committed |
| `_emit_dispatches_healing_run` | Healer pipeline activated |
| `_emit_escalates_to_human` | HITL escalation triggered |

Every layer emits all ten signals at module init, ensuring complete ADG edge coverage and lifecycle traceability from startup.

---

## L0 — Routing

### Sovereignty Assertion

L0 is the **sole entry point** for all requests. No agent, tool, or application component may execute a route without a committed, policy-hashed `RoutingContract`. Raw route output is forbidden downstream.

### Hardening Criteria

| Criterion | Enforcement module |
|---|---|
| Every routing decision backed by immutable contract | `enforcement/routing_contract.py` |
| All contracts carry 14 mandatory fields | `RoutingContract` frozen dataclass |
| Policy hash and version locked at contract creation | `enforcement/policy_hash_enforcer.py` |
| Stale contracts (policy changed since issuance) rejected | `RoutingContract.require_valid()` |
| Deterministic replay key and digest emitted per decision | `enforcement/deterministic_replay_guard.py` |
| Capacity governance enforced before route selection | `capacity/capacity_aware_router.py` |
| Route degradation tracked per route | `capacity/capacity_snapshot.py` |
| Historical outcomes analyzed for policy optimization | `optimization/optimization_orchestrator.py` |
| Governance contracts enforce boundary/crypto/traceability | `enforcement/governance_contracts.py` |
| Mutation prohibited at routing layer | `enforcement/mutation_prohibition.py` |
| Boot sequence enforced before first route | `enforcement/boot_sequence.py` |
| Apps taxonomy validated (scope isolation) | `enforcement/apps_taxonomy_guard.py` |
| Runtime guard blocks unsafe routing paths | `enforcement/runtime_guard.py` |
| Trace ID generated and propagated on every request | `enforcement/trace_id_generator.py` |

### 100% Capability Coverage Unlocks

- **Zero uncontrolled entry points.** Every execution path is traced back to a `RoutingContract` with a known policy version.
- **Deterministic replay.** Any routing decision can be replayed identically from its `replay_key` and `request_hash`.
- **Policy drift detection.** Contracts issued against stale policy versions are automatically rejected, surfacing policy regressions before they propagate.
- **Capacity-aware degradation.** Routes with elevated failure rates or latency degrade gracefully rather than silently retrying until timeout.
- **Historical optimization.** Routing policy adapts from observed `(success_rate, latency_p95, cost_estimate)` tuples — self-improving without human intervention.

### Why It Is Critical

Without a governed routing layer, agents select execution paths ad hoc. There is no policy enforcement surface, no replay anchor, and no audit trail for why a given agent was invoked. Any security or compliance review becomes impossible. L0 makes every decision traceable to a specific policy version at a specific point in time.

---

## L1 — Cognition

### Sovereignty Assertion

L1 is **propose-only**. This layer reasons, plans, and captures patterns. It does not execute actions, route requests, or persist data. Those responsibilities belong exclusively to L2, L0, and L4 respectively. Violation of this boundary is an architectural inversion caught by CI.

### Hardening Criteria

| Criterion | Enforcement module |
|---|---|
| No execution or routing logic permitted in L1 | `layer_sovereignty_enforcer.py` (L5) + CI |
| Multi-step reasoning plans with checkpoint enforcement | `planning/plan_creator.py` |
| Plan checkpoints halt execution on condition violation | `planning/reasoning_plan.py` `PlanCheckpoint` |
| Plan revisions recorded immutably | `PlanRevision` dataclass |
| Reasoning patterns captured, versioned, and validated | `knowledge/knowledge_orchestrator.py` |
| Pattern reuse tracked with outcome quality scores | `knowledge/reasoning_knowledge.py` |
| Action requests typed and validated before dispatch | `types/action_request_types.py` |
| Reasoning traces bound to originating trace ID | `ReasoningTrace.originating_trace_id` |
| Validators enforce reasoning output contracts | `validators/` (7 modules) |
| Telemetry emitted at reasoning phase boundaries | `telemetry/` |

### 100% Capability Coverage Unlocks

- **Isolated cognitive testing.** Reasoning logic can be tested in complete isolation — no side effects, no network calls, no state mutations. Reproducibility is guaranteed.
- **Checkpoint-gated planning.** Multi-step plans stop at checkpoints when preconditions fail rather than continuing on invalid state.
- **Pattern learning.** Successful reasoning traces are captured and reused, improving quality over runs without retraining.
- **Typed action proposals.** The boundary between "deciding to act" and "actually acting" is a typed interface, making cognitive failures distinct from execution failures.

### Why It Is Critical

When cognition and execution are co-located, every cognitive failure manifests as a side effect. Debugging becomes archaeology. L1 separation means a bad reasoning step produces a typed error, not a corrupted file or a runaway LLM call. It also makes the reasoning layer independently testable, upgradeable, and replaceable.

---

## L2 — Execution

### Sovereignty Assertion

L2 is the **sole authority for side effects**. All filesystem writes, LLM invocations, embedding generations, and tool executions pass through explicit sovereign gateways. No agent or cognition module may mutate state directly.

### Hardening Criteria

| Criterion | Enforcement module |
|---|---|
| All writes through `UniversalWriteGateway` | `UniversalWriteGateway.py` |
| Write allowlist enforced — paths outside allowlist rejected | `enforcement/write_set_enforcer.py` |
| All LLM calls through `SovereignLLMGateway` | `enforcement/SovereignLLMGateway.py` |
| LLM gateway supports OpenAI, Anthropic, Google with unified audit | `SovereignLLMGateway` FIFO audit log |
| Tool invocations validated against typed `ToolContract` | `contracts/typed_tool_contract.py` |
| Capability chokepoint blocks unauthorized tool access | `enforcement/capability_chokepoint.py` |
| Capability revocation enforced at runtime | `enforcement/capability_revoker.py` |
| Provider substitution prohibited (no silent fallback) | `enforcement/provider_substitution_prohibition.py` |
| Network egress guarded | `enforcement/network_egress_guard.py` |
| Execution strategy safety evaluated before selection | `adaptation/adaptation_orchestrator.py` |
| Unsafe strategies explicitly rejected | `execution_strategy_chosen` → `unsafe_strategy_rejected` |
| Execution status fully enumerated (STARTED/SUCCEEDED/FAILED/RETRIED/CANCELLED/BLOCKED/ESCALATED) | `observability/execution_observability.py` |
| Failure classification taxonomy (7 classes) | `FailureClassification` enum |
| Hash-chain audit log for all gateway operations | `audit/hash_chain_audit_log.py` |
| Mutation records immutable and tamper-evident | `MutationRecord` SHA-256 hash chain |
| Deterministic loop detection | `enforcement/deterministic_loop_detector.py` |
| Sandbox isolation for untrusted execution | `enforcement/sovereign_sandbox_isolation.py` |
| Budget enforcement (latency, token, cost) | `enforcement/budget_enforcer.py` |
| Replay envelopes wrap all execution output | `types/replay_envelope_types.py` |
| 29 healers for structured failure recovery | `healers/` |

### 100% Capability Coverage Unlocks

- **Zero uncontrolled mutations.** Every write to disk, every model call, every tool invocation is recorded, hashed, and attributable.
- **Provider-agnostic governance.** Switching from Gemini to Claude to local Qwen changes only gateway configuration — all audit, retry, and policy logic is unchanged.
- **Typed tool safety.** Tools cannot be invoked with wrong argument shapes; `ToolContract` validation catches schema violations before execution.
- **Failure taxonomy.** Every failure is classified as exactly one of: `POLICY_BLOCK`, `TOOL_ERROR`, `NETWORK_FAILURE`, `MUTATION_FAILURE`, `VALIDATION_FAILURE`, `UNKNOWN_FAILURE` — enabling targeted healing rather than generic retry.
- **Replay simulation.** Execution can run in replay mode, replaying mutation records without actual side effects — enabling deterministic debugging.

### Why It Is Critical

Scattered side effects are the root cause of most agentic system failures in production. When any agent can write files, call models, or invoke tools directly, there is no surface for policy enforcement, no audit trail, and no deterministic replay. L2 collapses all mutation authority into auditable gateways, turning side effects from a liability into a governed capability.

---

## L3 — Orchestration

### Sovereignty Assertion

L3 governs **multi-agent coordination**. No agent may invoke another agent directly. All agent-to-agent transitions pass through `HandoffDispatcher` → `CapabilityRegistry` → `CapabilityToken`. This layer contains no cognition, no routing, and no execution logic.

### Hardening Criteria

| Criterion | Enforcement module |
|---|---|
| All agent handoffs through `HandoffDispatcher` | `contracts/agent_handoff.py` |
| Every handoff resolved through `CapabilityRegistry` | `registry/capability_registry.py` |
| Capability tokens issued per resolved handoff | `CapabilityToken` |
| Exclusive capability conflicts detected | `ExclusiveCapabilityConflictError` |
| Unregistered dispatch blocked | `UnregisteredDispatchError` |
| Registry version conflicts detected | `RegistryVersionError` |
| Agent capability ownership model enforced (SINGLETON/SHARED) | `CapabilityOwnership` enum |
| Human review requirement enforced per capability entry | `CapabilityRegistryEntry.human_review_requirement` |
| Action class restrictions per capability | `CapabilityRegistryEntry.action_classes` |
| Allowed caller set enforced | `CapabilityRegistryEntry.allowed_callers` |
| Workflow stage and owner transitions recorded | `visualization/visualization_updater.py` |
| Workflow status fully enumerated (ACTIVE/BLOCKED/RETRYING/ESCALATED/COMPLETED/FAILED) | `WorkflowStatus` enum |
| Transition reason taxonomy (6 classes) | `StageTransitionReason` enum |
| Arbitration for multi-agent conflicts | `arbitration/` |
| Prompt-to-contract (PTC) handshake enforced | `ptc/` |
| Replay journal for workflow traces | `replay/` |
| Workflow visualization queryable | `query_workflow_visualization()` |

### 100% Capability Coverage Unlocks

- **Static agent topology.** Every possible agent-to-agent dispatch path is visible in the ADG as a `HandoffDispatcher.register()` edge — no hidden dynamic invocations.
- **Capability-gated coordination.** An agent cannot be dispatched to a capability it is not registered for, eliminating scope creep in multi-agent workflows.
- **Workflow observability.** Every stage transition, owner change, and workflow completion is recorded as a `WorkflowVisualizationRecord` — the full execution DAG is reconstructable post-hoc.
- **Conflict-free multi-agent ownership.** Singleton capability conflicts are caught at registration time, not at runtime after a race condition.
- **Human-in-the-loop integration.** Capabilities requiring human review are flagged at the registry level, not embedded in agent logic.

### Why It Is Critical

In unstructured multi-agent systems, agents invoke each other through strings, dynamic imports, or shared state. This produces non-deterministic execution graphs that cannot be audited, replayed, or safely modified. L3 makes every agent-to-agent relationship a first-class, registry-governed contract — turning the execution graph from implicit to explicit.

---

## L4 — State

### Sovereignty Assertion

L4 is the **sole persistence authority**. It manages versioned state transitions, conflict detection, and snapshot lineage. No execution logic or agent orchestration belongs in this layer. Agents never write state directly — they commit transitions through L4 interfaces.

### Hardening Criteria

| Criterion | Enforcement module |
|---|---|
| All state transitions committed through versioned interface | `versioning/commit_versioned_state_transition.py` |
| State reads return versioned read artifacts | `StateVersionedRead` |
| Conflict detection on concurrent transitions | `StateConflictError` |
| Snapshot lineage enforced (no orphan snapshots) | `SnapshotLineageError` |
| Namespace isolation enforced | `StateNamespaceError` |
| Unversioned state writes blocked | `UnversionedStateError` |
| Snapshot policies govern retention | `SnapshotPolicy` |
| Actor context tracked on every transition | `ActorContext` |
| State version registry queryable | `get_state_version_registry()` |
| Caching layer with sovereignty | `caching/` |
| Memory subsystem with 19 modules | `memory/` |
| Storage backends (vector, DuckDB, Redis) | `storage/`, `stores/` |
| State authority validated before write | `authority/` |
| Workflow engine state lifecycle managed | `workflow_engines/` |
| 22 enforcement modules | `enforcement/` |

### 100% Capability Coverage Unlocks

- **Conflict-safe concurrent agents.** Multiple agents writing to overlapping state namespaces produce `StateConflictError` rather than silent corruption.
- **Full audit lineage.** Every state value traces back through a chain of versioned transitions with actor attribution and timestamps.
- **Revertible state.** Because every write is a versioned transition, any state can be rewound to any prior snapshot without data loss.
- **Namespace isolation.** Agent A's state namespace is physically separate from agent B's — cross-agent state contamination is structurally impossible.
- **Replay-safe reads.** `StateVersionedRead` artifacts can be replayed deterministically without rerunning the original computation.

### Why It Is Critical

Shared mutable state is the most common source of multi-agent bugs: race conditions, stale reads, and silent overwrites. L4 turns state into an append-only versioned log with conflict detection, giving the system the same guarantees as a database transaction log — but for agent state.

---

## L5 — Safety

### Sovereignty Assertion

L5 is the **constitutional enforcement layer**. It validates that all other layers comply with their sovereignty assertions, enforces SSOT (Single Source of Truth) governance, operates the HITL escalation pipeline, and maintains the safety audit registry. It is the layer that makes the architecture self-enforcing rather than merely documented.

### Hardening Criteria

| Criterion | Enforcement module |
|---|---|
| Layer sovereignty enforced via AST analysis | `enforcement/layer_sovereignty_enforcer.py` |
| Upward imports (L-low → L-high) detected and blocked | `LAYER_HIERARCHY` dict + CI gate |
| SSOT structure validation (blueprint compliance) | `enforcement/ssot_structure_validation_enforcer.py` |
| SSOT import paths enforced | `enforcement/ssot_import_enforcer.py` |
| SSOT scanner for drift detection | `enforcement/ssot_scanner_enforcer.py` |
| SSOT guardrail (runtime) | `enforcement/ssot_guardrail.py` |
| Policy enforcement point (PEP) | `enforcement/policy_enforcement_point.py` |
| Policy action contract with 5 action classes | `enforcement/policy_action_contract.py` |
| HITL gate for escalation decisions | `enforcement/hitl_gate.py` |
| Human escalation record registry | `escalation/human_escalation.py` |
| Escalation trigger taxonomy (5 types) | `EscalationTriggerType` enum |
| Reviewer outcome taxonomy (6 outcomes) | `ReviewerOutcome` enum |
| Safety audit record registry | `audit/safety_audit_registry.py` |
| Safety audit emitter | `audit/safety_audit_emitter.py` |
| Input validation and membrane guardrails | `enforcement/input_validation_guardrail.py`, `input_membrane_guardrail.py` |
| Circuit breaker gate | `enforcement/circuit_breaker_gate.py` |
| Oscillation firewall (infinite loop prevention) | `enforcement/oscillation_firewall_gate.py` |
| Phase acceptance guardrail | `enforcement/phase_acceptance_guardrail.py` |
| Module collision detection | `enforcement/module_collision_guardrail.py` |
| RAG guardrail | `enforcement/rag_guardrail.py` |
| PII vault enforcer | `enforcement/pii_vault_enforcer.py` |
| Dependency graph enforcer | `enforcement/dependency_graph_enforcer.py` |
| Three-tier compliance enforcer | `enforcement/three_tier_compliance_enforcer.py` |
| Critical dual enforcement audit | `enforcement/critical_dual_enforcement_audit_enforcer.py` |
| 80 reasoning modules for domain-specific safety | `reasoning/` |
| 47 validators | `validators/` |
| Secure error handler (no information leakage) | `enforcement/secure_error_handler_enforcer.py` |
| Canary token defense | `enforcement/canary_token_defense_strategy.py` |
| Airlock trimmer (output airlock) | `enforcement/airlock_guardrail.py` |

### 100% Capability Coverage Unlocks

- **Self-enforcing architecture.** Layer boundary violations are detected by AST analysis at commit time, not discovered in production. Architectural drift becomes a CI failure.
- **SSOT governance at scale.** Every configuration value, path constant, and schema field has exactly one authoritative source. Drift from SSOT is detected and blocked, not just documented.
- **Typed escalation.** Human review is triggered by a taxonomy of conditions (`IRREVERSIBLE_DESTRUCTIVE`, `POLICY_AMBIGUITY`, `PRIVILEGED_ACTION`, `SENSITIVE_REASONING`, `DISPUTED_AUTHORIZATION`) — not by ad hoc `if uncertain: ask_human()` scattered through agent logic.
- **Immutable safety audit log.** Every guardrail activation, policy block, and human review decision is recorded in a typed registry queryable by run ID, trace ID, and policy hash.
- **Circuit breaking.** Oscillating agents (looping between states) are detected by the oscillation firewall and halted before consuming unbounded resources.

### Why It Is Critical

Safety enforcement embedded in individual agents is fragile — it can be bypassed, forgotten, or inconsistently applied. L5 externalizes enforcement: the same layer that enforces boundary contracts, SSOT compliance, and HITL escalation is the layer that cannot be bypassed without violating layer sovereignty. Safety becomes structural rather than behavioral.

---

## L6 — Observability

### Sovereignty Assertion

L6 is the **system truth layer**. It aggregates execution signals from all lower layers into queryable dashboards, latency budget enforcement, and health state computation. It is read-only from the perspective of the execution path — it observes without interfering.

### Hardening Criteria

| Criterion | Enforcement module |
|---|---|
| Dashboard snapshots with 12 runtime metrics | `dashboard/dashboard_aggregate.py` |
| Health state enumeration (HEALTHY/DEGRADED/CRITICAL/UNKNOWN) | `HealthFlag` enum |
| Budget violation error on latency SLA breach | `BudgetViolationError` |
| Performance records per stage with latency budget | `performance/performance_registry.py` |
| Stage ownership tracked in performance records | `StageOwner` |
| Throughput metrics (routing, reasoning, execution) | `DashboardSnapshot` fields |
| Latency metrics (median and p95 per stage) | `median_latency_by_stage`, `p95_latency_by_stage` |
| Policy block rate tracked | `policy_block_rate` field |
| Human escalation rate tracked | `human_escalation_rate` field |
| Execution success/failure rate tracked | `execution_success_rate`, `execution_failure_rate` |
| Queue depth summary | `queue_depth_summary` field |
| Bottleneck analysis query | `get_bottleneck_analysis()` |
| System health summary query | `get_system_health_summary()` |
| Active run count | `active_run_count` field |
| Snapshot persistence | `snapshot_persisted` ADG edge |
| Dashboard aggregation from telemetry window | `TelemetryWindow` + `DashboardPolicy` |
| Golden evaluation framework | `golden_evaluation/` |
| Performance measurement by stage timing | `measure_stage_timing()` |

### 100% Capability Coverage Unlocks

- **SLA enforcement with hard failure.** `LatencyBudget` + `BudgetViolationError` means latency regressions produce errors, not just metrics — they block the execution path.
- **Cross-layer health composition.** `DashboardSnapshot` aggregates signals from L0 (routing throughput) through L5 (policy block rate, human escalation rate) into a single queryable health artifact.
- **Proactive degradation detection.** The system transitions from `HEALTHY` to `DEGRADED` before reaching `CRITICAL`, providing an actionable window for intervention.
- **Bottleneck attribution.** `get_bottleneck_analysis()` identifies which layer or stage is consuming latency budget, enabling targeted optimization rather than global tuning.
- **Historical performance baselines.** Performance records persist across runs, enabling regression detection without external monitoring infrastructure.

### Why It Is Critical

Agentic systems without structured observability fail invisibly. Agents retry silently, latency drifts upward slowly, and policy blocks go unnoticed until downstream failures surface. L6 makes the health of every layer a first-class, typed artifact — queryable, alertable, and comparable across runs. It closes the feedback loop that makes the system self-aware.

---

## Capability Coverage Matrix

The following matrix shows what hardening criteria must be satisfied at 100% for each layer, and what failure mode each criterion prevents.

| Layer | Hardening Criterion | Failure Mode Prevented |
|---|---|---|
| L0 | RoutingContract on every decision | Untraced, ungoverned execution paths |
| L0 | Policy hash locked at contract creation | Policy-blind routing decisions |
| L0 | Capacity governance before route selection | Thundering herd / cascading overload |
| L0 | Replay key and determinism digest emitted | Non-reproducible routing decisions |
| L1 | Propose-only sovereignty | Cognition-triggered side effects |
| L1 | Plan checkpoints enforced | Continuation on invalid preconditions |
| L1 | Reasoning patterns versioned and validated | Untracked cognitive drift over time |
| L2 | All writes through UniversalWriteGateway | Unaudited filesystem mutations |
| L2 | All LLM calls through SovereignLLMGateway | Unlogged model invocations |
| L2 | Provider substitution prohibited | Silent fallback masking infrastructure failure |
| L2 | Failure classification taxonomy | Generic retry hiding root cause |
| L2 | Hash-chain audit log | Tamper-evident mutation record |
| L3 | All handoffs through CapabilityRegistry | Hidden agent-to-agent dependencies |
| L3 | Capability token required for dispatch | Unauthorized cross-agent invocation |
| L3 | Workflow visualization recorded | Unobservable execution DAG |
| L4 | Versioned state transitions | Silent state overwrites |
| L4 | Conflict detection | Race conditions in concurrent agents |
| L4 | Snapshot lineage enforced | Orphaned, unrecoverable state |
| L5 | Layer sovereignty via AST analysis | Architectural drift undetected in production |
| L5 | SSOT guardrail | Configuration inconsistency across modules |
| L5 | HITL escalation with trigger taxonomy | Irreversible actions without human review |
| L5 | Safety audit registry | Unaudited policy decisions |
| L5 | Circuit breaker + oscillation firewall | Runaway agent loops |
| L6 | Latency budget with hard failure | Silent SLA degradation |
| L6 | Health flag enumeration | Binary up/down health model |
| L6 | Policy block rate tracking | Governance load invisible to operators |
| L6 | Bottleneck analysis | Untargeted performance optimization |

---

## Enforcement Infrastructure

The architecture is enforced by a CI pipeline with 21 workflow files and a single entrypoint.

```
python ops_scripts/ci/run_contract_gates.py
```

| CI Gate | Layer(s) | What it enforces |
|---|---|---|
| `layer-sovereignty-enforcement.yml` | L0–L6 | No upward imports between layers |
| `adg-ci-gates.yml` | All | ADG freshness, schema, proof artifact truth |
| `adg-antipattern-ci.yml` | All | Anti-pattern violations blocked on PR |
| `adg-invariant-scan.yml` | All | ADG edge invariants stable |
| `ci-integrity-gate.yml` | All | Test count invariants, skip registry |
| `safe-remediation-gate.yml` | All | 5-gate repair discipline enforced |
| `ssot_verify.yml` | L4, L5 | SSOT sovereignty not violated |
| `environment-contract.yml` | L2 | Subprocess paths, env vars stable |
| `policy-drift-classification.yml` | L0, L5 | Policy hash regressions classified |
| `agent-deletion-guard.yml` | L3 | Agent deletion authorization required |
| `guardian-tests.yml` | L5 | Guardian exemption ceiling enforced |
| `import-resolution-guardian.yml` | All | Dead/forbidden imports blocked |
| `skip-registry-convergence.yml` | Tests | Unregistered skips block convergence |
| `adg-proof-artifact-truthfulness.yml` | All | Evidence artifacts match raw ADG output |
| `structure-invariants.yml` | All | Module count and structure frozen |
| `spine-determinism-guard.yml` | L0, L2 | Determinism digest stable across runs |
| `timeout-progress-enforcement.yml` | All | All queries have timeout and progress |

---

## Architecture Dependency Graph (ADG)

The ADG is not documentation. It is an executable verification artifact built from AST analysis of the entire codebase.

**What it models:**
- Module imports (directed)
- Symbol-level imports
- Class inheritance and mixin realization
- Decorator attachment
- Registry lookup and registration
- Factory and provider resolution
- CLI entrypoint → function chains
- Test → production coverage edges

**What it enforces:**
- Layer boundary direction (L-low cannot import L-high)
- Gateway bypass attempts (direct LLM/write calls without gateway)
- Dependency cycles
- Dead code and orphan modules
- Structural drift between releases

**Current scale:** 8,487 modules, 235,188 edges across the full platform.

The ADG is stored as four artifacts:

| Artifact | Purpose |
|---|---|
| `adg_indexed_<ts>.sqlite` | Primary queryable DB |
| `adg_snapshot_<ts>.json` | Metrics and counts |
| `adg_file_graph_<ts>.json` | Import and call chains |
| `adg_governance_graph_<ts>.json` | Layer violation records |

---

## Why the Layer Separation Is Non-Negotiable

Each layer separation eliminates a class of failure mode that cannot be eliminated any other way.

| Separation | Failure mode eliminated |
|---|---|
| L0 from L1 | Agents cannot route themselves — circular routing is structurally impossible |
| L1 from L2 | Reasoning cannot produce side effects — cognitive failures are typed errors, not mutations |
| L2 from L3 | Execution cannot dispatch agents directly — all agent calls are capability-registry-mediated |
| L3 from L4 | Orchestration cannot write state directly — all persistence is versioned and conflict-detected |
| L4 from L5 | State layer cannot self-validate — safety enforcement is independent of the data it governs |
| L5 from L6 | Safety enforcement cannot silence its own observability — health signals are structurally upstream |

Each of these separations is verified by AST analysis on every commit. They are not conventions — they are enforced invariants.

---

## Reading Order

To understand this system from architecture through enforcement to application:

1. `README.md` — Platform overview and working applications
2. This document — Layer-by-layer hardening criteria and capabilities
3. `agentic_core/L0_routing/enforcement/routing_contract.py` — RoutingContract (the entry contract)
4. `agentic_core/L2_execution/UniversalWriteGateway.py` — Write gateway (the mutation authority)
5. `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` — LLM gateway (model governance)
6. `agentic_core/L3_orchestration/contracts/agent_handoff.py` — HandoffDispatcher (agent coordination)
7. `agentic_core/L5_safety/enforcement/layer_sovereignty_enforcer.py` — AST boundary enforcement
8. `agentic_core/L6_observability/dashboard/dashboard_aggregate.py` — System health model
9. `ops_scripts/ci/run_contract_gates.py` — CI enforcement entrypoint
