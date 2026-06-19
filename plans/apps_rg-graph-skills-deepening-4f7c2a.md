---
plan_id: apps_rg-graph-skills-deepening-4f7c2a
plan_format: v2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# Graph Skills Deepening and Confidence Scoring

Improve the graph skills SSOT so competencies, headline, and executive summary can express more granular, better-validated evidence without inventing facts or overfitting to vendor labels.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-06-20

---

## Context (SCQA)

- **Situation** — `apps_rg` already has a graph-backed competencies pipeline with section-level semantic coverage, employer routing, and fail-closed evidence selection.
- **Complication** — Several competencies and shared sections still collapse into broad or vendor-specific phrasing, reuse the same few metrics, and do not expose a per-bullet confidence signal. The graph can therefore look “present” while remaining too thin to justify the exact wording it emits.
- **Question** — How do we deepen the graph skills SSOT so the resume can stay graph-grounded, more specific, and more trustworthy at the bullet level?
- **Answer** — Split overloaded capability nodes, enrich evidence density, add per-bullet confidence/weakest-link scoring, and harden deterministic gates so thin graph areas fail visibly instead of being padded by LLM wording.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Graph taxonomy decomposition and vendor-neutral capability labels | ~12K | Existing graph rows and employer bundles are the SSOT baseline | 🔲 TODO | Weak capability clusters are split into finer nodes without losing provenance |
| W2 | W2.1, W2.2, W2.3 | Evidence densification and per-bullet confidence scoring | ~16K | The pipeline can carry extra metadata from graph selection to final competencies | 🔲 TODO | Each competency category emits confidence, weakest-link, and support ratios |
| W3 | W3.1, W3.2 | Gates and regression tests for graph depth, uniqueness, and anti-overfit | ~14K | Current section and X2/X3 gates can be extended without changing product flow | 🔲 TODO | Thin graph areas fail closed and new regressions are covered by tests |
| W4 | W4.1, W4.2 | Calibration, before/after reporting, and documentation writeback | ~10K | We can compare pre/post artifacts on one or more representative JDs | 🔲 TODO | The plan proves measurable improvement rather than subjective cleanup |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Split overloaded capability nodes | 🔲 TODO |
| W1.2 | Remove vendor leakage from generic labels | 🔲 TODO |
| W2.1 | Add per-bullet confidence fields | 🔲 TODO |
| W2.2 | Add weakest-link and support-ratio metrics | 🔲 TODO |
| W2.3 | Thread JD/briefing overlap into scoring | 🔲 TODO |
| W3.1 | Add graph-depth and repetition gates | 🔲 TODO |
| W3.2 | Add regression tests for weak graph families | 🔲 TODO |
| W4.1 | Run calibration on representative JDs | 🔲 TODO |
| W4.2 | Publish summary to SSOT and Notion | 🔲 TODO |

---

## Out Of Scope

- Rewriting the core apps_rg generation flow.
- Changing the JD/briefing contract so they become proof sources.
- Adding silent fallback paths that invent evidence when the graph is thin.
- Broad resume redesign unrelated to graph skills quality.

---

## Wave 1 — Taxonomy Decomposition

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — Split overloaded capability clusters into narrower nodes with single-purpose labels | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Rewrite or retire vendor-specific generic labels so vendor names appear only when the graph truly supports them | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- The graph has finer-grained nodes for the weak families we identified, especially `Data & Analytics Modernization` and `Cloud & Partner Ecosystems`.
- Capability labels read as capabilities, not as incidental certifications or platform brands.
- Source evidence, fact IDs, and allowed phrases remain intact for every new or revised node.

### W1.1 — Split Overloaded Capability Nodes

**Scope**:
- Break broad graph nodes into smaller nodes where the current wording is doing too much work.
- Prioritize weak clusters first:
- `Data & Analytics Modernization`
- `Cloud & Partner Ecosystems`
- `Commercial & Operating Impact`
- `Engineering & Delivery Leadership`
- `LLMOps & Reliability`

**Expected output**:
- More distinct capability nodes with one dominant meaning each.
- Clearer mapping from employer bundles to the right capability family.

**Commands**:
- Update the taxonomy file under `apps_rg/config/competencies/`.
- Update graph skill evidence sources in `apps_rg/fact_inventory/`.
- Add or revise unit tests around taxonomy resolution and capability mapping.

### W1.2 — Remove Vendor Leakage From Generic Labels

**Scope**:
- Audit where vendor names are being surfaced as a shorthand for a broader capability.
- Keep `Databricks`, `AWS`, or similar labels only when the graph evidence is actually vendor-specific and useful to the JD.

