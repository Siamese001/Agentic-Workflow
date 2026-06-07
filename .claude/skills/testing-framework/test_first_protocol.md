# Test-First Protocol

Tests MUST exist before logic changes are committed.

## Sequence

1. Write the test (failing)
2. Run the test — confirm it fails for the right reason
3. Write the minimal production code to make it pass
4. Run the test — confirm it passes
5. Refactor if needed — tests must still pass

## Determinism Requirements

- No random inputs — fix seeds explicitly
- No time-dependent behavior — inject timestamps
- No external mutable state — mock or fixture
- Identical input → identical output, always

## Mock Discipline

Mocks are ONLY permitted for:
- External services that cannot run locally
- Hardware interfaces
- Filesystem permissions in CI

Mocks MUST NOT bypass:
- Validation logic
- Signature checks
- Routing gates
- Replay enforcement
- Side-effect guards

## Test Dimensions (mandatory per changed surface)

| Dimension | What to test |
|---|---|
| Edge cases | null/None, empty input, malformed, boundary values, unauthorized, stale state, dependency failure |
| State transitions | valid→valid, invalid→attempted, repeated, interrupted, replayed |
| Determinism | identical inputs → identical outputs; independent of wall clock and execution order |
| Fail-closed | invalid preconditions block operation; no side-effects before block |
| Matrix | all combinations of interacting gates (feature flag × input validity, etc.) |

## Regression Rule

Every bug fix MUST include:
1. A minimal reproducer test that fails before the fix
2. An adjacent near-miss test that verifies the boundary is correct
