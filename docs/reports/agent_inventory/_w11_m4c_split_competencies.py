#!/usr/bin/env python3
"""W11-M4C — move run_competencies_execution to competencies_lane_execution."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DISPATCH = REPO / "apps_rg/runtime/sections/competencies_lane_api.py"
LANE_EXEC = REPO / "apps_rg/runtime/sections/competencies_lane_execution.py"

HEADER = '''"""Canonical competencies lane runtime execution (W11-M4C).

``apps_rg.runtime.sections.competencies_lane_api.run_competencies_execution`` re-exports
this entry for deprecated CLI compatibility only.
"""
from __future__ import annotations

from typing import Any

import argparse
from pathlib import Path

from apps_rg.runtime.dispatch import competencies_dispatch as _cd

# Re-use module-level helpers/constants from dispatch (shared compile/runtime utilities).
REPO_ROOT = _cd.REPO_ROOT
LANE_KEY = _cd.LANE_KEY
collect_employment_bullets = _cd.collect_employment_bullets
compile_competencies_prompt = _cd.compile_competencies_prompt
load_companion_context = _cd.load_companion_context
build_resume_support_blob = _cd.build_resume_support_blob
build_c0_proof_support_blob = _cd.build_c0_proof_support_blob
build_runtime_payload = _cd.build_runtime_payload
sha16 = _cd.sha16
write_json = _cd.write_json
attach_reasoning_to_prompt_trace = _cd.attach_reasoning_to_prompt_trace
'''

FOOTER = '''

def run_competencies_execution(
    args: argparse.Namespace,
    *,
    artifact_dir_override: Path | None = None,
    trace_runtime_path: str = "apps_rg.runtime.sections.competencies_lane",
    print_output: bool = True,
) -> dict[str, Any]:
    """Canonical competencies execution — default trace path is the section lane."""
    return run_competencies_lane_execution(
        args,
        artifact_dir_override=artifact_dir_override,
        trace_runtime_path=trace_runtime_path,
        print_output=print_output,
    )


__all__ = ["run_competencies_lane_execution", "run_competencies_execution"]
'''


def main() -> None:
    lines = DISPATCH.read_text(encoding="utf-8").splitlines(keepends=True)
    # 0-based: line 1490 is index 1489
    body_lines = lines[1489:2154]
    body = "".join(body_lines)
    body = body.replace(
        "def run_competencies_execution(",
        "def run_competencies_lane_execution(",
        1,
    )
    body = body.replace(
        'trace_runtime_path: str = "apps_rg.runtime.sections.competencies_lane_api"',
        'trace_runtime_path: str = "apps_rg.runtime.sections.competencies_lane"',
        1,
    )
    LANE_EXEC.write_text(HEADER + body + FOOTER, encoding="utf-8")
    shim = [
        '"""Compat re-export — canonical: apps_rg.runtime.sections.competencies_lane_execution."""',
        "",
        "from apps_rg.runtime.sections.competencies_lane_execution import (",
        "    run_competencies_execution,",
        "    run_competencies_lane_execution,",
        ")",
        "",
        "__all__ = ['run_competencies_execution', 'run_competencies_lane_execution']",
        "",
    ]
    new_dispatch = lines[:1489] + shim
    DISPATCH.write_text("".join(new_dispatch), encoding="utf-8")
    print("wrote", LANE_EXEC.relative_to(REPO))
    print("patched", DISPATCH.relative_to(REPO))


if __name__ == "__main__":
    main()
