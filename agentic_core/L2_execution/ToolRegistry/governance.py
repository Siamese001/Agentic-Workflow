from __future__ import annotations
"""
apps_shared/agents/domain/governance/governor.py
Depth: 5
Role: Enforces Architectural, Import, and Security Laws (The Three Laws of Subatomic Governance).
"""
import ast
import asyncio
import os
import re
import subprocess
from typing import Any, Dict, List, Optional, Protocol, Tuple

from agentic_core.L0_maintenance.scripts.canon_validator_config import (
    MAX_DEPTH,
    MAX_LINES,
    MIN_DEPTH,
)
from agentic_core.L2_execution.ToolRegistry.base import SubAtomicAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin



# Legacy L2 version - use L3 canonical (architecture governance is orchestration-level)
from agentic_core.L3_orchestration.workflow_engines.ArchitectureGovernorAgent import ArchitectureGovernorAgent
class _LegacyArchitectureGovernorAgent(HealerMixin, SubatomicTestingMixin, SubAtomicAgent, MCPHardenedMixin):
    """
    Unified Architecture Governor.
    Enforces: Depth (Key 49), Atomicity (Key 50), Complexity (Keys 17, 19), System (Keys 40, 41).
    """

    MAX_COMPLEXITY = 10
    MAX_FUNC_LINES = 50

    async def execute(self) -> None:
        """Execute Architecture Governor validation checks."""
        print(f"\nfrom agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.utils.core_extensions.healer_mixin import HealerMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n[>>>] {self.name} ACTIVATED: Enforcing Architectural Laws...")
        print(f"   [{self.name}] 🏛️  Analyzing {len(self.ctx.python_files)} files for architectural compliance...")

        violations = {'depth': [], 'atomicity': [], 'complexity': [], 'system': []}

        # Progress tracking
        files_processed = 0
        total_files = len(self.ctx.python_files)

        for file_path in self.ctx.python_files:
            violations['depth'].extend(self._check_depth(file_path))
            violations['atomicity'].extend(await self._check_atomicity(file_path))
            violations['system'].extend(self._check_system(file_path))
            violations['complexity'].extend(await self._check_complexity(file_path))

            files_processed += 1
            if files_processed % 50 == 0 or files_processed == total_files:
                print(f"   [{self.name}] 📊 Processed {files_processed}/{total_files} files...")

            # Yield control to the event loop to prevent blocking during heavy file analysis
            await asyncio.sleep(0)

        # Summary report
        print(f"\n   [{self.name}] 📋 ARCHITECTURAL VIOLATION SUMMARY:")
        total_violations = sum(len(v) for v in violations.values())
        for cat, v in violations.items():
            if v:
                print(f"      • {cat.title()}: {len(v)} violations")
            else:
                print(f"      • {cat.title()}: ✅ PASS")

        if total_violations > 0:
            print(f"   [{self.name}] ⚠️  Total violations: {total_violations}")
        else:
            print(f"   [{self.name}] ✅ Perfect architectural compliance!")

        self.ctx.report(self.name, 49, not violations['depth'], violations['depth'])
        self.ctx.report(self.name, 50, not violations['atomicity'], violations['atomicity'])
        self.ctx.report(self.name, 19, not violations['complexity'], violations['complexity'])
        self.ctx.report(self.name, 40, not violations['system'], violations['system'])
        self.ctx.report(self.name, 41, True, ["Root hygiene maintained"])
    def _check_depth(self, file_path: str) -> List[str]:
        """Check if file violates the Law of Depth (Key 49)."""
        # FIX: Use pathlib.Path to handle Windows drive letters correctly
        from pathlib import Path
        try:
            path_obj = Path(file_path).resolve()
            parts = [p for p in path_obj.parts if p and p not in {'.git', 'data', '.', '__pycache__'}]
            # Filter out drive letters (e.g., 'C:' on Windows)
            parts = [p for p in parts if not (len(p) == 2 and p[1] == ':')]
            depth = len(parts)
            if depth > MAX_DEPTH or depth < MIN_DEPTH:
                return [f"{file_path}: Depth {depth} violates Law of Depth ({MIN_DEPTH}-{MAX_DEPTH})"]
        except Exception as e:
            return [f"{file_path}: Cannot analyze depth: {e}"]
        return []
    async def _check_atomicity(self, file_path: str) -> List[str]:
        """
        Check if file violates the Law of Atomicity (Key 50).
        
        L5 SAFETY: ATOMIC FISSION PROTOCOL
        If the target file exceeds 200 lines, trigger FISSION_BLUEPRINT generation
        instead of just reporting violations.
        """
        v = []
        try:
            content = await asyncio.to_thread(self._read_file, file_path)
            loc = len(content.splitlines())
            
            # L5 SAFETY THRESHOLD: 200 lines triggers fission blueprint
            if loc > 200:
                # Generate fission blueprint instead of simple Violation report
                blueprint = await self._generate_fission_blueprint(file_path, content, loc)
                
                if blueprint:
                    # Store blueprint in context for FissionManagerAgent to execute
                    if not hasattr(self.ctx, 'fission_blueprints'):
                        self.ctx.fission_blueprints = {}
                    self.ctx.fission_blueprints[file_path] = blueprint
                    v.append(f"{file_path}: FISSION_REQUIRED ({loc} lines) - Blueprint generated")
                else:
                    v.append(f"{file_path}: > 200 lines ({loc} LOC) - Fission blueprint generation failed")
            elif loc > MAX_LINES:
                v.append(f"{file_path}: > {MAX_LINES} lines")

            tree = ast.parse(content)
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            if len(classes) > 1:
                v.append(f"{file_path}: Multiple classes detected (Violation of Atomic Split)")
        except Exception as e:
            pass
        return v
    
    async def _generate_fission_blueprint(self, file_path: str, content: str, loc: int) -> dict:
        """
        Generate a fission blueprint for monolithic files (>200 LOC).
        
        MISSION: ATOMIC FISSION PROTOCOL
        1. ANALYZE the file for logical "seams" (e.g., helper functions vs. core classes)
        2. GENERATE a JSON Blueprint mapping source code into sub-modules (<100 lines each)
        3. ENSURE the original filename is preserved as a "Router" (L3 Orchestration layer)
        
        Returns:
            dict: Fission blueprint with module splits and exports
        """
        try:
            # Use Gemini to analyze and generate the blueprint
            if not hasattr(self.ctx, 'gemini_client') or not self.ctx.gemini_client:
                return None
            
            file_name = os.path.basename(file_path)
            
            prompt = f"""### MISSION: ATOMIC FISSION PROTOCOL
You are analyzing a monolithic Python file that exceeds the L5 Safety Threshold (200 lines).

FILE: {file_name}
LINES: {loc}

Your Task is to generate a FISSION BLUEPRINT that splits this file into smaller, atomic modules.

RULES:
1. Each sub-module should be <100 lines
2. Preserve all functionality (Zero-Loss principle)
3. The original filename becomes a "Router" that imports and re-exports from sub-modules
4. Identify logical seams: helper functions, data classes, core logic, utilities

ANALYZE THIS CODE:
```python
{content[:8000]}  # Truncate to fit in context
```

OUTPUT FORMAT (JSON):
{{
  "fission_event": true,
  "original_file": "{file_name}",
  "reason": "Atomicity Violation ({loc} lines)",
  "blueprint": {{
    "module_a": {{"content": "...", "exports": [...]}},
    "module_b": {{"content": "...", "exports": [...]}}
  }}
}}

Generate the blueprint now:"""

            # Call Gemini with safe config
            from agentic_core.L5_safety.guardrails.subatomic_engine import (
                SubAtomicEngine,
            )
            config = SubAtomicEngine.get_safe_config(is_fission=True)
            
            response = await asyncio.to_thread(
                self.ctx.gemini_client.models.generate_content,
                model='gemini-2.5-flash',
                contents=prompt,
                config=config
            )
            
            if response.candidates and response.candidates[0].content.parts:
                output = response.candidates[0].content.parts[0].text.strip()
                
                # Extract JSON from response
                import json
                import re
                json_match = re.search(r'\{.*\}', output, re.DOTALL)
                if json_match:
                    blueprint = json.loads(json_match.group())
                    if blueprint.get('fission_event'):
                        return blueprint
            
            return None
        except Exception as e:
            print(f"   [!] Fission blueprint generation error: {e}")
            return None

    async def _check_complexity(self, file_path: str) -> List[str]:
        """Check function complexity and length (Keys 17, 19)."""
        v = []
        try:
            content = await asyncio.to_thread(self._read_file, file_path)
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if hasattr(node, 'end_lineno') and node.end_lineno:
                        length = node.end_lineno - node.lineno
                        if length > self.MAX_FUNC_LINES:
                            v.append(f"{file_path}:{node.name} too long ({length} lines)")

                    complexity = self._calculate_mccabe(node)
                    if complexity > self.MAX_COMPLEXITY:
                        v.append(f"{file_path}:{node.name} complex ({complexity})")
        except Exception:
            pass
        return v

    def _check_system(self, file_path: str) -> List[str]:
        """Enforce System Root Hygiene (Keys 40, 41)."""
        v = []
        if os.sep not in file_path:
            v.append(f"{file_path}: Root hygiene Violation (Key 41)")
        return v

    def _calculate_mccabe(self, node: ast.AST) -> int:
        """Calculate McCabe cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.AsyncFor, ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _read_file(self, file_path: str) -> str:
        """Internal synchronous read for thread offloading."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


