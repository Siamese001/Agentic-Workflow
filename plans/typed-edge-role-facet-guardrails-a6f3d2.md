---
plan_id: typed-edge-role-facet-guardrails-a6f3d2
plan_format: v2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: ["phase2-gtm-presales-remaining-f7a2c9"]
---

# Typed Edge Role Facet Guardrails

Make GraphDB the skills and metrics SSOT, remove legacy candidate-fact authority noise before baseline, certify graph behavior before typed edges, add role-family facets, then add typed proof edges and sliding-scale composition guardrails with mandatory E2E waterfall evidence.

> **plan_id discipline**: markers use `plan=typed-edge-role-facet-guardrails-a6f3d2`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: W2
LAST_COMPLETED_WAVE: W1
LAST_UPDATED: 2026-06-13

---

## Context (SCQA)

- **Situation** - `apps_rg` already has an augmented skills graph with role-family inference, track weights, bridge edges, section projection, and senior-role fixtures. The Anthropic partner applied-AI fixture correctly identifies partner applied AI architecture, hyperscaler GTM, partnerships GTM, AI solutions architecture, and customer adoption signals.
- **Complication** - If traversal sources only approved partner skills and partner metrics, the selected skill pool becomes ATS-heavy and overfit before generation. Final text anti-overfit checks are too late when graph traversal has already created an over-concentrated proof pool.
- **Question** - How do we redesign traversal so role-family granularity improves targeting without replacing typed proof edges, without keeping `candidate_fact` or `fact_ledger` as competing skills or metrics authority, and without losing cross-role signal diversity?
- **Answer** - First run a P0 pre-flight that removes or fences `candidate_fact` as a runtime authority while preserving compatibility aliases for historical lineage. Then run the controlled waterfall: certify finalized graphs without typed edges, remove `fact_ledger` authority in favor of GraphDB SSOT, add role-family facets, add typed edges, then add sliding-scale percent composition. Each waterfall stage must run the three target resumes/briefings across all 11 generated lanes and produce graph-skill percentage breakouts plus variance rationalization.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| P0 | P0.1, P0.2, P0.3 | Candidate-fact deprecation and test gate | ~12K | GraphDB can expose equivalent fact/proof/source identifiers or fail closed where missing | DONE | `candidate_fact` authority is deprecated and tested before W1 starts |
| W1 | W1.1, W1.2 | Finalized graph baseline without typed edges | ~14K | Current graph receipts, fixtures, and E2E command path are discoverable | DONE | Three targets x 11 lanes run without typed edges, with graph-skill percent breakouts |
| W2 | W2.1, W2.2 | GraphDB SSOT, first-class metric outcomes, graph-era runtime field migration, and `fact_ledger` reference removal | ~18K | GraphDB can expose all skills, metrics, and metric outcomes needed by generation before Stage B E2E | TODO | No skills or metrics eligibility path depends on `fact_ledger`; E2E parity delta is explained |
| W3 | W3.1, W3.2 | Role-family and role-facet targeting | ~18K | Role facets can be implemented as targeting weights over eligible graph paths | TODO | Three-target E2E shows role-family variance without partner-only overfit |
| W4 | W4.1, W4.2 | Typed GraphDB proof/traversal edges | ~20K | Typed edges can be layered over the GraphDB SSOT without changing app/core boundaries | TODO | Three-target E2E shows typed edges explain eligibility and block unsupported paths |
| W5 | W5.1, W5.2 | Sliding-scale percent policy, anti-overfit guardrails, and waterfall closeout | ~18K | Composition metrics can be emitted before prompt assembly | TODO | Final E2E emits waterfall deltas, variance rationales, and closeout evidence |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| P0.1 | Inventory and classify `candidate_fact` usage before W1 | DONE |
| P0.2 | Deprecate or fence `candidate_fact` authority | DONE |
| P0.3 | Run candidate-fact deprecation tests and block W1 on failures | DONE |
| W1.1 | Resolve canonical E2E commands, target fixtures, and baseline graph receipts | DONE |
| W1.2 | Run finalized graph baseline without typed edges across all targets and lanes | DONE |
| W2.1 | Materialize metric outcomes, migrate fact-era runtime fields behind graph-era aliases, and fence `fact_ledger` skills/metrics authority | TODO |
| W2.2 | Run GraphDB SSOT E2E and explain variance from W1 | TODO |
| W3.1 | Introduce reusable role-family facets and target alignment diagnostics | TODO |
| W3.2 | Run role-family E2E and explain variance from W2 | TODO |
| W4.1 | Implement typed GraphDB edge contracts for proof, traversal, and targeting | TODO |
| W4.2 | Run typed-edge E2E and explain variance from W3 | TODO |
| W5.1 | Review and implement sliding-scale percentage composition guardrails | TODO |
| W5.2 | Run final E2E, produce waterfall analysis, and update Notion closeout | TODO |

---

## Out Of Scope

- Manually editing generated resume text to hide graph behavior.
- Promoting DRAFT, INTERNAL_ONLY, LOW, or directional skills to external claims.
- Treating JD or briefing text as proof.
- Replacing typed edges with granular role families in the final architecture.
- Adding company-specific edge types such as `anthropic_partner_supports_skill`.
- Implementing `agentic_core` runtime `EdgeContract` handoffs between U0, L1, L0, C0, PA, L3, L2, Exit, UWG, L4, or L6.
- Changing runtime handoff authority outside `apps_rg` resume generation.
- Changing `agentic_core`.
- Removing `master_skills_arsenal_ledger.json` as a serialization, export, bootstrap, or review artifact. This plan may fence it behind the `augmented_skills_graph` authority interface, but DB-only persistence migration is not part of W2 closure.
- Implementing ADG-style graph-skill materialized views, Redis hot projections, or GraphDB Lite/NetworkX projections as production runtime dependencies before W5 closeout. Read-only/offline analysis is allowed only under the Post-Waterfall Graph Projection Recommendation.
- Applying evidence-strength, metric-strength, recency, confidence, or capability-depth as active ranking multipliers before W2.2. W2 may emit those values as diagnostics only; selection behavior changes require a later waterfall stage or separate authorized scope.
- Adding first-class `ResumeBullet` nodes to the core graph. Bullet scoring and generated-output history remain downstream of role-episode bundles and section outputs for this plan.
- Weakening final text anti-overfit, X2, X1D, or C0 evidence discipline.

---

## Architecture Position

The final hierarchy is:

1. GraphDB skills and metrics SSOT.
2. Typed proof, provenance, employer, capability, and section eligibility edges.
3. Role-family and role-facet targeting weights.
4. Sliding-scale percent composition policy.
5. Anti-overfit traversal guardrails.
6. Resume section generation.
7. Final text lint and judge checks.

