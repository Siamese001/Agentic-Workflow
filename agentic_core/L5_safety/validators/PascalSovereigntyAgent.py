"""
File: agentic_core/L5_safety/validators/PascalSovereigntyAgent.py
Path: agentic_core/L5_safety/validators/PascalSovereigntyAgent.py
Rationale:
    Canonizes the PascalSovereigntyFixer as a first-class L5 Agent.
    Relocated from L0_maintenance/scripts to L5_safety/validators to
    centralize enforcement and enable auto-discovery by execute_ssot.py.

    Integration Features:
    - Inherits from SovereignBaseAgent for full infrastructure support
    - Implements standard agent interface for execute_ssot.py orchestration
    - Preserves all original PascalSovereigntyFixer functionality
    - Adds heal_repository() method for standard healing chain integration
"""

import ast
import re
import sys
import os
import platform
import time
from pathlib import Path
from typing import Literal, Any
from dataclasses import dataclass, field

# Optional: Import SovereignBaseAgent if available for full integration
try:
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from agentic_core.L5_safety.validators.decorators import standard_heal

    HAS_SOVEREIGN_BASE = True
except ImportError:
    HAS_SOVEREIGN_BASE = False
    SovereignBaseAgent = object

    def standard_heal(func):
        """Fallback decorator when full infrastructure unavailable."""
        return func


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


