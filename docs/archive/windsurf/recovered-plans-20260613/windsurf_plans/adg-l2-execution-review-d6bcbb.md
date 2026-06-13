# ADG L2 Execution Logic Review & Gap Closure Plan

Use refreshed ADG to review codebase ensuring all live execution modules (agents, tool runners, execution wrappers, healers, sandboxed actions) follow L2 logic and document breakout in process mapping.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-------------|-------|-------------|-------------|--------|------------------|
| Wave 1 | P1.1-P1.4 | ADG Analysis & Gap Identification | 8K | ADG cache available, L2 contract defined | 🟡 IN-PROGRESS | L2 execution inventory complete, gaps catalogued |
| Wave 2 | P2.1-P2.6 | Critical Executor Compliance | 12K | Healers follow tier-router pattern | 🔵 PENDING | Core executors implement L2ExecutionContract |
| Wave 3 | P3.1-P3.4 | Agent Class Standardization | 10K | SovereignBaseAgent compat preserved | 🔵 PENDING | All L2 agents inherit from L2ExecutionAgent |
| Wave 4 | P4.1-P4.3 | Process Mapping Documentation | 6K | Template exists at docs/reference/ | 🔵 PENDING | L2 breakout section published |

**Total: ~36K tokens across 4 waves**

---

## Gap Register

**GAP-1: Missing L2ExecutionContract Implementation**
- **Evidence**: `agentic_core/L2_execution/contracts/l2_execution_contract.py` defines `L2ExecutionAgent` base class with 4-phase contract (INIT→EXECUTE→EVALUATE_HEAL→SYNTHESIZE)
- **Gap**: 0 of 6 L2 reasoning agents (`EmbeddingSovereignAgent`, `RedisSovereignAgent`, `SovereignMCPGatewayAgent`, `StructuredEngineAgent`, `SubAtomicRegistryAgent`, `ToolsmithAgent`) inherit from `L2ExecutionAgent`
- **Impact**: Execution logic is inconsistent; no standardized healing integration; phase boundaries not enforced
- **Files**: 6 agent files in `agentic_core/L2_execution/reasoning/`

**GAP-2: ToolIntentExecutor Not Contract-Compliant**
- **Evidence**: `tool_intent_executor.py` implements L2.2 sandbox execution but as standalone class, not inheriting from `L2ExecutionAgent`
- **Gap**: Missing formal phase separation (E1-E5), no healing loop integration, no standardized result synthesis
- **Impact**: Tool execution lacks unified error handling and recovery paths
- **Files**: `agentic_core/L2_execution/engines/tool_intent_executor.py`

**GAP-3: Healer Infrastructure Exists but No Contract Wiring**
- **Evidence**: 25+ healer files in `healers/` directory including `healing_tier_router.py`, `healing_tier_dispatcher.py`, `file_classification_healer.py`
- **Gap**: Healers implement tier-based routing but don't integrate with `L2ExecutionAgent.l2_evaluate_and_heal()` method
- **Impact**: Healing is ad-hoc; no standardized E4 (Fixing Desk) implementation per process map
- **Files**: All files in `agentic_core/L2_execution/healers/`

**GAP-4: Missing L2 Phase E1 (Pre-Commit) Formalization**
- **Evidence**: Process map defines E1: PRE-COMMIT / PREP DESK with env/caps/budget locking, idempotency key binding, blueprint hash binding
- **Gap**: No centralized E1 implementation; each executor handles setup differently
- **Impact**: Inconsistent pre-execution validation; duplicate work not suppressed uniformly
- **Files**: Scattered across all L2 execution entry points

**GAP-5: L2 Logic Not Documented in Process Mapping**
- **Evidence**: `docs/reference/04_Live_Task_Dispatch_Execution.md` exists with E1-E5 phases
- **Gap**: No explicit module-to-phase mapping; no agent breakout showing which modules implement which L2 sub-phases
- **Impact**: Runtime behavior not traceable to documented process map; onboarding difficulty
- **Files**: `docs/reference/agentic_process_mapping_v29.md`, `docs/reference/04_Live_Task_Dispatch_Execution.md`