Role family is a consumer of the graph, not the graph authority. Typed edges answer "is this allowed and why?" Role facets answer "how much should this eligible area matter for this JD?" Sliding-scale percentages answer "is the final selected pool balanced enough for this target without overfitting?"

The implementation order deliberately runs role-family E2E before typed-edge E2E to isolate its effect in the waterfall. That does not make role family the authority layer. The final architecture still requires typed edges to control proof and eligibility.

---

## Hardening Rules

### Typed Edge Scope Clarification

In this plan, "typed edges" means GraphDB proof/traversal edges used by `apps_rg` resume generation:
- proof edges
- provenance edges
- employer edges
- capability edges
- section eligibility edges
- targeting edges
- facet edges

This plan does not implement `agentic_core` runtime `EdgeContract` handoffs between U0, L1, L0, C0, PA, L3, L2, Exit, UWG, L4, or L6. Runtime handoff authority remains out of scope.

### Authority Stack Invariant

```text
targeting_weight <= section_eligibility <= claim_eligibility <= proof <= provenance <= GraphDB SSOT
```

A lower layer may narrow, rank, demote, or block. A lower layer may not admit a skill, metric, or claim that the higher authority layer did not allow.

### Proof Pool Runtime Boundary

`proof_pool`, `proof_pool_resolver`, and any allowed-pool metadata are not a second SSOT. They are runtime transport/cache surfaces for the selected GraphDB-approved evidence set. Their only valid job is to carry forward `selected_graph_evidence_plan`, `allowed_graph_evidence_ids`, selected graph node IDs, selected graph edge IDs, and selected graph metric IDs so validators and generation can enforce the allowed set.

During W2.1, keep proof-pool plumbing only as a compatibility surface while migrating consumers to graph-era names. It may narrow, deduplicate, group, or explain GraphDB-approved evidence. It may not create proof, repair missing graph paths, admit fact-era IDs as authority, or preserve `candidate_fact`, `fact_ledger`, `source_fact_ids`, or `allowed_fact_ids` as proof authority. If a proof-pool row cannot resolve to GraphDB-authorized evidence, traversal fails closed with `MISSING_GRAPH_PATH` or a `BLOCKED_*` verdict.

Do not remove or broadly rename proof-pool plumbing as a standalone pre-W2 cleanup. The controlled implementation point is W2.1, before W2.2 E2E, so any behavior change is captured in the GraphDB SSOT waterfall delta.

### No Silent Fallback Rule

If GraphDB lacks a required skill, metric, proof edge, employer edge, provenance edge, or section edge, traversal must emit `MISSING_GRAPH_PATH` or a `BLOCKED_*` verdict. It may not infer, synthesize, or backfill eligibility from JD text, briefing text, generated text, `candidate_fact`, `fact_ledger`, prompt context, or historical output.

### Canonical Traversal Verdicts

Allowed verdicts:
- `SELECTED`
- `DEMOTED`
- `BLOCKED_UNPROVEN`
- `BLOCKED_SECTION`
- `BLOCKED_EMPLOYER_SCOPE`
- `BLOCKED_PROVENANCE`
- `BLOCKED_CANDIDATE_FACT_AUTHORITY`
- `BLOCKED_FACT_LEDGER_AUTHORITY`
- `REBALANCE_REQUIRED`
- `MISSING_GRAPH_PATH`
- `DIAGNOSTIC_ONLY`

Unknown verdicts fail closed.

### Required Negative Tests

- `high_role_facet_weight_cannot_select_unproven_skill`
- `jd_keyword_cannot_create_proof_or_provenance`
- `section_block_overrides_high_facet_weight`
- `missing_supporting_fact_blocks_claim_eligibility`
- `missing_employer_binding_blocks_employer_scoped_claim`
- `candidate_fact_runtime_authority_read_fails_closed_before_W1`
- `fact_ledger_runtime_skill_read_fails_closed_after_W2`
- `linked_metric_outcome_id_must_resolve_to_graph_metric_outcome_after_W2`
- `strength_diagnostics_do_not_change_selection_before_ranking_stage`
- `typed_edge_missing_path_blocks_selected_skill_after_W4`
- `over_concentrated_pool_blocks_prompt_assembly_after_W5`
- `repeated_metric_family_triggers_rebalance`
- `target_company_name_cannot_be_claimed_as_experience`

### Prompt-Hack Exclusion

Prompt-only fixes are not valid closure evidence. Changing prompt wording, examples, or anti-overfit text without changing traversal diagnostics and enforcement does not satisfy W3, W4, or W5.

---

## Candidate Fact P0 Recommendation

**Recommendation: move `candidate_fact` authority deprecation and testing to P0 before W1 starts.**

This should be a pre-flight deprecation and test gate, not a broad physical deletion. P0 should deprecate or fence `candidate_fact` as a runtime source of skills, metrics, proof, claim eligibility, section eligibility, or weighting. Historical identifiers may remain temporarily as compatibility aliases or lineage fields only when they point to GraphDB-backed fact nodes and cannot admit anything.

**Why P0 is the right timing**:
- W1 is supposed to be the clean finalized-graph baseline. If `candidate_fact` can still influence proof or eligibility, the baseline measures legacy substrate noise instead of graph behavior.
- Removing it after W1 would create avoidable waterfall variance that is not about role family, typed edges, or sliding-scale policy.
- P0 keeps W2 focused on `fact_ledger` storage/source cleanup instead of mixing two authority migrations in one E2E delta.
- GraphDB SSOT should be true before the first all-lane baseline; otherwise later graph-skill percentage breakouts can be contaminated by candidate-fact selection behavior.

**Why this is not a full destructive removal before W1**:
- Existing reports, validators, prompts, and legacy artifacts may still use `candidate_fact_id` as a lineage label.
- Deleting every field up front would expand blast radius and could block the plan on renaming churn rather than authority correctness.
- The needed P0 outcome is fail-closed authority behavior: any `candidate_fact` runtime read that would admit, prove, rank, or select must return `BLOCKED_CANDIDATE_FACT_AUTHORITY` or `MISSING_GRAPH_PATH` unless it resolves to a GraphDB-authorized path.

**Tradeoff accepted**:
- The plan loses a pre-P0 E2E comparison against legacy candidate-fact behavior. That is intentional. Legacy candidate-fact behavior is noise, not a useful waterfall stage. P0 should still emit a static inventory and targeted fail-closed test evidence so the removed noise is auditable.

---

## Fact Ledger Timing Decision

Remove `fact_ledger` authority immediately after the finalized-graph/no-typed-edge baseline E2E and before role-family or typed-edge implementation.

**Why this timing is recommended**:
- W1 creates a clean control run against the current finalized graph, so later SSOT changes have a measurable baseline.
- W2 prevents dual authority before role-family weighting or typed edges are introduced. Otherwise, a role-family or typed-edge regression could be masked by stale `fact_ledger` reads.
- GraphDB must be the only skills and metrics authority before traversal is made more powerful. Role facets and typed edges should operate on one source of truth, not arbitrate between GraphDB and ledger remnants.
- Any remaining claim-audit artifact must be renamed or fenced so it cannot be confused with skills or metrics authority. No runtime path may consult `fact_ledger` for skill eligibility, metric eligibility, weighting, proof, or traversal.

