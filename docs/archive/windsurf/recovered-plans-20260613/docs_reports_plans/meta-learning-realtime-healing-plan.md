# Meta-Learning Real-Time Healing — Gap Analysis & Implementation Plan

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

The current architecture applies meta-learning **post-fact** (after healing completes), never **at heal-time** (before or during the routing/invocation decision). This plan defines the gaps, the architectural constraints that govern what is allowed, and a 4-phase implementation to close every gap.

---

## Part 1 — Current Architecture (As-Is)

### Data Flow (Current)

```
HealingInput
    │
    ▼
route_healing_tier()          ← NO meta-learning input here
    │
    ▼
dispatch_healing()            ← NO meta-learning input here
    │
    ▼
invoker.invoke_*()            ← NO meta-learning input here
    │
    ▼
_emit_outcome()  ─────────►  HealingOutcomeSink (fire-and-forget)
                                    │
                                    ▼
                              HealingOutcomeAggregator
                                    │
                                    ▼
                              HealingConfigOptimizer (offline batch)
                                    │
                                    ▼
                              ThresholdAdjustmentProposal (PROPOSAL ONLY)
```

### Key Contracts Currently In Effect

| Contract | Location | Implication |
|---|---|---|
| `HEALING_CONFIDENCE_X = 0.75` and `HEALING_CONFIDENCE_Y = 0.40` are **IMMUTABLE** | `qwen_meta_learning.py:14-16` | Routing thresholds cannot be changed by meta-learning |
| Meta-learning proposals are **NO runtime behavior changes. NO mutation logic. NO automatic application.** | `meta_learning_types.py` | All meta-learning outputs are advisory artifacts only |
| `HealingOutcomeSink.emit()` is **fire-and-forget** | `healing_outcome_sink.py` | Outcome data is collected async after healing, not fed back synchronously |
| `_HISTORICAL_SUCCESS_RATES` is a **module-level stub dict** | `healing_tier_router.py:66` | Historical success rates exist but have NO live feed from meta-learning |
| `MetaLearningClient.retrieve_healing_patterns()` exists but is **NEVER called from dispatcher or router** | `meta_client.py:363` | Pattern retrieval infrastructure is built but not wired into healing path |
| `MetaLearningClientMixin.ml_recall_healing_pattern()` exists but is **NEVER used in L2.3** | `meta_learning_client_mixin.py:143` | The mixin exists on agents but not on the healing dispatcher |

---

## Part 2 — Gap Analysis

### Gap 1: `_HISTORICAL_SUCCESS_RATES` is a dead stub

**File:** `agentic_core/L2_execution/healers/healing_tier_router.py:66`

`_HISTORICAL_SUCCESS_RATES` is a plain `dict[str, float]` initialized to empty. `get_historical_success_rate()` always returns the neutral prior `0.50`. There is no mechanism to feed outcomes from the aggregator or meta-learning system back into this dict at heal-time.

**Effect:** The `WEIGHT_HISTORICAL_SUCCESS * historical_rate` term in `compute_heal_confidence()` is permanently fixed at `0.20 * 0.50 = 0.10` for every unrecognized error signature — it never improves.

---

### Gap 2: `MetaLearningClient.retrieve_healing_patterns()` is never called in the healing path

**File:** `agentic_core/L1_cognition/engines/meta_client.py:363`

The `MetaLearningClient` has a full `retrieve_healing_patterns()` method (Pinecone + Redis) and a `store_healing_pattern()` method. The `MetaLearningClientMixin` wraps these. But **neither is called anywhere in:**
- `healing_tier_dispatcher.py`
- `healing_tier_router.py`
- `qwen_meta_learning.py`

Retrieved patterns could inform routing decisions (which tier succeeded for similar errors in the past) and could influence `compute_heal_confidence()`.

---

### Gap 3: `HealingOutcomeAggregator` data never feeds back into the router

**File:** `system_learning/engines/healing_outcome_aggregator.py`

The aggregator builds `HealingOutcomeAggregateSnapshot` from emitted events. `HealingConfigOptimizer` then uses those snapshots to produce `ThresholdAdjustmentProposal` artifacts. But:
- The success-rate-per-error-signature data in the snapshot is never written back to `_HISTORICAL_SUCCESS_RATES`
- The meta-learning operator (`meta_learning_operator.py`) runs as a DRY_RUN offline batch
- No bridge exists between the aggregator's in-memory state and the router's `_HISTORICAL_SUCCESS_RATES`

---

### Gap 4: Pattern-matching confidence boost is absent at routing time

**File:** `system_learning/engines/pattern_analysis_engine.py`, `system_learning/engines/healing_config_optimizer.py`

`PatternAnalysisEngine.analyze()` detects recurring failure motifs from historical embeddings. `HealingConfigOptimizer.propose_threshold_adjustments_with_embeddings()` applies a bounded embedding influence to confidence scores. However, both are:
- Informational-only ("C0 influence only")
- Used only in the offline batch pipeline
- Never invoked during live `dispatch_healing()` calls