**Expected output**:
- Vendor terms no longer dominate generic competency labels.
- The graph can express `lakehouse modernization` or `data cataloging` without always collapsing to `Databricks`.

**Commands**:
- Update projection synonyms and label resolution logic.
- Add tests that distinguish “capability label” from “vendor-supported evidence.”

---

## Wave 2 — Evidence Densification

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Add per-bullet confidence scoring based on graph support, JD overlap, and briefing overlap | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Add weakest-link and support-ratio fields to each competency category | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** — Add metric diversity and uniqueness penalties so repeated metrics do not masquerade as depth | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Every competency category can report a confidence score and a reason for that score.
- Each category can expose the weakest link, not just the final text.
- Reused metrics reduce confidence instead of inflating it.

### W2.1 — Add Per-Bullet Confidence Scoring

**Scope**:
- Introduce a structured confidence field for each competency category.
- Combine multiple inputs:
- graph skill support density
- fact support density
- metric support density
- JD overlap
- briefing overlap
- repetition penalties

**Proposed shape**:
- `graph_match_confidence`: 0.0 to 1.0
- `jd_overlap_pct`: 0.0 to 1.0
- `briefing_overlap_pct`: 0.0 to 1.0
- `graph_skill_density`: unique skill IDs divided by term count

**Expected output**:
- A category can be “good but thin” instead of merely passing or failing.
- The pipeline can show why a given bullet was selected.

### W2.2 — Add Weakest-Link Reporting

**Scope**:
- Emit the weakest supporting term or fact for each category.
- Surface whether the weak point is:
- a low-support term
- a repeated metric
- a vendor-specific phrase
- a category with too few unique facts

**Expected output**:
- The team can inspect the exact failure mode without replaying the whole run.
- The graph can be improved surgically instead of by guesswork.

### W2.3 — Add Diversity and Repetition Penalties

**Scope**:
- Penalize repeated metric use across categories.
- Penalize too many categories using the same skill node family.
- Penalize vendor-specific overfitting when the JD did not ask for it.

**Expected output**:
- The system rewards breadth across distinct facts and metrics.
- “Same three metrics over and over” no longer looks like deep coverage.

---

## Wave 3 — Gates and Tests

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Add deterministic gates for thin graph families and repeated metric surfaces | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Add regression tests for the exact weak cases we care about | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- If the graph cannot support a phrase, the run fails closed instead of inventing a close-looking substitute.
- Tests prove the failure modes we want to catch.
- The plan prevents regressions in the same weak families that surfaced in review.

### W3.1 — Add Deterministic Gates

**Scope**:
- Add or tighten gates for:
- minimum unique fact count per category
- minimum unique metric count per category
- repeated metric reuse ratio
- skill diversity ratio
- vendor leakage in generic capability categories
- unsupported over-specific labels when the graph is thin

**Expected output**:
- Thin categories fail visibly.
- Support gaps are caught before prose generation.

### W3.2 — Add Regression Tests

**Scope**:
- Add tests that directly exercise:
- `Databricks` appearing only when graph-supported
- vendor-neutral `Data & Analytics Modernization`
- `Cloud & Partner Ecosystems` mechanics like co-sell, enablement, and technical close
- `LLMOps & Reliability` with distinct evaluation/reliability/telemetry nodes
- repeated metric reuse failing the new gates

**Expected output**:
- The graph is forced to grow in breadth and depth.
- The tests document what “good” looks like.

---

## Wave 4 — Calibration and Writeback

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — Run before/after calibration on representative JDs and briefings | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** — Write the final summary back to SSOT and mirror the result into Notion | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- The plan can prove a delta, not just a theory.
- Calibration outputs show improvement in graph depth and confidence.
- The SSOT and Notion copies stay aligned.

### W4.1 — Calibration Runs

**Scope**:
- Compare pre/post on at least two prompts:
- Anthropic partnership JD
- one unrelated senior engineering JD
- Measure:
- semantic coverage
- axis coverage
- unique skill count
- unique metric count
- repeated metric ratio
- per-category confidence

**Expected output**:
- The team can see whether the graph improved or simply changed wording.

### W4.2 — Writeback and Mirror

**Scope**:
- Update the SSOT plan status after implementation.
- Create or update the Notion page with the same plan content.
- Preserve the final before/after metrics as a durable record.

**Expected output**:
- One plan source of truth in-repo.
- One mirrored operational copy in Notion.

---

## Execution Details

### W1.1 — Split Overloaded Capability Nodes
**Scope**: Narrow the capability taxonomy and graph nodes in the weak families.

