---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\execute_ssot_simplification_plan-460a9b.md'
original_relative_path: 'execute_ssot_simplification_plan-460a9b.md'
source_sha256: 694b76cab896d36bad8aad2c8e3d89c4ff7be3aca37066a7bfb338c484d4514d
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-01'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# execute_ssot Orchestration Simplification Plan

Introduce a uniform `L2AgentProtocol` so every agent exposes the same four-method taxonomy (`pre_commit`, `validate`, `execute`, `heal`) and the orchestrator can drive all 10 agents through an identical loop instead of 5 hand-written phase functions with bespoke per-agent call sites.

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


## 1. Problem Statement

`execute_ssot.py` drives 10 agents across five phase functions
(`execute_phase1_discovery_impl`, `execute_phase2_alignment_impl`,
`execute_phase3_validation_impl`, `execute_phase4_healing_impl`,
`execute_phase5_final_impl`). Each phase function was authored independently and
calls agents through completely different surface APIs:

| Agent key | Phase | Actual call site |
|---|---|---|
| `reconciler` (FilesystemSSOTReconcilerAgent) | 1 | `detect_root_drift()` / `heal_repository()` |
| `location` (LocationAgent → LocationHealerAgent) | 1 | `run(target_territory=…)` / `heal_violations(…)` |
| `file_classification` (FileClassificationAgent) | 1 + 2.5 | `run()` / `heal_repository()` |
| `hierarchy` (HierarchyAgent) | 2 | `scan_root_violations()` / `heal_hierarchy(…, dry_run=…)` |
| `arch_governor` (ArchitectureGovernorAgent) | 3 + 4 | `comprehensive_territory_audit()` → `generate_healing_plan()` → `heal_repository()` |
| `gravity_repair` (GravityLeakRepairAgent) | 3.5 | `heal_repository(dry_run=…, execute=…)` |
| `system_architect` (SystemArchitectAgent) | 3 | `validate_core_architecture(path)` |
| `conversational_repair` (ObservabilityProbeExecutor) | 5 | `scan_violations(target_territory=…)` |
| `root_hygiene` (RootHygieneAgent) | 5 | violations pulled from `state["hygiene_violations"]` (never called directly) |
| `cognitive_disposition` (CognitiveDispositionAgent) | 1 | `analyze_violations(…)` (async, optional) |

Consequences of this heterogeneity:
- **Five large bespoke phase functions** (≈ 600 LOC combined) each re-implement
  confidence gating, `update_agent` / `complete_agent` / `skip_agent` calls, and
  error handling — duplicated 5 times with slight differences.
- **Phase numbering is non-contiguous** (1, 2, 2.5, 3, 3.5, 4, 4.5, 5) because
  agents were bolted on after the fact.
- **`root_hygiene` is never invoked** — violations are read from state that nobody
  populates, so the agent is dead weight.
- **`gravity_repair`** is embedded in the middle of phase 3 with its own
  try/except block — it doesn't participate in the confidence gate.
- **`ObservabilityProbeExecutor`** is registered as `conversational_repair` and
  called as `scan_violations`, a name inherited from a deleted `DebateSynthesisAgent`.
- `state_mgr.update_agent` / `complete_agent` pairs are inconsistently placed: some
  agents call `update_agent` before confidence is checked, causing phantom-run
  artefacts if the gate fires.

---

## 2. Proposed Taxonomy: `L2AgentProtocol`

Define a four-method protocol that maps directly to the four L2 subphases:

```python
class L2AgentProtocol(Protocol):
    # Subphase 1 — Pre-commit gates (read-only, fast, no mutations)
    def pre_commit(self, territory: str, ctx: HealContext) -> SubphaseResult: ...

    # Subphase 2 — Deep validation (read-only, may be slow)
    def validate(self, territory: str, ctx: HealContext) -> SubphaseResult: ...

    # Subphase 3 — Execute mutations (writes, confidence-gated)
    def execute(self, territory: str, ctx: HealContext) -> SubphaseResult: ...

    # Subphase 4 — Heal residual failures (writes, confidence-gated)
    def heal(self, territory: str, ctx: HealContext) -> SubphaseResult: ...
```

`SubphaseResult` is a lightweight dataclass:

```python
@dataclass
class SubphaseResult:
    violations: list[dict]        # always present; empty = clean
    fixed: list[dict]             # mutations applied
    skipped: bool = False         # confidence gate fired
    skip_reason: str = ""
    error: str | None = None      # exception message if subphase crashed
```

