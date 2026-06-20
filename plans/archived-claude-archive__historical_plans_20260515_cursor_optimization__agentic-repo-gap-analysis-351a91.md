---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\agentic-repo-gap-analysis-351a91.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\agentic-repo-gap-analysis-351a91.md'
source_sha256: 2b75a9b369fe4cd5f6baa12fc5665cb96444c7963c2663ef05a5852ad5e4172c
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Agentic Repository Gap Analysis & Implementation Plan

## Executive Summary

Comprehensive analysis of 8 reference documentation files against current ADG (138,670 nodes, 692,842 edges) reveals significant gaps in Shadow Evaluation System Learning (Stage 6) implementation. This plan outlines prioritized remediation steps across wiring, integration, dependencies, and feedback loops without immediate code changes.

---

## 1. REQUIREMENTS ANALYSIS (from 8 Reference Documents)

### 1.1 Process Map Stages

| Stage | Document | Core Function | Key Components |
|-------|----------|---------------|----------------|
| X0 | 01_request_intake.md | Request Ingest & Validation | X0A-X0D: Ingest, Pre-flight, BOM Assembly |
| X1 | 02_L1_Reasoning_Plan_Generation.md | L1 Cognition & Planning | X1A-X1D: Decomposition, Strategy, Capability |
| X2 | 03_Route_Decision_Switching.md | Route Arbitration | X2A-X2D: Arbitration, Escalation, Dispatch |
| X3 | 04_Live_Task_Dispatch_Execution.md | Live Execution | X3A-X3D: Tool Auth, UWG Commit, Response |
| X4 | 05_Live_Runtime_Exit_Control.md | Exit Control | X4A-X4D: Outcome routing, Author-Gate Airlock |
| S1-S6 | 06_Shadow_Evaluation_System_Learning.md | After-Hours Review | S1-S6: Observability → Async Eval → RCA → Draft → Approve → Promote |

### 1.2 Shadow Evaluation Requirements (S1-S6)

**S1 Observability (Watching the Tapes)**
- S1A: Gather logs (telemetry intake, exit outcomes, trace capture)
- S1B: Normalize evidence (align formats, preserve lineage, correlate dispositions)
- S1C: Review bundle (seal async eval packet, no live mutation, future-run only)
- S1D: Strict observer rule (evidence only, no patron impact, reads only)

**S2 Async Evaluation (Grading the Staff)**
- S2A: Outcome evals (task completion, groundedness, citation support, abstain correctness, escalation correctness, answer relevance)
- S2B: Trajectory evals (tool selection/ordering, arg correctness, retry thrash/budget, policy compliance, trajectory integrity)
- S2C: Governance regressions (exact match drift, schema/state drift, API drift, rubric/grader drift, gate regression)
- S2D: Human calibration (SME adjudication, spot checks, grader calibration)

**S3 Signal Aggregation (Finding Patterns)**
- S3A: Score bundle (qualitative/quantitative metrics, unified score packet)
- S3B: Decision tags (drift flags, confidence variance, severity class)
- S3C: Baseline tagging (baseline IDs, data-source tags, comparison anchors)
- S3D: Clustering (repeated failure isolate, separate noise, candidate patterns)

**S4 Root Cause Analysis**
- S4A: RCA trigger (signal-to-defect linkage)
- S4B: Fault localization (symbol-level fault isolation via ADG)
- S4C: Impact blast radius (downstream/upstream scope via ADG fan-out/fan-in)
- S4D: Repair classification (type tagging, confidence scoring, effort estimation)

**S5 Change Drafting**
- S5A: Candidate change generation (symbol-level diff proposals)
- S5B: Policy compatibility check (against active policy hash)
- S5C: Risk scoring (blast radius + confidence → risk class)
- S5D: Change packet assembly (immutable proposal record)

**S6 Change Promotion**
- S6A: Proposal queue (priority-ordered change packets)
- S6B: Approval gauntlet (multi-factor approval with materialization)
- S6C: UWG commit (sole write path via UniversalWriteGateway)
- S6D: Read surface refresh (alias swap, audit sync)

### 1.3 Cross-Cutting Buses

