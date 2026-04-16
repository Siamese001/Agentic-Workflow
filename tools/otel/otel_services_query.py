from __future__ import annotations

import json
import logging
import time
from typing import Any

from tools.otel.otel_config import OTelServerConfig
from tools.otel.otel_loaders import OTelLoaderBundle
from tools.otel.otel_mock import create_mock_trace
from tools.otel.otel_projection import convert_snapshot_to_adg_edges
from tools.otel.otel_state import RuntimeMetrics, TraceCache


logger = logging.getLogger(__name__)


class OTelQueryService:
    """Trace fetch and cache-backed analytical query surface."""

    def __init__(
        self,
        config: OTelServerConfig,
        loaders: OTelLoaderBundle,
        trace_cache: TraceCache,
        metrics: RuntimeMetrics,
    ) -> None:
        self._config = config
        self._loaders = loaders
        self._trace_cache = trace_cache
        self._metrics = metrics

    def trace(self, trace_id: str) -> dict[str, Any]:
        trace_id = trace_id.strip()
        if not trace_id:
            return {"success": False, "error": "trace_id cannot be empty"}
        if len(trace_id) < 8 or len(trace_id) > 128:
            return {"success": False, "error": "trace_id must be between 8 and 128 characters"}

        cached = self._trace_cache.get(trace_id)
        if cached is not None:
            logger.info("otel_trace_cache_hit", extra={"trace_id": trace_id})
            return cached

        store, store_error = self._loaders.safe_get(self._loaders.get_store_blocking, "runtime_adg_store")
        if store is not None:
            try:
                version_id = store.get_version_id_for_trace(trace_id)
                if version_id:
                    raw = store.get_by_version(version_id)
                    if raw:
                        snapshot = json.loads(raw)
                        result = {
                            "trace_id": trace_id,
                            "snapshot_id": snapshot.get("snapshot_id"),
                            "timestamp": snapshot.get("started_at_utc"),
                            "node_count": len(snapshot.get("nodes", [])),
                            "edge_count": len(convert_snapshot_to_adg_edges(snapshot)),
                            "adg_edges": convert_snapshot_to_adg_edges(snapshot),
                            "source": "file_backed_runtime_adg_store",
                        }
                        self._trace_cache.put(trace_id, result)
                        logger.info("otel_trace_loaded_from_store", extra={"trace_id": trace_id})
                        return result
            except Exception as exc:
                logger.error("otel_trace_store_read_error", extra={"trace_id": trace_id, "error": str(exc)})
                self._metrics.mark_error()

        snapshot_files = (
            list(self._config.runtime_adg_dir.glob(f"*{trace_id}*.json"))
            if self._config.runtime_adg_dir.exists()
            else []
        )
        if snapshot_files:
            try:
                with snapshot_files[0].open() as handle:
                    snapshot = json.load(handle)
                adg_edges = convert_snapshot_to_adg_edges(snapshot)
                result = {
                    "trace_id": trace_id,
                    "snapshot_id": snapshot.get("snapshot_id"),
                    "timestamp": snapshot.get("timestamp"),
                    "node_count": len(snapshot.get("nodes", [])),
                    "edge_count": len(adg_edges),
                    "adg_edges": adg_edges,
                    "source": "runtime_adg_snapshot",
                }
                self._trace_cache.put(trace_id, result)
                logger.info(
                    "otel_trace_loaded",
                    extra={
                        "trace_id": trace_id,
                        "node_count": result["node_count"],
                        "edge_count": result["edge_count"],
                    },
                )
                return result
            except Exception as exc:
                logger.error("otel_trace_load_error", extra={"trace_id": trace_id, "error": str(exc)})
                self._metrics.mark_error()

        if self._config.allow_mock_traces:
            mock_trace = create_mock_trace(trace_id)
            self._trace_cache.put(trace_id, mock_trace)
            logger.info("otel_trace_mock_created", extra={"trace_id": trace_id})
            return mock_trace

        return {
            "success": False,
            "error": "trace not found",
            "trace_id": trace_id,
            "store_error": store_error,
        }

    def spans_by_agent(self, agent_class: str, limit: int = 50) -> dict[str, Any]:
        spans: list[dict[str, Any]] = []
        for _trace_id, trace_data in self._trace_cache.items():
            for edge in trace_data.get("adg_edges", []):
                if edge.get("component") == agent_class:
                    spans.append(edge)
                    if len(spans) >= limit:
                        break
            if len(spans) >= limit:
                break

        result = {
            "agent_class": agent_class,
            "span_count": len(spans),
            "spans": spans[:limit],
            "search_time": int(time.time()),
        }
        logger.info(
            "otel_spans_by_agent_searched",
            extra={"agent_class": agent_class, "span_count": result["span_count"]},
        )
        return result

    def healing_chain(self, trace_id: str) -> dict[str, Any]:
        trace_data = self.trace(trace_id)
        edges = trace_data.get("adg_edges", [])
        healing_edges = [
            edge
            for edge in edges
            if any(
                keyword in edge.get("relation_type", "").lower()
                for keyword in ["healing", "escalation", "recovery"]
            )
        ]
        chain = [
            {
                "step": index,
                "relation_type": edge.get("relation_type"),
                "source": edge.get("source"),
                "target": edge.get("target"),
                "timestamp": edge.get("timestamp"),
                "attributes": edge.get("attributes", {}),
            }
            for index, edge in enumerate(healing_edges, start=1)
        ]
        result = {
            "trace_id": trace_id,
            "healing_events_found": len(healing_edges),
            "healing_chain": chain,
            "has_escalation": any(
                "escalation" in edge.get("relation_type", "").lower() for edge in healing_edges
            ),
        }
        logger.info(
            "otel_healing_chain_analyzed",
            extra={"trace_id": trace_id, "healing_events": result["healing_events_found"]},
        )
        return result

    def policy_decisions(self, time_window_hours: int = 24) -> dict[str, Any]:
        cutoff_time = int(time.time()) - (time_window_hours * 3600)
        policy_decisions: list[dict[str, Any]] = []
        for trace_id, trace_data in self._trace_cache.items():
            for edge in trace_data.get("adg_edges", []):
                if edge.get("timestamp", 0) >= cutoff_time and any(
                    keyword in edge.get("relation_type", "").lower()
                    for keyword in ["policy", "safety", "validation", "path"]
                ):
                    policy_decisions.append(
                        {
                            "trace_id": trace_id,
                            "relation_type": edge.get("relation_type"),
                            "source": edge.get("source"),
                            "target": edge.get("target"),
                            "timestamp": edge.get("timestamp"),
                            "attributes": edge.get("attributes", {}),
                        }
                    )
        result = {
            "time_window_hours": time_window_hours,
            "policy_decisions_found": len(policy_decisions),
            "policy_decisions": policy_decisions,
            "safety_plane_validations": len(
                [item for item in policy_decisions if "safety" in item.get("relation_type", "").lower()]
            ),
        }
        logger.info(
            "otel_policy_decisions_analyzed",
            extra={
                "time_window_hours": time_window_hours,
                "decisions_found": result["policy_decisions_found"],
            },
        )
        return result

    def metrics_summary(self) -> dict[str, Any]:
        edge_type_counts: dict[str, int] = {}
        layer_counts: dict[str, int] = {}
        component_counts: dict[str, int] = {}
        total_edges = 0
        error_edges = 0

        for trace_data in self._trace_cache.values():
            for edge in trace_data.get("adg_edges", []):
                edge_type = edge.get("relation_type", "unknown")
                layer = edge.get("layer", "unknown")
                component = edge.get("component", "unknown")
                edge_type_counts[edge_type] = edge_type_counts.get(edge_type, 0) + 1
                layer_counts[layer] = layer_counts.get(layer, 0) + 1
                component_counts[component] = component_counts.get(component, 0) + 1
                total_edges += 1
                if edge.get("status") == "error":
                    error_edges += 1

        result = {
            "summary_timestamp": int(time.time()),
            "total_cached_traces": len(self._trace_cache),
            "total_edges": total_edges,
            "error_edges": error_edges,
            "error_rate": error_edges / max(total_edges, 1),
            "edge_type_breakdown": dict(sorted(edge_type_counts.items())),
            "layer_breakdown": dict(sorted(layer_counts.items())),
            "top_components": dict(
                sorted(component_counts.items(), key=lambda item: item[1], reverse=True)[:10]
            ),
            "global_metrics": self._metrics.to_dict(),
        }
        logger.info(
            "otel_metrics_summary_generated",
            extra={"total_edges": total_edges, "error_rate": result["error_rate"]},
        )
        return result

    def anomalies(self, severity: str = "any") -> dict[str, Any]:
        if severity not in {"any", "low", "medium", "high"}:
            return {"success": False, "error": "severity must be one of: any, low, medium, high"}

        anomalies: list[dict[str, Any]] = []
        for trace_id, trace_data in self._trace_cache.items():
            for edge in trace_data.get("adg_edges", []):
                attributes = edge.get("attributes", {})
                is_anomaly = (
                    attributes.get("error", False)
                    or attributes.get("circuit_breaker_open", False)
                    or attributes.get("safety_plane_triggered", False)
                    or "anomaly" in edge.get("relation_type", "").lower()
                )
                if not is_anomaly:
                    continue
                anomaly_severity = attributes.get("severity", "medium")
                if severity == "any" or anomaly_severity == severity:
                    anomalies.append(
                        {
                            "trace_id": trace_id,
                            "relation_type": edge.get("relation_type"),
                            "source": edge.get("source"),
                            "target": edge.get("target"),
                            "timestamp": edge.get("timestamp"),
                            "severity": anomaly_severity,
                            "error": attributes.get("error"),
                            "circuit_breaker_open": attributes.get("circuit_breaker_open"),
                            "safety_plane_triggered": attributes.get("safety_plane_triggered"),
                            "attributes": attributes,
                        }
                    )

        anomalies.sort(key=lambda item: item.get("timestamp", 0), reverse=True)
        self._metrics.anomaly_count = len(anomalies)
        result = {
            "severity_filter": severity,
            "anomalies_found": len(anomalies),
            "anomalies": anomalies[:100],
            "high_severity_count": len([item for item in anomalies if item.get("severity") == "high"]),
            "medium_severity_count": len([item for item in anomalies if item.get("severity") == "medium"]),
            "low_severity_count": len([item for item in anomalies if item.get("severity") == "low"]),
        }
        logger.info(
            "otel_anomalies_analyzed",
            extra={"severity": severity, "anomalies_found": result["anomalies_found"]},
        )
        return result
