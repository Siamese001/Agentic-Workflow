# ADR-028 — apps_eval → system_learning Publisher Boundary

**Status**: Accepted
**Date**: 2026-04-22
**Deciders**: Cascade (planning); implemented under plan `eval-meta-otel-deferred-completion-d6b4e0`
**Impact Layers**: L_APP (apps_eval) ↔ L_SL (system_learning)
**Related**: ADR-025 (heal_router OTel), ADR-023 (runtime HITL), parent plan `eval-meta-otel-gap-review-ef4a20`

---

## 1. Context

The evaluation harness (`apps_eval/`) historically did not feed evaluation results (scorecards, regression verdicts, HITL quality reports, retrieval signals, scenario-suite outcomes) into the canonical meta-learning bus (`system_learning/meta_learning/meta_learning_bus.py`). The parent plan wired five eval engines to publish via a new adapter at `apps_eval/integrations/meta_bus_publisher.py`. The two imports that actually cross the layer boundary are:

```python
from system_learning.meta_learning.meta_learning_bus import get_process_bus
from system_learning.meta_learning.meta_learning_bus import MetaLearningChangePackage
```

Both imports are **lazy** (inside try/except blocks) and **fail-open** (if `system_learning` is unimportable, the publisher degrades to a log-only stub and the eval run continues). They still trigger the `authority_boundary`, `capability_egress`, and `write_sovereignty` ADG gates because structurally they are `L_APP → L_SL` edges, which is the general direction the layer policy forbids.

---

## 2. Decision

**Keep the cross-layer import in place**, protected by a guardian-exemption comment, and document the rationale in this ADR. Do **not** relocate the publisher shim to `infrastructure/`.

### 2.1 The canonical pattern

The adapter imports each symbol once, inside a `try: ... except ImportError:` block, accompanied by a guardian comment stating the rationale:

```python
def _try_get_process_bus() -> Any | None:
    try:
        # guardian: allow-cross-layer-import -- apps_eval -> system_learning is the
        # documented publisher boundary (plan eval-meta-otel-gap-review-ef4a20 W2).
        # Kept lazy + fail-open so eval never hard-depends on system_learning.
        from system_learning.meta_learning.meta_learning_bus import get_process_bus

        return get_process_bus()
    except ImportError as exc:  # pragma: no cover - minimal env
        logger.info("meta_bus_publisher: canonical bus unavailable (%s)", exc)
        return None
```

### 2.2 What this decision does and does not bless

| Permitted under ADR-028 | NOT permitted |
|---|---|
| `apps_eval/integrations/meta_bus_publisher.py` importing from `system_learning.meta_learning.meta_learning_bus` | Any other `apps_eval/**` module importing from `system_learning/**` |
| Any `apps_eval` engine importing **only from** `apps_eval.integrations.meta_bus_publisher` to publish outcomes | `apps_eval` engines reaching into `system_learning` directly |
| Future publisher adapters under `apps_eval/integrations/*` following the same lazy+fail-open pattern | Synchronous consumption of `system_learning` side effects inside an eval hot path |

This ADR is narrowly scoped to the **publisher boundary**. Consumers, drainers, or learning-pipeline clients remain forbidden in `apps_eval/`.

---

## 3. Alternatives Considered

### 3.1 Relocate the shim to `infrastructure/` (rejected)

Moving `meta_bus_publisher.py` into `infrastructure/sdks_mcps/` would put the cross-layer edge under the infra layer instead of `apps_eval`. It was rejected because:

1. The cross-layer edge **still exists** — it just moves to `infrastructure → L_SL`. ADG gates would flag it identically.
2. Callers in `apps_eval` would still import *from* `infrastructure` to reach the publisher, creating a new `L_APP → infrastructure` edge that is also currently flagged.
3. The lazy+fail-open pattern is the actual safety guarantee, not the file location. Moving the file is cosmetic.
4. Score (0.88 keep+ADR vs 0.42 relocate, gap 0.46) dominates per the Author-Gate threshold rule.

### 3.2 Introduce a callback-based interface (rejected)

Let `system_learning` register a callback that `apps_eval` invokes by reference. Rejected because it inverts the dependency at the cost of making the wiring implicit, harder to test, and requires a bootstrap hook on every eval run. No tangible safety improvement.

### 3.3 Synchronous HTTP / message-bus indirection (rejected)

Route publications through `enhanced_http` or a queue. Rejected because it introduces a runtime dependency, eliminates the deterministic content-hash property of `MetaLearningChangePackage.create()`, and adds failure modes that `publish_eval_outcome` currently handles by returning `PublishReceipt(ok=False, ...)` in-process.

