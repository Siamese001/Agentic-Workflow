from __future__ import annotations

import hashlib

from apps_rg.prompt_assembly.contracts import CompiledPromptArtifact, PromptSlotPayload, SlotAuthority
from apps_rg.runtime.providers.anthropic_section_cache_payload import MAX_ANTHROPIC_CACHE_MARKERS, build_anthropic_section_cache_payload

_LONG_STABLE = "NO FABRICATION truth oath\n" + ("stable-instruction " * 600)


def _slot(slot_id: str, content: str) -> PromptSlotPayload:
    return PromptSlotPayload(slot_id=slot_id, slot_name=slot_id, authority_class=SlotAuthority.SYSTEM_AUTHORITY, content=content, content_hash=hashlib.sha256(content.encode()).hexdigest()[:16])


def _compiled_system(slots):
    return "\n\n".join(f"<!-- SLOT: {slot_id} -->\n{content}" for slot_id, content in slots)


def _artifact(*slots, supplemental_system_tail="", compiled_system_override=None):
    slot_tuple = tuple(slots)
    system = _compiled_system(slot_tuple)
    if supplemental_system_tail:
        system = f"{system}\n\n{supplemental_system_tail}"
    if compiled_system_override is not None:
        system = compiled_system_override
    return CompiledPromptArtifact(slot_payloads=[_slot(a, b) for a, b in slot_tuple], messages=[{"role": "system", "content": system}], system_prompt=_compiled_system(slot_tuple), prompt_hash="prompt-hash")


def _blocks(payload):
    system = payload["system"]
    assert isinstance(system, list)
    return system


def _hints_by_slot(rendered):
    return {str(h["slot_id"]): h for h in rendered.cache_boundary_hints}


def test_renderer_marks_tier_boundaries_not_every_slot():
    artifact = _artifact(("S0", _LONG_STABLE), ("D0", "origin fence"), ("I0", "lane instructions"), ("C0", "stable graph proof pool"), ("E0", "approved examples"), ("Y0", "style advice"), ("U0", "target company changes per run"), ("R0", '{"type":"object"}'), ("H0", "repair note"))
    rendered = build_anthropic_section_cache_payload(section_id="competencies", model="claude-sonnet-5", compiled_prompt_artifact=artifact, messages=[*artifact.messages, {"role": "user", "content": "path_index=2 temperature=0.43"}], workload_kind="SELF_CONSISTENCY")
    hints = _hints_by_slot(rendered)
    marked = [h["slot_id"] for h in rendered.cache_boundary_hints if h["marked"]]
    assert marked == ["I0", "Y0"]
    assert hints["I0"]["ttl"] == "1h"
    assert hints["Y0"]["ttl"] == "5m"
    assert rendered.cache_marker_count == 2
    assert rendered.cache_marker_count <= MAX_ANTHROPIC_CACHE_MARKERS
    assert all("slot_id" not in block for block in _blocks(rendered.anthropic_payload))
    assert "cache_control" not in str(rendered.anthropic_payload["messages"])


def test_one_shot_c0_cannot_be_indirectly_cached_by_later_example_slots():
    common = (("S0", _LONG_STABLE), ("D0", "origin fence"), ("I0", "lane instructions"))
    first = build_anthropic_section_cache_payload(section_id="executive_summary", model="claude-sonnet-5", compiled_prompt_artifact=_artifact(*common, ("C0", "selected facts A"), ("E0", "approved examples"), ("Y0", "style advice")), workload_kind="ONE_SHOT")
    second = build_anthropic_section_cache_payload(section_id="executive_summary", model="claude-sonnet-5", compiled_prompt_artifact=_artifact(*common, ("C0", "selected facts B"), ("E0", "approved examples"), ("Y0", "style advice")), workload_kind="ONE_SHOT")
    assert [h["slot_id"] for h in first.cache_boundary_hints if h["marked"]] == ["I0"]
    assert first.cache_receipt_seed["effective_cached_prefix_hash"] == second.cache_receipt_seed["effective_cached_prefix_hash"]
    assert first.volatile_tail_hash != second.volatile_tail_hash


