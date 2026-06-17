#!/usr/bin/env python3
"""One-shot Author-Gate spec → packet → card → OPTIONS_JSON for legacy editor ask_user_question.

Usage:
    echo '<spec-json>' | python tools/cursor/author_gate_prepare_ask.py

Stdout:
    AUTHOR_GATE_PACKET: {...}
    <recommendation card>
    ASK_PROMPT: ...
    OPTIONS_JSON: [...]
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        print("[author_gate_prepare_ask] empty stdin", file=sys.stderr)
        return 2
    try:
        spec = json.loads(raw.strip())
    except json.JSONDecodeError as exc:
        print(f"[author_gate_prepare_ask] bad spec JSON: {exc}", file=sys.stderr)
        return 2

    emit = _load(
        "emit_packet_prepare",
        REPO_ROOT / ".claude" / "skills" / "author-gate-packet-builder" / "emit_packet.py",
    )
    render = _load(
        "render_card_prepare",
        REPO_ROOT / ".claude" / "skills" / "author-gate-ui-renderer" / "render_card.py",
    )

    packet = emit.build_packet(spec)
    for err in emit._validate_schema(packet):
        print(f"[author_gate_prepare_ask] WARN: {err}", file=sys.stderr)

    packet_json = json.dumps(packet, ensure_ascii=False)
    print("AUTHOR_GATE_PACKET: " + packet_json)
    print()

    card, options = render.render_card(packet)
    decision_type = packet.get("decision_type") or "decision"
    intent = (packet.get("normalized_intent") or packet.get("request_summary") or "").replace(
        "\n", " "
    )[:100]
    ask_q = f"Author-Gate ({decision_type}): {intent or 'select an approach'}"
    print(card)
    print()
    print("ASK_PROMPT: " + ask_q)
    print("OPTIONS_JSON: " + json.dumps(options, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
