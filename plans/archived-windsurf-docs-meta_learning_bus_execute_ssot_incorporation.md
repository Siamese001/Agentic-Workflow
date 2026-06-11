---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\meta_learning_bus_execute_ssot_incorporation.md'
original_relative_path: 'meta_learning_bus_execute_ssot_incorporation.md'
source_sha256: 9b6d5bb571ec4aa9e8c05c37d365370493ba933253082586175eb3047381ee00
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Meta-Learning Bus: What execute_ssot Incorporates for the Next Healing Round

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Overview

Every `execute_ssot --heal` run feeds data into the meta-learning bus through
three distinct channels.  This document maps **what data is captured**, **where
it is persisted**, and **how it influences the next healing round**.

---

## 1. Healing Action Records (Runtime State)

### What is captured

Each agent that successfully fixes violations during a run emits a structured
healing action via `_record_healing_action()`.  The record schema:

| Field | Source | Example |
|---|---|---|
| `agent` | Agent class key | `"FileClassificationAgent"` |
| `territory` | Current scan territory | `"L5_safety"`, `"__global__"` |
| `routing_score` | Confidence value from SovereignDecisionEngine | `0.95` |
| `routing_tier` | Decision tier (DETERMINISTIC, LLM, etc.) | `"DETERMINISTIC"` |
| `model` | LLM model if used | `"none"` |
| `routing_gate` | Gate that approved the action | `"N/A"` |
| `confidence` | Heal confidence score | `0.95` |
| `fix_summary` | Human-readable summary | `"Fixed 3 of 5 architecture violations"` |
| `outcome` | SUCCESS / FAILED | `"SUCCESS"` |
| `timestamp` | ISO-8601 timestamp | `"2025-06-01T16:00:19.123456"` |

### Recording sites (6 call sites in execute_ssot.py)

| Agent | Territory Scope | Line |
|---|---|---|
| LocationAgent | per-territory | ~2591 |
| GravityLeakRepairAgent | `__global__` | ~2756 |
| ArchitectureGovernorAgent | per-territory | ~2938 |
| Phase 2 reconciliation agents | per-territory | ~1959 |
| RootHygieneAgent | `__global__` | ~4684 |

### Where it accumulates

All records append to `state_mgr.state["healing_actions"]` (in-memory list).
This list is the **primary input** to the meta-learning intake adapter fired
at the end of the run.

---

## 2. Meta-Learning Intake Pipeline (`_fire_meta_learning_intake`)

Fired once at the end of every run (line ~4964), this function converts
healing actions into the meta-learning persistence layer.

### Stage A: HealingOutcomeIntakeAdapter

```
healing_actions[] --> HealingOutcomeAggregator --> HealingOutcomeIntakeAdapter --> InMemoryHealingOutcomeIntakeStore
```

1. **HealingOutcomeAggregator** ingests each healing action as a
   `HealingOutcomeEvent` with fields:
   - `healer_id` = agent name
   - `tier` = routing tier (defaults to `"L5"`)
   - `failure_type` = violation type (defaults to `"UNKNOWN"`)
   - `success` = True unless status is plan_only/skipped/error/failed
   - `timestamp_utc` = 0 (deterministic — no wall-clock)

2. **Aggregator produces a snapshot**: deterministic stats grouped by
   `(healer_id, tier, failure_type)` with `success_rate` rounded
   half-up to 4 decimal places.

3. **IntakeAdapter builds an `HealingOutcomeIntakeRecord`**:
   - `schema_version` = 1
   - `snapshot` = sorted tuple of `HealingOutcomeStats`
   - `proposal` = `HealingOutcomeProposal` (Phase 1: no-op container)
   - `source` = `"execute_ssot"`

4. **Record persisted** to `InMemoryHealingOutcomeIntakeStore`.

5. **`RuntimeStateManager.update_meta_learning()`** updates the dashboard
   state with the count of persisted records and a human-readable experience
   string.

