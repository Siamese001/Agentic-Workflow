"""
test_ci_hardening_2026_05_05.py — Acceptance tests for the 2026-05-05 CI hardening pass.

Proves:
  1. No duplicate gate invocation in the same run_contract_gates plane.
  2. Stale Windsurf hooks.json working_directory paths fail the schema gate.
  3. Correct repo-root hooks.json working_directory passes the schema gate.
  4. Freshness gate CF1 (ADG-first violations) logic is correct.
  5. Runtime-certification is no longer in pre-commit default stages.
  6. HITL corpus trigger regex covers all four validator-owned files.
  7. Author-gate ledger schema trigger includes the DDL file.
  8. Intentional two-lane gates (snapshot-has-mvs, pipeline-skips) remain in pre-commit.
  9. Promoted manual gates (OTEL, spans, purity, PII) are in run_contract_gates assurance plane.
"""
from __future__ import annotations

import ast
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
PRECOMMIT = REPO_ROOT / ".pre-commit-config.yaml"
GATES_PY = REPO_ROOT / "ops_scripts" / "ci" / "run_contract_gates.py"
HOOKS_JSON = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "hooks.json"

# ---------------------------------------------------------------------------
# Helper: parse run_contract_gates.py for all script references per plane
# ---------------------------------------------------------------------------

