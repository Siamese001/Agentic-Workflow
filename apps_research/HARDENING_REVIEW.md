# Graph Skills and apps_research → apps_rg Hardening Review

**Review mode:** review and implementation plan only; no production code was changed.  
**Source of truth:** the uploaded `apps_rg.zip` and `apps_research.zip` archives.  
**Target scenario:** the shipped Anthropic partnerships fixtures in `apps_rg/config/targeting/jd_anthropic_partnerships_2026.json` and `apps_rg/config/targeting/brief_anthropic_partnerships_2026.json`.

## Review basis and limitations

The review traced graph selection, proof-pool construction, section prompt authority, X2/X3 enforcement, runtime artifacts, inventory policy fields, company-brief synthesis, CLI artifact writing, and briefing consumption. A direct selector probe was also run against the shipped Anthropic fixtures and the shipped graph inventory files. That probe exercised `build_selected_graph_evidence_plan_for_section()` for every graph-backed section and then independently checked the selected skill and metric IDs against the policy fields in the uploaded ledgers.

Two limitations matter:

1. Neither uploaded archive contains a conventional automated test suite (`tests/`, `test_*.py`, or `*_test.py`). Existing validators are runtime controls, not regression tests.
2. A complete product E2E run could not be established from the archives alone. `apps_rg/fact_inventory/candidate_fact_ledger.py` points to `artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json`, which is absent, and several paths import `agentic_core`, which is outside the uploaded archive. Findings based on direct source inspection and the selector probe are definitive for those surfaces. Any whole-run path conclusion is labeled as static path analysis.

The packaged source files are byte-for-byte copies of the uploaded files. This preserves the user's “do not implement changes” constraint while identifying the exact refactor surface. `REFACTOR_MANIFEST.json` records SHA-256 equality for every copied source file.

# 1. Executive verdict

## Verdict: materially incomplete

The implementation has useful building blocks—graph plans, depth reports, proof-pool digests, X2 gates, section input authority ledgers, judge packets, and a visible competencies sourcing summary—but they do not yet form one authoritative evidence chain. Several controls can report `PASS` or `judge_grade` while the selected graph nodes violate section or external-claim policy, while eligible alternatives are never accounted for, or while the receipt describes a different graph plan from the proof pool used for generation.

## Single biggest remaining risk

**There is no single, policy-clean, digest-bound graph evidence plan that survives unchanged from candidate traversal through generation, claim binding, X2/X1D/X3, and runtime output.** As a result, a good-looking graph receipt can attest evidence that was not actually used, or can bless selected nodes that were never eligible to become proof.

This is not a presentation issue. It is a proof-identity and proof-authority issue. Until it is fixed, deeper prompts, more judges, and larger graph counts can make the system look stronger without making it more trustworthy.

## Anthropic fixture result in one sentence

The current selector can call the Anthropic partnerships profile `judge_grade` for competencies and executive summary while selecting section-ineligible skills, externally blocked draft skills, and section-ineligible metrics, and while omitting decision receipts for most eligible roots in cross-role sections.

# 2. Findings first, ordered by severity

## F1. Competencies generation and graph audit bind to two independently selected plans

**Severity:** Critical  
**Control classification:** Correctness gate

**Impacted files/functions**

- `apps_rg/runtime/proof_pool_resolver.py` — `_resolve_competencies_graph_skills_proof_pool()`
- `apps_rg/fact_inventory/competencies_graph_skills_proof_pool.py` — `build_competencies_graph_skills_proof_payload()`
- `apps_rg/runtime/sections/graph_role_episode_selector.py` — `build_selected_graph_evidence_plan_for_section()`
- `apps_rg/runtime/sections/competencies_pa.py` — competencies prompt-authority assembly
- `apps_rg/runtime/sections/section_prompt_authority_ssot.py` — section authority compilation
- `apps_rg/runtime/section_graph_skills_proof_pool.py` — shared graph plan construction

**Current behavior**

`_resolve_competencies_graph_skills_proof_pool()` first calls `build_competencies_graph_skills_proof_payload()` and assigns its `selected_fact_plan` to `plan`. That plan supplies the facts, allowed IDs, bullet rows, proof-pool digest, and the `SectionProofPool.selected_fact_plan`. The same function then independently calls `build_selected_graph_evidence_plan_for_section(section_id="competencies")` and stores that second result as `selected_graph_plan`. Traversal, depth, selected graph rows, skew diagnostics, and visible graph sourcing metadata are derived from the second plan.

`competencies_pa.py` can also construct a selected graph plan if it does not find one in metadata. The architecture therefore permits three selection moments: the track-weighted competencies payload, the role-episode selector inside the proof-pool resolver, and a prompt-authority fallback selection.

**Why this is a real risk**

The proof-pool digest and allowed IDs can describe plan A while X2 traversal/depth receipts and operator output describe plan B. A downstream gate can be internally consistent with plan B and still say nothing about the evidence that generated the section under plan A. This breaks the basic invariant that every enforcement artifact must bind to the same immutable evidence decision.

**Concrete proof gap**

There is no canonical `plan_id`/`plan_digest` equality check across:

- candidate decision ledger;
- selected graph plan;
- selected fact plan;
- proof-pool digest;
- compiled prompt;
- claim ledger;
- X2 gate inputs;
- X1D judge packet;
- X3 disposition;
- runtime graph sourcing assessment.

**How it could fail on the Anthropic partnership resume**

The role-episode plan can display partnership roots, rejected siblings, metrics, and `judge_grade`, while the track-weighted competencies facts that authorize the actual competencies output differ in composition and policy status. An operator sees a convincing partnership graph assessment but cannot prove those were the facts available to the writer.

**Smallest hardening slice**

Create exactly one immutable `section_graph_evidence_plan` per section. The competencies-specific weighting logic may enrich or rank candidates, but it must produce the same canonical plan object consumed by the proof pool. Remove all independent re-selection from PA and validators. Every downstream artifact must carry and verify the same `plan_id`, `plan_digest`, graph digest, and ledger digest.

**Test to add**

`tests/runtime/test_competencies_single_plan_binding.py`

- Monkeypatch the second selector call to return a different plan.
- Assert resolution fails closed with `graph_plan_digest_mismatch`.
- Assert PA cannot reselect when the canonical plan is absent; it must block rather than synthesize a replacement.
- Assert selected fact IDs, allowed IDs, prompt plan, X2 input, and X3 receipt all carry the same digest.

**Artifact/receipt/runtime output to emit**

`graph_selection_binding_receipt.json` with canonical plan digest and equality checks for proof pool, prompt, claim ledger, X2, X1D, and X3.

---

## F2. The role-episode selector does not enforce skill or metric proof policy before targeting

**Severity:** Critical  
**Control classification:** Correctness gate

**Impacted files/functions**

- `apps_rg/runtime/sections/graph_role_episode_selector.py` — `_eligible_bundle()`, `_token_score()`, `_bundle_to_fact()`, `build_selected_graph_evidence_plan_for_section()`
- `apps_rg/fact_inventory/master_skills_arsenal_ledger.json`
- `apps_rg/fact_inventory/unify_role_episode_bundles.json`
- `apps_rg/fact_inventory/ibm_role_episode_bundles.json`
- `apps_rg/fact_inventory/insurtech_role_episode_bundles.json`
- `apps_rg/fact_inventory/ey_role_episode_bundles.json`
- `apps_rg/runtime/sections/graph_evidence_contract.py`

**Current behavior**

The selector filters role-episode bundles using bundle-level section eligibility, scores them using target-role/JD/brief token overlap, and then takes skill and metric IDs from the winning bundles. It does not consult the selected skill rows' `activation_status`, `allowed_sections`, `external_claim_policy`, `visibility_rule`, `confidence_grade`, or `fact_id_links`. It also does not enforce metric `approved`, `approval_status`, `section_eligibility`, or bundle binding before selection.

Within a selected root, skill IDs are truncated by source-list order (`raw_skill_ids[:skill_cap]`) rather than ranked by a policy-clean leaf/specificity score. `_bundle_to_fact()` sets the bundle ID as the fact ID and uses graph presence as verification, while actual linked identity fact IDs are carried separately. This makes a bundle's existence look like source-fact authority.

**Why this is a real risk**

Target relevance is being applied before proof eligibility. A node can win because it resembles the Anthropic JD even when the ledger says it is draft, internal-only, not permitted in the section, not externally claimable, or not linked to a fact. Once selected, its IDs enter the graph plan and allowed-ID surfaces, laundering targeting relevance into apparent proof authority.

**Concrete proof gap**

There is no pre-target authority receipt showing that every candidate passed all of these before scoring:

- active status;
- section eligibility;
- external-claim policy;
- visibility/review policy;
- source-fact linkage;
- graph path validity;
- explicit leaf or permitted parent status;
- metric approval and section eligibility;
- metric-to-root and metric-to-source binding;
- freshness policy where applicable.

**Anthropic fixture evidence**

A direct call to the shipped selector with the shipped Anthropic partnership fixtures produced the following policy conflicts. “Unreceipted roots” are bundle roots that passed `_eligible_bundle()` but were neither selected nor represented in the selector's rejection output.

| Section | Selected / eligible roots | Unreceipted roots | Unique selected skills | Section-ineligible skills | Draft/externally blocked skills | Selected metrics | Section-ineligible metrics | Current depth status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Headline | 4 / 35 | 31 | 12 | 11 | 1 | 6 | 0 | `insufficient_depth` |
| Executive summary | 10 / 35 | 25 | 34 | 12 | 3 | 19 | 18 | `judge_grade` |
| Competencies | 8 / 35 | 27 | 27 | 6 | 1 | 16 | 4 | `judge_grade` |
| Unify bullets | 8 / 8 | 0 | 30 | 2 | 0 | 18 | 0 | `judge_grade` |
| Unify narrative | 8 / 8 | 0 | 30 | 20 | 0 | 18 | 0 | `judge_grade` |
| IBM bullets | 10 / 10 | 0 | 31 | 23 | 1; one has no fact links | 21 | 0 | `judge_grade` |
| IBM narrative | 10 / 10 | 0 | 31 | 24 | 1; one has no fact links | 21 | 0 | `judge_grade` |
| InsurTech bullets | 12 / 12 | 0 | 24 | 0 | 12 | 12 | 0 | `judge_grade` |
| InsurTech narrative | 12 / 12 | 0 | 24 | 0 | 12 | 12 | 0 | `judge_grade` |
| EY bullets | 5 / 5 | 0 | 4 | 2 | 0 | 0 | 0 | `insufficient_depth` |
| EY narrative | 5 / 5 | 0 | 4 | 2 | 0 | 0 | 0 | `insufficient_depth` |

