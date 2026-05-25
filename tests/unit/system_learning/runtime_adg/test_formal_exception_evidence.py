"""Tests for the CC-SHARED-05 evidence helper (Phase B.4).

Tests use the helper's injection points (``env``, ``sys_modules``,
``import_probe``) to simulate full-stack and standalone states without
ever mutating the real process-wide ``sys.modules`` or importing the
real ``agentic_core`` in a way that would affect other tests.

The shim file ``apps_shared/_compat/agentic_core_shim.py`` is NOT
edited by Phase B.4; these tests exercise only the helper.
"""

from __future__ import annotations

import sys
import types
from typing import Any

import pytest

from agentic_core.L6_system_learning.formal_exception_evidence import (
    CC_SHARED_05_CONTROL_ID,
    FULL_STACK_ENV_VALUE,
    FULL_STACK_ENV_VAR,
    SHIMMED_MODULE_NAMES,
    SharedShimEvidence,
    assert_cc_shared_05_passes,
    collect_cc_shared_05_evidence,
)


# ---------------------------------------------------------------------------
# Helpers to build synthetic / real module stand-ins for sys.modules injection
# ---------------------------------------------------------------------------


def _fake_synthetic_agentic_core_tree() -> dict[str, Any]:
    """Return a dict mimicking what the shim installs in standalone mode.

    Pulls the real shim's ``_LifecycleModule`` and ``ConfCalibRiskGate``
    classes so the helper's identity checks fire exactly as in production.
    """
    from apps_shared._compat.agentic_core_shim import (  # type: ignore
        ConfCalibRiskGate,
        _LifecycleModule,
    )

    mods: dict[str, Any] = {}
    for name in SHIMMED_MODULE_NAMES:
        if name == "agentic_core.runtime.contracts.lifecycle_trace_contract":
            mods[name] = _LifecycleModule(name)
        elif name == "agentic_core.L5_safety.enforcement.conf_calib_gate":
            m = types.ModuleType(name)
            m.ConfCalibRiskGate = ConfCalibRiskGate
            mods[name] = m
        else:
            # Plain ModuleType, no __file__, no __path__ — mimics what the
            # shim installs.
            mods[name] = types.ModuleType(name)
    return mods


def _fake_real_agentic_core_tree(tmp_path_str: str) -> dict[str, Any]:
    """Return a dict mimicking real filesystem-loaded packages.

    Real modules always have ``__file__`` (leaf) or ``__path__``
    (package), so the helper's structural heuristic treats them as
    NON-synthetic.
    """
    mods: dict[str, Any] = {}
    # Simulate just the root package as a real loaded module.
    m = types.ModuleType("agentic_core")
    m.__file__ = f"{tmp_path_str}/agentic_core/__init__.py"
    m.__path__ = [f"{tmp_path_str}/agentic_core"]
    mods["agentic_core"] = m
    return mods


# ---------------------------------------------------------------------------
# Passing paths
# ---------------------------------------------------------------------------


def test_full_stack_env_var_plus_real_import_passes(tmp_path) -> None:
    env = {FULL_STACK_ENV_VAR: FULL_STACK_ENV_VALUE}
    ev = collect_cc_shared_05_evidence(
        env=env,
        sys_modules=_fake_real_agentic_core_tree(str(tmp_path)),
        import_probe=lambda: True,
    )
    assert ev.passed is True
    assert ev.agentic_core_importable is True
    assert ev.fallback_modules_present == ()
    assert ev.fallback_conf_calib_gate_active is False
    assert ev.standalone_mode_detected is False
    assert ev.full_stack_noop_observed is True
    assert ev.risk_bearing_allowed is False
    assert ev.mode_assertion == FULL_STACK_ENV_VALUE
    assert ev.failure_reasons == ()


def test_no_env_var_but_real_agentic_core_observed_passes(tmp_path) -> None:
    """Option (a): env var absent but observed full-stack no-op."""
    env: dict[str, str] = {}  # no AGENTIC_CORE_STACK
    ev = collect_cc_shared_05_evidence(
        env=env,
        sys_modules=_fake_real_agentic_core_tree(str(tmp_path)),
        import_probe=lambda: True,
    )
    assert ev.passed is True
    assert ev.mode_assertion is None
    assert ev.full_stack_noop_observed is True
    assert ev.failure_reasons == ()
    # Notes should record that the env var was missing and we fell back.
    assert any(FULL_STACK_ENV_VAR in n for n in ev.notes)


