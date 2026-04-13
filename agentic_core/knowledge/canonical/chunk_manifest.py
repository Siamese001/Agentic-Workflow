"""ChunkManifest — full metadata sidecar bound to each canonical chunk.

Produced at ingestion time (Pipeline B Phase B2 / 00C §Dual Storage Pattern).
Every chunk that reaches the vector store and sparse index carries one of these
so that query-time pre-filters can enforce ACL, tenant, freshness, and version
without reading the raw chunk content.

Architecture reference: 00C_index_materialization_runtime_handoff.md §Canonical Metadata Store
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


class FreshnessBand:
    """Constants for freshness tiers.

    Architecture reference: 00C §Freshness / Temporal sidecar.
    """

    HOT = "hot"  # < 7 days
    WARM = "warm"  # 7–90 days
    COLD = "cold"  # > 90 days

    @classmethod
    def from_date(cls, effective_date: datetime, now: datetime | None = None) -> str:
        """Derive freshness band from effective date."""
        now = now or datetime.utcnow()
        delta_days = (now - effective_date).days
        if delta_days < 7:
            return cls.HOT
        if delta_days < 90:
            return cls.WARM
        return cls.COLD

    @classmethod
    def ordered(cls) -> list[str]:
        """Return bands ordered hottest → coldest."""
        return [cls.HOT, cls.WARM, cls.COLD]


@dataclass
class AclSidecar:
    """Access-control sidecar per 00C §Canonical Metadata Store.

    Attributes
    ----------
    allowed_principals : list[str]
        Role/principal names that may access this chunk.
    tenant_id : str
        Owning tenant identifier.
    confidentiality_tier : str
        One of: "public", "internal", "restricted", "classified".
    """

    allowed_principals: list[str] = field(default_factory=list)
    tenant_id: str = "default"
    confidentiality_tier: str = "internal"

    def allows(self, principal: str) -> bool:
        """Return True if *principal* is explicitly allowed or list is empty (open)."""
        if not self.allowed_principals:
            return True
        return principal in self.allowed_principals


@dataclass
class FreshnessSidecar:
    """Temporal / freshness sidecar per 00C §Search Surfaces.

    Attributes
    ----------
    freshness_band : str
        ``FreshnessBand`` constant.
    effective_date : datetime | None
        Date from which this chunk is valid.
    expiry_date : datetime | None
        Date after which this chunk should not be served; ``None`` = no expiry.
    """

    freshness_band: str = FreshnessBand.WARM
    effective_date: datetime | None = None
    expiry_date: datetime | None = None

    def is_expired(self, now: datetime | None = None) -> bool:
        """Return True if chunk has passed its expiry date."""
        if self.expiry_date is None:
            return False
        now = now or datetime.utcnow()
        return now > self.expiry_date

    def is_warmer_than(self, band: str) -> bool:
        """Return True if this chunk's band is at least as fresh as *band*."""
        order = FreshnessBand.ordered()
        try:
            self_idx = order.index(self.freshness_band)
            target_idx = order.index(band)
        except ValueError:
            return False
        return self_idx <= target_idx  # lower index = hotter


@dataclass
class ChunkManifest:
    """Full metadata sidecar for a canonical chunk.

    Immutable after ingestion.  Stored in the Canonical Metadata Store
    alongside the vector store entry so query-time pre-filters can operate
    without fetching raw content.

    Architecture reference: 00C §Dual Storage Pattern — Canonical Metadata Store row.

    Attributes
    ----------
    chunk_id : str
        Stable identifier for this chunk version.
    raw_text : str
        Canonical source text (immutable truth).
    enriched_json : dict
        Contextual / enriched representation (headings, symbols, tables …).
    content_hash : str
        SHA-256 of ``raw_text`` for integrity / dedup checks.
    parent_id : str | None
        Parent chunk or document ID in the lineage graph (``None`` for roots).
    child_ids : list[str]
        Ordered list of child chunk IDs.
    acl : AclSidecar
        Access-control metadata.
    freshness : FreshnessSidecar
        Temporal / freshness metadata.
    schema_version : str
        Schema version this chunk was indexed under.
    embedding_schema_version : str
        Embedding model version used for the stored vectors.
    provenance : dict
        Source file, extraction method, processing chain, etc.
    modality : str
        One of: "text", "code", "table", "image".
    raw_text_vector : list[float] | None
        Dense vector over ``raw_text`` (populated post-embedding).
    contextual_text_vector : list[float] | None
        Dense vector over the enriched contextual representation.
    custom_attributes : dict
        Arbitrary corpus-specific attributes.
    """

    chunk_id: str
    raw_text: str
    enriched_json: dict[str, Any] = field(default_factory=dict)
    content_hash: str = ""
    parent_id: str | None = None
    child_ids: list[str] = field(default_factory=list)
    acl: AclSidecar = field(default_factory=AclSidecar)
    freshness: FreshnessSidecar = field(default_factory=FreshnessSidecar)
    schema_version: str = "1.0"
    embedding_schema_version: str = "1.0"
    provenance: dict[str, Any] = field(default_factory=dict)
    modality: str = "text"
    raw_text_vector: list[float] | None = None
    contextual_text_vector: list[float] | None = None
    custom_attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.content_hash and self.raw_text:
            self.content_hash = hashlib.sha256(self.raw_text.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage / transport."""
        return {
            "chunk_id": self.chunk_id,
            "raw_text": self.raw_text,
            "enriched_json": self.enriched_json,
            "content_hash": self.content_hash,
            "parent_id": self.parent_id,
            "child_ids": self.child_ids,
            "acl": {
                "allowed_principals": self.acl.allowed_principals,
                "tenant_id": self.acl.tenant_id,
                "confidentiality_tier": self.acl.confidentiality_tier,
            },
            "freshness": {
                "freshness_band": self.freshness.freshness_band,
                "effective_date": self.freshness.effective_date.isoformat()
                if self.freshness.effective_date
                else None,
                "expiry_date": self.freshness.expiry_date.isoformat() if self.freshness.expiry_date else None,
            },
            "schema_version": self.schema_version,
            "embedding_schema_version": self.embedding_schema_version,
            "provenance": self.provenance,
            "modality": self.modality,
            "custom_attributes": self.custom_attributes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChunkManifest":
        """Reconstruct from serialized dict."""
        acl_data = data.get("acl", {})
        freshness_data = data.get("freshness", {})

        acl = AclSidecar(
            allowed_principals=acl_data.get("allowed_principals", []),
            tenant_id=acl_data.get("tenant_id", "default"),
            confidentiality_tier=acl_data.get("confidentiality_tier", "internal"),
        )

        eff = freshness_data.get("effective_date")
        exp = freshness_data.get("expiry_date")
        freshness = FreshnessSidecar(
            freshness_band=freshness_data.get("freshness_band", FreshnessBand.WARM),
            effective_date=datetime.fromisoformat(eff) if eff else None,
            expiry_date=datetime.fromisoformat(exp) if exp else None,
        )

        manifest = cls(
            chunk_id=data["chunk_id"],
            raw_text=data.get("raw_text", ""),
            enriched_json=data.get("enriched_json", {}),
            content_hash=data.get("content_hash", ""),
            parent_id=data.get("parent_id"),
            child_ids=data.get("child_ids", []),
            acl=acl,
            freshness=freshness,
            schema_version=data.get("schema_version", "1.0"),
            embedding_schema_version=data.get("embedding_schema_version", "1.0"),
            provenance=data.get("provenance", {}),
            modality=data.get("modality", "text"),
            custom_attributes=data.get("custom_attributes", {}),
        )
        return manifest


__all__ = [
    "AclSidecar",
    "ChunkManifest",
    "FreshnessBand",
    "FreshnessSidecar",
]
