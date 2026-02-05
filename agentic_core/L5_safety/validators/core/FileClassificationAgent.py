"""
File: agentic_core/L5_safety/validators/FileClassificationAgent.py
Path: agentic_core/L5_safety/validators/FileClassificationAgent.py
Rationale:
    Comprehensive file classification and naming enforcement agent.
    Provides intelligent file categorization and naming enforcement
    across all architectural layers with AST-based analysis.

    Integration Features:
    - Inherits from SovereignBaseAgent for full infrastructure support
    - Implements standard agent interface for execute_ssot.py orchestration
    - Preserves all original file classification functionality
    - Adds heal_repository() method for standard healing chain integration

    Hardening Features (Architecture Hallucination Prevention):
    - SCRIPT category for ops_scripts (snake_case enforcement)
    - TYPES category for collections and private modules (immunity from renaming)
    - Priority-based classification to prevent misidentification
    - Enhanced file type detection with strict ordering
"""

import ast
import os
import platform
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

# Optional: Import SovereignBaseAgent if available for full integration
try:
    from agentic_core.base_agents.atomic_execution_mixin import AtomicExecutionMixin
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from agentic_core.L5_safety.validators.decorators import standard_heal

    HAS_SOVEREIGN_BASE = True
    HAS_ATOMIC_MIXIN = True
except ImportError:
    HAS_SOVEREIGN_BASE = False
    HAS_ATOMIC_MIXIN = False
    SovereignBaseAgent = object
    AtomicExecutionMixin = object

    def standard_heal(func):
        """Fallback decorator when full infrastructure unavailable."""
        return func


# Logger for healing operations
import logging

Logger = logging.getLogger(__name__)


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


FileType = Literal[
    "AGENT",
    "CLASS",
    "MIXIN",
    "UTILITY",
    "PROTOCOL",
    "ENGINE",
    "STUB",
    "TEST",
    "SCRIPT",  # For ops_scripts and maintenance tools
    "TYPES",  # For schemas/types/enums/collections
    "GATEWAY",
    # WINDSURF IMPLEMENTATION: New architectural categories
    "ORCHESTRATOR",
    "VALIDATOR",
    "FACTORY",
    "CONFIG",
    "ADAPTER",
    "IGNORE",
]


