# Evaluation Spine & System Learning Pipeline — Implementation Plan

Bridge documentation-defined gaps in system learning with dependency-first hybrid waves, implementing core pipeline infrastructure before evaluation components.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| Wave 1 | SL-CORE | Case Compilation Engine + Signal Aggregator infrastructure | 185,000 | Core types and engines follow existing case_memory_types.py patterns; ADG hot cache available | GREEN | CaseRecord bundles compile from L2 sealed outputs; SignalAggregator emits deterministic digests |
| Wave 2 | SL-EVAL | Outcome & Trajectory Evaluation engines | 195,000 | Existing offline_healing_outcome_evaluator.py patterns reusable; evaluation types extend case_memory_types | GREEN | OutcomeEvaluationEngine scores task completion/groundedness; TrajectoryEvaluationEngine measures tool selection/order |
| Wave 3 | SL-GAUNTLET | Rule Drafting + Approval Gauntlet | 190,000 | Meta-learning pipeline patterns from meta_learning_pipeline.py reusable; gauntlet approval mirrors existing arbitration | GREEN | RuleDraftingEngine proposes policy updates; ApprovalGauntletEngine validates with COMMANDANT sovereign authority |
| Wave 4 | SL-CONTROL | Live Exit Control + Human Calibration | 175,000 | Exit gate mirrors existing enforcement patterns; calibration extends HITLPreferenceRecord | GREEN | LiveExitControlGate validates env/replay completeness; HumanCalibrationEngine calibrates B/C/D evaluations |

**Total: 745,000 projected tokens across 4 waves, all GREEN**

---

## Gap Register

**GAP-1: Case Compilation Engine (Step 4)**
- Documentation requires: Ingest sealed L2 outputs, build CaseRecord bundles, attach context logs, finalize master archive payload
- Current state: Only `case_memory_types.py` types exist; no compilation engine
- Impact: System Learning Pipeline cannot ingest execution traces into case memory

**GAP-2: Signal Aggregator (Component E)**
- Documentation requires: Score bundling, decisiveness tags, drift flags, confidence/variance, severity classification
- Current state: `signal_grouping_engine.py` exists but incomplete per Evaluation Spine spec
- Impact: BUS P (Preferences/Grades) and BUS T (Telemetry/Trace) cannot aggregate into unified evaluation signals

**GAP-3: Outcome Evaluation Engine (Component B)**
- Documentation requires: Task completion, groundedness, citation support, abstain correctness, escalation correctness, answer relevance
- Current state: `offline_healing_outcome_evaluator.py` exists but only covers healing outcomes, not general execution outcomes
- Impact: Cannot evaluate execution quality per Evaluation Spine metrics

**GAP-4: Trajectory Evaluation Engine (Component C)**
- Documentation requires: Tool selection/order, argument correctness, retry thrashing, budget discipline, policy compliance
- Current state: No dedicated trajectory evaluator exists
- Impact: Cannot evaluate execution path quality per Evaluation Spine metrics

**GAP-5: G-Gate Regression Checker (Component D)**
- Documentation requires: Exact match validation, schema/state checks, trajectory invariance, API drift detection, rubric grading
- Current state: No G-Gate specific checker exists
- Impact: Cannot validate governance gate stability across runs

**GAP-6: Rule Drafting Engine (Step 6)**
- Documentation requires: Derive fix targets, structure improvements, control reverts
- Current state: No rule drafting engine exists
- Impact: Cannot propose policy/config updates from incident investigation

**GAP-7: Approval Gauntlet Engine (Step 7)**
- Documentation requires: Modes/shadow reply validation, gates for regression/safety, COMMANDANT sovereign approval decision
- Current state: Arbitration engine exists but not aligned with COMMANDANT persona pattern
- Impact: Cannot enforce sovereign approval before learning commits

**GAP-8: Live Exit Control Gate (Component A)**
- Documentation requires: Env integrity, schema validation, sandbox isolation, mutation authorization, replay completeness
- Current state: No live exit gate engine exists
- Impact: Cannot validate runtime exit conditions per Evaluation Spine

**GAP-9: Human Calibration Engine (Component F)**
- Documentation requires: SME adjudication, spot checks, grader calibration for B/C/D evaluations
- Current state: HITLPreferenceRecord exists but no calibration engine
- Impact: Cannot calibrate automated evaluators against human judgments

---

## Execution Plan

### Phase 1 — Wave 1: Core Pipeline Infrastructure
**Scope**: Implement Case Compilation Engine and Signal Aggregator as foundation. These components ingest from L2/L6 and feed downstream evaluation.

