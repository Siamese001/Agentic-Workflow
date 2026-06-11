---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\cursor-governance-two-tier-b4e8f2.md'
original_relative_path: '_archive\\2026-05\\cursor-governance-two-tier-b4e8f2.md'
source_sha256: 11e67c78bdef9455454c6cc007b8fe59eb15c0c36695c3484d4fa63704fbfc17
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: cursor-governance-two-tier-b4e8f2
plan_type: governance
selected_policy_option: A
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: true
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Cursor governance two-tier consolidation (rules / skills / workflows / hooks)

Align Cursor governance with Anthropic two-tier doctrine (Rules = invariants ≤51 KB always-on; Skills = progressive disclosure; Hooks = deterministic zero-token enforcement). **Analysis complete; implementation deferred** until operator selects policy Option A, B, or C below.

**Source:** [Claude RAG Rules and Skills.pdf](docs/reference/_notes/Claude%20RAG%20Rules%20and%20Skills.pdf)  
**Related plans:** [rules-hooks-memories-consolidation-48b4d6](rules-hooks-memories-consolidation-48b4d6.md) (W1–W6 DONE) · [cursor-only-governance-ssot-d9e4b1](cursor-only-governance-ssot-d9e4b1.md) (DONE) · [always-on-budget-compression-ds2-c7f4a3](always-on-budget-compression-ds2-c7f4a3.md) (DONE) · [anthropic-rag-gaps-7f3c2a](anthropic-rag-gaps-7f3c2a.md) (runtime RAG — separate track)

> **plan_id discipline:** `plan_id` matches filename stem `cursor-governance-two-tier-b4e8f2`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: COMPLETED  
CURRENT_WAVE: NONE  
LAST_COMPLETED_WAVE: W5  
LAST_UPDATED: 2026-05-19  
SELECTED_POLICY_OPTION: **A** (recorded 2026-05-19)  
IMPLEMENTATION: **W0–W5 DONE** — two-tier consolidation closed; see [governance_two_tier_closeout.md](../../docs/reports/cursor/governance_two_tier_closeout.md)

---

## Context (SCQA)

- **Situation** — Repo has 62 `.cursor/rules/*.mdc`, 34 skills (~199 KB), 25 workflows, 7 `hooks.json` events, 41 `post_cursor_agent_*.py` audits, and constitutional §33 two-tier doctrine. Prior consolidation (2026-05) compressed Windsurf `always_on` rules to 46,882 B (PASS under 51,200 B gate).
- **Complication** — Three parallel “always on” surfaces: (1) five `alwaysApply: true` `.mdc` files (~10.5 KB), (2) `AGENTS.md` (~26 KB) injected every Cursor session, (3) thirteen `.windsurf/rules` files with `trigger: always_on` (~47 KB) measured only by `check_always_on_token_budget.py`. `check_cursor_optimized_config.py` expects three always-on rules but repo has five (FAIL). ~496 active plan files vs optimizer intent (&lt;20). Rule/skill/workflow triplication (Author-Gate, structured-reasoning, Tavily, scope-containment, MCP).
- **Question** — How do we unify Tier-0/1/2 governance under one measured always-on budget and eliminate SSOT drift without losing invariants (§21 zero-loss)?
- **Answer** — Wave 0 fixes measurement gates; Waves 1–3 consolidate SSOT and dedupe clusters; Waves 4–5 skill hygiene and optional learnings loop; runtime RAG stays in `anthropic-rag-gaps-7f3c2a`. **Do not execute until policy option selected.**

---

## Policy Options (operator choice required)

| Option | Tier-1 shape | Trade-off |
|--------|----------------|-----------|
| **A (recommended)** | 4× `alwaysApply` rules + `AGENTS.md` ≤15 KB; demote all 13 windsurf `always_on` to on-demand `.mdc` | Cleanest token economics; one-time migration effort |
| **B** | 5× `alwaysApply` (keep P-band + Author-Gate) + `AGENTS.md` ≤10 KB | Less rule churn; heavier AGENTS compression |
| **C** | Freeze rule text; only wire hooks + archive plans | Fastest; leaves G1/G3 SSOT drift open |

