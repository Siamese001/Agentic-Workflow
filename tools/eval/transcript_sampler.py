"""Transcript sampler & regrade queue.

Anthropic best-practice step 6 codified: sample a representative set of
execution transcripts from runtime ADG / OTel traces and enqueue them for
judge regrade + human spot-check. The sampler is deterministic given a seed
and a time window so cadence can be reproduced in CI.

Invariants:
  - Observer posture only (read, never mutate).
  - Anonymizes secrets / PII before writing to the regrade queue.
  - Sampling is stratified per rubric family so rare dimensions are not
    drowned out by high-traffic dimensions.

Source: reads from the L6 runtime-ADG snapshot index written by
``system_learning.runtime_adg.l6_integration.L6MetaLearningBridge``. The
default path is ``system_learning/meta_learning/runtime_adg_snapshots/
snapshot_index.json``; override with ``--source``.

Usage:
    python tools/eval/transcript_sampler.py \
        --window 24h --per-family 25 --out artifacts/eval/regrade_queue.jsonl
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_SNAPSHOT_INDEX = Path("system_learning/meta_learning/runtime_adg_snapshots/snapshot_index.json")


@dataclass(frozen=True, slots=True)
class SampleRequest:
    window: str
    per_family: int
    seed: int
    source: Path
    families: tuple[str, ...] = ("rag", "governance", "security")


def _anonymize(trace: dict[str, Any]) -> dict[str, Any]:
    """Remove credentials / PII before enqueueing for regrade.

    W2.1 scaffold: uses a deny-list redaction pass. W2.3 curation adapter
    replaces this with the full anonymization pipeline shared with the
    prod→golden loop.
    """
    redacted = json.loads(json.dumps(trace))
    for sensitive_key in ("api_key", "secret", "token", "password", "authorization"):
        for node in _walk(redacted):
            if isinstance(node, dict) and sensitive_key in node:
                node[sensitive_key] = "<REDACTED>"
    return redacted


def _walk(obj: Any):
    yield obj
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)


def _parse_window_seconds(window: str) -> int:
    """Parse ``24h`` / ``7d`` / ``30m`` / ``3600s`` into seconds."""
    window = window.strip().lower()
    if not window:
        return 24 * 3600
    unit = window[-1]
    try:
        value = int(window[:-1])
    except ValueError:
        raise ValueError(f"invalid window spec: {window!r}") from None
    return {"s": value, "m": value * 60, "h": value * 3600, "d": value * 86400}.get(unit, 24 * 3600)


def _infer_rubric_family(mission: str) -> str:
    """Best-effort family inference from snapshot mission string."""
    m = mission.lower()
    if any(key in m for key in ("inject", "secret", "pii", "credential", "guardrail_bypass")):
        return "security"
    if any(key in m for key in ("policy", "authorization", "audit", "governance", "write_gate")):
        return "governance"
    return "rag"


def _load_runtime_traces(source: Path, window: str, now_epoch: float) -> list[dict[str, Any]]:
    """Load candidate traces from the L6 runtime-ADG snapshot index.

    The index file is produced by
    ``L6MetaLearningBridge.store_snapshot_for_meta_learning``; each entry
    carries ``trace_id``, ``timestamp``, ``mission``, ``node_count``,
    ``edge_count``, ``duration_ms``, and ``file_path``. We project those
    into a minimal trace dict for the regrade queue.
    """
    if not source.exists():
        logger.warning("snapshot index not found: %s (returning empty)", source)
        return []
    try:
        index = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("failed to read snapshot index %s: %s", source, exc)
        return []

    window_s = _parse_window_seconds(window)
    cutoff = now_epoch - window_s
    out: list[dict[str, Any]] = []
    for meta_learning_id, entry in (index or {}).items():
        ts = float(entry.get("timestamp", 0))
        if ts < cutoff:
            continue
        mission = str(entry.get("mission", ""))
        out.append(
            {
                "meta_learning_id": meta_learning_id,
                "trace_id": str(entry.get("trace_id", "")),
                "mission": mission,
                "rubric_family": _infer_rubric_family(mission),
                "timestamp": ts,
                "node_count": int(entry.get("node_count", 0)),
                "edge_count": int(entry.get("edge_count", 0)),
                "duration_ms": int(entry.get("duration_ms", 0)),
                "snapshot_path": str(entry.get("file_path", "")),
            }
        )
    logger.info("loaded %d traces within window=%s from %s", len(out), window, source)
    return out


def sample(req: SampleRequest, now_epoch: float | None = None) -> list[dict[str, Any]]:
    rng = random.Random(req.seed)
    traces = _load_runtime_traces(req.source, req.window, now_epoch or time.time())
    buckets: dict[str, list[dict[str, Any]]] = {f: [] for f in req.families}
    for t in traces:
        fam = t.get("rubric_family", "rag")
        if fam in buckets:
            buckets[fam].append(t)
    sampled: list[dict[str, Any]] = []
    for fam, items in buckets.items():
        if not items:
            continue
        rng.shuffle(items)
        sampled.extend(_anonymize(x) for x in items[: req.per_family])
    return sampled


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window", default="24h", help="time window, e.g. 24h, 7d")
    parser.add_argument("--per-family", type=int, default=25)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--source",
        type=Path,
        default=_DEFAULT_SNAPSHOT_INDEX,
        help="L6 snapshot index JSON (default: runtime_adg_snapshots/snapshot_index.json)",
    )
    parser.add_argument(
        "--now-epoch", type=float, default=None, help="override 'now' for deterministic test runs"
    )
    parser.add_argument("--out", type=Path, default=Path("artifacts/eval/regrade_queue.jsonl"))
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")

    samples = sample(
        SampleRequest(args.window, args.per_family, args.seed, args.source),
        now_epoch=args.now_epoch,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for s in samples:
            fh.write(json.dumps(s, sort_keys=True) + "\n")
    logger.info("wrote %d samples to %s", len(samples), args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
