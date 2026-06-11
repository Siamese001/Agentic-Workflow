---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\plumbing-gap-analysis-94f211.md'
original_relative_path: 'plumbing-gap-analysis-94f211.md'
source_sha256: 8a0d13cd46f51fc02e85afede6306af067b05ff8a028941ced966baa48fd9e1e
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# AST Plumbing Gap Analysis & Implementation Plan (Refined)

Comprehensive AST-verified gap analysis of all cross-layer connections across agentic_core (L0–L6), apps_*, system_learning, and the evaluation framework — with detailed implementation specifications.

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


## Architecture Map (AST-Verified)

```
apps_lic / apps_rg
    └─ BaseSpineAdapter (apps_shared/spine/base_spine_adapter.py)
         └─ ExecutionOrchestrator (L0_routing/engines/execution_orchestrator.py)
              │  __init__(assembler, path_router, d0_engine, risk_gate,
              │           cid_registry, reentry_loop, vigilance_dispatcher, meta_bus)
              │  execute(intent_input: dict) -> dict
              │
              ├─ AirlockAssembler ✓ (L0_routing/engines/assembly_stage.py)
              ├─ PathRouter ✓ (L0_routing/engines/path_router.py)
              │    select_path(payload: GovernedPayload) -> Path[A/B/C/D]
              │
              ├─ [D0InjectionEngine] ← NULL STUB (G1-a)
              │    Real: L5_safety/enforcement/d0_injection_engine_enforcer.py
              │    render_d0(fences: tuple[RoleFence, ...]) -> str
              │
              ├─ [ConfCalibRiskGate] ← NULL STUB (G1-b)
              │    Real: L5_safety/enforcement/conf_calib_gate.py
              │    evaluate(payload_like, d0_injections: str) -> RiskDecision
              │
              ├─ [VigilanceDispatcher] ← NULL STUB (G1-c)
              │    Real: L6_observability/engines/vigilance_dispatcher.py
              │    dispatch(event: VigilanceEventArtifact, enqueue_fn: Callable)
              │
              ├─ [MetaLearningBus] ← NULL STUB (G1-d)
              │    Real: L0_routing/meta_control/meta_learning_bus.py
              │    enqueue(pkg: MetaLearningChangePackage)
              │    apply_next(apply_fn: Callable) -> tuple | None
              │
              └─ → L3 IOrchestrator ← NOT WIRED (G5)
                   Protocol: seams/orchestration_protocols.py::IOrchestrator
                   orchestrate(governed_payload, route_mode, trace_id,
                              policy_hash, allowed_tools) -> OrchestrationResult

L0_routing/seams/ (12 files)
  ├─ learning_seam.py           ✓ LearningArtifactIntent + LearningPersistenceService
  ├─ safety_enforcement_seam.py ✓ lazy-import L5 modules
  ├─ c0_context_retriever.py    ← C0ContextArtifact.load() returns None (G4)
  ├─ elevator_shaft_seam.py     ← load_context_jit() returns {} (G3)
  ├─ observability_seam.py      ← DEAD: L6_observability.meta_learning.* DNE (G6)
  └─ [10 more seams]            ← No contract tests (G16)

system_learning/
  ├─ pipelines/meta_learning_pipeline.py ✓ W2-W5 complete
  ├─ engines/l0_threshold_tuner.py → L0ThresholdChangePackage (G8)
  ├─ engines/l1_model_proposer.py → L1ModelChangePackage (G8)
  ├─ engines/healing_outcome_intake_adapter.py (G17)
  │    build_record(aggregator, created_utc, source) -> HealingOutcomeIntakeRecord
  │    persist_record(record) -> None
  └─ adapters/l1_meta_adapter.py (G11)
       extract_telemetry(meta_client_output) -> TelemetryRecord

L2_execution/healers/healing_tier_dispatcher.py (G19)
  dispatch_healing(healing_input, config, invoker) -> HealingOutcome

L1_cognition/engines/meta_client.py (G11)
  MetaLearningClient.recall(pattern_key) / .learn(pattern, outcome)
```

---

## Gap Inventory

### P0 — Broken Pipes (Immediate Runtime Failures)

| ID | Location | Description |
|----|----------|-------------|
| **G6** | `agentic_core/L0_routing/seams/observability_seam.py` | `load_meta_learning_agent()` references `agentic_core.L6_observability.meta_learning.MetaLearningAgent` — this subpackage does not exist in `L6_observability/`. Any call raises `ModuleNotFoundError`. |
| **G13** | `tests/unit/apps_rg/` and `tests/unit/agentic_core/L*` | apps_rg test collection errors (per Phase 11 history); blocks full-suite CI. |

### P1 — Unimplemented Stubs with Contract Gaps

| ID | Location | Description |
|----|----------|-------------|
| **G1** | `apps_lic/engines/lic_spine_adapter.py`, `apps_rg/engines/rg_spine_adapter.py` | Four null-object stubs per adapter: `_NullD0Engine`, `_NullRiskGate`, `_NullVigilanceDispatcher`, `_NullMetaBus`. Spine runs without risk-gating, without D0 injection, without vigilance events, and without meta-learning feedback. Explicitly documented "not yet wired." |
| **G5** | `agentic_core/L0_routing/engines/execution_orchestrator.py` | `ExecutionOrchestrator.execute()` assembles, routes (Path A/B/C/D), evaluates risk, and returns — but never calls any L3 orchestrator for Paths B/C/D. L3 is unreachable from the canonical spine entry. |
| **G7** | `agentic_core/L0_routing/meta_control/meta_learning_bus.py` + `meta_apply.py` | `MetaLearningBus.apply_next()` requires an injected `apply_fn`, but in neither spine adapter nor any boot sequence is `meta_apply.MetaApply.apply()` bound as that function. The bus is a queue with no consumer. |

