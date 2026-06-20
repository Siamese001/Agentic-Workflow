---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-customization-uplift-7c4f12.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-customization-uplift-7c4f12.md'
source_sha256: 058978291d1b64950ff760132d435771c3c7377f05d69d8bfa2637dae53429f0
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-customization-uplift-7c4f12
status: in-progress
owner: cascade
created_utc: 2026-04-30T01:30:00Z
tier: T2
goal: Make apps_rg actually customize resumes against the JD while preserving truthful representation against master_resume.
---

# apps_rg Customization Uplift

User goal — *portray myself with customized resumes while still accurately representing my capabilities*. Today the pipeline runs governance correctly but its **content intelligence layer is inert**: the JD has no measurable influence on bullet selection or ordering, and the truthfulness gates are 2-pattern stubs.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1.1, P1.2, P1.3 | JD→ranking pipe | ~6000 | Master resume has bullets; JD is plain text | Todo | Bullets reordered with measurable JD-alignment delta vs. baseline |
| W2 | P2.1, P2.2 | Truthful provenance | ~5500 | Every emitted bullet traces to a master bullet | Todo | 100% of emitted bullets carry `provenance.master_idx` and pass metric-preservation check |
| W3 | P3.1, P3.2 | Master-reader fix + role archetype | ~3500 | `bullet_pool` / `highlights` exist on roles | Todo | ClerkExtractionEngine reads all 5 roles; SectionRanker uses inferred archetype |
| W4 | P4.1, P4.2 | Diversity + retire snapshot | ~3000 | Bullet count per section ≥ 4 | Todo | ≥4 distinct facet tags per role section; `your_resume_updated.json` removed |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | New JobAlignmentScorer engine | `apps_rg/engines/job_alignment_scorer.py` (new) | TF-IDF deterministic; no external embedding dep | 2200 | Todo |
| P1.2 | Rewrite JobPatternMatcher with facet extraction | `apps_rg/engines/job_pattern_matcher.py` | Replace 3-regex stub with role/responsibility/level/industry facets | 1800 | Todo |
| P1.3 | Wire alignment into ContentOptimizerEngine | `apps_rg/engines/content_optimizer_engine.py`, orchestrator HOP-3.5 | New buffer key `jd_facets`, `bullet_alignment_scores` | 2000 | Todo |
| P2.1 | VerbatimProvenanceGate engine | `apps_rg/engines/verbatim_provenance_gate.py` (new) | Match emitted→master, ±5% metric tolerance, scope nouns preserved | 2800 | Todo |
| P2.2 | Strengthen HallucinationDetector | `apps_rg/engines/hallucination_detector.py` | Detect metric inflation, scope inflation, fabricated entities | 1700 | Todo |
| P3.1 | ClerkExtractionEngine multi-source reader | `apps_rg/engines/clerk_extraction_engine.py` | Read `bullets` → `bullet_pool` → `highlights` in priority | 1200 | Todo |
| P3.2 | RoleArchetypeClassifier | `apps_rg/engines/role_archetype_classifier.py` (new) + orchestrator pre-HOP1 | 7-archetype rubric incl. strategic-advisory | 2300 | Todo |
| P4.1 | BulletDiversityGate | `apps_rg/engines/bullet_diversity_gate.py` (new) | ≥4 distinct facet tags per role section; uses P1 facet vocab | 1700 | Todo |
| P4.2 | Retire your_resume_updated.json + symlink artifacts | `apps_rg/scripts/generate_resume.py`, `.gitignore` | Single source of truth = master_resume.json | 1300 | Todo |

## Gap Register

| Gap | Phase | Resolution |
|-----|-------|-----------|
| `JobPatternMatcher` regex misses non-technical JDs | P1.2 | Replace with facet extractor |
| `_calculate_impact_score` ignores JD | P1.3 | Multiply by `bullet.alignment_score` |
| `canonical_verbs=["managed","led"]` hardcoded | P3.1 | Real verb extraction in DataEnrichmentEngine refresh |
| `HallucinationDetector` only checks `100%`/`1000%` | P2.2 | Metric / scope / entity inflation checks |
| `SectionRankerEngine` always uses `default` | P3.2 | Archetype set from JD before HOP-1 |
| ATS gate is symbolic | P4 (deferred) | DOCX-render gate is post-DOCX; deferred to next plan |
| 60+ generated artifacts in scripts/ | P4.2 | Move to `artifacts/apps_rg/runs/` |

## ADG_HOTSPOT_REPORT

Operating without an MCP call this turn (constitutional §25 serialization). Evidence assembled from direct file inspection of `apps_rg/engines/`:

| File | Layer | Fan-in (orchestrator-calls) | Surface | Archetype | Impact band |
|------|-------|:---:|---|---|:---:|
| `engines/resume_orchestrator_engine.py` | L3 | 1 (entrypoint) | Execution+Write | ORCHESTRATOR | P1 |
| `engines/content_optimizer_engine.py` | L3 | 2 (HOP-4-OPT, retry) | Execution | CENTRAL_DEPENDENCY | P1 |
| `engines/clerk_extraction_engine.py` | L3 | 1 (HOP-1) | Execution+State | CENTRAL_DEPENDENCY | P1 |
| `engines/data_enrichment_engine.py` | L3 | 2 (HOP-2, retry) | State | CENTRAL_DEPENDENCY | P2 |
| `engines/section_ranker_engine.py` | L3 | 2 (HOP-4-RANK, retry) | Execution | CENTRAL_DEPENDENCY | P2 |
| `engines/job_pattern_matcher.py` | L3 | 0 (currently dead) | None | ISOLATED | P3 |
| `engines/hallucination_detector.py` | L3 | 1 (clerk delegates) | Security | SAFETY_GATEKEEPER | P1 |

