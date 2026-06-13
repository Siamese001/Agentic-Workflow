# Meta-Learning Real-Time Healing — Hardened v3 Consolidated Plan

Consolidated implementation plan integrating all sovereignty, determinism, and C0 hardenings to close 6 meta-learning gaps while preserving architectural invariants.

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


## Audit Summary

Two rounds of sovereignty audit identified and corrected:

1. **C0 tier mutation** — pattern-derived boost was capable of promoting tiers; now advisory-only metadata, `heal_confidence` is never overwritten
2. **Bus instantiation in L2** — `MetaLearningBus()` was constructed ad-hoc; now strictly injected from L0, default is `NullBus`
3. **Cross-layer imports** — `DefaultHealingPatternAdvisor` imported L1 directly; now protocol-injected only
4. **Replay divergence** — `HealingSuccessRateStore` lacked version surface; now emits `store_state_hash`, exports deterministic snapshot
5. **Silent failure** — write-back swallowed exceptions; now emits structured telemetry
6. **Write-back retry guard** — incorrectly skipped on retry >= 3; removed (write-back always executes, escalation applies only to routing)
7. **Oscillation guard** — was documented but unspecified; now has fixed N/M/K constants
8. **Process model** — undefined; now declares single-process invariant with pid guard
9. **Bus proposal_only** — not enforced in payload; now hard-set `proposal_only=True`

---

## Gaps Closed

| Gap | Description | Closed By |
|---|---|---|
| Gap 1 | `_HISTORICAL_SUCCESS_RATES` dead stub | Phase 1 |
| Gap 2 | `MetaLearningClient.retrieve_healing_patterns()` never called | Phase 3 |
| Gap 3 | `HealingOutcomeAggregator` never feeds back to router | Phase 1 + 2 |
| Gap 4 | Pattern-matching confidence boost absent at routing | Phase 3 (advisory) |
| Gap 5 | `update_qwen_confidence_prior()` disconnected | Phase 2 |
| Gap 6 | `MetaLearningBus` idle for healing | Phase 4 |

---

## Architecture Constraints (Immutable)

| Constraint | Value |
|---|---|
| `HEALING_CONFIDENCE_X` | `0.75` (immutable) |
| `HEALING_CONFIDENCE_Y` | `0.40` (immutable) |
| C0 embedding influence | Informational-only; MUST NOT mutate routing tiers or `heal_confidence` |
| `retry_count >= max_heal_retries` | Forces `GEMINI_2_5_PRO` unconditionally |
| Layer model | L2 must not import L1/L4 directly; seams only |
| Meta-learning | Proposal-only; no automatic application |
| Dispatch path | Synchronous, deterministic; no async I/O |

---

## Revised Target Architecture

```
HealingInput
    │
    ├──► [Phase 1] MetaPriorProvider.get_prior(error_signature)
    │         └── reads from deterministic HealingSuccessRateStore
    │                   ▲
    │                   │ [Phase 2] write-back with telemetry
    │                   │
    ▼
route_healing_tier()    ← pure f(core_signals, historical_prior, retry_count)
    │                      pattern advice CANNOT change tier
    ▼
dispatch_healing()
    │
    ├──► [Phase 3] HealingPatternAdvisor.advise() → metadata only
    │         └── appends reason_codes (no tier/confidence mutation)
    │
    ├──► invoker.invoke_*()
    │
    ├──► [Phase 2] OutcomeWriteBackHook.on_outcome() (always executes)
    │         ├── HealingSuccessRateStore.record_outcome()
    │         └── update_qwen_confidence_prior() (if QWEN tier)
    │
    ├──► _emit_outcome() → HealingOutcomeSink (existing)
    │
    └──► [Phase 4] MetaOutcomeBusHook.publish() (injected bus)
              └── proposal_only=True ChangePackage
```

---

# Phase 1 — Deterministic Prior Cache

**Objective:** Replace dead `_HISTORICAL_SUCCESS_RATES` stub with seam-injected `MetaPriorProvider` backed by a deterministic, replay-reconstructable store.

**Scope: N=3 files (1 new port, 1 new engine, 1 modified)**

---

