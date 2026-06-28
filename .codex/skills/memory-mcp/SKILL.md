---
name: memory-mcp
description: Optional SQLite-backed knowledge graph projection. Native file memory under memory/ is SSOT; use this MCP only when graph recall/writeback is useful and the transport is healthy.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
  deprecated: true
  redirect_to: mcp-integration
---
# DEPRECATED - Redirected to mcp-integration §12

> **Consolidated**: This skill content moved to `mcp-integration/SKILL.md` §12 — Memory MCP (2026-05-12, W4.P2).
> **Status**: Redirect stub — preserved for backwards compatibility.
> **Action**: Consult `.codex/skills/mcp-integration/SKILL.md` §12 for current guidance.
> **ADR-095 update**: Native file memory under `memory/` is SSOT. `mem_recall_session_start` is no
> longer a mandatory first-call ritual; Memory MCP degrades to file memory when unavailable.

---
