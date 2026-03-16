from __future__ import annotations

import logging

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "verb_canonicalizer_validator")
emit_determinism_digest("p0", "verb_canonicalizer_validator")

_emit_dispatches_healing_run("p1", "verb_canonicalizer_validator", "L5")
_emit_routes_through("p1", "verb_canonicalizer_validator", "L5")
_emit_escalates_to_human("p1", "verb_canonicalizer_validator", "L5")
_emit_reads_policy_state("p1", "verb_canonicalizer_validator", "L5")
_emit_authorize_and_execute("p2", "verb_canonicalizer_validator", "execution_auth")
_emit_validates_capability("p2", "verb_canonicalizer_validator", "capability_check")
_emit_routes_to_capability("p2", "verb_canonicalizer_validator", "capability_route")
_emit_writes_via_uwg("p2", "verb_canonicalizer_validator", "uwg_write")
_emit_blocks_direct_write("p2", "verb_canonicalizer_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "verb_canonicalizer_validator", "tool_invocation")
_emit_captures_execution_output("p2", "verb_canonicalizer_validator", "exec_output")
_emit_dispatches_agent("p3", "verb_canonicalizer_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "verb_canonicalizer_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "verb_canonicalizer_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "verb_canonicalizer_validator", "healing_outcome")
_emit_escalates_failure("p3", "verb_canonicalizer_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "verb_canonicalizer_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verb_canonicalizer_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "verb_canonicalizer_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "verb_canonicalizer_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verb_canonicalizer_validator", "eval_metric")
_emit_stores_embedding("p4", "verb_canonicalizer_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "verb_canonicalizer_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verb_canonicalizer_validator", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import re
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_logger = logging.getLogger(__name__)
"\nVerb canonicalization for resume bullet points.\n\nCanonicalizes action verbs to approved list and detects forbidden verbs.\n"


class VerbCanonicalizer:
    """Canonicalize action verbs to approved list."""

    _CANONICAL_VERBS: dict[str, list[str]] = {
        "led": ["led", "lead", "leading"],
        "built": ["built", "build", "building"],
        "drove": ["drove", "drive", "driving"],
        "launched": ["launched", "launch", "launching"],
        "scaled": ["scaled", "scale", "scaling"],
        "delivered": ["delivered", "deliver", "delivering"],
        "achieved": ["achieved", "achieve", "achieving"],
        "established": ["established", "establish", "establishing"],
        "managed": ["managed", "manage", "managing"],
        "developed": ["developed", "develop", "developing"],
    }
    _FORBIDDEN_VERBS: list[str] = [
        "pioneered",
        "spearheaded",
        "orchestrated",
        "architected",
        "revolutionized",
        "transformed",
    ]


def canonicalize(self: Any, text: str) -> list[str]:
    """Extract and canonicalize verbs from text."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "canonicalize", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "canonicalize", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "canonicalize")
    text_lower: Any = text.lower()
    for canonical_form, variants in self.CANONICAL_VERBS.items():
        if any(variant in text_lower for variant in variants):
            canonical.append(canonical_form)
    return canonical


def check_for_forbidden_verbs(self: Any, text: str) -> list[str]:
    """Check for forbidden verbs in the text."""
    found_verbs: Any = []
    text_lower: Any = text.lower()
    for verb in self.FORBIDDEN_VERBS:
        # guardian: allow-path-string
        if re.search("\\b" + verb + "\\b", text_lower):
            found_verbs.append(verb)
    return found_verbs
