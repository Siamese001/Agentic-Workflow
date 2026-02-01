r"""
File: PascalSovereigntyFixer.py
Path: C:\Git\Agentic-Workflow\PascalSovereigntyFixer.py
Status: FINAL - GOLD MASTER (Phase 4)
Rationale:
    Removes legacy commentary regarding 'healer_mixin.py' to produce a clean,
    professional artifact. The logic is now fully reliant on the '_mixin.py'
    pattern matcher verified in Phase 2/3.
"""

import ast
import os
import platform
import re
import sys
import time
from pathlib import Path
from typing import Literal


# SSOT Integration with fast-fail pruning
def get_python_files_fast(root: Path) -> list[Path]:
    """
    Optimized repository scanner that prunes heavy/irrelevant directories
    before they enter the pipeline.
    """
    python_files = []
    # Prune list based on project-specific 'slow' directories
    # Critical Analysis: Excluding .git and archives prevents the scanner
    # from wasting cycles on version history or dead code.
    exclude_dirs = {".git", "archives", "__pycache__", "node_modules", "venv", ".env"}

    for dirpath, dirnames, filenames in os.walk(root):
        # In-place directory pruning for os.walk prevents recursion into excluded paths
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for filename in filenames:
            if filename.endswith(".py"):
                python_files.append(Path(dirpath) / filename)
    return python_files


FileType = Literal["AGENT", "CLASS", "MIXIN", "UTILITY", "IGNORE"]