### P2 — Partial/Placeholder Implementations

| ID | Location | Description |
|----|----------|-------------|
| **G2** | `agentic_core/L0_routing/engines/shadow_routing_wiring.py` | `observe_and_classify()` has TODO comments: "In a real implementation, this would emit to L6 bus" and "this would store to L4." Both L4 storage and L6 telemetry emission are bypassed. |
| **G3** | `agentic_core/L0_routing/seams/elevator_shaft_seam.py` | `load_context_jit()` returns `{}` unconditionally — a pure stub with no context loading logic. |
| **G4** | `agentic_core/L0_routing/seams/c0_context_retriever.py` | `C0ContextArtifact.load()` is a `classmethod` returning `None` unconditionally (placeholder). `C0ContextRetriever.retrieve()` raises `RuntimeError` on every call. C0 slot is always empty. |
| **G20** | `agentic_core/L3_orchestration/arbitration/` | `arbitration_contract.py`, `arbitrator.py`, `advisors.py`, `run_advisors.py` exist but have no integration tests confirming the arbitration contract is enforced when orchestrators dispute routes. |

### P3 — Test Coverage Gaps (Logic Exists, Tests Missing)

| ID | Location | Gap |
|----|----------|-----|
| **G10** | `tests/unit/agentic_core/L3_orchestration/engines/` | Directory contains only `__init__.py`. Zero unit tests for `orchestrator_engine.py` (32 KB), `dag_manager.py`, `recursive_orchestrator.py`, `deterministic_orchestrator.py`, `decomposition_orchestrator.py`, `rl_coordinator_orchestrator.py` (23 KB). |
| **G11** | `system_learning/adapters/l1_meta_adapter.py` ↔ `agentic_core/L1_cognition/engines/meta_client.py` | No test proves L1 `MetaClient` recall/learn outcomes pass through `L1MetaAdapter.extract_telemetry()` into `system_learning.stores.telemetry_store.TelemetryStore`. |
| **G12** | `agentic_core/L4_state/enforcement/metrics_emission.py` → `agentic_core/L6_observability/engines/TieredVigilanceEmitter.py` | No test proves a L4 state-mutation event produces a metric in L6's emitter. The emission chain is architecturally assumed but not contract-tested. |
| **G14** | `apps_shared/spine/base_spine_adapter.py` | Error recovery paths (failed assembly, risk-blocked re-entry, max-retries exceeded) have no dedicated tests. |
| **G15** | `system_learning/validators/` ↔ `system_learning/enforcement/authority_invariants.py` | No integration test that shows `OscillationPolicy` or `CooldownPolicy` actually blocks a `MetaLearningPipeline.run()` commit when the policy is violated. |
| **G16** | `agentic_core/L0_routing/seams/` (all 12 files) | No seam contract test file asserting each seam: (a) loads without error, (b) delegates to the correct downstream module, (c) returns correct type, (d) fails closed on missing downstream. |
| **G17** | `system_learning/engines/healing_outcome_intake_adapter.py` ↔ `agentic_core/L2_execution/healers/` | No test proves a healer execution result flows through `HealingOutcomeIntakeAdapter.ingest()` into `HealingOutcomeIntakeStore`. |
| **G18** | `agentic_core/L4_state/enforcement/phase_lock_store.py` + `activation_flags.py` | No test for post-restart persistence: write a phase lock, simulate restart by re-instantiating from serialized state, assert lock survives. |
| **G19** | `agentic_core/L5_safety/reasoning/` → `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` | No E2E test for the L5 safety-agent → L2 healer dispatch chain: agent detects violation → produces `SelfHealingTrigger` → tier router dispatches correct healer → healer returns outcome. |

### P4 — End-to-End Circuit Gaps

| ID | Description |
|----|-------------|
| **G8** | `system_learning/engines/l0_threshold_tuner.py`, `l1_model_proposer.py`, `l3_efficiency_tuner.py` — exist in isolation; no test drives a real system snapshot through the tuner and asserts it produces a bounded proposal that reaches the meta-learning pipeline's approval gate. |
| **G9** | `agentic_core/evaluation/retrieval/meta_learning_bridge.py::EvaluationSignals` → `system_learning/pipelines/meta_learning_pipeline.py::RagProposer` — the evaluation→system_learning circuit has no E2E test confirming `EvaluationSignals` flows into a `RetrievalProfileProposal` stored in L4. |

---

## Implementation Phases

### Phase 1 — Fix Broken Pipes (P0)

**Step 1.1 — Fix observability_seam.py dead import (G6)**

