"""Smoke-compile the apps_rg AgentSpec via the deterministic Spec Compiler.

This proves the new spec is internally consistent: every section produces a
section, persona-token estimate fits the cap, and a stable compilation_hash
is produced. Re-running yields a byte-identical hash with frozen_clock.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from agentic_core.prompt_governance.spec_compiler import (  # noqa: E402
    COMPILER_VERSION,
    compile_spec,
)


def main() -> int:
    spec_path = REPO / "apps_rg/config/specs/agent_spec.resume_generation.v1.0.0.yaml"
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    print(f"compiler_version={COMPILER_VERSION}")
    print(f"spec_id={spec['spec_id']}")
    print(f"spec_version={spec['spec_version']}")
    artifact = compile_spec(spec, frozen_clock="2026-04-29T23:30:00+00:00")
    print(f"compilation_hash={artifact.compilation_hash}")
    print(f"prompt_sections={[s.role for s in artifact.prompt_manifest.sections]}")
    print(f"persona_token_estimate={artifact.prompt_manifest.persona_token_estimate}")
    print(f"persona_token_cap={artifact.prompt_manifest.persona_token_cap}")
    print(f"tool_count={len(artifact.tool_manifest.tools)}")
    print(f"egress_blocked={artifact.tool_manifest.egress.get('blocked_by_default')}")
    print(f"rubric_id={artifact.eval_manifest.rubric_id}")
    print(f"rubric_version={artifact.eval_manifest.rubric_version}")

    # Determinism check
    artifact2 = compile_spec(spec, frozen_clock="2026-04-29T23:30:00+00:00")
    if artifact.compilation_hash == artifact2.compilation_hash:
        print("DETERMINISM: PASS (byte-identical hash on rerun)")
    else:
        print(f"DETERMINISM: FAIL ({artifact.compilation_hash} vs {artifact2.compilation_hash})")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
