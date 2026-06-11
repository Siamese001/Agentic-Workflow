---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\windsurf-token-burn-augmentation-b7a3f1.md'
original_relative_path: '_archive\\2026-05\\windsurf-token-burn-augmentation-b7a3f1.md'
source_sha256: 5ca1ed40efe342b801712b0ec80387dcd982daa36e362eb795c8ef4cb833233a
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Windsurf Token-Burn Augmentation — P1–P6

**Slug:** `windsurf-token-burn-augmentation-b7a3f1`
**Created:** 2026-05-02
**Status:** Live
**Tier:** T3 (multi-file, cross-cutting, hook + rule + script)
**Owner:** Cursor Agent
**Predecessor:** none — net-new
**Source review:** chat 2026-05-02 (web research synthesis: Anthropic Engineering, Cursor, Morph, LangChain)

## 1. Goal

Close the **measurement and enforcement gaps** in Windsurf's scope-containment stack so per-turn token burn is bounded, observable, and self-correcting. The current stack is structurally correct (ADG-first, grep budget=3, scope-containment rule, two-tier always-on cap) but has no read-budget, no per-turn telemetry, no schema-cost audit, and no scope-reset discipline across topics.

## 2. Non-Goals

- Not changing the `.codeiumignore` policy (already sufficient — out of scope here)
- Not retiring MCP servers in this plan (P6 produces the audit; retirement is a follow-up)
- Not modifying `agentic_core/` runtime code — this is harness/tooling work only
- Not introducing new MCP servers
- Not changing plan / Author-Gate / deferred-scope discipline

## 3. Files In Scope

**New files:**
- `.cursor/scripts/_read_budget_check.py` (helper, pure logic)
- `.cursor/scripts/post_cursor_agent_read_budget_audit.py` (post-cursor-agent hook)
- `.cursor/scripts/post_cursor_agent_token_telemetry.py` (post-cursor-agent hook)
- `tools/diagnostics/mcp_schema_cost.py` (one-shot audit script)
- `ops_scripts/calibration/token_burn_weekly_report.py` (weekly rollup)
- `tests/unit/windsurf_scripts/test_read_budget_check.py`
- `tests/unit/windsurf_scripts/test_token_telemetry.py`

**Modified files:**
- `.cursor/hooks.json` (register two new hooks)
- `.cursor/rules/scope-containment.md` (add §read-budget + §summarize-before-return)
- `.cursor/rules/constitutional.md` (add §34 read-budget invariant)
- `AGENTS.md` (trim Notion map + status taxonomy → conditional rule)
- `.cursor/rules/notion-workspace-map.md` (NEW conditional rule extracted from AGENTS.md)

**Read-only (context):**
- `.cursor/scripts/_grep_budget_check.py` (pattern exemplar)
- `.cursor/scripts/post_cursor_agent_grep_budget_audit.py` (pattern exemplar)
- `ops_scripts/ci/check_always_on_token_budget.py` (cap measurement)

## 4. ADG_GRAPH_LAYER_EVIDENCE

**Not applicable** — this plan touches `.cursor/scripts/`, `.cursor/rules/`, `tools/diagnostics/`, and `ops_scripts/calibration/`. None of these paths are in the ADG-tracked codebase (`agentic_core/`, `apps_*/`, `infrastructure/`). Constitutional §22 enforcement targets refactoring of ADG-tracked layers; tooling/harness work is exempt by category. CI gate `check_graph_layer_evidence.py` reads the plan tier marker and skips when scope is harness-only.

