---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\cursor-only-governance-ssot-d9e4b1.md'
original_relative_path: '_archive\\2026-05\\cursor-only-governance-ssot-d9e4b1.md'
source_sha256: fea343e9dacf476e8cb3838c8683a57c914cce1f7988292f657691ba4186cdb1
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: cursor-only-governance-ssot-d9e4b1
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: true
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Cursor-only governance and Windsurf SSOT retirement

Consolidate operator truth to **`.cursor/`** and repo automation: fix stale AGENTS / helper defaults, add explicit MCP serialization policy for Cursor agents, rename misleading workflow files, and schedule CI parity cleanup without duplicating `.windsurf/` as a second runtime.

> **plan_id discipline**: `plan_id` matches filename stem `cursor-only-governance-ssot-d9e4b1`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-15

---

## Context (SCQA)

- **Situation** — Canonical plans, rules, and hooks live under `.cursor/`. `.windsurf/` still mirrors scripts, hooks, and MCP config; some gates and helpers still default to Windsurf paths. The operator no longer runs Windsurf locally.
- **Complication** — Dual trees and wrong defaults cause drift (e.g. Notion plan path, AGENTS Notion map rows), confused onboarding, and CI that validates files the operator does not use.
- **Question** — How do we make **Cursor + `.cursor/`** the sole operational SSOT while keeping optional `.windsurf/` only for CI mirror parity until explicitly retired?
- **Answer** — **Wave 1**: correct SSOT prose and defaults + one new Cursor rule. **Wave 2**: narrow or re-scope CI that hard-requires `.windsurf/hooks.json`. **Wave 3**: single-source shared Python (`pre_mcp_gate`, unified notion auditor). **Wave 4 (optional)**: selective `afterAgentResponse` dispatcher wiring behind timeouts — only if same-turn capture is required.

---

## Wave summary (planning)

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.3 | AGENTS + helper defaults + `mcp-serialization` rule + workflow rename | ~12k | NOTION_TOKEN available for registration | ✅ DONE | Plan on disk; Notion row; wave start OK; docs consistent |
| W2 | W2.1–W2.2 | CI scan paths (`PLAN-DOD`, windsurf-only gates) scoped safely | ~18k | PLAN-DOD fail-closed stays off until path fix is safe | ✅ DONE | `_PLANS_DIR` → `.cursor/plans` (top-level `*.md` only); windsurf schema gate tolerates enriched hook entries + `WINDSURF_CONFIG_SCHEMA_BYPASS` |
| W3 | W3.1 | Dedupe `pre_mcp_gate` / `unified_notion_status_auditor` sources | ~14k | No behavior change intended — byte-parity or tests | ✅ DONE | `.windsurf/scripts/pre_mcp_gate.py` shim → `.cursor/scripts/pre_mcp_gate.py`; notion auditor already SSOT under `tools/notion/` |
| W4 | W4.1 | Optional Cursor `afterAgentResponse` dispatcher | ~20k | Product approval for latency | ✅ DONE | **No-go** for default `hooks.json` merge — keep targeted `after_agent_*.py` hooks; dispatcher stays opt-in (`POST_CURSOR_AGENT_DISPATCHER=1`) per `post_cursor_agent_dispatch.py` docstring (§30 shadow-mode precedent) |

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | SSOT docs + rule + renames | ✅ DONE | — | 7 |
| W2 | CI path rationalization | ✅ DONE | — | `check_plan_definition_of_done.py`, `check_windsurf_config_schema.py`, CI remedy strings |
| W3 | Script dedup | ✅ DONE | `test_hooks_deep_edge_cases.py` | `.windsurf/scripts/pre_mcp_gate.py` shim |
| W4 | Hook dispatcher (optional) | ✅ DONE | — | Plan Gap + AGENTS wave CLI path correction |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | AGENTS Notion map + notion skill line | ✅ DONE |
| W1.2 | `plan_creation_helper` default path + docstring | ✅ DONE |
| W1.3 | `mcp-serialization.mdc` + workflow rename | ✅ DONE |
| W2.1 | PLAN-DOD / windsurf scan audit | ✅ DONE |
| W2.2 | `check_windsurf_config_schema` policy | ✅ DONE |
| W3.1 | Python SSOT dedup | ✅ DONE |
| W4.1 | Dispatcher decision | ✅ DONE |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Notion map correctness | `AGENTS.md` | Wrong plan root; wrong rules/MCP SSOT rows; Anti-Pattern DB vs archived rule | ~3k | ✅ DONE |
| W1.2 | Plan helper default | `tools/notion/plan_creation_helper.py` | Default `.windsurf/plans` contradicts plan-location | ~2k | ✅ DONE |
| W1.3 | Agent-visible serialization + workflow name | `.cursor/rules/mcp-serialization.mdc`, `.cursor/workflows/refresh-cursor-docs.md` | Filename says Windsurf; policy only in Windsurf tree | ~4k | ✅ DONE |
| W2.1 | PLAN-DOD scanner | `ops_scripts/ci/check_plan_definition_of_done.py` | `_PLANS_DIR` → `.cursor/plans`; non-recursive top-level scan (excludes `_archive/` tree) | ~6k | ✅ DONE |
| W2.2 | Windsurf schema gate | `ops_scripts/ci/check_windsurf_config_schema.py` | Enriched hook entry allowlist; optional `WINDSURF_CONFIG_SCHEMA_BYPASS` for Cursor-only clones | ~5k | ✅ DONE |
| W3.1 | Script parity | `.cursor/scripts`, `.windsurf/scripts` | `pre_mcp_gate` Windsurf shim; tests patch `pre_mcp_gate.repo_root` | ~8k | ✅ DONE |
| W4.1 | Post-response wiring | `.cursor/hooks.json`, `.cursor/scripts/post_cursor_agent_dispatch.py` | **Decision:** do not add dispatcher to default hook chain; remain opt-in behind env + operator hook edits | ~10k | ✅ DONE |

