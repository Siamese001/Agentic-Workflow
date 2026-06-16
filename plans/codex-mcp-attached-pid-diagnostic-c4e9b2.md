---
plan_id: codex-mcp-attached-pid-diagnostic-c4e9b2
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

# Codex MCP Attached PID Diagnostic

Expose attached process identity from repo-owned MCP servers so Codex-owned duplicate cohort cleanup can be driven by live tool proof instead of process-age guessing.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: W1
LAST_UPDATED: 2026-06-16

---

## Context (SCQA)

- **Situation** - Cleanup now refuses Codex-owned duplicate MCP cohorts unless attached PID proof is supplied.
- **Complication** - Codex did not have a cheap, uniform tool response that identifies the host-attached process PID for Memory, ADG, and Vector.
- **Question** - How do we make the guard actionable without unsafe process heuristics?
- **Answer** - Add a shared MCP process-identity helper, expose cheap identity tools from repo-owned MCP servers, and document the cleanup workflow.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2, W1.3 | Process identity, docs, tests | ~7K | Tool responses are the only trustworthy proof of the host-attached stdio process. | DONE | Memory/ADG/Vector can report attached PID cleanup arguments and tests pass. |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Add MCP process identity helper and tools | DONE |
| W1.2 | Document cleanup workflow with attached PID proof | DONE |
| W1.3 | Verify focused tests and receipts | DONE |

---

## Out Of Scope

- Changing Codex desktop host process management.
- Killing Codex-owned MCP children without attached PID proof.
- Treating Vector readiness timeout as semantic parity.

---

## Wave 1 - Attached PID Diagnostic

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: COMPLETE

**Authorization**: GRANTED - User requested completion of the host lifecycle / attached-PID next steps.

**Phases**:
- **W1.1** - Add MCP process identity helper and tools | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Document cleanup workflow with attached PID proof | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.3** - Verify focused tests and receipts | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Repo-owned MCP servers can return a process identity payload with `pid`, env key, and cleanup argument.
- Cleanup docs explain how to use live MCP tool output as attached PID proof.
- Focused unit tests and Codex primary verification pass.

---

PLAN_COMPLETE: 2026-06-16
