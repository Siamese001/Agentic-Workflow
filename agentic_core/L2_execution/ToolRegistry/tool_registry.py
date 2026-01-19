from __future__ import annotations
"""
Dynamic Tool Registry for Runtime Tool Discovery

Allows agents to discover and request tools dynamically based on Task requirements,
rather than being hardcoded with a fixed set of tools.
"""
import inspect
import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Protocol
import numpy as np
Logger: Any = logging.getLogger(__name__)

@dataclass
class ToolDefinition:
    """Definition of a tool in the registry."""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]
    tags: List[str] = field(default_factory=list)
    category: str = 'general'
    embedding: Optional[List[float]] = None
    usage_count: int = 0
    success_rate: float = 1.0

# Alias for consistency
ToolDefinition = ToolDefinition

@dataclass
class ToolMatch:
    """A matched tool for a Task."""
    tool: ToolDefinition
    relevance_score: float
    reason: str

# Alias for consistency
ToolMatch = ToolMatch

class ToolRegistry:
    """
    Dynamic tool registry that enables agents to discover tools at runtime.

    Uses semantic similarity to match Task descriptions to tool capabilities.
    """

    def __init__(self, embedder, enable_caching: bool=True):
        """
        Initialize the tool registry.

        Args:
            embedder: Embedding function
            enable_caching: Whether to cache tool embeddings
        """
        self.embedder = embedder
        self.enable_caching = enable_caching
        self.tools: Dict[str, ToolDefinition] = {}
        self._embedding_matrix: Optional[np.ndarray] = None
        self._tool_names: List[str] = []
        LOGGER.info('Tool registry initialized')

    def register(self, name: str, func: Callable, description: str, parameters: Optional[Dict[str, Any]]=None, tags: Optional[List[str]]=None, category: str='general') -> None:
        """
        Register a tool in the registry.

        Args:
            name: Unique tool name
            func: The tool function
            description: What the tool does
            parameters: Parameter schema
            tags: Optional tags for categorization
            category: Tool category
        """
        if name in self.tools:
            LOGGER.warning(f'Tool {name} already registered, overwriting')
        if not description:
            description: Any = self._generate_description_from_func(func)
        if not parameters:
            parameters: Any = self._generate_parameters_from_func(func)
        tool: Any = ToolDefinition(name=name, description=description, function=func, parameters=parameters, tags=tags or [], category=category)
        self.tools[name] = tool
        LOGGER.info(f'Registered tool: {name} ({category})')

    async def find_tools_for_task(self, task_description: str, max_tools: int=5, min_relevance: float=0.6, categories: Optional[List[str]]=None) -> List[ToolMatch]:
        """
        Find tools relevant to a Task using semantic search.

        Args:
            task_description: Description of the Task
            max_tools: Maximum number of tools to return
            min_relevance: Minimum relevance score
            categories: Optional category filter

        Returns:
            List of matched tools with relevance scores
        """
        if not self.tools:
            return []
        await self._ensure_embeddings()
        task_embedding: Any = await self.embedder.embed_query(task_description)
        task_vec: Any = np.array(task_embedding)
        matches: Any = []
        for i, tool_name in enumerate(self._tool_names):
            tool: Any = self.tools[tool_name]
            if categories and tool.category not in categories:
                continue
            tool_vec: Any = self._embedding_matrix[i]
            similarity: Any = np.dot(task_vec, tool_vec) / (np.linalg.norm(task_vec) * np.linalg.norm(tool_vec))
            if similarity >= min_relevance:
                reason: Any = self._generate_match_reason(task_description, tool, similarity)
                matches.append(ToolMatch(tool=tool, relevance_score=similarity, reason=reason))
        matches.sort(key=lambda x: x.relevance_score, reverse=True)
        return matches[:max_tools]

    async def _ensure_embeddings(self):
        """Ensure tool embeddings are computed."""
        if self._embedding_matrix is not None:
            return
        LOGGER.debug('Computing tool embeddings...')
        embeddings = []
        tool_names = []
        for tool in self.tools.values():
            searchable_text = f"{tool.name} {tool.description} {' '.join(tool.tags)}"
            embedding = await self.embedder.embed_query(searchable_text)
            embeddings.append(embedding)
            tool_names.append(tool.name)
            tool.embedding = embedding
        self._embedding_matrix = np.array(embeddings)
        self._tool_names = tool_names
        LOGGER.debug(f'Computed embeddings for {len(embeddings)} tools')

    def _generate_match_reason(self, Task: str, tool: ToolDefinition, similarity: float) -> str:
        """Generate a reason why this tool matches the Task."""
        task_lower = Task.lower()
        desc_lower = tool.description.lower()
        name_lower = tool.name.lower()
        reasons = []
        if any((word in desc_lower for word in task_lower.split())):
            reasons.append('description contains Task keywords')
        if any((word in name_lower for word in task_lower.split())):
            reasons.append('name matches Task keywords')
        if 'file' in task_lower and tool.category == 'filesystem':
            reasons.append('file operation tool')
        elif 'api' in task_lower and tool.category == 'network':
            reasons.append('API communication tool')
        elif 'data' in task_lower and tool.category == 'analysis':
            reasons.append('data analysis tool')
        if not reasons:
            reasons.append(f'semantic similarity ({similarity:.2f})')
        return '; '.join(reasons)

    async def get_tool_recommendations(self, Task: str, context: Optional[Dict[str, Any]]=None) -> str:
        """
        Get natural language tool recommendations for a Task.

        Args:
            Task: Task description
            context: Optional execution context

        Returns:
            Formatted Recommendation string
        """
        matches: Any = await self.find_tools_for_task(Task)
        if not matches:
            return 'No specific tools found for this Task.\n                . You may need to implement a custom solution.\n                .'
        Recommendation: Any = f"Recommended tools for '{Task}':\n\n"
        for i, match in enumerate(matches, 1):
            tool: Any = match.tool
            Recommendation += f'{i}. {tool.name}\n'
            Recommendation += f'   Description: {tool.description}\n'
            Recommendation += f'   Relevance: {match.relevance_score:.2f}\n'
            Recommendation += f'   Reason: {match.reason}\n'
            if tool.parameters:
                Recommendation += f'   Parameters: {json.dumps(tool.parameters, indent=6)}\n'
            Recommendation += '\n'
        return Recommendation

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self, category: Optional[str]=None, tags: Optional[List[str]]=None) -> List[ToolDefinition]:
        """List all tools, optionally filtered."""
        tools_list: Any = list(self.tools.values())
        if category:
            tools_list: Any = [t for t in tools_list if t.category == category]
        if tags:
            tools_list: Any = [t for t in tools_list if any((tag in t.tags for tag in tags))]
        return tools_list

    def update_tool_stats(self, name: str, success: bool) -> Any:
        """Update tool usage statistics."""
        if name in self.tools:
            tool: Any = self.tools[name]
            tool.usage_count += 1
            alpha: Any = 0.1
            if success:
                tool.success_rate = tool.success_rate * (1 - alpha) + 1 * alpha
            else:
                tool.success_rate = tool.success_rate * (1 - alpha) + 0 * alpha

    def _generate_description_from_func(self, func: Callable) -> str:
        """Generate description from function docstring."""
        if func.__doc__:
            return func.__doc__.strip()
        return f'Function: {func.__name__}'

    def _generate_parameters_from_func(self, func: Callable) -> Dict[str, Any]:
        """Generate parameter schema from function signature."""
        sig = inspect.signature(func)
        parameters_schema = {}
        for name, param in sig.parameters.items():
            param_info = {'type': 'unknown'}
            if param.annotation != inspect.Parameter.empty:
                param_info['type'] = str(param.annotation)
            if param.default == inspect.Parameter.empty:
                param_info['required'] = True
            else:
                param_info['default'] = str(param.default)
            parameters_schema[name] = param_info
        return parameters_schema

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        categories_count: Any = {}
        for tool in self.tools.values():
            categories_count[tool.category] = categories_count.get(tool.category, 0) + 1
        return {'total_tools': len(self.tools), 'categories': categories_count, 'most_used': max(self.tools.values(), key=lambda t: t.usage_count).name if self.tools else None, 'avg_success_rate': np.mean([t.success_rate for t in self.tools.values()]) if self.tools else 0.0}

