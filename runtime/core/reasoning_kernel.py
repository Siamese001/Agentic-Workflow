"""
Reasoning Kernel - System 2 Thinking Implementation

Implements deliberative reasoning for agents, allowing them to
draft, critique, and refine plans internally before execution.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ReasoningStep:
    """A single step in the reasoning process."""
    step_id: str
    content: str
    confidence: float
    reasoning_type: str  # "generate", "critique", "refine"


@dataclass
class ReasoningTrace:
    """Complete trace of the reasoning process."""
    initial_goal: str
    candidates: List[Dict[str, Any]]
    critiques: List[Dict[str, Any]]
    selected_plan: str
    confidence: float
    reasoning_time_ms: float
    steps: List[ReasoningStep]


class ReasoningKernel:
    """
    Implements System 2 thinking for agents.
    
    Instead of 1-shot generation, it generates multiple approaches,
    critiques them, and selects the best one through deliberation.
    """
    
    def __init__(
        self,
        llm_client,
        max_candidates: int = 3,
        critique_threshold: float = 0.7,
        enable_tree_of_thoughts: bool = True
    ):
        """
        Initialize the reasoning kernel.
        
        Args:
            llm_client: LLM client for generation
            max_candidates: Number of candidate plans to generate
            critique_threshold: Minimum critique score to accept a plan
            enable_tree_of_thoughts: Whether to use ToT reasoning
        """
        self.llm = llm_client
        self.max_candidates = max_candidates
        self.critique_threshold = critique_threshold
        self.enable_tot = enable_tree_of_thoughts
        
        logger.info(f"Reasoning kernel initialized (candidates={max_candidates}, ToT={enable_tot})")

    async def deliberate(
        self,
        context: Dict[str, Any],
        goal: str,
        constraints: Optional[List[str]] = None,
        memory_context: Optional[str] = None
    ) -> Tuple[str, ReasoningTrace]:
        """
        Main deliberation method that implements System 2 thinking.
        
        Args:
            context: Current execution context
            goal: The goal to achieve
            constraints: Optional constraints on the plan
            memory_context: Optional context from episodic memory
            
        Returns:
            Tuple of (selected_plan, reasoning_trace)
        """
        start_time = time.time()
        trace = ReasoningTrace(
            initial_goal=goal,
            candidates=[],
            critiques=[],
            selected_plan="",
            confidence=0.0,
            reasoning_time_ms=0.0,
            steps=[]
        )
        
        try:
            # Step 1: Divergent Thinking (Generate multiple approaches)
            candidates = await self._generate_candidates(
                goal=goal,
                context=context,
                constraints=constraints,
                memory_context=memory_context
            )
            
            trace.candidates = candidates
            trace.steps.append(ReasoningStep(
                step_id="generate",
                content=f"Generated {len(candidates)} candidate plans",
                confidence=0.0,
                reasoning_type="generate"
            ))
            
            # Step 2: Self-Reflection (Critique each approach)
            critiques = await self._critique_candidates(
                candidates=candidates,
                goal=goal,
                context=context
            )
            
            trace.critiques = critiques
            
            # Step 3: Convergent Selection (Select best plan)
            best_plan, confidence = await self._select_best_plan(
                candidates=candidates,
                critiques=critiques
            )
            
            trace.selected_plan = best_plan
            trace.confidence = confidence
            trace.reasoning_time_ms = (time.time() - start_time) * 1000
            
            trace.steps.append(ReasoningStep(
                step_id="select",
                content=f"Selected plan with confidence {confidence:.2f}",
                confidence=confidence,
                reasoning_type="refine"
            ))
            
            logger.info(f"Deliberation completed (confidence={confidence:.2f}, time={trace.reasoning_time_ms:.0f}ms)")
            
            return best_plan, trace
            
        except Exception as e:
            logger.error(f"Deliberation failed: {e}")
            # Fallback to simple generation
            fallback_plan = await self._fallback_generation(goal, context)
            trace.selected_plan = fallback_plan
            trace.confidence = 0.5
            trace.reasoning_time_ms = (time.time() - start_time) * 1000
            
            return fallback_plan, trace

    async def _generate_candidates(
        self,
        goal: str,
        context: Dict[str, Any],
        constraints: Optional[List[str]],
        memory_context: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Generate multiple candidate approaches."""
        
        # Build prompt
        prompt = self._build_generation_prompt(
            goal=goal,
            context=context,
            constraints=constraints,
            memory_context=memory_context
        )
        
        # Generate candidates
        if self.enable_tot:
            # Tree of Thoughts: generate with intermediate reasoning steps
            candidates = await self._generate_with_tot(prompt)
        else:
            # Standard generation
            candidates = await self._generate_standard(prompt)
        
        return candidates

    def _build_generation_prompt(
        self,
        goal: str,
        context: Dict[str, Any],
        constraints: Optional[List[str]],
        memory_context: Optional[str]
    ) -> str:
        """Build the prompt for generating candidates."""
        
        prompt = f"Goal: {goal}\n\n"
        
        if context:
            prompt += f"Context: {self._format_context(context)}\n\n"
        
        if memory_context:
            prompt += f"Previous Experience:\n{memory_context}\n\n"
        
        if constraints:
            prompt += f"Constraints:\n"
            for constraint in constraints:
                prompt += f"- {constraint}\n"
            prompt += "\n"
        
        prompt += """Generate {num_candidates} distinct, detailed approaches to achieve this goal.
Each approach should include:
1. A clear step-by-step plan
2. Required tools or resources
3. Potential risks and mitigations

Format each approach as:
APPROACH {n}:
[Detailed plan here]

""".format(num_candidates=self.max_candidates)
        
        return prompt

    async def _generate_with_tot(self, prompt: str) -> List[Dict[str, Any]]:
        """Generate candidates using Tree of Thoughts reasoning."""
        
        # First, generate intermediate thoughts
        thoughts_prompt = prompt + """
Before generating the final approaches, think step-by-step:
1. What are the key sub-problems to solve?
2. What are different strategies for each sub-problem?
3. How can these be combined into complete approaches?

THOUGHTS:
"""
        
        thoughts_response = await self.llm.generate(thoughts_prompt)
        
        # Now generate approaches based on thoughts
        approaches_prompt = prompt + f"""
Based on this reasoning:
{thoughts_response}

Now generate the {self.max_candidates} approaches as requested:
"""
        
        approaches_response = await self.llm.generate(approaches_prompt)
        
        # Parse the response
        return self._parse_candidates(approaches_response)

    async def _generate_standard(self, prompt: str) -> List[Dict[str, Any]]:
        """Generate candidates using standard generation."""
        
        response = await self.llm.generate(prompt)
        return self._parse_candidates(response)

    def _parse_candidates(self, response: str) -> List[Dict[str, Any]]:
        """Parse candidate plans from LLM response."""
        candidates = []
        
        # Split by "APPROACH" and parse each
        sections = response.split("APPROACH")
        
        for i, section in enumerate(sections[1:], 1):  # Skip first empty section
            if section.strip():
                # Extract the plan content
                lines = section.strip().split('\n')
                plan_content = []
                
                for line in lines:
                    if line and not line.startswith(str(i) + ':'):
                        plan_content.append(line)
                
                plan = '\n'.join(plan_content).strip()
                
                if plan:
                    candidates.append({
                        "id": f"candidate_{i}",
                        "plan": plan,
                        "raw_response": section.strip()
                    })
        
        # Ensure we have the requested number of candidates
        while len(candidates) < self.max_candidates:
            candidates.append({
                "id": f"candidate_{len(candidates) + 1}",
                "plan": "[Failed to generate distinct approach]",
                "raw_response": ""
            })
        
        return candidates[:self.max_candidates]

    async def _critique_candidates(
        self,
        candidates: List[Dict[str, Any]],
        goal: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Critique each candidate approach."""
        
        critiques = []
        
        for candidate in candidates:
            critique_prompt = f"""
Goal: {goal}

Proposed Approach:
{candidate['plan']}

Critique this approach for:
1. Feasibility (Can it actually be done?)
2. Efficiency (Is it optimal?)
3. Safety (Are there risks?)
4. Completeness (Does it fully address the goal?)

Provide a score from 0.0 to 1.0 and explain your reasoning.

Format:
SCORE: [0.0-1.0]
REASONING: [Detailed critique]
"""
            
            critique_response = await self.llm.generate(critique_prompt)
            
            # Parse the critique
            score = self._extract_score(critique_response)
            reasoning = self._extract_reasoning(critique_response)
            
            critiques.append({
                "candidate_id": candidate["id"],
                "score": score,
                "reasoning": reasoning,
                "full_response": critique_response
            })
        
        return critiques

    def _extract_score(self, response: str) -> float:
        """Extract score from critique response."""
        import re
        
        match = re.search(r'SCORE:\s*([0-9.]+)', response)
        if match:
            try:
                return float(match.group(1))
            except:
                pass
        
        # Default score if parsing fails
        return 0.5

    def _extract_reasoning(self, response: str) -> str:
        """Extract reasoning from critique response."""
        
        lines = response.split('\n')
        reasoning_lines = []
        capture = False
        
        for line in lines:
            if line.startswith('REASONING:'):
                capture = True
                reasoning_lines.append(line.replace('REASONING:', '').strip())
            elif capture and line.strip():
                reasoning_lines.append(line.strip())
        
        return '\n'.join(reasoning_lines)

    async def _select_best_plan(
        self,
        candidates: List[Dict[str, Any]],
        critiques: List[Dict[str, Any]]
    ) -> Tuple[str, float]:
        """Select the best plan based on critiques."""
        
        # Find the highest scoring candidate
        best_score = 0.0
        best_plan = ""
        
        for critique in critiques:
            if critique["score"] > best_score:
                best_score = critique["score"]
                
                # Find the corresponding candidate
                for candidate in candidates:
                    if candidate["id"] == critique["candidate_id"]:
                        best_plan = candidate["plan"]
                        break
        
        # If no plan meets threshold, try to refine
        if best_score < self.critique_threshold:
            logger.warning(f"Best plan score {best_score:.2f} below threshold {self.critique_threshold}")
            best_plan = await self._refine_plan(best_plan, critiques)
        
        return best_plan, best_score

    async def _refine_plan(
        self,
        plan: str,
        critiques: List[Dict[str, Any]]
    ) -> str:
        """Refine a plan based on critiques."""
        
        # Collect all critique reasoning
        all_critiques = '\n'.join([
            c["reasoning"] for c in critiques
            if c["reasoning"]
        ])
        
        refine_prompt = f"""
Original Plan:
{plan}

Critiques:
{all_critiques}

Please refine the plan to address the critiques while maintaining its core approach.
Provide the improved plan:
"""
        
        refined = await self.llm.generate(refine_prompt)
        return refined.strip()

    async def _fallback_generation(
        self,
        goal: str,
        context: Dict[str, Any]
    ) -> str:
        """Fallback simple generation if deliberation fails."""
        
        prompt = f"Generate a simple plan to achieve: {goal}\n\n"
        
        if context:
            prompt += f"Context: {self._format_context(context)}\n\n"
        
        prompt += "Plan:\n"
        
        return await self.llm.generate(prompt)

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for prompts."""
        formatted = []
        
        for key, value in context.items():
            if isinstance(value, dict):
                formatted.append(f"{key}: {self._format_context(value)}")
            elif isinstance(value, list):
                formatted.append(f"{key}: {', '.join(map(str, value))}")
            else:
                formatted.append(f"{key}: {value}")
        
        return '\n'.join(formatted)


def create_reasoning_kernel(
    llm_client,
    max_candidates: int = 3,
    critique_threshold: float = 0.7,
    enable_tree_of_thoughts: bool = True
) -> ReasoningKernel:
    """
    Factory function to create a reasoning kernel.
    
    Args:
        llm_client: LLM client instance
        max_candidates: Number of candidate plans to generate
        critique_threshold: Minimum critique score to accept
        enable_tree_of_thoughts: Whether to use ToT reasoning
        
    Returns:
        ReasoningKernel instance
    """
    return ReasoningKernel(
        llm_client=llm_client,
        max_candidates=max_candidates,
        critique_threshold=critique_threshold,
        enable_tree_of_thoughts=enable_tree_of_thoughts
    )
