---
plan_id: codex-mcp-transport-diagnosis-latest-main-73b728
plan_format: v2
plan_type: governance
touches_governance_ci: true
touches_agentic_core: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
related_plans:
  - codex-mcp-transport-parity-4b9c7e
---

# Codex MCP Transport Diagnosis on Latest Main

Add a narrow read-only diagnostic wrapper that turns current Codex MCP transport evidence into deterministic diagnosis and recovery guidance.

> **plan_id discipline**: `plan_id` matches the filename stem `codex-mcp-transport-diagnosis-latest-main-73b728`.

This plan does **not** replace or complete `codex-mcp-transport-parity-4b9c7e`. The parity plan remains the broader in-progress MCP parity authority. This successor plan closes only the operational diagnosis and recovery recommendation gap left by current `main` when Codex reports `Transport closed`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W3
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-07-04

---

## Context (SCQA)

- **Situation** - Latest `main` already contains the transport audit helper, route classifications, readiness closed-transport RCA, session epoch callability proof ledger, ADG out-of-band `transport_status()`, cleanup guard docs, and the in-progress parity plan.
- **Complication** - Operators still need a single read-only command that answers "what now?" when Codex says `Transport closed`, without reimplementing the audit, guessing from process presence, treating SQLite as green MCP proof, or blindly restarting/killing Codex-owned processes.
- **Question** - How do we diagnose a closed Codex MCP transport deterministically and recommend the safe recovery path?
- **Answer** - Compose current main's audit, readiness RCA, ADG supervisor status, callability epoch proof, and duplicate-cohort cleanup guard into one focused diagnosis command, test the decision matrix, and record a fresh report.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2, W1.3 | Plan and diagnostic wrapper | ~5K | Latest `origin/main` remains authoritative and existing audit/readiness helpers are reused | DONE | Plan is minted and wrapper emits the requested schema without launching/killing/calling MCP tools |
| W2 | W2.1, W2.2 | Focused tests and docs/report | ~5K | Current ADG route may remain closed; evidence must be diagnosis-only | DONE | Tests cover the requested classifications and a fresh diagnosis report records current state |
| W3 | W3.1 | Validation closeout | ~3K | Readiness may fail due active-session MCP callability and must be reported honestly | DONE | Requested validation commands run and failures are classified as transport diagnosis, not green readiness |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Confirm latest main and non-duplication scope | DONE |
| W1.2 | Mint successor plan | DONE |
| W1.3 | Implement read-only diagnosis wrapper | DONE |
| W2.1 | Add focused diagnosis tests | DONE |
| W2.2 | Generate current evidence report and minimal docs update | DONE |
| W3.1 | Run requested validation and record stop-condition evidence | DONE |

---

## Out Of Scope

- Replacing `scripts/governance/audit_codex_mcp_transports.py`.
- Replacing `scripts/governance/codex_readiness.py` readiness gates.
- Creating a second MCP registry or changing root `.mcp.json`.
- Calling Codex MCP tools, launching MCP servers, killing MCP processes, or auto-cleaning duplicate cohorts.
- Treating direct SQLite access as green ADG MCP transport readiness.
- Implementing HTTP MCP transport or editing upstream Codex.
- Broadening into memory/vector behavior beyond generic diagnosis classification.

---

## Wave 1 - Plan And Diagnostic Wrapper

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: A

**Authorization**: USER_APPROVED - User approved the plan on 2026-07-04.

**Phases**:
- **W1.1** - Confirm latest main and non-duplication scope | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Mint successor plan | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.3** - Implement read-only diagnosis wrapper | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Plan metadata includes `plan_format: v2`, `plan_type: governance`, `touches_governance_ci: true`, `touches_agentic_core: false`, `supersedes: []`, and related plan `codex-mcp-transport-parity-4b9c7e`.
- Wrapper supports `--server <server_id>`, `--json`, and optional `--route-contract <path>`.
- Wrapper output schema is `codex-mcp-transport-diagnosis/v1`.
- Wrapper is read-only and does not launch/kill servers, call Codex MCP tools, or query SQLite as green ADG proof.

---

## Wave 2 - Tests, Docs, And Evidence

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: B

**Phases**:
- **W2.1** - Add focused diagnosis tests | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** - Generate current evidence report and minimal docs update | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Tests cover closed transport, process-only, duplicate process without attached PID, callable route, degraded fallback, and missing route contract.
- Report records what latest main already had, what this branch adds, current `adg_sqlite` diagnosis output, stale lifecycle audit evidence, and remaining manual recovery.
- `docs/codex-primary-execution.md` is updated only if needed under the MCP Lifecycle Cleanup Guard.

---

## Wave 3 - Validation Closeout

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: C

**Phases**:
- **W3.1** - Run requested validation and record stop-condition evidence | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `python -m py_compile scripts/governance/diagnose_codex_mcp_transport.py` passes.
- Focused diagnosis pytest passes.
- Existing audit/readiness pytest slice runs.
- Audit and diagnosis commands run.
- `codex_readiness.py --json --skip-searxng` is recorded honestly, including active-session MCP callability failure if still present.

