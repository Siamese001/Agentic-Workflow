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

# Competencies Graph Skills Deepening and Confidence Scoring

Improve the graph skills SSOT so competencies can express more granular, better-validated evidence without inventing facts or overfitting to vendor labels. Headline and executive summary may consume the shared graph-depth report, but their gates and output schemas are out of scope until a separate scoped wave or plan names them explicitly.

---

## Plan State Markers

FORMAT_VERSION: plan-format-v2
PLAN_STATUS: DONE
CURRENT_WAVE: COMPLETE
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-06-19

---

## Context (SCQA)

- **Situation** — `apps_rg` already has a graph-backed competencies pipeline with section-level semantic coverage, employer routing, and fail-closed evidence selection.
- **Complication** — Several competencies still collapse into broad or vendor-specific phrasing, reuse the same few metrics, and do not expose category/term confidence. The graph can therefore look "present" while remaining too thin to justify the exact wording it emits.
- **Question** — How do we deepen the graph skills SSOT so competencies stay graph-grounded, more specific, and more trustworthy at the category and term layer?
- **Answer** — First harden the scoring and gate contracts, then split overloaded capability nodes, enrich evidence density, add category/term confidence and weakest-link scoring, and harden deterministic gates so thin graph areas fail visibly instead of being padded by LLM wording.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1, W0.2, W0.3, W0.4 | Contract-first hardening before taxonomy work | ~8K | Existing graph-depth report and X2 gates are the right seams | DONE | Plan, scoring schema, thresholds, and bundle loophole are explicit and test-backed |
| W1 | W1.1, W1.2 | Graph taxonomy decomposition and vendor-neutral capability labels | ~12K | Existing graph rows and employer bundles are the SSOT baseline | DONE | Weak capability clusters are split into finer nodes without losing provenance |
| W2 | W2.1, W2.2, W2.3 | Evidence densification and category/term confidence scoring | ~16K | The pipeline can carry extra metadata from graph selection to final competencies | DONE | Each competency category emits confidence, weakest-link, and support ratios |
| W3 | W3.1, W3.2 | Gates and regression tests for graph depth, uniqueness, and anti-overfit | ~14K | Current section and X2/X3 gates can be extended without changing product flow | DONE | Thin graph areas fail closed and new regressions are covered by tests |
| W4 | W4.1, W4.2 | Calibration, before/after reporting, and documentation writeback | ~10K | We can compare pre/post artifacts on one or more representative JDs | DONE | The plan proves measurable improvement rather than subjective cleanup |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Resolve plan format and scope | DONE |
| W0.2 | Define category/term/claim confidence schema | DONE |
| W0.3 | Close bundle-binding and coverage authority loopholes | DONE |
| W0.4 | Name deterministic CI/test gates and thresholds | DONE |
| W1.1 | Split overloaded capability nodes | DONE |
| W1.2 | Remove vendor leakage from generic labels | DONE |
| W2.1 | Add category/term confidence fields | DONE |
| W2.2 | Add weakest-link and support-ratio metrics | DONE |
| W2.3 | Thread JD/briefing overlap into scoring | DONE |
| W3.1 | Add graph-depth and repetition gates | DONE |
| W3.2 | Add regression tests for weak graph families | DONE |
| W4.1 | Run calibration on representative JDs | DONE |
| W4.2 | Publish summary to SSOT | DONE |

---

## Out Of Scope

- Rewriting the core apps_rg generation flow.
- Changing the JD/briefing contract so they become proof sources.
- Adding silent fallback paths that invent evidence when the graph is thin.
- Broad resume redesign unrelated to graph skills quality.
- Headline or executive-summary gate/schema changes in this PR. Shared report fields may remain available to those lanes, but competencies are the only active enforcement scope.

---

## Wave 0 — Contract Hardening

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: W0

**Phases**:
- **W0.1** — Resolve plan-format conflict and narrow execution scope to competencies | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W0.2** — Define deterministic category/term/claim confidence schema on `graph_evidence_depth_report_v2` | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W0.3** — Close bundle-binding and capability-family authority loopholes | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W0.4** — Name CI/test gates, thresholds, and regression fixtures | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- The plan uses one format marker: frontmatter `plan_format: v2` plus body `FORMAT_VERSION: plan-format-v2`.
- Confidence is scoped to `category_graph_confidence`, `term_confidence_rows`, `claim_ledger_confidence`, `weakest_link`, and `support_ratio`; rendered resume bullet scoring is outside this plan.
- JD and briefing overlap are targeting signals only and cannot increase `proof_authority_score`.
- Generic categories require `competency_bundle_id`, category `graph_skill_node_ids`, at least three graph-backed terms, and term-level skill or fact support.
- Capability-family coverage uses bundle `capability_family` as authority when present; token matching is diagnostic/fallback only.

