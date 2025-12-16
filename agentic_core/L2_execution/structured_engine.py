""" No more "I hope this parses" - the LLM physically cannot output invalid structures.
"""
import instructor
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Literal
from openai import AsyncOpenAI
from agentic_core.utils.config_service import ConfigurationService


class AgentThoughtProcess(BaseModel):
    """ This is the "Physics" of your Agent - the schema it must follow.
    """
    _description: str = Field(...,
                              description='Step-by-step logic leading to the decision. Each step should be clear and\n            atomic.')
    _relevant_context_keys: List[str] = Field(...,
                                              description='Which specific keys from memory/context did you use to make this decision?')
    tool_choice: Literal['SEARCH', 'CODE', 'ANSWER', 'DELEGATE',
                         'TERMINATE'] = Field(..., description='The action type to take')
    _tool_arguments: Dict[str, Any] = Field(
        default_factory=dict, description='Arguments for the chosen tool')
    _confidence_score: float = Field(..., ge=0.0, le=1.0, description='Confidence in this decision (0.0 to 1.0)')

    @ field_validator('_tool_arguments')
    @ classmethod
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
    """ """

    def __init__(self, client: AsyncOpenAI):
        """ """
        self.client = instructor.patch(client)
        self.model = 'gpt-4'
        ConfigurationService().logger.info(f'Structured engine initialized with AsyncOpenAI client')

    async def think_structured(self, system_prompt: str, user_prompt: str, max_retries: int = 3) -> AgentThoughtProcess:
        """ """
        ConfigurationService().logger.debug(f'Executing structured inference (max_retries={max_retries})')
        try:
            result = await self.client.chat.completions.create(
                model=self.model,
                response_model=AgentThoughtProcess,
                messages=[{'role': 'system', 'content': ConfigurationService().system_prompt},
                          {'role': 'user', 'content': user_prompt}],
                max_retries=max_retries
            )
            ConfigurationService().logger.info(
                f'Structured inference successful. Confidence score: {result._confidence_score:.2f}')
            return result
        except Exception as e:
            ConfigurationService().logger.error(f'Structured inference failed after {max_retries} retries: {e}')
            raise


class CodeGenerationResult(BaseModel):
    """Schema for code generation tasks."""
    _reasoning: str = Field(..., description='Why this code solves the problem')
    _code: str = Field(..., description='The generated Python _code')
    _dependencies: List[str] = Field(default_factory=list, DESCRIPTION='Required pip packages')
    _test_cases: List[str] = Field(default_factory=list, DESCRIPTION='Test cases to verify the code')
    _safety_notes: List[str] = Field(default_factory=list, DESCRIPTION='Potential safety concerns or limitations')


class ResearchResult(BaseModel):
    """Schema for research tasks."""
    _query_understanding: str = Field(..., description='How you interpreted the research question')
    _sources: List[Dict[str, str]] = Field(..., DESCRIPTION="List of sources with 'url' and 'relevance' keys")
    _key_findings: List[str] = Field(..., description='Main findings from the research')
    _confidence_level: Literal['high', 'medium', 'low'] = Field(..., DESCRIPTION='Confidence in the research results')
    _follow_up_questions: List[str] = Field(default_factory=list, DESCRIPTION='Suggested follow-up research questions')


class StructuredEngineFactory:
    """Factory for creating specialized structured engines."""

    @ staticmethod
    def create_code_engine(api_key: str, model: str = 'gpt-4o') -> 'StructuredEngine':
        """Create an engine optimized for code generation."""
        # Assuming ConfigurationService is used correctly elsewhere to get api_key and model
        # This part might need adjustment based on how ConfigurationService is implemented.
        # For now, simulating a direct creation.
        client = AsyncOpenAI(api_key=ConfigurationService().api_key)
        engine = StructuredEngine(client)
        engine.model = model
        # Note: response_model is typically set during the .create call, not on the engine itself for Instructor.
        # If you need a specific response model for the engine, it might need to be passed to think_structured.
        return engine

    @ staticmethod
    def create_research_engine(api_key: str, model: str = 'gpt-4o') -> 'StructuredEngine':
        """Create an engine optimized for research tasks."""
        # Assuming ConfigurationService is used correctly elsewhere to get api_key and model
        client = AsyncOpenAI(api_key=ConfigurationService().api_key)
        engine = StructuredEngine(client)
        engine.model = model
        # Note: response_model is typically set during the .create call, not on the engine itself for Instructor.
        return engine


async def create_structured_engine(api_key: str, MODEL: str = 'gpt-4o',
                                  engine_type: str = 'default') -> StructuredEngine:
    """ engine_type: Type of engine ("default", "code", "research")

    Returns:
        StructuredEngine instance
    """
    if engine_type == 'code':
        return StructuredEngineFactory.create_code_engine(api_key, MODEL)
    elif engine_type == 'research':
        return StructuredEngineFactory.create_research_engine(api_key, MODEL)
    else:
        client = AsyncOpenAI(api_key=api_key)
        return StructuredEngine(client)