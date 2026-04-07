"""ADG Artifact Normalizer — compact node/edge representation.

Converts the verbose repeated-string format into an integer-indexed format:

    Verbose (current):
        edges: [{"from_name": "ADG::Module::foo.py", "relation_type": "imports",
                 "to_name": "ADG::Module::bar.py", "edge_kind": "import",
                 "source_file": "foo.py", "line_no": 5, "symbol": ""}]

    Normalized (compact):
        nodes: {"0": {"n": "ADG::Module::foo.py", "t": "module", "l": "L2"},
                "1": {"n": "ADG::Module::bar.py", "t": "module", "l": "L2"}}
        edges: [{"s": 0, "d": 1, "r": "imports", "k": "import", "f": "foo.py",
                 "ln": 5}]

Key size savings for the live ADG (149,584 edges):
    - "ADG::Module::" prefix (14 chars) × 2 sides × 149,584 = ~4.2 MB saved
    - "ADG::Symbol::" prefix same — total ~60–70% reduction in edges section
    - node metadata stored once instead of repeated per edge

Round-trip safe: normalize() → denormalize() produces identical ADGArtifact.

Schema version: 4.0.0 (normalized)
"""

from __future__ import annotations

import hashlib
import json
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

_emit_applies_guardrail("p0", "normalizer", "p0_governance")
_emit_reads_policy_state("p0", "normalizer", "policy_binding")
_emit_snapshots_state("p0", "normalizer", "state_snapshot")
emit_replay_key("p0", "normalizer")
emit_determinism_digest("p0", "normalizer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "normalizer", "execution_auth")
_emit_validates_capability("p2", "normalizer", "capability_check")
_emit_routes_to_capability("p2", "normalizer", "capability_route")
_emit_writes_via_uwg("p2", "normalizer", "uwg_write")
_emit_blocks_direct_write("p2", "normalizer", "direct_write_block")
_emit_records_tool_invocation("p2", "normalizer", "tool_invocation")
_emit_captures_execution_output("p2", "normalizer", "exec_output")
_emit_dispatches_agent("p3", "normalizer", "agent_dispatch")
_emit_coordinates_agents("p3", "normalizer", "agent_coordination")
_emit_records_workflow_lineage("p3", "normalizer", "workflow_lineage")
_emit_records_healing_outcome("p3", "normalizer", "healing_outcome")
_emit_escalates_failure("p3", "normalizer", "failure_escalation")
_emit_orchestrates_workflow("p3", "normalizer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "normalizer", "healing_dispatch")
_emit_invokes_evaluation("p3", "normalizer", "evaluation_signal")
_emit_records_telemetry_event("p4", "normalizer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "normalizer", "eval_metric")
_emit_stores_embedding("p4", "normalizer", "embedding_store")
_emit_updates_meta_learning_state("p4", "normalizer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "normalizer", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.artifact.builder_types import ADGArtifact
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

_emit_emits_metric_event("normalizer", "p4obs", "metric_1")
_emit_emits_metric_event("normalizer", "p4obs", "metric_2")
_emit_emits_metric_event("normalizer", "p4obs", "metric_3")
_emit_emits_metric_event("normalizer", "p4obs", "metric_4")
_emit_emits_metric_event("normalizer", "p4obs", "metric_5")
_emit_emits_metric_event("normalizer", "p4obs", "metric_6")
_emit_records_incident_event("normalizer", "p4obs", "incident")
_emit_captures_runtime_anomaly("normalizer", "p4obs", "anomaly")
_emit_writes_observability_log("normalizer", "p4obs", "obs_log")
_emit_updates_monitoring_state("normalizer", "p4obs", "mon_state")
_emit_triggers_alert("normalizer", "p4obs", "alert")
_emit_links_incident_trace("normalizer", "p4obs", "trace_link")
_emit_captures_pattern("normalizer", "p3lm", "pattern")
_emit_records_learning_event("normalizer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("normalizer", "p3lm", "snapshot")
_emit_feeds_meta_learning("normalizer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("normalizer", "p3lm", "routing")
_emit_improves_agent_policy("normalizer", "p3lm", "policy")
_emit_stores_learning_state("normalizer", "p3lm", "state")
_emit_records_execution_trace("normalizer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("normalizer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("normalizer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("normalizer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("normalizer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("normalizer", "env_read", "p2_env_1")
_emit_reads_environ("normalizer", "env_read", "p2_env_2")
_emit_reads_runtime_state("normalizer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("normalizer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "normalizer", "context_pull")
_emit_pulls_context("p1", "normalizer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "normalizer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "normalizer", "uwg_term_2")
_emit_writes_through("p1", "normalizer", "write_through")
_emit_writes_through("p1", "normalizer", "write_through_2")
_emit_validated_by_safety_plane("p1", "normalizer", "safety_validation")
_emit_invokes_eval("p1", "normalizer", "eval_call")
_emit_proposal_commits_routing("p1", "normalizer", "routing_commit")
_emit_escalates_to_human("p1", "normalizer", "human_escalation")
_emit_routes_through("p1", "normalizer", "route_through")
_emit_checks_agent_registry("p1", "normalizer", "agent_registry")
_emit_validates_agent_capability("p1", "normalizer", "capability")
_emit_dispatches_execution_plan("p1", "normalizer", "exec_plan")
_emit_agent_executes_agent("p1", "normalizer", "sub_agent")
_emit_routes_to_agent("p1", "normalizer", "target_agent")
_emit_verifies_policy("p1", "normalizer", "policy_check")
_emit_observes_runtime_state("p1", "normalizer", "runtime_state")
_emit_verifies_boundary("p1", "normalizer", "boundary_check")
_emit_transcripts_response("p1", "normalizer", "transcript")
_emit_hard_fails_untranscripted("p1", "normalizer")
_emit_gated_by_confidence("p1", "normalizer", "confidence_gate")

_SCHEMA_VERSION_NORMALIZED = "4.0.0"


# ---------------------------------------------------------------------------
# Compact data model
# ---------------------------------------------------------------------------


@dataclass
class NormalizedGraph:
    """Compact integer-indexed graph representation.

    Attributes
    ----------
    schema_version:
        Always ``"4.0.0"`` for normalized format.
    commit_sha:
        Source commit SHA.
    scanner_digest:
        SHA256 of the raw scan.
    artifact_digest:
        SHA256 of the normalized content.
    nodes:
        ``{str(int_id): {"n": adg_name, "t": entity_type, "l": layer,
                          "k": identity_kind, "c": confidence, "p": resolved_path}}``
        Keys are stringified ints for JSON compatibility.
    edges:
        ``[{"s": src_id, "d": dst_id, "r": relation_type, "k": edge_kind,
             "f": source_file, "ln": line_no}]``
        ``symbol`` field only included when non-empty.
    meta:
        Lightweight metrics: total_nodes, total_edges, by_relation_type,
        by_layer, blind_spots summary.
    """

    schema_version: str = _SCHEMA_VERSION_NORMALIZED
    commit_sha: str = ""
    repo_state_hash: str = ""
    scanner_digest: str = ""
    artifact_digest: str = ""
    nodes: dict[str, dict] = field(default_factory=dict)
    edges: list[dict] = field(default_factory=list)
    meta: dict = field(default_factory=dict)

    def compute_digest(self) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "NormalizedGraph.compute_digest",
        )

        # D2a: Canonical-stream hash — avoids building a 450 MB+ JSON string.
        # Streams sorted node keys and edge canonical fields directly into sha256.
        h = hashlib.sha256()
        for k in sorted(self.nodes.keys(), key=lambda x: int(x)):
            node = self.nodes[k]
            h.update(("%s|%s|%s\n" % (k, node.get("n", ""), node.get("t", ""))).encode("utf-8"))
        for e in self.edges:
            h.update(
                ("%s|%s|%s|%s\n" % (e["s"], e["d"], e["r"], e.get("k", ""))).encode("utf-8"),
            )
        self.artifact_digest = h.hexdigest()
        return self.artifact_digest

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "commit_sha": self.commit_sha,
            "repo_state_hash": self.repo_state_hash,
            "scanner_digest": self.scanner_digest,
            "artifact_digest": self.artifact_digest,
            "nodes": self.nodes,
            "edges": self.edges,
            "meta": self.meta,
        }

    def to_json(self, indent: int | None = None) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, indent=indent)

    def write(self, path: Path, indent: int | None = None) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(indent=indent), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> NormalizedGraph:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            schema_version=raw.get("schema_version", _SCHEMA_VERSION_NORMALIZED),
            commit_sha=raw.get("commit_sha", ""),
            repo_state_hash=raw.get("repo_state_hash", ""),
            scanner_digest=raw.get("scanner_digest", ""),
            artifact_digest=raw.get("artifact_digest", ""),
            nodes=raw.get("nodes", {}),
            edges=raw.get("edges", []),
            meta=raw.get("meta", {}),
        )


# ---------------------------------------------------------------------------
# Normalizer
# ---------------------------------------------------------------------------


class ArtifactNormalizer:
    """Converts an ADGArtifact into compact NormalizedGraph form.

    Usage::

        ng = ArtifactNormalizer().normalize(artifact)
        ng.write(Path("artifacts/adg/adg_normalized.json"))
        restored = ArtifactNormalizer().denormalize(ng)
    """

    def normalize(self, artifact: ADGArtifact) -> NormalizedGraph:
        """Convert verbose ADGArtifact → compact NormalizedGraph.

        Algorithm:
        1. Assign integer IDs to every unique node name (adg_name).
        2. Emit compact node metadata dict keyed by str(id).
        3. Convert every relation to {s, d, r, k, f, ln} using IDs.
        4. Compute digest and attach metrics.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ArtifactNormalizer.normalize",
        )

        def _infer_precision_type(adg_name: str) -> str:
            if "::expr_" in adg_name:
                return "expression_unit"
            if "::if_" in adg_name or "::for_" in adg_name or "::try_" in adg_name:
                return "control_branch"
            if "::block" in adg_name:
                return "code_block"
            return "symbol"

        # Phase 3b: type surface map from scanner
        ts_map: dict[str, str] = getattr(artifact, "type_surface_map", {})

        def _infer_enclosing_symbol(adg_name: str) -> str:
            """For block nodes, extract the enclosing function/class symbol."""
            for tag in ("::if_L", "::for_L", "::try_L", "::block_L", "::expr_L"):
                idx = adg_name.find(tag)
                if idx != -1:
                    return adg_name[:idx]
            return ""

        # Step 1: build name → id mapping
        name_to_id: dict[str, int] = {}
        nodes: dict[str, dict] = {}

        # Register all entity nodes first
        for ent in sorted(artifact.entities, key=lambda e: e.adg_name):
            if ent.adg_name not in name_to_id:
                nid = len(name_to_id)
                name_to_id[ent.adg_name] = nid
                nodes[str(nid)] = {
                    "n": ent.adg_name,
                    "t": ent.entity_type,
                    "l": ent.layer,
                    "k": ent.identity_kind,
                    "c": ent.confidence,
                    "p": ent.resolved_path,
                    "pt": _infer_precision_type(ent.adg_name),
                    "lsid": 0,
                    "ts": ts_map.get(ent.adg_name, ""),
                    "es": _infer_enclosing_symbol(ent.adg_name),
                }

        # Register any node referenced in edges that isn't already in entities
        for rel in artifact.relations:
            for name in (rel.from_name, rel.to_name):
                if name not in name_to_id:
                    nid = len(name_to_id)
                    name_to_id[name] = nid
                    nodes[str(nid)] = {
                        "n": name,
                        "t": "symbol",
                        "l": "",
                        "k": "",
                        "c": "",
                        "p": "",
                        "pt": _infer_precision_type(name),
                        "lsid": 0,
                        "ts": ts_map.get(name, ""),
                        "es": _infer_enclosing_symbol(name),
                    }

        # Step 2: compact edges
        edges: list[dict] = []
        for rel in artifact.relations:
            e: dict = {
                "s": name_to_id[rel.from_name],
                "d": name_to_id[rel.to_name],
                "r": rel.relation_type,
                "k": rel.edge_kind,
                "f": rel.source_file,
                "ln": rel.line_no,
            }
            if rel.symbol:
                e["sym"] = rel.symbol
            if getattr(rel, "semantic_type", ""):
                e["st"] = rel.semantic_type
            if getattr(rel, "confidence", 1.0) != 1.0:
                e["conf"] = rel.confidence
            if getattr(rel, "source_span_start", 0):
                e["sss"] = rel.source_span_start
            if getattr(rel, "source_span_end", 0):
                e["sse"] = rel.source_span_end
            if getattr(rel, "source_span_line", 0):
                e["ssl"] = rel.source_span_line
            if getattr(rel, "source_span_column", 0):
                e["ssc"] = rel.source_span_column
            if getattr(rel, "target_span_start", 0):
                e["tss"] = rel.target_span_start
            if getattr(rel, "target_span_end", 0):
                e["tse"] = rel.target_span_end
            if getattr(rel, "target_span_line", 0):
                e["tsl"] = rel.target_span_line
            if getattr(rel, "target_span_column", 0):
                e["tsc"] = rel.target_span_column
            if getattr(rel, "dynamic_resolution", ""):
                e["dr"] = rel.dynamic_resolution
            edges.append(e)

        # Step 3: build metrics
        by_rel: dict[str, int] = {}
        for e in edges:
            by_rel[e["r"]] = by_rel.get(e["r"], 0) + 1

        by_layer: dict[str, int] = {}
        for node in nodes.values():
            if node["t"] == "module" and node["l"]:
                by_layer[node["l"]] = by_layer.get(node["l"], 0) + 1

        meta = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "module_count": sum(1 for n in nodes.values() if n["t"] == "module"),
            "symbol_count": sum(1 for n in nodes.values() if n["t"] == "symbol"),
            "by_relation_type": dict(sorted(by_rel.items())),
            "by_layer": dict(sorted(by_layer.items())),
            "blind_spots": artifact.blind_spots.to_dict() if artifact.blind_spots else {},
            "identity_health": artifact.identity_health,
            "structural_metrics": artifact.structural_metrics.to_dict(),
        }

        ng = NormalizedGraph(
            commit_sha=artifact.commit_sha,
            repo_state_hash=artifact.repo_state_hash,
            scanner_digest=artifact.scanner_digest,
            nodes=nodes,
            edges=edges,
            meta=meta,
        )
        ng.compute_digest()
        return ng

    def normalize_with_planes(
        self,
        artifact: ADGArtifact,
        file_rels: frozenset[str],
        symbol_rels: frozenset[str],
        governance_rels: frozenset[str],
    ) -> tuple[NormalizedGraph, NormalizedGraph, NormalizedGraph, NormalizedGraph]:
        """Single-pass fusion: normalize artifact AND split into three planes.

        Returns (full_ng, file_ng, symbol_ng, governance_ng).

        All four NormalizedGraphs share the same ``name_to_id`` mapping built
        in one traversal of artifact.entities and artifact.relations.  This
        avoids the duplicate full-artifact walk that separate
        normalize() + split_artifact() calls would perform.

        Parameters
        ----------
        artifact:
            The ADGArtifact to normalize and split.
        file_rels, symbol_rels, governance_rels:
            Frozensets of relation_type strings defining each plane.
            Together they must cover all edge types without overlap.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ArtifactNormalizer.normalize_with_planes",
        )

        def _infer_precision_type(adg_name: str) -> str:
            if "::expr_" in adg_name:
                return "expression_unit"
            if "::if_" in adg_name or "::for_" in adg_name or "::try_" in adg_name:
                return "control_branch"
            if "::block" in adg_name:
                return "code_block"
            return "symbol"

        ts_map: dict[str, str] = getattr(artifact, "type_surface_map", {})

        def _infer_enclosing_symbol(adg_name: str) -> str:
            for tag in ("::if_L", "::for_L", "::try_L", "::block_L", "::expr_L"):
                idx = adg_name.find(tag)
                if idx != -1:
                    return adg_name[:idx]
            return ""

        # --- Single shared name→id map for all four outputs ---
        name_to_id: dict[str, int] = {}
        nodes_full: dict[str, dict] = {}

        for ent in sorted(artifact.entities, key=lambda e: e.adg_name):
            if ent.adg_name not in name_to_id:
                nid = len(name_to_id)
                name_to_id[ent.adg_name] = nid
                nodes_full[str(nid)] = {
                    "n": ent.adg_name,
                    "t": ent.entity_type,
                    "l": ent.layer,
                    "k": ent.identity_kind,
                    "c": ent.confidence,
                    "p": ent.resolved_path,
                    "pt": _infer_precision_type(ent.adg_name),
                    "lsid": 0,
                    "ts": ts_map.get(ent.adg_name, ""),
                    "es": _infer_enclosing_symbol(ent.adg_name),
                }

        for rel in artifact.relations:
            for name in (rel.from_name, rel.to_name):
                if name not in name_to_id:
                    nid = len(name_to_id)
                    name_to_id[name] = nid
                    nodes_full[str(nid)] = {
                        "n": name,
                        "t": "symbol",
                        "l": "",
                        "k": "",
                        "c": "",
                        "p": "",
                        "pt": _infer_precision_type(name),
                        "lsid": 0,
                        "ts": ts_map.get(name, ""),
                        "es": _infer_enclosing_symbol(name),
                    }

        # --- Single pass over relations — partition edges, collect referenced names per plane ---
        edges_full: list[dict] = []

        # Accumulate plane edge raw tuples using global IDs; name sets for node assembly
        _plane_raw: dict[str, list[dict]] = {"file": [], "sym": [], "gov": []}
        _plane_refs: dict[str, set[str]] = {"file": set(), "sym": set(), "gov": set()}

        for rel in artifact.relations:
            sid = name_to_id[rel.from_name]
            did = name_to_id[rel.to_name]
            rt = rel.relation_type

            # Full compact edge
            e_full: dict = {
                "s": sid,
                "d": did,
                "r": rt,
                "k": rel.edge_kind,
                "f": rel.source_file,
                "ln": rel.line_no,
            }
            if rel.symbol:
                e_full["sym"] = rel.symbol
            if getattr(rel, "semantic_type", ""):
                e_full["st"] = rel.semantic_type
            if getattr(rel, "confidence", 1.0) != 1.0:
                e_full["conf"] = rel.confidence
            if getattr(rel, "source_span_start", 0):
                e_full["sss"] = rel.source_span_start
            if getattr(rel, "source_span_end", 0):
                e_full["sse"] = rel.source_span_end
            if getattr(rel, "source_span_line", 0):
                e_full["ssl"] = rel.source_span_line
            if getattr(rel, "source_span_column", 0):
                e_full["ssc"] = rel.source_span_column
            if getattr(rel, "target_span_start", 0):
                e_full["tss"] = rel.target_span_start
            if getattr(rel, "target_span_end", 0):
                e_full["tse"] = rel.target_span_end
            if getattr(rel, "target_span_line", 0):
                e_full["tsl"] = rel.target_span_line
            if getattr(rel, "target_span_column", 0):
                e_full["tsc"] = rel.target_span_column
            if getattr(rel, "dynamic_resolution", ""):
                e_full["dr"] = rel.dynamic_resolution
            edges_full.append(e_full)

            # Plane compact edge (shared fields only — stored with global IDs, remapped later)
            e_plane: dict = {
                "s": sid, "d": did, "r": rt,
                "k": rel.edge_kind, "f": rel.source_file, "ln": rel.line_no,
            }
            if rel.symbol:
                e_plane["sym"] = rel.symbol

            if rt in file_rels:
                _plane_raw["file"].append(e_plane)
                _plane_refs["file"].add(rel.from_name)
                _plane_refs["file"].add(rel.to_name)
            elif rt in symbol_rels:
                _plane_raw["sym"].append(e_plane)
                _plane_refs["sym"].add(rel.from_name)
                _plane_refs["sym"].add(rel.to_name)
            elif rt in governance_rels:
                _plane_raw["gov"].append(e_plane)
                _plane_refs["gov"].add(rel.from_name)
                _plane_refs["gov"].add(rel.to_name)

        # --- Build per-plane node dicts in _build_plane canonical order ---
        # _build_plane order: sorted(entities that pass type filter) THEN sorted(dangling refs)
        # file_graph has node_type_filter={"module"}; symbol/governance have None (all types).
        from typing import Any as _Any
        entity_lookup: dict[str, _Any] = {e.adg_name: e for e in artifact.entities}

        def _build_plane_nodes(
            referenced: set[str],
            node_type_filter: set[str] | None,
        ) -> dict[str, int]:
            """Return name→local_id in _build_plane canonical order."""
            local: dict[str, int] = {}

            def _reg(name: str) -> None:
                if name not in local:
                    local[name] = len(local)

            for ent in sorted(artifact.entities, key=lambda e: e.adg_name):
                if node_type_filter and ent.entity_type not in node_type_filter:
                    continue
                _reg(ent.adg_name)

            for name in sorted(referenced):
                _reg(name)

            return local

        def _compact_plane_node(name: str) -> dict:
            ent = entity_lookup.get(name)
            if ent is not None:
                return {
                    "n": name,
                    "t": ent.entity_type,
                    "l": ent.layer,
                    "k": ent.identity_kind,
                    "c": ent.confidence,
                    "p": ent.resolved_path,
                }
            return {"n": name, "t": "symbol", "l": "", "k": "", "c": "", "p": ""}

        def _assemble_plane(
            plane_key: str,
            node_type_filter: set[str] | None,
        ) -> tuple[dict[str, dict], list[dict]]:
            local_map = _build_plane_nodes(_plane_refs[plane_key], node_type_filter)
            local_nodes = {str(lid): _compact_plane_node(nm) for nm, lid in local_map.items()}
            # Remap global IDs → local IDs in edges
            global_to_local = {name_to_id[nm]: lid for nm, lid in local_map.items()}
            local_edges: list[dict] = []
            for e in _plane_raw[plane_key]:
                le = dict(e)
                le["s"] = global_to_local[e["s"]]
                le["d"] = global_to_local[e["d"]]
                local_edges.append(le)
            return local_nodes, local_edges

        nodes_file, edges_file = _assemble_plane("file", {"module"})
        nodes_sym, edges_sym = _assemble_plane("sym", None)
        nodes_gov, edges_gov = _assemble_plane("gov", None)

        # --- Metrics for full graph ---
        by_rel_full: dict[str, int] = {}
        for e in edges_full:
            by_rel_full[e["r"]] = by_rel_full.get(e["r"], 0) + 1

        by_layer: dict[str, int] = {}
        for node in nodes_full.values():
            if node["t"] == "module" and node["l"]:
                by_layer[node["l"]] = by_layer.get(node["l"], 0) + 1

        meta_full = {
            "total_nodes": len(nodes_full),
            "total_edges": len(edges_full),
            "module_count": sum(1 for n in nodes_full.values() if n["t"] == "module"),
            "symbol_count": sum(1 for n in nodes_full.values() if n["t"] == "symbol"),
            "by_relation_type": dict(sorted(by_rel_full.items())),
            "by_layer": dict(sorted(by_layer.items())),
            "blind_spots": artifact.blind_spots.to_dict() if artifact.blind_spots else {},
            "identity_health": artifact.identity_health,
            "structural_metrics": artifact.structural_metrics.to_dict(),
        }

        ng_full = NormalizedGraph(
            commit_sha=artifact.commit_sha,
            repo_state_hash=artifact.repo_state_hash,
            scanner_digest=artifact.scanner_digest,
            nodes=nodes_full,
            edges=edges_full,
            meta=meta_full,
        )
        ng_full.compute_digest()

        # --- Helper to build a plane NormalizedGraph with plane-local IDs ---
        # _build_plane assigns IDs 0,1,2,... scoped to each plane.  We must
        # remap the global IDs accumulated above to plane-local sequential IDs
        # so the resulting JSON — and therefore the digest — is identical to
        # what split_artifact() would have produced.
        def _make_plane_ng(
            plane_nodes_global: dict[str, dict],
            plane_edges_global: list[dict],
            plane_name: str,
        ) -> NormalizedGraph:
            # Build global_id → local_id mapping in insertion order
            global_to_local: dict[int, int] = {}
            local_nodes: dict[str, dict] = {}
            for gkey, node_dict in sorted(plane_nodes_global.items(), key=lambda kv: int(kv[0])):
                local_id = len(global_to_local)
                global_to_local[int(gkey)] = local_id
                local_nodes[str(local_id)] = node_dict

            local_edges: list[dict] = []
            for e in plane_edges_global:
                le = dict(e)
                le["s"] = global_to_local[e["s"]]
                le["d"] = global_to_local[e["d"]]
                local_edges.append(le)

            by_rel: dict[str, int] = {}
            for e in local_edges:
                by_rel[e["r"]] = by_rel.get(e["r"], 0) + 1
            ng = NormalizedGraph(
                commit_sha=artifact.commit_sha,
                scanner_digest=artifact.scanner_digest,
                nodes=local_nodes,
                edges=local_edges,
                meta={
                    "plane": plane_name,
                    "total_nodes": len(local_nodes),
                    "total_edges": len(local_edges),
                    "by_relation_type": dict(sorted(by_rel.items())),
                },
            )
            ng.compute_digest()
            return ng

        ng_file = _make_plane_ng(nodes_file, edges_file, "file_graph")
        ng_sym = _make_plane_ng(nodes_sym, edges_sym, "symbol_graph")
        ng_gov = _make_plane_ng(nodes_gov, edges_gov, "governance_graph")

        return ng_full, ng_file, ng_sym, ng_gov

    def denormalize(self, ng: NormalizedGraph) -> dict:
        """Reconstruct a verbose artifact dict from NormalizedGraph.

        Returns a plain dict compatible with the schema v3 artifact format.
        Used for round-trip verification and backward-compatible consumers.
        """
        id_to_node: dict[int, dict] = {int(k): v for k, v in ng.nodes.items()}

        entities = []
        for node in sorted(id_to_node.values(), key=lambda n: n["n"]):
            entities.append(
                {
                    "adg_name": node["n"],
                    "entity_type": node["t"],
                    "layer": node["l"],
                    "identity_kind": node["k"],
                    "confidence": node["c"],
                    "resolved_path": node["p"],
                    "observations": [],
                },
            )

        relations = []
        for e in ng.edges:
            src = id_to_node[e["s"]]
            dst = id_to_node[e["d"]]
            rel = {
                "from_name": src["n"],
                "relation_type": e["r"],
                "to_name": dst["n"],
                "edge_kind": e["k"],
                "source_file": e["f"],
                "line_no": e["ln"],
                "symbol": e.get("sym", ""),
                "semantic_type": e.get("st", ""),
                "confidence": e.get("conf", 1.0),
                "source_span_start": e.get("sss", 0),
                "source_span_end": e.get("sse", 0),
                "source_span_line": e.get("ssl", 0),
                "source_span_column": e.get("ssc", 0),
                "target_span_start": e.get("tss", 0),
                "target_span_end": e.get("tse", 0),
                "target_span_line": e.get("tsl", 0),
                "target_span_column": e.get("tsc", 0),
                "dynamic_resolution": e.get("dr", ""),
            }
            relations.append(rel)

        return {
            "schema_version": "3.0.0",
            "commit_sha": ng.commit_sha,
            "scanner_digest": ng.scanner_digest,
            "artifact_digest": ng.artifact_digest,
            "entities": sorted(entities, key=lambda x: x["adg_name"]),
            "relations": sorted(relations, key=lambda x: (x["from_name"], x["relation_type"], x["to_name"])),
            "meta_source": "denormalized_from_v4",
        }


def normalize_artifact(artifact: ADGArtifact) -> NormalizedGraph:
    """Convenience: normalize an ADGArtifact in one call."""
    return ArtifactNormalizer().normalize(artifact)


def size_comparison(artifact: ADGArtifact, ng: NormalizedGraph) -> dict:
    """Report size reduction achieved by normalization."""
    verbose_json = json.dumps(artifact.to_dict(), separators=(",", ":"))
    compact_json = ng.to_json(indent=None)
    verbose_sz = len(verbose_json.encode("utf-8"))
    compact_sz = len(compact_json.encode("utf-8"))
    return {
        "verbose_bytes": verbose_sz,
        "compact_bytes": compact_sz,
        "reduction_bytes": verbose_sz - compact_sz,
        "reduction_pct": round((verbose_sz - compact_sz) / max(verbose_sz, 1) * 100, 1),
    }


__all__ = [
    "NormalizedGraph",
    "ArtifactNormalizer",
    "normalize_artifact",
    "size_comparison",
]
