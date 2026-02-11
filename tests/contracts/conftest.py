"""Shared fixtures for Guardian sovereign agent contract tests.

All enforcement is AST-based. No runtime imports of production agents.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.contracts._scanner import (
    collect_reasoning_agent_files,
    parse_file_ast,
    rel,
)

# ── Collect once at import time ────────────────────────────────────────────────
_ALL_AGENT_FILES: list[Path] = collect_reasoning_agent_files()


@pytest.fixture(
    params=[pytest.param(f, id=rel(f)) for f in _ALL_AGENT_FILES],
)
def agent_file(request: pytest.FixtureRequest) -> Path:
    """Parametrized fixture yielding each reasoning Agent file path."""
    return request.param


@pytest.fixture
def agent_ast(agent_file: Path) -> ast.Module:
    """Parsed AST for agent_file. Skips on SyntaxError."""
    tree = parse_file_ast(agent_file)
    if tree is None:
        pytest.skip(f"SyntaxError in {agent_file.name}")
    return tree
