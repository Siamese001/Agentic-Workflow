"""P0/P1/P2 quality gates, structural conformance, agentic anti-pattern detection for ADG generation."""

from __future__ import annotations

import copy
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]

# --- Violation class constants ---
CLASS_HYGIENE = "hygiene"
CLASS_STRUCTURAL = "structural_conformance"
CLASS_AGENTIC = "agentic_antipattern"

# Valid violation classes (used for validation)
VALID_VIOLATION_CLASSES = frozenset({CLASS_HYGIENE, CLASS_STRUCTURAL, CLASS_AGENTIC})


def _check_p0_violations(routing_summary: dict[str, int], sqlite_path: Path | None = None) -> None:
    """Fail if P0 layer violations, circular imports, or dynamic_exec are present (unconditional fail-fast).

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

            p0_count = len(unapproved)
            if p0_count > 0:
                print(f"\n[ERROR] P0 layer violations detected: {p0_count}")
                for sf, ln in unapproved[:10]:
                    print(f"[ERROR]   {sf}:{ln}")
                print("[ERROR] ADG generation failed - P0 layer violations present")
                print("[ERROR] Fix layer violations before regenerating ADG")
                sys.exit(1)
        except SystemExit:
            raise
        except Exception:  # guardian: allow-silent-swallow -- non-critical: SQLite query failure during P0 check falls back gracefully
            pass
    else:
        p0_count = routing_summary.get("by_severity", {}).get("critical", 0)
        if p0_count > 0:
            print(f"\n[ERROR] P0 layer violations detected: {p0_count}")
            print("[ERROR] ADG generation failed - P0 layer violations present")
            print("[ERROR] Fix layer violations before regenerating ADG")
            sys.exit(1)

    if sqlite_path is not None and sqlite_path.exists():
        try:
            with sqlite3.connect(str(sqlite_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type='in_cycle'")
                in_cycle_count = cursor.fetchone()[0]
                if in_cycle_count > 0:
                    print(f"\n[ERROR] P0 Tier 1A: Circular imports detected: {in_cycle_count}")
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
                    print(f"\n[ERROR] P0 Tier 1B: Dynamic execution detected: {dynamic_exec_count}")
                    print("[ERROR] ADG generation failed - graph is provably incomplete")
                    print("[ERROR] Replace eval/exec/dynamic imports with static alternatives")
                    sys.exit(1)
        except Exception:  # guardian: allow-silent-swallow -- non-critical: SQLite query failure during Tier 1B check falls back gracefully
            pass


def _check_p1_ratchet(sqlite_path: Path | None = None, ratchet_file: Path | None = None) -> None:
    """Block if HIGH-severity antipatterns INCREASED vs prior run (P1 non-regression ratchet).

    Args:
        sqlite_path: Path to SQLite database for exception swallow queries
        ratchet_file: Path to JSON file storing P1 ceiling (default: artifacts/adg/p1_ratchet.json)
    """
    if sqlite_path is None or not sqlite_path.exists():
        return

    if ratchet_file is None:
        ratchet_file = ROOT / "artifacts" / "adg" / "p1_ratchet.json"
        # Backward-compat: migrate legacy p2_ratchet.json on first run
        if not ratchet_file.exists():
            legacy = ROOT / "artifacts" / "adg" / "p2_ratchet.json"
            if legacy.exists():
                legacy.rename(ratchet_file)

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
            print(f"[INFO] Initialized P1 ratchet ceiling: {ceiling}")

        if current_count > ceiling:
            print(f"\n[ERROR] P1 antipattern regression: {current_count} > ceiling {ceiling}")
            print("[ERROR] ADG generation failed - HIGH antipattern count increased")
            print(f"[ERROR] Fix new exception swallows or update ceiling: {ratchet_file}")
            sys.exit(1)
        elif current_count < ceiling:
            with open(ratchet_file, "w") as f:
                json.dump({"high_severity_ceiling": current_count}, f, indent=2)
            print(f"[INFO] P1 ratchet: Reduced ceiling from {ceiling} to {current_count}")
        else:
            print(f"[INFO] P1 ratchet: Current count {current_count} at ceiling {ceiling}")
    except SystemExit:
        raise
    except Exception:  # guardian: allow-silent-swallow -- non-critical: SQLite query failure during P1 ratchet falls back gracefully
        pass


def _check_p2_ratchet(sqlite_path: Path | None = None, ratchet_file: Path | None = None) -> None:
    """Enforce non-regression ratchet for MEDIUM-severity antipatterns (P2 non-regression ratchet).

    Args:
        sqlite_path: Path to SQLite database
        ratchet_file: Path to JSON file storing P2 ceiling (default: artifacts/adg/p2_ratchet.json)
    """
    if sqlite_path is None or not sqlite_path.exists():
        return

    if ratchet_file is None:
        ratchet_file = ROOT / "artifacts" / "adg" / "p2_ratchet.json"
        # Backward-compat: migrate legacy p3_ratchet.json on first run
        if not ratchet_file.exists():
            legacy = ROOT / "artifacts" / "adg" / "p3_ratchet.json"
            if legacy.exists():
                legacy.rename(ratchet_file)

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
            print(f"[INFO] Initialized P2 ratchet ceiling: {ceiling}")

        if current_count > ceiling:
            print("\n[ERROR] P2 ratchet: MEDIUM antipattern regression detected")
            print(f"[ERROR] Current count: {current_count}, Ceiling: {ceiling}")
            print("[ERROR] ADG generation failed - MEDIUM antipattern count increased")
            print(f"[ERROR] Fix antipatterns or update ceiling: {ratchet_file}")
            sys.exit(1)
        elif current_count < ceiling:
            with open(ratchet_file, "w") as f:
                json.dump({"exception_swallow_ceiling": current_count}, f, indent=2)
            print(f"[INFO] P2 ratchet: Reduced ceiling from {ceiling} to {current_count}")
        else:
            print(f"[INFO] P2 ratchet: Current count {current_count} at ceiling {ceiling}")
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


# ---------------------------------------------------------------------------
# SC/AP configuration + audit-mode gate infrastructure (Wave 1)
# ---------------------------------------------------------------------------

_DEFAULT_SC_AP_CONFIG_PATH = ROOT / "artifacts" / "adg" / "sc_ap_config.json"

_DEFAULT_SC_AP_CONFIG: dict[str, dict[str, Any]] = {
    "SC-1": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Gravity import / illegal layer reach",
    },
    "SC-2": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "L2 execution lifecycle conformance",
    },
    "SC-3": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "UWG-only durable write conformance",
    },
    "SC-4": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Capability/tool/provider choke-point",
    },
    "AP-1": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Unsafe text-to-action path",
    },
    "AP-2": {"enabled": False, "audit_mode": True, "promoted_date": None, "label": "L2 phase bypass"},
    "AP-3": {"enabled": False, "audit_mode": True, "promoted_date": None, "label": "Provider/tool bypass"},
    "AP-4": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Direct durable write breach",
    },
    "SC-5": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Agentic spine completeness",
    },
    "SC-6": {"enabled": False, "audit_mode": True, "promoted_date": None, "label": "L0/L1/L6 role purity"},
    "SC-7": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Grounding contract / C0-PA separation",
    },
    "SC-8": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Trace/replay/eval surface coverage",
    },
    "AP-5": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Tool overlap / ambiguous surfaces",
    },
    "AP-6": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Premature multi-agent sprawl",
    },
    "AP-7": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Duplicate specialization",
    },
    "AP-8": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Missing trace/eval on action paths",
    },
    "AP-9": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Infrastructure spread / service locator drift",
    },
    "AP-10": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Live/future mutation confusion",
    },
    "AP-11": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Poorly scoped work contracts",
    },
    "AP-12": {"enabled": False, "audit_mode": True, "promoted_date": None, "label": "Prompt scatter"},
    "AP-13": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Retry/heal without exit criteria",
    },
    "AP-14": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Retrieval without evidence contract",
    },
    "AP-15": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Agent count outrunning tool surfaces",
    },
    "AP-16": {"enabled": False, "audit_mode": True, "promoted_date": None, "label": "Dormant infrastructure"},
    "AP-17": {
        "enabled": False,
        "audit_mode": True,
        "promoted_date": None,
        "label": "Agentic semantic precision gaps",
    },
}


def _load_sc_ap_config(config_path: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load SC/AP check configuration, merging with defaults for missing keys.

    Args:
        config_path: Path to sc_ap_config.json. If None, uses default location.

    Returns:
        Merged config dict keyed by check ID (e.g. "SC-1", "AP-3").
    """
    if config_path is None:
        config_path = _DEFAULT_SC_AP_CONFIG_PATH

    config = copy.deepcopy(_DEFAULT_SC_AP_CONFIG)
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            user_config = json.load(f)
        for check_id, check_cfg in user_config.items():
            if check_id in config:
                config[check_id].update(check_cfg)
            else:
                config[check_id] = check_cfg
    return config