## Wave 1.1: `system_learning/ports/meta_prior_provider.py` (NEW)

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

## Wave 1.2: `system_learning/engines/healing_success_rate_store.py` (NEW)

**Hardenings applied:**
- Fixed 6-decimal precision on all stored rates
- `export_state()` for replay reconstruction
- `store_state_hash()` for version surface
- `_log_update()` structured telemetry (no silent failure)
- Single-process invariant with `_OWNER_PID` guard
- `_NEUTRAL_PRIOR` used during warm-up only

```python
"""Healing Success Rate Store — deterministic, replay-reconstructable store.

Backed by a dict[str, float].  In production populated by
OutcomeWriteBackHook (Phase 2).  In tests seeded directly.

Layer contract:
- Lives in system_learning layer.
- Exposed to L2.3 ONLY via MetaPriorProvider seam.
- MUST NOT import agentic_core modules.

Determinism contract:
- All stored rates rounded to 6 decimals.
- export_state() returns snapshot for replay reconstruction.
- store_state_hash() returns deterministic content hash.
- Single-process invariant: _OWNER_PID guards against fork divergence.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_NEUTRAL_PRIOR: float = 0.50
_MIN_SAMPLE_SIZE: int = 5
_EMA_ALPHA: float = 0.10


class HealingSuccessRateStore:
    """Deterministic store of per-signature success rates.

    Single-process invariant: if _OWNER_PID differs from current pid,
    operations are no-ops that log a warning (prevents fork divergence).
    """

    def __init__(self) -> None:
        self._rates: dict[str, float] = {}
        self._counts: dict[str, int] = {}
        self._owner_pid: int = os.getpid()

    def _check_pid(self) -> bool:
        """Return True if current process owns this store."""
        if os.getpid() != self._owner_pid:
            logger.warning(
                "HealingSuccessRateStore: pid mismatch "
                "(owner=%d, current=%d); operation skipped",
                self._owner_pid,
                os.getpid(),
            )
            return False
        return True

    def get_prior(self, error_signature: str) -> float:
        """Return current success-rate prior for error_signature.

        Returns _NEUTRAL_PRIOR when fewer than _MIN_SAMPLE_SIZE outcomes
        are recorded (dampening to avoid over-weighting early noisy data).
        """
        count = self._counts.get(error_signature, 0)
        if count < _MIN_SAMPLE_SIZE:
            return _NEUTRAL_PRIOR
        return self._rates.get(error_signature, _NEUTRAL_PRIOR)

    def record_outcome(self, error_signature: str, success: bool) -> None:
        """Update running success-rate average with a new outcome.

        Uses cumulative average during warm-up, then EMA.
        All stored values rounded to 6 decimals.
        """
        if not self._check_pid():
            return

        count = self._counts.get(error_signature, 0)
        current = self._rates.get(error_signature, _NEUTRAL_PRIOR)
        outcome_value = 1.0 if success else 0.0

        if count < _MIN_SAMPLE_SIZE:
            new_rate = round((current * count + outcome_value) / (count + 1), 6)
        else:
            new_rate = round(
                (1.0 - _EMA_ALPHA) * current + _EMA_ALPHA * outcome_value, 6
            )

        # Clamp to [0.0, 1.0]
        new_rate = max(0.0, min(1.0, new_rate))

        self._rates[error_signature] = new_rate
        self._counts[error_signature] = count + 1

        self._log_update(error_signature, success, new_rate, count + 1)

    def _log_update(
        self,
        error_signature: str,
        success: bool,
        new_rate: float,
        new_count: int,
    ) -> None:
        """Structured telemetry for every update (never silent)."""
        logger.info(
            "success_rate_update",
            extra={
                "error_signature": error_signature,
                "success": success,
                "new_rate": new_rate,
                "observation_count": new_count,
                "owner_pid": self._owner_pid,
            },
        )

    def export_state(self) -> dict[str, Any]:
        """Deterministic snapshot for replay reconstruction."""
        return {
            "rates": dict(sorted(self._rates.items())),
            "counts": dict(sorted(self._counts.items())),
            "owner_pid": self._owner_pid,
        }

    def store_state_hash(self) -> str:
        """Deterministic content hash of current store state."""
        state = self.export_state()
        # Remove pid from hash (not part of logical state)
        hashable = {"rates": state["rates"], "counts": state["counts"]}
        canonical = json.dumps(hashable, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def import_state(self, state: dict[str, Any]) -> None:
        """Restore from exported snapshot (for replay/testing)."""
        self._rates = dict(state.get("rates", {}))
        self._counts = dict(state.get("counts", {}))

    def get_all(self) -> dict[str, float]:
        """Snapshot of all current priors (for audit)."""
        return dict(self._rates)

    def get_counts(self) -> dict[str, int]:
        """Snapshot of all observation counts."""
        return dict(self._counts)

    def reset(self) -> None:
        """Clear all state (testing only)."""
        self._rates.clear()
        self._counts.clear()


# Module-level singleton
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
    "_EMA_ALPHA",
]
```

