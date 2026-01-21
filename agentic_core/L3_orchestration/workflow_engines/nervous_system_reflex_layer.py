from __future__ import annotations

"""Reflex Layer for Nervous System."""
from typing import Any


class ReflexLayer:
    """Mock Reflex Layer for testing."""

    def __init__(self):
        self.reflexes = []
        self.status = "healthy"

    def register_reflex(self, trigger: str, action: callable) -> Any:
        """Register a reflex action."""
        self.reflexes.append({"trigger": trigger, "action": action})
        return True

    def trigger_reflex(self, event: str) -> dict[str, Any]:
        """Trigger a reflex based on event."""
        for reflex in self.reflexes:
            if reflex["trigger"] == event:
                result: Any = reflex["action"]()
                return {"handled": True, "result": result}
        return {"handled": False}

    def get_status(self) -> dict[str, Any]:
        """Get reflex layer status."""
        return {"status": self.status, "reflex_count": len(self.reflexes), "health": "ok"}
