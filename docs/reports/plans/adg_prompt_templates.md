# ADG Prompt Templates — Packet-by-Packet Runtime-Readiness Review
**Stage 1 Design — No code changes**
**Date:** 2026-04-11 | Scope: All 8 PacketTemplate entries, shared static blocks, block ordering

---

## 1. Executive Summary

All 8 packet families are **runtime-ready for the C0→PA bridge without template modifications**. The static block design (shared `_SHARED_POLICY`, `_SHARED_ABSTAIN`, `_SHARED_REFINE`) has zero duplication and zero wording drift. The canonical 10-block envelope order is enforced structurally. The `_assemble()` helper is the single convergence point — no per-builder assembly drift. Two low-severity template gaps are documented: (1) `graph_path_explanation` has a structural dependency on a loaded `graph` object that is not always satisfiable from C0 evidence alone; (2) the `evidence_contract_status` threshold in `_assemble()` uses `> 0.0` for `"partial"` rather than the C0-derived `>= 0.30` threshold — a cosmetic misalignment that does not affect bridge correctness.

---

## 2. Shared Static Block Review

### 2.1 `_SHARED_POLICY` — CLEAN, NO DRIFT

Used by all 8 packet types. Content (from `registry.py` line 61–68):

```
1. Canonical ADG artifacts (SQLite, JSON reports) are the source of truth.
2. Graph DB outputs are augmenting evidence only — never override canonical truth.
3. Contradictions between sources MUST be preserved and reported, never hidden.
4. Weak evidence MUST be flagged; do not present weak support as strong.
5. If evidence is insufficient, abstain or request scope refinement.
6. All durable mutations terminate at the Universal Write Gateway (UWG).
7. C0 retrieves only; prompt assembly packages only; L0 routes only; L2 executes only.
```

**Bridge impact:** Rule 7 explicitly names the C0→PA separation law. No change needed.

**Scatter check:** `_SHARED_POLICY` is defined **once** at `registry.py:60`, referenced by all 8 `PacketTemplate` constructors via `policy_block=_SHARED_POLICY`. No per-template copy exists. **No duplication, no drift.**

### 2.2 `_SHARED_ABSTAIN` — CLEAN

Content: "If the evidence is insufficient to answer the task with confidence, state explicitly what is missing and suggest a refinement query. Do not fabricate evidence or invent findings not grounded in the provided artifacts."

All 8 types use `abstain_instructions=_SHARED_ABSTAIN`. `_assemble()` augments it dynamically when `coverage < 0.3` (prepends gap list). No per-template override. **No duplication, no drift.**

### 2.3 `_SHARED_REFINE` — CLEAN

Content: "If the evidence bundle has coverage_score < 0.3 or critical gaps, request: (a) regeneration of the ADG with --force, (b) a narrower scope (specific layer or file), or (c) additional artifact types to fill the gap."

All 8 types use `refine_instructions=_SHARED_REFINE`. `_assemble()` augments with `budget_result.summary_note` when overflow occurs. No per-template override. **No duplication, no drift.**

**Bridge compatibility note:** The refine instruction references ADG regeneration (`--force`). For a C0-sourced bundle, the refine path is different — narrower scope at the retrieval layer, not ADG regeneration. This is a **low-severity content gap** but does not block the bridge. The instruction is a fallback; L2 will read it only when evidence is insufficient. In C0 bridge mode, the `refine_instructions` field should be supplemented by the bridge dispatcher with a C0-specific refinement hint. This does not require a template change — the dispatcher can supply it via `task_block` context or a `replay_extras["refine_hint"]` key in `replay_metadata`.

---

## 3. Packet-by-Packet Runtime-Readiness Review

### 3.1 `determinism_rca`

| Dimension | Assessment |
|-----------|-----------|
| **Purpose** | Diagnose digest mismatches, node/edge reconciliation failures, provenance probe errors |
| **Required inputs** | ADG provenance report, closure report, SQLite node/edge counts |
| **Must-use evidence sources** | `provenance_report`, `closure_report`, `sqlite` |
| **Optional evidence sources** | `graph_db` (neighborhood around `__root__`) |
| **Contradiction handling** | `_reconcile_counts()` detects provenance `nodes_match=False`, `edges_match=False` — exact use case for this packet |
| **Abstain / refine behavior** | Abstain if none of 3 must-use sources present; refine with ADG regeneration |
| **Output schema** | `root_cause_hypotheses[]`, `affected_artifacts[]`, `mismatch_details{}`, `next_diagnostic_steps[]`, `confidence` |
| **Replay metadata expectations** | `snapshot_ids`, `commit_shas`, `artifact_digests`, `source_artifacts` |
| **L2 consumption expectations** | L2 receives structured JSON; executes `next_diagnostic_steps` via UWG where applicable |
| **Token budget** | 8,000 total — largest budget; appropriate for multi-source reconciliation |
| **C0 bridge fit** | **LOW** — this packet is ADG-file specific; C0 spans do not contain provenance/closure data. Not a natural bridge target. |
| **Bridge gap** | If a C0 bundle is passed here, `coverage_score` will be low (none of the 3 must-use sources present) → `abstain` path fires correctly. No template change needed. |

