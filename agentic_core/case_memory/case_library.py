"""CaseLibrary — Entity/relation wiring for case memory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class BridgeProtocol(Protocol):
    """Protocol for bridge implementations."""

    def create_entity(self, entity_type: str, properties: dict[str, Any]) -> str:
        """Create an entity and return its ID."""
        ...

    def create_relation(self, from_id: str, to_id: str, relation_type: str) -> str:
        """Create a relation between entities."""
        ...

    def commit(self) -> None:
        """Commit pending changes."""
        ...


@dataclass(frozen=True)
class CaseRecord:
    """Frozen case record for deterministic serialization."""

    artifact_type: str = "CASE_RECORD"
    case_id: str = ""
    timestamp_utc: int = 0
    query_hash: str = ""
    context_summary: str = ""


@dataclass(frozen=True)
class HealerBundle:
    """Frozen healer bundle for healing run records."""

    artifact_type: str = "HEALER_BUNDLE"
    bundle_hash: str = ""
    case_ref: str = ""
    healer_name: str = ""
    timestamp_utc: int = 0


@dataclass(frozen=True)
class HITLPreferenceRecord:
    """Frozen HITL preference record."""

    artifact_type: str = "HITL_PREFERENCE_RECORD"
    preference_hash: str = ""
    case_ref: str = ""
    approved: bool = False
    timestamp_utc: int = 0


class CaseLibrary:
    """Library for storing and retrieving case records with bridge injection."""

    def __init__(self, bridge: BridgeProtocol):
        self._bridge = bridge

    def store(self, record: Any) -> bool:
        """Store a record and create entity/relation wiring."""
        if not hasattr(record, "artifact_type"):
            return False

        artifact_type = getattr(record, "artifact_type", "")
        if artifact_type not in {"CASE_RECORD", "HEALER_BUNDLE", "HITL_PREFERENCE_RECORD", "HITL_PREFERENCE"}:
            return False

        entity_id = self._bridge.create_entity(
            artifact_type,
            {
                "name": f"{record.artifact_type}_{getattr(record, 'case_id', 'unknown')}",
                **self._record_to_dict(record),
            },
        )

        if artifact_type == "CASE_RECORD":
            self._bridge.create_relation(entity_id, entity_id, "lineage_of")
            self._bridge.create_relation(entity_id, entity_id, "governed_by_policy")
            self._bridge.create_relation(entity_id, entity_id, "sourced_from_adg_node")

        if artifact_type == "HEALER_BUNDLE":
            self._bridge.create_relation(entity_id, entity_id, "healer_resolved")

        if artifact_type in {"HITL_PREFERENCE_RECORD", "HITL_PREFERENCE"}:
            self._bridge.create_relation(entity_id, entity_id, "hitl_approved")

        self._bridge.commit()
        return True

    def _record_to_dict(self, record: Any) -> dict[str, Any]:
        """Convert a record to dictionary."""
        return {
            k: getattr(record, k)
            for k in dir(record)
            if not k.startswith("_") and not callable(getattr(record, k))
        }

    def get(self, case_id: str) -> CaseRecord | None:
        """Retrieve a case record by ID."""
        return None  # Stub implementation
