"""Annotate golden items and run the kappa promotion gate (F4.1).

Two sub-commands:
  - ``list``     — print pending items across all rubric families.
  - ``label``    — record a rater's score+notes for a specific item.
  - ``promote``  — run the kappa gate across all pending items and
                   persist promotions (scored / unknown) in place.

Usage examples::

    python tools/eval/annotate_golden.py list --family gov
    python tools/eval/annotate_golden.py label \\
        --item-id seed-gov_policy_compliance-abc123 \\
        --rater alice --score 5 --notes "fully compliant"
    python tools/eval/annotate_golden.py promote --kappa 0.6

All mutations are idempotent: re-labeling with the same rater_id overwrites
that rater's prior entry; re-running ``promote`` on a scored item is a no-op.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from tools.eval.kappa_promotion_gate import (
    DEFAULT_KAPPA_THRESHOLD,
    RUBRIC_MAX,
    RUBRIC_MIN,
    apply_promotion,
    evaluate_item,
)

logger = logging.getLogger(__name__)

_FAMILY_DIRS: dict[str, str] = {"rag": "rag", "governance": "gov", "security": "sec"}


def _iter_items(golden_root: Path, family: str | None) -> list[tuple[Path, dict[str, Any]]]:
    roots: list[Path] = []
    if family:
        sub = _FAMILY_DIRS.get(family, family)
        roots = [golden_root / sub]
    else:
        roots = [golden_root / sub for sub in _FAMILY_DIRS.values()]
    out: list[tuple[Path, dict[str, Any]]] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.json")):
            try:
                with path.open("r", encoding="utf-8") as fh:
                    out.append((path, json.load(fh)))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("skipping %s: %s", path, exc)
    return out


def _write_item(path: Path, item: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(item, fh, indent=2, sort_keys=True)


def cmd_list(args: argparse.Namespace) -> int:
    items = _iter_items(args.golden_root, args.family)
    rows = [(p, it) for p, it in items if str(it.get("gold_outcome") or "").lower() == "pending"]
    if not rows:
        print("(no pending items)")
        return 0
    for path, item in rows:
        label_count = len(item.get("human_labels") or [])
        print(f"{path}  item_id={item.get('item_id')}  labels={label_count}")
    return 0


def cmd_label(args: argparse.Namespace) -> int:
    if not (RUBRIC_MIN <= args.score <= RUBRIC_MAX):
        logger.error("score must be in [%d, %d]", RUBRIC_MIN, RUBRIC_MAX)
        return 2
    for path, item in _iter_items(args.golden_root, args.family):
        if str(item.get("item_id")) != args.item_id:
            continue
        labels = list(item.get("human_labels") or [])
        # Overwrite any prior entry from this rater (idempotent update).
        labels = [lbl for lbl in labels if str(lbl.get("rater_id")) != args.rater]
        entry: dict[str, Any] = {"rater_id": args.rater, "score": args.score, "notes": args.notes}
        labels.append(entry)
        item["human_labels"] = labels
        _write_item(path, item)
        logger.info("labeled %s by rater=%s score=%d", args.item_id, args.rater, args.score)
        return 0
    logger.error("item_id %s not found", args.item_id)
    return 1


def cmd_promote(args: argparse.Namespace) -> int:
    summary = {"scored": 0, "unknown": 0, "pending": 0, "unchanged": 0}
    for path, item in _iter_items(args.golden_root, args.family):
        decision = evaluate_item(item, kappa_threshold=args.kappa)
        summary[decision.outcome] = summary.get(decision.outcome, 0) + 1
        if decision.outcome in ("scored", "unknown"):
            new_item = apply_promotion(item, decision)
            _write_item(path, new_item)
            logger.info("promoted %s -> %s (%s)", decision.item_id, decision.outcome, decision.reason)
        elif decision.outcome == "pending" and (item.get("human_labels") or []):
            logger.info("hold %s: %s", decision.item_id, decision.reason)
    json.dump(summary, sys.stdout, indent=2, sort_keys=True)
    print()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--golden-root", type=Path, default=Path("data/eval/golden"))
    parser.add_argument("--family", choices=["rag", "governance", "security"], default=None)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="list pending items")

    p_label = sub.add_parser("label", help="record a rater label")
    p_label.add_argument("--item-id", required=True)
    p_label.add_argument("--rater", required=True)
    p_label.add_argument("--score", type=int, required=True)
    p_label.add_argument("--notes", default="")

    p_promote = sub.add_parser("promote", help="run kappa gate and persist promotions")
    p_promote.add_argument("--kappa", type=float, default=DEFAULT_KAPPA_THRESHOLD)

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")

    if args.cmd == "list":
        return cmd_list(args)
    if args.cmd == "label":
        return cmd_label(args)
    if args.cmd == "promote":
        return cmd_promote(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
