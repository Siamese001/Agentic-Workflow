# Five-Tier Governance Enforcement Table

Complete inventory of all enforcement across the five tiers with SSOT owner and duplication analysis.

---

## Tier 1: Windsurf Cascade Hooks (`.windsurf/hooks.json`)

### Pre-Hooks — HARD GATES (can BLOCK, exit 2, FAIL-CLOSED per H-6)

| Hook Event | Gate Script | What It Enforces | Exit Code | Test File |
|------------|------------|-----------------|-----------|----------|
| `pre_run_command` | `pre_run_gate.py` | PowerShell ban (PP-4), dangerous commands | 2 = BLOCK | `test_pre_run_gate.py` |
| `pre_write_code` | `pre_write_gate.py` | Anti-pattern injection (PP-3), syntax errors via edit reconstruction + `ast.parse()` (PP-13), MCP config tiered validation (PP-2) | 2 = BLOCK (or ALLOW/REQUIRE_APPROVAL for MCP config) | `test_pre_write_gate.py` |
| `pre_mcp_tool_use` | `pre_mcp_gate.py` | ADG SQLite lock check (PP-10), ADG health prerequisite (PP-1) | 2 = BLOCK (ADG), 0 = pass (non-ADG) | `test_pre_mcp_gate.py` |

### Pre-Hook — ADVISORY CLASSIFIER (always exit 0, FAIL-OPEN per H-6)

| Hook Event | Script | What It Does | Blocks? | Test File |
|------------|--------|-------------|---------|----------|
| `pre_user_prompt` | `pre_prompt_classifier.py` | Tier classification (T0-T3), context seeding, plan/MCP warnings | **NO** (exit 0 always) | `test_pre_prompt_classifier.py` |

### Post-Hooks — ADVISORY ONLY (never block, exit 0 always, FAIL-OPEN per H-6)

| Hook Event | Audit Script | What It Does | Blocks? | Test File |
|------------|-------------|-------------|---------|----------|
| `post_write_code` | `post_write_audit.py` | MCP JSON-native lint (schema, env vars, tool count, risky edits), write telemetry (PP-2) | **NO** (exit 0) | `test_post_write_audit.py` |
| `post_run_command` | `post_run_audit.py` | Command tracking, best-effort PID registry (PP-9). PID not in native payload. | **NO** (exit 0) | `test_post_run_audit.py` |
| `post_mcp_tool_use` | `post_mcp_audit.py` | MCP tool usage telemetry, response time tracking | **NO** (exit 0) | `test_post_mcp_audit.py` |
| `post_cascade_response` | `post_cascade_cleanup.py` | Response-tail cleanup attempt: best-effort zombie kill (PP-9), ADG lock release (PP-10). Fires per-response, NOT per-session. | **NO** (exit 0) | `test_post_cascade_cleanup.py` |

All scripts in `ops_scripts/hooks/windsurf/`. Paths repo-relative via `working_directory: "."`.

**Hardening**: Zero hardcoded paths. `pathlib.Path(__file__).resolve().parents[N]` for repo root. Risk-based fail policy per H-6: critical pre-hooks fail-closed (exit 2), advisory hooks fail-open (exit 0). Post-hooks: `show_output: false` default.

---

## Tier 2: Windsurf Rules + Skills + Workflows

Behavioral governance in Cascade context window. No blocking — advisory only.

### Rules (13 → 11 after dedup)

| Rule File | Trigger | Status | What It Enforces |
|-----------|---------|--------|-----------------|
| `constitutional.md` | `always_on` | ✅ LOADING | Master floor: 14 sections (add §13 MCP green light, §14 timeout) |
| `adg-repair-discipline.md` | `always_on` | ✅ LOADING | ADG-first repair loops |
| `author-gate-enforcement.md` | `always_on` | ✅ LOADING | Human-in-the-loop decisions |
| `memory-management.md` | `always_on` | ✅ LOADING | Memory graph hygiene |
| `plan-location.md` | `always_on` | ✅ LOADING | Plan SSOT path + wave format |
| `sequential-thinking-enforcement.md` | `always_on` | ✅ LOADING | Task management for T2/T3, timeout recovery |
| `mcp-config-ssot.md` | ❌ `file_change` → FIX to `glob` | ❌ NOT LOADING | MCP YAML SSOT guidance (rewrite: behavioral only) |
| `mcp-pytest-enforcement.md` | ❌ `file_change` → FIX to `glob` | ❌ NOT LOADING | Pytest MCP validation |
| `security-hardening.md` | ❌ `file_change` → FIX to `model_decision` | ❌ NOT LOADING | Security practices |
| `anti-pattern-author-gate.md` | ❌ `file_change` → FIX to `model_decision` | ❌ NOT LOADING | Anti-pattern Author-Gate approval |
| `adg-test-accelerator-enforcement.md` | ❌ `file_change` → FIX to `glob` | ❌ NOT LOADING | ADG test acceleration |
| ~~`plan_ci_enforcement.md`~~ | `file_change` | **DELETE** | Dup of T1 hook + pre-commit |
| ~~`pytest-config-ssot.md`~~ | `file_change` | **DELETE** | Dup of pre-commit T11.3 |

### Skills (5 — no changes)

| Skill | Invocation | What It Enforces |
|-------|-----------|-----------------|
| `graph-analysis` | Auto / `@mention` | ADG-first dependency analysis |
| `boundary-enforcement` | Auto / `@mention` | Layer boundary + import hygiene |
| `testing-framework` | Auto / `@mention` | Test rigor + skip prevention |
| `operational-gates` | Auto / `@mention` | Rollback + MCP validation |
| `artifact-management` | Auto / `@mention` | Evidence + path validation |

### Workflows (15 → 14 after dedup)

| Workflow | Slash Command | What It Enforces | Keep/Remove |
|----------|--------------|-----------------|-------------|
| `adg-repair-loop.md` | `/adg-repair-loop` | Cluster repair | KEEP (interactive) |
| `adg-redis-refresh.md` | `/adg-redis-refresh` | ADG regen + Redis | KEEP (manual action) |
| `adg-accelerator-optimization.md` | `/adg-accelerator-optimization` | Tool consolidation | KEEP |
| `adg-test-triage-gate.md` | `/adg-test-triage-gate` | Fan-in triage | KEEP |
| `adg-timeout-recovery.md` | `/adg-timeout-recovery` | Timeout recovery | KEEP |
| `agent-deletion-gate.md` | `/agent-deletion-gate` | Agent deletion | KEEP |
| `antipattern-author-gate.md` | `/antipattern-hitl-gate` | Anti-pattern Author-Gate | KEEP |
| `author-gate-decision-gate.md` | `/hitl-decision-gate` | Decision options | KEEP |
| `mcp-config-sync.md` | `/mcp-config-sync` | YAML→JSON sync | KEEP (manual action) |
| `mcp-failure-rca.md` | `/mcp-failure-rca` | MCP diagnosis | KEEP (interactive) |
| ~~`mcp-validate.md`~~ | `/mcp-validate` | MCP config check | **ARCHIVE** (dup of pre-commit T11) |
| `memory-purge-sync.md` | `/memory-purge-sync` | Memory cleanup | KEEP |
| `preprocess-rules.md` | `/preprocess-rules` | Rules expansion | KEEP |
| `progress-display-enforcement.md` | `/progress-display-enforcement` | Progress bars | KEEP |
| `timeout-progress-enforcement.md` | `/timeout-progress-enforcement` | Timeout reporting | KEEP |

---

## Tier 3: ADG (Analysis-Time)

| Gate / Artifact | Script | What It Enforces | Output |
|----------------|--------|-----------------|--------|
| ADG generation | `tools/generate_full_adg.py --strict` | Layer violations, anti-patterns, burndown | `artifacts/adg/adg_indexed_*.sqlite` |
| Governance graph | (part of generation) | Layer boundary violations | `artifacts/adg/adg_governance_graph_*.json` |
| Burndown table (NEW) | (part of generation) | P0/P1/P2 counts, ratchet | `artifacts/adg/adg_burndown_table.json` |
| ADG MCP (runtime) | `tools/adg/core/server.py` | Query interface for T2 rules | SQLite + Redis backends |

---

## Tier 4: Pre-commit (Evidence Consumer — `.pre-commit-config.yaml`)

### KEEP (not duplicated by upstream tiers)

| Hook ID | Tier | Script | What It Enforces |
|---------|------|--------|-----------------|
| `trailing-whitespace` | T0 | (pre-commit-hooks) | Whitespace normalization |
| `end-of-file-fixer` | T0 | (pre-commit-hooks) | EOF normalization |
| `mixed-line-ending` | T0 | (pre-commit-hooks) | LF enforcement |
| `check-merge-conflict` | T0 | (pre-commit-hooks) | Merge conflict markers |
| `guard-no-verify` | T0 | `ops_scripts/ci/guard_no_verify.py` | No-verify bypass auth |
| `guard-guardian-hitl` | T0 | `ops_scripts/ci/guard_guardian_hitl.py` | Guardian Author-Gate auth |
| `guard-agent-deletion` | T0 | `ops_scripts/ci/guard_agent_deletion.py` | Agent deletion auth |
| `python-syntax-check` | T1 | `py -m py_compile` | Syntax validation |
| `guardian-comment-fixer` | T4 | `tools/adg/adg_antipattern_fixer.py` | Auto-fix guardian comments |
| `adg-autofix` | T4.5 | `ops_scripts/hooks/adg_autofix_hook.py` | ADG auto-fix (MEDIUM/LOW) |
| `hollow-file-gate` | T6 | `ops_scripts/ci/hollow_file_gate.py` | AST semantic verification |
| `check-report-location` | T7 | `ops_scripts/hooks/validate_report_location.py` | Report SSOT path |
| `windsurf-governance-health` | T7.7 | `ops_scripts/ci/check_windsurf_governance.py` | Rules/skills health |
| `adg-grep-ban-gate` | T7.9 | `ops_scripts/ci/adg_grep_ban_gate.py` | Grep ban (source code) |
| `no-unconditional-xfail-gate` | T7.10 | `ops_scripts/ci/check_no_unconditional_xfail.py` | xfail discipline |
| `hitl-decision-record-gate` | T7.11 | `ops_scripts/ci/check_hitl_decision_record.py` | Author-Gate records in plans |
| `rca-closure-gate` | T7.12 | `ops_scripts/ci/check_rca_closure.py` | RCA must be RESOLVED |
| `reject-generated-artifacts-tracked` | T8 | `ops_scripts/hooks/reject_tracked_generated_artifacts.py` | No tracked artifacts |
| `check-tooling-apps-boundary` | T9 | `ops_scripts/ci/check_tooling_apps_boundary.py` | Tooling/apps boundary |
| `module-collision-guard` | T10 | `agentic_core/.../module_collision_guardrail.py` | Module collision |
| `adg-unified-gate` | T10.6 | `ops_scripts/hooks/adg_unified_gate.py` | ADG generation + source checks |
| `adg-suggest-report` | T10.7 | `ops_scripts/hooks/adg_suggest_hook.py` | ADG:HIGH suggestions |
| `mcp-config-sovereignty` | T11 | `ops_scripts/ci/check_mcp_config_sovereignty.py` | MCP config structure |
| `mcp-npx-windows-gate` | T11.1 | `ops_scripts/ci/check_mcp_npx_windows.py` | npx platform check |
| `pytest-config-ssot` | T11.3 | `ops_scripts/ci/_validate_pytest_config.py` | Pytest config consistency |
| `guardian-exemption-gate` | T12 | `ops_scripts/ci/guardian_exemption_gate.py` | Exemption quality ratchet |
| `adg-accelerator-compliance-gate` | T14 | `ops_scripts/ci/adg_accelerator_compliance_gate.py` | Python+YAML grep ban |
| `ruff-severity-gate` | T2 | `ops_scripts/ci/ruff_severity_gate.py` | Lint (P0+P1 block) |
| `ruff-format` | T3 | (ruff-pre-commit) | Code formatting |
| `pre-commit-summary-report` | T21 | `ops_scripts/ci/pre_commit_summary_reporter.py` | Summary dashboard |
| NEW: `adg-evidence-gate` | T-NEW | `ops_scripts/hooks/check_adg_evidence.py` | Burndown P0=0, P1 no ratchet |

### ARCHIVE (duplicated by T1 Windsurf hooks)

| Hook ID | Tier | Why Archive | Upstream SSOT |
|---------|------|-------------|---------------|
| `powershell-ban-gate` | T7.8 | PowerShell now blocked at write-time by T1 hook | `pre_run_gate.py` |
| `mcp-config-drift-check` | T11.2 | Drift now detected at write-time by T1 hook | `post_write_gate.py` |
| `windsurf-plan-ci` | T5.5 | Plan validation now at write-time by T1 hook | `pre_write_gate.py` |
| `plan-location-gate` | T7.5 | Plan path now validated at write-time by T1 hook | `pre_write_gate.py` |

---

## Tier 5: GitHub CI (`.github/workflows/`)

### KEEP (cross-platform, integration, or conditional ADG)

| Workflow File | What It Enforces | Why Not Upstream |
|---------------|-----------------|------------------|
| `main_ci_pipeline.yml` | Matrix tests, main gate | Cross-platform validation |
| `adg-pipeline.yml` | Full ADG generation | Conditional — only when evidence stale |
| `adg-mcp-ci.yml` | MCP integration tests | Needs server backends |
| `structure-invariants.yml` | Architectural invariants | Full-repo scan |
| `test-import-contracts.yml` | Import resolution | Cross-platform |
| `environment-contract.yml` | Environment validation | CI-only |

### CANDIDATES FOR ARCHIVE (duplicated by upstream tiers)

| Workflow File | Why Archive | Upstream SSOT |
|---------------|-------------|---------------|
| `adg-grep-ban-ci.yml` | Dup of pre-commit T7.9 + T14 | Pre-commit gates |
| `windsurf-governance-health.yml` | Dup of pre-commit T7.7 | Pre-commit gate |
| `plan-validation-ci.yml` | Dup of T1 hook + pre-commit | T1 hook + pre-commit |
| `pytest-config-ssot.yml` | Dup of pre-commit T11.3 | Pre-commit gate |
| `timeout-progress-enforcement.yml` | Dup of T2 rule + workflow | T2 rule (always_on) |
| `adg-antipattern-ci.yml` | Dup of pre-commit T10.6 ADG unified | ADG unified gate |
| `adg-ci-gates.yml` | Dup of pre-commit T5 | Pre-commit gate |
| `adg-invariant-gates.yml` | Partial dup of structure-invariants | Consolidate into one |
| `adg-invariant-scan.yml` | Partial dup of adg-pipeline | Consolidate into one |
| `prompt-taxonomy-enforcement.yml` | Low signal, rarely fails | Archive |
| `policy-drift-classification.yml` | Low signal | Archive |
| `skip-registry-convergence.yml` | Low signal | Archive |
| `spine-determinism-guard.yml` | Low signal | Archive |
| `ssot-kernel-guardrail.yml` | Dup of pre-commit + structure-invariants | Consolidate |

**Target**: 36 active workflows → ~6 essential workflows.

---

## SSOT Duplication Summary

| Concern | T1 Hook | T2 Rule | T3 ADG | T4 Pre-commit | T5 CI | SSOT Owner |
|---------|:-------:|:-------:|:------:|:--------------:|:-----:|:----------:|
| PowerShell ban | **SSOT** | behavioral | — | ~~ARCHIVE~~ | — | T1 |
| Anti-pattern injection | **SSOT** | behavioral | detection | ratchet (T12) | ~~ARCHIVE~~ | T1 (block) + T3 (detect) |
| MCP config drift | **SSOT** | behavioral | — | ~~ARCHIVE~~ | — | T1 |
| MCP config structure | — | behavioral | — | **SSOT** | — | T4 |
| MCP health | warn | **SSOT** (§13) | — | — | integration | T2 (rule) |
| Plan format | warn | **SSOT** | — | ~~ARCHIVE~~ | ~~ARCHIVE~~ | T1 (block) + T2 (behavioral) |
| Pytest config | — | ~~DELETE~~ | — | **SSOT** | ~~ARCHIVE~~ | T4 |
| Layer violations | — | behavioral | **SSOT** | evidence check | — | T3 |
| Silent swallowers | **SSOT** (block) | behavioral | **SSOT** (detect) | evidence check | — | T1+T3 |
| Grep ban (source) | — | behavioral | — | **SSOT** | ~~ARCHIVE~~ | T4 |
| Timeout discipline | — | **SSOT** (§14) | — | — | ~~ARCHIVE~~ | T2 |
| Author-Gate enforcement | — | **SSOT** | — | record check | — | T2 |
| ADG generation | — | — | **SSOT** | evidence check | conditional regen | T3 |
| Syntax validation | — | — | — | **SSOT** | — | T4 |
| Code style (ruff) | — | — | — | **SSOT** | — | T4 |
| Cross-platform tests | — | — | — | — | **SSOT** | T5 |

---

## ops_scripts/ci — Full Rationalization

### Inventory Summary

| Category | Count | Action |
|----------|------:|--------|
| Non-underscore scripts (public) | 63 | Rationalize below |
| Underscore-prefixed scripts (internal/dead) | 73 | 71 ARCHIVE, 2 KEEP |
| **Total** | **136** | ~96 are archive candidates |

### Underscore-Prefixed Scripts (73 total)

**Only 2 are actively referenced in pre-commit or CI configs:**

| Script | Referenced By | Action |
|--------|--------------|--------|
| `_adg_ci_gates.py` | Pre-commit T5, CI `adg-ci-gates.yml` | KEEP (active gate) |
| `_validate_pytest_config.py` | Pre-commit T11.3, CI `pytest-config-ssot.yml` | KEEP (active gate) |

**71 are DEAD — referenced only in JSON artifact caches, not in any active config:**

Categories of dead underscore scripts:

| Pattern | Count | Examples | Origin |
|---------|------:|---------|--------|
| `_fix_*` fixers | 12 | `_fix_hardcoded_dirs.py`, `_fix_xfail.py`, `_fix_silent_except.py` | One-shot batch repairs |
| `_*_gate.py` gates | 22 | `_capability_registry_gate.py`, `_routing_determinism_gate.py` | Abandoned CI gates never wired |
| `_find_*` / `_search_*` scanners | 4 | `_find_hardcoded_dirs.py`, `_search_fixable.py` | Ad-hoc discovery scripts |
| `_repair_*` / `_converge_*` | 5 | `_repair_and_fix_all.py`, `_converge_fixes.py` | Batch repair campaigns |
| `_debug_*` / `_analyse_*` | 4 | `_debug_mixed_list.py`, `_analyse_ssot_violations.py` | Debugging artifacts |
| `_categorise_*` / `_count_*` | 3 | `_categorise_remaining.py`, `_count_remaining_violations.py` | Triage helpers |
| `_batch_*` / `_run_*` | 3 | `_batch_fix_test_violations.py`, `_run_baseline_and_commit.py` | Batch operations |
| Other one-offs | 18 | `_wave7_burndown_tracker.py`, `_trace_inject.py` | Miscellaneous |

**Recommendation**: Archive all 71 to `tools/archive/ops_scripts_ci_deprecated/`. They are historical artifacts of past repair campaigns, not governance infrastructure.

### Non-Underscore Scripts — Active vs Dead

**ACTIVE in pre-commit (29 scripts):**

| Script | Pre-commit Hook ID | Tier |
|--------|-------------------|------|
| `guard_no_verify.py` | `guard-no-verify` | T0 |
| `guard_guardian_hitl.py` | `guard-guardian-hitl` | T0 |
| `guard_agent_deletion.py` | `guard-agent-deletion` | T0 |
| `pre_commit_summary_reporter.py` | `pre-commit-summary-init` + `pre-commit-summary-report` | T-1, T21 |
| `hollow_file_gate.py` | `hollow-file-gate` | T6 |
| `plan_location_gate.py` | `plan-location-gate` | T7.5 |
| `check_windsurf_governance.py` | `windsurf-governance-health` | T7.7 |
| `check_powershell_ban.py` | `powershell-ban-gate` | T7.8 |
| `adg_grep_ban_gate.py` | `adg-grep-ban-gate` | T7.9 |
| `check_no_unconditional_xfail.py` | `no-unconditional-xfail-gate` | T7.10 |
| `check_hitl_decision_record.py` | `hitl-decision-record-gate` | T7.11 |
| `check_rca_closure.py` | `rca-closure-gate` | T7.12 |
| `check_tooling_apps_boundary.py` | `check-tooling-apps-boundary` | T9 |
| `check_mcp_config_sovereignty.py` | `mcp-config-sovereignty` | T11 |
| `check_mcp_npx_windows.py` | `mcp-npx-windows-gate` | T11.1 |
| `guardian_exemption_gate.py` | `guardian-exemption-gate` | T12 |
| `adg_accelerator_compliance_gate.py` | `adg-accelerator-compliance-gate` | T14 |
| `ruff_severity_gate.py` | `ruff-severity-gate` | T2 |
| `check_dedup_violations.py` | `check-dedup-violations` | manual |
| `check_script_sprawl.py` | `check-script-sprawl` | manual |
| `check_shim_discipline.py` | `check-shim-discipline` | manual |
| `check_rollback_checkpoints.py` | `check-rollback-checkpoints` | T18 |

**ACTIVE in CI only (not pre-commit) — 18 scripts across 18 workflows:**

| Script | CI Workflow | Dup of Pre-commit? |
|--------|------------|-------------------|
| `check_powershell_ban.py` | `ci-integrity-gate.yml` | YES — dup of T7.8 |
| `ci_integrity_gate_fallback.py` | `ci-integrity-gate.yml` | Unique (CI integrity) |
| `check_ci_integrity.py` | `ci-integrity-gate.yml` | Unique (CI integrity) |
| `manifest_ssot_check.py` | `agent-sprawl-check.yml` | Unique (agent sprawl) |
| `active_set_ssot_check.py` | `agent-sprawl-check.yml` | Unique (agent sprawl) |
| `governance_coverage_check.py` | `agent-sprawl-check.yml` | Unique (agent sprawl) |
| `agent_count_cap.py` | `agent-sprawl-check.yml` | Unique (agent sprawl) |
| `discovery_registry_consistency_check.py` | `agent-sprawl-check.yml` | Unique (agent sprawl) |
| `active_set_snapshot_check.py` | `agent-sprawl-check.yml` | Unique (agent sprawl) |
| `mro_new_diamond_check.py` | `agent-sprawl-check.yml` | Unique (MRO) |
| `mro_contract_check.py` | `agent-sprawl-check.yml` | Unique (MRO) |
| `check_tooling_apps_boundary.py` | `structure-invariants.yml` | YES — dup of T9 |
| `validate_timeout_progress.py` | `timeout-progress-enforcement.yml` | No pre-commit equiv |
| `validate_timeout_recovery.py` | `timeout-progress-enforcement.yml` | No pre-commit equiv |
| `check_skip_convergence_gate.py` | `skip-registry-convergence.yml` | No pre-commit equiv |
| `check_policy_drift_classification.py` | `policy-drift-classification.yml` | No pre-commit equiv |
| `check_spine_bypass.py` | `spine-determinism-guard.yml` | No pre-commit equiv |
| `check_spine_adapter_contract.py` | `spine-determinism-guard.yml` | No pre-commit equiv |
| `check_evidence_contract_v2.py` | `spine-determinism-guard.yml` | No pre-commit equiv |
| `check_environment_contract.py` | `environment-contract.yml` | No pre-commit equiv |
| `import_resolution_guardian.py` | `import-resolution-guardian.yml` | No pre-commit equiv |
| `check_directory_deletion_sweep.py` | `import-resolution-guardian.yml` | No pre-commit equiv |
| `check_c0_boundary.py` | `layer-sovereignty-enforcement.yml` | No pre-commit equiv |
| `check_adg_proof_artifact_truthfulness.py` | `adg-proof-artifact-truthfulness.yml` | No pre-commit equiv |

**UNREFERENCED by any active config (~21 scripts) — ARCHIVE candidates:**

| Script | Likely Purpose | Action |
|--------|---------------|--------|
| `active_set_helper.py` | Library helper, not a gate | KEEP if imported by active scripts |
| `adg_burndown_gate.py` | Disabled T13 (subsumed by adg-unified-gate) | ARCHIVE |
| `adg_fanin_triage_gate.py` | ADG triage, no hook/CI ref | ARCHIVE |
| `adg_harden_gate.py` | Hardening, no hook/CI ref | ARCHIVE |
| `adg_layer_violation_gate.py` | Disabled T13.5 (subsumed by adg-unified-gate) | ARCHIVE |
| `adg_lifecycle_gate.py` | No hook/CI ref | ARCHIVE |
| `adg_mypy_ban_gate.py` | Subsumed by accelerator compliance | ARCHIVE |
| `adg_p1_defect_gate.py` | Disabled T13.6 (subsumed by adg-unified-gate) | ARCHIVE |
| `adg_pytest_ban_gate.py` | Subsumed by accelerator compliance | ARCHIVE |
| `adg_python_ban_gate.py` | Subsumed by accelerator compliance | ARCHIVE |
| `adg_skip_file_ratchet.py` | Disabled T15 (subsumed by adg-unified-gate) | ARCHIVE |
| `adg_test_gate.py` | No active hook/CI ref | ARCHIVE |
| `adg_yaml_grep_ban_gate.py` | Subsumed by T14 compliance gate | ARCHIVE |
| `agent_validation.py` | No hook/CI ref | ARCHIVE |
| `archive_authorization_gate.py` | No hook/CI ref | ARCHIVE |
| `assess_phase_wave_tests.py` | One-shot assessment | ARCHIVE |
| `ast_canonical_scanner.py` | Scanner, not a gate | ARCHIVE (if unused) |
| `ast_gap_analysis.py` | One-shot gap analysis | ARCHIVE |
| `ast_gap_deep.py` | One-shot gap analysis | ARCHIVE |
| `ast_gap_report.py` | One-shot gap analysis | ARCHIVE |
| `ast_gap_strict.py` | One-shot gap analysis | ARCHIVE |
| `baseline_io.py` | Library helper | KEEP if imported |
| `benchmark_sqlite_vs_redis.py` | One-shot benchmark | ARCHIVE |
| `capture_ssot_cleanup_evidence.py` | One-shot evidence | ARCHIVE |
| `centrality_gate.py` | No hook/CI ref | ARCHIVE |
| `check_adapter_prohibition.py` | No hook/CI ref | ARCHIVE |
| `check_adg_ingestion.py` | No hook/CI ref | ARCHIVE |
| `check_adg_schema_field_names.py` | CI `adg-schema-field-names.yml` only | KEEP (CI-only) |
| `check_agent_registry_completeness.py` | No hook/CI ref | ARCHIVE |
| `check_anti_patterns.py` | Superseded by adg-unified-gate | ARCHIVE |
| `check_apps_output_contract.py` | No hook/CI ref | ARCHIVE |
| `check_ast_collection_compliance.py` | No hook/CI ref | ARCHIVE |
| `check_determinism_replay.py` | No hook/CI ref | ARCHIVE |
| `check_determinism_violations.py` | No hook/CI ref | ARCHIVE |
| `ast_hardcoded_path_scanner.py` | Scanner tool | ARCHIVE (if unused) |
| `ast_layer_sovereignty_scanner.py` | Scanner tool | ARCHIVE (if unused) |

**Summary: ~40 active scripts, ~96 archive candidates (71 underscore + ~25 non-underscore).**

---

## ops_scripts/ci — Pre-commit `cmd /c` Debt

The following pre-commit hooks use `cmd /c "set PYTHONPATH=.&&..."` — a Windows-only shell wrapper that breaks cross-platform CI and violates the spirit of Constitutional §0 (no shell dependency):

| Hook ID | Current Entry | Fix |
|---------|--------------|-----|
| `adg-ci-gates` | `cmd /c "set PYTHONPATH=.&& py ..."` | Add `PYTHONPATH=.` to script via `sys.path.insert` |
| `hollow-file-gate` | `cmd /c "set PYTHONPATH=.&& set ...&& py ..."` | Internalize env vars in script |
| `check-report-location` | `cmd /c "set PYTHONPATH=.&& py ..."` | Add `sys.path.insert` |
| `reject-generated-artifacts-tracked` | `cmd /c "set PYTHONPATH=.&& py ..."` | Add `sys.path.insert` |
| `check-tooling-apps-boundary` | `cmd /c "set PYTHONPATH=.&& py ..."` | Add `sys.path.insert` |
| `module-collision-guard` | `cmd /c "set PYTHONPATH=.&& py ..."` | Add `sys.path.insert` |
| `adg-unified-gate` | `py ops_scripts/hooks/adg_unified_gate.py` | Already clean ✅ |
| `mcp-config-sovereignty` | `cmd /c "set PYTHONPATH=.&& py ..."` | Add `sys.path.insert` |
| `guardian-exemption-gate` | `cmd /c "set PYTHONPATH=.&& set ...&& py ..."` | Internalize env vars in script |
| `check-dedup-violations` | `cmd /c "set PYTHONPATH=.&& py ..."` | Add `sys.path.insert` |
| `check-script-sprawl` | `cmd /c "set PYTHONPATH=.&& py ..."` | Add `sys.path.insert` |
| `check-shim-discipline` | `cmd /c "set PYTHONPATH=.&& py ..."` | Add `sys.path.insert` |
| `check-rollback-checkpoints` | `cmd /c "set PYTHONPATH=.&& py ..."` | Add `sys.path.insert` |

**13 hooks need `cmd /c` elimination** — each script should handle PYTHONPATH internally.

---

## GitHub CI Workflows — Full Rationalization

### Inventory

| Category | Count | Action |
|----------|------:|--------|
| Active workflows (`.github/workflows/*.yml`) | ~36 | Rationalize below |
| Deleted workflows (`.github/workflows/_deleted/`) | ~4 | Already removed |

### KEEP (6 essential workflows)

| Workflow | What It Enforces | Why Not Upstream |
|----------|-----------------|------------------|
| `main_ci_pipeline.yml` | Matrix tests (ubuntu/windows), main gate | Cross-platform validation |
| `adg-pipeline.yml` | Full ADG generation on evidence staleness | Conditional + heavy compute |
| `adg-mcp-ci.yml` | MCP integration tests (SQLite+Redis) | Needs server backends |
| `structure-invariants.yml` | Import graph, tooling boundary, layer sovereignty | Full-repo scan, multi-gate |
| `test-import-contracts.yml` | Import resolution cross-platform | Ubuntu+Windows matrix |
| `environment-contract.yml` | Environment validation (`check_environment_contract.py`) | CI-only environment |

### CONSOLIDATE (agent-sprawl → structure-invariants or standalone)

| Workflow | Reason | Target |
|----------|--------|--------|
| `agent-sprawl-check.yml` | 13 script calls, 6 gates — too heavy for pre-commit but valuable | KEEP as standalone OR consolidate into `structure-invariants.yml` |
| `ci-integrity-gate.yml` | PowerShell ban (dup of T7.8) + CI integrity fallback | Merge PowerShell check into main CI; keep CI integrity as lightweight job |
| `import-resolution-guardian.yml` | ImportResolutionGuardian + directory deletion sweep | Merge into `test-import-contracts.yml` |
| `safe-remediation-gate.yml` | Protected class allowlist, test count baseline | KEEP (unique safe-remediation concern) |
| `layer-sovereignty-enforcement.yml` | C0 boundary check | Merge into `structure-invariants.yml` |
| `adg-proof-artifact-truthfulness.yml` | ADG proof artifact validation | Merge into `adg-pipeline.yml` |

### ARCHIVE (14 workflows — duplicated by upstream tiers)

| Workflow | Pre-commit Dup | CI Dup | Upstream SSOT |
|----------|---------------|--------|---------------|
| `adg-grep-ban-ci.yml` | T7.9 + T14 | — | Pre-commit gates |
| `windsurf-governance-health.yml` | T7.7 | — | Pre-commit `check_windsurf_governance.py` |
| `plan-validation-ci.yml` | T5.5 + T7.5 | — | T1 hook + pre-commit |
| `pytest-config-ssot.yml` | T11.3 | — | Pre-commit `_validate_pytest_config.py` |
| `timeout-progress-enforcement.yml` | — | — | T2 rule (always_on) + workflow |
| `adg-antipattern-ci.yml` | T10.6 | — | ADG unified gate |
| `adg-ci-gates.yml` | T5 | — | Pre-commit `_adg_ci_gates.py` |
| `adg-invariant-gates.yml` | — | `structure-invariants.yml` | Consolidate |
| `adg-invariant-scan.yml` | — | `adg-pipeline.yml` | Consolidate |
| `prompt-taxonomy-enforcement.yml` | — | — | Low signal, rarely fails |
| `policy-drift-classification.yml` | — | — | Low signal |
| `skip-registry-convergence.yml` | — | — | Low signal |
| `spine-determinism-guard.yml` | — | — | Low signal, niche |
| `ssot-kernel-guardrail.yml` | — | `structure-invariants.yml` | Consolidate |
| `adg-schema-field-names.yml` | — | — | Low signal, merge into adg-pipeline |

### FRAGILE CI PATTERNS (fix during consolidation)

Several CI workflows use defensive `if [ -f "script" ]` guards, indicating uncertainty about script existence:

- `skip-registry-convergence.yml` → `if [ -f "ops_scripts/ci/check_skip_convergence_gate.py" ]`
- `policy-drift-classification.yml` → `if [ -f "ops_scripts/ci/check_policy_drift_classification.py" ]`
- `environment-contract.yml` → `if [ -f "ops_scripts/ci/check_environment_contract.py" ]`
- `ci-integrity-gate.yml` → cascading `if [ -f ... ] elif [ -f ... ]`

These should either reference scripts that definitely exist or be archived.

---

## Missing Enforcement Gaps (Discovered via Cross-Reference)

### GAP-7: No `check_no_archives_imports.py` in pre-commit

Constitutional §12 forbids imports from `archives/` in production code. `check_no_archives_imports.py` exists but is **not wired into any pre-commit hook or CI workflow**. Enforcement is rule-only (behavioral).

**Fix**: Add pre-commit hook at T7.13 tier.

### GAP-8: No `check_terminal_cleanup.py` enforcement

Constitutional §11 mandates terminal process lifecycle management. `check_terminal_cleanup.py` exists but is **not wired into any pre-commit hook or CI workflow**.

**Fix**: This is a runtime concern — best enforced by T2 rule (behavioral). Pre-commit cannot check runtime behavior. **No action needed** — T2 rule is correct SSOT.

### GAP-9: `check_memory_health.py` not in pre-commit or CI

Memory management rule requires daily health checks. Script exists but has **no CI workflow or pre-commit hook**.

**Fix**: Add CI workflow (nightly cron) or make it part of `adg-pipeline.yml`.

### GAP-10: Agent sprawl gates only in CI, not pre-commit

`agent_count_cap.py`, `manifest_ssot_check.py`, `active_set_ssot_check.py` — 6 agent-related gates exist only in `agent-sprawl-check.yml`. No local pre-commit enforcement.

**Assessment**: These are full-repo scans and are appropriately CI-only. **No gap** — T5 is correct SSOT.

### GAP-11: MRO diamond checks only in CI

`mro_new_diamond_check.py`, `mro_contract_check.py` — only in `agent-sprawl-check.yml`.

**Assessment**: MRO analysis requires full import graph. CI-only is appropriate. **No gap**.

### GAP-12: `check_secrets_scan.py` and `check_sensitive_logs.py` unreferenced

Security-critical scripts exist but are **not wired into any hook or CI workflow**.

**Fix**: Add `check_secrets_scan.py` as pre-commit hook at T0 tier (critical security gate). Add `check_sensitive_logs.py` as CI-only (needs full repo scan).

### GAP-13: `dead_production_import_gate.py` unreferenced

Dead import detection exists but is **not wired into any hook or CI workflow**.

**Fix**: Add to `structure-invariants.yml` CI workflow.

### GAP-14: `zero_loss_refactor_verifier.py` unreferenced

Constitutional §10 requires zero-loss refactor verification. Script exists but has **no pre-commit hook**.

**Fix**: Add pre-commit hook at T6.5 tier (after hollow-file-gate, before governance checks).

---

## Updated SSOT Duplication Summary

| Concern | T1 Hook | T2 Rule | T3 ADG | T4 Pre-commit | T5 CI | SSOT Owner |
|---------|:-------:|:-------:|:------:|:--------------:|:-----:|:----------:|
| PowerShell ban | **SSOT** | behavioral | — | ~~ARCHIVE~~ | ~~dup~~ | T1 |
| Anti-pattern injection | **SSOT** | behavioral | detection | ratchet (T12) | ~~ARCHIVE~~ | T1 (block) + T3 (detect) |
| MCP config drift | **SSOT** | behavioral | — | ~~ARCHIVE~~ | — | T1 |
| MCP config structure | — | behavioral | — | **SSOT** | — | T4 |
| MCP health | warn | **SSOT** (§13) | — | — | integration | T2 (rule) |
| Plan format | warn | **SSOT** | — | ~~ARCHIVE~~ | ~~ARCHIVE~~ | T1 (block) + T2 (behavioral) |
| Pytest config | — | ~~DELETE~~ | — | **SSOT** | ~~ARCHIVE~~ | T4 |
| Layer violations | — | behavioral | **SSOT** | evidence check | — | T3 |
| Silent swallowers | **SSOT** (block) | behavioral | **SSOT** (detect) | evidence check | — | T1+T3 |
| Grep ban (source) | — | behavioral | — | **SSOT** | ~~ARCHIVE~~ | T4 |
| Timeout discipline | — | **SSOT** (§14) | — | — | ~~ARCHIVE~~ | T2 |
| Author-Gate enforcement | — | **SSOT** | — | record check | — | T2 |
| ADG generation | — | — | **SSOT** | evidence check | conditional regen | T3 |
| Syntax validation | — | — | — | **SSOT** | — | T4 |
| Code style (ruff) | — | — | — | **SSOT** | — | T4 |
| Cross-platform tests | — | — | — | — | **SSOT** | T5 |
| Zombie process cleanup (PP-9) | **SSOT** (cleanup) | behavioral (§11) | — | — | — | T1 |
| ADG SQLite lock mgmt (PP-10) | **SSOT** (release+warn) | behavioral (§15) | — | — | — | T1 |
| MCP responsibility SSOT (PP-11) | — | **SSOT** (§16) | — | — | — | T2 (registry) |
| MCP config freshness (PP-12) | — | **SSOT** (audit) | — | — | — | T2 (RAG audit + registry) |
| Syntax error prevention (PP-13) | **SSOT** (block) | — | — | backstop (`py_compile`) | — | T1 (write-time) + T4 (commit-time) |
| Guardian comment quality (PP-14) | — | **SSOT** (vocab §8) | flag weak | idempotent fixer + dup gate | — | T2 (vocab) + T3 (scan) + T4 (gate) |
| MCP config simplification (PP-15) | remove drift logic | **SSOT** (Windsurf-native JSON) | — | ARCHIVE sovereignty + npx only | — | T2 (simplify) + T4 (archive gates) |
| Author-Gate ⭐ SVP calibration (PP-16) | — | **SSOT** (target state doc + §Author-Gate-0.2 + §9) | — | — | — | T2 (rule + doc) |
| ADG blast radius intelligence (PP-17) | — | **SSOT** (§2.2 enhanced + playbook) | blast radius evidence | — | — | T2 (rule) + T3 (ADG analysis) |
| Plan format enforcement (PP-18) | — | **SSOT** (template + plan-location rule) | — | — | — | T2 (rule + template) |
| Archives import ban | — | behavioral (§12) | — | **NEW T7.13** | — | T4 (NEW) |
| Secrets scan | — | — | — | **NEW T0** | — | T4 (NEW) |
| Agent sprawl | — | — | — | — | **SSOT** | T5 |
| MRO diamond | — | — | — | — | **SSOT** | T5 |
| Dead imports | — | — | — | — | **NEW** | T5 (NEW) |
| Zero-loss refactor | — | behavioral (§10) | — | **NEW T6.5** | — | T4 (NEW) |
| Memory health | — | behavioral | — | — | **NEW (cron)** | T5 (NEW) |

