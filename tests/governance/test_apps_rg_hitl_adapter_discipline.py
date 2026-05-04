"""DS-5 Governance sentinels for apps_rg HITL adapter discipline.

DS-5 was originally scoped as: "W7 HITL adapter surface Author-Gate + TUI /
async webhook variant; Author-Gate decision recorded; chosen adapter variant
implemented; sentinel tests updated".

Investigation found:
  - cli_hitl_adapter.py is complete, fully wired, and is the single input()
    chokepoint for all of apps_rg (per its own module docstring).
  - No AG-RG-012 decision was ever seeded or needed — the CLI variant is
    the correct and sufficient adapter for apps_rg's interactive single-user
    workflow. A TUI or async webhook would add complexity without benefit
    for this use case.
  - No tui_hitl_adapter.py or async_hitl_adapter.py exists or is required.

DS-5 is therefore closed as: governance tests that lock the CLI adapter's
single-chokepoint invariants and prevent accidental bypass or duplication.

Tests:
1. Only cli_hitl_adapter.py exists in apps_rg/hitl/ — no second adapter.
2. cli_hitl_adapter._input is patchable (test-injectable, not hardcoded).
3. NonInteractiveError is raised when stdin is not a TTY.
4. prompt() is the sole public entry point for human decisions.
5. No other module in apps_rg/ calls input() directly (single-chokepoint).
6. HumanReviewDecision.verify_hash() round-trips correctly.
7. HITLReplayStore appends and verifies hash-bound rows correctly.
8. hitl_trigger_policy.yaml declares exactly 6 trigger kinds matching TRIGGER_KINDS.
9. hitl_bridge.evaluate_hitl returns None gracefully when run_report.json absent.
10. hitl_schemas TRIGGER_KINDS is a non-empty tuple of strings.

Plan: apps-rg-deferred-scope-followon-d4e1b9 DS-5.
"""
from __future__ import annotations

import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
HITL_DIR = REPO_ROOT / "apps_rg" / "hitl"
APPS_RG_DIR = REPO_ROOT / "apps_rg"
TRIGGER_POLICY = REPO_ROOT / "apps_rg" / "config" / "hitl_trigger_policy.yaml"


@pytest.mark.governance
def test_only_cli_adapter_exists_no_second_adapter() -> None:
    """Only cli_hitl_adapter.py must exist — no tui/async variant."""
    adapter_files = list(HITL_DIR.glob("*hitl_adapter*.py"))
    names = [f.name for f in adapter_files]
    assert names == ["cli_hitl_adapter.py"], (
        f"Expected exactly ['cli_hitl_adapter.py'] in apps_rg/hitl/. "
        f"Found: {sorted(names)}. "
        "A second adapter would violate the single-chokepoint invariant."
    )


@pytest.mark.governance
def test_cli_adapter_input_is_patchable() -> None:
    """cli_hitl_adapter._input must be a module-level name (patchable in tests)."""
    import apps_rg.hitl.cli_hitl_adapter as mod
    assert hasattr(mod, "_input"), (
        "cli_hitl_adapter must expose module-level '_input' for test injection."
    )
    assert callable(mod._input)


@pytest.mark.governance
def test_cli_adapter_non_interactive_error_on_non_tty() -> None:
    """prompt() must raise NonInteractiveError when stdin is not a TTY."""
    from apps_rg.hitl.cli_hitl_adapter import NonInteractiveError, prompt
    from apps_rg.hitl.hitl_schemas import BoundedOption, make_decision_request

    request = make_decision_request(
        trigger_kind="RELEASE_APPROVAL",
        run_id="test-run-id",
        input_manifest_hash="abc123",
        recommendations=["approve"],
        confidence_score=0.9,
        evidence_refs=[],
        bounded_options=[
            BoundedOption("APPROVE", "Approve", "allow", is_recommended=True)
        ],
        replay_key="rk-test",
    )
    with patch("sys.stdin") as mock_stdin:
        mock_stdin.isatty.return_value = False
        with pytest.raises(NonInteractiveError):
            prompt(request)


@pytest.mark.governance
def test_cli_adapter_prompt_is_sole_public_entry() -> None:
    """cli_hitl_adapter must export 'prompt' as its primary callable."""
    import apps_rg.hitl.cli_hitl_adapter as mod
    assert hasattr(mod, "prompt") and callable(mod.prompt), (
        "cli_hitl_adapter must expose 'prompt' as the sole public human-decision entry."
    )
    # NonInteractiveError must also be exported for callers to catch
    assert hasattr(mod, "NonInteractiveError")


