---
plan_id: apps-rg-c03-resume-graph-hardening-9f3c2a
plan_format: v2
plan_type: hardening
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
base_ref: origin/main
base_sha: b94748ad26a7ca01f258805bb77f0d778aebec7d
---

# apps_rg C0.3 Resume Graph Retrieval and Allocation Hardening

## Plan state

- `PLAN_STATUS: IMPLEMENTATION_COMPLETE__RELEASE_EVIDENCE_PENDING`
- `CURRENT_WAVE: W9_RELEASE_EVIDENCE`
- `LAST_COMPLETED_WAVE: W9_ENGINEERING`
- `LAST_UPDATED: 2026-07-14`
- `IMPLEMENTATION_AUTHORIZED: W1-W9`
- `OFFICIAL_W6_STATUS: UNKNOWN`
- `OFFICIAL_W9_RELEASE_STATUS: UNKNOWN`
- `PROMOTION_ELIGIBLE: false`
- `STOP_CONDITION: official human W6 labels/adjudication and authorized W9 generation/coach evidence are not yet present`
- `DOWNSTREAM_DISPOSITION: W7-W9_ENGINEERING_COMPLETE__RELEASE_AND_PROMOTION_BLOCKED`

> **Implementation authority:** the user explicitly authorized W1-W9 and, on 2026-07-14, approved deterministic representative W6 proxy scoring so engineering could continue while real human scoring remains unavailable. The proxy is non-authoritative, future-replaceable engineering evidence only: it cannot set an official threshold, satisfy the W6 release gate, authorize W9 generation, or permit promotion. W7-W9 engineering is complete at implementation commit `29bee56aa39302d75141909a69999ab6e7201d6a`; official W6 and W9 release status remain `UNKNOWN`. C0.3 authority is this plan and its frozen C0.3 evaluation profile. Unrelated observability programs are not C0.3 dependencies. Automatic GitHub CI covers C0.3 code and contract paths only; SVP documentation gates are intentionally run separately by the user.

## 1. Objective

Harden the `apps_rg` C0.3 graph-skills path so a customized resume is:

1. authentic to the candidate's already-validated graph skills and metrics;
2. selected through deterministic, inspectable graph traversal rather than first-available loading;
3. globally allocated across the final resume, not greedily selected one section at a time;
4. free of repeated `skill_id` and `metric_outcome_id` use in the final visible resume under the default strict policy;
5. bound claim-by-claim to a complete graph path, source fact, and metric outcome when a metric is rendered;
6. fail-closed when evidence is empty, weak, conflicted, stale, blocked, or not externally eligible;
7. accompanied by complete traversal, alternative-candidate, confidence, selection, usage, and downstream binding receipts.

The truthfulness of skill and metric values in the canonical graph is an input assumption for this plan. This plan does **not** re-litigate or rewrite those values. It hardens retrieval, traversal, allocation, evidence binding, uniqueness, confidence, and release gates.

## 2. Non-negotiable product laws

### 2.1 Evidence authority

- A skill node is routing and semantic context, not standalone claim proof.
- Each externally visible claim must cite an externally eligible canonical fact.
- Each externally visible metric must bind to one canonical `metric_outcome_id`, its source fact, and a valid graph path.
- JD, target-company, target-title, and briefing content are targeting inputs only. They never become claim evidence.
- No C0.3 component may mint, infer, merge, interpolate, or recombine metrics.

### 2.2 Retrieval behavior

- Authority filters run **before** target-role/JD relevance scoring.
- The selector must enumerate and decision each eligible candidate within the bounded traversal plan before allocation.
- No child skill or metric may be selected by source-list slicing, first-match logic, insertion order, or early top-N truncation.
- Budget limits apply after deterministic eligibility and candidate enumeration, not as a shortcut that hides alternatives.
- Missing or weak context gets one bounded C0.6 refinement. If it remains weak, the section blocks or abstains.

### 2.3 Whole-resume uniqueness

Default strict policy for the final materialized resume:

- `max_resume_uses(skill_id) = 1`
- `max_resume_uses(metric_outcome_id) = 1`
- `max_resume_uses(normalized_metric_value + unit + semantic_family) = 1`
- `max_section_uses(skill_id) = 1`
- `max_section_uses(metric_outcome_id) = 1`
- repeated `(skill_id, metric_outcome_id, fact_id)` triples are always forbidden
- duplicate metric prose or semantically equivalent numeric claims are forbidden even if different lane outputs use different wording

An optional future `anchor_skill_exception` may permit one explicitly named anchor skill to occur twice for ATS/coherence, but it is **disabled by default**, must use different claim units and source facts, and requires an explicit policy receipt. It is not part of initial acceptance.

### 2.4 Same-run state and write sovereignty

- The current-run uniqueness ledger is a sealed run artifact owned by the allocation workflow.
- Selection must not mutate the generated SQLite graph projection during retrieval.
- Historical usage may be proposed after Exit, but no runtime component may directly write durable graph state. Any future durable promotion follows the repo's UWG/write-gateway law.

## 3. Resume-coaching product correction

“Each section uses graph skills and metrics” must be implemented as **machine-verifiable graph evidence for each claim-bearing generated lane**, not as forcing visible numbers into each section.

- Headline: show unique leaf skills; normally no visible numeric metric.
- Executive summary: show a small number of unique skills and one or two high-value outcomes.
- Competencies: show unique skills; metric-linked proof can strengthen selection, but numeric metrics should normally remain invisible.
- Experience bullets: show the strongest natural outcomes and unique skills.
- Narrative and bullet lanes for the same employer are alternative renderings of the same role, not two independent final-resume sections. The final resume must materialize one representation or explicitly share one `claim_unit_id` and count it once.
- Locked identity, education, and certification sections get integrity/lineage receipts; they are not forced to consume a skill or metric merely to satisfy a count.

This prevents keyword stuffing and unnatural resumes while still proving that C0.3 shaped each generated claim-bearing section.

## 4. Current-state verdict at pinned `origin/main`

Current main is materially stronger than older archive-era reviews:

- all eleven generated lanes are represented as graph-backed lanes;
- competencies now bind to a canonical selected graph plan;
- first-class `metric_outcome` nodes and SQLite selection projections exist;
- graph authority, JD-as-targeting, and fact-as-proof boundaries are documented;
- deterministic ranking, soft novelty penalties, and some rejected-sibling receipts exist;
- final assembly runs cross-section overlap and graph-coherence checks.

It does **not** yet satisfy the strict product target in this plan. The highest-risk gaps are global allocation, actual traversal proof, hard no-reuse, fail-open fallbacks, exact claim-path binding, calibrated confidence, and final-resume enforcement.

## 5. Gap inventory

| ID | Severity | Gap | Current risk | Required closure |
|---|---:|---|---|---|
| G01 | P0 | Multiple selection/contract surfaces | Role-episode selection, SQLite ranking/context, and native C0.3 expose overlapping but non-identical authority and receipts. | One authoritative `ResumeGraphAllocationPlan` and one adapter boundary. |
| G02 | P0 | Lazy child skill loading | Role-episode selector slices `raw_skill_ids[:cap]`; alternatives are not scored before selection. | Enumerate, gate, score, and decision all bounded child candidates before allocation. |
| G03 | P0 | Synthetic traversal receipt | Some receipts reconstruct visited/frontier data from selected arrays rather than recording attempted nodes/edges. | Event-sourced bounded traversal with terminal disposition for each attempted candidate. |
| G04 | P0 | No whole-resume allocator | Sections select independently, so order and local choices can exhaust the best evidence or repeat it. | Gather all section candidate sets, then solve one deterministic constrained allocation. |
| G05 | P0 | No hard skill reuse ledger | There is no current-run `skill_id` reservation/usage authority. | Run-local skill/metric/fact usage ledger with atomic reservations. |
| G06 | P0 | Metric reuse is soft and permissive | Local penalties permit repeats; assembly fails only when the same metric/fact appears in at least three sections. | Hard zero-reuse at allocation and final assembly. |
| G07 | P0 | Usage memory is not run-scoped or live-wired | `resume_metric_usage` queries aggregate across runs and the write helper has no authoritative runtime call path. | Do not use mutable SQLite history for same-run uniqueness; scope historical analytics explicitly. |
| G08 | P0 | Fail-open fallback bypass | Empty ranked results can fall back to broad fact links or label/tag matching. | Remove proof-bypassing fallback; one bounded refinement, then `EMPTY/WEAK/BLOCKED`. |
| G09 | P0 | Authority filters incomplete | External eligibility, activation, support, human confirmation, freshness, section permission, path validity, and edge policy are not uniformly hard prefilters. | One reusable hard-gate predicate applied before target scoring. |
| G10 | P0 | Metric bucket used as proxy | Selection penalizes a skill's metric bucket even when no exact metric outcome is allocated. | Treat `metric_outcome_id` as first-class candidate and usage key. |
| G11 | P0 | Target inputs can influence ranking too early | JD/brief signals can shape root/rank choices before all node/path proof gates are established. | Gate authority first; use targeting only for ranking eligible paths. |
| G12 | P0 | Rank score mislabeled as confidence risk | Categorical confidence is converted to an uncalibrated score contribution; no empirical calibration. | Separate categorical authority, raw rank, proof confidence, target alignment, and calibrated probability. |
| G13 | P0 | Proof strictness uneven across lanes | Only selected lanes receive the strictest C0.4 proof posture; cross-section graph warnings can remain non-blocking. | All claim-bearing generated lanes require exact graph/fact support and blocking failures. |
| G14 | P0 | Claim binding is too shallow | ID intersections and phrase/citation checks do not prove exact claim→skill→fact→metric paths. | Canonical `GraphClaimBinding` per visible claim with path and edge IDs. |
| G15 | P0 | Downstream digest chain incomplete | Selection plan equality is proven locally, but PA/L2/claim ledger/X2/X1D/X3/final parity is not globally bound. | Carry and verify allocation-plan digest at each stage. |
| G16 | P1 | Alternative receipts incomplete/truncated | Siblings are fetched only around selected skills, capped per skill; expansion summaries truncate rejection rows. | Full authoritative candidate-decision artifact plus compact display summary. |
| G17 | P1 | Greedy fact/section order bias | Facts and sections are processed sequentially; same inputs in a different order can change allocations. | Global optimization and permutation-invariance tests. |
| G18 | P1 | Narrative and bullet duplication semantics | Final assembly includes both narrative and bullet lanes for each employer. | Choose one final representation or bind both to one counted claim unit. |
| G19 | P1 | C0.6 refinement disabled | Weak support does not receive the bounded refinement described by the architecture. | One deterministic broaden/decompose/retry pass with a receipt. |
| G20 | P1 | Graph coherence is breadth-oriented and warn-only | Current whole-resume receipt checks a low minimum of active sections/unique skills but not path completeness or reuse. | Blocking whole-resume graph-evidence contract with per-section parity and zero reuse. |
| G21 | P1 | Depth metrics are structural and gameable | Counts/ratios can pass despite weak semantic claim support or repeated source concentration. | Add entailment, independence, leafness, and source-concentration gates. |
| G22 | P1 | Canonical substrate identity is ambiguous | Generic C0.3 docs and `apps_rg` implementation describe different JSON/SQLite/GraphDB authority roles. | Freeze an app-specific authority matrix and adapter contract; no parallel truth. |
| G23 | P1 | Standalone lane cannot prove whole-resume uniqueness | A single section run lacks other-section reservations but can appear globally compliant. | Mark `scope=SECTION_ONLY`; require a whole-run allocation plan for global claims. |
| G24 | P1 | No final rendered-output skill/metric scan | Existing overlap logic operates on text/fact patterns, not exact graph allocation IDs. | Final materialization must reconcile rendered claims to allocation and usage ledgers. |
| G25 | P1 | CI ratchet is manual and incomplete | Graph-skills authority workflow is `workflow_dispatch` only and omits current SQLite/global-allocation tests. | PR/push path-triggered strict ratchet and required check. |
| G26 | P1 | Retrieval/evidence evaluation is incomplete | No labeled Recall@K/nDCG, candidate-decision coverage, confidence calibration, or path-faithfulness suite. | Gold fixtures, retrieval metrics, calibration report, and release thresholds. |
| G27 | P2 | Receipt observability lacks complete stop/budget telemetry | Some artifacts omit attempted edges, gate latencies, stop reason, and conservation hashes. | Complete traversal manifest, OTEL spans, and deterministic hashes. |
| G28 | P2 | Existing hardening validator is inventory-oriented | It validates graph shape/heterogeneity and marker rows, not live no-reuse or claim binding. | Replace/extend with runtime contract and full-resume validators. |

