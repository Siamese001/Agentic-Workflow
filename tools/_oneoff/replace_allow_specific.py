"""Bulk-replace non-canonical 'allow-specific' guardian token with canonical 'allow-log-and-swallow'.

allow-specific is NEVER canonical per _CANONICAL_GUARDIAN_TOKENS at multi_writer.py:545.
The most common pattern is except Clause: logger.warning/error(...) — maps to log_and_swallow
edge_kind whose canonical token is allow-log-and-swallow.

Skipped:
- archives/ (frozen)
- agentic_core/adg/artifact/multi_writer.py (contains the token definitions themselves in prose)
- tests/ (test fixtures may deliberately keep the non-canonical form)
"""
from pathlib import Path
import re

ROOT = Path(".")
SKIP_DIRS = {"archives", ".git", "__pycache__", ".venv", "venv", "node_modules"}
SKIP_FILES = {
    Path("agentic_core/adg/artifact/multi_writer.py"),
    Path("tests/unit/conftest.py"),  # may be test fixture
    Path(".claude/governance/scripts/_legacy_windsurf/post_cursor_agent_author_gate_capture.py"),  # hook probably uses as test
}


def iter_py_files(root: Path):
    for p in root.rglob("*.py"):
        parts = set(p.parts)
        if parts & SKIP_DIRS:
            continue
        try:
            rel = p.relative_to(root)
        except ValueError:
            rel = p
        if rel in SKIP_FILES:
            continue
        yield p, rel


pat = re.compile(r"guardian:\s*allow-specific\b")
total_files = 0
total_replacements = 0
for path, rel in iter_py_files(ROOT):
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        continue
    if "allow-specific" not in text:
        continue
    new_text, n = pat.subn("guardian: allow-log-and-swallow", text)
    if n > 0:
        path.write_text(new_text, encoding="utf-8")
        total_files += 1
        total_replacements += n
        print(f"  {n}x  {rel}")

print(f"\nTotal: {total_replacements} replacements across {total_files} files")
