# execute_ssot.py — Capability Assessment (Current Repo State)

Assessment of what `agentic_core/L0_routing/scripts/execute_ssot.py` currently uses from `agentic_core` and what rich capabilities it is not yet exploiting, based on actual verified source code.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Currently Used

### L0 — Routing & Enforcement
| Import | Role |
|---|---|
| `mutation_prohibition.assert_no_persistent_write` | Guards every atomic write in `RuntimeStateManager.save()` and `save_comprehensive_reports()` |
| `mutation_prohibition.{IMMUTABLE_ROOTS, get_default_protected_root_policy, SourceMutationBlocked, enforce_protected_root}` | Fence self-check + startup probe |
| `enforcement.runtime_guard.runtime_guard` | Decorator on `with_retry` and `_legacy_main` |
| `enforcement.execution_gateway.V15ExecutionGateway` | V15 audit trail in LOG_ONLY mode |
| `enforcement.traceability_contracts.generate_trace_id` | Correlation ID for `SurgicalManifest` |
| `types.guardian_contract.is_v15_enforced` | V15 enforcement toggle |
| `types.determinism_types.{SurgicalManifest, FixConstraint}` | V15 manifest construction |
| `seams.safety_validators_seam.load_cognitive_disposition_agent` | Lazy CDA loader |
| `utils.subprocess_runner.{invoke_orchestrator_mission, invoke_arch_governor, invoke_agent_roster_validation}` | Subprocess delegation to L3 / arch governor / roster validation |
| `utils.discovery.Full_Agent_discovery.discover_all_agents` | Live agent scan fallback |
| `scripts.runtime_state_digest.{DIGEST_SCHEMA_VERSION, compute_runtime_state_digest}` | SHA-256 digest of runtime state |

### L2 — Execution
| Import | Role |
|---|---|
| `tools.safe_subprocess.safe_subprocess_run` | Windows UTF-8 `chcp 65001` invocation |
| `tools.write_gateway` | Inspected for `allow_override` + `enforce_protected_root` in fence self-check |

> **NOT used at all**: `L2_execution.healers.*` — the entire 3-tier healing system is unreachable from `execute_ssot.py`.

### L5 — Safety Reasoning
| Agent | Phase |
|---|---|
| `FilesystemSSOTReconcilerAgent` | Phase 1 — SSOT drift detection |
| `LocationAgent` / `LocationValidatorAgent` | Phase 1 — location validation + auto-heal |
| `FileClassificationAgent` | Phase 1 early detection + Phase 2.5 sovereignty purge |
| `HierarchyAgent` | Phase 2.5 — structural alignment |
| `ArchitectureGovernorAgent` | Phase 3 — territory audit + Phase 4 healing plan |
| `GravityLeakRepairAgent` | Phase 3.5 — layer inversion detection |
| `SystemArchitectAgent` | Phase 3 — circular dependency validation |
| `CognitiveDispositionAgent` | Phase 1 opt-in via `--enable-cda` |
| `RootHygieneAgent` | Phase 4.5 — root hygiene scan |

### L6 — Observability
| Import | Role |
|---|---|
| `ObservabilityProbeExecutor` | Phase 4.5 aliased as `conversational_repair` |

### L3 — Orchestration (thin / plan-mode only)
| Import | Role |
|---|---|
| `arbitration.{ArbitrationInput, Arbitrator, run_all_advisors}` | `--plan --arbitrate` flag only |
| `ptc.{ToolCall, ToolInvoker, registry, tool_call_store}` | `--plan --ptc` flag only |
| `try_summon_orchestrator` via subprocess | `--domains` mode; immediately falls back if unavailable |

### Base / Cross-cutting
| Import | Role |
|---|---|
| `utils.decorators_compat_util.{standard_heal, HEAL_RESULT_SCHEMA}` | Decorator on `execute_phase3_validation` |
| `base_agents.{IHealerProtocol, LegacyAgentAdapter}` | Dynamic `load_agents()` dispatch |

---

## Critical Gaps — Not Used

### 🔴 GAP 1: L2 Healing Tier System (Biggest Gap)

**The entire `agentic_core.L2_execution.healers` package is unused.**

The package is a fully-implemented, tested (16 passing tests), 3-tier LLM dispatch system:

| Module | What it does |
|---|---|
| `healing_tier_types.py` | `HealingTier` enum (`LOCAL_AGENT`, `QWEN_VLLM`, `GEMINI_2_5_PRO`), frozen `HealingInput`, `HealingDecision`, `FailureSignal` dataclasses |
| `healing_tier_config.py` | Validated, immutable `HealingTierConfig` (thresholds X=0.75/Y=0.40, model IDs `qwen2.5-coder-32b-instruct` / `gemini-2.5-pro`) |
| `healing_tier_router.py` | **Single choke point** — deterministic 5-factor scoring (failure class prior, blast radius, historical success rate, tool readiness, retry decay) → tier selection |
| `healing_tier_dispatcher.py` | `dispatch_healing()` — routes `HealingDecision.tier` to the correct provider via injectable `HealingProviderInvoker` |
| `healing_provider_adapters.py` | `QwenInvokerAdapter` (real OpenAI-compatible SDK calls), `GeminiInvokerAdapter` (real `google.generativeai` SDK calls), `LocalAgentAdapter` |
| `tiering_allowlist.py` | Allowed agent names for tiered healing |
| `{classification,drift_detection,hierarchy_compliance,architecture_governance}_healer.py` | Domain-specific healer implementations |

**Current gap in `execute_ssot.py`:**
- `AutonomousDecisionEngine.should_proceed_with_healing()` has `enable_llm=True` path that returns `"LLM-ARBITRATED-FLASH"` / `"REASONING-RECOVERY-PRO"` strings — but makes **zero actual LLM calls**. It is phantom arbitration.
- `historical_success_rate=0.8` is hardcoded in `calculate_healing_confidence()` — the router's `FAILURE_CLASS_PRIORS` dict has per-type priors already computed.
- Phase 2 `execute_phase2_reconciliation` dispatches agents via `agents["key"]` dict lookup with no tier escalation path. A failed agent appends to `failed_fixes[]` and stops.

**Fix:** Replace `AutonomousDecisionEngine.calculate_healing_confidence()` + `should_proceed_with_healing()` with calls to `route_healing_tier()` from `healing_tier_router`, and wire `dispatch_healing()` into Phase 2 agent invocation using the real `QwenInvokerAdapter` / `GeminiInvokerAdapter`.

---

### 🔴 GAP 2: `healing_tier_router._HISTORICAL_SUCCESS_RATES` is stub-backed

The router's `get_historical_success_rate()` currently uses an in-memory dict `_HISTORICAL_SUCCESS_RATES` with no persistence — "backed by L4 in production" per the comment.

`agentic_core.L4_state.memory.reasoning_memory` and `sovereign_reasoning_memory_ledger` exist to back this. Neither is wired.

---

### 🟠 GAP 3: L4 State — No Cross-Run Memory

`RuntimeStateManager` is a flat in-memory JSON dict written to `runtime_state.json`. Each run starts completely blind.

| L4 module | Value |
|---|---|
| `reasoning_memory.py` (9.8KB) | Persist violation patterns and healing outcomes across runs → feed `healing_tier_router.set_historical_success_rate()` |
| `verifiable_checkpoint_manager.py` (7.7KB) | Checkpoint state between phases so a crash in Phase 4 can resume from Phase 3 checkpoint |
| `sovereign_reasoning_memory_ledger.py` (3KB) | Auditable ledger of every healing decision over time |
| `semantic_cache_manager.py` (27KB) | Cache violation classification per file hash — skip rescanning unchanged files in Phase 1 |

---

### 🟠 GAP 4: L3 Orchestration — DAG Not Used for Phase Parallelism

The 5-phase pipeline is a hardcoded linear sequence. Phase 1 runs `FilesystemSSOTReconcilerAgent` → `LocationAgent` → `FileClassificationAgent` serially. The `dag_manager.py` (8.9KB) and `decomposition_orchestrator.py` (14KB) exist and are unused.

Phase 1 location scan and Phase 1 file classification have no dependency on each other and could run in parallel today via `dag_manager`.

The L3 `try_summon_orchestrator` shim used in `--domains` mode immediately falls back on error — it never actually routes through `orchestrator_engine.py` (32KB) in production.

---

### 🟠 GAP 5: L1 Cognition — `episodic_manager` for Evidence-Based Confidence

`AutonomousDecisionEngine.calculate_healing_confidence()` uses hardcoded weights and `historical_success_rate=0.8`.

`agentic_core.L1_cognition.engines.episodic_manager` (9.5KB) is built to record and retrieve episodic healing outcomes per agent × violation type. Wiring it would replace the hardcoded `0.8` with actual evidence.

