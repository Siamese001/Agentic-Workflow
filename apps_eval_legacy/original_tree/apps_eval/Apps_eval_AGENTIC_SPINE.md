# apps_eval Agentic Spine

> Evaluation Lab — benchmarks `agentic_core` and application workloads against deterministic scenarios.
> Produces weighted scorecards, regression detection, and audit-grade certification reports.
> **Read-only harness** — no side-effect actions; evaluation artifacts only.

```
USER (CLI: python -m apps_eval --suites <suite_id> ...)
 │
 v
U0 INTAKE
 │  raw input capture, arg parse, suite binding
 │  validate suite configuration exists and is active
 │  bind request envelope (suite_id, scenario_filter, baseline_mode, out_dir)
 │
 v
L1 PLAN
 │  parse evaluation intent from suite metadata
 │  define target module + scenario selection criteria
 │  create EvalRun spec (suite_id, dimensions, threshold_profile)
 │  grounding_required = false (preloaded scenarios, no C0 retrieval)
 │  emit L1PlanContract
 │
 v
L0 ROUTE DECISION
 │
 ├── R1A EXACT_CACHE?
 │     hit ──► [RET] sealed scorecard ref → Exit X3D_ALLOW_FINISH
 │     (SHA256 of suite_id + scenario_filter + policy_hash + schema_version)
 │
 ├── R1B SEMANTIC_CACHE?
 │     hit ──► [RET] cached scorecard chunks + lineage → Exit X3D_ALLOW_FINISH
 │     (compatibility key: suite_id, scenario_count, dimension_weights_hash,
 │      threshold_profile_hash, policy_hash, freshness_class)
 │
 ├── R5 PRE_ROUTE_FALLBACK?
 │     selected ──► [RET] sealed degradation packet → Exit X3E_SAFE_ABSTAIN
 │     (suite_id missing / no scenarios match filter / policy invalid)
 │
 └── R4_SINGLE_ACTION ────────────────────────────────────────────────┐
                                                                     │
L2 BOUNDED EXECUTION PACKET                                          │
 │                                                                   │
 ├── E1 PREP                                                        │
 │   • Load suite configuration from eval_policies.yaml              │
 │   • Load scenario definitions from evaluation_prompts.json        │
 │   • Compute content hashes (policy, scenarios, thresholds)        │
 │   • Freeze run directory (artifacts/apps_eval/runs/<ts>/)       │
 │   • Bind judge model lane (Qwen default / external sanity)      │
 │   • Create replay_key + idempotency_key                           │
 │   • Initialize scorecard shell with dimension weights             │
 │                                                                   │
 ├── E2 VALID                                                       │
 │   • Validate scenario JSON schema                                  │
 │   • Validate threshold profile exists and has dimensions        │
 │   • Validate judge model availability (Qwen heartbeat)           │
 │   • Validate output paths writable                               │
 │   • Validate baseline exists (if regression mode enabled)        │
 │   • Validate cache compatibility rules                            │
 │                                                                   │
 ├── E3 EXEC (scenario loop within L2)                              │
 │   • ScenarioRunner loop over filtered scenarios                  │
 │     - Load scenario payload + expected assertions                │
 │     - Execute target app via execution_adapter (sandboxed)      │
 │     - Capture output + metadata                                   │
 │   • BaseEvalEngine.evaluate() per scenario                      │
 │     - Dimension scoring: correctness, determinism, governance    │
 │     - LLM-as-judge via evaluate_with_qwen (configurable)        │
 │     - Emit per-scenario dim_scores + verdict                     │
 │   • ScorecardEngine.aggregate()                                  │
 │     - Weighted dimension rollup                                   │
 │     - Pass/fail threshold application                             │
 │   • RegressionDetector.compare() (if baseline mode)              │
 │     - Delta detection vs. stored baseline                         │
 │     - REGRESSION verdict if drop > threshold                      │
 │                                                                   │
 │   Execution failure paths:                                        │
 │   • Scenario load failed ──► sealed_failure_packet               │
 │   • Target app execution failed ──► sealed_failure_packet        │
 │   • Judge unavailable ──► sealed_degraded_packet (dim skip)      │
 │   • Scorecard aggregation error ──► sealed_failure_packet          │
 │   (All sealed packets flow to E5, NOT directly to Exit X3)        │
 │                                                                   │
 ├── E4 HEAL (same-authority local repair only)                     │
 │   • Retry scenario on transient target app failure                 │
 │   • Retry JSON/schema formatting fixes                            │
 │   • Skip LLM-judge dimensions if judge degraded                  │
 │   • NOT allowed: scenario mutation, baseline rewrite, L4 write     │
 │                                                                   │
 └── E5 SEAL                                                        │
     • Seal eval_report_<trace_id>.md (full markdown report)         │
     • Seal scorecard_<trace_id>.csv (machine-readable scores)       │
     • Seal eval_manifest_<trace_id>.json (lightweight manifest)    │
     • Seal run_summary_<trace_id>.json (provenance + gate results) │
     • terminal_class: SUCCESS | DEGRADED_SUCCESS | FAILURE         │
     • Optional cache_commit_candidate (inert until Exit)            │
                                                                     │
EXIT                                                                │
 │  X1 checkout checks (provenance, schema, scorecard integrity)  │
 │  X2 aggregation (gate_violations + terminal_class)               │
 │  Exactly one X3 disposition:                                      │
 │    X3A_DENY_REROUTE — hard failure, no usable scorecard         │
 │    X3C_COMMIT_REQUEST_TO_UWG — cache commit only (if enabled)    │
 │    X3D_ALLOW_FINISH — success or degraded success                │
 │    X3E_SAFE_ABSTAIN — suite missing, judge down, etc.             │
 │    (X3B_ESCALATE_HITL not used — no runtime HITL in eval)       │
 │                                                                   │
 ├── Optional CommitRequest → UWG → L4 (cache commit only)          │
 │                                                                   │
 └── L6 (after run completion only — evaluation + future-run learning)
```