The table does not assume every current ledger policy is correct; it shows that the selector does not enforce the policies that the same archive declares authoritative.

**How it could fail on the Anthropic partnership resume**

The resume can surface `partner_motions`, co-selling, partner-led AI solutions, hyperscaler alliance, or AWS framing because they score well against the JD even where the selected row is not allowed for that section or is marked `DRAFT`, `BLOCKED`, or `pending_source_internal_only`. Executive summary can simultaneously report `judge_grade` despite 18 of 19 selected metrics being section-ineligible under the metric rows inspected by the probe.

**Smallest hardening slice**

Build a normalized authority index once from the skills ledger and metric nodes. Before any JD/brief score is calculated, mark every root/skill/metric `ELIGIBLE` or `REJECTED_PRETARGET` with explicit policy reasons. Only eligible candidates may enter ranking. Do not silently drop invalid children; record them. For roots whose required children are all invalid, reject the root with a derived reason.

**Test to add**

`tests/runtime/test_graph_selector_authority_filter.py`

- Seed a high-scoring Anthropic-relevant skill that is `DRAFT`, blocked, section-ineligible, or unlinked.
- Assert it is rejected before scoring and cannot appear in allowed IDs.
- Seed a metric that is unapproved, wrong-section, or not bound to the selected root.
- Assert it is rejected and cannot improve depth or confidence.
- Run the shipped Anthropic fixtures across every section and assert zero selected policy violations.

**Artifact/receipt/runtime output to emit**

`graph_evidence_authority_receipt.json` plus one row per candidate in `graph_candidate_decision_ledger.jsonl`.

---

## F3. The competencies traversal receipt is reconstructed from outputs, not emitted by traversal

**Severity:** Critical  
**Control classification:** Correctness gate

**Impacted files/functions**

- `apps_rg/runtime/validators/competencies_quality_x2.py` — `_build_traversal_sufficiency_receipt()`, `check_competencies_graph_traversal_sufficiency()`
- `apps_rg/runtime/sections/graph_role_episode_selector.py` — selection loop and cap exclusions
- `apps_rg/runtime/sections/competencies_lane_execution.py` — graph sourcing output

**Current behavior**

`_build_traversal_sufficiency_receipt()` builds “visited” counts from selected IDs plus `excluded_due_to_root_cap` and `excluded_due_to_metric_cap`. It hardcodes skill/root hop-depth assumptions, derives frontier sizes from those final collections, and labels cap exclusions as rejected siblings. The selector itself does not emit a queue, visit order, attempted edge, frontier transition, skip reason, or stop condition.

`check_competencies_graph_traversal_sufficiency()` validates the shape and counts of that reconstructed object. It therefore proves that selected and cap-excluded arrays are populated, not that a traversal explored the candidate graph sufficiently.

**Why this is a real risk**

A selector can inspect only the easiest or first-listed roots, return enough skills and metrics to satisfy thresholds, and obtain a traversal `PASS`. Unvisited eligible roots and siblings are invisible. A fabricated root→skill→metric depth can be inferred after the fact even when no edge was read or validated during selection.

**Concrete proof gap**

Missing runtime facts include:

- candidate roots discovered;
- candidate nodes enqueued and actually visited;
- edge IDs read and validated;
- frontier size before and after each hop;
- candidates skipped before visit and why;
- roots terminated early and why;
- all eligible candidates accounted for;
- negative evidence that caused rejection;
- score and policy deltas between selected and rejected siblings.

**How it could fail on the Anthropic partnership resume**

For competencies, 35 roots are bundle-eligible, 8 are selected, and 27 do not appear in a rejection receipt. The reconstructed receipt can still show nonzero rejected siblings because it counts children excluded by caps inside selected roots. That looks like broad exploration while most roots were never decision-accounted.

**Smallest hardening slice**

Emit traversal events while selecting, not afterward. Define a deterministic conservation invariant for every candidate class:

`eligible_candidates = selected + rejected + skipped_with_reason`

Require zero unexplained candidates. Emit explicit hop frontiers and edge IDs. X2 should validate the immutable selector receipt; it must not synthesize traversal facts.

**Test to add**

`tests/runtime/test_graph_traversal_receipt.py`

- Give the selector 20 eligible roots but force it to inspect only the first 5.
- Assert the gate fails for 15 unexplained candidates even if selected counts exceed all minima.
- Delete one visited edge from the receipt and assert path-depth validation fails.
- Reorder source JSON and assert the same canonical decisions and traversal accounting result.

**Artifact/receipt/runtime output to emit**

`graph_traversal_receipt.json` and `graph_candidate_decision_ledger.jsonl`.

---

## F4. apps_research computes semantic handoff fitness but does not make it authoritative

**Severity:** Critical  
**Control classification:** Correctness gate

**Impacted files/functions**

- `apps_research/types/apps_rg_targeting_brief_contract.py` — `validate_targeting_brief_text()`, `assess_targeting_brief_semantics()`, `seal_targeting_brief()`
- `apps_research/engines/company_brief_engine.py` — `_synthesize_apps_rg_targeting_brief()`, `_build_targeting_brief_sidecar()`, result assembly
- `apps_research/__main__.py` — `_write_research_artifacts()`
- `apps_rg/integrations/apps_research_bridge.py` — `_translate()`

**Current behavior**

`seal_targeting_brief()` runs the structural/text validator and can return `SEALED` without requiring `assess_targeting_brief_semantics().handoff_eligible`. The company brief engine computes a useful sidecar containing semantic score, required/present source families, handoff eligibility, and brief SHA, but the main assembly promotes the Markdown to `company_brief_text` based on the syntactic disposition and C0 result. The CLI writes `briefing.md` and `company_brief.json`; the sidecar is not the mandatory handoff object. The apps_rg bridge validates only the Markdown contract.

**Why this is a real risk**

A brief can be correctly shaped, nonempty, and sealed while lacking the partnership-specific research needed for targeting. Because the semantic sidecar is advisory, the producer and consumer can both succeed without agreeing on substantive adequacy.

**Concrete proof gap**

There is no authoritative handoff envelope binding:

- company and target role;
- JD digest;
- brief digest;
- semantic eligibility and score;
- required and present research families;
- source authority/freshness result;
- producer/run/schema versions;
- generated and expiry timestamps;
- stub/dry-run status;
- C0 gate result;
- artifact digests.

**How it could fail on the Anthropic partnership resume**

A generic company overview with the expected headings can be `SEALED` and consumed even when it lacks partner ecosystem structure, co-sell/commercial motion, adoption motion, technical integration signals, or evidence that these claims came from current authoritative sources. apps_rg then targets phrasing to a briefing that is syntactically present but substantively weak.

**Smallest hardening slice**

Define `SEALED_FOR_APPS_RG` as structural validity **and** semantic handoff eligibility **and** source/freshness eligibility. Write one canonical JSON envelope adjacent to the Markdown and make apps_rg verify it. Keep the Markdown human-readable; do not treat it as the contract by itself.

**Test to add**

`apps_research/tests/test_targeting_brief_semantic_gate.py` and `apps_rg/tests/integration/test_apps_research_handoff_envelope.py`

- A structurally valid but generic brief must be blocked.
- A partnership brief missing `partner_ecosystem` or `commercial_motion` must be blocked.
- Changing the Markdown after sealing must produce a digest mismatch in apps_rg.
- `handoff_eligible=false` must block consumption even if status text says `SEALED`.

**Artifact/receipt/runtime output to emit**

`apps_rg_targeting_brief_envelope.json`, `apps_rg_targeting_brief_semantic_receipt.json`, and consumer-side `briefing_consumption_receipt.json`.

---

## F5. Partnership semantic requirements and default retrieval family IDs are structurally misaligned

**Severity:** High  
**Control classification:** Correctness gate

**Impacted files/functions**

- `apps_research/engines/query_decomposer.py` — `_COVERAGE_FAMILY_CATALOG`, standard company-brief profiles, `decompose_coverage_families()`
- `apps_research/types/apps_rg_targeting_brief_contract.py` — `_research_families()`, partnership-mode requirements in `assess_targeting_brief_semantics()`
- `apps_research/engines/company_brief_engine.py` — retrieval and semantic sidecar construction
- `apps_research/prompt_assembly/apps_rg_targeting_brief.py`

**Current behavior**

The default adaptive decomposition uses family IDs such as `company_basics`, `role_context`, `leadership_and_org`, `recent_news_and_signals`, `competitive_landscape`, `financials_and_growth`, `tech_stack_and_tools`, and `culture_and_values`. JD context only ensures `role_context` and `tech_stack_and_tools` are present.

The semantic assessment expects a different exact taxonomy: base families such as `overview`, `strategic_priorities`, `leadership`, and `recent_moves`; partnership mode additionally expects `partner_ecosystem`, `commercial_motion`, `adoption_motion`, and `tech_stack_signals`.

**Why this is a real risk**

The producer can perform substantial generic research but never execute explicit partnership-family retrieval. Conversely, semantically useful results can be marked missing because equivalent family IDs are not normalized. A prompt cannot repair a retrieval plan that never asked the partnership questions.

**Concrete proof gap**

There is no canonical family taxonomy or alias map shared by decomposition, retrieval, synthesis, semantic assessment, and the handoff envelope. There is also no role-archetype receipt proving which research families were planned, attempted, covered, and omitted.

**How it could fail on the Anthropic partnership resume**

The brief can over-index on company basics, leadership, culture, and general technology while omitting how Anthropic works with hyperscalers, GSIs, ISVs, joint solutions, co-sell motions, customer adoption, technical integrations, and partner-sourced outcomes—the information most relevant to the target role.

**Smallest hardening slice**

