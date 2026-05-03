---
trigger: always_on
---

# Notion Plan-Wave Deferral — No Mid-Plan Notion Writes

> ⛔ **While executing a multi-wave plan, Cascade MUST NOT call any Notion MCP tool. ALL Notion writes are deferred until after the final wave completes.**

Sibling to constitutional §25 (MCP serialization — remote MCPs one per response). This rule operationalizes the case where a plan contains multiple waves: mid-wave Notion calls stall the turn and force the user to manually prompt "next wave" repeatedly. Batching to plan-end eliminates the stalls.

## The Protocol

1. **At the start of Wave 1** of any multi-wave plan, Cascade runs:

    ```bash
    python tools/windsurf/wave_execution_state.py start --plan <slug-6hex>
    ```

    where `<slug-6hex>` matches the plan filename `.windsurf/plans/<slug>-<6hex>.md` (without the `.md` suffix).

2. **During wave execution**, Cascade DOES NOT call any Notion MCP tool. `pre_mcp_gate.check_notion_wave_deferral()` blocks all Notion calls while the state file exists — the block is deterministic, not advisory.

3. **After the FINAL wave's verification passes**, Cascade runs:

    ```bash
    python tools/windsurf/wave_execution_state.py complete --plan <slug-6hex>
    ```

4. **Only after step 3**, Cascade batches all deferred Notion writes (plan status updates, backlog row updates, ADR-related rows, etc.) in a sequence of one-Notion-call-per-response turns per §25.

## When This Applies

- ANY plan at `.windsurf/plans/<slug>-<6hex>.md` with a Wave Structure table containing ≥2 waves.
- T2/T3 tasks where waves must complete sequentially without mid-way user prompting.

Does NOT apply to:

- Single-wave plans or T0/T1 tasks.
- Notion **reads** when explicitly requested by the user mid-plan — bypass with `NOTION_WAVE_DEFERRAL_BYPASS=1` one-shot env var (logged), rare.
- Reads of Plans DB to determine wave status BEFORE `start` is invoked.

## Forbidden Patterns

- ❌ Calling `API-patch-page`, `API-post-page`, `API-query-data-source`, or any other Notion tool between `start` and `complete`.
- ❌ Clearing wave-execution state to "sneak in" a Notion write, then restarting it.
- ❌ Interpreting this rule as "batch Notion calls at the end of each wave" — it is **end of plan**, not end of wave.

## Bypass

`NOTION_WAVE_DEFERRAL_BYPASS=1` — emits `BLOCKED` → `allowed (bypass)` trace and lets the call proceed. Use only when the user explicitly requests a mid-plan Notion read, or for scripted exceptional batch runs.

## Enforcement

1. **This rule** (always_on — behavioral).
2. **Helper** `.windsurf/scripts/_wave_execution_state.py` — session-scoped state API.
3. **CLI** `tools/windsurf/wave_execution_state.py` — `start | complete | status`.
4. **Hook** `pre_mcp_gate.check_notion_wave_deferral()` — deterministic block at `pre_mcp_tool_use`.
5. **Tests** `tests/unit/windsurf_scripts/test_wave_execution_state.py`.

## References

- Constitutional §25 (MCP serialization — remote MCPs)
- `mcp-serialization.md` (remote-MCP allowlist)
- `plan-location.md` (plan SSOT location and wave-table format)
- `memory-notion-writeback.md` (what to write back at plan completion)
