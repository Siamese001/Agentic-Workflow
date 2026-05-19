# Author-Gate Hardening — Confidence Calibration, Outcome Loop, Spine Integration, UI Signal

**Plan ID:** `author-gate-hardening-a3b8f2`
**Status:** � Completed — all 5 waves shipped 2026-05-03 (tests 9/9 green, smoke-tested end-to-end)
**Owner:** Cursor Agent (author-loop)
**Constitutional:** §6 (Author-Gate), §29 (closed-loop router), §30 (capture health), §17 (memory lifecycle)
**Related:** `author-gate-enforcement.md`, `author-gate-decision-points.md`, `closed-loop-router-enforcement.md`, ADR-050 (intelligence-ledger-family)
**Scope:** Architecture + mechanism design only. **No code changes in this plan** — this is a gap-analysis + implementation design document. Code waves are scaffolded but gated behind Author-Gate approval per §6.

---

## 1. Executive Summary

The Author-Gate (harness author-loop decision gate, distinct from runtime HITL per ADR-023) is operationally functional:

- Packet emitter `.cursor/skills/author-gate-packet-builder/emit_packet.py` produces AG-10 compliant packets with didactic fields.
- Capture hook `.cursor/scripts/post_cursor_agent_author_gate_capture.py` drains `DECISION_CAPTURED:` markers into SQLite (`refactor_decision_ledger.sqlite`).
- Schema carries calibration seeds: `confidence_top`, `confidence_dominance_gap`, `override_vs_recommendation`, `selection_latency_ms`, `principle_at_stake`, `precedent_verdict`, `exit_criteria_json`.
- Precedent injection via `refactor-decision-memory` skill is wired.

**But the loop is open.** Six gaps reduce the gate to a compliance artifact rather than a learning system:

| # | Gap | Consequence |
|---|---|---|
| G1 | Raw LLM confidence used as single signal — no calibration, no validation | Research (Galileo, Anthropic, arXiv 2601.15778) shows 0.90–1.00 range holds 42% of errors. Current packet scores are token-probability proxies. |
| G2 | `decision_outcomes` table exists but **no writer** | Every decision is captured; zero are scored. `promote_to_pattern`, `regression_found`, `rollback_required` are all NULL in prod. No feedback = no learning. |
| G3 | Author-Gate is **not on the agentic spine** — emits no `ROUTER_DECISION:` / `emit_ledger_event`, has no exit-gate criteria enforced post-execution | Violates §29 closed-loop parity. Cannot participate in Wilson-CI promotion (§6D) or regret accounting (L6/regret). |
| G4 | UI (`ask_user_question`) shows **labels only** — recommended option, confidence bands, precedent verdict, "what would flip" are hidden from the approver | Reviewer attention burned on parsing; recommendation signal discarded. Galileo: "reviewer attention is your scarcest resource." |
| G5 | Meta-learning pipeline stops at precedent injection — no reliability diagram, no Brier-score tracking, no bandit update, no per-principle drift | Decisions accumulate but the gate does not get smarter. `run_hitl_consumer.py` exists for runtime HITL only. |
| G6 | Metrics captured are narrow — latency + gap + override. **Missing:** decision-class distribution, reviewer-fatigue proxies, FP rate against outcomes, principle-drift, time-to-outcome, precedent-agreement | Cannot answer "is the gate firing at the right threshold?" or "is class X drifting?" |

**This plan proposes five waves that close G1–G6 end-to-end.** Wave 0 is documentation + Author-Gate approval; Waves 1–4 are implementation. Total estimated scope: ~18 files, 4 new SQLite columns, 2 new tables, 1 new consumer CLI, 1 UI-helper skill.

---

## 2. External-Research Anchors

Synthesized from: Anthropic (`anthropic.com/engineering/demystifying-evals-for-ai-agents`, `anthropic.com/research/building-effective-agents`), Galileo HITL oversight guide, `dev.to/taimoor-ijaz` HITL patterns, arXiv 2601.15778 (Agentic Confidence Calibration), Microsoft Learn HITL connector, codeongrass.com mobile approval gates, RLHF literature (arXiv 2504.12501).

### R1. Confidence-score trap (near-universal finding)

