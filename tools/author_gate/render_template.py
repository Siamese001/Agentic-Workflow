#!/usr/bin/env python3
"""render_template.py — Generate packet_template.md from canonical schema.

Plan: author-gate-ssot-consolidation-b7c3e1 W2.P2.2.

Reads .windsurf/schemas/author_gate_packet.schema.json and emits a
human-readable Markdown reference at:

    .windsurf/skills/author-gate-packet-builder/packet_template.md

The header section (didactic guidance for Cascade/authors) is preserved
verbatim from a prelude file; only the per-field reference table is
auto-generated. CI gate compares the file's body hash against the live
generation to detect hand-edits.

Usage:
    python tools/author_gate/render_template.py            # write
    python tools/author_gate/render_template.py --check    # exit 1 on drift
    python tools/author_gate/render_template.py --print    # stdout only

CONSTITUTIONAL
    - No subprocess / shell.
    - Specific exceptions only.
    - Deterministic output (sorted keys).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / ".windsurf" / "schemas" / "author_gate_packet.schema.json"
TEMPLATE_PATH = (
    REPO_ROOT / ".windsurf" / "skills" / "author-gate-packet-builder" / "packet_template.md"
)

PRELUDE = """# Author-Gate Decision Packet Template — Didactic Option Shape

> ⚠️ **GENERATED FILE** — Do not hand-edit. Regenerate with
> `python tools/author_gate/render_template.py`. The reference below is
> derived from `.windsurf/schemas/author_gate_packet.schema.json` (canonical
> SSOT per plan `author-gate-ssot-consolidation-b7c3e1`).

This template is loaded by Cascade when `emit_packet.py` is constructing an
`ask_user_question` packet for a **developer-loop / harness** decision point.

Terminology note (do NOT conflate):
- **Author-Gate Decision** = this template. Developer-loop / harness-side.
  Fires when Cascade is about to write code and a trigger in
  `author_gate_triggers.yaml` matches.
- **Runtime Author-Gate** = v30 step [5] ESCALATE branch. Production agent
  escalates a live request to a human approver. Covered by `ADR-023`.

## Header Packet (above the options)

```
AUTHOR-GATE DECISION — <decision_type_human_readable>
⭐ Recommended: <winning option id>            (only when routing.rule_applied == "dominance_fires")
Why it wins: <one case-specific sentence>
Principle at stake: <layer gravity | fail-closed | zero-loss refactor | SSOT | reversibility | ...>
What the ADG shows: <fan_in=N, fan_out=M, layer=L?, blast_radius_files=K>
Historical precedent: <strong|suggestive|none> — <matched_decision_id or "no precedent">
What you're optimizing for: <goal verb>
What you're trading off: <precise cost, not generic>
What would flip this decision: <concrete condition>
Counts: N candidates | M surfaced | X low-confidence | Y non-distinct
```

## Gold-Star Marking

The ⭐ Recommended label fires **iff `routing.rule_applied == "dominance_fires"`**
(top confidence ≥ 0.85 AND gap to next ≥ 0.12). Every surfaced option carries
`[confidence=0.NN]` prefix; only the dominant winner adds `[RECOMMENDED ⭐]`.
"""

EPILOGUE = """
## Routing Rules

| Condition | `routing.rule_applied` | UI behavior |
|-----------|------------------------|-------------|
| All candidates < 0.72 | `low_confidence_ambiguity` | No options surfaced; route to clarify/replan |
| Top ≥ 0.85 AND gap ≥ 0.12 | `dominance_fires` | Surface only top; ⭐ on it |
| Otherwise | `surface_top_<N>` | Surface up to 4 above threshold; no star |

## Suppression Reasons

Suppressed options are still EMITTED in `candidates[]` with `surfaced: false`
for audit transparency; only filtered from the user-facing prompt.

## References

