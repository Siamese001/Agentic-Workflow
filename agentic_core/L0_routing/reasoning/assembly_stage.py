"""
Assembly Stage - GAP-03 Implementation
Deterministic composition of governed payloads with stable slot ordering.

This module implements the Assembly Stage that composes system, instructional,
context, and user prompts into a governed payload with deterministic hashing.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.L0_routing.utils.elevator_shaft_seam import load_context_jit
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    emit_determinism_digest,
    emit_replay_key,
)
from tqdm import tqdm


# Lazy imports to avoid L0->L_PG gravity violations
def _get_prompt_bom():
    from agentic_core.prompt_governance.contracts import PromptBOM

    return PromptBOM


def _get_compiled_artifact():
    # Post-RH2B.2 merge: the narrow governance variant is now an alias for the
    # rich L2 CompiledPromptArtifact. The import path is preserved for
    # back-compat; it resolves to the canonical class.
    from agentic_core.prompt_governance.contracts.compiled_artifact_types import CompiledPromptArtifact

    return CompiledPromptArtifact


def _get_neutralizer():
    from agentic_core.prompt_governance.security.assembly_injection_neutralizer import (
        AssemblyInjectionNeutralizer,
    )

    return AssemblyInjectionNeutralizer


def _validate_slot_order(*args, **kwargs):
    from agentic_core.prompt_governance.validation.validate_assembly import validate_slot_order

    return validate_slot_order(*args, **kwargs)


# ---------------------------------------------------------------------------
# EQ-3 — optional-slot helpers. Kept at module level so assemble_from_bom
# (a @staticmethod) can reference them without circular indirection, and
# so tests can stub the registry surface.
# ---------------------------------------------------------------------------


def _load_exemplars(registry: Any, exemplar_ids: tuple[str, ...]) -> str:
    """Load E0 exemplar content from the template registry.

    Uses ``registry.get_e0_exemplar(id)`` when present; otherwise falls back
    to ``registry.get_i0_mixin(id)`` so existing mixin-backed exemplar
    content still resolves during the EQ-3 shim window. Returns empty
    string when no exemplars are requested.
    """
    if not exemplar_ids:
        return ""
    getter = getattr(registry, "get_e0_exemplar", None) or getattr(
        registry, "get_i0_mixin", None
    )
    if getter is None:
        return ""
    parts: list[str] = []
    for ex_id in sorted(exemplar_ids):
        try:
            content = getter(ex_id)
        except KeyError:
            # Missing exemplar is non-fatal — absent content means slot stays empty.
            continue
        if content:
            parts.append(content)
    return "\n\n".join(parts)


def _load_meta_cognitive(registry: Any, mixin_id: str | None) -> str:
    """Load M0 meta-cognitive mixin content by ID.

    Routes through the same I0 mixin catalog (M0 is authored as a mixin
    with the ``thinking`` tag convention). Returns empty string when the
    BOM does not request one.
    """
    if not mixin_id:
        return ""
    getter = getattr(registry, "get_m0_mixin", None) or getattr(
        registry, "get_i0_mixin", None
    )
    if getter is None:
        return ""
    try:
        return getter(mixin_id) or ""
    except KeyError:
        return ""


def _build_structured_slots(
    slots: dict[str, str], u0_clean: str
) -> dict[str, Any] | None:
    """Construct ``CompiledPromptArtifact.structured_slots`` from flat content.

    Produces one :class:`AuthoritySlot` per populated slot code. Empty slot
    content is skipped entirely so the adapter surface only sees live data.
    Returns ``None`` when no structured slots were populated, which tells
    the artifact to fall back to the flat-string manifest-hash path (EQ-1).
    """
    from agentic_core.L2_execution.reasoning.compiled_artifact import (  # guardian: allow-layer-violation -- L0 assembly stage reads L2 compiled-artifact types to build structured AuthoritySlot records; the types are defined in L2 to keep them co-located with the artifact emitter, and L0 is the boundary-inversion caller
        AuthorityLevel,
        AuthoritySlot,
    )

    source_layer_by_slot = {
        "S0": "L4",
        "D0": "L5",
        "I0": "L4",
        "E0": "L4",
        "C0": "L1",
        "M0": "L4",
        "U0": "L1",
        "H0": "L2",
    }
    level_by_slot = {
        "S0": AuthorityLevel.ABSOLUTE,
        "D0": AuthorityLevel.BINDING,
        "I0": AuthorityLevel.GOVERNED,
        "E0": AuthorityLevel.EXEMPLAR,
        "C0": AuthorityLevel.INFO,
        "M0": AuthorityLevel.META_COGNITIVE,
        "U0": AuthorityLevel.ZERO,
        "H0": AuthorityLevel.HEALING,
    }

    structured: dict[str, Any] = {}
    for code, content in slots.items():
        # Normalize U0 to the post-neutralizer string so the structured
        # surface matches what the adapter actually renders.
        effective = u0_clean if code == "U0" else content
        if not effective:
            continue
        structured[code] = AuthoritySlot(
            slot_type=code,
            content=effective,
            authority_level=level_by_slot[code],
            source_layer=source_layer_by_slot[code],
        )
    return structured or None


# Rest of the existing file content continues...


def canonical_bytes(data: dict[str, Any]) -> bytes:
    """
    Convert a dictionary to canonical JSON bytes for deterministic hashing.

    Args:
        data: Dictionary to canonicalize

    Returns:
        Deterministic bytes representation
    """
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True)
class GovernedPayload:
    """
    Immutable governed payload with assembly stage slots.

    Slots are ordered S0→D0→I0→C0→U0 for deterministic manifest hashing.
    """

    s0_system: str
    i0_instructional: str
    c0_context: str
    u0_user_prompt: str
    d0_injections: str = ""
    check_ids: tuple[str, ...] = ()
    sanitized: bool = False
    c0_context_source: str = "static"
    manifest_hash: str = ""
    routing_hash: str = ""

    def __post_init__(self):
        import logging as _logging

        _logger = _logging.getLogger(__name__)
        if self.s0_system and self.u0_user_prompt and not self.d0_injections:
            _logger.warning(
                "MISSING_D0_FENCE: GovernedPayload assembled with S0+U0 but no D0 injection fence. "
                "This is a prompt injection risk. Add d0_injections to guard against user prompt "
                "overriding system constitution. manifest_hash=%s",
                self.manifest_hash or "<pending>",
            )
        if not self.manifest_hash or not self.routing_hash:
            manifest = {
                "s0_system": self.s0_system,
                "d0_injections": self.d0_injections,
                "i0_instructional": self.i0_instructional,
                "c0_context": self.c0_context,
                "u0_user_prompt": self.u0_user_prompt,
                "check_ids": tuple(sorted(self.check_ids)),
                "sanitized": self.sanitized,
                "c0_context_source": self.c0_context_source,
            }
            manifest_hash_hex = hashlib.sha256(canonical_bytes(manifest)).hexdigest()
            object.__setattr__(self, "manifest_hash", manifest_hash_hex)
            routing_manifest = {
                "s0_system": self.s0_system,
                "d0_injections": self.d0_injections,
                "i0_instructional": self.i0_instructional,
                "u0_user_prompt": self.u0_user_prompt,
                "check_ids": tuple(sorted(self.check_ids)),
                "sanitized": self.sanitized,
            }
            routing_hash_hex = hashlib.sha256(canonical_bytes(routing_manifest)).hexdigest()
            object.__setattr__(self, "routing_hash", routing_hash_hex)


class AirlockAssembler:
    """
    Assembly stage for composing governed payloads with deterministic hashing.

    Implements the Assembly Stage (GAP-03) with stable slot composition
    and deterministic manifest hashing.
    """

    @staticmethod
    def _sanitize(u0_user_prompt: str) -> str:
        """
        Deterministic minimal sanitizer for user prompts.

        Performs exact, deterministic substitutions only - no ML or fuzzy matching.

        Args:
            u0_user_prompt: Raw user prompt text

        Returns:
            Sanitized user prompt text
        """
        sanitized = u0_user_prompt
        sanitized = sanitized.replace("\x00", "")
        sanitized = sanitized.replace("\r\n", "\n").replace("\r", "\n")
        hijack_patterns = [
            ("[SYSTEM]", ""),
            ("[ADMIN]", ""),
            ("[ROOT]", ""),
            ("[ESCALATE]", ""),
            ("[BYPASS]", ""),
            ("[OVERRIDE]", ""),
        ]
        for pattern, replacement in hijack_patterns:
            sanitized = sanitized.replace(pattern, replacement)
        return sanitized

    @staticmethod
    def _shred(u0_user_prompt: str) -> tuple[str, ...]:
        """
        Deterministic shred of user prompt into atomic intent check IDs.

        Splits by common intent delimiters and returns lexicographically sorted IDs.

        Args:
            u0_user_prompt: User prompt text to shred

        Returns:
            Tuple of stable, lexicographically sorted check IDs
        """
        lines = u0_user_prompt.strip().split("\n")
        check_ids = []
        for line in tqdm(lines, desc="Processing", unit="item"):
            line = line.strip()
            if not line:
                continue
            if line and line[0].isdigit() and ("." in line[:10]):
                check_id = line.split(".", 1)[1].strip()
                if check_id:
                    check_ids.append(check_id)
            elif line.startswith(("-", "*", "•")):
                check_id = line[1:].strip()
                if check_id:
                    check_ids.append(check_id)
            else:
                check_ids.append(line)
        return tuple(sorted(check_ids))

    @staticmethod
    def assemble(
        *,
        s0_system: str,
        i0_instructional: str,
        c0_context: str,
        u0_user_prompt: str,
        d0_injections: str = "",
        c0_context_source: Literal["static", "embedding_artifact"] = "static",
    ) -> GovernedPayload:
        """
        Assemble a governed payload from component slots.

        Performs sanitization first, then shredding, then computes manifest hash.

        Args:
            s0_system: System prompt slot
            d0_injections: Reserved injection slot (default empty)
            i0_instructional: Instructional prompt slot
            c0_context: Context slot
            u0_user_prompt: User prompt slot

        Returns:
            GovernedPayload with deterministic manifest hash
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "AirlockAssembler.assemble")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        sanitized_prompt = AirlockAssembler._sanitize(u0_user_prompt)
        sanitized = sanitized_prompt != u0_user_prompt
        check_ids = AirlockAssembler._shred(sanitized_prompt)
        payload = GovernedPayload(
            s0_system=s0_system,
            d0_injections=d0_injections,
            i0_instructional=i0_instructional,
            c0_context=c0_context,
            u0_user_prompt=sanitized_prompt,
            check_ids=check_ids,
            sanitized=sanitized,
            c0_context_source=c0_context_source,
        )
        return payload

    @staticmethod
    def assemble_from_bom(
        bom: PromptBOM,
        secret_key: bytes,
        d0_fences: tuple[str, ...] = (),
        s0_override: str | None = None,
        allowed_tools: tuple[Any, ...] = (),
    ) -> CompiledPromptArtifact:
        """Assemble CompiledPromptArtifact from PromptBOM.

        This is the canonical entry point for the governed prompt lifecycle.
        Wires together L4 TemplateRegistry, L0 ElevatorShaft, L_PG validators.

        Slot Assembly Order: S0 → D0 → I0 → C0 → U0

        Args:
            bom: PromptBOM from PromptBOMBuilder.
            secret_key: HMAC secret key for artifact signing.
            d0_fences: Optional D0 injection fences.
            s0_override: Optional S0 string that replaces the registry-sourced
                S0. Used by callers that already own their system prompt (e.g.
                `GovernedPromptAdapter` in apps_shared). When None, S0 is
                loaded from `TemplateRegistry.get_s0(bom.system_version_hash)`.
            allowed_tools: Tool schemas to publish on the artifact. Must be an
                immutable tuple. Defaults to empty for gateway-level control.

        Returns:
            CompiledPromptArtifact with HMAC-SHA256 signature.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L0_ROUTING,
            "AirlockAssembler.assemble_from_bom",
        )
        emit_replay_key(_trace_id, f"artifact:{bom.trace_id}")
        emit_determinism_digest(_trace_id, f"path:{bom.path}")

        # 1. Load S0 — caller override wins, otherwise pull from TemplateRegistry
        from agentic_core.L4_state.utils.memory.template_registry import get_template_registry

        registry = get_template_registry()
        if s0_override is not None:
            s0_content = s0_override
        else:
            s0_content = registry.get_s0(bom.system_version_hash)

        # 1b. Pull registry-sourced D0 fences when caller did not supply any.
        #     Keeps a single SSOT for injection defense (P2.1 — gap G3).
        if not d0_fences:
            d0_fences = registry.get_d0_fences(bom.system_version_hash)

        # 2. Load I0 mixins
        i0_parts = []
        for mixin_id in sorted(bom.mixins_required):
            mixin_content = registry.get_i0_mixin(mixin_id)
            i0_parts.append(mixin_content)
        i0_content = "\n\n".join(i0_parts)

        # 3. Load C0 via ElevatorShaft JIT context loading
        c0_context = load_context_jit(
            trace_id=bom.trace_id,
            intent_class=bom.template_args.get("intent_class", "default"),
        )
        c0_content = str(c0_context)

        # 4. Wrap U0
        u0_content = f"<U0>\n{bom.raw_u0}\n</U0>"

        # 5. Render D0 fences
        d0_content = ""
        if d0_fences:
            d0_lines = ["<D0>"]
            for fence in sorted(d0_fences):
                d0_lines.append(f"  {fence}")
            d0_lines.append("</D0>")
            d0_content = "\n".join(d0_lines)

        # 5b. EQ-3 — Load E0 exemplars, M0 meta-cognitive mixin, H0 healing
        # context when the BOM carries them. All three paths are additive:
        # missing fields leave the corresponding slot empty, preserving the
        # legacy 5-slot behavior for callers that have not opted in.
        e0_content = _load_exemplars(registry, bom.exemplars_required)
        m0_content = _load_meta_cognitive(
            registry, getattr(bom, "meta_cognitive_mixin_id", None)
        )
        h0_content = getattr(bom, "healing_context", None) or ""

        # 6. Validate slot order (S0→D0→I0→E0→C0→M0→U0→H0). E0/M0/H0 are
        # optional — validator only checks present slots are in canonical
        # position relative to each other.
        slots = {
            "S0": s0_content,
            "D0": d0_content,
            "I0": i0_content,
            "E0": e0_content,
            "C0": c0_content,
            "M0": m0_content,
            "U0": u0_content,
            "H0": h0_content,
        }
        slot_order = [
            {"name": "S0", "order": 0},
            {"name": "D0", "order": 1},
            {"name": "I0", "order": 2},
            {"name": "C0", "order": 3},
            {"name": "U0", "order": 4},
        ]
        is_valid, errors = validate_slot_order(slot_order)
        if not is_valid:
            raise ValueError(f"Invalid slot order: {errors}")

        # 7. Run injection neutralizer on U0
        neutralizer = AssemblyInjectionNeutralizer()
        u0_clean = neutralizer.neutralize(u0_content)

        # 8. Assemble final strings. Optional slots appear in canonical
        # order between C0 and U0 for flat-string consumers. Structured
        # consumers (provider adapters in EQ-2) should use
        # CompiledPromptArtifact.structured_slots instead.
        system_parts = [
            p
            for p in [s0_content, d0_content, i0_content, e0_content, c0_content, m0_content]
            if p
        ]
        final_system = "\n\n".join(system_parts)
        final_user = u0_clean
        if h0_content:
            # Healing context travels with the user turn so the re-entry
            # path keeps it inside the untrusted-content plane rather than
            # silently hoisting to system.
            final_user = f"{final_user}\n\n<H0>\n{h0_content}\n</H0>"

        # 9. Estimate tokens (rough approximation: 4 chars ≈ 1 token)
        token_estimate = (len(final_system) + len(final_user)) // 4

        # 10. Build structured_slots for EQ-2 provider adapters.
        structured = _build_structured_slots(slots, u0_clean)

        # 11. Build artifact and sign (post-RH2B.2: rich SSOT variant)
        slots_used = [
            code
            for code in ("S0", "D0", "I0", "E0", "C0", "M0", "U0", "H0")
            if slots.get(code)
        ]
        unsigned_artifact = CompiledPromptArtifact(
            trace_id=bom.trace_id,
            system_version_hash=bom.system_version_hash,
            final_system_string=final_system,
            final_user_string=final_user,
            allowed_tools_schema=list(allowed_tools),  # Caller-supplied; list per rich contract.
            tokens=token_estimate,
            slots_used=slots_used,
            signature="",  # Placeholder, computed below via rich's built-in scheme.
            structured_slots=structured,
        )

        # Compute HMAC-SHA256 via the rich variant's canonical scheme.
        # Note: this differs from the pre-merge narrow scheme; no downstream
        # consumer relies on the pre-merge scheme operationally.
        signature = unsigned_artifact._compute_signature(secret_key)

        # Return signed artifact (dataclass replace keeps all other fields identical).
        from dataclasses import replace as _replace

        return _replace(unsigned_artifact, signature=signature)