Introduce one canonical coverage-family registry with aliases. For the `ai_partnerships_gtm` archetype, require explicit retrieval plans for partner ecosystem, commercial motion, adoption motion, and technical integration. Record attempted and covered families. Preserve current generic families as aliases; do not rewrite the retrieval stack.

**Test to add**

`apps_research/tests/test_partnership_retrieval_family_plan.py`

- The shipped Anthropic JD must resolve to `ai_partnerships_gtm`.
- The query plan must contain all four partnership-critical canonical families.
- Aliased legacy family IDs must normalize consistently.
- Omitting a critical family must prevent handoff eligibility.

**Artifact/receipt/runtime output to emit**

`research_family_coverage_receipt.json`, referenced by the targeting brief envelope.

---

## F6. The C0 research gate equates nonempty family output with sourced, authoritative support

**Severity:** High  
**Control classification:** Correctness gate

**Impacted files/functions**

- `apps_research/engines/company_brief_engine.py` — `_build_c0_bundle()`, `_evaluate_c0_pa_gate()`
- `apps_research/validators/research_source_validator.py`
- `apps_research/validators/research_gate_validator.py`
- `apps_research/integrations/evidence_lineage.py`
- `apps_research/integrations/governed_research_run.py`
- `apps_research/types/research_types.py`

**Current behavior**

In `_build_c0_bundle()`, a family is covered when its result is a nonempty string. URL count can be used as source count, and if no URLs are found, covered-family count can stand in for source count. “Authoritative anchor” becomes true when any source is present. Claim support is inferred from family coverage. The contradiction matrix is emitted with zero conflicts, and the freshness report is not substantively evaluated.

`research_source_validator.py` checks source-register field presence and aggregate confidence but does not prove authority tier, publication/fetch time, document identity, or claim-level binding. `research_gate_validator.py` focuses on source presence, required section presence, and nonempty bodies.

**Why this is a real risk**

A generated paragraph, low-authority page, stale page, duplicated page, or unsupported synthesis can satisfy the count-shaped gate. A source count does not prove source independence, authority, freshness, or that the source entails the claim used in the targeting brief.

**Concrete proof gap**

Missing controls include:

- source authority classification;
- canonical URL/document fingerprint deduplication;
- published and fetched timestamps;
- freshness policy by claim class;
- claim-to-source edges;
- independent-source count;
- contradiction detection based on actual claims;
- explicit unsupported-claim disposition.

**How it could fail on the Anthropic partnership resume**

A single stale or generic page could populate several research families, causing C0 and the targeting brief to look well supported. Partnership claims about commercial motion or ecosystem relationships could then enter targeting without a source that actually establishes them.

**Smallest hardening slice**

Replace the family-count fallback with a source/claim ledger. A family is “covered” only when at least one claim in the family is bound to an authority-qualified, fresh-enough source. Count canonical documents, not URLs or populated strings. Emit real contradiction and freshness statuses; unknown is not pass.

**Test to add**

`apps_research/tests/test_c0_source_authority_and_freshness.py`

- Nonempty family text with no source binding must fail.
- Five aliases of the same document count as one source.
- An expired source cannot satisfy a current partnership claim.
- A low-authority source cannot be the sole anchor for a critical family.
- Contradictory source claims must produce `REVIEW` or `BLOCK`, not zero conflicts.

**Artifact/receipt/runtime output to emit**

`apps_rg_targeting_brief_source_register.json` and `research_claim_source_binding.jsonl`.

---

## F7. Graph depth and granularity gates measure structural counts, not semantic proof quality

**Severity:** High  
**Control classification:** Correctness gate

**Impacted files/functions**

- `apps_rg/runtime/sections/graph_evidence_contract.py` — `build_allowed_fact_ids_for_plan_facts()`, `_graph_evidence_depth_row()`, `build_graph_evidence_depth_report()`, `require_graph_evidence_depth()`
- `apps_rg/runtime/validators/competencies_quality_x2.py` — graph granularity and concentration checks
- `apps_rg/runtime/graph/graph_skill_concentration_policy.py`
- `apps_rg/runtime/sections/competency_capability_evidence.py`
- `apps_rg/runtime/sections/headline_positioning_evidence.py`

**Current behavior**

`build_graph_evidence_depth_report()` calls an item rich when expected ID arrays are present, computes item-rich, skill-diversity, and detail-diversity ratios, and labels their minimum `semantic_coverage_pct`. It can default a missing source-fact list to the item ID itself. `judge_grade` requires non-thin items and a count/diversity threshold. It does not prove that a selected skill is a leaf, that graph edges exist, that a source fact is authoritative, that the fact entails the skill claim, or that the metric is an approved outcome bound to the same episode and source.

The competencies granularity gate requires only one unique skill and one source fact per category, uses a 0.75 dominant fact-share ceiling, and relies on lexical role-axis coverage. `build_allowed_fact_ids_for_plan_facts()` also puts root, skill, metric, and fact IDs into a broad allowed-ID set, obscuring which ID class supplies claim authority.

**Why this is a real risk**

Counts can rise through aliases, duplicate nodes, self-referential IDs, generic parent skills, or metrics unrelated to the actual claim. A report named “semantic coverage” can return 100% without semantic validation.

**Concrete proof gap**

No hard gate proves:

- explicit leafness or justified parent-node use;
- validated root→skill→source-fact→metric edges;
- independent base facts/documents;
- semantic duplicate normalization;
- claim entailment;
- source authority/freshness;
- outcome metric applicability;
- critical role-axis evidence quality.

**How it could fail on the Anthropic partnership resume**

Executive summary and competencies both returned `semantic_coverage_pct=1.0` and `judge_grade` in the direct probe despite the policy violations listed in F2. Generic partnership nodes and reused facts can satisfy count ratios while providing weak proof of the specific Anthropic partnership capabilities.

**Smallest hardening slice**

Rename the current metric to `structural_saturation` if retained. Add a separate semantic evidence gate that validates leafness, edge/path identity, authority, independent base facts, claim binding, and metric applicability. Raise the critical-category minimum to two distinct leaf skills and two independent base facts, with a dominant semantic fact ceiling of 50%.

**Test to add**

`tests/runtime/test_graph_semantic_granularity_gate.py`

- Duplicate aliases of one skill/fact must not satisfy diversity.
- A parent-only generic node must not satisfy a critical category.
- Fabricated or missing edges must fail depth.
- Unapproved or unrelated metrics must not make an item rich.
- Two IDs resolving to one base fact must count as one source fact.

**Artifact/receipt/runtime output to emit**

`graph_granularity_receipt.json` and a renamed `graph_structural_depth_receipt.json`.

---

## F8. Competency term support is broad ID membership plus whole-resume token overlap

**Severity:** High  
**Control classification:** Correctness gate

**Impacted files/functions**

- `apps_rg/runtime/validators/competencies_x2.py` — `check_canonical_competency_terms()`, `_term_primary_support_ok()`, `term_supports_resume_or_graph()`
- `apps_rg/runtime/validators/competencies_quality_x2.py` — `check_jd_only_skill_forbidden()`
- `apps_rg/runtime/section_proof/section_input_usage_ledger.py`

**Current behavior**

Canonical competency validation confirms expected shapes and allowed-ID membership. `_term_primary_support_ok()` does not bind the supplied primary fact ID to the term; it can pass when a substantive term token appears anywhere in the resume support blob. `term_supports_resume_or_graph()` can pass on an allowed skill or fact ID without proving that the ID entails the emitted phrase. `check_jd_only_skill_forbidden()` blocks an exact JD phrase only when both skill and fact IDs are absent, so any unrelated allowed ID can defeat the check.

**Why this is a real risk**

A section can attach a valid but irrelevant graph ID to a JD-shaped competency and pass. Whole-resume keyword presence is not claim-level support. This is especially risky for broad terms such as “partnership strategy,” “co-selling,” “partner ecosystem,” or “technical advisory,” which are easy to match lexically.

**Concrete proof gap**

There is no deterministic claim record binding the exact emitted term to:

- selected root and path;
- specific leaf skill;
- specific source fact span or normalized fact;
- metric where outcome language is used;
- entailment verdict and method;
- canonical plan digest.

**How it could fail on the Anthropic partnership resume**

A term such as “hyperscaler co-sell strategy” can be supported by an unrelated allowed graph ID plus a coincidental occurrence of “strategy” or “co-sell” elsewhere in source text. The gate proves the presence of some permitted evidence, not that the evidence proves the term.

**Smallest hardening slice**

Require a claim-binding row for every emitted competency term. Allowed-ID membership becomes necessary but not sufficient. Deterministic exact/alias mappings can pass directly; otherwise require a bounded entailment check over the specific fact text. Do not permit whole-resume token fallback for a claim-level gate.

**Test to add**

`tests/runtime/test_competency_claim_binding.py`

- Attach an unrelated allowed fact ID to a JD-only partnership phrase; assert failure.
- Use a fact that contains one overlapping token but does not entail the competency; assert failure.
- Use a canonical skill→fact binding with an approved alias; assert pass.

**Artifact/receipt/runtime output to emit**

`graph_claim_binding_receipt.jsonl`.

---

## F9. JD and briefing targeting influence proof selection and proof confidence without a pre-target authority boundary

**Severity:** High  
**Control classification:** Correctness gate

**Impacted files/functions**

- `apps_rg/runtime/sections/graph_role_episode_selector.py` — `_infer_target_role_profile()`, `_token_score()`, selection
- `apps_rg/runtime/validators/competencies_quality_x2.py` — `_specific_alignment_score()`, per-category confidence construction
- `apps_rg/runtime/dispatch/input_authority_prompt_block.py`
- `apps_rg/runtime/section_proof/section_input_usage_ledger.py`
- `apps_rg/LEAN_CORE.md` and `apps_rg/AGENTS.md` as governing contracts

**Current behavior**

The selector uses JD and briefing terms to infer the role profile and score roots before it has proven node-level eligibility. Selected roots are converted into graph facts and allowed IDs. Per-category confidence then includes JD/brief alignment as a positive component. Prompt and ledger contracts correctly state that JD/briefing are targeting-only, but no machine receipt demonstrates the required two-stage boundary.

**Why this is a real risk**

