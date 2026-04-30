"""Negative fixture for ``check_lifecycle_pairs`` (W4 P4.5 audit).

Contains a ``sqlite3.connect`` call whose result is:
  * NOT used inside a ``with`` statement
  * NOT assigned to ``self.<attr>``
  * NOT followed by any ``.close()`` call in the enclosing function

The lifecycle-pairs gate MUST detect this. It is the canonical resource-leak
pattern the gate exists to prevent.

Do NOT import this file from production code.
"""

from __future__ import annotations

import sqlite3


def _leaking_connect_use() -> int:
    """Should be flagged as a lifecycle-pair leak."""
    conn = sqlite3.connect(":memory:")  # noqa: F841 -- deliberate leak
    # No close, no with, no self.<attr> — three independent leak indicators.
    cur = conn.cursor()
    cur.execute("SELECT 1")
    row = cur.fetchone()
    return row[0] if row else -1


def _properly_closed_connect_use() -> int:
    """Control: should NOT be flagged — uses ``with`` context manager."""
    with sqlite3.connect(":memory:") as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        row = cur.fetchone()
        return row[0] if row else -1