---

## Post-Waterfall Graph Projection Recommendation

**Recommendation: defer production implementation of ADG-style graph-skill materialized views, GraphDB Lite/NetworkX projections, Redis hot projections, and selector-manifest wiring until after W5 closes.**

During P0-W5, only read-only/offline exploratory artifacts are allowed. They may inspect copied waterfall outputs or graph snapshots, but they must not feed proof pools, C0/C0.3 receipts, traversal verdicts, packet generation, validators, prompt assembly, or waterfall pass/fail status.

**Defense**:
- P0-W5 is a causal waterfall. Each stage is supposed to isolate one source of variance: candidate-fact deprecation, GraphDB SSOT, role-family facets, typed edges, then sliding-scale composition. Adding a derived projection layer mid-waterfall would introduce a second variance source and weaken stage attribution.
- The authority boundary is already the core invariant: GraphDB / `augmented_skills_graph` is the skills and metrics SSOT; materialized views, GraphDB Lite projections, Redis keys, and manifests are derived receipts or projections. They may narrow, rank, explain, cache, or audit; they may not admit new skills, metrics, proof, or claims.
- Implementing the projection layer after W5 lets it reuse stable verdicts, breakout dimensions, artifact paths, row-count expectations, and variance categories proven by the waterfall instead of freezing intermediate contracts.
- The useful ADG pattern is the discipline, not the ADG schema: bounded materialized query surfaces, manifest row counts, fail-closed presence checks, and analyst artifacts. The `apps_rg` version should be purpose-built around section evidence candidates, allowed-pool closure, skill/fact support strength, hop paths, bundle skew, and utilization.

**Allowed before W5**:
- Design notes naming candidate `apps_rg` views and receipt fields.
- Offline reports that read existing graph snapshots or waterfall artifacts without changing runtime behavior.
- Static row-count or schema experiments that are clearly labeled non-authoritative and disposable.

**Not allowed before W5**:
- Runtime consumption of new graph-skill MVs, Redis projections, or NetworkX projections.
- Fallbacks from missing GraphDB proof into derived projections.
- Product proof, release claims, or pass/fail gates based on derived projection rows.

**Post-W5 candidate follow-up scope**:
- `mv_section_evidence_candidates`
- `mv_role_episode_bundle_rank`
- `mv_skill_fact_support_strength`
- `mv_allowed_pool_closure`
- `mv_hop_paths_by_fact`
- `mv_bundle_skew_diagnostics`
- A bounded graph-selection analyst artifact with selected/demoted/blocked/missing rows and row-count manifest.

---

## Mandatory E2E Matrix And Waterfall

Every E2E gate in this plan must run the same target matrix:

| Target slug | Reader-facing target |
|---|---|
| `anthropic_partner_applied_ai` | Anthropic AI Partner |
| `truist_head_of_agentic_engineering` | Truist Head of Agentic Engineering |
| `brown_brown_svp_it_strategy_innovation` | Brown & Brown SVP IT Strategy & Innovation |

Each target must run all 11 generated-content lanes from `apps_rg.runtime.section_execution_plan.GENERATED_CONTENT_LANES`:

| Order | Lane |
|---:|---|
| 1 | `competencies` |
| 2 | `unify_bullets` |
| 3 | `ibm_bullets` |
| 4 | `insurtech_bullets` |
| 5 | `ey_bullets` |
| 6 | `unify_narrative` |
| 7 | `ibm_narrative` |
| 8 | `insurtech_narrative` |
| 9 | `ey_narrative` |
| 10 | `executive_summary` |
| 11 | `headline` |

P0 is a prerequisite, not a waterfall stage. P0 must pass before W1 starts, and W1 Stage A is the first all-lane E2E run. This avoids spending 3 x 11 baseline effort on known legacy candidate-fact authority noise.

The waterfall stages are:

| Stage | Required state | E2E requirement |
|---|---|---|
| A | Post-P0 finalized graphs without typed edges | Run 3 targets x 11 lanes; typed edges disabled or absent; `candidate_fact` authority removed or fenced |
| B | GraphDB SSOT with `fact_ledger` skills/metrics authority removed | Run 3 targets x 11 lanes; explain variance from A |
| C | Role family and role facets enabled | Run 3 targets x 11 lanes; explain variance from B |
| D | Typed edges enabled | Run 3 targets x 11 lanes; explain variance from C |
| E | Sliding-scale percentages and anti-overfit guardrails enabled | Run 3 targets x 11 lanes; explain variance from D and full A to E waterfall |

Every run artifact must include:
- Target slug, briefing/resume input path, graph version, run id, stage id, lane id, and lane status.
- Feature flags or configuration proving which stage was active.
- Graph skills percentage breakout by lane.
- Breakout dimensions for role family, role facet, pillar, source fact family, employer scope, and metric type.
- Selected, demoted, blocked, and missing skills with reasons.
- A variance rationalization versus the prior waterfall stage, including top added, removed, promoted, and demoted graph skills.
- An expected/unexpected classification for each material variance.

A stage is not complete unless every target-lane combination either passes or has an explicit blocker with blocker class, failed command, artifact path, and next action.

---

## P0 - Candidate-Fact Deprecation And Test Gate

P0_STATUS: DONE
P0_COMPLETE: YES
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: P0

**Authorization**: REQUIRED - Candidate-fact authority deprecation can touch proof, selection, validators, prompts, and legacy artifact compatibility.

**Phases**:
- **P0.1** - Inventory and classify `candidate_fact` usage before W1 | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **P0.2** - Deprecate or fence `candidate_fact` authority | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **P0.3** - Run candidate-fact deprecation tests and block W1 on failures | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Allowed after P0**:
- `candidate_fact_id` as a compatibility alias or lineage identifier in historical artifacts.
- Adapters that translate legacy candidate-fact identifiers to GraphDB fact/proof nodes.
- Diagnostic output showing a legacy identifier and its GraphDB-backed path.

**Not allowed after P0**:
- Any `candidate_fact` runtime read that admits, proves, ranks, weights, or selects a skill, metric, claim, or section.
- Any fallback where missing GraphDB proof is filled from candidate facts.
- Any prompt context that treats candidate facts as proof independent of GraphDB provenance.

**Acceptance**:
- Static inventory classifies each live `candidate_fact` reference as allowed lineage/compatibility or disallowed authority.
- Disallowed authority paths are removed, renamed, or fail closed behind GraphDB lookup.
- `candidate_fact_runtime_authority_read_fails_closed_before_W1` passes.
- Missing GraphDB translation for a legacy candidate-fact identifier emits `MISSING_GRAPH_PATH` or `BLOCKED_CANDIDATE_FACT_AUTHORITY`.
- W1 cannot start until P0 deprecation and test evidence exists.

