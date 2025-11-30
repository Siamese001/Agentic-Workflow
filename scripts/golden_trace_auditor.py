#!/usr/bin/env python3
"""
golden_trace_auditor.py

Agentic L5 Golden-Flow Trace Auditor
====================================

This validator enforces Agentic L5 expectations for:

- Pillar 4  Structural / Workflow (DAGs) – golden engine flows must be stable
- Pillar 5  Behavioral / Capability Maturity – critical flows are locked by golden traces
- Pillar 6  Behavioral / Reasoning Models – reasoning trajectories must not regress
- Pillar 10 Operational / Observability – traces are captured and comparable
- Pillar 11 Operational / Cost & Optimization – no unexpected engine changes
- Pillar 12 Operational / Testing (Golden State) – golden-state regression guardrail

Conceptually it does the following:

1) Loads the *canonical* golden trace spec:
      data/golden/golden_traces.json

   Expected shape (minimal, extensible):

      {
        "schema_version": "1.0.0",
        "flows": [
          {
            "id": "resume_happy_path",
            "description": "...",
            "hash": "<hex sha256>",
            "metadata": {...}   # optional
          },
          ...
        ]
      }

2) Loads the *current* golden run traces:
      ci_reports/golden_traces_current.json

   with the exact same structural expectations.

   NOTE:
   - The current traces file must be produced by either:
       a) an external CI step that runs `python main.py --golden-flow ...`
          and writes a JSON snapshot; OR
       b) any golden runner that aggregates trace spans into a deterministic
          JSON representation.

3) Compares the two sets:
   - ID sets must match exactly (no missing/no extra)
   - For each flow id:
       - `hash` field must match (case-insensitive hex)
   - Optionally, schema_version must match (best practice).

4) Emits violations for:
   - Missing golden_traces.json
   - Missing or malformed golden_traces_current.json
   - Structural issues in either file
   - ID set mismatches
   - Hash mismatches per flow

Exit codes:
- 0: all checks pass
- 1: violations detected

This script is intentionally strict. If the orchestrator or engine
changes in a way that affects the golden traces, the golden spec must
be updated in a deliberate, version-controlled manner.
"""

import json
import os
import sys
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple


# =====================================================================
# CONFIG
# =====================================================================

DEFAULT_REPO_ROOT = (
    r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines"
    r"\Resume Gen\Git\Agentic_Workflow-10_11"
)
REPO_ROOT = os.getenv("AGENTIC_REPO_ROOT", DEFAULT_REPO_ROOT)

GOLDEN_SPEC_PATH = os.path.join(REPO_ROOT, "data", "golden", "golden_traces.json")
CURRENT_RUN_PATH = os.path.join(REPO_ROOT, "ci_reports", "golden_traces_current.json")


@dataclass
class Violation:
    code: str
    message: str
    path: str


# =====================================================================
# HELPERS
# =====================================================================

def rel(path: str) -> str:
    try:
        return os.path.relpath(path, REPO_ROOT)
    except ValueError:
        return path


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_hash(h: str) -> str:
    if not isinstance(h, str):
        return ""
    return h.strip().lower()


