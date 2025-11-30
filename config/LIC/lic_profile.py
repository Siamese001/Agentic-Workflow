# LIC profile configuration
from typing import Dict, Any

def create_custom_profile(name: str, **kwargs) -> Dict[str, Any]:
    """Create a custom LIC profile with specified parameters"""
    profile = {
        "name": name,
        "provider": kwargs.get("provider", "anthropic"),
        "model": kwargs.get("model", "claude-haiku-4-5-20251001"),
        "temperature": kwargs.get("temperature", 0.7),
        "max_tokens": kwargs.get("max_tokens", 1000),
        "cost_limit": kwargs.get("cost_limit", 0.01)
    }

    return profile
