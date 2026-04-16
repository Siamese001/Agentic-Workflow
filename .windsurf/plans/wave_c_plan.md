# Wave C Implementation Plan

**Version**: 1.0 · **Status**: ACTIVE · **Date**: 2026-04-16  
**Author**: Agentic-Workflow engineering  
**Binding contract**: `docs/requirements/wave_c_handoff_contract.md` v2.0  
**Entry precondition**: Wave B COMPLETE — all 11 freeze gates PASS (see `wave_b_b7_freeze_gates.md`)  
**Plan tier**: T2/T3 — multi-phase, cross-layer  

---

## Wave Summary

| Wave | Phase IDs | Focus | Status |
|------|-----------|-------|--------|
| **C1** | C1.1–C1.3 | Current-state inventory and repo gap map | TODO |
| **C2** | C2.1–C2.2 | repo_evidence Lane C additions for TS-20 and F25-int | TODO |
| **C3** | C3.1–C3.2 | Optional F02 advisory ext_authority source + full G9 re-run | TODO |
| **C4** | C4.1–C4.2 | E2E validation and non-regression proof | TODO |

**Token budget**: C1 low · C2 medium · C3 medium · C4 high  
**Critical path**: C1 → C2 → C4 (C3 is optional/parallel with C2)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files/modules) | Pain Points | Est. Tokens | Status |
|----------|-------|-----------------------|-------------|-------------|--------|
| C1.1 | Repo inspection — L0–L6 modules | `agentic_core/`, `apps_*/`, `tools/` | May surface undocumented architecture gaps | LOW | TODO |
| C1.2 | repo_evidence gap map — TS-20 and F25-int queries | `tools/eval/`, `data/cache/chromadb/` | ChromaDB query; zombie-process risk | LOW | TODO |
| C1.3 | Current-state gap map document | `docs/reports/wave_c_gap_map.md` | None | LOW | TODO |
| C2.1 | TS-20 normative requirements spec — Lane C doc | `docs/requirements/`, `tools/generate/ingestion/ingest_repo_evidence.py` | Must satisfy G4/G5/G6; no https:// URL | MEDIUM | TODO |
| C2.2 | F25-int healing dispatch routing — Lane C doc | `docs/architecture/` (new), `tools/generate/ingestion/ingest_repo_evidence.py` | Internal arch only; no ext_authority addition | MEDIUM | TODO |
| C3.1 | F02 advisory — evaluate source candidate (optional) | `tools/generate/ingestion/ingest_ext_authority.py` | Advisory only; not a hard gate; must not break G9 | MEDIUM | TODO |
| C3.2 | G9 re-run after any C3.1 addition | `tools/eval/audit_wave_b_target_state.py` | G9 must stay ≥75% | LOW | TODO |
| C4.1 | All 11 freeze gate non-regression run | `tools/eval/`, `docs/reports/wave_c_freeze_gates.md` | Must reproduce B7 baseline before Wave C additions | HIGH | TODO |
| C4.2 | Wave C closeout report | `docs/reports/wave_c_closeout.md` | Final verdict only after all gates pass | MEDIUM | TODO |

---

## 1. Wave C Objective

Produce a documented, gate-proven current-state → target-state gap map for the live retrieval system, add the two permitted `repo_evidence` Lane C documents (TS-20, F25-int), optionally consider the one advisory ext_authority source (F02), and prove no Wave B freeze gate has regressed.

**Wave C does NOT begin any retrieval path redesign, router changes, topology changes, or implementation of new retrieval strategies.** Those are Wave D scope.

---

## 2. Frozen Constraints Inherited from Wave B

All of the following are **non-negotiable**. No exception without a new HITL decision and documented blocker.

### 2a. Topology (DO NOT CHANGE)

| Collection | Lanes | Normative use |
|------------|-------|---------------|
| `ext_authority` | A, B | Target-state — `invalid_for_normative_use=False` |
| `repo_evidence` | C, D | Current-state — `invalid_for_normative_use=True` |
| `ext_raw` | E | Never normative — `invalid_for_normative_use=True` |

No collection renames, splits, merges, or deletions.

### 2b. Lane separation rule

> **ext_authority defines target state.**  
> **repo_evidence defines current state.**  
> **No cross-lane gap filling.**

