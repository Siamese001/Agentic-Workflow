---
plan_id: codex-primary-execution-7e4c2a
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

# Codex Primary Execution

Promote Codex from backup-only wording to the primary local execution surface while keeping repo-owned governance files as the rule source of truth.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W5
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-06-16

---

## Context (SCQA)

- **Situation** - Codex can run repo work and now has callable Memory, GitKraken, and Vector DB surfaces in-session, but repo docs still describe it as a backup adapter.
- **Complication** - Claude API rate limits make Claude-first execution brittle, while stale Codex MCP evidence can push agents into degraded fallbacks even when live tools are callable.
- **Question** - How do we make Codex the practical execution SSOT without creating a second governance registry?
- **Answer** - Add a Codex-primary contract, executable readiness checks, run receipt validation, a refreshed live MCP snapshot, and advisory-only local Codex skill checks while preserving repo-owned files as versioned governance inputs during migration.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Contract and plan | ~4K | Existing `.claude` rules remain repo-owned governance inputs. | DONE | Primary contract and AGENTS/doc pointers exist. |
| W2 | W2.1, W2.2 | Readiness and receipts | ~8K | Shell-side scripts cannot directly introspect Codex MCP tools, so callable proof can be supplied by env/status evidence. | DONE | Readiness and receipt validators pass focused unit tests. |
| W3 | W3.1, W3.2 | Evidence refresh and verification | ~5K | MCP reports are evidence snapshots, not routing registries. | DONE | Live snapshot documents callable/degraded routes and governance checks pass. |
| W4 | W4.1, W4.2 | Local skill dependency cleanup | ~4K | Personal Codex skills are workstation bootstrap shims, not repo governance SSOT. | DONE | Compatibility verifier no longer hard-fails on missing personal skills by default. |
| W5 | W5.1, W5.2 | Follow-up docs and verification | ~4K | Primary verifier remains repo-only. | DONE | Docs, tests, receipt, and plan reflect advisory skill behavior. |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Add Codex primary contract | DONE |
| W1.2 | Update adapter docs and AGENTS pointers | DONE |
| W2.1 | Add Codex readiness gate | DONE |
| W2.2 | Add run receipt validator | DONE |
| W3.1 | Refresh live MCP snapshot | DONE |
| W3.2 | Run targeted verification | DONE |
| W4.1 | Make personal skills advisory by default | DONE |
| W4.2 | Preserve strict bootstrap audit flag | DONE |
| W5.1 | Document bootstrap-only skill role | DONE |
| W5.2 | Verify follow-up wave | DONE |

---

## Out Of Scope

- Rewriting `.claude` rule bodies into Codex-specific skills.
- Changing credentials, MCP secrets, or provider API keys.
- Removing Claude compatibility files in this pass.
- Solving raw DeepWiki or ADG MCP host exposure if the Codex host does not expose those tools.

---

## Wave 1 - Contract

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: A

**Authorization**: GRANTED - User requested implementation of the Codex-primary recommendations.

**Phases**:
- **W1.1** - Add Codex primary contract | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Update adapter docs and AGENTS pointers | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `docs/codex-primary-execution.md` exists and defines Codex as the primary local execution surface.
- AGENTS and adapter docs point to the new contract without duplicating `.claude` rule bodies.

---

## Wave 2 - Executable Gates

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: B

**Phases**:
- **W2.1** - Add Codex readiness gate | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** - Add run receipt validator | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `scripts/governance/codex_readiness.py` can emit JSON/text readiness output.
- `scripts/governance/verify_codex_run_receipt.py` validates required run receipt fields and failure RCA.
- Unit tests cover pass/fail cases.

---

## Wave 3 - Evidence And Verification

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: C

**Phases**:
- **W3.1** - Refresh live MCP snapshot | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** - Run targeted verification | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `docs/reports/codex/codex_primary_mcp_live_snapshot.*` separates callable, degraded, and blocked routes.
- `scripts/governance/verify_codex_primary.py` passes.
- Existing backup verifier still passes for compatibility.

---

## Wave 4 - Local Skill Dependency Cleanup

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: D

**Phases**:
- **W4.1** - Make personal skills advisory by default | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.2** - Preserve strict bootstrap audit flag | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `scripts/governance/verify_codex_backup.py` passes by default when repo anchors are valid even if personal Codex skills are absent.
- `--require-personal-skills` preserves hard-fail behavior for workstation bootstrap audits.
- `--repo-only` still suppresses personal-skill checks entirely for CI.

