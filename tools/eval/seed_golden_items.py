"""Seed pending golden items per rubric (F1 follow-up).

Reads rubric anchors from ``config/judges/rubrics.yaml`` and emits
``gold_outcome: "pending"`` template items into the correct rubric folder.
These items are NOT calibrated — they carry ``gold_score: null`` and
``human_labels: []`` so they do not falsely inflate the κ-gate population,
but they DO give the capability/regression runner, the transcript sampler,
and the curation pipeline a non-empty dataset to exercise.

Deterministic: same rubric_id + seed + count ⇒ same item IDs and bodies.
Idempotent: re-running overwrites existing seeds only if ``--force`` is set.

Usage:
    python tools/eval/seed_golden_items.py --per-rubric 10
    python tools/eval/seed_golden_items.py --per-rubric 50 --seed 1 --force

Families written:
    data/eval/golden/rag/<dim>/seed-*.json         (dimensions block)
    data/eval/golden/gov/<dim>/seed-*.json         (governance_dimensions block)
    data/eval/golden/sec/<dim>/seed-*.json         (security_dimensions block)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_FAMILY_KEYS: dict[str, str] = {
    "rag": "dimensions",
    "governance": "governance_dimensions",
    "security": "security_dimensions",
}

# Map family → on-disk root (README.md schema uses "gov" and "sec").
_FAMILY_DIR: dict[str, str] = {
    "rag": "rag",
    "governance": "gov",
    "security": "sec",
}


def _load_rubrics(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit(f"PyYAML required: {exc}") from exc
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _deterministic_id(dim: str, seed: int, idx: int) -> str:
    digest = hashlib.sha256(f"{dim}|{seed}|{idx}".encode("utf-8")).hexdigest()[:12]
    return f"seed-{dim}-{digest}"


def _template_item(dim: str, spec: dict[str, Any], seed: int, idx: int, now_iso: str) -> dict[str, Any]:
    anchors = spec.get("anchors", {}) or {}
    # Rotate through anchors so seed items cover low/mid/high score targets.
    anchor_keys = sorted(anchors.keys())
    target_anchor = anchor_keys[idx % len(anchor_keys)] if anchor_keys else None
    target_text = anchors.get(target_anchor) if target_anchor is not None else ""
    return {
        "item_id": _deterministic_id(dim, seed, idx),
        "rubric_id": dim,
        "query": f"[seed {idx}] probe {dim} targeting anchor {target_anchor}",
        "context": (
            f"Anchor guidance for score {target_anchor}: {target_text}. "
            "This is a seed template; a human rater must supply the real query, "
            "context, and answer before calibration."
        ),
        "answer": None,
        "human_labels": [],
        "gold_score": None,
        "gold_outcome": "pending",
        "target_anchor": target_anchor,
        "created_at": now_iso,
        "generator": "seed_golden_items",
        "notes": "pending human authorship; do not count toward κ-gate population",
    }


def seed(
    rubrics: dict[str, Any],
    golden_root: Path,
    per_rubric: int,
    seed_value: int,
    force: bool,
    now_iso: str,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for family, key in _FAMILY_KEYS.items():
        dims = rubrics.get(key, {}) or {}
        fam_dir = golden_root / _FAMILY_DIR[family]
        for dim, spec in dims.items():
            dim_dir = fam_dir / dim
            dim_dir.mkdir(parents=True, exist_ok=True)
            written = 0
            for idx in range(per_rubric):
                item = _template_item(dim, spec, seed_value, idx, now_iso)
                path = dim_dir / f"{item['item_id']}.json"
                if path.exists() and not force:
                    continue
                with path.open("w", encoding="utf-8") as fh:
                    json.dump(item, fh, indent=2, sort_keys=True)
                written += 1
            counts[f"{family}.{dim}"] = written
            logger.info("seeded %d items into %s", written, dim_dir)
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rubrics", type=Path, default=Path("config/judges/rubrics.yaml"))
    parser.add_argument("--golden-root", type=Path, default=Path("data/eval/golden"))
    parser.add_argument("--per-rubric", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--now", default="2026-04-23T00:00:00Z")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")

    rubrics = _load_rubrics(args.rubrics)
    counts = seed(rubrics, args.golden_root, args.per_rubric, args.seed, args.force, args.now)
    total = sum(counts.values())
    logger.info("total seed items written: %d", total)
    json.dump(counts, sys.stdout, indent=2, sort_keys=True)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
