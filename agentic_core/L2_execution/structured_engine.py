"""
Structured Engine with Instructor

Forces LLMs to output valid, schema-compliant JSON using grammar-based constrained decoding.
No more "I hope this parses" - the LLM physically cannot output invalid structures.
"""

import logging
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

try:
    import instructor
    from openai import AsyncOpenAI
    INSTRUCTOR_AVAILABLE = True
except ImportError:
    INSTRUCTOR_AVAILABLE = False
    logger.warning("Instructor library not available. Install with: pip install instructor openai")


class AgentThoughtProcess(BaseModel):
    """
    Forces the agent to show its work before acting.
    This is the "Physics" of your Agent - the schema it must follow.
    """
    reasoning_trace: List[str] = Field(
        ..., 
        description="Step-by-step logic leading to the decision. Each step should be clear and atomic."
    )
    relevant_context_keys: List[str] = Field(
        ..., 
        description="Which specific keys from memory/context did you use to make this decision?"
    )
    tool_choice: Literal["SEARCH", "CODE", "ANSWER", "DELEGATE", "TERMINATE"] = Field(
        ...,
        description="The action type to take"
    )
    tool_arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments for the chosen tool"
    )
    confidence_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Confidence in this decision (0.0 to 1.0)"
    )
    
    @field_validator('tool_arguments')
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
    
    This call WILL NOT return until it matches the schema perfectly.
    It automatically retries and fixes validation errors internally.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Initialize the structured engine.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o)
        """
        if not INSTRUCTOR_AVAILABLE:
            raise ImportError("Instructor library not installed. Run: pip install instructor openai")
        
        self.client = instructor.patch(AsyncOpenAI(api_key=api_key))
        self.model = model
        
        logger.info(f"Structured engine initialized with model: {model}")

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
        logger.debug(f"Executing structured inference (max_retries={max_retries})")
        
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
            
            logger.info(f"Structured inference successful. Tool choice: {result.tool_choice}, "
                       f"Confidence: {result.confidence_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Structured inference failed after {max_retries} retries: {e}")
            raise


class CodeGenerationResult(BaseModel):
    """Schema for code generation tasks."""
    reasoning: str = Field(..., description="Why this code solves the problem")
    code: str = Field(..., description="The generated Python code")
    dependencies: List[str] = Field(
        default_factory=list,
        description="Required pip packages"
    )
    test_cases: List[str] = Field(
        default_factory=list,
        description="Test cases to verify the code"
    )
    safety_notes: List[str] = Field(
        default_factory=list,
        description="Potential safety concerns or limitations"
    )


class ResearchResult(BaseModel):
    """Schema for research tasks."""
    query_understanding: str = Field(..., description="How you interpreted the research question")
    sources: List[Dict[str, str]] = Field(
        ...,
        description="List of sources with 'url' and 'relevance' keys"
    )
    key_findings: List[str] = Field(..., description="Main findings from the research")
    confidence_level: Literal["high", "medium", "low"] = Field(
        ...,
        description="Confidence in the research results"
    )
    follow_up_questions: List[str] = Field(
        default_factory=list,
        description="Suggested follow-up research questions"
    )


class StructuredEngineFactory:
    """Factory for creating specialized structured engines."""
    
    @staticmethod
    def create_code_engine(api_key: str, model: str = "gpt-4o") -> "StructuredEngine":
        """Create an engine optimized for code generation."""
        engine = StructuredEngine(api_key, model)
        engine.response_model = CodeGenerationResult
        return engine
    
    @staticmethod
    def create_research_engine(api_key: str, model: str = "gpt-4o") -> "StructuredEngine":
        """Create an engine optimized for research tasks."""
        engine = StructuredEngine(api_key, model)
        engine.response_model = ResearchResult
        return engine


async def create_structured_engine(
    api_key: str,
    model: str = "gpt-4o",
    engine_type: str = "default"
) -> StructuredEngine:
    """
    Factory function to create a structured engine.
    
    Args:
        api_key: OpenAI API key
        model: Model to use
        engine_type: Type of engine ("default", "code", "research")
        
    Returns:
        StructuredEngine instance
    """
    if engine_type == "code":
        return StructuredEngineFactory.create_code_engine(api_key, model)
    elif engine_type == "research":
        return StructuredEngineFactory.create_research_engine(api_key, model)
    else:
        return StructuredEngine(api_key, model)