AST Analysis:
```python
# Current (BROKEN):
# agentic_core/L0_routing/seams/observability_seam.py:12
mod = importlib.import_module("agentic_core.L6_observability.meta_learning.MetaLearningAgent")
# → ModuleNotFoundError: No module named 'agentic_core.L6_observability.meta_learning'

# L6_observability/ structure:
# ├─ engines/
# ├─ reasoning/  ← MetaLearningAgent likely here
# └─ meta_learning/  ← DOES NOT EXIST
```

Implementation:
- **Option A (Recommended)**: Update seam to point to actual location:
  ```python
  # Fix: agentic_core/L0_routing/seams/observability_seam.py
  def load_meta_learning_agent():
      import importlib
      # Delegate to L1 MetaClient which is the actual meta-learning interface
      mod = importlib.import_module("agentic_core.L1_cognition.engines.meta_client")
      return mod.MetaLearningClient
  ```
- **Option B**: Create stub package delegating to L1:
  ```python
  # New: agentic_core/L6_observability/meta_learning/__init__.py
  from agentic_core.L1_cognition.engines.meta_client import MetaLearningClient as MetaLearningAgent
  __all__ = ["MetaLearningAgent"]
  ```

Tests Required:
```python
# tests/governance/test_l0_seam_contracts.py::test_observability_seam_loads
def test_observability_seam_loads():
    from agentic_core.L0_routing.seams.observability_seam import load_meta_learning_agent
    agent_cls = load_meta_learning_agent()
    assert agent_cls is not None
    assert callable(agent_cls)
```

**Step 1.2 — Fix apps_rg test collection errors (G13)**

AST Scan Strategy:
```python
import ast
import sys
from pathlib import Path

def scan_test_file(path: Path) -> dict:
    try:
        tree = ast.parse(path.read_text())
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        return {"status": "ok", "imports": len(imports)}
    except SyntaxError as e:
        return {"status": "syntax_error", "line": e.lineno, "msg": e.msg}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

# Scan all apps_rg test files
for test_file in Path("tests/unit/apps_rg").rglob("*.py"):
    result = scan_test_file(test_file)
    if result["status"] != "ok":
        print(f"FAIL: {test_file} - {result}")
```

Common Issues (from Phase 11 history):
- Duplicate `__init__.py` files with different content
- Missing `conftest.py` fixtures
- Import paths referencing moved/renamed modules
- Circular imports between test modules

Tests Required:
```bash
python -m pytest tests/unit/apps_rg/ --collect-only -q
# Must exit 0 with N collected items, 0 errors
```

---

### Phase 2 — Wire Critical Stubs (P1)

**Step 2.1 — Wire D0InjectionEngine into spine adapters (G1-a)**

AST Analysis:
```python
# Current NULL stub in apps_lic/engines/lic_spine_adapter.py:38-42
class _NullD0Engine:
    def render_d0(self, d0_injections: str) -> str:
        return d0_injections

# Real implementation: L5_safety/enforcement/d0_injection_engine_enforcer.py:19-68
class D0InjectionEngine:
    def render_d0(self, *, fences: tuple[RoleFence, ...]) -> str:
        # Signature MISMATCH: expects tuple[RoleFence, ...], not str
```

Adapter Signature Mismatch Resolution:
```python
# Create adapter wrapper in apps_shared/spine/d0_engine_adapter.py
from agentic_core.L5_safety.enforcement.d0_injection_engine_enforcer import (
    D0InjectionEngine, RoleFence
)

class D0EngineAdapter:
    """Adapter converting string d0_injections to RoleFence tuple."""
    def __init__(self):
        self._engine = D0InjectionEngine()

    def render_d0(self, d0_injections: str) -> str:
        # Parse d0_injections string into RoleFence tuple
        # Format: "fence_id_1:text1|fence_id_2:text2"
        if not d0_injections:
            return ""

        fences = []
        for segment in d0_injections.split("|"):
            if ":" in segment:
                fence_id, text = segment.split(":", 1)
                fences.append(RoleFence(fence_id=fence_id.strip(), text=text.strip()))

        return self._engine.render_d0(fences=tuple(fences))
```

Wiring in Spine Adapters:
```python
# Modify apps_lic/engines/lic_spine_adapter.py:119-136
from apps_shared.spine.d0_engine_adapter import D0EngineAdapter

class LicSpineAdapter(BaseSpineAdapter):
    def __init__(self, max_reentry_attempts: int = _DEFAULT_MAX_REENTRY_ATTEMPTS) -> None:
        cid_registry = CIDRegistry()
        reentry_loop = ReEntryLoop(max_attempts=max_reentry_attempts, cid_registry=cid_registry)

        # Wire real D0 engine via adapter
        try:
            d0_engine = D0EngineAdapter()
        except ImportError:
            d0_engine = _NullD0Engine()  # Fail-open fallback

        orchestrator = ExecutionOrchestrator(
            assembler=_LicAssemblerAdapter(),
            path_router=PathRouter(),
            d0_engine=d0_engine,  # ← Real engine wired
            # ... rest unchanged
        )
```

Tests Required:
```python
# tests/unit/apps/test_spine_d0_wiring.py
def test_d0_engine_wired_in_lic_spine():
    adapter = LicSpineAdapter()
    result = adapter.execute({"d0_injections": "safety:DENY_EXECUTION"})
    # Assert D0 engine was called (not null stub)
    assert "<D0>" in str(result)
    assert "[safety] DENY_EXECUTION" in str(result)

def test_d0_engine_import_failure_fallback():
    # Mock import failure
    with patch("apps_shared.spine.d0_engine_adapter.D0InjectionEngine", side_effect=ImportError):
        adapter = LicSpineAdapter()
        result = adapter.execute({"d0_injections": "test"})
        # Null stub returns input unchanged
        assert result is not None
```

