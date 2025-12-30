"""
KeyMappingAgent: Canon Key Applicability Resolver (Key 0-19 territory)

Determines which Canon Keys apply to a given file based on its sovereign location.
- Territorial keys (0-12): Strict folder prefix matching
- Behavioral keys (13-19): Wildcard '*' → apply globally unless excluded

Replaces logic from void_compliance.py:
  - get_applicable_keys_for_file()

Placed in L5_safety/validators alongside other canon validators
(LocationAgent, HierarchyAgent) per semantic_l2_registry purpose.
"""
from pathlib import Path
from typing import Set, Dict, List

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    CANON_KEY_TO_FOLDER_MAP,  # SSOT: {key_num: [folder_patterns]}
)


class key_mapping_agent:
    """
    Autonomous lightweight agent for Canon Key resolution.
    Used by orchestrators, healers, and auditors to know which keys govern a file.
    """

    BEHAVIORAL_KEY_START = 13  # Keys 13-19 are global (* wildcard)
    BEHAVIORAL_KEY_END = 19

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.key_to_folder_map = CANON_KEY_TO_FOLDER_MAP

    def get_applicable_keys_for_file(
        self,
        file_path: Path,
        include_behavioral: bool = True
    ) -> Set[int]:
        """
        Resolve applicable Canon Keys for a file.

        Args:
            file_path: Absolute path to the file
            include_behavioral: If False, exclude global keys 13-19

        Returns:
            Set of applicable key numbers (int)

        Logic:
        - Convert to relative path string (forward slashes)
        - For each key, check if any folder pattern matches prefix or is '*'
        - Behavioral keys (13-19) use '*' → apply to all files unless filtered
        """
        try:
            rel_path = file_path.relative_to(self.project_root)
            rel_path_str = str(rel_path).replace("\\", "/")
        except ValueError:
            # File outside project root → no keys apply
            return set()

        applicable_keys: Set[int] = set()

        for key_num, folder_patterns in self.key_to_folder_map.items():
            if key_num < self.BEHAVIORAL_KEY_START or key_num > self.BEHAVIORAL_KEY_END:
                # Territorial keys (0-12): require exact prefix match
                for pattern in folder_patterns:
                    if pattern == "*" or rel_path_str.startswith(pattern + "/") or rel_path_str == pattern:
                        applicable_keys.add(key_num)
                        break
            else:
                # Behavioral keys (13-19): wildcard '*' → always apply if not excluded
                if include_behavioral and any(pattern == "*" for pattern in folder_patterns):
                    applicable_keys.add(key_num)

        return applicable_keys

    def get_territorial_keys(self, file_path: Path) -> Set[int]:
        """Convenience: Only territorial keys (0-12)"""
        return self.get_applicable_keys_for_file(file_path, include_behavioral=False)

    def get_behavioral_keys(self, file_path: Path) -> Set[int]:
        """Convenience: Only behavioral keys (13-19)"""
        all_keys = self.get_applicable_keys_for_file(file_path, include_behavioral=True)
        return {
            k for k in all_keys
            if self.BEHAVIORAL_KEY_START <= k <= self.BEHAVIORAL_KEY_END
        }

    def run_on_files(self, files: List[Path]) -> Dict[Path, Set[int]]:
        """
        Batch resolve keys for multiple files.
        Useful for orchestrator pre-processing.
        """
        return {
            file_path: self.get_applicable_keys_for_file(file_path)
            for file_path in files
        }

    def run(self) -> List[Dict]:
        """
        Execute agent on all Python files in project.
        Required for ComplianceOrchestrator discovery.
        """
        results = []
        for py_file in self.project_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            keys = self.get_applicable_keys_for_file(py_file)
            if keys:
                results.append({"file": str(py_file), "keys": list(keys)})
        return results


# Uppercase alias for backward compatibility
KeyMappingAgent = key_mapping_agent
