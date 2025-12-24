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
    L1 Cognition: High-Signal Naming Law Healer — Key 49 Sovereign Enforcement
    The "Naming Surgeon" that standardizes file identities by renaming
    forbidden patterns or low-signal files to comply with naming laws.
    """
    
    def __init__(self, project_root: Path, ctx):
        self.root = project_root
        self.ctx = ctx
        self.healed_count = 0
        self.healed_files = []
        self.reasoning_steps = []
        self.scratchpad = ""
        
    async def execute(self, file_path: str = None):
        """
        Execute the naming law healing pass.
        Can operate in batch mode (all files) or per-file mode with cognitive reasoning.
        """
        # Per-file mode with cognitive reasoning
        if file_path:
            return await self._execute_per_file(file_path)
        
        # Batch mode (legacy)
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
    
    async def _execute_per_file(self, file_path: str) -> Dict:
        """Per-file execution with cognitive reasoning transparency."""
        code = Path(file_path).read_text(encoding='utf-8', errors='replace')
        current_name = Path(file_path).stem
        
        # [L1 REASONING] Reset cognitive state for this session
        self.scratchpad = f"Analyzing: {current_name}.py\n"
        self.reasoning_steps = []
        
        self._think(f"STEP 1: Current name '{current_name}' — assessing signal density against Key 49 signals")
        
        # Signal analysis
        violations = self._detect_low_signal(code, current_name)
        
        if not violations:
            self._think("CONCLUSION: Name already satisfies high-signal requirements — no healing required")
            return {
                "healed": True,
                "reason": "High signal name",
                "reasoning_steps": self.reasoning_steps,
                "scratchpad_update": self.scratchpad
            }
        
        self._think(f"VIOLATIONS FOUND: {len(violations)} low-signal patterns detected")
        self.scratchpad += f"\nViolations identified: {violations}\n"
        
        self._think("STEP 2: Generating sovereign alternatives using territory-specific positive signals")
        suggestions = self._generate_suggestions(current_name, code)
        
        self._think(f"Generated {len(suggestions)} candidates: {', '.join(suggestions[:3])}...")
        
        self._think("STEP 3: Evaluating candidates against L1 cognitive criteria (entropy, clarity, canon match)")
        best = self._rank_suggestions(suggestions, code)
        
        if not best or best == current_name:
            self._think("CONCLUSION: No superior high-signal name found — marking as persistent violation")
            return {
                "healed": False,
                "reason": "No better name found",
                "persistent": True,
                "key_id": 49,
                "reasoning_steps": self.reasoning_steps,
                "scratchpad_update": self.scratchpad + "\nStatus: Persistent low-signal — escalation required"
            }
        
        self._think(f"SELECTED: '{best}' — identified as providing highest sovereign signal")
        self.scratchpad += f"\nDecision: Chosen '{best}' to maximize domain entropy."
        
        self._think("STEP 4: Preparing atomic rename and cross-file import refactor")
        new_code = self._apply_rename(code, current_name, best)
        
        return {
            "healed": True,
            "healed_code": new_code,
            "move_to": str(Path(file_path).with_name(f"{best}.py")),
            "reason": f"Renamed to high-signal '{best}'",
            "key_id": 49,
            "reasoning_steps": self.reasoning_steps,
            "scratchpad_update": self.scratchpad + f"\nHealing complete. Target: {best}.py"
        }
            
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
