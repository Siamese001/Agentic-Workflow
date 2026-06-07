# Per-Module Audit Follow-Up — agentic_core Evaluation / Control Pattern

**Slug**: `agentic-core-eval-control-audit-per-module-followup-c8e3f1`
**Parent**: `.cursor/plans/agentic-core-eval-control-audit-b7d4a2.md`
**Parent report**: `docs/reports/agentic_core_eval_control_audit/2026-05-02.md`
**Date created**: 2026-05-02
**Tier**: T3 read-only (same as parent)
**Status**: Draft

---

## 1. Why This Plan Exists

The parent audit at `docs/reports/agentic_core_eval_control_audit/2026-05-02.md` used archetype grouping to stay within a manageable row count (121 rows). Four of those rows collapse multiple dozens of modules behind a single recommendation. That grouping is defensible — the modules share a family — but it hides the possibility that individual modules inside the group diverge from the family default.

This follow-up plan re-opens those four grouped rows and produces a per-module recommendation for each constituent file, using the same fixed decision enum from the parent (`None` | `Judge` | `Hybrid (Judge + Ensemble)` | `Ensemble Only`) and the same Qwen 32B vLLM default.

## 2. Non-Goals (inherited from parent)

- No code changes, no patches, no refactors, no file writes outside the report.
- No new abstractions, no agent swarms, no multi-agent ensembles.
- No changes to existing runtime wiring.
- No invalidation of the parent audit rows — this plan EXTENDS the parent report by refining grouped rows, never contradicts it.

## 3. Grouped Rows in Scope

| Parent row # | Parent path | Count | Notes |
|---|---|---|---|
| 67 | `agentic_core/L3_orchestration/reasoning/*` | 94 items | Mixed: reflexion / rewoo / recursive / planners |
| 110 | `agentic_core/L5_safety/reasoning/*` | 92 items | Mixed: rule-based + semantic safety lanes |
| 113 | `agentic_core/L5_safety/v5/*` | 20 items | v5 module group |
| 120 | `agentic_core/evaluation/judges/*` | 20 items | External + local judges |

Total: 226 modules to refine.

## 4. Deliverable

A single Markdown file at `docs/reports/agentic_core_eval_control_audit/2026-05-02-per-module-followup.md` (or dated as the day executed) containing four sub-reports, one per grouped row, each with a per-module recommendation table using the same 13-column schema as parent Section 2.

### Required file layout

```
# Per-Module Audit Follow-Up — <YYYY-MM-DD>

## L3_orchestration/reasoning — per-module table (94 rows)
## L5_safety/reasoning — per-module table (92 rows)
## L5_safety/v5 — per-module table (20 rows)
## evaluation/judges — per-module table (20 rows)

## Cross-Row Consistency Notes
## Aggregate Deltas vs Parent Audit
## Gaps
```

## 5. Execution Waves

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.1 | Enumerate the 226 modules; read minimal-needed slice of each to confirm role | ~40k | ADG MCP is green; filesystem read allowed on all four paths | pending | Every module has a role verdict (structural / semantic / offline / harness) |
| W2 | W2.1, W2.2 | Per-module scoring on the fixed decision enum + Qwen role | ~35k | No module requires code reading beyond first 80 lines + docstring | pending | Every module has a row with all 13 columns populated |
| W3 | W3.1 | Cross-consistency: verify the 226 rows agree with parent Section 3 layer rollup | ~10k | Parent rollup is authoritative | pending | No row contradicts parent rollup without a `## Cross-Row Consistency Notes` entry explaining why |
| W4 | W4.1 | Author the report; move to canonical path via cmd-copy (parent precedent) | ~20k | `.codeiumignore` still blocks `docs/reports/`; cmd-move works | pending | File at `docs/reports/agentic_core_eval_control_audit/<date>-per-module-followup.md` |

## 6. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.1 | Module enumeration + role classification | 4 directory listings + ~50 targeted read_file slices (first 40 lines each) | Large directories return symbol-level noise; mitigate via list_dir only | 40k | pending |
| W2.1 | L3_orchestration/reasoning per-module scoring | 94 modules | Reflexion / rewoo / recursive / planner sub-families each need a different default | 20k | pending |
| W2.2 | L5_safety/reasoning + L5_safety/v5 + evaluation/judges per-module scoring | 92 + 20 + 20 modules | Some L5_safety/reasoning modules already have tests — may short-circuit role determination | 15k | pending |
| W3.1 | Cross-consistency vs parent Section 3 | all 226 rows | Disagreements between sub-family defaults and parent layer default must be flagged | 10k | pending |
| W4.1 | Final assembly + move to canonical path | single output MD | `.codeiumignore` staging workaround (repo-root staging + `cmd /c move`) same as parent | 20k | pending |

