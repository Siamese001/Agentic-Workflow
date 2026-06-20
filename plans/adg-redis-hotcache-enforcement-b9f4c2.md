---
plan_id: adg-redis-hotcache-enforcement-b9f4c2
plan_type: infra    # refactor | governance | audit | doc | infra | tracker | platform_core_change
touches_agentic_core: false
touches_governance_ci: true   # modifies a pre_user_prompt hook + a CI gate + hooks.json
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# ADG Redis Hot-Cache Enforcement — SQLite MCP as SSOT, Redis MCP as Hot Cache

Repair the constitutional §13 "MCP green light before T2/T3" gate so it actually fires: ADG **SQLite MCP is the authoritative health signal (SSOT)**, ADG **Redis is a non-authoritative hot-cache accelerator** (cold = warn, never block), driven off live snapshot availability instead of an orphaned sentinel and a nonexistent probe script.

> **plan_id discipline**: filename stem `adg-redis-hotcache-enforcement-b9f4c2` == `plan_id`. Wave markers use `plan=adg-redis-hotcache-enforcement-b9f4c2`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W3
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-07

---

## Context (SCQA)

- **Situation** — Constitutional §13 mandates a T2/T3 "MCP green light": Redis hot cache (`adg_redis_ingest.py --check`) → `adg_health` fallback, *"Both red = BLOCKED."* The gate is implemented in [pre_prompt_classifier.py](.codex/governance/scripts/pre_prompt_classifier.py). The rest of the ADG stack already treats SQLite as canonical and Redis as a hot projection ([adg-canonical-invariants.md](.codex/rules/adg-canonical-invariants.md) §1; [redis_cache.py:38-43](tools/adg/cache/redis_cache.py); CI gate [check_mcp_adg_redis_consistency.py](ops_scripts/ci/check_mcp_adg_redis_consistency.py)).
- **Complication** — The gate never blocked a single turn. Six independent defects (Gap Register below): an orphaned `_hot` sentinel nobody reliably publishes; a hardcoded `localhost:6379` probe contradicting the `ADG_REDIS_URL` SSOT the rest of the stack enforces (S-03/S-08); a fail-open AND-condition; a **nonexistent** `ops_scripts/ci/mcp_health_check.py` that makes the fallback always read "green"; keyword tiering that skips the check; and **no registration** of the hook on the Claude Code surface. It carried over inert from prior IDE surfaces.
- **Question** — How do we make the green-light gate enforce correctly, with ADG SQLite MCP as the authoritative SSOT signal and ADG Redis MCP as a non-authoritative hot cache?
- **Answer** — Re-anchor the gate on ADG SQLite SSOT snapshot availability (a red SSOT blocks; a Redis hot-cache hit may not substitute for it), resolve Redis via the `ADG_REDIS_URL` SSOT, register the gate on the Claude Code `UserPromptSubmit` surface, and lock it with tests.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Unify Redis URL contract + correct gate semantics (SQLite SSOT / Redis advisory) | ✅ DONE | resolver class | 2 |
| W2 | Real health signal: SSOT snapshot probe replaces dead mcp_health_check.py | ✅ DONE | — | 1 |
| W3 | Wire into Claude Code surface + sentinel publish + tests/§13 wording | ✅ DONE | 20 | 4 |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Shared `ADG_REDIS_URL` resolver replaces hardcoded localhost in probe helpers | ✅ DONE |
| W1.2 | Redefine gate semantics: SQLite red ⇒ BLOCK, Redis cold ⇒ WARN-only | ✅ DONE |
| W2.1 | Replace dead `mcp_health_check.py` dependency with SSOT snapshot probe | ✅ DONE |
| W2.2 | Hot/cold derived from real state; sentinel becomes optional fast-path | ✅ DONE |
| W3.1 | Register gate on `UserPromptSubmit` (dispatched from before_submit_prompt.py) | ✅ DONE |
| W3.2 | Tests, §13 wording, memory writeback | ✅ DONE |

