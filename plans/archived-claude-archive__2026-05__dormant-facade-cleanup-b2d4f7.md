---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\dormant-facade-cleanup-b2d4f7.md'
original_relative_path: '_archive\\2026-05\\dormant-facade-cleanup-b2d4f7.md'
source_sha256: 966e87f698a9c58631adf8f092f89952a46b4c9d4701969e866ad269bd44fd43
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Dormant Facade Cleanup — apps_portfolio R1-R6

Status: **CLOSED 2026-05-01.** W1 done; W2/R1/R6 cancelled-by-evidence; W3 done; W4 blocked-by-P2-ratchet (deferred-scope filed); W5 done.
Created: 2026-05-01
Last updated: 2026-05-01 (W5 closure)
Owner: Cursor Agent
Plan slug: `dormant-facade-cleanup-b2d4f7` (renamed in spirit — the "dormant" framing was wrong)

## Mission

Execute recommendations R1–R6 from the apps-portfolio consolidation v2 assessment (`artifacts/_scan_consolidation_v2_output.txt` + `artifacts/_scan_consolidation_v3_output.txt`). The recommendations were derived from ADG graph evidence showing zero static cross-app integration between candidate producers (`apps_eval`, `apps_research`, `apps_exec`, `apps_rfp`) and consumers (`apps_rg`, `apps_lic`), with `apps_shared/adapters/research_facade.py` confirmed as dormant scaffolding (zero callers).

Predecessor plans:
- `apps-portfolio-integrated-evaluation-7d3a91.md` (closed) — established the K1 KEEP BOTH and N1 W3/W4 no-op verdicts.
- `apps-cross-app-duplication-review` (NEW, P3 backlog row) — original duplication concern; this plan does NOT reopen it.
- `apps-portfolio-operational-grounds-review` (NEW, P5 backlog row) — operational metrics review; this plan does NOT preempt it.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| **W1** | W1.1 | Scope verification: confirm dormant set | ~3k | **Done** | W1.1 evidence below; INVALIDATED the "dormant" hypothesis |
| **W2** | W2.1 | ~~Archive dormant scaffolding~~ | 0 | **CANCELLED** | `research_facade.py` has a live caller in `apps_rg/integrations/company_research_loader.py` (added today, post-snapshot). Archive would break the HOP-0.6-COMPANY-RESEARCH 4-mode loader. |
| **W3** | W3.1 | Document `rg_orchestrator_facade` AND `research_facade` as the two working cross-app integration patterns (R3, expanded) | ~5k | Ready | One reference doc under `docs/architecture/` documenting both patterns + their fan-in evidence |
| **W4** | W4.1 | ADG snapshot regeneration (R4) | ~2k | **BLOCKED on unrelated CI gate** | Regen attempted; aborted by P2 ratchet hard-fail (17 MEDIUM antipatterns over ceiling 0). DEFERRED_SCOPE filed for the antipattern remediation. |
| **W5** | W5.1 | Notion + memory writebacks: plan registry, wave/phase closure, deferred-scope row, memory pattern | ~4k | **Done** | Plans DB row `35427693-f55c-818f-b3fa-c08c58fcca9f` Status=Complete; Wave/Phase closure row `35427693-f55c-8186-bbe9-f66d341fba37`; deferred-scope row `35427693-f55c-81a3-a441-ef45a54cf4a0`; memory pattern updated |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **W1.1** | Scope verification | `apps_shared/adapters/research_facade.py`, sibling adapters, tests | None — read-only | 3k | Ready |
| **W2.1** | Archive dormant scaffolding | `git mv apps_shared/adapters/research_facade.py archives/research_facade_20260501/`; remove any orphaned tests | Need to check tests reference + import surface | 3k | Blocked on W1 |
| **W3.1** | Cross-app pattern doc | New `docs/architecture/cross-app-facade-pattern.md` documenting `rg_orchestrator_facade` shape; reference from apps_shared if there's an existing README | Document doesn't exist yet — pure write | 5k | Independent |
| **W4.1** | Regenerate ADG snapshot | `python tools/generate_full_adg.py` | Long-running command; not blocking for this plan but recommended before next T2/T3 | 2k | Optional |
| **W5.1** | Notion + memory writebacks | Plans DB row, Wave/Phase closure row, ADR Registry row for archive, memory pattern updates | MCP serialization (Notion is remote — one per response) | 4k | Final |

## Recommendation Mapping

| Rec | Wave | Status |
|---|---|---|
| R1 — Archive `research_facade.py` | W2 | **CANCELLED** — facade has live caller in apps_rg (W1 evidence) |
| R2 — Don't pursue original consolidation | (already closed via K1 + N1) | Holds |
| R3 — Document cross-app facade patterns | W3 | EXPANDED — covers both `rg_orchestrator_facade` AND `research_facade` |
| R4 — Regenerate ADG snapshot | W4 | NOW MANDATORY — staleness was the root cause of the wrong R1 verdict |
| R5 — Operational-grounds review | (already P5 in backlog) | Holds |
| R6 — Cleanup dormant facade scaffolding | W2 | **CANCELLED** — nothing to clean up; both candidate "dormants" are alive |

