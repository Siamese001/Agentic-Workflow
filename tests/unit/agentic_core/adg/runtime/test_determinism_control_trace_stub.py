from __future__ import annotations

import ast
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[5]
    / "agentic_core"
    / "adg"
    / "runtime"
    / "determinism_control.py"
)


def test_determinism_control_uses_trace_contract_module_alias() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))

    direct_trace_imports: list[str] = []
    has_module_alias = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "agentic_core.runtime.contracts.lifecycle_trace_contract":
                direct_trace_imports.extend(alias.name for alias in node.names)
            if node.module == "agentic_core.runtime.contracts":
                has_module_alias = any(
                    alias.name == "lifecycle_trace_contract" and alias.asname == "ltc"
                    for alias in node.names
                )

    fanout = [
        name
        for name in direct_trace_imports
        if name.startswith("_emit_") or name.startswith("emit_")
    ]
    assert fanout == []
    assert has_module_alias


def test_determinism_controller_digest_survives_trace_import_refactor() -> None:
    from agentic_core.adg.runtime.determinism_control import DeterminismController

    controller = DeterminismController(agent_id="agent-a", run_id="run-a")
    controller.seed_rng(7)
    controller.patch_time()

    digest = controller.emit_determinism_digest(["event-a", "event-b"])
    report = controller.report.to_dict()

    assert digest.digest_hash
    assert report["rng_seed"] == 7
    assert report["digest_hash"] == digest.digest_hash
    assert report["violation_count"] == 0