def _save_sc_ap_config(config: dict[str, dict[str, Any]], config_path: Path | None = None) -> None:
    """Persist SC/AP config to disk.

    Args:
        config: Config dict to save.
        config_path: Target path. If None, uses default location.
    """
    if config_path is None:
        config_path = _DEFAULT_SC_AP_CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, sort_keys=True)


def _insert_sc_ap_violation(
    conn: sqlite3.Connection,
    check_id: str,
    violation_class: str,
    severity: str,
    source_file: str,
    line_no: int,
    evidence: str,
) -> None:
    """Insert a structural conformance or agentic anti-pattern violation row.

    Uses edge_id=0 since SC/AP violations are graph-query results, not individual edge detections.

    Args:
        conn: Open SQLite connection.
        check_id: Check identifier (e.g. "SC-1", "AP-3").
        violation_class: One of CLASS_STRUCTURAL or CLASS_AGENTIC.
        severity: P-band severity ("P0", "P1", "P2", "P3").
        source_file: Source file path of the violation.
        line_no: Line number (0 if not applicable).
        evidence: Human-readable evidence string.
    """
    conn.execute(
        "INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity, violation_class) "
        "VALUES (0, ?, ?, ?, ?, ?, ?)",
        (check_id, evidence, source_file, line_no, severity, violation_class),
    )