---

## Out Of Scope

- Deleting the entire `.windsurf/` tree in Wave 1 (requires CI + parity decision in W2/W3).
- Changing `agentic_core` or app runtime behavior.
- Fail-closing NP Notion gates or new Notion databases.

---

## Wave 1 — SSOT and operator clarity

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — documentation and Cursor-local governance only.

**Phases**:
- **W1.1** — AGENTS Notion map + MCP row | ~3k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — `plan_creation_helper` default plan path | ~2k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.3** — `mcp-serialization.mdc` + rename `refresh-windsurf-docs.md` → `refresh-cursor-docs.md` | ~4k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- AGENTS Plans write trigger references `.cursor/plans/`; filesystem SSOT rows for rules/MCP point at `.cursor/`; Anti-Pattern Burndown aligned with `notion-archived-databases.mdc`.
- `create_plan_in_notion()` default `plan_file_path` uses `.cursor/plans/{slug}.md`.
- New rule documents remote MCP serialization; workflow filename matches `/refresh-cursor-docs`.

---

## Wave 2 — CI and scan paths

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — PLAN-DOD `_PLANS_DIR` → `.cursor/plans` (top-level `*.md` only; `_archive/` not scanned) | ~6k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** — `check_windsurf_config_schema`: extended hook field allowlist; `WINDSURF_CONFIG_SCHEMA_BYPASS` documented for Cursor-only operators | ~5k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- PLAN-DOD exits 0 with advisory WARN until plans gain `## Definition of Done` (no mass fail-closed flip).
- Windsurf schema gate exits 0 on real `.windsurf/hooks.json` enriched entries.

**Gap Register closure**: GAP-1 resolved (scanner root + scope). Wave lifecycle CLI path corrected in AGENTS, `tools/windsurf/wave_execution_state.py` docstring, NP13 remedy text, and NP-GUARD module docstring (`tools/windsurf/…` is canonical for `start` / `complete` / `wave-progress`; `tools/plan_lifecycle/wave_execution_state.py` remains parse/update-only).

---

## Wave 3 — Single-source scripts

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — `.windsurf/scripts/pre_mcp_gate.py` shim delegates to `.cursor/scripts/pre_mcp_gate.py` | ~8k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `tests/unit/ops_scripts/hooks/windsurf/test_hooks_deep_edge_cases.py` patches `pre_mcp_gate.repo_root` (module-global used by `main()`).

---

## Wave 4 — Optional post-agent dispatcher

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — Decision recorded | ~10k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Decision (W4.1)** — **No default merge** of `post_cursor_agent_dispatch.py` into `.cursor/hooks.json`:
- Current production chain is already **two** targeted hooks (`after_agent_adg_audit.py`, `after_agent_notion_status_audit.py`), not the legacy 16-script subprocess cascade the dispatcher was sized for.
- Turning on the dispatcher without the §30-prescribed shadow period would risk silent capture gaps relative to today’s proven hooks.
- Operators who want the fan-in dispatcher follow `POST_CURSOR_AGENT_DISPATCHER=1` and replace hook entries per `.cursor/scripts/post_cursor_agent_dispatch.py` module docstring.

**Acceptance**:
- Explicit go/no-go documented here; no `hooks.json` change in this wave.

---

## Execution Details

### W1.1 — AGENTS
**Scope**: Correct Notion workspace map and MCP quick reference for Cursor-only SSOT and archived Anti-Pattern Burndown.

**Commands**:
```bash
python -m json.tool AGENTS.md 2>nul || true
```

### W1.2 — Plan creation helper
**Scope**: Default `plan_file_path` to `.cursor/plans/{slug}.md`; update module docstring examples.

