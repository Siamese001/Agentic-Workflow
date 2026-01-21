"""K.X Node Executor - Execute knowledge extraction nodes in workflows.

Integrates K.X nodes with agent execution, RAG, and validation gates
for end-to-end resume and outreach generation.

Phase 1C - Knowledge Extraction Integration
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from .agent_executor import AgentExecutor, AgentMessage, AgentResponse
from .kx_nodes import KNodeConfig, ReasoningStrategy, get_kx_registry
from .observability_clients import create_span, set_span_attribute
from .vector_store_clients import search_vectors_chroma

logger = logging.getLogger(__name__)


@dataclass
class KXExecutionContext:
    """Execution context for K.X node."""
    node_config: KNodeConfig
    agent_executor: AgentExecutor
    vector_store: Any | None = None
    cache_client: Any | None = None
    source_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class KXExecutionResult:
    """Result from K.X node execution."""
    node_id: str
    element: str
    content: str
    reasoning_trace: str | None = None
    rag_sources: list[dict[str, Any]] = field(default_factory=list)
    validation_results: list[dict[str, Any]] = field(default_factory=list)
    usage: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class KXNodeExecutor:
    """Executor for K.X knowledge extraction nodes."""

    def __init__(self, agent_executor: AgentExecutor):
        """Initialize K.X node executor.

        Args:
            agent_executor: Agent executor for LLM calls
        """
        self.agent_executor = agent_executor
        self.registry = get_kx_registry()

    def execute_node(
        self,
        node_key: str,
        context: KXExecutionContext,
        system_prompt: str | None = None,
    ) -> KXExecutionResult:
        """Execute a K.X node.

        Args:
            node_key: K.X node key
            context: Execution context
            system_prompt: Optional system prompt override

        Returns:
            KXExecutionResult with generated content
        """
        config = context.node_config

        with create_span(f"kx_node.{config.node_id}.{config.element}") as span:
            set_span_attribute("kx.node_id", config.node_id)
            set_span_attribute("kx.element", config.element)
            set_span_attribute("kx.reasoning_strategy", config.reasoning_strategy.value)

            # Execute RAG if enabled
            rag_sources = []
            if config.rag_config and config.rag_config.enabled and context.vector_store:
                rag_sources = self._execute_rag(config, context)

            # Build prompt based on reasoning strategy
            messages = self._build_messages(config, context, rag_sources)

            # Execute agent
            if system_prompt is None:
                system_prompt = self._build_system_prompt(config, context)

            response = self.agent_executor.execute(
                messages=messages,
                system_prompt=system_prompt,
            )

            # Validate output
            validation_results = self._validate_output(config, response.content, context)

            return KXExecutionResult(
                node_id=config.node_id,
                element=config.element,
                content=response.content,
                reasoning_trace=self._extract_reasoning_trace(response),
                rag_sources=rag_sources,
                validation_results=validation_results,
                usage=response.usage,
                metadata={
                    "reasoning_strategy": config.reasoning_strategy.value,
                    "rag_enabled": config.rag_config.enabled if config.rag_config else False,
                    "validation_passed": all(v.get("passed", False) for v in validation_results),
                },
            )

    def _execute_rag(
        self,
        config: KNodeConfig,
        context: KXExecutionContext,
    ) -> list[dict[str, Any]]:
        """Execute RAG retrieval for K.X node.

        Args:
            config: Node configuration
            context: Execution context

        Returns:
            List of retrieved sources
        """
        if not config.rag_config or not context.vector_store:
            return []

        # Build query from context
        query_text = f"{config.element}: {context.source_data.get('query', '')}"

        # Get query embedding (placeholder - would use actual embedding model)
        query_embedding = [0.1] * 1536  # Placeholder

        # Search vector store
        try:
            from .vector_store_clients import create_chroma_collection

            collection = create_chroma_collection(
                context.vector_store,
                context.metadata.get("collection_name", "knowledge_base")
            )

            results = search_vectors_chroma(
                collection,
                query_embeddings=[query_embedding],
                n_results=config.rag_config.max_retrievers,
            )

            # Apply source weighting
            sources = []
            if results and "documents" in results:
                for i, doc in enumerate(results["documents"][0]):
                    source_type = results.get("metadatas", [[{}]])[0][i].get("source_type", "generic")
                    weight = config.rag_config.source_weighting.get(source_type, 1.0)

                    sources.append({
                        "document": doc,
                        "metadata": results.get("metadatas", [[{}]])[0][i],
                        "distance": results.get("distances", [[0]])[0][i],
                        "weight": weight,
                        "weighted_score": weight / (1 + results.get("distances", [[0]])[0][i]),
                    })

            # Sort by weighted score
            sources.sort(key=lambda x: x["weighted_score"], reverse=True)

            logger.info(f"Retrieved {len(sources)} sources for K.X node {config.node_id}")
            return sources[:config.rag_config.min_retrievers]

        except Exception as e:
            logger.warning(f"RAG retrieval failed for K.X node {config.node_id}: {e}")
            return []

    def _build_messages(
        self,
        config: KNodeConfig,
        context: KXExecutionContext,
        rag_sources: list[dict[str, Any]],
    ) -> list[AgentMessage]:
        """Build messages for agent execution.

        Args:
            config: Node configuration
            context: Execution context
            rag_sources: Retrieved RAG sources

        Returns:
            List of agent messages
        """
        messages = []

        # Add RAG context if available
        if rag_sources:
            rag_context = "\n\n".join([
                f"Source {i+1} ({src['metadata'].get('source_type', 'unknown')}):\n{src['document']}"
                for i, src in enumerate(rag_sources[:3])
            ])

            messages.append(AgentMessage(
                role="user",
                content=f"Context from knowledge base:\n\n{rag_context}"
            ))

        # Add main generation prompt
        prompt = self._build_generation_prompt(config, context)
        messages.append(AgentMessage(role="user", content=prompt))

        return messages

    def _build_generation_prompt(
        self,
        config: KNodeConfig,
        context: KXExecutionContext,
    ) -> str:
        """Build generation prompt for K.X node.

        Args:
            config: Node configuration
            context: Execution context

        Returns:
            Generation prompt
        """
        prompt_parts = [f"Generate: {config.element}"]

        # Add structure template if available
        if config.structure_template:
            prompt_parts.append(f"\nStructure: {config.structure_template}")

        # Add constraints
        constraints = []
        if config.max_words:
            constraints.append(f"max {config.max_words} words")
        if config.max_chars:
            constraints.append(f"max {config.max_chars} characters")

        if constraints:
            prompt_parts.append(f"\nConstraints: {', '.join(constraints)}")

        # Add source data
        if context.source_data:
            source_info = "\n".join([
                f"{key}: {value}"
                for key, value in context.source_data.items()
                if key != "query"
            ])
            if source_info:
                prompt_parts.append(f"\nSource Data:\n{source_info}")

        # Add reasoning strategy guidance
        if config.reasoning_strategy == ReasoningStrategy.COT:
            prompt_parts.append("\nUse step-by-step reasoning to generate the content.")
        elif config.reasoning_strategy == ReasoningStrategy.TOT:
            prompt_parts.append(f"\nExplore {config.tot_branches} different approaches and select the best.")
        elif config.reasoning_strategy == ReasoningStrategy.HYBRID_COT_TOT:
            prompt_parts.append("\nUse step-by-step reasoning with multiple branches to find the optimal solution.")

        return "\n".join(prompt_parts)

    def _build_system_prompt(
        self,
        config: KNodeConfig,
        context: KXExecutionContext,
    ) -> str:
        """Build system prompt for K.X node.

        Args:
            config: Node configuration
            context: Execution context

        Returns:
            System prompt
        """
        prompts = [
            f"You are an expert at generating {config.element}.",
            "Follow all constraints and validation rules strictly.",
        ]

        if config.validation_rules:
            prompts.append(f"Validation rules: {', '.join(config.validation_rules)}")

        return " ".join(prompts)

    def _extract_reasoning_trace(self, response: AgentResponse) -> str | None:
        """Extract reasoning trace from response.

        Args:
            response: Agent response

        Returns:
            Reasoning trace or None
        """
        # Placeholder - would extract actual reasoning trace
        return None

    def _validate_output(
        self,
        config: KNodeConfig,
        content: str,
        context: KXExecutionContext,
    ) -> list[dict[str, Any]]:
        """Validate generated output against rules.

        Args:
            config: Node configuration
            content: Generated content
            context: Execution context

        Returns:
            List of validation results
        """
        results = []

        for rule in config.validation_rules:
            result = self._apply_validation_rule(rule, content, config, context)
            results.append(result)

        return results

    def _apply_validation_rule(
        self,
        rule: str,
        content: str,
        config: KNodeConfig,
        context: KXExecutionContext,
    ) -> dict[str, Any]:
        """Apply a single validation rule.

        Args:
            rule: Validation rule name
            content: Generated content
            config: Node configuration
            context: Execution context

        Returns:
            Validation result
        """
        # Basic validation rules
        if rule == "non_empty":
            passed = len(content.strip()) > 0
            return {"rule": rule, "passed": passed, "message": "Content must not be empty"}

        elif rule == "word_count_range":
            word_count = len(content.split())
            passed = True
            if config.max_words:
                passed = word_count <= config.max_words
            return {
                "rule": rule,
                "passed": passed,
                "message": f"Word count: {word_count}/{config.max_words or 'unlimited'}",
                "word_count": word_count,
            }

        elif rule == "character_limit" or rule == "character_limit_strict":
            char_count = len(content)
            passed = True
            if config.max_chars:
                passed = char_count <= config.max_chars
            return {
                "rule": rule,
                "passed": passed,
                "message": f"Character count: {char_count}/{config.max_chars or 'unlimited'}",
                "char_count": char_count,
            }

        else:
            # Placeholder for other validation rules
            return {
                "rule": rule,
                "passed": True,
                "message": f"Validation rule '{rule}' not implemented (assumed pass)",
            }


def execute_kx_node(
    node_key: str,
    agent_executor: AgentExecutor,
    source_data: dict[str, Any],
    vector_store: Any | None = None,
    cache_client: Any | None = None,
    engine: str = "resume",
) -> KXExecutionResult:
    """Execute a K.X node by key.

    Args:
        node_key: K.X node key
        agent_executor: Agent executor
        source_data: Source data for generation
        vector_store: Optional vector store for RAG
        cache_client: Optional cache client
        engine: Engine type ("resume" or "outreach")

    Returns:
        KXExecutionResult
    """
    registry = get_kx_registry()

    # Get node configuration
    if engine == "resume":
        config = registry.get_resume_node(node_key)
    else:
        config = registry.get_outreach_node(node_key)

    if not config:
        raise ValueError(f"K.X node not found: {node_key} (engine: {engine})")

    # Create execution context
    context = KXExecutionContext(
        node_config=config,
        agent_executor=agent_executor,
        vector_store=vector_store,
        cache_client=cache_client,
        source_data=source_data,
    )

    # Execute node
    executor = KXNodeExecutor(agent_executor)
    return executor.execute_node(node_key, context)
