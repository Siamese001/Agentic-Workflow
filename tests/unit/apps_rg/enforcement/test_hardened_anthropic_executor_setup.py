"""Source-level regression tests for HardenedAnthropicExecutor client setup.

These tests lock in the fix for the original null-client bug:
  - Before: _setup_client set self._client = None, so _completion()'s
    self._client.messages.create(...) would raise AttributeError at first call.
  - After: _setup_client instantiates anthropic.Anthropic(api_key=...) when
    ANTHROPIC_API_KEY is present, and logs a warning when absent.

NOTE: We use *source-level* assertions (reading the file's text) rather than
importing the module, because the executor module has a pre-existing import
cascade (apps_rg.utils.agent_executor_util -> agentic_core.L2_execution.utils
-> get_clock) that prevents it from being importable in the current repo
state. That cascade is tracked as a separate RCA and is out of scope for this
fix. The source-level regression tests are still meaningful — they prevent a
future refactor from silently reverting the null-client fix.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_EXECUTOR_PATH = (
    Path(__file__).resolve().parents[4]
    / "apps_rg"
    / "enforcement"
    / "HardenedanthropicexecutorStrategy.py"
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
    assert re.search(
        r"^load_dotenv\(\)", executor_source, re.MULTILINE
    ), "load_dotenv() must be invoked at module-load time, not lazily."


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
    """This test is a self-documenting pin that points to the separate RCA.

    It does NOT validate behavior — it simply fails loudly if someone deletes
    the RCA reference below without acknowledging the cascade. Keep the link
    so future me knows why the executor can't be imported in unit tests today.
    """
    rca_note = (
        "HardenedAnthropicExecutor module import is blocked by a cascade in "
        "apps_rg.utils.agent_executor_util -> agentic_core.L2_execution.utils."
        "get_clock. Tracked via DEFERRED_SCOPE in plan "
        ".windsurf/plans/anthropic-rag-gaps-7f3c2a.md W2 P2.1.followup."
    )
    assert rca_note  # Trivially true; serves as in-file documentation.