- **BUS P (Preferences/Grades)**: Evaluation → Meta-learning signals
- **BUS T (Telemetry/Replay Evidence)**: Deterministic replay data for shadow evaluation

---

## 2. ADG ANALYSIS FINDINGS

### 2.1 Current ADG State (04042026_2145_probe)

```
Nodes: 138,670
Edges: 692,842
SQLite: artifacts/adg/adg_indexed_04042026_2145_probe.sqlite
Status: Healthy (SQLite + Redis cache)
```

### 2.2 Layer Violations (50+ Found)

**Critical Layer Boundary Violations:**
- L0→L2: 15 violations (execution_gateway.py, agentic_router.py, path_router.py)
- L0→L5: 8 violations (mutation_prohibition.py, routing_contract.py)
- L0→L_RUNTIME: 6 violations (boot_sequence.py, execution_orchestrator.py)
- L0→L4: 4 violations (assembly_stage.py, timeshift_router.py)
- L1→L2: 2 violations (execution_status.py, cognitive_engine.py)

**Sample Violations:**
```
agentic_core/L0_routing/enforcement/execution_gateway.py:179 → L0->L2
agentic_core/L0_routing/engines/agentic_router.py:174 → L0->L2
agentic_core/L0_routing/enforcement/mutation_prohibition.py:318 → L0->L2
```

### 2.3 Semantic Edge Coverage Gaps

**P0 Governance ( records_execution_trace )**
- Expected: 100% module coverage
- Current: ~115 modules (denominator) vs partial numerator coverage
- Gap: Missing trace coverage in apps_* tier

**P1 Orchestration (6 edge types)**
- routes_to_agent, orchestrates_workflow, dispatches_execution_plan
- validates_agent_capability, checks_agent_registry, execution_terminates_at_uwg
- Current: Partial coverage, missing apps_* wiring

**P2 Execution (6 edge types)**
- authorize_and_execute, validates_capability, routes_to_capability
- writes_via_uwg, blocks_direct_write, records_tool_invocation
- Current: Core wired, apps_* incomplete

**P3 Learning Maturity (7 edge types)**
- captures_pattern, records_learning_event, writes_learning_snapshot
- feeds_meta_learning, updates_routing_strategy, improves_agent_policy, stores_learning_state
- Current: ~3,011 modules wired but apps_* integration incomplete

**P4 Observability (7 edge types)**
- emits_metric_event, records_incident_event, captures_runtime_anomaly
- writes_observability_log, updates_monitoring_state, triggers_alert, links_incident_trace
- Current: Partial; missing S1-S6 shadow evaluation wiring

### 2.4 Missing ADG Edge Types (Requirements vs Implementation)

| Requirement Edge | Status | Location Needed |
|-----------------|--------|-----------------|
| evaluation_feeds_learning | ⚠️ PARTIAL | evaluation_learning_bridge.py exists, wiring incomplete |
| shadow_observes_production | ❌ MISSING | S1 observability visitor needed |
| async_evaluates_outcome | ⚠️ PARTIAL | shadow_evaluator.py exists, no visitor |
| signal_aggregates_pattern | ⚠️ PARTIAL | signal_aggregator_engine.py partial |
| rca_localizes_fault | ❌ MISSING | S4 ADG-based fault localization needed |
| draft_proposes_change | ❌ MISSING | S5 change drafting not implemented |
| approver_commits_via_uwg | ⚠️ PARTIAL | UWG exists, approval gauntlet incomplete |

---

## 3. GAP ANALYSIS BY REQUIREMENT AREA

### 3.1 Wiring Gaps

**GAP-W1: Shadow Evaluation S1-S6 Wiring Missing**
- No S1A-S1D observability pipeline wiring
- No S2A-S2D evaluation stage instrumentation
- No S3A-S3D signal aggregation wiring
- Missing BUS P (Preferences) full wiring
- Missing BUS T (Telemetry) full wiring

**GAP-W2: apps_* Tier ADG Wiring Incomplete**
- apps_eval: Partial (base_eval_engine has Qwen, missing trace contracts)
- apps_exec: Partial (base_exec_engine missing full P0-P4 wiring)
- apps_lic: Incomplete (control_plane missing trace contracts)
- apps_rg: Partial (missing evaluation_learning_bridge integration)
- apps_research, apps_rfp, apps_underwriting_ai: Not analyzed (likely incomplete)

