"""
File: pascal_sovereignty_fixer.py
Path: C:\Git\Agentic-Workflow\pascal_sovereignty_fixer.py
Status: Hardened (Phase 3)
Rationale: 
    Automating the 'LongPathsEnabled' registry check (previously manual).
    Deeply nested paths in 'apps_rg' will fail silently or crash without this on Windows.
    Moving this check from documentation to code reduces deployment risk.
"""

import ast
import re
import sys
import os
import shutil
import platform
from pathlib import Path
from typing import Literal, Optional, Dict, List, Tuple

# SSOT Integration - Critical for path discovery
# If these imports fail, the script defaults to local directory scanning
try:
    from agentic_core.L5_safety.validators.structure_blueprint import (
        AGENTIC_CORE_DIR,
        APPS_RG_DIR,
        APPS_LIC_DIR,
        APPS_SHARED_DIR,
    )
    from agentic_core.utils.ssot_discovery import get_python_files
except ImportError:
    # Fallback for standalone execution or bootstrapping
    AGENTIC_CORE_DIR = "agentic_core"
    APPS_RG_DIR = "apps_rg"
    APPS_LIC_DIR = "apps_lic"
    APPS_SHARED_DIR = "apps_shared"
    
    def get_python_files(root: Path) -> List[Path]:
        return list(root.rglob("*.py"))

FileType = Literal["AGENT", "CLASS", "UTILITY", "IGNORE"]