---

## 4. Consequences

### 4.1 Positive

- Zero refactor cost; the parent plan's completed W-D1/W-D2 work stands.
- The guardian comment pattern is auditable — `check_guardian_exemptions.py` can validate the comment format.
- Content-hash + fail-open + lazy-import triad is preserved.
- Downstream `system_learning.engines.bus_consumer.drain_and_apply()` receives packages without any additional wiring.

### 4.2 Negative

- Future maintainers must read this ADR when they see the guardian comment. Mitigation: guardian comment points at ADR-028 and the plan slug.
- (Originally believed: "ADG gates will flag these imports and they will appear in P0 waves until gates are taught the exemption." Verified 2026-04-22 that this is NOT the case — see §4.3 resolution. Leaving note for provenance.)

### 4.3 Follow-up work

- **[resolved 2026-04-22]** Teach ADG gates about ADR-028. *Outcome: no change needed.* Verified via `mv_authority_boundary_breaches` on `adg_indexed_04222026_2055.sqlite`: the MV only flags `L_APP → L0/L1/L2` (class `L_APP_core_bypass`) and `L6 → L0/L2` (class `L6_downstream_mutation`). `L_APP → L_SL` is not a flagged pair. `apps_eval/integrations/meta_bus_publisher.py → system_learning/**` edges return zero rows from `mv_authority_boundary_breaches`, zero rows from `mv_capability_and_egress_gaps` (capability gates the provider surface, not module imports), and zero rows from `mv_write_sovereignty_paths` (writer paths are UWG-based, not import-based). The guardian comments on the two lazy imports therefore serve as documentation for reviewers, not as gate suppressors. No `check_*.py` modification required.
- **[resolved 2026-04-22]** Replace the `apps_eval._telemetry` no-op shim. *Outcome: shim now lazily delegates to `agentic_core.runtime.contracts.lifecycle_trace_contract` (SSOT) with fail-open fallback to the original no-op when standalone. `LayerSegment` values are locally defined and match SSOT exactly. Tests: `tests/unit/apps_eval/test_telemetry_shim.py` (5 cases covering delegation, fallback, and attribute contract).
- **[informational 2026-04-22]** Extend the pattern to future publisher adapters (e.g., `apps_exec`, `apps_research`) under `apps_*/integrations/*`. *Outcome: no work available now — no such adapters exist in the current tree.* `grep_search` over `apps_exec/**` and `apps_research/**` returned zero cross-layer imports from `system_learning/**`. The pattern (lazy import inside `try/except ImportError` + guardian comment referencing ADR-028 + fail-open publish) stands as documentation for whenever a new eval-style publisher is introduced. If/when that happens, the implementer should:
  1. Place the adapter at `apps_<name>/integrations/<bus>_publisher.py`.
  2. Use the same `_try_get_process_bus()` lazy-import wrapper.
  3. Add a guardian comment: `# guardian: allow-cross-layer-import -- apps_<name> -> system_learning is the documented publisher boundary (ADR-028).`
  4. Add integration tests modeled on `@c:/Git/Agentic-Workflow/tests/integration/apps_eval/test_eval_to_bus_roundtrip.py`.

---

## 5. Compliance Matrix

| Constitutional rule | Compliance |
|---|---|
| §22 ADG graph-layer primary | ✅ — MVs/P-views confirmed populating; gate passes on `adg_indexed_04222026_2055.sqlite` |
| §5 ADG before T2/T3 | ✅ — parent plan drove wiring from ADG snapshot evidence |
| §8 Guardian exemption requires Author-Gate | ✅ — Author-Gate scored (0.88 vs 0.42), dominance rule applied, this ADR is the record |
| §15 Precise exception handling | ✅ — the lazy import catches `ImportError` specifically |
| §19 Mode separation | ✅ — this ADR documents a completed decision, not a plan |

---

## 6. References

- Plan: `.windsurf/plans/eval-meta-otel-gap-review-ef4a20.md`
- Plan: `.windsurf/plans/eval-meta-otel-deferred-completion-d6b4e0.md`
- Review: `docs/reports/plans/eval-meta-otel-gap-review.md`
- Commits: `9468dcb3ec` (initial wiring), `5c99fa635d` (μW-1 guardian + HITL + scenario), `11ee7a8644` (retrieval engine), `a3cca1afea` (W-D2 L_SL/L6 tracer wiring)