`capability_analyzer.py` (11.4KB) could dynamically verify which agents support which failure types instead of the hardcoded `CANONICAL_ROSTER_KEYS` + `AGENT_DEPENDENCIES` dicts.

---

### 🟡 GAP 6: Mixins — Hand-Rolled Safety vs. Tested Mixins

`SovereignDecisionEngine` hand-rolls: cycle detection, budget counter, atomic locking, stack depth tracking, and exponential-backoff retry (`with_retry`).

| Mixin | What it replaces |
|---|---|
| `circuit_breaker_mixin.py` (7.9KB) | Replaces manual `_max_healing_operations` + `_atomic_lock` with a proper half-open circuit breaker |
| `audit_trail_mixin.py` (14KB) | Replaces `decisions_made[]` list with a structured, replayable, serializable audit trail |
| `tracing_mixin.py` (11KB) | V15 trace IDs are generated in `_v15_build_ssot_manifest()` but never propagated to child agent calls |
| `cost_mixin.py` (15.9KB) | No token cost accounting for healing decisions (even phantom ones) |
| `meta_learning_mixin.py` (4KB) | `update_meta_learning()` in `RuntimeStateManager` is a no-op stub; real mixin updates strategy weights from outcomes |

---

### 🟡 GAP 7: L6 Dashboard — Compliance JSON Never Rendered

`save_comprehensive_reports()` writes `compliance_report_{territory}.json` + `executive_summary_{territory}.md` to `logs/compliance_reports/`.

`agentic_core.L6_observability.dashboards.dashboard_generator.py` (38KB) is a full HTML dashboard generator with a SSOT YAML schema, CSS, and JS. It is never invoked from `execute_ssot.py`.

---

### 🟡 GAP 8: L2 `write_set_enforcer` — No Pre-Declaration of Phase 2 Writes

Phase 2 `execute_phase2_reconciliation` calls `agent.heal(violation)` with no pre-declaration of which files may be written.

`agentic_core.L2_execution.enforcement.write_set_enforcer.py` enforces a declared write-set, hard-failing any write outside it before it happens. Currently the only protection is `assert_no_persistent_write` on `L0` immutable roots — there's no scope containment for the writable targets.

---

### 🟢 GAP 9: Knowledge Layer — Playbook-Driven Healing

`agentic_core.knowledge.healing/` (2 items) provides playbook-based healing strategies per violation type. `calculate_healing_confidence()` uses only heuristic weights; the knowledge layer could provide evidence-based priors indexed by violation taxonomy.

---

## Priority Table

| P | Gap | What to wire | Estimated scope |
|---|---|---|---|
| 🔴 **P0** | L2 Healing Tier Router in Phase 2 dispatch | `route_healing_tier()` → `dispatch_healing()` → `QwenInvokerAdapter` / `GeminiInvokerAdapter` | 1 file, ~60 lines |
| 🔴 **P0** | Replace phantom LLM in `AutonomousDecisionEngine` | Replace `should_proceed_with_healing()` branch logic with `HealingInput` + `route_healing_tier()` | 1 file, ~40 lines |
| 🟠 **P1** | L4 `reasoning_memory` → `set_historical_success_rate()` | Post-heal: record `(error_signature, success)` into `reasoning_memory`; pre-heal: query it | 2 files, ~30 lines |
| 🟠 **P1** | `verifiable_checkpoint_manager` between phases | Checkpoint after Phase 1 and Phase 3; resume on crash | 1 file, ~20 lines |
| 🟠 **P2** | `episodic_manager` for confidence calibration | Feed historical success per agent × violation type into `calculate_healing_confidence()` | 2 files, ~30 lines |
| 🟡 **P2** | `circuit_breaker_mixin` on `SovereignDecisionEngine` | Replace hand-rolled `_atomic_lock` + `_max_healing_operations` | 1 file, ~25 lines |
| 🟡 **P2** | `audit_trail_mixin` on decision engine | Structured replayable audit trail for decisions | 1 file, ~15 lines |
| 🟡 **P3** | L6 dashboard invocation after `save_comprehensive_reports()` | Call `dashboard_generator` with compliance JSON | 1 file, ~10 lines |
| 🟡 **P3** | `write_set_enforcer` pre-declaration in Phase 2 | Declare write-set before Phase 2 loop begins | 1 file, ~15 lines |
| 🟢 **P4** | DAG-based Phase 1 parallelism | Route Phase 1 agents through `dag_manager` | Multi-file, high effort |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

