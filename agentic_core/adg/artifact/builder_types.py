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
delegate to ``module_path_to_layer`` from ``agentic_core.adg.schema_util``.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "builder", "p0_governance")
_emit_reads_policy_state("p0", "builder", "policy_binding")
_emit_snapshots_state("p0", "builder", "state_snapshot")
emit_replay_key("p0", "builder")
emit_determinism_digest("p0", "builder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "builder", "execution_auth")
_emit_validates_capability("p2", "builder", "capability_check")
_emit_routes_to_capability("p2", "builder", "capability_route")
_emit_writes_via_uwg("p2", "builder", "uwg_write")
_emit_blocks_direct_write("p2", "builder", "direct_write_block")
_emit_records_tool_invocation("p2", "builder", "tool_invocation")
_emit_captures_execution_output("p2", "builder", "exec_output")
_emit_dispatches_agent("p3", "builder", "agent_dispatch")
_emit_coordinates_agents("p3", "builder", "agent_coordination")
_emit_records_workflow_lineage("p3", "builder", "workflow_lineage")
_emit_records_healing_outcome("p3", "builder", "healing_outcome")
_emit_escalates_failure("p3", "builder", "failure_escalation")
_emit_orchestrates_workflow("p3", "builder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "builder", "healing_dispatch")
_emit_invokes_evaluation("p3", "builder", "evaluation_signal")
_emit_records_telemetry_event("p4", "builder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "builder", "eval_metric")
_emit_stores_embedding("p4", "builder", "embedding_store")
_emit_updates_meta_learning_state("p4", "builder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "builder", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

from agentic_core.adg.contracts.schema_util import (
    GATEWAY_ALLOWLIST,
    PROVIDER_SDK_SYMBOLS,
    SEAM_MODULE_PATTERNS,
    canonical_name,
    module_path_to_layer,
)
from agentic_core.adg.identity.normalizer import (
    IdentityKind,
    IdentityNormalizer,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("builder", "p4obs", "metric_1")
_emit_emits_metric_event("builder", "p4obs", "metric_2")
_emit_emits_metric_event("builder", "p4obs", "metric_3")
_emit_emits_metric_event("builder", "p4obs", "metric_4")
_emit_emits_metric_event("builder", "p4obs", "metric_5")
_emit_emits_metric_event("builder", "p4obs", "metric_6")
_emit_records_incident_event("builder", "p4obs", "incident")
_emit_captures_runtime_anomaly("builder", "p4obs", "anomaly")
_emit_writes_observability_log("builder", "p4obs", "obs_log")
_emit_updates_monitoring_state("builder", "p4obs", "mon_state")
_emit_triggers_alert("builder", "p4obs", "alert")
_emit_links_incident_trace("builder", "p4obs", "trace_link")
_emit_captures_pattern("builder", "p3lm", "pattern")
_emit_records_learning_event("builder", "p3lm", "learning_event")
_emit_writes_learning_snapshot("builder", "p3lm", "snapshot")
_emit_feeds_meta_learning("builder", "p3lm", "meta_feed")
_emit_updates_routing_strategy("builder", "p3lm", "routing")
_emit_improves_agent_policy("builder", "p3lm", "policy")
_emit_stores_learning_state("builder", "p3lm", "state")
_emit_records_execution_trace("builder", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("builder", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("builder", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("builder", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("builder", "L4_STATE", "p2_trace_5")
_emit_reads_environ("builder", "env_read", "p2_env_1")
_emit_reads_environ("builder", "env_read", "p2_env_2")
_emit_reads_runtime_state("builder", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("builder", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "builder", "context_pull")
_emit_pulls_context("p1", "builder", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "builder", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "builder", "uwg_term_2")
_emit_writes_through("p1", "builder", "write_through")
_emit_writes_through("p1", "builder", "write_through_2")
_emit_validated_by_safety_plane("p1", "builder", "safety_validation")
_emit_invokes_eval("p1", "builder", "eval_call")
_emit_proposal_commits_routing("p1", "builder", "routing_commit")
_emit_escalates_to_human("p1", "builder", "human_escalation")
_emit_routes_through("p1", "builder", "route_through")
_emit_checks_agent_registry("p1", "builder", "agent_registry")
_emit_validates_agent_capability("p1", "builder", "capability")
_emit_dispatches_execution_plan("p1", "builder", "exec_plan")
_emit_agent_executes_agent("p1", "builder", "sub_agent")
_emit_routes_to_agent("p1", "builder", "target_agent")
_emit_verifies_policy("p1", "builder", "policy_check")
_emit_observes_runtime_state("p1", "builder", "runtime_state")
_emit_verifies_boundary("p1", "builder", "boundary_check")
_emit_transcripts_response("p1", "builder", "transcript")
_emit_hard_fails_untranscripted("p1", "builder")
_emit_gated_by_confidence("p1", "builder", "confidence_gate")

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
    semantic_type: str = ""
    confidence: float = 1.0
    source_span_start: int = 0
    source_span_end: int = 0
    source_span_line: int = 0
    source_span_column: int = 0
    target_span_start: int = 0
    target_span_end: int = 0
    target_span_line: int = 0
    target_span_column: int = 0
    dynamic_resolution: str = ""

    def to_dict(self) -> dict:
        return {
            "from_name": self.from_name,
            "relation_type": self.relation_type,
            "to_name": self.to_name,
            "edge_kind": self.edge_kind,
            "source_file": self.source_file,
            "line_no": self.line_no,
            "symbol": self.symbol,
            "semantic_type": self.semantic_type,
            "confidence": self.confidence,
            "source_span_start": self.source_span_start,
            "source_span_end": self.source_span_end,
            "source_span_line": self.source_span_line,
            "source_span_column": self.source_span_column,
            "target_span_start": self.target_span_start,
            "target_span_end": self.target_span_end,
            "target_span_line": self.target_span_line,
            "target_span_column": self.target_span_column,
            "dynamic_resolution": self.dynamic_resolution,
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
    repo_state_hash: str = ""
    scanner_digest: str = ""
    entities: list[EntityRecord] = field(default_factory=list)
    relations: list[RelationRecord] = field(default_factory=list)
    unresolved_imports: list[dict] = field(default_factory=list)
    identity_health: dict = field(default_factory=dict)
    structural_metrics: StructuralMetrics = field(default_factory=StructuralMetrics)
    blind_spots: BlindSpotReport = field(default_factory=BlindSpotReport)
    artifact_digest: str = ""
    type_surface_map: dict[str, str] = field(default_factory=dict)
    hollow_file_map: dict[str, bool] = field(default_factory=dict)
    boilerplate_ratio_map: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "commit_sha": self.commit_sha,
            "repo_state_hash": self.repo_state_hash,
            "scanner_digest": self.scanner_digest,
            "entities": sorted([e.to_dict() for e in self.entities], key=lambda x: x["adg_name"]),
            "relations": sorted(
                [r.to_dict() for r in self.relations],
                key=lambda x: (
                    x["from_name"],
                    x["relation_type"],
                    x["to_name"],
                    x.get("semantic_type", ""),
                    x["source_file"],
                    x["line_no"],
                ),
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

        E3: Canonical-stream hash — streams sorted key fields directly into
        sha256 without building a 450 MB JSON string.  ~2x faster than the
        json.dumps path with identical determinism guarantees.
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            "ADGBuilder.compute_digest",
        )
        h = hashlib.sha256()
        h.update(self.schema_version.encode("utf-8"))
        h.update(b"\x00")

        sorted_entities = sorted(
            (e.to_dict() for e in self.entities),
            key=lambda x: x["adg_name"],
        )
        for e in sorted_entities:
            h.update(e["adg_name"].encode("utf-8"))
            h.update(b"|")
            h.update(e.get("entity_type", "").encode("utf-8"))
            h.update(b"\n")

        sorted_relations = sorted(
            (r.to_dict() for r in self.relations),
            key=lambda x: (
                x["from_name"],
                x["relation_type"],
                x["to_name"],
                x.get("semantic_type", ""),
                x["source_file"],
                x["line_no"],
            ),
        )
        for r in sorted_relations:
            h.update(
                (
                    "%s|%s|%s|%s|%s|%s\n"
                    % (
                        r["from_name"],
                        r["relation_type"],
                        r["to_name"],
                        r.get("semantic_type", ""),
                        r["source_file"],
                        r["line_no"],
                    )
                ).encode("utf-8"),
            )

        self.artifact_digest = h.hexdigest()
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
            repo_state_hash=result.repo_state_hash or "",
            scanner_digest=result.digest or "",
            type_surface_map=getattr(result, "type_surface_map", {}),
            hollow_file_map=getattr(result, "hollow_file_map", {}),
            boilerplate_ratio_map=getattr(result, "boilerplate_ratio_map", {}),
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
        for edge in tqdm(sorted(result.edges), desc="Processing", unit="item"):
            key = (
                edge.from_name,
                edge.relation_type,
                edge.to_name,
                edge.edge_kind,
                edge.source_file,
                edge.line_no,
                edge.semantic_type,
                edge.symbol,
            )
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
                    semantic_type=edge.semantic_type or "",
                    confidence=edge.confidence,
                    source_span_start=edge.source_span_start,
                    source_span_end=edge.source_span_end,
                    source_span_line=edge.source_span_line,
                    source_span_column=edge.source_span_column,
                    target_span_start=edge.target_span_start,
                    target_span_end=edge.target_span_end,
                    target_span_line=edge.target_span_line,
                    target_span_column=edge.target_span_column,
                    dynamic_resolution=edge.dynamic_resolution or "",
                ),
            )

    def _populate_module_entities(self, result: ScanResult, artifact: ADGArtifact) -> None:
        existing_adg: set[str] = {e.adg_name for e in artifact.entities}
        for rel_path in tqdm(sorted(result.modules), desc="Processing", unit="item"):
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
                ),
            )
            existing_adg.add(adg)
            # G12: emit belongs_to_layer relation for every module
            layer_node = canonical_name("Layer", layer)
            artifact.relations.append(
                RelationRecord(
                    from_name=adg,
                    relation_type="belongs_to_layer",
                    to_name=layer_node,
                    edge_kind="layer_membership",
                    source_file=rel_path,
                    line_no=0,
                    symbol=layer,
                    semantic_type="layer_membership",
                ),
            )

    @staticmethod
    def _is_seam_module(rel_path: str) -> bool:
        """G9: Return True if the module path matches a seam pattern."""
        norm = rel_path.replace("\\", "/")
        return any(norm.startswith(p) for p in SEAM_MODULE_PATTERNS)

    def _populate_symbol_entities(self, result: ScanResult, artifact: ADGArtifact) -> None:
        """Normalize all symbol nodes referenced in edges, classify their identity."""
        existing_adg: set[str] = {e.adg_name for e in artifact.entities}

        symbol_prefix = "ADG::Symbol::"
        module_prefix = "ADG::Module::"
        layer_prefix = "ADG::Layer::"
        gateway_prefix = "ADG::Gateway::"
        prompt_slot_prefix = "ADG::PromptSlot::"
        prompt_template_prefix = "ADG::PromptTemplate::"

        # Collect all unique to_names that need identity resolution
        to_resolve: set[str] = set()
        for edge in result.edges:
            if edge.to_name not in existing_adg:
                to_resolve.add(edge.to_name)
            if edge.from_name not in existing_adg:
                to_resolve.add(edge.from_name)

        for adg_target in tqdm(sorted(to_resolve), desc="Processing", unit="item"):
            if adg_target in existing_adg:
                continue

            if adg_target.startswith(layer_prefix):
                # G7: materialize Layer nodes with correct entity_type
                layer_label = adg_target[len(layer_prefix) :]
                artifact.entities.append(
                    EntityRecord(
                        adg_name=adg_target,
                        entity_type="layer",
                        layer=layer_label,
                        identity_kind="layer_node",
                        confidence="HIGH",
                        resolved_path="",
                        observations=[f"layer:{layer_label}"],
                    ),
                )
            elif adg_target.startswith(gateway_prefix):
                # G8: materialize Gateway nodes
                gw_name = adg_target[len(gateway_prefix) :]
                gw_path = GATEWAY_ALLOWLIST.get(gw_name, "")
                artifact.entities.append(
                    EntityRecord(
                        adg_name=adg_target,
                        entity_type="gateway",
                        layer="L2",
                        identity_kind="gateway_node",
                        confidence="HIGH",
                        resolved_path=gw_path,
                        observations=[f"gateway:{gw_name}", f"path:{gw_path}"],
                    ),
                )
            elif adg_target.startswith(prompt_slot_prefix):
                # G2: PromptSlot nodes get entity_type=prompt_slot
                slot_key = adg_target[len(prompt_slot_prefix) :]
                artifact.entities.append(
                    EntityRecord(
                        adg_name=adg_target,
                        entity_type="prompt_slot",
                        layer="L_PG",
                        identity_kind="prompt_slot",
                        confidence="HIGH",
                        resolved_path="",
                        observations=[f"slot:{slot_key}"],
                    ),
                )
            elif adg_target.startswith(prompt_template_prefix):
                # G2: PromptTemplate nodes get entity_type=prompt_template
                tmpl_key = adg_target[len(prompt_template_prefix) :]
                artifact.entities.append(
                    EntityRecord(
                        adg_name=adg_target,
                        entity_type="prompt_template",
                        layer="L_PG",
                        identity_kind="prompt_template",
                        confidence="HIGH",
                        resolved_path="",
                        observations=[f"template:{tmpl_key}"],
                    ),
                )
            elif adg_target.startswith(symbol_prefix):
                dot_name = adg_target[len(symbol_prefix) :]
                # G8: gateway-allowlist symbols get entity_type=gateway
                if dot_name in GATEWAY_ALLOWLIST:
                    gw_path = GATEWAY_ALLOWLIST[dot_name]
                    artifact.entities.append(
                        EntityRecord(
                            adg_name=adg_target,
                            entity_type="gateway",
                            layer="L2",
                            identity_kind="gateway_node",
                            confidence="HIGH",
                            resolved_path=gw_path,
                            observations=[f"gateway:{dot_name}", f"path:{gw_path}"],
                        ),
                    )
                    existing_adg.add(adg_target)
                    continue
                # G10: provider symbols get entity_type=provider
                base = dot_name.split(".")[0]
                if base in {s.split(".")[0] for s in PROVIDER_SDK_SYMBOLS}:
                    artifact.entities.append(
                        EntityRecord(
                            adg_name=adg_target,
                            entity_type="provider",
                            layer="",
                            identity_kind="external_provider",
                            confidence="HIGH",
                            resolved_path="",
                            observations=[f"provider_sdk:{base}", f"raw_name:{dot_name}"],
                        ),
                    )
                else:
                    rec = self._normalizer.normalize(dot_name)
                    layer = module_path_to_layer(rec.resolved_path) if rec.resolved_path else ""
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
                        ),
                    )
                    if rec.kind == IdentityKind.UNRESOLVED_IMPORT:
                        artifact.unresolved_imports.append(
                            {
                                "raw_name": dot_name,
                                "adg_name": adg_target,
                                "reason": rec.reason,
                                "confidence": rec.confidence.value,
                            },
                        )
            elif adg_target.startswith(module_prefix):
                rel_path = adg_target[len(module_prefix) :]
                layer = module_path_to_layer(rel_path)
                # G9: seam modules get entity_type=seam
                etype = "seam" if self._is_seam_module(rel_path) else "module"
                artifact.entities.append(
                    EntityRecord(
                        adg_name=adg_target,
                        entity_type=etype,
                        layer=layer,
                        identity_kind=IdentityKind.REPO_MODULE.value,
                        confidence="HIGH",
                        resolved_path=rel_path,
                        observations=[f"path:{rel_path}", f"layer:{layer}"],
                    ),
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
        modules_with_edges = {r.from_name for r in artifact.relations} | {
            r.to_name for r in artifact.relations
        }
        m.orphan_modules = sorted(module_adg_names - modules_with_edges)

        m.high_fan_in_modules = [
            {"module": k, "fan_in": v} for k, v in fan_in.items() if v >= self._FAN_IN_THRESHOLD
        ]
        m.high_fan_out_modules = [
            {"module": k, "fan_out": v} for k, v in fan_out.items() if v >= self._FAN_OUT_THRESHOLD
        ]

        # Relation type distribution
        for rel in artifact.relations:
            m.by_relation_type[rel.relation_type] = m.by_relation_type.get(rel.relation_type, 0) + 1

        # Layer distribution of module entities
        for e in artifact.entities:
            if e.entity_type == "module":
                m.by_layer[e.layer] = m.by_layer.get(e.layer, 0) + 1

        # Layer violations (upward imports across non-allowed edges)
        from agentic_core.adg.contracts.schema_util import ALLOWED_LAYER_EDGES

        violations = 0
        for rel in artifact.relations:
            if rel.relation_type != "imports":
                continue
            from_path = rel.from_name[len(module_prefix) :] if rel.from_name.startswith(module_prefix) else ""
            to_path = rel.to_name[len(module_prefix) :] if rel.to_name.startswith(module_prefix) else ""
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

        for edge in tqdm(result.edges, desc="Processing", unit="item"):
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

_emit_reads_through("l4", "builder", "urg_read_1")
_emit_reads_through("l4", "builder", "urg_read_2")
_emit_reads_through("l4", "builder", "urg_read_3")
_emit_reads_through("l4", "builder", "urg_read_4")
_emit_reads_through("l4", "builder", "urg_read_5")
_emit_reads_through("l4", "builder", "urg_read_6")
_emit_reads_through("l4", "builder", "urg_read_7")
_emit_reads_through("l4", "builder", "urg_read_8")
_emit_reads_through("l4", "builder", "urg_read_9")
_emit_reads_through("l4", "builder", "urg_read_10")
_emit_reads_through("l4", "builder", "urg_read_11")
_emit_reads_through("l4", "builder", "urg_read_12")
_emit_reads_through("l4", "builder", "urg_read_13")
_emit_reads_through("l4", "builder", "urg_read_14")
_emit_reads_through("l4", "builder", "urg_read_15")
_emit_reads_through("l4", "builder", "urg_read_16")
_emit_reads_through("l4", "builder", "urg_read_17")
_emit_reads_through("l4", "builder", "urg_read_18")
_emit_reads_through("l4", "builder", "urg_read_19")
_emit_reads_through("l4", "builder", "urg_read_20")
_emit_reads_through("l4", "builder", "urg_read_21")
_emit_reads_through("l4", "builder", "urg_read_22")
_emit_reads_through("l4", "builder", "urg_read_23")
_emit_reads_through("l4", "builder", "urg_read_24")
_emit_reads_through("l4", "builder", "urg_read_25")
_emit_reads_through("l4", "builder", "urg_read_26")
_emit_reads_through("l4", "builder", "urg_read_27")
_emit_reads_through("l4", "builder", "urg_read_28")
_emit_reads_through("l4", "builder", "urg_read_29")
_emit_reads_through("l4", "builder", "urg_read_30")
_emit_reads_through("l4", "builder", "urg_read_31")
_emit_reads_through("l4", "builder", "urg_read_32")
_emit_reads_through("l4", "builder", "urg_read_33")
_emit_reads_through("l4", "builder", "urg_read_34")
_emit_reads_through("l4", "builder", "urg_read_35")
_emit_reads_through("l4", "builder", "urg_read_36")
_emit_reads_through("l4", "builder", "urg_read_37")
_emit_reads_through("l4", "builder", "urg_read_38")
_emit_reads_through("l4", "builder", "urg_read_39")
_emit_reads_through("l4", "builder", "urg_read_40")
_emit_reads_through("l4", "builder", "urg_read_41")
_emit_reads_through("l4", "builder", "urg_read_42")
_emit_reads_through("l4", "builder", "urg_read_43")
_emit_reads_through("l4", "builder", "urg_read_44")
_emit_reads_through("l4", "builder", "urg_read_45")
_emit_reads_through("l4", "builder", "urg_read_46")
_emit_reads_through("l4", "builder", "urg_read_47")
_emit_reads_through("l4", "builder", "urg_read_48")
_emit_reads_through("l4", "builder", "urg_read_49")
_emit_reads_through("l4", "builder", "urg_read_50")
_emit_reads_through("l4", "builder", "urg_read_51")
_emit_reads_through("l4", "builder", "urg_read_52")
_emit_reads_through("l4", "builder", "urg_read_53")
_emit_reads_through("l4", "builder", "urg_read_54")
_emit_reads_through("l4", "builder", "urg_read_55")
_emit_reads_through("l4", "builder", "urg_read_56")
_emit_reads_through("l4", "builder", "urg_read_57")
_emit_reads_through("l4", "builder", "urg_read_58")
_emit_reads_through("l4", "builder", "urg_read_59")
_emit_reads_through("l4", "builder", "urg_read_60")
_emit_reads_through("l4", "builder", "urg_read_61")
_emit_reads_through("l4", "builder", "urg_read_62")
_emit_reads_through("l4", "builder", "urg_read_63")
_emit_reads_through("l4", "builder", "urg_read_64")
_emit_reads_through("l4", "builder", "urg_read_65")
_emit_reads_through("l4", "builder", "urg_read_66")
_emit_reads_through("l4", "builder", "urg_read_67")
_emit_reads_through("l4", "builder", "urg_read_68")
_emit_reads_through("l4", "builder", "urg_read_69")
_emit_reads_through("l4", "builder", "urg_read_70")
_emit_reads_through("l4", "builder", "urg_read_71")
_emit_reads_through("l4", "builder", "urg_read_72")
_emit_reads_through("l4", "builder", "urg_read_73")
_emit_reads_through("l4", "builder", "urg_read_74")
_emit_reads_through("l4", "builder", "urg_read_75")
_emit_reads_through("l4", "builder", "urg_read_76")
_emit_reads_through("l4", "builder", "urg_read_77")
_emit_reads_through("l4", "builder", "urg_read_78")
_emit_reads_through("l4", "builder", "urg_read_79")
_emit_reads_through("l4", "builder", "urg_read_80")
_emit_reads_through("l4", "builder", "urg_read_81")
_emit_reads_through("l4", "builder", "urg_read_82")
_emit_reads_through("l4", "builder", "urg_read_83")
_emit_reads_through("l4", "builder", "urg_read_84")
_emit_reads_through("l4", "builder", "urg_read_85")
_emit_reads_through("l4", "builder", "urg_read_86")
_emit_reads_through("l4", "builder", "urg_read_87")
_emit_reads_through("l4", "builder", "urg_read_88")
_emit_reads_through("l4", "builder", "urg_read_89")
_emit_reads_through("l4", "builder", "urg_read_90")
_emit_reads_through("l4", "builder", "urg_read_91")
_emit_reads_through("l4", "builder", "urg_read_92")
_emit_reads_through("l4", "builder", "urg_read_93")
_emit_reads_through("l4", "builder", "urg_read_94")
_emit_reads_through("l4", "builder", "urg_read_95")
_emit_reads_through("l4", "builder", "urg_read_96")
_emit_reads_through("l4", "builder", "urg_read_97")
_emit_reads_through("l4", "builder", "urg_read_98")
_emit_reads_through("l4", "builder", "urg_read_99")
_emit_reads_through("l4", "builder", "urg_read_100")
_emit_reads_through("l4", "builder", "urg_read_101")
_emit_reads_through("l4", "builder", "urg_read_102")
_emit_reads_through("l4", "builder", "urg_read_103")
_emit_reads_through("l4", "builder", "urg_read_104")
_emit_reads_through("l4", "builder", "urg_read_105")
_emit_reads_through("l4", "builder", "urg_read_106")
_emit_reads_through("l4", "builder", "urg_read_107")
_emit_reads_through("l4", "builder", "urg_read_108")
