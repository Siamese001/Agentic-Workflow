"""
Safety module stub for apps_rg.

This module provides safety checking functionality for resume generation.
"""

# Stub classes to prevent import errors
class HallucinationDetector:
    """Stub hallucination detector."""
    def __init__(self, *args, **kwargs: object):
        pass

    def check(self, *args, **kwargs: object):
        return {"safe": True, "confidence": 0.95}

class SafetyValidator:
    """Stub safety validator."""
    def __init__(self, *args, **kwargs: object):
        pass

    def validate(self, *args, **kwargs: object):
        return {"valid": True}

class ContentFilter:
    """Stub content filter."""
    def __init__(self, *args, **kwargs: object):
        pass

    def filter(self, *args, **kwargs: object):
        return {"filtered": False, "content": args[0] if args else ""}
