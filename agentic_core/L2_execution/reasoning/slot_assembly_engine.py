"""
Slot Assembly Engine for prompt compilation.

Assembles authority slots (S0→I0→D0→C0→U0) into a CompiledPromptArtifact
with HMAC-SHA256 signature for verification by SovereignLLMGateway.
"""

import hashlib
import hmac
import json
import secrets
from typing import Any

from .authority_validator import AuthorityValidationError, AuthorityValidator
from .compiled_artifact import (
    AuthoritySlot,
    CompiledPromptArtifact,
    InjectionScanResult,
    PromptBOM,
    RoutingDecision,
    TemplateManifest,
)


class SlotAssemblyEngine:
    """
    Core engine for assembling authority slots into compiled prompts.

    Responsibilities:
    1. Collect slots in canonical order (S0→I0→D0→C0→U0)
    2. Validate authority hierarchy
    3. Concurrent injection scan (U0 vs S0/I0)
    4. Compute token budget
    5. Generate HMAC-SHA256 signed CompiledPromptArtifact
    """

    def __init__(self, secret_key: bytes | None = None) -> None:
        self.validator = AuthorityValidator()
        self.secret_key = secret_key or secrets.token_bytes(32)
        self._slots: dict[str, AuthoritySlot] = {}
        self._injection_scan_result: InjectionScanResult | None = None
        self._routing_decision: RoutingDecision | None = None
        self._template_manifest: TemplateManifest | None = None
        self._prompt_bom: PromptBOM | None = None

    def add_slot(self, slot: AuthoritySlot) -> "SlotAssemblyEngine":
        """
        Add an authority slot to the assembly.

        Slots are keyed by slot_type; adding duplicate overwrites previous.
        """
        self._slots[slot.slot_type.upper()] = slot
        return self

    def with_routing_decision(self, decision: RoutingDecision) -> "SlotAssemblyEngine":
        """Set the routing decision from L0 classifier."""
        self._routing_decision = decision
        return self

    def with_template_manifest(self, manifest: TemplateManifest) -> "SlotAssemblyEngine":
        """Set the template manifest for validation."""
        self._template_manifest = manifest
        return self

    def with_prompt_bom(self, bom: PromptBOM) -> "SlotAssemblyEngine":
        """Set the prompt BOM."""
        self._prompt_bom = bom
        return self

    def assemble(self) -> CompiledPromptArtifact:
        """
        Assemble all added slots into a CompiledPromptArtifact.

        Performs:
        1. Authority validation
        2. Injection scan
        3. Token estimation
        4. HMAC signing

        Returns:
            CompiledPromptArtifact with signature

        Raises:
            AuthorityValidationError: If slot ordering/hierarchy invalid
            AssemblyError: If assembly fails (injection detected, etc.)
        """
        # Get slots in canonical order
        slots = AuthorityValidator.canonical_order(list(self._slots.values()))
        slot_codes = [s.slot_type.upper() for s in slots]

        # Validate authority
        if not self.validator.validate_authority_chain(slots):
            raise AuthorityValidationError(
                f"Authority validation failed: {'; '.join(self.validator.get_errors())}",
            )

        # Concurrent injection scan (U0 vs S0/I0)
        self._injection_scan_result = self._scan_for_injections(slots)
        if self._injection_scan_result.blocked:
            raise AssemblyError(f"Injection detected: {self._injection_scan_result.override_attempts}")

        # Validate template variables if manifest provided
        if self._template_manifest and self._prompt_bom:
            missing = self._template_manifest.validate(self._prompt_bom.template_args)
            if missing:
                raise AssemblyError(f"Missing template variables: {missing}")

        # Assemble final strings
        system_parts: list[str] = []
        user_parts: list[str] = []

        # S0: System/State (Absolute) - goes to system message
        if "S0" in self._slots:
            system_parts.append(self._slots["S0"].content)

        # I0: Instructional (Governed) - goes to system message
        if "I0" in self._slots:
            system_parts.append(self._slots["I0"].content)

        # D0: Binding (Semantic Fences) - goes to system as constraints
        if "D0" in self._slots:
            system_parts.append(f"[CONSTRAINTS]\n{self._slots['D0'].content}")

        # C0: Info (Grounding/RAG) - goes to user context
        if "C0" in self._slots:
            user_parts.append(f"[CONTEXT]\n{self._slots['C0'].content}")

        # U0: Zero (Raw Intent) - goes to user message
        if "U0" in self._slots:
            user_parts.append(self._slots["U0"].content)

        final_system = "\n\n".join(system_parts)
        final_user = "\n\n".join(user_parts)

        # Estimate tokens (rough approximation)
        tokens = self._estimate_tokens(final_system, final_user)

        # Build artifact
        trace_id = self._prompt_bom.trace_id if self._prompt_bom else self._generate_trace_id()
        version_hash = self._prompt_bom.system_version_hash if self._prompt_bom else "unknown"

        # Build allowed tools schema from D0 slot if present
        allowed_tools: list[dict[str, Any]] = []
        if "D0" in self._slots:
            tools_meta = self._slots["D0"].metadata.get("allowed_tools", [])
            if tools_meta:
                allowed_tools = tools_meta

        artifact = CompiledPromptArtifact(
            trace_id=trace_id,
            system_version_hash=version_hash,
            final_system_string=final_system,
            final_user_string=final_user,
            allowed_tools_schema=allowed_tools,
            tokens=tokens,
            slots_used=slot_codes,
            signature="",  # Will be computed
            prompt_bom=self._prompt_bom.to_dict() if self._prompt_bom else {},
            template_manifest=self._template_manifest.__dict__ if self._template_manifest else {},
            injection_scan_result=self._injection_scan_result.__dict__
            if self._injection_scan_result
            else None,
            routing_decision=self._routing_decision.__dict__ if self._routing_decision else None,
        )

        # Compute signature
        signature = self._sign_artifact(artifact)
        # Create new artifact with signature (since frozen, we need to recreate)
        artifact = CompiledPromptArtifact(
            trace_id=artifact.trace_id,
            system_version_hash=artifact.system_version_hash,
            final_system_string=artifact.final_system_string,
            final_user_string=artifact.final_user_string,
            allowed_tools_schema=artifact.allowed_tools_schema,
            tokens=artifact.tokens,
            slots_used=artifact.slots_used,
            signature=signature,
            timestamp=artifact.timestamp,
            metadata=artifact.metadata,
            prompt_bom=artifact.prompt_bom,
            template_manifest=artifact.template_manifest,
            injection_scan_result=artifact.injection_scan_result,
            routing_decision=artifact.routing_decision,
        )

        return artifact

    def _scan_for_injections(self, slots: list[AuthoritySlot]) -> InjectionScanResult:
        """
        Concurrent injection scan: check U0 for S0/I0 override attempts.

        Detects patterns like:
        - "Ignore previous instructions"
        - "You are now a different agent"
        - Attempts to override S0/I0 content
        """
        detected = False
        override_attempts: list[str] = []
        risk_score = 0.0

        u0_slot = next((s for s in slots if s.slot_type == "U0"), None)
        if not u0_slot:
            return InjectionScanResult(detected=False, override_attempts=[], risk_score=0.0, blocked=False)

        u0_content = u0_slot.content.lower()

        # Injection patterns to detect
        patterns = [
            ("ignore previous", 0.8),
            ("ignore the above", 0.8),
            ("forget previous", 0.7),
            ("you are now", 0.6),
            ("you must now", 0.6),
            ("disregard", 0.5),
            ("instead, you should", 0.5),
            ("new instruction", 0.7),
            ("override", 0.9),
            ("system override", 1.0),
        ]

        for pattern, score in patterns:
            if pattern in u0_content:
                detected = True
                override_attempts.append(pattern)
                risk_score = max(risk_score, score)

        # Check for S0/I0 content keywords in U0 (attempting to fake authority)
        s0_slot = next((s for s in slots if s.slot_type == "S0"), None)
        i0_slot = next((s for s in slots if s.slot_type == "I0"), None)

        if s0_slot:
            s0_keywords = self._extract_keywords(s0_slot.content)
            for kw in s0_keywords:
                if kw.lower() in u0_content and len(kw) > 8:
                    detected = True
                    override_attempts.append(f"S0 keyword hijack: {kw[:20]}...")
                    risk_score = max(risk_score, 0.9)

        if i0_slot:
            i0_keywords = self._extract_keywords(i0_slot.content)
            for kw in i0_keywords:
                if kw.lower() in u0_content and len(kw) > 8:
                    detected = True
                    override_attempts.append(f"I0 keyword hijack: {kw[:20]}...")
                    risk_score = max(risk_score, 0.7)

        blocked = risk_score >= 0.8

        return InjectionScanResult(
            detected=detected,
            override_attempts=override_attempts,
            risk_score=risk_score,
            blocked=blocked,
        )

    def _extract_keywords(self, content: str) -> list[str]:
        """Extract potential authority keywords from slot content."""
        # Simple extraction: words that look like technical terms or rules
        words = content.split()
        keywords = [w for w in words if len(w) > 5 and w[0].isupper()]
        return keywords[:20]  # Limit to top 20

    def _estimate_tokens(self, system: str, user: str) -> int:
        """Estimate token count (rough approximation)."""
        # Rough estimate: ~4 chars per token
        total_chars = len(system) + len(user)
        return total_chars // 4

    def _sign_artifact(self, artifact: CompiledPromptArtifact) -> str:
        """Compute HMAC-SHA256 signature for artifact."""
        payload = {
            "trace_id": artifact.trace_id,
            "system_version_hash": artifact.system_version_hash,
            "final_system_string": artifact.final_system_string,
            "final_user_string": artifact.final_user_string,
            "allowed_tools_schema": artifact.allowed_tools_schema,
            "tokens": artifact.tokens,
            "slots_used": artifact.slots_used,
            "timestamp": artifact.timestamp,
        }
        payload_bytes = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hmac.new(self.secret_key, payload_bytes, hashlib.sha256).hexdigest()

    def _generate_trace_id(self) -> str:
        """Generate a unique trace ID."""
        return f"prompt-{secrets.token_hex(8)}"

    def clear(self) -> "SlotAssemblyEngine":
        """Clear all slots and state for reuse."""
        self._slots.clear()
        self._injection_scan_result = None
        self._routing_decision = None
        self._template_manifest = None
        self._prompt_bom = None
        return self


class AssemblyError(Exception):
    """Raised when prompt assembly fails."""

    pass
