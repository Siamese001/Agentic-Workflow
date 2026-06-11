---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\adg_prompt_packet_families.md'
original_relative_path: 'adg_prompt_packet_families.md'
source_sha256: fe5ef956f1bd351d07c9256aa1a788df8112cf9df572deadfb414814215af23d
recovered_status: LOST_RECOVERED
last_commit: 'fd8afcb3494'
last_commit_date: '2026-04-11 11:10:04 -0400'
created_date: '2026-04-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Prompt Packet Families — Applicability Matrix and Selection Policy
**Stage 1 Design — No code changes**
**Date:** 2026-04-11 | Scope: Packet applicability for C0 bridge, runtime selection policy, family-specific rules

---

## 1. Executive Summary

Of the 8 existing packet families, **1 is the valid default** for the C0 bridge, **1 is conditionally valid**, and **6 are ADG-file-first**. No new packet families are required. The runtime packet selection policy is a decision tree keyed on request shape (does the request involve a specific structural path?), evidence shape (confidence band, span count, source type), and abstain state. The safe default is always `executive_summary`. The decision to escalate to `graph_path_explanation` requires explicit path-node evidence in the C0 bundle.

**Architecture law preserved:** Packet type selection is a dispatcher decision (L3 orchestration). The PA package does not select packet types — it only validates and assembles them.

---

## 2. Packet Applicability Matrix

| Packet type | C0 Bridge Status | Reasoning |
|-------------|-----------------|-----------|
| `executive_summary` | **DEFAULT VALID** | Broadest output schema; smallest budget (4,000 tokens); handles most query types; output_schema is generic enough to absorb C0-sourced narrative summaries |
| `graph_path_explanation` | **CONDITIONALLY VALID** | Valid only when: (a) request concerns a specific from_node→to_node structural path, AND (b) C0 spans contain path-relevant evidence, AND (c) `from_node` and `to_node` are populated by the dispatcher |
| `determinism_rca` | **ADG-FILE-FIRST** | Requires `provenance_report`, `closure_report`, `sqlite` — structured ADG artifacts not produceable from C0 text spans |
| `p0_failure` | **ADG-FILE-FIRST** | Requires structured violation records from SQLite — violation severity, rule_id, hop analysis are not recoverable from text spans |
| `ratchet_review` | **ADG-FILE-FIRST** | Requires P1/P2 ratchet JSON and burndown table — historical count data not available from retrieval |
| `unknown_unresolved_triage` | **ADG-FILE-FIRST** | Requires layer coverage report and SQLite unresolved imports — structural ADG outputs |
| `hotspot_investigation` | **ADG-FILE-FIRST** | Requires fan-in/fan-out metrics and structural centrality — graph metrics not available from text retrieval |
| `infrastructure_boundary` | **ADG-FILE-FIRST** | Requires infra wiring SQL views — structured schema not available from text retrieval |

### 2.1 Why `executive_summary` Is the Default

- **Output schema is broadest:** covers `run_summary`, `top_blockers`, `likely_false_positives`, `taxonomy_mismatches`, `recommended_next_wave`, `uncertainty_disclosure` — all expressible from narrative C0 spans
- **Smallest token budget (4,000):** least risk of overflow; bounded at 15 spans
- **`uncertainty_disclosure` field:** explicitly carries evidence quality signals to L2 — no schema change needed
- **`abstain` path is natural:** if C0 coverage is insufficient, `executive_summary` abstain output is meaningful (L2 sees "insufficient evidence for summary")
- **Template task block is overrideable:** the dispatcher supplies a C0-specific task block describing the current query, not the ADG analysis task

### 2.2 Why `graph_path_explanation` Is Conditional, Not Default

- Requires `from_node` and `to_node` explicit parameters — C0 retrieval may not always surface these
- Output schema (`violating_path[]`, `first_illegal_hop{}`, `blast_radius_neighbors[]`) is path-specific — a C0 bundle without path structure cannot fill these fields meaningfully
- If the dispatcher routes here without explicit path params, the `replay_extras` will have empty `from_node`/`to_node`, and the `task_block` will reference empty node names
- The larger budget (6,000 tokens) provides headroom but does not offset the schema mismatch risk

