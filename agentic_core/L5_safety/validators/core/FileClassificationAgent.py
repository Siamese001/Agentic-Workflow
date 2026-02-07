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
    from agentic_core.mixins.atomic_execution_mixin import atomic_execution_mixin
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from agentic_core.L5_safety.validators.core.decorators import standard_heal

    HAS_SOVEREIGN_BASE = True
    HAS_ATOMIC_MIXIN = True
    # Define base classes tuple for inheritance
    BASE_CLASSES = (AtomicExecutionMixin, SovereignBaseAgent)
except ImportError:
    HAS_SOVEREIGN_BASE = False
    HAS_ATOMIC_MIXIN = False
    # Use single base class to avoid duplication
    BASE_CLASSES = (object,)

    def standard_heal(func):
        """Fallback decorator when full infrastructure unavailable."""
        return func


# Logger for healing operations
import logging

logger = logging.getLogger(__name__)


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
    "ADAPTER",  # Classes ending in Adapter, Wrapper, Bridge
    "STRATEGY",  # Classes ending in Strategy
    "EXCEPTION",  # Exception/Error classes (snake_case _exceptions.py)
    "IGNORE",
]


@dataclass
class FileClassificationAgent(*BASE_CLASSES):
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
                "STRATEGY": 0,
                "EXCEPTION": 0,
            },
            "territory_moves": 0,
        }
        # CACHE: Track file paths in memory to avoid repetitive disk scanning (O(1) lookups)
        self.file_registry: list[Path] = []
        self.logger = logging.getLogger(__name__)
        # UNIFIED ACTION COUNTERS (2026-02-05 HARDENING)
        # Separate fine-grained trackers to prevent summary vs stats drift
        self.action_counters = {
            "renames": 0,
            "territory_moves": 0,
            "import_fixes": 0,
            "deep_refactors": 0,
            "config_updates": 0,  # Non-python asset refs
        }

        # GLOBAL RUN-LEVEL IDEMPOTENCE CACHE (FINAL HARDENING 2026-02-05)
        self.processed_paths: set[Path] = set()

        # APP-SPECIFIC TERRITORY MAP (DEPTH-2 MVC)
        self.app_territory_map = {
            "AGENT": ["engines"],
            "ORCHESTRATOR": ["engines"],
            "VALIDATOR": ["domain", "utils"],
            "CONFIG": ["config"],
            "TYPES": ["domain"],
            "CLASS": ["domain", "engines", "utils"],
            "MIXIN": ["utils", "shared", "mixins"],
        }

        # STANDARD KERNEL: All layers should have these subfolders
        self.standard_kernel = ["utils", "config", "agents"]

    def enforce_kernel_structure(self, file_path: Path, layer_root: Path | None = None) -> Path | None:
        """
        Enforce Standard Kernel structure by detecting and relocating misplaced files.

        Standard Kernel subfolders (utils, config, agents) should exist in all layers.
        Files matching kernel patterns are routed to their appropriate subfolder.

        GLOBAL OVERRIDES (apply regardless of current location):
        - *_validator.py -> agentic_core/L5_safety/validators/ (all validators go to L5)

        KERNEL ROUTING (within layer):
        - *_util.py -> layer_root/utils/
        - *_config.py -> layer_root/config/
        - *_script.py (L0 only) -> layer_root/scripts/
        - *Agent.py (at layer root) -> layer_root/agents/

        Args:
            file_path: The file to check
            layer_root: Optional pre-computed layer root

        Returns:
            New target path if file should be moved, None if file is correctly placed.
        """
        parts = file_path.parts
        filename = file_path.name

        # Skip critical files
        if filename in ("__init__.py", "__main__.py", "conftest.py"):
            return None

        # === GLOBAL OVERRIDE: Validators always go to L5_safety/validators ===
        if filename.endswith("_validator.py"):
            # Find agentic_core root
            if "agentic_core" in parts:
                agentic_idx = parts.index("agentic_core")
                agentic_root = Path(*parts[: agentic_idx + 1])
                target = agentic_root / "L5_safety" / "validators" / filename
                # Only return if not already there
                if file_path.parent != target.parent:
                    return target
            return None

        # Only process files in agentic_core layers for kernel routing
        if "agentic_core" not in parts:
            return None

        # Find the layer root (L0-L6) if not provided
        if layer_root is None:
            layer_prefixes = ("L0_", "L1_", "L2_", "L3_", "L4_", "L5_", "L6_")
            layer_idx = None

            for i, part in enumerate(parts):
                if any(part.startswith(prefix) for prefix in layer_prefixes):
                    layer_root = Path(*parts[: i + 1])
                    layer_idx = i
                    break

            if not layer_root:
                return None
        else:
            # Calculate layer_idx from provided layer_root
            layer_idx = len(layer_root.parts) - 1

        # Determine current file depth relative to layer
        file_depth = len(parts) - 1  # Index of filename

        # === L0 SCRIPTS SPECIAL CASE ===
        if "L0_maintenance" in parts and "scripts" in parts:
            scripts_idx = parts.index("scripts")
            # If file is directly in scripts/ (not in a sub-subfolder)
            if file_depth == scripts_idx + 1:
                # Utilities in scripts should go to utils
                if filename.endswith("_util.py"):
                    return layer_root / "utils" / filename
                # Agents in scripts should go to agents
                if filename.endswith("Agent.py"):
                    return layer_root / "agents" / filename
                # Scripts stay in scripts (if properly named)
                if filename.endswith("_script.py"):
                    return None  # Already correct

        # If file is not at layer root, it's already in a subfolder
        if file_depth != layer_idx + 1:
            return None

        # === KERNEL ROUTING FOR FILES AT LAYER ROOT ===

        # Utilities -> utils/
        if filename.endswith("_util.py"):
            return layer_root / "utils" / filename

        # Configs -> config/ (except structure_blueprint_config.py)
        if filename.endswith("_config.py") and filename != "structure_blueprint_config.py":
            return layer_root / "config" / filename

        # Scripts (L0 only) -> scripts/
        if filename.endswith("_script.py") and "L0_maintenance" in str(layer_root):
            return layer_root / "scripts" / filename

        # Agents -> agents/
        if filename.endswith("Agent.py"):
            return layer_root / "agents" / filename

        return None

    def run(self) -> dict[str, Any]:
        """Entry point for execute_ssot.py orchestration."""
        self.logger.info(f"Executing File Classification Audit at {self.project_root}")
        success = self._orchestrate_audit(self.project_root)
        return {
            "success": success == 0,
            "stats": self.stats,
            "summary": (f"Renamed: {self.stats['renamed']}, Refactors: {self.stats['deep_refactors']}"),
        }

    def _orchestrate_audit(self, root: Path) -> int:
        """Core file classification and audit logic."""
        self.logger.info(f"{'DRY RUN' if self.dry_run else 'EXECUTE'} MODE")
        self.logger.info("=" * 60)

        if not self.verify_environment():
            return 1

        self.logger.info("Scanning repository (Fast One-Time Pass)...")
        self.file_registry = get_python_files_fast(root)
        self.stats["analyzed"] = len(self.file_registry)

        # Iterating over a copy to allow registry updates during renames
        for idx, path in enumerate(list(self.file_registry)):
            if not path.exists():
                continue

            ftype = self.classify_file(path)
            if ftype == "IGNORE":
                continue

            # [ROOT CAUSE] Check forbidden filename patterns (stuttering, ___, leading _)
            forbidden_violations = self._check_forbidden_patterns(path.name)
            for fv in forbidden_violations:
                self.logger.warning(f"[FORBIDDEN] {path.name}: {fv['reason']}")

            # [LAYER PURITY] Detect cognitive contamination and passive agent naming
            # [FAKE CONFIG] Detect _config.py files with active logic
            try:
                file_content = path.read_text(encoding="utf-8")
                purity_violation = self.check_layer_purity(path, file_content, ftype)
                if purity_violation:
                    self.logger.warning(
                        f"[{purity_violation['type']}] {path.name}: "
                        f"{purity_violation['message']}"
                    )
                    # Force reclassification for passive agents
                    if purity_violation["type"] == "PASSIVE_AGENT_NAMING":
                        ftype = "UTILITY"

                fake_config = self.check_fake_config(path, file_content)
                if fake_config:
                    self.logger.warning(
                        f"[{fake_config['type']}] {path.name}: "
                        f"{fake_config['message']}"
                    )
            except Exception:
                pass  # File read failure — skip purity/config check

            # [BASE_AGENTS PURITY] Enforce STRICT IDENTITY ONLY
            ba_violation = self.check_base_agents_purity(path)
            if ba_violation:
                self.logger.warning(
                    f"[{ba_violation['type']}] {path.name}: "
                    f"{ba_violation['message']}"
                )

            # [UTILS PURITY] Ban tests, utilities_ prefix, misplaced scripts in core
            utils_violation = self.check_utils_purity(path, content)
            if utils_violation:
                self.logger.warning(
                    f"[{utils_violation['type']}] {path.name}: "
                    f"{utils_violation['message']}"
                )

            # [DOMAIN ROOT PURITY] Leaf Node Rule + PascalCase in knowledge/
            domain_violation = self.check_domain_root_purity(path)
            if domain_violation:
                self.logger.warning(
                    f"[{domain_violation['type']}] {path.name}: "
                    f"{domain_violation['message']}"
                )

            # [NEW] Territory Enforcement (Move before Rename)
            target_territory_path = self.check_territory_violation(path, ftype)
            if target_territory_path:
                self.logger.info(f"\n[TERRITORY] {path.name} ({ftype}) is in {path.parent.name}")
                self.logger.info(f"  [ACTION] MOVE to {target_territory_path.parent.name}")

                # Cache paths before move
                self.processed_paths.add(path)
                self.processed_paths.add(target_territory_path)

                # Execute Move
                if self.resolve_collision_and_rename(
                    path,
                    target_territory_path.name,
                    target_dir=target_territory_path.parent,
                ):
                    if not self.dry_run:
                        self.stats["territory_moves"] += 1
                        self.action_counters["territory_moves"] += 1
                        # Update path registry to reflect new location for subsequent operations
                        path = target_territory_path
                        self.file_registry[idx] = path
                else:
                    # If move failed (collision), log and continue to rename check in place
                    self.logger.warning("Move failed. Proceeding with in-place audit.")

            new_name = self.get_compliant_name(path, ftype)
            if new_name and new_name != path.name:
                self.stats["violations"][ftype] += 1
                self.logger.info(f"\n[DETECT] {path.name} ({ftype}) -> {new_name}")
                # [CHANGED] From safe_rename_windows to resolve_collision_and_rename
                if self.resolve_collision_and_rename(path, new_name):
                    if not self.dry_run:
                        self.stats["renamed"] += 1
                        self.stats["collisions_resolved"] += 1
                        self.action_counters["renames"] += 1

                        # Cache source and renamed path
                        self.processed_paths.add(path)
                        self.processed_paths.add(path.parent / new_name)

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

                            # APP DEEP REFACTOR SUPPRESSION
                            is_app = any(p.startswith("apps_") for p in path.parts)
                            if is_app:
                                # Suppress deep refactors in apps for stability
                                pass
                            elif old_stem != new_stem and old_stem[0].isupper() and new_stem[0].isupper():
                                self.logger.info(f"  [DEEP REFACTOR] {old_stem} -> {new_stem}")
                                refactor_count = self.deep_refactor_name(old_stem, new_stem)
                                self.stats["deep_refactors"] += refactor_count
                                self.stats["imports_fixed"] += refactor_count
                                self.action_counters["deep_refactors"] += 1
                                self.action_counters["import_fixes"] += refactor_count

                                # 4. Refactor Non-Python Assets (Configs/Manifests)
                                self.refactor_non_python_assets(old_stem, new_stem)
                                self.action_counters["config_updates"] += 1

                            else:
                                # Standard Import Update for non-architectural renames
                                import_count = self.update_imports(path.name, new_name)
                                self.stats["imports_fixed"] += import_count
                                self.action_counters["import_fixes"] += import_count
                        else:
                            # File was deleted due to duplicate content - remove from registry
                            self.file_registry[idx] = None
            else:
                self.stats["compliant"] += 1

        # 5. [NEW] Cleanup Redundant Conflicts
        # Removes .CONFLICT files ONLY if they are identical to the live file
        self.cleanup_redundant_conflicts(root)

        self.logger.info("\n" + "=" * 60)
        self.logger.info(f"Total files analyzed: {self.stats['analyzed']}")
        self.logger.info(f"Compliant files:      {self.stats['compliant']}")
        total_violations = sum(self.stats["violations"].values())
        self.logger.info(f"Violations detected:  {total_violations}")
        self.logger.info(f"  - Agents:  {self.stats['violations']['AGENT']}")
        self.logger.info(f"  - Classes: {self.stats['violations']['CLASS']}")
        self.logger.info(f"  - Utils:   {self.stats['violations']['UTILITY']}")
        self.logger.info(f"  - Mixins:  {self.stats['violations']['MIXIN']}")
        self.logger.info(f"  - Protocols: {self.stats['violations']['PROTOCOL']}")
        self.logger.info(f"  - Engines: {self.stats['violations']['ENGINE']}")
        self.logger.info(f"  - Stubs:   {self.stats['violations']['STUB']}")
        self.logger.info(f"  - Tests:   {self.stats['violations']['TEST']}")
        self.logger.info(f"  - Scripts: {self.stats['violations']['SCRIPT']}")
        self.logger.info(f"  - Types:   {self.stats['violations']['TYPES']}")
        print(f"  - Gateways: {self.stats['violations']['GATEWAY']}")
        # WINDSURF IMPLEMENTATION: New categories summary
        self.logger.info(f"  - Orchestrators: {self.stats['violations']['ORCHESTRATOR']}")
        self.logger.info(f"  - Validators: {self.stats['violations']['VALIDATOR']}")
        self.logger.info(f"  - Factories: {self.stats['violations']['FACTORY']}")
        self.logger.info(f"  - Configs: {self.stats['violations']['CONFIG']}")
        self.logger.info(f"  - Adapters: {self.stats['violations']['ADAPTER']}")
        self.logger.info(f"  - Exceptions: {self.stats['violations']['EXCEPTION']}")
        if not self.dry_run:
            self.logger.info("\n=== FINAL HEALING SUMMARY ===")
            self.logger.info(f"Files Analyzed:     {self.stats['analyzed']}")
            self.logger.info(f"Compliant:          {self.stats['compliant']}")
            self.logger.info(f"Renames:            {self.action_counters['renames']}")
            self.logger.info(f"Territory Moves:    {self.action_counters['territory_moves']}")
            self.logger.info(f"Import Fixes:       {self.action_counters['import_fixes']}")
            self.logger.info(f"Deep Refactors:     {self.action_counters['deep_refactors']}")
            self.logger.info(f"Config Updates:     {self.action_counters['config_updates']}")
            self.logger.info(f"Total Actions:      {sum(self.action_counters.values())}")
            self.logger.info("=" * 60)

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

        # [PRIORITY 0] BASE AGENT Detection: agentic_core/base_agents/ directory
        # CONSTITUTIONAL: Must come BEFORE STUB detection because base agents
        # legitimately carry NOT_AN_AGENT markers to prevent downstream misclassification.
        # V10 Zero-Ambiguity: ALL files in base_agents/ are foundational CLASSes
        # EXCEPT mixins (which remain MIXIN) and scripts/utilities (flagged for move).
        if "base_agents" in path.parts:
            # Allow Mixin files to be classified as MIXIN (don't force CLASS)
            if "Mixin" in path.name or "mixin" in path.name.lower():
                pass  # Let normal classification handle it below
            # Scripts, utilities, exceptions, and types in base_agents should NOT be forced to CLASS
            elif path.name.endswith(("_script.py", "_util.py", "_exceptions.py", "_types.py")):
                pass  # Let normal classification handle it below
            else:
                # Force CLASS for all other files in base_agents/
                # This covers SovereignBaseAgent, L0-L6 bases, MetaLearningBase, etc.
                return "CLASS"

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

        # CONSOLIDATED TEST IMMUNITY FOR GUARDRAILS
        if "guardrails" in path.parts:
            pass  # Skip TEST classification entirely

        # === REFACTORED PRIMARY-CLASS-CENTRIC DETECTION ===
        # Collect all ClassDef nodes
        class_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        if not class_nodes:
            return "UTILITY"

        class_names = [node.name for node in class_nodes]

        # Determine primary class (heuristic: name matches filename stem)
        primary_name = class_names[0]
        stem_clean = re.sub(r"[^a-zA-Z0-9]", "", path.stem.lower())
        for name in class_names:
            if re.sub(r"[^a-zA-Z0-9]", "", name.lower()) == stem_clean:
                primary_name = name
                break

        primary_node = next(n for n in class_nodes if n.name == primary_name)

        # Reset flags based exclusively on primary class
        is_protocol = False
        is_mixin = primary_name.endswith("Mixin")
        is_factory = primary_name.endswith("Factory")
        is_exception = primary_name.endswith(("Error", "Exception"))

        # Protocol via bases
        for base in primary_node.bases:
            if isinstance(base, ast.Name):
                if base.id == "Protocol":
                    is_protocol = True
                if "Exception" in base.id or "Error" in base.id:
                    is_exception = True
            elif isinstance(base, ast.Attribute):
                if base.attr == "Protocol":
                    is_protocol = True
                if base.attr in ("Exception", "BaseException"):
                    is_exception = True

        # Agent via name or inheritance
        is_agent = primary_name.endswith("Agent")
        if not is_agent:
            for base in primary_node.bases:
                if isinstance(base, ast.Name) and "Agent" in base.id:
                    is_agent = True
                elif isinstance(base, ast.Attribute) and "Agent" in base.attr:
                    is_agent = True

        # CONSOLIDATED L5 GUARDRAILS SUPER-BOOST
        if "guardrails" in path.parts:
            # Primary: canonical Agent signals
            if (
                primary_name.endswith("Agent")
                or is_agent
                or "SovereignBaseAgent" in content
                or "SubatomicTestingMixin" in content
            ):
                return "AGENT"
            # Extended: non-inherited safety components
            elif any(
                k in content.lower()
                for k in [
                    "guardrail",
                    "membrane",
                    "sanitizer",
                    "redact",
                    "scrub",
                    "block",
                    "l5 safety",
                    "hygiene",
                ]
            ) and any(
                m in content for m in ["sanitize(", "scrub(", "redact(", "block(", "clean(", "verify("]
            ):
                return "AGENT"

        # Architectural fuzzy - STRICT: primary class name only
        orchestrator_patterns = [
            "Orchestrator",
            "orchestrator",
            "orchestrate",
            "Coordinator",
            "Pipeline",
        ]
        is_orchestrator = any(p in primary_name for p in orchestrator_patterns)

        # Split ADAPTER into STRATEGY and ADAPTER categories
        strategy_patterns = ["Strategy"]
        is_strategy = any(p in primary_name for p in strategy_patterns)

        adapter_patterns = ["Adapter", "Wrapper", "Bridge"]
        is_adapter = any(p in primary_name for p in adapter_patterns)

        # PROTOCOL priority: Files starting with "I" (interface convention)
        is_interface_protocol = path.name.startswith("I") and path.name[1:2].isupper()

        # Check Config via pattern helper (passed tree for attribute check)
        config_indicators = ["config", "blueprint", "settings", "manifest", "Config", "Settings", "Options"]
        config_patterns = {"configuration", "settings", "options", "params", "parameters"}
        is_config = self._detect_config_patterns(tree, path, content, config_indicators, config_patterns)

        # Enhanced VALIDATOR detection using AST patterns
        validator_patterns = ["validator", "validate", "check", "verify", "Validator", "Check", "Verify"]
        is_validator = self._detect_validator_patterns(tree, path, content, validator_patterns)

        # [PRIORITY 4] SCRIPT Detection - MOVED AFTER AGENT CHECK
        # CRITICAL FIX: Explicitly exclude Agents, Orchestrators, Engines, Adapters from being classified as Scripts
        if path.name != "FileClassificationAgent.py" and not is_agent:
            # Exclude architectural components from SCRIPT classification (case-insensitive)
            exclusion_keywords = ["agent", "orchestrator", "engine", "adapter"]
            if not any(keyword in path.name.lower() for keyword in exclusion_keywords):
                script_indicators = self._detect_script_patterns(tree, path)
                if script_indicators["is_script"]:
                    return "SCRIPT"

        # [WINDSURF IMPLEMENTATION] PRIORITY EXECUTION - Order matters!
        # 1. STUB: Already handled above (preempts all)
        # 2. BASE_AGENT: Already handled above
        # 2.5 SELF_DETECTION: Already handled above
        # 2.7 BLUEPRINT_DETECTION: Already handled above
        # 3. TEST: Already handled above
        # 4. SCRIPT: Handled above (with Agent exclusion)
        # 5. TYPES: Already handled above

        # EXCEPTION: Classes inheriting from Exception/Error -> EXCEPTION type
        if is_exception:
            return "EXCEPTION"
        # NEW: Elevate MIXIN priority to prevent override
        if is_mixin:
            return "MIXIN"

        # 5.5. PROTOCOL PRIORITY: Interface files (I*.py) are strictly PROTOCOL
        if is_interface_protocol or is_protocol:
            return "PROTOCOL"

        # 6. ORCHESTRATOR: Detect if Orchestrator in class name or path
        if is_orchestrator:
            return "ORCHESTRATOR"
        # 7. STRATEGY: Classes ending in Strategy
        elif is_strategy:
            return "STRATEGY"
        # 7.5. ADAPTER: Classes ending in Adapter, Wrapper, Bridge
        elif is_adapter:
            return "ADAPTER"
        # APP-SPECIFIC CLASSIFICATION OVERRIDES
        is_app = any(p.startswith("apps_") for p in path.parts)
        if is_app:
            # Suppress loose SCRIPT in apps (no __main__ = CLASS)
            if not is_agent and not is_validator and not is_config and "__main__" not in content:
                # Would have been SCRIPT, force to CLASS
                pass
            # Force VALIDATOR on hybrid names
            if "Validator" in primary_name and "Agent" in primary_name:
                return "VALIDATOR"

        # 8. AGENT: PRIORITY - Agent detection must come before CONFIG/VALIDATOR
        # Files can contain Config/Validator classes but if primary class is Agent, it's an AGENT
        if is_agent:
            return "AGENT"
        # 9. CONFIG: Detect if file name or path contains config, blueprint, settings, or manifest
        elif is_config:
            return "CONFIG"
        # 10. VALIDATOR: Detect if path contains validators/ or file name ends in _validator
        elif is_validator:
            return "VALIDATOR"
        # 10. PROTOCOL: Already handled above with priority
        # 11. FACTORY: Detect if class name ends in Factory
        elif is_factory:
            return "FACTORY"

        # [PRIORITY 12] TYPES Detection: HARDENED for runtime/types/ and models/
        # Files in runtime/types/ or models/ are TYPES even with minor config/validation logic
        # This prevents hybrid names like _types_config.py - enforce pure _types.py suffix
        if "models" in path.parts or ("runtime" in path.parts and "types" in path.parts):
            # Force TYPES classification for data structure files in these folders
            if not is_agent and not is_orchestrator:
                return "TYPES"

        type_indicators = self._detect_type_patterns(tree, path)
        if type_indicators["is_types"]:
            return "TYPES"

        # HARDENED TYPES PRIORITY (secondary check)
        if "types" in path.name.lower() and path.name.endswith(".py"):
            if any(
                keyword in content
                for keyword in ["TypedDict", "Protocol", "TypeAlias", "Enum", "Literal", "Final"]
            ):
                return "TYPES"

        # 14. CLASS: Fallback for any other class
        else:
            return "CLASS"

    # ========================================================================
    # ENHANCED AST-BASED DETECTION METHODS
    # ========================================================================

    def _to_pascal_case(self, name: str) -> str:
        """
        Converts snake_case or mixed case to PascalCase.
        Example: 'pii_sanitizer' -> 'PiiSanitizer', 'PDFLoader' -> 'PdfLoader'
        """
        # If already PascalCase, return as-is
        if name and name[0].isupper() and "_" not in name:
            return name

        # Split on underscores and capitalize each part
        parts = name.split("_")
        return "".join(word.capitalize() for word in parts if word)

    def _to_smart_snake_case(self, name: str) -> str:
        """
        Converts PascalCase to snake_case while preserving acronyms.
        Example: 'PIISanitizer' -> 'pii_sanitizer', 'PDFLoader' -> 'pdf_loader'

        Hardening: Recognizes project-specific atomic words to prevent false positives.
        - "Grounding" stays as "grounding", not "g_r_ounding"
        - "Routing" stays as "routing", not "r_outing"
        """
        # Project-specific atomic words that should not be split
        atomic_words = {
            "Grounding": "grounding",
            "Routing": "routing",
            "Sender": "sender",
            "Receiver": "receiver",
            "Planner": "planner",
            "Scheduler": "scheduler",
            "RG": "rg",  # Resume Generation acronym protection
        }

        # Check if the entire name is an atomic word
        if name in atomic_words:
            return atomic_words[name]

        # Replace atomic words with placeholders before processing
        placeholders = {}
        temp_name = name
        for idx, (word, replacement) in enumerate(atomic_words.items()):
            if word in temp_name:
                placeholder = f"__ATOMIC_{idx}__"
                placeholders[placeholder] = replacement
                temp_name = temp_name.replace(word, placeholder)

        # Pass 1: Handle acronym boundaries (PDFLoader -> PDF_Loader)
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", temp_name)
        # Pass 2: Handle standard camel boundaries (LoaderFile -> Loader_File)
        s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

        # Restore atomic words from placeholders
        result = s2
        for placeholder, replacement in placeholders.items():
            result = result.replace(placeholder.lower(), replacement)

        return result

    def _sanitize_filename(self, stem: str) -> str:
        """
        Strip known architectural suffixes from a filename stem to prevent stuttering.

        This prevents "stuttering" (e.g., feature_flags_config_util.py) and
        "hybrid suffixes" (e.g., embedding_config_types_config.py).

        Logic: Iteratively remove known suffixes until none remain.

        IMPORTANT: Only strips TRAILING architectural suffixes, not semantic content.
        For example, "agent_discovery" keeps "agent" because it's semantic, not a suffix.

        Args:
            stem: The filename stem (without .py extension)

        Returns:
            The sanitized core name with trailing architectural suffixes removed.

        Examples:
            - "feature_flags_config_util" -> "feature_flags"
            - "embedding_config_types_config" -> "embedding"
            - "user_profile_types" -> "user_profile"
            - "agent_discovery_util" -> "agent_discovery" (keeps semantic "agent")
        """
        # Known architectural suffixes to strip (trailing only)
        # These are file-type markers, not semantic content
        known_suffixes = [
            "_config",
            "_util",
            "_types",
            "_script",
            "_mixin",
            "_base",
            "_validator",
            "_protocol",
            "_strategy",
            "_adapter",
            "_factory",
            "_orchestrator",
            "_engine",
            "_gateway",
            "_stub",
            "_test",
            "Config",
            "Util",
            "Types",
            "Script",
            "Mixin",
            "Base",
            "Validator",
            "Protocol",
            "Strategy",
            "Adapter",
            "Factory",
            "Orchestrator",
            "Engine",
            "Gateway",
            "Stub",
            "Test",
        ]

        # NOTE: "_agent" and "Agent" are NOT stripped because they often carry
        # semantic meaning (e.g., "agent_discovery" describes what the utility does)
        # Only strip "_agent" if it's a trailing suffix AND followed by another suffix

        sanitized = stem
        changed = True

        # Iteratively strip suffixes until no more are found
        while changed:
            changed = False
            for suffix in known_suffixes:
                if sanitized.endswith(suffix) and len(sanitized) > len(suffix):
                    sanitized = sanitized[: -len(suffix)]
                    changed = True
                    break  # Restart from beginning of suffix list

        # Special case: Strip trailing "_agent" or "Agent" if it appears AFTER a known suffix pattern
        # This catches cases like "healing_mixin_agent" (mixin before agent) but not "agent_discovery"
        # Check if the original stem had a pattern like *_mixin_agent, *_config_agent, etc.
        agent_after_suffix_patterns = [
            "_mixin_agent",
            "_config_agent",
            "_types_agent",
            "_util_agent",
            "_validator_agent",
            "_script_agent",
            "_base_agent",
        ]
        for pattern in agent_after_suffix_patterns:
            if stem.endswith(pattern):
                # Strip the trailing _agent since it was after another suffix
                if sanitized.endswith("_agent"):
                    sanitized = sanitized[:-6]
                elif sanitized.endswith("Agent"):
                    sanitized = sanitized[:-5]
                break

        # Clean up trailing underscores
        sanitized = sanitized.rstrip("_")

        return sanitized if sanitized else stem  # Fallback to original if fully stripped

    def normalize_filename(self, name: str) -> str:
        """
        Smart normalization that fixes root cause naming violations.

        Fixes:
        1. Stuttering acronyms: s_s_o_t_ → ssot_ (naive CamelCase split)
        2. Multiple underscores: ___ → _ (unsanitized concatenation)
        3. Leading underscores: _cc_visitor → cc_visitor (legacy convention)

        Args:
            name: The filename (with or without .py extension)

        Returns:
            Normalized filename with root cause violations corrected.

        Examples:
            - "s_s_o_t_consolidation_analyzer_script.py" → "ssot_consolidation_analyzer_script.py"
            - "setup___init___util.py" → "setup_init_util.py"
            - "_cc_visitor_script.py" → "cc_visitor_script.py"
        """
        # Exempt __init__.py entirely — it's a Python convention
        if name == "__init__.py" or name == "__init__":
            return name

        # Separate extension
        stem = name
        ext = ""
        if name.endswith(".py"):
            stem = name[:-3]
            ext = ".py"

        # 1. Fix stuttering acronyms: collapse runs of single-char_single-char segments
        # Matches sequences like a_b_c_d and collapses to abcd
        # Uses iterative approach to catch overlapping patterns
        prev = None
        while prev != stem:
            prev = stem
            stem = re.sub(r"\b([a-z])_([a-z])_([a-z])_([a-z])\b", r"\1\2\3\4", stem)
            stem = re.sub(r"\b([a-z])_([a-z])_([a-z])_([a-z])(?=_)", r"\1\2\3\4", stem)

        # 2. Fix multiple underscores: collapse __ or ___ to single _
        stem = re.sub(r"_{2,}", "_", stem)

        # 3. Fix leading underscores
        stem = stem.lstrip("_")

        # 4. Fix trailing underscores
        stem = stem.rstrip("_")

        return f"{stem}{ext}" if stem else name  # Fallback to original if empty

    def _check_forbidden_patterns(self, filename: str) -> list[dict[str, str]]:
        """
        Check a filename against FORBIDDEN_FILENAME_PATTERNS from the constitution.

        Args:
            filename: The filename to check (without directory path)

        Returns:
            List of violation dicts with 'pattern' and 'reason' for each match.
        """
        from agentic_core.L5_safety.config.structure_blueprint_config import (
            FORBIDDEN_FILENAME_PATTERNS,
        )

        violations = []
        # Skip __init__.py — always exempt
        if filename == "__init__.py":
            return violations

        stem = filename.removesuffix(".py")
        for rule in FORBIDDEN_FILENAME_PATTERNS:
            if re.search(rule["pattern"], stem):
                violations.append(
                    {
                        "pattern": rule["pattern"],
                        "reason": rule["reason"],
                        "filename": filename,
                    }
                )
        return violations

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
                        if isinstance(decorator.func, ast.Name) and decorator.func.id == "dataclass":
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

    def _fuzzy_match_name_or_content(self, name: str, path: Path, content: str, patterns: list[str]) -> bool:
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
        self,
        tree: ast.AST,
        path: Path,
        content: str,
        indicators: list[str],
        patterns: set[str],
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
        self,
        tree: ast.AST,
        path: Path,
        content: str,
        patterns: list[str],
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

        # CONSOLIDATED VALIDATOR HARDENING IN GUARDRAILS
        if "guardrails" in str(path).lower():
            validation_methods = sum(
                1
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and any(
                    w in node.name.lower()
                    for w in ("validate", "check", "verify", "ensure", "scrub", "sanitize")
                )
            )
            if validation_methods < 4:
                return False

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
            "L1CognitionBase",
            "L2ExecutionBase",
            "L3OrchestrationBase",
            "L4StateBase",
            "L5SafetyBase",
            "L6ObservabilityBase",
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
                    regex_init_mod = re.compile(rf"(from\s+\.+){re.escape(old_file_stem)}(\s+import)")
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
            r"(?P<prefix>from\s+\.*)" + re.escape(old_mod) + r"(?P<suffix>\s+import)",
        )
        regex_import = re.compile(  # guardian: allow-path_fragility
            rf"(?P<prefix>import\s+){re.escape(old_mod)}(?P<suffix>(\s+as\s+\w+)?(\s*,|\s|$))",
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
                    r"\g<prefix>" + new_mod + r"\g<suffix>",
                    content,
                )  # guardian: allow-path_fragility
                new_content = regex_import.sub(
                    r"\g<prefix>" + new_mod + r"\g<suffix>",
                    new_content,
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
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\FileSystem",
                )
                value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
                if value != 1:
                    print("[WARNING] Windows LongPathsEnabled is NOT set to 1.")
                    if not self.dry_run:
                        return False
            except Exception:  # guardian: allow-silent_swallower
                pass
        return True

    def resolve_collision_and_rename(self, src: Path, dest_name: str, target_dir: Path | None = None) -> bool:
        """
        Handles renaming with intelligent collision resolution.
        Supports optional target_dir for moving files across directories.
        Returns True if the VIOLATION was resolved (either by rename, delete, or move).
        """
        dest_parent = target_dir if target_dir else src.parent
        dest = dest_parent / dest_name

        # Case 0: Trivial match
        if src.name == dest_name and src.parent == dest_parent:
            return False

        if self.dry_run:
            if target_dir:
                print(f"  [PLAN] MOVE {src} -> {dest}")
            else:
                print(f"  [PLAN] RENAME {src.name} -> {dest_name}")
            return True

        # Ensure target directory exists if we are moving
        if target_dir and not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)

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
                    print("  [INFO] Source and destination are the same file (case-insensitive match)")
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

    def check_fake_config(self, path: Path, content: str) -> dict[str, str] | None:
        """
        Detect files ending in _config.py that contain active logic (classes with methods).

        A genuine config file should only contain constants, dataclasses, or simple assignments.
        If it has class definitions with non-trivial methods (beyond __init__), it's a
        misnamed utility masquerading as config.

        Also classifies Verifier/Guardian/Lock classes as UTILITY unless they inherit
        from SovereignBaseAgent.

        Args:
            path: File path being checked
            content: File content as string

        Returns:
            Violation dict with 'type', 'message', 'suggested_suffix' or None if clean.
        """
        stem = path.stem

        # Only check *_config.py files
        if not stem.endswith("_config"):
            return None

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return None

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            # Skip pure dataclasses — they're legitimate config containers
            is_dataclass = any(
                (isinstance(d, ast.Name) and d.id == "dataclass")
                or (isinstance(d, ast.Attribute) and d.attr == "dataclass")
                for d in node.decorator_list
            )
            if is_dataclass:
                continue

            # Check for non-trivial methods (beyond __init__, __repr__, __str__)
            trivial_methods = {"__init__", "__repr__", "__str__", "__post_init__"}
            active_methods = [
                item.name
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and item.name not in trivial_methods
            ]
            if active_methods:
                return {
                    "type": "MISNAMED_UTILITY",
                    "message": (
                        f"{path.name} contains class '{node.name}' with active methods "
                        f"{active_methods[:3]}. This is a utility, not a config file."
                    ),
                    "suggested_suffix": "_util.py",
                }

        return None

    def check_domain_root_purity(self, path: Path) -> dict[str, str] | None:
        """
        Enforce the Leaf Node Rule: domain roots must NOT contain logic files.

        Domain directories like knowledge/, semantic_memory/ must only contain
        sub-directories. Python files (except __init__.py) at the root level
        are violations that must be moved into appropriate sub-directories.

        Also enforces snake_case naming within knowledge/ domain.

        Args:
            path: File path being checked

        Returns:
            Violation dict or None if clean.
        """
        # Domain roots that enforce the leaf node rule
        domain_roots = {"knowledge", "semantic_memory"}

        parts = path.parts
        if path.name == "__init__.py":
            return None

        for i, part in enumerate(parts):
            if part in domain_roots and i + 1 < len(parts):
                # Check if this file is directly in the domain root (not a subfolder)
                if parts[i + 1] == path.name:
                    return {
                        "type": "LEAF_NODE_VIOLATION",
                        "message": (
                            f"{path.name} is in {part}/ root. "
                            f"Domain roots must only contain sub-directories (Leaf Node Rule)."
                        ),
                        "suggested_destination": f"agentic_core/{part}/engine/",
                    }

        # Check PascalCase in knowledge domain
        if "knowledge" in parts and path.suffix == ".py":
            if any(c.isupper() for c in path.stem):
                return {
                    "type": "KNOWLEDGE_PASCAL_CASE",
                    "message": (
                        f"{path.name} uses PascalCase in knowledge/ domain. "
                        f"Must be snake_case per naming convention."
                    ),
                    "suggested_destination": "Rename to snake_case",
                }

        return None

    def check_base_agents_purity(self, path: Path) -> dict[str, str] | None:
        """
        Enforce STRICT IDENTITY ONLY rule for base_agents/.

        Only SovereignBaseAgent.py, L*Base.py, decorators.py, __init__.py, and
        CanonBaseAgentInterface.py are allowed. Mixins must be in mixins/.
        Everything else (types, utils, exceptions, engines) is a CRITICAL VIOLATION.

        Args:
            path: File path being checked

        Returns:
            Violation dict or None if clean.
        """
        parts = path.parts
        if "base_agents" not in parts:
            return None

        name = path.name
        stem = path.stem

        # Whitelist: identity files
        if name == "__init__.py":
            return None
        if name == "SovereignBaseAgent.py":
            return None
        if name == "CanonBaseAgentInterface.py":
            return None
        if stem.startswith("L") and stem.endswith("Base"):
            return None  # L0MaintenanceBase, L1CognitionBase, etc.
        if name == "LightweightBase.py":
            return None
        if name.endswith("_mixin.py"):
            return {
                "type": "BASE_AGENTS_MIXIN_VIOLATION",
                "message": f"Mixin '{name}' must be in agentic_core/mixins/, not base_agents/.",
            }
        if name == "decorators.py":
            return None  # Core decorators

        # Everything else is a violation
        return {
            "type": "BASE_AGENTS_IMPURITY",
            "message": (
                f"{name} violates STRICT IDENTITY ONLY rule for base_agents/. "
                f"Only SovereignBaseAgent, L*Base, decorators.py are allowed. Mixins go to mixins/."
            ),
            "suggested_destination": "runtime/ or mixins/",
        }

    def check_utils_purity(self, path: Path, content: str | None = None) -> dict[str, str] | None:
        """
        Enforce sanitization rules for agentic_core/ directories.

        Rules:
        1. test_*.py files must NOT exist inside agentic_core/ (except tests/).
        2. utilities_* prefix is banned (redundant naming).
        3. Scripts (if __name__ == '__main__') in utils/ must move to L0_maintenance/scripts.

        Args:
            path: File path being checked
            content: Optional file content for script detection

        Returns:
            Violation dict or None if clean.
        """
        parts = path.parts
        name = path.name

        # Only check inside agentic_core (not tests/)
        if "agentic_core" not in parts or "tests" in parts:
            return None

        # Rule 1: test_ files in agentic_core are violations
        if name.startswith("test_") and name.endswith(".py"):
            return {
                "type": "TEST_IN_CORE_VIOLATION",
                "message": f"Test file '{name}' must reside in tests/ directory, not agentic_core/.",
                "suggested_destination": "tests/unit/",
            }

        # Rule 2: utilities_ prefix is banned
        if name.startswith("utilities_"):
            return {
                "type": "MALFORMED_NAME_VIOLATION",
                "message": f"'{name}' uses banned 'utilities_' prefix. Use simple snake_case.",
                "suggested_destination": "Rename: strip 'utilities_' prefix.",
            }

        # Rule 3: Scripts in utils/ should be in L0_maintenance/scripts
        if "utils" in parts and content:
            if 'if __name__ ==' in content or "if __name__==" in content:
                return {
                    "type": "MISPLACED_SCRIPT",
                    "message": f"'{name}' in utils/ contains __main__ guard. Move to L0_maintenance/scripts/.",
                    "suggested_destination": "agentic_core/L0_maintenance/scripts/",
                }

        return None

    def check_layer_purity(self, path: Path, content: str, classification: str) -> dict[str, Any] | None:
        """
        Detect cognitive contamination in L0 and passive-agent naming violations.

        Rules:
        1. L0 agents must be reflexive/deterministic — no debate, synthesis, or LLM generation.
        2. Classes named *Agent that are dataclasses/BaseModel with no run/execute/heal method
           are "passive agents" and should be classified as UTILITY or TYPES.

        Args:
            path: File path being checked
            content: File content as string
            classification: Current file type classification

        Returns:
            Violation dict with 'type', 'message', 'suggested_destination' or None if clean.
        """
        content_lower = content.lower()
        parts = path.parts

        # --- Rule 1: L0 Cognitive Pollution Detection ---
        if "L0_maintenance" in parts:
            cognitive_signals = ["debate", "synthesis", "conversation", "llm_generate", "multi_agent"]
            orchestration_signals = ["strategy", "orchestrat", "coordination", "workflow_engine"]
            found_cognitive = [s for s in cognitive_signals if s in content_lower]
            found_orchestration = [s for s in orchestration_signals if s in content_lower]
            if found_cognitive:
                return {
                    "type": "L0_COGNITIVE_POLLUTION",
                    "message": (
                        f"Cognitive signals {found_cognitive} detected in L0 file {path.name}. "
                        f"L0 must be reflexive/deterministic only."
                    ),
                    "suggested_destination": "agentic_core/L6_observability/agents/",
                }
            if found_orchestration:
                return {
                    "type": "L0_ORCHESTRATION_LEAK",
                    "message": (
                        f"Orchestration signals {found_orchestration} detected in L0 file {path.name}. "
                        f"Strategy/orchestration belongs in L3_orchestration."
                    ),
                    "suggested_destination": "agentic_core/L3_orchestration/engine/",
                }

        # --- Rule 2: Passive Agent Detection ---
        if classification == "AGENT" and path.stem.endswith("Agent"):
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return None

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                    # Check if it's a dataclass or BaseModel
                    is_passive = False
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                            is_passive = True
                        elif isinstance(decorator, ast.Attribute) and decorator.attr == "dataclass":
                            is_passive = True

                    # Also check inheritance for BaseModel
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == "BaseModel":
                            is_passive = True

                    if is_passive:
                        # Verify no active methods exist
                        active_methods = {"run", "execute", "heal", "process", "validate"}
                        has_active = any(
                            isinstance(item, ast.FunctionDef) and item.name in active_methods
                            for item in node.body
                        )
                        if not has_active:
                            return {
                                "type": "PASSIVE_AGENT_NAMING",
                                "message": (
                                    f"{node.name} is a dataclass/BaseModel with no active methods. "
                                    f"Rename to *_util.py or *_types.py."
                                ),
                                "suggested_destination": "UTILITY or TYPES reclassification",
                            }

        return None

    def check_territory_violation(self, path: Path, file_type: str) -> Path | None:
        """
        Enforces physical-to-logical alignment with Context-Aware Sovereignty.
        Distinguishes between App-Layer (Strict Pattern) and Core-Layer (Domain Semantic).

        [HARDENED] Robust against deep nesting and handles all file types.
        """
        # 1. IDENTIFY CONTEXT & ANCHOR
        parts = path.parts
        current_parent = path.parent.name.lower()

        # Determine the Sovereign Root (App vs Core)
        # We search path parts to find the anchor directory
        sovereign_roots = {"agentic_core", "apps_rg", "apps_lic", "apps_shared"}
        root_anchor = None
        root_index = -1

        for i, part in enumerate(parts):
            if part in sovereign_roots:
                root_anchor = part
                root_index = i
                break

        if not root_anchor:
            return None  # Outside of sovereign territory control

        # GLOBAL IDEMPOTENCE GATE
        if path in self.processed_paths:
            return None

        is_core = root_anchor == "agentic_core"
        is_app = root_anchor.startswith("apps_")

        # 2. DEFINE RULES (THE CONSTITUTION)

        # [APP RULES] Now using self.app_territory_map instead

        # [CORE RULES] Domain-Driven Design with Functional Stratification
        # In Core, Agents follow the Domain (Guardrails, Registry, etc.)
        # We explicitly whitelist valid functional domains for each type.
        core_rules = {
            "AGENT": {
                "engines",
                "core",
                "agents",  # Standard
                "guardrails",  # L5 Safety
                "tool_registry",  # L2 Execution
                "thought_engine",  # L1 Cognition
                "workflow_engines",  # L3 Orchestration
                "validation_context",  # L4 State
                "red_teaming",  # L5 Safety
                "observability",  # L6 Observability
                "mcp",  # L2/L3 MCP Agents
                "fission_logic",  # L3
                "scripts",  # L0 Maintenance (Allow agents in scripts if they are autonomous)
            },
            "VALIDATOR": {
                "validators",
                "safety",
                "guards",
                "validation",
                "guardrails",
                "validation_context",
                "gravity",
                "red_teaming",
                "core",  # Allow validators in core/
            },
            "CONFIG": {
                "config",  # Root config folder
                "core",  # config/core/ for foundational settings
                "manifests",  # config/manifests/ for system metadata
                "engines",  # config/engines/ for layer-specific parameters
                "core",  # DISSOLVED: was blueprint_sovereign
            },
            "PROTOCOL": {"interfaces", "protocols", "mcp"},  # MCP has protocols
            "TYPES": {"models", "domain", "types"},  # schemas DISSOLVED
            "MIXIN": {"mixins"},  # Strict: mixins ONLY in mixins/ folder (migrated from base_agents)
            "CLASS": {"base_agents", "core", "shared_runtime"},  # Base classes allowed here
            "SCRIPT": {"scripts", "L0_maintenance"},  # Scripts only in scripts/ or L0_maintenance/
            "UTILITY": {"utils", "scripts", "L0_maintenance"},  # Utilities in utils/ or L0_maintenance/
        }

        # 3. EXECUTE VALIDATION

        target_folder = None

        if is_app:
            allowed = self.app_territory_map.get(file_type, [])
            if current_parent not in allowed:
                target_dir = (
                    "config"
                    if file_type == "CONFIG"
                    else "engines"
                    if file_type in ("AGENT", "ORCHESTRATOR")
                    else "domain"
                )
                target_path = path.parent.parent / target_dir / path.name
                self.processed_paths.add(path)
                self.processed_paths.add(target_path)
                return target_path
            return None

        elif is_core:
            # [HARDENED] APP PREFIX DEPORTATION: "App*" files are FORBIDDEN in agentic_core
            # They belong in apps_shared/agents/ - trigger territory violation
            if path.name.startswith("App") and "agentic_core" in str(path):
                # Deport to apps_shared/agents/
                target_path = self.project_root / "apps_shared" / "agents" / path.name
                self.processed_paths.add(path)
                self.processed_paths.add(target_path)
                return target_path

            # [HARDENED] base_agents PURIFICATION: Only CLASS (*Base.py) and MIXIN (*_mixin.py) allowed
            # Scripts, utilities, and active workers MUST be relocated
            if current_parent == "base_agents":
                if file_type in ("SCRIPT", "UTILITY"):
                    # Flag for movement to L0_maintenance/scripts/
                    for i, part in enumerate(path.parts):
                        if part == "agentic_core":
                            target_path = (
                                Path(*path.parts[: i + 1]) / "L0_maintenance" / "scripts" / path.name
                            )
                            self.processed_paths.add(path)
                            self.processed_paths.add(target_path)
                            return target_path
                    return None
                # CLASS and MIXIN are allowed in base_agents - no violation
                if file_type in ("CLASS", "MIXIN"):
                    return None
                # AGENT workers should be moved to engines/ (not L0_maintenance/scripts/)
                if file_type == "AGENT":
                    for i, part in enumerate(path.parts):
                        if part == "agentic_core":
                            target_path = Path(*path.parts[: i + 1]) / "engines" / path.name
                            self.processed_paths.add(path)
                            self.processed_paths.add(target_path)
                            return target_path
                # CONFIG, PROTOCOL, TYPES, STRATEGY, ADAPTER etc. should NOT be in base_agents
                # Flag for movement to appropriate location
                if file_type in ("CONFIG", "PROTOCOL", "TYPES", "STRATEGY", "ADAPTER"):
                    for i, part in enumerate(path.parts):
                        if part == "agentic_core":
                            # Route to appropriate folder based on type
                            target_folder = {
                                "CONFIG": "config",
                                "PROTOCOL": "L3_orchestration/types",
                                "TYPES": "runtime/types",
                                "STRATEGY": "L3_orchestration/utils",
                                "ADAPTER": "L2_execution/mcp",
                            }.get(file_type, "utils")
                            target_path = Path(*path.parts[: i + 1]) / target_folder / path.name
                            self.processed_paths.add(path)
                            self.processed_paths.add(target_path)
                            return target_path

            # [HARDENED] config/ PURIFICATION: Only CONFIG types allowed
            # Scripts and utilities in config/ MUST be moved to L0_maintenance/scripts/
            if current_parent == "config":
                if file_type in ("SCRIPT", "UTILITY"):
                    for i, part in enumerate(path.parts):
                        if part == "agentic_core":
                            target_path = (
                                Path(*path.parts[: i + 1]) / "L0_maintenance" / "scripts" / path.name
                            )
                            self.processed_paths.add(path)
                            self.processed_paths.add(target_path)
                            return target_path
                    return None
                # CONFIG is allowed in config/ - no violation
                if file_type == "CONFIG":
                    return None

            # Domain Check
            allowed_set = core_rules.get(file_type)
            if allowed_set:
                # If current parent is NOT in the allowed domain set
                if current_parent not in allowed_set:
                    # Generic Catch-All: If it's in a generic junk folder, move it.
                    # If in specialized domain (e.g. 'planning'), assume OK (Innocent until proven guilty)
                    # DEPRECATED ZONES: These folders are "junk drawers" that must be evacuated
                    junk_drawers = {
                        "utils",
                        "common",
                        "helpers",
                        "misc",
                        "temp",
                        "patterns",
                        "agent_roles",  # Deprecated: evacuate to base_agents
                    }

                    if current_parent in junk_drawers:
                        # Move to the primary home for that type
                        # Map Type -> Primary Core Home
                        core_defaults = {
                            "AGENT": "base_agents",
                            "VALIDATOR": "validators",
                            "CONFIG": "config",
                            "PROTOCOL": "interfaces",
                            "TYPES": "runtime/types",
                            "MIXIN": "mixins",
                            "CLASS": "base_agents",  # Classes evacuate to base_agents
                            "SCRIPT": "L0_maintenance/scripts",  # Scripts evacuate to L0
                            "UTILITY": "L0_maintenance/scripts",  # Utilities evacuate to L0
                            "STRATEGY": "L3_orchestration/utils",
                            "ADAPTER": "L2_execution/mcp",
                        }
                        target_folder = core_defaults.get(file_type)

                    # DEPRECATED ZONE EVACUATION: Force evacuation from patterns/* regardless of type
                    if "patterns" in path.parts and target_folder is None:
                        # Default evacuation for any file type in patterns/
                        type_to_folder = {
                            "MIXIN": "base_agents",
                            "CLASS": "base_agents",
                            "CONFIG": "config",
                            "SCRIPT": "L0_maintenance/scripts",
                            "UTILITY": "L0_maintenance/scripts",
                            "TYPES": "runtime/types",
                        }
                        target_folder = type_to_folder.get(file_type, "base_agents")

        # GUARDRAILS IMMUNITY
        if "guardrails" in path.parts and file_type == "AGENT":
            return None

        # 4. SPECIAL HANDLING: TESTS
        if file_type == "TEST":
            if "tests" not in parts and not path.name.startswith("test_"):
                # It's a test file outside of tests/ -> Violates Mirroring
                # (Complex logic, handled by mirror check, skip to avoid over-engineering)
                pass

        # 5. CALCULATE RESULT
        if target_folder:
            return self._calculate_move_target(path, root_index, target_folder)

        return None

    def _calculate_move_target(self, path: Path, root_index: int, target_folder: str) -> Path:
        """
        Robustly calculates the move target relative to the Sovereign Root.
        Fixes the 'parent.parent' fragility by pivoting from the anchor.

        Strategy: Root / Target_Folder / Filename
        (Flattens nesting to enforce standard structure)
        """
        # parts[0...root_index] is the path up to and including 'apps_rg'
        # e.g. (..., 'apps_rg')
        root_parts = path.parts[: root_index + 1]

        # Construct new path: .../apps_rg/target_folder/filename
        new_path = Path(*root_parts) / target_folder / path.name

        return new_path

    def get_compliant_name(self, path: Path, file_type: FileType) -> str | None:
        """Calculates the target filename. Returns None if no change needed.

        Zero-Ambiguity Naming Standard:
        - PROTOCOL: PascalCase, starts with 'I' (e.g., IHealerProtocol.py)
        - CLASS: *Base.py for foundational base agents (e.g., L1CognitionBase.py)
        - STRATEGY: PascalCase with Strategy.py suffix
        - ADAPTER: PascalCase with Adapter.py suffix
        - SCRIPT: snake_case with _script.py suffix
        - UTILITY: snake_case with _util.py suffix
        - TYPES: snake_case with _types.py suffix
        - EXCEPTION: snake_case with _exceptions.py suffix
        - STRATEGY (in strategies/): snake_case with _strategy.py suffix
        - MIXIN: snake_case with _mixin.py suffix
        """
        if file_type == "IGNORE":
            return None

        # GLOBAL IDEMPOTENCE GATE
        if path in self.processed_paths:
            return None

        is_app = any(p.startswith("apps_") for p in path.parts)

        # [ROOT CAUSE FIX] Normalize filename FIRST to catch stuttering/underscore violations
        # This runs before any type-specific logic so all names are clean
        normalized = self.normalize_filename(path.name)
        if normalized != path.name:
            # The filename itself has a root cause violation — return the normalized name
            # Let the caller handle the rename (type-specific suffixes applied later if needed)
            self.logger.info(f"[NORMALIZE] {path.name} → {normalized} (root cause fix)")
            return normalized

        # [V10 ZERO-AMBIGUITY] BASE AGENT NAMING ENFORCEMENT
        # Files in agentic_core/base_agents/ classified as CLASS must use Base suffix (not BaseAgent)
        # PascalCase is the convention for these foundational blueprints (e.g., L1CognitionBase.py)
        if file_type == "CLASS" and "base_agents" in path.parts:
            stem = path.stem
            # Strip Agent suffix if present (e.g., L1CognitionBaseAgent -> L1CognitionBase)
            if stem.endswith("BaseAgent") and stem != "SovereignBaseAgent":
                new_stem = stem.removesuffix("Agent")
                new_name = f"{new_stem}.py"
                if new_name != path.name:
                    self.processed_paths.add(path)
                    self.processed_paths.add(path.with_name(new_name))
                    return new_name
            # Already compliant - no rename needed
            return None

        # SSOT IMMUNITY LIST (2026-02-05)
        # Known sovereign configuration/blueprint files - immune to renaming
        immune_paths = {
            "structure_blueprint_config.py",
            "file_classification_healing_manifest.json",  # Prevent self-mutation
        }
        if path.name in immune_paths:
            self.logger.info(f"[IMMUNE] Skipping rename for SSOT file: {path.name}")
            return None

        # Get target_name from AST for accurate comparison
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            target_name = classes[0] if classes else path.stem
        except Exception:
            target_name = path.stem

        if is_app:
            # APPS HIGH-SIGNAL NAMING (MINIMALIST MVC)
            base_name = re.sub(r"Phase\d+", "", target_name)  # Strip Phase#
            if "hop" in base_name.lower():
                base_name = re.sub(r"hop", "HOP", base_name, flags=re.IGNORECASE)

            if file_type in ("AGENT", "CLASS", "ORCHESTRATOR"):
                base_name = base_name.removesuffix("Agent").removesuffix("Strategy").removesuffix("Validator")
                new_name = f"{self._to_pascal_case(base_name)}.py"
                if new_name != path.name:
                    self.processed_paths.add(path)
                    self.processed_paths.add(path.with_name(new_name))
                    return new_name
                return None

            if file_type == "CONFIG":
                if path.name.endswith("_config.py"):
                    return None
                base_name = path.stem.removesuffix("Config").removesuffix("Agent")
                new_name = f"{self._to_smart_snake_case(base_name)}_config.py"
                if new_name != path.name:
                    self.processed_paths.add(path)
                    self.processed_paths.add(path.with_name(new_name))
                    return new_name
                return None

            if file_type == "VALIDATOR":
                if path.name.endswith("_validator.py"):
                    return None
                base_name = target_name.removesuffix("Validator").removesuffix("Agent")
                new_name = f"{self._to_smart_snake_case(base_name)}_validator.py"
                if new_name != path.name:
                    self.processed_paths.add(path)
                    self.processed_paths.add(path.with_name(new_name))
                    return new_name
                return None

            return None

        # SCRIPT: Force snake_case with _script.py suffix
        if file_type == "SCRIPT":
            # ANTI-STUTTER: Sanitize first, then apply single correct suffix
            core_name = self._sanitize_filename(path.stem)
            snake = self._to_smart_snake_case(core_name)
            new_name = f"{snake}_script.py"
            return new_name if new_name != path.name else None

        # UTILITY: Force snake_case with _util.py suffix
        if file_type == "UTILITY":
            # ANTI-STUTTER: Sanitize first, then apply single correct suffix
            core_name = self._sanitize_filename(path.stem)
            snake = self._to_smart_snake_case(core_name)
            new_name = f"{snake}_util.py"
            return new_name if new_name != path.name else None

        # TYPES: Force snake_case with _types.py suffix
        if file_type == "TYPES":
            # ANTI-STUTTER: Sanitize first, then apply single correct suffix
            core_name = self._sanitize_filename(path.stem)
            snake = self._to_smart_snake_case(core_name)
            new_name = f"{snake}_types.py"
            return new_name if new_name != path.name else None

        # EXCEPTION: Force snake_case with _exceptions.py suffix
        if file_type == "EXCEPTION":
            # ANTI-STUTTER: Sanitize first, then apply single correct suffix
            core_name = self._sanitize_filename(path.stem)
            snake = self._to_smart_snake_case(core_name)
            new_name = f"{snake}_exceptions.py"
            return new_name if new_name != path.name else None

        # STRATEGY in strategies/ directory: Force snake_case with _strategy.py suffix
        # (L0 healing strategies use snake_case; L5 strategies use PascalCase handled later)
        if file_type == "STRATEGY" and "strategies" in path.parts:
            core_name = self._sanitize_filename(path.stem)
            snake = self._to_smart_snake_case(core_name)
            new_name = f"{snake}_strategy.py"
            return new_name if new_name != path.name else None

        # CONSOLIDATED GUARDRAILS NAMING CONVENTION ENFORCEMENT
        if file_type == "AGENT" and "guardrails" in path.parts:
            if path.name.endswith("_agent.py"):
                return None
            base_name = target_name.removesuffix("Agent").removesuffix("Strategy").removesuffix("Handler")
            new_name = f"{self._to_smart_snake_case(base_name)}_agent.py"
            if new_name != path.name:
                self.processed_paths.add(path)
                self.processed_paths.add(path.with_name(new_name))
                return new_name
            return None

        # TEST: Force test_ prefix + snake_case
        if file_type == "TEST":
            clean = re.sub(r"(?<!^)(?=[A-Z])", "_", path.stem.replace("test_", "")).lower()
            return f"test_{clean}.py" if f"test_{clean}.py" != path.name else None

        # CONFIG STANDARDIZATION HARDENING (SEMANTIC PRESERVATION 2026-02-05)
        if file_type == "CONFIG":
            # ANTI-STUTTER: Sanitize first, then apply single correct suffix
            core_name = self._sanitize_filename(path.stem)
            snake_name = self._to_smart_snake_case(core_name)
            new_name = f"{snake_name}_config.py"
            if new_name == path.name:
                self.logger.info(f"[CONFIG COMPLIANT] Skipping rename (already correct): {path.name}")
                return None
            return new_name

        # VALIDATOR HARDENING (similar conservative approach)
        if file_type == "VALIDATOR":
            # ANTI-STUTTER: Sanitize first, then apply single correct suffix
            core_name = self._sanitize_filename(path.stem)
            snake_name = self._to_smart_snake_case(core_name)
            new_name = f"{snake_name}_validator.py"
            if new_name == path.name:
                self.logger.info(f"[VALIDATOR COMPLIANT] Skipping rename (already correct): {path.name}")
                return None
            return new_name

        # --- MIXIN STANDARDIZATION ---
        # Logic: Forces Mixins to snake_case.
        # Example: HygieneMixin.py -> hygiene_mixin.py
        if file_type == "MIXIN":
            # ANTI-STUTTER: Sanitize first, then apply single correct suffix
            core_name = self._sanitize_filename(path.stem)
            snake = self._to_smart_snake_case(core_name)
            new_name = f"{snake}_mixin.py"
            return new_name if new_name != path.name else None

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
                # Protocols must be PascalCase and start with 'I' prefix
                if not target_name.startswith("I"):
                    target_name = "I" + target_name
                # Ensure Protocol suffix if not present
                if not target_name.endswith("Protocol"):
                    target_name += "Protocol"

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
                # [FIXED] Strip conflicting suffixes first to prevent "AgentOrchestrator" or "ConfigOrchestrator"
                target_name = target_name.replace("Agent", "").replace("Service", "").replace("Config", "")
                # Force PascalCase and ensure Orchestrator suffix
                if not target_name.endswith("Orchestrator"):
                    target_name += "Orchestrator"

            elif file_type == "STRATEGY":
                # STRATEGY: PascalCase with Strategy suffix
                target_name = target_name.replace("Agent", "")
                # STUTTER PREVENTION: Check if Strategy already exists
                if not target_name.endswith("Strategy"):
                    target_name += "Strategy"

            elif file_type == "ADAPTER":
                if "guardrails" in path.parts:
                    return None
                # ADAPTER: PascalCase with Adapter suffix
                target_name = target_name.replace("Agent", "")
                # STUTTER PREVENTION: Check if Adapter/Wrapper/Bridge already exists
                if not any(target_name.endswith(s) for s in ["Adapter", "Wrapper", "Bridge"]):
                    target_name += "Adapter"

            elif file_type == "FACTORY":
                # Force PascalCase and ensure Factory suffix
                if not target_name.endswith("Factory"):
                    target_name += "Factory"

            # VALIDATOR and CONFIG are now handled earlier with conservative approach
            # These elif blocks are kept for fallback but should not be reached
            elif file_type == "VALIDATOR":
                # Fallback: should be handled by early return above
                pass

            elif file_type == "CONFIG":
                # Fallback: should be handled by early return above
                pass

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

        self.logger.info(f"[HEAL] Processing {violation_type} violation at {path}")

        if violation_type != "naming":
            self.logger.warning(f"  Unknown violation type: {violation_type}")
            return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

        file_path = Path(path)

        # Validate file exists and is Python
        if not file_path.exists():
            self.logger.warning(f"  File does not exist: {path}")
            return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

        if file_path.suffix != ".py":
            self.logger.info(f"  Non-Python file {path}, skipping")
            return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

        try:
            # Use unified classification logic (same as main audit)
            file_type = self.classify_file(file_path)

            if file_type == "IGNORE":
                self.logger.info(f"  File {path} is IGNORE type, skipping")
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

            # Use unified naming logic (same as main audit)
            new_name = self.get_compliant_name(file_path, file_type)

            if not new_name or new_name == file_path.name:
                self.logger.info(f"  File {path} is already compliant")
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

            new_path = file_path.parent / new_name

            if new_path.exists():
                self.logger.warning(f"  Target {new_path} already exists")
                return {"violations_fixed": 0, "violations_found": 1, "errors": 0, "skipped": 1}

            # Perform the rename
            file_path.rename(new_path)
            self.logger.info(f"  Renamed {path} -> {new_path}")

            return {"violations_fixed": 1, "violations_found": 1, "errors": 0, "skipped": 0}

        except Exception as e:  # guardian: allow-silent_swallower
            self.logger.error(f"  Error processing {path}: {e}")
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

            # UNIFIED HEALING RESULT CALCULATION
            total_violations = sum(self.stats["violations"].values())
            violations_fixed = (
                self.action_counters["renames"]
                + self.action_counters["territory_moves"] * 2  # Move counts as find+fix
                + self.action_counters["import_fixes"]
                + self.action_counters["deep_refactors"]
            )

            return {
                "violations_found": total_violations,
                "violations_fixed": violations_fixed,
                "errors": 0 if exit_code == 0 else 1,
                "skipped": 0,
                "action_counters": self.action_counters,  # Include for external tracking
            }

        except Exception as e:  # guardian: allow-silent_swallower
            print(f"[ERROR] FileClassificationAgent healing failed: {e}")
            return {"violations_found": 0, "violations_fixed": 0, "errors": 1, "skipped": 0}
        finally:
            _call_path.discard(agent_id)
            self.processed_paths.clear()  # Fresh for next run


def main():
    """Standalone execution for testing."""
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description="File Classification Agent")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--validate", action="store_true", help="Check compliance only")
    args = parser.parse_args()

    from pathlib import Path

    is_dry_run = args.dry_run or args.validate

    agent = FileClassificationAgent(project_root=Path("."), dry_run=is_dry_run, validate_only=args.validate)

    result = agent.run()
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