---

## Wave 1 - Finalized Graph Baseline Without Typed Edges

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED - Command discovery, fixture resolution, and baseline evidence collection only.

**Phases**:
- **W1.1** - Resolve canonical E2E commands, target fixtures, and baseline graph receipts | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Run finalized graph baseline without typed edges across all targets and lanes | ~8K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- P0 has passed, so `candidate_fact` cannot act as skills, metrics, proof, eligibility, selection, or weighting authority.
- Canonical fixture/input paths are resolved for Anthropic AI Partner, Truist Head of Agentic Engineering, and Brown & Brown SVP IT Strategy & Innovation.
- The baseline run covers all 33 target-lane combinations.
- Typed edges are disabled, absent, or explicitly no-op in the baseline configuration.
- Artifacts show graph-skill percentage breakouts per target and lane.
- Baseline partner concentration, AI architecture concentration, platform credibility, metric diversity, and employer coverage are documented.

---

## Wave 2 - GraphDB SSOT, Metric Outcomes, Graph-Era Fields, And Fact Ledger Removal

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: B

**Authorization**: REQUIRED - Any schema, traversal, validator, or runtime authority change must be explicitly reviewed before execution.

**Phases**:
- **W2.1** - Materialize metric outcomes, migrate fact-era runtime fields behind graph-era aliases, and fence `fact_ledger` skills/metrics authority | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** - Run GraphDB SSOT E2E and explain variance from W1 | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Pre-W2 cleanup status**:

| Cleanup | Status | Timing decision | Rationale |
|---|---|---|---|
| Metric SSOT derivation from graph JSON | DONE before W2 | Pre-waterfall baseline hardening complete | Low-disruption removal of hardcoded metric allowlists; W2 can assume metric approval comes from graph JSON `metric_outcome_nodes`. |
| First-class `metric_outcome` nodes in materialized GraphDB | OPEN | Execute inside W2.1 before W2.2 E2E | W2 claims GraphDB is the skills and metrics SSOT. Metric outcomes may originate from graph JSON and role-episode bundle references, but Stage B should verify them as graph nodes/edges rather than side fields only. |
| Generic employer bundle registry behind existing wrappers | DONE before W2 | Pre-waterfall baseline hardening complete | Existing imports keep working while all employer graph wrappers share loader/access/validation primitives. |
| Normalize graph JSON bundle schema | DONE before W2 | Pre-waterfall baseline hardening complete | All employer bundles share the common graph shape before W2 changes runtime contracts. |
| Rename fact-era runtime fields to graph-era fields | OPEN | Execute inside W2.1 before W2.2 E2E | Highest blast radius because `selected_fact_plan`, `allowed_fact_ids`, `source_fact_ids`, `fact_id`, and `candidate_fact_id` still cross validators, lanes, proof pools, prompt artifacts, and output schemas. Do not perform as an untracked pre-waterfall cleanup; make it a controlled W2 compatibility migration with variance evidence. |
| Proof-pool authority boundary | OPEN | Execute inside W2.1 before W2.2 E2E | Keep proof-pool plumbing only as selected graph evidence transport/cache while consumers migrate. Do not delete or rename it as a standalone cleanup; prove it cannot admit, repair, or preserve proof outside GraphDB-approved IDs. |

**W2.1 implementation order**:

1. Materialize first-class metric outcome graph rows before W2.2:
   - `metric_outcome` node type or equivalent canonical graph row
   - edges from supporting facts, skills, role episodes, employers, and sections where available
   - resolver validation for every `linked_metric_outcome_ids` / `metric_outcome_nodes` reference emitted by role-episode bundles
   - fail-closed `MISSING_GRAPH_PATH` or `BLOCKED_*` verdict for unresolved metric outcome IDs
2. Introduce graph-era output names while preserving fact-era read aliases for compatibility:
   - `selected_graph_evidence_plan` beside `selected_fact_plan`
   - `allowed_graph_evidence_ids` beside `allowed_fact_ids`
   - `graph_evidence_ids` beside `source_fact_ids`
   - `graph_evidence_id` beside `fact_id`
   - `legacy_candidate_fact_id` only as lineage, never authority
3. Update validators, proof-pool metadata, and section packets to prefer graph-era names.
4. Treat proof-pool outputs as internal selected-graph-evidence transport/cache only; every retained row must resolve to GraphDB-approved node, edge, or metric IDs.
5. Emit evidence-strength and metric-strength diagnostics as report-only fields. They may explain selected, weak, blocked, or missing paths, but they may not alter W2.2 skill selection, metric selection, ranking, prompt assembly, or waterfall percentages.
6. Keep fact-era fields as compatibility aliases until all generated lanes and X2/X1D gates read graph-era fields.
7. Remove or hard-fail any fact-era field that can still admit, rank, prove, or select a skill, metric, claim, or section.

**Authority rule**:

GraphDB is the SSOT for skills, metrics, skill eligibility, metric eligibility, graph traversal, and skill weighting. `fact_ledger` references must be removed, renamed, or fenced so they cannot act as a skills or metrics source of truth.

Selected skill references, including `selection_plan_skill_ref` values and lane-selected `skill_id` values, must resolve through the `augmented_skills_graph` authority interface. The current `master_skills_arsenal_ledger.json` file may remain as the backing serialization/export/bootstrap artifact for that authority, but it must not be named, queried, or reported as an independent skills authority.

Metric outcome references, including `linked_metric_outcome_ids` and bundle `metric_outcome_nodes`, must resolve to first-class GraphDB metric outcome rows before W2.2. Role-episode bundle fields may carry references and summaries, but they are not the metric authority once W2 closes.

Allowed after W2:
- A clearly named claim-audit or generation-audit artifact that records what was emitted.
- Backward-compatible adapters that fail closed and delegate to GraphDB.
- JSON ledger artifacts only when labeled as non-authoritative serialization/export/bootstrap/review artifacts or hidden behind the `augmented_skills_graph` resolver boundary.
- Proof-pool plumbing only as an internal allowed-graph-evidence transport/cache whose rows are derived from GraphDB-approved selected graph evidence and fail closed on unresolved IDs.
- Evidence-strength and metric-strength diagnostics only when labeled report-only and excluded from ranking, selection, and prompt assembly until a later authorized stage.
- Historical documentation describing the migration.