### Stage B: MetaLearningPipeline.run_pipeline()

After intake, `_fire_meta_learning_intake` attempts to run the full
`meta_learning_pipeline.run_pipeline()` which orchestrates:

| Step | Engine | Output |
|---|---|---|
| Snapshot | `create_snapshot()` | `MetaLearningSnapshot` |
| RCA | `RCAEngine.analyze()` | `RCAReport` with classified failure findings |
| Pattern Analysis (W3) | `PatternAnalysisEngine.analyze()` | `PatternFindingReport` with clusters |
| Semantic Retrieval (W2) | `_retrieve_semantic_context()` | Embedding metadata (C0 informational) |
| Shadow Drift (W4-C) | `ShadowDriftAnalyzer.analyze_batch()` | `DriftSummary` written to L4 |
| Policy Recommendation (W4-D) | `PolicyRecommendationEngine` | Advisory recommendation to L4 |
| Retrieval Profile Proposal (W4-E) | `RetrievalProfileProposalManager` | Proposal requiring approval |
| Config Optimization | `HealingConfigOptimizer` | Threshold adjustment proposals |
| RLHF | `RLHFOptimizer` | DPO-driven threshold adjustments |
| Proposers (L0/RAG/L1/L5) | Per-layer proposers | `ChangePackage` proposals |

**Critical invariant**: `proposal_only=True` by default.  The pipeline
produces proposals but does **not** commit or activate them without explicit
approval through the `ApprovalGate` protocol.

### Guard-import resilience

Both Stage A and Stage B imports are wrapped in `try/except ImportError`.
Pre-Wave 0B (before system_learning modules are fully restored), these are
safe no-ops.  After Wave 0B restoration, the full pipeline activates
automatically.

---

## 3. RuntimeStateManager Meta-Learning State

The `state_mgr.state["meta_learning"]` dict tracks dashboard-level metrics
that persist across the run:

```python
{
    "enabled": True,                          # Set to True on first update
    "total_experiences": <count>,             # From intake store
    "patterns_extracted": 0,                  # Reserved for pattern engine
    "strategy_weights": {"cot": 1.0, "tot": 1.0, "react": 1.0},  # Reserved
    "recent_experiences": ["intake: N healing records persisted", ...],  # Last 5
}
```

This state is saved to the mission state file via `state_mgr.save()` after
each `update_meta_learning()` call.

---

## 4. What the Next Healing Round Consumes

### 4a. HealingOutcomeAggregateSnapshot

The `HealingConfigOptimizer` reads persisted intake records and builds
`HealingOutcomeAggregateSnapshot` objects.  For each `(healer_name, tier,
failure_type)` key with enough samples (`min_sample_size >= 20`):

- **Low success rate** (`< 0.5`): proposes escalation delta (+0.1) to
  threshold, capped at `max_threshold=2.0` and `max_delta=0.2` per run.
- These are **proposal-only** — they produce `ChangePackage` artifacts that
  require approval before activation.

### 4b. Pattern Analysis Clusters

The `PatternAnalysisEngine` clusters historical healing outcomes by failure
signature embeddings.  Clusters with `min_cluster_size >= 2` and
`distance_threshold <= 0.25` produce `PatternFinding` objects that:

- Feed into `DefaultHealingPatternAdvisor` as advisory hints (C0 only)
- Provide `pattern_boost` values for audit logging
- Append `reason_codes` to healing decisions
- **Cannot** change routing tiers or heal_confidence values

### 4c. Shadow Drift Signals

If a shadow embedder is configured in `RetrievalProfile`:

- `ShadowDriftAnalyzer` computes drift metrics from accumulated telemetry
- `DriftSummary` is written to L4 (informational only)
- `PolicyRecommendationEngine` converts drift into bounded recommendations
- `RetrievalProfileProposalManager` stages recommendations as proposals
  requiring explicit approval before activating

### 4d. MetaLearningClientMixin (Agent-Level)

