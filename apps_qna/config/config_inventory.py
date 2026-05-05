"""SSOT config inventory and drift detection — D4.1.

Catalogs all apps_qna domain-contract YAML files, parses canonical header
fields (app_id, version, policy_hash, created_at, status), and detects
drift across contracts (mismatched policy_hash or version within the same
app_id / task_class pair).

This module is purely analytical — no mutations, no I/O side-effects beyond
reading YAML from disk. It is the machine-readable foundation for any future
SSOT-enforcement gate.

Plan: .windsurf/plans/apps-qna-spine-deferred-e9c5b3.md D4.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


_DOMAIN_CONTRACT_DIR = Path(__file__).parent / "domain_contract"

_CANONICAL_FIELDS = (
    "app_id",
    "task_class",
    "version",
    "status",
    "policy_hash",
    "created_at",
)


@dataclass(frozen=True)
class ConfigEntry:
    """One top-level record parsed from a domain-contract YAML.

    Attributes:
        filename: YAML filename (relative to domain_contract/).
        record_id: The primary id field (e.g. eval_rubric_id, grader_roster_id).
        app_id: Owning app.
        task_class: Task class this config applies to.
        version: Semver string.
        status: active / draft / retired.
        policy_hash: Policy hash referenced by this config.
        created_at: ISO date string.
        extra_keys: Any additional top-level keys found in the record.
    """

    filename: str = ""
    record_id: str = ""
    app_id: str = ""
    task_class: str = ""
    version: str = ""
    status: str = ""
    policy_hash: str = ""
    created_at: str = ""
    extra_keys: tuple[str, ...] = ()


@dataclass(frozen=True)
class DriftViolation:
    """A detected drift between two config entries.

    Attributes:
        field: The field that differs.
        file_a: First file contributing the value.
        file_b: Second file contributing the value.
        value_a: Value from file_a.
        value_b: Value from file_b.
    """

    field: str
    file_a: str
    file_b: str
    value_a: str
    value_b: str


@dataclass(frozen=True)
class ConfigInventoryReport:
    """Result of a full config inventory scan.

    Attributes:
        entries: All parsed ConfigEntry records.
        drift_violations: Detected drift between records in the same task_class group.
        files_scanned: Number of YAML files examined.
        records_parsed: Total number of top-level YAML records parsed.
        missing_fields: Mapping of filename → list of missing canonical fields.
        aligned: True when no drift_violations and no missing_fields.
    """

    entries: tuple[ConfigEntry, ...] = ()
    drift_violations: tuple[DriftViolation, ...] = ()
    files_scanned: int = 0
    records_parsed: int = 0
    missing_fields: dict[str, list[str]] = field(default_factory=dict)
    aligned: bool = False


def _load_yaml_records(path: Path) -> list[dict[str, Any]]:
    """Load top-level YAML records from a file. Returns [] on failure."""
    try:
        import yaml  # type: ignore[import]
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, list):
            return [r for r in data if isinstance(r, dict)]
        if isinstance(data, dict):
            return [data]
        return []
    except Exception:
        return []


def _primary_id(record: dict[str, Any]) -> str:
    """Extract the primary ID field from a record."""
    for key in (
        "eval_rubric_id",
        "grader_roster_id",
        "prompt_profile_id",
        "cache_profile_id",
        "capability_profile_id",
        "learning_profile_id",
        "orchestration_profile_id",
        "repair_profile_id",
        "retrieval_profile_id",
        "route_profile_id",
        "task_class_id",
        "threshold_profile_id",
        "output_schema_id",
        "app_domain_manifest_id",
        "input_contract_id",
        "negative_control_id",
        "fixture_id",
    ):
        if key in record:
            return str(record[key])
    for key in record:
        if key.endswith("_id"):
            return str(record[key])
    return ""


def _parse_entry(filename: str, record: dict[str, Any]) -> ConfigEntry:
    known_keys = set(_CANONICAL_FIELDS) | {"score_dimensions", "deterministic_graders",
                                             "llm_judge_graders", "ensemble_or_consensus_graders",
                                             "calibration_refs", "source_app_config_ref"}
    extra = tuple(k for k in record if k not in known_keys and not k.endswith("_id"))
    return ConfigEntry(
        filename=filename,
        record_id=_primary_id(record),
        app_id=str(record.get("app_id", "")),
        task_class=str(record.get("task_class", "")),
        version=str(record.get("version", "")),
        status=str(record.get("status", "")),
        policy_hash=str(record.get("policy_hash", "")),
        created_at=str(record.get("created_at", "")),
        extra_keys=extra,
    )


def _check_missing(filename: str, record: dict[str, Any]) -> list[str]:
    return [f for f in _CANONICAL_FIELDS if not record.get(f)]


def scan_config_inventory(
    domain_contract_dir: Path | None = None,
) -> ConfigInventoryReport:
    """Scan all YAML files in domain_contract/ and build a ConfigInventoryReport.

    Args:
        domain_contract_dir: Override for the canonical domain_contract path.

    Returns:
        ConfigInventoryReport with all entries, drift violations, and missing fields.
    """
    target_dir = domain_contract_dir or _DOMAIN_CONTRACT_DIR
    yaml_files = sorted(target_dir.glob("*.yaml"))

    all_entries: list[ConfigEntry] = []
    missing_fields: dict[str, list[str]] = {}
    files_scanned = 0
    records_parsed = 0

    for yaml_path in yaml_files:
        filename = yaml_path.name
        records = _load_yaml_records(yaml_path)
        files_scanned += 1
        for record in records:
            records_parsed += 1
            entry = _parse_entry(filename, record)
            all_entries.append(entry)
            missing = _check_missing(filename, record)
            if missing:
                existing = missing_fields.get(filename, [])
                missing_fields[filename] = list(set(existing + missing))

    drift_violations = _detect_drift(all_entries)
    aligned = not drift_violations and not any(
        v for v in missing_fields.values()
        if any(f in ("app_id", "version", "policy_hash") for f in v)
    )

    return ConfigInventoryReport(
        entries=tuple(all_entries),
        drift_violations=tuple(drift_violations),
        files_scanned=files_scanned,
        records_parsed=records_parsed,
        missing_fields=missing_fields,
        aligned=aligned,
    )


def _detect_drift(entries: list[ConfigEntry]) -> list[DriftViolation]:
    """Detect policy_hash or version mismatches within the same (app_id, task_class) group."""
    from collections import defaultdict

    groups: dict[tuple[str, str], list[ConfigEntry]] = defaultdict(list)
    for entry in entries:
        key = (entry.app_id, entry.task_class)
        if entry.app_id and entry.task_class:
            groups[key].append(entry)

    violations: list[DriftViolation] = []
    drift_fields = ("policy_hash", "version")
    for (app_id, task_class), group_entries in groups.items():
        for drift_field in drift_fields:
            values = {getattr(e, drift_field) for e in group_entries if getattr(e, drift_field)}
            if len(values) > 1:
                sorted_entries = sorted(group_entries, key=lambda e: e.filename)
                for i in range(len(sorted_entries) - 1):
                    va = getattr(sorted_entries[i], drift_field)
                    vb = getattr(sorted_entries[i + 1], drift_field)
                    if va and vb and va != vb:
                        violations.append(DriftViolation(
                            field=drift_field,
                            file_a=sorted_entries[i].filename,
                            file_b=sorted_entries[i + 1].filename,
                            value_a=va,
                            value_b=vb,
                        ))
    return violations


def get_policy_hashes(report: ConfigInventoryReport) -> dict[str, set[str]]:
    """Return mapping of filename → set of policy_hash values seen in that file."""
    result: dict[str, set[str]] = {}
    for entry in report.entries:
        if entry.policy_hash:
            result.setdefault(entry.filename, set()).add(entry.policy_hash)
    return result


__all__ = [
    "ConfigEntry",
    "ConfigInventoryReport",
    "DriftViolation",
    "get_policy_hashes",
    "scan_config_inventory",
]
