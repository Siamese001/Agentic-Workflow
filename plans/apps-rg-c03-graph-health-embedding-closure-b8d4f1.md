---
plan_id: apps-rg-c03-graph-health-embedding-closure-b8d4f1
plan_format: v2
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: "artifacts/governance/core_addition_author_gate/apps-rg-c03-graph-health-embedding-closure-b8d4f1.json"
dod_exempt: false
supersedes: []
base_ref: codex-apps-rg-graphdb-hardening
base_sha: a587a578c9ff0589d6f8cecb4b50b3bc91145493
---

# apps_rg C0.3 Graph Health, Provenance, and Conditional Embedding Closure

Close the remaining graph-data and operational-evidence gaps on the hardened C0.3 branch, qualify rather
than assume the value of embeddings, and release only after graph health and the full apps_rg product proof
are genuinely green.

> **Planning boundary:** this file is the requested plan artifact. It does not authorize implementation.
> Continue on the existing `codex-apps-rg-graphdb-hardening` branch and PR #565 only after explicit approval.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: D0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-07-19
IMPLEMENTATION_AUTHORIZED: YES
PROMOTION_ELIGIBLE: false
STOP_CONDITION: the bounded D0 repair fails to produce a certified ADG, or reviewed source authority, operational evidence, and product-run proof remain absent

---

## Context (SCQA)

- **Situation** — Candidate commit `a587a578c9ff0589d6f8cecb4b50b3bc91145493` hardens the canonical
  JSON-to-SQLite projection, runtime read purity, graph invariants, and a 37-metric NEE-inspired health
  receipt. Its exact-head CI is green; focused and broad suites passed 137 and 369 tests respectively.
- **Complication** — Engineering integrity is stronger than data readiness. Current health is
  `control_plane_status=UNKNOWN`, `graph_data_readiness=NOT_READY`, and `overall_status=NOT_READY`.
  The checked-in graph lacks 75 graph-bound skill proofs, 84 required node source references, four skill
  graph nodes, and 19 domain/epoch bindings. Seven operational dimensions are `UNKNOWN`. A fresh ADG audit
  also found repository-wide P0/write-sovereignty blockers and did not produce a certified snapshot pointer.
- **Question** — How do we close the real provenance and certification gaps, and should C0.3 add a unique
  embedding for graph records?
- **Answer** — Close source authority and decision readiness first. Do **not** add production graph
  embeddings now. After graph health is green, run a frozen shadow qualification against the existing
  exact-graph and `fact_vectors` baselines. Only a measured semantic-retrieval gain may authorize one
  derived embedding per evidence-bearing canonical skill assertion; naked nodes, edges, paths, and
  projection rows never receive independent authority-bearing embeddings.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| D0 | D0.1, D0.2, D0.3, D0.4 | Repair the three ADG P0 gate classes, runtime index concurrency, and runtime-proof/certification finalization | ~42K | User authorized repo-wide expansion with `Expand` on 2026-07-18 | 🟨 IN PROGRESS | Fresh exact-SHA audit has zero blocking P0 rows, lossless concurrent index publication, attested runtime proof, complete manifests, and a digest-verified certified pointer |
| W0 | W0.1, W0.2, W0.3 | Restore structural proof, pin cohorts, and emit exact recovery registers | ~24K | D0 is merged into the feature candidate | ⏸ BLOCKED ON D0 | Certified ADG is callable; every current KPI failure has an exact locator, owner class, and disposition |
| W1 | W1.1, W1.2, W1.3, W1.4 | Close measurement blind spots, then execute reviewed source recovery and canonical assertion closure | ~56K | Authoritative source material and human review are available | 🔲 TODO | Every invariant has a typed denominator/locator; 254/254 skill assertions are graph-bound or explicitly non-retrieval-eligible; no evidence is fabricated |
| W2 | W2.1, W2.2, W2.3 | Unify canonical/SQLite semantics, rebuild projections, and certify graph-data KPIs | ~44K | W1 source decisions are digest-bound and approved | 🔲 TODO | `graph_data_readiness=PASS`; typed edges, node types, path capability, same-snapshot reads, and structural zero-defect invariants are green |
| W3 | W3.1, W3.2, W3.3 | Replace seven `UNKNOWN` control-plane metrics with producer-bound evidence | ~34K | Real operational sources exist for every required dimension | 🔲 TODO | `control_plane_status=PASS` without self-attestation or synthetic authority |
| W4 | W4.1, W4.2, W4.3 | Determine whether embeddings add measurable retrieval value | ~38K | W2 and W3 pass; frozen labeled queries and two reviewers are available | 🔲 TODO | A digest-bound `QUALIFIED_GO` or `NO_EMBEDDING_PROMOTION` decision is produced |
| W5 | W5.1, W5.2, W5.3 | Conditional evidence-bearing skill-assertion embedding projection | ~36K | Runs only if W4 returns `QUALIFIED_GO` | 🔲 TODO | One active vector per eligible skill assertion; zero stale, leaked, or authority-bypassing results |
| W6 | W6.1, W6.2, W6.3 | Full apps_rg certification, PR merge, and exact main convergence | ~42K | User supplies exact run inputs; every preceding mandatory gate passes | 🔲 TODO | Fresh 11/11 run, valid DOCX and receipts, merged PR, and exact local/origin ancestry |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| D0.1 | Correct write-sovereignty and UWG view classification | DONE |
| D0.2 | Harden fail-fast manifest finalization and runtime-proof recovery | DONE |
| D0.3 | Merge the ADG repair branch into main and consume it on the feature branch | 🟨 IN PROGRESS |
| D0.4 | Remove the real apps_rg direct-SQLite violation and certify the exact feature SHA | 🔲 TODO |
| W0.1 | Restore certified ADG pointer and active-session health | ⏸ BLOCKED ON D0 |
| W0.2 | Pin candidate SHA, graph digests, and frozen KPI denominators | 🔲 TODO |
| W0.3 | Emit source, coverage, operational, and ADG dependency registers | 🔲 TODO |
| W1.1 | Close KPI/validator measurement blind spots | 🔲 TODO |
| W1.2 | Review and authorize exact source recovery | 🔲 TODO |
| W1.3 | Close missing skill-node, domain, and epoch mappings | 🔲 TODO |
| W1.4 | Close claim-evidence and required source-reference gaps | 🔲 TODO |
| W2.1 | Revalidate canonical closed-world assertions | 🔲 TODO |
| W2.2 | Rebuild and validate SQLite v3 projection | 🔲 TODO |
| W2.3 | Produce graph-data PASS receipt and negative controls | 🔲 TODO |
| W3.1 | Define operational-evidence producer and cohort contract | 🔲 TODO |
| W3.2 | Bind all seven operational metrics to real evidence | 🔲 TODO |
| W3.3 | Prove control-plane rollup and read/write purity | 🔲 TODO |
| W4.1 | Freeze route-balanced queries, qrels, and baseline arms | 🔲 TODO |
| W4.2 | Benchmark exact, fact-vector, dense, and hybrid candidate retrieval | 🔲 TODO |
| W4.3 | Issue embedding promotion/no-promotion decision | 🔲 TODO |
| W5.1 | Build deterministic `C03SkillAssertionDocumentV1` corpus | 🔲 TODO |
| W5.2 | Build and validate immutable exact-vector SQLite generation | 🔲 TODO |
| W5.3 | Add candidate-only runtime adapter and rehydration guard | 🔲 TODO |
| W6.1 | Run focused, broad, contract, security, and mutation gates | 🔲 TODO |
| W6.2 | Run and inspect the fresh 11/11 apps_rg product proof | 🔲 TODO |
| W6.3 | Merge without squash and prove local/origin main convergence | 🔲 TODO |

