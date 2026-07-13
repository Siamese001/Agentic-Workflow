---
name: testing-framework
description: Use this skill when adding or changing tests, selecting graph-backed tests for a code change, triaging pytest failures, reviewing skip or xfail use, or validating collection, execution, determinism, and regression coverage.
metadata:
  owner: platform-team
  version: "2.0"
---

# Testing framework

Use tests to prove behavior rather than to conceal implementation defects. Editing tests is legitimate
when the intended contract changes, a regression test is added, or test infrastructure is defective;
weakening assertions merely to make a run pass is not.

## Workflow

1. Use `graph-analysis` to identify production surfaces, direct tests, fixtures, integration entrypoints,
   and registry/factory reachability.
2. State the behavior contract and the failure that the test must detect.
3. Add or update the smallest deterministic test before or alongside the implementation change.
4. Run exact node IDs first, then the containing file, then broader suites as confidence grows.
5. Compare collected, selected, executed, skipped, xfailed, and deselected counts.
6. Run the relevant broader contract gate and inspect the diff for weakened assertions or broad mocks.

Read [pre_code_generation_gate.md](pre_code_generation_gate.md) before a T2/T3 implementation and
[test_first_protocol.md](test_first_protocol.md) for test-shape guidance.

## Required dimensions

Cover the dimensions that can change the result:

- success and expected state transition;
- malformed, missing, unauthorized, stale, or replayed input;
- dependency failure and recovery;
- repeated or interrupted execution;
- deterministic output under fixed inputs;
- side effects and fail-closed behavior.

A bug fix needs a minimal reproducer and at least one adjacent near-miss case.

## Collection and skip integrity

- Unexpected deselection or collection-count reduction is a failure until explained.
- `xfail` must be strict and tied to a specific unresolved behavior.
- A skip needs the repository's allowlist metadata, owner, reason, and expiry or removal condition.
- Do not add `assert True`, empty test bodies, zero-assert mocks, or broad exception swallowing.

Read [collection_execution_integrity.md](collection_execution_integrity.md) and
[skip_management_protocol.md](skip_management_protocol.md) when those surfaces change.

## Mock discipline

Mock external services, hardware, or inaccessible permissions only. Do not mock away validation,
authorization, routing, replay protection, or side-effect guards that the test is meant to prove.

## Validation

```bash
python -m pytest <exact-nodeids> -q
python ops_scripts/ci/check_test_integrity.py
```

For application-owned tests, read [apps_testing_model.md](./apps_testing_model.md). Finish with the
broader command specified by [post_code_validation.md](post_code_validation.md).
