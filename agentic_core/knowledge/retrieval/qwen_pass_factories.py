"""Qwen-backed pass1/pass2 callable factories for the dual-pass orchestrator.

Provides drop-in Qwen implementations of the ``_Pass1Fn`` and ``_Pass2Fn``
protocols declared in
``agentic_core.knowledge.retrieval.dual_pass_citation_orchestrator``. Callers
that currently construct Anthropic-backed callables can swap these in with
no other changes to get a zero-marginal-cost local pipeline.

Use-cases
---------
* **Pass 2 (JSON shaping)** — always safe for Qwen. The task is a pure
  transformation of an already-produced answer into a schema-constrained
  JSON payload. Deterministic temp=0 config keeps output reproducible.
* **Pass 1 (grounded answer)** — appropriate for cost-sensitive retrieval
  flows where exact Anthropic-style ``<document-citation>`` blocks are NOT
  required. Qwen does not emit Anthropic-format citations; callers that
  require citation spans MUST keep pass 1 on Anthropic. When Qwen pass 1
  is used, the orchestrator's citation extraction returns empty.

Plan ref: ``.windsurf/plans/qwen-adoption-waves-a7f3c2.md`` Wave C.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

_log = logging.getLogger(__name__)


def _run_async(coro: Any) -> Any:
    """Run ``coro`` regardless of running-loop state (same pattern as Wave A)."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    import threading  # noqa: PLC0415

    result: dict[str, Any] = {}

    def _worker() -> None:
        loop = asyncio.new_event_loop()
        try:
            result["value"] = loop.run_until_complete(coro)
        except BaseException as exc:  # guardian: allow-broad-catch -- propagate worker exception back
            result["error"] = exc
        finally:
            loop.close()

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    thread.join()
    if "error" in result:
        raise result["error"]
    return result.get("value")


def build_qwen_pass2_fn(
    app_name: str = "dual_pass_orchestrator",
    temperature: float = 0.0,
    max_tokens: int = 2048,
) -> Callable[[str], str]:
    """Build a pass-2 callable backed by the local Qwen gateway.

    Pass 2 is a deterministic JSON reshape of the pass-1 grounded answer.
    Qwen-2.5-14B-Instruct-AWQ handles this reliably at temperature 0.0 and
    costs nothing per call, eliminating Haiku billing for the JSON step.

    Returns a callable matching the ``_Pass2Fn`` protocol
    (``(prompt: str) -> str``) so it plugs directly into
    ``DualPassOrchestrator(pass2_fn=...)``.
    """

    def _pass2(prompt: str) -> str:
        # Import locally to keep module load cheap and avoid L_PG->L3 cycles.
        from agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway import (  # noqa: PLC0415
            QwenInferenceRequest,
            get_qwen_inference_gateway,
        )

        request = QwenInferenceRequest(
            app_name=app_name,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            use_cache=True,
        )

        async def _run() -> Any:
            gateway = await get_qwen_inference_gateway()
            return await gateway.infer(request)

        response = _run_async(_run())
        if not response.success:
            _log.warning(
                "[build_qwen_pass2_fn] Qwen pass2 failed: %s",
                response.error_message,
            )
            return ""
        return response.response or ""

    return _pass2


def build_qwen_pass1_fn(
    app_name: str = "dual_pass_orchestrator",
    temperature: float = 0.1,
    max_tokens: int = 4096,
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Build a pass-1 callable backed by the local Qwen gateway.

    WARNING: Qwen does NOT emit Anthropic-format ``<document-citation>``
    blocks. Callers that require native citations MUST keep pass 1 on
    Anthropic. Use this factory only for cost-sensitive flows where
    citation extraction returning empty is acceptable (e.g., internal
    drafts, non-customer-facing analyses).

    The returned callable takes an Anthropic-style messages payload and
    returns a minimal Anthropic-shaped response dict:
    ``{"content": [{"type": "text", "text": ..., "citations": []}]}``.
    The orchestrator's ``extract_answer_text`` reads ``content[*].text``
    and ``extract_citations`` reads ``content[*].citations`` — both work
    correctly with this shape (citations list is simply empty).
    """

    def _pass1(payload: dict[str, Any]) -> dict[str, Any]:
        # Import locally to keep module load cheap and avoid L_PG->L3 cycles.
        from agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway import (  # noqa: PLC0415
            QwenInferenceRequest,
            get_qwen_inference_gateway,
        )

        system_prompt = payload.get("system", "") or ""
        if isinstance(system_prompt, list):
            # Anthropic accepts system as a list of content blocks. Flatten
            # to text for Qwen.
            system_prompt = "\n\n".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in system_prompt
            )

        # Flatten Anthropic messages into a single Qwen prompt. This loses
        # turn boundaries but for single-turn RAG that is acceptable.
        messages = payload.get("messages", []) or []
        parts: list[str] = [system_prompt] if system_prompt else []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if isinstance(content, list):
                content = "\n\n".join(
                    block.get("text", "") if isinstance(block, dict) else str(block)
                    for block in content
                )
            parts.append(f"[{role}]\n{content}")
        prompt_text = "\n\n".join(p for p in parts if p)

        request = QwenInferenceRequest(
            app_name=app_name,
            prompt=prompt_text,
            temperature=temperature,
            max_tokens=max_tokens,
            use_cache=True,
        )

        async def _run() -> Any:
            gateway = await get_qwen_inference_gateway()
            return await gateway.infer(request)

        response = _run_async(_run())
        if not response.success:
            _log.warning(
                "[build_qwen_pass1_fn] Qwen pass1 failed: %s",
                response.error_message,
            )
            return {
                "content": [{"type": "text", "text": "", "citations": []}],
                "stop_reason": "error",
                "model": response.model_used,
            }

        return {
            "content": [
                {
                    "type": "text",
                    "text": response.response or "",
                    "citations": [],
                },
            ],
            "stop_reason": "end_turn",
            "model": response.model_used,
        }

    return _pass1


__all__ = [
    "build_qwen_pass1_fn",
    "build_qwen_pass2_fn",
]
