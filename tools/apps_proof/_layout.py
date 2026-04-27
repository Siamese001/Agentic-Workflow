"""User-spec proof artifact tree — single source of truth for the layout.

``artifacts/apps_proof/<app_name>/<run_id>/`` per the master plan §"PROOF
ARTIFACT STRUCTURE". This module owns the directory layout, sub-paths, and
helper functions for re-organising scenario_base output into the user's
exact tree.

No I/O happens at import time. All paths are pure ``Path`` arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Canonical sub-directories under <proof_root>/<app>/<run_id>/.
TRACE_DIR = "trace"
CONTRACTS_DIR = "contracts"
GATES_DIR = "gates"
REPLAY_DIR = "replay"
ADG_DIR = "adg"
VERIFIER_DIR = "verifier"

# Canonical contract filenames per master plan.
# Maps logical kind → on-disk basename. The runner aliases scenario_base
# contract files (which use content-hash suffixes) onto these stable names.
CONTRACT_FILE_BY_KIND: dict[str, str] = {
    # Spine contracts (scenario_base)
    "ValidatedRequest": "u0_validated_request.json",
    "L1PlanContract": "l1_plan_contract.json",
    "RouteContract": "l0_route_contract.json",
    "RetrievalPlan": "c0_retrieval_plan.json",
    "FinalEvidenceContract": "c0_final_evidence_contract.json",
    "PromptEnvelope": "prompt_assembly_manifest.json",
    "L3WorkflowContract": "l3_workflow_contract.json",
    "L2ExecutionRequest": "l2_execution_request.json",
    "SealedArtifact": "l2_sealed_artifact.json",
    "ExitReviewPacket": "exit_review_packet.json",
    "ExitDecision": "exit_disposition.json",
    "UWGCommitRequest": "uwg_commit_request.json",
    "UWGCommitReceipt": "uwg_commit_receipt.json",
    "RuntimeExhaustBundle": "runtime_exhaust_bundle.json",
    "L6ShadowEvalRecord": "l6_shadow_eval_record.json",
    # App-runtime driver artifacts (W2)
    "DecisionPacket": "decision_packet.json",
    "DecisionMemo": "decision_memo.json",
    "AuditTrace": "audit_trace.json",
    "EvidenceRegister": "evidence_register.json",
    "ExceptionRegister": "exception_register.json",
}

# Canonical L3 step list filename (JSONL, one record per step).
L3_STEP_CONTRACTS_FILE = "l3_step_contracts.jsonl"


@dataclass(frozen=True)
class ProofRunPaths:
    """Resolved paths for one proof run.

    All paths are absolute; sub-directories are created on demand by the
    runner via :meth:`mkdirs`.
    """

    proof_root: Path  # artifacts/apps_proof
    app_name: str
    run_id: str

    @property
    def app_root(self) -> Path:
        return self.proof_root / self.app_name

    @property
    def run_root(self) -> Path:
        return self.app_root / self.run_id

    @property
    def trace_dir(self) -> Path:
        return self.run_root / TRACE_DIR

    @property
    def contracts_dir(self) -> Path:
        return self.run_root / CONTRACTS_DIR

    @property
    def gates_dir(self) -> Path:
        return self.run_root / GATES_DIR

    @property
    def replay_dir(self) -> Path:
        return self.run_root / REPLAY_DIR

    @property
    def adg_dir(self) -> Path:
        return self.run_root / ADG_DIR

    @property
    def verifier_dir(self) -> Path:
        return self.run_root / VERIFIER_DIR

    @property
    def run_manifest(self) -> Path:
        return self.run_root / "run_manifest.json"

    @property
    def run_request(self) -> Path:
        return self.run_root / "run_request.json"

    @property
    def proof_verdict(self) -> Path:
        return self.verifier_dir / "proof_verdict.json"

    @property
    def proof_report(self) -> Path:
        return self.verifier_dir / "proof_report.md"

    @property
    def failure_reasons(self) -> Path:
        return self.verifier_dir / "failure_reasons.jsonl"

    @property
    def replay_comparison(self) -> Path:
        return self.replay_dir / "replay_comparison.json"

    @property
    def replay_run1(self) -> Path:
        return self.replay_dir / "replay_run_1.json"

    @property
    def replay_run2(self) -> Path:
        return self.replay_dir / "replay_run_2.json"

    @property
    def deterministic_digest_report(self) -> Path:
        return self.replay_dir / "deterministic_digest_report.json"

    @property
    def adg_before(self) -> Path:
        return self.adg_dir / "adg_before.json"

    @property
    def adg_after(self) -> Path:
        return self.adg_dir / "adg_after.json"

    @property
    def adg_delta(self) -> Path:
        return self.adg_dir / "adg_delta.json"

    @property
    def otel_trace(self) -> Path:
        return self.trace_dir / "otel_trace.json"

    @property
    def span_tree(self) -> Path:
        return self.trace_dir / "span_tree.txt"

    @property
    def span_coverage(self) -> Path:
        return self.trace_dir / "span_coverage.json"

    @property
    def gate_verdicts_jsonl(self) -> Path:
        return self.gates_dir / "gate_verdicts.jsonl"

    @property
    def gate_summary(self) -> Path:
        return self.gates_dir / "gate_summary.md"

    @property
    def l3_step_contracts(self) -> Path:
        return self.contracts_dir / L3_STEP_CONTRACTS_FILE

    def mkdirs(self) -> None:
        """Create every sub-directory the runner needs."""
        for d in (
            self.run_root,
            self.trace_dir,
            self.contracts_dir,
            self.gates_dir,
            self.replay_dir,
            self.adg_dir,
            self.verifier_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)

    def contract_path(self, kind: str) -> Path:
        """Resolve the canonical filename for ``kind`` under contracts/."""
        if kind not in CONTRACT_FILE_BY_KIND:
            return self.contracts_dir / f"{kind.lower()}.json"
        return self.contracts_dir / CONTRACT_FILE_BY_KIND[kind]


__all__ = [
    "TRACE_DIR",
    "CONTRACTS_DIR",
    "GATES_DIR",
    "REPLAY_DIR",
    "ADG_DIR",
    "VERIFIER_DIR",
    "CONTRACT_FILE_BY_KIND",
    "L3_STEP_CONTRACTS_FILE",
    "ProofRunPaths",
]
