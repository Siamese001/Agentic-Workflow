"""C0 Dispatcher — converts a validated C0EvidenceContract into a PromptEnvelope.

Layer: L_TOOLS (tools/adg/prompt_assembly/)
Imports from L3 are legal: ("L_TOOLS", "L3") is an allowed edge.
No L3 code imports from here — boundary is strictly one-way.

Public API:
    assemble_from_c0_contract(contract, task_block, intent_hint="") -> PromptEnvelope | None
"""

from __future__ import annotations

from pathlib import Path

from agentic_core.L3_orchestration.types.c0_evidence_contract_types import C0EvidenceContract
from tools.adg.prompt_assembly.adapters.c0_bridge_adapter import translate_contract
from tools.adg.prompt_assembly.contracts import PromptEnvelope
from tools.adg.prompt_assembly.packets.builders import _assemble
from tools.adg.prompt_assembly.packets.registry import get_template

_GRAPH_INTENT_KEYWORDS: frozenset[str] = frozenset({"path", "graph", "route", "hop", "hops", "edge", "node"})


def _maybe_write_packet(
    envelope: PromptEnvelope,
    output_dir: Path | None,
) -> Path | None:
    """Conditionally persist the packet JSON to output_dir.

    Guards (all must pass to write):
    - output_dir is not None
    - envelope.assembly_status is not None
    - assembly_result is "pass" or "partial"

    Never writes on "fail".  Abstain envelopes never reach this function
    because assemble_from_c0_contract returns None before calling it.

    Returns the path written, or None when the guard suppresses the write.
    """
    if output_dir is None:
        return None
    if envelope.assembly_status is None:
        return None
    if envelope.assembly_status.assembly_result not in ("pass", "partial"):
        return None
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    filename = f"packet_{envelope.packet_type}_{envelope.packet_id}.json"
    out_path = out / filename
    out_path.write_text(envelope.to_json(), encoding="utf-8")
    return out_path


def assemble_from_c0_contract(
    contract: C0EvidenceContract,
    task_block: str,
    intent_hint: str = "",
    output_dir: Path | None = None,
) -> PromptEnvelope | None:
    """Convert a validated C0EvidenceContract into a PromptEnvelope.

    Packet selection:
        - Default: ``executive_summary``
        - Graph/path queries: ``graph_path_explanation`` when any word in
          ``intent_hint`` matches _GRAPH_INTENT_KEYWORDS.

    Returns ``None`` when the bridge emits an abstain signal (coverage too low
    or ``abstain_hint=True`` on the contract).  Caller is responsible for any
    disk writes or L2 handoff — this function produces no side-effects.

    Args:
        contract:    Validated C0EvidenceContract from the retrieval plane.
        task_block:  Task instruction forwarded verbatim into the envelope.
        intent_hint: Optional free-text hint; presence of path/graph keywords
                     selects the graph_path_explanation packet type.

    Returns:
        PromptEnvelope on success, None on abstain.
    """
    # 1. Packet type selection
    _hint_words = set(intent_hint.lower().split())
    if _hint_words & _GRAPH_INTENT_KEYWORDS:
        packet_type = "graph_path_explanation"
    else:
        packet_type = "executive_summary"

    # 2. Bridge: C0EvidenceContract → shaped EvidenceBundle
    bundle, replay_extras = translate_contract(contract, packet_type)

    # 3. Abstain short-circuit — bridge returns None bundle when abstain_hint=True
    if bundle is None:
        return None

    # 4. Fetch template and assemble envelope
    template = get_template(packet_type)
    envelope = _assemble(
        template,
        [],
        [],
        task_block,
        replay_extras=replay_extras,
        pre_shaped_bundle=bundle,
    )

    # 5. Optional guarded write — only on pass / partial
    _maybe_write_packet(envelope, output_dir)

    return envelope
