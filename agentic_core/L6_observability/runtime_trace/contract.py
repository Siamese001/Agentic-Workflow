"""Runtime trace contract — loader, model, and validator.

Loads YAML contracts from ``config/runtime_trace/contracts/`` and validates
collected OTEL span graphs against them. Pure-Python; no MCP dependencies.

Contract schema: see ``config/runtime_trace/README.md``.

Example::

    from agentic_core.L6_observability.runtime_trace import (
        load_contract, validate_trace,
    )

    contract = load_contract("canary.lic.v1")
    spans = collect_spans_from_trace_id("abc123")  # caller's responsibility
    result = validate_trace(contract, spans)
    if not result.ok:
        for v in result.violations:
            print(v.kind, v.detail)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

# Layer-skip detection — ordered layer-rank map. Cross-layer skip means a
# child span is at layer L_n with a parent at layer L_(n+2) or further.
_LAYER_RANK: Mapping[str, int] = {
    "L0": 0,
    "L1": 1,
    "L2": 2,
    "L3": 3,
    "L4": 4,
    "L5": 5,
    "L6": 6,
}

# Default registry root. Tests may override.
_DEFAULT_CONTRACT_ROOT = Path(__file__).resolve().parents[3] / "config" / "runtime_trace" / "contracts"


class ContractValidationError(Exception):
    """Raised when a contract file is malformed at load time."""


@dataclass(frozen=True)
class RequiredSpan:
    """A span that MUST appear in the trace."""

    name: str
    layer: str
    parent: str | None
    attributes: tuple[str, ...] = ()
    optional_attributes: tuple[str, ...] = ()


@dataclass(frozen=True)
class RequiredEdge:
    """A semantic or parent/child edge that MUST exist between two spans."""

    from_span: str
    to_span: str
    kind: str  # parent_child | writes_to | flows_to | emits_side_effect


@dataclass(frozen=True)
class RuntimeTraceContract:
    """In-memory representation of a runtime trace contract YAML."""

    contract_id: str
    version: int
    description: str
    required_spans: tuple[RequiredSpan, ...]
    required_edges: tuple[RequiredEdge, ...]
    forbidden: tuple[str, ...]
    invariant_attributes: tuple[str, ...]


@dataclass(frozen=True)
class Violation:
    """A single contract violation found in a trace."""

    kind: str  # e.g., "missing_span", "wrong_parent", "cross_layer_skip"
    detail: str  # human-readable specifics
    span_name: str | None = None


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of validating a span graph against a contract."""

    ok: bool
    contract_id: str
    violations: tuple[Violation, ...] = field(default_factory=tuple)
    spans_seen: int = 0


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def load_contract(
    contract_id: str,
    *,
    root: Path | str | None = None,
) -> RuntimeTraceContract:
    """Load a contract by ID from the registry.

    Args:
        contract_id: e.g., ``"canary.lic.v1"``.
        root: optional override for the contract registry root (test injection).

    Returns:
        Parsed :class:`RuntimeTraceContract`.

    Raises:
        FileNotFoundError: contract file does not exist.
        ContractValidationError: contract YAML is malformed.
    """
    registry_root = Path(root) if root is not None else _DEFAULT_CONTRACT_ROOT
    filename = contract_id.replace(".", "_") + ".yaml"
    path = registry_root / filename
    if not path.is_file():
        raise FileNotFoundError(f"runtime_trace_contract_unresolved: {contract_id} (expected {path})")

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ContractValidationError(f"contract {contract_id}: invalid YAML: {exc}") from exc

    if not isinstance(raw, dict):
        raise ContractValidationError(f"contract {contract_id}: top-level must be a mapping")

    if raw.get("contract_id") != contract_id:
        raise ContractValidationError(
            f"contract_id mismatch: file declares {raw.get('contract_id')!r}, requested {contract_id!r}"
        )

    version = raw.get("version")
    if version != 1:
        raise ContractValidationError(f"contract {contract_id}: unsupported version {version!r} (only 1)")

    return RuntimeTraceContract(
        contract_id=contract_id,
        version=version,
        description=str(raw.get("description", "")).strip(),
        required_spans=tuple(_parse_required_span(s) for s in raw.get("required_spans") or ()),
        required_edges=tuple(_parse_required_edge(e) for e in raw.get("required_edges") or ()),
        forbidden=tuple(str(f) for f in raw.get("forbidden") or ()),
        invariant_attributes=tuple(str(a) for a in raw.get("invariant_attributes") or ()),
    )


