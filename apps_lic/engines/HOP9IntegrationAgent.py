"""
HOP-9: Integration Agent (V2.5 Architecture).

LIC Sovereign Dispatcher.
Handles delivery payload formatting and final audit verification.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

from apps_lic.utils.lic_agent_base_util import LICAgentBase
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
class HOP9IntegrationAgent(LICAgentBase, SubatomicTestingMixin):
    """
    LIC Sovereign Dispatcher.

    Architecture:
    - Base: LICAgentBase (Config, Tracing, Healing)
    - Inputs: HOP-4 (Route), HOP-5 (Draft), HOP-8 (QA Report)
    - Logic: Checksum Integrity -> Payload Formatting -> Delivery Seal
    - Output: 'hop9_integration' to ImmutableStagingBuffer
    """

    # Sovereign Configuration
    integration_config: dict[str, Any] = field(
        default_factory=lambda: {"checksum_enabled": True, "audit_trail": True}
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute integration handoff logic.

        1. Read Sovereign Mission Output.
        2. Checksum Integrity Verification.
        3. Format Delivery Payload.
        4. Write to Buffer and Seal.
        """
        registry.add_trace("PHASE_START", {"agent": self.__class__.__name__})

        # 1. Read Sovereign Mission Output
        try:
            hop5 = buffer.read("hop5_generation")
            hop8 = buffer.read("hop8_qa_report")
            hop4 = buffer.read("hop4_routing")
            mission_input = buffer.read("mission_input")
        except Exception as e:
            registry.add_trace("DATA_ERROR", {"msg": str(e)})
            raise RuntimeError("HOP-9 missing final mission artifacts")

        if not hop5 or not hop4:
            registry.add_trace("DATA_ERROR", {"msg": "Missing required HOP outputs"})
            raise RuntimeError("HOP-9 missing final mission artifacts")

        registry.add_trace("PHASE_STEP", {"action": "starting_integration_handoff"})

        final_draft = hop5["selected_draft"]["text"]
        route = hop4["route"]

        # 2. Hardened Checksum Integrity Verification
        # Ensuring the message hasn't been mutated since generation.
        current_checksum = hashlib.sha256(final_draft.encode()).hexdigest()
        stored_checksum = hop5["selected_draft"].get("checksum")

        if not stored_checksum:
            registry.add_trace(
                "INTEGRITY_WARNING", {"msg": "No stored checksum found in HOP-5 output"}
            )
        elif current_checksum != stored_checksum:
            registry.add_trace(
                "INTEGRITY_FAILURE", {"expected": stored_checksum, "actual": current_checksum}
            )
            raise ValueError("HOP-9 Integrity Violation: Final draft checksum mismatch")

        # 3. Format Delivery Payload
        # Determine archetype from meta or hop1
        archetype = hop5.get("meta", {}).get("archetype", "UNKNOWN")
        if archetype == "UNKNOWN":
            hop1 = buffer.read("hop1_analysis")
            if hop1:
                archetype = hop1.get("Archetype", "UNKNOWN")

        # Determine priority based on archetype
        priority = "HIGH" if "C_LEVEL" in archetype else "NORMAL"

        # Get recipient ID
        recipient_id = None
        if mission_input:
            recipient_id = mission_input.get("recipient_id")

        delivery_payload = {
            "message": final_draft,
            "delivery_route": route,
            "recipient_id": recipient_id,
            "audit_report_path": hop8.get("report_path") if hop8 else None,
            "priority": priority,
        }

        # 4. Write to Buffer and Seal
        buffer.write_once(
            "hop9_integration",
            {
                "status": "READY_FOR_DELIVERY",
                "payload": delivery_payload,
                "checksum": current_checksum,
            },
        )

        registry.add_trace(
            "MISSION_COMPLETED", {"status": "SUCCESS", "route": route, "archetype": archetype}
        )
