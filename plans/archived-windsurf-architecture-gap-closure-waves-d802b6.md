---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\architecture-gap-closure-waves-d802b6.md'
original_relative_path: 'architecture-gap-closure-waves-d802b6.md'
source_sha256: f7dcdbdd135f994f53f00b317c7ffe4b68e2864e5cdef77421b94d77bb6922e4
recovered_status: LOST_RECOVERED
last_commit: '41dafddcfc7'
last_commit_date: '2026-04-04 07:19:10 -0400'
created_date: '2026-04-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Architecture Gap Closure - Wave-Based Execution Plan

Wave-based micro-wave execution plan for closing all 50 architecture gaps identified in the canonical compliance audit, using <=15 modules per wave with ADG-backed validation gates.

---

## Wave Summary Table

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | EM-1,2 | Emergency Runtime Prohibition | ~18,000 | Mutation prohibition works | 🟢 GREEN | apps_* writes blocked |
| W2 | UWG-1,2 | Critical apps_* UWG Integration | ~22,000 | WriteGovernorMixin ready | 🟢 GREEN | 7 critical files migrated |
| W3 | UWG-3,4 | L4 Storage UWG Injection | ~25,000 | UWG 4-field API stable | 🟢 GREEN | L4 providers use UWG |
| W4 | ISO-1,2 | Break Circular Dependencies | ~20,000 | apps_engines_aliases isolated | 🟢 GREEN | 25 cross-layer imports removed |
| W5 | ISO-3,4 | L2 Facade Layer Creation | ~24,000 | Facade pattern defined | 🟢 GREEN | 15 apps_* files use facades |
| W6 | L5-1,2 | HITL Re-Clearance Gates | ~21,000 | L5ReClearanceGate implemented | 🟢 GREEN | 3 HITL paths secured |
| W7 | HASH-1,2 | Hash Continuity Wiring | ~19,000 | blueprint_hash API available | 🟢 GREEN | 4 hash chains complete |
| W8 | ORCH-1,2 | L3 Orchestration Fixes | ~17,000 | Replay engine validated | 🟢 GREEN | 2 orchestrators compliant |
| W9 | FALL-1,2 | Silent Fallback Removal | ~15,000 | Explicit disposition gates | 🟢 GREEN | 3 routers fixed |
| W10 | AUD-1,2 | Remaining Gaps + Validation | ~16,000 | ADG scanner operational | 🟢 GREEN | 12 remaining gaps closed |

**Total: ~197,000 tokens across 10 waves, all GREEN (89% of SAFE_OPERATING_CAP)**

---

## Gap Register

### Critical Gaps (C1-C5): Direct Write Bypass

**C1: apps_* Direct Writes (7 files)**
- `apps_lic/types/lic_vector_memory_types.py` - 17 write calls
- `apps_lic/types/TraceRegistry.py` - 15 write calls
- `apps_lic/reasoning/OutreachLearningAgent.py` - 8 write calls
- `apps_lic/utils/manifest_manager_util.py` - 4 write calls
- `apps_lic/reasoning/LicHealingOrchestrator.py` - 5 write calls
- `apps_lic/reasoning/LicCodeInterpreter.py` - direct writes
- `apps_lic/types/state_checkpoint_types.py` - checkpoint writes

**C2: Cross-Layer Imports (6 files)**
- `agentic_core/utils/workflow_engines/apps_engines_aliases.py` - 14 imports
- `agentic_core/L5_safety/config/structure_blueprint/ssot.py` - 7 imports
- `agentic_core/L0_routing/scripts/execution_context.py` - 5 imports
- `apps_lic/utils/lic_agent_base_util.py` - 10 imports
- `apps_lic/engines/lic_spine_adapter.py` - 6 imports
- `apps_lic/reasoning/OutreachSignalRouterAgent.py` - 6 imports

**C3: Missing HITL Re-Clearance (3 files)**
- `apps_lic/reasoning/LicHealingOrchestrator.py` - healing HITL
- `apps_lic/reasoning/HOPPipelineExecutor.py` - pipeline HITL
- `apps_rg/reasoning/RgHealingOrchestrator.py` - RG healing HITL

**C4: L4 Storage Direct Writes (4 files)**
- `agentic_core/L4_state/storage/filesystem_store.py` - storage operations
- `agentic_core/L4_state/memory/blob_storage_provider.py` - blob writes
- `agentic_core/L4_state/authority/memory_authority.py` - authority writes
- `agentic_core/L4_state/authority/run_scoped_state_authority.py` - state writes