---

## Wave 1.3: `agentic_core/L2_execution/healers/healing_tier_router.py` (MODIFY)

**Change summary:** Add optional `meta_prior_provider` parameter to `get_historical_success_rate()`, `compute_heal_confidence()`, and `route_healing_tier()`. All parameters keyword-only with `None` default for full backward compat.

### Diff A: Imports (add at top, after existing imports)

```python
# --- ADD after line 28 (after existing imports) ---
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from system_learning.ports.meta_prior_provider import MetaPriorProvider
```

### Diff B: `get_historical_success_rate()` (lines 70-75)

```python
# --- BEFORE ---
def get_historical_success_rate(error_signature: str) -> float:
    """Look up historical success rate for an error signature.

    Returns neutral prior (0.50) if no history is available.
    """
    return _HISTORICAL_SUCCESS_RATES.get(error_signature, _NEUTRAL_PRIOR)

# --- AFTER ---
def get_historical_success_rate(
    error_signature: str,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
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

### Diff C: `compute_heal_confidence()` (line 95)

```python
# --- BEFORE ---
def compute_heal_confidence(healing_input: HealingInput) -> tuple[float, list[str]]:

# --- AFTER ---
def compute_heal_confidence(
    healing_input: HealingInput,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
) -> tuple[float, list[str]]:
```

And the call inside (line 113):

```python
# --- BEFORE ---
    historical_rate = get_historical_success_rate(healing_input.error_signature)

# --- AFTER ---
    historical_rate = get_historical_success_rate(
        healing_input.error_signature,
        meta_prior_provider=meta_prior_provider,
    )
```

### Diff D: `route_healing_tier()` (line 150-153)

```python
# --- BEFORE ---
def route_healing_tier(
    healing_input: HealingInput,
    config: HealingTierConfig,
) -> HealingDecision:

# --- AFTER ---
def route_healing_tier(
    healing_input: HealingInput,
    config: HealingTierConfig,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
) -> HealingDecision:
```

And the call inside (line 190):

```python
# --- BEFORE ---
    heal_confidence, reason_codes = compute_heal_confidence(healing_input)

# --- AFTER ---
    heal_confidence, reason_codes = compute_heal_confidence(
        healing_input,
        meta_prior_provider=meta_prior_provider,
    )
```

And update `_apply_qwen_kill_switch` call (line 247):

```python
# --- BEFORE ---
        heal_confidence, reason_codes = compute_heal_confidence(healing_input)

# --- AFTER ---
        heal_confidence, reason_codes = compute_heal_confidence(
            healing_input,
            meta_prior_provider=meta_prior_provider,
        )
```

Note: `_apply_qwen_kill_switch` also needs `meta_prior_provider` parameter threaded through. Signature changes to:

```python
def _apply_qwen_kill_switch(
    healing_input: HealingInput,
    config: HealingTierConfig,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
) -> HealingDecision | None:
```

And the call in `route_healing_tier` (line 170):

```python
# --- BEFORE ---
    decision = _apply_qwen_kill_switch(healing_input, config)

# --- AFTER ---
    decision = _apply_qwen_kill_switch(
        healing_input, config, meta_prior_provider=meta_prior_provider,
    )
