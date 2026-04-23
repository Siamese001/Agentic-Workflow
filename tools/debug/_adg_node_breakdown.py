"""Show per-file node breakdown for sample archived files."""
from __future__ import annotations

import sqlite3

OLD = "artifacts/adg/adg_indexed_04232026_0925.sqlite"
c = sqlite3.connect(OLD)

samples = [
    "agentic_core/adg/_compat/sandbox_airlock.py",   # Wave A empty shim
    "agentic_core/evaluation/metrics/mrr.py",         # Wave B empty shim
    "agentic_core/interfaces/validators_shim.py",     # Wave C.1 small
    "apps_shared/utils/unified_signal_pipeline_util.py",  # Wave C.2 59KB
    "apps_shared/utils/format_data_util.py",          # Wave C.2 tiny
    "apps_lic/tools/GeminiLLMClient.py",              # Wave C.3 mid
]
for s in samples:
    total = c.execute(
        "SELECT COUNT(*) FROM nodes WHERE resolved_path=?", (s,)
    ).fetchone()[0]
    by_type = c.execute(
        "SELECT entity_type, COUNT(*) FROM nodes WHERE resolved_path=? GROUP BY entity_type",
        (s,),
    ).fetchall()
    print(f"{total:4d} nodes  {s}")
    for et, n in by_type:
        print(f"         {n:4d}  {et}")
