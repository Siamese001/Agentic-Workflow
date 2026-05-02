"""L7_AUDITABILITY — cross-cutting evidence plane for agentic_core.

L7_AUDITABILITY may observe, collect refs, hash, verify, emit evidence,
and fail closed.  L7_AUDITABILITY MUST NOT route, retrieve, assemble
prompts, orchestrate, execute tools/models, judge final output, mutate
current run, or write L4.

This package owns:
    - contracts/how_trace.py             — typed HowTrace and HowTraceStage
    - how_trace/how_trace_builder.py     — pure projection over chain artifacts
    - fortknox/emit_l7_fortknox_evidence.py
                                         — RTC-REQ-bound evidence emitter

The evidence plane is mandatory for every governed runtime run.  It is a
thin projection over already-emitted chain artifacts: it produces a HOW
trace that names, for each spine stage, what ran or was bypassed and
why, with ref+hash binding back to the source artifact.
"""
from __future__ import annotations

__all__: list[str] = []
