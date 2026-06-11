---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\w7-p1-adr-tooling-followup-b5c9e2.md'
original_relative_path: 'w7-p1-adr-tooling-followup-b5c9e2.md'
source_sha256: fa5b24e3aa0c6dc145ae5b45cab3369a88d54999957d27782164662222444594
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_type: refactor
---

# W7.1-P1 + ADR Revision + Tooling Follow-up

- **Plan ID**: `w7-p1-adr-tooling-followup-b5c9e2`
- **Parents**: `sc1-structural-block-closure-f9e3b1`, `ssot-and-guardian-backlog-f1a5c4`, `w6-w7-continuation-a7b3d2`
- **ADR reference**: ADR-051 (SC-1 remediation — to be revised)
- **Status**: In-Progress
- **Start**: 2026-04-24
- **Target completion**: same session

## Intent

Close the "Recommended Next Actions" follow-up batch from the prior session:

1. **Update ADR-051 + companion plan** to reflect 3-violation reality (not 54).
2. **W7.1-P1**: Fix the 3 UWG-bypass sites (`self._path.parent.mkdir` → `ensure_dir(...)` from `agentic_core.L2_execution.utils.write_gateway`).
3. **Enhance triage classifier** `tools/debug/_w6_3_substring_triage.py` with 4 context filters (argparse help, raise arg, re.compile, prose).
4. **Defer W6.1 BARE-guardian pass** to dedicated sessions (unchanged from prior plan's Non-Goals).

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| **W1** | P0 | Plan + Notion post | 1,000 | git clean | In Progress | Plan committed + Notion row |
| **W2** | P1 | ADR-051 + SC-1 plan revision | 2,000 | Prior session's findings authoritative | Todo | ADR status Superseded-by-scope-revision OR Accepted-with-revision; SC-1 plan updated |
| **W3** | P2 | W7.1-P1 fix 3 UWG bypass sites | 2,500 | `ensure_dir` is canonical governed-mkdir | Todo | All 3 sites use `ensure_dir`; py_compile clean; commit + push |
| **W4** | P3 | Enhance triage classifier | 3,000 | AST parent-chain context detection straightforward | Todo | 4 new filters added; classifier re-runs; reduced ACCIDENTAL_CONCAT tally documented |
| **W5** | P4 | Notion sync | 1,000 | MCP notion available | Todo | 3 Done rows + parent-plan status updates |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| P0 | Plan + Notion post | `.windsurf/plans/w7-p1-adr-tooling-followup-b5c9e2.md`, Notion Wave/Phase row | None | 1,000 | In Progress |
| P1 | ADR-051 + SC-1 plan revision | `docs/architecture/adr/ADR-051-sc1-structural-block-remediation.md`, `.windsurf/plans/sc1-structural-block-closure-f9e3b1.md` | Must preserve ADR audit trail; add "Amendment" section rather than overwrite rationale | 2,000 | Todo |
| P2 | W7.1-P1 fix 3 sites | `agentic_core/L3_orchestration/exit_control/ledger_integrity.py`, `agentic_core/L3_orchestration/exit_control/runtime_hitl_ledger.py`, `apps_shared/integrations/runtime_hitl_integration.py` | Import path must be absolute `agentic_core.L2_execution.utils.write_gateway`; function call returns `Path` but original mkdir returned `None` — `ensure_dir` return value ignored at call sites (same semantics) | 2,500 | Todo |
| P3 | Enhance triage classifier | `tools/debug/_w6_3_substring_triage.py` | Must detect `argparse.add_argument(help=...)`, `raise Exception(...)` first arg, `re.compile(...)` first arg, `.append(...)` on prose-name lists | 3,000 | Todo |
| P4 | Notion sync | 3 Wave/Phase rows | MCP serialization 1 call per response | 1,000 | Todo |

## Gap Register

| Gap | Impact | Mitigation |
|---|---|---|
| ADR-051 was authored with 54-violation scope; revision must preserve audit integrity | Could look like sloppy ADR authorship | Add explicit "Amendment 2026-04-24" section below original; do not rewrite Decision section |
| `ensure_dir` import may introduce a layering issue (L3 importing from L2) | Could re-violate layer gravity | Verified: agentic_core L2_execution.utils.write_gateway is a lower-layer utility, safe to import from L3 (gravity correct). `apps_shared` importing agentic_core is also correct (apps depend on core) |
| Re-running SC-1 classifier after P2 may still show 3 rows if ADG snapshot is pre-edit | Noise in verification | Regenerate ADG after P2 commit, then re-run classifier as confirmation |
| Triage-classifier enhancement adds complexity to a debug tool | Future maintenance burden | Keep filters simple; each is a 3–5 line AST parent check |

## ADG_HOTSPOT_REPORT

This is execution-oriented; the 3 UWG-bypass sites are THE hotspots per
W7.1-P0 classifier output. Classification:

| # | Module | Layer | Fan-in | Archetype | Surface | Subtype |
|---|---|:---:|---:|---|:---:|:---:|
| 1 | `agentic_core/L3_orchestration/exit_control/ledger_integrity.py:222` | L3 | 0 | STATE_NODE | Write | 1 |
| 2 | `agentic_core/L3_orchestration/exit_control/runtime_hitl_ledger.py:122` | L3 | 0 | STATE_NODE | Write | 1 |
| 3 | `apps_shared/integrations/runtime_hitl_integration.py:207` | L_APP | 0 | STATE_NODE | Write | 1 |

All three are STATE_NODE archetype (SQLite-backed ledger stores), Write
Surface, Subtype 1 (direct mutation bypass of UWG). The remediation is
identical across all three.

## ADG_GRAPH_LAYER_EVIDENCE

### Materialized views cited (≥3)

1. **`v_p0_write_bypass_uwg`** — the SSOT for all 3 violations; classifier
   output confirmed via `SELECT * FROM v_p0_write_bypass_uwg`.
2. **`mv_graph_critical_path_blast_radius`** — all 3 modules have fan_in=0
   (no other code imports them directly). Impact is scoped to their own
   runtime.
3. **`mv_hotspot_centrality`** — none of the 3 modules are CENTRAL_DEPENDENCY
   or ORCHESTRATOR; they are leaf STATE_NODE stores. Confirms low blast
   radius and supports the single-pass remediation strategy.

### Semantic edges used

- `writes_to` — the flagged edge; after remediation, the write goes through
  `ensure_dir` which is itself in `agentic_core/L2_execution/utils/write_gateway.py`
  and already audited at gate-time as a governed path.
- `imports` — post-fix, 3 new `imports` edges appear from the fixed modules
  to `write_gateway`; these are gravity-correct (L3→L2, L_APP→L2).

### P-view cross-references

- `v_p0_write_bypass_uwg` (primary).
- Post-fix: should drop to 0 rows, confirming closure.

## Author-Gate Checkpoints

None expected during execution. The fix is mechanical (import + single-line
replacement); the ADR revision is editorial (amendment); the triage-classifier
enhancement adds filtering logic without changing disposition categories.
Bypass condition #2 (single correct solution exists) applies per
`author-gate-enforcement.md`.

## Success Criteria

1. ADR-051 has an Amendment section noting 3-violation reality; companion
   plan waves collapsed from 5 to 2 (P0 classify → P1 fix).
2. All 3 UWG-bypass sites compile and run with `ensure_dir`; `git grep
   "_path.parent.mkdir"` on the 3 files returns no results.
3. Enhanced triage classifier runs clean; ACCIDENTAL_CONCAT tally drops from
   30 → expected ~4.
4. 3 Wave/Phase Done rows posted to Notion.
5. All commits pushed to origin/main.

## Non-Goals

- Not executing W6.1 BARE-guardian 1696-site pass — deferred per constitutional
  collision-avoidance with concurrent L5 v4 G-04 work.
- Not regenerating ADG snapshot (that's the concurrent agent's work path).
- Not changing `ensure_dir` itself or introducing a new UWG primitive.

## Token Budget

Total: **9,500 tokens** (1,000 + 2,000 + 2,500 + 3,000 + 1,000).
Status: 🟢 GREEN.

## Execution Order

P0 → P1 → P2 → P3 → P4 sequential. Commit + push after each phase.
