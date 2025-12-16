""" """
import asyncio
import json
import logging

from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import List, Dict, Any

from services.configuration import ConfigurationService

LOGGER = logging.getLogger(__name__)


class ConsensusVerdict(BaseModel):
    """Result of a consensus deliberation."""
    chosen_plan: str
    consensus_score: float
    dissenting_opinions: List[str]
    reasoning: str
    safe_to_proceed: bool


class ModelOpinion(BaseModel):
    """Individual model's opinion on a plan."""
    model_name: str
    plan: str
    reasoning: str
    risk_assessment: str
    confidence: float


class SupremeCourt:
    """
    Multi-model consensus system for critical decision making.

    Queries multiple AI models and requires consensus before
    proceeding with potentially dangerous actions.
    """

    def __init__(self, primary_client: AsyncOpenAI, secondary_clients: List[tuple[AsyncOpenAI, str]]):
        """
        Initialize the Supreme Court.

        Args:
            primary_client: Primary model client (e.g., GPT-4)
            secondary_clients: List of (client, model_name) tuples
            consensus_threshold: Minimum consensus score to proceed
        """
        self.primary = primary_client
        self.jury = secondary_clients
        self.threshold = 0.7 # Default consensus threshold

        self.personas: Dict[str, Dict[str, str]] = {
            'security_engineer': {
                'role': 'You are a Security Engineer focused on safety,\n                    risks,\n                    and potential vulnerabilities.',
                'priority': 'Identify any security risks, potential for harm, or safety concerns.'},
            'product_manager': {
                'role': 'You are a Product Manager focused on user value and business impact.',
                'priority': 'Evaluate if this action delivers value and meets user needs.'},
            'quality_assurance': {
                'role': 'You are a QA Engineer focused on reliability,\n                    testing,\n                    and error handling.',
                'priority': 'Assess reliability, potential failures, and testing requirements.'}
        }
        ConfigurationService().logger.info(
            f'SupremeCourt initialized with {len(self.jury) + 1} models')

    async def deliberate(self, context: str, goal: str, risk_level: str='medium') -> ConsensusVerdict:
        """ """
        ConfigurationService().logger.info(
            f'Starting deliberation for goal: {goal}')
        opinions = await self._gather_opinions(context, goal, risk_level)
        verdict = await self._analyze_consensus(opinions, context, goal)
        if verdict.consensus_score < self.threshold:
            error_msg = f'Consensus Failure ({verdict.consensus_score:.2f} < {self.threshold})'
            if verdict.dissenting_opinions:
                error_msg += f". Dissent: {'; '.join(verdict.dissenting_opinions[:2])}"
            raise ValueError(error_msg) # Corrected to use error_msg
        ConfigurationService().logger.info(
            f'Consensus reached with score {verdict.consensus_score:.2f}')
        return verdict

    async def _gather_opinions(self, context: str, goal: str, risk_level: str) -> List[ModelOpinion]:
        """Get opinions from all models in parallel."""
        tasks = []
        # Ensure context is not excessively long, truncate if necessary
        truncated_context = context[:1000] + '...' if len(context) > 1000 else context

        tasks.append(
            self._get_opinion(
                self.primary,
                'gpt-4', # Assuming primary is always gpt-4 for this part
                truncated_context,
                goal,
                risk_level,
                'You are a Senior Software Architect. Provide a balanced, technical solution.'))

        # Cycle through personas for jury members
        persona_keys = list(self.personas.keys())
        for i, (client, model_name) in enumerate(self.jury):
            persona_name = persona_keys[i % len(persona_keys)]
            persona = self.personas[persona_name]
            tasks.append(
                self._get_opinion(
                    client,
                    model_name,
                    truncated_context,
                    goal,
                    risk_level,
                    persona['role']))

        raw_opinions = await asyncio.gather(*tasks, return_exceptions=True)

        valid_opinions: List[ModelOpinion] = []
        for opinion in raw_opinions:
            if isinstance(opinion, Exception):
                ConfigurationService().logger.error(
                    f'Model failed to provide opinion: {opinion}')
            elif opinion: # Check if opinion is not None or empty
                valid_opinions.append(opinion)
        return valid_opinions

    async def _get_opinion(self, client: AsyncOpenAI, model_name: str, context: str,
                           goal: str, risk_level: str, system_role: str) -> ModelOpinion:
        """Get opinion from a single model."""
        system_prompt = f'\n{system_role}\n\nYou are evaluating a potential action for an autonomous agent. Consider:\n\n1. The goal: {goal}\n2. The context: {context}\n3. Risk level: {risk_level}\n\nProvide:\n- A specific plan to achieve the goal\n- Your reasoning for this approach\n- Risk assessment (LOW/MEDIUM/HIGH/CRITICAL)\n- Confidence in your recommendation (0.0-1.0)\n\nBe concise but thorough. Focus on safety and reliability.\n'
        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': f'Evaluate this action: {goal}'}
                ],
                temperature=0.3,
                max_tokens=500
            )
            content = response.choices[0].message.content
            if not content:
                return ModelOpinion(model_name=model_name, plan='No plan provided', reasoning='No reasoning provided', risk_assessment='UNKNOWN', confidence=0.0)

            plan = self._extract_section(content, ['Plan:', 'Action:', 'Solution:'])
            reasoning = self._extract_section(content, ['Reasoning:', 'Rationale:', 'Because:'])
            risk = self._extract_section(content, ['Risk:', 'Risk Assessment:']).upper()
            confidence = self._extract_confidence(content)

            # Basic validation, though detailed validation is in _analyze_consensus
            if not plan: plan = 'No clear plan provided'
            if not reasoning: reasoning = 'No reasoning provided'
            if not risk: risk = 'UNKNOWN'
            if confidence is None: confidence = 0.5 # Default if extraction fails

            return ModelOpinion(model_name=model_name, plan=plan, reasoning=reasoning, risk_assessment=risk, confidence=confidence)
        except Exception as e:
            ConfigurationService().logger.error(f"Error getting opinion from {model_name}: {e}")
            # Return a default/error opinion to avoid breaking gather
            return ModelOpinion(model_name=model_name, plan='ERROR', reasoning=f'Error occurred: {e}', risk_assessment='CRITICAL', confidence=0.0)


    async def _analyze_consensus(self, opinions: List[ModelOpinion], context: str, goal: str) -> ConsensusVerdict:
        """Analyze opinions to determine consensus."""
        if not opinions:
            raise ValueError('No valid opinions received')

        high_risk_count = sum(1 for o in opinions if o.risk_assessment in ['HIGH', 'CRITICAL'])

        if high_risk_count > len(opinions) / 2:
            return ConsensusVerdict(chosen_plan='CONSENSUS_BLOCKED', consensus_score=0.0, dissenting_opinions=[
                                    f'High risk assessed by {high_risk_count}/{len(opinions)} models'], REASONING='Multiple models assessed high risk', safe_to_proceed=False)

        # Prepare prompt for consensus judge
        opinion_summaries = "\n".join([f"- Model: {o.model_name}\n  Plan: {o.plan}\n  Reasoning: {o.reasoning}\n  Risk: {o.risk_assessment}\n  Confidence: {o.confidence}" for o in opinions])
        judge_prompt = f'''
        You are a consensus judge. You will be given opinions from multiple AI models about a plan to achieve a specific goal.
        Your task is to analyze these opinions and provide a synthesized consensus verdict.

        Goal: {goal}
        Context: {context[:500]}...

        Opinions from models:
        {opinion_summaries}

        Based on these opinions, determine:
        1. A consolidated, safe, and effective plan that incorporates the best elements from the individual plans. If consensus is impossible or unsafe, state "CONSENSUS_BLOCKED" as the plan.
        2. A consensus score (0.0 to 1.0) representing the level of agreement among the models.
        3. A list of dissenting opinions or major concerns if consensus is not strong or if there are significant safety issues. Limit to the top 3.
        4. A final reasoning for your verdict, explaining the consensus plan and score.
        5. A boolean indicating if it is safe to proceed.

        Provide your response ONLY in the following JSON format:
        {{
            "consensus_plan": "string",
            "consensus_score": float,
            "dissenting_opinions": ["string", "string", ...],
            "reasoning": "string",
            "safe_to_proceed": bool
        }}
        '''
        dissenting: List[str] = []
        try:
            # Use the primary client as the judge
            response = await self.primary.chat.completions.create(
                model='gpt-4', # Assuming judge is gpt-4
                messages=[
                    {'role': 'system', 'content': 'You are a consensus judge. Respond with valid JSON only.'},
                    {'role': 'user', 'content': judge_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            judge_result_str = response.choices[0].message.content
            judge_result = json.loads(judge_result_str)

            # Collect dissenting opinions from models if risk is high/critical
            for o in opinions:
                if o.risk_assessment in ['HIGH', 'CRITICAL']:
                    dissenting.append(f'{o.model_name}: {o.reasoning} (Risk: {o.risk_assessment})')

            # Fallback for consensus_plan if not provided by judge
            chosen_plan = judge_result.get('consensus_plan', opinions[0].plan if opinions else 'No plan')
            if chosen_plan == 'CONSENSUS_BLOCKED' or not judge_result.get('safe_to_proceed', True):
                 safe_to_proceed = False
                 consensus_score = 0.0
                 chosen_plan = 'CONSENSUS_BLOCKED'
                 reasoning = judge_result.get('reasoning', 'Consensus could not be reached or action is deemed unsafe.')
                 dissenting.append('Action blocked due to lack of consensus or safety concerns.')
            else:
                safe_to_proceed = judge_result.get('safe_to_proceed', True)
                consensus_score = judge_result.get('consensus_score', 0.5)
                reasoning = judge_result.get('reasoning', 'Consensus based on model agreement')

            return ConsensusVerdict(
                chosen_plan=chosen_plan,
                consensus_score=consensus_score,
                dissenting_opinions=dissenting[:3],
                REASONING=reasoning,
                safe_to_proceed=safe_to_proceed
            )
        except Exception as e:
            ConfigurationService().logger.error(f'Judge analysis failed: {e}')
            # Fallback to simple consensus if judge fails
            return self._simple_consensus(opinions)

    def _simple_consensus(self, opinions: List[ModelOpinion]) -> ConsensusVerdict:
        """Simple fallback consensus method."""
        risk_counts: Dict[str, int] = {}
        for o in opinions:
            risk_counts[o.risk_assessment] = risk_counts.get(o.risk_assessment, 0) + 1

        if risk_counts.get('CRITICAL', 0) > 0:
            return ConsensusVerdict(chosen_plan='BLOCKED_CRITICAL_RISK', consensus_score=0.0, dissenting_opinions=[
                                    'Critical risk detected'], REASONING='Critical risk assessment requires blocking', safe_to_proceed=False)

        # If no critical risk, find the opinion with the highest confidence
        if not opinions: # Handle case where opinions list is empty
             return ConsensusVerdict(chosen_plan='NO_OPINIONS', consensus_score=0.0, dissenting_opinions=[], REASONING='No opinions were gathered', safe_to_proceed=False)

        best_opinion = max(opinions, key=lambda o: o.confidence)

        # Determine consensus score based on confidence and risk level distribution
        # This is a simplified approach. More sophisticated scoring can be implemented.
        consensus_score = 0.6 # Default score if not critical risk
        if best_opinion.confidence > 0.8:
            consensus_score = 0.7
        if risk_counts.get('HIGH', 0) > 0:
            consensus_score *= 0.8 # Reduce score if high risks exist

        return ConsensusVerdict(chosen_plan=best_opinion.plan,
                                consensus_score=consensus_score,
                                dissenting_opinions=[f'{o.model_name}: {o.reasoning}' for o in opinions if o.confidence < best_opinion.confidence and o.risk_assessment not in ['LOW', 'UNKNOWN']],
                                REASONING='Selected highest confidence plan',
                                safe_to_proceed=True) # Default to safe if not critical risk

    def _extract_section(self, text: str, markers: List[str]) -> str:
        """Extract a section from model response."""
        for marker in markers:
            if marker in text:
                start_index = text.find(marker) + len(marker)
                # Define potential end markers for the section
                end_markers = ['\n\n', 'Plan:', 'Action:', 'Solution:', 'Reasoning:', 'Rationale:', 'Because:', 'Risk:', 'Risk Assessment:', 'Confidence:']
                min_end_pos = len(text)

                # Find the earliest occurrence of any end marker after the start_index
                for next_marker in end_markers:
                    pos = text.find(next_marker, start_index)
                    if pos != -1:
                        min_end_pos = min(min_end_pos, pos)

                # Extract the text between the marker and the next marker
                section_text = text[start_index:min_end_pos].strip()
                # Remove any leading/trailing newlines that might have been captured
                return section_text.strip('\n')
        return ''

    def _extract_confidence(self, text: str) -> float:
        """Extract confidence score from text."""
        import re
        # Patterns to find confidence values
        patterns = [
            r'confidence[:\s]+(\d+\.?\d*)',           # e.g., confidence: 0.85 or confidence 85
            r'(\d+\.?\d*)%?\s*confident',             # e.g., 85% confident or 0.85 confident
            r'(\d+\.?\d*)/10'                         # e.g., 8/10
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    value = float(match.group(1))
                    # Normalize value to be between 0.0 and 1.0
                    if value > 1.0 and value <= 10.0: # Assumes "8/10" format
                        value = value / 10.0
                    elif value > 10.0 and value <= 100.0: # Assumes "85%" format
                        value = value / 100.0
                    # Ensure the value is within the valid range [0.0, 1.0]
                    return max(0.0, min(value, 1.0))
                except ValueError:
                    continue # Ignore if conversion fails
        return 0.5 # Default confidence if not found


async def create_supreme_court(openai_client: AsyncOpenAI) -> SupremeCourt:
    """Create a SupremeCourt instance with multiple models."""
    # Placeholder for secondary clients; in a real app, this would be configured.
    # For this example, we'll assume a default like gpt-3.5-turbo if not provided.
    # In a real scenario, ConfigurationService().secondary_clients would be populated.
    secondary_clients_config = getattr(ConfigurationService(), 'secondary_clients', [(openai_client, 'gpt-3.5-turbo')])

    # Ensure clients are actual AsyncOpenAI instances, not just tuples if they were configured that way
    processed_secondary_clients = []
    for client_info in secondary_clients_config:
        if isinstance(client_info, tuple) and len(client_info) == 2:
            client, model_name = client_info
            if not isinstance(client, AsyncOpenAI):
                 # If a raw client object isn't provided, create one
                 client = AsyncOpenAI() # Or use specific config if available
            processed_secondary_clients.append((client, model_name))
        elif isinstance(client_info, AsyncOpenAI): # If only a client is provided without a model name
             processed_secondary_clients.append((client_info, 'gpt-3.5-turbo')) # Default model
        else:
             ConfigurationService().logger.warning(f"Skipping invalid secondary client config: {client_info}")


    return SupremeCourt(openai_client, processed_secondary_clients)