def _plane_scripts(plane_name: str) -> list[str]:
    """Extract the list of script paths from a named gate plane in run_contract_gates.py.

    Uses bracket-counting to handle `]` appearing inside comment strings within
    the list literal (e.g. ``stages: [manual]`` in comments).
    """
    source = GATES_PY.read_text(encoding="utf-8")
    header_re = re.compile(r"\b" + re.escape(plane_name) + r"\s*=\s*\[")
    m = header_re.search(source)
    if not m:
        return []
    start = m.end()  # position just after the opening `[`
    depth = 1
    i = start
    while i < len(source) and depth > 0:
        ch = source[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        elif ch == "#":
            # skip to end of line — comments may contain [] that confuse bracket counting
            while i < len(source) and source[i] != "\n":
                i += 1
            continue
        elif ch in ('"', "'"):
            # skip string literal — its contents must not affect bracket counting
            quote = ch
            i += 1
            while i < len(source):
                if source[i] == "\\" :
                    i += 2
                    continue
                if source[i] == quote:
                    break
                i += 1
        i += 1
    block = source[start : i - 1]
    # Extract all string literals that look like script paths (contain '/')
    script_re = re.compile(r'"(ops_scripts/ci/[^"]+\.py|scripts/[^"]+\.py|tools/[^"]+\.py)"')
    return script_re.findall(block)


# ---------------------------------------------------------------------------
# 1. No duplicate gate invocation in the same plane
# ---------------------------------------------------------------------------

class TestNoDuplicateGatesInSamePlane:
    def test_assurance_gates_no_duplicates(self) -> None:
        scripts = _plane_scripts("assurance_gates")
        seen: set[str] = set()
        for s in scripts:
            assert s not in seen, (
                f"Duplicate gate in assurance_gates: {s!r}. "
                "Remove the second invocation from the same CI plane."
            )
            seen.add(s)

    def test_wiring_gates_no_duplicates(self) -> None:
        scripts = _plane_scripts("wiring_gates")
        seen: set[str] = set()
        for s in scripts:
            assert s not in seen, (
                f"Duplicate gate in wiring_gates: {s!r}. "
                "Remove the second invocation from the same CI plane."
            )
            seen.add(s)

    def test_windsurf_schema_gate_in_wiring_only(self) -> None:
        """check_windsurf_config_schema.py must appear in wiring_gates ONLY (canonical home)."""
        assurance = _plane_scripts("assurance_gates")
        wiring = _plane_scripts("wiring_gates")
        target = "ops_scripts/ci/check_windsurf_config_schema.py"
        assert target not in assurance, (
            f"{target} must not be in assurance_gates — wiring_gates is canonical."
        )
        assert target in wiring, (
            f"{target} must be present in wiring_gates."
        )


# ---------------------------------------------------------------------------
# 2 & 3. Windsurf working_directory validation (schema gate extension)
# ---------------------------------------------------------------------------

SCHEMA_GATE = REPO_ROOT / "ops_scripts" / "ci" / "check_windsurf_config_schema.py"


def _run_schema_gate(tmp_repo: Path, hooks_data: dict) -> tuple[int, str, str]:
    import subprocess
    # Copy the schema gate into the tmp repo so ROOT resolves correctly
    import shutil
    gate_dest_dir = tmp_repo / "ops_scripts" / "ci"
    gate_dest_dir.mkdir(parents=True, exist_ok=True)
    gate_dest = gate_dest_dir / SCHEMA_GATE.name
    shutil.copy2(SCHEMA_GATE, gate_dest)
    (tmp_repo / "docs/archive/windsurf/legacy-tree").mkdir(parents=True, exist_ok=True)
    (tmp_repo / "docs/archive/windsurf/legacy-tree" / "hooks.json").write_text(
        json.dumps({"hooks": hooks_data}, indent=2), encoding="utf-8"
    )
    (tmp_repo / "docs/archive/windsurf/legacy-tree" / "mcp_config.json").write_text(
        json.dumps({"mcpServers": {}}, indent=2), encoding="utf-8"
    )
    result = subprocess.run(
        [sys.executable, str(gate_dest)],
        capture_output=True, text=True, cwd=str(tmp_repo), timeout=30, check=False,
    )
    return result.returncode, result.stdout, result.stderr


class TestWorkingDirectoryValidation:
    def test_stale_absolute_path_fails(self, tmp_path: Path) -> None:
        """A hooks.json entry pointing to a nonexistent absolute path fails the gate."""
        stale_path = "C:\\Git\\Agentic-Workflow"  # stale clone — does not match tmp_path
        hooks = {
            "post_cursor_agent_response": [
                {"command": "python script.py", "working_directory": stale_path, "show_output": False}
            ]
        }
        rc, stdout, stderr = _run_schema_gate(tmp_path, hooks)
        assert rc != 0, (
            f"Gate must reject stale working_directory '{stale_path}'; stdout={stdout!r}"
        )
        assert "working_directory" in (stdout + stderr), "Violation message must mention working_directory"

    def test_repo_root_aligned_path_passes(self, tmp_path: Path) -> None:
        """A hooks.json entry with working_directory pointing to the tmp repo root passes."""
        hooks = {
            "post_cursor_agent_response": [
                {
                    "command": "python script.py",
                    "working_directory": str(tmp_path),
                    "show_output": False,
                }
            ]
        }
        rc, stdout, stderr = _run_schema_gate(tmp_path, hooks)
        assert rc == 0, (
            f"Gate must accept working_directory matching repo root; stdout={stdout!r} stderr={stderr!r}"
        )

    def test_relative_path_passes(self, tmp_path: Path) -> None:
        """A relative working_directory is always acceptable (resolved by Windsurf against workspace)."""
        hooks = {
            "post_cursor_agent_response": [
                {"command": "python script.py", "working_directory": ".", "show_output": False}
            ]
        }
        rc, _stdout, _stderr = _run_schema_gate(tmp_path, hooks)
        assert rc == 0, "Relative working_directory must pass."

    def test_local_only_waiver_skips_path_check(self, tmp_path: Path) -> None:
        """An entry with _local_only_waiver: true is exempt from absolute path validation."""
        stale_path = "C:\\Git\\Agentic-Workflow"
        hooks = {
            "post_cursor_agent_response": [
                {
                    "command": "python script.py",
                    "working_directory": stale_path,
                    "show_output": False,
                    "_local_only_waiver": True,
                }
            ]
        }
        rc, stdout, stderr = _run_schema_gate(tmp_path, hooks)
        assert rc == 0, (
            f"Entry with _local_only_waiver must pass path check; stdout={stdout!r}"
        )

    def test_live_hooks_json_passes(self) -> None:
        """The live repo hooks.json must pass the schema gate (post H20 fix)."""
        import subprocess
        result = subprocess.run(
            [sys.executable, str(SCHEMA_GATE)],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, check=False,
        )
        assert result.returncode == 0, (
            f"Live hooks.json must pass §26 gate; stdout={result.stdout!r} stderr={result.stderr!r}"
        )


# ---------------------------------------------------------------------------
# 4. CF1 — ADG-first violations freshness gate (pure evaluate() function)
# ---------------------------------------------------------------------------

sys.path.insert(0, str(REPO_ROOT / "ops_scripts" / "ci"))
from check_adg_first_violations_freshness import evaluate as adg_evaluate  # type: ignore[import]


class TestAdgFirstViolationsFreshness:
    def _ts(self, *, days_ago: int = 0) -> str:
        dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
        return dt.isoformat()

    def test_empty_rows_passes(self) -> None:
        assert adg_evaluate([], 7) == []

    def test_bypass_row_ignored(self) -> None:
        rows = [{"reason": "bypass", "ts": self._ts(days_ago=1)}]
        assert adg_evaluate(rows, 7) == []

    def test_resolved_row_ignored(self) -> None:
        rows = [{"resolved": True, "ts": self._ts(days_ago=1)}]
        assert adg_evaluate(rows, 7) == []

    def test_fresh_unresolved_fails(self) -> None:
        rows = [{"severity": "critical", "ts": self._ts(days_ago=1)}]
        result = adg_evaluate(rows, 7)
        assert len(result) == 1

    def test_aged_out_row_passes(self) -> None:
        rows = [{"severity": "critical", "ts": self._ts(days_ago=10)}]
        assert adg_evaluate(rows, 7) == []

    def test_row_without_ts_treated_as_unresolved(self) -> None:
        rows = [{"severity": "critical"}]
        result = adg_evaluate(rows, 7)
        assert len(result) == 1


# ---------------------------------------------------------------------------
# 5. runtime-certification is manual-only in pre-commit
# ---------------------------------------------------------------------------

class TestRuntimeCertificationStage:
    def test_runtime_cert_not_in_default_precommit_stage(self) -> None:
        content = PRECOMMIT.read_text(encoding="utf-8")
        # Find the runtime-certification hook block
        m = re.search(r"id:\s*runtime-certification.*?(?=\n\s*-\s*id:|\Z)", content, re.DOTALL)
        assert m, "runtime-certification hook not found in .pre-commit-config.yaml"
        block = m.group(0)
        # stages must be present and must not include 'pre-commit'
        stages_m = re.search(r"stages:\s*\[([^\]]+)\]", block)
        assert stages_m, "runtime-certification hook must have an explicit stages: field"
        stages = [s.strip() for s in stages_m.group(1).split(",")]
        assert "pre-commit" not in stages, (
            f"runtime-certification must not be in default pre-commit stage. "
            f"Current stages: {stages}. CI wiring_gates is the authoritative sweep."
        )
        assert "manual" in stages, "runtime-certification must retain 'manual' stage for on-demand use"


# ---------------------------------------------------------------------------
# 7. HITL corpus trigger regex covers all four validator-owned files
# ---------------------------------------------------------------------------

class TestHitlCorpusTriggerRegex:
    def _get_hitl_corpus_files_pattern(self) -> str:
        content = PRECOMMIT.read_text(encoding="utf-8")
        # Find the hitl-rules-corpus block
        m = re.search(r"id:\s*hitl-rules-corpus.*?(?=\n\s*-\s*id:|\Z)", content, re.DOTALL)
        assert m, "hitl-rules-corpus hook not found"
        block = m.group(0)
        fm = re.search(r"files:\s*(\S+)", block)
        assert fm, "hitl-rules-corpus must have a files: pattern"
        return fm.group(1)

    @pytest.mark.parametrize("filename", [
        "author-gate-enforcement.md",
        "author-gate-decision-points.md",
        "author-gate-svp-calibration.md",
        "anti-pattern-author-gate.md",
    ])
    def test_corpus_file_matches_trigger(self, filename: str) -> None:
        pattern = self._get_hitl_corpus_files_pattern()
        path = f".claude/rules/{filename}"
        assert re.search(pattern, path), (
            f"HITL corpus trigger regex {pattern!r} does not match {path!r}. "
            "Edits to this file would silently skip the corpus validator."
        )


# ---------------------------------------------------------------------------
# 8. Author-gate ledger schema trigger includes the DDL file
# ---------------------------------------------------------------------------

class TestLedgerSchemaTrigger:
    def test_ddl_file_in_trigger(self) -> None:
        content = PRECOMMIT.read_text(encoding="utf-8")
        m = re.search(r"id:\s*author-gate-ledger-schema.*?(?=\n\s*-\s*id:|\Z)", content, re.DOTALL)
        assert m, "author-gate-ledger-schema hook not found"
        block = m.group(0)
        fm = re.search(r"files:\s*(\S+)", block)
        assert fm, "author-gate-ledger-schema must have a files: pattern"
        pattern = fm.group(1)
        ddl_path = ".cursor/schemas/decision_ledger.schema.sql"
        assert re.search(pattern, ddl_path), (
            f"Trigger regex {pattern!r} does not match DDL file {ddl_path!r}. "
            "Changes to the DDL alone would silently skip the schema validator."
        )


# ---------------------------------------------------------------------------
# 9. Intentional two-lane gates remain in pre-commit
# ---------------------------------------------------------------------------

TWO_LANE_IDS = [
    "snapshot-has-mvs",
    "pipeline-skips",
    "skill-frontmatter",
    "wiring-waiver-expiry",
    "author-gate-ledger-schema",
]


class TestIntentionalTwoLaneCoverage:
    @pytest.mark.parametrize("hook_id", TWO_LANE_IDS)
    def test_hook_still_in_precommit(self, hook_id: str) -> None:
        content = PRECOMMIT.read_text(encoding="utf-8")
        assert f"id: {hook_id}" in content, (
            f"Hook '{hook_id}' was removed from .pre-commit-config.yaml. "
            "This is an intentional two-lane coverage gate — pre-commit provides "
            "changed-file protection; CI provides the authoritative full-repo sweep. "
            "Restore the pre-commit entry."
        )


# ---------------------------------------------------------------------------
# 10. Promoted manual gates are in run_contract_gates assurance plane
# ---------------------------------------------------------------------------

PROMOTED_SCRIPTS = [
    "ops_scripts/ci/check_apps_otel_coverage.py",
    "ops_scripts/ci/check_required_spans_coverage.py",
    "ops_scripts/ci/check_apps_shared_purity.py",
    "ops_scripts/ci/check_pii_in_telemetry.py",
    "ops_scripts/ci/check_adg_first_violations_freshness.py",
]


class TestPromotedGatesInCI:
    @pytest.mark.parametrize("script", PROMOTED_SCRIPTS)
    def test_script_in_assurance_gates(self, script: str) -> None:
        assurance = _plane_scripts("assurance_gates")
        assert script in assurance, (
            f"Expected {script!r} in run_contract_gates.py assurance_gates but it was not found. "
            "This gate was promoted from manual-only pre-commit to CI authoritative sweep on 2026-05-05."
        )
