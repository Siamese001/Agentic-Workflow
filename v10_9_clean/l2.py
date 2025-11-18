# FILE: v10_9_clean/l2.py
"""
Unified L2 Execution Layer (v10_9)

This module consolidates ALL L2 responsibilities:
    • ExecutionAgent base class
    • Async model clients (OpenAI/Anthropic/Gemini stubs)
    • Strategy execution
    • RAG execution
    • Bullet execution
    • Draft execution
    • QA execution
    • Safety execution
    • Tool router (L1 mode → L2 executor)
    • Cost tracking
    • Resilience utilities (retry/backoff)

Pure execution:
    • NO planning
    • NO orchestration
    • NO state mutation beyond ExecutionResult payloads
"""

from __future__ import annotations
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, Awaitable, Optional

# Flattened imports
from models import ExecutionResult, PlanObject
from exceptions import ToolExecutionError
from observability import CostTracker


# ============================================================================
# EXECUTION INTERFACE
# ============================================================================

class ExecutionAgent(ABC):
    """Abstract L2 executor interface."""

    @abstractmethod
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
        raise NotImplementedError


# ============================================================================
# ASYNC CLIENTS (stubs for OpenAI/Anthropic/Gemini)
# ============================================================================

class BaseAsyncClient:
    def __init__(self, model: str, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.endpoint = endpoint

    async def chat_completion_async(self, messages: Any, **kwargs: Any) -> Dict[str, Any]:
        raise NotImplementedError


class AsyncOpenAIClient(BaseAsyncClient):
    async def chat_completion_async(self, messages: Any, **kwargs: Any) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return {"model": self.model, "choices": [{"message": {"content": "ok"}}], "usage": {}}


class AsyncAnthropicClient(BaseAsyncClient):
    async def chat_completion_async(self, messages: Any, **kwargs: Any) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return {"model": self.model, "content": [{"text": "ok"}], "usage": {}}


class AsyncGeminiClient(BaseAsyncClient):
    async def chat_completion_async(self, messages: Any, **kwargs: Any) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return {"model": self.model, "candidates": [{"content": {"parts": [{"text": "ok"}]}}], "usage": {}}


def build_client(model: str) -> BaseAsyncClient:
    m = (model or "").lower()
    if "claude" in m:
        return AsyncAnthropicClient(model)
    if "gemini" in m:
        return AsyncGeminiClient(model)
    return AsyncOpenAIClient(model)


# ============================================================================
# RESILIENCE UTILITIES
# ============================================================================

async def retry_async(fn: Callable[[], Awaitable[Any]], attempts: int = 3, delay: float = 0.1) -> Any:
    last_exc = None
    for attempt in range(attempts):
        try:
            return await asyncio.wait_for(fn(), timeout=30.0)
        except Exception as exc:
            last_exc = exc
            await asyncio.sleep(delay * (attempt + 1))
    if last_exc:
        raise last_exc
    raise RuntimeError("retry_async failed without exception")


# ============================================================================
# STRATEGY EXECUTION
# ============================================================================

async def execute_strategy(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
    try:
        objective = plan.objective or "unspecified-objective"
        constraints = plan.constraints or []
        dependencies = plan.dependencies or []
        deliverables = plan.deliverables or []

        outline = [f"Clarify: {objective}", "Assess context", f"Deliverables: {deliverables}"]
        next_actions = [f"Generate: {deliverables[0]}"] if deliverables else ["Draft summary"]

        payload = {
            "objective": objective,
            "constraints": constraints,
            "dependencies": dependencies,
            "deliverables": deliverables,
            "outline": outline,
            "next_actions": next_actions,
        }

        return ExecutionResult(status=ExecutionResult.SUCCESS, payload=payload, model="strategy-stub", usage={})

    except Exception as exc:
        raise ToolExecutionError(f"Strategy execution failed: {exc}") from exc


# ============================================================================
# RAG EXECUTION
# ============================================================================

from retrieval import normalize_documents, dedupe_results, rerank_results, fuse_results
from ranking import bm25_rank, dense_rank, hybrid_rank

async def execute_rag(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
    try:
        fragment = plan.retrieval or {}
        queries = fragment.get("queries") or []
        filters = fragment.get("filters") or {}
        ranking_cfg = fragment.get("ranking") or {}

        client = build_client(plan.handoff.get("model") or "gpt-4.1")

        # Deterministic stub retrieval
        raw_results = [
            {"query": q, "evidence": f"stub evidence for {q}", "rank": 0}
            for q in queries
        ]

        docs = normalize_documents(raw_results)
        docs = dedupe_results(docs)

        strat = ranking_cfg.get("strategy", "hybrid")
        if strat == "bm25":
            docs = bm25_rank(docs)
        elif strat == "dense":
            docs = dense_rank(docs)
        else:
            docs = hybrid_rank(docs)

        docs = rerank_results(docs, strat)
        fused = fuse_results([docs])

        payload = {
            "queries": queries,
            "filters": filters,
            "ranking": ranking_cfg,
            "documents": fused,
        }

        return ExecutionResult(
            status=ExecutionResult.SUCCESS,
            payload=payload,
            model=client.model,
            usage={}
        )

    except Exception as exc:
        raise ToolExecutionError(f"RAG execution failed: {exc}") from exc


# ============================================================================
# BULLET EXECUTION
# ============================================================================

async def execute_bullets(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
    try:
        step = plan.steps[0]
        highlights = step.get("highlight_order") or []
        metrics_focus = step.get("metrics_focus") or []

        bullets = [
            f"• Delivered impact: {h} (metrics: {', '.join(metrics_focus[:2])})"
            for h in highlights
        ]

        payload = {
            "bullets": bullets,
            "target_sections": step.get("target_sections") or [],
            "guidelines": step.get("style_guidelines") or [],
            "validation_checks": step.get("validation_checks") or [],
        }

        client = build_client(plan.handoff.get("model") or "gpt-4.1")

        return ExecutionResult(status=ExecutionResult.SUCCESS, payload=payload, model=client.model, usage={})

    except Exception as exc:
        raise ToolExecutionError(f"Bullet execution failed: {exc}") from exc


# ============================================================================
# DRAFT EXECUTION
# ============================================================================

async def execute_drafting(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
    try:
        step = plan.steps[0]
        sections = step.get("sections") or []
        tone = step.get("tone") or "Professional"
        audience = step.get("audience") or "general"
        hints = step.get("hints") or []

        draft_paragraphs = [
            f"[{sec.upper()} — tone={tone}, audience={audience}] Generated narrative ({', '.join(hints[:2])})"
            for sec in sections
        ]

        payload = {
            "sections": sections,
            "tone": tone,
            "audience": audience,
            "hints": hints,
            "draft": draft_paragraphs,
        }

        client = build_client(plan.handoff.get("model") or "gpt-4.1")

        return ExecutionResult(status=ExecutionResult.SUCCESS, payload=payload, model=client.model, usage={})

    except Exception as exc:
        raise ToolExecutionError(f"Draft execution failed: {exc}") from exc


# ============================================================================
# QA EXECUTION
# ============================================================================

def _run_qa_checks(checks: List[str], audience: str, content: str) -> Dict[str, bool]:
    results = {}
    forbidden = ["lorem ipsum", "fake placeholder", "insert text here"]

    for ch in checks:
        if ch == "content_not_empty":
            results[ch] = bool(content.strip())
        elif ch == "no_forbidden_phrases":
            results[ch] = not any(f in content.lower() for f in forbidden)
        elif ch == "logical_consistency":
            results[ch] = len(content.split()) > 5
        elif ch == "factual_coherence":
            results[ch] = content.endswith(".")
        elif ch == "format_integrity":
            results[ch] = "\n\n" not in content
        elif ch == "child_safe_language":
            results[ch] = not any(x in content.lower() for x in ["violent", "explicit", "adult"])
        else:
            results[ch] = True
    return results


async def execute_qa(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
    try:
        step = plan.steps[0]
        checks = step.get("checks") or []
        audience = step.get("audience") or "general"

        # Find content from draft or bullets
        content = ""
        d = state.get("draft_result")
        if isinstance(d, dict) and "draft" in d:
            data = d["draft"]
            content = "\n".join(data) if isinstance(data, list) else str(data)
        b = state.get("bullet_result")
        if isinstance(b, dict) and "bullets" in b and not content:
            content = "\n".join(str(x) for x in b["bullets"])

        results = _run_qa_checks(checks, audience, content)
        failed = [k for k, ok in results.items() if not ok]

        confidence = round((len(results) - len(failed)) / max(1, len(results)), 3)
        passed = len(failed) == 0

        payload = {
            "qa_report": {
                "issues": failed,
                "confidence": confidence,
                "passed": passed,
            }
        }

        return ExecutionResult(status=ExecutionResult.SUCCESS, payload=payload, model="qa-stub", usage={})

    except Exception as exc:
        raise ToolExecutionError(f"QA execution failed: {exc}") from exc


# ============================================================================
# SAFETY EXECUTION
# ============================================================================

import re
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\b(?:\+?1[ -]?)?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}\b")

def _sanitize(text: str) -> str:
    text = EMAIL_RE.sub("[EMAIL_REDACTED]", text)
    text = PHONE_RE.sub("[PHONE_REDACTED]", text)
    return text

async def execute_safety(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
    try:
        step = plan.steps[0]
        rules = step.get("rules") or []
        audience = step.get("audience") or "general"

        # Collect content from draft or bullets
        content = ""
        d = state.get("draft_result")
        if isinstance(d, dict) and "draft" in d:
            data = d["draft"]
            content = "\n".join(data) if isinstance(data, list) else str(data)
        b = state.get("bullet_result")
        if isinstance(b, dict) and "bullets" in b and not content:
            content = "\n".join(str(x) for x in b["bullets"])

        sanitized = _sanitize(content)

        issues = []
        if sanitized != content:
            issues.append("pii_redacted")

        forbidden_terms = ["violence", "explicit", "adult"]
        if "forbidden_content_scan" in rules:
            for term in forbidden_terms:
                if term in content.lower():
                    issues.append(f"unsafe:{term}")

        if "bias_scan" in rules:
            for term in ["he/she", "his/her", "old", "young"]:
                if term in content.lower():
                    issues.append(f"bias:{term}")

        if "toxicity_scan" in rules:
            if content.count("!") > 5:
                issues.append("high_exclamation_density")

        if "child_protection_rules" in rules and audience.lower() == "children":
            if any(t in content.lower() for t in forbidden_terms):
                issues.append("child_violation")

        issues = sorted(set(issues))

        payload = {
            "safety_report": {
                "issues": issues,
                "passed": len(issues) == 0,
                "audience": audience,
                "sensitivity": step.get("sensitivity") or "normal",
            },
            "sanitized_content": sanitized,
        }

        return ExecutionResult(status=ExecutionResult.SUCCESS, payload=payload, model="safety-stub", usage={})

    except Exception as exc:
        raise ToolExecutionError(f"Safety execution failed: {exc}") from exc


# ============================================================================
# TOOL ROUTER
# ============================================================================

EXECUTOR_MAP: Dict[str, Callable[[PlanObject, Dict[str, Any]], Awaitable[Any]]] = {
    "strategy": execute_strategy,
    "rag": execute_rag,
    "bullets": execute_bullets,
    "drafting": execute_drafting,
    "qa": execute_qa,
    "safety": execute_safety,
}

def route_executor(plan: PlanObject) -> Callable[[PlanObject, Dict[str, Any]], Awaitable[Any]]:
    mode = (plan.mode or "").lower()
    if mode not in EXECUTOR_MAP:
        raise ToolExecutionError(f"No executor for mode '{mode}'")
    return EXECUTOR_MAP[mode]