def test_repair_reuses_c0_and_keeps_repair_messages_volatile():
    artifact = _artifact(("S0", _LONG_STABLE), ("D0", "origin fence"), ("I0", "lane instructions"), ("C0", "selected facts"))
    one = build_anthropic_section_cache_payload(section_id="executive_summary", model="claude-sonnet-5", compiled_prompt_artifact=artifact, workload_kind="ONE_SHOT")
    repair = build_anthropic_section_cache_payload(section_id="executive_summary", model="claude-sonnet-5", compiled_prompt_artifact=artifact, messages=[*artifact.messages, {"role": "user", "content": "repair reason and prior output"}], workload_kind="REPAIR")
    assert [h["slot_id"] for h in one.cache_boundary_hints if h["marked"]] == ["I0"]
    assert [h["slot_id"] for h in repair.cache_boundary_hints if h["marked"]] == ["I0", "C0"]
    assert "cache_control" not in str(repair.anthropic_payload["messages"])


def test_post_compile_prompt_controls_are_preserved_exactly_once_and_uncached():
    supplemental = "INPUT_AUTHORITY:\n- source_fact_ids: ALLOWED_SOURCE_FACT_IDS in C0 only\n\nPRODUCT_SHAPE:\n- output must satisfy deterministic X2 gates"
    artifact = _artifact(("S0", _LONG_STABLE), ("D0", "origin fence"), ("I0", "lane instructions"), ("C0", "proof pool"), ("U0", "volatile task"), supplemental_system_tail=supplemental)
    rendered = build_anthropic_section_cache_payload(section_id="headline", model="claude-sonnet-5", compiled_prompt_artifact=artifact, workload_kind="ONE_SHOT")
    text = "\n\n".join(block["text"] for block in _blocks(rendered.anthropic_payload))
    assert text == artifact.messages[0]["content"]
    assert text.count("INPUT_AUTHORITY:") == 1
    assert _hints_by_slot(rendered)["POST_COMPILE_SYSTEM_TAIL"]["marked"] is False


def test_compiled_system_mismatch_falls_back_to_full_uncached_prompt():
    rewritten = "FULL COMPILED PROMPT WITH POST-COMPILE CONTROLS"
    artifact = _artifact(("S0", _LONG_STABLE), ("I0", "lane instructions"), compiled_system_override=rewritten)
    rendered = build_anthropic_section_cache_payload(section_id="headline", model="claude-sonnet-5", compiled_prompt_artifact=artifact, workload_kind="ONE_SHOT")
    assert _blocks(rendered.anthropic_payload) == [{"type": "text", "text": rewritten}]
    assert rendered.cache_marker_count == 0
    assert rendered.cache_strategy == "pa_compiled_system_fallback_uncached_v1"


def test_model_floor_suppresses_cache_markers_for_short_prefix():
    rendered = build_anthropic_section_cache_payload(section_id="headline", model="claude-sonnet-5", compiled_prompt_artifact=_artifact(("S0", "short oath"), ("I0", "short instructions")))
    assert rendered.cache_marker_count == 0
    assert _hints_by_slot(rendered)["I0"]["reason"] == "below_model_cache_floor"


def test_path_diversity_only_changes_volatile_tail_hash():
    artifact = _artifact(("S0", _LONG_STABLE), ("D0", "origin fence"), ("I0", "lane instructions"), ("C0", "same evidence pack"))
    path_0 = build_anthropic_section_cache_payload(section_id="unify_bullets", model="claude-sonnet-5", compiled_prompt_artifact=artifact, messages=[*artifact.messages, {"role": "user", "content": "path_index=0 temperature=0.39"}], workload_kind="SELF_CONSISTENCY")
    path_1 = build_anthropic_section_cache_payload(section_id="unify_bullets", model="claude-sonnet-5", compiled_prompt_artifact=artifact, messages=[*artifact.messages, {"role": "user", "content": "path_index=1 temperature=0.44"}], workload_kind="SELF_CONSISTENCY")
    assert path_0.cache_receipt_seed["effective_cached_prefix_hash"] == path_1.cache_receipt_seed["effective_cached_prefix_hash"]
    assert path_0.volatile_tail_hash != path_1.volatile_tail_hash


def test_payload_is_deep_copied_after_build():
    rendered = build_anthropic_section_cache_payload(section_id="headline", model="claude-sonnet-5", compiled_prompt_artifact=_artifact(("S0", _LONG_STABLE), ("I0", "instructions")))
    returned = rendered.to_dict()
    returned["anthropic_payload"]["system"][0]["text"] = "mutated"
    assert rendered.anthropic_payload["system"][0]["text"] != "mutated"