**Step 2.2 — Wire ConfCalibRiskGate into spine adapters (G1-b)**

AST Analysis:
```python
# Current NULL stub: apps_lic/engines/lic_spine_adapter.py:50-54
class _NullRiskGate:
    def evaluate(self, *, payload_like: Any, d0_injections: Any) -> _RiskResult:
        return _RiskResult(allow=True)  # Always allows

# Real implementation: L5_safety/enforcement/conf_calib_gate.py:29-81
class ConfCalibRiskGate:
    def evaluate(self, *, payload_like: object, d0_injections: str) -> RiskDecision:
        # Returns RiskDecision(allow: bool, level: RiskLevel, reasons: tuple[str, ...])
```

Signature Compatibility:
```python
# _RiskResult vs RiskDecision - INCOMPATIBLE
# Need adapter to convert RiskDecision → _RiskResult

# Create: apps_shared/spine/risk_gate_adapter.py
from dataclasses import dataclass
from agentic_core.L5_safety.enforcement.conf_calib_gate import ConfCalibRiskGate

@dataclass(frozen=True)
class RiskResult:
    allow: bool

class RiskGateAdapter:
    def __init__(self):
        self._gate = ConfCalibRiskGate()

    def evaluate(self, *, payload_like, d0_injections) -> RiskResult:
        decision = self._gate.evaluate(payload_like=payload_like, d0_injections=d0_injections)
        return RiskResult(allow=decision.allow)
```

Wiring:
```python
# Modify apps_lic/engines/lic_spine_adapter.py
from apps_shared.spine.risk_gate_adapter import RiskGateAdapter, RiskResult

class LicSpineAdapter(BaseSpineAdapter):
    def __init__(self, max_reentry_attempts: int = _DEFAULT_MAX_REENTRY_ATTEMPTS) -> None:
        try:
            risk_gate = RiskGateAdapter()
        except ImportError:
            risk_gate = _NullRiskGate()  # Fail-open fallback

        orchestrator = ExecutionOrchestrator(
            # ...
            risk_gate=risk_gate,
            # ...
        )
```

Tests Required:
```python
# tests/unit/apps/test_spine_risk_gate_wiring.py
def test_risk_gate_blocks_high_risk():
    adapter = LicSpineAdapter()
    result = adapter.execute({
        "s0_system": "test",
        "d0_injections": "DENY_EXECUTION"  # Triggers HIGH risk
    })
    assert result["state"] in ["retry", "blocked"]
    assert result["risk"].allow is False

def test_risk_gate_allows_low_risk():
    adapter = LicSpineAdapter()
    result = adapter.execute({"s0_system": "test", "d0_injections": ""})
    assert result["state"] == "success"
    assert result["risk"].allow is True

def test_reentry_loop_on_block():
    adapter = LicSpineAdapter(max_reentry_attempts=3)
    result = adapter.execute({"d0_injections": "DENY_EXECUTION"})
    # First attempt blocked, should retry
    assert result["cycle"].attempt <= 3
```

**Step 2.3 — Wire VigilanceDispatcher into spine adapters (G1-c)**
- Target: `agentic_core/L6_observability/engines/vigilance_dispatcher.py`
- Wire via `agentic_core.interfaces.observability` seam; dispatcher must be non-blocking (fire-and-forget)
- Tests required: dispatcher receives `VigilanceEventArtifact`; dispatcher failure does NOT block execution; events contain correct trace_id from `CIDRegistry`

**Step 2.4 — Wire MetaLearningBus consumer (G1-d + G7)**
- Bind `meta_apply.MetaApply.apply()` as the `apply_fn` in `ExecutionOrchestrator` post-execution
- `MetaLearningBus.enqueue()` should be called with execution outcome intent (using `LearningArtifactIntent.create()` from `learning_seam.py`)
- Tests required: bus receives package after successful execution; `intent.verify()` passes; `meta_apply` is invoked; queue is empty after drain; bus failure does NOT fail execution

**Step 2.5 — Connect ExecutionOrchestrator → L3 for Paths B/C/D (G5)**

AST Analysis:
```python
# Current: L0_routing/engines/execution_orchestrator.py:53-98
def execute(self, intent_input: dict[str, Any]) -> dict[str, Any]:
    payload = self.assembler.assemble(intent_input)
    path = self.path_router.select_path(payload)  # Returns Path.A/B/C/D
    # ...
    # Line 97: return {"path": path, "risk": risk, "cycle": cycle, "state": "success"}
    # ← NO L3 CALL for Path B/C/D

# Protocol: seams/orchestration_protocols.py:46-75
class IOrchestrator(Protocol):
    def orchestrate(
        self, governed_payload: GovernedPayload, route_mode: str,
        trace_id: str, policy_hash: str, allowed_tools: tuple[str, ...]
    ) -> OrchestrationResult
```

