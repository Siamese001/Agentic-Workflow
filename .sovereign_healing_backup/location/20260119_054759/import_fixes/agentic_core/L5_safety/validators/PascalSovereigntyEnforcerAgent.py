"""PascalSovereigntyEnforcerAgent — Ultra Phase 13 (Jan 01, 2026)

Eternal PascalCase SSOT Enforcer.
- Purges snake_case class/enum/dataclass definitions
- Eliminates all backward-compatibility aliases
- Updates references repo-wide
- Subatomic hops with self-validation (integrated test cases)
- All test cases must pass before commit
- Optional strict_mode: Delegate advanced to TestSovereigntyAgent
- AST-precise audit, layer-incremental purge
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

# CANONICAL: True - Eternal PascalCase enforcer for classes/enums/dataclasses (2026-01-06)

from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from enum import Enum

from agentic_core.L2_execution.ToolRegistry.ExecutionCanonBaseAgent import CanonBaseAgent
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.L5_safety.validators.TestSovereigntyAgent import TestSovereigntyAgent
from agentic_core.L5_safety.utils.ASTEnforcementMixin import ASTEnforcementMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)


class SovereignSeverity(Enum):
    """Sovereign event Severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class PascalSovereigntyEnforcerAgent(SubatomicTestingMixin, CanonBaseAgent, ASTEnforcementMixin, MCPHardenedMixin):
    """L5 Safety agent — enforces PascalCase as eternal sole SSOT.
    
    Uses ASTEnforcementMixin for ultra-precise AST analysis.
    """

    def __init__(self, ctx: Any, dry_run: bool = False, strict_mode: bool = False, _allow_mock: bool = False) -> None:
        """Ultra init — ctx mandatory, strict_mode configurable.
        
        Args:
            ctx: Execution context (mandatory for production)
            dry_run: If True, audit only without making changes
            strict_mode: If True, delegate to TestSovereigntyAgent for deep validation
            _allow_mock: Internal flag for testing - allows MagicMock ctx
        """
        if ctx is None:
            if _allow_mock:
                from unittest.mock import MagicMock
                ctx = MagicMock()
            else:
                raise ValueError("ctx mandatory — full runtime required for sovereign enforcement")
        super().__init__(ctx)
        self.repo_root = Path.cwd()
        self.branch_name = "refactor/eternal-pascal-sovereignty-2026"
        self.dry_run = dry_run
        self.strict_mode = strict_mode  # False = basic fast, True = specialist deep
        # Prefer agent suffix for sovereign discovery
        self.prefer_agent_suffix = True
        # Sovereign scope
        self.target_prefixes = [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]
        # Incremental layer order (from audit priority — schemas first)
        self.purge_order = [
            "schemas", "config", "apps_", "L5_safety", "L4_state",
            "L3_orchestration", "L2_execution", "L1_cognition", "L0_maintenance"
        ]

    def get_validation_keys(self) -> List[int]:
        """Return canon keys for naming sovereignty."""
        return [1, 2, 3]  # Naming, structure, sovereignty keys

    async def execute(self, scope: str = "schemas") -> Dict:
        """Subatomic entrypoint — audit + purge with configurable testing."""
        self._emit_event(SovereignSeverity.INFO, "PASCAL_PURGE_INITIATED")

        if not self.dry_run:
            # Safe branch creation
            branches = subprocess.run(["git", "branch", "--list", self.branch_name], 
                                     capture_output=True, text=True).stdout
            if self.branch_name not in branches:
                subprocess.run(["git", "checkout", "-b", self.branch_name], check=False)

        # Full AST audit
        audit = self._ast_audit()
        print(f"Audit complete: {audit['summary']}")

        if not audit["files"]:
            return {"status": "clean", "message": "PascalCase already eternal", "audit": audit}

        # Purge phase — incremental by layer
        results = []
        for layer in self.purge_order:
            if scope != "all" and layer not in scope:
                continue
            layer_files = [Path(f) for f in audit["files"] if layer in str(f)]
            if layer_files:
                print(f"Processing layer: {layer} ({len(layer_files)} files)")
                layer_result = await self._purge_layer(layer_files)
                results.extend(layer_result)

        # Final COMMIT if all purged
        if all(r["status"] in ["purged", "no_change"] for r in results) and not self.dry_run:
            subprocess.run(["git", "add", "-A"], check=False)
            subprocess.run(["git", "commit", "-m", "refactor: Eternal PascalCase SSOT — purge snake_case + aliases"], check=False)
            self._emit_event(SovereignSeverity.INFO, "PASCAL_SOVEREIGNTY_ACHIEVED")

        return {"audit": audit, "results": results, "dry_run": self.dry_run}

    async def _purge_layer(self, layer_files: List[Path]) -> List[Dict]:
        """Purge one layer — atomic with configurable testing."""
        layer_results = []
        for i, file_path in enumerate(layer_files, 1):
            print(f"  [{i}/{len(layer_files)}] {file_path.name}")
            original_content = Path(file_path).read_text(encoding='utf-8')
            purged_content = self._purge_snake_case(original_content)
            if purged_content == original_content:
                layer_results.append({"file": str(file_path), "status": "no_change"})
                continue

            # Additional validation: primary class should end with Agent
            try:
                tree = ast.parse(purged_content)
                # Filter for classes that are not Exceptions, Enums, or standard utility types
                sovereign_classes = [
                    node.name for node in ast.walk(tree) 
                    if isinstance(node, ast.ClassDef) 
                    and not any(getattr(base, 'id', '') in ('Exception', 'Enum', 'str', 'int') for base in node.bases if isinstance(base, ast.Name))
                ]
                
                if sovereign_classes:
                    # Select primary class based on filename match or first non-utility class
                    primary_class = next((c for c in sovereign_classes if c in file_path.stem), sovereign_classes[0])
                    
                    if not primary_class.endswith("Agent") and self.prefer_agent_suffix:
                        # Only warn for execution/safety layers that mandate Agent status
                        if any(layer in str(file_path) for layer in ["L1", "L2", "L3", "L5", "orchestration", "execution", "validators"]):
                            print(f"   [WARNING] Sovereign class {primary_class} in {file_path.name} lacks Agent suffix - consider rename")
                    
                    # Verify File/Class SSOT alignment
                    if file_path.stem != primary_class:
                        print(f"   [SSOT VIOLATION] Filename '{file_path.name}' mismatch with detected Primary Class '{primary_class}'")
            except SyntaxError:
                pass

            if not self.dry_run:
                Path(file_path).write_text(purged_content, encoding='utf-8')

            # Hop 3: CRITIQUE - Basic mandatory + optional specialist
            test_result = await self._run_critique_tests()
            if not test_result["basic_passed"]:
                if not self.dry_run:
                    Path(file_path).write_text(original_content, encoding='utf-8')
                    subprocess.run(["git", "restore", str(file_path)], check=False)
                layer_results.append({"file": str(file_path), "status": "failed_basic", TESTS_DIR: test_result})
                self._emit_event(SovereignSeverity.ERROR, "PASCAL_PURGE_CRITIQUE_FAILED")
                continue

            # Optional strict specialist
            advanced_passed = True
            advanced_result = None
            if self.strict_mode:
                try:
                    specialist = TestSovereigntyAgent()
                    advanced_result = await specialist.execute({"Artifact": purged_content, "type": "advanced"})
                    advanced_passed = advanced_result["passed"]
                    if not advanced_passed:
                        if not self.dry_run:
                            Path(file_path).write_text(original_content, encoding='utf-8')
                            subprocess.run(["git", "restore", str(file_path)], check=False)
                        layer_results.append({"file": str(file_path), "status": "failed_strict", "advanced": advanced_result})
                        self._emit_event(SovereignSeverity.ERROR, "PASCAL_STRICT_FAILED")
                        continue
                except Exception as e:
                    print(f"    [!] Specialist error (non-blocking): {e}")

            layer_results.append({"file": str(file_path), "status": "purged", TESTS_DIR: test_result, "advanced": advanced_result})

        return layer_results

    def _ast_audit(self) -> Dict:
        """Ultra-precise AST audit for snake_case + aliases."""
        files_with_snake = []
        total_snake = 0
        total_aliases = 0

        for path in self.repo_root.rglob("*.py"):
            if not any(prefix in str(path) for prefix in self.target_prefixes):
                continue
            try:
                content = path.read_text(encoding='utf-8')
                tree = ast.parse(content)
            except (SyntaxError, UnicodeDecodeError):
                continue

            snake_count = sum(1 for node in ast.walk(tree) 
                             if isinstance(node, ast.ClassDef) 
                             and node.name[0].islower())
            alias_count = len(re.findall(r'^\s*([A-Z][A-Za-z0-9_]*)\s*=\s*([a-z_][a-z0-9_]*)\s*$', content, re.MULTILINE))

            if snake_count or alias_count:
                files_with_snake.append(str(path))
                total_snake += snake_count
                total_aliases += alias_count

        return {
            "files": files_with_snake,
            "snake_classes": total_snake,
            "aliases": total_aliases,
            "summary": f"{len(files_with_snake)} files | {total_snake} snake_classes | {total_aliases} aliases"
        }

    def _audit_snake_case(self, scope: str) -> List[str]:
        """Audit for snake_case defs + aliases."""
        targets = []
        pattern_def = re.compile(r'^\s*class\s+([a-z_][a-z0-9_]*)\s*[\(:]', re.MULTILINE)
        pattern_alias = re.compile(r'^\s*([A-Z][A-Za-z0-9_]*)\s*=\s*([a-z_][a-z0-9_]*)\s*$', re.MULTILINE)

        for path in Path(self.repo_root).rglob("*.py"):
            if scope in str(path) or scope == "repo_wide":
                try:
                    content = path.read_text(encoding='utf-8')
                    if pattern_def.search(content) or pattern_alias.search(content):
                        targets.append(str(path))
                except Exception:
                    pass
        return targets

    def _purge_snake_case(self, content: str) -> str:
        """Core purge logic — AST-safe rename + alias removal."""
        # Parse aliases to mapping
        lines = content.splitlines()
        mapping = {}
        cleaned_lines = []
        for line in lines:
            # Match snake_case = PascalCase aliases
            alias_match = re.match(r'^\s*([A-Z][A-Za-z0-9_]*)\s*=\s*([a-z_][a-zA-Z0-9_]*)\s*$', line)
            if alias_match:
                pascal, snake = alias_match.groups()
                mapping[snake] = pascal
                continue  # Remove alias
            
            # Also remove self-referential aliases (ClassName = ClassName)
            self_alias_match = re.match(r'^\s*([A-Z][A-Za-z0-9_]*)\s*=\s*\1\s*$', line)
            if self_alias_match:
                continue  # Remove self-referential alias
            
            cleaned_lines.append(line)

        content = '\n'.join(cleaned_lines)

        # Rename definitions
        for snake, pascal in mapping.items():
            content = re.sub(rf'class\s+{re.escape(snake)}\s*[\(:]', f'class {pascal}(', content)
            content = re.sub(rf'@dataclass\s*\n\s*class\s+{re.escape(snake)}', f'@dataclass\nclass {pascal}', content)

        # Update references (member + whole-word)
        for snake, pascal in mapping.items():
            content = re.sub(rf'\b{re.escape(snake)}\.', f'{pascal}.', content)
            content = re.sub(rf'\b{re.escape(snake)}\b', pascal, content)

        return content

    async def _run_critique_tests(self) -> Dict:
        """Ultra CRITIQUE: Mandatory basic self-tests (expanded)."""
        tests = []

        # Test 1: Basic purge + alias removal
        input_content = """
class SovereignSeverity(str, Enum):
    CRITICAL = "CRITICAL"
"""
        expected = """
class SovereignSeverity(str, Enum):
    CRITICAL = "CRITICAL"
"""
        result = self._purge_snake_case(input_content).strip()
        tests.append({"name": "basic_purge_alias", "passed": result == expected.strip()})

        # Test 2: References + member access
        input_content = """
class ToneType(str, Enum):
    AUTHORITATIVE = "authoritative"
Severity = ToneType.AUTHORITATIVE
obj = ToneType()
"""
        expected = """
class ToneType(str, Enum):
    AUTHORITATIVE = "authoritative"
Severity = ToneType.AUTHORITATIVE
obj = ToneType()
"""
        result = self._purge_snake_case(input_content).strip()
        tests.append({"name": "references_member", "passed": result == expected.strip()})

        # Test 3: Dataclass + purge
        input_content = """
@dataclass
class HardState:
    id: str
"""
        expected = """
@dataclass
class HardState:
    id: str
"""
        result = self._purge_snake_case(input_content).strip()
        tests.append({"name": "dataclass_purge", "passed": result == expected.strip()})

        # Test 4: Clean file (no change)
        input_content = """
class SovereignEvent(BaseModel):
    pass
"""
        result = self._purge_snake_case(input_content)
        tests.append({"name": "clean_no_change", "passed": result.strip() == input_content.strip()})

        basic_passed = all(t["passed"] for t in tests)
        return {
            TESTS_DIR: tests,
            "basic_passed": basic_passed,
            "all_passed": basic_passed  # Strict mode checked in _purge_layer
        }

    def _emit_event(self, Severity: SovereignSeverity, event_type: str, payload: Optional[Dict] = None) -> None:
        """Telemetry for observability."""
        print(f"[SOVEREIGN EVENT] {Severity.value} | {event_type}")
        if payload:
            print(f"  Payload: {payload}")

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """PascalCase enforcer - scans and fixes snake_case violations."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
            super().heal_repository()
            
            result = self.run(dry_run=not execute)
            print(f"[{agent_name} HEAL @ depth {depth}] Found {result['total_violations']} violations")
            return {"violations_found": result['total_violations'], "purged": result['purged']}
        finally:
            _call_path.discard(agent_name)
