"""
Multi-Agent Orchestration Example
Version: 1.0
Compatible with: openai>=1.0.0

Demonstrates a supervisor pattern where a coordinator agent
delegates tasks to specialized worker agents.
"""

import json
from dataclasses import dataclass
from typing import Callable
from openai import OpenAI


@dataclass
class AgentConfig:
    """Configuration for a specialized agent."""
    name: str
    system_prompt: str
    model: str = "gpt-4o-mini"


class MultiAgentOrchestrator:
    """
    Supervisor pattern orchestrator that routes tasks to specialized agents.
    """

    def __init__(self, client: OpenAI | None = None):
        self.client = client or OpenAI()
        self.agents: dict[str, AgentConfig] = {}

    def register_agent(self, config: AgentConfig) -> None:
        """Register a specialized agent."""
        self.agents[config.name] = config

    def _call_agent(self, agent_name: str, task: str) -> str:
        """Execute a task with a specific agent."""
        config = self.agents[agent_name]

        response = self.client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "system", "content": config.system_prompt},
                {"role": "user", "content": task},
            ],
        )

        return response.choices[0].message.content or ""

    def run(self, query: str, max_iterations: int = 5) -> str:
        """
        Run the orchestration loop.

        The supervisor analyzes the query and delegates to specialized agents.
        """
        agent_descriptions = "\n".join(
            f"- {name}: {config.system_prompt[:100]}..."
            for name, config in self.agents.items()
        )

        supervisor_prompt = f"""You are a supervisor agent that coordinates specialized agents.

Available agents:
{agent_descriptions}

Your job is to:
1. Analyze the user's request
2. Decide which agent(s) to delegate to
3. Synthesize the results into a final answer

Respond in JSON format:
{{"action": "delegate", "agent": "agent_name", "task": "specific task"}}
or
{{"action": "respond", "answer": "final answer"}}
"""

        messages = [
            {"role": "system", "content": supervisor_prompt},
            {"role": "user", "content": query},
        ]

        for _ in range(max_iterations):
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                response_format={"type": "json_object"},
            )

            decision = json.loads(response.choices[0].message.content)

            if decision["action"] == "respond":
                return decision["answer"]

            if decision["action"] == "delegate":
                agent_name = decision["agent"]
                task = decision["task"]

                if agent_name not in self.agents:
                    messages.append({
                        "role": "assistant",
                        "content": json.dumps(decision),
                    })
                    messages.append({
                        "role": "user",
                        "content": f"Error: Agent '{agent_name}' not found. Available: {list(self.agents.keys())}",
                    })
                    continue

                result = self._call_agent(agent_name, task)

                messages.append({
                    "role": "assistant",
                    "content": json.dumps(decision),
                })
                messages.append({
                    "role": "user",
                    "content": f"Result from {agent_name}: {result}",
                })

        return "Max iterations reached without final answer."


# Example usage
if __name__ == "__main__":
    orchestrator = MultiAgentOrchestrator()

    # Register specialized agents
    orchestrator.register_agent(AgentConfig(
        name="researcher",
        system_prompt="You are a research specialist. Provide detailed, factual information on topics. Always cite your reasoning.",
    ))

    orchestrator.register_agent(AgentConfig(
        name="writer",
        system_prompt="You are a professional writer. Create clear, engaging content. Focus on readability and structure.",
    ))

    orchestrator.register_agent(AgentConfig(
        name="critic",
        system_prompt="You are a constructive critic. Review content for accuracy, clarity, and completeness. Provide specific feedback.",
    ))

    # Run orchestration
    result = orchestrator.run(
        "Write a brief explanation of how neural networks learn, then review it for accuracy."
    )

    print("Final Result:")
    print(result)