- Canonical schema: `.windsurf/schemas/author_gate_packet.schema.json`
- Skill: `.windsurf/skills/author-gate-packet-builder/SKILL.md`
- Renderer skill: `.windsurf/skills/author-gate-ui-renderer/SKILL.md`
- Constitutional §6, §30
- Plan: `.windsurf/plans/author-gate-ssot-consolidation-b7c3e1.md`
"""


def _format_type(spec: dict) -> str:
    t = spec.get("type")
    if isinstance(t, list):
        return " | ".join(t)
    if isinstance(t, str):
        return t
    if "$ref" in spec:
        return spec["$ref"].split("/")[-1]
    if "enum" in spec:
        return "enum: " + ", ".join(repr(v) for v in spec["enum"])
    return "any"


def _render_field_table(title: str, properties: dict, required: list) -> list[str]:
    lines: list[str] = [f"### {title}", "", "| Field | Type | Required | Notes |", "|-------|------|----------|-------|"]
    for name in sorted(properties):
        spec = properties[name]
        type_str = _format_type(spec)
        req = "✅" if name in required else ""
        notes_parts = []
        if "pattern" in spec:
            notes_parts.append(f"pattern `{spec['pattern']}`")
        if "enum" in spec:
            notes_parts.append("enum: " + ", ".join(repr(v) for v in spec["enum"]))
        if "minimum" in spec or "maximum" in spec:
            notes_parts.append(
                f"range [{spec.get('minimum', '-∞')}, {spec.get('maximum', '∞')}]"
            )
        if "description" in spec:
            notes_parts.append(spec["description"])
        notes = "; ".join(notes_parts) or "—"
        lines.append(f"| `{name}` | `{type_str}` | {req} | {notes} |")
    lines.append("")
    return lines


def render(schema: dict) -> str:
    out: list[str] = [PRELUDE.rstrip(), ""]
    out.append("## Per-Packet Schema (auto-generated)")
    out.append("")
    out.extend(_render_field_table("Top-level fields", schema["properties"], schema["required"]))

    defs = schema.get("$defs", {})
    if "candidate" in defs:
        out.extend(_render_field_table(
            "Candidate (one per option in `candidates[]`)",
            defs["candidate"]["properties"],
            defs["candidate"].get("required", []),
        ))
    if "routing" in defs:
        out.extend(_render_field_table(
            "Routing object (`routing`)",
            defs["routing"]["properties"],
            defs["routing"].get("required", []),
        ))
    if "precedent" in defs:
        out.extend(_render_field_table(
            "Precedent object (`precedent`)",
            defs["precedent"]["properties"],
            [],
        ))
    if "context_fingerprint" in defs:
        out.extend(_render_field_table(
            "Context Fingerprint (`context_fingerprint`)",
            defs["context_fingerprint"]["properties"],
            [],
        ))

    out.append(EPILOGUE.lstrip())
    rendered = "\n".join(out).rstrip() + "\n"
    return rendered


def _hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit 1 if drift")
    parser.add_argument("--print", action="store_true", help="print to stdout")
    args = parser.parse_args()

    with SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        schema = json.load(fh)
    rendered = render(schema)

    if args.print:
        sys.stdout.write(rendered)
        return 0

    if args.check:
        if not TEMPLATE_PATH.exists():
            print(f"[render_template] DRIFT: template missing at {TEMPLATE_PATH}", file=sys.stderr)
            return 1
        existing = TEMPLATE_PATH.read_text(encoding="utf-8")
        if _hash(existing) != _hash(rendered):
            print(
                f"[render_template] DRIFT: template hash {_hash(existing)} "
                f"!= generated {_hash(rendered)}. "
                f"Run: python tools/author_gate/render_template.py",
                file=sys.stderr,
            )
            return 1
        print("[render_template] OK — template in sync with schema")
        return 0

    TEMPLATE_PATH.write_text(rendered, encoding="utf-8")
    print(f"[render_template] wrote {TEMPLATE_PATH} ({len(rendered)} bytes, hash={_hash(rendered)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
