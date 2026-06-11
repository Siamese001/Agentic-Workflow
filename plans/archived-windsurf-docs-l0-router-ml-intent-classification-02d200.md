---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\l0-router-ml-intent-classification-02d200.md'
original_relative_path: 'l0-router-ml-intent-classification-02d200.md'
source_sha256: 6dbd1a9fe59904af584fe5265550d7896677e926c98ee725e05bee19aaa85b5a
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-14'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# L0 Router — ML Intent Classification Upgrade

Augment `AgenticRouter._classify()` from keyword-ratio scoring to a three-tier learned pipeline that feeds system_learning telemetry back into L0 routing decisions, while preserving determinism and governance invariants.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State (Gaps)

| Component | File | Weakness |
|---|---|---|
| `AgenticRouter._classify()` | `L0_routing/engines/agentic_router.py:159-179` | Keyword hit-ratio — O(n·k) scan, no semantic understanding, ties broken by dict insertion order |
| `RouteTarget.intent_keywords` | same | Static list, never updated from outcome data |
| `ShadowRouterClassifier.classify_shadow_route()` | `L0_routing/engines/shadow_router_classifier.py:91-144` | Hard-coded 3-bucket risk split; comment says "could be ML model" |
| `L0ThresholdTuner` | `system_learning/engines/l0_threshold_tuner.py` | Only tunes `escalation_threshold`; ignores routing confidence distribution |
| `MetaLearningBus` (L0 shim) | `L0_routing/meta_control/meta_learning_bus.py` | Passes `MetaLearningChangePackage` but nothing feeds routing classification outcomes back into it |

---

## Proposed ML Architecture — Three Tiers

### Tier 1 — Embedding-based Intent Classifier (drop-in `_classify` replacement)

**Model:** Sentence-embedding cosine similarity against per-target **prototype vectors** stored in system_learning's existing FAISS index (`system_learning/engines/local_faiss_store.py`).

**How it works:**
1. At registration time, `router.register(...)` encodes `intent_keywords + description` → averaged embedding → stored as prototype.
2. At routing time, `_classify(user_input)` encodes the input → cosine-similarity against all prototypes → best match = target.
3. Falls back to legacy keyword scoring if `EmbeddingServiceFactory` returns `EmbeddingDisabledError` (kill-switch path already exists).
4. Confidence = raw cosine similarity (already in `[0, 1]`, replaces hit-ratio).

**Key integration points:**
- `EmbeddingServiceFactory` (`system_learning/engines/embedding_service_factory.py`) — already handles BLAS determinism, fork guard, kill-switch.
- `LocalFaissStore` (`system_learning/engines/local_faiss_store.py`) — prototype vectors stored here, keyed by target name hash.
- **Determinism**: embedding model is pinned via pack-hash; same input → same vector → same decision. Satisfies `ReasoningPolicyEngine` invariants.

---

### Tier 2 — Online Feedback Loop via system_learning MetaLearningBus

**Problem:** Even with embeddings, prototypes stay frozen after registration. We need outcome signal to drift the prototypes toward successful routes.

**How it works:**
1. After each `router.route()` call resolves, `RoutingDecision` (including `result` / `error`) is wrapped into a `MetaLearningChangePackage` (`kind="routing_outcome"`) and enqueued on the `MetaLearningBus`.
2. `TraceFeatureExtractor` (`system_learning/engines/trace_feature_extractor.py`) — already extracts routing signals from execution traces. Add a `routing_confidence` field to `FeatureBundle`.
3. `RCAClusterEngine` clusters repeated misroutes (SAFE_FAILURE / HUMAN_OVERRIDE outcomes on a target) → produces `RCACluster` with `failure_pattern = "ROUTING_MISCLASSIFICATION"`.
4. `OptimizationProposalEngine` maps `ROUTING_MISCLASSIFICATION` → `change_type="ROUTING_RULE_ADJUSTMENT"` proposal (rule table at `_PROPOSAL_RULES` already has this type).
5. `GovernanceRewardModel` scores the proposal; if `invariant_preserved=True`, the proposal updates the FAISS prototype for the misrouted target (re-encode with corrected exemplars).

**New `_PROPOSAL_RULES` entry needed:**
```python
(
    "ROUTING_MISCLASSIFICATION",
    "ROUTING_RULE_ADJUSTMENT",
    "LOW",
    "Update intent prototype embedding for consistently misrouted target",
),
```

---

### Tier 3 — RLHF/DPO Signal from HITL Decisions

**Problem:** Automated outcome signals are noisy. Human-in-the-loop corrections are high-quality supervision.