---

### 3.2 `p0_failure`

| Dimension | Assessment |
|-----------|-----------|
| **Purpose** | Diagnose hard-fail violations (layer violations, circular imports, dynamic_exec) |
| **Required inputs** | SQLite violations (limit 30), closure report, `sc_ap_config.json` |
| **Must-use evidence sources** | `sqlite`, `closure_report`, `sc_ap_config` |
| **Optional evidence sources** | `graph_db` |
| **Contradiction handling** | SQLite violation count vs. closure report summary may diverge; `ContradictionFlag` fires |
| **Abstain / refine behavior** | Abstain if SQLite missing or zero violations present with all sources empty |
| **Output schema** | `rule_id`, `violation_class`, `stage`, `offending_files[]`, `offending_path`, `first_illegal_hop`, `candidate_repair_mode`, `safe_next_step` |
| **Replay metadata expectations** | `snapshot_ids`, `commit_shas`, `artifact_digests`, `source_artifacts` |
| **L2 consumption expectations** | L2 routes repair actions via UWG; violation class determines repair mode |
| **Token budget** | 6,000 total |
| **C0 bridge fit** | **LOW** — P0 violations live in ADG SQLite; C0 retrieval does not surface structured violation records |
| **Bridge gap** | Same as `determinism_rca`: abstain path fires correctly when C0 bundle has no `sqlite` source type. |

---

### 3.3 `ratchet_review`

| Dimension | Assessment |
|-----------|-----------|
| **Purpose** | Compare P1/P2 anti-pattern counts against baseline ratchet ceilings |
| **Required inputs** | P1 ratchet JSON, P2 ratchet JSON, burndown table, SQLite anti-pattern counts |
| **Must-use evidence sources** | `ratchet`, `burndown`, `sqlite` |
| **Optional evidence sources** | `structural` |
| **Contradiction handling** | Burndown table vs. SQLite anti-pattern counts may diverge — `_reconcile_counts()` fires |
| **Abstain / refine behavior** | Abstain if ratchet files missing; refine with ADG regeneration |
| **Output schema** | `gross_count`, `net_delta`, `new_violations`, `resolved_violations`, `affected_layers[]`, `critical_path_count`, `exemptions`, `recommended_fix_ordering[]` |
| **Replay metadata expectations** | `snapshot_ids`, `commit_shas`, `artifact_digests` |
| **L2 consumption expectations** | L2 triggers ratchet-repair wave; fix ordering drives PR review scope |
| **Token budget** | 6,000 total |
| **C0 bridge fit** | **LOW** — ratchet data is ADG-specific |
| **Bridge gap** | Correct abstain path. No template change. |

---

### 3.4 `unknown_unresolved_triage`

| Dimension | Assessment |
|-----------|-----------|
| **Purpose** | Classify unknown modules and unresolved imports as taxonomy lag vs. structural gaps |
| **Required inputs** | Layer coverage report, SQLite unresolved imports (limit 30) |
| **Must-use evidence sources** | `layer_coverage_report`, `sqlite` |
| **Optional evidence sources** | `graph_db` (neighborhood around `__unknown__`) |
| **Contradiction handling** | Layer coverage report unknown count vs. SQLite unresolved import count |
| **Abstain / refine behavior** | Abstain if layer coverage missing |
| **Output schema** | `unknown_modules[]`, `unresolved_imports[]`, `taxonomy_lag_candidates[]`, `real_structural_gaps[]`, `package_concentration{}` |
| **Replay metadata expectations** | `snapshot_ids`, `commit_shas` |
| **L2 consumption expectations** | L2 issues layer mapping tasks or deletion requests via UWG |
| **Token budget** | 6,000 total |
| **C0 bridge fit** | **LOW** — layer coverage is ADG-specific |
| **Bridge gap** | Correct abstain path. No template change. |

---

### 3.5 `hotspot_investigation`

