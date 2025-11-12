# Phase Status

## Phase 1 — Agentic Core & Safety

Phase 1 of the LIC agentic rollout is complete and the exit criteria are satisfied:

- **Safety defenses**: High-risk prompt injections are blocked by the outreach stack via `detect_injection`, as exercised in the regression suite.
- **Reasoning toggles**: `ReasoningToggles` enforces bounded CoT/ToT/reflexion settings with deterministic normalization and validation.
- **End-to-end orchestration**: `OutreachStack` composes the router, architect, CTA, signature, and validator agents into a single pass that returns a draft or safety stop.
- **Test coverage**: `tools/run_tests_with_coverage.py` enforces the 90% gate without third-party plugins; the latest run reports 90% coverage across `src/lic_agentic`.

## Evidence

- Unit, integration, e2e, and regression suites all pass with zero skips (see testing logs).
- Coverage command: `tools/run_tests_with_coverage.py`.

Use the commands documented in `TESTING.md` to rerun the verification flow whenever Phase 1 functionality changes.

## Phase 2 — Memory + RAGStack (Complete)

Phase 2 is complete and meets all documented exit criteria:

- **Duplicate suppression**: `tests/unit/test_retrieval_planner.py::test_dedupe_and_budget` exercises the planner's
  dedupe/budget controls, keeping tool calls within the max-call envelope.
- **Evidence anchoring**: `tests/e2e/test_value_claim_evidence.py` ensures every retrieval outcome results in an
  `[artifact_id:…]` marker in the outreach draft.
- **Latency SLO**: `tests/regression/test_retrieval_latency_slo.py` validates that the deterministic tool latencies
  maintain a p95 ≤ 3.5 seconds.
- **Coverage**: `tools/run_tests_with_coverage.py` reports ≥90% line coverage across `src/lic_agentic`, exceeding the
  ≥88% Phase 2 gate.

Refer to `TESTING.md` for the command sequence to reproduce these results.

## Phase 3 — QAStack + Reflexive Retry (Complete)

Phase 3 is now complete with all exit criteria satisfied:

- **Schema-driven QA**: `QAValidator` enforces subject, opener, CTA, signature, and
  evidence markers, catching placeholder regressions and ungrounded claims.
- **Reflexive retry loop**: `ValidatorAgent` performs targeted retries that repair
  missing CTAs, signatures, and artifacts; unit and e2e suites confirm ≥80% of
  initial FAILs are fixed on retry.
- **Token drift guardrails**: Metrics capture per-run token counts and drift, and
  regression tests ensure the drift ceiling stays ≤10% while pass rate remains ≥85%.
- **Metrics visibility**: `MetricsTracker` reports retry success rates, latency p95,
  pass rate, and token drift so QA SLOs remain observable.

See `TESTING.md` for the CI command list that validates these guarantees end to end.
