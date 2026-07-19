"""Fail-closed C0.3 operational-evidence envelope primitives.

The v2 envelope is a reference manifest, not an authority receipt.  It carries
no caller-authored measurements or verdicts.  Verification reopens every
artifact beneath an out-of-band trusted root, recomputes its digest, checks an
out-of-band binding anchor, and then consults a closed producer registry.

No currently registered artifact contract is sufficient to produce a C0.3
operational measurement.  Consequently every binding remains ``UNKNOWN``
until a real producer and measurement adapter are added to the registry.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import stat
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any, Final, Literal, Mapping

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_VERSION: Final = "apps_rg.c03_graph_health_operational_evidence.v2"
PRODUCER_REGISTRY_VERSION: Final = "apps_rg.c03_graph_operational_producer_registry.v1"
MAX_ARTIFACT_BYTES: Final = 16 * 1024 * 1024
SCHEMA_PATH: Final = (
    Path(__file__).resolve().parent / "schemas" / "c03_graph_health_operational_evidence.v2.schema.json"
)

METRIC_IDS: Final[tuple[str, ...]] = (
    "decision_safe_regression",
    "source_currentness",
    "source_freshness",
    "hitl_approval_coverage",
    "write_audit_coverage",
    "p0_sla_compliance",
    "p1_sla_compliance",
)

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")


class OperationalEvidenceError(ValueError):
    """Raised when an envelope cannot be assembled safely."""


@dataclass(frozen=True, slots=True)
class ArtifactReferenceInput:
    """Unhashed artifact reference supplied to the reference-only assembler."""

    role: str
    artifact_root_id: str
    relative_path: str


@dataclass(frozen=True, slots=True)
class ProducerBindingInput:
    """Producer/cohort metadata supplied to the reference-only assembler."""

    producer_id: str
    producer_schema_version: str
    producer_run_id: str
    cohort_id: str
    cohort_as_of_utc: datetime
    cohort_closed_at_utc: datetime
    authority_anchor_id: str
    artifact_refs: tuple[ArtifactReferenceInput, ...]


@dataclass(frozen=True, slots=True)
class OperationalTrustContext:
    """Out-of-band trust supplied by the operational-evidence consumer.

    ``artifact_roots`` maps opaque root IDs to consumer-selected directories.
    ``authority_anchors`` maps opaque anchor IDs to expected SHA-256 digests of
    the registry version, envelope subject, metric ID, and complete metric
    binding.  Neither mapping is serialized into the envelope.
    A digest copied from the envelope into this context is still self-attested;
    callers must source these values from an independent trust channel.
    """

    artifact_roots: Mapping[str, Path]
    authority_anchors: Mapping[str, str]
    expected_candidate_commit_sha: str
    expected_canonical_graph_sha256: str
    expected_health_policy_sha256: str
    expected_health_run_id: str
    observed_at_utc: datetime
    max_replay_age: timedelta = timedelta(days=7)

    def __post_init__(self) -> None:
        candidate = str(self.expected_candidate_commit_sha).strip().lower()
        graph = str(self.expected_canonical_graph_sha256).strip().lower()
        policy = str(self.expected_health_policy_sha256).strip().lower()
        run_id = str(self.expected_health_run_id).strip()
        if not _COMMIT_SHA.fullmatch(candidate):
            raise OperationalEvidenceError("expected_candidate_commit_sha must be a lowercase Git SHA-1")
        if not _SHA256.fullmatch(graph):
            raise OperationalEvidenceError("expected_canonical_graph_sha256 must be a lowercase SHA-256")
        if not _SHA256.fullmatch(policy):
            raise OperationalEvidenceError("expected_health_policy_sha256 must be a lowercase SHA-256")
        if not run_id:
            raise OperationalEvidenceError("expected_health_run_id must be nonempty")
        observed_at = _require_aware_datetime(self.observed_at_utc, "observed_at_utc")
        if self.max_replay_age < timedelta(0):
            raise OperationalEvidenceError("max_replay_age must be nonnegative")

        roots = {str(root_id).strip(): Path(root_path) for root_id, root_path in self.artifact_roots.items()}
        if any(not root_id for root_id in roots):
            raise OperationalEvidenceError("artifact root IDs must be nonempty")
        anchors = {
            str(anchor_id).strip(): str(digest).strip().lower()
            for anchor_id, digest in self.authority_anchors.items()
        }
        if any(not anchor_id for anchor_id in anchors):
            raise OperationalEvidenceError("authority anchor IDs must be nonempty")
        if any(not _SHA256.fullmatch(digest) for digest in anchors.values()):
            raise OperationalEvidenceError("authority anchors must be lowercase SHA-256 digests")

        object.__setattr__(self, "artifact_roots", MappingProxyType(roots))
        object.__setattr__(self, "authority_anchors", MappingProxyType(anchors))
        object.__setattr__(self, "expected_candidate_commit_sha", candidate)
        object.__setattr__(self, "expected_canonical_graph_sha256", graph)
        object.__setattr__(self, "expected_health_policy_sha256", policy)
        object.__setattr__(self, "expected_health_run_id", run_id)
        object.__setattr__(self, "observed_at_utc", observed_at)


@dataclass(frozen=True, slots=True)
class ProducerContract:
    """Closed, code-owned description of a recognized genuine artifact."""

    schema_versions: frozenset[str]
    artifact_roles: frozenset[str]
    required_roles: frozenset[str]
    primary_schema_role: str


@dataclass(frozen=True, slots=True)
class MetricEvidenceResult:
    """Fail-closed producer support result for one operational metric."""

    metric_id: str
    status: Literal["SUPPORTED", "UNKNOWN"]
    reason_codes: tuple[str, ...]
    producer_id: str | None = None
    verified_artifact_sha256s: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class OperationalEvidenceVerification:
    """Read-only verification result for a v2 envelope."""

    schema_valid: bool
    integrity_valid: bool
    subject_valid: bool
    metrics: tuple[MetricEvidenceResult, ...]
    envelope_errors: tuple[str, ...] = ()


# These are recognized, real artifact contracts.  Recognition is not
# operational authority; it only lets schema/role drift fail precisely.
_KNOWN_ARTIFACT_CONTRACTS: Final[Mapping[str, ProducerContract]] = MappingProxyType(
    {
        "apps_rg.resume_graph_w6_ci_receipt.v1": ProducerContract(
            schema_versions=frozenset({"apps_rg.resume_graph_w6_ci_receipt.v1"}),
            artifact_roles=frozenset({"ci_receipt"}),
            required_roles=frozenset({"ci_receipt"}),
            primary_schema_role="ci_receipt",
        ),
    }
)

# No existing producer contract provides a complete, cohort-bound operational
# measurement.  Activation belongs here only after a real producer and its
# derivation verifier exist; envelope content cannot add entries to this map.
_OPERATIONAL_PRODUCER_REGISTRY: Final[Mapping[str, frozenset[str]]] = MappingProxyType({})


class _ArtifactPathError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code


class _ArtifactSnapshotError(OSError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code


def _require_aware_datetime(value: datetime, field: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise OperationalEvidenceError(f"{field} must be a timezone-aware datetime")
    return value.astimezone(timezone.utc)


def _format_datetime(value: datetime, field: str) -> str:
    normalized = _require_aware_datetime(value, field)
    rendered = normalized.isoformat(timespec="microseconds").replace("+00:00", "Z")
    return rendered.replace(".000000Z", "Z")


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _canonical_bytes(value: Any) -> bytes:
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise OperationalEvidenceError(f"value is not canonical-JSON serializable: {exc}") from exc
    return encoded.encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def compute_envelope_integrity(envelope: Mapping[str, Any]) -> str:
    """Recompute transport integrity, excluding the self-referential field."""

    if not isinstance(envelope, Mapping):
        raise OperationalEvidenceError("operational envelope must be a mapping")
    payload = {key: value for key, value in envelope.items() if key != "integrity_sha256"}
    return _sha256_bytes(_canonical_bytes(payload))


def compute_binding_anchor_digest(
    metric_id: str,
    binding: Mapping[str, Any],
    *,
    subject: Mapping[str, Any],
    producer_registry_version: str,
) -> str:
    """Compute a binding digest for comparison with an out-of-band trust pin.

    Computing this value does not make it authoritative.  The expected digest
    must enter through ``OperationalTrustContext.authority_anchors`` from an
    independent source.
    """

    if metric_id not in METRIC_IDS:
        raise OperationalEvidenceError(f"unsupported operational metric: {metric_id}")
    if not isinstance(binding, Mapping):
        raise OperationalEvidenceError("producer binding must be a mapping")
    if not isinstance(subject, Mapping):
        raise OperationalEvidenceError("operational evidence subject must be a mapping")
    if producer_registry_version != PRODUCER_REGISTRY_VERSION:
        raise OperationalEvidenceError("unsupported operational producer registry version")
    return _sha256_bytes(
        _canonical_bytes(
            {
                "metric_id": metric_id,
                "producer_registry_version": producer_registry_version,
                "subject": dict(subject),
                "binding": dict(binding),
            }
        )
    )


@lru_cache(maxsize=1)
def _schema_validator() -> Draft202012Validator:
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OperationalEvidenceError(f"operational evidence schema is unreadable: {exc}") from exc
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _schema_errors(envelope: Any) -> tuple[str, ...]:
    errors = sorted(
        _schema_validator().iter_errors(envelope),
        key=lambda error: (tuple(str(item) for item in error.absolute_path), error.message),
    )
    return tuple(
        f"{'/'.join(str(item) for item in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    )


def _relative_parts(relative_path: str) -> tuple[str, ...]:
    if not isinstance(relative_path, str) or not relative_path:
        raise _ArtifactPathError("artifact_path_unsafe", "relative path must be nonempty")
    if "\\" in relative_path or "\x00" in relative_path:
        raise _ArtifactPathError(
            "artifact_path_unsafe",
            "relative path must use POSIX separators and contain no NUL",
        )
    if relative_path.startswith("/") or _WINDOWS_DRIVE.match(relative_path):
        raise _ArtifactPathError("artifact_path_unsafe", "relative path must not be absolute")
    path = PurePosixPath(relative_path)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise _ArtifactPathError(
            "artifact_path_unsafe",
            "relative path must not contain empty, dot, or parent segments",
        )
    return tuple(path.parts)


def _is_link_or_junction(path: Path) -> bool:
    if path.is_symlink():
        return True
    junction_check = getattr(path, "is_junction", None)
    return bool(junction_check is not None and junction_check())


def _validate_artifact_components(
    resolved_root: Path,
    parts: tuple[str, ...],
) -> Path:
    candidate = resolved_root
    for index, part in enumerate(parts):
        candidate = candidate / part
        try:
            mode = os.lstat(candidate).st_mode
            link_like = _is_link_or_junction(candidate)
        except FileNotFoundError as exc:
            raise _ArtifactPathError(
                "artifact_missing",
                f"artifact path component is missing: {'/'.join(parts[: index + 1])}",
            ) from exc
        except OSError as exc:
            raise _ArtifactPathError(
                "artifact_path_unsafe",
                f"artifact path component cannot be inspected safely: {exc}",
            ) from exc
        if link_like or stat.S_ISLNK(mode):
            raise _ArtifactPathError(
                "artifact_path_unsafe",
                "artifact path must not contain symlinks or junctions",
            )
        final = index == len(parts) - 1
        if not final and not stat.S_ISDIR(mode):
            raise _ArtifactPathError(
                "artifact_path_unsafe",
                "artifact parent path component is not a directory",
            )
        if final and not stat.S_ISREG(mode):
            raise _ArtifactPathError(
                "artifact_not_file",
                "artifact path does not identify a regular file",
            )
    return candidate


def _prepare_artifact_path(root: Path, relative_path: str) -> tuple[Path, Path, tuple[str, ...]]:
    parts = _relative_parts(relative_path)
    try:
        resolved_root = root.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise _ArtifactPathError(
            "artifact_root_missing", f"trusted artifact root is unavailable: {exc}"
        ) from exc
    if not resolved_root.is_dir():
        raise _ArtifactPathError("artifact_root_invalid", "trusted artifact root is not a directory")
    candidate = _validate_artifact_components(resolved_root, parts)
    try:
        resolved_candidate = candidate.resolve(strict=True)
    except FileNotFoundError as exc:
        raise _ArtifactPathError("artifact_missing", f"artifact is missing: {relative_path}") from exc
    except (OSError, RuntimeError) as exc:
        raise _ArtifactPathError(
            "artifact_path_unsafe", f"artifact path cannot be resolved safely: {exc}"
        ) from exc
    if not resolved_candidate.is_relative_to(resolved_root):
        raise _ArtifactPathError(
            "artifact_path_unsafe",
            "artifact path or symlink escapes its trusted root",
        )
    return resolved_root, candidate, parts


def _artifact_stat_fingerprint(value: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        int(value.st_dev),
        int(value.st_ino),
        int(value.st_size),
        int(value.st_mtime_ns),
        int(value.st_ctime_ns),
    )


def _validate_open_artifact_identity(
    handle: Any,
    *,
    resolved_root: Path,
    candidate: Path,
    parts: tuple[str, ...],
) -> os.stat_result:
    _validate_artifact_components(resolved_root, parts)
    try:
        resolved_candidate = candidate.resolve(strict=True)
        path_stat = candidate.stat()
        handle_stat = os.fstat(handle.fileno())
    except FileNotFoundError as exc:
        raise _ArtifactSnapshotError(
            "artifact_identity_changed",
            "artifact path disappeared after it was opened",
        ) from exc
    except OSError as exc:
        raise _ArtifactSnapshotError("artifact_unreadable", str(exc)) from exc
    if not resolved_candidate.is_relative_to(resolved_root):
        raise _ArtifactPathError(
            "artifact_path_unsafe",
            "opened artifact path escapes its trusted root",
        )
    if not stat.S_ISREG(handle_stat.st_mode) or not os.path.samestat(
        handle_stat,
        path_stat,
    ):
        raise _ArtifactSnapshotError(
            "artifact_identity_changed",
            "opened artifact no longer matches its trusted path",
        )
    return handle_stat


def _read_trusted_artifact_snapshot(root: Path, relative_path: str) -> bytes:
    resolved_root, candidate, parts = _prepare_artifact_path(root, relative_path)
    try:
        with candidate.open("rb") as handle:
            before = _validate_open_artifact_identity(
                handle,
                resolved_root=resolved_root,
                candidate=candidate,
                parts=parts,
            )
            if before.st_size > MAX_ARTIFACT_BYTES:
                raise _ArtifactSnapshotError(
                    "artifact_size_limit_exceeded",
                    f"artifact exceeds {MAX_ARTIFACT_BYTES} bytes",
                )
            snapshot = handle.read(MAX_ARTIFACT_BYTES + 1)
            after = _validate_open_artifact_identity(
                handle,
                resolved_root=resolved_root,
                candidate=candidate,
                parts=parts,
            )
    except (_ArtifactPathError, _ArtifactSnapshotError):
        raise
    except OSError as exc:
        raise _ArtifactSnapshotError("artifact_unreadable", str(exc)) from exc
    if len(snapshot) > MAX_ARTIFACT_BYTES:
        raise _ArtifactSnapshotError(
            "artifact_size_limit_exceeded",
            f"artifact exceeds {MAX_ARTIFACT_BYTES} bytes",
        )
    if _artifact_stat_fingerprint(before) != _artifact_stat_fingerprint(after):
        raise _ArtifactSnapshotError(
            "artifact_changed_during_read",
            "artifact metadata changed while its snapshot was read",
        )
    return snapshot


def _subject_payload(context: OperationalTrustContext) -> dict[str, str]:
    return {
        "candidate_commit_sha": context.expected_candidate_commit_sha,
        "canonical_graph_sha256": context.expected_canonical_graph_sha256,
        "health_policy_sha256": context.expected_health_policy_sha256,
        "health_run_id": context.expected_health_run_id,
    }


def assemble_operational_evidence_envelope(
    *,
    envelope_id: str,
    assembled_at_utc: datetime,
    bindings: Mapping[str, ProducerBindingInput],
    context: OperationalTrustContext,
) -> dict[str, Any]:
    """Assemble a reference-only v2 envelope without authority or measurements."""

    assembled_bindings: dict[str, dict[str, Any]] = {}
    for metric_id in sorted(bindings):
        if metric_id not in METRIC_IDS:
            raise OperationalEvidenceError(f"unsupported operational metric: {metric_id}")
        binding = bindings[metric_id]
        if not isinstance(binding, ProducerBindingInput):
            raise OperationalEvidenceError(f"binding for {metric_id} must be ProducerBindingInput")
        if not binding.artifact_refs:
            raise OperationalEvidenceError(f"binding for {metric_id} requires at least one artifact ref")

        artifact_rows: list[dict[str, str]] = []
        for artifact_ref in sorted(
            binding.artifact_refs,
            key=lambda row: (row.role, row.artifact_root_id, row.relative_path),
        ):
            root = context.artifact_roots.get(artifact_ref.artifact_root_id)
            if root is None:
                raise OperationalEvidenceError(
                    f"artifact_root_not_trusted: {artifact_ref.artifact_root_id}",
                )
            try:
                artifact_snapshot = _read_trusted_artifact_snapshot(
                    root,
                    artifact_ref.relative_path,
                )
            except (_ArtifactPathError, _ArtifactSnapshotError) as exc:
                raise OperationalEvidenceError(f"{exc.code}: {exc}") from exc
            artifact_rows.append(
                {
                    "role": str(artifact_ref.role),
                    "artifact_root_id": str(artifact_ref.artifact_root_id),
                    "relative_path": str(artifact_ref.relative_path),
                    "sha256": _sha256_bytes(artifact_snapshot),
                }
            )

        assembled_bindings[metric_id] = {
            "producer_id": binding.producer_id,
            "producer_schema_version": binding.producer_schema_version,
            "producer_run_id": binding.producer_run_id,
            "cohort_id": binding.cohort_id,
            "cohort_as_of_utc": _format_datetime(
                binding.cohort_as_of_utc,
                f"bindings.{metric_id}.cohort_as_of_utc",
            ),
            "cohort_closed_at_utc": _format_datetime(
                binding.cohort_closed_at_utc,
                f"bindings.{metric_id}.cohort_closed_at_utc",
            ),
            "authority_anchor_id": binding.authority_anchor_id,
            "artifact_refs": artifact_rows,
        }

    envelope: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "envelope_id": str(envelope_id),
        "producer_registry_version": PRODUCER_REGISTRY_VERSION,
        "assembled_at_utc": _format_datetime(assembled_at_utc, "assembled_at_utc"),
        "subject": _subject_payload(context),
        "bindings": assembled_bindings,
    }
    envelope["integrity_sha256"] = compute_envelope_integrity(envelope)
    errors = _schema_errors(envelope)
    if errors:
        raise OperationalEvidenceError("assembled envelope failed v2 schema: " + "; ".join(errors))
    return envelope


def _unknown_metric(
    metric_id: str,
    reason_codes: tuple[str, ...],
    *,
    producer_id: str | None = None,
    verified_artifacts: tuple[str, ...] = (),
) -> MetricEvidenceResult:
    return MetricEvidenceResult(
        metric_id=metric_id,
        status="UNKNOWN",
        reason_codes=reason_codes,
        producer_id=producer_id,
        verified_artifact_sha256s=verified_artifacts,
    )


def _all_unknown(
    reason: str,
    *,
    schema_valid: bool,
    integrity_valid: bool,
    subject_valid: bool,
    errors: tuple[str, ...] = (),
) -> OperationalEvidenceVerification:
    return OperationalEvidenceVerification(
        schema_valid=schema_valid,
        integrity_valid=integrity_valid,
        subject_valid=subject_valid,
        metrics=tuple(_unknown_metric(metric_id, (reason,)) for metric_id in METRIC_IDS),
        envelope_errors=errors,
    )


def _verify_artifact_schema(snapshot: bytes, expected_schema: str) -> bool:
    try:
        payload = json.loads(snapshot.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        return False
    return isinstance(payload, dict) and payload.get("schema_version") == expected_schema


def _verify_binding(
    metric_id: str,
    binding: Mapping[str, Any],
    context: OperationalTrustContext,
) -> MetricEvidenceResult:
    producer_id = str(binding.get("producer_id") or "")
    contract = _KNOWN_ARTIFACT_CONTRACTS.get(producer_id)
    if contract is None:
        return _unknown_metric(metric_id, ("producer_not_registered",), producer_id=producer_id)

    producer_schema = str(binding.get("producer_schema_version") or "")
    if producer_schema not in contract.schema_versions:
        return _unknown_metric(
            metric_id,
            ("producer_schema_not_registered",),
            producer_id=producer_id,
        )

    artifact_refs = binding.get("artifact_refs")
    if not isinstance(artifact_refs, list):
        return _unknown_metric(metric_id, ("artifact_refs_invalid",), producer_id=producer_id)
    roles = [str(row.get("role") or "") for row in artifact_refs if isinstance(row, Mapping)]
    if any(role not in contract.artifact_roles for role in roles):
        return _unknown_metric(
            metric_id,
            ("producer_artifact_role_not_registered",),
            producer_id=producer_id,
        )
    if not contract.required_roles.issubset(roles):
        return _unknown_metric(
            metric_id,
            ("producer_required_artifact_role_missing",),
            producer_id=producer_id,
        )
    if len(roles) != len(set(roles)):
        return _unknown_metric(
            metric_id,
            ("producer_artifact_role_duplicated",),
            producer_id=producer_id,
        )

    cohort_as_of = _parse_datetime(binding.get("cohort_as_of_utc"))
    cohort_closed_at = _parse_datetime(binding.get("cohort_closed_at_utc"))
    if cohort_as_of is None or cohort_closed_at is None:
        return _unknown_metric(metric_id, ("cohort_timestamp_invalid",), producer_id=producer_id)
    if cohort_as_of > cohort_closed_at:
        return _unknown_metric(
            metric_id,
            ("cohort_timestamp_order_invalid",),
            producer_id=producer_id,
        )
    if cohort_closed_at > context.observed_at_utc:
        return _unknown_metric(metric_id, ("cohort_timestamp_in_future",), producer_id=producer_id)
    if context.observed_at_utc - cohort_closed_at > context.max_replay_age:
        return _unknown_metric(
            metric_id,
            ("cohort_replay_window_exceeded",),
            producer_id=producer_id,
        )

    anchor_id = str(binding.get("authority_anchor_id") or "")
    expected_anchor = context.authority_anchors.get(anchor_id)
    if expected_anchor is None:
        return _unknown_metric(
            metric_id,
            ("authority_anchor_missing",),
            producer_id=producer_id,
        )
    observed_anchor = compute_binding_anchor_digest(
        metric_id,
        binding,
        subject=_subject_payload(context),
        producer_registry_version=PRODUCER_REGISTRY_VERSION,
    )
    if not hmac.compare_digest(observed_anchor, expected_anchor):
        return _unknown_metric(
            metric_id,
            ("authority_anchor_mismatch",),
            producer_id=producer_id,
        )

    verified_digests: list[str] = []
    primary_snapshot: bytes | None = None
    for artifact_ref in artifact_refs:
        if not isinstance(artifact_ref, Mapping):
            return _unknown_metric(metric_id, ("artifact_ref_invalid",), producer_id=producer_id)
        root_id = str(artifact_ref.get("artifact_root_id") or "")
        relative_path = str(artifact_ref.get("relative_path") or "")
        expected_sha256 = str(artifact_ref.get("sha256") or "")
        root = context.artifact_roots.get(root_id)
        if root is None:
            return _unknown_metric(
                metric_id,
                ("artifact_root_not_trusted",),
                producer_id=producer_id,
            )
        try:
            artifact_snapshot = _read_trusted_artifact_snapshot(root, relative_path)
        except (_ArtifactPathError, _ArtifactSnapshotError) as exc:
            return _unknown_metric(metric_id, (exc.code,), producer_id=producer_id)
        observed_sha256 = _sha256_bytes(artifact_snapshot)
        if not hmac.compare_digest(observed_sha256, expected_sha256):
            return _unknown_metric(
                metric_id,
                ("artifact_sha256_mismatch",),
                producer_id=producer_id,
            )
        verified_digests.append(observed_sha256)
        if artifact_ref.get("role") == contract.primary_schema_role:
            primary_snapshot = artifact_snapshot

    verified = tuple(sorted(verified_digests))
    if primary_snapshot is None or not _verify_artifact_schema(primary_snapshot, producer_schema):
        return _unknown_metric(
            metric_id,
            ("producer_artifact_schema_mismatch",),
            producer_id=producer_id,
            verified_artifacts=verified,
        )

    supported_metrics = _OPERATIONAL_PRODUCER_REGISTRY.get(producer_id, frozenset())
    if metric_id not in supported_metrics:
        return _unknown_metric(
            metric_id,
            ("producer_not_registered_for_metric",),
            producer_id=producer_id,
            verified_artifacts=verified,
        )

    return MetricEvidenceResult(
        metric_id=metric_id,
        status="SUPPORTED",
        reason_codes=(),
        producer_id=producer_id,
        verified_artifact_sha256s=verified,
    )


def verify_operational_evidence_envelope(
    envelope: Mapping[str, Any],
    *,
    context: OperationalTrustContext,
) -> OperationalEvidenceVerification:
    """Verify a v2 reference envelope without mutating any source artifact."""

    errors = _schema_errors(envelope)
    if errors:
        return _all_unknown(
            "envelope_schema_invalid",
            schema_valid=False,
            integrity_valid=False,
            subject_valid=False,
            errors=errors,
        )

    claimed_integrity = str(envelope.get("integrity_sha256") or "")
    observed_integrity = compute_envelope_integrity(envelope)
    if not hmac.compare_digest(claimed_integrity, observed_integrity):
        return _all_unknown(
            "envelope_integrity_mismatch",
            schema_valid=True,
            integrity_valid=False,
            subject_valid=False,
        )

    if envelope.get("subject") != _subject_payload(context):
        return _all_unknown(
            "envelope_subject_mismatch",
            schema_valid=True,
            integrity_valid=True,
            subject_valid=False,
        )

    bindings = envelope.get("bindings")
    if not isinstance(bindings, Mapping):
        return _all_unknown(
            "envelope_schema_invalid",
            schema_valid=False,
            integrity_valid=True,
            subject_valid=True,
            errors=("bindings: expected object",),
        )
    metric_results: list[MetricEvidenceResult] = []
    for metric_id in METRIC_IDS:
        binding = bindings.get(metric_id)
        if not isinstance(binding, Mapping):
            metric_results.append(_unknown_metric(metric_id, ("binding_missing",)))
            continue
        metric_results.append(_verify_binding(metric_id, binding, context))
    return OperationalEvidenceVerification(
        schema_valid=True,
        integrity_valid=True,
        subject_valid=True,
        metrics=tuple(metric_results),
    )


__all__ = [
    "METRIC_IDS",
    "PRODUCER_REGISTRY_VERSION",
    "SCHEMA_PATH",
    "SCHEMA_VERSION",
    "ArtifactReferenceInput",
    "MetricEvidenceResult",
    "OperationalEvidenceError",
    "OperationalEvidenceVerification",
    "OperationalTrustContext",
    "ProducerBindingInput",
    "assemble_operational_evidence_envelope",
    "compute_binding_anchor_digest",
    "compute_envelope_integrity",
    "verify_operational_evidence_envelope",
]
