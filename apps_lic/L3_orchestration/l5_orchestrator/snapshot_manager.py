"""
L5 Autonomous Orchestrator - Snapshot and Rollback Manager (Outreach Engine)
"""

import copy
import logging
from typing import Any, Dict

from apps_lic.L3_orchestration.l5_orchestrator.types import OutreachSnapshot

logger = logging.getLogger(__name__)


def take_snapshot(orchestrator, recipient_context: Dict[str, Any]) -> None:
    """Take a snapshot of current state for potential rollback."""

    snapshot = OutreachSnapshot(
        cycle=orchestrator.current_cycle,
        context=copy.deepcopy(recipient_context),
        outputs=copy.deepcopy(orchestrator.outputs),
        messages=copy.deepcopy(orchestrator.generated_messages),
    )
    orchestrator.snapshots.append(snapshot)

    # Keep only last 3 snapshots
    if len(orchestrator.snapshots) > 3:
        orchestrator.snapshots = orchestrator.snapshots[-3:]


def rollback_to_snapshot(orchestrator) -> bool:
    """Rollback to the previous snapshot."""

    if len(orchestrator.snapshots) < 2:
        logger.warning("No previous snapshot available for rollback")
        return False

    # Get the snapshot before the current one
    snapshot = orchestrator.snapshots[-2]

    orchestrator.context = copy.deepcopy(snapshot.context)
    orchestrator.outputs = copy.deepcopy(snapshot.outputs)
    orchestrator.generated_messages = copy.deepcopy(snapshot.messages)

    logger.info(f"Rolled back to cycle {snapshot.cycle} state")
    return True


def calculate_blast_radius(orchestrator, modified_items: set) -> set:
    """Calculate blast radius of modifications."""
    impacted = set(modified_items)

    for item in modified_items:
        dependents = orchestrator.dependency_map.get(item, set())
        impacted.update(dependents)

    return impacted
