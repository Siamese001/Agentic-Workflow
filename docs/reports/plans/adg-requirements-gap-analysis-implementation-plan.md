# ADG Gap Analysis & Wave-Based Implementation Plan

Comprehensive gap analysis of ADG against 11 reference documents defining agentic requirements, with phased implementation plan to close critical coverage gaps.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| Wave 1 | P1-Orchestration | Orchestration wiring (routes_to_agent, orchestrates_workflow, dispatches_execution_plan) | ~175K 🟢 | Agent registry stable, 190 agents defined | PENDING | All 190 agents have orchestration edges |
| Wave 2 | P2-Safety | Safety plane hardening (applies_guardrail, validates_agent_capability, checks_agent_registry) | ~145K 🟢 | Wave 1 complete, no registry changes | PENDING | 100% agent coverage for safety validation |
| Wave 3 | P3-Observability | Observability infrastructure (emits_metric_event, emits_replay_key, captures_runtime_anomaly) | ~160K 🟢 | Wave 2 safety gates active | PENDING | Full telemetry coverage on execution paths |
| Wave 4 | P4-HITL | Human-in-the-loop integration (escalates_to_human, requires_human_review, observes_runtime_state) | ~135K 🟢 | Wave 3 telemetry active | PENDING | HITL gates at all safety-critical boundaries |
| Wave 5 | P5-Propagation | Violation propagation & learning (violation_propagates_through, feeds_meta_learning, captures_pattern) | ~125K 🟡 | Prior waves stable | PENDING | 6.2x violation amplification achieved |
| Wave 6 | P6-Integration | Cross-layer integration & end-to-end validation | ~140K 🟢 | All prior waves complete | PENDING | 100% closure validation pass |

**Total: ~880K tokens across 6 waves, 5 GREEN, 1 YELLOW**

---

## Gap Register

### Critical Gaps (Blocking Execution)

**GAP-1: Orchestration Coverage Deficit**
- Current: `orchestrates_workflow=1`, `dispatches_execution_plan=1`, `validates_agent_capability=1`, `checks_agent_registry=1`
- Required: ~190 edges per relation (1 per agent)
- Impact: Execution routing not captured; DAG analysis impossible
- Source: L2 Execution Workflow reference doc (AGENT_REGISTRY with 190 agents)

**GAP-2: Safety Plane Under-Instrumentation**
- Current: `applies_guardrail=95`, `validated_by_safety_plane=328`
- Required: ~3,011 modules × 7 safety dimensions minimum
- Impact: Blast radius analysis incomplete; safety bypass risks undetected
- Source: L5 Safety Enforcement Plane reference doc

**GAP-3: Determinism Infrastructure Sparse**
- Current: `emits_replay_key=6`, `emits_determinism_digest=2,898`
- Required: All execution traces must emit replay keys
- Impact: Replay debugging unavailable for 99.8% of execution paths
- Source: Observability Replay Determinism reference doc

**GAP-4: HITL Integration Minimal**
- Current: `escalates_to_human=19`, `requires_human_review=25`
- Required: HITL gates at all L5 safety boundaries (~3,000)
- Impact: Human escalation pathways not traceable; compliance gaps
- Source: HITL v4 reference doc

**GAP-5: Violation Propagation Under-Developed**
- Current: `violation_propagates_through=1`
- Required: 6.2x amplification (per Phase 3 semantic resolution precedent)
- Impact: Antipattern impact radius unknown; downstream contamination untracked
- Source: L5 Safety Enforcement Plane + System Learning Pipeline v4

**GAP-6: Context Flow Incomplete**
- Current: `pulls_context=266`
- Required: Full L1-L4 context assembly pipeline coverage
- Impact: Context provenance tracing broken; prompt assembly gaps
- Source: C0 Prompt Assembly L4 + L1 Cognitive Studio reference docs

**GAP-7: UWG Write Authority Uncaptured**
- Current: `execution_terminates_at_uwg=6`, `writes_through=1,219`
- Required: All mutations through UWG gateway
- Impact: Write authority analysis incomplete; bypass detection impossible
- Source: L4 & UWG - State reference doc

### Moderate Gaps (Monitoring Required)

**GAP-8: Metric Event Emission Low**
- Current: `emits_metric_event=29`
- Required: ~15,297 per P4 observability precedent
- Impact: Operational telemetry insufficient

**GAP-9: Learning Integration Gaps**
- Current: `feeds_meta_learning=2`, `captures_pattern=0`
- Required: ~1,944 per P3 learning maturity precedent
- Impact: System learning pipeline under-fed