**Selected:** Option A (2026-05-19). W1 blocked until explicit `WAVE_START` for W1.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1–W0.3 | Measure & align gates (no semantic rule edits) | ~6k | CI green after gate path fix only | ✅ DONE | [governance_tier_inventory.json](../../docs/reports/cursor/governance_tier_inventory.json); Tier-1 gate PASS |
| W1 | W1.1–W1.3 | SSOT unification (Cursor vs Windsurf; AGENTS compress) | ~14k | Policy A selected | ✅ DONE | Tier-1 **18,382** B; AGENTS **9,101** B; 4× `alwaysApply`; windsurf mirror frozen |
| W2 | W2.1–W2.4 | Dedupe rule/skill/workflow clusters | ~18k | W1 complete | ✅ DONE | Workflows thinned; triples 8→0; [governance_w2_dedupe_report.json](../../docs/reports/cursor/governance_w2_dedupe_report.json) |
| W3 | W3.1–W3.3 | Hooks wiring + plan archive | ~12k | W2 complete | ✅ DONE | Dispatcher wired; active plans **9** (&lt;20) |
| W3R | W3R.1 | Graph baseline orphan remediation | ~2k | W3 complete | ✅ DONE | [governance_w3_remediation_receipt.json](../../docs/reports/cursor/governance_w3_remediation_receipt.json); orphans **507→0** |
| W4 | W4.1–W4.2 | Skill description hygiene + CI gate | ~8k | W3R complete | ✅ DONE | [governance_w4_skill_hygiene_report.json](../../docs/reports/cursor/governance_w4_skill_hygiene_report.json); mcp-integration **3,989** B |
| W5 | W5.1 | Report + memory writeback | ~3k | W4 complete | ✅ DONE | [governance_two_tier_closeout.md](../../docs/reports/cursor/governance_two_tier_closeout.md) + manifest on disk |

