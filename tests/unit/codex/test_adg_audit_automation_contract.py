from __future__ import annotations

from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[3]
AUTOMATION_TOML = (
    REPO_ROOT
    / ".codex"
    / "automations"
    / "adg-audit-and-burndown"
    / "automation.toml"
)
GENERATOR = REPO_ROOT / "tools" / "generate" / "generate_full_adg.py"
WRAPPER = REPO_ROOT / "tools" / "adg" / "run_full_adg_audit.py"


def test_adg_audit_automation_requires_bcg_before_burndown_inline() -> None:
    payload = tomllib.loads(AUTOMATION_TOML.read_text(encoding="utf-8"))
    prompt = payload["prompt"]

    assert "Inline report order contract:" in prompt
    assert "The first inline report is mandatory and must be the BCG RCA / executive summary." in prompt
    assert "The second inline report must be the ADG burndown report." in prompt
    assert (
        "This ordering must hold across the primary generator path, finalize/recovery path, "
        "and wrapper fallback path."
    ) in prompt
    assert (
        "If the run cannot emit BCG first and burndown second, report contract drift or "
        "incomplete output instead of silently changing order."
    ) in prompt


def test_adg_audit_automation_releases_digest_bound_handoff_pointer() -> None:
    payload = tomllib.loads(AUTOMATION_TOML.read_text(encoding="utf-8"))
    handoff = payload["handoff"]
    prompt = payload["prompt"]

    pointer_path = "artifacts/adg/handoffs/adg_repair_handoff_latest.json"
    validator = (
        "python tools/adg/consume_adg_repair_handoff.py "
        "--handoff-pointer artifacts/adg/handoffs/adg_repair_handoff_latest.json --json"
    )

    assert handoff["handoff_pointer_path"] == pointer_path
    assert handoff["validator"] == validator
    assert handoff["requires_digest_bound_handoff_pointer"] is True
    assert "adg-repair-handoff-pointer/v1" in prompt
    assert "immutable adg_repair_handoff_<run_id>.json" in prompt
    assert "downstream_release_status=released" in prompt


def test_adg_audit_contract_paths_match_runtime_ordering_helpers() -> None:
    payload = tomllib.loads(AUTOMATION_TOML.read_text(encoding="utf-8"))
    prompt = payload["prompt"]
    generator_source = GENERATOR.read_text(encoding="utf-8")
    wrapper_source = WRAPPER.read_text(encoding="utf-8")

    for path_label in (
        "primary generator path",
        "finalize/recovery path",
        "wrapper fallback path",
    ):
        assert path_label in prompt

    primary_materialize = generator_source.index(
        "_burndown_emit_rc = emit_mandatory_adg_burndown_report(\n"
        "        burndown=adg_artifacts_dir / \"adg_burndown_table.json\",\n"
        "        fail_closed=False,\n"
        "        print_inline=False,"
    )
    primary_bcg = generator_source.index(
        "_bcg_rc, bcg_summary_path = emit_bcg_executive_summary(",
        primary_materialize,
    )
    primary_inline = generator_source.index(
        "_burndown_inline_rc = emit_existing_burndown_markdown()",
        primary_bcg,
    )
    assert primary_materialize < primary_bcg < primary_inline

    recovery_materialize = generator_source.index(
        "_burndown_emit_rc = emit_mandatory_adg_burndown_report(\n"
        "                fail_closed=False,\n"
        "                print_inline=False,",
        primary_inline,
    )
    recovery_bcg = generator_source.index("emit_bcg_executive_summary(", recovery_materialize)
    recovery_inline = generator_source.index("emit_existing_burndown_markdown()", recovery_bcg)
    assert recovery_materialize < recovery_bcg < recovery_inline

    wrapper_bcg = wrapper_source.index("bcg_rc, _bcg_path = emit_bcg_executive_summary(")
    wrapper_materialize = wrapper_source.index(
        "burndown_rc = emit_mandatory_adg_burndown_report(",
        wrapper_bcg,
    )
    wrapper_inline = wrapper_source.index("emit_existing_burndown_markdown()", wrapper_materialize)
    assert wrapper_bcg < wrapper_materialize < wrapper_inline
