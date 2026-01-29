from __future__ import annotations

"""
DDDAlignmentAgent - Domain-Driven Design Bounded Context Enforcement

PURPOSE: Enforces DDD bounded context boundaries to prevent cross-context
coupling that undermines the L0-L6 sovereign layer architecture.

KEYS: Architectural integrity, bounded contexts, aggregate roots
TIER: 2 (Architectural) - runs after structural validation

LOCATION: agentic_core/L5_safety/validators/ (SSOT-compliant)
"""


import ast
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.timeout_decorator import timeout

try:
    from agentic_core.L2_execution.mcp.mcp_hardened_mixin import mcp_hardened_mixin
except ImportError:

    class MCPHardenedMixin:
        pass


try:
    from agentic_core.base_agents.subatomic_testing_mixin import subatomic_testing_mixin
except ImportError:

    class SubatomicTestingMixin:
        pass


# [SSOT IMPORT] Structure blueprint is the single source of truth
try:
    from agentic_core.L5_safety.validators.structure_blueprint import (
        CORE_SUBFOLDER_MAP,
        SOVEREIGN_REGISTRY,
    )
except ImportError:
    pass

# DDD Bounded Contexts - derived from sovereign layer hierarchy
BOUNDED_CONTEXTS: dict[str, dict[str, Any]] = {
    "L0_Governance": {
        "path": "agentic_core/L0_maintenance",
        "rank": 0,
        "role": "Metacognition: The Law, Auditors, and Healers",
    },
    "L1_Cognition": {
        "path": "agentic_core/L1_cognition",
        "rank": 1,
        "role": "Strategic Reasoning: Planning and Consensus",
    },
    "L2_Execution": {
        "path": "agentic_core/L2_execution",
        "rank": 2,
        "role": "Action: Tool Implementation and Agent Realization",
    },
    "L3_Orchestration": {
        "path": "agentic_core/L3_orchestration",
        "rank": 3,
        "role": "Workflow: Task Fission and Fusion",
    },
    "L4_State": {
        "path": "agentic_core/L4_state",
        "rank": 4,
        "role": "Memory: Persistence and Semantic Caching",
    },
    "L5_Safety": {
        "path": "agentic_core/L5_safety",
        "rank": 5,
        "role": "Membrane: Input/Output Sanitization",
    },
    "L6_Observability": {
        "path": "agentic_core/L6_observability",
        "rank": 6,
        "role": "Truth: Telemetry, Logging, and Audit Trails",
    },
    "SharedContracts": {
        "path": "apps_shared/base_agents",
        "rank": -1,  # Neutral layer, no rank in hierarchy
        "role": "Neutral Interfaces: Cross-context contracts",
    },
}

# Standard library modules (exempt from DDD checks)
STDLIB_MODULES = frozenset(
    {
        "pathlib",
        "os",
        "sys",
        "json",
        "logging",
        "typing",
        "datetime",
        "collections",
        "itertools",
        "functools",
        "re",
        "asyncio",
        "abc",
        "dataclasses",
        "enum",
        "copy",
        "io",
        "time",
        "uuid",
        "hashlib",
        "ast",
        "inspect",
        "importlib",
        "warnings",
        "contextlib",
        "shutil",
        "tempfile",
        "traceback",
        "threading",
        "multiprocessing",
        "subprocess",
        "socket",
        "http",
        "urllib",
        "email",
        "html",
        "xml",
        "csv",
        "pickle",
        "struct",
        "codecs",
        "base64",
        "binascii",
        "zlib",
        "gzip",
        "bz2",
        "lzma",
        "zipfile",
        "tarfile",
        "configparser",
        "argparse",
        "getopt",
        "textwrap",
        "difflib",
        "string",
        "unicodedata",
        "locale",
        "gettext",
        "math",
        "cmath",
        "decimal",
        "fractions",
        "random",
        "statistics",
        "secrets",
        "operator",
        "heapq",
        "bisect",
        "array",
        "weakref",
        "types",
        "pprint",
        "reprlib",
        "graphlib",
        "fnmatch",
        "glob",
        "linecache",
        "tokenize",
        "keyword",
        "symbol",
        "token",
        "dis",
        "builtins",
        "__future__",
        "gc",
        "atexit",
        "signal",
        "errno",
        "ctypes",
        "platform",
        "sysconfig",
        "site",
        "code",
        "codeop",
    }
)

