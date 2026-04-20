# Windsurf Rules and Skills — Master Index

**Last Updated**: 2026-04-20 (added `adg-p7-analyst-artifacts.md` for pre-computed refactoring evidence)
**Purpose**: Zero-loss two-tier operating system for this repo. Keep the global layer thin, route specialized work to skills and workflows, preserve strict repo evidence discipline.

> **SSOT**: Windsurf discovers rules directly from `.windsurf/rules/*.md` (one file per rule). Skills are entry-file-based: each `.windsurf/skills/<name>/SKILL.md` is authoritative. No preprocessor.

---

## Operating Model

The old failure mode was not too little guidance — it was too much guidance loaded at once.

This repo uses a **two-tier model**:

1. **Always-on constitutional floor**
   - tiny set of rules that are always true
   - authority boundaries, tool routing guardrails, safety/scope/validation rules

2. **Load-on-demand skills and workflows**
   - only load deep procedure when the task matches
   - each skill has a sharp purpose, negative boundary, and output contract
   - workflows exist for repeatable operational loops

## Design Principles

- Keep the global prompt lean.
- Preserve strict repo evidence over guesswork.
- Separate **analyze**, **plan**, **edit**, and **verify** modes.
- Use ADG for structural dependency questions.
- Use MCPs by capability, not by habit.
- Stop only for genuine ambiguity, risk, or approval gates.
- Validate before claiming completion.

---



## Always-On Files

| File | Role |
|---|---|
| `.windsurf/rules/constitutional.md` | Non-negotiable constitutional floor; section numbers referenced by hooks/scripts |
| `.windsurf/rules/global_rules.md` | Thin operating kernel for tool use, scope, and validation |
| `.windsurf/rules/hitl-enforcement.md` | Compact continuous-execution and HITL core |
| `.windsurf/rules/plan-location.md` | SSOT plan location and overwrite rules |
| `.windsurf/rules/query-progress-bar.md` | Long-running operation progress contract |
| `.windsurf/rules/adg-canonical-invariants.md` | ADG doctrinal floor — SSOT hierarchy, 5 Surfaces, 4 Antipatterns, 4 Archetypes, Zero-Loss Propagation Pipeline |

## On-Demand Rule Files

| File | Use When |
|---|---|
| `adg-hotspot-enforcement.md` | T2/T3 refactoring, anti-pattern burndown, wave scope selection — violations + centrality MUST drive target order |
| `adg-p7-analyst-artifacts.md` | T2/T3 refactoring, blast radius, centrality, test scope — per-run P7 JSON artifacts are PRIMARY source before live MCP |
| `adg-repair-discipline.md` | ADG break/fix, graph-first debugging, repair loops |
| `adg-test-accelerator-enforcement.md` | Working in `tools/adg/**` or `test_*_adg.py` |
| `agents-memory-lifecycle.md` | Session start/end and persistent memory decisions |
| `anti-pattern-hitl-gate.md` | A change may require a guardian exception |
| `approval-exception-policy.md` | Evaluating whether an exception is even eligible |
| `hitl-decision-points.md` | Need to build a proper HITL packet |
| `hitl-svp-calibration.md` | Need to rank options and recommend one |
| `mcp-config-ssot.md` | Editing `.windsurf/mcp_config.json` |
| `mcp-pytest-enforcement.md` | MCP tests, `conftest.py`, or pytest execution discipline |
| `memory-management.md` | Memory graph hygiene, purges, sync, write thresholds |
| `refactor-decision-memory.md` | Refactor-class HITL requires historical precedent check |
| `security-hardening.md` | Secrets, auth, external service credentials, env handling |
| `sequential-thinking-enforcement.md` | T2/T3 work needs structured reasoning packet |
| `windsurf-config-lookup.md` | Question is about Windsurf config, docs, hooks, rules, skills, workflows |

## Skill Catalog

| Skill | Primary Use | Do Not Use When |
|---|---|---|
| `artifact-management` | Plans, reports, evidence, progress display, path validation | Core code reasoning or architecture decisions |
| `boundary-enforcement` | Imports, layer sovereignty, shims, relocation discipline | Non-code writing or business analysis |
| `graph-analysis` | Structural dependency analysis, blast radius, ADG-first routing | Pure literal text search or non-code lookup |
| `operational-gates` | Preflight, rollback, gate evidence, recovery | Feature design without execution risk |
| `refactor-decision-memory` | Pull precedent before refactor-class HITL | Routine edits with no meaningful design choice |
| `structured-reasoning` | T2/T3 task framing, decomposition, failure packets, verification | T0/T1 trivial work |
| `testing-framework` | Scoped validation strategy, skip discipline, collection integrity | Work that does not touch code or tests |

