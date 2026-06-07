#!/usr/bin/env python3
"""
One-off back-fill: Cat 4 territory cleanup HITL decisions (Apr 10 2026 session).
Run once then delete.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
db_path = repo_root / ".claude" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
ddl = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS decisions (
    decision_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, branch TEXT, commit_sha TEXT,
    task_id TEXT, decision_type TEXT NOT NULL DEFAULT 'unknown', request_summary TEXT,
    normalized_intent TEXT, user_goal TEXT, constraints_json TEXT, risk_profile_json TEXT,
    blast_radius_estimate TEXT, options_json TEXT, recommended_option_id TEXT,
    selected_option_id TEXT, selection_rationale TEXT, status TEXT NOT NULL DEFAULT 'surfaced'
);
CREATE TABLE IF NOT EXISTS decision_scope (
    scope_id INTEGER PRIMARY KEY AUTOINCREMENT, decision_id TEXT NOT NULL REFERENCES decisions(decision_id),
    file_path TEXT, symbol_name TEXT, symbol_kind TEXT, layer TEXT, repo_area TEXT, tags TEXT
);
CREATE TABLE IF NOT EXISTS decision_outcomes (
    outcome_id INTEGER PRIMARY KEY AUTOINCREMENT, decision_id TEXT NOT NULL REFERENCES decisions(decision_id),
    execution_completed INTEGER DEFAULT 0, tests_passed INTEGER DEFAULT 0,
    regression_found INTEGER DEFAULT 0, rollback_required INTEGER DEFAULT 0,
    followup_decision_id TEXT, promote_to_pattern INTEGER DEFAULT 0, outcome_notes TEXT
);
CREATE VIRTUAL TABLE IF NOT EXISTS decisions_fts USING fts5(
    decision_id UNINDEXED, normalized_intent, request_summary, user_goal, selection_rationale,
    content=decisions, content_rowid=rowid
);
"""

branch = "main"
sha = "7a97507efe"  # last Cat 4 commit

