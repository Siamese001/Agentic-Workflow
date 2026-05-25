"""LocalVLLMProvider — LLMProvider implementation backed by QwenInferenceGateway.

Provides the ``LLMProvider`` protocol declared in
``agentic_core.L2_execution.enforcement.SovereignLLMGateway`` so that
``ProviderType.LOCAL_VLLM`` has a real provider instead of the placeholder.

Bridges the sync ``generate(system_prompt, user_prompt, tools_schema, **kwargs)``
contract expected by ``SovereignLLMGateway.generate`` to the async
``QwenInferenceGateway.infer`` at L3. Uses ``asyncio.run`` with existing-loop
detection so it is safe to call from both sync code and from code already
running inside an event loop.

Plan ref: ``.windsurf/plans/qwen-adoption-waves-a7f3c2.md`` Wave A / Phase A1.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from agentic_core.L0_routing.config.model_registry import (  # guardian: allow-layer-violation -- model registry SSOT lives in L0 config (lowest layer); QWEN_LOCAL_MODEL_ID is a canonical identifier that every layer reads, matching the same pattern as path_constants.DOCS_REPORTS_DIR
    QWEN_LOCAL_MODEL_ID,
)

_LOGGER = logging.getLogger(__name__)


def _run_async(coro: Any) -> Any:
    """Run ``coro`` to completion regardless of current event-loop state.

    If no loop is running, uses ``asyncio.run``. If a loop is already
    running (FastAPI, Jupyter, pytest-asyncio), falls back to a dedicated
    thread with a fresh loop so the caller is not re-entered.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop — cheap path.
        return asyncio.run(coro)

    # A loop is already running. Dispatch to a worker thread with its own loop.
    import threading  # noqa: PLC0415 — local import keeps module import cheap

    result: dict[str, Any] = {}

    def _worker() -> None:
        loop = asyncio.new_event_loop()
        try:
            result["value"] = loop.run_until_complete(coro)
        except (
            BaseException
        ) as exc:  # guardian: allow-broad-catch -- propagate worker exception back to caller thread
            result["error"] = exc
        finally:
            loop.close()

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    thread.join()
    if "error" in result:
        raise result["error"]
    return result.get("value")


class LocalVLLMProvider:
    """LLMProvider implementation for local vLLM serving Qwen.

    Wraps the L3 ``QwenInferenceGateway`` singleton. Concatenates the
    system and user prompts into a single Qwen prompt with explicit role
    markers (Qwen/OpenAI wire format is chat-style; the gateway's
    ``OptimizedVLLMClient`` handles tokenization).
    """

    def __init__(self, model: str | None = None, app_name: str = "sovereign_gateway") -> None:
        self._model = model or QWEN_LOCAL_MODEL_ID
        self._app_name = app_name

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        tools_schema: list[dict] | None = None,  # noqa: ARG002 — tools unused until vLLM tool-call is wired
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a response via the local vLLM Qwen gateway.

        Args:
            system_prompt: System / role prompt.
            user_prompt: User turn prompt.
            tools_schema: Unused today; local vLLM tool-calling is tracked
                separately.
            **kwargs: Forwarded to ``QwenInferenceRequest``
                (``max_tokens``, ``temperature``, ``use_cache``).

        Returns:
            ``{"content": str, "tokens_used": int, "model": str, "success": bool,
               "cached": bool, "latency_ms": float, "confidence": float}``.

        Raises:
            RuntimeError: If gateway initialization or inference fails.
        """
        # Import locally to avoid circular imports at module load time.
        from agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway import (  # noqa: PLC0415
            QwenInferenceRequest,
            get_qwen_inference_gateway,
        )

        raw_messages = kwargs.get("messages")
        if raw_messages is not None:
            msg_tuple = tuple(dict(m) for m in raw_messages)
            composed = ""
        else:
            msg_tuple = None
            composed = self._compose_prompt(system_prompt, user_prompt)

        request = QwenInferenceRequest(
            app_name=self._app_name,
            prompt=composed,
            messages=msg_tuple,
            max_tokens=int(kwargs.get("max_tokens", 2048)),
            temperature=float(kwargs.get("temperature", 0.1)),
            use_cache=bool(kwargs.get("use_cache", True)),
            confidence_threshold=float(kwargs.get("confidence_threshold", 0.7)),
        )

        observed_transport = {
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "use_cache": request.use_cache,
            "confidence_threshold": request.confidence_threshold,
        }

        async def _run() -> Any:
            gateway = await get_qwen_inference_gateway(model_id=self._model)
            return await gateway.infer(request)

        response = _run_async(_run())

        if not response.success:
            raise RuntimeError(
                f"LocalVLLMProvider inference failed: {response.error_message or 'unknown error'}",
            )

        out: dict[str, Any] = {
            "content": response.response or "",
            "tokens_used": response.tokens_used,
            "model": response.model_used,
            "success": True,
            "cached": response.cached,
            "latency_ms": response.latency_ms,
            "confidence": response.confidence,
            "_reasoning_transport_observed": observed_transport,
        }
        if msg_tuple is not None:
            out["messages"] = list(msg_tuple)
        return out

    def reasoning_transport_kw_forwarded(self) -> frozenset[str]:
        """Names forwarded into ``QwenInferenceRequest`` (transport proof surface)."""

        return frozenset({"max_tokens", "temperature", "use_cache", "confidence_threshold"})

    def get_token_count(self, text: str) -> int:
        """Estimate token count for ``text``.

        Conservative ~4-chars-per-token heuristic; matches the fallback
        used by other adapters when a real tokenizer is unavailable.
        """
        if not text:
            return 0
        return max(1, len(text) // 4)

    @staticmethod
    def _compose_prompt(system_prompt: str, user_prompt: str) -> str:
        """Compose a chat-style prompt for Qwen/vLLM.

        vLLM's OpenAI-compatible endpoint accepts either a chat-formatted
        messages array or a single prompt string. Since
        ``QwenInferenceRequest`` takes a single prompt field, we render
        an explicit role-delimited string that Qwen tokenizers parse
        reliably.
        """
        system = (system_prompt or "").strip()
        user = (user_prompt or "").strip()
        if not system:
            return user
        if not user:
            return system
        # Chat-template markers Qwen2.5 tokenizers parse reliably.
        # Built from chr() to avoid embedding the pipe/angle sequence in an
        # f-string literal, which some IDE Mypy configs mis-tokenize.
        sys_open = chr(60) + chr(124) + "system" + chr(124) + chr(62)
        end_mark = chr(60) + chr(124) + "end" + chr(124) + chr(62)
        usr_open = chr(60) + chr(124) + "user" + chr(124) + chr(62)
        ast_open = chr(60) + chr(124) + "assistant" + chr(124) + chr(62)
        nl = chr(10)
        return (
            sys_open
            + nl
            + system
            + nl
            + end_mark
            + nl
            + usr_open
            + nl
            + user
            + nl
            + end_mark
            + nl
            + ast_open
            + nl
        )


__all__ = ["LocalVLLMProvider"]
