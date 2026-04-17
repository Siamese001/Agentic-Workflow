"""Fix testing and observability coverage for discovered agents.

This utility reads the agent discovery manifest, adds a logger definition where
missing, and injects ``SubatomicTestingMixin`` into discovered classes that do
not already inherit it.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L2_execution.utils import (
    write_gateway as _wg,
)  # guardian: allow-layer-violation -- L6 observability module uses L2 execution type; intentional cross-layer instrumentation dependency

try:
    from ops_scripts.dev_tools.L0_routing_scripts.full_agent_discovery import AGENT_DISCOVERY_JSON
except ImportError:  # guardian: allow-silent-swallow
    AGENT_DISCOVERY_JSON = "agent_discovery_full.json"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DISCOVERY_JSON = PROJECT_ROOT / AGENT_DISCOVERY_JSON
LOGGING_IMPORT = "import logging"
LOGGER_INIT = "logger = logging.getLogger(__name__)"
TESTING_IMPORT = (
    "from agentic_core.L3_orchestration.reasoning.subatomic_testing_mixin import SubatomicTestingMixin"
)
_IMPORT_RE = re.compile(r"^(?:from\s+\S+\s+import\s+.+|import\s+.+)$")


def _deterministic_trace_id(label: str, payload: Any = None) -> str:
    material = json.dumps({"label": label, "payload": payload}, sort_keys=True, default=str)
    return f"fto-{hashlib.sha256(material.encode('utf-8')).hexdigest()[:16]}"


def load_agents() -> list[dict[str, Any]]:
    """Load all agents from the discovery manifest."""
    if not DISCOVERY_JSON.exists():
        raise FileNotFoundError(f"Discovery manifest not found: {DISCOVERY_JSON}")
    with DISCOVERY_JSON.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError(f"Discovery manifest must contain a list of agents, got {type(payload).__name__}")
    return [agent for agent in payload if isinstance(agent, dict)]


def _find_import_insertion_index(lines: list[str]) -> int:
    in_docstring = False
    doc_quote = ""
    last_import_idx = -1
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(('"""', "'''")):
            quote = stripped[:3]
            if not in_docstring:
                in_docstring = True
                doc_quote = quote
                if stripped.count(quote) >= 2 and len(stripped) > 3:
                    in_docstring = False
                    doc_quote = ""
                continue
            if stripped.endswith(doc_quote):
                in_docstring = False
                doc_quote = ""
            continue
        if in_docstring:
            continue
        if _IMPORT_RE.match(stripped):
            last_import_idx = index
            continue
        break
    return last_import_idx + 1 if last_import_idx >= 0 else 0


def _write_text(file_path: Path, content: str) -> None:
    assert_no_persistent_write("L6", "write_text")
    _wg.write_text(file_path, content, encoding="utf-8")


def add_logging_to_file(file_path: Path) -> bool:
    """Add logging import and logger initialization to a file."""
    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception as exc:  # guardian: allow-broad-exception
        print(f"  [ERROR] Cannot read {file_path}: {exc}")
        return False

    modified = False
    lines = source.splitlines()

    if "import logging" not in source and "from logging" not in source:
        insert_idx = _find_import_insertion_index(lines)
        lines.insert(insert_idx, LOGGING_IMPORT)
        modified = True

    if "logger = logging.getLogger" not in "\n".join(lines) and "Logger = logging.getLogger" not in "\n".join(
        lines
    ):
        insert_idx = _find_import_insertion_index(lines)
        if insert_idx < len(lines) and lines[insert_idx : insert_idx + 1] != [""]:
            lines.insert(insert_idx, "")
            insert_idx += 1
        lines.insert(insert_idx, LOGGER_INIT)
        modified = True

    if not modified:
        return False

    try:
        _write_text(file_path, "\n".join(lines) + ("\n" if source.endswith("\n") else ""))
        return True
    except Exception as exc:  # guardian: allow-broad-exception
        print(f"  [ERROR] Cannot write {file_path}: {exc}")
        return False


def add_testing_mixin_to_class(file_path: Path, class_name: str) -> bool:
    """Add ``SubatomicTestingMixin`` to a class definition if absent."""
    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception as exc:  # guardian: allow-broad-exception
        print(f"  [ERROR] Cannot read {file_path}: {exc}")
        return False

    if not class_name or f"class {class_name}" not in source:
        return False

    modified = False
    lines = source.splitlines()
    if TESTING_IMPORT not in source:
        insert_idx = _find_import_insertion_index(lines)
        lines.insert(insert_idx, TESTING_IMPORT)
        source = "\n".join(lines)
        modified = True

    pattern = re.compile(rf"(class\s+{re.escape(class_name)}\s*\()([^)]*?)(\)\s*:)")

    def _replace(match: re.Match[str]) -> str:
        bases = [base.strip() for base in match.group(2).split(",") if base.strip()]
        if "SubatomicTestingMixin" in bases:
            return match.group(0)
        return (
            f"{match.group(1)}SubatomicTestingMixin{', ' if bases else ''}{', '.join(bases)}{match.group(3)}"
        )

    new_source, replacements = pattern.subn(_replace, source, count=1)
    if replacements == 0:
        return False
    if new_source == source and not modified:
        return False

    try:
        _write_text(
            file_path, new_source + ("\n" if source.endswith("\n") and not new_source.endswith("\n") else "")
        )
        return True
    except Exception as exc:  # guardian: allow-broad-exception
        print(f"  [ERROR] Cannot write {file_path}: {exc}")
        return False


def main() -> None:
    trace_id = _deterministic_trace_id("main", str(DISCOVERY_JSON))
    print("=" * 80)
    print("FIX TESTING & OBSERVABILITY")
    print(trace_id)
    print("=" * 80)

    agents = load_agents()
    print(f"\nProcessing {len(agents)} agents...\n")

    by_file: dict[str, list[str]] = {}
    for agent in agents:
        path = str(agent.get("path", "") or "").strip()
        class_name = str(agent.get("class_name", "") or "").strip()
        if not path or not class_name:
            continue
        full_path = str(PROJECT_ROOT / path)
        class_list = by_file.setdefault(full_path, [])
        if class_name not in class_list:
            class_list.append(class_name)

    logging_added = 0
    testing_added = 0
    for file_path_str, class_names in sorted(by_file.items()):
        file_path = Path(file_path_str)
        if not file_path.exists():
            continue
        if add_logging_to_file(file_path):
            logging_added += 1
            print(f"[LOGGING] {file_path.relative_to(PROJECT_ROOT)}")
        for class_name in sorted(class_names):
            if add_testing_mixin_to_class(file_path, class_name):
                testing_added += 1
                print(f"[TESTING] {class_name} in {file_path.name}")

    print("\n" + "=" * 80)
    print(f"SUMMARY: Logging added to {logging_added} files | Testing mixin added to {testing_added} classes")
    print("=" * 80)


if __name__ == "__main__":
    main()
