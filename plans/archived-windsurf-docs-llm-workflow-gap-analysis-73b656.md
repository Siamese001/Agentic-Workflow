---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\llm-workflow-gap-analysis-73b656.md'
original_relative_path: 'llm-workflow-gap-analysis-73b656.md'
source_sha256: 652aee75cbc55fd4d6c8962c28193c3f2a8486f560e9a90456a01858707555f0
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-13'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# LLM Agentic Workflow Gap Analysis & Implementation Plan

Gap analysis of the 10 target agentic LLM workflow patterns (9 from screenshot + ReACT) against the existing codebase, with a phased implementation plan to close all gaps.

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


## Pattern Inventory & Coverage Assessment

| # | Pattern | Best Suited For | Existing Coverage | Key Gaps |
|---|---------|----------------|-------------------|----------|
| 1 | **Prompt Chaining** | Multi-step apps, sequential agents | ~60% — `ResumeOrchestratorEngine` chains engines; `SubatomicHopAgent` has hop-chaining | No reusable `PromptChain` class; no explicit gate/fail logic |
| 2 | **Parallelization** | Guardrails, automating evals | ~40% — `DAGManager` (networkx), `ConvergenceEngine` | No aggregator class; no fan-out/fan-in pattern formalized |
| 3 | **Orchestrator-Worker** | Agentic RAG, coding agents | ~65% — `OrchestratorEngine` facade, `DecompositionOrchestrator`, `NervousSystemAgent` | Pattern is heal-scoped; no clean delegating API for general task dispatch |
| 4 | **Evaluator-Optimizer** | Data science agents, monitoring | ~35% — `ReflectionEngine` (scoring only), `ContentQualityEngine` + `ContentOptimizerEngine` exist | No wired generator→evaluator→revise feedback loop |
| 5 | **Router** | Customer support, MAD | ~70% — `ShadowRouterClassifier`, `EscalationRouter`, `TimeshiftRouter`, `ActionRouter` | Routers are infra-internal; no user-input→specialized-agent dispatch pattern |
| 6 | **Autonomous Workflow** | Embodied agents, CUA | ~40% — `AutonomousExecutionEngine` (self-healing only), `RLCoordinatorOrchestrator` | Scoped to code healing; no reusable environment-feedback action loop |
| 7 | **Reflexion** | Complex data monitoring, full-stack agents | ~20% — `ReflectionEngine` stub (post-cycle score only) | Missing: critique LLM call, verbal feedback storage, revision-with-memory loop |
| 8 | **Rewoo** | Deep research agents, multi-step QA | ~15% — `ResumePlanningEngine` (planner only) | No Planner→task-list→Solver→Worker→update chain at all |
| 9 | **Plan and Execute** | BPA, data pipeline orchestration | ~55% — `DecompositionOrchestrator` creates `MissionPlan`+`AtomicTask` | Missing: single-task-agent dispatch loop, replan-on-failure branch |
| 10 | **ReACT** *(required)* | Tool-use agents, complex reasoning | ~70% — `ReActEngine` (Think→Act→Observe loop in `react_config.py`), `ReActStrategy` | `ReActStrategy` uses mock logic; not wired to real `ToolRegistry`; lives in `config/` not `engines/` |

---

## Gap Severity Tiers

**Tier 1 – Missing Pattern (build new)**
- Rewoo (`~15%`) — No planner-solver-worker chain
- Reflexion (`~20%`) — Only a stub scorer

**Tier 2 – Components exist but unconnected (wire + extend)**
- Evaluator-Optimizer (`~35%`) — Generator + evaluator exist; feedback loop missing
- Parallelization (`~40%`) — DAG infra exists; aggregator + fan-out formalization missing
- Autonomous Workflow (`~40%`) — Engine exists but scoped to code healing only

**Tier 3 – Mostly implemented (harden + expose)**
- ReACT (`~70%`) — `ReActEngine` is functional; `ReActStrategy` is mocked; wrong module location (`config/` vs `engines/`)
- Router (`~70%`) — Internal routing mature; public classification→dispatch API missing
- Orchestrator-Worker (`~65%`) — Decomposition exists; clean general-purpose API missing
- Plan and Execute (`~55%`) — Decomposition present; replan loop absent
- Prompt Chaining (`~60%`) — Implicit in pipelines; no first-class `PromptChain` abstraction

