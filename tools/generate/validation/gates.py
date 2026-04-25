"""P0/P1/P2 quality gates, structural conformance, agentic anti-pattern detection for ADG generation."""

from __future__ import annotations

import copy
import json
import sqlite3
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


def _discover_repo_root(start: Path) -> Path:
    """Best-effort repository root discovery for direct script and package execution."""
    for candidate in (start, *start.parents):
        if (candidate / "agentic_core").exists() or (candidate / ".git").exists():
            return candidate
        if candidate.name == "tools" and (candidate / "generate").exists():
            return candidate.parent
    return start.parents[3] if len(start.parents) > 3 else start.parent


ROOT = _discover_repo_root(Path(__file__).resolve().parent)

# --- Violation class constants ---
CLASS_HYGIENE = "hygiene"
CLASS_STRUCTURAL = "structural_conformance"
CLASS_AGENTIC = "agentic_antipattern"

# Valid violation classes (used for validation)
VALID_VIOLATION_CLASSES = frozenset({CLASS_HYGIENE, CLASS_STRUCTURAL, CLASS_AGENTIC})


def _load_json_file(path: Path) -> dict[str, Any]:
    """Load a JSON object from disk and validate its shape."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    """Atomically persist ratchet state to avoid truncated files on interruption."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
        json.dump(payload, tmp, indent=2)
        tmp.flush()
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def _fail_closed_gate(gate_name: str, exc: Exception) -> None:
    """Abort the run when a gate cannot be evaluated reliably.

    Plan adg-cascading-ratchet-defer-exit-a41828 (Wave B): when the
    ``ADG_CONTINUE_ON_P0=1`` env var (or ``--continue-on-p0`` CLI flag) is
    set, the failure is recorded into the shared deferred-failure registry
    instead of terminating the process. ``main()`` reads the registry at
    the end of the run and exits with the first recorded non-zero rc.
    """
    from tools.generate.integration.deferred_failures import record_or_exit

    print(f"[ERROR] {gate_name} failed closed: {exc}")
    record_or_exit(gate_name, 1, message=str(exc))


