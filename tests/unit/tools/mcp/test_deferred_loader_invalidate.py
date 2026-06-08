"""W1 unit test: DeferredLoader.invalidate forces a rebuild on the next get().

Backs the ChromaDB rebuild-on-death recovery (apps_rg AIG E2E remediation, E2E-11):
when a cached client is detected dead, the loader cache must be droppable so a fresh
client is built.
"""
from __future__ import annotations

from tools.mcp.mcp_deferred_loader import DeferredLoader


def test_invalidate_forces_rebuild():
    calls = {"n": 0}

    def factory():
        calls["n"] += 1
        return f"client-{calls['n']}"

    dl = DeferredLoader("test-invalidate", factory, timeout=5.0)
    assert dl.get() == "client-1"
    assert dl.get() == "client-1"  # cached, no rebuild
    assert calls["n"] == 1

    dl.invalidate()
    assert not dl.is_loaded()

    assert dl.get() == "client-2"  # rebuilt after invalidate
    assert calls["n"] == 2


def test_invalidate_noop_when_empty():
    dl = DeferredLoader("test-empty", lambda: "x", timeout=5.0)
    dl.invalidate()  # nothing cached -> must not raise
    assert not dl.is_loaded()