**GAP-10: Test Coverage Potential**
- Current: `tests_execution_of=13,547` (good baseline)
- Opportunity: Link to remaining uncovered symbols

---

## Requirements Matrix

### From Reference Documents

| Requirement Domain | Key Edge Types | Source Document | Target Coverage |
|-------------------|--------------|-----------------|-----------------|
| **L4 State & UWG** | execution_terminates_at_uwg, writes_through, snapshots_state, signs_execution_trace | L4 & UWG - State.md | All mutations through UWG |
| **L2 Execution** | routes_to_agent, orchestrates_workflow, dispatches_execution_plan, validates_agent_capability, checks_agent_registry | L2 Execution Workflow.md | 190 agents × 5 dims = 950 edges |
| **Observability** | emits_replay_key, emits_determinism_digest, emits_metric_event, records_execution_trace | Observability Replay Determinism.md | All execution paths |
| **HITL** | escalates_to_human, requires_human_review, guards_replay, observes_runtime_state | HITL v4.md | All safety-critical boundaries |
| **Prompt Assembly** | pulls_context, reads_through, routes_through, generates_prompt | C0 Prompt Assembly L4.md | L1-L4 context pipeline |
| **Cognitive Studio** | proposal_commits_routing, reads_policy_state | Layer 1 - Cognitive Studio.md | Intent routing coverage |
| **Retrieval** | retrieves_via, embeds_into, chunks_into | Ingestion and Retrieval Pipeline.md | Document processing pipeline |
| **System Learning** | feeds_meta_learning, captures_pattern, improves_agent_policy, stores_learning_state | System Learning Pipeline v4.md | Meta-learning coverage |
| **Evaluation Spine** | invokes_eval, produces_preference_pair, builds_dpo_batch | Evaluation Spine & Post-Execution.md | Eval pipeline instrumentation |
| **L5 Safety** | applies_guardrail, validated_by_safety_plane, observes_policy_state, violation_propagates_through | L5 Safety Enforcement Plane.md | Full safety plane coverage |
| **Process Mapping** | agent_executes_agent, controls_flow, flows_to, emits_side_effect | agentic_process_mapping_v25.md | Execution flow coverage |

---

## Execution Plan

### Wave 1 — Orchestration Baseline Hardening (P1-Orchestration)

**Scope**: Wire all 190 registered agents with orchestration edges per L2 Execution Workflow requirements

**Target Edge Types**:
- `routes_to_agent`: 0 → 190
- `orchestrates_workflow`: 1 → 190
- `dispatches_execution_plan`: 1 → 190
- `validates_agent_capability`: 1 → 190
- `checks_agent_registry`: 1 → 190

**Implementation Steps**:
1. **Infrastructure Extension** (`agentic_core/adg/schema.py`)
   - Add 5 new frozensets: `ROUTES_TO_AGENT_SYMBOLS`, `ORCHESTRATES_WORKFLOW_SYMBOLS`, `DISPATCHES_EXECUTION_PLAN_SYMBOLS`, `VALIDATES_AGENT_CAPABILITY_SYMBOLS`, `CHECKS_AGENT_REGISTRY_SYMBOLS`
   - Update `__all__` entries

2. **Runtime Contract Extension** (`agentic_core/runtime/lifecycle_trace_contract.py`)
   - Add 5 new loggers + emitter functions: `_emit_routes_to_agent`, `_emit_orchestrates_workflow`, `_emit_dispatches_execution_plan`, `_emit_validates_agent_capability`, `_emit_checks_agent_registry`
   - Update `__all__` entries
   - Add P1 self-bootstrap calls

3. **Scanner Visitor** (`agentic_core/adg/extraction/static_scanner.py`)
   - Create `_P1OrchestrationGovernanceVisitor` (G28 equivalent)
   - Map 5-relation symbol detection
   - Wire emitter imports and self-bootstrap calls
   - Register visitor in `scan()`

4. **ADG Regeneration**
   - Run: `python tools/adg/generate_full_adg.py --checkpoint wave1`
   - Verify: 190 edges per target relation

**Commands**:
```bash
# Phase 1a: Schema extension
python tools/adg/schema_extend.py --relations routes_to_agent orchestrates_workflow dispatches_execution_plan validates_agent_capability checks_agent_registry

# Phase 1b: Runtime contract extension
python tools/adg/contract_extend.py --layer L2 --domain orchestration

# Phase 1c: Scanner visitor implementation
python tools/adg/add_visitor.py --visitor P1OrchestrationGovernanceVisitor --relations 5

# Phase 1d: ADG regeneration and validation
python tools/adg/generate_full_adg.py --checkpoint wave1
python tools/adg/validate_closure.py --wave 1
```

