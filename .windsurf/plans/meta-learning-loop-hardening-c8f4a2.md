# Meta-Learning Loop Hardening — Author-Gate + 10 Intelligence Ledgers

**Plan ID:** `meta-learning-loop-hardening-c8f4a2`
**Status:** DRAFT (awaiting SR_APPROVAL)
**Tier:** T3 (cross-subsystem; touches calibration reporters, ledger consulters, CI gates)
**Date:** 2026-04-24
**Parent ADRs:** ADR-050 (Intelligence Ledger Family)
**Parent rules:** `author-gate-enforcement.md`, `intelligence-ledger-family.md`, `judge-calibration-cadence.md`
**Related plans:** `intelligence-ledgers-ten-a7c3e2.md` (built the ledgers), `meta-learning-confidence-audit-b7c4e1.md` (audited shim surfaces)

---

## 1. Context

The Author-Gate decision ledger and ten intelligence ledgers (`artifacts/ledgers/*.sqlite`) all
record `(prediction, outcome, latency, metadata)` rows. None of them currently close the
**calibration loop** — the path from "what did we predict" to "did the prediction help" to
"adjust the prior next time".

User-named gaps in `.windsurf/scripts/generate_calibration_report.py` (Author-Gate weekly report):

1. `dec_with_precedent` is a **proxy** (`recommended_option_id IS NOT NULL`) — does not
   measure how often a precedent block was actually injected, only that *something* was
   recommended. Source: `generate_calibration_report.py:226-228`.
2. **No metric** joins `precedent.verdict ∈ {strong, suggestive, none}` against
   `decision_outcomes.outcome_label`. The ledger has the data; no script joins it.
3. `confidence_top` is captured per decision but **outcomes are not binned by confidence
   band**. There is no calibration curve telling Cascade "your 0.85s actually succeed
   60% of the time" — which is the natural signal for learning priors.

The **same three gaps exist in all ten intelligence ledgers** — every ledger has rows but
none binds prediction strength to outcome correlation, and none feeds a learned coefficient
back to its consulter.

## 2. Problem Statement

| Loop | Captures prediction | Captures outcome | Joins them | Bins by confidence | Feeds back into next decision |
|---|:---:|:---:|:---:|:---:|:---:|
| Author-Gate (decisions / decision_outcomes) | ✅ | ✅ | ❌ | ❌ | ⚠️ via precedent retrieval only (no score adjustment) |
| `tool_routing` | ✅ | ⚠️ partial | ❌ | ❌ | ⚠️ via consulter, no calibration |
| `refactor_outcome` | ✅ | ✅ via post-commit binder | ❌ | ❌ | ⚠️ via consulter, no calibration |
| `prompt_classifier` | ✅ T0–T3 | ❌ no actual-tier outcome row | ❌ | n/a | ❌ |
| `mcp_invocation` | ✅ latency | ✅ retries / hangs | ❌ | ❌ | ❌ |
| `hotspot_defect` | ✅ | ⚠️ requires 30-day window | ❌ | ❌ | ❌ |
| `deferred_scope_calibration` | ✅ P-band | ✅ days-to-done | ❌ | ❌ | ❌ |
| `guardian_exemption` | ✅ | ❌ no RCA-attribution row | ❌ | n/a | ❌ |
| `progress_eta` | ✅ predicted ms | ✅ actual ms | ❌ | n/a | ❌ |
| `memory_recall` | ✅ recalled entities | ⚠️ session-reference partial | ❌ | n/a | ❌ |
| `test_selection` | ✅ ADG-triaged set | ✅ actual regressions | ❌ | n/a | ❌ |

Net: **0 of 11 loops** currently close prediction → outcome → coefficient adjustment. The
pieces are all on disk; the joins and the writeback are not.

## 3. Layering Invariants (Must Preserve)

- All ledgers remain **SQLite-canonical**, never remote DBs (ADR-050).
- Calibration reports remain **read-only** over the ledgers — no mutation in reporters.
- Threshold/coefficient updates remain **human-gated** (an SSOT-edit decision), but
  the report MUST surface a recommended delta with confidence interval.
