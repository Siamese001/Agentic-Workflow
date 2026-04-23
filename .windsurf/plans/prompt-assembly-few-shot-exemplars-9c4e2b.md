# Plan: Prompt Assembly — One-Shot Many-Example Exemplars

- **Slug**: `prompt-assembly-few-shot-exemplars-9c4e2b`
- **Tier**: T2 (scoped, L4 GoldenContextMixin + assembly)
- **Status**: Todo — backlog enhancement
- **Parent Plan Summary**: Ensure prompt assembly uniformly uses "one-shot many-example" (few-shot) EXEMPLARS sourced from `GoldenContextMixin` at every assembly site. Prevent zero-exemplar or single-exemplar prompts where the category matters for output-style conformance.

## Goal

Every assembled prompt whose category supports EXEMPLARS (per `Agentic Prompt Categories.txt`) includes ≥3 curated golden-context examples, drawn from a versioned exemplar bank, selected by task-similarity.

## Scope

| In Scope | Out of Scope |
|---|---|
| Audit of all prompt-assembly sites (`apps_*/engines/*assembly*.py`, `agentic_core/L0_routing/**`) | New exemplar authoring (only harness; curation is separate) |
| `GoldenContextMixin` / L4 exemplar bank interface | Dynamic few-shot selection via embeddings (future phase) |
| Assembly-gate check that rejects exemplar-eligible prompts with <3 examples | |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | ENH2.1 | ADG audit of assembly sites + current exemplar usage | 3000 | Todo | Inventory in `docs/reports/plans/` |
| W2 | ENH2.2 | Exemplar bank schema + retrieval API | 5000 | Todo | `agentic_core/L4_state/exemplars/` module with tests |
| W3 | ENH2.3 | Retrofit assembly sites to pull ≥3 exemplars | 4000 | Todo | Assembly gate blocks offending prompts; all apps_* updated |
| W4 | ENH2.4 | CI gate: `check_exemplar_coverage.py` | 2000 | Todo | Gate wired into pre-commit + `run_contract_gates.py` |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| ENH2.1 | Assembly site audit | `apps_*/engines/**`, `agentic_core/L0_routing/` | Unknown exemplar count baseline | 3000 | Todo |
| ENH2.2 | Exemplar bank | `agentic_core/L4_state/exemplars/` | Schema design | 5000 | Todo |
| ENH2.3 | Assembly retrofit | All assembly sites | Many sites | 4000 | Todo |
| ENH2.4 | CI gate | `ops_scripts/ci/` | — | 2000 | Todo |

## ADG_GRAPH_LAYER_EVIDENCE (to be filled in ENH2.1)

- MVs: `mv_hotspot_centrality`, `mv_graph_chokepoint_bridges`
- Semantic edges: `calls`, `reads_from`
- P-views: L4 consumer P-views
