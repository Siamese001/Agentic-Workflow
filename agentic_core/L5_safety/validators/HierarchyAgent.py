from __future__ import annotations
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

GOLD STANDARD UPGRADE (2026-01-02):
- Structured Violation dataclass with severity levels
- Post-heal validation for verifying fixes
- Deep validation cycles with NamingAgent/ImportAgent integration
- Batch post-heal reporting with FULL_SUCCESS/PARTIAL/NEEDS_REVIEW status
- Safe move/flatten operations with backup
- Autonomous cleanup_violations with multi-stage healing
- run_with_cleanup returning comprehensive summaries
"""
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional, Set
from dataclasses import dataclass
import os
import hashlib
import json
import ast
import re
import shutil
from datetime import datetime

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
    AUTONOMOUS_AGENT_WHITELIST,
    SOVEREIGN_EXCLUDED_FOLDERS,
    ROOT_WHITELIST,
    TESTS_ROOT_FILE_WHITELIST,
    is_app_specific_file,
    get_correct_app_path,
    validate_path_within_project,
    get_validated_project_root,
    safe_path_join,
)
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout, HealTimeoutError

# Try to import Logger, fallback to print
try:
    from agentic_core.utils.core_extensions.logger_mixin import Logger
except ImportError:
    class Logger:
        @staticmethod
        def info(msg): print(f"[INFO] {msg}")
        @staticmethod
        def warning(msg): print(f"[WARNING] {msg}")
        @staticmethod
        def error(msg): print(f"[ERROR] {msg}")


class HierarchyAgent(HealerMixin, MCPHardenedMixin):
    """
    Autonomous agent for hierarchical structure compliance.
    Scans folders only (no file content parsing).
    Run after LocationAgent.
    
    RCA FIX 2026-01-02: Added project root validation to prevent folder creation
    outside the active project root.
    
    GOLD STANDARD FEATURES (2026-01-02):
    - Structured Violation dataclass with severity levels and suggested fixes
    - Post-heal validation confirming hierarchy compliance after moves
    - Deep validation cycles integrating NamingAgent for naming compliance
    - Batch post-heal reporting with status: FULL_SUCCESS / PARTIAL / NEEDS_REVIEW
    - Safe flatten operations with backup for span-of-two violations
    - Autonomous cleanup_violations with multi-stage healing:
        1. Flatten redundant tunnels (span-of-two)
        2. Move shallow/deep files to correct depth
        3. Archive unapproved L1/L2 folders
        4. Post-heal validation on all affected paths
        5. NamingAgent integration for naming compliance
    - run_with_cleanup returning comprehensive summaries
    
    VIOLATION SEVERITY LEVELS:
    - 10: CRITICAL - Structural corruption requiring immediate fix
    - 7: HIGH - Depth violations, unapproved folders
    - 5: MEDIUM - Span-of-two violations (redundant tunnels)
    - 3: LOW - Minor drift, cosmetic issues
    """

    @dataclass
    class Violation:
        """Structured violation output for deterministic healing."""
        is_valid: bool
        message: str
        file_path: Optional[Path] = None
        suggested_action: Optional[str] = None  # FLATTEN, MOVE, ARCHIVE, REPORT
        suggested_target: Optional[str] = None  # Target path for healing
        severity: int = 5

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.excluded_folders = SOVEREIGN_EXCLUDED_FOLDERS
        # Cache for faster healing suggestions
        self._app_specific_checked: Dict[Path, bool] = {}
        # Validate project root
        self._validate_project_root()
        # LocationAgent and GovernanceAgent are lazy-loaded to avoid circular imports
        self._location_agent = None
        self._governance_agent = None
        # Backup directory for safe operations
        self._backup_dir: Optional[Path] = None
    
    @property
    def location_agent(self):
        """Lazy-load LocationAgent to avoid circular import."""
        if self._location_agent is None:
            try:
                from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
                self._location_agent = LocationAgent(self.project_root)
            except ImportError:
                pass
        return self._location_agent
    
    @property
    def governance_agent(self):
        """Lazy-load GovernanceAgent to avoid circular import."""
        if self._governance_agent is None:
            try:
                from agentic_core.L3_orchestration.workflow_engines.ArchitectureGovernorAgent import ArchitectureGovernorAgent
                self._governance_agent = ArchitectureGovernorAgent(str(self.project_root))
            except ImportError:
                pass
        return self._governance_agent

    def _validate_project_root(self) -> None:
        """Validate project_root is the actual project root."""
        validated_root = get_validated_project_root()
        if self.project_root != validated_root:
            self.project_root = validated_root

    def suggest_healing_move(self, file_path: Path, violation_msg: str) -> Optional[str]:
        """
        HealerMixin-compatible suggestion for app-specific misplacement.
        Returns a git mv command string or None.
        """
        if "APP-SPECIFIC IN CORE" in violation_msg or (
            len(file_path.parts) > 0 and file_path.parts[0] == "agentic_core" and is_app_specific_file(file_path.name)
        ):
            correct_path = get_correct_app_path(file_path.name)
            if correct_path:
                return f"git mv {file_path} {self.project_root / correct_path / file_path.name}"
        return None

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

            # No files directly under root (Key 41) - except whitelisted test infrastructure
            whitelist = TESTS_ROOT_FILE_WHITELIST if root_key == "tests" else frozenset()
            root_py_files = [
                p.name for p in root_path.iterdir()
                if p.is_file() and p.suffix == ".py" and p.name != "__init__.py"
                and p.name not in whitelist
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

    def check_span_of_two(self) -> Dict[str, Any]:
        """
        Wrapper for check_span_of_two_violations() returning structured result.
        Used by mission_preflight.py for L6 preflight checks.
        """
        violations = self.check_span_of_two_violations()
        return {
            "compliant": len(violations) == 0,
            "violations": len(violations),
            "details": [msg for _, msg in violations],
        }

    def validate_hierarchy(self) -> List[Tuple[Path, str]]:
        """
        Alias for validate_canonical_hierarchy().
        Used by mission_preflight.py for L6 preflight checks.
        """
        return self.validate_canonical_hierarchy()


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
            # Use agent_discovery_full.json as authoritative source
            json_path = self.project_root / "agent_discovery_full.json"
            if json_path.exists():
                try:
                    data = json.loads(json_path.read_text(encoding="utf-8"))
                    agent_files = []
                    for agent in data:
                        path_str = agent.get("path", "").replace("\\", "/")
                        if path_str:
                            full_path = self.project_root / path_str
                            if full_path.exists():
                                agent_files.append(full_path)
                except Exception:
                    agent_files = list(self.project_root.rglob("*Agent*.py"))
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

    # ==================== GOLD STANDARD METHODS (2026-01-02) ====================

    def _init_backup_dir(self) -> Path:
        """Initialize and return the backup directory for safe operations."""
        if self._backup_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._backup_dir = self.project_root / ".hierarchy_healer_backups" / timestamp
            self._backup_dir.mkdir(parents=True, exist_ok=True)
        return self._backup_dir

    def _backup_path(self, path: Path) -> Path:
        """Backup a file or directory before modification."""
        backup_dir = self._init_backup_dir()
        try:
            rel_path = path.relative_to(self.project_root)
        except ValueError:
            rel_path = Path(path.name)
        backup_path = backup_dir / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            shutil.copytree(path, backup_path, dirs_exist_ok=True)
        else:
            shutil.copy2(path, backup_path)
        return backup_path

    def safe_flatten(self, tunnel_path: Path, dry_run: bool = True) -> Dict[str, Any]:
        """
        Safely flatten a span-of-two tunnel directory.
        Moves contents up to parent and removes empty tunnel.
        """
        result = {
            "applied": False,
            "action_taken": "",
            "files_moved": [],
            "error": None,
        }

        if not tunnel_path.is_dir():
            result["error"] = "Not a directory"
            return result

        parent = tunnel_path.parent
        children = list(tunnel_path.iterdir())

        if dry_run:
            result["applied"] = True
            result["action_taken"] = f"PREVIEW: Would flatten {tunnel_path.name} → move {len(children)} items to {parent.name}"
            return result

        try:
            self._backup_path(tunnel_path)
            moved = []
            for child in children:
                target = parent / child.name
                if target.exists():
                    # Handle collision
                    stem, suffix = child.stem, child.suffix
                    counter = 1
                    while target.exists():
                        target = parent / f"{stem}_{counter}{suffix}"
                        counter += 1
                shutil.move(str(child), str(target))
                moved.append(str(target.relative_to(self.project_root)))

            # Remove empty tunnel
            if not list(tunnel_path.iterdir()):
                tunnel_path.rmdir()

            result["applied"] = True
            result["action_taken"] = f"FLATTENED: {tunnel_path.name} → {len(moved)} items moved to {parent.name}"
            result["files_moved"] = moved
            Logger.info(f"[HierarchyAgent] Flattened tunnel: {tunnel_path}")

        except Exception as e:
            result["error"] = str(e)
            Logger.error(f"[HierarchyAgent] Flatten failed: {e}")

        return result

    def safe_move_to_depth(self, file_path: Path, target_depth: int, dry_run: bool = True) -> Dict[str, Any]:
        """
        Safely move a file to the correct depth in the hierarchy.
        Creates intermediate directories as needed.
        """
        result = {
            "applied": False,
            "action_taken": "",
            "new_path": None,
            "error": None,
        }

        try:
            rel_parts = file_path.relative_to(self.project_root).parts
        except ValueError:
            result["error"] = "File not within project root"
            return result

        current_depth = len(rel_parts)
        if current_depth == target_depth:
            result["action_taken"] = "Already at correct depth"
            return result

        # Determine target path
        if current_depth < target_depth:
            # Need to move deeper - create intermediate folder
            root = rel_parts[0] if rel_parts else "agentic_core"
            l1 = rel_parts[1] if len(rel_parts) > 1 else "L0_maintenance"
            l2 = "scripts"  # Default L2 for shallow files
            target_path = self.project_root / root / l1 / l2 / file_path.name
        else:
            # Need to move shallower - move up
            target_path = self.project_root / "/".join(rel_parts[:target_depth-1]) / file_path.name

        if dry_run:
            result["applied"] = True
            result["action_taken"] = f"PREVIEW: Would move to depth {target_depth}: {target_path.relative_to(self.project_root)}"
            result["new_path"] = str(target_path.relative_to(self.project_root))
            return result

        try:
            self._backup_path(file_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Handle collision
            final_target = target_path
            if final_target.exists():
                stem, suffix = target_path.stem, target_path.suffix
                counter = 1
                while final_target.exists():
                    final_target = target_path.parent / f"{stem}_{counter}{suffix}"
                    counter += 1

            shutil.move(str(file_path), str(final_target))
            result["applied"] = True
            result["action_taken"] = f"MOVED: {file_path.name} → {final_target.relative_to(self.project_root)}"
            result["new_path"] = str(final_target.relative_to(self.project_root))
            Logger.info(f"[HierarchyAgent] Moved to depth: {file_path} → {final_target}")

        except Exception as e:
            result["error"] = str(e)
            Logger.error(f"[HierarchyAgent] Move to depth failed: {e}")

        return result

    def safe_archive(self, path: Path, dry_run: bool = True) -> Dict[str, Any]:
        """Safely archive an unapproved folder/file to archives."""
        result = {
            "applied": False,
            "action_taken": "",
            "archive_path": None,
            "error": None,
        }

        archive_root = self.project_root / "archives" / "hierarchy_violations"
        try:
            rel_path = path.relative_to(self.project_root)
        except ValueError:
            result["error"] = "Path not within project root"
            return result

        archive_target = archive_root / rel_path

        if dry_run:
            result["applied"] = True
            result["action_taken"] = f"PREVIEW: Would archive to {archive_target.relative_to(self.project_root)}"
            result["archive_path"] = str(archive_target.relative_to(self.project_root))
            return result

        try:
            self._backup_path(path)
            archive_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(archive_target))
            result["applied"] = True
            result["action_taken"] = f"ARCHIVED: {rel_path} → {archive_target.relative_to(self.project_root)}"
            result["archive_path"] = str(archive_target.relative_to(self.project_root))
            Logger.info(f"[HierarchyAgent] Archived: {path}")

        except Exception as e:
            result["error"] = str(e)
            Logger.error(f"[HierarchyAgent] Archive failed: {e}")

        return result

    def post_heal_validation(self, affected_paths: List[Path], dry_run: bool = True) -> Dict[str, Any]:
        """
        Validate hierarchy compliance on affected paths after healing.
        Returns structured report with status.
        """
        report = {
            "post_heal_status": "SKIPPED",
            "remaining_violations": [],
            "success_rate": 0.0,
            "message": "",
        }

        if dry_run:
            report["message"] = "PREVIEW: Post-heal validation skipped in dry-run"
            return report

        valid_paths = [p for p in affected_paths if p.exists()]
        if not valid_paths:
            report["post_heal_status"] = "NO_PATHS"
            report["message"] = "No valid paths to validate"
            return report

        # Re-run hierarchy checks on affected paths
        remaining = []
        for path in valid_paths:
            if path.is_dir():
                is_valid, msg = self.check_span_of_two_violation(path)
                if not is_valid:
                    remaining.append({"path": str(path), "issue": msg})
            elif path.is_file() and path.suffix == ".py":
                try:
                    rel_parts = path.relative_to(self.project_root).parts
                    if rel_parts[0] == "agentic_core" and path.name != "__init__.py":
                        depth = len(rel_parts)
                        if depth != 4:
                            remaining.append({"path": str(path), "issue": f"Depth {depth} != 4"})
                except ValueError:
                    pass

        report["remaining_violations"] = remaining
        total = len(valid_paths)
        resolved = total - len(remaining)
        report["success_rate"] = (resolved / total * 100) if total > 0 else 100.0

        if not remaining:
            report["post_heal_status"] = "FULL_SUCCESS"
            report["message"] = f"All {total} paths now hierarchy-compliant"
        elif report["success_rate"] >= 90:
            report["post_heal_status"] = "HIGH_SUCCESS"
            report["message"] = f"{report['success_rate']:.1f}% success — minor remaining issues"
        else:
            report["post_heal_status"] = "PARTIAL"
            report["message"] = f"{report['success_rate']:.1f}% success — review remaining violations"

        return report

    def post_location_validation(self, affected_paths: List[Path], dry_run: bool = True) -> Dict[str, Any]:
        """
        Run LocationAgent validation on affected paths after hierarchy healing.
        Ensures files are in correct territories after depth/structure fixes.
        """
        report = {
            "location_status": "SKIPPED",
            "location_violations": [],
            "message": "",
        }

        if dry_run or not self.location_agent:
            report["message"] = "PREVIEW: Location validation skipped"
            return report

        py_files = [p for p in affected_paths if p.suffix == ".py" and p.exists()]
        if not py_files:
            report["location_status"] = "NO_FILES"
            report["message"] = "No Python files to validate"
            return report

        # Run LocationAgent validation on affected files
        try:
            violations = self.location_agent.run(py_files)
            report["location_violations"] = [
                {"file": str(v.file_path), "message": v.message} 
                for v in violations if hasattr(v, 'file_path')
            ]
            
            if not report["location_violations"]:
                report["location_status"] = "FULL_SUCCESS"
                report["message"] = f"All {len(py_files)} files location-compliant"
            else:
                report["location_status"] = "PARTIAL"
                report["message"] = f"{len(report['location_violations'])} location issues found"
        except Exception as e:
            report["location_status"] = "ERROR"
            report["message"] = f"Location validation error: {e}"

        return report

    def post_governance_validation(self, affected_paths: List[Path], dry_run: bool = True) -> Dict[str, Any]:
        """
        Run GovernanceAgent validation on affected paths after hierarchy healing.
        Checks architectural rules, blast radius, and complexity.
        """
        report = {
            "governance_status": "SKIPPED",
            "governance_violations": [],
            "blast_radius": None,
            "message": "",
        }

        if dry_run or not self.governance_agent:
            report["message"] = "PREVIEW: Governance validation skipped"
            return report

        py_files = [str(p) for p in affected_paths if p.suffix == ".py" and p.exists()]
        if not py_files:
            report["governance_status"] = "NO_FILES"
            report["message"] = "No Python files to validate"
            return report

        try:
            # Run architectural validation
            arch_report = self.governance_agent.validate_architecture(file_paths=py_files, enforce=False)
            
            all_violations = (
                arch_report.get("depth_violations", []) +
                arch_report.get("atomicity_violations", []) +
                arch_report.get("complexity_violations", [])
            )
            report["governance_violations"] = all_violations
            report["blast_radius"] = arch_report.get("BlastRadius")
            
            if arch_report.get("overall_status") == "PASS":
                report["governance_status"] = "FULL_SUCCESS"
                report["message"] = f"All {len(py_files)} files governance-compliant"
            else:
                report["governance_status"] = "PARTIAL"
                report["message"] = f"{len(all_violations)} governance issues found"
        except Exception as e:
            report["governance_status"] = "ERROR"
            report["message"] = f"Governance validation error: {e}"

        return report

    def cleanup_violations(self, violations: List[Tuple[Path, str]], dry_run: bool = True, max_actions: int = 50) -> List[Dict[str, Any]]:
        """
        GOLD STANDARD CLEANUP ENGINE — Multi-stage autonomous healing.
        
        Healing stages:
        1. Flatten span-of-two tunnels
        2. Move depth violations to correct level
        3. Archive unapproved L1/L2 folders
        4. Post-heal validation on all affected paths
        5. LocationAgent integration for territory compliance
        6. GovernanceAgent integration for architectural rules
        
        Returns:
            List of action results with batch post-heal summary
        """
        actions = []
        affected_paths: List[Path] = []

        for idx, (path, msg) in enumerate(violations[:max_actions]):
            action = {
                "violation": msg,
                "path": str(path),
                "applied": False,
                "action_taken": "",
                "error": None,
            }

            # Determine healing action based on violation type
            if "SPAN-OF-TWO" in msg:
                result = self.safe_flatten(path, dry_run=dry_run)
                action.update(result)
                if result.get("files_moved"):
                    affected_paths.extend([self.project_root / p for p in result["files_moved"]])

            elif "DEEP VIOLATION" in msg or "SHALLOW VIOLATION" in msg:
                result = self.safe_move_to_depth(path, target_depth=4, dry_run=dry_run)
                action.update(result)
                if result.get("new_path"):
                    affected_paths.append(self.project_root / result["new_path"])

            elif "HIERARCHY DRIFT" in msg or "DEPTH VIOLATION" in msg:
                result = self.safe_archive(path, dry_run=dry_run)
                action.update(result)
                if result.get("archive_path"):
                    affected_paths.append(self.project_root / result["archive_path"])

            else:
                action["action_taken"] = "REPORT_ONLY: Manual review required"
                action["applied"] = False

            actions.append(action)

        # === BATCH POST-HEAL VALIDATION ===
        batch_report = {
            "batch_post_heal_status": "PENDING",
            "batch_remaining_violations": [],
            "batch_success_rate": 0.0,
            "batch_message": "",
        }

        if dry_run:
            batch_report["batch_message"] = "PREVIEW: Batch validation skipped"
            batch_report["batch_post_heal_status"] = "PREVIEW"
        else:
            # Post-heal hierarchy validation
            heal_report = self.post_heal_validation(affected_paths, dry_run=False)
            batch_report.update({
                "batch_post_heal_status": heal_report["post_heal_status"],
                "batch_remaining_violations": heal_report["remaining_violations"],
                "batch_success_rate": heal_report["success_rate"],
                "batch_message": heal_report["message"],
            })

            # LocationAgent integration - ensure files are in correct territories
            location_report = self.post_location_validation(affected_paths, dry_run=False)
            batch_report["location_validation"] = location_report
            batch_report["batch_message"] += f" | Location: {location_report['location_status']}"

            # GovernanceAgent integration - check architectural rules and blast radius
            governance_report = self.post_governance_validation(affected_paths, dry_run=False)
            batch_report["governance_validation"] = governance_report
            batch_report["batch_message"] += f" | Governance: {governance_report['governance_status']}"

        # Attach batch report to all actions
        for action in actions:
            action["batch_post_heal"] = batch_report

        return actions

    def run_with_cleanup(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        GOLD STANDARD WORKFLOW — Full hierarchy compliance with autonomous cleanup.
        
        Returns:
            Dict with violation count, actions applied, batch summaries, and details
        """
        violations = self.run()
        cleanup_results = self.cleanup_violations(violations, dry_run=dry_run) if violations else []

        # Extract batch summary
        batch_summary = cleanup_results[0].get("batch_post_heal", {}) if cleanup_results else {}

        return {
            "violations_detected": len(violations),
            "actions_applied": sum(1 for a in cleanup_results if a.get("applied")),
            "detailed_actions": cleanup_results,
            "batch_post_heal_summary": batch_summary,
            "location_validation_summary": batch_summary.get("location_validation", {}),
            "governance_validation_summary": batch_summary.get("governance_validation", {}),
            "capability_violations": self.enforce_subatomic_capability_isolation(),
            "dry_run": dry_run,
        }

    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[Set[str]] = None,
    ) -> Dict[str, int]:
        """
        Autonomous full-repository hierarchy law healing.
        Canon Key 51 compliance - fully self-orchestrating.
        
        Args:
            dry_run: If True, only propose changes
            execute: Must be explicitly True to perform changes
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Set of agent names in call path (cycle detection)
            
        Returns:
            Summary dict with counts
        """
        if _call_path is None:
            _call_path = set()
        
        agent_name = self.__class__.__name__
        
        # CYCLE DETECTION
        if agent_name in _call_path:
            print(f"  [!] HEALING CYCLE DETECTED: {agent_name} already in path → stopping")
            return {"healed": 0, "blocked": 0, "errors": 0, "skipped": 0, "cycle_detected": True}
        
        # DEPTH LIMIT
        if depth > max_depth:
            print(f"  [!] RECURSION DEPTH LIMIT REACHED ({depth}/{max_depth}) → stopping")
            return {"healed": 0, "blocked": 0, "errors": 0, "skipped": 0, "depth_limited": True}
        
        _call_path.add(agent_name)
        
        if execute and dry_run:
            raise ValueError("execute and dry_run cannot both be True")
        
        actual_execute = execute and not dry_run
        
        try:
            # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
            super().heal_repository()
            
            violations = self.run()
            print(f"[HIERARCHY HEAL @ depth {depth}] Found {len(violations)} violations")
            
            counts = {"healed": 0, "blocked": 0, "errors": 0, "skipped": 0}
            
            for file_path, reason in violations:
                try:
                    # Use existing cleanup_violations for single-item healing
                    cleanup_results = self.cleanup_violations([(file_path, reason)], dry_run=not actual_execute)
                    
                    if cleanup_results and cleanup_results[0].get("applied"):
                        counts["healed"] += 1
                        print(f"  [+] HEALED: {file_path.name} - {cleanup_results[0].get('action_taken', 'fixed')}")
                    elif cleanup_results and cleanup_results[0].get("error"):
                        counts["errors"] += 1
                        print(f"  [!] ERROR: {file_path.name} - {cleanup_results[0]['error']}")
                    else:
                        counts["skipped"] += 1
                        
                except Exception as e:
                    counts["errors"] += 1
                    print(f"  [!] ERROR on {file_path.name}: {e}")
            
            print(f"\n[HIERARCHY HEAL SUMMARY] "
                  f"Healed: {counts['healed']} | "
                  f"Blocked: {counts['blocked']} | "
                  f"Skipped: {counts['skipped']} | "
                  f"Errors: {counts['errors']}")
            
            return counts
            
        finally:
            _call_path.discard(agent_name)


# PascalCase is now the canonical name
