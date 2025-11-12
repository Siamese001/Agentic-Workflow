"""Retrieval planning utilities."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence


@dataclass
class RetrievalJob:
    tool: str
    query: str
    scope: str = "outreach"
    section: str = "value_wedge"


@dataclass
class RetrievalPlan:
    wants: Sequence[str]
    context: Dict[str, str]
    jobs: List[RetrievalJob] = field(default_factory=list)

    def add(self, job: Dict[str, str] | RetrievalJob) -> None:
        if isinstance(job, RetrievalJob):
            self.jobs.append(job)
        else:
            self.jobs.append(RetrievalJob(**job))

    def dedupe(self) -> None:
        unique: Dict[tuple[str, str], RetrievalJob] = {}
        for job in self.jobs:
            key = (job.tool, job.query)
            unique[key] = job
        self.jobs = list(unique.values())

    def budget(self, max_calls: int = 6) -> None:
        self.jobs = self.jobs[: max(0, max_calls)]

    def execute(
        self,
        registry,
        store,
        *,
        conductor=None,
    ) -> List[tuple[str, RetrievalJob, object]]:
        ttl_s = int(self.context.get("ttl_s", 60 * 60 * 24 * 90))
        ordered: Dict[int, tuple[str, RetrievalJob, object]] = {}
        pending_factories = []
        for idx, job in enumerate(self.jobs):
            cache_key = registry.make_key(
                {"tool": job.tool, "query": job.query, "scope": job.scope}, self.context
            )
            cached = store.get(cache_key, ttl_s=ttl_s)
            if cached and cached[2]:
                ordered[idx] = ("cache", job, cached[0])
                continue
            tool = registry.resolve(job.tool)
            tool_context = {
                "company_id": self.context.get("company_id"),
                "contact_id": self.context.get("contact_id"),
            }

            def _call_tool(tool=tool, job=job, cache_key=cache_key, tool_context=tool_context):
                outcome = tool.run(job.query, tool_context)

                def _store(result):
                    store.put(cache_key, result, {"tool": job.tool, "scope": job.scope})

                return outcome, _store

            if conductor is not None:
                def factory(idx=idx, job=job, cache_key=cache_key, tool=tool, tool_context=tool_context):
                    def _call():
                        outcome = tool.run(job.query, tool_context)
                        store.put(cache_key, outcome, {"tool": job.tool, "scope": job.scope})
                        payload = ("live", job, outcome)
                        latency = getattr(outcome, "latency_ms", 0)
                        return payload, latency

                    return conductor.wrap_tool_call(idx, _call)

                pending_factories.append(factory())
            else:
                outcome, store_callback = _call_tool()
                store_callback(outcome)
                ordered[idx] = ("live", job, outcome)

        if conductor is not None and pending_factories:
            live_results = conductor.run(pending_factories)
            for result in live_results:
                idx, value = result  # conductor returns (idx, payload)
                ordered[idx] = value

        return [ordered[i] for i in range(len(self.jobs)) if i in ordered]
