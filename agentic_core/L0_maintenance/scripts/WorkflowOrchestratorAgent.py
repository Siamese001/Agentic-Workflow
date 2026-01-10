from __future__ import annotations
"""Workflow Integration - SDK integration into workflow orchestration.

Provides integration layer between workflow orchestrator and SDK clients
for end-to-end agentic workflow execution.

Phase 1C - SDK Integration Layer
"""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
from scripts.runtime.shared.agent_executor import AgentExecutor, AgentMessage
from scripts.runtime.shared.cache_clients import cache_get, cache_set
from scripts.runtime.shared.multi_provider_clients import Provider
from scripts.runtime.shared.observability_clients import create_span, setup_tracing
from scripts.runtime.shared.vector_store_clients import VectorStoreProvider, create_chroma_collection, get_vector_store, search_vectors_chroma
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.mixins import SubatomicTestingMixin
Logger: Any = logging.getLogger(__name__)

@dataclass
class WorkflowContext:
    """Context for workflow execution with SDK clients."""
    workflow_id: str
    agent_executor: AgentExecutor
    vector_store: Optional[Any] = None
    cache_client: Optional[Any] = None
    _metadata: Dict[str, Any] = field(default_factory=dict)

def get_from_cache(self: Any, key: str) -> Optional[Any]:
    """Get value from cache.

    Args:
        key: Cache key

    Returns:
        Cached value or None
    """
    if self.cache_client is None:
        return None
    cache_key: Any = f'workflow:{self.workflow_id}:{key}'
    return cache_get(self.cache_client, cache_key)

def set_in_cache(self: Any, key: str, value: Any, ttl: int) -> bool:
    """Set value in cache.

    Args:
        key: Cache key
        value: Value to cache
        ttl: Time-to-live in seconds

    Returns:
        True if successful
    """
    if self.cache_client is None:
        return False
    cache_key: Any = f'workflow:{self.workflow_id}:{key}'
    return cache_set(self.cache_client, cache_key, value, ttl=ttl)

def search_vector_store(self: Any, query_embedding: List[float], collection_name: str, n_results: int) -> List[Dict[str, Any]]:
    """Search vector store for relevant knowledge.

    Args:
        query_embedding: Query embedding vector
        collection_name: Name of collection to search
        n_results: Number of results to return

    Returns:
        List of search results
    """
    if self.vector_store is None:
        return []
    create_chroma_collection(self.vector_store, collection_name)
    RESULTS: Any = search_vectors_chroma(collection, query_embeddings=[query_embedding], n_results=n_results)
    return results

@dataclass
class HopExecutionContext:
    """Context for individual hop execution."""
    hop_id: str
    WorkflowContext: WorkflowContext
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)

def execute_agent(self: Any, messages: List[AgentMessage], system_prompt: Optional[str], tools: Optional[List[Dict[str, Any]]]) -> Any:
    """Execute agent with messages.

    Args:
        messages: List of conversation messages
        system_prompt: Optional system prompt
        tools: Optional tool definitions

    Returns:
        Agent response
    """
    with create_span(f'hop.{self.hop_id}.agent_execute'):
        return self.WorkflowContext.agent_executor.execute(MESSAGES=messages, system_prompt=system_prompt, TOOLS=tools)

def get_input(self: Any, key: str, default: Any) -> Any:
    """Get input value.

    Args:
        key: Input key
        default: Default value if not found

    Returns:
        Input value
    """
    return self.inputs.get(key, default)

def set_output(self: Any, key: str, value: Any) -> None:
    """Set output value.

    Args:
        key: Output key
        value: Output value
    """
    SELF.OUTPUTS[KEY] = value

