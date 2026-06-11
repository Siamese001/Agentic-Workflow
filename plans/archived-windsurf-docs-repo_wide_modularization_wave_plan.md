---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\repo_wide_modularization_wave_plan.md'
original_relative_path: 'repo_wide_modularization_wave_plan.md'
source_sha256: 697a4ff56564b86669103d8ec12b2cc1b03238664684511454860c13567123ae
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-04-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Repository-Wide Modularization Plan

Derisked refactoring initiative targeting the top 8 file-size bottlenecks across the Agentic-Workflow repository using wave-based incremental decomposition.

---

## Wave Summary Table

| Wave | Target File | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-------------|-------|-------------|-------------|--------|------------------|
| Wave 1 | `execute_ssot.py` | Extract 15+ helper functions, 8 dataclasses, 4 enums to `utils/` and `models/` | 12,500 | Pydantic models stable, no circular imports | 🟡 YELLOW | File size <300KB, 25+ symbols extracted |
| Wave 2 | `FileClassificationAgent.py` | Decompose 5,903-line agent into strategy classes: `ClassificationStrategy`, `HealingStrategy`, `ValidationMixin` | 10,200 | Agent base classes stable | 🟡 YELLOW | File size <250KB, 3 strategy modules created |
| Wave 3 | `sovereign_severity_types.py` | Split 50+ Pydantic models into 4 category files: `contracts/`, `events/`, `agents/`, `states/` | 8,800 | Model registry pattern ready | 🟢 GREEN | 4 model category modules, registry intact |
| Wave 4 | `generate_full_adg.py` | Extract 40+ functions into `adg/generation/` subpackage: `archive.py`, `reports.py`, `validation.py` | 9,500 | ADG pipeline stable | 🟡 YELLOW | File size <100KB, generation pipeline modular |
| Wave 5 | `LocationHealerAgent.py` | Decompose 3,154-line agent: extract `LocationValidator`, `PathNormalizer`, `BatchProcessor` | 7,200 | Healing pattern established | 🟢 GREEN | 3 component classes extracted |
| Wave 6 | `system_learning_memory_bridge.py` | Split 2,025-line bridge into `adapters/`, `persistence/`, `query/` modules | 6,400 | Memory MCP stable | 🟢 GREEN | 3 submodules, bridge facade preserved |
| Wave 7 | `_ssot_phases.py` | Extract phase implementations into `phases/` subpackage with registration pattern | 5,800 | Phase interface stable | 🟢 GREEN | Phase registry, 6+ phase modules |
| Wave 8 | Integration & Cleanup | Wire all modular components, remove backward-compat shims, validate with full test suite | 4,500 | All prior waves complete | 🟢 GREEN | 0 circular imports, all tests pass |

**Total: 64,900 tokens across 8 waves, YELLOW** (architectural refactoring with behavior preservation)

---

## Gap Register

**GAP-1: Monolithic Script Files**
- `execute_ssot.py` at 501KB/8,564 lines contains 50+ standalone functions, 8 dataclasses, 4 enums
- Mixes orchestration logic, utility functions, and data models in single file
- Impact: Slow IDE performance, high cognitive load, difficult testing

**GAP-2: God Class Agents**
- `FileClassificationAgent.py` (414KB) and `LocationHealerAgent.py` (179KB) violate SRP
- Agents contain classification, healing, validation, and batch processing logic
- Impact: Cannot test components independently, changes risk side effects

**GAP-3: Type Definition Monoliths**
- `sovereign_severity_types.py` at 167KB defines 50+ Pydantic models for contracts, events, agents
- Single file mixing concerns: severity levels, agent messages, state containers, simulation types
- Impact: Type changes trigger full-file rebuilds, circular import risk

**GAP-4: Tool Script Bloat**
- `generate_full_adg.py` at 147KB contains 40+ functions spanning archiving, reporting, validation
- No separation between ADG generation phases
- Impact: Cannot reuse components for partial ADG updates

**GAP-5: Adapter Complexity**
- `system_learning_memory_bridge.py` at 98KB mixes persistence, querying, and adaptation logic
- Single class handling 15+ responsibilities
- Impact: Memory bridge changes affect all downstream consumers

**GAP-6: Phase Orchestration Rigidity**
- `_ssot_phases.py` at 111KB contains hardcoded phase sequences
- Adding/removing phases requires file modification
- Impact: Cannot extend SSOT phases without core file changes

---

## Modularization Targets

### Target 1: execute_ssot.py (501KB → <300KB)

**Current State:**
- 8,564 lines mixing orchestration, utilities, models
- 50+ standalone functions (`_get_*`, `_emit_*`, `_configure_*`)
- 8 dataclasses (`RoutingDecision`, `RoutingInputs`, `ConfidenceScore`)
- 4 enums (`FailureType`, `RoutingTier`, `AgentMode`, `Territory`)