---

## Evidence Baseline

### Directly observed

| Surface | Current candidate evidence | Disposition |
|---|---|---|
| Candidate branch | `codex-apps-rg-graphdb-hardening@a587a578c9ff0589d6f8cecb4b50b3bc91145493`; PR #565 | Continue the same objective/branch; no new wave PR |
| Regression proof | 137 focused tests and 369 broad apps_rg graph/runtime tests passed; exact-head GitHub checks passed | Preserve as the minimum branch regression floor |
| Live health | 37 KPIs currently resolve to 23 `PASS`, 7 `FAIL`, and 7 `UNKNOWN` | Treat structural health, data readiness, and operational evidence as separate release dimensions |
| Canonical graph | 371 graph nodes, 1,908 canonical edges, 254 canonical skill rows; projected SQLite has 774 nodes and 2,364 edges | JSON remains authority; generated stores remain projections |
| Structural closure | Registered endpoints 3,816/3,816; orphan edges 0/1,908; FK 13/13; reverse/path/sibling/neighborhood integrity PASS | Do not rewrite a green structural substrate to mask data gaps |
| Claim evidence | 179/254 complete; nine skills declare no facts and 66 have incomplete graph bindings | Source-authority remediation, not an embedding problem |
| Skill-node parity | 250/254; missing `skill_meddpicc_sales_qualification`, `skill_cpq_deal_velocity_automation`, `skill_saas_arr_ltv_cac_metrics`, `skill_nps_customer_health_scoring` | Add only from approved canonical rows and exact mappings |
| Required node sources | 117/201 complete; 84 required nodes lack source references | Resolve through source recovery or explicit non-eligibility; never synthesize citations |
| Domain and epoch | Row fields are 235/254 complete for each, but actual graph edges cover only 217/254 domains and 198/254 epochs | Measure field and edge completeness separately; close exact mappings from approved taxonomy authority |
| Edge semantics | 25/32 observed edge types lack canonical semantics and three edge types are singletons | Establish one typed edge-semantics/signature registry and adjudicate rare types before declaring graph health |
| Projection semantics | Endpoint existence is checked, but edge-to-node signatures are not; canonical `metric`/`metric_bucket` collapse to `metric_outcome`; base and applicator path capabilities differ | Make projection lossless and capability-versioned before certifying semantic parity |
| Read/admission hardening | Runtime verifies, closes, and reopens the DB; same-count semantic tamper and reopen races are not excluded; admission covers 5/8 relevant tables and 10/13 expected FK signatures | Add same-snapshot reads, semantic digests, and complete admission manifests |
| Operational metrics | `decision_safe_regression`, `source_currentness`, `source_freshness`, `hitl_approval_coverage`, `write_audit_coverage`, `p0_sla_compliance`, and `p1_sla_compliance` are `UNKNOWN` | Bind to real producer artifacts or remain blocked |
| Existing embeddings | apps_rg already defines local `BAAI/bge-m3`, 1,024-dimensional, precomputed Chroma `fact_vectors`, keyed by canonical fact ID and explicitly non-authoritative | Reuse the governed model contract; keep the optional skill projection separate from fact vectors and graph v3 |
| NEE comparison | NEE embeds deterministic evidence-bearing assertions, not naked nodes/edges; its latest available model qualification failed Recall@20 at 0.375 against a 0.90 floor | Adopt assertion/document governance, not the failed performance claim |
| Closeout receipt | The committed receipt names pre-feature HEAD `e46d8d37`, records `dirty_after=true`, and ends `execution.status=PARTIAL` | Replace with an exact-candidate-SHA clean run receipt; do not use it as certification evidence |

### ADG graph-layer evidence

`ADG Provenance: backend=degraded_sqlite, snapshot=adg_indexed_07182026_1105.sqlite`

- The active ADG MCP is callable but reports `critical`: certified pointer missing, certification unknown,
  canonical SQLite unavailable, and projection status unknown. This evidence is diagnostic only.
- The fresh diagnostic materialized view ranks the likely high-risk existing modules as follows:
  `embedding_settings.py` fan-in 63/fan-out 16; `augmented_skills_graph_sqlite.py` 63/23;
  `master_skills_arsenal_ledger.py` 60/5; `fact_vector_readiness.py` 17/15;
  `c03_graph_sqlite_context.py` 12/21; `c03_sqlite_graph_selection.py` 5/15.
- Scope consequence: prefer new app-owned document, qualification, and adapter modules; minimize edits to
  the high-centrality model/settings and graph materializer modules. W0 must repeat fan-in, fan-out, P-view,
  and semantic-edge analysis from a certified candidate snapshot before any implementation edit.
- Fresh audit run `07182026_1105` remains a separate repository dependency: 131 write-sovereignty findings,
  two P0 layer violations, and `dependency_not_ready`. This plan consumes the repaired handoff; it does not
  widen into repo-wide ADG remediation.

### Derived conclusions

1. Embeddings cannot repair missing facts, source locators, lifecycle/currentness, HITL approvals, or write
   audit evidence. Creating them before W1-W3 would make unsupported content easier to retrieve.
2. Existing fact vectors already provide semantic retrieval at the fact grain. A second vector per raw fact,
   graph edge, path, neighborhood, section, or role would duplicate state and create invalidation ambiguity.
3. The only defensible future graph embedding grain is a deterministic, evidence-bearing logical assertion
   that rehydrates to current canonical IDs and sources. In apps_rg, that is one canonical skill row/claim,
   not one physical SQLite row.
4. At 254 skills, a normalized 1,024-dimensional float32 matrix is roughly 1 MiB. Exact cosine/dot-product
   search in a separate immutable SQLite projection is simpler and safer than adding ANN/Chroma lifecycle
   coupling to graph v3. Chroma remains a future scale-up option only after measured need.

### Unresolved inputs

- Reviewed source material and authority decisions for the 75/84 provenance gaps.
- Whether semantic candidate recall is a measured bottleneck after exact graph and existing fact-vector
  retrieval are evaluated on the same frozen query set.
- Exact target company, role, level, JD, and research briefing for the final fresh product run.
- A certified ADG pointer and downstream-ready repair handoff.