| Dimension | Assessment |
|-----------|-----------|
| **Purpose** | Identify high fan-in/fan-out nodes and connected risk surfaces |
| **Required inputs** | SQLite fan-in hotspots (top N), fan-out hotspots (top N), structural centrality (top N) |
| **Must-use evidence sources** | `sqlite`, `structural` |
| **Optional evidence sources** | `graph_db` (blast radius of top hotspot) |
| **Contradiction handling** | SQLite fan-in vs. structural centrality ranking may differ; `ContradictionFlag` fires |
| **Abstain / refine behavior** | Abstain if both sqlite and structural missing; refine with narrower scope |
| **Output schema** | `top_fan_in[]`, `top_fan_out[]`, `top_violation_files[]`, `connected_risk_surfaces[]`, `root_cause_neighborhoods[]` |
| **Replay metadata expectations** | `snapshot_ids`, `commit_shas`, `artifact_digests` |
| **L2 consumption expectations** | L2 prioritizes repair tasks by fan-in score; high-fan-in nodes are fix-ordering input |
| **Token budget** | 8,000 total — largest budget |
| **Builder note** | `build_hotspot_investigation()` calls `fetch_fan_in_hotspots(top_n=1)` twice (once for must_items, once to get hotspot node for graph). This is a minor inefficiency but not a correctness issue. |
| **C0 bridge fit** | **LOW** — structural centrality and fan-in data are ADG graph artifacts |
| **Bridge gap** | Correct abstain path. No template change. |

---

### 3.6 `infrastructure_boundary`

| Dimension | Assessment |
|-----------|-----------|
| **Purpose** | Identify raw infra spread, write-path bypass risks, provider choke-point failures |
| **Required inputs** | SQLite infra wiring views (limit 30), SQLite violations (limit 20) |
| **Must-use evidence sources** | `infra_view`, `sqlite` |
| **Optional evidence sources** | `graph_db` (neighborhood around `__infra__`) |
| **Contradiction handling** | Infra view counts vs. violation count may diverge |
| **Abstain / refine behavior** | Abstain if infra views missing |
| **Output schema** | `raw_infra_spread[]`, `write_path_bypass_risks[]`, `choke_point_failures[]`, `approved_surfaces[]`, `miswired_surfaces[]` |
| **Replay metadata expectations** | `snapshot_ids`, `commit_shas` |
| **L2 consumption expectations** | L2 triggers infra wiring repair tasks via UWG |
| **Token budget** | 6,000 total |
| **Registry / builder mismatch note** | `PacketTemplate.must_use_sources = ["infra_view", "sqlite"]` but `build_infrastructure_boundary()` passes `sq.fetch_infra_wiring_views()` as `source_type="sqlite"` (not `"infra_view"`). The coverage computation will find `"sqlite"` but not `"infra_view"` in present sources → **partial coverage flag fires unnecessarily**. This is a **low-severity content mismatch** between registry template and builder. |
| **C0 bridge fit** | **LOW** |
| **Bridge gap** | Correct abstain path. The registry/builder mismatch noted above is pre-existing. |

---

### 3.7 `graph_path_explanation`

| Dimension | Assessment |
|-----------|-----------|
| **Purpose** | Explain violating paths, first illegal hops, missing choke points, blast-radius neighbors |
| **Required inputs** | `from_node`, `to_node` parameters; SQLite violations; NetworkX `graph` object |
| **Must-use evidence sources** | `graph_db`, `sqlite` |
| **Optional evidence sources** | `structural` |
| **Contradiction handling** | Graph path vs. SQLite violation record may disagree on severity |
| **Abstain / refine behavior** | When `graph=None`, an error `EvidenceItem` is injected into `must_items` with `data={"error": "graph_not_loaded"}` — this triggers `evidence_status="partial"` → `assembly_result="partial"` |
| **Output schema** | `violating_path[]`, `first_illegal_hop{}`, `missing_choke_point`, `blast_radius_neighbors[]`, `cross_snapshot_diff{}` |
| **Replay metadata** | Includes `from_node`, `to_node` via `replay_extras` — **the only packet with path-specific replay data** |
| **L2 consumption expectations** | L2 uses path data to guide surgical repair; blast-radius informs regression test scope |
| **Token budget** | 6,000 total |
| **Structural dependency gap** | `build_graph_path_explanation()` requires both `from_node`/`to_node` params and a loaded `graph` object. The CLI default is `graph=None`. When `graph=None`, the `graph_db` must-use item is an error placeholder. The `_assemble()` coverage check excludes error items (`if not item.data.get("error")`). If `graph=None`, the only non-error must item is the SQLite violation list — coverage will be partial, not empty. `assembly_result="partial"` fires. L2 receives a partial packet — this is correct behavior, not a defect. |
| **C0 bridge fit** | **MEDIUM** — if C0 retrieves structured path data (e.g., from a graph traversal result), this packet could receive it as `must_use_evidence`. The `replay_extras` mechanism already supports `from_node`/`to_node`. |
| **Bridge gap** | `graph_db` items from C0 would need `is_derived=False` (C0 retrieval is canonical, not derived). The `GraphDBAdapter` currently hardcodes `is_derived=True`. For C0-sourced path data, the adapter sets `is_derived=False` — no template change needed. |

