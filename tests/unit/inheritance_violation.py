"""
Inheritance Violation Test Fixture

This file simulates a class in L2_execution that does NOT inherit from L2ExecutionBaseAgent.
The CodeStandardsEnforcerAgent should flag this as an INHERITANCE_ERR.

DO NOT FIX - Used for testing inheritance validation.
"""




# VIOLATION: This class is in L2_execution but doesn't inherit from L2ExecutionBaseAgent
class BadL2Agent:
    """A class that should inherit from L2ExecutionBaseAgent but doesn't."""

    def __init__(self) -> None:
        self.name = "BadL2Agent"

    def execute(self) -> dict[str, Any]:
        """Execute some operation."""
        return {"status": "ok"}


# Another violation - inherits from wrong base
class AnotherBadAgent:
    """Another class that should inherit from L2ExecutionBaseAgent."""

    def run(self) -> None:
        pass