## 6. Target architecture

### 6.1 One authoritative flow

```text
L1/L0 section intents
    -> C0.3 authority prefilter
    -> bounded graph traversal for each final claim-bearing section
    -> exhaustive eligible candidate sets + terminal rejection ledger
    -> whole-resume constrained allocation
    -> immutable ResumeGraphAllocationPlan + UsageLedger
    -> per-section FinalEvidenceContract slices
    -> PA/L2 generation
    -> exact GraphClaimBinding validation
    -> C0.4/C0.7 + X2/X1D/X3
    -> final materialization reconciliation
```

### 6.2 New/updated contracts

1. `ResumeGraphSelectionPolicyV2`
   - graph snapshot/version/hash
   - final output mode
   - section budgets
   - authority filters
   - max hops/nodes/edges/candidates
   - hard uniqueness rules
   - target-alignment weights
   - confidence policy/version
   - bounded refinement policy

2. `C03TraversalEventV1`
   - event sequence
   - section and request IDs
   - node/edge/path identifiers
   - hop depth
   - gate inputs and verdicts
   - accepted/rejected/expanded/terminal state
   - stop reason and budget counters

3. `C03CandidateDecisionV2`
   - candidate tuple `(section_id, claim_unit_id, skill_id, fact_id, metric_outcome_id?)`
   - full path and edge IDs
   - authority-gate result
   - proof components
   - target score
   - selected/rejected disposition
   - competing selected candidate
   - deterministic reason code

4. `ResumeGraphAllocationPlanV1`
   - all final section assignments
   - selected and rejected candidate IDs
   - global objective and solver metadata
   - stable tie-break rule
   - uniqueness and budget receipts
   - graph/policy/source digests

5. `ResumeGraphUsageLedgerV1`
   - current-run reservations by `skill_id`, `metric_outcome_id`, normalized metric signature, fact ID/family, claim unit, and section
   - no direct database mutation
   - allocation-plan digest

6. `GraphClaimBindingV1`
   - visible claim text/hash
   - section and claim unit
   - selected skill(s)
   - source fact(s)
   - optional metric outcome
   - graph path/edge IDs
   - citations
   - proof/target scores
   - exact plan-digest binding

7. `WholeResumeGraphEvidenceContractV1`
   - section parity
   - final rendered claim reconciliation
   - zero reuse
   - complete traversal and candidate conservation
   - confidence/calibration status
   - X2/X1D/X3/final digest parity

### 6.3 Global allocation algorithm

Codex must ADG-audit available dependencies before choosing an implementation. Prefer the simplest deterministic solver that meets the constraints:

- small-pool pure-Python branch-and-bound or min-cost assignment; or
- an already-approved optimization dependency if present.

Do not add a new solver dependency without approval.

Hard constraints:

- all authority gates pass;
- section/employer locality holds;
- required graph node/edge types exist;
- `skill_id` and `metric_outcome_id` have zero reuse in final visible output;
- normalized metric signatures have zero reuse;
- section min/max budgets hold;
- each visible metric binds to its exact fact and metric node;
- each claim has at least one complete claim path;
- source concentration limits hold;
- final representation policy excludes double-counting narrative/bullet variants.

Objective order, lexicographic unless the approved solver proves equivalent:

1. maximize minimum proof quality;
2. maximize total proof quality and source independence;
3. maximize role/JD alignment among eligible candidates;
4. maximize section and capability-family coverage;
5. maximize metric and skill diversity;
6. maximize selection margin over rejected alternatives;
7. stable ID tie-break.

The output must be invariant to candidate input order, fact order, and section dispatch order.

## 7. Section evidence policy

| Final section type | Machine C0.3 evidence | Visible skill target | Visible numeric metric target | Rule |
|---|---|---:|---:|---|
| Headline | required | 2–4 unique leaf skills | 0 normally | No forced numeric outcome; prove all surfaced capability phrases. |
| Executive summary | required | 3–5 unique skills | 1–2 unique outcomes | Use only high-confidence, high-level outcomes not allocated elsewhere. |
| Competencies | required | 8–12 unique leaf skills | 0 normally | Metric-linked facts may support confidence but numbers stay out unless explicitly requested. |
| Employer bullets | required | 1–2 unique skills per bullet | 0–1 per bullet; at least one per role when strong evidence exists | Each bullet is a claim unit with employer-local facts. |
| Employer narrative | required as an alternate rendering | derived from allocated role claim units | no new metric allocation | Cannot coexist as a separately counted final section with bullets. |
| Early career | locked/lineage receipt | no forced skill | no forced metric | Preserve canonical copy. |
| Education | locked/lineage receipt | no forced skill | no forced metric | No artificial graph stuffing. |
| Certifications | locked/lineage receipt | certification node lineage only | no forced metric | Preserve exact credential facts. |

## 8. Confidence and evaluation policy

### 8.1 Never conflate these quantities

- `authority_pass`: deterministic boolean; never averaged.
- `graph_confidence_grade`: canonical categorical graph metadata, not a probability.
- `proof_strength_raw`: deterministic ranking feature.
- `target_alignment_score`: JD/role fit; cannot rescue weak proof.
- `claim_entailment_score`: claim supported by cited fact(s).
- `metric_binding_score`: metric text/value/unit exactly supported by its metric node/fact.
- `path_confidence_raw`: path and edge quality.
- `source_independence_score`: independent proof diversity.
- `selection_margin`: difference from best eligible rejected alternative.
- `proof_confidence_calibrated`: probability-like value only after calibration on labeled data.

