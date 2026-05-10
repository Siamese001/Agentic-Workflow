---
trigger: always_on
---

# Notion Plan-Wave Deferral

> ⛔ **While executing a multi-wave plan, Cascade MUST NOT call any Notion MCP tool. ALL Notion writes are deferred until after the final wave completes.**

## Protocol

1. **Wave 1 start**: `python tools/windsurf/wave_execution_state.py start --plan <slug-6hex>` — also patches Plans DB Status → `In Progress` via direct HTTP (sanctioned non-MCP path, see below).
2. **During execution**: NO Notion **MCP** calls. `pre_mcp_gate.check_notion_wave_deferral()` blocks MCP deterministically. Direct-HTTP wave-progress writes ARE sanctioned (see §"Sanctioned non-MCP path").
3. **After each wave** (optional but recommended): `python tools/windsurf/wave_execution_state.py wave-progress --plan <slug-6hex> --wave N` — appends `[Wave-Log <ts>] W{N} DONE` to Notion Summary via direct HTTP.
4. **After final wave**: `python tools/windsurf/wave_execution_state.py complete --plan <slug-6hex>` — patches Plans DB Status → `Completed` via direct HTTP.
5. **After step 4**: any remaining Cascade-side Notion **MCP** writes (post-mortem reads, ledger sync, etc.) batch one-per-block per §25.

Applies to plans with ≥2 waves. Single-wave/T0/T1 exempt. Notion **reads** at end-of-plan, not end-of-wave.

## Sanctioned non-MCP path (added 2026-05-10, plan notion-wave-lifecycle-autosync-f4a2b8)

> ⛔ The "no Notion MCP calls" rule above governs **MCP tool invocations** only — i.e. anything that emits an `<invoke name="mcp*_API-*">` tag in the Cascade response. **Direct HTTP calls to Notion's REST API from Python scripts are explicitly sanctioned**, even mid-wave, because they:
>
> 1. Do not invoke any MCP tool (no `<invoke>` tag → §25 audit does not fire).
> 2. Do not pass through Cascade's MCP transport layer (immune to the upstream Anthropic concurrent-dispatch race that motivates §25).
> 3. Are deterministically invoked by hooks / CLI subcommands, not by Cascade prose (drift-resistant).

The sanctioned chain is:

| Trigger | Mechanism | Notion side effect |
|---|---|---|
| `wave_execution_state.py start` | Direct HTTP via `tools/notion/wave_lifecycle_writer.py` | Status → `In Progress` (if currently `Not Started`/`Waiting`); Summary append |
| `wave_execution_state.py wave-progress --wave N` | Direct HTTP | Summary append `[Wave-Log <ts>] W{N} DONE` |
| `wave_execution_state.py complete` | Direct HTTP | Status → `Completed`; Summary append `[Wave-Log <ts>] PLAN COMPLETE` |
| `WAVE_START:` / `WAVE_COMPLETE:` / `PHASE_COMPLETE:` / `PLAN_COMPLETE:` markers in Cascade response | `post_cascade_wave_lifecycle_capture.py` hook → direct HTTP | Same as above, decided per marker |

**Failure mode**: fail-soft. Any HTTP error logs to `artifacts/windsurf/wave_lifecycle_notion.jsonl` and exits 0. Wave-state on disk is the source of truth; Notion sync is best-effort.

**Backstop**: CI gate `NP4 Notion Plans wave freshness` (`ops_scripts/ci/check_plan_notion_wave_freshness.py`) detects on-disk-vs-Notion skew >7d on active plans.

## Bypass

- `NOTION_WAVE_DEFERRAL_BYPASS=1` — bypass MCP-call deferral; logged. Use for user-requested mid-plan Notion **MCP reads** only.
- `WAVE_LIFECYCLE_NOTION_BYPASS=1` — skip the sanctioned direct-HTTP writer (logs only, no PATCH). Use when the Notion API is intentionally offline.
- `WAVE_LIFECYCLE_CAPTURE_BYPASS=1` — skip the post-cascade marker hook entirely.

Constitutional §25, §35, §36.
