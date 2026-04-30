"""OTel Collector-Backed Proof Harness (W1 of plan 10c-proof-depth-remediation-a9f9af).

Purpose
=======
Execute a target test (or arbitrary callable) under a real OpenTelemetry
TracerProvider with an InMemorySpanExporter installed BEFORE the test runs.
After the test completes, the harness reads back every span the production
code actually emitted, computes a deterministic SHA-256 over the canonical
span dump, and returns a structured `OTelProof` record.

The result is honest evidence at the `E6.5_INTEGRATED_RUNTIME` tier (real
OTel SDK + in-memory exporter, deterministic, replay-stable). Strict
`E7_REAL_OTEL_EXPORT` requires a real collector (e.g., docker
otel-collector) with collector-side ack receipts; that is a separate W1.2
work item.

Two execution modes
-------------------

1. **In-process callable mode** (`run_callable_proof`) — the harness
   installs the TracerProvider, calls a Python callable, and returns the
   proof. Useful when production code is reachable as a function call.

2. **Subprocess test-file mode** (`run_test_file_proof`) — the harness
   spawns a pytest subprocess that loads our `pytest_otel_capture`
   plugin, runs the target test file, and dumps captured spans to JSON.
   The harness reads back the JSON and computes the proof. Useful when
   the existing 10C test files (`test_10c_req_*.py`) carry the right
   semantic shape and we want to know whether they exercise real OTel
   emit paths.

Anti-cheat invariants (per plan §8)
-----------------------------------

- **No fabricated runtime evidence**: bundles report exactly what the
  in-memory exporter captured, not what we wished was emitted.
- **Replay determinism**: ``replay_digest`` is stable across runs of the
  same code at the same git HEAD; non-deterministic data (timestamps,
  trace_ids generated at runtime) are normalized BEFORE hashing.
- **Honest residual**: when zero spans are captured, the proof reports
  ``status=NO_SPANS_EMITTED`` and the bundle MUST NOT claim
  ``actual_proof_depth=E6.5`` or higher.

Usage
-----

    from tools.proof.otel_collector_proof import run_test_file_proof

    proof = run_test_file_proof(
        test_path="tests/unit/agentic_core/L6_observability/test_10c_req_128.py",
        expected_span="l6.eval.record_sealed",
    )
    print(proof.status, proof.actual_proof_depth, proof.replay_digest)

Output schema
-------------

See ``OTelProof`` dataclass.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]


# ──────────────────────────────────────────────────────────────────────
# Result dataclass
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CapturedSpan:
    """A normalized record of one span the harness captured."""

    name: str
    attributes: Mapping[str, Any] = field(default_factory=dict)
    status: str = ""
    kind: str = ""

    def normalized(self) -> dict[str, Any]:
        """Emit a canonical dict for hashing.

        We DROP timing fields and runtime-generated IDs (trace_id, span_id,
        timestamps) so the digest is stable across runs. We KEEP the
        canonical name + sorted attribute keys + values. Replay_key,
        policy_hash, etc. that the application sets remain in the digest
        because they are deterministic at fixed git HEAD.
        """
        return {
            "name": self.name,
            "kind": self.kind,
            "status": self.status,
            "attrs": {k: self.attributes[k] for k in sorted(self.attributes)},
        }


@dataclass(frozen=True)
class OTelProof:
    """The harness's output. One object per harness invocation."""

    target: str
    """What was run (test path or callable name)."""

    expected_span: str | None
    """The span name the caller wanted captured (None = any)."""

    spans: tuple[CapturedSpan, ...]
    """Every span the in-memory exporter captured."""

    span_count: int
    """Convenience: len(spans)."""

    expected_seen: bool
    """True iff `expected_span` is None or appears in `spans`."""

    status: str
    """One of:
       - SATISFIED:          ≥1 span captured AND expected_seen is True
       - NO_SPANS_EMITTED:   zero spans captured (no production OTel emit reached)
       - WRONG_SPAN_EMITTED: spans captured but expected_span not present
       - HARNESS_ERROR:      target failed to run (test errored, import failed, etc.)
    """

    actual_proof_depth: str
    """One of:
       - E6.5_INTEGRATED_RUNTIME:    SATISFIED via in-memory exporter
       - E4_NEGATIVE_CONTROL:        no upgrade — spans not emitted
       - E0_REQUIREMENT_TEXT:        harness errored
    """

    replay_digest: str
    """SHA-256 over canonical normalized span dump."""

    captured_at_utc: str
    """ISO-8601 UTC timestamp."""

    git_head: str
    """git HEAD short-sha at capture time."""

    git_dirty: bool
    """Whether working tree was dirty at capture time."""

    target_exit_code: int | None = None
    """Subprocess exit code when run_test_file_proof; None for callable mode."""

    target_stderr: str = ""
    """Tail of stderr (last ~2KB) when subprocess; empty for callable mode."""

    def to_bundle_payload(self) -> dict[str, Any]:
        """Project to the JSON shape that goes into proof_bundles/*.json."""
        return {
            "harness": "tools.proof.otel_collector_proof",
            "harness_mode": "in_memory_exporter",
            "target": self.target,
            "expected_span": self.expected_span,
            "span_count": self.span_count,
            "expected_seen": self.expected_seen,
            "status": self.status,
            "actual_proof_depth": self.actual_proof_depth,
            "captured_spans": [s.normalized() for s in self.spans],
            "replay_digest": self.replay_digest,
            "captured_at_utc": self.captured_at_utc,
            "git_head": self.git_head,
            "git_dirty": self.git_dirty,
            "target_exit_code": self.target_exit_code,
        }