### 8.2 Initial release gates

These are starting policies, not claims that current scores are already calibrated:

| Gate | Initial target |
|---|---:|
| Hard authority gates | 100% pass |
| Candidate terminal-decision coverage | 100% |
| Traversal conservation | 100% |
| Selected path completeness | 100% |
| Claim-to-plan binding coverage | 100% |
| Final skill reuse violations | 0 |
| Final metric-outcome reuse violations | 0 |
| Final normalized metric-signature reuse violations | 0 |
| Section/order permutation invariance | 100% |
| Gold candidate Recall@K | ≥ 0.95 |
| Gold ranking nDCG@K | ≥ 0.90 |
| Metric binding score for rendered metrics | ≥ 0.95 after calibration baseline exists |
| Claim entailment score | ≥ 0.90 after calibration baseline exists |
| Calibrated proof confidence | ≥ 0.90 for selected visible claims |
| Expected Calibration Error | target ≤ 0.05 after sufficient labeled fixtures |
| Brier score | improve against frozen baseline; set absolute ratchet after W6 baseline |
| C0.3 weak refinement attempts | maximum 1 |

Before calibration exists, use categorical authority/status gates and raw rank only for ordering. Do not display an uncalibrated number as “confidence.”

### 8.3 Evaluation dimensions

Track separately:

1. retrieval relevance and recall;
2. graph-path correctness;
3. claim faithfulness/entailment;
4. metric exactness;
5. target relevance;
6. whole-resume coverage/diversity;
7. no-reuse and source-concentration compliance;
8. human resume quality: clarity, naturalness, executive signal, ATS fit, and authenticity.

## 9. Hardened implementation waves

## W0 — Pin, map, baseline, and freeze the contract matrix

**Purpose:** establish reproducible current-main evidence before edits.

### Tasks

1. Run strict Codex readiness and confirm clean worktree.
2. Fetch and pin `origin/main`; record the exact SHA. Stop if it differs from the plan SHA until the plan is rebased and reviewed.
3. Load repo memory and governing rules.
4. Use ADG before grep to map producers/consumers for:
   - role-episode graph selector;
   - SQLite graph selection/context;
   - native C0.3 contract;
   - proof-pool resolver;
   - C0.4/C0.7;
   - all eleven lane PA/L2/X2/X1D/X3 paths;
   - modular whole-run orchestration, rollup, and final assembly;
   - graph-skills CI workflows.
5. Run focused existing tests and validators without changing code.
6. Build a finite contract matrix: invariant × lane × stage × final assembly.
7. Generate adversarial baseline fixtures and measure:
   - skill/metric repeats;
   - candidate order sensitivity;
   - section order sensitivity;
   - candidate decision coverage;
   - traversal receipt completeness;
   - path completeness;
   - fallback behavior;
   - downstream digest parity.

### Required artifacts

- `docs/reports/apps_rg/c03_resume_graph_w0_baseline.json`
- `docs/reports/apps_rg/c03_resume_graph_contract_matrix.json`
- `docs/reports/apps_rg/c03_resume_graph_adg_impact.json`
- command transcripts under the repo-approved report path

### Exit gate

- no production edits;
- baseline and matrix validate;
- each gap maps to at least one contract row and one later wave;
- plan is updated with any base drift and submitted for explicit implementation approval.

## W1 — Contract and authority consolidation

**Purpose:** define one selection/allocation authority before changing ranking behavior.

### Tasks

1. Add schemas/dataclasses for all contracts in §6.2.
2. Define the app-specific graph authority matrix:
   - canonical source ledger;
   - generated SQLite projection;
   - traversal adapter;
   - current-run plan/ledger artifacts;
   - optional future historical usage projection.
3. Designate one public C0.3 candidate-selection entrypoint.
4. Make legacy selectors/adapters call the authority or emit explicit compatibility receipts; no independent selection logic.
5. Define final-output representation policy for narrative vs bullet lanes.
6. Define standalone-section scope and prohibitions.
7. Add schema validators and digest functions before wiring runtime behavior.

### Likely files

- new focused modules under `apps_rg/runtime/c0/`
- `apps_rg/runtime/sections/graph_role_episode_selector.py`
- `apps_rg/runtime/c0/c03_sqlite_graph_selection.py`
- `apps_rg/runtime/native_c03_skills_graph.py`
- `apps_rg/runtime/proof_pool_resolver.py`
- schemas under the repo-approved `apps_rg` schema surface

### Exit gate

- one authority entrypoint;
- no dual plan digest for the same section;
- schema negative controls pass;
- no `agentic_core` edit.

## W2 — Hard authority prefilters and graph adapter boundary

**Purpose:** ensure only valid candidates can be ranked.

### Tasks

1. Implement one reusable eligibility predicate for nodes, edges, links, paths, facts, and metrics.
2. Require:
   - active/confirmed activation;
   - external eligibility;
   - allowed section and route;
   - claim-eligible fact link;
   - human confirmation where required;
   - current graph projection/version/hash;
   - valid path and edge policy;
   - allowed data/source class;
   - confidence not blocked/unknown;
   - no contradiction/supersession blocker.
3. Apply this predicate before target-role/JD/brief scoring.
4. Remove `approved_by_graph_presence` as sufficient verification.
5. Remove broad label/tag/fact-link proof fallback.
6. Treat empty, stale, or invalid projection as fail-closed.
7. Keep SQLite behind the adapter; high-level C0.3 code cannot issue ad hoc selection queries.

### Exit gate

- blocked high-score candidate never wins;
- missing/stale graph blocks;
- target text cannot widen authority;
- negative-control fixtures pass.

## W3 — Actual bounded traversal and exhaustive alternative accounting

**Purpose:** eliminate synthetic receipts and lazy loading.

### Tasks