# Allowed cross-context import patterns
ALLOWED_CROSS_CONTEXT_PATTERNS = frozenset(
    {
        "contracts",
        "interfaces",
        "protocols",
        "base_agents",
        "mixins",
    }
)

Logger = logging.getLogger(__name__)


@dataclass
class DDDViolation:
    """Structured DDD violation for reporting."""

    file_path: Path
    source_context: str
    target_context: str
    imported_module: str
    line_number: int
    severity: int = 5  # Medium severity by default

    def __str__(self) -> str:
        return (
            f"DDD Violation in {self.file_path.name}:{self.line_number} - "
            f"Context '{self.source_context}' imports from '{self.target_context}' "
            f"via '{self.imported_module}'"
        )


@dataclass
class DDDAlignmentAgent(SovereignBaseAgent):
    """
    Domain-Driven Design Alignment Agent.

    Enforces bounded context boundaries to prevent cross-context coupling.

    DETECTION:
    - Scans all Python files for imports
    - Identifies the bounded context of each file
    - Detects imports from other bounded contexts
    - Allows imports from SharedContracts and interface modules

    HEALING:
    - Reports violations (no auto-fix - requires manual refactoring)
    - Suggests using dependency inversion via interfaces

    KEYS: Architectural integrity, DDD, bounded contexts
    """

    project_root: Path = None

    def __post_init__(self):
        if self.project_root is None:
            self.project_root = Path.cwd()
        else:
            self.project_root = Path(self.project_root).resolve()

        self.violations: list[DDDViolation] = []
        self._skip_patterns = {"tests", "archives", "__pycache__", ".git", "venv", ".venv"}

    def _get_file_context(self, filepath: Path) -> str | None:
        """Determine which bounded context a file belongs to."""
        file_str = str(filepath).replace("\\", "/")

        for ctx_name, ctx_info in BOUNDED_CONTEXTS.items():
            ctx_path = ctx_info.get("path", "")
            if ctx_path and ctx_path in file_str:
                return ctx_name

        return None

    def _is_allowed_import(self, module: str, source_context: str) -> bool:
        """Check if an import is allowed (stdlib, same context, or interface)."""
        if not module:
            return True

        # Check if it's a stdlib module
        module_root = module.split(".")[0]
        if module_root in STDLIB_MODULES:
            return True

        # Check if it's an allowed cross-context pattern
        for pattern in ALLOWED_CROSS_CONTEXT_PATTERNS:
            if pattern in module:
                return True

        return False

    def _check_file_imports(self, filepath: Path) -> list[DDDViolation]:
        """Check a single file for DDD violations."""
        violations = []

        source_context = self._get_file_context(filepath)
        if not source_context:
            return violations  # File not in a bounded context

        try:
            content = filepath.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError) as e:
            Logger.debug(f"Could not parse {filepath}: {e}")
            return violations

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                module = node.module

                # Skip allowed imports
                if self._is_allowed_import(module, source_context):
                    continue

                # Check if importing from another bounded context
                for ctx_name, ctx_info in BOUNDED_CONTEXTS.items():
                    if ctx_name == source_context:
                        continue
                    if ctx_name == "SharedContracts":
                        continue  # Always allowed

                    ctx_path = ctx_info.get("path", "").replace("/", ".")
                    if ctx_path and ctx_path in module:
                        violations.append(
                            DDDViolation(
                                file_path=filepath,
                                source_context=source_context,
                                target_context=ctx_name,
                                imported_module=module,
                                line_number=node.lineno,
                            )
                        )

        return violations

    def _should_skip_path(self, path: Path) -> bool:
        """Check if a path should be skipped."""
        path_str = str(path)
        return any(skip in path_str for skip in self._skip_patterns)

    def run(self, target_dir: Path = None) -> list[DDDViolation]:
        """
        Scan for DDD bounded context violations.

        Args:
            target_dir: Directory to scan (defaults to project_root)

        Returns:
            List of DDDViolation objects
        """
        target = target_dir or self.project_root
        self.violations = []

        Logger.info(f"[DDDAlignmentAgent] Scanning for bounded context violations in {target}")

        # Use ssot_discovery for consistent file discovery
        try:
            from agentic_core.utils.ssot_discovery import get_python_files

            python_files = list(get_python_files(target))
        except ImportError:
            python_files = list(target.rglob("*.py"))

        files_checked = 0
        for filepath in python_files:
            if self._should_skip_path(filepath):
                continue

            files_checked += 1
            file_violations = self._check_file_imports(filepath)
            self.violations.extend(file_violations)

        Logger.info(
            f"[DDDAlignmentAgent] Checked {files_checked} files, "
            f"found {len(self.violations)} violations"
        )

        return self.violations

    def get_alignment_score(self) -> float:
        """Calculate DDD alignment score (0-100)."""
        if not self.violations:
            return 100.0

        # Deduct 2 points per violation, minimum 0
        score = max(0.0, 100.0 - len(self.violations) * 2)
        return score

    def get_violation_summary(self) -> dict[str, Any]:
        """Get summary of violations by context pair."""
        summary: dict[str, int] = {}

        for v in self.violations:
            key = f"{v.source_context} -> {v.target_context}"
            summary[key] = summary.get(key, 0) + 1

        return {
            "total_violations": len(self.violations),
            "alignment_score": self.get_alignment_score(),
            "violations_by_context_pair": summary,
        }

    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, Any]:
        """
        Autonomous DDD alignment enforcement (Canon Key 51 compliance).

        NOTE: DDD violations cannot be auto-healed - they require manual
        refactoring to use dependency inversion via interfaces.

        Args:
            dry_run: If True, only report violations
            execute: If True, would apply fixes (not applicable for DDD)

        Returns:
            Dict with violation counts and recommendations
        """
        if _call_path is None:
            _call_path = set()

        agent_name = self.__class__.__name__

        # Cycle detection
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}

        _call_path.add(agent_name)

        try:
            # Run parent chain
            try:
                super().heal_repository(dry_run=dry_run)
            except Exception as e:
                Logger.debug(f"Parent chain warning: {e}")

            # Scan for violations
            violations = self.run()

            result = {
                "violations_found": len(violations),
                "fixed": 0,  # DDD violations require manual refactoring
                "errors": 0,
                "alignment_score": self.get_alignment_score(),
                "summary": self.get_violation_summary(),
            }

            # Report violations
            if violations:
                print(f"\n[DDDAlignmentAgent] Found {len(violations)} bounded context violations:")
                for v in violations[:10]:  # Show first 10
                    print(f"   [!] {v}")
                if len(violations) > 10:
                    print(f"   ... and {len(violations) - 10} more")
                print("\n   RECOMMENDATION: Use dependency inversion via interfaces/contracts")
                print("   to decouple bounded contexts. Import from 'contracts' or 'interfaces'")
                print("   modules instead of directly importing implementation classes.")
            else:
                print("   [OK] DDD Alignment: 100% - No bounded context violations")

            return result

        finally:
            _call_path.discard(agent_name)


def validate_ddd_alignment(target_dir: str) -> tuple[float, list[str]]:
    """
    Convenience function for DDD validation.

    Args:
        target_dir: Directory to validate

    Returns:
        Tuple of (alignment_score, list of violation messages)
    """
    agent = DDDAlignmentAgent(project_root=Path(target_dir))
    violations = agent.run()

    messages = [str(v) for v in violations]
    return (agent.get_alignment_score(), messages)


if __name__ == "__main__":
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    agent = DDDAlignmentAgent(project_root=target)
    result = agent.heal_repository(dry_run=True)

    print(f"\nAlignment Score: {result['alignment_score']:.1f}%")
    print(f"Violations: {result['violations_found']}")
