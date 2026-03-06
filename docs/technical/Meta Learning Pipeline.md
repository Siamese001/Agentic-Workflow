# Meta Learning Pipeline

## Overview

The meta-learning pipeline is a widescreen, policy-driven adaptation loop that ingests audit telemetry, healing outcomes, shadow drift signals, and RLHF feedback to produce versioned `ChangePackage` proposals across L0 (thresholds), L1 (model params), L5 (policy params), and RAG (retrieval profiles). Each proposal passes through an `ApprovalGate` before being committed to the `L4VersionStore` and optionally activated.

---

## Architecture

```
AuditStore (L4a)     TelemetryStore      ConfigProvider
     │                    │                    │
     └────────────────────┴────────────────────┘
                          │
                          ▼
               PipelineConfig + PipelineDependencies
                          │
              ┌───────────┴────────────────────────────────┐
              │                                            │
     SignalGroupingEngine                      PatternAnalysisEngine
              │                                            │
              ▼                                            ▼
     HealingOutcomeAggregator             ShadowDriftAnalyzer
              │                                            │
              └──────────────┬─────────────────────────────┘
                             │
                    ┌────────┴─────────────────────────┐
                    │        Proposer Layer             │
                    ├── L0ThresholdTuner (L0Proposer)  │
                    ├── L1ModelProposer                 │
                    ├── L5PolicyProposer                │
                    └── RAGProposer                     │
                             │
                             ▼
                       ApprovalGate
                             │
                             ▼
                       L4VersionStore  ──► Activator
```

---

## Pipeline Configuration

**File:** `system_learning/pipelines/meta_learning_pipeline.py`

`PipelineConfig` (dataclass) — the full configuration surface for one pipeline run:

| Field | Type | Description |
|---|---|---|
| `engine_version` | `str` | Pipeline engine version string |
| `config_surface_version` | `str` | Config surface version at run time |
| `shadow_thresholds` | `ShadowThresholds` | Thresholds for shadow validation |
| `cooldown_policy` | `CooldownPolicy` | Minimum time between proposals |
| `sample_policy` | `SampleSizePolicy` | Minimum observation counts |
| `oscillation_policy` | `OscillationPolicy` | Anti-oscillation constraints |
| `enabled_proposers` | `tuple[str, ...]` | Which proposers to activate this run |
| `require_replay_validation` | `bool` | Gate on replay digest match |
| `require_shadow_validation` | `bool` | Gate on shadow drift score |
| `proposal_only` | `bool` | Dry-run: propose but do not commit |

---

## Pipeline Dependencies

`PipelineDependencies` (dataclass) — all injected collaborators:

| Field | Type | Description |
|---|---|---|
| `audit_store` | `AuditStore` | L4a audit slice reader |
| `telemetry_store` | `TelemetryStore` | Telemetry event reader |
| `config_provider` | `ConfigProvider` | Current config surface |
| `baseline_metrics_provider` | `BaselineMetricsProvider` | Production + shadow metrics |
| `l0_proposer` | `L0Proposer | None` | L0 threshold proposer |
| `rag_proposer` | `RAGProposer | None` | RAG retrieval profile proposer |
| `l1_proposer` | `L1Proposer | None` | L1 model parameter proposer |
| `l5_proposer` | `L5Proposer | None` | L5 policy parameter proposer |
| `version_store` | `VersionStore | None` | L4 versioned change store |
| `activator` | `Activator | None` | Activates committed versions |
| `approval_gate` | `ApprovalGate | None` | Approval decision gate |
| `healing_outcome_intake_adapter` | `HealingOutcomeIntakeAdapter | None` | Healing outcome ingestion |
| `healing_config_optimizer` | `HealingConfigOptimizer | None` | Healing config optimizer |
| `l4_state_writer` | `L4StateWriter | None` | L4 state persistence |
| `pattern_analysis_engine` | `PatternAnalysisEngine | None` | Pattern clustering |
| `resource_predictor_bytes` | `bytes | None` | Serialized resource predictor model |
| `rollback_refinement_decision_bytes` | `bytes | None` | Serialized rollback model |
| `dpo_batch_bytes` | `bytes | None` | Serialized DPO batch |
| `rlhf_optimizer` | `RLHFOptimizer | None` | RLHF optimizer |
| `healing_confidence_scorer` | `HealingConfidenceScorer | None` | Confidence scorer |
| `failure_fingerprinter` | `FailureFingerprinter | None` | Failure fingerprinter |
| `risk_correlator` | `RiskCorrelator | None` | Risk correlator |
| `arbitration_engine` | `ArbitrationEngine | None` | Proposal arbitration |
| `arbitration_policy` | `ArbitrationPolicy | None` | Arbitration policy |

