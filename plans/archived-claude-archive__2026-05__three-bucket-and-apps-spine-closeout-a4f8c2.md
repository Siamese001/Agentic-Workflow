---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\three-bucket-and-apps-spine-closeout-a4f8c2.md'
original_relative_path: '_archive\\2026-05\\three-bucket-and-apps-spine-closeout-a4f8c2.md'
source_sha256: 4cee5b6107c4ba26f8b34ad5497a3026fa99598a594594fb2ccfd8fcc17ac86e
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Three-Bucket W6 Remainder + Apps_* Spine Closeout

- **Plan ID**: `three-bucket-and-apps-spine-closeout-a4f8c2`
- **Status**: Planning — Author-Gate APPROVED 2026-05-01 for plan authorship; per-wave Author-Gates required for each WA execution
- **Tier**: T2 (multi-file, multi-wave, cross-thread)
- **Created**: 2026-05-01
- **Owner**: Cursor Agent (proposes); operator (approves wave gates)
- **SSOT**: this file

## 1. Mission

Close out the two parallel threads that share architectural intent ("apps_*
delegate to agentic_core spine; ADG snapshot is three-bucket certified") in
one ordered wave structure. The threads are:

- **Thread A — `adg-three-bucket-unified-c4f8e2` W6 remainder.** Mechanism is
  ✅ done; what remains is calendar-gated soak + per-owner burndown +
  Notion writeback.
- **Thread B — apps_* spine-coverage migration.** W8/W9 done
  (`apps_eval`, `apps_underwriting_ai`, `apps_research`); 3 apps remain
  (`apps_exec`, `apps_lic`, `apps_rfp`).

This plan does NOT re-author either source plan. It coordinates the
remaining work into linearly-ordered waves with explicit start/end
commits, deferred-scope markers for calendar-gated items, and per-wave
success criteria.

## 2. Predecessor plans (read-only references)

| Source plan | Disposition |
|---|---|
| `.cursor/plans/adg-three-bucket-unified-c4f8e2.md` | W1–W5 ✅ done; W6 ⏳ partially done; **WA1 + WA6 of THIS plan finish W6** |
| `.cursor/plans/adg-ci-spine-delegation-gate-438b16.md` | Already superseded by three-bucket-unified; gate ships strict via P5.1 |
| `.cursor/plans/apps-qna-spine-integration-e8f3a1.md` | Sibling per-app plan (apps_qna); pattern reused for apps_exec/apps_lic/apps_rfp here |
| W8 (chat-only) — apps_eval, apps_underwriting_ai → `FORMAL_EXCEPTION_STATIC_EVIDENCE` | Done |
| W9 (chat-only) — apps_research → `APP_OVERLAY_STATIC_EVIDENCE` | Done; commit `f8e9366` |

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| **WA1** | WA1.P1, WA1.P2 | W6 session-doable: declare 30 residual env flags (P6.5) + Notion writeback (P6.7) | ~6,000 | `.env.example` writable; Notion MCP healthy | Pending | `check_config_references.py` NEW count drops 30→≤5; 4 superseded-plan rows + this plan's W6 close-out posted to ADR Registry / Wave Convergence; Memory `ProceduralPattern:ThreeBucketADGCertification` written |
| **WA2** | WA2.P1, WA2.P2, WA2.P3 | apps_exec migration → `APP_OVERLAY_STATIC_EVIDENCE` (R3) | ~10,000 | apps_exec is R3-shaped per W9 finding (mirror of apps_research; HITL_ENABLED is runner-property, not contract-surface) | Blocked on WA1 | New `apps_exec/spine_manifest.yaml` + `apps_exec/integrations/spine_handoff.py`; scanner classifies apps_exec as `APP_OVERLAY_STATIC_EVIDENCE` with `manifest_missing_contracts == []`; +6 narrow tests pinning W2 contract; existing apps_exec suite zero-regression |
| **WA3** | WA3.P1, WA3.P2 | apps_lic UWG verification → migration (R3R4) | ~12,000 | apps_lic has a real durable-write path through UWG (per `governed_lic_run.py` integrations) | Blocked on WA2 | UWG path proven via `v_p0_write_bypass_uwg` query showing zero apps_lic bypass edges; `apps_lic/spine_manifest.yaml` declares `R3R4_managed_workflow` with CommitRequest contract; scanner classification flips to `APP_OVERLAY_STATIC_EVIDENCE` |
| **WA4** | WA4.P1 | apps_rfp `_compat/` lifecycle-trace shim cleanup (W7d unblocker) | ~6,000 | `apps_rfp/_compat/` callers can be migrated to canonical lifecycle helpers; downstream tests stable | Blocked on WA3 | `apps_rfp/_compat/` directory removed; lifecycle-trace usage routed through canonical `agentic_core` helpers; full apps_rfp suite green |
| **WA5** | WA5.P1, WA5.P2 | apps_rfp migration → `APP_OVERLAY_STATIC_EVIDENCE` (R3R4) | ~10,000 | WA4 unblocked the path; apps_rfp R3R4 shape confirmed | Blocked on WA4 | `apps_rfp/spine_manifest.yaml` + `apps_rfp/integrations/spine_handoff.py`; scanner promotion; +6 narrow tests; zero regression |
| **WA6** | WA6.P1, WA6.P2 | W6 calendar-gated close-out: `ADG_CERTIFIED_STRICT=1` flip + `NOT NULL` graduation | ~4,000 | P5.5 soak counter ≥ 4 (currently 1); 3 more in-band weeks (W19/W20/W21) elapsed | **DEFERRED_SCOPE** — calendar-gated; do not execute before 2026-05-22 | `ADG_CERTIFIED` strict run green; `python tools/adg/graduate_schema_not_null.py --commit` succeeds; W22 soak report shows 4 consecutive in-band weeks |

**Total**: ~48,000 tokens across 6 waves; WA1–WA5 are session-scoped (one
wave per prompt); WA6 is calendar-gated.

## 4. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| **WA1.P1** | Declare 30 residual env flags (W6 P6.5) | `.env.example` (modify) — append per-flag block per existing convention | 30 flags need rationale text; some are private bypass switches that should be documented as such | ~3,000 | Pending |
| **WA1.P2** | Notion writeback (W6 P6.7) | Notion ADR Registry, Wave/Phase Convergence, Memory MCP | 4 superseded plans + this plan + Memory entity all need posting; do as separate API calls (constitutional §25 MCP serialization) | ~3,000 | Pending |
| **WA2.P1** | apps_exec spine_manifest.yaml | `apps_exec/spine_manifest.yaml` (NEW) — `claimed_routes: [R3_grounded_read]`; explicit notes disclaiming CommitRequest / formal-exception / runtime-cert | Mirror of apps_research W9 manifest | ~2,000 | Blocked |
| **WA2.P2** | apps_exec spine_handoff.py | `apps_exec/integrations/spine_handoff.py` (NEW) — 8 R3 contract imports; thin delegate to `GovernedExecRun.run_governed_e2e()` | HITL_ENABLED=True is runner-property (no contract-surface change); reuse apps_research helpers verbatim | ~5,000 | Blocked |
| **WA2.P3** | apps_exec narrow tests | `tests/unit/tools/analysis/test_apps_spine_coverage.py` (modify) — +6 tests pinning W2 contract | Existing apps_exec test suite must remain zero-regression (smoke check) | ~3,000 | Blocked |
| **WA3.P1** | apps_lic UWG durable-write verification | `tools/adg` queries against latest snapshot; `apps_lic/integrations/governed_lic_run.py` static review | Confirm `v_p0_write_bypass_uwg` shows zero apps_lic edges; if any, surface via DEFERRED_SCOPE before migration | ~4,000 | Blocked |
| **WA3.P2** | apps_lic spine_manifest + spine_handoff (R3R4) | `apps_lic/spine_manifest.yaml`, `apps_lic/integrations/spine_handoff.py` | Add `CommitRequest` contract to the imports list (vs apps_research's 8); `claimed_routes: [R3R4_managed_workflow]` | ~8,000 | Blocked |
| **WA4.P1** | apps_rfp `_compat/` shim removal | `apps_rfp/_compat/**` (delete), callers (modify to canonical helpers) | Need to identify call sites; each call must migrate to `agentic_core.lifecycle_*` canonical equivalent | ~6,000 | Blocked |
| **WA5.P1** | apps_rfp spine_manifest.yaml | `apps_rfp/spine_manifest.yaml` (NEW) — `claimed_routes: [R3R4_managed_workflow]` | Same shape as apps_lic | ~2,000 | Blocked |
| **WA5.P2** | apps_rfp spine_handoff.py + tests | `apps_rfp/integrations/spine_handoff.py` (NEW) + +6 narrow tests | Same shape as apps_lic | ~8,000 | Blocked |
| **WA6.P1** | `ADG_CERTIFIED_STRICT=1` flip | `ops_scripts/ci/check_adg_certified.py` (modify default OR `.env.example` declaration) | Soak-gated on P5.5 counter ≥ 4 | ~2,000 | DEFERRED |
| **WA6.P2** | `NOT NULL` graduation execution | Run `python tools/adg/graduate_schema_not_null.py --commit` | Schema-gated on W1 column materialization + zero-NULL precondition | ~2,000 | DEFERRED |

## 5. ADG_HOTSPOT_REPORT

This plan does NOT introduce new hotspots — it extends an already-classified
surface (`apps_*` spine delegation) and closes baseline burndowns.
Risk-relevant nodes:

| Hotspot | Layer | Fan-in proxy | Archetype | ADG Surface | Layer multiplier | Impact (rel.) |
|---|---|---:|---|---|---:|---:|
| `agentic_core.L0_routing.intake.validated_request.ValidatedRequest` | L0 | 3 (apps_eval, apps_underwriting_ai, apps_research) → growing to 6 | CENTRAL_DEPENDENCY | Execution | 2.0 | high — every new app migration adds another importer |
| `agentic_core.L4_state.uwg.commit.CommitRequest` | L4 | apps_lic (WA3) + apps_rfp (WA5) will add edges | STATE_NODE | Write | 1.75 | medium — WA3/WA5 new write surface |
| `apps_rfp/_compat/` lifecycle shim | L_APP | unknown until WA4 audit | ORCHESTRATOR (legacy shim) | Observability | 1.0 | medium — must not break trace contracts during removal |

## 6. ADG_GRAPH_LAYER_EVIDENCE

Per constitutional §22, T2/T3 refactoring plans must cite ≥3 materialized
views + semantic edges + P-views. Citations for this plan:

- **`mv_graph_reverse_dependency_hotspots`** — confirms ValidatedRequest /
  CommitRequest as central dependencies; baseline for measuring new
  apps_* importers
- **`mv_graph_critical_path_blast_radius`** — used by WA4 to scope shim
  removal blast radius before deletion
- **`mv_dependency_cone_risk`** — used by WA3.P1 to confirm apps_lic UWG
  path coverage
- **Semantic edges**: `imports` (existing scanner surface), `writes_to`
  (WA3 UWG verification), `flows_to` (WA4 shim caller migration)
- **P-views**: `v_p0_write_bypass_uwg` (WA3 verification — must be
  zero for apps_lic), `v_p0_apps_direct_infra` (W3 advisory baseline)

## 7. Constraints

- **One wave per prompt.** WA1 → WA2 → WA3 → WA4 → WA5 → WA6.
  Skipping order is allowed only if a wave is independently green
  (e.g., WA2 could run in parallel with WA1 — but only after explicit
  Author-Gate per wave).
- **No `git add -A` / `git commit -a`.** Each wave commits an explicit
  staged set; ~91 lines of unrelated working-tree noise on `main` MUST
  remain unstaged.
- **Implementation branch per wave.** Pattern: `three-bucket-WA<N>-impl`
  off `main`; merge or rebase upstream as the operator chooses.
- **No CI wiring changes.** WA1.P1 declares env vars in `.env.example`
  only; does not flip strict defaults (P6.5 baseline gate already handles
  ratchet-down on declaration).
- **DEFERRED_SCOPE markers** required for WA6 sub-phases at plan-merge
  time (see §9).

## 8. Per-Wave Author-Gate prompts

Each wave executes under its own Author-Gate. Suggested prompts:

| Wave | Suggested prompt |
|---|---|
| WA1 | "Execute WA1.P1 + WA1.P2 of three-bucket-and-apps-spine-closeout-a4f8c2 — declare residual env flags + post Notion writeback" |
| WA2 | "Execute WA2 of three-bucket-and-apps-spine-closeout-a4f8c2 — apps_exec R3 spine migration mirroring apps_research W9" |
| WA3 | "Execute WA3 of three-bucket-and-apps-spine-closeout-a4f8c2 — apps_lic UWG verification + R3R4 spine migration" |
| WA4 | "Execute WA4 of three-bucket-and-apps-spine-closeout-a4f8c2 — remove apps_rfp/_compat/ lifecycle shim" |
| WA5 | "Execute WA5 of three-bucket-and-apps-spine-closeout-a4f8c2 — apps_rfp R3R4 spine migration" |
| WA6 | "Execute WA6 of three-bucket-and-apps-spine-closeout-a4f8c2 — ADG_CERTIFIED strict flip + NOT NULL graduation (only after P5.5 soak counter ≥ 4)" |

## 9. DEFERRED_SCOPE markers (WA6)

Calendar-gated items — emit at plan-merge time so the auto-capture hook
posts them to Wave/Phase Convergence with computed P-band.

## 10. Out of scope

- L1PlanContract / RetrievalPlan SSOT collapse (separate future plan)
- OTel-trace → contract-surface binding (separate future plan)
- apps_shared extraction of handoff helpers (only after WA2 lands; even
  then, optional)
- New `apps_*` packages beyond the 3 named (`apps_exec`, `apps_lic`,
  `apps_rfp`)

## 11. References

- `@.cursor/plans/adg-three-bucket-unified-c4f8e2.md` (parent W6 thread)
- `@.cursor/plans/adg-ci-spine-delegation-gate-438b16.md` (superseded
  spine-delegation gate predecessor)
- `@docs/architecture/adr/ADR-079-l2-agent-graph-layer-contract.md`
- `@docs/architecture/adr/ADR-078-apps-spine-delegation.md`
- `@AGENTS.md` MCP Quick Reference (live tool routing)
- W9 apps_research migration commit `f8e9366` (template for WA2/WA5)

DEFERRED_SCOPE: plan=three-bucket-and-apps-spine-closeout-a4f8c2 wave=WA6 phase=WA6.P1 layer=L6 fan_in=3 surface=Observability coverage_gap_pct=0.0 est_tokens=2000 reason=ADG_CERTIFIED_STRICT flip soak-gated on P5.5 counter >= 4

DEFERRED_SCOPE: plan=three-bucket-and-apps-spine-closeout-a4f8c2 wave=WA6 phase=WA6.P2 layer=L4 fan_in=3 surface=State coverage_gap_pct=0.0 est_tokens=2000 reason=NOT NULL triplet column graduation soak-gated and W1 schema dependent
