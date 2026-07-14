"""Run the canonical apps_research -> briefing.md -> apps_rg U0 proof.

The GitHub workflow calls this checked-in runner instead of embedding a long
list of pytest paths. This keeps workflow-reference validation deterministic
while preserving one authoritative test command for local and CI execution.
"""

from __future__ import annotations

import ast
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


def _top_level_function(tree: ast.Module, name: str) -> ast.FunctionDef:
    function = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == name
        ),
        None,
    )
    if function is None:
        raise AssertionError(f"producer function missing: {name}")
    return function


def _call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
        return f"{node.func.value.id}.{node.func.attr}"
    return ""


def _calls(function: ast.FunctionDef, name: str) -> list[ast.Call]:
    return [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Call) and _call_name(node) == name
    ]


def _named_dict_assignment(function: ast.FunctionDef, name: str) -> ast.Dict:
    assignments: list[ast.Dict] = []
    for node in ast.walk(function):
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == name
                for target in node.targets
            )
            and isinstance(node.value, ast.Dict)
        ):
            assignments.append(node.value)
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == name
            and isinstance(node.value, ast.Dict)
        ):
            assignments.append(node.value)
    if len(assignments) != 1:
        raise AssertionError(f"producer must define exactly one {name} dictionary")
    return assignments[0]


def _dict_items(node: ast.Dict) -> dict[str, ast.expr]:
    items: dict[str, ast.expr] = {}
    for key, value in zip(node.keys, node.values, strict=True):
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
            items[key.value] = value
    return items


def _is_name(node: ast.expr | None, name: str) -> bool:
    return isinstance(node, ast.Name) and node.id == name


def _is_string(node: ast.expr | None, value: str) -> bool:
    return isinstance(node, ast.Constant) and node.value == value


def _is_call(node: ast.expr | None, name: str) -> bool:
    return isinstance(node, ast.Call) and _call_name(node) == name


def _is_authorization_guard(node: ast.If) -> bool:
    test = node.test
    return (
        isinstance(test, ast.UnaryOp)
        and isinstance(test.op, ast.Not)
        and isinstance(test.operand, ast.Attribute)
        and isinstance(test.operand.value, ast.Name)
        and test.operand.value.id == "authorization"
        and test.operand.attr == "allows_finish"
    )


def _enforce_v2_producer_authority(producer: str) -> None:
    tree = ast.parse(producer, filename="apps_research/integrations/apps_rg_handoff.py")
    binder = _top_level_function(tree, "run_apps_rg_handoff_exit_authorization")
    publisher = _top_level_function(tree, "persist_apps_rg_targeting_brief_artifacts")

    if not _calls(binder, "exit_bind_and_finalize_apps_research"):
        raise AssertionError("producer Exit authorization does not use the canonical binder")
    authorization_calls = _calls(publisher, "run_apps_rg_handoff_exit_authorization")
    guards = [
        node
        for node in ast.walk(publisher)
        if isinstance(node, ast.If) and _is_authorization_guard(node)
    ]
    if len(authorization_calls) != 1 or len(guards) != 1:
        raise AssertionError("producer must authorize once and fail closed on canonical Exit")
    guard = guards[0]
    if authorization_calls[0].lineno >= guard.lineno:
        raise AssertionError("producer checks Exit authorization before invoking the canonical binder")

    mutation_calls = [
        node
        for node in ast.walk(publisher)
        if isinstance(node, ast.Call)
        and (
            _call_name(node) in {"_write_fsync", "_fsync_directory", "os.replace"}
            or (isinstance(node.func, ast.Attribute) and node.func.attr == "mkdir")
        )
    ]
    if not mutation_calls or guard.lineno >= min(node.lineno for node in mutation_calls):
        raise AssertionError("producer mutates the bundle before canonical Exit ALLOW")

    artifact_payloads = _dict_items(
        _named_dict_assignment(publisher, "artifact_payloads")
    )
    persisted_exit = artifact_payloads.get("exit_disposition_receipt.json")
    if not _is_call(persisted_exit, "_canonical_json_bytes"):
        raise AssertionError("producer does not persist the canonical Exit receipt")
    exit_arg = (
        persisted_exit.args[0]
        if isinstance(persisted_exit, ast.Call) and persisted_exit.args
        else None
    )
    expected_exit_expr = "authorization.exit_disposition_receipt.as_dict()"
    if exit_arg is None or ast.unparse(exit_arg) != expected_exit_expr:
        raise AssertionError("persisted Exit receipt is not derived from canonical authorization")

    handoff = _dict_items(_named_dict_assignment(publisher, "handoff_v2"))
    if not _is_string(
        handoff.get("schema_version"),
        "apps_research.apps_rg_handoff.v2",
    ):
        raise AssertionError("producer does not emit the canonical v2 handoff schema")
    exit_authorization = handoff.get("exit_authorization")
    if not isinstance(exit_authorization, ast.Dict):
        raise AssertionError("v2 handoff lacks exit_authorization")
    exit_items = _dict_items(exit_authorization)
    required_exit_keys = {
        "x3_code",
        "receipt_ref",
        "receipt_sha256",
        "output_artifact_sha256",
    }
    if set(exit_items) != required_exit_keys:
        raise AssertionError("v2 exit_authorization does not have the exact contract keys")
    if not _is_name(exit_items["x3_code"], "X3D_ALLOW_FINISH"):
        raise AssertionError("v2 exit_authorization is not exact X3D_ALLOW_FINISH")
    if ast.unparse(exit_items["receipt_ref"]) != "str(exit_disposition_path)":
        raise AssertionError("v2 exit_authorization does not reference the persisted Exit receipt")
    expected_receipt_digest = (
        "_sha256_bytes(artifact_payloads['exit_disposition_receipt.json'])"
    )
    if ast.unparse(exit_items["receipt_sha256"]) != expected_receipt_digest:
        raise AssertionError("v2 exit_authorization is not digest-bound to the persisted Exit receipt")
    if not _is_name(exit_items["output_artifact_sha256"], "exact_brief_sha256"):
        raise AssertionError("v2 Exit authorization is not bound to the exact briefing bytes")


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

    _enforce_v2_producer_authority(producer)
    if '"reason": "model_backed_x2_passed"' in producer:
        raise AssertionError("application-local X3 authorization remains in producer")
    required_consumer_fragments = (
        "def _validate_v2_handoff(",
        'exit_auth.get("x3_code") != _CANONICAL_X3_ALLOW',
        'exit_auth.get("receipt_sha256")',
        'exit_auth.get("output_artifact_sha256") != identity.get("brief_sha256")',
        'exit_receipt.get("x3_code") != _CANONICAL_X3_ALLOW',
    )
    missing_consumer = [
        fragment for fragment in required_consumer_fragments if fragment not in consumer
    ]
    if missing_consumer:
        raise AssertionError(
            f"consumer v2 Exit validation fragments missing: {missing_consumer}"
        )
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