---

### Gap 5: Qwen meta-learning updates (`update_qwen_confidence_prior`) are disconnected from the router

**File:** `agentic_core/L2_execution/healers/qwen_meta_learning.py`

`update_qwen_confidence_prior()` is supposed to update historical success rates for Qwen invocations. But:
- It is never called after an invocation in `dispatch_healing()` or `_emit_outcome()`
- It updates `_HISTORICAL_SUCCESS_RATES` via `set_historical_success_rate()` — but only when explicitly invoked
- There is no callback or hook in the dispatcher to call this after a Qwen invocation

---

### Gap 6: `MetaLearningBus` is idle with respect to healing

**File:** `agentic_core/L0_routing/meta_control/meta_learning_bus.py`

`MetaLearningBus` is a FIFO queue for `MetaLearningChangePackage` objects. It exists to relay change packages to an injected apply function. But:
- It carries no connection to `_HISTORICAL_SUCCESS_RATES` or `compute_heal_confidence()`
- No code path in the healing subsystem enqueues packages to the bus after outcomes are received

---

## Part 3 — Architecture Constraints (What Cannot Change)

These are hard-wired constraints that any implementation must respect:

1. **`HEALING_CONFIDENCE_X` and `HEALING_CONFIDENCE_Y` are IMMUTABLE.** Meta-learning cannot modify routing thresholds.
2. **`MetaLearningProposalArtifact` is proposal-only.** No automatic application.
3. **`dispatch_healing()` must remain synchronous and deterministic.** No async I/O in the routing hot path.
4. **Allowed meta-learning operations** (per `qwen_meta_learning.py`): historical success rate updates, failure class prior adjustments, tool readiness certainty updates.
5. **Layer model:** L2 (`healing_tier_dispatcher`, `healing_tier_router`) must not directly import L4 state. Cross-layer access goes through seams.
6. **`IMMUTABLE_COMPONENTS`** (per `meta_learning_types.py`): `guardian_contract`, `capability_enforcement`, `inventory_schema`, `evidence_hashing`, `territory_map` — none of these may be targeted.
7. **All code analysis must use AST parsing.** Regex/grep forbidden for structural logic.
8. **No `pwsh`/`powershell` in evidence runners.** Use `subprocess.run(argv, shell=False)`.

---

## Part 4 — Target Architecture (To-Be)

```
HealingInput
    │
    ├──► [Phase 1] RealTimeMetaPriorProvider.get_prior(error_signature)
    │         └── reads from L4-backed HealingSuccessRateStore
    │                   ▲
    │                   │ [Phase 2] post-outcome write-back
    │                   │
    ▼
route_healing_tier()          ← now uses live historical success rates
    │
    ├──► [Phase 3] HealingPatternAdvisor.advise(healing_input)
    │         └── calls MetaLearningClient.retrieve_healing_patterns()
    │         └── returns tier_hint + confidence_boost (bounded, advisory)
    │
    ▼
dispatch_healing()
    │
    ├──► invoker.invoke_*()
    │
    ├──► [Phase 2] update_qwen_confidence_prior() (if QWEN tier)
    │
    ├──► _emit_outcome()  ────►  HealingOutcomeSink
    │                                   │
    │                                   ▼ [Phase 2]
    │                            OutcomeWriteBackHook
    │                                   │
    │                                   ▼
    │                            HealingSuccessRateStore.update()
    │                                   ▲
    │                                   │
    └── feeds back to RealTimeMetaPriorProvider ─┘
    │
    └──► [Phase 4] audit: MetaLearningBus.enqueue(change_package)
```

---

## Part 5 — Implementation Phases

---

### Phase 1 — Live Prior Provider: Wire `_HISTORICAL_SUCCESS_RATES` to a Real-Time Store

**Objective:** Replace the dead module-level stub with a seam-injected `RealTimeMetaPriorProvider` so that `compute_heal_confidence()` gets live historical success rates.

**Scope (N=3 files):**
- `agentic_core/L2_execution/healers/healing_tier_router.py` — inject provider
- `system_learning/ports/meta_prior_provider.py` — new Protocol (seam)
- `system_learning/engines/healing_success_rate_store.py` — new concrete store

---

#### File Diff 1: `system_learning/ports/meta_prior_provider.py` (NEW)

```python
"""L2.3 Meta-Prior Provider Port — seam for injecting live success-rate priors.

This port is the ONLY allowed path for meta-learning data to enter the
heal-time routing computation. It is read-only from the perspective of L2.3.

Contracts:
- get_prior() MUST be synchronous and deterministic given the same store state.
- Returns float in [0.0, 1.0].  Default neutral prior = 0.50.
- NO side effects. NO writes. NO imports of L4 state directly.
"""

from __future__ import annotations

from typing import Protocol

_NEUTRAL_PRIOR: float = 0.50


class MetaPriorProvider(Protocol):
    """Read-only seam for retrieving heal-time meta-learning priors."""

    def get_prior(self, error_signature: str) -> float:
        """Return historical success rate prior for error_signature.

        Parameters
        ----------
        error_signature : str
            Deterministic error class identifier from HealingInput.

        Returns
        -------
        float
            Prior in [0.0, 1.0].  Returns _NEUTRAL_PRIOR if unknown.
        """
        ...


class NeutralMetaPriorProvider:
    """Fallback provider that always returns the neutral prior.

    Used when no L4-backed store is available (e.g., cold start, test isolation).
    """

    def get_prior(self, error_signature: str) -> float:  # noqa: ARG002
        return _NEUTRAL_PRIOR


__all__ = ["MetaPriorProvider", "NeutralMetaPriorProvider", "_NEUTRAL_PRIOR"]
```

