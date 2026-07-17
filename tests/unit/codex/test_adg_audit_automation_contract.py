from __future__ import annotations

import runpy
from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[3]
AUTOMATION_TOML = REPO_ROOT / ".codex" / "automations" / "adg-audit-and-burndown" / "automation.toml"
GENERATOR = REPO_ROOT / "tools" / "generate" / "generate_full_adg.py"
WRAPPER = REPO_ROOT / "tools" / "adg" / "run_full_adg_audit.py"
OUTPUT_BUNDLE = REPO_ROOT / "tools" / "reports" / "adg_run_output_bundle.py"
INLINE_AUDIT = REPO_ROOT / ".codex" / "governance" / "scripts" / "post_agent_adg_burndown_inline_audit.py"


def _evaluate_inline_audit(text: str) -> tuple[str, str]:
    evaluate = runpy.run_path(str(INLINE_AUDIT))["evaluate"]
    return evaluate(text)


def _complete_adg_response() -> str:
    return "\n".join(
        (
            "python tools/generate/generate_full_adg.py",
            "ADG generation complete",
            "## ADG Executive Brief",
            "### Impact Inventory",
            "Decision gate: PASS",
            "Fix now: none",
            "## Final disposition",
            "- **Process exit code:** `0`",
        )
    )


def test_adg_audit_automation_requires_one_sealed_terminal_bundle() -> None:
    payload = tomllib.loads(AUTOMATION_TOML.read_text(encoding="utf-8"))
    prompt = payload["prompt"]

    assert "Sealed terminal-output contract:" in prompt
    assert (
        "Render exactly one inline report, `## ADG Executive Brief`, after generator and "
        "wrapper certification gates finish."
    ) in prompt
    assert (
        "The brief must include the decision-gate/FIX view, P0-P3 impact inventory, and "
        "final process disposition."
    ) in prompt
    assert (
        "The standalone burndown remains a timestamped, digest-inventoried artifact; never "
        "replay it as a second inline report."
    ) in prompt
    assert (
        "Direct generation and wrapper fallback must use the same snapshot-bound "
        "output-bundle orchestrator. Missing, stale, mixed-run, or duplicate output is incomplete."
    ) in prompt


def test_adg_audit_automation_releases_digest_bound_handoff_pointer() -> None:
    payload = tomllib.loads(AUTOMATION_TOML.read_text(encoding="utf-8"))
    handoff = payload["handoff"]
    prompt = payload["prompt"]

    pointer_path = (
        handoff["producer_repo_root"].rstrip("\\/")
        + "\\artifacts\\adg\\handoffs\\adg_repair_handoff_latest.json"
    )
    validator = f"python tools/adg/consume_adg_repair_handoff.py --handoff-pointer {pointer_path} --json"

    assert handoff["handoff_pointer_path"] == pointer_path
    assert handoff["validator"] == validator
    assert handoff["requires_digest_bound_handoff_pointer"] is True
    assert "adg-repair-handoff-pointer/v1" in prompt
    assert "immutable adg_repair_handoff_<run_id>.json" in prompt
    assert "downstream_release_status=released" in prompt


def test_adg_audit_contract_paths_share_one_snapshot_bound_bundle() -> None:
    payload = tomllib.loads(AUTOMATION_TOML.read_text(encoding="utf-8"))
    prompt = payload["prompt"]
    generator_source = GENERATOR.read_text(encoding="utf-8")
    wrapper_source = WRAPPER.read_text(encoding="utf-8")
    bundle_source = OUTPUT_BUNDLE.read_text(encoding="utf-8")

    assert "Direct generation and wrapper fallback" in prompt
    assert generator_source.count("emit_adg_run_output_bundle(") == 2
    assert wrapper_source.count("emit_adg_run_output_bundle(") == 1
    assert "print_adg_run_terminal_summary(" in generator_source
    assert "print_adg_run_terminal_summary(" in wrapper_source
    # Both paths freeze the digest-bound terminal with printing suppressed
    # before exactly one final render. Counting helper calls is intentionally
    # avoided because early-failure sealing adds a mutually exclusive call.
    assert "print_terminal=False" in generator_source
    assert "print_terminal=False" in wrapper_source

    for source in (generator_source, wrapper_source):
        assert "emit_bcg_executive_summary(" not in source
        assert "emit_existing_burndown_markdown(" not in source

    assert "validate_existing_adg_run_output_bundle(" in wrapper_source
    assert "load_existing_adg_run_output_bundle(" in wrapper_source
    assert wrapper_source.index("_write_receipt(result") < wrapper_source.rindex(
        "print_adg_run_terminal_summary("
    )
    assert generator_source.index("emit_adg_run_output_bundle(") < generator_source.index(
        "print_adg_run_terminal_summary("
    )
    assert '"terminal_output_count": 1' in bundle_source
    assert '"## ADG Executive Brief"' in bundle_source


def test_adg_inline_audit_accepts_one_finalized_sealed_brief() -> None:
    verdict, reason = _evaluate_inline_audit(_complete_adg_response())

    assert verdict == "ALLOW"
    assert "final disposition" in reason


def test_adg_inline_audit_rejects_missing_or_duplicate_final_disposition() -> None:
    complete = _complete_adg_response()
    without_disposition = complete.split("\n## Final disposition", 1)[0]
    verdict, reason = _evaluate_inline_audit(without_disposition)

    assert verdict == "VIOLATION"
    assert "exactly one final disposition (found 0)" in reason
    assert "exactly one process exit code (found 0)" in reason

    verdict, reason = _evaluate_inline_audit(
        complete + "\n## Final disposition\n\n- **Process exit code:** `0`"
    )
    assert verdict == "VIOLATION"
    assert "exactly one final disposition (found 2)" in reason
    assert "exactly one process exit code (found 2)" in reason


def test_adg_inline_audit_rejects_standalone_burndown_replay() -> None:
    verdict, reason = _evaluate_inline_audit(
        _complete_adg_response() + "\n# ADG CI Burndown Report\n\n| Gate ID | Status |"
    )

    assert verdict == "VIOLATION"
    assert "no standalone burndown replay (found 1)" in reason


def test_adg_inline_audit_does_not_require_terminal_output_for_dispatcher_only() -> None:
    verdict, reason = _evaluate_inline_audit(
        "python ops_scripts/ci/adg_gates/run.py --json-only\nADG complete\nexit code 0"
    )

    assert verdict == "NOT_APPLICABLE"
    assert "no ADG generate/audit run" in reason