@dataclass
class PascalSovereigntyAgent(SovereignBaseAgent):
    """
    Enforces strict file naming conventions and resolves SSOT collisions.

    This agent canonizes the PascalSovereigntyFixer functionality as a
    first-class L5 safety agent with full orchestration capabilities.
    """

    project_root: Path = field(default_factory=Path.cwd)
    dry_run: bool = False
    verbose: bool = False
    validate_only: bool = False

    def __post_init__(self):
        if HAS_SOVEREIGN_BASE and hasattr(super(), "__post_init__"):
            super().__post_init__()
        # [HARDENING] Ensure path is absolute for resolve() calls
        self.project_root = self.project_root.resolve()
        self.stats = {
            "analyzed": 0,
            "compliant": 0,
            "renamed": 0,
            "imports_fixed": 0,
            "collisions_resolved": 0,
            "violations": {"AGENT": 0, "CLASS": 0, "MIXIN": 0, "UTILITY": 0},
        }
        # CACHE: Track file paths in memory to avoid repetitive disk scanning (O(1) lookups)
        self.file_registry: list[Path] = []

    def run(self) -> dict[str, Any]:
        """Entry point for execute_ssot.py orchestration."""
        print(f"[SOVEREIGNTY] Executing Pascal Sovereignty Audit at {self.project_root}")
        success = self._orchestrate_audit(self.project_root)
        return {
            "success": success == 0,
            "stats": self.stats,
            "summary": f"Renamed: {self.stats['renamed']}, Collisions: {self.stats['collisions_resolved']}",
        }

    def _orchestrate_audit(self, root: Path) -> int:
        """Original core logic from PascalSovereigntyFixer.py."""
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
                    if not self.dry_run:
                        self.stats["renamed"] += 1
                        self.stats["collisions_resolved"] += 1

                        # [HARDENED] Update in-memory tracker AFTER successful file operation
                        dest = path.parent / new_name

                        # Only update registry if the file exists and wasn't deleted (duplicate merge)
                        if dest.exists():
                            self.file_registry[idx] = dest
                            # Update imports only after registry is updated
                            self.stats["imports_fixed"] += self.update_imports(path.name, new_name)
                        else:
                            # File was deleted due to duplicate content - remove from registry
                            self.file_registry[idx] = None
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
            print(f"Collisions Resolved:  {self.stats['collisions_resolved']}")

        # Critical Analysis: Returning exit 1 on violations ensures git hooks
        # block non-compliant commits.
        return 0 if (not self.validate_only or total_violations == 0) else 1

    def classify_file(self, path: Path) -> FileType:
        """
        Analyze file AST to determine architectural role with strict test exemptions.

        CRITICAL ANALYSIS:
        Hardened definition of 'AGENT':
        1. Class name ends in 'Agent'.
        2. Inherits from *Agent.
        3. [NEW] Resides in a structural 'agents/' or 'validators/' directory.
        """
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

        # [HARDENED] Structural Location Check
        # If the file is in an 'agents' or 'validators' folder, it IS an agent contextually.
        is_structural_agent = "agents" in path.parts or "validators" in path.parts

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
            # [HARDENED] Enforce Agent suffix if structurally located in agent territory
            if is_structural_agent:
                return "AGENT"
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
        for i, path in enumerate(self.file_registry):
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

        [HARDENED] Fixed race conditions, added verification, rollback, and proper Windows handling.
        """
        dest = src.parent / dest_name

        # Case 0: Trivial match
        if src.name == dest_name:
            return False

        if self.dry_run:
            print(f"  [PLAN] Rename {src.name} -> {dest_name}")
            return True

        # [HARDENED] Verify source exists before proceeding
        if not src.exists():
            print(f"  [ERROR] Source file {src.name} does not exist")
            return False

        # Case 1: Destination Conflict Detection
        is_collision = False
        if dest.exists():
            try:
                # [HARDENED] Proper Windows case-insensitive path comparison
                src_resolved = src.resolve()
                dest_resolved = dest.resolve()

                # Check if they're the same file (case-insensitive on Windows)
                if src_resolved == dest_resolved:
                    print(
                        "  [INFO] Source and destination are the same file (case-insensitive match)"
                    )
                    return False  # No action needed
                else:
                    is_collision = True
            except OSError as e:
                print(f"  [WARNING] Could not resolve paths for comparison: {e}")
                is_collision = True

        if is_collision:
            print(f"  [COLLISION] Target {dest_name} already exists. Analyzing content...")
            try:
                # [HARDENED] Verify both files exist before reading
                if not src.exists():
                    print("  [ERROR] Source file disappeared during collision analysis")
                    return False
                if not dest.exists():
                    print("  [ERROR] Destination file disappeared during collision analysis")
                    return False

                # Critical Analysis: Binary read ensures exact match without encoding issues.
                src_content = src.read_bytes()
                dest_content = dest.read_bytes()

                if src_content == dest_content:
                    print(
                        "  [ANALYSIS] Files are IDENTICAL. Remediation: Deleting redundant violator."
                    )
                    print(f"  [ACTION] DELETE {src.name}")

                    # [HARDENED] Atomic delete with verification
                    src.unlink()

                    # [HARDENED] Verify deletion succeeded
                    if src.exists():
                        print(f"  [ERROR] Failed to delete {src.name} - file still exists")
                        return False

                    print(f"  [SUCCESS] {src.name} deleted successfully")
                    return True  # Violation resolved by deletion

                else:
                    # Divergent content: Rename to .CONFLICT to preserve data
                    print(
                        "  [ANALYSIS] Files are DIFFERENT. Remediation: Preserving data via conflict rename."
                    )
                    timestamp = int(time.time())
                    conflict_name = f"{dest_name}.CONFLICT_{timestamp}"
                    conflict_path = src.parent / conflict_name

                    # [HARDENED] Check if conflict file already exists
                    if conflict_path.exists():
                        # Add microseconds to ensure uniqueness
                        timestamp = int(time.time() * 1000000)
                        conflict_name = f"{dest_name}.CONFLICT_{timestamp}"
                        conflict_path = src.parent / conflict_name

                    print(f"  [ACTION] RENAME {src.name} -> {conflict_name}")

                    # [HARDENED] Atomic rename with verification
                    src.rename(conflict_path)

                    # [HARDENED] Verify rename succeeded and source no longer exists
                    if src.exists():
                        print(f"  [ERROR] Failed to rename {src.name} - source still exists")
                        return False
                    if not conflict_path.exists():
                        print(f"  [ERROR] Failed to rename {src.name} - conflict file not found")
                        return False

                    print(f"  [SUCCESS] {src.name} renamed to {conflict_name}")
                    return True  # Violation resolved by moving aside

            except Exception as e:
                print(f"  [ERROR] Failed to resolve collision: {e}")
                # [HARDENED] Don't attempt rollback on collision - preserve existing files
                return False

        # Case 2: Standard Rename (or Case-Only Rename)
        temp_path = None
        try:
            # [HARDENED] Atomic temp shuffle for Windows case-sensitivity support
            temp = src.parent / f"__temp_{int(time.time() * 1000000)}_{src.name}"
            temp_path = temp

            # Step 1: Move source to temp
            src.rename(temp)

            # [HARDENED] Verify temp move succeeded
            if not temp.exists():
                print(f"  [ERROR] Failed to move {src.name} to temp location")
                return False
            if src.exists():
                print(f"  [ERROR] Source {src.name} still exists after temp move")
                return False

            # Step 2: Move temp to destination
            temp.rename(dest)

            # [HARDENED] Verify final rename succeeded
            if not dest.exists():
                print(f"  [ERROR] Failed to move temp to {dest_name}")
                # Attempt rollback: restore from temp
                if temp.exists():
                    temp.rename(src)
                    print(f"  [ROLLBACK] Restored {src.name} from temp")
                return False
            if temp.exists():
                print("  [WARNING] Temp file still exists after rename - cleaning up")
                try:
                    temp.unlink()
                except:
                    pass  # Best effort cleanup

            print(f"  [SUCCESS] {src.name} -> {dest_name}")
            return True

        except Exception as e:
            print(f"  [ERROR] Rename failed: {e}")

            # [HARDENED] Attempt rollback if temp file exists
            if temp_path and temp_path.exists():
                try:
                    temp_path.rename(src)
                    print(f"  [ROLLBACK] Restored {src.name} from temp")
                except Exception as rollback_error:
                    print(f"  [CRITICAL] Rollback failed: {rollback_error}")
                    print(f"  [CRITICAL] Manual intervention required - file may be at {temp_path}")

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
            # [HARDENED] Heuristic: The primary class often matches the filename.
            primary = classes[0]
            stem_clean = path.stem.replace("_", "").lower()
            for cls_name in classes:
                if cls_name.lower() == stem_clean:
                    primary = cls_name
                    break
            target_name = primary
            
            # [HARDENED] Enforce Suffix
            if file_type == "AGENT" and not target_name.endswith("Agent"):
                target_name += "Agent"
                
            return f"{target_name}.py"
        except:
            return None

    def heal(self, violation: dict) -> dict:
        """Heal Pascal naming violations using standard_heal decorator pattern.
        
        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (naming)
                - path: Path to the violating file
                - severity: Severity level of the violation
                
        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        """
        from agentic_core.base_agents.decorators import standard_heal
        
        @standard_heal
        def _heal_pascal_violation(self, violation: dict) -> dict:
            """Internal heal method with standard_heal decorator."""
            violation_type = violation.get("type", "naming")
            path = violation.get("path", "")
            
            Logger.info(f"[PASCAL] Healing {violation_type} violation at {path}")
            
            if violation_type == "naming":
                # Fix Pascal naming convention violations
                file_path = Path(path)
                
                # Check if it's an agent that needs renaming
                if file_path.suffix == ".py":
                    stem = file_path.stem
                    
                    # If it doesn't follow Agent.py pattern
                    if not stem.endswith("Agent"):
                        # Determine correct naming based on content
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            # Check if it's actually an agent class
                            if "class " in content and "Agent" in content:
                                # Extract the actual class name
                                import re
                                class_match = re.search(r'class (\w+Agent)', content)
                                if class_match:
                                    class_name = class_match.group(1)
                                    new_path = file_path.parent / f"{class_name}.py"
                                    
                                    if not new_path.exists():
                                        file_path.rename(new_path)
                                        Logger.info(f"  Renamed {path} -> {new_path}")
                                        return {"violations_fixed": 1, "violations_found": 1, "errors": 0, "skipped": 0}
                                    else:
                                        Logger.warning(f"  Target {new_path} already exists")
                                        return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
                                else:
                                    # Add Agent suffix
                                    new_path = file_path.parent / f"{stem}Agent.py"
                                    if not new_path.exists():
                                        file_path.rename(new_path)
                                        Logger.info(f"  Renamed {path} -> {new_path}")
                                        return {"violations_fixed": 1, "violations_found": 1, "errors": 0, "skipped": 0}
                                    else:
                                        Logger.warning(f"  Target {new_path} already exists")
                                        return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
                            else:
                                Logger.info(f"  File {path} is not an agent, skipping")
                                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
                        except Exception as e:
                            Logger.error(f"  Error processing {path}: {e}")
                            return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}
                else:
                    Logger.info(f"  Non-Python file {path}, skipping")
                    return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
            else:
                Logger.warning(f"  Unknown violation type: {violation_type}")
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}
        
        # Call the internal heal method
        return _heal_pascal_violation(self, violation)

    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
        target_territory: str | None = None,
        auto_approve: bool = True,
        **kwargs,
    ) -> dict[str, int]:
        """
        Standard healing interface for execute_ssot.py integration.

        This method provides the canonical healing interface that integrates
        with the HealerMixin chain and execute_ssot.py orchestration.

        Args:
            dry_run: If True, only propose changes without applying them
            execute: If True, apply changes (overrides dry_run)
            depth: Current recursion depth for cycle detection
            max_depth: Maximum recursion depth allowed
            _call_path: Set of agent IDs already in call path (cycle detection)
            target_territory: If specified, scope healing to this territory only
                              (e.g., "prompt_governance" -> agentic_core/prompt_governance)
            auto_approve: If True, skip interactive prompts (for CI/automated runs)
        """
        if _call_path is None:
            _call_path = set()

        # Prevent cycles
        agent_id = f"PascalSovereigntyAgent@{self.project_root}"
        if agent_id in _call_path:
            return {"violations_found": 0, "violations_fixed": 0, "errors": 0, "skipped": 0}
        _call_path.add(agent_id)

        # Configure healing mode
        self.dry_run = dry_run and not execute

        # Determine scan root based on target_territory
        # [HARDENED] Support both absolute paths and relative territory names
        if target_territory:
            if (self.project_root / "agentic_core" / target_territory).exists():
                scan_root = self.project_root / "agentic_core" / target_territory
            elif (self.project_root / target_territory).exists():
                scan_root = self.project_root / target_territory
            else:
                print(f"[WARNING] Territory path does not exist: {target_territory}")
                return {"violations_found": 0, "violations_fixed": 0, "errors": 0, "skipped": 1}
            print(f"[SOVEREIGNTY] Scoped to territory: {target_territory}")
        else:
            scan_root = self.project_root

        try:
            # Execute the sovereignty audit on the scoped root
            exit_code = self._orchestrate_audit(scan_root)

            # Calculate violations based on stats
            total_violations = sum(self.stats["violations"].values())
            violations_fixed = self.stats["renamed"] + self.stats["collisions_resolved"]

            return {
                "violations_found": total_violations,
                "violations_fixed": violations_fixed,
                "errors": 0 if exit_code == 0 else 1,
                "skipped": 0,
            }

        except Exception as e:
            print(f"[ERROR] PascalSovereigntyAgent healing failed: {e}")
            return {"violations_found": 0, "violations_fixed": 0, "errors": 1, "skipped": 0}
        finally:
            _call_path.discard(agent_id)


def main():
    """Standalone execution for testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Pascal Sovereignty Agent")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--validate", action="store_true", help="Check compliance only")
    args = parser.parse_args()

    from pathlib import Path

    is_dry_run = args.dry_run or args.validate

    agent = PascalSovereigntyAgent(
        project_root=Path("."), dry_run=is_dry_run, validate_only=args.validate
    )

    result = agent.run()
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