Targeting may choose among valid evidence, but it may not make evidence valid. The current ordering and confidence model blur those concepts. A candidate can gain both selection status and confidence from JD resemblance even if its source authority is weak.

**Concrete proof gap**

There is no separate record of:

1. proof eligibility computed without JD/brief content; and
2. targeting rank computed only among eligible candidates.

There is also no confidence partition that distinguishes proof confidence from targeting fitness.

**How it could fail on the Anthropic partnership resume**

Adding “co-sell,” “partner-led AI solutions,” or “hyperscaler” to the JD can cause matching graph nodes to become selected and more confident, even when their ledger policy would otherwise exclude them. The system can then appear highly aligned and highly proven for the same reason: the target text itself.

**Smallest hardening slice**

Split selection into `authority_filter` and `targeting_rank`. Freeze the authority-filter output and digest before passing JD/brief content to ranking. Split confidence into `proof_confidence` and `targeting_alignment`; only proof confidence may affect claim admissibility.

**Test to add**

`tests/runtime/test_jd_brief_targeting_only.py`

- Add a high-scoring JD-only phrase for an ineligible node; eligibility must not change.
- Modify the JD while keeping evidence unchanged; proof confidence must remain unchanged while targeting alignment may move.
- Remove the briefing; authority-clean candidates remain the same, though ranking may change.

**Artifact/receipt/runtime output to emit**

`graph_pretarget_authority_receipt.json` and targeting components in `graph_candidate_decision_ledger.jsonl`.

---

## F10. Selector, judge, deterministic gates, and X3 can disagree without a single arbitration receipt

**Severity:** High  
**Control classification:** Correctness gate

**Impacted files/functions**

- `apps_rg/runtime/sections/competencies_lane_execution.py`
- `apps_rg/runtime/validators/competencies_quality_x2.py`
- `apps_rg/runtime/exit/competencies_x3.py`
- `apps_rg/runtime/exit/executive_summary_x3.py`
- `apps_rg/runtime/sections/section_prompt_authority_ssot.py`
- section judge modules and common section runtime wiring

**Current behavior**

Competencies computes selector confidence, decomposed category confidence, X2 gates, and X1D judge outputs. Its X3 call can set `judge_required_for_allow=False`, following the generic executive-summary exit implementation. There is no central artifact that ties selector score, proof-authority status, graph traversal/granularity results, judge score/verdict, disagreement reason, and final precedence into one decision.

**Why this is a real risk**

A high selector score and positive judge can coexist with a deterministic graph-authority failure; or X2 can pass while a judge identifies generic evidence; or a judge can fail while X3 allows because the judge is advisory. Without an arbitration receipt, the operator cannot tell which authority won or whether disagreement was ignored.

**Concrete proof gap**

Missing fields include:

- canonical plan/proof digest;
- selector score and threshold;
- proof-authority gate result;
- traversal/granularity/claim-binding results;
- judge score, threshold, and evidence packet digest;
- disagreement category;
- precedence rule applied;
- final disposition and responsible gate.

**How it could fail on the Anthropic partnership resume**

A judge can praise a polished partnership competency set while deterministic evidence is policy-ineligible, or a deterministic count gate can pass while a judge detects generic phrasing. The current outputs do not prove that the final `ALLOW` reconciled those conflicts.

**Smallest hardening slice**

Add one arbitration function after all selector, deterministic, and judge results are available. Deterministic authority/path/claim-binding failures always block. Quality judge disagreement may trigger one bounded repair or `REVIEW`, but cannot override proof authority. X3 consumes only the arbitration disposition.

**Test to add**

`tests/runtime/test_graph_selector_judge_arbitration.py`

- Judge pass + authority fail = block.
- Selector pass + judge fail = review/repair according to explicit policy.
- X2 pass + digest mismatch = block.
- All pass = allow with zero unresolved disagreements.

**Artifact/receipt/runtime output to emit**

`graph_selector_judge_arbitration_receipt.json`.

---
## F11. Competencies is the only section with a human-readable graph sourcing assessment, and other lanes lack equivalent proof depth

**Severity:** High  
**Control classification:** Correctness gate for machine receipts; telemetry for the human summary

**Impacted files/functions**

- `apps_rg/runtime/sections/competencies_lane_execution.py` — `_format_competencies_graph_sourcing_assessment()`
- `apps_rg/runtime/proof_pool_resolver.py` — executive summary and generic section resolvers
- `apps_rg/runtime/section_graph_skills_proof_pool.py`
- `apps_rg/runtime/sections/headline_positioning_evidence.py`
- `apps_rg/runtime/sections/competency_capability_evidence.py`
- `apps_rg/runtime/orchestration/section_lane_executor.py`
- `apps_rg/runtime/spine/section_cli_runners.py`

**Current behavior**

Competencies prints a `GRAPH_SOURCING_ASSESSMENT` in the requested order: role, roots, skills, metrics, rejected siblings, confidence, verdict. Other graph-backed sections carry some combination of selected graph plans, depth reports, headline positioning packets, or role-episode bundle lineage, but they do not expose an equivalent complete runtime assessment. They also do not share a complete candidate ledger, real traversal receipt, semantic granularity gate, rejected-candidate accounting, or arbitration receipt.

Executive summary has the strongest non-competencies depth enforcement, but it still uses the count-shaped graph depth contract described in F7. Headline and role lanes receive graph packets and lineage but lack a common hard gate and operator-facing summary. The direct Anthropic probe showed policy violations across these lanes even where `graph_evidence_depth_status` was `judge_grade`.

**Why this is a real risk**

A whole resume can appear graph-grounded because competencies is auditable while headline, summary, and experience sections silently drift to generic, invalid, or inconsistent graph evidence. The strongest section becomes a false proxy for the rest of the document.

**Concrete proof gap**

There is no common per-section contract requiring:

- canonical plan identity;
- candidate conservation;
- source-authority eligibility;
- semantic granularity and concentration;
- claim binding;
- rejected sibling explanation;
- selector/judge arbitration;
- visible assessment;
- whole-resume parity check.

**How it could fail on the Anthropic partnership resume**

Competencies can show partnership roots and a detailed receipt while headline remains depth-insufficient, executive summary uses mostly section-ineligible metrics, and narrative sections select skills not permitted for those sections. A human reviewing only the competencies output would miss the drift.

**Smallest hardening slice**

Create one shared `section_graph_sourcing_assessment` schema and producer. Use section-specific thresholds, but require the same identity, authority, traversal, granularity, rejection, confidence, and arbitration fields for every graph-backed section. Add a whole-run summary that blocks when a required section lacks its receipt or uses a different graph/ledger digest.

**Test to add**

`tests/runtime/test_section_graph_receipt_parity.py`

- Enumerate all graph-backed sections.
- Assert each emits the common receipt schema and canonical plan binding.
- Delete a receipt from one lane and assert whole-run graph parity fails.
- Introduce a graph digest drift in one lane and assert the whole-run summary blocks.

**Artifact/receipt/runtime output to emit**

Per section: `section_graph_sourcing_assessment.json`.  
Whole run: `resume_graph_sourcing_summary.json`.

---

## F12. The product upload-only briefing contract coexists with a legacy automatic-delegation branch

**Severity:** High  
**Control classification:** Correctness gate

**Impacted files/functions**

- `apps_rg/runtime/bindings/briefing_u0_signals.py`
- `apps_rg/runtime/bindings/l1_binding.py`
- `apps_rg/runtime/orchestration/r3r4_whole_run_orchestration.py`
- `apps_rg/integrations/managed_research_delegation.py`
- `apps_rg/integrations/apps_research_bridge.py`
- `apps_rg/LEAN_CORE.md`

**Current behavior**

The governing contract in `LEAN_CORE.md` and the U0 briefing policy state that apps_rg does not delegate to apps_research from the critical product path and that a run-specific briefing is required. `briefing_u0_signals.py` reports delegation disabled, and L1 validates the briefing before later orchestration.

`r3r4_whole_run_orchestration.py` nevertheless has an `auto_research_internal=True` default and a later delegation branch. Static path analysis indicates that the product path reaches L1 before that branch: a missing briefing blocks before delegation, while a present briefing suppresses the need to delegate. This makes the branch dead or nonconforming for the declared product contract, while still looking like a supported recovery path in code.

**Why this is a real risk**

Two incompatible policies are encoded: upload-only and automatic retrieval. Future refactoring can accidentally activate the legacy branch, bypass L1, or produce route-dependent semantics. Operators may also believe a missing brief will be fetched when the product contract says it must fail closed.

**Concrete proof gap**

No route-policy receipt proves:

- whether the run is product-visible or certified non-product;
- whether delegation is permitted for that route;
- the exact policy version;
- where the briefing was obtained;
- that L1 consumed the same artifact later used by lanes.

**How it could fail on the Anthropic partnership resume**

One invocation path can reject a missing Anthropic brief, while a future or alternate path might silently invoke research and continue with a differently validated artifact. That would make handoff behavior depend on orchestration entrypoint rather than one product contract.

**Smallest hardening slice**

Keep upload-only as the product SSOT. Quarantine or remove the legacy auto-delegation branch from product-visible execution. If retained for a non-product harness, require an explicit certified route and emit a route-policy receipt. Do **not** move automatic delegation before L1.

**Test to add**

`tests/runtime/test_briefing_route_policy.py`

- Product route + missing brief = deterministic block; bridge is never invoked.
- Product route + valid envelope = proceed; bridge is never invoked.
- Non-product delegation route requires explicit certification and produces a distinct receipt.
- Default parameters cannot activate delegation in product mode.

**Artifact/receipt/runtime output to emit**

`briefing_route_policy_receipt.json`.

**Static-analysis note:** Full whole-run execution was not available from the uploaded archives, so branch reachability should be confirmed with an integration test before deleting code. The contract conflict itself is directly present in the uploaded source.

---

## F13. The briefing writer and consumer do not preserve semantic provenance, freshness, or a digest chain

**Severity:** High  
**Control classification:** Correctness gate

**Impacted files/functions**

