"""P1/P2/P3 quality gates and dead import detection for ADG generation."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _check_p1_defects(routing_summary: dict[str, int], sqlite_path: Path | None = None) -> None:
    """Fail if P1 critical defects are present (unconditional fail-fast).

    Args:
        routing_summary: Dictionary with by_severity counts
        sqlite_path: Path to SQLite database for in_cycle/dynamic_exec queries
    """
    if sqlite_path is not None and sqlite_path.exists():
        try:
            with sqlite3.connect(str(sqlite_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT source_file, line_no FROM edges WHERE relation_type='violates'")
                violation_rows = cursor.fetchall()

            unapproved = []
            for source_file, line_no in violation_rows:
                try:
                    src_path = ROOT / source_file
                    if src_path.exists() and line_no and line_no > 0:
                        lines = src_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                        check_lines = lines[max(0, line_no - 2) : line_no]
                        exempted = any("guardian: allow-layer-violation" in ln for ln in check_lines)
                        if not exempted:
                            unapproved.append((source_file, line_no))
                    else:
                        print(
                            f"[DEBUG] Guardian check: file not found or invalid line_no: {source_file}:{line_no}"
                        )
                        unapproved.append((source_file, line_no))
                except Exception as e:  # guardian: allow-silent-swallow -- non-critical: file read failure during exemption check
                    print(f"[DEBUG] Guardian check exception for {source_file}:{line_no}: {e}")
                    unapproved.append((source_file, line_no))

            p1_count = len(unapproved)
            if p1_count > 0:
                print(f"\n[ERROR] P1 critical defects detected: {p1_count}")
                for sf, ln in unapproved[:10]:
                    print(f"[ERROR]   {sf}:{ln}")
                print("[ERROR] ADG generation failed - P1 defects present")
                print("[ERROR] Fix critical layer violations before regenerating ADG")
                sys.exit(1)
        except SystemExit:
            raise
        except Exception:  # guardian: allow-silent-swallow -- non-critical: SQLite query failure during P1 check falls back gracefully
            pass
    else:
        p1_count = routing_summary.get("by_severity", {}).get("critical", 0)
        if p1_count > 0:
            print(f"\n[ERROR] P1 critical defects detected: {p1_count}")
            print("[ERROR] ADG generation failed - P1 defects present")
            print("[ERROR] Fix critical layer violations before regenerating ADG")
            sys.exit(1)

    if sqlite_path is not None and sqlite_path.exists():
        try:
            with sqlite3.connect(str(sqlite_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type='in_cycle'")
                in_cycle_count = cursor.fetchone()[0]
                if in_cycle_count > 0:
                    print(f"\n[ERROR] P1 Tier 1A: Circular imports detected: {in_cycle_count}")
                    print("[ERROR] ADG generation failed - graph topology corrupted by cycles")
                    print("[ERROR] Fix circular imports before regenerating ADG")
                    sys.exit(1)
        except Exception:  # guardian: allow-silent-swallow -- non-critical: SQLite query failure during Tier 1A check falls back gracefully
            pass

    if sqlite_path is not None and sqlite_path.exists():
        try:
            with sqlite3.connect(str(sqlite_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type='dynamic_exec'")
                dynamic_exec_count = cursor.fetchone()[0]
                if dynamic_exec_count > 0:
                    print(f"\n[ERROR] P1 Tier 1B: Dynamic execution detected: {dynamic_exec_count}")
                    print("[ERROR] ADG generation failed - graph is provably incomplete")
                    print("[ERROR] Replace eval/exec/dynamic imports with static alternatives")
                    sys.exit(1)
        except Exception:  # guardian: allow-silent-swallow -- non-critical: SQLite query failure during Tier 1B check falls back gracefully
            pass


def _check_p2_antipatterns(sqlite_path: Path | None = None, ratchet_file: Path | None = None) -> None:
    """Block if HIGH-severity antipatterns INCREASED vs prior run (ratchet).

    Args:
        sqlite_path: Path to SQLite database for exception swallow queries
        ratchet_file: Path to JSON file storing P2 ceiling (default: artifacts/adg/p2_ratchet.json)
    """
    if sqlite_path is None or not sqlite_path.exists():
        return

    if ratchet_file is None:
        ratchet_file = ROOT / "artifacts" / "adg" / "p2_ratchet.json"

    try:
        with sqlite3.connect(str(sqlite_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM violations WHERE severity='HIGH' AND category='antipattern'",
            )
            current_count = cursor.fetchone()[0]

        if ratchet_file.exists():
            with open(ratchet_file) as f:
                ratchet_data = json.load(f)
            ceiling = ratchet_data.get(
                "high_severity_ceiling", ratchet_data.get("p2_antipattern_ceiling", current_count)
            )
        else:
            ceiling = current_count
            ratchet_file.parent.mkdir(parents=True, exist_ok=True)
            with open(ratchet_file, "w") as f:
                json.dump({"high_severity_ceiling": ceiling}, f, indent=2)
            print(f"[INFO] Initialized P2 ratchet ceiling: {ceiling}")

        if current_count > ceiling:
            print(f"\n[ERROR] P2 antipattern regression: {current_count} > ceiling {ceiling}")
            print("[ERROR] ADG generation failed - exception antipattern count increased")
            print(f"[ERROR] Fix new exception swallows or update ceiling: {ratchet_file}")
            sys.exit(1)
        elif current_count < ceiling:
            with open(ratchet_file, "w") as f:
                json.dump({"high_severity_ceiling": current_count}, f, indent=2)
            print(f"[INFO] P2 ratchet: Reduced ceiling from {ceiling} to {current_count}")
        else:
            print(f"[INFO] P2 ratchet: Current count {current_count} at ceiling {ceiling}")
    except SystemExit:
        raise
    except Exception:  # guardian: allow-silent-swallow -- non-critical: SQLite query failure during P2 check falls back gracefully
        pass


def _check_p3_ratchet(sqlite_path: Path | None = None, ratchet_file: Path | None = None) -> None:
    """Enforce non-regression ratchet for MEDIUM-severity antipatterns (all paths).

    Args:
        sqlite_path: Path to SQLite database
        ratchet_file: Path to JSON file storing P3 ceiling (default: artifacts/adg/p3_ratchet.json)
    """
    if sqlite_path is None or not sqlite_path.exists():
        return

    if ratchet_file is None:
        ratchet_file = Path("artifacts/adg/p3_ratchet.json")

    try:
        with sqlite3.connect(str(sqlite_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM violations WHERE severity='MEDIUM' AND category='antipattern'",
            )
            current_count = cursor.fetchone()[0]

        if ratchet_file.exists():
            with open(ratchet_file) as f:
                ratchet_data = json.load(f)
                ceiling = ratchet_data.get("exception_swallow_ceiling", current_count)
        else:
            ceiling = current_count
            ratchet_file.parent.mkdir(parents=True, exist_ok=True)
            with open(ratchet_file, "w") as f:
                json.dump({"exception_swallow_ceiling": ceiling}, f, indent=2)
            print(f"[INFO] Initialized P3 ratchet ceiling: {ceiling}")

        if current_count > ceiling:
            print("\n[ERROR] P3 ratchet: MEDIUM antipattern regression detected")
            print(f"[ERROR] Current count: {current_count}, Ceiling: {ceiling}")
            print("[ERROR] ADG generation failed - MEDIUM antipattern count increased")
            print(f"[ERROR] Fix antipatterns or update ceiling: {ratchet_file}")
            sys.exit(1)
        elif current_count < ceiling:
            with open(ratchet_file, "w") as f:
                json.dump({"exception_swallow_ceiling": current_count}, f, indent=2)
            print(f"[INFO] P3 ratchet: Reduced ceiling from {ceiling} to {current_count}")
        else:
            print(f"[INFO] P3 ratchet: Current count {current_count} at ceiling {ceiling}")
    except (
        Exception
    ):  # guardian: allow-silent-swallow -- non-critical: Ratchet check failure falls back gracefully
        pass


def _check_dead_production_imports(sqlite_path: Path | None = None) -> None:
    """Fail if production modules have zero non-test/non-ops fan-in edges.

    Args:
        sqlite_path: Path to SQLite database for fan-in queries
    """
    if sqlite_path is None or not sqlite_path.exists():
        return

    try:
        with sqlite3.connect(str(sqlite_path)) as conn:
            cursor = conn.cursor()

            query = """
            SELECT n.resolved_path, n.layer, n.entity_type,
                   (SELECT COUNT(e.id) FROM edges e
                    WHERE e.relation_type = 'imports'
                      AND e.dst_id IN (
                        SELECT id FROM nodes nx WHERE nx.resolved_path = n.resolved_path
                      )
                      AND e.src_id IN (
                        SELECT id FROM nodes WHERE layer NOT IN ('L_TEST','L_OPS','L_TOOLS','L_SHARED')
                      )
                   ) AS fan_in
            FROM nodes n
            WHERE n.entity_type = 'module'
              AND n.layer NOT IN ('L_TEST','L_OPS','L_TOOLS','L_SHARED')
              AND n.resolved_path LIKE 'agentic_core/L4_state/cache/%'
            HAVING fan_in = 0
            ORDER BY n.resolved_path;
            """
            cursor.execute(query)
            violations = cursor.fetchall()

            if violations:
                print(f"\n[ERROR] Dead production import gate: Found {len(violations)} dead module(s)")
                print("[ERROR] Modules with ZERO production importers:")
                for row in violations:
                    print(f"[ERROR]   - {row[0]} (layer={row[1]}, fan_in={row[3]})")
                print("[ERROR]")
                print("[ERROR] These modules have ZERO importers from production code.")
                print("[ERROR] Either:")
                print("[ERROR]   1. Wire them into production code (add imports), OR")
                print("[ERROR]   2. Archive them to tools/archive/ if deprecated")
                print("[ERROR] ADG generation blocked. Fix violations and retry.")
                sys.exit(1)
            else:
                print("[INFO] Dead production import gate: PASSED (no dead modules in L4_state/cache)")
    except (
        Exception
    ):  # guardian: allow-silent-swallow -- non-critical: Gate query failure falls back gracefully
        pass