**Modularization Strategy:**
```
agentic_core/L0_routing/
├── scripts/
│   └── execute_ssot.py          # Orchestration only (3,000 lines)
├── models/
│   ├── routing.py               # RoutingDecision, RoutingInputs, etc.
│   ├── confidence.py            # ConfidenceScore, scoring utilities
│   └── territory.py             # Territory enum, territory utilities
├── utils/
│   ├── context_retrieval.py     # _retrieve_execution_context, caching
│   ├── logging_config.py        # _configure_logging, UTF-8 helpers
│   └── lazy_loaders.py          # All _get_* lazy import helpers
└── enums/
    └── routing_enums.py         # FailureType, RoutingTier, AgentMode
```

**W1 Deliverables:**
- [ ] Extract 15+ helper functions to `utils/` modules
- [ ] Move 8 dataclasses to `models/` with validation
- [ ] Relocate 4 enums to `enums/` with SSOT
- [ ] Update imports with backward-compat shims
- [ ] File size: 501KB → <300KB

---

### Target 2: FileClassificationAgent.py (414KB → <250KB)

**Current State:**
- 5,903 lines: classification + healing + validation + batch processing
- Single class `FileClassificationHealerAgent` with 30+ methods
- Tight coupling between classification logic and healing actions

**Modularization Strategy:**
```
agentic_core/L5_safety/reasoning/
├── file_classification/
│   ├── __init__.py              # Public exports
│   ├── agent.py                 # Slimmed agent (2,000 lines)
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base.py              # ClassificationStrategy ABC
│   │   ├── content_based.py     # ContentWeightedStrategy
│   │   └── extension_based.py   # ExtensionFallbackStrategy
│   ├── healing/
│   │   ├── __init__.py
│   │   ├── base.py              # HealingStrategy ABC
│   │   ├── naming.py            # NamingConventionHealer
│   │   ├── imports.py           # ImportCycleHealer
│   │   └── location.py          # LocationComplianceHealer
│   └── batch/
│       ├── __init__.py
│       └── processor.py         # BatchHealingProcessor
```

**W2 Deliverables:**
- [ ] Create `ClassificationStrategy` ABC and 2 implementations
- [ ] Create `HealingStrategy` ABC and 3 implementations  
- [ ] Extract `BatchHealingProcessor` for batch operations
- [ ] Refactor agent to use strategy pattern
- [ ] File size: 414KB → <250KB

---

### Target 3: sovereign_severity_types.py (167KB → 4 modules)

**Current State:**
- 4,072 lines, 50+ Pydantic models
- Mixes: severity enums, event types, agent messages, state containers, simulation types

**Modularization Strategy:**
```
apps_shared/types/
├── sovereign_severity_types.py  # Deprecated shim (backward compat)
├── contracts/
│   ├── __init__.py
│   ├── base.py                  # SovereignBaseModelTypes
│   ├── severity.py              # sovereign_severity, sovereign_event_type
│   └── registry.py              # CORE_CONTRACTS_REGISTRY
├── agents/
│   ├── __init__.py
│   ├── messages.py              # agent_message, agent_thought_process
│   ├── planning.py              # agent_plan, consensus_verdict
│   └── style.py                 # tone_type, style_profile, generation_config
├── states/
│   ├── __init__.py
│   ├── hard_soft.py             # hard_state, soft_state
│   ├── thermal.py               # thermal_profile, thermal_config
│   └── signals.py               # signal_context, signed_claim
└── simulation/
    ├── __init__.py
    ├── scenario.py              # sim_scenario, sim_outcome
    └── metacognition.py         # hypothesis, metacognition_report
```

**W3 Deliverables:**
- [ ] Split into 4 category modules
- [ ] Maintain `CORE_CONTRACTS_REGISTRY` across modules
- [ ] Create backward-compat shim
- [ ] All 50+ models accessible via original import path

---

### Target 4: generate_full_adg.py (147KB → <100KB)

**Current State:**
- 2,212 lines with 40+ functions
- Responsibilities: ADG generation, archiving, reporting, validation, git ops

**Modularization Strategy:**
```
tools/
├── adg/
│   ├── generation/
│   │   ├── __init__.py          # Public API
│   │   ├── core.py              # generate_full_adg() orchestration
│   │   ├── archive.py           # _archive_old_artifacts, _create_zip_archive
│   │   ├── reports.py           # _generate_standardized_reports, _generate_closure_report
│   │   ├── validation.py        # _artifact_determinism_probe, _audit_semantic_surfaces
│   │   └── persistence.py       # _persist_adg_to_memory, _auto_ingest_to_redis
│   └── generate_full_adg.py     # CLI entry point shim
```

**W4 Deliverables:**
- [ ] Extract archive operations to `archive.py`
- [ ] Extract report generation to `reports.py`
- [ ] Extract validation to `validation.py`
- [ ] Extract persistence to `persistence.py`
- [ ] File size: 147KB → <100KB

---

### Target 5: LocationHealerAgent.py (179KB → <120KB)

**Current State:**
- 3,154 lines mixing location validation, path normalization, batch processing
- Duplicates some logic from FileClassificationAgent

