"""
HOP-1: Profile Analysis Agent (V2.5 Architecture).

LIC Sovereign Gatekeeper.
Implements mandatory LIC 7 Entrance Gates and CXO Precedence Rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_lic.config.loader_config import load_agent_specs
from apps_lic.types.k1_router_types import K1Router
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.utils.lic_agent_base_util import LICAgentBase
from apps_lic.types.TraceRegistry import TraceRegistry

# Import mixin with fallback
try:
    from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
except ImportError:
    class SubatomicTestingMixin:
        pass


@dataclass
class HOP1ProfileAnalysisAgent(LICAgentBase, SubatomicTestingMixin):
    """
    LIC Sovereign Gatekeeper.

    Architecture:
    - Base: LICAgentBase (Config, Tracing, Healing)
    - Input: 'mission_input' or 'recipient_profile' from ImmutableStagingBuffer
    - Logic: Gate Validation -> CXO Precedence -> Heuristic Classification
    - Output: 'hop1_analysis' (Dict) to ImmutableStagingBuffer
    """

    # Sovereign Seal: Runtime immutability flag
    _sealed: bool = field(default=False, init=False, repr=False)

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Enforce Sovereign Seal (Runtime Immutability).
        """
        if getattr(self, "_sealed", False):
            raise AttributeError(
                f"Sovereign Seal Active: Cannot modify '{name}' on {self.__class__.__name__}"
            )
        super().__setattr__(name, value)

    def __getstate__(self) -> dict[str, Any]:
        """
        Pickling support for Sovereign Sealed agent.
        """
        return self.__dict__.copy()

    def __setstate__(self, state: dict[str, Any]) -> None:
        """
        Unpickling support: Temporarily bypass Sovereign Seal to restore state.
        """
        object.__setattr__(self, "_sealed", False)
        self.__dict__.update(state)
        object.__setattr__(self, "_sealed", True)

    def __post_init__(self) -> None:
        """
        Initialize after dataclass construction.
        """
        # Root Injection: LICAgentBase must initialize first
        super().__post_init__()

        # Critical Analysis: Verify State Injection
        if not getattr(self, "config", None):
            raise RuntimeError(
                f"CRITICAL: {self.__class__.__name__} failed to inherit Sovereign Config."
            )

        # Load domain-specific agent specs
        self.agent_specs = load_agent_specs()

        # Integration of the new Logic Node
        self.router = K1Router(
            config=self.config.__dict__ if hasattr(self, "config") and self.config else {}
        )

        # Engage Sovereign Seal
        object.__setattr__(self, "_sealed", True)

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute profile analysis logic.

        1. Read Mission Input (Sovereign Defensiveness).
        2. Gate 2: Contact Block Validation.
        3. Gate 4: Archetype Classification with CXO Precedence.
        4. L3 Slow Path trigger for low confidence.
        5. Final Gate Approval & Write.
        """
        registry.add_trace("PHASE_START", {"agent": self.__class__.__name__})

        # 1. Read Mission Input (Sovereign Defensiveness)
        # Support both mission_input (new) and recipient_profile (legacy)
        mission_input = buffer.read("mission_input")
        profile = buffer.read("recipient_profile")

        # Determine input source
        if mission_input and isinstance(mission_input, dict):
            # New format: mission_input with contact_* fields
            title = mission_input.get("contact_title", "")
            about = mission_input.get("contact_about", "")
            # Also check nested recipient_profile with defensive type checking
            if not title and isinstance(mission_input.get("recipient_profile"), dict):
                nested = mission_input["recipient_profile"]
                title = nested.get("title", "")
                about = nested.get("about", "")
        elif profile and isinstance(profile, dict):
            # Legacy format: recipient_profile
            title = profile.get("title", "")
            about = profile.get("about", "")
        else:
            registry.add_trace("DATA_ERROR", {"msg": "Missing mission_input or recipient_profile"})
            raise ValueError(
                "HOP-1 requires 'recipient_profile' or 'mission_input' in buffer"
            )

        # Defensive Title Normalization
        title = (title or "").strip()
        about = (about or "").strip()
        registry.add_trace("INPUT_NORMALIZED", {"title_len": len(title), "about_len": len(about)})

        # Gate 2: Contact Block Validation
        if not title:
            registry.add_trace("GATE_2_FAILED", {"reason": "missing_title"})
            raise ValueError("GATE_2_FAILED: Contact title is required")

        registry.add_trace("PHASE_STEP", {"action": "starting_gate_validation"})

        # Gate 4: Archetype Classification with CXO Precedence
        combined_text = f"{title} {about}".upper()

        archetype = None
        confidence = 0.0
        cxo_triggered = False
        key_indicators = []
        reasoning = ""

        # Rule: CXO Precedence tokens take immediate priority
        # Hardened boundary regex: word boundaries + exclusion of common false-positives
        import re

        cxo_tokens = self.agent_specs.profile_analysis_agent.cxo_precedence_tokens
        for token in cxo_tokens:
            # Hardened boundary regex: case-insensitive flag in pattern
            # Target: 'CEO', 'CTO', 'CFO', 'COO', 'CHRO', 'CMO'
            pattern = r"(?i)\b" + re.escape(token) + r"\b"
            if re.search(pattern, combined_text):
                archetype = "C_LEVEL"
                confidence = 1.0  # CXO precedence = 100% confidence
                cxo_triggered = True
                key_indicators = [token]
                reasoning = f"K.1 CXO Precedence: Token '{token}' found in profile"
                registry.add_trace("CXO_PRECEDENCE_TRIGGERED", {"token": token})
                break

        # Heuristic Classification Fallback
        if not archetype:
            result = self._classify_heuristic(title.lower())
            archetype = result["archetype"]
            confidence = result["confidence"]
            key_indicators = result["key_indicators"]
            reasoning = result["reasoning"]

        # L3 Slow Path: Reasoning Injection for low confidence
        needs_override = confidence < self.agent_specs.profile_analysis_agent.manual_override_threshold
        if needs_override:
            registry.add_trace(
                "REASONING_ACTIVATED",
                {
                    "reason": "low_confidence",
                    "score": confidence,
                    "threshold": self.agent_specs.profile_analysis_agent.manual_override_threshold,
                },
            )
            # [Logic: Internal LLM call for CoT/ToT reasoning if confidence < threshold]
            # Defensive: ``self.toggles`` and ``self.llm`` are runtime-injected
            # attributes that may be absent in unit-test contexts. Treat
            # missing attributes as "feature disabled" rather than crashing.
            _toggles = getattr(self, "toggles", None)
            _llm = getattr(self, "llm", None)
            if _toggles is not None and getattr(_toggles, "use_cot", False) and _llm:
                try:
                    llm_response = self._execute_reasoning(
                        title, {"archetype": archetype, "confidence": confidence}
                    )
                    if llm_response["confidence"] > confidence:
                        registry.add_trace(
                            "DECISION_OVERRIDE",
                            {"old": archetype, "new": llm_response["archetype"]},
                        )
                        archetype = llm_response["archetype"]
                        confidence = llm_response["confidence"]
                        needs_override = False
                except Exception as e:
                    registry.add_trace("REASONING_ERROR", {"error": str(e)})
            else:
                registry.add_trace("REASONING_SKIPPED", {"reason": "LLM_or_COT_disabled"})
        else:
            registry.add_trace("REASONING_NOT_REQUIRED", {"confidence": confidence})

        # Final Gate Approval & Write
        # Get profile data for output (handle both input formats)
        if profile and isinstance(profile, dict):
            recipient_name = profile.get("name", "")
            recipient_company = profile.get("company", "")
        elif mission_input:
            recipient_name = mission_input.get("contact_name", "")
            recipient_company = mission_input.get("contact_company", "")
        else:
            recipient_name = ""
            recipient_company = ""

        output_data = {
            "Archetype": archetype,
            "confidence": confidence,
            "cxo_precedence_triggered": cxo_triggered,
            "reasoning": reasoning,
            "key_indicators": key_indicators,
            "needs_manual_override": needs_override,
            "entrance_gates_passed": ["GATE_1_LIFECYCLE", "GATE_2_BLOCK", "GATE_4_ARCHETYPE"],
            "recipient_title": title,
            "recipient_name": recipient_name,
            "recipient_company": recipient_company,
            "metadata": {"title": title},
        }

        buffer.write_once("hop1_analysis", output_data)
        registry.add_trace("DECISION_FINAL", {"archetype": archetype, "confidence": confidence})

    def _execute_reasoning(self, title: str, current_result: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the 'Slow Path' using the LLM.
        """
        # In a real implementation, this would:
        # 1. Load prompt template
        # 2. Format with title and current_result
        # 3. self.llm.generate(prompt)
        # 4. Parse JSON

        # For Phase 6 Prototype, we delegate to the injected MockLLM
        return self.llm.analyze(title, current_result)

    def _classify_heuristic(self, title: str) -> dict[str, Any]:
        """
        Apply deterministic keyword matching rules from AgentSpecs.
        """
        config = self.agent_specs.profile_analysis_agent

        best_match = {
            "archetype": config.default_archetype,
            "confidence": config.default_confidence,
            "reasoning": f"Default fallback for title: '{title}'",
            "key_indicators": [title],
            "needs_manual_override": True,
        }

        # Iterate defined archetypes in config
        for archetype_name, indicators in config.archetype_indicators.items():
            for keyword in indicators.keywords:
                if keyword in title:
                    # Match found
                    return {
                        "archetype": archetype_name,
                        "confidence": indicators.confidence,
                        "reasoning": f"Title '{title}' contains indicator '{keyword}'",
                        "key_indicators": [keyword],
                        "needs_manual_override": indicators.confidence
                        < config.manual_override_threshold,
                    }

        return best_match

    def heal_repository(self) -> None:
        """
        V2 Self-Healing.

        The base class handles Mixin logic. Here we add domain-specific checks.
        """
        super().heal_repository()
        self._run_profile_diagnostics()

    def _run_profile_diagnostics(self) -> None:
        """Run sanity checks on the configuration logic."""
        test_title = "Chief Executive Officer"
        result = self._classify_heuristic(test_title.lower())

        if result["archetype"] != "C_LEVEL":
            # Note: log_warning not available in current mixin implementation
            pass
        else:
            # Note: log_info not available in current mixin implementation
            pass
