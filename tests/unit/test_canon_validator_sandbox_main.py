import pytest
pytestmark = pytest.mark.skip(reason="DEPRECATED: Test requires external modules")

"""
Sandbox file with intentional Key 50 violation.
Key 50: No root-level logic outside sovereign directories.
"""

def root_logic() -> Any:
    """This function violates Key 50 by existing at root level."""
if __name__ == '__main__':
    root_logic()
