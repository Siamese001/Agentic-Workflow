# apps_rg Spine Hardening — Deferred Scope (T3)

**Slug:** `apps-rg-spine-hardening-deferred-d4e7a3`
**Status:** Not Started
**Tier:** T3
**Type:** Follow-up scope from `apps-rg-spine-hardening-7e3b9c` completion
**Owner:** Cursor Agent
**Authored:** 2026-05-09
**Parent plan:** `apps-rg-spine-hardening-7e3b9c` (Completed 2026-05-09)

> Captures all DEFERRED_SCOPE items emitted during the parent plan's six-wave execution. Do not implement until prioritized.

## 1. Goal

Close the residual scope identified during execution of `apps-rg-spine-hardening-7e3b9c`. The parent plan delivered W1-W6 (ADG findings, doc rewrite, PA receipts, airlocks, OTEL spans, anti-bypass scanner). This plan captures items that were either explicitly deferred in §13 of the parent plan or surfaced during the W1 ADG sweep as out-of-scope follow-ups.

## 2. Non-Goals

- Re-do anything closed by the parent plan.
- Modify the airlock pipeline behavior (W4 of parent).
- Change OTEL span names (W5 of parent — they are now contract).

## 3. Scope Inventory

### 3.1 Folder/Module Reorganization (parent §13)

| Item | Source | Risk | Estimated Effort |
|---|---|---|---|
| **D1** Move `agentic_core/L0_routing/reasoning/assembly_stage.py` into `agentic_core/prompt_governance/` PA namespace. Behavior preserved by parent plan's §4 wrapper; this is the physical relocation. | Parent §13 line 1; deferred from W3 of parent | High — affects every importer of `assembly_stage` | ~20k tokens |
| **D2** Rewrite `agentic_core/prompt_governance/` taxonomy to align with PA / Runtime-Gates / L5-evidence split. | Parent §13 line 3 | Medium — taxonomic only, behavior preserving | ~12k tokens |

### 3.2 Cross-App Spine Corrections (parent §13)

| Item | Source | Apps | Estimated Effort |
|---|---|---|---|
| **D3** Apply parent W1-W6 pattern to `apps_qna` | Parent §13 line 2 | apps_qna | ~30k tokens |
| **D4** Apply parent W1-W6 pattern to `apps_research` | Parent §13 line 2 | apps_research | ~30k tokens |
| **D5** Apply parent W1-W6 pattern to `apps_underwriting_ai` | Parent §13 line 2 | apps_underwriting_ai | ~30k tokens |
| **D6** Apply parent W1-W6 pattern to `apps_lic` | Parent §13 line 2 | apps_lic | ~30k tokens |
| **D7** Apply parent W1-W6 pattern to `apps_rfp` | Parent §13 line 2 | apps_rfp | ~30k tokens |
| **D8** Apply parent W1-W6 pattern to `apps_exec` | Parent §13 line 2 | apps_exec | ~30k tokens |

Each app is its own self-contained sub-plan with its own slug. This plan is the index, not the implementation.

### 3.3 W1 Findings Carry-Forward (W1 §6)

| Item | Source | Risk | Estimated Effort |
|---|---|---|---|
| **D9** Enumerate `apps_rg/integrations/` (40 items) for `VIOLATION_DIRECT_PROVIDER_CALL_BYPASS` (V1) — confirm each provider call site consumes `CompiledPromptArtifact`, not raw strings | W1 report §6 | Medium | ~10k tokens |
| **D10** Enumerate `apps_rg/engines/` (57 items) for `VIOLATION_PROVIDER_READY_PROMPT_OUTSIDE_PA` (V2) | W1 report §6 | Medium | ~12k tokens |
| **D11** Audit `apps_rg/scripts/narrative_pass.py` template surface for `VIOLATION_SCHEMA_ONLY_AS_PROSE` (V8) | W1 report §6 | Low | ~6k tokens |
| **D12** Confirm `apps_rg/cache/r1a_adapter.py` does not reconstruct prompts on cache hit (W1 left as DEFERRED) | W1 report Tier B | Low | ~4k tokens |

### 3.4 ADR Registry Update (parent §13)

| Item | Source | Risk | Estimated Effort |
|---|---|---|---|
| **D13** Author ADR-NNN ratifying the apps_rg PA ownership boundary correction | Parent §13 line 4 | Low (doc only) | ~4k tokens |

