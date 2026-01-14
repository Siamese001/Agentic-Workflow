from __future__ import annotations
"""
⚛️ Dependency Diplomat - Graph Optimizer

Maintains live Directed Acyclic Graph (DAG) of imports to optimize healing scope.
Calculates surgical target lists based on blast radius analysis.

Mission: Drastic CI/CD time reduction via surgical targeting
Strategy: "Heal the Neighborhood" not "Heal the World"

Impact: Hours → Minutes for targeted healing
"""
import ast
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Set
from agentic_core.utils.core_extensions.timeout_decorator import timeout
try:
    import redis
    REDIS_AVAILABLE: Any = True
except ImportError:
    REDIS_AVAILABLE: Any = False
from agentic_core.L2_execution.ToolRegistry.base import SubAtomicAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

Logger: Any = logging.getLogger(__name__)

@dataclass
class ImportNode:
    """Represents a file in the import graph."""
    file_path: str
    imports: Set[str] = field(default_factory=set)
    imported_by: Set[str] = field(default_factory=set)

@dataclass
class BlastRadius:
    """Blast radius analysis for a modified file."""
    modified_file: str
    direct_dependents: List[str]
    indirect_dependents: List[str]
    total_affected: int
    depth: int
    
    def _run_self_tests(self) -> bool:
        """Phase 1 Final: Minimal self-testing for data container."""
        assert hasattr(self, "modified_file"), "Missing modified_file"
        assert hasattr(self, "total_affected"), "Missing total_affected"
        assert isinstance(self.direct_dependents, list), "direct_dependents must be list"
        assert isinstance(self.indirect_dependents, list), "indirect_dependents must be list"
        return True
    
    def __post_init__(self) -> None:
        """Run self-tests after dataclass initialization."""
        assert self._run_self_tests(), f"Self-test failed: {self.__class__.__name__}"