---

#### File Diff 2: `system_learning/engines/healing_success_rate_store.py` (NEW)

```python
"""Healing Success Rate Store — in-memory store with atomic update semantics.

Backed by a dict[str, float].  In production this store is populated by
OutcomeWriteBackHook (Phase 2).  In tests it can be seeded directly.

Layer contract:
- Lives in system_learning (L6 / system_learning layer).
- Exposed to L2.3 only via the MetaPriorProvider seam in system_learning/ports/.
- MUST NOT import agentic_core modules.
"""

from __future__ import annotations

_NEUTRAL_PRIOR: float = 0.50
_MIN_SAMPLE_SIZE: int = 5  # minimum observations before prior is trusted


class HealingSuccessRateStore:
    """Thread-safe*, deterministic store of per-signature success rates.

    (* single-threaded for now; locking deferred to Phase 2b if needed)

    Each entry is a running average updated with each new outcome.
    """

    def __init__(self) -> None:
        self._rates: dict[str, float] = {}
        self._counts: dict[str, int] = {}

    def get_prior(self, error_signature: str) -> float:
        """Return the current success-rate prior for error_signature.

        Returns _NEUTRAL_PRIOR when fewer than _MIN_SAMPLE_SIZE outcomes
        are available (dampening: avoid over-weighting early noisy data).
        """
        count = self._counts.get(error_signature, 0)
        if count < _MIN_SAMPLE_SIZE:
            return _NEUTRAL_PRIOR
        return self._rates.get(error_signature, _NEUTRAL_PRIOR)

    def record_outcome(self, error_signature: str, success: bool) -> None:
        """Update the running success-rate average with a new outcome.

        Uses exponential moving average with alpha=0.1 after initial window.
        Before _MIN_SAMPLE_SIZE observations: simple cumulative average.

        Parameters
        ----------
        error_signature : str
            The deterministic error class identifier.
        success : bool
            Whether the heal attempt succeeded.
        """
        count = self._counts.get(error_signature, 0)
        current = self._rates.get(error_signature, _NEUTRAL_PRIOR)
        outcome_value = 1.0 if success else 0.0

        if count < _MIN_SAMPLE_SIZE:
            # Cumulative average during warm-up
            new_rate = (current * count + outcome_value) / (count + 1)
        else:
            # Exponential moving average
            alpha = 0.10
            new_rate = round((1.0 - alpha) * current + alpha * outcome_value, 6)

        self._rates[error_signature] = new_rate
        self._counts[error_signature] = count + 1

    def get_all(self) -> dict[str, float]:
        """Return a snapshot of all current priors (for audit/observability)."""
        return dict(self._rates)

    def get_counts(self) -> dict[str, int]:
        """Return a snapshot of all observation counts."""
        return dict(self._counts)

    def reset(self) -> None:
        """Clear all state (for testing only)."""
        self._rates.clear()
        self._counts.clear()


# Module-level singleton (injectable in tests via direct mutation)
_default_store: HealingSuccessRateStore | None = None


def get_default_store() -> HealingSuccessRateStore:
    """Return the process-global default store (lazy-initialized)."""
    global _default_store
    if _default_store is None:
        _default_store = HealingSuccessRateStore()
    return _default_store


def reset_default_store() -> None:
    """[TESTING ONLY] Reset the process-global store."""
    global _default_store
    _default_store = None


__all__ = [
    "HealingSuccessRateStore",
    "get_default_store",
    "reset_default_store",
    "_MIN_SAMPLE_SIZE",
    "_NEUTRAL_PRIOR",
]
```

---

#### File Diff 3: `agentic_core/L2_execution/healers/healing_tier_router.py` (MODIFY)

**Change:** Add `meta_prior_provider` parameter to `compute_heal_confidence()` and `route_healing_tier()`. When not provided, fall back to module-level `_HISTORICAL_SUCCESS_RATES` (backward-compatible).

