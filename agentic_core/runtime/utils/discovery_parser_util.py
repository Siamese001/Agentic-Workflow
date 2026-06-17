"""
File: agentic_core/utils/discovery_parser.py
Hunk 1: Immutability Propagation to Metadata Parser
Location: Lines 45-72
Description: Updating the JSON parser to cast loaded agent metadata into Final Mapping structures.
[CRITICAL ANALYSIS] legacy editor (Junior AI) typically uses simple `json.load`, yielding mutable dictionaries.
By wrapping the dictionary output in a Mapping at the ingestion layer and marking it Final,
we prevent 'Junior' agents from modifying agent fingerprints or capability flags during an active Mission,
preventing state-drift attacks. This strictly enforces the read-only nature of the discovery manifest.
"""

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final


class AgentListMapping(Mapping[str, Any]):
    """
    [SSOT] A read-only Mapping wrapper that enforces metadata immutability.
    Prevents pop, clear, or __setitem__ operations during mission execution.
    """

    def __init__(self, data: dict[str, Any]):
        self._data = data

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        return iter(self._data)


def load_hardened_agent_metadata(discovery_path: Path) -> Mapping[str, Any]:
    """
    Loads agent_discovery_full.json into a read-only Mapping.
    Ensures UTF-8 encoding stability across all system environments.
    """
    with open(discovery_path, encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
    return AgentListMapping(data)


AGENT_METADATA: Final[Mapping[str, Any]] = load_hardened_agent_metadata(Path("agent_discovery_full.json"))
