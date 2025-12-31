"""
Dynamic Tool Registry for Runtime Tool Discovery

Allows agents to discover and request tools dynamically based on task requirements,
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
logger: Any = logging.getLogger(__name__)

@dataclass
class tool_definition:
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

@dataclass
class tool_match:
    """A matched tool for a task."""
    tool: ToolDefinition
    relevance_score: float
    reason: str

class tool_registry:
    """
    Dynamic tool registry that enables agents to discover tools at runtime.

    Uses semantic similarity to match task descriptions to tool capabilities.
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
        Find tools relevant to a task using semantic search.

        Args:
            task_description: Description of the task
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

    def _generate_match_reason(self, task: str, tool: ToolDefinition, similarity: float) -> str:
        """Generate a reason why this tool matches the task."""
        task_lower = task.lower()
        desc_lower = tool.description.lower()
        name_lower = tool.name.lower()
        reasons = []
        if any((word in desc_lower for word in task_lower.split())):
            reasons.append('description contains task keywords')
        if any((word in name_lower for word in task_lower.split())):
            reasons.append('name matches task keywords')
        if 'file' in task_lower and tool.category == 'filesystem':
            reasons.append('file operation tool')
        elif 'api' in task_lower and tool.category == 'network':
            reasons.append('API communication tool')
        elif 'data' in task_lower and tool.category == 'analysis':
            reasons.append('data analysis tool')
        if not reasons:
            reasons.append(f'semantic similarity ({similarity:.2f})')
        return '; '.join(reasons)

    async def get_tool_recommendations(self, task: str, context: Optional[Dict[str, Any]]=None) -> str:
        """
        Get natural language tool recommendations for a task.

        Args:
            task: Task description
            context: Optional execution context

        Returns:
            Formatted recommendation string
        """
        matches: Any = await self.find_tools_for_task(task)
        if not matches:
            return 'No specific tools found for this task.\n                . You may need to implement a custom solution.\n                .'
        recommendation: Any = f"Recommended tools for '{task}':\n\n"
        for i, match in enumerate(matches, 1):
            tool: Any = match.tool
            recommendation += f'{i}. {tool.name}\n'
            recommendation += f'   Description: {tool.description}\n'
            recommendation += f'   Relevance: {match.relevance_score:.2f}\n'
            recommendation += f'   Reason: {match.reason}\n'
            if tool.parameters:
                recommendation += f'   Parameters: {json.dumps(tool.parameters, indent=6)}\n'
            recommendation += '\n'
        return recommendation

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
