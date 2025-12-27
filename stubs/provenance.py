class ProvenanceTracker:
    """Stub for recording the chain of custody for decisions."""
    def log_event(self, event: str, metadata: dict = None): return True
    def get_chain(self): return []
