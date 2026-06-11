---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\system-learning-signal-enhancement-top10-a3f8c1.md'
original_relative_path: 'system-learning-signal-enhancement-top10-a3f8c1.md'
source_sha256: 59f71ce5b0fa64e09e1b0443c5c15f10f063171125d1021291b1c44b80d5978e
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# System Learning Signal Enhancement — Top 10 Opportunities

**Date:** 2026-03-25
**Scope:** ADG, Execute_SSOT, apps_*
**Goal:** Ensure system learning has all the information needed to enhance and optimize across all three domains.

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


## Current State Summary

### What system learning consumes TODAY

| Signal | Producer | Consumer | Path |
|--------|----------|----------|------|
| Healing EMA rates | `HealingSuccessRateStore` | `DefaultHealingPatternAdvisor` | execute_ssot → meta_learning_pipeline |
| RCA findings (regex) | `rca_engine.analyze_failures` | `SystemLearningMemoryBridge` | meta_learning_pipeline step 5 |
| Drift summaries | `ShadowDriftAnalyzer` (embedding cosine) | `PolicyRecommendationEngine` | meta_learning_pipeline W4-C |
| Policy recommendations | `PolicyRecommendationEngine` | `RetrievalProfileProposalManager` | meta_learning_pipeline W4-D/E |
| Healing outcome events | `HealingOutcomeIntakeAdapter` | `HealingOutcomeAggregator` | execute_ssot → _fire_meta_learning_intake |
| Pattern analysis | `PatternAnalysisEngine` | `HealingConfigOptimizer` | meta_learning_pipeline step 8.6 |
| BGE-m3 failure embeddings | `bmg_embed_text` | FAISS store | _fire_meta_learning_intake |
| Historical backfill | `.healing_backups` dir | `HealingOutcomeAggregator` | _fire_meta_learning_intake Wave 3 |
| BaseHealingOrchestrator cycles | `LicHealingOrchestrator` / `RgHealingOrchestrator` | `GraphMemoryBridge` (Memory MCP) | apps_lic/apps_rg healing loops |

### What system learning does NOT consume (the gaps)

| Available Signal | Producer | Not Connected To |
|------------------|----------|------------------|
| ADG violations (typed, severity-tagged) | `ADGMemoryAdapter._ingest_violations` | Any system learning engine |
| ADG hotspots (fan-out top 20) | `ADGMemoryAdapter._ingest_hotspots` | Healing priority / blast radius |
| ADG repair routes (agent + CI lane) | `RepairRoute.route_violations` | Optimization proposal engine |
| ADG confidence tiers (E9 summary) | `generate_full_adg.py` | L0 confidence monitor |
| ADG violation trend (cross-snapshot) | Multiple `ADGSnapshot_*` entities | Drift analyzer |
| Execute_SSOT phase outcomes | `state_mgr.state` (per-territory) | Meta-learning pipeline |
| Execute_SSOT ADG behavioral scores | `state_mgr.state["adg_territory_score"]` | Routing confidence |
| Execute_SSOT cognitive dispositions | `state_mgr.state["cognitive_dispositions"]` | RCA / pattern engine |
| apps_* domain-specific healing outcomes | `LicHealingOrchestrator._execute_healing` | Cross-domain pattern learning |
| apps_* telemetry spans | `OpenTelemetryTracingAdapter` | System learning telemetry store |

---

## Top 10 Enhancement Opportunities

### #1 — RCA Engine: ADG Violation Correlation

**Domain:** ADG → System Learning
**Value:** Highest — enables causal root-cause attribution
**Current gap:** `rca_engine.analyze_failures()` classifies failures by regex only (SYNTAX, IMPORT, RUNTIME). Zero awareness of whether the failing file has a known architectural violation.

**Enhancement:**
- Add optional `violation_file_set: frozenset[str]` parameter to `analyze_failures()`
- Populated from `ADGMemoryAdapter.query_violations()` (returns `ADGViolation` entities with `source=` observation)
- When a failure's file path matches a violation source → tag `RCAFinding` with `adg_correlated=True` and `violation_type=layer_boundary`
- Persist enriched findings via existing `SystemLearningMemoryBridge.persist_rca_findings()`

