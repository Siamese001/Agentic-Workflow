---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\agentic-antipattern-tier1-9f2c8a.md'
original_relative_path: 'agentic-antipattern-tier1-9f2c8a.md'
source_sha256: 23ff996d73af2719a94d044563aa7a4b0b36616d9bc7aab7313a2e850c9f74ab
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-20'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Agentic Antipattern Tier 1 — 9 New Categories

**Plan ID:** `agentic-antipattern-tier1-9f2c8a`
**Tier:** T3 (cross-layer: registry + AST detectors + burndown report + ADG regen)
**ADG snapshot at plan time:** `adg_indexed_04202026_1802.sqlite` (healthy sqlite+redis)
**Decision source:** Author-Gate Tier 1 selection (9 patterns) — DECISION_CAPTURED emitted
**SSOT:** `.windsurf/plans/agentic-antipattern-tier1-9f2c8a.md` (this file)

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1.1, P1.2 | Registry: enum + severity map | 3k | types file unchanged shape | 🟢 pending | 9 new `AntipatternCategory` members + `_SEVERITY_MAP` entries, py_compile clean |
| W2 | P2.1, P2.2, P2.3 | AST detectors in `visitors/core.py` for the 6 AST-local patterns | 12k | existing visitor API stable | 🟢 pending | Unit tests pass for each new detector on fixture files |
| W3 | P3.1, P3.2 | Cross-layer detectors (A3 Author-Gate-gap, A5 chokepoint-bypass) via edge analysis | 8k | edge kinds `calls`/`dispatches_to` populated | 🟡 pending | Edge-based detection produces non-zero count where expected, zero FP on guardrail-exempted call sites |
| W4 | P4.1, P4.2 | Burndown report rollup: include A4 (write_bypass_uwg) in P0 `by_kind`, wire new categories | 4k | `_print_defect_table` is the canonical generator | 🟢 pending | Regenerated `adg_burndown_table.json` shows new `by_kind` entries |
| W5 | P5.1 | ADG regen + burndown diff + ratchet review | 3k | `tools/generate_full_adg.py` succeeds | 🟡 pending | New snapshot created, burndown shows all 9 categories, no ratchet regression on existing counts |

**Token total estimate:** ~30k (GREEN — well under 100k budget)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Add 9 enum values to `AntipatternCategory` | `agentic_core/adg/runtime/antipattern_types.py` | None | 1.5k | pending |
| P1.2 | Add severity bindings in `_SEVERITY_MAP` | same file | Ensure HIGH→P1, CRITICAL→P0 mapping correct | 1.5k | pending |
| P2.1 | AST detector: `exception_type_erasure` (`raise X(...)` inside `except` with no `from exc`) | `agentic_core/adg/extraction/visitors/core.py` | Distinguish intentional wrapping vs erasure — rule: flag only when `raise` has no `cause` AND new exception type != caught type | 2.5k | pending |
| P2.2 | AST detectors: `cleanup_masks_primary`, `finally_overrides_outcome` | same | `finalbody` scanning; flag `Return`/`Break`/`Continue` directly, flag unguarded risky calls in finally | 3k | pending |
| P2.3 | AST detectors: `unbounded_agent_loop` (A1), `llm_output_unvalidated` (A2), `hallucinated_tool_name` (A15) | same | A1: `while True` in `*Agent.heal`/`*Agent.run` with no counter; A2: `json.loads` on LLM response var with no `validate_*`/`Pydantic.parse` follow-up; A15: `tools[x]`/`getattr(toolkit,x)` where `x` sourced from LLM output var without `in registry` check | 6.5k | pending |
| P3.1 | Edge detector: `missing_hitl_on_irreversible` (A3) | `agentic_core/adg/extraction/` (new visitor or edge post-processor) | Build reachability from `*Agent.*` tool nodes to `os.remove`/`shutil.rmtree`/`db.delete`/`write_gateway` ops; flag when path has no guardrail edge | 4.5k | pending |
| P3.2 | Edge detector: `chokepoint_bypass` (A5) | same | Call to tool resolving *not* through `reasoning_chokepoint` or `execution_guardrail_chokepoint` module | 3.5k | pending |
| P4.1 | Burndown rollup: promote A4 `write_bypass_uwg` from P-view only to P0 `by_kind` | `tools/generate/reporting/reports.py` (`_print_defect_table`) | Already detected — only needs aggregation into `summary.P0.by_kind` | 1.5k | pending |
| P4.2 | Wire new categories into `by_kind` rollup | same | Ensure severity→band routing honors `severity_bands.py` SSOT | 2.5k | pending |
| P5.1 | Run `python tools/generate_full_adg.py`, capture new burndown, validate ratchet | — | May surface many new violations — expected; triage via guardian exemption if needed | 3k | pending |