Implementation:
```python
# Modify L0_routing/engines/execution_orchestrator.py
from agentic_core.seams.orchestration_protocols import IOrchestrator, OrchestrationResult

class ExecutionOrchestrator:
    def __init__(
        self, assembler, path_router, d0_engine, risk_gate,
        cid_registry, reentry_loop, vigilance_dispatcher, meta_bus,
        l3_orchestrator: IOrchestrator | None = None  # ← NEW
    ):
        # ... existing fields ...
        self.l3_orchestrator = l3_orchestrator

    def execute(self, intent_input: dict[str, Any]) -> dict[str, Any]:
        payload = self.assembler.assemble(intent_input)
        path = self.path_router.select_path(payload)
        d0_injections = self.d0_engine.render_d0(payload.d0_injections)
        risk = self.risk_gate.evaluate(payload_like=payload, d0_injections=d0_injections)
        cycle = self.cid_registry.new_cycle(f"execute_{path.value}")

        if not risk.allow:
            # ... existing re-entry logic ...

        # NEW: Delegate Path B/C/D to L3
        orchestration_result = None
        if path.value in ("B", "C", "D") and self.l3_orchestrator is not None:
            try:
                orchestration_result = self.l3_orchestrator.orchestrate(
                    governed_payload=payload,
                    route_mode=path.value,
                    trace_id=cycle.cid,
                    policy_hash=payload.manifest_hash,
                    allowed_tools=()  # TODO: derive from payload
                )
            except Exception as e:
                # L3 failure does not block execution
                orchestration_result = OrchestrationResult(
                    success=False, route_mode=path.value,
                    plan_hash="", metadata={"error": str(e)}
                )

        return {
            "path": path, "risk": risk, "cycle": cycle, "state": "success",
            "orchestration": orchestration_result.to_dict() if orchestration_result else None
        }
```

Wiring in Spine Adapters:
```python
# Modify apps_lic/engines/lic_spine_adapter.py
from agentic_core.L3_orchestration.engines.orchestrator_engine import get_consolidated_orchestrator

class LicSpineAdapter(BaseSpineAdapter):
    def __init__(self, max_reentry_attempts: int = _DEFAULT_MAX_REENTRY_ATTEMPTS) -> None:
        # ...
        try:
            l3_orchestrator = get_consolidated_orchestrator()
        except ImportError:
            l3_orchestrator = None  # Path A still works

        orchestrator = ExecutionOrchestrator(
            # ... existing args ...
            l3_orchestrator=l3_orchestrator  # ← NEW
        )
```

Tests Required:
```python
# tests/unit/L0_routing/test_execution_orchestrator_l3_wiring.py
def test_path_a_bypasses_l3():
    orch = ExecutionOrchestrator(..., l3_orchestrator=Mock())
    result = orch.execute({"check_ids": ()})  # → Path.A
    assert result["path"].value == "A"
    assert result["orchestration"] is None  # L3 not called

def test_path_b_calls_l3():
    mock_l3 = Mock(spec=IOrchestrator)
    mock_l3.orchestrate.return_value = OrchestrationResult(
        success=True, route_mode="B", plan_hash="abc123"
    )
    orch = ExecutionOrchestrator(..., l3_orchestrator=mock_l3)
    result = orch.execute({"sanitized": True})  # → Path.B
    assert result["path"].value == "B"
    assert result["orchestration"]["plan_hash"] == "abc123"
    mock_l3.orchestrate.assert_called_once()

def test_l3_failure_does_not_block():
    mock_l3 = Mock(spec=IOrchestrator)
    mock_l3.orchestrate.side_effect = RuntimeError("L3 failed")
    orch = ExecutionOrchestrator(..., l3_orchestrator=mock_l3)
    result = orch.execute({"check_ids": ("c1",)})  # → Path.C
    assert result["state"] == "success"  # Execution not blocked
    assert "error" in result["orchestration"]["metadata"]
```

---

### Phase 3 — Resolve Placeholders (P2)

**Step 3.1 — Implement elevator_shaft_seam JIT context loading (G3)**

AST Analysis:
```python
# Current stub: L0_routing/seams/elevator_shaft_seam.py
def load_context_jit() -> dict:
    return {}  # Pure stub

# Target: L4_state/memory/blackboard_store.py or semantic_cache_manager.py
```

Implementation:
```python
# Modify L0_routing/seams/elevator_shaft_seam.py
def load_context_jit() -> dict:
    """Load JIT context from L4 blackboard (read-only)."""
    try:
        from agentic_core.L4_state.memory.blackboard_store import BlackboardStore
        store = BlackboardStore()
        context = store.read_all(max_items=20)  # Bounded read
        return context if context else {}
    except (ImportError, Exception):
        return {}  # Fail-open: empty context on error
```

Tests:
```python
# tests/governance/test_elevator_shaft_seam.py
def test_elevator_shaft_loads_from_blackboard():
    # Populate blackboard
    from agentic_core.L4_state.memory.blackboard_store import BlackboardStore
    store = BlackboardStore()
    store.write("key1", "value1")

    from agentic_core.L0_routing.seams.elevator_shaft_seam import load_context_jit
    context = load_context_jit()
    assert "key1" in context
    assert context["key1"] == "value1"

def test_elevator_shaft_bounded_read():
    context = load_context_jit()
    assert len(context) <= 20  # Max items enforced
```