---

## File Locations of Key Existing Assets

| Asset | Path |
|-------|------|
| `ReActEngine` (full loop) | `agentic_core/L1_cognition/config/react_config.py` |
| `ReActStrategy` (mocked) | `agentic_core/L1_cognition/enforcement/react_strategy.py` |
| `ReflectionEngine` (stub) | `apps_rg/engines/reflection_engine.py` |
| `DecompositionOrchestrator` | `agentic_core/L3_orchestration/engines/decomposition_orchestrator.py` |
| `DAGManager` | `agentic_core/L3_orchestration/engines/dag_manager.py` |
| `AutonomousExecutionEngine` | `agentic_core/L3_orchestration/engines/autonomous_execution_engine.py` |
| `OrchestratorEngine` (facade) | `agentic_core/L3_orchestration/engines/orchestrator_engine.py` |
| `RecursiveOrchestrator` | `agentic_core/L3_orchestration/engines/recursive_orchestrator.py` |
| `ContentQualityEngine` | `apps_rg/engines/content_quality_engine.py` |
| `ContentOptimizerEngine` | `apps_rg/engines/content_optimizer_engine.py` |
| `ResumePlanningEngine` | `apps_rg/engines/resume_planning_engine.py` |
| `ResumeOrchestratorEngine` | `apps_rg/engines/resume_orchestrator_engine.py` |
| Feedback loop types | `apps_shared/types/feedback_loop_types.py` |

---

## Phased Implementation Plan

### Phase A — Tier 1: Build Missing Patterns (Rewoo + Reflexion)

**A1 — Rewoo Engine** (`agentic_core/L3_orchestration/engines/rewoo_engine.py`)
- `RewooPlanner`: generates ordered task list with reasoning annotations
- `RewooSolver`: executes each task with tool access, stores intermediate results
- `RewooWorker`: updates task results back into planner context
- Wire into `rl_coordinator_orchestrator.py` as a new coordinator strategy
- New type: `RewooTaskList`, `RewooContext` in `agentic_core/L3_orchestration/types/`

**A2 — Reflexion Engine** (`agentic_core/L3_orchestration/engines/reflexion_engine.py`)
- Replace stub `ReflectionEngine` with full Reflexion loop:
  1. Generator LLM call → initial response
  2. Evaluator LLM call → verbal critique (not just a score)
  3. Memory buffer: store critique history across iterations
  4. Revisor: uses critique + memory to generate revised response
  5. Loop up to `n` times with convergence gate
- Delegate scoring back to existing `ReflectionEngine` for score signal
- New types: `ReflexionMemory`, `ReflexionCritique` in `apps_rg/types/`

---

### Phase B — Tier 2: Wire Unconnected Components

**B1 — Evaluator-Optimizer Loop** (`agentic_core/L3_orchestration/engines/evaluator_optimizer_engine.py`)
- Connect `ContentQualityEngine` (evaluator) → `ContentOptimizerEngine` (optimizer) in a loop
- Generator produces response; evaluator scores + flags `Rejected`; optimizer revises until threshold
- Expose as standalone `EvaluatorOptimizerEngine` wrapping existing engines
- Reuse `FeedbackLoopTypes` from `apps_shared/types/feedback_loop_types.py`

**B2 — Parallelization Engine** (`agentic_core/L3_orchestration/engines/parallelization_engine.py`)
- Wrap `DAGManager` fan-out into a clean `ParallelizationEngine` class
- Support two modes: **Sectioning** (split task → parallel LLM calls) and **Sampling** (same task N times → vote/aggregate)
- `Aggregator` step: majority-vote or LLM-synthesize parallel outputs
- Add `asyncio.gather` concurrency for parallel branch execution

**B3 — Autonomous Workflow Generalization** (`agentic_core/L3_orchestration/engines/autonomous_workflow_engine.py`)
- Refactor `AutonomousExecutionEngine` to accept a pluggable `EnvironmentToolSet` interface
- Decouple from filesystem/heal-specific logic
- Expose clean `Action → EnvironmentTools → Feedback → Stop` loop via protocol
- Support both `Stop` signal and `max_iterations` convergence gate

