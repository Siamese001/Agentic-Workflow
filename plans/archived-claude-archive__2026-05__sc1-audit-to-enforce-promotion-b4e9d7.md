---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\sc1-audit-to-enforce-promotion-b4e9d7.md'
original_relative_path: '_archive\\2026-05\\sc1-audit-to-enforce-promotion-b4e9d7.md'
source_sha256: fdbbeadbb713db549a2a26d581c8a8b7550319dd99cce1ad2932212bbd92600f
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan — SC-1 Audit-Mode → Enforce-Mode Promotion

**Slug**: `sc1-audit-to-enforce-promotion-b4e9d7`
**Status**: Draft (awaiting /plan kick-off)
**Tier**: T2 (scoped, single concern: gate-mode flip + backlog clean-up)
**Parent marker**: `DEFERRED_SCOPE: plan=adg-pipeline-e2e-5287a1 wave=W8 phase=W8.1 layer=L_TOOLS fan_in=3 surface=Security coverage_gap_pct=60.0 est_tokens=5500`
**Priority band**: **P2** (auto-scored)
**ADG baseline**: latest `adg_indexed_<ts>.sqlite` at kick-off
**ADG provenance**: `backend=sqlite, snapshot=adg_indexed_<ts>.sqlite`

---

## Intent

SC-1 (structure-contract rule 1: "actionable surface has a schema") currently runs in **audit mode** with a 54-violation backlog. Every new commit can add more SC-1 violations without blocking CI. This plan remediates the 54 baseline violations and flips the gate to **enforce mode** so the backlog cannot grow.

---

## ADG_GRAPH_LAYER_EVIDENCE

Primary drivers (constitutional §22):

- **Materialized views (≥3)**: `mv_actionable_surface_without_schema` (the SC-1 backlog itself), `mv_tool_surface_overlap` (flag duplicate surfaces to collapse before schema-adding), `mv_structured_output_gaps` (identify which surfaces need which schema shape), `mv_task_contract_gaps` (contract coverage)
- **Semantic edges**: `emits_side_effect`, `resolves_callsite` — identify actionable surfaces
- **P-views**: `v_p1_not_on_spine` (low-priority backlog items — deprioritize), `v_p0_apps_direct_infra` (must fix first)

## ADG_HOTSPOT_REPORT

Ranked from `mv_actionable_surface_without_schema` at kick-off. Target archetypes:

- **SAFETY_GATEKEEPER** (policy / guardrail surfaces without schema — top priority)
- **ORCHESTRATOR** (tool-dispatch surfaces — schema enforces contract)
- **CENTRAL_DEPENDENCY** (widely-imported surfaces — schema-adding ripples broadly)

Impact score = `1 × (1 + log10(1 + fan_in)) × layer_multiplier × surface_boost(Security=1.5)`.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|:---:|---|:---:|---|
| W1 | P1.1 | Triage 54 violations: classify into P0/P1/P2 + flag duplicates | 1000 | MV populated at kick-off | Todo | CSV at `artifacts/reports/sc1_triage_<ts>.csv` with 54 classified rows |
| W2 | P2.1 | Fix P0 (Security surfaces) — add schemas | 2000 | ≤15 P0 items | Todo | Each P0 surface has schema + test |
| W3 | P3.1 | Fix P1 (Orchestration surfaces) | 1500 | ≤20 P1 items | Todo | Each P1 surface has schema |
| W4 | P4.1 | Suppress P2 (isolated / experimental) via exemption registry + ADR | 500 | exemption gate exists | Todo | Exemption rows posted; gate accepts |
| W5 | P5.1 | Flip `check_sc1.py` from audit → enforce + ratchet baseline to 0 | 500 | W2–W4 all green | Todo | Gate exits non-zero on new SC-1 violation |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|:---:|:---:|
| P1.1 | Triage | `tools/reports/sc1_triage.py` (new) | Classify with MV joins | 1000 | Todo |
| P2.1 | P0 schema-add | ~15 actionable surfaces in L5/L3 | Schema shape discovery | 2000 | Todo |
| P3.1 | P1 schema-add | ~20 surfaces in L2/L3 | Contract coverage | 1500 | Todo |
| P4.1 | P2 exemption | `artifacts/exemptions/sc1_exemptions.yaml` + ADR | Justify each exemption | 500 | Todo |
| P5.1 | Gate flip | `ops_scripts/ci/check_sc1.py` + `.pre-commit-config.yaml` | Baseline ratchet | 500 | Todo |

**Total est**: 5500 tokens (matches marker)

## Gap Register

| Gap | Impact | Resolution Wave |
|---|---|---|
| G-1 | 54-item backlog grows unchecked | W2–W5 |
| G-2 | No triage record | W1 |
| G-3 | Exemption path undocumented | W4 |

## Success Criteria (rollup)

1. 54 SC-1 violations → 0 (via fix + exemption)
2. `check_sc1.py` runs in enforce mode
3. Baseline ratchet at 0 — any new SC-1 violation blocks commit
4. ADR documents P2 exemption policy
5. Triage CSV in `docs/reports/plans/`

## Dependencies

- MV `mv_actionable_surface_without_schema` populating — VERIFIED 2026-04-22 (51 MVs present)
- Guardian-exemption gate `check_guardian_exemptions.py` extant

## Out of Scope

- Other SC-* rules (SC-2, SC-3 have separate backlogs)
- AP-* (anti-pattern) promotions
- Surface collapse / deduplication beyond exact duplicates flagged by MV
