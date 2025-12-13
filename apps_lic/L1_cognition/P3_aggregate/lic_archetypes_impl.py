"""Implementation for lic_archetypes."""

from typing import Any, Dict, List, Optional
from .lic_archetypes_types import *

class ArchetypeTemplateManager:
    """coordinator for archetype templates."""

    def __init__(self) -> None:
        """Initialize the template coordinator."""
        self._templates = ARCHETYPE_TEMPLATES
        self._signatures = SIGNATURE_TEMPLATES
        self._greetings = GREETING_TEMPLATES

    def get_template(self, archetype: RecipientArchetype) -> ArchetypeTemplate:
        """Get template for an archetype."""
        return self._templates.get(archetype, self._templates[RecipientArchetype.EXECUTIVE])

    def get_system_instructions(self, archetype: RecipientArchetype) -> str:
        """Get system instructions for an archetype."""
        template = self.get_template(archetype)
        return template.system_instructions

    def get_creative_brief(self, archetype: RecipientArchetype) -> CreativeBrief:
        """Get creative brief for an archetype."""
        template = self.get_template(archetype)
        return template.creative_brief

    def get_word_count_range(self, archetype: RecipientArchetype) -> tuple[int, int]:
        """Get word count range for an archetype."""
        template = self.get_template(archetype)
        return template.creative_brief.message_body.word_count

    def get_signature_template(self, format_name: str) -> SignatureTemplate:
        """Get signature template by format name."""
        return self._signatures.get(format_name, self._signatures['standard'])

    def get_greeting_template(self, route: str) -> GreetingTemplate:
        """Get greeting template by route."""
        return self._greetings.get(route, self._greetings['SHORT_NEW'])

    def format_signature(self, format_name: str, first_name: str, last_name: str='', title: str='', linkedin_url: str='') -> str:
        """Format a signature with provided values."""
        template = self.get_signature_template(format_name)
        return template.template.format(first_name=first_name, last_name=last_name, title=title, linkedin_url=linkedin_url)

    def format_greeting(self, route: str, first_name: str) -> str:
        """Format a greeting with provided values."""
        template = self.get_greeting_template(route)
        return template.template.format(first_name=first_name)

    def validate_greeting(self, greeting: str) -> Dict[str, object]:
        """Validate a greeting against forbidden patterns."""
        result: Dict[str, object] = {'is_valid': True, 'violations': []}
        for forbidden in FORBIDDEN_GREETINGS:
            pattern_base = forbidden.replace('{first_name}', '')
            if pattern_base.strip() in greeting:
                result['is_valid'] = False
                result['violations'].append(f'Forbidden pattern: {forbidden}')
        if ',' not in greeting:
            result['violations'].append('Missing comma after name')
        return result

def create_template_manager() -> ArchetypeTemplateManager:
    """builder function to create a template coordinator."""
    return ArchetypeTemplateManager()

def get_archetype_template(archetype: RecipientArchetype) -> ArchetypeTemplate:
    """Get template for an archetype."""
    return ARCHETYPE_TEMPLATES.get(archetype, ARCHETYPE_TEMPLATES[RecipientArchetype.EXECUTIVE])

def get_signature_template(format_name: str) -> SignatureTemplate:
    """Get signature template by format name."""
    return SIGNATURE_TEMPLATES.get(format_name, SIGNATURE_TEMPLATES['standard'])

