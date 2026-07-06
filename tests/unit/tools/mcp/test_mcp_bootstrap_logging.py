from __future__ import annotations

import logging
from pathlib import Path

from tools.mcp import mcp_bootstrap


def test_resolve_stderr_level_defaults_to_warning() -> None:
    assert mcp_bootstrap._resolve_stderr_level(None) == logging.WARNING
    assert mcp_bootstrap._resolve_stderr_level("nonsense") == logging.WARNING


def test_resolve_stderr_level_accepts_error_critical_and_quiet() -> None:
    assert mcp_bootstrap._resolve_stderr_level("ERROR") == logging.ERROR
    assert mcp_bootstrap._resolve_stderr_level("critical") == logging.CRITICAL
    assert mcp_bootstrap._resolve_stderr_level("QUIET") is None


def test_bootstrap_sets_protocol_safe_environment_defaults() -> None:
    assert mcp_bootstrap.os.environ["TOKENIZERS_PARALLELISM"] == "false"
    assert mcp_bootstrap.os.environ["PYTHONUNBUFFERED"] == "1"
    assert mcp_bootstrap.os.environ["PYTHONIOENCODING"] == "utf-8"


def test_configure_logging_from_env_can_write_to_file(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "mcp.stderr.log"
    monkeypatch.setenv("MCP_STDERR_LOG_PATH", str(log_path))
    monkeypatch.setenv("MCP_STDERR_LEVEL", "ERROR")

    mcp_bootstrap._configure_logging_from_env()
    logging.getLogger("unit-mcp").warning("not written")
    logging.getLogger("unit-mcp").error("written")
    logging.shutdown()

    text = log_path.read_text(encoding="utf-8")
    assert "written" in text
    assert "not written" not in text