---

## Gap Register

| ID | Severity | Gap | Authority class | Required closure |
|---|---:|---|---|---|
| G01 | P0 | Certified ADG pointer/materialization unavailable | Structural dependency | Restore certified pointer, verified digest, green MCP health, P-view and semantic-edge queries |
| G02 | P0 | 75/254 skill assertions lack graph-bound claim proof | Source/human authority | Exact fact IDs and source lineage, or explicit non-retrieval eligibility |
| G03 | P0 | 84/201 required nodes lack `source_refs` | Source/taxonomy authority | Reviewed source refs appropriate to claim, taxonomy, policy, or deterministic derivation type |
| G04 | P0 | Four canonical skill rows lack graph nodes | Canonical data mapping | One node per exact `skill_id`, correct type/signature, no duplicate identity |
| G05 | P1 | Domain/epoch fields are each 235/254 while graph edges are only 217/254 and 198/254 | Canonical taxonomy mapping | Exact approved field plus edge per affected skill, with negative conflict checks |
| G06 | P0 | Seven required control-plane metrics are `UNKNOWN` | Operational evidence | Digest-bound producer evidence; no arbitrary `VERIFIED` flag or self-declared hash |
| G07 | P0 | ADG audit has two distinct critical write sites, one direct-infrastructure import, incomplete fail-fast manifests, and zero indexed runtime proof | Authorized dependency lane | Execute D0 on a fresh ADG repair branch, merge it into main, consume it on the feature branch, and certify without waivers |
| G08 | P1 | No frozen apps_rg test proves graph-skill semantic retrieval quality | Evaluation | Route-balanced labeled query/qrel set, baseline arms, error taxonomy, two-reviewer adjudication |
| G09 | P1 | No graph-skill embedding corpus contract exists | Optional derived projection | Execute W5 only after W4 `QUALIFIED_GO`; otherwise record `NO_EMBEDDING_PROMOTION` |
| G10 | P0 | Official W6 PASS and fresh 11/11 product/DOCX proof are absent | Product release | Fail-closed official W6 receipt, exact user-owned inputs, all mandatory artifacts, per-lane judge/X2/X3 evidence, rendered inspection |
| G11 | P0 | KPI validators conflate row fields with graph edges and omit typed reference/edge resolution | Measurement contract | Versioned numerator, denominator, locator, and authority class for every invariant; adversarial fixtures fail deterministically |
| G12 | P0 | SQLite projection loses node-type distinctions, exposes path-capability drift, and has TOCTOU/admission gaps | Projection/runtime code | Lossless typed projection, one path capability/version, same-snapshot verification/read, complete table/FK manifests |
| G13 | P0 | Current run receipt is stale/dirty/partial and CI does not yet gate live canonical health | Certification | Exact-head clean receipt plus live validator/KPI artifact upload; make blocking only after governed data closure |

The gap counts overlap and field/edge denominators differ. W0 must emit exact row locators and set
intersections; it must not sum headline counts into a false count of independent records.

---

## Embedding Architecture Decision

### Decision now: do not create production graph embeddings

Production embedding creation is deferred until W4. The current objective is blocked by evidence authority,
not demonstrated semantic candidate recall. NEE provides a strong assertion-envelope pattern but no healthy
performance precedent: its available BGE-M3 qualification is failed/unlocked. apps_rg already has canonical
fact embeddings, so a second graph corpus must earn its operational cost and failure surface.

### Conditional unit if W4 qualifies embeddings

Create exactly one `C03SkillAssertionDocumentV1` per canonical `skill_rows[].skill_id` that is atomic,
source-complete, lifecycle-current, and retrieval-eligible.

The logical document is the embedding unit:

| Field group | Required contents |
|---|---|
| Identity | `assertion_id=skill_id`, schema version, canonical ledger digest, skill-row digest |
| Semantics | canonical label/capability, approved description/phrases, predicate `demonstrates_capability` |
| Scope | pillar, capability domain, career epoch/track, allowed sections, role-family facets |
| Authority | activation, support, visibility, external-claim policy, human-confirmation state |
| Lineage | sorted `fact_id_links`, required source refs/locators, source-lineage digest |
| Retrieval state | approved/retrieval-eligible namespace only for production; exclusions get reason receipts |
| Vector binding | local model ID, full model revision/artifact digest, dimension, document SHA-256, corpus generation digest |

Rules:

- One active vector per logical `skill_id` within a corpus generation. Section, role, employer, and query
  variants are metadata/filters, not duplicate embeddings.
- If a skill row contains materially different claims, split the canonical skill assertion through reviewed
  source authority before embedding. Never hide multiple assertions behind one averaged vector.
- Existing `fact_vectors` remain the only fact-level embeddings. The skill assertion stores fact IDs and
  source lineage; it does not mint a second fact authority.
- The text sent to the embedding model is a deterministic semantic card derived from approved label,
  capability, description/phrases, pillar/subpillar, domain, epoch/track, skill family, and metric bucket.
  Raw claim text, source spans, facts, authority policy, eligibility, role weights, and paths remain exact
  fields/digests in the assertion envelope and are not blended into vector similarity.
- Metric values, path rows, reverse edges, siblings, neighborhoods, budgets, policies, receipts, and
  aggregating domain/pillar nodes receive no unique embeddings. Their exact graph structure is the feature.
- Query/JD embeddings are ephemeral request inputs. They are not canonical graph records.
- Dense similarity produces candidate `skill_id`s only. Runtime must rehydrate the current assertion hash,
  apply exact authority gates, and traverse canonical SQLite paths before selection.
- Embedding score is targeting relevance, never proof confidence, source authority, or claim permission.
- Build is offline and content-addressed; runtime is read-only. A stale ledger, model, document, or corpus
  digest makes the vector route unavailable without repairing or writing during the read.

### Conditional physical projection

Keep vectors out of graph SQLite v3. W5 creates a separate immutable generation named
`graph_skill_embeddings.<projection_digest>.sqlite` and atomically publishes an `active.json` pointer only
after validation and a second source-digest check. At the current 254-skill scale, rank pre-normalized
float32 vectors with application-side exact dot product; no ANN extension or Chroma collection is needed.

| Table | Required contract |
|---|---|
| `projection_metadata` | schema/card versions; canonical and SQLite graph digests; exact card-input digest; graph-index/materializer versions; model ID and immutable fingerprint; dimension, dtype=`float32-le`, normalized flag; row count, ordered matrix digest, build time |
| `skill_embeddings` | `skill_id` primary key; deterministic `card_text` and SHA-256; dimension; little-endian float32 blob with nonempty/hash/dimension/length constraints |

The builder must read ordered card inputs from graph v3 in one short read transaction, close graph v3
before model inference, validate a fresh generation, reopen graph v3, and reject promotion if any bound
digest changed. Published generations use DELETE journal mode and are opened with `mode=ro` plus
`query_only=ON`. Readers pin one generation for the request; cleanup observes a grace period and never
deletes the active generation. Missing/stale projection falls back to the deterministic graph path unless
the caller explicitly requires dense routing, in which case the route fails closed.