def compute_flow_hash(flow: Dict[str, Any]) -> str:
    """
    Compute a canonical hash over the 'flow' entry itself, excluding the
    'hash' field. This can be used both to verify the stored hash is
    consistent and to recompute if needed.

    NOTE: This isn't strictly required to compare golden_spec vs current;
    we trust that both sides already stored hashes. This function is a
    safety net and may be used in future enhancements.
    """
    # Copy without 'hash'
    clone = {k: v for k, v in flow.items() if k != "hash"}
    # Canonical JSON encoding
    payload = json.dumps(clone, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def extract_flows(data: Any, path: str, violations: List[Violation]) -> Tuple[str, Dict[str, Dict[str, Any]]]:
    """
    Validate top-level shape and extract flows as a mapping: id -> flow_dict.

    Returns:
        (schema_version: str, flows_by_id: dict[id -> flow])
    """
    if not isinstance(data, dict):
        violations.append(
            Violation(
                code="GOLDEN_ROOT_NOT_OBJECT",
                message="Golden traces JSON root must be an object",
                path=rel(path),
            )
        )
        return "", {}

    schema_version = data.get("schema_version", "")
    if not isinstance(schema_version, str) or not schema_version.strip():
        violations.append(
            Violation(
                code="GOLDEN_SCHEMA_VERSION_MISSING",
                message="Golden traces must define a non-empty 'schema_version' string",
                path=rel(path),
            )
        )

    flows = data.get("flows")
    if not isinstance(flows, list):
        violations.append(
            Violation(
                code="GOLDEN_FLOWS_NOT_LIST",
                message="'flows' must be a list",
                path=rel(path),
            )
        )
        return schema_version, {}

    flows_by_id: Dict[str, Dict[str, Any]] = {}
    for idx, flow in enumerate(flows):
        if not isinstance(flow, dict):
            violations.append(
                Violation(
                    code="GOLDEN_FLOW_NOT_OBJECT",
                    message=f"Flow at index {idx} must be an object",
                    path=rel(path),
                )
            )
            continue

        fid = flow.get("id")
        if not isinstance(fid, str) or not fid.strip():
            violations.append(
                Violation(
                    code="GOLDEN_FLOW_ID_MISSING",
                    message=f"Flow at index {idx} missing non-empty 'id'",
                    path=rel(path),
                )
            )
            continue
        fid = fid.strip()

        if fid in flows_by_id:
            violations.append(
                Violation(
                    code="GOLDEN_FLOW_ID_DUPLICATE",
                    message=f"Duplicate flow id '{fid}' in {rel(path)}",
                    path=rel(path),
                )
            )
            continue

        # Ensure 'hash' exists
        if "hash" not in flow or not isinstance(flow["hash"], str) or not flow["hash"].strip():
            violations.append(
                Violation(
                    code="GOLDEN_FLOW_HASH_MISSING",
                    message=f"Flow '{fid}' missing non-empty 'hash'",
                    path=rel(path),
                )
            )

        flows_by_id[fid] = flow

    return schema_version, flows_by_id


# =====================================================================
# COMPARISON
# =====================================================================

def compare_schema_versions(
    spec_version: str,
    current_version: str,
    violations: List[Violation],
) -> None:
    """
    Warn/fail if schema versions drift; for strictness we treat mismatch
    as a violation to force explicit updates.
    """
    if not spec_version or not current_version:
        # Already reported as violations (missing)
        return

    if spec_version != current_version:
        violations.append(
            Violation(
                code="GOLDEN_SCHEMA_VERSION_MISMATCH",
                message=f"Golden schema_version mismatch: spec={spec_version}, current={current_version}",
                path=rel(GOLDEN_SPEC_PATH),
            )
        )


def compare_flows(
    spec_flows: Dict[str, Dict[str, Any]],
    current_flows: Dict[str, Dict[str, Any]],
    violations: List[Violation],
) -> None:
    spec_ids = set(spec_flows.keys())
    current_ids = set(current_flows.keys())

    missing_ids = spec_ids - current_ids
    extra_ids = current_ids - spec_ids

    for fid in sorted(missing_ids):
        violations.append(
            Violation(
                code="GOLDEN_FLOW_MISSING",
                message=f"Golden flow id '{fid}' missing in current run",
                path=rel(CURRENT_RUN_PATH),
            )
        )

    for fid in sorted(extra_ids):
        violations.append(
            Violation(
                code="GOLDEN_FLOW_UNEXPECTED",
                message=f"Unexpected flow id '{fid}' present in current run but not in spec",
                path=rel(CURRENT_RUN_PATH),
            )
        )

    # Compare hashes for common IDs
    common_ids = spec_ids & current_ids
    for fid in sorted(common_ids):
        spec_hash = normalize_hash(spec_flows[fid].get("hash", ""))
        curr_hash = normalize_hash(current_flows[fid].get("hash", ""))

        if not spec_hash or not curr_hash:
            # Already reported missing hash above
            continue

        if spec_hash != curr_hash:
            violations.append(
                Violation(
                    code="GOLDEN_FLOW_HASH_MISMATCH",
                    message=f"Flow '{fid}' hash mismatch: spec={spec_hash}, current={curr_hash}",
                    path=rel(CURRENT_RUN_PATH),
                )
            )


# =====================================================================
# MAIN
# =====================================================================

def main() -> None:
    violations: List[Violation] = []

    # 1. Ensure golden spec exists
    golden_spec = {}
    if not os.path.isfile(GOLDEN_SPEC_PATH):
        violations.append(
            Violation(
                code="GOLDEN_SPEC_MISSING",
                message=f"Golden spec not found at {rel(GOLDEN_SPEC_PATH)}",
                path=rel(GOLDEN_SPEC_PATH),
            )
        )
    else:
        golden_spec = {}
        try:
            golden_spec = load_json(GOLDEN_SPEC_PATH)
        except Exception as e:
            violations.append(
                Violation(
                    code="GOLDEN_SPEC_LOAD_ERROR",
                    message=f"Failed to load golden spec: {e}",
                    path=rel(GOLDEN_SPEC_PATH),
                )
            )
            golden_spec = {}

    # 2. Ensure current run traces exist
    if not os.path.isfile(CURRENT_RUN_PATH):
        violations.append(
            Violation(
                code="GOLDEN_CURRENT_MISSING",
                message=f"Current golden run traces not found at {rel(CURRENT_RUN_PATH)}",
                path=rel(CURRENT_RUN_PATH),
            )
        )
        current = {}
    else:
        try:
            current = load_json(CURRENT_RUN_PATH)
        except Exception as e:
            violations.append(
                Violation(
                    code="GOLDEN_CURRENT_LOAD_ERROR",
                    message=f"Failed to load current golden traces: {e}",
                    path=rel(CURRENT_RUN_PATH),
                )
            )
            current = {}

    # If either side failed to load, we already have violations but still attempt structure checks
    spec_version = ""
    spec_flows: Dict[str, Dict[str, Any]] = {}
    current_version = ""
    current_flows: Dict[str, Dict[str, Any]] = {}

    if isinstance(golden_spec, dict):
        spec_version, spec_flows = extract_flows(golden_spec, GOLDEN_SPEC_PATH, violations)

    if isinstance(current, dict):
        current_version, current_flows = extract_flows(current, CURRENT_RUN_PATH, violations)

    # Compare schema versions
    compare_schema_versions(spec_version, current_version, violations)

    # Compare flows and hashes
    compare_flows(spec_flows, current_flows, violations)

    # Output
    if not violations:
        print("[golden_trace_auditor] OK: All golden-flow traces match specification.")
        sys.exit(0)

    print("[golden_trace_auditor] FAIL: Violations detected.")
    for v in violations:
        print(f"[{v.code}] {v.message} :: {v.path}")
    sys.exit(1)


if __name__ == "__main__":
    main()