# NAMING CANON ETERNAL — renamed for sovereign discovery — Phase 3 — 2025-12-30
class DependencyDiplomatAgent(SubAtomicAgent, MCPHardenedMixin):
    """
    The Dependency Diplomat - Graph Optimizer
    
    Maintains live DAG of imports in Redis.
    Calculates blast radius for modified files.
    Provides surgical target lists to orchestrator.
    
    Process:
    1. Parse all Python files for imports
    2. Build adjacency lists in Redis
    3. On file modification, calculate reverse dependencies
    4. Return surgical target list (only affected files)
    """

    def __init__(self, ctx: Any) -> None:
        """
        Initialize Dependency Diplomat.
        
        Args:
            ctx: ValidationContext
        """
        super().__init__(ctx)
        self.redis_available = REDIS_AVAILABLE
        if REDIS_AVAILABLE:
            try:
                self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
                self.redis.ping()
                Logger.info('[OK] Dependency Diplomat connected to Redis')
            except Exception as e:
                Logger.warning(f'[!]  Could not connect to Redis: {e}')
                self.redis_available = False
        self.graph: Dict[str, ImportNode] = {}

    async def execute(self) -> Any:
        """
        Execute dependency graph construction and analysis.
        
        Builds import graph and provides blast radius analysis.
        """
        Logger.info('🔗 Dependency Diplomat: Building import graph...')
        await self._build_graph()
        if hasattr(self.ctx, 'modified_files') and self.ctx.modified_files:
            for file_path in self.ctx.modified_files:
                BlastRadius: Any = self._calculate_blast_radius(file_path)
                self._report_blast_radius(BlastRadius)
                if not hasattr(self.ctx, 'blast_radii'):
                    self.ctx.blast_radii = {}
                self.ctx.blast_radii[file_path] = BlastRadius
        Logger.info(f'   Graph contains {len(self.graph)} nodes')

    async def _build_graph(self) -> Any:
        """Build import dependency graph."""
        python_files = self._find_python_files()
        for file_path in python_files:
            imports = self._parse_imports(file_path)
            if file_path not in self.graph:
                self.graph[file_path] = ImportNode(file_path=file_path)
            self.graph[file_path].imports = imports
            for imported_file in imports:
                if imported_file not in self.graph:
                    self.graph[imported_file] = ImportNode(file_path=imported_file)
                self.graph[imported_file].imported_by.add(file_path)
        if self.redis_available:
            self._persist_to_redis()

    def _find_python_files(self) -> List[str]:
        """Find all Python files in agentic_core."""
        python_files = []
        for py_file in Path('agentic_core').rglob('*.py'):
            python_files.append(str(py_file))
        return python_files

    def _parse_imports(self, file_path: str) -> Set[str]:
        """Parse imports from a Python file."""
        imports = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except Exception:
            return imports
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        return imports

    def _persist_to_redis(self) -> Any:
        """Persist graph to Redis with deps:forward: and deps:reverse: keys."""
        try:
            for file_path, node in self.graph.items():
                key = f'deps:forward:{file_path}'
                self.redis.delete(key)
                if node.imports:
                    self.redis.sadd(key, *node.imports)
                key = f'deps:reverse:{file_path}'
                self.redis.delete(key)
                if node.imported_by:
                    self.redis.sadd(key, *node.imported_by)
            Logger.info('   Graph persisted to Redis with deps:forward: and deps:reverse: keys')
        except Exception as e:
            Logger.warning(f'Could not persist to Redis: {e}')

    def _calculate_blast_radius(self, modified_file: str, max_depth: int=5) -> BlastRadius:
        """
        Calculate blast radius for a modified file.
        
        Walks graph in reverse to find all dependent files.
        
        Args:
            modified_file: File that was modified
            max_depth: Maximum depth to traverse
            
        Returns:
            Blast radius analysis
        """
        if modified_file not in self.graph:
            return BlastRadius(modified_file=modified_file, direct_dependents=[], indirect_dependents=[], total_affected=0, depth=0)
        node = self.graph[modified_file]
        direct_dependents = list(node.imported_by)
        indirect_dependents = []
        visited = set([modified_file] + direct_dependents)
        queue = [(dep, 1) for dep in direct_dependents]
        max_depth_reached = 0
        while queue and max_depth_reached < max_depth:
            current_file, depth = queue.pop(0)
            max_depth_reached = max(max_depth_reached, depth)
            if current_file not in self.graph:
                continue
            current_node = self.graph[current_file]
            for dependent in current_node.imported_by:
                if dependent not in visited:
                    visited.add(dependent)
                    indirect_dependents.append(dependent)
                    queue.append((dependent, depth + 1))
        return BlastRadius(modified_file=modified_file, direct_dependents=direct_dependents, indirect_dependents=indirect_dependents, total_affected=len(direct_dependents) + len(indirect_dependents), depth=max_depth_reached)

    def _report_blast_radius(self, BlastRadius: BlastRadius) -> Any:
        """Report blast radius analysis."""
        Logger.info(f"\n{'=' * 80}")
        Logger.info(f'🔗 BLAST RADIUS ANALYSIS')
        Logger.info(f"{'=' * 80}")
        Logger.info(f'Modified File: {BlastRadius.modified_file}')
        Logger.info(f'Direct Dependents: {len(BlastRadius.direct_dependents)}')
        Logger.info(f'Indirect Dependents: {len(BlastRadius.indirect_dependents)}')
        Logger.info(f'Total Affected: {BlastRadius.total_affected}')
        Logger.info(f'Max Depth: {BlastRadius.depth}')
        if BlastRadius.direct_dependents:
            Logger.info(f'\nDirect Dependents (showing first 10):')
            for dep in BlastRadius.direct_dependents[:10]:
                Logger.info(f'  - {dep}')
            if len(BlastRadius.direct_dependents) > 10:
                Logger.info(f'  ... and {len(BlastRadius.direct_dependents) - 10} more')
        if BlastRadius.indirect_dependents:
            Logger.info(f'\nIndirect Dependents (showing first 10):')
            for dep in BlastRadius.indirect_dependents[:10]:
                Logger.info(f'  - {dep}')
            if len(BlastRadius.indirect_dependents) > 10:
                Logger.info(f'  ... and {len(BlastRadius.indirect_dependents) - 10} more')
        Logger.info(f"{'=' * 80}\n")

    def calculate_impact_scope(self, modified_files: List[str], max_depth: int=2) -> List[str]:
        """
        Calculate impact scope for modified files using BFS on reverse dependency graph.
        
        This is the primary method for orchestrator integration.
        Performs BFS on deps:reverse graph to find all files that import the changed files.
        Depth is capped at 2 levels to keep testing focused.
        
        Args:
            modified_files: List of files changed by SystemArchitect
            max_depth: Maximum depth for BFS traversal (default: 2)
            
        Returns:
            List of files that need healing/testing (surgical target list)
        """
        Logger.info(f'🔗 Calculating impact scope for {len(modified_files)} modified files...')
        impact_scope: Any = set(modified_files)
        queue: Any = [(file, 0) for file in modified_files]
        visited: Any = set(modified_files)
        while queue:
            current_file, depth = queue.pop(0)
            if depth >= max_depth:
                continue
            if current_file in self.graph:
                reverse_deps: Any = self.graph[current_file].imported_by
                for dependent in reverse_deps:
                    if dependent not in visited:
                        visited.add(dependent)
                        impact_scope.add(dependent)
                        queue.append((dependent, depth + 1))
        result: Any = list(impact_scope)
        Logger.info(f'   Impact scope: {len(result)} files (depth limit: {max_depth})')
        return result

    def get_surgical_target_list(self, modified_files: List[str]) -> List[str]:
        """
        Get surgical target list for modified files.
        
        This is an alias for calculate_impact_scope() for backward compatibility.
        
        Args:
            modified_files: List of modified files
            
        Returns:
            List of files that need healing/testing
        """
        return self.calculate_impact_scope(modified_files, max_depth=2)

    def export_graph_visualization(self, output_file: str='DependencyGraph.json') -> Any:
        """Export graph for visualization."""
        graph_data: Any = {'nodes': [], 'edges': []}
        for file_path, node in self.graph.items():
            graph_data['nodes'].append({'id': file_path, 'label': Path(file_path).name})
            for imported_file in node.imports:
                graph_data['edges'].append({'from': file_path, 'to': imported_file})
        with open(output_file, 'w') as f:
            json.dump(graph_data, f, indent=2)
        Logger.info(f'Graph exported to {output_file}')

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L2 execution agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L2 execution - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

_dependency_diplomat = None

def get_dependency_diplomat(ctx: Any) -> DependencyDiplomat:
    """Get or create global Dependency Diplomat instance."""
    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    global _dependency_diplomat
    if _dependency_diplomat is None:
        _dependency_diplomat = DependencyDiplomat(ctx)
    return _dependency_diplomat