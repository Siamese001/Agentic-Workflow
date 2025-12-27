"""Stub for fact_checker module."""

class FactChecker:
    """Stub for fact checking functionality."""
    def __init__(self):
        self.verified_facts = []
    
    def check(self, claim: str) -> dict:
        return {
            "claim": claim,
            "verified": True,
            "confidence": 0.95,
            "sources": []
        }
    
    def verify_multiple(self, claims: list) -> list:
        return [self.check(claim) for claim in claims]
