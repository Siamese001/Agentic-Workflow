# Notion Backlog Reconciliation — 2026-04-29

**Scope:** Wave/Phase Convergence DB (`fc7f6bf4...`) reconciled against `.windsurf/plans/` and `archives/windsurf_plans/`.
**Source:** `artifacts/notion_recon.json` + `artifacts/recon_categorize.txt`.

## Headline

| Category | Keys | Rows | Open | Done | Other |
|---|---:|---:|---:|---:|---:|
| **LIVE_PLAN** (plan exists on disk) | 48 | 205 | **119** | 86 | 0 |
| **ARCHIVED_PLAN** (parent plan moved to `archives/`) | 44 | 233 | **52** | 173 | 8 |
| **NEW_PLACEHOLDER** (`NEW:` / `(NEW...)`) | 7 | 14 | 6 | 8 | 0 |
| **SENTINEL_NO_PLAN** (`(in-session...)` / `_INDEX_...`) | 3 | 3 | 0 | 2 | 1 |
| **TRULY_ORPHAN** (slug missing everywhere) | 16 | 18 | **7** | 11 | 0 |
| **TOTAL** | 118 | 473 | **184** | 280 | 9 |

> The earlier snapshot reported 193 open / 4 stale UNSCORED; my corrected count is **184 open** because `Status="Complete"` (4 rows) and `Status="Descoped"` (16 rows) were counted with Done.

## Reconciliation by category

### 1. Real remaining work (LIVE_PLAN, 119 open rows across 36 active plans)

Top backlogs (these are the "what still needs to be done"):

| Open | Plan | Notes |
|---:|---|---|
| 13 | `adg-gap-remediation-wave-plan-ae5b42` | All Todo, 11 P3 + 1 P2 + 1 P1 |
| 12 | `adg-ci-gate-hardening-deferred-b4e3c9` | All Todo, fully enriched |
| 12 | `l0-routing-calibration-gap-audit-b3c9d4` | 5 Todo + **7 Blocked** |
| 11 | `gap-closure-test-impl-b77a11` | L4/L5 cert binding tests; 4 P1, 6 P2 |
| 8 | `ssot-consolidation-cleanup-b7f3a1` | All Todo, all P3 |
| 7 | `windsurf-maintenance-2026-q2-0f3564` | Scheduled NEXT-* maintenance items |
| 5 | `c0-context-assembly-best-practices-b7c3a1` | 3 In-Progress, 2 Todo |
| 5 | `notion-backlog-human-scoring-e7a941` | All Todo (the human-scoring waves) |
| 5 | `adg-wiring-ci-dispatcher-hardening-b2f4a1` | All Todo |
| 5 | `scorer-otel-autosource-layer-b-c5e4d1` | 4 Todo + 1 Blocked |

…plus 26 more LIVE plans with 1–4 open rows each.

### 2. Stale rows under archived plans (52 rows — auto-closeable)

These rows are still `Todo`/`Blocked`/`In Progress` but their parent plan was moved to `archives/windsurf_plans/2026-04/` (work complete). Top offenders:

| Open | Archived plan |
|---:|---|
| **14** | `five-tier-governance-model-a3f7c2` (W1/W2 gate-wiring rows still Todo despite plan archive) |
| **13** | `l5-governance-best-practice-gap-4615ae` (P8.* guardrail rows W4/W5) |
| 3 | `prompt-reception-followups-a7b3c4` (PRF2/PRF3 rows; 2 Blocked + 1 Todo) |
| 3 | `routing-unification-qwen-abe735` (F4.1–F4.3 ADG-graph-layer items) |
| 2 each | `cache-r1ab-residuals-8c4e2a`, `post-wave10-roadmap-a1e7f2`, `test-coverage-backlog-f8f5a7` |
| 1 each | 14 plans with single straggler rows |

**Action:** Either (a) flip these rows to `Done`/`Descoped` if work is genuinely complete, or (b) carry the open items into a successor plan and update each row's Plan File before flipping.