> "Never use a single LLM confidence score as your gating mechanism. Weight the LLM confidence at 15% or less." — dev.to (empirical table: 42% of errors live in 0.90–1.00 band)

Corollary (Galileo): **neural networks exhibit systematic overconfidence** — raw softmax/verbalized confidence without calibration produces "systematic over-autonomy in incorrect predictions."

### R2. Multi-signal routing (all sources agree)

Pair confidence with **≥2 independent signals**:

- **Rule-based validators** (blast-radius, layer-gravity, ADG hotspot rank)
- **Historical accuracy** (precedent verdict from same decision class)
- **Cross-checker** (LLM-as-judge with "Unknown" escape per Anthropic demystification)

### R3. Calibration, not raw score

arXiv 2601.15778 distinguishes:

- **Verbalized confidence** (current state — "Confidence: 85%")
- **LastStep token-probability**
- **Trajectory-aware calibration** (features: number of tool calls, revision count, precedent match)

Production systems use isotonic regression or Platt scaling over historical outcomes to map raw score → calibrated probability. Brier score and ECE (Expected Calibration Error) are the scorecards.

### R4. Outcome loop is the learning engine

Anthropic "Demystifying evals" + RLHF: the decision + outcome pair is the training signal. Without outcome capture (did the selected option land without regression? did it get rolled back?) there is no way to calibrate, no way to update precedent, no way to improve.

### R5. Reviewer UX is the scarcest resource

Galileo + dev.to + codeongrass all converge: **review dashboards must show context** (diff preview, confidence band, precedent match, "what would flip"), support **keyboard shortcuts**, and surface **queue state**. Current `ask_user_question` shows labels + short descriptions; the recommendation signal and precedent verdict are absent from the UI surface.

### R6. Structured decision records (Microsoft Learn HITL)

> "Ensure that the human step records a structured decision (approve/reject plus reason) to avoid freeform comments that are hard to audit."

Current ledger captures `selected_option_id` + `selection_rationale` (free text). Missing: **reason code enum** (`override_recommendation`, `insufficient_precedent`, `blast_radius_too_high`, `principle_shift`, `test_strategy_change`), which is the pivot key for class-level calibration.

---

## 3. Gap → Remediation Map

| Gap | Remediation | Wave |
|---|---|---|
| G1 — raw confidence | Multi-signal confidence vector: `{verbalized, precedent_agreement, blast_radius_penalty, hotspot_penalty, rule_violation_penalty}`; calibrated via isotonic regression over `decision_outcomes`; Brier score + ECE tracked per decision_type. | W2 |
| G2 — outcome writer absent | New `tools/capture/outcome_writer.py` + Git post-commit hook. Scans for `DECISION_OUTCOME:` markers; writes to `decision_outcomes`; ties to `exit_criteria_json`. | W1 |
| G3 — not on spine | Emit `ROUTER_DECISION: layer=author_gate, ...` marker per §29. Register as synthetic router in `closed-loop-router-enforcement.md`. Exit-gate criteria = `exit_criteria_json` rendered as acceptance tests run at outcome time. | W3 |
| G4 — UI signal loss | New skill `author-gate-ui-renderer` that, pre-`ask_user_question`, emits a condensed recommendation card (Recommended / Why / Precedent verdict / Confidence band / What would flip). Options carry structured descriptions with inline gold-star + confidence band pill. | W3 |
| G5 — no meta-learning | New `tools/meta_learning/author_gate_consumer.py` parallel to `run_hitl_consumer.py`: scores the Author-Gate ledger, updates a per-class Thompson bandit (decision_type × decision_class_reason), emits weekly calibration report `docs/reports/author-gate/<YYYY-Www>.md`. | W4 |
| G6 — narrow metrics | Additive schema: `decisions.reason_code`, `decisions.adg_hotspot_rank`, `decisions.blast_radius_hops`, `decisions.surface_intersections_json`; new table `decision_signals` (one row per signal per decision). | W1 |

