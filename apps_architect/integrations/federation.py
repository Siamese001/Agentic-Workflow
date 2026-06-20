"""Multi-repo pattern federation — DS-6.

Plan: ``.codex/plans/apps-architect-deferred-scope-b8e3f1.md`` DW5 DS-6.

Enables cross-repo pattern sharing: export patterns to JSON, import from
remote repos, and merge federated collections.
"""

from __future__ import annotations

import json as _json
import logging
from pathlib import Path
from typing import Tuple

from apps_architect.types.architect_types import Pattern, PatternCollection
from apps_architect.types.schema_versioning import pattern_to_dict, pattern_from_dict

_log = logging.getLogger(__name__)


class FederationExporter:
    """Exports pattern collections for cross-repo sharing."""

    @staticmethod
    def to_json(collection: PatternCollection, indent: int = 2) -> str:
        data = {
            "federation_version": "1.0",
            "source_repo": "Agentic-Workflow-FRESH",
            "collection_digest": collection.collection_digest,
            "scan_timestamp": collection.scan_timestamp.isoformat(),
            "pattern_count": len(collection.patterns),
            "patterns": [pattern_to_dict(p) for p in collection.patterns],
        }
        return _json.dumps(data, indent=indent)

    @staticmethod
    def to_file(collection: PatternCollection, path: str | Path) -> Path:
        fp = Path(path)
        fp.write_text(FederationExporter.to_json(collection), encoding="utf-8")
        _log.info("Exported %d patterns to %s", len(collection.patterns), fp)
        return fp


class FederationImporter:
    """Imports pattern collections from remote repos."""

    @staticmethod
    def from_json(data: str) -> PatternCollection:
        doc = _json.loads(data)
        patterns = tuple(pattern_from_dict(p) for p in doc.get("patterns", []))
        return PatternCollection.from_patterns(patterns)

    @staticmethod
    def from_file(path: str | Path) -> PatternCollection:
        return FederationImporter.from_json(Path(path).read_text(encoding="utf-8"))


class FederationMerger:
    """Merges federated collections with deduplication."""

    @staticmethod
    def merge(*collections: PatternCollection) -> PatternCollection:
        seen: set[str] = set()
        merged: list[Pattern] = []
        for col in collections:
            for p in col.patterns:
                if p.pattern_id not in seen:
                    merged.append(p)
                    seen.add(p.pattern_id)
        return PatternCollection.from_patterns(tuple(merged))

    @staticmethod
    def diff(local: PatternCollection, remote: PatternCollection) -> dict[str, list[str]]:
        local_ids = {p.pattern_id for p in local.patterns}
        remote_ids = {p.pattern_id for p in remote.patterns}
        return {
            "only_local": sorted(local_ids - remote_ids),
            "only_remote": sorted(remote_ids - local_ids),
            "shared": sorted(local_ids & remote_ids),
        }


__all__ = ["FederationExporter", "FederationImporter", "FederationMerger"]
