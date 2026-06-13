# L0 Routing Scope Hardening Plan

Harden L0_maintenance to its canonical routing-only scope per Layer 0 Details.md, moving 319 out-of-scope maintenance scripts and utilities to their SSOT-approved destinations per structure_blueprint.

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

`L0_maintenance/` contains 388 items. Per `Layer 0 Routing Details.md`, L0 is **"Core Logic & Routing — Ingestion, Route Election, Capability Arbitration, Policy-Aware Dispatch."** Yet the folder is dominated by developer tooling (292 scripts, 24 utils) that have nothing to do with runtime routing.

## Blast Radius

- **85 files** across `agentic_core/` import from `L0_maintenance` (155 import statements)
- **139 test files** import from `L0_maintenance` (477 import statements)
- The folder name `L0_maintenance` is baked into `LAYER_ROOTS`, `LAYER_OVERRIDES`, `SOVEREIGN_TERRITORIES`, and `build_sovereign_territories()` in `structure_blueprint/_constants.py`

## Current L0_maintenance Contents — Classification

### IN-SCOPE (Routing per Layer 0 spec)

These files implement the 4 routing phases (Ingestion, Election, Arbitration, Dispatch):

| Subfolder | File | Routing Role |
|-----------|------|--------------|
| `reasoning/` | `RootCustomsAgent.py` | Contextual router / dispatch (Phase 1-4) |
| `enforcement/` | `v15_execution_gateway.py` | Execution gate (Phase 3 arbitration) |
| `enforcement/` | `v15_runtime_guard.py` | Runtime policy guard (Phase 4 dispatch) |
| `enforcement/` | `vigilance_routing.py` | Routing vigilance (Phase 2 election) |
| `enforcement/` | `v15_p3_contracts.py` | Governance contracts (Phase 3) |
| `enforcement/` | `v15_p4_contracts.py` | Knowledge/provenance contracts |
| `enforcement/` | `v15_p5_contracts.py` | Crypto trust contracts |
| `enforcement/` | `v15_p6_contracts.py` | Meta-invariant contracts |
| `enforcement/` | `boot_sequence.py` | System boot integrity (Phase 0 pre-routing) |
| `types/` | `v15_types.py` | RouteDecisionArtifact, routing types |
| `types/` | `v15_contracts.py` | TelemetryEmitter, enforcement contracts |
| `types/` | `v15_p2_types.py` | SemanticClock (used by routing decisions) |
| `types/` | `v15_p2_contracts.py` | Determinism contracts |
| `types/` | `v15_p3_types.py` | Governance types (EvidencePack, etc.) |
| `types/` | `v15_p4_types.py` | Knowledge/provenance types |
| `types/` | `v15_p5_types.py` | Crypto trust types |
| `types/` | `v15_p6_types.py` | Meta-invariant types |
| `types/` | `guardian_contract.py` | Guardian interface contracts |
| `types/` | `guardian_registry.py` | Guardian registry types |
| `types/` | `integration_contract.py` | Integration contract types |
| `config/` | `detection_signal_config.py` | Signal detection config (Phase 1 ingestion) |
| `policy/` | `v15_policy_pack.json` | Policy configuration data |
| `engines/` | `sovereign_healing_engine.py` | **BORDERLINE** — healing is maintenance, not routing |

### OUT-OF-SCOPE (Maintenance tooling, NOT routing)

| Subfolder | Count | Content | Proposed Destination |
|-----------|-------|---------|---------------------|
| `scripts/` | 292 .py files | Developer tooling: fix_imports, fix_apps, ast_stats, agent_discovery, guardian runners, dashboard generators, migration utilities | See Script Triage below |
| `utils/` | 24 .py files | fix_depth_violations, force_annexation, scorched_earth_merge, gravity_audit, sovereign_alignment, structural_fix, etc. | See Utils Triage below |
| `reasoning/` | 6 agents | BenchmarkingAgent, BootstrapAgent, DocstringComplianceAgent, FilesystemSSOTReconcilerAgent, GospelSyncAgent, IntegrityGateExecutorAgent, SSOTFolderCleanupAgent | `L5_safety/reasoning/` (governance/compliance agents) |
| `enforcement/` | 4 files | audit_healing_strategy, git_health_sensor, git_kraken_healing_strategy, vector_healing_strategy | `L5_safety/enforcement/` (healing strategies) |
| `enforcement/` | 1 file | ssot_guardrail.py | `L5_safety/enforcement/` |
| `types/` | 1 file | agent_audit_result.py | `L5_safety/types/` |
| root | 1 file | legacy_agent_name_allowlist.py | `L5_safety/config/` or `agentic_core/config/` |
| `engines/` | 1 file | sovereign_healing_engine.py | `L5_safety/enforcement/` (healing, not routing) |