---

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | P0.1 | Plan authored, Author-Gate opened, Notion row created | ~8k | No code; Author-Gate approval required before W1 | ✅ DONE | Plan file present; Notion Plans row created; Author-Gate packet emitted |
| W1 | P1.1, P1.2, P1.3 | Schema + outcome writer + reason-code enum | ~12k | W0 approved; additive migration only | ✅ DONE | New columns present; outcome writer CLI smoke-tested; reason enum in emit_packet |
| W2 | P2.1, P2.2, P2.3 | Multi-signal confidence + calibrator + Brier/ECE | ~15k | ≥50 closed outcomes exist (else cold-start with uniform prior) | ✅ DONE | `confidence_calibrated` column populated; calibration report renders |
| W3 | P3.1, P3.2 | Spine integration (ROUTER_DECISION emit) + UI renderer skill | ~10k | §29 enforcement running | ✅ DONE | ROUTER_DECISION rows present for author_gate layer; UI card emitted before ask_user_question |
| W4 | P4.1, P4.2 | Meta-learning consumer + weekly calibration report + bandit-backed precedent weighting | ~12k | W1–W2 outcomes flowing ≥2 weeks | ✅ DONE | Weekly report lands at `docs/reports/author-gate/<YYYY-Www>.md`; bandit state visible in next packet |

Total: ~57k tokens across 5 waves. No single wave exceeds 15k.

---

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P0.1 | Plan + Author-Gate approval | `.cursor/plans/author-gate-hardening-a3b8f2.md`, Notion Plans row | Gate on §6 (no implementation before approval) | 8k | 🟡 |
| P1.1 | Additive schema: `reason_code`, `adg_hotspot_rank`, `blast_radius_hops`, `surface_intersections_json`; new `decision_signals` table | `post_cursor_agent_author_gate_capture.py` (DDL + idempotent ALTER), `tools/capture/queue_to_ledger.py` | SQLite lacks `ADD COLUMN IF NOT EXISTS` — must PRAGMA-probe; FTS5 content table re-sync | 5k | ⚪ |
| P1.2 | Outcome writer `tools/capture/outcome_writer.py` + `DECISION_OUTCOME:` marker + Git post-commit hook | `tools/capture/outcome_writer.py` (new), `tools/capture/append_marker.py` (add OUTCOME prefix), `.githooks/post-commit.sample` | Commit → decision linkage via `decision_id` in commit trailer or branch-matching fallback | 4k | ⚪ |
| P1.3 | Reason-code enum wired through `emit_packet.py` + capture regex | `.cursor/skills/author-gate-packet-builder/emit_packet.py`, `post_cursor_agent_author_gate_capture.py` | Back-compat for existing in-flight packets without `reason_code` | 3k | ⚪ |
| P2.1 | Multi-signal confidence vector construction in `emit_packet.py` | `emit_packet.py`, `precedent_injector.py`, new `signal_collector.py` | Signals: verbalized, precedent_agreement (already via precedent_verdict), blast_radius_penalty (from ADG), hotspot_penalty (from ADG mv_hotspot_centrality), rule_violation_penalty (from rule registry) | 6k | ⚪ |
| P2.2 | Isotonic calibrator `ops_scripts/calibration/author_gate_calibrator.py` fit nightly over `decision_outcomes` | `ops_scripts/calibration/author_gate_calibrator.py` (new) | Cold-start with uniform prior when n<30 per class; sklearn isotonic regression or hand-rolled; Brier/ECE metrics | 5k | ⚪ |
| P2.3 | Calibrated score persisted as `decisions.confidence_calibrated` + per-class reliability diagram written to `artifacts/author_gate/reliability_<YYYY-Www>.json` | Schema migration + calibrator writeback | Versioning: calibrator version stamped on each row so historical analysis can re-fit | 4k | ⚪ |
| P3.1 | Spine integration: emit `ROUTER_DECISION: layer=author_gate, ...` at packet-surface time + `emit_ledger_event` | `emit_packet.py`, `post_cursor_agent_router_decision_audit.py` (register author_gate layer), `closed-loop-router-enforcement.md` (document) | Synthetic router: author_gate is not in the canonical 10; must be declared in the rule and the audit's allowlist | 5k | ⚪ |
| P3.2 | New skill `author-gate-ui-renderer` — composes condensed card before `ask_user_question` | `.cursor/skills/author-gate-ui-renderer/SKILL.md` (new), supporting template | Card fields: Recommended option, Confidence band (🟢≥0.85 / 🟡 0.72–0.85 / 🔴<0.72), Precedent verdict, "What would flip" top-2, 1-line principle-at-stake | 5k | ⚪ |
| P4.1 | Meta-learning consumer `tools/meta_learning/author_gate_consumer.py` | New CLI analogous to `run_hitl_consumer.py`; scores ledger, updates per-class Thompson bandit at `.cursor/state/refactor_decisions/bandit_state.json` | Bandit cell = (decision_type, reason_code); Beta posterior updated on outcome = promote_to_pattern OR regression_found | 6k | ⚪ |
| P4.2 | Weekly calibration report `ops_scripts/calibration/author_gate_weekly_report.py` → `docs/reports/author-gate/<YYYY-Www>.md` | New script; renders: decision counts by class, FP rate vs outcomes, Brier score trend, flip-readiness per class, top-5 overrides, precedent-agreement % | Zero-data weeks render "insufficient data" row, not crash | 5k | ⚪ |