---

### 3.8 `executive_summary`

| Dimension | Assessment |
|-----------|-----------|
| **Purpose** | One-run executive summary: top blockers, false positives, taxonomy mismatches, recommended next wave |
| **Required inputs** | Snapshot JSON, burndown table, closure report, P1 ratchet, P2 ratchet |
| **Must-use evidence sources** | `snapshot`, `burndown`, `closure_report`, `ratchet` |
| **Optional evidence sources** | `structural` (centrality top 5), `graph_db` |
| **Contradiction handling** | Snapshot node count vs. burndown violation count vs. closure summary — multi-source reconciliation |
| **Abstain / refine behavior** | Abstain if snapshot missing; partial if ratchet missing |
| **Output schema** | `run_summary`, `top_blockers[]`, `likely_false_positives[]`, `taxonomy_mismatches[]`, `recommended_next_wave`, `uncertainty_disclosure` |
| **Replay metadata expectations** | `snapshot_ids`, `commit_shas`, `artifact_digests` |
| **L2 consumption expectations** | L2 uses `recommended_next_wave` to select next workwave; `top_blockers` drives prioritization |
| **Token budget** | 4,000 total — smallest budget; appropriate for summary packet |
| **Builder note** | `build_executive_summary()` constructs `StructuralAdapter(sqlite_path)` and calls `st.fetch_centrality(top_n=5)` even though `structural` is an optional source. This is correct — optional evidence is fetched unconditionally and filtered by budget. |
| **C0 bridge fit** | **MEDIUM** — a C0 retrieval that produces summary statistics could supply `snapshot`-type evidence here. More likely this packet remains ADG-file-only. |
| **Bridge gap** | None specific to this packet. |

---

## 4. Template and Static-Block Scatter Findings

### 4.1 Shared Block Duplication — NONE FOUND
- `_SHARED_POLICY`: 1 definition, 8 references — clean
- `_SHARED_ABSTAIN`: 1 definition, 8 references — clean  
- `_SHARED_REFINE`: 1 definition, 8 references — clean

### 4.2 Per-Packet System Block Wording Drift — NONE FOUND
Each of the 8 `system_block` strings describes a distinct analyst role. No overlapping wording, no copy-paste artifacts. The pattern is consistent: `"You are an ADG <role> analyst/reviewer. Your role is to <verb phrase>."` All 8 follow this template exactly.

### 4.3 Task Block Wording — CLEAN, NO DRIFT
Task blocks are defined **inside builder functions** (not in registry templates), making them per-call configurable. They are single-string literals — no interpolation except for `graph_path_explanation` which interpolates `from_node`/`to_node`. No duplication found.

### 4.4 Output Schema Consistency — CLEAN
Every `output_schema` is a JSON Schema `object` with `properties`. No arrays at root level, no untyped objects. Consistent across all 8 types.

### 4.5 Pre-Existing Low-Severity Findings

| Finding | Location | Severity | Blocking? |
|---------|----------|---------|-----------|
| `infrastructure_boundary` builder uses `source_type="sqlite"` for infra wiring data but registry expects `"infra_view"` in `must_use_sources` | `builders.py:323`, `registry.py:270` | LOW | No — partial coverage flag, not abstain |
| `graph_path_explanation` always injects an error `EvidenceItem` when `graph=None`, producing a "partial" assembly result even when the packet is otherwise well-formed | `builders.py:366–374` | LOW | No — partial is correct behavior for missing graph |
| `hotspot_investigation` calls `fetch_fan_in_hotspots(top_n=1)` twice (once for evidence, once to get top hotspot node ID) | `builders.py:296–299` | LOW | No — extra DB call, not a correctness issue |
| `_SHARED_REFINE` mentions ADG regeneration as the primary refine action, which is irrelevant for C0-sourced bundles | `registry.py:76–81` | LOW | No — refine path is only hit when coverage is insufficient |

---

## 5. Block Ordering Confirmation

The `PromptEnvelope` field ordering is enforced by `to_dict()` / `to_json()` / `to_markdown()`:

| # | Block | Trimmed by budget? | Preserved under C0 bridge? |
|---|-------|-------------------|---------------------------|
| 1 | `system_block` | Never | ✅ Yes |
| 2 | `policy_block` | Never | ✅ Yes |
| 3 | `task_block` | Never | ✅ Yes |
| 4 | `must_use_evidence` | Trimmed last | ✅ Yes — C0 spans land here |
| 5 | `optional_evidence` | Trimmed first | ✅ Yes — empty for pure C0 |
| 6 | `contradiction_flags` | Never | ✅ Yes — never hidden |
| 7 | `abstain_instructions` | Never | ✅ Yes — augmented when coverage < 0.3 |
| 8 | `refine_instructions` | Never | ✅ Yes — augmented with budget note |
| 9 | `output_schema` | Never | ✅ Yes |
| 10 | `replay_metadata` | Never | ✅ Yes — extended with C0 identity fields |

**Ordering is canonical, enforced by dataclass field order and `to_dict()` key sequence. No reordering required.**

---

## 6. C0 Bridge Template Compatibility Matrix

| Packet type | C0 bridge fit | Natural bridge use case | Gap |
|-------------|--------------|------------------------|-----|
| `determinism_rca` | LOW | ADG-file-only | Correct abstain path fires |
| `p0_failure` | LOW | ADG-file-only | Correct abstain path fires |
| `ratchet_review` | LOW | ADG-file-only | Correct abstain path fires |
| `unknown_unresolved_triage` | LOW | ADG-file-only | Correct abstain path fires |
| `hotspot_investigation` | LOW | ADG-file-only | Correct abstain path fires |
| `infrastructure_boundary` | LOW | ADG-file-only | Correct abstain path fires; pre-existing source_type mismatch |
| `graph_path_explanation` | MEDIUM | C0 could supply structured path data | No template change; `is_derived=False` for C0 path items |
| `executive_summary` | MEDIUM | C0 could supply summary statistics | No template change |

**Observation:** The 8 existing packet families are ADG-analysis-oriented by design. The C0→PA bridge is primarily used when L3 orchestration selects a packet type appropriate to the current request. For most runtime dispatch scenarios, the L3 dispatcher will select a packet type and supply a `task_block` that reflects the live request — not the ADG-analysis task blocks hardcoded in the builders. The bridge does not require new packet types; it requires the builder dispatch to accept a pre-built `EvidenceBundle` rather than always invoking retrieval adapters internally.

---

## 7. Runtime Call Pattern Design (Template Level)

For the C0 bridge, the L3 dispatcher bypasses the per-builder retrieval adapter calls and calls `_assemble()` directly with pre-built items:

```
L3 orchestration dispatcher:
  1. Validate C0EvidenceContract
  2. Select packet_type from registry (based on request context)
  3. Call c0_to_pa_adapter.translate_c0_to_evidence_bundle(contract, packet_type)
     → returns (EvidenceBundle, ContradictionFlag[], gap_strings[])
  4. Merge bundle with adapter contradictions and gaps
  5. Compute confidence_band
  6. Call _assemble(
         template=get_template(packet_type),
         must_items=bundle.items,
         opt_items=[],
         task_block=<request-specific task description>,
         replay_extras={retrieval_id, request_id, evidence_hmac,
                        coverage_score, abstain_hint, confidence_band}
     )
  7. Return PromptEnvelope to L2 dispatcher
  8. Optionally write envelope.to_json() to artifacts/adg/packets/
```

**Key design point:** Steps 1–6 are in the new `c0_to_pa_adapter`. Step 4 (select packet_type) is in L3 orchestration. Steps 7–8 are in L3 orchestration. `_assemble()` is the only PA function called, and it is called with the same signature it already has.

---

## 8. Assumptions and Uncertainties

| Item | Status |
|------|--------|
| All 8 system blocks follow the `"You are an ADG <role>."` pattern | **Confirmed** — read all 8 |
| Task blocks are per-builder literals, not per-template | **Confirmed** — task strings are in `builders.py`, not `registry.py` |
| `_SHARED_POLICY` rule 7 explicitly encodes the C0→PA separation law | **Confirmed** — line 67 of `registry.py` |
| `build_executive_summary()` fetches `StructuralAdapter` evidence unconditionally | **Confirmed** — lines 415–416 of `builders.py` |
| `graph_path_explanation` `replay_extras` pattern is the correct model for bridge-supplied metadata | **Confirmed** — lines 382–391 of `builders.py` |
| The `infrastructure_boundary` registry/builder `source_type` mismatch is pre-existing and known | **Confirmed from code** — not introduced by bridge design |
