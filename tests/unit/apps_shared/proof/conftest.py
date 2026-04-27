"""Shared fixtures for apps_shared/proof tests."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def tiny_adg_snapshot(tmp_path: Path) -> Path:
    """Create a minimal SQLite DB with the ADG schema fragments tests need."""
    p = tmp_path / "tiny_adg.sqlite"
    con = sqlite3.connect(p)
    cur = con.cursor()
    # nodes table for app_inventory.discover_apps
    cur.execute(
        """
        CREATE TABLE nodes (
            id TEXT PRIMARY KEY,
            resolved_path TEXT,
            file_path TEXT,
            layer TEXT
        )
        """
    )
    fixtures = [
        ("n1", "apps_eval/integrations/foo.py", "apps_eval/integrations/foo.py", "L_APP"),
        ("n2", "apps_eval/engines/bar.py", "apps_eval/engines/bar.py", "L_APP"),
        ("n3", "apps_shared/proof/proof_contracts.py", "apps_shared/proof/proof_contracts.py", "L_APP"),
        ("n4", "agentic_core/L0_routing/foo.py", "agentic_core/L0_routing/foo.py", "L0"),
    ]
    cur.executemany("INSERT INTO nodes VALUES (?, ?, ?, ?)", fixtures)

    # Minimal versions of the views used by adg_queries + write_sovereignty.
    # Each view returns zero rows for our test apps but has the COLUMNS each
    # production query expects, so SELECTs succeed against an empty result set.
    view_defs = {
        "mv_trace_replay_eval_gaps": (
            "SELECT id AS node_id, resolved_path AS file, layer, "
            "0 AS has_trace, 0 AS has_replay_link, 0 AS has_eval, "
            "NULL AS gap_type FROM nodes WHERE 1=0"
        ),
        "mv_replay_surface_gaps": (
            "SELECT id AS node_id, resolved_path AS file, layer, "
            "0 AS mutation_count, 0 AS replay_link_count, 0 AS gap_flag "
            "FROM nodes WHERE 1=0"
        ),
        "mv_task_contract_gaps": (
            "SELECT id AS node_id, resolved_path AS file, layer, "
            "0 AS action_edge_count, 0 AS schema_or_policy_count, "
            "0 AS contract_impl_count, 0 AS gap_flag "
            "FROM nodes WHERE 1=0"
        ),
        "mv_write_sovereignty_paths": (
            "SELECT id AS edge_id, resolved_path AS writer_file, "
            "layer AS writer_layer, '' AS write_symbol, 0 AS write_line, "
            "0 AS is_uwg_routed, 0 AS is_direct_infra_write, "
            "'P0' AS severity FROM nodes WHERE 1=0"
        ),
        "v_p0_apps_direct_infra": (
            "SELECT id AS violation_edge_id, id AS consumer_id, "
            "resolved_path AS consumer_file, layer AS consumer_layer, "
            "'' AS import_symbol, 0 AS import_line, "
            "'apps_direct_infra' AS violation_type FROM nodes WHERE 1=0"
        ),
        "mv_gateway_bypass_paths": (
            "SELECT id AS edge_id, resolved_path AS src_file, "
            "layer AS src_layer, '' AS provider_symbol, "
            "resolved_path AS source_file, 0 AS line_no, "
            "'' AS bypass_type FROM nodes WHERE 1=0"
        ),
        "v_p1_not_on_spine": (
            "SELECT id AS adapter_id, resolved_path AS adapter_file, "
            "layer AS adapter_layer, '' AS adapter_name, "
            "0 AS spine_caller_count, '' AS violation_type "
            "FROM nodes WHERE 1=0"
        ),
        "v_p1_ad_hoc_imports": (
            "SELECT id AS violation_edge_id, id AS consumer_id, "
            "resolved_path AS consumer_file, layer AS consumer_layer, "
            "'' AS import_symbol, 0 AS import_line, "
            "'' AS violation_type FROM nodes WHERE 1=0"
        ),
        "mv_capability_and_egress_gaps": (
            "SELECT id AS node_id, resolved_path AS file, layer, "
            "0 AS provider_invoke_count, 0 AS capability_route_count, "
            "0 AS egress_gate_count, NULL AS gap_type FROM nodes WHERE 1=0"
        ),
        "mv_prompt_assembly_wiring_gaps": (
            "SELECT id AS node_id, '' AS target_symbol, "
            "resolved_path AS target_file, layer, 0 AS total_callers, "
            "0 AS live_callers, 0 AS test_callers, NULL AS gap_type "
            "FROM nodes WHERE 1=0"
        ),
        "mv_exit_disposition_coverage": (
            "SELECT id AS node_id, resolved_path AS file, layer, "
            "0 AS outgoing_terminal_count, 0 AS is_terminal_covered, "
            "NULL AS gap_type FROM nodes WHERE 1=0"
        ),
        "v_p0_write_bypass_uwg": (
            "SELECT id AS violation_edge_id, id AS writer_id, "
            "resolved_path AS writer_file, layer AS writer_layer, "
            "'' AS write_symbol, 0 AS write_line, "
            "'write_bypass_uwg' AS violation_type FROM nodes WHERE 1=0"
        ),
    }
    for name, body in view_defs.items():
        cur.execute(f"CREATE VIEW {name} AS {body}")
    con.commit()
    con.close()
    return p