---

## 6. Confidence-Score Design (G1 detail)

**Current:** `confidence_score ∈ [0,1]` per candidate in packet JSON, hand-provided by Cursor Agent.

**Proposed vector** (per candidate, stored in `decision_signals` table, one row per signal):

```
signals = {
  verbalized:              <Cursor Agent's own 0..1>,           # weight 0.15
  precedent_agreement:     <0|0.5|1 from lookup>,         # weight 0.30
  blast_radius_penalty:    <1 - min(hops/5, 1)>,          # weight 0.20
  hotspot_penalty:         <1 - mv_hotspot_rank/top_N>,   # weight 0.15
  rule_violation_penalty:  <1 if no §8/§22/§28 flag>,     # weight 0.20
}
raw_score = Σ (weight_i × signal_i)
calibrated = isotonic_fit[decision_type](raw_score)        # after 30+ outcomes per class
```

**Gating:** thresholds unchanged from `author-gate-enforcement.md` (filter 0.72, dominance ≥0.12, strong ≥0.85) but applied to **calibrated** score. During cold-start (<30 outcomes), calibrated := raw and a `COLD_START` tag is attached to the packet.

**Scorecards (persisted weekly):**

- **Brier score** per decision_type: `mean((calibrated_i − outcome_i)²)`
- **ECE (Expected Calibration Error):** 10 bins, weighted abs gap between bin mean confidence and bin outcome rate
- **Reliability diagram:** `artifacts/author_gate/reliability_<YYYY-Www>.json`
- **Flip-readiness:** per class, fraction of decisions where top score − 2nd score ∈ [0.08, 0.15] (near-indifference band — signal that the rubric needs refinement)

---

## 7. Metrics & Persistent-SQLite Additions (G6 detail)

### 7.1 New columns on `decisions`

| Column | Type | Source | Why |
|---|---|---|---|
| `reason_code` | TEXT | emit_packet | Auditable pivot (R6); enum: `override_recommendation`, `insufficient_precedent`, `blast_radius_too_high`, `principle_shift`, `test_strategy_change`, `dependency_risk`, `deletion_risk`, `other` |
| `confidence_calibrated` | REAL | calibrator | Post-isotonic score actually gated against |
| `calibrator_version` | TEXT | calibrator | e.g. `iso_v1_2026w18` — enables re-fit analysis |
| `adg_hotspot_rank` | INTEGER | ADG mv_hotspot_centrality | Structural criticality of scope |
| `blast_radius_hops` | INTEGER | ADG blast_radius | Risk proxy |
| `surface_intersections_json` | TEXT | ADG 5-surfaces | Execution/Write/Security/State/Observability intersections |
| `decision_class_tier` | TEXT | triage | T1/T2/T3 tier |

### 7.2 New table `decision_signals`

One row per signal per candidate per decision:

```sql
CREATE TABLE decision_signals (
  signal_id       INTEGER PRIMARY KEY AUTOINCREMENT,
  decision_id     TEXT NOT NULL REFERENCES decisions(decision_id),
  option_id       TEXT NOT NULL,
  signal_name     TEXT NOT NULL,   -- verbalized, precedent_agreement, blast_radius_penalty, ...
  signal_value    REAL NOT NULL,
  signal_weight   REAL NOT NULL,
  signal_source   TEXT             -- 'cascade', 'adg_mv', 'precedent_skill', 'rule_registry'
);
CREATE INDEX idx_decision_signals_decision ON decision_signals(decision_id);
```

### 7.3 New table `decision_calibration_snapshots`

One row per weekly calibrator fit, per decision_type:

```sql
CREATE TABLE decision_calibration_snapshots (
  snapshot_id        INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at         TEXT NOT NULL,
  calibrator_version TEXT NOT NULL,
  decision_type      TEXT NOT NULL,
  n_outcomes         INTEGER NOT NULL,
  brier_score        REAL,
  ece_score          REAL,
  reliability_json   TEXT,           -- full 10-bin diagram
  isotonic_points_json TEXT          -- x,y pairs for re-application
);
```

### 7.4 `decision_outcomes` — writer finally wired

Already in schema (§4 of capture hook) but zero-row. W1.P1.2 adds:

- `DECISION_OUTCOME:` marker appended by Cursor Agent at end of execution turn (or by post-commit hook matching branch→decision_id).
- Fields: `decision_id`, `execution_completed`, `tests_passed`, `regression_found`, `rollback_required`, `followup_decision_id`, `promote_to_pattern`, `outcome_notes`, `time_to_outcome_s`.
- Outcome = **selected option landed without rollback AND tests_passed AND no regression for 7 days** → `promote_to_pattern=1`, fed to bandit.

---

## 8. Agentic-Spine Integration (G3 detail)

Author-Gate is today a **parallel sidecar** to the 10 routers (§29). Integrating it:

1. **Register as an 11th router layer** in `closed-loop-router-enforcement.md`: `author_gate` at the L0/harness plane, distinct from L5/hitl (runtime) and L0/bandit (namespace).
2. **Emit `ROUTER_DECISION:` marker** at packet-surface time with fields `layer=author_gate`, `decision_id`, `calibrated_score`, `selected_option_id`, `reason_code`, `outcome=pending`.
3. **`emit_ledger_event`** parallel to `ROUTER_DECISION:` per §29. New ledger: `intelligence_ledgers/author_gate_decision` (follows ADR-050 writer contract). Consulting skill: inherit from `ledger-consulter`.
4. **Exit-gate criteria enforced at outcome time:** `exit_criteria_json` (already in schema) is a list of JSON-encoded testable conditions; `DECISION_OUTCOME:` is only emitted `promote_to_pattern=1` if ALL exit criteria verified.
5. **Wilson-CI promotion (§6D parallel):** calibrator fit only runs on a class when n≥30 and Wilson-CI lower bound on outcome rate ≥ 0.60 (precedent from L6/promo).
6. **Regret ledger (§29 L6/regret):** each Author-Gate override (`selected ≠ recommended`) emits a `regret_sample` when the outcome lands — measures whether the Cursor Agent recommendation would have been better.

---

## 9. UI Placement & Content — High-Signal Card (G4 detail)

**Problem:** `ask_user_question` accepts `options: [{label, description}]` max 4. User sees labels first, descriptions second. Confidence, precedent, and "what would flip" are dropped.

**Proposal (P3.2):** Before calling `ask_user_question`, Cursor Agent emits a **recommendation card** in the response body via the `author-gate-ui-renderer` skill:

```
🎯 Recommended: <option.id> — <one-line thesis>
   Confidence:  🟢 0.89 (calibrated, n=47 precedents)
   Why:         <principle_at_stake> · precedent verdict: <strong|suggestive|none>
   Would flip:  <what_would_flip top-2, joined>
   Blast:       <hops> hops · hotspot rank #<N>/<total> · surfaces: <Exec,Write,...>

📋 Alternatives:
   • <option.id_2>: 🟡 0.71 — <one-line>
   • <option.id_3>: 🔴 0.54 — <one-line>

Reason-code for override (if not picking recommended):
   [override_recommendation | insufficient_precedent | blast_radius_too_high
    | principle_shift | test_strategy_change | dependency_risk | other]
```

