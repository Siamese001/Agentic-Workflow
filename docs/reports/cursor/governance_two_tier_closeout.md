# Cursor governance two-tier consolidation — W5 closeout

**Plan ID:** `cursor-governance-two-tier-b4e8f2`  
**Policy:** Option A (4× `alwaysApply` + `AGENTS.md` ≤15 KB)  
**Closeout date:** 2026-05-19  
**Manifest:** [governance_two_tier_closeout_manifest.json](governance_two_tier_closeout_manifest.json)

## STATUS: PASS (plan scope)

Two-tier Cursor governance consolidation is **closed** for this plan. In-scope gates pass; unrelated failures are documented below and were **not** remediated in W5.

---

## Executive summary

| Dimension | Before (audit) | After (W5) |
|-----------|----------------|------------|
| Tier-1 always-on (Cursor-native) | ~36 KB rules + ~26 KB AGENTS (mis-measured) | **18,460 B** (4 rules + AGENTS) |
| `alwaysApply` rules | 5 (drift) | **4** (Option A) |
| Active top-level plans | ~499 | **10** |
| Rule/skill/workflow duplicate triples | 8 | **0** |
| Post-agent hook wiring | 3 scripts in hooks.json | **1 dispatcher** (41 scripts classified) |
| Graph baseline orphans | 507 | **0** |
| `mcp-integration` SKILL.md | 18,264 B | **3,989 B** (indexed `sections/`) |

---

## Wave evidence summary

### W0 — Truthful measurement

- Extended [check_always_on_token_budget.py](../../ops_scripts/ci/check_always_on_token_budget.py) to measure `.cursor/rules` `alwaysApply` + `AGENTS.md`.
- Added [governance_tier_measurement.py](../../ops_scripts/ci/governance_tier_measurement.py) and [governance_tier_inventory.json](governance_tier_inventory.json).
- Aligned [check_cursor_optimized_config.py](../../.cursor/scripts/check_cursor_optimized_config.py) with Option A target set.

### W1 — Option A convergence

- Demoted extra `alwaysApply`; froze `.windsurf/rules` as read-only mirror ([MIGRATION_MAP.md](../../.cursor/MIGRATION_MAP.md)).
- Compressed [AGENTS.md](../../AGENTS.md) (~26 KB → **9,179 B**); procedural MCP prose → [mcp-integration/agents-tier1-companion.md](../../.cursor/skills/mcp-integration/agents-tier1-companion.md).

### W2 — Cluster dedupe

- Thinned Author-Gate, ADG, structured-reasoning, Tavily, and plan-governance workflows to aliases.
- **Duplicate triples:** 8 → **0** ([governance_w2_dedupe_report.json](governance_w2_dedupe_report.json)).

### W3 — Dispatcher + plan archive

- [hooks.json](../../.cursor/hooks.json): single `after_agent_governance_dispatch.py`.
- Plans **499 → 9** active after archive passes; **490** files under `.cursor/plans/_archive/2026-05/` (no deletes).
- [governance_w3_hook_audit_matrix.json](governance_w3_hook_audit_matrix.json) · [governance_w3_plan_archive_manifest.json](governance_w3_plan_archive_manifest.json).

### W3R — Archive orphan remediation

- Fixed [check_graph_layer_evidence.py](../../ops_scripts/ci/check_graph_layer_evidence.py) baseline integrity for archived plan paths.
- **Orphans:** 507 → **0** ([governance_w3_remediation_receipt.json](governance_w3_remediation_receipt.json)).

### W4 — Skill hygiene + MCP split

- New [check_skill_description_quality.py](../../ops_scripts/ci/check_skill_description_quality.py) (wired in contract-gates MCP health phase).
- **Skills:** 35 total; 31 pass; 0 fail; 4 warn (body-opener overlap only).
- [governance_w4_skill_hygiene_report.json](governance_w4_skill_hygiene_report.json).

### W5 — Closeout (this artifact)

- Evidence bundle on disk; plan marked **COMPLETED**.
- No runtime/product code changes.

---

## Final Tier-1 measurement (Option A)

| Field | Value |
|-------|------:|
| Tier-1 total bytes | 18,460 |
| Threshold | 51,200 |
| Headroom | 32,740 |
| `alwaysApply` count | 4 |
| AGENTS.md bytes | 9,179 |
| Gate | `check_always_on_token_budget.py` → **exit 0** |

