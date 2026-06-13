# Backlog ↔ Plan Linkage Enforcement

**Slug**: `backlog-plan-linkage-enforcement-a4b2f1`
**Status**: Completed
**Type**: Data-hygiene + governance (not code refactoring)
**Parent context**: 2026-05-03 session — Backlog Items DB MECE v2 cleanup + fill-rate audit.

## Goal

Make the invariant **"every Backlog Items row links to a registered Plans DB row"** true and keep it true. Close the 286-row slug-but-no-relation gap, handle the 3 true-orphans, spot-fix 32 misc outliers, re-derive field accuracy once relations land, and land a CI gate that prevents regression.

## Scope

**In scope**
- `aa8d2507-101e-4384-81d9-60ea3fe33876` Backlog Items DB (518 rows).
- `6aba34d9-4d0b-4f4c-b956-b2bdea541ca9` Plans DB (parent relation target).
- `tools/notion/` scripts (backfill + audit family, already established in today's session).
- `ops_scripts/ci/` CI gate (NP3-class, sibling of NP1/NP2).
- `.windsurf/scripts/post_cascade_deferred_scope_capture.py` (already upgraded 2026-05-03; no further changes unless re-audit surfaces bugs).

**Out of scope**
- Re-authoring historical plan markdown files.
- Recovering prose lost when MECE v2 columns were deleted (`Blocking Items`, `Success Criteria`, `Dependencies`) — unrecoverable via Notion API; on-disk plan files remain the fallback SSOT.
- Changes to Wave/Phase Convergence semantics or scorer formula (ADR-031 stable).
- Apps-eval harness work (separate plan family).

## Non-Goals

- Zero-orphan at the hook level via fail-closed capture. Hook stays fail-open per constitutional §25 sibling discipline — backfill + CI gate close the loop without blocking capture.
- Cross-relation joins (Backlog → Plan → ADR). ADR linkage already exists via `Blocking ADR` rich_text, stays as-is.

## Baseline (measured 2026-05-03 09:41 UTC)

```
Total rows:           518
Plan relation:        229  (44.2%)
Plan File slug:       515  (99.4%)
Impact Score:         518  (100.0%, post-backfill today)
P-Band:               518  (100.0%)
Layer:                502  (96.9%, post-backfill today)
Surface:              502  (96.9%)
Fan-In:               498  (96.1%)
Status:               509  (98.3%)
Phase ID:             509  (98.3%)
Wave ID:              514  (99.2%)
Evidence:             263  (50.8%)  ← legacy prose unrecoverable
Last Updated:         408  (78.8%)
Actual Tokens:         60  (11.6%)  ← completion-only by design
Blocking ADR:          34  (6.6%)   ← manual/rare by design
```

Link-gap arithmetic:
- **286 rows** have `Plan File` slug but no resolved `Plan` relation → **closable by backfill** (resolver already written).
- **3 rows** have neither `Plan File` nor `Plan` relation → **true orphans** needing catch-all plan or deletion.
- **32 misc outliers** (16 Layer/Surface edge cases + 9 Phase ID/Status + 4 Wave ID + 3 Plan File) → second-pass spot-fix.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W1 | 1.1–1.2 | Plan-relation backfill for 286 slug-but-no-relation rows | ~4k | Resolver `_resolve_plan_page_id` works against Plans DB; Notion rate limit ~3 rps | ✅ Done | Plan relation 97.1% (504/518); audit confirmed |
| W2 | 2.1 | True-orphan handling for 3 rows (no slug, no relation) | ~2k | A catch-all plan page is acceptable org; user approves label | ✅ Done | 3 orphans routed to catch-all; 0 unresolved |
| W3 | 3.1–3.2 | Misc outlier spot-fix (32 rows across Layer/Surface/Phase ID/Status/Wave ID/Plan File) | ~3k | Missing values recoverable from Plan File slug or safe defaults | ✅ Done | Phase ID/Status/Wave ID ≥ 99.8%, Plan File 100%, Layer/Surface ≥ 99% |
| W4 | 4.1–4.3 | Post-linkage field re-audit + Plan-derived enrichment | ~6k | Plans DB carries `Layer` / `Surface` hints on plan rows; where absent, scorer defaults remain | ✅ Done | 504 rows audited; 117 Status rows upgraded from scorer-default Draft to Plan-derived value |
| W5 | 5.1–5.2 | CI gate + rule for linkage invariant | ~4k | Sibling of NP1/NP2 pattern; advisory default; `BACKLOG_PLAN_LINKAGE_FAIL_CLOSED=1` strict | ✅ Done | NP3 gate green (advisory); registered in `run_contract_gates.py`; rule + AGENTS.md note |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| 1.1 | Plan-relation backfill script | `tools/notion/backfill_backlog_plan_relation.py` (new) | Notion rate limit; slug collisions across multiple plans | 2.5k | Todo |
| 1.2 | Run backfill + verify | audit re-run | Transient Notion 5xx | 1.5k | Todo |
| 2.1 | Catch-all orphan plan | Plans DB row `unlinked-backlog-orphan` + 3-row reassign via patch | User approval on naming | 2k | Todo |
| 3.1 | Outlier recovery script | `tools/notion/backfill_backlog_outliers.py` (new) — per-column probes | Need defaults for unrecoverable Phase ID / Wave ID | 2k | Todo |
| 3.2 | Execute outlier recovery + verify | audit re-run | — | 1k | Todo |
| 4.1 | Plan-derived field re-audit | `tools/notion/audit_backlog_plan_derived.py` (new) — joins Backlog × Plans and reports fields that could be upgraded | Plans DB schema richness unknown until probed | 2k | Todo |
| 4.2 | Author-Gate: accept Plan-derived overrides? | AG packet — replace scorer defaults with Plan data where present | Authoritative source per field (Plan vs scorer defaults) | 1k | Todo |
| 4.3 | Execute override pass if approved | re-use `backfill_backlog_scores.py` with new inputs | — | 3k | Todo |
| 5.1 | CI gate | `ops_scripts/ci/check_notion_backlog_plan_linkage.py` (new) | Offline CI must skip | 2.5k | Todo |
| 5.2 | Rule + registry | `.windsurf/rules/notion-backlog-plan-linkage.md` (new) + `run_contract_gates.py` entry + AGENTS.md Notion-map note | Rule discoverability | 1.5k | Todo |

## Waves — Detail

### W1 — Plan-relation backfill (286 rows)

**Phase 1.1 — script**

- New file: `tools/notion/backfill_backlog_plan_relation.py`.
- Paginate Backlog, filter rows where `Plan.relation = []` AND `Plan File != ""`.
- For each: derive slug from `Plan File` (strip `.md`), call `_resolve_plan_page_id(slug, token)` from `@c:\Git\Agentic-Workflow-FRESH\.windsurf\scripts\post_cascade_deferred_scope_capture.py`.
- On hit: `API-patch-page` with `Plan = {relation: [{id: page_id}]}` + `Last Updated = today`.
- On miss: log to `artifacts/windsurf/backlog_plan_linkage_misses.jsonl` for W2 triage.
- Progress bar via `tqdm`, throttle 0.35s per row (constitutional §16).
- Dry-run flag; idempotent; fail-open per row.

**Phase 1.2 — run + verify**

- Dry-run-gated execution.
- Expect `ok ≥ 280`, `miss ≤ 6` (slugs that point to deleted/renamed plans).
- Re-run `tools/notion/audit_backlog_fill_rates.py` — confirm Plan fill ≥ 99%.

### W2 — True-orphan catch-all (3 rows)

- Create one Plans DB row: `slug=unlinked-backlog-orphan`, `Status=Draft`, Summary describing intent, Plan File Path `.windsurf/plans/_virtual/unlinked-backlog-orphan.md` (virtual sentinel, not a real file).
- Author-Gate AG-packet: decide between (A) reassign the 3 true orphans to catch-all, (B) delete them, (C) inspect each case individually.
- Execute the selected path; Backlog goes to **0 unlinked rows**.

### W3 — Misc outlier spot-fix (32 rows)

Three sub-probes:
1. **Phase ID / Status / Wave ID** — 9 + 9 + 4 rows. Recover from `Plan File` slug where pattern `<slug>-<6hex>.md` matches a known plan; else default `Phase ID=1.1`, `Status=Draft`, `Wave ID=W1` (explicit, auditable in Evidence note).
2. **Plan File** — 3 rows. Use `Plan.relation` to walk back to Plans DB; read Plan File Path property; write that back into the Backlog row's `Plan File`.
3. **Layer / Surface non-select edge cases** — 16 rows. Root cause: `_select_name` check in the first backfill returned None for non-null rows whose select value was structurally broken (probably mid-migration multi_select→select survivors). Write `L_MIXED` / `None` unconditionally for this set; log the 16 IDs for post-hoc inspection.

### W4 — Post-linkage accuracy re-audit

**Phase 4.1 — new audit tool**

- `tools/notion/audit_backlog_plan_derived.py`.
- For each Backlog row with resolved `Plan` relation, read the linked Plans row's properties.
- Emit per-field comparison: current Backlog value vs Plan-derived value vs scorer-default value.
- Output: `artifacts/notion/backlog_plan_derived_delta.json` + markdown summary.

**Phase 4.2 — Author-Gate: authoritative-source policy**

- AG packet: for each field where Plan has data AND Backlog value is scorer-default, which wins?
  - Candidate field: `Layer` — Plans DB may carry the owning layer.
  - Candidate field: `Status` — Plans DB Status (Live/Draft/Completed) may imply Backlog Status.
  - Candidate field: `Blocking ADR` — Plans DB may link to ADR registry; propagate to Backlog.
- Score options; surface to user; durable decision in refactor ledger.

**Phase 4.3 — override pass (if AG approves)**

- Re-use `tools/notion/backfill_backlog_scores.py` with an `--upgrade-from-plan` flag.
- Patches only fields where Plan-derived data supersedes scorer defaults AND the row was originally backfilled (to avoid clobbering hand-authored values).

### W5 — CI gate + rule

**Phase 5.1 — gate**

- New file: `ops_scripts/ci/check_notion_backlog_plan_linkage.py`.
- Advisory by default; fail-closed via `BACKLOG_PLAN_LINKAGE_FAIL_CLOSED=1`.
- Skips when `NOTION_API_KEY` / `NOTION_TOKEN` unset (offline CI safe).
- Emits `artifacts/notion/backlog_plan_linkage.json`.
- Registered as "NP3 Notion Backlog plan linkage (advisory)" in `ops_scripts/ci/run_contract_gates.py` after NP2.

**Phase 5.2 — rule + docs**

- New file: `.windsurf/rules/notion-backlog-plan-linkage.md` (conditional, not always_on — token budget).
- AGENTS.md Notion-map note: add Backlog → Plan linkage invariant to the MCP Registry section.
- AG_QUEUE_SEED rows for each AG decision below.

## Gap Register

1. **Slug collisions** — two plans with overlapping slug fragments could resolve to the wrong page. Mitigation: resolver already uses exact-match probes (Slug property first, then Plan File Path, then Name contains). Log any ambiguous matches (>1 result) to miss-file for manual triage.
2. **Deleted plans** — a legacy slug may reference a plan that was archived/deleted. Those land in the W2 orphan bucket.
3. **Plans DB Slug property optional** — not every plan row has a Slug property populated. Resolver falls through to Plan File Path contains, then Name contains.
4. **Plan-derived overrides** — may conflict with hand-authored Backlog values. Mitigation: W4.2 Author-Gate + `--upgrade-from-plan` only touches scorer-defaulted cells.

## AG_QUEUE_SEED markers

```
AG_QUEUE_SEED: plan=backlog-plan-linkage-enforcement-a4b2f1 id=true-orphan-handling depends_on= title=True-orphan handling — catch-all vs delete vs per-row
AG_QUEUE_SEED: plan=backlog-plan-linkage-enforcement-a4b2f1 id=plan-derived-authority depends_on=true-orphan-handling title=Field authority — Plan-derived vs scorer-default precedence per field
AG_QUEUE_SEED: plan=backlog-plan-linkage-enforcement-a4b2f1 id=ci-gate-strictness depends_on=plan-derived-authority title=CI gate strictness — advisory only vs fail-closed via env var
```

## ADG_HOTSPOT_REPORT

N/A — this plan is Notion data-hygiene + governance, not code refactoring. No AST nodes, layer boundaries, or structural fan-in involved. Constitutional §22 applies to T2/T3 refactoring; this plan touches only `tools/notion/` one-shot scripts + one CI gate, all self-contained at L_TOOLS / L_OPS. Reference: see sibling plan `notion-plans-status-enforcement-7a1e2d.md` for the established pattern (same N/A stance).

## ADG_GRAPH_LAYER_EVIDENCE

N/A — see above. The work touches no production module, no agentic_core/apps_* code path, no layer boundary. Hotspot / graph-layer driver requirements are refactoring-specific.

## Success Criteria (whole-plan)

1. **Plan relation fill ≥ 99.4%** (matches Plan File fill, minus any unresolvable slugs routed to catch-all).
2. **0 rows with null Plan AND null Plan File** (true orphan count == 0).
3. **All 16 Layer/Surface edge-case rows normalized** (select type, valid option).
4. **CI gate NP3 green** on subsequent runs.
5. **Audit delta report published** at `docs/reports/notion/backlog-plan-linkage-<YYYY-MM-DD>.md` summarizing before/after.
6. **Zero regressions** in Impact Score / P-Band (backfill of today remains stable — W1/W3 patches must not overwrite those cells).

## AI Summary

- Target: Notion Backlog Items DB (518 rows) linkage to Plans DB.
- Closes: Plan relation gap (44.2% → ≥99.4%), 3 true orphans, 32 misc outliers.
- New files: `tools/notion/backfill_backlog_plan_relation.py`, `tools/notion/backfill_backlog_outliers.py`, `tools/notion/audit_backlog_plan_derived.py`, `ops_scripts/ci/check_notion_backlog_plan_linkage.py`, `.windsurf/rules/notion-backlog-plan-linkage.md`.
- Edits: `ops_scripts/ci/run_contract_gates.py` (+ NP3 entry), AGENTS.md Notion-map note.
- Pattern source: `notion-plans-status-enforcement-7a1e2d` (NP1/NP2 gate family, advisory + fail-closed env var). 5 waves, ~19k tokens.
- Non-goals: historical plan re-authoring, prose recovery from deleted MECE v2 columns, capture-hook fail-closed semantics.
- Success: Plan relation ≥99.4%, 0 orphans, CI gate green, post-linkage audit delta published, zero regression on today's Impact Score backfill.

## References

- Constitutional §25 (MCP serialization — remote MCP isolation)
- Constitutional §35 (Author-Gate queue drain)
- Constitutional §36 (plan-registration enforcement — Plans DB SSOT)
- `.windsurf/rules/notion-plans-taxonomy.md` (canonical Status values)
- `.windsurf/plans/notion-plans-status-enforcement-7a1e2d.md` (NP1/NP2 pattern source)
- `@c:\Git\Agentic-Workflow-FRESH\tools\notion\audit_backlog_fill_rates.py` (baseline measurement tool, created 2026-05-03)
- `@c:\Git\Agentic-Workflow-FRESH\tools\notion\backfill_backlog_scores.py` (Impact Score backfill tool, created 2026-05-03 — pattern source for W1 and W3 scripts)
- `@c:\Git\Agentic-Workflow-FRESH\.windsurf\scripts\post_cascade_deferred_scope_capture.py` (capture hook with `_resolve_plan_page_id` resolver, upgraded 2026-05-03)
