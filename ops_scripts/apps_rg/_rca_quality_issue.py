"""RCA: identify quality issues using inlined placeholder rules (reasoning agent removed)."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

PLACEHOLDER_PATTERNS = [
    r"\[(?:NAME|COMPANY|TITLE|PLACEHOLDER|YOUR_NAME|INSERT)\]",
    r"\{(?:name|company|title|placeholder|your_name|insert)\}",
    r"<(?:NAME|COMPANY|TITLE|PLACEHOLDER)>",
    r"\bTODO\b",
    r"\bTBD\b",
    r"\bFIXME\b",
    r"\bXXX\b",
    r"Lorem ipsum",
    r"PLACEHOLDER",
]
MIN_SECTION_LENGTHS = {
    "summary": 50,
    "experience": 100,
    "skills": 20,
    "education": 30,
}

_CANONICAL_MASTER = Path(__file__).resolve().parents[2] / "apps_shared" / "data" / "master_resume.json"
resume = json.loads(_CANONICAL_MASTER.read_text(encoding="utf-8"))

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
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, content_str, re.IGNORECASE):
            issues.append(f"Placeholder in {section_name}: {pattern}")
    min_length = MIN_SECTION_LENGTHS.get(section_name, 10)
    if len(content_str) < min_length:
        issues.append(f"{section_name} too short ({len(content_str)} < {min_length})")

print(f"Issues found: {len(issues)}")
for issue in issues:
    print(f"  - {issue}")
