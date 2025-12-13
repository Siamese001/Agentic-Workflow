"""Enum types for match_schema_context."""


class ContextMatchType(Enum):
    """Types of context matching."""
    DOMAIN = 'domain'
    PURPOSE = 'purpose'
    SEMANTIC = 'semantic'
    STRUCTURAL = 'structural'
    USAGE = 'usage'