---

## Pipeline Protocols

All collaborators are typed as `Protocol` classes to support dependency injection and testing:

| Protocol | Method(s) | Description |
|---|---|---|
| `AuditStore` | `read_audit_slice(start, end)` | Reads L4a audit records in time window |
| `TelemetryStore` | `read_events(start, end)` | Reads telemetry events in time window |
| `ConfigProvider` | `get_current_configs()`, `get_last_update_utc()`, `get_param_history(param)` | Config surface access |
| `VersionStore` | `commit_change_package(package)` | Commits a `ChangePackage` to L4 |
| `Activator` | `activate(version_id)` | Activates a committed version |
| `ApprovalGate` | `decide(proposal, context)` | Returns `ApprovalDecision` |
| `L0Proposer` | `propose(snapshot)` | Returns `L0ThresholdChangePackage | None` |
| `RAGProposer` | `propose(snapshot)` | Returns RAG retrieval profile proposal |
| `L1Proposer` | `propose(snapshot)` | Returns `L1ModelChangePackage | None` |
| `L5Proposer` | `propose(snapshot)` | Returns `L5PolicyChangePackage | None` |
| `BaselineMetricsProvider` | `production_metrics()`, `shadow_metrics()` | Returns metrics for shadow comparison |

`PipelineError(RuntimeError)` — base pipeline error class.
`ValidationError(PipelineError)` — raised on proposal validation failure.

---

## L0 Threshold Tuner

**File:** `system_learning/engines/l0_threshold_tuner.py`

`L0ProposerAdapter` implements `L0Proposer` via `propose(snapshot)`.

`L0ThresholdChangePackage` (dataclass):

| Field | Type | Description |
|---|---|---|
| `surface_name` | `str` | Config surface identifier (e.g., `healing_confidence_x`) |
| `old_value` | `float` | Current threshold value |
| `new_value` | `float` | Proposed threshold value |
| `justification` | `str` | Evidence-based rationale |
| `snapshot_id` | `str` | Source snapshot reference |

Note: `HEALING_CONFIDENCE_X` (0.75) and `HEALING_CONFIDENCE_Y` (0.40) are **IMMUTABLE** — the L0 tuner may propose changes to other surfaces but these two constants are locked.

---

## L1 Model Proposer

**File:** `system_learning/engines/l1_model_proposer.py`

`L1ModelProposer.propose(snapshot)` — proposes changes to L1 cognitive model parameters.

`L1ModelChangePackage` (dataclass):

| Field | Type | Description |
|---|---|---|
| `surface_name` | `str` | Model parameter surface |
| `parameter` | `str` | Parameter name (e.g., `temperature`, `top_p`) |
| `old_value` | `float` | Current value |
| `new_value` | `float` | Proposed value |
| `justification` | `str` | Evidence-based rationale |
| `snapshot_id` | `str` | Source snapshot reference |

---

## L3 Efficiency Tuner

**File:** `system_learning/engines/l3_efficiency_tuner.py`

`L3EfficiencyTuner` analyzes orchestration performance and identifies bottlenecks.

`EfficiencyBottleneck` dataclass:

| Field | Type | Description |
|---|---|---|
| `component` | `str` | Component identifier |
| `metric_name` | `str` | Metric name (e.g., `dag_dispatch_ms`) |
| `observed_value_ms` | `float` | Measured value |
| `threshold_ms` | `float` | Configured threshold |
| `territory` | `str` | Territory (apps_lic / apps_rg / agentic_core) |
| `recommendation` | `str` | Suggested remediation |

`EfficiencyReport` dataclass:

| Field | Type | Description |
|---|---|---|
| `snapshot_id` | `str` | Source snapshot |
| `bottlenecks` | `tuple[EfficiencyBottleneck, ...]` | All detected bottlenecks |
| `total_territories` | `int` | Territories scanned |
| `total_agents_executed` | `int` | Total agents in snapshot |
| `avg_territory_time_ms` | `float` | Average territory execution time |

---

## L5 Policy Proposer

**File:** `system_learning/engines/l5_policy_proposer.py`

`L5PolicyProposer.propose(snapshot)` — proposes changes to L5 safety policy parameters based on false-positive / false-negative rates.

`L5PolicyChangePackage` (dataclass):

| Field | Type | Description |
|---|---|---|
| `surface_name` | `str` | Policy surface identifier |
| `direction` | `str` | `UP` / `DOWN` |
| `delta` | `float` | Magnitude of proposed change |
| `justification` | `str` | Evidence rationale |
| `snapshot_id` | `str` | Source snapshot |
| `false_positive_rate` | `float` | FP rate in observation window |
| `false_negative_rate` | `float` | FN rate in observation window |
| `observation_count` | `int` | Number of observations |

---

## Pattern Analysis Engine

**File:** `system_learning/engines/pattern_analysis_engine.py`

`PatternAnalysisEngine` clusters healing outcomes and drift signals into deterministic pattern summaries for proposer input.

`PatternAnalysisConfig` dataclass:

| Field | Default | Description |
|---|---|---|
| `precision` | — | Rounding precision for vector coordinates |
| `min_cluster_size` | — | Minimum observations per cluster |
| `distance_threshold` | — | Max cosine distance within a cluster |
| `success_rate_threshold_low` | — | Below this rate, findings are elevated |
| `min_observations` | — | Minimum for statistical validity |
| `drift_score_threshold` | — | Drift score triggering a finding |

Key methods:

| Method | Description |
|---|---|
| `analyze(snapshot)` | Full analysis run from snapshot, returns `PatternAnalysisReport` |
| `_analyze_from_snapshots(snapshots)` | Processes L4 snapshot data |
| `_analyze_embeddings(texts)` | Clustering over embedding vectors |
| `analyze_texts(texts)` | Public embedding analysis entry point |
| `_deterministic_cluster(vectors)` | Deterministic k-means-style clustering |
| `_l2_normalize(vector)` / `_cosine_distance(a, b)` | Vector math helpers |
| `_compute_centroid(vectors)` | Centroid computation |
| `_vector_hash(vector)` / `_compute_digest(report)` | Deterministic hashing |

`PatternFinding` dataclass: `key: PatternFindingKey`, `severity: float`, `evidence: str`, `metrics: tuple`.

`PatternFindingKey` dataclass: `label`, `component`, `dimension`.

`PatternAnalysisReport` dataclass: `findings: tuple`, `source_ids: PatternSourceIds`, `_digest: str`.

`PatternSourceIds` dataclass: `healing_snapshot_version`, `detection_signal_version`, `drift_snapshot_version`.

`Cluster` dataclass: `centroid: list[float]`, `cluster_size: int`, `representative_metadata_keys: list[str]`.

---

## Signal Grouping Engine

**File:** `system_learning/engines/signal_grouping_engine.py`

`SignalGroupingEngine` aggregates raw telemetry signals into coalesced groups for efficient pattern analysis.

`SignalGroup` dataclass:

| Field | Type | Description |
|---|---|---|
| `group_key` | `str` | Deterministic group identifier |
| `signal_type` | `str` | Signal type identifier |
| `component` | `str` | Component that emitted the signal |
| `count` | `int` | Number of signals in group |
| `earliest_utc` | `int` | Earliest signal timestamp |
| `latest_utc` | `int` | Latest signal timestamp |
| `sample_payloads` | `tuple[bytes, ...]` | Up to N representative payloads |

`SignalGroupingReport` dataclass: `snapshot_id`, `groups`, `total_signals`, `total_groups`.

`SignalGroupingEngine.group_signals(events, snapshot_id)` — produces a `SignalGroupingReport`.

---

