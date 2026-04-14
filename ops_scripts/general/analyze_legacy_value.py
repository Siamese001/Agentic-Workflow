"""
scripts/analyze_legacy_value.py
"""

import ast
import re
from pathlib import Path
from tqdm import tqdm

LEGACY_ROOT = Path("apps_shared/legacy")


def extract_strings(node) -> list[str]:
    """Find prompt templates (long strings with formatting)."""
    strings = []
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            if len(n.value) > 50 and ("{" in n.value or "%" in n.value):
                strings.append(n.value[:100] + "...")
    return strings


def extract_regex(content: str) -> list[str]:
    """Find regex patterns."""
    return re.findall('r"([^"]{5,})"', content)


def analyze_file(file_path: Path) -> dict:
    content = file_path.read_text(encoding="utf-8")
    tree = ast.parse(content)
    return {
        "file": file_path.name,
        "classes": [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)],
        "prompts": extract_strings(tree),
        "regex_patterns": extract_regex(content),
        "methods": [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)],
    }


def generate_report():
    report = ["# LEGACY VALUE EXTRACTION REPORT", "", "## Organic Value Findings"]
    for f in tqdm(LEGACY_ROOT.glob("*.py"), desc="Processing", unit="item"):
        try:
            data = analyze_file(f)
            if data["prompts"] or data["regex_patterns"]:
                report.append(f"### File: {data['file']}")
                if data["prompts"]:
                    report.append(f"- **Prompts Found:** {len(data['prompts'])}")
                if data["regex_patterns"]:
                    report.append(f"- **Regex Patterns:** {len(data['regex_patterns'])}")
                    for r in data["regex_patterns"]:
                        report.append(f"  - `{r}`")
                report.append("")
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"Error analyzing {f.name}: {e}")
            pass
    Path("LEGACY_VALUE_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print("Report Generated: LEGACY_VALUE_REPORT.md")


if __name__ == "__main__":
    generate_report()