Not allowed after W2:
- Any runtime read from `fact_ledger` to admit, weight, prove, or select a skill or metric.
- Any fallback path where missing GraphDB data is silently filled from `fact_ledger`.
- Any diagnostic that reports `fact_ledger` as an authoritative source for skills or metrics.
- Any runtime, report, or diagnostic contract that tells consumers to look up selected skills against "master skills" as an authority instead of the `augmented_skills_graph` authority interface.
- Any proof-pool or allowed-pool path that creates proof, repairs missing GraphDB evidence, accepts fact-era IDs as authority, or reports itself as the source of claim truth.
- Any metric claim, metric eligibility decision, or metric-strength diagnostic that depends only on side-field bundle references without resolving the metric outcome through GraphDB.
- Any evidence-strength, metric-strength, recency, confidence, or capability-depth score that changes W2.2 ranking or selected evidence before a distinct ranking waterfall stage is authorized.
- Any DB-vs-JSON arbitration path during generation; if the GraphDB authority cannot resolve a required skill, metric, proof, employer, provenance, or section path, traversal fails closed.

**Acceptance**:
- Static search and runtime tracing show no skills or metrics authority depends on `fact_ledger`.
- Materialized GraphDB exposes first-class metric outcome rows and resolver checks for role-episode `linked_metric_outcome_ids` / `metric_outcome_nodes`.
- Per-lane diagnostics resolve `selection_plan_skill_ref` and selected `skill_id` values through the `augmented_skills_graph` authority interface; any `lookup_backend` detail is explicitly non-authoritative.
- Per-lane diagnostics include evidence-strength and metric-strength as report-only fields, and a regression check proves they do not alter W2.2 selected skill IDs, selected metric IDs, ranking order, or prompt inputs.
- Proof-pool metadata carries graph-era selected evidence IDs and is documented as transport/cache only, not authority.
- Non-GraphDB-resolvable proof-pool rows fail closed before validators or generation can use them.
- Missing GraphDB skill, metric, proof, employer, provenance, or section paths emit `MISSING_GRAPH_PATH` or a `BLOCKED_*` verdict; no runtime path silently backfills from `fact_ledger`.
- `fact_ledger_runtime_skill_read_fails_closed_after_W2` passes.
- GraphDB SSOT E2E covers all 33 target-lane combinations.
- Variance from W1 is rationalized as expected migration variance or flagged as regression.
- The W2 run preserves or improves graph-skill breakout visibility versus W1.

---

## Wave 3 - Role Family And Role Facet Targeting

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: C

**Authorization**: REQUIRED - Role-family granularity changes can affect every generated lane and must be reviewed before execution.

**Phases**:
- **W3.1** - Introduce reusable role-family facets and target alignment diagnostics | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** - Run role-family E2E and explain variance from W2 | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Facet model**:

| Role family | Candidate reusable facets |
|---|---|
| `PARTNER_APPLIED_AI_ARCHITECTURE` | `applied_ai_architecture`, `partner_gtm`, `hyperscaler_cosell`, `technical_presales`, `customer_adoption_derisking`, `enterprise_platform_credibility` |
| `AGENTIC_ENGINEERING_LEADERSHIP` | `agentic_platform_architecture`, `engineering_leadership`, `ai_governance`, `delivery_operating_model`, `platform_reliability`, `stakeholder_alignment` |
| `IT_STRATEGY_AND_INNOVATION` | `it_strategy`, `innovation_portfolio`, `operating_model_transformation`, `enterprise_architecture`, `vendor_partner_leverage`, `business_outcome_delivery` |

**Acceptance**:
- Facets are reusable across role families and cannot directly admit a claim.
- Role-family granularity does not replace typed proof edges.
- A facet can boost only skills that already pass GraphDB SSOT eligibility.
- `high_role_facet_weight_cannot_select_unproven_skill` passes.
- `jd_keyword_cannot_create_proof_or_provenance` passes.
- `section_block_overrides_high_facet_weight` passes.
- Role-family E2E covers all 33 target-lane combinations.
- Variance from W2 explains how Anthropic, Truist, and Brown & Brown move differently by role-family and lane.

---

## Wave 4 - Typed GraphDB Edge Contracts

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: D

**Authorization**: REQUIRED - Typed edge changes alter proof, traversal, targeting, and eligibility semantics across `apps_rg` graph traversal.

**Phases**:
- **W4.1** - Implement typed GraphDB edge contracts for proof, traversal, and targeting | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** - Run typed-edge E2E and explain variance from W3 | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Typed edge categories**:

| Category | Purpose | Example edge types |
|---|---|---|
| Proof | Shows a skill or claim is evidence-backed | `skill_supported_by_fact`, `fact_claim_eligible` |
| Provenance | Shows where proof came from | `fact_source_provenance`, `fact_source_trace` |
| Employer | Constrains facts to IBM, Unify, EY, InsurTech, or other employers | `employment_hosts_fact`, `fact_bound_to_employer` |
| Capability | Connects tracks, pillars, skills, and facts | `career_track_contains_pillar`, `pillar_contains_skill` |
| Section eligibility | Decides where a claim may appear | `skill_allowed_in_section`, `skill_blocked_for_section` |
| Targeting | Lets JD/briefing influence rank only | `target_context_suggests_role_family` |
| Facet | Applies reusable role intent over eligible paths | `role_family_contains_facet`, `facet_prioritizes_pillar` |

**Traversal explanation packet**:
- `role_family`
- `role_facet`
- `pillar_id`
- `skill_id`
- `supporting_fact_ids`
- `source_fact_family`
- `metric_type`
- `employer_scope`
- `section_eligibility`
- `claim_eligibility`
- `targeting_only_terms`
- `blocked_or_demoted_reason`

**Acceptance**:
- Every selected skill can emit a path with role family, facet, pillar, supporting fact, employer, section eligibility, and blocking notes.
- JD/briefing signals never appear in proof or provenance fields.
- Section lanes can reject a skill even when its role facet weight is high.
- Unknown traversal verdicts fail closed.
- `missing_supporting_fact_blocks_claim_eligibility` passes.
- `missing_employer_binding_blocks_employer_scoped_claim` passes.
- `typed_edge_missing_path_blocks_selected_skill_after_W4` passes.
- Typed-edge E2E covers all 33 target-lane combinations.
- Variance from W3 explains whether typed edges changed selection by proof, provenance, employer, or section eligibility.

---

## Wave 5 - Sliding-Scale Percent Policy And Waterfall

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: E

**Authorization**: REQUIRED - Sliding-scale thresholds and blocking behavior affect generation eligibility.

**Phases**:
- **W5.1** - Review and implement sliding-scale percentage composition guardrails | ~9K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.2** - Run final E2E, produce waterfall analysis, and update Notion closeout | ~9K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Sliding-scale design requirements**:
- Use ranges, caps, floors, and penalties rather than fixed one-size percentages.
- Compute percentages from eligible graph skills, not JD keyword counts.
- Use section-specific thresholds so headline, executive summary, competencies, bullets, and narratives can differ.
- Preserve durable candidate strengths even when a target role is highly specialized.
- Require a rebalancing verdict before prompt assembly when concentration breaches caps or floors.

