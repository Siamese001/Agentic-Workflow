"""OpenAI v1.53.0 - Streaming Chat with Structured Output (Pydantic)
Production client used for resume extraction and message classification.
"""

import os
import json
from typing import Optional, List, Dict, object
from archives.legacy_resume_gen.Older Microservices Models.v10.6.pydantic import BaseModel, Field
from data.sdks_mcps.reference_clients.minimal_openai import OpenAI
from openai.types.chat import ChatCompletionChunk


class ResumeSection(BaseModel):
    """Resume section with confidence scoring."""
    title: str = Field(..., description="Section title (e.g., 'Experience', 'Education')")
    content: str = Field(..., description="Section content")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")


class ResumeExtract(BaseModel):
    """Complete resume extraction with metadata."""
    name: Optional[str] = Field(None, description="Candidate full name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    sections: List[ResumeSection] = Field(default_factory=list, description="Resume sections")
    summary: Optional[str] = Field(None, description="Professional summary")


def stream_structured_resume(
    resume_text: str,
    model: str = "gpt-4o-2024-08-06",
    max_tokens: int = 4000,
    temperature: float = 0.1
) -> Dict[str, object]:
    """Stream resume extraction with structured output.
    
    Args:
        resume_text: Raw resume text content
        model: OpenAI model to use
        max_tokens: Maximum tokens for response
        temperature: Sampling temperature
        
    Returns:
        Dict with extracted resume data and metadata
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system_prompt = """Extract structured information from the resume.
    Return valid JSON matching the ResumeExtract schema.
    Include confidence scores for each section."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Resume:\n{resume_text}"}
    ]
    
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "resume_extract",
            "schema": ResumeExtract.model_json_schema()
        }
    }
    
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format=response_format,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True
    )
    
    chunks = []
    for chunk in stream:
        if chunk.choices[0].delta.content:
            chunks.append(chunk.choices[0].delta.content)
    
    # Parse the complete structured response
    full_response = "".join(chunks)
    try:
        structured_data = json.loads(full_response)
        validated = ResumeExtract(**structured_data)
        return {
            "success": True,
            "data": validated.model_dump(),
            "model": model,
            "tokens_used": len(full_response.split()),
            "raw_response": full_response
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"JSON parsing failed: {e}",
            "raw_response": full_response
        }


if __name__ == "__main__":
    # Example usage
    sample_resume = """
    John Doe
    john.doe@email.com | (555) 123-4567
    
    EXPERIENCE
    Senior Software Engineer at Tech Corp (2020-Present)
    - Led development of microservices architecture
    - Reduced latency by 40% through optimization
    
    EDUCATION
    BS Computer Science, State University (2016-2020)
    """
    
    result = stream_structured_resume(sample_resume)
    print(json.dumps(result, indent=2))
