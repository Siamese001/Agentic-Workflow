#!/usr/bin/env python3
"""W3 — OTel Collector Probe (RTC-REQ-113).

Probes OTel collector status and trace completeness.
Per plan: Real OTel collector + trace plane.

Exit codes:
  0 — OTEL_READY (collector healthy, traces flowing)
  1 — OTEL_UNAVAILABLE (collector not reachable)
  2 — OTEL_TRACES_STUCK (collector up, but no recent traces)
  3 — OTEL_INCOMPLETE_SPANS (traces missing required spans)

W3 implementation per runtime-cert-hardened-w0-7e3c9a.md
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Configuration
OTEL_ENDPOINT = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
OTEL_TRACES_PATH = os.environ.get("OTEL_TRACES_PATH", "artifacts/otel/traces.jsonl")
REQUIRED_SPANS = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
MAX_TRACE_AGE_MINUTES = 5


def check_collector_health() -> tuple[bool, str]:
    """Check if OTel collector is healthy and reachable.
    
    Returns: (healthy, reason)
    """
    # Try HTTP health check if OTLP HTTP endpoint configured
    if OTEL_ENDPOINT.startswith("http://") or OTEL_ENDPOINT.startswith("https://"):
        try:
            import urllib.request
            health_url = f"{OTEL_ENDPOINT}/health"
            req = urllib.request.Request(health_url, method="GET", timeout=5)
            with urllib.request.urlopen(req) as resp:
                if resp.status == 200:
                    return True, "HTTP_HEALTH_OK"
        except Exception as e:
            return False, f"HEALTH_CHECK_FAILED: {e}"
    
    # For gRPC or other protocols, check if endpoint is reachable
    try:
        import socket
        parsed = OTEL_ENDPOINT.replace("http://", "").replace("https://", "")
        host = parsed.split(":")[0] if ":" in parsed else parsed
        port = int(parsed.split(":")[1]) if ":" in parsed else 4317
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return True, "PORT_REACHABLE"
        return False, f"PORT_UNREACHABLE: {host}:{port}"
    except Exception as e:
        return False, f"CONNECTION_ERROR: {e}"


def check_traces_exist() -> tuple[bool, dict[str, Any]]:
    """Check if traces exist and are recent.
    
    Returns: (ok, info)
    """
    trace_path = Path(OTEL_TRACES_PATH)
    
    if not trace_path.exists():
        return False, {"error": "TRACES_FILE_MISSING", "path": str(trace_path)}
    
    if trace_path.stat().st_size == 0:
        return False, {"error": "TRACES_FILE_EMPTY", "path": str(trace_path)}
    
    # Check file modification time
    mtime = datetime.fromtimestamp(trace_path.stat().st_mtime)
    age_minutes = (datetime.now() - mtime).total_seconds() / 60
    
    if age_minutes > MAX_TRACE_AGE_MINUTES:
        return False, {
            "error": "TRACES_STALE",
            "age_minutes": age_minutes,
            "max_age": MAX_TRACE_AGE_MINUTES,
        }
    
    return True, {"age_minutes": age_minutes, "path": str(trace_path)}


def check_trace_completeness() -> tuple[bool, dict[str, Any]]:
    """Check if traces have all required spans.
    
    Returns: (ok, info)
    """
    trace_path = Path(OTEL_TRACES_PATH)
    
    if not trace_path.exists():
        return False, {"error": "TRACES_MISSING", "missing_spans": REQUIRED_SPANS}
    
    try:
        # Read last N traces
        with open(trace_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if not lines:
            return False, {"error": "NO_TRACES", "missing_spans": REQUIRED_SPANS}
        
        # Parse and check spans
        found_spans: set[str] = set()
        
        for line in lines[-100:]:  # Check last 100 traces
            try:
                trace = json.loads(line.strip())
                # Extract span info
                if "spans" in trace:
                    for span in trace["spans"]:
                        layer = span.get("attributes", {}).get("layer")
                        if layer in REQUIRED_SPANS:
                            found_spans.add(layer)
            except json.JSONDecodeError:
                continue
        
        missing = set(REQUIRED_SPANS) - found_spans
        
        if missing:
            return False, {
                "error": "INCOMPLETE_SPANS",
                "missing_spans": list(missing),
                "found_spans": list(found_spans),
            }
        
        return True, {
            "found_spans": list(found_spans),
            "trace_count": len(lines),
        }
        
    except Exception as e:
        return False, {"error": f"PARSE_ERROR: {e}", "missing_spans": REQUIRED_SPANS}


def emit_evidence(result: dict[str, Any]) -> None:
    """Emit evidence to artifacts directory."""
    evidence_dir = Path("artifacts/certification/evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    evidence_path = evidence_dir / "otel_collector_probe.json"
    
    evidence = {
        "probe": "otel_collector",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "endpoint": OTEL_ENDPOINT,
        "result": result,
    }
    
    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)
    
    print(f"Evidence written to: {evidence_path}")


def main() -> int:
    """Main entry point."""
    # Step 1: Check collector health
    healthy, health_reason = check_collector_health()
    
    if not healthy:
        result = {
            "status": "OTEL_UNAVAILABLE",
            "reason": health_reason,
            "endpoint": OTEL_ENDPOINT,
        }
        emit_evidence(result)
        print(f"OTEL UNAVAILABLE: {health_reason}")
        return 1
    
    print(f"Collector healthy: {health_reason}")
    
    # Step 2: Check traces exist and are recent
    traces_ok, traces_info = check_traces_exist()
    
    if not traces_ok:
        result = {
            "status": "OTEL_TRACES_STUCK",
            "reason": traces_info,
            "endpoint": OTEL_ENDPOINT,
        }
        emit_evidence(result)
        print(f"OTEL TRACES STUCK: {traces_info}")
        return 2
    
    print(f"Traces recent: {traces_info}")
    
    # Step 3: Check trace completeness
    complete, completeness_info = check_trace_completeness()
    
    if not complete:
        result = {
            "status": "OTEL_INCOMPLETE_SPANS",
            "reason": completeness_info,
            "endpoint": OTEL_ENDPOINT,
        }
        emit_evidence(result)
        print(f"OTEL INCOMPLETE SPANS: {completeness_info}")
        return 3
    
    # All checks passed
    result = {
        "status": "OTEL_READY",
        "endpoint": OTEL_ENDPOINT,
        "health_reason": health_reason,
        "traces": traces_info,
        "completeness": completeness_info,
    }
    emit_evidence(result)
    
    print("OTEL READY")
    print(f"  Endpoint: {OTEL_ENDPOINT}")
    print(f"  Traces: {completeness_info.get('trace_count', 'N/A')} spans")
    print(f"  Layers: {completeness_info.get('found_spans', [])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