decisions = [
    # --- L3 Group B ---
    {
        "key": "l3_coordination_declare",
        "decision_type": "architecture_choice",
        "layer": "L3_orchestration",
        "repo_area": "agentic_core/L3_orchestration/reasoning/coordination",
        "request_summary": "L3/reasoning/coordination/ undeclared — 2 files (lease_coordinator, work_coordination_bundle), 0 importers, not in _constants.py",
        "normalized_intent": "declare undeclared L3 reasoning subfolder coordination",
        "user_goal": "Territory Cat 4: bring territories.yaml and _constants.py in sync with filesystem",
        "recommended_option_id": "A: Declare in territories.yaml + add to _constants.py",
        "selected_option_id": "A: Declare in territories.yaml + add to _constants.py",
        "selection_rationale": "Names architecturally coherent for L3. Absent from _constants.py but not absent from intent.",
        "options_json": json.dumps(["A: Declare", "B: Delete"]),
        "status": "executed",
        "execution_completed": 1,
    },
    {
        "key": "l3_learning_move_seams",
        "decision_type": "architecture_choice",
        "layer": "L3_orchestration",
        "repo_area": "agentic_core/L3_orchestration/reasoning/learning",
        "request_summary": "L3/reasoning/learning/ — 1 file (workflow_learning_bridge.py). Intentional seam bridging L3->system_learning. 0 importers. Not in _constants.py. Misplaced: bridge/seam not reasoning component.",
        "normalized_intent": "move L3 learning bridge to seams layer boundary fix",
        "user_goal": "Layer purity — seams belong in seams/",
        "recommended_option_id": "B: Move to agentic_core/seams/",
        "selected_option_id": "B: Move to agentic_core/seams/",
        "selection_rationale": "File's own docstring says it's a bridge. seams/ exists exactly for cross-layer integration contracts. reasoning/learning/ is architectural misclassification.",
        "options_json": json.dumps(["B: Move to seams/", "A: Declare as-is", "C: Delete"]),
        "status": "executed",
        "execution_completed": 1,
    },
    {
        "key": "l3_territory_healing_move_tools",
        "decision_type": "architecture_choice",
        "layer": "L3_orchestration",
        "repo_area": "agentic_core/L3_orchestration/reasoning/territory_healing",
        "request_summary": "L3/reasoning/territory_healing/ — 3 files, 0 importers. territory_heal.py uses sys.path.insert — CLI script pattern. Ops tooling inside L3 framework layer.",
        "normalized_intent": "move territory healing ops scripts out of L3 framework to tools",
        "user_goal": "Layer purity — ops tooling belongs in ops_scripts/ or tools/",
        "recommended_option_id": "B: Move to tools/generate/",
        "selected_option_id": "B: Move to tools/generate/ or ops_scripts/",
        "selection_rationale": "sys.path.insert + CLI entry point = ops script. L3/reasoning/ is for decision-making framework, not SSOT remediation scripts.",
        "options_json": json.dumps(["B: Move to tools/generate/", "A: Declare as-is", "C: Delete"]),
        "status": "executed",
        "execution_completed": 1,
    },
    {
        "key": "l3_registry_declare",
        "decision_type": "architecture_choice",
        "layer": "L3_orchestration",
        "repo_area": "agentic_core/L3_orchestration/utils/registry",
        "request_summary": "L3/utils/registry/ — 3 files (agent_capability_registry, agent_dispatch_registry, capability_registry), 0 importers, not in _constants.py.",
        "normalized_intent": "declare undeclared L3 utils subfolder registry",
        "user_goal": "Territory Cat 4: bring territories.yaml and _constants.py in sync",
        "recommended_option_id": "A: Declare in territories.yaml + add to _constants.py",
        "selected_option_id": "A: Declare in territories.yaml + add to _constants.py",
        "selection_rationale": "Registry utilities are standard pattern in orchestration layers. 0 importers but likely pre-wired for future wiring.",
        "options_json": json.dumps(["A: Declare", "B: Delete"]),
        "status": "executed",
        "execution_completed": 1,
    },
    # --- L4 Group B ---
    {
        "key": "l4_cache_naming_fix",
        "decision_type": "refactor_scope",
        "layer": "L4_state",
        "repo_area": "agentic_core/L4_state/cache",
        "request_summary": "L4_state/cache/ on disk (10 files) but _constants.py declares it as 'caching'. Name mismatch — one must win.",
        "normalized_intent": "resolve L4 cache vs caching name mismatch between filesystem and _constants.py",
        "user_goal": "SSOT consistency — filesystem name vs _constants.py declaration",
        "recommended_option_id": "B: Keep cache/ — fix _constants.py from caching to cache",
        "selected_option_id": "B: Keep cache/ — fix _constants.py from caching to cache",
        "selection_rationale": "'cache' is the universal convention. The _constants.py entry was a typo. 10 files already use agentic_core.L4_state.cache.*",
        "options_json": json.dumps(["B: Keep cache/ fix _constants.py", "A: Rename to caching/"]),
        "status": "executed",
        "execution_completed": 1,
    },
    {
        "key": "l4_enforcement_authority_declare",
        "decision_type": "architecture_choice",
        "layer": "L4_state",
        "repo_area": "agentic_core/L4_state/enforcement/authority",
        "request_summary": "L4/enforcement/authority/ — 4 files (memory_authority, run_scoped_state_authority, run_scoped_state_ledger, run_state_authority), 0 importers, not in _constants.py.",
        "normalized_intent": "declare undeclared L4 enforcement subfolder authority",
        "user_goal": "Territory Cat 4: enforcement/authority is architecturally coherent",
        "recommended_option_id": "A: Declare in territories.yaml + _constants.py",
        "selected_option_id": "A: Declare in territories.yaml + _constants.py",
        "selection_rationale": "Subdirectory of already-declared enforcement/. Domain-appropriate names (state authority, memory authority).",
        "options_json": json.dumps(["A: Declare", "B: Delete"]),
        "status": "executed",
        "execution_completed": 1,
    },
    {
        "key": "l4_stores_data_bleed",
        "decision_type": "deletion_strategy",
        "layer": "L4_state",
        "repo_area": "agentic_core/L4_state/utils/stores",
        "request_summary": "utils/stores/ contains only drift_timeline.jsonl — a JSON Lines runtime data file, not Python code. Cat 2 data bleed.",
        "normalized_intent": "remove L4 utils stores data bleed jsonl runtime artifact",
        "user_goal": "Remove runtime data from source tree, add *.jsonl to excluded_paths",
        "recommended_option_id": "A: git rm stores/ + add *.jsonl to excluded_paths.yaml",
        "selected_option_id": "A: git rm stores/ + add *.jsonl to excluded_paths.yaml",
        "selection_rationale": ".jsonl files are runtime output. A stores/ dir with zero Python files has no reason to exist in source tree.",
        "options_json": json.dumps(["A: git rm + gitignore", "B: Declare as-is"]),
        "status": "executed",
        "execution_completed": 1,
    },
    {
        "key": "l4_prompt_taxonomy_move_l1",
        "decision_type": "architecture_choice",
        "layer": "L4_state",
        "repo_area": "agentic_core/L4_state/utils/prompt_taxonomy",
        "request_summary": "L4/utils/prompt_taxonomy/ — 12 files (categories.py, loader.py, template_manifest.py + 9 Jinja2 templates), 0 importers. Layer boundary violation — prompt taxonomy is cognition-layer concern, not state-layer.",
        "normalized_intent": "move prompt taxonomy from L4 to L1_cognition layer boundary fix",
        "user_goal": "Layer purity — prompt categorization belongs in L1_cognition not L4_state",
        "recommended_option_id": "B: Move to L1_cognition/utils/prompt_taxonomy/",
        "selected_option_id": "B: Move to L1_cognition/utils/prompt_taxonomy/",
        "selection_rationale": "Prompt categorization (C0_dependency, I0_instructional, S0_system_state) is cognition-layer concern. L4 notes say 'graph/ledger/schemas DISSOLVED'. 0 importers so no import path updates needed.",
        "options_json": json.dumps(["B: Move to L1", "A: Declare as-is in L4", "C: Delete"]),
        "status": "executed",
        "execution_completed": 1,
    },
    {
        "key": "l4_utils_six_subdirs_declare",
        "decision_type": "architecture_choice",
        "layer": "L4_state",
        "repo_area": "agentic_core/L4_state/utils",
        "request_summary": "6 remaining L4 utils/ subdirs: context, ledger, lifecycle, retrieval, storage, versioning — all domain-coherent names, 0 importers, not in _constants.py.",
        "normalized_intent": "declare all 6 remaining L4 utils subdirs context ledger lifecycle retrieval storage versioning",
        "user_goal": "Territory Cat 4: batch declare domain-coherent utils subdirs",
        "recommended_option_id": "A: Declare all 6 + fix _constants.py phantom storage",
        "selected_option_id": "A: Declare all 6 in territories.yaml + fix _constants.py phantom",
        "selection_rationale": "Naming unambiguous for L4. Batch faster than 6 individual HITLs for identical decisions.",
        "options_json": json.dumps(["A: Declare all 6 batch", "B: Review individually"]),
        "status": "executed",
        "execution_completed": 1,
    },
]