```

### Phase 1 Tests

**File:** `tests/agentic_core/L2_execution/healers/test_meta_prior_provider.py` (NEW)

- `test_neutral_prior_provider_always_returns_050`
- `test_store_warm_up_uses_neutral_prior`
- `test_store_records_outcomes_and_updates_rate`
- `test_store_ema_after_warmup`
- `test_store_fixed_precision_6_decimals`
- `test_store_export_import_roundtrip`
- `test_store_state_hash_deterministic`
- `test_store_pid_guard_rejects_foreign_pid`
- `test_compute_heal_confidence_uses_injected_prior`
- `test_route_healing_tier_uses_injected_prior`
- `test_route_healing_tier_backward_compat_no_provider`
- `test_qwen_kill_switch_threads_provider`

---

# Phase 2 — Write-Back with Guardrails

**Objective:** After each healing invocation, write the outcome into `HealingSuccessRateStore` with structured telemetry. Write-back always executes (no retry-count short-circuit).

**Scope: N=2 files (1 new port, 1 modified)**

---

## Wave 2.1: `system_learning/ports/outcome_write_back_hook.py` (NEW)

**Hardenings:**
- Structured telemetry on failure (never silent)
- Write-back ALWAYS executes (no retry guard)
- Qwen prior update for QWEN tier only

```python
"""Outcome Write-Back Hook Port — seam for real-time meta-learning feedback.

Called by dispatch_healing() immediately after an invocation completes.
Implementations write to HealingSuccessRateStore and call
update_qwen_confidence_prior() (for QWEN tier).

Contracts:
- MUST be synchronous and fast (no network I/O in hot path).
- MUST emit structured telemetry on failure (never fully silent).
- MUST NOT modify HEALING_CONFIDENCE_X or HEALING_CONFIDENCE_Y.
- MUST NOT mutate healing_input or decision.
- MUST always execute (no retry-count short-circuit).
  Forced escalation applies to routing only, not write-back.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord
    from agentic_core.L2_execution.healers.healing_tier_types import (
        HealingDecision,
        HealingInput,
    )

logger = logging.getLogger(__name__)


class OutcomeWriteBackHook(Protocol):
    """Synchronous write-back seam called after each heal invocation."""

    def on_outcome(
        self,
        *,
        healing_input: HealingInput,
        decision: HealingDecision,
        record: InvocationRecord | None,
        success: bool,
    ) -> None:
        """Handle a completed healing outcome.

        Parameters
        ----------
        healing_input : HealingInput
            The original structured failure context.
        decision : HealingDecision
            The routing decision that was executed.
        record : InvocationRecord | None
            The invocation trace record (None if exception before record).
        success : bool
            Whether the heal attempt succeeded.
        """
        ...


class NullOutcomeWriteBackHook:
    """No-op hook (default when no store is configured)."""

    def on_outcome(self, **kwargs) -> None:
        pass


class DefaultOutcomeWriteBackHook:
    """Default hook: writes to HealingSuccessRateStore + Qwen prior update.

    Never silently swallows exceptions — always emits structured telemetry.
    Always executes regardless of retry_count (forced escalation is routing-only).
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
        # Always record outcome (no retry-count short-circuit)
        try:
            self._store.record_outcome(healing_input.error_signature, success)
        except Exception as exc:
            logger.warning(
                "write_back_store_failed",
                extra={
                    "error_signature": healing_input.error_signature,
                    "exception": str(exc),
                    "trace_id": healing_input.trace_id,
                },
            )

        # Qwen-specific prior update (per qwen_meta_learning contract)
        from agentic_core.L2_execution.healers.healing_tier_types import HealingTier
        if decision.tier == HealingTier.QWEN_VLLM:
            try:
                from agentic_core.L2_execution.healers.qwen_meta_learning import (
                    update_qwen_confidence_prior,
                )
                update_qwen_confidence_prior(healing_input.error_signature, success)
            except Exception as exc:
                logger.warning(
                    "write_back_qwen_prior_failed",
                    extra={
                        "error_signature": healing_input.error_signature,
                        "exception": str(exc),
                        "trace_id": healing_input.trace_id,
                    },
                )