1. Traverse bounded graph paths from section/role/employer roots through skill, fact, and metric nodes.
2. Record each attempted node and edge as `C03TraversalEventV1`.
3. Assign one terminal decision to each candidate path:
   - selected candidate pool;
   - rejected authority;
   - rejected path;
   - rejected confidence;
   - rejected relevance;
   - rejected budget;
   - rejected global conflict;
   - not reached because bounded stop condition.
4. Enumerate all bounded children before applying top-K allocation budgets.
5. Remove list slicing and first-match selection.
6. Persist full authoritative receipts; compact display artifacts may be truncated but must reference the full hash.
7. Add deterministic traversal-manifest hash and OTEL spans.

### Exit gate

- candidate decision coverage and traversal conservation are 100%;
- same graph/policy/query produces the same manifest;
- no traversal proceeds through a rejected node;
- all alternative candidates have reason codes.

## W4 — Whole-resume constrained allocation and zero reuse

**Purpose:** make global selection authoritative before generation.

### Tasks

1. Gather candidate sets for each final claim-bearing lane.
2. Resolve narrative/bullet final representation policy.
3. Run one deterministic global allocator.
4. Emit `ResumeGraphAllocationPlanV1` and `ResumeGraphUsageLedgerV1`.
5. Enforce all strict uniqueness constraints.
6. Add source-fact/family concentration limits and employer locality.
7. Reserve evidence atomically within the plan; no mutable SQLite writes.
8. Slice the frozen plan into section-specific FinalEvidenceContracts.
9. Make dispatch order irrelevant.
10. Mark standalone runs `SECTION_ONLY` and prohibit global uniqueness claims.

### Exit gate

- zero repeated skill or metric IDs/signatures in final-visible allocation;
- permutation tests pass;
- impossible allocation fails with explicit unsatisfied constraints instead of silent reuse;
- plan digest is stable.

## W5 — Exact claim/skill/fact/metric binding and section render contracts

**Purpose:** ensure generated text uses only its allocation.

### Tasks

1. Add `GraphClaimBindingV1` to all generated lane output schemas.
2. Require exact path and edge IDs for each visible claim.
3. Require exact metric node/fact/value/unit binding for each rendered metric.
4. Prevent causal merging of unrelated facts/metrics.
5. Enforce section budgets from §7.
6. Make narrative lanes derived renderings that cannot allocate new evidence.
7. Require all claim-bearing lanes to use strict C0.4 proof posture.
8. Block orphan skills, facts, metrics, and source IDs.
9. Update PA guardrails, repair code, deterministic X2, and judge rubrics together.

### Exit gate

- 100% claim binding coverage;
- metric exactness negative controls pass;
- unsupported claim or metric cannot reach X3_ALLOW;
- headline/competencies remain natural and are not forced to display numbers.

## W6 — Confidence calibration, retrieval evaluation, and bounded refinement

**Purpose:** make “confidence” meaningful and measurable.

### Tasks

1. Implement separate score fields from §8.1.
2. Freeze a labeled evaluation set across target profiles and sections.
3. Measure Recall@K, nDCG@K, MRR, path accuracy, entailment, metric binding, and selection margin.
4. Calibrate proof confidence on held-out labeled fixtures; report ECE and Brier.
5. Add one deterministic C0.6 refinement for weak/empty coverage.
6. Ensure refinement cannot widen ACL/authority or alter route.
7. Set thresholds from measured baseline and record policy version.
8. Keep target alignment non-authoritative.

### Exit gate

- no uncalibrated probability label;
- release thresholds pass on held-out fixtures;
- refinement is bounded, receipted, and fail-closed.

### W6 engineering disposition (updated 2026-07-14)

- **Engineering complete:** separate raw score fields, deterministic isotonic calibration, ECE/Brier reporting, Recall@K/nDCG@K/MRR/path/authority/entailment/metric/margin evaluation, future-run-only threshold candidacy, one bounded C0.6 retry, and the C0.7 receipt binding are implemented.
- **Frozen source complete:** six real allocator cases were frozen from clean source commit `c56c75bf9e28455e5c206588f6c53003c8684497`, producing 282 proof items, 84 full bounded-universe retrieval queries, 57 binding-only proof split groups, and zero W9 pairs.
- **Blind review materials complete:** proof and retrieval distributions are isolated, secret-HMAC blinded, source/manifest/checksum pinned, owner-only, outside the repository, and accompanied by a private human-authority receipt template. No labels or reviewer identities were fabricated.
- **Approved representative proxy:** the deterministic `PROVISIONAL_MODEL_PROXY` baseline uses the previously frozen W6 packet and canonical profile without fabricating reviewers, labels, adjudications, or official authority. Its committed sanitized summary is `docs/reports/apps_rg/c03_resume_graph_w6_proxy_baseline.json` (SHA-256 `b2eb273826bbfba6b8c35b5378e15e946d54390b364b7a6ca4142aeaf9635573`; record digest `3b7686578e863513ede32d19c9345c1b3432241fffe3d9b3fc36b0f57e2267e8`).
- **Representative measurements:** authority eligibility `1.0`, exact-path accuracy `1.0`, metric-binding accuracy `1.0`, claim entailment `0.7142857142857143`, ECE `0.08184523809523811`, Brier `0.19606894841269842`, Recall@10 `0.35560404848039256`, nDCG@10 `0.5257259181730278`, and MRR `0.5283403104831675`. Authority, path, and metric-binding targets are met; entailment, calibration, retrieval, and proof-support targets are not. Floor and precision remain unmeasured.
- **Exit gate still open:** official W6 remains `UNKNOWN`; no release threshold is activated and promotion remains false until rostered humans provide the frozen reviews, adjudication, validation, sealed export, and held-out metrics required by the official gate.
- **Historical stop superseded for engineering only:** the user's proxy authorization allowed W7-W9 implementation and test work to proceed. It did not authorize W9 release execution or promotion.

## W7 — End-to-end digest binding and whole-resume release gate

**Purpose:** prove that the selected plan is the plan that reaches the user.

### Tasks