**C5: Missing Replay/Hash Continuity (4 files)**
- `apps_lic/reasoning/LicHealingOrchestrator.py` - replay_key chain
- `apps_lic/reasoning/HOPPipelineExecutor.py` - policy_hash
- `agentic_core/L3_orchestration/engines/prompt_chain_engine.py` - blueprint_hash
- `agentic_core/L2_execution/wrappers/l2_agent_wrappers.py` - trace lineage

### High/Medium Gaps (G-series): Layer Violations

**G-L0: Silent Fallbacks (3 files)**
- Telemetry events, ensemble router, agentic router

**G-L1: L1 Writes (1 file)**
- `agentic_core/L1_cognition/engines/strategist_bio_writer.py`

**G-L2: Hash/Validation Gaps (2 files)**
- Healing tier router, tool intent executor

**G-L3: Orchestration Gaps (2 files)**
- Sovereign RAG orchestrator, reflexion engine

**G-L5: L5 Enforcement Gaps (2 files)**
- HITL missing gate, validator side-effects

**G-L6: L6 Evidence Gaps (1 file)**
- Auto-persistence adapter

**G-APPS: Package-Wide Gaps (6 packages)**
- apps_lic, apps_rg, apps_exec, apps_eval, apps_research, apps_rfp

---

## Execution Plan

### Wave 1 — Emergency Runtime Prohibition (W1: EM-1,2)
**Scope**: Block all apps_* direct writes via runtime enforcement before full UWG migration

**Modules**: 3 files
- `agentic_core/L0_routing/enforcement/mutation_prohibition.py`
- `agentic_core/L5_safety/static_checks/write_gateway_enforcer.py`
- `agentic_core/L2_execution/enforcement/uwg_interceptor_shim.py` (create)

**Commands**:
```bash
# EM-1: Extend FORBIDDEN_WRITE_LAYERS
python ops_scripts/wave1_emergency_prohibition.py --apply

# EM-2: Install UWG interceptor shim
python -c "from agentic_core.L2_execution.enforcement.uwg_interceptor_shim import install_uwg_interceptor; install_uwg_interceptor()"

# Validate
python -c "from apps_lic.types.lic_vector_memory_types import VectorMemory; vm = VectorMemory(); vm.persist()"  # Should raise PermissionError
```

**Acceptance**:
- [ ] All apps_* direct writes raise `PermissionError`
- [ ] UWG shim intercepts file operations
- [ ] Telemetry logs prohibition events
- [ ] ADG shows `blocks_direct_write` edges for all 7 C1 files

---

### Wave 2 — Critical apps_* UWG Integration (W2: UWG-1,2)
**Scope**: Add WriteGovernorMixin to 7 critical apps_* files

**Modules**: 7 files + 1 base
- `apps_lic/types/lic_vector_memory_types.py`
- `apps_lic/types/TraceRegistry.py`
- `apps_lic/reasoning/OutreachLearningAgent.py`
- `apps_lic/utils/manifest_manager_util.py`
- `apps_lic/reasoning/LicHealingOrchestrator.py`
- `apps_lic/reasoning/LicCodeInterpreter.py`
- `apps_lic/types/state_checkpoint_types.py`
- `agentic_core/L2_execution/enforcement/write_governor_mixin.py` (enhance)

**Commands**:
```bash
# UWG-1: Add WriteGovernorMixin inheritance
python tools/refactor/add_mixin.py --files wave2_critical_apps_files.txt --mixin WriteGovernorMixin

# UWG-2: Replace direct writes with governed_write
python tools/refactor/replace_writes.py --files wave2_critical_apps_files.txt --gateway-method governed_write

# Validate
pytest tests/architecture/test_uwg_integration.py -v
```

**Acceptance**:
- [ ] All 7 files use WriteGovernorMixin
- [ ] `governed_write()` called instead of direct writes
- [ ] Mutation ledger shows entries for each write
- [ ] ADG shows `writes_through` edges for all writes

---

### Wave 3 — L4 Storage UWG Injection (W3: UWG-3,4)
**Scope**: Refactor L4 storage providers to inject UWG dependency

**Modules**: 4 files
- `agentic_core/L4_state/storage/filesystem_store.py`
- `agentic_core/L4_state/memory/blob_storage_provider.py`
- `agentic_core/L4_state/authority/memory_authority.py`
- `agentic_core/L4_state/authority/run_scoped_state_authority.py`

**Commands**:
```bash
# UWG-3: Add UWG constructor injection
python tools/refactor/inject_uwg.py --files wave3_l4_storage_files.txt --pattern constructor

# UWG-4: Replace internal writes with UWG calls
python tools/refactor/replace_writes.py --files wave3_l4_storage_files.txt --gateway-method write_to_store

# Validate
pytest tests/L4_state/test_uwg_storage.py -v
```

