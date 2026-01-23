"""
HOP-5: Generation Agent (V2 Architecture).

Synthesizes inputs from HOPs 1-4 to generate candidate messages.
"""

from __future__ import annotations

import asyncio

from apps_lic.shared.v2_patterns.agent_base import V2AgentBase
from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry


class HOP5GenerationAgent(V2AgentBase):
    """
    V2 Implementation of HOP-5 Writer.

    Architecture:
    - Base: V2AgentBase
    - Inputs:
        - HOP-1 (Archetype)
        - HOP-2 (Research/Context)
        - HOP-3 (Sender Grounding)
        - HOP-4 (Route/Constraints)
    - Logic: N-Candidate Generation -> Scoring -> Selection.
    - Output: 'hop5_generation'
    """

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

        n_candidates = config.c_level_n_candidates if archetype == "C_LEVEL" else 1
        temperature = config.base_temperatures.get(archetype, 0.5)

        registry.add_trace(
            "PHASE_STEP",
            {"action": "configuring_generation", "n_candidates": n_candidates, "temp": temperature},
        )

        # 3. Generate Candidates (Fan-out)
        candidates = []
        for i in range(n_candidates):
            prompt = self._construct_prompt(hop1, hop2, hop3, hop4)

            # Async generation
            if self.llm:
                response = self._run_async(self.llm.generate(prompt, temperature=temperature))
                candidates.append(
                    {
                        "id": i,
                        "text": response.strip(),
                        "score": 0.0,  # Placeholder for scoring logic
                    }
                )
            else:
                registry.add_trace("GEN_SKIPPED", {"reason": "No LLM Client"})
                candidates.append({"id": 0, "text": "Simulated Draft", "score": 0})

        # 4. Score & Select (Fan-in)
        # Simplified internal scoring for V2 (Length/Constraints check)
        selected = self._score_and_select(candidates, hop4["constraints"])

        # 5. Write Output
        output = {
            "selected_draft": selected,
            "all_candidates": candidates,
            "meta": {
                "temperature": temperature,
                "n_candidates": n_candidates,
                "archetype": archetype,
                "route": route,
            },
        }

        buffer.write_once("hop5_generation", output)
        registry.add_trace(
            "DECISION_FINAL", {"selected_id": selected["id"], "length": len(selected["text"])}
        )

    def _construct_prompt(self, h1, h2, h3, h4) -> str:
        """Constructs the prompt from context."""
        # In a real implementation, load template from prompts.json
        # Simplified for V2 logic demo
        return f"""
        Generate a {h4["route"]} message.
        Recipient: {h1.get("recipient_title")} at {h1.get("recipient_company")}
        Research: {h2.get("signal_score")} signal
        Sender: {len(h3["sender_grounding"]["products"])} products
        Constraints: Max {h4["constraints"]["char_limit"]} chars.
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