## 7. Row Schema (same as parent Section 2)

```
| component_path | layer_or_surface | component_role | recommended_decision | qwen_32b_vllm_role | deterministic_checks_that_remain | judge_rubric_needed | ensemble_trigger_if_any | risk_level | cost_posture | rationale | repo_evidence | divergence_from_parent_group |
```

The 13th column (`divergence_from_parent_group`) is new vs parent: `yes` when the per-module decision differs from the parent grouped row's decision; `no` otherwise. A `yes` value requires an entry in Cross-Row Consistency Notes.

## 8. Decision Tree (inherited from parent §9.2, unchanged)

1. Is the module structurally checkable (schema / hash / HMAC / enum / allowlist / policy-hash / invariant)? → `None`
2. Else, is it a semantic judgment (groundedness / trajectory / intent / safety-classification / claim-extraction / refactor-readiness)? → `Judge` (Qwen primary)
3. Else, is it high-risk AND on a user-visible / durable-mutation path? → `Hybrid (Judge + Ensemble)`
4. Else, is it offline / shadow / harness / variance measurement? → `Ensemble Only`
5. Else → review and document gap.

## 9. Qwen 32B vLLM Role Assignment (inherited from parent §9.3)

- `not_used` — surface is deterministic or cryptographic
- `primary_judge` — surface is semantic and runs on live request path
- `fallback_judge` — external judge primary, Qwen is cost-tier fallback (unusual)
- `escalation_only` — Qwen primary; external model invoked only on abstain (Hybrid cases)
- `not_applicable` — offline harness / shadow / variance

## 10. Success Criteria

- All 226 modules have a row.
- No row leaves any of the 13 columns empty.
- Every `divergence_from_parent_group = yes` row has a corresponding entry in `## Cross-Row Consistency Notes`.
- The aggregate per-module decision distribution (e.g., "of 94 L3/reasoning modules: 61 None, 22 Judge, 8 Hybrid, 3 Ensemble Only") appears in `## Aggregate Deltas vs Parent Audit` and matches or refines the parent grouped row.
- Zero code changes, zero patches, zero refactors, zero new Python files, zero changes to existing runtime wiring.
- Deliverable lands at `docs/reports/agentic_core_eval_control_audit/<date>-per-module-followup.md`.

## 11. Execution Notes

- Use `list_dir` first per directory to get the module list without symbol-level noise.
- Use `read_file` with `limit=40` per module to confirm role from docstring + imports — do NOT read full files unless role is ambiguous after the first 40 lines.
- ADG MCP (`adg_nodes_by_file`, `adg_edge_fanin`) is the canonical fan-in authority when a module's role is unclear from source.
- `.codeiumignore` blocks `docs/reports/` for Cursor Agent's native `write_to_file`. Parent used the workaround: stage at repo-root, then `cmd /c move` to final path. Reuse.
- Per MCP serialization rule §25, any Notion writeback (Plans row for this plan; row update on completion) must be its own response.

## 12. Dependencies

- Parent plan `.cursor/plans/agentic-core-eval-control-audit-b7d4a2.md` — must remain authoritative. This plan refines, does not replace.
- Parent report `docs/reports/agentic_core_eval_control_audit/2026-05-02.md` — grouped rows 67, 110, 113, 120 are the inputs.
- ADG snapshot `artifacts/adg/adg_indexed_04292026_0654.sqlite` or later.

## 13. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Per-module reads exceed token budget | medium | Cap read_file at 40 lines per module; escalate only on ambiguous cases |
| Aggregate deltas contradict parent rollup | low | Cross-consistency check (W3.1) forces reconciliation before authoring |
| Sub-family discoveries require new archetypes beyond the four-decision enum | low | Enum is fixed by user constraint; document in gaps, do not extend |
| Plan execution spans multiple sessions | medium | All decisions recorded in the report as they are made; no cross-session state required |

## 14. Supersedes / Superseded-By

- Supersedes: none
- Superseded-by: none
- Extends: `agentic-core-eval-control-audit-b7d4a2`

---

**End of plan.** Ready for execution in a future session. No code changes will be made during execution.