## Healing Outcome Aggregator

**File:** `system_learning/engines/healing_outcome_aggregator.py`

`HealingOutcomeAggregator` feeds per-invocation healing outcomes into the meta-learning pipeline.

Key methods: `ingest`, `ingest_invocation`, `compute_success_rate`, `build_proposal`, `create_snapshot`, `snapshot`, `clear_aggregates`.

`HealingOutcomeAggregatorProtocol` — minimal injectable interface: `ingest_invocation`, `compute_success_rate`, `create_snapshot`.

See [Healing & Escalation Loop](Healing%20%26%20Escalation%20Loop.md) for full method documentation.

---

## Shadow Drift Analyzer

**File:** `system_learning/engines/shadow_drift_analyzer.py`

`ShadowDriftAnalyzer.analyze_batch(pairs)` produces `DriftSummary`:
- `mean_cosine`, `p95_cosine` — distribution statistics
- `drift_flag` — `True` when `drift_score > drift_score_threshold`
- `deterministic_digest` — SHA-256 of entire summary

See [Agentic RAG](Agentic%20RAG.md) for full documentation.

---

## L4 State Writer

**File:** `system_learning/engines/l4_state_writer.py`

`L4StateWriter` (Protocol) — the pipeline's write interface to L4 state. Concrete implementations: `FileBackedL4StateWriter`, `DefaultL4StateWriter`, `InMemoryL4StateWriter`, `NoOpL4StateWriter`.

| Method | Description |
|---|---|
| `write_l4a_detection_signal(signal)` | Writes a detection signal to L4a bucket |
| `write_l4b_healing_snapshot(snapshot)` | Writes a healing outcome snapshot to L4b |
| `write_l4c_shadow_drift(drift)` | Writes a shadow drift summary to L4c |
| `write_l4c_policy_recommendation(rec)` | Writes a policy proposal to L4c |
| `write_l4c_retrieval_profile_proposal(proposal)` | Writes a RAG profile proposal to L4c |
| `read_latest_detection_signal()` | Reads most recent L4a signal |
| `read_latest_drift_snapshot()` | Reads most recent L4c drift snapshot |

`_VersionEntry` dataclass: `version_id`, `bucket`, `component_name`, `created_utc`, `payload_bytes`.

---

## L4 Version Store

**File:** `system_learning/engines/l4_version_store.py`

`L4VersionStore` — the canonical versioned change store. Implements `VersionStore` protocol.

| Method | Description |
|---|---|
| `commit_change_package(package)` | Commits a `ChangePackage`, returns `version_id` |
| `get_change_package(version_id)` | Retrieves a committed package |
| `list_versions(component)` | Lists version history for a component |
| `update_activation_pointer(version_id)` | Advances the active pointer |
| `get_active_version(component)` | Returns current active `VersionedPackage` |
| `rollback(version_id)` | Rolls back active pointer to a prior version |

`VersionedPackage` dataclass: `version_id`, `parent_version_id`, `change_spec_hash`, `committed_at_utc`, `package_bytes`.

`ParentVersionNotFound(Exception)` / `VersionNotFound(Exception)` — raised on invalid version references.

---

## Change Package

**File:** `system_learning/engines/change_package_impl.py`

`ChangePackage` (dataclass) — the universal transfer object for all meta-learning proposals:

| Field | Type | Description |
|---|---|---|
| `source` | `str` | Proposer identifier |
| `target` | `str` | Target component |
| `changes` | `bytes` | Serialized change specification |
| `confidence` | `float` | Proposer confidence score [0, 1] |
| `reason` | `tuple[str, ...]` | Evidence reason codes |
| `timestamp_utc` | `int` | Unix timestamp of proposal |
| `embedding_context_hash` | `str | None` | Hash of embedding context if RAG-driven |
| `authority_sensitivity` | `str` | LOW / MEDIUM / HIGH / CRITICAL |
| `target_surface` | `str | None` | Specific parameter surface |

---

## RCA Engine

**File:** `system_learning/engines/rca_engine.py`

`RCAAnalysisError(RuntimeError)` — raised when root-cause analysis cannot produce a reliable determination. The pipeline treats RCA failures as non-blocking (proposal proceeds with reduced confidence) unless `proposal_only=False`.