- `apps_research/__main__.py` — `_write_research_artifacts()`
- `apps_research/outputs/envelope_emitter.py`
- `apps_research/engines/company_brief_engine.py` — sidecar construction
- `apps_rg/runtime/briefing_resolution.py` — `resolve_briefing_for_lanes()`
- `apps_rg/runtime/pre_dispatch_preflight.py` — `evaluate_manual_brief_cli_input()`
- `apps_rg/prerequisites/briefing_validator.py` — `HistoricalBriefingValidator.validate()`
- `apps_rg/enforcement/cli_prerequisite_gate.py`
- `apps_rg/runtime/targeting_input_freshness.py`
- `apps_rg/runtime/orchestration/canonical_dispatch.py`
- `apps_rg/integrations/apps_research_bridge.py`
- `apps_rg/integrations/managed_research_delegation.py`

**Current behavior**

The research CLI writes `company_brief.json` and raw `briefing.md`, rejecting empty or obvious stub-looking targeting text. The JSON records `generated_at_utc`, while the apps_rg historical validator looks for `generated_at` or `created_at`. `briefing_resolution.py` accepts `.txt`, `.md`, `.json`, `.yaml`, URL, and inline content as text; JSON/YAML are not treated as a typed handoff envelope. Pre-dispatch checks are mostly existence/nonempty/default-placeholder checks.

The bridge's `result_hash`/`company_brief_hash` is built from run metadata rather than a canonical brief-envelope digest. Its request does not bind the actual JD text/digest. `managed_research_delegation.py` carries a freshness TTL parameter but does not establish a consumer-side expiry decision over a canonical producer timestamp.

**Why this is a real risk**

A stale, modified, wrong-company, wrong-role, wrong-JD, sidecar-ineligible, or provenance-poor brief can be consumed as plain text. The producer may calculate the right metadata, but the consumer is not required to receive or verify it.

**Concrete proof gap**

Missing end-to-end bindings:

- producer schema/version/run ID;
- normalized company and target role;
- JD SHA-256;
- brief SHA-256;
- semantic receipt SHA-256;
- source-register SHA-256;
- generation and expiry times;
- stub/dry-run flags;
- consumer validation time and policy;
- exact resolved text digest passed to every lane.

**How it could fail on the Anthropic partnership resume**

An old Anthropic brief can be renamed and supplied for a new JD, a user can edit `briefing.md` after generation, or a JSON sidecar with `handoff_eligible=false` can be ignored while the Markdown proceeds. The lane receives text but cannot prove which research run, JD, sources, or semantic gate produced it.

**Smallest hardening slice**

Write the Markdown and a canonical envelope atomically. Resolve JSON/YAML as structured envelopes, not raw text. Verify company, role, JD digest, brief digest, semantic eligibility, source/freshness verdict, and expiry before L1. Record the resolved envelope and text digests in the section input usage ledger and every section plan.

**Test to add**

`apps_research/tests/test_handoff_artifact_digest_binding.py` and `apps_rg/tests/integration/test_briefing_freshness_and_digest.py`

- Mutate Markdown after envelope creation; block.
- Supply a valid envelope for a different JD/company/role; block.
- Use `generated_at_utc`; verify freshness is actually computed.
- Supply an expired envelope; block.
- Supply raw JSON text without the envelope schema; block in product mode.
- Confirm every lane receives the same brief digest.

**Artifact/receipt/runtime output to emit**

Producer: `apps_rg_handoff_receipt.json`.  
Consumer: `briefing_consumption_receipt.json`.

---

## F14. Graph inventory policy, leafness, duplicates, and freshness are not normalized at selection time

**Severity:** Medium-High  
**Control classification:** Correctness gate for policy/leafness; warning and audit for duplicate cleanup

**Impacted files/functions**

- `apps_rg/fact_inventory/master_skills_arsenal_ledger.json`
- the four `*_role_episode_bundles.json` files
- `apps_rg/runtime/sections/graph_role_episode_selector.py`
- `apps_rg/runtime/sections/graph_evidence_contract.py`
- `apps_rg/fact_inventory/candidate_fact_ledger.py`

**Current behavior**

The uploaded master skills ledger contains 235 skill rows: 101 `ACTIVE_CONFIRMED`, 94 `ACTIVE`, and 40 `DRAFT`. Thirty-four rows use `pending_source_internal_only`, nine have no fact links, and 33 require `human_confirm`. The role-episode bundles reference 141 unique skill IDs. Among referenced skills, 28 are `DRAFT`/pending-source; two referenced rows have no fact links (`skill_partner_product_feedback_loops` and `skill_capital_reserving`).

The current graph shape gives no referenced skill an outgoing skill-like child, so leafness can be inferred from the present edge set, but it is not declared, versioned, or enforced. A heuristic inventory scan also found duplicate/coarse capability labels such as `pricing_actuarial`, `regulatory_capital`, `partner_motions`, `co_selling`, and `pre_sales`. This duplicate/coarseness result is a reviewer heuristic, not a canonical semantic judgment.

Freshness is not proven by the selection receipts. This review does **not** claim that the graph is actually stale; it claims the runtime cannot prove that it is current enough for the policy being enforced.

**Why this is a real risk**

The selector can treat draft/internal rows as normal candidates, count aliases as diversity, and rely on generic parent-like labels as if they were specific leaves. Inventory cleanup performed later cannot repair claims already admitted at runtime.

**Concrete proof gap**

There is no versioned normalization index containing:

- canonical capability ID and aliases;
- explicit `leaf`, `parent`, or `hybrid` classification;
- allowed parent-only exceptions;
- semantic duplicate group;
- active/external/section policy normalization;
- source-fact base IDs;
- graph/ledger effective date and freshness policy.

**How it could fail on the Anthropic partnership resume**

Several superficially distinct partnership skills can resolve to the same broad capability or source fact, satisfying unique-skill counts while adding little proof diversity. A draft partnership node can outrank a narrower confirmed skill because it matches the JD more directly.

**Smallest hardening slice**

Build a read-time normalized index; do not mass-edit the graph first. Apply authority and leafness gates during selection, collapse aliases for concentration calculations, and emit duplicate/coarse warnings. Defer renaming or merging IDs until runtime behavior is safe and regression-covered.

**Test to add**

`tests/runtime/test_graph_inventory_normalization.py`

- Alias IDs count once for diversity and concentration.
- Draft/internal/unlinked rows cannot be proof candidates.
- A parent-only node cannot be the sole support for a critical axis.
- A declared leaf with an active child causes an inventory integrity failure.

**Artifact/receipt/runtime output to emit**

`graph_inventory_normalization_receipt.json`.

---

## F15. No supplied regression tests would catch silent generic/easy-node collapse

**Severity:** Medium  
**Control classification:** Test infrastructure requirement

**Impacted files/functions**

- Both uploaded repositories: no conventional test files were supplied
- All selector, gate, handoff, and section integration surfaces listed in this report

**Current behavior**

Runtime validators exist, but the archives contain no automated tests that mutate graph order, remove edges, inject invalid nodes, alter source concentration, change a briefing digest, or compare section behavior. Therefore the literal answer to “what tests would fail today?” is: **none in the supplied code, because no such tests are present.**

**Why this is a real risk**

The selector can regress toward list-order bias or generic nodes without CI evidence. A future change can weaken a gate, activate the legacy handoff branch, or stop emitting a receipt and still merge if external CI does not supply unpublished tests.

**Concrete proof gap**

No source-controlled evidence establishes:

- deterministic selection under input order changes;
- authority filtering;
- traversal conservation;
- semantic concentration;
- role-axis coverage;
- cross-section parity;
- handoff integrity;
- end-to-end Anthropic acceptance.

**How it could fail on the Anthropic partnership resume**

A change that truncates roots earlier, prioritizes generic partnership nodes, drops metrics, or accepts a stale brief would not trigger any test in these archives.

**Smallest hardening slice**

Add focused unit tests before changing graph content or prompts. Add one end-to-end Anthropic fixture test after the canonical plan and envelope contracts exist. Keep tests deterministic and fixture-driven; do not require live web retrieval or model calls for correctness gates.

**Test to add**

The complete test plan is in section 6.

**Artifact/receipt/runtime output to emit**

CI should publish the exact fixture digests and the machine receipts from the Anthropic E2E test.

---

## F16. The uploaded apps_rg archive is not self-contained for full proof-pool execution

**Severity:** Medium  
**Control classification:** Correctness gate at preflight; audit-only for developer diagnostics

**Impacted files/functions**

- `apps_rg/fact_inventory/candidate_fact_ledger.py`
- `apps_rg/runtime/proof_pool_resolver.py`
- paths that import `agentic_core`
- apps_rg preflight and artifact-manifest surfaces

**Current behavior**

`candidate_fact_ledger.py` references an artifact path outside the uploaded package, and that artifact is absent. Several runtime paths require `agentic_core`, also absent. The archive therefore cannot independently prove that all graph/fact authorities needed by a product run are present and digest-matched.

**Why this is a real risk**

A deployment or review can inspect the package but unknowingly depend on mutable or missing external files. Fallback behavior, environment-specific imports, or stale external artifacts can change evidence outcomes without a source-tree diff.

**Concrete proof gap**

There is no package-level dependency manifest with required artifact paths, schema versions, expected digests, and fail-closed availability checks for graph/fact authorities.

**How it could fail on the Anthropic partnership resume**

The Anthropic run can behave differently across environments depending on which candidate ledger or `agentic_core` version is available. A graph receipt may identify one digest while the external proof substrate is missing or different.

**Smallest hardening slice**

Add a required evidence dependency manifest and preflight. Do not copy external authorities into a new store. Fail before section selection if a required artifact is absent, schema-incompatible, or digest-mismatched.

**Test to add**

`tests/runtime/test_graph_authority_dependency_preflight.py`

- Missing candidate ledger = block.
- Wrong digest/schema = block.
- Optional developer-only dependency = explicit non-product disposition, never silent fallback.

**Artifact/receipt/runtime output to emit**

`graph_authority_dependency_receipt.json`.

# 3. Cross-section comparison

The matrix below compares the currently uploaded implementation, not the target state.

