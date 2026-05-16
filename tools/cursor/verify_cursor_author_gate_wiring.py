#!/usr/bin/env python3
"""verify_cursor_author_gate_wiring.py — operator smoke check (non-interactive).

Validates that precedent lookup targets ``.cursor/state/...``, capture targets the
same, ``author_gate_prepare_ask`` emits ``AUTHOR_GATE_PACKET:``, and capture inserts
on a synthetic ``DECISION_CAPTURED`` marker into a temp ledger.

Exit 0 — all checks passed
Exit 1 — any check failed
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load(mod_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    errors: list[str] = []

    lookup = _load(
        "lookup_verify",
        REPO_ROOT / ".cursor" / "skills" / "refactor-decision-memory" / "lookup_refactor_decisions.py",
    )
    cpath = str(lookup.DB_PATH).replace("\\", "/")
    if ".cursor/state/refactor_decisions/refactor_decision_ledger.sqlite" not in cpath:
        errors.append(f"lookup DB_PATH not Cursor ledger: {lookup.DB_PATH}")

    cap = _load(
        "capture_verify",
        REPO_ROOT / ".cursor" / "scripts" / "post_cursor_agent_author_gate_capture.py",
    )
    cpath2 = str(cap.DB_PATH).replace("\\", "/")
    if ".cursor/state/refactor_decisions/refactor_decision_ledger.sqlite" not in cpath2:
        errors.append(f"capture DB_PATH not Cursor ledger: {cap.DB_PATH}")

    proc = subprocess.run(
        [
            sys.executable,
            str(
                REPO_ROOT
                / ".cursor"
                / "skills"
                / "refactor-decision-memory"
                / "lookup_refactor_decisions.py"
            ),
        ],
        input=json.dumps(
            {
                "decision_type": "refactor_scope",
                "normalized_intent": "verify wiring smoke intent",
                "limit": 2,
            }
        ),
        text=True,
        capture_output=True,
        cwd=str(REPO_ROOT),
        check=False,
        timeout=60,
    )
    if proc.returncode != 0:
        errors.append(f"lookup exit={proc.returncode} stderr={proc.stderr[:500]}")

    spec = {
        "decision_type": "refactor_scope",
        "normalized_intent": "verify wiring smoke",
        "files_in_scope": [],
        "candidates": [
            {
                "id": "a",
                "thesis": "smoke",
                "confidence_score": 0.86,
                "principle_at_stake": "test",
                "what_youd_miss": "x",
                "what_would_flip": "y",
                "key_tradeoffs": ["t1", "t2"],
            },
            {
                "id": "b",
                "thesis": "alt",
                "confidence_score": 0.55,
                "principle_at_stake": "test",
                "what_youd_miss": "x",
                "what_would_flip": "y",
                "key_tradeoffs": ["t1", "t2"],
            },
        ],
    }
    p2 = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "cursor" / "author_gate_prepare_ask.py")],
        input=json.dumps(spec),
        text=True,
        capture_output=True,
        cwd=str(REPO_ROOT),
        check=False,
        timeout=120,
    )
    if p2.returncode != 0:
        errors.append(f"author_gate_prepare_ask exit={p2.returncode}: {p2.stderr[:800]}")
    elif "AUTHOR_GATE_PACKET:" not in (p2.stdout or "") or "OPTIONS_JSON:" not in (p2.stdout or ""):
        errors.append("author_gate_prepare_ask stdout missing AUTHOR_GATE_PACKET or OPTIONS_JSON")

    with tempfile.TemporaryDirectory() as td:
        tdb = Path(td) / "ledger.sqlite"
        cap_mod = _load(
            "cap_run",
            REPO_ROOT / ".cursor" / "scripts" / "post_cursor_agent_author_gate_capture.py",
        )
        cap_mod.DB_DIR = tdb.parent
        cap_mod.DB_PATH = tdb
        cap_mod._log_path = tdb.parent / "author_gate_capture.log"
        before = 0
        conn_init = cap_mod._init_db()
        if conn_init:
            try:
                before = conn_init.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
            finally:
                conn_init.close()
        marker = (
            "DECISION_CAPTURED: type=refactor_scope, repo_area=.cursor/hooks, "
            "selected=smoke-test, outcome=executed, precedent=none\n"
        )
        c2 = cap_mod._init_db()
        assert c2 is not None
        try:
            cap_mod.detect_and_capture(marker, c2)
        finally:
            c2.close()
        c3 = sqlite3.connect(str(tdb))
        try:
            after = c3.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
        finally:
            c3.close()
        if after <= before:
            errors.append(f"capture did not insert (before={before} after={after})")

    if errors:
        for e in errors:
            print(f"[verify] FAIL: {e}", file=sys.stderr)
        return 1
    print("[verify] PASS: lookup path, capture path, lookup run, prepare_ask, marker capture")
    return 0


if __name__ == "__main__":
    sys.exit(main())
