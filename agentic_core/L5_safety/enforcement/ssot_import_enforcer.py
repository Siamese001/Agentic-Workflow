from __future__ import annotations

from agentic_core.L2_execution.tools import write_gateway as _wg

"\nSSOT Enforcement Script\nAdds structure_blueprint.py import to files that reference L0-L5 layers\nbut don't already import from SSOT.\n"
import re
from pathlib import Path

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR
from agentic_core.L0_routing.config.path_constants import TESTS_DIR

PROJECT_ROOT = Path(__file__).resolve().parents[3]
AGENTIC_CORE = PROJECT_ROOT / AGENTIC_CORE_DIR
SSOT_IMPORT = "# [SSOT IMPORT] Structure blueprint is the single source of truth\nfrom agentic_core.L5_safety.config.structure_blueprint_config import (\n    SOVEREIGN_REGISTRY,\n    CORE_SUBFOLDER_MAP,\n)\n"
LAYER_PATTERN = re.compile("L[0-5]_")
SSOT_IMPORT_PATTERN = re.compile("from agentic_core\\.config\\.blueprint_sovereign\\.structure_blueprint")


def needs_ssot_import(content: str) -> bool:
    """Check if file references layers but doesn't import SSOT."""
    has_layer_ref = bool(LAYER_PATTERN.search(content))
    has_ssot_import = bool(SSOT_IMPORT_PATTERN.search(content))
    return has_layer_ref and (not has_ssot_import)


def add_ssot_import(file_path: Path) -> bool:
    """Add SSOT import to a file if needed."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return False
    if not needs_ssot_import(content):
        return False
    if "structure_blueprint.py" in str(file_path):
        return False
    if file_path.name == "__init__.py":
        return False
    lines = content.split("\n")
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_idx = i + 1
        elif line.startswith("class ") or line.startswith("def "):
            break
    lines.insert(insert_idx, "")
    lines.insert(insert_idx + 1, SSOT_IMPORT)
    new_content = "\n".join(lines)
    _wg.write_text(file_path, new_content, encoding="utf-8")
    return True


def main():
    """Process all Python files in agentic_core, tests, apps_shared, apps_rg, apps_lic."""
    updated = 0
    skipped = 0
    territories = [
        AGENTIC_CORE,
        PROJECT_ROOT / TESTS_DIR,
        PROJECT_ROOT / APPS_SHARED_DIR,
        PROJECT_ROOT / APPS_RG_DIR,
        PROJECT_ROOT / APPS_LIC_DIR,
    ]
    for territory in territories:
        if not territory.exists():
            continue
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        for py_file in get_python_files(territory):
            if add_ssot_import(py_file):
                print(f"[UPDATED] {py_file.relative_to(PROJECT_ROOT)}")
                updated += 1
            else:
                skipped += 1
    print(f"\n[DONE] Updated {updated} files, skipped {skipped}")


if __name__ == "__main__":
    main()