## Workflow Catalog

| Workflow | Use When |
|---|---|
| `adg-redis-refresh.md` | Redis cache is cold, stale, or after full ADG regen |
| `adg-repair-loop.md` | Running a scoped cluster repair loop |
| `adg-test-triage-gate.md` | Evaluating `_adg.py` deletion/archive decisions |
| `adg-timeout-recovery.md` | ADG or long-running analysis timed out |
| `agent-deletion-gate.md` | Production agent/module deletion is proposed |
| `antipattern-hitl-gate.md` | Guardian exception or anti-pattern gate triggered |
| `hitl-decision-gate.md` | Need a HITL packet with options |
| `mcp-failure-rca.md` | MCP appears broken, unhealthy, or never invoked |
| `memory-purge-sync.md` | Cleaning stale memory entities or syncing memory state |
| `progress-display-enforcement.md` | Long operation needs progress instrumentation |
| `refresh-windsurf-docs.md` | Local Windsurf docs mirror refresh |
| `structured-reasoning.md` | Need the structured packet flow in one place |
| `timeout-progress-enforcement.md` | Timeout risk plus long-running progress obligations |

## Routing Order

Use this order whenever a task is non-trivial:

1. Read `constitutional.md` and `global_rules.md`
2. Classify mode: analyze / plan / edit / verify
3. Pick the one most relevant skill
4. Pull the supporting checklist/template file if needed
5. Pull a workflow only if the task is repeatable or operationally stateful
6. Validate before declaring done

## Quick Start Matrix

| Task Pattern | First File |
|---|---|
| "Why did this break?" / blast radius / imports / consumers | `skills/graph-analysis/SKILL.md` |
| "Which files to refactor first?" / wave queue / hotspot rank / anti-pattern priority | `rules/adg-hotspot-enforcement.md` + `rules/adg-p7-analyst-artifacts.md` (P7 accelerator ships the ranked queue pre-computed) |
| "Blast radius / top-N centrality / seams / burndown?" | `rules/adg-p7-analyst-artifacts.md` → `adg_structural_outputs_<ts>.json` |
| "GraphDB structural queries (layer purity, UWG bypass, spine completeness)?" | `rules/adg-p7-analyst-artifacts.md` → `adg_graphdb_queries_<ts>.json` |
| "Runtime handoff / cross-cutting witness tier satisfaction?" | `rules/adg-p7-analyst-artifacts.md` → `adg_runtime_spine_<ts>.json` |
| "Fix this ADG issue" | `rules/adg-repair-discipline.md` |
| "Should we stop for HITL?" | `rules/hitl-enforcement.md` then `rules/hitl-decision-points.md` |
| "Need a plan" | `rules/sequential-thinking-enforcement.md` + `templates/execution-plan-template.md` |
| "Where should this artifact go?" | `skills/artifact-management/SKILL.md` |
| "Can we add this exception?" | `rules/approval-exception-policy.md` + `rules/anti-pattern-hitl-gate.md` |
| "Which tests should I run?" | `skills/testing-framework/SKILL.md` |
| "Why is this MCP not being used?" | `workflows/mcp-failure-rca.md` |
| "How do Windsurf rules/hooks/config work?" | `rules/windsurf-config-lookup.md` |

## Authoring Rules for Future Updates

- Prefer adding detail to a skill or workflow, not the always-on files.
- One file, one job.
- Put trigger language in the first three lines.
- Every skill should answer: what it does, when to use it, when NOT to use it, required evidence, output contract, stop conditions.
- Preserve constitutional section numbers already referenced by scripts.

---

## Skills & Enforcement Gates (CI Mapping)

| # | Skill | Layer | Timing | Type | CI Gate | Pre-commit Hook |
|---|-------|-------|--------|------|---------|----------------|
| 1 | **graph-analysis** | Windsurf | Before work | Behavioural + Structural | None | None |
| 2 | **boundary-enforcement** | Pre-commit | After work | Structural | ADG GV edges | T2a, T4a |
| 3 | **operational-gates** | Both | Before work | Behavioural + Structural | `check_rollback_checkpoints.py` | T3a-rollback |
| 4 | **testing-framework** | Pre-commit | After work | Structural | `adg_ci_lane_gate.py` | T3a-skip |
| 5 | **artifact-management** | Pre-commit | After work | Structural | `validate_report_location.py` | T3b |
| 6 | **structured-reasoning** | Windsurf | Before work | Behavioural | None (behavioral) | None |
| 7 | **refactor-decision-memory** | Windsurf | On demand | Behavioural | None (behavioral) | None |

