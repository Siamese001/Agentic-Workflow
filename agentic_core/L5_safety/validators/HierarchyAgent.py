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
from typing import List, Tuple, Dict, Any, Optional, Set
import os
import hashlib
import json
import ast

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
    AUTONOMOUS_AGENT_WHITELIST,
    SOVEREIGN_EXCLUDED_FOLDERS,
    ROOT_WHITELIST,
)
from agentic_core.common.healing.healer_mixin import HealerMixin


class HierarchyAgent(HealerMixin):
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
        'agentic_core/L4_state': 'memory cache pinecone redis Historian audit ledger',
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


    # SUB-ATOMIC CAPABILITY ENFORCEMENT — resurrected from LayerCapabilityAgent — eternal DDD purity — 2025-12-30
    
    # AST-based layer responsibility signatures (structural analysis)
    LAYER_METHOD_PATTERNS: Dict[str, List[str]] = {
        "L1": [
            "plan", "reason", "think_step_by_step", "critique", "reflect",
            "decompose", "generate_plan", "hypothesize", "self_critique"
        ],
        "L2": [
            "execute", "run_tool", "call_tool", "retrieve", "fetch",
            "get_evidence", "perform_action", "tool_use"
        ],
        "L3": [
            "orchestrate", "Route", "dispatch", "schedule", "coordinate",
            "next_node", "handle_retry", "manage_flow"
        ],
        "L4": [
            "apply_patch", "merge_patch", "update_state", "persist",
            "load_memory", "save_episode"
        ],
        "L5": [
            "check_safety", "apply_guardrail", "veto", "filter_output",
            "constitutional_review", "policy_enforce", "override", "validate", "heal"
        ]
    }

    # Forbidden cross-layer call targets (Enforcing Key 18 - Gravity)
    FORBIDDEN_CALLS: Dict[str, Set[str]] = {
        "L1": {"L2", "L3", "L4", "L5"},  # L1 only thinks — no execution/state/safety calls
        "L2": {"L1", "L3", "L5"},        # L2 executes — no reasoning/orchestration/safety
        "L3": set(),                      # L3 orchestrates — coordination calls permitted
    }

    MAX_CAPABILITIES = 2

    def enforce_subatomic_capability_isolation(self, file_path: Path = None) -> List[Tuple[Path, str]]:
        """
        SUB-ATOMIC CAPABILITY ENFORCEMENT — resurrected from LayerCapabilityAgent.
        
        Validates ≤2 layer capabilities per agent class.
        Ensures primary residency in exactly one dominant L-layer (L1–L5).
        
        Canon Key Enforcement:
        - Key 13 (Span of Two): Max 2 distinct capability domains
        - Key 18 (Gravity): No forbidden cross-layer calls
        - DDD Bounded Context: Clear primary layer responsibility
        
        Args:
            file_path: Optional specific file to analyze. If None, scans all *Agent*.py files.
            
        Returns:
            List of (file_path, violation_message) tuples
        """
        violations: List[Tuple[Path, str]] = []
        
        if file_path:
            agent_files = [file_path]
        else:
            agent_files = list(self.project_root.rglob("*Agent*.py"))
        
        for agent_file in agent_files:
            # Skip __init__.py and test files
            if agent_file.name == "__init__.py" or "test" in agent_file.name.lower():
                continue
                
            try:
                analysis = self._analyze_file_ast_capabilities(agent_file)
                
                if "error" in analysis:
                    violations.append((
                        agent_file,
                        f"PARSE_ERROR: {analysis['error']}"
                    ))
                    continue
                
                defined = analysis["defined_methods"]
                called = analysis["called_methods"]
                active_defined_layers = [l for l, methods in defined.items() if methods]
                primary_layer, primary_count = self._determine_primary_layer(defined)
                
                # Violation 1: Exceeding capability limit (Key 13 - Span of Two)
                if len(active_defined_layers) > self.MAX_CAPABILITIES:
                    violations.append((
                        agent_file,
                        f"TOO_MANY_CAPABILITIES: Defines methods from {len(active_defined_layers)} layers "
                        f"({', '.join(active_defined_layers)}) — max {self.MAX_CAPABILITIES} allowed"
                    ))
                
                # Violation 2: Weak Primary Residency (Unclear domain dominance)
                if len(active_defined_layers) > 1:
                    secondary_max = max(
                        len(defined[l]) for l in active_defined_layers if l != primary_layer
                    )
                    if primary_count <= secondary_max:
                        violations.append((
                            agent_file,
                            f"WEAK_PRIMARY_RESIDENCY: Primary {primary_layer} ({primary_count} methods) "
                            f"not clearly dominant over secondary ({secondary_max} methods)"
                        ))
                
                # Violation 3: Forbidden Cross-Layer Calls (Key 18 - Gravity Enforcement)
                if primary_layer != "UNKNOWN" and primary_layer in self.FORBIDDEN_CALLS:
                    forbidden = self.FORBIDDEN_CALLS[primary_layer]
                    violated_calls = []
                    for forbidden_layer in forbidden:
                        if called.get(forbidden_layer):
                            violated_calls.extend(list(called[forbidden_layer]))
                    
                    if violated_calls:
                        violations.append((
                            agent_file,
                            f"FORBIDDEN_CROSS_LAYER_CALL: Layer {primary_layer} agent violates gravity "
                            f"by calling forbidden methods: {', '.join(violated_calls[:5])}"
                        ))
                        
            except Exception as e:
                violations.append((
                    agent_file,
                    f"ANALYSIS_ERROR: {str(e)}"
                ))
        
        return violations

    def _analyze_file_ast_capabilities(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse AST and collect layer signals from method definitions and call sites.
        Distinguishes logic implementation from logic usage.
        
        Returns:
            Dict with 'defined_methods' and 'called_methods' per layer, or 'error' key
        """
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8", errors='ignore'))
        except SyntaxError as e:
            return {"error": f"SyntaxError: {e}"}
        except Exception as e:
            return {"error": f"ReadError: {e}"}
        
        signals = {
            "defined_methods": {layer: set() for layer in self.LAYER_METHOD_PATTERNS},
            "called_methods": {layer: set() for layer in self.LAYER_METHOD_PATTERNS}
        }
        
        class CapabilityVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node: ast.FunctionDef):
                method_name = node.name.lower()
                for layer, patterns in HierarchyAgent.LAYER_METHOD_PATTERNS.items():
                    if any(p.lower() in method_name for p in patterns):
                        signals["defined_methods"][layer].add(method_name)
                self.generic_visit(node)
            
            def visit_Call(self, node: ast.Call):
                # Detect target function name from direct call or attribute access
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id.lower()
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr.lower()
                
                for layer, patterns in HierarchyAgent.LAYER_METHOD_PATTERNS.items():
                    if any(p.lower() in func_name for p in patterns):
                        signals["called_methods"][layer].add(func_name)
                self.generic_visit(node)
        
        visitor = CapabilityVisitor()
        visitor.visit(tree)
        return signals

    def _determine_primary_layer(self, defined_methods: Dict[str, Set[str]]) -> Tuple[str, int]:
        """
        Identify the dominant layer based on the highest count of defined responsibility methods.
        
        Returns:
            Tuple of (primary_layer_name, method_count)
        """
        counts = {layer: len(methods) for layer, methods in defined_methods.items()}
        if not any(counts.values()):
            return "UNKNOWN", 0
        primary = max(counts, key=counts.get)
        return primary, counts[primary]

    def _classify_capability_domain(self, node: ast.AST) -> Optional[str]:
        """
        Classify AST node into capability domain based on imports and method patterns.
        
        Returns:
            Layer identifier (L1-L5) or None
        """
        if isinstance(node, ast.FunctionDef):
            method_name = node.name.lower()
            for layer, patterns in self.LAYER_METHOD_PATTERNS.items():
                if any(p in method_name for p in patterns):
                    return layer
        
        return None

    def run_with_capability_enforcement(self) -> Dict[str, Any]:
        """
        Full hierarchy compliance scan WITH sub-atomic capability enforcement.
        
        Returns:
            Dict with all violations including capability isolation violations
        """
        results = {
            'hierarchy_violations': [],
            'capability_violations': [],
            'total_violations': 0,
        }
        
        # Standard hierarchy checks
        hierarchy_violations = self.run()
        results['hierarchy_violations'] = hierarchy_violations
        
        # Sub-atomic capability enforcement
        capability_violations = self.enforce_subatomic_capability_isolation()
        results['capability_violations'] = capability_violations
        
        results['total_violations'] = len(hierarchy_violations) + len(capability_violations)
        
        return results


# PascalCase is now the canonical name