```diff
# --- BEFORE (lines 62-75) ---
# Historical success rate store (stub — in production backed by L4)
_HISTORICAL_SUCCESS_RATES: dict[str, float] = {}
_NEUTRAL_PRIOR = 0.50


def get_historical_success_rate(error_signature: str) -> float:
    """Look up historical success rate for an error signature.

    Returns neutral prior (0.50) if no history is available.
    """
    return _HISTORICAL_SUCCESS_RATES.get(error_signature, _NEUTRAL_PRIOR)


def set_historical_success_rate(error_signature: str, rate: float) -> None:
    """Record historical success rate (for testing / L4 integration)."""
    if not (0.0 <= rate <= 1.0):
        raise ValueError(f"rate must be in [0.0, 1.0], got {rate}")
    _HISTORICAL_SUCCESS_RATES[error_signature] = rate

# --- AFTER ---
# Historical success rate store (stub preserved for backward-compat + test seeding)
_HISTORICAL_SUCCESS_RATES: dict[str, float] = {}
_NEUTRAL_PRIOR = 0.50


def get_historical_success_rate(
    error_signature: str,
    meta_prior_provider: "MetaPriorProvider | None" = None,
) -> float:
    """Look up historical success rate for an error signature.

    Priority:
    1. meta_prior_provider.get_prior() — live store (Phase 1+)
    2. _HISTORICAL_SUCCESS_RATES — module-level stub (legacy / tests)
    3. _NEUTRAL_PRIOR (0.50) — cold-start fallback

    Returns neutral prior (0.50) if no history is available.
    """
    if meta_prior_provider is not None:
        return meta_prior_provider.get_prior(error_signature)
    return _HISTORICAL_SUCCESS_RATES.get(error_signature, _NEUTRAL_PRIOR)
```

```diff
# --- BEFORE: compute_heal_confidence signature ---
def compute_heal_confidence(healing_input: HealingInput) -> tuple[float, list[str]]:

# --- AFTER ---
def compute_heal_confidence(
    healing_input: HealingInput,
    meta_prior_provider: "MetaPriorProvider | None" = None,
) -> tuple[float, list[str]]:
    ...
    # 3. Historical success rate  ← CHANGED
    historical_rate = get_historical_success_rate(
        healing_input.error_signature,
        meta_prior_provider=meta_prior_provider,
    )
```

```diff
# --- BEFORE: route_healing_tier signature ---
def route_healing_tier(
    healing_input: HealingInput,
    config: HealingTierConfig,
) -> HealingDecision:

# --- AFTER ---
def route_healing_tier(
    healing_input: HealingInput,
    config: HealingTierConfig,
    *,
    meta_prior_provider: "MetaPriorProvider | None" = None,
) -> HealingDecision:
    ...
    heal_confidence, reason_codes = compute_heal_confidence(
        healing_input,
        meta_prior_provider=meta_prior_provider,
    )
```

**Import addition at top of file (TYPE_CHECKING guard, no circular import):**

```python
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from system_learning.ports.meta_prior_provider import MetaPriorProvider
```

---

### Phase 2 — Outcome Write-Back Hook: Feed Results Into the Live Store

**Objective:** After each healing invocation, write the outcome back into `HealingSuccessRateStore` so that subsequent calls to `get_historical_success_rate()` benefit immediately.

**Scope (N=2 files):**
- `system_learning/ports/outcome_write_back_hook.py` — new Protocol (seam)
- `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` — wire hook into `dispatch_healing()`

---

#### File Diff 4: `system_learning/ports/outcome_write_back_hook.py` (NEW)

```python
"""Outcome Write-Back Hook Port — seam for real-time meta-learning feedback.

Called by dispatch_healing() immediately after an invocation completes.
Implementations write to HealingSuccessRateStore and call
update_qwen_confidence_prior() (for QWEN tier).

Constraints:
- MUST be synchronous and fast (no network I/O in the hot path).
- MUST NOT raise exceptions (swallow internally and log).
- MUST NOT modify HEALING_CONFIDENCE_X or HEALING_CONFIDENCE_Y.
- MUST NOT mutate healing_input or decision.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord
    from agentic_core.L2_execution.healers.healing_tier_types import (
        HealingDecision,
        HealingInput,
    )


class OutcomeWriteBackHook(Protocol):
    """Synchronous write-back seam called after each heal invocation."""

    def on_outcome(
        self,
        *,
        healing_input: "HealingInput",
        decision: "HealingDecision",
        record: "InvocationRecord",
        success: bool,
    ) -> None:
        """Handle a completed healing outcome.

        Parameters
        ----------
        healing_input : HealingInput
            The original structured failure context.
        decision : HealingDecision
            The routing decision that was executed.
        record : InvocationRecord
            The invocation trace record.
        success : bool
            Whether the heal attempt succeeded.
        """
        ...


class DefaultOutcomeWriteBackHook:
    """Default hook: writes success rate to HealingSuccessRateStore and
    calls update_qwen_confidence_prior() for QWEN invocations.
    """

    def __init__(self, store=None) -> None:
        if store is None:
            from system_learning.engines.healing_success_rate_store import get_default_store
            store = get_default_store()
        self._store = store

    def on_outcome(
        self,
        *,
        healing_input,
        decision,
        record,
        success: bool,
    ) -> None:
        try:
            self._store.record_outcome(healing_input.error_signature, success)
        except Exception:
            pass  # Never let write-back crash the dispatch path

        # Qwen-specific prior update (per qwen_meta_learning contract)
        from agentic_core.L2_execution.healers.healing_tier_types import HealingTier
        if decision.tier == HealingTier.QWEN_VLLM:
            try:
                from agentic_core.L2_execution.healers.qwen_meta_learning import (
                    update_qwen_confidence_prior,
                )
                update_qwen_confidence_prior(healing_input.error_signature, success)
            except Exception:
                pass  # Never crash dispatch path


__all__ = ["OutcomeWriteBackHook", "DefaultOutcomeWriteBackHook"]
```

