"""One-shot mixin MRO/consolidation audit.

Reads the latest ADG SQLite snapshot and emits a JSON inventory of:
  - all *Mixin classes (file, layer, fan-in)
  - all classes that subclass >=2 mixins (the MRO consumers) with their bases
  - candidate clusters (mixins whose names share a stem: healer*, healing*,
    tracing*, meta_learning*, etc.)
"""

from __future__ import annotations

import glob
import json
import os
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SNAP = sorted(glob.glob(str(REPO / "artifacts" / "adg" / "adg_indexed_*.sqlite")), key=os.path.getmtime)[-1]

con = sqlite3.connect(SNAP)
con.row_factory = sqlite3.Row
cur = con.cursor()

# 1. Inspect schema
tables = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
print("# snapshot:", os.path.basename(SNAP), file=sys.stderr)
print("# tables:", sorted(tables), file=sys.stderr)


# Discover schema for `nodes` and `edges`
def cols(t: str) -> list[str]:
    return [r[1] for r in cur.execute(f"PRAGMA table_info({t})")]


print("# nodes cols:", cols("nodes"), file=sys.stderr)
print("# edges cols:", cols("edges"), file=sys.stderr)