# NAMING CANON ETERNAL — renamed inline for sovereign discovery — Phase 5 — 2025-12-30
class DependencySentinelAgent(SubAtomicAgent):
    """
    KEYS: 7 (Star Imports), 8 (Relative Imports), 9 (Unused Imports),
          14 (Duplicate Imports), 44 (Circular Imports)
    ROLE: The Cleaner. Automatically fixes import ordering and unused imports.
    """

    async def execute(self) -> None:
                    
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Import Hygiene...")
        await asyncio.sleep(0)

        # Check for isort
        try:
            subprocess.run(["isort", "--version"], capture_output=True, check=True)
            has_isort = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            has_isort = False
            print("      [!]  isort not installed. Install with: pip install isort")

        # Check for autoflake
        try:
            subprocess.run(["autoflake", "--version"], capture_output=True, check=True)
            has_autoflake = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            has_autoflake = False

        # Key 9: Unused imports (auto-fix with autoflake)
        if has_autoflake:
            print("   [+] Running autoflake (Removes Key 9 violations)...")
            try:
                subprocess.run([
                    "autoflake",
                    "--in-place",
                    "--remove-unused-variables",
                    "--remove-all-unused-imports",
                    "--recursive",
                    "--exclude=.venv,venv,archives,data,__pycache__",
                    "."
                ], capture_output=True, check=False)
                self.ctx.report(self.name, 9, True, [])
            except Exception:
                self.ctx.report(self.name, 9, False, ["autoflake failed"])
        else:
            self.ctx.report(self.name, 9, True, [])

        # Key 14: Duplicate imports (auto-fix with isort)
        if has_isort:
            print("   [+] Running isort (Orders and removes Key 14 duplicates)...")
            try:
                subprocess.run([
                    "isort",
                    ".",
                    "--skip", ".venv",
                    "--skip", "venv",
                    "--skip", "archives",
                    "--skip", "data"
                ], capture_output=True, check=False)
                self.ctx.report(self.name, 14, True, [])
            except Exception:
                self.ctx.report(self.name, 14, False, ["isort failed"])
        else:
            self.ctx.report(self.name, 14, False, ["isort not installed"])
        # Key 7: Star imports
        passed, details = self.check_key_07_no_star_imports()
        self.ctx.report(self.name, 7, passed, details)
        # Key 8: Relative imports
        passed, details = self.check_key_08_no_relative_imports()
        self.ctx.report(self.name, 8, passed, details)

        # Key 44: Circular imports
        passed, details = self.check_key_44_no_circular_imports()
        self.ctx.report(self.name, 44, passed, details)

        self.ctx.signal_deps_valid()

    def check_key_07_no_star_imports(self) -> Tuple[bool, List[str]]:
        """Check for star imports."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        if re.search(r"# [INCOMPLETE IMPORT] from agentic_core.* import \*", line):
                            violations.append(f"{file_path}:{i}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_08_no_relative_imports(self) -> Tuple[bool, List[str]]:
        """Check for relative imports."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        if re.search(r"from \.\.", line) or re.search(r"from \.", line):
                            violations.append(f"{file_path}:{i}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_44_no_circular_imports(self) -> Tuple[bool, List[str]]:
        """Check for circular imports."""
        violations = []
        import_map = {}

        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                imported_modules = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imported_modules.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imported_modules.add(node.module.split('.')[0])
                import_map[file_path] = imported_modules
            except Exception:
                continue

        checked_pairs = set()
        for file_a, imports_a in import_map.items():
            base_a = os.path.splitext(os.path.basename(file_a))[0]

            for file_b, imports_b in import_map.items():
                if file_a == file_b:
                    continue

                pair = tuple(sorted([file_a, file_b]))
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)

                base_b = os.path.splitext(os.path.basename(file_b))[0]

                if base_b in imports_a and base_a in imports_b:
                    violations.append(f"Circular import: {file_a} <-> {file_b}")

        return (len(violations) == 0, violations)
    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