- `LedgerConsulter` contract from `ledger-consulter` skill stays pure-read.
- Hash-chain integrity (`row_hash`/`prev_hash`) on Author-Gate ledger preserved.
- Each calibration extension is **additive** to the existing `events`/`decisions` tables —
  no DROP / RENAME columns.

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|-------------------|
| W1 | 1.1–1.4 | Author-Gate calibration: fix the 3 named gaps | ~10k | TODO | `generate_calibration_report.py` emits true precedent-hit count, precedent→outcome correlation table, and per-band calibration curve |
| W2 | 2.1–2.5 | Shared library `tools/calibration/loop_metrics.py` — generic prediction→outcome joiner, band-binned outcome curve, precedent-effect estimator | ~8k | TODO | Library has unit tests; Author-Gate reporter uses it; signature is ledger-agnostic |
| W3 | 3.1–3.10 | Apply library to each of 10 intelligence ledgers via `ops_scripts/calibration/ledger_weekly_report.py` extension; one phase per ledger | ~12k | TODO | Unified weekly report contains a calibration block per ledger; missing-outcome ledgers are explicitly tagged with reason |
| W4 | 4.1–4.3 | Cross-ledger meta-calibration dashboard + auto-Notion writeback + CI gate `check_calibration_completeness.py` | ~6k | TODO | Notion ADR Registry + Anti-Pattern Burndown updated; CI fails if a ledger has >7d of unbound rows |
| W5 | 5.1–5.2 | Verify on real data; document the empirical formula tuning ritual | ~3k | TODO | First weekly report committed under `docs/reports/calibration/<YYYY-Www>.md`; ADR-050 references this plan as evidence of closed-loop |

