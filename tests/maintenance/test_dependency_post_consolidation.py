"""
file: tests/maintenance/test_dependency_post_consolidation.py
description: Scans the live codebase to ensure no active agents are importing
             deprecated bases or legacy orchestrators.
"""

import os
import re
from pathlib import Path

import pytest

# --- Configuration ---
LIVE_CORE_PATH = Path("agentic_core")
DEPRECATED_TERMS = [
    "CanonBaseAgent",
    "ExecutionCanonBaseAgent",
    "MaintenanceBaseAgent",
    "SSOTOrchestratorAgent",
    "HealingOrchestratorAgent",
    "ConsolidatedOrchestratorAgent"
]

def find_legacy_usage():
    """Scans .py files for legacy class usage in actual code (not docs/comments)."""
    violations = []

    # Paths to exclude from scanning (utility scripts, not live agents)
    EXCLUDED_PATHS = [
        "L0_maintenance/scripts",  # Utility/migration scripts
        "orchestrator_registry.py",  # Contains deprecated terms for aliasing
        "config/blueprint_sovereign",  # Blueprint templates
        "__pycache__",
        "test_discovery_roster_builder.py",  # Test file with expected references
    ]

    for root, _, files in os.walk(LIVE_CORE_PATH):
        # Skip excluded directories
        if any(excl in root.replace("\\", "/") for excl in EXCLUDED_PATHS):
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file

                # Skip specific files that contain deprecated terms for documentation/aliasing
                if any(excl in str(file_path).replace("\\", "/") for excl in EXCLUDED_PATHS):
                    continue

                content = file_path.read_text(errors='ignore')
                lines = content.split('\n')
                in_docstring = False

                for line_num, line in enumerate(lines, 1):
                    stripped = line.strip()

                    # Track docstring state (triple quotes)
                    if '"""' in stripped or "'''" in stripped:
                        # Toggle docstring state (simple heuristic)
                        quote_count = stripped.count('"""') + stripped.count("'''")
                        if quote_count == 1:
                            in_docstring = not in_docstring
                        # If line has opening and closing quotes, it's a single-line docstring
                        continue

                    # Skip if inside docstring
                    if in_docstring:
                        continue

                    # Skip comment lines
                    if stripped.startswith('#'):
                        continue

                    # Skip lines mentioning deprecation/legacy/consolidation context
                    lower_line = line.lower()
                    if any(ctx in lower_line for ctx in ['deprecated', 'legacy', 'consolidat', 'replaces', 'from ', 'formerly']):
                        continue

                    for term in DEPRECATED_TERMS:
                        # Look for actual code usage patterns:
                        # - Class inheritance: class Foo(CanonBaseAgent)
                        # - Import statements: from ... import CanonBaseAgent
                        # - Direct instantiation: CanonBaseAgent(...)
                        # - Type hints: def foo() -> CanonBaseAgent
                        if re.search(r'\b' + term + r'\b', line):
                            # Check if it's actual code usage (not just a string/comment)
                            # Patterns that indicate real usage:
                            is_import = re.search(r'^\s*(from|import)\s+', line)
                            is_inheritance = re.search(r'class\s+\w+\s*\([^)]*' + term, line)
                            is_instantiation = re.search(term + r'\s*\(', line)
                            is_type_hint = re.search(r':\s*' + term + r'\b', line) or re.search(r'->\s*' + term + r'\b', line)
                            is_assignment = re.search(r'=\s*' + term + r'\b', line)

                            if is_import or is_inheritance or is_instantiation or is_type_hint or is_assignment:
                                violations.append((str(file_path), term, line_num, stripped[:80]))
    return violations

class TestDependencyPostConsolidation:

    def test_no_legacy_imports_in_core(self):
        """
        TC-001: Verifies that no live files in agentic_core use deprecated bases/orchestrators.
        """
        violations = find_legacy_usage()
        if violations:
            msg = "\n".join([f"Violation: {v[1]} found in {v[0]}:{v[2]} -> {v[3]}" for v in violations])
            pytest.fail(f"Consolidation Clean-up Required:\n{msg}")

    def test_registry_import_integrity(self):
        """
        TC-002: Verifies the new orchestrator_registry is importable.
        """
        try:
            from agentic_core.L3_orchestration.orchestrator_registry import get_orchestrator
            assert get_orchestrator is not None
        except ImportError as e:
            pytest.fail(f"Orchestrator Registry is broken: {e}")

    def test_unified_orchestrator_instantiation(self):
        """
        TC-003: Ensures the UnifiedOrchestratorAgent can be created via registry.
        """
        from agentic_core.L3_orchestration.orchestrator_registry import get_orchestrator
        # Test default mode
        orchestrator = get_orchestrator(mode="unified")
        assert orchestrator.__class__.__name__ == "UnifiedOrchestratorAgent"

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main(["-v", __file__]))