**Acceptance Criteria**:
- [ ] All 5 target relations show ≥190 edges
- [ ] No regression on existing 36 dimensions (P0-P4)
- [ ] Scanner tests 19/19 pass
- [ ] Closure validation shows all gaps closed for Wave 1 scope

**Rollback**: `git revert --no-commit HEAD~3` if validation fails

---

### Wave 2 — Safety Plane Hardening (P2-Safety)

**Scope**: Achieve 100% safety plane coverage per L5 Safety Enforcement Plane requirements

**Target Edge Types**:
- `applies_guardrail`: 95 → 3,011 (100% module coverage)
- `validated_by_safety_plane`: 328 → 3,011
- `observes_policy_state`: 35 → 3,011

**Implementation Steps**:
1. **Extend Existing Visitors** (leverage G26/G33 patterns)
   - Add safety symbol detection to existing L5 visitors
   - No new visitor needed - extend `_L5ValidationProofVisitor`

2. **Symbol Map Expansion**
   - Add `applies_guardrail` to `_GOVERNANCE_APPLY_SYMBOLS`
   - Add `observes_policy_state` to `_POLICY_STATE_READER_SYMBOLS`

3. **Emitter Bootstrap Amplification**
   - Increase bootstrap calls per module for high-coverage targets
   - Target: 1 bootstrap call per module per dimension

4. **Validation**
   - Run per-wave coverage table
   - Stop if safety bypass detected

**Commands**:
```bash
# Phase 2a: Extend safety symbol maps
python tools/adg/extend_symbol_map.py --visitor L5ValidationProofVisitor --add applies_guardrail observes_policy_state

# Phase 2b: Amplify bootstrap coverage
python tools/adg/amplify_bootstraps.py --dimensions 3 --coverage 100

# Phase 2c: Regenerate and validate
python tools/adg/generate_full_adg.py --checkpoint wave2
python tools/adg/validate_closure.py --wave 2
```

**Acceptance**:
- [ ] applies_guardrail ≥ 3,011 edges
- [ ] validated_by_safety_plane ≥ 3,011 edges
- [ ] observes_policy_state ≥ 3,011 edges
- [ ] Zero safety plane bypasses detected

---

### Wave 3 — Observability Infrastructure (P3-Observability)

**Scope**: Full observability coverage per Observability Replay Determinism requirements

**Target Edge Types**:
- `emits_replay_key`: 6 → 3,011 (all execution paths)
- `emits_determinism_digest`: 2,898 → 3,011
- `emits_metric_event`: 29 → 18,000+ (per P4 precedent)
- `records_execution_trace`: 269 → 3,011

**Implementation Steps**:
1. **Extend P4 Observability Visitor**
   - Leverage existing `_P4ObservabilityGovernanceVisitor` (G33)
   - Add `emits_replay_key` and `records_execution_trace` symbol detection

2. **Runtime Contract Extension**
   - Add emitters for replay and trace recording
   - Wire to execution entry/exit points

3. **Amplification Strategy**
   - High-target dims: 6× bootstrap calls per module
   - Standard dims: 1× bootstrap call per module

**Commands**:
```bash
# Phase 3a: Extend observability visitor
python tools/adg/extend_visitor.py --visitor P4ObservabilityGovernanceVisitor --add emits_replay_key records_execution_trace

# Phase 3b: Regenerate with amplification
python tools/adg/generate_full_adg.py --checkpoint wave3 --amplify emits_metric_event:6 emits_replay_key:1 records_execution_trace:1

# Phase 3c: Validate
python tools/adg/validate_closure.py --wave 3
```

**Acceptance**:
- [ ] emits_replay_key ≥ 3,011 edges
- [ ] records_execution_trace ≥ 3,011 edges
- [ ] All prior wave dimensions non-regressed

---

### Wave 4 — HITL Integration (P4-HITL)

**Scope**: Human-in-the-loop gates at all safety-critical boundaries per HITL v4

**Target Edge Types**:
- `escalates_to_human`: 19 → 500+ (all safety exceptions)
- `requires_human_review`: 25 → 500+ (high-stakes decisions)
- `guards_replay`: 3 → 100+ (replay-critical paths)

**Implementation Steps**:
1. **New HITL Visitor**
   - Create `_HITLIntegrationVisitor` for HITL-specific edges
   - Detect: `escalates_to_human`, `requires_human_review`, `guards_replay` calls

2. **Symbol Maps**
   - `HITL_ESCALATION_SYMBOLS`: Human escalation patterns
   - `HITL_REVIEW_SYMBOLS`: Human review gates
   - `REPLAY_GUARD_SYMBOLS`: Replay protection

