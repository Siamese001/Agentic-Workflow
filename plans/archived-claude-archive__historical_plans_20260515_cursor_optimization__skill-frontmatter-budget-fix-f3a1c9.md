---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\skill-frontmatter-budget-fix-f3a1c9.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\skill-frontmatter-budget-fix-f3a1c9.md'
source_sha256: e0395e7ea145a82ee33e80870e1647969375cacc898ca2cf41a577f08cca43ed
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: skill-frontmatter-budget-fix-f3a1c9
plan_type: infra
touches_agentic_core: false
touches_governance_ci: false
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Skill Frontmatter Budget Fix — mcp-integration SKILL.md

Unblock `run_contract_gates.py` end-to-end from the `skill_frontmatter` pre-flight failure caused by `.windsurf/skills/mcp-integration/SKILL.md` exceeding the Anthropic 500-line budget.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W1
CURRENT_WAVE_STATUS: DONE
LAST_COMPLETED_WAVE: W1
W1_STATUS: DONE (547→499 lines, skill_frontmatter gate green)
CHROMA_PLAN_REMAINS: DONE (apps-rg-chroma-ingestion-wiring-c7f2d9, Notion=Completed)
LAST_UPDATED: 2026-05-13

---

## Context (SCQA)

- **Situation** — `apps-rg-chroma-ingestion-wiring-c7f2d9` is fully complete (W1–W5 DONE, Notion=Completed). The CHECK-RG-CHROMA CI gate passes 9/9 via direct invocation (`python ops_scripts/ci/check_apps_rg_chroma_readiness.py`, exit 0).
- **Complication** — `run_contract_gates.py` executes `check_skill_frontmatter.py` as part of `validate_mcp_health()` **before** the `--gate` selector is evaluated. `.windsurf/skills/mcp-integration/SKILL.md` is 547 lines, exceeding the Anthropic 500-line budget enforced by `BODY_MAX_LINES = 500` in `check_skill_frontmatter.py`. The runner exits 1 unconditionally on any `--gate` invocation, blocking clean end-to-end CI proof for CHECK-RG-CHROMA.
- **Question** — What is the minimal safe fix that restores the skill_frontmatter gate to green without touching Chroma logic, agentic_core, or any plan state?
- **Answer** — Split the two appendix-style sections (§13 Task Manager MCP detail + Appendix: Constitutional §25 + Redirects table) out of `SKILL.md` into a sibling `SUPPORTING.md`. No routing logic, no description text, no frontmatter changes — structural split only.

---

## CI Blocker Report

| Item | Detail |
|------|--------|
| **Gate** | `check_skill_frontmatter.py` |
| **Invocation path** | `run_contract_gates.py` → `validate_mcp_health()` → line 104 |
| **Failing skill** | `.windsurf/skills/mcp-integration/SKILL.md` |
| **Observed lines** | 547 |
| **Budget** | 500 (`BODY_MAX_LINES` in `check_skill_frontmatter.py:40`) |
| **Over by** | 47 lines |
| **Effect** | Runner exits 1 before reaching assurance_gates — CHECK-RG-CHROMA never runs via runner |
| **CHECK-RG-CHROMA status** | ✅ 9/9 OK via direct invocation (unaffected) |
| **Chroma plan status** | ✅ DONE, Notion=Completed (unaffected) |
| **Fix scope** | `.windsurf/skills/mcp-integration/SKILL.md` + `.windsurf/skills/mcp-integration/SUPPORTING.md` only |

---

## Wave 1 — Split mcp-integration SKILL.md

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases**:
- **W1.1** — Move §13 Task Manager MCP section (~30 lines) to `SUPPORTING.md` | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Move Appendix §25 + Redirects table (~31 lines) to `SUPPORTING.md` | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.3** — Add `See SUPPORTING.md` cross-reference stubs in `SKILL.md` | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.4** — Verify `check_skill_frontmatter.py` exits 0 | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `SKILL.md` line count ≤ 500 (actual: 499)
- `check_skill_frontmatter.py` exits 0
- `run_contract_gates.py` passes the skill_frontmatter pre-flight check
- CHECK-RG-CHROMA via direct invocation remains 9/9 OK
- No changes to Chroma data, c0_binding.py, agentic_core, or W1–W5 plan state

---

## Files In Scope

- `.windsurf/skills/mcp-integration/SKILL.md` — reduced to 499 lines (from 547)
- `.windsurf/skills/mcp-integration/SUPPORTING.md` — new sibling for split content

> Governance CI pre-flight fixes (`infra_wiring_scan.py`, `executor_theater_gate.py`, `graph_layer_evidence_baseline.json`) are attributed to plan `runner-preflight-unblock-3b7d4a`.

## Files Out Of Scope (hard constraint)

- `apps_rg/runtime/bindings/c0_binding.py` — DO NOT TOUCH
- `data/cache/chromadb/` — DO NOT TOUCH
- `agentic_core/` — DO NOT TOUCH
- `artifacts/apps_rg/retrieval/` — DO NOT TOUCH
- `.windsurf/plans/apps-rg-chroma-ingestion-wiring-c7f2d9.md` — DO NOT REOPEN

---

## Definition of Done

| # | Criterion | Verified |
|---|-----------|---------|
| DoD-1 | `SKILL.md` line count ≤ 500 (actual: **499**) | ✅ |
| DoD-2 | `python ops_scripts/ci/check_skill_frontmatter.py` exits 0 | ✅ |
| DoD-3 | `run_contract_gates.py --gate CHECK-RG-CHROMA` exits 0 | ❌ pre-existing: stale ADG snapshot (mv_*=4, min=30); runner pre-flight fixes attributed to `runner-preflight-unblock-3b7d4a`; ADG regeneration is the remaining blocker |
| DoD-4 | CHECK-RG-CHROMA direct invocation still 9/9 OK | ✅ |
| DoD-5 | No Chroma/agentic_core/binding files modified | ✅ |

| Criterion | Disposition |
|-----------|-------------|
| Smoke-run DoD row | N/A — no executable surface changed |
| Chroma plan reopened | NEVER — DEFERRED_SCOPE not applicable |
