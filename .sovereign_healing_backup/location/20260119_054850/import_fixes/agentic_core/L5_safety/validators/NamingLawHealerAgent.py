
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: orchestrator, state, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations
from dataclasses import dataclass
#!/usr/bin/env python3
"""
[DEPRECATED - 2026-01-02] Naming Law Healer Agent - File Identity Standardizer

THIS AGENT IS DEPRECATED AND SHOULD NOT BE USED.

Reason: Creates snake_case *_agent.py files, which conflicts with NamingAgent's 
PascalCase *Agent.py enforcement. This agent's logic is misaligned with canon 
naming standards.

Use instead:
- NamingAgent: Validates PascalCase *Agent.py files
- PascalSovereigntyEnforcerAgent: Fixes snake_case → PascalCase class names

This file will be removed in a future release.
"""

import warnings
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# Emit deprecation warning on import
warnings.warn(
    "NamingLawHealerAgent is deprecated (conflicts with PascalCase naming). "
    "Use NamingAgent for validation or PascalSovereigntyEnforcerAgent for fixes.",
    DeprecationWarning,
    stacklevel=2
)

from agentic_core.L5_safety.validators.structure_blueprint import (
    CANON_SIGNALS,
    FORBIDDEN_PATTERNS,
)
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.decorators import standard_heal
from agentic_core.utils.sovereign_index import SovereignIndex


@dataclass
class NamingLawHealerAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    L1 Cognition: High-Signal Naming Law Healer — Key 49 Sovereign Enforcement
    The "Naming Surgeon" that standardizes file identities by renaming
    forbidden patterns or low-signal files to comply with naming laws.
    """
    
    SYSTEM_PROMPT = """
You are the NamingLawHealerAgent — the final arbiter of signal purity (Key 49).
Your mandate is absolute: Every file and class name must conform exactly to the eternal canon.

=== CANONICAL NAMING LAWS (ZERO TOLERANCE) ===

1. **File Names**:
   - lowercase snake_case ONLY.
   - Mandatory role suffixes:
     - Agents: *_agent.py | Engines: *_engine.py | Managers: *_manager.py
     - Validators: *_validator.py | Guardrails: *_guardrail.py
     - Models/Enums: *_models.py / *_enums.py | Tools: *_tool.py
   - Forbidden: utils.py, helper.py, misc.py, base.py, temp.py. 
   - Naming must reflect primary responsibility with high semantic signal.

2. **Class Names**:
   - PascalCase ONLY.
   - Must explicitly match the file role (e.g., NamingHealerAgent).

=== HEALING PROTOCOL ===
1. Diagnose violations.
2. Propose exact new filename (preserve path).
3. Generate full import reconciliation plan for all impacted files.
4. Output JSON ONLY.

{
  "current_path": "<full_path>",
  "new_filename": "<new_basename>",
  "reason": "<justification>",
  "renamed": true,
  "import_fixes": [{"file": "<path>", "old_import": "...", "new_import": "..."}]
}

=== CONSTRAINTS ===
- No folder moves. No overwrites. No broken imports.
- If target exists, return "renamed": false with conflict reason.

Eliminate noise. Amplify signal.
Current date: December 24, 2025
"""
    
    def __init__(self, project_root: Path, ctx: Any) -> None:
        """Initialize the instance."""
        self.root = project_root
        self.ctx = ctx
        self.healed_count = 0
        self.healed_files = []
        self.reasoning_steps = []
        self.scratchpad = ""
        
    async def execute(self, file_path: str = None) -> Any:
        """
        Execute the naming law healing pass.
        Can operate in batch mode (all files) or per-file mode with cognitive reasoning.
        """
        # Per-file mode with cognitive reasoning
        if file_path:
            return await self._execute_per_file(file_path)
        
        # Batch mode (legacy)
        print(f"\nfrom agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n   [*] NamingLawHealerAgent: Scanning for naming violations...")
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
    
    async def _execute_per_file(self, file_path: str) -> Dict:
        """Per-file execution with sovereign mutation and physical transformation."""
        # [SOVEREIGN MUTATION]
        response = await self.ctx.engine.resilient_mutation(
            prompt=f"{self.SYSTEM_PROMPT}\n\nTarget: {file_path}",
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response)
        if result.get("renamed"):
            new_p = Path(file_path).parent / result["new_filename"]
            if not new_p.exists():
                # Physical Transformation
                Path(file_path).rename(new_p)
                
                # Import Reconciliation (The Safety Net)
                for fix in result.get("import_fixes", []):
                    importer = self.root / fix["file"]
                    if importer.exists():
                        content = importer.read_text()
                        importer.write_text(content.replace(fix["old_import"], fix["new_import"]))
                
                return {"status": "HEALED", "path": str(new_p)}
        return result
            
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
            # Heuristic: Add appropriate suffix based on Violation
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
        
    def _think(self, thought: str) -> None:
        """Sovereign thought recording with size-limit shielding"""
        # L5 safety check: ensure a single thought doesn't flood the memory
        if len(thought) > 1000:
            thought = thought[:997] + "..."
        self.reasoning_steps.append(thought)
        self.scratchpad += f"- {thought}\n"
    
    def _detect_low_signal(self, code: str, current_name: str) -> List[str]:
        """Detect low-signal patterns in file name."""
        violations = []
        stem = current_name.lower()
        
        # Check for forbidden patterns
        if any(re.match(p, current_name) for p in FORBIDDEN_PATTERNS):
            violations.append("forbidden_pattern")
        
        # Check for high-signal keywords
        if not any(sig in stem for sig in CANON_SIGNALS):
            violations.append("low_signal_name")
        
        return violations
    
    def _generate_suggestions(self, current_name: str, code: str) -> List[str]:
        """Generate high-signal name suggestions based on code content."""
        suggestions = []
        stem = current_name.lower()
        
        # Extract class names from code
        class_matches = re.findall(r'class\s+(\w+)', code)
        for cls in class_matches:
            suggestions.append(f"{cls.lower()}")
        
        # Add sovereign suffix if not present
        if not stem.endswith("_agent"):
            suggestions.append(f"{stem}_agent")
        
        # Add core suffix
        suggestions.append(f"{stem}_core")
        
        return list(set(suggestions))
    
    def _rank_suggestions(self, suggestions: List[str], code: str) -> str:
        """Rank suggestions by signal strength."""
        if not suggestions:
            return None
        
        # Score each suggestion
        scores = {}
        for sug in suggestions:
            score = 0
            # Prefer names with canon signals
            score += sum(1 for sig in CANON_SIGNALS if sig in sug.lower())
            # Prefer shorter names
            score -= len(sug) / 100
            scores[sug] = score
        
        # Return highest scoring
        return max(scores, key=scores.get) if scores else None
    
    def _apply_rename(self, code: str, old_name: str, new_name: str) -> str:
        """Apply rename to code (update class names if needed)."""
        # Simple implementation - just return code as-is
        # More sophisticated version would update class names
        return code
    
    def get_summary(self) -> Dict:
        """Return a summary of the healing pass."""
        return {
            "agent": "NamingLawHealerAgent",
            "healed_count": self.healed_count,
            "healed_files": self.healed_files,
            "canon_signals": list(CANON_SIGNALS),
            "forbidden_patterns": list(FORBIDDEN_PATTERNS)
        }

    @timeout(300)
    @standard_heal
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """Naming/utils agent - operational only."""
        if _call_path is None:
            # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
            super().heal_repository()

        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] Naming/utils - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
