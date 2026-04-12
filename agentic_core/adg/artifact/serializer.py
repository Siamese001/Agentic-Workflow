"""ADG Artifact Serializer — deterministic JSON I/O and artifact diff.

Responsibilities:
- Serialize ADGArtifact to deterministic JSON (sort_keys=True, no floats)
- Deserialize from JSON back to ADGArtifact (round-trip safe)
- Produce a structural diff between two artifacts for CI drift detection
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.adg.artifact.builder import ADGArtifact

logger = logging.getLogger(__name__)


def serialize_artifact(artifact: ADGArtifact, indent: int = 2) -> str:
    """Serialize an ADGArtifact to deterministic JSON string."""
    return json.dumps(artifact.to_dict(), sort_keys=True, indent=indent)


def write_artifact(artifact: ADGArtifact, output_path: Path) -> Path:
    """Write artifact to a file, creating parent directories as needed."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    text = serialize_artifact(artifact)
    output_path.write_text(text, encoding="utf-8")
    logger.info("ADG artifact written: %s (digest=%s)", output_path, artifact.artifact_digest[:12])
    return output_path


def load_artifact(source: Path | str) -> dict:
    """Load a raw artifact dict from a JSON file (no schema validation)."""
    path = Path(source)
    return json.loads(path.read_text(encoding="utf-8"))


def _set_diff(a: list, b: list) -> tuple[list, list]:
    """Return (added, removed) between two sorted lists.

    added   = items in b (current) but not in a (baseline)
    removed = items in a (baseline) but not in b (current)
    """
    sa, sb = set(a), set(b)
    return sorted(sb - sa), sorted(sa - sb)


def diff_artifacts(
    baseline_path: Path | str,
    current_path: Path | str,
) -> dict:
    """Produce a deterministic structural diff between two artifact JSON files.

    Returns a dict with:
      schema_versions: {baseline, current}
      commit_shas: {baseline, current}
      digest_changed: bool
      entities: {added_count, removed_count, added[:20], removed[:20]}
      relations: {added_count, removed_count}
      unresolved_imports: {baseline_count, current_count, delta}
      layer_violations: {baseline_count, current_count, delta}
      orphan_modules: {baseline_count, current_count, delta}
      identity_health_delta: dict of kind-level deltas
    """
    baseline = load_artifact(baseline_path)
    current = load_artifact(current_path)

    baseline_entity_names = [e["adg_name"] for e in baseline.get("entities", [])]
    current_entity_names = [e["adg_name"] for e in current.get("entities", [])]
    entities_added, entities_removed = _set_diff(baseline_entity_names, current_entity_names)

    baseline_rel_keys = [
        f"{r['from_name']}|{r['relation_type']}|{r['to_name']}" for r in baseline.get("relations", [])
    ]
    current_rel_keys = [
        f"{r['from_name']}|{r['relation_type']}|{r['to_name']}" for r in current.get("relations", [])
    ]
    rels_added, rels_removed = _set_diff(baseline_rel_keys, current_rel_keys)

    baseline_metrics = baseline.get("structural_metrics", {})
    current_metrics = current.get("structural_metrics", {})

    baseline_health = baseline.get("identity_health", {}).get("by_identity_kind", {})
    current_health = current.get("identity_health", {}).get("by_identity_kind", {})
    all_kinds = sorted(set(baseline_health) | set(current_health))
    identity_health_delta = {k: current_health.get(k, 0) - baseline_health.get(k, 0) for k in all_kinds}

    return {
        "schema_versions": {
            "baseline": baseline.get("schema_version", ""),
            "current": current.get("schema_version", ""),
        },
        "commit_shas": {
            "baseline": baseline.get("commit_sha", ""),
            "current": current.get("commit_sha", ""),
        },
        "digest_changed": baseline.get("artifact_digest", "") != current.get("artifact_digest", ""),
        "entities": {
            "baseline_count": len(baseline_entity_names),
            "current_count": len(current_entity_names),
            "added_count": len(entities_added),
            "removed_count": len(entities_removed),
            "added": entities_added[:20],
            "removed": entities_removed[:20],
        },
        "relations": {
            "baseline_count": len(baseline_rel_keys),
            "current_count": len(current_rel_keys),
            "added_count": len(rels_added),
            "removed_count": len(rels_removed),
        },
        "unresolved_imports": {
            "baseline_count": baseline_metrics.get("unresolved_count", 0),
            "current_count": current_metrics.get("unresolved_count", 0),
            "delta": current_metrics.get("unresolved_count", 0) - baseline_metrics.get("unresolved_count", 0),
        },
        "layer_violations": {
            "baseline_count": baseline_metrics.get("layer_violation_count", 0),
            "current_count": current_metrics.get("layer_violation_count", 0),
            "delta": (
                current_metrics.get("layer_violation_count", 0)
                - baseline_metrics.get("layer_violation_count", 0)
            ),
        },
        "orphan_modules": {
            "baseline_count": baseline_metrics.get("orphan_module_count", 0),
            "current_count": current_metrics.get("orphan_module_count", 0),
            "delta": (
                current_metrics.get("orphan_module_count", 0) - baseline_metrics.get("orphan_module_count", 0)
            ),
        },
        "identity_health_delta": identity_health_delta,
    }


__all__ = [
    "serialize_artifact",
    "write_artifact",
    "load_artifact",
    "diff_artifacts",
]