def _parse_required_span(raw: Mapping[str, Any]) -> RequiredSpan:
    name = raw.get("name")
    layer = raw.get("layer")
    if not isinstance(name, str) or not isinstance(layer, str):
        raise ContractValidationError(f"required_spans entry missing name/layer: {raw!r}")
    if layer not in _LAYER_RANK:
        raise ContractValidationError(
            f"span {name!r}: unknown layer {layer!r} (expected one of {sorted(_LAYER_RANK)})"
        )
    parent = raw.get("parent")
    if parent is not None and not isinstance(parent, str):
        raise ContractValidationError(f"span {name!r}: parent must be string or null")
    return RequiredSpan(
        name=name,
        layer=layer,
        parent=parent,
        attributes=tuple(str(a) for a in raw.get("attributes") or ()),
        optional_attributes=tuple(str(a) for a in raw.get("optional_attributes") or ()),
    )


def _parse_required_edge(raw: Mapping[str, Any]) -> RequiredEdge:
    from_span = raw.get("from")
    to_span = raw.get("to")
    kind = raw.get("kind")
    if not (isinstance(from_span, str) and isinstance(to_span, str) and isinstance(kind, str)):
        raise ContractValidationError(f"required_edges entry malformed: {raw!r}")
    valid_kinds = {"parent_child", "writes_to", "flows_to", "emits_side_effect"}
    if kind not in valid_kinds:
        raise ContractValidationError(
            f"edge {from_span}->{to_span}: unknown kind {kind!r} (expected one of {sorted(valid_kinds)})"
        )
    return RequiredEdge(from_span=from_span, to_span=to_span, kind=kind)


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------


def validate_trace(
    contract: RuntimeTraceContract,
    spans: Sequence[Mapping[str, Any]],
) -> ValidationResult:
    """Validate a collected span graph against a contract.

    Args:
        contract: parsed contract.
        spans: list of span dicts. Each span must have at minimum:
            ``name`` (str), ``layer`` (str | None),
            ``parent_name`` (str | None), ``attributes`` (Mapping),
            and may have ``status`` (e.g., "ok"/"error") and
            ``edges`` (list of {to, kind}).

    Returns:
        :class:`ValidationResult` with ``ok`` reflecting clean validation.
    """
    violations: list[Violation] = []
    by_name: dict[str, Mapping[str, Any]] = {}
    for span in spans:
        name = span.get("name")
        if isinstance(name, str):
            by_name[name] = span

    # 1. Required spans present, with correct layer and parent.
    for req in contract.required_spans:
        actual = by_name.get(req.name)
        if actual is None:
            violations.append(Violation("missing_span", f"required span {req.name!r} not found", req.name))
            continue
        actual_layer = actual.get("layer")
        if actual_layer != req.layer:
            violations.append(
                Violation(
                    "wrong_layer",
                    f"span {req.name!r}: expected layer {req.layer!r}, got {actual_layer!r}",
                    req.name,
                )
            )
        actual_parent = actual.get("parent_name")
        if req.parent != actual_parent:
            violations.append(
                Violation(
                    "wrong_parent",
                    f"span {req.name!r}: expected parent {req.parent!r}, got {actual_parent!r}",
                    req.name,
                )
            )
        attrs = actual.get("attributes") or {}
        for required_attr in req.attributes:
            if required_attr not in attrs:
                violations.append(
                    Violation(
                        "missing_attribute",
                        f"span {req.name!r}: missing required attribute {required_attr!r}",
                        req.name,
                    )
                )

    # 2. Required edges present.
    for req_edge in contract.required_edges:
        src = by_name.get(req_edge.from_span)
        if src is None:
            # Already flagged as missing_span; skip edge check.
            continue
        if req_edge.kind == "parent_child":
            dst = by_name.get(req_edge.to_span)
            if dst is None or dst.get("parent_name") != req_edge.from_span:
                violations.append(
                    Violation(
                        "missing_edge",
                        f"parent_child edge {req_edge.from_span} -> {req_edge.to_span} not present",
                        req_edge.from_span,
                    )
                )
            continue
        # Semantic edges live on the source span's `edges` list.
        edges = src.get("edges") or ()
        if not _has_semantic_edge(edges, req_edge.to_span, req_edge.kind):
            violations.append(
                Violation(
                    "missing_edge",
                    f"semantic edge {req_edge.from_span} --[{req_edge.kind}]--> "
                    f"{req_edge.to_span} not present",
                    req_edge.from_span,
                )
            )

    # 3. Forbidden invariants.
    if "cross_layer_skip" in contract.forbidden:
        violations.extend(_check_cross_layer_skip(spans))
    if "direct_l4_write_outside_uwg" in contract.forbidden:
        violations.extend(_check_direct_l4_write(spans))
    if "swallowed_exception" in contract.forbidden:
        violations.extend(_check_swallowed_exception(spans))
    if "missing_trace_id_attribute" in contract.forbidden:
        violations.extend(_check_missing_trace_id(spans))

    # 4. Invariant attributes consistent across all spans.
    for inv_attr in contract.invariant_attributes:
        seen_values: set[Any] = set()
        for span in spans:
            attrs = span.get("attributes") or {}
            if inv_attr in attrs:
                seen_values.add(attrs[inv_attr])
        if len(seen_values) > 1:
            violations.append(
                Violation(
                    "invariant_attribute_drift",
                    f"attribute {inv_attr!r} has multiple distinct values "
                    f"across trace: {sorted(map(repr, seen_values))}",
                )
            )

    return ValidationResult(
        ok=len(violations) == 0,
        contract_id=contract.contract_id,
        violations=tuple(violations),
        spans_seen=len(spans),
    )


