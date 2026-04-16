from __future__ import annotations

from typing import Any


class RuntimeADGWriteGateway:
    """Single persistence seam for Runtime ADG writes.

    This keeps write mechanics out of the MCP tool layer and makes it easy to
    swap direct store persistence for a stricter Universal Write Gateway later.
    """

    def __init__(self, store_loader) -> None:
        self._store_loader = store_loader

    def persist_snapshot(self, snapshot: Any) -> str:
        store = self._store_loader.get_store_blocking()
        return store.persist(snapshot)
