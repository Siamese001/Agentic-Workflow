# L0 Routing Scope Hardening Plan — Hardened v2

> Supersedes: `.windsurf/plans/l0-routing-scope-hardening-85d38b.md` (draft v1)
> Date: 2026-02-13
> Status: APPROVED FOR EXECUTION

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


## Problem

`L0_maintenance/` contains 388 items. Per `Layer 0 Routing Details.md`, L0 is **"Core Logic & Routing — Ingestion, Route Election, Capability Arbitration, Policy-Aware Dispatch."** The folder is dominated by developer tooling (292 scripts, 24 utils) that have nothing to do with runtime routing.

### Blast Radius

- **85 source files** across `agentic_core/` import from `L0_maintenance` (155 import statements)
- **139 test files** import from `L0_maintenance` (477 import statements)
- **Total**: 632 import statements across 224 files
- The folder name `L0_maintenance` is baked into `LAYER_ROOTS`, `LAYER_OVERRIDES`, `SOVEREIGN_TERRITORIES`, and `build_sovereign_territories()` in `structure_blueprint/_constants.py`

---

## Authority Model Decision (BINDING)

### Chosen: Model A — L0 = Routing + Control Plane Core

L0 is the **routing and system integrity control plane**. It owns:

| Capability | Rationale |
|-----------|-----------|
| Runtime routing (Ingestion, Election, Arbitration, Dispatch) | Primary L0 charter |
| Guardian runners | System-health orchestration is control-plane |
| SSOT discovery | Registry integrity is control-plane |
| Boot sequence | Pre-routing initialization |
| Routing types & contracts | Data contracts for the above |

L0 does **NOT** own:

| Excluded | Rationale | Destination |
|----------|-----------|-------------|
| Healing strategies / healing engine | Mutates system state → safety enforcement | `L5_safety/enforcement/` |
| Governance reasoning agents | Compliance enforcement → safety layer | `L5_safety/reasoning/` |
| Developer fix-it/analysis scripts | Dev tooling, not runtime | `dev_tools/` at repo root |
| Developer fix-it utils | Dev tooling, not runtime | `dev_tools/` at repo root |
| Audit types (`agent_audit_result`) | Safety data contract | `L5_safety/types/` |

### Why Model A over Model B

Model B (routing-only) would force guardian runners and SSOT discovery out of L0, creating an orphan problem — these are tightly coupled to the boot/routing lifecycle. Model A keeps them co-located while still evicting everything that violates the mutation-free principle.

### Consequence: No Rename

Under Model A, `L0_maintenance` is semantically acceptable as "maintenance of the control plane." Renaming to `L0_routing` would be misleading since guardian runners and SSOT discovery are not routing. The rename is **permanently abandoned**.

---

## Architectural Invariant (BINDING)

> **Routing must not mutate. Safety must not dispatch. Execution must not authorize.**

This invariant is enforced mechanically via:
1. Import graph analysis (no upward imports from L5→L0 routing modules)
2. AST-based cross-layer import prohibition tests
3. Deterministic test baselines

---

## Phase 0 — Architectural Freeze & Import Modeling

**MANDATORY before any file moves.**

### 0.1 Generate Import Graph

```
python ops_scripts/general/generate_import_graph.py \
  --root agentic_core/L0_maintenance \
  --output artifacts/l0_refactor/import_graph.json
```

Deliverables:
- `artifacts/l0_refactor/import_graph.json` — full import dependency graph
- `artifacts/l0_refactor/layer_dependency_matrix.json` — layer-to-layer matrix
- `artifacts/l0_refactor/upward_imports.json` — imports from higher layers into L0 (must be zero post-refactor)
- `artifacts/l0_refactor/circular_imports.json` — any import cycles involving L0

Each L0 import tagged by:
- Source file (layer + subfolder)
- Target file (layer + subfolder)
- Import type (direct, dynamic, `LAYER_ROOTS`-based)

### 0.2 Snapshot Test Baseline

```
pytest tests/ -x --tb=short > artifacts/l0_refactor/test_baseline.txt
```

- Store exit code + pass/fail/skip counts
- Store guardian runner CLI outputs for regression comparison
- Store `structure_blueprint._verify` output

### 0.3 Freeze

- No parallel feature commits during migration
- Branch: `refactor/l0-scope-hardening`
- Each phase = separate commit(s), one structural concern per commit
- Never combine move + rename in a single commit

### Acceptance Gate

- [ ] `import_graph.json` saved and reviewed
- [ ] `upward_imports.json` lists zero upward imports into L0 routing modules (pre-existing violations documented)
- [ ] `circular_imports.json` lists zero cycles (pre-existing violations documented)
- [ ] Test baseline artifact stored with pass/fail/skip counts
- [ ] Branch created, freeze communicated

---

## Phase 1 — Blueprint Update (Low risk)

Update `LAYER_OVERRIDES["L0_maintenance"]`:
- Purpose: "Core Logic & Routing — Ingestion, Route Election, Capability Arbitration, Policy-Aware Dispatch, System Integrity Control Plane"
- Update `forbidden_capabilities` to reflect routing + control-plane scope
- Add `routing_rules` and `routing_suffixes` to L0 override
- Document Model A decision in override comments

