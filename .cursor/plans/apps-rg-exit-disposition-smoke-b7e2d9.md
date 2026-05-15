---
plan_id: apps-rg-exit-disposition-smoke-b7e2d9
plan_type: governance
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg governed runtime smoke — `07_Exit_disposition.json`

**Parent closeout:** `.cursor/plans/p4.2_apps-rg-l6-shadow-learning-hardening-7e4c2f.md` (2026-05-15)  
**Purpose:** Close **W6.P2** gap: a **governed** (non-stub) apps_rg product path must emit **`07_Exit_disposition.json`** in the run directory so disposition proof is on-disk, not simulated by dry-run-only harnesses.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: TODO  
CURRENT_WAVE: W0  
LAST_COMPLETED_WAVE: NONE  
LAST_UPDATED: 2026-05-15  

---

## Context (SCQA)

- **Situation** — Contract tests and plan DoD reference Exit disposition artifacts; stub/dry-run paths may finish without writing `07_Exit_disposition.json`.
- **Complication** — Claiming W6.P2 complete without that file is false proof.
- **Question** — What is the smallest **governed** smoke that produces the file?
- **Answer** — Add or extend an integration smoke (likely under `tests/_apps_contract/` or governed CLI entry) that drives `dispatch_apps_rg_run` (or successor canonical entry) through Exit and asserts the JSON exists and schema-valid.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Trace where Exit writes `07_Exit_disposition.json` in real runs | 🔲 TODO | — | — |
| W2 | Implement smoke + assertions | 🔲 TODO | +N | apps_rg / tests |
| W3 | Document run dir contract in plan/receipt | 🔲 TODO | — | — |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Find producer of `07_Exit_disposition.json` in governed path | 🔲 TODO |
| W1.2 | List prerequisites (fixtures, mock provider, env) | 🔲 TODO |
| W2.1 | Implement smoke with deterministic inputs | 🔲 TODO |
| W2.2 | Assert file presence + minimal schema keys | 🔲 TODO |
| W3.1 | Link evidence path in parent master / portfolio notes | 🔲 TODO |

---

## Definition of Done

DoD-1: Single governed smoke creates `07_Exit_disposition.json` under a test-controlled run directory  
- Evidence: pytest node passes; path printed or fixture-scoped `$TMP`  
- Status: TODO  

DoD-2: Smoke does not invoke stub-only short-circuit that skips Exit emission  
- Evidence: code comment + test name encodes “governed path” discriminator  
- Status: TODO  

DoD-3: No semantic-cache direct-write regression  
- Evidence: existing `check_no_direct_semantic_cache_write` / related gates still pass  
- Status: TODO  

DoD-4: No `*_BYPASS` in smoke command transcript  
- Evidence: logged env snapshot in CI log  
- Status: TODO  

DoD-5: W6.P2 row in parent portfolio may flip from PARTIAL → PASS only after this smoke is merged and rerun on CI  
- Evidence: marker in parent plan / master plan receipt  
- Status: TODO  

---

## Out Of Scope

- Real LLM provider calls unless already standard for `_apps_contract` harness.
- Modifying constitutional Exit/UWG semantics in `agentic_core` without Author-Gate (prefer apps_rg overlay + existing contracts).
