"""Stub for proactive audit scanner."""

def get_proactive_scanner(**kwargs):
    """Returns a stub proactive scanner."""
    class ProactiveScanner:
        def scan(self): return {"status": "clean"}
    return ProactiveScanner()