**Illustrative Anthropic partner applied-AI target ranges**:

| Facet | Target range |
|---|---:|
| Applied AI / solution architecture | 25-30% |
| Partner / alliance GTM | 20-25% |
| Hyperscaler / co-sell | 15-20% |
| Technical presales / adoption | 15-20% |
| Enterprise platform credibility | 10-15% |
| Legacy quant/risk credibility | 0-5% |

**Guardrails**:

| Guardrail | Purpose |
|---|---|
| Facet concentration caps | Prevent generic partner GTM from dominating the pool |
| Facet floors | Preserve applied AI architecture, technical presales, platform credibility, engineering leadership, and IT strategy signals where relevant |
| Source diversity | Prevent all selected skills from coming from one fact family such as `fact_partnerships_gtm_*` |
| Section-specific caps | Keep headline, summary, bullets, narratives, and competencies from using the same density rules |
| Repeated concept penalty | Demote repeated co-sell, alliance, marketplace, partner enablement, agentic, innovation, and transformation concepts |
| Metric diversity | Balance revenue/GTM, platform delivery, adoption, operational scale, governance/reliability, and transformation metrics |
| Core candidate preservation | Reserve space for durable candidate strengths independent of target JD wording |
| Proof-targeting firewall | Keep JD/briefing terms out of proof and claim eligibility |

**Diagnostic shape**:

```text
target: anthropic_partner_applied_ai
stage: sliding_scale_percent
lane: executive_summary
role_family: PARTNER_APPLIED_AI_ARCHITECTURE
facet_mix:
  partner_gtm: 32% WARN cap 30%
  applied_ai_architecture: 18% WARN floor 20%
  enterprise_platform_credibility: 7% WARN floor 10%
source_mix:
  partnerships_gtm facts: 65% WARN
  platform facts: 20%
  adoption facts: 15%
verdict: REBALANCE_REQUIRED
```

**Waterfall report requirements**:
- Compare A to B, B to C, C to D, D to E, and A to E for every target and lane.
- Show graph-skill percent change by role family, facet, pillar, source fact family, employer scope, and metric type.
- Call out top variance drivers and whether each was expected.
- Explain why Anthropic, Truist, and Brown & Brown diverge from one another after each stage.
- Include a compact summary table suitable for Notion closeout.

**Acceptance**:
- Final sliding-scale E2E covers all 33 target-lane combinations.
- A full waterfall report exists for all five stages.
- Over-concentrated selected pools return `REBALANCE_REQUIRED` before prompt assembly.
- `over_concentrated_pool_blocks_prompt_assembly_after_W5` passes.
- `repeated_metric_family_triggers_rebalance` passes.
- `target_company_name_cannot_be_claimed_as_experience` passes.
- Prompt-only wording, example, or anti-overfit text changes are rejected as W5 closure evidence unless traversal diagnostics and enforcement changed.
- Final text anti-overfit remains in place for copied JD phrasing, keyword stuffing, unsupported target-company claims, repeated buzzwords, and target role as past experience.
- Notion row links the disk plan and final evidence.

---

## Execution Details

### P0.1 - Candidate-Fact Authority Inventory

**Scope**: Classify `candidate_fact` usage before W1 as either allowed lineage/compatibility or disallowed runtime authority.

**Required searches**:
```bash
rg -n "candidate_fact|candidate facts|CandidateFact" apps_rg tests docs plans .claude
```

**Classification rule**:
- Allowed: lineage identifier, historical artifact reference, or compatibility alias that resolves to a GraphDB-backed path.
- Disallowed: any use that admits, proves, ranks, weights, selects, or backfills a skill, metric, claim, proof path, or section.

**Completion evidence**: `docs/reports/apps_rg/candidate_fact_p0_authority_inventory_20260612.md` classifies remaining references as lineage/compatibility, fact-vector substrate labels pending W2, tombstones, or historical prompt/test artifacts. The post-patch static search found no remaining `candidate_facts_as_proof: true` declarations or tests expecting candidate facts to prove claims.

### P0.2 - Candidate-Fact Authority Deprecation

**Scope**: Deprecate, rename, or fence disallowed `candidate_fact` authority before any W1 E2E baseline run.

**Completion evidence**: `apps_rg/runtime/validators/graph_skills_proof_common.py` now emits `BLOCKED_CANDIDATE_FACT_AUTHORITY` for candidate-fact/SRFS authority flags, authority source fields, selection methods, and candidate-fact claim substrate without GraphDB claim authority. `apps_rg/runtime/sections/section_spec.py` forces deprecated `candidate_facts_as_proof` input closed and preserves `candidate_fact_lineage_allowed` as lineage-only configuration.

### P0.3 - Candidate-Fact Deprecation Tests

**Scope**: Run the fail-closed test gate before W1.

**Required evidence**:
- Static inventory artifact.
- Runtime fail-closed evidence for at least one disallowed candidate-fact authority read.
- Passing `candidate_fact_runtime_authority_read_fails_closed_before_W1`.
- A compatibility map for any remaining `candidate_fact_id` fields.
- Explicit W1 block if the test fails or if any disallowed authority read remains.

**Completion evidence**: Focused P0 gate passed: `tests/unit/apps_rg/runtime/sections/test_section_spec_wave6.py`, `tests/unit/apps_rg/test_candidate_fact_deprecation_p0.py`, `tests/unit/apps_rg/test_graph_skills_authority_separation.py`, `tests/unit/apps_rg/test_selected_role_fact_set_retirement_guard.py`, and `tests/_apps_contract/test_apps_rg_augmented_skills_graph_source_authority.py` reported 47 passed, 3 warnings with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and local `addopts` override for the unavailable timeout plugin.

### W1.1 - Resolve Commands And Fixtures

**Scope**: Identify the canonical E2E command, target fixtures, graph receipt paths, and generated-content lane list before changing behavior.

**Required searches**:
```bash
rg -n "anthropic_partner_applied_ai|truist_head_of_agentic_engineering|brown_brown_svp_it_strategy_innovation" apps_rg tests docs/reports/apps_rg plans
rg -n "GENERATED_CONTENT_LANES|section_execution_plan|e2e|end to end" apps_rg tests docs/reports/apps_rg plans
```

**Completion evidence**:
- Canonical generated lane matrix resolved from `apps_rg.runtime.section_execution_plan.GENERATED_CONTENT_LANES`: 11 generated lanes per target.
- Canonical target fixtures resolved:
  - Anthropic AI Partner: `apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_jd.txt` and `apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_briefing.md`.
  - Truist Head of Agentic Engineering: `apps_rg/config/targeting/truist_head_agentic_ai_engineering_jd.txt` and `apps_rg/config/targeting/truist_head_agentic_ai_engineering_briefing.md`.
  - Brown & Brown SVP IT Strategy & Innovation: `apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt` and `apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md`.