**Step 3.2 — Implement C0ContextRetriever seed pack loading (G4)**

AST Analysis:
```python
# Current placeholder: L0_routing/seams/c0_context_retriever.py:27-29
@classmethod
async def load(cls) -> C0ContextArtifact | None:
    return None  # Placeholder

# Target: system_learning/engines/local_faiss_store.py or embedding service
```

Implementation:
```python
# Modify L0_routing/seams/c0_context_retriever.py
@classmethod
async def load(cls) -> C0ContextArtifact | None:
    """Load C0 seed pack from FAISS store."""
    try:
        from system_learning.engines.local_faiss_store import LocalFAISSStore
        store = LocalFAISSStore()

        # Load seed pack artifact
        seed_pack = store.load_seed_pack("c0_context_v1")
        if not seed_pack:
            raise RuntimeError("C0 seed pack not found in store")

        # Load supporting content hashes with scores
        results = store.query(seed_pack["query_embedding"], top_k=20)
        content_hashes = [
            ContentHash(content_hash=r["hash"], score=r["score"])
            for r in results if r["score"] >= 0.5
        ]

        return cls(
            seed_pack=seed_pack["text"],
            seed_pack_hash=seed_pack["hash"],
            supporting_content_hashes=content_hashes
        )
    except Exception as e:
        raise RuntimeError(f"C0 seed pack loading failed: {e}")
```

Tests:
```python
# tests/governance/test_c0_context_retriever.py
async def test_c0_loads_from_faiss():
    # Populate FAISS with seed pack
    from system_learning.engines.local_faiss_store import LocalFAISSStore
    store = LocalFAISSStore()
    store.save_seed_pack("c0_context_v1", {"text": "...", "hash": "..."})

    artifact = await C0ContextArtifact.load()
    assert artifact is not None
    assert len(artifact.supporting_content_hashes) <= 20
    assert all(h.score >= 0.5 for h in artifact.supporting_content_hashes)

async def test_c0_hash_mismatch_fails():
    # Corrupt seed pack hash
    with pytest.raises(RuntimeError, match="hash mismatch"):
        retriever = C0ContextRetriever()
        await retriever.retrieve("test query")
```

**Step 3.3 — Wire shadow routing → L4 and L6 (G2)**
- In `shadow_routing_wiring.py::observe_and_classify()`: replace log-only with real L6 emission via `agentic_core.interfaces.observability` seam and real L4 write via `L4StateWriter`
- Shadow path must remain non-invasive: routing result unchanged; failures silently swallowed
- Tests required: telemetry appears in L6 emitter mock; L4 write called with bounded `ShadowRoutingTelemetry`; L6/L4 failure leaves route_decision unchanged

---

### Phase 4 — Integration Tests for Existing Logic (P3)

**Test Template Pattern:**
```python
# All integration tests follow this structure:
import pytest
from pathlib import Path

class TestIntegrationName:
    @pytest.fixture
    def setup_real_components(self):
        """Setup real components, no mocks for connection under test."""
        # Initialize real objects
        yield components
        # Cleanup

    def test_success_path(self, setup_real_components):
        """Test successful data flow through connection."""
        # Arrange: prepare input
        # Act: invoke connection
        # Assert: verify output at destination
        pass

    def test_failure_path(self, setup_real_components):
        """Test connection handles failures gracefully."""
        # Inject failure, assert fail-closed behavior
        pass

    def test_determinism(self, setup_real_components):
        """Test identical input produces identical output."""
        # Run twice, assert results match
        pass
```

**Priority Test Files (create in order):**

1. **`tests/governance/test_l0_seam_contracts.py` (G16)** — Foundation for all seam wiring
```python
import pytest
import importlib
from pathlib import Path

SEAM_FILES = [
    "learning_seam", "safety_enforcement_seam", "c0_context_retriever",
    "elevator_shaft_seam", "observability_seam", "vigilance_seam",
    "layer_emission_seam", "redis_decision_cache",
    # ... all 12 seams
]

@pytest.mark.parametrize("seam_name", SEAM_FILES)
def test_seam_loads_without_error(seam_name):
    mod = importlib.import_module(f"agentic_core.L0_routing.seams.{seam_name}")
    assert mod is not None

@pytest.mark.parametrize("seam_name", SEAM_FILES)
def test_seam_exports_expected_interface(seam_name):
    # Each seam must export specific functions/classes
    # Assert __all__ contains expected names
    pass
```

2. **`tests/governance/test_healer_outcome_intake_wiring.py` (G17)** — Critical for system_learning feedback
```python
def test_healer_outcome_flows_to_intake_store():
    from agentic_core.L2_execution.healers.healing_tier_dispatcher import dispatch_healing
    from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
    from system_learning.ports.healing_outcome_intake_store import InMemoryHealingOutcomeIntakeStore

    store = InMemoryHealingOutcomeIntakeStore()
    adapter = HealingOutcomeIntakeAdapter(store)

    # Dispatch healing
    outcome = dispatch_healing(healing_input, config, invoker)

    # Build and persist record
    aggregator = HealingOutcomeAggregator()
    aggregator.add(outcome)
    record = adapter.build_record(aggregator, created_utc=1234567890)
    adapter.persist_record(record)

    # Assert store contains entry
    assert len(store.read_all()) == 1
    assert store.read_all()[0].snapshot[0].healer_id == outcome.healer_id
```

