"""Probe canonical-replacement utils for each of the 6 remaining agents.

For each util, list (a) module path exists, (b) top-level exported names,
(c) whether a 1:1 function equivalent of the agent's public methods exists.
"""

from __future__ import annotations

import importlib
import inspect
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]

# (agent_class_name, agent_module, util_module_candidates[])
TARGETS = [
    (
        "SSOTFolderCleanupAgent",
        "agentic_core.L0_routing.reasoning.SSOTFolderCleanupAgent",
        ["agentic_core.L0_routing.utils.ssot_folder_cleanup_util", "agentic_core.L0_routing.utils"],
    ),
    (
        "CodeJanitorAgent",
        "agentic_core.L5_safety.reasoning.CodeJanitorAgent",
        ["agentic_core.L5_safety.utils.code_janitor_util"],
    ),
    (
        "CodeDetectorAgent",
        "agentic_core.L5_safety.reasoning.CodeDetectorAgent",
        ["agentic_core.L5_safety.utils.code_detector_util"],
    ),
    (
        "CodeValidatorAgent",
        "agentic_core.L5_safety.reasoning.CodeValidatorAgent",
        ["agentic_core.L5_safety.utils.code_validator_util"],
    ),
    (
        "CodeEnforcerAgent",
        "agentic_core.L5_safety.reasoning.CodeEnforcerAgent",
        ["agentic_core.L5_safety.utils.code_enforcer_util"],
    ),
    (
        "SubAtomicAgent",
        "agentic_core.L3_orchestration.reasoning.SubAtomicAgent",
        ["agentic_core.L3_orchestration.utils.subatomic_agent_util"],
    ),
]


def try_import(m: str):
    try:
        return importlib.import_module(m), None
    except BaseException as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {str(e)[:200]}"


def top_names(mod) -> list[str]:
    if mod is None:
        return []
    names = getattr(mod, "__all__", None)
    if names is None:
        names = [n for n in dir(mod) if not n.startswith("_")]
    return sorted(names)


for agent_cls, agent_mod, utils in TARGETS:
    print(f"\n=== {agent_cls} ===")
    print(f"  agent module: {agent_mod}")
    am, aerr = try_import(agent_mod)
    if aerr:
        print(f"    agent import FAIL: {aerr}")
    elif am:
        cls = getattr(am, agent_cls, None)
        if cls:
            methods = [
                n
                for n, _ in inspect.getmembers(cls, predicate=inspect.isfunction)
                if not n.startswith("_") or n == "__init__"
            ]
            print(f"    agent public methods: {methods[:15]}")
    for u in utils:
        um, uerr = try_import(u)
        if uerr:
            print(f"  util {u}: IMPORT FAIL ({uerr})")
        else:
            names = top_names(um)
            print(f"  util {u}: {len(names)} names")
            print(f"    exports: {names[:20]}")
