---
plan_id: hooks-deep-edge-tests-remediation-e7c2a9
plan_type: governance
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Hooks deep edge-case tests — narrow drift remediation (child)

**Parent / predecessor (closed axis):** `cursor-only-governance-ssot-d9e4b1` — SSOT governance, PLAN-DOD, `pre_mcp_gate` shim, dispatcher no-go, NP13/NP-GUARD path alignment. **This plan does not repeat that scope.**

**Owned surface:** `tests/unit/ops_scripts/hooks/windsurf/test_hooks_deep_edge_cases.py` and the hook/audit modules it imports (e.g. `pre_write_gate`, `post_run_audit`, `post_mcp_audit`, `post_write_audit`, cascade cleanup), so that the **full** deep-edge file is green again without changing default `afterAgentResponse` dispatcher wiring.

> **plan_id discipline**: `plan_id` matches filename stem `hooks-deep-edge-tests-remediation-e7c2a9`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-15

---

## Context (SCQA)

- **Situation** — After `pre_mcp_gate` SSOT shim and `repo_root` patch alignment, `TestPreMcpGate*` passes, but **~33** tests in the same file still fail: SSOT-folder blocks on synthetic `foo.py` at repo root, missing module attributes on shims (`PROCESS_LOG`, `AUDIT_LOG`), and `ModuleNotFoundError` for `post_cursor_agent_cleanup`.
- **Complication** — Tests were written against older monolithic `.windsurf/scripts/*.py` contracts; shims and stricter SSOT gates changed observable behavior without a dedicated remediation pass.
- **Question** — How do we realign fixtures, patch targets, and optional bypasses so the suite proves hook contracts **without** weakening production gates or mixing in dispatcher / governance SSOT work?
- **Answer** — Four narrow waves: baseline + contracts, pre-write payloads/paths, post-audit patch surfaces, cascade/cleanup imports — then one command proves the full file passes.

---

## Wave summary (planning)

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.2 | Baseline inventory + patch-target map | ~8k | pytest available | ✅ DONE | Baseline 33 fail captured; root cause = path + patch names + sys.path order |
| W2 | W2.1–W2.2 | `pre_write_gate` / payload fixtures | ~10k | SSOT rules unchanged for prod | ✅ DONE | `_SAFE_PY_REL` + dummy module; argv tests aligned |
| W3 | W3.1–W3.2 | post-audit patch targets | ~12k | Windsurf modules are import SSOT for hooks | ✅ DONE | `process_log` / `audit_log` patches; portable write-audit sink |
| W4 | W4.1 | cleanup import + full file | ~8k | `.cursor/scripts` on path after windsurf | ✅ DONE | 130/130 pytest PASS |

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Baseline + map | ✅ DONE | — | Plan Gap baseline row |
| W2 | Pre-write suite | ✅ DONE | `_pre_write_gate_payload_dummy.py` | `test_hooks_deep_edge_cases.py` |
| W3 | Post-audit suite | ✅ DONE | — | `test_hooks_deep_edge_cases.py` |
| W4 | Cleanup / full file | ✅ DONE | — | `test_hooks_deep_edge_cases.py` |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Pytest baseline capture | ✅ DONE |
| W1.2 | Patch-target / module SSOT map | ✅ DONE |
| W2.1 | Pre-write payload paths | ✅ DONE |
| W2.2 | Pre-write multi-violation expectations | ✅ DONE |
| W3.1 | post_run_audit / post_mcp_audit patches | ✅ DONE |
| W3.2 | post_write_audit patches | ✅ DONE |
| W4.1 | Cleanup import + full-file proof | ✅ DONE |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Baseline capture | `test_hooks_deep_edge_cases.py` | 33 failing classes | ~3k | ✅ DONE |
| W1.2 | Contract map | `.windsurf/scripts`, `.cursor/scripts` | Cursor `pre_write_gate` shadowed Windsurf when `.cursor` was first on `sys.path` | ~4k | ✅ DONE |
| W2.1 | SSOT-safe paths | Tests only | `_SAFE_PY_REL` dummy under `tests/unit/.../windsurf/` | ~5k | ✅ DONE |
| W2.2 | Multi-violation ordering | Tests + gate messages | Same safe path for `module.py` payloads | ~4k | ✅ DONE |
| W3.1 | Run/mcp audit patches | Tests | `process_log` / `audit_log` module globals | ~6k | ✅ DONE |
| W3.2 | Write audit patches | Tests | `audit_log` + tmp sink vs `/dev/null` | ~5k | ✅ DONE |
| W4.1 | Cleanup + full run | Tests | `.cursor/scripts` on path; `windsurf_dir`/`session_summary` patch names | ~8k | ✅ DONE |

---

## Out Of Scope

- `cursor-only-governance-ssot-d9e4b1` closeout items (PLAN-DOD defaults, dispatcher default wiring, NP13/NP-GUARD strings) — already accepted elsewhere.
- Changing default `.cursor/hooks.json` to the multi-handler dispatcher (`POST_CURSOR_AGENT_DISPATCHER`) — explicit non-goal until a separate design plan proves chain replacement.
- Broad refactors of hook semantics beyond restoring test/implementation alignment.

---

## Gap Register

**W1.1 baseline (2026-05-15, pre-fix):** `pytest tests/unit/ops_scripts/hooks/windsurf/test_hooks_deep_edge_cases.py -n 0` → **33 failed, 97 passed**.

