"""
Structure Blueprint Config — Backward-Compatible Re-export Shim.

SSOT: agentic_core.L5_safety.config.structure_blueprint/

This file contains NO data definitions and NO domain logic.  It re-exports
names from the modular package so that every existing
``from structure_blueprint_config import X`` continues to work unchanged.

The only "logic" present is structural contract enforcement:
  1. ``from package import *`` to pull in the canonical public API.
  2. Explicit re-imports for 18 backward-compat names.
  3. ``__all__ = list(_pkg_all)`` to mirror the package surface.

Import-Path Policy
~~~~~~~~~~~~~~~~~~
- **Supported import path (external consumers):**
  ``from agentic_core.L5_safety.config.structure_blueprint_config import X``
  This is the stable backward-compatible entry point.

- **SSOT import path (package internals / new code):**
  ``from agentic_core.L5_safety.config.structure_blueprint import X``
  The package ``__all__`` (163 names) is the canonical public API.

Contract
~~~~~~~~
- ``__all__`` mirrors the package's ``__all__`` exactly (163 names).
  ``from structure_blueprint_config import *`` exposes only these names.
- 18 additional internal/scaffolding names (types, builders, lazy getters,
  derived registries) are explicitly re-exported below for backward
  compatibility.  They are importable via
  ``from structure_blueprint_config import X`` but are NOT in ``__all__``
  and are NOT exposed by ``import *``.

DO NOT add new definitions here. Add them to the modular package instead.
"""
# noqa: F401 — re-exports for backward compatibility

from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Re-export the entire public API from the package.
# The canonical __all__ lives in the package __init__.py; this shim mirrors it.
from agentic_core.L5_safety.config.structure_blueprint import *  # noqa: F401,F403
from agentic_core.L5_safety.config.structure_blueprint import __all__ as _pkg_all
from agentic_core.L5_safety.config.structure_blueprint._constants import (  # noqa: F401
    AGENT_RESILIENCE_CONFIG,
    DOWNSTREAM_ROOTS,
    GRAVITY_CONFIG,
    GRAVITY_SURGERY_ENABLED,
    HEALING_CONFIG,
    LAYER_OVERRIDES,
    MCP_CAPABILITIES,
    MISSION_CONFIG,
    UPSTREAM_SOVEREIGN_ROOTS,
    SubfolderDefinition,
    TerritoryDefinition,
    # build_sovereign_territories removed - internal only
)

# Backward-compat alias: SOVEREIGN_REGISTRY -> SOVEREIGN_TERRITORIES
from agentic_core.L5_safety.config.structure_blueprint._constants import (  # noqa: F401
    SOVEREIGN_TERRITORIES as SOVEREIGN_REGISTRY,
)
from agentic_core.L5_safety.config.structure_blueprint.artifacts import (  # noqa: F401
    get_app_specific_patterns_compiled,
)
from agentic_core.L5_safety.config.structure_blueprint.classification import (  # noqa: F401
    get_classification_suffix_patterns_compiled,
    get_compound_suffix_patterns_compiled,
)

# Backward-compat re-exports: names that have active consumers but were
# removed from the package's public __all__ (internal/scaffolding names).
# These are importable via ``from structure_blueprint_config import X``
# but NOT via ``from structure_blueprint_config import *``.
from agentic_core.L5_safety.config.structure_blueprint.derived import (  # noqa: F401
    L4_APPROVED_FOLDERS,
    L4_SUBFOLDER_MAP,
    SCRIPTS_PLACEMENT_RULES,
    agentic_core_registry,
    verify_derived_registries,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (  # noqa: F401
    get_apps_eval_subfolder_map,
    get_apps_exec_subfolder_map,
    get_apps_lic_subfolder_map,
    get_apps_research_subfolder_map,
    get_apps_rfp_subfolder_map,
    get_apps_rg_subfolder_map,
    get_apps_shared_subfolder_map,
    get_core_subfolder_map,
    get_sovereign_territories,
    get_subfolder_metadata,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_records_execution_trace("p0", "evidence", "structure_blueprint_config")
# __all__ mirrors the package's __all__ exactly (163 names).
# The 18 backward-compat re-exports above are importable by explicit import
# but are intentionally excluded from __all__ / import *.
__all__ = list(_pkg_all)