**GAP-W3: Cross-Layer Integration Wiring**
- L0→L2 violations need remediation or shims
- L6_observability→system_learning bus incomplete
- EvaluationLearningBridge→meta_learning_pipeline wiring partial

### 3.2 Integration Gaps

**GAP-I1: Shadow Evaluation Integration Missing**
- No S1→S2→S3→S4→S5→S6 stage integration
- Missing shadow_drift_analyzer→meta_learning_pipeline integration
- Missing shadow_replay_validator→evaluation_learning_bridge integration
- No async_eval packet materialization

**GAP-I2: Author-Gate Airlock Integration Incomplete**
- X3B Author-Gate Secure Reading Room exists in docs
- Implementation: Author-Gate visitor exists but integration gaps remain
- Missing: Materialization packet → L5 re-clearance → Restart wiring

**GAP-I3: UWG Integration Gaps**
- UniversalWriteGateway exists (L2_execution/enforcement/)
- Missing: UWG commit path from S6 approval gauntlet
- Missing: Rollback/heal on failure wiring
- Missing: Read surface refresh/alias swap wiring

### 3.3 Dependency Gaps

**GAP-D1: BUS P Dependencies**
- evaluation_learning_bridge.py exists
- Missing: Path D Preference Embedder full integration
- Missing: BUS P signal routing to meta_learning_bus

**GAP-D2: BUS T Dependencies**
- Telemetry bus partially exists in L6_observability
- Missing: Full shadow telemetry capture (S1A)
- Missing: Replay evidence packaging for shadow runs

**GAP-D3: Cross-Repo Learning Dependencies**
- cross_repo_system_learning_import.py exists
- Missing: Integration with S4 RCA fault localization
- Missing: Cross-repo signal aggregation

### 3.4 Functionality Gaps

**GAP-F1: S1 Observability Functionality**
- S1A gather logs: Partial (telemetry exists, shadow mode missing)
- S1B normalize evidence: Missing
- S1C review bundle: Missing
- S1D strict observer: Missing (no patron impact rule)

**GAP-F2: S2 Async Evaluation Functionality**
- S2A outcome evals: Partial (evaluation_retrieval_engine exists)
- S2B trajectory evals: Missing
- S2C governance regressions: Missing
- S2D human calibration: Missing

**GAP-F3: S3-S6 Functionality Missing**
- S3 signal aggregation: Partial (signal_aggregator_engine stub)
- S4 RCA: Partial (shadow_drift_analyzer exists, fault localization missing)
- S5 change drafting: Missing
- S6 promotion: Partial (approval_gauntlet_engine exists, UWG commit missing)

### 3.5 Feedback Loop Gaps

**GAP-FB1: Evaluation → Learning Loop**
- Partial: evaluation_learning_bridge feeds to system_learning
- Missing: Closed-loop from shadow evaluation outcomes to routing policy updates
- Missing: Preference signal aggregation (BUS P)

**GAP-FB2: RCA → Change Drafting Loop**
- Missing: S4 fault localization → S5 change generation
- Missing: Blast radius analysis → risk scoring

**GAP-FB3: Approval → Deployment Loop**
- Missing: S6 approval → UWG commit → Read surface refresh
- Missing: Rollback on failure loop

### 3.6 System Learning Gaps

**GAP-SL1: Meta-Learning Pipeline Integration**
- meta_learning_pipeline.py exists with W4-A through W4-D stages
- Missing: W4-E (RetrievalProfileProposalManager) full integration
- Missing: Shadow evaluation outcomes as pipeline inputs

**GAP-SL2: Learning State Storage**
- stores_learning_state symbols exist
- Missing: S3-S6 derived learning state persistence

**GAP-SL3: Policy Recommendation Integration**
- policy_recommendation_engine.py exists
- Missing: Integration with S6 approval gauntlet
- Missing: Policy → Routing strategy update loop

---

## 4. IMPLEMENTATION PLAN (No Code Changes)

### Phase 1: Foundation Remediation (Weeks 1-2)

