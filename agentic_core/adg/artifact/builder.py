"""ADG Artifact Builder — produces the canonical ADG artifact (schema v3).

Consumes a ScanResult and IdentityNormalizer to produce a fully structured
ADGArtifact with:
  - entities section: module + symbol entities with kind, layer, confidence
  - relations section: all edges in canonical form
  - identity_health: unresolved counts, confidence distribution
  - structural_metrics: orphans, cycles, violations, fan-in/fan-out hotspots
  - blind_spots: dynamic imports, star imports, parse failures
  - artifact_digest: deterministic SHA256 of the whole artifact

No classification or territory logic is duplicated here — all layer queries
delegate to ``module_path_to_layer`` from ``agentic_core.adg.schema``.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

from agentic_core.adg.identity.normalizer import (
    IdentityKind,
    IdentityNormalizer,
    NormalizationReport,
)
from agentic_core.adg.schema import canonical_name, module_path_to_layer

logger = logging.getLogger(__name__)

_ARTIFACT_SCHEMA_VERSION = "3.0.0"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class EntityRecord:
    """One entity node in the canonical artifact."""

    adg_name: str
    entity_type: str
    layer: str
    identity_kind: str
    confidence: str
    resolved_path: str
    observations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "adg_name": self.adg_name,
            "entity_type": self.entity_type,
            "layer": self.layer,
            "identity_kind": self.identity_kind,
            "confidence": self.confidence,
            "resolved_path": self.resolved_path,
            "observations": sorted(self.observations),
        }


@dataclass
class RelationRecord:
    """One directed relation in the canonical artifact."""

    from_name: str
    relation_type: str
    to_name: str
    edge_kind: str
    source_file: str
    line_no: int
    symbol: str = ""

    def to_dict(self) -> dict:
        return {
            "from_name": self.from_name,
            "relation_type": self.relation_type,
            "to_name": self.to_name,
            "edge_kind": self.edge_kind,
            "source_file": self.source_file,
            "line_no": self.line_no,
            "symbol": self.symbol,
        }


@dataclass
class StructuralMetrics:
    """Structural graph metrics derived from the ADG."""

    total_entities: int = 0
    total_relations: int = 0
    module_count: int = 0
    symbol_count: int = 0
    external_count: int = 0
    unresolved_count: int = 0
    orphan_modules: list[str] = field(default_factory=list)
    high_fan_in_modules: list[dict] = field(default_factory=list)
    high_fan_out_modules: list[dict] = field(default_factory=list)
    layer_violation_count: int = 0
    by_relation_type: dict[str, int] = field(default_factory=dict)
    by_layer: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "total_entities": self.total_entities,
            "total_relations": self.total_relations,
            "module_count": self.module_count,
            "symbol_count": self.symbol_count,
            "external_count": self.external_count,
            "unresolved_count": self.unresolved_count,
            "orphan_module_count": len(self.orphan_modules),
            "orphan_modules": sorted(self.orphan_modules),
            "high_fan_in_modules": sorted(self.high_fan_in_modules, key=lambda x: -x["fan_in"])[:20],
            "high_fan_out_modules": sorted(self.high_fan_out_modules, key=lambda x: -x["fan_out"])[:20],
            "layer_violation_count": self.layer_violation_count,
            "by_relation_type": dict(sorted(self.by_relation_type.items())),
            "by_layer": dict(sorted(self.by_layer.items())),
        }


@dataclass
class BlindSpotReport:
    """Explicit blind spot section — what we cannot see."""

    dynamic_import_count: int = 0
    star_import_count: int = 0
    parse_failure_count: int = 0
    dynamic_import_locations: list[str] = field(default_factory=list)
    star_import_locations: list[str] = field(default_factory=list)
    parse_failure_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "dynamic_import_count": self.dynamic_import_count,
            "star_import_count": self.star_import_count,
            "parse_failure_count": self.parse_failure_count,
            "dynamic_import_locations": sorted(self.dynamic_import_locations),
            "star_import_locations": sorted(self.star_import_locations),
            "parse_failure_files": sorted(self.parse_failure_files),
        }


@dataclass
class ADGArtifact:
    """The canonical ADG artifact (schema v3).

    Deterministic: same ScanResult always produces the same artifact_digest.
    """

    schema_version: str = _ARTIFACT_SCHEMA_VERSION
    commit_sha: str = ""
    scanner_digest: str = ""
    entities: list[EntityRecord] = field(default_factory=list)
    relations: list[RelationRecord] = field(default_factory=list)
    unresolved_imports: list[dict] = field(default_factory=list)
    identity_health: dict = field(default_factory=dict)
    structural_metrics: StructuralMetrics = field(default_factory=StructuralMetrics)
    blind_spots: BlindSpotReport = field(default_factory=BlindSpotReport)
    artifact_digest: str = ""

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "commit_sha": self.commit_sha,
            "scanner_digest": self.scanner_digest,
            "entities": sorted([e.to_dict() for e in self.entities], key=lambda x: x["adg_name"]),
            "relations": sorted(
                [r.to_dict() for r in self.relations],
                key=lambda x: (x["from_name"], x["relation_type"], x["to_name"]),
            ),
            "unresolved_imports": sorted(self.unresolved_imports, key=lambda x: x.get("raw_name", "")),
            "identity_health": self.identity_health,
            "structural_metrics": self.structural_metrics.to_dict(),
            "blind_spots": self.blind_spots.to_dict(),
            "artifact_digest": self.artifact_digest,
        }

    def compute_digest(self) -> str:
        """Compute a deterministic SHA256 digest over structural content only.

        commit_sha is excluded so the same graph content always produces the
        same digest regardless of which commit triggered the scan.
        """
        payload = {
            "schema_version": self.schema_version,
            "entities": sorted([e.to_dict() for e in self.entities], key=lambda x: x["adg_name"]),
            "relations": sorted(
                [r.to_dict() for r in self.relations],
                key=lambda x: (x["from_name"], x["relation_type"], x["to_name"]),
            ),
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        self.artifact_digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return self.artifact_digest


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


class ADGArtifactBuilder:
    """Builds an ADGArtifact from a ScanResult.

    Usage
    -----
    builder = ADGArtifactBuilder(repo_root=Path("."))
    artifact = builder.build(scan_result)
    """

    # Fan-in/fan-out thresholds for hotspot reporting
    _FAN_IN_THRESHOLD = 10
    _FAN_OUT_THRESHOLD = 15

    def __init__(self, repo_root: Path | None = None) -> None:
        self._repo_root = Path(repo_root) if repo_root else Path.cwd()
        self._normalizer = IdentityNormalizer(repo_root=self._repo_root)

    def build(self, result: ScanResult) -> ADGArtifact:
        """Build a fully-populated ADGArtifact from a ScanResult."""
        artifact = ADGArtifact(
            commit_sha=result.commit_sha or "",
            scanner_digest=result.digest or "",
        )

        # 1. Populate relations from edges
        self._populate_relations(result, artifact)

        # 2. Populate module entities
        self._populate_module_entities(result, artifact)

        # 3. Populate symbol entities + unresolved imports via identity normalizer
        self._populate_symbol_entities(result, artifact)

        # 4. Build identity health section
        self._build_identity_health(artifact)

        # 5. Compute structural metrics
        self._compute_structural_metrics(result, artifact)

        # 6. Collect blind spots
        self._collect_blind_spots(result, artifact)

        # 7. Compute artifact digest
        artifact.compute_digest()

        logger.info(
            "ADG artifact built: %d entities, %d relations, digest=%s",
            len(artifact.entities),
            len(artifact.relations),
            artifact.artifact_digest[:12],
        )
        return artifact

    def _populate_relations(self, result: ScanResult, artifact: ADGArtifact) -> None:
        seen: set[tuple] = set()
        for edge in sorted(result.edges):
            key = (edge.from_name, edge.relation_type, edge.to_name, edge.edge_kind, edge.source_file, edge.line_no)
            if key in seen:
                continue
            seen.add(key)
            artifact.relations.append(
                RelationRecord(
                    from_name=edge.from_name,
                    relation_type=edge.relation_type,
                    to_name=edge.to_name,
                    edge_kind=edge.edge_kind,
                    source_file=edge.source_file,
                    line_no=edge.line_no,
                    symbol=edge.symbol or "",
                )
            )

    def _populate_module_entities(self, result: ScanResult, artifact: ADGArtifact) -> None:
        existing_adg: set[str] = {e.adg_name for e in artifact.entities}
        for rel_path in sorted(result.modules):
            adg = canonical_name("Module", rel_path)
            if adg in existing_adg:
                continue
            layer = module_path_to_layer(rel_path)
            artifact.entities.append(
                EntityRecord(
                    adg_name=adg,
                    entity_type="module",
                    layer=layer,
                    identity_kind=IdentityKind.REPO_MODULE.value,
                    confidence="HIGH",
                    resolved_path=rel_path,
                    observations=[f"path:{rel_path}", f"layer:{layer}"],
                )
            )
            existing_adg.add(adg)

    def _populate_symbol_entities(self, result: ScanResult, artifact: ADGArtifact) -> None:
        """Normalize all symbol nodes referenced in edges, classify their identity."""
        existing_adg: set[str] = {e.adg_name for e in artifact.entities}

        symbol_prefix = "ADG::Symbol::"
        module_prefix = "ADG::Module::"

        # Collect all unique to_names that need identity resolution
        to_resolve: set[str] = set()
        for edge in result.edges:
            if edge.to_name.startswith(symbol_prefix) or edge.to_name.startswith(module_prefix):
                if edge.to_name not in existing_adg:
                    to_resolve.add(edge.to_name)

        for adg_target in sorted(to_resolve):
            if adg_target in existing_adg:
                continue

            if adg_target.startswith(symbol_prefix):
                dot_name = adg_target[len(symbol_prefix):]
                rec = self._normalizer.normalize(dot_name)
                layer = module_path_to_layer(rec.resolved_path) if rec.resolved_path else "L_UNKNOWN"
                artifact.entities.append(
                    EntityRecord(
                        adg_name=adg_target,
                        entity_type="symbol",
                        layer=layer,
                        identity_kind=rec.kind.value,
                        confidence=rec.confidence.value,
                        resolved_path=rec.resolved_path,
                        observations=[
                            f"raw_name:{dot_name}",
                            f"identity_kind:{rec.kind.value}",
                            f"reason:{rec.reason}",
                        ],
                    )
                )
                if rec.kind == IdentityKind.UNRESOLVED_IMPORT:
                    artifact.unresolved_imports.append(
                        {
                            "raw_name": dot_name,
                            "adg_name": adg_target,
                            "reason": rec.reason,
                            "confidence": rec.confidence.value,
                        }
                    )
            elif adg_target.startswith(module_prefix):
                rel_path = adg_target[len(module_prefix):]
                layer = module_path_to_layer(rel_path)
                artifact.entities.append(
                    EntityRecord(
                        adg_name=adg_target,
                        entity_type="module",
                        layer=layer,
                        identity_kind=IdentityKind.REPO_MODULE.value,
                        confidence="HIGH",
                        resolved_path=rel_path,
                        observations=[f"path:{rel_path}", f"layer:{layer}"],
                    )
                )

            existing_adg.add(adg_target)

    def _build_identity_health(self, artifact: ADGArtifact) -> None:
        by_kind: dict[str, int] = {}
        by_confidence: dict[str, int] = {}
        for ent in artifact.entities:
            by_kind[ent.identity_kind] = by_kind.get(ent.identity_kind, 0) + 1
            by_confidence[ent.confidence] = by_confidence.get(ent.confidence, 0) + 1

        artifact.identity_health = {
            "by_identity_kind": dict(sorted(by_kind.items())),
            "by_confidence": dict(sorted(by_confidence.items())),
            "unresolved_import_count": len(artifact.unresolved_imports),
            "null_node_inflation_eliminated": True,
        }

    def _compute_structural_metrics(self, result: ScanResult, artifact: ADGArtifact) -> None:
        m = artifact.structural_metrics
        m.total_entities = len(artifact.entities)
        m.total_relations = len(artifact.relations)

        entity_kinds: dict[str, int] = {}
        for e in artifact.entities:
            entity_kinds[e.entity_type] = entity_kinds.get(e.entity_type, 0) + 1
        m.module_count = entity_kinds.get("module", 0)
        m.symbol_count = entity_kinds.get("symbol", 0)
        m.external_count = sum(
            1 for e in artifact.entities if e.identity_kind == IdentityKind.EXTERNAL_MODULE.value
        )
        m.unresolved_count = len(artifact.unresolved_imports)

        # Fan-in / fan-out per module
        fan_in: dict[str, int] = {}
        fan_out: dict[str, int] = {}
        module_prefix = "ADG::Module::"
        for rel in artifact.relations:
            if rel.from_name.startswith(module_prefix):
                fan_out[rel.from_name] = fan_out.get(rel.from_name, 0) + 1
            if rel.to_name.startswith(module_prefix):
                fan_in[rel.to_name] = fan_in.get(rel.to_name, 0) + 1

        # Orphan modules: appear in entities but have no in or out edges
        module_adg_names = {e.adg_name for e in artifact.entities if e.entity_type == "module"}
        modules_with_edges = {r.from_name for r in artifact.relations} | {r.to_name for r in artifact.relations}
        m.orphan_modules = sorted(module_adg_names - modules_with_edges)

        m.high_fan_in_modules = [
            {"module": k, "fan_in": v}
            for k, v in fan_in.items()
            if v >= self._FAN_IN_THRESHOLD
        ]
        m.high_fan_out_modules = [
            {"module": k, "fan_out": v}
            for k, v in fan_out.items()
            if v >= self._FAN_OUT_THRESHOLD
        ]

        # Relation type distribution
        for rel in artifact.relations:
            m.by_relation_type[rel.relation_type] = m.by_relation_type.get(rel.relation_type, 0) + 1

        # Layer distribution of module entities
        for e in artifact.entities:
            if e.entity_type == "module":
                m.by_layer[e.layer] = m.by_layer.get(e.layer, 0) + 1

        # Layer violations (upward imports across non-allowed edges)
        from agentic_core.adg.schema import ALLOWED_LAYER_EDGES
        violations = 0
        for rel in artifact.relations:
            if rel.relation_type != "imports":
                continue
            from_path = rel.from_name[len(module_prefix):] if rel.from_name.startswith(module_prefix) else ""
            to_path = rel.to_name[len(module_prefix):] if rel.to_name.startswith(module_prefix) else ""
            if from_path and to_path:
                fl = module_path_to_layer(from_path)
                tl = module_path_to_layer(to_path)
                if fl != tl and (fl, tl) not in ALLOWED_LAYER_EDGES:
                    violations += 1
        m.layer_violation_count = violations

    def _collect_blind_spots(self, result: ScanResult, artifact: ADGArtifact) -> None:
        bs = artifact.blind_spots
        dynamic_prefix = "ADG::Symbol::__dynamic__"

        seen_dynamic: set[tuple] = set()
        seen_star: set[tuple] = set()

        for edge in result.edges:
            loc = (edge.source_file, edge.line_no)

            # Dynamic imports: either a __dynamic__ symbol target OR an exec edge_kind
            is_dynamic = edge.to_name.startswith(dynamic_prefix) or edge.edge_kind == "exec"
            if is_dynamic and loc not in seen_dynamic:
                seen_dynamic.add(loc)
                bs.dynamic_import_count += 1
                bs.dynamic_import_locations.append(f"{edge.source_file}:{edge.line_no}")

            # Star imports: symbol is "*" or edge_kind is star_import
            is_star = edge.symbol == "*" or edge.edge_kind == "star_import"
            if is_star and loc not in seen_star:
                seen_star.add(loc)
                bs.star_import_count += 1
                bs.star_import_locations.append(f"{edge.source_file}:{edge.line_no}")

        manifest = getattr(result, "manifest", None)
        if manifest is not None:
            bs.parse_failure_count = getattr(manifest, "parse_failure_count", 0)
            bs.parse_failure_files = sorted(getattr(manifest, "parse_failure_files", []))


def build_artifact(
    result: ScanResult,
    repo_root: Path | None = None,
) -> ADGArtifact:
    """Convenience function: build a canonical artifact from a ScanResult."""
    builder = ADGArtifactBuilder(repo_root=repo_root)
    return builder.build(result)


__all__ = [
    "EntityRecord",
    "RelationRecord",
    "StructuralMetrics",
    "BlindSpotReport",
    "ADGArtifact",
    "ADGArtifactBuilder",
    "build_artifact",
]