| Section / lane | Traversal receipt | Visible runtime graph sourcing | Granularity gate | Rejected candidates | JD/brief targeting-only discipline | Selector/judge arbitration |
|---|---|---|---|---|---|---|
| Competencies | **Partial, synthetic.** Reconstructed from selected and cap-excluded IDs; no actual visit/frontier ledger. | **Yes.** `GRAPH_SOURCING_ASSESSMENT` in `competencies_lane_execution.py`. | **Present but count-shaped.** One skill/source per category, 0.75 concentration ceiling, lexical axes. | **Partial.** Cap exclusions and model-facing neighbor audit; most unselected eligible roots are not accounted for. | **Declared, not proven.** Prompt/input ledgers say targeting-only, but pre-target authority is absent and alignment raises confidence. | **No common receipt.** Scores and gates exist but precedence/disagreement is not bound. |
| Executive summary | Selected graph plan and hard depth requirement, but no true traversal event ledger. | No equivalent role→roots→skills→metrics→rejections summary. | Count/diversity depth gate; no leaf/authority/entailment gate. | Cap exclusions only; 25 of 35 eligible Anthropic roots were unreceipted in the probe. | Input authority protections exist, but selector target relevance is not separated from proof eligibility. | Judge infrastructure is rich, but no graph-specific arbitration receipt ties it to authority/traversal. |
| Headline | Selected plan plus headline positioning packet; no complete candidate traversal ledger. | No equivalent summary. | Packet/depth checks only; direct probe was `insufficient_depth`. | No all-candidate accounting; 31 of 35 eligible Anthropic roots were unreceipted. | Declared in prompt policy; no two-stage authority receipt. | None. |
| Unify bullets | Role-episode plan/bundle lineage; no true traversal receipt. | No equivalent summary. | Shared structural depth telemetry; no shared semantic hard gate. | All employer roots happened to fit current caps, but sibling/negative-evidence quality is still absent. | Declared, not machine-proven. | None. |
| Unify narrative | Same as Unify bullets. | No equivalent summary. | Same gap; 20 selected skills were section-ineligible in the probe. | No scored rejected-sibling comparison. | Declared, not machine-proven. | None. |
| IBM bullets | Role-episode plan/bundle lineage; no true traversal receipt. | No equivalent summary. | Structural depth can be `judge_grade`; no policy/leaf/source binding gate. | No complete negative-evidence ledger. | Declared, not machine-proven. | None. |
| IBM narrative | Same as IBM bullets. | No equivalent summary. | Same gap; 24 selected skills were section-ineligible in the probe. | No complete negative-evidence ledger. | Declared, not machine-proven. | None. |
| InsurTech bullets | Role-episode plan/bundle lineage; no true traversal receipt. | No equivalent summary. | Structural depth `judge_grade`; 12 selected skills were externally blocked/draft in the probe. | No policy-based rejection proof. | Declared, not machine-proven. | None. |
| InsurTech narrative | Same as InsurTech bullets. | No equivalent summary. | Same gap. | No policy-based rejection proof. | Declared, not machine-proven. | None. |
| EY bullets | Role-episode plan/bundle lineage; no true traversal receipt. | No equivalent summary. | Direct probe had zero metrics and `insufficient_depth`. | No negative-evidence ledger. | Declared, not machine-proven. | None. |
| EY narrative | Same as EY bullets. | No equivalent summary. | Same gap. | No negative-evidence ledger. | Declared, not machine-proven. | None. |

## Cross-section conclusion

Competencies has the best operator surface, executive summary has the strongest existing depth enforcement, and role lanes have useful graph lineage. None has the complete best-class chain. The correct next step is a shared evidence-plan/receipt contract, not copying competencies' current synthetic traversal logic into every lane.

# 4. Graph quality rubric

## Hard gates that apply before scoring

A section is not acceptable, regardless of numeric quality score, when any of these is true:

1. Any selected root, skill, fact, or metric fails source-authority, activation, section, visibility, external-claim, or binding policy.
2. The plan/proof/prompt/claim/X2/X1D/X3 digests do not match.
3. Any eligible candidate is missing from selected/rejected/skipped accounting.
4. A selected path contains a missing or invalid edge.
5. A critical emitted claim lacks claim-level source binding.
6. JD or briefing content is used as proof authority.
7. A required critical role axis has no authority-clean evidence.
8. A required apps_research envelope is missing, stale, mismatched, stub/dry-run, or semantically ineligible.
9. A deterministic authority failure is overridden by a selector or judge.
10. A required section does not emit the common graph receipt.

## Scored dimensions

Score each dimension `0`, `1`, or `2`. Best-class requires all hard gates to pass, at least **18/20**, and no dimension scored `0`.

| Dimension | 0 — inadequate | 1 — serviceable | 2 — best-class criterion |
|---|---|---|---|
| Traversal breadth | Selected-only or cap-only accounting. | Most roots accounted for, but some skips or edges lack reasons. | 100% eligible root/skill/metric conservation; every skipped/rejected candidate has a deterministic reason and score/policy delta. |
| Traversal depth | Depth inferred from ID shape/count. | Valid root→skill→fact paths for most selected claims. | Every selected claim has validated root→leaf skill→source fact and, when outcome-bearing, metric path; edge IDs and graph digest are recorded. |
| Leaf skill specificity | Generic/coarse nodes can be sole support. | Mixed leaf and parent nodes with manual exceptions. | Critical category has at least two semantically distinct authority-clean leaf skills; parent-only use is explicitly justified and cannot be sole support. |
| Source fact diversity | One fact or aliases dominate. | Two fact IDs but document/base-fact independence is incomplete. | Critical category has at least two independent base facts from at least two canonical documents; dominant semantic fact ≤50% per category and section-level concentration is reported. |
| Metric outcome binding | Metric IDs are present but unverified. | Approved metrics are root-bound but claim/source binding is partial. | Outcome language uses approved, section-eligible metrics bound to the selected root, source fact, and exact claim; no metric is used merely to improve depth. |
| Role/JD axis coverage | Lexical match or generic role label only. | Required axes are configured and mostly covered. | Role profile declares critical axes; each is covered by authority-clean leaf paths and independent facts. For Anthropic partnerships: ecosystem/alliance, co-sell/commercial, joint solution/technical integration, adoption/customer success, and measurable outcomes. |
| Rejected sibling quality | Rejections absent or only cap overflow. | Rejection reasons exist for selected-root siblings. | All candidates accounted; at least the top three rejected alternatives per selected root show policy status, score components, score delta, negative evidence, and stop reason. |
| Source authority | Graph presence or ID membership is treated as proof. | Policy filtering exists but some fields/freshness are advisory. | Authority filter runs before targeting and enforces activation, external policy, section, visibility, fact links, source class, and freshness; receipt is immutable. |
| Selector/judge agreement | Disagreement invisible or ignored. | Disagreement logged but precedence is implicit. | One arbitration receipt binds selector, deterministic gates, judges, digests, disagreement class, precedence rule, repair attempt, and final disposition. |
| Human-auditable runtime output | Code reading required. | Per-section summary exists but does not link all receipts. | Every section prints a concise assessment and links machine receipts; whole-run summary highlights failures, unaccounted candidates, concentration, critical axes, and handoff status without code inspection. |

## Current-state rubric interpretation

The current implementation fails multiple hard gates, so a numeric score should not be used to soften the verdict. Its strongest dimensions are partial structural depth telemetry and competencies operator visibility. Its weakest are pre-target authority, actual traversal accounting, plan identity, claim binding, and arbitration.

# 5. Prioritized roadmap

## Slice 1 — Canonical plan identity and pre-target proof eligibility

**Value / blast radius:** Highest value, lowest safe blast radius. It prevents invalid evidence and false receipt binding without changing prose generation strategy.

**Files likely touched**

- `apps_rg/runtime/proof_pool_resolver.py`
- `apps_rg/fact_inventory/competencies_graph_skills_proof_pool.py`
- `apps_rg/runtime/section_graph_skills_proof_pool.py`
- `apps_rg/runtime/sections/graph_role_episode_selector.py`
- `apps_rg/runtime/sections/graph_evidence_contract.py`
- `apps_rg/runtime/sections/competencies_pa.py`
- `apps_rg/runtime/sections/section_prompt_authority_ssot.py`
- `apps_rg/fact_inventory/candidate_fact_ledger.py`
- the master skills ledger and four role-episode bundle files only where policy metadata is demonstrably inconsistent, not for broad cleanup

**Expected tests**

- `test_competencies_single_plan_binding.py`
- `test_graph_selector_authority_filter.py`
- `test_graph_authority_dependency_preflight.py`
- Anthropic selector fixture test across all sections

**Acceptance criteria**

- One canonical plan is created once per section.
- `plan_id` and `plan_digest` are identical in proof pool, PA, prompt artifact, X2, X1D, X3, and runtime summary.
- No PA or validator path can reselect.
- Every selected skill and metric passes all declared policy fields.
- Anthropic fixture selects zero section-ineligible, blocked, draft, unlinked, unapproved, or wrong-bound nodes.
- Missing graph/fact authority blocks before selection.

**Rollback risk**

Low to medium. More runs may block because invalid nodes are no longer tolerated. The code change is localized to selection/proof construction. Rollback must not re-enable invalid evidence; rollback should mean restoring the prior release, not converting failures to warnings.

**What not to change**

- Do not rewrite prompts or resume prose.
- Do not add a new graph store.
- Do not change X3 quality thresholds yet.
- Do not mass-rename skills.
- Do not allow JD/briefing to participate in authority filtering.

## Slice 2 — Real traversal, semantic binding, concentration, confidence, and arbitration

**Files likely touched**

- `apps_rg/runtime/sections/graph_role_episode_selector.py`
- `apps_rg/runtime/sections/graph_evidence_contract.py`
- `apps_rg/runtime/validators/competencies_quality_x2.py`
- `apps_rg/runtime/validators/competencies_x2.py`
- `apps_rg/runtime/graph/graph_skill_concentration_policy.py`
- `apps_rg/runtime/section_proof/section_input_usage_ledger.py`
- `apps_rg/runtime/sections/competencies_lane_execution.py`
- `apps_rg/runtime/exit/competencies_x3.py`
- `apps_rg/runtime/exit/executive_summary_x3.py`
- one new shared graph receipt/arbitration module

**Expected tests**

