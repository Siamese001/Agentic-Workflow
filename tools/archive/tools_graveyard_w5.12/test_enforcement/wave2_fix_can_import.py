"""Fix CAN_IMPORT pattern in the 3 remaining phase test files.

Pattern:
  try:
      from X import Y
      CAN_IMPORT = True
  except ImportError as e:
      print(f"...")
      CAN_IMPORT = False

  ... later in test methods:
      if not CAN_IMPORT:
          pytest.skip("Cannot import ...")
      ... or ...
      @pytest.mark.skipif(not CAN_IMPORT, reason="...")

Fix: Direct import, remove all CAN_IMPORT checks.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

FILES = [
    "tests/unit/test_phase22_comprehensive.py",
    "tests/unit/test_phase22_medium_severity_fixes.py",
    "tests/unit/test_phase23_low_severity_fixes.py",
]


def fix_file(filepath: pathlib.Path) -> str:
    source = filepath.read_text(encoding="utf-8", errors="replace")
    original = source

    # 1. Replace try/except ImportError block with direct import
    source = re.sub(
        r'try:\n'
        r'    from (\S+) import (\S+)\n'
        r'    CAN_IMPORT = True\n'
        r'except ImportError as e:\n'
        r'    print\(f"[^"]*"\)\n'
        r'    CAN_IMPORT = False\n',
        r'from \1 import \2\n',
        source,
    )

    # 2. Remove @pytest.mark.skipif(not CAN_IMPORT, ...) decorators
    source = re.sub(
        r'\s*@pytest\.mark\.skipif\(not CAN_IMPORT,\s*reason="[^"]*"\)\n',
        '\n',
        source,
    )

    # 3. Remove inline "if not CAN_IMPORT: pytest.skip(...)" blocks
    # Pattern: "        if not CAN_IMPORT:\n            pytest.skip(...)\n"
    source = re.sub(
        r'\s+if not CAN_IMPORT:\n\s+pytest\.skip\([^\)]+\)\n',
        '\n',
        source,
    )

    # 4. Remove "if CAN_IMPORT: ... else: pytest.skip(...)" blocks
    # This is trickier - replace the if/else with just the if body
    source = re.sub(
        r'(\s+)if CAN_IMPORT:\n((?:\1    [^\n]+\n)+)\1else:\n\1    pytest\.skip\([^\)]+\)\n',
        r'\2',
        source,
    )

    # 5. Clean up multiple blank lines
    while "\n\n\n\n" in source:
        source = source.replace("\n\n\n\n", "\n\n\n")

    if source != original:
        filepath.write_text(source, encoding="utf-8")
        return "fixed"
    return "unchanged"


def main():
    for fp_str in FILES:
        fp = ROOT / fp_str
        if not fp.exists():
            print(f"  MISSING: {fp_str}")
            continue
        result = fix_file(fp)
        print(f"  {result.upper()}: {fp_str}")

    # Verify syntax
    import ast
    for fp_str in FILES:
        fp = ROOT / fp_str
        if fp.exists():
            try:
                ast.parse(fp.read_text(encoding="utf-8", errors="replace"))
                print(f"  SYNTAX OK: {fp_str}")
            except SyntaxError as e:
                print(f"  SYNTAX ERROR: {fp_str}: {e}")


if __name__ == "__main__":
    main()
