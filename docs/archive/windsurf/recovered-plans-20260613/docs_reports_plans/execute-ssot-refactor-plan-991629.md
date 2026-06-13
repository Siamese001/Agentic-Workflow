# Refactor: Replace Legacy execute_ssot Pipeline with Guardian-Driven Remediation

Retire `execute_ssot_entrypoint.py` and decompose the 3,126-line `execute_ssot.py` monolith into layer-aligned modules that consume Guardian output, matching the A++ Enforceable L2 Control Spec (Guardian → L3 HIL → L2 Validator-Healer).

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Context

**Current state**: `execute_ssot.py` is a pre-Guardian monolith containing a 5-phase pipeline (Discovery → Reconciliation → Alignment → Validation → Healing → Certification) with its own confidence-based decision engine, agent discovery, state management, and reporting. `execute_ssot_entrypoint.py` is a 115-line shell that gates access to it behind `--legacy`.

**Future state** (per diagram): Guardian scripts (L5, deterministic pass/fail) → L3 HIL (human approval queue) → L2 Symmetric Validator-Healer Pipe → RESULT artifact → L6 observability.

**Guardian infrastructure already exists**:
- `guardian_contract.py` — schema-locked `GuardianResult` with `checks`, `evidence`, `remediation_hints`
- `guardian_registry.py` — SSOT `GuardianSpec` registry with `entrypoint_module`, `check_ids`
- `run_all_guardians.py` — aggregator emitting `combined_guardian_result.json`
- 3 guardian scripts (hygiene, manifest, contract_integrity)

## What to extract vs. discard

### Discard (dead/superseded)
- `execute_ssot_entrypoint.py` — vestigial bridge, replaced by `run_all_guardians.py` CLI
- `AutonomousDecisionEngine` class hierarchy (3 classes, ~200 LOC) — confidence scoring replaced by Guardian PASS/FAIL + HIL approval
- `PreFlightValidator` — environment checks belong in a guardian (or already covered by hygiene guardian)
- `NonInteractiveGuard` — CI-specific, not part of agentic flow
- `with_retry` decorator — generic utility, move to `apps_shared/utils/` if still needed
- `_legacy_main()` — monolithic orchestrator replaced by Guardian aggregator + dispatcher
- `RuntimeStateManager` — dashboard state; if still needed, extract to L6 observability
- Phase functions (`execute_phase1_discovery` through `execute_phase5_final`) — replaced by individual Guardian scripts + healer dispatch
- V15 manifest/gateway audit code — already has its own module
- `discover_agents_from_registry()` — already has canonical `full_agent_discovery.py`
- Markdown report generation (~200 LOC) — reporting is L6 concern, not L0

### Extract & relocate (salvageable logic)
- `EXECUTION_PLAN` + `AGENT_DEPENDENCIES` + `CANONICAL_ROSTER_KEYS` → useful metadata, relocate to `agentic_core/L0_maintenance/config/` as a healer registry
- `ReconciliationViolation` / `ReconciliationManifest` data classes → relocate to `agentic_core/L0_maintenance/types/` if still referenced
- `ASTCodeQualityValidator` → already covered by `classification_kernel.py` and FCA; archive
- `validate_territory_input()` → simple utility, relocate to shared validation utils if needed

## Implementation Plan

### Step 1: Build Healer Registry (new file)
**`agentic_core/L0_maintenance/types/healer_registry.py`**

Analogous to `guardian_registry.py`. Maps `check_id` → healer spec:
```
@dataclass(frozen=True)
class HealerSpec:
    check_id: str              # Guardian check_id this healer handles
    healer_module: str         # Dotted module path
    healer_fn: str             # Function name returning HealResult
    requires_approval: bool    # Must pass through L3 HIL?
    tier: str                  # "auto" | "supervised" | "manual"
```

Initial entries from existing guardian check_ids:
- `temp_artifacts` → auto-delete .pyc/.tmp/.bak files
- `empty_folders` → auto-remove empty dirs
- `init_only_folders` → auto-remove or flag for review
- `manifest_exists` / `lock_exists` / `checksum_match` → re-seal manifest

### Step 2: Build Remediation Dispatcher (new file)
**`agentic_core/L2_execution/scripts/remediation_dispatcher.py`**