class PascalSovereigntyFixer:
    """Enforces strict file naming conventions based on AST content analysis."""

    def __init__(self, dry_run: bool = False, verbose: bool = False, validate_only: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.validate_only = validate_only
        self.stats = {
            "analyzed": 0,
            "compliant": 0,
            "renamed": 0,
            "imports_fixed": 0,
            "violations": {"AGENT": 0, "CLASS": 0, "MIXIN": 0, "UTILITY": 0},
        }
        # CACHE: Track file paths in memory to avoid repetitive disk scanning (O(1) lookups)
        self.file_registry: list[Path] = []

    def classify_file(self, path: Path) -> FileType:
        """Analyze file AST to determine architectural role with strict test exemptions."""
        # --- EXEMPTION PATCH: TESTS ---
        # Critical Analysis: Preserving Pytest Discovery. Renaming test_*.py to PascalCase
        # would render the CI/CD pipeline blind as pytest would ignore the files.
        if path.name.startswith("test_") or path.name.endswith("_test.py") or "tests" in path.parts:
            return "IGNORE"

        if path.name == "conftest.py" or path.name == "__init__.py":
            return "IGNORE"

        # --- EXEMPTION PATCH: MIXINS ---
        # Mixins are explicitly categorized to enforce snake_case naming conventions,
        # differentiating them from the PascalCase requirement of primary Agent/Class files.
        if path.name.endswith("_mixin.py") or path.name.endswith("Mixin.py"):
            return "MIXIN"

        # --- EXEMPTION PATCH: SSOT ---
        # Critical SSOT files that have hundreds of import references.
        critical_ssot_files = {
            "structure_blueprint.py",  # 926+ import references
            "tool_registry.py",  # Tool registration system
            "execute_ssot.py",  # SSOT execution orchestrator - do not rename
        }
        if path.name in critical_ssot_files:
            return "IGNORE"

        try:
            if not path.exists() or path.stat().st_size == 0:
                return "IGNORE"
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError, OSError):
            return "IGNORE"

        has_class = False
        is_agent = False

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_class = True
                if node.name.endswith("Agent"):
                    is_agent = True
                for base in node.bases:
                    if (isinstance(base, ast.Name) and "Agent" in base.id) or (
                        isinstance(base, ast.Attribute) and "Agent" in base.attr
                    ):
                        is_agent = True

        if is_agent:
            return "AGENT"
        elif has_class:
            return "CLASS"
        else:
            return "UTILITY"

    def update_imports(self, old_name: str, new_name: str) -> int:
        """Refactors imports using the in-memory registry to avoid O(N²) disk hits."""
        count = 0
        old_mod, new_mod = old_name.replace(".py", ""), new_name.replace(".py", "")

        # Ultra-Precision Regex: Handles 'from x import', 'import x', and 'import x as y'
        # Critical Analysis: Expanded to handle relative imports (e.g., 'from .old_mod import')
        # by adding an optional dot-prefix group. This is vital for maintaining integrity
        # in hierarchical multi-agent systems where local package imports are standard.
        regex_from = re.compile(
            r"(?P<prefix>from\s+\.*)" + re.escape(old_mod) + r"(?P<suffix>\s+import)"
        )
        regex_import = re.compile(
            rf"(?P<prefix>import\s+){re.escape(old_mod)}(?P<suffix>(\s+as\s+\w+)?(\s*,|\s|$))"
        )
        # Note: The \.* in regex_from captures any number of leading dots for relative paths,
        # ensuring that 'from ..llm_mixin' correctly becomes 'from ..new_name' (or the new name).

        # Optimized: Scans in-memory file_registry instead of hitting disk rglob
        for _i, path in enumerate(self.file_registry):
            if path.name == new_name or not path.exists():
                continue
            try:
                content = path.read_text(encoding="utf-8")
                if old_mod not in content:
                    continue

                new_content = regex_from.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", content)
                new_content = regex_import.sub(r"\g<prefix>" + new_mod + r"\g<suffix>", new_content)

                if new_content != content:
                    if not self.dry_run:
                        path.write_text(new_content, encoding="utf-8")
                    count += 1
            except:
                continue
        return count

    def run(self, root: Path) -> int:
        """Main orchestration loop."""
        print(f"[SOVEREIGNTY] {'DRY RUN' if self.dry_run else 'EXECUTE'} MODE")
        print("=" * 60)

        if not self.verify_environment():
            return 1

        print("Scanning repository (Fast One-Time Pass)...")
        self.file_registry = get_python_files_fast(root)
        self.stats["analyzed"] = len(self.file_registry)

        # Iterating over a copy to allow registry updates during renames
        for idx, path in enumerate(list(self.file_registry)):
            if not path.exists():
                continue
            ftype = self.classify_file(path)
            if ftype == "IGNORE":
                continue

            new_name = self.get_compliant_name(path, ftype)
            if new_name and new_name != path.name:
                self.stats["violations"][ftype] += 1
                print(f"\n[DETECT] {path.name} ({ftype}) -> {new_name}")
                # [CHANGED] From safe_rename_windows to resolve_collision_and_rename
                if self.resolve_collision_and_rename(path, new_name):
                    self.stats["renamed"] += 1
                    # Update in-memory tracker for subsequent import refactors
                    dest = path.parent / new_name

                    # Only update registry if the file wasn't deleted (duplicate merge)
                    if dest.exists():
                        self.file_registry[idx] = dest

                    self.stats["imports_fixed"] += self.update_imports(path.name, new_name)
            else:
                self.stats["compliant"] += 1

        print("\n" + "=" * 60)
        print(f"Total files analyzed: {self.stats['analyzed']}")
        print(f"Compliant files:      {self.stats['compliant']}")
        total_violations = sum(self.stats["violations"].values())
        print(f"Violations detected:  {total_violations}")
        print(f"  - Agents:  {self.stats['violations']['AGENT']}")
        print(f"  - Classes: {self.stats['violations']['CLASS']}")
        print(f"  - Utils:   {self.stats['violations']['UTILITY']}")
        print(f"  - Mixins:  {self.stats['violations']['MIXIN']}")
        if not self.dry_run:
            print(f"Files Renamed:        {self.stats['renamed']}")
            print(f"Imports Fixed:        {self.stats['imports_fixed']}")

        # Critical Analysis: Returning exit 1 on violations ensures git hooks
        # block non-compliant commits.
        return 0 if (not self.validate_only or total_violations == 0) else 1

    def verify_environment(self) -> bool:
        """Checks for LongPathsEnabled on Windows."""
        if platform.system() == "Windows":
            try:
                import winreg

                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\FileSystem"
                )
                value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
                if value != 1:
                    print("[WARNING] Windows LongPathsEnabled is NOT set to 1.")
                    if not self.dry_run:
                        return False
            except:
                pass
        return True

    def resolve_collision_and_rename(self, src: Path, dest_name: str) -> bool:
        """
        Handles renaming with intelligent collision resolution.
        Returns True if the VIOLATION was resolved (either by rename, delete, or move).
        """
        dest = src.parent / dest_name

        # Case 0: Trivial match
        if src.name == dest_name:
            return False

        if self.dry_run:
            print(f"  [PLAN] Rename {src.name} -> {dest_name}")
            return True

        # Case 1: Destination Conflict Detection
        is_collision = False
        if dest.exists():
            try:
                # Resolve paths to handle case-insensitivity on Windows
                if dest.resolve() != src.resolve():
                    is_collision = True
            except OSError:
                is_collision = True

        if is_collision:
            print(f"  [COLLISION] Target {dest_name} already exists. Analyzing content...")
            try:
                # Critical Analysis: Binary read ensures exact match without encoding issues.
                src_content = src.read_bytes()
                dest_content = dest.read_bytes()

                if src_content == dest_content:
                    print(
                        "  [ANALYSIS] Files are IDENTICAL. Remediation: Deleting redundant violator."
                    )
                    print(f"  [ACTION] DELETE {src.name}")
                    src.unlink()
                    return True  # Violation resolved by deletion
                else:
                    # Divergent content: Rename to .CONFLICT to preserve data
                    print(
                        "  [ANALYSIS] Files are DIFFERENT. Remediation: Preserving data via conflict rename."
                    )
                    timestamp = int(time.time())
                    conflict_name = f"{dest_name}.CONFLICT_{timestamp}"
                    conflict_path = src.parent / conflict_name

                    print(f"  [ACTION] RENAME {src.name} -> {conflict_name}")
                    src.rename(conflict_path)
                    return True  # Violation resolved by moving aside
            except Exception as e:
                print(f"  [ERROR] Failed to resolve collision: {e}")
                return False

        # Case 2: Standard Rename (or Case-Only Rename)
        try:
            # Atomic temp shuffle for Windows case-sensitivity support
            temp = src.parent / f"__temp_{src.name}"
            src.rename(temp)
            temp.rename(dest)
            return True
        except OSError as e:
            print(f"  [ERROR] Rename failed: {e}")
            return False

    def get_compliant_name(self, path: Path, file_type: FileType) -> str | None:
        """Calculates the target filename based on the primary class definition."""
        if file_type == "IGNORE":
            return None

        # --- MIXIN STANDARDIZATION ---
        # Logic: Forces Mixins to snake_case.
        # Example: HygieneMixin.py -> hygiene_mixin.py
        if file_type == "MIXIN":
            stem = path.stem
            # Acronym-aware snake_case conversion (Pass 1: LLMProvider -> LLM_Provider)
            s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", stem)
            # Pass 2: camelCase boundaries (llmProvider -> llm_Provider)
            clean_stem = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

            if not clean_stem.endswith("_mixin"):
                clean_stem += "_mixin"

            target = f"{clean_stem}.py"
            return target if target != path.name else None

        if file_type == "UTILITY":
            return None
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            if not classes:
                return None
            primary = classes[0]
            stem_clean = path.stem.replace("_", "").lower()
            for cls_name in classes:
                if cls_name.lower() == stem_clean:
                    primary = cls_name
                    break
            target_name = primary
            if file_type == "AGENT" and not target_name.endswith("Agent"):
                target_name += "Agent"
            return f"{target_name}.py"
        except:
            return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Pascal Sovereignty Fixer")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--validate", action="store_true", help="Check compliance only")
    args = parser.parse_args()
    is_dry_run = args.dry_run or args.validate
    sys.exit(PascalSovereigntyFixer(dry_run=is_dry_run, validate_only=args.validate).run(Path(".")))


if __name__ == "__main__":
    main()
