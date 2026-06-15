"""
HOP-5: Generation Agent (LIC Sovereign Architecture).

Synthesizes inputs from HOPs 1-4 to generate candidate messages.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from apps_lic.utils.lic_agent_base_util import LICAgentBase
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin

# W1-P3: per-(archetype, section) temperature adjustment. Wires
# MessagePlanner.temperature_adjustments through to the LLM call sites
# in K.3 and K.5A. See apps_lic/engines/section_temperature_resolver.py.
from apps_lic.engines.section_temperature_resolver import resolve_section_temperature
from apps_lic.policy.reasoning_intensity import default_reasoning_policy


@dataclass
class HOP5GenerationAgent(LICAgentBase, SubatomicTestingMixin):
    """
    V2 Implementation of HOP-5 Writer.

    Architecture:
    - Base: LICAgentBase
    - Inputs:
        - HOP-1 (Archetype)
        - HOP-2 (Research/Context)
        - HOP-3 (Sender Grounding)
        - HOP-4 (Route/Constraints)
    - Logic: N-Candidate Generation -> scoring -> Selection.
    - Output: 'hop5_generation'
    """

    # Sovereign Configuration.
    # The live candidate count is driven by the reasoning policy (max_candidates
    # 1/2/3 by tier) and the archetype envelope (C_LEVEL -> c_level_n_candidates,
    # else 1), NOT this field. It is synced to the policy default (R1
    # max_candidates) so it no longer implies a fixed 3-candidate fan-out.
    generation_params: dict[str, Any] = field(
        default_factory=lambda: {
            "temperature": 0.7,
            "n_candidates": default_reasoning_policy()["max_candidates"],
            "max_tokens": 500,
        }
    )
    # Optional injected dependencies (test fixtures + production wiring).
    # ``llm_client`` is the canonical kwarg name; ``llm`` is a back-compat
    # attribute alias that the existing _process body reads.
    llm_client: Any | None = field(default=None)

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()
        # Mirror llm_client onto self.llm without going through the
        # Sovereign Seal (object.__setattr__ bypasses __setattr__ guards
        # in subclasses that may seal). Subsequent _process body uses
        # ``self.llm`` for invocation.
        object.__setattr__(self, "llm", self.llm_client)

    @staticmethod
    def _resolve_pre_flight(hop1: dict, mission_input: dict) -> dict | None:
        """Consult PreFlightPolicy YAML for the route + generation envelope.

        Returns the verdict dict (route, char_limit, n_candidates,
        temperature, signature_required) on match, or None on any
        failure — callers fall back to legacy hop4_routing buffer read.

        Wired W2-P1 per docs/archive/windsurf/legacy-tree/plans/decision-router-policy-tables-b3a4d2.md.
        Additive: HOP4 still runs upstream and writes hop4_routing; this
        function is consulted only when callers want to short-circuit the
        legacy path. Deletion of HOP4 is gated on the 90-day deprecation
        window per constitutional §3.
        """
        try:
            from pathlib import Path

            from apps_lic.policy import DecisionRouter

            policy_path = (
                Path(__file__).resolve().parents[1]
                / "policy"
                / "pre_flight_policy.yaml"
            )
            router = DecisionRouter(policy_path)
            state = {
                "archetype": (hop1 or {}).get("Archetype", "OTHER"),
                "connection_status": (mission_input or {}).get(
                    "connection_status", "NOT_CONNECTED"
                ),
                "premium_available": (mission_input or {}).get(
                    "premium_available", False
                ),
            }
            override = (mission_input or {}).get("route_override")
            if override:
                state["route_override"] = override
            match = router.resolve(state)
            return dict(match.verdict)
        except Exception:  # guardian: allow-log-and-swallow -- pre-flight policy is best-effort; legacy HOP4 path covers fallback
            return None

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute generation logic.

        1. Read all upstream inputs (HOPs 1-4).
        2. Configure generation parameters (temperature, n_candidates).
        3. Generate N candidates via LLM.
        4. Score candidates based on constraints.
        5. Select best candidate and write output.
        """
        # 1. Read Inputs
        try:
            hop1 = buffer.read("hop1_analysis")
            hop2 = buffer.read("hop2_research")
            hop3 = buffer.read("hop3_sender_grounding")
            hop4 = buffer.read("hop4_routing")
        except Exception:
            registry.add_trace("DATA_ERROR", {"msg": "Failed to read required inputs"})
            raise ValueError("HOP-5 requires outputs from HOPs 1, 2, 3, and 4")

        # Validate existence
        if not all([hop1, hop2, hop3, hop4]):
            registry.add_trace("CRITICAL_FAILURE", {"msg": "One or more upstream inputs missing"})
            raise RuntimeError("Missing required upstream state")

        # 2. Configure Generation
        config = self.config.generation_agent
        archetype = hop1["Archetype"]
        route = hop4["route"]

        # Legacy archetype switch — preserved as the default envelope.
        n_candidates = config.c_level_n_candidates if archetype == "C_LEVEL" else 1
        temperature = config.base_temperatures.get(archetype, 0.5)

        # 2b. PreFlightPolicy override (W2-P1 wiring). When the YAML
        # policy resolves a verdict, it supersedes the imperative
        # archetype switch above. This is the substrate that lets the
        # archetype/route/connection envelope be tuned without code
        # edits. ROUTE_RESOLVED trace records the matched rule for
        # audit replay.
        try:
            mission_input = buffer.read("mission_input") or {}
        except Exception:  # guardian: allow-log-and-swallow -- mission_input optional in unit-test contexts
            mission_input = {}
        pre_flight = self._resolve_pre_flight(hop1, mission_input)
        if pre_flight is not None:
            n_candidates = int(pre_flight.get("n_candidates", n_candidates))
            temperature = float(pre_flight.get("temperature", temperature))
            registry.add_trace(
                "ROUTE_RESOLVED",
                {
                    "source": "pre_flight_policy",
                    "route": pre_flight.get("route"),
                    "n_candidates": n_candidates,
                    "temperature": temperature,
                    "char_limit": pre_flight.get("char_limit"),
                },
            )

        registry.add_trace(
            "PHASE_STEP",
            {"action": "configuring_generation", "n_candidates": n_candidates, "temp": temperature},
        )

        # 3. Specialist Assembly Chain (K.3 -> K.5A -> K.5 -> K.7)
        registry.add_trace("PHASE_STEP", {"action": "starting_specialist_assembly"})

        candidates = []
        for i in range(n_candidates):
            # K.3: Body Generation with Archetype Transition Phrases
            body_data = self._run_k3_body_generation(hop1, hop2, registry)

            # K.5A: Bullet Generation with 3V-3T-1S Provenance
            bullet_data = self._run_k5a_bullet_generation(
                hop3, hop2, registry, archetype=archetype
            )

            # K.5: CTA Generation (Route-Specific Constraints)
            cta_data = self._run_k5_cta_generation(hop4, registry)

            # K.7: Final Message Assembly (Immutable Signature + Fencing)
            assembly_data = self._assemble_k7_final_message(
                body_data["text"], bullet_data["bullets"], cta_data["text"], hop1, registry
            )

            candidates.append(
                {
                    "id": i,
                    "text": assembly_data["full_text"],
                    "checksum": assembly_data["checksum"],
                    "body": body_data["text"],
                    "bullets": bullet_data["bullets"],
                    "cta": cta_data["text"],
                    "provenance_labels": bullet_data["labels"],
                    "transition_phrase": body_data["transition_phrase"],
                    "score": 0.0,
                }
            )

        # 4. Score & Select (Fan-in)
        # Simplified internal scoring for V2 (Length/Constraints check)
        selected = self._score_and_select(candidates, hop4["constraints"])

        # 5. Write Output with Enhanced Metadata
        output = {
            "selected_draft": selected,
            "all_candidates": candidates,
            "meta": {
                "temperature": temperature,
                "n_candidates": n_candidates,
                "archetype": archetype,
                "route": route,
                "k3_phrase": selected.get("transition_phrase"),
            },
        }

        buffer.write_once("hop5_generation", output)
        registry.add_trace(
            "DECISION_FINAL",
            {
                "status": "SUCCESS",
                "selected_id": selected["id"],
                "length": len(selected["text"]),
                "route": route,
            },
        )

    def _construct_prompt(self, h1, h2, h3, h4) -> str:
        """Constructs the prompt from context. Defensive against partial inputs."""
        # In a real implementation, load template from prompts.json
        # Simplified for V2 logic demo
        sender_grounding = (h3 or {}).get("sender_grounding") or {}
        products = sender_grounding.get("products") or []
        constraints = (h4 or {}).get("constraints") or {}
        char_limit = constraints.get("char_limit", 2000)
        return f"""
        Generate a {(h4 or {}).get("route", "INMAIL")} message.
        Recipient: {(h1 or {}).get("recipient_title")} at {(h1 or {}).get("recipient_company")}
        Research: {(h2 or {}).get("signal_score")} signal
        Sender: {len(products)} products
        Constraints: Max {char_limit} chars.
        """

    def _score_and_select(self, candidates: list[dict], constraints: dict) -> dict:
        """Basic scoring logic to select best candidate."""
        best = candidates[0]
        max_score = -1

        limit = constraints.get("char_limit", 2000)

        for c in candidates:
            score = 0
            length = len(c["text"])

            # Constraint penalty
            if length > limit:
                score -= 100
            else:
                score += 10  # Base score

            c["score"] = score
            if score > max_score:
                max_score = score
                best = c

        return best

    def _run_async(self, coro):
        """Helper to run async code in sync V2 pipeline."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    def _run_k3_body_generation(self, hop1: dict, hop2: dict, registry: TraceRegistry) -> dict:
        """
        K.3: Body Generation with Archetype Transition Phrases.

        Returns dict with 'text' and 'transition_phrase' keys.
        """
        registry.add_trace("K3_START", {"archetype": hop1.get("Archetype")})

        archetype = hop1.get("Archetype", "UNKNOWN")
        company = hop1.get("recipient_company", "your organization")
        research_signals = hop2.get("strategic_signals", [])

        # K.3 Transition phrase for C_LEVEL
        if archetype == "C_LEVEL":
            transition = f"Two strategic insights I have gleaned from my research about {company}:"
        else:
            transition = f"I noticed some interesting developments at {company}:"

        # Build body with research signals
        body_parts = [transition]

        if research_signals:
            for i, signal in enumerate(research_signals[:2], 1):
                body_parts.append(f"\n{i}. {signal}")
        elif self.llm:
            # Fallback to LLM generation if no signals
            prompt = self._construct_prompt(
                hop1, hop2, {}, {"route": "INMAIL", "constraints": {"char_limit": 500}}
            )
            # W1-P3: hook-section temperature derived from archetype.
            # Default base 0.5 preserved; resolver applies per-archetype delta.
            hook_temp = resolve_section_temperature(archetype, "hook", 0.5)
            registry.add_trace(
                "K3_TEMPERATURE_RESOLVED",
                {"section": "hook", "archetype": archetype, "temperature": hook_temp},
            )
            response = self._run_async(self.llm.generate(prompt, temperature=hook_temp))
            body_parts.append(f"\n{response.strip()}")
        else:
            body_parts.append("\nYour strategic initiatives align well with our capabilities.")

        body_text = "\n".join(body_parts)
        registry.add_trace(
            "K3_BODY_GENERATED", {"archetype": archetype, "transition_used": transition[:50]}
        )

        return {"text": body_text, "transition_phrase": transition}

    def _run_k5a_bullet_generation(
        self,
        hop3: dict,
        hop2: dict,
        registry: TraceRegistry,
        *,
        archetype: str = "OTHER",
    ) -> dict:
        """
        K.5A: Bullet Generation with 3V-3T-1S Provenance Distribution.

        V = Verbatim (from sender profile)
        T = Transformed (research insights)
        S = Synthetic (LLM generated)

        Args:
            archetype: W1-P3 — drives per-(archetype, section="value")
                temperature adjustment on the synthetic-bullet LLM call.
                Default "OTHER" preserves pre-W1-P3 behaviour for callers
                that do not pass it.

        Returns dict with 'bullets' list and 'labels' list.
        """
        registry.add_trace("K5A_START", {"rule": "3V-3T-1S"})

        bullets = []
        labels = []

        # Extract sender capabilities for Verbatim bullets (3V)
        sender_data = hop3.get("sender_grounding", {})
        products = sender_data.get("products", [])
        capabilities = sender_data.get("capabilities", [])

        verbatim_sources = products + capabilities
        for i in range(min(3, len(verbatim_sources))):
            bullets.append(f"• {verbatim_sources[i]}")
            labels.append("V")

        # Pad with generic if needed
        while len(labels) < 3:
            bullets.append("• Industry-leading solutions")
            labels.append("V")

        # Extract research signals for Transformed bullets (3T)
        research_signals = hop2.get("strategic_signals", [])
        for i in range(min(3, len(research_signals))):
            bullets.append(f"• Aligned with your {research_signals[i].lower()} initiatives")
            labels.append("T")

        # Pad with generic if needed
        while len(labels) < 6:
            bullets.append("• Strategic alignment opportunities")
            labels.append("T")

        # Generate one Synthetic bullet (1S)
        if self.llm:
            try:
                prompt = "Generate a single compelling value proposition in 5-7 words."
                # W1-P3: value-section temperature tuned per archetype.
                # Base 0.7 preserves the original default for "OTHER".
                value_temp = resolve_section_temperature(archetype, "value", 0.7)
                registry.add_trace(
                    "K5A_TEMPERATURE_RESOLVED",
                    {
                        "section": "value",
                        "archetype": archetype,
                        "temperature": value_temp,
                    },
                )
                synthetic = self._run_async(
                    self.llm.generate(prompt, temperature=value_temp)
                )
                bullets.append(f"• {synthetic.strip()}")
            except (RuntimeError, ValueError, TimeoutError, ConnectionError):  # guardian: allow-log-and-swallow -- LLM failure falls back to static bullet
                bullets.append("• Innovative partnership opportunities")
        else:
            bullets.append("• Innovative partnership opportunities")
        labels.append("S")

        registry.add_trace(
            "K5A_BULLETS_GENERATED",
            {
                "total_bullets": len(bullets),
                "provenance": {
                    "V": labels.count("V"),
                    "T": labels.count("T"),
                    "S": labels.count("S"),
                },
            },
        )

        return {"bullets": bullets, "labels": labels}

    def _run_k5_cta_generation(self, hop4: dict, registry: TraceRegistry) -> dict:
        """
        K.5: Generate CTA with word count constraints.

        CONNECTION_REQ: <= 5 words, no meeting requests
        INMAIL: <= 10 words, can include soft meeting request
        """
        route = hop4.get("route", "INMAIL")

        # K.5 CTA Templates by route
        cta_templates = {
            "CONNECTION_REQ": [
                "Open to connecting?",
                "Would love to connect.",
                "Let's connect?",
                "Interested in connecting?",
            ],
            "INMAIL": [
                "Would a brief conversation be valuable?",
                "Open to a quick discussion?",
                "Would you be open to connecting?",
            ],
            "FOLLOW_UP": [
                "Any thoughts on this?",
                "Would love your perspective.",
            ],
        }

        templates = cta_templates.get(route, cta_templates["INMAIL"])
        cta = templates[0]  # Select first template (could randomize)

        # Validate word count constraint
        word_limit = 5 if route == "CONNECTION_REQ" else 10
        word_count = len(cta.split())

        registry.add_trace(
            "K5_CTA_GENERATED",
            {
                "route": route,
                "cta": cta,
                "word_count": word_count,
                "word_limit": word_limit,
                "compliant": word_count <= word_limit,
            },
        )

        return {"text": cta}

    def _assemble_k7_final_message(
        self, body: str, bullets: list, cta: str, hop1: dict, registry: TraceRegistry
    ) -> dict:
        """
        K.7: Final Message Assembly with Immutable Signature and Fencing.

        Format:
        ```
        [Body]
        [Bullets]

        [CTA]

        [4-line Signature]
        ```

        Returns:
            dict with 'full_text' (fenced message) and 'checksum' (SHA256)
        """
        # Get sender name from config or default
        sender_name = getattr(self.config, "sender_name", "Best regards")

        # K.7 Immutable 4-line signature format
        signature_lines = [
            "Regards,",
            sender_name if sender_name != "Best regards" else "[Sender Name]",
            "",
            "linkedin.com/in/[profile]",
        ]
        signature = "\n".join(signature_lines)

        # Format bullets
        bullets_text = "\n".join(bullets) if bullets else ""

        # Assemble final message
        parts = [body]
        if bullets_text:
            parts.append(bullets_text)
        parts.append(cta)
        parts.append(signature)

        # Fenced block assembly for delivery integrity
        full_text = "```\n" + "\n\n".join(parts) + "\n```"
        import hashlib

        checksum = hashlib.sha256(full_text.encode()).hexdigest()

        registry.add_trace(
            "K7_MESSAGE_ASSEMBLED",
            {
                "body_length": len(body),
                "bullets_count": len(bullets),
                "checksum": checksum[:8],
            },
        )

        return {"full_text": full_text, "checksum": checksum}