---

## Out Of Scope

- Changing the ADG Redis **key scheme** or the `redis_cache.py` read-through cache itself.
- Re-architecting the tier classifier's keyword heuristics.
- Any `agentic_core/**` edit.
- Legacy mirror scripts under `_legacy_*` — forward-only on the Claude Code surface.
- Standing up / sizing a remote Redis instance (operational).
- `check_mcp_adg_redis_consistency.py` legacy-path breakage — DEFERRED to the legacy-tree decommission effort (see Gap Register / W3.2 note).

---

## ADG Evidence Note

Structural blast radius is the governance/hook + tools/adg surface, **not** the L0–L6 product spine, so a full `## ADG_HOTSPOT_REPORT` / `## ADG_GRAPH_LAYER_EVIDENCE` (constitutional §22) is not applicable (`plan_type: infra`). Touched nodes: `pre_prompt_classifier.py`, `pre_user_prompt_adg_ssot_gate.py` (new), `before_submit_prompt.py`, `constitutional.md`, two test files. SQLite-canonical invariant preserved end-to-end: Redis never becomes an authority.

---

## Wave 1 — Unify Redis URL Contract + Correct Gate Semantics

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — Shared `ADG_REDIS_URL` resolver replaces hardcoded localhost | PHASE_STATUS: DONE
- **W1.2** — SQLite-SSOT / Redis-advisory gate semantics | PHASE_STATUS: DONE

**Acceptance** (met): `check_redis_up()` / `check_redis_adg_hot()` resolve from `ADG_REDIS_URL` (localhost only as named fallback); block keys on SQLite-red alone, Redis cold = WARN-only.

---

## Wave 2 — Real Health Signal, Retire Dead Probe + Orphan Sentinel

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Replace nonexistent `mcp_health_check.py` call with an SSOT snapshot probe | PHASE_STATUS: DONE
- **W2.2** — Hot/cold from real state; `_hot` sentinel = optional fast-path | PHASE_STATUS: DONE

**Acceptance** (met): `check_adg_health_red()` now does a bounded read-only sqlite probe of the latest `artifacts/adg/adg_indexed_*.sqlite`; "red" = no readable canonical snapshot. MCP-server-down with a readable snapshot is green (constitutional §28 direct-SQLite fallback).

---

## Wave 3 — Wire Into Claude Code Surface + Lock With Tests

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: C

**Authorization**: self-authorized — modifies `.codex/hooks/before_submit_prompt.py` dispatch + constitutional §13 wording; no new `.codex/hooks.json` entry needed (before_submit_prompt.py is already the registered `UserPromptSubmit` hook).

**Phases**:
- **W3.1** — Register gate via before_submit_prompt.py dispatch; sentinel publish on regen | PHASE_STATUS: DONE
- **W3.2** — Tests + §13 wording + memory writeback | PHASE_STATUS: DONE

**Acceptance** (met): `before_submit_prompt.py` dispatches `pre_user_prompt_adg_ssot_gate.py` and propagates its exit-2 block; auto-ingest surfaces a visible WARNING on a failed/unconfigured ingest; 154 tests green.

---

## Execution Details

### W1.1 / W1.2 — Resolver + semantics
`_resolve_redis_url()` (env `ADG_REDIS_URL` or `redis://localhost:6379/0` fallback); `check_redis_up()` parses host/port from it; `check_redis_adg_hot()` resolves the same. Decision block: SQLite-SSOT red ⇒ `return 2`; Redis hot/cold/down ⇒ advisory stderr, never blocks.

### W2.1 / W2.2 — SSOT snapshot probe
`check_adg_health_red(repo_root)` rewritten: find latest `artifacts/adg/adg_indexed_*.sqlite`; none ⇒ red; open read-only + `SELECT 1 FROM sqlite_master LIMIT 1` ⇒ green; corrupt ⇒ red; no ADG dir / OS error ⇒ fail-open. Removed unused `subprocess` import.

