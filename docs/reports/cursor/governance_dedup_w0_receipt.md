# W0 Receipt — governance-dedup-closeout-e8a4c2

**Wave:** W0 — Baseline matrix refresh + dispatch shadow metrics  
**Date:** 2026-05-26  
**Status:** PASS

## W0.1 — Hook audit matrix refresh

| Check | Result |
|-------|--------|
| Command | `python ops_scripts/ci/governance_w3_hook_audit_matrix.py` |
| Matrix JSON | [governance_w3_hook_audit_matrix.json](governance_w3_hook_audit_matrix.json) |
| Matrix MD | [governance_w3_hook_audit_matrix.md](governance_w3_hook_audit_matrix.md) |
| `post_agent_scripts_total` | 42 |
| `hook_required` | 17 |
| `obsolete_candidate` | 12 |
| `manual_only` | 13 |
| Strategy | `after_agent_governance_dispatch.py` (single `afterAgentResponse` entry) |

## W0.2 — Dispatch shadow baseline

| Check | Result |
|-------|--------|
| Artifact | [governance_dispatch_shadow.jsonl](../../artifacts/cursor/governance_dispatch_shadow.jsonl) |
| Event | `shadow_period_started` |
| `shadow_days_required` | 7 |
| W1 eligible (earliest) | 2026-06-02 UTC (7 days after W0 start) |
| AG chain scripts | 10 (governance dispatch `_AG_CHAIN`) |
| Dispatch legacy scripts | 13 (`post_cursor_agent_dispatch` in-process) |

## Verification gates

| Gate | Result |
|------|--------|
| `check_ag_hook_wiring.py` | PASS (AG-WIRE-1..4) |
| `check_cursor_optimized_config.py` | PASS (4 alwaysApply; plan sprawl warning only) |

## Notion / wave lifecycle

| Check | Result |
|-------|--------|
| Plan registration | Notion page `36c27693-f55c-815e-a2d1-e6e867ffe7bd` |
| `wave_execution_state.py start` | OK — Status → In Progress |
| Windsurf cache sync | Merged slug from `.cursor/state` → `.windsurf/state` (cache path drift) |

## Marker

```
WAVE_COMPLETE: plan=governance-dedup-closeout-e8a4c2 wave=0 note="matrix refresh 42 scripts 12 obsolete, shadow jsonl started, AG-WIRE PASS"
```

## Next wave

**W1** — Archive obsolete post-agent scripts (blocked until shadow ≥7 days unless operator waives with receipt).