**Files touched:**
- `system_learning/engines/rca_engine.py` — add parameter + correlation logic
- `agentic_core/adg/adapters/ADGMemoryAdapter.py` — expose `get_violation_file_set()` helper
- `system_learning/pipelines/meta_learning_pipeline.py` — wire violation set into `analyze_failures` call

**Contract:** Informational-only (C0). ADG unavailable = skip correlation, never crash.

---

### #2 — Execute_SSOT: Phase Outcome Feedback Loop

**Domain:** Execute_SSOT → System Learning
**Value:** Very High — closes the loop between healing actions and learning
**Current gap:** `_fire_meta_learning_intake` ingests `healing_actions` from `state_mgr.state` but NOT the per-phase outcomes (discovery violations, alignment results, gravity fixes, classification results). These are set on `state_mgr.state` keys like `location_violations`, `hierarchy_fixed`, `gravity_fixed`, `classification_violations`, `compliance_scores`, `adg_territory_score` — but never forwarded to the meta-learning pipeline.

**Enhancement:**
- After all phases complete, collect phase outcome summary dict from `state_mgr.state`
- Feed as `phase_outcomes_bytes` into `PipelineDependencies` (new optional field)
- `meta_learning_pipeline.run_pipeline()` unpacks and attaches to snapshot for proposers to consume
- Enables proposers to see: "LocationHealer fixed 5 violations in apps_lic but 0 in apps_rg" → adjust routing

**Files touched:**
- `agentic_core/L0_routing/scripts/_ssot_meta_learning.py` — collect + serialize phase outcomes
- `system_learning/pipelines/meta_learning_pipeline.py` — add `phase_outcomes_bytes` to `PipelineDependencies`

**Contract:** Read-only from state_mgr; proposal-only output.

---

### #3 — Healing Pattern Advisor: ADG Hotspot-Aware Priority Boost

**Domain:** ADG → System Learning
**Value:** High — failures in high-fan-out modules have wider blast radius
**Current gap:** `DefaultHealingPatternAdvisor.advise()` returns `PatternAdvice` with `pattern_boost` based only on historical healing rates. No awareness of architectural risk.

**Enhancement:**
- Query `ADGHotspot` entities from Memory MCP for the failing module
- If module is a top-20 fan-out hotspot → add `reason_code="adg_hotspot"` + boost multiplier (capped by `_MAX_PATTERN_BOOST`)
- `BaseHealingOrchestrator.ml_heal_with_learning_enhanced()` already consumes `PatternAdvice` — no wiring changes needed downstream

**Files touched:**
- `system_learning/engines/default_healing_pattern_advisor.py` — add hotspot query + boost
- `agentic_core/adg/adapters/ADGMemoryAdapter.py` — expose `get_hotspot_modules()` helper

**Contract:** Informational-only (C0). Boost is advisory, cannot change routing tiers.

---

### #4 — Optimization Proposal Engine: ADG Repair Route Feed

**Domain:** ADG → System Learning
**Value:** High — connects static detection to dynamic optimization
**Current gap:** `optimization_proposal_engine.py` has templates for `POLICY_VIOLATION` and `NEG_SEED_ANTIPATTERN` but these trigger only from runtime signals. The 10 critical ADG violations already have `recommended_agent` and `ci_lane` from `RepairRoute` — but this data never reaches the proposal engine.

**Enhancement:**
- Feed `repair_routing_summary()` output as a new `RepairRouteCluster` into the optimization engine
- Map each `RepairRoute` (violation_type, severity, recommended_agent) to an `OptimizationProposal`
- Closes: static ADG detects → repair route classifies → optimizer proposes → system learning tracks outcome

**Files touched:**
- `system_learning/engines/optimization_proposal_engine.py` — add `RepairRouteCluster` handling
- `agentic_core/L0_routing/scripts/_ssot_meta_learning.py` — serialize repair routes into pipeline deps

**Contract:** Proposal-only. Human/gate approval required.

---

### #5 — Shadow Drift Analyzer: ADG Violation Trend as Drift Dimension

**Domain:** ADG → System Learning
**Value:** High — structural regression is invisible to embedding-only drift
**Current gap:** `ShadowDriftAnalyzer` computes drift from embedding cosine similarity only. If violations grow between ADG builds (10→15), no drift signal fires.

