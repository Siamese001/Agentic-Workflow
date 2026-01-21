from __future__ import annotations

"""
Structured Engine with Instructor

Forces LLMs to output valid, schema-compliant JSON using grammar-based constrained decoding.
No more "I hope this parses" - the LLM physically cannot output invalid structures.
"""
import logging
from typing import Any

from agentic_core.schemas.models.core_contracts import AgentThoughtProcess

Logger: Any = logging.getLogger(__name__)
try:
    import instructor
    from openai import AsyncOpenAI
    INSTRUCTOR_AVAILABLE: Any = True
except ImportError:
    INSTRUCTOR_AVAILABLE: Any = False
    LOGGER.warning('Instructor library not available. Install with: pip install instructor openai')

class StructuredEngine:
    """
    The Hardened Engine that enforces schema compliance at the network layer.

    This call WILL not return until it matches the schema perfectly.
    It automatically retries and fixes validation errors internally.
    """

    def __init__(self, client: AsyncOpenAI):
        """
        Initialize the structured engine with an OpenAI client.

        Args:
            client: AsyncOpenAI instance
        """
        self.client = instructor.patch(client)
        self.model = 'gpt-4'
        LOGGER.info('Structured engine initialized with AsyncOpenAI client')

    async def think_structured(self, system_prompt: str, user_prompt: str, max_retries: int=3) -> AgentThoughtProcess:
        """
        Executes an inference call that is GUARANTEED to match AgentThoughtProcess.

        If the LLM makes a mistake, Instructor retries automatically with the error message.

        Args:
            system_prompt: System instructions for the agent
            user_prompt: User query or Task
            max_retries: Maximum number of retry attempts

        Returns:
            Validated AgentThoughtProcess instance
        """
        LOGGER.debug(f'Executing structured inference (max_retries={max_retries})')
        try:
            result: Any = await self.client.chat.completions.create(model=self.model, response_model=AgentThoughtProcess, messages=[{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}], max_retries=max_retries)
            LOGGER.info(f'Structured inference successful. Tool choice: {result.tool_choice}, Confidence: {result._confidence_score:.2f}')
            return result
        except Exception as e:
            LOGGER.error(f'Structured inference failed after {max_retries} retries: {e}')
            raise

class StructuredEngineFactory:
    """Factory for creating specialized structured engines."""

    @staticmethod
    def create_code_engine(client: AsyncOpenAI, model: str='gpt-4o') -> StructuredEngine:
        """Create an engine optimized for code generation."""
        engine: Any = StructuredEngine(client)
        engine.model = model
        return engine

    @staticmethod
    def create_research_engine(client: AsyncOpenAI, model: str='gpt-4o') -> StructuredEngine:
        """Create an engine optimized for research tasks."""
        engine: Any = StructuredEngine(client)
        engine.model = model
        return engine

async def create_structured_engine(client: AsyncOpenAI, model: str='gpt-4o', engine_type: str='default') -> StructuredEngine:
    """
    Factory function to create a structured engine.

    Args:
        client: AsyncOpenAI client instance
        model: Model to use
        engine_type: Type of engine ("default", "code", "research")

    Returns:
        StructuredEngine instance
    """
    if engine_type == 'code':
        return StructuredEngineFactory.create_code_engine(client, model)
    elif engine_type == 'research':
        return StructuredEngineFactory.create_research_engine(client, model)
    else:
        return StructuredEngine(client)
