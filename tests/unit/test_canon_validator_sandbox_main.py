"""
Sandbox file with intentional Key 50 violation.
Key 50: No root-level logic outside sovereign directories.
"""
from typing import Any

def root_logic() -> Any:
    """This function violates Key 50 by existing at root level."""
if __name__ == '__main__':
    root_logic()
