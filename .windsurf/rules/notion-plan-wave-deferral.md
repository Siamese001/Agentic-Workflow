---
trigger: always_on
---

# Notion Plan-Wave Deferral

> ⛔ **While executing a multi-wave plan, Cascade MUST NOT call any Notion MCP tool. ALL Notion writes are deferred until after the final wave completes.**

## Protocol

1. **Wave 1 start**: `python tools/windsurf/wave_execution_state.py start --plan <slug-6hex>`
2. **During execution**: NO Notion MCP calls. `pre_mcp_gate.check_notion_wave_deferral()` blocks deterministically.
3. **After final wave**: `python tools/windsurf/wave_execution_state.py complete --plan <slug-6hex>`
4. **After step 3**: batch deferred Notion writes (one per block per §25).

Applies to plans with ≥2 waves. Single-wave/T0/T1 exempt. Notion **reads** at end-of-plan, not end-of-wave.

## Bypass

`NOTION_WAVE_DEFERRAL_BYPASS=1` — logged. Use for user-requested mid-plan Notion reads only. Constitutional §25.
