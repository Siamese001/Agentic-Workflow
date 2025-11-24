from __future__ import annotations

"""Lightweight communication channel between workflow agents.

This module defines a simple in-memory "bus" that lets different agents in
the workflow pass messages to one another. In business terms, it is the
handoff mechanism that keeps each step of the resume process informed about
what the others have already done.

By keeping these handoffs predictable and contained, the bus helps preserve
important details about a candidate's experience as work moves from parsing to
rewriting to quality checks. That coordination reduces the risk of losing key
achievements or duplicating work, which in turn supports clearer, more
coherent resumes for each job.
"""

from dataclasses import dataclass, field
from typing import Dict, List

from models import AgentMessage


@dataclass
class AgentBus:
    """In-memory mailbox for agents collaborating on a resume.

    The bus gives each agent its own queue of messages so that planning,
    drafting, and review steps can exchange information in an organized way.
    Because it runs entirely in memory and behaves predictably, it is safe for
    tests and for small-scale orchestration while still mirroring how agents
    would coordinate in production.

    From a business perspective, this coordination channel helps ensure that
    insights about a candidate's skills, gaps, and target role are shared
    across steps. That way, later agents do not overlook important context and
    the final resume remains consistent, focused, and aligned with the job.
    """

    _queues: Dict[str, List[AgentMessage]] = field(default_factory=dict)

    def send_message(self, message: AgentMessage) -> None:
        """Deliver a message to the agent responsible for the next step.

        Each message typically carries context or results from an earlier
        stage of the workflow. Routing it through this bus means downstream
        agents can pick up exactly what they need to refine, review, or score
        the resume without redoing work or guessing about prior decisions.
        """

        queue = self._queues.setdefault(message.target_agent_id, [])
        queue.append(message)

    def get_messages_for(self, agent_id: str) -> List[AgentMessage]:
        """Retrieve all messages waiting for a given agent.

        In practice this lets an agent see everything that earlier steps have
        discovered or decided about the candidate and role. That shared view
        supports better judgments about what to highlight, clarify, or remove
        in the resume.
        """

        return list(self._queues.get(agent_id, []))

    def clear(self) -> None:
        """Reset all agent queues.

        This is mainly used when starting a fresh workflow run or cleaning up
        between tests, so each resume is processed independently without
        leaking information from previous runs.

        This helps to ensure that each resume is produced in isolation, without
        any residual information from previous runs that could impact its quality.
        """

        self._queues.clear()

    # Phase-1 compatibility helpers -------------------------------------

    def send(self, message: AgentMessage) -> None:
        """Compatibility alias that forwards to ``send_message``.

        This keeps older code paths working while still benefiting from the
        same, predictable message handling that newer parts of the workflow
        rely on to coordinate resume improvements.
        """

        self.send_message(message)

    def get_for(self, agent_id: str) -> List[AgentMessage]:
        """Compatibility alias that forwards to ``get_messages_for``.

        Older callers can still retrieve all messages for an agent without
        being aware of newer APIs. This helps maintain stability as the
        workflow evolves, which is important for keeping resume outputs
        consistent over time.
        """

        return self.get_messages_for(agent_id)
