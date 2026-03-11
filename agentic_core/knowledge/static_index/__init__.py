"""Static Index - Hard-coded knowledge bases and taxonomies."""

from agentic_core.knowledge.static_index.action_verbs_types import ACTION_VERBS, STRONG_VERBS
from agentic_core.knowledge.static_index.skill_taxonomy_types import ALL_SKILLS, SKILL_TAXONOMY

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

__all__ = ["ACTION_VERBS", "STRONG_VERBS", "SKILL_TAXONOMY", "ALL_SKILLS"]
