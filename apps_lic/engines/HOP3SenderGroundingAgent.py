"""
HOP-3: Sender Grounding Agent (V2 Architecture).

Extracts and structures sender capabilities from static knowledge base files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_lic.shared.v2_patterns.agent_base import V2AgentBase
from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry


class HOP3SenderGroundingAgent(V2AgentBase):
    """
    V2 Implementation of HOP-3.

    Architecture:
    - Base: V2AgentBase
    - Input: Static JSON files (Resume, Knowledge Base) defined in Config.
    - Logic: Extraction & Structuring of capabilities.
    - Output: 'hop3_sender_grounding' to ImmutableStagingBuffer.
    """

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute grounding extraction.

        1. Identify source files from config.
        2. Load and parse JSON content.
        3. Extract specific targets (Team, Products, etc.).
        4. Write immutable output.
        """
        config = self.config.sender_grounding_agent
        grounding = {
            "team_members": [],
            "products": [],
            "case_studies": [],
            "quantifiable_achievements": [],
            "raw_evidence": {},
        }
        loaded_sources = []

        registry.add_trace(
            "PHASE_STEP", {"action": "loading_sources", "files": config.source_files}
        )

        for filename in config.source_files:
            # Resolve file path (assuming relative to cwd or specific data dir)
            file_path = Path(filename)

            if not file_path.exists():
                registry.add_trace("SOURCE_MISSING", {"file": filename})
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)

                self._extract_data(data, filename, grounding)
                loaded_sources.append(filename)

            except json.JSONDecodeError:
                registry.add_trace("DATA_ERROR", {"file": filename, "error": "Invalid JSON"})
            except Exception as e:
                registry.add_trace("DATA_ERROR", {"file": filename, "error": str(e)})

        # Validate we got *something*
        if not loaded_sources:
            registry.add_trace("CRITICAL_FAILURE", {"msg": "No source files loaded"})
            # We might choose to raise here if grounding is strictly required
            # raise RuntimeError("Failed to load any grounding sources")

        # Write Output
        output_data = {
            "sender_grounding": grounding,
            "source_files_loaded": loaded_sources,
            "stats": {k: len(v) for k, v in grounding.items() if isinstance(v, list)},
        }

        buffer.write_once("hop3_sender_grounding", output_data)

        registry.add_trace(
            "DECISION_FINAL",
            {
                "loaded": len(loaded_sources),
                "products": len(grounding["products"]),
                "achievements": len(grounding["quantifiable_achievements"]),
            },
        )

    def _extract_data(self, data: dict[str, Any], filename: str, grounding: dict[str, Any]) -> None:
        """Extract fields based on file content heuristics."""

        # Heuristic 1: Sender Knowledge Base Structure
        if "whitelisted_team_members" in data:
            grounding["team_members"].extend(
                [m["name"] for m in data["whitelisted_team_members"] if "name" in m]
            )
        if "whitelisted_products" in data:
            grounding["products"].extend(
                [p["name"] for p in data["whitelisted_products"] if "name" in p]
            )
        if "whitelisted_case_studies" in data:
            grounding["case_studies"].extend(
                [c["client"] for c in data["whitelisted_case_studies"] if "client" in c]
            )
        if "quantifiable_achievements" in data:
            grounding["quantifiable_achievements"].extend(data["quantifiable_achievements"])

        # Heuristic 2: Master Resume Structure
        if "professional_experience" in data:
            for exp in data["professional_experience"]:
                company = exp.get("company", "Unknown")
                grounding["raw_evidence"].setdefault("companies", []).append(company)

                # Extract bullet achievements if pool exists
                if "bullet_pool" in exp:
                    grounding["raw_evidence"].setdefault("achievements", []).extend(
                        exp["bullet_pool"][:3]  # Top 3 per company cap
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
