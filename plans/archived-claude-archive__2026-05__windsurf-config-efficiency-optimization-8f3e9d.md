---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\windsurf-config-efficiency-optimization-8f3e9d.md'
original_relative_path: '_archive\\2026-05\\windsurf-config-efficiency-optimization-8f3e9d.md'
source_sha256: 6c439a9abe1f49ec587ea505da20880b2c198a1e7cb3deca6c6e350a5bedef00
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Windsurf Config Efficiency Optimization

> **Notion Page**: https://www.notion.so/windsurf-config-efficiency-optimization-8f3e9d-35c27693f55c8103b619e31413ebeebe  
> **Plan Slug**: `windsurf-config-efficiency-optimization-8f3e9d`  
> **Status**: Not Started  
> **Created**: 2026-05-09  

---

## 1. Current State Analysis

### 1.1 Always-On Budget Status

| Metric | Value | % of Threshold |
|--------|-------|----------------|
| **Used** | 47,321 bytes | 92.4% |
| **Threshold** | 51,200 bytes | 100% |
| **Headroom** | 3,879 bytes | 7.6% |
| **Risk Level** | 🔶 HIGH | Near limit |

### 1.2 Always-On Rules Breakdown (Ranked by Size)

| Rank | File | Bytes | % of Budget | Notes |
|------|------|-------|-------------|-------|
| 1 | `constitutional.md` | 11,562 | 24.4% | Constitutional floor — cannot move |
| 2 | `author-gate-enforcement.md` | 9,741 | 20.6% | Recently promoted 2026-05-09; optimizable |
| 3 | `global_rules.md` | 6,590 | 13.9% | Operating kernel — keep always_on |
| 4 | `scope-containment.md` | 5,280 | 11.2% | Procedural bloat → skill candidate |
| 5 | `ssot-folder-enforcement.md` | 3,044 | 6.4% | Recently demoted; keep lean |
| 6 | `plan-location.md` | 2,596 | 5.5% | Compact — keep |
| 7 | `author-gate-queue-drain.md` | 2,584 | 5.5% | Compact invariant — keep |
| 8 | `apps-rg-interactive-discipline.md` | 1,992 | 4.2% | Small app-specific rule |
| 9 | `adg-canonical-invariants.md` | 1,865 | 3.9% | Thin invariant layer |
| 10 | `mcp-serialization.md` | 1,213 | 2.6% | Compact |
| 11 | `notion-plan-wave-deferral.md` | 854 | 1.8% | Tiny |

### 1.3 Hooks Chain Analysis

| Hook Phase | Count | Overhead Assessment |
|------------|-------|---------------------|
| `pre_user_prompt` | 10 | High — runs before every prompt |
| `pre_write_code` | 4 | Moderate — only on writes |
| `pre_mcp_tool_use` | 1 | Low — necessary |
| `pre_run_command` | 1 | Low — necessary |
| `pre_read_code` | 1 | Low — necessary |
| `post_cursor_agent_response` | 25 | **CRITICAL** — 25 hooks fire every response |
| `post_write_code` | 4 | Moderate |
| `post_run_command` | 1 | Low |
| `post_mcp_tool_use` | 1 | Low |
| `post_setup_worktree` | 1 | Low |
| **TOTAL** | **49** | **35 post_cascade hooks = overhead risk** |

### 1.4 Oversized Model_Decision Rules (Skill Candidates)

| File | Bytes | Trigger | Issue |
|------|-------|---------|-------|
| `adg-hotspot-enforcement.md` | 11,714 | `model_decision` | Should be skill (>10KB) |
| `adg-graph-layer-enforcement.md` | 11,519 | `model_decision` | Should be skill (>10KB) |
| `notion-plans-taxonomy.md` | 9,839 | `model_decision` | Near threshold, could be skill |
| `author-gate-decision-points.md` | 8,591 | `model_decision` | Near threshold |
| `intelligence-ledger-family.md` | 7,259 | `model_decision` | Substantial |

---

## 2. Gap Register

### Gap 1: Author-Gate Rule Budget Spike
- **Location**: `.cursor/rules/author-gate-enforcement.md`
- **Size**: 9,741 bytes (20.6% of budget)
- **Gap**: Recently promoted from `model_decision` to `always_on` on 2026-05-09 per plan `always-on-budget-compression-ds2-c7f4a3`. Contains procedural detail (lines 65-75 "Required pipeline", lines 109-123 "Where the procedural detail lives" table) that could be referenced rather than inline.
- **Impact**: Single rule consumes 1/5 of always-on budget

### Gap 2: Scope-Containment Procedural Bloat
- **Location**: `.cursor/rules/scope-containment.md`
- **Size**: 5,280 bytes
- **Gap**: Lines 68-78 "Enforcement" table duplicates hook references. Lines 61-66 "Escape Hatches" detail could move to skill. The "Summarize-Before-Return" behavioral guidance is verbose.
- **Impact**: 11.2% of budget; procedural detail that belongs in skill

### Gap 3: Post-Cursor-Agent Hook Chain Overhead
- **Location**: `.cursor/hooks.json` → `post_cursor_agent_response`
- **Count**: 25 hooks
- **Gap**: Many hooks are audit-only (`show_output=false`) but still consume process spawn overhead on every response. No consolidation layer exists. Hooks like `post_cursor_agent_author_gate_*` (4 hooks) could be merged.
- **Impact**: Latency on every Cursor Agent response

### Gap 4: Model_Decision Rules Approaching Limit
- **Files**: `adg-hotspot-enforcement.md` (11,714 bytes), `adg-graph-layer-enforcement.md` (11,519 bytes)
- **Gap**: Both exceed 10KB threshold for rules. Per constitutional §33, procedural detail should be in skills. These are essentially skills masquerading as rules.
- **Impact**: Risk of context compaction if loaded together with always_on rules