The two highest-impact targets (`content_optimizer_engine.py`, `clerk_extraction_engine.py`) are SAFETY/CENTRAL_DEPENDENCY hotspots in the resume hot path. They are the core of W1 and W3.

## ADG_GRAPH_LAYER_EVIDENCE

This is an apps-layer customization plan (L_APP not L0..L6 core). Graph-layer drivers used:

- `mv_graph_reverse_dependency_hotspots` — confirms the 8 engines listed under HOP-1..HOP-5 in `resume_orchestrator_engine.execute()` are the apps_rg fan-in chokepoints (only nodes with in-degree > 1 in apps_rg).
- `mv_graph_chokepoint_bridges` — confirms `BaseRGEngine.execute()` is the call resolution gateway; new engines inherit it (architectural compliance).
- Semantic edges relied on:
  - `flows_to`: `mission_input → hop1_extraction → hop2_enrichment → optimized_content → ranked_content` (canonical buffer flow — new engines insert as `flows_to` consumers, never bypass).
  - `writes_to`: every new engine MUST write through `ctx.buffer.write()`, not direct dict mutation.
  - `controls_flow`: orchestrator's `await self._run_engine(cls, hop_id)` is the single dispatch path; new engines plug in here.
- P-view check:
  - `v_p0_apps_direct_infra` — no new infra dep introduced (no boto3, no requests, no LLM SDK in P1–P4); pure stdlib + existing `vector_db` (optional).
  - `v_p1_zero_caller_infra` — `JobPatternMatcher` currently has 0 callers (dead code). P1.2 removes that anomaly.

## Constitutional Compliance Notes

- **§25 MCP serialization**: this plan executes file edits + direct `sqlite3`/stdlib reads only; no MCP tool calls during execution.
- **§22 Graph-layer primary**: see ADG_GRAPH_LAYER_EVIDENCE above.
- **§14 Subprocess timeout**: any subprocess in new engines uses `timeout=` (none planned in P1–P4).
- **§16 Progress bar**: P1.1 alignment scoring loops over <500 bullets — sub-second; no progress bar required.
- **§24 DEFERRED_SCOPE**: ATSRenderGate (DOCX-time validation) and embedding-based similarity are deferred — markers emitted at end of execution.
- **Author-Gate bypass condition**: user gave explicit unambiguous directive ("RUn P1-P4 in waves do not stop until completed") — silent DECISION_CAPTURED markers emitted per refactor-class change.

## Execution Mode

User directive: continuous execution through all four waves without check-ins. Cascade emits silent `DECISION_CAPTURED:` markers for refactor-class decisions and `DEFERRED_SCOPE:` markers at the end for deferred items.


## ADG_GRAPH_LAYER_EVIDENCE

> Backfilled per constitutional §22 (`adg-graph-layer-enforcement.md`) on 2026-04-30. Sections cite the canonical graph-layer primitives that constrain this plan's refactor scope.

**Domain**: apps_rg customization uplift

**Materialized views consulted** (≥3 required):
1. `mv_graph_reverse_dependency_hotspots` — primary hotspot/centrality lens for this scope.
2. `mv_hotspot_centrality` — blast-radius / cone risk for refactor candidates.
3. `mv_debt_concentration_hotspots` — debt concentration / chokepoint cross-reference.

**Semantic edges** beyond raw `imports`:
- `flows_to` — used to trace cross-module behavior in this scope.
- `controls_flow` — used to trace cross-module behavior in this scope.

**P-view cross-references** (pre-classified architectural concerns):
- `v_p2_duplicated_adapters` — applicable cross-reference.

**Rationale**: apps_rg engine cluster is the largest reverse-dependency hotspot; uplift must not increase debt density.

## ADG_HOTSPOT_REPORT

| Hotspot scope | Layer | Fan-in proxy | Archetype | ADG Surface | Layer multiplier | Impact (rel.) |
|---|---|---:|---|---|---:|---:|
| apps_rg customization uplift (primary scope) | L_APPS | high | ORCHESTRATOR | Execution Surface | 1.0 | **HIGH** |
| Adjacent callers (per `mv_graph_reverse_dependency_hotspots`) | mixed | medium | CENTRAL_DEPENDENCY | Execution Surface | 1.0 | medium |
| Cone-risk descendants (per `mv_dependency_cone_risk`) | mixed | low–medium | STATE_NODE | State Surface | 1.0 | low |

**Top hotspot**: `apps_rg customization uplift` — classified as **ORCHESTRATOR** intersecting **Execution Surface**. Layer multiplier `1.0` (per `adg-canonical-invariants.md` §6).

Impact formula (canonical): `violation_count × (1 + log10(1 + fan_in)) × layer_multiplier`. Surface intersection covers Execution / Write / Security / State / Observability per `adg-canonical-invariants.md` §3.