---

## Wave 5 - Follow-Up Docs And Verification

WAVE_ID: W5
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: E

**Phases**:
- **W5.1** - Document bootstrap-only skill role | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W5.2** - Verify follow-up wave | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `AGENTS.md`, `docs/codex-primary-execution.md`, and `docs/codex-backup-adapter.md` state that personal Codex skills are optional bootstrap shims.
- Unit tests cover default advisory, repo-only, and strict personal-skill behavior.
- Primary and compatibility verifiers pass.

---

## Execution Details

### W1.1 - Add Codex Primary Contract
**Scope**: Create a repo-owned contract that makes Codex primary for local execution state, readiness, receipts, and verification.

**Commands**:
```bash
python scripts/governance/verify_codex_primary.py
```

### W2.1 - Add Codex Readiness Gate
**Scope**: Implement a read-only preflight that composes git cleanliness, transport audit output, MCP route evidence, path-budget script presence, and process hygiene.

**Commands**:
```bash
python scripts/governance/codex_readiness.py --json
```

### W2.2 - Add Run Receipt Validator
**Scope**: Define a JSON run receipt contract and validate status, files changed, checks, commands, fallbacks, and RCA on failures.

**Commands**:
```bash
python scripts/governance/verify_codex_run_receipt.py <receipt.json>
```

### W4.1 - Make Personal Skills Advisory
**Scope**: Change the legacy compatibility verifier so personal Codex skill drift is advisory by default.

**Commands**:
```bash
python scripts/governance/verify_codex_backup.py
```

### W4.2 - Preserve Strict Bootstrap Audit
**Scope**: Keep strict failure behavior available when explicitly auditing the workstation bootstrap layer.

**Commands**:
```bash
python scripts/governance/verify_codex_backup.py --require-personal-skills
```

---

## Gap Register

**GAP-1: Codex host MCP discovery is not available to shell scripts**
- Details: Python scripts cannot see the agent's live tool namespace.
- Impact: Callable MCP proof must be passed through environment/status evidence or recorded snapshots.

**GAP-2: Raw ADG and DeepWiki MCPs are not callable in the current Codex session**
- Details: Live discovery did not expose those tool namespaces.
- Impact: ADG must use a named degraded SQLite fallback until host exposure is repaired.

---

## Definition of Done

DoD-1: Codex primary contract exists
- Evidence: `python scripts/governance/verify_codex_primary.py` exits 0
- Status: DONE

DoD-2: Readiness gate exists and emits machine-readable output
- Evidence: `python scripts/governance/codex_readiness.py --json` exits 0
- Status: DONE

DoD-3: Run receipt validator enforces failure RCA
- Evidence: `python -m pytest tests/unit/scripts/governance/test_verify_codex_run_receipt.py -q` passes
- Status: DONE

DoD-4: Existing compatibility verifier still passes
- Evidence: `python scripts/governance/verify_codex_backup.py` exits 0
- Status: DONE

DoD-5: Targeted unit tests pass
- Evidence: `python -m pytest tests/unit/scripts/governance/test_codex_readiness.py tests/unit/scripts/governance/test_verify_codex_primary.py tests/unit/scripts/governance/test_verify_codex_run_receipt.py -q` passes
- Status: DONE

DoD-6: Personal Codex skills are advisory by default
- Evidence: `python -m pytest tests/unit/scripts/governance/test_verify_codex_backup.py -q` passes
- Status: DONE

DoD-7: Follow-up docs and receipt validate
- Evidence: `python scripts/governance/verify_codex_run_receipt.py docs/reports/codex/codex_primary_execution_7e4c2a_receipt.json` exits 0
- Status: DONE

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```text
DISCOVERED_SCOPE: plan=codex-primary-execution-7e4c2a wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=codex-primary-execution-7e4c2a decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=codex-primary-execution-7e4c2a reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |

---

## Supersedes

_None - net-new plan._

---

## Marker Quick Reference

```text
WAVE_START: plan=codex-primary-execution-7e4c2a wave=<N>
WAVE_COMPLETE: plan=codex-primary-execution-7e4c2a wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=codex-primary-execution-7e4c2a phase=<W1.1>
PLAN_COMPLETE: plan=codex-primary-execution-7e4c2a note="<final outcome>"
```

PLAN_COMPLETE: plan=codex-primary-execution-7e4c2a note="Codex primary execution contract, readiness gate, run receipt validator, live snapshot, advisory local-skill checks, docs, and tests implemented."