__all__ = [
    "OutcomeWriteBackHook",
    "NullOutcomeWriteBackHook",
    "DefaultOutcomeWriteBackHook",
]
```

---

## Wave 2.2: `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` (MODIFY)

### Diff A: TYPE_CHECKING additions (after line 35)

```python
# --- ADD to TYPE_CHECKING block ---
    from system_learning.ports.meta_prior_provider import MetaPriorProvider
    from system_learning.ports.outcome_write_back_hook import OutcomeWriteBackHook
```

### Diff B: `dispatch_healing()` signature (lines 200-210)

```python
# --- BEFORE ---
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

### Diff C: Route call (line 231)

```python
# --- BEFORE ---
    decision = route_healing_tier(healing_input, config)

# --- AFTER ---
    decision = route_healing_tier(
        healing_input, config, meta_prior_provider=meta_prior_provider,
    )
```

### Diff D: Finally block (after line 258, before `return`)

```python
# --- ADD after _emit_outcome block in finally ---
        # Phase 2: Real-time write-back into meta-learning store
        if outcome_write_back_hook is not None:
            outcome_write_back_hook.on_outcome(
                healing_input=healing_input,
                decision=decision,
                record=record if success else None,
                success=success,
            )
```

Note: `record` is only bound if `success=True`. The hook receives `None` when invocation raised.

### Phase 2 Tests

**File:** `tests/agentic_core/L2_execution/healers/test_outcome_write_back.py` (NEW)

- `test_default_hook_records_success`
- `test_default_hook_records_failure`
- `test_hook_calls_qwen_prior_for_qwen_tier`
- `test_hook_does_not_call_qwen_prior_for_non_qwen`
- `test_hook_emits_telemetry_on_store_exception`
- `test_hook_emits_telemetry_on_qwen_exception`
- `test_hook_always_executes_regardless_of_retry_count`
- `test_dispatch_healing_calls_write_back_hook`
- `test_dispatch_healing_backward_compat_no_hook`
- `test_null_hook_is_noop`

---

# Phase 3 — Advisory-Only Pattern Influence

**Objective:** Wire pattern retrieval as metadata-only advisory. Pattern advice appends `reason_codes` but NEVER modifies `heal_confidence` or tier selection.

**Scope: N=3 files (2 new, 1 modified)**

---

## Wave 3.1: `system_learning/ports/healing_pattern_advisor.py` (NEW)

**Key hardening:** `confidence_boost` is computed but stored as advisory metadata only. It is NEVER applied to `heal_confidence` or used for tier decisions.

```python
"""Healing Pattern Advisor Port — seam for semantic pattern hints at routing time.

Contracts:
- MUST be synchronous.
- Returns HealingPatternAdvice (immutable, advisory only).
- MUST NOT modify heal_confidence.
- MUST NOT cause tier promotion or demotion.
- confidence_boost is INFORMATIONAL ONLY (C0) — for audit/reason_codes.
- tier_hint is INFORMATIONAL ONLY — for audit/reason_codes.
- Routing remains: tier = f(core_signals, historical_prior, retry_count).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

PATTERN_BOOST_CAP: float = 0.10


@dataclass(frozen=True, slots=True)
class HealingPatternAdvice:
    """Advisory output from the pattern advisor (C0 informational only).

    Attributes
    ----------
    tier_hint : str | None
        Historical tier that succeeded for similar patterns (informational).
    confidence_boost : float
        Computed boost in [0.0, PATTERN_BOOST_CAP] (informational, NOT applied).
    pattern_found : bool
        True if at least one pattern above similarity threshold was found.
    similarity_score : float
        Similarity of best matched pattern. 0.0 if none found.
    source : str
        Identifier of the provider (for audit).
    """

    tier_hint: str | None
    confidence_boost: float
    pattern_found: bool
    similarity_score: float
    source: str


class HealingPatternAdvisor(Protocol):
    """Seam for retrieving healing pattern advice (advisory only)."""

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
            Advisory output. pattern_found=False when nothing relevant.
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

## Wave 3.2: `system_learning/engines/default_healing_pattern_advisor.py` (NEW)

**Hardenings:**
- ML client is protocol-injected, never imported across layers
- No direct L1 import at module level
- `_ensure_client` removed — client must be injected or is None

```python
"""Default Healing Pattern Advisor — protocol-injected ML client wrapper.

Translates ML client output into bounded HealingPatternAdvice.
ML client MUST be injected; no cross-layer imports.

Bounded influence: confidence_boost = min(similarity - threshold, PATTERN_BOOST_CAP)
(informational only — never applied to heal_confidence)
"""

