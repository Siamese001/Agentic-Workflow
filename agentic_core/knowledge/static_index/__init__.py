"""Static Index - Hard-coded knowledge bases and taxonomies."""
from agentic_core.knowledge.static_index.action_verbs_types import ACTION_VERBS, STRONG_VERBS
from agentic_core.knowledge.static_index.skill_taxonomy_types import ALL_SKILLS, SKILL_TAXONOMY
from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

__all__ = ['ACTION_VERBS', 'STRONG_VERBS', 'SKILL_TAXONOMY', 'ALL_SKILLS']
