"""Versioned contract registry for ADG repository-health metrics.

The registry is declarative and read-only.  This module validates contract
completeness and naming but does not calculate metrics or create a competing
source of graph truth.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

DEFAULT_METRIC_REGISTRY = Path(__file__).with_name("metric_registry.json")

_METRIC_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:\.[A-Z0-9][A-Z0-9_]*){2,}$")
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
_SQL_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_MUTATING_SQL_RE = re.compile(
    r"\b(?:ALTER|ATTACH|CREATE|DELETE|DETACH|DROP|INSERT|PRAGMA|REINDEX|REPLACE|UPDATE|VACUUM)\b",
    re.IGNORECASE,
)

_EXACTNESS = frozenset({"exact", "approximate", "mixed", "statistical"})
_HEALTH_DIMENSIONS = frozenset(
    {
        "architecture",
        "change_risk",
        "dependency_risk",
        "extraction_trust",
        "graph_integrity",
        "operational_health",
        "ownership",
        "runtime_witness",
        "security_governance",
        "temporal",
        "test_eval_coverage",
    }
)

_REQUIRED_FIELDS = frozenset(
    {
        "metric_id",
        "version",
        "name",
        "health_dimension",
        "decision",
        "definition",
        "formula",
        "source_table",
        "value_columns",
        "key_columns",
        "population",
        "exclusions",
        "unit",
        "normalization",
        "exactness",
        "confidence_derivation",
        "baseline_strategy",
        "threshold_strategy",
        "severity_mapping",
        "minimum_sample_size",
        "limitations",
        "evidence_query",
        "consumers",
        "refresh_cadence",
        "validation",
        "remediation",
    }
)


class MetricRegistryError(ValueError):
    """Raised when the ADG metric registry is malformed or incomplete."""


@dataclass(frozen=True)
class MetricContract:
    metric_id: str
    version: str
    name: str
    health_dimension: str
    decision: str
    definition: str
    formula: str
    source_table: str
    value_columns: tuple[str, ...]
    key_columns: tuple[str, ...]
    population: str
    exclusions: tuple[str, ...]
    unit: str
    normalization: str
    exactness: str
    confidence_derivation: str
    baseline_strategy: str
    threshold_strategy: str
    severity_mapping: str
    minimum_sample_size: int
    limitations: tuple[str, ...]
    evidence_query: str
    consumers: tuple[str, ...]
    refresh_cadence: str
    validation: str
    remediation: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "MetricContract":
        return cls(
            metric_id=str(value["metric_id"]),
            version=str(value["version"]),
            name=str(value["name"]),
            health_dimension=str(value["health_dimension"]),
            decision=str(value["decision"]),
            definition=str(value["definition"]),
            formula=str(value["formula"]),
            source_table=str(value["source_table"]),
            value_columns=tuple(str(item) for item in value["value_columns"]),
            key_columns=tuple(str(item) for item in value["key_columns"]),
            population=str(value["population"]),
            exclusions=tuple(str(item) for item in value["exclusions"]),
            unit=str(value["unit"]),
            normalization=str(value["normalization"]),
            exactness=str(value["exactness"]),
            confidence_derivation=str(value["confidence_derivation"]),
            baseline_strategy=str(value["baseline_strategy"]),
            threshold_strategy=str(value["threshold_strategy"]),
            severity_mapping=str(value["severity_mapping"]),
            minimum_sample_size=int(value["minimum_sample_size"]),
            limitations=tuple(str(item) for item in value["limitations"]),
            evidence_query=str(value["evidence_query"]),
            consumers=tuple(str(item) for item in value["consumers"]),
            refresh_cadence=str(value["refresh_cadence"]),
            validation=str(value["validation"]),
            remediation=str(value["remediation"]),
        )


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_string_list(
    metric: Mapping[str, Any],
    field: str,
    *,
    allow_empty: bool,
    index: int,
) -> list[str]:
    errors: list[str] = []
    value = metric.get(field)
    if not isinstance(value, list):
        return [f"metrics[{index}].{field} must be a list"]
    if not allow_empty and not value:
        errors.append(f"metrics[{index}].{field} must not be empty")
    if any(not _non_empty_string(item) for item in value):
        errors.append(f"metrics[{index}].{field} must contain only non-empty strings")
    if len(value) != len(set(value)):
        errors.append(f"metrics[{index}].{field} must not contain duplicates")
    return errors


def validate_registry_document(document: Any) -> tuple[str, ...]:
    """Return deterministic validation errors; an empty tuple means valid."""
    if not isinstance(document, dict):
        return ("registry document must be an object",)

    errors: list[str] = []
    registry_version = document.get("registry_version")
    if not _non_empty_string(registry_version) or not _SEMVER_RE.fullmatch(registry_version):
        errors.append("registry_version must be semantic version X.Y.Z")

    metrics = document.get("metrics")
    if not isinstance(metrics, list) or not metrics:
        errors.append("metrics must be a non-empty list")
        return tuple(errors)

    seen_metric_ids: set[str] = set()
    for index, metric in enumerate(metrics):
        prefix = f"metrics[{index}]"
        if not isinstance(metric, dict):
            errors.append(f"{prefix} must be an object")
            continue

        missing = sorted(_REQUIRED_FIELDS - metric.keys())
        unknown = sorted(metric.keys() - _REQUIRED_FIELDS)
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
        if unknown:
            errors.append(f"{prefix} unknown fields: {', '.join(unknown)}")
        if missing:
            continue

        metric_id = metric["metric_id"]
        if not _non_empty_string(metric_id) or not _METRIC_ID_RE.fullmatch(metric_id):
            errors.append(f"{prefix}.metric_id has invalid stable-ID format")
        elif metric_id in seen_metric_ids:
            errors.append(f"{prefix}.metric_id duplicates {metric_id}")
        else:
            seen_metric_ids.add(metric_id)

        version = metric["version"]
        if not _non_empty_string(version) or not _SEMVER_RE.fullmatch(version):
            errors.append(f"{prefix}.version must be semantic version X.Y.Z")

        for field in sorted(
            _REQUIRED_FIELDS
            - {
                "value_columns",
                "key_columns",
                "exclusions",
                "limitations",
                "consumers",
                "minimum_sample_size",
            }
        ):
            if not _non_empty_string(metric[field]):
                errors.append(f"{prefix}.{field} must be a non-empty string")

        health_dimension = metric["health_dimension"]
        if not isinstance(health_dimension, str) or health_dimension not in _HEALTH_DIMENSIONS:
            errors.append(f"{prefix}.health_dimension is not registered")
        exactness = metric["exactness"]
        if not isinstance(exactness, str) or exactness not in _EXACTNESS:
            errors.append(f"{prefix}.exactness must be one of {sorted(_EXACTNESS)}")
        source_table = metric["source_table"]
        if not isinstance(source_table, str) or not _SQL_IDENTIFIER_RE.fullmatch(source_table):
            errors.append(f"{prefix}.source_table must be a SQLite identifier")

        for field, allow_empty in (
            ("value_columns", False),
            ("key_columns", False),
            ("exclusions", True),
            ("limitations", True),
            ("consumers", False),
        ):
            errors.extend(
                _validate_string_list(metric, field, allow_empty=allow_empty, index=index)
            )

        for field in ("value_columns", "key_columns"):
            value = metric[field]
            if isinstance(value, list):
                for column in value:
                    if _non_empty_string(column) and not _SQL_IDENTIFIER_RE.fullmatch(column):
                        errors.append(f"{prefix}.{field} contains invalid SQLite identifier {column!r}")

        minimum_sample_size = metric["minimum_sample_size"]
        if (
            isinstance(minimum_sample_size, bool)
            or not isinstance(minimum_sample_size, int)
            or minimum_sample_size < 0
        ):
            errors.append(f"{prefix}.minimum_sample_size must be an integer >= 0")

        raw_evidence_query = metric["evidence_query"]
        if isinstance(raw_evidence_query, str):
            evidence_query = raw_evidence_query.strip()
            if not evidence_query.upper().startswith(("SELECT ", "WITH ")):
                errors.append(f"{prefix}.evidence_query must be read-only SELECT SQL")
            if ";" in evidence_query.rstrip(";") or _MUTATING_SQL_RE.search(evidence_query):
                errors.append(f"{prefix}.evidence_query contains non-read-only SQL")

    return tuple(errors)


def load_metric_registry(path: Path = DEFAULT_METRIC_REGISTRY) -> tuple[MetricContract, ...]:
    """Load and validate the registry, raising ``MetricRegistryError`` on drift."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MetricRegistryError(f"invalid registry JSON: {exc}") from exc

    errors = validate_registry_document(document)
    if errors:
        raise MetricRegistryError("\n".join(errors))
    return tuple(MetricContract.from_mapping(metric) for metric in document["metrics"])