**Enhancement:**
- Compare `ADGSnapshot` violation counts across Memory MCP snapshots (current vs. previous)
- New drift dimension: `violation_delta` = current_violations - previous_violations
- If `violation_delta > 0` → emit `drift_flag=True` with `drift_source="adg_structural"`
- Folds into existing `DriftSummary` → `PolicyRecommendationEngine` already consumes it

**Files touched:**
- `system_learning/engines/shadow_drift_analyzer.py` — add violation trend dimension
- `system_learning/adapters/system_learning_memory_bridge.py` — expose `get_latest_violation_counts()`

**Contract:** Informational-only. No automatic mutation.

---

### #6 — Execute_SSOT: ADG Behavioral Score → Routing Confidence

**Domain:** Execute_SSOT → System Learning
**Value:** Medium-High — ADG already computes per-territory risk scores
**Current gap:** `execute_ssot.py` Phase 1 calls `build_pre_run_report()` and stores `adg_territory_score` in `state_mgr.state` — but this score is never forwarded to `l0_routing_confidence_monitor.py`. The confidence monitor tracks routing confidence independently, blind to ADG's view.

**Enhancement:**
- After Phase 1, emit `adg_territory_score` as a signal to `HealingSuccessRateStore` keyed by territory
- `l0_routing_confidence_monitor.py` reads this alongside its own signals
- If ADG score < threshold (e.g., `risk_score > 0.7`) → lower routing confidence for that territory

**Files touched:**
- `agentic_core/L0_routing/scripts/_ssot_meta_learning.py` — forward behavioral score
- `system_learning/engines/l0_routing_confidence_monitor.py` — consume ADG score

**Contract:** Informational. Score is one input among many; cannot unilaterally change routing.

---

### #7 — apps_* Domain Healing: Cross-Domain Pattern Sharing

**Domain:** apps_* → System Learning
**Value:** Medium-High — patterns learned in apps_lic should help apps_rg
**Current gap:** `BaseHealingOrchestrator._persist_healing_cycle()` writes to `GraphMemoryBridge` (Memory MCP) but each domain (LIC, RG, eval, exec, research, rfp) writes to its own entity namespace. The `meta_learning_pipeline` only sees outcomes from `_fire_meta_learning_intake` in execute_ssot, which doesn't include app-domain healing cycles.

**Enhancement:**
- `BaseHealingOrchestrator._persist_healing_cycle()` additionally emits a `HealingOutcomeEvent` to a shared cross-domain bus
- `_fire_meta_learning_intake` or `meta_learning_pipeline` consumes these events via `PipelineDependencies.cross_repo_learning_context` (field already exists but is always `None`)
- Pattern analysis can then detect: "structural violations in HOPPipelineExecutor follow same pattern as gravity violations in apps_rg"

**Files touched:**
- `apps_shared/reasoning/BaseHealingOrchestrator.py` — emit cross-domain healing events
- `system_learning/pipelines/pipeline_factory.py` — wire `cross_repo_learning_context` from Memory MCP

**Contract:** Informational context only. Existing C0 contract preserved.

---

### #8 — Execute_SSOT: Cognitive Disposition → RCA Enrichment

**Domain:** Execute_SSOT → System Learning
**Value:** Medium — cognitive analysis adds nuance to failure classification
**Current gap:** Phase 1 stores `cognitive_dispositions` on `state_mgr.state` (from `CognitiveDispositionAgent`). These contain enhanced violation analysis with cognitive framing. But `rca_engine.analyze_failures()` never sees them — it only gets raw audit bytes.

**Enhancement:**
- Serialize `cognitive_dispositions` as supplementary evidence attached to the audit slice
- `rca_engine` recognizes cognitive disposition markers → creates richer `RCAFinding` with `cognitive_category` field
- System learning can then track: "violations with cognitive_category=anchoring_bias have 30% lower heal rate"

**Files touched:**
- `agentic_core/L0_routing/scripts/_ssot_meta_learning.py` — append cognitive dispositions to audit
- `system_learning/engines/rca_engine.py` — add cognitive classification rules

