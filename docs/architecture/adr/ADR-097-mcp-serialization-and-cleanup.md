# ADR-097 — MCP serialization retired; W5 cleanup scope & deferral

- **Status:** Accepted
- **Date:** 2026-06-07
- **Plan:** [claude-native-supersession-9d3f7a](../../../plans/claude-native-supersession-9d3f7a.md) (Wave W5)

## Context

W5 (S5/S6) covered hook-overhead, legacy trees, thin-alias commands, and the MCP-serialization rule.
During execution the working repository was found to host **concurrent parallel decommission efforts**
(`chore/governance-rule-residue-cleanup`, `cursor-decommission`, `windsurf-deprecation`) that already
own legacy-tree deletion and brand-decommission. To avoid collision, W5 was scoped to the items unique
to this plan.

## Decision

**Done in W5:**
- **`mcp-serialization.md` retired** — the "one remote-MCP call per block" batching constraint was a
  legacy-IDE transport limitation; Claude Code parallelizes MCP calls natively. `pre_mcp_gate.py`'s
  substantive checks (Notion token, GitKraken upstream) are untouched.
- **Dead Author-Gate alias commands removed** — `author-gate-decision-gate.md`,
  `antipattern-author-gate.md`, `author-gate-calibration-report.md` (aliases to W1-retired machinery).
- **Stop-dispatch already slimmed in W1** — `_AG_CHAIN` dropped from 10 → 2 entries.

**Deferred (to avoid collision with parallel efforts, not abandoned):**
- **Legacy-tree deletion** (`.claude/governance/scripts/_legacy_cursor/`, `_legacy_windsurf/`) — owned
  by the active `cursor-decommission` / `windsurf-deprecation` branches; deleting here would conflict.
- **Physical archiving of dormant scripts** from W1/W3/W4 (`pre_author_gate.py`, `_author_gate_queue.py`,
  `post_cursor_agent_*_author_gate_*.py`, `post_cursor_agent_deferred_scope_capture.py`,
  `tools/priority/deferred_scope_scorer.py`, memory purge tools, the `ops_scripts/ci/author_gate/`
  gate scripts). These are **dormant** (no invocation path remains after W1–W4), so leaving them
  on-disk is inert. Moving them risks breaking the `post_cursor_agent_dispatch.py` / `_post_handlers`
  import graph and the legacy unit tests under `tests/unit/windsurf_scripts/` that still import them —
  best done as a dedicated sweep with a full import-graph check, coordinated with the decommission
  effort.
- **tavily-/adg- alias commands** kept — they alias *live* skills, out of this plan's scope.

## Consequences

- The behavioural supersession (W1–W4) is complete and self-consistent: no live invocation path,
  rule, or constitutional clause still *requires* the retired machinery.
- Residual dormant files are inert and clearly marked for a follow-up decommission sweep.
- Reversible from git history.