---

## Execution Details

### W1.1 - Confirm Latest Main And Scope
**Scope**: Fetch `origin/main`, verify no existing diagnosis wrapper/tests/report on latest main, and inspect the existing audit/readiness/epoch/supervisor helpers.

**Commands**:
```bash
git fetch origin main --prune
git rev-parse main
git rev-parse origin/main
git ls-tree -r --name-only origin/main scripts/governance tests/unit/scripts/governance docs/reports/codex plans
```

### W1.3 - Implement Diagnostic Wrapper
**Scope**: Add `scripts/governance/diagnose_codex_mcp_transport.py` as a read-only adapter over existing evidence.

**Commands**:
```bash
python scripts/governance/diagnose_codex_mcp_transport.py --server adg_sqlite --json
```

### W2.1 - Add Tests
**Scope**: Add `tests/unit/scripts/governance/test_diagnose_codex_mcp_transport.py` with focused branch-free fixtures.

**Commands**:
```bash
python -m pytest -q tests/unit/scripts/governance/test_diagnose_codex_mcp_transport.py
```

### W2.2 - Generate Evidence Report
**Scope**: Write current diagnosis evidence under `docs/reports/codex/`, and minimally document the new command if needed.

**Commands**:
```bash
python scripts/governance/audit_codex_mcp_transports.py --json
python scripts/governance/diagnose_codex_mcp_transport.py --server adg_sqlite --json
```

### W3.1 - Validation
**Scope**: Run the requested validation commands.

**Commands**:
```bash
python -m py_compile scripts/governance/diagnose_codex_mcp_transport.py
python -m pytest -q tests/unit/scripts/governance/test_diagnose_codex_mcp_transport.py
python -m pytest -q tests/unit/scripts/governance/test_audit_codex_mcp_transports.py tests/unit/scripts/governance/test_codex_readiness.py
python scripts/governance/audit_codex_mcp_transports.py --json
python scripts/governance/diagnose_codex_mcp_transport.py --server adg_sqlite --json
python scripts/governance/codex_readiness.py --json --skip-searxng
```

---

## Gap Register

**GAP-1: Closed transport recovery guidance is scattered**
- Audit and readiness already know the facts, but operators need one deterministic diagnosis record.
- Impact: closed stdio transport can trigger guessing, blind restarts, or unsafe process cleanup.

**GAP-2: Process evidence can look healthier than callability**
- Current local processes and heartbeat files can exist while Codex cannot call the MCP route.
- Impact: process-only state must remain blocked until active Codex callability proof exists.

**GAP-3: Duplicate Codex-owned cohorts require attached PID proof**
- Cleanup is unsafe without knowing which PID owns the active host-attached stdio transport.
- Impact: diagnostic output must recommend process-identity proof, not automatic termination.

---

## Definition of Done

DoD-1: Successor plan exists and does not supersede the parity plan.
- Evidence: `plans/codex-mcp-transport-diagnosis-latest-main-73b728.md`.
- Status: DONE

DoD-2: Diagnostic wrapper emits the requested schema.
- Evidence: `python scripts/governance/diagnose_codex_mcp_transport.py --server adg_sqlite --json`.
- Status: DONE

DoD-3: Focused tests pass.
- Evidence: `python -m pytest -q tests/unit/scripts/governance/test_diagnose_codex_mcp_transport.py`.
- Status: DONE

DoD-4: Existing transport audit/readiness tests remain covered.
- Evidence: `python -m pytest -q tests/unit/scripts/governance/test_audit_codex_mcp_transports.py tests/unit/scripts/governance/test_codex_readiness.py`.
- Status: DONE

DoD-5: Fresh evidence report records latest-main state and stale lifecycle audit note.
- Evidence: `docs/reports/codex/codex_mcp_transport_diagnosis_latest_main_73b728.md`.
- Status: DONE

DoD-6: Readiness stop condition is respected.
- Evidence: `python scripts/governance/codex_readiness.py --json --skip-searxng` result is recorded without claiming ADG green readiness if active-session MCP callability fails.
- Status: DONE

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=codex-mcp-transport-diagnosis-latest-main-73b728 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=codex-mcp-transport-diagnosis-latest-main-73b728 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=codex-mcp-transport-diagnosis-latest-main-73b728 reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |

---

## Supersedes

| Predecessor slug | Reason |
|---|---|
| _None_ | This is a successor diagnosis slice, not a replacement plan. |

_None - net-new successor plan. Related plan `codex-mcp-transport-parity-4b9c7e` remains in progress._

---

## Marker Quick Reference

Wave lifecycle markers:
```
WAVE_START: plan=codex-mcp-transport-diagnosis-latest-main-73b728 wave=<N>
WAVE_COMPLETE: plan=codex-mcp-transport-diagnosis-latest-main-73b728 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=codex-mcp-transport-diagnosis-latest-main-73b728 phase=<W1.1>
PLAN_COMPLETE: plan=codex-mcp-transport-diagnosis-latest-main-73b728 note="<final outcome>"
```
