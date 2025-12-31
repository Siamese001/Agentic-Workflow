#!/usr/bin/env python3
"""Temporary script to update semantic_l2_registry in structure_blueprint.py"""
from pathlib import Path
import re

blueprint_path = Path("agentic_core/config/blueprint_sovereign/structure_blueprint.py")
content = blueprint_path.read_text(encoding='utf-8')

# Find and replace the agent_roles entry
old_pattern = r"'agent_roles': \{'purpose': 'Pre-defined agent personas, role templates, and behavioral archetypes', 'entity_types': \['Class', 'Dict'\], 'keywords': \['role', 'persona', 'agent_type', 'archetype', 'behavior'\], 'imports': \[\], 'bases': \['CanonBaseAgent'\], 'examples': \['SocraticPersona', 'CriticRole', 'ArchitectArchetype'\]\}"

new_value = "'agent_roles': {'purpose': 'Reusable sovereign agent role mixins enabling autonomy, adaptation, self-learning, proactivity, and resilience', 'entity_types': ['Class'], 'keywords': ['mixin', 'autonomy', 'proactive', 'adaptive', 'self_learning', 'resilience', 'role', 'experience', 'diagnosis'], 'imports': ['agentic_core.patterns.agent_roles'], 'bases': ['AutonomyMixin', 'AdaptiveExecutionMixin', 'ExperienceBufferMixin', 'SelfDiagnosisMixin'], 'examples': ['AutonomyMixin', 'AdaptiveExecutionMixin', 'ExperienceBuffer', 'SelfDiagnosisMixin', 'ProactiveScheduler', 'ContextAwareValidator']}"

if old_pattern in content:
    content = content.replace(old_pattern, new_value)
    blueprint_path.write_text(content, encoding='utf-8')
    print("✅ Updated semantic_l2_registry['patterns']['agent_roles']")
else:
    print("❌ Pattern not found - manual edit required")