### W0.2 — Confidence Schema

Add or preserve this scoring shape on the shared depth report instead of creating a parallel metrics stack:

```json
{
  "schema": "graph_evidence_depth_report_v2",
  "category_id": "cloud_partner_ecosystems",
  "competency_bundle_id": "ccb_partnerships_ecosystem_execution",
  "category_graph_confidence": 0.86,
  "claim_ledger_confidence": 0.82,
  "proof_authority_score": 0.82,
  "targeting_fit_score": 0.64,
  "support_ratio": {
    "items_with_fact_support": 3,
    "items_with_skill_support": 3,
    "items_total": 4
  },
  "term_confidence_rows": [],
  "weakest_link": {
    "category_id": "cloud_partner_ecosystems",
    "term": "cloud partner ecosystem GTM",
    "reason": "repeated_metric",
    "source_fact_ids": ["fact_partner_001"],
    "graph_skill_node_ids": ["skill_partner_ecosystem"],
    "confidence": 0.71
  },
  "penalties": {
    "metric_reuse_penalty": 0.10,
    "vendor_overfit_penalty": 0.00,
    "generic_label_penalty": 0.00
  }
}
```

Weakest-link ranking is deterministic:

```text
weakness_score =
  missing_skill_axis * 0.30
+ missing_fact_or_metric_axis * 0.30
+ repeated_detail_penalty * 0.15
+ vendor_overfit_penalty * 0.15
+ jd_only_or_briefing_only_penalty * 0.10
```

### W0.4 — Named Gates and Thresholds

Required gate/test surfaces:
- `check_apps_rg_competency_confidence_schema.py` or equivalent pytest coverage for `graph_evidence_depth_report_v2`.
- `check_apps_rg_graph_bundle_depth_contract.py` or equivalent pytest coverage for bundle depth fields.
- `check_apps_rg_no_generic_category_bundle_loophole.py` or equivalent pytest coverage for the generic-category bundle loophole.
- `check_apps_rg_vendor_overfit_terms.py` or equivalent pytest coverage before W1/W2 vendor decomposition lands.

Thresholds:
- Generic competency category: minimum three graph-backed terms.
- Generic competency category: non-empty `competency_bundle_id`.
- Generic competency category: non-empty category `graph_skill_node_ids`.
- Term support: each counted graph-backed term has `source_skill_ids`, `graph_skill_node_ids`, or `source_fact_ids`.
- Metric/detail reuse: `detail_reuse_ratio`, `max_detail_frequency`, and repeated detail IDs are report fields and become hard X2 thresholds in W3.
- Vendor leakage: vendor terms require vendor-specific graph support plus targeting relevance; otherwise vendor-neutral phrasing wins.

---

## Wave 1 — Taxonomy Decomposition

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — Split overloaded capability clusters into narrower nodes with single-purpose labels | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Rewrite or retire vendor-specific generic labels so vendor names appear only when the graph truly supports them | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

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
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Add category/term confidence scoring based on graph support, JD overlap, and briefing overlap | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** — Add weakest-link and support-ratio fields to each competency category | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.3** — Add metric diversity and uniqueness penalties so repeated metrics do not masquerade as depth | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Every competency category can report a confidence score and a reason for that score.
- Each category can expose the weakest link, not just the final text.
- Reused metrics reduce confidence instead of inflating it.

### W2.1 — Add Category/Term Confidence Scoring

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
- `category_graph_confidence`: 0.0 to 1.0
- `claim_ledger_confidence`: 0.0 to 1.0
- `proof_authority_score`: 0.0 to 1.0; excludes JD/briefing targeting overlap
- `targeting_fit_score`: 0.0 to 1.0; JD/briefing targeting-only overlap
- `support_ratio`: fact/skill support counts over total items or terms

**Expected output**:
- A category can be “good but thin” instead of merely passing or failing.
- The pipeline can show why a given category or term was selected.

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
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Add deterministic gates for thin graph families and repeated metric surfaces | ~7K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** — Add regression tests for the exact weak cases we care about | ~7K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

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
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — Run before/after calibration on representative JDs and briefings | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.2** — Write the final summary back to SSOT | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- The plan can prove a delta, not just a theory.
- Calibration outputs show improvement in graph depth and confidence.
- The SSOT plan and durable calibration artifacts stay aligned.

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
- Completed evidence: `artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260619_215750/runtime_payload.json` contains `graph_evidence_depth_comparison_report_v1` with `7/8 rich items -> 8/8 rich items`, `semantic coverage 88% -> 100%`, `detail reuse 0% -> 0%`, and `improved: true`.

