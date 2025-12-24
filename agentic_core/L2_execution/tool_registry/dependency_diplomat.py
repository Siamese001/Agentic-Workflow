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
from typing import Any, Optional, Protocol, Dict, List

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from agentic_core.L2_execution.tool_registry.base import SubAtomicAgent

logger = logging.getLogger(__name__)


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


class DependencyDiplomat(SubAtomicAgent):
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
    
    def __init__(self, ctx):
        """
        Initialize Dependency Diplomat.
        
        Args:
            ctx: ValidationContext
        """
        super().__init__(ctx)
        
        # Redis connection
        self.redis_available = REDIS_AVAILABLE
        if REDIS_AVAILABLE:
            try:
                self.redis = redis.Redis(
                    host='localhost',
                    port=6379,
                    decode_responses=True
                )
                self.redis.ping()
                logger.info("[OK] Dependency Diplomat connected to Redis")
            except Exception as e:
                logger.warning(f"[!]  Could not connect to Redis: {e}")
                self.redis_available = False
        
        # In-memory graph (fallback)
        self.graph: Dict[str, ImportNode] = {}
    
    async def execute(self):
        """
        Execute dependency graph construction and analysis.
        
        Builds import graph and provides blast radius analysis.
        """
        logger.info("🔗 Dependency Diplomat: Building import graph...")
        
        # Build graph
        await self._build_graph()
        
        # Analyze modified files
        if hasattr(self.ctx, 'modified_files') and self.ctx.modified_files:
            for file_path in self.ctx.modified_files:
                blast_radius = self._calculate_blast_radius(file_path)
                self._report_blast_radius(blast_radius)
                
                # Store in context for orchestrator
                if not hasattr(self.ctx, 'blast_radii'):
                    self.ctx.blast_radii = {}
                self.ctx.blast_radii[file_path] = blast_radius
        
        logger.info(f"   Graph contains {len(self.graph)} nodes")
    
    async def _build_graph(self):
        """Build import dependency graph."""
        # Get all Python files
        python_files = self._find_python_files()
        
        # Parse each file for imports
        for file_path in python_files:
            imports = self._parse_imports(file_path)
            
            # Add to graph
            if file_path not in self.graph:
                self.graph[file_path] = ImportNode(file_path=file_path)
            
            self.graph[file_path].imports = imports
            
            # Update reverse dependencies
            for imported_file in imports:
                if imported_file not in self.graph:
                    self.graph[imported_file] = ImportNode(file_path=imported_file)
                
                self.graph[imported_file].imported_by.add(file_path)
        
        # Persist to Redis
        if self.redis_available:
            self._persist_to_redis()
    
    def _find_python_files(self) -> List[str]:
        """Find all Python files in agentic_core."""
        python_files = []
        
        # Scan agentic_core
        for py_file in Path("agentic_core").rglob("*.py"):
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
    
    def _persist_to_redis(self):
        """Persist graph to Redis with deps:forward: and deps:reverse: keys."""
        try:
            for file_path, node in self.graph.items():
                # Store forward dependencies (what this file imports)
                key = f"deps:forward:{file_path}"
                self.redis.delete(key)
                if node.imports:
                    self.redis.sadd(key, *node.imports)
                
                # Store reverse dependencies (what imports this file)
                key = f"deps:reverse:{file_path}"
                self.redis.delete(key)
                if node.imported_by:
                    self.redis.sadd(key, *node.imported_by)
            
            logger.info("   Graph persisted to Redis with deps:forward: and deps:reverse: keys")
        except Exception as e:
            logger.warning(f"Could not persist to Redis: {e}")
    
    def _calculate_blast_radius(self, modified_file: str, max_depth: int = 5) -> BlastRadius:
        """
        Calculate blast radius for a modified file.
        
        Walks graph in reverse to find all dependent files.
        
        Args:
            modified_file: File that was modified
            max_depth: Maximum depth to traverse
            
        Returns:
            Blast radius analysis
        """
        # Get node
        if modified_file not in self.graph:
            return BlastRadius(
                modified_file=modified_file,
                direct_dependents=[],
                indirect_dependents=[],
                total_affected=0,
                depth=0
            )
        
        node = self.graph[modified_file]
        
        # Direct dependents
        direct_dependents = list(node.imported_by)
        
        # Indirect dependents (BFS)
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
        
        return BlastRadius(
            modified_file=modified_file,
            direct_dependents=direct_dependents,
            indirect_dependents=indirect_dependents,
            total_affected=len(direct_dependents) + len(indirect_dependents),
            depth=max_depth_reached
        )
    
    def _report_blast_radius(self, blast_radius: BlastRadius):
        """Report blast radius analysis."""
        logger.info(f"\n{'='*80}")
        logger.info(f"🔗 BLAST RADIUS ANALYSIS")
        logger.info(f"{'='*80}")
        logger.info(f"Modified File: {blast_radius.modified_file}")
        logger.info(f"Direct Dependents: {len(blast_radius.direct_dependents)}")
        logger.info(f"Indirect Dependents: {len(blast_radius.indirect_dependents)}")
        logger.info(f"Total Affected: {blast_radius.total_affected}")
        logger.info(f"Max Depth: {blast_radius.depth}")
        
        if blast_radius.direct_dependents:
            logger.info(f"\nDirect Dependents (showing first 10):")
            for dep in blast_radius.direct_dependents[:10]:
                logger.info(f"  - {dep}")
            
            if len(blast_radius.direct_dependents) > 10:
                logger.info(f"  ... and {len(blast_radius.direct_dependents) - 10} more")
        
        if blast_radius.indirect_dependents:
            logger.info(f"\nIndirect Dependents (showing first 10):")
            for dep in blast_radius.indirect_dependents[:10]:
                logger.info(f"  - {dep}")
            
            if len(blast_radius.indirect_dependents) > 10:
                logger.info(f"  ... and {len(blast_radius.indirect_dependents) - 10} more")
        
        logger.info(f"{'='*80}\n")
    
    def calculate_impact_scope(self, modified_files: List[str], max_depth: int = 2) -> List[str]:
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
        logger.info(f"🔗 Calculating impact scope for {len(modified_files)} modified files...")
        
        # Start with modified files
        impact_scope = set(modified_files)
        
        # BFS queue: (file_path, current_depth)
        queue = [(file, 0) for file in modified_files]
        visited = set(modified_files)
        
        # Perform BFS on reverse dependencies
        while queue:
            current_file, depth = queue.pop(0)
            
            # Stop if we've reached max depth
            if depth >= max_depth:
                continue
            
            # Get reverse dependencies (files that import current_file)
            if current_file in self.graph:
                reverse_deps = self.graph[current_file].imported_by
                
                for dependent in reverse_deps:
                    if dependent not in visited:
                        visited.add(dependent)
                        impact_scope.add(dependent)
                        queue.append((dependent, depth + 1))
        
        result = list(impact_scope)
        logger.info(f"   Impact scope: {len(result)} files (depth limit: {max_depth})")
        
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
    
    def export_graph_visualization(self, output_file: str = "dependency_graph.json"):
        """Export graph for visualization."""
        graph_data = {
            "nodes": [],
            "edges": []
        }
        
        for file_path, node in self.graph.items():
            graph_data["nodes"].append({
                "id": file_path,
                "label": Path(file_path).name
            })
            
            for imported_file in node.imports:
                graph_data["edges"].append({
                    "from": file_path,
                    "to": imported_file
                })
        
        with open(output_file, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        logger.info(f"Graph exported to {output_file}")


# Singleton instance
_dependency_diplomat = None

def get_dependency_diplomat(ctx) -> DependencyDiplomat:
    """Get or create global Dependency Diplomat instance."""
    global _dependency_diplomat
    if _dependency_diplomat is None:
        _dependency_diplomat = DependencyDiplomat(ctx)
    return _dependency_diplomat