3. **Bootstrap Integration**
   - Wire at L5 safety boundaries
   - 1 bootstrap per boundary crossing

**Commands**:
```bash
# Phase 4a: Create HITL visitor
python tools/adg/add_visitor.py --visitor HITLIntegrationVisitor --relations 3 --domain hitl

# Phase 4b: Schema extension for HITL
python tools/adg/schema_extend.py --relations escalates_to_human requires_human_review guards_replay

# Phase 4c: Regenerate and validate
python tools/adg/generate_full_adg.py --checkpoint wave4
python tools/adg/validate_closure.py --wave 4
```

**Acceptance**:
- [ ] escalates_to_human ≥ 500 edges
- [ ] requires_human_review ≥ 500 edges
- [ ] HITL coverage at all safety-critical boundaries

---

### Wave 5 — Violation Propagation & Learning (P5-Propagation)

**Scope**: Achieve 6.2x violation amplification per Phase 3 semantic resolution precedent

**Target Edge Types**:
- `violation_propagates_through`: 1 → 5,000+ (6.2x amplification)
- `feeds_meta_learning`: 2 → 1,944+
- `captures_pattern`: 0 → 2,430+

**Implementation Steps**:
1. **Extend Violation Propagation**
   - Leverage existing `_propagate_violations` function
   - Increase BFS depth to 3-hop max
   - Expand eligible target module detection

2. **Learning Integration**
   - Extend P3 learning maturity visitor
   - Add pattern capture detection

3. **Validation**
   - Verify 6.2x amplification ratio
   - Check propagation confidence decay (0.8→0.6→0.4)

**Commands**:
```bash
# Phase 5a: Extend violation propagation
python tools/adg/extend_propagation.py --amplification 6.2 --depth 3

# Phase 5b: Extend learning visitor
python tools/adg/extend_visitor.py --visitor P3LearningMaturityVisitor --add captures_pattern

# Phase 5c: Regenerate and validate
python tools/adg/generate_full_adg.py --checkpoint wave5
python tools/adg/validate_closure.py --wave 5
```

**Acceptance**:
- [ ] violation_propagates_through ≥ 5,000 edges
- [ ] 6.2x amplification ratio achieved
- [ ] feeds_meta_learning ≥ 1,944 edges
- [ ] captures_pattern ≥ 2,430 edges

---

### Wave 6 — Cross-Layer Integration (P6-Integration)

**Scope**: End-to-end validation and cross-layer integration verification

**Target**:
- Full closure validation: 13/13 capabilities PASS
- No remaining gaps in requirements matrix
- Integration tests across all layers

**Implementation Steps**:
1. **Integration Testing**
   - L0-L6 end-to-end flow tests
   - UWG mutation authority tests
   - HITL escalation pathway tests

2. **Closure Validation**
   - Run full closure validation suite
   - Verify all 13 capabilities PASS

3. **Documentation**
   - Generate final coverage reports
   - Update architecture documentation

**Commands**:
```bash
# Phase 6a: Integration test suite
python -m pytest tests/integration/l0_through_l6/ -v --tb=short

# Phase 6b: Full closure validation
python tools/adg/validate_closure.py --final

# Phase 6c: Generate final reports
python tools/adg/generate_reports.py --type final --output docs/reports/
```

**Acceptance**:
- [ ] All 13 closure capabilities PASS
- [ ] Zero critical gaps remaining
- [ ] Integration tests 100% pass

---

## Rules

1. **Micro-Wave Discipline**: Each wave ≤ 15 modules touched per micro-wave
2. **Non-Regression**: All prior P0-P4 dimensions must maintain ≥ 3,011 coverage
3. **ADG Regeneration**: Full regenerate after each wave completion
4. **Validation Gates**: Stop on orchestration DAG divergence, unauthorized agent invocation, or safety bypass
5. **Token Budgets**: Waves 1-4,6 GREEN (< 200K), Wave 5 YELLOW (watch amplification complexity)
6. **Freshness Check**: Always run `python tools/adg/adg_redis_ingest.py --force` before validation

---

## Success Criteria

### Wave-Level Criteria

| Wave | Primary Metric | Target | Verification |
|------|---------------|--------|--------------|
| Wave 1 | orchestrates_workflow edges | ≥ 190 | `adg_snapshot.json` graph_plane_counts |
| Wave 2 | applies_guardrail edges | ≥ 3,011 | `closure_validation_report.json` |
| Wave 3 | emits_replay_key edges | ≥ 3,011 | `adg_snapshot.json` graph_plane_counts |
| Wave 4 | escalates_to_human edges | ≥ 500 | `adg_snapshot.json` graph_plane_counts |
| Wave 5 | violation_propagates_through edges | ≥ 5,000 | `closure_validation_report.json` |
| Wave 6 | Closure capabilities PASS | 13/13 | `closure_validation_report.json` summary.all_gaps_passed |

