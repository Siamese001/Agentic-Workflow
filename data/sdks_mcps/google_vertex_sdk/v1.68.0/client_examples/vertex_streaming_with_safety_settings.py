"""Google Vertex AI v1.68.0 - Streaming with Safety Settings
Production client for real-time streaming with configurable safety thresholds.
"""

import os
import json
import time
from typing import Iterator, Dict, Any, Optional, List
from vertexai.generative_models import (
    GenerativeModel,
    Content,
    Part,
    HarmCategory,
    HarmBlockThreshold,
    GenerationConfig,
    SafetySetting
)


class StreamingVertexClient:
    """Vertex AI client with streaming and configurable safety settings."""
    
    def __init__(
        self,
        project_id: str = None,
        location: str = "us-central1",
        model_name: str = "gemini-1.5-pro-002"
    ):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.model = GenerativeModel(model_name)
        self.model_name = model_name
    
    def get_safety_settings(
        self,
        block_threshold: HarmBlockThreshold = HarmBlockThreshold.BLOCK_NONE,
        custom_thresholds: Dict[HarmCategory, HarmBlockThreshold] = None
    ) -> List[SafetySetting]:
        """Create safety settings configuration.
        
        Args:
            block_threshold: Default threshold for all categories
            custom_thresholds: Specific thresholds per category
            
        Returns:
            List of safety settings
        """
        settings = []
        
        # Default categories with custom thresholds
        categories = [
            HarmCategory.HARM_CATEGORY_HARASSMENT,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT
        ]
        
        for category in categories:
            threshold = custom_thresholds.get(category, block_threshold)
            settings.append(SafetySetting(category=category, threshold=threshold))
        
        return settings
    
    def stream_with_safety(
        self,
        prompt: str,
        block_threshold: HarmBlockThreshold = HarmBlockThreshold.BLOCK_NONE,
        custom_safety: Dict[HarmCategory, HarmBlockThreshold] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        candidate_count: int = 1
    ) -> Iterator[Dict[str, Any]]:
        """Stream response with configurable safety settings.
        
        Args:
            prompt: Input prompt
            block_threshold: Default safety threshold
            custom_safety: Category-specific safety thresholds
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
            candidate_count: Number of candidates to generate
            
        Yields:
            Streaming chunks with metadata
        """
        # Configure safety settings
        safety_settings = self.get_safety_settings(block_threshold, custom_safety)
        
        # Generation config
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            candidate_count=candidate_count
        )
        
        # Create content
        content = Content(parts=[Part.from_text(prompt)], role="user")
        
        try:
            # Generate streaming response
            response_stream = self.model.generate_content(
                content,
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=True
            )
            
            chunk_count = 0
            for chunk in response_stream:
                chunk_count += 1
                
                # Extract text from chunk
                text = ""
                if chunk.candidates and chunk.candidates[0].content:
                    for part in chunk.candidates[0].content.parts:
                        if hasattr(part, 'text') and part.text:
                            text += part.text
                
                # Extract safety ratings
                safety_ratings = []
                if chunk.candidates and chunk.candidates[0].safety_ratings:
                    for rating in chunk.candidates[0].safety_ratings:
                        safety_ratings.append({
                            "category": rating.category.name,
                            "probability": rating.probability.name if rating.probability else None,
                            "blocked": rating.blocked if hasattr(rating, 'blocked') else False
                        })
                
                # Extract finish reason
                finish_reason = None
                if chunk.candidates and hasattr(chunk.candidates[0], 'finish_reason'):
                    finish_reason = chunk.candidates[0].finish_reason.name
                
                yield {
                    "chunk_id": chunk_count,
                    "text": text,
                    "safety_ratings": safety_ratings,
                    "finish_reason": finish_reason,
                    "is_complete": finish_reason is not None,
                    "model": self.model_name
                }
                
        except Exception as e:
            yield {
                "error": str(e),
                "error_type": type(e).__name__,
                "model": self.model_name
            }
    
    def collect_stream_with_metadata(
        self,
        prompt: str,
        **stream_kwargs
    ) -> Dict[str, Any]:
        """Collect full stream and aggregate metadata.
        
        Args:
            prompt: Input prompt
            **stream_kwargs: Arguments for stream_with_safety
            
        Returns:
            Complete response with aggregated metadata
        """
        start_time = time.time()
        
        # Collect all chunks
        chunks = []
        full_text = ""
        safety_events = []
        errors = []
        
        for chunk in self.stream_with_safety(prompt, **stream_kwargs):
            chunks.append(chunk)
            
            if "error" in chunk:
                errors.append(chunk)
                continue
            
            full_text += chunk["text"]
            
            # Track safety events
            for rating in chunk.get("safety_ratings", []):
                if rating.get("blocked", False):
                    safety_events.append({
                        "chunk_id": chunk["chunk_id"],
                        "category": rating["category"],
                        "probability": rating["probability"]
                    })
            
            if chunk.get("is_complete", False):
                break
        
        end_time = time.time()
        
        return {
            "success": len(errors) == 0,
            "text": full_text,
            "model": self.model_name,
            "chunks_count": len(chunks),
            "processing_time_seconds": end_time - start_time,
            "safety_events": safety_events,
            "errors": errors,
            "final_finish_reason": chunks[-1].get("finish_reason") if chunks else None,
            "stream_metadata": {
                "total_chunks": len(chunks),
                "has_safety_blocks": len(safety_events) > 0,
                "average_chunk_size": len(full_text) / max(len(chunks), 1)
            }
        }


