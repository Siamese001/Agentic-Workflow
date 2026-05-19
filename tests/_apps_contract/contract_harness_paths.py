"""Repo paths for offline contract/pytest harness runs under ``contract_harness/``."""

from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.runtime_proof_layout import contract_harness_run_dir

REPO = Path(__file__).resolve().parents[2]


def harness_run(run_key: str, *parts: str) -> Path:
    return contract_harness_run_dir(REPO, run_key, *parts)