_GRAVITY_FORBIDDEN: dict[str, set[str]] = {
    "L0": {"L1", "L2", "L3", "L6"},
    "L1": {"L2", "L3", "L6"},
    "L2": {"L0", "L1", "L6"},
    "L6": {"L2"},
}

_SC_CHECK_DISPATCH: dict[str, str] = {
    "SC-1": "_query_sc1_gravity",
    "SC-2": "_query_sc2_lifecycle",
    "SC-3": "_query_sc3_uwg_write",
    "SC-4": "_query_sc4_choke_point",
}


def _query_sc1_gravity(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """SC-1: Gravity import / illegal layer reach."""
    violations: list[dict[str, Any]] = []
    rows = conn.execute(
        "SELECT e.source_file, e.line_no, n_src.layer, n_dst.layer, e.relation_type "
        "FROM edges e "
        "JOIN nodes n_src ON e.src_id = n_src.id "
        "JOIN nodes n_dst ON e.dst_id = n_dst.id "
        "WHERE e.relation_type IN ('imports', 'reads_from', 'controls_flow', 'flows_to') "
        "  AND n_src.layer IS NOT NULL AND n_src.layer != '' "
        "  AND n_dst.layer IS NOT NULL AND n_dst.layer != '' "
        "  AND n_src.layer != n_dst.layer",
    ).fetchall()
    for src_file, line_no, src_layer, dst_layer, rel_type in rows:
        forbidden = _GRAVITY_FORBIDDEN.get(src_layer, set())
        if dst_layer in forbidden:
            violations.append(
                {
                    "source_file": src_file or "",
                    "line_no": line_no or 0,
                    "evidence": f"{src_layer}->{dst_layer} via {rel_type}",
                }
            )
    return violations


def _query_sc2_lifecycle(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """SC-2: L2 execution lifecycle conformance (E1-E5 phases)."""
    violations: list[dict[str, Any]] = []
    exec_modules = conn.execute(
        "SELECT DISTINCT e.src_id, n.adg_name, n.resolved_path "
        "FROM edges e JOIN nodes n ON e.src_id = n.id "
        "WHERE n.layer = 'L2' "
        "  AND e.relation_type IN ('invokes_provider', 'resolves_callsite')",
    ).fetchall()
    for src_id, adg_name, resolved_path in exec_modules:
        phase_edges = conn.execute(
            "SELECT DISTINCT e.relation_type FROM edges e WHERE e.src_id = ? "
            "AND e.relation_type IN ("
            "  'enters_sandbox', 'stamps_work_contract',"
            "  'validates_uwg_intent', 'checks_capability_set',"
            "  'invokes_provider', 'resolves_callsite',"
            "  'orchestrates_healing', 'heals',"
            "  'packages_execution_trace', 'applies_hmac_seal'"
            ")",
            (src_id,),
        ).fetchall()
        found_phases = set()
        for (rt,) in phase_edges:
            if rt in ("enters_sandbox", "stamps_work_contract"):
                found_phases.add("E1")
            elif rt in ("validates_uwg_intent", "checks_capability_set"):
                found_phases.add("E2")
            elif rt in ("invokes_provider", "resolves_callsite"):
                found_phases.add("E3")
            elif rt in ("orchestrates_healing", "heals"):
                found_phases.add("E4")
            elif rt in ("packages_execution_trace", "applies_hmac_seal"):
                found_phases.add("E5")
        missing = {"E1", "E2", "E3", "E4", "E5"} - found_phases
        if len(missing) >= 2:
            violations.append(
                {
                    "source_file": resolved_path or "",
                    "line_no": 0,
                    "evidence": f"{adg_name} missing phases: {', '.join(sorted(missing))}",
                }
            )
    return violations


def _query_sc3_uwg_write(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """SC-3: UWG-only durable write conformance."""
    violations: list[dict[str, Any]] = []
    rows = conn.execute(
        "SELECT e.source_file, e.line_no, n_src.layer, n_src.adg_name "
        "FROM edges e "
        "JOIN nodes n_src ON e.src_id = n_src.id "
        "WHERE e.relation_type IN ('writes_to', 'writes_through') "
        "  AND n_src.layer IN ('L2', 'L6') "
        "  AND e.src_id NOT IN ("
        "    SELECT e2.src_id FROM edges e2 "
        "    WHERE e2.relation_type IN ('validates_uwg_intent', 'commits_mutation_durable')"
        "  )",
    ).fetchall()
    for src_file, line_no, layer, adg_name in rows:
        violations.append(
            {
                "source_file": src_file or "",
                "line_no": line_no or 0,
                "evidence": f"{adg_name} ({layer}) writes without UWG governance",
            }
        )
    return violations


def _query_sc4_choke_point(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """SC-4: Capability/tool/provider choke-point conformance."""
    violations: list[dict[str, Any]] = []
    rows = conn.execute(
        "SELECT e.source_file, e.line_no, n_src.layer, n_src.adg_name "
        "FROM edges e "
        "JOIN nodes n_src ON e.src_id = n_src.id "
        "WHERE e.relation_type = 'invokes_provider' "
        "  AND e.src_id NOT IN ("
        "    SELECT e2.src_id FROM edges e2 "
        "    WHERE e2.relation_type IN ("
        "      'enters_sandbox', 'issues_capability_token', "
        "      'checks_capability_set', 'validates_capability'"
        "    )"
        "  )",
    ).fetchall()
    for src_file, line_no, layer, adg_name in rows:
        violations.append(
            {
                "source_file": src_file or "",
                "line_no": line_no or 0,
                "evidence": f"{adg_name} ({layer}) invokes provider without capability gate",
            }
        )
    return violations


def _check_structural_conformance(
    sqlite_path: Path | None = None,
    config_path: Path | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Run structural conformance checks (SC-1 through SC-4, more in future waves).

    In audit mode (default), violations are logged and inserted into the violations table
    but do NOT cause sys.exit. When audit_mode is False for a check, violations cause sys.exit(1).

    Args:
        sqlite_path: Path to the ADG SQLite database.
        config_path: Path to sc_ap_config.json. If None, uses default.

    Returns:
        Dict mapping check_id to list of violation dicts (for reporting).
    """
    results: dict[str, list[dict[str, Any]]] = {}

    if sqlite_path is None or not sqlite_path.exists():
        return results

    config = _load_sc_ap_config(config_path)

    sc_checks = {k: v for k, v in config.items() if k.startswith("SC-") and v.get("enabled", False)}

    if not sc_checks:
        print("[ADG] Structural conformance: no checks enabled")
        return results

    with sqlite3.connect(str(sqlite_path)) as conn:
        for check_id, check_cfg in sorted(sc_checks.items()):
            audit = check_cfg.get("audit_mode", True)
            label = check_cfg.get("label", check_id)
            violations: list[dict[str, Any]] = []

            query_fn_name = _SC_CHECK_DISPATCH.get(check_id)
            if query_fn_name:
                query_fn = globals().get(query_fn_name)
                if query_fn is not None:
                    try:
                        violations = query_fn(conn)
                    except sqlite3.OperationalError:
                        pass

            for v in violations:
                _insert_sc_ap_violation(
                    conn,
                    check_id,
                    CLASS_STRUCTURAL,
                    "P0",
                    v.get("source_file", ""),
                    v.get("line_no", 0),
                    v.get("evidence", ""),
                )
            conn.commit()

            results[check_id] = violations
            count = len(violations)

            if count > 0:
                mode_tag = "[AUDIT]" if audit else "[BLOCK]"
                print(f"{mode_tag} {check_id} ({label}): {count} violation(s)")
                if not audit:
                    print(f"[ERROR] {check_id} structural conformance check FAILED")
                    sys.exit(1)
            else:
                print(f"[ADG] {check_id} ({label}): PASSED")

    return results


_AP_CHECK_DISPATCH: dict[str, str] = {
    "AP-1": "_query_ap1_text_to_action",
    "AP-2": "_query_ap2_phase_bypass",
    "AP-3": "_query_ap3_provider_bypass",
    "AP-4": "_query_ap4_direct_write",
}


def _query_ap1_text_to_action(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-1: Unsafe text-to-action path — flows_to reaching invokes_provider without guardrail."""
    violations: list[dict[str, Any]] = []
    rows = conn.execute(
        "SELECT DISTINCT e.source_file, e.line_no, n_src.adg_name "
        "FROM edges e "
        "JOIN nodes n_src ON e.src_id = n_src.id "
        "WHERE e.relation_type = 'flows_to' "
        "  AND e.dst_id IN ("
        "    SELECT e2.src_id FROM edges e2 "
        "    WHERE e2.relation_type IN ('invokes_provider', 'writes_to')"
        "  ) "
        "  AND e.src_id NOT IN ("
        "    SELECT e3.src_id FROM edges e3 "
        "    WHERE e3.relation_type IN ('applies_guardrail', 'validates_uwg_intent')"
        "  )",
    ).fetchall()
    for src_file, line_no, adg_name in rows:
        violations.append(
            {
                "source_file": src_file or "",
                "line_no": line_no or 0,
                "evidence": f"{adg_name} flows to action without guardrail",
            }
        )
    return violations


def _query_ap2_phase_bypass(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-2: L2 phase bypass — execution without validate (E2) or seal (E5)."""
    violations: list[dict[str, Any]] = []
    exec_modules = conn.execute(
        "SELECT DISTINCT e.src_id, n.adg_name, n.resolved_path "
        "FROM edges e JOIN nodes n ON e.src_id = n.id "
        "WHERE n.layer = 'L2' "
        "  AND e.relation_type IN ('invokes_provider', 'resolves_callsite')",
    ).fetchall()
    for src_id, adg_name, resolved_path in exec_modules:
        phase_edges = conn.execute(
            "SELECT DISTINCT e.relation_type FROM edges e WHERE e.src_id = ? "
            "AND e.relation_type IN ("
            "  'validates_uwg_intent', 'checks_capability_set',"
            "  'packages_execution_trace', 'applies_hmac_seal'"
            ")",
            (src_id,),
        ).fetchall()
        has_validate = any(rt in ("validates_uwg_intent", "checks_capability_set") for (rt,) in phase_edges)
        has_seal = any(rt in ("packages_execution_trace", "applies_hmac_seal") for (rt,) in phase_edges)
        if not has_validate or not has_seal:
            missing = []
            if not has_validate:
                missing.append("E2-validate")
            if not has_seal:
                missing.append("E5-seal")
            violations.append(
                {
                    "source_file": resolved_path or "",
                    "line_no": 0,
                    "evidence": f"{adg_name} executes without {', '.join(missing)}",
                }
            )
    return violations


def _query_ap3_provider_bypass(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-3: Provider/tool bypass — SC-4 scoped to production layers (agentic_core/)."""
    violations: list[dict[str, Any]] = []
    rows = conn.execute(
        "SELECT e.source_file, e.line_no, n_src.layer, n_src.adg_name "
        "FROM edges e "
        "JOIN nodes n_src ON e.src_id = n_src.id "
        "WHERE e.relation_type = 'invokes_provider' "
        "  AND e.source_file LIKE 'agentic_core/%' "
        "  AND e.src_id NOT IN ("
        "    SELECT e2.src_id FROM edges e2 "
        "    WHERE e2.relation_type IN ("
        "      'enters_sandbox', 'issues_capability_token', "
        "      'checks_capability_set', 'validates_capability'"
        "    )"
        "  )",
    ).fetchall()
    for src_file, line_no, layer, adg_name in rows:
        violations.append(
            {
                "source_file": src_file or "",
                "line_no": line_no or 0,
                "evidence": f"{adg_name} ({layer}) invokes provider in agentic_core/ without capability gate",
            }
        )
    return violations


def _query_ap4_direct_write(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-4: Direct durable write breach — any layer writing to state without governed path."""
    violations: list[dict[str, Any]] = []
    rows = conn.execute(
        "SELECT e.source_file, e.line_no, n_src.layer, n_src.adg_name "
        "FROM edges e "
        "JOIN nodes n_src ON e.src_id = n_src.id "
        "WHERE e.relation_type IN ('writes_to', 'writes_through') "
        "  AND e.src_id NOT IN ("
        "    SELECT e2.src_id FROM edges e2 "
        "    WHERE e2.relation_type IN ('validates_uwg_intent', 'commits_mutation_durable')"
        "  )",
    ).fetchall()
    for src_file, line_no, layer, adg_name in rows:
        violations.append(
            {
                "source_file": src_file or "",
                "line_no": line_no or 0,
                "evidence": f"{adg_name} ({layer}) direct durable write without governed path",
            }
        )
    return violations


def _check_agentic_antipatterns(
    sqlite_path: Path | None = None,
    config_path: Path | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Run agentic anti-pattern checks (AP-1 through AP-4, more in future waves).

    In audit mode (default), violations are logged and inserted into the violations table
    but do NOT cause sys.exit. When audit_mode is False for a check, violations cause sys.exit(1).

    Args:
        sqlite_path: Path to the ADG SQLite database.
        config_path: Path to sc_ap_config.json. If None, uses default.

    Returns:
        Dict mapping check_id to list of violation dicts (for reporting).
    """
    results: dict[str, list[dict[str, Any]]] = {}

    if sqlite_path is None or not sqlite_path.exists():
        return results

    config = _load_sc_ap_config(config_path)

    ap_checks = {k: v for k, v in config.items() if k.startswith("AP-") and v.get("enabled", False)}

    if not ap_checks:
        print("[ADG] Agentic anti-patterns: no checks enabled")
        return results

    with sqlite3.connect(str(sqlite_path)) as conn:
        for check_id, check_cfg in sorted(ap_checks.items()):
            audit = check_cfg.get("audit_mode", True)
            label = check_cfg.get("label", check_id)
            violations: list[dict[str, Any]] = []

            query_fn_name = _AP_CHECK_DISPATCH.get(check_id)
            if query_fn_name:
                query_fn = globals().get(query_fn_name)
                if query_fn is not None:
                    try:
                        violations = query_fn(conn)
                    except sqlite3.OperationalError:
                        pass

            for v in violations:
                _insert_sc_ap_violation(
                    conn,
                    check_id,
                    CLASS_AGENTIC,
                    "P0",
                    v.get("source_file", ""),
                    v.get("line_no", 0),
                    v.get("evidence", ""),
                )
            conn.commit()

            results[check_id] = violations
            count = len(violations)

            if count > 0:
                mode_tag = "[AUDIT]" if audit else "[BLOCK]"
                print(f"{mode_tag} {check_id} ({label}): {count} violation(s)")
                if not audit:
                    print(f"[ERROR] {check_id} agentic anti-pattern check FAILED")
                    sys.exit(1)
            else:
                print(f"[ADG] {check_id} ({label}): PASSED")

    return results