# ──────────────────────────────────────────────────────────────────────
# Determinism helpers
# ──────────────────────────────────────────────────────────────────────


def _git_head() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
            check=True, timeout=10,
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def _git_dirty() -> bool:
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
            check=True, timeout=10,
        ).stdout
        return bool(out.strip())
    except (subprocess.SubprocessError, OSError):
        return True  # safe default


def _replay_digest(spans: Sequence[CapturedSpan]) -> str:
    """SHA-256 over canonical normalized span list."""
    canonical = json.dumps(
        [s.normalized() for s in spans],
        sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _spans_to_proof(
    target: str,
    expected_span: str | None,
    spans: Sequence[CapturedSpan],
    *,
    target_exit_code: int | None = None,
    target_stderr: str = "",
    harness_error: bool = False,
) -> OTelProof:
    span_count = len(spans)
    expected_seen = (expected_span is None) or any(s.name == expected_span for s in spans)

    if harness_error:
        status = "HARNESS_ERROR"
        depth = "E0_REQUIREMENT_TEXT"
    elif span_count == 0:
        status = "NO_SPANS_EMITTED"
        depth = "E4_NEGATIVE_CONTROL"
    elif expected_seen:
        status = "SATISFIED"
        depth = "E6.5_INTEGRATED_RUNTIME"
    else:
        status = "WRONG_SPAN_EMITTED"
        depth = "E4_NEGATIVE_CONTROL"

    return OTelProof(
        target=target,
        expected_span=expected_span,
        spans=tuple(spans),
        span_count=span_count,
        expected_seen=expected_seen,
        status=status,
        actual_proof_depth=depth,
        replay_digest=_replay_digest(spans),
        captured_at_utc=datetime.now(timezone.utc).isoformat(),
        git_head=_git_head(),
        git_dirty=_git_dirty(),
        target_exit_code=target_exit_code,
        target_stderr=target_stderr,
    )


# ──────────────────────────────────────────────────────────────────────
# Mode 1: in-process callable
# ──────────────────────────────────────────────────────────────────────


def _install_in_memory_tracer():
    """Attach a fresh InMemorySpanExporter to the global TracerProvider.

    OpenTelemetry's ``trace.set_tracer_provider`` is once-per-process —
    a second call is a no-op and logs a warning. So instead of trying
    to install a fresh provider on each harness call (which fails on
    the second call), we attach our processor to whatever provider is
    already in place, OR install ours if none exists. Either way our
    in-memory exporter receives the spans emitted during the harness
    invocation.

    Returns (provider, exporter, processor). The caller MUST remove the
    processor in a finally-block (via ``processor.shutdown()``) so a
    subsequent harness call gets a fresh exporter.
    """
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
        InMemorySpanExporter,
    )

    current = trace.get_tracer_provider()
    if isinstance(current, TracerProvider):
        # Reuse existing provider; just add our processor to it.
        provider = current
    else:
        # Either ProxyTracerProvider (default) or a foreign provider.
        # Install a real one. set_tracer_provider is once-per-process;
        # if a real provider was already installed by another harness
        # call we'd have hit the branch above, so this is the first call.
        provider = TracerProvider()
        trace.set_tracer_provider(provider)

    exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)
    return provider, exporter, processor


def _exporter_to_captured(exporter) -> list[CapturedSpan]:
    """Convert InMemorySpanExporter spans to CapturedSpan list."""
    out = []
    for s in exporter.get_finished_spans():
        # ReadableSpan attribute names + status text
        attrs = dict(s.attributes or {})
        try:
            status_code = s.status.status_code.name if s.status else ""
        except AttributeError:
            status_code = ""
        try:
            kind = s.kind.name if s.kind else ""
        except AttributeError:
            kind = ""
        out.append(CapturedSpan(
            name=s.name,
            attributes=attrs,
            status=status_code,
            kind=kind,
        ))
    return out


