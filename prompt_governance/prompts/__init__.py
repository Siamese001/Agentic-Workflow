"""
Prompt Governance Module
Centralized prompt management with schema-first approach
"""

from typing import Dict, Any, Optional
import json
import os

class PromptRegistry:
    """Registry for managing prompts with schemas and versions"""

    def __init__(self):
        self.prompts = {}
        self._load_prompts()

    def _load_prompts(self):
        """Load all prompts from the governance directory"""
        prompt_dir = os.path.dirname(__file__)

        for filename in os.listdir(prompt_dir):
            if filename.endswith('.json') and filename != '__init__.py':
                prompt_name = filename[:-5]  # Remove .json extension
                try:
                    with open(os.path.join(prompt_dir, filename), 'r') as f:
                        prompt_data = json.load(f)
                    self.prompts[prompt_name] = prompt_data
                except Exception as e:
                    print(f"Failed to load prompt {filename}: {e}")

    def get_prompt(self, name: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a prompt by name and optional version"""
        prompt = self.prompts.get(name)
        if prompt is None:
            return None

        if version is not None:
            # Return specific version if available
            versions = prompt.get('versions', {})
            return versions.get(version)

        # Return latest version
        return prompt.get('latest', prompt)

    def list_prompts(self) -> list:
        """List all available prompt names"""
        return list(self.prompts.keys())

# Global prompt registry instance
_prompt_registry = None

def get_prompt_registry() -> PromptRegistry:
    """Get the global prompt registry instance"""
    global _prompt_registry
    if _prompt_registry is None:
        _prompt_registry = PromptRegistry()
    return _prompt_registry

def resolve_prompt(name: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Resolve a prompt by name and version"""
    registry = get_prompt_registry()
    return registry.get_prompt(name, version)