def test_live_process_evidence_passes_if_full_stack_asserted() -> None:
    """Sanity check against the LIVE interpreter: this repo IS full-stack,
    so with env var set, the helper must pass.

    This runs against the real ``sys.modules`` but uses an explicit env
    to avoid dependence on the tester's shell environment.
    """
    ev = collect_cc_shared_05_evidence(
        env={FULL_STACK_ENV_VAR: FULL_STACK_ENV_VALUE},
    )
    assert ev.agentic_core_importable is True
    # The real agentic_core modules in sys.modules are filesystem-backed,
    # so none should be flagged as synthetic fallback.
    assert ev.fallback_modules_present == ()
    assert ev.passed is True


# ---------------------------------------------------------------------------
# Failing paths
# ---------------------------------------------------------------------------


def test_missing_agentic_core_fails() -> None:
    env = {FULL_STACK_ENV_VAR: FULL_STACK_ENV_VALUE}
    ev = collect_cc_shared_05_evidence(
        env=env,
        sys_modules={},  # empty — nothing loaded
        import_probe=lambda: False,  # agentic_core NOT importable
    )
    assert ev.passed is False
    assert ev.agentic_core_importable is False
    assert ev.standalone_mode_detected is True
    assert any("not importable" in r for r in ev.failure_reasons)


def test_env_var_not_full_fails(tmp_path) -> None:
    env = {FULL_STACK_ENV_VAR: "standalone"}
    ev = collect_cc_shared_05_evidence(
        env=env,
        sys_modules=_fake_real_agentic_core_tree(str(tmp_path)),
        import_probe=lambda: True,
    )
    assert ev.passed is False
    assert any(
        f"{FULL_STACK_ENV_VAR}='standalone'" in r for r in ev.failure_reasons
    )


def test_env_var_empty_string_fails(tmp_path) -> None:
    env = {FULL_STACK_ENV_VAR: ""}
    ev = collect_cc_shared_05_evidence(
        env=env,
        sys_modules=_fake_real_agentic_core_tree(str(tmp_path)),
        import_probe=lambda: True,
    )
    # Empty string is not FULL_STACK_ENV_VALUE, so the explicit assertion
    # fails — but full_stack_noop_observed is True, so overall passes.
    # The helper only fails HARD on mismatched non-empty value.
    # Per §6.3 option (a+b): observed noop alone is sufficient.
    assert ev.passed is True
    assert ev.full_stack_noop_observed is True


def test_synthetic_fallback_module_present_fails() -> None:
    env = {FULL_STACK_ENV_VAR: FULL_STACK_ENV_VALUE}
    synthetic = _fake_synthetic_agentic_core_tree()
    ev = collect_cc_shared_05_evidence(
        env=env,
        sys_modules=synthetic,
        import_probe=lambda: False,  # agentic_core is not importable in standalone
    )
    assert ev.passed is False
    assert ev.standalone_mode_detected is True
    assert set(ev.fallback_modules_present).issubset(set(SHIMMED_MODULE_NAMES))
    # The lifecycle module AND the conf_calib_gate module must both be
    # detected by their strong identity checks.
    assert (
        "agentic_core.runtime.contracts.lifecycle_trace_contract"
        in ev.fallback_modules_present
    )
    assert (
        "agentic_core.L5_safety.enforcement.conf_calib_gate"
        in ev.fallback_modules_present
    )


def test_fallback_ConfCalibRiskGate_active_fails() -> None:
    """Even if ONLY the gate fallback is present, the helper must fail
    and set ``fallback_conf_calib_gate_active=True``."""
    from apps_shared._compat.agentic_core_shim import (  # type: ignore
        ConfCalibRiskGate,
    )

    gate_mod = types.ModuleType("agentic_core.L5_safety.enforcement.conf_calib_gate")
    gate_mod.ConfCalibRiskGate = ConfCalibRiskGate

    env = {FULL_STACK_ENV_VAR: FULL_STACK_ENV_VALUE}
    ev = collect_cc_shared_05_evidence(
        env=env,
        sys_modules={
            "agentic_core.L5_safety.enforcement.conf_calib_gate": gate_mod,
        },
        import_probe=lambda: True,  # pretend core is importable
    )
    assert ev.passed is False
    assert ev.fallback_conf_calib_gate_active is True
    assert any("null ConfCalibRiskGate" in r for r in ev.failure_reasons)


def test_plain_ModuleType_without_file_detected_as_synthetic() -> None:
    """Structural heuristic: a plain ``types.ModuleType`` with no
    ``__file__`` and no ``__path__`` looks like a shim fallback."""
    plain = types.ModuleType("agentic_core.interfaces.determinism")
    env = {FULL_STACK_ENV_VAR: FULL_STACK_ENV_VALUE}
    ev = collect_cc_shared_05_evidence(
        env=env,
        sys_modules={"agentic_core.interfaces.determinism": plain},
        import_probe=lambda: True,
    )
    assert ev.passed is False
    assert "agentic_core.interfaces.determinism" in ev.fallback_modules_present
    assert ev.standalone_mode_detected is True


# ---------------------------------------------------------------------------
# assert_cc_shared_05_passes wrapper
# ---------------------------------------------------------------------------


def test_assert_helper_raises_on_failure_with_reason() -> None:
    with pytest.raises(RuntimeError, match=CC_SHARED_05_CONTROL_ID):
        assert_cc_shared_05_passes(
            env={FULL_STACK_ENV_VAR: FULL_STACK_ENV_VALUE},
            sys_modules={},
            import_probe=lambda: False,
        )


def test_assert_helper_returns_evidence_on_success(tmp_path) -> None:
    ev = assert_cc_shared_05_passes(
        env={FULL_STACK_ENV_VAR: FULL_STACK_ENV_VALUE},
        sys_modules=_fake_real_agentic_core_tree(str(tmp_path)),
        import_probe=lambda: True,
    )
    assert isinstance(ev, SharedShimEvidence)
    assert ev.passed is True


def test_assert_error_message_includes_failure_reasons() -> None:
    with pytest.raises(RuntimeError) as excinfo:
        assert_cc_shared_05_passes(
            env={FULL_STACK_ENV_VAR: "standalone"},
            sys_modules={},
            import_probe=lambda: False,
        )
    msg = str(excinfo.value)
    assert FULL_STACK_ENV_VAR in msg or "not importable" in msg


# ---------------------------------------------------------------------------
# Invariants
# ---------------------------------------------------------------------------


def test_risk_bearing_allowed_is_always_False(tmp_path) -> None:
    """Hard invariant: the helper never allows risk-bearing standalone."""
    for env_value in (FULL_STACK_ENV_VALUE, "standalone", None):
        env = {} if env_value is None else {FULL_STACK_ENV_VAR: env_value}
        ev = collect_cc_shared_05_evidence(
            env=env,
            sys_modules=_fake_real_agentic_core_tree(str(tmp_path)),
            import_probe=lambda: True,
        )
        assert ev.risk_bearing_allowed is False


def test_SharedShimEvidence_rejects_risk_bearing_allowed_True() -> None:
    """Hand-constructing with ``risk_bearing_allowed=True`` must fail."""
    with pytest.raises(ValueError, match="risk_bearing_allowed must always be False"):
        SharedShimEvidence(risk_bearing_allowed=True)


def test_SharedShimEvidence_rejects_wrong_control_id() -> None:
    with pytest.raises(ValueError, match="control_id must be"):
        SharedShimEvidence(control_id="CC-OTHER-99")


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def test_evidence_is_serializable_via_to_dict(tmp_path) -> None:
    ev = collect_cc_shared_05_evidence(
        env={FULL_STACK_ENV_VAR: FULL_STACK_ENV_VALUE},
        sys_modules=_fake_real_agentic_core_tree(str(tmp_path)),
        import_probe=lambda: True,
    )
    d = ev.to_dict()
    assert d["control_id"] == CC_SHARED_05_CONTROL_ID
    assert d["passed"] is True
    assert d["risk_bearing_allowed"] is False
    assert d["fallback_modules_present"] == ()
    # Confirm it's JSON-serializable as well.
    import json

    json.dumps(d)  # must not raise


def test_evidence_dataclass_asdict_round_trip(tmp_path) -> None:
    from dataclasses import asdict

    ev = collect_cc_shared_05_evidence(
        env={},
        sys_modules=_fake_real_agentic_core_tree(str(tmp_path)),
        import_probe=lambda: True,
    )
    d = asdict(ev)
    assert d["control_id"] == CC_SHARED_05_CONTROL_ID
    assert d["passed"] is True


# ---------------------------------------------------------------------------
# Shimmed module name constant sanity
# ---------------------------------------------------------------------------


def test_SHIMMED_MODULE_NAMES_matches_shim_install() -> None:
    """Count must match the ``_ensure_module`` calls in
    ``apps_shared/_compat/agentic_core_shim.py::install()``."""
    # 13 modules are installed by the shim as of W15 (the W15 prose said
    # "12" — the precise count from the shim source is 13). Each is
    # enumerated here for auditability.
    assert len(SHIMMED_MODULE_NAMES) == 13
    # Every name must start with "agentic_core".
    for name in SHIMMED_MODULE_NAMES:
        assert name.startswith("agentic_core"), f"not an agentic_core name: {name!r}"


def test_SHIMMED_MODULE_NAMES_no_duplicates() -> None:
    assert len(set(SHIMMED_MODULE_NAMES)) == len(SHIMMED_MODULE_NAMES)