3. **`tests/system_learning/test_l1_meta_adapter_wiring.py` (G11)** — L1→system_learning bridge
```python
def test_l1_meta_client_telemetry_extraction():
    from agentic_core.L1_cognition.engines.meta_client import MetaLearningClient
    from system_learning.adapters.l1_meta_adapter import L1MetaAdapter
    from system_learning.stores.telemetry_store import InMemoryTelemetryStore

    client = MetaLearningClient()
    adapter = L1MetaAdapter()
    store = InMemoryTelemetryStore()

    # Client learns pattern
    client.learn(pattern_key="test_pattern", outcome={"success": True})

    # Extract telemetry
    telemetry = adapter.extract_telemetry(client.get_state())
    store.record(telemetry)

    # Assert telemetry in store
    assert len(store.read_all()) == 1
```

**Remaining Tests (G10, G12, G14, G15, G18, G19, G20):**
- Follow same pattern: real components, no mocks for connection under test
- Each test file: 3-5 test functions covering success/failure/determinism
- All tests must pass `pytest -xvv` with zero skips

---

### Phase 5 — End-to-End Circuit Completion (P4)

**Step 5.1 — system_learning tuner E2E (G8)**

Implementation:
```python
# tests/system_learning/test_tuner_to_proposal_e2e.py
def test_l0_threshold_tuner_produces_proposal():
    from system_learning.snapshots.snapshot_factory import create_snapshot
    from system_learning.engines.l0_threshold_tuner import L0ThresholdTuner
    from system_learning.engines.retrieval_profile_proposal_manager import RetrievalProfileProposalManager
    from system_learning.stores.l4_state_writer import InMemoryL4StateWriter

    # Create snapshot with high escalation rate
    snapshot = create_snapshot(
        snapshot_id="test_001",
        routing_metrics={"escalation_rate": 0.25},  # Exceeds 0.20 trigger
        created_utc=1234567890
    )

    # Run tuner
    tuner = L0ThresholdTuner()
    change_package = tuner.propose_adjustment(
        snapshot=snapshot,
        current_threshold=0.70,
        surface_name="escalation_threshold"
    )

    # Convert to proposal
    proposal_mgr = RetrievalProfileProposalManager()
    proposal = proposal_mgr.create_proposal_from_change_package(change_package)

    # Write to L4
    writer = InMemoryL4StateWriter()
    writer.write_proposal(proposal)

    # Assert proposal in store
    proposals = writer.read_all_proposals()
    assert len(proposals) == 1
    assert proposals[0].surface_name == "escalation_threshold"
    assert 0.50 <= proposals[0].new_value <= 0.95  # Bounded
    assert abs(proposals[0].new_value - 0.70) <= 0.05  # Max delta enforced

def test_l1_model_proposer_e2e():
    # Similar pattern for L1ModelChangePackage → proposal
    pass

def test_proposal_requires_approval_gate():
    # Assert proposal.approved == False by default
    # Assert proposal cannot activate without explicit approval
    pass
```

**Step 5.2 — evaluation → system_learning feedback circuit (G9)**

Implementation:
```python
# tests/evaluation/test_evaluation_to_system_learning_e2e.py
def test_evaluation_signals_produce_retrieval_proposal():
    from agentic_core.evaluation.retrieval.meta_learning_bridge import EvaluationSignals
    from system_learning.pipelines.meta_learning_pipeline import MetaLearningPipeline
    from system_learning.stores.l4_state_writer import InMemoryL4StateWriter

    # Create evaluation signals with low completeness
    signals = EvaluationSignals(
        snapshot_id="eval_001",
        retrieval_relevance_mean=0.85,
        retrieval_precision=0.80,
        retrieval_recall=0.75,
        mean_completeness_score=0.60,  # Low completeness
        missing_condition_rate=0.15,
        missing_exception_rate=0.10,
        missing_scope_rate=0.05,
        missing_temporal_qualifier_rate=0.08,
        answer_correctness_rate=0.90,
        fully_supported_rate=0.85,
        mean_support_score=0.88,
        high_similarity_wrong_answer_rate=0.05,
        parent_reconstruction_applied_rate=0.12,
        chunk_fragmentation_error_rate=0.03,
        observation_count=100
    )

    # Run through pipeline
    pipeline = MetaLearningPipeline()
    writer = InMemoryL4StateWriter()

    proposal = pipeline.process_evaluation_signals(
        signals=signals,
        state_writer=writer,
        proposal_only=True  # Default: proposal-only mode
    )

    # Assert proposal created
    assert proposal is not None
    assert proposal.justification.startswith("Low completeness detected")

    # Assert proposal in L4
    proposals = writer.read_all_proposals()
    assert len(proposals) == 1
    assert proposals[0].content_hash() == proposal.content_hash()

    # Assert approval required
    assert proposal.approved is False
```

---

## Test Requirements Matrix

Every new test MUST satisfy:
- **Branch coverage**: success, failure, null-input, boundary, exception paths
- **Negative control**: all fail-closed guards tested with invalid input
- **Determinism**: identical input → identical output (no wall-clock, no uuid4)
- **No silent masking**: exception paths assert semantically correct error type/message
- **Branch inventory section** in evidence file per `§1.3`