### 3.5 Anti-Bypass Scanner Coverage Expansion (parent §11 AG seed)

| Item | Source | Risk | Estimated Effort |
|---|---|---|---|
| **D14** Expand W6 scanner (`check_apps_rg_pa_boundary.py`) coverage to shared PA surface (`agentic_core/prompt_governance/`, `agentic_core/L0_routing/reasoning/assembly_stage.py`) | Parent §11 AG-W6-SCANNER-COVERAGE | Medium — false-positive risk | ~8k tokens |

### 3.6 CI Gate Promotion (parent §11 AG seed)

| Item | Source | Risk | Estimated Effort |
|---|---|---|---|
| **D15** After 30-day clean baseline, flip `PA-RG1` gate from advisory to fail-closed (set `APPS_RG_PA_BOUNDARY_FAIL_CLOSED=1` as default in CI) | Parent §11 (calibration cadence implicit) | High — first violation breaks CI | ~2k tokens (one-line change + ADR) |

### 3.7 Calibration Cadence (parent §11 AG seed)

| Item | Source | Risk | Estimated Effort |
|---|---|---|---|
| **D16** Establish weekly calibration report for airlock detection rates (`pa.airlock_security_pass` count, `pa.injection_neutralization` count, `pa.unsafe_payload_rejection` count) — pattern same as `tools/notion/snapshot_renderer.py` for backlog | Implicit from W5 OTEL spans | Low | ~6k tokens |

## 4. Wave Structure

> Each item D1-D16 is its own micro-wave; the items are NOT grouped because they have independent dependencies. This plan is the index. Each item promoted to its own plan when scheduled.

| Item Bucket | Count | Total Est. Tokens | Priority Hint |
|---|---|---|---|
| §3.1 Folder/Module reorg | 2 | ~32k | P3 (low — wrapper preserves behavior) |
| §3.2 Cross-app spine | 6 | ~180k | P2 (medium — each app earns own plan) |
| §3.3 W1 carry-forward | 4 | ~32k | P1 (high — closes V1/V2/V8) |
| §3.4 ADR | 1 | ~4k | P4 (low — historical record) |
| §3.5 Scanner expansion | 1 | ~8k | P2 (medium) |
| §3.6 Gate promotion | 1 | ~2k | P3 (gated on calibration) |
| §3.7 Calibration | 1 | ~6k | P3 |
| **TOTAL** | 16 | ~264k | mixed |

## 5. Implementation Approach

This plan is an **index**, not a single executable wave queue. Each item D1-D16 should be promoted to its own plan when scheduled, with its own slug, status, and Notion row. This plan exists so that:

1. Deferred items have a single registered home in Notion (no orphan defer markers).
2. Future Cursor Agent sessions can query this plan to see what's parked.
3. Prioritization happens against this consolidated view rather than scattered DEFERRED_SCOPE comments.

## 6. Acceptance Condition

This plan is considered "active" once registered in Notion. It is considered "complete" only when:
- Every item D1-D16 has been either:
  - Promoted to its own plan (status: Live or Completed), or
  - Explicitly retired with a written reason in this plan.

There is no single "done" state for this index — it transitions to `Retired` only when fully decomposed.

## 7. Plan Marker

```
PLAN_CREATED: slug=apps-rg-spine-hardening-deferred-d4e7a3 path=.cursor/plans/apps-rg-spine-hardening-deferred-d4e7a3.md tier=T3 status=Not Started waves=index-only
```

## 8. AI Summary

- Target: index of 16 deferred-scope items from completed parent plan apps-rg-spine-hardening-7e3b9c
- Buckets: folder/module reorg (D1-D2), cross-app spine corrections (D3-D8 for 6 apps), W1 carry-forward findings (D9-D12), ADR registry (D13), scanner expansion (D14), gate promotion (D15), calibration cadence (D16)
- New files: this plan only — implementation deferred. Each item earns its own future plan.
- Edit: none in this plan
- Pattern source: parent plan apps-rg-spine-hardening-7e3b9c §13 deferred-scope. Index-only, 16 items, ~264k tokens total estimated when fully decomposed
- Non-goals: no implementation. No re-doing parent W1-W6. No airlock or OTEL changes
- Success: every item D1-D16 either promoted to own plan or explicitly retired with reason
