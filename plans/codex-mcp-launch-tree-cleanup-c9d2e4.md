---
plan_id: codex-mcp-launch-tree-cleanup-c9d2e4
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

# Codex MCP Launch Tree Cleanup

Align read-only MCP process audit and guarded cleanup so normal multi-process launch trees are not mistaken for duplicate Codex-owned MCP cohorts.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: W1
LAST_UPDATED: 2026-06-16

---

## Context (SCQA)

- **Situation** - Strict readiness passed the duplicate gate, but cleanup dry-run still blocked on `context7` and GitKraken.
- **Complication** - `context7` was a normal `npx` launch tree with several matching descendants, while GitKraken had multiple independent `gk.exe mcp` roots that audit did not classify.
- **Question** - How should cleanup distinguish a single launch tree from duplicate launch roots?
- **Answer** - Group cleanup candidates by topmost same-server root, and add GitKraken process markers to the read-only audit.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Launch-tree grouping and audit alignment | ~3K | Multiple matching descendants are normal inside one launch tree. | DONE | `context7` single launch tree is not blocked; GitKraken duplicates are reported by audit/readiness. |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Group cleanup candidates by launch-tree root | DONE |
| W1.2 | Add GitKraken process markers to audit | DONE |

---

## Out Of Scope

- Killing GitKraken processes without attached-PID proof.
- Changing Codex host process spawning.
- Treating process visibility as callable MCP proof.

---

## Wave 1 - Launch Tree Guard

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: COMPLETE

**Authorization**: GRANTED - User asked to run the next verification set and complete the remaining lifecycle guard steps.

**Phases**:
- **W1.1** - Group cleanup candidates by launch-tree root | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Add GitKraken process markers to audit | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Cleanup dry-run no longer blocks on a single `context7` launch tree.
- GitKraken duplicate roots are visible to `audit_codex_mcp_transports.py`.
- Focused cleanup/readiness tests pass.

---

PLAN_COMPLETE: 2026-06-16
