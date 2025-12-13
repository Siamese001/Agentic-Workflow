"""Implementation for lic_routing_rules."""

from typing import Any, Dict, List, Optional
from .lic_routing_rules_types import *

class LICRouter:
    """Router for determining message route and constraints."""

    def __init__(self) -> None:
        """Initialize the router."""
        self._route_configs = ROUTE_CONFIGS
        self._archetype_tones = ARCHETYPE_TONES
        self._archetype_temps = ARCHETYPE_TEMPERATURES

    def determine_route(self, connection_status: str, prior_message_count: int, route_override: Optional[MessageRoute]=None) -> MessageRoute:
        """
        Determine the appropriate message route.

        Args:
            connection_status: Current connection status
            prior_message_count: Number of prior messages
            route_override: Optional route override

        Returns:
            Determined MessageRoute
        """
        if route_override is not None:
            return route_override
        if prior_message_count > 0:
            return MessageRoute.FOLLOW_UP
        if connection_status == 'not_connected':
            return MessageRoute.SHORT_NEW
        return MessageRoute.SHORT_NEW

    def get_route_config(self, route: MessageRoute) -> RouteConfig:
        """Get configuration for a route."""
        return self._route_configs[route]

    def get_constraints(self, route: MessageRoute) -> RouteConstraints:
        """Get constraints for a route."""
        return self._route_configs[route].constraints

    def get_archetype_tone(self, archetype: RecipientArchetype) -> ArchetoneConfig:
        """Get tone configuration for an archetype."""
        return self._archetype_tones.get(archetype, self._archetype_tones[RecipientArchetype.EXECUTIVE])

    def get_temperature(self, archetype: RecipientArchetype) -> float:
        """Get foundation temperature for an archetype."""
        return self._archetype_temps.get(archetype, 0.55)

    def get_tool_budget(self, route: MessageRoute) -> str:
        """Get tool call budget for a route."""
        return TOOL_CALL_BUDGETS.get(route, '3-6')

    def validate_message_length(self, text: str, route: MessageRoute) -> Dict[str, object]:
        """
        Validate message length against route constraints.

        Args:
            text: Message text
            route: Message route

        Returns:
            Validation result dictionary
        """
        constraints = self.get_constraints(route)
        result: Dict[str, object] = {'is_valid': True, 'violations': [], 'word_count': len(text.split()), 'char_count': len(text)}
        if constraints.char_limit is not None:
            if len(text) > constraints.char_limit:
                result['is_valid'] = False
                result['violations'].append(f'Character count {len(text)} exceeds limit {constraints.char_limit}')
        if constraints.word_range is not None:
            word_count = len(text.split())
            min_words, max_words = constraints.word_range
            if word_count < min_words:
                result['is_valid'] = False
                result['violations'].append(f'Word count {word_count} below minimum {min_words}')
            elif word_count > max_words:
                result['is_valid'] = False
                result['violations'].append(f'Word count {word_count} exceeds maximum {max_words}')
        return result

def create_router() -> LICRouter:
    """builder function to create a router."""
    return LICRouter()

def get_route_config(route: MessageRoute) -> RouteConfig:
    """Get configuration for a route."""
    return ROUTE_CONFIGS[route]

def get_archetype_tone(archetype: RecipientArchetype) -> ArchetoneConfig:
    """Get tone configuration for an archetype."""
    return ARCHETYPE_TONES.get(archetype, ARCHETYPE_TONES[RecipientArchetype.EXECUTIVE])