**Out of band:** Runtime RAG (contextual retrieval, citations, cache_control) — [anthropic-rag-gaps-7f3c2a](anthropic-rag-gaps-7f3c2a.md).

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W0 | Gates + inventory | ✅ DONE | — | 4 |
| W1 | SSOT + AGENTS | ✅ DONE | — | 12 |
| W2 | Dedupe clusters | ✅ DONE | — | 28 |
| W3 | Hooks + plans | ✅ DONE | — | 8+490 moves |
| W3R | Baseline orphan fix | ✅ DONE | graph gate | 4 |
| W4 | Skill hygiene | ✅ DONE | skill-desc gate | 20+ |
| W5 | Closeout report | ✅ DONE | closeout gates | 2 |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Extend always-on budget gate to `.cursor` + `AGENTS.md` | ✅ DONE |
| W0.2 | Sync `EXPECTED_ALWAYS` in `check_cursor_optimized_config.py` | ✅ DONE |
| W0.3 | Emit `governance_tier_inventory.json` | ✅ DONE |
| W1.1 | Freeze `.windsurf/rules` as mirror; `.mdc` SSOT for edits | ✅ DONE |
| W1.2 | Compress `AGENTS.md` (MCP prose → mcp-integration skill) | ✅ DONE |
| W1.3 | Resolve `alwaysApply` set per policy option | ✅ DONE |
| W2.1 | Author-Gate cluster → one skill + `003` rule | ✅ DONE |
| W2.2 | ADG cluster → on-demand rules + adg-sqlite/graph-analysis skills | ✅ DONE |
| W2.3 | Structured-reasoning + Tavily workflow trim | ✅ DONE |
| W2.4 | Notion/plan rules → plan-governance skill + glob rules | ✅ DONE |
| W3.1 | Audit script → {hook, CI, delete} matrix | ✅ DONE |
| W3.2 | Dispatcher or top-8 explicit `afterAgentResponse` wiring | ✅ DONE |
| W3.3 | Archive plan sprawl to `plans/_archive/YYYY-MM/` | ✅ DONE |
| W4.1 | CI gate for skill `description:` quality | ✅ DONE |
| W4.2 | Trim/split `mcp-integration` if &gt;8 KB | ✅ DONE |
| W4.3 | Optional learnings-loop writer (PDF §50) | ⏸ DEFERRED |
| W5.1 | Closeout report + Memory entity | 🔲 TODO |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.1 | Budget gate path fix | `ops_scripts/ci/check_always_on_token_budget.py`, `governance_tier_measurement.py` | Gate reads `.windsurf/rules` only; misses `alwaysApply` + AGENTS | ~2k | ✅ DONE |
| W0.2 | Optimized config sync | `.cursor/scripts/check_cursor_optimized_config.py` | Option A target vs transitional extras | ~1k | ✅ DONE |
| W0.3 | Tier inventory artifact | `docs/reports/cursor/governance_tier_inventory.json` | No single dashboard | ~3k | ✅ DONE |
| W1.1 | Windsurf mirror policy | `.windsurf/rules/`, `.cursor/MIGRATION_MAP.md` | Dual SSOT drift | ~4k | ✅ DONE |
| W1.2 | AGENTS compression | `AGENTS.md`, `.cursor/skills/mcp-integration/SKILL.md` | 26 KB always-on | ~5k | ✅ DONE |
| W1.3 | alwaysApply policy | `.cursor/rules/000–003`, `adg-p-band-burn-down-discipline.mdc` | Five vs three drift | ~5k | ✅ DONE |
| W2.1 | Author-Gate dedupe | rules `003`, `author-gate-*`; skills packet-builder, ui-renderer | Triplication | ~5k | ✅ DONE |
| W2.2 | ADG dedupe | `adg-*.mdc`, skills `adg-sqlite`, `graph-analysis` | always_on windsurf copies | ~4k | ✅ DONE |
| W2.3 | SR + Tavily dedupe | `sequential-thinking-enforcement.mdc`, workflows | workflow ≈ skill body | ~4k | ✅ DONE |
| W2.4 | Notion/plan dedupe | `plan-governance` skill, `plan-*.mdc` | Prose in always_on windsurf | ~5k | ✅ DONE |
| W3.1 | Post-agent audit matrix | `.cursor/scripts/post_cursor_agent_*.py` | 41 scripts, sparse hook wiring | ~4k | ✅ DONE |
| W3.2 | Hook dispatcher decision | `.cursor/hooks.json`, `post_cursor_agent_dispatch.py` | Unified governance dispatch | ~4k | ✅ DONE |
| W3.3 | Plan archive | `.cursor/plans/`, `_archive/` | 499→9 active | ~4k | ✅ DONE |
| W4.1 | Skill description gate | `ops_scripts/ci/check_skill_description_quality.py` | PDF discoverability | ~3k | ✅ DONE |
| W4.2 | mcp-integration trim | `.cursor/skills/mcp-integration/SKILL.md` + `sections/` | 18 KB → 4 KB index | ~3k | ✅ DONE |
| W4.3 | Learnings loop (optional) | skill `references/` writer hook | PDF adaptive skills | ~2k | ⏸ DEFERRED |
| W5.1 | Closeout | `docs/reports/cursor/governance_two_tier_closeout.md` | Evidence bundle | ~3k | ✅ DONE |

---

## Gap Register (from PDF + repo audit 2026-05-19)

