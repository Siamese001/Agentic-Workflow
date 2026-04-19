from __future__ import annotations

import os
from pathlib import Path

_CANONICAL_MEMORY_DB = Path("artifacts/memory/knowledge_graph.sqlite")


def _is_test_context() -> bool:
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return True
    if os.environ.get("ALLOW_NONCANONICAL_MEMORY_DB_FOR_TESTS") == "1":
        return True
    return False


def resolve_canonical_memory_db_path() -> Path:
    configured = Path(os.environ.get("MEMORY_DB", str(_CANONICAL_MEMORY_DB)))
    if _is_test_context():
        return configured

    if configured != _CANONICAL_MEMORY_DB:
        raise RuntimeError(
            "Non-canonical MEMORY_DB path rejected in production scope: "
            f"{configured}. Expected {_CANONICAL_MEMORY_DB}.",
        )

    return configured
