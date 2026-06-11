---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\agent-taxonomy-healing-hardening-0dea72.md'
original_relative_path: 'agent-taxonomy-healing-hardening-0dea72.md'
source_sha256: a3425d4ff0ea9e6366abcc4a68962a0b0b632579dca7ebc4e825a53eb55fb267
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-04-01'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Agent Taxonomy & Healing Standardization Hardening Plan

Standardize all agents across the repository to a canonical execution taxonomy aligned with L2 subphases, eliminate healing blockers, and make `--heal` deterministic and universal across all eligible agents while preserving sovereign boundaries and backward compatibility.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| Wave 1 | P1-DISCOVERY, P2-CONTRACT | Pilot: 5 core agents, L2 contract definition, heal flag audit | 45,000 🟢 | ADG hot, entrypoint stable, tests passing | PENDING | Pilot agents execute heal phase; contract interface defined |
| Wave 2 | P3-HOP, P4-HOP-TEST | HOP Pipeline: 9 HOP agents normalized to canonical taxonomy | 65,000 🟢 | Wave 1 contract stable, HOP engine accessible | PENDING | All HOP agents classify correctly; --heal propagates |
| Wave 3 | P5-CROSS-APP | Cross-App Territory: RG/Eval/Exec agents aligned | 55,000 🟢 | Wave 2 complete, no HOP regressions | PENDING | 8 cross-app agents follow L2 contract |
| Wave 4 | P6-L5L6, P7-REMAINING | L5 Safety + L6 Observability + Remaining LIC agents | 85,000 🟢 | Prior waves stable, safety plane active | PENDING | 22 agents classified; heal control matrix complete |
| Wave 5 | P8-CORE-L2, P9-VALIDATION | Core L2 execution agents + Integration validation | 60,000 🟢 | All prior waves complete, tests green | PENDING | 6 core L2 agents aligned; --heal deterministic proof |

**Total: ~310,000 tokens across 5 waves, all GREEN**

---

## Gap Register

**GAP-1: Agent Taxonomy Drift**
- 58+ agent files exist with inconsistent naming, role definitions, and layer assignments
- Many are shims redirecting to consolidated implementations (e.g., `ArchetypeIndicatorsAgent` → config module)
- No canonical classification: Planner vs Router vs Execution vs Heal vs Orchestrator vs Safety vs Observer
- **Impact**: Cannot consistently apply healing policy; agents may bypass L2 execution contract

**GAP-2: Healing Control Fragmentation**
- `--heal` parsed at entrypoint (`execute_ssot_entrypoint.py:227`) but propagation to agents is inconsistent
- No unified heal enablement check across agent classes
- Per-agent `heal_mode`, `disable_heal`, and feature flags exist but are not centrally governed
- **Impact**: Healing behavior varies by agent; some agents silently skip heal phase

**GAP-3: L2 Subphase Inconsistency**
- Documented L2 model: INIT → EXECUTE → EVALUATE/HEAL → SYNTHESIZE (per `agentic_process_mapping_v25.md:184-211`)
- Actual implementation varies: some agents use custom phase names, skip validation, or have divergent heal entry conditions
- No shared `L2ExecutionPhase` enum or base protocol enforced
- **Impact**: Inconsistent execution semantics; heal phase may be entered at wrong time or skipped

**GAP-4: Flag Parsing Inconsistency**
- Entrypoint defines `--heal`, `--dry-run`, `--validate`, `--interactive`, `--manual` flags
- Agents may interpret these differently or ignore them
- Shadow copies of flag logic in agent-specific argument parsers
- **Impact**: Same flags produce different behavior across agents

**GAP-5: Shim/Consolidation Debt**
- Many `apps_lic/reasoning/*Agent.py` files are now backward-compatibility shims
- Actual implementations relocated to `engines/`, `config/`, or consolidated executors
- **Impact**: Code clutter; import confusion; MRO complexity

---

## Execution Plan

### Phase 1 — Discovery & Base Contract (Wave 1)
**Scope**: Inventory all agents; define canonical taxonomy; establish L2 execution contract; pilot with 5 core agents

