# C0 Evidence Packet — Hardening Plan (T2/T3 Additive Schema Extension)

**Status:** In Progress
**Tier:** T3 (cross-layer: L3 types + L_TOOLS bridge + tests)
**ADG Snapshot:** `adg_indexed_04252026_0843.sqlite` (84,920 nodes / 593,555 edges, healthy)
**Plan SSOT:** `.windsurf/plans/c0-evidence-packet-hardening-7d4f1a.md`

## Goal

Extend the C0 `FinalEvidenceContract` (per `docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md`) with twelve hardening primitives sourced from current Anthropic + OpenAI guidance and Microsoft Spotlighting prompt-injection research. **All additive** — no removals, no breaking changes — so the existing 18 imports of `c0_evidence_contract_types.py` keep working unchanged.

## Web-validated sources

| Source | Primitive |
|---|---|
| Anthropic Citations API (`docs.anthropic.com/en/docs/build-with-claude/citations`) | `char_location` / `page_location` / `block_location` anchors; verbatim quote echo; non-citable `context` field |
| Anthropic Contextual Retrieval (`anthropic.com/news/contextual-retrieval`) | 50–100 token chunk-context blurb; reranker top-150→top-20 |
| Anthropic Context Engineering (`anthropic.com/engineering/effective-context-engineering-for-ai-agents`) | Just-in-time handles, tiered token budget, compaction |
| Anthropic Prompt Injection Defense (`anthropic.com/research/prompt-injection-defenses`) | Retrieved text is data not instruction (already in C0); per-span injection risk score |
| OpenAI File Search (`developers.openai.com/api/docs/guides/tools-file-search`) | `score_threshold`, `ranking_options`, `include=["file_search_call.results"]`, structured `annotations` |
| Microsoft Spotlighting (`arxiv.org/html/2403.14720v1`) | Delimiting → datamarking → encoding (datamarking ASR 50% → <3%) |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.P1, W1.P2, W1.P3 | Citation-grade anchors + verbatim quotes + retrieval-recipe HMAC | 4500 | Existing `CitedSpan` keeps current 5 fields; new fields default-empty | done | New `CitationAnchor` tagged-union; `cited_quote` + `cited_quote_sha256` on `CitedSpan`; `RetrievalRecipe` + `recipe_hmac` on `C0EvidenceContract` |
| W2 | W2.P1, W2.P2 | Spotlighting transform + injection risk scoring | 2500 | Default `spotlight_mode=none` for back-compat | done | `spotlight_mode` literal + `spotlight_token`; `injection_risk_score` + `injection_risk_signals` on `CitedSpan` |
| W3 | W3.P1, W3.P2 | `chunk_context` + per-span retrieval/rerank/support scores | 2000 | Existing `relevance_score` retained, new scores additive | done | `chunk_context` field; `retrieval_score` / `rerank_score` / `support_score` triple on `CitedSpan` |
| W4 | W4.P1, W4.P2 | Per-claim support map + structured disposition | 2500 | `recommended_disposition` becomes a struct, but `claim_confidences` field already exists | done | `PerClaimSupport` (extension of existing `ClaimGroundingConfidence`); `RecommendedDisposition` enum-coded record |
| W5 | W5.P1, W5.P2, W5.P3 | Lineage detail + tiered budget envelope + just-in-time handles | 3000 | Handles signed via existing HMAC key | done | `retrieval_lane` / `lanes_that_recovered_this`; `BudgetEnvelope`; `ExpansionHandle` w/ HMAC |
| W6 | W6.P1 | Verification — full test suite pass | 1000 | All additive, no existing test should break | done | `pytest tests/unit/agentic_core/L3_orchestration/test_c0_evidence_contract.py tests/unit/agentic_core/L3_orchestration/test_c0_hardening.py tests/unit/tools/adg/prompt_assembly/test_c0_bridge_adapter.py` green |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Add `CitationAnchor` tagged-union | `agentic_core/L3_orchestration/types/c0_evidence_contract_types.py` | Tagged union via Literal kind + start/end ints; PDF/text/block anchor parity with Anthropic Citations API | 1500 | done |
| W1.P2 | Extend `CitedSpan` with verbatim quote + anchor list | same file | `cited_quote` and `cited_quote_sha256` default empty; `anchors` defaults to `()` | 1500 | done |
| W1.P3 | Add `RetrievalRecipe` + `recipe_hmac` on contract | same file | Replay primitive — captures plan_hash, embed_model, sparse_index_version, rerank_model_id, max_k, max_hops, filter_set_hash, snapshot_ids | 1500 | done |
| W2.P1 | Add `spotlight_mode` + `spotlight_token` on `CitedSpan` | same file | Default `none` so legacy spans untouched; `datamarked` and `encoded` recommended for untrusted sources | 1500 | done |
| W2.P2 | Add `injection_risk_score` + `injection_risk_signals` on `CitedSpan` | same file | Score in `[0,1]`; signals are Literal codes (regex-driven detector lives downstream) | 1000 | done |
| W3.P1 | Add `chunk_context` (Anthropic Contextual Retrieval) | same file | Default empty; non-citable supporting context, ≤200 chars enforced | 1000 | done |
| W3.P2 | Split scores: `retrieval_score` + `rerank_score` + `support_score` | same file | `relevance_score` retained as legacy alias = `support_score` if not split | 1000 | done |
| W4.P1 | Extend per-claim with `PerClaimSupport` struct | same file | Builds on existing `ClaimGroundingConfidence`; adds `status` literal + `citing_anchor_ids` | 1500 | done |
| W4.P2 | Add `RecommendedDisposition` structured record | same file | `verdict` enum + `primary_reason` code + `secondary_reasons` + `blocking_gaps` + `confidence` | 1000 | done |
| W5.P1 | Add lineage detail on `CitedSpan` | same file | `retrieval_lane` literal + `lane_rank` + `lanes_that_recovered_this` | 1000 | done |
| W5.P2 | Add `BudgetEnvelope` on contract | same file | Tiered: must_use / supporting / contradicts / background / total; `overflow_policy` literal | 1000 | done |
| W5.P3 | Add `ExpansionHandle` with signed HMAC | same file | Just-in-time: handle id + allowed_op + ACL_scope + budget_remaining + handle_hmac | 1000 | done |
| W6.P1 | Bridge adapter pass-through + tests | `tools/adg/prompt_assembly/adapters/c0_bridge_adapter.py`, new `tests/unit/agentic_core/L3_orchestration/test_c0_hardening.py` | Adapter consumes new fields when present; emits replay_extras keys; pure-additive | 1000 | done |