---

#### File Diff 5: `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` (MODIFY)

**Change:** Add `outcome_write_back_hook` and `meta_prior_provider` to `dispatch_healing()`. Wire the hook call after the invocation. Wire the provider into `route_healing_tier()`.

```diff
# --- BEFORE: dispatch_healing signature ---
def dispatch_healing(
    healing_input: HealingInput,
    config: HealingTierConfig,
    *,
    invoker: HealingProviderInvoker | None = None,
    agent_name: str = "",
    outcome_sink: HealingOutcomeSink | None = None,
    timestamp_utc: int | None = None,
    resource_predictor: ResourcePredictor | None = None,
    rollback_refiner: RollbackRefiner | None = None,
) -> tuple[HealingDecision, InvocationRecord]:

# --- AFTER ---
def dispatch_healing(
    healing_input: HealingInput,
    config: HealingTierConfig,
    *,
    invoker: HealingProviderInvoker | None = None,
    agent_name: str = "",
    outcome_sink: HealingOutcomeSink | None = None,
    timestamp_utc: int | None = None,
    resource_predictor: ResourcePredictor | None = None,
    rollback_refiner: RollbackRefiner | None = None,
    meta_prior_provider: MetaPriorProvider | None = None,
    outcome_write_back_hook: OutcomeWriteBackHook | None = None,
) -> tuple[HealingDecision, InvocationRecord]:
```

```diff
# --- BEFORE: inside dispatch_healing body ---
    decision = route_healing_tier(healing_input, config)

# --- AFTER ---
    decision = route_healing_tier(
        healing_input,
        config,
        meta_prior_provider=meta_prior_provider,
    )
```

```diff
# --- BEFORE: inside dispatch_healing finally block ---
    finally:
        if outcome_sink is not None and timestamp_utc is not None:
            _emit_outcome(...)

# --- AFTER ---
    finally:
        if outcome_sink is not None and timestamp_utc is not None:
            _emit_outcome(...)
        # Phase 2: Real-time write-back into meta-learning store
        if outcome_write_back_hook is not None:
            outcome_write_back_hook.on_outcome(
                healing_input=healing_input,
                decision=decision,
                record=record,   # note: may be unset if exception; guard below
                success=success,
            )
```

**Note on `record` availability:** In the current code, `record` is only bound on the success path. The `finally` block needs a guard. The implementation must initialize `record: InvocationRecord | None = None` before the try block and only pass it when set.

**TYPE_CHECKING additions:**
```python
if TYPE_CHECKING:
    from system_learning.ports.meta_prior_provider import MetaPriorProvider
    from system_learning.ports.outcome_write_back_hook import OutcomeWriteBackHook
```

---

### Phase 3 — Pattern Advisor: Inject Semantic Pattern Hints at Routing Time

**Objective:** Wire `MetaLearningClient.retrieve_healing_patterns()` into `dispatch_healing()` as an optional advisory influence on the routing decision (tier hint + bounded confidence boost). This is the "real-time meta-learning" for pattern-based correction.

**Scope (N=3 files):**
- `system_learning/ports/healing_pattern_advisor.py` — new Protocol (seam)
- `system_learning/engines/default_healing_pattern_advisor.py` — new concrete adapter
- `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` — wire into `dispatch_healing()`

---

#### File Diff 6: `system_learning/ports/healing_pattern_advisor.py` (NEW)