**P1.1: Layer Violation Analysis**
```
Priority: HIGH
Files: 50+ violation sources in ADG
Action: Categorize violations into:
  - Legitimate shims (require exemption annotation)
  - Accidental imports (require remediation)
  - Missing intermediate layers (require new modules)
Deliverable: Violation taxonomy report with remediation map
```

**P1.2: ADG Semantic Edge Verification**
```
Priority: HIGH
Current: Semantic edge queries return empty
Action: 
  - Verify _SEMANTIC_TYPE_MAP in static_scanner.py
  - Check visitor registration for P0-P4 edge types
  - Validate frozenset symbols match actual emitters
Deliverable: ADG semantic coverage report
```

**P1.3: apps_* Tier Inventory**
```
Priority: HIGH
Scope: apps_eval, apps_exec, apps_lic, apps_rg, apps_research, apps_rfp, apps_underwriting_ai
Action:
  - Document current wiring status per app
  - Identify missing P0-P4 trace contracts
  - Map integration points to system_learning
Deliverable: apps_* wiring status matrix
```

### Phase 2: Shadow Evaluation Infrastructure (Weeks 3-4)

**P2.1: S1 Observability Design**
```
Priority: HIGH
Components: S1A Gather, S1B Normalize, S1C Review, S1D Observer Rule
Action:
  - Design telemetry intake pipeline for shadow mode
  - Define evidence normalization schema
  - Specify async eval packet structure
  - Document observer rule enforcement
Deliverable: S1 Observability Specification Document
```

**P2.2: S2 Evaluation Engine Design**
```
Priority: HIGH
Components: S2A Outcome, S2B Trajectory, S2C Regression, S2D Calibration
Action:
  - Design outcome evaluation rubrics
  - Define trajectory scoring metrics
  - Specify governance regression detection
  - Document human calibration workflow
Deliverable: S2 Evaluation Engine Specification
```

**P2.3: BUS P/T Architecture**
```
Priority: MEDIUM
Components: BUS P (Preferences), BUS T (Telemetry)
Action:
  - Design BUS P message schema (preference signals)
  - Design BUS T message schema (telemetry/replay)
  - Specify bus routing topology
  - Document fail-open behavior
Deliverable: BUS P/T Architecture Document
```

### Phase 3: Integration Design (Weeks 5-6)

**P3.1: S3-S6 Pipeline Design**
```
Priority: MEDIUM
Components: S3 Aggregation, S4 RCA, S5 Drafting, S6 Promotion
Action:
  - Design signal aggregation algorithms
  - Specify ADG-based fault localization (S4B)
  - Define change drafting workflow (S5)
  - Document approval gauntlet → UWG commit flow (S6)
Deliverable: S3-S6 Pipeline Architecture Document
```

**P3.2: Author-Gate Integration Design**
```
Priority: MEDIUM
Components: H1 Freeze, H2 Materialize, H3 Review, H4 Decision, Re-clearance
Action:
  - Design Author-Gate airlock state machine
  - Specify materialization packet format
  - Document human review UI requirements
  - Define L5 re-clearance protocol
Deliverable: Author-Gate Integration Specification
```

**P3.3: UWG Commit Flow Design**
```
Priority: MEDIUM
Components: U1 Verify, U2 Check, U3 Commit
Action:
  - Design mutation authority verification
  - Specify catalog rules checking
  - Document durable commit protocol
  - Define rollback/heal procedures
Deliverable: UWG Commit Flow Specification
```

### Phase 4: Testing & Validation Design (Weeks 7-8)

**P4.1: Shadow Evaluation Test Strategy**
```
Priority: MEDIUM
Action:
  - Design shadow mode test fixtures
  - Specify determinism validation approach
  - Document replay verification methods
  - Define regression threshold testing
Deliverable: Shadow Evaluation Test Plan
```

**P4.2: Integration Test Design**
```
Priority: LOW
Action:
  - Design S1→S6 end-to-end integration tests
  - Specify BUS P/T message flow tests
  - Document Author-Gate workflow tests
  - Define UWG commit integration tests
Deliverable: Integration Test Specification
```

**P4.3: ADG Coverage Validation**
```
Priority: LOW
Action:
  - Design semantic edge coverage tests
  - Specify layer violation detection tests
  - Document governance edge validation
Deliverable: ADG Coverage Validation Plan
```

