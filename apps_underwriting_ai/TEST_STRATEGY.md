# Test Strategy — apps_underwriting_ai

**Application:** apps_underwriting_ai (AI Underwriting Decision Pipeline)
**Last Updated:** 2026-05-02
**Companion docs:** `README.md` · `RUNBOOK.md` · `SLO.md` · `SVP_ENGINEERING_REVIEW.md` · `TECHNICAL_SPEC.md`

---

## Test Tiers

apps_underwriting_ai uses a **three-tier test strategy** matching sibling apps (`apps_rfp/tests/`, `apps_research/tests/`):

| Tier | File | Purpose | Run frequency |
|---|---|---|---|
| **Smoke** | `tests/test_smoke.py` | Pipeline runs end-to-end via every entrypoint | Every commit; fastest signal |
| **Contract** | `tests/test_contract.py` | Type-contract invariants (frozen dataclasses, verdict enum bounds, field presence) | Every commit |
| **Integration** | `tests/test_integrations.py` | Adapter contracts (ExecutionAdapter, IngressRunner, SpineHandoff, Observability) | Every commit |
| **Output** | `tests/test_outputs.py` | Renderer round-trips (Markdown / JSON / disk emission) | Every commit |
| **Types** | `tests/test_underwriting_types.py` | Frozen-dataclass discipline, enum bounds, immutability | Every commit |

All tests run via `python -m pytest apps_underwriting_ai/tests/ -v`.

---

## Test Inventory (skeleton stage)

### Smoke (`tests/test_smoke.py`) — 5 tests

| Test | What it proves |
|---|---|
| `test_imperative_driver_runs_end_to_end` | `UnderwritingEngine.run()` emits a verdict for a 2-document request |
| `test_governed_run_matches_imperative_path` | `governed_underwriting_run()` produces equivalent results |
| `test_execution_adapter_dispatches` | `ExecutionAdapter` wires inbound requests through the pipeline |
| `test_decision_renderer_emits_markdown_and_json` | `DecisionRenderer` produces non-empty Markdown + JSON |
| `test_spine_handoff_packages_envelope` | `SpineHandoff.package()` returns an R3_grounded_read envelope |

### Contract (`tests/test_contract.py`) — pending

Validates pipeline-level invariants:
- Every APPROVE has `len(register.records) ≥ 1`
- Every `unresolved > 0` reconciliation forces verdict = REFER
- Every empty-evidence + empty-features state forces verdict = INSUFFICIENT_EVIDENCE
- `result.request_id == request.request_id` (no reshuffling)
- `result.trace_id == trace_id_passed_in`
- `decision.gate_violations` is always a tuple, never None

### Types (`tests/test_underwriting_types.py`) — pending

Validates frozen-dataclass discipline:
- `UnderwritingRequest` is `frozen=True` (cannot mutate fields)
- `EvidenceRegister.records` is a tuple (immutable)
- `DecisionVerdict` enum has exactly 4 members; no string drift
- All optional fields default deterministically

### Integrations (`tests/test_integrations.py`) — pending

Validates adapter contracts:
- `ExecutionAdapter.execute(ExecutionRequest)` returns `UnderwritingResult`
- `UnderwritingIngressRunner.run_from_file` raises on missing `request_id`/`applicant_id`/`product_class`
- `UnderwritingIngressRunner.run_from_file` raises on `.txt` extension
- `SpineHandoff.package` returns envelope with `app=apps_underwriting_ai`, `route=R3_grounded_read`
- `ObservabilityAdapter.emit_*` does not raise on any well-formed input

### Outputs (`tests/test_outputs.py`) — pending

Validates renderer round-trips:
- `DecisionRenderer.to_json` parses back as valid JSON
- `DecisionRenderer.to_markdown` contains the verdict, request_id, all evidence_refs, all feature names
- `EnterpriseUnderwritingRenderer.render_to_disk` creates both `decision_<id>.md` and `run_summary_<id>.json`
- Output files have non-zero size

---

## Test Quality Bar

### What every test must do

1. **Be deterministic** — no clocks, no randomness, no network. Skeleton stage forbids any non-deterministic input.
2. **Be self-contained** — no shared fixtures across tests; each test constructs its own request.
3. **Use real types** — never mock `UnderwritingRequest` / `DecisionPacket` / etc. Construct real instances.
4. **Assert specific signals** — `assert result.decision.verdict == DecisionVerdict.APPROVE`, not `assert result is not None`.

### What no test may do

1. **Mock the pipeline orchestration** — that defeats the test's purpose. Test the real pipeline.
2. **Assert on rationale string content** — rationale wording is implementation detail; assert on verdict enum + evidence count instead.
3. **Use `pytest.mark.skip` or `xfail`** — forbidden by constitutional §1. Either fix the test or delete it.

---

## Coverage Targets

| Surface | Target |
|---|---|
| `engines/*.py` | 100% line coverage at skeleton stage (small surfaces) |
| `integrations/*.py` | 100% line coverage |
| `outputs/*.py` | 100% line coverage |
| `types/underwriting_types.py` | 100% (dataclass exercise) |
| `__main__.py` | Smoke-tested via `--demo`; no separate target |
| `parsers/`, `validators/` | Reserved (empty); no tests until populated |

---

## Property Tests (deferred)

Property-based tests (Hypothesis) are deferred to feature-complete stage. The skeleton's deterministic heuristics make property tests low-value relative to enumerated contract tests. When real verdict logic lands, candidate properties:

- For all `request: UnderwritingRequest`, `engine.run(request).decision.verdict` is one of the 4 enum members.
- For all `request` with `documents=()`, `engine.run(request).decision.verdict ∈ {APPROVE, INSUFFICIENT_EVIDENCE, REFER}` (never DECLINE since DECLINE requires real verdict logic).
- For all `request`, `engine.run(request).request_id == request.request_id`.

---

## Running Tests

```bash
# All apps_underwriting_ai tests
python -m pytest apps_underwriting_ai/tests/ -v

# Smoke only (fastest)
python -m pytest apps_underwriting_ai/tests/test_smoke.py -v

# Just contract + types
python -m pytest apps_underwriting_ai/tests/test_contract.py apps_underwriting_ai/tests/test_underwriting_types.py -v

# With coverage
python -m pytest apps_underwriting_ai/tests/ --cov=apps_underwriting_ai --cov-report=term-missing
```

---

## CI Gating

apps_underwriting_ai tests run in the standard test suite. No app-specific gates at skeleton stage. Feature-complete stage will introduce:

- Pipeline-shape immutability gate (verify the 5 stage names + IDs match `config/hop_pipeline.py`)
- Verdict-distribution sanity gate (large input fixtures don't all collapse to one verdict)
- Spine-route consistency gate (`spine_manifest.yaml` matches `SpineHandoff.ROUTE`)

---

## References

- `apps_rfp/TEST_STRATEGY.md` — sibling pattern (where extant)
- Constitutional §1 — no test skipping
- `.windsurf/skills/testing-framework/` — test rigor invariants
- Plan: `.windsurf/plans/apps-completeness-followups-287d2a.md` (this doc + contract tests)