**RESOLVED (2026-05-15):** Full file **130 passed** after: (1) `_SAFE_PY_REL` + `_pre_write_gate_payload_dummy.py` for SSOT-safe `.py` payloads; (2) patch `post_run_audit.process_log`, `post_mcp_audit.audit_log`, `post_write_audit.audit_log`; (3) insert `.cursor/scripts` then `.windsurf/scripts` so Windsurf hook modules win over Cursor duplicates; (4) `post_cursor_agent_cleanup` patches `windsurf_dir` / `session_summary`.

**GAP-1: SSOT folder gate vs synthetic root `foo.py`** — **RESOLVED** — use `_SAFE_PY_REL` under `tests/unit/.../windsurf/` (see `_pre_write_gate_payload_dummy.py`).

**GAP-2: Shim vs SSOT for `post_*_audit` patch targets** — **RESOLVED** — patch `process_log` / `audit_log` on imported modules (Windsurf implementations).

**GAP-3: `post_cursor_agent_cleanup` import** — **RESOLVED** — add `.cursor/scripts` to `sys.path` after `.windsurf/scripts`; fix `main()` test patches to `windsurf_dir` / `session_summary`.

---

## Wave 1 — Baseline and contract map

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — Baseline pytest captured | ~3k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Root causes: SSOT paths, wrong patch attr names, sys.path shadowing | ~4k tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**: Met.

---

## Wave 2 — Pre-write gate suite

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Acceptance**: Met (`TestPreWriteGate*`).

---

## Wave 3 — Post-audit suites

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Acceptance**: Met (`TestPost*Audit*`).

---

## Wave 4 — Cascade cleanup + full-file proof

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Acceptance**:
```bash
python -m pytest tests/unit/ops_scripts/hooks/windsurf/test_hooks_deep_edge_cases.py -n 0 -q --timeout=180
```
→ exit 0 (130 passed).

---

## Runtime receipt

Machine-readable: `artifacts/plan_lifecycle/hooks-deep-edge-tests-remediation-e7c2a9_wave_completion_receipt.json`

---

## Definition of Done

DoD-1: Plan file exists at `.cursor/plans/hooks-deep-edge-tests-remediation-e7c2a9.md` with wave summary, phase summary, Gap Register, and this DoD section.
- Evidence: file read / `dir`
- Status: DONE (on creation)

DoD-2: Notion Plans row exists with Status **Not Started**, `Exists On Disk=true`, `Plan File Path` set to `.cursor/plans/hooks-deep-edge-tests-remediation-e7c2a9.md`.
- Evidence: `create_plan_in_notion` → `page_id=36127693-f55c-81b1-87b8-e638fe4aa7e9` (Status Not Started at creation)
- Status: DONE

DoD-3: Wave lifecycle `start` succeeds after registration cache refresh when Notion is available.
- Evidence: `python ops_scripts/ci/check_plan_registration_freshness.py --refresh` (450 Plans rows) then `python tools/windsurf/wave_execution_state.py start --plan hooks-deep-edge-tests-remediation-e7c2a9` → exit 0, `NOTION_SYNC OK`
- Status: DONE

DoD-4: Full test file green (post W4).
- Evidence: `python -m pytest tests/unit/ops_scripts/hooks/windsurf/test_hooks_deep_edge_cases.py -n 0 -q --timeout=180` → exit 0 (130 passed)
- Status: DONE

DoD-5: Explicit statement in PR/commit message or plan note: **no** default dispatcher wiring and **no** governance SSOT scope creep in this branch.
- Evidence: plan Out Of Scope section + this execution stayed in tests + path order only
- Status: DONE

### Verification vs deferral

| DoD | Verified in-wave | Deferred |
|-----|-------------------|----------|
| DoD-1 | Yes | — |
| DoD-2 | Yes | — |
| DoD-3 | Yes | — |
| DoD-4 | Yes | — |
| DoD-5 | Yes | — |

---

## Marker Quick Reference

WAVE_COMPLETE: plan=hooks-deep-edge-tests-remediation-e7c2a9 wave=1 note="baseline + contract map (33 fail inventory)"
WAVE_COMPLETE: plan=hooks-deep-edge-tests-remediation-e7c2a9 wave=2 note="pre_write SSOT-safe _SAFE_PY_REL + argv payloads"
WAVE_COMPLETE: plan=hooks-deep-edge-tests-remediation-e7c2a9 wave=3 note="post_* audit patches process_log/audit_log + write sink"
WAVE_COMPLETE: plan=hooks-deep-edge-tests-remediation-e7c2a9 wave=4 note="sys.path order + cleanup patches; 130 pytest PASS"
PLAN_COMPLETE: plan=hooks-deep-edge-tests-remediation-e7c2a9 note="hooks deep edge tests green; receipt artifacts/plan_lifecycle/hooks-deep-edge-tests-remediation-e7c2a9_wave_completion_receipt.json"

```
WAVE_START: plan=hooks-deep-edge-tests-remediation-e7c2a9 wave=1
```

---

## Scope Expansion Authorization

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter test-only alignment | Yes |
| DEFERRED | Requires hook product behavior change | Yes; split follow-up plan |
| SPLIT_TO_NEW_PLAN | Core hook semantics debate | Yes; keep this file test-only |
| REJECTED | Weakening SSOT / guardian rules to pass tests | No |
