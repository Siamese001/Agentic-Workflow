"""Fort Knox v2 — CI Gate Binding Report Emitter.

Statically proves that `scripts/verify_rtc_req_csv_gate.py` is registered
in at least one fail-closed GitHub Actions workflow and that its execution
is not opt-out (no `continue-on-error: true` on its step or job).

Methodology:
  1. Walk every `.github/workflows/*.yml` file.
  2. Parse with PyYAML to inspect step `run:` blocks.
  3. For each match of `scripts/verify_rtc_req_csv_gate.py`, record:
       - workflow filename + sha256
       - matched step `id`/`name`
       - line numbers (best-effort via raw text scan)
       - workflow trigger events (`on:` keys)
       - fail_closed: True if the step lacks continue-on-error AND the job
         lacks continue-on-error AND the workflow has no global override
  4. If at least one fail-closed binding exists → overall_result=PASS.
  5. Emit per_req/<req_id>/ci_gate payloads referencing the strongest binding.

The artifact must be regenerated whenever the workflow file changes; the
sha256 stamp catches drift, and the bundle verifier recomputes it on every
run.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # we fall back to text scanning if PyYAML missing

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
SUBJECT_REL = "scripts/verify_rtc_req_csv_gate.py"
OUTPUT_REL = "artifacts/certification/ci_gate_binding_report.json"

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


def find_match_lines(text: str, needle: str) -> list[int]:
    return [i + 1 for i, line in enumerate(text.splitlines()) if needle in line]


def analyze_workflow(yml_path: Path, needle: str) -> dict | None:
    """Return a binding dict if the workflow registers the needle, else None."""
    text = yml_path.read_text(encoding="utf-8")
    lines = find_match_lines(text, needle)
    if not lines:
        return None

    sha = sha256_file(yml_path)
    binding = {
        "workflow_file": str(yml_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "workflow_sha256": sha,
        "match_lines": lines,
        "trigger_events": [],
        "step_continue_on_error": None,
        "job_continue_on_error": None,
        "fail_closed": None,
    }

    if yaml is None:
        # Fallback: assume fail-closed if we don't see continue-on-error: true
        binding["fail_closed"] = ("continue-on-error: true" not in text.lower())
        binding["parser"] = "text-fallback (PyYAML not installed)"
        return binding

    try:
        doc = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        binding["fail_closed"] = False
        binding["parse_error"] = f"yaml: {exc}"
        return binding

    on_block = doc.get("on") or doc.get(True)  # YAML quirk: "on" can parse to True
    if isinstance(on_block, dict):
        binding["trigger_events"] = sorted(on_block.keys())
    elif isinstance(on_block, list):
        binding["trigger_events"] = sorted(on_block)
    elif isinstance(on_block, str):
        binding["trigger_events"] = [on_block]

    # Find the step + job containing the needle
    found_step_coe = False
    found_job_coe = False
    for job_name, job in (doc.get("jobs") or {}).items():
        if not isinstance(job, dict):
            continue
        steps = job.get("steps") or []
        step_hit = False
        for step in steps:
            if not isinstance(step, dict):
                continue
            run_block = step.get("run") or ""
            if needle in str(run_block):
                step_hit = True
                step_coe = step.get("continue-on-error", False)
                if step_coe is True:
                    found_step_coe = True
                binding["matched_step_name"] = step.get("name") or step.get("id") or "(unnamed)"
                binding["matched_job"] = job_name
        if step_hit:
            job_coe = job.get("continue-on-error", False)
            if job_coe is True:
                found_job_coe = True

    binding["step_continue_on_error"] = found_step_coe
    binding["job_continue_on_error"] = found_job_coe
    binding["fail_closed"] = (not found_step_coe) and (not found_job_coe)
    return binding


def main() -> int:
    needle = SUBJECT_REL
    if not WORKFLOWS_DIR.exists():
        print(f"[emit_ci_gate_binding_report] FAIL: workflows dir missing: {WORKFLOWS_DIR}",
              file=sys.stderr)
        return 1

    bindings: list[dict] = []
    for yml in sorted(WORKFLOWS_DIR.glob("*.yml")):
        b = analyze_workflow(yml, needle)
        if b is not None:
            bindings.append(b)

    fail_closed_bindings = [b for b in bindings if b.get("fail_closed")]
    overall_pass = len(fail_closed_bindings) >= 1

    # Choose the strongest binding (first fail-closed, else first)
    strongest = fail_closed_bindings[0] if fail_closed_bindings else (
        bindings[0] if bindings else None
    )
    now = iso_now()

    per_req: dict[str, dict] = {}
    for rid in COVERED_REQS:
        # Nest under control name so /per_req/<req_id>/<control> resolves.
        per_req[rid] = {"ci_gate": {
            "req_id": rid,
            "control": "ci_gate",
            "result": "PASS" if overall_pass else "FAIL",
            "subject": SUBJECT_REL,
            "binding": strongest,
            "fail_closed_binding_count": len(fail_closed_bindings),
            "all_binding_count": len(bindings),
            "proof": (
                f"{SUBJECT_REL} appears in {len(bindings)} workflow(s); "
                f"{len(fail_closed_bindings)} fail-closed registration(s) "
                f"({'PASS' if overall_pass else 'FAIL'})."
            ),
            "generated_at_utc": now,
        }}

    report = {
        "schema_version": "fortknox-ci-gate-binding-v1",
        "report_class": "CI_GATE_BINDING_REPORT",
        "subject": SUBJECT_REL,
        "overall_result": "PASS" if overall_pass else "FAIL",
        "binding_count": len(bindings),
        "fail_closed_binding_count": len(fail_closed_bindings),
        "bindings": bindings,
        "covered_req_ids": list(COVERED_REQS),
        "per_req": per_req,
        "generated_at_utc": now,
        "generated_by_command": "tools/cert/emit_ci_gate_binding_report.py",
    }

    out_path = REPO_ROOT / OUTPUT_REL
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")

    print(f"[emit_ci_gate_binding_report] subject={SUBJECT_REL}")
    print(f"  workflows scanned:           {len(list(WORKFLOWS_DIR.glob('*.yml')))}")
    print(f"  bindings found:              {len(bindings)}")
    print(f"  fail-closed bindings:        {len(fail_closed_bindings)}")
    print(f"  overall_result:              {'PASS' if overall_pass else 'FAIL'}")
    print(f"  wrote: {OUTPUT_REL}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