1. Bind allocation-plan digest through:
   - selected fact plan;
   - FinalEvidenceContract;
   - compiled prompt artifact;
   - L2 output;
   - canonical claim ledger;
   - X2;
   - X1D;
   - X3;
   - rollup;
   - final resume assembly.
2. Add `WholeResumeGraphEvidenceContractV1`.
3. Reconcile final rendered claims against bindings and the usage ledger.
4. Replace warn-only graph breadth checks with blocking contract failures for:
   - missing lane evidence;
   - weak materiality;
   - reuse;
   - digest drift;
   - missing traversal;
   - orphan claims/metrics.
5. Retain text-overlap checks as secondary quality checks, not graph authority.

### Exit gate

- all digests equal the frozen allocation plan;
- final materialized resume has zero graph allocation drift;
- any UNKNOWN is non-PASS;
- final assembly cannot include both alternative role renderings as separately counted claims.

### W7 engineering disposition (2026-07-14)

- `WholeResumeGraphEvidenceContractV1` now binds the allocation plan, per-section evidence contracts, visible claim bindings, exact artifact hashes, traversal conservation, uniqueness, and the official W6 receipt through modular generation, X2, final X2, and final assembly.
- Engineering status is complete and verified. `engineering_pass` is distinct from `release_pass`; any missing or non-PASS official W6 receipt keeps release false.
- The final resume, manifest, X2 surfaces, and whole-resume receipt carry the contract reference and digest. Failures in artifact parity, claim coverage, path conservation, reuse, or W6 authority fail closed.
- Release status remains `UNKNOWN` pending official W6 human evidence and an authorized full generation.

## W8 — Tests, mutation suite, CI ratchet, and observability

**Purpose:** make regressions impossible to merge silently.

### Required tests

Unit and contract tests for:

- candidate input-order permutation;
- fact-order permutation;
- section-order permutation;
- blocked candidate with highest target score;
- stale/missing graph projection;
- disconnected skill/fact/metric path;
- unconfirmed or internal-only evidence;
- duplicate skill and metric across sections;
- semantically equivalent metric signatures;
- empty eligible pool;
- weak confidence and low selection margin;
- prohibited fallback;
- complete candidate conservation;
- sibling/alternative reason completeness;
- exact plan-digest drift;
- all eleven generated lanes;
- narrative/bullet alternative representation;
- final rendered-output reconciliation;
- standalone section scope;
- no direct durable-state mutation.

Add mutation-style negative controls that deliberately remove each gate or alter each digest and prove the suite fails.

### CI tasks

1. Extend `graph-skills-authority-ratchet.yml` to run on relevant PR/push paths or route the same suite through required `contract-gates` lanes.
2. Include current SQLite selector, shared-lane skew, allocation, claim-binding, whole-resume, and calibration tests.
3. Publish machine-readable receipts and selected diagnostics.
4. Fail on UNKNOWN, missing artifacts, stale baselines, or warning-only authority failures.
5. Keep the `agentic_core` no-diff boundary unless a separate author gate approves migration.

### Exit gate

- required CI check runs automatically on graph/resume changes;
- all negative controls fail for the intended reason;
- no flaky/order-sensitive test;
- focused and apps-contract suites pass.

### W8 engineering disposition (2026-07-14)

- A C0.3-specific automatic PR/push ratchet now runs on relevant C0.3 code and contract paths. SVP documentation paths and documentation gates are intentionally excluded for separate user execution.
- The ratchet records strict-suite results independently from the pinned W0 external diagnostic. Locally, the strict suite passed with 234 passed, 1 skipped, and 1 deselected; the separate diagnostic reproduced the exact known `agentic_core/L0_routing/__init__.py contains augmented_skills_graph` baseline failure.
- Ratchet receipt v3 passed with record digest `11c87fa5a83597418dbd02c109a5d5018ab6443d000e17eeec337ae7ea470292`. A changed external failure signature is rejected; the exact pinned signature or an improvement is accepted without hiding the debt.
- No `agentic_core` code is changed. GitHub-hosted execution remains to be verified on the draft PR.

## W9 — Shadow rollout, resume-coach review, and closeout

**Purpose:** prove product quality, not only structural correctness.

### Tasks

1. Shadow old and hardened selection on representative target profiles:
   - AI partnerships/GTM;
   - SVP agentic engineering/platform;
   - insurance IT strategy/modernization.
2. Compare:
   - proof quality;
   - target relevance;
   - skill/metric uniqueness;
   - source concentration;
   - claim naturalness;
   - ATS keyword coverage;
   - executive readability;
   - traversal/alternative coverage;
   - latency and candidate budgets.
3. Conduct blinded resume-coach review with a fixed rubric.
4. Run complete modular whole-resume generation and final assembly.
5. Emit closeout receipt and rollback instructions.
6. Promote only when all release gates pass. Rollback may change code version, never weaken evidence gates.

### Exit gate

- all structural gates pass;
- no skill or metric reuse in the final visible resume;
- all claim-bearing generated sections have graph traversal and claim-binding evidence;
- human quality is no worse than baseline and target relevance improves or remains equal;
- closeout receipt validates.

### W9 engineering disposition (2026-07-14)

- A fail-closed closeout harness requires six unique blinded comparison pairs, two qualified independent reviews per pair, six adjudications, an official W6 `PASS`, a whole-resume `release_pass`, and explicit authorization for generation.
- Harness implementation and negative controls are complete. No resume variants, human reviews, adjudications, or quality conclusions were fabricated.
- Actual representative generation and blinded resume-coach review remain external release inputs. Official W9 status is `UNKNOWN`; promotion is false.

## 10. Primary code surfaces for ADG confirmation

Codex must confirm impact before editing. Expected surfaces include:

- `apps_rg/runtime/sections/graph_role_episode_selector.py`
- `apps_rg/runtime/c0/c03_sqlite_graph_selection.py`
- `apps_rg/runtime/c0/c03_graph_expansion.py`
- `apps_rg/runtime/c0/evidence_room.py`
- `apps_rg/runtime/c0/c04_stratify.py`
- `apps_rg/runtime/c0/c07_handoff_audit.py`
- `apps_rg/runtime/native_c03_skills_graph.py`
- `apps_rg/runtime/c03_graph_sqlite_context.py`
- `apps_rg/runtime/proof_pool_resolver.py`
- `apps_rg/runtime/sections/graph_evidence_contract.py`
- `apps_rg/runtime/graph_skills_utilization_scorer.py`
- `apps_rg/runtime/aggregation/cross_section_x2.py`
- `apps_rg/runtime/assembly/final_resume_x2.py`
- `apps_rg/runtime/internal/final_resume_assembler.py`
- `apps_rg/l2_recipe/modular_resume_generation.py`
- `apps_rg/fact_inventory/graph_sqlite_path_index.py`
- `apps_rg/fact_inventory/augmented_skills_graph_sqlite.py`
- `apps_rg/fact_inventory/validate_c03_graph_hardening.py`
- relevant lane PA/X2/X1D/X3 modules
- `.github/workflows/graph-skills-authority-ratchet.yml`
- `ops_scripts/ci/classify_ci_lanes.py` if contract-gate routing is used
- tests under `tests/unit/apps_rg/`, `tests/unit/apps_rg/runtime/c0/`, and `tests/_apps_contract/`

Do not edit `agentic_core` under this plan. If ADG shows a core contract must change, stop and request an author-gated migration plan.

## 11. Verification command set

Codex must adapt exact paths after W0 ADG discovery, but the minimum runbook is:

```powershell
# Preflight
python scripts/governance/codex_readiness.py --json --require-clean-worktree --fail-duplicate-processes
python tools/adg/adg_cli.py status --json
python scripts/governance/verify_codex_enforcement_home.py --json

git fetch origin
git status --short --branch
git rev-parse origin/main

# Existing baseline
python apps_rg/fact_inventory/validate_c03_graph_hardening.py
python -m pytest tests/unit/apps_rg/runtime/c0/test_c03_sqlite_graph_selection.py -q
python -m pytest tests/unit/apps_rg/test_shared_lane_skew_elimination.py -q
python -m pytest tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py -q

# Wave-specific suites added by this plan
python -m pytest tests/unit/apps_rg/runtime/c0/ -q
python -m pytest tests/unit/apps_rg/ -q
python -m pytest tests/_apps_contract/ -q

# Governance/closeout
python scripts/governance/verify_codex_primary.py
python scripts/governance/codex_readiness.py --json
python scripts/governance/verify_codex_run_receipt.py <receipt.json>
git diff --check
```

All subprocesses invoked by code or scripts must remain bounded by the repository timeout law.

## 12. Wave execution protocol for Codex

For each wave:

1. Re-read this plan and current governing `AGENTS.md` files.
2. Confirm base and worktree state.
3. Run ADG impact for the intended edit set.
4. Update the finite contract matrix before code.
5. Add failing tests/negative controls first.
6. Implement the smallest authority-preserving change.
7. Run focused tests, then broader apps tests, then contract gates.
8. Emit machine-readable wave receipt with:
   - base/head SHA;
   - changed files;
   - contract rows closed;
   - tests and command results;
   - artifacts and hashes;
   - unresolved gaps;
   - stop-condition checks.
9. Update plan state markers.
10. Stop at the end of each wave for review unless the user explicitly authorized multi-wave execution.

## 13. Stop conditions

Stop and report rather than weakening policy when:

- `origin/main` moved and the plan has not been rebased/reviewed;
- worktree is dirty outside declared scope;
- ADG is unavailable for a structural edit after the allowed fallback procedure is exhausted;
- implementation requires an `agentic_core` change;
- a candidate cannot meet hard authority gates;
- global uniqueness cannot be satisfied with the available evidence;
- graph source/projection hashes disagree;
- a metric lacks an exact metric node/fact/path;
- a test reveals an unrelated baseline failure outside declared scope;
- a CI/governance change exceeds this plan's approved surface;
- confidence thresholds cannot be calibrated from adequate labeled data.

The correct product outcome in these cases is a sealed block, weak-with-caveats packet, bounded abstention, or a revised plan—not silent reuse or fallback.

## 14. Definition of done

This plan is complete only when all of the following are demonstrated on a clean branch based on current main:

- one authoritative C0.3 selection/allocation path;
- complete bounded traversal receipts for each claim-bearing generated section;
- 100% candidate terminal-decision coverage;
- no lazy/first-available child selection;
- one frozen whole-resume allocation plan before generation;
- zero final visible skill-ID reuse;
- zero final visible metric-outcome/signature reuse;
- exact claim→skill→fact→metric path binding;
- all hard authority gates applied before targeting scores;
- one bounded weak-support refinement, then fail-closed;
- calibrated confidence reported separately from target alignment;
- all PA/L2/X2/X1D/X3/final digests bound to the same plan;
- final assembly reconciles each rendered claim and prohibits alternative-lane double counting;
- retrieval, calibration, order-invariance, mutation, and whole-run tests pass;
- graph-skills CI ratchet runs automatically on relevant PRs/pushes;
- no direct durable graph-state writes during selection;
- validated closeout and Codex run receipts exist.

## 15. Codex kickoff prompt

Use the following prompt in Codex after the user approves this plan:

> Review and execute `plans/apps-rg-c03-resume-graph-hardening-9f3c2a.md` against a clean branch based on `origin/main`. Start with W0 only. Do not edit production code until W0 evidence, the finite contract matrix, ADG impact map, baseline test results, and rebased plan are complete and explicitly approved. Treat all canonical graph skill and metric values as validated; harden retrieval, graph traversal, global allocation, zero reuse, confidence, claim binding, and release gates without altering those facts. Do not touch `agentic_core`. Use repo-native Codex readiness, ADG-first discovery, test-first changes, machine-readable receipts, and stop conditions exactly as specified.


## W1-W3 implementation record (2026-07-13)

