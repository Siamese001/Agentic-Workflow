"""Canonical artifact paths for the apps_e2e harness.

SSOT for: where the proof bundle lives, where the static DAG proof lives,
where the matrix lives, and where the run log goes. All paths are derived
from REPO_ROOT and app_name; no per-app special cases.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.certification.apps_e2e.hash_utils import REPO_ROOT

CERT_ROOT = REPO_ROOT / "artifacts" / "certification" / "apps_e2e"
MATRIX_PATH = CERT_ROOT / "apps_e2e_matrix.json"

CORE_CERT_ROOT = REPO_ROOT / "artifacts" / "certification" / "agentic_core_e2e"


@dataclass(frozen=True)
class AppCertPaths:
    app_name: str

    @property
    def app_dir(self) -> Path:
        return CERT_ROOT / self.app_name

    @property
    def proof_bundle(self) -> Path:
        return self.app_dir / f"{self.app_name}_e2e_proof.json"

    @property
    def static_dag_proof(self) -> Path:
        return self.app_dir / f"{self.app_name}_static_l3_dag_proof.json"

    @property
    def runtime_l3_receipt(self) -> Path:
        return self.app_dir / f"{self.app_name}_runtime_l3_orchestration_receipt.json"

    @property
    def l3_bypass_receipt(self) -> Path:
        return self.app_dir / f"{self.app_name}_l3_bypass_receipt.json"

    @property
    def artifact_manifest(self) -> Path:
        return self.app_dir / f"{self.app_name}_artifact_manifest.json"

    @property
    def run_log(self) -> Path:
        return self.app_dir / f"{self.app_name}_run.log"

    @property
    def runs_root(self) -> Path:
        return REPO_ROOT / "artifacts" / self.app_name / "runs"

    def ensure(self) -> None:
        self.app_dir.mkdir(parents=True, exist_ok=True)


__all__ = [
    "REPO_ROOT",
    "CERT_ROOT",
    "MATRIX_PATH",
    "CORE_CERT_ROOT",
    "AppCertPaths",
]