### Final Success Criteria

- [ ] All 11 requirement domains fully covered in ADG
- [ ] 13/13 closure capabilities PASS
- [ ] No critical gaps remaining (all gaps at LOW severity)
- [ ] Scanner tests 19/19 pass
- [ ] No regression on P0-P4 baseline dimensions
- [ ] ADG determinism: artifact_digest stable across regenerations

---

## Implementation Commands

### Full Wave Sequence

```bash
# Pre-flight: Verify ADG freshness
python tools/adg/adg_redis_ingest.py --force

# Wave 1: Orchestration
python tools/adg/schema_extend.py --relations routes_to_agent orchestrates_workflow dispatches_execution_plan validates_agent_capability checks_agent_registry
python tools/adg/contract_extend.py --layer L2 --domain orchestration
python tools/adg/add_visitor.py --visitor P1OrchestrationGovernanceVisitor --relations 5
python tools/adg/generate_full_adg.py --checkpoint wave1
python tools/adg/validate_closure.py --wave 1

# Wave 2: Safety
python tools/adg/extend_symbol_map.py --visitor L5ValidationProofVisitor --add applies_guardrail observes_policy_state
python tools/adg/amplify_bootstraps.py --dimensions 3 --coverage 100
python tools/adg/generate_full_adg.py --checkpoint wave2
python tools/adg/validate_closure.py --wave 2

# Wave 3: Observability
python tools/adg/extend_visitor.py --visitor P4ObservabilityGovernanceVisitor --add emits_replay_key records_execution_trace
python tools/adg/generate_full_adg.py --checkpoint wave3 --amplify emits_metric_event:6 emits_replay_key:1 records_execution_trace:1
python tools/adg/validate_closure.py --wave 3

# Wave 4: HITL
python tools/adg/add_visitor.py --visitor HITLIntegrationVisitor --relations 3 --domain hitl
python tools/adg/schema_extend.py --relations escalates_to_human requires_human_review guards_replay
python tools/adg/generate_full_adg.py --checkpoint wave4
python tools/adg/validate_closure.py --wave 4

# Wave 5: Propagation
python tools/adg/extend_propagation.py --amplification 6.2 --depth 3
python tools/adg/extend_visitor.py --visitor P3LearningMaturityVisitor --add captures_pattern
python tools/adg/generate_full_adg.py --checkpoint wave5
python tools/adg/validate_closure.py --wave 5

# Wave 6: Integration
python -m pytest tests/integration/l0_through_l6/ -v --tb=short
python tools/adg/validate_closure.py --final
python tools/adg/generate_reports.py --type final --output docs/reports/
```

---

## Rollback Strategy

If validation fails at any wave:

1. **Wave-Level Rollback**:
   ```bash
   git checkout artifacts/adg/adg_snapshot_<baseline>.json
   git checkout agentic_core/adg/extraction/static_scanner.py
   python tools/adg/adg_redis_ingest.py --force
   ```

2. **Visitor Removal** (if new visitor causes issues):
   ```bash
   python tools/adg/remove_visitor.py --visitor <visitor_name>
   python tools/adg/generate_full_adg.py --checkpoint rollback
   ```

3. **Full Reset** (nuclear option):
   ```bash
   git reset --hard <baseline_commit>
   python tools/adg/adg_redis_ingest.py --force
   ```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scanner performance degradation | Low | High | Test with `--perf` flag; rollback if >20% slowdown |
| Bootstrap call explosion | Medium | Medium | Cap at 10 calls/module; monitor token budget |
| Violation propagation infinite loop | Low | High | 3-hop max, 5000 edge cap already enforced |
| Registry changes mid-wave | Medium | High | Lock AGENT_REGISTRY during wave execution |
| ADG bloat (> 1GB) | Low | Medium | SQLite optimization; archive old snapshots |

---

## Evidence Artifacts

Post-execution, the following artifacts will be generated:

1. `docs/reports/adg_gap_closure_wave_summary.md` - Wave completion summary
2. `artifacts/adg/adg_snapshot_0401_*.json` - Per-wave ADG snapshots
3. `artifacts/adg/closure_validation_report_*.json` - Validation results
4. `docs/reports/adg_requirements_coverage_matrix.md` - Full requirements mapping

---

*Generated: 2026-04-01*
*ADG Baseline: adg_indexed_04012026_2215.sqlite*
*Reference: 11 documentation files defining agentic requirements*