## Spine Characteristics

| Property | Value |
|----------|-------|
| **Route Type** | `R4_SINGLE_ACTION` (see `config/route_registry.yaml`) |
| **Execution Form** | `DETERMINISTIC_PIPELINE` (scenario loop, no async/resume) |
| **L3 DAG Path** | `BYPASSED` — no orchestration graph (execution within L2 E3) |
| **C0 Grounding** | `False` (preloaded scenario definitions, no vector retrieval) |
| **Prompt Assembly** | `CANONICAL_PA` for judge prompts (CompiledPromptArtifact with fenced assertions) |
| **Runtime Authority** | `FILESYSTEM_SANDBOX_READ` + `MODEL_EGRESS` (judge calls only) |
| **HITL Posture** | `False` (no runtime HITL; evaluation is deterministic/automated) |
| **Cache Strategy** | R1A exact + R1B semantic (cache commit via Exit → UWG only) |

## Benchmark Suites

The `ScenarioRunner` executes configured suites against target modules:

| Suite ID | Target Module | Scenarios | Dimensions |
|----------|---------------|-----------|------------|
| `routing_enforcement` | L0 routing enforcement | 3 | correctness, determinism, governance |
| `determinism_contracts` | L5 static analysis | 3 | determinism, governance |
| `orchestration_hop` | apps_rg orchestration | 3 | correctness, latency_sla |
| `output_contracts` | agentic_core execution | 2 | correctness, output_richness |
| `exec_brief_generation` | apps_exec ExecOrchestrator | 3 | correctness, governance |

## Scorecard Dimensions

| Dimension | Weight | Pass Threshold | Grader |
|-----------|--------|----------------|--------|
| **Correctness** | 3.0 | 80% | deterministic + LLM judge |
| **Determinism** | 3.0 | 90% | deterministic (hash compare) |
| **Governance** | 2.5 | 75% | deterministic + LLM judge |
| **Latency SLA** | 1.5 | 70% | deterministic (timing) |
| **Output Richness** | 1.0 | 65% | LLM judge |

## Route and Cache Strategy

| Route | Key / Condition | Hit Behavior |
|-------|-----------------|--------------|
| **R1A Exact** | SHA256(suite_id + scenario_filter + policy_hash + schema_version) | Sealed scorecard ref → Exit X3D |
| **R1B Semantic** | Compatibility key: suite_id, scenario_count, dimension_weights_hash, threshold_profile_hash, policy_hash, freshness_class | Cached scorecard + lineage → Exit X3D |
| **R5 Suite Gate** | Suite existence + scenario count > 0 + policy validity | sealed_failure_packet → Exit X3E |

## L2 Execution Stages (Scenario Loop)

| Stage | Engine | Function | Gate |
|-------|--------|----------|------|
| 1 | `ScenarioRunner` | Load + filter scenarios from JSON | Scenario count > 0 |
| 2 | `ExecutionAdapter` | Run target app in sandbox per scenario | Exit code capture |
| 3 | `BaseEvalEngine` | Score output against assertions + rubric | Per-dimension scoring |
| 4 | `ScorecardEngine` | Aggregate weighted scores across scenarios | Threshold application |
| 5 | `RegressionDetector` | Compare vs. baseline (optional) | Regression threshold |

## Exit Disposition Mapping (Canonical X3)

> Scenarios emit sealed packets to E5. Exit consumes sealed packets and emits exactly one X3 disposition.
> Individual scenario failures are captured in scorecard, NOT as X3 dispositions.

| Failure Mode | Stage | Sealed Packet | X3 Disposition | terminal_class | User Action |
|--------------|-------|---------------|----------------|----------------|-------------|
| Suite ID missing | R5 (pre-L2) | `sealed_failure_packet` | `X3E_SAFE_ABSTAIN` | FAILURE | Provide valid `--suite` |
| No scenarios match filter | R5 (pre-L2) | `sealed_failure_packet` | `X3E_SAFE_ABSTAIN` | FAILURE | Relax `--filter` criteria |
| Judge unavailable (Qwen down) | E3 | `sealed_degraded_packet` | `X3D_ALLOW_FINISH` (degraded=true) | DEGRADED_SUCCESS | Check Qwen health; run deterministic-only |
| Scorecard aggregation error | E3 | `sealed_failure_packet` | `X3E_SAFE_ABSTAIN` | FAILURE | Check eval engine logs |
| Regression detected (baseline mode) | E3 | (in scorecard) | `X3D_ALLOW_FINISH` (warn) | SUCCESS | Review regression table |
| Full success | E5 | `sealed_success_packet` | `X3D_ALLOW_FINISH` | SUCCESS | — |
| Full success + cache eligible | E5 | `sealed_success_packet` + `cache_commit_candidate` | `X3C_COMMIT_REQUEST_TO_UWG` then `X3D` | SUCCESS | — |