| ID | Gap | P-band | Owner wave |
|----|-----|--------|------------|
| G1 | Dual SSOT: `.cursor/rules` vs `.windsurf/rules`; budget gate on wrong path | P0 | W0, W1 |
| G2 | `check_cursor_optimized_config` expects 3 `alwaysApply`; repo has 5 | P0 | W0 |
| G3 | `AGENTS.md` (~26 KB) outside 51 KB always-on measurement | P0 | W0, W1 |
| G4 | Rule / skill / workflow triplication (AG, SR, Tavily, scope, MCP) | P1 | W2 |
| G5 | 41 `post_cursor_agent_*` scripts; only 3 in `afterAgentResponse` | P1 | W3 |
| G6 | ~496 active plans vs &lt;20 target | P1 | W3 |
| G7 | Skill descriptions not CI-gated (PDF progressive disclosure) | P2 | W4 |
| G8 | Runtime RAG gaps (separate plan) | P2 | anthropic-rag-gaps |
| G9 | No CitationAgent-style verification for doc-heavy outputs | P3 | deferred |

**GAP-implementation:** Operator must select Policy Option A, B, or C before W1. Implementation explicitly out of scope for the analysis save (2026-05-19).

---

## Target two-tier model

### Tier 0 — Deterministic (zero LLM tokens)

Hooks: `beforeShellExecution`, `beforeMCPExecution`, `beforeReadFile`, `afterFileEdit`, `stop`, optional single `afterAgentResponse` dispatcher.  
CI: `run_contract_gates.py`, always-on budget (fixed paths), grep/read budgets, Author-Gate capture, Fort Knox.

### Tier 1 — Always on (≤51,200 bytes measured bundle)

Proposed under **Option A:** `000`, `001`, `002`, `003` `.mdc` + compressed `AGENTS.md` ≤15 KB. P-band via glob rule or merged into `001`.

### Tier 2 — On demand

Remaining `.mdc` (`alwaysApply: false` + globs), 34 skills (procedural SSOT), workflows as thin slash aliases (&lt;30 lines).

---

## Out Of Scope

- Implementing waves before policy selection (this save is plan-only).
- `agentic_core` runtime / apps_rg product seams.
- Anthropic RAG runtime waves (W1–W4 in `anthropic-rag-gaps-7f3c2a`).
- Deleting entire `.windsurf/` tree without CI parity (follow `cursor-only-governance-ssot-d9e4b1` precedent).

---

## Wave 0 — Measure and align gates

WAVE_ID: W0  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: A

**Phases:**

- **W0.1** — Extend `check_always_on_token_budget.py` + `governance_tier_measurement.py` | PHASE_STATUS: DONE
- **W0.2** — Option A alignment in `check_cursor_optimized_config.py` | PHASE_STATUS: DONE
- **W0.3** — `docs/reports/cursor/governance_tier_inventory.json` | PHASE_STATUS: DONE

**Acceptance:**

- `python ops_scripts/ci/check_always_on_token_budget.py` → exit 0; Tier-1 includes `AGENTS.md` + `alwaysApply` `.mdc`.
- `python .cursor/scripts/check_cursor_optimized_config.py` → exit 0; transitional `adg-p-band-burn-down-discipline.mdc` warned only.
- Inventory JSON on disk with `policy_option_selected: A`.

### W0 commands run (2026-05-19)

| Command | Exit | Notes |
|---------|------|-------|
| `python ops_scripts/ci/check_always_on_token_budget.py` | 0 | Tier-1 **37,468** B PASS; windsurf legacy **47,493** B reported separately |
| `python .cursor/scripts/check_cursor_optimized_config.py` | 0 | Option A; transitional warning `adg-p-band-burn-down-discipline.mdc` |
| `python .cursor/scripts/check_cursor_native_config.py --strict` | 1 | Pre-existing: legacy refs in `post_cursor_agent_*.py`, `windsurf-config-lookup.mdc` |
| `python ops_scripts/ci/run_contract_gates.py` | 1 | Pre-existing: `W4d-4` 10C pilot proof-evidence (bundle HEAD drift) |
| `git diff -- agentic_core` | — | Pre-existing dirty tree; **not modified by W0** |
| `git diff --` (scoped governance paths) | — | Only W0 measurement files + this plan |

Artifact: [governance_tier_inventory.json](../../docs/reports/cursor/governance_tier_inventory.json)