### Script Triage (292 files → 3 destinations)

| Category | Examples | Destination |
|----------|----------|-------------|
| **Guardian runners** (run_guardian_*, run_all_guardians) | `run_all_guardians.py`, `run_guardian_hierarchy_compliance.py` | Keep in `L0_maintenance/scripts/` — these are L0 system-health scripts per blueprint `extra_subfolders.scripts` |
| **SSOT/discovery** (execute_ssot, full_agent_discovery, ssot_discovery) | `execute_ssot.py`, `full_agent_discovery.py` | Keep in `L0_maintenance/scripts/` — system integrity |
| **Developer fix-it scripts** (fix_*, finalize_*, migrate_*, rename_*) | `fix_all_imports_comprehensive_util.py`, `fix_remaining_imports_util.py` | Move to `scripts/` at repo root (dev tooling, not runtime) |
| **Analysis/audit utilities** (analyze_*, audit_*, complexity_*, generate_*) | `analyze_app_files_util.py`, `complexity_reducer.py` | Move to `scripts/` at repo root |

### Utils Triage (24 files → 2 destinations)

| Category | Examples | Destination |
|----------|----------|-------------|
| **Runtime utils** (project_root, timeout_decorator, json_formatter) | `project_root_util.py`, `timeout_decorator_util.py` | Keep in `L0_maintenance/utils/` |
| **Developer/fix utils** (fix_depth, force_annexation, scorched_earth, structural_fix) | `fix_all_tunnels_util.py`, `scorched_earth_merge_util.py` | Move to `scripts/` at repo root or `agentic_core/utils/` |

## Execution Strategy

Due to the enormous blast radius (632 import statements across 224 files), this must be phased:

### Phase 1: Blueprint Update (Low risk)
- Update `LAYER_OVERRIDES["L0_maintenance"]` purpose from "Reflexive system health, boot integrity, and compliance checks" to "Core Logic & Routing — Ingestion, Route Election, Capability Arbitration, Policy-Aware Dispatch"
- Update `forbidden_capabilities` to reflect routing scope
- Add routing_rules and routing_suffixes to L0 override

### Phase 2: Move Out-of-Scope Agents (Medium risk, ~7 agents)
- Move 6 maintenance agents from `L0_maintenance/reasoning/` → `L5_safety/reasoning/`
- Move 5 healing/audit enforcement files from `L0_maintenance/enforcement/` → `L5_safety/enforcement/`
- Move `agent_audit_result.py` from `L0_maintenance/types/` → `L5_safety/types/`
- Move `sovereign_healing_engine.py` → `L5_safety/enforcement/`
- Update all imports (§1.4 Rename/Move Closure Rule)
- Run discovery + structure verification + tests

### Phase 3: Script Segregation (High risk, ~292 files)
- Create `scripts/` at repo root if not exists (for pure dev tooling)
- Move ~200 developer fix-it/analysis scripts out of `L0_maintenance/scripts/`
- Keep ~90 guardian/SSOT/system-health scripts in `L0_maintenance/scripts/`
- Update any cross-references

### Phase 4: Folder Rename (HIGHEST risk — optional, deferred)
- Rename `L0_maintenance` → `L0_routing` to match spec
- Update ALL 632 import paths
- Update `LAYER_ROOTS`, `LAYER_OVERRIDES`, `SOVEREIGN_TERRITORIES`
- Update `structure_blueprint_config.py`, discovery, and all test fixtures
- **Recommend deferring** this to a dedicated wave due to blast radius

## Questions Before Implementation

1. **Phase 4 (rename)**: Should we rename `L0_maintenance` → `L0_routing` now, or defer to a separate dedicated wave? (Blast radius: 632 imports across 224 files)
2. **Script destination**: Should out-of-scope dev scripts go to `scripts/` at repo root, or to a new `dev_tools/` directory?
3. **Healing engine**: `sovereign_healing_engine.py` is borderline — it runs healing during boot which is arguably L0 scope. Move to L5, or keep?
4. **Phase ordering**: Execute all phases in one commit, or separate commits per phase?

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

