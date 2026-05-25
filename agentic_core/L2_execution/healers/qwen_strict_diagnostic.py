"""Strict-mode Qwen-vLLM diagnostic with Docker Desktop attribution.

Used by callers that want to fail LOUD (not silently fall through to stub or
cloud) when the local Qwen vLLM stack is unavailable. Distinguishes three
root causes so the operator (or Cascade) gets an actionable error:

1. Docker Desktop / docker daemon not running
2. Docker daemon up but vLLM container not responding
3. vLLM container up but no Qwen model loaded

Env switches:
    APPS_RESEARCH_REQUIRE_QWEN=1
        Engines that synthesize via Qwen (e.g. CompanyBriefEngine) MUST
        raise QwenUnavailableError instead of falling through.
    QWEN_STRICT_DOCKER_TIMEOUT_SECONDS (default 3.0)
        Bound on the `docker info` subprocess.

Plan ref: post-2026-05-05 hardening — never silently degrade Qwen synthesis
when the operator expects local-grounded LLM output.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Literal

from agentic_core.L2_execution.healers.vllm_health_probe import probe

_log = logging.getLogger(__name__)

_DEFAULT_DOCKER_TIMEOUT = float(os.getenv("QWEN_STRICT_DOCKER_TIMEOUT_SECONDS", "3.0"))

DiagStatus = Literal[
    "ok",
    "docker_desktop_down",
    "docker_cli_missing",
    "vllm_container_down",
    "qwen_model_not_loaded",
    "unknown",
]


@dataclass(frozen=True)
class QwenDiagnostic:
    """Result of a strict Qwen-availability check.

    Attributes:
        status: Categorical root cause.
        message: One-line human-readable summary.
        action_hint: Concrete action the operator should take.
        docker_cli_present: True iff `docker` is on PATH.
        docker_daemon_responsive: True iff `docker info` returned 0 within timeout.
        vllm_responsive: True iff /v1/models returned 200.
        qwen_model_loaded: True iff /v1/models reports a Qwen-* model id.
    """

    status: DiagStatus
    message: str
    action_hint: str
    docker_cli_present: bool
    docker_daemon_responsive: bool
    vllm_responsive: bool
    qwen_model_loaded: bool

    @property
    def ok(self) -> bool:
        return self.status == "ok"


class QwenUnavailableError(RuntimeError):
    """Raised in strict mode when Qwen vLLM cannot be reached.

    Carries the :class:`QwenDiagnostic` so callers (Cascade, CLIs) can
    surface a precise action hint to the operator.
    """

    def __init__(self, diagnostic: QwenDiagnostic) -> None:
        full = (
            f"{diagnostic.message}\n"
            f"  status      = {diagnostic.status}\n"
            f"  action_hint = {diagnostic.action_hint}"
        )
        super().__init__(full)
        self.diagnostic = diagnostic


def _docker_cli_present() -> bool:
    """True iff `docker` is on PATH."""
    return shutil.which("docker") is not None


def _docker_daemon_responsive(timeout: float) -> bool:
    """True iff `docker info` returns 0 within the timeout.

    Subprocess is bounded; never raises. This is the canonical "is Docker
    Desktop running" check on Windows / macOS / Linux.
    """
    try:
        proc = subprocess.run(  # guardian: allow-chokepoint-bypass -- bounded docker daemon health probe; not LLM/tool egress
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        _log.debug("docker info failed: %s", exc)
        return False
    return proc.returncode == 0 and bool(proc.stdout.strip())


def diagnose() -> QwenDiagnostic:
    """Run the full Qwen-availability cascade and return a categorized result.

    Order: Docker CLI → Docker daemon → vLLM HTTP → Qwen model id. The
    first failure wins so the action hint targets the actual root cause.
    """
    cli_present = _docker_cli_present()
    if not cli_present:
        return QwenDiagnostic(
            status="docker_cli_missing",
            message="docker CLI not found on PATH",
            action_hint=(
                "Install Docker Desktop and ensure `docker` is on your PATH. "
                "Then start Docker Desktop and the vLLM container."
            ),
            docker_cli_present=False,
            docker_daemon_responsive=False,
            vllm_responsive=False,
            qwen_model_loaded=False,
        )

    daemon_up = _docker_daemon_responsive(_DEFAULT_DOCKER_TIMEOUT)
    if not daemon_up:
        return QwenDiagnostic(
            status="docker_desktop_down",
            message="Docker Desktop / docker daemon is not running",
            action_hint=(
                "Start Docker Desktop, wait until the whale icon is steady, "
                "then re-run. (On Windows: Start menu → Docker Desktop.)"
            ),
            docker_cli_present=True,
            docker_daemon_responsive=False,
            vllm_responsive=False,
            qwen_model_loaded=False,
        )

    health = probe(force_refresh=True)
    if not health.is_healthy:
        return QwenDiagnostic(
            status="vllm_container_down",
            message=(
                f"Docker is up but vLLM is not responding: {health.error or 'no response'}"
            ),
            action_hint=(
                "Docker Desktop is running but the vLLM container is not. "
                "Start it: `docker compose up -d vllm` (or your equivalent), "
                "wait ~30s for the model to load, then re-run."
            ),
            docker_cli_present=True,
            docker_daemon_responsive=True,
            vllm_responsive=False,
            qwen_model_loaded=False,
        )

    if "Qwen" not in (health.model_id or ""):
        return QwenDiagnostic(
            status="qwen_model_not_loaded",
            message=(
                f"vLLM is responding but no Qwen model loaded "
                f"(reported model_id={health.model_id!r})"
            ),
            action_hint=(
                "vLLM is up but is not serving a Qwen-* model. Reload the "
                "container with the correct --model arg pointing at a Qwen "
                "checkpoint, or update your compose file."
            ),
            docker_cli_present=True,
            docker_daemon_responsive=True,
            vllm_responsive=True,
            qwen_model_loaded=False,
        )

    return QwenDiagnostic(
        status="ok",
        message=f"Qwen vLLM healthy (model_id={health.model_id})",
        action_hint="",
        docker_cli_present=True,
        docker_daemon_responsive=True,
        vllm_responsive=True,
        qwen_model_loaded=True,
    )


def require_qwen_or_raise() -> None:
    """Run :func:`diagnose` and raise :class:`QwenUnavailableError` if not ok."""
    d = diagnose()
    if not d.ok:
        raise QwenUnavailableError(d)


def strict_mode_enabled() -> bool:
    """True iff APPS_RESEARCH_REQUIRE_QWEN is set to a truthy value."""
    return os.environ.get("APPS_RESEARCH_REQUIRE_QWEN", "").strip() in {
        "1",
        "true",
        "yes",
        "on",
    }


__all__ = [
    "DiagStatus",
    "QwenDiagnostic",
    "QwenUnavailableError",
    "diagnose",
    "require_qwen_or_raise",
    "strict_mode_enabled",
]
