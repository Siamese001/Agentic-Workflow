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

# Atomic Fission: Import from new subatomic modules
from .process_utils import log_action as log_action_atomic
from .process_utils import register_process as register_process_atomic
from .shadow_mode import ShadowModeEngine, ShadowModeResult

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
