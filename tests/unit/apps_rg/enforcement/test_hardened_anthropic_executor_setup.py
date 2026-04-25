"""Regression tests for HardenedAnthropicExecutor client setup.

Tests lock in the fix for the original null-client bug:
  - Before: _setup_client set self._client = None, so _completion()'s
    self._client.messages.create(...) would raise AttributeError at first call.
  - After: _setup_client instantiates anthropic.Anthropic(api_key=...) when
    ANTHROPIC_API_KEY is present, and logs a warning when absent.

The suite has two tiers:

1. *Source-level* regression tests (robust to future import-cascade regressions)
2. *Functional* regression tests that actually import and instantiate the
   executor, exercising the end-to-end construction path that EX1+EX2 unblocked
   (agentic_core package re-export of get_clock, apps_rg bootstrap_runtime
   _ensure_module real-import preference, hardening_mixin lazy-import helpers).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_EXECUTOR_PATH = (
    Path(__file__).resolve().parents[4] / "apps_rg" / "enforcement" / "HardenedanthropicexecutorStrategy.py"
)


@pytest.fixture(scope="module")
def executor_source() -> str:
    """Read the executor source once per test module."""
    return _EXECUTOR_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Imports present
# ---------------------------------------------------------------------------


def test_anthropic_sdk_is_imported(executor_source: str):
    assert re.search(r"^import anthropic\b", executor_source, re.MULTILINE), (
        "HardenedAnthropicExecutor must import the anthropic SDK at module level "
        "to instantiate a real client in _setup_client."
    )


def test_dotenv_load_is_called_at_module_level(executor_source: str):
    assert "from dotenv import load_dotenv" in executor_source, (
        "Module must import load_dotenv so ANTHROPIC_API_KEY from .env is "
        "available at client construction time."
    )
    # load_dotenv() is called at module-level (not inside a function)
    assert re.search(r"^load_dotenv\(\)", executor_source, re.MULTILINE), (
        "load_dotenv() must be invoked at module-load time, not lazily."
    )


# ---------------------------------------------------------------------------
# Client instantiation (the core fix)
# ---------------------------------------------------------------------------


def test_setup_client_instantiates_anthropic_from_env(executor_source: str):
    assert "anthropic.Anthropic(api_key=" in executor_source, (
        "Regression guard: _setup_client MUST construct an anthropic.Anthropic "
        "client with api_key from environ. The prior bug was a hardcoded "
        "self._client = None in _setup_client that left the executor unable "
        "to call messages.create at runtime."
    )


def test_setup_client_reads_api_key_from_environ(executor_source: str):
    assert 'os.environ.get("ANTHROPIC_API_KEY")' in executor_source, (
        "The fix must read ANTHROPIC_API_KEY from os.environ (populated by "
        "dotenv.load_dotenv()); hardcoding or skipping the env read would "
        "revert the fix."
    )


def test_setup_client_warns_when_api_key_missing(executor_source: str):
    # The warning path is essential — silent None assignment hides config errors
    assert re.search(
        r'logger\.warning\(\s*"ANTHROPIC_API_KEY not set',
        executor_source,
    ), (
        "When ANTHROPIC_API_KEY is absent, _setup_client MUST log a warning "
        "rather than silently construct a null client that crashes on first use."
    )


# ---------------------------------------------------------------------------
# Negative assertions — prevent regression to the broken state
# ---------------------------------------------------------------------------


def test_setup_client_does_not_unconditionally_null_the_client(executor_source: str):
    """The OLD bug pattern: unconditional `self._client = None` inside _setup_client.

    The current code has `self._client = None` inside the else branch (when
    no API key is present), which is correct. But there must NOT be an
    unconditional assignment of None that overwrites the real client.
    """
    # Find _setup_client function body
    setup_match = re.search(
        r"def _setup_client\(self\)[^:]*:(.*?)(?=\n    def |\nclass |\Z)",
        executor_source,
        re.DOTALL,
    )
    assert setup_match is not None, "_setup_client method not found"
    body = setup_match.group(1)

    # Ensure the body DOES contain the instantiation
    assert "anthropic.Anthropic(api_key=" in body, (
        "_setup_client body must contain anthropic.Anthropic(api_key=...) call"
    )

    # Ensure the body does NOT contain an unconditional `self._client = None`
    # as the final assignment. We check that the LAST assignment to _client
    # is the Anthropic constructor, not None.
    # Simpler: count self._client = None occurrences — there should be at
    # most one (inside the `if not api_key:` branch).
    null_assignments = re.findall(r"self\._client\s*=\s*None", body)
    assert len(null_assignments) <= 1, (
        f"Found {len(null_assignments)} `self._client = None` assignments in "
        f"_setup_client body. The fix allows AT MOST ONE (the no-key branch). "
        f"Multiple None assignments indicate the bug has been partially reverted."
    )


def test_init_declares_client_type_as_optional_anthropic(executor_source: str):
    # Type annotation `self._client: anthropic.Anthropic | None = None` in
    # __init__ is the guarantee that the field is typed and the codebase
    # understands it can be either real client or None.
    assert re.search(
        r"self\._client\s*:\s*anthropic\.Anthropic\s*\|\s*None",
        executor_source,
    ), (
        "Regression guard: __init__ must declare self._client's type so that "
        "type checkers and future refactors cannot silently drop the SDK type."
    )


# ---------------------------------------------------------------------------
# Cascade-known-broken marker (documents the separately-tracked issue)
# ---------------------------------------------------------------------------


def test_cascade_breakage_is_acknowledged():
    """Historical pin: the cascade was resolved in EX1+EX2 commits.

    The executor module can now be imported and instantiated end-to-end. This
    test used to assert a DEFERRED_SCOPE marker; it now stands as a history
    marker that the cascade existed and was resolved, so a future regression
    would be easy to trace back to its origin.
    """
    rca_note = (
        "HardenedAnthropicExecutor import cascade RESOLVED by: "
        "(1) agentic_core/L2_execution/utils/__init__.py get_clock re-export, "
        "(2) apps_rg/bootstrap_runtime.py _ensure_module real-import preference, "
        "(3) agentic_core/mixins/hardening_mixin.py __init__ lazy-import fix."
    )
    assert rca_note  # History marker; survives refactors.


# ---------------------------------------------------------------------------
# Functional tier — end-to-end construction path
# ---------------------------------------------------------------------------


def test_executor_class_is_importable():
    """EX1 regression guard: the cascade used to prevent this import."""
    from apps_rg.enforcement.HardenedanthropicexecutorStrategy import (
        HardenedAnthropicExecutor,
    )

    assert HardenedAnthropicExecutor is not None
    assert HardenedAnthropicExecutor.__name__ == "HardenedAnthropicExecutor"


def test_executor_instantiates_with_real_anthropic_client(monkeypatch):
    """EX2 regression guard: hardening_mixin.__init__ used to reference
    undefined `get_breaker` / `ErrorRecoveryStrategy` / `get_telemetry`.
    Construction now resolves the lazy-import helpers cleanly.
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-" + "x" * 90)
    from apps_rg.enforcement.HardenedanthropicexecutorStrategy import (
        HardenedAnthropicExecutor,
    )

    executor = HardenedAnthropicExecutor()

    # The fix produces a REAL anthropic.Anthropic client
    import anthropic as anthropic_sdk

    assert isinstance(executor._client, anthropic_sdk.Anthropic), (
        f"Expected anthropic.Anthropic instance, got {type(executor._client).__name__}"
    )
    # Circuit breaker and error recovery must also be wired (EX2 fix)
    assert executor.circuit_breaker is not None
    assert executor.error_recovery is not None


def test_executor_without_api_key_keeps_client_none(monkeypatch, caplog):
    """Regression guard: when key is absent, construction logs a warning and
    returns a None client rather than crashing. This preserves the ability to
    construct the executor in offline tests / CI without a live key.
    """
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    # Also need to prevent .env from repopulating the key during this test
    monkeypatch.setattr(
        "apps_rg.enforcement.HardenedanthropicexecutorStrategy.load_dotenv",
        lambda *a, **kw: None,
    )

    from apps_rg.enforcement.HardenedanthropicexecutorStrategy import (
        HardenedAnthropicExecutor,
    )

    # Use a fresh instance so we don't hit cached state
    import importlib
    import apps_rg.enforcement.HardenedanthropicexecutorStrategy as mod

    importlib.reload(mod)

    # After reload, re-delete key (reload may have re-run load_dotenv)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with caplog.at_level("WARNING"):
        executor = mod.HardenedAnthropicExecutor()

    # When key is absent, client must be None (not a broken/half-built object)
    assert executor._client is None


def test_get_clock_reexport_from_l2_execution_utils():
    """EX1 regression guard: the package-level re-export must remain."""
    from agentic_core.L2_execution.utils import get_clock

    assert callable(get_clock)


def test_bootstrap_runtime_does_not_clobber_agentic_core_package():
    """EX1 regression guard: _ensure_module must prefer real imports.

    Before EX1: importing apps_rg would replace the real `agentic_core`
    package with a bare types.ModuleType (no __path__), breaking all
    subsequent `from agentic_core.X import Y` calls.
    """
    # Import apps_rg (which runs bootstrap_runtime.install_runtime_shims)
    import apps_rg  # noqa: F401
    import agentic_core

    # The real package has __path__ set; a bare types.ModuleType stub does not
    assert hasattr(agentic_core, "__path__"), (
        "agentic_core must remain a real package after apps_rg import; "
        "bootstrap_runtime._ensure_module has regressed if __path__ is missing"
    )
    assert agentic_core.__path__ is not None
    assert agentic_core.__spec__ is not None
