# ADR-095 — Memory MCP ritual superseded by native file memory

- **Status:** Accepted
- **Date:** 2026-06-07
- **Plan:** [claude-native-supersession-9d3f7a](../../../plans/claude-native-supersession-9d3f7a.md) (Wave W3)

## Context

The memory contract mandated `mem_recall_session_start` as the **first tool call of every session**
(constitutional §17), enforced by a hard **memory-first gate** in `pre_mcp_gate.py` that blocked all
other MCP calls until recall ran, plus purge/staleness gates (`mem_cleanup_stale`,
`check_memory_health.py`, `purge_sync.py`) to keep an auto-growing SQLite knowledge graph from bloating.

Claude Code now ships **native file-based memory** (`memory/MEMORY.md` + per-fact files) that is loaded
into context at session start by the harness — no ritual call, and curated-not-auto-grown so no purge
gate is needed.

## Decision

- **Invariant kept:** recall project memory at session start; write back significant decisions/patterns
  (the 15/3 rule). Target shifts from the MCP graph to native file memory.
- **Retired:**
  - The mandatory `mem_recall_session_start` first-call ritual (constitutional §17 reworded).
  - The **memory-first MCP gate** in `pre_mcp_gate.py` (the block that fail-closed every non-memory MCP
    call). Its other checks (Notion token, GitKraken, serialization) are untouched.
  - The purge/staleness obligations as *requirements* (the maintenance guidance survives, scoped to
    "only when the MCP is in use").
- **Kept optional:** the knowledge-graph MCP remains available for genuine graph queries
  (cross-entity relations); it is no longer the mandated SSOT.

## Consequences

- No first-call ordering constraint; MCP calls aren't gated on a recall ritual.
- Memory that must survive across sessions lives in `memory/` (version-controlled, human-readable).
- `check_memory_health.py` / `purge_sync.py` are dormant (not invoked by `run_contract_gates.py`);
  swept in W5.
- Reversible: §17 text and the gate block restorable from git history.
