"""
apps_lic.config - Configuration for LinkedIn Outreach app.
"""

try:
    from apps_lic.config.loader import get_config_path, load_agent_specs
except ImportError:
    get_config_path = None
    load_agent_specs = None

from apps_lic.config.knowledge_base import (
    FROZEN_SNAPSHOT,
    LicPromptEntry,
    LicNodeEntry,
    LicGlobalRule,
    LicSovereignKnowledge,
    get_prompt,
    get_system_prompt,
    get_prompt_entry,
    get_node_config,
    get_global_rule,
    list_all_prompts,
    list_all_nodes,
)

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
    'get_system_prompt',
    'get_prompt_entry',
    'get_node_config',
    'get_global_rule',
    'list_all_prompts',
    'list_all_nodes',
]