Do not fill an external target-state gap with `repo_evidence` chunks. Do not fill an internal architecture gap with `ext_authority` chunks.

### 2c. Frozen routing (query_router.py — DO NOT MODIFY)

```
policy          → ext_authority
best_practice   → ext_authority
tool_contracts  → ext_authority
architecture    → repo_evidence (prefilter: source_band=repo_canonical)
code            → code_chunks
```

### 2d. Frozen normative filter (evidence_shaper.py — DO NOT MODIFY)

`allowed_collections` default = `ext_authority`. Do not change.

### 2e. Frozen metadata contract (14 required fields — DO NOT CHANGE)

`source_collection`, `source_band`, `authority_tier`, `normative_scope`, `invalid_for_normative_use`, `source_type`, `topic_bucket`, `doc_family`, `source_url`, `heading_path`, `collapse_group`, `title`, `chunk_index`, `canonical_digest`

### 2f. F25 adjudication (FINAL — DO NOT REOPEN)

- **F25-ext**: ADEQUATE advisory — grounded by running_agents.md HITL/durable-execution (rank-3, dist=0.519). Do not add more sources.
- **F25-int**: INTERNAL — project-specific vocabulary. Route to `repo_evidence` Lane C. No ext_authority addition permitted.

### 2g. Closed B7 topics (DO NOT ADD SOURCES)

TS-03, TS-04, TS-07, TS-09, TS-19 are ADEQUATE at B7. Adding further ext_authority sources for these is forbidden.

---

## 3. Allowed Wave C Workstreams

### Workstream A — Current-State Inventory (C1)

Inspect live repo modules and `repo_evidence` collection to produce a gap map documenting where the current codebase diverges from the B7 external target-state baseline.

**Allowed actions**:
- Read `agentic_core/`, `apps_*/`, `tools/` source files (no edits)
- Query `repo_evidence` ChromaDB collection for TS-20 and F25-int topics
- Query `ext_authority` ChromaDB collection for gap confirmation (read-only)
- Produce `docs/reports/wave_c_gap_map.md`

**Forbidden actions**: No edits, no ingestion, no topology change.

### Workstream B — repo_evidence Lane C Documentation (C2)

Add two internal architecture documents to `repo_evidence` Lane C:

| Document | `source_band` | `invalid_for_normative_use` | Content |
|----------|--------------|----------------------------|---------|
| Normative requirements spec (TS-20) | `repo_canonical` | True | Internal policy document defining system requirements |
| F25-int healing dispatch routing architecture | `repo_canonical` | True | Internal architecture decision for confidence-scored tiered healing |

**Allowed actions**:
- Author the two documents in `docs/requirements/` or `docs/architecture/`
- Add them to `ingest_repo_evidence.py` source list
- Rebuild `repo_evidence` collection (repo_evidence only — NOT ext_authority or ext_raw)
- Verify G4/G5/G6 pass after rebuild

**Forbidden actions**:
- No `https://` URL on either document
- No addition to `ext_authority`
- No new mandatory metadata fields beyond the 14 required

### Workstream C — Optional F02 Advisory Source (C3)

Evaluate and optionally add one ext_authority source for F02 (ingress auth/quota/schema). This is advisory-only — not a hard gate.

**Allowed actions**:
- Identify one candidate source (e.g. OpenAI platform auth docs, agentic ingress patterns cookbook)
- Validate source returns dist@1 < 0.45 for F02 gap query (minimum evidence standard per §8 handoff contract)
- If validated: add to `ingest_ext_authority.py` source list, rebuild `ext_authority`
- Re-run G9 audit after rebuild; confirm G9 ≥ 75%

**Gate condition**: If F02 candidate does NOT return dist@1 < 0.45, do not add source. Mark C3 as skipped, proceed to C4.

**Forbidden actions**:
- Do not frame this source as closing F25-int or any retired query
- Do not add sources for TS-03, TS-04, TS-07, TS-09, TS-19 (closed at B7)

### Workstream D — E2E Validation (C4)

Run all 11 Wave B freeze gates against the post-Wave-C collection state and produce the Wave C closeout report.

**Required outputs**:
- `docs/reports/wave_c_freeze_gates.md` — all 11 gates must PASS
- `docs/reports/wave_c_closeout.md` — final verdict

