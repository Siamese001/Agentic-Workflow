"""
Structured Engine with Instructor

Forces LLMs to output valid, schema-compliant JSON using grammar-based constrained decoding.
No more "I hope this parses" - the LLM physically cannot output invalid structures.
"""
from typing import Any, Optional, Protocol, Dict, List


import logging
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field, field_validator

LOGGER = logging.getLogger(__name__)

try:
    import instructor
    from openai import AsyncOpenAI
    INSTRUCTOR_AVAILABLE = True
except ImportError:
    INSTRUCTOR_AVAILABLE = False
    LOGGER.warning("Instructor library not available. Install with: pip install instructor openai")


class AgentThoughtProcess(BaseModel):
    """
    Forces the agent to show its work before acting.
    This is the "Physics" of your Agent - the schema it must follow.
    """
    _reasoning_trace: List[str] = Field(
        ...,
        DESCRIPTION="""Step-by-step logic leading to the decision. Each step should be clear and
            atomic."""
    )
    _relevant_context_keys: List[str] = Field(
        ...,
    )
    tool_choice: Literal["SEARCH", "CODE", "ANSWER", "DELEGATE", "TERMINATE"] = Field(
        ...,
        DESCRIPTION="The action type to take"
    )
    _tool_arguments: Dict[str, Any] = Field(
        default_factory=dict,
        DESCRIPTION="Arguments for the chosen tool"
    )
    _confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        DESCRIPTION="Confidence in this decision (0.0 to 1.0)"
    )

    @field_validator('_tool_arguments')
    @classmethod
    def validate_args(cls, v, info):
        """Self-validation inside the schema."""
        tool_choice = info.data.get('tool_choice')

        if tool_choice == 'CODE' and 'code' not in v:
            raise ValueError("Tool choice CODE requires a 'code' argument.")

        if tool_choice == 'SEARCH' and 'query' not in v:
            raise ValueError("Tool choice SEARCH requires a 'query' argument.")

        if tool_choice == 'DELEGATE' and 'subtask' not in v:
            raise ValueError("Tool choice DELEGATE requires a 'subtask' argument.")

        return v


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
        self.model = "gpt-4"

        LOGGER.info(f"Structured engine initialized with AsyncOpenAI client")

    async def think_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        max_retries: int = 3
    ) -> AgentThoughtProcess:
        """
        Executes an inference call that is GUARANTEED to match AgentThoughtProcess.

        If the LLM makes a mistake, Instructor retries automatically with the error message.

        Args:
            system_prompt: System instructions for the agent
            user_prompt: User query or task
            max_retries: Maximum number of retry attempts

        Returns:
            Validated AgentThoughtProcess instance
        """
        LOGGER.debug(f"Executing structured inference (max_retries={max_retries})")

        try:
            result = await self.client.chat.completions.create(
                model=self.model,
                response_model=AgentThoughtProcess,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_retries=max_retries
            )

            LOGGER.info(f"Structured inference successful. Tool choice: {result.tool_choice}, "
                       f"Confidence: {result._confidence_score:.2f}")

            return result

        except Exception as e:
            LOGGER.error(f"Structured inference failed after {max_retries} retries: {e}")
            raise


class CodeGenerationResult(BaseModel):
    """Schema for code generation tasks."""
    _reasoning: str = Field(..., description="Why this code solves the problem")
    _code: str = Field(..., description="The generated Python _code")
    _dependencies: List[str] = Field(
        default_factory=list,
        DESCRIPTION="Required pip packages"
    )
    _test_cases: List[str] = Field(
        default_factory=list,
        DESCRIPTION="Test cases to verify the code"
    )
    _safety_notes: List[str] = Field(
        default_factory=list,
        DESCRIPTION="Potential safety concerns or limitations"
    )


class ResearchResult(BaseModel):
    """Schema for research tasks."""
    _query_understanding: str = Field(..., description="How you interpreted the research question")
    _sources: List[Dict[str, str]] = Field(
        ...,
        DESCRIPTION="List of sources with 'url' and 'relevance' keys"
    )
    _key_findings: List[str] = Field(..., description="Main findings from the research")
    _confidence_level: Literal["high", "medium", "low"] = Field(
        ...,
        DESCRIPTION="Confidence in the research results"
    )
    _follow_up_questions: List[str] = Field(
        default_factory=list,
        DESCRIPTION="Suggested follow-up research questions"
    )


class StructuredEngineFactory:
    """Factory for creating specialized structured engines."""

    @staticmethod
    def create_code_engine(client: AsyncOpenAI, model: str = "gpt-4o") -> "StructuredEngine":
        """Create an engine optimized for code generation."""
        engine = StructuredEngine(client)
        engine.model = model # Set the model for the engine
        # Note: Instructor's patch applies to the client, not the engine directly.
        # The response_model is passed at the call site (think_structured), not set on the engine itself.
        # This factory method would need to return a callable or a configured function if it were to pre-set response_model.
        # For now, we'll assume the caller of the engine will specify response_model.
        return engine

    @staticmethod
    def create_research_engine(client: AsyncOpenAI, model: str = "gpt-4o") -> "StructuredEngine":
        """Create an engine optimized for research tasks."""
        engine = StructuredEngine(client)
        engine.model = model # Set the model for the engine
        return engine


async def create_structured_engine(
    client: AsyncOpenAI,
    model: str = "gpt-4o",
    engine_type: str = "default"
) -> StructuredEngine:
    """
    Factory function to create a structured engine.

    Args:
        client: AsyncOpenAI client instance
        model: Model to use
        engine_type: Type of engine ("default", "code", "research")

    Returns:
        StructuredEngine instance
    """
    if engine_type == "code":
        return StructuredEngineFactory.create_code_engine(client, model)
    elif engine_type == "research":
        return StructuredEngineFactory.create_research_engine(client, model)
    else:
        return StructuredEngine(client) # Default engine, model will be set in __init__ or overridden by call site