**Commands**:
```bash
python tools/notion/plan_creation_helper.py --help
```

### W1.3 — Rule + workflow
**Scope**: Add `.cursor/rules/mcp-serialization.mdc`; rename workflow file.

**Commands**:
```bash
dir .cursor\workflows\refresh-cursor-docs.md
```

---

## Gap Register

**GAP-1: PLAN-DOD `_PLANS_DIR` mismatch** — **RESOLVED (W2)**  
`check_plan_definition_of_done.py` now scans `.cursor/plans` for top-level `*.md` only (does not recurse into `_archive/`).

**GAP-2: Wave lifecycle CLI path drift** — **RESOLVED (W2)**  
Canonical CLI for `start` / `complete` / `wave-progress` / `status` is `tools/windsurf/wave_execution_state.py`. AGENTS.md auto-routing table, this file’s Usage block, `check_plan_complete_marker_freshness.py` remedy text, and `check_notion_plan_lifecycle_guard.py` docstring updated. `tools/plan_lifecycle/wave_execution_state.py` remains a separate parse/update utility (no `start` subcommand).

**GAP-3: Post-agent dispatcher default wiring** — **CLOSED — NO-GO (W4)**  
Default `.cursor/hooks.json` keeps targeted `after_agent_*.py` entries; full dispatcher stays opt-in per `post_cursor_agent_dispatch.py` (env `POST_CURSOR_AGENT_DISPATCHER=1`) and §30 shadow-mode precedent.

**FOLLOW-UP (child plan, separate scope):** `hooks-deep-edge-tests-remediation-e7c2a9` — restores `tests/unit/ops_scripts/hooks/windsurf/test_hooks_deep_edge_cases.py` to full green (~33 failures as of 2026-05-15); **not** mixed with this plan’s governance SSOT closeout.

---

## Definition of Done

DoD-1: Plan file exists at `.cursor/plans/cursor-only-governance-ssot-d9e4b1.md` with required tables and DoD.
- Evidence: `dir` / file read
- Status: DONE

DoD-2: Notion Plans row created with Status **Not Started** and correct `Plan File Path`.
- Evidence: `python tools/notion/plan_creation_helper.py` → `page_id=36127693-f55c-8154-b4c8-eccbd9688d08`
- Status: DONE

DoD-3: Wave execution marked started for W1 (Notion registration prerequisite met).
- Evidence: `python ops_scripts/ci/check_plan_registration_freshness.py --refresh` then `python tools/windsurf/wave_execution_state.py start --plan cursor-only-governance-ssot-d9e4b1` exit 0
- Status: DONE

DoD-4: Smoke — plan helper CLI still runs.
- Evidence: `python tools/notion/plan_creation_helper.py --help` exits 0
- Status: DONE

DoD-5: Governance artifacts present (`mcp-serialization.mdc`, renamed workflow).
- Evidence: paths exist under `.cursor/`
- Status: DONE

### Verification vs deferral

| DoD | Verified in-wave | Deferred |
|-----|-------------------|----------|
| DoD-1 | Yes (file on disk) | — |
| DoD-2 | Yes | — |
| DoD-3 | Yes (cache refresh required before `start`) | — |
| DoD-4 | Yes | — |
| DoD-5 | Yes | — |

---

## Runtime receipt

Machine-readable closeout (one object per plan, all waves listed): `artifacts/plan_lifecycle/cursor-only-governance-ssot-d9e4b1_wave_completion_receipt.json`

Emit in chat / hook capture (same strings as receipt `waves[].note`):

---

## Marker Quick Reference

```
WAVE_START: plan=cursor-only-governance-ssot-d9e4b1 wave=1
WAVE_COMPLETE: plan=cursor-only-governance-ssot-d9e4b1 wave=1 note="SSOT docs + mcp-serialization + plan helper default + workflow rename"
WAVE_COMPLETE: plan=cursor-only-governance-ssot-d9e4b1 wave=2 note="PLAN-DOD .cursor/plans scan; windsurf schema gate policy + bypass; wave CLI doc alignment"
WAVE_COMPLETE: plan=cursor-only-governance-ssot-d9e4b1 wave=3 note="pre_mcp_gate Windsurf shim; tests patch pre_mcp_gate.repo_root"
WAVE_COMPLETE: plan=cursor-only-governance-ssot-d9e4b1 wave=4 note="Dispatcher no-go default hooks; Gap register + opt-in POST_CURSOR_AGENT_DISPATCHER"
PLAN_COMPLETE: plan=cursor-only-governance-ssot-d9e4b1 note="W1-W4 delivered; receipt artifacts/plan_lifecycle/cursor-only-governance-ssot-d9e4b1_wave_completion_receipt.json"
```

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order per `.cursor/templates/execution-plan-template.md`.

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |
