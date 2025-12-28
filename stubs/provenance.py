"""
Provenance Tracker Stub - Decision Audit Trail

PURPOSE:
    Stub implementation for provenance tracking.
    Records chain of custody for decisions and actions.

STATUS: Active - Used for testing audit trails
PLANNED: Full implementation with immutable logging
"""


class ProvenanceTracker:
    """Stub for recording the chain of custody for decisions."""
    def log_event(self, event: str, metadata: dict = None): return True
    def get_chain(self): return []