**Key**: Layer = Windsurf (AI-time) / Pre-commit (commit-time) / Both. Timing = Before work (process) / After work (structural) / During work (runtime).

---

## Pre-Commit Hook Mapping

### Tier 0-ADG: ADG Phase Gate
- **Hook ID**: `adg-phase-gate`
- **Script**: `tools/adg_ci_gate.py check-phase`
- **Stage**: manual (reverted from automatic — repair phase state is session context)
- **Purpose**: Block full-suite pytest during PHASE 5-6 repair loops
- **Always Run**: Yes (when manually invoked)

### Tier 0: Normalization
- **Hooks**: trailing-whitespace, end-of-file-fixer, mixed-line-ending, check-merge-conflict
- **Purpose**: Deterministic whitespace normalization

### Tier 1: Syntax Gate
- **Hook ID**: `python-syntax-check`
- **Script**: `python -m py_compile`
- **Purpose**: Fast-fail on broken syntax

### Tier 2: Auto-Fixers
- **Hook ID**: `ruff`, `ruff-format`
- **Purpose**: Lint and format before analysis

### Tier 3a: Analysis & Guards
- **Hook ID**: `check-anti-patterns`
- **Script**: `ops_scripts/ci/check_anti_patterns.py`
- **Purpose**: Landmine detection (silent swallowers, magic config, etc.)

- **Hook ID**: `check-dedup-violations` ✅ NEW
- **Script**: `ops_scripts/ci/check_dedup_violations.py`
- **Purpose**: Prevent duplicate symbols

- **Hook ID**: `check-script-sprawl` ✅ NEW
- **Script**: `ops_scripts/ci/check_script_sprawl.py`
- **Purpose**: Block new runner scripts

- **Hook ID**: `check-shim-discipline` ✅ NEW
- **Script**: `ops_scripts/ci/check_shim_discipline.py`
- **Purpose**: Enforce shim/backward-compatibility discipline

- **Hook ID**: `check-rollback-checkpoints` ✅ NEW
- **Script**: `ops_scripts/ci/check_rollback_checkpoints.py`
- **Purpose**: Validate rollback gates for multi-file phases

- **Hook ID**: `enforce-unit-strict-zero-skip`
- **Script**: `tools/adg_ci_lane_gate.py --lane unit_strict --fail-on-skip`
- **Purpose**: Block pytest.skip in UNIT_STRICT

- **Hook ID**: `check-c0-sovereignty`
- **Script**: `agentic_core/L0_routing/scripts/run_guardian_c0_sovereignty.py`
- **Purpose**: Embedding boundary enforcement

### Tier 3b: Structural Checks
- **Hook ID**: `check-report-location`
- **Script**: `ops_scripts/hooks/validate_report_location.py`
- **Purpose**: SSOT plan location enforcement

### Tier 3c-3i: Additional Guards
- **Hook IDs**: reject-generated-artifacts-tracked, folder-purity-validation, module-collision-guard, governance-policy-validation, validate-evidence-contract, guard-pytest-ini-scope, guard-apps-shared-instructional-layer
- **Purpose**: Architectural and policy enforcement

### Tier 4a: Import Validation
- **Hook ID**: `import-dependency-check`
- **Script**: `ops_scripts/ci/validate_import_dependencies.py`
- **Purpose**: Validate all imports resolve

### Tier 5: Cleanup
- **Hook ID**: `purge-cache`
- **Script**: `ops_scripts/maintenance/purge_cache.py`
- **Purpose**: Final __pycache__ cleanup

---

## CI Scripts Inventory (41 total)