from __future__ import annotations

import logging
from typing import Any, Protocol

from system_learning.ports.healing_pattern_advisor import (
    PATTERN_BOOST_CAP,
    HealingPatternAdvice,
)

logger = logging.getLogger(__name__)

_MIN_SIMILARITY: float = 0.85


class PatternRetriever(Protocol):
    """Protocol for pattern retrieval (abstracts MetaLearningClient)."""

    def retrieve_healing_patterns(
        self,
        violation: dict[str, str],
        domain: str,
        top_k: int,
        min_similarity: float,
    ) -> list[Any]: ...


class DefaultHealingPatternAdvisor:
    """Concrete advisor backed by injected PatternRetriever.

    ML client must be injected at construction. No dynamic cross-layer imports.
    """

    def __init__(
        self,
        retriever: PatternRetriever | None = None,
        min_similarity: float = _MIN_SIMILARITY,
    ) -> None:
        self._retriever = retriever
        self._min_similarity = min_similarity

    def advise(
        self,
        *,
        error_signature: str,
        failure_type: str,
    ) -> HealingPatternAdvice:
        if self._retriever is None:
            return HealingPatternAdvice(
                tier_hint=None,
                confidence_boost=0.0,
                pattern_found=False,
                similarity_score=0.0,
                source="default_advisor:no_retriever",
            )

        try:
            violation = {
                "type": failure_type,
                "message": error_signature,
                "path": "",
            }
            patterns = self._retriever.retrieve_healing_patterns(
                violation,
                domain="agentic_core",
                top_k=1,
                min_similarity=self._min_similarity,
            )
        except Exception as exc:
            logger.warning(
                "pattern_retrieval_failed",
                extra={"error_signature": error_signature, "exception": str(exc)},
            )
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
        sim = float(getattr(best, "similarity_score", 0.0))
        strategy = getattr(best, "healing_strategy", {}) or {}
        tier_hint = strategy.get("tier") if isinstance(strategy, dict) else None

        # Bounded informational boost (NOT applied to heal_confidence)
        boost = round(min(max(sim - self._min_similarity, 0.0), PATTERN_BOOST_CAP), 6)

        return HealingPatternAdvice(
            tier_hint=tier_hint,
            confidence_boost=boost,
            pattern_found=True,
            similarity_score=round(sim, 6),
            source="default_advisor:pattern_match",
        )


__all__ = ["DefaultHealingPatternAdvisor", "PatternRetriever"]
```

---

## Wave 3.3: `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` (MODIFY)

### Diff A: TYPE_CHECKING addition

```python
    from system_learning.ports.healing_pattern_advisor import HealingPatternAdvisor
```

### Diff B: New parameter in `dispatch_healing()`

```python
    pattern_advisor: HealingPatternAdvisor | None = None,
```

### Diff C: Advisory metadata injection (after route call, before invocation)

```python
    # Phase 3: Advisory-only pattern metadata (C0 — NEVER changes tier or confidence)
    if pattern_advisor is not None:
        advice = pattern_advisor.advise(
            error_signature=healing_input.error_signature,
            failure_type=healing_input.failure_type,
        )
        if advice.pattern_found:
            # Append advisory metadata to reason_codes only
            advisory_codes = list(decision.reason_codes) + [
                f"pattern_found=true",
                f"pattern_similarity={advice.similarity_score:.6f}",
                f"pattern_advisory_boost={advice.confidence_boost:.6f}",
                f"pattern_tier_hint={advice.tier_hint or 'none'}",
                f"pattern_source={advice.source}",
                f"audit_confidence={round(decision.heal_confidence + advice.confidence_boost, 6):.6f}",
            ]
            # Reconstruct decision with SAME tier and SAME heal_confidence
            decision = HealingDecision(
                heal_confidence=decision.heal_confidence,  # UNCHANGED
                tier=decision.tier,                        # UNCHANGED
                reason_codes=tuple(advisory_codes),
            )
