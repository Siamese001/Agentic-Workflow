from __future__ import annotations

"""
L6 Conversational Repair & Multi-Agent Debate

Implements a simplified debate loop where specialist agents
discuss complex failures to reach consensus on fixes.
"""
import json
import logging
from typing import Any

Logger: Any = logging.getLogger(__name__)


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
        self.specialists = {
            "sherlock": {
                "name": "Sherlock",
                "role": "Root Cause Analysis",
                "prompt_template": self._get_sherlock_prompt(),
            },
            "safety": {
                "name": "SafetyInspectorAgent",
                "role": "Security Review",
                "prompt_template": self._get_safety_prompt(),
            },
            "dependency": {
                "name": "DependencySentinelAgent",
                "role": "Import Analysis",
                "prompt_template": self._get_dependency_prompt(),
            },
            "architecture": {
                "name": "ArchitectureGovernor",
                "role": "Architecture Compliance",
                "prompt_template": self._get_architecture_prompt(),
            },
        }

    async def debate_failure(self, failure_context: dict[str, Any]) -> dict[str, Any]:
        """
        Initiate multi-agent debate to resolve a failure.

        Args:
            failure_context: Context about the failure

        Returns:
            Debate results including consensus fix
        """
        LOGGER.info("🗣️  Initiating conversational repair for failure")
        debate_log: Any = []
        specialist_responses: Any = {}
        LOGGER.info("Round 1: Initial specialist analysis")
        for specialist_id, config in self.specialists.items():
            response: Any = await self._query_specialist(
                specialist_id, failure_context, previous_responses=[]
            )
            specialist_responses[specialist_id] = response
            debate_log.append(
                {
                    "round": 1,
                    "specialist": config["name"],
                    "analysis": response["analysis"],
                    "proposal": response["proposal"],
                }
            )
            LOGGER.info(f"  {config['name']}: {response['analysis'][:100]}...")
        LOGGER.info("Round 2: Reactive analysis and refinement")
        for specialist_id, config in self.specialists.items():
            others: Any = [
                f"{self.specialists[oid]['name']}: {specialist_responses[oid]['proposal']}"
                for oid in self.specialists
                if oid != specialist_id
            ]
            response: Any = await self._query_specialist(
                specialist_id, failure_context, previous_responses=others
            )
            specialist_responses[specialist_id] = response
            debate_log.append(
                {
                    "round": 2,
                    "specialist": config["name"],
                    "analysis": response["analysis"],
                    "proposal": response["proposal"],
                }
            )
            LOGGER.info(f"  {config['name']} (refined): {response['analysis'][:100]}...")
        LOGGER.info("Round 3: Final consensus building")
        consensus_prompt: Any = self._build_consensus_prompt(specialist_responses)
        consensus_response: Any = await self._query_llm(consensus_prompt)
        consensus_code: Any = self._extract_code_block(consensus_response)
        result: Any = {
            "success": consensus_code is not None,
            "consensus_code": consensus_code,
            "debate_log": debate_log,
            "specialist_responses": specialist_responses,
            "consensus_reasoning": consensus_response,
        }
        if result["success"]:
            LOGGER.info("[OK] Consensus reached on fix")
        else:
            LOGGER.warning("[!]  No consensus reached")
        return result

    async def _query_specialist(
        self, specialist_id: str, failure_context: dict[str, Any], previous_responses: list[str]
    ) -> dict[str, str]:
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
        prompt = config["prompt_template"].format(
            failure_info=json.dumps(failure_context, indent=2),
            previous_responses="\n\n".join(previous_responses)
            if previous_responses
            else "None yet",
        )
        response = await self._query_llm(prompt)
        analysis = self._extract_section(response, "ANALYSIS")
        proposal = self._extract_section(response, "PROPOSAL")
        return {"analysis": analysis or response, "proposal": proposal or response}

    async def _query_llm(self, prompt: str) -> str:
        """
        Query the LLM with a prompt.

        Args:
            prompt: The prompt to send

        Returns:
            LLM response
        """
        if not self.llm_client:
            return f"Mock response for: {prompt[:50]}..."
        try:
            import openai

            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000,
            )
            return response.choices[0].message.content
        except ImportError:
            LOGGER.warning("openai not installed - using mock response")
            return f"Mock response for: {prompt[:50]}..."
        except Exception as e:
            LOGGER.error(f"LLM query failed: {e}")
            return "Error: Unable to query LLM"

    def _extract_section(self, response: str, section: str) -> str | None:
        """
        Extract a section from LLM response.

        Args:
            response: LLM response
            section: Section name to extract

        Returns:
            Section content or None
        """
        lines = response.split("\n")
        in_section = False
        section_lines = []
        for line in lines:
            if line.strip().startswith(f"{section}:"):
                in_section = True
                content = line.replace(f"{section}:", "").strip()
                if content:
                    section_lines.append(content)
            elif in_section and line.strip():
                if any(
                    line.strip().startswith(s) for s in ["ANALYSIS:", "PROPOSAL:", "CONSENSUS:"]
                ):
                    break
                section_lines.append(line.strip())
        return "\n".join(section_lines) if section_lines else None

    def _extract_code_block(self, response: str) -> str | None:
        """
        Extract Python code block from response.

        Args:
            response: LLM response

        Returns:
            Python code or None
        """
        import re

        pattern = "```python\\n(.*?)\\n```"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
        pattern = "```\\n(.*?)\\n```"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _build_consensus_prompt(self, specialist_responses: dict[str, dict[str, str]]) -> str:
        """
        Build prompt for consensus extraction.

        Args:
            specialist_responses: All specialist responses

        Returns:
            Consensus prompt
        """
        prompt = "Based on the following specialist analyses and proposals, extract the CONSENSUS FIX that addresses all concerns:\n\nSPECIALIST INPUTS:\n"
        for specialist_id, response in specialist_responses.items():
            config = self.specialists[specialist_id]
            prompt += f"\n{config['name']} ({config['role']}):\n"
            prompt += f"Analysis: {response['analysis']}\n"
            prompt += f"Proposal: {response['proposal']}\n"
        prompt += "\n\nTASK:\nReview all proposals and extract the best consensus fix that:\n1. Addresses the root cause (Sherlock's concern)\n2. Maintains security (SafetyInspectorAgent's concern)\n3. Fixes imports/dependencies (DependencySentinelAgent's concern)\n4. Follows architecture rules (ArchitectureGovernor's concern)\n\nFormat your response as:\nCONSENSUS: [Brief explanation of the consensus approach]\n\nCODE:\n[The final consensus code fix]\n```\n"
        return prompt

    def _get_sherlock_prompt(self) -> str:
        """Get Sherlock's root cause analysis prompt."""
        return "You are Sherlock, the Root Cause Analysis specialist.\n\nFAILURE INFORMATION:\n{failure_info}\n\nPREVIOUS RESPONSES:\n{previous_responses}\n\nANALYSIS:\nAnalyze the failure to identify the root cause. Consider:\n- What exactly is failing?\n- Why is it failing?\n- What are the contributing factors?\n- What's the minimal fix needed?\n\nPROPOSAL:\nPropose a specific code fix that addresses the root cause.\nProvide clear, actionable Python code.\n"

    def _get_safety_prompt(self) -> str:
        """Get SafetyInspectorAgent's security review prompt."""
        return "You are SafetyInspectorAgent, the Security specialist.\n\nFAILURE INFORMATION:\n{failure_info}\n\nPREVIOUS RESPONSES:\n{previous_responses}\n\nANALYSIS:\nAnalyze the failure from a security perspective:\n- Are there any security vulnerabilities?\n- Could the fix introduce security issues?\n- Are there unsafe operations?\n- Is input validation needed?\n\nPROPOSAL:\nPropose a fix that maintains security best practices.\nEnsure no security regressions.\n"

    def _get_dependency_prompt(self) -> str:
        """Get DependencySentinelAgent's import analysis prompt."""
        return "You are DependencySentinelAgent, the Import/Dependency specialist.\n\nFAILURE INFORMATION:\n{failure_info}\n\nPREVIOUS RESPONSES:\n{previous_responses}\n\nANALYSIS:\nAnalyze the failure from a dependency perspective:\n- Are there Missing imports?\n- Are imports incorrectly ordered?\n- Are there circular dependencies?\n- Are external dependencies available?\n\nPROPOSAL:\nPropose a fix that resolves import/dependency issues.\nEnsure all imports are correct and available.\n"

    def _get_architecture_prompt(self) -> str:
        """Get ArchitectureGovernor's compliance review prompt."""
        return "You are ArchitectureGovernor, the Architecture Compliance specialist.\n\nFAILURE INFORMATION:\n{failure_info}\n\nPREVIOUS RESPONSES:\n{previous_responses}\n\nANALYSIS:\nAnalyze the failure from an architecture perspective:\n- Does this violate architectural rules?\n- Is the code properly structured?\n- Are naming conventions followed?\n- Is the file in the correct location?\n\nPROPOSAL:\nPropose a fix that maintains architectural integrity.\nEnsure compliance with all architectural laws.\n"


_conversational_repair: ConversationalRepair | None = None


def get_conversational_repair() -> ConversationalRepair:
    """Get or create the global ConversationalRepair instance."""
    global _conversational_repair
    if _conversational_repair is None:
        _conversational_repair = ConversationalRepair()
    return _conversational_repair


async def initialize_conversational_repair(llm_client: Any = None) -> Any:
    """
    Initialize the conversational repair system.

    Args:
        llm_client: LLM client instance
    """
    global _conversational_repair
    _conversational_repair = ConversationalRepair(llm_client)
    LOGGER.info("Conversational repair system initialized")


async def debate_complex_failure(failure_context: dict[str, Any]) -> dict[str, Any]:
    """
    Initiate debate for a complex failure.

    Args:
        failure_context: Context about the failure

    Returns:
        Debate results
    """
    repair: Any = get_conversational_repair()
    return await repair.debate_failure(failure_context)