**Acceptance**:
- [ ] L4 providers accept UWG in constructor
- [ ] No direct Path.write_* calls remain
- [ ] All writes include replay_key, signature, plan_hash
- [ ] ADG shows `writes_via_uwg` edges from L4 modules

---

### Wave 4 — Break Circular Dependencies (W4: ISO-1,2)
**Scope**: Remove agentic_core → apps_* imports and relocate aliases

**Modules**: 6 files
- `agentic_core/utils/workflow_engines/apps_engines_aliases.py` → move to apps_shared
- `agentic_core/L5_safety/config/structure_blueprint/ssot.py` - remove 7 imports
- `agentic_core/L0_routing/scripts/execution_context.py` - remove 5 imports
- `apps_lic/utils/lic_agent_base_util.py` - refactor 10 imports
- `apps_lic/engines/lic_spine_adapter.py` - refactor 6 imports
- `apps_lic/reasoning/OutreachSignalRouterAgent.py` - refactor 6 imports

**Commands**:
```bash
# ISO-1: Relocate aliases
python tools/refactor/move_module.py --from agentic_core/utils/workflow_engines/apps_engines_aliases.py --to apps_shared/compat/

# ISO-2: Update all importers
python tools/refactor/update_imports.py --old-path agentic_core.utils.workflow_engines.apps_engines_aliases --new-path apps_shared.compat.apps_engines_aliases

# Remove circular deps
python tools/refactor/remove_imports.py --files wave4_circular_dep_files.txt --pattern "from apps_lic|from apps_rg|from apps_exec"

# Validate
python tools/adg/check_layer_isolation.py --from agentic_core --to apps_*
```

**Acceptance**:
- [ ] Zero agentic_core → apps_* imports remain
- [ ] aliases module relocated to apps_shared
- [ ] All importers updated to new path
- [ ] ADG shows no `imports` edges from agentic_core to apps_*

---

### Wave 5 — L2 Facade Layer Creation (W5: ISO-3,4)
**Scope**: Create L2 facades and route apps_* calls through them

**Modules**: 15 files (3 new + 12 refactored)
- `apps_shared/gateways/agentic_core_facade.py` (create)
- `apps_shared/gateways/l2_gateway_base.py` (create)
- `apps_shared/gateways/__init__.py` (create)
- 12 apps_* files updated to use facades

**Commands**:
```bash
# ISO-3: Create L2 facade layer
python tools/refactor/create_facade.py --target agentic_core --output apps_shared/gateways/

# ISO-4: Route apps_* calls through facades
python tools/refactor/route_through_facade.py --files wave5_apps_files.txt --facade AgenticCoreFacade

# Validate
pytest tests/apps_shared/test_facade_layer.py -v
```

**Acceptance**:
- [ ] Facade layer created with L2ExecutionAgent base
- [ ] 12 apps_* files route through facades
- [ ] No direct agentic_core imports from apps_*
- [ ] ADG shows `routes_through` edges to facade layer

---

### Wave 6 — HITL Re-Clearance Gates (W6: L5-1,2)
**Scope**: Implement L5ReClearanceGate and integrate into HITL paths

**Modules**: 5 files (2 new + 3 modified)
- `agentic_core/L5_safety/enforcement/hitl_re_clearance_gate.py` (create)
- `agentic_core/L5_safety/enforcement/hitl_airlock.py` (create)
- `apps_lic/reasoning/LicHealingOrchestrator.py`
- `apps_lic/reasoning/HOPPipelineExecutor.py`
- `apps_rg/reasoning/RgHealingOrchestrator.py`

**Commands**:
```bash
# L5-1: Create re-clearance gate
python tools/codegen/create_l5_gate.py --template hitl_re_clearance --output agentic_core/L5_safety/enforcement/

# L5-2: Integrate into HITL orchestrators
python tools/refactor/add_re_clearance.py --files wave6_hitl_files.txt --gate L5ReClearanceGate

# Validate
pytest tests/L5_safety/test_hitl_re_clearance.py -v
```

**Acceptance**:
- [ ] L5ReClearanceGate class implemented
- [ ] HITL airlock pattern in place
- [ ] 3 HITL paths validate through gate
- [ ] ADG shows `validated_by_safety_plane` edges for HITL

---

### Wave 7 — Hash Continuity Wiring (W7: HASH-1,2)
**Scope**: Add blueprint_hash, policy_hash, replay_key propagation

