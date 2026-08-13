"""Build a read-only C0.3 graph health receipt.

The canonical JSON remains graph authority and SQLite remains a generated
projection.  This module only reads those artifacts.  It never calls an
``ensure_*`` or materializer API, never opens SQLite writable, and never writes
unless the CLI receives an explicit ``--output`` path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from agentic_core.L4_state.adapters import sqlite3_adapter as sqlite3
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    canonical_node_type,
    open_graph_sqlite,
    project_registered_graph_node_type,
    projected_graph_edge_signature_report,
    projected_registered_graph_edge_signatures,
)
from apps_rg.fact_inventory.c03_graph_operational_evidence import (
    METRIC_IDS as OPERATIONAL_METRIC_IDS,
)
from apps_rg.fact_inventory.c03_graph_operational_evidence import (
    PRODUCER_REGISTRY_VERSION as OPERATIONAL_PRODUCER_REGISTRY_VERSION,
)
from apps_rg.fact_inventory.c03_graph_operational_evidence import (
    SCHEMA_VERSION as OPERATIONAL_EVIDENCE_SCHEMA_VERSION,
)
from apps_rg.fact_inventory.c03_graph_operational_evidence import (
    OperationalTrustContext,
    verify_operational_evidence_envelope,
)
from apps_rg.fact_inventory.graph_metric_heterogeneity_policy import (
    POLICY_VERSION as METRIC_HETEROGENEITY_POLICY_VERSION,
)
from apps_rg.fact_inventory.graph_metric_heterogeneity_policy import (
    metric_bucket_for_row,
)
from apps_rg.fact_inventory.graph_sqlite_path_index import (
    SIBLING_NODE_TYPES,
    compute_sqlite_graph_digest,
    compute_sqlite_schema_digest,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    derive_registered_graph_endpoint_types,
    graph_node_requires_source_refs,
)

SCHEMA_VERSION = "apps_rg.c03_graph_kpi_health_receipt.v2"
BUILDER_VERSION = "c03_graph_kpi_health_builder.v4.producer_bound_operational_evidence"
CANONICAL_CHECK_VERSION = "c03_graph_canonical_health_checks.v2"
SQLITE_CHECK_VERSION = "c03_graph_sqlite_health_checks.v3"
POLICY_SCHEMA_VERSION = "apps_rg.c03_graph_health_policy.v2"
POLICY_VERSION = "c03_graph_health_policy.v4.producer_bound_operational_evidence"

DEFAULT_CANONICAL_REL = Path("apps_rg/fact_inventory/master_skills_arsenal_ledger.json")
DEFAULT_SQLITE_REL = Path("artifacts/apps_rg/fact_inventory/augmented_skills_graph.sqlite")
DEFAULT_POLICY_REL = Path("apps_rg/config/c03_graph_health_policy.v2.json")

STATUS_PRECEDENCE = {
    "PASS": 0,
    "UNKNOWN": 1,
    "NOT_READY": 2,
    "MIGRATION_REQUIRED": 3,
    "BLOCKED": 4,
}

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

CONTROL_PLANE_METRIC_IDS = (
    "canonical_artifact_available",
    "sqlite_artifact_available",
    "sqlite_read_purity",
    "canonical_sqlite_digest_match",
    "canonical_metadata_node_count_parity",
    "canonical_metadata_edge_count_parity",
    "sqlite_projection_node_count_parity",
    "sqlite_projection_edge_count_parity",
    "sqlite_foreign_key_coverage",
    "sqlite_foreign_key_integrity",
    "reverse_view_parity",
    "decision_safe_regression",
    "source_currentness",
    "source_freshness",
    "hitl_approval_coverage",
    "write_audit_coverage",
    "p0_sla_compliance",
    "p1_sla_compliance",
)
GRAPH_DATA_METRIC_IDS = (
    "orphan_edge_rate",
    "duplicate_node_id_rate",
    "duplicate_edge_id_rate",
    "duplicate_logical_edge_rate",
    "identity_collision_rate",
    "explicit_endpoint_closure",
    "registered_endpoint_closure",
    "canonical_projected_edge_signature_integrity",
    "sqlite_projected_edge_signature_integrity",
    "claim_evidence_completeness",
    "skill_row_node_coverage",
    "skill_source_metadata_completeness",
    "graph_node_source_ref_completeness",
    "temporal_completeness",
    "rare_edge_type_rate",
    "path_integrity",
    "sibling_integrity",
    "neighborhood_integrity",
    "metric_bucket_concentration",
    "domain_coverage",
    "epoch_coverage",
)
EXPECTED_METRIC_IDS = CONTROL_PLANE_METRIC_IDS + GRAPH_DATA_METRIC_IDS
_METRIC_SPEC_FIELDS = frozenset({"plane", "operator", "target", "failure_status", "required"})
_ALLOWED_OPERATORS = frozenset({">=", "<=", "=="})
_ALLOWED_FAILURE_STATUSES = frozenset({"BLOCK", "FAIL", "MIGRATION_REQUIRED"})


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_policy_path(repo_root: Path | None = None) -> Path:
    return (repo_root or _repo_root()) / DEFAULT_POLICY_REL


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sqlite_sidecar_names(path: Path) -> tuple[str, ...]:
    """Return the exact SQLite sidecar set without opening or creating files."""
    return tuple(
        sorted(candidate.name for candidate in path.parent.glob(f"{path.name}-*") if candidate.is_file())
    )


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _payload_digest(value: Any) -> str:
    return _sha256_bytes(_canonical_json(value).encode("utf-8"))


def _load_json_object(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if not isinstance(raw, dict):
        return None, f"TypeError: expected JSON object, found {type(raw).__name__}"
    return raw, None


def _validate_policy_metrics(metrics: Any) -> None:
    if not isinstance(metrics, dict) or not metrics:
        raise ValueError("graph health policy metrics must be a non-empty object")
    expected = set(EXPECTED_METRIC_IDS)
    observed = set(metrics)
    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    if missing or extra:
        raise ValueError(f"graph health policy metric registry drift: missing={missing}, extra={extra}")

    control_plane = set(CONTROL_PLANE_METRIC_IDS)
    for metric_id in EXPECTED_METRIC_IDS:
        spec = metrics[metric_id]
        if not isinstance(spec, dict):
            raise ValueError(f"graph health policy metric {metric_id!r} must be an object")
        fields = set(spec)
        if fields != _METRIC_SPEC_FIELDS:
            raise ValueError(
                f"graph health policy metric {metric_id!r} fields drift: "
                f"missing={sorted(_METRIC_SPEC_FIELDS - fields)}, "
                f"extra={sorted(fields - _METRIC_SPEC_FIELDS)}"
            )
        expected_plane = "control_plane" if metric_id in control_plane else "graph_data"
        if spec["plane"] != expected_plane:
            raise ValueError(f"graph health policy metric {metric_id!r} plane must be {expected_plane!r}")
        if spec["operator"] not in _ALLOWED_OPERATORS:
            raise ValueError(f"graph health policy metric {metric_id!r} has unsupported operator")
        target = spec["target"]
        if (
            isinstance(target, bool)
            or not isinstance(target, (int, float))
            or not math.isfinite(float(target))
            or not 0.0 <= float(target) <= 1.0
        ):
            raise ValueError(f"graph health policy metric {metric_id!r} target must be finite in [0, 1]")
        if spec["failure_status"] not in _ALLOWED_FAILURE_STATUSES:
            raise ValueError(f"graph health policy metric {metric_id!r} has unsupported failure_status")
        if not isinstance(spec["required"], bool):
            raise ValueError(f"graph health policy metric {metric_id!r} required must be boolean")


def load_health_policy(path: Path | None = None) -> dict[str, Any]:
    policy_path = path or default_policy_path()
    policy, error = _load_json_object(policy_path)
    if policy is None:
        raise ValueError(f"invalid graph health policy {policy_path}: {error}")
    if policy.get("schema_version") != POLICY_SCHEMA_VERSION:
        raise ValueError(f"unsupported graph health policy schema: {policy.get('schema_version')}")
    if policy.get("policy_version") != POLICY_VERSION:
        raise ValueError(f"unsupported graph health policy version: {policy.get('policy_version')}")
    if policy.get("operational_evidence_schema_version") != OPERATIONAL_EVIDENCE_SCHEMA_VERSION:
        raise ValueError(
            "graph health policy operational evidence schema does not match the code-owned contract"
        )
    if policy.get("operational_producer_registry_version") != OPERATIONAL_PRODUCER_REGISTRY_VERSION:
        raise ValueError(
            "graph health policy operational producer registry does not match the code-owned contract"
        )
    _validate_policy_metrics(policy.get("metrics"))
    return policy


def _as_rows(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [row for row in value if isinstance(row, dict)]


def _nonempty_strings(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple, set)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _string(value: Any) -> str:
    return str(value or "").strip()


def _valid_count(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _stable_samples(values: Iterable[Any], limit: int) -> list[Any]:
    materialized = list(values)
    materialized.sort(key=lambda value: _canonical_json(value))
    return materialized[:limit]


def _cohort(
    *,
    kind: str,
    cohort_id: str,
    digest: str | None,
    definition: str,
) -> dict[str, Any]:
    return {
        "kind": kind,
        "cohort_id": cohort_id,
        "cohort_digest": digest,
        "definition": definition,
    }


def _target_satisfied(rate: float, operator: str, target: float) -> bool:
    if operator == ">=":
        return rate >= target
    if operator == "<=":
        return rate <= target
    if operator == "==":
        return rate == target
    raise ValueError(f"unsupported metric target operator: {operator}")


def _metric(
    policy: Mapping[str, Any],
    metric_id: str,
    *,
    numerator: int | None,
    denominator: int | None,
    numerator_semantics: str,
    denominator_semantics: str,
    cohort: Mapping[str, Any],
    failure_count: int | None = None,
    failure_locators: Iterable[Any] = (),
    unknown_reason: str | None = None,
    status_override: str | None = None,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    specs = policy["metrics"]
    if metric_id not in specs:
        raise KeyError(f"metric missing from policy: {metric_id}")
    spec = specs[metric_id]
    operator = str(spec["operator"])
    target = float(spec["target"])
    sample_limit = int(policy.get("sample_limit") or 12)

    rate: float | None = None
    if numerator is not None and denominator is not None and denominator > 0:
        rate = round(numerator / denominator, 6)

    if status_override is not None:
        status = status_override
    elif unknown_reason is not None or numerator is None or denominator is None or denominator <= 0:
        status = "UNKNOWN"
        if unknown_reason is None:
            unknown_reason = "denominator_missing_or_zero"
    elif _target_satisfied(float(rate), operator, target):
        status = "PASS"
    else:
        status = str(spec.get("failure_status") or "FAIL")

    if status == "UNKNOWN":
        rate = None
    if failure_count is None and numerator is not None and denominator is not None:
        if operator == ">=":
            failure_count = max(0, denominator - numerator)
        elif operator == "<=":
            failure_count = max(0, numerator)
        elif operator == "==":
            failure_count = abs(denominator - numerator)

    result: dict[str, Any] = {
        "metric_id": metric_id,
        "plane": spec["plane"],
        "required": bool(spec.get("required", True)),
        "frozen_measurement": True,
        "cohort": dict(cohort),
        "numerator": numerator,
        "numerator_semantics": numerator_semantics,
        "denominator": denominator,
        "denominator_semantics": denominator_semantics,
        "rate": rate,
        "target": {"operator": operator, "value": target},
        "status": status,
        "failure_count": failure_count,
        "sample_failure_locators": _stable_samples(failure_locators, sample_limit),
    }
    if unknown_reason:
        result["unknown_reason"] = unknown_reason
    if details:
        result["details"] = dict(details)
    return result


def _unknown_metric(
    policy: Mapping[str, Any],
    metric_id: str,
    *,
    reason: str,
    cohort: Mapping[str, Any],
    denominator_semantics: str,
) -> dict[str, Any]:
    return _metric(
        policy,
        metric_id,
        numerator=None,
        denominator=None,
        numerator_semantics="unsupported without authoritative evidence",
        denominator_semantics=denominator_semantics,
        cohort=cohort,
        unknown_reason=reason,
    )


class _MetricCollector:
    """Bind policy and cohort so collectors stay data-focused."""

    def __init__(self, policy: Mapping[str, Any], cohort: Mapping[str, Any]) -> None:
        self.policy = policy
        self.cohort = cohort
        self.rows: list[dict[str, Any]] = []

    def add(
        self,
        metric_id: str,
        numerator: int | None,
        denominator: int | None,
        numerator_semantics: str,
        denominator_semantics: str,
        **kwargs: Any,
    ) -> None:
        self.rows.append(
            _metric(
                self.policy,
                metric_id,
                numerator=numerator,
                denominator=denominator,
                numerator_semantics=numerator_semantics,
                denominator_semantics=denominator_semantics,
                cohort=self.cohort,
                **kwargs,
            )
        )

    def unknown(self, metric_id: str, reason: str, denominator_semantics: str) -> None:
        self.rows.append(
            _unknown_metric(
                self.policy,
                metric_id,
                reason=reason,
                cohort=self.cohort,
                denominator_semantics=denominator_semantics,
            )
        )


def _rollup_metric_statuses(metrics: Sequence[Mapping[str, Any]], plane: str) -> str:
    statuses = {
        str(row.get("status"))
        for row in metrics
        if row.get("plane") == plane and bool(row.get("required", True))
    }
    if "BLOCK" in statuses:
        return "BLOCKED"
    if "MIGRATION_REQUIRED" in statuses:
        return "MIGRATION_REQUIRED"
    if "FAIL" in statuses:
        return "NOT_READY"
    if "UNKNOWN" in statuses:
        return "UNKNOWN"
    return "PASS"


def _rollup_overall(control_plane_status: str, graph_data_readiness: str) -> str:
    values = (control_plane_status, graph_data_readiness)
    return max(values, key=lambda value: STATUS_PRECEDENCE[value])


def _counter_duplicates(values: Iterable[str]) -> tuple[int, list[dict[str, Any]]]:
    counts = Counter(value for value in values if value)
    samples = [{"identity": value, "occurrences": count} for value, count in counts.items() if count > 1]
    return sum(count - 1 for count in counts.values() if count > 1), samples


def _registry_items(value: Any) -> set[str]:
    out: set[str] = set()
    if isinstance(value, dict):
        out.update(str(key).strip() for key in value if str(key).strip())
        for row in value.values():
            if isinstance(row, dict):
                for key in ("node_id", "endpoint_id", "id", "skill_id", "fact_id"):
                    if _string(row.get(key)):
                        out.add(_string(row[key]))
            elif isinstance(row, str) and row.strip():
                out.add(row.strip())
    elif isinstance(value, list):
        for row in value:
            if isinstance(row, str) and row.strip():
                out.add(row.strip())
            elif isinstance(row, dict):
                for key in ("node_id", "endpoint_id", "id", "skill_id", "fact_id"):
                    if _string(row.get(key)):
                        out.add(_string(row[key]))
    return out


def _registered_endpoint_ids(
    payload: Mapping[str, Any], explicit_ids: set[str], policy: Mapping[str, Any]
) -> set[str]:
    del policy
    return set(explicit_ids) | set(derive_registered_graph_endpoint_types(payload))


def _canonical_projected_endpoint_types(
    payload: Mapping[str, Any],
) -> dict[str, str]:
    raw_types = {
        _string(row.get("node_id")): _string(row.get("node_type"))
        for row in _as_rows(payload.get("graph_nodes"))
        if _string(row.get("node_id"))
    }
    for endpoint_id, raw_type in derive_registered_graph_endpoint_types(payload).items():
        raw_types.setdefault(endpoint_id, raw_type)
    projected: dict[str, str] = {}
    for endpoint_id, raw_type in raw_types.items():
        try:
            projected[endpoint_id] = project_registered_graph_node_type(raw_type)
        except ValueError:
            projected[endpoint_id] = f"<unregistered:{raw_type or 'blank'}>"
    return projected


def _edge_signature_metric_details(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "edge_count": report["edge_count"],
        "registered_edge_count": report["registered_edge_count"],
        "unregistered_edge_count": report["unregistered_edge_count"],
        "normalized_registered_edge_type_count": len(projected_registered_graph_edge_signatures()),
    }


def _canonical_metrics(
    payload: Mapping[str, Any],
    policy: Mapping[str, Any],
    *,
    canonical_digest: str,
) -> list[dict[str, Any]]:
    nodes = _as_rows(payload.get("graph_nodes"))
    edges = _as_rows(payload.get("graph_edges"))
    skills = _as_rows(payload.get("skill_rows"))
    cohort = _cohort(
        kind="observed_operational_graph",
        cohort_id=f"canonical:{canonical_digest[:16]}",
        digest=canonical_digest,
        definition="Rows present in the immutable canonical JSON input identified by this digest.",
    )
    collector = _MetricCollector(policy, cohort)

    node_ids = [_string(row.get("node_id")) for row in nodes]
    edge_ids = [_string(row.get("edge_id")) for row in edges]
    explicit_ids = {value for value in node_ids if value}
    registered_ids = _registered_endpoint_ids(payload, explicit_ids, policy)

    for metric_id, values, rows, identity_name in (
        ("duplicate_node_id_rate", node_ids, nodes, "node_id"),
        ("duplicate_edge_id_rate", edge_ids, edges, "edge_id"),
    ):
        duplicate_count, samples = _counter_duplicates(values)
        collector.add(
            metric_id,
            duplicate_count,
            len(rows),
            f"duplicate rows beyond the first row for each nonblank {identity_name}",
            f"all canonical {identity_name} rows in the observed graph digest",
            failure_locators=samples,
        )

    logical_edges = [
        (
            _string(row.get("source_node_id")),
            _string(row.get("target_node_id")),
            _string(row.get("edge_type")),
        )
        for row in edges
    ]
    logical_counts = Counter(logical_edges)
    duplicate_logical = sum(count - 1 for count in logical_counts.values() if count > 1)
    logical_samples = [
        {"source_node_id": key[0], "target_node_id": key[1], "edge_type": key[2], "occurrences": count}
        for key, count in logical_counts.items()
        if count > 1
    ]
    collector.add(
        "duplicate_logical_edge_rate",
        duplicate_logical,
        len(edges),
        "edge rows beyond the first row for each source-target-type triple",
        "all canonical graph_edge rows in the observed graph digest",
        failure_locators=logical_samples,
    )

    node_fingerprints: dict[str, set[tuple[str, str]]] = defaultdict(set)
    edge_fingerprints: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
    for row in nodes:
        node_fingerprints[_string(row.get("node_id"))].add(
            (_string(row.get("node_type")), _string(row.get("label")))
        )
    for row in edges:
        edge_fingerprints[_string(row.get("edge_id"))].add(
            (
                _string(row.get("source_node_id")),
                _string(row.get("target_node_id")),
                _string(row.get("edge_type")),
            )
        )
    collision_samples = [
        {"namespace": "node", "identity": key, "semantic_variants": len(values)}
        for key, values in node_fingerprints.items()
        if key and len(values) > 1
    ]
    collision_samples.extend(
        {"namespace": "edge", "identity": key, "semantic_variants": len(values)}
        for key, values in edge_fingerprints.items()
        if key and len(values) > 1
    )
    identity_denominator = len({value for value in node_ids if value}) + len(
        {value for value in edge_ids if value}
    )
    collector.add(
        "identity_collision_rate",
        len(collision_samples),
        identity_denominator,
        "node or edge identifiers bound to more than one semantic fingerprint",
        "all unique nonblank node_id and edge_id identities",
        failure_locators=collision_samples,
    )

    endpoint_denominator = len(edges) * 2
    explicit_closed = 0
    registered_closed = 0
    orphan_edges: list[dict[str, Any]] = []
    explicit_failures: list[dict[str, Any]] = []
    registered_failures: list[dict[str, Any]] = []
    for row in edges:
        edge_id = _string(row.get("edge_id")) or "<blank-edge-id>"
        endpoints = (
            ("source_node_id", _string(row.get("source_node_id"))),
            ("target_node_id", _string(row.get("target_node_id"))),
        )
        missing_registered: list[str] = []
        for field, endpoint_id in endpoints:
            if endpoint_id in explicit_ids:
                explicit_closed += 1
            else:
                explicit_failures.append({"edge_id": edge_id, "field": field, "endpoint_id": endpoint_id})
            if endpoint_id and endpoint_id in registered_ids:
                registered_closed += 1
            else:
                registered_failures.append({"edge_id": edge_id, "field": field, "endpoint_id": endpoint_id})
                missing_registered.append(endpoint_id or f"<{field}:blank>")
        if missing_registered:
            orphan_edges.append({"edge_id": edge_id, "missing_registered_endpoints": missing_registered})
    collector.add(
        "explicit_endpoint_closure",
        explicit_closed,
        endpoint_denominator,
        "edge endpoint references present as explicit canonical graph_nodes",
        "two endpoint references for every canonical graph_edge row",
        failure_locators=explicit_failures,
    )
    collector.add(
        "registered_endpoint_closure",
        registered_closed,
        endpoint_denominator,
        "edge endpoint references present in explicit nodes or deterministic canonical registries",
        "two endpoint references for every canonical graph_edge row",
        failure_locators=registered_failures,
        details={"registered_endpoint_count": len(registered_ids)},
    )
    canonical_signature_report = projected_graph_edge_signature_report(
        node_types_by_id=_canonical_projected_endpoint_types(payload),
        edge_rows=edges,
    )
    collector.add(
        "canonical_projected_edge_signature_integrity",
        canonical_signature_report["valid_edge_count"],
        canonical_signature_report["edge_count"],
        "canonical edges admitted by a type authority with a valid projected endpoint signature",
        "all canonical graph_edge rows",
        failure_count=canonical_signature_report["failure_count"],
        failure_locators=canonical_signature_report["failure_locators"],
        details=_edge_signature_metric_details(canonical_signature_report),
    )
    collector.add(
        "orphan_edge_rate",
        len(orphan_edges),
        len(edges),
        "edges with at least one blank or unregistered endpoint",
        "all canonical graph_edge rows in the observed graph digest",
        failure_locators=orphan_edges,
    )

    graph_metadata = payload.get("graph_metadata") if isinstance(payload.get("graph_metadata"), dict) else {}
    for metric_id, rows, metadata_key, row_name in (
        ("canonical_metadata_node_count_parity", nodes, "node_count", "graph_node"),
        ("canonical_metadata_edge_count_parity", edges, "edge_count", "graph_edge"),
    ):
        expected = _valid_count(graph_metadata.get(metadata_key))
        observed = len(rows)
        collector.add(
            metric_id,
            observed if expected is not None else None,
            expected,
            f"observed canonical {row_name} row count",
            f"frozen graph_metadata.{metadata_key} declared by the canonical artifact",
            failure_count=abs(observed - expected) if expected is not None else None,
            failure_locators=(
                [{"field": f"graph_metadata.{metadata_key}", "declared": expected, "observed": observed}]
                if expected is not None and expected != observed
                else []
            ),
            unknown_reason=f"graph_metadata.{metadata_key}_missing_or_invalid" if expected is None else None,
        )

    graph_fact_bindings: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        if _string(edge.get("edge_type")) == "skill_supported_by_fact":
            graph_fact_bindings[_string(edge.get("source_node_id"))].add(_string(edge.get("target_node_id")))
    claim_evidence_complete: list[dict[str, Any]] = []
    claim_evidence_failures: list[dict[str, Any]] = []
    explicitly_ineligible = 0
    for row in skills:
        skill_id = _string(row.get("skill_id"))
        declared_fact_ids = set(_nonempty_strings(row.get("fact_id_links")))
        bound_fact_ids = graph_fact_bindings.get(skill_id, set())
        missing_bindings = sorted(declared_fact_ids - bound_fact_ids)
        retrieval_disposition = row.get("retrieval_eligible")
        ineligibility_reason = _string(row.get("retrieval_ineligibility_reason"))
        if retrieval_disposition is False and ineligibility_reason:
            explicitly_ineligible += 1
            claim_evidence_complete.append(row)
        elif retrieval_disposition is False:
            claim_evidence_failures.append(
                {
                    "skill_id": skill_id or "<blank-skill-id>",
                    "declared_fact_ids": sorted(declared_fact_ids),
                    "bound_graph_fact_ids": sorted(bound_fact_ids),
                    "missing_graph_fact_bindings": missing_bindings,
                    "reason": "non_retrieval_disposition_reason_missing",
                }
            )
        elif declared_fact_ids and not missing_bindings:
            claim_evidence_complete.append(row)
        else:
            claim_evidence_failures.append(
                {
                    "skill_id": skill_id or "<blank-skill-id>",
                    "declared_fact_ids": sorted(declared_fact_ids),
                    "bound_graph_fact_ids": sorted(bound_fact_ids),
                    "missing_graph_fact_bindings": missing_bindings,
                    "reason": "declared_fact_ids_missing"
                    if not declared_fact_ids
                    else "graph_binding_missing",
                }
            )
    collector.add(
        "claim_evidence_completeness",
        len(claim_evidence_complete),
        len(skills),
        (
            "skill_rows whose declared fact_id_links are all graph-bound, or whose explicit "
            "non-retrieval disposition has a reason"
        ),
        (
            "all canonical skill_rows in the graph digest; source snippets are not graph fact "
            "bindings and cannot make a row retrieval-eligible"
        ),
        failure_count=len(claim_evidence_failures),
        failure_locators=claim_evidence_failures,
        details={"explicitly_non_retrieval_eligible": explicitly_ineligible},
    )

    provenance_nodes = [row for row in nodes if graph_node_requires_source_refs(row)]
    coverage_specs = (
        (
            "skill_row_node_coverage",
            skills,
            lambda row: _string(row.get("skill_id")) in explicit_ids,
            "skill_id",
            "skill_rows whose skill_id has an explicit canonical skill or skill_row graph node",
        ),
        (
            "skill_source_metadata_completeness",
            skills,
            lambda row: bool(
                _nonempty_strings(row.get("source_resume_files"))
                or _nonempty_strings(row.get("repo_evidence_files"))
                or _string(row.get("source_ledger_ref"))
            ),
            "skill_id",
            "skill_rows with a resume source file, repository evidence file, or source ledger reference",
        ),
        (
            "graph_node_source_ref_completeness",
            provenance_nodes,
            lambda row: bool(_nonempty_strings(row.get("source_refs"))),
            "node_id",
            "policy-required provenance graph_nodes with at least one nonblank source_refs locator",
        ),
        (
            "domain_coverage",
            skills,
            lambda row: bool(_string(row.get("domain_id"))),
            "skill_id",
            "skill_rows with a nonblank domain_id",
        ),
        (
            "epoch_coverage",
            skills,
            lambda row: bool(_string(row.get("career_epoch"))),
            "skill_id",
            "skill_rows with a nonblank career_epoch",
        ),
    )
    for metric_id, rows, predicate, locator_key, numerator_text in coverage_specs:
        passed = [row for row in rows if predicate(row)]
        failures = [
            {locator_key: _string(row.get(locator_key)) or f"<blank-{locator_key}>"}
            for row in rows
            if not predicate(row)
        ]
        collector.add(
            metric_id,
            len(passed),
            len(rows),
            numerator_text,
            (
                "canonical graph_nodes whose claim and visibility policy requires source_refs"
                if metric_id == "graph_node_source_ref_completeness"
                else f"all canonical {'graph_nodes' if locator_key == 'node_id' else 'skill_rows'} in the graph digest"
            ),
            failure_count=len(failures),
            failure_locators=failures,
        )

    temporal_types = {str(value) for value in policy.get("temporal_node_types") or []}
    temporal_nodes = [row for row in nodes if _string(row.get("node_type")) in temporal_types]
    temporal_complete: list[dict[str, Any]] = []
    temporal_failures: list[dict[str, Any]] = []
    for row in temporal_nodes:
        has_start = bool(_string(row.get("start_date")) or _string(row.get("start_year")))
        has_end = bool(
            row.get("is_current") is True or _string(row.get("end_date")) or _string(row.get("end_year"))
        )
        if has_start and has_end:
            temporal_complete.append(row)
        else:
            temporal_failures.append({"node_id": _string(row.get("node_id")) or "<blank-node-id>"})
    collector.add(
        "temporal_completeness",
        len(temporal_complete),
        len(temporal_nodes),
        "temporal nodes with a start locator and an end locator or current-state marker",
        f"canonical graph_nodes whose node_type is in {sorted(temporal_types)}",
        failure_locators=temporal_failures,
    )

    edge_type_counts = Counter(_string(row.get("edge_type")) or "<blank-edge-type>" for row in edges)
    rare_minimum = int(policy.get("rare_edge_type_min_count") or 2)
    rare_exemptions = {
        str(value).strip()
        for value in policy.get("rare_edge_type_exemptions") or []
        if str(value).strip()
    }
    rare_types = {
        edge_type: count
        for edge_type, count in edge_type_counts.items()
        if count < rare_minimum and edge_type not in rare_exemptions
    }
    rare_rows = sum(rare_types.values())
    collector.add(
        "rare_edge_type_rate",
        rare_rows,
        len(edges),
        f"edge rows whose edge_type occurs fewer than {rare_minimum} times",
        "all canonical graph_edge rows in the observed graph digest",
        failure_locators=(
            {"edge_type": edge_type, "observed_count": count, "minimum_count": rare_minimum}
            for edge_type, count in rare_types.items()
        ),
        details={
            "distinct_edge_type_count": len(edge_type_counts),
            "exempt_singleton_policy_edge_types": sorted(
                edge_type
                for edge_type, count in edge_type_counts.items()
                if count < rare_minimum and edge_type in rare_exemptions
            ),
        },
    )

    bucket_counts = Counter(_string(metric_bucket_for_row(row)) or "<unclassified>" for row in skills)
    largest_bucket_count = max(bucket_counts.values(), default=0)
    collector.add(
        "metric_bucket_concentration",
        largest_bucket_count,
        len(skills),
        "skill_rows in the most frequent policy-derived metric bucket, including fallback classification",
        "all canonical skill_rows in the observed graph digest",
        failure_locators=(
            {"metric_bucket": bucket, "row_count": count}
            for bucket, count in bucket_counts.items()
            if count == largest_bucket_count
        ),
        details={"metric_bucket_counts": dict(sorted(bucket_counts.items()))},
    )

    return collector.rows


def _safe_identifier(value: str) -> str:
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"unsafe SQLite identifier: {value}")
    return value


def _table_exists(conn: sqlite3.Connection, name: str, *, kind: str | None = None) -> bool:
    if kind:
        row = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type=? AND name=? LIMIT 1",
            (kind, name),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type IN ('table','view') AND name=? LIMIT 1",
            (name,),
        ).fetchone()
    return bool(row)


def _table_columns(conn: sqlite3.Connection, name: str) -> set[str]:
    safe = _safe_identifier(name)
    return {str(row[1]) for row in conn.execute(f"PRAGMA table_info({safe})")}


def _table_count(conn: sqlite3.Connection, name: str) -> int | None:
    if not _table_exists(conn, name, kind="table"):
        return None
    safe = _safe_identifier(name)
    return int(conn.execute(f"SELECT COUNT(*) FROM {safe}").fetchone()[0])


def _read_sqlite_metadata(conn: sqlite3.Connection) -> dict[str, Any]:
    if not _table_exists(conn, "graph_metadata", kind="table"):
        return {}
    columns = _table_columns(conn, "graph_metadata")
    selected = [
        name
        for name in ("graph_version", "materialized_at", "ledger_hash", "graph_count_summary")
        if name in columns
    ]
    if not selected:
        return {}
    order = " ORDER BY materialized_at DESC" if "materialized_at" in columns else ""
    row = conn.execute(f"SELECT {','.join(selected)} FROM graph_metadata{order} LIMIT 1").fetchone()
    if row is None:
        return {}
    result = dict(zip(selected, row, strict=True))
    summary: dict[str, Any] = {}
    if "graph_count_summary" in result:
        try:
            decoded = json.loads(result.get("graph_count_summary") or "{}")
            if isinstance(decoded, dict):
                summary = decoded
        except (TypeError, json.JSONDecodeError):
            summary = {}
    result["graph_count_summary"] = summary
    return result


def _foreign_key_signatures(
    conn: sqlite3.Connection, tables: Iterable[str]
) -> set[tuple[str, str, str, str]]:
    signatures: set[tuple[str, str, str, str]] = set()
    for table in sorted(set(tables)):
        if not _table_exists(conn, table, kind="table"):
            continue
        safe = _safe_identifier(table)
        for row in conn.execute(f"PRAGMA foreign_key_list({safe})"):
            signatures.add((table, str(row[3]), str(row[2]), str(row[4])))
    return signatures


def _load_sqlite_edges(conn: sqlite3.Connection) -> list[dict[str, str]] | None:
    if not _table_exists(conn, "graph_edges", kind="table"):
        return None
    required = {"edge_id", "source_node_id", "target_node_id", "edge_type"}
    if not required.issubset(_table_columns(conn, "graph_edges")):
        return None
    return [
        {
            "edge_id": _string(row[0]),
            "source_node_id": _string(row[1]),
            "target_node_id": _string(row[2]),
            "edge_type": _string(row[3]),
        }
        for row in conn.execute(
            "SELECT edge_id,source_node_id,target_node_id,edge_type FROM graph_edges ORDER BY edge_id"
        )
    ]


def _canonical_graph_semantic_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    nodes = sorted(
        [
            {
                "node_id": _string(row.get("node_id")),
                "node_type": canonical_node_type(
                    _string(row.get("node_type")),
                    node_id=_string(row.get("node_id")),
                ),
            }
            for row in _as_rows(payload.get("graph_nodes"))
        ],
        key=_canonical_json,
    )
    edges = sorted(
        [
            {
                "edge_id": _string(row.get("edge_id")),
                "source_node_id": _string(row.get("source_node_id")),
                "target_node_id": _string(row.get("target_node_id")),
                "edge_type": _string(row.get("edge_type")),
            }
            for row in _as_rows(payload.get("graph_edges"))
        ],
        key=_canonical_json,
    )
    return {"nodes": nodes, "edges": edges}


def _sqlite_canonical_graph_semantic_payload(
    conn: sqlite3.Connection,
    canonical_payload: Mapping[str, Any],
) -> dict[str, Any] | None:
    if not _table_exists(conn, "graph_nodes", kind="table") or not _table_exists(
        conn, "graph_edges", kind="table"
    ):
        return None
    if not {"node_id", "node_type"}.issubset(_table_columns(conn, "graph_nodes")):
        return None
    if not {"edge_id", "source_node_id", "target_node_id", "edge_type"}.issubset(
        _table_columns(conn, "graph_edges")
    ):
        return None
    canonical_node_ids = {
        _string(row.get("node_id")) for row in _as_rows(canonical_payload.get("graph_nodes"))
    }
    canonical_edge_ids = {
        _string(row.get("edge_id")) for row in _as_rows(canonical_payload.get("graph_edges"))
    }
    nodes = sorted(
        [
            {"node_id": _string(row[0]), "node_type": _string(row[1])}
            for row in conn.execute("SELECT node_id,node_type FROM graph_nodes")
            if _string(row[0]) in canonical_node_ids
        ],
        key=_canonical_json,
    )
    edges = sorted(
        [
            {
                "edge_id": _string(row[0]),
                "source_node_id": _string(row[1]),
                "target_node_id": _string(row[2]),
                "edge_type": _string(row[3]),
            }
            for row in conn.execute("SELECT edge_id,source_node_id,target_node_id,edge_type FROM graph_edges")
            if _string(row[0]) in canonical_edge_ids
        ],
        key=_canonical_json,
    )
    return {"nodes": nodes, "edges": edges}


def _parse_json_list(value: Any) -> list[Any] | None:
    try:
        decoded = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return None
    return decoded if isinstance(decoded, list) else None


def _path_integrity_metric(
    conn: sqlite3.Connection,
    policy: Mapping[str, Any],
    cohort: Mapping[str, Any],
    edges: list[dict[str, str]] | None,
) -> dict[str, Any]:
    metric_id = "path_integrity"
    required = {
        "path_id",
        "start_node_id",
        "end_node_id",
        "path_depth",
        "node_path_json",
        "edge_path_json",
        "edge_types_json",
    }
    if not _table_exists(conn, "graph_paths", kind="table"):
        return _unknown_metric(
            policy,
            metric_id,
            reason="graph_paths_table_missing",
            cohort=cohort,
            denominator_semantics="all generated graph_paths rows",
        )
    if not required.issubset(_table_columns(conn, "graph_paths")) or edges is None:
        return _unknown_metric(
            policy,
            metric_id,
            reason="graph_paths_or_graph_edges_schema_incomplete",
            cohort=cohort,
            denominator_semantics="all generated graph_paths rows",
        )
    rows = conn.execute(
        """
        SELECT path_id,start_node_id,end_node_id,path_depth,
               node_path_json,edge_path_json,edge_types_json
        FROM graph_paths ORDER BY path_id
        """
    ).fetchall()
    edge_map = {row["edge_id"]: row for row in edges}
    expected_direct_paths = {
        (
            edge["source_node_id"],
            edge["target_node_id"],
            edge["edge_id"],
            edge["edge_type"],
        )
        for edge in edges
    }
    valid_direct_counts: Counter[tuple[str, str, str, str]] = Counter()
    failures: list[dict[str, Any]] = []
    for raw in rows:
        path_id, start, end, depth_raw, nodes_raw, edge_ids_raw, edge_types_raw = raw
        nodes = _parse_json_list(nodes_raw)
        edge_ids = _parse_json_list(edge_ids_raw)
        edge_types = _parse_json_list(edge_types_raw)
        reasons: list[str] = []
        depth = depth_raw if isinstance(depth_raw, int) and not isinstance(depth_raw, bool) else -1
        if depth < 1:
            reasons.append("invalid_depth")
        if nodes is None or edge_ids is None or edge_types is None:
            reasons.append("invalid_json_list")
        else:
            if len(nodes) != depth + 1 or len(edge_ids) != depth or len(edge_types) != depth:
                reasons.append("path_length_mismatch")
            if nodes and (_string(nodes[0]) != _string(start) or _string(nodes[-1]) != _string(end)):
                reasons.append("endpoint_mismatch")
            if len(nodes) == depth + 1 and len(edge_ids) == depth and len(edge_types) == depth:
                for index, edge_id in enumerate(edge_ids):
                    edge = edge_map.get(_string(edge_id))
                    if edge is None:
                        reasons.append(f"edge_missing:{edge_id}")
                        continue
                    if (
                        edge["source_node_id"] != _string(nodes[index])
                        or edge["target_node_id"] != _string(nodes[index + 1])
                        or edge["edge_type"] != _string(edge_types[index])
                    ):
                        reasons.append(f"edge_continuity_mismatch:{edge_id}")
        direct_identity: tuple[str, str, str, str] | None = None
        if (
            depth == 1
            and nodes is not None
            and edge_ids is not None
            and edge_types is not None
            and len(nodes) == 2
            and len(edge_ids) == 1
            and len(edge_types) == 1
        ):
            direct_identity = (
                _string(start),
                _string(end),
                _string(edge_ids[0]),
                _string(edge_types[0]),
            )
            if direct_identity not in expected_direct_paths:
                reasons.append("unexpected_direct_path")
        if reasons:
            failures.append({"path_id": _string(path_id), "reasons": sorted(set(reasons))})
        elif direct_identity is not None:
            valid_direct_counts[direct_identity] += 1
    for identity in sorted(expected_direct_paths):
        occurrences = valid_direct_counts[identity]
        if occurrences == 0:
            failures.append(
                {
                    "start_node_id": identity[0],
                    "end_node_id": identity[1],
                    "edge_id": identity[2],
                    "edge_type": identity[3],
                    "reasons": ["expected_direct_path_missing"],
                }
            )
        elif occurrences > 1:
            failures.append(
                {
                    "start_node_id": identity[0],
                    "end_node_id": identity[1],
                    "edge_id": identity[2],
                    "edge_type": identity[3],
                    "occurrences": occurrences,
                    "reasons": ["duplicate_direct_path"],
                }
            )
    valid_expected = sum(1 for identity in expected_direct_paths if valid_direct_counts[identity] == 1)
    return _metric(
        policy,
        metric_id,
        numerator=valid_expected,
        denominator=len(expected_direct_paths),
        numerator_semantics=(
            "graph-derived direct paths materialized exactly once with coherent JSON, "
            "depth, endpoints, and edge continuity"
        ),
        denominator_semantics="all direct paths derived from graph_edges",
        cohort=cohort,
        failure_count=len(failures),
        failure_locators=failures,
        status_override=(str(policy["metrics"][metric_id]["failure_status"]) if failures else None),
        details={
            "expected_direct_path_count": len(expected_direct_paths),
            "materialized_row_count": len(rows),
        },
    )


def _sibling_integrity_metric(
    conn: sqlite3.Connection,
    policy: Mapping[str, Any],
    cohort: Mapping[str, Any],
    edges: list[dict[str, str]] | None,
) -> dict[str, Any]:
    metric_id = "sibling_integrity"
    required = {"node_id", "sibling_node_id", "shared_parent_node_id", "shared_edge_type"}
    if not _table_exists(conn, "graph_sibling_links", kind="table"):
        return _unknown_metric(
            policy,
            metric_id,
            reason="graph_sibling_links_table_missing",
            cohort=cohort,
            denominator_semantics="all generated graph_sibling_links rows",
        )
    if not required.issubset(_table_columns(conn, "graph_sibling_links")) or edges is None:
        return _unknown_metric(
            policy,
            metric_id,
            reason="graph_sibling_links_or_graph_edges_schema_incomplete",
            cohort=cohort,
            denominator_semantics="all generated graph_sibling_links rows",
        )
    if not _table_exists(conn, "graph_nodes", kind="table") or not {
        "node_id",
        "node_type",
    }.issubset(_table_columns(conn, "graph_nodes")):
        return _unknown_metric(
            policy,
            metric_id,
            reason="graph_nodes_schema_incomplete_for_sibling_cohort",
            cohort=cohort,
            denominator_semantics=(
                "all generated graph_sibling_links rows for sanctioned sibling node types"
            ),
        )
    rows = conn.execute(
        """
        SELECT node_id,sibling_node_id,shared_parent_node_id,shared_edge_type
        FROM graph_sibling_links ORDER BY node_id,sibling_node_id
        """
    ).fetchall()
    sibling_node_type_parameters = tuple(sorted(SIBLING_NODE_TYPES))
    sibling_node_type_placeholders = ",".join("?" for _ in sibling_node_type_parameters)
    sibling_node_ids = {
        _string(row[0])
        for row in conn.execute(
            f"SELECT node_id FROM graph_nodes WHERE node_type IN ({sibling_node_type_placeholders})",
            sibling_node_type_parameters,
        )
    }
    children_by_parent: dict[tuple[str, str], set[str]] = defaultdict(set)
    for edge in edges:
        if edge["target_node_id"] in sibling_node_ids:
            children_by_parent[(edge["source_node_id"], edge["edge_type"])].add(edge["target_node_id"])
    expected_siblings = {
        (node_id, sibling_id, parent_id, edge_type)
        for (parent_id, edge_type), children in children_by_parent.items()
        for node_id in children
        for sibling_id in children
        if node_id != sibling_id
    }
    materialized_counts = Counter(
        (
            _string(row[0]),
            _string(row[1]),
            _string(row[2]),
            _string(row[3]),
        )
        for row in rows
    )
    materialized_siblings = set(materialized_counts)
    edge_triples = {(row["source_node_id"], row["target_node_id"], row["edge_type"]) for row in edges}
    valid_expected = 0
    failures: list[dict[str, Any]] = []
    for node, sibling, parent, edge_kind in sorted(materialized_siblings):
        relationship = (node, sibling, parent, edge_kind)
        reasons: list[str] = []
        if not node or not sibling or node == sibling:
            reasons.append("blank_or_self_sibling")
        if (sibling, node, parent, edge_kind) not in materialized_siblings:
            reasons.append("reciprocal_link_missing")
        if (
            not parent
            or (parent, node, edge_kind) not in edge_triples
            or (parent, sibling, edge_kind) not in edge_triples
        ):
            reasons.append("shared_parent_edges_missing")
        if relationship not in expected_siblings:
            reasons.append("unexpected_sibling_row")
        occurrences = materialized_counts[relationship]
        if occurrences > 1:
            reasons.append("duplicate_sibling_row")
        if reasons:
            failure = {
                "node_id": node,
                "sibling_node_id": sibling,
                "shared_parent_node_id": parent,
                "shared_edge_type": edge_kind,
                "reasons": sorted(set(reasons)),
            }
            if occurrences > 1:
                failure["occurrences"] = occurrences
            failures.append(failure)
        else:
            valid_expected += 1
    for node, sibling, parent, edge_kind in sorted(expected_siblings - materialized_siblings):
        failures.append(
            {
                "node_id": node,
                "sibling_node_id": sibling,
                "shared_parent_node_id": parent,
                "shared_edge_type": edge_kind,
                "reasons": ["expected_sibling_missing"],
            }
        )
    return _metric(
        policy,
        metric_id,
        numerator=valid_expected,
        denominator=len(expected_siblings),
        numerator_semantics=(
            "graph-derived sibling relationships materialized exactly once with reciprocal and "
            "shared-parent integrity"
        ),
        denominator_semantics=(
            "all directed sibling relationships derived from shared graph parent edges whose "
            "targets are sanctioned sibling node types"
        ),
        cohort=cohort,
        failure_count=len(failures),
        failure_locators=failures,
        status_override=(str(policy["metrics"][metric_id]["failure_status"]) if failures else None),
        details={
            "expected_relationship_count": len(expected_siblings),
            "materialized_distinct_relationship_count": len(materialized_siblings),
            "materialized_row_count": len(rows),
            "sibling_node_types": sorted(SIBLING_NODE_TYPES),
        },
    )


def _neighborhood_integrity_metric(
    conn: sqlite3.Connection,
    policy: Mapping[str, Any],
    cohort: Mapping[str, Any],
    edges: list[dict[str, str]] | None,
) -> dict[str, Any]:
    metric_id = "neighborhood_integrity"
    required = {
        "center_node_id",
        "neighbor_node_id",
        "distance",
        "connecting_path_json",
        "edge_types_json",
    }
    if not _table_exists(conn, "graph_neighborhoods", kind="table"):
        return _unknown_metric(
            policy,
            metric_id,
            reason="graph_neighborhoods_table_missing",
            cohort=cohort,
            denominator_semantics="all generated graph_neighborhoods rows",
        )
    if not required.issubset(_table_columns(conn, "graph_neighborhoods")) or edges is None:
        return _unknown_metric(
            policy,
            metric_id,
            reason="graph_neighborhoods_or_graph_edges_schema_incomplete",
            cohort=cohort,
            denominator_semantics="all generated graph_neighborhoods rows",
        )
    rows = conn.execute(
        """
        SELECT center_node_id,neighbor_node_id,distance,connecting_path_json,edge_types_json
        FROM graph_neighborhoods ORDER BY center_node_id,neighbor_node_id,distance
        """
    ).fetchall()
    expected_direct_neighborhoods = {(edge["source_node_id"], edge["target_node_id"], 1) for edge in edges}
    expected_direct_neighborhoods.update(
        (edge["target_node_id"], edge["source_node_id"], 1) for edge in edges
    )
    adjacency = {(row["source_node_id"], row["target_node_id"], row["edge_type"]) for row in edges}
    adjacency.update(
        (row["target_node_id"], row["source_node_id"], f"{row['edge_type']}_reverse") for row in edges
    )
    valid_direct_counts: Counter[tuple[str, str, int]] = Counter()
    failures: list[dict[str, Any]] = []
    for center_raw, neighbor_raw, distance_raw, path_raw, edge_types_raw in rows:
        center = _string(center_raw)
        neighbor = _string(neighbor_raw)
        distance = (
            distance_raw if isinstance(distance_raw, int) and not isinstance(distance_raw, bool) else -1
        )
        path = _parse_json_list(path_raw)
        edge_types = _parse_json_list(edge_types_raw)
        reasons: list[str] = []
        if distance < 1:
            reasons.append("invalid_distance")
        if path is None or edge_types is None:
            reasons.append("invalid_json_list")
        else:
            if len(path) != distance + 1 or len(edge_types) != distance:
                reasons.append("distance_path_length_mismatch")
            if path and (_string(path[0]) != center or _string(path[-1]) != neighbor):
                reasons.append("endpoint_mismatch")
            if len(path) == distance + 1 and len(edge_types) == distance:
                for index, edge_type in enumerate(edge_types):
                    if (_string(path[index]), _string(path[index + 1]), _string(edge_type)) not in adjacency:
                        reasons.append(f"edge_continuity_mismatch:{index}")
        direct_identity = (center, neighbor, 1) if distance == 1 else None
        if direct_identity is not None and direct_identity not in expected_direct_neighborhoods:
            reasons.append("unexpected_direct_neighborhood")
        if reasons:
            failures.append(
                {
                    "center_node_id": center,
                    "neighbor_node_id": neighbor,
                    "distance": distance,
                    "reasons": sorted(set(reasons)),
                }
            )
        elif direct_identity is not None:
            valid_direct_counts[direct_identity] += 1
    for center, neighbor, distance in sorted(expected_direct_neighborhoods):
        identity = (center, neighbor, distance)
        occurrences = valid_direct_counts[identity]
        if occurrences == 0:
            failures.append(
                {
                    "center_node_id": center,
                    "neighbor_node_id": neighbor,
                    "distance": distance,
                    "reasons": ["expected_direct_neighborhood_missing"],
                }
            )
        elif occurrences > 1:
            failures.append(
                {
                    "center_node_id": center,
                    "neighbor_node_id": neighbor,
                    "distance": distance,
                    "occurrences": occurrences,
                    "reasons": ["duplicate_direct_neighborhood"],
                }
            )
    valid_expected = sum(
        1 for identity in expected_direct_neighborhoods if valid_direct_counts[identity] == 1
    )
    return _metric(
        policy,
        metric_id,
        numerator=valid_expected,
        denominator=len(expected_direct_neighborhoods),
        numerator_semantics=(
            "graph-derived direct neighborhoods materialized exactly once with coherent distance, "
            "endpoint path, and edge continuity"
        ),
        denominator_semantics="all forward and reverse direct neighborhoods derived from graph edges",
        cohort=cohort,
        failure_count=len(failures),
        failure_locators=failures,
        status_override=(str(policy["metrics"][metric_id]["failure_status"]) if failures else None),
        details={
            "expected_direct_neighborhood_count": len(expected_direct_neighborhoods),
            "materialized_row_count": len(rows),
        },
    )


def _sqlite_metrics(
    conn: sqlite3.Connection,
    policy: Mapping[str, Any],
    *,
    sqlite_digest: str,
    canonical_payload: Mapping[str, Any] | None,
    canonical_payload_digest: str | None,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    metadata = _read_sqlite_metadata(conn)
    cohort = _cohort(
        kind="observed_operational_graph",
        cohort_id=f"sqlite:{sqlite_digest[:16]}",
        digest=sqlite_digest,
        definition=(
            "Rows visible through the locking-aware read-only SQLite projection, "
            "bound separately to its semantic row digest."
        ),
    )
    collector = _MetricCollector(policy, cohort)
    metrics = collector.rows
    summary = (
        metadata.get("graph_count_summary") if isinstance(metadata.get("graph_count_summary"), dict) else {}
    )

    ledger_hash = _string(metadata.get("ledger_hash"))
    canonical_semantic_digest: str | None = None
    projection_semantic_digest: str | None = None
    stored_projection_logical_digest = _string(summary.get("sqlite_graph_digest")).lower()
    stored_projection_schema_digest = _string(summary.get("sqlite_schema_digest")).lower()
    projection_logical_digest: str | None = None
    projection_logical_digest_error: str | None = None
    projection_schema_digest: str | None = None
    projection_schema_digest_error: str | None = None
    try:
        projection_logical_digest = compute_sqlite_graph_digest(conn)
    except (sqlite3.DatabaseError, ValueError) as exc:
        projection_logical_digest_error = str(exc)
    try:
        projection_schema_digest = compute_sqlite_schema_digest(conn)
    except sqlite3.DatabaseError as exc:
        projection_schema_digest_error = str(exc)
    if canonical_payload is not None:
        canonical_semantic_digest = _payload_digest(_canonical_graph_semantic_payload(canonical_payload))
        projected_semantics = _sqlite_canonical_graph_semantic_payload(conn, canonical_payload)
        if projected_semantics is not None:
            projection_semantic_digest = _payload_digest(projected_semantics)
    if canonical_payload_digest is None or canonical_payload is None:
        collector.unknown(
            "canonical_sqlite_digest_match",
            "canonical_payload_or_digest_missing",
            "canonical ledger-hash and semantic-row bindings",
        )
    else:
        ledger_digest_match = int(bool(ledger_hash) and ledger_hash == canonical_payload_digest)
        semantic_digest_match = int(
            projection_semantic_digest is not None and projection_semantic_digest == canonical_semantic_digest
        )
        projection_logical_digest_match = int(
            bool(stored_projection_logical_digest)
            and projection_logical_digest is not None
            and projection_logical_digest == stored_projection_logical_digest
        )
        projection_schema_digest_match = int(
            bool(stored_projection_schema_digest)
            and projection_schema_digest is not None
            and projection_schema_digest == stored_projection_schema_digest
        )
        binding_failures: list[dict[str, Any]] = []
        if not ledger_digest_match:
            binding_failures.append(
                {
                    "binding": "canonical_payload_to_sqlite_ledger_hash",
                    "canonical_payload_sha256": canonical_payload_digest,
                    "sqlite_ledger_sha256": ledger_hash or None,
                }
            )
        if not semantic_digest_match:
            binding_failures.append(
                {
                    "binding": "canonical_projection_semantic_digest",
                    "canonical_graph_semantic_sha256": canonical_semantic_digest,
                    "sqlite_projection_semantic_sha256": projection_semantic_digest,
                }
            )
        if not projection_logical_digest_match:
            binding_failures.append(
                {
                    "binding": "sqlite_projection_logical_digest",
                    "stored_sqlite_graph_sha256": stored_projection_logical_digest or None,
                    "recomputed_sqlite_graph_sha256": projection_logical_digest,
                    "recompute_error": projection_logical_digest_error,
                }
            )
        if not projection_schema_digest_match:
            binding_failures.append(
                {
                    "binding": "sqlite_projection_schema_digest",
                    "stored_sqlite_schema_sha256": stored_projection_schema_digest or None,
                    "recomputed_sqlite_schema_sha256": projection_schema_digest,
                    "recompute_error": projection_schema_digest_error,
                }
            )
        collector.add(
            "canonical_sqlite_digest_match",
            (
                ledger_digest_match
                + semantic_digest_match
                + projection_logical_digest_match
                + projection_schema_digest_match
            ),
            4,
            (
                "matching canonical ledger-hash, canonical-row semantic digest, and SQLite "
                "logical-row and schema-object digest bindings"
            ),
            "four required canonical-to-SQLite authority bindings",
            failure_count=len(binding_failures),
            failure_locators=binding_failures,
        )

    for metric_id, table, summary_key in (
        ("sqlite_projection_node_count_parity", "graph_nodes", "node_count_sqlite"),
        ("sqlite_projection_edge_count_parity", "graph_edges", "edge_count_sqlite"),
    ):
        actual = _table_count(conn, table)
        expected = _valid_count(summary.get(summary_key))
        collector.add(
            metric_id,
            actual if expected is not None else None,
            expected,
            f"observed SQLite {table} row count",
            f"frozen graph_metadata.graph_count_summary.{summary_key}",
            failure_count=abs(actual - expected) if actual is not None and expected is not None else None,
            failure_locators=(
                [{"table": table, "declared": expected, "observed": actual}]
                if actual is not None and expected is not None and actual != expected
                else []
            ),
            unknown_reason=(
                f"{table}_missing_or_{summary_key}_missing_or_invalid"
                if actual is None or expected is None
                else None
            ),
        )

    required_fk_rows = [row for row in policy.get("required_foreign_keys") or [] if isinstance(row, dict)]
    required_signatures = {
        (
            _string(row.get("table")),
            _string(row.get("from")),
            _string(row.get("to_table")),
            _string(row.get("to")),
        )
        for row in required_fk_rows
    }
    try:
        observed_signatures = _foreign_key_signatures(conn, (row[0] for row in required_signatures))
    except ValueError as exc:
        observed_signatures = set()
        invalid_fk_policy = str(exc)
    else:
        invalid_fk_policy = None
    missing_fk = sorted(required_signatures - observed_signatures)
    policy_cohort = _cohort(
        kind="frozen_policy_cohort",
        cohort_id=_string(policy.get("policy_version")),
        digest=_payload_digest(policy),
        definition="Foreign-key contracts frozen in the versioned graph health policy.",
    )
    metrics.append(
        _metric(
            policy,
            "sqlite_foreign_key_coverage",
            numerator=len(required_signatures & observed_signatures) if not invalid_fk_policy else None,
            denominator=len(required_signatures) if not invalid_fk_policy else None,
            numerator_semantics="required policy foreign-key signatures present in SQLite DDL",
            denominator_semantics="all foreign-key signatures frozen in the graph health policy",
            cohort=policy_cohort,
            failure_count=len(missing_fk) if not invalid_fk_policy else None,
            failure_locators=(
                {"table": row[0], "from": row[1], "to_table": row[2], "to": row[3]} for row in missing_fk
            ),
            unknown_reason=invalid_fk_policy,
        )
    )
    if invalid_fk_policy or missing_fk or not required_signatures:
        metrics.append(
            _unknown_metric(
                policy,
                "sqlite_foreign_key_integrity",
                reason=invalid_fk_policy or "required_foreign_keys_not_fully_installed",
                cohort=policy_cohort,
                denominator_semantics="all installed required foreign-key constraints in the frozen policy cohort",
            )
        )
    else:
        fk_violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        metrics.append(
            _metric(
                policy,
                "sqlite_foreign_key_integrity",
                numerator=len(fk_violations),
                denominator=len(required_signatures),
                numerator_semantics="rows returned by SQLite PRAGMA foreign_key_check",
                denominator_semantics="all installed required foreign-key constraints in the frozen policy cohort",
                cohort=policy_cohort,
                failure_count=len(fk_violations),
                failure_locators=(
                    {"table": _string(row[0]), "rowid": row[1], "parent": _string(row[2]), "fkid": row[3]}
                    for row in fk_violations
                ),
            )
        )

    edges = _load_sqlite_edges(conn)
    if (
        edges is None
        or not _table_exists(conn, "graph_nodes", kind="table")
        or not {"node_id", "node_type"}.issubset(_table_columns(conn, "graph_nodes"))
    ):
        metrics.append(
            _unknown_metric(
                policy,
                "sqlite_projected_edge_signature_integrity",
                reason="graph_nodes_or_graph_edges_schema_incomplete_for_typed_signatures",
                cohort=cohort,
                denominator_semantics="all SQLite graph_edges rows",
            )
        )
    else:
        sqlite_signature_report = projected_graph_edge_signature_report(
            node_types_by_id={
                _string(row[0]): _string(row[1])
                for row in conn.execute("SELECT node_id,node_type FROM graph_nodes")
            },
            edge_rows=edges,
        )
        metrics.append(
            _metric(
                policy,
                "sqlite_projected_edge_signature_integrity",
                numerator=sqlite_signature_report["valid_edge_count"],
                denominator=sqlite_signature_report["edge_count"],
                numerator_semantics=(
                    "SQLite edges admitted by a type authority with a valid projected endpoint signature"
                ),
                denominator_semantics="all SQLite graph_edges rows",
                cohort=cohort,
                failure_count=sqlite_signature_report["failure_count"],
                failure_locators=sqlite_signature_report["failure_locators"],
                details=_edge_signature_metric_details(sqlite_signature_report),
            )
        )
    if edges is None or not _table_exists(conn, "graph_edges_reverse", kind="view"):
        metrics.append(
            _unknown_metric(
                policy,
                "reverse_view_parity",
                reason="graph_edges_schema_or_graph_edges_reverse_view_missing",
                cohort=cohort,
                denominator_semantics="all forward and reverse edge rows in the SQLite projection",
            )
        )
    else:
        expected_reverse = Counter(
            (
                edge["edge_id"],
                edge["target_node_id"],
                edge["source_node_id"],
                f"{edge['edge_type']}_reverse",
            )
            for edge in edges
        )
        observed_reverse = Counter(
            tuple(_string(value) for value in row)
            for row in conn.execute(
                "SELECT edge_id,source_node_id,target_node_id,edge_type FROM graph_edges_reverse"
            )
        )
        mismatch_count = sum(
            abs(expected_reverse[row] - observed_reverse[row])
            for row in expected_reverse.keys() | observed_reverse.keys()
        )
        denominator = max(sum(expected_reverse.values()), sum(observed_reverse.values()))
        mismatch_samples = [
            {
                "edge_id": row[0],
                "source_node_id": row[1],
                "target_node_id": row[2],
                "edge_type": row[3],
                "expected_occurrences": expected_reverse[row],
                "observed_occurrences": observed_reverse[row],
            }
            for row in expected_reverse.keys() | observed_reverse.keys()
            if expected_reverse[row] != observed_reverse[row]
        ]
        metrics.append(
            _metric(
                policy,
                "reverse_view_parity",
                numerator=mismatch_count,
                denominator=denominator,
                numerator_semantics="absolute multiset count differences across expected and observed reverse rows",
                denominator_semantics="larger multiset cardinality of expected and observed reverse edge rows",
                cohort=cohort,
                failure_count=mismatch_count,
                failure_locators=mismatch_samples,
            )
        )

    metrics.append(_path_integrity_metric(conn, policy, cohort, edges))
    metrics.append(_sibling_integrity_metric(conn, policy, cohort, edges))
    metrics.append(_neighborhood_integrity_metric(conn, policy, cohort, edges))
    versions = {
        "sqlite_graph_version": metadata.get("graph_version"),
        "sqlite_materializer_version": summary.get("c03_sqlite_materializer_code_version"),
        "sqlite_graph_index_schema_version": summary.get("graph_index_schema_version"),
    }
    digests = {
        "canonical_graph_semantic_sha256": canonical_semantic_digest,
        "sqlite_projection_canonical_semantic_sha256": projection_semantic_digest,
        "sqlite_projection_ledger_sha256": ledger_hash or None,
        "sqlite_projection_logical_stored_sha256": stored_projection_logical_digest or None,
        "sqlite_projection_logical_recomputed_sha256": projection_logical_digest,
        "sqlite_projection_logical_recompute_error": projection_logical_digest_error,
        "sqlite_projection_schema_stored_sha256": stored_projection_schema_digest or None,
        "sqlite_projection_schema_recomputed_sha256": projection_schema_digest,
        "sqlite_projection_schema_recompute_error": projection_schema_digest_error,
    }
    return metrics, versions, digests


def _operational_metrics(
    evidence: Mapping[str, Any] | None,
    policy: Mapping[str, Any],
    *,
    trust_context: OperationalTrustContext | None,
    candidate_commit_sha: str | None,
    canonical_graph_sha256: str | None,
    health_policy_sha256: str,
    health_run_id: str | None,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    unknown_cohort = _cohort(
        kind="frozen_policy_cohort",
        cohort_id="unsupported",
        digest=None,
        definition=("No producer-bound operational authority cohort was independently verified."),
    )
    if evidence is None:
        return (
            [
                _unknown_metric(
                    policy,
                    metric_id,
                    reason="authoritative_operational_evidence_not_supplied",
                    cohort=unknown_cohort,
                    denominator_semantics=(
                        "producer-derived total from an out-of-band pinned operational cohort"
                    ),
                )
                for metric_id in OPERATIONAL_METRIC_IDS
            ],
            {
                "operational_evidence_schema_version": None,
                "operational_producer_registry_version": OPERATIONAL_PRODUCER_REGISTRY_VERSION,
                "operational_trust_context_supplied": False,
            },
            {
                "operational_evidence_sha256": None,
                "operational_evidence_integrity_sha256": None,
            },
        )

    try:
        evidence_digest = _payload_digest(evidence)
    except (TypeError, ValueError, OverflowError, RecursionError):
        return (
            [
                _unknown_metric(
                    policy,
                    metric_id,
                    reason="operational_evidence_not_canonical_json",
                    cohort=unknown_cohort,
                    denominator_semantics=(
                        "producer-derived total from an out-of-band pinned operational cohort"
                    ),
                )
                for metric_id in OPERATIONAL_METRIC_IDS
            ],
            {
                "operational_evidence_schema_version": None,
                "operational_producer_registry_version": OPERATIONAL_PRODUCER_REGISTRY_VERSION,
                "operational_trust_context_supplied": trust_context is not None,
            },
            {
                "operational_evidence_sha256": None,
                "operational_evidence_integrity_sha256": None,
            },
        )
    evidence_schema = _string(evidence.get("schema_version")) or None
    claimed_integrity = _string(evidence.get("integrity_sha256")).lower() or None
    envelope_cohort = _cohort(
        kind="frozen_policy_cohort",
        cohort_id=(
            f"operational-envelope:{_string(evidence.get('envelope_id'))}"
            if _string(evidence.get("envelope_id"))
            else "operational-envelope:unsupported"
        ),
        digest=claimed_integrity,
        definition=(
            "Reference-only operational envelope; authority requires independent trust pins "
            "and a code-owned producer verifier."
        ),
    )

    preflight_reason: str | None = None
    if evidence_schema != OPERATIONAL_EVIDENCE_SCHEMA_VERSION:
        preflight_reason = "legacy_or_unsupported_operational_evidence_schema"
    elif trust_context is None:
        preflight_reason = "operational_trust_context_not_supplied"
    elif candidate_commit_sha != trust_context.expected_candidate_commit_sha:
        preflight_reason = "operational_candidate_commit_binding_mismatch"
    elif canonical_graph_sha256 != trust_context.expected_canonical_graph_sha256:
        preflight_reason = "operational_canonical_graph_binding_mismatch"
    elif health_policy_sha256 != trust_context.expected_health_policy_sha256:
        preflight_reason = "operational_health_policy_binding_mismatch"
    elif health_run_id != trust_context.expected_health_run_id:
        preflight_reason = "operational_health_run_binding_mismatch"

    if preflight_reason is not None:
        return (
            [
                _unknown_metric(
                    policy,
                    metric_id,
                    reason=preflight_reason,
                    cohort=envelope_cohort,
                    denominator_semantics=(
                        "producer-derived total from an out-of-band pinned operational cohort"
                    ),
                )
                for metric_id in OPERATIONAL_METRIC_IDS
            ],
            {
                "operational_evidence_schema_version": evidence_schema,
                "operational_producer_registry_version": OPERATIONAL_PRODUCER_REGISTRY_VERSION,
                "operational_trust_context_supplied": trust_context is not None,
            },
            {
                "operational_evidence_sha256": evidence_digest,
                "operational_evidence_integrity_sha256": claimed_integrity,
            },
        )

    assert trust_context is not None
    verification = verify_operational_evidence_envelope(
        evidence,
        context=trust_context,
    )
    metrics: list[dict[str, Any]] = []
    for result in verification.metrics:
        reasons = result.reason_codes
        if result.status == "SUPPORTED":
            reasons = ("producer_measurement_adapter_not_available",)
        row = _unknown_metric(
            policy,
            result.metric_id,
            reason=";".join(reasons) or "operational_producer_not_authoritative",
            cohort=envelope_cohort,
            denominator_semantics=("producer-derived total from an out-of-band pinned operational cohort"),
        )
        row["details"] = {
            "producer_id": result.producer_id,
            "verified_artifact_sha256s": list(result.verified_artifact_sha256s),
            "envelope_schema_valid": verification.schema_valid,
            "envelope_integrity_valid": verification.integrity_valid,
            "envelope_subject_valid": verification.subject_valid,
        }
        metrics.append(row)
    return (
        metrics,
        {
            "operational_evidence_schema_version": evidence_schema,
            "operational_producer_registry_version": OPERATIONAL_PRODUCER_REGISTRY_VERSION,
            "operational_trust_context_supplied": True,
        },
        {
            "operational_evidence_sha256": evidence_digest,
            "operational_evidence_integrity_sha256": claimed_integrity,
        },
    )


def build_c03_graph_health_receipt(
    *,
    canonical_path: Path | None = None,
    sqlite_path: Path | None = None,
    policy_path: Path | None = None,
    operational_evidence: Mapping[str, Any] | None = None,
    operational_trust_context: OperationalTrustContext | None = None,
    candidate_commit_sha: str | None = None,
    generated_at: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Return a deterministic receipt for fixed inputs without mutating them."""
    root = _repo_root()
    canonical = (canonical_path or (root / DEFAULT_CANONICAL_REL)).resolve()
    sqlite_db = (sqlite_path or (root / DEFAULT_SQLITE_REL)).resolve()
    selected_policy_path = (policy_path or (root / DEFAULT_POLICY_REL)).resolve()
    policy = load_health_policy(selected_policy_path)
    timestamp = generated_at or _utc_now()
    normalized_candidate_commit_sha = _string(candidate_commit_sha).lower() or None
    requested_run_id = run_id or (
        operational_trust_context.expected_health_run_id if operational_trust_context is not None else None
    )

    metrics_by_id: dict[str, dict[str, Any]] = {}
    versions: dict[str, Any] = {
        "builder_version": BUILDER_VERSION,
        "canonical_check_version": CANONICAL_CHECK_VERSION,
        "sqlite_check_version": SQLITE_CHECK_VERSION,
        "policy_version": policy.get("policy_version"),
        "metric_heterogeneity_policy_version": METRIC_HETEROGENEITY_POLICY_VERSION,
        "candidate_commit_sha": normalized_candidate_commit_sha,
    }
    digests: dict[str, Any] = {
        "policy_sha256": _payload_digest(policy),
        "canonical_file_sha256": None,
        "canonical_payload_sha256": None,
        "sqlite_file_sha256_before": None,
        "sqlite_file_sha256_after": None,
        "sqlite_projection_ledger_sha256": None,
    }
    canonical_payload: dict[str, Any] | None = None
    canonical_error: str | None = None
    canonical_digest: str | None = None
    canonical_cohort = _cohort(
        kind="observed_operational_graph",
        cohort_id="canonical:unavailable",
        digest=None,
        definition="Canonical graph input was unavailable or unreadable.",
    )
    if canonical.is_file():
        try:
            digests["canonical_file_sha256"] = _sha256_file(canonical)
        except OSError as exc:
            canonical_error = f"{type(exc).__name__}: {exc}"
        if canonical_error is None:
            canonical_payload, canonical_error = _load_json_object(canonical)
    else:
        canonical_error = "FileNotFoundError: canonical graph artifact missing"
    if canonical_payload is not None:
        canonical_digest = _payload_digest(canonical_payload)
        digests["canonical_payload_sha256"] = canonical_digest
        metadata = (
            canonical_payload.get("metadata") if isinstance(canonical_payload.get("metadata"), dict) else {}
        )
        graph_metadata = (
            canonical_payload.get("graph_metadata")
            if isinstance(canonical_payload.get("graph_metadata"), dict)
            else {}
        )
        overwrite = metadata.get("c03_actual_graph_full_zero_loss_overwrite")
        versions.update(
            {
                "canonical_schema_version": metadata.get("schema_version"),
                "canonical_graph_schema_version": graph_metadata.get("schema_version"),
                "canonical_overwrite_version": overwrite.get("version")
                if isinstance(overwrite, dict)
                else None,
            }
        )
        canonical_cohort = _cohort(
            kind="observed_operational_graph",
            cohort_id=f"canonical:{canonical_digest[:16]}",
            digest=canonical_digest,
            definition="Rows present in the immutable canonical JSON input identified by this digest.",
        )
        for row in _canonical_metrics(canonical_payload, policy, canonical_digest=canonical_digest):
            metrics_by_id[row["metric_id"]] = row
        canonical_available = 1
    else:
        canonical_available = 0
    metrics_by_id["canonical_artifact_available"] = _metric(
        policy,
        "canonical_artifact_available",
        numerator=canonical_available,
        denominator=1,
        numerator_semantics="readable canonical JSON object artifacts",
        denominator_semantics="one required canonical JSON graph artifact",
        cohort=canonical_cohort,
        failure_count=1 - canonical_available,
        failure_locators=([{"path": str(canonical), "error": canonical_error}] if canonical_error else []),
    )

    sqlite_digest_before: str | None = None
    sqlite_digest_after: str | None = None
    sqlite_sidecars_before: tuple[str, ...] = ()
    sqlite_sidecars_after: tuple[str, ...] = ()
    sqlite_error: str | None = None
    sqlite_metrics: list[dict[str, Any]] = []
    if sqlite_db.is_file():
        try:
            sqlite_digest_before = _sha256_file(sqlite_db)
            sqlite_sidecars_before = _sqlite_sidecar_names(sqlite_db)
            digests["sqlite_file_sha256_before"] = sqlite_digest_before
            digests["sqlite_sidecars_before"] = list(sqlite_sidecars_before)
            conn = open_graph_sqlite(db_path=sqlite_db, read_only=True)
            try:
                conn.execute("PRAGMA query_only=ON")
                conn.execute("BEGIN")
                sqlite_metrics, sqlite_versions, sqlite_digests = _sqlite_metrics(
                    conn,
                    policy,
                    sqlite_digest=sqlite_digest_before,
                    canonical_payload=canonical_payload,
                    canonical_payload_digest=canonical_digest,
                )
                versions.update(sqlite_versions)
                digests.update(sqlite_digests)
            finally:
                conn.close()
        except (OSError, sqlite3.Error, TypeError, ValueError) as exc:
            sqlite_error = f"{type(exc).__name__}: {exc}"
        try:
            sqlite_digest_after = _sha256_file(sqlite_db)
            sqlite_sidecars_after = _sqlite_sidecar_names(sqlite_db)
        except OSError as exc:
            sqlite_error = sqlite_error or f"{type(exc).__name__}: {exc}"
    else:
        sqlite_error = "FileNotFoundError: SQLite graph projection missing"
    digests["sqlite_file_sha256_after"] = sqlite_digest_after
    digests["sqlite_sidecars_after"] = list(sqlite_sidecars_after)
    sqlite_readable = int(sqlite_digest_before is not None and sqlite_error is None)
    sqlite_cohort = _cohort(
        kind="observed_operational_graph",
        cohort_id=f"sqlite:{sqlite_digest_before[:16]}" if sqlite_digest_before else "sqlite:unavailable",
        digest=sqlite_digest_before,
        definition="Locking-aware read-only SQLite projection identified by file and semantic digests.",
    )
    metrics_by_id["sqlite_artifact_available"] = _metric(
        policy,
        "sqlite_artifact_available",
        numerator=sqlite_readable,
        denominator=1,
        numerator_semantics="SQLite artifacts opened successfully through locking-aware mode=ro",
        denominator_semantics="one required generated SQLite graph projection",
        cohort=sqlite_cohort,
        failure_count=1 - sqlite_readable,
        failure_locators=([{"path": str(sqlite_db), "error": sqlite_error}] if sqlite_error else []),
    )
    if sqlite_digest_before is None or sqlite_digest_after is None:
        metrics_by_id["sqlite_read_purity"] = _unknown_metric(
            policy,
            "sqlite_read_purity",
            reason="sqlite_before_or_after_digest_unavailable",
            cohort=sqlite_cohort,
            denominator_semantics="one before/after SQLite file digest comparison",
        )
    else:
        unchanged = int(
            sqlite_digest_before == sqlite_digest_after and sqlite_sidecars_before == sqlite_sidecars_after
        )
        metrics_by_id["sqlite_read_purity"] = _metric(
            policy,
            "sqlite_read_purity",
            numerator=unchanged,
            denominator=1,
            numerator_semantics=("unchanged SQLite file SHA-256 and sidecar set after all health queries"),
            denominator_semantics="one before/after SQLite file-and-sidecar comparison",
            cohort=sqlite_cohort,
            failure_count=1 - unchanged,
            failure_locators=(
                [
                    {
                        "before_sha256": sqlite_digest_before,
                        "after_sha256": sqlite_digest_after,
                        "sidecars_before": list(sqlite_sidecars_before),
                        "sidecars_after": list(sqlite_sidecars_after),
                    }
                ]
                if not unchanged
                else []
            ),
        )
    for row in sqlite_metrics:
        metrics_by_id[row["metric_id"]] = row

    operational_metrics, operational_versions, operational_digests = _operational_metrics(
        operational_evidence,
        policy,
        trust_context=operational_trust_context,
        candidate_commit_sha=normalized_candidate_commit_sha,
        canonical_graph_sha256=canonical_digest,
        health_policy_sha256=str(digests["policy_sha256"]),
        health_run_id=requested_run_id,
    )
    versions.update(operational_versions)
    digests.update(operational_digests)
    for row in operational_metrics:
        metrics_by_id[row["metric_id"]] = row

    unavailable_cohort = _cohort(
        kind="observed_operational_graph",
        cohort_id="unavailable",
        digest=None,
        definition="Required authority surface was unavailable for this measurement.",
    )
    for metric_id, spec in policy["metrics"].items():
        if metric_id in metrics_by_id:
            continue
        metrics_by_id[metric_id] = _unknown_metric(
            policy,
            metric_id,
            reason="required_measurement_surface_unavailable",
            cohort=unavailable_cohort,
            denominator_semantics=(
                "required control-plane cohort"
                if spec.get("plane") == "control_plane"
                else "required graph-data cohort"
            ),
        )

    metrics = [metrics_by_id[metric_id] for metric_id in policy["metrics"]]
    control_plane_status = _rollup_metric_statuses(metrics, "control_plane")
    graph_data_readiness = _rollup_metric_statuses(metrics, "graph_data")
    overall_status = _rollup_overall(control_plane_status, graph_data_readiness)
    status_counts = Counter(str(row["status"]) for row in metrics)
    unknown_dimensions = [
        {"metric_id": row["metric_id"], "reason": row.get("unknown_reason")}
        for row in metrics
        if row["status"] == "UNKNOWN"
    ]
    derived_run_id = requested_run_id or (
        "c03-graph-health-"
        + _sha256_bytes(
            _canonical_json(
                {
                    "generated_at": timestamp,
                    "policy": digests["policy_sha256"],
                    "canonical": canonical_digest,
                    "sqlite": sqlite_digest_before,
                    "sqlite_semantic": digests.get("sqlite_projection_semantic_sha256"),
                    "operational": digests.get("operational_evidence_sha256"),
                }
            ).encode("utf-8")
        )[:16]
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": derived_run_id,
        "generated_at": timestamp,
        "versions": versions,
        "artifacts": {
            "canonical_path": str(canonical),
            "sqlite_path": str(sqlite_db),
            "policy_path": str(selected_policy_path),
        },
        "digests": digests,
        "denominator_contract": {
            "frozen_policy_cohort": (
                "Versioned targets, required FK signatures, and independently pinned "
                "producer-bound operational evidence cohorts."
            ),
            "observed_operational_graph": (
                "Canonical and SQLite rows actually present in the supplied file and semantic digests."
            ),
            "zero_denominator_rule": "A missing or zero denominator is UNKNOWN and can never PASS.",
        },
        "metrics": metrics,
        "status_counts": dict(sorted(status_counts.items())),
        "control_plane_status": control_plane_status,
        "graph_data_readiness": graph_data_readiness,
        "overall_status": overall_status,
        "unknown_dimensions": unknown_dimensions,
    }


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    root = _repo_root()
    parser = argparse.ArgumentParser(description="Build a pure C0.3 graph health receipt")
    parser.add_argument("--canonical", type=Path, default=root / DEFAULT_CANONICAL_REL)
    parser.add_argument("--sqlite", type=Path, default=root / DEFAULT_SQLITE_REL)
    parser.add_argument("--policy", type=Path, default=root / DEFAULT_POLICY_REL)
    parser.add_argument("--operational-evidence", type=Path)
    parser.add_argument("--output", type=Path, help="write receipt only when this path is explicit")
    parser.add_argument("--generated-at", help="inject a UTC timestamp for deterministic replay")
    parser.add_argument("--run-id", help="inject a run identifier for deterministic replay")
    parser.add_argument(
        "--candidate-commit-sha",
        help="bind the receipt to an exact candidate commit",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    evidence: dict[str, Any] | None = None
    if args.operational_evidence is not None:
        evidence, error = _load_json_object(args.operational_evidence.resolve())
        if evidence is None:
            evidence = {
                "schema_version": None,
                "_load_error": error,
            }
    receipt = build_c03_graph_health_receipt(
        canonical_path=args.canonical,
        sqlite_path=args.sqlite,
        policy_path=args.policy,
        operational_evidence=evidence,
        candidate_commit_sha=args.candidate_commit_sha,
        generated_at=args.generated_at,
        run_id=args.run_id,
    )
    rendered = json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output is not None:
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if receipt["overall_status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "BUILDER_VERSION",
    "SCHEMA_VERSION",
    "build_c03_graph_health_receipt",
    "default_policy_path",
    "load_health_policy",
    "main",
]
