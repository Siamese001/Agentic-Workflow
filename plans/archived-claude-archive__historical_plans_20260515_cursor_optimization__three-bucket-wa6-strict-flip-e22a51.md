---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\three-bucket-wa6-strict-flip-e22a51.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\three-bucket-wa6-strict-flip-e22a51.md'
source_sha256: 76fb79e7017df5d590a476e563a945ebf036eaa880d7320923871ac55760ca96
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Three-Bucket WA6 — `ADG_CERTIFIED_STRICT=1` Flip + `NOT NULL` Graduation

- **Plan ID**: `three-bucket-wa6-strict-flip-e22a51`
- **Status**: Waiting (calendar-gated until 2026-05-22)
- **Tier**: T1 (single-wave, ~4,000 tokens)
- **Created**: 2026-05-03
- **Owner**: Cascade (proposes); operator (approves WA6 gate)
- **SSOT**: this file

## 1. Mission

Execute the calendar-gated portion of the three-bucket ADG certification thread.
Spun out of `three-bucket-and-apps-spine-closeout-a4f8c2` (now Completed) so
the parent plan can close cleanly while WA6 waits for soak completion.

This is the WA6 portion verbatim — no rewriting of mechanism, only execution
once the soak counter qualifies.

## 2. Predecessor

| Source plan | Disposition |
|---|---|
| `.windsurf/plans/three-bucket-and-apps-spine-closeout-a4f8c2.md` | **Completed 2026-05-03** — WA1/WA4 landed in-session; WA2/WA3/WA5 already green; WA6 spun out into this plan |
| `.windsurf/plans/adg-three-bucket-unified-c4f8e2.md` | Parent W6 thread; mechanism done; this plan finishes W6 calendar gate |

## 3. Wait Conditions (all must be true before execution)

1. **P5.5 soak counter ≥ 4** — currently 1 as of 2026-05-03; need 3 more in-band weeks (W19/W20/W21).
2. **Earliest execution date**: 2026-05-22 (per parent plan §3 WA6 row).
3. **W22 soak report green** — 4 consecutive in-band weeks with `ADG_CERTIFIED` advisory passing.

## 4. Wave Structure (single wave)

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---:|---|---|
| **WA6** | WA6.P1, WA6.P2 | `ADG_CERTIFIED_STRICT=1` flip + `NOT NULL` graduation | ~4,000 | **Waiting** — soak-gated until 2026-05-22 | `ADG_CERTIFIED` strict run green; `python tools/adg/graduate_schema_not_null.py --commit` succeeds; W22 soak report shows 4 consecutive in-band weeks |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| **WA6.P1** | `ADG_CERTIFIED_STRICT=1` flip | `ops_scripts/ci/check_adg_certified.py` (modify default) OR `.env.example` declaration | Soak-gated on P5.5 counter ≥ 4 | ~2,000 | Waiting |
| **WA6.P2** | `NOT NULL` graduation execution | Run `python tools/adg/graduate_schema_not_null.py --commit` | Schema-gated on W1 column materialization + zero-NULL precondition | ~2,000 | Waiting |

## 6. ADG_HOTSPOT_REPORT

This plan introduces no new hotspots — it flips a flag and graduates schema
columns that have soaked at zero-NULL for 4 weeks. Risk-relevant nodes
inherit from parent plan §5 (no change).

## 7. ADG_GRAPH_LAYER_EVIDENCE

Per constitutional §22:

- **`mv_dependency_cone_risk`** — confirms zero net-new risk vs the soaked snapshot
- **`mv_graph_critical_path_blast_radius`** — used to verify the strict-flip cannot regress fan-in to certification surface
- **Semantic edges**: `flows_to` (cert pipeline), `writes_to` (schema graduation)
- **P-views**: `v_p0_apps_direct_infra` (must remain at advisory baseline)

## 8. Constraints

- **Do NOT execute before 2026-05-22.** Hard calendar gate.
- **Verify soak counter ≥ 4** before WA6.P1 — implementation step 1.
- **Single Author-Gate per WA6**, not per phase — both phases share fate.
- **Rollback**: if strict run fails, immediately revert flag default; do NOT graduate schema.

## 9. Author-Gate prompt (when ready)

> "Execute WA6 of three-bucket-wa6-strict-flip-e22a51 — soak counter is now ≥ 4; flip ADG_CERTIFIED_STRICT=1 and graduate NOT NULL columns."

## 10. Out of Scope

- Anything outside WA6 of the parent plan — already completed in `three-bucket-and-apps-spine-closeout-a4f8c2`
- Soak counter increment logic (already in place via P5.5)
- New env-flag declarations (closed under WA1.P1 of parent plan)

## 11. References

- `@.windsurf/plans/three-bucket-and-apps-spine-closeout-a4f8c2.md` (parent plan, Completed 2026-05-03)
- `@.windsurf/plans/adg-three-bucket-unified-c4f8e2.md` (W6 mechanism)
- `@docs/architecture/adr/ADR-079-l2-agent-graph-layer-contract.md`

DEFERRED_SCOPE: plan=three-bucket-wa6-strict-flip-e22a51 wave=WA6 phase=WA6.P1 layer=L6 fan_in=3 surface=Observability coverage_gap_pct=0.0 est_tokens=2000 reason=ADG_CERTIFIED_STRICT flip soak-gated on P5.5 counter >= 4 (earliest 2026-05-22)

DEFERRED_SCOPE: plan=three-bucket-wa6-strict-flip-e22a51 wave=WA6 phase=WA6.P2 layer=L4 fan_in=3 surface=State coverage_gap_pct=0.0 est_tokens=2000 reason=NOT NULL triplet column graduation soak-gated and schema-dependent (earliest 2026-05-22)