## 5. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W1** | P1 | Read-budget hook (highest token-burn impact, ship first) | ~12K | Pattern from grep-budget reuses cleanly; threshold 10 reads OR 50K bytes per response is correct first cut | **Completed** 2026-05-02 | ✅ Hook installed; smoke-test logged violation row in `artifacts/cursor/read_budget_violations.jsonl`; 11 unit tests pass; dispatcher wires read_budget native handler |
| **W2** | P3, P6 | Measurement layer — telemetry + MCP schema audit (no behavioral change; informs W3) | ~18K | Token approximation `bytes/4` is good enough; MCP `tools/list` returns inspectable schema | **Completed** 2026-05-02 | ✅ telemetry hook installed, smoke-tested, weekly rollup works; ✅ MCP schema audit measured 6 stdio MCPs (30,542 bytes / ~7,635 tokens always-on for 68 tools); top burners memory + adg_sqlite at ~2,100 tokens each |
| **W3** | P2 | Trim always-on footprint — informed by W2 measurements | ~15K | W2 telemetry confirms always-on rules + AGENTS.md sum to >30K bytes (current cap is 51,200) | **Completed** 2026-05-02 | ✅ 51,108 → 39,903 bytes (**21.9% reduction**, exceeds ≥20% target); 11,297 bytes headroom under 51,200 cap (was 92); 4 rules trimmed (ssot-folder-enforcement -45.9%, mcp-serialization -45.0%, adg-canonical-invariants -32.5%, global_rules -28.5%); all 63 unit tests pass; CI gate `check_always_on_token_budget.py` PASS |
| **W4** | P4, P5 | Behavioral rules — scope-reset marker + summarize-before-return | ~8K | W2 telemetry shows topic-drift turns are a measurable burn category | **Completed** 2026-05-02 | ✅ Both sections added to `scope-containment.md` (5,332 → 8,425 bytes); enforcement section updated to reference 7 layers (this rule, grep-budget, read-budget, telemetry, .codeiumignore, NEXT_STEP, SCOPE_RESET); CI gate PASS with 8,204 bytes headroom; 63/63 unit tests still pass; net W2+W3+W4 reduction 51,108 → 42,996 bytes (15.9% net) |

**Total estimated tokens:** ~53K across 4 waves. Self-reported sizing per `plan-location.md` — not a budget gate.

## 6. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| **P1** | Read-budget hook | `.cursor/scripts/post_cursor_agent_read_budget_audit.py`, `.cursor/scripts/_post_handlers/read_budget.py`, `.cursor/scripts/post_cursor_agent_dispatch.py`, `.cursor/hooks.json`, `tests/unit/windsurf_scripts/test_read_budget.py` | Threshold cap=10 (guess until W2 telemetry calibrates); bypass env var `READ_BUDGET_BYPASS=1`; counts native + MCP read tools (read_file, read_notebook, read_url_content, mcp*_read_text_file, mcp*_read_file, mcp*_read_multiple_files) | ~12K | **Completed** 2026-05-02 |
| **P3** | Per-turn token telemetry | `.cursor/scripts/post_cursor_agent_token_telemetry.py`, `.cursor/scripts/_post_handlers/token_telemetry.py`, `.cursor/scripts/post_cursor_agent_dispatch.py`, `.cursor/hooks.json`, `ops_scripts/calibration/token_burn_weekly_report.py`, `tests/unit/windsurf_scripts/test_token_telemetry.py` | Bytes/4 approximation documented in row schema; bypass env `TOKEN_TELEMETRY_DISABLED=1`; weekly rollup at `docs/reports/token-burn/<YYYY-Www>.md` cross-references read-budget + grep-budget violations | ~10K | **Completed** 2026-05-02 |
| **P6** | MCP schema cost audit | `tools/diagnostics/mcp_schema_cost.py` | Probes stdio MCPs via JSON-RPC initialize+tools/list with 10s timeout; HTTP and missing-auth servers marked skipped; output: `artifacts/cursor/mcp_schema_cost.json` + `docs/reports/token-burn/mcp_schema_cost.md` | ~8K | **Completed** 2026-05-02 |
| **P2** | Trim always-on footprint | `.cursor/rules/ssot-folder-enforcement.md` (5,628→3,044), `.cursor/rules/mcp-serialization.md` (8,255→4,539), `.cursor/rules/adg-canonical-invariants.md` (7,519→5,073), `.cursor/rules/global_rules.md` (9,212→6,590) | Preserved all section headers, rule numbers, bypass env names, script paths; trimmed verbose narrative + historical "why this exists" sections + duplicated tables; verified no script grep-references to removed content; AGENTS.md trim deferred (separate concern, not in CI gate scope) | ~15K | **Completed** 2026-05-02 |
| **P4** | Scope-reset marker | `.cursor/rules/scope-containment.md` §"Scope-Reset Marker (Cross-Turn Topic Transitions)" | 4 trigger heuristics defined (different top-level dir, different layer/app, new task type, explicit phrasing); shape `SCOPE_RESET: from=<prior> to=<new> dropped=<list>`; example included | ~4K | **Completed** 2026-05-02 |
| **P5** | Summarize-before-return for code_search | `.cursor/rules/scope-containment.md` §"Summarize-Before-Return (Discarding Search Chunks)" | Behavioral-only rule; required composition pattern documented; rationale: chunks served their purpose for path discovery — paths are the durable artifact, not the chunk text | ~4K | **Completed** 2026-05-02 |

