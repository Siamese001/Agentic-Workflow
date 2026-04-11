"""Regression tests for the otel_mcp_server startup hardening pass.

Tests verify:
- Importing the module does not execute lifecycle emit calls at import time
- Lifecycle-unavailable startup degrades cleanly instead of crashing
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = str(Path(__file__).resolve().parents[4])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


# ---------------------------------------------------------------------------
# Regression: lifecycle emits must not execute at import time
# ---------------------------------------------------------------------------


def test_import_does_not_execute_lifecycle_emits():
    """Importing otel_mcp_server must not call lifecycle emit functions.

    Regression for: top-level _emit_* calls crashed the process at exec() time
    before MCP handshake could occur. After fix, emits are deferred to
    _register_lifecycle_traces() called from __main__.
    """
    # Clear module if already imported
    mod_name = "tools.otel.otel_mcp_server"
    if mod_name in sys.modules:
        del sys.modules[mod_name]

    # Mock the lifecycle contract to track if any emit functions are called
    with (
        patch(
            "agentic_core.runtime.contracts.lifecycle_trace_contract.emit_determinism_digest"
        ) as mock_digest,
        patch("agentic_core.runtime.contracts.lifecycle_trace_contract.record_execution_trace") as mock_trace,
        patch(
            "agentic_core.runtime.contracts.lifecycle_trace_contract._emit_applies_guardrail"
        ) as mock_guardrail,
    ):
        import tools.otel.otel_mcp_server as otel_server  # noqa: PLC0415

        # Import should succeed
        assert hasattr(otel_server, "mcp")
        assert hasattr(otel_server, "_register_lifecycle_traces")

        # No lifecycle emits should have been called at import time
        mock_digest.assert_not_called()
        mock_trace.assert_not_called()
        mock_guardrail.assert_not_called()


def test_lifecycle_emits_called_from_register_function():
    """_register_lifecycle_traces() should call lifecycle emits when available.

    Verifies the deferred emit function actually works when called explicitly.
    """
    mod_name = "tools.otel.otel_mcp_server"
    if mod_name in sys.modules:
        del sys.modules[mod_name]

    with (
        patch(
            "agentic_core.runtime.contracts.lifecycle_trace_contract.emit_determinism_digest"
        ) as mock_digest,
        patch("agentic_core.runtime.contracts.lifecycle_trace_contract.record_execution_trace") as mock_trace,
    ):
        import tools.otel.otel_mcp_server as otel_server  # noqa: PLC0415

        # Call the registration function explicitly
        otel_server._register_lifecycle_traces()

        # After calling, emits should have been executed
        mock_digest.assert_called_once_with("otel_mcp_server", "otel_mcp_server_digest")
        mock_trace.assert_called_once_with("otel_mcp_server", "otel_mcp_server_trace")


# ---------------------------------------------------------------------------
# Regression: lifecycle-unavailable startup degrades cleanly
# ---------------------------------------------------------------------------


def _load_server_with_broken_lifecycle():
    """Load otel_mcp_server with lifecycle contract blocked via sys.modules sentinel.

    Injects a module-like object that raises ImportError on any attribute
    access, simulating a missing or broken lifecycle_trace_contract package.
    Returns the loaded server module.
    """
    mod_name = "tools.otel.otel_mcp_server"
    lifecycle_mod = "agentic_core.runtime.contracts.lifecycle_trace_contract"
    # Remove server module to force re-execution
    sys.modules.pop(mod_name, None)
    # Save and replace lifecycle module with an object that errors on from-import
    saved = sys.modules.get(lifecycle_mod)

    class _BrokenModule:
        """Raises ImportError on any attribute lookup to simulate missing exports."""

        def __getattr__(self, name: str):
            raise ImportError(f"lifecycle missing: {name}")

    sys.modules[lifecycle_mod] = _BrokenModule()  # type: ignore[assignment]
    try:
        import importlib  # noqa: PLC0415
        import importlib.util  # noqa: PLC0415

        spec = importlib.util.spec_from_file_location(
            mod_name,
            Path(_PROJECT_ROOT) / "tools" / "otel" / "otel_mcp_server.py",
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return module
    finally:
        # Restore lifecycle module
        if saved is None:
            sys.modules.pop(lifecycle_mod, None)
        else:
            sys.modules[lifecycle_mod] = saved


def test_lifecycle_unavailable_import_succeeds():
    """Import should succeed even if lifecycle contract is unavailable.

    Regression for: ImportError in lifecycle contract crashed the entire
    server process. After fix, import failure is caught, flagged via
    _LIFECYCLE_AVAILABLE, and emits are skipped.
    """
    otel_server = _load_server_with_broken_lifecycle()
    assert hasattr(otel_server, "mcp")
    assert otel_server._LIFECYCLE_AVAILABLE is False


def test_lifecycle_unavailable_register_noops():
    """_register_lifecycle_traces() should no-op when lifecycle unavailable."""
    otel_server = _load_server_with_broken_lifecycle()
    # Should not raise even though lifecycle is unavailable
    otel_server._register_lifecycle_traces()


def test_fastmcp_import_failure_exits_cleanly():
    """FastMCP import failure should exit with explicit stderr message, code 1."""
    import importlib.util  # noqa: PLC0415
    import io  # noqa: PLC0415

    mod_name = "tools.otel.otel_mcp_server"
    fastmcp_mod = "mcp.server.fastmcp"

    saved_fastmcp = sys.modules.get(fastmcp_mod)

    class _BrokenFastMCP:
        """Raises ImportError on attribute access to simulate missing mcp package."""

        def __getattr__(self, name: str):
            raise ImportError(f"mcp missing: {name}")

    sys.modules[fastmcp_mod] = _BrokenFastMCP()  # type: ignore[assignment]
    sys.modules.pop(mod_name, None)

    stderr_capture = io.StringIO()
    exited: list[int] = []

    def _capture_exit(code: int) -> None:
        exited.append(code)
        raise SystemExit(code)

    try:
        spec = importlib.util.spec_from_file_location(
            mod_name,
            Path(_PROJECT_ROOT) / "tools" / "otel" / "otel_mcp_server.py",
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module

        with patch("sys.exit", side_effect=_capture_exit), patch("sys.stderr", stderr_capture):
            with pytest.raises(SystemExit) as exc_info:
                spec.loader.exec_module(module)  # type: ignore[union-attr]

        assert exc_info.value.code == 1
        assert "FATAL" in stderr_capture.getvalue()
    finally:
        if saved_fastmcp is None:
            sys.modules.pop(fastmcp_mod, None)
        else:
            sys.modules[fastmcp_mod] = saved_fastmcp
        sys.modules.pop(mod_name, None)


# ---------------------------------------------------------------------------
# Repo-root bootstrap verification
# ---------------------------------------------------------------------------


def test_repo_root_bootstrap_sets_syspath():
    """Module must bootstrap repo root into sys.path before agentic_core import.

    The server file's bootstrap adds _REPO_ROOT_BOOTSTRAP = Path(__file__).resolve().parents[2]
    which equals C:/Git/Agentic-Workflow. This test verifies that path is present after import.
    """
    mod_name = "tools.otel.otel_mcp_server"
    sys.modules.pop(mod_name, None)

    # The bootstrap path is parents[2] from the server file (tools/otel/otel_mcp_server.py)
    # parents[0]=tools/otel, parents[1]=tools, parents[2]=repo_root
    server_file = (Path(_PROJECT_ROOT) / "tools" / "otel" / "otel_mcp_server.py").resolve()
    expected_bootstrap = str(server_file.parents[2])

    # Remove from sys.path if present so the bootstrap must re-add it
    was_present = expected_bootstrap in sys.path
    if was_present:
        sys.path.remove(expected_bootstrap)

    try:
        import tools.otel.otel_mcp_server  # noqa: PLC0415, F401

        assert expected_bootstrap in sys.path
    finally:
        # Always restore
        if expected_bootstrap not in sys.path:
            sys.path.insert(0, expected_bootstrap)
        sys.modules.pop(mod_name, None)
