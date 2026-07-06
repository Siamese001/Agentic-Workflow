from __future__ import annotations

import hashlib

from apps_rg.prompt_assembly.contracts import (
    CompiledPromptArtifact,
    PromptSlotPayload,
    SlotAuthority,
)
from apps_rg.runtime.providers.anthropic_section_cache_payload import (
    MAX_ANTHROPIC_CACHE_MARKERS,
    build_anthropic_section_cache_payload,
)


def _slot(slot_id: str, content: str) -> PromptSlotPayload:
    return PromptSlotPayload(
        slot_id=slot_id,
        slot_name=slot_id,
        authority_class=SlotAuthority.SYSTEM_AUTHORITY,
        content=content,
        content_hash=hashlib.sha256(content.encode()).hexdigest()[:16],
    )


def _artifact(*slots: tuple[str, str]) -> CompiledPromptArtifact:
    return CompiledPromptArtifact(
        slot_payloads=[_slot(slot_id, content) for slot_id, content in slots],
        messages=[{"role": "system", "content": "flat compiled prompt"}],
        prompt_hash="prompt-hash",
    )


def _blocks(payload: dict) -> list[dict]:
    system = payload["system"]
    assert isinstance(system, list)
    return system


def test_pa_slot_renderer_marks_stable_slots_and_never_marks_volatile_slots() -> None:
    rendered = build_anthropic_section_cache_payload(
        section_id="competencies",
        model="claude-sonnet-5",
        compiled_prompt_artifact=_artifact(
            ("S0", "truth oath"),
            ("D0", "origin fence"),
            ("I0", "lane instructions"),
            ("C0", "stable graph proof pool"),
            ("U0", "target company changes per run"),
            ("H0", "repair note"),
            ("R0", '{"type":"object"}'),
        ),
        messages=[
            {"role": "system", "content": "flat compiled prompt"},
            {"role": "user", "content": "path_index=2 temperature=0.43"},
        ],
        workload_kind="SELF_CONSISTENCY",
    )

    blocks_by_slot = {block["slot_id"]: block for block in _blocks(rendered.anthropic_payload)}
    assert "cache_control" in blocks_by_slot["S0"]
    assert "cache_control" in blocks_by_slot["D0"]
    assert "cache_control" in blocks_by_slot["I0"]
    assert "cache_control" in blocks_by_slot["C0"]
    assert "cache_control" not in blocks_by_slot["U0"]
    assert "cache_control" not in blocks_by_slot["H0"]
    assert "cache_control" not in blocks_by_slot["R0"]
    assert rendered.cache_marker_count <= MAX_ANTHROPIC_CACHE_MARKERS
    assert rendered.cache_receipt_seed["sc_group_hash"]


def test_c0_is_skipped_for_one_shot_but_reused_for_repair() -> None:
    artifact = _artifact(
        ("S0", "truth oath"),
        ("D0", "origin fence"),
        ("I0", "lane instructions"),
        ("C0", "selected facts"),
    )

    one_shot = build_anthropic_section_cache_payload(
        section_id="executive_summary",
        model="claude-sonnet-5",
        compiled_prompt_artifact=artifact,
        workload_kind="ONE_SHOT",
    )
    repair = build_anthropic_section_cache_payload(
        section_id="executive_summary",
        model="claude-sonnet-5",
        compiled_prompt_artifact=artifact,
        messages=[{"role": "user", "content": "repair reason and prior output"}],
        workload_kind="REPAIR",
    )

    one_shot_c0 = {block["slot_id"]: block for block in _blocks(one_shot.anthropic_payload)}["C0"]
    repair_c0 = {block["slot_id"]: block for block in _blocks(repair.anthropic_payload)}["C0"]
    assert "cache_control" not in one_shot_c0
    assert "cache_control" in repair_c0
    assert one_shot.stable_prefix_hash == repair.stable_prefix_hash
    assert one_shot.c0_prefix_hash == repair.c0_prefix_hash
    assert one_shot.volatile_tail_hash != repair.volatile_tail_hash


def test_path_diversity_only_changes_volatile_tail_hash() -> None:
    artifact = _artifact(
        ("S0", "truth oath"),
        ("D0", "origin fence"),
        ("I0", "lane instructions"),
        ("C0", "same evidence pack"),
    )

    path_0 = build_anthropic_section_cache_payload(
        section_id="unify_bullets",
        model="claude-sonnet-5",
        compiled_prompt_artifact=artifact,
        messages=[{"role": "user", "content": "path_index=0 temperature=0.39"}],
        workload_kind="SELF_CONSISTENCY",
    )
    path_1 = build_anthropic_section_cache_payload(
        section_id="unify_bullets",
        model="claude-sonnet-5",
        compiled_prompt_artifact=artifact,
        messages=[{"role": "user", "content": "path_index=1 temperature=0.44"}],
        workload_kind="SELF_CONSISTENCY",
    )

    assert path_0.stable_prefix_hash == path_1.stable_prefix_hash
    assert path_0.c0_prefix_hash == path_1.c0_prefix_hash
    assert path_0.volatile_tail_hash != path_1.volatile_tail_hash
    assert "cache_control" not in str(path_0.anthropic_payload["messages"])


def test_payload_is_deep_copied_after_build() -> None:
    rendered = build_anthropic_section_cache_payload(
        section_id="headline",
        model="claude-sonnet-5",
        compiled_prompt_artifact=_artifact(("S0", "truth oath"), ("I0", "instructions")),
    )

    returned = rendered.to_dict()
    returned["anthropic_payload"]["system"][0]["text"] = "mutated"

    assert rendered.anthropic_payload["system"][0]["text"] != "mutated"