Then `ask_user_question` renders with **enriched descriptions**:

```
options = [
  {"label": "Extract SovereignBaseAgent only", "description": "🟢 0.89 · recommended · precedent: strong · flip if blast>5"},
  {"label": "Extract all 5 siblings", "description": "🟡 0.71 · precedent: none · 3× larger diff"},
  {"label": "Skip — defer to W2", "description": "🔴 0.54 · reason: scope_change"},
  {"label": "Abort refactor", "description": "⛔ no-op · emits DEFERRED_SCOPE marker"},
]
```

This keeps `ask_user_question` compatible (no new primitive) while surfacing the signal the approver actually needs.

**Reviewer-fatigue mitigations (R5):**

- Confidence-band emoji pill in every option description.
- Gold star (🎯) ONLY on the recommended option.
- Precedent verdict verb-first ("precedent: strong" not "strong precedent exists").
- "Would flip" capped at 2 bullets.
- Reason-code palette pre-listed so the override path is a single pick, not prose.

---

## 10. Meta-Learning for Future Decisions (G5 detail)

**Pipeline (parallel to `run_hitl_consumer.py` for runtime HITL):**

```
decisions + decision_outcomes + decision_signals
    → AuthorGateQualityEngine.score_ledger()
        → per-(decision_type, reason_code) Beta posterior (Thompson bandit)
            → bandit_state.json persisted under .cursor/state/refactor_decisions/
                → precedent_injector reads bandit mean + CI
                    → next packet: precedent verdict includes prior strength
```

**Bandit cell:** `(decision_type, reason_code)` — e.g. `(refactor_scope, override_recommendation)` has its own Beta(α,β) posterior reflecting "how often did overrides in this class land without regression?"

**Write-back to precedent:** `precedent_injector.py` gains a `bandit_prior` field in the verdict block. A decision class with 40/50 successful overrides gets a `bandit_prior: 0.80 (n=50)` injection, telling Cursor Agent "in this class, override-the-recommendation historically wins — don't anchor too hard on your own recommendation."

**Weekly report `<YYYY-Www>.md`** surfaces:

1. Decision counts by class + override %
2. Calibration: Brier + ECE per class, trend vs previous 4 weeks
3. Flip-readiness: fraction in 0.72–0.85 gap (rubric refinement signal)
4. Top-5 overrides that led to promote_to_pattern=1 (learning candidates)
5. Top-5 recommendations that led to rollback=1 (calibration failures)
6. Precedent-agreement % (did Cursor Agent's pick match historical winning pick?)

---

## 11. Should Author-Gate Go Through the Agentic Spine with Exit Criteria?

**Yes — with clarification.** The Author-Gate is a *harness-plane* author-loop decision (§6, AGENTS.md "Plan First. Execute Second."), not a *runtime* HITL (ADR-023). Integration means:

- **Spine-native telemetry:** §29 `ROUTER_DECISION:` + ADR-050 ledger writer contract (W3.P1).
- **Exit-gate criteria = `exit_criteria_json`:** already captured; W1.P1.2 adds the enforcement loop (outcome writer verifies each criterion before `promote_to_pattern=1`).
- **Not a runtime blocker:** Author-Gate fires pre-execution in the author loop; it does NOT participate in UWG commit-allow (L4) or runtime HITL (L5). Those remain the runtime spine.
- **Promotion parity:** Author-Gate *classes* (not individual decisions) can promote rubrics via §6D once Wilson-CI ≥ 0.60 and n ≥ 30 precedents agree.

Net: treat Author-Gate as **the 11th router at the author-plane layer**, not a replacement for L5 HITL. It emits the same telemetry shape; consumers downstream (calibrator, bandit, regret ledger) treat its rows symmetrically with the other 10.

---

## 12. Risk Register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Cold-start: <30 outcomes per class, no calibration possible | High (first 4 weeks) | Uniform prior + `COLD_START` tag in packet; no gating threshold change until calibration converges |
| Outcome-writer drift: commits not linkable to decisions | Medium | Primary: `decision_id` in commit trailer via `git commit -m "... Decision-Id: dec_xxxxx"`. Fallback: branch-match against open decisions within 24h window |
| Reviewer-fatigue increase from richer UI | Low | Card is compressed to 6 lines max; emoji pills are scannable |
| `reason_code` enum stale | Medium | Review cadence at weekly calibration report; additions require ADR |
| Bandit exploration explodes option space | Low | Thompson sampling is exploit-heavy by construction; pure exploration only when n<5 per cell |
| SQLite schema drift breaks existing capture | Low | All migrations additive + idempotent PRAGMA-probed; existing rows unaffected |

---

## 13. Success Criteria (plan-wide)

1. **G1 closed:** ≥80% of new decisions carry a `confidence_calibrated` value drawn from isotonic fit after week 4.
2. **G2 closed:** `decision_outcomes` row count ≥ `decisions` row count × 0.7 after week 4 (30% may legitimately be pending).
3. **G3 closed:** `post_cursor_agent_router_decision_audit.py` recognizes `layer=author_gate` and logs zero unknown-layer violations for it.
4. **G4 closed:** Every `ask_user_question` call for an Author-Gate packet is preceded by a rendered card in the response body (audited by new post-cursor-agent hook).
5. **G5 closed:** Weekly report lands under `docs/reports/author-gate/` with non-zero rows; bandit state file present; precedent_injector emits `bandit_prior` field.
6. **G6 closed:** `decision_signals` row count ≥ `decisions.count × candidates_per_decision × 5` (5 signals per candidate).
7. **No regressions:** existing Author-Gate capture still exits 0; existing decisions readable unchanged; `check_decision_ledger_sqlite_freshness.py` still green.

---

## 14. Out of Scope

- Runtime HITL (L5, ADR-023) — unaffected.
- Notion Author-Gate ledger mirror — retired 2026-05-02 (see `sync_decision_ledger.py` stub), no revival.
- Mobile approval UI (codeongrass.com pattern) — future consideration, not this plan.
- LLM-as-judge cross-checker (R2 third signal) — requires judge calibration cadence per `judge-calibration-cadence.md`; deferred to separate plan.
- Replacing `ask_user_question` with a custom primitive — non-goal; we enrich, not replace.

---

## 15. Author-Gate Packet for This Plan

Per §6, this plan itself needs Author-Gate approval before W1 starts. The recommended option is to approve as drafted; alternatives are to split W2 (calibration) into a separate plan, or to descope UI work (P3.2) to a follow-up.

The packet will be emitted in the same turn as this plan's Notion row creation, scoring three options: `approve_as_drafted` (0.86), `split_calibration_out` (0.71), `descope_ui` (0.58). Precedent verdict: suggestive — `apps-eval-harness-parity-f8d4a2` Wave 1 approved similarly-scoped schema+consumer combo decisions in 2026-05-02 precedent.

---

## 16. References

**External research:**
- Anthropic — Demystifying evals for AI agents (`anthropic.com/engineering/demystifying-evals-for-ai-agents`)
- Anthropic — Building Effective AI Agents (`anthropic.com/research/building-effective-agents`)
- Galileo — Human-in-the-Loop Agent Oversight (`galileo.ai/blog/human-in-the-loop-agent-oversight`)
- dev.to — HITL for AI Agents: Patterns and Best Practices (Taimoor Ijaz)
- arXiv 2601.15778 — Agentic Confidence Calibration
- arXiv 2504.12501 — RLHF: A Book
- Microsoft Learn — Human in the Loop connector
- codeongrass.com — How to Build HITL Approval Gates for AI Coding Agents

**Internal:**
- `.cursor/rules/author-gate-enforcement.md` · `.cursor/rules/author-gate-decision-points.md`
- `.cursor/rules/closed-loop-router-enforcement.md` · `.cursor/rules/intelligence-ledger-family.md`
- `.cursor/skills/author-gate-packet-builder/SKILL.md`
- `.cursor/scripts/post_cursor_agent_author_gate_capture.py`
- `tools/capture/append_marker.py` · `tools/capture/queue_to_ledger.py`
- ADR-050 (intelligence-ledger-family) · ADR-080 (closed-loop routing)
- Constitutional §6, §17, §29, §30