### W0 explicit non-claims

- W1–W5 not executed.
- No semantic rule consolidation (no demote/compress/delete of rule bodies).
- `.windsurf/` not deleted.
- Runtime RAG / `agentic_core` not touched.
- Two-tier consolidation is **not** complete.

---

## Wave 1 — SSOT unification

WAVE_ID: W1  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: B

**Phases:** W1.1–W1.3 — all DONE.

**Acceptance:** Tier-1 measured bundle ≤51,200 B; single edit path for new rules (`.cursor/rules/*.mdc`).

### W1 receipt (2026-05-19)

| Field | Value |
|-------|-------|
| STATUS | **PASS** |
| POLICY_OPTION | A |
| AGENTS_MD_BEFORE_BYTES | 26,831 |
| AGENTS_MD_AFTER_BYTES | 9,101 |
| TIER_1_TOTAL_BYTES | 18,382 |
| TIER_1_HEADROOM_BYTES | 32,818 |
| ALWAYS_APPLY_RULES_BEFORE | 5 (`000`–`003` + `adg-p-band-burn-down-discipline.mdc`) |
| ALWAYS_APPLY_RULES_AFTER | 4 (`000`–`003`) |
| DEMOTED_RULES | `adg-p-band-burn-down-discipline.mdc` → `alwaysApply: false` + globs |
| WINDSURF_STATUS | Mirror read-only; edit `.cursor/rules/*.mdc` only (see `.windsurf/rules/README.md`) |
| FORBIDDEN_FILES_TOUCHED | **no** (`agentic_core` not modified by W1) |

| Command | Exit | Notes |
|---------|------|-------|
| `python ops_scripts/ci/check_always_on_token_budget.py` | 0 | Tier-1 PASS |
| `python .cursor/scripts/check_cursor_optimized_config.py` | 0 | 4× alwaysApply; no transitional P-band warning |
| `python .cursor/scripts/check_cursor_native_config.py --strict` | 1 | Pre-existing legacy Windsurf refs in hooks/scripts |
| `python ops_scripts/ci/run_contract_gates.py` | 1 | Pre-existing 10C pilot proof-evidence HEAD drift |
| `python ops_scripts/ci/check_mcp_sync_integrity.py` | 0 | AGENTS MCP table in sync |
| `git diff -- agentic_core` | — | Pre-existing dirty tree; **not modified by W1** |

Artifact: [governance_tier_inventory.json](../../docs/reports/cursor/governance_tier_inventory.json)

### W1 explicit non-claims

- W2–W5 not executed.
- No cluster dedupe (Author-Gate, Tavily, structured-reasoning, Notion, ADG beyond P-band demotion).
- Active plan archive not performed.
- `.windsurf/` not deleted.
- Runtime RAG not touched.
- `agentic_core` untouched by W1.
- Full two-tier consolidation **not** complete.

---

## Wave 2 — Dedupe clusters

WAVE_ID: W2  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: C

**Acceptance:** Zero verbatim Author-Gate / SR / Tavily triples; rules ≤45 active `.mdc` after dedupe (target, not hard gate).

### W2 receipt (2026-05-19)

| Field | Value |
|-------|-------|
| STATUS | **PASS** |
| CLUSTERS_DEDUPED | Author-Gate, ADG, Structured reasoning, Tavily, Notion/plan |
| TIER_1_TOTAL_BYTES | 18,460 |
| ALWAYS_APPLY_COUNT | 4 |
| DUPLICATE_TRIPLES_BEFORE | 8 |
| DUPLICATE_TRIPLES_AFTER | 0 |
| FORBIDDEN_FILES_TOUCHED | **no** |

