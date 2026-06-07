#!/usr/bin/env python3
"""render_card.py — Render an Author-Gate recommendation card + enriched options.

Plan: `.claude/plans/author-gate-hardening-a3b8f2.md` W3.P3.2.

Reads an AUTHOR_GATE_PACKET JSON (the `{...}` body, without the marker prefix)
on stdin and prints:

1. A 6-line recommendation card (plus ≤2 alternatives) to stdout
2. A line `OPTIONS_JSON: [...]` carrying enriched {label, description} dicts
   the caller should pass directly to ``ask_user_question``

Usage:
    cat packet.json | python .claude/skills/author-gate-ui-renderer/render_card.py

Fail policy: exits 2 on unparseable stdin; exits 0 otherwise (fail-soft).
"""

from __future__ import annotations

import json
import sys
from typing import Any


def _confidence_pill(score: float) -> str:
    if score >= 0.85:
        return "🟢"
    if score >= 0.72:
        return "🟡"
    return "🔴"


def _one_line(s: str, width: int = 80) -> str:
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= width else (s[: width - 1] + "…")


def _thesis(opt: dict[str, Any]) -> str:
    return _one_line(opt.get("thesis") or opt.get("id") or "")


def render_card(packet: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
    """Return (card_text, options_for_ask_user_question)."""
    candidates = [c for c in packet.get("candidates") or [] if c.get("surfaced")]
    candidates.sort(key=lambda c: float(c.get("confidence_score", 0)), reverse=True)
    routing = packet.get("routing") or {}
    rule = routing.get("rule_applied", "unknown")
    precedent = (packet.get("precedent") or {}).get("verdict", "none")
    match_count = (packet.get("precedent") or {}).get("match_count") or \
                  len((packet.get("precedent") or {}).get("matched_ids") or [])

    lines: list[str] = []
    if not candidates:
        lines.append("⚠️ No surfaced candidates — nothing to recommend.")
        return "\n".join(lines), []

    top = candidates[0]
    top_score = float(top.get("confidence_score", 0))
    pill_top = _confidence_pill(top_score)

    if top.get("is_recommended"):
        recommended_header = f"🎯 Recommended: {top.get('id')} — {_thesis(top)}"
    elif rule == "dominance_fires":
        recommended_header = f"🎯 Recommended: {top.get('id')} — {_thesis(top)}"
    else:
        recommended_header = (
            f"⚠️ Leading option (not dominant): {top.get('id')} — "
            f"score {top_score:.2f} (rule={rule}). Pick in UI below."
        )
    lines.append(recommended_header)
    lines.append(
        f"   Confidence:  {pill_top} {top_score:.2f} "
        f"(calibrated={bool(packet.get('calibrator_version'))}, n={match_count} precedents)"
    )
    lines.append(
        f"   Why:         {_one_line(top.get('principle_at_stake') or '—', 60)} · precedent: {precedent}"
    )
    wwf = top.get("what_would_flip") or ""
    if isinstance(wwf, list):
        wwf_top2 = "; ".join(wwf[:2])
    else:
        wwf_top2 = _one_line(wwf, 100)
    lines.append(f"   Would flip:  {wwf_top2 or '—'}")

    # Blast / hotspot / surfaces (all best-effort from packet)
    hops = packet.get("blast_radius_hops") or "n/a"
    rank = packet.get("adg_hotspot_rank") or "n/a"
    surfaces = packet.get("surface_intersections_json") or "[]"
    try:
        surfaces_str = ",".join(json.loads(surfaces)) if surfaces else "n/a"
    except (TypeError, json.JSONDecodeError):
        surfaces_str = "n/a"
    lines.append(f"   Blast:       {hops} hops · hotspot rank #{rank} · surfaces: {surfaces_str or 'n/a'}")

    palette = packet.get("reason_code_palette") or []
    if palette:
        lines.append("   Reason-code palette (pick ONE if overriding):")
        # Compact two-column layout
        per_line = 3
        for i in range(0, len(palette), per_line):
            lines.append("     " + " | ".join(palette[i : i + per_line]))

    if len(candidates) > 1:
        lines.append("")
        lines.append("📋 Alternatives:")
        for alt in candidates[1:3]:
            s = float(alt.get("confidence_score", 0))
            lines.append(f"   • {alt.get('id')}: {_confidence_pill(s)} {s:.2f} — {_thesis(alt)}")

    # Build ask_user_question options (≤4).
    #
    # Plan author-gate-four-req-enforcement-c4d2a8 W1.P2:
    # The CANONICAL description is `candidate.surface_description` minted by
    # emit_packet.py — it carries the four-requirement floor (confidence prefix,
    # optional ⭐ for dominance, and a · trade-off: <text> segment that
    # post_cursor_agent_author_gate_ui_audit.py invariant 4 enforces).
    # Renderer falls through floor → prefix → locally-built description for
    # back-compat with older packets emitted before this plan.
    options: list[dict[str, str]] = []
    for i, opt in enumerate(candidates[:4]):
        canonical_desc = opt.get("surface_description") or opt.get("surface_description_floor")
        if isinstance(canonical_desc, str) and canonical_desc.strip():
            description = canonical_desc.strip()
        else:
            # Legacy fallback path — pre-W1.P1 packets.
            s = float(opt.get("confidence_score", 0))
            pill = _confidence_pill(s)
            is_rec = bool(opt.get("is_recommended")) or (i == 0)
            tag = "recommended · " if is_rec else ""
            flip_hint = ""
            wf = opt.get("what_would_flip")
            if isinstance(wf, list) and wf:
                flip_hint = f" · flip: {_one_line(wf[0], 40)}"
            elif isinstance(wf, str) and wf:
                flip_hint = f" · flip: {_one_line(wf, 40)}"
            prefix = opt.get("surface_description_prefix") or f"{pill} {s:.2f}"
            description = f"{prefix} · {tag}precedent: {precedent}{flip_hint}"
        label = opt.get("surface_label") or _thesis(opt)
        options.append({"label": _one_line(label, 120), "description": description[:240]})
    return "\n".join(lines), options


def main() -> int:
    try:
        raw = sys.stdin.read()
    except OSError as exc:
        print(f"[render_card] stdin error: {exc}", file=sys.stderr)
        return 2
    if not raw.strip():
        print("[render_card] empty stdin — nothing to render", file=sys.stderr)
        return 2
    # Accept either raw JSON or the `AUTHOR_GATE_PACKET: { ... }` form.
    body = raw.strip()
    if body.startswith("AUTHOR_GATE_PACKET:"):
        body = body.split(":", 1)[1].strip()
    try:
        packet = json.loads(body)
    except json.JSONDecodeError as exc:
        print(f"[render_card] bad JSON: {exc}", file=sys.stderr)
        return 2

    card, options = render_card(packet)
    decision_type = packet.get("decision_type") or "decision"
    intent = _one_line(packet.get("normalized_intent") or packet.get("request_summary") or "", 100)
    ask_q = f"Author-Gate ({decision_type}): {intent or 'select an approach'}"
    print(card)
    print()
    print("ASK_PROMPT: " + ask_q)
    print("OPTIONS_JSON: " + json.dumps(options, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