---

## Proposed Enum + Severity Additions

```python
# In AntipatternCategory (antipattern_types.py)
EXCEPTION_TYPE_ERASURE = "exception_type_erasure"          # P1
CLEANUP_MASKS_PRIMARY = "cleanup_masks_primary"            # P2
FINALLY_OVERRIDES_OUTCOME = "finally_overrides_outcome"    # P1
UNBOUNDED_AGENT_LOOP = "unbounded_agent_loop"              # P1
LLM_OUTPUT_UNVALIDATED = "llm_output_unvalidated"          # P1
MISSING_HITL_ON_IRREVERSIBLE = "missing_hitl_on_irreversible"  # P0
CHOKEPOINT_BYPASS = "chokepoint_bypass"                    # P0
HALLUCINATED_TOOL_NAME = "hallucinated_tool_name"          # P1
# A4 is already an edge/P-view — no new enum; rollup fix only

# In _SEVERITY_MAP
EXCEPTION_TYPE_ERASURE: HIGH
CLEANUP_MASKS_PRIMARY: MEDIUM
FINALLY_OVERRIDES_OUTCOME: HIGH
UNBOUNDED_AGENT_LOOP: HIGH
LLM_OUTPUT_UNVALIDATED: HIGH
MISSING_HITL_ON_IRREVERSIBLE: CRITICAL
CHOKEPOINT_BYPASS: CRITICAL
HALLUCINATED_TOOL_NAME: HIGH
```

---

## ADG_GRAPH_LAYER_EVIDENCE

- `mv_graph_reverse_dependency_hotspots` — rank catch sites in agent modules by fan-in for A3/A5 scoping
- `mv_hotspot_centrality` — identify central agent dispatchers where A1/A11 loops most damaging
- `mv_debt_concentration_hotspots` — validate new violations cluster in expected layers (L1/L2/L3), not random
- Semantic edges used: `calls`, `resolves_callsite`, `flows_to`, `controls_flow`, `emits_side_effect`
- P-views cross-referenced: `v_p0_write_bypass_uwg` (A4 source), `v_p0_apps_direct_infra` (A3/A5 proximity)

## ADG_HOTSPOT_REPORT (pre-implementation estimate)

| Pattern | Layer(s) | Expected fan-in | Archetype | Surfaces crossed |
|---------|----------|-----------------|-----------|-------------------|
| A1 unbounded_agent_loop | L1, L3 | high (SovereignBaseAgent.heal) | ORCHESTRATOR | Execution, Observability |
| A2 llm_output_unvalidated | L1, L2 | medium | STATE_NODE | Execution, State |
| A3 missing_hitl_on_irreversible | L2, L4 | high (write_gateway) | SAFETY_GATEKEEPER | Write, Security |
| A5 chokepoint_bypass | L5 | very high (chokepoints are central) | SAFETY_GATEKEEPER | Security, Execution |
| A15 hallucinated_tool_name | L0, L2 | medium (capability registry) | CENTRAL_DEPENDENCY | Execution, Security |

Layer multipliers applied per constitutional invariants §6 (L0/L5 ×2.0, L2/L3 ×1.0–1.75).

**Surfaces referenced in this report** (full names for §22 evidence compliance): Execution Surface, Write Surface, Security Surface, State Surface, Observability Surface.

---

## Rollback Checkpoints

- After W1: enum/map only — rollback = revert `antipattern_types.py`
- After W2: AST detectors — rollback = revert `visitors/core.py`
- After W3: edge detectors — rollback = delete new visitor module
- After W4: report rollup — rollback = revert `_print_defect_table`
- After W5: ADG snapshot — keep prior snapshot; rollback = use `adg_indexed_04202026_1802.sqlite`

## Verification Gates

1. `python -m py_compile` on every touched file
2. `python tools/generate_full_adg.py` exits 0 (or only pre-existing SC-1 unrelated failures)
3. New `adg_burndown_table.json` contains 8 new entries in `summary.P*.by_kind` (+1 rollup for A4)
4. `python ops_scripts/ci/run_contract_gates.py` passes
5. No pre-existing `by_kind` kind sees gross count change >5% (sanity — we're adding detectors, not modifying existing ones)

---

## Out of Scope (Tier 2 deferred)

A6 missing_llm_timeout, A8 prompt_injection_surface, A11 circular_agent_delegation, A12 tool_result_unvalidated, A13 missing_otel_span, A7/A9/A10/A14 (Tier 3). Tracked as known gaps.