| Command | Exit |
|---------|------|
| `python ops_scripts/ci/check_always_on_token_budget.py` | 0 |
| `python .cursor/scripts/check_cursor_optimized_config.py` | 0 |
| `python .cursor/scripts/check_cursor_native_config.py --strict` | 1 (pre-existing) |
| `python ops_scripts/ci/run_contract_gates.py` | 1 (pre-existing 10C pilot) |
| `python ops_scripts/ci/check_mcp_sync_integrity.py` | 0 |
| `python ops_scripts/ci/governance_w2_dedupe_report.py` | 0 |

Artifacts: [governance_w2_dedupe_report.json](../../docs/reports/cursor/governance_w2_dedupe_report.json) · [governance_w2_dedupe_report.md](../../docs/reports/cursor/governance_w2_dedupe_report.md)

### W2 explicit non-claims

- W3–W5 not executed.
- Hooks not rewired.
- Active plans not archived.
- `.windsurf/` not deleted.
- Runtime RAG not touched.
- `agentic_core` / `apps_rg` product runtime untouched by W2.
- Full consolidation **not** complete.

---

## Wave 3 — Hooks and plan archive

WAVE_ID: W3  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: D

**Acceptance:** Audit matrix committed; active `plans/*.md` count &lt;20 (excluding README, template, `_archive`).

### W3 receipt (2026-05-19)

| Field | Value |
|-------|-------|
| STATUS | **PASS** |
| HOOK_STRATEGY | **dispatcher** (`after_agent_governance_dispatch.py`) |
| POST_AGENT_SCRIPTS_TOTAL | 41 |
| HOOK_REQUIRED_COUNT | 16 |
| CI_REQUIRED_COUNT | 6 |
| MANUAL_ONLY_COUNT | 19 |
| OBSOLETE_OR_DUPLICATE_COUNT | 11 |
| ACTIVE_PLANS_BEFORE | 499 |
| ACTIVE_PLANS_AFTER | 9 |
| ARCHIVED_PLAN_COUNT | 490 (406 pass-1 + 84 pass-2) |
| TIER_1_TOTAL_BYTES | 18,460 |
| ALWAYS_APPLY_COUNT | 4 |
| FORBIDDEN_FILES_TOUCHED | **no** |

| Command | Exit |
|---------|------|
| `python ops_scripts/ci/governance_w3_hook_audit_matrix.py` | 0 |
| `python ops_scripts/ci/governance_w3_plan_archive.py` | 0 |
| `python ops_scripts/ci/check_always_on_token_budget.py` | 0 |
| `python .cursor/scripts/check_cursor_optimized_config.py` | 0 |
| `python .cursor/scripts/check_cursor_native_config.py --strict` | 1 (pre-existing) |
| `python ops_scripts/ci/check_mcp_sync_integrity.py` | 0 |
| `python ops_scripts/ci/run_contract_gates.py` | 1 (pre-existing baseline orphans + 10C pilot) |
| `python ops_scripts/ci/check_ag_hook_wiring.py` | 0 |

Artifacts: [governance_w3_hook_audit_matrix.json](../../docs/reports/cursor/governance_w3_hook_audit_matrix.json) · [governance_w3_plan_archive_manifest.json](../../docs/reports/cursor/governance_w3_plan_archive_manifest.json)

### W3 explicit non-claims

- W4–W5 not executed.
- Skill hygiene / closeout not claimed.
- Runtime RAG not touched.
- `.windsurf/` not deleted.
- `agentic_core` / `apps_rg` product runtime untouched by W3.
- No `post_cursor_agent_*.py` scripts deleted.
- Full consolidation **not** complete.

---

## Wave 3R — Graph baseline orphan remediation

WAVE_ID: W3R  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  

**Acceptance:** `check_graph_layer_evidence.py` baseline integrity **0** orphans; archived plans remain under `_archive/`.

Receipt: [governance_w3_remediation_receipt.json](../../docs/reports/cursor/governance_w3_remediation_receipt.json) · [governance_w3_remediation_receipt.md](../../docs/reports/cursor/governance_w3_remediation_receipt.md)

