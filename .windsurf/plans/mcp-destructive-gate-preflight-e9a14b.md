# MCP Destructive-Call Health Preflight Gate

> Plan ID: `mcp-destructive-gate-preflight-e9a14b`
> Created: 2026-04-24
> Source: RCA — `adg_health` not called before `adg_close_connections` hang (2026-04-24 session)
> Status: **W1 DONE (2026-04-24 14:09 UTC)** — pending live verification on next MCP cycle

## Context

Constitutional §13 requires **MCP Green Light** (Redis hot cache → `adg_health` fallback) before T2/T3 work. Enforcement is `pre_prompt_classifier.py` Step 0, which fires **only on prompt ingress**. Autonomous T2/T3 loops bypass it.

In the 2026-04-24 ADG burn-down session, Cascade issued 7+ `mcp1_adg_close_connections` calls across ~2 hours with **zero** `mcp1_adg_health` calls. A cumulative hang forced the user to cancel a pending call. Post-cancel `adg_health` confirmed the service was actually healthy the entire time — the hang was attributable to repeated state-mutating calls against an MCP with no verified health signal.

Secondary finding: `close_connections` returning `{"closed": false, "message": "No active ADG service instance to close."}` is ambiguous — indistinguishable between "service never opened a connection" (benign) and "service is non-responsive" (dangerous). Without a preceding health call, Cascade cannot disambiguate.

## Goal

Treat destructive / state-mutating MCP calls (`adg_close_connections`, `adg_reopen_connections`, `adg_reload`, `redis_flush_namespace`, `redis_del_key`, `redis_del_pattern`, `mem_cleanup_stale`) as **preflight-gated**: require a recent (≤60s) `adg_health` / `redis_health` / `memory_health` success before the call is honored.

## Non-Goals

- Blocking read-only MCP calls (`adg_node`, `adg_edge_fanin`, etc.) — no change.
- Changing MCP server internals — enforcement is Cascade-side via a `pre_mcp_gate` extension.
- Runtime HITL (v30 step [5], ADR-023) — out of scope.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1, P2 | Preflight gate + audit hook | ~5500 | `pre_mcp_gate.py` can parse Cascade's outbound tool invocation; `artifacts/windsurf/` writable | 🟢 Todo | Destructive MCP call without recent health preflight is blocked; audit log captures omissions |

🟢 GREEN — both phases under 8k tokens

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1 | Preflight requirement in `pre_mcp_gate.py` | `.windsurf/scripts/pre_mcp_gate.py`, `.windsurf/hooks.json`, `ops_scripts/ci/check_mcp_preflight.py` | Need to track "last health call timestamp" per server across Cascade turn boundaries; no existing cross-turn state for tool invocations | ~3500 | Todo |
| P2 | Post-response audit of preflight omissions | `.windsurf/scripts/post_cascade_mcp_preflight_audit.py`, `artifacts/windsurf/mcp_preflight_violations.jsonl`, session-start surfacer | Audit must run fail-open (exit 0 on internal error) to match `mcp_serialization_audit` pattern | ~2000 | Todo |

## Gap Register

| Gap | Impact | Mitigation |
|-----|--------|------------|
| Cross-turn state | `pre_mcp_gate.py` runs per-call; no built-in memory of prior turns' health calls | Persist last-health-ok timestamps to `artifacts/windsurf/mcp_health_heartbeat.json`; read on preflight check |
| False-positive on server startup | First MCP call of a new session has no prior health call | Grace-window: allow first 60s of session to pass without heartbeat (bootstraps naturally when first `adg_health` completes) |
| Destructive-call classification | Not all MCP tools are equally destructive | Explicit allowlist (`_DESTRUCTIVE_MCP_TOOLS` set in gate); missing tools fail-open by default |

## Success Criteria

- [ ] `pre_mcp_gate.py` blocks `adg_close_connections` / `adg_reload` / `redis_flush_namespace` when no `adg_health` / `redis_health` success in the last 60s.
- [ ] `artifacts/windsurf/mcp_preflight_violations.jsonl` captures every bypass or omission with UTC timestamp, tool, and reason.
- [ ] Session-start hook surfaces preflight violation count if non-zero.
- [ ] Adding a new destructive MCP tool to `_DESTRUCTIVE_MCP_TOOLS` is a single-line change with CI gate to require doc update.
- [ ] Escape hatch: `MCP_PREFLIGHT_BYPASS=1` logs a bypass row and passes (matches `MCP_SERIAL_BYPASS` precedent).

## References

- Constitutional §13 (MCP Green Light) — `c:/Git/Agentic-Workflow/.windsurf/rules/constitutional.md`
- Precedent: `post_cascade_mcp_serialization_audit.py` — fail-open audit hook template
- Precedent: `pre_mcp_gate.py` — ADG SQLite lock protocol (already blocks ADG calls during write lock)
- RCA source: conversation 2026-04-24 06:51 UTC (ADG burn-down session)

## Notes

This is a **developer-loop (harness)** gate, not runtime HITL. It protects Cascade's outbound MCP calls, not user-facing agent actions. Runtime HITL is governed by ADR-023 and lives in `agentic_core/L5_safety/`.
