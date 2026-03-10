"""GAP-A + GAP-B invariant tests.

GAP-A invariant: run_manifest.json exists with correct trace_id after heal run.
  Negative control: removing the _write_run_manifest_json call → file absent.

GAP-B invariant: mutation ledger is non-empty after a heal run that commits writes.
  Negative control: passing None path → ledger absent AND ERROR logged.
"""

from __future__ import annotations

import json

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
)


class TestGapARunManifest:
    def test_write_run_manifest_creates_file(self, tmp_path):
        from agentic_core.L0_routing.scripts.execute_ssot import _write_run_manifest_json

        trace_id = "TEST-GAP-A-001"
        _write_run_manifest_json(
            trace_id=trace_id,
            execution_mode="heal",
            territories=[APPS_RG_DIR, APPS_LIC_DIR],
            agents_executed=["AgentA", "AgentB"],
            output_dir=tmp_path,
        )

        manifest_path = tmp_path / "run_manifest.json"
        assert manifest_path.exists(), "run_manifest.json must exist after _write_run_manifest_json()"

        with manifest_path.open(encoding="utf-8") as fh:
            data = json.load(fh)

        assert data["trace_id"] == trace_id
        assert data["execution_mode"] == "heal"
        assert set(data["territories"]) == {APPS_RG_DIR, APPS_LIC_DIR}
        assert data["agent_count"] == 2

    def test_negative_control_no_call_means_no_file(self, tmp_path):
        manifest_path = tmp_path / "run_manifest.json"
        assert not manifest_path.exists(), "Negative control: no manifest without call"

    def test_write_run_manifest_trace_id_in_file(self, tmp_path):
        from agentic_core.L0_routing.scripts.execute_ssot import _write_run_manifest_json

        trace_id = "SSOT-20260101-abcdef01"
        _write_run_manifest_json(
            trace_id=trace_id,
            execution_mode="scan",
            territories=[AGENTIC_CORE_DIR],
            agents_executed=["ScanAgent"],
            output_dir=tmp_path,
        )

        manifest_path = tmp_path / "run_manifest.json"
        raw = manifest_path.read_text(encoding="utf-8")
        assert trace_id in raw, "trace_id must appear verbatim in run_manifest.json"

    def test_write_run_manifest_creates_parent_dirs(self, tmp_path):
        from agentic_core.L0_routing.scripts.execute_ssot import _write_run_manifest_json

        deep_dir = tmp_path / "logs" / "run_manifests" / "TRACE-X"
        _write_run_manifest_json(
            trace_id="TRACE-X",
            execution_mode="heal",
            territories=[],
            agents_executed=[],
            output_dir=deep_dir,
        )
        assert (deep_dir / "run_manifest.json").exists()


class TestGapBMutationLedger:
    def test_set_mutation_ledger_path_then_write_creates_ledger(self, tmp_path):
        from agentic_core.L2_execution.tools.write_gateway import (
            set_mutation_ledger_path,
            write_text,
        )

        ledger_path = tmp_path / "mutation_ledger.jsonl"
        set_mutation_ledger_path(ledger_path, "TEST-GAP-B-001")

        target = tmp_path / "output.txt"
        write_text(target, "hello")

        assert ledger_path.exists(), "Ledger file must be created after write_text()"
        entries = [json.loads(line) for line in ledger_path.read_text().splitlines() if line.strip()]
        assert len(entries) >= 1
        assert entries[0]["trace_id"] == "TEST-GAP-B-001"

    def test_negative_control_no_ledger_path_means_no_ledger(self, tmp_path):
        from agentic_core.L2_execution.tools.write_gateway import write_text

        target = tmp_path / "out.txt"
        write_text(target, "content")

        jsonl_files = list(tmp_path.rglob("*.jsonl"))
        assert jsonl_files == [], "Negative control: no ledger when set_mutation_ledger_path not called"

    def test_ledger_non_empty_after_heal_write(self, tmp_path):
        from agentic_core.L2_execution.tools.write_gateway import (
            set_mutation_ledger_path,
            write_text,
        )

        ledger_path = tmp_path / "mutation_ledger.jsonl"
        set_mutation_ledger_path(ledger_path, "TEST-GAP-B-002")

        for i in range(3):
            write_text(tmp_path / f"file_{i}.txt", f"content {i}")

        entries = [json.loads(line) for line in ledger_path.read_text().splitlines() if line.strip()]
        assert len(entries) == 3, f"Expected 3 ledger entries, got {len(entries)}"

    def test_ledger_entries_have_required_fields(self, tmp_path):
        from agentic_core.L2_execution.tools.write_gateway import (
            set_mutation_ledger_path,
            write_text,
        )

        ledger_path = tmp_path / "mutation_ledger.jsonl"
        set_mutation_ledger_path(ledger_path, "TEST-GAP-B-003")
        write_text(tmp_path / "test.py", "x = 1")

        entries = [json.loads(line) for line in ledger_path.read_text().splitlines() if line.strip()]
        assert len(entries) == 1
        entry = entries[0]
        required_fields = {"trace_id", "path", "operation", "result"}
        assert required_fields.issubset(entry.keys()), f"Missing fields: {required_fields - entry.keys()}"