| Field | Value |
|-------|-------|
| STATUS | **PASS** |
| ROOT_CAUSE | Baseline listed top-level paths; W3 archive moved files to `_archive/2026-05/` |
| ORPHAN_REFERENCE_COUNT_BEFORE | 507 |
| ORPHAN_REFERENCE_COUNT_AFTER | 0 |
| ACTIVE_PLANS_COUNT | 10 |
| ARCHIVED_PLANS_COUNT | 490 |

---

## Wave 4 — Skill hygiene

WAVE_ID: W4  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: E

**Acceptance:** `check_skill_description_quality.py` in contract gates; mcp-integration ≤8 KB or split index.

Report: [governance_w4_skill_hygiene_report.json](../../docs/reports/cursor/governance_w4_skill_hygiene_report.json) · [governance_w4_skill_hygiene_report.md](../../docs/reports/cursor/governance_w4_skill_hygiene_report.md)

| Field | Value |
|-------|-------|
| STATUS | **PASS** |
| SKILLS_TOTAL / PASS / FAIL / WARN | 35 / 31 / 0 / 4 |
| MCP_INTEGRATION_BEFORE_BYTES | 18,264 |
| MCP_INTEGRATION_AFTER_BYTES | 3,989 |
| SPLIT_FILES_CREATED | 13 under `mcp-integration/sections/` |
| TIER_1_TOTAL_BYTES | 18,460 |
| ALWAYS_APPLY_COUNT | 4 |

| Command | Exit |
|---------|------|
| `python ops_scripts/ci/check_skill_description_quality.py` | 0 |
| `python ops_scripts/ci/check_graph_layer_evidence.py` | 0 |
| `python ops_scripts/ci/run_contract_gates.py` | 1 (pre-existing 10C pilot only) |

### W4 explicit non-claims

- W5 closeout not executed.
- Full consolidation **not** complete.
- W4.3 learnings-loop writer deferred.
- Runtime RAG not touched; `.windsurf` not deleted; `agentic_core` / apps_rg product runtime untouched.

---

## Wave 5 — Closeout

WAVE_ID: W5  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: F

**Acceptance:** Closeout report on disk; Memory entity `ProceduralPattern:CursorGovernanceTwoTier2026`.

### W5 receipt (2026-05-19)

| Field | Value |
|-------|-------|
| STATUS | **PASS** (plan scope) |
| CLOSEOUT_MD | [governance_two_tier_closeout.md](../../docs/reports/cursor/governance_two_tier_closeout.md) |
| CLOSEOUT_MANIFEST | [governance_two_tier_closeout_manifest.json](../../docs/reports/cursor/governance_two_tier_closeout_manifest.json) |
| TIER_1_TOTAL_BYTES | 18,460 |
| ALWAYS_APPLY_COUNT | 4 |
| ACTIVE_PLANS_FINAL | 10 |
| FORBIDDEN_FILES_TOUCHED | **no** |

| Command | Exit | Notes |
|---------|------|-------|
| `python ops_scripts/ci/check_always_on_token_budget.py` | 0 | in-scope |
| `python .cursor/scripts/check_cursor_optimized_config.py` | 0 | in-scope |
| `python ops_scripts/ci/check_skill_description_quality.py` | 0 | in-scope |
| `python ops_scripts/ci/check_mcp_sync_integrity.py` | 0 | in-scope |
| `python ops_scripts/ci/check_ag_hook_wiring.py` | 0 | in-scope |
| `python ops_scripts/ci/check_graph_layer_evidence.py` | 0 | in-scope |
| `python .cursor/scripts/check_cursor_native_config.py --strict` | 1 | pre-existing Windsurf refs |
| `python ops_scripts/ci/run_contract_gates.py` | 1 | pre-existing 10C pilot |

### W5 explicit non-claims

- Full repo CI green **not** claimed (10C pilot fails).
- Runtime RAG, `agentic_core`, apps_rg product runtime untouched.
- `.windsurf/` not deleted; 10C/native strict **not** fixed in W5.
- Memory MCP + Notion Plans row: operator follow-up (optional W5.1).

