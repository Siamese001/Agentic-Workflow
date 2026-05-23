# Pre-commit Hook Detailed Analysis

Complete breakdown of every pre-commit hook (T0-T21) with rationale, effectiveness, and optimization notes.

---

## TIER 0: Admission Guards

### T0-guard: No-Verify Bypass Authorization
- **Script**: `ops_scripts/ci/guard_no_verify.py`
- **Stage**: commit-msg
- **Trigger**: Always runs
- **What it does**: Blocks commits with `--no-verify` bypass unless authorized
- **Rationale**: Prevents accidental or malicious bypass of all pre-commit checks
- **Effectiveness**: Critical - enforces governance compliance
- **Cost**: Minimal (string check in commit message)
- **Optimization**: None needed

### T0-guard: HITL Authorization for New Guardian Exemptions
- **Script**: `ops_scripts/ci/guard_guardian_hitl.py`
- **Stage**: commit-msg
- **Trigger**: Always runs on commit-msg
- **What it does**: Requires HITL approval when new guardian exemptions are added
- **Rationale**: Constitutional §8.5.2 - prevents silent addition of anti-pattern exemptions
- **Effectiveness**: High - enforces human review for critical governance changes
- **Cost**: Minimal (pattern matching in commit message)
- **Optimization**: None needed

### T0-guard: Agent Deletion Authorization
- **Script**: `ops_scripts/ci/guard_agent_deletion.py`
- **Trigger**: Always runs
- **What it does**: Blocks deletion of *Agent.py files without authorization marker
- **Rationale**: Constitutional §1.6 - prevents accidental deletion of critical agents
- **Effectiveness**: Critical - protects core architecture
- **Cost**: Minimal (file pattern check)
- **Optimization**: None needed

### T0: Trailing Whitespace
- **Tool**: pre-commit-hooks (standard)
- **Trigger**: All files except .md
- **What it does**: Removes trailing whitespace
- **Rationale**: Prevents git diff noise, ensures clean diffs
- **Effectiveness**: High - auto-fixes common formatting issues
- **Cost**: Minimal
- **Optimization**: None needed

### T0: End-of-File Fixer
- **Tool**: pre-commit-hooks (standard)
- **Trigger**: All files except .md
- **What it does**: Ensures files end with newline
- **Rationale**: POSIX compliance, prevents diff noise
- **Effectiveness**: High
- **Cost**: Minimal
- **Optimization**: None needed

### T0: Enforce LF Line Endings
- **Tool**: pre-commit-hooks (standard)
- **Trigger**: All files except .md
- **What it does**: Converts CRLF to LF
- **Rationale**: Cross-platform consistency, Windows/Linux compatibility
- **Effectiveness**: Critical for cross-platform development
- **Cost**: Minimal
- **Optimization**: None needed

### T0: Check Merge Conflict Markers
- **Tool**: pre-commit-hooks (standard)
- **Trigger**: All files
- **What it does**: Blocks commits with `<<<<<<<`, `=======`, `>>>>>>>` markers
- **Rationale**: Prevents committing unresolved merge conflicts
- **Effectiveness**: Critical - prevents broken merges
- **Cost**: Minimal
- **Optimization**: None needed

---

## TIER 1: Syntax Gate

### T1: Python Syntax Validation
- **Tool**: `python -m py_compile`
- **Trigger**: Python files only
- **What it does**: Compiles Python files to check for syntax errors
- **Rationale**: Fastest possible fail - broken syntax should never proceed
- **Effectiveness**: Critical - catches syntax errors before any other checks
- **Cost**: Fast (~0.1s per file)
- **Optimization**: None needed - already optimal

---

## TIER 2: Ruff Lint (4 passes)

### T2-P0: Ruff Critical (Security/Safety/Runtime)
- **Tool**: ruff
- **Rules**: F821,F401,B012,B904,S102,S307,S601,F541,B013,B015
- **What it does**: Undefined names, unused imports, assert in except, etc.
- **Rationale**: Security and safety issues must be caught immediately
- **Effectiveness**: Critical - blocks dangerous code
- **Cost**: Medium (subprocess overhead)
- **Optimization**: **CONSOLIDATE** - merge with P1-P3 into single pass

### T2-P1: Ruff High (Bug Patterns/Code Quality)
- **Tool**: ruff
- **Rules**: B002,B006,B009,B010,B019,B027,S105,S106,S107,S108,S311,S324,S603,S607,UP028,C401-C404,B904
- **What it does**: Bug patterns, hardcoded passwords, random module, etc.
- **Rationale**: High-severity bugs should block commits
- **Effectiveness**: High - prevents common bug patterns
- **Cost**: Medium (subprocess overhead)
- **Optimization**: **CONSOLIDATE** - merge with P0-P2-P3 into single pass

### T2-P2: Ruff Medium (Style/Organization)
- **Tool**: ruff
- **Rules**: E402,E721,E731,F811,B007,B011,B023,B024,B028,C405-C411,COM812,COM819,I001
- **What it does**: Import placement, bare except, duplicate args, etc.
- **Rationale**: Code quality issues with --exit-zero (warning mode)
- **Effectiveness**: Medium - non-blocking, informative
- **Cost**: Medium (subprocess overhead)
- **Optimization**: **CONSOLIDATE** - merge with P0-P1-P3 into single pass

### T2-P3: Ruff Low (Formatting/Python3)
- **Tool**: ruff
- **Rules**: E501,W291-W293,W505,T201,T203,UP001,UP003-UP005,UP008-UP010
- **What it does**: Line length, trailing whitespace, print statements, Python 2/3 issues
- **Rationale**: Low-priority style issues with --exit-zero (info mode)
- **Effectiveness**: Low - purely informational
- **Cost**: Medium (subprocess overhead)
- **Optimization**: **CONSOLIDATE** - merge with P0-P1-P2 into single pass

**TIER 2 OPTIMIZATION SUMMARY**: All 4 passes can be merged into single ruff call with combined `--select` flags. Estimated savings: ~1s per commit.

---

## TIER 3: Ruff Format

### T3: Ruff Format
- **Tool**: ruff-format
- **Trigger**: All files except .md and check_anti_patterns.py
- **What it does**: Normalizes Python code formatting (Black-compatible)
- **Rationale**: Consistent style across codebase, reduces diff noise
- **Effectiveness**: High - auto-fixes formatting
- **Cost**: Medium (requires full file parse)
- **Optimization**: None needed - separate from lint for clarity

---

## TIER 4: ADG Accelerator Auto-Fixers

### T4: Guardian Comment Auto-Fix (Accelerator #1)
- **Script**: `tools/adg/adg_antipattern_fixer.py --staged`
- **Trigger**: Always runs
- **What it does**: Canonicalizes guardian comment format to `# guardian: allow-<type> -- <justification>`
- **Rationale**: Ensures guardian comments are parseable by scanner
- **Effectiveness**: High - auto-fixes non-canonical comments
- **Cost**: Low (regex-based, no Redis)
- **Optimization**: None needed

---

## TIER 5+: Logic Analysis & Structural Checks

### T-1: Pre-Commit Summary Initialization
- **Script**: `ops_scripts/ci/pre_commit_summary_reporter.py --init`
- **Trigger**: Always runs
- **What it does**: Clears temp issue collection directory before governance hooks
- **Rationale**: Initialize issue aggregation for T21 summary report
- **Effectiveness**: High - enables comprehensive issue reporting
- **Cost**: Minimal (directory cleanup)
- **Optimization**: **MOVE** - should run at very beginning (before T0), not after T4

### T5: ADG CI Delta Gates (Wave 0 M1-M6)
- **Script**: `ops_scripts/ci/_adg_ci_gates.py`
- **Stage**: manual only
- **What it does**: Six ADG CI delta gates (M1-M6) for plan hardening
- **Rationale**: CI-only checks too heavy for local commits
- **Effectiveness**: N/A (manual stage only)
- **Cost**: High (ADG generation)
- **Optimization**: None needed (manual only)

### T6: Hollow File Gate — AST Semantic Verification
- **Script**: `ops_scripts/ci/hollow_file_gate.py --changed-only`
- **Trigger**: Always runs
- **What it does**: Blocks new hollow files (no behavioral code), flags files that become hollow
- **Rationale**: Constitutional §10 - prevents zero-loss refactor violations
- **Effectiveness**: Critical - enforces semantic validity
- **Cost**: Low (AST parse on changed files only)
- **Optimization**: None needed

### T7: Report Location SSOT Check
- **Script**: `ops_scripts/hooks/validate_report_location.py --staged-only`
- **Trigger**: Always runs
- **What it does**: Ensures reports are in `docs/reports/plans/` not elsewhere
- **Rationale**: SSOT enforcement for report locations
- **Effectiveness**: High - prevents report sprawl
- **Cost**: Minimal (path check)
- **Optimization**: None needed

### T7.5: Plan Location SSOT Gate
- **Script**: `ops_scripts/ci/plan_location_gate.py`
- **Trigger**: Always runs
- **What it does**: Blocks plans in `.windsurf/plans/` instead of `docs/reports/plans/`
- **Rationale**: SSOT enforcement for plan locations
- **Effectiveness**: High - prevents plan sprawl
- **Cost**: Minimal (path check)
- **Optimization**: None needed

### T7.7: Windsurf Governance Health Check (P1) — **REMOVED 2026-04**
- **Script**: ~~`ops_scripts/ci/check_windsurf_governance.py`~~ (deleted; never re-homed)
- **GitHub Action**: ~~`.github/workflows/_deleted/windsurf-governance-health.yml`~~ (removed W1 windsurf-gha-cutover-d9f2a7)
- **Replacement**: Cursor governance hooks + `contract-gates.yml`; see [windsurf_gha_cutover_closeout.md](cursor/windsurf_gha_cutover_closeout.md)

### T8: Reject Tracked Generated Artifacts
- **Script**: `ops_scripts/hooks/reject_tracked_generated_artifacts.py`
- **Trigger**: Always runs
- **What it does**: Blocks commits if git tracks generated artifacts (guardian_report.json, etc.)
- **Rationale**: Generated artifacts should not be in version control
- **Effectiveness**: Critical - prevents artifact pollution
- **Cost**: Minimal (git ls-files check)
- **Optimization**: None needed

### T9: Tooling/Apps Boundary Guard (§8.3)
- **Script**: `ops_scripts/ci/check_tooling_apps_boundary.py --staged-only`
- **Trigger**: Python files only, `always_run: false`
- **What it does**: Ensures tools/evidence and ops_scripts/ci don't import apps_* runtime modules
- **Rationale**: Tooling must remain pure - apps_* only referenced as strings/paths
- **Effectiveness**: High - enforces architectural boundaries
- **Cost**: Low (import analysis on staged files)
- **Optimization**: None needed

### T10: Module Collision Guard
- **Script**: `agentic_core/L5_safety/enforcement/module_collision_guardrail.py`
- **Trigger**: Always runs
- **What it does**: Detects duplicate modules, logical import paths, case collisions
- **Rationale**: Architectural enforcement - prevents module namespace conflicts
- **Effectiveness**: High - maintains module integrity
- **Cost**: Medium (filesystem scan)
- **Optimization**: None needed

### T10.5: Eager Import Lint
- **Script**: `tools/lint_eager_imports.py tests --strict --config config/eager_import_risk.yml`
- **Trigger**: Always runs
- **What it does**: Blocks test files with eager agentic_core imports that cause collection failures
- **Rationale**: Prevents pytest collection failures from circular imports
- **Effectiveness**: High - prevents test infrastructure breakage
- **Cost**: Low (test file analysis)
- **Optimization**: None needed

### T10.6: ADG Preflight — Gap Analysis + Collection Safety
- **Script**: `tools/adg/adg_test.py preflight --quick`
- **Trigger**: Always runs
- **What it does**: Runs gap analysis and collection safety check using ADG
- **Rationale**: Unified testing accelerator - validates test coverage before expensive gates
- **Effectiveness**: High - early test validation
- **Cost**: Medium (ADG query)
- **Optimization**: None needed

---

## TIER 11: Config SSOT Checks

### T11: MCP Config Sovereignty
- **Script**: `ops_scripts/ci/check_mcp_config_sovereignty.py`
- **Trigger**: `mcp_config.json` only
- **What it does**: Validates MCP config: filesystem server locked to repo root (Rule #0)
- **Rationale**: Constitutional Rule #0 - filesystem security boundary
- **Effectiveness**: Critical - enforces filesystem security
- **Cost**: Minimal (config validation)
- **Optimization**: None needed

### T11.2: MCP Config Drift Detection
- **Script**: `tools/adg/sync_global_config.py --check`
- **Trigger**: Always runs
- **What it does**: Compares workspace MCP config with global config, detects drift
- **Rationale**: Prevents workspace vs global MCP configuration drift
- **Effectiveness**: High - maintains MCP consistency
- **Cost**: Low (config comparison)
- **Optimization**: **CONSIDER FILE-TRIGGER** - could run only when MCP config files change

### T11.3: Pytest Config SSOT
- **Script**: `ops_scripts/ci/_validate_pytest_config.py --strict`
- **Trigger**: `pytest.ini` or `pyproject.toml` only
- **What it does**: Validates pytest.ini vs pyproject.toml [tool.pytest.ini_options] consistency
- **Rationale**: Prevents Windsurf IDE vs CI pytest behavior mismatch
- **Effectiveness**: High - ensures test consistency
- **Cost**: Minimal (config validation)
- **Optimization**: None needed

---

## TIER 12: Ratchets & Policy Enforcement

### T12: Guardian Exemption Quality Ratchet
- **Script**: `ops_scripts/ci/guardian_exemption_gate.py`
- **Trigger**: Always runs
- **What it does**: 
  - Rule 1: Every guardian comment MUST have `-- <justification>`
  - Rule 2: Exemption counts in production code may only decrease
- **Rationale**: Closes scanner blind spot - burndown gate only counts unwhitelisted violations
- **Effectiveness**: Critical - enforces exemption quality and limits
- **Cost**: Medium (file scan)
- **Optimization**: None needed

### T13: ADG Anti-Pattern Burndown Ratchet
- **Script**: `ops_scripts/ci/adg_burndown_gate.py`
- **Trigger**: Always runs
- **What it does**: 
  - Rule 1: No new file+category pairs (blocking)
  - Rule 2: Existing counts may only decrease (ratchet)
- **Rationale**: Unified anti-pattern governance - prevents regression
- **Effectiveness**: Critical - enforces anti-pattern burndown
- **Cost**: Medium (anti-pattern scanner)
- **Optimization**: None needed

### T13.5: ADG Layer Violation Gate
- **Script**: `ops_scripts/ci/adg_layer_violation_gate.py --warn`
- **Trigger**: Always runs
- **What it does**: Queries ADG edges table for `relation_type = 'violates'`, reports in warning mode
- **Rationale**: Visibility for layer boundary violations
- **Effectiveness**: **INEFFECTIVE** - 0 'violates' edges in current ADG
- **Cost**: Low (SQLite query)
- **Optimization**: **REMOVE** - dead code, never blocks

### T13.6: ADG P1 Defect Gate
- **Script**: `ops_scripts/ci/adg_p1_defect_gate.py`
- **Trigger**: Always runs
- **What it does**: Queries ADG violations table for `severity = 'critical'`, blocks if found
- **Rationale**: Block commits with critical ADG defects
- **Effectiveness**: **INEFFECTIVE** - 0 'critical' severity violations in current ADG
- **Cost**: Low (SQLite query)
- **Optimization**: **REMOVE** - dead code, never blocks

---

## TIER 14-16: ADG Accelerator Compliance

### T14: ADG Python Ban Gate
- **Script**: `ops_scripts/ci/adg_python_ban_gate.py --staged`
- **Trigger**: Python files only, `always_run: false`
- **What it does**: Hard-fails if staged Python files use grep/mypy/pytest as ADG substitutes
- **Rationale**: Enforces use of ADG accelerators instead of grep/mypy/pytest
- **Effectiveness**: High - enforces ADG adoption
- **Cost**: Medium (file scan)
- **Optimization**: **CONSOLIDATE** - merge with T15-T16 into single gate

### T15: ADG YAML Grep-Ban Gate
- **Script**: `ops_scripts/ci/adg_yaml_grep_ban_gate.py --staged`
- **Trigger**: YAML files only, `always_run: false`
- **What it does**: Hard-fails if staged YAML workflows invoke grep/rg in run: steps
- **Rationale**: Enforces Python-based ADG accelerators in CI
- **Effectiveness**: High - enforces ADG adoption in CI
- **Cost**: Medium (file scan)
- **Optimization**: **CONSOLIDATE** - merge with T14-T16 into single gate

### T16: ADG Skip-File Ratchet
- **Script**: `ops_scripts/ci/adg_skip_file_ratchet.py`
- **Trigger**: Python files only, `always_run: false`
- **What it does**: Hard-fails if new skip-file directives added without updating budget
- **Rationale**: Prevents abuse of skip-file exemptions
- **Effectiveness**: High - enforces exemption discipline
- **Cost**: Low (count check)
- **Optimization**: **CONSOLIDATE** - merge with T14-T15 into single gate

**TIER 14-16 OPTIMIZATION SUMMARY**: All three gates check ADG accelerator compliance patterns. Can be merged into single `adg_accelerator_compliance_gate.py` with unified error reporting. Estimated savings: ~1s per commit.

---

## TIER 19: Freshness Warning

### T19: ADG Staleness Guard
- **Script**: `tools/adg/adg_stale_guard.py --warn`
- **Trigger**: Python files only, `always_run: false`
- **What it does**: Warns when ADG Redis cache is stale vs latest Python commits
- **Rationale**: Alert developers to regenerate ADG after code changes
- **Effectiveness**: Medium (warning mode only, non-blocking)
- **Cost**: Low (timestamp comparison)
- **Optimization**: **MOVE** - should run before ADG-dependent gates (T12-T13) for fail-fast

---

## TIER 20: Cleanup

### T20: Pycache Purge
- **Script**: `ops_scripts/maintenance/purge_cache.py --quiet --all`
- **Trigger**: Always runs
- **What it does**: Removes __pycache__ directories from repo
- **Rationale**: Prevents __pycache__ pollution, must run after all Python hooks
- **Effectiveness**: Critical for cleanliness
- **Cost**: Low (filesystem cleanup)
- **Optimization**: None needed - must be last

---

## TIER 21: Summary Report

### T21: Pre-Commit Governance Summary Report
- **Script**: `ops_scripts/ci/pre_commit_summary_reporter.py --report`
- **Trigger**: Always runs
- **What it does**: Aggregates issues from all governance hooks and displays formatted table
- **Rationale**: Provides comprehensive summary of all governance issues
- **Effectiveness**: High - visibility into all issues
- **Cost**: Low (reads JSONL from temp dir)
- **Optimization**: None needed - must be last after T20

---

## Manual / CI-Only Lane

These hooks only run in `stages: [manual]` and are too heavy for local commits.

### CI: C0 Sovereignty Guardian
- **Script**: `agentic_core/L0_routing/scripts/run_guardian_c0_sovereignty.py`
- **What it does**: Ensures embeddings don't drive routing decisions
- **Rationale**: Prevents embedding bias in routing

### CI: Dedup Guard
- **Script**: `ops_scripts/ci/check_dedup_violations.py`
- **What it does**: Prevents duplicate symbols in codebase
- **Rationale**: Architectural cleanliness

### CI: Script Sprawl Guard
- **Script**: `ops_scripts/ci/check_script_sprawl.py`
- **What it does**: Blocks new runner scripts
- **Rationale**: Prevents tooling proliferation

### CI: Shim Discipline
- **Script**: `ops_scripts/ci/check_shim_discipline.py`
- **What it does**: Enforces backward-compatibility shims
- **Rationale**: Prevents breaking changes

### CI: Rollback Gate
- **Script**: `ops_scripts/ci/check_rollback_checkpoints.py`
- **What it does**: Validates multi-file phase checkpoints
- **Rationale**: Ensures safe multi-file operations

---

## Summary Table

| Hook | Effectiveness | Cost | Optimization |
|------|---------------|------|--------------|
| T0 guards | Critical | Minimal | None |
| T1 syntax | Critical | Fast | None |
| T2 ruff (4x) | High | Medium | **CONSOLIDATE to 1 pass** |
| T3 format | High | Medium | None |
| T4 guardian fix | High | Low | None |
| T-1 summary init | High | Minimal | **MOVE to start** |
| T5 ADG CI gates | N/A (manual) | High | None |
| T6-T10 structural | High | Low-Medium | None |
| T11-T11.3 config | High | Minimal | T11.2 could be file-triggered |
| T12 exemption ratchet | Critical | Medium | None |
| T13 burndown | Critical | Medium | None |
| T13.5 layer violation | **INEFFECTIVE** | Low | **REMOVE** |
| T13.6 P1 defect | **INEFFECTIVE** | Low | **REMOVE** |
| T14-T16 ADG bans | High | Medium | **CONSOLIDATE to 1 gate** |
| T19 staleness | Medium | Low | **MOVE before ADG gates** |
| T20 purge | Critical | Low | None |
| T21 summary | High | Low | None |

---

## Priority Optimizations

1. **REMOVE T13.5 and T13.6** - Dead code, never block commits
2. **CONSOLIDATE T2 ruff passes** - 4 subprocess calls → 1 call (~1s savings)
3. **CONSOLIDATE T14-T16** - 3 ADG ban gates → 1 gate (~1s savings)
4. **MOVE T-1 to start** - Initialize before any hooks run
5. **MOVE T19 before T12** - Check ADG freshness before ADG-dependent gates
6. **CONSIDER T11.2 file-trigger** - Only run when MCP config changes

**Total estimated savings: ~3s per commit (30% reduction)**