**Modules**: 4 files
- `apps_lic/reasoning/LicHealingOrchestrator.py` - replay_key chain
- `apps_lic/reasoning/HOPPipelineExecutor.py` - policy_hash freeze
- `agentic_core/L3_orchestration/engines/prompt_chain_engine.py` - blueprint_hash
- `agentic_core/L2_execution/wrappers/l2_agent_wrappers.py` - trace lineage

**Commands**:
```bash
# HASH-1: Add hash freeze validation
python tools/refactor/add_hash_continuity.py --files wave7_hash_files.txt --hashes replay_key,policy_hash,blueprint_hash

# HASH-2: Wire trace lineage
python tools/refactor/add_trace_lineage.py --files wave7_hash_files.txt

# Validate
pytest tests/architecture/test_hash_continuity.py -v
```

**Acceptance**:
- [ ] All 4 files propagate hash chain
- [ ] blueprint_hash frozen at L3 entry
- [ ] policy_hash validated during HITL
- [ ] ADG shows `signs_execution_trace` edges with hash metadata

---

### Wave 8 — L3 Orchestration Fixes (W8: ORCH-1,2)
**Scope**: Add replay validation and policy freeze to L3 orchestrators

**Modules**: 2 files
- `agentic_core/L3_orchestration/engines/sovereign_rag_orchestrator.py`
- `agentic_core/L3_orchestration/engines/reflexion_engine.py`

**Commands**:
```bash
# ORCH-1: Add replay validation
python tools/refactor/add_replay_validation.py --files wave8_orchestrator_files.txt

# ORCH-2: Add policy_hash freeze
python tools/refactor/add_policy_freeze.py --files wave8_orchestrator_files.txt

# Validate
pytest tests/L3_orchestration/test_replay_validation.py -v
```

**Acceptance**:
- [ ] RAG orchestrator validates replay
- [ ] Reflexion engine freezes policy_hash
- [ ] All L3 entries have hash snapshots
- [ ] ADG shows `pulls_context` edges with validated metadata

---

### Wave 9 — Silent Fallback Removal (W9: FALL-1,2)
**Scope**: Add explicit disposition gates to L0 routing

**Modules**: 3 files
- `agentic_core/L0_routing/engines/ensemble_router.py`
- `agentic_core/L0_routing/engines/agentic_router.py`
- `agentic_core/L0_routing/logs/telemetry_events.ndjson` (config)

**Commands**:
```bash
# FALL-1: Add explicit disposition gates
python tools/refactor/add_disposition_gates.py --files wave9_router_files.txt

# FALL-2: Remove silent telemetry fallbacks
python tools/refactor/remove_silent_fallbacks.py --config telemetry_events.ndjson

# Validate
pytest tests/L0_routing/test_explicit_disposition.py -v
```

**Acceptance**:
- [ ] All routers have explicit disposition gates
- [ ] No silent fallback patterns remain
- [ ] Telemetry logs explicit error codes
- [ ] ADG shows `routes_through` edges with disposition metadata

---

### Wave 10 — Remaining Gaps + Validation (W10: AUD-1,2)
**Scope**: Close remaining gaps and establish continuous compliance

**Modules**: 12 gaps
- G-L1-001: strategist_bio_writer move writes
- G-L2-001, G-L2-002: hash validation, replay validation
- G-L5-001, G-L5-002: L5 enforcement, side-effect removal
- G-L6-001: L6 evidence-only fix
- G-APPS-002..006: Package-wide fixes

**Commands**:
```bash
# AUD-1: Close remaining gaps
python tools/refactor/close_gaps.py --gaps wave10_remaining_gaps.txt

# AUD-2: Create ADG compliance scanner
python tools/codegen/create_compliance_scanner.py --output tools/adg/architecture_compliance_scanner.py

# Run full validation
python tools/adg/architecture_compliance_scanner.py --full-audit --output artifacts/compliance_report.json

# Validate all gaps closed
python -c "import json; r=json.load(open('artifacts/compliance_report.json')); assert r['critical_violations']==0"
```

**Acceptance**:
- [ ] All 50 gaps closed
- [ ] ADG compliance scanner operational
- [ ] CI gate blocks non-compliant changes
- [ ] Compliance score >= 95%

---

## Rules

1. **Microwave Constraint**: No wave exceeds 15 modules/files
2. **ADG Validation**: Each wave must regenerate ADG and validate edges
3. **Wave Gate**: All prior waves GREEN before starting next wave
4. **Rollback**: Each wave has git checkpoint; rollback on failure
5. **Evidence**: ADG edge counts required as wave completion evidence
6. **No Cross-Wave Dependencies**: Each wave is self-contained

---

## Success Criteria

