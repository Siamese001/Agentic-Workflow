"""
Batch-fix REPLACE violations in tests/ directory.
Adds SSOT import and replaces hardcoded directory strings with path_constants.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CONST_MAP = {
    "agentic_core": "AGENTIC_CORE_DIR",
    "apps_lic": "APPS_LIC_DIR",
    "apps_rg": "APPS_RG_DIR",
    "apps_shared": "APPS_SHARED_DIR",
    "system_learning": "SYSTEM_LEARNING_DIR",
    "tools": "TOOLS_DIR",
    "tests": "TESTS_DIR",
    "ops_scripts": "OPS_SCRIPTS_DIR",
    "L0_routing": "L0_ROUTING_DIR",
    "L1_cognition": "L1_COGNITION_DIR",
    "L2_execution": "L2_EXECUTION_DIR",
    "L3_orchestration": "L3_ORCHESTRATION_DIR",
    "L4_state": "L4_STATE_DIR",
    "L6_observability": "L6_OBSERVABILITY_DIR",
}

IMPORT_LINE = "from agentic_core.L0_routing.config.path_constants import ("
IMPORT_MODULE = "agentic_core.L0_routing.config.path_constants"


def get_needed_constants(filepath: Path, const_map: dict) -> set[str]:
    src = filepath.read_text(encoding="utf-8")
    needed = set()
    for dir_str, const_name in const_map.items():
        # Match quoted string literals only (single or double quotes)
        # guardian: allow-path-string
        pattern = r'(?<![a-zA-Z0-9_])(?:\'|")' + re.escape(dir_str) + r'(?:\'|")(?![a-zA-Z0-9_/.])'
        if re.search(pattern, src):
            needed.add(const_name)
    return needed


def already_imports(src: str, const: str) -> bool:
    # guardian: allow-path-string
    return bool(re.search(r"\b" + re.escape(const) + r"\b", src.split("def ")[0].split("class ")[0]))


def add_import(src: str, needed_consts: set[str]) -> str:
    """Insert or extend path_constants import block near top of file."""
    # Check if import block already exists
    existing_match = re.search(
        r"from agentic_core\.L0_routing\.config\.path_constants import \(([^)]*)\)",
        src,
        re.DOTALL,
    )
    if existing_match:
        existing_body = existing_match.group(1)
        existing_consts = set(re.findall(r"\b[A-Z_]+\b", existing_body))
        missing = needed_consts - existing_consts
        if not missing:
            return src
        # Append missing consts to existing block
        sorted_missing = sorted(missing)
        old_block = existing_match.group(0)
        lines = existing_body.rstrip().rstrip(",")
        new_body = lines + ",\n    " + ",\n    ".join(sorted_missing) + ","
        new_block = "from agentic_core.L0_routing.config.path_constants import (" + new_body + "\n)"
        return src.replace(old_block, new_block)

    # Also check single-line import
    single_match = re.search(r"from agentic_core\.L0_routing\.config\.path_constants import ([^\n]+)", src)
    if single_match:
        existing_line = single_match.group(0)
        existing_consts = set(re.findall(r"\b[A-Z_]+\b", single_match.group(1)))
        missing = needed_consts - existing_consts
        if not missing:
            return src
        all_consts = sorted(existing_consts | missing)
        new_block = (
            "from agentic_core.L0_routing.config.path_constants import (\n    "
            + ",\n    ".join(all_consts)
            + ",\n)"
        )
        return src.replace(existing_line, new_block)

    # No existing import — insert after last stdlib/third-party import block
    sorted_consts = sorted(needed_consts)
    new_import = (
        "from agentic_core.L0_routing.config.path_constants import (\n    "
        + ",\n    ".join(sorted_consts)
        + ",\n)"
    )

    # Find insertion point: after "from __future__" block or after last import
    lines = src.splitlines(keepends=True)
    insert_after = 0
    in_imports = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if (
            stripped.startswith("from __future__")
            or stripped.startswith("import ")
            or stripped.startswith("from ")
        ):
            insert_after = i + 1
            in_imports = True
        elif in_imports and stripped == "":
            continue
        elif in_imports:
            break

    # Insert after last import line (after its trailing blank line)
    lines.insert(insert_after, "\n" + new_import + "\n")
    return "".join(lines)


def replace_literals(src: str, const_map: dict) -> str:
    """Replace ALL hardcoded dir string literals with constants."""
    for dir_str, const_name in const_map.items():
        # Replace double-quoted
        # guardian: allow-path-string
        src = re.sub(r'(?<![a-zA-Z0-9_])"' + re.escape(dir_str) + r'"(?![a-zA-Z0-9_/.])', const_name, src)
        # Replace single-quoted
        # guardian: allow-path-string
        src = re.sub(r"(?<![a-zA-Z0-9_])'" + re.escape(dir_str) + r"'(?![a-zA-Z0-9_/.])", const_name, src)
    return src


def fix_file(filepath: Path, needed_consts: set[str]) -> bool:
    src = filepath.read_text(encoding="utf-8")
    new_src = replace_literals(src, CONST_MAP)
    new_src = add_import(new_src, needed_consts)
    if new_src != src:
        filepath.write_text(new_src, encoding="utf-8")
        return True
    return False


def main():
    scan_file = ROOT / "artifacts" / "hardcoded_path_scan.json"
    data = json.load(scan_file.open())
    hits = [h for h in data["all_hits"] if h["classification"] == "REPLACE"]
    sep = os.sep
    test_hits = [h for h in hits if h["file"].startswith("tests" + sep) or sep + "tests" + sep in h["file"]]

    by_file: dict[str, list] = {}
    for h in test_hits:
        by_file.setdefault(h["file"], []).append(h)

    fixed = 0
    errors = []
    for rel_path, violations in sorted(by_file.items()):
        filepath = ROOT / rel_path
        needed = {v["ssot_constant"] for v in violations}
        try:
            changed = fix_file(filepath, needed)
            status = "FIXED" if changed else "SKIP"
            print(f"{status}: {rel_path} ({len(violations)} violations, consts: {sorted(needed)})")
            if changed:
                fixed += 1
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            raise
            errors.append((rel_path, str(e)))
            print(f"ERROR: {rel_path}: {e}")

    print(f"\nDone: {fixed} files fixed, {len(errors)} errors.")
    for p, e in errors:
        print(f"  ERROR {p}: {e}")


if __name__ == "__main__":
    main()