**Modularization Strategy:**
```
agentic_core/L5_safety/reasoning/
├── location/
│   ├── __init__.py
│   ├── agent.py                 # Slimmed LocationHealerAgent
│   ├── validator.py             # LocationValidator (extracted)
│   ├── normalizer.py            # PathNormalizer (extracted)
│   └── batch_processor.py       # BatchProcessor (extracted, shared)
```

**W5 Deliverables:**
- [ ] Extract `LocationValidator` class
- [ ] Extract `PathNormalizer` class
- [ ] Extract/share `BatchProcessor` with FileClassification
- [ ] File size: 179KB → <120KB

---

### Target 6: system_learning_memory_bridge.py (98KB → 3 modules)

**Current State:**
- 2,025 lines, single `SystemLearningMemoryBridge` class
- Mixes: persistence, querying, caching, adapter logic

**Modularization Strategy:**
```
system_learning/
├── adapters/
│   ├── __init__.py
│   └── memory_bridge.py         # Public facade (200 lines)
├── persistence/
│   ├── __init__.py
│   ├── writer.py                # Write operations (600 lines)
│   └── reader.py                # Read/query operations (800 lines)
└── cache/
    ├── __init__.py
    └── signal_cache.py          # Caching layer (400 lines)
```

**W6 Deliverables:**
- [ ] Create persistence layer with writer/reader split
- [ ] Extract caching to dedicated module
- [ ] Maintain `SystemLearningMemoryBridge` as facade
- [ ] No breaking changes to consumers

---

### Target 7: _ssot_phases.py (111KB → 6+ phase modules)

**Current State:**
- 1,645 lines with hardcoded phase implementations
- Adding phases requires modifying core file

**Modularization Strategy:**
```
agentic_core/L0_routing/
├── scripts/
│   └── _ssot_phases.py          # Phase registry + imports only
├── phases/
│   ├── __init__.py              # Phase registration
│   ├── base.py                  # SSOTPhase ABC
│   ├── validation.py            # ValidationPhase
│   ├── healing.py               # HealingPhase
│   ├── ingestion.py             # IngestionPhase
│   ├── reporting.py             # ReportingPhase
│   └── audit.py                 # AuditPhase
```

**W7 Deliverables:**
- [ ] Define `SSOTPhase` ABC with common interface
- [ ] Extract 6 phase implementations to modules
- [ ] Create phase registry with auto-discovery
- [ ] Maintain `_ssot_phases.py` as orchestrator

---

### Target 8: Integration & Cleanup

**Scope:**
- Wire all modular components from Waves 1-7
- Remove backward-compatibility shims where safe
- Resolve any circular imports
- Run full test suite validation

**W8 Deliverables:**
- [ ] All 7 targets integrated and cross-compatible
- [ ] 0 circular import violations
- [ ] Full test suite passes (7671 tests)
- [ ] ADG generation pipeline validated
- [ ] Documentation updated

---

## Success Criteria

| Metric | Target | Verification |
|--------|--------|--------------|
| execute_ssot.py size | <300KB | `wc -c` |
| FileClassificationAgent.py size | <250KB | `wc -c` |
| sovereign_severity_types.py split | 4 modules | Directory listing |
| generate_full_adg.py size | <100KB | `wc -c` |
| LocationHealerAgent.py size | <120KB | `wc -c` |
| memory_bridge modules | 3 modules | Directory listing |
| ssot_phases modules | 6+ modules | Directory listing |
| Test suite | 100% pass | `pytest tests/ -q` |
| Circular imports | 0 | `python -c "import agentic_core"` |

---

## Rollback Strategy

1. **Per-wave revert:** Git revert individual wave commits
2. **Full rollback:** Restore from pre-modularization backup branch
3. **Compatibility layer:** All waves maintain backward-compat imports
4. **Feature flags:** Critical paths can be toggled to legacy mode

---

## Implementation Commands

```bash
# Wave 1: execute_ssot.py modularization
python tools/modularize.py --target execute_ssot --output agentic_core/L0_routing/models

# Wave 2: FileClassificationAgent decomposition
python tools/modularize.py --target FileClassificationAgent --strategy pattern

# Wave 3: Type definition split
python tools/modularize.py --target sovereign_severity_types --category pydantic

# Wave 4: ADG generation modularization
python tools/modularize.py --target generate_full_adg --output tools/adg/generation/

# Wave 5-7: Agent and bridge modularization
python tools/modularize.py --target LocationHealerAgent --strategy component
python tools/modularize.py --target system_learning_memory_bridge --strategy layer
python tools/modularize.py --target _ssot_phases --strategy registry

# Wave 8: Integration validation
python -m pytest tests/ -q --tb=short
python tools/adg/generate_full_adg.py --smoke-test
```

---

*Plan generated: 2026-04-02*
*Total estimated tokens: 64,900*
*Target completion: 8 waves*
*Repository: Siamese001/Agentic-Workflow*
