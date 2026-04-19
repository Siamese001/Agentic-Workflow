from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L4_state.enforcement.memory_db_canonical_policy import (
    resolve_canonical_memory_db_path,
)


def test_rejects_noncanonical_memory_db_in_production_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("ALLOW_NONCANONICAL_MEMORY_DB_FOR_TESTS", raising=False)
    monkeypatch.setenv("MEMORY_DB", "tmp/noncanonical.sqlite")

    with pytest.raises(RuntimeError, match="Non-canonical MEMORY_DB path rejected"):
        resolve_canonical_memory_db_path()


def test_accepts_canonical_memory_db_in_production_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("ALLOW_NONCANONICAL_MEMORY_DB_FOR_TESTS", raising=False)
    monkeypatch.setenv("MEMORY_DB", "artifacts/memory/knowledge_graph.sqlite")

    assert resolve_canonical_memory_db_path() == Path("artifacts/memory/knowledge_graph.sqlite")


def test_allows_noncanonical_memory_db_in_test_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLOW_NONCANONICAL_MEMORY_DB_FOR_TESTS", "1")
    monkeypatch.setenv("MEMORY_DB", "tmp/noncanonical.sqlite")

    assert resolve_canonical_memory_db_path() == Path("tmp/noncanonical.sqlite")
