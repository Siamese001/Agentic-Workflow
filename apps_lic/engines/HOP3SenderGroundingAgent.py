"""
HOP-3: Sender Grounding Agent (V2.5 Architecture).

LIC Sovereign Grounder.
Implements targeted whitelist extraction and achievement binding.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from apps_lic.utils.lic_agent_base_util import LICAgentBase
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
class HOP3SenderGroundingAgent(LICAgentBase, SubatomicTestingMixin):
    """
    LIC Sovereign Grounder.

    Architecture:
    - Base: LICAgentBase
    - Input: Static JSON files (Resume, Knowledge Base) defined in Config.
    - Logic: Whitelist Extraction -> Achievement Binding -> Metric Mapping
    - Output: 'hop3_sender_grounding' with grounding_whitelists and metric_source_map
    """

    # Sovereign Configuration
    grounding_rules: dict[str, str] = field(
        default_factory=lambda: {"strict_mode": "enabled", "default_region": "us-east-1"}
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        # CRITICAL: Trigger Core Lock & Healing
        super().__post_init__()

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute grounding extraction.

        1. Read Sovereign Config.
        2. Specialist Extraction Loop.
        3. Metric Source Binding (LIC-QA-041 Compliance).
        4. Write to Immutable Buffer.
        """
        # 1. Read Sovereign Config
        try:
            config = self.config.sender_grounding_agent
            source_files = config.source_files
            if not source_files:
                raise ValueError("No source files defined in agent_specs")
        except Exception as e:
            registry.add_trace("DATA_ERROR", {"msg": "Missing grounding config"})
            raise RuntimeError("HOP-3 missing configuration targets") from e

        registry.add_trace("PHASE_STEP", {"action": "starting_grounding_extraction"})

        grounding_map = {"team_members": [], "products": [], "achievements": [], "case_studies": []}
        loaded_sources = []

        # Use field factory for mutable defaults
        if not hasattr(self, "_grounding_map_initialized"):
            self._grounding_map_initialized = True
            self._default_grounding_map = {
                "team_members": [],
                "products": [],
                "achievements": [],
                "case_studies": [],
            }

        # 2. Specialist Extraction Loop
        for filename in source_files:
            data = self._load_json_file(filename)
            if data:
                self._extract_grounded_entities(data, grounding_map, registry)
                loaded_sources.append(filename)

        # 3. Metric Source Binding (LIC-QA-041 Compliance)
        # Organizes achievements by metric for HOP-5 bullet generation
        metric_map = self._map_metrics(grounding_map["achievements"])

        # 4. Write to Immutable Buffer
        output_data = {
            "grounding_whitelists": grounding_map,
            "metric_source_map": metric_map,
            "metadata": {"sources_loaded": len(loaded_sources)},
        }

        buffer.write_once("hop3_sender_grounding", output_data)
        registry.add_trace("DECISION_FINAL", {"status": "GROUNDING_COMPLETE"})

    def _load_json_file(self, filename: str) -> dict[str, Any] | None:
        """Load and parse a JSON file, returning None on failure."""
        file_path = Path(filename)
        if not file_path.exists():
            return None
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return None

    def _extract_grounded_entities(self, data: dict, mapping: dict, reg: TraceRegistry) -> None:
        """Strictly extracts entities based on whitelist targets."""
        # Map config targets to data keys
        target_key_map = {
            "products": ["whitelisted_products", "products"],
            "team_members": ["whitelisted_team_members", "team_members"],
            "achievements": ["quantifiable_achievements", "achievements"],
            "case_studies": ["whitelisted_case_studies", "case_studies"],
        }

        for target in self.config.sender_grounding_agent.extraction_targets:
            if target in target_key_map:
                for data_key in target_key_map[target]:
                    if data_key in data:
                        items = data[data_key]
                        if isinstance(items, list):
                            # Extract names if items are dicts, otherwise use raw
                            extracted = []
                            for item in items:
                                if isinstance(item, dict):
                                    extracted.append(
                                        item.get("name", item.get("client", str(item)))
                                    )
                                else:
                                    extracted.append(item)
                            mapping[target].extend(extracted)
                            reg.add_trace(
                                "ENTITY_EXTRACTED", {"category": target, "count": len(extracted)}
                            )
                        break

    def _map_metrics(self, achievements: list[Any]) -> dict[str, list[str]]:
        """Map achievements to metric categories for HOP-5 generation."""
        metric_map = {"revenue": [], "efficiency": [], "growth": [], "other": []}

        for achievement in achievements:
            text = str(achievement).lower()
            if any(kw in text for kw in ["revenue", "sales", "$", "million", "billion"]):
                metric_map["revenue"].append(str(achievement))
            elif any(kw in text for kw in ["efficiency", "reduced", "saved", "cost"]):
                metric_map["efficiency"].append(str(achievement))
            elif any(kw in text for kw in ["growth", "increased", "expanded", "%"]):
                metric_map["growth"].append(str(achievement))
            else:
                metric_map["other"].append(str(achievement))

        return metric_map

    def _extract_data_legacy(
        self, data: dict[str, Any], filename: str, grounding: dict[str, Any]
    ) -> None:
        """Legacy extraction method - kept for backward compatibility."""
        # Heuristic 1: Sender Knowledge Base Structure
        if "whitelisted_team_members" in data:
            grounding.setdefault("team_members", []).extend(
                [m["name"] for m in data["whitelisted_team_members"] if "name" in m]
            )
        if "whitelisted_products" in data:
            grounding.setdefault("products", []).extend(
                [p["name"] for p in data["whitelisted_products"] if "name" in p]
            )

    def heal_repository(self) -> None:
        """Check integrity of source files."""
        super().heal_repository()

        # V2 Self-Healing: Check if configured files exist
        if hasattr(self, "config"):
            for f in self.config.sender_grounding_agent.source_files:
                path = Path(f)
                if not path.exists():
                    pass  # Would log warning about missing file
