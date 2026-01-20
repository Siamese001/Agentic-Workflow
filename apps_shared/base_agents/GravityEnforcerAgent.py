from __future__ import annotations
#!/usr/bin/env python3
"""
DEPRECATED (2026-01-07): Use GravityHealerAgent in L2_execution/ToolRegistry/ instead.

This agent has been consolidated into the unified Gravity system:
- Detection: GravityValidatorAgent (L5_safety/validators/)
- Healing: GravityHealerAgent (L2_execution/ToolRegistry/)

Gravity Enforcer Agent - Neural Link Stabilizer
Seals neural leaks by commenting out forbidden imports from upstream to downstream.
This agent doesn't just flag violations; it actively stops the bleeding.
"""

import re
import warnings
from pathlib import Path
from typing import Dict, Set, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeout

from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY
from agentic_core.L5_safety.guardrails.cached_safety_shield import CachedSafetyShield
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin


class GravityEnforcerAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin, CachedSafetyShield):
    """
    The "Neural Link" stabilizer that enforces gravity rules by actively
    commenting out forbidden imports from upstream sovereign code to downstream domains.
    """
    
    def __init__(self, project_root: Path, ctx) -> None:
        warnings.warn(
            "GravityEnforcerAgent is deprecated. Use GravityHealerAgent from "
            "agentic_core.L2_execution.ToolRegistry.GravityHealerAgent instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(project_root, "gravity_gate")
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
        
    async def execute(self) -> None:
        """
        Execute the gravity enforcement pass.
        Scans agentic_core files and comments out any forbidden downstream imports.
        """
        print(f"\nfrom agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n   [*] GravityEnforcerAgent: Scanning for neural leaks...")
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
        # [CACHE-FIRST] Sovereign reflex
        cached = self.get_cached_verdict("gravity", str(file_path))
        if cached:
            print(f"   [CACHE HIT] Gravity Verdict for {file_path.name}")
            return cached.get('had_violations', False)
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            print(f"   [!] Could not read {file_path}: {e}")
            return False
            
        # Check for violations
        if not self.forbidden_pattern or not self.forbidden_pattern.search(content):
            return False
            
        # [HEALING] Comment out the Violation to restore Gravity
        # This preserves the code but prevents it from executing
        new_content = self.forbidden_pattern.sub(r"# GRAVITY VIOLATION: \g<0>", content)
        
        # Only write if content changed
        if new_content != content:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                # Cache the Verdict
                Verdict = {"had_violations": True, "healed": True}
                self.store_verdict("gravity", str(file_path), Verdict)
                return True
            except Exception as e:
                print(f"   [!] Could not write to {file_path}: {e}")
        
        # Cache no violations
        Verdict = {"had_violations": False, "healed": False}
        self.store_verdict("gravity", str(file_path), Verdict)
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

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L5 safety agent - operational only."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()
        
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