---

## 3. Per-Agent Mapping

Each agent needs a thin **adapter wrapper** (not a rewrite of the agent itself)
that maps its existing bespoke methods onto the four-method surface:

### 3.1 FilesystemSSOTReconcilerAgent

| L2 subphase | Maps to |
|---|---|
| `pre_commit` | `detect_root_drift()` — read-only drift check |
| `validate` | `run_ci_verification_sync()` — deep verification |
| `execute` | `heal_repository(dry_run=not ctx.heal)` |
| `heal` | same as `execute` with `execute=True` |

### 3.2 LocationAgent / LocationHealerAgent

| L2 subphase | Maps to |
|---|---|
| `pre_commit` | `run(target_territory=territory)` scan |
| `validate` | re-use scan result; validate violations list |
| `execute` | `heal_violations(violations, auto_approve=ctx.auto_approve)` |
| `heal` | same as `execute` |

### 3.3 FileClassificationAgent

| L2 subphase | Maps to |
|---|---|
| `pre_commit` | `run()` with `validate_only=True, dry_run=True` |
| `validate` | `run()` with `validate_only=True` |
| `execute` | `heal_repository(dry_run=not ctx.heal)` |
| `heal` | `heal_repository(dry_run=False, execute=True)` |

### 3.4 HierarchyAgent

| L2 subphase | Maps to |
|---|---|
| `pre_commit` | `scan_root_violations(target_territory=territory)` |
| `validate` | re-use scan; count violations |
| `execute` | `heal_hierarchy(dry_run=not ctx.heal, target_territory=territory)` |
| `heal` | same as `execute` |

### 3.5 ArchitectureGovernorAgent

| L2 subphase | Maps to |
|---|---|
| `pre_commit` | `run_audit(target_territories=[territory])` |
| `validate` | `comprehensive_territory_audit([territory], ...)` |
| `execute` | `generate_healing_plan(report)` + `heal_repository(dry_run=not ctx.heal)` |
| `heal` | `heal_repository(dry_run=False, execute=True)` |

### 3.6 GravityLeakRepairAgent

| L2 subphase | Maps to |
|---|---|
| `pre_commit` | `heal_repository(dry_run=True)` — report only |
| `validate` | same; extract `violations_found` |
| `execute` | `heal_repository(dry_run=not ctx.heal)` |
| `heal` | `heal_repository(dry_run=False, execute=True)` |

### 3.7 SystemArchitectAgent

| L2 subphase | Maps to |
|---|---|
| `pre_commit` | `validate_core_architecture(f"agentic_core/{territory}")` |
| `validate` | same; check `imports_valid` |
| `execute` | no-op (agent explicitly returns `manual_required`) |
| `heal` | no-op |

### 3.8 ObservabilityProbeExecutor (currently `conversational_repair`)

| L2 subphase | Maps to |
|---|---|
| `pre_commit` | `scan_violations(target_territory=territory)` |
| `validate` | re-use result |
| `execute` | no-op (observability is read-only) |
| `heal` | no-op |

### 3.9 RootHygieneAgent

| L2 subphase | Maps to |
|---|---|
| `pre_commit` | `scan_root_violations()` |
| `validate` | `run()` |
| `execute` | `heal_repository(dry_run=not ctx.heal)` |
| `heal` | `heal_repository(dry_run=False, execute=True)` |

### 3.10 CognitiveDispositionAgent

Remains optional — not part of the uniform loop. It acts as an **advisor** that
augments the confidence score; it does not produce `SubphaseResult` violations.
Keep it as a pre-loop hook that the `SovereignDecisionEngine` queries.

---

## 4. Unified Orchestration Loop

Replace the five bespoke phase functions with a single generic loop:

```python
AGENT_PIPELINE: list[str] = [
    "reconciler",
    "location",
    "file_classification",
    "hierarchy",
    "arch_governor",
    "gravity_repair",
    "system_architect",
    "conversational_repair",
    "root_hygiene",
]

def run_pipeline(
    adapters: dict[str, L2AgentProtocol],
    territory: str,
    decision_engine: SovereignDecisionEngine,
    state_mgr: RuntimeStateManager,
    ctx: HealContext,
) -> dict[str, SubphaseResult]:
    results: dict[str, SubphaseResult] = {}

    for key in AGENT_PIPELINE:
        if key not in adapters:
            continue
        adapter = adapters[key]
        agent_name = type(adapter).__name__

        for subphase_name in ("pre_commit", "validate", "execute", "heal"):
            method = getattr(adapter, subphase_name)

            # Skip mutating subphases when not healing
            if subphase_name in ("execute", "heal") and not ctx.heal:
                continue

            state_mgr.update_agent(agent_name, f"{subphase_name}")
            try:
                result: SubphaseResult = method(territory, ctx)
            except Exception as exc:
                result = SubphaseResult(violations=[], fixed=[], error=str(exc))

            if not result.skipped and result.violations and subphase_name == "validate":
                confidence = decision_engine.calculate_healing_confidence(
                    len(result.violations),
                    [v.get("type", "UNKNOWN") for v in result.violations[:10]],
                    territory,
                )
                proceed, reason = decision_engine.should_proceed_with_healing(
                    confidence, agent_name
                )
                if not proceed:
                    result.skipped = True
                    result.skip_reason = reason
                    state_mgr.skip_agent(agent_name, reason)
                    break  # skip execute + heal for this agent

            state_mgr.complete_agent(agent_name, result.error is None, result.error or "")
        results[key] = result

    return results
```

Key improvements over the current approach:
- **Confidence gating is applied once per agent** after `validate`, not scattered
  across 5 functions.
- **`update_agent` / `complete_agent` / `skip_agent`** always form a consistent
  trio — no phantom-run risk.
- The pipeline order is declared in one constant (`AGENT_PIPELINE`) instead of
  being implied by function call order across 600 LOC.
- Phase numbers disappear — they were an artefact of sequential accumulation, not
  an intentional design.

---

## 5. Concrete Refactoring Steps

### Step A — Define `SubphaseResult` and `L2AgentProtocol` (new file)

`agentic_core/L2_execution/protocol.py`

- `SubphaseResult` dataclass (violations, fixed, skipped, skip_reason, error).
- `L2AgentProtocol` Protocol class with four methods.
- No agent imports; zero side effects.

### Step B — Write adapters (new file per agent, or one file per domain)

`agentic_core/L0_routing/scripts/ssot_adapters.py`

One adapter class per agent, implementing `L2AgentProtocol`. Each adapter wraps
the existing agent class. No changes to agent internals.

### Step C — Add `run_pipeline` (new function in `execute_ssot.py`)

Replace the body of `_legacy_main` phase dispatch with a single `run_pipeline`
call. The existing five `execute_phase*` functions can be kept as dead code
initially, then deleted once the new loop passes all integration tests.

### Step D — Rename `conversational_repair` key to `observability_probe`

Update `CANONICAL_ROSTER_KEYS`, `AGENT_DEPENDENCIES`, `EXECUTION_PLAN`, and
`agents` dict to use the semantically correct key. Add a deprecated alias for
the old key with a `DeprecationWarning`.

### Step E — Fix `root_hygiene` dead-code path

`run_pipeline` will call `root_hygiene.pre_commit()` directly, which invokes
`scan_root_violations()`. This replaces the current pattern where violations
were expected in `state["hygiene_violations"]` but never written there.

---

## 6. What NOT to Change

- Agent internal implementations — no rewrites; only thin adapter wrappers.
- `EXECUTION_PLAN` structure (used by `--plan` introspection and AST contract
  tests) — update phase names to match the four subphases, but keep the dict
  shape.
- `SovereignDecisionEngine`, `RuntimeStateManager`, `HealContext` — no changes.
- Test suite — all existing `unit_min_deps` tests remain valid.

---

## 7. Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Adapter wraps method with wrong signature | Medium | Unit test each adapter's four methods with mocks before wiring into pipeline |
| Phase ordering changes break an implicit dependency | Low | `AGENT_DEPENDENCIES` graph already encodes ordering; new pipeline respects it |
| `arch_governor` uses return value of `generate_healing_plan` as input to `heal_repository` — two-step sequence | Medium | Adapter stores plan result in instance state between `execute` and `heal` subphase calls |
| Existing integration tests hard-coded to phase function names | Low | Phase functions are internal; no public test asserts on them by name |

---

## 8. Acceptance Criteria

1. `python -m pytest -q --color=no` exits 0 with the same collection count.
2. `python execute_ssot.py --plan` output reflects updated phase/agent structure.
3. All 10 agents appear in pipeline order in a single `AGENT_PIPELINE` constant.
4. No agent has more than one `update_agent` call without a matching
   `complete_agent` or `skip_agent` in the same code path.
5. The five `execute_phase*_impl` functions are deleted or clearly marked
   `# DEPRECATED: replaced by run_pipeline`.

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