### W4 qualification arms and promotion thresholds

Use a frozen, blinded set of at least 55 holdout queries: at least five per each of the eleven claim-bearing
lanes, plus adversarial alias, unsupported-claim, stale-source, and wrong-section negatives. Two independent
reviewers grade qrels on a fixed 0-3 scale; development and holdout sets remain separate.

| Arm | Candidate generator | Authority after retrieval |
|---|---|---|
| A | Exact/sparse canonical SQLite graph only | Exact graph gates and paths |
| B | Existing `fact_vectors` plus graph expansion | Fact rehydration plus exact graph gates |
| C | Proposed skill-assertion dense BGE candidates | Assertion rehydration plus exact graph gates |
| D | Proposed BGE dense+sparse hybrid, then exact graph | Assertion rehydration plus exact graph gates |

`QUALIFIED_GO` requires all of the following on untouched holdout data, preserving the existing apps_rg
retrieval rubric/profile floors rather than inventing a new threshold set:

- Recall@10 at least 0.95 and nDCG@10 at least 0.90;
- authority-eligibility accuracy exactly 1.00 and exact-path accuracy exactly 1.00;
- claim-entailment accuracy at least 0.90, metric-binding accuracy at least 0.95, proof-candidate precision
  at least 0.90, and expected calibration error at most 0.05;
- the qualified hybrid improves at least one of Recall@10 or nDCG@10 over the better of A and B, while
  degrading neither retrieval KPI materially and degrading none of the authority/path gates;
- zero per-lane material regression and zero decision-safe product regression; Spearman/MRR remain reported
  diagnostics unless a separately approved evaluation profile makes them release gates;
- 100% eligible-document/skill parity, canonical-ID hydration, source-lineage completeness, deterministic
  top-K reproducibility, and content/model/pipeline/graph digest parity;
- zero orphan, duplicate-active, stale, ineligible/forbidden-source, unauthorized, or authority-bypassing
  vectors/candidates and zero runtime writes;
- local artifact-pinned BGE-M3 only, zero network egress, 1,024 finite normalized float32 dimensions, and
  warm-query p95 within the existing 12-second section budget with zero budget breaches.

If any threshold fails, W4 emits `NO_EMBEDDING_PROMOTION`, W5 is not executed, and W6 proceeds on the exact
graph/fact-vector architecture. A no-go result is a successful decision, not an invitation to lower gates.

---

## Scope and Ownership

### Expected edit scope after approval and W0 revalidation

- Canonical data and validation:
  - `apps_rg/fact_inventory/master_skills_arsenal_ledger.json`
  - `apps_rg/fact_inventory/master_skills_arsenal_ledger.py`
  - `apps_rg/fact_inventory/c03_graph_kpi_health.py`
  - `apps_rg/config/c03_graph_health_policy.v1.json`
- Projection/readiness, only when required by a proven contract:
  - `apps_rg/fact_inventory/augmented_skills_graph_sqlite.py`
  - `apps_rg/runtime/c0/c03_sqlite_graph_selection.py`
  - new app-owned skill-assertion document, exact-vector SQLite projection, qualification, and runtime
    candidate modules
  - new `tools/apps_rg/` offline builders/qualifiers
  - new `apps_rg/config/` embedding corpus/retrieval policy
- Tests and CI:
  - focused `tests/unit/apps_rg/fact_inventory/`, `tests/unit/apps_rg/runtime/c0/`, and
    `tests/unit/tools/apps_rg/` modules
  - `.github/workflows/c03-resume-graph-ratchet.yml` only for decisive candidate-head gates

W0 must replace this expected list with a certified ADG impact map before edits. Any transitive file enters
scope only with an exact consumer/contract reason.

### Authorized D0 dependency-lane edit scope

The user explicitly authorized this previously external lane with `Expand` on 2026-07-18. The repair is
limited to the exact run `07182026_1815` blockers and their direct regression tests.

ADG certification-repair branch, created fresh from current `origin/main`:

- `tools/generate/infra_wiring_views.py`
- `tools/generate/materialized_views/phase_a_path_authority.py`
- `tools/generate/generate_full_adg.py`
- `tools/generate/_gate_manifest.py`
- `tools/adg/run_full_adg_audit.py`
- `tools/runtime_adg/backfill_trace_index.py`
- `agentic_core/L6_system_learning/stores/index_file_lock.py`
- `agentic_core/L6_system_learning/stores/version_store.py`
- `agentic_core/L6_system_learning/runtime_adg/store.py`
- `tests/unit/tools/generate/test_infra_wiring_views.py`
- `tests/unit/tools/generate/test_materialized_views_phase_a.py`
- `tests/unit/tools/generate/test_generate_full_adg_failfast.py`
- `tests/unit/tools/generate/test_gate_manifest_validation_recording.py`
- `tests/unit/tools_adg/test_run_full_adg_audit.py`
- `tests/unit/tools/runtime_adg/test_backfill_trace_index.py`
- focused file-backed version/runtime-store concurrency tests under `tests/unit/agentic_core/`
- `.github/workflows/adg-hardening-contracts.yml`
- `artifacts/governance/core_addition_author_gate/apps-rg-c03-graph-health-embedding-closure-b8d4f1.json`
- `artifacts/governance/boundary_receipts/apps-rg-c03-runtime-index-synchronization-b8d4f1.json`
- `artifacts/governance/session_state.json`

Existing `codex-apps-rg-graphdb-hardening` branch after it consumes the repair merge:

- `apps_rg/fact_inventory/c03_graph_kpi_health.py`
- `tests/unit/ops_scripts/ci/test_infra_wiring_scan.py`

Every production change is test-first. The three declared `agentic_core` files are generic L6 storage
infrastructure only: they add no app identity, semantics, thresholds, or policy. No other application,
core surface, gate threshold, waiver, baseline, generated latest report, or warning-only write site enters D0.

### Read-only evidence scope

- Existing apps_rg fact-vector, BGE/Chroma, proof-pool/runtime-allowlist, allocation, calibration, and full-run
  surfaces.
- NEE assertion-document, retrieval, qualification, and KPI definitions as comparative evidence only.
- ADG audit and handoff artifacts from the producer root.

### Out of scope

- Other `agentic_core` changes, a new embedding model/provider, external embedding egress, or ANN/Chroma for the
  first 254-skill projection. Chroma is a later v2 option only if measured scale/latency requires it.
- Making generated SQLite or Chroma a second source of truth.
- Embedding every graph node/edge/path or duplicating existing fact embeddings.
- Fabricating sources, citations, metrics, dates, domain/epoch mappings, approvals, or SLA evidence.
- Treating optional explicit-endpoint closure as a reason to explode every deterministically registered
  derived endpoint into a canonical node. Registered endpoint closure remains the hard invariant.
