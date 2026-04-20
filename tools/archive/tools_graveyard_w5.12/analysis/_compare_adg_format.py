"""Compare old ADG zip format vs new ADG artifacts to find format differences."""

import glob
import json
import os
import zipfile
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

_emit_writes_through("p1", "_compare_adg_format", "uwg_governed_write")
_emit_writes_through("p1", "_compare_adg_format", "uwg_governed_write_2")
_emit_pulls_context("p1", "_compare_adg_format", "context_retrieval")
_emit_pulls_context("p1", "_compare_adg_format", "context_retrieval_2")
emit_determinism_digest("trace__compare_adg_format", "_compare_adg_format_dispatch")
emit_determinism_digest("trace__compare_adg_format", "_compare_adg_format_complete")
_emit_validated_by_safety_plane("p1", "_compare_adg_format", "safety_validation")
ZIP_PATH = str(REPO_ROOT / "artifacts" / "adg" / "adg_file_graph_20260311T171158Z.zip")
ADG_DIR = str(REPO_ROOT / "artifacts" / "adg")
EXTRACT_DIR = str(REPO_ROOT / "artifacts" / "adg" / "_prior_format")
os.makedirs(EXTRACT_DIR, exist_ok=True)
print("=== EXTRACTING ZIP ===")
with zipfile.ZipFile(ZIP_PATH) as z:
    z.extractall(EXTRACT_DIR)
    print(f"Extracted {len(z.namelist())} files to {EXTRACT_DIR}")
print("\n=== PRIOR FORMAT (zip contents) ===")
for fname in sorted(os.listdir(EXTRACT_DIR)):
    fpath = Path(EXTRACT_DIR) / fname
    if fname.endswith(".json"):
        try:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                top_keys = list(data.keys())[:10]
                print(f"\n  {fname}")
                print(f"    top-level keys: {top_keys}")
                for k in top_keys:
                    v = data[k]
                    if isinstance(v, list):
                        print(
                            f"    [{k}]: list({len(v)})  first item keys: {(list(v[0].keys())[:6] if v and isinstance(v[0], dict) else '?')}"
                        )
                    elif isinstance(v, dict):
                        print(f"    [{k}]: dict({len(v)})  sample keys: {list(v.keys())[:6]}")
                    else:
                        print(f"    [{k}]: {type(v).__name__} = {str(v)[:80]}")
            elif isinstance(data, list):
                print(f"\n  {fname}: list({len(data)})  first item: {(str(data[0])[:120] if data else '?')}")
        except Exception as e:  # guardian: allow-silent-swallow
            print(f"\n  {fname}: ERROR {e}")
    elif fname.endswith(".sqlite"):
        import sqlite3

        conn = sqlite3.connect(fpath)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        print(f"\n  {fname}: tables={tables}")
        for t in tables:
            cur.execute(f"PRAGMA table_info({t})")
            cols = [r[1] for r in cur.fetchall()]
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cur.fetchone()[0]
            print(f"    {t}({cnt} rows): {cols}")
        conn.close()
print("\n\n=== NEW FORMAT (latest artifacts) ===")
new_files = {
    "file_graph": sorted(glob.glob(Path(ADG_DIR) / "adg_file_graph_*.json"))[-1],
    "governance_graph": sorted(glob.glob(Path(ADG_DIR) / "adg_governance_graph_*.json"))[-1],
    "symbol_graph": sorted(glob.glob(Path(ADG_DIR) / "adg_symbol_graph_*.json"))[-1],
    "test_graph": sorted(glob.glob(Path(ADG_DIR) / "adg_test_graph_*.json"))[-1],
    "full": sorted(glob.glob(Path(ADG_DIR) / "adg_full_*.json"))[-1],
    "sqlite": sorted(glob.glob(Path(ADG_DIR) / "adg_indexed_*.sqlite"))[-1],
}
for label, fpath in new_files.items():
    fname = Path(fpath).name
    if fpath.endswith(".json"):
        try:
            with open(fpath, encoding="utf-8") as f:
                snippet = f.read(4096)
            data = json.loads(
                snippet + '"}'
                if not snippet.rstrip().endswith("}") and (not snippet.rstrip().endswith("]"))
                else snippet
            )
        except Exception:  # guardian: allow-silent-swallow
            try:
                with open(fpath, encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:  # guardian: allow-silent-swallow
                print(f"\n  {fname}: ERROR {e}")
                continue
        if isinstance(data, dict):
            top_keys = list(data.keys())[:10]
            print(f"\n  {fname}")
            print(f"    top-level keys: {top_keys}")
            for k in top_keys:
                v = data[k]
                if isinstance(v, list):
                    print(
                        f"    [{k}]: list({len(v)})  first item keys: {(list(v[0].keys())[:6] if v and isinstance(v[0], dict) else '?')}"
                    )
                elif isinstance(v, dict):
                    print(f"    [{k}]: dict({len(v)})  sample keys: {list(v.keys())[:6]}")
                else:
                    print(f"    [{k}]: {type(v).__name__} = {str(v)[:80]}")
        elif isinstance(data, list):
            print(f"\n  {fname}: list({len(data)})")
    elif fpath.endswith(".sqlite"):
        import sqlite3

        conn = sqlite3.connect(fpath)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        print(f"\n  {fname}: tables={tables}")
        for t in tables:
            cur.execute(f"PRAGMA table_info({t})")
            cols = [r[1] for r in cur.fetchall()]
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cur.fetchone()[0]
            print(f"    {t}({cnt} rows): {cols}")
        conn.close()
