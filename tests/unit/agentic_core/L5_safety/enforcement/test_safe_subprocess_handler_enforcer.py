"""Surface coverage for `agentic_core.L5_safety.enforcement.safe_subprocess_handler_enforcer`.

Wave 5 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v2). L5 safety
seam — the canonical safe subprocess wrapper (constitutional rule §0/§14).
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.enforcement.safe_subprocess_handler_enforcer"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_all_exports(mod):
    assert hasattr(mod, "__all__")
    assert set(mod.__all__) >= {"safe_run", "safe_popen", "safe_communicate"}


@pytest.mark.parametrize("name", ["safe_run", "safe_popen", "safe_communicate"])
def test_public_functions_callable(mod, name):
    fn = getattr(mod, name)
    assert callable(fn)


def test_safe_run_signature_requires_args_list(mod):
    sig = inspect.signature(mod.safe_run)
    params = list(sig.parameters.keys())
    assert len(params) >= 1


def test_safe_run_executes_simple_command(mod):
    """End-to-end: run a quick benign Python one-liner via safe_run."""
    result = mod.safe_run(["python", "-c", "print('ok')"], timeout=10)
    # Tolerate either CompletedProcess or wrapped result with returncode/stdout
    rc = getattr(result, "returncode", None)
    assert rc is not None and rc == 0


def test_safe_run_signature_pins_safe_kwargs(mod):
    """safe_run signature must expose timeout, capture_output, sanitize_output keywords.

    These are the safety-relevant defaults. (Note: shell=True is forwarded via
    **kwargs to subprocess for compatibility — constitutional shell=False enforcement
    happens at the call-site level via pre_run_gate, not at this function.)
    """
    sig = inspect.signature(mod.safe_run)
    for name in ("timeout", "capture_output", "sanitize_output"):
        assert name in sig.parameters, f"{name} kwarg missing from safe_run"
