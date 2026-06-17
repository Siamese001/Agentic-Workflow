"""apps_shared.cert.rubric_output_mapper — declarative YAML engine.

W2.P1 of plan ``.claude/plans/apps-runtime-domain-enforcement-a7e9d4.md``.

Per Author-Gate decision AG-W2-mapper-scope (Option B, 2026-05-03):
declarative YAML per app beats per-app Python boilerplate. Each runtime
app declares its (rubric dimension -> L2-receipt extractor) mapping in
``<app>/config/domain_contract/rubric_output_map.yaml``; this engine
resolves it at cert time and builds the canonical
``{dim_scores: {...}, dim_evidence: {...}}`` dict that
:class:`agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator.AppSpecificEvaluator`
consumes via ``read_dim_score_from_output``.

Extractor DSL
-------------
Each dimension entry:

.. code-block:: yaml

    - dimension_id: factual_grounding
      score:
        type: jsonpath | literal | count_nonempty | presence | all_present
        path: $.output.grounding.score     # for jsonpath / presence / count_nonempty
        paths: [$.a.b, $.c.d]              # for all_present
        value: 1.0                         # for literal
        default: 0.0                       # returned when path is unresolvable
        clamp: [0.0, 1.0]                  # optional — clamp into range
      evidence:
        - literal: "scorer=deterministic"  # static string
        - jsonpath: $.output.evidence_refs.factual  # extract list or scalar (stringified)
        - template: "resume_length={$.output.resume.length}"

Evaluators
----------
- ``jsonpath``     : Resolve a ``$.`` -prefixed path against the receipt dict.
                     Returns the value (coerced to float for score; stringified
                     for evidence). Missing path -> ``default``.
- ``literal``      : Fixed ``value`` (for score) or ``literal`` string (evidence).
- ``count_nonempty``: Resolve path; if result is a list, count non-empty entries;
                     normalize by ``normalize_by`` (default 1). 0.0 if missing.
- ``presence``     : 1.0 iff path resolves to a non-None non-empty value, else 0.0.
- ``all_present``  : 1.0 iff ALL listed ``paths`` resolve to non-empty values,
                     else 0.0.
- ``template``     : (evidence only) substitute ``{$.path}`` tokens into a
                     format string.

Fail-soft contract
------------------
This engine NEVER raises. Any YAML parse error, path resolution error, or
extractor misuse returns ``default=0.0`` for score and ``[]`` for evidence,
and logs a warning. The downstream AppSpecificEvaluator treats missing
dim_scores as UNKNOWN (fail-closed per rubric config) — so mapper bugs
CANNOT produce false-positive PASS verdicts.

Security
--------
JSONPath subset is deliberately minimal: only ``$.`` + ``[idx]`` +
``.key``. No filter expressions, no scripts, no function calls. This is
a config-driven extractor, not an eval engine.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

_LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Minimal JSONPath resolver
# ---------------------------------------------------------------------------
_PATH_TOKEN = re.compile(r"\.([A-Za-z_][A-Za-z0-9_]*)|\[(-?\d+)\]")
_TEMPLATE_TOKEN = re.compile(r"\{(\$[^\}]+)\}")


def _resolve_jsonpath(path: str, data: Any) -> Any | None:
    """Resolve ``$.a.b[0].c`` against ``data``; None on miss."""
    if not isinstance(path, str) or not path.startswith("$"):
        return None
    cursor: Any = data
    pos = 1  # skip '$'
    while pos < len(path):
        m = _PATH_TOKEN.match(path, pos)
        if not m:
            return None
        pos = m.end()
        key, idx = m.group(1), m.group(2)
        if key is not None:
            if not isinstance(cursor, Mapping) or key not in cursor:
                return None
            cursor = cursor[key]
        else:
            try:
                i = int(idx)
                cursor = cursor[i]
            except (TypeError, IndexError, KeyError, ValueError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
                return None
    return cursor


def _is_nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (str, bytes, list, tuple, dict, set)):
        return len(value) > 0
    return True


def _coerce_float(value: Any, default: float) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


def _clamp(value: float, bounds: Iterable[float] | None) -> float:
    if not bounds:
        return value
    try:
        lo, hi = [float(b) for b in bounds]
    except (TypeError, ValueError):
        return value
    return max(lo, min(hi, value))


# ---------------------------------------------------------------------------
# Score / evidence extractors
# ---------------------------------------------------------------------------
def _extract_score(spec: Mapping[str, Any] | None, receipt: Mapping[str, Any]) -> float:
    if not isinstance(spec, Mapping):
        return 0.0
    kind = spec.get("type", "literal")
    default = _coerce_float(spec.get("default", 0.0), 0.0)
    clamp = spec.get("clamp")
    try:
        if kind == "literal":
            return _clamp(_coerce_float(spec.get("value", default), default), clamp)
        if kind == "jsonpath":
            val = _resolve_jsonpath(spec.get("path", ""), receipt)
            if val is None:
                return _clamp(default, clamp)
            return _clamp(_coerce_float(val, default), clamp)
        if kind == "presence":
            val = _resolve_jsonpath(spec.get("path", ""), receipt)
            return _clamp(1.0 if _is_nonempty(val) else 0.0, clamp)
        if kind == "count_nonempty":
            val = _resolve_jsonpath(spec.get("path", ""), receipt)
            if not isinstance(val, (list, tuple)):
                return _clamp(default, clamp)
            count = sum(1 for v in val if _is_nonempty(v))
            norm = _coerce_float(spec.get("normalize_by", 1.0), 1.0) or 1.0
            return _clamp(count / norm, clamp)
        if kind == "all_present":
            paths = spec.get("paths") or []
            if not paths:
                return _clamp(default, clamp)
            ok = all(_is_nonempty(_resolve_jsonpath(p, receipt)) for p in paths)
            return _clamp(1.0 if ok else 0.0, clamp)
    except Exception as exc:  # noqa: BLE001  # guardian: allow-log-and-swallow -- P2 burndown: fail-soft optional boundary  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        # guardian: allow-broad-except -- mapper MUST be fail-soft;
        # any extraction error yields default (fail-closed downstream)
        _LOGGER.warning(
            "[rubric_output_mapper] score extractor kind=%s raised %s: %s",
            kind, type(exc).__name__, exc,
        )
    return _clamp(default, clamp)


def _render_template(template: str, receipt: Mapping[str, Any]) -> str:
    def _sub(match: re.Match[str]) -> str:
        val = _resolve_jsonpath(match.group(1), receipt)
        return "" if val is None else str(val)
    return _TEMPLATE_TOKEN.sub(_sub, template)


def _extract_evidence(
    specs: Iterable[Mapping[str, Any]] | None, receipt: Mapping[str, Any]
) -> list[str]:
    if not specs:
        return []
    out: list[str] = []
    for spec in specs:
        if not isinstance(spec, Mapping):
            continue
        try:
            if "literal" in spec:
                out.append(str(spec["literal"]))
            elif "jsonpath" in spec:
                val = _resolve_jsonpath(spec["jsonpath"], receipt)
                if val is None:
                    continue
                prefix = str(spec.get("prefix", ""))
                if isinstance(val, (list, tuple)):
                    out.extend(f"{prefix}{v}" for v in val if _is_nonempty(v))
                else:
                    out.append(f"{prefix}{val}")
            elif "template" in spec:
                out.append(_render_template(str(spec["template"]), receipt))
        except Exception as exc:  # noqa: BLE001  # guardian: allow-log-and-swallow -- P2 burndown: fail-soft optional boundary  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            # guardian: allow-broad-except -- evidence extraction is fail-soft;
            # empty evidence on a required dim still triggers fail-closed per
            # evidence_required=true in the rubric
            _LOGGER.warning(
                "[rubric_output_mapper] evidence extractor raised %s: %s",
                type(exc).__name__, exc,
            )
    return out


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def map_l2_receipt_to_dim_scores(
    l2_receipt: Mapping[str, Any],
    mapper_yaml_path: Path | str,
) -> dict[str, Any]:
    """Build ``{dim_scores, dim_evidence}`` from an L2 receipt + YAML map.

    Fail-soft: returns ``{"dim_scores": {}, "dim_evidence": {}}`` when the
    YAML is missing, unreadable, or malformed. Callers should merge the
    returned dict into the ``output`` slot of the ExitReviewPacket
    receipts::

        receipts["output"] = {
            **existing_output,
            **map_l2_receipt_to_dim_scores(l2_receipt, map_yaml_path),
        }

    The AppSpecificEvaluator reads ``dim_scores[dim_id]`` via
    ``read_dim_score_from_output`` and ``dim_evidence[dim_id]`` as the
    evidence_refs list.
    """
    try:
        import yaml  # noqa: PLC0415
    except ImportError:  # pragma: no cover
        _LOGGER.warning("[rubric_output_mapper] PyYAML unavailable")
        return {"dim_scores": {}, "dim_evidence": {}}
    path = Path(mapper_yaml_path)
    if not path.exists():
        _LOGGER.warning("[rubric_output_mapper] map missing: %s", path)
        return {"dim_scores": {}, "dim_evidence": {}}
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        # guardian: allow-broad-except -- YAML load failure MUST NOT break
        # the cert path; evaluator will see empty dim_scores and fail-close
        _LOGGER.warning(
            "[rubric_output_mapper] YAML load failed for %s: %s", path, exc,
        )
        return {"dim_scores": {}, "dim_evidence": {}}
    dims = doc.get("dimensions") if isinstance(doc, Mapping) else None
    if not isinstance(dims, list):
        _LOGGER.warning(
            "[rubric_output_mapper] no 'dimensions' list in %s", path,
        )
        return {"dim_scores": {}, "dim_evidence": {}}
    scores: dict[str, float] = {}
    evidence: dict[str, list[str]] = {}
    for entry in dims:
        if not isinstance(entry, Mapping):
            continue
        dim_id = entry.get("dimension_id")
        if not isinstance(dim_id, str) or not dim_id:
            continue
        scores[dim_id] = _extract_score(entry.get("score"), l2_receipt)
        evidence[dim_id] = _extract_evidence(entry.get("evidence"), l2_receipt)
    return {"dim_scores": scores, "dim_evidence": evidence}


__all__ = ["map_l2_receipt_to_dim_scores"]
