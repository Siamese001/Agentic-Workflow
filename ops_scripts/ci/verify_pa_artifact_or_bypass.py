"""Spine verifier — Prompt Assembly ran OR PA was lawfully bypassed.

Asserts exactly one of these holds for the run:

    A) ``route_contract.prompt_assembly_required == True`` (or
       ``model_execution_required == True``) AND a
       ``compiled_prompt_artifact.json`` exists.

    B) Both flags False AND a ``prompt_assembly_bypass_receipt.json``
       exists with ``prompt_assembly_required=False``,
       ``model_execution_required=False``, and a permitted bypass reason.

The R1B terminal-shortcircuit path always lands on Branch B because the
cache returns the cached answer; no model call is made.

Exit codes: 0 PASS / 2 FAIL_CLOSED / 3 HARNESS_ERROR.
"""

from __future__ import annotations

import sys

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from _w2_verifier_common import (  # noqa: E402
    EXIT_HARNESS_ERROR,
    fail,
    load_payload,
    passed,
    resolve_artifact_dir,
)

from agentic_core.runtime.contracts.prompt_assembly_bypass_receipt import (  # noqa: E402
    ALLOWED_PA_BYPASS_REASONS,
)


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    print(f"[verify_pa_artifact_or_bypass] artifact_dir={art_dir}")

    try:
        rc = load_payload(art_dir, "route_contract.json")
    except FileNotFoundError as exc:
        return fail("ROUTE_CONTRACT_MISSING", str(exc))

    pa_required = bool(rc.get("prompt_assembly_required", False))
    model_required = bool(rc.get("model_execution_required", False))

    if pa_required or model_required:
        # Branch A.
        cpa_path = art_dir / "compiled_prompt_artifact.json"
        if not cpa_path.exists():
            return fail(
                "COMPILED_PROMPT_ARTIFACT_MISSING",
                f"prompt_assembly_required={pa_required} or "
                f"model_execution_required={model_required} but "
                f"compiled_prompt_artifact.json is absent.",
            )
        return passed(
            f"prompt_assembly_required={pa_required} / "
            f"model_execution_required={model_required}; "
            f"CompiledPromptArtifact present"
        )

    # Branch B — bypass required.
    try:
        bypass = load_payload(art_dir, "prompt_assembly_bypass_receipt.json")
    except FileNotFoundError as exc:
        return fail(
            "PA_BYPASS_RECEIPT_MISSING",
            "prompt_assembly_required=False and model_execution_required=False, "
            f"but prompt_assembly_bypass_receipt.json is absent: {exc}",
        )

    if bypass.get("prompt_assembly_required") is not False:
        return fail(
            "PA_BYPASS_PA_REQUIRED_TRUE",
            f"prompt_assembly_required={bypass.get('prompt_assembly_required')!r}; must be False",
        )
    if bypass.get("model_execution_required") is not False:
        return fail(
            "PA_BYPASS_MODEL_REQUIRED_TRUE",
            f"model_execution_required={bypass.get('model_execution_required')!r}; must be False",
        )
    reason = bypass.get("prompt_assembly_bypass_reason", "")
    if reason not in ALLOWED_PA_BYPASS_REASONS:
        return fail(
            "PA_BYPASS_REASON_INVALID",
            f"prompt_assembly_bypass_reason={reason!r} not in "
            f"{sorted(ALLOWED_PA_BYPASS_REASONS)}",
        )

    return passed(f"Prompt Assembly lawfully bypassed: reason={reason!r}")


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001 - top-level harness boundary
        print(f"HARNESS_ERROR: {exc}")
        sys.exit(EXIT_HARNESS_ERROR)