Windsurf legacy `always_on` (**47,493 B**, 13 files) reported separately — not summed into Tier-1.

---

## Final hook status

| Field | Value |
|-------|-------|
| Strategy | `dispatcher` |
| `afterAgentResponse` | `after_agent_governance_dispatch.py` |
| Post-agent scripts inventoried | 41 |
| Hook-required (matrix) | 17 |
| Gate | `check_ag_hook_wiring.py` → **exit 0** |

---

## Final plan archive status

| Field | Value |
|-------|------:|
| Active top-level plans (excl. README/template) | 10 |
| Archived (W3 cumulative moves) | 490 |
| Archive folder | `.cursor/plans/_archive/2026-05/` |
| Graph baseline orphans | 0 |
| Gate | `check_graph_layer_evidence.py` → **exit 0** |

---

## Final skill hygiene status

| Field | Value |
|-------|------:|
| Skills total | 35 |
| Pass / warn / fail | 31 / 4 / 0 |
| mcp-integration bytes | 3,989 (was 18,264) |
| Section companions | 13 under `mcp-integration/sections/` |
| Gate | `check_skill_description_quality.py` → **exit 0** |

---

## W5 verification commands

| Command | Exit | In-plan? |
|---------|-----:|:--------:|
| `python ops_scripts/ci/check_always_on_token_budget.py` | 0 | yes |
| `python .cursor/scripts/check_cursor_optimized_config.py` | 0 | yes |
| `python ops_scripts/ci/check_skill_description_quality.py` | 0 | yes |
| `python ops_scripts/ci/check_mcp_sync_integrity.py` | 0 | yes |
| `python ops_scripts/ci/check_ag_hook_wiring.py` | 0 | yes |
| `python ops_scripts/ci/check_graph_layer_evidence.py` | 0 | yes |
| `python .cursor/scripts/check_cursor_native_config.py --strict` | 1 | no (pre-existing) |
| `python ops_scripts/ci/run_contract_gates.py` | 1 | no (10C pilot) |

---

## Remaining known failures (out of plan scope)

1. **10C pilot proof-evidence** — `check_10c_pilot_proof_evidence.py` via `run_contract_gates.py` exits **1**; multiple `10C-REQ-*` rows `FAIL` with `status=EVIDENCE_PRESENT` (HEAD drift). Not fixed in W5.
2. **Native config strict** — `check_cursor_native_config.py --strict` exits **1**; legacy `.windsurf` / `Windsurf` tokens remain in rules and hook scripts by design (mirror frozen, not deleted).

---

## Explicit non-claims

- Runtime RAG not touched (`anthropic-rag-gaps-7f3c2a` remains separate).
- `.windsurf/` not deleted.
- `agentic_core` / `apps_rg` product runtime not modified by this plan.
- Full repository health / all contract gates green **not** claimed.
- W4.3 learnings-loop writer deferred.
- Memory MCP writeback left to operator follow-up.
- **Notion:** Plans row `cursor-governance-two-tier-b4e8f2` → **Completed** (2026-05-19); receipt [governance_notion_wave_sync_receipt.json](governance_notion_wave_sync_receipt.json).

---

## Artifact index

| Wave | Artifact |
|------|----------|
| W0–W4 inventory | [governance_tier_inventory.json](governance_tier_inventory.json) |
| W2 | [governance_w2_dedupe_report.json](governance_w2_dedupe_report.json) |
| W3 hooks | [governance_w3_hook_audit_matrix.json](governance_w3_hook_audit_matrix.json) |
| W3 archive | [governance_w3_plan_archive_manifest.json](governance_w3_plan_archive_manifest.json) |
| W3R | [governance_w3_remediation_receipt.json](governance_w3_remediation_receipt.json) |
| W4 | [governance_w4_skill_hygiene_report.json](governance_w4_skill_hygiene_report.json) |
| W5 | This file + [manifest](governance_two_tier_closeout_manifest.json) |
| Plan SSOT | [cursor-governance-two-tier-b4e8f2.md](../../.cursor/plans/cursor-governance-two-tier-b4e8f2.md) |
