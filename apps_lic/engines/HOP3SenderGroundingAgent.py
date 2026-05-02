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
        raw_evidence: dict[str, list] = {"companies": [], "achievements": []}
        for filename in source_files:
            data = self._load_json_file(filename, registry=registry)
            if data:
                self._extract_grounded_entities(data, grounding_map, registry)
                self._extract_raw_evidence(data, raw_evidence)
                loaded_sources.append(filename)

        # 3. Metric Source Binding (LIC-QA-041 Compliance)
        # Organizes achievements by metric for HOP-5 bullet generation
        metric_map = self._map_metrics(grounding_map["achievements"])

        # 3b. Mutual-Connection Priming (W2-P5 follow-up wiring 2026-05-01).
        # Pure resolver — empty/missing candidate list yields empty priming
        # line, which HOP5 interprets as "use default opener". Candidates
        # are sourced from mission_input["mutual_connections"] when the
        # caller supplies them; the resolver tolerates absence cleanly.
        from apps_lic.engines.mutual_connection_resolver import (
            MutualConnectionResolver,
        )

        try:
            mission_input = buffer.read("mission_input") or {}
        except Exception:
            mission_input = {}
        candidates = mission_input.get("mutual_connections", []) or []
        priming_line = MutualConnectionResolver().resolve_priming_line(candidates)

        # 4. Write to Immutable Buffer
        # ``sender_grounding`` and ``source_files_loaded`` are the
        # canonical test-contract keys; ``grounding_whitelists`` and
        # ``metadata.sources_loaded`` are preserved for back-compat.
        sender_grounding = {
            "products": list(grounding_map.get("products", [])),
            "team_members": list(grounding_map.get("team_members", [])),
            "case_studies": list(grounding_map.get("case_studies", [])),
            "quantifiable_achievements": list(grounding_map.get("achievements", [])),
            "raw_evidence": raw_evidence,
        }
        output_data = {
            "grounding_whitelists": grounding_map,
            "sender_grounding": sender_grounding,
            "source_files_loaded": list(loaded_sources),
            "metric_source_map": metric_map,
            "mutual_connection_priming_line": priming_line,
            "metadata": {
                "sources_loaded": len(loaded_sources),
                "mutual_candidates_considered": len(candidates),
                "priming_line_rendered": bool(priming_line),
            },
        }

        buffer.write_once("hop3_sender_grounding", output_data)
        registry.add_trace(
            "DECISION_FINAL",
            {"status": "GROUNDING_COMPLETE", "priming_rendered": bool(priming_line)},
        )

    def _load_json_file(self, filename: str, registry: Any | None = None) -> dict[str, Any] | None:
        """Load and parse a JSON file, returning None on failure.

        Emits ``SOURCE_MISSING`` trace when the file is absent and
        ``DATA_ERROR`` with "Invalid JSON" when parsing fails. The
        ``registry`` argument is optional to preserve the legacy
        callsite signature.
        """
        file_path = Path(filename)
        if not file_path.exists():
            if registry is not None:
                try:
                    registry.add_trace("SOURCE_MISSING", {"file": filename})
                except Exception:  # guardian: allow-log-and-swallow -- trace path must not mask file outcome
                    pass
            return None
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as exc:
            if registry is not None:
                try:
                    registry.add_trace(
                        "DATA_ERROR",
                        {"file": filename, "error": f"Invalid JSON: {exc}"},
                    )
                except Exception:  # guardian: allow-log-and-swallow -- trace path must not mask parse outcome
                    pass
            return None
        except Exception as exc:  # guardian: allow-log-and-swallow -- broad IO catch with traced fallback
            if registry is not None:
                try:
                    registry.add_trace(
                        "DATA_ERROR", {"file": filename, "error": str(exc)}
                    )
                except Exception:
                    pass
            return None

    def _extract_raw_evidence(
        self, data: dict[str, Any], raw_evidence: dict[str, list]
    ) -> None:
        """Extract resume-shaped raw evidence (companies + achievements).

        Looks for ``professional_experience`` blocks and pulls each
        entry's ``company`` plus its ``bullet_pool`` items into the
        cross-source ``raw_evidence`` aggregate. Tolerates missing
        keys and non-list shapes silently.
        """
        experience = data.get("professional_experience")
        if not isinstance(experience, list):
            return
        for entry in experience:
            if not isinstance(entry, dict):
                continue
            company = entry.get("company")
            if isinstance(company, str) and company:
                raw_evidence["companies"].append(company)
            bullets = entry.get("bullet_pool")
            if isinstance(bullets, list):
                for bullet in bullets:
                    if isinstance(bullet, str) and bullet:
                        raw_evidence["achievements"].append(bullet)

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
