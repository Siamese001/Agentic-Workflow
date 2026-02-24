"""
L2.3 Tiering Allowlist — SSOT-Derived from agent_confidence_tiering_recommendations.csv.

ONLY agents in TIERING_ALLOWLIST may invoke the centralized healing tier router.
All other agents MUST emit FailureSignal and let L2.3 handle tier selection.

This allowlist is deterministic and must match the CSV exactly.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# YES_TIERING agents — derived from docs/technical/agent_confidence_tiering_recommendations.csv
# Format: (agent_name, file_path)
# ---------------------------------------------------------------------------

TIERING_ALLOWLIST: frozenset[tuple[str, str]] = frozenset(
    {
        ("CodeHealerAgent", "agentic_core/L5_safety/reasoning/CodeHealerAgent.py"),
        ("GravityLeakRepairAgent", "agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py"),
        ("IntegrityGateExecutorAgent", "agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py"),
        ("LocationHealerAgent", "agentic_core/L5_safety/reasoning/LocationHealerAgent.py"),
        ("SafetyExecutorAgent", "agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py"),
        ("StructureHealerAgent", "agentic_core/L5_safety/reasoning/StructureHealerAgent.py"),
        ("TypeHintFixerAgent", "agentic_core/L5_safety/reasoning/TypeHintFixerAgent.py"),
        ("DispatchOutreachToolsAgent", "apps_lic/reasoning/DispatchOutreachToolsAgent.py"),
        ("OutreachValidationExecutorAgent", "apps_lic/reasoning/OutreachValidationExecutorAgent.py"),
        ("DispatchResumeToolsAgent", "apps_rg/reasoning/DispatchResumeToolsAgent.py"),
    }
)

TIERING_ALLOWLIST_AGENT_NAMES: frozenset[str] = frozenset(name for name, _ in TIERING_ALLOWLIST)

TIERING_ALLOWLIST_FILE_PATHS: frozenset[str] = frozenset(path for _, path in TIERING_ALLOWLIST)


def is_tiering_allowed(agent_name: str) -> bool:
    """Check if an agent is allowed to invoke the healing tier router directly."""
    return agent_name in TIERING_ALLOWLIST_AGENT_NAMES


def is_tiering_allowed_by_path(file_path: str) -> bool:
    """Check if a file path is in the tiering allowlist."""
    normalized = file_path.replace("\\", "/")
    return normalized in TIERING_ALLOWLIST_FILE_PATHS


__all__ = [
    "TIERING_ALLOWLIST",
    "TIERING_ALLOWLIST_AGENT_NAMES",
    "TIERING_ALLOWLIST_FILE_PATHS",
    "is_tiering_allowed",
    "is_tiering_allowed_by_path",
]
