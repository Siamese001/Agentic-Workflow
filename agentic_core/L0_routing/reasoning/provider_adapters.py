"""PA.6 — Provider-Aware Rendering Adapters.

Renders the structured slot dict produced by `AirlockAssembler.assemble_from_bom`
into provider-specific wire format. Each adapter is pure, deterministic, and
takes (system_string, user_string, slots) plus a provider hint. The
CompiledPromptArtifact and replay-key inputs remain unchanged — this is a
downstream rendering pass.

Doctrinal anchor: docs/reference/03_L0_Routing/Prompt Assembly/Prompt_Assembly_detailed.md PA.6
Plan: prompt-assembly-best-practices-gap-b4e1c2 W2 (G2)

Adapters supported:
  - AnthropicAdapter  — XML-tagged slots (<system>, <instructions>, <context>)
  - OpenAIAdapter     — role-split messages (system/developer/user) per o-series
  - GeminiAdapter     — markdown-headed sections (## Identity, ## Context, ...)
  - PassthroughAdapter — returns the legacy concatenated string unchanged

Determinism contract:
  - Same input slots → same output bytes (no randomness, no clock reads)
  - Adapter version is part of the rendered envelope so consumers can detect
    rendering shifts without re-hashing the upstream artifact.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


# Slot-rendering order is provider-agnostic; deviations live inside each adapter.
_CANONICAL_RENDER_ORDER: tuple[str, ...] = (
    "S0",  # Identity / system
    "D0",  # Developer / domain constraints
    "I0",  # Instructions / mixins
    "E0",  # Exemplars (few-shot)
    "C0",  # Context / retrieved evidence
    "M0",  # Meta-cognitive scaffolds
    "Y0",  # Tool-policy slot
    "R0",  # Response-format schema (structured output)
    "U0",  # User turn
    "H0",  # Healing re-entry payload (lives with user)
)

# Slots that always render to the system/instructions plane.
_SYSTEM_PLANE_SLOTS: frozenset[str] = frozenset({"S0", "D0", "I0", "E0", "C0", "M0", "Y0", "R0"})

# Slots that always render to the user/untrusted plane.
_USER_PLANE_SLOTS: frozenset[str] = frozenset({"U0", "H0"})

# OpenAI o-series header for re-enabling markdown output (G4).
_OPENAI_FORMATTING_HEADER: str = "Formatting re-enabled\n"


@dataclass(frozen=True)
class RenderedPrompt:
    """Provider-rendered prompt envelope.

    Attributes:
        provider: Adapter identifier ("anthropic"|"openai"|"gemini"|"passthrough").
        adapter_version: Semver of the adapter used. Part of replay metadata.
        system: System-plane payload as a single string. May be empty for
                providers that don't use a separate system field.
        messages: For role-split providers (OpenAI), the typed message list.
                  Empty tuple for adapters that emit a single string.
        user: User-plane payload as a single string. Always present.
        rendered_chars: Total character count of the wire payload.
    """

    provider: str
    adapter_version: str
    system: str
    user: str
    messages: tuple[dict[str, str], ...] = field(default_factory=tuple)
    rendered_chars: int = 0


class ProviderAdapter(Protocol):
    """Adapter contract — render structured slots into provider format."""

    provider_id: str
    version: str

    def render(self, slots: dict[str, str]) -> RenderedPrompt:
        """Render slots → RenderedPrompt. MUST be deterministic."""
        ...


# --------------------------------------------------------------------------
# Anthropic adapter — XML tags for clear instruction/context separation.
# --------------------------------------------------------------------------


class AnthropicAdapter:
    """Render slots with Anthropic XML conventions (per Anthropic A1, A4)."""

    provider_id: str = "anthropic"
    version: str = "1.0.0"

    # XML tag names per Anthropic best-practice corpus.
    _XML_TAGS: dict[str, str] = {
        "S0": "identity",
        "D0": "domain_constraints",
        "I0": "instructions",
        "E0": "examples",
        "C0": "context",
        "M0": "meta_cognitive",
        "Y0": "tool_policy",
        "R0": "response_format",
    }

    def render(self, slots: dict[str, str]) -> RenderedPrompt:
        """Render system slots as XML-tagged blocks; user is plain."""
        system_parts: list[str] = []
        for slot_name in _CANONICAL_RENDER_ORDER:
            if slot_name not in _SYSTEM_PLANE_SLOTS:
                continue
            content = slots.get(slot_name, "").strip()
            if not content:
                continue
            tag = self._XML_TAGS.get(slot_name, slot_name.lower())
            # Anthropic A4 multi-doc convention for C0
            if slot_name == "C0":
                system_parts.append(self._wrap_documents(content))
            else:
                system_parts.append(f"<{tag}>\n{content}\n</{tag}>")

        system_str = "\n\n".join(system_parts)

        # User plane: U0 + optional H0 inside <healing_reentry>
        u0 = slots.get("U0", "").strip()
        h0 = slots.get("H0", "").strip()
        if h0:
            user_str = f"{u0}\n\n<healing_reentry>\n{h0}\n</healing_reentry>" if u0 else h0
        else:
            user_str = u0

        return RenderedPrompt(
            provider=self.provider_id,
            adapter_version=self.version,
            system=system_str,
            user=user_str,
            rendered_chars=len(system_str) + len(user_str),
        )

    @staticmethod
    def _wrap_documents(c0_content: str) -> str:
        """Wrap C0 content as Anthropic <documents><document index=N>... pattern.

        If the content already contains <documents>, pass through to allow
        callers to control multi-doc structure explicitly.
        """
        if "<documents>" in c0_content or "<document " in c0_content:
            return f"<context>\n{c0_content}\n</context>"
        # Single-doc default wrapping
        return (
            "<documents>\n"
            "  <document index='1'>\n"
            "    <document_content>\n"
            f"{c0_content}\n"
            "    </document_content>\n"
            "  </document>\n"
            "</documents>"
        )


# --------------------------------------------------------------------------
# OpenAI adapter — role-split messages with developer/system separation.
# --------------------------------------------------------------------------


class OpenAIAdapter:
    """Render slots as OpenAI message list (per OpenAI O1/O2 + o-series)."""

    provider_id: str = "openai"
    version: str = "1.0.0"

    def __init__(self, *, model_family: str = "gpt-4", markdown_output: bool = False):
        """Initialize adapter.

        Args:
            model_family: Either 'gpt-4' (system role) or 'o-series' (developer role).
            markdown_output: If True and model is o-series, prepends
                'Formatting re-enabled' header (per OpenAI G4 caveat).
        """
        self.model_family = model_family.lower()
        self.markdown_output = markdown_output

    def render(self, slots: dict[str, str]) -> RenderedPrompt:
        """Render slots into role-split OpenAI message list."""
        # Identity (S0) goes into system or developer role.
        s0 = slots.get("S0", "").strip()
        # Other system-plane slots become a single developer-role payload
        # so o-series can still see them while system stays minimal.
        dev_parts: list[str] = []
        for slot_name in ("D0", "I0", "E0", "M0", "Y0", "R0"):
            content = slots.get(slot_name, "").strip()
            if content:
                # Markdown headers per OpenAI O1 "Output Format" pattern
                section = self._slot_to_section(slot_name)
                dev_parts.append(f"## {section}\n{content}")

        # C0 evidence — per OpenAI O3, place context BEFORE the question
        c0 = slots.get("C0", "").strip()
        if c0:
            dev_parts.append(f"## Context\n{c0}")

        dev_payload = "\n\n".join(dev_parts)
        if self.markdown_output and self.model_family.startswith(("o1", "o3", "o4", "o-series")):
            dev_payload = _OPENAI_FORMATTING_HEADER + dev_payload

        # User plane
        u0 = slots.get("U0", "").strip()
        h0 = slots.get("H0", "").strip()
        user_payload = f"{u0}\n\n[healing_reentry]\n{h0}" if h0 and u0 else (u0 or h0)

        # Determine role for the system-identity message
        identity_role = (
            "developer" if self.model_family.startswith(("o1", "o3", "o4", "o-series")) else "system"
        )

        messages: list[dict[str, str]] = []
        if s0:
            messages.append({"role": identity_role, "content": s0})
        if dev_payload:
            # For non-o-series, dev_payload still goes to system (combined)
            target_role = "developer" if identity_role == "developer" else "system"
            messages.append({"role": target_role, "content": dev_payload})
        if user_payload:
            messages.append({"role": "user", "content": user_payload})

        # Concatenated form for callers that don't consume messages
        system_str = "\n\n".join(m["content"] for m in messages if m["role"] != "user")
        user_str = user_payload

        return RenderedPrompt(
            provider=self.provider_id,
            adapter_version=self.version,
            system=system_str,
            user=user_str,
            messages=tuple(messages),
            rendered_chars=sum(len(m["content"]) for m in messages),
        )

    @staticmethod
    def _slot_to_section(slot_name: str) -> str:
        """Map slot id to OpenAI markdown section header."""
        return {
            "D0": "Domain Constraints",
            "I0": "Instructions",
            "E0": "Examples",
            "M0": "Reasoning Approach",
            "Y0": "Tool Policy",
            "R0": "Output Format",
        }.get(slot_name, slot_name)


# --------------------------------------------------------------------------
# Gemini adapter — markdown-headed sections (per Google G1, G6).
# --------------------------------------------------------------------------


class GeminiAdapter:
    """Render slots as markdown-headed sections (per Google Gemini conventions)."""

    provider_id: str = "gemini"
    version: str = "1.0.0"

    def render(self, slots: dict[str, str]) -> RenderedPrompt:
        """Render system-plane slots as markdown sections."""
        sections: list[str] = []
        section_titles = {
            "S0": "Identity",
            "D0": "Constraints",
            "I0": "Instructions",
            "E0": "Examples",
            "C0": "Context",
            "M0": "Reasoning Approach",
            "Y0": "Tool Policy",
            "R0": "Output Format",
        }
        for slot_name in _CANONICAL_RENDER_ORDER:
            if slot_name not in _SYSTEM_PLANE_SLOTS:
                continue
            content = slots.get(slot_name, "").strip()
            if not content:
                continue
            title = section_titles.get(slot_name, slot_name)
            sections.append(f"## {title}\n\n{content}")

        system_str = "\n\n".join(sections)

        u0 = slots.get("U0", "").strip()
        h0 = slots.get("H0", "").strip()
        if h0:
            user_str = f"{u0}\n\n## Healing Re-entry\n\n{h0}" if u0 else f"## Healing Re-entry\n\n{h0}"
        else:
            user_str = u0

        return RenderedPrompt(
            provider=self.provider_id,
            adapter_version=self.version,
            system=system_str,
            user=user_str,
            rendered_chars=len(system_str) + len(user_str),
        )


# --------------------------------------------------------------------------
# Passthrough adapter — preserves legacy concat behavior.
# --------------------------------------------------------------------------


class PassthroughAdapter:
    """No-op adapter — returns legacy "\\n\\n".join concatenation unchanged.

    Used when no provider hint is available or the caller explicitly opts out.
    Preserves replay-key determinism for pre-PA.6 callers.
    """

    provider_id: str = "passthrough"
    version: str = "1.0.0"

    def render(self, slots: dict[str, str]) -> RenderedPrompt:
        system_parts: list[str] = []
        for slot_name in _CANONICAL_RENDER_ORDER:
            if slot_name not in _SYSTEM_PLANE_SLOTS:
                continue
            content = slots.get(slot_name, "").strip()
            if content:
                system_parts.append(content)
        system_str = "\n\n".join(system_parts)
        u0 = slots.get("U0", "").strip()
        h0 = slots.get("H0", "").strip()
        user_str = f"{u0}\n\n<H0>\n{h0}\n</H0>" if h0 and u0 else (u0 or h0)

        return RenderedPrompt(
            provider=self.provider_id,
            adapter_version=self.version,
            system=system_str,
            user=user_str,
            rendered_chars=len(system_str) + len(user_str),
        )


# --------------------------------------------------------------------------
# Adapter registry + factory.
# --------------------------------------------------------------------------


_ADAPTER_REGISTRY: dict[str, type] = {
    "anthropic": AnthropicAdapter,
    "claude": AnthropicAdapter,
    "openai": OpenAIAdapter,
    "gpt": OpenAIAdapter,
    "o1": OpenAIAdapter,
    "o3": OpenAIAdapter,
    "o4": OpenAIAdapter,
    "gemini": GeminiAdapter,
    "google": GeminiAdapter,
    "passthrough": PassthroughAdapter,
    "": PassthroughAdapter,
}


def get_adapter(provider: str | None = None, **kwargs: Any) -> ProviderAdapter:
    """Resolve a provider hint to an adapter instance.

    Args:
        provider: Provider name. Common variants: 'anthropic', 'claude-3.5',
                  'openai', 'gpt-4', 'o1', 'gemini', 'google'.
                  None → PassthroughAdapter.
        **kwargs: Adapter-specific options (e.g. model_family, markdown_output
                  for OpenAIAdapter).

    Returns:
        Instantiated adapter implementing the ProviderAdapter protocol.
    """
    if not provider:
        return PassthroughAdapter()
    prov = provider.lower()
    # Match by prefix to handle versioned names like 'claude-3.5-sonnet'
    for key, adapter_cls in _ADAPTER_REGISTRY.items():
        if key and prov.startswith(key):
            if adapter_cls is OpenAIAdapter:
                # Detect o-series for role-split treatment
                if prov.startswith(("o1", "o3", "o4")):
                    kwargs.setdefault("model_family", "o-series")
                else:
                    kwargs.setdefault("model_family", "gpt-4")
                return adapter_cls(**kwargs)
            return adapter_cls()
    return PassthroughAdapter()


def render_for_provider(
    slots: dict[str, str], provider: str | None = None, **adapter_kwargs: Any
) -> RenderedPrompt:
    """Convenience: resolve adapter + render in one call.

    Deterministic given identical inputs. Caller is responsible for ensuring
    `slots` is the same shape as what AirlockAssembler emits.
    """
    adapter = get_adapter(provider, **adapter_kwargs)
    return adapter.render(slots)