---

## 5. DEPENDENCY MAP

### 5.1 Blockers

1. **ADG Generation Path Issue**: `tools/generate/generate_full_adg.py` has path errors
   - Impact: Cannot generate fresh ADG for validation
   - Resolution: Fix path resolution in generate_full_adg.py

2. **Layer Violation Remediation**: 50+ violations require categorization
   - Impact: Architecture integrity
   - Resolution: Complete P1.1 violation taxonomy

3. **Semantic Edge Detection**: Queries return empty for semantic types
   - Impact: Cannot verify P0-P4 coverage
   - Resolution: Complete P1.2 semantic edge verification

### 5.2 Critical Path

```
P1.1 (Violation Analysis) 
    → P1.2 (Semantic Edge Verification)
        → P1.3 (apps_* Inventory)
            → P2.1 (S1 Design)
                → P2.2 (S2 Design)
                    → P2.3 (BUS P/T Design)
                        → P3.1 (S3-S6 Pipeline)
                            → P3.2 (Author-Gate Integration)
                                → P3.3 (UWG Flow)
                                    → P4.1-P4.3 (Test Design)
```

### 5.3 Parallel Workstreams

- **Stream A**: P1.1 + P1.2 + P1.3 (Foundation)
- **Stream B**: P2.1 + P2.2 (S1-S2 Design)
- **Stream C**: P2.3 + P3.2 + P3.3 (Buses + Author-Gate + UWG)
- **Stream D**: P3.1 + P4.1-P4.3 (Pipeline + Tests)

---

## 6. ARTIFACTS & EVIDENCE

### 6.1 Reference Documents Analyzed

1. `docs/reference/01_request_intake.md` - X0 Stage Requirements
2. `docs/reference/Layer 1 - Reasoning/02_L1_Reasoning_Plan_Generation.md` - X1 Stage Requirements
3. `docs/reference/03_Route_Decision_Switching.md` - X2 Stage Requirements
4. `docs/reference/04_Live_Task_Dispatch_Execution.md` - X3 Stage Requirements
5. `docs/reference/05_Live_Runtime_Exit_Control.md` - X4 Stage Requirements
6. `docs/reference/06_Shadow_Evaluation_System_Learning.md` - S1-S6 Requirements
7. `docs/reference/_notes/agentic_system_process_map_exec.md` - Execution Mapping
8. `docs/reference/agentic_process_mapping_v29.md` - Process Mapping v29

### 6.2 ADG Evidence

- **SQLite Path**: `artifacts/adg/adg_indexed_04042026_2145_probe.sqlite`
- **Node Count**: 138,670
- **Edge Count**: 692,842
- **Violations**: 50+ layer boundary violations catalogued
- **Status**: Healthy (SQLite + Redis cache operational)

### 6.3 Implementation Files Examined

**Core Infrastructure:**
- `agentic_core/runtime/lifecycle_trace_contract.py` - P0-P4 trace contracts
- `agentic_core/L2_execution/enforcement/UniversalWriteGateway.py` - UWG implementation
- `agentic_core/adg/extraction/static_scanner.py` - ADG scanner with visitors

**Shadow Evaluation:**
- `system_learning/engines/shadow_drift_analyzer.py` - W4-C drift analysis
- `system_learning/validators/shadow_evaluator.py` - Shadow regression validator
- `system_learning/pipelines/meta_learning_pipeline.py` - Meta-learning orchestrator

**Evaluation Bridge:**
- `agentic_core/L6_observability/evaluation/evaluation_learning_bridge.py` - BUS P implementation

**Apps Tier:**
- `apps_eval/engines/base_eval_engine.py` - Eval engine with Qwen integration
- `apps_exec/engines/base_exec_engine.py` - Exec engine base
- `apps_lic/engines/control_plane.py` - LIC control plane

---

## 7. RISK ASSESSMENT

### 7.1 High Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| ADG generation path issues block validation | Cannot verify changes | Fix paths in P0 |
| Layer violations indicate architectural drift | System integrity | Complete P1.1 analysis |
| Shadow evaluation S1-S6 largely unimplemented | Future-run learning gap | Phased design approach |

