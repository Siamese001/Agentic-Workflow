from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HealingContext:
    heal: bool
    project_root: Path
    verbose: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "heal", bool(self.heal))
        object.__setattr__(self, "project_root", Path(self.project_root).resolve())
        object.__setattr__(self, "verbose", bool(self.verbose))

    @property
    def dry_run(self) -> bool:
        return not self.heal