### W4.2 — Writeback

**Scope**:
- Update the SSOT plan status after implementation.
- Preserve the final before/after metrics as a durable record.

**Expected output**:
- One plan source of truth in-repo.
- Durable calibration artifacts referenced from this plan.
- This SSOT file now records the final DONE state for the plan.

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

### W2.1 — Add Category/Term Confidence
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

---

## Gap Register

**GAP-1: Vendor-specific overfitting**
- `Databricks` can appear when the graph has a cert-anchored node, even when the category should stay vendor-neutral.
- Impact: weakens portability and makes the competency read narrower than the JD requires.

**GAP-2: Reused metrics masquerading as depth**
- The same metric surfaces can appear repeatedly across categories.
- Impact: section looks rich but is not actually diverse.

**GAP-3: No category/term confidence**
- Current reporting is too coarse to tell whether a specific category or term is strong or merely passable.
- Impact: weak nodes can hide inside an overall passing run.

**GAP-4: Limited weakest-link diagnostics**
- Current depth reporting is section-level rather than bullet-level.
- Impact: harder to fix the graph precisely.

---

## Definition of Done

DoD-1: Taxonomy decomposition
- Evidence: `apps_rg/config/competencies/executive_capability_taxonomy.yaml` carries stable category IDs plus aliases; `apps_rg/fact_inventory/competency_capability_bundles.json` binds active bundles to capability families, graph skill node IDs, and linked source fact IDs.
- Status: DONE

DoD-2: Confidence scoring
- Evidence: `apps_rg/runtime/sections/graph_evidence_contract.py` emits `category_graph_confidence`, `claim_ledger_confidence`, `proof_authority_score`, `term_confidence_rows`, `support_ratio`, and penalties; contract tests cover the shape.
- Status: DONE

DoD-3: Weakest link
- Evidence: weakest-link ranking is deterministic and support-aware; `tests/unit/apps_rg/runtime/test_graph_evidence_contract.py` pins the lowest-support row instead of first position.
- Status: DONE

DoD-4: Bundle rigor
- Evidence: bundle ID, category graph skill IDs, and graph-backed terms are required together; `tests/unit/apps_rg/test_competencies_authority_gates.py` and `tests/unit/apps_rg/test_competencies_capability_bundle_wiring.py` cover the loophole closure.
- Status: DONE

DoD-5: Vendor leakage
- Evidence: vendor overlap affects targeting only, not proof authority, and vendor overfit penalties are surfaced in the depth report.
- Status: DONE

DoD-6: Metric reuse
- Evidence: repeated metrics are surfaced through `detail_reuse_ratio`, `max_detail_frequency`, and repeated detail IDs, with regression coverage in the graph-evidence contract tests.
- Status: DONE

DoD-7: JD/briefing discipline
- Evidence: `targeting_fit_score` is separated from `proof_authority_score`, and JD/briefing fields remain targeting-only in the contract and tests.
- Status: DONE

DoD-8: Regression tests
- Evidence: focused pytest slices cover graph-evidence contract behavior, authority gates, bundle wiring, repeated metric reuse, and thin generic category handling.
- Status: DONE

DoD-9: Calibration
- Evidence: `artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260619_215750/runtime_payload.json` records `graph_evidence_depth_comparison_report_v1` with `improved: true` and a 7/8 -> 8/8 rich-item delta.
- Status: DONE

DoD-10: Runtime proof
- Evidence: the latest competencies runtime proof includes the new confidence/report fields, the comparison report, and passing contract/test evidence in the branch receipt.
- Status: DONE

---

## Execution Closeout

PLAN_COMPLETE: plan=apps_rg-graph-skills-deepening-4f7c2a note="W0-W4 implementation, calibration, and SSOT writeback complete"

Verification anchors:
- `tests/unit/apps_rg/runtime/test_graph_evidence_contract.py`
- `tests/unit/apps_rg/test_competencies_authority_gates.py`
- `tests/unit/apps_rg/test_competencies_capability_bundle_wiring.py`
- `artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260619_215750/runtime_payload.json`

---

## Scope Expansion Authorization

When implementation uncovers adjacent graph weak spots, expand only if the issue directly affects competency evidence quality. Headline and executive-summary graph paths require explicit scope expansion or a separate plan.

```
DISCOVERED_SCOPE: plan=apps_rg-graph-skills-deepening-4f7c2a wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=apps_rg-graph-skills-deepening-4f7c2a decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=apps_rg-graph-skills-deepening-4f7c2a reason="<summary>" added="<waves/phases>" authorized="yes"
```