| Metric | Target | Verification |
|---|---|---|
| CRITICAL gaps closed | 7/7 | `grep -c CRITICAL architecture_gap_matrix.csv` returns 0 |
| HIGH gaps closed | 12/12 | HIGH severity count = 0 |
| DIRECT_WRITE violations | 0 | ADG query shows 0 direct writes outside UWG |
| CROSS_LAYER_IMPORT cycles | 0 | ADG shows no cycles between agentic_core and apps_* |
| HITL with re-clearance | 3/3 | All HITL paths have `validated_by_safety_plane` edges |
| Compliance score | >= 95% | `architecture_compliance_scanner.py --score` |
| Test pass rate | 100% | `pytest tests/ --ignore="*_adg.py"` passes |

---

## Implementation Commands (Full Sequence)

```bash
# Pre-flight: Setup
python tools/adg/regenerate_full_adg.py
git tag checkpoint-pre-wave1

# Wave 1: Emergency Hardening
python ops_scripts/wave1_emergency_prohibition.py --apply
python tools/adg/regenerate_full_adg.py
python tools/validate/wave1_validator.py --pass-gate || git checkout checkpoint-pre-wave1

# Wave 2: Critical UWG Integration
python tools/refactor/add_mixin.py --files wave2_critical_apps_files.txt --mixin WriteGovernorMixin
python tools/adg/regenerate_full_adg.py
python tools/validate/wave2_validator.py --pass-gate || git checkout checkpoint-pre-wave2

# Wave 3: L4 Storage
python tools/refactor/inject_uwg.py --files wave3_l4_storage_files.txt
python tools/adg/regenerate_full_adg.py
python tools/validate/wave3_validator.py --pass-gate || git checkout checkpoint-pre-wave3

# Continue waves 4-10...
# (Each wave follows same pattern: refactor → ADG regen → validate → checkpoint)

# Final validation
python tools/adg/architecture_compliance_scanner.py --full-audit --fail-on-critical
```

---

## Rollback Strategy

**Per-Wave Rollback**:
1. Wave fails validation → `git checkout checkpoint-pre-wave{N}`
2. Investigate failure → fix in isolation
3. Retry wave → new checkpoint on success

**Full Rollback**:
1. All waves fail → `git checkout checkpoint-pre-wave1`
2. Emergency mode → keep runtime prohibition only
3. Replan with smaller waves → retry

**Emergency Circuit Breaker**:
```python
# If production issues detected
from agentic_core.L2_execution.enforcement.uwg_interceptor_shim import uninstall_uwg_interceptor
uninstall_uwg_interceptor()  # Restores original file operations
```

---

## ADG Validation Gates

Each wave must pass ADG validation:

```python
# Wave completion validation
from tools.adg.core.adg_mcp_client import AdgMcpClient

client = AdgMcpClient()

# Check for new edges
def validate_wave(wave_id, expected_edges):
    status = client.adg_status()
    meta = client.adg_meta()
    
    # Verify ADG freshness
    assert status['is_fresh'], f"Wave {wave_id}: ADG stale"
    
    # Check edge growth
    edge_count = meta['edge_count']
    assert edge_count >= expected_edges['min'], f"Wave {wave_id}: Edge count too low"
    
    # Validate specific relation types
    for rel_type, min_count in expected_edges['relations'].items():
        nodes = client.adg_nodes_by_relation(rel_type)
        assert len(nodes) >= min_count, f"Wave {wave_id}: {rel_type} count {len(nodes)} < {min_count}"
    
    return True

# Wave 2 validation example
validate_wave('W2', {
    'min': 350000,
    'relations': {
        'writes_through': 7,
        'writes_via_uwg': 7
    }
})
```

---

## Acceptance Criteria by Wave

| Wave | Primary Evidence | Gate Condition |
|------|------------------|----------------|
| W1 | `blocks_direct_write` edges = 7 | ADG shows prohibition wired |
| W2 | `writes_through` edges >= 7 | All C1 files migrated |
| W3 | `writes_via_uwg` from L4 = 4 | L4 storage UWG-compliant |
| W4 | `imports` from agentic_core to apps_* = 0 | Circular deps broken |
| W5 | `routes_through` facade edges >= 12 | Facade layer active |
| W6 | `validated_by_safety_plane` HITL edges = 3 | Re-clearance enforced |
| W7 | `signs_execution_trace` with hash >= 4 | Hash continuity wired |
| W8 | `pulls_context` validated >= 2 | L3 replay valid |
| W9 | explicit disposition gates >= 3 | No silent fallbacks |
| W10 | compliance_score >= 95% | All gaps closed |

---

**End of Execution Plan**
