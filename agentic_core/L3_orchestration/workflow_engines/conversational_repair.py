"""
L6 Conversational Repair & Multi-Agent Debate

Implements a simplified debate loop where specialist agents
discuss complex failures to reach consensus on fixes.
"""
import json
import logging
from typing import Any, Dict, List, Optional, Protocol

LOGGER = logging.getLogger(__name__)


class ConversationalRepair:
    """
    Manages multi-agent debate for complex failure resolution.

    Uses a simple debate loop pattern where specialist agents
    take turns analyzing and proposing fixes.
    """

    def __init__(self, llm_client=None):
        """
        Initialize the conversational repair system.

        Args:
            llm_client: LLM client for agent responses
        """
        self.llm_client = llm_client
        self.max_rounds = 3

        # Specialist agent configurations
        self.specialists = {
            "sherlock": {
                "name": "Sherlock",
                "role": "Root Cause Analysis",
                "prompt_template": self._get_sherlock_prompt()
            },
            "safety": {
                "name": "SafetyInspector",
                "role": "Security Review",
                "prompt_template": self._get_safety_prompt()
            },
            "dependency": {
                "name": "DependencySentinel",
                "role": "Import Analysis",
                "prompt_template": self._get_dependency_prompt()
            },
            "architecture": {
                "name": "ArchitectureGovernor",
                "role": "Architecture Compliance",
                "prompt_template": self._get_architecture_prompt()
            }
        }

    async def debate_failure(self, failure_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate multi-agent debate to resolve a failure.

        Args:
            failure_context: Context about the failure

        Returns:
            Debate results including consensus fix
        """
        LOGGER.info(f"🗣️  Initiating conversational repair for failure")

        debate_log = []
        specialist_responses = {}

        # Round 1: Initial analysis
        LOGGER.info("Round 1: Initial specialist analysis")
        for specialist_id, config in self.specialists.items():
            response = await self._query_specialist(
                specialist_id,
                failure_context,
                previous_responses=[]
            )

            specialist_responses[specialist_id] = response
            debate_log.append({
                "round": 1,
                "specialist": config["name"],
                "analysis": response["analysis"],
                "proposal": response["proposal"]
            })

            LOGGER.info(f"  {config['name']}: {response['analysis'][:100]}...")

        # Round 2: Reactive analysis
        LOGGER.info("Round 2: Reactive analysis and refinement")
        for specialist_id, config in self.specialists.items():
            # Get other specialists' responses
            others = [
                f"{self.specialists[oid]['name']}: {specialist_responses[oid]['proposal']}"
                for oid in self.specialists
                if oid != specialist_id
            ]

            response = await self._query_specialist(
                specialist_id,
                failure_context,
                previous_responses=others
            )

            # Update response
            specialist_responses[specialist_id] = response
            debate_log.append({
                "round": 2,
                "specialist": config["name"],
                "analysis": response["analysis"],
                "proposal": response["proposal"]
            })

            LOGGER.info(f"  {config['name']} (refined): {response['analysis'][:100]}...")

        # Round 3: Final consensus
        LOGGER.info("Round 3: Final consensus building")
        consensus_prompt = self._build_consensus_prompt(specialist_responses)

        consensus_response = await self._query_llm(consensus_prompt)

        # Extract final code block
        consensus_code = self._extract_code_block(consensus_response)

        result = {
            "success": consensus_code is not None,
            "consensus_code": consensus_code,
            "debate_log": debate_log,
            "specialist_responses": specialist_responses,
            logger.info("[L6_AUDIT] Action at line 131")
            "consensus_reasoning": consensus_response
        }

        if result["success"]:
            LOGGER.info("[OK] Consensus reached on fix")
        else:
            LOGGER.warning("[!]  No consensus reached")

        return result

    async def _query_specialist(self, specialist_id: str,
                               failure_context: Dict[str, Any],
                               previous_responses: List[str]) -> Dict[str, str]:
        """
        Query a specialist agent for analysis and proposal.

        Args:
            specialist_id: ID of the specialist
            failure_context: Failure context
            previous_responses: Previous specialist responses

        Returns:
            Specialist response with analysis and proposal
        """
        config = self.specialists[specialist_id]

        # Build prompt
        prompt = config["prompt_template"].format(
            failure_info=json.dumps(failure_context, indent=2),
            previous_responses="\n\n".join(previous_responses) if previous_responses else "None yet"
        )

        # Query LLM
        response = await self._query_llm(prompt)

        # Parse response
        analysis = self._extract_section(response, "ANALYSIS")
        proposal = self._extract_section(response, "PROPOSAL")

        return {
            "analysis": analysis or response,
            "proposal": proposal or response
        }

    async def _query_llm(self, prompt: str) -> str:
        """
        Query the LLM with a prompt.

        Args:
            prompt: The prompt to send

        Returns:
            LLM response
        """
        if not self.llm_client:
            # Mock response for testing
            return f"Mock response for: {prompt[:50]}..."

        try:
            # Try to use OpenAI
            import openai

            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )

            return response.choices[0].message.content

        except ImportError:
            LOGGER.warning("openai not installed - using mock response")
            return f"Mock response for: {prompt[:50]}..."
        except Exception as e:
            LOGGER.error(f"LLM query failed: {e}")
            return f"Error: Unable to query LLM"

    def _extract_section(self, response: str, section: str) -> Optional[str]:
        """
        Extract a section from LLM response.

        Args:
            response: LLM response
            section: Section name to extract

        Returns:
            Section content or None
        """
        lines = response.split('\n')
        in_section = False
        section_lines = []

        for line in lines:
            if line.strip().startswith(f"{section}:"):
                in_section = True
                content = line.replace(f"{section}:", "").strip()
                if content:
                    section_lines.append(content)
            elif in_section and line.strip():
                if any(line.strip().startswith(s) for s in ["ANALYSIS:", "PROPOSAL:", "CONSENSUS:"]):
                    break
                section_lines.append(line.strip())

        return '\n'.join(section_lines) if section_lines else None

    def _extract_code_block(self, response: str) -> Optional[str]:
        """
        Extract Python code block from response.

        Args:
            response: LLM response

        Returns:
            Python code or None
        """
        import re

        # Look for ```python blocks
        pattern = r'```python\n(.*?)\n```'
        match = re.search(pattern, response, re.DOTALL)

        if match:
            return match.group(1).strip()

        # Look for any ``` block
        pattern = r'```\n(.*?)\n```'
        match = re.search(pattern, response, re.DOTALL)

        if match:
            return match.group(1).strip()

        return None

    def _build_consensus_prompt(self, specialist_responses: Dict[str, Dict[str, str]]) -> str:
        """
        Build prompt for consensus extraction.

        Args:
            specialist_responses: All specialist responses

        Returns:
            Consensus prompt
        """
        prompt = """Based on the following specialist analyses and proposals, extract the CONSENSUS FIX that addresses all concerns:

SPECIALIST INPUTS:
"""

        for specialist_id, response in specialist_responses.items():
            config = self.specialists[specialist_id]
            prompt += f"\n{config['name']} ({config['role']}):\n"
            prompt += f"Analysis: {response['analysis']}\n"
            prompt += f"Proposal: {response['proposal']}\n"

        prompt += """

TASK:
Review all proposals and extract the best consensus fix that:
1. Addresses the root cause (Sherlock's concern)
2. Maintains security (SafetyInspector's concern)
3. Fixes imports/dependencies (DependencySentinel's concern)
4. Follows architecture rules (ArchitectureGovernor's concern)

logger.info("[L6_AUDIT] Action at line 296")
Format your response as:
CONSENSUS: [Brief explanation of the consensus approach]

CODE:
[The final consensus code fix]
```
"""

        return prompt

    def _get_sherlock_prompt(self) -> str:
        """Get Sherlock's root cause analysis prompt."""
        return """You are Sherlock, the Root Cause Analysis specialist.

FAILURE INFORMATION:
{failure_info}

PREVIOUS RESPONSES:
{previous_responses}

ANALYSIS:
Analyze the failure to identify the root cause. Consider:
- What exactly is failing?
- Why is it failing?
- What are the contributing factors?
- What's the minimal fix needed?

PROPOSAL:
Propose a specific code fix that addresses the root cause.
Provide clear, actionable Python code.
"""

    def _get_safety_prompt(self) -> str:
        """Get SafetyInspector's security review prompt."""
        return """You are SafetyInspector, the Security specialist.

FAILURE INFORMATION:
{failure_info}

PREVIOUS RESPONSES:
{previous_responses}

ANALYSIS:
Analyze the failure from a security perspective:
- Are there any security vulnerabilities?
- Could the fix introduce security issues?
- Are there unsafe operations?
- Is input validation needed?

PROPOSAL:
Propose a fix that maintains security best practices.
Ensure no security regressions.
"""

    def _get_dependency_prompt(self) -> str:
        """Get DependencySentinel's import analysis prompt."""
        return """You are DependencySentinel, the Import/Dependency specialist.

FAILURE INFORMATION:
{failure_info}

PREVIOUS RESPONSES:
{previous_responses}

ANALYSIS:
Analyze the failure from a dependency perspective:
- Are there missing imports?
- Are imports incorrectly ordered?
- Are there circular dependencies?
- Are external dependencies available?

PROPOSAL:
Propose a fix that resolves import/dependency issues.
Ensure all imports are correct and available.
"""

    def _get_architecture_prompt(self) -> str:
        """Get ArchitectureGovernor's compliance review prompt."""
        return """You are ArchitectureGovernor, the Architecture Compliance specialist.

FAILURE INFORMATION:
{failure_info}

PREVIOUS RESPONSES:
{previous_responses}

ANALYSIS:
Analyze the failure from an architecture perspective:
- Does this violate architectural rules?
- Is the code properly structured?
- Are naming conventions followed?
- Is the file in the correct location?

PROPOSAL:
Propose a fix that maintains architectural integrity.
Ensure compliance with all architectural laws.
"""


# Global instance
_conversational_repair: Optional[ConversationalRepair] = None


def get_conversational_repair() -> ConversationalRepair:
    """Get or create the global ConversationalRepair instance."""
    global _conversational_repair
    if _conversational_repair is None:
        _conversational_repair = ConversationalRepair()
    return _conversational_repair


async def initialize_conversational_repair(llm_client=None):
    """
    Initialize the conversational repair system.

    Args:
        llm_client: LLM client instance
    """
    global _conversational_repair
    _conversational_repair = ConversationalRepair(llm_client)
    LOGGER.info("Conversational repair system initialized")


# Convenience function
async def debate_complex_failure(failure_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initiate debate for a complex failure.

    Args:
        failure_context: Context about the failure

    Returns:
        Debate results
    """
    repair = get_conversational_repair()
    return await repair.debate_failure(failure_context)
