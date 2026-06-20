---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\prompt-categories-coverage-audit-b8f5d3.md'
original_relative_path: '_archive\\2026-05\\prompt-categories-coverage-audit-b8f5d3.md'
source_sha256: 62781e12b0b3ee6d84962dc4664bdbb9a277fd4e5bd1cd1978c5fa0f29045196
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Prompt Categories Coverage Audit & Enforcement

- **Slug**: `prompt-categories-coverage-audit-b8f5d3`
- **Tier**: T3 (cross-layer L0→L5, assembly taxonomy)
- **Status**: Todo — backlog enhancement
- **Parent Plan Summary**: Ensure every prompt category defined in `docs/reference/03_L0_Routing/Prompt Assembly/Agentic Prompt Categories.txt` (USER PROMPT, INSTRUCTIONAL, INJECTIONS, EXEMPLARS, DEPENDENCY, META-COGNITIVE, SYNTHESIS, SYSTEM/STATE, HEALING PROPOSAL) is actively utilized in assembled prompts where applicable, with traceability per category.

## Goal

Every assembled prompt is annotated with which of the 9 categories it uses, and an assembly-time gate verifies that mandatory categories (SYSTEM/STATE, USER PROMPT) plus context-appropriate categories (INSTRUCTIONAL, INJECTIONS, EXEMPLARS, DEPENDENCY, META-COGNITIVE) are present.

## Category SSOT

See `@c:/Git/Agentic-Workflow/docs/reference/03_L0_Routing/Prompt Assembly/Agentic Prompt Categories.txt`.

| Category | Mandatory? | Applicable Layer |
|---|---|---|
| USER PROMPT | Yes | L1 |
| INSTRUCTIONAL | Context-dependent | L0→L3 |
| INJECTIONS (Role Fencing) | Yes (assembly gate) | L4/L5 → pre-L2 |
| EXEMPLARS | Context-dependent (see `prompt-assembly-few-shot-exemplars-9c4e2b`) | L1/L3 |
| DEPENDENCY | Context-dependent (RAG) | L0/L2 runtime |
| META-COGNITIVE (CoT/ToT) | Context-dependent (see `cot-reflexion-self-consistency-config-7a3f1c`) | L1/L3 |
| SYNTHESIS | L4 background only | L4 Historian |
| SYSTEM/STATE | Yes (hard gate) | Assembly gate |
| HEALING PROPOSAL | L2.3 loop only | L2.3 → L5 |

## Scope

| In Scope | Out of Scope |
|---|---|
| All assembly sites in `agentic_core/L0_routing/**` | New categories |
| Category-tagging on assembled prompts | Category taxonomy redesign |
| CI gate `check_prompt_category_coverage.py` | |
| Cross-references with plans `cot-reflexion-self-consistency-config-7a3f1c` and `prompt-assembly-few-shot-exemplars-9c4e2b` | |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | ENH3.1 | ADG + grep audit: which categories are in use today | 4000 | Todo | Coverage matrix in `docs/reports/plans/` |
| W2 | ENH3.2 | Category-tag schema + prompt envelope | 4000 | Todo | Every assembled prompt carries a category manifest |
| W3 | ENH3.3 | Retrofit assembly sites for missing applicable categories | 6000 | Todo | Mandatory categories always present; context-sensitive categories present where applicable |
| W4 | ENH3.4 | CI gate + ADR | 2000 | Todo | Gate blocks assembly with missing mandatory category |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| ENH3.1 | Coverage audit | `agentic_core/L0_routing/`, `apps_*/engines/**` | No current telemetry on category use | 4000 | Todo |
| ENH3.2 | Category manifest schema | `agentic_core/L0_routing/` | Envelope shape needs decision | 4000 | Todo |
| ENH3.3 | Assembly retrofit | All assembly sites | Dependency on ENH1/ENH2 for META-COGNITIVE + EXEMPLARS | 6000 | Todo |
| ENH3.4 | CI gate + ADR | `ops_scripts/ci/`, `docs/architecture/adr/` | — | 2000 | Todo |

## Dependencies

- ENH1 (`cot-reflexion-self-consistency-config-7a3f1c`) — supplies META-COGNITIVE implementation
- ENH2 (`prompt-assembly-few-shot-exemplars-9c4e2b`) — supplies EXEMPLARS implementation

## ADG_GRAPH_LAYER_EVIDENCE (to be filled in ENH3.1)

- MVs: `mv_hotspot_centrality`, `mv_dependency_cone_risk`
- Semantic edges: `calls`, `flows_to`, `reads_from`
- P-views: L0 assembly P-views
