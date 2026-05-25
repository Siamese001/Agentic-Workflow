"""PromptBOM Builder — L0 Router → Assembly Stage bridge.

Creates PromptBOM from InstructionPacket, bridging L0 to L_PG territory.
"""

from __future__ import annotations

import uuid
from typing import Any

from agentic_core.L0_routing.types.l0_instruction_packet import InstructionPacket
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    emit_determinism_digest,
    emit_replay_key,
)


# Lazy import to avoid L0->L_PG gravity violation
def _get_prompt_bom():
    from agentic_core.prompt_governance.contracts import PromptBOM

    return PromptBOM


# Self-bootstrap governance wiring
def _get_version_store():
    """Lazy import to avoid circular dependencies."""
    from agentic_core.L4_state.utils.memory.prompt_version_store import get_version_store

    return get_version_store()


class PromptBOMBuilder:
    """Builds PromptBOM from InstructionPacket.

    Bridges L0 routing decisions to L_PG assembly stage.
    Fetches system version hash from L4 state store.
    """

    def build(
        self,
        packet: InstructionPacket,
        raw_u0: str,
        raw_c0: dict[str, Any] | None = None,
        template_args: dict[str, Any] | None = None,
    ) -> PromptBOM:
        """Build PromptBOM from instruction packet.

        Args:
            packet: InstructionPacket from PathRouter.
            raw_u0: Raw user input (U0 slot).
            raw_c0: Context pointers for C0 slot.
            template_args: Template variable bindings.

        Returns:
            Immutable PromptBOM for Assembly Stage.
        """
        PromptBOM = _get_prompt_bom()
        trace_id = str(uuid.uuid4())
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L0_ROUTING,
            "PromptBOMBuilder.build",
        )
        emit_replay_key(trace_id, f"bom:{packet.trace_id}")
        emit_determinism_digest(trace_id, f"path:{packet.path}")

        # Fetch system version hash from L4 store
        version_store = _get_version_store()
        system_version_hash = version_store.get_current_system_hash()

        bom = PromptBOM(
            trace_id=packet.trace_id,
            system_version_hash=system_version_hash,
            mixins_required=tuple(sorted(packet.required_mixins)),
            raw_u0=raw_u0,
            raw_c0=dict(raw_c0) if raw_c0 else {},
            template_args=dict(template_args) if template_args else {},
            path=packet.path,
        )

        return bom


# Singleton instance
_builder_instance: PromptBOMBuilder | None = None


def get_prompt_bom_builder() -> PromptBOMBuilder:
    """Get singleton PromptBOMBuilder instance."""
    global _builder_instance
    if _builder_instance is None:
        _builder_instance = PromptBOMBuilder()
    return _builder_instance


__all__ = ["PromptBOMBuilder", "get_prompt_bom_builder"]
