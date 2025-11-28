"""
CMS (Content Management System) store for prompt storage and retrieval.

This module provides storage functionality for compiled prompts and templates.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class StoredPrompt:
    """Represents a stored prompt with metadata."""
    id: str
    content: str
    template: Optional[str] = None
    context_schema: Optional[Dict[str, Any]] = None
    version: str = "1.0"
    created_at: Optional[str] = None


class PromptStore:
    """
    Content Management System prompt storage.
    
    Provides storage and retrieval for compiled prompts and templates.
    """
    
    def __init__(self):
        self._prompts: Dict[str, StoredPrompt] = {}
    
    def store(self, prompt: StoredPrompt) -> str:
        """Store a prompt and return its ID."""
        self._prompts[prompt.id] = prompt
        return prompt.id
    
    def retrieve(self, prompt_id: str) -> Optional[StoredPrompt]:
        """Retrieve a stored prompt by ID."""
        return self._prompts.get(prompt_id)
    
    def list_prompts(self) -> List[str]:
        """List all stored prompt IDs."""
        return list(self._prompts.keys())
    
    def delete(self, prompt_id: str) -> bool:
        """Delete a stored prompt."""
        if prompt_id in self._prompts:
            del self._prompts[prompt_id]
            return True
        return False


# Global prompt store instance
default_store = PromptStore()


def get_store() -> PromptStore:
    """Get the default prompt store instance."""
    return default_store


def store_prompt(prompt_id: str, content: str, **kwargs) -> str:
    """Convenience function to store a prompt."""
    prompt = StoredPrompt(id=prompt_id, content=content, **kwargs)
    return default_store.store(prompt)


def retrieve_prompt(prompt_id: str) -> Optional[StoredPrompt]:
    """Convenience function to retrieve a prompt."""
    return default_store.retrieve(prompt_id)


def get_prompt_version(prompt_id: str) -> Optional[str]:
    """Get the version of a stored prompt."""
    prompt = default_store.retrieve(prompt_id)
    return prompt.version if prompt else None