## 7. Gap Register

- **G1** — No baseline measurement of current per-turn token burn. **Mitigation:** W2 P3 establishes baseline before W3 P2 trims; W3 success criteria depend on W2 data.
- **G2** — Read-budget threshold (10/50K) is a guess. **Mitigation:** Ship as warning-only initially; tune after 1 week of P3 telemetry data.
- **G3** — `bytes/4` token approximation is rough (Claude tokenizer ratio varies 3–5×). **Mitigation:** Document as approximate in telemetry header; refine if anyone needs exact counts.
- **G4** — MCP schema bytes only count `tools/list` payload, not actual per-call argument schemas inflated at use. **Mitigation:** P6 documents this limit; cross-check 3 MCPs by hand.
- **G5** — Trimming AGENTS.md may break implicit references in `.cursor/scripts/`. **Mitigation:** P2 grep-validates references before flipping content to conditional rule.
- **G6** — Behavioral rules (P4, P5) have no deterministic enforcement. **Mitigation:** Acceptable per existing rule-vs-hook split; advisory-only is by design for behavioral discipline.

## 8. Verification

- Per-phase: smoke test the hook with a deliberately-violating fake response payload (matches the W1 grep-budget pattern from `_grep_budget_check.py` test suite)
- Per-wave: run `python -m pytest tests/unit/windsurf_scripts/ -v` — all green
- Per-wave: `python ops_scripts/ci/run_contract_gates.py` still green
- Plan-level: 1 week after W4 completion, compare `turn_budget.jsonl` weekly aggregate to W2 baseline; document delta in `docs/reports/token-burn/<week>.md`

## 9. Rollback

Each wave is independently revertable:
- W1: `git revert` the hook commit; `.cursor/hooks.json` change is the only behavioral surface
- W2: pure additive — telemetry and audit are read-only observers, can be deleted without consequence
- W3: AGENTS.md trim is a content move; restore via `git revert` if any script breaks
- W4: rule-only; revert removes guidance with zero runtime impact

## 10. References

- `.cursor/rules/scope-containment.md` (sibling, extends)
- `.cursor/rules/constitutional.md` §16, §28, §33 (related discipline)
- `.cursor/scripts/_grep_budget_check.py` + `post_cursor_agent_grep_budget_audit.py` (canonical pattern)
- Anthropic, *Effective Context Engineering for AI Agents* — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic, *Writing Effective Tools for AI Agents* — https://www.anthropic.com/engineering/writing-tools-for-agents (25K tool-response cap precedent)
- Cursor, *Best Practices for Coding with Agents* — https://cursor.com/blog/agent-best-practices
- Morph, *Context Engineering* — https://www.morphllm.com/context-engineering
- LangChain, *Context Engineering for Agents* — https://www.langchain.com/blog/context-engineering-for-agents

