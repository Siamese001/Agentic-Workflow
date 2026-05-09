"""W1 baseline scan for apps_rg declarative-ingress-only governance plan.

Reads the canonical ADG SQLite snapshot directly (per constitutional §28
when MCP transport is unstable) and emits:

  1. Fan-in / fan-out for the 8 quarantine targets.
  2. Schema discovery for the relations table.
  3. Runtime-authority smell inventory across live apps_rg/ files.
  4. Cross-app caller enumeration (any non-apps_rg, non-test importer).

Output: artifacts/_w1_apps_rg_baseline.json
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SNAPSHOT = REPO / "artifacts" / "adg" / "adg_indexed_05052026_0722.sqlite"
OUT = REPO / "artifacts" / "_w1_apps_rg_baseline.json"

# Module IDs from prior query
TARGETS = {
    "RgResumeOrchestrator":     {"module_id": 3296, "symbol_id": 52243, "path": "apps_rg/reasoning/RgResumeOrchestrator.py"},
    "_llm_client":              {"module_id": 3244, "symbol_id": 52134, "path": "apps_rg/integrations/hops/_llm_client.py"},
    "jd_planner":               {"module_id": 3155, "symbol_id": None,  "path": "apps_rg/L1_cognition/jd_planner.py"},
    "resume_planning_engine":   {"module_id": 3211, "symbol_id": None,  "path": "apps_rg/engines/resume_planning_engine.py"},
    "RGStrategyExecutor":       {"module_id": 3288, "symbol_id": 52229, "path": "apps_rg/reasoning/RGStrategyExecutor.py"},
    "RgStrategicPlannerAgent":  {"module_id": 3297, "symbol_id": 52245, "path": "apps_rg/reasoning/RgStrategicPlannerAgent.py"},
    "strategic_planning_engine":{"module_id": 3222, "symbol_id": None,  "path": "apps_rg/engines/strategic_planning_engine.py"},
    "resume_section_node_types":{"module_id": 3367, "symbol_id": None,  "path": "apps_rg/types/resume_section_node_types.py"},
}

# §10 forbidden patterns for live-path smell inventory
FORBIDDEN_NAME_LIKE = [
    "%Planner%", "%Router%", "%Orchestrator%", "%Executor%", "%Agent%",
    "%LlmClient%", "%llm_client%", "%Gateway%", "%Judge%", "%Strategy%",
    "%Workflow%", "%Generator%",
]


def fetchall_dicts(cur, sql, params=()):
    cur.execute(sql, params)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def main() -> None:
    conn = sqlite3.connect(str(SNAPSHOT))
    cur = conn.cursor()

    out: dict = {
        "snapshot": str(SNAPSHOT.relative_to(REPO)),
        "targets": {},
        "smell_inventory": {},
        "cross_app_callers": {},
        "schema": {},
    }

    # ---- Schema discovery ----
    out["schema"]["edges_columns"] = fetchall_dicts(cur, "PRAGMA table_info(edges)")
    out["schema"]["edges_relation_types"] = fetchall_dicts(
        cur, "SELECT relation_type, COUNT(*) AS n FROM edges GROUP BY relation_type ORDER BY n DESC LIMIT 20"
    )

    # ---- Fan-in / fan-out per target ----
    for name, meta in TARGETS.items():
        ids = [meta["module_id"]]
        if meta["symbol_id"]:
            ids.append(meta["symbol_id"])
        placeholders = ",".join("?" * len(ids))

        fanin_imports = fetchall_dicts(cur, f"""
            SELECT e.relation_type, n.id AS src_id, n.adg_name AS src_name, n.resolved_path AS src_path, n.layer
            FROM edges e
            JOIN nodes n ON n.id = e.src_id
            WHERE e.dst_id IN ({placeholders})
              AND e.relation_type = 'imports'
            ORDER BY n.resolved_path
            LIMIT 200
        """, ids)

        fanin_all_rel = fetchall_dicts(cur, f"""
            SELECT e.relation_type, COUNT(*) AS n
            FROM edges e
            WHERE e.dst_id IN ({placeholders})
            GROUP BY e.relation_type
            ORDER BY n DESC
        """, ids)

        fanout_imports = fetchall_dicts(cur, f"""
            SELECT e.relation_type, n.id AS dst_id, n.adg_name AS tgt_name, n.resolved_path AS tgt_path, n.layer
            FROM edges e
            JOIN nodes n ON n.id = e.dst_id
            WHERE e.src_id IN ({placeholders})
              AND e.relation_type = 'imports'
            ORDER BY n.resolved_path
            LIMIT 200
        """, ids)

        fanout_all_rel = fetchall_dicts(cur, f"""
            SELECT e.relation_type, COUNT(*) AS n
            FROM edges e
            WHERE e.src_id IN ({placeholders})
              GROUP BY e.relation_type
              ORDER BY n DESC
        """, ids)

        out["targets"][name] = {
            "ids": ids,
            "path": meta["path"],
            "fanin_imports": fanin_imports,
            "fanin_count_imports": len(fanin_imports),
            "fanin_relation_summary": fanin_all_rel,
            "fanout_imports_count": len(fanout_imports),
            "fanout_relation_summary": fanout_all_rel,
        }

        # cross-app callers (importers from any path NOT under apps_rg/ or tests/)
        cross_app = [
            r for r in fanin_imports
            if r["src_path"] and not (
                r["src_path"].startswith("apps_rg/")
                or r["src_path"].startswith("tests/")
                or r["src_path"].startswith("docs/")
            )
        ]
        out["cross_app_callers"][name] = cross_app

    # ---- Runtime-authority smell inventory across live apps_rg/ ----
    smell_rows = []
    for like in FORBIDDEN_NAME_LIKE:
        rows = fetchall_dicts(cur, """
            SELECT id, adg_name, entity_type, layer, resolved_path
            FROM nodes
            WHERE resolved_path LIKE 'apps_rg/%'
              AND resolved_path NOT LIKE 'apps_rg/tests/%'
              AND resolved_path NOT LIKE 'apps_rg/docs/%'
              AND adg_name LIKE ?
            ORDER BY resolved_path, adg_name
            LIMIT 100
        """, (like,))
        for r in rows:
            r["matched_pattern"] = like
            smell_rows.append(r)

    # Dedup by id
    seen = set()
    deduped = []
    for r in smell_rows:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        deduped.append(r)
    out["smell_inventory"]["matches"] = deduped
    out["smell_inventory"]["match_count"] = len(deduped)
    out["smell_inventory"]["distinct_files"] = sorted({r["resolved_path"] for r in deduped})

    # ---- All apps_rg/ live-path files (modules) ----
    all_modules = fetchall_dicts(cur, """
        SELECT id, resolved_path
        FROM nodes
        WHERE entity_type = 'module'
          AND resolved_path LIKE 'apps_rg/%'
          AND resolved_path NOT LIKE 'apps_rg/tests/%'
          AND resolved_path NOT LIKE 'apps_rg/docs/%'
          AND resolved_path NOT LIKE 'apps_rg/fixtures/%'
        ORDER BY resolved_path
    """)
    out["all_apps_rg_modules"] = all_modules
    out["all_apps_rg_modules_count"] = len(all_modules)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"[w1-baseline] wrote {OUT.relative_to(REPO)}")
    print(f"[w1-baseline] live apps_rg/ modules: {len(all_modules)}")
    print(f"[w1-baseline] runtime-authority smell matches: {len(deduped)} across "
          f"{len(out['smell_inventory']['distinct_files'])} files")
    for name, t in out["targets"].items():
        cross = len(out["cross_app_callers"][name])
        print(f"[w1-baseline] {name}: fan_in_imports={t['fanin_count_imports']} (cross-app={cross})")


if __name__ == "__main__":
    main()