### Active CI Gates
1. `check_adg_proof_artifact_truthfulness.py`
2. `check_adg_schema_field_names.py`
3. `check_agent_registry_completeness.py`
4. `check_anti_patterns.py` ✅
5. `check_apps_output_contract.py`
6. `check_c0_boundary.py`
7. `check_ci_integrity.py` ✅ UPDATED (added cond. 8b: broken_test_fix semantic equivalence)
8. `check_dedup_violations.py` ✅ UPDATED (proxy check only)
10. `check_determinism_replay.py`
11. `check_determinism_violations.py`
12. `check_direct_execute_calls.py`
13. `check_directory_deletion_sweep.py`
14. `check_embedding_instantiation.py`
15. `check_environment_contract.py`
16. `check_evidence_contract_v2.py`
17. `check_faiss_persist_contract.py`
18. `check_healer_direct_model.py`
19. `check_kernel_extension_boundary.py`
20. `check_layer_write_sovereignty.py`
21. `check_llm_sdk_imports.py`
22. `check_model_string_literals.py`
23. `check_no_unconditional_xfail.py` ✅ NOW WIRED (§11.4)
24. `check_object_dunder_setattr.py`
25. `check_plan_location_compliance.py` ✅
26. `check_policy_drift_classification.py`
27. `check_powershell_ban.py` ✅ NOW WIRED (§2)
28. `check_rollback_checkpoints.py` ✅ NEW
29. `check_script_sprawl.py` ✅ NEW
30. `check_shim_discipline.py` ✅ NEW
31. `check_skip_convergence_gate.py`
32. `check_sovereign_llm_gateway.py`
33. `check_spine_adapter_contract.py`
34. `check_spine_bypass.py`
35. `check_structured_output_emission.py`
36. `check_system_learning_boundary.py`
37. `check_test_integrity.py` ✅ NOW WIRED (§11/§13)
38. `check_tooling_apps_boundary.py`
39. `check_utility_silent_swallowers.py` ✅ NOW WIRED (§10/§11)
40. `check_wall_clock_in_determinism.py`
41. `validate_import_dependencies.py` ✅
42. `check_query_progress_bar.py` ✅ NEW


---

## Conditional Rules (model_decision & glob triggers)

All `model_decision` and `glob` rules require a `description` field in frontmatter for Cascade trigger mapping.

| Rule File | Trigger | Description |
|---|---|---|
| `adg-hotspot-enforcement.md` | `model_decision` | Before any refactoring or wave planning — run violations snapshot + fan-in rank; hotspot report must drive scope |
| `adg-repair-discipline.md` | `model_decision` | Use when diagnosing ADG failures or running the ADG repair loop |
| `anti-pattern-hitl-gate.md` | `model_decision` | Use before introducing any new anti-pattern instance |
| `memory-management.md` | `model_decision` | Use when reading/writing the persistent memory graph |
| `security-hardening.md` | `model_decision` | Use when handling credentials, env vars, secrets, or external auth |
| `windsurf-config-lookup.md` | `model_decision` | Use for Windsurf IDE configuration, rules, hooks, MCP, skills, workflows |
| `hitl-decision-points.md` | `model_decision` | Use when a HITL decision point is reached — full trigger patterns, option shape, scoring guidance |
| `sequential-thinking-enforcement.md` | `model_decision` | Use when a T2/T3 task requires structured reasoning before execution |
| `adg-test-accelerator-enforcement.md` | `glob` | Fires on ADG test files and tools — enforces adg_test_accelerator.py usage |
| `mcp-config-ssot.md` | `glob` | Fires on edits to `.windsurf/mcp_config.json` |
| `mcp-pytest-enforcement.md` | `glob` | Fires on edits to `test_*.py` and `conftest.py` |
| `refactor-decision-memory.md` | `model_decision` | Before opening HITL for any refactor-class decision, consult the refactor-decision-memory skill for historical precedent |
| `agents-memory-lifecycle.md` | `model_decision` | Apply when reading/writing the persistent memory knowledge graph, or deciding memory MCP boundaries |

---

## VSCodium Extensions Policy Pack

Repo-local standards for VSCodium extension and marketplace decisions. Not a Windsurf rule file — a standards doc set consulted by Windsurf prompts.

| Artifact | Path | Purpose |
|---|---|---|
| Source notes | `docs/external/vscodium/` (4 files) | Primary-source facts from VSCodium upstream docs (retrieval date: 2026-04-11) |
| Policy | `docs/standards/windsurf/windsurf_vscodium_extensions_policy.md` | Operational repo standard: approved/blocked sources, replacements, fallback paths, Copilot (PROVISIONAL) |
| Decision log | `docs/standards/windsurf/windsurf_vscodium_decision_log.md` | Durable decision entries D001–D011 with FINAL/PROVISIONAL status |
| Prompt pack | `docs/standards/windsurf/windsurf_vscodium_prompt_pack.md` | 6 reusable prompt templates for marketplace, compatibility, Copilot, config validation work |