**Total est:** ~39k tokens. Strictly sequential W1→W2→W3→W4→W5.

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Replace `dec_with_precedent` proxy with real precedent-hit count | `.windsurf/scripts/generate_calibration_report.py` (re-parse `context_fingerprint_json` or join via `precedent` field if extended) | Current schema does not store precedent verdict — may require schema extension `decisions.precedent_verdict` and writer update in `post_cascade_author_gate_capture.py` | 3k | TODO |
| 1.2 | Persist precedent verdict at decision-surface time | `post_cascade_author_gate_capture.py` (write `precedent_verdict ∈ {strong,suggestive,none}` from packet's `precedent.verdict`); schema migration `.windsurf/schemas/decision_ledger.schema.sql` adds nullable column | Schema is additive only; old rows stay NULL and are excluded from new metric until backfilled | 2k | TODO |
| 1.3 | Add precedent → outcome correlation table to weekly report | `generate_calibration_report.py` — new `_precedent_outcome_join()` joining `decisions.precedent_verdict` × `decision_outcomes.outcome_label` | Need ≥30 bound decisions per verdict for statistical signal; below that emit "insufficient sample" | 2k | TODO |
| 1.4 | Add per-band calibration curve | `generate_calibration_report.py` — bin `confidence_top` into [0.72,0.80), [0.80,0.85), [0.85,0.90), [0.90,1.0] and report success rate per band | `selection_latency_ms` already binnable; confidence binning is new. Reliability diagram in markdown table form (no plotting dep) | 3k | TODO |
| 2.1 | Define `LoopMetrics` dataclass + interface | `tools/calibration/loop_metrics.py` (NEW) | Must be ledger-agnostic — accept `(prediction_field, outcome_field, band_extractor)` callables | 1k | TODO |
| 2.2 | Implement `precedent_hit_count()` and `precedent_outcome_correlation()` | same file | Wilson score interval for proportions to handle small-N gracefully | 2k | TODO |
| 2.3 | Implement `band_calibration_curve()` returning `[(band, n, success_rate, ci_low, ci_high)]` | same file | Use Wilson score, not normal approx — small bins are common | 2k | TODO |
| 2.4 | Unit tests `tests/unit/tools/calibration/test_loop_metrics.py` | NEW | Test small-N edge cases, missing-outcome rows, all-success edge case | 2k | TODO |
| 2.5 | Refactor `generate_calibration_report.py` to consume `LoopMetrics` | edit existing | Author-Gate becomes the reference implementation | 1k | TODO |
| 3.1 | Apply to `tool_routing` ledger | `ops_scripts/calibration/ledger_weekly_report.py` + extend writer in `post_cascade_adg_audit.py` to bind outcome (was the grep-fallback actually wrong?) | Outcome signal: did Cascade later have to re-query via ADG? Heuristic — flag if same fingerprint appears with different tool within 24h | 2k | TODO |
| 3.2 | Apply to `refactor_outcome` ledger | extend `post_commit_outcome_binder.py` to write band; reporter consumes | Already has outcome — just needs band binning by predicted P-count delta | 1k | TODO |
| 3.3 | Apply to `prompt_classifier` ledger | extend `pre_prompt_classifier.py` writer to record predicted tier; new outcome binder `post_session_tier_outcome.py` infers actual tier from files-touched / lines-changed | New writer needed; T-tier outcome inference has known noise — accept ±1 tier as "correct" | 2k | TODO |
| 3.4 | Apply to `mcp_invocation` ledger | extend `post_mcp_audit.py` outcome already in `latency_ms`; reporter just needs band binning by latency tier | Trivial — pure reporter change | 1k | TODO |
| 3.5 | Apply to `hotspot_defect` ledger | `hotspot_defect_join.py` already exists; reporter consumes; flag insufficient-window if <30d data | Outcome window is structural, not a bug — surface "ETA-to-signal" line | 1k | TODO |
| 3.6 | Apply to `deferred_scope_calibration` ledger | `deferred_scope_poller.py` already binds days-to-done; reporter joins predicted P-band × actual days; flags miscalibrated bands | If P1 items take >median(P3) days for ≥3 instances → recommend P-band threshold shift | 2k | TODO |
| 3.7 | Apply to `guardian_exemption` ledger | extend `post_write_audit.py` to record exemption-grant; new join with RCA documents (file-based heuristic: was a guardian-exempt file later modified by an RCA-tagged commit?) | Outcome inference is heuristic; document the heuristic in the ledger schema | 2k | TODO |
| 3.8 | Apply to `progress_eta` ledger | `tools/progress_display.py` already records both predicted & actual ms; reporter needs band-binning by op type | Trivial — pure reporter change | 1k | TODO |
| 3.9 | Apply to `memory_recall` ledger | extend `post_cascade_writeback_audit.py` to record recalled entity IDs; outcome binder cross-references session-end mention list | Session-reference detection requires post-response text scan; accept noisy signal | 1k | TODO |
| 3.10 | Apply to `test_selection` ledger | `post_run_audit.py` records ADG-triaged set; outcome = pytest result; reporter computes precision/recall vs full-suite outcome (sampled) | Full-suite sampling cost — run full suite weekly, not per session | 2k | TODO |
| 4.1 | Cross-ledger dashboard section in `ledger_weekly_report.py` | edit | Single table: ledger × precedent-hit-rate × outcome-correlation × top-band success | 2k | TODO |
| 4.2 | Auto-Notion writeback of weekly report into `MCP Registry` notes + `Anti-Pattern Burndown` calibration row | new `post_calibration_notion_writeback.py` | Writes to two databases; uses `API-post-page` per AGENTS.md routing rules; idempotent via report-week dedup key | 2k | TODO |
| 4.3 | CI gate `ops_scripts/ci/check_calibration_completeness.py` — fail if any ledger has >7d of unbound rows AND has a defined outcome binder | NEW | Hard-fail variant requires green-light env var; soft-warn variant default | 2k | TODO |
| 5.1 | Run end-to-end on current week; commit first real report | `docs/reports/calibration/2026-W17.md` | Empirical bands may be too narrow with low N — accept "insufficient sample" rows | 1k | TODO |
| 5.2 | Document the empirical-tuning ritual in `author-gate-enforcement.md` and `intelligence-ledger-family.md` | rule edits | When does report's recommended threshold delta get applied? Author-Gate decision required for delta ≥0.05; deltas <0.05 are auto-applied via SSOT edit | 2k | TODO |

## 6. Rollback Checkpoints

| After wave | Rollback trigger | Rollback action |
|------------|-----------------|-----------------|
| W1 | Reporter crashes on real data | Revert reporter; keep schema migration (additive, harmless) |
| W2 | Library API churn / wrong signature | Revert library; W1 reporter falls back to inline implementation |
| W3 | Any ledger writer crashes | Revert that single phase; other ledgers continue (writer changes are independent) |
| W4 | Notion writeback creates duplicate rows | Disable writeback; CI gate stays in soft-warn mode |
| W5 | First report shows pathological data | Investigate (data bug) before tuning thresholds; do NOT auto-apply |

## 7. Author-Gate Decisions Deferred to Execution

1. **Phase 3.3 (Author-Gate)** — How to infer actual T-tier from a session? Candidates: files-touched count, lines-changed, layer-breadth, presence of architecture-decision phrases. Author-Gate will surface scored options at execution time.
2. **Phase 5.2 (Author-Gate)** — Auto-apply threshold deltas <0.05 vs always-human-gate. Constitutional rule §6 leans human-gate; this Author-Gate decides whether reliability-curve-driven micro-deltas are an exception.

## 8. Non-Goals (explicit)

- NOT changing the routing constants `surface_threshold=0.72` etc. as part of this plan — only making them empirically observable
- NOT replacing `confidence_score` author-by-Cascade with an algorithmic score — confidence remains authored; the loop only measures whether it's well-calibrated
- NOT introducing a TSDB or external metrics system — stays SQLite-canonical
- NOT touching the runtime HITL system in `agentic_core/L5_safety/` — that has its own ADR-023 calibration path

## ADG_HOTSPOT_REPORT

| Rank | Node | Layer | Fan-in | Archetype | Surfaces | Wave |
|------|------|-------|:------:|-----------|----------|------|
| 1 | `.windsurf/scripts/generate_calibration_report.py` | L_OPS | 1 (workflow `/author-gate-calibration-report`) | ORCHESTRATOR | Observability | W1, W2 |
| 2 | `.windsurf/schemas/decision_ledger.schema.sql` | L_OPS | high (3 writers + 1 reader + integrity verifier) | STATE_NODE | State, Observability | W1.2 |
| 3 | `.windsurf/scripts/post_cascade_author_gate_capture.py` | L_OPS | 1 (post-hook) | CENTRAL_DEPENDENCY | Observability | W1.2 |
| 4 | `tools/ledgers/schema_registry.py` (LEDGER_REGISTRY) | L_TOOLS | 10 (every consulter + reporter) | CENTRAL_DEPENDENCY | State | W2, W3 |
| 5 | `ops_scripts/calibration/ledger_weekly_report.py` | L_OPS | 1 (weekly job) | ORCHESTRATOR | Observability | W3, W4 |
| 6 | 10× `.windsurf/scripts/post_*_audit.py` writers | L_OPS | 10× independent | STATE_NODE | Observability, Write | W3.1–W3.10 |
| 7 | `tools/calibration/loop_metrics.py` (NEW) | L_TOOLS | will be 11 (Author-Gate + 10 ledgers) | CENTRAL_DEPENDENCY | State | W2 |

Layer multiplier: L_OPS / L_TOOLS sit outside L0–L6 gravity. Impact rationale = governance
+ observability rather than runtime safety. Surface intersection: **Observability** (every
phase) + **State** (W1.2, W2, W3) — drives wave ordering.

## ADG_GRAPH_LAYER_EVIDENCE

| MV / Semantic edge / P-view | Application in this plan |
|---|---|
| `mv_hotspot_centrality` | W2.1 — confirm `loop_metrics.py` becomes a high-fan-in node before committing API |
| `mv_graph_reverse_dependency_hotspots` | W1.2 — full fan-in on `decisions.precedent_verdict` before schema migration |
| `mv_dependency_cone_risk` | W3.* — bound blast radius of each writer extension before edit |
| `mv_graph_chokepoint_bridges` | W4.3 — confirm `check_calibration_completeness.py` sits at a chokepoint, not a leaf |
| semantic edge `imports` | W2 — primary primitive for verifying library is consumed |
| semantic edge `writes_to` | W1.2, W3.* — ensure each writer mutates only its own ledger |
| semantic edge `reads_from` | W4.1 — confirm dashboard reads (no writes) every ledger |
| P-view `v_p1_zero_caller_infra` | W3 — detect any ledger consulter with zero callers (signals dead loop) |
| P-view `v_p3_isolated_experimental` | W2.1 — confirm new `loop_metrics.py` does not land here |

## 9. Constitutional Compliance Check

| Rule | Status |
|------|--------|
| §1 No PowerShell | ✅ All subprocess calls argv + shell=False |
| §15 Precise exceptions | ✅ Each writer extension catches `sqlite3.Error`, `OSError`, `json.JSONDecodeError` only |
| §16 Progress bar | ✅ Library N>1000 paths get `ProgressReporter` |
| §17 Memory lifecycle | ✅ W4.2 + W5.2 update memory entities `ProceduralPattern:CalibrationLoopHardening` and `ArchitecturalInvariant:LoopMetricsAPI` |
| §18 No hidden scope expansion | ✅ Bounded to 11 loops; runtime HITL explicitly excluded (§8) |
| §22 ADG graph layer primary | ✅ Both mandatory sections present |
| §23 ADG canonical invariants | ✅ Layer multipliers documented; static vs runtime ADG separation respected |
| §26 MCP serialization | ✅ Notion writeback (W4.2) is one MCP call per response |

## 10. References

- ADR-050: `docs/architecture/adr/ADR-050-intelligence-ledger-family.md`
- Parent plan (built ledgers): `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`
- Author-Gate calibration script: `.windsurf/scripts/generate_calibration_report.py`
- Unified report: `ops_scripts/calibration/ledger_weekly_report.py`
- Schema SSOT: `.windsurf/schemas/decision_ledger.schema.sql`, `.windsurf/schemas/ledger_base.schema.sql`
- Constitutional rules: §22 graph-layer, §23 canonical invariants