### Acceptance Gate

- [ ] Blueprint updated
- [ ] `structure_blueprint._verify` passes
- [ ] Commit: `refactor(L0): update blueprint to Model A control-plane scope`

---

## Phase 2 — Move Healing & Governance to L5 (Medium risk)

### 2.1 Files to Move

#### Healing (mutates state → L5_safety/enforcement/)

| Source | Destination |
|--------|-------------|
| `L0_maintenance/enforcement/audit_healing_strategy.py` | `L5_safety/enforcement/` |
| `L0_maintenance/enforcement/git_health_sensor_enforcer.py` | `L5_safety/enforcement/` |
| `L0_maintenance/enforcement/git_kraken_healing_strategy.py` | `L5_safety/enforcement/` |
| `L0_maintenance/enforcement/vector_healing_strategy.py` | `L5_safety/enforcement/` |
| `L0_maintenance/enforcement/ssot_guardrail.py` | `L5_safety/enforcement/` |
| `L0_maintenance/engines/sovereign_healing_engine.py` | `L5_safety/enforcement/` |

#### Governance Agents (compliance → L5_safety/reasoning/)

| Source | Destination |
|--------|-------------|
| `L0_maintenance/reasoning/BenchmarkingAgent.py` | `L5_safety/reasoning/` |
| `L0_maintenance/reasoning/BootstrapAgent.py` | `L5_safety/reasoning/` |
| `L0_maintenance/reasoning/DocstringComplianceAgent.py` | `L5_safety/reasoning/` |
| `L0_maintenance/reasoning/FilesystemSSOTReconcilerAgent.py` | `L5_safety/reasoning/` |
| `L0_maintenance/reasoning/GospelSyncAgent.py` | `L5_safety/reasoning/` |
| `L0_maintenance/reasoning/IntegrityGateExecutorAgent.py` | `L5_safety/reasoning/` |
| `L0_maintenance/reasoning/SSOTFolderCleanupAgent.py` | `L5_safety/reasoning/` |

#### Audit Types (safety data contract → L5_safety/types/)

| Source | Destination |
|--------|-------------|
| `L0_maintenance/types/agent_audit_result.py` | `L5_safety/types/` |

#### Config

| Source | Destination |
|--------|-------------|
| `L0_maintenance/legacy_agent_name_allowlist.py` | `L5_safety/config/` |

### 2.2 Healing Engine Rationale

`sovereign_healing_engine.py` (15KB) **mutates system state** — it applies healing strategies that modify files. Per the architectural invariant, routing must be mutation-free. Boot-time healing is still mutation. Healing is L5 safety enforcement, not L0 routing. Moving it preserves the authority stack: Detection (L0) → Authorization (L3) → Mutation (L5).

### 2.3 Pre-Commit Validation

Before committing each move batch:
1. AST-based import rewrite (§6 — no string-based replacement)
2. Validate no remaining L0 file imports moved files via stale paths
3. Validate L5 does not import L0 routing logic (no reverse coupling)
4. Run `circular_imports` check — zero new cycles
5. Import diff must be limited to moved files only
6. Full test suite pass

### Acceptance Gate

- [ ] All 16 files moved
- [ ] All imports updated (AST-verified, §1.4 Rename/Move Closure Rule)
- [ ] Zero circular imports introduced
- [ ] Zero cross-layer violations (L5 does not import L0 routing)
- [ ] `agent_discovery_full.json` updated
- [ ] Tests pass (compare against Phase 0 baseline — same pass count)
- [ ] Commits: one per logical group (healing, agents, types/config)

---

## Phase 3 — Script Segmentation (High risk — Migration Program)

**This is structural re-anchoring of the control plane, not a bulk move.**

### 3.1 Script Classification

Classify all 292 scripts in `L0_maintenance/scripts/` into three buckets:

| Category | Destination | Criteria |
|----------|-------------|----------|
| **Control-plane** (guardian runners, SSOT, system health) | STAY in `L0_maintenance/scripts/` | Runs in CI/boot, validates system integrity |
| **Developer tooling** (fix_*, analyze_*, migrate_*, rename_*, finalize_*) | `dev_tools/` at repo root | One-shot dev scripts, not runtime |
| **Dead/obsolete** | `archives/deprecated/` | Unused, superseded, or broken |

### 3.2 Why `dev_tools/` Not `scripts/`

`scripts/` is semantically ambiguous and will regrow entropy. `dev_tools/` is:
- Self-documenting (developer tooling, not runtime)
- Enforceable (no runtime module may import from `dev_tools/`)
- Already distinguished from `ops_scripts/` (CI/ops) and `L0_maintenance/scripts/` (control-plane)

### 3.3 Migration Checklist (Per-Batch)

For each batch of scripts moved:
1. Update imports (AST-based)
2. Update CI paths (`.github/workflows/*.yml`)
3. Update test discovery paths
4. Update CLI entrypoints / hardcoded paths
5. Update `Makefile` targets
6. Update GitHub Actions path filters
7. Update documentation references
8. Verify standalone executability (scripts must not import from `dev_tools/` at runtime)