def demonstrate_safety_thresholds():
    """Demonstrate different safety threshold configurations."""
    
    client = StreamingVertexClient()
    
    test_prompts = [
        "Write a professional email to a potential employer",
        "Generate code for a web scraping script",
        "Create a story about a detective solving a mystery",
        "Explain quantum computing in simple terms"
    ]
    
    # Safety configurations to test
    safety_configs = [
        {
            "name": "Permissive (BLOCK_NONE)",
            "threshold": HarmBlockThreshold.BLOCK_NONE,
            "description": "No content blocking - maximum permissiveness"
        },
        {
            "name": "Low Threshold (BLOCK_ONLY_HIGH)", 
            "threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH,
            "description": "Block only high probability harmful content"
        },
        {
            "name": "Medium Threshold (BLOCK_MEDIUM_AND_ABOVE)",
            "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            "description": "Block medium and high probability harmful content"
        },
        {
            "name": "Strict (BLOCK_LOW_AND_ABOVE)",
            "threshold": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            "description": "Block all potentially harmful content"
        }
    ]
    
    print("Vertex AI Streaming Safety Settings Demo")
    print("=" * 60)
    
    for config in safety_configs:
        print(f"\n{config['name']}: {config['description']}")
        print("-" * 40)
        
        for i, prompt in enumerate(test_prompts[:2]):  # Test first 2 prompts
            print(f"\nPrompt {i+1}: {prompt[:50]}...")
            
            try:
                result = client.collect_stream_with_metadata(
                    prompt,
                    block_threshold=config["threshold"],
                    temperature=0.5,
                    max_tokens=200
                )
                
                print(f"  Success: {result['success']}")
                print(f"  Text length: {len(result['text'])}")
                print(f"  Safety events: {len(result['safety_events'])}")
                print(f"  Processing time: {result['processing_time_seconds']:.2f}s")
                
                if result['safety_events']:
                    print(f"  Safety blocks: {result['safety_events']}")
                
                if not result['success']:
                    print(f"  Errors: {[e['error'] for e in result['errors']]}")
                
            except Exception as e:
                print(f"  Failed: {e}")


def custom_safety_example():
    """Example with custom safety thresholds per category."""
    
    client = StreamingVertexClient()
    
    # Custom safety: strict on dangerous content, permissive on others
    custom_thresholds = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    }
    
    prompt = "Write a technical blog post about AI safety considerations"
    
    print("Custom Safety Thresholds Example")
    print("=" * 40)
    print(f"Prompt: {prompt}")
    print("\nCustom thresholds:")
    for category, threshold in custom_thresholds.items():
        print(f"  {category.name}: {threshold.name}")
    
    result = client.collect_stream_with_metadata(
        prompt,
        custom_safety=custom_thresholds,
        temperature=0.6
    )
    
    print(f"\nResult:")
    print(f"  Success: {result['success']}")
    print(f"  Text preview: {result['text'][:200]}...")
    print(f"  Safety events: {len(result['safety_events'])}")


if __name__ == "__main__":
    # Run safety demonstrations
    demonstrate_safety_thresholds()
    
    print("\n" + "=" * 60)
    custom_safety_example()
    
    # Export configuration examples
    config_examples = {
        "production_permissive": {
            "block_threshold": "BLOCK_NONE",
            "temperature": 0.7,
            "max_tokens": 4096,
            "use_case": "Internal tools, trusted users"
        },
        "production_balanced": {
            "block_threshold": "BLOCK_MEDIUM_AND_ABOVE", 
            "temperature": 0.5,
            "max_tokens": 2048,
            "use_case": "Customer-facing applications"
        },
        "production_strict": {
            "block_threshold": "BLOCK_LOW_AND_ABOVE",
            "temperature": 0.3,
            "max_tokens": 1024,
            "use_case": "Educational content, public APIs"
        },
        "custom_enterprise": {
            "custom_thresholds": {
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_LOW_AND_ABOVE",
                "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_ONLY_HIGH",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE"
            },
            "temperature": 0.4,
            "max_tokens": 2048,
            "use_case": "Enterprise with custom policies"
        }
    }
    
    with open("vertex_safety_configurations.json", "w") as f:
        json.dump(config_examples, f, indent=2)
    
    print(f"\nSafety configuration examples saved to: vertex_safety_configurations.json")