## Local Evidence Contract (FEC)

> apps_eval produces a certification-grade FEC via `apps_eval/cert/fec_producer.py` → `resolve_fec()`
> This is a local evidence contract — scenarios are preloaded, not retrieved from C0.

```yaml
# Produced by apps_eval/cert/fec_producer.py
producer: apps_eval.cert.fec_producer
schema_version: "1.0"
grounded: false                              # Always false — scenarios preloaded from disk
evidence_sufficiency: template_only          # empty | template_only | partial | grounded
retrieval_sources: []                          # Scenarios loaded from eval corpus, not retrieved
route_id: apps_eval.evaluation_v1
template_ids:
  - apps_eval.scenario_runner.v1
  - apps_eval.scorecard_engine.v1
  - apps_eval.regression_detector.v1
eval_context:
  suite_id: <suite_identifier>
  scenario_count: <n>
  dimensions: [correctness, determinism, governance, latency_sla, output_richness]
  judge_model: qwen_2.5_7b | external_llm
  threshold_profile: default | strict | permissive
source_ladder:
  scenario_sources: []                       # From evaluation_prompts.json (preloaded)
  policy_sources: []                         # From eval_policies.yaml
  threshold_sources: []                      # From threshold_profiles.yaml
# Additional fields:
#   scorecard_summary: {}                     # Dimension scores + verdicts
#   regression_delta: {}                      # Baseline comparison results
#   judge_calibration_status: {}              # Per-dimension judge confidence
```

## File Outputs (Sealed Artifacts)

```
artifacts/apps_eval/runs/<timestamp>/
├── eval_report_<trace_id[:8]>.md           # Full markdown report with scorecard
├── scorecard_<trace_id[:8]>.csv             # Machine-readable dimension scores
├── eval_manifest_<trace_id[:8]>.json        # Lightweight run manifest
├── run_summary_<trace_id[:8]>.json          # Provenance + gate results + verdict
├── regression_table_<trace_id[:8]>.json     # Baseline comparison (if applicable)
└── compiled_prompt_artifact.json            # Judge prompt assembly (audit replay)
```

## Cross-App Integration Points

| Source App | Artifact Consumed | Usage | Boundary |
|------------|-------------------|-------|----------|
| `apps_exec` | Executive brief (disk) | Evaluated by `exec_brief_generation` suite | Read-only; prebuilt artifact |
| `apps_rg` | Resume output (disk) | Evaluated by `orchestration_hop` suite | Read-only; prebuilt artifact |
| `apps_qna` | StoryBank cards (disk) | Evaluated by Q&A contract validation suite | Read-only; prebuilt artifact |
| `apps_research` | Company brief (disk) | Reference for cross-app eval scenarios | Read-only; prebuilt artifact |

> **apps_eval does NOT invoke target apps at runtime.**
> Target apps are executed via `execution_adapter` in isolated sandbox.
> The integration is artifact-on-disk or adapter-boundary, not API call.

## Non-Goals (This Spine Does NOT)

- ❌ Side-effect actions (no durable writes to target apps, no state mutation)
- ❌ CommitRequest for scenario data (eval is read-only harness)
- ❌ L3 orchestration DAG (bypassed — scenario loop runs within L2 E3)
- ❌ C0 vector retrieval (scenarios preloaded from `evaluation_prompts.json`)
- ❌ Runtime HITL chat (evaluation is fully automated; X3B not emitted)
- ❌ Direct L4 writes (optional cache commit via Exit → CommitRequest → UWG only)
- ❌ Hidden cross-app execution (target apps run via adapter boundary only)
- ❌ Judge model training or fine-tuning (read-only inference only)

## See Also

- `README.md` — Quick start and benchmark suite table
- `RUNBOOK.md` — On-call triage and failure modes
- `SLO.md` — Service level objectives and cost ceilings
- `SVP_ENGINEERING_REVIEW.md` — Architecture review
- `config/eval_policies.yaml` — Suite configuration and kill switches
- `config/domain_contract/eval_rubrics.yaml` — Dimension rubrics
- `config/domain_contract/threshold_profiles.yaml` — Pass thresholds
- `engines/scenario_runner.py` — Main execution loop
- `engines/base_eval_engine.py` — Core evaluation scoring
- `engines/scorecard_engine.py` — Weighted aggregation
- `engines/regression_detector.py` — Baseline comparison
- `cert/fec_producer.py` — Local evidence contract producer
- `__main__.py` — Canonical CLI entrypoint
