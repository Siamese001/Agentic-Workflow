"""Helper to record golden-replay fixtures for prompt-reception.

Plan: prompt-reception-followups-a7b3c4, phase RH5B.2.

This module is a TEST utility — it lives under ``tests/`` on purpose so it
is never imported by production code. Consumers call
:func:`record_fixture` to snapshot the current ``PromptMessages`` shape
for a given app + scenario.

Do NOT import from production ``agentic_core`` modules unless necessary;
the recorder should remain self-contained and mirror what the harness
reads back.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.reasoning.compiled_artifact import (
    AuthorityLevel,
    AuthoritySlot,
    CompiledPromptArtifact,
)
from agentic_core.L4_state.cache.replay_key import (
    SLOT_DIGEST_PREFIX,
    compute_slot_digest_key,
)

FIXTURE_SCHEMA_VERSION = 1


def _build_artifact_and_slots(
    slots: dict[str, str],
    trace_id: str = "fixture-trace",
) -> tuple[CompiledPromptArtifact, dict[str, AuthoritySlot]]:
    """Reconstruct an artifact + slot map from a simple code->text dict."""
    slot_objs: dict[str, AuthoritySlot] = {}
    for code, content in slots.items():
        slot_objs[code.upper()] = AuthoritySlot(
            slot_type=code.upper(),
            content=content,
            authority_level=AuthorityLevel.from_slot_code(code),
            source_layer="L0",
        )
    system_parts = [slots[c] for c in ("S0", "I0", "D0", "C0", "E0", "M0", "H0") if c in slots]
    final_system = "\n\n".join(p for p in system_parts if p)
    final_user = slots.get("U0", "")
    artifact = CompiledPromptArtifact(
        trace_id=trace_id,
        system_version_hash="fixture-svh",
        final_system_string=final_system,
        final_user_string=final_user,
        allowed_tools_schema=[],
        tokens=0,
        slots_used=list(slot_objs.keys()),
        signature="",
    )
    return artifact, slot_objs


def record_fixture(
    app: str,
    scenario: str,
    slots: dict[str, str],
    output_dir: str | Path,
    adapter_version: str = "v2",
    exemplar_task_class: str | None = None,
) -> Path:
    """Write a golden-replay fixture file.

    Parameters
    ----------
    app
        App identifier (``apps_research``, ...).
    scenario
        Short kebab-or-snake-case label for the recorded scenario.
    slots
        Map from slot code (S0/I0/D0/C0/E0/M0/H0/U0) to rendered text.
    output_dir
        Directory to write the fixture into. Created if missing.
    adapter_version
        Adapter pipeline version in use at record time. Recorded so
        fixture replay can verify matching adapter_version.
    exemplar_task_class
        Exemplar task class at record time (``None`` when app does not
        opt into E0).

    Returns
    -------
    Path
        The written fixture file path.
    """
    artifact, slot_objs = _build_artifact_and_slots(slots)
    ir = artifact.to_prompt_messages(slots=slot_objs)
    replay_key = compute_slot_digest_key(ir)

    fixture: dict[str, Any] = {
        "fixture_schema_version": FIXTURE_SCHEMA_VERSION,
        "app": app,
        "scenario": scenario,
        "inputs": {
            "adapter_version": adapter_version,
            "exemplar_task_class": exemplar_task_class,
            "slots": [[code, text] for code, text in slots.items()],
        },
        "expected": {
            "slots_used": list(artifact.slots_used),
            "slot_map": dict(ir.slot_map),
            "ordered_slots": list(ir.ordered_slots),
            "replay_key_prefix": SLOT_DIGEST_PREFIX,
            "replay_key_digest_length": len(replay_key) - len(SLOT_DIGEST_PREFIX),
        },
    }

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{app}__{scenario}.json"
    out_path.write_text(
        json.dumps(fixture, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    return out_path


__all__ = ["FIXTURE_SCHEMA_VERSION", "record_fixture"]