### 2.3 ADG-File-First: What Happens if C0 Evidence Arrives Anyway

Each ADG-file-first packet type has a defined behavior when a C0 bundle is routed there:

| Packet type | C0 bundle received | Behavior |
|-------------|-------------------|---------|
| `determinism_rca` | C0 spans with no provenance/closure data | `coverage_score=0.0` from shaper (no must-use sources present) → bridge merger patches to `contract.coverage_score` → if ≥ 0.30: partial emit; if < 0.30: adapter abstain fires first |
| `p0_failure` | C0 spans with no violation records | Same as above |
| `ratchet_review` | C0 spans with no ratchet JSON data | Same as above |
| `unknown_unresolved_triage` | C0 spans | Same as above |
| `hotspot_investigation` | C0 spans | Same as above |
| `infrastructure_boundary` | C0 spans | Same as above; pre-existing source_type mismatch means infra_view coverage is always 0 anyway |

**In all cases:** The adapter's abstain gate prevents routing a low-coverage C0 bundle to these packets. If coverage ≥ 0.30 and a misconfigured dispatcher routes here, the packet emits as `"partial"` with weak_support=True and explicit gap signals. This is degraded but not catastrophically wrong — L2 receives evidence quality signals.

**Dispatcher rule:** Never explicitly route to ADG-file-first packets for C0-only evidence. The routing logic must check the request type before selecting a packet family.

---

## 3. Runtime Packet Selection Policy

### 3.1 Decision Tree

```
L3 Dispatcher receives: (request_context, C0EvidenceContract, confidence_band)
    │
    ├── [1] abstain_hint == True OR coverage_score < 0.30?
    │         YES → ABSTAIN — do not select any packet type
    │               Return abstain signal to caller
    │         NO  → continue
    │
    ├── [2] Does the request explicitly name a structural path
    │        (from_node, to_node) AND are these fields populated
    │        from C0 span data?
    │         YES → Select: graph_path_explanation
    │               Populate from_node, to_node in replay_extras
    │         NO  → continue
    │
    ├── [3] confidence_band == "HIGH" AND request is general-purpose?
    │         YES → Select: executive_summary
    │         NO  → continue
    │
    ├── [4] confidence_band == "MEDIUM" OR "LOW"?
    │         YES → Select: executive_summary (safest packet under weak evidence)
    │         NO  → continue
    │
    └── [5] Default: executive_summary
```

**Rationale for simplicity:** The decision tree has only 5 branches because 6 of 8 packet types are off-limits for C0-only evidence, and the remaining 2 cover the full range of valid C0 request types. Future branches can be added as new packet types become C0-compatible.

### 3.2 When to Force `executive_summary`

Force `executive_summary` unconditionally when:

| Condition | Force reason |
|-----------|-------------|
| `confidence_band` is `"MEDIUM"` or `"LOW"` | Not enough evidence quality for specialized analysis |
| Request does not name a specific structural path | No basis for `graph_path_explanation` |
| `from_node` or `to_node` is empty string `""` | `graph_path_explanation` would produce malformed task block |
| C0 spans cover multiple unrelated source files | No coherent structural path can be synthesized |
| `coverage_score` is between 0.30 and 0.50 (LOW band) | Maximize coverage via broadest schema |
| First-time bridge invocation (no prior packet for this request) | Always start with the broadest packet; narrow in follow-on |

### 3.3 When `graph_path_explanation` Is Allowed

All conditions must be true simultaneously:

| Condition | Check |
|-----------|-------|
| `confidence_band` is `"HIGH"` or `"MEDIUM"` | `coverage_score >= 0.50` |
| Request explicitly identifies `from_node` | Dispatcher has resolved node ID from C0 span context |
| Request explicitly identifies `to_node` | Same |
| At least 3 C0 spans reference the structural path between `from_node` and `to_node` | Verified from span `source_ref` values |
| `abstain_hint` is `False` | No abstain signal |

### 3.4 When to Emit No Packet (Abstain Wins)

