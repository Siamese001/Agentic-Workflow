"""Audit the 138 blocker modules for existing scanner-visible symbols.

Determines which modules already have emit_determinism_digest() calls
(now scanner-visible after schema fix) and which need record_execution_trace()
calls added.
"""
from __future__ import annotations

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TARGETS_JSON = os.path.join(ROOT, "artifacts", "adg", "_convergence_blocker_targets.json")

with open(TARGETS_JSON) as f:
    data = json.load(f)

trace_blockers = data["trace_blockers"]

# Patterns to search for
DIGEST_PATTERN = re.compile(r"emit_determinism_digest\s*\(")
TRACE_PATTERN = re.compile(r"record_execution_trace\s*\(")
# Also check for EXECUTION_TRACE_CLASSES symbols
EXEC_TRACE_CLASSES = {
    "ExecutionTrace", "ExecutionProof", "DeterminismDigest",
    "ProofArtifact", "SignedExecutionTrace", "ExecutionProofEmitter",
    "ReasoningTraceArtifact", "reason_and_record",
    "get_active_execution_trace", "generate_trace_id",
    "get_trace_context", "TraceFeatureExtractor",
}

needs_digest_call = []
needs_trace_call = []
has_digest_call = []
has_trace_call = []
missing_files = []

for entry in trace_blockers:
    module = entry["module"]
    missing = entry["missing"]
    fpath = os.path.join(ROOT, module)

    if not os.path.exists(fpath):
        missing_files.append(module)
        continue

    with open(fpath, encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Check emits_determinism_digest
    if "emits_determinism_digest" in missing:
        if DIGEST_PATTERN.search(content):
            has_digest_call.append(module)
        else:
            needs_digest_call.append(module)

    # Check records_execution_trace
    if "records_execution_trace" in missing:
        has_any_trace = False
        if TRACE_PATTERN.search(content):
            has_any_trace = True
        else:
            for cls in EXEC_TRACE_CLASSES:
                if re.search(rf"\b{cls}\s*\(", content):
                    has_any_trace = True
                    break
        if has_any_trace:
            has_trace_call.append(module)
        else:
            needs_trace_call.append(module)

print("=" * 70)
print("CONVERGENCE WIRING AUDIT")
print("=" * 70)
print(f"\nTotal blocker modules: {len(trace_blockers)}")
print(f"Missing files: {len(missing_files)}")
print("\n--- emits_determinism_digest ---")
print(f"Already have emit_determinism_digest() call (schema fix sufficient): {len(has_digest_call)}")
print(f"Need new emit_determinism_digest() call: {len(needs_digest_call)}")
print("\n--- records_execution_trace ---")
print(f"Already have scanner-visible trace call: {len(has_trace_call)}")
print(f"Need new record_execution_trace() call: {len(needs_trace_call)}")

if needs_digest_call:
    print("\nModules needing emit_determinism_digest() call:")
    for m in sorted(needs_digest_call):
        print(f"  {m}")

if needs_trace_call:
    print("\nModules needing record_execution_trace() call:")
    for m in sorted(needs_trace_call):
        print(f"  {m}")

if missing_files:
    print("\nMissing files:")
    for m in sorted(missing_files):
        print(f"  {m}")

# Write structured output
output = {
    "total_blockers": len(trace_blockers),
    "missing_files": missing_files,
    "digest_already_covered": len(has_digest_call),
    "digest_needs_call": needs_digest_call,
    "trace_already_covered": len(has_trace_call),
    "trace_needs_call": needs_trace_call,
}
out_path = os.path.join(ROOT, "artifacts", "adg", "_convergence_wiring_audit.json")
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nAudit saved to {out_path}")
