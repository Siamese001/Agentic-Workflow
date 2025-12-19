"""
Core utilities for Agentic Workflow
Provides draft generation, scoring, file operations, networking, and safety
"""

from .core_utilities import (
    DraftGenerator,
    DraftResult,
    FileManager,
    SemanticScorer,
    log_action,
    register_process,
)
from .dead_man_switch import DeadManSwitch, get_dead_man_switch, track_action, watchdog
from .networking import (
    OUTREACH_ALLOWED_HOSTS,
    EgressResult,
    NetworkingUtility,
    get_networking_utility,
    send_email,
    strict_egress_filter,
)
from .pitch_generator import PitchGenerator, PitchResult
from .shadow_mode import ShadowModeEngine, ShadowModeResult
# Atomic Fission: Import from new subatomic modules
from .syntax_validator import validate_python_syntax
from .mcp_mocks import (
    get_current_time, convert_time, issues_get_detail,
    browser_navigate, browser_type, browser_click,
    string_get, string_set, start_transaction, watch_key,
    transaction_set_with_ttl, commit_transaction, incr, get_and_set,
    brave_search, execute_cost_controlled_search,
    get_from_langcache, set_to_langcache,
    search_nodes, add_observations,
    search_records, write_file, read_text_file,
    semantic_score_draft, generate_draft_llm,
    get_variable_defs, get_file_versions,
)
from .error_handling import MCPError, CircuitBreakerOpenError, retry_with_backoff
from .validation_utils import validate_email, validate_url, sanitize_filename
from .crypto_utils import setup_gpg_signing, sign_and_commit
from .process_utils import register_process as register_process_atomic, log_action as log_action_atomic

# Backward compatibility: prefer atomic versions if not already defined
if 'register_process' not in dir():
    register_process = register_process_atomic
if 'log_action' not in dir():
    log_action = log_action_atomic

__all__ = [
    "DraftGenerator",
    "SemanticScorer",
    "FileManager",
    "register_process",
    "log_action",
    "DraftResult",
    "NetworkingUtility",
    "EgressResult",
    "get_networking_utility",
    "strict_egress_filter",
    "send_email",
    "OUTREACH_ALLOWED_HOSTS",
    "PitchGenerator",
    "PitchResult",
    "ShadowModeEngine",
    "ShadowModeResult",
    "DeadManSwitch",
    "get_dead_man_switch",
    "watchdog",
    "track_action"
]