**Provisional sections:** GitHub Copilot (D010) and non-MS third-party compatibility (D011) — see decision log for unblock conditions.

---

## Quick Reference

### Adding a New Rule
1. Create skill in `.windsurf/skills/<skill-name>/`
2. Create CI gate in `ops_scripts/ci/check_<rule>.py`
3. Add pre-commit hook to `.pre-commit-config.yaml`
4. Update this index
5. Test with: `pre-commit run <hook-id> --all-files`

### Testing a Gate
```bash
# Test specific gate
pre-commit run check-dedup-violations --all-files

# Test all gates
pre-commit run --all-files

# Skip gates for emergency commit
git commit --no-verify -m "..."
```

### Bypassing a Gate (Justified)
Include justification keywords in commit message:
- Dedup: "dedup", "no duplicate", "searched for", "DEDUP_SEARCH: decision=create"
- Script Sprawl: "script-sprawl", "CI gate", "canonical invocation"
- Shim: "shim-discipline", "backward-compatibility"
- Rollback: "checkpoint", "rollback", "phase checkpoint"

---

## Maintenance

**Review Frequency**: Monthly
**Owner**: Platform Team
**Last Audit**: 2026-04-15
**Next Audit**: 2026-05-09

**Changelog**:
- 2026-04-11: **VSCODIUM EXTENSIONS POLICY PACK** — New standards doc set at `docs/standards/windsurf/` and `docs/external/vscodium/`. Four upstream source notes created (retrieval date 2026-04-11). Policy file (`windsurf_vscodium_extensions_policy.md`) covers approved/blocked galleries, 8 blocked extensions, 5 approved replacements, proprietary debugger policy, alternate gallery config, Copilot (PROVISIONAL), and fallback paths. Decision log (`windsurf_vscodium_decision_log.md`) records D001–D011 (9 FINAL, 2 PROVISIONAL). Prompt pack (`windsurf_vscodium_prompt_pack.md`) provides 6 reusable templates. Discoverable from this index under §VSCodium Extensions Policy Pack.
- 2026-04-11: **QUERY PROGRESS BAR** — New constitutional rule §16 (`query-progress-bar.md`, always_on). New CI gate `check_query_progress_bar.py` (detects bare long loops ≥10 lines and heavy-named functions ≥12 lines without progress reporting). New pre-commit hook `check-query-progress-bar` on staged Python files. 38 unit tests added (`tests/ci/test_check_query_progress_bar.py`). `constitutional.md` updated with §16. RULES_INDEX coverage updated: 6 Constitutional Rules, 42 CI Gates, 26+ Pre-commit Hooks.
- 2026-04-19: **ADG HOTSPOT ENFORCEMENT** — New rule `adg-hotspot-enforcement.md` (model_decision). Enforces mandatory hotspot report before any T2/T3 refactoring: `adg_violations` snapshot + `adg_p0_wave_plan` + fan-in rank (impact = violations × (1 + log10(1+fan_in))) + layer multipliers. Plans without `## ADG_HOTSPOT_REPORT` section are invalid. Compact always-on gate added to `global_rules.md` §Hotspot-First Refactoring Gate. RULES_INDEX wired: On-Demand table, Conditional Rules table, Quick Start Matrix.
- 2026-04-19: **REFACTOR DECISION MEMORY** — New rule `refactor-decision-memory.md` (model_decision). New skill `refactor-decision-memory/` with `lookup_refactor_decisions.py`. New hook `post_cascade_hitl_capture.py` wired into `post_cascade_response`. SQLite+FTS5 ledger at `.windsurf/state/refactor_decisions/`. `hitl-enforcement.md` unchanged — memory system sits under the policy layer. 30 unit tests added.
- 2026-04-15: **RULE SIZE REDUCTION** — `constitutional.md` 29K→3.3K (always_on core, 16 constraints + tier table). `hitl-enforcement.md` 33K→2.7K (always_on pipeline + bypass + thresholds). New `hitl-decision-points.md` (model_decision, 10 decision triggers + HITL-10 shape + telemetry). `sequential-thinking-enforcement.md` converted from always_on (6.9K) to model_decision (1.8K). `adg-test-accelerator-enforcement.md` description frontmatter added. `skills/graph-analysis/fail_closed_discipline.md` created. All 7 skill entry files confirmed as `SKILL.md`. Always_on rules: constitutional (3.3K), global_rules (3.0K), hitl-enforcement (2.7K), plan-location (1.9K).
- 2026-04-14: **WINDSURF DOC ALIGNMENT** — All 6 skill entry files renamed `skill.md` → `SKILL.md` (canonical naming). Added `description` frontmatter to 4 `model_decision` rules (`adg-repair-discipline`, `anti-pattern-hitl-gate`, `memory-management`, `security-hardening`) and 2 `glob` rules (`mcp-config-ssot`, `mcp-pytest-enforcement`). New rule: `windsurf-config-lookup.md`. Removed non-standard `file_pattern` fields from `hooks.json`; moved path filtering logic into `post_write_mcp_config_sync.py`. Added 25 support files across all 5 incomplete skill directories (5 per skill). Added `## Windsurf Configuration Docs` block to repo-root `AGENTS.md`. Updated RULES_INDEX: file count 13→14, skills count 5→6, added Conditional Rules table.
- 2026-04-09: **WINDSURF DRIFT CLEANUP** — Deleted `.windsurf/rules/.windsurfrules` (90KB aggregate, not a documented Windsurf rule artifact, preprocessor archived). Deleted `.windsurf/rules/_variables.yaml` (orphaned config for archived preprocessor). Relocated `pytest-optimization.md` from `.windsurf/` root to `docs/` (no activation path at root). Flattened `.windsurf/plans/plans/` and `.windsurf/plans/tasks/` subdirs into `.windsurf/plans/` per plan-location.md SSOT. Archived `_show_diffs.py` to `tools/archive/`. Updated RULES_INDEX.md: removed dead preprocessor workflow, corrected file count (9→13), fixed `.windsurfrules` status claim. All 7 `SKILL.md` files: moved non-standard frontmatter fields (`enforcement_layer`, `enforcement_timing`, `enforcement_type`) into `metadata:` block per Agent Skills spec.
- 2026-04-08: **POWERSHELL-BAN CI GATE FIXED** — Root cause: `check_powershell_ban.py` had 20 over-broad regex patterns (`$var`, `|pipe|`, `if(){`) generating 7,244 false-positive violations per commit, overflowing Windsurf context and causing internal error `170ba0ebe0fc4955bb7b3ae6ada485f7`. Fix: replaced with 17 precise `\bVerb-Noun\b` patterns scoped to unambiguous PS cmdlets only. Also fixed `pre_run_gate.py` which blocked running the checker itself (substring match on script filename containing "powershell"). Now 0 violations. Committed: `8c1719c99a`.
- 2026-04-08: **MCP ROSTER CLEANUP + GLOBAL CONFIG FIXES** — Deleted 5 redundant/broken MCP servers (Playwright, Figma, Brave Search, Fetch, GitHub MCP) dropping ~50 tools. Fixed Redis MCP env vars from bash `${VAR:-default}` syntax (broken on Windows) to literal values. Removed `disabledTools: [read_file]` from filesystem MCP. Removed web allowlist restriction (all sites now accessible). Added turbo allow/deny lists and global `files.exclude` patterns.
- 2026-04-07: **SEQUENTIAL THINKING MCP RETIRED** — Permanently removed Sequential Thinking MCP from active roster. Root causes: stdio fragility on Windows, zombie node.exe processes, opaque tool surface, no reliable timeout, architectural mismatch. Replacement: native Cascade reasoning + compositional MCP pattern. New artifacts: `.windsurf/workflows/structured-reasoning.md`, `.windsurf/skills/structured-reasoning/SKILL.md` (+ checklist, plan-template, verification-template, failure-template), `docs/mcp/sequential-thinking-replacement.md`. Updated `mcp-failure-rca.md` STEP 6 to tombstone. Updated RULES_INDEX skills table with skill #6.
- 2026-04-04: **RCA FIX — WAVE/MICRO-WAVE PLAN MODEL NOT AUTO-EMPLOYED** — Root cause: §10 was reactive (validated existing plans) with no proactive trigger at plan-creation time; micro-wave discipline (≤15 modules/wave) was never codified in any rule file; template wave table columns mismatched §10.1 spec. Fix: Added Constitutional Rule #13 to `.windsurfrules` floor + §10.0 "Plan Creation Protocol" pre-draft trigger section (fires before any content is drafted) + same rule (#11) to `.windsurfrules.consolidated` + §10 section appended to consolidated file + template updated to §10.1 column spec with micro-wave sub-table example + RULES_INDEX updated with §10.0 entry.
- 2026-04-03: **SKILLS CONSOLIDATION** — Archived 30 individual skills to `tools/archive/.windsurf/skills/`. Consolidated into 5 canonical skills per SVP Engineering principle: `graph-analysis` (replaces dependency-graph-analysis, scope-guard, dedup-guard), `boundary-enforcement` (replaces layer-boundary-guard, import-hygiene, shim-discipline), `operational-gates` (replaces rollback-gate, mcp-tool-verify), `testing-framework` (replaces test-rigor-enforcement, pytest-integrity), `artifact-management` (replaces evidence-bundle, ssot-write-gate, progress-display). Updated Skills table to show 5 consolidated skills. Coverage remains 100%.
- 2026-03-25: **PROGRESS DISPLAY ENFORCEMENT** — Added `progress-display` skill with mandatory colored progress bars and percentage displays for all operations >5s. Updated §5.3 with detailed progress reporting requirements including ANSI color codes, ETA display, and standardized progress bar formats. Skill provides terminal protocol, color scheme reference, and implementation guide for integration across all Windsurf operations.
- 2026-03-14: **HITL (HUMAN-IN-THE-LOOP) ENFORCEMENT** — Added §8.5 HITL Framework to `.windsurfrules` and Constitutional Rule #8. Created comprehensive rule (`.windsurf/rules/hitl-enforcement.md`) with 10 mandatory decision triggers. Created workflow (`/hitl-decision-gate`) with option presentation templates. HITL required for: architecture decisions, refactoring scope, anti-patterns, test repair, dependencies, deletions, config changes, error handling, performance trade-offs, ADG timing. Registered as constitutional rule with Windsurf-only enforcement (behavioral, no CI gate).
- 2026-03-12: **TEST FAILURE TRIAGE PROTOCOL** — Added canonical 5-check decision tree (`docs/technical/TEST_FAILURE_decision_tree.md`). Registered as §2.5 constitutional rule. Added CI condition 8b (`check_broken_test_fix_semantic_equivalence`) to `check_ci_integrity.py`. Updated `adg-repair-discipline.md` with triage step before repair loop. Updated `test-rigor-enforcement` skill with triage trigger. Reference added to `.windsurfrules` §2.5 without duplicating taxonomy.
- 2026-03-11: **RULES CONSOLIDATION** — `.windsurfrules` reduced 3906→~400 lines. Removed all Python code blocks (redundant with `ops_scripts/ci/`). Added Constitutional Floor banner to top. Wired 4 previously dormant CI gates into `run_contract_gates.py`: `check_powershell_ban`, `check_test_integrity`, `check_no_unconditional_xfail`, `check_utility_silent_swallowers`.
- 2026-03-11: Initial index creation, added 5 new CI gates
- 2026-03-11: **ARCHITECTURE REDESIGN** — Removed misfits from pre-commit, strengthened Windsurf skills
  - Deleted `check_ast_first_gate.py` (misplaced — process rule, not structural)
  - Reverted `adg-phase-gate` to manual stage (repair phase state is session context)
  - Added MANDATORY PRE-CONDITION blocks to 5 Windsurf skills (ast-first, scope, rollback, dedup, adg-repair)
  - Tightened dedup and rollback CI gates to proxy/artifact checks only
  - Added `enforcement_layer` metadata to all skills
  - Created `docs/rules/enforcement_architecture.md` canonical contract
  - Updated RULES_INDEX.md with Layer, Timing, Type columns

## Claude Alignment Map

This index follows the Claude split described in the briefing:

- **Rules**: always-on invariants, routing cues, compact standards, and non-negotiable boundaries.
- **Skills**: heavy reusable procedures, checklists, templates, and domain execution playbooks loaded only when relevant.
- **Scripts / Hooks**: deterministic fail-closed enforcement, audit capture, and compact machine-readable signals.
- **Templates / Workflows**: staged execution artifacts that preserve context budget by keeping multi-step process detail out of always-on rules.

### Retrieval and Context Hygiene

- Prefer **local-first** retrieval for repo and config work.
- Prefer **exact / structural** lookup before broader semantic expansion.
- For high-risk synthesis, require **evidence extraction before summarization**.
- Keep long reference material fragmented and scoped; avoid monolithic always-on context.