predefined_tool_categories: Any = {'filesystem': 'File and directory operations', 'network': 'Network and API communication', 'analysis': 'Data analysis and processing', 'utility': 'General utility functions', 'mcp': 'Model Context Protocol tools', 'ai': 'AI/ML related tools'}

def ast_analysis(code: str, mode: str = "audit_classes") -> Dict[str, Any]:
    """AST tool — analyze Python code for patterns (e.g., snake_case classes).
    
    Args:
        code: Python source code to analyze
        mode: Analysis mode - "audit_classes", "extract_names", "check_snake_case"
        
    Returns:
        Dict with analysis results based on mode
    """
    import ast
    
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {"error": "syntax_error", "message": "Invalid Python syntax"}
    
    if mode == "audit_classes":
        # Count snake_case vs PascalCase classes
        snake_classes = sum(
            1 for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and (node.name[0].islower() or '_' in node.name)
        )
        pascal_classes = sum(
            1 for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and node.name[0].isupper() and '_' not in node.name
        )
        return {
            "snake_classes": snake_classes,
            "pascal_classes": pascal_classes,
            "total_classes": snake_classes + pascal_classes
        }
    
    elif mode == "extract_names":
        # Extract all class names
        class_names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        ]
        return {"class_names": class_names, "count": len(class_names)}
    
    elif mode == "check_snake_case":
        # Check if any snake_case classes exist
        has_violations = any(
            isinstance(node, ast.ClassDef) and (node.name[0].islower() or '_' in node.name)
            for node in ast.walk(tree)
        )
        return {"has_snake_case": has_violations}
    
    return {"error": "invalid_mode", "message": f"Unknown mode: {mode}"}