**Contract:** Deterministic parsing. No randomness.

---

### #9 — apps_* Telemetry: OpenTelemetry Span → System Learning Telemetry Store

**Domain:** apps_* → System Learning
**Value:** Medium — structured telemetry replaces log scraping
**Current gap:** `apps_shared/utils/open_telemetry_tracing_adapter_util.py` produces structured spans (timing, errors, retries) but these are consumed only by the OTel exporter. The `TelemetryStore` protocol in `meta_learning_pipeline.py` reads from a separate telemetry store. No bridge exists.

**Enhancement:**
- Add an `OTelTelemetryStoreAdapter` that implements the `TelemetryStore` protocol
- Reads OTel spans from the local exporter and converts to `(timestamp, event_type, payload_bytes)` tuples
- Wire into `PipelineDependencies.telemetry_store` via `pipeline_factory.build_pipeline_deps()`
- System learning gets structured timing, error rates, and retry patterns from real app executions

**Files touched:**
- `system_learning/adapters/` — new adapter (or extend existing)
- `system_learning/pipelines/pipeline_factory.py` — wire adapter
- `apps_shared/utils/open_telemetry_tracing_adapter_util.py` — expose span buffer

**Contract:** Read-only from OTel. No mutation.

---

### #10 — ADG Confidence Tiers → L0 Routing Confidence Monitor

**Domain:** ADG → System Learning
**Value:** Medium — the static graph itself has confidence issues (443K low > 314K high)
**Current gap:** `l0_routing_confidence_monitor.py` monitors routing confidence but has zero visibility into the ADG's E9 confidence tiers. When the static graph has more low-confidence edges than high-confidence edges, the confidence monitor doesn't know.

**Enhancement:**
- After ADG build, persist `conf_summary` (high/medium/low counts, avg) as `SLDriftSummary` entity type
- `l0_routing_confidence_monitor.py` reads this at startup as a baseline confidence signal
- When `low_count > high_count` → emit informational warning that graph confidence is degraded

**Files touched:**
- `tools/generate_full_adg.py` — persist confidence summary to Memory MCP
- `system_learning/engines/l0_routing_confidence_monitor.py` — read and factor in ADG confidence

**Contract:** Informational only. Cannot unilaterally modify thresholds.

---

## Priority Matrix

| # | Enhancement | Domain | Value | Effort | Risk |
|---|-------------|--------|-------|--------|------|
| 1 | RCA ↔ ADG Violation Correlation | ADG | **Highest** | Low | Low |
| 2 | Execute_SSOT Phase Outcome Feedback | SSOT | **Very High** | Medium | Low |
| 3 | Hotspot-Aware Healing Priority | ADG | **High** | Low | Low |
| 4 | Repair Route → Optimization Proposals | ADG | **High** | Medium | Low |
| 5 | Violation Trend as Drift Dimension | ADG | **High** | Low | Low |
| 6 | ADG Behavioral Score → Routing Confidence | SSOT | **Med-High** | Low | Low |
| 7 | Cross-Domain Pattern Sharing | apps_* | **Med-High** | Medium | Medium |
| 8 | Cognitive Disposition → RCA Enrichment | SSOT | **Medium** | Medium | Low |
| 9 | OTel Spans → Telemetry Store | apps_* | **Medium** | High | Medium |
| 10 | ADG Confidence Tiers → L0 Monitor | ADG | **Medium** | Low | Low |

## Implementation Order (Recommended)

**Wave A — Quick wins, low effort, high value (1 session each):**
- #1, #3, #5, #6, #10

**Wave B — Medium effort, requires pipeline wiring (2-3 sessions each):**
- #2, #4, #8

**Wave C — Larger effort, cross-cutting (3-5 sessions each):**
- #7, #9

## Common Design Contracts (All 10)

1. **Informational-only (C0)** — no automatic mutation of routing tiers or safety configs
2. **Proposal-only outputs** — human/gate approval required for any config change
3. **Resilient** — upstream unavailability (ADG, Memory MCP, OTel) = skip, never crash
4. **Deterministic** — same inputs → same outputs; no wall-clock reads
5. **Backward compatible** — all new parameters are optional with sensible defaults

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