**Files to create**:
- `system_learning/engines/case_compilation_engine.py` — Compiles L2 sealed outputs into CaseRecord bundles
- `system_learning/types/case_compilation_types.py` — Types for compilation pipeline stages
- `system_learning/engines/signal_aggregator_engine.py` — Aggregates BUS P and BUS T into unified signals

**Files to modify**:
- `system_learning/types/__init__.py` — Export new types
- `system_learning/engines/__init__.py` — Export new engines

**Commands**:
```bash
python -m pytest tests/unit/system_learning/ -k "case_compilation or signal_aggregator" -v
python tools/adg/adg_redis_ingest.py --force
python -c "from system_learning.engines.case_compilation_engine import CaseCompilationEngine; print('Import OK')"
```

**Acceptance**:
- CaseCompilationEngine successfully bundles 5+ test traces into CaseRecord artifacts
- SignalAggregator emits deterministic digests for aggregated signals
- All new files have ADG edges wired (records_execution_trace, applies_guardrail)

---

### Phase 2 — Wave 2: Evaluation Components
**Scope**: Implement Outcome and Trajectory Evaluation engines per Evaluation Spine spec B and C.

**Files to create**:
- `system_learning/engines/outcome_evaluation_engine.py` — Evaluates task completion, groundedness, citations
- `system_learning/engines/trajectory_evaluation_engine.py` — Evaluates tool selection, arg correctness, retry patterns
- `system_learning/types/evaluation_spine_types.py` — Evaluation result types, metric containers
- `system_learning/validators/g_gate_regression_checker.py` — Validates governance gate stability

**Files to modify**:
- `system_learning/types/__init__.py` — Export evaluation types
- `system_learning/engines/__init__.py` — Export evaluation engines

**Commands**:
```bash
python -m pytest tests/unit/system_learning/ -k "outcome or trajectory or g_gate" -v
python -c "from system_learning.engines.outcome_evaluation_engine import OutcomeEvaluationEngine; print('Outcome OK')"
python -c "from system_learning.engines.trajectory_evaluation_engine import TrajectoryEvaluationEngine; print('Trajectory OK')"
```

**Acceptance**:
- OutcomeEvaluationEngine produces scores for all 6 metrics (task_completion, groundedness, citation_support, abstain_correctness, escalation_correctness, answer_relevance)
- TrajectoryEvaluationEngine produces scores for all 5 metrics (tool_selection, arg_correctness, retry_thrashing, budget_discipline, policy_compliance)
- GGateRegressionChecker validates exact match and schema stability

---

### Phase 3 — Wave 3: Rule Drafting & Approval Gauntlet
**Scope**: Implement Step 6 (Rule Drafting) and Step 7 (Approval Gauntlet) of System Learning Pipeline.

**Files to create**:
- `system_learning/engines/rule_drafting_engine.py` — Derives fixes, structures improvements, controls reverts
- `system_learning/engines/approval_gauntlet_engine.py` — COMMANDANT sovereign approval with regression/safety gates
- `system_learning/types/rule_drafting_types.py` — Rule proposal types, change specs

**Files to modify**:
- `system_learning/pipelines/meta_learning_pipeline.py` — Wire new engines at appropriate stages
- `system_learning/types/__init__.py` — Export new types
- `system_learning/engines/__init__.py` — Export new engines

**Commands**:
```bash
python -m pytest tests/unit/system_learning/pipelines/ -v
python -m pytest tests/unit/system_learning/engines/test_rule_drafting.py -v
python -m pytest tests/unit/system_learning/engines/test_approval_gauntlet.py -v
```

**Acceptance**:
- RuleDraftingEngine produces valid RuleProposal artifacts from incident investigations
- ApprovalGauntletEngine enforces COMMANDANT approval with reject/loop logic
- MetaLearningPipeline correctly stages new engines after RCA and before ledger commit

---

### Phase 4 — Wave 4: Exit Control & Human Calibration
**Scope**: Implement Component A (Live Exit Control) and Component F (Human Calibration) of Evaluation Spine.

**Files to create**:
- `system_learning/engines/live_exit_control_gate.py` — Validates env integrity, replay completeness, policy pass/fail
- `system_learning/engines/human_calibration_engine.py` — Calibrates automated evaluators against SME judgments
- `system_learning/types/calibration_types.py` — Calibration record types, preference mappings

**Files to modify**:
- `system_learning/types/__init__.py` — Export calibration types
- `system_learning/engines/__init__.py` — Export new engines

