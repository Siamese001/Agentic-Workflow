"""
Rogue script at Depth 2 (should be Depth 3).
This file tests automatic structural re-alignment.
"""

def rogue_function():
    """This should trigger a NESTED violation and be moved automatically."""
    return "I'm at the wrong depth!"

if __name__ == "__main__":
    print(rogue_function())