**Commands**:
- Edit `apps_rg/config/competencies/executive_capability_taxonomy.yaml`
- Edit graph skill inventory files under `apps_rg/fact_inventory/`
- Update mapping tests under `tests/unit/apps_rg/`

### W1.2 — Remove Vendor Leakage
**Scope**: Make generic competencies read as capabilities, not vendor brands.

**Commands**:
- Edit `apps_rg/runtime/sections/competencies_capability_projection.py`
- Edit `apps_rg/runtime/sections/competencies_lane_runtime.py`
- Add regression tests for vendor-neutral wording

### W2.1 — Add Per-Bullet Confidence
**Scope**: Carry confidence and overlap metrics through final competency output.

**Commands**:
- Edit `apps_rg/runtime/sections/graph_evidence_contract.py`
- Edit `apps_rg/runtime/sections/graph_role_episode_selector.py`
- Edit `apps_rg/runtime/sections/competencies_lane_execution.py`

### W2.2 — Add Weakest-Link Reporting
**Scope**: Surface the exact weak term, fact, or metric in each category.

**Commands**:
- Extend section output JSON schemas
- Update display formatting and diagnostic receipts

### W2.3 — Add Diversity and Repetition Penalties
**Scope**: Penalize reused metrics and repeated skill-node families.

**Commands**:
- Update selector scoring functions
- Add gates for repeated detail reuse
- Add tests for repeated-metric failure

### W3.1 — Add Deterministic Gates
**Scope**: Fail on thin graph categories and unsupported phrasing.

**Commands**:
- Edit X2 gates in `apps_rg/runtime/validators/competencies_x2.py`
- Edit supporting rigor checks in `apps_rg/runtime/sections/competencies_rigor.py`

### W3.2 — Add Regression Tests
**Scope**: Lock down the exact failures this review surfaced.

**Commands**:
- Add tests under `tests/unit/apps_rg/`
- Add coverage for vendor leakage, thin graph, and repeated metric surfaces

### W4.1 — Calibration Runs
**Scope**: Compare output before and after the graph improvements.

**Commands**:
- Run focused e2e competencies tests
- Collect calibration artifacts and compare metrics

### W4.2 — Writeback and Mirror
**Scope**: Publish the final plan state.

**Commands**:
- Update this SSOT file
- Update Notion page

---

## Gap Register

**GAP-1: Vendor-specific overfitting**
- `Databricks` can appear when the graph has a cert-anchored node, even when the category should stay vendor-neutral.
- Impact: weakens portability and makes the competency read narrower than the JD requires.

**GAP-2: Reused metrics masquerading as depth**
- The same metric surfaces can appear repeatedly across categories.
- Impact: section looks rich but is not actually diverse.

**GAP-3: No per-bullet confidence**
- Current reporting is too coarse to tell whether a specific category is strong or merely passable.
- Impact: weak nodes can hide inside an overall passing run.

**GAP-4: Limited weakest-link diagnostics**
- Current depth reporting is section-level rather than bullet-level.
- Impact: harder to fix the graph precisely.

---

## Definition of Done

DoD-1: Graph taxonomy is deeper and less vendor-biased
- Evidence: taxonomy diff plus regression tests for vendor-neutral labels and specific vendor phrases.
- Status: TODO

DoD-2: Competency output includes per-bullet confidence and weakest-link diagnostics
- Evidence: focused e2e run shows `graph_match_confidence`, `jd_overlap_pct`, `briefing_overlap_pct`, and `weakest_link`.
- Status: TODO

DoD-3: Thin graph cases fail closed
- Evidence: tests show unsupported phrases and repeated metric surfaces are rejected.
- Status: TODO

DoD-4: Calibration shows measurable improvement
- Evidence: before/after report with semantic coverage, axis coverage, unique skill count, unique metric count, and repetition ratio.
- Status: TODO

DoD-5: SSOT and Notion copies are synchronized
- Evidence: `plans/apps_rg-graph-skills-deepening-4f7c2a.md` and the mirrored Notion page match.
- Status: TODO

---

## Scope Expansion Authorization

When implementation uncovers adjacent graph weak spots, expand only if the issue directly affects competency evidence quality or the shared headline/executive-summary graph path.

```
DISCOVERED_SCOPE: plan=apps_rg-graph-skills-deepening-4f7c2a wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=apps_rg-graph-skills-deepening-4f7c2a decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=apps_rg-graph-skills-deepening-4f7c2a reason="<summary>" added="<waves/phases>" authorized="yes"
```
