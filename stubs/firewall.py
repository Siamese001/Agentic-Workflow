class Firewall:
    """Stub for network/egress filtering."""
    def allow(self, request: dict) -> bool: return True
    def block(self, request: dict) -> bool: return False