### 3.4 Structural Enforcement

After Phase 3:
- `dev_tools/` added to `SCAN_ROOTS` exclusion (not scanned by agent discovery)
- No runtime module (`agentic_core/`, `apps_*/`) may import from `dev_tools/`
- CI guard added: `ops_scripts/ci/check_dev_tools_isolation.py`

### Acceptance Gate

- [ ] All 292 scripts classified (manifest artifact saved)
- [ ] Control-plane scripts remain in `L0_maintenance/scripts/`
- [ ] Dev tooling scripts moved to `dev_tools/`
- [ ] Dead scripts archived
- [ ] Zero runtime imports from `dev_tools/`
- [ ] CI paths updated and passing
- [ ] Makefile targets updated
- [ ] Test suite passes (compare against Phase 0 baseline)
- [ ] Commits: batched by category, one structural concern per commit

---

## Phase 4 — Utils Triage (Medium risk)

### 4.1 Classification

| Category | Files | Destination |
|----------|-------|-------------|
| **Runtime utils** (project_root, timeout_decorator, json_formatter, file_utils, init_setup, component, scan, ssot_discovery, core_integrity, complexity_visitor) | ~10 files | STAY in `L0_maintenance/utils/` |
| **Dev/fix utils** (fix_depth, force_annexation, scorched_earth, gravity_audit, sovereign_alignment, structural_fix, trim_airlocks, fix_tunnels, fix_remaining_depth, fix_mission_runner, manifest_guardian, find_misnamed, add_test_coverage, sovereign_convergence) | ~14 files | `dev_tools/` at repo root |

### Acceptance Gate

- [ ] All 24 utils classified
- [ ] Runtime utils remain in `L0_maintenance/utils/`
- [ ] Dev utils moved to `dev_tools/`
- [ ] Imports updated (AST-based)
- [ ] Tests pass

---

## Non-Regression Gates (ALL PHASES)

### Structural Invariants (Checked After Every Phase)

| Invariant | Enforcement |
|-----------|-------------|
| Zero circular imports involving L0 | `circular_imports.json` diff |
| Zero upward imports into L0 routing from L5+ | `upward_imports.json` check |
| No runtime module imports from `dev_tools/` | AST-based CI guard |
| L0 contains only routing + control-plane files | Blueprint verification pass |
| Agent discovery count unchanged (modulo expected moves) | `agent_discovery_full.json` diff |
| Test pass count ≥ Phase 0 baseline | `pytest` comparison |
| `structure_blueprint._verify` passes | Deterministic check |

### Prohibited Cross-Layer Imports (Post-Refactor)

| From | To | Status |
|------|----|--------|
| `L5_safety/*` | `L0_maintenance/reasoning/*` (routing agents) | PROHIBITED |
| `L0_maintenance/*` | `dev_tools/*` | PROHIBITED |
| `agentic_core/*` | `dev_tools/*` | PROHIBITED |
| `apps_*/*` | `dev_tools/*` | PROHIBITED |

### Runtime Equivalence

- Guardian runner CLI outputs must match Phase 0 snapshots (modulo path changes)
- `structure_blueprint._verify` output must be equivalent or improved
- No new test failures introduced

---

## Risk Rating

| Dimension | Rating | Notes |
|-----------|--------|-------|
| Phase 0 (freeze + modeling) | Low | Data gathering only |
| Phase 1 (blueprint update) | Low | Config change only |
| Phase 2 (healing/agent moves) | Medium | 16 files, well-bounded import surface |
| Phase 3 (script segmentation) | **High** | 292 files, CI/entrypoint/doc impact |
| Phase 4 (utils triage) | Medium | 24 files, smaller blast radius |
| Overall (with Phase 0 modeling) | **A** | Import graph prevents blind surgery |
| Overall (without Phase 0) | **C+** | High risk of circular dependency and authority drift |

---

## Commit Strategy

- One branch: `refactor/l0-scope-hardening`
- Multiple commits per phase, one structural concern per commit
- Never combine move + rename
- Never combine cross-layer moves with same-layer restructuring
- Each commit message: `refactor(L0): <verb> <what> to <where>`
- Squash-merge to main after full validation

---

## Artifacts Produced

| Artifact | Phase | Location |
|----------|-------|----------|
| Import graph | 0 | `artifacts/l0_refactor/import_graph.json` |
| Layer dependency matrix | 0 | `artifacts/l0_refactor/layer_dependency_matrix.json` |
| Upward imports | 0 | `artifacts/l0_refactor/upward_imports.json` |
| Circular imports | 0 | `artifacts/l0_refactor/circular_imports.json` |
| Test baseline | 0 | `artifacts/l0_refactor/test_baseline.txt` |
| Script classification manifest | 3 | `artifacts/l0_refactor/script_classification.json` |
| Utils classification manifest | 4 | `artifacts/l0_refactor/utils_classification.json` |
| This plan | — | `docs/reports/plans/l0-routing-scope-hardening.md` |

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

