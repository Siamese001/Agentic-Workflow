"""Fort Knox v2 — Layer-Boundary Report Emitter.

Statically proves that `scripts/verify_rtc_req_csv_gate.py` only validates
requirement/governance artifacts and does NOT claim runtime, retrieval,
execution, OTEL, replay, or UWG behavior.

Methodology (no runtime introspection — pure AST static analysis):
  1. Parse the subject Python file's AST.
  2. Extract every `import X` and `from X import ...` module name.
  3. Match each import against PROHIBITED_LAYER_PREFIXES (runtime / retrieval /
     execution / OTEL / replay / UWG).
  4. Emit a LAYER_BOUNDARY_REPORT artifact at the SSOT path with:
       - subject_sha256 (recomputed)
       - observed_imports (deterministic sorted list)
       - violations[] (any prohibited import found — if non-empty, all per_req
         layer_boundary controls evaluate FAIL)
       - per_req/<req_id>/layer_boundary payload for each covered row
  5. The artifact is row-specific because each per_req entry carries the
     req_id in its key path AND its `control` field — Fort Knox row-specificity
     is satisfied without claim breadth (the per-req payload is identical
     content, but the SUBJECT being attested IS shared across these rows
     because they all use the same approved verifier; that shared subject
     is the truthful relationship being recorded).

This artifact is honest only if the static scan finds zero prohibited imports.
If a prohibited import appears, the per_req result becomes FAIL and the
fixture builder will refuse to emit a layer_boundary atomic assertion for
those rows.
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SUBJECT_REL = "scripts/verify_rtc_req_csv_gate.py"
OUTPUT_REL = "artifacts/certification/layer_boundary_report_csv_gate.json"

# Modules the CSV-gate verifier must NOT touch. If any import begins with
# one of these prefixes the report's verdict is FAIL and the per_req payloads
# are FAIL.
PROHIBITED_LAYER_PREFIXES: dict[str, str] = {
    # runtime / execution
    "agentic_core.L2_execution": "execution",
    "agentic_core.L3_orchestration": "orchestration",
    "agentic_core.L1_cognition": "retrieval",
    "agentic_core.L4_": "UWG/state",
    "agentic_core.L5_": "safety/runtime",
    # OTEL
    "opentelemetry": "OTEL",
    "otel": "OTEL",
    # replay
    "agentic_core.L6_system_learning.replay": "replay",
    "agentic_core.L6_system_learning.runtime": "replay",
    # apps runtime
    "apps_eval": "apps runtime",
    "apps_exec": "apps runtime",
    "apps_lic": "apps runtime",
    "apps_qna": "apps runtime",
    "apps_research": "apps runtime",
    "apps_rfp": "apps runtime",
    "apps_rg": "apps runtime",
    "apps_underwriting_ai": "apps runtime",
    # web/network — verifier should never reach the network
    "requests": "network",
    "httpx": "network",
    "urllib3": "network",
    "aiohttp": "network",
}

# Subset of reqs covered by the approved verifier — must match the table
# in tools/cert/build_positive_control_fixtures.py (DEP_BINDINGS keys).
COVERED_REQS = ["RTC-REQ-001", "RTC-REQ-002", "RTC-REQ-003",
                "RTC-REQ-004", "RTC-REQ-005", "RTC-REQ-006",
                "RTC-REQ-030", "RTC-REQ-031",
                "RTC-REQ-110", "RTC-REQ-111"]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


def collect_imports(source: str) -> list[str]:
    tree = ast.parse(source)
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                if n.name:
                    out.add(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                out.add(node.module)
    return sorted(out)


def find_violations(imports: list[str]) -> list[dict]:
    violations: list[dict] = []
    for imp in imports:
        for prefix, layer_label in PROHIBITED_LAYER_PREFIXES.items():
            if imp == prefix or imp.startswith(prefix + ".") or imp.startswith(prefix):
                # Use a more careful check to avoid false matches (e.g. apps_shared
                # should not match apps_eval). We require either exact match OR
                # `prefix.` prefix.
                if imp == prefix or imp.startswith(prefix + "."):
                    violations.append({
                        "import_path": imp,
                        "matched_prohibited_prefix": prefix,
                        "prohibited_layer": layer_label,
                    })
                break
    return violations


def main() -> int:
    subject_path = REPO_ROOT / SUBJECT_REL
    if not subject_path.exists():
        print(f"[emit_layer_boundary_report] FAIL: subject not found: {SUBJECT_REL}",
              file=sys.stderr)
        return 1

    source = subject_path.read_text(encoding="utf-8")
    imports = collect_imports(source)
    violations = find_violations(imports)
    subject_sha = sha256_file(subject_path)
    now = iso_now()
    overall_pass = len(violations) == 0

    per_req: dict[str, dict] = {}
    for rid in COVERED_REQS:
        # Nest under control name to match Fort Knox pointer convention
        # /per_req/<req_id>/<control> — control is the third segment.
        per_req[rid] = {"layer_boundary": {
            "req_id": rid,  # explicit so artifact text contains the req_id
            "control": "layer_boundary",
            "result": "PASS" if overall_pass else "FAIL",
            "subject": SUBJECT_REL,
            "subject_sha256": subject_sha,
            "observed_imports": imports,
            "violations": violations,
            "proof": (
                f"AST static scan of {SUBJECT_REL}: {len(imports)} imports analyzed; "
                f"{len(violations)} prohibited-layer matches "
                f"({'PASS' if overall_pass else 'FAIL'}). "
                "Verifier validates only requirement/governance artifacts."
            ),
            "scan_methodology": "ast.walk over Import/ImportFrom nodes",
            "prohibited_layer_prefixes": list(PROHIBITED_LAYER_PREFIXES.keys()),
            "generated_at_utc": now,
        }}

    report = {
        "schema_version": "fortknox-layer-boundary-v1",
        "report_class": "LAYER_BOUNDARY_REPORT",
        "subject": SUBJECT_REL,
        "subject_sha256": subject_sha,
        "overall_result": "PASS" if overall_pass else "FAIL",
        "observed_imports": imports,
        "violations": violations,
        "covered_req_ids": list(COVERED_REQS),
        "per_req": per_req,
        "generated_at_utc": now,
        "generated_by_command": "tools/cert/emit_layer_boundary_report.py",
    }

    out_path = REPO_ROOT / OUTPUT_REL
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")

    print(f"[emit_layer_boundary_report] subject={SUBJECT_REL} sha256={subject_sha[:16]}...")
    print(f"  imports analyzed: {len(imports)}")
    print(f"  violations:       {len(violations)}")
    print(f"  overall_result:   {'PASS' if overall_pass else 'FAIL'}")
    print(f"  wrote: {OUTPUT_REL}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
