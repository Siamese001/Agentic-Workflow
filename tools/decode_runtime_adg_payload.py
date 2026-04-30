"""Decode the freshest apps_rg runtime ADG payload and summarize structure."""
from __future__ import annotations

import json
import pathlib
import time

BASE = pathlib.Path("agentic_core/L4_state/memory/runtime_adg")
CUTOFF = time.time() - 30 * 60


def main() -> int:
    cands: list[tuple[float, pathlib.Path]] = []
    for d in BASE.iterdir():
        if d.is_dir() and len(d.name) == 2:
            for f in d.rglob("*.json"):
                if f.is_file() and f.stat().st_mtime > CUTOFF and f.stat().st_size > 100_000:
                    cands.append((f.stat().st_mtime, f))
    cands.sort()
    print(f"large_recent_files={len(cands)}")
    if not cands:
        return 1
    target = cands[-1][1]
    print(f"target={target.relative_to(BASE)}")

    raw = json.loads(target.read_text(encoding="utf-8"))
    print(f"version_id={raw.get('version_id')}")
    print(f"type={raw.get('type')}")
    print(f"content_hash={raw.get('content_hash')}")
    payload_hex = raw.get("payload_hex", "")
    print(f"payload_hex_length={len(payload_hex)}")

    if not payload_hex:
        print("[!] no payload_hex; cannot decode")
        return 1

    payload_bytes = bytes.fromhex(payload_hex)
    print(f"first_64_bytes_hex={payload_bytes[:64].hex()}")
    print(f"first_200_chars_repr={payload_bytes[:200]!r}")
    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"[!] direct json decode failed: {exc}")
        # Try NDJSON: split by newlines
        text = payload_bytes.decode("utf-8", errors="replace")
        lines = [ln for ln in text.split("\n") if ln.strip()]
        print(f"lines_count={len(lines)}")
        if lines:
            try:
                first = json.loads(lines[0])
                print(f"first_line_keys={list(first.keys())[:20]}")
                # All NDJSON
                spans = []
                for ln in lines:
                    try:
                        spans.append(json.loads(ln))
                    except json.JSONDecodeError:
                        pass
                print(f"parsed_lines={len(spans)}")
                payload = {"spans": spans}
            except json.JSONDecodeError as exc2:
                print(f"[!] NDJSON parse failed: {exc2}")
                return 1
        else:
            return 1

    print(f"payload_keys={list(payload.keys())[:30]}")
    if "spans" in payload:
        spans = payload["spans"]
        print(f"spans_count={len(spans)}")
        if spans:
            print(f"sample_span_keys={list(spans[0].keys())[:20]}")
            print(f"sample_span={json.dumps(spans[0], indent=2)[:600]}")
            ek: dict[str, int] = {}
            layer: dict[str, int] = {}
            ops: dict[str, int] = {}
            for s in spans:
                attrs = s.get("attributes", {}) if isinstance(s, dict) else {}
                e = attrs.get("edge_kind") or s.get("name") or "(none)"
                ek[e] = ek.get(e, 0) + 1
                lyr = attrs.get("layer") or s.get("layer") or "(none)"
                layer[lyr] = layer.get(lyr, 0) + 1
                op = attrs.get("op") or s.get("op") or s.get("name") or "(none)"
                ops[op] = ops.get(op, 0) + 1
            print()
            print("=== TOP-15 edge_kinds ===")
            for k, v in sorted(ek.items(), key=lambda x: -x[1])[:15]:
                print(f"  {v:6d}  {k}")
            print()
            print("=== Layer distribution ===")
            for k, v in sorted(layer.items(), key=lambda x: -x[1]):
                print(f"  {v:6d}  {k}")
            print()
            print("=== TOP-15 ops ===")
            for k, v in sorted(ops.items(), key=lambda x: -x[1])[:15]:
                print(f"  {v:6d}  {k}")

    if "edges" in payload:
        edges = payload["edges"]
        print()
        print(f"edges_count={len(edges)}")
        if edges:
            print(f"sample_edge={json.dumps(edges[0], indent=2)[:500]}")
            rt: dict[str, int] = {}
            for e in edges:
                r = e.get("relation_type") or e.get("kind") or "(none)"
                rt[r] = rt.get(r, 0) + 1
            print("=== Edge relation_type distribution ===")
            for k, v in sorted(rt.items(), key=lambda x: -x[1])[:20]:
                print(f"  {v:6d}  {k}")

    if "metadata" in payload:
        print()
        print(f"metadata={json.dumps(payload['metadata'], indent=2)[:600]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