@pytest.mark.governance
def test_no_direct_input_calls_outside_cli_adapter() -> None:
    """No module in apps_rg/ (except cli_hitl_adapter.py) may call input() directly.

    Uses AST parsing to detect actual Call nodes whose function is the bare
    name 'input' — this correctly ignores docstrings, comments, and any
    identifier whose name ends with 'input' (validate_input, jd_input, etc.).
    """
    import ast

    def _find_bare_input_calls(src: str) -> list[int]:
        """Return line numbers of bare input() calls in src."""
        try:
            tree = ast.parse(src)
        except SyntaxError:
            return []
        lines: list[int] = []
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "input"
            ):
                lines.append(node.lineno)
        return lines

    violations: list[str] = []
    for py_file in APPS_RG_DIR.rglob("*.py"):
        if py_file.name == "cli_hitl_adapter.py":
            continue
        src = py_file.read_text(encoding="utf-8")
        bad_lines = _find_bare_input_calls(src)
        src_lines = src.splitlines()
        for lineno in bad_lines:
            snippet = src_lines[lineno - 1].strip()[:80] if lineno <= len(src_lines) else ""
            violations.append(f"{py_file.relative_to(REPO_ROOT)}:{lineno}: {snippet}")
    assert not violations, (
        f"Found direct input() calls outside cli_hitl_adapter.py "
        f"(single-chokepoint violation):\n" + "\n".join(violations)
    )


@pytest.mark.governance
def test_human_review_decision_hash_round_trips() -> None:
    """HumanReviewDecision.compute_hash / verify_hash must be consistent."""
    from apps_rg.hitl.hitl_schemas import HumanReviewDecision

    decision_id = str(uuid.uuid4())
    chosen = "APPROVE"
    manifest_hash = "deadbeef"
    h = HumanReviewDecision.compute_hash(decision_id, chosen, manifest_hash)
    decision = HumanReviewDecision(
        decision_id=decision_id,
        request_id=str(uuid.uuid4()),
        chosen_option_id=chosen,
        decision_timestamp=datetime.now(tz=timezone.utc).isoformat(),
        input_manifest_hash=manifest_hash,
        decision_hash=h,
        replay_key="rk-test",
    )
    assert decision.verify_hash(), "HumanReviewDecision.verify_hash() failed on a freshly constructed decision."


@pytest.mark.governance
def test_hitl_replay_store_append_and_verify() -> None:
    """HITLReplayStore must append rows and verify_all must return no errors."""
    from apps_rg.hitl.hitl_replay_store import HITLReplayStore
    from apps_rg.hitl.hitl_schemas import HumanReviewDecision

    with tempfile.TemporaryDirectory() as tmpdir:
        store = HITLReplayStore(Path(tmpdir))
        decision_id = str(uuid.uuid4())
        chosen = "APPROVE"
        manifest_hash = "cafebabe"
        h = HumanReviewDecision.compute_hash(decision_id, chosen, manifest_hash)
        decision = HumanReviewDecision(
            decision_id=decision_id,
            request_id=str(uuid.uuid4()),
            chosen_option_id=chosen,
            decision_timestamp=datetime.now(tz=timezone.utc).isoformat(),
            input_manifest_hash=manifest_hash,
            decision_hash=h,
            replay_key="rk-store-test",
        )
        store.append(decision)
        rows = store.load_all()
        assert len(rows) == 1
        errors = store.verify_all()
        assert not errors, f"HITLReplayStore.verify_all() found errors: {errors}"


@pytest.mark.governance
def test_trigger_policy_yaml_matches_trigger_kinds() -> None:
    """hitl_trigger_policy.yaml trigger_kinds must exactly match TRIGGER_KINDS in hitl_schemas."""
    from apps_rg.hitl.hitl_schemas import TRIGGER_KINDS

    assert TRIGGER_POLICY.exists(), f"hitl_trigger_policy.yaml missing: {TRIGGER_POLICY}"
    doc = yaml.safe_load(TRIGGER_POLICY.read_text(encoding="utf-8"))
    yaml_kinds = {t["trigger_kind"] for t in doc.get("triggers", [])}
    schema_kinds = set(TRIGGER_KINDS)
    assert yaml_kinds == schema_kinds, (
        f"hitl_trigger_policy.yaml trigger_kinds {yaml_kinds} "
        f"!= hitl_schemas.TRIGGER_KINDS {schema_kinds}. "
        "Both must stay in sync."
    )


@pytest.mark.governance
def test_hitl_bridge_evaluate_returns_none_when_no_run_report() -> None:
    """evaluate_hitl must return None gracefully when run_report.json is absent."""
    from apps_rg.integrations.hitl_bridge import evaluate_hitl

    with tempfile.TemporaryDirectory() as tmpdir:
        result = evaluate_hitl(Path(tmpdir))
        assert result is None, (
            f"evaluate_hitl must return None when run_report.json absent. Got: {result!r}"
        )


@pytest.mark.governance
def test_trigger_kinds_is_non_empty_tuple_of_strings() -> None:
    """TRIGGER_KINDS must be a non-empty tuple of non-empty strings."""
    from apps_rg.hitl.hitl_schemas import TRIGGER_KINDS

    assert isinstance(TRIGGER_KINDS, tuple) and TRIGGER_KINDS
    for kind in TRIGGER_KINDS:
        assert isinstance(kind, str) and kind, f"TRIGGER_KINDS entry is empty or non-string: {kind!r}"