def _check_p0_violations(
    routing_summary: dict[str, int],
    sqlite_path: Path | None = None,
    plan_path: Path | None = None,
) -> None:
    """Fail if P0 layer violations, circular imports, or dynamic_exec are present.

    Args:
        routing_summary: Dictionary with by_severity counts
        sqlite_path: Path to SQLite database for in_cycle/dynamic_exec queries
        plan_path: Optional emitted remediation-wave artifact to surface on failure
    """

    def _print_plan_hint() -> None:
        if plan_path is not None:
            print(f"[ERROR] See remediation wave plan: {plan_path}")

    if sqlite_path is not None and sqlite_path.exists():
        try:
            with sqlite3.connect(str(sqlite_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT source_file, line_no FROM edges WHERE relation_type='violates'")
                violation_rows = cursor.fetchall()

            # SSOT: tools/adg/core/guardian_filter.is_layer_violation_exempted
            # (shared by reports.py and the adg_p0_wave_plan MCP tool).
            from tools.adg.core.guardian_filter import is_layer_violation_exempted

            unapproved = []
            for source_file, line_no in violation_rows:
                normalized_source_file = source_file or ""
                if "tools/archive/" in normalized_source_file:
                    print(f"[INFO] Skipping archived file: {normalized_source_file}")
                    continue

                if is_layer_violation_exempted(normalized_source_file, line_no, repo_root=ROOT):
                    continue

                # Not exempted — record as unapproved.
                unapproved.append((normalized_source_file, line_no))

            p0_count = len(unapproved)
            if p0_count > 0:
                print(f"\n[ERROR] P0 layer violations detected: {p0_count}")
                for sf, ln in unapproved[:10]:
                    print(f"[ERROR]   {sf}:{ln}")
                print("[ERROR] ADG generation failed - P0 layer violations present")
                print("[ERROR] Fix layer violations before regenerating ADG")
                _print_plan_hint()
                sys.exit(1)
        except SystemExit:
            raise
        except sqlite3.Error as exc:
            _fail_closed_gate("P0 violation query", exc)
    else:
        p0_count = routing_summary.get("by_severity", {}).get("critical", 0)
        if p0_count > 0:
            print(f"\n[ERROR] P0 layer violations detected: {p0_count}")
            print("[ERROR] ADG generation failed - P0 layer violations present")
            print("[ERROR] Fix layer violations before regenerating ADG")
            _print_plan_hint()
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
                    _print_plan_hint()
                    sys.exit(1)
        except sqlite3.Error as exc:
            _fail_closed_gate("P0 Tier 1A circular import query", exc)

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
                    _print_plan_hint()
                    sys.exit(1)
        except sqlite3.Error as exc:
            _fail_closed_gate("P0 Tier 1B dynamic execution query", exc)


def _surface_override_ceiling_bump(base_ceiling: int) -> tuple[int, bool]:
    """Return the P1 ceiling + whether the ADR-024 Part B bump is applied.

    ADR-024 OQ#2 (resolved 2026-04-24): the ``P1_RATCHET_POLICY_V2`` env-flag
    gates a +48 ceiling bump to accommodate ~48 items promoted P2/P3 → P1 by
    :data:`agentic_core.adg.severity_bands.SURFACE_OVERRIDE`. When the flag is
    OFF (default), returns ``base_ceiling`` unchanged. When ON, returns
    ``base_ceiling + 48``.

    Separating this from the in-line math keeps the ratchet's rollback story
    trivial: flipping the env-flag OFF fully reverts the bump with no code
    change.
    """
    import os as _os

    flag = _os.environ.get("P1_RATCHET_POLICY_V2", "").strip().lower()
    if flag in {"1", "true", "yes", "on"}:
        return base_ceiling + 48, True
    return base_ceiling, False


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
            ratchet_data = _load_json_file(ratchet_file)
            base_ceiling = ratchet_data.get(
                "high_severity_ceiling", ratchet_data.get("p2_antipattern_ceiling", current_count)
            )
        else:
            base_ceiling = current_count
            _atomic_json_write(ratchet_file, {"high_severity_ceiling": base_ceiling})
            print(f"[INFO] Initialized P1 ratchet ceiling: {base_ceiling}")

        # ADR-024 Part B: when P1_RATCHET_POLICY_V2 env-flag is ON, allow up to
        # +48 above the stored ceiling to accommodate SURFACE_OVERRIDE promotions.
        # When OFF (default), ceiling is the stored value (no behavior change).
        ceiling, bump_applied = _surface_override_ceiling_bump(base_ceiling)
        if bump_applied:
            print(
                f"[INFO] P1 ratchet: P1_RATCHET_POLICY_V2=ON, effective ceiling "
                f"{ceiling} (= stored {base_ceiling} + 48 ADR-024 Part B bump)"
            )

        if current_count > ceiling:
            from tools.generate.integration.deferred_failures import record_or_exit

            print(f"\n[ERROR] P1 antipattern regression: {current_count} > ceiling {ceiling}")
            print("[ERROR] ADG generation failed - HIGH antipattern count increased")
            print(f"[ERROR] Fix new exception swallows or update ceiling: {ratchet_file}")
            record_or_exit(
                "P1_ratchet",
                1,
                message=f"current={current_count} > ceiling={ceiling}",
            )
            return  # only reached when defer-exit is on
        elif current_count < base_ceiling:
            # Only ratchet DOWN against the stored base, not the bumped ceiling,
            # so turning the flag off later doesn't create an artificial regression.
            _atomic_json_write(ratchet_file, {"high_severity_ceiling": current_count})
            print(f"[INFO] P1 ratchet: Reduced ceiling from {base_ceiling} to {current_count}")
        else:
            print(f"[INFO] P1 ratchet: Current count {current_count} within ceiling {ceiling}")
    except SystemExit:
        raise
    except (sqlite3.Error, OSError, json.JSONDecodeError, ValueError) as exc:
        _fail_closed_gate("P1 ratchet", exc)


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
            ratchet_data = _load_json_file(ratchet_file)
            ceiling = ratchet_data.get("exception_swallow_ceiling", current_count)
        else:
            ceiling = current_count
            _atomic_json_write(ratchet_file, {"exception_swallow_ceiling": ceiling})
            print(f"[INFO] Initialized P2 ratchet ceiling: {ceiling}")

        if current_count > ceiling:
            from tools.generate.integration.deferred_failures import record_or_exit

            print("\n[ERROR] P2 ratchet: MEDIUM antipattern regression detected")
            print(f"[ERROR] Current count: {current_count}, Ceiling: {ceiling}")
            print("[ERROR] ADG generation failed - MEDIUM antipattern count increased")
            print(f"[ERROR] Fix antipatterns or update ceiling: {ratchet_file}")
            record_or_exit(
                "P2_ratchet",
                1,
                message=f"current={current_count} > ceiling={ceiling}",
            )
            return  # only reached when defer-exit is on
        elif current_count < ceiling:
            _atomic_json_write(ratchet_file, {"exception_swallow_ceiling": current_count})
            print(f"[INFO] P2 ratchet: Reduced ceiling from {ceiling} to {current_count}")
        else:
            print(f"[INFO] P2 ratchet: Current count {current_count} at ceiling {ceiling}")
    except SystemExit:
        raise
    except (sqlite3.Error, OSError, json.JSONDecodeError, ValueError) as exc:
        _fail_closed_gate("P2 ratchet", exc)


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
            SELECT n.resolved_path, n.layer, n.entity_type, 0 AS fan_in
            FROM nodes n
            WHERE n.entity_type = 'module'
              AND n.layer NOT IN ('L_TEST','L_OPS','L_TOOLS','L_SHARED')
              AND n.resolved_path LIKE 'agentic_core/L4_state/cache/%'
              AND NOT EXISTS (
                SELECT 1
                FROM edges e
                JOIN nodes dst ON dst.id = e.dst_id
                JOIN nodes src ON src.id = e.src_id
                WHERE e.relation_type = 'imports'
                  AND dst.resolved_path = n.resolved_path
                  AND src.layer NOT IN ('L_TEST','L_OPS','L_TOOLS','L_SHARED')
              )
            ORDER BY n.resolved_path;
            """
            cursor.execute(query)
            raw_violations = cursor.fetchall()

            def _is_tombstoned(resolved_path: str) -> bool:
                abs_path = ROOT / resolved_path
                try:
                    with open(abs_path, encoding="utf-8") as fh:
                        head = fh.read(512)
                    return "TOMBSTONED" in head
                except OSError:
                    return False

            violations = [row for row in raw_violations if not _is_tombstoned(row[0])]

            if violations:
                from tools.generate.integration.deferred_failures import record_or_exit

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
                record_or_exit(
                    "dead_production_imports",
                    1,
                    message=f"{len(violations)} dead module(s)",
                )
                return  # only reached when defer-exit is on
            else:
                print("[INFO] Dead production import gate: PASSED (no dead modules in L4_state/cache)")
    except SystemExit:
        raise
    except sqlite3.Error as exc:
        _fail_closed_gate("Dead production import gate", exc)


# ---------------------------------------------------------------------------
# SC/AP configuration + audit-mode gate infrastructure (Wave 1)
# ---------------------------------------------------------------------------

_DEFAULT_SC_AP_CONFIG_PATH = ROOT / "config" / "sc_ap_config.json"

_DEFAULT_SC_AP_CONFIG: dict[str, dict[str, Any]] = {
    "SC-1": {
        "enabled": True,
        "audit_mode": True,
        "promoted_date": "2026-04-17",
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
        "enabled": True,
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
    "AP-18": {
        "enabled": True,
        "audit_mode": False,
        "promoted_date": None,
        "label": "Prompt assembly subsystem disconnected from runtime",
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


def _ensure_violation_class_column(conn: sqlite3.Connection) -> None:
    """Add violation_class column to violations table if it does not exist.

    Handles live DBs that predate the SC/AP violation_class column.
    No-op if the violations table does not exist at all.
    """
    cols = {r[1] for r in conn.execute("PRAGMA table_info(violations)").fetchall()}
    if not cols:
        return  # violations table does not exist
    if "violation_class" not in cols:
        conn.execute("ALTER TABLE violations ADD COLUMN violation_class TEXT NOT NULL DEFAULT 'hygiene'")


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
    "SC-5": "_query_sc5_spine",
    "SC-6": "_query_sc6_role_purity",
    "SC-7": "_query_sc7_grounding",
    "SC-8": "_query_sc8_trace_coverage",
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
    # SSOT guardian-comment filter (shared by P0 violation scan, reports.py, and MCP wave_plan).
    from tools.adg.core.guardian_filter import is_layer_violation_exempted

    for src_file, line_no, src_layer, dst_layer, rel_type in rows:
        forbidden = _GRAVITY_FORBIDDEN.get(src_layer, set())
        if dst_layer not in forbidden:
            continue
        if is_layer_violation_exempted(src_file, line_no, repo_root=ROOT):
            continue
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
    for src_id, adg_name, resolved_path in exec_modules:  # progress_bar: bounded by exec_modules
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
        for (rt,) in phase_edges:  # progress_bar: bounded by phase_edges
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


def _query_sc5_spine(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """SC-5: Agentic spine completeness — verify end-to-end path L1→L0→L2."""
    violations: list[dict[str, Any]] = []
    spine_edges = {
        "pulls_context",
        "generates_prompt",
        "consumes_prompt",
        "packages_execution_trace",
    }
    found = set()
    for (rt,) in conn.execute(
        "SELECT DISTINCT relation_type FROM edges "
        "WHERE relation_type IN ('pulls_context','generates_prompt','consumes_prompt','packages_execution_trace')"
    ).fetchall():
        found.add(rt)
    missing = spine_edges - found
    if missing:
        violations.append(
            {
                "source_file": "",
                "line_no": 0,
                "evidence": f"Agentic spine missing edge types: {', '.join(sorted(missing))}",
            }
        )
    return violations


_ROLE_FORBIDDEN_EDGES: dict[str, list[str]] = {
    "L0": ["invokes_provider", "writes_to", "orchestrates_healing"],
    "L1": ["invokes_provider", "writes_to", "commits_mutation_durable"],
    "L6": ["invokes_provider", "writes_to", "commits_mutation_durable"],
}


def _query_sc6_role_purity(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """SC-6: Role purity for L0, L1, L6 — these layers should not have action edges."""
    violations: list[dict[str, Any]] = []
    for layer, forbidden in _ROLE_FORBIDDEN_EDGES.items():  # progress_bar: bounded by ROLE_FORBIDDEN_EDGES
        placeholders = ",".join(["?"] * len(forbidden))
        rows = conn.execute(
            "SELECT e.source_file, e.line_no, e.relation_type, n_src.adg_name "
            "FROM edges e JOIN nodes n_src ON e.src_id = n_src.id "
            f"WHERE n_src.layer = ? AND e.relation_type IN ({placeholders})",
            [layer, *forbidden],
        ).fetchall()
        for src_file, line_no, rel_type, adg_name in rows:
            violations.append(
                {
                    "source_file": src_file or "",
                    "line_no": line_no or 0,
                    "evidence": f"{adg_name} ({layer}) has forbidden edge: {rel_type}",
                }
            )
    return violations


def _query_sc7_grounding(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """SC-7: Grounding contract — consumes_prompt + invokes_provider requires pulls_context."""
    violations: list[dict[str, Any]] = []
    rows = conn.execute(
        "SELECT DISTINCT e.src_id, n.adg_name, n.resolved_path "
        "FROM edges e JOIN nodes n ON e.src_id = n.id "
        "WHERE e.relation_type = 'consumes_prompt' "
        "  AND e.src_id IN ("
        "    SELECT e2.src_id FROM edges e2 WHERE e2.relation_type = 'invokes_provider'"
        "  ) "
        "  AND e.src_id NOT IN ("
        "    SELECT e3.src_id FROM edges e3 WHERE e3.relation_type = 'pulls_context'"
        "  )",
    ).fetchall()
    for _src_id, adg_name, resolved_path in rows:
        violations.append(
            {
                "source_file": resolved_path or "",
                "line_no": 0,
                "evidence": f"{adg_name} consumes prompt and invokes provider without pulls_context",
            }
        )
    return violations


def _query_sc8_trace_coverage(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """SC-8: Trace/replay/eval surface coverage — action modules need trace edges."""
    violations: list[dict[str, Any]] = []
    rows = conn.execute(
        "SELECT DISTINCT n.adg_name, n.resolved_path "
        "FROM edges e JOIN nodes n ON e.src_id = n.id "
        "WHERE e.relation_type IN ('invokes_provider', 'writes_to') "
        "  AND e.src_id NOT IN ("
        "    SELECT e2.src_id FROM edges e2 "
        "    WHERE e2.relation_type IN ('packages_execution_trace', 'triggered_telemetry', 'scores_groundedness')"
        "  )",
    ).fetchall()
    for adg_name, resolved_path in rows:
        violations.append(
            {
                "source_file": resolved_path or "",
                "line_no": 0,
                "evidence": f"{adg_name} action-capable without trace/eval coverage",
            }
        )
    return violations


def _check_structural_conformance(
    sqlite_path: Path | None = None,
    config_path: Path | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Run structural conformance checks (SC-1 through SC-8).

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
        _ensure_violation_class_column(conn)
        for check_id, check_cfg in sorted(sc_checks.items()):  # progress_bar: bounded by sc_checks
            audit = check_cfg.get("audit_mode", True)
            label = check_cfg.get("label", check_id)
            violations: list[dict[str, Any]] = []

            query_fn_name = _SC_CHECK_DISPATCH.get(check_id)
            if query_fn_name:
                query_fn = globals().get(query_fn_name)
                if query_fn is not None:
                    try:
                        violations = query_fn(conn)
                    except sqlite3.OperationalError as _sc_err:
                        print(f"[ADG] WARNING: {check_id} query failed: {_sc_err}")
                else:
                    print(f"[ADG] WARNING: {check_id} dispatch function '{query_fn_name}' not found")

            sc_num = int(check_id.split("-")[1]) if "-" in check_id else 0
            severity = "P0" if sc_num <= 4 else "P1"

            for v in violations:
                _insert_sc_ap_violation(
                    conn,
                    check_id,
                    CLASS_STRUCTURAL,
                    severity,
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
                    from tools.generate.integration.deferred_failures import record_or_exit

                    print(f"[ERROR] {check_id} structural conformance check FAILED")
                    record_or_exit(
                        f"structural_conformance:{check_id}",
                        1,
                        message=f"{count} violation(s)",
                    )
                    # only reached when defer-exit is on; loop continues
                    # to the next check_id so the user sees the full
                    # picture in one run instead of one-fix-per-iteration
            else:
                print(f"[ADG] {check_id} ({label}): PASSED")

    return results


_AP_CHECK_DISPATCH: dict[str, str] = {
    "AP-1": "_query_ap1_text_to_action",
    "AP-2": "_query_ap2_phase_bypass",
    "AP-3": "_query_ap3_provider_bypass",
    "AP-4": "_query_ap4_direct_write",
    "AP-5": "_query_ap5_tool_overlap",
    "AP-6": "_query_ap6_manager_sprawl",
    "AP-7": "_query_ap7_dup_specialization",
    "AP-8": "_query_ap8_missing_trace",
    "AP-9": "_query_ap9_infra_spread",
    "AP-10": "_query_ap10_mutation_confusion",
    "AP-11": "_query_ap11_work_contracts",
    "AP-12": "_query_ap12_prompt_scatter",
    "AP-13": "_query_ap13_retry_no_exit",
    "AP-14": "_query_ap14_retrieval_no_evidence",
    "AP-15": "_query_ap15_agent_tool_ratio",
    "AP-16": "_query_ap16_dormant_infra",
    "AP-17": "_query_ap17_semantic_precision",
    "AP-18": "_query_ap18_prompt_assembly_orphan",
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
    for src_id, adg_name, resolved_path in exec_modules:  # progress_bar: bounded by exec_modules
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


def _query_ap5_tool_overlap(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-5: Tool overlap / ambiguous tool surfaces — nodes sharing >70% imports."""
    violations: list[dict[str, Any]] = []
    provider_nodes = conn.execute(
        "SELECT DISTINCT e.src_id, n.adg_name, n.resolved_path "
        "FROM edges e JOIN nodes n ON e.src_id = n.id "
        "WHERE e.relation_type = 'invokes_provider'",
    ).fetchall()
    if len(provider_nodes) < 2:
        return violations
    import_map: dict[int, set[int]] = {}
    for src_id, _, _ in provider_nodes:
        targets = conn.execute(
            "SELECT dst_id FROM edges WHERE src_id = ? AND relation_type = 'imports'",
            (src_id,),
        ).fetchall()
        import_map[src_id] = {t[0] for t in targets}
    checked: set[tuple[int, int]] = set()
    for i, (id_a, name_a, path_a) in enumerate(provider_nodes):  # progress_bar: bounded by provider_nodes
        for j, (id_b, name_b, _path_b) in enumerate(
            provider_nodes
        ):  # progress_bar: bounded by provider_nodes
            if i >= j:
                continue
            pair = (min(id_a, id_b), max(id_a, id_b))
            if pair in checked:
                continue
            checked.add(pair)
            set_a = import_map.get(id_a, set())
            set_b = import_map.get(id_b, set())
            if not set_a or not set_b:
                continue
            shared = len(set_a & set_b)
            total = min(len(set_a), len(set_b))
            if total > 0 and shared / total > 0.7:
                violations.append(
                    {
                        "source_file": path_a or "",
                        "line_no": 0,
                        "evidence": f"{name_a} and {name_b} share >{int(shared / total * 100)}% imports",
                    }
                )
    return violations


def _query_ap6_manager_sprawl(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-6: Premature multi-agent / manager sprawl — excessive routes_to_agent fan-out."""
    violations: list[dict[str, Any]] = []
    rows = conn.execute(
        "SELECT n.adg_name, n.resolved_path, COUNT(*) as cnt "
        "FROM edges e JOIN nodes n ON e.src_id = n.id "
        "WHERE e.relation_type IN ('routes_to_agent', 'dispatches_agent') "
        "GROUP BY e.src_id "
        "HAVING cnt > 5",
    ).fetchall()
    for adg_name, resolved_path, cnt in rows:
        violations.append(
            {
                "source_file": resolved_path or "",
                "line_no": 0,
                "evidence": f"{adg_name} routes/dispatches to {cnt} agents (>5 threshold)",
            }
        )
    return violations


def _query_ap7_dup_specialization(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-7: Duplicate specialization — sibling agents with >80% overlapping imports."""
    violations: list[dict[str, Any]] = []
    agent_nodes = conn.execute(
        "SELECT id, adg_name, resolved_path, layer FROM nodes "
        "WHERE entity_type IN ('agent', 'class') "
        "  AND adg_name LIKE '%Agent%'",
    ).fetchall()
    if len(agent_nodes) < 2:
        return violations
    import_map: dict[int, set[int]] = {}
    for nid, _, _, _ in agent_nodes:
        targets = conn.execute(
            "SELECT dst_id FROM edges WHERE src_id = ? AND relation_type = 'imports'",
            (nid,),
        ).fetchall()
        import_map[nid] = {t[0] for t in targets}
    checked: set[tuple[int, int]] = set()
    for i, (id_a, name_a, path_a, layer_a) in enumerate(agent_nodes):  # progress_bar: bounded by agent_nodes
        for j, (id_b, name_b, _path_b, layer_b) in enumerate(
            agent_nodes
        ):  # progress_bar: bounded by agent_nodes
            if i >= j or layer_a != layer_b:
                continue
            pair = (min(id_a, id_b), max(id_a, id_b))
            if pair in checked:
                continue
            checked.add(pair)
            set_a = import_map.get(id_a, set())
            set_b = import_map.get(id_b, set())
            if not set_a or not set_b:
                continue
            shared = len(set_a & set_b)
            total = min(len(set_a), len(set_b))
            if total > 0 and shared / total > 0.8:
                violations.append(
                    {
                        "source_file": path_a or "",
                        "line_no": 0,
                        "evidence": f"{name_a} and {name_b} ({layer_a}) share >{int(shared / total * 100)}% imports",
                    }
                )
    return violations


def _query_ap8_missing_trace(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-8: Missing trace/eval on action-capable paths — same as SC-8 as anti-pattern."""
    return _query_sc8_trace_coverage(conn)


def _query_ap9_infra_spread(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-9: Infrastructure spread — infra modules imported from >3 distinct layers."""
    violations: list[dict[str, Any]] = []
    infra_nodes = conn.execute(
        "SELECT id, adg_name, resolved_path FROM nodes "
        "WHERE LOWER(adg_name) LIKE '%redis%' "
        "   OR LOWER(adg_name) LIKE '%cache%' "
        "   OR LOWER(adg_name) LIKE '%vector%' "
        "   OR LOWER(adg_name) LIKE '%embedding%'",
    ).fetchall()
    for nid, adg_name, resolved_path in infra_nodes:  # progress_bar: bounded by infra_nodes
        layers = conn.execute(
            "SELECT DISTINCT n.layer FROM edges e JOIN nodes n ON e.src_id = n.id "
            "WHERE e.dst_id = ? AND e.relation_type IN ('imports', 'reads_from')",
            (nid,),
        ).fetchall()
        layer_count = len(layers)
        if layer_count > 3:
            violations.append(
                {
                    "source_file": resolved_path or "",
                    "line_no": 0,
                    "evidence": f"{adg_name} imported from {layer_count} layers (>3 threshold)",
                }
            )
    return violations


def _query_ap10_mutation_confusion(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-10: Live/future mutation confusion — L6 writing to non-L6 execution modules."""
    violations: list[dict[str, Any]] = []
    rows = conn.execute(
        "SELECT e.source_file, e.line_no, n_src.adg_name, n_dst.layer "
        "FROM edges e "
        "JOIN nodes n_src ON e.src_id = n_src.id "
        "JOIN nodes n_dst ON e.dst_id = n_dst.id "
        "WHERE n_src.layer = 'L6' "
        "  AND e.relation_type IN ('writes_to', 'controls_flow') "
        "  AND n_dst.layer != 'L6'",
    ).fetchall()
    for src_file, line_no, adg_name, dst_layer in rows:
        violations.append(
            {
                "source_file": src_file or "",
                "line_no": line_no or 0,
                "evidence": f"{adg_name} (L6) mutates {dst_layer} execution-time module",
            }
        )
    return violations


def _query_ap11_work_contracts(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-11: Poorly scoped work contracts — L2 execution without stamps_work_contract."""
    violations: list[dict[str, Any]] = []
    rows = conn.execute(
        "SELECT DISTINCT n.adg_name, n.resolved_path "
        "FROM edges e JOIN nodes n ON e.src_id = n.id "
        "WHERE n.layer = 'L2' "
        "  AND e.relation_type IN ('resolves_callsite', 'invokes_provider') "
        "  AND e.src_id NOT IN ("
        "    SELECT e2.src_id FROM edges e2 WHERE e2.relation_type = 'stamps_work_contract'"
        "  )",
    ).fetchall()
    for adg_name, resolved_path in rows:
        violations.append(
            {
                "source_file": resolved_path or "",
                "line_no": 0,
                "evidence": f"{adg_name} (L2) executes without stamps_work_contract",
            }
        )
    return violations


def _query_ap12_prompt_scatter(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-12: Prompt scatter — modules generating >3 prompts without reuse."""
    violations: list[dict[str, Any]] = []
    rows = conn.execute(
        "SELECT n.adg_name, n.resolved_path, COUNT(*) as cnt "
        "FROM edges e JOIN nodes n ON e.src_id = n.id "
        "WHERE e.relation_type = 'generates_prompt' "
        "GROUP BY e.src_id "
        "HAVING cnt > 3",
    ).fetchall()
    for adg_name, resolved_path, cnt in rows:
        violations.append(
            {
                "source_file": resolved_path or "",
                "line_no": 0,
                "evidence": f"{adg_name} generates {cnt} prompts (>3 threshold)",
            }
        )
    return violations


def _query_ap13_retry_no_exit(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-13: Retry/heal without clear exit criteria — orchestrates_healing without seal."""
    violations: list[dict[str, Any]] = []
    rows = conn.execute(
        "SELECT DISTINCT n.adg_name, n.resolved_path "
        "FROM edges e JOIN nodes n ON e.src_id = n.id "
        "WHERE e.relation_type = 'orchestrates_healing' "
        "  AND e.src_id NOT IN ("
        "    SELECT e2.src_id FROM edges e2 "
        "    WHERE e2.relation_type IN ('packages_execution_trace', 'applies_hmac_seal')"
        "  )",
    ).fetchall()
    for adg_name, resolved_path in rows:
        violations.append(
            {
                "source_file": resolved_path or "",
                "line_no": 0,
                "evidence": f"{adg_name} orchestrates healing without execution trace seal",
            }
        )
    return violations


def _query_ap14_retrieval_no_evidence(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-14: Retrieval without evidence contract — pulls_context without guardrail."""
    violations: list[dict[str, Any]] = []
    rows = conn.execute(
        "SELECT DISTINCT n.adg_name, n.resolved_path "
        "FROM edges e JOIN nodes n ON e.src_id = n.id "
        "WHERE e.relation_type IN ('retrieves_via', 'pulls_context') "
        "  AND e.src_id IN ("
        "    SELECT e2.src_id FROM edges e2 WHERE e2.relation_type = 'invokes_provider'"
        "  ) "
        "  AND e.src_id NOT IN ("
        "    SELECT e3.src_id FROM edges e3 WHERE e3.relation_type = 'applies_guardrail'"
        "  )",
    ).fetchall()
    for adg_name, resolved_path in rows:
        violations.append(
            {
                "source_file": resolved_path or "",
                "line_no": 0,
                "evidence": f"{adg_name} retrieves context and invokes provider without guardrail",
            }
        )
    return violations


def _query_ap15_agent_tool_ratio(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-15: Agent count outrunning tool surfaces — ratio >3:1."""
    violations: list[dict[str, Any]] = []
    agent_count = conn.execute(
        "SELECT COUNT(DISTINCT dst_id) FROM edges WHERE relation_type IN ('routes_to_agent', 'dispatches_agent')",
    ).fetchone()[0]
    tool_count = conn.execute(
        "SELECT COUNT(DISTINCT dst_id) FROM edges WHERE relation_type = 'invokes_provider'",
    ).fetchone()[0]
    if tool_count > 0 and agent_count / tool_count > 3:
        violations.append(
            {
                "source_file": "",
                "line_no": 0,
                "evidence": f"Agent/tool ratio {agent_count}:{tool_count} exceeds 3:1 threshold",
            }
        )
    elif tool_count == 0 and agent_count > 0:
        violations.append(
            {
                "source_file": "",
                "line_no": 0,
                "evidence": f"{agent_count} agents with 0 tool surfaces",
            }
        )
    return violations


def _query_ap16_dormant_infra(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-16: Dormant infrastructure — infra modules with <3 incoming imports."""
    violations: list[dict[str, Any]] = []
    infra_nodes = conn.execute(
        "SELECT id, adg_name, resolved_path FROM nodes "
        "WHERE LOWER(adg_name) LIKE '%redis%' "
        "   OR LOWER(adg_name) LIKE '%cache%' "
        "   OR LOWER(adg_name) LIKE '%vector%' "
        "   OR LOWER(adg_name) LIKE '%embedding%' "
        "   OR LOWER(adg_name) LIKE '%eval%'",
    ).fetchall()
    for nid, adg_name, resolved_path in infra_nodes:  # progress_bar: bounded by infra_nodes
        import_count = conn.execute(
            "SELECT COUNT(*) FROM edges WHERE dst_id = ? AND relation_type = 'imports'",
            (nid,),
        ).fetchone()[0]
        if import_count < 3:
            violations.append(
                {
                    "source_file": resolved_path or "",
                    "line_no": 0,
                    "evidence": f"{adg_name} has only {import_count} incoming imports (<3 threshold)",
                }
            )
    return violations


_GENERIC_EDGE_KINDS = {"call", "read", "write"}


def _query_ap17_semantic_precision(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-17: Agentic semantic precision gaps — generic edge_kind where domain-specific exists."""
    violations: list[dict[str, Any]] = []
    placeholders = ",".join(["?"] * len(_GENERIC_EDGE_KINDS))
    rows = conn.execute(
        "SELECT e.source_file, e.line_no, e.edge_kind, e.relation_type, n.adg_name "
        "FROM edges e JOIN nodes n ON e.src_id = n.id "
        f"WHERE e.edge_kind IN ({placeholders}) "
        "  AND e.relation_type NOT IN ('imports', 'violates')",
        list(_GENERIC_EDGE_KINDS),
    ).fetchall()
    for src_file, line_no, edge_kind, relation_type, adg_name in rows:
        violations.append(
            {
                "source_file": src_file or "",
                "line_no": line_no or 0,
                "evidence": f"{adg_name} uses generic edge_kind '{edge_kind}' for {relation_type}",
            }
        )
    return violations


_PROMPT_ASSEMBLY_PATH_FRAGMENTS: tuple[str, ...] = (
    "tools/adg/prompt_assembly/",
    "c0_evidence_contract_types",
    "c0_dispatcher",
    "c0_bridge_adapter",
)


def _query_ap18_prompt_assembly_orphan(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """AP-18: Prompt assembly subsystem disconnected from runtime.

    Fails when a module in the prompt-assembly wiring surface exists and has
    test callers but zero live (non-test) runtime callers.  This is the
    exact negative-space pattern that was previously undetectable by:
      - SC-5  (spine completeness: passes trivially when *any* path emits the edges)
      - AP-14 (retrieval without guardrail: different failure mode)
      - mv_unknown_taxonomy_and_orphans (requires *zero* edges; test callers pass it)

    Does NOT fire on:
      - modules with no callers at all (mv_unknown_taxonomy_and_orphans covers those)
      - modules that have at least one live runtime import
    """
    violations: list[dict[str, Any]] = []
    path_clauses = " OR ".join(f"n.resolved_path LIKE '%{frag}%'" for frag in _PROMPT_ASSEMBLY_PATH_FRAGMENTS)
    rows = conn.execute(
        "SELECT n.adg_name, n.resolved_path, "
        "    COUNT(DISTINCT CASE "
        "        WHEN c.resolved_path NOT LIKE 'tests/%' "
        "         AND c.resolved_path NOT LIKE 'test_%' "
        "        THEN e.id END) AS live_callers, "
        "    COUNT(DISTINCT CASE "
        "        WHEN c.resolved_path LIKE 'tests/%' "
        "          OR c.resolved_path LIKE 'test_%' "
        "        THEN e.id END) AS test_callers "
        "FROM nodes n "
        "LEFT JOIN edges e ON e.dst_id = n.id AND e.relation_type = 'imports' "
        "LEFT JOIN nodes c ON c.id = e.src_id "
        f"WHERE n.entity_type = 'module' "
        f"  AND n.resolved_path NOT LIKE 'tests/%' "
        f"  AND ({path_clauses}) "
        "GROUP BY n.id "
        "HAVING live_callers = 0 AND test_callers > 0",
    ).fetchall()
    for adg_name, resolved_path, _live_callers, test_callers in rows:  # progress_bar: bounded by rows
        violations.append(
            {
                "source_file": resolved_path or "",
                "line_no": 0,
                "evidence": (
                    f"{adg_name} prompt-assembly surface has {test_callers} test "
                    f"caller(s) but 0 live runtime callers — subsystem is test-only "
                    f"(missing_runtime_consumer)"
                ),
            }
        )
    return violations


def _check_agentic_antipatterns(
    sqlite_path: Path | None = None,
    config_path: Path | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Run agentic anti-pattern checks (AP-1 through AP-18).

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
        _ensure_violation_class_column(conn)
        for check_id, check_cfg in sorted(ap_checks.items()):  # progress_bar: bounded by ap_checks
            audit = check_cfg.get("audit_mode", True)
            label = check_cfg.get("label", check_id)
            violations: list[dict[str, Any]] = []

            query_fn_name = _AP_CHECK_DISPATCH.get(check_id)
            if query_fn_name:
                query_fn = globals().get(query_fn_name)
                if query_fn is not None:
                    try:
                        violations = query_fn(conn)
                    except sqlite3.OperationalError as _ap_err:
                        print(f"[ADG] WARNING: {check_id} query failed: {_ap_err}")
                else:
                    print(f"[ADG] WARNING: {check_id} dispatch function '{query_fn_name}' not found")

            ap_num = int(check_id.split("-")[1]) if "-" in check_id else 0
            if ap_num <= 4:
                severity = "P0"
            elif ap_num <= 10:
                severity = "P1"
            elif ap_num <= 14:
                severity = "P2"
            else:
                severity = "P3"

            for v in violations:
                _insert_sc_ap_violation(
                    conn,
                    check_id,
                    CLASS_AGENTIC,
                    severity,
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
                    from tools.generate.integration.deferred_failures import record_or_exit

                    print(f"[ERROR] {check_id} agentic anti-pattern check FAILED")
                    record_or_exit(
                        f"agentic_antipattern:{check_id}",
                        1,
                        message=f"{count} violation(s)",
                    )
                    # only reached when defer-exit is on; loop continues
            else:
                print(f"[ADG] {check_id} ({label}): PASSED")

    return results


# ---------------------------------------------------------------------------
# Architecture witness-tier gates: Class A (positive witness) + Class B (absence/breach)
# ---------------------------------------------------------------------------

# Required columns in both witness-tier tables (regression schema protection)
_WITNESS_TIER_REQUIRED_COLUMNS: frozenset[str] = frozenset(
    {
        "snapshot_id",
        "plumbing_witness_count",
        "test_witness_count",
        "live_runtime_witness_count",
        "zero_witness_count",
        "runtime_orphaned",
    }
)

# Class A: runtime-spine handoff families (view_name in mv_handoff_witness_tiers).
# All currently PLANNED — plumbing/schema wired but no live callers yet.
_CLASS_A_SPINE_FAMILIES_PLANNED: frozenset[str] = frozenset(
    {
        "mv_ingress_before_anything",
        "mv_l1_plan_before_route",
        "mv_retrieval_evidence_handoff",
        "mv_evidence_to_prompt_handoff",
        "mv_governed_execution_envelope_continuity",
        "mv_runtime_exit_continuity",
    }
)

# Class A: cross-cutting families required-live NOW (confirmed live_rt > 0 in repo).
_CLASS_A_CC_FAMILIES_REQUIRED: frozenset[str] = frozenset(
    {
        "capability_egress_chokepoint",
        "heal_retry_under_blueprint",
        "hitl_freeze_materialize_reclear",
        "retrieval_surface_integrity",
        "uwg_full_commit_chain",
    }
)

# Class A: cross-cutting families PLANNED (runtime-orphaned; not yet blocking).
_CLASS_A_CC_FAMILIES_PLANNED: frozenset[str] = frozenset(
    {
        "commit_uwg_envelope_continuity",
        "exit_hitl_envelope_continuity",
        "future_run_only_promotion",
        "offline_publication_before_runtime",
    }
)

# Class B: absence/negative families and their governing breach views.
# All four families now have dedicated breach surfaces.
_CLASS_B_FAMILIES: dict[str, str | None] = {
    "no_direct_write_live_planes": "mv_write_sovereignty_paths",
    "replay_envelope_continuity": "mv_digest_reconciliation",
    "local_heal_first": "mv_local_heal_first_breaches",
    "observability_non_interference": "mv_observability_interference_breaches",
}


def _check_witness_tier_gates(sqlite_path: Path | None = None) -> dict[str, Any]:
    """Validate architecture witness-tier views and enforce Class A / Class B gate policies.

    Class A (positive witness) -- live runtime proof required:
      - required families: sys.exit(1) if runtime-orphaned
      - planned families: warn but do not fail

    Class B (absence / negative) -- breach/forbidden-path surface required:
      - checks governing breach views exist and are populated
      - reports families without a dedicated breach surface as insufficient

    Regression protection:
      - sys.exit(1) if mv_handoff_witness_tiers or mv_cross_cutting_witness_tiers missing
      - sys.exit(1) if required schema columns absent from either table
      - sys.exit(1) if a required Class A family missing from mv_cross_cutting_witness_tiers

    Returns:
        Dict with keys: 'class_a_required_violations', 'class_a_planned_warnings',
        'class_b_status', 'schema_ok', 'tables_present', 'error'
    """
    result: dict[str, Any] = {
        "class_a_required_violations": [],
        "class_a_planned_warnings": [],
        "class_b_status": {},
        "schema_ok": False,
        "tables_present": False,
        "error": None,
    }

    if sqlite_path is None or not sqlite_path.exists():
        result["error"] = "SQLite not found"
        return result

    try:
        with sqlite3.connect(str(sqlite_path)) as conn:
            # -- Regression: required mv_* tables must exist ------------------
            existing_tables: set[str] = {
                row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            }
            required_mv = frozenset(
                {
                    "mv_handoff_witness_tiers",
                    "mv_cross_cutting_witness_tiers",
                }
            )
            missing_mv = required_mv - existing_tables
            if missing_mv:
                msg = f"[ERROR][WITNESS-REGRESSION] Tables missing: {sorted(missing_mv)}"
                print(msg)
                print("[ERROR] Re-run: python tools/generate_full_adg.py")
                result["error"] = msg
                sys.exit(1)

            result["tables_present"] = True

            # -- Regression: required schema columns must exist ---------------
            for tbl in required_mv:
                cols = {r[1] for r in conn.execute(f"PRAGMA table_info({tbl})").fetchall()}
                missing_cols = _WITNESS_TIER_REQUIRED_COLUMNS - cols
                if missing_cols:
                    msg = f"[ERROR][SCHEMA-DRIFT] {tbl} missing columns: {sorted(missing_cols)}"
                    print(msg)
                    print("[ERROR] Schema drift detected -- regenerate ADG.")
                    result["error"] = msg
                    sys.exit(1)

            result["schema_ok"] = True

            # -- Class A: runtime-spine handoff families ----------------------
            spine_rows = conn.execute(
                "SELECT view_name,"
                " COALESCE(SUM(live_runtime_witness_count), 0),"
                " COALESCE(SUM(runtime_orphaned), 0)"
                " FROM mv_handoff_witness_tiers"
                " GROUP BY view_name"
            ).fetchall()

            for view_name, _live_rt_total, orphaned_count in spine_rows:  # tqdm: DB result set, no bar needed
                if view_name in _CLASS_A_SPINE_FAMILIES_PLANNED and orphaned_count > 0:
                    print(
                        f"[ADG-WITNESS][PLANNED] {view_name}: "
                        f"spine runtime-orphaned={orphaned_count} (planned -- not yet blocking)"
                    )
                    result["class_a_planned_warnings"].append(
                        {
                            "family": view_name,
                            "table": "mv_handoff_witness_tiers",
                            "orphaned_count": int(orphaned_count),
                            "status": "planned",
                        }
                    )

            # -- Class A: cross-cutting required families ---------------------
            cc_rows = conn.execute(
                "SELECT family_name,"
                " COALESCE(SUM(live_runtime_witness_count), 0),"
                " COALESCE(SUM(plumbing_witness_count), 0),"
                " COALESCE(SUM(test_witness_count), 0),"
                " COALESCE(SUM(runtime_orphaned), 0)"
                " FROM mv_cross_cutting_witness_tiers"
                " GROUP BY family_name"
            ).fetchall()

            present_cc = {row[0] for row in cc_rows}
            missing_required = _CLASS_A_CC_FAMILIES_REQUIRED - present_cc
            if missing_required:
                msg = (
                    f"[ERROR][WITNESS-REGRESSION] Required Class A families missing from "
                    f"mv_cross_cutting_witness_tiers: {sorted(missing_required)}"
                )
                print(msg)
                result["error"] = msg
                sys.exit(1)

            for (
                family_name,
                live_rt,
                plumbing,
                test,
                orphaned,
            ) in cc_rows:  # tqdm: DB result set, no bar needed
                if family_name in _CLASS_A_CC_FAMILIES_REQUIRED:
                    if orphaned > 0:
                        msg = (
                            f"[ERROR][CLASS-A] '{family_name}': required-live family is "
                            f"runtime-orphaned -- plumbing={plumbing} test={test} "
                            f"live_rt={live_rt} orphaned_rels={orphaned}"
                        )
                        print(msg)
                        result["class_a_required_violations"].append(
                            {
                                "family": family_name,
                                "table": "mv_cross_cutting_witness_tiers",
                                "plumbing": int(plumbing),
                                "test": int(test),
                                "live_rt": int(live_rt),
                                "orphaned_count": int(orphaned),
                                "status": "required",
                            }
                        )
                    else:
                        print(f"[ADG-WITNESS][CLASS-A] '{family_name}': live_rt={live_rt} OK")
                elif family_name in _CLASS_A_CC_FAMILIES_PLANNED:
                    if orphaned > 0:
                        print(
                            f"[ADG-WITNESS][PLANNED] '{family_name}': "
                            f"cc runtime-orphaned={orphaned} (planned -- not yet blocking)"
                        )
                        result["class_a_planned_warnings"].append(
                            {
                                "family": family_name,
                                "table": "mv_cross_cutting_witness_tiers",
                                "orphaned_count": int(orphaned),
                                "status": "planned",
                            }
                        )

            # -- Class B: absence/negative families --------------------------
            for family, breach_view in _CLASS_B_FAMILIES.items():  # tqdm: small config dict, no bar needed
                status_b: dict[str, Any] = {
                    "family": family,
                    "gate_class": "B",
                    "breach_view": breach_view,
                }
                if breach_view is None:
                    status_b["breach_surface"] = "INSUFFICIENT"
                    status_b["note"] = "No dedicated breach view -- zero witnesses is ambiguous"
                    print(
                        f"[ADG-WITNESS][CLASS-B] '{family}': "
                        f"no dedicated breach surface -- enforcement insufficient"
                    )
                elif breach_view in existing_tables:
                    row_count = conn.execute(
                        f"SELECT COUNT(*) FROM {breach_view}"  # noqa: S608
                    ).fetchone()[0]
                    status_b["breach_surface"] = "PRESENT"
                    status_b["breach_view_rows"] = row_count
                    print(
                        f"[ADG-WITNESS][CLASS-B] '{family}': "
                        f"breach surface {breach_view} present ({row_count} rows)"
                    )
                else:
                    status_b["breach_surface"] = "MISSING"
                    status_b["note"] = f"Breach view {breach_view} not in DB"
                    print(f"[ADG-WITNESS][CLASS-B] '{family}': breach surface {breach_view} MISSING")
                result["class_b_status"][family] = status_b

            # -- Final summary ------------------------------------------------
            req_violations = result["class_a_required_violations"]
            planned_warnings = result["class_a_planned_warnings"]
            b_insufficient = sum(
                1 for s in result["class_b_status"].values() if s.get("breach_surface") == "INSUFFICIENT"
            )
            print()
            print("[ADG-WITNESS] Architecture witness-tier gate summary:")
            print(f"  Class A required violations  : {len(req_violations)}")
            print(f"  Class A planned warnings     : {len(planned_warnings)}")
            print(f"  Class B families surveyed    : {len(_CLASS_B_FAMILIES)}")
            print(f"  Class B breach-surface gaps  : {b_insufficient}")

            if req_violations:
                print()
                print("[ERROR] Class A required-live violations -- gate FAILED:")
                for v in req_violations:
                    print(f"  [x] {v['family']} (orphaned={v['orphaned_count']})")
                sys.exit(1)
            else:
                print("[ADG-WITNESS] Class A gate: PASSED")

    except SystemExit:
        raise
    except sqlite3.Error as exc:
        result["error"] = str(exc)
        print(f"[ADG-WITNESS] WARNING: witness-tier gate query failed: {exc}")

    return result
