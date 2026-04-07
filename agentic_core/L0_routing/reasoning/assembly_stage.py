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


# Lazy imports to avoid L0->L_PG gravity violations
def _get_prompt_bom():
    from agentic_core.prompt_governance.contracts import PromptBOM
    return PromptBOM

def _get_compiled_artifact():
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
        for line in lines:
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
    ) -> CompiledPromptArtifact:
        """Assemble CompiledPromptArtifact from PromptBOM.

        This is the canonical entry point for the governed prompt lifecycle.
        Wires together L4 TemplateRegistry, L0 ElevatorShaft, L_PG validators.

        Slot Assembly Order: S0 → D0 → I0 → C0 → U0

        Args:
            bom: PromptBOM from PromptBOMBuilder.
            secret_key: HMAC secret key for artifact signing.
            d0_fences: Optional D0 injection fences.

        Returns:
            CompiledPromptArtifact with HMAC-SHA256 signature.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "AirlockAssembler.assemble_from_bom",
        )
        emit_replay_key(_trace_id, f"artifact:{bom.trace_id}")
        emit_determinism_digest(_trace_id, f"path:{bom.path}")

        # 1. Load S0 from TemplateRegistry
        from agentic_core.L4_state.utils.memory.template_registry import get_template_registry
        registry = get_template_registry()
        s0_content = registry.get_s0(bom.system_version_hash)

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

        # 6. Validate slot order (S0→D0→I0→C0→U0)
        slots = {
            "S0": s0_content,
            "D0": d0_content,
            "I0": i0_content,
            "C0": c0_content,
            "U0": u0_content,
        }
        # Validate slot order S0→D0→I0→C0→U0
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

        # 8. Assemble final strings
        system_parts = [p for p in [s0_content, d0_content, i0_content, c0_content] if p]
        final_system = "\n\n".join(system_parts)
        final_user = u0_clean

        # 9. Estimate tokens (rough approximation: 4 chars ≈ 1 token)
        token_estimate = (len(final_system) + len(final_user)) // 4

        # 10. Build artifact and sign
        artifact = CompiledPromptArtifact(
            trace_id=bom.trace_id,
            final_system_string=final_system,
            final_user_string=final_user,
            allowed_tools_schema=(),  # Tools configured at gateway level
            token_estimate=token_estimate,
            signature="",  # Placeholder, computed below
        )

        # Compute HMAC-SHA256 signature
        canonical = json.dumps(artifact.to_dict(), sort_keys=True, separators=(",", ":"))
        signature = hmac.new(
            secret_key, canonical.encode("utf-8"), hashlib.sha256,
        ).hexdigest()

        # Return signed artifact
        return CompiledPromptArtifact(
            trace_id=artifact.trace_id,
            final_system_string=artifact.final_system_string,
            final_user_string=artifact.final_user_string,
            allowed_tools_schema=artifact.allowed_tools_schema,
            token_estimate=artifact.token_estimate,
            signature=signature,
        )