```

**Critical:** `heal_confidence` and `tier` are NEVER modified. `audit_confidence` is computed inline for the reason_code string only.

### Phase 3 Tests

**File:** `tests/agentic_core/L2_execution/healers/test_healing_pattern_advisor.py` (NEW)

- `test_null_advisor_returns_no_pattern`
- `test_default_advisor_no_retriever_returns_no_pattern`
- `test_default_advisor_returns_pattern_with_bounded_boost`
- `test_boost_capped_at_pattern_boost_cap`
- `test_advisory_does_not_change_heal_confidence`
- `test_advisory_does_not_change_tier`
- `test_advisory_appends_reason_codes_only`
- `test_dispatch_healing_preserves_tier_with_pattern_advisor`
- `test_dispatch_healing_backward_compat_no_advisor`
- `test_immutable_thresholds_not_affected`
- `test_forced_escalation_immune_to_pattern_advice`

---

# Phase 4 — Bus Injection Only

**Objective:** Enqueue outcomes via injected bus with explicit `proposal_only=True`.

**Scope: N=2 files (1 new port, 1 modified)**

---

## Wave 4.1: `system_learning/ports/meta_outcome_bus_hook.py` (NEW)

**Hardenings:**
- Bus is injected only (never constructed internally)
- Default is `NullMetaOutcomeBusHook`
- `proposal_only=True` hard-set in payload
- Structured telemetry on failure

```python
"""Meta Outcome Bus Hook — seam for enqueuing outcomes onto MetaLearningBus.

Contracts:
- Bus MUST be injected from L0. No internal instantiation.
- Default is NullMetaOutcomeBusHook (no-op).
- MUST set proposal_only=True in every ChangePackage payload.
- MUST be synchronous and non-blocking.
- MUST emit structured telemetry on failure (never silent).
- Bus consumers responsible for gate validation before applying.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord
    from agentic_core.L2_execution.healers.healing_tier_types import (
        HealingDecision,
        HealingInput,
    )

logger = logging.getLogger(__name__)


class MetaOutcomeBusHook(Protocol):
    """Seam for publishing outcomes onto MetaLearningBus."""

    def publish(
        self,
        *,
        healing_input: HealingInput,
        decision: HealingDecision,
        record: InvocationRecord | None,
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
            Invocation trace (None if exception before record).
        success : bool
            Whether the heal attempt succeeded.
        timestamp_utc : int
            Deterministic timestamp (injected by caller).
        """
        ...


class NullMetaOutcomeBusHook:
    """No-op hook (default when no bus is injected)."""

    def publish(self, **kwargs) -> None:
        pass


class DefaultMetaOutcomeBusHook:
    """Hook that publishes to an injected MetaLearningBus.

    Bus MUST be injected at construction from L0.
    Never constructs a bus internally.
    """

    def __init__(self, bus=None) -> None:
        self._bus = bus  # Injected from L0; None = disabled

    def publish(
        self,
        *,
        healing_input,
        decision,
        record,
        success: bool,
        timestamp_utc: int,
    ) -> None:
        if self._bus is None:
            return

        try:
            from agentic_core.L0_routing.meta_control.meta_learning_bus import (
                MetaLearningChangePackage,
            )
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
                    "proposal_only": True,  # HARD-SET: never auto-commit
                },
            )
            self._bus.enqueue(pkg)
        except Exception as exc:
            logger.warning(
                "meta_outcome_bus_publish_failed",
                extra={
                    "trace_id": healing_input.trace_id,
                    "exception": str(exc),
                },
            )


__all__ = [
    "MetaOutcomeBusHook",
    "NullMetaOutcomeBusHook",
    "DefaultMetaOutcomeBusHook",
]
```

---

## Wave 4.2: `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` (MODIFY)

### Diff A: TYPE_CHECKING addition

```python
    from system_learning.ports.meta_outcome_bus_hook import MetaOutcomeBusHook
```

### Diff B: New parameter in `dispatch_healing()`

```python
    meta_outcome_bus_hook: MetaOutcomeBusHook | None = None,
