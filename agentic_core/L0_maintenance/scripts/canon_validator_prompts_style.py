"""
Code style and hygiene few-shot patterns.
Used by CodeStyleGuardian, HygieneGuardian.
"""
few_shot_style: Any = '\nFEW-SHOT CODE STYLE FIXES (CodeStyleGuardian — Follow exactly):\n\nEXAMPLE 1: Import Ordering (isort)\nBAD:\nimport os\nfrom pathlib import Path\n\nimport pandas as pd\n\nGOOD (isort sections):\nimport os\n\nfrom pathlib import Path\n\nimport pandas as pd\n\nEXAMPLE 2: Type Hints (Modern Python)\nBAD:\ndef process(data):\n    return data.upper()\n\nGOOD:\ndef process(data: str) -> str:\n    return data.upper()\n\nAlways follow black formatting.\nAlways use type hints.\nAlways use f-strings.\n'
few_shot_hygiene: Any = '\nFEW-SHOT HYGIENE FIXES (HygieneGuardian — Follow exactly):\n\nEXAMPLE 1: Unused Import\nBAD:\nimport pandas as pd\n# pandas never used\n\nGOOD:\n# Remove line entirely\n\nEXAMPLE 2: Unused Variable\nBAD:\ntemp = setup()\n# temp never read\n\nGOOD:\nsetup()  # Or remove if side-effect free\n\nRules:\n- Remove unused imports ALWAYS\n- Remove unused variables ONLY if not in loop/setup\n- Never remove __all__, abstract methods, dunder\n'
