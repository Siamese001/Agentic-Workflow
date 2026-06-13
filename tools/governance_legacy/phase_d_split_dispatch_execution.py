#!/usr/bin/env python3
"""Phase D — move run_*_execution from dispatch modules to section lane_execution modules."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _find_def(lines: list[str], name: str) -> int:
    for i, ln in enumerate(lines):
        if ln.startswith(f"def {name}("):
            return i
    raise ValueError(f"missing def {name}")


def split_competencies() -> None:
    dispatch_path = REPO / "apps_rg/runtime/sections/competencies_lane_runtime.py"
    lane_path = REPO / "apps_rg/runtime/sections/competencies_lane_execution.py"
    lines = dispatch_path.read_text(encoding="utf-8").splitlines(keepends=True)
    start = _find_def(lines, "run_competencies_execution")
    end = _find_def(lines, "run_dispatch")
    body = "".join(lines[start:end])
    body = body.replace("def run_competencies_execution(", "def run_competencies_lane_execution(", 1)
    body = body.replace(
        'trace_runtime_path: str = "apps_rg.runtime.sections.competencies_lane_runtime"',
        'trace_runtime_path: str = "apps_rg.runtime.sections.competencies_lane"',
        1,
    )
    header = '''"""Canonical competencies lane runtime execution (W11-M4C / legacy burndown Phase D).

``apps_rg.runtime.sections.competencies_lane_runtime`` retains shared compile/repair helpers and
compat re-exports; product entry is ``python -m apps_rg --section competencies``.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


def _hydrate_dispatch_helpers() -> None:
    import apps_rg.runtime.sections.competencies_lane_runtime as _cd

    _skip = frozenset({
        "run_competencies_execution",
        "run_competencies_lane_execution",
        "run_dispatch",
        "main",
        "build_parser",
    })
    g = globals()
    for name in dir(_cd):
        if name.startswith("__") or name in _skip:
            continue
        g.setdefault(name, getattr(_cd, name))


_hydrate_dispatch_helpers()

'''
    footer = '''

def run_competencies_execution(
    args: argparse.Namespace,
    *,
    artifact_dir_override: Path | None = None,
    trace_runtime_path: str = "apps_rg.runtime.sections.competencies_lane_runtime",
    print_output: bool = True,
) -> dict[str, Any]:
    """Compat alias — canonical trace path is sections.competencies_lane."""
    return run_competencies_lane_execution(
        args,
        artifact_dir_override=artifact_dir_override,
        trace_runtime_path=trace_runtime_path,
        print_output=print_output,
    )


__all__ = ["run_competencies_lane_execution", "run_competencies_execution"]
'''
    lane_path.write_text(header + body + footer, encoding="utf-8")
    shim = [
        '"""Compat re-export — canonical: apps_rg.runtime.sections.competencies_lane_execution."""\n',
        "\n",
        "from apps_rg.runtime.sections.competencies_lane_execution import (\n",
        "    run_competencies_execution,\n",
        "    run_competencies_lane_execution,\n",
        ")\n",
        "\n",
        "__all__ = ['run_competencies_execution', 'run_competencies_lane_execution']\n",
        "\n",
    ]
    dispatch_path.write_text("".join(lines[:start] + shim + lines[end:]), encoding="utf-8")
    print(f"competencies: moved {end - start} lines -> {lane_path.relative_to(REPO)}")


def split_ibm_narrative() -> None:
    dispatch_path = REPO / "apps_rg/runtime/sections/ibm_narrative_lane_runtime.py"
    lane_path = REPO / "apps_rg/runtime/sections/ibm_narrative_lane_execution.py"
    lines = dispatch_path.read_text(encoding="utf-8").splitlines(keepends=True)
    start = _find_def(lines, "run_ibm_narrative_execution")
    end = next(i for i, ln in enumerate(lines) if ln.startswith('if __name__ == "__main__"'))
    body = "".join(lines[start:end])
    body = body.replace("def run_ibm_narrative_execution(", "def run_ibm_narrative_lane_execution(", 1)
    body = body.replace(
        'trace_runtime_path: str = "apps_rg.runtime.sections.ibm_narrative_lane_runtime"',
        'trace_runtime_path: str = "apps_rg.runtime.sections.ibm_narrative_lane"',
        1,
    )
    header = '''"""Canonical IBM narrative lane runtime execution (legacy burndown Phase D).

``apps_rg.runtime.sections.ibm_narrative_lane_runtime`` retains shared helpers and compat re-exports;
product entry is ``python -m apps_rg --section ibm_narrative``.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


def _hydrate_dispatch_helpers() -> None:
    import apps_rg.runtime.sections.ibm_narrative_lane_runtime as _cd

    _skip = frozenset({
        "run_ibm_narrative_execution",
        "run_ibm_narrative_lane_execution",
    })
    g = globals()
    for name in dir(_cd):
        if name.startswith("__") or name in _skip:
            continue
        g.setdefault(name, getattr(_cd, name))


_hydrate_dispatch_helpers()

'''
    footer = '''

def run_ibm_narrative_execution(
    args: argparse.Namespace,
    *,
    artifact_dir_override: Path | None = None,
    trace_runtime_path: str = "apps_rg.runtime.sections.ibm_narrative_lane_runtime",
    print_output: bool = False,
) -> dict[str, Any]:
    """Compat alias — canonical trace path is sections.ibm_narrative_lane."""
    return run_ibm_narrative_lane_execution(
        args,
        artifact_dir_override=artifact_dir_override,
        trace_runtime_path=trace_runtime_path,
        print_output=print_output,
    )


__all__ = ["run_ibm_narrative_lane_execution", "run_ibm_narrative_execution"]
'''
    lane_path.write_text(header + body + footer, encoding="utf-8")
    shim = [
        '"""Compat re-export — canonical: apps_rg.runtime.sections.ibm_narrative_lane_execution."""\n',
        "\n",
        "from apps_rg.runtime.sections.ibm_narrative_lane_execution import (\n",
        "    run_ibm_narrative_execution,\n",
        "    run_ibm_narrative_lane_execution,\n",
        ")\n",
        "\n",
        "__all__ = ['run_ibm_narrative_execution', 'run_ibm_narrative_lane_execution']\n",
        "\n",
    ]
    dispatch_path.write_text("".join(lines[:start] + shim + lines[end:]), encoding="utf-8")
    print(f"ibm_narrative: moved {end - start} lines -> {lane_path.relative_to(REPO)}")


def main() -> None:
    split_competencies()
    split_ibm_narrative()


if __name__ == "__main__":
    main()
