"""
SSOT Archive Path Refactor

Replaces all hardcoded "archives" strings with imports from structure_blueprint.ARCHIVES_DIR
to ensure Single Source of Truth compliance.

USAGE:
    python scripts/maintenance/ssot_archive_refactor_util.py --dry-run
    python scripts/maintenance/ssot_archive_refactor_util.py --execute
"""

import argparse
import re
from pathlib import Path


def find_hardcoded_archives(file_path: Path) -> list[tuple[int, str]]:
    """Find lines with hardcoded 'archives' strings."""
    matches = []
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("#"):
                continue
            if '"""' in line or "'''" in line:
                continue
            if '"archives"' in line or "'archives'" in line:
                if "ARCHIVES_DIR" in line:
                    continue
                if "#" in line and line.index("#") < line.find("archives"):
                    continue
                matches.append((i, line))
    except Exception:
        pass
    return matches


def needs_import(file_path: Path) -> bool:
    """Check if file needs ARCHIVES_DIR import."""
    try:
        content = file_path.read_text(encoding="utf-8")
        if "from agentic_core.L5_safety.validators.structure_blueprint_config import ARCHIVES_DIR" in content:
            return False
        if "ARCHIVES_DIR" in content and "import" in content:
            return False
        return True
    except:
        return False


def add_import(file_path: Path, dry_run: bool = True) -> bool:
    """Add ARCHIVES_DIR import to file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        import_line = -1
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                import_line = i
        if import_line == -1:
            for i, line in enumerate(lines):
                if '"""' in line or "'''" in line:
                    import_line = i + 1
                    break
        if import_line == -1:
            import_line = 0
        new_import = "from agentic_core.L5_safety.validators.structure_blueprint_config import ARCHIVES_DIR"
        lines.insert(import_line + 1, new_import)
        if not dry_run:
            file_path.write_text("\n".join(lines), encoding="utf-8")
        return True
    except Exception:
        return False


def replace_hardcoded_archives(file_path: Path, dry_run: bool = True) -> int:
    """Replace hardcoded 'archives' with ARCHIVES_DIR."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        content = re.sub("([\"\\'])archives\\1", "ARCHIVES_DIR", content)
        replacements = content.count("ARCHIVES_DIR") - original_content.count("ARCHIVES_DIR")
        if content != original_content and (not dry_run):
            file_path.write_text(content, encoding="utf-8")
        return replacements
    except Exception:
        return 0


def main():
    """TODO: Add documentation for main."""
    parser = argparse.ArgumentParser(description="SSOT Archive Path Refactor")
    parser.add_argument("--execute", action="store_true", help="Execute changes (default is dry-run)")
    args = parser.parse_args()
    dry_run = not args.execute
    agentic_core = Path("agentic_core")
    files_to_fix = []
    for py_file in agentic_core.rglob("*.py"):
        if "archives" in py_file.parts:
            continue
        if "__pycache__" in py_file.parts:
            continue
        matches = find_hardcoded_archives(py_file)
        if matches:
            files_to_fix.append((py_file, matches))
    if not files_to_fix:
        return 0
    total_replacements = 0
    for file_path, matches in files_to_fix:
        if dry_run:
            if needs_import(file_path):
                pass
        else:
            if needs_import(file_path):
                if add_import(file_path, dry_run=False):
                    pass
            replacements = replace_hardcoded_archives(file_path, dry_run=False)
            if replacements > 0:
                total_replacements += replacements
    if dry_run:
        pass
    return 0


if __name__ == "__main__":
    exit(main())