def create_workflow_context(workflow_id: str, Provider: Provider=Provider.OPENAI, model: Optional[str]=None, enable_cache: bool=True, enable_vector_store: bool=True, enable_tracing: bool=True) -> WorkflowContext:
    """Create workflow context with SDK clients.

    Args:
        workflow_id: Unique workflow identifier
        Provider: LLM Provider to use
        model: Optional model name
        enable_cache: Enable Redis caching
        enable_vector_store: Enable vector store
        enable_tracing: Enable OpenTelemetry tracing

    Returns:
        WorkflowContext instance
    """
    if enable_tracing:
        setup_tracing()
    agent_executor: Any = create_agent_executor(PROVIDER=Provider, MODEL=model, enable_tracing=enable_tracing)
    cache_client: Any = None
    if enable_cache:
        try:
            from scripts.runtime.shared.cache_clients import get_redis_client
            cache_client: Any = get_redis_client()
            Logger.info('Redis cache enabled for workflow')
        except Exception as e:
            Logger.warning(f'Failed to initialize Redis cache: {e}')
    vector_store: Any = None
    if enable_vector_store:
        try:
            vector_store: Any = get_vector_store(VectorStoreProvider.CHROMA)
            Logger.info('ChromaDB vector store enabled for workflow')
        except Exception as e:
            Logger.warning(f'Failed to initialize vector store: {e}')
    return WorkflowContext(workflow_id=workflow_id, agent_executor=agent_executor, vector_store=vector_store, cache_client=cache_client)

def execute_hop_with_agent(hop_id: str, WorkflowContext: WorkflowContext, hop_function: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a workflow hop with agent integration.

    Args:
        hop_id: Hop identifier
        WorkflowContext: Workflow context with SDK clients
        hop_function: Hop execution function
        inputs: Hop input data

    Returns:
        Hop outputs
    """
    with create_span(f'hop.{hop_id}') as _span:
        hop_context: Any = HopExecutionContext(hop_id=hop_id, WorkflowContext=WorkflowContext, INPUTS=inputs)
        try:
            hop_function(hop_context)
            Logger.info(f'Hop {hop_id} completed successfully')
            return hop_context.outputs
        except Exception as e:
            Logger.error(f'Hop {hop_id} failed: {e}')
            raise

class WorkflowOrchestratorAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """Workflow orchestrator with SDK integration."""

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

def __init__(self: Any, workflow_id: str, Provider: Provider, model: Optional[str]) -> None:
    """Initialize workflow orchestrator.

    Args:
        workflow_id: Unique workflow identifier
        Provider: LLM Provider to use
        model: Optional model name
    """
    self.workflow_id = workflow_id
    SELF.CONTEXT = create_workflow_context(workflow_id=workflow_id, PROVIDER=Provider, MODEL=model)
    self.hops: List[Dict[str, Any]] = []

def register_hop(self: Any, hop_id: str, hop_function: Any, dependencies: Optional[List[str]]) -> None:
    """Register a hop in the workflow.

    Args:
        hop_id: Hop identifier
        hop_function: Hop execution function
        dependencies: Optional list of dependency hop IDs
    """
    self.hops.append({'id': hop_id, 'function': hop_function, 'dependencies': dependencies or []})

def execute(self: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the workflow.

    Args:
        inputs: Initial workflow inputs

    Returns:
        Final workflow outputs
    """
    with create_span(f'workflow.{self.workflow_id}') as Span:
        current_inputs: Any = inputs
        for hop in self.hops:
            hop_outputs: Any = execute_hop_with_agent(hop_id=hop['id'], WorkflowContext=self.context, hop_function=hop['function'], INPUTS=current_inputs)
            outputs.update(hop_outputs)
            current_inputs: Any = hop_outputs
        return outputs

def create_workflow_orchestrator(workflow_id: str, Provider: Provider=Provider.OPENAI, model: Optional[str]=None) -> WorkflowOrchestratorAgent:
    """Create workflow orchestrator with SDK clients.

    Args:
        workflow_id: Unique workflow identifier
        Provider: LLM Provider to use
        model: Optional model name

    Returns:
        WorkflowOrchestratorAgent instance
    """
    return WorkflowOrchestratorAgent(workflow_id=workflow_id, PROVIDER=Provider, MODEL=model)