---

### Phase C — Tier 3: Harden & Expose

**C1 — ReACT Wiring** (priority: highest in Tier 3)
- Move `ReActEngine` from `react_config.py` → `agentic_core/L1_cognition/engines/react_engine.py` (correct layer placement)
- Replace mock logic in `ReActStrategy` with real delegation to `ReActEngine`
- Wire `ToolRegistry` to `act_fn` parameter in `ReActEngine.run()`
- Register `ReActStrategy` as a `ReasoningMode.REACT` handler in `CognitiveNode`

**C2 — Router Pattern** (`agentic_core/L0_routing/engines/agentic_router.py`)
- Create `AgenticRouter` that classifies user/task input using `ShadowRouterClassifier` logic
- Maps classified intent → registered specialist agent/workflow
- Support MAD (Multi-Agent Debate) as a routing target
- Expose as a first-class workflow pattern via `L0_routing`

**C3 — Prompt Chaining Abstraction** (`agentic_core/L3_orchestration/engines/prompt_chain_engine.py`)
- Extract implicit chaining from `ResumeOrchestratorEngine` into `PromptChainEngine`
- Explicit `Gate` node: evaluates intermediate output, routes to `pass`/`fail` branch
- Each step's output is injected as context into the next step's prompt
- Configurable chain definition (list of callables + gate conditions)

**C4 — Orchestrator-Worker Clean API** (extend `decomposition_orchestrator.py`)
- Add `SynthesizerNode` to aggregate worker outputs back to orchestrator
- Add explicit `WorkerPool` interface: `register_worker(name, fn)`, `dispatch(task)`, `collect_results()`
- Clean separation: `Orchestrator` → question → `Workers` → answers → `Synthesizer` → output

**C5 — Plan and Execute: Replan Loop** (extend `decomposition_orchestrator.py`)
- Add `replan_on_failure(failed_task, reason) -> updated_plan` method
- Loop: Planner creates task list → dispatch to `SingleTaskAgents` → on failure → Replan → resume
- Add `ReplanArtifact` type to track plan mutations for observability

---

### Phase D — Tests & Invariants

For each new/modified engine, add:
- **Unit test** in `tests/architecture/` verifying pattern contract (input → output shape, loop terminates)
- **Invariant assertion**: max iterations respected, no infinite loops
- **Architecture test**: verify each new engine file resides in correct layer per `structure_blueprint`

---

## Suggested Sequencing

```
Week 1: A1 (Rewoo) + A2 (Reflexion)         ← highest gap, zero foundation
Week 2: B1 (Eval-Optimizer) + C1 (ReACT)    ← wiring + highest-priority Tier  3: B2 (Parallelization) + B3 (Autonomous)
Week 4: C2 (Router) + C3 (Prompt Chaining) + C4 (Orch-Worker) + C5 (Plan+Execute)
Week 5: Phase D tests + architecture invariants for all 10 patterns
```

---

## Summary Table

| Pattern | Current State | Target State | Effort |
|---------|--------------|-------------|--------|
| Prompt Chaining | Implicit in RG pipeline | `PromptChainEngine` with gate | S |
| Parallelization | DAG infra only | `ParallelizationEngine` + aggregator | M |
| Orchestrator-Worker | Heal-scoped | `WorkerPool` + `Synthesizer` clean API | M |
| Evaluator-Optimizer | Disconnected components | Wired feedback loop engine | M |
| Router | Internal routing only | `AgenticRouter` classification→dispatch | S |
| Autonomous Workflow | Heal-only loop | Pluggable env-tool action loop | M |
| Reflexion | Scoring stub only | Full critique→memory→revise loop | L |
| Rewoo | Not present | Planner→Solver→Worker chain | L |
| Plan and Execute | No replan | Replan loop + `SingleTaskAgent` dispatch | M |
| **ReACT** | Engine functional, strategy mocked | Strategy wired to real `ToolRegistry` | S |

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