### Gap 5: Redundancy Between ADG Rules
- **Location**: `adg-canonical-invariants.md` + `global_rules.md`
- **Gap**: Both contain ADG-first doctrine:
  - `adg-canonical-invariants.md` §6: "ADG vs Hardcoded String — Query ADG for paths/identifiers"
  - `global_rules.md` §ADG-First Analysis: "Dependency analysis MUST use ADG MCP tools"
- **Impact**: ~500 bytes duplicated; risk of drift between sources

### Gap 6: Pre-User-Prompt Hook Consolidation
- **Location**: `.cursor/hooks.json` → `pre_user_prompt`
- **Count**: 10 hooks
- **Gap**: `pre_user_prompt_author_gate_reminder.py`, `pre_user_prompt_ag_queue_surface.py`, `pre_user_prompt_plan_registration_surface.py` all related to Author-Gate pipeline. Could be unified.
- **Impact**: 3 separate Python process spawns per prompt

---

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W1 | P1 | Trim author-gate rule | ~2,000 | Not Started | Rule <8KB, procedural refs externalized |
| W2 | P1-P2 | Extract scope-containment skill | ~3,000 | Not Started | New skill created, rule <3.5KB |
| W3 | P1-P3 | Audit/consolidate post_cascade hooks | ~2,500 | Not Started | Hook count 25→15, latency measured |
| W4 | P1-P2 | Demote oversized rules to skills | ~4,000 | Not Started | 2 rules converted, model_decision slimmed |
| W5 | P1 | Deduplicate ADG doctrine | ~1,500 | Not Started | Single source of truth, no redundancy |

---

## 4. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Trim author-gate-enforcement.md | 1 rule, 1 skill ref | Promoted rule is 20% of budget | ~2,000 | Not Started |
| W2.P1 | Create scope-containment skill | New skill dir, SKILL.md | Procedural detail extraction | ~1,500 | Not Started |
| W2.P2 | Slim scope-containment rule | 1 rule | Remove extracted detail, add skill refs | ~1,500 | Not Started |
| W3.P1 | Audit post_cascade hook necessity | 1 JSON, 25 scripts | Identify merge candidates | ~800 | Not Started |
| W3.P2 | Merge author-gate audit hooks | 4→1 hook | Unify schema/ui/pipeline/miss audits | ~1,000 | Not Started |
| W3.P3 | Measure hook latency | hooks.json | Baseline before/after latency | ~700 | Not Started |
| W4.P1 | Convert adg-hotspot to skill | 1 rule → skill | Large model_decision rule demotion | ~2,000 | Not Started |
| W4.P2 | Convert adg-graph-layer to skill | 1 rule → skill | Large model_decision rule demotion | ~2,000 | Not Started |
| W5.P1 | Deduplicate ADG-first doctrine | 2 rules | Choose canonical source, cross-ref | ~1,500 | Not Started |

---

## 5. Target Outcomes

### 5.1 Byte Budget Targets

| Optimization | Target Saving | Cumulative |
|--------------|---------------|------------|
| W1: Trim author-gate | -2,000 bytes | 5,879 bytes headroom (11.5%) |
| W2: Scope-containment to skill | -2,000 bytes | 7,879 bytes headroom (15.4%) |
| W3: Hook consolidation (no byte saving) | - | 7,879 bytes headroom |
| W4: Demote oversized rules | -4,000 bytes | 11,879 bytes headroom (23.2%) |
| W5: Deduplicate doctrine | -500 bytes | 12,379 bytes headroom (24.2%) |
| **TOTAL TARGET** | **-8,500 bytes** | **~20% budget headroom** |

### 5.2 Hooks Optimization Target

| Metric | Before | After Target |
|--------|--------|--------------|
| post_cascade hooks | 25 | 15-18 |
| pre_user_prompt hooks | 10 | 7-8 |
| Total hooks | 49 | 35-40 |

### 5.3 Quality Metrics (Non-Regression)

- All existing CI gates must pass (`run_contract_gates.py`)
- `check_always_on_token_budget.py` must show PASS with >15% headroom
- Hook chain must fire successfully (verified via `post_cursor_agent_heartbeat.py`)
- No behavioral change — only structural optimization

---

## 6. Non-Goals

- ❌ Converting `constitutional.md` or `global_rules.md` to skills (must stay always_on per architecture)
- ❌ Reducing always_on rule count below 7 (current is 11; target is 9-10)
- ❌ Converting hooks to non-Python implementations
- ❌ Modifying enforcement behavior (only reducing size/consolidating)
- ❌ Optimizing skills (they are already on-demand; out of scope)

---

## 7. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Hook merge causes missed audit events | Medium | High | Keep individual log files; merge caller only |
| Skill extraction loses behavioral guidance | Low | Medium | Preserve invariants in rule, move procedures to skill |
| Byte savings overestimated | Medium | Low | Measure after each wave; adjust targets |
| Author-Gate rule trim breaks pipeline | Low | High | Keep canonical-emitter invariant; trim peripheral detail only |

---

## 8. References

- **Constitutional §33**: Two-tier compliance (Anthropic) — `trigger: always_on` rules MUST sum ≤51,200 bytes
- **Rule**: `.cursor/rules/constitutional.md` lines 50-52
- **CI Gate**: `ops_scripts/ci/check_always_on_token_budget.py`
- **RULES_INDEX**: `.cursor/RULES_INDEX.md` — two-tier model operating principles
- **Notion Plan**: `windsurf-config-efficiency-optimization-8f3e9d` (this plan)
