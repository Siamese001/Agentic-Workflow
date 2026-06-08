"""Adapt apps_rg PA ``CompiledPromptArtifact`` → agentic_core ``CompiledPromptArtifact``.

The PA compiler in ``apps_rg.prompt_assembly.contracts`` emits a local dataclass
shape (messages/system_prompt/…). The L2 v4 envelope expects the core runtime
contract (request_id, replay_key, compilation_hash, …). This module bridges the
two without changing PA compilation output.
"""
from __future__ import annotations

import json
import uuid
from typing import Any

from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact as CoreCompiledPromptArtifact,
    PromptBlock,
)
from apps_rg.runtime.section_model_limits import SECTION_MODEL_ID


def adapt_apps_rg_cpa_for_l2_envelope(
    local_cpa: Any,
    context: dict[str, Any],
) -> CoreCompiledPromptArtifact:
    """Project a apps_rg PA artifact into the core CPA consumed by ``run_apps_rg_l2_envelope``."""
    req = str(context.get("request_id") or "").strip()
    run = str(context.get("run_id") or "").strip()
    trace = str(context.get("trace_root") or "").strip()
    replay = getattr(local_cpa, "replay_manifest", None) or {}
    if isinstance(replay, dict):
        inp = replay.get("input") or {}
        if isinstance(inp, dict):
            req = req or str(inp.get("request_id") or "")
            run = run or str(inp.get("run_id") or "")
    if not req:
        req = f"req-{uuid.uuid4().hex[:24]}"
    if not run:
        run = f"run-{uuid.uuid4().hex[:24]}"
    if not trace:
        trace = f"trace-{uuid.uuid4().hex[:24]}"

    ph = str(getattr(local_cpa, "prompt_hash", "") or "").strip()
    compilation_hash = ph if ph.startswith("sha256:") else (f"sha256:{ph}" if ph else "sha256:pending")
    replay_key = ph or f"rk-{uuid.uuid4().hex}"

    prov = getattr(local_cpa, "provider_render_manifest", None) or {}
    if not isinstance(prov, dict):
        prov = {}
    raw_model = str(prov.get("model") or "").strip()
    _missing = ("", "unspecified", "unknown", "none")
    if not raw_model or raw_model.lower() in _missing:
        target_model = SECTION_MODEL_ID
    else:
        target_model = raw_model
    max_tok = int(prov.get("max_tokens") or 4096)
    if max_tok <= 0:
        max_tok = 4096
    if prov.get("top_p") is not None:
        top_p = float(prov.get("top_p"))
    else:
        top_p = 0.8
    top_p = max(0.0, min(top_p, 0.8))

    if prov.get("temperature") is not None:
        temperature = float(prov.get("temperature"))
    else:
        temperature = 0.1
    temperature = max(0.0, min(temperature, 0.1))

    messages = getattr(local_cpa, "messages", None) or []
    blocks: list[PromptBlock] = []
    if isinstance(messages, list) and messages:
        for i, m in enumerate(messages):
            if not isinstance(m, dict):
                continue
            role = str(m.get("role") or "system")
            content = str(m.get("content") or "")
            blocks.append(PromptBlock(role=role, content=content, block_index=i))
    else:
        sp = str(getattr(local_cpa, "system_prompt", "") or "")
        if sp.strip():
            blocks.append(PromptBlock(role="system", content=sp, block_index=0))

    system_preamble = blocks[0].content if blocks and blocks[0].role == "system" else ""
    user_instruction = ""
    if len(blocks) > 1:
        user_instruction = "\n".join(b.content for b in blocks[1:] if b.role == "user")

    lineage = getattr(local_cpa, "slot_lineage_map", None) or {}
    comp_map: dict[str, str] = {}
    if isinstance(lineage, dict):
        comp_map = {str(k): str(v) for k, v in lineage.items()}

    slot_pm = getattr(local_cpa, "component_hash_map", None)
    chm: dict[str, str] = {}
    if slot_pm is not None and hasattr(slot_pm, "to_dict"):
        try:
            chm = {str(k): str(v) for k, v in slot_pm.to_dict().items()}
        except (TypeError, ValueError):
            chm = {}

    return CoreCompiledPromptArtifact(
        request_id=req,
        run_id=run,
        app_id="apps_rg",
        trace_id=trace,
        prompt_blocks=tuple(blocks),
        system_preamble=system_preamble,
        user_instruction=user_instruction,
        assembly_timestamp="",
        schema_version="W6.0",
        target_model=target_model,
        target_provider="vllm_local",
        evidence_digest=compilation_hash,
        compilation_hash=compilation_hash,
        slot_lineage_map=comp_map,
        component_hash_map=chm,
        replay_manifest_ref=json.dumps(replay, sort_keys=True)[:512] if replay else "",
        tenant_id="apps_rg",
        sandbox_required=False,
        egress_policy_ref="",
        allowed_tools=(),
        allowed_models=(target_model,),
        allowed_networks=("localhost",),
        allowed_file_roots=(),
        max_tokens=max_tok,
        temperature=temperature,
        top_p=top_p,
        replay_key=replay_key,
        l5_certification_ref="l2-apps-rg-resume-generation-w3p5",
    )


__all__ = ["adapt_apps_rg_cpa_for_l2_envelope"]
