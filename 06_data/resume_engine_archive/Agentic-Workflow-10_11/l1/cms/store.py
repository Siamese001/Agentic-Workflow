"""
CMS store for resume generation prompt storage and retrieval.

Provides storage functionality for compiled prompts and templates
to ensure consistent resume improvement and job alignment.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class StoredPrompt:
    """
    Represents a stored resume generation prompt with metadata.

    Ensures prompt storage supports consistent resume improvement.
    """
    id: str
    content: str
    template: Optional[str] = None
    context_schema: Optional[Dict[str, Any]] = None
    version: str = "1.0"
    created_at: Optional[str] = None


class PromptStore:
    """
    CMS prompt storage for resume generation.

    Provides storage and retrieval for compiled prompts and templates
    to ensure consistent resume improvement and job alignment.
    """
    
    def __init__(self):
        self._prompts: Dict[str, StoredPrompt] = {}
    
    def store(self, prompt: StoredPrompt) -> str:
        """Stores resume generation prompt and returns its ID."""
        self._prompts[prompt.id] = prompt
        return prompt.id
    
    def retrieve(self, prompt_id: str) -> Optional[StoredPrompt]:
        """Retrieves stored resume generation prompt by ID."""
        return self._prompts.get(prompt_id)
    
    def list_prompts(self) -> List[str]:
        """Lists all stored resume generation prompt IDs."""
        return list(self._prompts.keys())
    
    def delete(self, prompt_id: str) -> bool:
        """Deletes stored resume generation prompt."""
        if prompt_id in self._prompts:
            del self._prompts[prompt_id]
            return True
        return False


# Global prompt store instance
default_store = PromptStore()


def get_store() -> PromptStore:
    """Gets the default resume generation prompt store instance."""
    return default_store


def store_prompt(prompt_id: str, content: str, **kwargs) -> str:
    """Convenience function to store resume generation prompt."""
    prompt = StoredPrompt(id=prompt_id, content=content, **kwargs)
    return default_store.store(prompt)


def retrieve_prompt(prompt_id: str) -> Optional[StoredPrompt]:
    """Convenience function to retrieve resume generation prompt."""
    return default_store.retrieve(prompt_id)


def get_prompt_version(prompt_id: str) -> Optional[str]:
    """Gets the version of a stored resume generation prompt."""
    prompt = default_store.retrieve(prompt_id)
    return prompt.version if prompt else None
