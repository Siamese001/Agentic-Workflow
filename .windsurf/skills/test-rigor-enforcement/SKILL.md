---
name: test-rigor-enforcement
description: Enforces §1 TESTING & EVIDENCE requirements from .windsurfrules during code generation. Use before any code changes to declare test requirements, during code generation to validate test-first discipline, and after code changes to verify test coverage. Prevents code commits without deterministic tests.
enforcement_layer: pre-commit
enforcement_timing: after_work
enforcement_type: structural
---

# Test Rigor Enforcement Skill

**PREREQUISITE:** `dependency-graph-analysis` skill MUST be invoked first (§0 tier-aware analysis).

Enforces constitutional testing requirements (§1.1-§1.12) during code generation with mandatory AST dependency graph backing.

## Files

- **`pre_code_generation_gate.md`** — MANDATORY before any code changes. Declares scope, identifies changed surfaces, specifies required test coverage per §1.5, §1.6, §1.7. BLOCKS code generation until test plan approved.

- **`test_first_protocol.md`** — Enforces §1.2 test-first discipline. Write tests BEFORE logic changes. Validates tests are deterministic (§1.3), cover edge cases (§1.5), and target real entrypoints (§1.10).

- **`post_code_validation.md`** — MANDATORY after code changes. Runs pytest with collection/execution count verification (§1.12), validates test coverage matches declared scope, checks for determinism violations, verifies no test skipping.

## When to use

- **ALWAYS before code generation:** Use `pre_code_generation_gate.md` to declare test requirements
- **During code generation:** Use `test_first_protocol.md` to write tests before logic
- **ALWAYS after code changes:** Use `post_code_validation.md` to verify compliance
- **ALWAYS when triaging a test failure:** Follow the 5-check decision tree in `docs/technical/TEST_FAILURE_decision_tree.md` to assign repair class before any edit (§2.5)

## Constitutional Requirements Enforced

### §1.1 Zero-tolerance
- Every line of changed logic MUST have tests
- No exceptions

### §1.2 Test-first discipline
- Tests MUST exist before logic changes are committed
- If tests do not exist, write them first

### §1.3 Deterministic tests only
- No random inputs, no time-dependent behavior, no external state
- Fix seeds for randomness, inject deterministic timestamps

### §1.5 Edge cases are mandatory
- null/None/missing field
- empty input
- malformed structure
- boundary values
- unauthorized input
- stale state
- replay input
- dependency failure
- negative control path
- recovery path

### §1.12 Zero-tolerance for test skipping
- Run ALL collected tests without selective skipping
- Fail HARD if any test is deselected or bypassed
- Report exact count of collected vs executed tests
