"""
Guardian Contract — Canonical Schema for All Guardian Results.

SSOT for structured Guardian output consumed by:
- Guardian scripts (L0_maintenance/scripts/)
- Guardian agents (L5_safety/reasoning/*Guardian*.py)
- Guardian tests (tests/guardian/)
- L6 observability ingestion

Every Guardian MUST emit results conforming to this schema.
No ad-hoc keys. No absolute paths. POSIX-normalized repo-relative paths only.

Contract version is an integer that increments on breaking changes.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Any

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class GuardianStatus(str, Enum):
    """Top-level guardian result status."""

    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"


class CheckStatus(str, Enum):
    """Per-check status."""

    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"


class ArtifactType(str, Enum):
    """Types of artifacts a guardian may emit."""

    DIFF = "diff"
    JSON = "json"
    LOG = "log"
    SNAPSHOT = "snapshot"


# ---------------------------------------------------------------------------
# Contract version
# ---------------------------------------------------------------------------

CONTRACT_VERSION: int = 1

# Frozen schema shape: top-level keys → expected types.
# Any change to this set is a BREAKING change requiring CONTRACT_VERSION bump.
CONTRACT_SCHEMA_SNAPSHOT: dict[str, str] = {
    "guardian_id": "str",
    "version": "int",
    "status": "str",
    "summary": "str",
    "checks": "list[dict]",
    "artifacts": "list[dict]",
    "metrics": "dict",
    "remediation_hints": "list[str]",
    "timestamp": "str|None",
    "correlation_id": "str|None",
    "index": "dict",
    "artifact_class": "str",
}

# Frozen check-level keys
CHECK_SCHEMA_KEYS: frozenset[str] = frozenset({"check_id", "status", "details", "evidence"})

# Frozen artifact-level keys
ARTIFACT_SCHEMA_KEYS: frozenset[str] = frozenset({"type", "path", "description"})

# ---------------------------------------------------------------------------
# JSON Schema Snapshot (Phase 2: Schema-level compatibility)
# ---------------------------------------------------------------------------

CONTRACT_JSON_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "GuardianResult",
    "type": "object",
    "required": [
        "guardian_id",
        "version",
        "status",
        "summary",
        "checks",
        "artifacts",
        "metrics",
        "remediation_hints",
    ],
    "additionalProperties": False,
    "properties": {
        "guardian_id": {"type": "string", "minLength": 1},
        "version": {"type": "integer", "minimum": 1},
        "status": {"type": "string", "enum": ["PASS", "FAIL", "ERROR"]},
        "summary": {"type": "string"},
        "checks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["check_id", "status", "details", "evidence"],
                "additionalProperties": False,
                "properties": {
                    "check_id": {"type": "string", "minLength": 1},
                    "status": {"type": "string", "enum": ["PASS", "FAIL", "SKIP"]},
                    "details": {"type": "string"},
                    "evidence": {
                        "type": "object",
                        "maxProperties": 30,
                    },
                },
            },
        },
        "artifacts": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type", "path", "description"],
                "additionalProperties": False,
                "properties": {
                    "type": {"type": "string", "enum": ["diff", "json", "log", "snapshot"]},
                    "path": {
                        "type": "string",
                        "pattern": "^[^\\\\]+$",  # No backslashes (POSIX only)
                        "not": {"pattern": "^/"},  # No leading slash (repo-relative)
                    },
                    "description": {"type": "string"},
                },
            },
        },
        "metrics": {
            "type": "object",
            "maxProperties": 50,
            "additionalProperties": {
                "anyOf": [
                    {"type": "integer"},
                    {"type": "number"},
                    {"type": "string", "maxLength": 500},
                    {"type": "boolean"},
                    {"type": "array"},
                    {"type": "object"},
                ],
            },
        },
        "remediation_hints": {"type": "array", "items": {"type": "string"}},
        "timestamp": {"type": ["string", "null"]},
        "correlation_id": {"type": ["string", "null"]},
        "index": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["status", "artifacts"],
                "additionalProperties": False,
                "properties": {
                    "status": {"type": "string", "enum": ["PASS", "FAIL", "ERROR"]},
                    "artifacts": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
        "artifact_class": {
            "type": "string",
            "enum": ["individual", "aggregate"],
        },
    },
}

# Frozen enum values — any change requires version bump
GUARDIAN_STATUS_VALUES: frozenset[str] = frozenset({"PASS", "FAIL", "ERROR"})
CHECK_STATUS_VALUES: frozenset[str] = frozenset({"PASS", "FAIL", "SKIP"})
ARTIFACT_TYPE_VALUES: frozenset[str] = frozenset({"diff", "json", "log", "snapshot"})

# Aggregate guardian identity (used by run_all_guardians aggregator)
AGGREGATE_GUARDIAN_ID: str = "combined"

# L6 ingestion contract constants
GUARDIAN_ARTIFACT_DIR: str = "docs/reports/verification/guardian"

# Artifact filename patterns (Phase 4: Individual vs Aggregate)
# Individual: per-guardian results
INDIVIDUAL_ARTIFACT_PATTERN: str = "guardian_{guardian_id}_{correlation_id}.json"
INDIVIDUAL_ARTIFACT_PATTERN_NO_CORR: str = "guardian_{guardian_id}_result.json"
# Aggregate: combined results from aggregator
AGGREGATE_ARTIFACT_PATTERN: str = "combined_guardian_{correlation_id}.json"
AGGREGATE_ARTIFACT_PATTERN_NO_CORR: str = "combined_guardian_result.json"

# Deprecated: use INDIVIDUAL_ARTIFACT_PATTERN instead
GUARDIAN_ARTIFACT_PATTERN: str = "guardian_{guardian_id}.json"


class ArtifactClass(str, Enum):
    """Classification of guardian artifacts."""

    INDIVIDUAL = "individual"  # Per-guardian result
    AGGREGATE = "aggregate"  # Combined aggregator result


def get_artifact_filename(
    guardian_id: str | None,
    correlation_id: str | None = None,
    artifact_class: ArtifactClass = ArtifactClass.INDIVIDUAL,
) -> str:
    """
    Generate the correct artifact filename based on class and correlation.

    Args:
        guardian_id: The guardian_id (required for INDIVIDUAL, ignored for AGGREGATE).
        correlation_id: Optional correlation ID for tracking.
        artifact_class: INDIVIDUAL or AGGREGATE.

    Returns:
        Filename matching the L6 contract pattern.
    """
    if artifact_class == ArtifactClass.AGGREGATE:
        if correlation_id:
            return AGGREGATE_ARTIFACT_PATTERN.format(correlation_id=correlation_id)
        return AGGREGATE_ARTIFACT_PATTERN_NO_CORR
    else:
        if not guardian_id:
            raise ValueError("guardian_id required for INDIVIDUAL artifacts")
        if correlation_id:
            return INDIVIDUAL_ARTIFACT_PATTERN.format(
                guardian_id=guardian_id,
                correlation_id=correlation_id,
            )
        return INDIVIDUAL_ARTIFACT_PATTERN_NO_CORR.format(guardian_id=guardian_id)


# Payload size bounds (Phase 2b: schema bounds enforcement)
MAX_METRICS_PROPERTIES: int = 50
MAX_EVIDENCE_PROPERTIES: int = 30
MAX_EVIDENCE_DEPTH: int = 3  # Nesting depth for evidence values
MAX_PAYLOAD_BYTES: int = 512 * 1024  # 512 KB total serialized payload
MAX_STRING_VALUE_LENGTH: int = 500  # Max length for string values in metrics

# Performance ceilings (Phase 5: Algorithmic caps enforced in-code)
MAX_GUARDIAN_RUNTIME_MS: int = 30_000
MAX_ARTIFACT_SIZE_KB: int = 512
MAX_SCAN_DEPTH: int = 10

# Scan bounds (enforced by guardians, not just tests)
MAX_FILES_PER_SCAN: int = 10_000  # Hard limit on file count per guardian scan
MAX_FOLDER_DEPTH: int = 10  # Maximum folder depth to traverse
IGNORE_PATTERNS: frozenset[str] = frozenset(
    {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".nox",
        "node_modules",
        ".venv",
        "venv",
    },
)


class ScanBudgetExceeded:
    """
    Sentinel returned by scan functions when a budget cap is breached.

    Carries which cap was exceeded, the limit value, and remediation hints
    so callers can emit a schema-locked FAIL (not ERROR/exception).

    Lives in SSOT types so all scanning guardians share the same pattern.
    """

    def __init__(self, cap_name: str, limit: int, scanned: int) -> None:
        self.cap_name = cap_name
        self.limit = limit
        self.scanned = scanned

    @property
    def details(self) -> str:
        return (
            f"Scan exceeded {self.cap_name} ({self.limit}). "
            f"Scanned {self.scanned} items before hitting the cap."
        )

    @property
    def remediation_hints(self) -> list[str]:
        return [
            "Tighten IGNORE_PATTERNS to exclude noisy directories",
            "Run in scoped mode with a smaller allowed_roots set",
            f"If justified, raise {self.cap_name} in guardian_contract.py with a code review",
        ]


def guard_scan_budget(
    file_count: int,
    cap_name: str = "MAX_FILES_PER_SCAN",
    limit: int | None = None,
) -> ScanBudgetExceeded | None:
    """
    Check whether a running file count exceeds a scan budget cap.

    Returns ScanBudgetExceeded sentinel if cap is breached, None otherwise.
    All scanning guardians MUST use this helper instead of raising RuntimeError.

    Args:
        file_count: Current count of files scanned.
        cap_name: Name of the cap constant (for diagnostics).
        limit: Override limit; defaults to MAX_FILES_PER_SCAN.

    Returns:
        ScanBudgetExceeded if breached, None if within budget.
    """
    if limit is None:
        limit = MAX_FILES_PER_SCAN
    if file_count > limit:
        return ScanBudgetExceeded(cap_name=cap_name, limit=limit, scanned=file_count)
    return None


def check_schema_compatibility(result_dict: dict[str, Any]) -> list[str]:
    """
    Verify a serialized result dict has exactly the expected top-level keys.
    Returns list of incompatibility messages (empty = compatible).
    """
    errors: list[str] = []
    expected_keys = set(CONTRACT_SCHEMA_SNAPSHOT.keys())
    actual_keys = set(result_dict.keys())
    missing = expected_keys - actual_keys - {"timestamp", "correlation_id", "index"}  # optional
    extra = actual_keys - expected_keys
    if missing:
        errors.append(f"Missing required keys: {sorted(missing)}")
    if extra:
        errors.append(f"Unexpected keys (schema drift): {sorted(extra)}")
    for check in result_dict.get("checks", []):
        check_keys = set(check.keys())
        if check_keys != CHECK_SCHEMA_KEYS:
            errors.append(
                f"Check keys mismatch: expected {sorted(CHECK_SCHEMA_KEYS)}, got {sorted(check_keys)}",
            )
    for artifact in result_dict.get("artifacts", []):
        artifact_keys = set(artifact.keys())
        if artifact_keys != ARTIFACT_SCHEMA_KEYS:
            errors.append(
                f"Artifact keys mismatch: expected {sorted(ARTIFACT_SCHEMA_KEYS)}, got {sorted(artifact_keys)}",
            )
    return errors


def validate_against_json_schema(result_dict: dict[str, Any]) -> list[str]:
    """
    Deep validation of result_dict against CONTRACT_JSON_SCHEMA.
    Returns list of validation errors (empty = valid).

    This is a lightweight validator that does NOT require jsonschema library.
    It validates: required fields, type constraints, enum values, additionalProperties.
    """
    errors: list[str] = []
    schema = CONTRACT_JSON_SCHEMA

    def _validate_type(value: Any, type_spec: Any, path: str) -> None:
        if isinstance(type_spec, list):
            # Union type like ["string", "null"]
            if value is None and "null" in type_spec:
                return
            for t in type_spec:
                if t == "null":
                    continue
                if t == "string" and isinstance(value, str):
                    return
                if t == "integer" and isinstance(value, int) and not isinstance(value, bool):
                    return
                if t == "object" and isinstance(value, dict):
                    return
                if t == "array" and isinstance(value, list):
                    return
            errors.append(f"{path}: expected one of {type_spec}, got {type(value).__name__}")
        elif type_spec == "string":
            if not isinstance(value, str):
                errors.append(f"{path}: expected string, got {type(value).__name__}")
        elif type_spec == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append(f"{path}: expected integer, got {type(value).__name__}")
        elif type_spec == "object":
            if not isinstance(value, dict):
                errors.append(f"{path}: expected object, got {type(value).__name__}")
        elif type_spec == "array":
            if not isinstance(value, list):
                errors.append(f"{path}: expected array, got {type(value).__name__}")

    def _validate_enum(value: Any, enum_values: list[str], path: str) -> None:
        if value not in enum_values:
            errors.append(f"{path}: value '{value}' not in enum {enum_values}")

    def _validate_pattern(value: str, pattern: str, path: str) -> None:
        """Validate string against regex pattern."""
        import re

        if not re.search(pattern, value):
            errors.append(f"{path}: value '{value}' does not match pattern '{pattern}'")

    def _validate_not_pattern(value: str, pattern: str, path: str) -> None:
        """Validate string does NOT match regex pattern."""
        import re

        if re.search(pattern, value):
            errors.append(f"{path}: value '{value}' must not match pattern '{pattern}'")

    def _validate_object(obj: dict, obj_schema: dict, path: str) -> None:
        props = obj_schema.get("properties", {})
        required = set(obj_schema.get("required", []))
        additional = obj_schema.get("additionalProperties", True)

        # Check required fields
        for req in required:
            if req not in obj:
                errors.append(f"{path}: missing required field '{req}'")

        # Check maxProperties
        max_props = obj_schema.get("maxProperties")
        if max_props is not None and len(obj) > max_props:
            errors.append(
                f"{path}: object has {len(obj)} properties, exceeds maxProperties ({max_props})",
            )

        # Check for extra fields if additionalProperties=False
        if additional is False:
            extra = set(obj.keys()) - set(props.keys())
            for e in extra:
                errors.append(f"{path}: unexpected field '{e}'")

        # Validate each field
        for key, val in obj.items():
            if key in props:
                prop_schema = props[key]
                field_path = f"{path}.{key}"
                if "type" in prop_schema:
                    _validate_type(val, prop_schema["type"], field_path)
                if "enum" in prop_schema and val is not None:
                    _validate_enum(val, prop_schema["enum"], field_path)
                # Pattern validation for strings
                if "pattern" in prop_schema and isinstance(val, str):
                    _validate_pattern(val, prop_schema["pattern"], field_path)
                # Not pattern validation for strings
                if "not" in prop_schema and isinstance(val, str):
                    not_schema = prop_schema["not"]
                    if "pattern" in not_schema:
                        _validate_not_pattern(val, not_schema["pattern"], field_path)
                # Recurse into nested objects (for maxProperties, etc.)
                if prop_schema.get("type") == "object" and isinstance(val, dict):
                    _validate_object(val, prop_schema, field_path)
                if prop_schema.get("type") == "array" and isinstance(val, list):
                    item_schema = prop_schema.get("items", {})
                    for i, item in enumerate(val):
                        if item_schema.get("type") == "object":
                            _validate_object(item, item_schema, f"{field_path}[{i}]")
                        elif "type" in item_schema:
                            _validate_type(item, item_schema["type"], f"{field_path}[{i}]")
                        if "enum" in item_schema:
                            _validate_enum(item, item_schema["enum"], f"{field_path}[{i}]")

    _validate_object(result_dict, schema, "$")

    # Evidence depth guard
    def _check_depth(obj: Any, current_depth: int, path: str) -> None:
        if current_depth > MAX_EVIDENCE_DEPTH:
            errors.append(
                f"{path}: nesting depth {current_depth} exceeds MAX_EVIDENCE_DEPTH ({MAX_EVIDENCE_DEPTH})",
            )
            return
        if isinstance(obj, dict):
            for k, v in obj.items():
                _check_depth(v, current_depth + 1, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _check_depth(v, current_depth + 1, f"{path}[{i}]")

    for i, check in enumerate(result_dict.get("checks", [])):
        evidence = check.get("evidence", {})
        if isinstance(evidence, dict):
            _check_depth(evidence, 0, f"$.checks[{i}].evidence")

    # Aggregate-only field guard: index is forbidden on non-aggregate results
    artifact_class = result_dict.get("artifact_class", ArtifactClass.INDIVIDUAL.value)
    has_index = "index" in result_dict and result_dict["index"]
    if has_index and artifact_class != ArtifactClass.AGGREGATE.value:
        errors.append(
            f"$.index: 'index' field is aggregate-only "
            f"(requires artifact_class='{ArtifactClass.AGGREGATE.value}', "
            f"got '{artifact_class}')",
        )

    # Payload size guard
    try:
        payload = json.dumps(result_dict, default=str)
        if len(payload.encode("utf-8")) > MAX_PAYLOAD_BYTES:
            errors.append(
                f"$: serialized payload size ({len(payload.encode('utf-8'))} bytes) "
                f"exceeds MAX_PAYLOAD_BYTES ({MAX_PAYLOAD_BYTES})",
            )
    except (TypeError, ValueError):
        errors.append("$: payload is not JSON-serializable")

    return errors


# ---------------------------------------------------------------------------
# Path normalization
# ---------------------------------------------------------------------------

_BACKSLASH_RE = re.compile(r"\\")
_DOTDOT_RE = re.compile(r"(^|/)\.\.(/|$)")
_DOT_RE = re.compile(r"(^|/)\./")


def normalize_repo_path(path: str | Path) -> str:
    """
    Normalize a path to repo-relative POSIX form.

    Rules (from Constitutional §20):
    - Forward slashes only
    - No ``..``
    - No absolute paths
    - No leading ``/``
    - No ``.`` segments
    """
    s = str(path)
    s = _BACKSLASH_RE.sub("/", s)
    # Strip drive letter on Windows (e.g. C:/)
    if len(s) >= 2 and s[1] == ":":
        s = s[2:]
    s = s.lstrip("/")
    # Collapse . and .. segments via PurePosixPath
    s = str(PurePosixPath(s))
    if s == ".":
        s = ""
    # Final safety: reject if still contains ..
    if _DOTDOT_RE.search(s):
        raise ValueError(f"Path contains '..' after normalization: {s}")
    return s


def validate_no_absolute_paths(data: dict[str, Any]) -> list[str]:
    """
    Recursively check a dict for absolute path strings.
    Returns list of JSON-path locations where absolute paths were found.
    """
    violations: list[str] = []

    def _walk(obj: Any, prefix: str) -> None:
        if isinstance(obj, str):
            if obj.startswith("/") or (len(obj) >= 2 and obj[1] == ":"):
                violations.append(prefix)
        elif isinstance(obj, dict):
            for k, v in obj.items():
                _walk(v, f"{prefix}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _walk(v, f"{prefix}[{i}]")

    _walk(data, "$")
    return violations


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class GuardianCheck:
    """Single check within a guardian run."""

    check_id: str
    status: str  # CheckStatus value
    details: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GuardianArtifact:
    """Artifact emitted by a guardian (path MUST be repo-relative POSIX)."""

    type: str  # ArtifactType value
    path: str  # repo-relative, POSIX normalized
    description: str

    def __post_init__(self) -> None:
        self.path = normalize_repo_path(self.path)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GuardianResult:
    """
    Canonical result object emitted by every Guardian.

    Fields:
        guardian_id: Stable string identifier (e.g. "hygiene", "autonomy").
        version: Contract version integer.
        timestamp: Optional ISO-8601 string. If present, must be injected or
                   fixed in tests. Omitted by default for determinism.
        status: One of PASS, FAIL, ERROR.
        summary: 1-2 line human-readable summary.
        checks: Ordered list of individual checks performed.
        artifacts: List of emitted artifacts (paths repo-relative POSIX).
        metrics: Numeric metrics (counts, timings if deterministic).
        remediation_hints: Optional list of short remediation strings.
    """

    guardian_id: str
    version: int = CONTRACT_VERSION
    timestamp: str | None = None
    correlation_id: str | None = None
    status: str = GuardianStatus.PASS.value
    summary: str = ""
    checks: list[GuardianCheck] = field(default_factory=list)
    artifacts: list[GuardianArtifact] = field(default_factory=list)
    metrics: dict[str, int | float] = field(default_factory=dict)
    remediation_hints: list[str] = field(default_factory=list)
    index: dict[str, Any] = field(default_factory=dict)
    artifact_class: str = ArtifactClass.INDIVIDUAL.value

    # -- Mutation helpers ---------------------------------------------------

    def add_check(
        self,
        check_id: str,
        status: CheckStatus | str,
        details: str,
        evidence: dict[str, Any] | None = None,
    ) -> None:
        """Add a check entry and update top-level status."""
        status_val = status.value if isinstance(status, CheckStatus) else status
        self.checks.append(
            GuardianCheck(
                check_id=check_id,
                status=status_val,
                details=details,
                evidence=evidence or {},
            ),
        )
        # Promote top-level status: any FAIL → FAIL, any ERROR stays ERROR
        if status_val == CheckStatus.FAIL.value and self.status != GuardianStatus.ERROR.value:
            self.status = GuardianStatus.FAIL.value

    def add_artifact(
        self,
        artifact_type: ArtifactType | str,
        path: str,
        description: str,
    ) -> None:
        type_val = artifact_type.value if isinstance(artifact_type, ArtifactType) else artifact_type
        self.artifacts.append(
            GuardianArtifact(type=type_val, path=path, description=description),
        )

    def set_error(self, summary: str) -> None:
        """Mark the entire result as ERROR (unexpected exception)."""
        self.status = GuardianStatus.ERROR.value
        self.summary = summary

    # -- Serialization ------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "guardian_id": self.guardian_id,
            "version": self.version,
            "status": self.status,
            "summary": self.summary,
            "checks": [c.to_dict() for c in self.checks],
            "artifacts": [a.to_dict() for a in self.artifacts],
            "metrics": self.metrics,
            "remediation_hints": self.remediation_hints,
        }
        if self.timestamp is not None:
            d["timestamp"] = self.timestamp
        if self.correlation_id is not None:
            d["correlation_id"] = self.correlation_id
        if self.index:
            d["index"] = self.index
        if self.artifact_class:
            d["artifact_class"] = self.artifact_class
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=False)

    # -- Validation ---------------------------------------------------------

    def validate(self) -> list[str]:
        """
        Validate this result against the contract.
        Returns a list of violation messages (empty = valid).
        """
        errors: list[str] = []
        if not self.guardian_id:
            errors.append("guardian_id is required")
        if self.status not in {s.value for s in GuardianStatus}:
            errors.append(f"Invalid status: {self.status}")
        for i, check in enumerate(self.checks):
            if check.status not in {s.value for s in CheckStatus}:
                errors.append(f"checks[{i}].status invalid: {check.status}")
            if not check.check_id:
                errors.append(f"checks[{i}].check_id is required")
        for i, artifact in enumerate(self.artifacts):
            if artifact.type not in {t.value for t in ArtifactType}:
                errors.append(f"artifacts[{i}].type invalid: {artifact.type}")
        # Check for absolute paths in serialized form
        abs_paths = validate_no_absolute_paths(self.to_dict())
        for loc in abs_paths:
            errors.append(f"Absolute path found at {loc}")
        return errors


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def write_guardian_result(
    result: GuardianResult,
    output_dir: Path,
    filename: str = "guardian_result.json",
) -> Path:
    """
    Write a GuardianResult to a JSON file.

    Args:
        result: The result to write.
        output_dir: Directory to write into (created if needed).
        filename: Output filename.

    Returns:
        Absolute path to the written file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / filename
    out_path.write_text(result.to_json(), encoding="utf-8")
    return out_path


def load_guardian_result(path: Path | str) -> GuardianResult:
    """Load a GuardianResult from a JSON file."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    checks = [GuardianCheck(**c) for c in data.get("checks", [])]
    artifacts = [
        GuardianArtifact(
            type=a["type"],
            path=a["path"],
            description=a["description"],
        )
        for a in data.get("artifacts", [])
    ]

    return GuardianResult(
        guardian_id=data["guardian_id"],
        version=data.get("version", CONTRACT_VERSION),
        timestamp=data.get("timestamp"),
        correlation_id=data.get("correlation_id"),
        status=data.get("status", GuardianStatus.PASS.value),
        summary=data.get("summary", ""),
        checks=checks,
        artifacts=artifacts,
        metrics=data.get("metrics", {}),
        remediation_hints=data.get("remediation_hints", []),
        index=data.get("index", {}),
        artifact_class=data.get("artifact_class", ArtifactClass.INDIVIDUAL.value),
    )