Abstain and emit no packet when any of these conditions is true:

| Condition | Source |
|-----------|--------|
| `abstain_hint == True` | C0 contract — authoritative, non-overridable |
| `coverage_score < 0.30` | C0 contract threshold |
| `len(cited_spans) == 0` after pruning | Empty evidence set |
| All spans have `relevance_score < 0.10` | Below minimum retrieval signal |
| `overflow_action == "abstained"` from `apply_budget()` | Budget cannot fit even 1 span |
| `evidence_hmac` is None in the contract | Unvalidated contract — refuse to process |

---

## 4. Packet-Family-Specific Boundedness Rules

### 4.1 `executive_summary` — Full Boundedness Spec

| Rule | Value |
|------|-------|
| Max span count | 15 |
| Max `text_snippet` length | 512 chars |
| Max tokens in `must_use_evidence` | 2,000 |
| Max `task_block` tokens | 200 |
| Max `ContradictionFlag` count | 4 |
| Overflow action order | narrow → summarize → partial emit |
| Abstain trigger | `coverage_score < 0.30` OR `overflow_action="abstained"` |
| `assembly_result` guarantee | Never `"fail"` if `coverage_score >= 0.30` and budget can fit ≥ 1 span |
| Must-use source type expected | None (bridge uses `source_type="json_report"` proxy; all C0 spans are treated as canonical) |
| Optional evidence | Empty (`opt_items=[]`) |
| Replay extras required | `retrieval_id`, `request_id`, `evidence_hmac`, `coverage_score`, `abstain_hint`, `confidence_band` |
| Disk write condition | `assembly_result in ("pass", "partial")` |

**Output schema compatibility with C0 spans:**

| Schema field | C0 bridge can fill? | How |
|-------------|---------------------|-----|
| `run_summary` | Yes | L2 synthesizes from C0 span text |
| `top_blockers` | Partially | Only if C0 spans reference violation-like content |
| `likely_false_positives` | Partially | If C0 spans reference taxonomy gap signals |
| `taxonomy_mismatches` | Partially | Same |
| `recommended_next_wave` | Yes | L2 generates from evidence quality and gap signals |
| `uncertainty_disclosure` | Yes | Driven by `weak_support`, `gaps`, `confidence_band` in replay_metadata |

### 4.2 `graph_path_explanation` — Conditional Boundedness Spec

| Rule | Value |
|------|-------|
| Max span count | 20 |
| Max `text_snippet` length | 512 chars |
| Max tokens in `must_use_evidence` | 4,000 |
| Max `task_block` tokens | 200 |
| Max `ContradictionFlag` count | 4 |
| Required `replay_extras` fields | Same as executive_summary + `from_node`, `to_node` |
| Overflow action order | narrow → summarize → partial emit |
| Abstain trigger | Same as executive_summary |
| Routing gate | `from_node` AND `to_node` must both be non-empty |

**Output schema compatibility with C0 spans:**

| Schema field | C0 bridge can fill? | How |
|-------------|---------------------|-----|
| `violating_path` | Conditionally | Only if C0 spans describe a structural hop |
| `first_illegal_hop` | Conditionally | Requires structured violation context in spans |
| `missing_choke_point` | Unlikely | This is ADG-analysis specific |
| `blast_radius_neighbors` | Unlikely | Graph metric not recoverable from text spans |
| `cross_snapshot_diff` | No | Multi-snapshot data not available from C0 |

**Consequence:** When routing to `graph_path_explanation` with C0 evidence, L2 may not be able to fill all output schema fields. The `uncertainty_disclosure` pattern from `executive_summary`'s schema is not present here. Dispatcher should prefer `executive_summary` unless the request is explicitly path-specific and the user accepts partial schema fill.

### 4.3 ADG-File-First Packets — Uniform Boundedness Rule

For all 6 ADG-file-first packets (`determinism_rca`, `p0_failure`, `ratchet_review`, `unknown_unresolved_triage`, `hotspot_investigation`, `infrastructure_boundary`):

**Routing rule:** Never route C0-only evidence bundles here in the initial bridge implementation.