**Commands**:
```bash
# Inventory all agents with taxonomy classification
python tools/adg/generate_full_adg.py --scope agent_inventory
# Run pilot agent tests
python -m pytest tests/unit/agentic_core/base_agents/ -v --tb=short
# Validate --heal propagation to pilot agents
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --heal --plan
```

**Deliverables**:
1. Complete agent inventory table (current_name, layer, role, canonical_role, action_needed)
2. `L2ExecutionContract` interface defined in `agentic_core/L2_execution/contracts/`
3. Pilot agents refactored: SovereignBaseAgent, 2 L2 execution agents, 2 L5 safety agents
4. Heal control matrix showing which flags/blockers were removed

**Acceptance**:
- [ ] All 58+ agents classified into 7 canonical roles
- [ ] `L2ExecutionPhase` enum with 4 phases (INIT, EXECUTE, EVALUATE_HEAL, SYNTHESIZE)
- [ ] Pilot agents enter HEAL phase when `--heal` and recoverable failure present
- [ ] No regressions in existing tests

### Phase 2 — HOP Pipeline Normalization (Wave 2)
**Scope**: Normalize 9 HOP agents to canonical taxonomy; wire to L2 execution contract

**Commands**:
```bash
# Test HOP agents pre-refactor
python -m pytest tests/unit/apps_lic/reasoning/test_HOP* -v
# Run refactored HOP pipeline
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --heal --territory apps_lic
# Validate taxonomy compliance
python ops_scripts/ci/check_taxonomy_compliance.py --territory apps_lic
```

**Agents to Refactor**:
- HOP1ProfileAnalysisAgent → **Planner Agent** (L1)
- Hop2ResearchAgent → **Execution Agent** (L2)
- HOP3SenderGroundingAgent → **Execution Agent** (L2)
- Hop4RoutingAgent → **Router Agent** (L0)
- HOP5GenerationAgent → **Execution Agent** (L2)
- Hop6ValidationAgent → **Safety/Guard Agent** (L5)
- HOP7GateDecisionAgent → **Safety/Guard Agent** (L5)
- HOP8QAReportAgent → **Observer/Evaluator Agent** (L6)
- HOP9IntegrationAgent → **Orchestrator Agent** (L3)

**Acceptance**:
- [ ] Each HOP agent classified and renamed if semantically inconsistent
- [ ] All HOP agents use shared `L2ExecutionContract` for L2 phases
- [ ] `--heal` triggers heal phase consistently across all 9 HOP agents
- [ ] Shim files marked deprecated but preserved for backward compatibility

### Phase 3 — Cross-App Territory Alignment (Wave 3)
**Scope**: Align apps_rg, apps_eval, apps_exec agents to canonical taxonomy

**Commands**:
```bash
# Run cross-app test sweep
python -m pytest tests/unit/apps_rg/ tests/unit/apps_eval/ tests/unit/apps_exec/ -v --ignore-glob="*_adg.py"
# Validate --heal across territories
python ops_scripts/ci/_run_heal_with_mutation.py --territory apps_rg
python ops_scripts/ci/_run_heal_with_mutation.py --territory apps_eval
```

**Agents to Refactor**:
- apps_rg: ProactiveAgent, FactCheckAgent, HeadlineOutputAgent, ExecutiveSummaryOutputAgent
- apps_eval: EvalOrchestrator, TestDiscoveryAgent
- apps_exec: BriefAssemblyAgent, SourceIngestionAgent

**Acceptance**:
- [ ] All 8 cross-app agents classified to canonical roles
- [ ] No layer violations (e.g., L1 agents not executing tools directly)
- [ ] Shared execution contract used for L2-capable agents

### Phase 4 — L5/L6 + Remaining LIC Agents (Wave 4)
**Scope**: Safety, observability, and remaining apps_lic agents; dead code elimination

**Commands**:
```bash
# Run L5/L6 safety tests
python -m pytest tests/unit/agentic_core/L5_safety/ tests/unit/agentic_core/L6_observability/ -v
# Execute heal with safety plane validation
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --heal --fence-self-check
# Generate heal control matrix report
python tools/adg/report_heal_control_matrix.py --output docs/reports/heal_control_matrix.md
```

