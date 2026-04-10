"""Defect table printing and standardized report generation for ADG."""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _print_defect_table(
    routing_summary: dict,
    semantic_warnings: list[str] | None = None,
    sqlite_path: Path | None = None,
) -> None:
    """Print P0-P3 defect table in terminal output."""
    by_severity = routing_summary.get("by_severity", {})

    p0_count = 0
    _violation_rows: list = []
    if sqlite_path is not None and sqlite_path.exists():
        try:
            with sqlite3.connect(str(sqlite_path)) as _conn:
                _violation_rows = _conn.execute(
                    "SELECT source_file, line_no FROM edges WHERE relation_type='violates'",
                ).fetchall()
            for _src_file, _line_no in _violation_rows:
                try:
                    _src_path = ROOT / _src_file
                    if _src_path.exists() and _line_no and _line_no > 0:
                        _file_lines = _src_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                        _check = _file_lines[max(0, _line_no - 2) : _line_no]
                        if not any("guardian: allow-layer-violation" in _ln for _ln in _check):
                            p0_count += 1
                    else:
                        p0_count += 1
                except Exception:  # guardian: allow-silent-swallow -- non-critical: file read failure counts violation as unapproved
                    p0_count += 1
        except (
            Exception
        ):  # guardian: allow-silent-swallow -- non-critical: table read failure falls back to 0
            pass

    p1_antipattern = 0
    p2_antipattern = 0
    p3_antipattern = 0
    if sqlite_path is not None and sqlite_path.exists():
        try:
            with sqlite3.connect(str(sqlite_path)) as _conn:
                rows = _conn.execute(
                    "SELECT severity, COUNT(*) FROM violations WHERE category='antipattern' GROUP BY severity",
                ).fetchall()
                _sev_map = {r[0]: r[1] for r in rows}
                p1_antipattern = _sev_map.get("HIGH", 0)
                p2_antipattern = _sev_map.get("MEDIUM", 0)
                p3_antipattern = _sev_map.get("LOW", 0)
        except (
            Exception
        ):  # guardian: allow-silent-swallow -- non-critical: table read failure falls back to routing counts
            pass

    _p1_ratchet_file = ROOT / "artifacts" / "adg" / "p1_ratchet.json"
    if not _p1_ratchet_file.exists():
        _legacy = ROOT / "artifacts" / "adg" / "p2_ratchet.json"
        if _legacy.exists():
            _p1_ratchet_file = _legacy
    _p1_ceiling = p1_antipattern
    try:
        if _p1_ratchet_file.exists():
            _p1_data = json.loads(_p1_ratchet_file.read_text(encoding="utf-8"))
            _p1_ceiling = _p1_data.get(
                "high_severity_ceiling", _p1_data.get("p2_antipattern_ceiling", p1_antipattern)
            )
    except Exception:  # guardian: allow-silent-swallow -- non-critical: ratchet read failure shows raw count
        pass
    _p1_delta = max(0, p1_antipattern - _p1_ceiling)
    p1_count = p1_antipattern

    _p2_ratchet_file = ROOT / "artifacts" / "adg" / "p2_ratchet.json"
    if not _p2_ratchet_file.exists():
        _legacy2 = ROOT / "artifacts" / "adg" / "p3_ratchet.json"
        if _legacy2.exists():
            _p2_ratchet_file = _legacy2
    _p2_ceiling: int | None = None
    try:
        if _p2_ratchet_file.exists():
            _p2_data = json.loads(_p2_ratchet_file.read_text(encoding="utf-8"))
            _p2_ceiling = _p2_data.get("exception_swallow_ceiling")
    except Exception:  # guardian: allow-silent-swallow -- non-critical: ratchet read failure
        pass
    p2_count = p2_antipattern

    p3_count = p3_antipattern + by_severity.get("low", 0)
    if semantic_warnings:
        p3_count += len(semantic_warnings)

    total = p0_count + p1_count + p2_count + p3_count

    _p0_layer_pairs: list = []
    _p0_cycle_count = 0
    _p0_dynamic_count = 0
    _cat_data: dict[str, list[tuple]] = {"HIGH": [], "MEDIUM": [], "LOW": []}
    _sev_files: dict[str, int] = {}
    _sev_top_layer: dict[str, str] = {}
    _sev_prod_pct: dict[str, dict[str, int]] = {}
    _hotspot_pct: dict[str, int] = {}
    _guardian_total = 0
    _guardian_by_sev: dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    _guardian_by_kind: dict[str, dict[str, int]] = {}
    _sev_top_hotspot: dict[str, str] = {}
    _sev_density: dict[str, str] = {}
    _refactor_top5: list[tuple] = []
    if sqlite_path is not None and sqlite_path.exists():
        try:
            _prod_layers = (
                "L0",
                "L1",
                "L2",
                "L3",
                "L4",
                "L5",
                "L6",
                "L_SHARED",
                "L_SL",
                "L_PG",
                "L_RUNTIME",
            )
            with sqlite3.connect(str(sqlite_path)) as _cc:
                _p0_layer_pairs = _cc.execute("""
                    SELECT n_src.layer, n_dst.layer, COUNT(*)
                    FROM edges e
                    JOIN nodes n_src ON e.src_id = n_src.id
                    JOIN nodes n_dst ON e.dst_id = n_dst.id
                    WHERE e.relation_type='violates'
                    GROUP BY 1,2 ORDER BY 3 DESC
                """).fetchall()
                _p0_cycle_count = _cc.execute(
                    "SELECT COUNT(*) FROM edges WHERE relation_type='in_cycle'",
                ).fetchone()[0]
                _p0_dynamic_count = _cc.execute(
                    "SELECT COUNT(*) FROM edges WHERE relation_type='dynamic_exec'",
                ).fetchone()[0]

                for _sev in ("HIGH", "MEDIUM", "LOW"):
                    _cat_data[_sev] = _cc.execute(
                        f"""
                        SELECT e.edge_kind, COUNT(*) cnt,
                               SUM(CASE WHEN n.layer IN ({",".join("?" for _ in _prod_layers)})
                                        THEN 1 ELSE 0 END) prod_cnt
                        FROM violations v
                        JOIN edges e ON v.edge_id=e.id
                        JOIN nodes n ON e.src_id=n.id
                        WHERE v.severity=? AND v.category='antipattern'
                        GROUP BY e.edge_kind ORDER BY cnt DESC
                    """,
                        (*_prod_layers, _sev),
                    ).fetchall()
                    _sev_files[_sev] = _cc.execute(
                        "SELECT COUNT(DISTINCT e.source_file) FROM violations v "
                        "JOIN edges e ON v.edge_id=e.id "
                        f"WHERE v.severity='{_sev}' AND v.category='antipattern'",
                    ).fetchone()[0]
                    _r = _cc.execute(
                        "SELECT n.layer FROM violations v JOIN edges e ON v.edge_id=e.id "
                        "JOIN nodes n ON e.src_id=n.id "
                        f"WHERE v.severity='{_sev}' AND v.category='antipattern' "
                        "AND n.layer IS NOT NULL GROUP BY n.layer ORDER BY COUNT(*) DESC LIMIT 1",
                    ).fetchone()
                    _sev_top_layer[_sev] = _r[0] if _r else "N/A"
                    _total_sev = _cc.execute(
                        f"SELECT COUNT(*) FROM violations WHERE severity='{_sev}' AND category='antipattern'",
                    ).fetchone()[0]
                    _top10 = (
                        _cc.execute(
                            "SELECT SUM(c) FROM (SELECT COUNT(*) c FROM violations v "
                            "JOIN edges e ON v.edge_id=e.id "
                            f"WHERE v.severity='{_sev}' AND v.category='antipattern' "
                            "GROUP BY e.source_file ORDER BY c DESC LIMIT 10)",
                        ).fetchone()[0]
                        or 0
                    )
                    _hotspot_pct[_sev] = (_top10 * 100 // _total_sev) if _total_sev else 0

                _meta_row = _cc.execute(
                    "SELECT value FROM meta WHERE key='guardian_exemptions'",
                ).fetchone()
                _guardian_total = int(_meta_row[0]) if _meta_row else 0

                _high_kinds = (
                    "broad_exception_catch",
                    "silent_exception_swallow",
                    "log_and_swallow",
                    "return_none_swallow",
                )
                _prod_prefixes = ("agentic_core/", "system_learning/")
                _exempt_rows = _cc.execute("""
                    SELECT e.edge_kind, e.source_file
                    FROM edges e
                    WHERE e.relation_type='antipattern'
                      AND e.id NOT IN (SELECT edge_id FROM violations WHERE category='antipattern')
                """).fetchall()
                for _ek, _sf in _exempt_rows:
                    if _ek in _high_kinds and any(_sf.startswith(p) for p in _prod_prefixes):
                        _s = "HIGH"
                    elif _ek in _high_kinds:
                        _s = "MEDIUM"
                    else:
                        _s = "LOW"
                    _guardian_by_sev[_s] = _guardian_by_sev.get(_s, 0) + 1
                    if _s not in _guardian_by_kind:
                        _guardian_by_kind[_s] = {}
                    _guardian_by_kind[_s][_ek] = _guardian_by_kind[_s].get(_ek, 0) + 1

                _total_prod_nodes = (
                    _cc.execute(
                        "SELECT COUNT(*) FROM nodes WHERE layer IN (%s)"
                        % ",".join("?" for _ in _prod_layers),
                        _prod_layers,
                    ).fetchone()[0]
                    or 1
                )
                _total_all_nodes = (
                    _cc.execute(
                        "SELECT COUNT(*) FROM nodes WHERE layer IS NOT NULL AND layer != ''",
                    ).fetchone()[0]
                    or 1
                )
                _sev_counts = {"HIGH": p1_antipattern, "MEDIUM": p2_antipattern, "LOW": p3_antipattern}
                for _sk, _sc in _sev_counts.items():
                    _base = _total_prod_nodes if _sk == "HIGH" else _total_all_nodes
                    _d = _sc * 100 / _base if _base else 0
                    _sev_density[_sk] = f"{_d:.1f}"

                _fan_in_map: dict[str, int] = {}
                for _fip, _fic in _cc.execute("""
                    SELECT n2.resolved_path, COUNT(DISTINCT e2.src_id)
                    FROM edges e2 JOIN nodes n2 ON e2.dst_id=n2.id
                    WHERE e2.relation_type IN ('imports','calls')
                    AND n2.resolved_path != ''
                    GROUP BY 1
                """).fetchall():
                    _fan_in_map[_fip] = _fic

                for _sk in ("HIGH", "MEDIUM", "LOW"):
                    _hs_rows = _cc.execute(
                        """
                        SELECT e_ap.source_file,
                               COUNT(DISTINCT e_ap.id) ap_cnt
                        FROM edges e_ap
                        JOIN violations v ON v.edge_id=e_ap.id
                        WHERE e_ap.relation_type='antipattern' AND v.severity=?
                        GROUP BY 1
                        ORDER BY ap_cnt DESC
                        LIMIT 20
                    """,
                        (_sk,),
                    ).fetchall()
                    _best = None
                    for _hsf, _hsa in _hs_rows:
                        _hsfi = _fan_in_map.get(_hsf, 0)
                        _hsr = _hsa * _hsfi
                        if _best is None or _hsr > _best[0]:
                            _best = (_hsr, _hsf, _hsa, _hsfi)
                    _hs_row = (_best[1], _best[2], _best[3]) if _best else None
                    if _hs_row:
                        _hf, _ha, _hfi = _hs_row
                        _short = _hf.rsplit("/", 1)[-1] if "/" in _hf else _hf
                        _risk_tag = f" [{_ha}x{_hfi}={_ha * _hfi}]"
                        _max_name = 32 - len(_risk_tag)
                        _trunc = _short[:_max_name]
                        _sev_top_hotspot[_sk] = f"{_trunc}{_risk_tag}"
                    else:
                        _sev_top_hotspot[_sk] = "\u2014"

                _refactor_top5 = _cc.execute("""
                    SELECT
                        COUNT(DISTINCT e_ap.id) * COALESCE(MAX(sub.fan_in), 0) risk,
                        e_ap.source_file,
                        n.layer,
                        COUNT(DISTINCT e_ap.id) ap_cnt,
                        COALESCE(MAX(sub.fan_in), 0) fan_in
                    FROM edges e_ap
                    JOIN nodes n ON e_ap.src_id=n.id
                    LEFT JOIN (
                        SELECT n2.resolved_path rp,
                               COUNT(DISTINCT e2.src_id) fan_in
                        FROM edges e2
                        JOIN nodes n2 ON e2.dst_id=n2.id
                        WHERE e2.relation_type IN ('imports','calls')
                        GROUP BY 1
                    ) sub ON sub.rp = e_ap.source_file
                    WHERE e_ap.relation_type='antipattern'
                    GROUP BY e_ap.source_file
                    HAVING ap_cnt >= 3 AND fan_in >= 2
                    ORDER BY risk DESC
                    LIMIT 5
                """).fetchall()

        except Exception:  # guardian: allow-silent-swallow -- non-critical: category query failure
            pass

    # --- SC/AP audit violation counts for defect table ---
    _sc_ap_counts: dict[str, int] = {}
    if sqlite_path is not None and sqlite_path.exists():
        try:
            with sqlite3.connect(str(sqlite_path)) as _sa_conn:
                _sa_cols = {r[1] for r in _sa_conn.execute("PRAGMA table_info(violations)").fetchall()}
                if "violation_class" in _sa_cols:
                    _sa_rows = _sa_conn.execute(
                        "SELECT category, COUNT(*) FROM violations "
                        "WHERE violation_class IN ('structural_conformance', 'agentic_antipattern') "
                        "GROUP BY category",
                    ).fetchall()
                    for _cat, _cnt in _sa_rows:
                        _sc_ap_counts[_cat] = _cnt
        except sqlite3.OperationalError:
            pass

    # --- Compact burndown table (auto-printed on every ADG run) ---
    _TH = "+-----+------------------------------+-------+-------+-------+------+"
    _THDR = "| Band| Kind                         | Gross | Exempt |   Net |   %  |"
    print("\n[ADG] Burndown:")
    print(_TH)
    print(_THDR)
    print(_TH)

    def _pct(a: int, b: int) -> str:
        return f"{a * 100 // b}%" if b else "—"

    # P0
    _p0_gate = "✓" if p0_count == 0 else "✗"
    print(f"| P0{_p0_gate} | layer violations             | {p0_count:5} |        | {p0_count:5} |      |")
    if _p0_cycle_count:
        print(
            f"|     |  circular_import             | {_p0_cycle_count:5} |        | {_p0_cycle_count:5} |      |"
        )
    if _p0_dynamic_count:
        print(
            f"|     |  dynamic_execution           | {_p0_dynamic_count:5} |        | {_p0_dynamic_count:5} |      |"
        )
    for _src_l, _dst_l, _cnt in _p0_layer_pairs:
        print(f"|     |    {_src_l or '?'} -> {_dst_l or '?':<22}| {_cnt:5} |        | {_cnt:5} |      |")
    print(_TH)

    # P1 / P2 / P3 bands
    _bands = [
        ("P1", "HIGH antipatterns", p1_count, "HIGH", _p1_ceiling, _p1_delta),
        (
            "P2",
            "MEDIUM antipatterns",
            p2_count,
            "MEDIUM",
            _p2_ceiling,
            max(0, p2_count - _p2_ceiling) if _p2_ceiling is not None else 0,
        ),
        ("P3", "style / warnings", p3_count, "LOW", None, 0),
    ]
    for _band, _label, _count, _sev, _ceil, _delta in _bands:
        _exempt = _guardian_by_sev.get(_sev, 0)
        _gross = _count + _exempt
        _status = ("*" if _delta > 0 else "^") if _ceil is not None else "~"
        print(
            f"| {_band}{_status} | {_label:<29}| {_gross:5} | {_exempt:6} | {_count:5} | {_pct(_exempt, _gross):>4} |"
        )
        for _kind, _cnt, _prod in _cat_data.get(_sev, []):
            _ek = _guardian_by_kind.get(_sev, {}).get(_kind, 0)
            _gk = _cnt + _ek
            print(f"|     |  {_kind:<28}| {_gk:5} | {_ek:6} | {_cnt:5} | {_pct(_ek, _gk):>4} |")
        print(_TH)

    # SC/AP audit rows
    if _sc_ap_counts:
        _sc_total = sum(v for k, v in _sc_ap_counts.items() if k.startswith("SC-"))
        _ap_total = sum(v for k, v in _sc_ap_counts.items() if k.startswith("AP-"))
        for _prefix, _row_label, _row_total in [
            ("SC-", "structural conformance", _sc_total),
            ("AP-", "agentic antipatterns", _ap_total),
        ]:
            if _row_total:
                print(f"| ~   | {_row_label:<29}| {_row_total:5} |        | {_row_total:5} |      |")
                for _ck, _cv in sorted(_sc_ap_counts.items()):
                    if _ck.startswith(_prefix):
                        print(f"|     |  {_ck:<28}| {_cv:5} |        | {_cv:5} |      |")
                print(_TH)

    # Totals
    _total_gross = total + _guardian_total
    print(
        f"| TOT | ALL                          | {_total_gross:5} | {_guardian_total:6} | {total:5} | {_pct(_guardian_total, _total_gross):>4} |"
    )
    print(_TH)

    # --- CI Gate rows (subprocess to avoid L_TOOLS → L_OPS layer violation) ---
    _ci_gate_results: list[tuple[str, str]] = []
    try:
        import subprocess as _sp
        import sys as _sys
        _gate_script = ROOT / "ops_scripts" / "ci" / "executor_theater_gate.py"
        if _gate_script.exists():
            _res = _sp.run(
                [_sys.executable, str(_gate_script), "--json"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(ROOT),
            )
            try:
                _gate_data = json.loads(_res.stdout)
                _gate_labels = {
                    "g1": "G1: executor_reachability  ",
                    "g2": "G2: claim_to_execution     ",
                    "g3": "G3: import_only_capability ",
                    "g4": "G4: production_classif.    ",
                }
                for _gk, _glabel in _gate_labels.items():
                    _ginfo = _gate_data.get(_gk, {})
                    _passed = _ginfo.get("passed", True)
                    _ci_gate_results.append((_glabel, _passed))
            except (json.JSONDecodeError, AttributeError):
                pass
    except (ImportError, OSError):
        pass

    if _ci_gate_results:
        for _gate_label, _gate_passed in _ci_gate_results:
            _gate_sym = "✓" if _gate_passed else "✗"
            _gate_net = " PASS" if _gate_passed else " FAIL"
            print(f"| CI{_gate_sym} | {_gate_label}|       |        | {_gate_net} |      |")
        print(_TH)

    print("  Gross=total  Exempt=approved exceptions (guardian:allow)  Net=actionable  %=exempt/gross")
    print("  Gate: *=BLOCKS  ^=ratchet  ~=watch  ✓=clean  ✗=failing  CI✓/CI✗=ci-gate")

    _p2_delta_val = max(0, p2_count - _p2_ceiling) if _p2_ceiling is not None else 0

    _p1_ratchet_label = "stable" if _p1_delta == 0 else "REGRESSION"
    print(f"[ADG] P1 ratchet: {p1_count}/{_p1_ceiling} ({_p1_delta:+d} \u2014 {_p1_ratchet_label})")
    if _p2_ceiling is not None:
        _p2_label = "stable" if _p2_delta_val == 0 else "REGRESSION"
        print(f"[ADG] P2 ratchet: {p2_count}/{_p2_ceiling} ({_p2_delta_val:+d} \u2014 {_p2_label})")

    # --- Query violation_class breakdown for burndown v2.0 ---
    _by_class: dict[str, dict[str, int]] = {
        "hygiene": {"P0": p0_count, "P1": p1_count, "P2": p2_count, "P3": p3_count},
        "structural_conformance": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
        "agentic_antipattern": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
    }
    if sqlite_path is not None and sqlite_path.exists():
        try:
            _sev_to_band = {
                "CRITICAL": "P0",
                "HIGH": "P1",
                "MEDIUM": "P2",
                "LOW": "P3",
                "P0": "P0",
                "P1": "P1",
                "P2": "P2",
                "P3": "P3",
            }
            with sqlite3.connect(str(sqlite_path)) as _bc_conn:
                _bc_rows = _bc_conn.execute(
                    "SELECT violation_class, severity, COUNT(*) FROM violations "
                    "WHERE violation_class IN ('structural_conformance', 'agentic_antipattern') "
                    "GROUP BY violation_class, severity",
                ).fetchall()
                for _vc, _sv, _cnt in _bc_rows:
                    _band = _sev_to_band.get(_sv, "P3")
                    if _vc in _by_class and _band in _by_class[_vc]:
                        _by_class[_vc][_band] = _cnt
        except sqlite3.OperationalError:
            pass

    # Guardian counts keyed by P-band (P1=HIGH, P2=MEDIUM, P3=LOW; P0 has no guardians)
    _guardian_p0 = 0
    _guardian_p1 = _guardian_by_sev.get("HIGH", 0)
    _guardian_p2 = _guardian_by_sev.get("MEDIUM", 0)
    _guardian_p3 = _guardian_by_sev.get("LOW", 0)

    # Gross = net + guardian (exempted); diff = gross - net = guardian count per band
    _gross_p0 = p0_count + _guardian_p0
    _gross_p1 = p1_count + _guardian_p1
    _gross_p2 = p2_count + _guardian_p2
    _gross_p3 = p3_count + _guardian_p3

    def _build_kind_rows(sev_key: str, gross_total: int) -> list[dict]:
        """Build per-kind breakdown rows matching the terminal defect table columns."""
        rows = []
        kinds_by_guardian = _guardian_by_kind.get(sev_key, {})
        for _kind, _net, _prod in _cat_data.get(sev_key, []):
            _gk = kinds_by_guardian.get(_kind, 0)
            _gross_k = _net + _gk
            rows.append(
                {
                    "kind": _kind,
                    "net": _net,
                    "guardian": _gk,
                    "gross": _gross_k,
                    "diff": _gk,
                    "prod_count": _prod,
                    "share_pct": round(_gross_k * 100 / gross_total, 1) if gross_total else 0,
                    "prod_pct": round(_prod * 100 / _net, 1) if _net else 0,
                }
            )
        return rows

    _burndown: dict = {
        "schema_version": "2.1",
        "summary": {
            "P0": {
                "net": p0_count,
                "guardian": _guardian_p0,
                "gross": _gross_p0,
                "diff": _guardian_p0,
                "label": "layer_violations",
                "by_kind": [],
            },
            "P1": {
                "net": p1_count,
                "guardian": _guardian_p1,
                "gross": _gross_p1,
                "diff": _guardian_p1,
                "label": "anti_patterns_high",
                "by_kind": _build_kind_rows("HIGH", _gross_p1),
            },
            "P2": {
                "net": p2_count,
                "guardian": _guardian_p2,
                "gross": _gross_p2,
                "diff": _guardian_p2,
                "label": "anti_patterns_medium",
                "by_kind": _build_kind_rows("MEDIUM", _gross_p2),
            },
            "P3": {
                "net": p3_count,
                "guardian": _guardian_p3,
                "gross": _gross_p3,
                "diff": _guardian_p3,
                "label": "style_warnings",
                "by_kind": _build_kind_rows("LOW", _gross_p3),
            },
        },
        # Legacy flat keys — kept for backward compatibility
        "P0_layer_violations": p0_count,
        "P1_anti_patterns": p1_count,
        "P2_anti_patterns": p2_count,
        "P3_style": p3_count,
        "p0_clean": p0_count == 0,
        "p1_no_ratchet": _p1_delta == 0,
        "by_class": _by_class,
        "structural_metrics": {
            "cycle_count": _p0_cycle_count,
            "dynamic_exec_count": _p0_dynamic_count,
            "guardian_exemptions": _guardian_total,
            "guardian_by_band": {
                "P0": _guardian_p0,
                "P1": _guardian_p1,
                "P2": _guardian_p2,
                "P3": _guardian_p3,
            },
        },
    }
    _burndown_path = ROOT / "artifacts" / "adg" / "adg_burndown_table.json"
    try:
        _burndown_path.parent.mkdir(parents=True, exist_ok=True)
        _burndown_path.write_text(json.dumps(_burndown, indent=2, sort_keys=True), encoding="utf-8")
        print(f"[ADG] Burndown artifact: {_burndown_path.name}")
    except OSError as e:
        print(f"[ADG] WARNING: Could not write burndown artifact: {e}")

    if _refactor_top5:
        print("\n[ADG] Refactoring Priority (risk = antipatterns \u00d7 fan-in):")
        _RH = "+------+------+------+----------+-----------------------------------------------------+"
        print(_RH)
        print("| Risk |   AP | FanI | Layer    | File                                                |")
        print(_RH)
        for _risk, _rf, _rl, _ra, _rfi in _refactor_top5:
            _rf_short = _rf if len(_rf) <= 51 else "..." + _rf[-(51 - 3) :]
            print(f"| {_risk:4} | {_ra:4} | {_rfi:4} | {_rl or '?':<8} | {_rf_short:<51} |")
        print(_RH)
        print("  AP=antipattern count in file  FanI=distinct importers/callers  Risk=AP\u00d7FanI")


def _generate_standardized_reports(
    adg_dir: Path,
    ts: str,
    artifact,
    result=None,
    repo_root: Path | None = None,
    enable_determinism_probe: bool = False,
) -> dict[str, object] | None:
    """Wave 6: Generate standardized ADG reports."""
    from tools.generate.reporting.analysis import (
        _artifact_determinism_probe,
        _semantic_precision_stats,
        _violation_surface_stats,
    )
    from tools.generate.utils.digest_utils import _ratio

    repo_root = repo_root or ROOT

    reports_dir = adg_dir
    sqlite_path = adg_dir / f"adg_indexed_{ts}.sqlite"
    if not sqlite_path.exists():
        from agentic_core.adg.artifact.multi_writer import write_all_artifacts

        write_all_artifacts(artifact, out_dir=adg_dir, ts=ts)

    layer_report: dict[str, object] = {
        "timestamp": ts,
        "schema_version": "1.0",
        "total_modules": len(artifact.entities),
        "layer_distribution": {},
        "unknown_modules": [],
        "coverage_metrics": {},
    }
    layer_counts: Counter[str] = Counter()
    unknown_modules = []
    for entity in artifact.entities:
        if entity.entity_type == "module":
            layer_counts[entity.layer] += 1
            if entity.layer == "L_UNKNOWN":
                unknown_modules.append(
                    {
                        "adg_name": entity.adg_name,
                        "resolved_path": entity.resolved_path,
                        "identity_kind": entity.identity_kind,
                    },
                )
    layer_report["layer_distribution"] = dict(layer_counts)
    layer_report["unknown_modules"] = unknown_modules[:50]
    layer_report["coverage_metrics"] = {
        "known_modules": layer_report["total_modules"] - len(unknown_modules),
        "unknown_modules": len(unknown_modules),
        "coverage_percentage": (layer_report["total_modules"] - len(unknown_modules))
        / layer_report["total_modules"]  # type: ignore[operator]
        * 100
        if layer_report["total_modules"]
        else 0,
    }

    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    total_edges = cur.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    sqlite_edge_counts = dict(
        cur.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type").fetchall(),
    )
    stored_edge_counts = sqlite_edge_counts.copy()

    edge_report: dict[str, object] = {
        "timestamp": ts,
        "schema_version": "1.0",
        "total_edges": total_edges,
        "edge_distribution": dict(sorted(sqlite_edge_counts.items(), key=lambda x: x[1], reverse=True)),
        "critical_edge_coverage": {},
        "density_metrics": {},
    }
    critical_edges = [
        "determinism_seed",
        "emits_determinism_digest",
        "policy_verification",
        "authorize_and_execute",
        "dispatches_execution_plan",
        "enters_sandbox",
        "guardian_gate",
    ]
    critical_coverage = {edge_type: sqlite_edge_counts.get(edge_type, 0) for edge_type in critical_edges}
    edge_report["critical_edge_coverage"] = critical_coverage
    edge_report["density_metrics"] = {
        "critical_edges_found": sum(1 for count in critical_coverage.values() if count > 0),
        "critical_edge_percentage": sum(1 for count in critical_coverage.values() if count > 0)
        / len(critical_edges)
        * 100,
        "top_edge_type": max(sqlite_edge_counts.items(), key=lambda x: x[1])[0]
        if sqlite_edge_counts
        else None,
    }

    cur.execute("SELECT * FROM meta LIMIT 1")
    meta_row = cur.fetchone()
    if meta_row:
        meta_columns = [description[0] for description in cur.description]
        meta_data = dict(zip(meta_columns, meta_row))
    else:
        meta_data = {}

    total_nodes = cur.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    total_modules = cur.execute("SELECT COUNT(*) FROM nodes WHERE entity_type='module'").fetchone()[0]
    type_surface_count = cur.execute(
        "SELECT COUNT(*) FROM nodes WHERE type_surface IS NOT NULL AND type_surface != ''",
    ).fetchone()[0]
    provenance_report: dict[str, object] = {
        "timestamp": ts,
        "schema_version": meta_data.get("schema_version", "4.0.0"),
        "commit_sha": meta_data.get("commit_sha", artifact.commit_sha),
        "repo_state_hash": meta_data.get("repo_state_hash", getattr(artifact, "repo_state_hash", "")),
        "scanner_digest": meta_data.get("scanner_digest", artifact.scanner_digest),
        "artifact_digest": meta_data.get("artifact_digest", artifact.artifact_digest),
        "validation": {
            "has_commit_sha": bool(meta_data.get("commit_sha")),
            "has_repo_state_hash": bool(meta_data.get("repo_state_hash")),
            "has_scanner_digest": bool(meta_data.get("scanner_digest")),
            "has_artifact_digest": bool(meta_data.get("artifact_digest")),
        },
        "reconciliation": {
            "report_nodes": len(artifact.entities),
            "db_nodes": total_nodes,
            "report_edges": len(artifact.relations),
            "db_edges": total_edges,
            "nodes_match": len(artifact.entities) == total_nodes,
            "edges_match": len(artifact.relations) == total_edges,
        },
        "generation_metrics": {
            "scan_duration_seconds": None,
            "modules_scanned": total_modules,
            "symbols_scanned": total_nodes - total_modules,
            "total_entities": total_nodes,
        },
    }

    determinism_proof = _artifact_determinism_probe(
        adg_dir,
        ts,
        artifact,
        result,
        repo_root,
        enable_determinism_probe,
    )
    closure_report = None
    if result is not None:
        audited = {
            "decomposes_into_expected": result.manifest.decomposes_into_expected_count,
            "controls_flow_expected": result.manifest.controls_flow_expected_count,
            "flows_to_expected": result.manifest.flows_to_expected_count,
            "emits_side_effect_expected": result.manifest.emits_side_effect_expected_count,
            "resolves_callsite_expected": result.manifest.resolves_callsite_expected_count,
            "type_surface_candidate_count": result.manifest.type_surface_candidate_count,
            "type_surface_expected": result.manifest.type_surface_expected_count,
            "tests_execution_of_expected": result.manifest.tests_execution_of_expected_count,
            "violation_propagation_eligible_count": result.manifest.violation_propagation_eligible_count,
            "violation_propagation_target_count": result.manifest.violation_propagation_target_count,
        }
        semantic_stats = _semantic_precision_stats(conn)
        semantic_stats.update(
            {
                "semantic_preexisting_count": result.manifest.semantic_preexisting_count,
                "semantic_exact_map_count": result.manifest.semantic_exact_map_count,
                "semantic_fallback_count": result.manifest.semantic_fallback_count,
                "semantic_raw_edge_kind_count": result.manifest.semantic_raw_edge_kind_count,
                "execution_generic_semantic_count": result.manifest.execution_generic_semantic_count,
            },
        )
        violation_stats = _violation_surface_stats(conn)
        propagation_stats = {
            "eligible_edge_count": result.manifest.violation_propagation_eligible_count,
            "eligible_target_module_count": result.manifest.violation_propagation_target_count,
            "actual_edge_count": stored_edge_counts.get("violation_propagates_through", 0),
            "coverage_ratio": _ratio(
                stored_edge_counts.get("violation_propagates_through", 0),
                result.manifest.violation_propagation_eligible_count,
            ),
            "depth_counts": dict(
                cur.execute(
                    "SELECT symbol, COUNT(*) FROM edges "
                    "WHERE relation_type='violation_propagates_through' GROUP BY symbol",
                ).fetchall(),
            ),
        }
        closure_rows = [
            {
                "id": 1,
                "capability": "STRUCTURAL COVERAGE",
                "numerator": result.manifest.parsed_module_count,
                "denominator": max(result.manifest.discovered_module_count, 1),
                "ratio": _ratio(result.manifest.parsed_module_count, result.manifest.discovered_module_count),
                "threshold": 0.99,
                "passed": _ratio(result.manifest.parsed_module_count, result.manifest.discovered_module_count)
                >= 0.99,
            },
            {
                "id": 2,
                "capability": "GOVERNANCE VISIBILITY",
                "numerator": 1 if violation_stats["surfaces_reconciled"] else 0,
                "denominator": 1,
                "ratio": 1.0 if violation_stats["surfaces_reconciled"] else 0.0,
                "threshold": 1.0,
                "passed": bool(violation_stats["surfaces_reconciled"]),
                "evidence": violation_stats,
            },
            {
                "id": 3,
                "capability": "DETERMINISM (ARTIFACT LEVEL)",
                "numerator": sum(
                    1
                    for key in (
                        "scanner_digest_match",
                        "artifact_digest_match",
                        "node_row_digest_match",
                        "edge_row_digest_match",
                    )
                    if determinism_proof.get(key)
                ),
                "denominator": 4,
                "ratio": _ratio(
                    sum(
                        1
                        for key in (
                            "scanner_digest_match",
                            "artifact_digest_match",
                            "node_row_digest_match",
                            "edge_row_digest_match",
                        )
                        if determinism_proof.get(key)
                    ),
                    4,
                ),
                "threshold": 1.0,
                "passed": determinism_proof["determinism_status"] == "closed",
                "evidence": determinism_proof,
            },
            {
                "id": 4,
                "capability": "NODE GRANULARITY (BLOCK / EXPRESSION)",
                "numerator": stored_edge_counts.get("decomposes_into", 0),
                "denominator": max(result.manifest.decomposes_into_expected_count, 1),
                "ratio": _ratio(
                    stored_edge_counts.get("decomposes_into", 0),
                    result.manifest.decomposes_into_expected_count,
                ),
                "threshold": 0.95,
                "passed": _ratio(
                    stored_edge_counts.get("decomposes_into", 0),
                    result.manifest.decomposes_into_expected_count,
                )
                >= 0.95,
            },
            {
                "id": 5,
                "capability": "EDGE SEMANTIC PRECISION",
                "numerator": semantic_stats["semantic_edges"],
                "denominator": max(semantic_stats["total_edges"], 1),
                "ratio": semantic_stats["semantic_edge_ratio"],
                "threshold": 0.95,
                "passed": bool(
                    semantic_stats["semantic_edge_ratio"] >= 0.95
                    and semantic_stats["execution_generic_semantic_count"] == 0
                    and semantic_stats["controls_flow_specific_ratio"] >= 0.95
                    and semantic_stats["flows_to_specific_ratio"] >= 0.95
                    and semantic_stats["side_effect_specific_ratio"] >= 0.95
                    and semantic_stats["callsite_specific_ratio"] >= 0.95,
                ),
                "evidence": semantic_stats,
            },
            {
                "id": 6,
                "capability": "DATA LINEAGE",
                "numerator": semantic_stats["flows_to_total"],
                "denominator": max(result.manifest.flows_to_expected_count, 1),
                "ratio": _ratio(semantic_stats["flows_to_total"], result.manifest.flows_to_expected_count),
                "threshold": 0.95,
                "passed": _ratio(semantic_stats["flows_to_total"], result.manifest.flows_to_expected_count)
                >= 0.95,
            },
            {
                "id": 7,
                "capability": "CONTROL FLOW",
                "numerator": semantic_stats["controls_flow_total"],
                "denominator": max(result.manifest.controls_flow_expected_count, 1),
                "ratio": _ratio(
                    semantic_stats["controls_flow_total"], result.manifest.controls_flow_expected_count
                ),
                "threshold": 0.95,
                "passed": _ratio(
                    semantic_stats["controls_flow_total"], result.manifest.controls_flow_expected_count
                )
                >= 0.95,
            },
            {
                "id": 8,
                "capability": "SIDE EFFECT MODELING",
                "numerator": semantic_stats["side_effect_total"],
                "denominator": max(result.manifest.emits_side_effect_expected_count, 1),
                "ratio": _ratio(
                    semantic_stats["side_effect_total"], result.manifest.emits_side_effect_expected_count
                ),
                "threshold": 0.95,
                "passed": _ratio(
                    semantic_stats["side_effect_total"], result.manifest.emits_side_effect_expected_count
                )
                >= 0.95,
            },
            {
                "id": 9,
                "capability": "TEMPORAL ORDERING",
                "numerator": semantic_stats["ordered_execution"],
                "denominator": max(semantic_stats["execution_total"], 1),
                "ratio": semantic_stats["temporal_ordering_ratio"],
                "threshold": 0.95,
                "passed": semantic_stats["temporal_ordering_ratio"] >= 0.95,
            },
            {
                "id": 10,
                "capability": "CALLSITE RESOLUTION",
                "numerator": semantic_stats["callsite_total"],
                "denominator": max(result.manifest.resolves_callsite_expected_count, 1),
                "ratio": _ratio(
                    semantic_stats["callsite_total"], result.manifest.resolves_callsite_expected_count
                ),
                "threshold": 0.95,
                "passed": _ratio(
                    semantic_stats["callsite_total"], result.manifest.resolves_callsite_expected_count
                )
                >= 0.95,
            },
            {
                "id": 11,
                "capability": "TYPE ENRICHMENT",
                "numerator": type_surface_count,
                "denominator": max(result.manifest.type_surface_expected_count, 1),
                "ratio": _ratio(type_surface_count, result.manifest.type_surface_expected_count),
                "threshold": 0.95,
                "passed": _ratio(type_surface_count, result.manifest.type_surface_expected_count) >= 0.95,
            },
            {
                "id": 12,
                "capability": "TEST \u2192 EXECUTION LINKAGE",
                "numerator": stored_edge_counts.get("tests_execution_of", 0),
                "denominator": max(result.manifest.tests_execution_of_expected_count, 1),
                "ratio": _ratio(
                    stored_edge_counts.get("tests_execution_of", 0),
                    result.manifest.tests_execution_of_expected_count,
                ),
                "threshold": 0.95,
                "passed": _ratio(
                    stored_edge_counts.get("tests_execution_of", 0),
                    result.manifest.tests_execution_of_expected_count,
                )
                >= 0.95,
            },
            {
                "id": 13,
                "capability": "VIOLATION TRACE DEPTH",
                "numerator": propagation_stats["actual_edge_count"],
                "denominator": max(propagation_stats["eligible_edge_count"], 1),
                "ratio": propagation_stats["coverage_ratio"],
                "threshold": 0.95,
                "passed": propagation_stats["coverage_ratio"] >= 0.95,
                "evidence": propagation_stats,
            },
        ]
        closure_report = {
            "timestamp": ts,
            "schema_version": "1.0",
            "closure_rows": closure_rows,
            "semantic_surface_audit": audited,
            "violation_surfaces": violation_stats,
            "semantic_precision": semantic_stats,
            "determinism": determinism_proof,
            "summary": {
                "all_gaps_passed": all(row["passed"] for row in closure_rows),
                "passed_count": sum(1 for row in closure_rows if row["passed"]),
                "total_count": len(closure_rows),
            },
        }

    conn.close()

    from agentic_core.L2_execution.utils.async_file_ops import BufferedFileWriter
    from tools.generate.generate_full_adg import _json_dumps  # type: ignore[attr-defined]

    reports = [
        (f"layer_coverage_report_{ts}.json", layer_report),
        (f"edge_density_report_{ts}.json", edge_report),
        (f"provenance_report_{ts}.json", provenance_report),
    ]
    if closure_report is not None:
        reports.append((f"closure_validation_report_{ts}.json", closure_report))

    buffered_writer = BufferedFileWriter(buffer_size=65536)
    for filename, report_data in reports:
        report_path = reports_dir / filename
        json_str = _json_dumps(report_data)
        buffered_writer.write_buffered(
            str(report_path),
            iter([json_str]),
            mode="w",
        )
        print(f"[ADG] Report generated: {filename}")

    return closure_report
