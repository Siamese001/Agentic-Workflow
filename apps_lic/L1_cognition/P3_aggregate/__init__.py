"""
09_apps/apps_lic/L1_cognition/P3_aggregate package initialization.

Generated: 2025-12-07T13:28:54.073115
"""

from __future__ import annotations


__all__: list[str] = [
    # Routing
    "LICRouter",
    "MessageRoute",
    "RecipientArchetype",
    "RouteConfig",
    "RouteConstraints",
    "RouteConditions",
    "SignatureFormat",
    "CTAFormat",
    "ArchetoneConfig",
    "ROUTE_CONFIGS",
    "ARCHETYPE_TONES",
    "ARCHETYPE_TEMPERATURES",
    "create_router",
    "get_route_config",
    "get_archetype_tone",
    # Templates
    "ArchetypeTemplateManager",
    "ArchetypeTemplate",
    "CreativeBrief",
    "SubjectLineBrief",
    "MessageBodyBrief",
    "CTABrief",
    "SignatureTemplate",
    "GreetingTemplate",
    "ARCHETYPE_TEMPLATES",
    "SIGNATURE_TEMPLATES",
    "GREETING_TEMPLATES",
    "create_template_manager",
    "get_archetype_template",
    "get_signature_template",
    # CTA
    "CTAGenerator",
    "DateWindowEngine",
    "CTAPattern",
    "CTATemplate",
    "CTAStyle",
    "DateWindowConfig",
    "CTA_PATTERNS",
    "CTA_TEMPLATES",
    "create_cta_generator",
    "create_date_window_engine",
    "get_cta_pattern",
]
