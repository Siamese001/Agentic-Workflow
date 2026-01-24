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

from .schemas import RGAgentSpecs, OrchestrationTopology, AgentSpec

Logger = logging.getLogger(__name__)

# Module-level cache
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

    if _RG_SPECS_CACHE and not force_reload:
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
        return specs


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


# =============================================================================
# SOVEREIGN CONFIG LOADER (Phase 2 Hardening)
# =============================================================================


class SovereignConfigLoader:
    """
    Central Configuration Authority.
    Loads topology from disk and merges with Frozen Knowledge Base.
    """

    _topology: OrchestrationTopology | None = None

    @classmethod
    def load_topology(cls, path: Path = None) -> OrchestrationTopology:
        """Load the orchestration topology from JSON or return cached version."""
        if path is None:
            path = Path("apps_rg/domain/config/agent_specs.json")

        if cls._topology:
            return cls._topology

        try:
            # If file doesn't exist yet, return a default scaffolding
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
                    module_path="apps_rg.engines.hops.hop1_clerk_engine.ClerkExtractionEngine",
                    inputs=["master_resume"],
                    outputs=["extraction_data"],
                ),
                "HOP2_ENRICH": AgentSpec(
                    name="HOP2_ENRICH",
                    module_path="apps_rg.engines.hops.hop2_enrichment_engine.EnrichmentEngine",
                    inputs=["extraction_data"],
                    outputs=["enriched_data"],
                ),
            },
        )

    @classmethod
    def reset(cls) -> None:
        """Reset the cached topology (useful for testing)."""
        cls._topology = None
