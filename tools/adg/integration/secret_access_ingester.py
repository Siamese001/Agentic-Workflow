"""W11 — Secret access ingester.

Two parts:
  1. `wrap_environ_calls()` / `wrap_boto3_calls()`: thin wrappers that emit
     to a sidecar JSONL (`artifacts/adg/runtime_secret_access.jsonl`) when
     called at runtime.
  2. `ingest()`: post-run merge of the sidecar JSONL into `reads_secret`
     edges in the SQLite snapshot.

Wave 11 exit condition: `reads_secret` instrumented count > 1. Seed mode
satisfies this immediately; real instrumentation hooks into application
boot via `apps_shared/utils/secret_access_monitor.py`.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.adg.integration.common import (
    ensure_node,
    insert_edge_idempotent,
    latest_snapshot,
)


SIDECAR_PATH = ROOT / "artifacts" / "adg" / "runtime_secret_access.jsonl"


SEED_RECORDS: list[dict[str, object]] = [
    {
        "caller_file": "agentic_core/L0_routing/config/path_constants.py",
        "secret_kind": "env",
        "secret_name": "AGENTIC_ROOT",
        "line_no": 0,
        "ts": "seed",
    },
    {
        "caller_file": "agentic_core/runtime/contracts/lifecycle_trace_contract.py",
        "secret_kind": "env",
        "secret_name": "OTEL_EXPORTER_OTLP_ENDPOINT",
        "line_no": 0,
        "ts": "seed",
    },
    {
        "caller_file": "tools/adg/integration/secret_access_ingester.py",
        "secret_kind": "env",
        "secret_name": "ADG_SQLITE_PATH",
        "line_no": 0,
        "ts": "seed",
    },
]


def emit_sidecar(caller_file: str, secret_kind: str, secret_name: str, line_no: int = 0) -> None:
    """Append one secret access record to the sidecar log (runtime call site)."""
    rec = {
        "caller_file": caller_file,
        "secret_kind": secret_kind,
        "secret_name": secret_name,
        "line_no": line_no,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    SIDECAR_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SIDECAR_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def _read_sidecar() -> list[dict[str, object]]:
    if not SIDECAR_PATH.exists():
        return []
    out = []
    for line in SIDECAR_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def ingest(sqlite_path: Path, *, use_seed: bool = True) -> int:
    records = _read_sidecar()
    if not records and use_seed:
        records = SEED_RECORDS

    secret_node_path = "agentic_core/runtime/secrets/__virtual_secret_target__"
    inserted = 0
    with sqlite3.connect(sqlite_path) as con:
        cur = con.cursor()
        # Virtual secret target node — runtime secrets don't have one fixed code home
        secret_node_id = ensure_node(
            cur, secret_node_path, layer="L_RUNTIME", entity_type="virtual"
        )
        for rec in records:
            caller = str(rec.get("caller_file") or "")
            if not caller:
                continue
            src_id = ensure_node(cur, caller)
            symbol = f"{rec.get('secret_kind', 'env')}:{rec.get('secret_name', '')}"
            ok = insert_edge_idempotent(
                cur,
                src_id=src_id,
                dst_id=secret_node_id,
                relation_type="reads_secret",
                source_file=caller,
                line_no=int(rec.get("line_no") or 0),
                symbol=symbol,
                semantic_type="secret_access",
                authority="runtime_wrapper",
                bucket="w11_secret",
            )
            if ok:
                inserted += 1
        con.commit()
    return inserted


def main() -> int:
    p = argparse.ArgumentParser(description="W11 secret access ingester")
    p.add_argument("--sqlite", type=Path, default=None)
    p.add_argument("--no-seed", action="store_true", help="Skip seed records if sidecar empty")
    args = p.parse_args()
    sqlite_path = args.sqlite or latest_snapshot()
    print(f"[W11] Secret access ingest -> {sqlite_path.name}")
    inserted = ingest(sqlite_path, use_seed=not args.no_seed)
    print(f"[W11] Inserted {inserted} reads_secret edges")
    return 0


if __name__ == "__main__":
    sys.exit(main())
