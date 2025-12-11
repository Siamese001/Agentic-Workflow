# scripts/auto_create_test.py
import sys
from pathlib import Path

for f in sys.argv[1:]:
    p = Path(f)
    test_file = Path("tests") / p.relative_to(".").with_name(f"test_{p.name}")
    if not test_file.exists():
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(f"def test_{p.stem}(): ...\n")
