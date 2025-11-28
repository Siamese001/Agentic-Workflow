"""DEPRECATED: Legacy LIC implementation.
This file is preserved only for archival/reference.
All runtime LIC behavior now uses the atomic engine under l1/l2/l3/l4/l5.
Do NOT import from this module in new code."""

"""
LICSafetyValidator (L5 Layer)
Applies LIC QA and safety rules.
Stub only — NO logic.
"""

class LICSafetyValidator:
    """Stub safety validator."""

    def __init__(self):
        pass

    def validate(self, plan, message):
        """Return (is_safe, violations) — stub."""
        pass

    def classify_violations(self, message):
        """Return stub violation list."""
        pass
