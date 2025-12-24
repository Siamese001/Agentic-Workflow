#!/usr/bin/env python3
"""
Naming Law Healer Agent - File Identity Standardizer
Renames forbidden or low-signal files to comply with naming laws.
This agent prevents circular drift by ensuring all files have high-signal names.
"""

import re
from pathlib import Path
from typing import Dict, List
from agentic_core.config.P1_core.structure_blueprint import CANON_SIGNALS, FORBIDDEN_PATTERNS


class NamingLawHealerAgent:
    """
    The "Naming Surgeon" that standardizes file identities by renaming
    forbidden patterns or low-signal files to comply with naming laws.
    """
    
    def __init__(self, project_root: Path, ctx):
        self.root = project_root
        self.ctx = ctx
        self.healed_count = 0
        self.healed_files = []
        
    async def execute(self):
        """
        Execute the naming law healing pass.
        Scans for files with forbidden patterns or lacking high-signal keywords
        and renames them to comply with naming laws.
        """
        print(f"\n   [*] NamingLawHealerAgent: Scanning for naming violations...")
        self.healed_count = 0
        self.healed_files = []
        
        for py_file in self.root.rglob("*.py"):
            # Skip protected files and __init__ files
            if py_file.name == "__init__.py" or self._is_protected_file(py_file):
                continue
                
            # Check if file needs healing
            new_name = self._determine_new_name(py_file)
            if new_name and new_name != py_file.name:
                # Perform the rename
                new_path = py_file.parent / new_name
                
                # Check if target already exists
                if new_path.exists():
                    print(f"   [!] Skipping {py_file.name}: target {new_name} already exists")
                    continue
                    
                try:
                    print(f"   [HEALING] NamingLawHealer: Renaming {py_file.name} -> {new_name}")
                    py_file.rename(new_path)
                    self.healed_count += 1
                    self.healed_files.append({
                        "old": str(py_file.relative_to(self.root)),
                        "new": str(new_path.relative_to(self.root))
                    })
                    self.ctx.report("NamingLawHealer", 1, True, f"Renamed {py_file.name}")
                except Exception as e:
                    print(f"   [!] Failed to rename {py_file.name}: {e}")
        
        if self.healed_count > 0:
            print(f"   [✓] NamingLawHealerAgent: Standardized {self.healed_count} file identities.")
            print(f"      [WARNING] Manual import updates may be required for renamed files.")
        else:
            print(f"   [✓] NamingLawHealerAgent: All files comply with naming laws.")
            
    def _is_protected_file(self, file_path: Path) -> bool:
        """Check if file is protected from renaming."""
        # Root level protected files
        if file_path.parent == self.root:
            protected = {"canon_validator_agentic_v2.py", "pyproject.toml", "README.md"}
            return file_path.name in protected
            
        # Files in sovereign directories that shouldn't be renamed
        rel_path = file_path.relative_to(self.root)
        parts = rel_path.parts
        
        # Skip config files and test files
        if "config" in parts or "test" in parts[0].lower():
            return True
            
        return False
        
    def _determine_new_name(self, file_path: Path) -> str:
        """
        Determine if a file needs a new name based on naming laws.
        Returns the new name if needed, None if current name is compliant.
        """
        stem = file_path.stem.lower()
        current_name = file_path.name
        
        # Rule 1: Check for forbidden patterns
        is_forbidden = any(re.match(p, current_name) for p in FORBIDDEN_PATTERNS)
        
        # Rule 2: Check for high-signal keywords
        is_low_signal = not any(sig in stem for sig in CANON_SIGNALS)
        
        # File needs healing if it violates either rule
        if (is_forbidden or is_low_signal):
            # Heuristic: Add appropriate suffix based on violation
            if is_forbidden:
                # Forbidden patterns get sovereign prefix
                if stem.endswith("_agent"):
                    new_name = f"sovereign_{current_name}"
                else:
                    new_name = f"sovereign_{stem}_agent.py"
            else:
                # Low signal files get agent suffix
                if stem.endswith("_agent"):
                    new_name = f"{stem}_core.py"
                else:
                    new_name = f"{stem}_agent.py"
                    
            return new_name
            
        return None
        
    def get_summary(self) -> Dict:
        """Return a summary of the healing pass."""
        return {
            "agent": "NamingLawHealerAgent",
            "healed_count": self.healed_count,
            "healed_files": self.healed_files,
            "canon_signals": list(CANON_SIGNALS),
            "forbidden_patterns": list(FORBIDDEN_PATTERNS)
        }
