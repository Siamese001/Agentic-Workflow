"""Formal-exception runtime-certification evidence helpers (Phase B.4).

Design references
-----------------
- ``docs/reference/runtime_certification/contract_span_binding_matrix.md`` v2 §6.3, §11
- ``docs/reports/runtime_certification/phase_a_trace_inventory.md``
- ``apps_shared/spine_manifest.yaml`` CC-SHARED-01 through CC-SHARED-05
- ``apps_shared/_compat/agentic_core_shim.py`` (READ-ONLY; not edited by this phase)

What this module does
---------------------
Provides a **read-only** cert-harness helper that verifies CC-SHARED-05 at
evidence-collection time. Returns a structured :class:`SharedShimEvidence`
record. Does NOT change runtime behavior, does NOT retire the shim, does
NOT edit ``apps_shared/_compat/agentic_core_shim.py`` or
``apps_shared/__init__.py``, does NOT certify any app.

CC-SHARED-05 evidence rule (from spine_manifest.yaml)
-----------------------------------------------------
CC-SHARED-05 passes ONLY when ALL of the following hold:

1. ``agentic_core`` is importable (real full-stack)
2. No synthetic fallback module is active in ``sys.modules``
3. No null fallback ``ConfCalibRiskGate`` is active
4. Risk-bearing execution is NOT allowed (this helper forces
   ``risk_bearing_allowed=False`` unconditionally)
5. Either the environment variable ``AGENTIC_CORE_STACK`` is set to
   ``"full"``, OR the full-stack no-op has been observed directly.

Any ambiguity fails closed with an explicit reason in
``failure_reasons``.

What this module is NOT
-----------------------
- Not a trace collector (Phase C).
- Not a certification evaluator (Phase D).
- Not a shim retirement tool (that requires the three-evidence audit
  per post-W14 scorecard addendum, out of scope for Phase B.4).
"""

from __future__ import annotations

import sys
import types
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

CC_SHARED_05_CONTROL_ID: str = "CC-SHARED-05"
"""Compensating-control identifier from ``apps_shared/spine_manifest.yaml``."""

FULL_STACK_ENV_VAR: str = "AGENTIC_CORE_STACK"
"""Env var name asserted at cert-harness startup (design matrix v2 §6.3 option b)."""

FULL_STACK_ENV_VALUE: str = "full"
"""The only env-var value that satisfies the full-stack assertion."""

#: Module names installed into ``sys.modules`` by
#: ``apps_shared/_compat/agentic_core_shim.py::install()`` when
#: ``agentic_core`` is unavailable. Order matches the shim's
#: ``_ensure_module`` calls (lines 149-161 in the shim).
SHIMMED_MODULE_NAMES: tuple[str, ...] = (
    "agentic_core",
    "agentic_core.runtime",
    "agentic_core.runtime.contracts",
    "agentic_core.runtime.contracts.lifecycle_trace_contract",
    "agentic_core.interfaces",
    "agentic_core.interfaces.execution",
    "agentic_core.interfaces.determinism",
    "agentic_core.L0_routing",
    "agentic_core.L0_routing.config",
    "agentic_core.L0_routing.config.path_constants",
    "agentic_core.L5_safety",
    "agentic_core.L5_safety.enforcement",
    "agentic_core.L5_safety.enforcement.conf_calib_gate",
)