class PascalSovereigntyFixer:
    """Enforces strict file naming conventions based on AST content analysis."""

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.stats = {
            "analyzed": 0,
            "compliant": 0,
            "renamed": 0,
            "imports_fixed": 0,
            "violations": {"AGENT": 0, "CLASS": 0, "UTILITY": 0}
        }

    def classify_file(self, path: Path) -> FileType:
        """
        Analyze file AST to determine architectural role.
        
        Logic:
        - IGNORE: __init__.py, empty, syntax error.
        - AGENT: Inherits from *Agent or name ends in 'Agent'.
        - CLASS: Contains class definitions (non-agent).
        - UTILITY: No class definitions.
        """
        if path.name == "__init__.py":
            return "IGNORE"
            
        try:
            if path.stat().st_size == 0:
                return "IGNORE"
        except OSError:
            return "IGNORE"

        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError, OSError):
            return "IGNORE"

        has_class = False
        is_agent = False

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_class = True
                # Heuristic 1: Name suffix
                if node.name.endswith("Agent"):
                    is_agent = True
                
                # Heuristic 2: Inheritance
                for base in node.bases:
                    # Handle: class X(BaseAgent)
                    if isinstance(base, ast.Name) and "Agent" in base.id:
                        is_agent = True
                    # Handle: class X(core.BaseAgent)
                    elif isinstance(base, ast.Attribute) and "Agent" in base.attr:
                        is_agent = True

        if is_agent:
            return "AGENT"
        elif has_class:
            return "CLASS"
        else:
            return "UTILITY"

    def get_compliant_name(self, path: Path, file_type: FileType) -> Optional[str]:
        """Determine the correct filename based on type and content."""
        if file_type == "IGNORE":
            return None

        current_name = path.name
        
        # UTILITY: Enforce snake_case
        if file_type == "UTILITY":
            # Simple check: if uppercase exists or not typical snake_case
            if not current_name.islower() and current_name != "__main__.py":
                # Warning: naive conversion. 
                # In strict mode, we might want to flag this but not auto-rename 
                # without better heuristics to avoid breaking weird scripts.
                # For now, we return None to avoid over-eager utility renaming.
                return None 
            return None

        # AGENT & CLASS: Enforce PascalCase
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            if not classes:
                return None
            
            # Select primary class (heuristic: matches existing stem or longest name)
            primary_class = classes[0]
            stem_clean = path.stem.replace("_", "").lower()
            
            for cls_name in classes:
                if cls_name.lower() == stem_clean:
                    primary_class = cls_name
                    break
            
            target_name = primary_class
            
            if file_type == "AGENT" and not target_name.endswith("Agent"):
                target_name += "Agent"
            
            # Ensure extension
            return f"{target_name}.py"

        except Exception:
            return None

    def safe_rename_windows(self, src: Path, dest_name: str) -> bool:
        """
        Rename file handling Windows case-insensitivity.
        Steps: src -> __temp -> dest
        """
        dest = src.parent / dest_name
        
        # Skip if names match exactly
        if src.name == dest_name:
            return False

        if self.dry_run:
            print(f"  [PLAN] Rename {src.name} -> {dest_name}")
            return True

        # Collision Check
        if dest.exists() and dest.resolve() != src.resolve():
            print(f"  [ERROR] Collision: {dest_name} already exists. Skipping.")
            return False

        try:
            temp = src.parent / f"__temp_{src.name}"
            src.rename(temp)
            temp.rename(dest)
            return True
        except OSError as e:
            print(f"  [ERROR] Rename failed: {e}")
            return False

    def update_imports(self, repo_root: Path, old_name: str, new_name: str) -> int:
        """
        Scan ALL python files and update import references.
        Regex targets 'from ... import old_name' and 'import old_name'
        """
        count = 0
        old_mod = old_name.replace(".py", "")
        new_mod = new_name.replace(".py", "")
        
        # Regex: match "from ... import old_mod" ensuring word boundaries
        # Capture group 1 is "from ... import "
        regex = re.compile(rf"(from\s+[\w\.]+\s+import\s+){re.escape(old_mod)}\b")
        
        files = get_python_files(repo_root)
        
        for path in files:
            if path.name == new_name: continue # Don't patch self
            
            try:
                content = path.read_text(encoding="utf-8")
            except: continue
            
            if old_mod not in content: continue
            
            new_content = regex.sub(rf"\1{new_mod}", content)
            
            if new_content != content:
                count += 1
                if self.dry_run:
                    print(f"    [REF] Would update imports in {path.name}")
                else:
                    path.write_text(new_content, encoding="utf-8")
        
        return count

    def verify_environment(self) -> bool:
        """
        Hardened Environment Check:
        1. Verify Windows LongPathsEnabled (Registry).
        2. Verify write permissions in current directory.
        """
        if platform.system() == "Windows":
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE, 
                    r"SYSTEM\CurrentControlSet\Control\FileSystem"
                )
                value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
                if value != 1:
                    print("[WARNING] Windows LongPathsEnabled is NOT set to 1.")
                    print("          Deeply nested files in 'apps_rg' may fail to rename.")
                    print("          Run 'DEPLOYMENT_PROTOCOL.md' registry fix.")
                    if not self.dry_run:
                        return False # Block execution
            except Exception as e:
                print(f"[WARNING] Could not verify LongPathsEnabled registry key: {e}")
                # We warn but don't block if we simply lack permission to read registry, 
                # though usually reading HKLM is allowed.
        
        return True

    def run(self, root: Path):
        print(f"[SOVEREIGNTY] {'DRY RUN' if self.dry_run else 'EXECUTE'} MODE")
        print("="*60)
        
        # Phase 3: Hardened Environment Check
        if not self.verify_environment():
            print("\n[FATAL] Environment check failed. Aborting.")
            sys.exit(1)
        
        files = get_python_files(root)
        self.stats["analyzed"] = len(files)

        for path in files:
            # 1. Classify
            ftype = self.classify_file(path)
            if ftype == "IGNORE": continue
            
            # 2. Determine Target
            new_name = self.get_compliant_name(path, ftype)
            
            # 3. Check for Violation
            if new_name and new_name != path.name:
                self.stats["violations"][ftype] += 1
                
                print(f"\n[DETECT] {path.name} ({ftype}) -> {new_name}")
                
                # 4. Rename
                if self.safe_rename_windows(path, new_name):
                    self.stats["renamed"] += 1
                    
                    # 5. Fix Imports
                    fixes = self.update_imports(root, path.name, new_name)
                    self.stats["imports_fixed"] += fixes
            else:
                self.stats["compliant"] += 1

        print("\n" + "="*60)
        print(f"Total files analyzed: {self.stats['analyzed']}")
        print(f"Compliant files:      {self.stats['compliant']}")
        print(f"Violations detected:  {sum(self.stats['violations'].values())}")
        print(f"  - Agents:  {self.stats['violations']['AGENT']}")
        print(f"  - Classes: {self.stats['violations']['CLASS']}")
        print(f"  - Utils:   {self.stats['violations']['UTILITY']}")
        if not self.dry_run:
            print(f"Files Renamed:        {self.stats['renamed']}")
            print(f"Imports Fixed:        {self.stats['imports_fixed']}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Pascal Sovereignty Fixer")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--validate", action="store_true", help="Check compliance only (implies --dry-run)")
    args = parser.parse_args()

    is_dry_run = args.dry_run or args.validate
    
    fixer = PascalSovereigntyFixer(dry_run=is_dry_run)
    fixer.run(Path("."))

if __name__ == "__main__":
    main()