### 7.2 Medium Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| BUS P/T design complexity | Integration delays | Early design (P2.3) |
| Author-Gate airlock workflow | Human-in-the-loop delays | Specification-driven (P3.2) |
| UWG commit flow | Write authority issues | Protocol design (P3.3) |

### 7.3 Low Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| apps_* wiring variations | Inconsistent coverage | Inventory (P1.3) + standardization |
| Test design complexity | Coverage gaps | Specification-first (P4) |

---

## 8. SUCCESS CRITERIA

### 8.1 Phase Completion Criteria

**Phase 1 (Foundation)**
- [ ] Violation taxonomy report with categorized 50+ violations
- [ ] ADG semantic coverage report with root cause analysis
- [ ] apps_* wiring status matrix (all 7 apps documented)

**Phase 2 (Shadow Evaluation)**
- [ ] S1 Observability Specification Document approved
- [ ] S2 Evaluation Engine Specification approved
- [ ] BUS P/T Architecture Document approved

**Phase 3 (Integration)**
- [ ] S3-S6 Pipeline Architecture Document approved
- [ ] Author-Gate Integration Specification approved
- [ ] UWG Commit Flow Specification approved

**Phase 4 (Testing)**
- [ ] Shadow Evaluation Test Plan approved
- [ ] Integration Test Specification approved
- [ ] ADG Coverage Validation Plan approved

### 8.2 Overall Success

- All 8 phases complete with approved design documents
- Clear remediation path for all identified gaps
- No code changes required (planning-only deliverables)
- Ready for implementation phase with clear specifications

---

## 9. APPENDIX: ADG QUERY RESULTS

### 9.1 Violation Sample (First 10)

```json
[
  {"id": 1940, "source_file": "agentic_core/L0_routing/context/c0_guard.py", "symbol": "L0->L5", "line_no": 108},
  {"id": 2438, "source_file": "agentic_core/L0_routing/enforcement/boot_sequence.py", "symbol": "L0->L_RUNTIME", "line_no": 66},
  {"id": 3370, "source_file": "agentic_core/L0_routing/enforcement/execution_gateway.py", "symbol": "L0->L2", "line_no": 179},
  {"id": 3371, "source_file": "agentic_core/L0_routing/enforcement/execution_gateway.py", "symbol": "L0->L5", "line_no": 80},
  {"id": 3806, "source_file": "agentic_core/L0_routing/enforcement/mutation_prohibition.py", "symbol": "L0->L2", "line_no": 318},
  {"id": 4559, "source_file": "agentic_core/L0_routing/enforcement/routing_contract.py", "symbol": "L0->L_RUNTIME", "line_no": 523},
  {"id": 5792, "source_file": "agentic_core/L0_routing/engines/agentic_router.py", "symbol": "L0->L2", "line_no": 174},
  {"id": 5793, "source_file": "agentic_core/L0_routing/engines/agentic_router.py", "symbol": "L0->L6", "line_no": 143},
  {"id": 5794, "source_file": "agentic_core/L0_routing/engines/agentic_router.py", "symbol": "L0->L_RUNTIME", "line_no": 309},
  {"id": 5991, "source_file": "agentic_core/L0_routing/engines/assembly_stage.py", "symbol": "L0->L4", "line_no": 334}
]
```

### 9.2 Semantic Edge Query Results

| Edge Type | Query Result | Status |
|-----------|--------------|--------|
| feeds_meta_learning | 0 edges | ⚠️ MISSING |
| records_execution_trace | 0 edges | ⚠️ MISSING |
| writes_via_uwg | 0 edges | ⚠️ MISSING |
| applies_guardrail | 0 edges | ⚠️ MISSING |

**Analysis**: Semantic edge queries return empty despite P0-P4 micro-wave hardening claiming 3,011 modules wired. This indicates either:
1. ADG SQLite schema issue with semantic type indexing
2. Query method mismatch (Redis vs SQLite)
3. Edge type naming mismatch

**Recommendation**: Verify in P1.2

---

*Document generated: 2026-04-05*
*ADG Reference: adg_indexed_04042026_2145_probe.sqlite*
*Analysis Scope: 8 reference documents, 138,670 ADG nodes, 692,842 edges*
