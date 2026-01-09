import pytest
pytestmark = pytest.mark.skip(reason="DEPRECATED: Test requires external modules")

"""
Sandbox file with intentional Key 49 violation.
Key 49: Maximum 5 levels from repository root.
This file is at depth 8 (sandbox/level1/level2/level3/level4/level5/level6/too_deep.py).
"""

def deeply_nested_function() -> Any:
    """This file violates Key 49 by being too deep in the hierarchy."""
    print('I am too deep!')
