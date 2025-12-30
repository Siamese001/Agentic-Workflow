"""
FileSystemAgent: Sovereign Non-Python File Naming Enforcer

Enforces naming laws on all files (not just .py):
- No repeated suffixes (.archived.archived...)
- No generic/versioned names (v1, copy_of, etc.)
- High-signal enforcement for configuration assets

Placed in L5_safety/validators per SSOT extension:
  "Enforcement of physical territory cleanliness and non-code asset naming."

Depth: agentic_core/L5_safety/validators/filesystem_agent.py -> 4 parts -> compliant
"""
import re
import os
from pathlib import Path
from typing import List, Tuple

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    FORBIDDEN_PATTERNS,
    SOVEREIGN_EXCLUDED_FOLDERS
)


class filesystem_agent:
    """
    Autonomous agent for physical filesystem purity.
    Targets technical debt markers in non-Python files.
    """
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.forbidden_patterns = FORBIDDEN_PATTERNS
        # REGEX: Catches repeated markers like .archived.archived or .old.old
        self.repeated_suffix = re.compile(r"\.(archived|backup|old|copy)+\.?\1", re.IGNORECASE)

    def run(self) -> List[Tuple[Path, str]]:
        """
        Scan project root for naming violations in non-Python files.
        """
        violations: List[Tuple[Path, str]] = []
        
        # Performance: Use os.walk with exclusion to avoid deep venv/git scans
        for root, dirs, files in os.walk(self.project_root):
            # Prune protected territories
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS and not d.startswith('.')]
            
            for name in files:
                file_path = Path(root) / name
                
                # Skip Python files (handled by specialized NamingAgent)
                if file_path.suffix == ".py":
                    continue

                # 1. Check for Repeated Suffixes (Technical Clutter)
                if self.repeated_suffix.search(name):
                    violations.append((file_path, f"NAMING VIOLATION: Repeated technical suffix: {name}"))
                    continue

                # 2. Check for Forbidden Patterns (Generic/Versioned)
                for pattern in self.forbidden_patterns:
                    if pattern.match(name):
                        violations.append((file_path, f"NAMING VIOLATION: Forbidden generic pattern: {name}"))
                        break

        return violations


# Uppercase alias for backward compatibility
FileSystemAgent = filesystem_agent