- `test_graph_traversal_receipt.py`
- `test_graph_easy_node_collapse.py`
- `test_graph_semantic_granularity_gate.py`
- `test_competency_claim_binding.py`
- `test_competencies_confidence_decomposition.py`
- `test_source_fact_concentration_semantic.py`
- `test_graph_role_axis_coverage.py`
- `test_jd_brief_targeting_only.py`
- `test_graph_selector_judge_arbitration.py`

**Acceptance criteria**

- Candidate conservation equals 100% for roots, skills, and metrics.
- Frontier sizes and visited edge IDs are selector-emitted, not validator-inferred.
- Critical categories have at least two leaf skills and two independent base facts.
- Dominant base fact share is ≤50% in each critical category.
- Outcome claims have approved metric bindings.
- Proof confidence excludes JD/brief alignment; targeting alignment remains separately visible.
- No unresolved selector/judge/deterministic disagreement reaches `ALLOW`.
- The current synthetic receipt fails the new gate.

**Rollback risk**

Medium. New correctness gates can expose latent inventory gaps. Release behind a shadow comparison only for measurement, then switch atomically to fail-closed; do not leave a permanent warning-only mode.

**What not to change**

- Do not add synthetic confidence jitter to avoid repeated values.
- Do not let an LLM judge create missing traversal facts.
- Do not accept selected-only evidence as traversal proof.
- Do not lower thresholds to preserve current pass rates.

## Slice 3 — Make apps_research produce an authoritative partnership-ready handoff

**Files likely touched**

- `apps_research/types/apps_rg_targeting_brief_contract.py`
- `apps_research/engines/company_brief_engine.py`
- `apps_research/engines/query_decomposer.py`
- `apps_research/__main__.py`
- `apps_research/validators/research_source_validator.py`
- `apps_research/validators/research_gate_validator.py`
- `apps_research/integrations/evidence_lineage.py`
- `apps_research/integrations/governed_research_run.py`
- `apps_research/types/research_types.py`
- `apps_research/outputs/envelope_emitter.py`
- `apps_research/prompt_assembly/apps_rg_targeting_brief.py` only to align output with the structural contract, not as the primary fix

**Expected tests**

- `test_targeting_brief_semantic_gate.py`
- `test_partnership_retrieval_family_plan.py`
- `test_c0_source_authority_and_freshness.py`
- `test_handoff_artifact_digest_binding.py`
- `test_targeting_cli_no_stub_dryrun.py`

**Acceptance criteria**

- `SEALED_FOR_APPS_RG` requires syntax, semantic eligibility, role-family coverage, C0 source authority, and freshness.
- Anthropic partnership mode plans and covers the four critical research families.
- Family aliases normalize to one taxonomy.
- Source counts are canonical-document counts; claims bind to source IDs.
- Markdown and envelope are written atomically and digest-bound.
- Stub, dry-run, stale, contradictory, or semantically weak output cannot be handoff-eligible.

**Rollback risk**

Medium. Fewer briefs may qualify initially. The safe rollback is to block and request a new brief, not to consume Markdown without the envelope.

**What not to change**

- Do not move proof authority to the company brief.
- Do not make live retrieval mandatory in unit tests.
- Do not rely on prompt wording to enforce source authority.
- Do not mark unknown freshness or contradiction state as pass.

## Slice 4 — Enforce the envelope in apps_rg and add cross-section parity

**Files likely touched**

- `apps_rg/integrations/apps_research_bridge.py`
- `apps_rg/integrations/managed_research_delegation.py`
- `apps_rg/runtime/orchestration/r3r4_whole_run_orchestration.py`
- `apps_rg/runtime/bindings/briefing_u0_signals.py`
- `apps_rg/runtime/bindings/l1_binding.py`
- `apps_rg/runtime/briefing_resolution.py`
- `apps_rg/runtime/pre_dispatch_preflight.py`
- `apps_rg/prerequisites/briefing_validator.py`
- `apps_rg/enforcement/cli_prerequisite_gate.py`
- `apps_rg/runtime/targeting_input_freshness.py`
- `apps_rg/runtime/orchestration/canonical_dispatch.py`
- `apps_rg/runtime/orchestration/section_lane_executor.py`
- `apps_rg/runtime/spine/section_cli_runners.py`
- shared graph assessment and whole-run summary modules

**Expected tests**

- `test_apps_research_handoff_envelope.py`
- `test_briefing_freshness_and_digest.py`
- `test_briefing_route_policy.py`
- `test_section_graph_receipt_parity.py`
- `test_anthropic_partnership_resume_graph_proof.py`

**Acceptance criteria**

- Product mode remains upload-only and cannot invoke the legacy bridge.
- L1 validates the canonical envelope before any section work.
- Company, role, JD, brief, semantic receipt, and source-register digests match.
- Every lane receives the same verified brief digest.
- Every graph-backed section emits the common assessment and all required machine receipts.
- Whole-run summary blocks on a missing receipt, digest drift, critical-axis failure, or unresolved arbitration.
- The Anthropic E2E run proves research family coverage, graph authority, traversal, granularity, claim binding, and final handoff in one digest chain.

**Rollback risk**

Medium to high operationally because the product will fail closed on old/plain-text brief artifacts. Provide an explicit one-time compatibility adapter that creates and validates an equivalent envelope from a legacy artifact only when all required metadata can be independently established. Do not silently accept legacy text.

**What not to change**

- Do not enable automatic apps_research delegation on the product critical path.
- Do not create per-section variants of the envelope.
- Do not hide a missing section receipt behind an aggregate warning.
- Do not make the judge the arbiter of source authority.

## Later / optional

- Curate duplicate/coarse capability groups and retire aliases after runtime normalization is proven.
- Add bounded model-assisted entailment for claims that cannot use deterministic canonical mappings.
- Add an operator UI over the same receipts; do not create a second telemetry truth.
- Add trend telemetry for concentration, axis coverage, selector/judge disagreement, and rejected-candidate distributions.
- Consider graph storage changes only if the existing JSON/ledger substrate cannot support immutable versioned edge IDs and efficient candidate accounting. No current finding proves a new store is necessary.

# 6. Test plan

No test below exists in the uploaded archives. These are the minimum implementation-ready tests that would expose the current weaknesses.

| Failure mode | Proposed test and mutation | Assertion | Would current code likely fail the proposed test? |
|---|---|---|---|
| Generic easy-node collapse | `test_graph_easy_node_collapse.py`: reorder bundle and skill arrays; insert high-token-overlap generic nodes before specific leaves. | Selection is order-invariant; generic parent cannot displace higher-authority specific leaves; selected/rejected score deltas are stable. | Yes. Skill truncation uses source-list order and there is no specificity/leaf gate. |
| Repeated flat confidence | `test_competencies_confidence_decomposition.py`: construct categories with materially different path specificity, fact diversity, metric quality, selector score, and judge score. | Component values and composite confidence differ for evidence reasons; no fabricated jitter; missing components reduce confidence explicitly. | Likely. Current components can flatten because structural ratios and broad judge scores are reused. |
| Overuse of one source fact | `test_source_fact_concentration_semantic.py`: use multiple alias IDs that all resolve to one base fact/document. | Alias-normalized dominant share exceeds threshold and blocks; unique ID count cannot mask reuse. | Yes. Current concentration is ID/count oriented and allows 0.75 dominance. |
| Missing rejected siblings | `test_graph_traversal_receipt.py`: remove all unselected roots from receipt while retaining cap-excluded child IDs. | Candidate conservation fails; cap exclusions do not stand in for unvisited roots. | Yes. Current receipt would still have rejected sibling counts. |
| Shallow traversal | Same test: provide selected root/skill/metric IDs without visited edges or with a missing source-fact hop. | Actual path-depth gate fails; hardcoded depth cannot pass. | Yes. Current depth is inferred. |
| Missing metrics | `test_graph_metric_binding.py`: critical outcome category has no metric, or metric is unapproved/wrong-section/wrong-root. | Outcome-bearing category blocks or emits an explicit non-outcome exception; invalid metrics do not improve richness/confidence. | Yes for several sections; current depth can pass on ID presence and EY currently has zero metrics. |
| Missing role-specific axes | `test_graph_role_axis_coverage.py`: remove co-sell, partner ecosystem, joint solution/technical integration, adoption/customer success, or outcome evidence from Anthropic plan. | Each critical axis must have authority-clean leaf paths and facts; lexical JD terms alone cannot pass. | Yes. Current axis checks are largely lexical/count based. |
| JD/brief proof leakage | `test_jd_brief_targeting_only.py`: add an ineligible high-overlap skill phrase to JD/brief and attach an unrelated allowed ID to output. | Eligibility and proof confidence remain unchanged; output claim fails without claim binding. | Yes. Current selector and confidence use JD/brief before authority separation. |
| Stale apps_research briefing | `test_briefing_freshness_and_digest.py`: envelope timestamp older than TTL, `generated_at_utc`, valid Markdown. | Consumer computes age from canonical timestamp and blocks stale input. | Yes/uncertain path. Current validator looks for different timestamp keys; exact product invocation requires integration confirmation. |
| Stub/dry-run briefing | `test_targeting_cli_no_stub_dryrun.py`: dry-run, obvious stub, and semantically generic non-stub text. | No product-eligible envelope or Markdown is emitted; generic non-stub fails semantic gate. | Generic non-stub would pass current syntactic sealing; obvious stub/dry-run already has partial protection. |
| Handoff digest mismatch | `test_handoff_artifact_digest_binding.py`: mutate Markdown, source register, or JD after sealing. | Producer/consumer digest chain fails closed. | Yes. No mandatory canonical envelope is consumed today. |
| Section drift | `test_section_graph_receipt_parity.py`: omit or alter one lane's receipt/graph digest. | Whole-run graph summary blocks and names the lane. | Yes. No common whole-run graph parity gate exists. |
| Selector/judge disagreement | `test_graph_selector_judge_arbitration.py`: authority fail + judge pass; authority pass + judge fail; digest mismatch. | Explicit precedence; authority failure always blocks; unresolved disagreement cannot allow. | Yes. No central arbitration receipt exists. |
| Plan identity split | `test_competencies_single_plan_binding.py`: force competencies payload and role selector to choose different IDs. | Resolver blocks before generation. | Yes. Current resolver stores both plans. |
| Policy-ineligible nodes | `test_graph_selector_authority_filter.py`: use current Anthropic fixtures and declared ledger policies. | Zero selected policy violations in every section. | Yes. The direct probe found violations in every section group. |