---

## Acceptance Criteria

### Hard Gates (must pass):
1. **Full test suite**: `python -m pytest -q --color=no` exits 0
2. **Zero collection errors**: `python -m pytest --collect-only -q` shows 0 errors
3. **All P0 gaps closed**: G6 (observability_seam) and G13 (apps_rg tests) resolved
4. **All P1 stubs wired**: G1 (4 stubs), G5 (L3 wiring), G7 (MetaBus consumer) functional
5. **Seam contract coverage**: `tests/governance/test_l0_seam_contracts.py` covers all 12 seams
6. **L3 test coverage**: `tests/unit/agentic_core/L3_orchestration/engines/` contains ≥ 3 test files

### Soft Gates (document waivers if not met):
7. **P2 placeholders**: G2, G3, G4, G20 resolved or waived with justification
8. **P3 test gaps**: G10-G19 have integration tests or documented coverage plan
9. **P4 E2E circuits**: G8, G9 have end-to-end tests or staged implementation plan

### Quality Gates:
10. **Branch coverage**: All new code has success/failure/edge-case tests per §1.2
11. **Determinism**: All tests pass `pytest -xvv --count=3` (run 3 times, identical results)
12. **No silent masking**: All exception paths assert semantic error types per §1.5
13. **Evidence bundling**: Implementation commits include evidence file per /phase-execute workflow

---

## Implementation Summary

### Files to Create (17 new files)

**Adapters (3 files):**
```
apps_shared/spine/d0_engine_adapter.py                               (G1-a adapter)
apps_shared/spine/risk_gate_adapter.py                               (G1-b adapter)
apps_shared/spine/vigilance_dispatcher_adapter.py                    (G1-c adapter)
```

**Tests (14 files):**
```
tests/governance/test_l0_seam_contracts.py                           (G16 — 12 seams)
tests/governance/test_l4_to_l6_emission_chain.py                     (G12)
tests/governance/test_healer_outcome_intake_wiring.py                (G17)
tests/governance/test_phase_lock_persistence.py                      (G18)
tests/governance/test_l5_to_l2_healer_dispatch_e2e.py               (G19)
tests/governance/test_elevator_shaft_seam.py                         (G3)
tests/governance/test_c0_context_retriever.py                        (G4)
tests/system_learning/test_l1_meta_adapter_wiring.py                 (G11)
tests/system_learning/test_validator_enforcement_integration.py      (G15)
tests/system_learning/test_tuner_to_proposal_e2e.py                  (G8)
tests/evaluation/test_evaluation_to_system_learning_e2e.py           (G9)
tests/unit/agentic_core/L3_orchestration/engines/test_orchestrator_engine.py  (G10)
tests/unit/agentic_core/L3_orchestration/engines/test_dag_manager.py          (G10)
tests/unit/agentic_core/L3_orchestration/test_arbitration_integration.py      (G20)
tests/unit/apps/test_spine_d0_wiring.py                              (G1-a)
tests/unit/apps/test_spine_risk_gate_wiring.py                       (G1-b)
tests/unit/apps/test_base_spine_adapter_error_paths.py               (G14)
tests/unit/L0_routing/test_execution_orchestrator_l3_wiring.py       (G5)
```

### Files to Modify (9 files)

**Seams (4 files):**
```
agentic_core/L0_routing/seams/observability_seam.py                  (G6 — fix import path)
agentic_core/L0_routing/seams/elevator_shaft_seam.py                 (G3 — wire L4 blackboard)
agentic_core/L0_routing/seams/c0_context_retriever.py                (G4 — wire FAISS store)
agentic_core/L0_routing/engines/shadow_routing_wiring.py             (G2 — wire L4/L6)
```

**Core (1 file):**
```
agentic_core/L0_routing/engines/execution_orchestrator.py            (G5 — add l3_orchestrator param)
```

**Spine Adapters (2 files):**
```
apps_lic/engines/lic_spine_adapter.py                                (G1 — wire 4 real components)
apps_rg/engines/rg_spine_adapter.py                                  (G1 — wire 4 real components)
```

**Test Fixes (2 files):**
```
tests/unit/apps_rg/*.py                                              (G13 — fix collection errors)
tests/unit/apps_rg/conftest.py                                       (G13 — fix fixtures)
```

### Effort Estimate

- **Phase 1 (P0)**: 2- (fix broken imports + test collection)
- **Phase 2 (P1)**: 8- (wire 4 stubs + L3 orchestrator + tests)
- **Phase 3 (P2)**: 4- (implement 2 placeholders + tests)
- **Phase 4 (P3)**: 12- (11 integration test files)
- **Phase 5 (P4)**: 4- (2 E2E circuit tests)

**Total**: 30- of implementation + testing

---

## Risk Notes

- **G5 (L3 wiring)** is the highest-risk implementation item — `orchestrator_engine.py` is 32 KB with extensive state; wire via protocol injection to avoid touching it directly
- **G4 (C0ContextRetriever)** requires FAISS to be available; tests must use `system_learning/engines/faiss_startup_integrity.py` to detect absence and skip gracefully
- **G1-d (MetaBus)** must never block execution on failure — wrap `apply_fn` in try/except and log only
- All seam fixes must preserve the lazy-import pattern used by existing seams to avoid circular imports

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