---

## 4. Phased Execution Order

### Phase C1 — Current-State Inventory

**Objective**: Map the gap between current codebase and B7 ext_authority baseline.

**Steps**:

1. **C1.1** Inspect key modules against B7 target-state topics:
   - Files to inspect first (priority order):
     - `agentic_core/L0_routing/` — routing, caching, evidence shaping
     - `agentic_core/L1_reasoning/` — planning, abstain, decomposition
     - `agentic_core/L3_orchestration/` — query router, evidence shaper
     - `agentic_core/L4_state/cache/` — exact cache, semantic cache (F08/F09 implementation status)
     - `agentic_core/L5_policy/` — governance, safety guardrails
     - `tools/eval/` — retrieval eval harness
   - For each module: note whether implementation aligns with the ADEQUATE ext_authority topic

2. **C1.2** Query `repo_evidence` for TS-20 and F25-int topics:
   - Query: `"normative requirements specification for the agentic routing system"`
   - Query: `"confidence-scored tiered healing dispatch routing tiers local rules model retry human escalation"`
   - Expected result: dist@1 > 0.50 (gap confirmed) — these are the C2 targets

3. **C1.3** Produce `docs/reports/wave_c_gap_map.md`:
   - One row per B7 grounded topic
   - Columns: topic | ext_authority grade | current-state impl status | gap type | Wave C action
   - Gap types: NONE (aligned), IMPL_GAP (code not yet aligned), DOC_GAP (undocumented), ADVISORY (non-blocking)

**Stop condition**: Gap map complete. No edits to production code.

---

### Phase C2 — repo_evidence Lane C Additions

**Objective**: Add two internal documents to `repo_evidence` Lane C.

**Prerequisite**: C1.3 gap map confirms both TS-20 and F25-int as MISSING in `repo_evidence`.

**Steps**:

1. **C2.1** Draft and add TS-20 normative requirements spec:
   - File path: `docs/requirements/normative_requirements_spec.md` (or equivalent)
   - Content: internal policy definitions, system-level requirements, scope boundaries for the agentic routing system
   - Metadata: `source_band=repo_canonical`, `invalid_for_normative_use=True`, `source_url=docs/requirements/normative_requirements_spec.md` (repo-relative, no https://)
   - Add to `ingest_repo_evidence.py` source list
   - Verify: query `repo_evidence` after rebuild; TS-20 query must return dist@1 < 0.50

2. **C2.2** Draft and add F25-int architecture decision record:
   - File path: `docs/architecture/healing_dispatch_routing_adr.md` (or equivalent)
   - Content: documents the project-specific confidence-scored tiered healing architecture — tier definitions, local rule fallback, model retry escalation, human HITL escalation thresholds
   - Metadata: `source_band=repo_canonical`, `invalid_for_normative_use=True`, `source_url=docs/architecture/healing_dispatch_routing_adr.md` (repo-relative)
   - Add to `ingest_repo_evidence.py` source list
   - Verify: query `repo_evidence` after rebuild; F25-int query must return dist@1 < 0.50

**Rebuild scope**: `repo_evidence` collection ONLY. `ext_authority` and `ext_raw` must not be touched.

**Stop condition**: Both documents added, `repo_evidence` rebuilt, G4/G5/G6 verified PASS.

---

### Phase C3 — Optional F02 Advisory (may run in parallel with C2)

**Objective**: Evaluate one ext_authority source for F02 ingress auth/quota/schema. Add only if it meets the minimum evidence standard.

**Gate condition**: Source must return dist@1 < 0.45 for F02 gap query. If not, skip C3 entirely.

**Steps**:

1. **C3.1** Evaluate F02 candidate source (e.g. `https://platform.openai.com/docs/api-reference/authentication`):
   - Dry-run: fetch and embed a sample chunk
   - Query: `"How do agentic systems implement ingress request authentication, quota enforcement, and schema normalization?"`
   - If dist@1 < 0.45: proceed to add source
   - If dist@1 ≥ 0.45: skip C3 entirely; note advisory gap is unresolved

2. **C3.2** If C3.1 passes: add source to `ingest_ext_authority.py`, rebuild `ext_authority`, re-run G9:
   - G9 must remain ≥ 75% (currently ≥ 95% — ample headroom)
   - G1/G2/G3 must pass on all chunks including new addition

**Stop condition**: Either source added and G1/G2/G3/G9 confirmed PASS, or C3 skipped (F02 remains advisory).

---

### Phase C4 — E2E Validation and Non-Regression Proof

**Objective**: Prove all 11 Wave B freeze gates still pass against the final Wave C collection state.

**Steps**:

1. **C4.1** Run full freeze gate suite against post-Wave-C collections:
   - G1–G3: ext_authority metadata and normative flags
   - G4–G6: repo_evidence metadata and normative flags
   - G7–G8: ext_raw metadata and URL dedup
   - G9: retrieval strength ≥ 75% (22-query denominator; F25 retired)
   - G10: 0 non-ext_authority chunks in target-state audit
   - G11: 0 ext_raw chunks in target-state audit
   - Produce `docs/reports/wave_c_freeze_gates.md`

2. **C4.2** Run gap map closure check:
   - Re-query `repo_evidence` for TS-20 and F25-int: both must return dist@1 < 0.50
   - Confirm no new gap families introduced by Wave C actions

3. **C4.3** Produce `docs/reports/wave_c_closeout.md`:
   - Gate table (all 11 gates)
   - Gap map delta (C1 vs C4 state)
   - Permitted workstreams completed
   - Wave C completion verdict

**Stop condition**: All 11 gates PASS. Wave C closeout report written. No Wave D implementation started.

---

## 5. Files to Inspect First (C1 Priority Order)

| Priority | Path | Why |
|----------|------|-----|
| 1 | `agentic_core/L0_routing/` | R1A/R1B cache routing (F08/F09), R4 external action, R5 fallback |
| 2 | `agentic_core/L3_orchestration/reasoning/engines/query_router.py` | Route purity reference — read only |
| 3 | `agentic_core/L3_orchestration/reasoning/engines/evidence_shaper.py` | Normative filter reference — read only |
| 4 | `agentic_core/L1_reasoning/` | Abstain planning (F06), decomposition (F05) |
| 5 | `agentic_core/L4_state/cache/` | Cache implementations — F08 (exact), F09 (semantic) |
| 6 | `agentic_core/L5_policy/` | Governance, safety guardrails (F18, F19, F27) |
| 7 | `agentic_core/L6_observation/` | Observability spine (F29), shadow evaluation (F30) |
| 8 | `docs/requirements/` | Presence/absence of TS-20 normative spec |
| 9 | `docs/architecture/` | Presence/absence of F25-int ADR |
| 10 | `tools/eval/audit_wave_b_target_state.py` | Eval harness baseline — read only |

---

## 6. Exact Out-of-Scope List

The following are **explicitly forbidden** in Wave C. Any proposal to do these requires a new HITL decision packet.

| Category | Forbidden action |
|----------|-----------------|
| Topology | Add, rename, split, or merge any ChromaDB collection |
| Metadata | Add or remove any of the 14 mandatory metadata fields |
| Routing | Modify `query_router.py` domain-to-collection mappings |
| Shaping | Modify `evidence_shaper.py` normative filter or `allowed_collections` |
| Eval harness | Modify `retrieval_eval_curated.py` query set, thresholds, or gates |
| F25 adjudication | Reopen F25-int as ext_authority target; add sources for retired F25 query |
| Closed topics | Add ext_authority sources for TS-03, TS-04, TS-07, TS-09, TS-19 |
| Retrieval redesign | Start any hybrid fusion, reranking pipeline, or query intent detection work |
| Wave D scope | Any implementation slice not listed in §3 allowed workstreams |
| Cross-lane filling | Fill ext_authority gap with repo_evidence; fill repo_evidence gap with ext_authority |
| ext_raw promotion | Promote any ext_raw chunk to ext_authority without full re-ingestion |

---

## 7. Validation and Non-Regression Gates

### 7a. Per-phase stop gates

| Phase | Gate condition | Fail action |
|-------|---------------|-------------|
| C1.3 | Gap map produced; no edits made | Stop; report gap map only |
| C2.1 | TS-20 query returns dist@1 < 0.50 in repo_evidence after rebuild | Revise document content; re-embed |
| C2.2 | F25-int query returns dist@1 < 0.50 in repo_evidence after rebuild | Revise document content; re-embed |
| C3.1 | F02 candidate returns dist@1 < 0.45 | Skip C3 entirely; F02 remains advisory |
| C4.1 | All 11 freeze gates PASS | BLOCKED — identify regressed gate and fix before proceeding |

### 7b. Non-regression invariants (always-on through Wave C)

| Invariant | Check method |
|-----------|-------------|
| G1–G3: ext_authority metadata | Run `tools/eval/audit_wave_b_target_state.py` after any ext_authority change |
| G4–G6: repo_evidence metadata | Run ingestion validation after any repo_evidence change |
| G9 ≥ 75% | Re-run G9 query suite after any ext_authority change |
| G10: 0 repo_evidence contamination | Run target-state audit after any collection change |
| G11: 0 ext_raw contamination | Run target-state audit after any collection change |
| Route purity | Confirm `query_router.py` domain mappings unchanged before C4 |
| Normative filter | Confirm `evidence_shaper.py` allowed_collections unchanged before C4 |

### 7c. Minimum evidence standard for new sources (§8 handoff contract)

A new ext_authority source is accepted only if it returns **dist@1 < 0.45** for the gap query. Sources that return dist@1 ≥ 0.45 are rejected (F02 advisory gate; same standard that closed F12, F14 etc. in B6.x).

---

## 8. Stop Conditions per Phase

| Phase | Stop condition |
|-------|---------------|
| C1 | `docs/reports/wave_c_gap_map.md` written. No edits to any code or ingestion config. |
| C2 | Both Lane C documents added to repo_evidence, G4/G5/G6 pass, dist@1 < 0.50 for both queries. |
| C3 | Either F02 source added + G1/G2/G3/G9 pass, **or** C3 skipped (dist@1 ≥ 0.45). |
| C4 | All 11 freeze gates PASS, `wave_c_closeout.md` written. |

**Wave C is complete when C4 stop condition is met.** Do not begin Wave D implementation until the C4 closeout report is written and verified.

---

## 9. Explicit Lane-Authority Declarations

These four statements are binding for every Wave C action:

1. **`ext_authority` defines target state.** Every external best-practice, policy, tool-contract, or architecture-pattern guidance comes from `ext_authority` only.

2. **`repo_evidence` defines current state.** Every query about what the current codebase does, how it is structured, and where it diverges from target state uses `repo_evidence` only.

3. **No cross-lane gap filling.** An external target-state gap (ext_authority dist@1 > 0.50) is never closed by adding a `repo_evidence` document. An internal current-state gap (repo_evidence dist@1 > 0.50) is never closed by adding an `ext_authority` source.

4. **No reopening of closed Wave B source-authority decisions.** The F25-int adjudication, the TS-20 scoping, the TS-03/TS-04/TS-07/TS-09/TS-19 ADEQUATE status, and the G9 denominator composition are all final. Wave C inherits them without modification.

---

## 10. Wave C Entry Criteria (verified at plan creation)

- [x] `wave_c_handoff_contract.md` v2.0 — Active
- [x] `wave_b_closeout.md` v2.0 — COMPLETE
- [x] All 11 Wave B freeze gates PASS (`wave_b_b7_freeze_gates.md`)
- [x] `wave_b_target_state_registry.md` v2.0 — 22 grounded topics, F25 split final
- [x] This plan created — Wave C may begin with C1.1

---

## 11. Gap Register (initial, from B7 artifacts)

| Gap ID | Topic | Type | Lane | C-Phase | Status |
|--------|-------|------|------|---------|--------|
| WC-G01 | TS-20 — Normative requirements spec | DOC_GAP | repo_evidence Lane C | C2.1 | Open |
| WC-G02 | F25-int — Healing dispatch routing architecture | DOC_GAP | repo_evidence Lane C | C2.2 | Open |
| WC-G03 | F02 — Ingress auth/quota/schema | ADVISORY | ext_authority advisory | C3.1 | Open (optional) |
| WC-G04 | F28 — UWG/write governance | ADVISORY | repo_evidence Lane C | Post-C4 | Advisory (Wave D) |

**All other B7 families**: ADEQUATE or INTERNAL — no Wave C action required.