**Commands**:
```bash
python -m pytest tests/unit/system_learning/engines/test_live_exit_control.py -v
python -m pytest tests/unit/system_learning/engines/test_human_calibration.py -v
python -m pytest tests/unit/system_learning/ -k "exit or calibration" -v
```

**Acceptance**:
- LiveExitControlGate allows/denies/escalates based on validation rules
- HumanCalibrationEngine generates calibration drift reports comparing auto-eval to SME
- All Evaluation Spine components A-G have engine implementations

---

## Rules

1. **Follow existing patterns**: Match code style from `case_memory_types.py`, `meta_learning_pipeline.py`, and `offline_healing_outcome_evaluator.py`
2. **ADG wiring mandatory**: Every new engine must emit lifecycle trace contracts (records_execution_trace, applies_guardrail, etc.)
3. **Fail-closed validation**: All gates reject by default; explicit allow conditions required
4. **Deterministic outputs**: All engines produce stable digests via `deterministic_json()` and `stable_sha256_json()`
5. **No wall-clock reads**: All timestamps caller-supplied; no `datetime.now()` in engines
6. **Frozen dataclasses**: All types use `@dataclass(frozen=True)` with canonical `to_dict()`/`to_json()` methods

---

## Success Criteria

- [ ] CaseCompilationEngine ingests L2 sealed outputs and emits CaseRecord bundles
- [ ] SignalAggregatorEngine aggregates BUS P and BUS T into unified evaluation signals
- [ ] OutcomeEvaluationEngine scores all 6 Evaluation Spine outcome metrics
- [ ] TrajectoryEvaluationEngine scores all 5 Evaluation Spine trajectory metrics
- [ ] GGateRegressionChecker validates exact match and schema/state stability
- [ ] RuleDraftingEngine proposes structured policy updates from incidents
- [ ] ApprovalGauntletEngine enforces COMMANDANT sovereign approval
- [ ] LiveExitControlGate validates runtime exit conditions
- [ ] HumanCalibrationEngine calibrates evaluators against SME judgments
- [ ] All engines have ADG edges and pass type checking

---

## Implementation Commands

```bash
# Verify ADG cache is hot before starting
python tools/adg/adg_redis_ingest.py --status

# After each wave, refresh ADG and validate no layer inversions
python tools/adg/adg_redis_ingest.py --force
python tools/adg/accelerators/adg_structure_validator.py

# Run targeted tests after each wave
python -m pytest tests/unit/system_learning/ -v --tb=short

# Full integration verification after all waves
python -m pytest tests/unit/system_learning/ tests/integration/system_learning/ -v
```

---

## Rollback Strategy

1. **Wave-level rollback**: If a wave introduces regressions, revert only that wave's files:
   ```bash
   git restore --source=HEAD --worktree --staged system_learning/engines/case_compilation_engine.py
   git restore --source=HEAD --worktree --staged system_learning/types/case_compilation_types.py
   ```

2. **Pipeline wiring rollback**: If meta_learning_pipeline.py integration fails:
   ```bash
   git checkout system_learning/pipelines/meta_learning_pipeline.py
   ```

3. **ADG recovery**: If ADG edges are incorrect after a wave:
   ```bash
   python tools/adg/generate_full_adg.py
   python tools/adg/adg_redis_ingest.py --force
   ```

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| New engines implemented | 8 | `ls system_learning/engines/*.py | wc -l` shows count increase |
| Documentation gaps closed | 9/9 | All GAP-1 through GAP-9 have engine implementations |
| ADG edge coverage | 100% | All new engines have records_execution_trace edges |
| Test coverage | ≥80% | `pytest --cov=system_learning` shows coverage |
| Determinism verified | Yes | All engines produce stable digests across runs |
| Import success | Yes | `python -c "from system_learning.engines import *"` succeeds |

---

## SSOT References

- **Documentation**: `docs/reference/System Learning/Evaluation Spine & Post-Execution.md`
- **Documentation**: `docs/reference/System Learning/System Learning Pipeline v4.md`
- **Existing patterns**: `system_learning/types/case_memory_types.py`
- **Existing patterns**: `system_learning/pipelines/meta_learning_pipeline.py`
- **Existing patterns**: `system_learning/engines/offline_healing_outcome_evaluator.py`
- **Plan location**: `docs/reports/plans/evaluation-spine-implementation-plan-1d1fbe.md`

---

*Plan generated per .windsurf/templates/execution-plan-template.md and plan_ci_enforcement.md §10.1/§10.2*
