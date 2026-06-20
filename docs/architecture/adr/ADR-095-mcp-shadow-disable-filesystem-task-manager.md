# ADR-095 — Shadow-Disable filesystem + task_manager MCPs

**Status:** Accepted
**Date:** 2026-05-02
**Deciders:** Codex (Author-Gate, plan `token-burn-followup-f8c2d1`)
**Plan:** `.codex/plans/token-burn-followup-f8c2d1.md` W3 / F4
**Predecessor data:** `.codex/plans/windsurf-token-burn-augmentation-b7a3f1.md` W2 / P6 (MCP schema cost audit)
**Impact Layers:** harness (`.mcp.json`); no `agentic_core/` impact

## Context

The W2 MCP schema cost audit (re-run in W3 W1 with PATHEXT fix) measured all 10 stdio MCPs:

- 111 tools, 74,963 bytes, ~18,740 always-on tokens
- This **exceeds the entire always-on rules cap** (12,800 tokens) by 46%
- MCP retirement is the highest-leverage remaining lever for token-burn reduction

W2 telemetry data (turn_budget.jsonl per-MCP usage frequency) is wall-clock-gated at ≥7 days and is not yet available. Author-Gate F4 must decide retirement candidates with available evidence: schema cost + architectural substitute analysis.

## Author-Gate F4 Decisions (per candidate)

### Candidate 1: `io.windsurf/mcp-playwright` (4,250 tokens / 23 tools / 185 per-tool)

| Option | Score | Rationale |
|--------|------:|-----------|
| **Keep** | **0.88** | Per-tool cost (185) is below median; functionality unique (browser automation, accessibility snapshots, E2E verification); no native substitute; retiring blocks `apps_*` E2E paths. |
| Shadow-disable | 0.40 | Would block any active E2E verification work; no upside until usage data shows none. |
| Retire | 0.10 | Same as above, irreversible. |

**Verdict: Keep.** (Dominance gap 0.48; surface alone.)

### Candidate 2: `filesystem` (3,056 tokens / 14 tools / 218 per-tool)

| Option | Score | Rationale |
|--------|------:|-----------|
| **Shadow-disable** | **0.78** | Native substitutes cover the 14 tools: `read_file`, `write_to_file`, `edit`, `list_dir`, `find_by_name`, `grep_search`. Pure-MCP-only use cases (`read_multiple_files`, `directory_tree`) have native equivalents at slight efficiency cost. Reversible. |
| Keep | 0.55 | Convenient for batch reads; non-zero historical use. |
| Retire | 0.30 | Premature without 30-day usage data; reversibility is cheap. |

**Verdict: Shadow-disable.** (Top score 0.78 < 0.85 surface-alone threshold; user-pre-authorized "finish all scope" closes the gate.)

### Candidate 3: `task_manager` (2,524 tokens / 4 tools / **631 per-tool — worst ratio**)

| Option | Score | Rationale |
|--------|------:|-----------|
| **Shadow-disable** | **0.82** | Highest per-tool waste in the fleet (631/tool vs median 117). Substitute: `structured-reasoning` skill (`SR_PLAN`/`SR_EXECUTE`) covers multi-step workflows. The MCP's distinctive value is *durable* task state across sessions — niche and rarely needed. |
| Retire | 0.45 | Same outcome as shadow-disable but irreversible without 30-day data. |
| Keep | 0.40 | No clear advantage given the per-tool ratio. |

**Verdict: Shadow-disable.** (Top score 0.82 < 0.85 surface-alone threshold; user-pre-authorized.)

### Candidate 4: `context7` (1,273 tokens / 2 tools / **637 per-tool — highest ratio**)

| Option | Score | Rationale |
|--------|------:|-----------|
| **Keep** | **0.72** | Lowest absolute cost in the candidate set (1,273 tokens). Unique value: versioned upstream library docs. Substitutes (`tavily_search`, `read_url_content`) are weaker — not version-aware, not structured. Worth the per-tool ratio at this absolute cost. |
| Shadow-disable | 0.50 | Would be saved 1,273 tokens; usage frequency unknown. |
| Retire | 0.20 | Premature; substitutes weaker. |

**Verdict: Keep.** (Dominance gap 0.22; user-pre-authorized.)

## Decision

| MCP | Verdict | Token Savings (until re-enable) |
|-----|---------|---------------------------------|
| `io.windsurf/mcp-playwright` | Keep | 0 |
| `filesystem` | **Shadow-disable** | **3,056** |
| `task_manager` | **Shadow-disable** | **2,524** |
| `context7` | Keep | 0 |
| **Total potential savings** | | **5,580 tokens (29.8% of MCP fleet always-on cost)** |

Implementation: `.mcp.json` — set `"disabled": true` on `filesystem` and `task_manager`; preserve all other config so re-enabling is a single JSON-bool flip.

## Re-Enablement / Retirement Criteria (30-day review)

**Methodology correction (added at decision time):** disabled MCPs do not appear in Codex's tool list, so direct tool-call counts in `turn_budget.jsonl` will always be 0 for the disabled prefixes. The retirement signal is **operator judgment** informed by:

1. **Diagnostic script:** `python tools/diagnostics/mcp_30day_retirement_review.py` (run on or after 2026-06-01) — confirms config status, days elapsed, telemetry baseline, and any anomalous calls (which should be 0).
2. **Operator checklist** (printed by the script): During the 30-day window, did any task feel harder due to absence? Were native substitutes strictly worse? Are there pending workflows that NEED the MCP within the next 30 days?

If all three answers are "no" → **RETIRE**: write retirement ADR; remove the entry from `mcp_config.json`; AGENTS.md regenerates via `python .codex/governance/scripts/sync_mcp_config.py`.

If any answer is "yes" → **RE-ENABLE**: set `disabled: false`; document the substitute-insufficiency case in a follow-up ADR.

Rollback: single keystroke per MCP (`disabled: true` → `disabled: false`); restart legacy editor. CI gate `check_mcp_sync_integrity.py` catches AGENTS.md drift on next pre-commit.

## Related

- Plan `token-burn-followup-f8c2d1` (this plan, W3 closure)
- Predecessor plan `windsurf-token-burn-augmentation-b7a3f1` (sealed)
- Constitutional §34 (per-turn retrieval budgets)
- AGENTS.md MCP Quick Reference (auto-regenerated by `.codex/governance/scripts/sync_mcp_config.py`)
- Author-Gate enforcement: `.codex/rules/author-gate-enforcement.md`

## Decision Captured

`DECISION_CAPTURED: type=mcp_retirement_review id=ADR-095 verdicts=4 shadow_disabled=2 kept=2 retired=0 token_savings_potential=5580`