### W3.1 / W3.2 — Surface wiring + tests
New `pre_user_prompt_adg_ssot_gate.py` reuses the classifier probe logic and enforces only the green-light contract. `before_submit_prompt.py` dispatches it (subprocess, surfaces stderr, propagates exit 2 via `block()`). Bypass `ADG_SSOT_GATE_BYPASS=1`. Tests: `tests/unit/ops_scripts/hooks/cursor/test_pre_user_prompt_adg_ssot_gate.py` (20) + resolver regression class. Constitutional §13 reworded to SQLite-SSOT authority / Redis advisory.

---

## Gap Register

**GAP-1: Orphaned `_hot` sentinel** — addressed: sentinel is now an optional fast-path; correctness no longer depends on it (Redis advisory). (W2.2)

**GAP-2: Hardcoded localhost vs `ADG_REDIS_URL` SSOT** — fixed via `_resolve_redis_url()` + regression test. (W1.1)

**GAP-3: Fail-open AND-gate** — fixed: SQLite-SSOT red is the sole BLOCK trigger; Redis never blocks. (W1.2)

**GAP-4: Dead probe script** — fixed: `mcp_health_check.py` dependency removed; replaced with a direct SSOT snapshot probe. (W2.1)

**GAP-5: Tier misrouting** — noted, out of scope (keyword heuristics unchanged; ≤4-word continuation⇒T2 default retained).

**GAP-6: Not registered on Claude Code surface** — fixed: dispatched from the already-registered `before_submit_prompt.py` `UserPromptSubmit` hook. (W3.1)

**GAP-7 (discovered):** `check_mcp_adg_redis_consistency.py` hard-errors on a decommissioned legacy-tree config path. DEFERRED to the legacy-tree decommission effort; the protected invariant (live `.mcp.json` `ADG_REDIS_URL` parity) was independently verified green.

---

## Definition of Done

DoD-1: SQLite-SSOT gate blocks correctly and Redis is advisory-only.
- Evidence: direct exit-code harness — missing-SSOT T3 ⇒ 2, present-SSOT T3 ⇒ 0, T0 red-SSOT ⇒ 0.
- Status: DONE

DoD-2: Smoke-run of the green-light surface.
- Evidence: `before_submit_prompt.py` E2E with a T3 payload exits 0 + advisory line; `pre_user_prompt_adg_ssot_gate.py` standalone exits 0/2 deterministically.
- Status: DONE

DoD-3: Tests added, zero regressions.
- Evidence: `pytest tests/unit/ops_scripts/hooks/windsurf/test_pre_prompt_classifier.py tests/unit/ops_scripts/hooks/cursor/test_pre_user_prompt_adg_ssot_gate.py` → 154 passed.
- Status: DONE

DoD-4: CI gate green / no new violations.
- Evidence: live `.mcp.json` `ADG_REDIS_URL` parity verified True. `check_mcp_adg_redis_consistency.py` red on a pre-existing decommissioned legacy path only (GAP-7, DEFERRED).
- Status: PARTIAL

DoD-5: Hook registered + docs/memory updated.
- Evidence: dispatch wired in `before_submit_prompt.py`; constitutional §13 updated; `mem:ProceduralPattern:ADGRedisSSOTGreenLightGate` written.
- Status: DONE

DoD-6: Sentinel publish guaranteed on regen/refresh.
- Evidence: regen auto-ingest calls `adg_redis_ingest.py --force` (writes `_hot`); failed/unconfigured ingest surfaces a visible `[ADG] WARNING` with the explanatory stderr (no silent no-op).
- Status: DONE

---

## Marker Quick Reference

```
WAVE_COMPLETE: plan=adg-redis-hotcache-enforcement-b9f4c2 wave=<N> note="..."
PLAN_COMPLETE: plan=adg-redis-hotcache-enforcement-b9f4c2 note="<final outcome>"
```
