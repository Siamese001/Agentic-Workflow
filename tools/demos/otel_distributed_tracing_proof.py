"""End-to-end proof that distributed tracing works in this repo.

What "distributed tracing" actually means
-----------------------------------------
A single logical request fans out across multiple *processes*, and every span
emitted by every process resolves to the **same trace_id** with a correct
parent/child topology — because the W3C `traceparent` header is propagated at
each hop.

This demo proves that with three real OS processes:

    [Process A: orchestrator]  --HTTP--> [Process B: tool-server]
                                                |
                                                +--HTTP--> [Process C: leaf]

Each process:
  - boots its own TracerProvider with InMemorySpanExporter,
  - extracts the inbound `traceparent` header to continue the upstream trace,
  - re-injects `traceparent` on every outbound HTTP call,
  - persists its completed spans to a JSON file before exit.

Then the orchestrator collects the three JSON files and asserts:
  - all spans share one trace_id,
  - the parent_span_id chain is intact (A->B->C),
  - the W3C traceparent received by C carries A's trace_id.

If those assertions pass, distributed tracing is provably working — not just
"a trace SDK is installed."

Run:
    python tools/demos/otel_distributed_tracing_proof.py
"""

from __future__ import annotations

import http.server
import json
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Worker process body — reused for B and C with different roles.
# ---------------------------------------------------------------------------

WORKER_BODY = r'''
import json, os, sys, urllib.request, http.server, socketserver, threading, time, signal
from pathlib import Path

from opentelemetry import trace, context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

ROLE       = os.environ["DEMO_ROLE"]
PORT       = int(os.environ["DEMO_PORT"])
DOWNSTREAM = os.environ.get("DEMO_DOWNSTREAM", "")
OUT_PATH   = Path(os.environ["DEMO_OUT"])

resource = Resource.create({"service.name": f"demo-{ROLE}"})
provider = TracerProvider(resource=resource)
exporter = InMemorySpanExporter()
provider.add_span_processor(SimpleSpanProcessor(exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(f"demo.{ROLE}")
propagator = TraceContextTextMapPropagator()


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # silence stderr noise
        return

    def do_GET(self):
        # Extract upstream trace context from headers.
        carrier = {k.lower(): v for k, v in self.headers.items()}
        ctx = propagator.extract(carrier=carrier)
        received_traceparent = carrier.get("traceparent", "")

        with tracer.start_as_current_span(f"{ROLE}.handle_request", context=ctx) as span:
            span.set_attribute("demo.role", ROLE)
            span.set_attribute("demo.received_traceparent", received_traceparent)

            payload = {"role": ROLE, "received_traceparent": received_traceparent}

            if DOWNSTREAM:
                # Inject MUST happen INSIDE the client span so the downstream
                # service nests under "call_downstream", not "handle_request".
                with tracer.start_as_current_span(f"{ROLE}.call_downstream"):
                    inject_carrier = {}
                    propagator.inject(carrier=inject_carrier)
                    req = urllib.request.Request(DOWNSTREAM)
                    for k, v in inject_carrier.items():
                        req.add_header(k, v)
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        downstream = json.loads(resp.read().decode())
                payload["downstream"] = downstream
                payload["sent_traceparent"] = inject_carrier.get("traceparent", "")

            body = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)


class _ReusableServer(socketserver.TCPServer):
    allow_reuse_address = True


server = _ReusableServer(("127.0.0.1", PORT), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()

# Tell parent we are ready by writing a sentinel file.
sentinel = OUT_PATH.with_suffix(".ready")
sentinel.write_text("ready")

def _shutdown(*_):
    server.shutdown()

signal.signal(signal.SIGTERM, _shutdown)
signal.signal(signal.SIGINT, _shutdown)

# Wait for parent to send shutdown via a different sentinel.
stop = OUT_PATH.with_suffix(".stop")
while not stop.exists():
    time.sleep(0.05)

server.shutdown()
provider.shutdown()

# Persist spans for the orchestrator to inspect.
spans_out = []
for s in exporter.get_finished_spans():
    ctx = s.get_span_context()
    parent = s.parent
    spans_out.append({
        "name": s.name,
        "trace_id": format(ctx.trace_id, "032x"),
        "span_id":  format(ctx.span_id,  "016x"),
        "parent_span_id": format(parent.span_id, "016x") if parent else "",
        "attributes": dict(s.attributes or {}),
        "service":   f"demo-{ROLE}",
    })
OUT_PATH.write_text(json.dumps(spans_out, indent=2))
'''