# ---------------------------------------------------------------------------
# Forbidden-invariant checks
# ---------------------------------------------------------------------------


def _has_semantic_edge(
    edges: Sequence[Mapping[str, Any]],
    to_span: str,
    kind: str,
) -> bool:
    for edge in edges:
        if edge.get("to") == to_span and edge.get("kind") == kind:
            return True
    return False


def _check_cross_layer_skip(spans: Sequence[Mapping[str, Any]]) -> list[Violation]:
    out: list[Violation] = []
    by_name = {s.get("name"): s for s in spans if isinstance(s.get("name"), str)}
    for span in spans:
        layer = span.get("layer")
        parent_name = span.get("parent_name")
        if not isinstance(layer, str) or not isinstance(parent_name, str):
            continue
        if layer not in _LAYER_RANK:
            continue
        parent = by_name.get(parent_name)
        if parent is None:
            continue
        parent_layer = parent.get("layer")
        if not isinstance(parent_layer, str) or parent_layer not in _LAYER_RANK:
            continue
        # UWG-boundary exemption: spans named ``uwg.*`` are the canonical
        # exit-write boundary and are allowed to attach above their parent's
        # layer (e.g., ``exit.disposition`` at L2 -> ``uwg.commit`` at L4).
        span_name = span.get("name")
        if isinstance(span_name, str) and span_name.startswith("uwg."):
            continue
        # Skip = child layer is more than 1 step above parent layer.
        if _LAYER_RANK[layer] - _LAYER_RANK[parent_layer] >= 2:
            out.append(
                Violation(
                    "cross_layer_skip",
                    f"span {span.get('name')!r} at {layer} has parent "
                    f"{parent_name!r} at {parent_layer} (skip ≥ 2 layers)",
                    span.get("name"),
                )
            )
    return out


def _check_direct_l4_write(spans: Sequence[Mapping[str, Any]]) -> list[Violation]:
    out: list[Violation] = []
    by_name = {s.get("name"): s for s in spans if isinstance(s.get("name"), str)}
    for span in spans:
        layer = span.get("layer")
        if layer != "L4":
            continue
        attrs = span.get("attributes") or {}
        is_write = bool(attrs.get("write")) or "write" in (span.get("name") or "").lower()
        if not is_write:
            continue
        # The UWG span itself is the canonical write boundary; it does not
        # need a UWG parent.
        own_name = span.get("name") or ""
        if isinstance(own_name, str) and (own_name.startswith("uwg.") or attrs.get("uwg") is True):
            continue
        # L4 writes must have a parent that is a UWG span.
        parent_name = span.get("parent_name") or ""
        parent = by_name.get(parent_name)
        is_uwg = parent_name.startswith("uwg.") or (
            parent is not None and (parent.get("attributes") or {}).get("uwg") is True
        )
        if not is_uwg:
            out.append(
                Violation(
                    "direct_l4_write_outside_uwg",
                    f"L4 write span {span.get('name')!r} has non-UWG parent {parent_name!r}",
                    span.get("name"),
                )
            )
    return out


def _check_swallowed_exception(spans: Sequence[Mapping[str, Any]]) -> list[Violation]:
    """Flag spans with status=error that have no recover.* sibling.

    A genuine recovery emits a sibling span named ``recover.*``. An error
    span followed by a clean ``ok`` continuation with no recovery span is a
    swallowed exception.
    """
    out: list[Violation] = []
    by_parent: dict[str | None, list[Mapping[str, Any]]] = {}
    for span in spans:
        by_parent.setdefault(span.get("parent_name"), []).append(span)
    for span in spans:
        if span.get("status") != "error":
            continue
        siblings = by_parent.get(span.get("parent_name"), [])
        has_recover = any((sib.get("name") or "").startswith("recover.") for sib in siblings)
        if not has_recover:
            out.append(
                Violation(
                    "swallowed_exception",
                    f"span {span.get('name')!r} status=error with no recover.* sibling",
                    span.get("name"),
                )
            )
    return out


def _check_missing_trace_id(spans: Sequence[Mapping[str, Any]]) -> list[Violation]:
    out: list[Violation] = []
    for span in spans:
        attrs = span.get("attributes") or {}
        if "trace_id" not in attrs:
            out.append(
                Violation(
                    "missing_trace_id_attribute",
                    f"span {span.get('name')!r} missing trace_id attribute",
                    span.get("name"),
                )
            )
    return out
