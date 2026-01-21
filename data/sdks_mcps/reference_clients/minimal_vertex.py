"""Minimal Google Vertex AI Reference Client
Production-ready minimal client for quick integration with grounding.
"""

import os

from vertexai import init as vertex_init
from vertexai.generative_models import GenerativeModel


def simple_generation(prompt: str, model: str = "gemini-1.5-pro-002") -> str:
    """Simple content generation with Vertex AI.

    Args:
        prompt: Input prompt text
        model: Vertex AI model to use

    Returns:
        Generated response text
    """
    # Initialize Vertex AI
    vertex_init(
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location="us-central1"
    )

    model_client = GenerativeModel(model)

    response = model_client.generate_content(
        prompt,
        generation_config={
            "temperature": 0.7,
            "max_output_tokens": 1000
        }
    )

    return response.text

def grounded_generation(prompt: str, threshold: float = 0.7) -> dict:
    """Generation with Google Search grounding and citations.

    Args:
        prompt: Input prompt text
        threshold: Grounding threshold (0.0-1.0)

    Returns:
        Response with grounding metadata
    """
    from vertexai.generative_models import Tool
    from vertexai.generative_models import grounding as vertex_grounding

    vertex_init(
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location="us-central1"
    )

    model_client = GenerativeModel("gemini-1.5-pro-002")

    # Create grounding tool
    grounding_tool = Tool.from_google_search_retrieval(
        vertex_grounding.GoogleSearchRetrieval(
            dynamic_retrieval_config=vertex_grounding.DynamicRetrievalConfig(
                mode="MODE_DYNAMIC",
                dynamic_threshold=threshold
            )
        )
    )

    response = model_client.generate_content(
        prompt,
        tools=[grounding_tool],
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 2000
        }
    )

    # Extract grounding metadata
    grounding_metadata = None
    if hasattr(response, 'candidates') and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
            grounding_metadata = {
                "grounding_score": candidate.grounding_metadata.grounding_score,
                "has_grounding": True
            }

    return {
        "content": response.text,
        "grounding_metadata": grounding_metadata
    }

def safe_generation(prompt: str, safety_threshold: str = "BLOCK_NONE") -> dict:
    """Generation with configurable safety settings.

    Args:
        prompt: Input prompt text
        safety_threshold: Safety threshold level

    Returns:
        Response with safety metadata
    """
    from vertexai.generative_models import (
        HarmBlockThreshold,
        HarmCategory,
        SafetySetting,
    )

    vertex_init(
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location="us-central1"
    )

    model_client = GenerativeModel("gemini-1.5-pro-002")

    # Safety settings
    safety_settings = [
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=HarmBlockThreshold[safety_threshold]
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=HarmBlockThreshold[safety_threshold]
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=HarmBlockThreshold[safety_threshold]
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=HarmBlockThreshold[safety_threshold]
        )
    ]

    response = model_client.generate_content(
        prompt,
        safety_settings=safety_settings,
        generation_config={
            "temperature": 0.7,
            "max_output_tokens": 1000
        }
    )

    # Extract safety ratings
    safety_ratings = []
    if hasattr(response, 'candidates') and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, 'safety_ratings'):
            for rating in candidate.safety_ratings:
                safety_ratings.append({
                    "category": rating.category.name,
                    "probability": rating.probability.name if rating.probability else None
                })

    return {
        "content": response.text,
        "safety_ratings": safety_ratings
    }

if __name__ == "__main__":
    # Test simple generation
    pass
    # Test grounded generation

    # Test safe generation
