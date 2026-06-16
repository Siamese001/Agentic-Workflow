---
plan_id: codex-mcp-lifecycle-guards-b8f2a1
plan_format: v2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# Codex MCP Lifecycle Guards

Implement guardrails for Codex-owned MCP process-cohort cleanup so strict readiness can fail safely without breaking host-attached transports.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: W1
LAST_UPDATED: 2026-06-16

---

## Context (SCQA)

- **Situation** - After a Codex restart, Memory, GitKraken, and raw ADG were callable, but strict readiness still failed because Codex spawned duplicate MCP process cohorts and Vector readiness timed out.
- **Complication** - Manual process cleanup can close host-attached stdio transports if the attached process is not known.
- **Question** - How do we prevent unsafe cleanup while still making duplicate cohorts visible and actionable?
- **Answer** - Extend the MCP cleanup helper with Codex-owned cohort detection, require explicit host-attached PID proof before Codex cleanup, document the operational rule, and test the guard.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2, W1.3 | Guard, docs, tests | ~6K | Codex cannot infer the host-attached stdio process from OS process rows alone. | DONE | Cleanup refuses unsafe Codex-owned duplicate cleanup and tests pass. |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Add Codex-owned cleanup guard | DONE |
| W1.2 | Document lifecycle runbook | DONE |
| W1.3 | Verify focused tests | DONE |

---

## Out Of Scope

- Changing Codex host internals or MCP spawning behavior.
- Killing Codex parent processes from repo scripts.
- Treating Vector lexical fallback as semantic parity.

---

## Wave 1 - Guard And Verify

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: A

**Authorization**: GRANTED - User requested implementation of the guards and tests.

**Phases**:
- **W1.1** - Add Codex-owned cleanup guard | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Document lifecycle runbook | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.3** - Verify focused tests | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `cleanup_duplicate_mcp_cohorts.py --json` reports Codex-owned duplicate cohorts instead of saying no cleanup target exists.
- `cleanup_duplicate_mcp_cohorts.py --apply` refuses Codex-owned cleanup unless attached PID proof is supplied.
- Focused unit tests and Codex primary verification pass.

---

PLAN_COMPLETE: plan=codex-mcp-lifecycle-guards-b8f2a1 note="Codex-owned MCP cleanup now requires attached PID proof; docs and focused tests updated."
