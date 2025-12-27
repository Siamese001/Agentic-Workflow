"""Stub for L1 identity module."""

class Identity:
    """Stub for agent identity management."""
    def __init__(self, name: str = "stub_agent"):
        self.name = name
        self.id = f"agent-{name}"
        self.capabilities = []
    
    def get_identity(self) -> dict:
        return {"name": self.name, "id": self.id, "capabilities": self.capabilities}
