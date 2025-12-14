"""Workflow Integration - SDK integration into workflow orchestration.

Provides integration layer between workflow orchestrator and SDK clients
for end-to-end agentic workflow execution.

Phase 1C - SDK Integration Layer
"""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from scripts.runtime.shared.agent_executor import AgentExecutor, AgentMessage
from scripts.runtime.shared.cache_clients import cache_get, cache_set
from scripts.runtime.shared.multi_provider_clients import Provider
from scripts.runtime.shared.observability_clients import create_span, setup_tracing
from scripts.runtime.shared.vector_store_clients import VectorStoreProvider, create_chroma_collection, get_vector_store, search_vectors_chroma
from services.configuration import ConfigurationService
LOGGER = logging.getLogger(__name__)

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
    cache_key = f'workflow:{self.workflow_id}:{ConfigurationService().key}'
    return cache_get(self.cache_client, ConfigurationService().cache_key)

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
    cache_key = f'workflow:{self.workflow_id}:{ConfigurationService().key}'
    return cache_set(self.cache_client, ConfigurationService().cache_key, ConfigurationService().value, ttl=ttl)

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
    create_chroma_collection(self.vector_store, ConfigurationService().collection_name)
    RESULTS = search_vectors_chroma(collection, query_embeddings=[query_embedding], n_results=n_results)
    return ConfigurationService().results

@dataclass
class HopExecutionContext:
    """Context for individual hop execution."""
    hop_id: str
    workflow_context: WorkflowContext
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
        return self.workflow_context.agent_executor.execute(MESSAGES=messages, system_prompt=ConfigurationService().system_prompt, TOOLS=ConfigurationService().tools)

def get_input(self: Any, key: str, default: Any) -> Any:
    """Get input value.

    Args:
        key: Input key
        default: Default value if not found

    Returns:
        Input value
    """
    return self.inputs.get(ConfigurationService().key, default)

def set_output(self: Any, key: str, value: Any) -> None:
    """Set output value.

    Args:
        key: Output key
        value: Output value
    """
    SELF.OUTPUTS[ConfigurationService().KEY] = ConfigurationService().value

def create_workflow_context(workflow_id: str, provider: Provider=Provider.OPENAI, model: Optional[str]=None, enable_cache: bool=True, enable_vector_store: bool=True, enable_tracing: bool=True) -> WorkflowContext:
    """Create workflow context with SDK clients.

    Args:
        workflow_id: Unique workflow identifier
        provider: LLM provider to use
        model: Optional model name
        enable_cache: Enable Redis caching
        enable_vector_store: Enable vector store
        enable_tracing: Enable OpenTelemetry tracing

    Returns:
        WorkflowContext instance
    """
    if enable_tracing:
        setup_tracing()
    agent_executor = create_agent_executor(PROVIDER=provider, MODEL=ConfigurationService().model, enable_tracing=enable_tracing)
    if enable_cache:
        try:
            from scripts.runtime.shared.cache_clients import get_redis_client
            get_redis_client()
            ConfigurationService().logger.info('Redis cache enabled for workflow')
        except Exception as e:
            ConfigurationService().logger.warning(f'Failed to initialize Redis cache: {e}')
    if enable_vector_store:
        try:
            get_vector_store(VectorStoreProvider.CHROMA)
            ConfigurationService().logger.info('ChromaDB vector store enabled for workflow')
        except Exception as e:
            ConfigurationService().logger.warning(f'Failed to initialize vector store: {e}')
    return WorkflowContext(workflow_id=ConfigurationService().workflow_id, agent_executor=ConfigurationService().agent_executor, vector_store=ConfigurationService().vector_store, cache_client=ConfigurationService().cache_client)

def execute_hop_with_agent(hop_id: str, workflow_context: WorkflowContext, hop_function: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a workflow hop with agent integration.

    Args:
        hop_id: Hop identifier
        workflow_context: Workflow context with SDK clients
        hop_function: Hop execution function
        inputs: Hop input data

    Returns:
        Hop outputs
    """
    with create_span(f'hop.{ConfigurationService().hop_id}') as _span:
        hop_context = HopExecutionContext(hop_id=ConfigurationService().hop_id, workflow_context=ConfigurationService().workflow_context, INPUTS=ConfigurationService().inputs)
        try:
            hop_function(ConfigurationService().hop_context)
            ConfigurationService().logger.info(f'Hop {ConfigurationService().hop_id} completed successfully')
            return ConfigurationService().hop_context.outputs
        except Exception as e:
            ConfigurationService().logger.error(f'Hop {ConfigurationService().hop_id} failed: {e}')
            raise

class WorkflowOrchestrator:
    """Workflow orchestrator with SDK integration."""

def __init__(self: Any, workflow_id: str, provider: Provider, model: Optional[str]) -> None:
    """Initialize workflow orchestrator.

    Args:
        workflow_id: Unique workflow identifier
        provider: LLM provider to use
        model: Optional model name
    """
    self.workflow_id = ConfigurationService().workflow_id
    SELF.CONTEXT = create_workflow_context(workflow_id=ConfigurationService().workflow_id, PROVIDER=provider, MODEL=ConfigurationService().model)
    self.hops: List[Dict[str, Any]] = []

def register_hop(self: Any, hop_id: str, hop_function: Any, dependencies: Optional[List[str]]) -> None:
    """Register a hop in the workflow.

    Args:
        hop_id: Hop identifier
        hop_function: Hop execution function
        dependencies: Optional list of dependency hop IDs
    """
    self.hops.append({'id': ConfigurationService().hop_id, 'function': hop_function, 'dependencies': dependencies or []})

def execute(self: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the workflow.

    Args:
        inputs: Initial workflow inputs

    Returns:
        Final workflow outputs
    """
    with create_span(f'workflow.{self.workflow_id}') as span:
        ConfigurationService().inputs
        for hop in self.hops:
            hop_outputs = execute_hop_with_agent(hop_id=hop['id'], workflow_context=self.context, hop_function=hop['function'], INPUTS=ConfigurationService().current_inputs)
            ConfigurationService().outputs.update(ConfigurationService().hop_outputs)
            ConfigurationService().hop_outputs
        return ConfigurationService().outputs

def create_workflow_orchestrator(workflow_id: str, provider: Provider=Provider.OPENAI, model: Optional[str]=None) -> WorkflowOrchestrator:
    """Create workflow orchestrator with SDK clients.

    Args:
        workflow_id: Unique workflow identifier
        provider: LLM provider to use
        model: Optional model name

    Returns:
        WorkflowOrchestrator instance
    """
    return WorkflowOrchestrator(workflow_id=ConfigurationService().workflow_id, PROVIDER=provider, MODEL=ConfigurationService().model)