def make_id(key: str) -> str:
    return "dec_" + hashlib.sha1(key.encode()).hexdigest()[:12]


def main() -> None:
    conn = sqlite3.connect(str(db_path), timeout=10)
    conn.executescript(ddl)

    ts_base = datetime(2026, 4, 10, 11, 30, 0, tzinfo=timezone.utc)

    for i, d in enumerate(decisions):
        did = make_id(str(d["key"]))
        ts = ts_base.replace(minute=30 + i * 3).isoformat()

        existing = conn.execute("SELECT 1 FROM decisions WHERE decision_id=?", (did,)).fetchone()
        if existing:
            print(f"  SKIP (already exists): {d['key']}")
            continue

        conn.execute(
            """INSERT OR IGNORE INTO decisions
               (decision_id, created_at, branch, commit_sha, decision_type,
                request_summary, normalized_intent, user_goal,
                recommended_option_id, selected_option_id, selection_rationale,
                options_json, status)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                did,
                ts,
                branch,
                sha,
                d["decision_type"],
                d["request_summary"],
                d["normalized_intent"],
                d.get("user_goal", ""),
                d["recommended_option_id"],
                d["selected_option_id"],
                d["selection_rationale"],
                d["options_json"],
                d["status"],
            ),
        )
        conn.execute(
            """INSERT INTO decision_scope (decision_id, layer, repo_area, tags)
               VALUES (?,?,?,?)""",
            (did, d["layer"], d["repo_area"], "cat4,territory_cleanup"),
        )
        conn.execute(
            """INSERT INTO decision_outcomes
               (decision_id, execution_completed, tests_passed, regression_found, rollback_required)
               VALUES (?,?,0,0,0)""",
            (did, d.get("execution_completed", 0)),
        )
        conn.execute(
            """INSERT INTO decisions_fts
               (decision_id, normalized_intent, request_summary, user_goal, selection_rationale)
               VALUES (?,?,?,?,?)""",
            (
                did,
                d["normalized_intent"],
                d["request_summary"],
                d.get("user_goal", ""),
                d["selection_rationale"],
            ),
        )
        print(f"  INSERTED: {d['key']}")

    conn.commit()
    conn.close()

    # Verify
    conn2 = sqlite3.connect(str(db_path))
    count = conn2.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
    conn2.close()
    print(f"\nTotal decisions in ledger: {count}")


if __name__ == "__main__":
    main()