@dataclass
class FileClassificationAgent(AtomicExecutionMixin, SovereignBaseAgent):
    """
    Enforces file classification and naming conventions with architectural integrity.

    This agent provides comprehensive file system governance through intelligent
    categorization and naming enforcement across all architectural layers.
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
            "deep_refactors": 0,
            "collisions_resolved": 0,
            "violations": {
                "AGENT": 0,
                "CLASS": 0,
                "MIXIN": 0,
                "UTILITY": 0,
                "PROTOCOL": 0,
                "ENGINE": 0,
                "STUB": 0,
                "TEST": 0,
                "SCRIPT": 0,
                "TYPES": 0,
                "GATEWAY": 0,
                # WINDSURF IMPLEMENTATION: New architectural categories
                "ORCHESTRATOR": 0,
                "VALIDATOR": 0,
                "FACTORY": 0,
                "CONFIG": 0,
                "ADAPTER": 0,
            },
        }
        # CACHE: Track file paths in memory to avoid repetitive disk scanning (O(1) lookups)
        self.file_registry: list[Path] = []

    def run(self) -> dict[str, Any]:
        """Entry point for execute_ssot.py orchestration."""
        print(f"[CLASSIFICATION] Executing File Classification Audit at {self.project_root}")
        success = self._orchestrate_audit(self.project_root)
        return {
            "success": success == 0,
            "stats": self.stats,
            "summary": (
                f"Renamed: {self.stats['renamed']}, Refactors: {self.stats['deep_refactors']}"
            ),
        }

    def _orchestrate_audit(self, root: Path) -> int:
        """Core file classification and audit logic."""
        print(f"[CLASSIFICATION] {'DRY RUN' if self.dry_run else 'EXECUTE'} MODE")
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

                        # Only update registry if file exists and wasn't deleted
                        if dest.exists():
                            self.file_registry[idx] = dest

                            # 1. Update File Header Metadata (Docstrings)
                            self.update_file_header(dest, path.name, new_name)

                            # 2. Sync Companion Test File (if exists)
                            self.sync_companion_test(path, new_name)

                            # 3. [CRITICAL FIX] DEEP REFACTORING LOGIC
                            # If we rename a file, we MUST rename the class inside
                            # to avoid "Ghost Classes"
                            # Condition: Architecture Components (PascalCase -> PascalCase)
                            old_stem = path.stem
                            new_stem = Path(new_name).stem

                            if (
                                old_stem != new_stem
                                and old_stem[0].isupper()
                                and new_stem[0].isupper()
                            ):
                                print(f"  [DEEP REFACTOR] {old_stem} -> {new_stem}")
                                refactor_count = self.deep_refactor_name(old_stem, new_stem)
                                self.stats["deep_refactors"] += refactor_count
                                self.stats["imports_fixed"] += refactor_count

                                # 4. Refactor Non-Python Assets (Configs/Manifests)
                                self.refactor_non_python_assets(old_stem, new_stem)

                            else:
                                # Standard Import Update for non-architectural renames
                                self.stats["imports_fixed"] += self.update_imports(
                                    path.name, new_name
                                )
                        else:
                            # File was deleted due to duplicate content - remove from registry
                            self.file_registry[idx] = None
            else:
                self.stats["compliant"] += 1

        # 5. [NEW] Cleanup Redundant Conflicts
        # Removes .CONFLICT files ONLY if they are identical to the live file
        self.cleanup_redundant_conflicts(root)

        print("\n" + "=" * 60)
        print(f"Total files analyzed: {self.stats['analyzed']}")
        print(f"Compliant files:      {self.stats['compliant']}")
        total_violations = sum(self.stats["violations"].values())
        print(f"Violations detected:  {total_violations}")
        print(f"  - Agents:  {self.stats['violations']['AGENT']}")
        print(f"  - Classes: {self.stats['violations']['CLASS']}")
        print(f"  - Utils:   {self.stats['violations']['UTILITY']}")
        print(f"  - Mixins:  {self.stats['violations']['MIXIN']}")
        print(f"  - Protocols: {self.stats['violations']['PROTOCOL']}")
        print(f"  - Engines: {self.stats['violations']['ENGINE']}")
        print(f"  - Stubs:   {self.stats['violations']['STUB']}")
        print(f"  - Tests:   {self.stats['violations']['TEST']}")
        print(f"  - Scripts: {self.stats['violations']['SCRIPT']}")
        print(f"  - Types:   {self.stats['violations']['TYPES']}")
        print(f"  - Gateways: {self.stats['violations']['GATEWAY']}")
        # WINDSURF IMPLEMENTATION: New categories summary
        print(f"  - Orchestrators: {self.stats['violations']['ORCHESTRATOR']}")
        print(f"  - Validators: {self.stats['violations']['VALIDATOR']}")
        print(f"  - Factories: {self.stats['violations']['FACTORY']}")
        print(f"  - Configs: {self.stats['violations']['CONFIG']}")
        print(f"  - Adapters: {self.stats['violations']['ADAPTER']}")
        if not self.dry_run:
            print(f"Files Renamed:        {self.stats['renamed']}")
            print(f"Deep Refactors:       {self.stats['deep_refactors']}")
            print(f"Imports Fixed:        {self.stats['imports_fixed']}")
            print(f"Collisions Resolved:  {self.stats['collisions_resolved']}")

        # Critical Analysis: Returning exit 1 on violations ensures git hooks
        # block non-compliant commits.
        return 0 if (not self.validate_only or total_violations == 0) else 1

    def classify_file(self, path: Path) -> FileType:
        """
        Analyze file AST to determine architectural role with STRICT PRIORITY ORDERING.

        WINDSURF IMPLEMENTATION PRIORITY QUEUE (First Match Wins):
        1. STUB     - File contains NOT_AN_AGENT marker (preempts all)
        2. BASE_AGENT - Files in base_agents/ directory (foundational classes)
        2.5 SELF_DETECTION - FileClassificationAgent.py is always an AGENT
        2.7 BLUEPRINT_DETECTION - structure_blueprint.py is always CONFIG
        3. TEST     - Path contains tests/ OR name starts with test_
        4. SCRIPT   - Ops/Maintenance scripts
        5. TYPES    - Collection files & private modules
        6. ORCHESTRATOR - Detect if Orchestrator in class name or path
        7. ADAPTER  - Detect if Strategy or Adapter in class name or file path
        8. CONFIG   - Detect if file name or path contains config, blueprint, settings, or manifest
        9. VALIDATOR - Detect if path contains validators/ or file name ends in _validator
        10. PROTOCOL - Class inherits from typing.Protocol
        11. FACTORY  - Detect if class name ends in Factory
        12. AGENT    - Keep existing inheritance/path logic
        13. MIXIN   - Keep existing logic
        14. CLASS   - Fallback for any other class
        15. UTILITY - Fallback for files with no classes
        """
        # --- EXEMPTION: SSOT & CRITICAL FILES ---
        critical_ignores = {
            "conftest.py",
            "__init__.py",
            "__main__.py",
            "setup.py",
            "tool_registry.py",
        }
        if path.name in critical_ignores:
            return "IGNORE"

        try:
            if not path.exists() or path.stat().st_size == 0:
                return "IGNORE"
            content = path.read_text(encoding="utf-8")

            # [PRIORITY 1] STUB Detection: Explicit Marker Override
            # CRITICAL: Must check BEFORE AST parsing to prevent Stubs from being detected as Agents
            # Only check for NOT_AN_AGENT at the start of a line (ignoring whitespace)
            if any(line.strip().startswith("NOT_AN_AGENT") for line in content.splitlines()):
                return "STUB"

            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError, OSError):
            return "IGNORE"

        # [PRIORITY 2.5] BASE AGENT Detection: Special case for base_agents
        # Base agents are foundational classes, not runtime agents
        if "base_agents" in path.parts:
            return "CLASS"

        # [PRIORITY 2.5] SELF DETECTION: FileClassificationAgent is always an AGENT
        if path.name == "FileClassificationAgent.py":
            return "AGENT"

        # [PRIORITY 2.7] BLUEPRINT DETECTION: structure_blueprint.py is always CONFIG
        if path.name == "structure_blueprint.py":
            return "CONFIG"

        # [PRIORITY 3] TEST Detection: Enhanced AST-based detection
        # Detect test classes and test-related patterns
        test_indicators = self._detect_test_patterns(tree, path)
        if test_indicators["is_test"]:
            # Check if already compliant test file
            if path.name.startswith("test_") or path.name.endswith("_test.py"):
                # Still return TEST for compliant files to maintain consistency
                pass
            return "TEST"

        # [PRIORITY 4] SCRIPT Detection: Enhanced AST-based detection
        # Detect scripts by entry points and execution patterns
        # Exclude the FileClassificationAgent itself
        if path.name != "FileClassificationAgent.py":
            script_indicators = self._detect_script_patterns(tree, path)
            if script_indicators["is_script"]:
                return "SCRIPT"

        # [PRIORITY 5] TYPES Detection: Enhanced AST-based detection
        # Detect type collections by class patterns
        type_indicators = self._detect_type_patterns(tree, path)
        if type_indicators["is_types"]:
            return "TYPES"

        has_class = False
        is_agent = False
        is_protocol = False
        # is_gateway = False  # Not used in new priority queue
        is_mixin = False

        # [HARDENED] Structural Contexts - REMOVED low-signal folder checks
        # is_engine = "engines" in path.parts  # Not used in new priority queue

        # WINDSURF IMPLEMENTATION: New category detection flags
        is_orchestrator = False
        is_adapter = False
        is_config = False
        is_validator = False
        is_factory = False

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_class = True
                name = node.name

                # Protocol Check (bases)
                for base in node.bases:
                    if (isinstance(base, ast.Name) and base.id == "Protocol") or (
                        isinstance(base, ast.Attribute) and base.attr == "Protocol"
                    ):
                        is_protocol = True

                # Name-based checks
                if name.endswith("Mixin"):
                    is_mixin = True
                if name.endswith("Agent"):
                    is_agent = True

                # Enhanced AST-based detection with fuzzy matching
                # ORCHESTRATOR detection
                orchestrator_patterns = [
                    "Orchestrator",
                    "orchestrator",
                    "orchestrate",
                    "coordinate",
                    "workflow",
                ]
                if self._fuzzy_match_name_or_content(name, path, content, orchestrator_patterns):
                    is_orchestrator = True

                # ADAPTER detection
                adapter_patterns = ["Strategy", "Adapter", "strategy", "adapter", "adapt", "wrap"]
                if self._fuzzy_match_name_or_content(name, path, content, adapter_patterns):
                    is_adapter = True
                if name.endswith("Factory"):
                    is_factory = True

                # Inheritance Check for Agents (if not already found)
                if not is_agent:
                    for base in node.bases:
                        if (isinstance(base, ast.Name) and "Agent" in base.id) or (
                            isinstance(base, ast.Attribute) and "Agent" in base.attr
                        ):
                            is_agent = True

        # Enhanced CONFIG detection using AST patterns
        config_indicators = [
            "config",
            "blueprint",
            "settings",
            "manifest",
            "Config",
            "Settings",
            "Options",
        ]
        config_patterns = {"configuration", "settings", "options", "params", "parameters"}
        if self._detect_config_patterns(tree, path, content, config_indicators, config_patterns):
            is_config = True

        # Enhanced VALIDATOR detection using AST patterns
        validator_patterns = [
            "validator",
            "validate",
            "check",
            "verify",
            "Validator",
            "Check",
            "Verify",
        ]
        if self._detect_validator_patterns(tree, path, content, validator_patterns):
            is_validator = True

        # [WINDSURF IMPLEMENTATION] PRIORITY EXECUTION - Order matters!
        # 1. STUB: Already handled above (preempts all)
        # 2. BASE_AGENT: Already handled above
        # 2.5 SELF_DETECTION: Already handled above
        # 2.7 BLUEPRINT_DETECTION: Already handled above
        # 3. TEST: Already handled above
        # 4. SCRIPT: Already handled above
        # 5. TYPES: Already handled above
        # 6. ORCHESTRATOR: Detect if Orchestrator in class name or path
        if is_orchestrator:
            return "ORCHESTRATOR"
        # 7. ADAPTER: Detect if Strategy or Adapter in class name or file path
        elif is_adapter:
            return "ADAPTER"
        # 8. CONFIG: Detect if file name or path contains config, blueprint, settings, or manifest
        elif is_config:
            return "CONFIG"
        # 9. VALIDATOR: Detect if path contains validators/ or file name ends in _validator
        elif is_validator:
            return "VALIDATOR"
        # 10. PROTOCOL: Keep existing AST check
        elif is_protocol:
            return "PROTOCOL"
        # 11. FACTORY: Detect if class name ends in Factory
        elif is_factory:
            return "FACTORY"
        # 12. AGENT: Keep existing inheritance/path logic
        elif is_agent:
            return "AGENT"
        # 13. MIXIN: Keep existing logic
        elif is_mixin:
            return "MIXIN"
        # 14. CLASS: Fallback for any other class
        elif has_class:
            return "CLASS"
        # 15. UTILITY: Fallback for files with no classes
        else:
            return "UTILITY"

    # ========================================================================
    # ENHANCED AST-BASED DETECTION METHODS
    # ========================================================================

    def _detect_test_patterns(self, tree: ast.AST, path: Path) -> dict[str, bool]:
        """
        Enhanced test detection using AST analysis.

        Detects:
        - Classes inheriting from unittest.TestCase
        - pytest fixtures and test functions
        - Test methods (starting with test_)
        - Mock/patch usage
        """
        indicators = {"is_test": False}

        # Check for unittest imports
        has_unittest = False
        has_pytest = False
        test_methods = 0
        fixtures = 0

        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "unittest":
                        has_unittest = True
                    elif alias.name == "pytest":
                        has_pytest = True
            elif isinstance(node, ast.ImportFrom):
                if node.module and ("unittest" in node.module or "pytest" in node.module):
                    has_unittest = has_unittest or "unittest" in node.module
                    has_pytest = has_pytest or "pytest" in node.module

            # Check classes
            elif isinstance(node, ast.ClassDef):
                # Check unittest.TestCase inheritance
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "TestCase":
                        indicators["is_test"] = True
                    elif isinstance(base, ast.Attribute) and base.attr == "TestCase":
                        indicators["is_test"] = True

                # Count test methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                        if item.name.startswith("test_"):
                            test_methods += 1

            # Check functions
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                # Check for pytest fixtures
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == "fixture":
                        fixtures += 1
                    elif isinstance(decorator, ast.Attribute) and decorator.attr == "fixture":
                        fixtures += 1

                # Check test functions at module level
                if node.name.startswith("test_"):
                    indicators["is_test"] = True

        # Determine if test file based on patterns
        if has_unittest or has_pytest or test_methods > 0 or fixtures > 0:
            indicators["is_test"] = True

        return indicators

    def _detect_script_patterns(self, tree: ast.AST, path: Path) -> dict[str, bool]:
        """
        Enhanced script detection using AST analysis.

        Detects:
        - if __name__ == "__main__" patterns
        - argparse or click usage
        - Direct execution patterns
        - Script-like function names (main, run, execute, start)
        """
        indicators = {"is_script": False}

        has_main_guard = False
        has_argparse = False
        has_click = False
        script_functions = 0

        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ("argparse", "click", "sys", "os"):
                        if alias.name == "argparse":
                            has_argparse = True
                        elif alias.name == "click":
                            has_click = True

            # Check for if __name__ == "__main__"
            elif isinstance(node, ast.If):
                if (
                    isinstance(node.test, ast.Compare)
                    and len(node.test.ops) == 1
                    and isinstance(node.test.ops[0], ast.Eq)
                ):
                    left = node.test.left
                    comparators = node.test.comparators
                    if (
                        isinstance(left, ast.Name)
                        and left.id == "__name__"
                        and len(comparators) == 1
                        and isinstance(comparators[0], ast.Constant)
                        and comparators[0].value == "__main__"
                    ):
                        has_main_guard = True

            # Check functions
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                script_names = {"main", "run", "execute", "start", "cli", "script"}
                if node.name in script_names:
                    script_functions += 1

        # Determine if script based on patterns
        if has_main_guard or has_argparse or has_click or script_functions > 0:
            indicators["is_script"] = True

        return indicators

    def _detect_type_patterns(self, tree: ast.AST, path: Path) -> dict[str, bool]:
        """
        Enhanced type collection detection using AST analysis.

        Detects:
        - Multiple enum classes
        - TypeVar usage
        - Protocol definitions
        - Abstract base classes
        - Data model patterns
        """
        indicators = {"is_types": False}

        enum_count = 0
        typevar_count = 0
        protocol_count = 0
        dataclass_count = 0
        model_count = 0

        for node in ast.walk(tree):
            # Check classes
            if isinstance(node, ast.ClassDef):
                # Check enum inheritance
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        if base.id == "Enum":
                            enum_count += 1
                        elif base.id == "Protocol":
                            protocol_count += 1
                        elif base.id in ("ABC", "abstractmethod"):
                            indicators["is_types"] = True
                    elif isinstance(base, ast.Attribute):
                        if base.attr == "Enum":
                            enum_count += 1
                        elif base.attr == "Protocol":
                            protocol_count += 1

                # Check dataclass decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                        dataclass_count += 1
                    elif isinstance(decorator, ast.Call):
                        if (
                            isinstance(decorator.func, ast.Name)
                            and decorator.func.id == "dataclass"
                        ):
                            dataclass_count += 1

                # Check model naming patterns
                if any(suffix in node.name for suffix in ("Model", "Schema", "DTO", "Type")):
                    model_count += 1

            # Check TypeVar usage
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and "TypeVar" in str(node.value):
                        typevar_count += 1

        # Determine if type collection based on patterns
        if (
            enum_count > 1
            or typevar_count > 0
            or protocol_count > 0
            or dataclass_count > 1
            or model_count > 1
        ):
            indicators["is_types"] = True

        return indicators

    def _fuzzy_match_name_or_content(
        self, name: str, path: Path, content: str, patterns: list[str]
    ) -> bool:
        """
        Fuzzy matching for names and content patterns.

        Uses multiple strategies:
        - Exact name matching
        - Partial name matching
        - Content pattern matching (excluding comments)
        """
        # Check exact name match
        if any(pattern in name for pattern in patterns):
            return True

        # Parse AST to check patterns in code (not comments)
        try:
            tree = ast.parse(content)
            content_lower = content.lower()

            for node in ast.walk(tree):
                # Check in function/class names
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                    if any(pattern.lower() in node.name.lower() for pattern in patterns):
                        return True

                # Check in string literals (but not comments)
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if any(pattern.lower() in node.value.lower() for pattern in patterns):
                        # Only count if it's a meaningful string, not just a word
                        if len(node.value) > 10:  # Longer strings are more likely meaningful
                            return True

                # Check in attribute names
                elif isinstance(node, ast.Attribute):
                    if any(pattern.lower() in node.attr.lower() for pattern in patterns):
                        return True

            # Check docstrings separately
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                    if (
                        hasattr(node, "doc_string")
                        and node.doc_string
                        and any(pattern.lower() in node.doc_string.lower() for pattern in patterns)
                    ):
                        return True

        except SyntaxError:
            # Fallback to simple content check if AST parsing fails
            content_lower = content.lower()
            for pattern in patterns:
                if pattern.lower() in content_lower:
                    pattern_count = content_lower.count(pattern.lower())
                    if pattern_count > 5:  # High threshold for fallback
                        return True

        return False

    def _detect_config_patterns(
        self, tree: ast.AST, path: Path, content: str, indicators: list[str], patterns: set[str]
    ) -> bool:
        """
        Enhanced config detection using AST analysis.

        Detects:
        - Classes with config-like attributes
        - Constant definitions
        - Configuration loading patterns
        - Settings management
        """
        # Check filename patterns
        if any(indicator in path.name.lower() for indicator in indicators):
            return True

        config_attributes = 0
        constant_assignments = 0
        config_methods = 0

        for node in ast.walk(tree):
            # Check classes
            if isinstance(node, ast.ClassDef):
                # Check naming
                if any(node.name.endswith(suffix) for suffix in ("Config", "Settings", "Options")):
                    return True

                # Check for config-like attributes
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        attr_name = item.target.id.lower()
                        if attr_name in patterns:
                            config_attributes += 1

                    # Check for config methods
                    elif isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                        if item.name in ("load", "save", "validate", "configure", "get_setting"):
                            config_methods += 1

            # Check module-level constants
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id.isupper() and len(target.id) > 1:
                            constant_assignments += 1

        # Determine if config based on patterns
        if config_attributes > 2 or constant_assignments > 3 or config_methods > 0:
            return True

        return False

    def _detect_validator_patterns(
        self, tree: ast.AST, path: Path, content: str, patterns: list[str]
    ) -> bool:
        """
        Enhanced validator detection using AST analysis.

        Detects:
        - Validation methods
        - Check functions
        - Verification patterns
        - Schema validation
        """
        # Check filename patterns (but exclude self)
        if path.name != "FileClassificationAgent.py":
            if any(pattern in path.name for pattern in patterns):
                return True

        validation_methods = 0
        check_functions = 0
        assert_usage = 0

        for node in ast.walk(tree):
            # Check classes
            if isinstance(node, ast.ClassDef):
                if any(pattern in node.name for pattern in patterns):
                    return True

                # Check for validation methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                        method_name = item.name.lower()
                        if any(
                            word in method_name
                            for word in ("validate", "check", "verify", "ensure", "assert")
                        ):
                            validation_methods += 1

            # Check functions
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                func_name = node.name.lower()
                if any(word in func_name for word in ("validate", "check", "verify", "ensure")):
                    check_functions += 1

                # Check for assert statements
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Assert):
                        assert_usage += 1

        # Determine if validator based on patterns
        if validation_methods > 0 or check_functions > 0 or assert_usage > 2:
            return True

        return False

    # ========================================================================
    # PHASE 1: Enhanced Detection Methods
    # ========================================================================

    def _is_true_agent(self, node: ast.ClassDef, file_path: Path) -> bool:
        """
        Enhanced agent detection with multiple criteria.

        Checks:
        1. Naming convention (ends with Agent)
        2. Inheritance from base agents
        3. Decorator-based detection
        4. Method-based detection (execute, act, heal, run)
        """
        # Check 1: Naming convention
        if node.name.endswith("Agent"):
            return True

        # Check 2: Inheritance from base agents
        base_agents = {
            "SovereignBaseAgent",
            "L0MaintenanceBaseAgent",
            "L1CognitionBaseAgent",
            "L2ExecutionBaseAgent",
            "L3OrchestrationBaseAgent",
            "L4StateBaseAgent",
            "L5SafetyBaseAgent",
            "L6ObservabilityBaseAgent",
        }
        for base in node.bases:
            if isinstance(base, ast.Name):
                if base.id in base_agents or "Agent" in base.id:
                    return True
            elif isinstance(base, ast.Attribute):
                if base.attr in base_agents or "Agent" in base.attr:
                    return True

        # Check 3: Decorator-based detection
        agent_decorators = {"agent", "sovereign_agent", "register_agent"}
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id in agent_decorators:
                    return True
            elif isinstance(decorator, ast.Attribute):
                if decorator.attr in agent_decorators:
                    return True

        # Check 4: Method-based detection
        agent_methods = {"execute", "act", "heal", "run"}
        for item in node.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                if item.name in agent_methods:
                    return True

        # Check 5: REMOVED - Structural context (low-signal folder check)

        return False

    def _is_service_class(self, node: ast.ClassDef, file_path: Path) -> bool:
        """
        Detect service classes with dependency injection patterns.

        Checks:
        1. @service decorator
        2. Constructor with service_container/injector/container parameter
        3. Name ends with Service
        """
        # Check 1: @service decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "service":
                return True
            elif isinstance(decorator, ast.Attribute) and decorator.attr == "service":
                return True

        # Check 2: Constructor with DI parameters
        di_params = {"service_container", "injector", "container", "dependencies"}
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                for arg in item.args.args:
                    if arg.arg in di_params:
                        return True

        # Check 3: Name ends with Service
        if node.name.endswith("Service"):
            return True

        return False

    def _is_factory_class(self, node: ast.ClassDef) -> bool:
        """
        Detect factory classes for object creation.

        Checks:
        1. Name ends with Factory
        2. Has create_* or make_* methods
        3. Has @factory decorator
        """
        # Check 1: Naming convention
        if node.name.endswith("Factory"):
            return True

        # Check 2: Factory methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name.startswith("create_") or item.name.startswith("make_"):
                    return True

        # Check 3: @factory decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "factory":
                return True

        return False

    def _is_async_agent(self, node: ast.ClassDef, file_path: Path) -> bool:
        """
        Detect async-based agents.

        Checks:
        1. Has async execute/act/run methods
        2. Has async context manager methods
        """
        has_async_agent_methods = False

        for item in node.body:
            if isinstance(item, ast.AsyncFunctionDef):
                if item.name in ("execute", "act", "run", "heal"):
                    has_async_agent_methods = True
                elif item.name in ("__aenter__", "__aexit__"):
                    has_async_agent_methods = True

        return has_async_agent_methods

    def _is_adapter_class(self, node: ast.ClassDef) -> bool:
        """
        Detect adapter/wrapper classes.

        Checks:
        1. Name ends with Adapter, Wrapper, or Bridge
        2. Has adapt/wrap/bridge methods
        3. Wraps another object (has _wrapped or _adaptee attribute)
        """
        # Check 1: Naming convention
        adapter_suffixes = ("Adapter", "Wrapper", "Bridge", "Proxy")
        if any(node.name.endswith(suffix) for suffix in adapter_suffixes):
            return True

        # Check 2: Adapter methods
        adapter_methods = {"adapt", "wrap", "bridge", "unwrap"}
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name in adapter_methods:
                    return True

        # Check 3: Wrapped object pattern in __init__
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                for stmt in ast.walk(item):
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Attribute):
                                if target.attr in ("_wrapped", "_adaptee", "_delegate"):
                                    return True

        return False

    # ========================================================================
    # PHASE 2: Additional Category Detection Methods
    # ========================================================================

    def _is_config_class(self, node: ast.ClassDef, file_path: Path) -> bool:
        """
        Detect configuration classes.

        Checks:
        1. Path contains config/
        2. Name ends with Config, Settings, or Options
        3. Has @dataclass decorator with config-like attributes
        """
        # Check 1: REMOVED - Path-based config detection (replaced with AST patterns)

        # Check 2: Naming convention
        config_suffixes = ("Config", "Settings", "Options", "Configuration")
        if any(node.name.endswith(suffix) for suffix in config_suffixes):
            return True

        # Check 3: Dataclass with simple attributes (config-like)
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                return True
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name) and decorator.func.id == "dataclass":
                    return True

        return False

    def _is_model_class(self, node: ast.ClassDef) -> bool:
        """
        Detect data model classes.

        Checks:
        1. Inherits from pydantic BaseModel
        2. Has @dataclass decorator
        3. Name ends with Model, Schema, DTO
        """
        # Check 1: Pydantic BaseModel inheritance
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "BaseModel":
                return True
            elif isinstance(base, ast.Attribute) and base.attr == "BaseModel":
                return True

        # Check 2: Name ends with model-related suffix
        model_suffixes = ("Model", "Schema", "DTO", "Entity")
        if any(node.name.endswith(suffix) for suffix in model_suffixes):
            return True

        return False

    def _is_repository_class(self, node: ast.ClassDef) -> bool:
        """
        Detect repository pattern classes.

        Checks:
        1. Name ends with Repository
        2. Has CRUD methods (create, read, update, delete, save, find, get, list)
        3. Name ends with DAO (Data Access Object)
        """
        # Check 1: Naming convention
        if node.name.endswith(("Repository", "DAO", "Store")):
            return True

        # Check 2: CRUD methods
        crud_methods = {"create", "read", "update", "delete", "save", "find", "get", "list_all"}
        methods = set()
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.add(item.name)

        # If has at least 2 CRUD methods, likely a repository
        if len(crud_methods & methods) >= 2:
            return True

        return False

    # ========================================================================
    # DEEP REFACTORING & IMPORT MANAGEMENT
    # ========================================================================

    def cleanup_redundant_conflicts(self, root: Path):
        """
        Scans for .CONFLICT files and removes them ONLY if they are byte-for-byte
        identical to the live file they conflicted with.
        """
        if self.dry_run:
            return

        print("\n[CLEANUP] Scanning for redundant conflict files...")
        count = 0

        # Regex to parse 'OriginalName.py.CONFLICT_123456' -> 'OriginalName.py'
        conflict_pattern = re.compile(r"^(.*)\.CONFLICT_\d+$")

        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                match = conflict_pattern.match(filename)
                if match:
                    conflict_path = Path(dirpath) / filename
                    original_name = match.group(1)
                    live_path = Path(dirpath) / original_name

                    if live_path.exists():
                        try:
                            # [SAFETY CHECK] Only delete if byte-identical (True Duplicate)
                            if conflict_path.read_bytes() == live_path.read_bytes():
                                print(f"  [DELETE] Redundant backup: {filename}")
                                conflict_path.unlink()
                                count += 1
                        except Exception as e:  # guardian: allow-silent_swallower
                            print(f"  [ERROR] Cleanup failed for {filename}: {e}")

        if count > 0:
            print(f"[CLEANUP] Removed {count} redundant conflict files.")

    def update_file_header(self, path: Path, old_name: str, new_name: str):
        """Updates the File: and Path: metadata in docstrings to match reality."""
        if self.dry_run:
            return
        try:
            content = path.read_text(encoding="utf-8")
            # Replace 'File: .../OldName.py' with 'File: .../NewName.py'
            new_content = content.replace(old_name, new_name)
            if new_content != content:
                path.write_text(new_content, encoding="utf-8")
        except Exception:  # guardian: allow-silent_swallower
            pass

    def sync_companion_test(self, src_path: Path, new_name: str):
        """Renames the corresponding test file if it exists."""
        # Heuristic: tests/test_{stem}.py or tests/{stem}_test.py
        stem = src_path.stem

        # 1. Calculate Expected Test Name
        test_dir = self.project_root / "tests"
        if not test_dir.exists():
            return

        # Try common patterns
        candidates = [test_dir / f"test_{stem}.py", test_dir / f"{stem}_test.py"]

        for test_file in candidates:
            if test_file.exists():
                # Determine new test name based on found pattern
                if test_file.name.startswith("test_"):
                    # test_Old.py -> test_New.py
                    new_test_name = f"test_{Path(new_name).stem}.py"
                else:
                    # Old_test.py -> New_test.py
                    new_test_name = f"{Path(new_name).stem}_test.py"

                print(f"  [SYNC] Renaming companion test: {test_file.name} -> {new_test_name}")
                self.resolve_collision_and_rename(test_file, new_test_name)

    def refactor_non_python_assets(self, old_name: str, new_name: str):
        """Scans JSON/YAML/TOML/TXT files for string references (Config Drift)."""
        extensions = {".json", ".yaml", ".yml", ".toml", ".txt", ".md"}

        # Simple scan of root and common config dirs
        config_files = []
        for ext in extensions:
            config_files.extend(self.project_root.glob(f"*{ext}"))
            config_files.extend((self.project_root / "config").glob(f"*{ext}"))
            config_files.extend((self.project_root / "docs").glob(f"*{ext}"))

        regex_symbol = re.compile(rf"\b{re.escape(old_name)}\b")

        for path in config_files:
            if not path.exists():
                continue
            try:
                content = path.read_text(encoding="utf-8")
                if old_name in content:
                    new_content = regex_symbol.sub(new_name, content)
                    if new_content != content:
                        print(f"  [CONFIG] Updating reference in {path.name}")
                        if not self.dry_run:
                            path.write_text(new_content, encoding="utf-8")
            except Exception:  # guardian: allow-silent_swallower
                continue

    def deep_refactor_name(self, old_name: str, new_name: str) -> int:
        """
        Performs a Deep Rename of a class symbol across the entire codebase.
        Updates:
        1. Class definitions: 'class OldName:' -> 'class NewName:'
        2. Imports: 'from x import OldName' -> 'from x import NewName'
        3. Init Exports: 'from .OldFile import OldName' -> 'from .NewFile import NewName'
        4. Type Hints / Usages: 'x: OldName' -> 'x: NewName'
        """
        count = 0
        # Strict word boundary regex to prevent substring matches
        regex_symbol = re.compile(rf"\b{re.escape(old_name)}\b")

        for path in self.file_registry:
            if not path or not path.exists():
                continue

            try:
                content = path.read_text(encoding="utf-8")

                # Optimization: Skip files that don't contain the symbol
                if old_name not in content:
                    continue

                # Apply Global Replace for Class Name
                new_content = regex_symbol.sub(new_name, content)

                # Special Handling for __init__.py re-exports
                if path.name == "__init__.py":
                    # Fix: from .OldFile import NewName -> from .NewFile import NewName
                    old_file_stem = old_name  # Assuming file matched class name
                    new_file_stem = new_name

                    # Regex to fix the module source in relative imports
                    # Pattern: from .OldName import
                    regex_init_mod = re.compile(
                        rf"(from\s+\.+){re.escape(old_file_stem)}(\s+import)"
                    )
                    new_content = regex_init_mod.sub(rf"\1{new_file_stem}\2", new_content)

                if new_content != content:
                    if not self.dry_run:
                        path.write_text(new_content, encoding="utf-8")
                    count += 1
            except Exception as e:  # guardian: allow-silent_swallower
                print(f"  [ERROR] Refactoring failed in {path.name}: {e}")
                continue
        return count

    def update_imports(self, old_name: str, new_name: str) -> int:
        """Refactors imports using the in-memory registry to avoid O(N²) disk hits."""
        count = 0
        old_mod, new_mod = old_name.replace(".py", ""), new_name.replace(".py", "")

        # Ultra-Precision Regex: Handles 'from x import', 'import x', and 'import x as y'
        # Critical Analysis: Expanded to handle relative imports (e.g., 'from .old_mod import')
        # by adding an optional dot-prefix group. This is vital for maintaining integrity
        # in hierarchical multi-agent systems where local package imports are standard.
        regex_from = re.compile(  # guardian: allow-path_fragility
            r"(?P<prefix>from\s+\.*)" + re.escape(old_mod) + r"(?P<suffix>\s+import)"
        )
        regex_import = re.compile(  # guardian: allow-path_fragility
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

                new_content = regex_from.sub(
                    r"\g<prefix>" + new_mod + r"\g<suffix>", content
                )  # guardian: allow-path_fragility
                new_content = regex_import.sub(
                    r"\g<prefix>" + new_mod + r"\g<suffix>", new_content
                )  # guardian: allow-path_fragility

                if new_content != content:
                    if not self.dry_run:
                        path.write_text(new_content, encoding="utf-8")
                    count += 1
            except Exception:  # guardian: allow-silent_swallower
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
            except Exception:  # guardian: allow-silent_swallower
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
                    print("  [ANALYSIS] Files are IDENTICAL. Deleting redundant.")
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
                    print("  [ANALYSIS] Files are DIFFERENT. Conflict rename.")
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

            except Exception as e:  # guardian: allow-silent_swallower
                print(f"  [ERROR] Failed to read {src}: {e}")
                return False  # [HARDENED] Don't attempt rollback

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
                except Exception:  # guardian: allow-silent_swallower
                    pass  # Best effort cleanup

            print(f"  [SUCCESS] {src.name} -> {dest_name}")
            return True

        except Exception as e:  # guardian: allow-silent_swallower
            print(f"[ERROR] Rollback failed: {e}")
            print(f"  [CRITICAL] Manual intervention required - file may be at {temp_path}")

            return False

    def get_compliant_name(self, path: Path, file_type: FileType) -> str | None:
        """Calculates the target filename. Returns None if no change needed."""
        if file_type in {"IGNORE", "TYPES", "UTILITY"}:
            return None

        # SCRIPT: Force Snake Case
        if file_type == "SCRIPT":
            snake = re.sub(r"(?<!^)(?=[A-Z])", "_", path.stem).lower().replace("__", "_")
            return f"{snake}.py" if f"{snake}.py" != path.name else None

        # TEST: Force test_ prefix + snake_case
        if file_type == "TEST":
            clean = re.sub(r"(?<!^)(?=[A-Z])", "_", path.stem.replace("test_", "")).lower()
            return f"test_{clean}.py" if f"test_{clean}.py" != path.name else None

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

            # [HARDENED] Type-Specific Naming Rules
            if file_type == "AGENT":
                if not target_name.endswith("Agent"):
                    target_name += "Agent"

            elif file_type == "PROTOCOL":
                # Protocols must remain strictly PascalCase, preserving 'I' prefix.
                pass

            elif file_type == "ENGINE":
                # Engines are high-authority classes, strictly PascalCase.
                pass

            elif file_type == "GATEWAY":
                # Gateways are strictly PascalCase.
                pass

            elif file_type == "STUB":
                # [CRITICAL] Stub Sovereignty: Strip 'Agent' and enforce 'Stub'
                # Example: SubAtomicAgent -> SubAtomicStub
                target_name = target_name.replace("Agent", "")
                if not target_name.endswith("Stub"):
                    target_name += "Stub"

            # WINDSURF IMPLEMENTATION: New naming conventions
            elif file_type == "ORCHESTRATOR":
                # Force PascalCase and ensure Orchestrator suffix
                if not target_name.endswith("Orchestrator"):
                    target_name += "Orchestrator"

            elif file_type == "ADAPTER":
                # Force PascalCase and ensure Strategy suffix (for Strategy patterns)
                if "Strategy" not in target_name:
                    # If it's an Adapter, ensure Adapter suffix
                    if "Adapter" not in target_name:
                        target_name += "Strategy"  # Default to Strategy for consistency

            elif file_type == "FACTORY":
                # Force PascalCase and ensure Factory suffix
                if not target_name.endswith("Factory"):
                    target_name += "Factory"

            elif file_type == "VALIDATOR":
                # Force snake_case and ensure validator suffix
                # Convert PascalCase to snake_case
                s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", target_name)
                target_name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
                if not target_name.endswith("_validator"):
                    target_name += "_validator"

            elif file_type == "CONFIG":
                # Force snake_case and ensure config suffix
                # Convert PascalCase to snake_case
                s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", target_name)
                target_name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
                if not target_name.endswith("_config"):
                    target_name += "_config"

            # Note: TEST handling is done earlier in the method (before AST parsing)

            return f"{target_name}.py"
        except Exception as e:  # guardian: allow-silent_swallower
            print(f"[ERROR] Classification failed: {e}")
            return "IGNORE"

    def heal(self, violation: dict) -> dict:  # guardian: allow-type-erasure
        """Heal naming violations using unified classification logic.

        Uses the same classify_file() and get_compliant_name() methods as the
        main audit to ensure consistent detection and healing behavior.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (naming)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        violation_type = violation.get("type", "naming")
        path = violation.get("path", "")

        Logger.info(f"[HEAL] Processing {violation_type} violation at {path}")

        if violation_type != "naming":
            Logger.warning(f"  Unknown violation type: {violation_type}")
            return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

        file_path = Path(path)

        # Validate file exists and is Python
        if not file_path.exists():
            Logger.warning(f"  File does not exist: {path}")
            return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

        if file_path.suffix != ".py":
            Logger.info(f"  Non-Python file {path}, skipping")
            return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

        try:
            # Use unified classification logic (same as main audit)
            file_type = self.classify_file(file_path)

            if file_type == "IGNORE":
                Logger.info(f"  File {path} is IGNORE type, skipping")
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

            # Use unified naming logic (same as main audit)
            new_name = self.get_compliant_name(file_path, file_type)

            if not new_name or new_name == file_path.name:
                Logger.info(f"  File {path} is already compliant")
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

            new_path = file_path.parent / new_name

            if new_path.exists():
                Logger.warning(f"  Target {new_path} already exists")
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

            # Perform the rename
            file_path.rename(new_path)
            Logger.info(f"  Renamed {path} -> {new_path}")

            return {"violations_fixed": 1, "violations_found": 1, "errors": 0, "skipped": 0}

        except Exception as e:  # guardian: allow-silent_swallower
            Logger.error(f"  Error processing {path}: {e}")
            return {"violations_fixed": 0, "violations_found": 1, "errors": 1, "skipped": 0}

    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,  # guardian: allow-magic_configuration
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
        agent_id = f"FileClassificationAgent@{self.project_root}"
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

        except Exception as e:  # guardian: allow-silent_swallower
            print(f"[ERROR] FileClassificationAgent healing failed: {e}")
            return {"violations_found": 0, "violations_fixed": 0, "errors": 1, "skipped": 0}
        finally:
            _call_path.discard(agent_id)


def main():
    """Standalone execution for testing."""
    import argparse

    parser = argparse.ArgumentParser(description="File Classification Agent")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--validate", action="store_true", help="Check compliance only")
    args = parser.parse_args()

    from pathlib import Path

    is_dry_run = args.dry_run or args.validate

    agent = FileClassificationAgent(
        project_root=Path("."), dry_run=is_dry_run, validate_only=args.validate
    )

    result = agent.run()
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
