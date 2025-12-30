"""
HierarchyAgent: Canon Structural Hierarchy Enforcer (Key 3/12/41 territory)

Enforces:
- Exact canonical L1/L2 folder structure (no drift)
- Span-of-Two rule: no redundant tunnel directories (single meaningful child folder)
- Exact file depth 4 in agentic_core (root/L1/L2/file.py)
- No Python files directly under sovereign roots or L1 layers (Key 41)

Replaces logic from void_compliance.py:
  - check_span_of_two_violation()
  - check_span_of_two_violations()
  - validate_canonical_hierarchy()

Placed in L5_safety/validators per semantic_l2_registry:
  "Canon constitution validators, structural policy enforcement..."
"""
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import os
import hashlib
import json

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
    AUTONOMOUS_AGENT_WHITELIST,
    SOVEREIGN_EXCLUDED_FOLDERS,
    ROOT_WHITELIST,
)


class HierarchyAgent:
    """
    Autonomous agent for hierarchical structure compliance.
    Scans folders only (no file content parsing).
    Run after LocationAgent.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.excluded_folders = SOVEREIGN_EXCLUDED_FOLDERS

    def check_span_of_two_violation(self, folder_path: Path) -> Tuple[bool, str]:
        """
        Enforce Span-of-Two rule.
        Violation only if exactly one meaningful child AND it is a directory (redundant tunnel).
        Single-file leaves are explicitly allowed.
        """
        if not folder_path.is_dir():
            return True, ""

        meaningful_children = [
            child for child in folder_path.iterdir()
            if child.name not in self.excluded_folders
            and not child.name.startswith('.')
        ]

        if len(meaningful_children) == 1 and meaningful_children[0].is_dir():
            return False, f"SPAN-OF-TWO VIOLATION: Redundant tunnel '{folder_path.name}' → flatten into parent"

        return True, ""

    def check_span_of_two_violations(self) -> List[Tuple[Path, str]]:
        """Project-wide scan for Span-of-Two violations in sovereign territories."""
        violations: List[Tuple[Path, str]] = []

        for root_name in ROOT_WHITELIST:
            root_path = self.project_root / root_name
            if not root_path.exists():
                continue

            for dirpath, dirs, _ in os.walk(root_path):
                # Filter out excluded dirs in-place for walk efficiency
                dirs[:] = [d for d in dirs if d not in self.excluded_folders and not d.startswith('.')]

                current_dir = Path(dirpath)
                if current_dir.name in self.excluded_folders or current_dir.name.startswith('.'):
                    continue

                is_valid, msg = self.check_span_of_two_violation(current_dir)
                if not is_valid:
                    violations.append((current_dir, msg))

        return violations

    def validate_canonical_hierarchy(self) -> List[Tuple[Path, str]]:
        """
        Enforce canonical hierarchy from SOVEREIGN_REGISTRY and CORE_SUBFOLDER_MAP.
        Flags:
        - Unapproved L1 or L2 folders
        - Files at invalid depths (especially agentic_core strict depth 4)
        - Files directly under root (Key 41)
        """
        violations: List[Tuple[Path, str]] = []
        MAX_FILE_DEPTH_AGENTIC_CORE = 4  # root/L1/L2/file.py → len(parts) == 4

        # === AGENTIC_CORE: Strict depth 4 enforcement for all .py files ===
        if (self.project_root / "agentic_core").exists():
            py_files = list((self.project_root / "agentic_core").rglob("*.py"))
            for file_path in py_files:
                try:
                    rel_parts = file_path.relative_to(self.project_root).parts
                except ValueError:
                    continue

                # Skip excluded/hidden
                if any(p.startswith('.') or p in {"venv", "__pycache__"} for p in rel_parts):
                    continue

                if rel_parts[0] != "agentic_core":
                    continue

                # Skip __init__.py files - structural package markers at every level
                if file_path.name == "__init__.py":
                    continue

                depth = len(rel_parts)
                if depth > MAX_FILE_DEPTH_AGENTIC_CORE:
                    violations.append((
                        file_path,
                        f"DEEP VIOLATION (Key 12): {file_path.name} at depth {depth} (> {MAX_FILE_DEPTH_AGENTIC_CORE})"
                    ))
                elif depth < MAX_FILE_DEPTH_AGENTIC_CORE:
                    violations.append((
                        file_path,
                        f"SHALLOW VIOLATION (Key 41): {file_path.name} at depth {depth} (< {MAX_FILE_DEPTH_AGENTIC_CORE})"
                    ))

        # === CANONICAL L1/L2 DRIFT DETECTION ===
        for root_key, config in SOVEREIGN_REGISTRY.items():
            root_path = self.project_root / root_key
            if not root_path.exists():
                continue

            subfolders_config = config.get("subfolders", [])
            is_dict_config = isinstance(subfolders_config, dict)

            # No files directly under root (Key 41)
            root_py_files = [
                p.name for p in root_path.iterdir()
                if p.is_file() and p.suffix == ".py" and p.name != "__init__.py"
            ]
            if root_py_files:
                violations.append((
                    root_path,
                    f"DEPTH VIOLATION (Key 41): Files directly under root '{root_key}': {root_py_files}"
                ))

            # L1 drift
            expected_l1 = set(subfolders_config.keys() if is_dict_config else subfolders_config)
            actual_l1 = {
                p.name for p in root_path.iterdir()
                if p.is_dir() and not p.name.startswith('.') and p.name not in self.excluded_folders
            }
            unexpected_l1 = actual_l1 - expected_l1
            for bad in unexpected_l1:
                violations.append((
                    root_path / bad,
                    f"HIERARCHY DRIFT: Unapproved L1 folder '{bad}'. Allowed: {sorted(expected_l1)}"
                ))

            # L2 drift (only for agentic_core and structured apps)
            if root_key == "agentic_core":
                for l1_name in (subfolders_config if isinstance(subfolders_config, list) else subfolders_config.keys()):
                    l1_path = root_path / l1_name
                    if not l1_path.exists():
                        continue

                    expected_l2 = set(CORE_SUBFOLDER_MAP.get(l1_name, []))
                    actual_l2_dirs = {
                        p.name for p in l1_path.iterdir()
                        if p.is_dir() and not p.name.startswith('.') and p.name not in self.excluded_folders
                    }
                    unexpected_l2 = actual_l2_dirs - expected_l2
                    for bad in unexpected_l2:
                        violations.append((
                            l1_path / bad,
                            f"HIERARCHY DRIFT: Unapproved L2 folder '{bad}' under '{l1_name}'. Allowed: {sorted(expected_l2)}"
                        ))

        return violations

    def run(self) -> List[Tuple[Path, str]]:
        """
        Full hierarchy compliance scan.
        Returns combined list of all violations.
        """
        all_violations: List[Tuple[Path, str]] = []

        all_violations.extend(self.check_span_of_two_violations())
        all_violations.extend(self.validate_canonical_hierarchy())

        return all_violations


    # SUPPLEMENTED FROM SemanticTerritoryMapperAgent — embedding-based semantic mapping — merged 2025-12-30
    # Territory examples for semantic matching
    TERRITORY_EXAMPLES: Dict[str, str] = {
        'agentic_core/L1_cognition': 'strategy planning reasoning mission decomposition intent',
        'agentic_core/L3_orchestration': 'fission orchestration routing workflow manager coordinator',
        'agentic_core/L4_state': 'memory cache pinecone redis historian audit ledger',
        'agentic_core/L5_safety': 'guardrail safety policy enforcer filter validator healer',
        'agentic_core/L2_execution': 'tool agent executor registry runner',
    }

    async def semantic_territory_map(self, file_path: Path, redis_client: Any = None) -> Dict[str, Any]:
        """
        Map file to semantic territory using embeddings.
        Ported from SemanticTerritoryMapperAgent.map_file_to_territory() (lines 55-79).
        
        Args:
            file_path: Path to file to map
            redis_client: Optional Redis client for caching
            
        Returns:
            Dict with territory mapping results
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')[:5000]
        except Exception as e:
            return {
                "file": str(file_path),
                "error": f"Cannot read file: {e}",
                "suggested_territory": None,
            }
        
        # Infer current territory from path
        current_territory = self._infer_current_territory(file_path)
        
        # Calculate similarity scores against territory examples
        content_lower = content.lower()
        scores = {}
        
        for territory, keywords in self.TERRITORY_EXAMPLES.items():
            keyword_list = keywords.split()
            matches = sum(1 for kw in keyword_list if kw in content_lower)
            scores[territory] = matches / len(keyword_list) if keyword_list else 0
        
        # Find best match
        if scores:
            best_territory = max(scores, key=scores.get)
            best_score = scores[best_territory]
        else:
            best_territory = "unknown"
            best_score = 0.0
        
        return {
            "file": str(file_path),
            "current_territory": current_territory,
            "suggested_territory": best_territory,
            "confidence": best_score,
            "move_recommended": best_score > 0.5 and best_territory != current_territory,
            "all_scores": scores,
        }

    def _infer_current_territory(self, file_path: Path) -> str:
        """Infer the current territory from file path."""
        try:
            rel_path = file_path.relative_to(self.project_root)
            parts = rel_path.parts
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1]}"
            elif len(parts) == 1:
                return parts[0]
        except ValueError:
            pass
        return "unknown"

    async def suggest_territory_move(self, file_path: Path) -> Optional[str]:
        """
        Suggest a better territory for a file if it's misplaced.
        Ported from SemanticTerritoryMapperAgent.suggest_territory_move() (lines 81-94).
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            Suggested new path or None if current location is appropriate
        """
        mapping = await self.semantic_territory_map(file_path)
        
        if mapping.get("move_recommended"):
            suggested = mapping["suggested_territory"]
            return f"{suggested}/{file_path.name}"
        
        return None

    async def analyze_territory_coverage(self) -> Dict[str, Any]:
        """
        Analyze the coverage of territories across the codebase.
        Ported from SemanticTerritoryMapperAgent.analyze_territory_coverage() (lines 96-112).
        
        Returns:
            Dict with territory distribution statistics
        """
        stats = {
            'total_files': 0,
            'mapped_files': 0,
            'territory_distribution': {},
            'unmapped_files': [],
            'move_recommendations': [],
        }
        
        for py_file in self.project_root.rglob('*.py'):
            if '__pycache__' in str(py_file) or py_file.name == '__init__.py':
                continue
                
            stats['total_files'] += 1
            
            mapping = await self.semantic_territory_map(py_file)
            
            if mapping.get("suggested_territory") and mapping["suggested_territory"] != "unknown":
                stats['mapped_files'] += 1
                territory = mapping["suggested_territory"]
                stats['territory_distribution'][territory] = stats['territory_distribution'].get(territory, 0) + 1
                
                if mapping.get("move_recommended"):
                    stats['move_recommendations'].append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'current': mapping["current_territory"],
                        'suggested': mapping["suggested_territory"],
                        'confidence': mapping["confidence"],
                    })
            else:
                stats['unmapped_files'].append(str(py_file.relative_to(self.project_root)))
        
        return stats


# PascalCase is now the canonical name