## Anthropic end-to-end acceptance test

`apps_rg/tests/e2e/test_anthropic_partnership_resume_graph_proof.py` should run with deterministic model substitutes and the shipped fixtures. It should assert:

1. The apps_research envelope is semantically eligible for partnership targeting and covers all critical research families.
2. Producer and consumer bind company, role, JD digest, brief digest, source register, and freshness.
3. Every selected graph node passes authority policy.
4. All eligible candidates are accounted for.
5. Every critical axis has at least two leaf skills and two independent base facts.
6. Outcome claims have approved metrics.
7. No single base fact dominates a critical category above 50%.
8. Every section emits the common assessment and uses the same graph/ledger/brief digests.
9. Selector, X2, judges, and X3 have no unresolved disagreement.
10. The final whole-run `resume_graph_sourcing_summary.json` is `ACCEPTABLE` and links all receipts.

# 7. Artifact plan

## apps_rg per-section artifacts

All per-section artifacts should live in the existing section artifact directory. JSONL artifacts should be stable-sorted and include a schema version on every row or in an adjacent manifest.

| Filename | Producer | Required schema fields | Pass/fail interpretation | How a human reads it |
|---|---|---|---|---|
| `graph_candidate_decision_ledger.jsonl` | `graph_role_episode_selector` | `schema_version`, `run_id`, `section_id`, `plan_id`, `plan_digest`, `candidate_id`, `candidate_type`, `parent_id`, `root_id`, `employer`, `path_edge_ids`, `hop_depth`, `pretarget_policy`, `source_fact_base_ids`, `metric_ids`, `leaf_status`, `freshness_status`, `selector_components`, `selector_score`, `decision`, `reason_codes`, `score_delta_to_selected` | Pass when every discovered eligible/ineligible candidate has exactly one terminal decision and all selected rows are pretarget-eligible. | Filter by root or reason to see what won, what lost, and whether rejection was policy- or relevance-driven. |
| `graph_traversal_receipt.json` | Selector/traversal engine | graph/ledger digests, candidate totals, `visited_nodes`, `visited_edges`, ordered events, per-hop `frontier_before`, `attempted`, `visited`, `selected`, `rejected`, `skipped`, stop reasons, max depth, unexplained count | Pass when edge/path validation succeeds and conservation holds with zero unexplained candidates. | Read the summary first; inspect per-hop rows to see whether the search actually expanded beyond easy nodes. |
| `graph_selection_binding_receipt.json` | Proof-pool resolver | canonical plan ID/digest; graph/ledger digests; proof-pool, prompt, claim-ledger, X2, X1D, X3 digests; equality booleans | Any mismatch is a block. | One-page identity chain showing whether every stage evaluated the same evidence. |
| `graph_evidence_authority_receipt.json` | Pre-target authority filter | selected root/skill/fact/metric IDs; activation, section, external policy, visibility, fact-link, approval, binding, source authority, freshness; reason codes | Pass only when every selected item passes every mandatory policy. | Scan failures by policy field; no model interpretation required. |
| `graph_granularity_receipt.json` | Semantic graph gate | category, canonical leaf IDs, parent exceptions, duplicate groups, base fact IDs, document IDs, metric bindings, concentration shares, required axes, coverage result | Critical category passes with ≥2 distinct leaves, ≥2 independent base facts/documents, valid outcome binding, dominant fact ≤50%, and all required axes covered. | Shows whether “many IDs” represent genuinely diverse, specific proof. |
| `graph_claim_binding_receipt.jsonl` | Section claim ledger/X2 | output claim/term ID and text hash, plan digest, root, leaf skill, source fact/base fact/document, source span/ref, metric, entailment method/verdict, authority verdict | Every externally meaningful claim must have a passing row; unrelated allowed IDs do not count. | Search the exact output phrase and follow its evidence path. |
| `graph_selector_judge_arbitration_receipt.json` | Central arbitration step | plan/proof digest, selector result, authority/traversal/granularity/claim gate results, judge scores/verdicts and packet digests, disagreements, precedence rule, repair attempt, final disposition | Pass only with no unresolved disagreement and no deterministic authority failure. | Explains why the final decision was allow/review/block and which control had authority. |
| `section_graph_sourcing_assessment.json` | Shared section reporting module | role/profile, selected roots, leaf skills, metrics, top rejected siblings, traversal summary, confidence components, critical axes, authority/granularity/claim/arbitration verdicts, artifact refs | `ACCEPTABLE` only when all required machine gates pass. | The concise operator view; links to deeper receipts rather than duplicating them. |
| `briefing_consumption_receipt.json` | L1/briefing resolver | envelope schema, normalized company/role, JD/brief/source/semantic digests, generated/expiry/validated timestamps, source route, stub/dry-run flags, semantic and freshness verdicts, resolved text digest | Any mismatch, expiry, ineligibility, or route-policy violation blocks before lanes. | Confirms exactly which brief every section received and why it was accepted. |

## apps_rg whole-run artifacts

| Filename | Producer | Required schema fields | Pass/fail interpretation | How a human reads it |
|---|---|---|---|---|
| `resume_graph_sourcing_summary.json` | Whole-run orchestration after all lanes | required sections, receipt refs/digests, common graph/ledger/brief digests, per-section verdicts, critical axes, concentration maxima, missing receipts, unresolved disagreements, final acceptability | Pass only when every required graph-backed section is acceptable and identity digests agree. | Start here for a whole-resume audit; it names the exact failing section and receipt. |
| `briefing_route_policy_receipt.json` | U0/L1/orchestration | product/non-product mode, policy version, delegation allowed, actual route, bridge invoked, artifact source, L1 result | Product pass requires upload-only and no bridge invocation. | Shows whether handoff behavior matched the declared product contract. |
| `graph_authority_dependency_receipt.json` | Preflight | required authority paths, schema versions, expected/actual digests, availability, optionality, disposition | Missing or mismatched required authority blocks. | Confirms the run did not depend on invisible or mutable graph/fact artifacts. |

## apps_research artifacts

| Filename | Producer | Required schema fields | Pass/fail interpretation | How a human reads it |
|---|---|---|---|---|
| `apps_rg_targeting_brief.md` | Company brief engine | Human-readable brief with canonical sections; no hidden authority role | Usable only when its SHA matches an eligible envelope. | Read the brief; use envelope/receipts to assess trust. |
| `apps_rg_targeting_brief_envelope.json` | Company brief engine / envelope emitter | schema/version, producer/run/model, normalized company/role, JD SHA, brief SHA, generated/expiry, semantic receipt SHA/status/score, source register SHA/status, C0 verdict, contradiction/freshness verdicts, dry-run/stub flags, handoff eligibility | `handoff_eligible=true` only when every required gate passes; immutable after emission. | The authoritative handoff cover sheet. |
| `apps_rg_targeting_brief_semantic_receipt.json` | Semantic assessor | role profile, required/present sections, required/planned/attempted/covered families, critical role axes, signal evidence refs, score, failures, handoff verdict | Missing critical family/axis blocks partnership handoff. | Shows whether the brief is substantively useful, not just correctly formatted. |
| `apps_rg_targeting_brief_source_register.json` | Research evidence lineage | source ID, canonical URL/document ID, title, domain, source type, authority tier, published/fetched timestamps, freshness, document SHA, claim IDs, family IDs | Critical family needs authority-qualified, fresh claim bindings; duplicates count once. | Inspect source quality and which claims each source supports. |
| `research_claim_source_binding.jsonl` | Research synthesis/lineage | claim ID/text hash, family, source IDs, support spans, contradiction status, confidence, freshness, synthesis disposition | Unsupported or contradicted critical claim blocks or reviews. | Trace each targeting assertion to source evidence. |
| `research_family_coverage_receipt.json` | Query decomposer/retrieval orchestrator | role profile, canonical family, aliases, required flag, queries, attempts, results, supported claim count, omission reason | All critical role families must be planned and supported. | Reveals whether research effort covered the partnership questions. |
| `apps_rg_handoff_receipt.json` | Research CLI/artifact writer | envelope/brief/source/semantic hashes, atomic write result, output paths, producer schema, handoff status | Pass when all artifacts exist, hashes match, and envelope is eligible. | Confirms the emitted bundle is internally consistent before upload. |

# 8. Non-goals

The hardening work should explicitly avoid the following:

- **No broad rewrite.** Preserve current section architecture, graph JSON substrate, proof-pool interfaces, and product flow where possible.
- **No new graph store unless unavoidable.** The current failure is missing authority/traversal contracts, not proven storage incapacity.
- **No moving proof authority to JD or briefing.** They remain targeting inputs only.
- **No enabling apps_research auto-delegation on the apps_rg product critical path.** The canonical product contract remains a required uploaded artifact.
- **No hiding correctness failures behind warnings.** Authority, digest, traversal, claim binding, freshness, critical-axis, and handoff failures are blocking.
- **No accepting selected-only evidence as traversal proof.** A traversal receipt must account for the candidate space and actual edges visited.
- **No prompt-only hardening.** Prompts may communicate the contract, but deterministic receipts and gates enforce it.
- **No synthetic confidence variation.** Repeated confidence values must be fixed by evidence decomposition, not jitter.
- **No judge override of deterministic authority.** Judges assess quality; they do not create proof or legalize invalid evidence.
- **No mass graph renaming or deduplication in the first slices.** Normalize at read time, then curate safely with tests.
- **No resume prose rewrite as part of infrastructure hardening.** First make evidence selection and proof auditable; content changes can follow through normal generation.
- **No silent legacy compatibility.** A legacy plain-text brief may use an explicit compatibility adapter only when equivalent metadata and proof can be established; otherwise block.

## Final implementation sequence

The safe order is: **one plan → policy-clean candidates → real traversal → claim/metric binding → arbitration → authoritative research envelope → consumer enforcement → cross-section parity → inventory curation.** Reversing that order risks polishing outputs while preserving the proof gaps.