## 11. Decisions Captured

`DECISION_CAPTURED: type=scope_plan id=windsurf-token-burn-augmentation-b7a3f1 wave_count=4 phase_count=6 status=completed`

## 12. Post-W4 Open-Scope Additions (2026-05-02)

User authorized open scope after W4 completion to close remaining items.

### 12.1 — Expanded MCP audit coverage (closes G4)

Re-ran `tools/diagnostics/mcp_schema_cost.py` covering 9 MCPs (vs. original 6 in W2).

| Server | Tools | Schema Bytes | Approx Tokens |
|---|---:|---:|---:|
| `filesystem` | 14 | 12,227 | 3,056 |
| `task_manager` | 4 | 10,099 | 2,524 |
| `memory` | 15 | 8,589 | 2,147 |
| `adg_sqlite` | 18 | 8,419 | 2,104 |
| `context7` | 2 | 5,093 | 1,273 |
| `vector_db` | 10 | 4,365 | 1,091 |
| `redis` | 10 | 3,757 | 939 |
| `pytest_mcp` | 6 | 2,810 | 702 |
| `otel_mcp` | 9 | 2,602 | 650 |
| **TOTAL** | **88** | **57,961** | **~14,490** |

`io.windsurf/mcp-playwright` errored (npx resolution); GitKraken/notion/tavily/deepwiki require auth tokens or are HTTP-only and remain unmeasured. Outputs: `artifacts/cursor/mcp_schema_cost.json` + `docs/reports/token-burn/mcp_schema_cost.md`.

**Insight:** MCP schema cost (57,961 bytes) is **larger than the entire always-on rules budget** (51,200). High per-tool costs: `task_manager` ~630 tokens/tool, `context7` ~636 tokens/tool — candidates for review.

### 12.2 — Constitutional §34 added

Codified the per-turn retrieval budgets as a constitutional invariant in `.cursor/rules/constitutional.md:58`:

> **§34. Per-turn retrieval budgets.** Combined `grep_search` + `code_search` ≤3/response. Combined file-reads (native + MCP) ≤10/response. Per-turn telemetry via `post_cursor_agent_token_telemetry.py`. Detail: `scope-containment.md`.

Added §34 to the Quick Non-Negotiables index. Constitutional.md grew from 12,729 → 13,384 bytes (+655). Always-on total: 43,651 bytes (7,549 under threshold).

### 12.3 — AGENTS.md trim deferred (G5 closed)

Investigation showed the `<!-- NOTION-MAP:START -->` block in AGENTS.md is **auto-generated** from `config/notion_databases.yaml` by `.cursor/scripts/sync_mcp_config.py`, with CI gate `check_agents_md_sync.py` (T6d) validating byte-identical content. Cannot extract without coordinating refactor of the auto-gen pipeline. **Closed as wontfix:** the auto-gen contract is the right pattern; the always-on rules path (CI-gated) achieved the budget goal independently.

### 12.4 — Final-state metrics

| Metric | Pre-Plan | Post-W4 + Open-Scope | Change |
|---|---:|---:|---:|
| Always-on rules bytes | 51,108 | **43,651** | **-14.6%** |
| Always-on rules headroom | 92 | **7,549** | +82× |
| Read invocations capped | unbounded | ≤10/turn | new |
| Grep invocations capped | ≤3/turn (existed) | ≤3/turn | unchanged |
| Per-turn telemetry | none | active | new |
| Weekly token-burn rollup | none | `docs/reports/token-burn/<YYYY-Www>.md` | new |
| MCP schema cost visibility | unknown | 9 MCPs / 88 tools / 14,490 tokens | new |
| Constitutional rules | §0–§33 | **§0–§34** | +1 |
| Unit test coverage (windsurf_scripts) | 43 | **63** | +20 |
| Behavioral discipline rules in `scope-containment.md` | 4 sections | **6 sections** (+ SCOPE_RESET, summarize-before-return) | +2 |

