"""
Phase 2A evidence runner — Python-only, shell=False, no PowerShell.

Writes evidence to: docs/reports/plans/phase_02a_lic_spine_adapter.md
"""

from __future__ import annotations

import subprocess
import sys

from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "phase02a_lic_spine_adapter_evidence_runner")
_emit_applies_guardrail("p0", "phase02a_lic_spine_adapter_evidence_runner", "p0_governance")
_emit_reads_policy_state("p0", "phase02a_lic_spine_adapter_evidence_runner", "policy_binding")
_emit_snapshots_state("p0", "phase02a_lic_spine_adapter_evidence_runner", "state_snapshot")
emit_replay_key("p0", "phase02a_lic_spine_adapter_evidence_runner")
emit_determinism_digest("p0", "phase02a_lic_spine_adapter_evidence_runner")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

PROJECT_ROOT = get_validated_project_root()
EVIDENCE_PATH = PROJECT_ROOT / "docs" / REPORTS_DIR / "plans" / "phase_02a_lic_spine_adapter.md"
ADAPTER_FILE = PROJECT_ROOT / APPS_LIC_DIR / "engines" / "lic_spine_adapter.py"
TEST_FILE = PROJECT_ROOT / TESTS_DIR / "unit_min_deps" / "test_apps_lic_spine_adapter.py"


def run(argv: list[str]) -> tuple[int, str]:
    result = subprocess.run(argv, cwd=str(PROJECT_ROOT), capture_output=True, shell=False)
    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    combined = stdout + stderr
    stderr_lines = [line for line in stderr.splitlines() if not line.strip().startswith("PS ")]
    stderr_check = "\n".join(stderr_lines)
    if "pwsh" in stderr_check.lower() or "powershell" in stderr_check.lower():
        print("ABORT: PowerShell detected in stderr output.", file=sys.stderr)
        sys.exit(1)
    return result.returncode, combined


def section(title: str, content: str) -> str:
    return "## " + title + "\n\n```\n" + content.strip() + "\n```\n\n"


def main() -> None:
    nl = "\n"

    print("Running focused pytest...")
    focused_rc, focused_out = run(
        [sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/test_apps_lic_spine_adapter.py"]
    )

    print("Running full suite...")
    full_rc, full_out = run([sys.executable, "-m", "pytest", "-q"])

    print("Running git diff --stat...")
    stat_rc, stat_out = run(["git", "diff", "--stat"])

    print("Running git diff...")
    diff_rc, diff_out = run(["git", "diff"])

    adapter_content = ADAPTER_FILE.read_text(encoding="utf-8")
    test_content = TEST_FILE.read_text(encoding="utf-8")

    sec_focused = section(
        "Command: python -m pytest -q tests/unit_min_deps/test_apps_lic_spine_adapter.py",
        "Exit code: " + str(focused_rc) + nl + nl + focused_out,
    )
    sec_full = section(
        "Command: python -m pytest -q (full suite)",
        "Exit code: " + str(full_rc) + nl + nl + full_out,
    )
    sec_stat = section(
        "Command: git diff --stat",
        "Exit code: " + str(stat_rc) + nl + nl + stat_out,
    )
    sec_diff = section(
        "Command: git diff",
        "Exit code: " + str(diff_rc) + nl + nl + diff_out,
    )

    parts = [
        "# Phase 2A: LIC Spine Adapter + CID Binding — Evidence",
        "",
        "Pure-wiring adapter forcing all LIC entry through the canonical spine "
        "(AirlockAssembler → PathRouter → ExecutionOrchestrator) with deterministic "
        "CID derived from GovernedPayload manifest hash before any HOP stage runs.",
        "",
        "## Commit Hash",
        "",
        "PENDING",
        "",
        "## Files Changed",
        "",
        "- `apps_lic/engines/lic_spine_adapter.py` (created)",
        "- `apps_lic/engines/__init__.py` (fixed broken eager imports)",
        "- `apps_lic/engines/ExecutiveStrategyAgent.py` (shim created)",
        "- `apps_lic/engines/HOPPipelineExecutor.py` (shim created)",
        "- `apps_lic/engines/LICValidationExecutor.py` (shim created)",
        "- `apps_lic/engines/OutreachMessageAgent.py` (shim created)",
        "- `tests/unit_min_deps/test_apps_lic_spine_adapter.py` (created)",
        "- `tools/evidence/phase02a_lic_spine_adapter_evidence_runner.py` (created)",
        "- `docs/reports/plans/phase_02a_lic_spine_adapter.md` (created)",
        "",
        sec_focused,
        sec_full,
        sec_stat,
        sec_diff,
        "## apps_lic/engines/lic_spine_adapter.py (verbatim)",
        "",
        "```python",
        adapter_content,
        "```",
        "",
        "## tests/unit_min_deps/test_apps_lic_spine_adapter.py (verbatim)",
        "",
        "```python",
        test_content,
        "```",
        "",
    ]
    md = nl.join(parts)
    md = "\n".join(line.rstrip() for line in md.splitlines()) + "\n"
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_bytes(md.encode("utf-8"))
    print("Evidence written to: " + str(EVIDENCE_PATH))

    if focused_rc != 0:
        print("FAIL: focused pytest returned non-zero.", file=sys.stderr)
        sys.exit(focused_rc)


if __name__ == "__main__":
    main()
