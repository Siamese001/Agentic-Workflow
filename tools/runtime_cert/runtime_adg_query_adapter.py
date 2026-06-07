"""Read-only runtime ADG query adapter — Phase C.1.

Converts ``RuntimeADGNode`` instances from a ``RuntimeADGSnapshot`` into
the Phase C 18-field trace row shape defined in
``docs/plans/runtime_cert_phase_c_trace_collector_plan.md`` §3.1.

Design references
-----------------
- Phase C plan: ``docs/plans/runtime_cert_phase_c_trace_collector_plan.md`` v2
- Phase C.1 plan: ``docs/archive/windsurf/legacy-tree/plans/runtime-cert-c1-query-adapter-7e3f92.md``
- Phase B.5 helpers: ``tools/runtime_cert/negative_controls.py``
- Snapshot types: ``system_learning/runtime_adg/snapshot.py``

What this module does
---------------------
- Accepts a ``RuntimeADGSnapshot`` (in-memory, content-addressed).
- Yields ``PhaseC1Row`` instances filtered by trace_id / time window.
- Parses ``attributes_json`` once at the boundary; downstream helpers
  receive a plain ``dict``.
- Applies documented fail-closed defaults for every field that cannot be
  derived from the node alone.

What this module does NOT do
----------------------------
- Does NOT certify apps. ``runtime_certification_status`` is always
  ``NOT_CERTIFIED`` — constructing a ``PhaseC1Row`` with any other value
  raises ``ValueError``.
- Does NOT write to any store (no I/O side-effects).
- Does NOT modify any emitter, scanner, or app.
- Does NOT perform contract resolution — ``contract_name`` and
  ``normalized_cert_alias`` are left as ``None`` for Phase C.2 to fill.
- Does NOT import ``RuntimeADGQuery`` (``tools/adg/runtime_query.py``),
  which targets the static code-structure ADG, not the runtime snapshot store.
- Does NOT call ``compute_manifest_hash_for_app`` or consult
  ``apps_spine_coverage.py`` — those are C.3/C.4/C.5 responsibilities.
"""

from __future__ import annotations

# ADR-079 consumer mode declaration (required for all runtime-cert tools).
__adg_consumer_mode__ = "runtime_cert_read"

import json
import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Iterator