- Broad remediation of the 130 steady-state warning write edges, including unrelated operational writes
  and scanner read/helper false positives. D0 closes only the two exact critical write sites, the one real
  direct-infrastructure import, manifest finalization, and runtime-proof indexing needed for certification.
- R1B whole-run semantic cache redesign or cache-policy changes.
- Gate/threshold weakening to achieve PASS.

---

## Dependency Wave D0 — ADG P0 and Certification Recovery

WAVE_ID: D0
WAVE_STATUS: IN_PROGRESS
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: D0

**Provenance**:

`DEGRADED_FALLBACK: reason=certified pointer absent; exact recovery diagnostics used the immutable read-only snapshot`

`ADG Provenance: backend=degraded_sqlite, snapshot=adg_indexed_07182026_1815.sqlite, sha256=a8e2bb8d082fc39bf34d0c9b93b3d1ed1bf3ed309826c78bbdcdc055a8b2eb5e`

**Observed blocker decomposition**:

- Gate `3_write_sovereignty`: 134 rows are 133 inventory edges plus one no-baseline sentinel. Only three
  edge rows at two distinct sites are critical; 21 sites are dual-relation duplicates. The 130 warnings are
  tracked debt and do not enter this repair.
- Gate `C1_uwg_bypass_pview`: the same three critical edge rows. The maintenance lock is a sanctioned
  adapter-local ephemeral write; the health receipt is explicit operator output. Neither is a database-state
  bypass, and neither app behavior should be rerouted through UWG.
- Gate `10_infra_wiring`: one real violation in `c03_graph_kpi_health.py`, which imports raw `sqlite3` and
  must use the canonical read-only graph adapter.
- Certification finalization: the audit lacked `--continue-on-p0`, so the P0 runner exited before normal
  manifest finalization. Emergency manifests contain null provenance and misreport an existing empty runtime
  view as absent.
- Runtime proof: 514 hash-valid shard files exist, but missing `_index.json` makes the version store expose
  zero snapshots. Recovery must reconstruct the index deterministically and fail closed on malformed or
  hash-divergent shards.
- Independent adversarial review found two duplicate trace IDs across 13 shards, including one valid current
  binding and one stale binding. Recovery must preserve a valid current binding and refuse ambiguous
  rebinding when no authoritative last-write identity survives; lexicographic shard order is not authority.
- Runtime-proof reads must use a read-only connection and convert locked, deleted, or unreadable snapshots
  into explicit non-certifying evidence. Certification must also verify the declared snapshot SHA-256.
- Missing-index publication must use writer-compatible mutual exclusion and compare-and-swap semantics so a
  concurrent live writer cannot be overwritten between recovery planning and atomic publication.
- Independent final-writer review proved that repair-only CAS cannot close this race: both file-backed stores
  cache complete maps and can replace a newly recovered index from stale state. D0 therefore adds one generic,
  shared, bounded cross-process index lock and reload/merge-on-write behavior to both L6 writers; repair and
  live writers use the same lock, no canonical path is renamed away, and crash recovery never depends on a
  private backfill-only lock.

**Phases**:

- **D0.1** — Test-first graph-view classification repair | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **D0.2** — Test-first manifest/runtime-index recovery | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **D0.3** — Repair branch verification, commit, PR/merge, and feature-branch consumption | PHASE_STATUS: IN_PROGRESS | PHASE_COMPLETE: NO
- **D0.4** — Test-first apps_rg adapter repair and exact-SHA certification | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Execution**:

1. Create `codex-adg-certification-repair` from current `origin/main`; do not reuse or cherry-pick stale
   `codex-adg-p0-blocker-burndown@9562e193`, which is 42 commits behind, misses both critical sites, lacks
   tests, and carries obsolete generated reports/baselines.
2. Add failing fixture tests proving exact site-scoped exclusions, adapter enrollment, counterexample
   preservation, dual-edge behavior, complete fail-fast manifests, and deterministic missing-index recovery.
3. Implement the minimal producer/runtime repairs in the declared D0 infrastructure/CI files and three generic
   L6 storage files covered by the CoreAdditionAuthorGateReceipt. Preserve the
   no-baseline fail-closed contract and do not weaken warning inventory or P0 thresholds.
4. Run focused tests, graph-layer/security/contract gates, and inspect the diff. Commit and merge the repair
   branch into local/main and `origin/main` with exact ancestry proof.
5. Merge updated main into `codex-apps-rg-graphdb-hardening`. Add the failing infra-wiring regression, replace
   the direct SQLite connection with `open_graph_sqlite(..., read_only=True)`, and preserve read purity.
6. Rebuild the missing runtime version index with the repaired hash-verifying backfill. Run the full audit
   with `--continue-on-p0`; only require runtime proof after the recovered index reports attested rows.
7. Require Gate 3 nonblocking with zero critical/new rows, C1 zero, infra wiring zero, complete manifests,
   runtime proof attested, certification PASS, and a digest-verified certified pointer before returning to W0.

**Acceptance**:

- Exact counterexamples remain blocked; no broad filename, layer, app, symbol, or write-family exemption exists.
- Gate 3 has zero critical and zero new write paths; the 130 unrelated warning rows remain visible.
- C1 and the authoritative infra-wiring file scan each return zero for the exact feature SHA.
- P0 early exit still records non-null snapshot path/digest, commit SHA, repo-state hash, registry count,
  accurate runtime-view status, exit code, and failed-gate evidence.
- Missing runtime `_index.json` is reconstructed only from hash-valid shard metadata using an atomic,
  deterministic, fail-closed write; malformed or divergent shards, ambiguous trace bindings, or concurrent
  index/trace-index drift produce no overwrite.
- A preinitialized live version or trace writer cannot erase recovered/prior bindings: all durable index writes
  reload and merge under the same bounded cross-process lock, and repair never creates a missing canonical-path
  window. Lock timeout, crash release, and competing-writer negative controls pass.
- Runtime-proof inspection is read-only and exception-safe for locked/deleted snapshots, and certification
  rejects a missing, malformed, or mismatched manifest `snapshot_sha256`.
- The health-receipt exemption remains one-call-site authority: a second same-file `output.write_text` site
  fails closed instead of inheriting the exemption.
- The ADG hardening workflow directly selects every new D0 regression file/class, including runtime-index,
  manifest-finalization, runtime-proof-read, digest, and unique-site counterexamples.
- Full certification produces a complete immutable handoff and certified pointer. Any failure stops D0
  without changing app-source authority, KPI thresholds, baselines, or release claims.

---

## Wave 0 — Certified Evidence and Exact Recovery Registers

WAVE_ID: W0
WAVE_STATUS: IN_PROGRESS
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: A

**Phases**:
- **W0.1** — Restore certified ADG pointer/transport | ~8K tokens | PHASE_STATUS: IN_PROGRESS | PHASE_COMPLETE: NO
- **W0.2** — Pin branch, graph, policy, SQLite, and KPI cohorts | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W0.3** — Emit exact gap and dependency registers | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Execution**:

1. Validate the producer-root immutable handoff, rerun the full certification audit in its governed lane,
   restore the certified pointer, and prove `adg_health` plus required materializations are green.
2. Fetch without merging; prove the feature branch remains based on the intended main and pin every input
   digest used by the health receipt.
3. Run the pure KPI builder with an explicit output path and emit four non-overlapping views:
   source-reference gaps, claim-evidence gaps, taxonomy/node gaps, and operational-evidence gaps.
4. For every gap record, capture canonical ID, node/row type, current evidence, required authority class,
   source candidate if any, owner class, status, and blocking reason. Capture set intersections.
5. Re-run certified ADG nodes, fan-in/out, P-views, semantic writes/reads, and test-selection queries for the
   proposed edit surface. Update scope before implementation.

**Acceptance**:

- Certified ADG pointer exists, digest verifies, required materializations pass, and MCP results name the
  certified snapshot.
- Gap-register denominators reproduce 179/254 claim evidence, 117/201 required sources, 250/254 skill
  nodes, 235/254 domain/epoch fields, 217/254 domain edges, 198/254 epoch edges, nine factless skills,
  66 incomplete graph bindings, and 25/32 unclassified edge types from the candidate commit.
- Every gap has an exact locator and disposition; no heuristic source recovery is marked approved.
- Dependency handoff is downstream-ready; otherwise the plan stops at W0.

---

## Wave 1 — Source Authority and Canonical Assertion Closure

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: B

**Phases**:
- **W1.1** — KPI/validator measurement closure | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Reviewed source recovery decisions | ~16K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** — Skill node/domain/epoch closure | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.4** — Claim-evidence/source-ref closure | ~16K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Execution**:

1. First version the KPI contract so it measures row-field and graph-edge domain/epoch coverage separately;
   resolves typed fact/source references; reports exact numerator, denominator, missing IDs, and authority
   class; and classifies all observed edge types. Add adversarial fixtures before changing governed data.
2. Present source candidates in bounded human-review batches. Bind each approved decision to exact source
   bytes/hash, locator, reviewer, decision time, affected IDs, and allowed claim scope.
3. Add the four missing skill nodes only by deterministic projection from their existing canonical skill
   rows. Resolve identity/type/signature parity before adding edges.
4. Resolve row-field gaps and the larger graph-edge gaps independently: current baselines are 235/254 for
   both fields, 217/254 domain edges, and 198/254 epoch edges. Conflicts or ambiguity stay blocked; no
   majority/inference shortcut.
5. For claim-bearing skill rows, require canonical fact IDs plus source lineage. A snippet without a graph
   fact remains context, not proof. Rows that cannot be supported become explicitly non-retrieval-eligible
   or inactive through reviewed policy; they are not silently counted complete.
6. Reconcile all existing declared fact links into graph bindings, including the nine factless and 66
   incomplete skill cohorts, without manufacturing facts. For non-claim taxonomy/policy/derived nodes in
   the 84-row source cohort, use the correct authority class
   rather than forcing resume evidence onto internal structure.
7. Classify 32/32 observed edge types and explicitly adjudicate the three singleton types. Preserve the
   registered-derived-endpoint policy unless W0 evidence proves explicit-node closure is required.

**Acceptance**:

- Every semantic write has a digest-bound approval and recovery path.
- Skill-row/node parity is 254/254; domain and epoch row fields and graph edges are each 254/254.
- Claim-evidence completeness and required source-ref completeness are 100% for the policy-required cohort,
  or the plan remains blocked with explicit reviewed exclusions and an unchanged denominator contract.
- Every existing declared fact link is represented or has a reviewed exclusion; all observed edge types have
  canonical semantics/signatures; zero material conflicts, identity collisions, unsupported source
  promotion, or fabricated evidence.

---

## Wave 2 — Canonical and SQLite Graph-Data Certification

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W2.1** — Canonical closed-world validation | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — SQLite v3 rebuild and read-purity proof | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** — Graph-data KPI certification | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Execution**:

1. Establish one canonical edge-semantics registry and validate source/destination node-type signatures,
   typed reference resolution, singleton dispositions, and lossless node types in both canonical JSON and
   SQLite. Preserve `metric` and `metric_bucket` rather than silently collapsing both to `metric_outcome`.
2. Recompute all canonical node/edge/signature/metadata/heterogeneity receipts from source; do not edit stored
   receipts independently.
3. Unify DDL and admission manifests across all eight relevant tables and all 13 expected FK signatures.
   Choose one path-index capability/version: base materialization and explicit applicator must produce the
   same advertised depth/feature receipt.
4. Rebuild the generated SQLite projection through the explicit applicator into a temporary path, validate
   it, then use the existing maintenance-lock/digest-CAS replacement contract.
5. Prove canonical/SQLite semantic digest parity, counts, typed signatures, FK coverage/integrity, reverse multiset parity,
   path continuity, sibling symmetry, neighborhood distance/path coherence, and read purity.
6. Remove verify/close/reopen TOCTOU: verification and retrieval must bind to one opened read-only snapshot.
   Run negative controls for wrong-type edges, null/partial schema, same-count semantic tamper, stale metadata,
   and reopen races; each must fail closed.
7. Emit a candidate-SHA-bound graph-health receipt.

**Acceptance**:

- `graph_data_readiness=PASS` on all required metrics.
- Orphan, duplicate identity/edge, FK, reverse, path, sibling, neighborhood, and registered endpoint defects
  remain zero.
- All 32 observed edge types are classified and type-valid; canonical node types and the selected path
  capability are lossless/equivalent across base materialization and applicator.
- KPI and runtime reads bind validation and selection to one snapshot, do not change SQLite bytes or sidecar
  state, and never materialize/repair.

---

## Wave 3 — Operational Control-Plane Evidence

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: D

**Phases**:
- **W3.1** — Producer/cohort evidence schema | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Seven required operational measurements | ~14K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.3** — Rollup, purity, and adversarial verification | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Execution**:

1. Define a strict operational-evidence envelope whose digest is recomputed from named producer artifacts,
   not accepted from a caller-provided 64-hex string or status label.
2. Bind `decision_safe_regression` to a frozen approved retrieval/product test set and exact before/after
   results.
3. Bind source currentness/freshness to reviewed source records, locator timestamps, and policy windows.
4. Bind HITL coverage to the W1 approval ledger, write-audit coverage to actual governed write receipts,
   and P0/P1 SLA metrics to the authoritative issue/gate timestamps and ownership records.
5. Prove wrong digest, stale cohort, missing producer, partial coverage, arbitrary `VERIFIED`, and replayed
   evidence all yield `UNKNOWN`/BLOCK rather than PASS.

**Acceptance**:

- All seven operational metrics are measured from available authoritative producers and pass.
- `control_plane_status=PASS` and overall health can reach PASS only when W2 also passes.
- Unsupported dimensions remain `UNKNOWN`; no synthetic operational packet is accepted.

---

## Wave 4 — Embedding Necessity and Model Qualification

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: E

**Phases**:
- **W4.1** — Frozen query/qrel and baseline contract | ~14K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** — Four-arm shadow benchmark | ~16K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.3** — Promotion/no-promotion decision | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Execution**:

1. Freeze development and holdout query sets, route/lane labels, qrels, reviewer/adjudication receipts,
   graph/corpus/policy digests, and error taxonomy before model execution.
2. Use local, artifact-pinned BGE-M3 only. Run A-D arms with identical query and graph cohorts.
3. Report per-lane and aggregate Recall@10, graded nDCG@10, proof-candidate precision, authority/path/
   entailment/metric-binding accuracy, ECE, MRR, Spearman, abstention/unsupported-query behavior, authority
   leakage, latency, storage, and every miss classified as source/qrel, route/lane, candidate generation,
   fusion/ranking, or graph rehydration.
4. Apply the frozen thresholds in this plan without tuning on holdout results.

**Acceptance**:

- A content-addressed decision receipt says exactly `QUALIFIED_GO` or `NO_EMBEDDING_PROMOTION`.
- W5 is authorized only by `QUALIFIED_GO`; no-go preserves the current graph/fact-vector architecture.
- No shadow result changes production selection, evidence, graph state, or model settings.

---

## Wave 5 — Conditional Skill-Assertion Embedding Projection

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: F

**Phases**:
- **W5.1** — Deterministic assertion-document corpus | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.2** — Immutable exact-vector SQLite generation | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.3** — Candidate-only runtime adapter | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Execution**:

1. Implement the pure `C03SkillAssertionDocumentV1` renderer and reject missing identity, claim, lifecycle,
   evidence, source, classification/policy, or retrieval state.
2. Render the deterministic semantic card separately from authority/lineage metadata. Bind both to the
   assertion-document hash so a change to either invalidates the vector without encoding authority as
   similarity text.
3. Build `graph_skill_embeddings.<projection_digest>.sqlite` offline from one ordered graph-v3 read
   transaction. Reject missing/zero/non-finite/non-normalized/wrong-dimension vectors; validate hashes,
   exact row count, unique IDs, blob lengths, norms, and ordered matrix digest; then recheck source digests
   before atomically advancing `active.json`.
4. Runtime resolves and pins the current generation read-only, computes allowed skill IDs from the same
   current graph first, ranks only those IDs with exact normalized dot product, rehydrates the exact
   assertion/document hash, and uses canonical SQLite for all authority, path, evidence, policy, and budget
   decisions.
5. Add source-drift-during-build, stale pointer/generation, partial generation, duplicate skill, wrong model/
   fingerprint/endian/dimension, NaN/zero vector, candidate leakage, corpus truncation, concurrent pointer
   replacement, unsafe cleanup, read mutation, and unavailable-projection negative controls.

**Acceptance**:

- Exactly one active vector exists for every production-eligible skill assertion and no other graph unit.
- Corpus count, ordered IDs, assertion hashes, ledger digest, model revision/digest, dimension, and generation
  digest all reconcile.
- Vector results can narrow candidate discovery but cannot add evidence, authorize a claim, or skip exact
  graph traversal.
- Published generations are immutable/read-only, graph v3 remains byte-pure, and readers survive pointer
  replacement without opening a mixed generation.
- Removing, disabling, or invalidating the optional vector route preserves the exact graph result contract.

---

## Wave 6 — Full Product Certification and Publication

WAVE_ID: W6
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: G

**Phases**:
- **W6.1** — Candidate-head engineering gates | ~12K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W6.2** — User-input-owned 11/11 product proof | ~20K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W6.3** — Governed PR merge and ancestry closeout | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Execution**:

1. Pin the candidate SHA before and after the run and require strict readiness:
   `python scripts/governance/codex_readiness.py --json --require-clean-worktree --fail-duplicate-processes`.
2. Explicitly materialize the remediated graph projection and require PASS from
   `validate_graph_sqlite_path_index.py`, `validate_c03_graph_hardening.py`, fact-vector readiness, and the
   Windows path-budget check. Then run the exact C0.3 strict/baseline pytest cohorts and
   `python -m apps_rg.evals.c03_ci_ratchet` against candidate/base SHAs.
3. Before launching a product run, set `APPS_RG_RESUME_GRAPH_W6_FAIL_CLOSED=1`, bind a sanitized official
   W6 receipt through `APPS_RG_RESUME_GRAPH_W6_ARTIFACT`, and require
   `python ops_scripts/ci/check_apps_rg_resume_graph_w6.py` to pass. If no official receipt exists, produce
   it through the controlled two-qualified-reviewer plus adjudication workflow; never fabricate a trusted
   digest or treat `UNKNOWN` as authorization.
4. Run the deterministic apps_research/apps_rg contract-freeze, handoff, full-chain, and structural/evidence
   traceability gates. Activate live canonical graph/KPI CI blocking only after the governed W1 data closure
   is merged into the candidate; upload the exact health and run receipts.
5. Freeze the fresh-run target. If W0 pins the existing Anthropic Partnership baseline, run exactly
   `python scripts/apps_rg/run_anthropic_partnership_e2e.py --output-root artifacts/apps_rg/runs/on_demand_anthropic_partnership_fresh_s2e --baseline-ref apps_rg/config/e2e_baselines/anthropic_partnership.v1.json`.
   For another target, request target company, role/level, JD, and briefing mode/path once and use the
   governed fresh `python -m apps_rg` launch contract. Never infer user inputs from memory.
6. Require one unambiguous returned run directory and validate `e2e_stage_ledger.json`,
   `01_BCG_executive_output.md`, `02_output_bisect.md`, `02_section_lane_summary_table.md`,
   `03_L7_audit_ability_output.md`, and `APPS_RG_MANDATORY_RUN_OUTPUT.json`. Do not backfill after exit.
7. Require all eleven claim-bearing lanes to be `REAL_LLM` and `X3_ALLOW`, every provider/judge/X2/X3
   row to be present, the DOCX to open and contain every required section, and allocation/claim/graph digests
   to reconcile. Render the run with `python tools/apps_rg/render_run_summary.py <run_dir>` and inspect it.
8. Verify the candidate-SHA-bound run receipt with `verify_codex_run_receipt.py`. Require exact whole-run
   `X3D_ALLOW_FINISH`, `product_authorized=true`, `pipeline_complete=true`, official W6 PASS,
   `release_pass=true`, and `FINAL_RESUME_OUTPUT.status=PASS`; no observability repair is closeout evidence.
9. Update PR #565 with exact results, wait for exact-head checks/review, merge with merge or rebase (never
   squash), run Codex publication closeout, and prove the feature tip is ancestor-contained in `origin/main`.

**Acceptance**:

- `control_plane_status=PASS`, `graph_data_readiness=PASS`, and `overall_status=PASS` are bound to the
  candidate SHA and product run.
- Full apps_rg product completion gate passes: 11/11, complete mandatory artifacts, valid inspected DOCX,
  consistent run ID/SHA, official W6 PASS, whole-resume `release_pass=true`, and no skipped mandatory lane.
- PR is merged, local `main` equals `origin/main`, and the feature tip is an ancestor of `origin/main`.

Full C0.3 W9 promotion is a separate post-closeout decision: six blinded pairs, twelve qualified coach
reviews, six adjudications, official W6 PASS, whole-resume release PASS, and explicit generation
authorization. W6 product certification must not imply that W9 evidence exists.

---

## Verification Matrix

| Surface | Success | Edge/failure controls | Required evidence |
|---|---|---|---|
| Source recovery | Approved exact source closes intended IDs | missing/conflicting/stale source remains blocked | approval ledger + source bytes/hash + locator |
| Canonical graph | all required field/edge/source KPIs pass | duplicate, unknown type/signature, unresolved typed reference, unsupported endpoint fails | canonical validator + KPI receipt |
| SQLite projection | lossless type/semantic/count/FK/path parity in one snapshot | wrong-type edge, same-count tamper, reopen race, partial admission, WAL state fails | applicator/validator receipts + byte-purity proof |
| Operational evidence | seven measurements are producer-bound | arbitrary hash/status, replay, partial cohort fails | operational envelope + producer digests |
| Assertion documents | one deterministic doc per eligible skill | missing evidence/source/ACL/lifecycle or multi-claim row rejected | corpus manifest + document hashes |
| Embedding qualification | thresholds pass with incremental value | no lift, leakage, regression, or excessive latency yields no-go | frozen qrels + four-arm decision receipt |
| Vector projection | one active exact-vector SQLite row per eligible assertion | source drift, stale pointer, partial/duplicate/wrong fingerprint/endian/dimension fails closed | generation metadata/pointer + read-only readiness receipt |
| Runtime retrieval | candidates rehydrate and traverse exact graph | vector cannot mint evidence or bypass authority | selection receipt + negative tests |
| Product | official W6 PASS, 11/11 REAL_LLM/X3_ALLOW, X3D_ALLOW_FINISH, release PASS, valid DOCX | UNKNOWN W6 or any missing lane/artifact/judge/gate blocks | W6 receipt + mandatory run output + renderer + DOCX inspection |
| Publication | exact ancestry and SHA convergence | draft/red/stale-head/squash/unique branch commit blocks | PR state + closeout JSON + ancestry checks |

---

## Stop Conditions and Recovery

Stop without policy weakening when:

- certified ADG health/pointer or downstream-ready dependency handoff is absent;
- source authority is missing, conflicting, stale, or not reviewed;
- semantic edits would exceed approved source scope or touch `agentic_core`;
- graph-data or control-plane health remains `NOT_READY`, `UNKNOWN`, `FAIL`, or `BLOCK`;
- W4 does not prove incremental embedding value;
- vector generation requires network egress, a new model, ANN/Chroma for v1, or runtime writes;
- a vector cannot rehydrate to the current canonical assertion/document hash;
- exact product inputs are missing or any mandatory apps_rg lane/artifact is absent;
- relevant tests, CI, security, mutation, review, or publication checks are not green.

Recovery boundaries:

- Each semantic source batch is a separate commit with an approval-bound inverse/forward-repair manifest.
- SQLite rebuilds use the existing temporary-build, validation, maintenance-lock, and digest-CAS contract.
- Optional exact-vector SQLite generations are immutable/content-addressed; rollback atomically repoints to
  the prior qualified generation or disables the optional route. Runtime never repairs them and cleanup
  observes an open-reader grace period.
- `main` remains untouched until W6. A failed wave stays on the feature branch with receipts preserved.

---

## Definition of Done

| # | Definition of Done | Verification | Status |
|---|---|---|---|
| 1 | Certified ADG pointer, digest, materializations, P-views, and active transport are green | `adg_health`, status, P-view, fan-in/out, semantic-edge receipts | TODO |
| 2 | Versioned KPI contracts expose field and edge denominators, typed locators, and every observed edge semantic before governed data changes | adversarial KPI fixtures + exact gap register | TODO |
| 3 | Required graph source, claim evidence, skill-node, domain-field/edge, and epoch-field/edge cohorts reach frozen targets without fabrication | candidate-bound `c03_graph_kpi_health` receipt | TODO |
| 4 | Canonical/SQLite types, edge signatures, admission manifests, and path capability remain lossless/zero-defect; reads verify and select from one pure snapshot | validators, tamper/race negatives, file/sidecar hashes | TODO |
| 5 | All seven operational dimensions are measured from real producer artifacts and `control_plane_status=PASS` | operational evidence envelope + adversarial tests | TODO |
| 6 | Embedding necessity is closed by `QUALIFIED_GO` or `NO_EMBEDDING_PROMOTION`; no production vector surface exists without GO | frozen four-arm decision receipt | TODO |
| 7 | If GO, exactly one immutable exact-vector SQLite row exists per eligible `C03SkillAssertionDocumentV1`, with zero stale/leaked/unauthorized rows | corpus/generation metadata, readiness, mutation and leakage tests | TODO |
| 8 | Candidate retrieval cannot add evidence or bypass canonical graph authority; disabling the optional vector route preserves the exact contract | runtime integration and negative-control tests | TODO |
| 9 | Focused, broad apps_rg, contract, boundary, security, mutation, static, live KPI, and exact-head CI checks pass with an exact-SHA clean run receipt | command receipts, validated run receipt, and GitHub checks | TODO |
| 10 | Official W6 is PASS and a fresh user-input-owned run completes all eleven REAL_LLM/X3_ALLOW lanes, X3D_ALLOW_FINISH, release PASS, mandatory artifacts, and an inspected non-empty DOCX | W6 receipt, mandatory run output, renderer, DOCX inspection | TODO |
| 11 | PR #565 is merged without squash and local/main/origin converge with exact branch-tip ancestry | PR/merge state, closeout JSON, SHA and merge-base checks | TODO |

---

## Supersedes

| Predecessor slug | Reason |
|---|---|
| _None — net-new continuation plan._ | Complements, but does not replace, `apps-rg-c03-resume-graph-hardening-9f3c2a` and the branch receipt. |

---

## Approval Prompt

After reviewing this plan, approve execution with:

> Execute `plans/apps-rg-c03-graph-health-embedding-closure-b8d4f1.md` on the existing
> `codex-apps-rg-graphdb-hardening` branch. Start at W0 and stop at every `AUTHORIZATION_STATUS: REQUIRED`
> checkpoint unless the approval explicitly covers the next bounded wave. Do not create production graph
> embeddings unless W4 produces `QUALIFIED_GO`; if it does, embed only `C03SkillAssertionDocumentV1` units.