```python
"""Healing Pattern Advisor Port — seam for semantic pattern hints at routing time.

Wraps MetaLearningClient.retrieve_healing_patterns() behind a deterministic
protocol so that L2.3 dispatcher can use it without a direct L2→L1 import.

Contracts:
- MUST be synchronous (reads from in-process cache first).
- Returns HealingPatternAdvice (immutable).  Advisory only.
- MUST NOT return HEALING_CONFIDENCE_X or HEALING_CONFIDENCE_Y modifications.
- Confidence boost is bounded by PATTERN_BOOST_CAP = 0.10 (additive, capped).
- tier_hint is advisory only; router STILL applies threshold routing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

# Bounded influence cap (matches system_learning's "C0 informational context" philosophy)
PATTERN_BOOST_CAP: float = 0.10


@dataclass(frozen=True, slots=True)
class HealingPatternAdvice:
    """Advisory output from the pattern advisor.

    Attributes
    ----------
    tier_hint : str | None
        The tier that succeeded for similar historical patterns, or None.
    confidence_boost : float
        Additive boost in [0.0, PATTERN_BOOST_CAP] to apply to heal_confidence.
        0.0 when no reliable pattern is found.
    pattern_found : bool
        True if at least one pattern above similarity threshold was found.
    similarity_score : float
        Similarity of the best matched pattern. 0.0 if no pattern found.
    source : str
        Identifier of the provider (for audit/reason codes).
    """

    tier_hint: str | None
    confidence_boost: float
    pattern_found: bool
    similarity_score: float
    source: str


class HealingPatternAdvisor(Protocol):
    """Seam for retrieving healing pattern advice before routing."""

    def advise(
        self,
        *,
        error_signature: str,
        failure_type: str,
    ) -> HealingPatternAdvice:
        """Return advisory pattern hint for the given failure context.

        Parameters
        ----------
        error_signature : str
            Deterministic error class identifier.
        failure_type : str
            Failure category (e.g., 'syntax_error', 'import_cycle').

        Returns
        -------
        HealingPatternAdvice
            Advisory output. pattern_found=False when nothing relevant is found.
        """
        ...


class NullHealingPatternAdvisor:
    """No-op advisor: always returns no pattern found."""

    def advise(self, *, error_signature: str, failure_type: str) -> HealingPatternAdvice:
        return HealingPatternAdvice(
            tier_hint=None,
            confidence_boost=0.0,
            pattern_found=False,
            similarity_score=0.0,
            source="null_advisor",
        )


__all__ = [
    "HealingPatternAdvice",
    "HealingPatternAdvisor",
    "NullHealingPatternAdvisor",
    "PATTERN_BOOST_CAP",
]
```

---

#### File Diff 7: `system_learning/engines/default_healing_pattern_advisor.py` (NEW)

```python
"""Default Healing Pattern Advisor — wraps MetaLearningClient for L2.3.

Translates MetaLearningClient.retrieve_healing_patterns() output into
a bounded HealingPatternAdvice without exposing L1 internals to L2.3.

Bounded influence: confidence_boost = min(similarity - threshold, PATTERN_BOOST_CAP)
"""

from __future__ import annotations

import logging

from system_learning.ports.healing_pattern_advisor import (
    PATTERN_BOOST_CAP,
    HealingPatternAdvice,
)

logger = logging.getLogger(__name__)

_MIN_SIMILARITY: float = 0.85


class DefaultHealingPatternAdvisor:
    """Concrete advisor backed by MetaLearningClient (Pinecone + Redis)."""

    def __init__(self, ml_client=None, min_similarity: float = _MIN_SIMILARITY) -> None:
        self._ml_client = ml_client
        self._min_similarity = min_similarity

    def _ensure_client(self):
        if self._ml_client is None:
            try:
                from agentic_core.L1_cognition.engines.meta_client import get_meta_learning_client
                self._ml_client = get_meta_learning_client()
            except Exception:
                self._ml_client = None

    def advise(
        self,
        *,
        error_signature: str,
        failure_type: str,
    ) -> HealingPatternAdvice:
        self._ensure_client()
        if self._ml_client is None:
            return HealingPatternAdvice(
                tier_hint=None,
                confidence_boost=0.0,
                pattern_found=False,
                similarity_score=0.0,
                source="default_advisor:no_client",
            )

        try:
            violation = {
                "type": failure_type,
                "message": error_signature,
                "path": "",
            }
            patterns = self._ml_client.retrieve_healing_patterns(
                violation,
                domain="agentic_core",
                top_k=1,
                min_similarity=self._min_similarity,
            )
        except Exception as exc:
            logger.debug("Pattern retrieval failed: %s", exc)
            return HealingPatternAdvice(
                tier_hint=None,
                confidence_boost=0.0,
                pattern_found=False,
                similarity_score=0.0,
                source="default_advisor:retrieval_error",
            )

        if not patterns:
            return HealingPatternAdvice(
                tier_hint=None,
                confidence_boost=0.0,
                pattern_found=False,
                similarity_score=0.0,
                source="default_advisor:no_match",
            )

        best = patterns[0]
        sim = getattr(best, "similarity_score", 0.0)
        strategy = getattr(best, "healing_strategy", {}) or {}
        tier_hint = strategy.get("tier") if isinstance(strategy, dict) else None

        # Bounded confidence boost
        boost = round(min(max(sim - self._min_similarity, 0.0), PATTERN_BOOST_CAP), 6)

        return HealingPatternAdvice(
            tier_hint=tier_hint,
            confidence_boost=boost,
            pattern_found=True,
            similarity_score=round(sim, 6),
            source="default_advisor:pinecone",
        )


__all__ = ["DefaultHealingPatternAdvisor"]
```

---

#### File Diff 8: `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` — Phase 3 additions

**Change:** Add `pattern_advisor` parameter to `dispatch_healing()`. Apply advisory advice after routing, adjusting `heal_confidence` by `confidence_boost` (clamped), and appending to `reason_codes`. The tier selection is re-evaluated with the boosted confidence **only if** the boost moves the confidence across a threshold boundary (preserving immutability of threshold values).

