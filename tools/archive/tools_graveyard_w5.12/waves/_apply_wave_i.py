"""Apply Wave I: mark Redis-dependent ADG tests with pytestmark = pytest.mark.serial.

These 4 files share Redis state and are not xdist-safe with -n auto.
Adding the serial marker documents the constraint and allows tooling to
select them separately from the parallel-safe test files.
"""

import pathlib

ROOT = pathlib.Path(r"c:\Git\Agentic-Workflow")

TARGETS = [
    "tests/adg/test_adg_projection_integrity.py",
    "tests/adg/test_adg_test_selector.py",
    "tests/adg/test_case_memory_architecture.py",
    "tests/adg/test_case_memory_creative.py",
]

for rel in TARGETS:
    p = ROOT / rel
    content = p.read_text(encoding="utf-8")

    if "pytestmark" in content:
        print(f"[SKIP] {rel} — pytestmark already present")
        continue

    # Find 'import pytest' line and insert pytestmark after it
    lines = content.split("\n")
    insert_after = -1
    for i, line in enumerate(lines):
        if line.strip() == "import pytest":
            insert_after = i
            break

    if insert_after == -1:
        print(f"[WARN] {rel} — 'import pytest' not found, skipping")
        continue

    lines.insert(insert_after + 1, "\npytestmark = pytest.mark.serial")
    new_content = "\n".join(lines)
    p.write_text(new_content, encoding="utf-8")
    print(f"[OK] {rel} — added pytestmark = pytest.mark.serial")

print("\n[DONE] Wave I applied")