**How it works:**
1. When a HITL override corrects a routing decision (already logged by `hitl_decision_logger.py`), emit a DPO pair: `(user_input, wrong_target, correct_target)`.
2. Feed into existing `DefaultDeterministicRLHFOptimizer.propose_from_dpo()` (`system_learning/engines/rlhf_optimizer.py`) — currently only used for threshold tuning; extend its `ChangePackage` to include `"prototype_update"` payloads.
3. `L0ThresholdTuner` already watches `escalation_rate`; add a parallel `routing_confidence_p10` metric (10th-percentile confidence across recent routing decisions) — when it drops below `0.3`, it triggers threshold tightening on `min_confidence` in `AgenticRouter`.

---

## Implementation Plan (ordered, minimal footprint)

### Step 1 — `IntentEmbeddingClassifier` (new module)
- **File:** `agentic_core/L0_routing/engines/intent_embedding_classifier.py`
- Pure class wrapping `EmbeddingServiceFactory` + `LocalFaissStore`.
- Exposes `encode_prototype(name, texts)` and `classify(user_input) → (target_name, confidence)`.
- Falls back gracefully to `None` on `EmbeddingDisabledError`.

### Step 2 — Patch `AgenticRouter._classify()`
- **File:** `agentic_core/L0_routing/engines/agentic_router.py`
- Inject `IntentEmbeddingClassifier` as optional constructor arg (`classifier: IntentEmbeddingClassifier | None = None`).
- If classifier present and returns non-None → use embedding result.
- Otherwise → existing keyword path (unchanged, tested).

### Step 3 — `RoutingOutcomeAdapter` (new module)
- **File:** `agentic_core/L0_routing/engines/routing_outcome_adapter.py`
- After `route()` resolves, wraps `RoutingDecision` → `MetaLearningChangePackage(kind="routing_outcome")`.
- Enqueues on injected `MetaLearningBus` (the existing L0 shim at `meta_control/meta_learning_bus.py`).
- Proposal-only; no direct mutation.

### Step 4 — Extend `TraceFeatureExtractor`
- **File:** `system_learning/engines/trace_feature_extractor.py`
- Add `routing_confidence: float` and `routing_target: str` fields to `FeatureBundle`.
- Populated from `routing_outcome` change packages.

### Step 5 — Add `ROUTING_MISCLASSIFICATION` rule to `OptimizationProposalEngine`
- **File:** `system_learning/engines/optimization_proposal_engine.py`
- Single tuple added to `_PROPOSAL_RULES`.

### Step 6 — `L0RoutingConfidenceMonitor` (new module)
- **File:** `system_learning/engines/l0_routing_confidence_monitor.py`
- Mirrors `l0_threshold_tuner.py` pattern.
- Tracks `routing_confidence_p10` metric; proposes `min_confidence` adjustment via `L0ThresholdChangePackage`.

### Step 7 — HITL DPO bridge
- **File:** `system_learning/engines/hitl_decision_logger.py` (extend existing)
- On `decision_type="routing_correction"`, emit DPO pair bytes into `DefaultDeterministicRLHFOptimizer`.

---

## Governance / Determinism Constraints Preserved

| Constraint | How preserved |
|---|---|
| Same inputs → same decision | Embedding pack pinned by hash; FAISS lookup is deterministic given frozen prototypes |
| No wall-clock reads in engine | `timestamp_utc` caller-supplied everywhere; no change needed |
| No direct L4 mutation | All prototype updates go through `MetaLearningBus` → `OptimizationProposal` → `OptimizationCommit` chain |
| Kill-switch coverage | `EmbeddingDisabledError` → fallback to keyword classifier; routing never breaks |
| Proposal-only until validated | `ProposalValidationEngine` gates every commit; `allow_critical=False` default retained |

---

## Files Touched

| File | Type | Change |
|---|---|---|
| `L0_routing/engines/agentic_router.py` | Modify | Inject optional `IntentEmbeddingClassifier` |
| `L0_routing/engines/intent_embedding_classifier.py` | **New** | Embedding classifier wrapper |
| `L0_routing/engines/routing_outcome_adapter.py` | **New** | Outcome → MetaLearningBus bridge |
| `system_learning/engines/trace_feature_extractor.py` | Modify | Add routing_confidence field |
| `system_learning/engines/optimization_proposal_engine.py` | Modify | Add ROUTING_MISCLASSIFICATION rule |
| `system_learning/engines/l0_routing_confidence_monitor.py` | **New** | Confidence metric tuner |
| `system_learning/engines/hitl_decision_logger.py` | Modify | DPO pair emission for routing corrections |

---

## Out of Scope
- `ReasoningPolicyEngine` complexity score weights (separate surface)
- `ShadowRouterClassifier` risk model (separate surface)
- Any changes to L3/L4/L5 layers

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

