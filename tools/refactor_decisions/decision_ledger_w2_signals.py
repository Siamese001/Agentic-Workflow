"""W2 decision_signals writer — mirrors emit_packet signal weights (advisory only).

Plan: author-gate-feedback-loop-d4e8f1. Aligns with
``.codex/skills/author-gate-packet-builder/emit_packet.py`` ``_attach_signal_vectors``.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

import sqlite3

from tools.refactor_decisions.ledger_w2_schema import ensure_w2_decision_signal_columns

# Bump when formula / columns change; must match golden tests.
W2_SIGNAL_WRITER_POLICY_VERSION = "ag-signals-w2-writer-20260517"

# Mirror emit_packet._attach_signal_vectors weights (sum = 1.0).
_SIGNAL_WEIGHTS: dict[str, float] = {
    "verbalized": 0.15,
    "precedent_agreement": 0.30,
    "blast_radius_penalty": 0.20,
    "hotspot_penalty": 0.15,
    "rule_violation_penalty": 0.20,
}

# Capture-time mapping: ledger precedent verdict -> [0,1] for recommended option.
_VERDICT_TO_PRECEDENT: dict[str, float] = {
    "strong": 0.85,
    "suggestive": 0.65,
    "none": 0.35,
}
# Public alias for golden tests / tooling (must stay aligned with emit_packet defaults).
PRECEDENT_AGREEMENT_BY_VERDICT: dict[str, float] = dict(_VERDICT_TO_PRECEDENT)
_DEFAULT_PRECEDENT_AGREEMENT = 0.5


def stable_option_key(label: str, index: int) -> str:
    """Stable option_id aligned with packet candidate ``id`` (deterministic)."""
    norm = (label or "").strip().lower()
    h = hashlib.sha1(f"{index}|{norm}".encode("utf-8")).hexdigest()[:10]
    return f"o{index}_{h}"


def _coerce_optional_int(val: object | None) -> int | None:
    if val is None:
        return None
    if isinstance(val, int):
        return val
    try:
        return int(val)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        try:
            return int(float(val))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return None


def _precedent_agreement_for_option(
    *,
    label: str,
    recommended_label: str | None,
    merged_verdict: str | None,
    meta: dict[str, Any] | None,
) -> tuple[float, str, str]:
    """Return (value, signal_source, source_ref JSON).

    ``signal_source`` is ``capture_hook`` when using W1 capture metadata;
    ``replayed_lookup`` when lookup pipeline did not return a verdict JSON.
    """
    meta = meta or {}
    lookup_ok = bool(meta.get("precedent_lookup_ok"))
    digest = (meta.get("precedent_lookup_query_digest") or "")[:128]
    top_ids = meta.get("precedent_top_match_ids_json") or "[]"

    is_primary = bool(recommended_label) and label.strip() == recommended_label.strip()
    if not is_primary:
        ref = json.dumps(
            {"digest": digest or None, "basis": "non_recommended_default"},
            sort_keys=True,
            separators=(",", ":"),
        )
        return _DEFAULT_PRECEDENT_AGREEMENT, "capture_hook", ref

    pv = (merged_verdict or "").strip().lower()
    if pv in _VERDICT_TO_PRECEDENT:
        val = _VERDICT_TO_PRECEDENT[pv]
        basis = "verdict_primary"
    elif lookup_ok and pv == "":
        val = _DEFAULT_PRECEDENT_AGREEMENT
        basis = "lookup_ok_no_verdict"
    elif not lookup_ok and meta.get("precedent_verdict_from_lookup") is None:
        val = _VERDICT_TO_PRECEDENT.get(pv, _DEFAULT_PRECEDENT_AGREEMENT)
        basis = "fallback_no_lookup_pipeline"
    else:
        val = _DEFAULT_PRECEDENT_AGREEMENT
        basis = "unknown_verdict"

    lookup_verdict = meta.get("precedent_verdict_from_lookup")
    src = "capture_hook" if (lookup_ok or basis == "verdict_primary") else "replayed_lookup"
    if basis == "fallback_no_lookup_pipeline":
        src = "replayed_lookup"
    ref_obj = {
        "digest": digest or None,
        "top_match_ids_json": top_ids[:500],
        "basis": basis,
        "merged_verdict": pv or None,
        "lookup_verdict": lookup_verdict,
        "lookup_reason": (meta.get("precedent_lookup_reason") if meta else None),
    }
    return val, src, json.dumps(ref_obj, sort_keys=True, separators=(",", ":"))


def _signal_values_for_option(
    *,
    label: str,
    recommended_label: str | None,
    merged_verdict: str | None,
    meta: dict[str, Any] | None,
    verbalized: float,
    blast_radius_hops: int | None,
    adg_hotspot_rank: int | None,
    adg_hotspot_top_n: int,
    rule_flagged: bool,
) -> tuple[dict[str, float], str, str]:
    """Return (signals dict, precedent_source, precedent_ref)."""
    prec, prec_src, prec_ref = _precedent_agreement_for_option(
        label=label,
        recommended_label=recommended_label,
        merged_verdict=merged_verdict,
        meta=meta,
    )
    if blast_radius_hops is None:
        blast = 1.0
    else:
        try:
            blast = 1.0 - min(float(blast_radius_hops) / 5.0, 1.0)
        except (TypeError, ValueError):
            blast = 1.0
    if adg_hotspot_rank is None:
        hspot = 1.0
    else:
        try:
            hspot = max(0.0, 1.0 - (float(adg_hotspot_rank) / float(adg_hotspot_top_n)))
        except (TypeError, ValueError):
            hspot = 1.0
    rule = 0.0 if rule_flagged else 1.0
    signals = {
        "verbalized": float(verbalized),
        "precedent_agreement": float(prec),
        "blast_radius_penalty": float(blast),
        "hotspot_penalty": float(hspot),
        "rule_violation_penalty": float(rule),
    }
    return signals, prec_src, prec_ref


def replace_decision_signals_for_capture(
    conn: sqlite3.Connection,
    decision_id: str,
    option_labels: list[str],
    *,
    recommended_label: str | None,
    merged_verdict: str | None,
    meta: dict[str, Any] | None,
    v2: dict[str, Any] | None = None,
) -> None:
    """Delete existing signal rows for ``decision_id`` and insert W2 rows (fail-soft)."""
    v2 = v2 or {}
    try:
        ensure_w2_decision_signal_columns(conn)
        conn.execute("DELETE FROM decision_signals WHERE decision_id = ?", (decision_id,))
        hop_i = _coerce_optional_int(v2.get("blast_radius_hops"))
        hrank_i = _coerce_optional_int(v2.get("adg_hotspot_rank"))
        top_n = 100
        flagged: set[str] = set()
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        meta = meta or {}

        for idx, label in enumerate(option_labels):
            oid = stable_option_key(label, idx)
            verbal = (
                0.85 if recommended_label and label.strip() == recommended_label.strip() else 0.5
            )
            signals, prec_src, prec_ref = _signal_values_for_option(
                label=label,
                recommended_label=recommended_label,
                merged_verdict=merged_verdict,
                meta=meta,
                verbalized=verbal,
                blast_radius_hops=hop_i,
                adg_hotspot_rank=hrank_i,
                adg_hotspot_top_n=top_n,
                rule_flagged=oid in flagged,
            )
            for sname, sval in signals.items():
                if sname == "precedent_agreement":
                    src, ref = prec_src, prec_ref
                else:
                    src = "capture_hook"
                    ref = json.dumps(
                        {
                            "digest": meta.get("precedent_lookup_query_digest"),
                            "option_index": idx,
                            "signal": sname,
                        },
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                wt = _SIGNAL_WEIGHTS.get(sname, 0.0)
                conn.execute(
                    """INSERT INTO decision_signals
                        (decision_id, option_id, signal_name, signal_value, signal_weight,
                         signal_source, source_ref, policy_version, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        decision_id,
                        oid,
                        sname,
                        float(sval),
                        float(wt),
                        src,
                        ref[:2000],
                        W2_SIGNAL_WRITER_POLICY_VERSION,
                        ts,
                    ),
                )
        conn.commit()
    except sqlite3.Error:
        # guardian: allow-silent-swallow -- advisory signals; capture must not fail
        pass


def signals_dict_for_options(
    option_labels: list[str],
    *,
    recommended_label: str | None,
    merged_verdict: str | None,
    meta: dict[str, Any] | None,
    v2: dict[str, Any] | None = None,
) -> dict[str, dict[str, float]]:
    """Test helper: option_id -> signal_name -> value (no DB)."""
    v2 = v2 or {}
    hop_i = _coerce_optional_int(v2.get("blast_radius_hops"))
    hrank_i = _coerce_optional_int(v2.get("adg_hotspot_rank"))
    out: dict[str, dict[str, float]] = {}
    meta = meta or {}
    for idx, label in enumerate(option_labels):
        oid = stable_option_key(label, idx)
        verbal = (
            0.85 if recommended_label and label.strip() == recommended_label.strip() else 0.5
        )
        signals, _, _ = _signal_values_for_option(
            label=label,
            recommended_label=recommended_label,
            merged_verdict=merged_verdict,
            meta=meta,
            verbalized=verbal,
            blast_radius_hops=hop_i,
            adg_hotspot_rank=hrank_i,
            adg_hotspot_top_n=100,
            rule_flagged=False,
        )
        out[oid] = signals
    return out