```diff
# New parameter added to dispatch_healing():
    pattern_advisor: HealingPatternAdvisor | None = None,

# After route_healing_tier() call, before invocation:
    if pattern_advisor is not None:
        advice = pattern_advisor.advise(
            error_signature=healing_input.error_signature,
            failure_type=healing_input.failure_type,
        )
        if advice.pattern_found and advice.confidence_boost > 0.0:
            # Re-evaluate routing with boosted confidence
            boosted_confidence = min(
                1.0,
                round(decision.heal_confidence + advice.confidence_boost, 6),
            )
            boosted_reason_codes = list(decision.reason_codes) + [
                f"pattern_boost={advice.confidence_boost:.6f}",
                f"pattern_similarity={advice.similarity_score:.6f}",
                f"pattern_source={advice.source}",
            ]
            # Re-apply threshold routing with boosted confidence (thresholds are immutable)
            if boosted_confidence >= config.heal_confidence_x and decision.tier != HealingTier.LOCAL_AGENT:
                boosted_reason_codes.append(f"pattern_boost_promoted_to:LOCAL_AGENT")
                decision = HealingDecision(
                    heal_confidence=boosted_confidence,
                    tier=HealingTier.LOCAL_AGENT,
                    reason_codes=tuple(boosted_reason_codes),
                )
            elif boosted_confidence >= config.heal_confidence_y and decision.tier == HealingTier.GEMINI_2_5_PRO:
                boosted_reason_codes.append(f"pattern_boost_promoted_to:QWEN_VLLM")
                decision = HealingDecision(
                    heal_confidence=boosted_confidence,
                    tier=HealingTier.QWEN_VLLM,
                    reason_codes=tuple(boosted_reason_codes),
                )
            else:
                # boost recorded in reason_codes but no tier change
                decision = HealingDecision(
                    heal_confidence=boosted_confidence,
                    tier=decision.tier,
                    reason_codes=tuple(boosted_reason_codes),
                )
```

**TYPE_CHECKING addition:**
```python
if TYPE_CHECKING:
    from system_learning.ports.healing_pattern_advisor import HealingPatternAdvisor
```

---

### Phase 4 — Observability & Audit: MetaLearningBus Enqueue on Each Outcome

**Objective:** After each healing outcome, enqueue a `MetaLearningChangePackage` onto the `MetaLearningBus` so that downstream operators (`meta_learning_operator.py`) can observe real-time outcome signals without breaking the proposal-only architecture.

**Scope (N=2 files):**
- `system_learning/ports/meta_outcome_bus_hook.py` — new Protocol (seam)
- `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` — wire into `dispatch_healing()`

---

#### File Diff 9: `system_learning/ports/meta_outcome_bus_hook.py` (NEW)

```python
"""Meta Outcome Bus Hook — seam for enqueuing outcomes onto MetaLearningBus.

Called by dispatch_healing() after each invocation.  Enqueues an immutable
MetaLearningChangePackage onto the bus for downstream consumption.

Contracts:
- MUST be synchronous and non-blocking.
- MUST NOT raise exceptions.
- MUST NOT directly activate any change package (proposal-only).
- Bus consumers are responsible for gate validation before applying packages.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord
    from agentic_core.L2_execution.healers.healing_tier_types import (
        HealingDecision,
        HealingInput,
    )


class MetaOutcomeBusHook(Protocol):
    """Seam for publishing outcomes onto the MetaLearningBus."""

    def publish(
        self,
        *,
        healing_input: "HealingInput",
        decision: "HealingDecision",
        record: "InvocationRecord | None",
        success: bool,
        timestamp_utc: int,
    ) -> None:
        """Enqueue a heal outcome as a MetaLearningChangePackage.

        Parameters
        ----------
        healing_input : HealingInput
            Original failure context.
        decision : HealingDecision
            Routing decision that was executed.
        record : InvocationRecord | None
            Invocation trace (None if exception occurred before record was created).
        success : bool
            Whether the heal attempt succeeded.
        timestamp_utc : int
            Deterministic timestamp (injected by caller).
        """
        ...


class DefaultMetaOutcomeBusHook:
    """Default hook: wraps MetaLearningBus.enqueue() with a change package."""

    def __init__(self, bus=None) -> None:
        self._bus = bus

    def _ensure_bus(self):
        if self._bus is None:
            try:
                from agentic_core.L0_routing.meta_control.meta_learning_bus import MetaLearningBus
                self._bus = MetaLearningBus()
            except Exception:
                pass

    def publish(
        self,
        *,
        healing_input,
        decision,
        record,
        success: bool,
        timestamp_utc: int,
    ) -> None:
        self._ensure_bus()
        if self._bus is None:
            return
        try:
            from agentic_core.L0_routing.meta_control.meta_learning_bus import MetaLearningChangePackage
            pkg = MetaLearningChangePackage.create(
                trace_id=healing_input.trace_id,
                kind="HEAL_OUTCOME",
                payload={
                    "error_signature": healing_input.error_signature,
                    "failure_type": healing_input.failure_type,
                    "tier": decision.tier.value,
                    "heal_confidence": decision.heal_confidence,
                    "success": success,
                    "timestamp_utc": timestamp_utc,
                },
            )
            self._bus.enqueue(pkg)
        except Exception:
            pass  # Never crash dispatch path


__all__ = ["MetaOutcomeBusHook", "DefaultMetaOutcomeBusHook"]
```