~80-100 lines. Consumes `combined_guardian_result.json`:
1. Load aggregate `GuardianResult`
2. Filter to `FAIL` checks
3. For each failed check, look up `HealerSpec` in registry
4. If `requires_approval=True`, skip unless HIL approval token present
5. Execute healer, capture result
6. Emit per-check `HealResult` (schema-locked, parallel to `GuardianResult`)
7. Write `combined_heal_result.json`

CLI:
```
python -m agentic_core.L2_execution.scripts.remediation_dispatcher \
    --guardian-result docs/reports/verification/guardian/combined_guardian_result.json \
    --approved-checks temp_artifacts,empty_folders \
    --write-artifacts docs/reports/verification/healer \
    --strict
```

### Step 3: Build HealResult contract (new file)
**`agentic_core/L2_execution/types/heal_contract_types.py`**

Parallel to `guardian_contract.py`:
- `HealStatus`: `HEALED | PARTIAL | FAILED | SKIPPED`
- `HealResult` dataclass with `check_id`, `status`, `changes_made`, `rollback_info`
- Schema validation matching the Guardian contract pattern

### Step 4: Archive legacy files
- `execute_ssot_entrypoint.py` → `archives/deprecated/execute_ssot_entrypoint.py`
- `execute_ssot.py` → `archives/deprecated/execute_ssot.py`
- Update any imports referencing these files (scan repo)

### Step 5: Add new Guardian scripts for legacy phase coverage
The legacy pipeline covers checks not yet in the Guardian registry. Add these as new guardian scripts:

| Guardian ID | Replaces Legacy Phase | Check IDs |
|---|---|---|
| `location_alignment` | Phase 1 LocationAgent scan | `misplaced_files`, `missing_directories` |
| `hierarchy_compliance` | Phase 2.5 HierarchyAgent scan | `depth_violations`, `structure_violations` |
| `architecture_governance` | Phase 3 ArchitectureGovernorAgent audit | `layer_violations`, `naming_violations`, `circular_deps` |
| `classification_compliance` | Phase 1 FCA early detection | `naming_suffix`, `folder_mismatch` |

Each follows the existing pattern: pure scan, emit `GuardianResult`, no side effects.

### Step 6: Register new guardians + healers
- Add `GuardianSpec` entries to `guardian_registry.py`
- Add `HealerSpec` entries to `healer_registry.py`
- Wire healer functions (initially thin wrappers around existing agent `.heal()` methods)

### Step 7: CI integration
- Replace any CI references to `execute_ssot_entrypoint.py` with `run_all_guardians.py --strict`
- Add CI step for `remediation_dispatcher.py` in non-strict mode (report only)

### Step 8: Tests
- Contract tests for `HealResult` schema (parallel to existing `GuardianResult` tests)
- Registry coverage ratchet for healers (parallel to `test_guardian_meta_coverage.py`)
- Integration test: Guardian FAIL → dispatcher → healer → verify fix

## Dependency graph (new architecture)

```
run_all_guardians.py          # L5: deterministic scan
  └─→ combined_guardian_result.json
        └─→ [L3 HIL: human reviews FAIL checks]
              └─→ remediation_dispatcher.py   # L2: approved fixes only
                    ├─→ healer_registry.py    # check_id → healer mapping
                    ├─→ individual healers     # per-check fix functions
                    └─→ combined_heal_result.json
                          └─→ [L6: telemetry, dashboard, audit log]
```

## Risk mitigation
- **No big bang**: Legacy files archived, not deleted. Import scan + shim if anything still references them.
- **Incremental guardian coverage**: Start with existing 3 guardians + dispatcher. Add new guardians one at a time.
- **Backward compat**: `EXECUTION_PLAN` and `AGENT_DEPENDENCIES` preserved in healer registry for reference.
- **Test coverage**: Each new file gets a parallel test file before the archive step.

## Estimated scope
- **New files**: 4 (healer_registry, remediation_dispatcher, heal_contract, + 1 test)
- **Modified files**: 2 (guardian_registry.py additions, CI workflow)
- **Archived files**: 2 (execute_ssot_entrypoint.py, execute_ssot.py)
- **New guardian scripts** (Step 5): 4, but these are phase 2 of the refactor
- **LOC delta**: ~+400 new, ~-3,240 archived = net -2,840

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