## Gap Register

| Gap | Resolution |
|---|---|
| New types may collide with old field names | All new fields default-empty; existing tests in `test_c0_evidence_contract.py` continue to construct contracts with only the legacy 6 fields. |
| `recipe_hmac` collides with `evidence_hmac` | Different keys (`_RECIPE_HMAC_KEY = b"agentic-core-c0-recipe-v1"`); separately validated. |
| Bridge adapter needs to keep existing replay_extras shape | Adapter only adds new keys (`citation_anchors`, `retrieval_recipe`, `spotlight_mode`, `injection_risk_max`, `chunk_context_count`, `disposition_verdict`) when present. |

## ADG_HOTSPOT_REPORT

| File | Layer | fan_in (imports) | Archetype | Surface | Impact |
|---|---|---|---|---|---|
| `c0_evidence_contract_types.py` | L3 | 0 (no upstream importers via package path; usage via direct `agentic_core.L3_orchestration.types.c0_evidence_contract_types`) | STATE_NODE (canonical evidence record) | State, Observability | Layer mult ×1.75; isolated, additive change is low-risk |
| `c0_bridge_adapter.py` | L_TOOLS | low | CENTRAL_DEPENDENCY (only translator C0→PA) | Execution | Layer mult ×1.0; touched only to pass through new fields |

Hotspot decision: extend the canonical record (`c0_evidence_contract_types.py`) — single edit point — and pass-through in the adapter. No code path forces existing callers to populate new fields.

## ADG_GRAPH_LAYER_EVIDENCE

- **mv_dependency_cone_risk**: queried `c0_evidence_contract_types.py` cone — additive field changes do not alter the cone shape.
- **mv_hotspot_centrality**: file is L3-types leaf, low centrality — change blast radius limited to the adapter.
- **mv_path_criticality_rollup**: critical paths through C0→PA assembly preserved because all new fields default-empty.
- **Semantic edges considered**: `flows_to` (C0→bridge→PA), `reads_from` (bridge reads contract fields), `writes_to` (bridge writes EvidenceBundle).
- **P-views**: `v_p2_duplicated_adapters` not affected; `v_p1_zero_caller_infra` not affected.

## Doctrinal references

- `.windsurf/rules/adg-canonical-invariants.md` §6 layer multipliers
- `.windsurf/rules/plan-location.md` SSOT path
- `.windsurf/rules/constitutional.md` §22 graph-layer evidence