---

## Hardening Checklist

- [ ] **H-1**: Zero hardcoded paths in hook scripts — all use `pathlib.Path(__file__).resolve()`
- [ ] **H-2**: Every hook script has companion test with exit-0 and exit-2 paths
- [ ] **H-3**: `hooks.json` uses `working_directory: "."` — no absolute paths
- [ ] **H-4**: MCP green light in `constitutional.md` §13 — prerequisite for T2/T3 work
- [ ] **H-5**: One SSOT per concern — no enforcement duplication across tiers
- [ ] **H-6**: 7 broken rule triggers fixed to valid activation modes
- [ ] **H-7**: Graceful degradation — hook bugs exit 0 (don't break Cascade on hook failures)
- [ ] **H-8**: Eliminate 13 `cmd /c` wrappers in pre-commit — scripts handle PYTHONPATH internally
- [ ] **H-9**: Archive 71 dead underscore-prefixed scripts to `tools/archive/ops_scripts_ci_deprecated/`
- [ ] **H-10**: Archive ~25 unreferenced non-underscore scripts
- [ ] **H-11**: Wire 4 missing enforcement scripts (GAP-7, GAP-9, GAP-12, GAP-14)
- [ ] **H-12**: Fix 4 fragile `if [ -f "script" ]` CI workflow guards
- [ ] **H-13**: Reduce CI workflows from ~36 → 6-8 essential (consolidate + archive 14-28)
- [ ] **H-14**: Zombie process cleanup hook kills orphaned PIDs on chat end (PP-9)
- [ ] **H-15**: ADG SQLite lock released on chat end + warned before ADG tool calls (PP-10)
- [ ] **H-16**: MCP registry `docs/guides/MCP_Registry.md` covers all 14 MCPs with rationale, scope, SSOT, overlaps (PP-11, PP-15 — Markdown replaces YAML)
- [ ] **H-17**: All 14 MCPs verified current — one-time version check via `npm outdated`/`pip list --outdated` + GitHub repo pulse (PP-12, PP-15 — simplified from 8-point audit)
- [ ] **H-18**: Zero red MCP indicators on Windsurf startup — all servers initialize cleanly after MCP Terminal migration review
- [ ] **H-19**: ADR published `docs/architecture/adr/adr-mcp-config-audit.md` documenting audit findings, version decisions, sequential-thinking lessons learned
- [ ] **H-20**: Syntax errors blocked at write-time via `ast.parse()` in `pre_write_gate.py` — zero `except as e:` class bugs survive (PP-13)
- [ ] **H-21**: `adg_antipattern_fixer.py` is idempotent — zero duplicate `# guardian:` comments injected on repeated runs (PP-14)
- [ ] **H-22**: Column 5 Precise Exceptions vocabulary from `docs/reference/Python/Error & Exception Handling.md` codified in constitutional §8 and `global_rules.md` (PP-14)
- [ ] **H-23**: ADG anti-pattern scanner flags guardian comments with generic-only justifications — P1 ratchet enforced (PP-14)
- [ ] **H-24**: MCP YAML SSOT (`config/mcp_servers.yaml`) archived — Windsurf-native `mcp_config.json` is sole config source (PP-15)
- [ ] **H-25**: `sync_yaml_to_global.py`, `check_mcp_config_sovereignty.py`, `/mcp-config-sync` workflow all archived (PP-15)
- [ ] **H-26**: MCP registry lives in `docs/guides/MCP_Registry.md` (Markdown, not YAML) — rationale, scope, overlaps documented (PP-15)
- [ ] **H-27**: MCP config change end-to-end takes <5 minutes — no sync scripts, no drift detection, no multi-step pipeline (PP-15)
- [ ] **H-28**: `docs/architecture/target-state-svp-engineering.md` published with concrete OpenAI Agentic SVP Engineering quality bar (PP-16)
- [ ] **H-29**: All Author-Gate ⭐ recommendation templates cite specific target-state attributes, not abstract principles (PP-16)
- [ ] **H-30**: Constitutional §9 SVP Engineering persona references target state doc (PP-16)
- [ ] **H-31**: Constitutional §2.2 includes mandatory blast radius computation (steps 5-7) before T2/T3 refactoring (PP-17)
- [ ] **H-32**: `docs/reference/ADG_Analysis_Playbook.md` published with 6 graph analysis patterns (blast radius, coupling hotspot, dependency cluster, orphan detection, layer violation map, weighted debt scoring) (PP-17)
- [ ] **H-33**: Author-Gate §1.2 refactoring scope template requires blast radius evidence from ADG `edge_fanout` + `edge_fanin` (PP-17)
- [ ] **H-34**: Blast radius intelligence validated via proof-of-concept on ≥1 real refactoring (PP-17)
- [ ] **H-35**: `.windsurf/templates/execution-plan-template.md` includes phase-level summary table with columns: Wave, Phase, Title, Scope, Pain Points, Est. Tokens, Status (PP-18)
- [ ] **H-36**: `.windsurf/rules/plan-location.md` mandates phase-level summary table — plan without it is invalid (PP-18)
- [ ] **H-37**: All env vars in `mcp_config.json` use Windsurf-native `${env:VAR_NAME}` interpolation, not shell `${VAR:-default}` syntax (PP-15, RAG finding)
- [ ] **H-38**: Total tool count across all MCPs audited and confirmed under 100 limit (Windsurf hard cap). Unused tools disabled. (PP-15, RAG finding)
- [ ] **H-39**: `docs/guides/MCP_Registry.md` includes transport type per MCP (stdio/Streamable HTTP/local) (PP-11, PP-15, RAG finding)
- [ ] **H-40**: RAG research completed for MCP standardization — 4 sources pulled (Windsurf docs, MCP best practices, Windsurf University, MCP protocol spec) with findings recorded in Phase 2.7 Step 1 (PP-12, PP-15)