from agentic_core.L6_system_learning.snapshot import (
    RuntimeADGNode,
    RuntimeADGSnapshot,
    attributes_to_json,
    create_runtime_adg_snapshot,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

NOT_CERTIFIED: Final[str] = "NOT_CERTIFIED"
EVIDENCE_SOURCE_PREFIX: Final[str] = "runtime_adg.snapshot."

VALID_ROUTE_SHAPES: Final[frozenset[str]] = frozenset(
    {
        "R3_grounded_read",
        "R3R4_grounded_write",
        "build_time_compiler",
        "formal_exception",
    }
)

#: Frozen schema version — bump this constant (and open an AG-C-3 amendment
#: Author-Gate) if the 18-field row schema changes.
PHASE_C1_SCHEMA_VERSION: Final[str] = "1.0"

# ---------------------------------------------------------------------------
# PhaseC1Row dataclass — the 18-field trace row
# ---------------------------------------------------------------------------


@dataclass
class PhaseC1Row:
    """Typed wrapper around the Phase C 18-field trace row.

    Fields
    ------
    Mandatory identity fields (set at construction time):

    app_name : str
        Application name — must start with ``apps_``.
        Empty string signals "not yet resolved" (fail-closed).
    route_shape : str
        One of ``VALID_ROUTE_SHAPES``. Empty = not yet resolved.
    trace_id : str
        OTel trace ID (snapshot-level value).
    span_id : str
        OTel span ID (= ``RuntimeADGNode.node_id``).
    parent_span_id : str | None
        ``None`` for root spans; extracted from ``attributes``.
    span_name : str
        Raw span name from ``RuntimeADGNode.name``. Preserved verbatim for
        C.2 pattern matching.
    timestamp : int
        Span start time (Unix milliseconds) from
        ``RuntimeADGNode.started_at_utc``.

    Contract-resolution fields (C.1 leaves as None — C.2 fills these):

    contract_name : str | None
        Resolved contract name (e.g. ``"ValidatedRequest"``).
    normalized_cert_alias : str | None
        Harness-internal alias from ``ContractSpanBinding``.

    App-level provenance (partially back-filled by C.3/C.4/C.5):

    manifest_hash : str
        64-char lowercase hex. Empty when not present in span attributes.
    static_runtime_mode : str
        Scanner output field (e.g. ``APP_OVERLAY_STATIC_EVIDENCE``).
        Empty until C.3/C.4/C.5 consulte the scanner.

    Certification status (invariant — always NOT_CERTIFIED in Phase C):

    runtime_certification_status : str
        Always ``"NOT_CERTIFIED"``. Any other value raises ``ValueError``
        in ``__post_init__``.

    Optional identifiers (populated post-hardening):

    artifact_id : str | None
        From ``attributes["artifact_id"]`` or ``attributes["contract_id"]``.
    contract_id : str | None
        From ``attributes["contract_id"]``.
    source_path : str | None
        From ``attributes["code.filepath"]`` or ``attributes["source_path"]``.
        Required by CC-SHARED-03 discrimination in Phase B.5.

    Nested attributes:

    attributes : dict[str, Any]
        Parsed from ``RuntimeADGNode.attributes_json`` via ``json.loads``.
        Set to ``{}`` on ``JSONDecodeError``.

    Provenance:

    evidence_source : str
        ``"runtime_adg.snapshot.<snapshot_id>"``. Provides the audit trail
        required by the parent plan §3.1.

    Notes
    -----
    - ``contract_name`` and ``normalized_cert_alias`` are intentionally
      ``None`` from C.1. Phase C.2 populates them via the §4 mapping
      precedence.
    - ``manifest_hash`` and ``static_runtime_mode`` are partially back-filled
      by Phase C.3/C.4/C.5 extractors.
    - ``to_dict()`` returns a flat JSON-serialisable dict compatible with
      Phase B.5's ``_row_str`` / ``_row_list`` accessors.
    """

    # ---- identity ----
    app_name: str
    route_shape: str
    trace_id: str
    span_id: str
    parent_span_id: str | None
    span_name: str
    timestamp: int

    # ---- contract resolution (C.2 fills) ----
    contract_name: str | None = None
    normalized_cert_alias: str | None = None

    # ---- app-level provenance (C.3/C.4/C.5 back-fill) ----
    manifest_hash: str = ""
    static_runtime_mode: str = ""

    # ---- certification status — INVARIANT ----
    runtime_certification_status: str = NOT_CERTIFIED

    # ---- optional identifiers ----
    artifact_id: str | None = None
    contract_id: str | None = None
    source_path: str | None = None

    # ---- nested attributes ----
    attributes: dict[str, Any] = field(default_factory=dict)

    # ---- provenance ----
    evidence_source: str = ""

    def __post_init__(self) -> None:
        if self.runtime_certification_status != NOT_CERTIFIED:
            raise ValueError(
                f"PhaseC1Row.runtime_certification_status must be "
                f"{NOT_CERTIFIED!r}; got {self.runtime_certification_status!r}. "
                "Phase C never writes a certification verdict. "
                "That is Phase D's responsibility."
            )

    def to_dict(self) -> dict[str, Any]:
        """Return a flat JSON-serialisable dict compatible with B.5 row accessors.

        The output has exactly 18 keys (the schema fields). An additional
        ``schema_version`` key is included for Phase D cache compatibility
        but does not count toward the 18-field schema count.
        """
        return {
            "app_name": self.app_name,
            "route_shape": self.route_shape,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "span_name": self.span_name,
            "timestamp": self.timestamp,
            "contract_name": self.contract_name,
            "normalized_cert_alias": self.normalized_cert_alias,
            "manifest_hash": self.manifest_hash,
            "static_runtime_mode": self.static_runtime_mode,
            "runtime_certification_status": self.runtime_certification_status,
            "artifact_id": self.artifact_id,
            "contract_id": self.contract_id,
            "source_path": self.source_path,
            "attributes": self.attributes,
            "evidence_source": self.evidence_source,
            # schema_version is an envelope field — included in to_dict() for
            # Phase D cache-invalidation but NOT counted as one of the 18
            # schema fields in PHASE_C1_SCHEMA_VERSION.
            "schema_version": PHASE_C1_SCHEMA_VERSION,
        }


# ---------------------------------------------------------------------------
# Core conversion helpers
# ---------------------------------------------------------------------------


def extract_attributes(node: RuntimeADGNode) -> dict[str, Any]:
    """Parse ``node.attributes_json`` and return a plain dict.

    Parameters
    ----------
    node:
        A ``RuntimeADGNode`` whose ``attributes_json`` field is a compact
        sorted JSON string (produced by ``attributes_to_json``).

    Returns
    -------
    dict[str, Any]
        Parsed attributes. Returns ``{}`` on any parse error — never raises.
    """
    if not node.attributes_json:
        return {}
    try:
        result = json.loads(node.attributes_json)
        if isinstance(result, dict):
            return result
        logger.warning(
            "C.1: attributes_json for span_id=%s is valid JSON but not a dict "
            "(type=%s); treating as empty.",
            node.node_id,
            type(result).__name__,
        )
        return {}
    except json.JSONDecodeError as exc:
        logger.warning(
            "C.1: attributes_json parse failure for span_id=%s: %s",
            node.node_id,
            exc,
        )
        return {}


def node_to_row(
    node: RuntimeADGNode,
    *,
    snapshot_id: str,
    trace_id: str,
    app_name: str = "",
    route_shape: str = "",
) -> PhaseC1Row:
    """Convert a single ``RuntimeADGNode`` into a ``PhaseC1Row``.

    This is the core Phase C.1 conversion. It applies the 18-field mapping
    defined in the plan §4 and documented in the ``PhaseC1Row`` docstring.

    Parameters
    ----------
    node:
        The span node to convert.
    snapshot_id:
        The ``RuntimeADGSnapshot.snapshot_id`` (SHA-256 hex). Used to build
        ``evidence_source``.
    trace_id:
        The OTel trace ID (snapshot-level). Caller supplies from
        ``snapshot.trace_id``.
    app_name:
        Caller-supplied application name. Takes precedence over
        ``attributes["app_name"]``. May be ``""`` if not yet known.
    route_shape:
        Caller-supplied route shape. Takes precedence over
        ``attributes["route_shape"]``. May be ``""`` if not yet known.

    Returns
    -------
    PhaseC1Row
        A partially-populated row. ``contract_name``, ``normalized_cert_alias``,
        ``manifest_hash``, and ``static_runtime_mode`` are left at their
        fail-closed defaults — Phase C.2 and C.3/C.4/C.5 fill those.

    Notes
    -----
    - ``runtime_certification_status`` is always ``NOT_CERTIFIED``.
    - ``attributes_json`` is parsed once here; downstream helpers see a dict.
    - ``CommitRequest`` spans and all other spans are yielded without filtering —
      C.3/C.4 detect ``FORBIDDEN_SPAN_VIOLATION``.
    """
    attrs = extract_attributes(node)

    # --- app_name: caller kwarg takes precedence; fallback to attribute ---
    resolved_app_name = app_name or _str_attr(attrs, "app_name", "")
    if resolved_app_name and not resolved_app_name.startswith("apps_"):
        logger.debug(
            "C.1: span_id=%s has app_name=%r which does not start with 'apps_'.",
            node.node_id,
            resolved_app_name,
        )

    # --- route_shape: caller kwarg takes precedence; fallback to attribute ---
    resolved_route_shape = route_shape or _str_attr(attrs, "route_shape", "")

    # --- parent_span_id: probe both common attribute key names ---
    parent_span_id: str | None = (
        _str_attr_or_none(attrs, "parent_span_id")
        or _str_attr_or_none(attrs, "parent_id")
    )

    # --- artifact_id: probe artifact_id first, then contract_id ---
    artifact_id: str | None = (
        _str_attr_or_none(attrs, "artifact_id")
        or _str_attr_or_none(attrs, "contract_id")
    )

    # --- contract_id: independent from artifact_id ---
    contract_id: str | None = _str_attr_or_none(attrs, "contract_id")

    # --- source_path: probe code.filepath first, then source_path ---
    source_path: str | None = (
        _str_attr_or_none(attrs, "code.filepath")
        or _str_attr_or_none(attrs, "source_path")
    )

    # --- manifest_hash: from attrs only (C.3/C.4/C.5 back-fill via helper) ---
    manifest_hash: str = _str_attr(attrs, "manifest_hash", "")

    # --- trace_id: snapshot-level is authoritative ---
    node_trace_id = _str_attr_or_none(attrs, "trace_id")
    if node_trace_id and node_trace_id != trace_id:
        logger.warning(
            "C.1: span_id=%s has attributes['trace_id']=%r which differs from "
            "snapshot-level trace_id=%r. Using snapshot-level value.",
            node.node_id,
            node_trace_id,
            trace_id,
        )

    return PhaseC1Row(
        app_name=resolved_app_name,
        route_shape=resolved_route_shape,
        trace_id=trace_id,
        span_id=node.node_id,
        parent_span_id=parent_span_id,
        span_name=node.name,
        timestamp=node.started_at_utc,
        contract_name=None,
        normalized_cert_alias=None,
        manifest_hash=manifest_hash,
        static_runtime_mode="",
        runtime_certification_status=NOT_CERTIFIED,
        artifact_id=artifact_id,
        contract_id=contract_id,
        source_path=source_path,
        attributes=attrs,
        evidence_source=f"{EVIDENCE_SOURCE_PREFIX}{snapshot_id}",
    )


def iter_rows_from_snapshot(
    snapshot: RuntimeADGSnapshot,
    *,
    app_name: str = "",
    route_shape: str = "",
    started_after_ms: int = 0,
    ended_before_ms: int = 0,
) -> Iterator[PhaseC1Row]:
    """Iterate over all span nodes in ``snapshot``, yielding ``PhaseC1Row`` instances.

    Parameters
    ----------
    snapshot:
        The ``RuntimeADGSnapshot`` to iterate.
    app_name:
        Passed through to ``node_to_row``. Overrides any per-node attribute.
    route_shape:
        Passed through to ``node_to_row``. Overrides any per-node attribute.
    started_after_ms:
        If non-zero, only nodes with ``started_at_utc >= started_after_ms``
        are yielded.
    ended_before_ms:
        If non-zero, only nodes with ``started_at_utc < ended_before_ms``
        are yielded.

    Yields
    ------
    PhaseC1Row
        One row per node. Empty snapshot → no rows, no exception.

    Notes
    -----
    - A malformed time window (``started_after_ms > ended_before_ms`` when both
      non-zero) logs a WARNING and applies no time filter (fail-open for time
      bounds only).
    - ``CommitRequest`` and all other spans are yielded without filtering.
    """
    apply_time_filter = False
    if started_after_ms != 0 or ended_before_ms != 0:
        if (
            started_after_ms > 0
            and ended_before_ms > 0
            and started_after_ms >= ended_before_ms
        ):
            logger.warning(
                "C.1: malformed time window started_after_ms=%d >= ended_before_ms=%d; "
                "applying no time filter.",
                started_after_ms,
                ended_before_ms,
            )
        else:
            apply_time_filter = True

    for node in snapshot.nodes:
        if apply_time_filter:
            if started_after_ms > 0 and node.started_at_utc < started_after_ms:
                continue
            if ended_before_ms > 0 and node.started_at_utc >= ended_before_ms:
                continue
        yield node_to_row(
            node,
            snapshot_id=snapshot.snapshot_id,
            trace_id=snapshot.trace_id,
            app_name=app_name,
            route_shape=route_shape,
        )


def iter_rows_for_trace(
    snapshot: RuntimeADGSnapshot,
    trace_id: str,
    *,
    app_name: str = "",
    route_shape: str = "",
) -> Iterator[PhaseC1Row]:
    """Convenience wrapper: yield rows for a specific OTel ``trace_id``.

    When the snapshot was built for a single trace (the common case), this
    is equivalent to ``iter_rows_from_snapshot`` with no time filter. When
    the snapshot contains spans from multiple traces (uncommon), only rows
    whose ``snapshot.trace_id`` or per-node ``attributes["trace_id"]`` matches
    are yielded.

    Parameters
    ----------
    snapshot:
        The ``RuntimeADGSnapshot`` to iterate.
    trace_id:
        The OTel trace ID to filter on.
    app_name:
        Passed through to ``node_to_row``.
    route_shape:
        Passed through to ``node_to_row``.

    Yields
    ------
    PhaseC1Row
        Rows whose effective trace_id matches the requested ``trace_id``.
    """
    if snapshot.trace_id == trace_id:
        yield from iter_rows_from_snapshot(
            snapshot, app_name=app_name, route_shape=route_shape
        )
        return
    # Multi-trace snapshot: filter per-node via attribute.
    for node in snapshot.nodes:
        attrs = extract_attributes(node)
        node_trace = _str_attr_or_none(attrs, "trace_id")
        if node_trace == trace_id:
            yield node_to_row(
                node,
                snapshot_id=snapshot.snapshot_id,
                trace_id=trace_id,
                app_name=app_name,
                route_shape=route_shape,
            )


# ---------------------------------------------------------------------------
# Test-only snapshot builder
# ---------------------------------------------------------------------------


def build_test_snapshot(
    trace_id: str,
    nodes: list[dict[str, Any]],
    *,
    mission: str = "test",
    started_at_utc: int = 0,
    ended_at_utc: int = 1,
) -> RuntimeADGSnapshot:
    """Build a ``RuntimeADGSnapshot`` from raw node dicts — test use only.

    This factory is **not intended for production paths**. It exists to make
    test fixture construction concise without requiring callers to import
    ``create_runtime_adg_snapshot`` directly.

    Parameters
    ----------
    trace_id:
        OTel trace ID for the snapshot.
    nodes:
        List of node dicts. Required keys: ``node_id``, ``name``.
        Optional keys match ``RuntimeADGNode`` fields; all default to safe
        empty values.
    mission:
        Human-readable run label. Defaults to ``"test"``.
    started_at_utc:
        Trace start (Unix ms). Defaults to ``0``.
    ended_at_utc:
        Trace end (Unix ms). Defaults to ``1``.

    Returns
    -------
    RuntimeADGSnapshot
        Immutable, content-addressed snapshot.
    """
    adg_nodes = tuple(
        RuntimeADGNode(
            node_id=n.get("node_id", ""),
            name=n.get("name", ""),
            kind=n.get("kind", ""),
            layer=n.get("layer", ""),
            component=n.get("component", ""),
            started_at_utc=int(n.get("started_at_utc", 0)),
            duration_ms=float(n.get("duration_ms", 0.0)),
            status=n.get("status", "ok"),
            attributes_json=attributes_to_json(n.get("attributes", {}))
            if isinstance(n.get("attributes"), dict)
            else str(n.get("attributes_json", "{}")),
        )
        for n in nodes
    )
    return create_runtime_adg_snapshot(
        trace_id=trace_id,
        mission=mission,
        started_at_utc=started_at_utc,
        ended_at_utc=ended_at_utc,
        nodes=adg_nodes,
        edges=(),
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _str_attr(attrs: dict[str, Any], key: str, default: str) -> str:
    """Return ``attrs[key]`` as a string, or ``default`` if absent/non-string."""
    val = attrs.get(key)
    if val is None:
        return default
    if isinstance(val, str):
        return val
    return str(val)


def _str_attr_or_none(attrs: dict[str, Any], key: str) -> str | None:
    """Return ``attrs[key]`` as a string, or ``None`` if absent or empty."""
    val = attrs.get(key)
    if val is None:
        return None
    s = str(val) if not isinstance(val, str) else val
    return s if s else None


# ---------------------------------------------------------------------------
# Public API surface
# ---------------------------------------------------------------------------

__all__ = [
    "PhaseC1Row",
    "node_to_row",
    "iter_rows_from_snapshot",
    "iter_rows_for_trace",
    "build_test_snapshot",
    "extract_attributes",
    "NOT_CERTIFIED",
    "EVIDENCE_SOURCE_PREFIX",
    "VALID_ROUTE_SHAPES",
    "PHASE_C1_SCHEMA_VERSION",
]
