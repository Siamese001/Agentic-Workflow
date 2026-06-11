---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-u0-gap-closure-lf03-lf27-a4b9c1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-u0-gap-closure-lf03-lf27-a4b9c1.md'
source_sha256: 2e4ec4ded00abcb3f4746ccf4b4449ca3c0209983edb041ffc848d6e027ad166
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-u0-gap-closure-lf03-lf27-a4b9c1
plan_type: audit
dod_exempt: true
status: RETIRED
retired_reason: Both recommended patches rejected by operator — see Architectural Decisions section below.
---

# apps_rg U0 Gap Closure — LF-03 + LF-27 ARCHITECTURAL DECISION RECORD

**Status: RETIRED — No patches applied. Decisions documented below.**

This plan was created to close two MEDIUM-severity gaps (LF-03, LF-27) identified in the Oct–Dec 2025 legacy JSON audit. After review, the operator rejected both patches. This file documents the rationale and the confirmed current approach for each gap.

---

## Context (SCQA)

- **Situation** — `AppsRgIngressContractV1` is the U0 ingress boundary for apps_rg. The Oct–Dec 2025 audit identified 6 gaps; 2 were rated MEDIUM severity: LF-03 (JD source type) and LF-27 (per-section enforcement controls).
- **Complication** — Cascade recommended patching both. Operator reviewed both recommendations and rejected them based on current usage constraints and best-practice policy.
- **Question** — Should LF-03 and LF-27 be surfaced as new U0 fields?
- **Answer** — No. Both are intentionally NOT patched. Rationale documented below under Architectural Decisions.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `artifacts/apps_rg/history_audit/apps_rg_oct_dec_2025_resume_json_u0_coverage_receipt.json` | Audit evidence — LF-03 and LF-27 gap definitions | ✅ |
| `apps_rg/contracts/apps_rg_ingress_contract_v1.py` | Contract file to edit | ✅ |
| `apps_rg/contracts/apps_rg_ingress_contract.v1.schema.json` | Generated schema to regenerate | 🔲 |
| `apps_rg/contracts/apps_rg_ingress_field_map.v1.yaml` | Field map requiring 2 new rows | 🔲 |
| Tests under `tests/_apps_contract/` covering the ingress contract | Regression baseline | 🔲 |

---

## Wave Structure

**No waves executed.** Plan retired before execution — operator rejected both patches.

Notion status set to **Retired**.

---

## Architectural Decisions

### LF-27 — Per-section enforcement controls — REJECTED

**Operator decision:** Word count is not a best practice for section quality enforcement. The current pipeline uses **sentence count** as the enforcement metric. The legacy `VG_MANDATORY_WORD_COUNT_COMPLIANCE` gate and its K-node word targets are therefore not worth surfacing at U0 — they represent a deprecated enforcement strategy.

**Current approach confirmed:** Sentence count enforcement is the canonical method. The existing `QualityThresholdsSection` (`word_min`/`word_max`) fields are a historical artefact of the legacy workflow and will not be extended. No new enforcement profile ref will be added.

**Result:** LF-27 status in the audit receipt updated to `INTENTIONAL_DEVIATION` — gap acknowledged, word-count-based approach intentionally NOT adopted.

---

### LF-03 — JD source type (`jd_source_type`) — REJECTED

**Operator decision:** JD will always be provided as **pasted text** — URL fetching is not an input method for this pipeline. There is no need to distinguish source types at U0 because the input mode is fixed: paste-only.

**Current approach confirmed:** `JdPayloadSection.jd_text` receives the full pasted JD text directly. `jd_ref` field remains available for optional reference but is never used for fetch. No `jd_source_type` enum is needed because there is only ever one source type in practice.

**Result:** LF-03 status in the audit receipt updated to `INTENTIONAL_DEVIATION` — gap acknowledged, URL-fetch source type discrimination intentionally NOT adopted.

---

### Governing principle

The U0 contract should reflect the **actual operational reality** of the pipeline, not the full theoretical surface of the legacy workflow. Both rejected fields would have added complexity without benefit given the confirmed usage pattern (paste-only JD, sentence-count enforcement).

---

## Phase-Level Summary

**No phases executed.** Plan retired. The single action taken was updating the audit receipt and Notion documentation.

---

## Gap Register

**LF-03:** `INTENTIONAL_DEVIATION` — JD is always pasted text; URL source type discrimination not needed.

**LF-27:** `INTENTIONAL_DEVIATION` — Word count is not a best practice; sentence count is the current enforcement method. Legacy word-count gate not adopted.

---

## Execution Plan

**No code changes.** Plan retired. Notion row updated to Retired with decision rationale in Summary.

---

## Rules

- No code changes from this plan.
- LF-03 and LF-27 are `INTENTIONAL_DEVIATION` in the audit receipt — not gaps to be closed.

---

## Success Criteria

- [x] Architectural decisions documented in this plan and in Notion
- [x] Notion row updated to Retired
- [x] Audit receipt LF-03 + LF-27 rows updated to `INTENTIONAL_DEVIATION`

---

## Rollback Strategy

N/A — no code was changed.

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | Architectural decisions documented | This plan file + Notion row Summary | ✅ |
| DoD-2 | Notion row set to Retired | Notion page 35d27693-f55c-816f-a4b3-e1defb7fdfb7 | ✅ |
| DoD-3 | Audit receipt LF-03 + LF-27 updated to INTENTIONAL_DEVIATION | `artifacts/apps_rg/history_audit/apps_rg_oct_dec_2025_resume_json_u0_coverage_receipt.json` | ✅ |

---

## Cascade Alignment Checks

- Contract is frozen + extra=forbid — always use `Optional[...] = None` or `str = Field(default="")` shapes for new optional fields.
- Schema regeneration is deterministic (`--emit-schema` → stdout redirect) — not a hand-edit.
- Field map DEFERRED status is the correct mechanism for U0-declared but downstream-unwired fields; do not skip this step.
