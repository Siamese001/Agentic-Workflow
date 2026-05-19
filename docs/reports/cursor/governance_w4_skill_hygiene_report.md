# W4 — Skill hygiene + mcp-integration index split

**Plan:** [cursor-governance-two-tier-b4e8f2.md](../../.cursor/plans/cursor-governance-two-tier-b4e8f2.md)  
**Generated:** 2026-05-19

## STATUS: PASS

## Skill description gate

| Metric | Value |
|--------|------:|
| SKILLS_TOTAL | 35 |
| SKILLS_PASS | 31 |
| SKILLS_FAIL | 0 |
| SKILLS_WARN | 4 |

**Gate:** [check_skill_description_quality.py](../../ops_scripts/ci/check_skill_description_quality.py) (wired in [run_contract_gates.py](../../ops_scripts/ci/run_contract_gates.py) MCP health phase).

**WARN (non-blocking):** `desc_duplicates_body_opener` — app-leakage-refactor, core-boundary-audit, scope-containment, u0-app-customization.

## mcp-integration trim/split

| Metric | Value |
|--------|------:|
| MCP_INTEGRATION_BEFORE_BYTES | 18,264 |
| MCP_INTEGRATION_AFTER_BYTES | 3,989 |
| Budget | ≤ 8,192 |

**Index:** [SKILL.md](../../.cursor/skills/mcp-integration/SKILL.md) (quick ref + progressive-disclosure table).  
**Bodies:** 13 files under [sections/](../../.cursor/skills/mcp-integration/sections/).  
**Preserved:** Tavily sole web-search authority (§8); [agents-tier1-companion.md](../../.cursor/skills/mcp-integration/agents-tier1-companion.md); [SUPPORTING.md](../../.cursor/skills/mcp-integration/SUPPORTING.md).

## Tier-1 (Option A)

| Metric | Value |
|--------|------:|
| TIER_1_TOTAL_BYTES | 18,460 |
| ALWAYS_APPLY_COUNT | 4 |
| AGENTS.md bytes | 9,179 |

## DESCRIPTION_RULES_ENFORCED

- Description length 60–420 chars
- When-to-use trigger required
- Body-opener duplication → WARN at ≥55% token overlap
- `mcp-integration/SKILL.md` ≤ 8 KB

## COMMANDS_RUN

| Command | Exit |
|---------|-----:|
| `python ops_scripts/ci/check_skill_description_quality.py` | 0 |
| `python ops_scripts/ci/check_always_on_token_budget.py` | 0 |
| `python .cursor/scripts/check_cursor_optimized_config.py` | 0 |
| `python ops_scripts/ci/check_mcp_sync_integrity.py` | 0 |
| `python ops_scripts/ci/check_ag_hook_wiring.py` | 0 |
| `python ops_scripts/ci/run_contract_gates.py` | 1 (10C pilot pre-existing) |
| `python .cursor/scripts/check_cursor_native_config.py --strict` | 1 (pre-existing) |

## NON_CLAIMS

W5 not executed; closeout not claimed; runtime RAG untouched; `.windsurf` not deleted; `agentic_core` / apps_rg product code untouched by W4.
