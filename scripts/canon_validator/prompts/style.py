"""
Code style and hygiene few-shot patterns.
Used by CodeStyleGuardian, HygieneGuardian.
"""

FEW_SHOT_STYLE = """
FEW-SHOT CODE STYLE FIXES (CodeStyleGuardian — Follow exactly):

EXAMPLE 1: Import Ordering (isort)
BAD:
import os
import pandas as pd
from pathlib import Path

GOOD (isort sections):
import os

from pathlib import Path

import pandas as pd

EXAMPLE 2: Type Hints (Modern Python)
BAD:
def process(data):
    return data.upper()

GOOD:
def process(data: str) -> str:
    return data.upper()

Always follow black formatting.
Always use type hints.
Always use f-strings.
"""

FEW_SHOT_HYGIENE = """
FEW-SHOT HYGIENE FIXES (HygieneGuardian — Follow exactly):

EXAMPLE 1: Unused Import
BAD:
import pandas as pd
# pandas never used

GOOD:
# Remove line entirely

EXAMPLE 2: Unused Variable
BAD:
temp = setup()
# temp never read

GOOD:
setup()  # Or remove if side-effect free

Rules:
- Remove unused imports ALWAYS
- Remove unused variables ONLY if not in loop/setup
- Never remove __all__, abstract methods, dunder
"""