**Agents to Refactor (22 total)**:
- L5 Safety: GovernanceAgent, CodeJanitorAgent, PascalSovereigntyAgent, HygieneGuardianAgent
- L6 Observability: PerformanceAnalystAgentSimple
- apps_lic remaining: GovernanceShieldAgent, ExecutiveStrategyAgent, LicReflectionAgent, LeadQualityAgent, DeliverabilityAgent, CampaignBalanceAgent, OutreachMessageAgent, MessageComplianceAgent, MessageArchitectAgent, OutreachValidationExecutorAgent, OutreachProactiveAgent, OutreachSignalRouterAgent, OutreachLearningAgent, IntelligenceLibrarianAgent, LicTemplateOptimizerAgent, DispatchOutreachToolsAgent, ValidatorAgent

**Dead Code Elimination**:
- Shim files marked deprecated in Wave 2-3 can be deleted in this wave
- Obsolete feature flags removed after centralized replacement

**Acceptance**:
- [ ] Heal control matrix documenting every blocker and its disposition
- [ ] All 22 agents classified; obsolete agents deleted or marked deprecated
- [ ] L5 safety agents never execute business work or own healing
- [ ] L6 observability agents never block L2 healing inline

### Phase 5 — Core L2 Execution + Validation (Wave 5)
**Scope**: Final alignment of core L2 execution agents; deterministic --heal validation

**Commands**:
```bash
# Test core L2 execution agents
python -m pytest tests/unit/agentic_core/L2_execution/ -v
# Validate --heal determinism
python tests/architecture/test_adg_digest_stable.py::test_adg_digest_stable_two_runs -v
# Full integration test with --heal
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --heal --territory agentic_core --verbose
```

**Agents to Refactor (6 core L2)**:
- StructuredEngineAgent → **Execution Agent** (L2)
- SovereignMCPGatewayAgent → **Execution Agent** (L2)
- RedisSovereignAgent → **Execution Agent** (L2)
- EmbeddingSovereignAgent → **Execution Agent** (L2)
- SubAtomicRegistryAgent → **Execution Agent** (L2)
- ToolsmithAgent → **Execution Agent** (L2)

**Acceptance**:
- [ ] All 6 core L2 agents conform to `L2ExecutionContract`
- [ ] `--heal` deterministically triggers heal phase across all eligible L2 agents
- [ ] Integration tests prove heal behavior consistency (before/after comparison)
- [ ] No duplicate or contradictory healing control paths remain

---

## Rules

1. **No Layer Violations**: L0 agents route only; L1 agents plan only; L2 agents execute and heal only; L5 agents constrain only; L6 agents observe only
2. **Backward Compatibility**: Existing public APIs preserved; shims maintained during deprecation period
3. **MRO Stability**: Inheritance chains must remain stable; no mixin insertion that changes method resolution
4. **Centralized Healing**: `--heal` flag parsed once at entrypoint; propagation via shared context, not per-agent reparse
5. **Deterministic Heal Entry**: Heal phase entered on: (a) recoverable failure classification + `--heal`, (b) explicit L5 hard deny, (c) unrecoverable failure, (d) exhausted retry budget
6. **Fail-Closed**: When in doubt, block healing; require explicit policy to enable
7. **No New Flags**: Reuse existing flag infrastructure; no agent-specific feature flags for heal enablement

---

## Success Criteria

- [ ] **Taxonomy Compliance**: Every agent belongs to one of 7 canonical roles (Planner, Router, Execution, Heal, Orchestrator, Safety, Observer)
- [ ] **L2 Contract Uniformity**: Every execution-capable agent uses the same L2 subphase contract (INIT → EXECUTE → EVALUATE/HEAL → SYNTHESIZE)
- [ ] **Heal Determinism**: `--heal` consistently activates healing across all eligible L2 agents; behavior does not vary by agent implementation
- [ ] **Blocker Elimination**: All dead flags, kill switches, and contradictory branches removed or converted to hard-stop policy gates
- [ ] **Boundary Preservation**: Architecture boundaries remain aligned to canonical process map; no healing moved into L1/L0/L4/L6
- [ ] **Test Compliance**: All existing tests pass; no test skips introduced; new regression tests for heal behavior
- [ ] **Documentation**: Architecture findings summary; canonical mapping table; heal control matrix; before/after examples