---

#### File Diff 10: `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` — Phase 4 additions

```diff
# New parameter added to dispatch_healing():
    meta_outcome_bus_hook: MetaOutcomeBusHook | None = None,

# In finally block, after existing emit_outcome and write-back:
        if meta_outcome_bus_hook is not None and timestamp_utc is not None:
            meta_outcome_bus_hook.publish(
                healing_input=healing_input,
                decision=decision,
                record=record,
                success=success,
                timestamp_utc=timestamp_utc,
            )
```

---

## Part 6 — Test Coverage Requirements

Each phase requires:

### Phase 1 Tests

**File:** `tests/agentic_core/L2_execution/healers/test_meta_prior_provider.py` (NEW)
- `test_neutral_prior_provider_always_returns_050`
- `test_healing_success_rate_store_warm_up_uses_neutral_prior`
- `test_healing_success_rate_store_records_outcomes_and_updates_rate`
- `test_healing_success_rate_store_ema_after_warmup`
- `test_compute_heal_confidence_uses_injected_prior`
- `test_route_healing_tier_uses_injected_prior`
- `test_route_healing_tier_backward_compat_no_provider`

### Phase 2 Tests

**File:** `tests/agentic_core/L2_execution/healers/test_outcome_write_back.py` (NEW)
- `test_default_write_back_hook_records_success`
- `test_default_write_back_hook_records_failure`
- `test_write_back_hook_calls_qwen_prior_for_qwen_tier`
- `test_write_back_hook_does_not_crash_on_exception`
- `test_dispatch_healing_calls_write_back_hook`
- `test_dispatch_healing_backward_compat_no_hook`

### Phase 3 Tests

**File:** `tests/agentic_core/L2_execution/healers/test_healing_pattern_advisor.py` (NEW)
- `test_null_advisor_returns_no_pattern`
- `test_default_advisor_no_client_returns_no_pattern`
- `test_default_advisor_returns_pattern_with_bounded_boost`
- `test_boost_capped_at_pattern_boost_cap`
- `test_dispatch_healing_promotes_tier_on_pattern_boost`
- `test_dispatch_healing_does_not_exceed_confidence_1_0`
- `test_immutable_thresholds_not_modified_by_pattern_boost`

### Phase 4 Tests

**File:** `tests/agentic_core/L2_execution/healers/test_meta_outcome_bus_hook.py` (NEW)
- `test_default_bus_hook_enqueues_package`
- `test_bus_hook_package_has_correct_payload`
- `test_bus_hook_does_not_crash_on_exception`
- `test_dispatch_healing_publishes_to_bus`
- `test_dispatch_healing_backward_compat_no_bus_hook`

---

## Part 7 — Immutable Constraints Summary (Non-Negotiable)

| Item | Value | Why |
|---|---|---|
| `HEALING_CONFIDENCE_X` | `0.75` | Cannot be changed by meta-learning |
| `HEALING_CONFIDENCE_Y` | `0.40` | Cannot be changed by meta-learning |
| `PATTERN_BOOST_CAP` | `0.10` | Bounded additive influence |
| `_MIN_SAMPLE_SIZE` | `5` | Dampening before trust |
| EMA alpha | `0.10` | Slow adaptation |
| All new parameters | keyword-only, default `None` | Full backward compatibility |
| All new artifacts | frozen dataclasses | Immutable after creation |
| No direct L4 imports in L2 | enforced by layer model | Cross-layer access via seams only |

---

## Part 8 — Phase Execution Order

| Phase | N Files | Primary Gap Closed |
|---|---|---|
| Phase 1 | 3 | Gap 1, Gap 3: Live prior store + router injection |
| Phase 2 | 2 | Gap 2, Gap 5: Post-invocation write-back + Qwen prior |
| Phase 3 | 3 | Gap 2 (pattern path), Gap 4: Pattern advisor at routing time |
| Phase 4 | 2 | Gap 6: MetaLearningBus observability |
| **Total** | **10** | **All 6 gaps closed** |

---

## Part 9 — Forbidden Actions (Reminder)

- Do NOT modify `HEALING_CONFIDENCE_X` or `HEALING_CONFIDENCE_Y`.
- Do NOT call `apply_meta_learning_rollout()` from within the dispatch path.
- Do NOT add async I/O to `route_healing_tier()` or `compute_heal_confidence()`.
- Do NOT import `agentic_core` from `system_learning` (boundary violation).
- Do NOT add inline pastes of command output in evidence files.
- Do NOT use `pwsh` / `powershell` in runners.
- Do NOT use regex for structural code analysis (use AST).

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

