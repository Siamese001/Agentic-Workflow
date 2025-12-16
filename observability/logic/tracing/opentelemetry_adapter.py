# AUTO-POPULATED BY WINDSURF v2 — 2025-12-07
# ======================================================================

"""Module implementation."""

import logging
import sys
import types

# import archives.legacy_resume_gen.Agentic_Workflow-10_10.l4.types  # DEPRECATED: Archive import...
from pathlib import Path

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "tests"
OUTPUT_ROOT = REPO_ROOT / "tests_flat"
SOURCE_REL_PATH = "state/test_safety_state_persistence.py"
SOURCE_PATH = REPO_ROOT / SOURCE_REL_PATH

# Embedded canonical source
EMBEDDED_SOURCES = {
    SOURCE_REL_PATH: """from models import MainGraphState
from states import StateAdapterStack

def test_safety_fields_persist_via_patch() -> None:
    \"\"\"Docstring.\"\"\"
    FOUNDATION = MainGraphState()
    PATCH = {
        "safety_report": {"is_safe": True, "findings": []},
        "policy_decision": {"allowed": True, "reason": None},
        "constitutional_review": {"passed": True, "violations": []},
    }

    ADAPTER = StateAdapterStack(context=None, debug_mode=False)
    new_state = ADAPTER.apply_patch(FOUNDATION, PATCH)

    assert new_state.safety_report == PATCH["safety_report"]
    assert new_state.policy_decision == PATCH["policy_decision"]
    assert new_state.constitutional_review == PATCH["constitutional_review"]
"""
}

ORIGINAL_MODULE_NAME = "tests.state.test_safety_state_persistence"
FLAT_MODULE_NAME = "tests_flat.state__test_safety_state_persistence"


def _ensure_import_roots() -> None:
    ROOT = str(REPO_ROOT)
    flat_root = str(OUTPUT_ROOT)
    for candidate in (ROOT, flat_root):
        if candidate not in sys.path:
            sys.path.insert(0, candidate)
    tests_pkg = sys.modules.setdefault("tests", types.ModuleType("tests"))
    tests_pkg.__path__ = list({*(getattr(tests_pkg,
                                         "__path__",
                                         []) or []),
                               str(SOURCE_ROOT),
                               flat_root})
    tests_flat_pkg = sys.modules.setdefault(
        "tests_flat", types.ModuleType("tests_flat"))
    tests_flat_pkg.__path__ = list(
        {*(getattr(tests_flat_pkg, "__path__", []) or []), flat_root})


def _materialize_module() -> types.ModuleType:
    MODULE = types.ModuleType(ORIGINAL_MODULE_NAME)
    MODULE.__file__ = str(SOURCE_PATH)
    MODULE.__package__ = ORIGINAL_MODULE_NAME.rpartition(".")[0]
    exec(compile(EMBEDDED_SOURCES[SOURCE_REL_PATH],
        str(SOURCE_PATH),
        "exec"),
    MODULE.__dict__)
    sys.modules[ORIGINAL_MODULE_NAME] = MODULE
    sys.modules[FLAT_MODULE_NAME] = MODULE
    return MODULE

_ensure_import_roots()
_embedded_module = _materialize_module()
for _name, _value in list(_embedded_module.__dict__.items()):
    if _name == "__builtins__":
        continue
    globals()[_name] = _value