- **Rebased branch:** `agent/apps-rg-c03-resume-graph-w1-w6` onto `origin/main` at `3ada93fc2c780fe548e723d68e7e5e5bdf8b21c7`.
- **W0 baseline disposition:** the apps-local circular import is closed by moving the C0.3 SQLite context import behind the public selection function. The pre-existing `agentic_core/L0_routing/__init__.py` app-authority literal remains outside this app-only plan and is neither hidden nor widened. GitHub-hosted readiness failures caused by unavailable local MCP transports remain environment evidence, not a product-code waiver.
- **W1:** added canonical pre-target authority, terminal candidate-decision, traversal-event, traversal-receipt, and canonical section-plan contracts with stable digests.
- **W2:** hard authority gates now precede target scoring; direct claim support is limited to a frozen selected graph plan or SQLite-ranked direct skill/fact paths. Broad fact-link loading and label/tag proof fallback are removed. Historical usage is ignored unless an explicit current `run_id` is supplied.
- **W3:** role-episode traversal is event-sourced; each bounded root, skill, metric, and source-fact path receives an authority evaluation and terminal decision. Skills and metrics are ranked across the full bounded sibling frontier before caps.
- **W1-W3 verification:** focused authority, SQLite, traversal, and fail-closed tests pass; see `docs/reports/apps_rg/c03_resume_graph_w1_w3_closeout.md`.

## W4-W9 execution record (updated 2026-07-14)

- **W4:** one immutable whole-resume allocator now traverses all eleven claim-bearing lanes before generation; emits a current-run-only allocation plan and usage ledger; allocates 30 canonical-visible claim units plus 17 non-counting derived narrative units; enforces zero skill-ID, metric-ID, and normalized-metric-signature reuse; and is invariant to section dispatch order.
- **W5:** a shared pre-X3 gate binds each final visible claim to the frozen allocation's exact skill, fact, graph-path, edge, citation, and metric value/unit. It appends a deterministic X2 gate, blocks X3 on any orphan or drift, and carries the allocation digest through FEC, compiled prompt, L2, canonical ledger, X2, X1D, and X3 without rewriting signed upstream artifacts.
- **Verification:** 38 focused W1-W5 tests, 12 section-X3 integration tests, compilation, graph hardening validation, and diff checks pass in the available runtime. The optional-package import boundary used import-only local stubs for unavailable `openai` and `chromadb`; official branch CI remains required.
- **Current-main refresh:** the three prior branch commits replayed conflict-free and patch-equivalent onto `3ada93fc2c780fe548e723d68e7e5e5bdf8b21c7`. On that refreshed base, all 50 focused W1-W5/X3 tests and all 6 evidence-authority boundary tests pass with real temporary-environment dependencies; graph validation, Python compilation, whitespace checks, and the no-`agentic_core` diff boundary also pass. The published implementation commit is `07cb833099126cec5e3b043ca94dee9c18b761f7`; refreshed branch CI remains required.
- **W6 engineering:** commit `c56c75bf9e28455e5c206588f6c53003c8684497` implements deterministic offline evaluation/calibration, a bounded authority-preserving C0.6 retry, exact C0.7 handoff binding, private source freezing, blind cohort packet construction, prelabel sealing, human-authority validation, adjudicated export, sanitized CI receipts, and fail-closed controlled-evidence containment.
- **W6 controlled freeze:** packet `c03-human-eval::3e810e9ec6958bfe901ea6f5` binds source-freeze receipt digest `87047d8b651adb7314b49a2f9d88d2c3e35b753fb881fe58d8570c2be7c2c2c5`, prelabel manifest SHA-256 `37b3155991e87d0592411f75b4ee864332dafcc7e5b3302d383316cb15b67e08`, and prelabel receipt digest `047ea87471be22e79598f99bc452151196aa76c0535c24e2bec7345b4f7435a1`. Proof and retrieval archives are separately sealed; W9 item count is zero.
- **W6 verification:** the final evaluator/runtime suite is 141 passed; the refreshed W1-W5 regression is 57 passed; the broader integration snapshot is 46 passed, 12 skipped, and one known W0 `agentic_core/L0_routing/__init__.py contains augmented_skills_graph` baseline failure. The graph validator, compilation, stress path, whitespace check, and no-`agentic_core` diff boundary pass. Independent packet, evaluator, and final adversarial reviews report no remaining P0/P1 findings.
- **W6 evidence state:** the sanitized receipt is truthfully `UNKNOWN` with null/unmeasured metrics, no active threshold, `promotion_eligible=false`, advisory exit 0, and fail-closed exit 1. No human-review authority receipt, human labels, or adjudications exist yet.
- **W6 proxy authorization:** on 2026-07-14 the user approved representative scores for engineering continuity, explicitly allowing later replacement by human scoring. The committed proxy summary is non-authoritative and cannot change official W6 status from `UNKNOWN`.
- **W7:** the whole-resume evidence contract and end-to-end artifact/digest reconciliation are implemented. Engineering can pass independently; release cannot pass without official W6 authority and authorized final generation.
- **W8:** the C0.3 automatic code/contract CI ratchet, mutation controls, exact W0 diagnostic handling, and receipt v3 are implemented. Local strict verification is 234 passed, 1 skipped, and 1 deselected, plus the exact known external diagnostic failure. SVP documentation gates are not part of automatic GitHub CI.
- **W9:** the fail-closed shadow/coach closeout harness is implemented and tested. It contains no manufactured variants or human judgments and cannot promote without authorized generation, qualified reviews, adjudication, official W6 PASS, and whole-resume release PASS.
- **Implementation commit:** `29bee56aa39302d75141909a69999ab6e7201d6a` on base `b94748ad26a7ca01f258805bb77f0d778aebec7d`; no `agentic_core` diff.
- **Disposition:** `W1_W9_ENGINEERING_COMPLETE__OFFICIAL_RELEASE_EVIDENCE_PENDING`. The Definition of Done remains unsatisfied because official human W6 evidence and authorized W9 product-quality evidence are external and absent. Promotion is not claimed. See `docs/reports/apps_rg/c03_resume_graph_w7_w9_engineering_closeout.json` and `docs/reports/apps_rg/c03_resume_graph_w6_proxy_baseline.json`.
