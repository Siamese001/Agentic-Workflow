"""Fail-fast CLI preflight for ``python -m apps_rg --section <lane>`` (apps_rg only)."""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any

from agentic_core.L0_routing.config.model_registry import VLLM_BASE_URL

from apps_rg.runtime.providers.competencies_live_provider_gate import competencies_vllm_preflight_timeout_s
from apps_rg.runtime.qwen_transport_diag import run_http_models_preflight

_ENV_SKIP_QWEN_HEALTH = "APPS_RG_SKIP_QWEN_VLLM_HEALTH"
_ENV_VLLM_AUTO_START = "APPS_RG_VLLM_AUTO_START"
_DEFAULT_CONTAINER = "local-qwen-vllm"


def _truthy_env(name: str) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return False
    return str(raw).strip().lower() in {"1", "true", "yes", "y", "on"}


def should_skip_qwen_vllm_health_gate() -> bool:
    """True when live vLLM health is not required for section-only CLI runs.

    Offline Qwen stub and skip-health are forbidden (see ``qwen_live_only_guard``).
    """
    return _truthy_env(_ENV_SKIP_QWEN_HEALTH)


def _qwen_container_name() -> str:
    name = str(os.environ.get("APPS_RG_QWEN_VLLM_CONTAINER_NAME", _DEFAULT_CONTAINER) or "").strip()
    return name or _DEFAULT_CONTAINER


def _try_start_qwen_container(container: str) -> tuple[bool, str]:
    """Opt-in ``docker start`` when preflight finds the container stopped."""
    if not shutil.which("docker"):
        return False, "docker CLI not on PATH"
    try:
        proc = subprocess.run(  # guardian: allow-chokepoint-bypass -- local vLLM preflight docker start; operator-initiated CLI only
            ["docker", "start", container],
            capture_output=True,
            text=True,
            timeout=60.0,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return False, f"docker start timed out for container {container!r}"
    except OSError as exc:
        return False, f"{type(exc).__name__}: {exc}"
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        return False, detail or f"docker start failed for container {container!r}"
    return True, ""


def _docker_container_running(container: str) -> tuple[bool, str]:
    if not shutil.which("docker"):
        return False, "docker CLI not on PATH; cannot verify local Qwen vLLM container"
    try:
        proc = subprocess.run(  # guardian: allow-chokepoint-bypass -- local vLLM preflight docker inspect; read-only container state check
            ["docker", "inspect", "-f", "{{.State.Running}}", container],
            capture_output=True,
            text=True,
            timeout=10.0,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return False, f"docker inspect timed out for container {container!r}"
    except OSError as exc:
        return False, f"{type(exc).__name__}: {exc}"
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        return False, detail or f"docker inspect failed for container {container!r}"
    if proc.stdout.strip().lower() != "true":
        return False, f"docker container {container!r} is not running"
    return True, ""


def _effective_vllm_base_url() -> str:
    raw = str(os.environ.get("VLLM_BASE_URL") or VLLM_BASE_URL or "").strip()
    return raw or "http://localhost:8000/v1"


def _http_models_health_check() -> tuple[bool, str]:
    base_url = _effective_vllm_base_url()
    timeout_s = float(competencies_vllm_preflight_timeout_s())
    ok, snap, code = run_http_models_preflight(base_url=base_url, timeout_s=timeout_s)
    if ok:
        return True, ""
    err = ""
    if isinstance(snap, dict):
        err = str(snap.get("error") or "").strip()
    detail = err or str(code or "http_v1_models_probe_failure")
    return False, f"{detail} (base_url={base_url!r})"


def require_qwen_vllm_cli_health(
    *,
    lane_provider: str,
    docker_restart_audit: dict[str, Any] | None = None,
) -> None:
    """Fail closed when section lane uses live ``qwen_vllm`` but Docker/HTTP health is not ready."""
    from apps_rg.runtime.section_cli_defaults import SectionCliConfigError

    if should_skip_qwen_vllm_health_gate():
        return
    if str(lane_provider).strip().lower() != "qwen_vllm":
        return

    audit = dict(docker_restart_audit or {})

    if audit.get("performed") and not audit.get("ready"):
        raise SectionCliConfigError(
            "qwen vLLM docker restart completed but readiness probe failed: "
            f"{audit.get('probe_error') or audit.get('decisive_reason') or 'unhealthy'}"
        )

    if audit.get("restart_requested") and audit.get("reason") == "model_readiness_failed":
        raise SectionCliConfigError(
            "qwen vLLM model readiness failed before run: "
            f"{audit.get('decisive_reason') or audit.get('readiness_status') or 'unhealthy'}"
        )

    container = _qwen_container_name()
    ok_docker, docker_err = _docker_container_running(container)
    if not ok_docker and _truthy_env(_ENV_VLLM_AUTO_START):
        started, start_err = _try_start_qwen_container(container)
        if started:
            ok_docker, docker_err = _docker_container_running(container)
        else:
            docker_err = f"{docker_err}; auto_start_failed: {start_err}".strip("; ")
    if not ok_docker:
        raise SectionCliConfigError(
            f"qwen vLLM docker container health check failed ({container!r}): {docker_err}"
        )

    ok_http, http_err = _http_models_health_check()
    if not ok_http:
        raise SectionCliConfigError(f"qwen vLLM HTTP /v1/models health check failed: {http_err}")


__all__ = [
    "require_qwen_vllm_cli_health",
    "should_skip_qwen_vllm_health_gate",
    "_try_start_qwen_container",
]
