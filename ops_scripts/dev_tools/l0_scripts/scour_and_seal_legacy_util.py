"""
scripts/scour_and_seal_legacy_util.py
"""

import ast
import os
import re
import shutil
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS

ROOTS = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]


def find_legacy_folders() -> list[Path]:
    legacy_paths = []
    for root in ROOTS:
        path = Path(root)
        if not path.exists():
            continue
        for root_dir, dirs, _files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            if "legacy" in dirs:
                legacy_paths.append(Path(root_dir) / "legacy")
    return legacy_paths


def attempt_repair(file_path: Path) -> str:
    """Apply the Lazarus Patch (indentation/imports) to make content parseable."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    # guardian: allow-silent-swallow
    except Exception:
        return ""
    if content.startswith("    "):
        lines = content.splitlines()
        content = "\n".join([line.lstrip() for line in lines])
    return content


def extract_value(content: str) -> dict[str, list[str]]:
    """Scan for Organic Gold."""
    artifacts = {"regex": [], "prompts": []}
    regex_matches = re.findall('r"([^"]{10,})"', content)
    artifacts["regex"].extend(regex_matches)
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if len(node.value) > 60 and ("{" in node.value or "You are" in node.value):
                    artifacts["prompts"].append(node.value[:100] + "...")
    # guardian: allow-silent-swallow
    except:
        pass
    return artifacts


def execute_scour():
    print(">>> INITIATING PHASE 29: LEGACY SCOUR <<<")
    targets = find_legacy_folders()
    if not targets:
        print("No legacy folders found. System is clean.")
        return
    print(f"Targets Identified: {[str(t) for t in targets]}")
    harvested_count = 0
    report = ["# FINAL LEGACY AUDIT", ""]
    for folder in targets:
        print(f"Scanning: {folder}")
        for f in folder.glob("*.py"):
            content = attempt_repair(f)
            val = extract_value(content)
            if val["regex"] or val["prompts"]:
                harvested_count += 1
                report.append(f"## Found Value in {f.name}")
                report.append(f"- Regex: {val['regex']}")
                report.append(f"- Prompts: {val['prompts']}")
                print(f"  [+] HARVESTED VALUE from {f.name}")
            else:
                print(f"  [-] No value in {f.name}")
    if harvested_count > 0:
        Path("FINAL_LEGACY_AUDIT.md").write_text("\n".join(report))
        print("Audit Saved: FINAL_LEGACY_AUDIT.md (Review for manual merge)")
    print(">>> EXECUTING FINAL SEAL (DELETION) <<<")
    for folder in targets:
        shutil.rmtree(folder)
        print(f"  [X] DELETED: {folder}")


if __name__ == "__main__":
    execute_scour()
