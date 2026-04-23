"""Gemini SDK client — PromptMessages-aware wrapper around ``google.generativeai``.

Plan: prompt-reception-followups-a7b3c4, phase RH8B.1.

Scope
-----
The existing ``infrastructure.sdks_mcps.create_gemini_model`` factory returns a
raw ``genai.GenerativeModel``. That leaves callers responsible for projecting
structured prompt artifacts onto Gemini's native request shape (system
instruction + contents[] with role alternation). This module introduces
``GeminiClient``, the structured-prompt entry point:

- Accepts a ``PromptMessages`` IR (from phase RH2B.3).
- Projects it onto Gemini's ``system_instruction`` + ``contents`` shape.
- Returns a typed ``GeminiResponse`` carrying the raw SDK response plus
  telemetry-friendly fields (response text, prompt/candidate token counts,
  finish reason).

This client is **dependency-injection friendly**: ``GeminiClient`` accepts a
``model_factory`` callable so tests can substitute a fake without touching
environment variables or the live SDK. Production code uses
``GeminiClient.from_env()``.

Environment requirements
------------------------
One of ``GEMINI_API_KEY`` or ``GOOGLE_API_KEY`` must be set. The
``from_env`` factory reads these via the existing ``create_gemini_model``
function so there is a single source of truth for credential resolution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from agentic_core.L2_execution.reasoning.prompt_messages import PromptMessages


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"

# Slot codes that populate the Gemini ``system_instruction`` field. U0 is the
# user turn and is surfaced via ``contents``.
_SYSTEM_INSTRUCTION_CODES: tuple[str, ...] = (
    "S0",
    "I0",
    "D0",
    "C0",
    "M0",
    "H0",
)


@dataclass(frozen=True)
class GeminiResponse:
    """Typed Gemini response payload.

    Attributes
    ----------
    text : str
        The concatenated text of the first candidate.
    prompt_tokens : int | None
        Input token count reported by Gemini, if available.
    output_tokens : int | None
        Candidate (output) token count, if available.
    finish_reason : str | None
        Gemini-reported finish reason (``STOP``, ``MAX_TOKENS``, ...).
    raw : Any
        The underlying SDK response object, for callers that need access to
        candidates, safety ratings, or tool-call blocks.
    metadata : dict[str, Any]
        Free-form provenance propagated from the ``PromptMessages``.
    """

    text: str
    prompt_tokens: int | None = None
    output_tokens: int | None = None
    finish_reason: str | None = None
    raw: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


class GeminiClient:
    """PromptMessages-aware Gemini client."""

    def __init__(
        self,
        model_name: str = DEFAULT_GEMINI_MODEL,
        model_factory: Callable[[str], Any] | None = None,
    ) -> None:
        """Build a client for ``model_name``.

        Parameters
        ----------
        model_name
            The Gemini model identifier, e.g. ``gemini-2.5-flash``.
        model_factory
            Optional override for the model-construction callable. When
            ``None``, :func:`infrastructure.sdks_mcps.create_gemini_model` is
            used. Tests should supply a factory that returns a mock so no
            network / credentials are required.
        """
        self.model_name = model_name
        self._model_factory = model_factory
        self._model: Any | None = None

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_env(cls, model_name: str = DEFAULT_GEMINI_MODEL) -> GeminiClient:
        """Build a client using the env-var-backed factory.

        The ``GEMINI_API_KEY`` / ``GOOGLE_API_KEY`` lookup is delegated to
        :func:`infrastructure.sdks_mcps.create_gemini_model` so credential
        handling stays in a single location.
        """
        return cls(model_name=model_name, model_factory=None)

    # ------------------------------------------------------------------
    # Projection: PromptMessages -> Gemini request shape
    # ------------------------------------------------------------------

    @staticmethod
    def project(prompt_messages: PromptMessages) -> dict[str, Any]:
        """Project a ``PromptMessages`` onto Gemini's native request shape.

        Returns a dict with:

        - ``system_instruction``: concatenated system-authority slots.
        - ``contents``: list of ``{"role": "user"/"model", "parts": [text]}``.
          E0 exemplars (when parsed) become leading user/model turn pairs
          before the final ``user`` U0 turn.
        """
        sys_parts = [
            prompt_messages.slot_map[c]
            for c in _SYSTEM_INSTRUCTION_CODES
            if c in prompt_messages.slot_map and prompt_messages.slot_map[c]
        ]
        # Back-compat path: when the IR only carries synthetic SYSTEM/USER
        # keys (no per-slot map), use those instead.
        if not sys_parts and "SYSTEM" in prompt_messages.slot_map:
            sys_parts = [prompt_messages.slot_map["SYSTEM"]]

        system_instruction = "\n\n".join(p for p in sys_parts if p)

        contents: list[dict[str, Any]] = []
        # E0 exemplars first (if present), projected onto Gemini roles.
        for role, text in prompt_messages.exemplars:
            gemini_role = "user" if role == "user" else "model"
            contents.append({"role": gemini_role, "parts": [text]})

        user_turn = prompt_messages.user_text()
        if user_turn:
            contents.append({"role": "user", "parts": [user_turn]})

        return {
            "system_instruction": system_instruction,
            "contents": contents,
        }

    # ------------------------------------------------------------------
    # Send
    # ------------------------------------------------------------------

    def send(
        self,
        prompt_messages: PromptMessages,
        **generation_config: Any,
    ) -> GeminiResponse:
        """Send a ``PromptMessages`` request and return a typed response.

        Parameters
        ----------
        prompt_messages
            Structured slot envelope from the assembly stage.
        **generation_config
            Forwarded to the underlying SDK's ``generate_content`` call
            (``temperature``, ``max_output_tokens``, ``top_p`` ...).
        """
        model = self._resolve_model()
        request = self.project(prompt_messages)

        raw = model.generate_content(
            contents=request["contents"],
            system_instruction=request["system_instruction"] or None,
            generation_config=generation_config or None,
        )

        return self._parse_response(raw, prompt_messages)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _resolve_model(self) -> Any:
        if self._model is not None:
            return self._model
        if self._model_factory is not None:
            self._model = self._model_factory(self.model_name)
        else:
            # Local import to avoid dragging the SDK in at module-load.
            from infrastructure.sdks_mcps import create_gemini_model

            self._model = create_gemini_model(self.model_name)
        return self._model

    @staticmethod
    def _parse_response(raw: Any, ir: PromptMessages) -> GeminiResponse:
        """Extract text + token counts + finish reason from the SDK response.

        Tolerant of mock responses that only provide a ``text`` attribute.
        """
        text = getattr(raw, "text", "")
        usage = getattr(raw, "usage_metadata", None)
        prompt_tokens = getattr(usage, "prompt_token_count", None) if usage else None
        output_tokens = getattr(usage, "candidates_token_count", None) if usage else None

        candidates = getattr(raw, "candidates", None) or []
        finish_reason: str | None = None
        if candidates:
            finish_reason = getattr(candidates[0], "finish_reason", None)
            # finish_reason may be an enum; stringify for telemetry-friendliness.
            if finish_reason is not None and not isinstance(finish_reason, str):
                finish_reason = getattr(finish_reason, "name", str(finish_reason))

        return GeminiResponse(
            text=text or "",
            prompt_tokens=prompt_tokens,
            output_tokens=output_tokens,
            finish_reason=finish_reason,
            raw=raw,
            metadata=dict(ir.metadata),
        )


__all__ = [
    "DEFAULT_GEMINI_MODEL",
    "GeminiClient",
    "GeminiResponse",
]