```

### Diff C: In finally block (after write-back hook)

```python
        # Phase 4: Enqueue outcome onto MetaLearningBus (injected)
        if meta_outcome_bus_hook is not None and timestamp_utc is not None:
            meta_outcome_bus_hook.publish(
                healing_input=healing_input,
                decision=decision,
                record=record if success else None,
                success=success,
                timestamp_utc=timestamp_utc,
            )
```

### Phase 4 Tests

**File:** `tests/agentic_core/L2_execution/healers/test_meta_outcome_bus_hook.py` (NEW)

- `test_null_hook_is_noop`
- `test_default_hook_no_bus_is_noop`
- `test_default_hook_enqueues_package`
- `test_package_has_proposal_only_true`
- `test_package_payload_structure`
- `test_hook_emits_telemetry_on_exception`
- `test_dispatch_healing_publishes_to_bus`
- `test_dispatch_healing_backward_compat_no_bus_hook`

---

# Oscillation Guard Specification

**Constants (deterministic):**

| Constant | Value | Meaning |
|---|---|---|
| `OSCILLATION_FLIP_THRESHOLD` (N) | 3 | Tier changed N times... |
| `OSCILLATION_WINDOW` (M) | 10 | ...within M consecutive observations... |
| `OSCILLATION_FREEZE_COUNT` (K) | 5 | ...freeze tier for K invocations |

**Rule:** If the same `error_signature` has had its routing tier change N times within the last M observations, the store freezes the prior at its current value for the next K invocations (no updates accepted).

**Location:** `HealingSuccessRateStore` tracks per-signature tier history. Freeze logic is internal to `record_outcome()`.

This is a Phase 2b follow-up after the core 4 phases are validated.

---

# Final Sovereignty Compliance Matrix

| Requirement | Ph1 | Ph2 | Ph3 | Ph4 |
|---|---|---|---|---|
| C0 informational-only | OK | OK | OK | OK |
| No threshold mutation | OK | OK | OK | OK |
| No tier mutation from C0 | N/A | N/A | OK | N/A |
| Control plane centralization | OK | OK | OK | OK |
| Layer boundaries (no cross-import) | OK | OK | OK | OK |
| Deterministic replay | OK | OK | OK | OK |
| No silent failures | OK | OK | OK | OK |
| Retry escalation preserved | OK | OK | OK | OK |
| proposal_only enforced | N/A | N/A | N/A | OK |
| Process model declared | OK | OK | OK | OK |

---

# File Summary

| Phase | File | Action | Wave |
|---|---|---|---|
| 1 | `system_learning/ports/meta_prior_provider.py` | NEW | 1.1 |
| 1 | `system_learning/engines/healing_success_rate_store.py` | NEW | 1.2 |
| 1 | `agentic_core/L2_execution/healers/healing_tier_router.py` | MODIFY | 1.3 |
| 2 | `system_learning/ports/outcome_write_back_hook.py` | NEW | 2.1 |
| 2 | `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` | MODIFY | 2.2 |
| 3 | `system_learning/ports/healing_pattern_advisor.py` | NEW | 3.1 |
| 3 | `system_learning/engines/default_healing_pattern_advisor.py` | NEW | 3.2 |
| 3 | `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` | MODIFY | 3.3 |
| 4 | `system_learning/ports/meta_outcome_bus_hook.py` | NEW | 4.1 |
| 4 | `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` | MODIFY | 4.2 |
| **Total** | **7 unique files** | **5 NEW + 2 MODIFY** | **10 waves** |

---

# Forbidden Actions (Final)

- Do NOT modify `HEALING_CONFIDENCE_X` or `HEALING_CONFIDENCE_Y`
- Do NOT allow pattern advice to change tier selection or `heal_confidence`
- Do NOT instantiate `MetaLearningBus` in L2
- Do NOT import across layers without protocol injection
- Do NOT use floating point without fixed 6-decimal precision
- Do NOT swallow exceptions silently (emit structured telemetry)
- Do NOT short-circuit write-back on retry_count
- Do NOT allow bus packages without `proposal_only=True`
- Do NOT add async I/O to routing hot path
- Do NOT use regex for structural code analysis

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

