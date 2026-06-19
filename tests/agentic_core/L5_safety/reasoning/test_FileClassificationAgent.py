"""ADG-hotspot regression tests for `agentic_core.L5_safety.reasoning.FileClassificationAgent`."""

from __future__ import annotations

import importlib
from pathlib import Path


MODULE_PATH = "agentic_core.L5_safety.reasoning.FileClassificationAgent"
mod = importlib.import_module(MODULE_PATH)
FileClassificationHealerAgent = mod.FileClassificationHealerAgent
FileClassificationAgent = mod.FileClassificationAgent


def _write_python_file(root: Path, relative_path: str, content: str) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_module_imports_clean() -> None:
    """High fan-in hotspot module must import cleanly."""
    assert mod is not None


def test_module_exports_current_alias() -> None:
    """The backward-compat alias must still point at the healer class."""
    assert FileClassificationAgent is FileClassificationHealerAgent
    public = [name for name in dir(mod) if not name.startswith("_")]
    assert "FileClassificationHealerAgent" in public
    assert "FileClassificationAgent" in public
    assert "ClassificationResult" in public


def test_module_reimports_idempotently() -> None:
    """Re-importing the hotspot module should not raise."""
    assert importlib.import_module(MODULE_PATH) is mod


def test_self_named_agent_file_stays_agent_and_compliant(tmp_path: Path) -> None:
    """A self-named FileClassificationAgent file must stay classified as AGENT."""
    target = _write_python_file(
        tmp_path,
        "FileClassificationAgent.py",
        "class FileClassificationAgent:\n    pass\n",
    )
    agent = FileClassificationHealerAgent(project_root=tmp_path)

    assert agent.classify_file(target) == "AGENT"
    assert agent.get_compliant_name(target, "AGENT") == target.name