- `python -m apps_rg doctor --strict --json` passed before W1 runs.

### W1.2 - Finalized Graph Baseline E2E

**Scope**: Run the Post-P0 finalized graph/no-typed-edge baseline for the three required targets across all 11 generated lanes and capture graph-skill breakouts plus explicit blockers.

**Completion evidence**:
- W1 report: `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/w1_finalized_graph_baseline_report.md`.
- Machine-readable W1 report: `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/w1_finalized_graph_baseline_report.json`.
- Anthropic baseline run: `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/anthropic_partner_applied_ai`; patch receipt `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/anthropic_partner_applied_ai/patch_run_receipt.json`.
- Truist baseline run: `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/truist_head_of_agentic_engineering`; patch receipt `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/truist_head_of_agentic_engineering/patch_run_receipt.json`.
- Brown & Brown baseline run: `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/brown_brown_svp_it_strategy_innovation`.

**Waterfall outcome**:
- Coverage: 33 explicit target-lane rows captured: 13 executed-and-blocked rows, 15 pre-run blocked rows, and 5 selected/authorized rows.
- Anthropic target graph-skill mix: partnerships ecosystem 27.9%, enterprise technology delivery 24.8%, agentic AI governance platform 18.5%, cloud data platform 15.2%, actuarial/capital/risk 7.1%, insurance/insurtech 5.4%, product commercialization 1.2%.
- Truist target graph-skill mix: agentic AI governance platform 37.0%, enterprise technology delivery 30.4%, partnerships ecosystem 18.5%, cloud data platform 9.8%, actuarial/capital/risk 2.2%, product commercialization 2.2%.
- Brown & Brown target graph-skill mix: cloud data platform 28.1%, enterprise technology delivery 24.9%, agentic AI governance platform 16.1%, insurance/insurtech 10.4%, partnerships ecosystem 10.0%, actuarial/capital/risk 9.2%, product commercialization 1.2%.
- `tools/apps_rg/graph_skill_utilization_report.py` could not run because W1 did not reach `final_resume_assembly/final_resume.json`; this is expected for the W1 blocking baseline. The W1-specific report uses lane receipts, X3 dispositions, provider responses, and patch receipts instead.
- Variance against P0 is classified as baseline creation and fail-closed behavior, not a percentage delta, because P0 was a candidate-fact authority deprecation/test gate rather than an all-lane E2E composition stage.
- W1 completion is accepted because every target-lane combination either reached authorized/generated evidence or has an explicit fail-closed blocker with artifact path. Final resume assembly is not required for this baseline stage.

### W2.1 - Graph-Era Runtime Field Migration And GraphDB SSOT

**Scope**: First migrate fact-era runtime field names to graph-era contracts behind compatibility aliases, then fence proof-pool plumbing as transport/cache only, replace or fence every `fact_ledger` skills/metrics authority reference, and ensure selected skill references resolve through the `augmented_skills_graph` authority interface rather than any separately named "master skills" authority.

**Required searches**:
```bash
rg -n "selected_fact_plan|allowed_fact_ids|source_fact_ids|candidate_fact_id|fact_id" apps_rg/runtime apps_rg/config tests docs plans .claude
rg -n "proof_pool|proof pool|proof_pool_resolver|allowed_pool|proof metadata" apps_rg/runtime apps_rg/config tests docs plans .claude
rg -n "fact_ledger|fact ledger|FactLedger" apps_rg tests docs plans .claude
rg -n "master_skills|master skills|master_skills_arsenal_ledger|selection_plan_skill_ref" apps_rg tests docs plans .claude
```

**Review rule**: fact-era names may remain only as explicit compatibility aliases while W2.1 migrates consumers to graph-era names. Proof-pool names may remain only for runtime compatibility when they carry GraphDB-approved selected evidence IDs and fail closed on unresolved IDs. References that only describe historical migration may remain in docs. Runtime, fixture, traversal, validator, and generator paths may not use `fact_ledger` as skills or metrics authority after W2. References to `master_skills_arsenal_ledger.json` may remain only as non-authoritative serialization/export/bootstrap/review labels or as resolver implementation detail behind `augmented_skills_graph`; user-facing diagnostics must not present it as a separate skills SSOT.

**Completion evidence**:
- Compatibility map from every fact-era runtime field to its graph-era replacement.
- Static audit showing graph-era fields are the preferred read path in validators, proof-pool metadata, and section packets.
- Static and runtime audit showing proof-pool plumbing is transport/cache only and all usable rows resolve to GraphDB-approved graph evidence IDs.
- Runtime proof that fact-era aliases do not admit, rank, prove, or select skills, metrics, claims, or sections.
- W2.2 E2E artifact includes both graph-era contract proof and compatibility-alias deprecation status.

### W4.2 - Traversal Explanation Packet

**Scope**: Emit the packet contract before final selection is passed into section generation.

**Expected packet fields** are listed in Wave 4 and must be present in artifacts for selected, demoted, and blocked skills.

**Verdict rule**: selected, demoted, blocked, missing, rebalance, and diagnostic-only outcomes must use the canonical verdict enum from Hardening Rules. Unknown verdicts fail closed.

### W5.2 - Waterfall Analysis

**Scope**: Produce a single waterfall artifact that joins all five stages.

**Minimum output tables**:
- `run_matrix`: target x stage x lane status.
- `skill_percent_breakout`: target x stage x lane x breakout dimension.
- `variance_drivers`: target x stage_transition x lane x driver.
- `waterfall_summary`: target x lane x A-to-E net change.

---

## Gap Register

**GAP-1: Role family too close to skill selection**
- Impact: A granular role family can behave like a keyword bucket.
- Closure: Role facets weight only GraphDB-eligible paths and typed edges control final proof.

**GAP-2: Final anti-overfit too late**
- Impact: A partner-heavy proof pool naturally generates partner-heavy text.
- Closure: Add traversal diagnostics and rebalance before generation.

**GAP-3: Source concentration invisible**
- Impact: IBM sections can overuse partnership facts while underusing platform/cloud/architecture proof.
- Closure: Source diversity diagnostics and section-specific caps.

**GAP-4: Proof and targeting can blur**
- Impact: JD/briefing terms can influence output as if they proved experience.
- Closure: Proof-targeting firewall and typed traversal packet.

**GAP-5: `fact_ledger` competes with GraphDB**
- Impact: Skills and metrics authority can drift between sources.
- Closure: Remove or fence `fact_ledger` skills/metrics authority before role-family or typed-edge changes.

**GAP-5A: `master_skills` wording creates a second-SSOT impression**
- Impact: Reports or diagnostics can appear to require a separate "master skills" authority even when the intended authority is GraphDB / `augmented_skills_graph`.
- Closure: Resolve selected skill refs through the `augmented_skills_graph` authority interface and label any JSON ledger usage as non-authoritative serialization/backend detail.