# =============================================================================
# CODE TRANSFORMATION ENGINE (CTE) — Phase 1 Tool
# =============================================================================
from archives.location_violations.code_transform import (
    CodeTransformArgs,
    TransformOperation,
    code_transform,
    rename_symbol,
    extract_function,
)


def code_transform_tool(args: CodeTransformArgs) -> Dict[str, Any]:
    """
    Deterministic AST-based code transformation tool.
    
    Enables agents to perform safe, syntax-preserving code transformations
    without LLM overhead. Supports rename, extract, decorator operations.
    
    Args:
        args: CodeTransformArgs with operation details
            - operation: "rename_symbol", "extract_function", "add_decorator", etc.
            - code: Source code to transform
            - target: Symbol name or line range
            - new_name: New name for rename operations
            - extract_name: Name for extracted function
            - line_start/line_end: Line range for extraction
            
    Returns:
        Dict with success status, transformed code, and change details
        
    Example:
        >>> args = CodeTransformArgs(
        ...     operation=TransformOperation.RENAME_SYMBOL,
        ...     code="def foo(): pass",
        ...     target="foo",
        ...     new_name="bar"
        ... )
        >>> result = code_transform_tool(args)
        >>> result["transformed_code"]
        'def bar(): pass'
    """
    return code_transform(args)


# Add CTE to predefined categories
predefined_tool_categories['code_manipulation'] = 'AST-based code transformation tools'


# =============================================================================
# DEPENDENCY GRAPH ANALYZER (DGA) — Phase 2 Tool
# =============================================================================
from agentic_core.L2_execution.ToolRegistry.tools.DependencyGraph import (
    DependencyGraphArgs,
    GraphOperation,
    DependencyGraph,
    quick_cycles,
    quick_impact,
)


def dependency_graph_tool(args: DependencyGraphArgs) -> Dict[str, Any]:
    """
    Dependency graph analysis tool for import/call relationships.
    
    Enables agents to analyze code dependencies for:
    - Cycle detection (circular imports)
    - Impact analysis (what breaks if X changes)
    - Unused import detection
    
    Args:
        args: DependencyGraphArgs with operation details
            - operation: "build_graph", "detect_cycles", "ImpactAnalysis", etc.
            - target_path: File or directory to analyze
            - symbol: Symbol name for impact analysis
            
    Returns:
        Dict with graph data, cycles, or impact analysis results
        
    Example:
        >>> args = DependencyGraphArgs(
        ...     operation=GraphOperation.DETECT_CYCLES,
        ...     target_path="agentic_core/"
        ... )
        >>> result = dependency_graph_tool(args)
        >>> result["data"]["has_cycles"]
        False
    """
    return DependencyGraph(args)


# Add DGA to predefined categories
predefined_tool_categories['analysis'] = 'Code analysis and dependency tools'


# =============================================================================
# DIFF/PATCH GENERATOR (DPG) — Phase 2 Tool
# =============================================================================
from archives.location_violations.diff_generator import (
    DiffGeneratorArgs,
    DiffFormat,
    generate_diff,
    apply_patch,
    validate_patch,
)


def diff_generator_tool(args: DiffGeneratorArgs) -> Dict[str, Any]:
    """
    Diff/patch generation tool for reviewable changes.
    
    Enables agents to generate human-reviewable diffs before applying changes,
    supporting human-in-loop validation for high-risk operations.
    
    Args:
        args: DiffGeneratorArgs with diff parameters
            - original: Original code/text
            - modified: Modified code/text
            - format: "unified", "context", "html", "ndiff"
            
    Returns:
        Dict with diff text, stats, and patch applicability
        
    Example:
        >>> args = DiffGeneratorArgs(
        ...     original="def foo(): pass",
        ...     modified="def bar(): pass",
        ...     format=DiffFormat.UNIFIED
        ... )
        >>> result = diff_generator_tool(args)
        >>> print(result["diff"])
    """
    return generate_diff(args)


def create_tool_registry(embedder: Any, enable_caching: bool=True) -> ToolRegistry:
    """
    Factory function to create a tool registry.

    Args:
        embedder: Embedding function
        enable_caching: Whether to enable caching

    Returns:
        ToolRegistry instance
    """
    return ToolRegistry(embedder=embedder, enable_caching=enable_caching)
