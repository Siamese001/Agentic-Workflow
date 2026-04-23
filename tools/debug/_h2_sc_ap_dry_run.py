"""H2 dry-run: confirm SC-5 promotion won't surprise-block current snapshot."""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.generate.validation.gates import (
    _query_sc5_spine,
    _query_sc7_grounding,
    _query_ap14_retrieval_no_evidence,
)

snap = Path("artifacts/adg/adg_indexed_04232026_0925.sqlite")
conn = sqlite3.connect(snap)
for name, fn in [
    ("SC-5 spine", _query_sc5_spine),
    ("SC-7 grounding", _query_sc7_grounding),
    ("AP-14 retrieval-no-evidence", _query_ap14_retrieval_no_evidence),
]:
    v = fn(conn)
    print(f"{name:30s}: {len(v)} violations")
    for row in v[:3]:
        print(f"   - {row}")
conn.close()