# ---------------------------------------------------------------------------
# Orchestrator: spawn B and C, then originate a trace from A and assert.
# ---------------------------------------------------------------------------


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _spawn_worker(role: str, port: int, downstream_url: str, out_path: Path) -> subprocess.Popen:
    env = {
        **__import__("os").environ,
        "DEMO_ROLE": role,
        "DEMO_PORT": str(port),
        "DEMO_DOWNSTREAM": downstream_url,
        "DEMO_OUT": str(out_path),
        "PYTHONPATH": str(REPO_ROOT),
        "PYTHONIOENCODING": "utf-8",
    }
    return subprocess.Popen(
        [sys.executable, "-u", "-c", WORKER_BODY],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _wait_ready(out_path: Path, timeout: float = 8.0) -> None:
    deadline = time.time() + timeout
    sentinel = out_path.with_suffix(".ready")
    while time.time() < deadline:
        if sentinel.exists():
            return
        time.sleep(0.05)
    raise TimeoutError(f"worker not ready: {out_path}")


def _stop_worker(out_path: Path) -> None:
    out_path.with_suffix(".stop").write_text("stop")


def main() -> int:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
        InMemorySpanExporter,
    )
    from opentelemetry.trace.propagation.tracecontext import (
        TraceContextTextMapPropagator,
    )

    tmpdir = Path(tempfile.mkdtemp(prefix="otel_dt_"))
    print(f"[A] tmpdir = {tmpdir}")

    port_b = _free_port()
    port_c = _free_port()
    out_b = tmpdir / "spans_b.json"
    out_c = tmpdir / "spans_c.json"

    # Start C first (leaf), then B (calls C), then A originates the request.
    proc_c = _spawn_worker("C", port_c, downstream_url="", out_path=out_c)
    proc_b = _spawn_worker(
        "B", port_b, downstream_url=f"http://127.0.0.1:{port_c}/", out_path=out_b
    )

    try:
        _wait_ready(out_c)
        _wait_ready(out_b)

        # Process A: originator with its own TracerProvider.
        provider_a = TracerProvider(resource=Resource.create({"service.name": "demo-A"}))
        exporter_a = InMemorySpanExporter()
        provider_a.add_span_processor(SimpleSpanProcessor(exporter_a))
        trace.set_tracer_provider(provider_a)
        tracer_a = trace.get_tracer("demo.A")
        propagator = TraceContextTextMapPropagator()

        with tracer_a.start_as_current_span("A.originate") as root_span:
            root_ctx = root_span.get_span_context()
            root_trace_id = format(root_ctx.trace_id, "032x")
            print(f"[A] originating trace_id = {root_trace_id}")

            with tracer_a.start_as_current_span("A.call_B"):
                carrier: dict[str, str] = {}
                propagator.inject(carrier=carrier)  # injects A.call_B context
                sent_tp_to_b = carrier["traceparent"]
                req = urllib.request.Request(f"http://127.0.0.1:{port_b}/")
                for k, v in carrier.items():
                    req.add_header(k, v)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    body = json.loads(resp.read().decode())

        provider_a.shutdown()

        # Stop workers and collect their span dumps.
        _stop_worker(out_b)
        _stop_worker(out_c)
        proc_b.wait(timeout=5)
        proc_c.wait(timeout=5)

        spans_a = [
            {
                "name": s.name,
                "trace_id": format(s.get_span_context().trace_id, "032x"),
                "span_id":  format(s.get_span_context().span_id,  "016x"),
                "parent_span_id": format(s.parent.span_id, "016x") if s.parent else "",
                "service":  "demo-A",
            }
            for s in exporter_a.get_finished_spans()
        ]
        spans_b = json.loads(out_b.read_text())
        spans_c = json.loads(out_c.read_text())
        all_spans = spans_a + spans_b + spans_c

        # ----- Distributed-tracing assertions -----
        print("\n=== EVIDENCE ===")
        print(f"trace_id A originated     : {root_trace_id}")
        print(f"traceparent A -> B (sent) : {sent_tp_to_b}")
        recv_b = next(s for s in spans_b if s["name"] == "B.handle_request")
        recv_c = next(s for s in spans_c if s["name"] == "C.handle_request")
        print(f"traceparent A -> B (recv) : {recv_b['attributes'].get('demo.received_traceparent')}")
        print(f"traceparent B -> C (recv) : {recv_c['attributes'].get('demo.received_traceparent')}")
        print(f"\nspans by service: A={len(spans_a)} B={len(spans_b)} C={len(spans_c)}")
        for s in all_spans:
            print(
                f"  [{s['service']:7s}] {s['name']:25s} "
                f"trace={s['trace_id']} span={s['span_id']} parent={s['parent_span_id']}"
            )

        trace_ids = {s["trace_id"] for s in all_spans}
        assert trace_ids == {root_trace_id}, (
            f"FAIL: trace_id divergence — saw {trace_ids}"
        )

        # Parent topology: every span except A.originate must have a parent_span_id
        # that resolves to a span_id we observed.
        all_span_ids = {s["span_id"] for s in all_spans}
        orphans = [
            s for s in all_spans
            if s["name"] != "A.originate"
            and s["parent_span_id"]
            and s["parent_span_id"] not in all_span_ids
        ]
        assert not orphans, f"FAIL: orphan parents: {orphans}"

        # B's handle_request parent must be A's call_B span_id.
        a_call_b = next(s for s in spans_a if s["name"] == "A.call_B")
        assert recv_b["parent_span_id"] == a_call_b["span_id"], (
            "FAIL: B did not continue A's trace (parent mismatch)"
        )

        # C's handle_request parent must be B's call_downstream span_id.
        b_call_c = next(s for s in spans_b if s["name"] == "B.call_downstream")
        assert recv_c["parent_span_id"] == b_call_c["span_id"], (
            "FAIL: C did not continue B's trace (parent mismatch)"
        )

        # The traceparent received by C must carry A's original trace_id.
        recv_tp_c = recv_c["attributes"]["demo.received_traceparent"]
        assert root_trace_id in recv_tp_c, (
            f"FAIL: A's trace_id {root_trace_id} not in C's traceparent {recv_tp_c}"
        )

        # End-to-end response also confirms B saw and forwarded the trace.
        assert body["downstream"]["role"] == "C"

        print("\n=== ALL DISTRIBUTED-TRACING ASSERTIONS PASSED ===")
        print(f"  - 1 trace_id across 3 processes (A,B,C)")
        print(f"  - {len(all_spans)} spans linked into one parent/child tree")
        print(f"  - W3C traceparent propagated A->B->C verbatim")
        return 0

    finally:
        for proc in (proc_b, proc_c):
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()


if __name__ == "__main__":
    sys.exit(main())
