---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\post-wave10-roadmap-a1e7f2.md'
original_relative_path: 'post-wave10-roadmap-a1e7f2.md'
source_sha256: 7250be6c10eb488d58c22fe437665616a0cd7cb81d47d73e8aef34b0cfe55bf3
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Post-Wave-10 Roadmap — Remaining Work Plan

**Status:** Active
**Created:** 2026-04-24 after Wave 10 backlog triage
**Scope:** Enumerate all remaining genuinely-blocked work surfaced during Waves 9-10 stale-backlog sweep, sequence by dependency + impact, assign to concrete wave slots.

## Context

Waves 1-8 executed concrete refactoring + feature work. Waves 9-10 were **backlog-integrity waves** — no LOC added, but 6 rows closed (3 already-landed verifications, 3 scope/dep blocks) and every remaining top-P2 row now has explicit reopen conditions documented in Notion.

The Blocked queue contains **~20 rows** that fall into 5 dependency clusters. The **`grounding_need_score` classifier (W3.P1)** is the keystone — its landing unblocks 4 downstream rows at ~zero marginal cost.

## Wave Summary Table

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W11** | W3.P1 + W1.P2 | Grounding-need-score classifier keystone | 22k 🟡 | Labeled eval set of ≥500 replay traces exists | Ready | Classifier produces [0,1] score; replay precision ≥0.75 at 0.70 threshold; `grounding_need_score` field populated on RoutingFeatureVector for live L0 traces |
| **W12** | W1.P1 + W5.P2 + W1.P1-consumers | Classifier consumer wiring (depends on W11) | 5k 🟢 | W11 classifier online | Blocked on W11 | L1 plan builder emits work_class + freshness_class + grounding_required; L0 routing reads grounding_need_score from live feature vector; tests green |
| **W13** | W3.P2 | Multi-signal R5 with labeled reason codes | 18k 🟡 | W11 provides 5th signal; existing 4 triggers (circuit-breaker / OOD / toxicity / token-budget) already emit typed errors | Ready (but larger scope w/o W11) | ≥5 abstain triggers with closed reason_codes enum entries; per-trigger precision measured on replay; abstain_contract.py emits structured reason tuples |
| **W14** | EQ-12b.1 | Apply-patch multi-file batching executor | 10k 🟡 | ADR-TBD on patch-envelope format; UWG write surface available | Needs author-gate on envelope format | Patch-envelope parser; all-or-nothing commit semantics; integration with assert_no_persistent_write; ≥10 tests covering rollback, partial-failure, idempotency |
| **W15** | ADR-024 Part B | SURFACE_OVERRIDE manifest + ratchet ceiling | 8k 🟢 | ADR-024 OQ#1/OQ#2 resolved; W5 re-scope complete | Blocked on author-gate | `agentic_core/adg/severity_bands.py` SURFACE_OVERRIDE table + `tools/generate/validation/gates.py` ratchet ceiling bump; single commit; full burndown re-run green |
| **W16** | W2.P2 | Per-namespace threshold calibration | 15k 🔴 | ≥30 days replay traces per namespace; L4_state/config/routing_calibration.yaml accepts namespace overrides (already plumbed) | Blocked on trace volume | Per-namespace threshold YAML block; calibration notebook reproducible; precision delta ≥+5% vs default thresholds on held-out set |
| **W17** | GUARDIAN-TOKEN-SSOT + ssot-sweep GAP-A + streamline-constants GAP-4 | Tech-debt burndown | 30k 🔴 | No dependencies; pure mechanical work | Ready (opportunistic) | (a) 19 singleton guardian tokens triaged + promoted or rewritten; (b) 1300+ malformed bare-marker comments auto-fixed; (c) 34 grandfathered hardcoded-exclusion sites moved to SSOT; (d) 10 `_constants.py` direct imports migrated to streamlined territories module |
| **W18** | Gemini-E2E-smoke | Gemini live E2E smoke on Vertex | 4k 🟢 | ANTHROPIC_API_KEY + GOOGLE_APPLICATION_CREDENTIALS provisioned | Vendor-blocked | Live Gemini call returns valid tool-use payload; streaming chunks ordered; non-2xx responses logged with trace-id |

**Legend**: 🟢 ≤8k comfortable · 🟡 8-20k moderate · 🔴 >20k split candidate