## ADG_GRAPH_LAYER_EVIDENCE

> Constitutional §22 compliance.

**Domain**: dormant facade cleanup; cross-app integration documentation

**Materialized views consulted**:
1. `mv_graph_reverse_dependency_hotspots` — confirmed zero fan-in to `research_facade` and `fetch_company_brief`.
2. `mv_dependency_cone_risk` — n/a (target is a leaf with zero callers, no cone).
3. `mv_chokepoint_bridges` — n/a.

**Semantic edges** beyond raw `imports`:
- `imports` — primary evidence for caller existence (zero across all candidate apps).
- `flows_to`, `resolves_callsite` — cross-app: zero in either direction (per v2 + v3 scans).

**P-view cross-references**:
- n/a — dormant code with no integration.

**Rationale**: the archive operation is justified by graph absence, not graph presence. R1 is safe because the static graph confirms no caller references the file.

## ADG_HOTSPOT_REPORT

| Hotspot scope | Layer | Fan-in | Archetype | ADG Surface | Layer multiplier | Impact (rel.) |
|---|---|---:|---|---|---:|---:|
| `apps_shared/adapters/research_facade.py` | L_SHARED | **0** | DORMANT_LEAF | None | 1.0 | **trivial** |
| `apps_shared/adapters/rg_orchestrator_facade.py` (W3 documentation target) | L_SHARED | 2 (apps_eval) | CENTRAL_DEPENDENCY | Execution | 1.0 | low |

The archive target has zero fan-in — that's the entire reason it's safe to remove. The documentation target (`rg_orchestrator_facade`) has 2 callers from `apps_eval/engines/scenario_runner.py`, which is the canonical example of the cross-app pattern this plan documents.

## W1.1 Evidence

> Status: **DONE 2026-05-01.** Snapshot used: `artifacts/adg/adg_indexed_05012026_0632.sqlite` (06:32 UTC).

`apps_shared/adapters/research_facade.py` (164 lines) is **NOT dormant**. Direct file inspection found:

- `apps_rg/integrations/company_research_loader.py:112` — `from apps_shared.adapters.research_facade import fetch_company_brief` (production import inside `_try_apps_research()`, mode 2 of the 4-mode CompanyBrief loader).
- `apps_rg/types/company_research.py:6` — documentation cross-reference listing the facade as one of the canonical brief sources.
- HOP-0.6-COMPANY-RESEARCH design (per `.cursor/plans/apps-rg-narrative-and-company-research-e3f8c1.md` P2.1) treats `research_facade` as the *cross-app generation* mode of a 4-mode loader (manual upload | apps_research subprocess | internal engine | tavily supplement).

Why the ADG showed zero callers: `company_research_loader.py` was added today, after the 06:32 snapshot. This is the THIRD instance this session of stale-snapshot-misses-today's-edits.

**Verdict**: R1 + R6 cancelled. The facade is the live integration path that the original "consolidate apps_research+exec to feed apps_rg/lic" framing was actually asking about — it just happened *after* my earlier read.

## Definition of Done

- [x] W1.1 evidence section populated; "dormant" hypothesis invalidated
- [x] W2.1 cancelled (facade in active use)
- [x] W3.1 cross-app pattern doc written: `docs/architecture/cross-app-facade-pattern.md`
- [x] W4.1 BLOCKED on P2 ratchet; deferred-scope row filed `35427693-f55c-81a3-a441-ef45a54cf4a0` (closure-by-deferral)
- [x] W5.1 Notion writebacks complete (Plans, Wave/Phase, deferred-scope); memory pattern updated

## Closure Summary

Net outcome: **1 new doc, 0 code changes**. The correct outcome — evidence said don't touch live tree. The plan started as "archive dormant scaffolding" and ended as "document why both candidate dormants are alive" — a complete reframing driven by W1 source-of-truth evidence.

Key lesson: ADG snapshot at 06:32 missed today's `apps_rg/integrations/company_research_loader.py` edit (HOP-0.6 wiring). Source-of-truth read of the file saved the archive operation from breaking production. This is the **third stale-snapshot save in one session** — the verification protocol is now in `docs/architecture/cross-app-facade-pattern.md` §"Verifying a facade is in active use".

Follow-up filed: `p2-ratchet-medium-antipattern-remediation` (Wave/Phase row `35427693-f55c-81a3-a441-ef45a54cf4a0`, P5 by formula, P2 by operational urgency — 17 MEDIUM antipatterns blocking ADG regen).

## Out of Scope (DEFERRED_SCOPE candidates)

- Building the producer-feed integration that `research_facade.py` was scaffolded for. That's the content of `apps-cross-app-duplication-review` + `apps-portfolio-operational-grounds-review` backlog rows.
- Touching `apps_lic/HOP2ResearchAgent` or any consumer-side research surface. Out of scope.
- Refactoring the `governed_app_runner.py` substrate. Working as designed per W4 closure of the prior plan.

## Next Action

None — plan closed. Operator decides whether to take up `p2-ratchet-medium-antipattern-remediation` next, or another item from the backlog.
