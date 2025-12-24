#!/usr/bin/env python3
"""
Gravity Enforcer Agent - Neural Link Stabilizer
Seals neural leaks by commenting out forbidden imports from upstream to downstream.
This agent doesn't just flag violations; it actively stops the bleeding.
"""

import re
from pathlib import Path
from typing import Dict, Set
from agentic_core.config.P1_core.structure_blueprint import SOVEREIGN_REGISTRY


class GravityEnforcerAgent:
    """
    The "Neural Link" stabilizer that enforces gravity rules by actively
    commenting out forbidden imports from upstream sovereign code to downstream domains.
    """
    
    def __init__(self, project_root: Path, ctx):
        self.root = project_root
        self.ctx = ctx
        # Derive Upstream vs Downstream from SSOT
        all_roots = set(SOVEREIGN_REGISTRY.keys())
        # Upstream sovereign: non-apps_* roots and not 'tests'
        self.upstream_roots = {r for r in all_roots if not r.startswith("apps_") and r != "tests"}
        # Downstream: everything else (domains + tests)
        self.downstream_roots = all_roots - self.upstream_roots
        
        # Build regex pattern to catch forbidden imports
        if self.downstream_roots:
            self.forbidden_pattern = re.compile(
                r"^(?:import|from)\s+(" + "|".join(map(re.escape, sorted(self.downstream_roots))) + r")(?:\.\w|\s|$)",
                re.MULTILINE
            )
        else:
            self.forbidden_pattern = None
            
        self.healed_count = 0
        self.healed_files = []
        
    async def execute(self):
        """
        Execute the gravity enforcement pass.
        Scans agentic_core files and comments out any forbidden downstream imports.
        """
        print(f"\n   [*] GravityEnforcerAgent: Scanning for neural leaks...")
        self.healed_count = 0
        self.healed_files = []
        
        # Only scan sovereign upstream code (agentic_core)
        agentic_core_path = self.root / "agentic_core"
        if not agentic_core_path.exists():
            print(f"   [!] GravityEnforcerAgent: agentic_core not found")
            return
            
        for py_file in agentic_core_path.rglob("*.py"):
            # Skip __init__ files and test files
            if py_file.name == "__init__.py" or "test" in py_file.name.lower():
                continue
                
            # Skip if already processed (has gravity violations)
            if self._has_gravity_violations(py_file):
                continue
                
            # Check and heal if needed
            if self._heal_file(py_file):
                self.healed_count += 1
                self.healed_files.append(py_file.relative_to(self.root))
                self.ctx.report("GravityEnforcer", 1, True, f"Sealed leak in {py_file.name}")
        
        if self.healed_count > 0:
            print(f"   [✓] GravityEnforcerAgent: Sealed {self.healed_count} neural leaks (Upstream -> Downstream).")
            for file_path in self.healed_files[:5]:  # Show first 5
                print(f"      - {file_path}")
            if len(self.healed_files) > 5:
                print(f"      ... and {len(self.healed_files) - 5} more files")
        else:
            print(f"   [✓] GravityEnforcerAgent: No neural leaks detected.")
            
    def _has_gravity_violations(self, file_path: Path) -> bool:
        """Check if file already has commented gravity violations."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                return "# GRAVITY VIOLATION:" in content
        except:
            return False
            
    def _heal_file(self, file_path: Path) -> bool:
        """
        Check a file for gravity violations and heal them by commenting out.
        Returns True if the file was healed, False if no violations found.
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            print(f"   [!] Could not read {file_path}: {e}")
            return False
            
        # Check for violations
        if not self.forbidden_pattern or not self.forbidden_pattern.search(content):
            return False
            
        # [HEALING] Comment out the violation to restore Gravity
        # This preserves the code but prevents it from executing
        new_content = self.forbidden_pattern.sub(r"# GRAVITY VIOLATION: \g<0>", content)
        
        # Only write if content changed
        if new_content != content:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return True
            except Exception as e:
                print(f"   [!] Could not write to {file_path}: {e}")
                
        return False
        
    def get_summary(self) -> Dict:
        """Return a summary of the enforcement pass."""
        return {
            "agent": "GravityEnforcerAgent",
            "healed_count": self.healed_count,
            "healed_files": [str(f) for f in self.healed_files],
            "upstream_roots": list(self.upstream_roots),
            "downstream_roots": list(self.downstream_roots)
        }