**GAP-6: Lifecycle Trace Contract Usage Without Phase Boundaries**
- **Evidence**: Modules use lifecycle emitters (`_emit_authorize_and_execute`, `_emit_records_healing_outcome`, etc.) but without formal phase structure
- **Gap**: Emitters called at module level, not at phase boundaries; no `run_l2_phases()` orchestration
- **Impact**: Telemetry emitted but not tied to L2.1-L2.4 phases; observability gaps
- **Files**: 393 L2 modules per ADG analysis

---

## Execution Plan

### Phase P1.1 — ADG Deep Query for L2 Execution Surface
**Scope**: Query ADG SQLite to identify all L2 execution entry points, classify by execution pattern

**Commands**:
```bash
# Query all L2 modules with call relationships
python -c "
import sqlite3
conn = sqlite3.connect('artifacts/adg/adg_indexed_04032026_1923.sqlite')
# Extract module names, classify by calls/exports pattern
# Output: l2_execution_surface.json
"

# Cross-reference with file-system agents
python tools/adg/classify_l2_modules.py --adg artifacts/adg/adg_indexed_04032026_1923.sqlite
```

**Acceptance**: JSON inventory of all 393 L2 modules with classification (agent/executor/healer/wrapper/utility)

---

### Phase P1.2 — Contract Compliance Scan
**Scope**: Static analysis of all L2 classes for L2ExecutionContract method implementation

**Commands**:
```bash
# Scan for l2_* methods and L2ExecutionAgent inheritance
python ops_scripts/ci/_adg_ci_gates.py --mode=l2_compliance --layer=L2

# Generate gap report
python -m tools.adg.analyze_l2_gaps --output docs/reports/l2_gap_analysis.json
```

**Acceptance**: Report showing which modules implement `l2_init`, `l2_execute`, `l2_evaluate_and_heal`, `l2_synthesize`

---

### Phase P1.3 — Healer Integration Analysis
**Scope**: Map healer tier routing to L2ExecutionAgent healing phase

**Commands**:
```bash
# Analyze healing_tier_router.py integration points
python tools/adg/trace_healer_integration.py --healer-dir agentic_core/L2_execution/healers/
```

**Acceptance**: Document showing how `healing_tier_router.route_by_confidence()` integrates with `l2_evaluate_and_heal()`

---

### Phase P1.4 — Gap Catalog Publication
**Scope**: Write gap analysis to SSOT location with severity scoring

**Acceptance**: `docs/reports/l2_execution_gap_analysis_04032026.md` exists with:
- [x] All 6 L2 agents listed with compliance status
- [x] ToolIntentExecutor gap documented
- [x] Healer integration gaps enumerated
- [x] Severity matrix (Critical/High/Medium/Low)

---

### Phase P2.1 — Core Executor Refactor: ToolIntentExecutor
**Scope**: Refactor `tool_intent_executor.py` to inherit from `L2ExecutionAgent`

**Changes**:
- Add `class ToolIntentExecutor(L2ExecutionAgent):`
- Implement `l2_init()` with sandbox context setup
- Move execution logic to `l2_execute()`
- Integrate healing via `l2_evaluate_and_heal()`
- Implement `l2_synthesize()` returning `ToolResult`

**Files**: `agentic_core/L2_execution/engines/tool_intent_executor.py`

**Acceptance**: 
- [x] ToolIntentExecutor inherits from L2ExecutionAgent
- [x] `run_l2_phases()` executes without error
- [x] Existing tests pass

---

### Phase P2.2 — SovereignLLMGateway Compliance
**Scope**: Align `SovereignLLMGateway` with L2ExecutionContract

**Files**: `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py`

**Acceptance**: Gateway implements 4-phase contract for LLM execution

---

### Phase P2.3 — UniversalWriteGateway Compliance
**Scope**: Align `UniversalWriteGateway` with L2ExecutionContract for L4 write operations

**Files**: `agentic_core/L2_execution/UniversalWriteGateway.py`

**Acceptance**: UWG implements 4-phase contract with proper E5 sealing

---

### Phase P2.4-P2.6 — Additional Critical Executors
**Scope**: Identify and refactor remaining high-priority executors (adaptation engines, cache clients)

---

### Phase P3.1-P3.4 — Agent Standardization
**Scope**: Migrate 6 L2 reasoning agents to L2ExecutionAgent base class