---

## Implementation Commands

```bash
# Phase 1: Discovery & Contract
python tools/adg/generate_full_adg.py --scope agent_inventory
python -c "from agentic_core.L2_execution.contracts.l2_execution_contract import L2ExecutionPhase; print('Contract OK')"

# Phase 2: HOP Pipeline
python ops_scripts/ci/check_taxonomy_compliance.py --territory apps_lic --fix
python -m pytest tests/unit/apps_lic/reasoning/test_HOP* -v

# Phase 3: Cross-App
python ops_scripts/ci/check_taxonomy_compliance.py --territory apps_rg,apps_eval,apps_exec --fix
python -m pytest tests/unit/apps_rg/ tests/unit/apps_eval/ tests/unit/apps_exec/ -v --ignore-glob="*_adg.py"

# Phase 4: L5/L6 + Remaining
python -m pytest tests/unit/agentic_core/L5_safety/ tests/unit/agentic_core/L6_observability/ -v
python tools/adg/report_heal_control_matrix.py

# Phase 5: Core L2 + Validation
python -m pytest tests/unit/agentic_core/L2_execution/ -v
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --heal --territory agentic_core --verbose
```

---

## Rollback Strategy

If things go wrong:
1. **Per-Wave Rollback**: Each wave maintains branch `wave{N}-agent-hardening`; can revert individual waves
2. **Deprecation-First**: Wave 2-4 mark shims deprecated but do not delete; full rollback via reverting deprecations
3. **Feature Flag Guard**: If `HEAL_STANDARDIZATION_ENABLED` env var not set, agents use legacy heal paths
4. **ADG Checkpoint**: ADG regenerated before each wave; `adg_indexed_pre_wave{N}.sqlite` preserved for comparison
5. **Emergency Stop**: If CI fails on any wave, block subsequent waves until resolved

---

## Acceptance Criteria Matrix

| Metric | Target | Verification |
|--------|--------|--------------|
| Agents classified | 58+ | `python tools/adg/report_agent_taxonomy.py --count` |
| Taxonomy compliance | 100% | `python ops_scripts/ci/check_taxonomy_compliance.py --pass` |
| Heal phase entry | All L2 agents | `python tests/architecture/test_heal_phase_entry.py` |
| Heal flag consistency | 0 variance | Compare `--heal` behavior across 10 sample agents |
| Dead flag removal | All identified | `python tools/adg/report_heal_control_matrix.py --verify` |
| Test pass rate | 100% | `python -m pytest tests/ --ignore-glob="*_adg.py" -q` |
| API backward compat | 100% | No import errors in `tests/compatibility/` |

---

## Remaining Risks / Intentionally Preserved Hard-Stops

**Preserved Hard-Stops** (will remain as explicit policy gates):
1. **L5 Hard Deny**: `GovernanceAgent` can emit explicit `heal_blocked` signal; this is valid safety authority
2. **Unrecoverable Failure**: Syntax errors, import cycles, and architectural violations classified non-recoverable
3. **Mutation Boundary**: Direct L4 writes without UWG routing are non-healable (sovereignty violation)
4. **Exhausted Budget**: Retry count > 3 triggers GEMINI tier; > 5 triggers HITL escalation (not auto-heal)

**Risks**:
1. **MRO Instability**: Deep mixin hierarchies may have unexpected resolution after base class changes
2. **Cross-Import Cycles**: Moving agents between modules may create import cycles requiring lazy import fixes
3. **Test Dependencies**: Some tests may rely on specific agent class names or method signatures
4. **Performance**: Unified execution contract may add overhead; need benchmark comparison

**Mitigation**:
- MRO validation unit test after each wave
- Import cycle detection in CI gate
- Test compatibility shims for renamed agents
- Performance benchmark before/after each wave