---

## MetaLearningAgent — L1 Cognitive Agent

**File:** `agentic_core/L1_cognition/reasoning/MetaLearningAgent.py`

`MetaLearningAgent(SovereignBaseAgent)` — the L1 cognitive agent that interfaces with the system_learning pipeline for online learning.

| Method | Description |
|---|---|
| `store_experience(state, thought_type, outcome, reward)` | Appends `ExperienceRecord` to experience buffer |
| `update_strategy_weights(experience)` | Updates strategy weights from experience |
| `_load_strategy_weights()` | Loads weights from disk |
| `strategy_weights_digest` | SHA-256 of current strategy weights (for `MetaLearningReplayBinding`) |
| `_save_strategy_weights()` | Persists updated weights |
| `extract_patterns(experiences)` | Calls `PatternAnalysisEngine` on experience buffer |
| `get_strategy_recommendation(context)` | Returns best strategy given current weights |
| `get_live_statistics()` | Live telemetry from current experience buffer |
| `get_statistics()` | Cumulative statistics across all sessions |
| `_discover_patterns()` | Internal pattern discovery loop |
| `heal_repository(context)` / `heal(context)` | Self-healing entry points |

`ExperienceRecord` (dataclass): `state: dict[str, Any]`, `thought_type: str`, `outcome: dict[str, Any]`, `reward: float`, `timestamp: datetime`.

---

## L1 Meta Adapter

**File:** `system_learning/adapters/l1_meta_adapter.py`

`L1MetaAdapter` bridges `MetaLearningAgent` to the pipeline's `TelemetryStore` interface.

| Method | Description |
|---|---|
| `extract_telemetry(agent)` | Extracts `L1TelemetryEvent` records from the agent's experience buffer |
| `detect_drift(agent, baseline)` | Produces `L1DriftSignal` by comparing current weights to a baseline |

`L1TelemetryEvent` dataclass: `timestamp_utc: int`, `event_type: str`, `payload_bytes: bytes`.

`L1DriftSignal` dataclass: `surface_name: str`, `drift_magnitude: float`, `direction: str`, `observation_count: int`, `snapshot_id: str`.

---

## Offline Healing Outcome Evaluator

**File:** `system_learning/engines/offline_healing_outcome_evaluator.py`

`OfflineHealingOutcomeEvaluator.evaluate(snapshot)` — evaluates a historical healing snapshot against a reference baseline to quantify learning progress. Used in non-production evaluation runs where the live aggregator is not active.

---

## Approval Gates

**File:** `system_learning/pipelines/approval_gates.py`

`ApprovalDecision(Enum)`: `APPROVE`, `REJECT`, `DEFER`.

`ApprovalGate(Protocol)`: `decide(proposal, context) -> ApprovalDecision`.
`RiskTierClassifier(Protocol)`: `classify(proposal) -> str`.

`DefaultRuleBasedGate` — threshold-driven approval.
`DefaultRiskClassifier` — maps `ChangePackage` fields to risk tier.

**File:** `system_learning/pipelines/approval_gate_impl.py`

`ApprovalDecision` (dataclass): `approved: bool`, `reason: str`, `requires_manual_review: bool`.

- `AutoApprovalGate` — auto-approves proposals above confidence threshold
- `AlwaysApproveGate` — test utility
- `NeverApproveGate` — lockdown / circuit-breaker

---

## RLHF Optimizer Integration

**File:** `system_learning/engines/rlhf_optimizer.py`

`RLHFOptimizer(Protocol)`: `propose_from_dpo(dpo_batch) -> RLHFChangePackage`.
`DefaultDeterministicRLHFOptimizer` — deterministic implementation.

`RLHFChangePackage` (in `rlhf_optimizer_impl.py`): `surface_name`, `parameter`, `direction`, `delta`, `justification`, `snapshot_id`, `pair_count`, `preference_strength`.

The pipeline injects `rlhf_optimizer` via `PipelineDependencies` and calls `propose_from_dpo(dpo_batch_bytes)` when `dpo_batch_bytes` is non-None.