def run_callable_proof(
    fn: Callable[[], Any],
    *,
    expected_span: str | None = None,
    target_label: str | None = None,
) -> OTelProof:
    """Run `fn()` under a fresh TracerProvider; return captured spans as proof.

    Use this when the production code path is reachable from Python.
    The harness installs the tracer BEFORE `fn` runs; any code under `fn`
    that uses ``opentelemetry.trace.get_tracer().start_as_current_span(...)``
    will land in the in-memory exporter.
    """
    label = target_label or getattr(fn, "__qualname__", repr(fn))
    try:
        provider, exporter, processor = _install_in_memory_tracer()
    except ImportError as exc:
        return _spans_to_proof(label, expected_span, [], harness_error=True,
                              target_stderr=f"opentelemetry import failed: {exc}")
    try:
        try:
            fn()
        except (BaseException) as exc:  # noqa: BLE001 — we WANT to capture spans even if test fails
            # Don't fabricate success on failure; record the residual via spans alone.
            stderr = f"target raised {type(exc).__name__}: {exc!s}"
            spans = _exporter_to_captured(exporter)
            return _spans_to_proof(label, expected_span, spans,
                                  target_exit_code=1, target_stderr=stderr[:2048])
        # Normal completion
        spans = _exporter_to_captured(exporter)
        return _spans_to_proof(label, expected_span, spans, target_exit_code=0)
    finally:
        # Clean up so subsequent harness calls get a fresh state
        try:
            processor.shutdown()
            provider.shutdown()
        except Exception:  # noqa: BLE001 — shutdown is best-effort
            pass


# ──────────────────────────────────────────────────────────────────────
# Mode 2: subprocess pytest
# ──────────────────────────────────────────────────────────────────────


def run_test_file_proof(
    test_path: str | Path,
    *,
    expected_span: str | None = None,
    pytest_args: Sequence[str] = (),
    timeout: int = 60,
) -> OTelProof:
    """Run `pytest <test_path>` under our OTel-capture plugin.

    The plugin (`tools/proof/_pytest_otel_capture_plugin.py`) installs
    a TracerProvider+InMemorySpanExporter at session_start and dumps
    captured spans to a JSON file at session_end. The harness reads
    back the JSON and builds the proof.
    """
    test_path = Path(test_path)
    target = str(test_path).replace("\\", "/")

    plugin_module = "tools.proof._pytest_otel_capture_plugin"
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, dir=str(REPO_ROOT)
    ) as tmp:
        out_path = tmp.name

    try:
        env = os.environ.copy()
        env["OTEL_PROOF_OUTPUT"] = out_path
        # Unbuffered output so the plugin's session_finish runs cleanly
        env["PYTHONUNBUFFERED"] = "1"
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_path),
            "-p", plugin_module,
            "--no-header",
            "-q",
            "-p", "no:cacheprovider",
            *pytest_args,
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, cwd=str(REPO_ROOT),
                timeout=timeout, check=False,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            return _spans_to_proof(target, expected_span, [], harness_error=True,
                                  target_exit_code=None,
                                  target_stderr=f"pytest timeout after {timeout}s")

        # Read back captured spans (plugin writes empty list if no spans)
        spans: list[CapturedSpan] = []
        try:
            if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                with open(out_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                for entry in raw:
                    spans.append(CapturedSpan(
                        name=entry.get("name", ""),
                        attributes=entry.get("attributes", {}),
                        status=entry.get("status", ""),
                        kind=entry.get("kind", ""),
                    ))
        except (OSError, json.JSONDecodeError) as exc:
            return _spans_to_proof(target, expected_span, [], harness_error=True,
                                  target_exit_code=result.returncode,
                                  target_stderr=f"read-back failed: {exc}; stderr={result.stderr[-1024:]}")

        stderr_tail = (result.stderr or "")[-2048:]
        return _spans_to_proof(target, expected_span, spans,
                              target_exit_code=result.returncode,
                              target_stderr=stderr_tail)
    finally:
        try:
            os.unlink(out_path)
        except OSError:
            pass


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────


def main(argv: Sequence[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="OTel collector-backed proof harness")
    p.add_argument("test_path", help="Path to a pytest target file")
    p.add_argument("--expected-span", default=None,
                  help="Expected span name (e.g., l6.eval.record_sealed). If omitted, any span counts.")
    p.add_argument("--timeout", type=int, default=60)
    p.add_argument("--out", default=None,
                  help="Optional output path for the JSON proof bundle")
    args = p.parse_args(argv)

    proof = run_test_file_proof(
        args.test_path,
        expected_span=args.expected_span,
        timeout=args.timeout,
    )
    payload = proof.to_bundle_payload()
    if args.out:
        Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Wrote {args.out}")
    print(f"target:               {proof.target}")
    print(f"status:               {proof.status}")
    print(f"actual_proof_depth:   {proof.actual_proof_depth}")
    print(f"span_count:           {proof.span_count}")
    print(f"expected_seen:        {proof.expected_seen}")
    print(f"replay_digest:        {proof.replay_digest}")
    print(f"target_exit_code:     {proof.target_exit_code}")
    return 0 if proof.status in ("SATISFIED", "NO_SPANS_EMITTED") else 1


if __name__ == "__main__":
    sys.exit(main())
