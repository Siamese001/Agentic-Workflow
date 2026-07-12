"""Run the canonical apps_research -> briefing.md -> apps_rg U0 proof.

The GitHub workflow calls this checked-in runner instead of embedding a long
list of pytest paths. This keeps workflow-reference validation deterministic
while preserving one authoritative test command for local and CI execution.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "artifacts" / "apps_research_rg_handoff"
_COMMAND_TIMEOUT_SECONDS = 600


def _run(args: list[str]) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(
        args,
        cwd=ROOT,
        check=True,
        shell=False,
        timeout=_COMMAND_TIMEOUT_SECONDS,
    )


def _enforce_source_structure() -> None:
    producer = (
        ROOT / "apps_research" / "integrations" / "apps_rg_handoff.py"
    ).read_text(encoding="utf-8")
    consumer = (
        ROOT / "apps_rg" / "prerequisites" / "briefing_validator.py"
    ).read_text(encoding="utf-8")
    u0_signal = (
        ROOT / "apps_rg" / "runtime" / "bindings" / "briefing_u0_signals.py"
    ).read_text(encoding="utf-8")

    required_fragments = (
        "exit_bind_and_finalize_apps_research(",
        "if not authorization.allows_finish:",
        '"canonical_exit_authorized": True',
        '"x3_code": receipt.x3_code',
        '"canonical_x3_code": receipt.x3_code',
    )
    missing = [fragment for fragment in required_fragments if fragment not in producer]
    if missing:
        raise AssertionError(f"producer authority fragments missing: {missing}")
    if producer.index("if not authorization.allows_finish:") >= producer.index(
        "run_dir.mkdir("
    ):
        raise AssertionError("producer creates the run directory before canonical Exit ALLOW")
    if '"reason": "model_backed_x2_passed"' in producer:
        raise AssertionError("application-local X3 authorization remains in producer")
    if "validate_canonical_apps_research_exit" not in consumer:
        raise AssertionError("consumer does not validate canonical producer Exit proof")
    if "require_canonical_exit=True" not in u0_signal:
        raise AssertionError("apps_rg U0 does not require canonical Exit for auto research")


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    _run(
        [
            sys.executable,
            "-m",
            "py_compile",
            "apps_research/integrations/apps_rg_handoff.py",
            "apps_rg/prerequisites/apps_research_exit_validator.py",
            "apps_rg/prerequisites/briefing_validator.py",
            "apps_rg/runtime/bindings/briefing_u0_signals.py",
            "tests/unit/apps_research/test_apps_rg_handoff_canonical_exit.py",
        ]
    )
    _enforce_source_structure()

    _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/apps_research/test_apps_rg_handoff_canonical_exit.py",
            "tests/e2e/apps_rg/test_apps_research_handoff_runtime_gates.py",
            "tests/unit/apps_research/test_cli_apps_rg_targeting_brief.py",
            "tests/unit/apps_rg/test_apps_research_bridge_contract_gate.py",
            "tests/unit/apps_rg/test_apps_research_bridge_u0_handoff.py",
            "-q",
            "--tb=short",
            "--no-header",
            "-p",
            "no:cacheprovider",
            f"--junitxml={EVIDENCE_DIR / 'canonical-tests.xml'}",
        ]
    )

    selection = (
        "research_enabled_when_brief_missing_and_auto_research_on or "
        "no_delegation_when_auto_research_disabled_and_brief_present or "
        "auto_research_static_brief_requires_delegation or "
        "auto_research_authorized_handoff_skips_delegation or "
        "whole_run_research_failure_fails_closed_with_manual_brief or "
        "whole_run_u0_rejection_emits_terminal_closeout or "
        "research_hop_rejects_ready_result_without_producer_artifact or "
        "whole_run_route_mismatch_fails_closed_when_apps_research_required"
    )
    _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/apps_rg/test_r3r4_whole_run_reachability.py",
            "-k",
            selection,
            "-q",
            "--tb=short",
            "--no-header",
            "-p",
            "no:cacheprovider",
            f"--junitxml={EVIDENCE_DIR / 'whole-run-tests.xml'}",
        ]
    )

    print(
        "apps_research -> briefing.md -> apps_rg U0 canonical handoff proof: PASS",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