# ---------------------------------------------------------------------------
# Evidence record
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SharedShimEvidence:
    """Structured CC-SHARED-05 evidence record.

    All fields are populated by :func:`collect_cc_shared_05_evidence`.
    ``passed`` is True only when every rule in §6.3 of the design matrix
    is satisfied. Failure reasons are accumulated in ``failure_reasons``
    so that a downstream cert report can cite every specific miss.
    """

    control_id: str = CC_SHARED_05_CONTROL_ID
    mode_assertion: str | None = None
    agentic_core_importable: bool = False
    fallback_modules_present: tuple[str, ...] = ()
    fallback_conf_calib_gate_active: bool = False
    full_stack_noop_observed: bool = False
    standalone_mode_detected: bool = False
    risk_bearing_allowed: bool = False  # MUST remain False by invariant
    passed: bool = False
    failure_reasons: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        # Hard invariant — this helper never allows risk-bearing standalone.
        if self.risk_bearing_allowed:
            raise ValueError(
                "SharedShimEvidence.risk_bearing_allowed must always be False; "
                "CC-SHARED-05 forbids risk-bearing standalone execution by "
                "design (apps_shared/spine_manifest.yaml)."
            )
        if self.control_id != CC_SHARED_05_CONTROL_ID:
            raise ValueError(
                f"SharedShimEvidence.control_id must be {CC_SHARED_05_CONTROL_ID!r}; "
                f"got {self.control_id!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Round-trip-friendly serialization for cert-report archival."""
        return asdict(self)


# ---------------------------------------------------------------------------
# Internal detection helpers
# ---------------------------------------------------------------------------


def _default_import_probe() -> bool:
    """Return True iff the real ``agentic_core`` can be imported.

    This delegates to ``importlib.util.find_spec``, which is cheap and
    does NOT execute the module. Tests inject their own probe.
    """
    import importlib.util  # local import — cheap and test-friendly

    try:
        spec = importlib.util.find_spec("agentic_core")
    except (ImportError, ValueError):
        return False
    return spec is not None


def _import_shim_symbols() -> tuple[type | None, type | None]:
    """Load ``_LifecycleModule`` and ``ConfCalibRiskGate`` from the shim.

    Returns ``(None, None)`` if the shim module itself cannot be loaded
    for any reason — the helper then falls back to structural heuristics.
    Does NOT call ``install()``; only imports the shim definitions.
    """
    try:
        from apps_shared._compat.agentic_core_shim import (  # type: ignore
            ConfCalibRiskGate,
            _LifecycleModule,
        )
    except (ImportError, AttributeError):
        return None, None
    return _LifecycleModule, ConfCalibRiskGate


def _looks_synthetic(module: Any) -> bool:
    """Structural heuristic — a plain ``types.ModuleType`` with no
    ``__file__`` is almost certainly a shim-installed fallback.

    Real ``agentic_core.*`` packages loaded from disk always have
    ``__file__`` (for submodules) or ``__path__`` (for packages).
    """
    if not isinstance(module, types.ModuleType):
        return False
    if type(module) is not types.ModuleType:
        # A subclass like ``_LifecycleModule`` — caller checks identity
        # separately; here we treat any non-plain ModuleType as "unusual"
        # and let the caller decide.
        return True
    # Real modules have either __file__ (leaf module) or __path__ (package).
    has_file = getattr(module, "__file__", None) is not None
    has_path = hasattr(module, "__path__") and bool(getattr(module, "__path__", None))
    return not (has_file or has_path)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def collect_cc_shared_05_evidence(
    env: Mapping[str, str] | None = None,
    *,
    sys_modules: Mapping[str, Any] | None = None,
    import_probe: Callable[[], bool] | None = None,
) -> SharedShimEvidence:
    """Return structured CC-SHARED-05 evidence.

    Parameters
    ----------
    env
        Environment mapping to read ``AGENTIC_CORE_STACK`` from. Defaults
        to ``os.environ``.
    sys_modules
        ``sys.modules``-like mapping for testability. Defaults to
        ``sys.modules``.
    import_probe
        Callable returning ``True`` iff ``agentic_core`` is importable.
        Defaults to :func:`_default_import_probe`.

    Returns
    -------
    SharedShimEvidence
        Populated record. ``passed`` is ``True`` only when every
        §6.3 rule holds.
    """
    if env is None:
        import os  # local — keep module-level import surface minimal

        env = os.environ
    mods: Mapping[str, Any] = sys_modules if sys_modules is not None else sys.modules
    probe = import_probe if import_probe is not None else _default_import_probe

    failures: list[str] = []
    notes: list[str] = []

    # 1. env-var assertion (design matrix v2 §6.3 option b, first half).
    mode_assertion = env.get(FULL_STACK_ENV_VAR)
    # A non-empty env var that is NOT "full" is a hard operator-intent
    # conflict: the operator is explicitly asserting standalone mode, so
    # certification must fail closed even if the observed state looks
    # full-stack. Empty string / None falls through to observation.
    env_var_conflict = (
        mode_assertion is not None
        and mode_assertion != ""
        and mode_assertion != FULL_STACK_ENV_VALUE
    )
    if mode_assertion is None:
        notes.append(
            f"env var {FULL_STACK_ENV_VAR} not set; falling back to "
            "full_stack_noop_observed detection"
        )
    elif mode_assertion == "":
        notes.append(
            f"env var {FULL_STACK_ENV_VAR} is empty; falling back to "
            "full_stack_noop_observed detection"
        )
    elif env_var_conflict:
        failures.append(
            f"{FULL_STACK_ENV_VAR}={mode_assertion!r} != {FULL_STACK_ENV_VALUE!r} "
            "— operator explicitly asserted non-full mode; fail closed"
        )

    # 2. importability probe.
    agentic_core_importable = bool(probe())
    if not agentic_core_importable:
        failures.append(
            "agentic_core is not importable; full-stack mode cannot be "
            "confirmed — standalone mode presumed"
        )

    # 3. Detect synthetic fallback modules in sys.modules.
    lifecycle_cls, null_gate_cls = _import_shim_symbols()
    fallback_present: list[str] = []
    fallback_gate_active = False

    for name in SHIMMED_MODULE_NAMES:
        mod = mods.get(name)
        if mod is None:
            continue
        # Strong identity check for _LifecycleModule subclass.
        if (
            lifecycle_cls is not None
            and isinstance(mod, lifecycle_cls)
            and type(mod) is lifecycle_cls
        ):
            fallback_present.append(name)
            continue
        # Strong identity check for the null ConfCalibRiskGate.
        gate_attr = getattr(mod, "ConfCalibRiskGate", None)
        if (
            null_gate_cls is not None
            and gate_attr is not None
            and gate_attr is null_gate_cls
        ):
            fallback_present.append(name)
            fallback_gate_active = True
            continue
        # Structural fallback — plain ModuleType with no __file__ / __path__.
        if _looks_synthetic(mod):
            fallback_present.append(name)

    fallback_present_tuple = tuple(fallback_present)
    if fallback_present_tuple:
        failures.append(
            f"synthetic fallback modules detected in sys.modules: "
            f"{list(fallback_present_tuple)}"
        )
    if fallback_gate_active:
        failures.append(
            "null ConfCalibRiskGate fallback is active — risk-bearing "
            "execution must NOT be certified"
        )

    standalone_mode_detected = (
        not agentic_core_importable or bool(fallback_present_tuple)
    )
    full_stack_noop_observed = (
        agentic_core_importable and not fallback_present_tuple
    )

    # 4. Compute pass/fail per §6.3.
    full_stack_asserted_or_observed = (
        mode_assertion == FULL_STACK_ENV_VALUE or full_stack_noop_observed
    )
    if not full_stack_asserted_or_observed:
        failures.append(
            "neither AGENTIC_CORE_STACK=full nor full_stack_noop_observed"
        )

    passed = (
        agentic_core_importable
        and not standalone_mode_detected
        and not fallback_gate_active
        and full_stack_asserted_or_observed
        and not env_var_conflict
    )

    return SharedShimEvidence(
        control_id=CC_SHARED_05_CONTROL_ID,
        mode_assertion=mode_assertion,
        agentic_core_importable=agentic_core_importable,
        fallback_modules_present=fallback_present_tuple,
        fallback_conf_calib_gate_active=fallback_gate_active,
        full_stack_noop_observed=full_stack_noop_observed,
        standalone_mode_detected=standalone_mode_detected,
        risk_bearing_allowed=False,  # invariant
        passed=passed,
        failure_reasons=tuple(failures),
        notes=tuple(notes),
    )


def assert_cc_shared_05_passes(
    env: Mapping[str, str] | None = None,
    *,
    sys_modules: Mapping[str, Any] | None = None,
    import_probe: Callable[[], bool] | None = None,
) -> SharedShimEvidence:
    """Assertive wrapper: raise ``RuntimeError`` if evidence does not pass.

    Returns the evidence record on success so the caller can archive it.
    """
    evidence = collect_cc_shared_05_evidence(
        env=env,
        sys_modules=sys_modules,
        import_probe=import_probe,
    )
    if not evidence.passed:
        reasons = "; ".join(evidence.failure_reasons) or "unknown failure"
        raise RuntimeError(
            f"{CC_SHARED_05_CONTROL_ID} evidence check did not pass: {reasons}"
        )
    return evidence


__all__ = [
    "CC_SHARED_05_CONTROL_ID",
    "FULL_STACK_ENV_VALUE",
    "FULL_STACK_ENV_VAR",
    "SHIMMED_MODULE_NAMES",
    "SharedShimEvidence",
    "assert_cc_shared_05_passes",
    "collect_cc_shared_05_evidence",
]