**Emergency fallback rule (if misconfigured dispatcher routes here):**
- Adapter abstain gate catches `coverage_score < 0.30` — no packet emitted
- If `coverage_score >= 0.30`: packet emits as `"partial"` with `weak_support=True`
- `evidence_contract_status = "partial"` (bridge merger's coverage override ensures this)
- L2 receives explicit partial + weak_support signal and must not treat output as ADG-grade analysis

**No new boundedness rules required** — existing overflow logic handles this correctly via the adapter abstain gate and bridge merger coverage override.

---

## 5. Packet Selection and Evidence Shape Interaction

### 5.1 Evidence Shape → Packet Type Mapping

| Coverage band | Span count | Confidence band | Recommended packet |
|--------------|-----------|-----------------|-------------------|
| ≥ 0.80 | 5–15 | HIGH | `executive_summary` or `graph_path_explanation` if path |
| ≥ 0.80 | 1–4 | HIGH | `executive_summary` (limited span diversity) |
| 0.50–0.79 | 5–15 | MEDIUM | `executive_summary` |
| 0.50–0.79 | 1–4 | MEDIUM | `executive_summary` (partial result expected) |
| 0.30–0.49 | any | LOW | `executive_summary` only (weak evidence; broadest schema safest) |
| < 0.30 | any | ABSTAIN | No packet — abstain |

### 5.2 Request Shape → Packet Type Override

| Request shape | Override | Condition |
|--------------|---------|-----------|
| "Explain the path from X to Y" | Route to `graph_path_explanation` | Only if coverage ≥ 0.50 AND `from_node`/`to_node` populated |
| "What are the P0 violations in this run?" | Route to `executive_summary` (not `p0_failure`) | C0 spans cannot fill P0 output schema |
| "What changed since last snapshot?" | Route to `executive_summary` | C0 spans may contain diff-like content; executive schema fits |
| "What hotspots should I fix?" | Route to `executive_summary` | C0 spans cannot supply fan-in metrics |
| "Give me a run summary" | Route to `executive_summary` | Natural fit |
| Any ambiguous request | Route to `executive_summary` | Safe default always |

---

## 6. Future-Extensible Packet Families

These are currently ADG-file-first but could become C0-compatible in future iterations with minimal design extension:

| Packet type | Extension needed | When |
|------------|-----------------|------|
| `p0_failure` | C0 would need to retrieve structured violation records (not text spans) — requires a C0 retrieval mode for SQLite violation rows | Future: if C0 gains structured-record retrieval mode |
| `ratchet_review` | C0 would need ratchet JSON retrieval | Future: if ratchet data is indexed in the retrieval store |
| `unknown_unresolved_triage` | C0 could retrieve unresolved import lists from report artifacts | Future: if reporting artifacts are indexed |
| `hotspot_investigation` | C0 would need graph metric retrieval — unlikely from text spans alone | Long-term; requires graph-metric indexing |
| `determinism_rca` | C0 could retrieve provenance report text — schema fill would be partial | Future: if provenance reports are indexed |
| `infrastructure_boundary` | C0 could retrieve infra wiring view results — source_type correction needed | Future: after pre-existing source_type mismatch is fixed |

**None of these extensions require new packet families.** They require C0 retrieval to expand its source types.

---

## 7. Assumptions and Uncertainties

| Item | Status |
|------|--------|
| L3 dispatcher has access to the request's `from_node`/`to_node` intent before calling the adapter | **Architectural assumption** — dispatcher design is out of scope |
| `executive_summary` output schema is flexible enough for general C0 query results | **Design assumption** — `uncertainty_disclosure` field provides the escape valve |
| `graph_path_explanation` routing will be rare in initial bridge usage | **Expected usage assumption** — most bridge queries are general-purpose |
| ADG-file-first packets remain off-limits for C0-only evidence in initial implementation | **Policy decision** — confirmed by design law |
| No new packet families are required for initial bridge | **Firm decision** — 8 existing families cover the design space |
| Future C0 retrieval mode expansion (structured records) does not require new packet types | **Design assumption** — confirmed by extensibility analysis |
