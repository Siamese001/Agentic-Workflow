import json
import sqlite3
from pathlib import Path

from tools.reports.adg_cleanup_queue_and_p2_blocker_trace import (
    emit_mandatory_adg_cleanup_queue_and_p2_blocker_trace,
)


def _sqlite(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            create table violations(
                id integer primary key,
                edge_id integer not null,
                category text not null,
                evidence text not null,
                file_path text not null,
                line_no integer not null,
                disposition text not null,
                disposition_source text,
                disposition_date text,
                severity text not null,
                violation_class text not null
            )
            """
        )
        rows = [
            (
                1,
                1001,
                "antipattern",
                "Exception",
                "apps_rg/runtime/c0/fact_vector_write_back.py",
                343,
                "untriaged",
                "",
                "",
                "MEDIUM",
                "hygiene",
            ),
            (
                2,
                1002,
                "antipattern",
                "Exception",
                "apps_rg/runtime/c0/fact_vector_write_back.py",
                441,
                "untriaged",
                "",
                "",
                "MEDIUM",
                "hygiene",
            ),
            (
                3,
                1003,
                "antipattern",
                "OSError",
                "apps_rg/runtime/bindings/u0_package_ingest.py",
                61,
                "untriaged",
                "",
                "",
                "MEDIUM",
                "hygiene",
            ),
            (
                4,
                1004,
                "antipattern",
                "from agentic_core.L6_system_learning.future_run_promotion import *",
                "agentic_core/L6_learning/__init__.py",
                34,
                "untriaged",
                "",
                "",
                "MEDIUM",
                "hygiene",
            ),
            (
                5,
                1005,
                "antipattern",
                "from apps_rg.runtime.sections.executive_summary_regen_dispatch import *",
                "apps_rg/runtime/sections/executive_summary_qwen_regen_dispatch.py",
                15,
                "untriaged",
                "",
                "",
                "MEDIUM",
                "hygiene",
            ),
        ]
        conn.executemany("insert into violations values (?,?,?,?,?,?,?,?,?,?,?)", rows)


def _dead_code_report(path: Path) -> None:
    doc = {
        "status": "PASS",
        "summary": {
            "total_dead_code_candidates": 4,
            "total_dead_imports": 4,
            "total_unresolved_imports": 191,
            "first_party_low_confidence_ratio": 3.2,
            "inferred_symbol_ratio": 9.7,
        },
        "dead_code_candidates": {
            "total_dead_code_candidates": 4,
            "dead_code_by_layer": {"L0": 4},
            "dead_code_by_entity_type": {"module": 4},
            "dead_code_by_confidence": {"HIGH": 4},
            "dead_code_hotspots": [("ADG::Module::legacy_path", 3), ("ADG::Module::stale_path", 1)],
        },
        "dead_imports": {
            "total_dead_imports": 4,
            "dead_imports_by_layer": {"L0": 4},
            "dead_imports_by_domain": {"core": 4},
            "dead_imports_by_confidence": {"HIGH": 4},
            "dead_imports_by_entity_type": {"module": 4},
            "dead_import_hotspots": [("ADG::Module::legacy_path", 3), ("ADG::Module::stale_path", 1)],
            "l4_dead_imports": 0,
        },
        "unresolved_imports": {
            "unresolved_hotspots": [
                ("tests/_apps_contract/test_apps_rg_u0_structured_resume_support.py", 105),
                ("tests/ops_scripts/ci/test_adg_accelerator_compliance_gate.py", 62),
                ("tests/_archived_obsolete/ops_scripts/ci/test_graphdb_gates.py", 24),
            ]
        },
        "low_confidence_zones": {
            "first_party_low_confidence_ratio": 3.2,
        },
        "inferred_symbols": {
            "inferred_symbol_ratio": 9.7,
        },
    }
    path.write_text(json.dumps(doc, indent=2, sort_keys=True), encoding="utf-8")


def _p2_ratchet(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "exception_swallow_ceiling": 3,
                "snapshot": "adg_indexed_20260618_120000.sqlite",
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def _gate_manifest(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "timestamp": "2026-06-18T10:30:15Z",
                "certification_status": "failed",
                "failed_gates": [{"name": "p2_ratchet"}],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def test_emit_cleanup_queue_and_p2_trace_writes_latest_copies(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts" / "adg"
    artifacts.mkdir(parents=True)
    docs = tmp_path / "docs_mirror"
    db = artifacts / "adg_indexed_20260618_120000.sqlite"
    _sqlite(db)
    _dead_code_report(artifacts / "dead_code_zone_control_report_latest.json")
    _p2_ratchet(artifacts / "p2_ratchet.json")
    _gate_manifest(artifacts / "adg_gate_invocation_manifest_20260618_0625.json")

    rc, out = emit_mandatory_adg_cleanup_queue_and_p2_blocker_trace(
        adg_artifacts_dir=artifacts,
        ts="run",
        print_inline=False,
        fail_closed=False,
        docs_dir=docs,
    )

    assert rc == 0
    assert out == artifacts / "adg_cleanup_queue_and_p2_blocker_trace_run.json"
    assert (artifacts / "adg_cleanup_queue_and_p2_blocker_trace.json").is_file()
    assert (artifacts / "adg_cleanup_queue_and_p2_blocker_trace.md").is_file()
    assert (artifacts / "adg_cleanup_queue_and_p2_blocker_trace_latest.json").is_file()
    assert (artifacts / "adg_cleanup_queue_and_p2_blocker_trace_latest.md").is_file()
    assert (docs / "adg_cleanup_queue_and_p2_blocker_trace.json").is_file()
    assert (docs / "adg_cleanup_queue_and_p2_blocker_trace.md").is_file()

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["artifact_kind"] == "adg_cleanup_queue_and_p2_blocker_trace"
    assert data["cleanup"]["summary"]["dead_code_candidates"] == 4
    assert data["cleanup"]["brief"]["status"] == "DELETION_CANDIDATES"
    assert data["cleanup"]["priority_rows"][0]["decision"] == "delete_after_deprecation"
    assert data["cleanup"]["priority_rows"][0]["scope"] == "ADG::Module::legacy_path"
    assert data["cleanup"]["live_queue"][0]["scope"] == "tests/_apps_contract/test_apps_rg_u0_structured_resume_support.py"
    assert data["p2"]["summary"]["current_medium_hygiene_count"] == 5
    assert data["p2"]["summary"]["delta"] == 2
    assert data["p2"]["summary"]["failed_run_timestamp"] == "2026-06-18T10:30:15Z"


def test_emit_cleanup_queue_and_p2_trace_inline_uses_bcg_brief(tmp_path: Path, capsys) -> None:
    artifacts = tmp_path / "artifacts" / "adg"
    artifacts.mkdir(parents=True)
    _sqlite(artifacts / "adg_indexed_20260618_120000.sqlite")
    _dead_code_report(artifacts / "dead_code_zone_control_report_latest.json")
    _p2_ratchet(artifacts / "p2_ratchet.json")
    _gate_manifest(artifacts / "adg_gate_invocation_manifest_20260618_0625.json")

    rc, _ = emit_mandatory_adg_cleanup_queue_and_p2_blocker_trace(
        adg_artifacts_dir=artifacts,
        ts="run",
        print_inline=True,
        fail_closed=False,
        docs_dir=tmp_path / "docs_mirror",
    )

    assert rc == 0
    captured = capsys.readouterr()
    assert "# ADG Cleanup Queue and P2 Ratchet Trace" in captured.out
    assert "### BCG Cleanup Brief" in captured.out
    assert "DELETION_CANDIDATES" in captured.out
    assert "### BCG P2 Ratchet Brief" in captured.out
    assert "Maintain SVP engineer-level repo standards" in captured.out
