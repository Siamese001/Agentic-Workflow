"""Enterprise LIC orchestrator for production-like campaign planning."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from apps_lic.services.repo_signal_service import RepoSignalService


@dataclass
class EnterpriseLicRequest:
    """Request envelope for enterprise LIC campaign planning."""

    campaign_goal: str
    audience_segment: str = "technical_buyers"
    channel: str = "linkedin"
    output_mode: str = "planning"
    enable_repo_signals: bool = True
    trace_id: str = ""

    def __post_init__(self) -> None:
        if not self.trace_id:
            stamp = f"{self.campaign_goal}:{self.audience_segment}:{datetime.now().isoformat()}"
            self.trace_id = hashlib.sha256(stamp.encode()).hexdigest()[:16]


@dataclass
class EnterpriseLicResult:
    """Decision-grade output for enterprise LIC campaign planning."""

    trace_id: str
    status: str
    campaign_plan: dict[str, Any] = field(default_factory=dict)
    repo_signals: dict[str, Any] = field(default_factory=dict)
    risk_summary: dict[str, Any] = field(default_factory=dict)
    confidence_summary: dict[str, Any] = field(default_factory=dict)
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    provenance_block: dict[str, Any] = field(default_factory=dict)
    execution_log: list[dict[str, Any]] = field(default_factory=list)


class EnterpriseLicOrchestrator:
    """Production-simulation orchestrator for LIC campaign planning."""

    def __init__(self) -> None:
        self.repo_signal_service = RepoSignalService()
        self._execution_log: list[dict[str, Any]] = []

    async def process(self, request: EnterpriseLicRequest) -> EnterpriseLicResult:
        result = EnterpriseLicResult(trace_id=request.trace_id, status="processing")

        self._log_step(request.trace_id, "INGEST", "start")
        result.campaign_plan = {
            "goal": request.campaign_goal,
            "audience_segment": request.audience_segment,
            "channel": request.channel,
            "output_mode": request.output_mode,
        }
        self._log_step(request.trace_id, "INGEST", "complete")

        if request.enable_repo_signals:
            self._log_step(request.trace_id, "ENRICH", "start")
            snapshot = self.repo_signal_service.collect()
            result.repo_signals = snapshot.as_dict()
            self._log_step(
                request.trace_id,
                "ENRICH",
                "complete",
                details={
                    "adg_available": bool(result.repo_signals.get("adg", {}).get("available")),
                    "workflow_count": result.repo_signals.get("ci", {}).get("workflow_count", 0),
                    "agent_spec_count": result.repo_signals.get("governance", {})
                    .get("lic_domain", {})
                    .get("agent_spec_count", 0),
                },
            )

        self._log_step(request.trace_id, "DECIDE", "start")
        result.risk_summary = self._build_risk_summary(result.repo_signals)
        result.confidence_summary = self._build_confidence_summary(result.repo_signals)
        result.recommendations = self._build_recommendations(
            request, result.risk_summary, result.confidence_summary
        )
        result.provenance_block = {
            "captured_at": result.repo_signals.get("captured_at"),
            "files_used": result.repo_signals.get("provenance", {}),
            "trace_id": request.trace_id,
        }
        result.status = "complete"
        self._log_step(request.trace_id, "DECIDE", "complete")

        result.execution_log = self._execution_log
        return result

    def _build_risk_summary(self, repo_signals: dict[str, Any]) -> dict[str, Any]:
        governance = repo_signals.get("governance", {})
        lic_domain = governance.get("lic_domain", {})
        observability = governance.get("observability", {})

        risk_points = 0
        reasons: list[str] = []

        if not governance.get("denominator_baseline_available"):
            risk_points += 2
            reasons.append("governance_baseline_missing")

        if lic_domain.get("agent_spec_count", 0) == 0:
            risk_points += 2
            reasons.append("agent_specs_unavailable")

        if observability.get("observability_artifact_count", 0) == 0:
            risk_points += 1
            reasons.append("observability_history_missing")

        if observability.get("governance_artifact_count", 0) == 0:
            risk_points += 1
            reasons.append("governance_history_missing")

        level = "low"
        if risk_points >= 4:
            level = "high"
        elif risk_points >= 2:
            level = "medium"

        return {"score": risk_points, "level": level, "reasons": reasons}

    def _build_confidence_summary(self, repo_signals: dict[str, Any]) -> dict[str, Any]:
        adg = repo_signals.get("adg", {})
        tests = repo_signals.get("tests", {})
        ci = repo_signals.get("ci", {})

        checks = {
            "adg_available": bool(adg.get("available")),
            "test_signals_available": bool(
                tests.get("inventory_available") or tests.get("surface_available")
            ),
            "workflow_signals_available": ci.get("workflow_count", 0) > 0,
        }
        passed = sum(1 for value in checks.values() if value)
        confidence = round(passed / len(checks), 3)

        return {
            "score": confidence,
            "level": "high" if confidence >= 0.8 else "medium" if confidence >= 0.5 else "low",
            "checks": checks,
        }

    def _build_recommendations(
        self,
        request: EnterpriseLicRequest,
        risk_summary: dict[str, Any],
        confidence_summary: dict[str, Any],
    ) -> list[dict[str, Any]]:
        recommendation_level = "go"
        if risk_summary.get("level") == "high" or confidence_summary.get("level") == "low":
            recommendation_level = "hold"
        elif risk_summary.get("level") == "medium":
            recommendation_level = "go_with_guardrails"

        return [
            {
                "action": "campaign_launch_decision",
                "decision": recommendation_level,
                "rationale": {
                    "goal": request.campaign_goal,
                    "risk_level": risk_summary.get("level"),
                    "confidence_level": confidence_summary.get("level"),
                },
            },
            {
                "action": "policy_guardrail_recheck",
                "decision": "required" if recommendation_level != "go" else "recommended",
                "rationale": {
                    "reason_codes": risk_summary.get("reasons", []),
                },
            },
        ]

    def _log_step(
        self,
        trace_id: str,
        step: str,
        status: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self._execution_log.append(
            {
                "trace_id": trace_id,
                "step": step,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "details": details or {},
            },
        )

    async def execute_workflow(self, mission: Any) -> dict[str, Any]:
        """Execute outreach workflow for an OutreachMission.

        This is the CLI-facing entry point invoked by ``tools/run_workflow_lic.py``.
        Produces a personalized outreach message + QA summary in the result shape
        expected by ``print_results()``.

        Uses Gemini when ``GEMINI_API_KEY`` is present (loaded from .env); otherwise
        emits a deterministic templated fallback so the pipeline remains runnable
        offline.
        """
        import os
        import time

        start = time.perf_counter()

        # Load .env best-effort (no hard dep on python-dotenv)
        self._load_env_file()

        sender = dict(mission.sender_profile or {})
        recipient = dict(mission.recipient_profile or {})
        job = dict(mission.job_description or {})

        route = self._select_route(mission)
        archetype = self._infer_archetype(recipient, job)

        message, used_llm, llm_error = self._generate_message(sender, recipient, job, route)
        word_count = len(message.split())

        qa_summary, qa_report, production_ready = self._qa_validate(
            message=message,
            route=route,
            word_count=word_count,
        )

        elapsed = time.perf_counter() - start
        return {
            "status": "success",
            "production_ready": production_ready,
            "workflow_time": elapsed,
            "route": route,
            "archetype": archetype,
            "message": message,
            "word_count": word_count,
            "qa_summary": qa_summary,
            "qa_report": qa_report,
            "used_llm": used_llm,
            "llm_error": llm_error,
            "mission_id": getattr(mission, "mission_id", ""),
        }

    @staticmethod
    def _load_env_file() -> None:
        """Best-effort load of repo .env so GEMINI_API_KEY is available."""
        import os
        from pathlib import Path

        env_path = Path(__file__).resolve().parents[2] / ".env"
        if not env_path.exists():
            return
        try:
            with env_path.open(encoding="utf-8") as fh:
                for raw in fh:
                    line = raw.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    # Drop inline comments after first whitespace run
                    if "#" in value:
                        value = value.split("#", 1)[0].strip()
                    if key and key not in os.environ:
                        os.environ[key] = value
        except OSError:  # guardian: allow-return-none-swallow -- env file is optional; absence/read failure is non-fatal startup condition
            return

    @staticmethod
    def _select_route(mission: Any) -> str:
        status = (getattr(mission, "connection_status", "") or "").lower()
        prior = int(getattr(mission, "prior_message_count", 0) or 0)
        if prior > 0:
            return "FOLLOW_UP"
        if status == "connected":
            return "SHORT_NEW"
        return "CONNECTION_REQ"

    @staticmethod
    def _infer_archetype(recipient: dict[str, Any], job: dict[str, Any]) -> str:
        title = (recipient.get("title") or "").lower()
        if any(tok in title for tok in ("recruiter", "talent", "people")):
            return "TALENT_PARTNER"
        if any(tok in title for tok in ("founder", "ceo", "cto", "chief")):
            return "EXECUTIVE"
        if any(tok in title for tok in ("engineer", "scientist", "ml")):
            return "PRACTITIONER"
        if (job.get("title") or "").lower().startswith("head"):
            return "SENIOR_IC"
        return "GENERAL"

    def _generate_message(
        self,
        sender: dict[str, Any],
        recipient: dict[str, Any],
        job: dict[str, Any],
        route: str,
    ) -> tuple[str, bool, str]:
        import os

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return self._template_message(sender, recipient, job, route), False, "no_api_key"

        prompt = self._build_prompt(sender, recipient, job, route)
        model_name = (os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").split()[0]
        # Known-good default if .env model is a preview slug not yet GA
        if "preview" in model_name or model_name == "gemini-2.0-flash-exp":
            model_name = "gemini-2.0-flash"

        import json as _json
        import urllib.error
        import urllib.request

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}"
            f":generateContent?key={api_key}"
        )
        payload = _json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            # guardian: allow-chokepoint-bypass -- Gemini REST API direct call; all error paths (HTTP/network/parse) fall back to _template_message, no silent failure
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:200]
            return (
                self._template_message(sender, recipient, job, route),
                False,
                f"gemini_http_{exc.code}: {body}",
            )
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            return (
                self._template_message(sender, recipient, job, route),
                False,
                f"gemini_network_error: {type(exc).__name__}: {exc}",
            )

        try:
            data = _json.loads(raw)
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join(p.get("text", "") for p in parts).strip()
        except (KeyError, IndexError, ValueError) as exc:
            return (
                self._template_message(sender, recipient, job, route),
                False,
                f"gemini_parse_error: {type(exc).__name__}: {exc}",
            )

        if not text:
            return (
                self._template_message(sender, recipient, job, route),
                False,
                "empty_gemini_response",
            )
        return text, True, ""

    @staticmethod
    def _build_prompt(
        sender: dict[str, Any],
        recipient: dict[str, Any],
        job: dict[str, Any],
        route: str,
    ) -> str:
        route_constraints = {
            "CONNECTION_REQ": "300 characters maximum, warm but direct, single clear ask.",
            "SHORT_NEW": "360-380 characters, one specific hook from their background, one ask.",
            "FOLLOW_UP": "Under 800 characters, reference prior context, re-anchor the ask.",
            "INMAIL": "Under 1900 characters, rich context, strong hook, clear CTA.",
        }
        return (
            "You are drafting a high-signal LinkedIn outreach message.\n"
            f"Route: {route}. Constraints: {route_constraints.get(route, 'Be concise.')}\n\n"
            f"SENDER:\n  name: {sender.get('name')}\n  title: {sender.get('title')}\n"
            f"  company: {sender.get('company')}\n  background: {sender.get('background', '')}\n\n"
            f"RECIPIENT:\n  name: {recipient.get('name')}\n  title: {recipient.get('title')}\n"
            f"  company: {recipient.get('company')}\n  background: {recipient.get('background', '')}\n\n"
            f"TARGET ROLE:\n  title: {job.get('title')}\n  company: {job.get('company')}\n"
            f"  summary: {job.get('summary', '')}\n\n"
            "Rules:\n"
            "- Lead with one specific, non-generic hook tied to the recipient's actual work.\n"
            "- Tie the sender's strongest, most relevant credential to the target role.\n"
            "- End with ONE clear, low-friction ask (not 'any chance we could connect').\n"
            "- No emojis. No cliches ('hope this finds you well', 'game-changer').\n"
            "- No fabrication: use only facts given above.\n"
            "Return only the message body. No subject line, no preamble."
        )

    @staticmethod
    def _template_message(
        sender: dict[str, Any],
        recipient: dict[str, Any],
        job: dict[str, Any],
        route: str,
    ) -> str:
        r_name = (recipient.get("name") or "there").split()[0]
        s_name = sender.get("name") or "—"
        job_title = job.get("title") or "the role"
        job_co = job.get("company") or recipient.get("company") or ""
        hook = (
            f"Your founding-recruiter work scaling {job_co} 0→100+ across AI/ML and GTM"
            if "recruiter" in (recipient.get("title") or "").lower()
            else f"Your work at {job_co}"
        )
        body = (
            f"Hi {r_name}, {hook} is exactly the context I am looking for. "
            f"I am {s_name} — {sender.get('title')}, with hands-on experience building "
            f"layered agentic AI systems (routing, orchestration, guardrails, observability) "
            f"and a bias for repeatable, product-integrated delivery. "
            f"Open to a 15-minute call this week about {job_title}?"
        )
        if route == "CONNECTION_REQ":
            return body[:300]
        return body

    @staticmethod
    def _qa_validate(
        message: str,
        route: str,
        word_count: int,
    ) -> tuple[dict[str, int], str, bool]:
        critical = 0
        high = 0
        errors = 0
        warnings = 0
        notes: list[str] = []

        limits = {
            "CONNECTION_REQ": (1, 300, "chars"),
            "SHORT_NEW": (360, 400, "chars"),
            "FOLLOW_UP": (1, 800, "chars"),
            "INMAIL": (1, 1900, "chars"),
        }
        lo, hi, _unit = limits.get(route, (1, 2000, "chars"))
        char_count = len(message)
        if char_count > hi:
            critical += 1
            notes.append(f"[CRITICAL] Over char limit: {char_count} > {hi} for route {route}")
        elif char_count < lo:
            high += 1
            notes.append(f"[HIGH] Under minimum chars: {char_count} < {lo}")

        cliches = ("hope this finds you well", "game-changer", "synergy", "circle back")
        lowered = message.lower()
        for c in cliches:
            if c in lowered:
                errors += 1
                notes.append(f"[MEDIUM] Cliche detected: '{c}'")

        if word_count < 20:
            warnings += 1
            notes.append(f"[WARN] Very short: {word_count} words")
        if word_count > 200:
            warnings += 1
            notes.append(f"[WARN] Verbose: {word_count} words")

        if "?" not in message:
            warnings += 1
            notes.append("[WARN] No question/ask detected")

        production_ready = (critical == 0) and (high == 0)
        qa_summary = {
            "critical_issues": critical,
            "high_issues": high,
            "errors": errors,
            "warnings": warnings,
        }
        report = "\n".join(notes) if notes else "All QA checks passed."
        return qa_summary, report, production_ready


async def run_enterprise_lic_campaign(
    campaign_goal: str,
    audience_segment: str = "technical_buyers",
) -> EnterpriseLicResult:
    """Convenience API for enterprise LIC campaign planning."""
    orchestrator = EnterpriseLicOrchestrator()
    request = EnterpriseLicRequest(campaign_goal=campaign_goal, audience_segment=audience_segment)
    return await orchestrator.process(request)
