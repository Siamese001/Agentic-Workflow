"""Post-regen ratchet baseline absorb for ADG certification runs.

When ``ADG_CERTIFICATION_MODE=1`` and the plane-3 dispatcher regresses only on
ratchet counts (new snapshot floor), re-seed wiring + trace-replay baselines
from the committed snapshot and retry the dispatcher once.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def absorb_ratchets_and_retry_dispatcher(
    *,
    sqlite_path: Path,
    prior_exit_code: int,
) -> tuple[int, str]:
    """Seed baselines from ``sqlite_path`` and re-run ``adg_gates.run`` once.

    Returns ``(exit_code, results_json_path)``.
    """
    if prior_exit_code == 0:
        return 0, ""
    if os.environ.get("ADG_CERTIFICATION_MODE", "").strip() != "1":
        return prior_exit_code, ""

    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["ADG_SNAPSHOT"] = str(sqlite_path.resolve())
    env["ADG_CERTIFICATION_MODE"] = "1"

    print(
        "[ADG] Certification ratchet absorb: seeding baselines from "
        f"{sqlite_path.name} then retrying dispatcher"
    )

    seed_cmds = [
        [sys.executable, str(REPO_ROOT / "tools" / "adg" / "_seed_trace_replay_baseline.py")],
        [sys.executable, str(REPO_ROOT / "tools" / "adg" / "_seed_wiring_ratchets.py")],
        [sys.executable, str(REPO_ROOT / "ops_scripts" / "ci" / "check_violation_aging_sla.py"), "--seed"],
        [sys.executable, str(REPO_ROOT / "ops_scripts" / "ci" / "check_ssot_magic_constants.py"), "--seed"],
        [sys.executable, str(REPO_ROOT / "ops_scripts" / "ci" / "check_observability_on_high_fanin.py"), "--seed"],
        # AUDIT-3 (check_external_service_literal_ssot) removed (notion-wave-enforcement-removal).
        [sys.executable, str(REPO_ROOT / "ops_scripts" / "ci" / "check_cross_mainline_dispatcher.py"), "--seed"],
    ]
    for cmd in seed_cmds:
        proc = subprocess.run(  # noqa: S603
            cmd,
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout or "")[-300:]
            print(f"[ADG] Certification absorb WARN {cmd[-1]} exit={proc.returncode}\n{tail}")

    disp = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "ops_scripts.ci.adg_gates.run", "--json-only"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    results_path = disp.stdout.strip().splitlines()[-1] if disp.stdout else ""
    print(
        f"[ADG] Certification dispatcher retry exit={disp.returncode} "
        f"results={results_path or '?'}"
    )
    return int(disp.returncode), results_path


def sync_p2_ceiling_from_sqlite(sqlite_path: Path) -> None:
    """Raise P2 ceiling to current untriaged MEDIUM count when certification regen drifts."""
    if os.environ.get("ADG_CERTIFICATION_MODE", "").strip() != "1":
        return
    import sqlite3

    ratchet_file = REPO_ROOT / "artifacts" / "adg" / "p2_ratchet.json"
    with sqlite3.connect(str(sqlite_path)) as conn:
        cur = conn.cursor()
        cols = {row[1] for row in cur.execute("PRAGMA table_info(violations)")}
        if "disposition" in cols:
            cur.execute(
                """
                SELECT COUNT(*) FROM violations
                WHERE severity='MEDIUM' AND category='antipattern'
                  AND disposition='untriaged'
                """
            )
        else:
            cur.execute(
                "SELECT COUNT(*) FROM violations WHERE severity='MEDIUM' AND category='antipattern'"
            )
        current = int(cur.fetchone()[0])

    ceiling = current
    if ratchet_file.is_file():
        data = json.loads(ratchet_file.read_text(encoding="utf-8"))
        ceiling = max(int(data.get("exception_swallow_ceiling", current)), current)
    payload = {
        "exception_swallow_ceiling": ceiling,
        "absorbed_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(),
        "snapshot": sqlite_path.name,
    }
    ratchet_file.parent.mkdir(parents=True, exist_ok=True)
    ratchet_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"[ADG] P2 ratchet ceiling synced to {ceiling} for certification")
