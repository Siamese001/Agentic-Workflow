"""L2 E4 same-authority incremental regen chassis (ADR-085)."""

from agentic_core.L2_execution.regen.delta_shape_guard import validate_delta_shape
from agentic_core.L2_execution.regen.incremental_repair_contract import (
    IncrementalRepairContract,
)
from agentic_core.L2_execution.regen.prefix_digest import (
    compute_delta_message_hash,
    compute_system_prefix_hash,
)
from agentic_core.L2_execution.regen.prompt_lock import (
    PROMPT_LOCK_GENERIC,
    REPAIR_TACTIC_INCREMENTAL_DELTA,
    format_regen_delta_user_turn,
)
from agentic_core.L2_execution.regen.regen_refusal import RegenRefusal
from agentic_core.L2_execution.regen.regen_types import (
    AnchorClassification,
    DefectClass,
    RegenRefusalCode,
    TriggerSource,
)
from agentic_core.L2_execution.regen.remediation_delta_mapper import RemediationDeltaMapper
from agentic_core.L2_execution.regen.same_authority_bundle import SameAuthorityBundle
from agentic_core.L2_execution.regen.same_authority_errors import (
    FrozenPrefixMutationError,
    SameAuthorityBundleDriftError,
)
from agentic_core.L2_execution.regen.same_authority_regen_receipt import (
    SameAuthorityRegenReceipt,
)
from agentic_core.L2_execution.regen.same_authority_regen_runner import (
    RegenRunResult,
    SameAuthorityRegenRunner,
)
from agentic_core.L2_execution.regen.same_authority_thread import (
    ChatTurn,
    SameAuthorityThreadState,
    append_same_authority_turn,
    assert_bundle_unchanged,
    assert_prefix_unchanged,
)

__all__ = [
    "AnchorClassification",
    "ChatTurn",
    "DefectClass",
    "FrozenPrefixMutationError",
    "IncrementalRepairContract",
    "PROMPT_LOCK_GENERIC",
    "REPAIR_TACTIC_INCREMENTAL_DELTA",
    "RegenRefusal",
    "RegenRefusalCode",
    "RegenRunResult",
    "RemediationDeltaMapper",
    "SameAuthorityBundle",
    "SameAuthorityBundleDriftError",
    "SameAuthorityRegenReceipt",
    "SameAuthorityRegenRunner",
    "SameAuthorityThreadState",
    "TriggerSource",
    "append_same_authority_turn",
    "assert_bundle_unchanged",
    "assert_prefix_unchanged",
    "compute_delta_message_hash",
    "compute_system_prefix_hash",
    "format_regen_delta_user_turn",
    "validate_delta_shape",
]
