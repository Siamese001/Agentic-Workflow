"""L0/L3 OTEL span stubs for apps_rg bindings (plan l0-l3 W4)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from agentic_core.runtime.contracts.route_contract import RouteContract


def _digest(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def emit_l0_route_span(route: RouteContract) -> dict[str, Any] | None:
    """Deterministic l0.route_decision span ref (fail-soft)."""
    try:
        ts = datetime.now(timezone.utc).isoformat()
        payload = {
            "span_kind": "l0.route_decision",
            "layer": "L0",
            "app_id": route.app_id or "apps_rg",
            "trace_id": route.trace_id,
            "run_id": route.run_id,
            "route_id": route.route_id,
            "execution_form": route.execution_form,
            "route_digest": route.route_digest or "",
            "timestamp": ts,
        }
        d = _digest(payload)
        return {
            "span_ref": f"span:l0:route_decision:{route.trace_id}:{route.run_id}:{d[:16]}",
            "payload": payload,
            "payload_digest": d,
        }
    except Exception:  # guardian: allow-return-none-swallow -- observability only
        return None


def emit_l3_orchestration_span(
    *,
    route: RouteContract,
    workflow_id: str,
    dag_id: str,
) -> dict[str, Any] | None:
    """Deterministic l3.orchestration span ref (fail-soft)."""
    try:
        ts = datetime.now(timezone.utc).isoformat()
        payload = {
            "span_kind": "l3.orchestration",
            "layer": "L3",
            "app_id": route.app_id or "apps_rg",
            "trace_id": route.trace_id,
            "run_id": route.run_id,
            "workflow_id": workflow_id,
            "dag_id": dag_id,
            "route_id": route.route_id,
            "timestamp": ts,
        }
        d = _digest(payload)
        return {
            "span_ref": f"span:l3:orchestration:{route.trace_id}:{route.run_id}:{d[:16]}",
            "payload": payload,
            "payload_digest": d,
        }
    except Exception:  # guardian: allow-return-none-swallow -- observability only
        return None


__all__ = ["emit_l0_route_span", "emit_l3_orchestration_span"]
