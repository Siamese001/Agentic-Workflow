"""Bulk-patch stale action versions and Python versions in all remaining workflows."""

from pathlib import Path

WF_DIR = Path(r"c:\Git\Agentic-Workflow\.github\workflows")

REPLACEMENTS = [
    ("actions/checkout@v3", "actions/checkout@v4"),
    ("actions/setup-python@v4", "actions/setup-python@v5"),
    ("actions/setup-python@v3", "actions/setup-python@v5"),
    ("python-version: '3.11'", "python-version: '3.12'"),
    ('python-version: "3.11"', 'python-version: "3.12"'),
]

for f in sorted(WF_DIR.glob("*.yml")):
    content = f.read_text(encoding="utf-8")
    original = content
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)
    if content != original:
        f.write_text(content, encoding="utf-8")
        print(f"PATCHED {f.name}")
    else:
        print(f"  ok    {f.name}")