Agents inheriting `MetaLearningClientMixin` can:

- **Recall** healing patterns from Pinecone vector store via
  `retrieve_healing_patterns(error_signature)`
- **Cache** expensive analysis results in Redis
- **Store** new successful patterns for future recall
- **Track** healing depth to prevent infinite loops

This operates independently of the pipeline-level intake and provides
per-agent healing memory across runs.

### 4e. MetaLearningMixin (Knowledge Graph)

Agents inheriting `MetaLearningMixin` connect to a knowledge graph for:

- `recall_or_execute()` — check KG before expensive computation
- `reflect_on_execution()` — post-hoc learning from outcomes
- `record_agent_interaction()` — track inter-agent call patterns
- `inherit_rules_from()` / `mark_incompatible_with()` — structural learning

---

## 5. Activation Gates

Meta-learning activation is governed by `ActivationFlags` (L4-persisted,
signed, replay-bound):

| Flag | Prerequisite |
|---|---|
| `execution_hardened` | P0 Execution Boundary complete |
| `mutation_surface_zero` | P0 Execution Boundary complete |
| `freeze_authority_active` | P1 Freeze Authority active |
| `meta_learning_prepared` | P2 Meta-Learning prep complete |
| `blast_radius_containment_active` | P2 containment active |
| `meta_learning_enabled` | **All above must be True** |

Until `meta_learning_enabled=True`, the pipeline runs in proposal-only mode
and healing pattern recall returns empty results.

---

## 6. Data Incorporated from Recent execute_ssot Runs

Based on the healing actions recorded during the duplicate-file RCA and
Phase 2 hang fix sessions:

### Healing outcomes persisted to intake store

| Agent | Violation Type | Territories | Outcome |
|---|---|---|---|
| FileClassificationAgent | SEMANTIC_DUPLICATE | L5_safety, interfaces | SUCCESS — 10 duplicates removed |
| LocationAgent | WRONG_LOCATION | per-territory | SUCCESS where violations found |
| ArchitectureGovernorAgent | LAYER_INVERSION | per-territory | SUCCESS where violations found |
| GravityLeakRepairAgent | GRAVITY_LEAK | __global__ | SUCCESS where violations found |
| RootHygieneAgent | ROOT_HYGIENE | __global__ | SUCCESS where violations found |

### Pattern signals extracted

- **Recurring duplicate-file motif**: Same-directory files with overlapping
  primary AST class names created by competing rename scripts
  (PascalSovereigntyFixer vs manual renames).
- **Timeout failure pattern**: `heal_repository()` calls without territory
  scoping causing full-repo AST re-parse during Phase 2 reconciliation.
- **O(n^2) performance anti-pattern**: Per-candidate import counting in
  `_detect_semantic_duplicates` triggering quadratic AST parsing.

### Fixes that feed forward as learned constraints

| Fix | Effect on Next Round |
|---|---|
| Territory scoping (`target_territory`) | Agents scope scans to current territory, reducing heal time |
| Timeout guard (300s default) | Hanging agents are skipped with RuntimeError, not blocking pipeline |
| Import index pre-computation | Semantic duplicate detection runs in O(n) instead of O(n^2) |
| Semantic duplicate detection | FileClassificationAgent now catches same-dir overlapping-class duplicates |

---

## 7. Summary

The meta-learning bus is a **multi-layer feedback system**:

1. **Immediate** — healing actions recorded per-agent, per-territory during the run
2. **Batch intake** — aggregated into `HealingOutcomeIntakeRecord` at run end
3. **Pipeline analysis** — RCA, pattern clustering, drift detection, threshold proposals
4. **Agent memory** — per-agent Pinecone/Redis/KG recall for future healing decisions
5. **Activation gates** — L4-persisted flags controlling when proposals can be applied

All layers currently operate in **proposal-only / informational-only** mode.
No automatic application occurs until `ActivationFlags.meta_learning_enabled`
is set to `True` via explicit approval.

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

