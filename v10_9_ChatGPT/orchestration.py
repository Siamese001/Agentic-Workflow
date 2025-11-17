"""Simplified orchestration DAG for the consolidated runtime."""
from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Dict, Iterable

from .context import WorkflowContext
from .models import MainGraphState, NodeResult
from .state_adapter import StateAdapterStack
from .strategy_stack import StrategyStack
from .rag_stack import RAGStack
from .prompt_stack import PromptStack
from .bullet_stack import BulletStack
from .drafting_stack import DraftingStack
from .qa_stack import QAStack
from .hil_stack import HILStack
from .safety_stack import SafetyStack
from .telemetry import log_event


class GraphApp:
    def __init__(self, workflow_context: WorkflowContext) -> None:
        self.ctx = workflow_context
        self.state_adapter = StateAdapterStack()
        self.strategy = StrategyStack(self.ctx.services)
        self.rag = RAGStack(self.ctx.services, self.ctx.embedding_client)
        self.prompt = PromptStack(self.ctx.services)
        self.bullet = BulletStack(self.ctx.services)
        self.drafting = DraftingStack(self.ctx.services, self.ctx.client)
        self.qa = QAStack(self.ctx.services)
        self.hil = HILStack(self.ctx.services)
        self.safety = SafetyStack(self.ctx.services)

    async def _run_once(self, job_input: Dict[str, Any]) -> MainGraphState:
        initial_message = job_input.get("prompt", "Provide assistance")
        state = self.state_adapter.apply_patch({"messages": [], "phase": "strategy"})

        plan_patch = self.strategy.plan(initial_message)
        state = self.state_adapter.apply_patch({"metadata": {"strategy_plan": plan_patch["plan"]}, "phase": "rag"})

        rag_plan = self.rag.plan(initial_message)["rag_plan"]
        rag_results = await self.rag.execute(rag_plan)
        messages = rag_results.get("messages", [])
        state = self.state_adapter.apply_patch({"messages": messages, "phase": "prompt"})

        prompt_text = self.prompt.render_prompt(initial_message, messages)["prompt"]
        bullets = self.bullet.plan(prompt_text)["bullet_plan"].bullets
        bullet_messages = self.bullet.execute(BulletPlan(bullets=bullets))["messages"]
        messages.extend(bullet_messages)
        state = self.state_adapter.apply_patch({"messages": messages, "phase": "draft"})

        draft_plan = self.drafting.plan([m.content for m in bullet_messages])["draft_plan"]
        draft_message = (await self.drafting.execute(draft_plan))["message"]
        messages.append(draft_message)
        state = self.state_adapter.apply_patch({"messages": messages, "phase": "qa"})

        qa_result = self.qa.run_checks(draft_message)["qa_result"]
        hil_decision = self.hil.assess(draft_message)["hil_decision"]
        final_message = draft_message
        if hil_decision.requires_human:
            final_message = self.hil.reconcile(draft_message)["message"]
        safety_report = self.safety.review(final_message)["safety_report"]
        state = self.state_adapter.apply_patch(
            {
                "messages": messages,
                "metadata": {
                    "qa": qa_result,
                    "hil": hil_decision,
                    "safety": safety_report,
                },
                "phase": "complete",
            }
        )
        return MainGraphState(**state)

    async def astream_events(self, job_input: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        log_event("workflow_start", {})
        final_state = await self._run_once(job_input)
        yield {"event": "final", "data": final_state}
        log_event("workflow_end", {})


from .models import BulletPlan  # placed at end to avoid circular import


def get_graph_app(workflow_context: WorkflowContext) -> GraphApp:
    return GraphApp(workflow_context)


__all__ = ["GraphApp", "get_graph_app"]