**Agents**:
1. `EmbeddingSovereignAgent`
2. `RedisSovereignAgent`
3. `SovereignMCPGatewayAgent`
4. `StructuredEngineAgent`
5. `SubAtomicRegistryAgent`
6. `ToolsmithAgent` (or deprecate if fully shim)

**Acceptance**: All agents pass `isinstance(agent, L2ExecutionAgent)` check

---

### Phase P4.1-P4.3 — Process Mapping Documentation
**Scope**: Create L2 module breakout section in `agentic_process_mapping_v29.md`

**Structure**:
```
[4.1] L2 MODULE BREAKOUT
├── [4.1.1] Phase E1 Implementations (Pre-Commit)
├── [4.1.2] Phase E2 Implementations (Validation)
├── [4.1.3] Phase E3 Implementations (Execution Core)
├── [4.1.4] Phase E4 Implementations (Healing Loop)
└── [4.1.5] Phase E5 Implementations (Sealing)
```

**Acceptance**: Process mapping contains explicit module-to-phase assignments with ADG evidence

---

## Rules

1. **Graph-First**: All file selections justified by ADG query results (skill: graph-analysis)
2. **Phase Preservation**: Existing lifecycle trace emitters must be preserved during refactoring
3. **Test Rigor**: All modified modules require tests passing before commit
4. **Backward Compatibility**: Existing agent APIs must remain functional during migration
5. **SSOT Documentation**: All process map updates saved to `docs/reference/`

---

## Success Criteria

- [ ] ADG analysis complete: 393 L2 modules classified
- [ ] Gap analysis published with severity scoring
- [ ] ToolIntentExecutor refactored to L2ExecutionAgent
- [ ] SovereignLLMGateway refactored to L2ExecutionAgent
- [ ] UniversalWriteGateway refactored to L2ExecutionAgent
- [ ] 6 L2 reasoning agents migrated to L2ExecutionAgent
- [ ] Process mapping updated with L2 module breakout section
- [ ] All tests passing (CI green)

---

## Implementation Commands (Post-Approval)

```bash
# Wave 1: Analysis
python tools/adg/classify_l2_modules.py
python -m tools.adg.analyze_l2_gaps

# Wave 2: Core executors (one at a time)
python tools/adg/migrate_to_l2_contract.py --target tool_intent_executor
python tools/adg/migrate_to_l2_contract.py --target sovereign_llm_gateway
python tools/adg/migrate_to_l2_contract.py --target universal_write_gateway

# Wave 3: Agents
python tools/adg/migrate_to_l2_contract.py --target embedding_sovereign_agent
python tools/adg/migrate_to_l2_contract.py --target redis_sovereign_agent
python tools/adg/migrate_to_l2_contract.py --target sovereign_mcp_gateway_agent
python tools/adg/migrate_to_l2_contract.py --target structured_engine_agent
python tools/adg/migrate_to_l2_contract.py --target sub_atomic_registry_agent

# Wave 4: Documentation
python tools/adg/generate_process_mapping_breakout.py --output docs/reference/agentic_process_mapping_v29.md
```

---

## Rollback Strategy

If critical issues encountered:
1. **Git revert**: Each phase is isolated commit, revert specific wave
2. **Feature flags**: Add `L2_CONTRACT_ENABLED` flag to toggle new behavior
3. **Parallel implementation**: Keep old implementation alongside new, switch via config
4. **ADG regeneration**: After any structural change, run `python tools/adg/generate_full_adg.py`

---

## Acceptance Criteria Matrix

| Metric | Target | Verification |
|--------|--------|--------------|
| L2 modules inventoried | 393 | ADG query count matches file system |
| L2ExecutionAgent implementations | 9+ (6 agents + 3 executors) | `grep -r "L2ExecutionAgent" agentic_core/L2_execution/ \| wc -l` |
| Gap analysis published | 1 document | `docs/reports/l2_execution_gap_analysis_*.md` exists |
| Process mapping updated | L2 breakout section | Section [4.1] exists in agentic_process_mapping_v29.md |
| Test pass rate | 100% | `pytest tests/unit/agentic_core/L2_execution/ --tb=short` |