## Phase-Level Summary Table

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W11.a | Labeled eval set curation | `tests/data/grounding_eval/*.jsonl` (new) | Requires manual labeling pass on ~500 traces | 6k | Ready |
| W11.b | Classifier implementation | `agentic_core/L3_orchestration/reasoning/grounding_need_classifier.py` (new) | Feature engineering: query-term count, retrieval-count, evidence-coverage, freshness-gap | 10k | Blocked on W11.a |
| W11.c | L1 producer wiring | `agentic_core/L1_cognition/reasoning/feature_vector_builder.py` | Injection point into existing L1 plan builder | 6k | Blocked on W11.b |
| W12.a | L0 consumer reads grounding_need_score | `agentic_core/L0_routing/reasoning/execution_orchestrator.py` (already supports field when present) | Trivial wiring | 2k | Blocked on W11 |
| W12.b | work_class taxonomy | `agentic_core/L0_routing/types/routing_artifact_types.py` (new enum beside RouteReasonCode) | Closed-set enum: summarize/compare/analyze/act/factual | 3k | Blocked on W11 |
| W13.a | Reason-code taxonomy extension | `routing_artifact_types.py::RouteReasonCode` | Already has R5_* entries for 4 triggers; add 5th (grounding_need_score) | 2k | Blocked on W11 |
| W13.b | Abstain emitter | `agentic_core/runtime/contracts/abstain_contract.py` | Emit structured `(trigger, reason_code, signal_value)` tuples | 8k | ✅ Done 2026-04-24 (already implemented: plan_abstain_multi_signal with 6 triggers, closed R5_REASON_CODES enum, 22/22 tests green) |
| W13.c | Replay precision harness | `tests/integration/abstain/test_r5_trigger_precision.py` (new) | Per-trigger precision measurement | 8k | Blocked on W13.b |
| W14.a | Patch-envelope ADR | `docs/architecture/adr/ADR-048-apply-patch-envelope.md` | Author-Gate on format (JSON patch vs git diff vs custom) | 2k | ✅ Done 2026-04-24 (ADR-048 Accepted, 3 Q's resolved) |
| W14.b | Parser + validator | `agentic_core/L2_execution/writers/patch_envelope.py` | All-or-nothing commit semantics | 4k | ✅ Done 2026-04-24 (parser + validator + executor, 20/20 tests green) |
| W14.c | Integration + tests | `tests/unit/agentic_core/L2_execution/writers/test_patch_envelope.py` | Rollback-on-mid-batch-failure edge cases | 4k | ✅ Done 2026-04-24 (included in W14.b delivery; mid-batch rollback verified via monkeypatched write_text) |
| W15 | SURFACE_OVERRIDE + ratchet | `severity_bands.py` + `gates.py` | ADR-024 OQs resolved 2026-04-24; P1_RATCHET_POLICY_V2 env-flag default OFF | 8k | ✅ Done 2026-04-24 (SURFACE_OVERRIDE table + effective_severity/effective_band helpers + feature-flagged ratchet bump + 39/39 tests green) |
| W16 | Per-namespace calibration | `config/routing_calibration.yaml` override block + calibration notebook | Needs ≥30d replay data | 15k | Blocked on data |
| W17.a | Guardian-token lint report | `artifacts/guardian_lint/baseline_2026-04-24.txt` (9.7KB) | Author-Gate 2026-04-24 chose lint-only mode; existing tools/debug/_w5_token_inventory.py already produces the report | 12k→2k | ✅ Done 2026-04-24 (baseline captured, no new tool needed) |
| W17.b | Non-canonical token triage | `agentic_core/adg/artifact/multi_writer.py` L557-569 | Author-Gate 2026-04-24 promoted 4 high-volume tokens (magic-config/type-erasure/global-mutation/path-string) = 1,076 sites compliant; 14 low-mid-volume + 9 singletons + 1300 malformed-bare-markers deferred to W17.b-tail | 10k→1k | ✅ Done 2026-04-24 (partial: high-volume cohort) |
| W17.c | ssot-sweep GAP-A | 34 hardcoded-exclusion sites | Mechanical migration | 6k | ✅ Done 2026-04-24 (gate reports baseline=0; 34 sites absorbed into prior waves) |
| W17.d | streamline-constants GAP-4 | n/a (stale) | Claim of "90 files, 155 dangling imports, 12 lost symbols" was based on pre-W6 snapshot. Verified 2026-04-24: `agentic_core.L0_routing.config.structure_blueprint_data` replacement module exists with 20+ canonical symbols; zero live `from X.structure_blueprint import Y` statements in prod code (19 grep hits, all in docstrings/comments). No ADR-026 needed. | n/a | ✅ Done 2026-04-24 (archaeology already complete in prior waves; roadmap row was stale) |
| W17.b-tail | Guardian marker hygiene | `.windsurf/rules/approval-exception-policy.md` + `tools/guardian/bulk_fix_bare_markers.py` (new) + 246 .py files | Author-Gate 2026-04-24 (Option B, confidence=0.82). Triage revealed original "1892 bare-markers" estimate was wrong: actual state = 1926 long-form + 1757 short-form exemptions (ALL valid) + 633 bare review-notes (misclassified as exemptions). Scanner regexes already accepted short-form; rule prose updated to match. Bulk rename `# guardian: <prose>` → `# review: <prose>` for 567 sites. Zero exemption directives touched. | 8k | ✅ Done 2026-04-24 (rule + CLI + 31 tests + 567 site rewrites + post-verify=0 bare remaining) |
| W18 | Gemini live smoke | `tests/integration/gemini/test_live_e2e.py` (new) | Needs Vertex creds on CI | 4k | Vendor-blocked |

## Gap Register

- **Token estimates**: All estimates derived from 2026-04-24 `token_estimator.py` run on equivalent-scope precedent waves. Treat as ±20%.
- **W11.a labeled eval set**: The 500-trace labeling pass is the single largest time cost in W11. Consider: can partial labels (e.g., 100 traces) unlock W11.b with higher-variance precision? **Open question.**
- **W14.a patch-envelope format**: JSON patch (RFC 6902) vs. git unified-diff vs. custom contract. Author-Gate required before W14.b starts.
- **W16 data volume**: ≥30 days replay traces per namespace may not exist for low-traffic namespaces; calibration may degrade to single-namespace-fits-all until volume accrues.

## Out-of-Scope (explicit deferrals)

- **Full BGE-M3 multi-vector embeddings** — W5 ChromaDB hardening optional path; defer until hybrid dense+sparse retrieval proves insufficient at P90 recall.
- **Reranker production rollout** — W4 hook exists; production wiring deferred until W11 classifier provides signal for "when to rerank".
- **ADG runtime snapshot consolidation** — separate plan under `docs/wave_h/` tracking.

## ADG_GRAPH_LAYER_EVIDENCE

Derived from Waves 9-10 investigation (ADG snapshot `adg_indexed_04202026_1523.sqlite`, Redis hot cache warm):

- **`adg_nodes_by_layer("L0")`**: 23 nodes — RouteReasonCode (landed W1b.P1), L0RouteContract, execution_orchestrator confirmed as consumer of grounding_need_score.
- **`adg_edge_fanin(tgt_id=<C0EvidenceContract>, relation_type="imports")`**: fan_in=2, confirmed C0.coverage_score field reaches ~4 consumers transitively (shadow_eval_runner, completeness_snapshot_registry, routing_calibration_metrics, retrieval_coverage_scorer).
- **`v_p0_write_bypass_uwg`**: zero violations after W14 would need explicit UWG integration — apply-patch MUST go through UWG surface.
- **Semantic edge `flows_to`**: grounding_need_score flow path is `L1 feature_vector_builder → RoutingFeatureVector → L0 execution_orchestrator → abstain_contract` (4-hop, no shortcut).

**ADG Provenance**: backend=redis_cache, snapshot=adg_indexed_04202026_1523.sqlite

## Execution Order (recommended)

1. **W11** (keystone) — unblocks W12 + W13 partial
2. **W17** (tech debt, parallel — any idle session) — no dependencies
3. **W15** (ADR-024 Part B — needs author-gate) — small, high-signal
4. **W13** (multi-signal R5) — builds on W11
5. **W12** (trivial wiring) — zero-risk after W11
6. **W14** (apply-patch) — needs envelope ADR first
7. **W16** (calibration) — needs data accrual
8. **W18** (Gemini E2E) — vendor-gated

## Total Estimated Work

- **Ready + bounded**: W11.a+W15+W17.c+W17.d ≈ 22k tokens
- **Blocked on single dep**: W12 + W13.a + W14.a ≈ 7k tokens
- **Large-scope T3**: W11.b+c, W13.b+c, W14.b+c, W16 ≈ 55k tokens
- **Tech debt long tail**: W17.a+b ≈ 22k tokens
- **Grand total remaining**: ~110k tokens across ~8 wave slots
