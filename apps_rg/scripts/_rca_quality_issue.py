"""RCA: identify the 1 remaining quality issue flagged by ContentQualityAgent."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps_rg.reasoning.ContentQualityAgent import ContentQualityAgent

# Replicate execute() loop locally to see which check fires.
# Load canonical master_resume (legacy `your_resume_updated.json` retired 2026-04-30).
_CANONICAL_MASTER = Path(__file__).resolve().parents[2] / "apps_shared" / "data" / "master_resume.json"
resume = json.loads(_CANONICAL_MASTER.read_text(encoding="utf-8"))

# Get the agent's class-level constants
PLACEHOLDER_PATTERNS = ContentQualityAgent.PLACEHOLDER_PATTERNS
MIN_SECTION_LENGTHS = ContentQualityAgent.MIN_SECTION_LENGTHS

print("=== PLACEHOLDER PATTERNS ===")
for p in PLACEHOLDER_PATTERNS:
    print(f"  {p!r}")
print()
print("=== MIN_SECTION_LENGTHS ===")
print(MIN_SECTION_LENGTHS)
print()


def to_string(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(str(x) for x in content)
    if isinstance(content, dict):
        return json.dumps(content)
    return str(content)


issues = []
for section_name, content in resume.items():
    if section_name.startswith("_"):
        continue
    content_str = to_string(content)

    # Placeholder check
    for pat in PLACEHOLDER_PATTERNS:
        m = re.search(pat, content_str, re.IGNORECASE)
        if m:
            issues.append(f"[PLACEHOLDER] section={section_name!r} pattern={pat!r} match={m.group(0)!r}")

    # Min length check
    min_len = MIN_SECTION_LENGTHS.get(section_name, 10)
    if len(content_str) < min_len:
        issues.append(f"[TOO_SHORT] section={section_name!r} len={len(content_str)} < {min_len}")

    # Quantified check (experience only)
    if section_name == "experience" and content_str:
        if not re.search(
            r"\d+[%KMB]?|\$\d+|\d+\s*(years?|months?|projects?|clients?|users?|engineers?|team)",
            content_str,
            re.IGNORECASE,
        ):
            issues.append(f"[NOT_QUANTIFIED] section={section_name!r}")

# Skill validation (we already know returns 0)
print("=== ISSUES FROM PLACEHOLDER + LENGTH + QUANTIFIED CHECKS ===")
for i in issues:
    print(f"  {i}")
print(f"\nTotal: {len(issues)}")
