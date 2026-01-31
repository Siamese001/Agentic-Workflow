"""Deep Deprecation Audit v2 - Find clearly deprecated/legacy Agent files."""

import re
import sys
from pathlib import Path

sys.path.insert(0, ".")
DEPRECATION_PATTERNS = [
    ("\\blegacy\\b", "legacy"),
    ("\\bdeprecated\\b", "deprecated"),
    ("\\bsuperseded\\b", "superseded"),
    ("\\barchive\\b", "archive"),
    ("use\\s+\\S+\\s+instead", "use X instead"),
    ("\\bremoved\\b", "removed"),
    ("\\bstub\\b", "stub"),
    ("\\bobsolete\\b", "obsolete"),
]


def scan_file(filepath):
    """TODO: Add documentation for scan_file."""
    findings = []
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.splitlines()[:50]
        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()
            for pattern, keyword in DEPRECATION_PATTERNS:
                if re.search(pattern, line_lower):
                    text = line.strip()[:100]
                    if text:
                        findings.append(
                            {
                                "file": filepath.name,
                                "path": str(filepath),
                                "line": line_num,
                                "keyword": keyword,
                                "text": text,
                            }
                        )
                        break
    except Exception:
        pass
    return findings


def main():
    """TODO: Add documentation for main."""
    project_root = Path(".")
    agent_files = []
    for search_dir in ["agentic_core", "apps_rg", "apps_lic", "apps_shared"]:
        search_path = project_root / search_dir
        if search_path.exists():
            for f in search_path.rglob("*Agent.py"):
                if "archives" not in str(f) and "__pycache__" not in str(f):
                    agent_files.append(f)
    all_findings = []
    for filepath in sorted(agent_files):
        findings = scan_file(filepath)
        all_findings.extend(findings)
    seen_files = set()
    unique_findings = []
    for f in all_findings:
        if f["file"] not in seen_files:
            seen_files.add(f["file"])
            unique_findings.append(f)
    actionable = []
    for f in unique_findings:
        text_lower = f["text"].lower()
        file_lower = f["file"].lower()
        if "detection" in text_lower or "detector" in text_lower:
            continue
        if "placeholder check" in text_lower:
            continue
        if "placeholder text" in text_lower:
            continue
        if "deprecated" in file_lower or "legacy" in file_lower:
            actionable.append(f)
            continue
        if "@deprecated" in text_lower:
            actionable.append(f)
            continue
        if "deprecated" in text_lower and (
            "use " in text_lower or "absorbed" in text_lower or "consolidated" in text_lower
        ):
            actionable.append(f)
            continue
        if re.search("use\\s+\\S+\\s+instead", text_lower):
            actionable.append(f)
            continue
    for f in actionable:
        file_lower = f["file"].lower()
        if "deprecated" in file_lower or "@deprecated" in f["text"].lower():
            pass
        elif "legacy" in file_lower:
            pass
        elif "use " in f["text"].lower() and " instead" in f["text"].lower():
            pass
        else:
            pass
    for f in actionable:
        pass


if __name__ == "__main__":
    main()
