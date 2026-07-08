import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

root = Path.cwd()
run_id = "adg_p1_ratchet_burndown_wave1_20260708T144236Z"

def run(argv):
    return subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=30, check=False)

changed = run(["git", "diff", "--name-only"]).stdout.splitlines()
untracked = run(["git", "ls-files", "--others", "--exclude-standard"]).stdout.splitlines()
files_changed = [p for p in changed + untracked if p and not p.startswith("artifacts/")]
head = run(["git", "rev-parse", "HEAD"]).stdout.strip()
branch = run(["git", "branch", "--show-current"]).stdout.strip()
receipt = {
    "schema_version": "codex-run-receipt/v1",
    "run_id": run_id,
    "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "repo": {
        "root": "C:\\Git\\Agentic-Workflow-FRESH",
        "worktree": str(root),
        "branch": branch,
        "head": head,
        "dirty_before": True,
        "dirty_after": True,
    },
    "scope": {
        "request": "Implement the first P1 ratchet burndown wave.",
        "plan_id": "plans/adg-p1-ratchet-burndown-wave-plan-4c8d2a.md",
        "files_changed": files_changed,
    },
    "execution": {
        "status": "PARTIAL",
        "commands": [
            {"command": "python tools/adg/consume_adg_repair_handoff.py --handoff-pointer C:\\Git\\Agentic-Workflow-FRESH\\artifacts\\adg\\handoffs\\adg_repair_handoff_latest.json --json", "cwd": "C:\\Git\\Agentic-Workflow-FRESH", "status": "PASS", "exit_code": 0},
            {"command": "python artifacts\\codex\\runtime_proofs\\refactor_e1_trace_imports.py --snapshot C:\\Git\\Agentic-Workflow-FRESH\\artifacts\\adg\\adg_indexed_07072026_2307.sqlite --repo-root . --limit 50 --apply --manifest artifacts\\codex\\runtime_proofs\\e1_trace_import_wave1_manifest.json", "cwd": str(root), "status": "PASS", "exit_code": 0},
            {"command": "python -m compileall -q <all changed python files>", "cwd": str(root), "status": "PASS", "exit_code": 0},
            {"command": "python artifacts\\codex\\runtime_proofs\\e1_trace_import_wave1_source_replay.py . artifacts\\codex\\runtime_proofs\\e1_trace_import_wave1_manifest.json artifacts\\codex\\runtime_proofs\\e1_trace_import_wave1_source_replay.json", "cwd": str(root), "status": "PASS", "exit_code": 0},
            {"command": "python artifacts\\codex\\runtime_proofs\\e1_trace_import_wave1_runtime_proof.py artifacts\\codex\\runtime_proofs\\e1_trace_import_wave1_runtime_importable_subset_manifest.json artifacts\\codex\\runtime_proofs\\e1_trace_import_wave1_runtime_importable_subset_proof.json", "cwd": str(root), "status": "PASS", "exit_code": 0},
            {"command": "python artifacts\\codex\\runtime_proofs\\e1_trace_import_wave1_runtime_proof.py artifacts\\codex\\runtime_proofs\\e1_trace_import_wave1_manifest.json artifacts\\codex\\runtime_proofs\\e1_trace_import_wave1_runtime_proof.json", "cwd": str(root), "status": "BLOCKED", "exit_code": 1},
            {"command": "python -m pytest tests\\unit\\agentic_core\\L2_execution\\test_l2_package_driven_repair.py tests\\unit\\agentic_core\\L3_orchestration\\exit_eval\\test_http_judges.py -q", "cwd": str(root), "status": "PASS", "exit_code": 0},
            {"command": "$env:ADG_SNAPSHOT='C:\\Git\\Agentic-Workflow-FRESH\\artifacts\\adg\\adg_indexed_07072026_2307.sqlite'; python ops_scripts\\ci\\check_trace_stub_modules.py", "cwd": str(root), "status": "PASS", "exit_code": 0},
            {"command": "git diff --check", "cwd": str(root), "status": "PASS", "exit_code": 0},
        ],
        "fallbacks": [
            {"route": "adg_sqlite", "reason": "ADG MCP tool namespace unavailable in this Codex session; immutable digest-bound SQLite snapshot used for wave selection and lightweight source replay.", "substitute": "degraded_sqlite snapshot adg_indexed_07072026_2307.sqlite"}
        ],
    },
    "verification": {
        "checks": [
            {"name": "handoff_validator", "status": "PASS", "evidence": "dependency_status=ready artifact_status=repair_ready adg_run_id=07072026_2307 P0_FIX=0 P0_WAVE=0 P1_FIX=0 P1_RATCHET_FLOOR_BACKLOG=7 P1_RATCHET_REGRESSION=0"},
            {"name": "ordinary_p1_repair", "status": "PASS", "evidence": "Existing ordinary P1 patch remains in branch; focused pytest collected 6 and passed 6."},
            {"name": "e1_wave1_source_replay", "status": "PASS", "evidence": "50 selected E1 modules now use trace_contract alias and have zero direct lifecycle trace symbol imports; artifact artifacts/codex/runtime_proofs/e1_trace_import_wave1_source_replay.json reports passed=50 failed=0."},
            {"name": "e1_wave1_runtime_import_subset", "status": "PASS", "evidence": "Runtime import proof for importable subset reports passed=47 failed=0; full manifest import proof captured 3 pre-existing import-time blockers."},
            {"name": "e1_snapshot_gate", "status": "PASS", "evidence": "Pinned consumed snapshot gate remains current=982 baseline=982; no regression against released ADG evidence. Improvement requires regenerated ADG."},
            {"name": "compileall", "status": "PASS", "evidence": "compileall passed for all changed Python files and runtime proof helpers."},
            {"name": "target_status", "status": "BLOCKED", "evidence": "target_status=missed/BLOCKED because P1=0 is not proven; expected E1 reduction is 50 rows on next ADG generation, remaining P1 ratchet backlog still requires follow-on waves."},
        ]
    },
    "rca": {
        "symptom": "First E1 wave is implemented but P1=0 is not proven.",
        "root_cause": "This wave intentionally reduces only the first 50 E1 trace-stub modules; the full ratchet backlog remains broad and requires additional waves plus regenerated ADG proof.",
        "evidence": "Source replay passed 50/50 selected modules; runtime import proof passed 47/47 importable modules; full import proof captured three pre-existing import blockers; pinned E1 gate remains pass against consumed snapshot.",
        "fix_or_next": "next: run regenerated/lightweight ADG to confirm E1 expected count reduction, then continue W2 wave 2 or publish this partial wave if merge gates are satisfied.",
        "recurrence_guard": "Keep downstream P2/P3 blocked until fresh/replayed ADG evidence reports P1_FIX=0, P1_RATCHET_REGRESSION=0, and P1_RATCHET_FLOOR_BACKLOG=0."
    },
    "p1_wave": {
        "wave": "W2.E1.1",
        "gate": "E1_trace_stub_module",
        "selected_rows": 50,
        "expected_e1_reduction_on_regen": 50,
        "target_status": "missed/BLOCKED",
        "downstream_unblock": False,
        "artifacts": [
            "artifacts/codex/runtime_proofs/e1_trace_import_wave1_manifest.json",
            "artifacts/codex/runtime_proofs/e1_trace_import_wave1_source_replay.json",
            "artifacts/codex/runtime_proofs/e1_trace_import_wave1_runtime_importable_subset_proof.json",
            "artifacts/codex/runtime_proofs/e1_trace_import_wave1_runtime_proof.json"
        ]
    }
}
out = root / "artifacts" / "codex" / "run_receipts" / f"{run_id}.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
print(out)
