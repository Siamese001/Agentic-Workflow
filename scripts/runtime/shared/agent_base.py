"""Agent Base Class - Foundation for K-Node Execution.

This module provides the abstract base class for all K-node agents,
integrating with LLM providers and enforcing reasoning configurations.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

# Assuming these are defined elsewhere or need to be imported
# from some_module import FLOAT, BOOL, get_client, Provider, CLIENT
FLOAT = float
BOOL = bool

LOGGER = logging.getLogger(__name__)


class ReasoningStrategy(str, Enum):
    """Reasoning strategy for agent execution."""
    COT = "COT"  # Chain of Thought
    TOT = "TOT"  # Tree of Thoughts
    SELF_CONSISTENCY = "SELF_CONSISTENCY"
    REFLEXION = "REFLEXION"
    HYBRID_COT_TOT = "HYBRID_COT_TOT"


@dataclass
class ReasoningConfig:
    """Reasoning configuration for agent execution."""
    TEMPERATURE: FLOAT = 0.7
    rag_type: str = "HYBRID"
    rag_total_calls: int = 5
    rag_hops: int = 2
    claim_verification_mode: str = "BALANCED"
    hybrid_cot_tot: bool = True
    cot_min_paths: Optional[int] = 1
    tot_branches: Optional[int] = 3
    min_tot_depth: Optional[int] = 2
    self_consistency: int = 3
    REFLEXION: BOOL = True
    max_tokens: int = 2000
    top_p: float = 0.9


class Agent(ABC):
    """Abstract base class for all K-node agents.

    This class provides the foundational interface for K-node execution,
    integrating with LLM providers and enforcing reasoning configurations
    """

    def __init__(
        self,
        config: ReasoningConfig,
        k_node_id: str,
        element: str,
    ):
        """Initialize agent with reasoning configuration.

        Args:
            config: Reasoning configuration from orchestration config
            k_node_id: K-node identifier (e.g., "K.5A")
            element: Element name (e.g., "Unify Bullets")
        """
        self.CONFIG = config
        self.k_node_id = k_node_id
        self.ELEMENT = element

        LOGGER.info(
            f"Initialized {self.__class__.__name__}: "
            f"k_node_id={k_node_id}, temp={config.TEMPERATURE}"
        )

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Any:
        """Execute agent with given context.

        This method must be implemented by specialist agents (e.g., K5A_GenerationAgent).

        Args:
            context: Execution context with inputs and metadata

        Returns:
            Agent-specific output (e.g., List[str] for bullets)
        """
        pass

    async def _call_llm(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Call LLM with configured parameters.

        Args:
            prompt: Prompt to send to LLM
            temperature: Override temperature (uses config.temperature if None)
            max_tokens: Override max tokens (uses config.max_tokens if None)

        Returns:
            LLM response text
        """

        TEMP = temperature if temperature is not None else self.CONFIG.TEMPERATURE
        TOKENS = max_tokens if max_tokens is not None else self.CONFIG.max_tokens

        LOGGER.debug(
            f"Calling LLM for {self.k_node_id}: temp={TEMP:.2f}, max_tokens={TOKENS}"
        )

        try:
            # Get Anthropic client (can be made configurable)
            # Mock implementations for demonstration
            class MockAnthropicClient:
                async def messages_create(self, **kwargs):
                    class MockResponse:
                        class ContentItem:
                            text = "Mock LLM response."
                        content = [ContentItem()]
                    return MockResponse()

            def get_client(provider):
                if provider == "ANTHROPIC":
                    return MockAnthropicClient()
                raise ValueError("Unsupported provider")

            class Provider:
                ANTHROPIC = "ANTHROPIC"

            CLIENT = get_client(Provider.ANTHROPIC)

            # Call LLM
            RESPONSE = await CLIENT.messages_create(
                MODEL="claude-3-5-sonnet-20241022",
                max_tokens=TOKENS,
                temperature=TEMP,
                top_p=self.CONFIG.top_p,
                MESSAGES=[{"role": "user", "content": prompt}]
            )

            return RESPONSE.content[0].text

        except Exception as e:
            LOGGER.error(f"LLM call failed for {self.k_node_id}: {e}")
            raise

    async def _call_llm_with_self_consistency(
        self,
        prompt: str,
        k: Optional[int] = None,
    ) -> List[str]:
        """Call LLM multiple times for self-consistency.

        Args:
            prompt: Prompt to send to LLM
            k: Number of candidates to generate (uses config.self_consistency if None)

        Returns:
            List of k candidate responses
        """
        k = k if k is not None else self.CONFIG.self_consistency

        LOGGER.info(f"Generating {k} candidates for self-consistency")

        CANDIDATES = []
        for i in range(k):
            LOGGER.debug(f"Generating candidate {i+1}/{k}")
            response = await self._call_llm(prompt)
            CANDIDATES.append(response)

        return CANDIDATES

    async def _call_llm_with_tot(
        self,
        prompt: str,
        branches: Optional[int] = None,
        depth: Optional[int] = None,
    ) -> List[str]:
        """Call LLM with Tree of Thoughts reasoning.

        Args:
            prompt: Base prompt
            branches: Number of branches (uses config.tot_branches if None)
            depth: Tree depth (uses config.min_tot_depth if None)

        Returns:
            List of candidate responses from tree exploration
        """
        BRANCHES = branches if branches is not None else self.CONFIG.tot_branches
        DEPTH = depth if depth is not None else self.CONFIG.min_tot_depth

        LOGGER.info(f"Generating ToT with {BRANCHES} branches, depth {DEPTH}")

        # Simplified ToT: generate multiple branches at each level
        CANDIDATES = []

        for level in range(DEPTH):
            level_prompt = f"{prompt}\n\nExploration level {level+1}/{DEPTH}"

            for branch in range(BRANCHES):
                LOGGER.debug(f"ToT level {level+1}, branch {branch+1}")
                response = await self._call_llm(level_prompt)
                CANDIDATES.append(response)

        return CANDIDATES

    def _select_best_candidate(
        self,
        candidates: List[str],
        selection_criteria: str = "length",
    ) -> str:
        """Select best candidate from multiple responses.

        Args:
            candidates: List of candidate responses
            selection_criteria: Criteria for selection ("length", "first", "last")

        Returns:
            Best candidate
        """
        if not candidates:
            raise ValueError("No candidates to select from")

        if selection_criteria == "length":
            # Select candidate with median length
            candidates_sorted = sorted(candidates, key=len)
            return candidates_sorted[len(candidates_sorted) // 2]
        elif selection_criteria == "first":
            return candidates[0]
        elif selection_criteria == "last":
            return candidates[-1]
        else:
            LOGGER.warning(f"Unknown selection criteria: {selection_criteria}, using first")
            return candidates[0]

    async def _execute_with_rag(
        self,
        prompt: str,
        context: Dict[str, Any],
    ) -> str:
        """Execute with RAG integration.

        Args:
            prompt: Base prompt
            context: Context with RAG configuration

        Returns:
            LLM response with RAG-enhanced context
        """
        # RAG integration pending - requires vector store and retrieval infrastructure
        LOGGER.warning(f"RAG not yet implemented for {self.k_node_id}, calling LLM directly")
        return await self._call_llm(prompt)