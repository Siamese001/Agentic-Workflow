"""L5 Identity sub-package — G-04 identity propagation surface (L5 v4).

Canonical adoption surface for v4-aware call sites. For the end-to-end
recipe, import `run_v4_action` — it composes the full pipeline
(lane decision + gated write + gated egresses + audit record). For
finer-grained control, import the per-layer adapters directly.

Wire-in layers exported here (bottom-up):

| Wave | Symbol                              | Purpose                              |
|------|-------------------------------------|--------------------------------------|
| W1   | resolve_front_door_principal        | seed PrincipalChain from env         |
| E    | emit_v4_write                       | v3+v4 write adapter                  |
| F    | run_chokepoint_v4                   | guardrail bank chokepoint            |
| G+H  | evaluate_runtime_lane               | base lane composition                |
| I    | get_active_registry_snapshot        | registry singleton                   |
| J    | get_active_data_authority_resolution| data-authority singleton             |
| K    | run_pre_l5_sweep                    | unified identity+registry+DA sweep   |
| L    | evaluate_runtime_lane_with_sweep    | lane + sweep composed                |
| M    | emit_lane_audit_record              | full-fidelity forensic record        |
| N    | emit_lane_gated_write               | lane-gated write                     |
| O    | emit_lane_gated_egress              | lane-gated egress                    |
| P    | run_v4_action                       | ONE-CALL composed recipe (preferred) |

Reference: docs/contracts/identity_propagation.md
Parent plan: docs/archive/windsurf/legacy-tree/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""

from __future__ import annotations

from agentic_core.L5_safety.identity.action_pipeline import (
    EgressRequest,
    V4ActionOutcome,
    run_v4_action,
)
from agentic_core.L5_safety.identity.audit_binding_lane import (
    LaneAuditRecord,
    emit_lane_audit_record,
    reconstruct_lane_audit_digest,
)
from agentic_core.L5_safety.identity.data_authority_loader import (
    clear_active_data_authority,
    get_active_data_authority_ledger,
    get_active_data_authority_resolution,
    get_active_policy_version,
    set_active_data_authority_ledger,
)
from agentic_core.L5_safety.identity.egress_adapter_gated import (
    EgressRefused,
    emit_lane_gated_egress,
)
from agentic_core.L5_safety.identity.front_door_resolver import (
    FRONT_DOOR_AUTOMATION_ENV_VARS,
    clear_resolver_cache,
    resolve_front_door_principal,
)
from agentic_core.L5_safety.identity.hitl_sweep_bridge import (
    classify_sweep_as_hitl_class,
)
from agentic_core.L5_safety.identity.llm_gateway_v4 import (
    GovernedLLMGateway,
    GovernedLLMResult,
    LLMEgressRefused,
)
from agentic_core.L5_safety.identity.pre_l5_sweep import (
    PreL5SweepResult,
    run_pre_l5_sweep,
)
from agentic_core.L5_safety.identity.registry_loader import (
    clear_active_snapshot,
    get_active_registry_snapshot,
    set_active_registry_snapshot,
)
from agentic_core.L5_safety.identity.runtime_entry_sweep import (
    RuntimeLaneDecisionWithSweep,
    evaluate_runtime_lane_with_sweep,
)
from agentic_core.L5_safety.identity.write_adapter import emit_v4_write
from agentic_core.L5_safety.identity.write_adapter_gated import (
    WriteRefused,
    emit_lane_gated_write,
)

__all__ = [
    # Wave-W1
    "FRONT_DOOR_AUTOMATION_ENV_VARS",
    "clear_resolver_cache",
    "resolve_front_door_principal",
    # Wave-E
    "emit_v4_write",
    # Wave-I
    "clear_active_snapshot",
    "get_active_registry_snapshot",
    "set_active_registry_snapshot",
    # Wave-J
    "clear_active_data_authority",
    "get_active_data_authority_ledger",
    "get_active_data_authority_resolution",
    "get_active_policy_version",
    "set_active_data_authority_ledger",
    # Wave-K
    "PreL5SweepResult",
    "run_pre_l5_sweep",
    # Wave-L
    "RuntimeLaneDecisionWithSweep",
    "evaluate_runtime_lane_with_sweep",
    # Wave-M
    "LaneAuditRecord",
    "emit_lane_audit_record",
    "reconstruct_lane_audit_digest",
    # Wave-N
    "WriteRefused",
    "emit_lane_gated_write",
    # Wave-O
    "EgressRefused",
    "emit_lane_gated_egress",
    # Wave-P (preferred one-call adoption entry)
    "EgressRequest",
    "V4ActionOutcome",
    "run_v4_action",
    # Wave-R (LLM gateway wrapper — SovereignLLMGateway closure)
    "GovernedLLMGateway",
    "GovernedLLMResult",
    "LLMEgressRefused",
    # Wave-S (HITL sweep bridge — hitl_policy closure)
    "classify_sweep_as_hitl_class",
]