**GAP-5B: `proof_pool` wording creates a second-SSOT impression**
- Impact: Reports, validators, or generation code can appear to treat the proof pool as claim truth instead of a selected-evidence transport surface derived from GraphDB.
- Closure: Keep proof-pool plumbing only as a runtime cache for GraphDB-approved selected evidence IDs, prefer graph-era names in user-facing contracts, and fail closed on any row that cannot resolve to GraphDB authority.

**GAP-6: No waterfall means no causal attribution**
- Impact: E2E differences cannot be attributed to SSOT migration, role family, typed edges, or sliding-scale policy.
- Closure: Require the same three targets and 11 lanes at every stage with variance rationalization.

**GAP-7: Missing graph paths can be silently backfilled**
- Impact: Traversal can appear to pass while sourcing eligibility from JD, briefing, prompt context, historical output, generated text, or `fact_ledger`.
- Closure: Enforce `MISSING_GRAPH_PATH` or `BLOCKED_*` verdicts and fail closed on unknown verdicts.

**GAP-8: Prompt-only closure can mask traversal defects**
- Impact: Rewording prompts can reduce visible overfit without fixing selection, proof, or composition enforcement.
- Closure: Disallow prompt-only fixes as W3, W4, or W5 closure evidence.

**GAP-9: Candidate-fact authority pollutes the first graph baseline**
- Impact: W1 can measure legacy candidate-fact behavior instead of GraphDB traversal behavior.
- Closure: Move `candidate_fact` authority removal/fencing to P0, before the first 3 x 11 E2E baseline.

---

## Definition of Done

DoD-0: Candidate-fact authority is deprecated and tested before W1.
- Evidence: P0 inventory classifies all live `candidate_fact` references, disallowed authority paths fail closed, `candidate_fact_runtime_authority_read_fails_closed_before_W1` passes, W1 is blocked on failure, and remaining `candidate_fact_id` fields are lineage/compatibility only.
- Status: DONE

DoD-1: Finalized graph baseline without typed edges is captured.
- Evidence: Post-P0 W1 E2E run covers Anthropic, Truist, and Brown & Brown across all 11 lanes with graph-skill percent breakouts in `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/w1_finalized_graph_baseline_report.md` and `artifacts/apps_rg/waterfall/typed_edge_role_facet_guardrails/W1/w1_finalized_graph_baseline_report.json`.
- Status: DONE

DoD-2: GraphDB is the skills and metrics SSOT.
- Evidence: Static and runtime evidence shows `fact_ledger` is not used for skill eligibility, metric eligibility, weighting, proof, or traversal; proof-pool plumbing is transport/cache only and cannot admit proof outside GraphDB-approved selected evidence IDs; per-lane selected skill refs resolve through the `augmented_skills_graph` authority interface, with any JSON ledger usage labeled as non-authoritative backend detail.
- Status: TODO

DoD-3: GraphDB SSOT migration has E2E parity or explained variance.
- Evidence: W2 E2E run covers all 33 target-lane combinations and rationalizes variance from W1.
- Status: TODO

DoD-4: Role facets exist as reusable targeting weights, not direct skill selectors.
- Evidence: `high_role_facet_weight_cannot_select_unproven_skill`, `jd_keyword_cannot_create_proof_or_provenance`, and `section_block_overrides_high_facet_weight` pass.
- Status: TODO

DoD-5: Role-family E2E is complete.
- Evidence: W3 E2E run covers all 33 target-lane combinations with per-lane graph-skill percent breakouts and variance from W2.
- Status: TODO

DoD-6: Typed edge hierarchy is documented and implemented without replacing proof edges with role-family buckets.
- Evidence: Design/spec artifact plus code diff showing `apps_rg` GraphDB proof, provenance, employer, capability, section eligibility, targeting, and facet edges remain authoritative within resume generation.
- Status: TODO

DoD-7: Typed-edge E2E is complete.
- Evidence: W4 E2E run covers all 33 target-lane combinations, explains variance from W3 by edge category, and `missing_supporting_fact_blocks_claim_eligibility`, `missing_employer_binding_blocks_employer_scoped_claim`, and `typed_edge_missing_path_blocks_selected_skill_after_W4` pass.
- Status: TODO

DoD-8: Sliding-scale percentage policy is reviewed and implemented.
- Evidence: Caps, floors, penalties, and section-specific thresholds are documented and exercised.
- Status: TODO

DoD-9: Anti-overfit diagnostics run before generation.
- Evidence: A concentrated candidate pool returns `REBALANCE_REQUIRED` and blocks prompt assembly; `over_concentrated_pool_blocks_prompt_assembly_after_W5` and `repeated_metric_family_triggers_rebalance` pass.
- Status: TODO

DoD-10: Full five-stage waterfall is complete.
- Evidence: Report compares finalized graph, GraphDB SSOT, role family, typed edges, and sliding-scale stages for all targets and lanes.
- Status: TODO

DoD-11: Final text anti-overfit remains active.
- Evidence: Existing or updated tests cover copied JD phrasing, keyword stuffing, unsupported target-company claims, target role as past experience, repeated buzzwords, and `target_company_name_cannot_be_claimed_as_experience`.
- Status: TODO

DoD-12: Notion and disk status are synchronized.
- Evidence: Plans DB row exists with `Status=Not Started`, `Exists On Disk=true`, and `Plan File Path=plans/typed-edge-role-facet-guardrails-a6f3d2.md`; predecessor comment notes scoped supersession.
- Status: TODO

DoD-13: Hardening contract is enforced.
- Evidence: The authority stack invariant, no-silent-fallback rule, canonical traversal verdict enum, candidate-fact authority fence, and prompt-hack exclusion are covered by tests or runtime validators. Prompt-only changes are not accepted as closure evidence for W3, W4, or W5.
- Status: TODO

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```text
DISCOVERED_SCOPE: plan=typed-edge-role-facet-guardrails-a6f3d2 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=typed-edge-role-facet-guardrails-a6f3d2 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=typed-edge-role-facet-guardrails-a6f3d2 reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |

---

## Supersedes

| Predecessor slug | Reason |
|---|---|
| `phase2-gtm-presales-remaining-f7a2c9` | Scoped supersession only: replaces the completed typed bridge-edge / role-family design posture for future traversal work. The predecessor remains historical and terminal for completed Phase 2 graph scope. |

---

## Marker Quick Reference

Wave lifecycle markers must be at start of line and use exact plan id:

```text
WAVE_START: plan=typed-edge-role-facet-guardrails-a6f3d2 wave=<N>
WAVE_COMPLETE: plan=typed-edge-role-facet-guardrails-a6f3d2 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=typed-edge-role-facet-guardrails-a6f3d2 phase=<W1.1>
PLAN_COMPLETE: plan=typed-edge-role-facet-guardrails-a6f3d2 note="<final outcome>"
```