### 3. NEW: placeholders (6 open rows)

Plans referenced as `NEW:<slug>` but never scaffolded:
- `anthropic-alignment-followups (NEW)` — 3 open rows
- `adg-l5-healer-design-decision (NEW — to be scaffolded)` — 1 open
- `NEW:adg-mcp-reopen-hardening (to be created)` — 1 open (note: archived plan with that slug now exists; redundant)
- `(no dedicated plan - trivial fix - see Blocking Items for 3-option remediation)` — 1 open

### 4. Truly orphan (7 open rows — need rescue)

Slug doesn't exist on disk OR in archives:

| Slug | Likely origin |
|---|---|
| `adg-trace-replay-eval-ratchet` | W1.1 ratchet regression — never scaffolded |
| `adg-l5-bypass-cleanup` | W1.1 P0 L5 safety bypass |
| `adg-seam-test-coherence-cleanup` | W1.1 P1 6 violations |
| `post-cursor-agent-watchdog-hardening` | hook hardening item |
| `windsurf-hook-outage-2026-04-23` | RCA item |
| `pytest-server-functional-tests` | test scaffolding |
| `d7-anchor-tuning` | D7 gate tuning |

### 5. Disk plans with ZERO Notion coverage (69 plans)

Most are first-principles refactor specs (`apps-*-first-principles-refactor-*`) and SVP review docs that may legitimately not need Notion tracking. A few that probably SHOULD have rows:
- `adg-three-graph-harness-e57cc7` (active per the IDE's open file)
- `next-step-gate-ci-workflow-8733a6`
- `mcp-skill-installation-2ee0d2`
- `notion-backlog-schema-refactor-7c3d9e` (parent of this very work)

## Confounders found during the audit

1. **Audit-script path-normalization bug** — `tools/reports/audit_notion_backlog_coverage.py:117` strips `.md` but **not** the `.windsurf/plans/` prefix. Inflates orphan count by ~3 keys / undercounts coverage by ~3 plans. Fix: add prefix-stripping in `_extract` (see correction script below).
2. **Mojibake in titles** — many rows show `ΓÇö` instead of em-dash and `ΓåÆ` instead of arrow. Cosmetic; from earlier UTF-8/cp1252 mix at write time.
3. **5 UNSCORED open rows** (no `[Pn]` prefix): 3 in `three-bucket-otel-view-5db409` (W9.1, W10.1, W11.1) plus `streamline-constants-territories-d0cb16/GAP-4` and `p2-burndown-wave-9e4c17/6.1`. Run scorer to band them.
4. **9 empty-status rows** — 8 of them under `test-coverage-backlog-f8f5a7` (D1–D5, E2, M.1) plus the `_INDEX_open_scope_inventory` row. These rows have a P-band prefix but no Status select set; should be flipped to `Todo` or `Done`.

## Recommended cleanup ordering (high signal-to-noise)

1. **Auto-close 52 archived-plan stragglers** (categories 2 above) — biggest noise reduction; can be batched by plan slug.
2. **Patch audit-script prefix bug** — one-line fix, prevents future false-positive surfaces.
3. **Score 5 UNSCORED + assign Status to 9 empty-status rows** — turns the snapshot's `UNSCORED Todo` count from 4 → 0.
4. **Decide fate of 7 truly-orphan rows** — either scaffold the missing plan or fold them into existing successors.
5. **Triage NEW: placeholders** — 4 of the 6 are likely already covered by archived/live plans.

## Artifacts

- `artifacts/notion_recon.json` — full structured reconciliation
- `artifacts/recon_categorize.txt` — categorized per-row breakdown
- `artifacts/_recon_categorize.py` / `artifacts/_notion_recon_oneshot.py` — re-runnable scripts
- `docs/reports/plans/notion_backlog_audit_20260430.md` — original audit (with prefix bug)