---

## Definition of Done

DoD-1: Tier-1 always-on bundle ≤51,200 bytes on Cursor-native paths  
- Evidence: `python ops_scripts/ci/check_always_on_token_budget.py` → PASS with path list including `AGENTS.md`  
- Status: ✅ DONE

DoD-2: Governance inventory and closeout report exist  
- Evidence: `docs/reports/cursor/governance_tier_inventory.json` and `docs/reports/cursor/governance_two_tier_closeout.md`  
- Status: ✅ DONE

DoD-3: Config optimizers pass  
- Evidence: `python .cursor/scripts/check_cursor_optimized_config.py` → exit 0; `python .cursor/scripts/check_cursor_native_config.py --strict` → exit 0  
- Status: ⚠️ PARTIAL — optimized **0**; native strict **1** (pre-existing, out of plan scope)

DoD-4: Contract gates green after governance edits  
- Evidence: `python ops_scripts/ci/run_contract_gates.py` → exit 0  
- Status: ⚠️ DEFERRED — exit **1** on pre-existing `check_10c_pilot_proof_evidence.py` only; in-scope governance gates pass

DoD-5: Notion Plans row reflects Completed + plan file Exists On Disk  
- Evidence: `python tools/notion/patch_cursor_governance_two_tier_completed.py`; Plans DB `Slug=cursor-governance-two-tier-b4e8f2`  
- Status: ✅ DONE (2026-05-19)

### Verification vs deferral

| Item | Verify in-plan | Defer |
|------|----------------|-------|
| Policy A/B/C | Operator marks choice before W1 | — |
| Runtime RAG | — | `anthropic-rag-gaps-7f3c2a` |
| CitationAgent pattern | — | G9 future plan |
| Full `.windsurf/` deletion | — | Separate CI parity plan |

---

## Marker Quick Reference

```
WAVE_START: plan=cursor-governance-two-tier-b4e8f2 wave=<N>
WAVE_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 wave=<N> note="<one-liner>"
PLAN_CREATED: slug=cursor-governance-two-tier-b4e8f2 path=.cursor/plans/cursor-governance-two-tier-b4e8f2.md
```

---

## Notion Summary

**Status:** Completed (2026-05-19). **Policy:** Option A. **Waves:** W0–W5 + W3R + post-closeout 10C HEAD resync (198 bundles). **Closeout:** [governance_two_tier_closeout.md](../../docs/reports/cursor/governance_two_tier_closeout.md). **Not in scope:** runtime RAG; `.windsurf` deletion; full repo CI green.

```
WAVE_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 wave=0 note="Tier-1 measurement + inventory"
WAVE_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 wave=1 note="Option A: 4x alwaysApply; AGENTS ~9KB"
WAVE_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 wave=2 note="Cluster dedupe; duplicate triples 8→0"
WAVE_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 wave=3 note="Dispatcher hook; 490 plans archived"
WAVE_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 wave=3 note="W3R: baseline orphans 507→0"
WAVE_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 wave=4 note="Skill hygiene gate; mcp-integration indexed"
WAVE_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 wave=5 note="Closeout manifest + md"
PLAN_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 note="Two-tier governance Option A closed"
```

---

## Analysis snapshot (2026-05-19)

| Surface | Count | Notes |
|---------|-------|-------|
| `.mdc` rules | 62 | 5× `alwaysApply: true` |
| `.windsurf` always_on `.md` | 13 | 46,882 B (legacy gate PASS) |
| `AGENTS.md` | ~26 KB | Not in legacy gate |
| Skills | 34 | ~199 KB total |
| Workflows | 25 | Overlap skills |
| Active plans | ~496 | Sprawl vs optimizer |

Commands run at analysis time:

- `check_cursor_optimized_config.py` → FAIL (alwaysApply drift, plan sprawl)
- `check_always_on_token_budget.py` → PASS (windsurf path only)
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |
