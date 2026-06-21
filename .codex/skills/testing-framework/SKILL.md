---
name: testing-framework
description: Enforces test rigor, pytest collection integrity, execution counts, and skip discipline with mandatory ADG-backed scope selection. Use when writing new tests, modifying existing tests, running pytest at T2/T3 scope, evaluating a proposed `pytest.mark.skip`/`xfail`, or selecting which tests must run for a given code change.
metadata:
  enforcement_layer: pre-commit
  enforcement_timing: after_work
  enforcement_type: structural
---

# Testing Framework Skill (Consolidated)

**PREREQUISITE:** `graph-analysis` skill MUST be invoked first (§0 tier-aware analysis).

Consolidated skill that merges `test-rigor-enforcement` and `pytest-integrity` into a unified testing enforcement framework.

## Files

- **`pre_code_generation_gate.md`** — MANDATORY before any code changes. Declares scope, identifies changed surfaces, specifies required test coverage.
- **`test_first_protocol.md`** — Enforces test-first discipline with deterministic requirements and edge case coverage.
- **`collection_execution_integrity.md`** — Validates pytest collection vs execution counts, prevents silent test deselection.
- **`skip_management_protocol.md`** — Zero-tolerance skip management with allowlist requirements and registry tracking.
- **`post_code_validation.md`** — MANDATORY after code changes. Runs coverage verification and count validation.
- **`apps_testing_model.md`** — Required for `apps_*`, `apps_eval`, and `tests/_apps_contract` testing work. Classifies app tests as LAW, APP CONTRACT, SPINE BINDING, EVAL CONTRACT, HARNESS, MIGRATION, ARCHAEOLOGY, or FUTURE.

## When to use

- **ALWAYS before code generation:** Use `pre_code_generation_gate.md` to declare test requirements
- **During code generation:** Use `test_first_protocol.md` to write tests before logic
- **ALWAYS after code changes:** Use `post_code_validation.md` to verify compliance
- **ALWAYS when triaging a test failure:** Follow the 5-check decision tree to assign repair class before any edit
- **When running pytest:** Use `collection_execution_integrity.md` to verify integrity
- **When changing app-owned tests:** Use `apps_testing_model.md` and include an `apps-test-model: <bucket>` marker in changed app test files.

## Constitutional Requirements Enforced

### Zero-Tolerance Coverage (§1.1)
Every changed line of logic MUST have deterministic tests. Use dependency graph to find existing coverage edges and identify gaps. No exceptions.

**Required test dimensions (mandatory for every changed surface):**
- **Edge cases:** null/None/missing field, empty input, malformed structure, boundary values, unauthorized input, stale/replay state, dependency failure, negative and recovery paths
- **State transitions:** valid→valid, invalid→attempted, repeated, interrupted, replayed
- **Determinism:** identical input → identical output; replay independence from wall clock, randomness, execution order
- **Fail-closed:** invalid preconditions block operation; no side-effects before block
- **Matrix:** test all interacting gates (feature flag × input validity, retry × confidence, policy × mutation, etc.)

### Test-First Discipline (§1.2)
Tests MUST exist before logic changes are committed. Write them first.

### Deterministic Tests Only (§1.3)
No random inputs, no time-dependent behavior, no external mutable state. Fix seeds and inject timestamps.

### Three Quality Gates (enforced in priority order)
1. **No silent exception swallowers** — any bare `except: pass` is assumed violation. Must convert to assertion, explicit re-raise, logged degraded path, or `# guardian: allow-silent-swallower` with tight scope and documented justification.
2. **No zero-assert / fake-healthy tests** — zero assertions, `assert True`, `pass`-only bodies, and broad mocks with no assertions are all FORBIDDEN. Tests MUST assert on returned value, emitted signal, state change, or side effect.
3. **No non-strict xfail** — `@pytest.mark.xfail` without `strict=True` = FORBIDDEN.

### Test Selection & Execution

**Graph-backed test selection:** Test selection MUST be dependency-graph-backed via **`tools/adg/adg_test_selector.py`** (Accelerator #5). For every changed production file, identify tests via: direct test imports, fixture dependency edges, integration entrypoint coverage, registry/factory reachability, CLI-to-function reachability. Filename similarity is not sufficient. No test edge found = coverage gap to fix, not proof no tests are needed.

**NodeID-first testing discipline:** When ADG provides exact test nodeids → run those nodeids first. File-level fallback ONLY when nodeid extraction fails. Directory-level ONLY in final full-suite run. Any fallback MUST be recorded as `## SCOPE_LOSSINESS` in evidence.

**Test-file edit restriction:** Test-file edits FORBIDDEN unless cluster root cause is itself in test infrastructure. Never edit tests to make them pass — fix production code.

### Skip Management (§1.4)

**Zero-tolerance for test skipping and xfail drift:**
- Run ALL collected tests — no selective skipping
- Collected ≠ executed = CRITICAL FAILURE
- `xfail` without `strict=True` = FORBIDDEN
- Adding `pytest.mark.skip`, `pytest.mark.xfail`, or commenting out assertions to unblock a phase = CONSTITUTIONAL VIOLATION
- Pre-existing skips MUST be in the skip registry BEFORE the run begins

**Skip allowlist requirements:**
- Test skips MUST be explicitly in the allowlist (`tests/_config/skip_allowlist.py`), fully documented (reason, ticket, expiry/owner), and tracked.
- **Forbidden outside allowlist:** `@pytest.mark.skip`, `@pytest.mark.skipif`, `pytest.skip()`, `unittest.skip*`.
- **Required skip metadata:** `reason` (specific), `ticket`, `expiry_date` OR `owner`, `skip_type`, `test`, `file`.
- **Forbidden reasons:** "broken", "TODO", "fix later", "not working", "WIP", "temporary", "skip for now".

**Pre-existing skip registry:** All pre-existing skips MUST be recorded in `artifacts/adg/pre_existing_skip_registry.json` with: `test_id`, `skip_reason` (specific), `cluster_id`, `registered_at`, `owner`, `expiry_date` (within 30 days), `resolution_plan` (concrete).

**Convergence BLOCKED unless:** zero unregistered skips, zero expired registry entries, all entries have resolution plans.

### Collection & Execution Integrity

**Test counts are invariants.** Unexpected drops = CI failure. CI tracks: total collected, per-directory counts, per-marker counts, xfail count, skip count (from allowlist).

Baseline: `tests/_config/test_count_baseline.json`. Count drops = FAIL. xfail increases = FAIL. Skip count increases = FAIL. Intentional reduction requires commit justification and manual baseline update.

**Collection vs Execution Validation:**
- MUST verify `collected == executed` for every test run
- ANY deselection = CRITICAL FAILURE
- Report exact counts in evidence: `## TEST_COUNT_AUDIT`

## Evidence Requirements

**ROBUSTNESS_MATRIX section mandatory:** success/edge/failure/recovery/determinism/side-effect tests per changed surface.

**Conditional sections (add when applicable):**
- `## TEST_QUALITY_AUDIT` — when test quality enforcement runs
- `## SKIP_DRIFT_AUDIT` — when skip drift enforcement runs
- `## TEST_COUNT_AUDIT` — when collection/execution counts are validated

## Regression Testing

Every bug fix MUST include a minimal reproducer and an adjacent near-miss case. Mutation-sensitive tests MUST fail if guard clauses are removed or comparisons flip.

## Mock Discipline

Mocks ONLY for: external services that cannot run locally, hardware interfaces, filesystem permissions in CI. Mocks MUST NOT bypass validation, signature checks, routing gates, replay enforcement, or side-effect guards.

## Agent Deletion Policy

**Zero-tolerance for unauthorized agent deletion.** Deleting any `*Agent.py` requires: `AGENT-DELETION-AUTHORIZED` commit marker, replacement specified, 90-day deprecation period, zero active references. Enforcement: pre-commit hook `guard-agent-deletion`.

## Enforcement Registry

| Requirement | Enforcement Script(s) |
|-------------|---------------------|
| Test quality gates | `ops_scripts/ci/check_test_integrity.py`, `ops_scripts/ci/check_no_unconditional_xfail.py`, `ops_scripts/ci/check_utility_silent_swallowers.py` |
| Skip management | `ops_scripts/ci/check_skip_convergence_gate.py`, `ops_scripts/ci/skip_quarantine_check.py` |
| Test count invariants | `ops_scripts/ci/check_test_integrity.py` |

**Single entrypoint:** `python ops_scripts/ci/run_contract_gates.py`

## Forbidden Patterns

- ❌ Tests without assertions (zero-assert tests)
- ❌ Random inputs or time-dependent behavior
- ❌ Mocks that bypass validation or routing gates
- ❌ Test skipping without allowlist documentation
- ❌ Silent test deselection (collected ≠ executed)
- ❌ Editing tests to make them pass instead of fixing production code
- ❌ `xfail` without `strict=True`
- ❌ Bare `except: pass` in tests without documented justification
