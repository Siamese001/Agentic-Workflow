"""CLI: project ADG truth into ChromaDB semantic cards.

Emits four dedicated collections — ``adg_symbol_cards``, ``adg_hotspot_cards``,
``adg_violation_cards``, ``adg_path_cards`` — from the current ADG SQLite
snapshot. Replaces the anti-pattern raw-edge-bulk ingest in
``tools/ingestion/ingest_adg.py`` (deprecated in µW4).

Usage:

    python tools/ingestion/project_adg_cards.py --adg-db artifacts/adg/adg_indexed_<ts>.sqlite --dry-run
    python tools/ingestion/project_adg_cards.py --adg-db <path> --chroma-dir artifacts/chromadb

Designed to be safe by default: ``--dry-run`` prints counts per kind without
touching ChromaDB.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import TYPE_CHECKING

# Repo-root bootstrap so the script runs directly (python tools/ingestion/project_adg_cards.py).
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.ingestion.adg_cards.hotspot_emitter import emit_hotspot_cards
from tools.ingestion.adg_cards.path_emitter import emit_path_cards
from tools.ingestion.adg_cards.symbol_emitter import emit_symbol_cards
from tools.ingestion.adg_cards.types import CardKind, SemanticCard
from tools.ingestion.adg_cards.violation_emitter import emit_violation_cards
from agentic_core.L4_state.config.chroma_paths import canonical_persist_dir_str

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger("adg_cards.project")

COLLECTION_BY_KIND: dict[CardKind, str] = {
    CardKind.SYMBOL: "adg_symbol_cards",
    CardKind.HOTSPOT: "adg_hotspot_cards",
    CardKind.VIOLATION: "adg_violation_cards",
    CardKind.PATH: "adg_path_cards",
}


def _group_by_kind(cards: Iterable[SemanticCard]) -> dict[CardKind, list[SemanticCard]]:
    out: dict[CardKind, list[SemanticCard]] = {k: [] for k in CardKind}
    for card in cards:
        out[card.card_kind].append(card)
    return out


def _iter_all_cards(adg_db: Path, limit: int | None) -> Iterator[SemanticCard]:
    yield from emit_symbol_cards(adg_db, limit=limit)
    yield from emit_hotspot_cards(adg_db, limit=limit)
    yield from emit_violation_cards(adg_db, limit=limit)
    yield from emit_path_cards(adg_db, limit=limit)


def _write_chroma(
    grouped: dict[CardKind, list[SemanticCard]],
    chroma_dir: Path,
    batch_size: int,
) -> None:
    """Upsert cards into their respective ChromaDB collections.

    Import is local so ``--dry-run`` avoids the Chroma dependency entirely.
    """

    # Local import: keeps --dry-run usable even if Chroma isn't installed.
    from agentic_core.L4_state.utils.client.chroma_client import (  # noqa: PLC0415
        SovereignChromaClient,
    )

    client = SovereignChromaClient(persist_dir=str(chroma_dir))
    for kind, cards in grouped.items():
        if not cards:
            continue
        collection = COLLECTION_BY_KIND[kind]
        for start in range(0, len(cards), batch_size):
            batch = cards[start : start + batch_size]
            client.add_documents(
                collection_name=collection,
                documents=[c.document for c in batch],
                metadatas=[c.metadata for c in batch],
                ids=[c.chroma_id() for c in batch],
            )
            logger.info("upserted %d cards into %s", len(batch), collection)


def _report(grouped: dict[CardKind, list[SemanticCard]]) -> None:
    total = sum(len(v) for v in grouped.values())
    print(f"ADG semantic card projection — total={total}")
    for kind in CardKind:
        cards = grouped[kind]
        sample = cards[0].card_id if cards else "-"
        print(f"  {COLLECTION_BY_KIND[kind]:24s}  count={len(cards):6d}  sample_id={sample}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adg-db", type=Path, required=True, help="Path to ADG SQLite snapshot.")
    parser.add_argument("--chroma-dir", type=Path, default=Path(canonical_persist_dir_str()))
    parser.add_argument("--limit", type=int, default=None, help="Per-emitter row cap (for smoke runs).")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--dry-run", action="store_true", help="Emit and count only; do not touch Chroma.")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=args.log_level.upper(), stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s"
    )

    if not args.adg_db.exists():
        parser.error(f"ADG sqlite not found: {args.adg_db}")

    cards = list(_iter_all_cards(args.adg_db, args.limit))
    grouped = _group_by_kind(cards)
    _report(grouped)

    if args.dry_run:
        return 0

    _write_chroma(grouped, args.chroma_dir, args.batch_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
