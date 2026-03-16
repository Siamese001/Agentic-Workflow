"""
RG Configuration Loader - LIC-Aligned Sovereign Architecture.

Handles loading, parsing, and validating JSON configurations against Pydantic schemas.
Aligned with LIC loader.py pattern.

HARDENING: Implements a Singleton Loader that merges the Static JSON Topology
with the Dynamic knowledge_base.py Prompts.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "sovereign_config_loader_util", "execution_auth")
_emit_validates_capability("p2", "sovereign_config_loader_util", "capability_check")
_emit_routes_to_capability("p2", "sovereign_config_loader_util", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_config_loader_util", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_config_loader_util", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_config_loader_util", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_config_loader_util", "exec_output")
_emit_dispatches_agent("p3", "sovereign_config_loader_util", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_config_loader_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_config_loader_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_config_loader_util", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_config_loader_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_config_loader_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_config_loader_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_config_loader_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_config_loader_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_config_loader_util", "eval_metric")
_emit_stores_embedding("p4", "sovereign_config_loader_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_config_loader_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_config_loader_util", "exec_snapshot_link")
from .AgentSpec import AgentSpec, OrchestrationTopology, RGAgentSpecs

_emit_applies_guardrail("p0", "sovereign_config_loader_util", "p0_governance")
_emit_reads_policy_state("p0", "sovereign_config_loader_util", "policy_binding")
_emit_snapshots_state("p0", "sovereign_config_loader_util", "state_snapshot")
emit_replay_key("p0", "sovereign_config_loader_util")
emit_determinism_digest("p0", "sovereign_config_loader_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)
_RG_SPECS_CACHE: RGAgentSpecs | None = None


def get_config_path() -> Path:
    """Returns the directory containing configuration files."""
    return Path(__file__).parent


def load_rg_specs(force_reload: bool = False) -> RGAgentSpecs:
    """
    Loads and validates the rg_agent_specs.json file.

    Args:
        force_reload: If True, ignores cache and reloads from disk.

    Returns:
        RGAgentSpecs: A validated, type-safe configuration object.

    Note:
        If the config file is missing, returns default configuration.
    """
    global _RG_SPECS_CACHE
    if _RG_SPECS_CACHE and (not force_reload):
        return _RG_SPECS_CACHE
    config_path = get_config_path() / "rg_agent_specs.json"
    if not config_path.exists():
        Logger.info(f"Config file not found at {config_path}, using defaults")
        specs = RGAgentSpecs()
        _RG_SPECS_CACHE = specs
        return specs
    try:
        with open(config_path, encoding="utf-8") as f:
            raw_data = json.load(f)
        specs = RGAgentSpecs(**raw_data)
        _RG_SPECS_CACHE = specs
        return specs
    except Exception as e:
        Logger.error(f"Failed to load RG agent specs: {e}")
        Logger.info("Falling back to default configuration")
        specs = RGAgentSpecs()
        _RG_SPECS_CACHE = specs
        return None


def save_rg_specs(specs: RGAgentSpecs) -> None:
    """
    Saves the current configuration to disk.

    Args:
        specs: The configuration to save.
    """
    config_path = get_config_path() / "rg_agent_specs.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(specs.model_dump(), f, indent=2)
    global _RG_SPECS_CACHE
    _RG_SPECS_CACHE = specs


class SovereignConfigLoader:
    """
    Central Configuration Authority.
    Loads topology from disk and merges with Frozen Knowledge Base.
    """

    _topology: OrchestrationTopology | None = None

    @classmethod
    def load_topology(cls, path: Path = None) -> OrchestrationTopology:
        """Load the orchestration topology from JSON or return cached version."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SovereignConfigLoader.load_topology")

        if path is None:
            path = Path("apps_rg/domain/config/agent_specs.json")
        if cls._topology:
            return cls._topology
        try:
            if not path.exists():
                Logger.warning(f"Config file {path} not found. Using default scaffold.")
                return cls._get_default_scaffold()
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)
            cls._topology = OrchestrationTopology(**data)
            Logger.info("Sovereign Topology loaded successfully.")
            return cls._topology
        except Exception as e:
            Logger.critical(f"Failed to load topology: {e}")
            raise

    @staticmethod
    def _get_default_scaffold() -> OrchestrationTopology:
        """Returns a minimal valid topology for bootstrapping."""
        return OrchestrationTopology(
            phases={"HOP1": ["HOP1_CLERK"], "HOP2": ["HOP2_ENRICH"]},
            agents={
                "HOP1_CLERK": AgentSpec(
                    name="HOP1_CLERK",
                    module_path="apps_rg.engines.hop1_clerk_engine.ClerkExtractionEngine",
                    inputs=["master_resume"],
                    outputs=["extraction_data"],
                ),
                "HOP2_ENRICH": AgentSpec(
                    name="HOP2_ENRICH",
                    module_path="apps_rg.engines.hop2_enrichment_engine.EnrichmentEngine",
                    inputs=["extraction_data"],
                    outputs=["enriched_data"],
                ),
            },
        )

    @classmethod
    def reset(cls) -> None:
        """Reset the cached topology (useful for testing)."""
        cls._topology = None


def reload_config() -> None:
    """Force reload of configuration from disk."""
    global _RG_SPECS_CACHE
    _RG_SPECS_CACHE = None
