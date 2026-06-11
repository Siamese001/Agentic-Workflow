---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\phase3b-architectural-hardening-report.md'
original_relative_path: 'phase3b-architectural-hardening-report.md'
source_sha256: b65dfe398a80259d537c45c1d027b1b15daf3ed5f75a98a47c0e67156b8d40fa
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phase 3b: Architectural Hardening Report

**Date**: 2026-02-08
**Scope**: Address 4 critique items from Phase 3 dedup validation

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## 1. Mixin Architecture Fix (Critical — COMPLETE)

**Problem**: `CodeToolRunnerMixin(SovereignBaseAgent)` created a tightly-coupled linear chain. Any agent needing two capabilities (e.g., ToolRunner + ContentValidator) would hit Python's Diamond Problem in MRO.

**Fix**: Refactored to pure capability class with backward-compat alias.

| Aspect | Before | After |
|--------|--------|-------|
| `code_tool_runner_core.py` | `class CodeToolRunnerMixin(SovereignBaseAgent)` | `class CodeToolRunnerCapability` (no base) |
| `CodeFormatterAgent.py` | `class CodeFormatterAgent(CodeToolRunnerMixin)` | `class CodeFormatterAgent(CodeToolRunnerCapability, SovereignBaseAgent)` |
| `UnusedCleanupAgent.py` | `class UnusedCleanupAgent(CodeToolRunnerMixin)` | `class UnusedCleanupAgent(CodeToolRunnerCapability, SovereignBaseAgent)` |
| Backward compat | N/A | `CodeToolRunnerMixin = CodeToolRunnerCapability` alias |

**Files modified**:
- `agentic_core/L5_safety/reasoning/code_tool_runner_core.py`
- `agentic_core/L5_safety/reasoning/CodeFormatterAgent.py`
- `agentic_core/L5_safety/reasoning/UnusedCleanupAgent.py`
- `tests/unit/dedup/test_consolidation_regression.py`

**Verification**: 3 new architectural tests added:
- `test_capability_does_not_inherit_sovereign_base` — PASSED
- `test_no_diamond_problem_code_formatter` — PASSED (SovereignBaseAgent appears exactly once in MRO)
- `test_no_diamond_problem_unused_cleanup` — PASSED
- `test_backward_compat_alias_importable` — PASSED

---

## 2. CI Guardrails (Critical — COMPLETE)

**Problem**: `stop-sprawl_policy.md` was a policy document, not a mechanism. No hard gate prevented duplication regression.

**Fix**: Created `artifacts/dedup/sprawl_gate.py` — a CI gate that reads similarity artifacts and exits non-zero on threshold breach.

**Features**:
- Configurable thresholds: `--max-code-sim`, `--max-prompt-sim`, `--max-resp-overlap`
- Waiver system: known-acceptable pairs (e.g., Cluster 6 post-extraction) can be exempted
- Exit codes: 0 (pass), 1 (breach), 2 (missing artifacts)
- GitHub Actions workflow: `.github/workflows/agent-sprawl-check.yml`

**Verification**:
```
$ python artifacts/dedup/sprawl_gate.py --max-code-sim 0.75
  WAIVER: CodeFormatterAgent <-> UnusedCleanupAgent = 0.8143 (waived)
  FAIL: 8 threshold breach(es) detected
  Exit code: 1
```

**Files created**:
- `artifacts/dedup/sprawl_gate.py`
- `.github/workflows/agent-sprawl-check.yml`

---

## 3. HOP Shared Plumbing Extraction (Medium — COMPLETE)

**Problem**: 9 HOP agents (Hop1–Hop9) repeat identical IO/State plumbing at their edges: `registry.add_trace("PHASE_START", ...)`, defensive buffer reads, `buffer.write_once(...)`.

**Fix**: Created `HOPStageCapability` — a pure capability class (same pattern as Task 1) that encapsulates the shared edge plumbing.

**Shared patterns extracted**:
- `read_required_inputs(buffer, registry)` — validates upstream dependencies
- `write_output(buffer, registry, output_data)` — writes to buffer + logs DECISION_FINAL
- `run_stage(buffer, registry)` — PHASE_START bookend + delegates to `_process()`
- `HOP_STAGE_NAME` / `REQUIRED_INPUTS` class variables for declarative config

**Files created**:
- `apps_lic/utils/hop_stage_capability.py`
- `tests/unit/dedup/test_hop_stage_capability.py`

**Verification**: 9/9 tests passed:
- `test_importable` — PASSED
- `test_does_not_inherit_lic_agent_base` — PASSED (pure mixin)
- `test_has_required_interface` — PASSED
- `test_read_required_inputs_missing_key` — PASSED (RuntimeError)
- `test_read_required_inputs_success` — PASSED
- `test_write_output` — PASSED (buffer + trace)
- `test_run_stage_adds_phase_start` — PASSED

**Note**: The 9 HOP agents are not yet migrated to use `HOPStageCapability`. This is intentional — the capability is ready for incremental adoption without breaking existing agents.

---

## 4. Import Complexity Metrics (Medium — COMPLETE)

**Problem**: LOC reduction is a vanity metric. The real signal is **blast radius** — how many internal dependencies an agent carries.

**Fix**: Added import complexity analysis to `run_dedup_analysis.py`. Classifies each import as internal/stdlib/third-party and reports blast radius per agent and per layer.

**Key findings**:
- **190 agents analyzed**
- **Average blast radius**: 4.3 internal imports
- **Max blast radius**: FileClassificationAgent (29 internal imports)
- **L5_safety layer**: highest avg blast radius (5.2), max 29
- **apps_rg layer**: lowest avg blast radius (2.0)

**Files modified**:
- `artifacts/dedup/run_dedup_analysis.py` (new Phase 1 section)

**Output artifact**: `artifacts/dedup/similarity/import_complexity.md`

---

## Test Results Summary

```
tests/unit/dedup/ — 12 passed, 23 skipped, 0 failed (0.14s)

Passed:
  - 3 architectural tests (mixin purity, Diamond Problem prevention, alias compat)
  - 9 HOPStageCapability contract tests

Skipped:
  - 23 tests requiring pydantic/meta_learning_client_types (pre-existing env constraint)
```

## Artifacts Produced

| Artifact | Path | Type |
|----------|------|------|
| Capability class | `agentic_core/L5_safety/reasoning/code_tool_runner_core.py` | Refactored |
| Capability class | `apps_lic/utils/hop_stage_capability.py` | New |
| CI gate | `artifacts/dedup/sprawl_gate.py` | New |
| CI workflow | `.github/workflows/agent-sprawl-check.yml` | New |
| Blast radius report | `artifacts/dedup/similarity/import_complexity.md` | Generated |
| Regression tests | `tests/unit/dedup/test_consolidation_regression.py` | Updated |
| Regression tests | `tests/unit/dedup/test_hop_stage_capability.py` | New |
| This report | `docs/reports/plans/phase3b-architectural-hardening-report.md` | New |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

