"""Deterministic replay proof — run the canary twice, assert digest stable.

W3.2 of plan ``assurance-p1-gates-ab4758``. Builds on W1's canary by extending
it with two consecutive runs and comparing the four-tuple replay invariant
digest from each.

Two runs MUST produce identical digests. If they don't, either:

  - The pipeline emitted non-deterministic content into the invariant
    (ordering, timestamps, generator state), or
  - The replay invariant changed between runs (tampering / drift).

Exit code:
    0  digests match — replay is deterministic.
    1  digests differ — replay defect.
    2  infrastructure error.

Usage::

    python scripts/proof/run_replay_proof.py
    python scripts/proof/run_replay_proof.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any

_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


def _emit(message: str) -> None:
    print(message, file=sys.stderr)


def _build_invariant_from_canary(spans: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive the four-tuple replay invariant from a canary span graph.

    For the W1 LIC canary the mapping is:

      - route_id          -> attributes.route_id on the L0 routing span
      - gate_decisions    -> ordered (span_name, status) for L0/L1/L2 spans
      - evidence_packet_ids -> attributes.evidence_packet_id on exit spans
      - final_disposition -> attributes.disposition on exit.disposition
    """
    invariant_route_id = ""
    gate_decisions: list[tuple[str, str]] = []
    evidence_ids: set[str] = set()
    final_disposition = ""

    gate_layers = {"L0", "L1", "L2"}
    for span in spans:
        attrs = span.get("attributes", {}) or {}
        layer = span.get("layer", "")
        name = span.get("name", "")
        if not invariant_route_id and attrs.get("route_id"):
            invariant_route_id = str(attrs["route_id"])
        if layer in gate_layers and name:
            gate_decisions.append((str(name), str(span.get("status", "ok"))))
        evp = attrs.get("evidence_packet_id")
        if isinstance(evp, str) and evp:
            evidence_ids.add(evp)
        if name == "exit.disposition":
            disp = attrs.get("disposition")
            if isinstance(disp, str):
                final_disposition = disp

    return {
        "route_id": invariant_route_id,
        "gate_decisions": gate_decisions,
        "evidence_packet_ids": sorted(evidence_ids),
        "final_disposition": final_disposition,
    }


def run_one_replay(*, trace_id: str) -> dict[str, Any]:
    """Run one canary replay and return the digest + invariant fields."""
    from agentic_core.L6_observability.runtime_trace import (
        build_canary_lic_spans,
    )
    from tools.proof.replay_digest import compute_digest

    spans = build_canary_lic_spans(
        trace_id=trace_id,
        # Pin base_time_ms to a constant — replay-invariant fields must NOT
        # include timestamps, but downstream extractors might. Pinning here
        # lets us compare strictly.
        base_time_ms=1700000000000,
    )
    inv = _build_invariant_from_canary(spans)
    digest = compute_digest(**inv)
    return {"trace_id": trace_id, "digest": digest, "invariant": inv}


def run_proof(*, route_id: str = "lic.standard") -> dict[str, Any]:
    """Run two replays and assert their digests match."""
    result: dict[str, Any] = {
        "ok": False,
        "route_id": route_id,
        "runs": [],
        "match": False,
        "error": None,
    }
    try:
        # Different trace_ids on each run — trace_id is NOT in the replay
        # invariant. If the digest still matches, the invariant fields
        # truly are run-deterministic.
        run_a = run_one_replay(trace_id=f"replay-a-{uuid.uuid4().hex[:8]}")
        _emit(f"  Run A: digest={run_a['digest'][:16]}…")
        run_b = run_one_replay(trace_id=f"replay-b-{uuid.uuid4().hex[:8]}")
        _emit(f"  Run B: digest={run_b['digest'][:16]}…")
    except (ImportError, AttributeError, ValueError, TypeError, KeyError) as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result

    result["runs"] = [run_a, run_b]
    result["match"] = run_a["digest"] == run_b["digest"]
    result["ok"] = result["match"]
    return result


def _format_human(result: dict[str, Any]) -> str:
    lines = ["replay_proof: " + ("PASS" if result["ok"] else "FAIL")]
    lines.append(f"  route_id: {result['route_id']}")
    if result["error"]:
        lines.append(f"  error:    {result['error']}")
    for i, run in enumerate(result.get("runs", []), 1):
        lines.append(f"  run_{i}:    digest={run['digest']}  trace_id={run['trace_id']}")
    if result.get("runs") and not result["match"]:
        a = result["runs"][0]["invariant"]
        b = result["runs"][1]["invariant"]
        for key in sorted(set(a) | set(b)):
            if a.get(key) != b.get(key):
                lines.append(f"  diff:     {key}: {a.get(key)!r} != {b.get(key)!r}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--route-id", default="lic.standard")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = run_proof(route_id=args.route_id)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(_format_human(result))

    if result["error"]:
        return 2
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
