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

- The `authority_boundary` / `capability_egress` / `write_sovereignty` ADG gates continue to flag these two imports. They will appear in every P0 remediation wave until the gates are taught about the ADR-028 exemption.
- Future maintainers must read this ADR when they see the guardian comment. Mitigation: guardian comment points at ADR-028 and the plan slug.

### 4.3 Follow-up work

- **[deferred]** Teach `check_authority_boundary.py` (and peers) to honor ADR-028: recognize the guardian comment pattern `allow-cross-layer-import` when the importing module is `apps_eval/integrations/meta_bus_publisher.py` and the target module is `system_learning.meta_learning.meta_learning_bus`.
- **[deferred]** Extend the pattern to any future publisher adapters (e.g., `apps_exec`, `apps_research`) under the same module prefix `apps_*/integrations/*`.

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
