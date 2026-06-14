"""Cross-app proof for apps_rg v40 L6 shadow eval and apps_eval bridge."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_eval.contracts import EvalRequest  # noqa: E402
from apps_eval.runner.core import run_eval  # noqa: E402
from apps_rg.runtime.spine.l6_shadow_eval_runner import (  # noqa: E402
    run_l6_v40_shadow_eval_for_section,
)


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _seed_apps_rg_artifacts(run_dir: Path) -> None:
    common = {
        "run_id": "run-l6-v40-e2e",
        "request_id": "req-l6-v40-e2e",
        "trace_root": "trace-l6-v40-e2e",
        "policy_hash": "policy-l6-v40-e2e",
        "blueprint_hash": "blueprint-l6-v40-e2e",
        "replay_key": "replay-l6-v40-e2e",
        "generated_at_utc": _ts(),
    }
    _write(
        run_dir / "runtime_exhaust_bundle.json",
        {
            **common,
            "x3_code": "X3D_ALLOW_FINISH",
            "route_id": "apps_rg.resume_generation",
        },
    )
    _write(
        run_dir / "exit_disposition_receipt.json",
        {**common, "x3_code": "X3D_ALLOW_FINISH", "exit_disposition": "ALLOW_FINISH"},
    )
    _write(
        run_dir / "x3_disposition.json",
        {"x3_code": "X3D_ALLOW_FINISH", "pass": True, "proof_eligible": True},
    )
    _write(run_dir / "x2_gate_outputs.json", {"gates": [], "x2_passed": 0, "x2_failed": 0})
    _write(run_dir / "x1d_llm_judge_outputs.json", {"judges": []})
    _write(run_dir / "route_contract.json", {**common, "route_id": "apps_rg.resume_generation"})
    _write(
        run_dir / "compiled_prompt_artifact.json",
        {"prompt_hash": "prompt-l6-v40-e2e", "allowed_fact_ids": []},
    )
    _write(run_dir / "final_evidence_contract_bridge.json", {"evidence_contract": "ok"})
    _write(run_dir / "provider_request.json", {"prompt_hash": "prompt-l6-v40-e2e"})
    _write(run_dir / "provider_response.json", {"status": "ok"})
    _write(
        run_dir / "l2_output.json",
        {
            **common,
            "section_id": "executive_summary",
            "runtime_generation_status": "OK",
            "prompt_hash": "prompt-l6-v40-e2e",
        },
    )


def main() -> int:
    proof_root = REPO_ROOT / "artifacts" / "proof" / "l6_v40_apps_rg_apps_eval"
    apps_rg_dir = proof_root / "apps_rg_section"
    _seed_apps_rg_artifacts(apps_rg_dir)
    apps_rg_outputs = run_l6_v40_shadow_eval_for_section(
        apps_rg_dir,
        section_id="executive_summary",
        repo_root=REPO_ROOT,
        session_id="sess-l6-v40-e2e",
        tenant_id="tenant-l6-v40-e2e",
        l5_certification_ref="l5-cert-ref:apps-rg:e2e",
    )
    apps_rg_package = json.loads(
        apps_rg_outputs["l6_v40_shadow_eval_package"].read_text(encoding="utf-8")
    )

    eval_record = run_eval(
        EvalRequest(
            suite_id="apps_rg.dev.resume_generation",
            mode="snapshot",
            deterministic_only=True,
            out_dir=str(proof_root / "apps_eval_runs"),
            emit_l6_handoff=True,
        )
    )
    bridge_path = Path(eval_record.artifact_paths["l6_shadow_bridge"])
    bridge = json.loads(bridge_path.read_text(encoding="utf-8"))

    proof = {
        "schema_version": "l6_v40_apps_rg_apps_eval_e2e.v1",
        "generated_at": _ts(),
        "apps_rg": {
            "package_ref": str(apps_rg_outputs["l6_v40_shadow_eval_package"]),
            "readiness_decision": apps_rg_package.get("readiness_decision"),
            "g28_verdict": (apps_rg_package.get("g28_audit_completeness") or {}).get("verdict"),
            "g29_verdict": (apps_rg_package.get("g29_learning_firewall") or {}).get("verdict"),
            "current_run_mutation_assertion": apps_rg_package.get("current_run_mutation_assertion"),
        },
        "apps_eval": {
            "record_id": eval_record.record_id,
            "bridge_ref": str(bridge_path),
            "readiness_decision": bridge.get("readiness_decision"),
            "g28_verdict": (bridge.get("g28_audit_completeness") or {}).get("verdict"),
            "g29_verdict": (bridge.get("g29_learning_firewall") or {}).get("verdict"),
            "current_run_mutated": bridge.get("current_run_mutated"),
        },
    }
    out_path = REPO_ROOT / "docs" / "reports" / "plans" / "l6_v40_apps_rg_apps_eval_e2e_proof.json"
    _write(out_path, proof)
    print(f"WROTE {out_path}")
    print(f"  apps_rg_readiness={proof['apps_rg']['readiness_decision']}")
    print(f"  apps_eval_readiness={proof['apps_eval']['readiness_decision']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
