"""Loads an emitted card pack from disk into a structured object.

Used by the validators to inspect a pack without running the builder.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LoadedCard:
    """One card on disk."""

    filename: str
    path: Path
    content: str


@dataclass(frozen=True)
class LoadedPack:
    """A loaded card pack — manifest + cards."""

    pack_dir: Path
    manifest: dict
    cards: list[LoadedCard]

    @property
    def card_filenames(self) -> set[str]:
        return {c.filename for c in self.cards}

    def card_by_filename(self, filename: str) -> LoadedCard | None:
        for card in self.cards:
            if card.filename == filename:
                return card
        return None


def load_pack(pack_dir: Path) -> LoadedPack:
    """Load an emitted card pack from disk.

    Args:
        pack_dir: Directory written by `CardPackBuilder.build`.

    Returns:
        A `LoadedPack` with the manifest and all .md cards.

    Raises:
        FileNotFoundError: pack_dir or pack_manifest.json missing.
        json.JSONDecodeError: manifest is malformed.
    """
    if not pack_dir.is_dir():
        raise FileNotFoundError(f"Pack directory not found: {pack_dir}")
    manifest_path = pack_dir / "pack_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"pack_manifest.json missing in {pack_dir}"
        )
    with manifest_path.open("r", encoding="utf-8") as fh:
        manifest = json.load(fh)

    cards: list[LoadedCard] = []
    for path in sorted(pack_dir.glob("*.md")):
        cards.append(
            LoadedCard(
                filename=path.name,
                path=path,
                content=path.read_text(encoding="utf-8"),
            )
        )
    return LoadedPack(pack_dir=pack_dir, manifest=manifest, cards=cards)
